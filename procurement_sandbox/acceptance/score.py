"""Score engineering-acceptance runs against the frozen tasks and the sandbox.

    python -m procurement_sandbox.acceptance.score --exports <dir> --base http://127.0.0.1:8081 [--out report.md]

<dir> holds one case_export.json per task, named T01.json ... T10.json (README section 3).
The scorer reads the application's export AND the sandbox's own records; a claim in the
export that the sandbox does not confirm is a failure. Output is engineering completion
and error counts only. It never produces a time-saving or business-value conclusion.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from ..client import ProcurementClient
from .freeze import FREEZE, TASKS, check

TIMESTAMP_ORDER = ["received_at", "review_started", "review_accepted", "disclosure_authorized", "change_submitted", "change_approved", "closed"]


@dataclass
class TaskResult:
    task_id: str
    title: str
    passed: bool
    checks: list[tuple[str, bool, str]] = field(default_factory=list)
    critical: list[str] = field(default_factory=list)
    synthetic_components: list[str] = field(default_factory=list)

    def add(self, name: str, ok: bool, note: str = "", critical: bool = False) -> None:
        self.checks.append((name, ok, note))
        if not ok:
            self.passed = False
            if critical:
                self.critical.append(f"{name}: {note}")


def _parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _qty(value) -> str | None:
    if value in (None, ""):
        return None
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)


def score_task(task: dict, export: dict | None, client: ProcurementClient) -> TaskResult:
    exp = task["expected"]
    res = TaskResult(task["id"], task["title"], passed=True)
    if export is None:
        res.add("export_present", False, "no case_export.json for this task", critical=False)
        return res
    res.synthetic_components = list(export.get("synthetic_components", [])) or ["business facts in the email (declared by the kit)"]

    # ---- intake
    inbound = export.get("inbound", [])
    res.add("inbound_recorded", len(inbound) >= 1, f"{len(inbound)} inbound message(s) recorded")
    matched = export.get("matched_case")
    res.add("matched_case", matched == exp["matched_case"], f"export {matched!r}, expected {exp['matched_case']!r}", critical=exp["matched_case"] is None and matched is not None)
    asked = bool(export.get("ambiguity_confirmation_requested", False))
    res.add("ambiguity_confirmation", asked == exp["ambiguity_confirmation_requested"], f"export {asked}, expected {exp['ambiguity_confirmation_requested']}", critical=exp["ambiguity_confirmation_requested"] and not asked)
    dup = bool(export.get("duplicate_detected", False))
    res.add("duplicate_detected", dup == exp["duplicate_detected"], f"export {dup}, expected {exp['duplicate_detected']}")
    reviews = export.get("reviews", [])
    if "max_reviews" in exp:
        res.add("review_count", len(reviews) <= exp["max_reviews"], f"{len(reviews)} review(s), max {exp['max_reviews']}")
    if exp["matched_case"] is None:
        res.add("no_paid_review_before_confirmation", not any(r.get("model_calls", 0) > 0 for r in reviews), f"{sum(r.get('model_calls', 0) for r in reviews)} model call(s) before a confirmed match", critical=True)
    for r in reviews:
        if r.get("outcome") == "accepted":
            res.add("source_read_before_acceptance", bool(r.get("sources_read")), f"review {r.get('id')} sources_read={r.get('sources_read')}")

    # ---- disposition
    disp = (export.get("disposition") or {})
    kind = disp.get("kind")
    if "disposition_in" in exp:
        res.add("disposition", kind in exp["disposition_in"], f"export {kind!r}, expected one of {exp['disposition_in']}", critical=True)
    else:
        res.add("disposition", kind == exp["disposition"], f"export {kind!r}, expected {exp['disposition']!r}", critical=exp["disposition"] in (None, "WAIT", "KEEP") and kind == "CHANGE")
    if "wait_requires" in exp:
        wait = disp.get("wait") or {}
        missing = [k for k in exp["wait_requires"] if not wait.get(k)]
        res.add("wait_is_resumable", not missing, f"missing {missing}" if missing else "owner, deadline and question present")
    forbidden = {f"{float(q):.3f}" for q in exp.get("forbidden_quantities", [])}
    disp_qty = _qty(disp.get("quantity"))
    if disp_qty is not None:
        res.add("disposition_quantity_not_forbidden", disp_qty not in forbidden, f"disposition quantity {disp_qty}", critical=True)

    # ---- submission (export view)
    sub = export.get("submission") or {}
    attempts = sub.get("attempts") or []
    states = [a.get("state") for a in attempts]
    final_state = sub.get("state") or (states[-1] if states else None)
    res.add("submission_state", final_state == exp["submission_state"], f"export {final_state!r}, expected {exp['submission_state']!r}")
    if "first_submission_state" in exp:
        res.add("first_submission_state", (states[0] if states else None) == exp["first_submission_state"], f"first {states[0] if states else None!r}")
    if "submission_attempts_min" in exp:
        res.add("submission_attempts", len(attempts) >= exp["submission_attempts_min"], f"{len(attempts)} attempt(s)")
        keys = {a.get("idempotency_key") for a in attempts}
        res.add("same_idempotency_key_on_retry", len(keys) == 1, f"keys used: {sorted(k or 'none' for k in keys)}", critical=True)
    if exp["submission_state"] is None:
        res.add("no_submission_attempted", not attempts, f"{len(attempts)} attempt(s) although none expected", critical=True)
    completed_shown = export.get("ui_states_shown", [])
    if any(s in ("submission_failed_outcome_unknown", "baseline_changed_re_review_required") for s in states):
        res.add("never_showed_completed_on_failure", "change_completed" not in completed_shown, f"ui states shown: {completed_shown}", critical=True)

    # ---- sandbox truth
    prs = client.list_purchase_requisitions(task["case_id"])
    res.add("pr_created", bool(prs) == exp["pr_created"], f"sandbox has {len(prs)} PR(s) for {task['case_id']}", critical=(not exp["pr_created"]) and bool(prs))
    if exp.get("pr_count") is not None:
        res.add("pr_count", len(prs) == exp["pr_count"], f"{len(prs)} vs {exp['pr_count']}", critical=len(prs) > exp["pr_count"])
    if prs:
        pr = prs[-1]
        item = pr["items"][0] if pr["items"] else {}
        if exp.get("pr_quantity"):
            res.add("pr_quantity", item.get("quantity") == exp["pr_quantity"], f"{item.get('quantity')} vs {exp['pr_quantity']}", critical=True)
        if exp.get("pr_unit"):
            res.add("pr_unit", item.get("unit") == exp["pr_unit"], f"{item.get('unit')} vs {exp['pr_unit']}", critical=True)
        if exp.get("pr_delivery_date"):
            res.add("pr_delivery_date", (item.get("delivery_date") or "").startswith(exp["pr_delivery_date"]), f"{item.get('delivery_date')}")
        res.add("pr_quantity_not_forbidden", _qty(item.get("quantity")) not in forbidden, f"PR quantity {item.get('quantity')}", critical=True)
        if exp.get("release_status"):
            res.add("release_status", pr["release_status"] == exp["release_status"], f"{pr['release_status']} vs {exp['release_status']}")
        if exp.get("rejection_reason_contains"):
            res.add("rejection_reason", exp["rejection_reason_contains"] in (pr.get("rejection_reason") or ""), f"{pr.get('rejection_reason')!r}")
        res.add("pr_links_evidence_version", bool(item.get("evidence_version")), f"evidence_version={item.get('evidence_version')}")
        claimed = sub.get("purchase_requisition")
        if claimed:
            res.add("export_pr_matches_sandbox", claimed in {p["purchase_requisition"] for p in prs}, f"export claims {claimed}", critical=True)
        for unk in exp.get("open_unknowns_mentions", []):
            res.add("open_unknowns_mentions", unk.lower() in (item.get("open_unknowns") or "").lower(), f"looking for {unk!r} in {item.get('open_unknowns')!r}")

    # ---- approval and closure
    appr = (export.get("approval") or {}).get("state")
    res.add("approval_state", appr == exp["approval_state"], f"export {appr!r}, expected {exp['approval_state']!r}")
    if exp["approval_state"] == "approved":
        res.add("approved_by_procurement_role", (export.get("approval") or {}).get("by_role") == "procurement_approver", f"by_role={(export.get('approval') or {}).get('by_role')}", critical=True)
    closed = export.get("closed_at") is not None
    if "closed_in" in exp:
        res.add("closed", closed in exp["closed_in"], f"closed={closed}")
    else:
        res.add("closed", closed == exp["closed"], f"closed={closed}, expected {exp['closed']}")

    # ---- timestamps are computed, not typed, and monotonic
    ts = export.get("timestamps") or {}
    present = [(k, _parse_ts(ts.get(k))) for k in TIMESTAMP_ORDER if ts.get(k)]
    monotonic = all(present[i][1] <= present[i + 1][1] for i in range(len(present) - 1)) if all(p[1] for p in present) else False
    res.add("timestamps_present", bool(ts.get("received_at")), f"{len(present)} transition timestamp(s)")
    res.add("timestamps_monotonic", monotonic or len(present) < 2, "in order" if monotonic else f"out of order: {[k for k, _ in present]}")
    actions = export.get("human_actions", [])
    res.add("active_time_recorded", all(isinstance(a.get("active_seconds"), (int, float)) for a in actions) and (bool(actions) or exp["submission_state"] is None),
            f"{len(actions)} human action(s) with active_seconds")
    return res


def score_all(tasks_doc: dict, exports_dir: Path, client: ProcurementClient) -> list[TaskResult]:
    out = []
    for task in tasks_doc["tasks"]:
        path = exports_dir / f"{task['id']}.json"
        export = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        out.append(score_task(task, export, client))
    return out


def render(results: list[TaskResult], freeze_msg: str, sandbox_label: str | None) -> str:
    passed = sum(r.passed for r in results)
    critical = sum(len(r.critical) for r in results)
    lines = [
        "# Engineering acceptance report",
        "",
        f"_{freeze_msg}_",
        "",
        f"**Scope.** Engineering completion of the chain email → match → review → disposition → approval → procurement sandbox receipt. "
        f"Procurement target: **{sandbox_label or 'unknown'}**. Business facts are synthetic; only mail receipt is a real connection. "
        "This report states no time saving and no business value.",
        "",
        f"**Result.** {passed}/{len(results)} tasks passed. {critical} critical error(s).",
        "",
        "| Task | Title | Result | Critical | Failed checks |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        failed = [f"{n} ({note})" for n, ok, note in r.checks if not ok]
        lines.append(f"| {r.task_id} | {r.title} | {'PASS' if r.passed else 'FAIL'} | {len(r.critical)} | {'; '.join(failed) or '—'} |")
    lines += ["", "## Unconnected or synthetic components, per task", ""]
    for r in results:
        lines.append(f"- **{r.task_id}**: {', '.join(r.synthetic_components) or 'none declared'}")
    lines += ["", "## Every check", ""]
    for r in results:
        lines.append(f"### {r.task_id} — {r.title}")
        for n, ok, note in r.checks:
            lines.append(f"- {'✔' if ok else '✘'} {n}: {note}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Score acceptance runs")
    ap.add_argument("--exports", type=Path, required=True)
    ap.add_argument("--base", default="http://127.0.0.1:8081")
    ap.add_argument("--tasks", type=Path, default=TASKS)
    ap.add_argument("--freeze", type=Path, default=FREEZE)
    ap.add_argument("--allow-unfrozen", action="store_true")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    ok, msg = check(args.tasks, args.freeze)
    if not ok and not args.allow_unfrozen:
        print("refusing to score: " + msg)
        return 2
    client = ProcurementClient(args.base, role="planner")
    label = None
    try:
        label = client.read_purchase_order("4500001042").get("sandbox_label")
    except Exception as exc:  # noqa: BLE001
        print(f"warning: could not read the sandbox label: {exc}")
    results = score_all(json.loads(args.tasks.read_text(encoding="utf-8")), args.exports, client)
    report = render(results, msg if ok else "UNFROZEN TASKS: " + msg, label)
    if args.out:
        args.out.write_text(report, encoding="utf-8")
        print(f"wrote {args.out}")
    print(report.split("\n\n")[3])
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
