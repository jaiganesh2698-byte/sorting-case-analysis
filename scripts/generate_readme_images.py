"""Render docs/sample_output.txt (or fresh demo output) as terminal-style PNGs for the README.

Text is drawn at high resolution then downscaled (supersampling) so edges look smooth
at normal zoom and when the faculty opens images full-screen.
"""

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


def render_terminal_png(
    lines: list[str],
    out_path: Path,
    *,
    title: str,
    supersample: int = 3,
    max_out_width: int = 1920,
    min_out_width: int = 960,
    base_font_px: int = 17,
    max_chars: int = 118,
) -> None:
    from PIL import Image, ImageDraw

    if supersample < 1:
        supersample = 1

    bg = (24, 26, 28)
    fg = (230, 245, 230)
    accent = (160, 195, 255)
    margin = int(28 * supersample)
    font_size = int(base_font_px * supersample)
    line_gap = int(6 * supersample)
    cap_w = max_out_width * supersample

    font = _load_font(font_size)
    draw_tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    wrapped: list[tuple[str, bool]] = []
    wrapped.append(("$ python demo.py --n 2000 --repeats 2", True))
    wrapped.append(("", False))
    for raw in lines:
        for seg in _wrap_line(raw, max_chars):
            wrapped.append((seg, False))

    header_bbox = draw_tmp.textbbox((0, 0), title, font=font)
    max_text_px = header_bbox[2] - header_bbox[0]

    line_heights: list[int] = []
    for text, is_title in wrapped:
        if not text and not is_title:
            bbox = draw_tmp.textbbox((0, 0), " ", font=font)
            line_heights.append(bbox[3] - bbox[1] + line_gap)
            continue
        bbox = draw_tmp.textbbox((0, 0), text or " ", font=font)
        h = bbox[3] - bbox[1] + line_gap
        line_heights.append(h)
        max_text_px = max(max_text_px, bbox[2] - bbox[0])

    min_canvas = int(min_out_width * supersample)
    width = min(cap_w, max(min_canvas, max_text_px + 2 * margin))
    header_h = header_bbox[3] - header_bbox[1] + int(12 * supersample)
    height = margin + header_h + sum(line_heights) + margin

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    draw.text((margin, margin // 2), title, font=font, fill=accent)

    y = margin + header_h
    for (text, is_title), lh in zip(wrapped, line_heights):
        fill = accent if is_title else fg
        if text or is_title:
            draw.text((margin, y), text, font=font, fill=fill)
        y += lh

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if supersample > 1:
        out_w = max(1, width // supersample)
        out_h = max(1, height // supersample)
        img = img.resize((out_w, out_h), Image.Resampling.LANCZOS)

    img.save(out_path, "PNG", compress_level=3)


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
    parser.add_argument(
        "--supersample",
        type=int,
        default=3,
        help="Draw at N× size then downscale (default 3 = smoother text). Use 1 for a fast draft.",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=1920,
        help="Maximum output width in pixels after downscaling (default 1920).",
    )
    parser.add_argument(
        "--min-width",
        type=int,
        default=960,
        help="Minimum output width in pixels after downscaling (default 960).",
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=17,
        help="Base font size in output pixels after downscaling (default 17).",
    )
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

    kw = dict(
        supersample=args.supersample,
        max_out_width=args.max_width,
        min_out_width=args.min_width,
        base_font_px=args.font_size,
    )

    render_terminal_png(
        lines,
        IMAGES / "terminal-output.png",
        title="Full program output (theory + empirical timings)",
        **kw,
    )
    render_terminal_png(
        theory_lines,
        IMAGES / "output-theory-table.png",
        title="Theoretical comparison and notes",
        **kw,
    )
    render_terminal_png(
        timing_lines,
        IMAGES / "output-empirical-timings.png",
        title="Empirical timings (milliseconds, mean over repeats)",
        **kw,
    )
    print(f"Wrote:\n  {IMAGES / 'terminal-output.png'}\n  {IMAGES / 'output-theory-table.png'}\n  {IMAGES / 'output-empirical-timings.png'}")


if __name__ == "__main__":
    main()
