/* Builds ../SAP_Demand_Pulse_Business_Case_Deck.pptx
 * Run from this folder:  node business_case_deck.js            (live deck: 10-slide story + appendix)
 *                        PREREAD=1 node business_case_deck.js  (pre-read: executive summary as slide 2)
 * Content sources: docs/STAKEHOLDER_BRIEF.md, docs/PRODUCT_THESIS_AND_SANDBOX_PLAN.md,
 * docs/PROGRESS.md, docs/VALIDATION.md, procurement_sandbox/CONTRACT.md (all in this repository).
 */
const path = require("path");
const pptxgen = require("pptxgenjs");
const SKILL = "C:/Users/chntw/AppData/Local/Claude-Data/claude_pzs8sxrjxfjjc/local-agent-mode-sessions/skills-plugin/882cb59a-4473-42fb-b441-a15e945c8e67/d2a91106-eb50-4fe5-b638-45da0d80d1af/skills/pptx";
const { applyTheme } = require(path.join(SKILL, "scripts/apply_theme.js"));

const PREREAD = process.env.PREREAD === "1";
const OUT = path.resolve(__dirname, "..", PREREAD ? "SAP_Demand_Pulse_Business_Case_Deck_preread.pptx" : "SAP_Demand_Pulse_Business_Case_Deck.pptx");

// ---------------------------------------------------------------- theme
const THEME = {
  name: "Demand Pulse Evidence",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "14353A", lt1: "FFFFFF", dk2: "0F5C4D", lt2: "EEF4F2",
    accent1: "16765F", // teal: Built
    accent2: "C8781E", // amber: Hypothesis / caution
    accent3: "B3261E", // red: critical / losing
    accent4: "557078", // muted slate
    accent5: "D9E6E1", // hairline
    accent6: "9AB7AE", // sage
    hlink: "0F5C4D", folHlink: "557078",
  },
};
const H = THEME.colors;
const FOOT = "Demand Pulse · internal stakeholder review · synthetic business facts · procurement sandbox, not SAP connected";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "The J Collective";
pres.title = "Demand Pulse business case";
pres.subject = "Internal stakeholder review";
const C = pres.SchemeColor;
const W = 13.333, M = 0.6;

// ---------------------------------------------------------------- layouts
const titlePh = (color) => ({
  placeholder: { options: { name: "title", type: "title", x: M, y: 0.42, w: W - 2 * M, h: 0.95, fontSize: 30, bold: true, color, valign: "middle", margin: 0 }, text: "" },
});
const footer = (color) => ({ text: { text: FOOT, options: { x: M, y: 7.02, w: 10.6, h: 0.3, fontSize: 10, color, margin: 0 } } });
pres.defineSlideMaster({ title: "CONTENT", background: { color: H.lt1 }, objects: [titlePh(C.text1), footer(C.accent4)],
  slideNumber: { x: 12.1, y: 7.02, w: 0.6, h: 0.3, fontSize: 10, color: C.accent4, align: "right" } });
pres.defineSlideMaster({ title: "DARK", background: { color: H.dk1 }, objects: [footer(C.accent6)],
  slideNumber: { x: 12.1, y: 7.02, w: 0.6, h: 0.3, fontSize: 10, color: C.accent6, align: "right" } });

// ---------------------------------------------------------------- helpers
const T = (slide, text, o) => slide.addText(text, Object.assign({ isTextBox: true, margin: 0, fontSize: 14, color: C.text1, valign: "top" }, o));
const box = (slide, x, y, w, h, o = {}) => slide.addShape(pres.ShapeType.roundRect, Object.assign({ x, y, w, h, rectRadius: 0.06, fill: { color: C.background2 }, line: { color: H.accent5, width: 0.75 } }, o));
const rect = (slide, x, y, w, h, o = {}) => slide.addShape(pres.ShapeType.rect, Object.assign({ x, y, w, h, fill: { color: C.background2 }, line: { color: H.accent5, width: 0 } }, o));
const TIER = {
  Built: { fill: C.accent1, text: C.background1 }, "Real-model": { fill: C.text1, text: C.background1 },
  Desk: { fill: C.accent6, text: C.text1 }, Hypothesis: { fill: C.accent2, text: C.background1 }, "In progress": { fill: C.accent4, text: C.background1 },
};
function pill(slide, label, x, y, w = 1.15) {
  const t = TIER[label] || TIER.Desk;
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.3, rectRadius: 0.15, fill: { color: t.fill }, line: { color: t.fill, width: 0 } });
  slide.addText(label, { x, y, w, h: 0.3, fontSize: 10, bold: true, color: t.text, align: "center", valign: "middle", margin: 0, isTextBox: true });
}
function pills(slide, labels, x, y) { let cx = x; for (const l of labels) { const w = l.length > 9 ? 1.25 : 1.0; pill(slide, l, cx, y, w); cx += w + 0.12; } }
function numCircle(slide, n, x, y, d = 0.42, fill = C.accent1) {
  slide.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 } });
  slide.addText(String(n), { x, y, w: d, h: d, fontSize: 13, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
}
const bullets = (items, size = 14, after = 6) => items.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, fontSize: size, breakLine: i < items.length - 1, paraSpaceAfter: after } }));
function card(slide, x, y, w, h, head, body, opts = {}) {
  box(slide, x, y, w, h, opts.boxOpts);
  T(slide, head, { x: x + 0.2, y: y + 0.16, w: w - 0.4, h: 0.36, fontSize: opts.headSize || 15, bold: true, color: opts.headColor || C.text2 });
  if (Array.isArray(body)) slide.addText(bullets(body, opts.bodySize || 12.5, 4), { x: x + 0.2, y: y + 0.58, w: w - 0.4, h: h - 0.7, isTextBox: true, margin: 0, color: C.text1, valign: "top" });
  else T(slide, body, { x: x + 0.2, y: y + 0.58, w: w - 0.4, h: h - 0.7, fontSize: opts.bodySize || 12.5 });
}
const hdr = (t) => ({ text: t, options: { bold: true, color: H.lt1, fill: { color: H.dk2 }, fontSize: 12, valign: "middle" } });
const cell = (t, o = {}) => ({ text: t, options: Object.assign({ fontSize: 11.5, color: H.dk1, valign: "top" }, o) });
const tierCell = (t) => ({ text: t, options: { bold: true, fontSize: 11, color: t === "Desk" ? H.dk1 : H.lt1, fill: { color: t === "Built" ? H.accent1 : t === "Real-model" ? H.dk1 : t === "In progress" ? H.accent4 : H.accent2 }, align: "center", valign: "middle" } });
const tableOpts = (x, y, w, colW, extra = {}) => Object.assign({ x, y, w, colW, border: { type: "solid", pt: 0.5, color: H.accent5 }, fill: { color: H.lt1 }, margin: 0.06, autoPage: false, fontFace: THEME.bodyFontFace }, extra);
const quoteLine = (s, labels, q, qx) => { pills(s, labels, M, 1.5); T(s, q, { x: qx, y: 1.47, w: W - M - qx, h: 0.4, fontSize: 13, italic: true, color: C.accent4 }); };

// ================================================================ eight-minute run sheet (slides 6:00 + demo 2:00)
const TIMING = {
  title: "0:00–0:15 (15 s)", problem: "0:15–0:50 (35 s)", evidence: "0:50–1:25 (35 s)", promise: "1:25–1:50 (25 s)",
  alternatives: "1:50–2:20 (30 s)", how: "2:20–2:45 (25 s)", demo: "2:45–3:00 (15 s) · LIVE DEMO 3:00–5:00 (2:00)",
  proven: "5:00–5:15 (15 s, point, do not read)", wrong: "5:15–5:45 (30 s)", finance: "5:45–6:10 (25 s)",
  stakeholders: "6:10–6:50 (40 s)", plan: "6:50–7:25 (35 s)", asks: "7:25–7:45 (20 s) · 15 s buffer",
};
const note = (key, text) => (TIMING[key] ? `[${TIMING[key]}] ${text}` : text);

// ================================================================ slide library
const S = {};

