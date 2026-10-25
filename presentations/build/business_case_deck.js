/* Builds ../SAP_Demand_Pulse_Business_Case_Deck.pptx
 * Run from this folder:  node business_case_deck.js
 * Lean product-design deck: one message per slide, ~35 words of body, detail in speaker notes.
 * Order follows the judging rubric: problem (20) · solution (20) · prototype (20) · alignment (20) · plan (10) · delivery (10).
 * Sources: docs/STAKEHOLDER_BRIEF.md, docs/PRODUCT_THESIS_AND_SANDBOX_PLAN.md, docs/PROGRESS.md, docs/VALIDATION.md.
 */
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const SKILL = "C:/Users/chntw/AppData/Local/Claude-Data/claude_pzs8sxrjxfjjc/local-agent-mode-sessions/skills-plugin/882cb59a-4473-42fb-b441-a15e945c8e67/d2a91106-eb50-4fe5-b638-45da0d80d1af/skills/pptx";
const { applyTheme } = require(path.join(SKILL, "scripts/apply_theme.js"));
const OUT = path.resolve(__dirname, "..", "SAP_Demand_Pulse_Business_Case_Deck.pptx");
const ASSETS = path.join(__dirname, "assets");

// ---------------------------------------------------------------- theme
const THEME = {
  name: "Demand Pulse Evidence", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "14353A", lt1: "FFFFFF", dk2: "0F5C4D", lt2: "EEF4F2", accent1: "16765F", accent2: "C8781E", accent3: "B3261E", accent4: "557078", accent5: "D9E6E1", accent6: "9AB7AE", hlink: "0F5C4D", folHlink: "557078" },
};
const H = THEME.colors;
const FOOT = "Demand Pulse · synthetic business facts · procurement sandbox, not SAP connected";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "The J Collective";
pres.title = "Demand Pulse business case";
const C = pres.SchemeColor;
const W = 13.333, M = 0.6;

const titlePh = (color) => ({ placeholder: { options: { name: "title", type: "title", x: M, y: 0.45, w: W - 2 * M, h: 0.9, fontSize: 32, bold: true, color, valign: "middle", margin: 0, align: "left" }, text: "" } });
const footer = (color) => ({ text: { text: FOOT, options: { x: M, y: 7.02, w: 10.6, h: 0.3, fontSize: 10, color, margin: 0 } } });
pres.defineSlideMaster({ title: "CONTENT", background: { color: H.lt1 }, objects: [titlePh(C.text1), footer(C.accent4)], slideNumber: { x: 12.1, y: 7.02, w: 0.6, h: 0.3, fontSize: 10, color: C.accent4, align: "right" } });
pres.defineSlideMaster({ title: "DARK", background: { color: H.dk1 }, objects: [footer(C.accent6)], slideNumber: { x: 12.1, y: 7.02, w: 0.6, h: 0.3, fontSize: 10, color: C.accent6, align: "right" } });

// ---------------------------------------------------------------- helpers
const T = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, margin: 0, fontSize: 14, color: C.text1, valign: "top" }, o));
const box = (s, x, y, w, h, o = {}) => s.addShape(pres.ShapeType.roundRect, Object.assign({ x, y, w, h, rectRadius: 0.08, fill: { color: C.background2 }, line: { color: H.accent5, width: 0.75 } }, o));
const rect = (s, x, y, w, h, o = {}) => s.addShape(pres.ShapeType.rect, Object.assign({ x, y, w, h, fill: { color: C.background2 }, line: { color: H.accent5, width: 0 } }, o));
const TIER = { Built: [C.accent1, C.background1], "Real-model": [C.text1, C.background1], Desk: [C.accent6, C.text1], Hypothesis: [C.accent2, C.background1], Planned: [C.accent4, C.background1], Live: [C.accent1, C.background1] };
function pill(s, label, x, y, w = 1.15, h = 0.3, size = 10) {
  const [f, t] = TIER[label] || TIER.Desk;
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: h / 2, fill: { color: f }, line: { color: f, width: 0 } });
  T(s, label, { x, y, w, h, fontSize: size, bold: true, color: t, align: "center", valign: "middle" });
}
function pills(s, labels, x, y) { let cx = x; for (const l of labels) { const w = l.length > 9 ? 1.25 : 1.0; pill(s, l, cx, y, w); cx += w + 0.12; } }
// Evidence labels are shown only on the "proven / not proven" slide; status legends (Live / Planned) stay where they are.
function tagline(s, labels, text) {
  const status = labels.filter((l) => l === "Live" || l === "Planned");
  if (status.length) pills(s, status, M, 1.45);
  T(s, text, { x: M + (status.length ? status.length * 1.12 + 0.1 : 0), y: 1.42, w: 11.5, h: 0.36, fontSize: 13, italic: true, color: C.accent4, valign: "middle" });
}
function num(s, n, x, y, d = 0.42, fill = C.accent1) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 } });
  T(s, String(n), { x, y, w: d, h: d, fontSize: 13, bold: true, color: C.background1, align: "center", valign: "middle" });
}
const bullets = (items, size = 13, after = 5) => items.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, fontSize: size, breakLine: i < items.length - 1, paraSpaceAfter: after } }));
function stat(s, x, y, w, h, big, label, color = C.text2) {
  box(s, x, y, w, h);
  T(s, big, { x: x + 0.25, y: y + 0.15, w: w - 0.5, h: 0.75, fontSize: 34, bold: true, color, fontFace: THEME.headFontFace, valign: "middle" });
  T(s, label, { x: x + 0.25, y: y + 0.92, w: w - 0.5, h: h - 1.0, fontSize: 12, color: C.text1 });
}
function card(s, x, y, w, h, head, body, o = {}) {
  box(s, x, y, w, h, o.boxOpts);
  T(s, head, { x: x + 0.22, y: y + 0.18, w: w - 0.44, h: 0.38, fontSize: o.headSize || 16, bold: true, color: o.headColor || C.text2 });
  if (Array.isArray(body)) s.addText(bullets(body, o.bodySize || 13, 5), { x: x + 0.22, y: y + 0.62, w: w - 0.44, h: h - 0.75, isTextBox: true, margin: 0, color: C.text1, valign: "top" });
  else T(s, body, { x: x + 0.22, y: y + 0.62, w: w - 0.44, h: h - 0.75, fontSize: o.bodySize || 13 });
}
const hdr = (t) => ({ text: t, options: { bold: true, color: H.lt1, fill: { color: H.dk2 }, fontSize: 12.5, valign: "middle" } });
const cell = (t, o = {}) => ({ text: t, options: Object.assign({ fontSize: 12.5, color: H.dk1, valign: "middle" }, o) });
const tableOpts = (x, y, w, colW, extra = {}) => Object.assign({ x, y, w, colW, border: { type: "solid", pt: 0.5, color: H.accent5 }, fill: { color: H.lt1 }, margin: 0.08, autoPage: false, fontFace: THEME.bodyFontFace }, extra);

