"""Inbound contract: payload builder, signing, simulator run against the reference receiver."""

import json
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from procurement_sandbox.acceptance import simulate_inbound as sim  # noqa: E402
from procurement_sandbox.acceptance.freeze import TASKS  # noqa: E402
from procurement_sandbox.acceptance.inbound_reference_receiver import create_receiver  # noqa: E402

DOC = json.loads(TASKS.read_text(encoding="utf-8"))
BY_ID = {t["id"]: t for t in DOC["tasks"]}
SECRET = "test-secret"


@pytest.fixture()
def receiver():
    with TestClient(create_receiver(SECRET), base_url="http://app.test") as tc:
        yield tc


def test_payload_shape_and_routing_hints():
    p = sim.build_payload(BY_ID["T02"], 1, BY_ID["T02"]["inbound"][0], "replies.example", "2026-10-25T13:10:04Z")
    for k in ("schema", "source", "provider", "message_id", "edge_received_at", "from", "to", "subject", "text", "attachments", "routing_hints", "raw_mime_sha256"):
        assert k in p
    assert p["schema"] == sim.SCHEMA and p["source"] == "simulator"
    assert p["to"] == ["case+CASE-1042-T02@replies.example"] and p["message_id"] == "<T02-1@sim.demand-pulse>"
    assert p["routing_hints"]["plus_address_case"] == "CASE-1042-T02" and "4500001042" in p["routing_hints"]["po_numbers"] and "OJ-250" in p["routing_hints"]["sku_tokens"]
    assert p["sent_at"] == "2026-10-25T13:10:00Z" and p["simulator"]["note"].startswith("Synthetic")


def test_ambiguous_task_goes_to_the_bare_address_and_duplicates_share_message_id():
    t05 = sim.build_payload(BY_ID["T05"], 1, BY_ID["T05"]["inbound"][0], "replies.example")
    assert t05["to"] == ["case@replies.example"] and t05["routing_hints"]["plus_address_case"] is None
    assert "4500001077" in t05["routing_hints"]["po_numbers"]
    t06 = [sim.build_payload(BY_ID["T06"], i, m, "replies.example") for i, m in enumerate(BY_ID["T06"]["inbound"], start=1)]
    assert t06[0]["message_id"] == t06[1]["message_id"] == "<dup-001@northorchard.example>" and t06[2]["message_id"] == "<fwd-002@northorchard.example>"


def test_all_tasks_produce_twelve_payloads_and_dry_run_writes_them(tmp_path):
    items = sim.payloads_for(DOC, None, "replies.example")
    assert len(items) == 12
    log = sim.run(None, SECRET, None, "replies.example", 0, True, tmp_path / "p")
    assert len(log) == 12 and len(list((tmp_path / "p").glob("T*.json"))) == 12


def test_signature_roundtrip():
    body = b'{"a":1}'
    assert sim.verify(SECRET, body, sim.sign(SECRET, body))
    assert not sim.verify(SECRET, body + b" ", sim.sign(SECRET, body))
    assert not sim.verify(SECRET, body, None)


def test_receiver_rejects_bad_auth_and_bad_schema(receiver):
    p = sim.build_payload(BY_ID["T02"], 1, BY_ID["T02"]["inbound"][0], "replies.example")
    body = json.dumps(p).encode()
    assert receiver.post("/api/inbound", content=body, headers={"X-Inbound-Secret": "wrong", "X-Inbound-Signature": sim.sign("wrong", body)}).status_code == 401
    assert receiver.post("/api/inbound", content=body, headers={"X-Inbound-Secret": SECRET, "X-Inbound-Signature": "sha256=00"}).status_code == 401
    bad = dict(p, message_id="no-brackets", schema="x")
    bb = json.dumps(bad).encode()
    r = receiver.post("/api/inbound", content=bb, headers={"X-Inbound-Secret": SECRET, "X-Inbound-Signature": sim.sign(SECRET, bb)})
    assert r.status_code == 400 and any("Message-ID" in d for d in r.json()["details"]) and any("schema" in d for d in r.json()["details"])
    assert receiver.get("/api/inbound/messages").json()["count"] == 0


def test_simulator_against_reference_receiver_matches_contract(receiver, tmp_path):
    log = sim.run("http://app.test/api/inbound", SECRET, None, "replies.example", 0, False, tmp_path, http=receiver)
    by = {}
    for e in log:
        by.setdefault(e["task_id"], []).append(e)
    # plus-addressed tasks are matched and trigger a review
    for tid in ("T01", "T02", "T03", "T04", "T07", "T08", "T09", "T10"):
        e = by[tid][0]
        assert e["status"] == 202 and e["response"]["case_id"] == BY_ID[tid]["case_id"] and e["response"]["review_triggered"] is True
    # T05: ambiguous, nothing triggered
    t05 = by["T05"][0]["response"]
    assert by["T05"][0]["status"] == 202 and t05["case_id"] is None and t05["needs_confirmation"] is True and t05["review_triggered"] is False
    # T06: second message is a duplicate (200), forward is a new message id
    assert by["T06"][0]["status"] == 202 and by["T06"][1]["status"] == 200 and by["T06"][1]["response"]["duplicate_of"] == "<dup-001@northorchard.example>"
    assert by["T06"][2]["status"] == 202
    stored = receiver.get("/api/inbound/messages").json()
    assert stored["count"] == 11  # 12 sent, one exact duplicate dropped
    assert all(m["source"] == "simulator" for m in stored["messages"])
    sent_log = json.loads((tmp_path / "sent_log.json").read_text(encoding="utf-8"))
    assert sent_log["mail_receipt"] == "simulated" and len(sent_log["entries"]) == 12


def test_replaying_the_simulator_is_idempotent(receiver, tmp_path):
    sim.run("http://app.test/api/inbound", SECRET, ["T02"], "replies.example", 0, False, None, http=receiver)
    again = sim.run("http://app.test/api/inbound", SECRET, ["T02"], "replies.example", 0, False, None, http=receiver)
    assert again[0]["status"] == 200 and again[0]["response"]["duplicate_of"] == "<T02-1@sim.demand-pulse>"
    assert receiver.get("/api/inbound/messages").json()["count"] == 1
