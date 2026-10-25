"""Freeze the acceptance tasks before the first run.

    python -m procurement_sandbox.acceptance.freeze            # writes freeze.json next to tasks.json
    python -m procurement_sandbox.acceptance.freeze --check    # verifies tasks.json still matches freeze.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE / "tasks.json"
FREEZE = HERE / "freeze.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute(tasks_path: Path = TASKS) -> dict:
    raw = tasks_path.read_bytes()
    doc = json.loads(raw)
    per_task = {t["id"]: sha256_bytes(json.dumps(t, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")) for t in doc["tasks"]}
    return {
        "kit": doc.get("kit"), "version": doc.get("version"),
        "tasks_file": tasks_path.name, "tasks_sha256": sha256_bytes(raw), "task_count": len(doc["tasks"]),
        "per_task_sha256": per_task,
        "frozen_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "statement": "Frozen before the first acceptance run. Engineering acceptance only: no time-saving or business-value conclusion may be drawn from these tasks.",
    }


def check(tasks_path: Path = TASKS, freeze_path: Path = FREEZE) -> tuple[bool, str]:
    if not freeze_path.exists():
        return False, f"{freeze_path.name} does not exist; run freeze first"
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    current = compute(tasks_path)
    if frozen["tasks_sha256"] != current["tasks_sha256"]:
        changed = [k for k, v in current["per_task_sha256"].items() if frozen["per_task_sha256"].get(k) != v]
        return False, f"tasks.json changed after freezing (frozen {frozen['frozen_at']}); changed tasks: {changed or 'file-level only'}"
    return True, f"tasks.json matches freeze.json (frozen {frozen['frozen_at']}, {frozen['task_count']} tasks)"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Freeze or verify the acceptance tasks")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--tasks", type=Path, default=TASKS)
    ap.add_argument("--out", type=Path, default=FREEZE)
    args = ap.parse_args(argv)
    if args.check:
        ok, msg = check(args.tasks, args.out)
        print(msg)
        return 0 if ok else 1
    if args.out.exists():
        ok, msg = check(args.tasks, args.out)
        if ok:
            print("already frozen; " + msg)
            return 0
        print("refusing to overwrite an existing freeze that no longer matches; delete it deliberately if the tasks were revised before any run: " + msg)
        return 2
    args.out.write_text(json.dumps(compute(args.tasks), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"frozen {args.tasks.name} -> {args.out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
