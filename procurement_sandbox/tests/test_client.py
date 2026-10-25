"""Reference client against the sandbox through Starlette's TestClient (an httpx.Client)."""

import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from procurement_sandbox import client as c  # noqa: E402
from procurement_sandbox.app import create_app  # noqa: E402

NOW = "2026-10-25T09:00:00Z"


@pytest.fixture()
def sandbox(tmp_path):
    with TestClient(create_app(tmp_path / "c.sqlite"), base_url="http://sandbox.test") as tc:
        yield tc


def planner(tc, role="planner"):
    return c.ProcurementClient("http://sandbox.test", role=role, http=tc, sandbox_now=NOW)


def draft(po, **over):
    d = {"case_id": "CASE-1042-T02", "evidence_version": "ev-1", "material": "OJ-250", "plant": "CA10", "storage_location": "DC01",
         "quantity": 140, "unit": "CS", "needed_by": "2026-10-28", "price_per_unit": 24, "currency": "CAD", "supplier": po["supplier"],
         "reason": "Explicit revision; carrier accepted; QA released", "open_unknowns": "receiving slot to be confirmed by DC",
         "baseline_po": po["purchase_order"], "baseline_po_item": po["items"][0]["item"], "baseline_po_changed_at": po["changed_at"]}
    d.update(over)
    return d


def test_read_po_and_stock_are_plain_python(sandbox):
    p = planner(sandbox)
    po = p.read_purchase_order("4500001042")
    assert po["changed_at"] == "2026-10-23T14:40:00Z" and po["etag"] == 'W/"2026-10-23T14:40:00Z"' and po["sandbox_label"] == "not-SAP-connected"
    assert po["items"][0]["quantity"] == "120.000" and po["items"][0]["schedule_lines"][0]["delivery_date"] == "2026-10-27T00:00:00Z"
    assert p.read_stock("OJ-250", "CA10")[0]["quantity"] == "240.000"


def test_full_state_mapping(sandbox):
    p = planner(sandbox)
    approver = planner(sandbox, "procurement_approver")
    supplier = planner(sandbox, "supplier")
    po = p.read_purchase_order("4500001042")
    d = draft(po)
    first = p.submit_change_draft(d)
    assert first.state == c.SUBMITTED and first.purchase_requisition == "1000000001" and first.is_persisted
    assert p.submit_change_draft(d).state == c.ALREADY_SUBMITTED
    dup = p.submit_change_draft(d, idem_key="another-key")
    assert dup.state == c.DUPLICATE and dup.purchase_requisition == "1000000001"
    assert supplier.submit_change_draft(draft(po, evidence_version="ev-s")).state == c.FORBIDDEN
    bad = p.submit_change_draft(draft(po, evidence_version="ev-bad", material="OJ-999"))
    assert bad.state == c.REJECTED_BEFORE_SUBMISSION and any(x["code"] == "ME/006" for x in bad.details)
    assert p.release("1000000001").state == c.FORBIDDEN
    assert approver.release("1000000001").state == c.APPROVED
    pr = p.get_purchase_requisition("1000000001")
    assert pr["release_status"] == "released" and pr["items"][0]["case_id"] == "CASE-1042-T02" and pr["items"][0]["baseline_po_changed_at"] == po["changed_at"]
    second = p.submit_change_draft(draft(po, evidence_version="ev-2"))
    assert approver.reject(second.purchase_requisition, "Quote expired").state == c.RETURNED
    assert p.get_purchase_requisition(second.purchase_requisition)["rejection_reason"] == "Quote expired"
    assert [x["purchase_requisition"] for x in p.list_purchase_requisitions("CASE-1042-T02")] == ["1000000001", "1000000002"]


def test_stale_baseline_after_po_change(sandbox):
    p = planner(sandbox)
    po = p.read_purchase_order("4500001042")
    new_etag = p.change_purchase_order_item("4500001042", "00010", po["etag"], OrderQuantity="150")
    assert new_etag != po["etag"]
    stale = p.submit_change_draft(draft(po))
    assert stale.state == c.STALE and stale.code == "SB/STALE_BASELINE" and not stale.is_persisted
    fresh = p.read_purchase_order("4500001042")
    assert p.submit_change_draft(draft(fresh)).state == c.SUBMITTED


def test_unknown_outcome_is_resolved_by_retrying_with_the_same_key(sandbox):
    p = planner(sandbox)
    po = p.read_purchase_order("4500001042")
    d = draft(po, case_id="CASE-1042-T10")
    key = c.idempotency_key(d["case_id"], d["evidence_version"])
    first = p.submit_change_draft(d, fault="accept_then_fail")
    assert first.state == c.OUTCOME_UNKNOWN and first.status_code == 502 and first.purchase_requisition is None
    resolved = p.resolve_unknown(c.map_change_draft(d), key)
    assert resolved.state == c.ALREADY_SUBMITTED and resolved.purchase_requisition == "1000000001"
    assert len(p.list_purchase_requisitions("CASE-1042-T10")) == 1


def test_map_change_draft_refuses_keep_and_missing_fields():
    with pytest.raises(ValueError):
        c.map_change_draft({"case_id": "x"})
    with pytest.raises(ValueError):
        c.map_change_draft({"case_id": "x", "evidence_version": "v", "material": "OJ-250", "plant": "CA10", "quantity": 1, "unit": "CS",
                            "needed_by": "2026-10-28", "reason": "r", "baseline_po": "p", "baseline_po_item": "i", "baseline_po_changed_at": "t",
                            "disposition": "KEEP"})
    payload = c.map_change_draft({"case_id": "CASE-1042-T04", "evidence_version": "v", "material": "OJ-250", "plant": "CA10", "quantity": 140, "unit": "CS",
                                  "needed_by": "2026-10-28", "reason": "r", "baseline_po": "4500001042", "baseline_po_item": "00010",
                                  "baseline_po_changed_at": "2026-10-23T14:40:00Z", "price_per_unit": 24})
    item = payload["to_PurchaseRequisitionItem"]["results"][0]
    assert item["RequestedQuantity"] == "140" and item["PurReqnItemCurrency"] == "CAD" and payload["PurReqnDescription"].startswith("CASE-1042-T04")


def test_odata_date_conversion():
    assert c.odata_date_to_iso("/Date(1793145600000+0000)/") == "2026-10-28T00:00:00Z"
    assert c.odata_date_to_iso(None) is None
