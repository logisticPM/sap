"""Crop the demo storyboard frames from retained screenshots in the full project folder.

    python crop_demo_frames.py

Writes assets/frame_*.png next to this script. Source screenshots are real UI captures of the
deployed workbench on synthetic business data; crops are by fraction of width and height.
"""

from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
DELIV = HERE.parents[2] / "deliverable"  # sap/deliverable

FRAMES = {
    # name: (source, (left, top, right, bottom) as fractions)
    "frame_1_supplier_reply": (DELIV / "competition_v51/supplier-live.png", (0.03, 0.40, 0.97, 0.66)),
    "frame_2_agent_reads": (DELIV / "competition_v31_activity_20261024/active-execution.png", (0.01, 0.21, 0.99, 0.57)),
    "frame_3_planner_card": (DELIV / "competition_v50/planner-task.png", (0.08, 0.31, 0.92, 0.60)),
    "frame_4_procurement_review": (DELIV / "competition_v50/planner-task.png", (0.08, 0.735, 0.92, 0.905)),
    "frame_5_planner_decision": (DELIV / "competition_v34_20261024/planner-demand-decision.png", (0.18, 0.02, 1.0, 1.0)),
}


def main() -> int:
    ASSETS.mkdir(exist_ok=True)
    for name, (src, (l, t, r, b)) in FRAMES.items():
        if not src.exists():
            print(f"missing source: {src}")
            return 1
        im = Image.open(src).convert("RGB")
        w, h = im.size
        crop = im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
        if crop.width > 1400:
            crop = crop.resize((1400, int(crop.height * 1400 / crop.width)), Image.LANCZOS)
        out = ASSETS / f"{name}.png"
        crop.save(out, optimize=True)
        print(f"{out.name}: {crop.width}x{crop.height} from {src.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
