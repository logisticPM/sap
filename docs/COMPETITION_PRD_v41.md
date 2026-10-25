# Demand Pulse Competition PRD v41

_Copied unchanged on 25 October 2026 from `deliverable/competition_v41_20261025/` in the full project folder. The `original/`, `FROZEN_TEST_PLAN.txt` and `VALIDATION.txt` files it mentions are in that folder, not in this repository; see [VALIDATION.md](VALIDATION.md) for the summary. Budget figures in the text were later raised (cloud cap USD 4); see [PROGRESS.md](PROGRESS.md)._

## Product and scope

Demand Pulse helps a retail replenishment planner and a supplier coordinator turn an uncertain additional-supply inquiry into an evidence-backed next action. CASE-1042 remains OJ-250 orange juice, NorthOrchard and Toronto DC. One task timeline connects demand review, incoming supplier replies, Agent interpretation, authorized disclosure and the planner's investigation or closure decision. No new module, forecasting engine or purchase execution is added.

This version preserves the original SAP purchase plan. It closes the workflow gap between a demand concern and supplier investigation; it does not establish a profitable order quantity. Earlier PRDs, deployed versions and session records remain retained.

## Demand evidence contract

The planner's real model review reads six original synthetic retailer records plus up to four appended materials. Each new material has a source label, scenario availability time and text; the service separately records actual entry time. Original records are available by 23 October 2026 at 14:35 UTC. New records advance the scenario information cutoff, and cannot claim availability in the future relative to actual entry. These are demonstration inputs, not live SAP, retail or social-network observations. The Agent writes its own short interpretation with an exact source quote. The Agent chooses continue, clarify or pause based on the combined evidence. A separate model audit reviews its reasoning against the sources; rules enforce provenance and permitted actions. Research papers are design support, never observations about this case.

| Record | Decision use | What it cannot establish |
|---|---|---|
| D-PLAN | Preserve the 360-case baseline; inspect timing and allocation | Stock 240 plus inbound 120 does not prove timely allocatable coverage |
| D-OOS | Reported unavailability motivates investigation of censored sales | Lost-demand amount, persistence or profitability |
| D-PROMO | Promotion is context to check against the forecast | Measured uplift or a verified delivery deadline |
| D-SUB | Investigate substitution with availability, prices and promotion controls | Treat substitute growth as recovered demand for this SKU |
| D-SOCIAL | Keep brand attention as an unverified contextual signal | Local purchasing intent, SKU conversion or a demand multiplier |
| PLAN-META | Request forecast provenance and existing corrections | Assume SAP omitted corrections or invalidate its plan |

The initial demand review is required before the planner can authorize further supply investigation. Only a current accepted continue judgment permits a human to authorize bounded investigation. An accepted clarify or pause judgment blocks that authorization. Completing the review alone does not open the gate. The planner may close without completing a paid review. The amount of additional demand, its persistence, allocatable coverage and the economic value of further investigation remain unknown. New material is manually entered synthetic text, not a connected dataset or a quantitative demand estimator. A new submission invalidates the previous judgment for authorization and suspends any active investigation mandate. Prior material, judgment, authorization and calls remain in history. A later continue judgment requires a new human authorization.

## One task and changing actions

1. Planner opens the inquiry and reviews the demand evidence. The planner can add material before or after a review. Actual source-reading events, cited interpretations, a comparison with the previous accepted judgment and remaining evidence gaps appear in the same timeline; detailed sources and traces remain collapsed.
2. Supplier enters a new synthetic reply. The real Agent reads all recorded replies, identifies applicable confirmations and conflicts, and proposes a focused question or next step.
3. Supplier previews the exact disclosure, adds a correction, keeps it private, or authorizes the checked version. The planner receives only that version and selected quoted evidence, never the private draft or complete source messages.
4. The planner sees what the authorized response changes for this inquiry, under rule-controlled action boundaries.
5. Planner authorizes limited investigation or closes and retains the original plan. No purchasing, booking, payment or external message is executed.

| New authorized evidence | Changed action | Demand judgment |
|---|---|---|
| Pending carrier decision or missing QA record | Clarify the unresolved conditions; do not label missing evidence a failure | Additional need remains unknown |
| Explicit applicable carrier refusal | Do not rely on that route; human may authorize a bounded alternative inquiry or close | Refusal does not prove the demand opportunity disappeared |
| Explicit confirmation replacing an earlier pending report | Stop re-asking that answered question; review remaining conditions | Supply confirmation does not create additional demand |
| All four operational conditions reported confirmed | Review the supply option and obtain incremental need, timing and commercial justification | No purchase authorization or quantified uplift |
| Conflicting applicable reports without explicit supersession | Reconcile the conflict | No automatic preference for the newest message |

A verified arrival after a validated demand window could justify stopping an option, but neither a verified arrival nor a validated window is established by this case. The promotion end date is not substituted for that missing window. Human closure remains available.

