"""Procurement sandbox - not SAP connected.

S/4HANA-shaped OData v2 mock (purchase order read, material stock read,
purchase requisition read/write) with CSRF, roles, ETags, idempotency,
duplicate guard, staleness check, fault injection and an audit log.
The contract is in CONTRACT.md. Nothing here talks to SAP.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import sqlite3
import time
import uuid
from contextlib import closing
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import unquote

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route

ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "data" / "sandbox.sqlite"
LABEL = "not-SAP-connected"
ODATA_ROOT = "/sap/opu/odata/sap"
SVC_PO = "API_PURCHASEORDER_PROCESS_SRV"
SVC_STOCK = "API_MATERIAL_STOCK_SRV"
SVC_PR = "API_PURCHASEREQ_PROCESS_SRV"
SERVICES = (SVC_PO, SVC_STOCK, SVC_PR)
MODIFYING_ROLES = {"planner", "system", "procurement_approver"}
CREATE_ROLES = {"planner", "system"}
APPROVER_ROLES = {"procurement_approver"}
PR_SEQUENCE_START = 1000000000

# ---------------------------------------------------------------- field types
# s string, d decimal(3), dt Edm.DateTime, dto Edm.DateTimeOffset, b boolean
PO_HEADER = {
    "PurchaseOrder": "s", "PurchaseOrderType": "s", "Supplier": "s", "CompanyCode": "s",
    "PurchasingOrganization": "s", "PurchasingGroup": "s", "DocumentCurrency": "s",
    "CreationDate": "dt", "LastChangeDateTime": "dto", "PurchasingDocumentDeletionCode": "s",
}
PO_ITEM = {
    "PurchaseOrder": "s", "PurchaseOrderItem": "s", "Material": "s", "PurchaseOrderItemText": "s",
    "Plant": "s", "StorageLocation": "s", "OrderQuantity": "d", "PurchaseOrderQuantityUnit": "s",
    "NetPriceAmount": "d", "NetPriceQuantity": "d", "DocumentCurrency": "s", "MaterialGroup": "s",
    "PurchasingDocumentDeletionCode": "s",
}
PO_SCHED = {
    "PurchaseOrder": "s", "PurchaseOrderItem": "s", "ScheduleLine": "s",
    "ScheduleLineDeliveryDate": "dt", "ScheduleLineOrderQuantity": "d", "DelivDateCategory": "s",
}
STOCK = {
    "Material": "s", "Plant": "s", "StorageLocation": "s", "Batch": "s", "InventoryStockType": "s",
    "MatlWrhsStkQtyInMatlBaseUnit": "d", "MaterialBaseUnit": "s",
}
PR_HEADER = {
    "PurchaseRequisition": "s", "PurchaseRequisitionType": "s", "PurReqnDescription": "s",
    "SourceDetermination": "b", "CreatedByUser": "s", "CreationDate": "dt", "LastChangeDateTime": "dto",
    "ProcessingStatus": "s", "ReleaseStatus": "s", "ReleasedByUser": "s", "ReleaseDateTime": "dto",
    "RejectionReason": "s",
}
PR_ITEM = {
    "PurchaseRequisition": "s", "PurchaseRequisitionItem": "s", "PurchaseRequisitionItemText": "s",
    "Material": "s", "Plant": "s", "StorageLocation": "s", "RequestedQuantity": "d", "BaseUnit": "s",
    "DeliveryDate": "dt", "PurchaseRequisitionPrice": "d", "PurReqnPriceQuantity": "d",
    "PurReqnItemCurrency": "s", "PurchasingGroup": "s", "PurchasingOrganization": "s", "Supplier": "s",
    "RequisitionerName": "s", "IsDeleted": "b",
    "YY1_DemandPulseCase_PRI": "s", "YY1_EvidenceVersion_PRI": "s", "YY1_Disposition_PRI": "s",
    "YY1_Reason_PRI": "s", "YY1_OpenUnknowns_PRI": "s", "YY1_RefPurchaseOrder_PRI": "s",
    "YY1_RefPurchaseOrderItem_PRI": "s", "YY1_RefPOChangeDateTime_PRI": "dto",
}
EDM = {"s": "Edm.String", "d": "Edm.Decimal", "dt": "Edm.DateTime", "dto": "Edm.DateTimeOffset", "b": "Edm.Boolean"}

ENTITY_SETS = {
    SVC_PO: {"A_PurchaseOrder": ("A_PurchaseOrderType", PO_HEADER), "A_PurchaseOrderItem": ("A_PurchaseOrderItemType", PO_ITEM),
             "A_PurchaseOrderScheduleLine": ("A_PurchaseOrderScheduleLineType", PO_SCHED)},
    SVC_STOCK: {"A_MatlStkInAcctMod": ("A_MatlStkInAcctModType", STOCK)},
    SVC_PR: {"A_PurchaseRequisitionHeader": ("A_PurchaseRequisitionHeaderType", PR_HEADER),
             "A_PurchaseRequisitionItem": ("A_PurchaseRequisitionItemType", PR_ITEM)},
}
FUNCTION_IMPORTS = {SVC_PR: ("ReleasePurchaseRequisition", "RejectPurchaseRequisition")}

PATH_RE = re.compile(r"^(?P<set>[A-Za-z_$][\w]*)(?:\((?P<key>.*)\))?(?:/(?P<nav>\w+))?$")


# ---------------------------------------------------------------- time/format
def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_dt(value) -> datetime | None:
    """Accept ISO 8601, YYYY-MM-DD, /Date(ms)/ or /Date(ms+0000)/."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    s = str(value).strip()
    m = re.fullmatch(r"/Date\((-?\d+)(?:[+-]\d{4})?\)/", s)
    if m:
        return datetime.fromtimestamp(int(m.group(1)) / 1000, tz=timezone.utc)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        s += "T00:00:00Z"
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def to_odata(kind: str, value):
    if value is None:
        return None
    if kind == "d":
        return format_decimal(value)
    if kind in ("dt", "dto"):
        dt = parse_dt(value)
        if dt is None:
            return None
        ms = int(dt.timestamp() * 1000)
        return f"/Date({ms})/" if kind == "dt" else f"/Date({ms}+0000)/"
    if kind == "b":
        return bool(value)
    return "" if value is None else str(value)