S.title = (sec) => {
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: sec });
  T(s, "Demand Pulse", { x: M, y: 1.5, w: 12, h: 1.1, fontSize: 54, bold: true, color: C.background1, fontFace: THEME.headFontFace });
  T(s, "Business case: closing a replenishment exception from supplier reply to procurement handoff", { x: M, y: 2.7, w: 11.4, h: 1.0, fontSize: 24, color: C.accent6 });
  T(s, "The J Collective  ·  internal stakeholder review  ·  25 October 2026", { x: M, y: 3.95, w: 11, h: 0.4, fontSize: 14, color: C.accent6 });
  box(s, M, 5.0, 12.1, 1.3, { fill: { color: C.text2 }, line: { color: H.dk2, width: 0 } });
  T(s, "Read before judging the rest", { x: M + 0.3, y: 5.15, w: 6, h: 0.35, fontSize: 13, bold: true, color: C.accent6 });
  T(s, "Every business fact in this deck is synthetic. The procurement target is a sandbox that says \"not SAP connected\" on every response. Model costs are measured; savings, adoption and profit are hypotheses that a pilot is designed to test. We would rather you hear that from us.", { x: M + 0.3, y: 5.5, w: 11.5, h: 0.75, fontSize: 13, color: C.background1 });
  s.addNotes(note("title", "Open with the boundary. This is a business case for a pilot, not a claim of realised benefit. The story has three beats: the problem is a handoff, not a forecast; the model reads while rules decide and humans authorise; we have said in advance how we lose. Then one ask."));
};

S.exec = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("One exception, closed end to end, with every commercial authority in human hands", { placeholder: "title" });
  const cards = [
    ["Software development", "Built", ["Model reads, cites and drafts; rules decide what is permitted", "Failures are kept and linked, never erased", "Procurement write path built in an S/4HANA-shaped sandbox, 41 tests"]],
    ["Marketing", "Desk", ["One buyer, one job: an SAP retailer's planner facing an ambiguous supplier reply", "Four weaker differentiation claims withdrawn after a competitive check", "Retailer pays; supplier entry is free"]],
    ["Finance", "Real-model", ["Model cost under USD 1 per exception, measured on real calls", "Savings and integration cost not yet measured", "Pilot and stop rules defined before any number is promised"]],
    ["Product strategy", "Hypothesis", ["A wedge chosen by elimination, not by ambition", "Six losing conditions stated in advance", "Gated roadmap: acceptance, pilot, SAP read, SAP write"]],
  ];
  cards.forEach(([h, tier, items], i) => {
    const x = M + i * 3.08, y = 1.65, w = 2.9, hh = 3.25;
    box(s, x, y, w, hh);
    T(s, h, { x: x + 0.2, y: y + 0.18, w: w - 0.4, h: 0.35, fontSize: 15, bold: true, color: C.text2 });
    pill(s, tier, x + 0.2, y + 0.6);
    s.addText(bullets(items, 12.5, 5), { x: x + 0.2, y: y + 1.05, w: w - 0.4, h: hh - 1.2, isTextBox: true, margin: 0, color: C.text1, valign: "top" });
  });
  box(s, M, 5.25, 12.1, 1.3, { fill: { color: C.text2 }, line: { color: H.dk2, width: 0 } });
  T(s, "What we ask", { x: M + 0.3, y: 5.4, w: 4, h: 0.35, fontSize: 13, bold: true, color: C.accent6 });
  T(s, "Approve the twelve-day engineering acceptance on the connected loop, accept that savings are reported as hypotheses until real tasks exist, and help us find one partner for ten to twenty consecutive real exceptions.", { x: M + 0.3, y: 5.75, w: 11.5, h: 0.7, fontSize: 13.5, color: C.background1 });
  s.addNotes("One-page summary. In the live deck it sits in the appendix as a handout; in the pre-read build it is slide 2. Each card names the strongest evidence that function's section rests on.");
};

S.problem = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("The exception we handle: a plan change meets a free-form supplier reply", { placeholder: "title" });
  const chips = ["Promotion surge", "Stockout", "Short shipment", "Carrier or QA disruption", "Substitute or lot change", "Date move"];
  let cx = M;
  T(s, "Triggers:", { x: cx, y: 1.5, w: 0.9, h: 0.3, fontSize: 11.5, color: C.accent4, valign: "middle" });
  cx += 0.95;
  chips.forEach((c) => {
    const w = 0.085 * c.length + 0.3;
    s.addShape(pres.ShapeType.roundRect, { x: cx, y: 1.5, w, h: 0.3, rectRadius: 0.15, fill: { color: C.background2 }, line: { color: H.accent5, width: 0.75 } });
    T(s, c, { x: cx, y: 1.5, w, h: 0.3, fontSize: 10.5, color: C.text1, align: "center", valign: "middle" });
    cx += w + 0.1;
  });
  const steps = [
    ["A plan changes", "A promotion, a stockout, a short shipment, a QA hold or a date move puts an existing purchase plan in doubt."],
    ["The planner asks the supplier", "More, less, earlier, split, or a different lot. Usually by email, often to a coordinator who must ask logistics and QA."],
    ["The reply is free-form and partial", "\"Friday or Monday, same lot, the dates should be fine.\" Ship or arrive? How many? Which lot? Nothing a system can act on."],
    ["Facts are chased across functions", "Carrier, QA release, receiving slot, capacity and price are confirmed in separate threads and re-keyed into a sheet."],
    ["No handoff", "Nothing reaches procurement approval in a form it can act on. The decision, and the commitment, live in a mailbox."],
  ];
  steps.forEach(([h, b], i) => {
    const y = 2.0 + i * 0.92;
    numCircle(s, i + 1, M, y + 0.02);
    T(s, h, { x: M + 0.6, y, w: 6.2, h: 0.32, fontSize: 14, bold: true, color: C.text2 });
    T(s, b, { x: M + 0.6, y: y + 0.32, w: 6.5, h: 0.58, fontSize: 12 });
  });
  card(s, 7.9, 2.0, 4.8, 2.55, "What goes wrong today, every time", [
    "The same facts are typed three times: thread, sheet, approval note",
    "Available supply is mistaken for demand",
    "Missing evidence is forced to yes or no",
    "Commitments slip into email with no authority behind them",
    "Elapsed time is nobody's number",
  ], { bodySize: 12 });
  box(s, 7.9, 4.7, 4.8, 2.1);
  T(s, "The one instance we built and tested against", { x: 8.1, y: 4.85, w: 4.4, h: 0.35, fontSize: 13, bold: true, color: C.text2 });
  T(s, "CASE-1042: orange juice OJ-250, Toronto DC, supplier NorthOrchard, promotion window 24–28 October, plan 360 cases. Every fact is synthetic; the workflow is not. The same loop handles any trigger above: a supplier reply either changes an existing arrangement or it does not.", { x: 8.1, y: 5.2, w: 4.4, h: 1.1, fontSize: 11.5 });
  pill(s, "Desk", 8.1, 6.4);
  T(s, "Pattern supported by GCA/YouGov 2025, ACCC roundtables, Loblaw PO-update guide.", { x: 9.3, y: 6.4, w: 3.3, h: 0.35, fontSize: 10.5, color: C.accent4, valign: "middle" });
  s.addNotes(note("problem", "Beat one: the problem is a handoff, not a forecast, and it is a class, not a case. Name the triggers on the chips, then walk the five generic steps. CASE-1042 is the instance we built against; say that once and move on. The pain is that the information exists and nothing carries it to a decision."));
};

