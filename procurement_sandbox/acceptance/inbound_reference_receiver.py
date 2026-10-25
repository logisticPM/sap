"""Reference receiver for POST /api/inbound: the contract's validation, authentication, deduplication
and matching rules with no Agent behind them. Use it to test a producer, or as the spec for the
application's real endpoint.

    python -m procurement_sandbox.acceptance.inbound_reference_receiver --port 5177 --secret dev-inbound-secret
"""

from __future__ import annotations

import argparse
import json
import re
import uuid
from datetime import datetime, timezone

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .simulate_inbound import SCHEMA, verify

KNOWN_PO = "4500001042"
KNOWN_SKU = "OJ-250"
MAX_BODY = 1_000_000
REQUIRED = ("schema", "source", "provider", "message_id", "edge_received_at", "from", "to", "subject", "text")


def create_receiver(secret: str, open_cases: set[str] | None = None) -> Starlette:
    state = {"messages": {}, "order": [], "cases": open_cases}

    def now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

    def validate(p: dict) -> list[str]:
        problems = [f"{k} is required" for k in REQUIRED if p.get(k) in (None, "")]
        if p.get("schema") != SCHEMA:
            problems.append(f"schema must be {SCHEMA}")
        if p.get("source") not in ("email", "simulator", "manual"):
            problems.append("source must be email, simulator or manual")
        mid = p.get("message_id")
        if mid and not (isinstance(mid, str) and mid.startswith("<") and mid.endswith(">")):
            problems.append("message_id must be an RFC 5322 Message-ID in angle brackets")
        if not isinstance(p.get("from"), dict) or not p["from"].get("address"):
            problems.append("from.address is required")
        if not isinstance(p.get("to"), list) or not p["to"]:
            problems.append("to must be a non-empty list")
        return problems

    def match(p: dict) -> tuple[str | None, bool, str]:
        """Contract section 4. Returns (case_id, needs_confirmation, reason)."""
        hints = p.get("routing_hints") or {}
        blob = f"{p.get('subject', '')}\n{p.get('text', '')}"
        pos = set(re.findall(r"\b(45\d{8})\b", blob))
        skus = {s.strip().upper() for s in re.findall(r"\b(OJ-\d{3}(?:\s+Family\s+1\s*L)?)\b", blob, re.IGNORECASE)}
        foreign_po = bool(pos - {KNOWN_PO})
        foreign_sku = bool(skus - {KNOWN_SKU})
        plus = hints.get("plus_address_case")
        if not plus:
            for addr in p.get("to", []):
                m = re.match(r"^case\+([^@]+)@", addr, re.IGNORECASE)
                if m:
                    plus = m.group(1)
        if plus and (state["cases"] is None or plus in state["cases"]):
            if foreign_po or foreign_sku:
                return None, True, "plus-address names a case but the text names a different PO or article"
            return plus, False, "plus-address"
        if KNOWN_PO in pos and KNOWN_SKU in skus and not foreign_po and not foreign_sku:
            case = next(iter(sorted(state["cases"]))) if state["cases"] else "CASE-1042"
            return case, False, "single open case named by PO and SKU"
        return None, True, "no decisive match; human confirmation required"

    async def inbound(request: Request):
        raw = await request.body()
        if len(raw) > MAX_BODY:
            return JSONResponse({"error": "too_large"}, 413)
        if request.headers.get("X-Inbound-Secret") != secret or not verify(secret, raw, request.headers.get("X-Inbound-Signature")):
            return JSONResponse({"error": "unauthorized"}, 401)
        try:
            p = json.loads(raw)
        except json.JSONDecodeError:
            return JSONResponse({"error": "schema", "details": ["body is not JSON"]}, 400)
        problems = validate(p)
        if problems:
            return JSONResponse({"error": "schema", "details": problems}, 400)
        received_at = now()
        mid = p["message_id"]
        if mid in state["messages"]:
            first = state["messages"][mid]
            return JSONResponse({"accepted": True, "inbound_id": first["inbound_id"], "received_at": first["received_at"], "case_id": first["case_id"],
                                 "needs_confirmation": first["needs_confirmation"], "duplicate_of": mid, "review_triggered": False}, 200)
        case_id, needs_confirmation, reason = match(p)
        rec = {"inbound_id": "in_" + uuid.uuid4().hex[:12], "received_at": received_at, "edge_received_at": p.get("edge_received_at"), "sent_at": p.get("sent_at"),
               "source": p["source"], "provider": p["provider"], "producer_header": request.headers.get("X-Inbound-Producer"), "case_id": case_id,
               "needs_confirmation": needs_confirmation, "match_reason": reason, "payload": p}
        state["messages"][mid] = rec
        state["order"].append(mid)
        return JSONResponse({"accepted": True, "inbound_id": rec["inbound_id"], "received_at": received_at, "case_id": case_id,
                             "needs_confirmation": needs_confirmation, "duplicate_of": None, "review_triggered": case_id is not None, "match_reason": reason}, 202)

    async def messages(request: Request):
        return JSONResponse({"count": len(state["order"]), "messages": [
            {k: v for k, v in state["messages"][m].items() if k != "payload"} | {"message_id": m, "subject": state["messages"][m]["payload"]["subject"]}
            for m in state["order"]]})

    app = Starlette(routes=[Route("/api/inbound", inbound, methods=["POST"]), Route("/api/inbound/messages", messages)])
    app.state.inbound = state
    return app


def main(argv=None) -> int:
    import uvicorn

    ap = argparse.ArgumentParser(description="Reference /api/inbound receiver (no Agent, no storage beyond memory)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5177)
    ap.add_argument("--secret", default="dev-inbound-secret")
    args = ap.parse_args(argv)
    uvicorn.run(create_receiver(args.secret), host=args.host, port=args.port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
