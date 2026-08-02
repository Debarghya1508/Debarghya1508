#!/usr/bin/env python3
"""
make_portrait.py
-----------------
Converts a photo into a self-typing ASCII-art SVG portrait.

Usage:
    python3 scripts/make_portrait.py path/to/photo.jpg assets/ascii.svg

No third-party services are used at runtime: the SVG produced is fully
self-contained and "types itself" using native SVG SMIL animation, so it
keeps animating on GitHub with nothing to rate-limit or go dark.
"""

import sys
from PIL import Image, ImageOps

# Dark -> light character ramp. Tune this if you want a denser/sparser look.
RAMP = "@%#*+=-:. "

COLS = 90                 # characters per row
FONT_SIZE = 9              # px
CHAR_W = FONT_SIZE * 0.6   # approx advance width for a monospace font
CHAR_H = FONT_SIZE * 1.15  # line height
ROW_DELAY = 0.035          # seconds between each row starting to type
TYPE_DUR = 0.55            # seconds for a single row to "type in"


def image_to_rows(path: str, cols: int = COLS) -> list[str]:
    img = Image.open(path).convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)

    # Monospace chars are taller than wide, so squash rows to compensate.
    aspect = img.height / img.width
    rows = max(1, round(cols * aspect * (CHAR_W / CHAR_H)))

    img = img.resize((cols, rows))
    pixels = list(img.getdata())

    ramp_len = len(RAMP) - 1
    lines = []
    for r in range(rows):
        row_pixels = pixels[r * cols:(r + 1) * cols]
        line = "".join(RAMP[int((255 - p) / 255 * ramp_len)] for p in row_pixels)
        lines.append(line)
    return lines


def escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(rows: list[str]) -> str:
    cols = max(len(r) for r in rows) if rows else 0
    width = round(cols * CHAR_W) + 20
    height = round(len(rows) * CHAR_H) + 20

    text_elems = []
    for i, row in enumerate(rows):
        y = 10 + FONT_SIZE + i * CHAR_H
        start = i * ROW_DELAY
        safe_row = escape(row) if row.strip() else "&#160;" * len(row)
        text_elems.append(
            f'''  <text x="10" y="{y:.1f}" class="ascii-row" opacity="0">{safe_row}'''
            f'''<animate attributeName="opacity" from="0" to="1" '''
            f'''begin="{start:.3f}s" dur="{TYPE_DUR}s" fill="freeze" /></text>'''
        )

    total_dur = len(rows) * ROW_DELAY + TYPE_DUR + 0.4

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" font-family="'JetBrains Mono','Cascadia Code','Fira Code',ui-monospace,'Courier New',monospace">
  <style>
    .ascii-bg {{ fill: #0d1117; }}
    .ascii-row {{ font-size: {FONT_SIZE}px; fill: #58a6ff; white-space: pre; }}
  </style>
  <rect class="ascii-bg" x="0" y="0" width="{width}" height="{height}" rx="6" />
{chr(10).join(text_elems)}
  <!-- loop: fade everything out, then back to the start -->
  <rect x="0" y="0" width="{width}" height="{height}" fill="#0d1117" opacity="0">
    <animate attributeName="opacity" values="0;0;1;0" keyTimes="0;0.97;0.985;1"
              dur="{total_dur + 3:.2f}s" repeatCount="indefinite" />
  </rect>
</svg>
'''
    return svg


def main():
    if len(sys.argv) != 3:
        print("usage: make_portrait.py <input-photo> <output-svg>")
        sys.exit(1)
    rows = image_to_rows(sys.argv[1])
    svg = build_svg(rows)
    with open(sys.argv[2], "w") as f:
        f.write(svg)
    print(f"wrote {sys.argv[2]} ({len(rows)} rows x {COLS} cols)")


if __name__ == "__main__":
    main()