S.promise = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("The promise: a reply becomes a procurement handoff or a reasoned stop", { placeholder: "title" });
  box(s, M, 1.65, 12.1, 1.55);
  T(s, "When a supplier's new reply affects an existing replenishment arrangement, Demand Pulse turns it into either a change draft that can be submitted to the retailer's existing procurement approval, or a reasoned keep-the-plan / stop result. The planner does not re-key information already provided. Every commercial commitment is still approved by someone with the authority to make it.", { x: M + 0.3, y: 1.82, w: 11.5, h: 1.25, fontSize: 15, italic: true, color: C.text2 });
  const d = [
    ["Request a change", "CHANGE", "Evidence sufficient. A change draft carries original and proposed values, reason, evidence and open unknowns to procurement approval.", C.accent1],
    ["Keep the plan / stop", "KEEP · STOP", "Reason recorded, exception closed, original SAP plan untouched. No procurement object is created.", C.text2],
    ["Wait for specific information", "WAIT", "A to-do with an owner, a deadline and one focused question. Resumes when the reply lands. Never a permanent hand-off of the pile to a human.", C.accent2],
  ];
  d.forEach(([h, tag, b, col], i) => {
    const x = M + i * 4.1, y = 3.4, w = 3.9, hh = 2.05;
    box(s, x, y, w, hh);
    rect(s, x + 0.2, y + 0.18, 1.3, 0.32, { fill: { color: col } });
    T(s, tag, { x: x + 0.2, y: y + 0.18, w: 1.3, h: 0.32, fontSize: 11, bold: true, color: C.background1, align: "center", valign: "middle" });
    T(s, h, { x: x + 0.2, y: y + 0.6, w: w - 0.4, h: 0.35, fontSize: 15, bold: true, color: C.text2 });
    T(s, b, { x: x + 0.2, y: y + 0.98, w: w - 0.4, h: 1.0, fontSize: 12 });
  });
  box(s, M, 5.65, 5.95, 1.2, { fill: { color: C.background1 }, line: { color: H.accent1, width: 1 } });
  T(s, [{ text: "Demand evidence gate.  ", options: { bold: true, color: C.accent1 } }, { text: "Before any supply investigation, the Agent reads the retailer's demand records and gives a cited judgment: continue, clarify or pause. Only a current continue opens the next step. It judges whether the demand evidence supports pursuing additional supply; it never estimates unrecorded demand.", options: {} }], { x: M + 0.25, y: 5.75, w: 5.5, h: 1.0, fontSize: 11.5 });
  box(s, M + 6.15, 5.65, 5.95, 1.2, { fill: { color: C.background1 }, line: { color: H.accent2, width: 1 } });
  T(s, [{ text: "Quantity boundary.  ", options: { bold: true, color: C.accent2 } }, { text: "The only quantity basis is a request the buyer has already approved, or an explicit calculation rule over reconciled customer requests. The Agent decides whether the reply keeps that request feasible. Abundant supply never becomes demand.", options: {} }], { x: M + 6.4, y: 5.75, w: 5.5, h: 1.0, fontSize: 11.5 });
  s.addNotes(note("promise", "The end point is the handoff to procurement approval. Not 'the Agent made a suggestion', not 'the goods arrived'. Dwell on WAIT: missing evidence stays missing and resumable. Then the two boundaries: the demand evidence gate (continue / clarify / pause; it judges whether the demand evidence supports pursuing supply, it does not estimate unrecorded demand) and the quantity boundary (approved requests or an explicit rule, never supply as demand)."));
};

S.how = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("How it works: one loop, three kinds of authority", { placeholder: "title" });
  // kind: m = model, g = gate (model judgment, rule-enforced), r = rules, h = human, n = neutral
  const steps = [
    ["Supplier email arrives", "n"], ["Matched to the open case", "n"], ["Demand evidence gate: continue · clarify · pause", "g"],
    ["Evidence review by the model", "m"], ["Rule validation and model audit", "r"], ["Supplier authorises disclosure", "h"],
    ["Planner decides", "h"], ["Procurement sandbox receipt", "n"],
  ];
  const gap = 0.16, bw = (W - 2 * M - gap * (steps.length - 1)) / steps.length, y = 1.75;
  steps.forEach(([t, kind], i) => {
    const x = M + i * (bw + gap);
    const fill = kind === "h" ? C.accent2 : kind === "m" ? C.text1 : kind === "r" || kind === "g" ? C.accent1 : C.background2;
    box(s, x, y, bw, 1.05, { fill: { color: fill }, line: kind === "g" ? { color: H.dk1, width: 1.5, dashType: "dash" } : undefined });
    T(s, t, { x: x + 0.06, y, w: bw - 0.12, h: 1.05, fontSize: kind === "g" ? 10.5 : 11.5, bold: true, align: "center", valign: "middle", color: kind === "n" ? C.text1 : C.background1 });
    if (i < steps.length - 1) s.addShape(pres.ShapeType.rightArrow, { x: x + bw + 0.01, y: y + 0.41, w: 0.14, h: 0.23, fill: { color: C.accent4 }, line: { color: H.accent4, width: 0 } });
  });
  const bands = [
    ["Model may", C.text1, ["Discover and read authorised sources", "Judge whether the demand evidence supports pursuing additional supply: continue, clarify or pause, with citations", "Write cited interpretations and reconcile replies", "Identify unanswered conditions", "Draft one focused next action or a change draft"]],
    ["Rules enforce", C.accent1, ["Exact quotation of a source actually read", "Only a current continue judgment opens investigation; no estimate of unrecorded demand, ever", "Required condition coverage; unknown stays unknown", "Retained baseline; typed timing and quantity consistency", "Disclosure boundary, call cap, budget stop"]],
    ["Humans hold", C.accent2, ["Supplier: what is disclosed, and when", "Planner: authorise investigation, stop, or submit a change", "Procurement approver: release or return", "Nothing is bought, booked or sent without one of them"]],
  ];
  bands.forEach(([h, col, items], i) => {
    const x = M + i * 4.1, by = 3.15, w = 3.9, hh = 3.05;
    box(s, x, by, w, hh);
    rect(s, x + 0.2, by + 0.18, 1.6, 0.34, { fill: { color: col } });
    T(s, h, { x: x + 0.2, y: by + 0.18, w: 1.6, h: 0.34, fontSize: 12, bold: true, color: C.background1, align: "center", valign: "middle" });
    s.addText(bullets(items, 11.5, 4), { x: x + 0.2, y: by + 0.7, w: w - 0.4, h: hh - 0.85, isTextBox: true, margin: 0, color: C.text1, valign: "top" });
  });
  T(s, "Colours match the bands: dark is model work, teal is rules, amber is a human decision. The dashed box is a model judgment that rules enforce: it decides whether demand evidence justifies going further, not how much demand there is.", { x: M, y: 6.35, w: 12.1, h: 0.5, fontSize: 11.5, color: C.accent4 });
  s.addNotes(note("how", "Beat two: the model reads, rules decide, humans authorise. Point at the dashed box: the demand evidence gate. The model gives a cited continue / clarify / pause judgment on the retailer's demand records; rules let only a current continue open investigation. It judges whether the evidence supports pursuing supply; it never estimates unrecorded demand. The demo follows this slide."));
};

S.wrong = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Where the model was wrong, and what caught it", { placeholder: "title" });
  quoteLine(s, ["Real-model"], "Three retained failures from our own runs. We show them because the rule layer exists for exactly these.", 2.0);
  const cases = [
    ["It overstated the blocker", "Free-form inference experiment, test packet 2",
     "Its summary called the carrier failure \"the sole current blocker\" while receiving and capacity were still unknown. The same-model auditor accepted it.",
     "A human reading the prose against the typed states.",
     "Component not released. Summary-versus-state contradiction tests are now required before any integration."],
    ["It hid a quantity in the prose", "Real-model test, third synthetic item",
     "Withheld the structured quantity, but kept \"80 cases / CAD 770\" in its text, computed on unconfirmed demand and without freight.",
     "Offline semantic inspection; then a rule audit blocked the artifact from any use.",
     "Quantity consistency now enforced across summary, evidence and recommendation; the calculator refuses when inputs are missing. Planner-triggered correction, two calls: proposal removed, missing evidence requested."],
    ["It mixed up two timestamps and a count", "Real-model test, first synthetic item",
     "Confused DC arrival at 08:00Z with store usable time at 12:00Z, and wrote 250 excluded cases where the figure was 200.",
     "Review of the retained output.",
     "Timing claims are now typed and tied to named source fields. Corrected in three calls; the original prose stays visible beside the correction."],
  ];
  cases.forEach(([h, sub, said, caught, changed], i) => {
    const x = M + i * 4.1, y = 2.05, w = 3.9, hh = 3.65;
    box(s, x, y, w, hh);
    T(s, h, { x: x + 0.2, y: y + 0.14, w: w - 0.4, h: 0.4, fontSize: 14, bold: true, color: C.text2 });
    T(s, sub, { x: x + 0.2, y: y + 0.54, w: w - 0.4, h: 0.25, fontSize: 10, color: C.accent4 });
    T(s, [{ text: "What it said  ", options: { bold: true, color: C.accent3 } }, { text: said, options: {} }], { x: x + 0.2, y: y + 0.85, w: w - 0.4, h: 1.0, fontSize: 11.5 });
    T(s, [{ text: "What caught it  ", options: { bold: true, color: C.text2 } }, { text: caught, options: {} }], { x: x + 0.2, y: y + 1.9, w: w - 0.4, h: 0.55, fontSize: 11.5 });
    T(s, [{ text: "What changed  ", options: { bold: true, color: C.accent1 } }, { text: changed, options: {} }], { x: x + 0.2, y: y + 2.45, w: w - 0.4, h: 1.15, fontSize: 11.5 });
  });
  box(s, M, 5.9, 12.1, 0.9, { fill: { color: C.background1 }, line: { color: H.accent3, width: 1 } });
  T(s, [{ text: "The pattern.  ", options: { bold: true, color: C.accent3 } }, { text: "Structure passes, prose fails. Our answer is not a better prompt. It is a rule for that failure class, the failure kept on the timeline, and a linked correction that never overwrites the original. The second model audit remains a fallible review, not proof.", options: {} }], { x: M + 0.3, y: 6.02, w: 11.5, h: 0.7, fontSize: 12.5 });
  s.addNotes(note("wrong", "Say the weaknesses before the panel does. Each column is one real failure, what caught it, and the rule that now exists because of it. This is why the correction loop and preserved records matter more than any single good answer."));
};

