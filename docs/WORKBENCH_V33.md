# Task workbench update — v33

The primary object is a replenishment inquiry, not an Agent run. This update preserves CASE-1042, its synthetic records, original purchase baseline, live model backend, disclosure boundary and budget ledger.

## Walkthrough

1. Open the work queue. In Live Agent mode enter the team testing code and open the incoming inquiry. This creates a separate retained session and starts a real evidence review. Historical Replay instead reuses archived records without model calls.
2. Read the communication timeline, current blocker and next owner. The Agent reads available material and prepares follow-up topics. Rules assign owners and validate condition states. External messages are not sent.
3. Expand Demo controls to deliver the explicitly simulated department replies. In live mode this starts another actual review. Carrier acceptance changes from not confirmed to not satisfied after the decline; QA remains unconfirmed.
4. The supplier authorizes disclosure of the final operational response. The planner cannot access private drafts or source records through the planner view.
5. The planner requests an alternative investigation or closes the inquiry while retaining the original plan. Investigation does not authorize booking, payment or a purchase-order change. Live investigation results require another supplier disclosure.
6. Closed records remain available. Start a separate test inquiry rather than erasing earlier work.

## Verification and limitations

The local replay passed both branches and privacy/retention contract checks. Sixteen cloud evidence, authority and budget-envelope assertions passed, and the cloud build succeeded. Browser checks verified the replay alternative-and-close route and the supplier disclosure boundary. Live-browser validation is recorded in the accompanying v33 validation note.

This is a task-oriented prototype, not a production operating system. SAP, email, QA, logistics and DC scheduling are not connected. The queue contains one synthetic incoming case. Demonstration roles in one browser are not production authentication. No new demand quantity, confirmed transport option, labor saving or fulfillment benefit is established. Historical v31 PPT screenshots and v32 cloud validation remain explicitly historical.

The existing shared cloud allocation remains $3 within the original $10 project authorization. It has not been reset. Keep the browser open during execution. Stop when budget or evidence checks prevent progress; do not substitute replay for a failed live run.