const TIMING = {
  title: "0:00–0:10", problem: "0:10–0:35", evidence: "0:35–0:55", promise: "0:55–1:15", alternatives: "1:15–1:35", how: "1:35–1:55",
  demo: "1:55–4:55 · VIDEO 3:00", proven: "4:55–5:10", wrong: "5:10–5:35", finance: "5:35–5:55", stakeholders: "5:55–6:30", plan: "6:30–7:00", vision: "7:00–7:25", asks: "7:25–7:50 · 10 s buffer",
};
const note = (k, t) => `[${TIMING[k]}] ${t}`;
const DELIV = path.resolve(__dirname, "../../../deliverable");
const VIDEO = path.join(DELIV, "competition_v62_video/Demand_Pulse_Demand_to_Decision_EN.mp4");
const VIDEO_COVER = path.join(DELIV, "competition_v62_video/check_15.png");
const S = {};

// ================================================================ 1 title
S.title = () => {
  const s = pres.addSlide({ masterName: "DARK" });
  T(s, "Demand Pulse", { x: M, y: 1.6, w: 12, h: 1.1, fontSize: 56, bold: true, color: C.background1, fontFace: THEME.headFontFace });
  T(s, "From demand signal to procurement decision: evidence-checked, human-approved", { x: M, y: 2.8, w: 12.1, h: 1.0, fontSize: 23, color: C.accent6 });
  T(s, "The J Collective  ·  internal stakeholder review  ·  25 October 2026", { x: M, y: 4.0, w: 11, h: 0.4, fontSize: 14, color: C.accent6 });
  s.addShape(pres.ShapeType.roundRect, { x: M, y: 5.6, w: 7.9, h: 0.42, rectRadius: 0.21, fill: { color: C.text2 }, line: { color: H.dk2, width: 0 } });
  T(s, "Synthetic data  ·  procurement sandbox, not SAP  ·  costs measured, value still a hypothesis", { x: M + 0.3, y: 5.6, w: 7.4, h: 0.42, fontSize: 12.5, color: C.background1, valign: "middle" });
  s.addNotes(note("title", "Say the boundary out loud in three sentences: every business fact is synthetic; the procurement target is a sandbox that says 'not SAP connected' on every response; model costs are measured, savings and profit are hypotheses a pilot is designed to test. We would rather you hear that from us. Then the three beats: the problem is a handoff, not a forecast; the model reads while rules decide and humans authorise; we have said in advance how we lose."));
};

// ================================================================ 2 problem
S.problem = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("One demand signal, two people, nowhere to decide", { placeholder: "title" });
  // personas
  const personas = [["Retail replenishment planner", "Owns the shelf. Answers for stockouts and for waste."], ["Supplier coordinator", "Owns the truck. Sees orders, never what shoppers wanted."]];
  personas.forEach(([h, b], i) => {
    const x = M + i * 6.15;
    box(s, x, 1.5, 5.95, 0.95);
    num(s, i === 0 ? "P" : "S", x + 0.2, 1.76, 0.42, i === 0 ? C.accent2 : C.text2);
    T(s, h, { x: x + 0.8, y: 1.6, w: 5.0, h: 0.35, fontSize: 15, bold: true, color: C.text2 });
    T(s, b, { x: x + 0.8, y: 1.95, w: 5.0, h: 0.4, fontSize: 12, color: C.accent4 });
  });
  // five steps with delay dots
  const steps = [["A demand signal", "stockout, promotion, a spike, a short ship", false], ["Worth pursuing?", "today: gut feel, no evidence on record", true], ["Supplier reply is free-form", "\"Friday or Monday, same lot, should be fine\"", true], ["Facts chased by email", "carrier, QA, slot, capacity, price, re-keyed", false], ["No handoff", "nothing procurement can act on", true]];
  const bw = 2.3, gap = 0.15, y = 2.75;
  steps.forEach(([h, b, delay], i) => {
    const x = M + i * (bw + gap);
    box(s, x, y, bw, 1.75, { fill: { color: delay ? C.background1 : C.background2 }, line: { color: delay ? H.accent3 : H.accent5, width: delay ? 1.25 : 0.75 } });
    num(s, i + 1, x + 0.18, y + 0.18, 0.38, delay ? C.accent3 : C.accent1);
    T(s, h, { x: x + 0.18, y: y + 0.65, w: bw - 0.36, h: 0.4, fontSize: 13.5, bold: true, color: C.text2 });
    T(s, b, { x: x + 0.18, y: y + 1.05, w: bw - 0.36, h: 0.65, fontSize: 11.5, color: C.accent4 });
    if (i < steps.length - 1) s.addShape(pres.ShapeType.rightArrow, { x: x + bw + 0.005, y: y + 0.75, w: 0.14, h: 0.24, fill: { color: C.accent4 }, line: { color: H.accent4, width: 0 } });
  });
  // three pains
  const pains = [["Demand judged by gut", "no cited evidence, no record of why"], ["Supply mistaken for demand", "an offer is not a need"], ["Decisions live in a mailbox", "no authority, no handoff, no clock"]];
  pains.forEach(([h, b], i) => {
    const x = M + i * 4.1;
    box(s, x, 4.75, 3.9, 1.15);
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.22, y: 4.98, w: 0.26, h: 0.26, fill: { color: C.accent3 }, line: { color: H.accent3, width: 0 } });
    T(s, h, { x: x + 0.6, y: 4.9, w: 3.1, h: 0.4, fontSize: 15, bold: true, color: C.text1 });
    T(s, b, { x: x + 0.6, y: 5.28, w: 3.1, h: 0.5, fontSize: 12, color: C.accent4 });
  });
  T(s, "Red = where the decision goes wrong today.  Built and tested on one synthetic instance, CASE-1042: orange juice, Toronto DC. The loop is the same for any signal.", { x: M, y: 6.15, w: 12.1, h: 0.5, fontSize: 11.5, color: C.accent4 });
  s.addNotes(note("problem", "Problem definition, twenty percent. Start with the pulse: a stockout during a promotion, a spike, a short shipment. Two users: the planner who owns the shelf, the coordinator who owns the truck. Five steps; the red ones are where the decision goes wrong: whether the signal is worth pursuing is judged by gut with nothing on record, the supplier's reply is free-form, and nothing reaches procurement in a form it can act on. CASE-1042 is the instance we built against. Workflow synthesised from desk research; planner interviews are the first pilot activity."));
};

