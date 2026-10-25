# Engineering acceptance kit

Ten frozen tasks that test whether the chain **email → case match → review → disposition → human approval → procurement sandbox receipt** runs end to end, plus a freeze tool and a scorer. This is engineering acceptance. It says nothing about time saved or business value, and the report is written so that it cannot be read that way.

**Author note.** The tasks were written by Claude on the development side while the build was being accelerated without a team. The author knows the harness design. This is therefore not an independent or blinded test. When a person outside the development pair becomes available, they should rewrite the email bodies and answer keys before any result is cited.

## 1. Files

| File | Purpose |
|---|---|
| `tasks.json` | Ten tasks: synthetic inbound emails, sandbox setup steps, expected outcomes, answer keys |
| `freeze.py` | Hashes `tasks.json` into `freeze.json` before the first run; `--check` verifies nothing changed |
| `score.py` | Reads one `case_export.json` per task from the application, cross-checks the sandbox's own records, writes a report |
| `../client.py` | Reference client used by the scorer to read the sandbox |

## 2. The ten tasks

| Id | Scenario | Correct end state |
|---|---|---|
| T01 | Ambiguous reply | WAIT with owner, deadline, question; no PR |
| T02 | Explicit revision completing all conditions | CHANGE 140 CS; PR created; released; closed |
| T03 | Partial fulfilment | CHANGE 60 CS plus WAIT for 80; PR for 60 only |
| T04 | Quantity in bottles | CHANGE 140 CS (3,360 bottles / 24); PR in cases |
| T05 | Reply matches the wrong order | Ask for confirmation; no paid review, no PR |
| T06 | Duplicate email and a forward | One review, one PR |
| T07 | Stale proposal after the PO changed | 412 from sandbox; re-review required; no PR |
| T08 | Rejected by procurement | PR created, then returned with reason; case open |
| T09 | Supply offered, no demand basis | KEEP or WAIT; no PR; no quantity from 7,200 bottles |
| T10 | Submission failure with unknown outcome | 502 then retry with the same key; exactly one PR |

Every task uses its own case id (`CASE-1042-T01` … `T10`) so the sandbox's duplicate guard and the scorer can tell them apart. All tasks share the seed baseline: PO `4500001042` item `00010`, 120 cases inbound 27 Oct, 240 on hand, authorised quote CIT-92 at CAD 24, **approved buyer request 140 cases**. That approved request is the only quantity basis; supply figures never become demand.

## 3. Export contract: `case_export.json`

The application writes one file per task after the run, named `T01.json` … `T10.json`. The scorer treats the export as the application's claim and the sandbox as the truth; a claimed PR that the sandbox does not have fails the task.

```json
{
  "task_id": "T02",
  "case_id": "CASE-1042-T02",
  "synthetic_components": ["email business facts", "supplier identity", "approver identity"],
  "inbound": [
    {"message_id": "<...>", "received_at": "2026-10-25T13:10:04Z", "from": "orders@northorchard.example",
     "subject": "...", "matched_case": "CASE-1042-T02", "duplicate_of": null, "source": "email"}
  ],
  "matched_case": "CASE-1042-T02",
  "ambiguity_confirmation_requested": false,
  "duplicate_detected": false,
  "reviews": [
    {"id": "rev-1", "started_at": "...", "accepted_at": "...", "model_calls": 3, "sources_read": ["D-PLAN", "PO-4500001042", "MSG-1"], "outcome": "accepted"}
  ],
  "disposition": {
    "kind": "CHANGE", "quantity": 140, "unit": "CS",
    "wait": null
  },
  "submission": {
    "attempts": [
      {"at": "...", "idempotency_key": "dp-...", "state": "submitted_awaiting_procurement_approval", "status_code": 201}
    ],
    "state": "submitted_awaiting_procurement_approval",
    "purchase_requisition": "1000000001",
    "evidence_version": "ev-..."
  },
  "approval": {"state": "approved", "by_role": "procurement_approver", "at": "..."},
  "closed_at": "...",
  "timestamps": {
    "received_at": "...", "review_started": "...", "review_accepted": "...",
    "disclosure_authorized": "...", "change_submitted": "...", "change_approved": "...", "closed": "..."
  },
  "human_actions": [
    {"role": "supplier", "action": "authorize_disclosure", "at": "...", "active_seconds": 38},
    {"role": "planner", "action": "authorize_submission", "at": "...", "active_seconds": 52},
    {"role": "procurement_approver", "action": "release", "at": "...", "active_seconds": 20}
  ],
  "ui_states_shown": ["submitted_awaiting_procurement_approval", "approved_by_procurement"]
}
```

Field rules:

- `disposition.kind` is `CHANGE`, `KEEP`, `WAIT` or `null`. For `WAIT`, `disposition.wait` must carry `owner`, `deadline` and `question`.
- `submission.attempts[].state` uses the client's state names (CONTRACT.md section 7): `submitted_awaiting_procurement_approval`, `already_submitted`, `already_submitted_for_this_evidence`, `baseline_changed_re_review_required`, `rejected_before_submission`, `not_permitted_for_role`, `submission_failed_outcome_unknown`.
- `approval.state` is `approved`, `returned` or `null`; `approval.by_role` must be `procurement_approver` for an approval to count.
- `timestamps` are server-side and must be monotonic in the order listed. The scorer fails typed or out-of-order timestamps.
- `human_actions[].active_seconds` is the focus time captured by the application for that step.
- `ui_states_shown` lists every state the planner screen displayed; showing `change_completed` after a failure or a 412 is a critical error.

## 4. Running an acceptance round

1. Start the sandbox fresh: `python -m procurement_sandbox --db acceptance_run.sqlite`, or `POST /sandbox/reset` with role `system`.
2. Freeze: `python -m procurement_sandbox.acceptance.freeze`. Commit `freeze.json` before sending the first email.
3. For each task, send the inbound emails from `tasks.json` to the case mailbox from an ordinary mail client (or, while no mailbox exists, through the inbound simulator the application provides; declare that in `synthetic_components`). Apply the task's `sandbox_setup` steps at the stated moment. Play the planner, supplier and procurement approver roles as the task requires.
4. Export `T01.json` … `T10.json` from the application into one folder.
5. Score: `python -m procurement_sandbox.acceptance.score --exports <folder> --base http://127.0.0.1:8081 --out report.md`.

The scorer refuses to run if `tasks.json` no longer matches `freeze.json`, unless `--allow-unfrozen` is passed, in which case the report is headed UNFROZEN.

## 5. What a pass means and does not mean

A pass means the chain ran and the sandbox records agree with the application's claims on these ten authored inputs. It does not mean the model would behave the same on unseen replies, that a planner saved time, or that a customer would pay. Those need the separate business validation with real tasks and participants described in the plan.
