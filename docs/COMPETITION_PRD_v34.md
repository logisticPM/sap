# Demand Pulse — competition PRD v34

Status: implemented prototype with synthetic business evidence; no customer validation or measured operational benefit. Supersedes the competition narrative, not prior experimental records. Original documents and v33 source snapshots are retained.

## Product and user job

For a retail replenishment planner handling a possible demand change, Demand Pulse organizes demand evidence and a supplier response into a bounded decision: investigate, keep the purchase on hold, or close additional-supply follow-up. A supplier coordinator controls disclosure of operational findings. The SAP purchase plan remains the baseline.

The product does not promise a recovered hidden-demand quantity, an optimal order, an earlier delivery or new SAP revenue. Its testable value proposition is less manual evidence reconciliation and fewer critical interpretation/authority errors, measured against a strong form-and-rule workflow.

## Same case, stronger trigger

CASE-1042 / OJ-250 orange juice / NorthOrchard / Toronto DC. All business records below are synthetic, copied unchanged from the v16 design fixture. Their timestamps describe when the information becomes available, not necessarily when the underlying event occurred.

| Source | Available on 23 Oct 2026, UTC | Content | Permitted implication |
|---|---|---|---|
| D-PLAN | 09:00 | 360-case plan for 24–28 Oct; stock 240 and inbound 120; method/corrections unknown | Retain baseline; arithmetic does not prove allocatable or time-phased coverage |
| D-OOS | 14:30 | Retail unavailability after noon on 22 Oct, with zero recorded sales during unavailable hours | Investigate censored demand; do not interpret zero sales as zero demand or infer a lost-sales quantity |
| D-PROMO | 14:31 | Approved promotion scheduled through 28 Oct | Check the opportunity window; not proof of uplift, persistence or an exact receiving deadline |
| D-SUB | 14:32 | Comparable substitute sales increased; controls incomplete | Supporting risk signal, not causal substitution volume |
| D-SOCIAL | 14:33 | Brand discussion, locality/SKU/conversion unverified | Attention signal only; no uplift multiplier |
| PLAN-META | 14:35 | Forecast inputs and correction treatment missing | Do not assume SAP omitted stockout, substitution or promotion corrections |

The inquiry is triggered by unavailable retail hours during a scheduled promotion, not by a fabricated forecast threshold. Additional demand, incremental need and justified purchase quantity stay unknown. Retail unavailable hours are distinct from current DC inventory.

Source provenance: `deliverable/competition_v16_20261024/case_1042_v16.json`. Earlier SAP mock context: `demand_pulse_workflow_v24/procurement.py`. These are design records, not observed retailer transactions. The new cloud `lib/demand-records.json` preserves the six original source records. FRN observations are not mapped to OJ-250/Toronto and are not evidence for this case's order quantity.

## Workflow and meaningful changes

1. Incoming quantity-free inquiry opens a retained task. Supplier evidence review starts in Live Agent mode. No message is sent to a real supplier.
2. Supplier Agent reads stock/pack records, conditional arrival, current draft and unresolved operational prerequisites. Follow-up topics remain unsent drafts.
3. A simulated logistics reply explicitly declines the carrier; a QA reply cannot locate the release record. Real re-review changes carrier state from unknown to not satisfied, while QA remains unknown. The original route cannot be treated as a delivery commitment.
4. Supplier authorizes the operational assessment. This is not a retail procurement approval.
5. Before alternative investigation, the planner asks the real Agent to review all six retailer demand records. Findings cite the records actually read. The server enforces unknown additional quantity and purchase hold; these gates are rule outputs, not model discoveries.
6. The planner sees two dimensions: demand justification remains incomplete; the original route has failed. The planner may authorize limited alternative fact-finding or close follow-up while preserving the baseline. Review completion does not establish a positive business case.
7. Alternative investigation has its own real model run and separate supplier disclosure. No alternative availability or quote is invented. Closure retains past evidence and decisions.

Historical Replay adds a deterministic demand-evidence checklist. It does not relabel that checklist as an archived or live demand-Agent run. Archived supplier traces remain unchanged. Existing live sessions keep their earlier runs; they must complete the newly required demand review before a new alternative mandate.

## Continue, hold and stop contract

