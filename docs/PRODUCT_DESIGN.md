# Product design — one replenishment exception

## Positioning and user job

Demand Pulse is a proposed coordination/evidence workbench beside a retailer's procurement workflow. A retail planner needs to decide whether to keep pursuing additional supply when demand changes. A supplier coordinator must reconcile current stock/pack information, arrival conditions and departmental replies before sharing a defensible response. We retain the SAP purchase plan as the baseline.

Success at this stage means a traceable, decision-ready assessment **or an explicit unresolved blocker**, not automatically placing an additional order. The supplier's supply option does not establish latent demand. No assumed 960-case demand is substituted for evidence.

## Current workflow and proposed change

| Work | Existing workflow hypothesis, grounded in desk research | Demo behavior |
|---|---|---|
| Receive request | Read order/inquiry context and find missing facts | One CASE-1042 request with baseline retained |
| Reconcile documents | Compare email, stock snapshots, pack units, route conditions | Agent reads available synthetic records and cites findings |
| Chase missing confirmations | Ask logistics/QA/DC contacts; check answered questions | Model selects unresolved topics; rules route them to owners; drafts remain unsent |
| Process reply | Re-read earlier conditions and update interpretation | Simulated carrier decline changes the assessment; missing QA stays unknown |
| Share externally | Decide what may be disclosed | Supplier authorizes scoped summary and conditions |
| Decide next step | Pursue alternative or abandon extra supply | Planner authorizes investigation only, or closes follow-up |

These are task hypotheses, not a measured time-and-motion study. The product must reduce total work across both sides, not merely move work to suppliers.

## Information and authority contract

| Actor | Can do | Cannot do |
|---|---|---|
| Agent | Discover/read tools; reconcile source text; draft cited findings; select unresolved topics | Invent missing demand; certify business truth; grant approval; send external messages |
| Rules | Validate typed conditions/citations; enforce stage and revision gates; route owners; retain records | Be represented as model inference or physical verification |
| Supplier | Preview and authorize the shared assessment in this workflow | Approve the retailer's purchase; equate disclosure with commitment |
| Planner | Authorize alternative investigation or stop follow-up | Convert missing QA/booking evidence into verified fulfillment |
| SAP procurement/approval owner | Proposed authority for an approved procurement change | Not connected in this build |

Quantity unit is cases for OJ-250 business records. FRN normalized units are unrelated. Unknown, not satisfied and confirmed are distinct states. Arrival is conditional until supporting conditions are established. New evidence invalidating a condition changes the recommendation; permission alone never fills a missing fact.

## State sequence

Request received → supplier review → new reply reviewed privately → supplier authorizes update → planner decision. Stop closes the local follow-up while preserving prior records. Alternative investigation creates a bounded fact-gathering mandate. In the local real-model mode the new result requires a separate supplier disclosure before the planner sees it. The historical alternative branch reuses an archived scoped release and labels it accordingly. Neither branch establishes a successful alternative quote or shipment.

The Agent's observable work is source retrieval, cited findings, correction requests and prepared topics. No hidden chain-of-thought is presented. Live mode displays actual persisted events; replay displays historical events. A failed live review never silently falls back to a successful archive.

## SAP boundary and potential benefit

Proposed S/4HANA procurement context: baseline purchase-order/item, quantity/unit, requested date and relevant procurement status. Proposed return: an approved, version-linked disposition/change request routed into the existing procurement approval process. Exact API/version mapping, tenant authorization and write semantics are not verified. Current records/interfaces are simulated; there is no SAP read or submission.

Potential SAP value is broader supplier participation around existing retail customers and a more useful procurement workflow. Potential partner value is implementation/support revenue. Neither new SAP license sales nor willingness to pay is established. A lightweight supplier entry may reduce adoption burden, but this demo does not prove suppliers will accept it.

## MVP boundaries

One case, two roles, synthetic inbox/docs, bounded Agent tools, rules, disclosure, investigation/closure and audit history. Excluded: production messaging, inventory optimization, autonomous buying, payment, carrier booking, customer profiling, multi-tenant security and a broader Agent platform.

## Production gaps

Authentication/tenant isolation, trusted record permissions, real integrations, idempotent writes, approval identities, durable shared database, monitoring/recovery, model-output security testing and privacy controls are still required. Public static role views do not provide confidentiality. The local server binds to loopback and must not be internet-exposed as a production service.
