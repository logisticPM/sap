"""Freeze and scorer behaviour on synthetic exports."""

import json
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from procurement_sandbox import client as c  # noqa: E402
from procurement_sandbox.acceptance import freeze, score  # noqa: E402
from procurement_sandbox.app import create_app  # noqa: E402

NOW = "2026-10-25T09:00:00Z"
TASKS = json.loads(freeze.TASKS.read_text(encoding="utf-8"))
BY_ID = {t["id"]: t for t in TASKS["tasks"]}


@pytest.fixture()
def sandbox(tmp_path):
    with TestClient(create_app(tmp_path / "a.sqlite"), base_url="http://sandbox.test") as tc:
        yield tc


def cli(tc, role="planner"):
    return c.ProcurementClient("http://sandbox.test", role=role, http=tc, sandbox_now=NOW)


def ts(i):
    return f"2026-10-25T13:{i:02d}:00Z"


def base_export(task, **over):
    e = {"task_id": task["id"], "case_id": task["case_id"], "synthetic_components": ["email business facts"],
         "inbound": [{"message_id": "<m1>", "received_at": ts(0), "from": "orders@northorchard.example", "subject": "x", "matched_case": task["case_id"], "duplicate_of": None, "source": "email"}],
         "matched_case": task["case_id"], "ambiguity_confirmation_requested": False, "duplicate_detected": False,
         "reviews": [{"id": "rev-1", "started_at": ts(1), "accepted_at": ts(2), "model_calls": 3, "sources_read": ["PO-4500001042", "MSG-1"], "outcome": "accepted"}],
         "disposition": {"kind": None, "quantity": None, "unit": "CS", "wait": None},
         "submission": {"attempts": [], "state": None, "purchase_requisition": None, "evidence_version": None},
         "approval": {"state": None, "by_role": None, "at": None}, "closed_at": None,
         "timestamps": {"received_at": ts(0), "review_started": ts(1), "review_accepted": ts(2)},
         "human_actions": [{"role": "supplier", "action": "authorize_disclosure", "at": ts(3), "active_seconds": 30}],
         "ui_states_shown": []}
    e.update(over)
    return e


def test_tasks_file_is_well_formed():
    assert len(TASKS["tasks"]) == 10 and len({t["case_id"] for t in TASKS["tasks"]}) == 10
    for t in TASKS["tasks"]:
        assert t["inbound"] and t["expected"] and t["answer_key"]
        assert "pr_created" in t["expected"] and "forbidden_quantities" in t["expected"]
    assert "NOT an independent" in TASKS["author_note"]


