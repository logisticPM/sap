"""Contract tests for the procurement sandbox (not SAP connected). Run: pytest procurement_sandbox/tests -q"""

import json
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from procurement_sandbox.app import create_app  # noqa: E402

PO_SVC = "/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV"
STOCK_SVC = "/sap/opu/odata/sap/API_MATERIAL_STOCK_SRV"
PR_SVC = "/sap/opu/odata/sap/API_PURCHASEREQ_PROCESS_SRV"
PO_SEED_CHANGE = "2026-10-23T14:40:00Z"
NOW = "2026-10-25T09:00:00Z"


@pytest.fixture()
def client(tmp_path):
    app = create_app(tmp_path / "sandbox.sqlite")
    with TestClient(app, base_url="http://sandbox.test") as c:
        yield c


def csrf(client):
    r = client.get(PR_SVC + "/", headers={"X-CSRF-Token": "Fetch"})
    assert r.status_code == 200
    return r.headers["x-csrf-token"]


def headers(client, role="planner", **extra):
    h = {"X-CSRF-Token": csrf(client), "X-Sandbox-Role": role, "X-Sandbox-Now": NOW, "Content-Type": "application/json"}
    h.update(extra)
    return h


def item(**overrides):
    base = {
        "Material": "OJ-250", "Plant": "CA10", "StorageLocation": "DC01",
        "RequestedQuantity": "140", "BaseUnit": "CS", "DeliveryDate": "2026-10-28",
        "PurchaseRequisitionPrice": "24", "PurReqnPriceQuantity": "1", "PurReqnItemCurrency": "CAD",
        "Supplier": "0000100421", "PurchaseRequisitionItemText": "OJ-250 additional supply",
        "YY1_DemandPulseCase_PRI": "CASE-1042", "YY1_EvidenceVersion_PRI": "ev-a-v3",
        "YY1_Disposition_PRI": "CHANGE",
        "YY1_Reason_PRI": "Authorised quote CIT-92; carrier accepted; 140 cases under 20% cancellation stress.",
        "YY1_OpenUnknowns_PRI": "QA release reported, not independently verified",
        "YY1_RefPurchaseOrder_PRI": "4500001042", "YY1_RefPurchaseOrderItem_PRI": "00010",
        "YY1_RefPOChangeDateTime_PRI": PO_SEED_CHANGE,
    }
    base.update(overrides)
    return base


def payload(*items_, description="CASE-1042 OJ-250 add 140 cases"):
    return {"PurchaseRequisitionType": "NB", "PurReqnDescription": description,
            "to_PurchaseRequisitionItem": {"results": list(items_) or [item()]}}


def create(client, body=None, role="planner", **extra):
    return client.post(PR_SVC + "/A_PurchaseRequisitionHeader", json=body or payload(), headers=headers(client, role, **extra))


# ---------------------------------------------------------------- label and health
def test_every_response_is_labelled_not_sap_connected(client):
    for r in (client.get("/"), client.get("/sandbox/health"), client.get(PO_SVC + "/"), client.get(PR_SVC + "/$metadata"), client.get(PR_SVC + "/Nope")):
        assert r.headers["X-Procurement-Sandbox"] == "not-SAP-connected"
        assert "not SAP" in r.headers["Server"]
    assert client.get("/sandbox/health").json()["sap_connected"] is False


# ---------------------------------------------------------------- CSRF and roles
def test_post_without_csrf_token_is_refused_sap_style(client):
    r = client.post(PR_SVC + "/A_PurchaseRequisitionHeader", json=payload(), headers={"X-Sandbox-Role": "planner"})
    assert r.status_code == 403
    assert r.headers["x-csrf-token"] == "Required"
    assert r.json()["error"]["message"]["value"] == "CSRF token validation failed"


def test_supplier_role_can_never_modify(client):
    r = create(client, role="supplier")
    assert r.status_code == 403 and r.json()["error"]["code"] == "SB/AUTH_ROLE"
    assert client.get(PR_SVC + "/A_PurchaseRequisitionHeader").json()["d"]["results"] == []