def format_decimal(value) -> str:
    return f"{Decimal(str(value)).quantize(Decimal('0.001')):f}"


def parse_decimal(value) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def etag_for(change_iso: str) -> str:
    return f'W/"{change_iso}"'


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


# ---------------------------------------------------------------- storage
class Store:
    """SQLite-backed documents, idempotency keys, CSRF tokens, counters, audit."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.seed = json.loads((ROOT / "seed.json").read_text(encoding="utf-8"))
        self._init()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init(self) -> None:
        with closing(self._conn()) as c:
            c.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (kind TEXT, key TEXT, body TEXT, etag TEXT, updated_at TEXT, PRIMARY KEY (kind, key));
                CREATE TABLE IF NOT EXISTS idempotency (key TEXT PRIMARY KEY, payload_hash TEXT, status INTEGER, body TEXT, created_at TEXT);
                CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, created_at TEXT);
                CREATE TABLE IF NOT EXISTS counters (name TEXT PRIMARY KEY, value INTEGER);
                CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, method TEXT, path TEXT, role TEXT, status INTEGER, request TEXT, response TEXT, note TEXT);
                """
            )
            if c.execute("SELECT COUNT(*) FROM documents WHERE kind='PO'").fetchone()[0] == 0:
                self._seed(c)

    def _seed(self, c: sqlite3.Connection) -> None:
        for po in self.seed["purchase_orders"]:
            body = json.loads(json.dumps(po))
            c.execute("INSERT OR REPLACE INTO documents VALUES ('PO',?,?,?,?)",
                      (po["PurchaseOrder"], json.dumps(body), etag_for(po["LastChangeDateTime"]), po["LastChangeDateTime"]))
        for i, s in enumerate(self.seed["stock"]):
            c.execute("INSERT OR REPLACE INTO documents VALUES ('STOCK',?,?,?,?)",
                      (f"{s['Material']}|{s['Plant']}|{s['StorageLocation']}|{s.get('Batch','')}", json.dumps(s), "", iso(utcnow())))
        c.execute("INSERT OR REPLACE INTO counters VALUES ('PR', ?)", (PR_SEQUENCE_START,))

    def reset(self) -> None:
        with closing(self._conn()) as c:
            c.execute("DELETE FROM documents")
            c.execute("DELETE FROM idempotency")
            c.execute("DELETE FROM counters")
            self._seed(c)

    # documents
    def get(self, kind: str, key: str) -> dict | None:
        with closing(self._conn()) as c:
            row = c.execute("SELECT body FROM documents WHERE kind=? AND key=?", (kind, key)).fetchone()
        return json.loads(row[0]) if row else None

    def list(self, kind: str) -> list[dict]:
        with closing(self._conn()) as c:
            rows = c.execute("SELECT body FROM documents WHERE kind=? ORDER BY key", (kind,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def put(self, kind: str, key: str, body: dict, etag: str) -> None:
        with closing(self._conn()) as c:
            c.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?)", (kind, key, json.dumps(body), etag, iso(utcnow())))

    def next_pr_number(self) -> str:
        with closing(self._conn()) as c:
            c.execute("UPDATE counters SET value = value + 1 WHERE name='PR'")
            value = c.execute("SELECT value FROM counters WHERE name='PR'").fetchone()[0]
        return str(value)

    # tokens
    def new_token(self) -> str:
        token = secrets.token_urlsafe(24)
        with closing(self._conn()) as c:
            c.execute("INSERT INTO tokens VALUES (?,?)", (token, iso(utcnow())))
        return token

    def token_valid(self, token: str | None) -> bool:
        if not token:
            return False
        with closing(self._conn()) as c:
            return c.execute("SELECT 1 FROM tokens WHERE token=?", (token,)).fetchone() is not None

    # idempotency
    def idem_get(self, key: str) -> tuple[str, int, dict] | None:
        with closing(self._conn()) as c:
            row = c.execute("SELECT payload_hash, status, body FROM idempotency WHERE key=?", (key,)).fetchone()
        return (row[0], row[1], json.loads(row[2])) if row else None

    def idem_put(self, key: str, payload_hash: str, status: int, body: dict) -> None:
        with closing(self._conn()) as c:
            c.execute("INSERT OR REPLACE INTO idempotency VALUES (?,?,?,?,?)", (key, payload_hash, status, json.dumps(body), iso(utcnow())))

    # audit
    def audit(self, method: str, path: str, role: str | None, status: int, request_body, response_body, note: str = "") -> None:
        with closing(self._conn()) as c:
            c.execute("INSERT INTO audit (ts, method, path, role, status, request, response, note) VALUES (?,?,?,?,?,?,?,?)",
                      (iso(utcnow()), method, path, role or "", status, json.dumps(request_body, ensure_ascii=False)[:20000],
                       json.dumps(response_body, ensure_ascii=False)[:20000], note))

    def audit_list(self) -> list[dict]:
        with closing(self._conn()) as c:
            rows = c.execute("SELECT id, ts, method, path, role, status, request, response, note FROM audit ORDER BY id").fetchall()
        return [{"id": r[0], "ts": r[1], "method": r[2], "path": r[3], "role": r[4], "status": r[5],
                 "request": _loads(r[6]), "response": _loads(r[7]), "note": r[8]} for r in rows]


def _loads(s):
    try:
        return json.loads(s)
    except Exception:  # noqa: BLE001
        return s


# ---------------------------------------------------------------- responses
class SandboxError(Exception):
    def __init__(self, status: int, code: str, message: str, details: list[dict] | None = None, headers: dict | None = None):
        super().__init__(message)
        self.status, self.code, self.message, self.details, self.headers = status, code, message, details or [], headers or {}


def error_body(code: str, message: str, details: list[dict]) -> dict:
    return {
        "error": {
            "code": code,
            "message": {"lang": "en", "value": message},
            "innererror": {
                "transactionid": uuid.uuid4().hex.upper(),
                "timestamp": utcnow().strftime("%Y%m%d%H%M%S.0000000"),
                "Error_Resolution": {
                    "SAP_Transaction": "Procurement sandbox - not SAP connected",
                    "SAP_Note": "See CONTRACT.md section 7 for the application state each error maps to",
                },
                "errordetails": details,
            },
        }
    }


def detail(code: str, message: str, target: str = "", severity: str = "error") -> dict:
    return {"code": code, "message": message, "propertyref": "", "severity": severity, "target": target}


def labelled(resp: Response) -> Response:
    resp.headers["X-Procurement-Sandbox"] = LABEL
    resp.headers["Server"] = "Procurement-Sandbox/1.0 (not SAP)"
    resp.headers["DataServiceVersion"] = "2.0"
    return resp


def odata_json(payload: dict, status: int = 200, headers: dict | None = None) -> Response:
    resp = JSONResponse(payload, status_code=status, headers=headers or {}, media_type="application/json; charset=utf-8")
    return labelled(resp)


def serialize(entity: dict, fields: dict, base: str, set_name: str, type_name: str, key_expr: str,
              etag: str | None = None, nav: dict | None = None) -> dict:
    uri = f"{base}/{set_name}({key_expr})"
    out = {"__metadata": {"id": uri, "uri": uri, "type": f"API.{type_name}"}}
    if etag:
        out["__metadata"]["etag"] = etag
    for name, kind in fields.items():
        out[name] = to_odata(kind, entity.get(name))
    for name, value in (nav or {}).items():
        out[name] = value if value is not None else {"__deferred": {"uri": f"{uri}/{name}"}}
    return out


def key_expr_single(value: str) -> str:
    return f"'{value}'"


def key_expr_multi(**parts: str) -> str:
    return ",".join(f"{k}='{v}'" for k, v in parts.items())


# ---------------------------------------------------------------- query options
def parse_filter(expr: str | None) -> list[tuple[str, str]]:
    if not expr:
        return []
    out = []
    for clause in re.split(r"\s+and\s+", expr.strip(), flags=re.IGNORECASE):
        m = re.fullmatch(r"\s*(\w+)\s+eq\s+(?:'((?:[^']|'')*)'|(true|false|[\w.-]+))\s*", clause, flags=re.IGNORECASE)
        if not m:
            raise SandboxError(400, "SB/FILTER", f"Unsupported $filter clause: {clause}. Only Field eq 'value' joined by and.")
        value = m.group(2).replace("''", "'") if m.group(2) is not None else m.group(3)
        out.append((m.group(1), value))
    return out


def apply_filter(rows: list[dict], clauses: list[tuple[str, str]]) -> list[dict]:
    def match(row):
        for field, value in clauses:
            actual = row.get(field)
            if isinstance(actual, bool):
                if str(actual).lower() != str(value).lower():
                    return False
            elif str(actual if actual is not None else "") != str(value):
                return False
        return True
    return [r for r in rows if match(r)]


def page(rows: list, params) -> list:
    skip = int(params.get("$skip", 0) or 0)
    top = params.get("$top")
    rows = rows[skip:]
    return rows[: int(top)] if top else rows


def expand_set(params) -> set[str]:
    raw = params.get("$expand", "")
    out = set()
    for part in raw.split(","):
        part = part.strip()
        if part:
            out.add(part)
            if "/" in part:
                out.add(part.split("/")[0])
    return out


def select_fields(entity: dict, params) -> dict:
    sel = params.get("$select")
    if not sel:
        return entity
    keep = {s.strip() for s in sel.split(",")} | {"__metadata"}
    return {k: v for k, v in entity.items() if k in keep or k.startswith("to_")}


# ---------------------------------------------------------------- metadata
def metadata_xml(service: str) -> str:
    sets = ENTITY_SETS.get(service, {})
    types = []
    for set_name, (type_name, fields) in sets.items():
        props = "".join(f'<Property Name="{n}" Type="{EDM[k]}"' + (' Precision="13" Scale="3"' if k == "d" else "") + "/>" for n, k in fields.items())
        key = {"A_PurchaseOrder": ["PurchaseOrder"], "A_PurchaseOrderItem": ["PurchaseOrder", "PurchaseOrderItem"],
               "A_PurchaseOrderScheduleLine": ["PurchaseOrder", "PurchaseOrderItem", "ScheduleLine"],
               "A_MatlStkInAcctMod": ["Material", "Plant", "StorageLocation", "Batch", "InventoryStockType"],
               "A_PurchaseRequisitionHeader": ["PurchaseRequisition"],
               "A_PurchaseRequisitionItem": ["PurchaseRequisition", "PurchaseRequisitionItem"]}[set_name]
        keyxml = "".join(f'<PropertyRef Name="{k}"/>' for k in key)
        types.append(f'<EntityType Name="{type_name}" sap:content-version="1"><Key>{keyxml}</Key>{props}</EntityType>')
    setsxml = "".join(f'<EntitySet Name="{s}" EntityType="API.{t}" sap:creatable="{"true" if s == "A_PurchaseRequisitionHeader" else "false"}" sap:updatable="{"true" if s == "A_PurchaseOrderItem" else "false"}" sap:deletable="false" sap:content-version="1"/>' for s, (t, _) in sets.items())
    fis = "".join(f'<FunctionImport Name="{f}" ReturnType="API.A_PurchaseRequisitionHeaderType" EntitySet="A_PurchaseRequisitionHeader" m:HttpMethod="POST"><Parameter Name="PurchaseRequisition" Type="Edm.String" Mode="In"/><Parameter Name="{"ReleaseCode" if f.startswith("Release") else "Reason"}" Type="Edm.String" Mode="In"/></FunctionImport>' for f in FUNCTION_IMPORTS.get(service, ()))
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<edmx:Edmx Version="1.0" xmlns:edmx="http://schemas.microsoft.com/ado/2007/06/edmx" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:sap="http://www.sap.com/Protocols/SAPData">'
        '<!-- Procurement sandbox - not SAP connected. Shape only; see CONTRACT.md -->'
        '<edmx:DataServices m:DataServiceVersion="2.0">'
        f'<Schema Namespace="API" xmlns="http://schemas.microsoft.com/ado/2008/09/edm">{"".join(types)}'
        f'<EntityContainer Name="{service}_Entities" m:IsDefaultEntityContainer="true">{setsxml}{fis}</EntityContainer>'
        "</Schema></edmx:DataServices></edmx:Edmx>"
    )