S.proven = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("What we have proven, and what we have not", { placeholder: "title" });
  const tiers = [
    ["Built", "Implemented, tested, walked through in a browser", "Business value of any kind"],
    ["Real-model", "Real Claude Sonnet 4.6 calls on synthetic records; failures retained", "A success rate; behaviour on real documents"],
    ["Desk", "Public sources reviewed by the team", "Our effect size, user adoption, the binding bottleneck"],
    ["Hypothesis", "Stated targets with no measurement yet", "Anything, until the pilot runs with real participants"],
  ];
  tiers.forEach(([tier, meaning, cannot], i) => {
    const x = M + i * 3.08, y = 1.6, w = 2.9, hh = 1.7;
    box(s, x, y, w, hh);
    pill(s, tier, x + 0.2, y + 0.15, 1.25);
    T(s, meaning, { x: x + 0.2, y: y + 0.52, w: w - 0.4, h: 0.55, fontSize: 10.5, color: C.accent4 });
    T(s, [{ text: "Cannot establish  ", options: { bold: true, color: C.accent3 } }, { text: cannot, options: {} }], { x: x + 0.2, y: y + 1.12, w: w - 0.4, h: 0.5, fontSize: 10.5 });
  });
  const rows = [
    [hdr("Component"), hdr("Status"), hdr("Proves"), hdr("Does not prove")],
    [cell("Deployed task workspace for planner and supplier", { bold: true }), tierCell("Built"), cell("Decision card over retained real-model records; six offline tests; browser walkthrough"), cell("Any order, SAP write, labour saving or profit")],
    [cell("Interactive supplier reply flow", { bold: true }), tierCell("In progress"), cell("Edit, save, Agent check, authorise, planner update"), cell("Nothing yet: no validation record; not cited here")],
    [cell("Real-model tests on three synthetic items, with correction loop", { bold: true }), tierCell("Real-model"), cell("A conditional 140-case proposal, a zero-case result, one failure caught and repaired with linked records"), cell("A success rate; robustness on unseen documents")],
    [cell("Procurement sandbox, reference client, 41 tests", { bold: true }), tierCell("Built"), cell("S/4HANA-shaped write path: CSRF, roles, ETags, idempotency, stale-baseline 412, fault injection, audit"), cell("SAP write semantics; it is not SAP and says so")],
    [cell("Acceptance kit: ten frozen tasks, inbound contract, simulator, scorer", { bold: true }), tierCell("Built"), cell("The chain email → match → review → approval → receipt can be tested and scored against sandbox records"), cell("Independence: tasks authored on the development side; mail receipt simulated")],
  ];
  s.addTable(rows, tableOpts(M, 3.5, 12.1, [3.0, 1.15, 4.45, 3.5], { rowH: [0.36, 0.55, 0.5, 0.55, 0.55, 0.55] }));
  s.addNotes(note("proven", "One slide for 'what do you actually have'. Top row: the four evidence labels used throughout and what each cannot establish. Table: each artefact with its strongest label and the thing it does not prove. The in-progress reply flow is deliberately not used as evidence."));
};

S.finance = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Finance: model cost is measured and small; the business case is not yet measured", { placeholder: "title" });
  quoteLine(s, ["Real-model", "Hypothesis"], "\"Show me the unit economics, and why should I believe any of it when your own report says the simulated profit gains failed replication?\"", 3.2);
  s.addChart(pres.ChartType.bar, [
    { name: "Initial review", labels: ["Item A (140 cases)", "Item B (0 cases)", "Item C (blocked, repaired)"], values: [0.475, 0.359, 0.277] },
    { name: "Correction round", labels: ["Item A (140 cases)", "Item B (0 cases)", "Item C (blocked, repaired)"], values: [0.085, 0, 0.063] },
  ], {
    x: M, y: 2.0, w: 6.3, h: 3.2, barDir: "col", barGrouping: "stacked", chartColors: [H.accent1, H.accent2],
    showTitle: true, title: "Measured model cost per exception, USD (real calls on three synthetic items)", titleFontSize: 12, titleColor: H.dk1, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: "$0.000;;", dataLabelFontSize: 10, dataLabelColor: H.lt1, dataLabelFontFace: "+mn-lt",
    showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: "+mn-lt", legendColor: H.dk1,
    catAxisLabelFontSize: 10, catAxisLabelColor: H.dk1, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontSize: 10, valAxisLabelColor: H.accent4, valAxisLabelFontFace: "+mn-lt",
    valAxisLabelFormatCode: "$0.00", valGridLine: { color: H.accent5, size: 0.5 }, catGridLine: { style: "none" }, valAxisMaxVal: 0.6,
  });
  const stats = [["< USD 1", "per exception including one correction round, on prototype prompts"], ["3.03 / 4.00", "USD on the cloud ledger; project authorisation USD 20"], ["1 of 3", "items produced an unsupported quantity in prose; caught, quarantined, repaired"]];
  stats.forEach(([n, l], i) => {
    const y = 2.0 + i * 1.08;
    box(s, 7.2, y, 5.5, 0.95);
    T(s, n, { x: 7.4, y: y + 0.12, w: 2.2, h: 0.7, fontSize: 26, bold: true, color: C.text2, fontFace: THEME.headFontFace, valign: "middle" });
    T(s, l, { x: 9.6, y: y + 0.15, w: 3.0, h: 0.7, fontSize: 11.5, valign: "middle" });
  });
  box(s, M, 5.4, 12.1, 1.4, { fill: { color: C.background1 }, line: { color: H.accent2, width: 1 } });
  T(s, [{ text: "What the break-even depends on, all unmeasured.  ", options: { bold: true, color: C.accent2 } }, { text: "Active minutes saved per exception on both sides; critical errors avoided versus introduced; one-time integration and onboarding on the customer's SAP landscape. Illustrative only: at a CAD 45 per hour loaded planner cost, about one minute covers the model cost, so integration is the number that matters. The simulated demand-recovery gains were withdrawn (equal-cost recovery negative on FreshRetailNet-50K; replication failed) and are not in this case.", options: {} }], { x: M + 0.3, y: 5.52, w: 11.5, h: 1.2, fontSize: 12 });
  s.addNotes(note("finance", "Beat three begins: three measured numbers, one hypothesis, never blended. Pilot model spend for 10 to 20 exceptions across three arms is under USD 50; the real budget line is participant time and an integration scoping engagement."));
};

