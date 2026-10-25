# Product thesis and sandbox integration plan

_Drafted 25 October 2026; revised the same day after team review. One thesis we are prepared to lose, and the smallest work that connects the existing evidence harness (v49–v51) to a real reply channel and a persistent procurement object. Nothing here is built yet._

**The correction this revision makes.** Connecting the sandbox proves the product can *complete the task*. Only a comparison on real tasks with real participants proves it is *worth buying*. Ten cases that run end to end in a sandbox must never be reported as a business-efficiency gain. The two kinds of evidence are produced and reported separately (section 6).

Until now we have mostly proven that the Agent does not overstep. We have not shown what it finishes for the user. That is what this plan changes. Two beliefs we drop along the way: that the product is only valuable if it sets the order quantity itself, and that the model must be irreplaceable. A customer can pay for exception handling that genuinely removes work and completes the handoff. A customer will not pay for one more screen a human has to maintain.

## 1. The thesis

**Product promise**

> When a supplier's new reply affects an existing replenishment arrangement, Demand Pulse turns that reply into either a change draft that can be submitted to the retailer's existing procurement approval, or a reasoned keep-the-plan / stop-following-up result. The planner does not re-key information that has already been provided. Every commercial commitment is still approved by someone with the authority to make it.

The end point is **the handoff to procurement approval**. It is not "the Agent made a suggestion", and it is not "the goods arrived".

**Thesis to be tested**

> On replenishment exceptions whose reply channel and procurement object are already connected, Demand Pulse reduces the median combined active handling time of planner and supplier by **at least 30 percent** against the current manual process, without increasing critical errors; and by **at least a further 15 percent** against a strong form-and-rules workflow, without shifting the retailer's saved work onto the supplier.

Both percentages are **pre-set product targets, not results**. They are confirmed with the pilot partner and frozen before the first test. Ten tasks can surface problems and tell us whether to continue; they cannot establish a stable commercial return.

**How we lose**

| Test result | Product decision |
|---|---|
| After connection, a human still re-keys or re-organises the same information | The loop is not closed; keep fixing the workflow before claiming anything |
| Active handling time misses the target | Do not claim an efficiency benefit |
| Strong form-and-rules performs as well as the Agent | Ship the form and rules; do not use AI for its own sake |
| Supplier workload rises enough to offset the retailer's gain | Redesign the division of work |
| Any critical error: overstepped authority, wrong case matched, duplicate submission | Suspend the automatic submission capability |
| Time is dominated by production and transport, not information handling | Do not promise improved arrival |

## 2. The same case, connected at both ends

Keep the current orange-juice case (CASE-1042, OJ-250, Toronto DC). Complete only this chain:

```
supplier email arrives → matched to the existing procurement item → original plan read
→ new reply checked → disposition formed → human approves → written to the procurement sandbox
→ object number and status returned → exception closed with the link
```

**A disposition has exactly three allowed outcomes.**

| Outcome | Meaning | What must exist |
|---|---|---|
| **Request a change** | Evidence is sufficient; a procurement change draft is generated | Original object, original and proposed values, reason, evidence, open unknowns |
| **Keep the plan / stop the add-on** | The reason is recorded and the exception is closed | Cited reason; original plan untouched |
| **Wait for specific information** | A to-do with an owner and a deadline; processing resumes when the reply lands | Owner, deadline, the exact question; a resumable state, never a permanent "hand the pile to a human" |

**Quantity boundary, stated plainly.** This minimum product does not forecast hidden demand. An additional quantity comes from a request the buyer has already provided and approved, or from an explicit calculation rule. The Agent's job is to decide whether the new reply keeps that request feasible and how it must be changed or stopped. Where no quantity basis exists, abundant supply is never used to infer demand.

## 3. Input end — minimal work

| Work | Minimal implementation | Accepted when | Owner | Size |
|---|---|---|---|---|
| Connect one real channel | A dedicated test mailbox (Cloudflare Email Routing → Worker → `/api/inbound`, or a vendor inbound webhook); the supplier replies from an ordinary mail client | The email enters the task automatically; nobody copies or pastes | Team (mailbox) + Codex | S |
| Match the business object | Match on PO number, line item, SKU and mail thread | On ambiguity the system asks for confirmation; it never matches silently | Codex | M |
| Read the original procurement data | One purchase order and its line items: quantity, unit, date, status, version | The screen shows the source and the read timestamp | Codex, after the sandbox probe below | S |
| Keep the raw material | Store body, timestamp, sender, attachments and the revision relationship | A citation leads back to the original text; a new reply never overwrites an older one | Codex | S |
| Trigger the check | A new reply starts a budget-bounded review | A duplicate email does not create a second task or a second review | Codex | S |

