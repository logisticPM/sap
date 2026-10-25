# Demand Pulse

**From a demand signal to a procurement decision.** One shared task per demand signal: an Agent checks the evidence, the planner decides, and procurement receives a recorded decision. The J Collective, SAP Product+ Summit semi-final.

## For the judges: start here

**Latest presentation: v71, 25 October 2026.** [Open the release and download all files](https://github.com/logisticPM/sap/releases/tag/presentation-v71).

1. **[Download the complete English ZIP](https://github.com/logisticPM/sap/releases/download/presentation-v71/Demand_Pulse_Presentation_v71_EN.zip)**: PowerPoint, standalone narrated video, English script and playback instructions.
2. **[PowerPoint with embedded video](https://github.com/logisticPM/sap/releases/download/presentation-v71/Demand_Pulse_Product_Story_v71_EN.pptx)**: slide 6 includes the three-minute recording with Jeremy English narration. Enable computer audio.
3. **[Watch or download the narrated video](https://github.com/logisticPM/sap/releases/download/presentation-v71/Demand_Pulse_Actual_Workflow_v71_EN_Voiced.mp4)**: new supplier reply, actual Agent review, revised information, authorized disclosure, planner decision and independent retailer approval with a persistent sandbox receipt.
4. **[English narration and timing](presentations/NARRATION_v71_EN.txt)** and **[recording boundaries](docs/PRESENTATION_V71.md)**.
5. **[Try the public replay](https://logisticpm.github.io/sap/)**: no login or key. This is an earlier interactive historical replay with no model calls. Publishing v71 presentation materials does not upgrade that replay or redeploy the live Agent.
6. **The code**: [procurement sandbox](procurement_sandbox/README.md), [local Agent workbench](docs/RUN_LOCAL.md), and [public replay](web/). The cloud workspace is hosted separately.

The video records real model executions on synthetic business materials. The opening demand context is retained from an earlier review; the supplier task then runs two new reviews and the authorization/approval flow. Business roles are simulated, SAP is not connected, and edited video timing does not establish time savings or business returns. The public ZIP contains no team testing code or model credentials.

Earlier files and notes below remain for provenance. For the current presentation, use the v71 release rather than the older repository deck.

---

## Historical team handoff notes (retained)

_Last synchronised: 25 October 2026, against deliverable v50 (deployed) and v51 (in progress)._

## Historical snapshot — v50 deployed, v51 under construction

**Deployed now (v50, Site version 37).** One English task flow on the same synthetic CASE-1042 (OJ-250 orange juice, Toronto DC, original plan 360 cases retained): request → supplier disclosure → decision update → retailer procurement review.

- Planner view: <https://demand-pulse-team-agent.keen-cod-0621.chatgpt.site/task?id=1c08677ed719499d8459ee432039c9db&role=planner>
- Supplier view: <https://demand-pulse-team-agent.keen-cod-0621.chatgpt.site/task?id=1c08677ed719499d8459ee432039c9db&role=supplier>
- Original workspace (retained real-Agent records): <https://demand-pulse-team-agent.keen-cod-0621.chatgpt.site/blind?id=1c08677ed719499d8459ee432039c9db&role=planner>

Teammates use the testing code from the English ZIP. The task view uses read-only state polling and makes **no model calls**. The planner can prepare a simulated procurement review packet; it lives in the browser only, `purchase_authorized=false`, `booking_authorized=false`, `SAP connected=false`, and nothing is submitted. Real Agent controls remain reachable in the original workspace.

**What v47–v50 added since the v34 update**

| Version | What it established | What it did not establish |
|---|---|---|
| v47 synthetic business pack | Three mutually exclusive branches A/B/C with request logs, inventory, reconciliation, conditional quote and itemised costs; deterministic evaluator | Any real Loblaw, Mucci or SAP record; forecast accuracy |
| v48 real-model tests | Claude Sonnet 4.6 reviewed each branch blind to the evaluator. A: conditional 140-case proposal. B: zero additional cases. C: **failed** semantic review (unsupported 80-case / CAD 770 prose) and was quarantined | A measured success rate; robustness on unseen real documents |
| v49 evidence-correction loop | Typed timing claims, quantity-consistency checks, same handler in production and tests, planner-triggered linked correction with a four-call cap. A and C corrected with 5 new real calls, originals preserved | A complete semantic verifier; general model reliability |
| v50 task workspace | Pinned trigger / blocker / original plan; decision card comparing three assessments; procurement-review handoff boundary; 6 offline tests and a browser walkthrough on the deployed site | Any order, requisition, SAP write, labour saving or realised profit |

**In progress (v51, not yet validated).** An interactive supplier-reply flow is being wired to the real review service: edit the supplier reply → save (no charge) → ask the Agent to check (model call) → preview and authorise sharing → planner receives only the authorised version. Editing again invalidates the previous check; the planner keeps seeing the last shared version until a new one is authorised. Historical replay is labelled separately. **Do not cite v51 until its VALIDATION record exists in `deliverable/competition_v51/`.**

**Budget (observed after v49, unchanged through v50).** Cloud ledger USD 3.0319 of a 4.00 cap; total project authorisation USD 20. Item A has used 18 of 19 calls, item C 10 of 12. The earlier "$3 envelope within $10" wording below is historical.

## Version history in this repository

| Date | Version | Milestone |
|---|---|---|
| 24 Oct | v31 | Local workbench with real Claude Sonnet 4.6 calls; 24 portable tests; public GitHub Pages replay |
| 24 Oct | v32 | Live cloud Agent on chatgpt.site with shared budget envelope |
| 24 Oct | v33 | Task-oriented workbench: inquiry is the primary object, not the Agent run ([notes](docs/WORKBENCH_V33.md)) |
| 24 Oct | v34 | Competition PRD v34 and frozen minimal-validation protocol |
| 25 Oct | v36 | Separate free-form inference experiment: 0/6 on frozen packets, then 2/2 by coded labels with a semantic defect found by hand; **not released** |
| 25 Oct | v41 | Demand evidence contract: six retailer records plus up to four appended materials, continue / clarify / pause gate before investigation ([PRD v41](docs/COMPETITION_PRD_v41.md)) |
| 25 Oct | v47–v50 | Synthetic pack, real-model A/B/C tests, correction loop, task workspace (table above) |
| 25 Oct | v51 | Interactive supplier reply flow — in progress |

Earlier PRDs, deployed versions and session records are retained in the full project folder, not in this repository.

## Earlier project references (retained)

1. [Try the public demo](https://logisticpm.github.io/sap/) — no login, no key, no model charges. Historical replay on synthetic business records (v31 records).
2. [Open the live v50 task workspace](https://demand-pulse-team-agent.keen-cod-0621.chatgpt.site/task?id=1c08677ed719499d8459ee432039c9db&role=planner) — testing code required; no model calls from the task view.
3. [Stakeholder brief](docs/STAKEHOLDER_BRIEF.md) — the hardest question from software development, marketing, finance and product strategy, with our answer and evidence links for each.
4. [Product thesis and sandbox plan](docs/PRODUCT_THESIS_AND_SANDBOX_PLAN.md) — the one claim we are prepared to lose, how we lose it, and the minimal work to connect a real supplier email in and a persistent procurement-sandbox object out. Engineering acceptance and business validation are reported apart. **Proposed, not built.**
5. [Procurement sandbox](procurement_sandbox/README.md) — S/4HANA-shaped mock of the purchase-order, stock and purchase-requisition services (CSRF, roles, ETags, idempotency, staleness, fault injection, audit) with a reference client and a ten-task engineering-acceptance kit. **Not SAP connected**, and it says so on every response.
6. [Competition PRD v41](docs/COMPETITION_PRD_v41.md) — current product definition. [PRD v34](docs/COMPETITION_PRD_v34.md) is retained for comparison.
7. [Progress and implementation status](docs/PROGRESS.md).
8. [Validation results, preserved failures and next experiment](docs/VALIDATION.md).
9. [Research report, including negative findings](docs/RESEARCH_REPORT.md).
10. [Product design and responsibility boundaries](docs/PRODUCT_DESIGN.md).
11. [Run the real Agent locally](docs/RUN_LOCAL.md), using your own key and an explicit separate budget.
12. [Business case deck](presentations/SAP_Demand_Pulse_Business_Case_Deck.pptx) — 11 slides, one message each, no appendix: today's workflow, the evidence (each number labelled real data, external study or our simulation, with its source), the product in one line and three moves, how it works, the **embedded three-minute video** (two retained real-model tests replayed: the demand gate's pause → continue, then a supplier reply read as a revision through to a persistent sandbox receipt; not one connected run), what is proven and not, where it plugs into SAP and what that costs, stakeholder trade-offs and gates, the twelve-day plan, and a recommendation with a now / next / later vision. Revised against last round's judge feedback; the mapping is in the run sheet. [Eight-minute run sheet](presentations/RUN_SHEET_8MIN.md). [Story definitions](docs/STORY_DEFINITIONS.md): the five statements deck, video and demo all follow. Generator in `presentations/build/`; it embeds the video from `deliverable/competition_v62_video/`, which is outside this repository.
13. [Five-minute English PPT](presentations/Team_Update_EN.pptx) — **built from v31 screenshots; it predates v33–v50 and has not been regenerated.**

## Five-minute walkthroughs

**Public replay (no model calls).** Start a historical replay → supplier reviews the request → inspect **Materials read** and cited findings → reveal the simulated logistics/QA replies → compare the changed conditions → authorise sharing → planner sees the released update → choose **Investigate an alternative** or **Stop additional supply**. Start another session to try the other branch. Open supplier/planner links in two tabs of the same browser to observe synchronisation.

**Live v50 task (testing code, no new model calls from this view).** Open the planner link → read the pinned trigger, current blocker and original plan → open the decision card comparing the initial quantity-unknown assessment, the authorised quote and the latest validated recommendation → expand evidence details to see previous attempts, failure records and call traces → prepare, inspect and reset a simulated procurement review packet → open the supplier link in a second tab and confirm it shows the disclosed quote only, never the retailer's review.

In both flows the carrier declines; missing QA evidence remains **Not confirmed**, not a failed QA inspection. Investigation authorises fact gathering only. It does not create an order, book transport, spend money or establish additional demand.

## What this package proves — and does not prove

- v31 and v48–v49 used real Claude Sonnet 4.6 calls with persisted tool events. The public website reuses three selected v31 records; the v50 task view reuses retained v48–v49 records. Neither reruns the model.
- Real-model failures are kept, not erased: v48 item C's unsupported numerical prose, v49's rejected first attempts, v36's semantic defects. Corrections are linked new records.
- Rules enforce exact quotation, source access, condition coverage, unknown quantities, retained baseline, disclosure boundaries and budget. They do **not** prove the prose is true; a second model audit is a fallible review, not verification.
- SAP procurement records, supplier records, department replies and workflow roles are simulated. No SAP tenant, supplier mailbox, carrier or DC scheduling system is connected.
- Demo roles are views in a shared test session, not production identities or access control. Never add real business data to this public repository.
- No measured labour savings, demand accuracy, revenue uplift, service improvement, supplier adoption or real financial return has been established. The three-arm comparison in [VALIDATION.md](docs/VALIDATION.md) has a protocol but no participants yet.

Sessions on the public website live in your browser, not on a shared server. The cloud task workspace stores records server-side under the testing code, but the procurement packet in v50 is browser-local. The local backend is a demo, not a production deployment.

---

**Original handoff description: v31 / 24 October 2026 (retained).** An English replenishment workbench connecting a retail planner and supplier around one additional-supply inquiry. The Agent reads fragmented evidence, prepares unresolved follow-ups and revises its assessment after new replies. Rules and human authorisation constrain what happens next. The v32 live cloud Agent reserved a shared $3 envelope within an original $10 project budget; both figures were later raised (see Budget above) and were never reset. Original project versions and full private runtime history remain preserved outside this repository, which contains a selected, portable handoff, not the full research data lake.
