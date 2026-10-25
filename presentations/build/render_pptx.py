"""Render every slide of a .pptx to PNG with the locally installed PowerPoint (COM automation).

    python render_pptx.py deck.pptx out_dir [width_px]

Used for visual QA on this Windows machine, which has PowerPoint but no LibreOffice.
"""

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    deck = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1600
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.PNG"):
        old.unlink()
    import win32com.client  # pywin32, present in the project venv

    app = win32com.client.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(str(deck), ReadOnly=True, Untitled=False, WithWindow=False)
    try:
        height = int(round(width * pres.PageSetup.SlideHeight / pres.PageSetup.SlideWidth))
        pres.Export(str(out), "PNG", width, height)
        count = pres.Slides.Count
    finally:
        pres.Close()
        app.Quit()
    files = sorted(out.glob("*.PNG"), key=lambda p: int("".join(ch for ch in p.stem if ch.isdigit()) or 0))
    for f in files:
        print(f)
    print(f"{count} slide(s) rendered to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