def test_freeze_and_check(tmp_path):
    tasks = tmp_path / "tasks.json"
    tasks.write_text(freeze.TASKS.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "freeze.json"
    assert freeze.main(["--tasks", str(tasks), "--out", str(out)]) == 0
    assert freeze.main(["--check", "--tasks", str(tasks), "--out", str(out)]) == 0
    doc = json.loads(tasks.read_text(encoding="utf-8"))
    doc["tasks"][1]["expected"]["pr_quantity"] = "150.000"
    tasks.write_text(json.dumps(doc), encoding="utf-8")
    assert freeze.main(["--check", "--tasks", str(tasks), "--out", str(out)]) == 1
    assert freeze.main(["--tasks", str(tasks), "--out", str(out)]) == 2  # refuses to overwrite


def test_t02_passes_when_sandbox_confirms_the_claim(sandbox):
    p, approver = cli(sandbox), cli(sandbox, "procurement_approver")
    task = BY_ID["T02"]
    po = p.read_purchase_order("4500001042")
    d = {"case_id": task["case_id"], "evidence_version": "ev-1", "material": "OJ-250", "plant": "CA10", "quantity": 140, "unit": "CS", "needed_by": "2026-10-28",
         "reason": "explicit revision", "open_unknowns": "Receiving slot 28 Oct 08:00 to be confirmed by DC",
         "baseline_po": po["purchase_order"], "baseline_po_item": "00010", "baseline_po_changed_at": po["changed_at"]}
    sub = p.submit_change_draft(d)
    approver.release(sub.purchase_requisition)
    export = base_export(task, disposition={"kind": "CHANGE", "quantity": 140, "unit": "CS", "wait": None},
                         submission={"attempts": [{"at": ts(4), "idempotency_key": "k", "state": sub.state, "status_code": 201}], "state": sub.state,
                                     "purchase_requisition": sub.purchase_requisition, "evidence_version": "ev-1"},
                         approval={"state": "approved", "by_role": "procurement_approver", "at": ts(5)}, closed_at=ts(6),
                         timestamps={"received_at": ts(0), "review_started": ts(1), "review_accepted": ts(2), "disclosure_authorized": ts(3), "change_submitted": ts(4), "change_approved": ts(5), "closed": ts(6)},
                         ui_states_shown=[c.SUBMITTED, c.APPROVED])
    r = score.score_task(task, export, p)
    assert r.passed, [x for x in r.checks if not x[1]]


def test_t01_fails_critically_if_a_pr_exists(sandbox):
    p = cli(sandbox)
    task = BY_ID["T01"]
    po = p.read_purchase_order("4500001042")
    p.submit_change_draft({"case_id": task["case_id"], "evidence_version": "ev-x", "material": "OJ-250", "plant": "CA10", "quantity": 140, "unit": "CS",
                           "needed_by": "2026-10-28", "reason": "guessed", "baseline_po": "4500001042", "baseline_po_item": "00010", "baseline_po_changed_at": po["changed_at"]})
    export = base_export(task, disposition={"kind": "CHANGE", "quantity": 140, "unit": "CS", "wait": None},
                         submission={"attempts": [{"at": ts(4), "idempotency_key": "k", "state": c.SUBMITTED, "status_code": 201}], "state": c.SUBMITTED, "purchase_requisition": "1000000001"})
    r = score.score_task(task, export, p)
    assert not r.passed and r.critical
    names = {x.split(":")[0] for x in r.critical}
    assert {"disposition", "pr_created", "disposition_quantity_not_forbidden"} <= names


def test_t01_passes_with_a_resumable_wait(sandbox):
    p = cli(sandbox)
    task = BY_ID["T01"]
    export = base_export(task, disposition={"kind": "WAIT", "quantity": None, "unit": "CS",
                                            "wait": {"owner": "supplier", "deadline": "2026-10-26T12:00:00Z", "question": "Ship or arrive? How many cases? Lot expiry?"}},
                         human_actions=[])
    r = score.score_task(task, export, p)
    assert r.passed, [x for x in r.checks if not x[1]]


def test_t10_requires_same_key_and_never_completed_on_failure(sandbox):
    p, approver = cli(sandbox), cli(sandbox, "procurement_approver")
    task = BY_ID["T10"]
    po = p.read_purchase_order("4500001042")
    d = {"case_id": task["case_id"], "evidence_version": "ev-1", "material": "OJ-250", "plant": "CA10", "quantity": 140, "unit": "CS", "needed_by": "2026-10-28",
         "reason": "confirmed", "baseline_po": "4500001042", "baseline_po_item": "00010", "baseline_po_changed_at": po["changed_at"]}
    key = c.idempotency_key(d["case_id"], d["evidence_version"])
    first = p.submit_change_draft(d, fault="accept_then_fail")
    second = p.resolve_unknown(c.map_change_draft(d), key)
    approver.release(second.purchase_requisition)
    good = base_export(task, disposition={"kind": "CHANGE", "quantity": 140, "unit": "CS", "wait": None},
                       submission={"attempts": [{"at": ts(4), "idempotency_key": key, "state": first.state, "status_code": 502},
                                                {"at": ts(5), "idempotency_key": key, "state": second.state, "status_code": 200}],
                                   "state": second.state, "purchase_requisition": second.purchase_requisition},
                       approval={"state": "approved", "by_role": "procurement_approver", "at": ts(6)}, closed_at=ts(7),
                       timestamps={"received_at": ts(0), "review_started": ts(1), "review_accepted": ts(2), "change_submitted": ts(5), "change_approved": ts(6), "closed": ts(7)},
                       ui_states_shown=[c.OUTCOME_UNKNOWN, c.ALREADY_SUBMITTED, c.APPROVED])
    assert score.score_task(task, good, p).passed
    bad = json.loads(json.dumps(good))
    bad["submission"]["attempts"][1]["idempotency_key"] = "a-new-key"
    bad["ui_states_shown"].append("change_completed")
    r = score.score_task(task, bad, p)
    assert {"same_idempotency_key_on_retry", "never_showed_completed_on_failure"} <= {x.split(":")[0] for x in r.critical}


def test_report_renders_and_states_no_business_claim(sandbox, tmp_path):
    p = cli(sandbox)
    exports = tmp_path / "exports"
    exports.mkdir()
    (exports / "T01.json").write_text(json.dumps(base_export(BY_ID["T01"], disposition={"kind": "WAIT", "quantity": None, "unit": "CS", "wait": {"owner": "supplier", "deadline": "d", "question": "q"}}, human_actions=[])), encoding="utf-8")
    results = score.score_all(TASKS, exports, p)
    assert len(results) == 10 and results[0].passed and not results[1].passed
    text = score.render(results, "frozen (test)", "not-SAP-connected")
    assert "states no time saving and no business value" in text and "| T01 |" in text and "not-SAP-connected" in text