| Evidence/state | Next action | Authority and limitation |
|---|---|---|
| Missing forecast metadata, unclear uplift, unmatched social data | Hold additional purchase; identify missing evidence | Unknown is not evidence of no opportunity |
| Explicit carrier refusal | Stop relying on that route; consider a bounded alternative inquiry | Does not prove all supply options are impossible |
| Missing QA release record | Request evidence; no shipment clearance | Unknown is not QA rejection |
| Supplier offers supply | Reconcile supply feasibility only | Does not increase estimated demand |
| Human authorizes investigation | Prepare an alternative inquiry | Does not permit booking, payment or procurement |
| Human closes inquiry | Stop this follow-up; retain original plan and record | A human disposition, not proof that demand was zero |
| Verified cutoff missed without renewed acceptance | Stop relying on expired offer | Future integration criterion; scenario clock remains frozen, no wall-clock expiry inferred |
| Verified feasible arrival after a validated need window | Stop that opportunity/option or request a new rationale | Not established here: promotion end date alone is insufficient |
| Reliable incremental-need assessment supports no extra order | Keep baseline and close after disposition | Not established here; no estimator or conclusion is fabricated |

The last three evidence-based criteria are specified for a future real-data trial, not shown as verified outcomes. There is no demo toggle that manufactures a favorable demand result.

## Agent, rules and people

Agent: read authorized records, interpret non-standard text, reconcile versions, produce cited findings and unresolved follow-up topics. The work-completed view reflects actual retrieved sources, responses and artifacts.

Rules: source/role gates, known typed conditions, null additional quantity, limited state transitions, disclosure, original budget and no purchase tool. Rules do not certify truth or estimate uplift.

Supplier: verify and authorize each external assessment. Planner: decide whether further investigation is worth the coordination burden or close. Procurement approval remains a separate future SAP workflow, not a button that overrides missing evidence.

Disconnected work remains explicit: retrieving missing metadata, sending and chasing messages, obtaining quotes, booking capacity, verifying receiving and QA, procurement approval/write-back. Task decomposition is not measured time saved and must not be presented as such.

## SAP connection and stakeholder value

Proposed read context is S/4HANA PO/item, quantity/unit, required date and procurement status, with authorized plan/inventory context. Proposed return is an approved, version-linked disposition/change request through existing procurement approval. No SAP tenant, API read or write is connected; exact mapping and implementation cost remain unverified.

Retailer hypothesis: fewer reconciliation steps and critical misinterpretations. Supplier hypothesis: reuse operational replies and control disclosure instead of repeatedly explaining conditions. SAP hypothesis: richer supplier participation around existing customer procurement workflows. None proves willingness to adopt, new licenses, partner revenue or profit.

## Minimal validation before broader rollout

Use the same inquiry and evidence releases in three arms: current-flow hypothesis (documents/mail), strong structured form/rules, and Agent assistance. Rules, source access, timestamps and permissions are identical. Include unresolved QA, superseded stock, conditional arrival, carrier refusal and uncertain demand. Do not give only the Agent a better source packet.

Measure critical errors, unsupported demand/order claims, missed unresolved items, duplicate answered questions, correctly scoped handoffs and task completion. Measure actual human active time only when participants interact; event intervals or model latency are not human labor. Include verification/correction time and supplier work, not just planner clicks. Present non-participant automated tests only as implementation checks.

The immediate deliverable is the test protocol and task packet, not a claim that the Agent wins. See MINIMAL_VALIDATION_v34.md. A real, consented, de-identified supplier task is required for external validity; no retailer contact is currently available.

## Competition presentation

Lead with the planner's task and the six source limitations. Demonstrate the changed carrier fact and the unchanged demand uncertainty. Show the two human choices, then the retained disposition. Reveal traces only to substantiate what the Agent actually read. Explain SAP's proposed connection and implementation gap. Do not show simulated profit as achieved benefit.

Problem definition: specific user and trigger, with direct validation absent. Solution: bounded evidence reconciliation and decision support. Prototype: real model plus synthetic data, explicit replay. Implementation: authorization, integration, real-task testing before rollout. Stakeholders: disclosure burden and adoption hypotheses. Communication: one case and one honest outcome, including stopping.

## Acceptance criteria

- No invented uplift, additional quantity, successful quote or committed arrival.
- Demand Agent uses only the six authorized retailer records, with actual citations.
- Supplier view excludes retailer demand source details; planner view excludes unshared supplier sources.
- Alternative investigation is blocked until demand review/checklist is complete; closing remains possible.
- Unknown QA and explicit carrier refusal remain different states.
- Replay cannot claim a fresh model run; failed live runs do not fall back.
- Original records, versions and cumulative budget are retained.
- No measured labor, fulfillment or financial benefit claimed without participants and observed outcomes.