S.strategy = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Product strategy: a wedge chosen by elimination, released through gates", { placeholder: "title" });
  quoteLine(s, ["Hypothesis"], "\"You started with a responsive supply network and ended with one exception on one synthetic case. Wedge or retreat?\"", 2.0);
  card(s, M, 2.05, 4.6, 4.75, "Tested and dropped", [
    "A complete detection-and-response policy: did not reliably improve profit; could lose at equal cost",
    "Store transfers: gains tiny, failed the preregistered replication criterion",
    "Available supply as proof of demand: wrong, and now a rule violation",
    "Low-friction supplier network as the differentiator: covered by incumbents",
  ], { bodySize: 12 });
  T(s, "What survived every test: evidence preparation across fragmented replies, bounded follow-up, explicit correction, separated authority. Useful even when the demand signal is noise, because the exception still has to be closed.", { x: M + 0.2, y: 5.6, w: 4.2, h: 1.1, fontSize: 12, bold: true, color: C.text2 });
  const rows = [
    [hdr("Phase"), hdr("What ships"), hdr("Gate to proceed")],
    [cell("0 · now", { bold: true }), cell("Task workspace deployed; interactive reply flow in progress; sandbox, client and acceptance kit built"), cell("Validation record for the reply flow exists; feature freeze")],
    [cell("1 · acceptance, then pilot", { bold: true }), cell("Twelve-day engineering acceptance on the connected loop; then three arms on 10–20 consecutive real exceptions with one partner"), cell("Critical errors do not worsen; total human burden falls enough to cover model, verification and onboarding. If forms match, ship the form")],
    [cell("2 · SAP read", { bold: true }), cell("Baseline PO, stock, inbound and status read from a real tenant; identities for planner and supplier roles"), cell("A tenant owner validates the boundary; no write yet")],
    [cell("3 · SAP write", { bold: true }), cell("Version-linked change request into the existing approval process"), cell("The approval owner accepts the disposition format; idempotent write path tested")],
  ];
  s.addTable(rows, tableOpts(5.4, 2.05, 7.3, [1.6, 3.0, 2.7], { rowH: [0.4, 0.75, 1.25, 0.85, 0.8] }));
  T(s, "Stop conditions are on the next slide. Each gate is a decision the panel can hold us to.", { x: 5.4, y: 6.35, w: 7.3, h: 0.4, fontSize: 11.5, color: C.accent4 });
  s.addNotes(note("strategy", "The wedge was chosen by elimination: our own experiments killed the broad story. The gated roadmap is how four functions with competing priorities get one answer: each priority is a gate, and nobody's gate is skipped."));
};

S.lose = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("How we lose: six conditions, decided before the first test", { placeholder: "title" });
  box(s, M, 1.6, 12.1, 1.0);
  T(s, [{ text: "Thesis under test.  ", options: { bold: true, color: C.text2 } }, { text: "On exceptions whose reply channel and procurement object are connected, Demand Pulse cuts the median combined active handling time of planner and supplier by at least 30 percent against the current manual process without increasing critical errors, and by a further 15 percent against a strong form-and-rules workflow without shifting work onto the supplier. Both percentages are pre-set targets, frozen with the pilot partner before run one.", options: {} }], { x: M + 0.3, y: 1.72, w: 11.5, h: 0.8, fontSize: 12.5 });
  const rows = [
    [hdr("If the test shows"), hdr("Then we")],
    [cell("After connection a human still re-keys or re-organises the same information"), cell("Treat the loop as not closed; fix the workflow before claiming anything", { bold: true })],
    [cell("Active handling time misses the target"), cell("Do not claim an efficiency benefit", { bold: true })],
    [cell("Strong form-and-rules performs as well as the Agent"), cell("Ship the form and rules; no AI for its own sake", { bold: true })],
    [cell("Supplier workload rises enough to offset the retailer's gain"), cell("Redesign the division of work", { bold: true })],
    [cell("Any critical error: overstepped authority, wrong case matched, duplicate submission"), cell("Suspend automatic submission", { bold: true })],
    [cell("Time is dominated by production and transport, not information handling"), cell("Do not promise improved arrival", { bold: true })],
  ];
  s.addTable(rows, tableOpts(M, 2.8, 12.1, [7.0, 5.1], { rowH: [0.38, 0.52, 0.45, 0.45, 0.45, 0.52, 0.45] }));
  T(s, "Ten tasks can surface problems and tell us whether to continue. They cannot establish a stable commercial return, and the 15 percent margin is not statistically detectable at that size. Real decisions wait for dozens of real tasks.", { x: M, y: 6.3, w: 12.1, h: 0.55, fontSize: 11.5, color: C.accent4 });
  s.addNotes(note("lose", "The slide that makes the thesis falsifiable. Read row three aloud: if forms and rules match, we ship the form. A team willing to be beaten by a form is more credible than one promising a multiple."));
};

S.asks = (sec) => {
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: sec });
  T(s, "What we ask of this panel", { x: M, y: 0.5, w: 12, h: 0.9, fontSize: 32, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "middle" });
  const asks = [
    ["Software development", "Review the sandbox contract and the SAP boundary; agree the production-gap list as the definition of done for phase 2."],
    ["Marketing", "Approve the one-sentence positioning and the four withdrawn claims; agree that \"hidden demand recovery\" is not said."],
    ["Finance", "Accept that costs are reported as measured and savings as hypotheses until the pilot; help size the integration scoping engagement."],
    ["Product strategy", "Approve the gated roadmap and the six stop conditions; help find one partner for ten to twenty consecutive real exceptions."],
  ];
  asks.forEach(([h, b], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * 6.15, y = 1.65 + row * 1.95, w = 5.95, hh = 1.75;
    box(s, x, y, w, hh, { fill: { color: C.text2 }, line: { color: H.dk2, width: 0 } });
    T(s, h, { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: 0.35, fontSize: 15, bold: true, color: C.accent6 });
    T(s, b, { x: x + 0.25, y: y + 0.6, w: w - 0.5, h: 1.05, fontSize: 13, color: C.background1 });
  });
  T(s, "Next twelve days if approved", { x: M, y: 5.65, w: 6, h: 0.35, fontSize: 13, bold: true, color: C.accent6 });
  T(s, "Days 1–3: inbound endpoint, case matching, duplicate guard, transition timestamps.  Days 4–7: procurement approver role, submission with receipts and staleness check, case closure; one version, then freeze.  Days 8–12: run the ten frozen tasks, score against sandbox records, publish the engineering report. Business validation starts only when a partner provides real tasks.", { x: M, y: 6.0, w: 12.1, h: 0.95, fontSize: 12.5, color: C.background1 });
  s.addNotes(note("asks", "Close on decisions, not features. One yes-or-no per function. If there are thirty seconds left: we proved the loop runs, stays inside its authority, and catches and repairs its own errors; we have not proved it is worth buying; the pilot answers that, and we have written down what losing looks like."));
};

S.divider = (sec) => {
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: sec });
  T(s, "Appendix", { x: M, y: 2.4, w: 12, h: 1.0, fontSize: 44, bold: true, color: C.background1, fontFace: THEME.headFontFace });
  T(s, "Pages for questions: the one-page summary, evidence ladder, finance, gated roadmap, how we lose, one page per function, the validation plan, risks, and the numbers.", { x: M, y: 3.5, w: 11.5, h: 0.9, fontSize: 18, color: C.accent6 });
  s.addNotes("Everything after this is backup for questions. Jump by function.");
};

S.softdev = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Software development: the model never holds write authority", { placeholder: "title" });
  quoteLine(s, ["Built", "Real-model"], "\"How do you stop an LLM inventing a quantity, leaking supplier data, or quietly rewriting its own mistakes?\"", 3.2);
  card(s, M, 2.05, 5.95, 3.1, "Agent loop the service owns", [
    "Backend calls Claude Sonnet 4.6 through OpenRouter; every tool is implemented by the service, not the model",
    "The same validation handler runs in production and in tests",
    "A rejected submission returns correction_required with field-level findings; the code never edits the model's answer",
    "A second model audit runs after the rule checks; only an accepted artifact can be disclosed",
    "Failed attempts stay on the timeline as linked records",
  ], { bodySize: 12 });
  card(s, 6.75, 2.05, 5.95, 3.1, "Procurement write path (sandbox, S/4HANA-shaped)", [
    "CSRF handshake; role header: a supplier can never write",
    "ETag on PO and requisition; 412 when the baseline changed since the review",
    "Idempotency-Key replay and a case/evidence duplicate guard: a retry never creates a second object",
    "Fault injection including accept-then-fail, the case that separates \"sent\" from \"completed\"",
    "Read: PO, stock, status. Return: a version-linked change request into existing approval. No SAP API exercised",
  ], { bodySize: 12 });
  box(s, M, 5.4, 12.1, 1.15, { fill: { color: C.background1 }, line: { color: H.accent3, width: 1 } });
  T(s, [{ text: "What the rules do not do.  ", options: { bold: true, color: C.accent3 } }, { text: "They do not prove the prose is true (see the failures slide). The model audit shares failure modes with the generator. Production gaps we list ourselves: identity and tenant isolation, trusted record permissions, idempotent writes in a real tenant, monitoring and recovery, model-output security testing.", options: {} }], { x: M + 0.3, y: 5.52, w: 11.5, h: 0.95, fontSize: 12 });
  s.addNotes("Backup for the engineering questions. Why not a deterministic form: we may end up there; the pilot has that arm. Provider: one function isolates it; swapping to a direct Anthropic or SAP AI Core endpoint is configuration.");
};