// ================================================================ 3 evidence
S.evidence = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("The handoff is the step our evidence did not eliminate", { placeholder: "title" });
  tagline(s, ["Desk", "Real-model"], "Four numbers behind the problem; each with what it cannot show.");
  const stats = [
    ["9.3 days", "median from order to first goods receipt in a real SAP purchasing log, 251,734 PO items (BPI Challenge 2019)"],
    ["12%", "of that time sits in compressible communication and approval steps; simulated agent saving 5–11%"],
    ["28", "supplier interviews (UK GCA / YouGov 2025): forecast-versus-order mismatch, portal burden, unclear stock risk"],
    ["−4.7%", "unmet-demand recovery at equal waste in our own simulation: the forecasting route failed, so the handoff is the wedge"],
  ];
  stats.forEach(([n, l], i) => stat(s, M + i * 3.08, 2.0, 2.9, 2.6, n, l, i === 3 ? C.accent3 : C.text2));
  box(s, M, 4.85, 12.1, 1.9);
  T(s, "Why this problem, and what is still missing", { x: M + 0.25, y: 5.0, w: 11.5, h: 0.35, fontSize: 15, bold: true, color: C.text2 });
  s.addText(bullets([
    "Regulators (ACCC 2024–25) and retailer documents (Loblaw PO-update guide, Mucci Farms roles) show the workflow exists and hurts; none measure its timing",
    "The information exists at every step; nothing carries it to a decision. That is a handoff problem, not a forecasting problem",
    "Not yet done: direct planner interviews and a measured frequency. Both are the first pilot activity",
  ], 12.5, 4), { x: M + 0.25, y: 5.4, w: 11.6, h: 1.3, isTextBox: true, margin: 0, color: C.text1, valign: "top" });
  s.addNotes(note("evidence", "Four numbers. The real SAP log gives the baseline: 9.3 days median, about twelve percent of it in steps a coordination tool can compress; simulation on that log gives five to eleven percent. The regulator study gives the supplier's view. The last number is ours and negative: at equal waste, the demand-recovery policy lost, which is why we stopped forecasting and chose the handoff. Say what is missing: planner interviews, frequency."));
};

