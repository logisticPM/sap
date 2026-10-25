# Progress report

_Synchronised 25 October 2026 against deliverable v50 (deployed, Site version 37) and v51 (in progress). The original v31 report is retained at the end._

## Product reached

We narrowed a broad responsive supply-network idea into one operational loop on a single synthetic case: **request → evidence review → missing confirmations → updated supplier assessment → supplier disclosure → planner decision → investigation, procurement review or closure**. CASE-1042 concerns synthetic OJ-250 orange juice at Toronto DC; NorthOrchard is a fictional supplier. The original SAP purchase plan (360 cases: 240 stock plus 120 inbound) is preserved throughout.

The deployed v50 task workspace pins the trigger, current blocker and original plan at the top, shows a decision card comparing the initial quantity-unknown assessment, the newly authorised supplier quote and the latest validated model recommendation, and folds previous attempts, failure records, exact source fields and call traces into collapsible evidence details. A planner can prepare a simulated procurement review packet (baseline, proposed quantity, quote, timing, conditions, evidence references). It is stored in the browser only; buyer approval stays pending, no purchase, booking, SAP write or submission occurs. The supplier view shows the disclosed quote and never the retailer's review.

## Architecture: from MCP demo to in-app agent harness

The 19 October line was an MCP server (`server.py`, FastMCP) that Claude Desktop called as a tool provider, with approvals in a separate planner console. From the v31 workbench onward the product runs its **own agent loop inside the service**: the backend calls Claude Sonnet 4.6 through OpenRouter, implements the tools itself (`read_sources`, `calculate_candidates`, `submit_assessment` and their manual/opportunity variants), validates every submission in the same handler that production uses, and then runs a separate model audit before anything can be disclosed. Rejections return `correction_required` with field-level findings to the model; the code never rewrites the model's answer. The MCP code remains in the project folder as the earlier evaluation harness and is not used by the cloud product.

## Status ledger

| Capability | Evidence / status (v50) | Limitation |
|---|---|---|
| Source discovery and reading through tools | Implemented. Real-model runs retained for v31 (3 archived), v48 A/B/C (34 calls) and v49 corrections (5 calls) | Inputs are synthetic and frozen; fixture authors know the material design |
| New reply changes the assessment | Implemented: carrier unknown → declined; QA stays unknown; v41 adds appended materials with a continue / clarify / pause gate | Deterministic rules supply and validate typed states; not independent discovery |
| Cited findings and follow-up selection | Real model output with server validation and a second model audit | Passing provenance and schema checks does not prove the prose true (v36 N2, v48 C) |
| Quantity proposal from authorised quote | v48: A reached a conditional 140-case proposal, B zero cases, C blocked for insufficient evidence. v49 added typed timing claims and quantity-consistency checks | Synthetic arithmetic under an authored 20% cancellation stress; not realised profit |
| Evidence-correction loop | v49: planner-triggered linked correction, four-call cap, originals preserved. A and C corrected and accepted | Repairs two specific failures; not general robustness |
| Procurement review handoff | v50: planner prepares a review packet; `purchase_authorized=false`, `booking_authorized=false`, `SAP connected=false` | Browser-local only; no requisition or order exists |
| Supplier authorisation and privacy | Backend projection plus workflow gate; supplier sees quote only, planner sees authorised version only | Demo roles lack identity and authentication |
| Interactive supplier reply (v51) | **In progress**: edit → save (free) → Agent check (paid) → preview → authorise → planner update; re-editing invalidates the check | Not yet validated; no VALIDATION record yet |
| Live activity | Persisted tool events on real runs; v50 task view polls read-only state | Public GitHub Pages site is historical replay only |
| SAP connection | Simulated business context and a proposed integration boundary | No real API read/write or tenant validation |
| Hidden demand | Research work and evidence constraints retained; v41 demand evidence contract defines what each record can and cannot establish | No component estimates latent demand; additional quantity remains unknown |
| Commercial benefit | Hypothesis and a frozen three-arm evaluation protocol | No measured outcomes, participants or willingness to pay |

## Budget

Cloud ledger observed after v49 and unchanged through v50: USD 3.0319 of a 4.00 cap (raised from 3.00 with explicit approval for at most four new calls each on items A and C). Total project authorisation USD 20, never reset. Item A has used 18 of 19 calls, item C 10 of 12, item B 11 calls. The v36 offline experiment added USD 0.37 to the local ledger. v50 made no model calls.

## What changed since the early concept

We withdrew a general claim that the complete policy reliably improves profit. Transfer gains were tiny and did not meet replication criteria; detection/response combinations could hurt. We stopped treating available supply as proof of additional demand, and stopped treating missing evidence as a failed condition. The product now preserves the original purchase plan unless demand, feasibility and approval are independently established.

Since v34 we learned three further things.

- **Free-form inference is possible but not release-ready (v36).** Six frozen novel packets scored 0/6; two revised packets matched coded labels 2/2, yet manual review found an unsupported exclusivity claim the model auditor had accepted. Coded label scores overstate semantic correctness.
- **Structure can pass while prose fails (v48 C).** The model withheld a structured quantity but kept an 80-case / CAD 770 recommendation in its text. A rule audit now blocks a numerical recommendation hidden in a withheld assessment, but this is a limited safeguard, not proof.
- **Correction must be linked, not overwritten (v49).** Field-only or disclaimer-only changes stay rejected; a complete replacement must pass the same handler. Failed attempts remain visible on the task flow.

The potentially valuable capability is evidence preparation across fragmented documents and replies, with bounded follow-up and explicit correction. Whether it beats a strong form/rule workflow remains unproven. The demo explicitly exposes that rules, not the model, enforce the allowed next action.

## Team decisions needed

1. Review whether the v50 task is recognisable and useful to a real planner and supplier coordinator.
2. Decide whether v51's interactive reply flow goes into the competition demo, once its validation record exists.
3. Identify a partner who can provide consecutive exception tasks, source timestamps and outcomes.
4. Run the three-arm evaluation before promising time savings or scaling the network.
5. Validate an SAP deployment boundary with an actual tenant owner before implementing procurement writes.
6. Regenerate the PPT; it still uses v31 screenshots.

---

## Original v31 report (24 October 2026, retained)

The latest workbench had independent supplier and planner entries, retained sessions, historical replay and local real-model modes, observable source/tool activity, version changes, explicit authorisation and a closed-loop stop decision. The planner saw only the released summary and typed conditions, not private supplier tool traces in the backend projection. Both the investigation and closure branches were implemented; there was no external inquiry delivery or alternative booking. SAP was represented by simulated business context and a proposed integration boundary. The follow-up Agent did not estimate latent demand. Commercial benefit was a hypothesis with an evaluation plan.
