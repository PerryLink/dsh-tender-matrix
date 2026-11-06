#!/usr/bin/env python3
"""Generate README image assets for dsh-tender-matrix (docs/assets/).

Outputs (idempotent overwrite):
  dsh-tender-matrix-flow-light.svg / dsh-tender-matrix-flow-dark.svg
      Hero pipeline diagram. Two hand-written SVG files (vector — never
      rasterized to webp). Text inside uses command/rule tokens only
      (file | material, parse, runCheck, TM-001…TM-007, skipped[]), so all
      five README languages share the same pair.

This checker has no benchmark data, so no evidence bar chart is emitted.
Pillow is still imported and the CJK font is probed, matching the family
asset skeleton: if a later evidence figure is added, the font is already
guaranteed to render Chinese instead of tofu boxes.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (pip install pillow)
"""
from __future__ import annotations

import os
import sys

from PIL import ImageFont  # noqa: F401  (family skeleton; SVG-only output today)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges use labelColor #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e"),
}

# --- CJK font probe: Chinese must never render as tofu boxes ----------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render Chinese "
             "as tofu boxes; install one of the probed fonts and re-run.")


# ---------------------------------------------------------------------------
# Hero pipeline SVG (light + dark). Tokens only — no long natural language.
# ---------------------------------------------------------------------------
FLOW_NODES = [
    ("file | material", "JSON or YAML"),
    ("parse", "header + rows"),
    ("runCheck", "TM-001 … TM-007"),
    ("report", "found · expected · fix"),
]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 440
    nw, nh, gap = 210, 92, 50
    x0, y0 = 105, 140
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="dsh-tender-matrix pipeline">',
        '<title>dsh-tender-matrix pipeline</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">dsh-tender-matrix</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="16">evaluation-factor scoring matrix · '
        f'arithmetic self-consistency</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]
    for i, (label, sub) in enumerate(FLOW_NODES):
        x = x0 + i * (nw + gap)
        accent = GREEN[skin] if i == len(FLOW_NODES) - 1 else (
            FAMILY if i == 2 else s["border"])
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 38}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="17" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 66}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="12">{sub}</text>')
        if i < len(FLOW_NODES) - 1:
            ax = x + nw + 6
            ay = y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 12}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    # rule-pack box (feeds runCheck) and skipped[] box (reported alongside)
    box_y, box_h = 288, 54
    rule_x, rule_w = 300, 540
    skip_x, skip_w = 880, 260
    for cx, top in ((x0 + 2 * (nw + gap) + nw // 2, box_y),
                    (x0 + 3 * (nw + gap) + nw // 2, box_y)):
        parts.append(
            f'<path d="M{cx} {y0 + nh}v{top - y0 - nh}" stroke="{FAMILY}" '
            f'stroke-width="2" stroke-dasharray="5 5"/>')
    parts.append(
        f'<rect x="{rule_x}" y="{box_y}" width="{rule_w}" height="{box_h}" '
        f'rx="12" fill="{s["box"]}" stroke="{FAMILY}" stroke-width="2"/>')
    parts.append(
        f'<text x="{rule_x + rule_w // 2}" y="{box_y + 33}" fill="{s["text"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="14">rules/tender-matrix.yaml · TM-001 … TM-007</text>')
    parts.append(
        f'<rect x="{skip_x}" y="{box_y}" width="{skip_w}" height="{box_h}" '
        f'rx="12" fill="{s["box"]}" stroke="{s["border"]}" stroke-width="2"/>')
    parts.append(
        f'<text x="{skip_x + skip_w // 2}" y="{box_y + 33}" fill="{s["sub"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="14">skipped[] · reason recorded</text>')
    parts.append(
        f'<text x="60" y="404" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">read-only material · no network · no model '
        f'call · differences only</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"dsh-tender-matrix-flow-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG hero assets to docs/assets/ "
          f"(CJK font: {os.path.basename(FONT_PATH)})")


if __name__ == "__main__":
    main()
