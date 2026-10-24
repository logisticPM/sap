# Demand Pulse — team handoff

**Current build: v31 / 24 October 2026.** An English replenishment workbench connecting a retail planner and supplier around one additional-supply inquiry. The Agent reads fragmented evidence, prepares unresolved follow-ups and revises its assessment after new replies. Rules and human authorization constrain what happens next.

## Start here

1. [Try the public demo](https://logisticpm.github.io/sap/) — no login, no key, no model charges. Historical replay on synthetic business records.
2. [Download the five-minute English PPT](presentations/Team_Update_EN.pptx).
3. [Progress and implementation status](docs/PROGRESS.md).
4. [Research report, including negative findings](docs/RESEARCH_REPORT.md).
5. [Product design and responsibility boundaries](docs/PRODUCT_DESIGN.md).
6. [Run the real Agent locally](docs/RUN_LOCAL.md), using your own key and explicit separate budget.
7. [Validation results and next experiment](docs/VALIDATION.md).

## Five-minute walkthrough

Start a historical replay → supplier reviews the request → inspect **Materials read** and cited findings → reveal the simulated logistics/QA replies → compare the changed conditions → authorize sharing → planner sees the released update → choose **Investigate an alternative** or **Stop additional supply**. Start another session to try the other branch. Open supplier/planner links in two tabs of the same browser to observe synchronization.

The carrier declines; missing QA evidence remains **Not confirmed**, not a failed QA inspection. Investigation authorizes fact gathering only. It does not create an order, book transport, spend money or establish additional demand.

## What this package proves — and does not prove

- The original v31 used real Claude Sonnet 4.6 calls and persisted tool events. This website reuses three selected completed records; it does not rerun the model.
- A separate local backend can make new calls. It never uses the original developer's key or budget ledger.
- SAP procurement records, supplier records, department replies and workflow roles are simulated. No SAP tenant, supplier mailbox or carrier is connected.
- Public fixtures include synthetic supplier-private information for demonstration. UI role filtering is **not** production authentication or confidentiality. Never add real business data to this public repository.
- No measured labor savings, revenue uplift, service improvement or real-world supplier adoption has been established.

Sessions on the website live in your browser, not on a shared server. They synchronize across tabs on the same origin/browser; sharing a session URL with another person does not share its state. The local backend is also a demo, not a production deployment.

Original project versions and full private runtime history remain preserved outside this repository. The repository contains a selected, portable handoff, not the full research data lake.