## Agent rules and human responsibility

Agent: read authorized records; produce original cited interpretations; reconcile supplier replies; identify unanswered conditions; draft a focused next action. Model interpretation is fallible.

Rules: enforce exact quotation and source access, required condition coverage, unknown additional quantity, retained baseline, disclosure boundaries, demand-review gate and budget. Evidence-use limits and the mapping from a current accepted investigation state to permitted controls are deterministic. The continue/clarify/pause selection and its explanation are real model outputs, not preset scenario wording. Narrow semantic backstops are not a proof of every possible statement. Both supplier drafts and demand reviews receive a separate model audit after source/schema/targeted rule checks. Two model calls agreeing is not independent real-world verification.

Supplier: check its statements and explicitly authorize disclosure. Planner: decide whether bounded investigation is worth pursuing or close. These are distinct from procurement approval, which is not implemented. Demo roles are views in a shared test session, not production identities or enterprise access control.

## Academic basis and external validity

[FreshRetailNet-50K, 2025](https://arxiv.org/html/2505.16319v1) supports studying censored demand using hourly sales and availability, with demand recovery and forecasting as separate modeling steps. It motivates D-OOS and the need for availability records. Its trained models and benchmark improvements are not results of our LLM workflow; this case does not run that estimator. Masked in-stock validation is not observation of naturally missing demand.

[Conlon and Mortimer, 2013, Demand Estimation under Incomplete Product Availability](https://www.aeaweb.org/articles?id=10.1257/mic.5.4.1) studies demand and substitution with incomplete availability in vending machines. It supports checking availability when interpreting substitute sales. It does not establish causal switching in our Toronto orange-juice case.

[Cui, Gallino, Moreno and Zhang, The Operational Value of Social Media Information, 2018](https://doi.org/10.1111/poms.12707) studies predictive value of social information using an online apparel retailer and Facebook alongside internal data. It motivates testing social signals for incremental out-of-sample value, rather than treating attention as demand. It does not establish a grocery uplift factor or local conversion rate. Publisher abstracts were used for the latter two papers; this is not a new full-paper replication.

Our earlier P2 and supplier-coordination simulations motivate investigating uncertainty and joint feasibility. Their numerical benefits are not transferred to this product. Artificial censor recovery, synthetic workflow tests and actual business outcomes remain distinct evidence categories.

## SAP and implementation boundaries

The SAP baseline is represented by frozen synthetic procurement records. No SAP API, live order, supplier ERP, email, carrier, social feed or DC scheduling system is connected. The prototype demonstrates a possible decision workflow around SAP; it neither replaces SAP forecasting nor establishes a verified SAP capability gap. Actual read/write integration, enterprise identity, supplier adoption and operational ownership remain pilot dependencies.

Total project authorization is USD 20. The existing USD 3 cloud allocation remains unchanged. Each browser can create one new v41 demand-input inquiry, with a 24-call cap for repeated material reviews and audits, alongside retained older inquiries. No charge or old-session counter is reset. Historical replay remains available without fresh model calls.

## Minimum validation and success criteria

Verify that real source reads precede accepted demand interpretations; missing evidence cannot become a quantity or invalidate the plan; no investigation mandate is accepted before demand review; pending is not refusal; a materially new supplier reply changes its applicable condition and next action; unpublished drafts remain absent from the planner view; disclosure releases exactly the authorized version; closure preserves the original plan and records.

Report failures and corrected outputs with their raw traces. Automated/UI checks establish implementation behavior on tested inputs, not demand-estimation accuracy. A later task comparison against current workflow and a strong rules form still needs actual participants and realistic records. Human time saved, supplier participation, faster arrival, service improvement, implementation cost and net replenishment profit remain unverified.

See VALIDATION.txt for the actual checks and live-run outcome of this release.


## New material changes the investigation decision

| New material | Judgment to evaluate | Authorization consequence |
|---|---|---|
| Social attention for another city or product | Explain why it does not add local demand evidence; retain any independently supported original trigger | No quantity or purchase permission; continuation only if a credible applicable trigger remains |
| Applicable report contradicts original availability without superseding it | Clarify the material conflict | Block new investigation authorization; suspend an active mandate |
| Scoped correction explicitly removes the original stockout trigger | Reassess whether any supported trigger remains; pause when none does | Keep baseline; allow further evidence or human closure, not an invented demand quantity |

The rule engine does not contain these input texts or force their verdicts. They form the frozen live test protocol. Newest receipt alone does not resolve a contradiction. A corrected report is still an unverified synthetic report; removing a trigger does not prove demand is zero. Supplier sees only neutral investigation-authorization status, never the private retailer inputs or interpretations.

Original v40 documents and source files are retained under original/. See FROZEN_TEST_PLAN.txt and VALIDATION.txt for actual test outcomes and failures.
