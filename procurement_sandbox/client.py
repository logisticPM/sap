"""Reference client for the procurement sandbox (not SAP connected).

Shows the exact call sequence an application should make and maps every
sandbox response to the application state named in CONTRACT.md section 7.
Usable as a library (ProcurementClient) or as a walkthrough:

    python -m procurement_sandbox.client --base http://127.0.0.1:8081
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx

ODATA = "/sap/opu/odata/sap"
SVC_PO = f"{ODATA}/API_PURCHASEORDER_PROCESS_SRV"
SVC_STOCK = f"{ODATA}/API_MATERIAL_STOCK_SRV"
SVC_PR = f"{ODATA}/API_PURCHASEREQ_PROCESS_SRV"

# Application states, CONTRACT.md section 7
SUBMITTED = "submitted_awaiting_procurement_approval"
ALREADY_SUBMITTED = "already_submitted"
DUPLICATE = "already_submitted_for_this_evidence"
STALE = "baseline_changed_re_review_required"
REJECTED_BEFORE_SUBMISSION = "rejected_before_submission"
FORBIDDEN = "not_permitted_for_role"
OUTCOME_UNKNOWN = "submission_failed_outcome_unknown"
APPROVED = "approved_by_procurement"
RETURNED = "returned_by_procurement"
NOT_SAP = "not-SAP-connected"


def odata_date_to_iso(value: str | None) -> str | None:
    """'/Date(1793145600000+0000)/' -> '2026-10-28T00:00:00Z'."""
    if not value:
        return None
    m = re.fullmatch(r"/Date\((-?\d+)(?:[+-]\d{4})?\)/", value)
    if not m:
        return value
    return datetime.fromtimestamp(int(m.group(1)) / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def idempotency_key(case_id: str, evidence_version: str) -> str:
    return "dp-" + hashlib.sha256(f"{case_id}|{evidence_version}".encode("utf-8")).hexdigest()[:32]


@dataclass
class SubmissionResult:
    state: str
    status_code: int
    purchase_requisition: str | None = None
    code: str | None = None
    message: str | None = None
    details: list[dict] = field(default_factory=list)
    etag: str | None = None
    sandbox_label: str | None = None

    @property
    def is_persisted(self) -> bool:
        return self.state in (SUBMITTED, ALREADY_SUBMITTED, DUPLICATE)


def map_change_draft(draft: dict) -> dict:
    """CONTRACT.md section 9: Demand Pulse change draft -> purchase requisition deep insert."""
    required = ("case_id", "evidence_version", "material", "plant", "quantity", "unit", "needed_by",
                "reason", "baseline_po", "baseline_po_item", "baseline_po_changed_at")
    missing = [k for k in required if draft.get(k) in (None, "")]
    if missing:
        raise ValueError(f"change draft is missing {missing}")
    if draft.get("disposition", "CHANGE") != "CHANGE":
        raise ValueError("only disposition CHANGE becomes a procurement object; keep/stop are closed in the application")
    item = {
        "Material": draft["material"],
        "Plant": draft["plant"],
        "RequestedQuantity": str(draft["quantity"]),
        "BaseUnit": draft["unit"],
        "DeliveryDate": draft["needed_by"],
        "YY1_DemandPulseCase_PRI": draft["case_id"],
        "YY1_EvidenceVersion_PRI": draft["evidence_version"],
        "YY1_Disposition_PRI": "CHANGE",
        "YY1_Reason_PRI": str(draft["reason"])[:255],
        "YY1_RefPurchaseOrder_PRI": draft["baseline_po"],
        "YY1_RefPurchaseOrderItem_PRI": draft["baseline_po_item"],
        "YY1_RefPOChangeDateTime_PRI": draft["baseline_po_changed_at"],
    }
    optional = {
        "storage_location": "StorageLocation", "open_unknowns": "YY1_OpenUnknowns_PRI", "supplier": "Supplier",
        "item_text": "PurchaseRequisitionItemText", "requisitioner": "RequisitionerName",
    }
    for src, dst in optional.items():
        if draft.get(src) not in (None, ""):
            item[dst] = str(draft[src])[:255 if dst.startswith("YY1_") else 40]
    if draft.get("price_per_unit") not in (None, ""):
        item["PurchaseRequisitionPrice"] = str(draft["price_per_unit"])
        item["PurReqnPriceQuantity"] = "1"
        item["PurReqnItemCurrency"] = draft.get("currency", "CAD")
    description = draft.get("description") or f"{draft['case_id']} {draft['material']} add {draft['quantity']} {draft['unit']}"
    return {"PurchaseRequisitionType": "NB", "PurReqnDescription": description[:40],
            "to_PurchaseRequisitionItem": {"results": [item]}}


class ProcurementClient:
    """Thin client over the sandbox's SAP-shaped services."""

    def __init__(self, base_url: str = "http://127.0.0.1:8081", role: str = "planner", http: httpx.Client | None = None,
                 sandbox_now: str | None = None, timeout: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.role = role
        self.sandbox_now = sandbox_now
        self._http = http or httpx.Client(base_url=self.base_url, timeout=timeout)
        self._token: str | None = None

    # ------------------------------------------------------------ plumbing
    def _headers(self, **extra) -> dict:
        h = {"Accept": "application/json", "X-Sandbox-Role": self.role}
        if self.sandbox_now:
            h["X-Sandbox-Now"] = self.sandbox_now
        h.update({k: v for k, v in extra.items() if v is not None})
        return h

    def _url(self, path: str) -> str:
        return path if self._http.base_url else self.base_url + path

    def fetch_token(self) -> str:
        r = self._http.get(self._url(SVC_PR + "/"), headers=self._headers(**{"X-CSRF-Token": "Fetch"}))
        r.raise_for_status()
        self._token = r.headers["x-csrf-token"]
        return self._token

    def _write_headers(self, **extra) -> dict:
        if not self._token:
            self.fetch_token()
        return self._headers(**{"X-CSRF-Token": self._token, "Content-Type": "application/json"}, **extra)

    @staticmethod
    def _error(r: httpx.Response) -> tuple[str | None, str | None, list[dict]]:
        try:
            err = r.json()["error"]
            return err.get("code"), err.get("message", {}).get("value"), err.get("innererror", {}).get("errordetails", [])
        except Exception:  # noqa: BLE001
            return None, r.text[:200], []

    # ------------------------------------------------------------ reads
    def read_purchase_order(self, po: str) -> dict:
        r = self._http.get(self._url(f"{SVC_PO}/A_PurchaseOrder('{po}')"), params={"$expand": "to_PurchaseOrderItem/to_ScheduleLine"}, headers=self._headers())
        r.raise_for_status()
        d = r.json()["d"]
        items = []
        for it in d["to_PurchaseOrderItem"]["results"]:
            sched = [{"delivery_date": odata_date_to_iso(s["ScheduleLineDeliveryDate"]), "quantity": s["ScheduleLineOrderQuantity"]}
                     for s in it["to_ScheduleLine"]["results"]]
            items.append({"item": it["PurchaseOrderItem"], "material": it["Material"], "plant": it["Plant"], "storage_location": it["StorageLocation"],
                          "quantity": it["OrderQuantity"], "unit": it["PurchaseOrderQuantityUnit"], "net_price": it["NetPriceAmount"],
                          "currency": it["DocumentCurrency"], "schedule_lines": sched})
        return {"purchase_order": d["PurchaseOrder"], "supplier": d["Supplier"], "currency": d["DocumentCurrency"],
                "changed_at": odata_date_to_iso(d["LastChangeDateTime"]), "etag": r.headers.get("ETag"), "items": items,
                "sandbox_label": r.headers.get("X-Procurement-Sandbox"), "read_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

    def read_stock(self, material: str, plant: str) -> list[dict]:
        r = self._http.get(self._url(f"{SVC_STOCK}/A_MatlStkInAcctMod"), params={"$filter": f"Material eq '{material}' and Plant eq '{plant}'"}, headers=self._headers())
        r.raise_for_status()
        return [{"storage_location": s["StorageLocation"], "batch": s["Batch"], "stock_type": s["InventoryStockType"],
                 "quantity": s["MatlWrhsStkQtyInMatlBaseUnit"], "unit": s["MaterialBaseUnit"]} for s in r.json()["d"]["results"]]

    def get_purchase_requisition(self, number: str) -> dict | None:
        r = self._http.get(self._url(f"{SVC_PR}/A_PurchaseRequisitionHeader('{number}')"), params={"$expand": "to_PurchaseRequisitionItem"}, headers=self._headers())
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return self._pr_view(r.json()["d"])

    def list_purchase_requisitions(self, case_id: str | None = None) -> list[dict]:
        params = {"$filter": f"YY1_DemandPulseCase_PRI eq '{case_id}'"} if case_id else {}
        r = self._http.get(self._url(f"{SVC_PR}/A_PurchaseRequisitionItem"), params=params, headers=self._headers())
        r.raise_for_status()
        numbers = sorted({it["PurchaseRequisition"] for it in r.json()["d"]["results"]})
        return [self.get_purchase_requisition(n) for n in numbers]

    @staticmethod
    def _pr_view(d: dict) -> dict:
        items = d.get("to_PurchaseRequisitionItem", {}).get("results", []) if isinstance(d.get("to_PurchaseRequisitionItem"), dict) else []
        status = {"": "awaiting_release", "R": "released", "X": "rejected"}.get(d.get("ReleaseStatus", ""), d.get("ReleaseStatus"))
        return {"purchase_requisition": d["PurchaseRequisition"], "description": d["PurReqnDescription"], "release_status": status,
                "released_by": d.get("ReleasedByUser"), "release_at": odata_date_to_iso(d.get("ReleaseDateTime")),
                "rejection_reason": d.get("RejectionReason"), "changed_at": odata_date_to_iso(d["LastChangeDateTime"]),
                "items": [{"item": it["PurchaseRequisitionItem"], "material": it["Material"], "plant": it["Plant"], "quantity": it["RequestedQuantity"],
                           "unit": it["BaseUnit"], "delivery_date": odata_date_to_iso(it["DeliveryDate"]), "case_id": it["YY1_DemandPulseCase_PRI"],
                           "evidence_version": it["YY1_EvidenceVersion_PRI"], "reason": it["YY1_Reason_PRI"], "open_unknowns": it.get("YY1_OpenUnknowns_PRI"),
                           "baseline_po": it["YY1_RefPurchaseOrder_PRI"], "baseline_po_item": it["YY1_RefPurchaseOrderItem_PRI"],
                           "baseline_po_changed_at": odata_date_to_iso(it["YY1_RefPOChangeDateTime_PRI"])} for it in items]}

    # ------------------------------------------------------------ writes
    def submit_change_draft(self, draft: dict, idem_key: str | None = None, fault: str | None = None) -> SubmissionResult:
        payload = map_change_draft(draft)
        key = idem_key or idempotency_key(draft["case_id"], draft["evidence_version"])
        return self.submit_payload(payload, key, fault=fault)

    def submit_payload(self, payload: dict, idem_key: str, fault: str | None = None) -> SubmissionResult:
        try:
            r = self._http.post(self._url(f"{SVC_PR}/A_PurchaseRequisitionHeader"), json=payload,
                                headers=self._write_headers(**{"Idempotency-Key": idem_key, "X-Sandbox-Fault": fault}))
        except httpx.TransportError as exc:
            return SubmissionResult(OUTCOME_UNKNOWN, 0, message=f"transport error: {exc}")
        label = r.headers.get("X-Procurement-Sandbox")
        if r.status_code == 201:
            d = r.json()["d"]
            return SubmissionResult(SUBMITTED, 201, d["PurchaseRequisition"], etag=r.headers.get("ETag"), sandbox_label=label)
        if r.status_code == 200 and r.headers.get("Idempotent-Replayed") == "true":
            d = r.json()["d"]
            return SubmissionResult(ALREADY_SUBMITTED, 200, d["PurchaseRequisition"], etag=r.headers.get("ETag"), sandbox_label=label)
        code, message, details = self._error(r)
        if r.status_code == 409 and code == "SB/DUPLICATE_REQUEST":
            existing = details[0].get("target") if details else None
            return SubmissionResult(DUPLICATE, 409, existing, code, message, details, sandbox_label=label)
        if r.status_code == 412:
            return SubmissionResult(STALE, 412, None, code, message, details, sandbox_label=label)
        if r.status_code in (400, 422):
            return SubmissionResult(REJECTED_BEFORE_SUBMISSION, r.status_code, None, code, message, details, sandbox_label=label)
        if r.status_code == 403:
            return SubmissionResult(FORBIDDEN, 403, None, code, message, details, sandbox_label=label)
        return SubmissionResult(OUTCOME_UNKNOWN, r.status_code, None, code, message, details, sandbox_label=label)

    def resolve_unknown(self, payload: dict, idem_key: str) -> SubmissionResult:
        """After OUTCOME_UNKNOWN: retry with the same key; the sandbox tells you what happened."""
        return self.submit_payload(payload, idem_key)

    def _decide(self, function: str, number: str, **params) -> SubmissionResult:
        r = self._http.post(self._url(f"{SVC_PR}/{function}"), params={"PurchaseRequisition": f"'{number}'", **{k: f"'{v}'" for k, v in params.items()}},
                            headers=self._write_headers())
        label = r.headers.get("X-Procurement-Sandbox")
        if r.status_code == 200:
            status = r.json()["d"]["ReleaseStatus"]
            return SubmissionResult(APPROVED if status == "R" else RETURNED, 200, number, etag=r.headers.get("ETag"), sandbox_label=label)
        code, message, details = self._error(r)
        state = FORBIDDEN if r.status_code == 403 else OUTCOME_UNKNOWN if r.status_code >= 500 else REJECTED_BEFORE_SUBMISSION
        return SubmissionResult(state, r.status_code, number, code, message, details, sandbox_label=label)

    def release(self, number: str, release_code: str = "01") -> SubmissionResult:
        return self._decide("ReleasePurchaseRequisition", number, ReleaseCode=release_code)

    def reject(self, number: str, reason: str) -> SubmissionResult:
        return self._decide("RejectPurchaseRequisition", number, Reason=reason)

    def change_purchase_order_item(self, po: str, item: str, etag: str, **fields: Any) -> str:
        """Test helper: simulate a PO change in SAP so a prepared draft becomes stale. Returns the new ETag."""
        r = self._http.patch(self._url(f"{SVC_PO}/A_PurchaseOrderItem(PurchaseOrder='{po}',PurchaseOrderItem='{item}')"), json=fields,
                             headers=self._write_headers(**{"If-Match": etag}))
        r.raise_for_status()
        return r.headers["ETag"]

    def audit(self) -> list[dict]:
        r = self._http.get(self._url("/sandbox/audit"), headers=self._headers())
        r.raise_for_status()
        return r.json()["events"]


# ---------------------------------------------------------------- walkthrough
def walkthrough(base: str) -> int:
    planner = ProcurementClient(base, role="planner")
    approver = ProcurementClient(base, role="procurement_approver")
    po = planner.read_purchase_order("4500001042")
    stock = planner.read_stock("OJ-250", "CA10")
    print(f"[{po['sandbox_label']}] PO {po['purchase_order']} item {po['items'][0]['item']} {po['items'][0]['quantity']} {po['items'][0]['unit']} changed_at {po['changed_at']}")
    print(f"stock {stock[0]['quantity']} {stock[0]['unit']} at {stock[0]['storage_location']}")
    draft = {"case_id": "CASE-1042", "evidence_version": "walkthrough-" + datetime.now(timezone.utc).strftime("%H%M%S"),
             "material": "OJ-250", "plant": "CA10", "storage_location": "DC01", "quantity": 140, "unit": "CS", "needed_by": "2026-10-28",
             "price_per_unit": 24, "currency": "CAD", "supplier": po["supplier"],
             "reason": "Authorised quote CIT-92; carrier accepted; 140 cases under 20% cancellation stress.",
             "open_unknowns": "QA release reported, not independently verified",
             "baseline_po": po["purchase_order"], "baseline_po_item": po["items"][0]["item"], "baseline_po_changed_at": po["changed_at"]}
    first = planner.submit_change_draft(draft)
    print(f"submit -> {first.state} ({first.status_code}) PR {first.purchase_requisition}")
    again = planner.submit_change_draft(draft)
    print(f"retry  -> {again.state} ({again.status_code}) PR {again.purchase_requisition}")
    decided = approver.release(first.purchase_requisition)
    print(f"release-> {decided.state} ({decided.status_code})")
    pr = planner.get_purchase_requisition(first.purchase_requisition)
    print(f"final  -> {pr['release_status']} by {pr['released_by']} at {pr['release_at']}")
    new_etag = planner.change_purchase_order_item(po["purchase_order"], po["items"][0]["item"], po["etag"], OrderQuantity="150")
    stale = planner.submit_change_draft({**draft, "evidence_version": draft["evidence_version"] + "-b"})
    print(f"after PO change (new ETag {new_etag}) -> {stale.state} ({stale.status_code})")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Procurement sandbox reference walkthrough")
    ap.add_argument("--base", default="http://127.0.0.1:8081")
    raise SystemExit(walkthrough(ap.parse_args().base))