// ================================================================ 4 promise
S.promise = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Judge the signal, check the reply, land the decision", { placeholder: "title" });
  box(s, M, 1.5, 12.1, 0.95, { fill: { color: C.text2 }, line: { color: H.dk2, width: 0 } });
  T(s, "A demand signal is judged on evidence, the supplier's reply is checked against it, and the result lands in procurement approval or a reasoned stop. Evidence and decisions stay attached to the task; every commitment is still approved by a human.", { x: M + 0.3, y: 1.58, w: 11.5, h: 0.8, fontSize: 15.5, italic: true, color: C.background1, valign: "middle" });
  // 1 · demand evidence gate
  box(s, M, 2.65, 12.1, 1.2, { fill: { color: C.background1 }, line: { color: H.accent1, width: 1.5 } });
  num(s, 1, M + 0.25, 2.85, 0.4);
  T(s, "Demand evidence gate", { x: M + 0.8, y: 2.78, w: 3.6, h: 0.35, fontSize: 16, bold: true, color: C.accent1 });
  T(s, "Judges whether the demand evidence supports pursuing additional supply. Never estimates unrecorded demand.", { x: M + 0.8, y: 3.13, w: 6.4, h: 0.65, fontSize: 12.5 });
  [["continue", C.accent1], ["clarify", C.accent2], ["pause", C.text1]].forEach(([t, col], i) => {
    rect(s, 8.0 + i * 1.5, 2.95, 1.35, 0.6, { fill: { color: col } });
    T(s, t, { x: 8.0 + i * 1.5, y: 2.95, w: 1.35, h: 0.6, fontSize: 13, bold: true, color: C.background1, align: "center", valign: "middle" });
  });
  T(s, "only continue opens investigation", { x: 8.0, y: 3.57, w: 4.4, h: 0.25, fontSize: 10.5, italic: true, color: C.accent4 });
  // 2 · reply checked, 3 · decision lands
  num(s, 2, M, 4.1, 0.4);
  T(s, "Supplier reply checked against the signal: read, revisions recognised, cited, rule-validated, authorised before disclosure", { x: M + 0.55, y: 4.08, w: 11.5, h: 0.45, fontSize: 13.5, bold: true, color: C.text2, valign: "middle" });
  num(s, 3, M, 4.7, 0.4);
  T(s, "The decision lands as one of three", { x: M + 0.55, y: 4.68, w: 11.5, h: 0.45, fontSize: 13.5, bold: true, color: C.text2, valign: "middle" });
  const d = [["CHANGE", "Request a change", "A change draft goes to existing procurement approval.", C.accent1], ["KEEP · STOP", "Keep the plan", "Reason recorded, plan untouched; routed for approval where policy requires.", C.text2], ["WAIT", "Wait, with an owner", "One question, a deadline, resumes on reply.", C.accent2]];
  d.forEach(([tag, h, b, col], i) => {
    const x = M + i * 4.1, y = 5.25, w = 3.9, hh = 1.3;
    box(s, x, y, w, hh);
    rect(s, x + 0.22, y + 0.18, 1.35, 0.3, { fill: { color: col } });
    T(s, tag, { x: x + 0.22, y: y + 0.18, w: 1.35, h: 0.3, fontSize: 10.5, bold: true, color: C.background1, align: "center", valign: "middle" });
    T(s, h, { x: x + 1.7, y: y + 0.15, w: w - 1.9, h: 0.36, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    T(s, b, { x: x + 0.22, y: y + 0.58, w: w - 0.44, h: 0.68, fontSize: 12 });
  });
  T(s, "Quantity boundary: only an approved request or an explicit rule over reconciled requests. Abundant supply never becomes demand.", { x: M, y: 6.68, w: 12.1, h: 0.32, fontSize: 11.5, color: C.accent4 });
  s.addNotes(note("promise", "Product solution, twenty percent. Three moves in order. One: the demand evidence gate gives a cited continue, clarify or pause on the retailer's own records; only a current continue opens investigation; it judges whether the evidence supports pursuing supply and never estimates unrecorded demand. Two: the supplier's reply is read, cited, rule-validated and authorised by the supplier before the planner sees it. Three: the decision lands as a change draft to procurement approval, a keep, or a wait with an owner. Dwell on WAIT. Quantity comes only from approved requests or an explicit rule."));
};

// ================================================================ 5 alternatives
S.alternatives = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Why this, not a form, a module, or the inbox", { placeholder: "title" });
  tagline(s, ["Desk", "Built"], "The honest competitor is a strong form with the same rules. The pilot includes it as an arm.");
  const yes = (t) => cell(t, { color: H.accent1, bold: true, align: "center" });
  const no = (t) => cell(t, { color: H.accent3, align: "center" });
  const part = (t) => cell(t, { color: H.accent2, align: "center" });
  const rows = [
    [hdr(""), hdr("Inbox + sheet"), hdr("Strong form + rules"), hdr("Incumbent modules"), hdr("Demand Pulse")],
    [cell("Reads a free-form reply", { bold: true }), no("human re-types"), no("not read"), part("partly"), yes("reads and cites")],
    [cell("Missing evidence", { bold: true }), no("forced to yes/no"), part("blank field"), part("varies"), yes("stays unknown · WAIT")],
    [cell("Authority separation", { bold: true }), no("none"), part("if designed"), part("inside their suite"), yes("enforced in code")],
    [cell("Handoff to approval", { bold: true }), no("typed note"), part("form output"), yes("native"), yes("version-linked request")],
    [cell("Cost to adopt", { bold: true }), cell("minutes", { align: "center" }), cell("low", { align: "center" }), cell("licence + integration", { align: "center" }), cell("< USD 1 per case + integration", { align: "center" })],
  ];
  s.addTable(rows, tableOpts(M, 2.0, 12.1, [2.6, 2.2, 2.3, 2.3, 2.7], { rowH: 0.55 }));
  box(s, M, 5.55, 12.1, 1.2, { fill: { color: C.background1 }, line: { color: H.accent5, width: 0.75 } });
  s.addText(bullets(["Priority: the loop and its guardrails before any forecasting, because the form is the real competitor", "Adoption: the retailer pays; the supplier keeps replying by email, no new portal", "Claim: less total work at equal correctness, not a lower price"], 12.5, 3), { x: M + 0.25, y: 5.68, w: 11.6, h: 1.0, isTextBox: true, margin: 0, color: C.text1, valign: "top" });
  s.addNotes(note("alternatives", "Improvement over alternatives, feature priority, adoption, value against cost. Read by rows. Incumbents: SAP Business Network Assistant, SourceDay, Microsoft Procurement Agent cover adjacent steps; four of our earlier differentiation claims were withdrawn after that check. Dwell on the form column: it may be enough, and the pilot will tell us before we scale."));
};

