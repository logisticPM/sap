# Presentation v71

[Download the release](https://github.com/logisticPM/sap/releases/tag/presentation-v71).

Use the release PowerPoint for the competition presentation. Slide 6 contains the three-minute actual-operation recording with Jeremy English narration. The release also provides a standalone MP4 and a complete English ZIP. [Narration and timing](../presentations/NARRATION_v71_EN.txt).

## What the recording shows

The opening uses retained demand context, then starts a new supplier task. The supplier enters a reply reporting carrier refusal and no allocated vehicle. A real Agent review checks the materials and prepares clarification. The supplier previews and authorizes disclosure.

The supplier then revises the reply to report carrier acceptance and an allocated vehicle. Before authorization, the planner still sees the earlier shared response. A second real Agent review changes the next question to the unresolved receiving appointment. After supplier authorization, the planner receives the revision.

The planner maintains the original 360-case plan and adds zero because extra demand is unquantified and receiving remains pending. A separate simulated retailer approval produces a persistent procurement-sandbox receipt, which is refreshed and read back.

## Evidence boundaries

- Model executions are real and prerecorded. Playback makes no model calls.
- The successful supplier task used six model calls, including independent review audits. This is one demonstration, not a reliability benchmark.
- Business records and acting roles are synthetic or simulated. Carrier acceptance and vehicle allocation are supplier reports, not independently verified events.
- Supplier disclosure and retailer procurement approval are different actions.
- SAP is not connected. No real purchase order, transport booking or shipment is created.
- Video timing is edited. No user time savings, demand-estimation accuracy, adoption or financial return is established.
- Earlier unsuccessful attempts and original artifacts remain in the private project records. The release does not include private traces, testing codes or access credentials.

## Playback

Open the PPTX in desktop PowerPoint with computer audio enabled. If embedded media playback is unavailable, play the standalone MP4. The voice is generated using ElevenLabs, Jeremy - Casual Guy Next Door. The earlier subtitle-only recording and prior decks remain preserved.

The public GitHub Pages replay and deployed cloud Agent are unchanged by this release. Older repository documentation describes historical versions and is not a claim about v71 implementation status.
