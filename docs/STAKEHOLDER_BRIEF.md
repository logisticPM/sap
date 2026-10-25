# Stakeholder brief — Demand Pulse

_Prepared 25 October 2026 for the internal stakeholder panel (software development, marketing, finance, product strategy). Each section opens with the hardest question that function is likely to ask, gives the answer we can defend, and links the evidence. Paths are relative to this repository; records marked **[project folder]** live in the full project archive under `deliverable/competition_v<NN>/` and are not in this public repository._

**How to read the evidence labels**

| Label | Meaning |
|---|---|
| **Built** | Implemented, covered by automated tests and browser walkthroughs on the deployed site |
| **Real-model** | Actual Claude Sonnet 4.6 calls on synthetic business records, traces retained including failures |
| **Desk** | Public sources reviewed by the team; supports plausibility, not our effect size |
| **Hypothesis** | Stated assumption with no measurement yet; the pilot is designed to test it |

**The product in one paragraph.** Demand Pulse sits beside an SAP retailer's procurement workflow and handles one kind of exception: an additional-supply inquiry triggered by a demand concern. It reads the fragmented evidence on both sides (retailer records, supplier replies, departmental confirmations), produces cited interpretations, chases only the conditions that change the decision, lets the supplier authorise exactly what is disclosed, and gives the planner a bounded next action. The original SAP purchase plan is never changed by the Agent. Rules enforce what the model may do; humans hold every commercial authority.

---

## 1. Software development

**Sharpest question.** "An LLM in the loop of a procurement decision is a liability. How do you stop it inventing a quantity, leaking supplier data, or quietly rewriting its own mistakes, and what does it cost to run and to integrate with SAP?"

**Answer.** The model never has write authority. It runs inside an agent loop that the service owns: the backend calls Claude Sonnet 4.6 through OpenRouter, implements every tool itself (`read_sources`, `calculate_candidates`, `submit_assessment` and their manual and opportunity variants), and validates each submission in the same handler that production uses. A rejected submission returns `correction_required` with field-level findings; the code never edits the model's answer. A separate model audit runs after the rule checks, and only an accepted artifact can be disclosed. Supplier and planner see projections of the same record filtered by role; the planner never receives private drafts or raw supplier documents. Failed attempts stay on the task timeline as linked records.

What the rules enforce today: exact quotation of the source actually read; required condition coverage (carrier acceptance, vehicle capacity, receiving slot, QA release); unknown stays unknown, never a failed condition and never a quantity; retained baseline; typed timing claims tied to source fields; quantity consistency across summary, evidence and recommendation; disclosure boundaries; call caps and a budget stop.

What the rules do **not** do: prove the prose is true. We have two documented cases where structure passed and text failed (v36 N2, v48 item C). The second model audit is a fallible review that shares failure modes with the generator. We say this in the room before anyone else does.

**SAP boundary, honestly.** Read: baseline purchase order and item, quantity and unit, requested date, procurement status, stock and inbound. Return: a version-linked disposition or change request routed into the existing procurement approval process. Today these are frozen synthetic records; no S/4HANA API call, tenant authorisation or write semantics has been exercised. The v50 procurement review packet is browser-local with `purchase_authorized=false`, `booking_authorized=false`, `SAP connected=false`.

**Production gaps we would list ourselves:** authentication and tenant isolation, trusted record permissions, idempotent writes, approval identities, durable shared database, monitoring and recovery, model-output security testing, privacy controls.

**Evidence**