// ================================================================ 6 how
S.how = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("One loop, three kinds of authority", { placeholder: "title" });
  const steps = [["Demand signal arrives", "n"], ["Demand gate: continue · clarify · pause", "g"], ["Supplier reply arrives by email", "n"], ["Model reads and cites", "m"], ["Rules validate, model audits", "r"], ["Supplier authorises disclosure", "h"], ["Planner decides", "h"], ["Procurement receipt persisted", "n"]];
  const gap = 0.16, bw = (W - 2 * M - gap * (steps.length - 1)) / steps.length, y = 1.6;
  steps.forEach(([t, kind, tag], i) => {
    const x = M + i * (bw + gap);
    const fill = kind === "h" ? C.accent2 : kind === "m" ? C.text1 : kind === "r" || kind === "g" ? C.accent1 : C.background2;
    box(s, x, y, bw, 1.05, { fill: { color: fill }, line: kind === "g" ? { color: H.dk1, width: 1.5, dashType: "dash" } : tag ? { color: H.accent4, width: 1.25, dashType: "sysDash" } : undefined });
    T(s, t, { x: x + 0.06, y, w: bw - 0.12, h: 1.05, fontSize: kind === "g" ? 10.5 : 11.5, bold: true, align: "center", valign: "middle", color: kind === "n" ? C.text1 : C.background1 });
    if (tag) pill(s, tag, x + bw / 2 - 0.4, y + 1.1, 0.8, 0.24, 9);
    if (i < steps.length - 1) s.addShape(pres.ShapeType.rightArrow, { x: x + bw + 0.01, y: y + 0.41, w: 0.14, h: 0.23, fill: { color: C.accent4 }, line: { color: H.accent4, width: 0 } });
  });
  const bands = [
    ["Model may", C.text1, ["Read authorised sources", "Judge the demand evidence: continue, clarify, pause", "Cite, reconcile replies, name open conditions", "Draft one next action or a change draft"]],
    ["Rules enforce", C.accent1, ["Exact quotes from sources actually read", "Only a current continue opens investigation", "Unknown stays unknown; baseline retained", "Disclosure boundary, call cap, budget stop"]],
    ["Humans hold", C.accent2, ["Supplier: what is disclosed, and when", "Planner: investigate, stop, or submit a change", "Procurement approver: release or return", "Nothing is bought, booked or sent otherwise"]],
  ];
  bands.forEach(([h, col, items], i) => {
    const x = M + i * 4.1, by = 3.25, w = 3.9, hh = 2.85;
    box(s, x, by, w, hh);
    rect(s, x + 0.22, by + 0.2, 1.6, 0.34, { fill: { color: col } });
    T(s, h, { x: x + 0.22, y: by + 0.2, w: 1.6, h: 0.34, fontSize: 12, bold: true, color: C.background1, align: "center", valign: "middle" });
    s.addText(bullets(items, 12.5, 5), { x: x + 0.22, y: by + 0.72, w: w - 0.44, h: hh - 0.85, isTextBox: true, margin: 0, color: C.text1, valign: "top" });
  });
  T(s, "Dark reads, teal decides, amber authorises. Dashed: a model judgment that rules enforce. Email arrives through a simulated test intake, not a live mailbox; the receipt is a procurement sandbox record, not SAP. Gate and reply path were demonstrated in two retained tests, not one connected run.", { x: M, y: 6.3, w: 12.1, h: 0.5, fontSize: 11.5, color: C.accent4 });
  s.addNotes(note("how", "Prototype, twenty percent, with the demo. The loop starts with the demand signal and the gate, then the supplier reply. The answer to 'is it just AI': the model reads and drafts, a deterministic rule layer validates every output in the same handler production uses, humans hold every commercial authority. Point at the dashed gate. Be straight about the two ends: the email arrives through a simulated test intake behind the same validator a real mailbox would use, and the receipt lives in a procurement sandbox, not SAP. They ran in two retained real-model tests, which the video replays; one connected run on a single task is still to do."));
};

// ================================================================ 7 demo
S.demo = () => {
  // Embedded video: the three-minute "demand evidence to procurement decision" cut (v62), two retained real-model
  // tests replayed, nothing re-run for filming. The clip is 1280x1080, so it sits centred at full height on the dark master.
  const s = pres.addSlide({ masterName: "DARK" });
  const cover = "data:image/png;base64," + fs.readFileSync(VIDEO_COVER).toString("base64");
  const vh = 7.5, vw = vh * 1280 / 1080, vx = (13.333 - vw) / 2;
  // Side bars cover the master's footer and page number so nothing peeks out beside the clip.
  rect(s, 0, 0, vx, 7.5, { fill: { color: C.text1 } });
  rect(s, vx + vw, 0, 13.333 - vx - vw, 7.5, { fill: { color: C.text1 } });
  s.addMedia({ type: "video", path: VIDEO, cover, x: vx, y: 0, w: vw, h: vh });
  s.addNotes(note("demo", "Before pressing play, one sentence: 'The prototype demonstrates these stages in two retained tests; one connected task-level validation remains to be done.' Then click once; three minutes, own narration, natural speed. Six chapters: 0:00 demand evidence gate, retained test A: a stockout traced to a feed outage, the Agent pauses; a later physical stockout with unfulfilled requests, the Agent recommends continue, quantity unknown, the planner re-authorises investigation. 0:41 supplier response, separate retained test B: an earlier refusal explicitly withdrawn, the Agent cites the revision; receiving and QA still unconfirmed. 1:16 two targeted questions, prepared not sent; supplier authorises what is shared. 1:41 planner disposition: retain 360 cases, add 0, a recorded decision. 2:06 this disposition followed the demo's separate approval path; receipt SBX-PR-3C6BEEEE62CB, refreshed and read back; not every KEEP needs approval, routing follows the retailer's policy. 2:36 close: Agent interprets, people authorise. If sound fails, narrate the chapter titles over the picture."));
};

