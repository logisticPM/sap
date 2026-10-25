# Story definitions: the five statements every deck, video and demo follows

_Agreed 25 October 2026. The business-case deck (`presentations/`), the walkthrough video (`deliverable/competition_v62_video/`, outside this repository) and any live demo use these definitions. If a slide, a narration line or a UI label contradicts one of them, the slide, line or label is wrong, not the definition._

## The five definitions

1. **The task starts with a demand signal, and a gate judges it.** The demand evidence gate returns one of `continue`, `clarify` or `pause`. It judges whether the recorded demand evidence supports pursuing additional supply. It never estimates unrecorded demand and never produces a quantity.
2. **Only a current `continue` opens the supplier investigation.** A `continue` is a recommendation; a human planner authorises the investigation separately, and that authorisation is not permission to purchase. New demand evidence invalidates an earlier verdict; the planner re-authorises.
3. **Supplier replies are read as revisions, not as the latest message.** A later reply can withdraw an earlier refusal; the Agent cites both. A record that was not supplied is "unknown", never "does not exist" and never "failed".
4. **A human makes the decision, and it lands as one of three: CHANGE, KEEP or WAIT.** Each disposition is recorded with its reason and the evidence it rested on, so it is traceable afterwards. Supply that is available is not demand that is established; KEEP is a business decision, not a failed order.
5. **Approval is triggered by policy, not by default.** Every disposition is recorded; whether it also needs an approver depends on the retailer's rules (quantity, value, exception type). In the retained test the KEEP disposition went through the demo's separate simulated approval and received a persistent receipt. That is one instance, not the rule.

## What this means for the three artefacts

| Artefact | Where the definitions show up |
|---|---|
| Deck | Slide 4 (the promise: gate → reply check → three dispositions, KEEP "routed for approval where policy requires"); slide 6 (the loop, with the footnote that gate and reply path were shown in two retained tests); slide 8 (what the two tests prove and do not prove); slide 12 (first milestone: one connected run on a single task) |
| Video (v62) | Chapter 1 is definition 1 and 2 on retained test A; chapters 2 and 3 are definition 3 on retained test B; chapter 4 is definition 4; chapter 5 states definition 5 in words |
| Live demo or Q&A | The presenter's one sentence before the video: "The prototype demonstrates these stages in two retained tests; one connected task-level validation remains to be done." |

## What is not yet demonstrated, in the same words everywhere

- One connected run of gate → supplier reply → disposition → receipt on a single task. Test A (inquiry `f1c3df49…`, v41) and test B (task `68b1d175…`, v59) are separate retained runs on the same synthetic case.
- A live mailbox: the email in test B arrived through a simulated test intake behind the same validator a real mailbox would use.
- Any SAP write: the receipt is a procurement-sandbox record and says so.
- A success rate, measured time saved, or any business value. Those are the pilot's questions.

## Sources of record

- Gate behaviour and the pause → continue sequence: `docs/COMPETITION_PRD_v41.md`; `deliverable/competition_v41_20261025/VALIDATION.txt` and traces (outside this repository).
- Reply handling, disclosure, disposition and receipt: `deliverable/competition_v59/VALIDATION.md` (outside this repository); `docs/VALIDATION.md`.
- The video's own boundary statement: `deliverable/competition_v62_video/README.txt`.