- Architecture and status ledger — [PROGRESS.md](PROGRESS.md) · **Built**
- Per-version checks, preserved failures — [VALIDATION.md](VALIDATION.md) · **Built / Real-model**
- Authority contract, state sequence, production gaps — [PRODUCT_DESIGN.md](PRODUCT_DESIGN.md)
- Portable backend you can run with your own key — [RUN_LOCAL.md](RUN_LOCAL.md), [`demo/engine.py`](../demo/engine.py), [`demo/test_workbench.py`](../demo/test_workbench.py) · **Built**
- 24 handoff tests, secret scan, public deployment — [HANDOFF_CHECKS.txt](HANDOFF_CHECKS.txt)
- Same handler in production and tests; 22 offline checks before paid correction, 24 after — `competition_v49/VALIDATION.txt` **[project folder]** · **Real-model**
- Structure-passed, prose-failed cases — `competition_v36_20261025/RESULTS.md`, `competition_v48/VALIDATION.txt` **[project folder]**
- Deployed v50 task workspace (team testing code; no model calls from this view) — [planner view](https://demand-pulse-team-agent.keen-cod-0621.chatgpt.site/task?id=1c08677ed719499d8459ee432039c9db&role=planner), [supplier view](https://demand-pulse-team-agent.keen-cod-0621.chatgpt.site/task?id=1c08677ed719499d8459ee432039c9db&role=supplier)

**Likely follow-ups**

- *Why not a deterministic form instead of a model?* We might end up there. The three-arm evaluation in [VALIDATION.md](VALIDATION.md) includes a strong form-and-rules arm; if it matches the Agent on correctness and burden, we recommend the form.
- *Why OpenRouter and Sonnet 4.6?* Cost and availability during the prototype. The service isolates the provider behind one function; swapping to a direct Anthropic or SAP AI Core endpoint is a configuration change, not a redesign.

---

## 2. Marketing

**Sharpest question.** "SAP already has Business Network supplier collaboration, Joule and the Business Network Assistant. SourceDay lets suppliers answer a PO from an email link. Microsoft's Procurement Agent reads supplier emails. What is left to sell, and to whom?"

**Answer.** We withdrew four differentiation claims after a documented competitive check: low-friction onboarding of non-ERP suppliers, split-shipment confirmation, fresh-produce shelf-life planning and downstream impact analysis are all covered or plausibly covered by incumbents. What we kept is one specific job for one specific buyer:

> For a replenishment planner at an existing SAP retailer, when a demand concern meets an ambiguous supplier reply, Demand Pulse gets the arrival and lot conditions that actually change the decision, applies the retailer's existing rules, and hands both sides a cited, authorisable proposal — so the exception closes with less manual reconciliation on both ends and nothing is committed that the evidence does not support.

Buyer: category or replenishment manager at an SAP retail customer. Economic owner: procurement operations. Second user: the supplier's customer-service or logistics coordinator, who gains a private draft and an explicit authorisation step instead of an email thread. Channel: an SAP partner extension on the customer's existing landscape, not a standalone network. We do not claim to be cheaper than incumbents; we claim lower total work at equal correctness, which is exactly what the pilot measures.

**What we have on the problem.** UK and Australian regulator studies document supplier frustration with forecast-versus-order mismatch and portal burden. Loblaw's PO-update guide and Mucci Farms' role descriptions show the multi-party coordination our task mirrors. These establish that the problem class exists; they do not establish that ambiguous supplier replies are the binding bottleneck. Direct user interviews are the single most important missing input and are the first pilot activity.

**Messaging rules for the room.** Lead with the planner's job and the closed loop, not with "AI". Show the rule-versus-model split as the safety story. Never say "hidden demand recovery": our own simulations showed the full detection-and-response policy can lose money at equal cost, so the product deliberately does not estimate latent demand.

**Evidence**

- Competitive check against SAP, SourceDay and Microsoft, with the four withdrawn claims — `competitive_review_20261022/COMPARISON.md` **[project folder]** · **Desk**
- Public workflow research and the three counter-hypotheses — `workflow_research_20261023/WORKFLOW_RESEARCH.md` and `SOURCES.md` **[project folder]** · **Desk**
- Problem-class sources: [GCA/YouGov 2025 supplier study](https://assets.publishing.service.gov.uk/media/68dd577ec487360cc70ca001/YouGov_slides_-_GCA_Annual_conference_2025.pdf), [ACCC supplier roundtables](https://www.accc.gov.au/system/files/supermarkets-inquiry-summary-roundtables.pdf), [Loblaw PO Updates guide](https://scvendorportal.loblaw.ca/LCLSCVendorPortal_POUpdatesUserGuide.pdf) — summarised in [RESEARCH_REPORT.md](RESEARCH_REPORT.md) · **Desk**
- Why we do not sell demand recovery — [RESEARCH_REPORT.md §2](RESEARCH_REPORT.md), [`evidence/E1_REPORT.txt`](../evidence/E1_REPORT.txt), [`evidence/REPLICATION_REPORT.txt`](../evidence/REPLICATION_REPORT.txt)
- Public demo for a two-minute walkthrough without a key — <https://logisticpm.github.io/sap/> · **Built**

**Likely follow-ups**

- *Who pays, retailer or supplier?* Retailer. The supplier gets a free, scoped entry point; charging suppliers is the failure mode the regulator studies describe.
- *Is this a feature or a product?* A feature-sized extension today. Whether it grows depends on the pilot, not on the pitch.

---

## 3. Finance

**Sharpest question.** "Show me the unit economics. What does one exception cost to run, what does it save, and what does it cost to implement? And why should I believe any of it when your own report says the simulated profit gains failed replication?"

**Answer.** Three numbers are measured, one is a hypothesis, and we will not blend them.

**Measured: model cost per exception.** From the v48 and v49 real-model runs on three synthetic items (34 initial calls, 5 correction calls, deduplicated by generation ID):

| Item | Initial review | Correction | Total model cost |
|---|---|---|---|
| A (conditional 140-case proposal) | 15 calls, USD 0.475 | 3 calls, USD 0.085 | USD 0.56 |
| B (zero additional cases) | 11 calls, USD 0.359 | none | USD 0.36 |
| C (blocked for insufficient evidence) | 8 calls, USD 0.277 | 2 calls, USD 0.063 | USD 0.34 |

Call it **under USD 1 per exception** including one correction round, on today's prototype prompts. Total real-model spend across the whole project: cloud ledger USD 3.03 of a 4.00 cap, project authorisation USD 20. Model cost is not the economic question.

**Measured: what the rules caught.** Of three real-model items, one produced an unsupported numerical recommendation in prose that passed structural checks and was caught only by a later rule audit. That is the kind of error a pilot must count, because a wrong additional order costs far more than any labour saved.

**Hypothesis: what it saves.** We have no participant timing. The break-even question is therefore: how many minutes of planner and supplier-coordinator time per exception must the workflow remove to cover model cost plus the amortised cost of verification, onboarding and integration? Illustrative only, with every input an assumption:

| Assumption | Value |
|---|---|
| Model cost per exception | USD 0.60 |
| Loaded planner cost | CAD 45 per hour (assumption) |
| Minutes of planner time that pay for the model cost alone | about 1 minute |
| Integration and onboarding (SAP read interface, identity, supplier enablement) | not quoted; this is the dominant cost and the first thing a pilot must price |

So the business case does not depend on model pricing. It depends on three things we have not measured: active minutes saved on both sides, critical errors avoided versus introduced, and the one-time integration cost on the customer's SAP landscape. The three-arm evaluation is designed to produce the first two; an SAP tenant owner is needed for the third.

**Why we withdrew the simulated profit claim.** On FreshRetailNet-50K the full policy recovered 46.6 percent of unmet demand at the same safety stock, but at equal expired stock the recovery was negative and the fresh-network replication failed its preregistered criterion. We therefore sell a coordination workflow with bounded authority, not a demand-recovery engine, and we do not carry those simulated gains into this business case.

**Evidence**

- Per-item call counts and spend — `competition_v48/VALIDATION.txt`, `competition_v48/usage_and_audit.json`, `competition_v49/VALIDATION.txt`, `competition_v49/live-results.json` **[project folder]** · **Real-model**
- Budget ledger and caps — [PROGRESS.md § Budget](PROGRESS.md) · **Real-model**
- Simulation results that constrain the claims — [RESEARCH_REPORT.md §2](RESEARCH_REPORT.md), [`evidence/ABLATION_REPORT.txt`](../evidence/ABLATION_REPORT.txt), [`evidence/REPLICATION_REPORT.txt`](../evidence/REPLICATION_REPORT.txt); full tables in `for_docs/key_numbers_simulation.md` **[project folder]**
- Procurement-process baseline from real enterprise data (BPI Challenge 2019: order-to-first-goods-receipt median 9.3 days, simulated saving 5–11 percent under stated assumptions) — `for_docs/key_numbers.md` **[project folder]** · **Desk / simulation**
- Evaluation protocol with stop rules — [VALIDATION.md § Next falsifiable comparison](VALIDATION.md)

**Likely follow-ups**

- *What is the pilot budget?* Model spend for 10–20 real exceptions across three arms is under USD 50 at current rates. The real budget line is participant time and an integration scoping engagement, which we ask the panel to size with us.
- *What kills it financially?* If forms and rules match the Agent on correctness and burden, or if production and transport dominate the exception timeline so that faster evidence work does not change arrival.

---

## 4. Product strategy

**Sharpest question.** "You started with a responsive supply network and ended with one exception type on one synthetic case. Is this a wedge or a retreat? What is the roadmap, and what would make you stop?"

**Answer.** It is a wedge chosen by elimination. We tested the broad idea and it failed on our own evidence: the full detection-and-response policy did not reliably improve profit, transfer gains were tiny, and treating available supply as proof of demand was wrong. What survived every test is narrower and more defensible: evidence preparation across fragmented documents and replies, with bounded follow-up, explicit correction and separated authority. That capability is useful even if the demand signal is noise, because the planner still has to close the exception.

**Why now, in SAP's ecosystem.** Incumbents cover collaboration, confirmation and planning as modules; the open question is whether an exception can be closed in one work item that pulls external, unstructured replies into existing rules. SAP's own custom-agent capability means this is more naturally an ecosystem extension than a standalone platform, and we position it that way.

**Gated roadmap.**

| Phase | What ships | Gate to proceed |
|---|---|---|
| 0 — now | v50 task workspace deployed; v51 interactive supplier reply in progress; real-model traces with preserved failures | v51 validation record exists; feature freeze |
| 1 — pilot evaluation | Three-arm comparison on 10–20 consecutive real exceptions with one partner: current process, strong form and rules, Agent-assisted | Critical errors do not worsen; total human burden falls enough to cover model, verification and onboarding cost. If forms match, ship the form |
| 2 — SAP read integration | Read baseline PO, stock, inbound and status from a real tenant; identity for planner and supplier roles | Tenant owner validates the boundary; no write yet |
| 3 — procurement write | Version-linked change request into the existing approval process | Approval owner accepts the disposition format; idempotent write path tested |

**Stop conditions, stated in advance.** Forms and rules perform as well; production or transport dominates the exception timeline; suppliers will not participate or disclosure effort exceeds planner savings; an incumbent closes the same loop in the same configuration at lower cost.

**What this demo proves and does not.** It proves constrained execution: real source reads, cited findings, rule-enforced boundaries, human authorisation, linked correction. It does not prove autonomous supply-chain understanding, demand accuracy, labour savings, supplier adoption or financial return. We would rather the panel hear that from us.

**Evidence**

- Current product definition and demand-evidence contract — [COMPETITION_PRD_v41.md](COMPETITION_PRD_v41.md)
- What changed since the early concept and why — [PROGRESS.md](PROGRESS.md)
- Negative findings that forced the narrowing — [RESEARCH_REPORT.md](RESEARCH_REPORT.md), [`evidence/`](../evidence/)
- Competitive positioning and the single surviving wedge — `competitive_review_20261022/COMPARISON.md` **[project folder]** · **Desk**
- Pilot protocol and stop rules — [VALIDATION.md](VALIDATION.md)
- Academic methods borrowed and their limits — [FreshRetailNet-50K](https://arxiv.org/html/2505.16319v1), [Conlon and Mortimer 2013](https://www.aeaweb.org/articles?id=10.1257/mic.5.4.1), [Cui et al. 2018](https://doi.org/10.1111/poms.12707), summarised in [COMPETITION_PRD_v41.md § Academic basis](COMPETITION_PRD_v41.md)

**Likely follow-ups**

- *Why one case?* Because every added case before a partner exists is more authored fiction. The v47 synthetic pack already has three branches; the next material should be real.
- *What is the ask?* One partner retailer or supplier willing to share 10–20 consecutive exception tasks with timestamps, and one SAP tenant owner to scope the read boundary.

---

## Numbers to have ready

| Figure | Value | Source |
|---|---|---|
| Real-model calls in v48 tests | 34 (A 15, B 11, C 8) | `competition_v48/VALIDATION.txt` **[project folder]** |
| Correction calls in v49 | 5 (A 3, C 2) | `competition_v49/VALIDATION.txt` **[project folder]** |
| Model cost per exception including one correction | under USD 1 | same |
| Cloud ledger / cap | USD 3.03 / 4.00 | [PROGRESS.md](PROGRESS.md) |
| Project authorisation | USD 20 | [PROGRESS.md](PROGRESS.md) |
| Offline tests, v49 / v50 | 24 / 6 passed | [VALIDATION.md](VALIDATION.md) |
| Real-model items that failed semantic review | 1 of 3 (item C), corrected and retained | [VALIDATION.md](VALIDATION.md) |
| Free-form inference on frozen novel packets (v36) | 0 of 6, then 2 of 2 by labels with a manual semantic defect | [VALIDATION.md](VALIDATION.md) |
| Simulated unmet-demand recovery, same safety stock vs equal waste (FRN) | +46.6 percent vs −4.7 percent | `for_docs/key_numbers_simulation.md` **[project folder]** |
| BPI 2019 order-to-first-GR median | 9.3 days; simulated saving 5–11 percent | `for_docs/key_numbers.md` **[project folder]** |
| Pilot size | 10–20 consecutive exceptions, three arms | [VALIDATION.md](VALIDATION.md) |