// ================================================================ 8 proven
S.proven = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("What is proven, and what is not", { placeholder: "title" });
  T(s, "Every claim in this deck rests on one of four kinds of evidence. This is the one slide that says which.", { x: M, y: 1.22, w: 12, h: 0.3, fontSize: 12.5, italic: true, color: C.accent4 });
  const tiers = [["Built", "tested, walked through", "business value"], ["Real-model", "real calls, failures kept", "a success rate"], ["Desk", "public sources", "our effect size"], ["Hypothesis", "targets, no measurement", "anything, until the pilot"]];
  tiers.forEach(([t, m, c], i) => {
    const x = M + i * 3.08;
    box(s, x, 1.55, 2.9, 1.25);
    pill(s, t, x + 0.2, 1.72, 1.25);
    T(s, m, { x: x + 1.55, y: 1.7, w: 1.3, h: 0.36, fontSize: 11, color: C.accent4, valign: "middle" });
    T(s, [{ text: "cannot show ", options: { bold: true, color: C.accent3 } }, { text: c, options: {} }], { x: x + 0.2, y: 2.2, w: 2.5, h: 0.5, fontSize: 11.5 });
  });
  const tc = (t) => ({ text: t, options: { bold: true, fontSize: 11, color: t === "Desk" ? H.dk1 : H.lt1, fill: { color: t === "Built" ? H.accent1 : t === "Real-model" ? H.dk1 : t === "In progress" ? H.accent4 : H.accent2 }, align: "center", valign: "middle" } });
  const rows = [
    [hdr("What exists"), hdr("Status"), hdr("Does not prove")],
    [cell("Deployed workspace for planner and supplier; retained real-model records", { bold: true }), tc("Built"), cell("Any order, SAP write, labour saving")],
    [cell("Demand gate: pause → continue on new evidence (test A, 18 real calls, failures kept); reply → receipt (test B, one run)", { bold: true }), tc("Real-model"), cell("One connected run; a success rate; a live mailbox")],
    [cell("Real-model tests on three synthetic items, with a correction loop", { bold: true }), tc("Real-model"), cell("A success rate; behaviour on real documents")],
    [cell("S/4HANA-shaped procurement sandbox, 41 tests", { bold: true }), tc("Built"), cell("SAP write semantics; it is not SAP")],
    [cell("Ten frozen acceptance tasks, inbound contract, simulator, scorer", { bold: true }), tc("Built"), cell("Independence: authored on the development side")],
  ];
  s.addTable(rows, tableOpts(M, 3.05, 12.1, [6.2, 1.5, 4.4], { rowH: 0.56 }));
  s.addNotes(note("proven", "Fifteen seconds, point only. Four labels used on every slide, each with what it cannot establish. The table says what each artefact does not prove; the in-progress reply flow is deliberately not used as evidence."));
};

// ================================================================ 9 wrong
S.wrong = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Three times the model was wrong, and what caught it", { placeholder: "title" });
  tagline(s, ["Real-model"], "Kept on purpose. The rule layer exists for exactly these.");
  const cases = [
    ["It overstated the blocker", "\"The carrier failure is the sole blocker\" while receiving and capacity were unknown. The model auditor agreed.", "A human reading the prose against the typed states", "Summary-versus-state contradiction tests; component not released"],
    ["It hid a quantity in the prose", "Withheld the structured quantity, kept \"80 cases / CAD 770\" in the text, on unconfirmed demand.", "Semantic inspection; then a rule audit blocked it", "Quantity consistency across summary, evidence, recommendation; corrected in two linked calls"],
    ["It mixed up two timestamps", "DC arrival 08:00Z read as store usable 12:00Z; 250 excluded cases where the figure was 200.", "Review of the retained output", "Typed timing claims tied to source fields; corrected in three calls, original kept"],
  ];
  cases.forEach(([h, said, caught, changed], i) => {
    const x = M + i * 4.1, y = 2.0, w = 3.9, hh = 3.75;
    box(s, x, y, w, hh);
    T(s, h, { x: x + 0.22, y: y + 0.18, w: w - 0.44, h: 0.4, fontSize: 15, bold: true, color: C.text2 });
    [["Said", said, C.accent3], ["Caught by", caught, C.text2], ["Changed", changed, C.accent1]].forEach(([k, v, col], j) => {
      const yy = y + 0.7 + j * 1.0;
      T(s, k.toUpperCase(), { x: x + 0.22, y: yy, w: 1.2, h: 0.25, fontSize: 9.5, bold: true, color: col });
      T(s, v, { x: x + 0.22, y: yy + 0.25, w: w - 0.44, h: 0.72, fontSize: 11.5 });
    });
  });
  box(s, M, 5.95, 12.1, 0.85, { fill: { color: C.background1 }, line: { color: H.accent3, width: 1.25 } });
  T(s, [{ text: "Pattern:  ", options: { bold: true, color: C.accent3 } }, { text: "structure passes, prose fails. The answer is a rule for the failure class, the failure kept on the timeline, a linked correction that never overwrites. The audit is a review, not proof.", options: {} }], { x: M + 0.3, y: 6.05, w: 11.5, h: 0.65, fontSize: 12.5, valign: "middle" });
  s.addNotes(note("wrong", "Stakeholder alignment: acknowledge limitations before they are raised. Three real failures from our runs, what caught each, and the rule that now exists because of it. This is why the correction loop and preserved records matter more than any single good answer."));
};

// ================================================================ 10 finance
S.finance = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Model cost is measured; the business case is not yet", { placeholder: "title" });
  tagline(s, ["Real-model", "Hypothesis"], "Three measured numbers, one hypothesis, never blended.");
  s.addChart(pres.ChartType.bar, [
    { name: "Initial review", labels: ["Item A", "Item B", "Item C"], values: [0.475, 0.359, 0.277] },
    { name: "Correction", labels: ["Item A", "Item B", "Item C"], values: [0.085, 0, 0.063] },
  ], { x: M, y: 2.0, w: 6.0, h: 3.4, barDir: "col", barGrouping: "stacked", chartColors: [H.accent1, H.accent2], showTitle: true, title: "Model cost per exception, USD (real calls, synthetic items)", titleFontSize: 12, titleColor: H.dk1, titleFontFace: "+mn-lt", showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: "$0.000;;", dataLabelFontSize: 10, dataLabelColor: H.lt1, dataLabelFontFace: "+mn-lt", showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: "+mn-lt", legendColor: H.dk1, catAxisLabelFontSize: 10, catAxisLabelColor: H.dk1, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontSize: 10, valAxisLabelColor: H.accent4, valAxisLabelFontFace: "+mn-lt", valAxisLabelFormatCode: "$0.00", valGridLine: { color: H.accent5, size: 0.5 }, catGridLine: { style: "none" }, valAxisMaxVal: 0.6 });
  stat(s, 6.95, 2.0, 5.75, 1.6, "< USD 1", "per exception including one correction round", C.text2);
  stat(s, 6.95, 3.8, 2.8, 1.6, "3.03 / 4", "USD cloud ledger; project cap 20", C.text2);
  stat(s, 9.9, 3.8, 2.8, 1.6, "1 of 3", "items failed, caught, repaired", C.accent3);
  box(s, M, 5.65, 12.1, 1.15, { fill: { color: C.background1 }, line: { color: H.accent2, width: 1.25 } });
  T(s, [{ text: "Unmeasured, and what the pilot measures:  ", options: { bold: true, color: C.accent2 } }, { text: "active minutes saved on both sides, critical errors avoided versus introduced, one-time integration cost. At CAD 45 per hour, one planner minute covers the model cost; integration is the number that matters. Simulated demand-recovery gains were withdrawn.", options: {} }], { x: M + 0.3, y: 5.75, w: 11.5, h: 0.95, fontSize: 12.5, valign: "middle" });
  s.addNotes(note("finance", "Value against cost. Model cost measured on real calls: under one dollar per exception. The cloud ledger and the project cap. One of three items failed semantic review and was repaired. Everything on the savings side is a hypothesis the pilot measures; pilot model spend for ten to twenty exceptions across three arms is under fifty dollars."));
};