S.marketing = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Marketing: one buyer, one job, four claims withdrawn", { placeholder: "title" });
  quoteLine(s, ["Desk"], "\"SAP has Business Network and Joule, SourceDay answers POs from an email link, Microsoft reads supplier mail. What is left to sell, and to whom?\"", 2.0);
  box(s, M, 2.05, 4.6, 2.7);
  T(s, "Withdrawn after the competitive check", { x: M + 0.2, y: 2.2, w: 4.2, h: 0.35, fontSize: 14, bold: true, color: C.accent3 });
  s.addText(["Low-friction onboarding of non-ERP suppliers", "Split-shipment confirmation", "Fresh-produce shelf-life planning", "Downstream impact analysis"].map((t, i) => ({ text: t, options: { strike: true, fontSize: 12.5, color: C.accent4, breakLine: i < 3, paraSpaceAfter: 5, bullet: { indent: 14 } } })), { x: M + 0.2, y: 2.6, w: 4.2, h: 1.6, isTextBox: true, margin: 0, valign: "top" });
  T(s, "Each is covered, or plausibly covered, by an incumbent.", { x: M + 0.2, y: 4.2, w: 4.2, h: 0.45, fontSize: 11.5, color: C.accent4 });
  box(s, 5.4, 2.05, 7.3, 2.7, { fill: { color: C.text2 }, line: { color: H.dk2, width: 0 } });
  T(s, "The one claim we kept", { x: 5.65, y: 2.2, w: 6.8, h: 0.35, fontSize: 14, bold: true, color: C.accent6 });
  T(s, "For a replenishment planner at an existing SAP retailer, when a demand concern meets an ambiguous supplier reply, Demand Pulse gets the arrival and lot conditions that actually change the decision, applies the retailer's existing rules, and hands both sides a cited, authorisable proposal, so the exception closes with less manual reconciliation on both ends and nothing is committed that the evidence does not support.", { x: 5.65, y: 2.6, w: 6.8, h: 2.05, fontSize: 13.5, italic: true, color: C.background1 });
  [["Buyer", "Category or replenishment manager at an SAP retail customer. Economic owner: procurement operations. The retailer pays."],
   ["Second user", "The supplier's customer-service or logistics coordinator: a private draft and an explicit authorisation step instead of an email thread. Free to the supplier."],
   ["Channel and claim", "An SAP partner extension on the existing landscape, not a standalone network. We claim lower total work at equal correctness, not a lower price."]]
    .forEach(([h, b], i) => card(s, M + i * 4.1, 4.95, 3.9, 1.85, h, b, { bodySize: 12 }));
  s.addNotes("Backup for positioning questions. Who pays: the retailer. Feature or product: feature-sized today; the pilot decides. Never say 'hidden demand recovery'.");
};

S.validation = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Two tests, reported apart: engineering acceptance, then business validation", { placeholder: "title" });
  box(s, M, 1.65, 5.95, 5.15);
  pill(s, "Built", M + 0.2, 1.82);
  T(s, "Engineering acceptance: ten frozen tasks", { x: M + 1.5, y: 1.8, w: 4.3, h: 0.35, fontSize: 14.5, bold: true, color: C.text2 });
  s.addText(bullets(["T01 Ambiguous reply → WAIT, no object", "T02 Explicit revision → CHANGE 140, released", "T03 Partial fulfilment → CHANGE 60 + WAIT 80", "T04 Bottles not cases → 140 CS, never 3,360", "T05 Wrong order → ask, no paid review", "T06 Duplicate and forward → one review, one PR", "T07 Stale after PO change → 412, re-review", "T08 Rejected by procurement → returned, open", "T09 Supply offered, no demand → KEEP or WAIT", "T10 502 then retry same key → exactly one PR"], 11.5, 3), { x: M + 0.2, y: 2.3, w: 5.55, h: 3.1, isTextBox: true, margin: 0, color: C.text1, valign: "top" });
  T(s, "Sealed by hash before the first run. The scorer cross-checks the application's export against the sandbox's own records and writes a report that states no business value. Authored on the development side: a development check, not a blinded test.", { x: M + 0.2, y: 5.45, w: 5.55, h: 1.25, fontSize: 11.5, color: C.accent4 });
  box(s, 6.75, 1.65, 5.95, 5.15);
  pill(s, "Hypothesis", 6.95, 1.82, 1.25);
  T(s, "Business validation: real tasks, real people", { x: 8.35, y: 1.8, w: 4.3, h: 0.35, fontSize: 14.5, bold: true, color: C.text2 });
  s.addText(bullets([
    "Three arms on the same materials and information rights: current process; strong form-and-rules; Agent-assisted",
    "10–20 consecutive real exceptions from one partner; counterbalanced so nobody handles a case twice",
    "Active minutes for planner and for supplier, separately",
    "Waiting time with its reason, separately; event gaps are not labour",
    "Critical errors, rework, omissions; share reaching the procurement handoff",
    "Model, verification, integration and maintenance cost",
  ], 12, 5), { x: 6.95, y: 2.3, w: 5.55, h: 3.1, isTextBox: true, margin: 0, color: C.text1, valign: "top" });
  box(s, 6.95, 5.75, 5.55, 0.85, { fill: { color: C.background1 }, line: { color: H.accent3, width: 1 } });
  T(s, "Without real participants we report engineering completion and error counts only. We generate no time-saving conclusion.", { x: 7.15, y: 5.85, w: 5.2, h: 0.7, fontSize: 12.5, bold: true, color: C.accent3, valign: "middle" });
  s.addNotes("Backup for 'how will you know'. Connecting the sandbox proves the product can complete the task; only the comparison on real tasks proves it is worth buying.");
};

S.risks = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Risks and limits we would rather name ourselves", { placeholder: "title" });
  const risks = [
    ["No measured business value", "No labour saving, demand accuracy, supplier adoption or financial return has been measured. Everything on that side is a target."],
    ["The sandbox is not SAP", "An S/4HANA-shaped mock proves the application-layer loop and labels itself on every response. SAP write semantics, identity and tenant rules are untested."],
    ["Tasks authored on the development side", "The ten acceptance tasks were written while building without a team. An outside author must rewrite bodies and keys, and re-freeze, before a result is cited."],
    ["Mail receipt is simulated for now", "Until a case mailbox domain exists, the simulator stands in for the inbound webhook. \"Mail receipt is a real connection\" is not yet true."],
    ["Correct structure, wrong prose", "Twice an output passed every provenance and schema check with a false statement in its text. A second model audit is a fallible review, not proof."],
    ["Incumbents may already cover this", "SAP Business Network Assistant, SourceDay and Microsoft's Procurement Agent cover adjacent steps. The form-and-rules arm exists so we find out before scaling."],
  ];
  risks.forEach(([h, b], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = M + col * 4.1, y = 1.65 + row * 2.55, w = 3.9, hh = 2.35;
    box(s, x, y, w, hh);
    numCircle(s, i + 1, x + 0.2, y + 0.2, 0.4, C.accent3);
    T(s, h, { x: x + 0.75, y: y + 0.2, w: w - 0.95, h: 0.45, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    T(s, b, { x: x + 0.2, y: y + 0.8, w: w - 0.4, h: hh - 0.95, fontSize: 12 });
  });
  s.addNotes("Also unverified: the in-progress reply flow, and whether the three end states are the ones real planners recognise. Two or three practitioner conversations are the cheapest fix.");
};

S.numbers = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Appendix: numbers to have ready", { placeholder: "title" });
  const rows = [
    [hdr("Figure"), hdr("Value"), hdr("Source")],
    [cell("Real-model calls in the three-item test"), cell("34 (items 15 / 11 / 8); USD 1.11"), cell("competition_v48/VALIDATION.txt")],
    [cell("Correction calls afterwards"), cell("5 (3 + 2); USD 0.147"), cell("competition_v49/VALIDATION.txt")],
    [cell("Model cost per exception incl. one correction"), cell("under USD 1"), cell("same")],
    [cell("Cloud ledger / cap; project authorisation"), cell("USD 3.03 / 4.00; USD 20"), cell("docs/PROGRESS.md")],
    [cell("Sandbox and acceptance tests; task-workspace offline tests"), cell("41 passed; 6 passed"), cell("procurement_sandbox/tests; competition_v50")],
    [cell("Real-model items failing semantic review before correction"), cell("1 of 3"), cell("docs/VALIDATION.md")],
    [cell("Free-form inference experiment on frozen novel packets"), cell("0 of 6; then 2 of 2 by labels with a manual semantic defect"), cell("competition_v36/RESULTS.md")],
    [cell("Simulated unmet-demand recovery, FRN: same safety stock vs equal waste"), cell("+46.6% vs −4.7%"), cell("for_docs/key_numbers_simulation.md")],
    [cell("BPI 2019 order-to-first-goods-receipt median; simulated saving"), cell("9.3 days; 5–11%"), cell("for_docs/key_numbers.md")],
    [cell("Pre-set pilot targets (not results)"), cell("−30% active time vs manual; −15% further vs strong forms"), cell("docs/PRODUCT_THESIS_AND_ SANDBOX_PLAN.md")],
    [cell("Pilot size"), cell("10–20 consecutive exceptions, three arms"), cell("docs/VALIDATION.md")],
  ];
  s.addTable(rows, tableOpts(M, 1.6, 12.1, [4.4, 4.4, 3.3], { rowH: 0.36 }));
  T(s, "Paths are relative to the repository logisticPM/sap; competition_v<NN> records live in the full project folder.", { x: M, y: 6.72, w: 12, h: 0.3, fontSize: 10.5, color: C.accent4 });
  s.addNotes("Backup slide. Use it when a number is challenged.");
};