def test_release_requires_procurement_approver(client):
    number = create(client).json()["d"]["PurchaseRequisition"]
    r = client.post(PR_SVC + f"/ReleasePurchaseRequisition?PurchaseRequisition='{number}'&ReleaseCode='01'", headers=headers(client, "planner"))
    assert r.status_code == 403
    r = client.post(PR_SVC + f"/ReleasePurchaseRequisition?PurchaseRequisition='{number}'&ReleaseCode='01'", headers=headers(client, "procurement_approver"))
    assert r.status_code == 200
    d = r.json()["d"]
    assert d["ReleaseStatus"] == "R" and d["ReleasedByUser"] == "PROCUREMENT_" and d["ReleaseDateTime"].startswith("/Date(")
    again = client.post(PR_SVC + f"/ReleasePurchaseRequisition?PurchaseRequisition='{number}'&ReleaseCode='01'", headers=headers(client, "procurement_approver"))
    assert again.status_code == 409 and again.json()["error"]["code"] == "SB/ALREADY_DECIDED"


def test_reject_records_reason_and_frees_the_case_for_a_new_request(client):
    number = create(client).json()["d"]["PurchaseRequisition"]
    r = client.post(PR_SVC + f"/RejectPurchaseRequisition?PurchaseRequisition='{number}'&Reason='Quote expired'", headers=headers(client, "procurement_approver"))
    assert r.status_code == 200 and r.json()["d"]["ReleaseStatus"] == "X" and r.json()["d"]["RejectionReason"] == "Quote expired"
    # same case and evidence version may be submitted again after rejection
    assert create(client).status_code == 201


# ---------------------------------------------------------------- reads
def test_read_purchase_order_with_expand_in_odata_v2_shape(client):
    r = client.get(PO_SVC + "/A_PurchaseOrder('4500001042')?$expand=to_PurchaseOrderItem/to_ScheduleLine")
    assert r.status_code == 200
    assert r.headers["ETag"] == f'W/"{PO_SEED_CHANGE}"'
    d = r.json()["d"]
    assert d["__metadata"]["etag"] == r.headers["ETag"]
    assert d["PurchaseOrder"] == "4500001042" and d["Supplier"] == "0000100421"
    assert d["LastChangeDateTime"].startswith("/Date(") and d["LastChangeDateTime"].endswith("+0000)/")
    it = d["to_PurchaseOrderItem"]["results"][0]
    assert it["Material"] == "OJ-250" and it["OrderQuantity"] == "120.000" and it["PurchaseOrderQuantityUnit"] == "CS"
    sl = it["to_ScheduleLine"]["results"][0]
    assert sl["ScheduleLineOrderQuantity"] == "120.000" and sl["ScheduleLineDeliveryDate"].startswith("/Date(")
    # unexpanded navigation is deferred
    bare = client.get(PO_SVC + "/A_PurchaseOrder('4500001042')").json()["d"]
    assert "__deferred" in bare["to_PurchaseOrderItem"]


def test_read_stock_with_filter(client):
    r = client.get(STOCK_SVC + "/A_MatlStkInAcctMod?$filter=Material eq 'OJ-250' and Plant eq 'CA10'")
    rows = r.json()["d"]["results"]
    assert len(rows) == 1 and rows[0]["MatlWrhsStkQtyInMatlBaseUnit"] == "240.000" and rows[0]["MaterialBaseUnit"] == "CS"
    assert client.get(STOCK_SVC + "/A_MatlStkInAcctMod?$filter=Material eq 'NOPE'").json()["d"]["results"] == []
    bad = client.get(STOCK_SVC + "/A_MatlStkInAcctMod?$filter=substringof('x',Material)")
    assert bad.status_code == 400 and bad.json()["error"]["code"] == "SB/FILTER"


def test_metadata_and_service_document(client):
    md = client.get(PR_SVC + "/$metadata")
    assert md.status_code == 200 and "xml" in md.headers["content-type"]
    assert "A_PurchaseRequisitionHeaderType" in md.text and "YY1_RefPOChangeDateTime_PRI" in md.text and "ReleasePurchaseRequisition" in md.text
    doc = client.get(PO_SVC + "/").json()["d"]["EntitySets"]
    assert "A_PurchaseOrder" in doc and "A_PurchaseOrderScheduleLine" in doc


# ---------------------------------------------------------------- create
def test_create_purchase_requisition_deep_insert(client):
    r = create(client)
    assert r.status_code == 201, r.text
    d = r.json()["d"]
    assert d["PurchaseRequisition"] == "1000000001"
    assert r.headers["Location"].endswith("/A_PurchaseRequisitionHeader('1000000001')")
    assert r.headers["ETag"] == d["__metadata"]["etag"]
    assert d["ReleaseStatus"] == "" and d["ProcessingStatus"] == "N" and d["CreatedByUser"] == "PLANNER"
    it = d["to_PurchaseRequisitionItem"]["results"][0]
    assert it["PurchaseRequisitionItem"] == "00010" and it["RequestedQuantity"] == "140.000"
    assert it["YY1_DemandPulseCase_PRI"] == "CASE-1042" and it["YY1_RefPOChangeDateTime_PRI"].endswith("+0000)/")
    assert it["PurchasingGroup"] == "C01"
    # readable afterwards, with expand
    got = client.get(PR_SVC + "/A_PurchaseRequisitionHeader('1000000001')?$expand=to_PurchaseRequisitionItem").json()["d"]
    assert got["to_PurchaseRequisitionItem"]["results"][0]["Material"] == "OJ-250"
    listed = client.get(PR_SVC + "/A_PurchaseRequisitionItem?$filter=YY1_DemandPulseCase_PRI eq 'CASE-1042'").json()["d"]["results"]
    assert len(listed) == 1