// ================================================================ 11 stakeholders
S.stakeholders = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Four stakeholders, four trade-offs, one roadmap of gates", { placeholder: "title" });
  const rows = [
    [hdr("Stakeholder"), hdr("Needs"), hdr("We chose"), hdr("We gave up")],
    [cell("Software development", { bold: true }), cell("Reliability; no model with write rights"), cell("Rules in the write path; failures retained; sandbox contract"), cell("Feature speed; the loop has run end to end once")],
    [cell("Marketing", { bold: true }), cell("A differentiated story"), cell("One claim, one buyer; four claims withdrawn"), cell("The \"network\" narrative as scope; any price advantage")],
    [cell("Finance", { bold: true }), cell("A return"), cell("Measured cost; pre-set targets; kill rules"), cell("Any savings number today")],
    [cell("Product strategy", { bold: true }), cell("A scalable wedge"), cell("The demand-to-decision loop, four gates"), cell("Forecasting, transfers, autonomous buying")],
  ];
  s.addTable(rows, tableOpts(M, 1.55, 12.1, [2.2, 2.9, 3.9, 3.1], { rowH: [0.42, 0.72, 0.65, 0.65, 0.65] }));
  const gates = [["0 · now", "workspace deployed; sandbox and acceptance kit built"], ["1 · pilot", "10 frozen tasks; then 3 arms on 10–20 real exceptions"], ["2 · SAP read", "a real tenant; planner and supplier identities"], ["3 · SAP write", "change request into existing approval"]];
  gates.forEach(([h, b], i) => {
    const x = M + i * 3.08;
    box(s, x, 5.0, 2.9, 1.05);
    T(s, h, { x: x + 0.2, y: 5.1, w: 2.5, h: 0.32, fontSize: 13, bold: true, color: C.text2 });
    T(s, b, { x: x + 0.2, y: 5.42, w: 2.6, h: 0.6, fontSize: 11.5, color: C.accent4 });
    if (i < 3) s.addShape(pres.ShapeType.rightArrow, { x: x + 2.92, y: 5.4, w: 0.14, h: 0.24, fill: { color: C.accent4 }, line: { color: H.accent4, width: 0 } });
  });
  T(s, "Where they still conflict: marketing wants a bigger claim than finance will fund and engineering will stand behind. Each gate is one function's condition; no gate is skipped. If a strong form matches the Agent, we ship the form.", { x: M, y: 6.2, w: 12.1, h: 0.6, fontSize: 12, color: C.text1 });
  s.addNotes(note("stakeholders", "Stakeholder alignment, twenty percent. One row per function: what they need, what we chose, what we gave up, how firm the evidence is. Then the gates: each is one function's condition. Limitations we own: no measured value, a sandbox that is not SAP, acceptance tasks authored on the development side, model prose that can pass checks and still be wrong."));
};

// ================================================================ 12 plan
S.plan = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Twelve days to an engineering result, then a pilot", { placeholder: "title" });
  tagline(s, ["Hypothesis"], "Resources, dependencies, milestones, success criteria and stop rules, stated before run one.");
  card(s, M, 2.0, 3.9, 3.5, "Milestones", ["Days 1–3: a real mailbox behind the same intake validator; call budget for ten runs", "Days 4–7: one connected run of gate → reply → receipt on the same task; then ten frozen tasks scored against sandbox records; freeze", "Days 8–12: repair, re-run, engineering report", "Then: 3-arm pilot on 10–20 real exceptions"], { bodySize: 12 });
  card(s, M + 4.1, 2.0, 3.9, 3.5, "Resources and dependencies", ["Two builders, two model lanes, no hires", "A case mailbox, or the simulator until then", "A reachable sandbox host", "One partner with real exceptions", "An SAP tenant owner for phase 2", "Cap USD 20; pilot model spend < USD 50"], { bodySize: 12 });
  card(s, M + 8.2, 2.0, 3.9, 3.5, "Success criteria and stop rules", ["Engineering: 10 of 10 tasks end to end, zero critical errors", "Business: −30% active time vs manual; −15% vs strong form; no burden shifted to the supplier", "Stop: forms match → ship the form; critical error → suspend auto-submit; transport dominates → no arrival promise"], { bodySize: 12 });
  box(s, M, 5.75, 12.1, 0.75, { fill: { color: C.background1 }, line: { color: H.accent3, width: 1.25 } });
  T(s, [{ text: "Top risks:  ", options: { bold: true, color: C.accent3 } }, { text: "no partner appears; the sandbox is mistaken for SAP; the ten tasks are read as a blinded test when they are not.", options: {} }], { x: M + 0.3, y: 5.75, w: 11.5, h: 0.75, fontSize: 12.5, valign: "middle" });
  s.addNotes(note("plan", "Implementation plan, ten percent. The twelve days produce an engineering report, never a business number. Business validation starts only when a partner provides real tasks. Measurable criteria are pre-set and frozen; the stop rules are the losing conditions in short form."));
};