// ---- Problem definition: user, workflow, evidence, reason to prioritise
S.evidence = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Who has this problem, and how we know it is real", { placeholder: "title" });
  quoteLine(s, ["Desk", "Real-model"], "A specific user, the current workflow, evidence of the pain, and the reason to prioritise it.", 3.2);
  card(s, M, 2.05, 3.9, 3.6, "The user and today's workflow", [
    "Primary user: the replenishment or category planner at an SAP retailer. Counterpart: the supplier's customer-service or logistics coordinator",
    "Today: the reply arrives by email; the planner chases carrier, QA and receiving slot in separate threads, re-keys the facts into a sheet, and writes the approval note by hand",
    "Pain: the same facts typed three times; missing evidence forced to yes or no; nothing reaches procurement in a form it can act on",
    "Frequency is not measured; the pilot counts it",
  ], { bodySize: 11.5 });
  const rows = [
    [hdr("Source"), hdr("What it shows"), hdr("What it cannot show")],
    [cell("UK GCA / YouGov 2025: 28 supplier interviews", { bold: true }), cell("Forecast-versus-order mismatch, portal burden, unclear stock risk"), cell("Canadian prevalence; the buyer's side")],
    [cell("ACCC supermarket inquiry 2024–25", { bold: true }), cell("Suppliers want PO certainty and forecast transparency; the regulator recommends both"), cell("A software remedy")],
    [cell("Loblaw PO-update guide; Mucci Farms role descriptions", { bold: true }), cell("A structured PO-change workflow and multi-party coordination exist today"), cell("Timing or frequency")],
    [cell("BPI Challenge 2019: real SAP purchasing log, 251,734 PO items", { bold: true }), cell("Order to first goods receipt median 9.3 days; about 12% of that time sits in compressible communication and approval steps; simulated agent saving 5–11%"), cell("Retail exceptions specifically")],
    [cell("Our own simulations on FreshRetailNet-50K and M5", { bold: true }), cell("The forecasting route failed: the full demand-response policy lost at equal cost; store transfers failed replication"), cell("That the handoff route pays; the pilot tests that")],
  ];
  s.addTable(rows, tableOpts(4.7, 2.05, 8.0, [2.5, 3.6, 1.9], { rowH: [0.36, 0.6, 0.6, 0.6, 0.85, 0.75] }));
  T(s, [{ text: "Why prioritise this.  ", options: { bold: true, color: C.text2 } }, { text: "It is the step where the information exists and no decision is reached, and it is the one route our own experiments did not eliminate. Still missing: direct planner interviews.", options: {} }], { x: 4.7, y: 6.0, w: 8.0, h: 0.75, fontSize: 12 });
  s.addNotes(note("evidence", "Problem definition carries twenty percent. Name the user, the workflow, and then the evidence ladder: two regulator studies, two retailer documents, one real SAP purchasing log with a 9.3-day median, and our own negative simulation results, which are why the handoff and not the forecast is the problem to solve. Say what is still missing: planner interviews."));
};

// ---- Product solution: improvement over alternatives, priorities, adoption, value vs cost
S.alternatives = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Why this, and not the alternatives", { placeholder: "title" });
  quoteLine(s, ["Desk", "Built"], "The honest competitor is a strong form with the same rules. The pilot includes it as an arm.", 3.2);
  const rows = [
    [hdr(""), hdr("Today: email + spreadsheet"), hdr("Strong form + rules"), hdr("Incumbent modules (SAP BN, SourceDay, Microsoft)"), hdr("Demand Pulse")],
    [cell("Reads a free-text reply", { bold: true }), cell("Human reads and re-types"), cell("Not read; the supplier fills fields"), cell("Partly: document and email parsing in some editions"), cell("Model reads and cites; rules check the citation")],
    [cell("Asks only what changes the decision", { bold: true }), cell("Depends on the planner"), cell("Fixed field list every time"), cell("Reminders and status chasing"), cell("Model drafts one question; rules route the owner")],
    [cell("Missing evidence", { bold: true }), cell("Forced to yes or no"), cell("Blank field, often ignored"), cell("Varies by product"), cell("Stays unknown: WAIT with owner and deadline")],
    [cell("Authority separation", { bold: true }), cell("None in the thread"), cell("Possible if designed"), cell("Inside their own approval flows"), cell("Enforced in code and in the sandbox; a supplier can never submit")],
    [cell("Handoff to procurement approval", { bold: true }), cell("A note typed by hand"), cell("Form output"), cell("Native to their suite"), cell("Version-linked change request with the evidence hash")],
    [cell("Cost to adopt", { bold: true }), cell("None; paid in minutes"), cell("Low"), cell("Licence plus integration"), cell("Model under USD 1 per exception; integration dominates")],
  ];
  s.addTable(rows, tableOpts(M, 2.05, 12.1, [2.2, 2.3, 2.3, 2.7, 2.6], { rowH: [0.42, 0.5, 0.5, 0.5, 0.55, 0.5, 0.5] }));
  box(s, M, 5.75, 12.1, 1.05);
  T(s, [{ text: "Priorities and adoption.  ", options: { bold: true, color: C.text2 } }, { text: "We built the loop and its guardrails before any forecasting, because the form arm is the real competitor. The retailer pays; the supplier keeps replying by email, no new portal. We do not claim to be cheaper than incumbents; we claim less total work at equal correctness, and the pilot measures exactly that.", options: {} }], { x: M + 0.3, y: 5.88, w: 11.5, h: 0.85, fontSize: 12 });
  s.addNotes(note("alternatives", "Product solution carries twenty percent: improvement over alternatives, feature priority, adoption, value against cost. Read the table by rows, not columns. Dwell on the second column: a strong form with our rules may be enough, and we will find out before scaling."));
};