Test emails may carry synthetic business content, but the two layers are labelled apart: **mail receipt is a real connection; the business facts inside the mail are synthetic**. Limit the first version to the message body plus one structured attachment type. Do not attempt email, WhatsApp, portal, PDF and Excel at once.

## 4. Output end — minimal work

Pick one explicit write target first: a **procurement change request or approval draft**, not a vague "write back to SAP".

| Work | Minimal implementation | Accepted when | Owner | Size |
|---|---|---|---|---|
| ~~Probe the real sandbox~~ | Dropped by team decision on 25 October: no SAP key, no public-sandbox probe. The output end is the mock below | — | — | — |
| Define the change draft | Original procurement object, original and proposed values, reason, evidence, open unknowns; mapped field by field to purchase-requisition fields | An approver understands exactly what changes without opening the Agent trace | Claude — **done**, `procurement_sandbox/CONTRACT.md` §3 and §9 | S |
| Separate procurement approval | Retailer-side approval role, distinct from the supplier's disclosure authorisation | A supplier sharing a reply can never trigger a procurement submission | Codex | S |
| Submit to the sandbox | After approval, create a real, persisted draft or request object | A number, a status and a viewable record come back | Codex (app); mock service by Claude — **done**, `procurement_sandbox/` | M |
| Prevent duplicates and staleness | Idempotent submission; before submitting, check whether the procurement object has changed since the review | A retry creates no second object; an old proposal cannot overwrite a newer plan | Codex | S |
| Receipts and failure handling | Show success, rejection, failure and re-approval-needed as distinct states | "Request sent" is never displayed as "change completed" | Codex | S |
| Close the exception | Store the final disposition and the object link on the case | The planner keeps no separate tracking sheet | Codex | S |

**Decision taken 25 October: no SAP tenant or public-sandbox probe; the output end is a mock, made as SAP-shaped as possible.** The standalone, persistent procurement mock service now exists in this repository under [`procurement_sandbox/`](../procurement_sandbox/README.md) (S/4HANA-shaped OData v2 services for purchase order read, stock read and purchase requisition read/write; SQLite; CSRF; roles; ETags; idempotency key; duplicate guard; staleness check; fault injection; audit; 21 contract tests). Its contract and the change-draft field mapping are in `procurement_sandbox/CONTRACT.md`; a reference client with the response-to-state mapping is in `procurement_sandbox/client.py`. It proves the application-layer loop. Every response and every screen labels it **"Procurement sandbox — not SAP connected"**.

Before anyone uses the SAP name to claim connectivity, we still need a test tenant, a technical contact, and a check of exactly which read and draft/approval interfaces that release supports. The mock never substitutes for that verification. Public material already suggests the free sandbox is effectively read-only and that released purchase-order APIs handle only active documents (sources in section 8); the probe gives the real answer.

## 5. Core changes needed to measure anything

| Work | Accepted when | Owner | Size |
|---|---|---|---|
| Case identity keyed by procurement object and mail thread, not by browser session | Two browsers on the same case see the same ledger | Codex | S |
| Server timestamps at every transition: received, review started, review accepted, disclosure authorised, change submitted, change approved, closed | One row per exception with all timestamps; elapsed time is computed, never typed | Codex | S |
| Active-time capture: per-screen focus timer plus one self-report field at each authorisation | Each human action records seconds of focus, summed per role | Codex | S |
| Waiting time recorded with its reason (supplier, production, transport, approval) | Waiting is reported separately from handling and never counted as labour | Codex | S |

## 6. Testing — engineering acceptance first, business validation second, reported apart

**Engineering acceptance: ten frozen tasks.** They cover: an ambiguous reply; an explicit revision; a partial fulfilment; a different quantity unit; a reply matched to the wrong order; a duplicate email; a stale proposal against an updated plan; a rejection; insufficient evidence; a submission failure. The question is whether the chain runs from email to procurement receipt. Every unconnected or synthetic component is listed item by item in the report.