// ================================================================ 13 vision
S.vision = () => {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("From one exception to the response layer on SAP", { placeholder: "title" });
  tagline(s, [], "Vision is context, not scope. Each horizon opens only when the one before it passes its gate.");
  const horizons = [
    ["Now · the pilot", "One exception type, one retailer and supplier, one case", ["Demand gate, supplier reply check, procurement handoff", "Email in, sandbox out", "Ten frozen tasks, then 10–20 real exceptions"], C.background2, C.text2],
    ["Next · every plan change", "All replenishment exceptions on a live SAP landscape", ["Promotion, stockout, short ship, recall, date move: one loop", "S/4HANA read, then write into existing approval", "Supplier replies through SAP Business Network", "A decision log on every exception; time-to-decision becomes a KPI"], C.background2, C.text2],
    ["Later · the Retail Response Network", "Suppliers answer once; evidence flows with consent", ["A supplier's checked reply reaches every retailer it serves", "The demand gate becomes a shared signal between retailer and supplier", "Joule as the surface; the rule layer as the contract", "Procurement, logistics and QA see the same evidence"], C.text2, C.background1],
  ];
  horizons.forEach(([h, sub, items, fill, fg], i) => {
    const x = M + i * 4.1, y = 2.0, w = 3.9, hh = 4.0;
    box(s, x, y, w, hh, { fill: { color: fill }, line: { color: i === 2 ? H.dk2 : H.accent5, width: 0.75 } });
    num(s, i + 1, x + 0.22, y + 0.22, 0.4, i === 2 ? C.accent6 : C.accent1);
    T(s, h, { x: x + 0.75, y: y + 0.18, w: w - 0.95, h: 0.48, fontSize: 16, bold: true, color: i === 2 ? C.accent6 : C.text2, valign: "middle" });
    T(s, sub, { x: x + 0.22, y: y + 0.78, w: w - 0.44, h: 0.5, fontSize: 12, italic: true, color: i === 2 ? C.background1 : C.accent4 });
    s.addText(bullets(items, 12, 4), { x: x + 0.22, y: y + 1.35, w: w - 0.44, h: hh - 1.5, isTextBox: true, margin: 0, color: fg, valign: "top" });
    if (i < 2) s.addShape(pres.ShapeType.rightArrow, { x: x + w + 0.02, y: y + 1.85, w: 0.16, h: 0.3, fill: { color: C.accent4 }, line: { color: H.accent4, width: 0 } });
  });
  T(s, "SAP integrations are proposed for discussion with SAP architects, not agreed. Gates: pilot result → tenant owner validates the read boundary → approval owner accepts the write.", { x: M, y: 6.2, w: 12.1, h: 0.5, fontSize: 11.5, color: C.accent4 });
  s.addNotes(note("vision", "Twenty seconds. Today is a pilot of one loop. If it passes, the same loop covers every plan-change exception on a real SAP landscape, with replies through Business Network and a decision log that makes time-to-decision a KPI. The long view is the Retail Response Network: a supplier answers once and the checked evidence reaches every retailer it serves, with consent, through Joule. Say clearly: vision is context, not scope, and nothing here is agreed with SAP."));
};

// ================================================================ 14 recommendation
S.asks = () => {
  const s = pres.addSlide({ masterName: "DARK" });
  T(s, "RECOMMENDATION", { x: M, y: 0.6, w: 6, h: 0.3, fontSize: 12, bold: true, color: C.accent6, charSpacing: 3 });
  T(s, "Run a focused pilot before any commercialisation", { x: M, y: 0.95, w: 12, h: 1.0, fontSize: 36, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "middle" });
  const cols = [
    ["1", "Finish the loop", "Twelve days: email intake, procurement write, ten frozen tasks scored against sandbox records. An engineering report, not a business number."],
    ["2", "Measure it on real work", "One partner, 10–20 consecutive exceptions, three arms: today's process, a strong form with our rules, the Agent. Minutes, errors, handoff rate."],
    ["3", "Decide with the stop rules", "If the form matches, ship the form. If critical errors rise, suspend auto-submit. Only then SAP read, then SAP write."],
  ];
  cols.forEach(([n, h, b], i) => {
    const x = M + i * 4.1, y = 2.35, w = 3.9, hh = 2.5;
    box(s, x, y, w, hh, { fill: { color: C.text2 }, line: { color: H.dk2, width: 0 } });
    num(s, n, x + 0.25, y + 0.25, 0.42, C.accent6);
    T(s, h, { x: x + 0.8, y: y + 0.22, w: w - 1.0, h: 0.5, fontSize: 17, bold: true, color: C.background1, valign: "middle" });
    T(s, b, { x: x + 0.25, y: y + 0.95, w: w - 0.5, h: 1.45, fontSize: 13, color: C.background1 });
  });
  T(s, "We proved the loop runs, stays inside its authority, and repairs its own errors. We have not proved it is worth buying. The pilot answers that, and we have written down what losing looks like.", { x: M, y: 5.35, w: 12.1, h: 0.9, fontSize: 16, italic: true, color: C.accent6 });
  s.addNotes(note("asks", "Close on a recommendation, not on requests the panel cannot grant. Three steps, each with its own gate. Then the three sentences on the slide, slowly."));
};

// ================================================================ build
const order = ["title", "problem", "evidence", "promise", "alternatives", "how", "demo", "proven", "wrong", "finance", "stakeholders", "plan", "vision", "asks"];
pres.addSection({ title: "Demand Pulse business case" });
order.forEach((k) => S[k]());
(async () => { await pres.writeFile({ fileName: OUT }); await applyTheme(OUT, THEME); console.log(`wrote ${OUT} (${order.length} slides)`); })().catch((e) => { console.error(e); process.exit(1); });