// ---- Prototype: the core workflow in frames (live demo follows)
S.demo = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Demo: the core workflow in six frames", { placeholder: "title" });
  quoteLine(s, ["Built"], "Real captures of the deployed workbench on synthetic data; frame 6 is the sandbox's answer. The live demo follows this slide.", 2.0);
  const assets = path.join(__dirname, "assets");
  const frames = [
    ["Supplier writes the reply; private until authorised", "frame_1_supplier_reply.png"],
    ["Agent reads the sources; a rule check forces a revision", "frame_2_agent_reads.png"],
    ["Planner sees the authorised quote and the decision card", "frame_3_planner_card.png"],
    ["Procurement review prepared; approvals stay separate", "frame_4_procurement_review.png"],
    ["Planner authorises limited investigation, or closes", "frame_5_planner_decision.png"],
    ["Procurement sandbox receipt", null],
  ];
  frames.forEach(([cap, file], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = M + col * 4.1, y = 2.0 + row * 2.45, w = 3.9, hh = 2.3;
    box(s, x, y, w, hh);
    numCircle(s, i + 1, x + 0.15, y + 0.12, 0.34);
    T(s, cap, { x: x + 0.58, y: y + 0.1, w: w - 0.7, h: 0.4, fontSize: 11.5, bold: true, color: C.text2, valign: "middle" });
    if (file) {
      s.addImage({ path: path.join(assets, file), x: x + 0.15, y: y + 0.58, w: w - 0.3, h: hh - 0.72, sizing: { type: "contain", w: w - 0.3, h: hh - 0.72 } });
    } else {
      rect(s, x + 0.15, y + 0.58, w - 0.3, hh - 0.72, { fill: { color: C.text1 } });
      T(s, [
        { text: "POST A_PurchaseRequisitionHeader", options: { bold: true, breakLine: true } },
        { text: "201 Created · PR 1000000001", options: { breakLine: true } },
        { text: "status: awaiting procurement approval", options: { breakLine: true } },
        { text: "X-Procurement-Sandbox: not-SAP-connected", options: { breakLine: true } },
        { text: "retry, same key → 200 already submitted", options: { breakLine: true } },
        { text: "approver release → released", options: {} },
      ], { x: x + 0.3, y: y + 0.68, w: w - 0.6, h: hh - 0.92, fontSize: 9.5, color: C.background1, fontFace: "Courier New", valign: "top", paraSpaceAfter: 2 });
    }
  });
  s.addNotes(note("demo", "Prototype carries twenty percent. Fifteen seconds on this slide, then two minutes live. Narrate the authority at each step, not the UI: who may see what, who may authorise what, what the rules refused. If the live demo fails, walk these six frames instead."));
};

// ---- Stakeholder alignment: competing needs, trade-offs, limitations
S.stakeholders = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Four stakeholders, and the trade-offs we made", { placeholder: "title" });
  quoteLine(s, ["Built", "Real-model", "Hypothesis"], "Each row is a need we could not fully satisfy at once. The evidence label says how firm our answer is.", 4.4);
  const rows = [
    [hdr("Stakeholder"), hdr("They need"), hdr("We chose"), hdr("We gave up"), hdr("Evidence")],
    [cell("Software development", { bold: true }), cell("Reliability; a clear SAP boundary; no model with write rights"), cell("Rules in the write path; the same handler in production and tests; failures retained; a sandbox contract that says what it is not"), cell("Feature speed; the interactive reply flow is still unvalidated"), tierCell("Built")],
    [cell("Marketing", { bold: true }), cell("A differentiated story"), cell("One claim for one buyer; four weaker claims withdrawn after the competitive check"), cell("The \"network\" narrative; any price advantage"), tierCell("Desk")],
    [cell("Finance", { bold: true }), cell("A return"), cell("Measured cost: under USD 1 per exception; cloud ledger USD 3.03 of 4.00. Pre-set targets, kill rules, pilot model spend under USD 50"), cell("Any savings number today; it is a hypothesis until the pilot"), tierCell("Real-model")],
    [cell("Product strategy", { bold: true }), cell("A scalable wedge"), cell("The exception handoff, released through four gates"), cell("Forecasting, store transfers, autonomous buying"), tierCell("Hypothesis")],
  ];
  s.addTable(rows, tableOpts(M, 2.05, 12.1, [1.8, 2.5, 3.9, 2.7, 1.2], { rowH: [0.4, 0.85, 0.65, 0.85, 0.65] }));
  box(s, M, 5.75, 12.1, 1.05, { fill: { color: C.text2 }, line: { color: H.dk2, width: 0 } });
  T(s, [{ text: "Where they still conflict.  ", options: { bold: true, color: C.accent6 } }, { text: "Marketing wants a bigger claim than finance will fund and engineering will stand behind. The gated roadmap resolves it: each gate is one function's condition, and no gate is skipped. Limitations we own: no measured value, a sandbox that is not SAP, tasks authored on the development side, model prose that can pass checks and still be wrong.", options: { color: C.background1 } }], { x: M + 0.3, y: 5.88, w: 11.5, h: 0.85, fontSize: 12 });
  s.addNotes(note("stakeholders", "Stakeholder alignment carries twenty percent. Read one row per function: what they need, what we chose, what we gave up. Then the conflict and how the gates resolve it. End on the limitations we own; docs/STAKEHOLDER_BRIEF.md has a full page per function for follow-up questions."));
};

// ---- Implementation plan: resources, dependencies, milestones, success criteria, risks
S.plan = (sec) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
  s.addText("Implementation plan: twelve days, then a pilot, then SAP in two steps", { placeholder: "title" });
  quoteLine(s, ["Hypothesis"], "Resources, dependencies, milestones, success criteria and stop rules, all stated before run one.", 2.0);
  card(s, M, 2.05, 3.9, 3.6, "Milestones", [
    "Days 1–3: inbound endpoint, case matching, duplicate guard, transition timestamps",
    "Days 4–7: procurement approver role, submission with receipts and staleness check, case closure; one version, then freeze",
    "Days 8–12: run the ten frozen tasks, score against sandbox records, publish the engineering report",
    "Then: three-arm pilot on 10–20 real exceptions when a partner exists; SAP read on a real tenant; SAP write into existing approval",
  ], { bodySize: 11.5 });
  card(s, M + 4.1, 2.05, 3.9, 3.6, "Resources and dependencies", [
    "Two builders and two model lanes; no new hires",
    "A case mailbox domain, or the inbound simulator until one exists",
    "A reachable sandbox host (tunnel for development, a small host for a stable demo)",
    "One partner with 10–20 consecutive real exceptions and timestamps",
    "An SAP tenant owner to validate the read boundary before phase 2",
    "Budget: project cap USD 20; cloud USD 3.03 of 4.00 used; pilot model spend under USD 50",
  ], { bodySize: 11.5 });
  card(s, M + 8.2, 2.05, 3.9, 3.6, "Success criteria and stop rules", [
    "Engineering: all ten tasks run end to end; zero critical errors; every claim confirmed by sandbox records",
    "Business: −30% combined active time versus manual; −15% further versus a strong form; no work shifted to the supplier; errors not worse",
    "Stop: forms match → ship the form. Any critical error → suspend automatic submission. Production or transport dominate → no arrival promise",
  ], { bodySize: 11.5 });
  box(s, M, 5.85, 12.1, 0.95, { fill: { color: C.background1 }, line: { color: H.accent3, width: 1 } });
  T(s, [{ text: "Top risks.  ", options: { bold: true, color: C.accent3 } }, { text: "No partner appears, so business validation never starts; the sandbox is mistaken for SAP; the ten tasks are read as a blinded test when they are not. Each is named in the report before anyone else names it.", options: {} }], { x: M + 0.3, y: 5.97, w: 11.5, h: 0.75, fontSize: 12 });
  s.addNotes(note("plan", "Implementation plan carries ten percent. Milestones, resources, dependencies, success criteria and stop rules in one view. The twelve days produce an engineering report, never a business number; the pilot needs a partner."));
};

// ================================================================ order
// One continuous deck, no appendix. Slides kept in the library but not shown: exec (shown with PREREAD=1),
// divider, strategy, lose, softdev, marketing, validation, risks, numbers. Their content lives in
// docs/STAKEHOLDER_BRIEF.md and docs/PRODUCT_THESIS_AND_SANDBOX_PLAN.md; add a key below to bring one back.
const story = ["title", PREREAD ? "exec" : null, "problem", "evidence", "promise", "alternatives", "how", "demo", "proven", "wrong", "finance", "stakeholders", "plan", "asks"].filter(Boolean);
const appendix = [];
pres.addSection({ title: "Demand Pulse business case" });
story.forEach((k) => S[k]("Demand Pulse business case"));

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log(`wrote ${OUT} (${story.length} slides${appendix.length ? ` + ${appendix.length} appendix` : ", no appendix"})`);
})().catch((e) => { console.error(e); process.exit(1); });
