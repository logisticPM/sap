# Eight-minute run sheet: 13 slides (5:45) + live demo (2:00) + 15 s buffer

Deck: `SAP_Demand_Pulse_Business_Case_Deck.pptx`, one continuous flow, no appendix. The same time budgets are in each slide's speaker notes. The order follows the judging weights: problem definition (20%), product solution (20%), prototype (20%), stakeholder alignment (20%), implementation plan (10%), delivery (10%).

| Clock | Slide | Rubric | Say, in one breath |
|---|---|---|---|
| 0:00–0:15 | 1 Title | Delivery | "Everything here is synthetic, the procurement target is a sandbox, and we will tell you what we have not proven before you ask." |
| 0:15–0:50 | 2 The exception | Problem | Name the triggers on the chips: promotion, stockout, short shipment, carrier or QA disruption, lot change, date move. Walk the five generic steps. "CASE-1042 is the instance we built against; the loop is the same for any trigger." |
| 0:50–1:25 | 3 Who has this problem | Problem | The user and today's workflow, then the evidence table: two regulator studies, two retailer documents, a real SAP purchasing log with a 9.3-day median, and our own failed forecasting experiments. "Still missing: planner interviews." |
| 1:25–1:50 | 4 The promise | Solution | Read the promise once. Three dispositions; five seconds on WAIT. Then the two boundaries: "the demand evidence gate judges whether the evidence supports pursuing supply, continue, clarify or pause; it never estimates unrecorded demand." |
| 1:50–2:20 | 5 Why this, not the alternatives | Solution | Read by rows. Dwell on the form column: "a strong form with our rules may be enough; the pilot includes it as an arm." Retailer pays, supplier keeps email. |
| 2:20–2:45 | 6 How it works | Prototype | Point at the colours: dark reads, teal decides, amber authorises. Point at the dashed box: "a model judgment that rules enforce; only a current continue opens investigation." |
| 2:45–3:00 | 7 Demo in six frames | Prototype | "This is what you will see; frame six is the sandbox's answer." |
| 3:00–5:00 | Live demo | Prototype | Email in → match → review with citations → a rule catches an error → supplier authorises → planner submits → sandbox returns a requisition number → approver releases. Narrate the authority at each step, not the UI. |
| 5:00–5:15 | 8 Proven and not proven | Prototype | Point only: four evidence labels, each with what it cannot establish; the table says what each artefact does not prove. Do not read it. |
| 5:15–5:45 | 9 Where the model was wrong | Alignment | Three retained failures; what caught each; the rule that now exists. "Structure passes, prose fails; our answer is a rule, a kept record, a linked correction." |
| 5:45–6:10 | 10 Finance | Solution | "Under one dollar per exception, measured. Minutes saved and integration cost are not measured; the pilot measures them. Simulated profit gains were withdrawn." |
| 6:10–6:50 | 11 Four stakeholders | Alignment | One row per function: need, chose, gave up. Then the conflict and the gates. End on the limitations we own. |
| 6:50–7:25 | 12 Implementation plan | Plan | Milestones, resources, success criteria, stop rules. "Twelve days produce an engineering report, never a business number." |
| 7:25–7:45 | 13 Asks | Delivery | Four asks, one per function, then the thirty-second close. |
| 7:45–8:00 | buffer | | |

## If the demo runs long

Cut in this order: slide 8 entirely (say "four evidence labels" over slide 9 instead), then slide 6 (say "dark reads, teal decides, amber authorises" over slide 7), then the bottom box of slide 5.

## If the demo fails

Stay on slide 7 and walk the six frames at the same pace; the frames are real captures of the deployed workbench. Do not apologise twice.

## Thirty-second close

"We proved the loop runs, stays inside its authority, and catches and repairs its own errors. We have not proved it is worth buying. The pilot answers that, and we have already written down what losing looks like."

## Three things never said

"Hidden demand recovery." Any saving percentage as a result. "Connected to SAP."

## Questions: where the full answer lives

| Question is about | Slide to return to | Fuller material |
|---|---|---|
| Architecture, provider, production gaps | 6, 9 | `docs/STAKEHOLDER_BRIEF.md` §1; `procurement_sandbox/CONTRACT.md` |
| Incumbents, buyer, pricing | 5, 11 | `docs/STAKEHOLDER_BRIEF.md` §2 |
| Unit economics | 10 | `docs/STAKEHOLDER_BRIEF.md` §3 |
| Roadmap gates, why one case | 12 | `docs/PRODUCT_THESIS_AND_SANDBOX_PLAN.md` |
| Stop rules in full | 12 | `docs/PRODUCT_THESIS_AND_SANDBOX_PLAN.md` §1 |
| How you will measure, the ten tasks, three arms | 12 | `procurement_sandbox/acceptance/README.md`; `docs/VALIDATION.md` |
| A number being challenged | 10 | `docs/STAKEHOLDER_BRIEF.md`, "Numbers to have ready" |