# ---------------------------------------------------------------- application
def create_app(db_path: str | Path | None = None) -> Starlette:
    store = Store(Path(db_path or os.environ.get("PROC_SANDBOX_DB") or DEFAULT_DB))
    timeout_seconds = float(os.environ.get("PROC_SANDBOX_TIMEOUT_SECONDS", "8"))

    # ------------------------------------------------------------ helpers bound to the store
    def role_of(request: Request) -> str | None:
        return request.headers.get("X-Sandbox-Role")

    def require_csrf(request: Request) -> None:
        if not store.token_valid(request.headers.get("X-CSRF-Token")):
            raise SandboxError(403, "SB/CSRF", "CSRF token validation failed", headers={"x-csrf-token": "Required"})

    def require_role(request: Request, allowed: set[str], action: str) -> str:
        role = role_of(request)
        if role not in allowed:
            raise SandboxError(403, "SB/AUTH_ROLE", f"Role '{role or 'none'}' is not authorised to {action}. Allowed: {', '.join(sorted(allowed))}.",
                               [detail("SB/AUTH_ROLE", f"X-Sandbox-Role must be one of {sorted(allowed)}", "X-Sandbox-Role")])
        return role

    def fault_before(request: Request) -> None:
        fault = request.headers.get("X-Sandbox-Fault")
        if not fault:
            return
        if fault == "http500":
            raise SandboxError(500, "SB/FAULT_500", "Injected server error. Nothing was persisted.")
        if fault == "timeout":
            time.sleep(timeout_seconds)
            raise SandboxError(504, "SB/FAULT_TIMEOUT", "Injected gateway timeout. Nothing was persisted.")
        if fault == "locked":
            raise SandboxError(409, "ME/006", "Purchase requisition is currently locked by user ADMIN. Nothing was persisted.")
        if fault not in ("accept_then_fail",):
            raise SandboxError(400, "SB/FAULT_UNKNOWN", f"Unknown X-Sandbox-Fault value '{fault}'.")

    def sandbox_now(request: Request) -> datetime:
        override = parse_dt(request.headers.get("X-Sandbox-Now"))
        return override or utcnow()

    def base_url(request: Request, service: str) -> str:
        return f"{str(request.base_url).rstrip('/')}{ODATA_ROOT}/{service}"

    # ------------------------------------------------------------ serializers
    def po_header_out(request, po, expand) -> dict:
        base = base_url(request, SVC_PO)
        items = None
        if "to_PurchaseOrderItem" in expand:
            items = {"results": [po_item_out(request, po, it, expand) for it in po["items"]]}
        return serialize(po, PO_HEADER, base, "A_PurchaseOrder", "A_PurchaseOrderType", key_expr_single(po["PurchaseOrder"]),
                         etag_for(po["LastChangeDateTime"]), {"to_PurchaseOrderItem": items})

    def po_item_out(request, po, it, expand) -> dict:
        base = base_url(request, SVC_PO)
        row = {**it, "PurchaseOrder": po["PurchaseOrder"]}
        sched = None
        if "to_PurchaseOrderItem/to_ScheduleLine" in expand or "to_ScheduleLine" in expand:
            sched = {"results": [serialize({**sl, "PurchaseOrder": po["PurchaseOrder"], "PurchaseOrderItem": it["PurchaseOrderItem"]}, PO_SCHED, base,
                                           "A_PurchaseOrderScheduleLine", "A_PurchaseOrderScheduleLineType",
                                           key_expr_multi(PurchaseOrder=po["PurchaseOrder"], PurchaseOrderItem=it["PurchaseOrderItem"], ScheduleLine=sl["ScheduleLine"]))
                                 for sl in it.get("schedule_lines", [])]}
        return serialize(row, PO_ITEM, base, "A_PurchaseOrderItem", "A_PurchaseOrderItemType",
                         key_expr_multi(PurchaseOrder=po["PurchaseOrder"], PurchaseOrderItem=it["PurchaseOrderItem"]),
                         etag_for(po["LastChangeDateTime"]), {"to_ScheduleLine": sched})

    def pr_header_out(request, pr, expand) -> dict:
        base = base_url(request, SVC_PR)
        items = None
        if "to_PurchaseRequisitionItem" in expand:
            items = {"results": [pr_item_out(request, pr, it) for it in pr["items"]]}
        return serialize(pr, PR_HEADER, base, "A_PurchaseRequisitionHeader", "A_PurchaseRequisitionHeaderType",
                         key_expr_single(pr["PurchaseRequisition"]), etag_for(pr["LastChangeDateTime"]), {"to_PurchaseRequisitionItem": items})

    def pr_item_out(request, pr, it) -> dict:
        base = base_url(request, SVC_PR)
        return serialize({**it, "PurchaseRequisition": pr["PurchaseRequisition"]}, PR_ITEM, base, "A_PurchaseRequisitionItem",
                         "A_PurchaseRequisitionItemType", key_expr_multi(PurchaseRequisition=pr["PurchaseRequisition"], PurchaseRequisitionItem=it["PurchaseRequisitionItem"]),
                         etag_for(pr["LastChangeDateTime"]))

    def collection(request, rows: list[dict]) -> Response:
        return odata_json({"d": {"results": rows}})

    # ------------------------------------------------------------ PR create
    def validate_items(request: Request, raw_items: list, now: datetime) -> tuple[list[dict], list[dict], list[dict]]:
        """Return (items, validation_details, stale_details)."""
        materials, plants, suppliers = store.seed["materials"], store.seed["plants"], store.seed["suppliers"]
        items, bad, stale = [], [], []
        if not raw_items:
            bad.append(detail("SB/ITEMS", "At least one purchase requisition item is required", "to_PurchaseRequisitionItem"))
        for idx, src in enumerate(raw_items, start=1):
            if not isinstance(src, dict):
                bad.append(detail("SB/ITEMS", f"Item {idx} is not an object", f"to_PurchaseRequisitionItem[{idx}]"))
                continue
            tgt = f"to_PurchaseRequisitionItem[{idx}]/"
            item = {"PurchaseRequisitionItem": f"{idx * 10:05d}", "IsDeleted": False}
            for name in PR_ITEM:
                if name in src and name not in ("PurchaseRequisition", "PurchaseRequisitionItem", "IsDeleted"):
                    item[name] = src[name]
            for req in ("Material", "Plant", "RequestedQuantity", "BaseUnit", "DeliveryDate",
                        "YY1_DemandPulseCase_PRI", "YY1_EvidenceVersion_PRI", "YY1_Disposition_PRI", "YY1_Reason_PRI",
                        "YY1_RefPurchaseOrder_PRI", "YY1_RefPurchaseOrderItem_PRI", "YY1_RefPOChangeDateTime_PRI"):
                if src.get(req) in (None, ""):
                    bad.append(detail("SB/REQUIRED", f"{req} is required", tgt + req))
            mat = materials.get(str(src.get("Material", "")))
            if src.get("Material") and not mat:
                bad.append(detail("ME/006", f"Material {src.get('Material')} does not exist", tgt + "Material"))
            if src.get("Plant") and str(src.get("Plant")) not in plants:
                bad.append(detail("ME/008", f"Plant {src.get('Plant')} does not exist", tgt + "Plant"))
            if src.get("StorageLocation") and str(src.get("Plant")) in plants and str(src.get("StorageLocation")) not in plants[str(src.get("Plant"))]["StorageLocations"]:
                bad.append(detail("ME/009", f"Storage location {src.get('StorageLocation')} does not exist in plant {src.get('Plant')}", tgt + "StorageLocation"))
            qty = parse_decimal(src.get("RequestedQuantity"))
            if src.get("RequestedQuantity") not in (None, "") and (qty is None or qty <= 0):
                bad.append(detail("SB/QUANTITY", "RequestedQuantity must be a decimal greater than zero", tgt + "RequestedQuantity"))
            elif qty is not None:
                item["RequestedQuantity"] = format_decimal(qty)
            if mat and src.get("BaseUnit") and str(src.get("BaseUnit")) != mat["BaseUnit"]:
                bad.append(detail("SB/UNIT", f"BaseUnit must be {mat['BaseUnit']} for material {src.get('Material')}", tgt + "BaseUnit"))
            dd = parse_dt(src.get("DeliveryDate"))
            if src.get("DeliveryDate") not in (None, "") and dd is None:
                bad.append(detail("SB/DATE", "DeliveryDate is not a recognised date", tgt + "DeliveryDate"))
            elif dd is not None:
                if dd.date() < now.date():
                    bad.append(detail("ME/039", f"Delivery date {dd.date()} lies in the past (sandbox now {now.date()})", tgt + "DeliveryDate"))
                item["DeliveryDate"] = iso(dd.replace(hour=0, minute=0, second=0))
            for pname in ("PurchaseRequisitionPrice", "PurReqnPriceQuantity"):
                if src.get(pname) not in (None, ""):
                    pv = parse_decimal(src.get(pname))
                    if pv is None or pv < 0:
                        bad.append(detail("SB/PRICE", f"{pname} must be a non-negative decimal", tgt + pname))
                    else:
                        item[pname] = format_decimal(pv)
            if src.get("PurReqnItemCurrency") and str(src.get("PurReqnItemCurrency")) != "CAD":
                bad.append(detail("SB/CURRENCY", "PurReqnItemCurrency must be CAD in this sandbox", tgt + "PurReqnItemCurrency"))
            if src.get("Supplier") and str(src.get("Supplier")) not in suppliers:
                bad.append(detail("SB/SUPPLIER", f"Supplier {src.get('Supplier')} does not exist", tgt + "Supplier"))
            if src.get("YY1_Disposition_PRI") and str(src.get("YY1_Disposition_PRI")) != "CHANGE":
                bad.append(detail("SB/DISPOSITION", "Only disposition CHANGE creates a procurement object; keep/stop are closed in the application", tgt + "YY1_Disposition_PRI"))
            for tname, limit in (("YY1_Reason_PRI", 255), ("YY1_OpenUnknowns_PRI", 255), ("PurchaseRequisitionItemText", 40)):
                if src.get(tname) and len(str(src.get(tname))) > limit:
                    bad.append(detail("SB/LENGTH", f"{tname} exceeds {limit} characters", tgt + tname))
            item.setdefault("PurchasingGroup", "C01")
            item.setdefault("PurchasingOrganization", "CA01")
            # referenced PO and staleness
            ref_po = store.get("PO", str(src.get("YY1_RefPurchaseOrder_PRI", "")))
            if src.get("YY1_RefPurchaseOrder_PRI") and not ref_po:
                bad.append(detail("SB/REF_PO", f"Referenced purchase order {src.get('YY1_RefPurchaseOrder_PRI')} does not exist", tgt + "YY1_RefPurchaseOrder_PRI"))
            elif ref_po:
                ref_item = next((i for i in ref_po["items"] if i["PurchaseOrderItem"] == str(src.get("YY1_RefPurchaseOrderItem_PRI", ""))), None)
                if src.get("YY1_RefPurchaseOrderItem_PRI") and not ref_item:
                    bad.append(detail("SB/REF_PO", f"Referenced item {src.get('YY1_RefPurchaseOrderItem_PRI')} does not exist on PO {ref_po['PurchaseOrder']}", tgt + "YY1_RefPurchaseOrderItem_PRI"))
                seen = parse_dt(src.get("YY1_RefPOChangeDateTime_PRI"))
                current = parse_dt(ref_po["LastChangeDateTime"])
                if src.get("YY1_RefPOChangeDateTime_PRI") not in (None, "") and seen is None:
                    bad.append(detail("SB/DATE", "YY1_RefPOChangeDateTime_PRI is not a recognised timestamp", tgt + "YY1_RefPOChangeDateTime_PRI"))
                elif seen is not None and seen != current:
                    stale.append(detail("SB/STALE_BASELINE",
                                        f"Purchase order {ref_po['PurchaseOrder']} changed at {ref_po['LastChangeDateTime']}; the review saw {iso(seen)}. Re-review and re-approval required.",
                                        tgt + "YY1_RefPOChangeDateTime_PRI"))
                if seen is not None:
                    item["YY1_RefPOChangeDateTime_PRI"] = iso(seen)
            items.append(item)
        return items, bad, stale

    def find_duplicate(items: list[dict]) -> tuple[str, dict] | None:
        for pr in store.list("PR"):
            if pr.get("ReleaseStatus") == "X":
                continue
            for it in pr["items"]:
                for new in items:
                    if (it.get("YY1_DemandPulseCase_PRI"), it.get("YY1_EvidenceVersion_PRI")) == (new.get("YY1_DemandPulseCase_PRI"), new.get("YY1_EvidenceVersion_PRI")):
                        return pr["PurchaseRequisition"], it
        return None

    def create_pr(request: Request, body: dict) -> Response:
        require_csrf(request)
        role = require_role(request, CREATE_ROLES, "create a purchase requisition")
        fault_before(request)
        now = sandbox_now(request)
        idem_key = request.headers.get("Idempotency-Key")
        payload_hash = hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()
        if idem_key:
            prior = store.idem_get(idem_key)
            if prior:
                prior_hash, status, prior_body = prior
                if prior_hash != payload_hash:
                    raise SandboxError(422, "SB/IDEMPOTENCY_KEY_REUSED", "Idempotency-Key was already used with a different payload",
                                       [detail("SB/IDEMPOTENCY_KEY_REUSED", "Use a new key for a new request", "Idempotency-Key")])
                pr = store.get("PR", prior_body["PurchaseRequisition"])
                resp = odata_json({"d": pr_header_out(request, pr, {"to_PurchaseRequisitionItem"})}, 200,
                                  {"Idempotent-Replayed": "true", "ETag": etag_for(pr["LastChangeDateTime"]),
                                   "Location": f"{base_url(request, SVC_PR)}/A_PurchaseRequisitionHeader('{pr['PurchaseRequisition']}')"})
                store.audit("POST", request.url.path, role, 200, body, {"PurchaseRequisition": pr["PurchaseRequisition"]}, "idempotent replay")
                return resp
        raw_items = body.get("to_PurchaseRequisitionItem")
        if isinstance(raw_items, dict):
            raw_items = raw_items.get("results", [])
        raw_items = raw_items or []
        items, bad, stale = validate_items(request, raw_items, now)
        if body.get("PurchaseRequisitionType") not in (None, "", "NB"):
            bad.append(detail("SB/TYPE", "PurchaseRequisitionType must be NB", "PurchaseRequisitionType"))
        if body.get("PurReqnDescription") and len(str(body["PurReqnDescription"])) > 40:
            bad.append(detail("SB/LENGTH", "PurReqnDescription exceeds 40 characters", "PurReqnDescription"))
        if bad:
            raise SandboxError(400, "SB/VALIDATION", f"{len(bad)} validation error(s); nothing was created", bad)
        if stale:
            raise SandboxError(412, "SB/STALE_BASELINE", "Referenced purchase order changed since the review", stale)
        dup = find_duplicate(items)
        if dup:
            number, _ = dup
            raise SandboxError(409, "SB/DUPLICATE_REQUEST", f"An open purchase requisition {number} already exists for this case and evidence version",
                               [detail("SB/DUPLICATE_REQUEST", "Submit a new evidence version or reject the existing requisition", number)])
        number = store.next_pr_number()
        stamp = iso(now)
        pr = {
            "PurchaseRequisition": number, "PurchaseRequisitionType": "NB",
            "PurReqnDescription": str(body.get("PurReqnDescription", ""))[:40],
            "SourceDetermination": bool(body.get("SourceDetermination", False)),
            "CreatedByUser": role.upper()[:12], "CreationDate": stamp, "LastChangeDateTime": stamp,
            "ProcessingStatus": "N", "ReleaseStatus": "", "ReleasedByUser": "", "ReleaseDateTime": None, "RejectionReason": "",
            "items": items,
        }
        store.put("PR", number, pr, etag_for(stamp))
        if idem_key:
            store.idem_put(idem_key, payload_hash, 201, {"PurchaseRequisition": number})
        if request.headers.get("X-Sandbox-Fault") == "accept_then_fail":
            store.audit("POST", request.url.path, role, 502, body, {"PurchaseRequisition": number}, "persisted, then injected 502")
            raise SandboxError(502, "SB/FAULT_ACCEPT_THEN_FAIL", "Injected failure after the object was persisted. Retry with the same Idempotency-Key to learn the outcome.")
        out = pr_header_out(request, pr, {"to_PurchaseRequisitionItem"})
        store.audit("POST", request.url.path, role, 201, body, {"PurchaseRequisition": number})
        return odata_json({"d": out}, 201, {"Location": f"{base_url(request, SVC_PR)}/A_PurchaseRequisitionHeader('{number}')", "ETag": etag_for(stamp)})

    # ------------------------------------------------------------ release / reject
    def decide_pr(request: Request, release: bool) -> Response:
        require_csrf(request)
        role = require_role(request, APPROVER_ROLES, "release or reject a purchase requisition")
        fault_before(request)
        number = (request.query_params.get("PurchaseRequisition") or "").strip("'")
        pr = store.get("PR", number)
        if not pr:
            raise SandboxError(404, "SB/NOT_FOUND", f"Purchase requisition {number or '(none)'} does not exist")
        if pr.get("ReleaseStatus") in ("R", "X"):
            raise SandboxError(409, "SB/ALREADY_DECIDED", f"Purchase requisition {number} already has release status {pr['ReleaseStatus']}",
                               [detail("SB/ALREADY_DECIDED", "A decided requisition cannot be decided again", number)])
        stamp = iso(sandbox_now(request))
        if release:
            code = (request.query_params.get("ReleaseCode") or "").strip("'")
            if not code:
                raise SandboxError(400, "SB/REQUIRED", "ReleaseCode is required", [detail("SB/REQUIRED", "ReleaseCode", "ReleaseCode")])
            pr.update({"ReleaseStatus": "R", "ReleasedByUser": role.upper()[:12], "ReleaseDateTime": stamp})
        else:
            reason = (request.query_params.get("Reason") or "").strip("'")
            if not reason:
                raise SandboxError(400, "SB/REQUIRED", "Reason is required", [detail("SB/REQUIRED", "Reason", "Reason")])
            pr.update({"ReleaseStatus": "X", "ReleasedByUser": role.upper()[:12], "ReleaseDateTime": stamp, "RejectionReason": reason[:255]})
        pr["LastChangeDateTime"] = stamp
        store.put("PR", number, pr, etag_for(stamp))
        store.audit("POST", request.url.path, role, 200, dict(request.query_params), {"PurchaseRequisition": number, "ReleaseStatus": pr["ReleaseStatus"]})
        return odata_json({"d": pr_header_out(request, pr, {"to_PurchaseRequisitionItem"})}, 200, {"ETag": etag_for(stamp)})

    # ------------------------------------------------------------ PO patch (test helper for staleness)
    def patch_po_item(request: Request, key: dict, body: dict) -> Response:
        require_csrf(request)
        role = require_role(request, MODIFYING_ROLES, "change a purchase order item")
        fault_before(request)
        po = store.get("PO", key.get("PurchaseOrder", ""))
        item = next((i for i in (po or {}).get("items", []) if i["PurchaseOrderItem"] == key.get("PurchaseOrderItem")), None)
        if not po or not item:
            raise SandboxError(404, "SB/NOT_FOUND", "Purchase order item does not exist")
        if_match = request.headers.get("If-Match")
        if not if_match:
            raise SandboxError(428, "SB/IF_MATCH_REQUIRED", "If-Match header with the current ETag is required")
        if if_match != "*" and if_match != etag_for(po["LastChangeDateTime"]):
            raise SandboxError(412, "SB/ETAG_MISMATCH", f"ETag does not match; current is {etag_for(po['LastChangeDateTime'])}")
        allowed = {"OrderQuantity": "d", "NetPriceAmount": "d", "PurchaseOrderItemText": "s", "PurchasingDocumentDeletionCode": "s"}
        changed = {}
        for name, kind in allowed.items():
            if name in body:
                if kind == "d":
                    val = parse_decimal(body[name])
                    if val is None or val < 0:
                        raise SandboxError(400, "SB/VALIDATION", f"{name} must be a non-negative decimal", [detail("SB/VALIDATION", name, name)])
                    item[name] = format_decimal(val)
                    if name == "OrderQuantity":
                        for sl in item.get("schedule_lines", []):
                            sl["ScheduleLineOrderQuantity"] = item[name]
                else:
                    item[name] = str(body[name])
                changed[name] = item[name]
        unknown = set(body) - set(allowed)
        if unknown:
            raise SandboxError(400, "SB/VALIDATION", f"Fields not updatable in this sandbox: {sorted(unknown)}", [detail("SB/VALIDATION", n, n) for n in sorted(unknown)])
        stamp_dt = sandbox_now(request)
        previous = parse_dt(po["LastChangeDateTime"])
        if stamp_dt <= previous:
            stamp_dt = previous + timedelta(seconds=1)
        stamp = iso(stamp_dt)
        po["LastChangeDateTime"] = stamp
        store.put("PO", po["PurchaseOrder"], po, etag_for(stamp))
        store.audit("PATCH", request.url.path, role, 204, body, changed)
        return labelled(Response(status_code=204, headers={"ETag": etag_for(stamp)}))

    # ------------------------------------------------------------ dispatcher
    async def odata(request: Request) -> Response:
        service = request.path_params["service"]
        raw_path = unquote(request.path_params.get("path", "") or "")
        role = role_of(request)
        try:
            if service not in SERVICES:
                raise SandboxError(404, "SB/NOT_FOUND", f"Service {service} is not provided by this sandbox")
            params = request.query_params
            if raw_path in ("", "/"):
                if request.method != "GET":
                    raise SandboxError(405, "SB/METHOD", "Method not allowed on the service document")
                headers = {}
                if request.headers.get("X-CSRF-Token", "").lower() == "fetch":
                    headers["x-csrf-token"] = store.new_token()
                sets = list(ENTITY_SETS[service])
                return odata_json({"d": {"EntitySets": sets}}, 200, headers)
            if raw_path == "$metadata":
                return labelled(Response(metadata_xml(service), media_type="application/xml"))
            m = PATH_RE.match(raw_path)
            if not m:
                raise SandboxError(404, "SB/NOT_FOUND", f"Resource path not understood: {raw_path}")
            set_name, key_raw, nav = m.group("set"), m.group("key"), m.group("nav")
            key = parse_key(key_raw)
            expand = expand_set(params)
            if nav:
                expand.add(nav)

            if request.method in ("POST", "PATCH", "PUT", "DELETE"):
                body = {}
                raw = await request.body()
                if raw:
                    try:
                        body = json.loads(raw)
                    except json.JSONDecodeError as exc:
                        raise SandboxError(400, "SB/JSON", f"Request body is not valid JSON: {exc.msg}") from exc
                    if isinstance(body, dict) and "d" in body and isinstance(body["d"], dict):
                        body = body["d"]
                if service == SVC_PR and set_name == "A_PurchaseRequisitionHeader" and request.method == "POST" and not key:
                    return create_pr(request, body)
                if service == SVC_PR and set_name == "ReleasePurchaseRequisition" and request.method == "POST":
                    return decide_pr(request, release=True)
                if service == SVC_PR and set_name == "RejectPurchaseRequisition" and request.method == "POST":
                    return decide_pr(request, release=False)
                if service == SVC_PO and set_name == "A_PurchaseOrderItem" and request.method == "PATCH" and key:
                    return patch_po_item(request, key, body)
                raise SandboxError(405, "SB/METHOD", f"{request.method} is not supported on {set_name} in this sandbox")

            # ---- GET
            if service == SVC_PO:
                pos = store.list("PO")
                if set_name == "A_PurchaseOrder":
                    if key:
                        po = store.get("PO", key.get("_single", ""))
                        if not po:
                            raise SandboxError(404, "SB/NOT_FOUND", f"Purchase order {key.get('_single')} does not exist")
                        if nav == "to_PurchaseOrderItem":
                            return collection(request, [po_item_out(request, po, it, expand) for it in po["items"]])
                        return odata_json({"d": select_fields(po_header_out(request, po, expand), params)}, 200, {"ETag": etag_for(po["LastChangeDateTime"])})
                    rows = apply_filter(pos, parse_filter(params.get("$filter")))
                    return collection(request, [select_fields(po_header_out(request, po, expand), params) for po in page(rows, params)])
                if set_name == "A_PurchaseOrderItem":
                    flat = [{**it, "PurchaseOrder": po["PurchaseOrder"], "_po": po} for po in pos for it in po["items"]]
                    if key:
                        hit = next((f for f in flat if f["PurchaseOrder"] == key.get("PurchaseOrder") and f["PurchaseOrderItem"] == key.get("PurchaseOrderItem")), None)
                        if not hit:
                            raise SandboxError(404, "SB/NOT_FOUND", "Purchase order item does not exist")
                        if nav == "to_ScheduleLine":
                            expand.add("to_ScheduleLine")
                            return collection(request, po_item_out(request, hit["_po"], hit, expand)["to_ScheduleLine"]["results"])
                        return odata_json({"d": po_item_out(request, hit["_po"], hit, expand)}, 200, {"ETag": etag_for(hit["_po"]["LastChangeDateTime"])})
                    rows = apply_filter(flat, parse_filter(params.get("$filter")))
                    return collection(request, [po_item_out(request, f["_po"], f, expand) for f in page(rows, params)])
                if set_name == "A_PurchaseOrderScheduleLine":
                    rows = [{**sl, "PurchaseOrder": po["PurchaseOrder"], "PurchaseOrderItem": it["PurchaseOrderItem"]} for po in pos for it in po["items"] for sl in it.get("schedule_lines", [])]
                    rows = apply_filter(rows, parse_filter(params.get("$filter")))
                    base = base_url(request, SVC_PO)
                    return collection(request, [serialize(r, PO_SCHED, base, "A_PurchaseOrderScheduleLine", "A_PurchaseOrderScheduleLineType",
                                                          key_expr_multi(PurchaseOrder=r["PurchaseOrder"], PurchaseOrderItem=r["PurchaseOrderItem"], ScheduleLine=r["ScheduleLine"])) for r in page(rows, params)])
            if service == SVC_STOCK and set_name == "A_MatlStkInAcctMod":
                rows = apply_filter(store.list("STOCK"), parse_filter(params.get("$filter")))
                base = base_url(request, SVC_STOCK)
                return collection(request, [serialize(r, STOCK, base, "A_MatlStkInAcctMod", "A_MatlStkInAcctModType",
                                                      key_expr_multi(Material=r["Material"], Plant=r["Plant"], StorageLocation=r["StorageLocation"], Batch=r.get("Batch", ""), InventoryStockType=r["InventoryStockType"]))
                                            for r in page(rows, params)])
            if service == SVC_PR:
                prs = store.list("PR")
                if set_name == "A_PurchaseRequisitionHeader":
                    if key:
                        pr = store.get("PR", key.get("_single", ""))
                        if not pr:
                            raise SandboxError(404, "SB/NOT_FOUND", f"Purchase requisition {key.get('_single')} does not exist")
                        if nav == "to_PurchaseRequisitionItem":
                            return collection(request, [pr_item_out(request, pr, it) for it in pr["items"]])
                        return odata_json({"d": select_fields(pr_header_out(request, pr, expand), params)}, 200, {"ETag": etag_for(pr["LastChangeDateTime"])})
                    rows = apply_filter(prs, parse_filter(params.get("$filter")))
                    return collection(request, [select_fields(pr_header_out(request, pr, expand), params) for pr in page(rows, params)])
                if set_name == "A_PurchaseRequisitionItem":
                    flat = [{**it, "PurchaseRequisition": pr["PurchaseRequisition"], "_pr": pr} for pr in prs for it in pr["items"]]
                    if key:
                        hit = next((f for f in flat if f["PurchaseRequisition"] == key.get("PurchaseRequisition") and f["PurchaseRequisitionItem"] == key.get("PurchaseRequisitionItem")), None)
                        if not hit:
                            raise SandboxError(404, "SB/NOT_FOUND", "Purchase requisition item does not exist")
                        return odata_json({"d": pr_item_out(request, hit["_pr"], hit)})
                    rows = apply_filter(flat, parse_filter(params.get("$filter")))
                    return collection(request, [pr_item_out(request, f["_pr"], f) for f in page(rows, params)])
            raise SandboxError(404, "SB/NOT_FOUND", f"Entity set {set_name} is not provided by {service}")
        except SandboxError as err:
            body = error_body(err.code, err.message, err.details)
            if request.method != "GET":
                store.audit(request.method, request.url.path, role, err.status, None, body["error"]["code"], "rejected")
            return odata_json(body, err.status, err.headers)

    # ------------------------------------------------------------ sandbox utilities
    async def health(request: Request) -> Response:
        return odata_json({"status": "ok", "sap_connected": False, "label": LABEL, "services": list(SERVICES),
                           "purchase_requisitions": len(store.list("PR")), "db": str(store.path)})

    async def audit(request: Request) -> Response:
        return odata_json({"sap_connected": False, "label": LABEL, "events": store.audit_list()})

    async def reset(request: Request) -> Response:
        if role_of(request) != "system":
            return odata_json(error_body("SB/AUTH_ROLE", "Only role system may reset the sandbox", []), 403)
        store.reset()
        store.audit("POST", request.url.path, "system", 200, None, {"reset": True}, "reseeded")
        return odata_json({"reset": True, "sap_connected": False})

    async def root(request: Request) -> Response:
        return labelled(PlainTextResponse(
            "Procurement sandbox - not SAP connected.\n"
            f"OData services: {', '.join(f'{ODATA_ROOT}/{s}/' for s in SERVICES)}\n"
            "Utilities: /sandbox/health /sandbox/audit /sandbox/reset\nContract: CONTRACT.md\n"))

    routes = [
        Route("/", root),
        Route("/sandbox/health", health),
        Route("/sandbox/audit", audit),
        Route("/sandbox/reset", reset, methods=["POST"]),
        Route(ODATA_ROOT + "/{service}", odata, methods=["GET"]),
        Route(ODATA_ROOT + "/{service}/", odata, methods=["GET"]),
        Route(ODATA_ROOT + "/{service}/{path:path}", odata, methods=["GET", "POST", "PATCH", "PUT", "DELETE"]),
    ]
    app = Starlette(routes=routes)
    app.state.store = store
    return app


def parse_key(raw: str | None) -> dict:
    if raw is None:
        return {}
    raw = raw.strip()
    if "=" in raw:
        out = {}
        for part in re.findall(r"(\w+)='((?:[^']|'')*)'", raw):
            out[part[0]] = part[1].replace("''", "'")
        return out
    return {"_single": raw.strip("'")}


app = create_app()