def test_input_date_formats_are_accepted_and_output_is_sap_form(client):
    # 2026-10-28T00:00:00Z = 1793145600 s; 08:00Z = 1793174400 s
    for value in ("2026-10-28", "2026-10-28T08:00:00Z", "/Date(1793174400000)/"):
        r = create(client, payload(item(DeliveryDate=value, YY1_EvidenceVersion_PRI=f"ev-{value}")))
        assert r.status_code == 201, r.text
        assert r.json()["d"]["to_PurchaseRequisitionItem"]["results"][0]["DeliveryDate"] == "/Date(1793145600000)/"


def test_validation_errors_are_field_level_and_nothing_is_created(client):
    bad = item(Material="OJ-999", BaseUnit="EA", DeliveryDate="2026-10-01", YY1_Disposition_PRI="KEEP", PurReqnItemCurrency="USD")
    del bad["YY1_Reason_PRI"]
    r = create(client, payload(bad))
    assert r.status_code == 400
    err = r.json()["error"]
    assert err["code"] == "SB/VALIDATION"
    targets = {d["target"].split("/")[-1] for d in err["innererror"]["errordetails"]}
    assert {"Material", "DeliveryDate", "YY1_Disposition_PRI", "PurReqnItemCurrency", "YY1_Reason_PRI"} <= targets
    codes = {d["code"] for d in err["innererror"]["errordetails"]}
    assert {"ME/006", "ME/039", "SB/DISPOSITION", "SB/CURRENCY", "SB/REQUIRED"} <= codes
    assert client.get(PR_SVC + "/A_PurchaseRequisitionHeader").json()["d"]["results"] == []


def test_keep_or_stop_disposition_never_creates_an_object(client):
    r = create(client, payload(item(YY1_Disposition_PRI="STOP")))
    assert r.status_code == 400
    assert any(d["code"] == "SB/DISPOSITION" for d in r.json()["error"]["innererror"]["errordetails"])


# ---------------------------------------------------------------- idempotency and duplicates
def test_idempotency_key_replays_same_object_and_rejects_reuse(client):
    first = create(client, **{"Idempotency-Key": "k-1"})
    assert first.status_code == 201
    replay = create(client, **{"Idempotency-Key": "k-1"})
    assert replay.status_code == 200 and replay.headers["Idempotent-Replayed"] == "true"
    assert replay.json()["d"]["PurchaseRequisition"] == first.json()["d"]["PurchaseRequisition"]
    reused = create(client, payload(item(RequestedQuantity="150")), **{"Idempotency-Key": "k-1"})
    assert reused.status_code == 422 and reused.json()["error"]["code"] == "SB/IDEMPOTENCY_KEY_REUSED"
    assert len(client.get(PR_SVC + "/A_PurchaseRequisitionHeader").json()["d"]["results"]) == 1


def test_duplicate_case_and_evidence_version_is_refused_with_existing_number(client):
    first = create(client).json()["d"]["PurchaseRequisition"]
    dup = create(client)
    assert dup.status_code == 409
    err = dup.json()["error"]
    assert err["code"] == "SB/DUPLICATE_REQUEST" and err["innererror"]["errordetails"][0]["target"] == first
    # a new evidence version is a new request
    assert create(client, payload(item(YY1_EvidenceVersion_PRI="ev-a-v4"))).status_code == 201


