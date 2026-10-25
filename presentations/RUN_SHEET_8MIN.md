# Eight-minute run sheet: 14 slides (5:55) + live demo (2:00) + 5 s buffer

Deck: `SAP_Demand_Pulse_Business_Case_Deck.pptx`, one flow, no appendix. The spine is one sentence: **a demand signal becomes a procurement decision, evidence-checked and human-approved.** Slides carry the message; the detail is in each slide's speaker notes with the same time budget. Order follows the judging weights: problem (20%), solution (20%), prototype (20%), stakeholder alignment (20%), implementation plan (10%), delivery (10%).

| Clock | Slide | Rubric | Say |
|---|---|---|---|
| 0:00–0:15 | 1 Title | Delivery | Read the one-line label, then the three boundary sentences from the notes: synthetic facts; a sandbox that says "not SAP connected"; costs measured, value a hypothesis the pilot tests. "We would rather you hear that from us." |
| 0:15–0:50 | 2 One demand signal, two people | Problem | The planner owns the shelf, the coordinator owns the truck. Walk the five steps; stop on the three red ones: worth pursuing is judged by gut, the reply is free-form, the decision has no handoff. "The information exists at every step; nothing carries it to a decision." |
| 0:50–1:25 | 3 Four numbers | Problem | 9.3 days and 12% from a real SAP log; 28 supplier interviews; our own −4.7%: "the forecasting route failed, so the handoff is the wedge." Say what is missing: planner interviews. |
| 1:25–1:50 | 4 Judge, check, land | Solution | Read the dark line once. Then the three moves in order: the demand evidence gate, "continue, clarify or pause; it judges whether the evidence supports pursuing supply and never estimates unrecorded demand"; the reply checked against the signal; the decision landing as CHANGE, KEEP or WAIT. Five seconds on WAIT. |
| 1:50–2:20 | 5 Why this | Solution | Read by rows, colours do the work. "A strong form with our rules may be enough; the pilot includes it as an arm." Retailer pays, supplier keeps email. |
| 2:20–2:45 | 6 One loop | Prototype | Signal arrives, the gate (dashed), then the reply path. Dark reads, teal decides, amber authorises. Say plainly: "the two Planned boxes, email intake and the procurement write, are built and tested separately and not yet wired into the app." |
| 2:45–3:00 | 7 Six frames | Prototype | "Frame one is the demand gate; five frames are live, one is planned; this is what you will see." |
| 3:00–5:00 | Live demo | Prototype | Planner workspace: the demand gate's cited continue, purchase on hold → supplier types the reply → Agent checks with citations → show one retained rule rejection → supplier authorises → planner sees the update and the decision card → procurement review packet, labelled not connected → switch to the terminal, run the sandbox client once: 201, requisition number, retry gives already submitted, approver release. Narrate the authority at each step, not the UI. |
| 5:00–5:15 | 8 Proven / not | Prototype | The only slide with evidence labels. Point only: four labels, each with what it cannot show. Do not read the table. |
| 5:15–5:45 | 9 Three failures | Alignment | Said, caught by, changed. "Structure passes, prose fails; our answer is a rule, a kept record, a linked correction." |
| 5:45–6:10 | 10 Finance | Solution | "Under one dollar per exception, measured. Minutes saved and integration cost are not; the pilot measures them. Simulated gains were withdrawn." |
| 6:10–6:45 | 11 Stakeholders and gates | Alignment | One row per function: need, chose, gave up. Then the four gates. "If a strong form matches the Agent, we ship the form." |
| 6:45–7:15 | 12 Twelve days | Plan | Milestones, resources, criteria, stop rules. "Twelve days produce an engineering report, never a business number." |
| 7:15–7:35 | 13 Vision | Delivery | "Vision is context, not scope." Now: the pilot. Next: every plan change on a live SAP landscape. Later: the Retail Response Network, where a supplier answers once and evidence flows with consent. "Each horizon opens only when the one before it passes its gate; the SAP integrations are proposals, not agreements." |
| 7:35–7:55 | 14 Recommendation | Delivery | "Run a focused pilot before any commercialisation": finish the loop, measure it on real work, decide with the stop rules. Then the three sentences on the slide, slowly. |
| 7:55–8:00 | buffer | | |

## If the demo runs long

Cut slide 8 entirely, then slide 13 (say "this is the pilot; the network is the horizon" over slide 14), then slide 6 (say "dark reads, teal decides, amber authorises" over slide 7).

## If the demo fails

Stay on slide 7 and walk the six frames at the same pace. Do not apologise twice.

## Three things never said

"Hidden demand recovery." Any saving percentage as a result. "Connected to SAP."

## Questions: where the full answer lives

| About | Slide | Fuller material |
|---|---|---|
| Architecture, provider, production gaps | 6, 9 | `docs/STAKEHOLDER_BRIEF.md` §1; `procurement_sandbox/CONTRACT.md` |
| The demand gate, what it does and does not estimate | 4, 6 | `docs/COMPETITION_PRD_v41.md` |
| Incumbents, buyer, pricing | 5, 11 | `docs/STAKEHOLDER_BRIEF.md` §2 |
| Unit economics | 10 | `docs/STAKEHOLDER_BRIEF.md` §3 |
| Gates, stop rules, why one case | 11, 12 | `docs/PRODUCT_THESIS_AND_SANDBOX_PLAN.md` |
| The ten tasks, three arms, measurement | 12 | `procurement_sandbox/acceptance/README.md`; `docs/VALIDATION.md` |
| Vision, SAP touchpoints, what is agreed | 13 | `docs/STAKEHOLDER_BRIEF.md` §4; nothing with SAP is agreed |
| A number being challenged | 3, 10 | `docs/STAKEHOLDER_BRIEF.md`, "Numbers to have ready" |
