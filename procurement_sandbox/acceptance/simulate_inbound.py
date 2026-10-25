"""Send the acceptance tasks' emails to POST /api/inbound in the contract shape (INBOUND_CONTRACT.md).

    python -m procurement_sandbox.acceptance.simulate_inbound --target http://127.0.0.1:5173/api/inbound --secret dev --all
    python -m procurement_sandbox.acceptance.simulate_inbound --task T06 --dry-run --out payloads/

Mail receipt through this tool is SIMULATED. Every payload says so (source: "simulator"); every report must too.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .freeze import TASKS

SCHEMA = "demand-pulse-inbound/1"
PRODUCER = "demand-pulse-acceptance-simulator/1"
PO_RE = re.compile(r"\b(45\d{8})\b")
SKU_RE = re.compile(r"\b(OJ-\d{3}(?:\s+Family\s+1\s*L)?)\b", re.IGNORECASE)
CASE_RE = re.compile(r"\b(CASE-\d{4}(?:-T\d{2})?)\b")


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def sign(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def verify(secret: str, body: bytes, signature: str | None) -> bool:
    return bool(signature) and hmac.compare_digest(sign(secret, body), signature)


def routing_hints(to: list[str], subject: str, text: str) -> dict:
    plus = None
    for addr in to:
        m = re.match(r"^case\+([^@]+)@", addr, re.IGNORECASE)
        if m:
            plus = m.group(1)
    blob = f"{subject}\n{text}"
    return {
        "plus_address_case": plus,
        "subject_tokens": sorted(set(CASE_RE.findall(subject)) | {f"PO {p}" for p in PO_RE.findall(subject)}),
        "po_numbers": sorted(set(PO_RE.findall(blob))),
        "sku_tokens": sorted({s.strip() for s in SKU_RE.findall(blob)}),
    }


def build_payload(task: dict, index: int, msg: dict, domain: str, edge_received_at: str | None = None) -> dict:
    ambiguous_task = task["expected"].get("matched_case") is None
    to = [f"case@{domain}" if ambiguous_task else f"case+{task['case_id']}@{domain}"]
    message_id = msg.get("message_id") or f"<{task['id']}-{index}@sim.demand-pulse>"
    name, address = None, msg["from"]
    m = re.match(r"^(.*?)\s*<([^>]+)>$", address)
    if m:
        name, address = m.group(1).strip() or None, m.group(2)
    text = msg["body"]
    return {
        "schema": SCHEMA,
        "source": "simulator",
        "provider": PRODUCER,
        "message_id": message_id,
        "in_reply_to": msg.get("in_reply_to"),
        "references": msg.get("references", []),
        "edge_received_at": edge_received_at or utcnow_iso(),
        "sent_at": msg.get("sent_at"),
        "from": {"address": address, "name": name},
        "to": to,
        "cc": [],
        "subject": msg.get("subject", ""),
        "text": text,
        "html": None,
        "attachments": [
            {"filename": a["filename"], "content_type": a.get("content_type", "application/octet-stream"), "size": a.get("size", 0),
             "sha256": a.get("sha256"), "content_base64": None}
            for a in msg.get("attachments", [])
        ],
        "routing_hints": routing_hints(to, msg.get("subject", ""), text),
        "raw_mime_sha256": hashlib.sha256(f"{message_id}\n{msg.get('subject', '')}\n{text}".encode("utf-8")).hexdigest(),
        "simulator": {"task_id": task["id"], "sequence": index, "note": "Synthetic business facts; mail receipt simulated"},
    }


def payloads_for(tasks_doc: dict, task_ids: list[str] | None, domain: str) -> list[dict]:
    out = []
    for task in tasks_doc["tasks"]:
        if task_ids and task["id"] not in task_ids:
            continue
        for i, msg in enumerate(task["inbound"], start=1):
            out.append(build_payload(task, i, msg, domain))
    return out


def send(payload: dict, target: str, secret: str, http: httpx.Client) -> dict:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {"Content-Type": "application/json", "X-Inbound-Secret": secret, "X-Inbound-Signature": sign(secret, body), "X-Inbound-Producer": PRODUCER}
    started = time.monotonic()
    try:
        r = http.post(target, content=body, headers=headers)
        status, resp_body = r.status_code, (r.json() if "json" in r.headers.get("content-type", "") else r.text[:500])
    except httpx.HTTPError as exc:
        status, resp_body = 0, f"transport error: {exc}"
    return {"task_id": payload["simulator"]["task_id"], "sequence": payload["simulator"]["sequence"], "message_id": payload["message_id"],
            "to": payload["to"][0], "sent_at_wallclock": utcnow_iso(), "status": status, "response": resp_body,
            "elapsed_ms": round((time.monotonic() - started) * 1000)}


def run(target: str | None, secret: str, task_ids: list[str] | None, domain: str, delay: float, dry_run: bool, out: Path | None,
        http: httpx.Client | None = None, tasks_path: Path = TASKS) -> list[dict]:
    tasks_doc = json.loads(tasks_path.read_text(encoding="utf-8"))
    items = payloads_for(tasks_doc, task_ids, domain)
    log: list[dict] = []
    if dry_run:
        out = out or Path("inbound_payloads")
        out.mkdir(parents=True, exist_ok=True)
        for p in items:
            (out / f"{p['simulator']['task_id']}-{p['simulator']['sequence']}.json").write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding="utf-8")
            log.append({"task_id": p["simulator"]["task_id"], "sequence": p["simulator"]["sequence"], "message_id": p["message_id"], "to": p["to"][0], "status": "dry-run"})
        return log
    if not target:
        raise SystemExit("--target is required unless --dry-run")
    client = http or httpx.Client(timeout=15.0)
    last_task = None
    for p in items:
        if last_task == p["simulator"]["task_id"] and delay:
            time.sleep(delay)
        entry = send(p, target, secret, client)
        log.append(entry)
        print(f"{entry['task_id']}#{entry['sequence']} -> {entry['status']} {json.dumps(entry['response'], ensure_ascii=False)[:160]}")
        last_task = p["simulator"]["task_id"]
    if out:
        out.mkdir(parents=True, exist_ok=True)
        (out / "sent_log.json").write_text(json.dumps({"producer": PRODUCER, "target": target, "mail_receipt": "simulated", "entries": log}, indent=2, ensure_ascii=False), encoding="utf-8")
    return log


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Simulate inbound supplier emails for the acceptance tasks")
    ap.add_argument("--target", help="Full URL of the application's /api/inbound")
    ap.add_argument("--secret", default="dev-inbound-secret")
    ap.add_argument("--task", action="append", help="Task id, repeatable (default: --all)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--domain", default="replies.example", help="Case mailbox domain used in the to: address")
    ap.add_argument("--delay", type=float, default=1.0, help="Seconds between messages of the same task")
    ap.add_argument("--dry-run", action="store_true", help="Write payloads to --out and send nothing")
    ap.add_argument("--out", type=Path, help="Folder for sent_log.json (or payloads with --dry-run)")
    args = ap.parse_args(argv)
    task_ids = None if args.all or not args.task else args.task
    log = run(args.target, args.secret, task_ids, args.domain, args.delay, args.dry_run, args.out)
    failures = [e for e in log if e["status"] not in ("dry-run", 200, 202)]
    print(f"{len(log)} message(s); {len(failures)} not accepted")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
