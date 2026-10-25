# Inbound contract — `POST /api/inbound`

The shape in which a supplier email reaches the application. One producer today, two later:

| Producer | Status | Notes |
|---|---|---|
| `simulate_inbound.py` (this folder) | **built** | Sends the ten acceptance tasks' emails in this exact shape. Declares `source: "simulator"` so every report can say mail receipt was simulated |
| Cloudflare Email Worker or a vendor inbound webhook (Postmark, Mailgun) | planned | A thin adapter maps the provider's event to this shape. Nothing else in the application changes |

The application owns the endpoint. This document is the contract both producers target and the acceptance scorer assumes.

## 1. Request

`POST /api/inbound` with `Content-Type: application/json` and two headers:

| Header | Required | Meaning |
|---|---|---|
| `X-Inbound-Secret` | yes | Shared secret configured on both sides. Wrong or missing → `401` |
| `X-Inbound-Signature` | yes | `sha256=` + hex HMAC-SHA256 of the raw request body with the same secret. Mismatch → `401`. Protects against a body altered in transit or a replay with a different body |
| `X-Inbound-Producer` | no | Free text naming the producer and version, for the audit log only |

Body (`schema` is fixed; unknown extra fields are ignored, not rejected):

```json
{
  "schema": "demand-pulse-inbound/1",
  "source": "email",
  "provider": "cloudflare-email-worker",
  "message_id": "<0d4e2c@northorchard.example>",
  "in_reply_to": "<request-1042@replies.example>",
  "references": ["<request-1042@replies.example>"],
  "edge_received_at": "2026-10-25T13:10:04Z",
  "sent_at": "2026-10-25T13:10:00Z",
  "from": {"address": "orders@northorchard.example", "name": "Priya"},
  "to": ["case+CASE-1042-T02@replies.example"],
  "cc": [],
  "subject": "Re: CASE-1042 OJ-250 additional supply, PO 4500001042",
  "text": "Correction to my earlier note. ...",
  "html": null,
  "attachments": [
    {"filename": "CIT-92-COA.pdf", "content_type": "application/pdf", "size": 48213, "sha256": "…", "content_base64": null}
  ],
  "routing_hints": {
    "plus_address_case": "CASE-1042-T02",
    "subject_tokens": ["CASE-1042", "PO 4500001042"],
    "po_numbers": ["4500001042"],
    "sku_tokens": ["OJ-250"]
  },
  "raw_mime_sha256": "…"
}
```

| Field | Required | Rules |
|---|---|---|
| `schema` | yes | Exactly `demand-pulse-inbound/1` |
| `source` | yes | `email` for a real mailbox, `simulator` for the acceptance simulator, `manual` for the v51 text box. The application copies it onto the stored message and into `case_export.json`'s `inbound[].source`. A report that contains any `simulator` or `manual` message must list "mail receipt simulated" under synthetic components |
| `provider` | yes | Producer name; free text |
| `message_id` | yes | RFC 5322 Message-ID including angle brackets. **This is the deduplication key.** Same `message_id` twice → the second is recorded as a duplicate of the first and triggers nothing |
| `in_reply_to`, `references` | no | Threading headers, used as routing hints only |
| `edge_received_at` | yes | UTC time the producer received the mail. Informational. **The application stamps its own `received_at` on arrival; that server time, not this field and not `sent_at`, is the start of elapsed time** |
| `sent_at` | no | The sender's `Date` header. A claim by the sender, never used for elapsed time |
| `from` | yes | `address` required, `name` optional |
| `to`, `cc` | yes / no | Full recipient addresses. The case plus-tag lives in `to` |
| `subject` | yes | May be empty string |
| `text` | yes | Plain-text body. If the mail was HTML-only, the producer converts and still fills `text`. Quoted history is **not** stripped by the producer; the application strips it before the Agent reads (plan item A4) |
| `html` | no | Raw HTML if present; stored, not read by the Agent |
| `attachments[]` | no | Metadata always; `content_base64` only when under the producer's size limit. The application stores attachments and marks them **unread evidence**; it does not parse them in this version |
| `routing_hints` | no | Computed by the producer from the plus-address, subject and body with simple patterns. **Advisory only.** The application performs its own match and must ask for confirmation when the hints disagree with each other or with the stored case |
| `raw_mime_sha256` | no | Hash of the raw message when the producer had it; lets a later audit prove the text was not altered |

