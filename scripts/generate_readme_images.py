"""Render docs/sample_output.txt (or fresh demo output) as terminal-style PNGs for the README."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
IMAGES = DOCS / "images"
SAMPLE = DOCS / "sample_output.txt"


def _load_font(size: int):
    from PIL import ImageFont

    candidates = [
        "/System/Library/Fonts/Supplemental/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "C:\\Windows\\Fonts\\consola.ttf",
    ]
    for path in candidates:
        p = Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size, index=0)
            except OSError:
                continue
    return ImageFont.load_default()


def _wrap_line(line: str, max_chars: int) -> list[str]:
    if max_chars <= 0 or len(line) <= max_chars:
        return [line]
    parts: list[str] = []
    rest = line
    while len(rest) > max_chars:
        split_at = rest.rfind(" ", 0, max_chars)
        if split_at <= 0:
            split_at = max_chars
        parts.append(rest[:split_at].rstrip())
        rest = rest[split_at:].lstrip()
    if rest:
        parts.append(rest)
    return parts


def render_terminal_png(lines: list[str], out_path: Path, *, title: str) -> None:
    from PIL import Image, ImageDraw

    bg = (30, 30, 30)
    fg = (220, 245, 220)
    accent = (180, 200, 255)
    margin = 20
    font_size = 13
    line_gap = 4
    max_chars = 118

    font = _load_font(font_size)
    draw_tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    wrapped: list[tuple[str, bool]] = []
    wrapped.append((f"$ python demo.py --n 2000 --repeats 2", True))
    wrapped.append(("", False))
    for raw in lines:
        for seg in _wrap_line(raw, max_chars):
            wrapped.append((seg, False))

    line_heights: list[int] = []
    max_width = 400
    for text, is_title in wrapped:
        if not text and not is_title:
            bbox = draw_tmp.textbbox((0, 0), " ", font=font)
            line_heights.append(bbox[3] - bbox[1] + line_gap)
            continue
        fill = accent if is_title else fg
        bbox = draw_tmp.textbbox((0, 0), text or " ", font=font)
        h = bbox[3] - bbox[1] + line_gap
        line_heights.append(h)
        w = bbox[2] - bbox[0] + 2 * margin
        max_width = max(max_width, w)

    width = min(1400, max_width + 2 * margin)
    height = sum(line_heights) + 2 * margin + 28
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    header = title
    hb = draw.textbbox((0, 0), header, font=font)
    draw.text((margin, margin // 2), header, font=font, fill=accent)

    y = margin + (hb[3] - hb[1]) + 8
    for (text, is_title), lh in zip(wrapped, line_heights):
        fill = accent if is_title else fg
        if text or is_title:
            draw.text((margin, y), text, font=font, fill=fill)
        y += lh

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def capture_demo_text(n: int, repeats: int) -> str:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "demo.py"), "--n", str(n), "--repeats", str(repeats)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-demo", action="store_true", help="Run demo.py instead of sample_output.txt")
    parser.add_argument("--n", type=int, default=2000)
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()

    if args.from_demo:
        text = capture_demo_text(args.n, args.repeats)
        SAMPLE.write_text(text, encoding="utf-8")
    else:
        text = SAMPLE.read_text(encoding="utf-8")

    lines = [ln.rstrip("\n") for ln in text.strip().splitlines()]

    empirical_idx = next((i for i, ln in enumerate(lines) if ln.startswith("## Empirical")), len(lines))
    theory_lines = lines[:empirical_idx]
    timing_lines = lines[empirical_idx:]

    render_terminal_png(
        lines,
        IMAGES / "terminal-output.png",
        title="Full program output (theory + empirical timings)",
    )
    render_terminal_png(
        theory_lines,
        IMAGES / "output-theory-table.png",
        title="Theoretical comparison and notes",
    )
    render_terminal_png(
        timing_lines,
        IMAGES / "output-empirical-timings.png",
        title="Empirical timings (milliseconds, mean over repeats)",
    )
    print(f"Wrote:\n  {IMAGES / 'terminal-output.png'}\n  {IMAGES / 'output-theory-table.png'}\n  {IMAGES / 'output-empirical-timings.png'}")


if __name__ == "__main__":
    main()