**Status 25 October:** the ten tasks, their answer keys, the `case_export.json` contract the application must emit, the freeze (`freeze.json`, hashed) and the scorer exist in [`procurement_sandbox/acceptance/`](../procurement_sandbox/acceptance/README.md). Because the build is being accelerated without a team, **the tasks were authored by Claude on the development side and are flagged as not independent**. An outside author should rewrite the email bodies and answer keys, and re-freeze, before any acceptance result is cited.

**Business validation: only once real tasks and participants exist.** Three arms on the same materials with the same information rights: current process, strong form-and-rules, Agent-assisted. Counterbalanced so that no one handles the same case twice and gains a memory advantage. Record:

- active minutes for planner and for supplier, separately;
- waiting time and its reason, separately;
- critical errors, rework count, omissions;
- share of cases that reach the procurement-approval handoff;
- cost of model calls, human verification, integration and maintenance.

**Without real participants we report engineering completion and error counts only. We generate no time-saving conclusion.**

## 7. Sequence and effort

**Days 1–3, in parallel.** Sandbox probe; mailbox and inbound endpoint; change-draft schema; mock procurement service; transition timestamps. The probe decides whether submission targets the mock or the sandbox.

**Days 4–7.** Object matching, raw-material storage, duplicate guard, procurement approval role, submission, staleness check, receipts, case closure, active-time capture. Ship as one version with its own validation record, then freeze.

**Days 8–12.** Freeze the ten tasks, run engineering acceptance, write the report. Business validation starts only when a partner provides real tasks.

Roughly nine to twelve engineering days across the two owners.

**Solo mode (decided 25 October): the build proceeds without waiting for the team.** Each item that needed the team has a substitute, and each substitute is declared in the acceptance report:

| Needed from the team | Substitute while solo | What it costs in evidence |
|---|---|---|
| Mailbox domain | Development runs use an inbound simulator that POSTs the task emails to `/api/inbound` in the same shape the mail webhook will use; declared as `synthetic_components: ["mail receipt simulated"]`. For real receipt, a Cloudflare Email Routing domain can be bought by one person in an afternoon | Until a real mailbox exists, "mail receipt is a real connection" is not yet true |
| SAP sandbox key | Dropped; output end is the mock, labelled on every response | No SAP write semantics tested |
| Sandbox reachable from the cloud app | `cloudflared tunnel --url http://127.0.0.1:8081` (no account; URL changes per start) for development; a small host or an in-deployment port for a stable demo | None, if the URL is refreshed per session |
| Independent author for the ten tasks | Claude authored them; flagged as not independent in `tasks.json` and in every report | Results are a development check, not a blinded test |
| Someone to play the supplier | The developer sends the task emails, or the simulator does | Same as above |
| Two or three conversations with practitioners | Deferred; the three end states remain our hypothesis | The thesis may be measuring a loop nobody runs; this is the first thing to fix when a person is available |

**Explicitly out of scope:** a production SAP tenant, carrier booking, payment, multi-tenant authentication, demand forecasting, multi-channel intake, more than one retailer or SKU, a general agent platform.

## 8. Sources consulted for the sandbox question

- SAP Knowledge Base 3756528: released Purchase Order APIs process only active documents; no released API supports draft purchase orders in the Public Edition — <https://userapps.support.sap.com/sap/support/knowledge/en/3756528>
- SAP Community thread showing the sandbox base path and API-key requirement for `API_PURCHASEORDER_PROCESS_SRV` — <https://groups.community.sap.com/t5/sap-btp-learning/developing-with-sap-integration-suite/m-p/1679>
- SAP Learning: Try Out on the Business Accelerator Hub sends several HTTP methods against sandbox test data — <https://learning.sap.com/courses/accessing-sourcing-and-procurement-data/working-with-apis-in-sourcing-and-procurement_fbe601e4-22d1-49a4-9784-d8b6c6825658>
- SAP Community blog on POST calls to `API_PURCHASEREQ_PROCESS_SRV` (generic host, not the sandbox) — <https://blogs.sap.com/2020/06/16/purchase-requisition-odata-api-episode-4/>
- Inbound email options (vendor-written comparisons; verify limits on each pricing page) — <https://www.sequenzy.com/blog/best-free-inbound-email-apis>, <https://webhookrelay.com/email-to-webhook/>

---

The next most valuable thing to build is not another Agent. It is to let one ordinary email reply actually enter the system, and to let one approved result actually create a traceable object in the procurement sandbox. Then, for the first time, the product can answer: what task did the user hand us, and how far did we take it.
