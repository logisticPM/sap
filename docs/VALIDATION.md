# Validation and next experiment

_Synchronised 25 October 2026 against deliverable v50. Per-version VALIDATION records, traces and screenshots live in the full project folder under `deliverable/competition_v<NN>/`; this page summarises them._

## Evidence categories

1. **Implemented behavior:** code, local tests, browser walkthroughs and stored real-model traces.
2. **Public workflow evidence:** cited desk-study sources, with geography and task limitations.
3. **Synthetic/replay demonstration:** CASE-1042 and all departmental responses; no observed operational outcome.
4. **Unvalidated value:** active labor saved, fewer business errors, earlier arrival, reduced waste, ROI and adoption.

## What has been checked, by version

| Version | Checks run | Result | Model calls |
|---|---|---|---|
| v31 (24 Oct) | 21 workbench tests; real runs for initial review, reply review and alternative investigation | Passed; 12 model requests across the checks | Real, Claude Sonnet 4.6 |
| Handoff (24 Oct) | 24 portable backend tests; static replay contract; public page reachable without login; secret scan of 35 tracked files | Passed; see `HANDOFF_CHECKS.txt` | None |
| v33–v34 | 16 cloud evidence, authority and budget-envelope assertions; replay both branches; live-browser validation | Passed; cloud build succeeded | Within the 3.00 envelope |
| v36 (25 Oct) | Separate offline judgment component on 6 frozen novel packets, then 2 revised packets | **0/6**, then 2/2 by coded labels; manual review found an unsupported "sole blocker" claim the model auditor accepted. Not released | USD 0.37 local |
| v41 | Demand evidence contract: source reads precede accepted interpretations; missing evidence cannot become a quantity; no investigation mandate before demand review; disclosure releases exactly the authorised version | Passed on the frozen test plan; failures and corrected outputs retained with raw traces | 24-call cap per inquiry |
| v42–v46 | Timeline projection, privacy, stale-review, handoff and QA-scope tests; production builds | Passed; ledger stayed at 24/24 calls and USD 1.7735 | None (presentation only) |
| v47 | Deterministic evaluator on the synthetic business pack: quantities, time feasibility, cash contribution, candidate ranking, missing-data gates, adversarial mutations | Passed; an arithmetic reference, not an Agent response | None |
| v48 | 13 local tests (authorisation projections, supplier privacy, identical initial prompts, input-only bundle, calculator sensitivity, missing evidence, invalid citations, business authority, prose contradiction, non-mutating audit); browser checks on A/B/C | A: conditional 140 cases. B: zero cases. **C: failed** semantic review and was quarantined. Three exploratory cases, not a success rate | 34 real calls, USD 1.11 |
| v49 | 22 offline checks before any paid correction; 24 test-runner cases after approval; same handler in production and tests; mutated source times and quantities to confirm no scenario answer is encoded | Original A and C rejected; field-only or disclaimer-only fixes stayed rejected; live corrections of A and C accepted; originals preserved | 5 real calls, USD 0.147 |
| v50 | 6 offline tests (packet eligibility; C blocked; unshared/rejected/closed/supplier ineligible; no record mutation; supplier projection; no automatic invocation); build and syntax checks; browser walkthrough of A, B, C on the deployed site | Passed; Site version 37 deployed | None |
| v51 | Interactive supplier reply flow | **In progress; no VALIDATION record yet** | Pending |

Cloud ledger after v49: USD 3.0319 of 4.00. Project authorisation USD 20. These are engineering checks on frozen synthetic inputs, not business-impact estimates.

## Failures preserved on purpose

- v36: ambiguous `baseline` field mixed "plan retained" with "plan correct"; T5 treated absent carrier/QA evidence as `reported_no` and the same-model auditor accepted it.
- v48 A: prose said 250 excluded cases where the actual figure was 200; final prose confused DC arrival 08:00Z with store usable time 12:00Z. Both are visible in retained outputs; v49 fixed the timing claim with typed source-field references.
- v48 C: calculated on unconfirmed 100-case demand, omitted freight, and kept an 80-case / CAD 770 recommendation in prose after a null-quantity submission was structurally accepted. Blocked by a later rule audit, then corrected in v49 by the model removing the proposal and requesting the missing evidence.
- Across versions: citation syntax errors, malformed JSON, omitted purchase or variable costs, incorrect stress application, incomplete quoted ranges.

Exact quotes do not establish entailment: wrong prose can pass provenance checks. The model auditor shares failure modes with the generator. Narrow semantic backstops are not proof of every possible statement.

## Next falsifiable comparison

Use consecutive real additional-supply exception tasks when a partner is available; freeze task selection before examining outcomes. Preserve original timestamps and release information only when it was available. Start with an exploratory 10–20 tasks; do not interpret that sample as powered proof of savings.

Compare **current process**, **strong structured form/rules**, and **Agent-assisted evidence work**. Give all arms the same information, access, task limits and approval policy. The form/rule baseline must include known routing and deterministic checks used by the Agent harness, including the v49 typed-claim and quantity-consistency checks. Record which work is performed by rules versus model. Randomize or counterbalance task assignment to reduce learning effects; freeze rubric and budgets before scoring.

Primary safety measures: unsupported commitments, wrong quantities or units, missed conditions, stale evidence, unauthorized disclosure, duplicate clarification, numerical recommendations hidden in withheld assessments, and wrong next action. Independent reviewers use source-linked answer keys and adjudicate disagreements. Measure actual active human work separately for planner and supplier; record elapsed waiting, production and transport separately. Event gaps are not labor time. Do not estimate a percentage saving without participant measurements.

Proceed only if critical errors do not worsen and total human burden improves enough to cover model, verification, onboarding and integration costs. If forms and rules perform as well, prefer them. If production and transport dominate or suppliers will not participate, reconsider the product wedge.

## Handoff limits

Public replay is single-browser state with no authentication. Test data is synthetic and inspectable. Model outputs are retained evidence, not independently verified truth. The portable backend is not a deployment security audit and was not connected to a real SAP tenant or supplier system. The cloud workspace requires the team testing code; its roles are views in a shared test session, not enterprise identities.