# ---------------------------------------------------------------- staleness
def test_stale_baseline_is_refused_after_the_po_changes(client):
    h = headers(client, "system", **{"If-Match": f'W/"{PO_SEED_CHANGE}"'})
    r = client.patch(PO_SVC + "/A_PurchaseOrderItem(PurchaseOrder='4500001042',PurchaseOrderItem='00010')", json={"OrderQuantity": "150"}, headers=h)
    assert r.status_code == 204
    new_etag = r.headers["ETag"]
    assert new_etag != f'W/"{PO_SEED_CHANGE}"'
    po = client.get(PO_SVC + "/A_PurchaseOrder('4500001042')?$expand=to_PurchaseOrderItem/to_ScheduleLine").json()["d"]
    assert po["to_PurchaseOrderItem"]["results"][0]["OrderQuantity"] == "150.000"
    assert po["to_PurchaseOrderItem"]["results"][0]["to_ScheduleLine"]["results"][0]["ScheduleLineOrderQuantity"] == "150.000"
    stale = create(client)  # prepared against the seed timestamp
    assert stale.status_code == 412
    err = stale.json()["error"]
    assert err["code"] == "SB/STALE_BASELINE" and "Re-review" in err["innererror"]["errordetails"][0]["message"]
    fresh_ts = new_etag.strip('W/"')
    assert create(client, payload(item(YY1_RefPOChangeDateTime_PRI=fresh_ts))).status_code == 201


def test_po_patch_requires_matching_if_match(client):
    url = PO_SVC + "/A_PurchaseOrderItem(PurchaseOrder='4500001042',PurchaseOrderItem='00010')"
    assert client.patch(url, json={"OrderQuantity": "150"}, headers=headers(client, "system")).status_code == 428
    wrong = client.patch(url, json={"OrderQuantity": "150"}, headers=headers(client, "system", **{"If-Match": 'W/"2000-01-01T00:00:00Z"'}))
    assert wrong.status_code == 412 and wrong.json()["error"]["code"] == "SB/ETAG_MISMATCH"
    notallowed = client.patch(url, json={"Material": "X"}, headers=headers(client, "system", **{"If-Match": "*"}))
    assert notallowed.status_code == 400


# ---------------------------------------------------------------- fault injection
def test_http500_and_locked_faults_persist_nothing(client):
    for fault, status in (("http500", 500), ("locked", 409)):
        r = create(client, **{"X-Sandbox-Fault": fault})
        assert r.status_code == status and "Nothing was persisted" in r.json()["error"]["message"]["value"]
    assert client.get(PR_SVC + "/A_PurchaseRequisitionHeader").json()["d"]["results"] == []


def test_accept_then_fail_is_resolved_by_retrying_with_the_same_key(client):
    r = create(client, **{"Idempotency-Key": "k-9", "X-Sandbox-Fault": "accept_then_fail"})
    assert r.status_code == 502
    assert len(client.get(PR_SVC + "/A_PurchaseRequisitionHeader").json()["d"]["results"]) == 1
    retry = create(client, **{"Idempotency-Key": "k-9"})
    assert retry.status_code == 200 and retry.headers["Idempotent-Replayed"] == "true"
    assert retry.json()["d"]["PurchaseRequisition"] == "1000000001"


def test_timeout_fault_uses_configured_delay(tmp_path, monkeypatch):
    monkeypatch.setenv("PROC_SANDBOX_TIMEOUT_SECONDS", "0.05")
    with TestClient(create_app(tmp_path / "t.sqlite"), base_url="http://sandbox.test") as c:
        r = create(c, **{"X-Sandbox-Fault": "timeout"})
        assert r.status_code == 504 and r.json()["error"]["code"] == "SB/FAULT_TIMEOUT"


# ---------------------------------------------------------------- audit, reset, persistence
def test_audit_records_every_modifying_call_and_reset_needs_system_role(client):
    create(client)
    create(client, role="supplier")
    events = client.get("/sandbox/audit").json()["events"]
    assert [e["status"] for e in events] == [201, 403]
    assert events[0]["role"] == "planner" and events[0]["request"]["PurReqnDescription"].startswith("CASE-1042")
    assert client.post("/sandbox/reset", headers={"X-Sandbox-Role": "planner"}).status_code == 403
    assert client.post("/sandbox/reset", headers={"X-Sandbox-Role": "system"}).status_code == 200
    assert client.get(PR_SVC + "/A_PurchaseRequisitionHeader").json()["d"]["results"] == []
    assert client.get(PO_SVC + "/A_PurchaseOrder('4500001042')").json()["d"]["PurchaseOrder"] == "4500001042"


def test_objects_survive_a_restart(tmp_path):
    db = tmp_path / "persist.sqlite"
    with TestClient(create_app(db), base_url="http://sandbox.test") as c:
        number = create(c).json()["d"]["PurchaseRequisition"]
    with TestClient(create_app(db), base_url="http://sandbox.test") as c:
        assert c.get(PR_SVC + f"/A_PurchaseRequisitionHeader('{number}')").status_code == 200
        assert create(c).status_code == 409  # duplicate guard also survives