Size limit: 1 MB body. Producers truncate `text` at 100 kB and set `attachments[].content_base64` to `null` beyond 2 MB per attachment.

## 2. Response

| Status | Body | Meaning |
|---|---|---|
| `202 Accepted` | `{"accepted": true, "inbound_id": "in_7f3…", "received_at": "2026-10-25T13:10:05Z", "case_id": "CASE-1042-T02", "needs_confirmation": false, "duplicate_of": null, "review_triggered": true}` | Stored, matched, review started (budget permitting) |
| `202 Accepted` | same with `"case_id": null, "needs_confirmation": true, "review_triggered": false` | Stored; the match is ambiguous or no case fits; a human must confirm before any paid review. Required behaviour for task T05 |
| `200 OK` | same with `"duplicate_of": "<original message_id>", "review_triggered": false` | Same `message_id` seen before; nothing new was created. Required behaviour for task T06 |
| `400 Bad Request` | `{"error": "schema", "details": ["message_id is required", …]}` | Shape violation; nothing stored |
| `401 Unauthorized` | `{"error": "unauthorized"}` | Bad secret or signature; nothing stored |
| `413 Payload Too Large` | | Over the size limit |
| `503 Service Unavailable` | `{"error": "budget_stopped"}` | Message stored, review **not** started because the case or project budget stop is active. `accepted` is still true in the sense that the mail is kept |

The application must respond within 10 seconds; a producer retries with the same body on timeout, which is why `message_id` deduplication is mandatory.

## 3. What the application must record

For each accepted message: the full body as received, the three times (`sent_at` as claimed, `edge_received_at`, server `received_at`), the match decision and whether confirmation was requested, the duplicate link, and the review it triggered. These feed `case_export.json`'s `inbound[]`, `matched_case`, `ambiguity_confirmation_requested` and `duplicate_detected`, which the scorer checks (acceptance README section 3).

## 4. Matching rules the producer relies on

The producer only computes hints. The application decides, using this order and stopping at the first decisive step:

1. **Plus-address** `case+<case_id>@…` names an open case → match, unless the subject or body names a different PO or SKU than that case → ask.
2. No plus-address: a single open case is named by PO number and SKU in subject or body → match.
3. Anything else (no case, several cases, a PO that does not exist, an article that differs from the case's SKU) → store, set `needs_confirmation`, start nothing.

Silent matching in step 3 is the critical error that task T05 exists to catch.

## 5. Simulator behaviour

`python -m procurement_sandbox.acceptance.simulate_inbound --target <url>/api/inbound --secret <s> --all`

- Builds one payload per inbound message in `tasks.json`, in task order, with `source: "simulator"`, `provider: "demand-pulse-acceptance-simulator/1"`.
- `to` is `case+<case_id>@<domain>` except for tasks whose expected `matched_case` is `null` (T05), which go to the bare `case@<domain>` address so the ambiguity is real.
- `message_id` is taken from the task when present (T06's duplicates share one) and otherwise generated deterministically as `<Txx-n@sim.demand-pulse>`, so a second simulator run replays the same ids and exercises deduplication.
- `edge_received_at` is the moment of sending; `sent_at` is the task's value.
- Signs every request, waits `--delay` seconds between messages of the same task, records every request and response in `sent_log.json` next to the exports folder.
- `--dry-run` writes the payloads to a folder and sends nothing. `--task T07` sends one task.

The simulator does not apply the tasks' `sandbox_setup` steps and does not play the human roles; those stay with whoever runs the round.
