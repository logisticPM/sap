# Progress report

## Product reached

We narrowed a broad responsive supply-network idea into one operational loop: **request → evidence review → missing confirmations → updated supplier assessment → supplier disclosure → planner decision → investigation or closure**. CASE-1042 concerns synthetic OJ-250 orange juice at Toronto DC. NorthOrchard is a fictional supplier in this scenario.

The latest workbench has independent supplier and planner entries, retained sessions, historical replay and local real-model modes, observable source/tool activity, version changes, explicit authorization and a closed-loop stop decision. The planner sees only the released summary/typed conditions, not private supplier tool traces in the backend projection.

## Status ledger

| Capability | Evidence/status | Limitation |
|---|---|---|
| Source discovery and reading through tools | Implemented; three archived real-model runs are included | Inputs are synthetic and frozen |
| New reply changes the assessment | Implemented: carrier unknown → declined; QA stays unknown | Deterministic rules supply/validate typed states; not independent model discovery |
| Cited findings and follow-up selection | Real model output with server validation | Passing validation does not prove all prose true |
| Investigation or closure | Both branches implemented | No external inquiry delivery or alternative booking |
| Supplier authorization | Backend projection + workflow gate implemented | Demo roles lack identity/authentication |
| Live activity | Actual persisted tool events on local real runs | Public website is historical only |
| SAP connection | Simulated business context and proposed integration boundary | No real API read/write or tenant validation |
| Hidden demand | Research work and evidence constraints retained | Current follow-up Agent does not estimate latent demand |
| Commercial benefit | Hypothesis and evaluation plan | No measured customer outcomes or willingness to pay |

## What changed since the early concept

We withdrew a general claim that the complete policy reliably improves profit. Transfer gains were tiny and did not meet replication criteria; detection/response combinations could hurt. We stopped treating available supply as proof of additional demand, and stopped treating missing evidence as a failed condition. The product now preserves the original purchase plan unless demand, feasibility and approval are independently established.

The potentially valuable capability is evidence preparation across fragmented documents and replies, with bounded follow-up. Whether it beats a strong form/rule workflow remains unproven. The demo explicitly exposes that rules, not the model, enforce the allowed next action.

## Team decisions needed

1. Review whether the task is recognizable and useful to a real planner and supplier coordinator.
2. Identify a partner who can provide consecutive exception tasks, source timestamps and outcomes.
3. Run the three-arm evaluation before promising time savings or scaling the network.
4. Validate an SAP deployment boundary with an actual tenant owner before implementing procurement writes.
