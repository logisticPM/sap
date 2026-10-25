# Eight-minute run sheet: 13 spoken slides (4:50) + embedded video (3:00) + 10 s buffer

Deck: `SAP_Demand_Pulse_Business_Case_Deck.pptx`, one flow, no appendix. The spine is one sentence: **a demand signal becomes a procurement decision, evidence-checked and human-approved.** Slide 7 is the three-minute walkthrough video embedded in the file (H.264 / AAC, plays in PowerPoint with one click, full slide, own narration). It replays the completed v59 real-model run; nothing was re-run for filming. Slides carry the message; the detail is in each slide's speaker notes with the same time budget. Order follows the judging weights: problem (20%), solution (20%), prototype (20%), stakeholder alignment (20%), implementation plan (10%), delivery (10%).

| Clock | Slide | Rubric | Say |
|---|---|---|---|
| 0:00–0:10 | 1 Title | Delivery | Read the one-line label, then one sentence from the notes: synthetic facts, a sandbox that says "not SAP connected", costs measured and value a hypothesis the pilot tests. |
| 0:10–0:35 | 2 One demand signal, two people | Problem | The planner owns the shelf, the coordinator owns the truck. Walk the five steps; stop on the three red ones. "The information exists at every step; nothing carries it to a decision." |
| 0:35–0:55 | 3 Four numbers | Problem | 9.3 days and 12% from a real SAP log; 28 supplier interviews; our own −4.7%: "the forecasting route failed, so the handoff is the wedge." |
| 0:55–1:15 | 4 Judge, check, land | Solution | The three moves: the demand evidence gate, "continue, clarify or pause; it never estimates unrecorded demand"; the reply checked against the signal; the decision landing as CHANGE, KEEP or WAIT. |
| 1:15–1:35 | 5 Why this | Solution | Read by rows, colours do the work. "A strong form with our rules may be enough; the pilot includes it as an arm." |
| 1:35–1:55 | 6 One loop | Prototype | Signal, gate, reply by email, model reads, rules decide, humans authorise, receipt persisted. "The email comes through a simulated test intake; the receipt is a sandbox record, not SAP. The whole loop ran end to end once, with real model calls. You are about to watch that run." |
| 1:55–4:55 | 7 Video | Prototype | Say once: "This is a replay of a completed real-model run, not new inference." Click. Let it play; do not talk over the narration. Chapters: 0:00 new supplier reply · 0:28 what the Agent checked · 1:10 supplier authorises disclosure · 1:41 planner decides: retain 360, add 0 · 2:11 separate approval, persisted receipt · 2:41 what this demonstrates. Optional after the clip, if time allows: switch to the planner tab and refresh the receipt once. |
| 4:55–5:10 | 8 Proven / not | Prototype | The only slide with evidence labels. Point only: "one end-to-end run proves the loop runs; it does not prove a success rate or value." Do not read the table. |
| 5:10–5:35 | 9 Three failures | Alignment | Said, caught by, changed. "Structure passes, prose fails; our answer is a rule, a kept record, a linked correction." |
| 5:35–5:55 | 10 Finance | Solution | "Under one dollar per exception, measured; the end-to-end run cost five cents. Minutes saved and integration cost are not measured; the pilot measures them." |
| 5:55–6:30 | 11 Stakeholders and gates | Alignment | One row per function: need, chose, gave up. Then the four gates. "If a strong form matches the Agent, we ship the form." |
| 6:30–7:00 | 12 Twelve days | Plan | A real mailbox behind the same validator, ten frozen tasks run end to end, engineering report; then the three-arm pilot. "Twelve days produce an engineering report, never a business number." |
| 7:00–7:25 | 13 Vision | Delivery | "Vision is context, not scope." Now the pilot; next every plan change on a live SAP landscape; later the Retail Response Network. "SAP integrations are proposals, not agreements." |
| 7:25–7:50 | 14 Recommendation | Delivery | "Run a focused pilot before any commercialisation": finish the loop, measure it on real work, decide with the stop rules. Then the three sentences on the slide, slowly. |
| 7:50–8:00 | buffer | | |

## Playback checklist

Open the deck in PowerPoint on the presenting laptop beforehand, go to slide 7, press play once with sound on, and stop it; this confirms codec and audio output. Keep the laptop volume at the level you tested. The video is embedded (9 MB), so no separate file or network is needed. If the room's audio fails, narrate the six chapter titles over the picture; the on-screen captions carry the boundary statements.

## If the demo runs long

Cut slide 8 entirely, then slide 13 (say "this is the pilot; the network is the horizon" over slide 14), then slide 5. Never stop the video early: it carries the prototype score.

## If the video fails to play

Say "the recording is in the pack", show the planner tab live and walk the same six beats from the saved task without triggering a model call: request and saved reply v3 → checked response with citations → authorised v3 → planner decision, retain 360 → approval record → refresh the receipt. Do not apologise twice. Do not start a new Agent review: the task's call budget is nearly spent.

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
| What the video shows and does not | 7 | `deliverable/competition_v60_video/README.txt`, `VALIDATION.md`; `deliverable/competition_v59/VALIDATION.md` |
| The ten tasks, three arms, measurement | 12 | `procurement_sandbox/acceptance/README.md`; `docs/VALIDATION.md` |
| Vision, SAP touchpoints, what is agreed | 13 | `docs/STAKEHOLDER_BRIEF.md` §4; nothing with SAP is agreed |
| A number being challenged | 3, 10 | `docs/STAKEHOLDER_BRIEF.md`, "Numbers to have ready" |
