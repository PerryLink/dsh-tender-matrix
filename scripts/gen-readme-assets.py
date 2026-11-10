#!/usr/bin/env python3
"""README visuals for dsh-tender-matrix, read off the shipped checker.

Two figures, both derived from this repository rather than a generic checker
template:

  hero 1440x576 (Pillow; zh/en x light/dark -> four WebP files)
      Left column: kicker / wordmark / two value lines / subtitle / meta /
      footer.  Right side: the real TM-002 fixture
      (`tests/fixtures/TM-002/TM-002-unsafe.json`) as a small scoring matrix.
      Row 1 carries bidderA 32 against maxScore 30, so TM-002 is the one warn;
      TM-003 and TM-004 are skipped because both `target`s ship as 0.  The
      seven-rule rail, the finding card and the 1 warn / 2 skipped / 4 clean
      tally are that run's actual result (lib/index.mjs, default config).

  flow 1100x660 (hand-written SVG, light/dark)
      Grammar: ANNOTATED MATRIX -- the scoring matrix is the object under
      audit, and each rule is attached to the column or band it reads:
        TM-001 header (project + method)
        TM-002 分值 · 投标人A (bidderA <= maxScore)
        TM-003 分值 column (sum of maxScore -> target, skipped)
        TM-004 投标人A column (sum of bidderA -> target, skipped)
        TM-005 评分依据 column (presence)
        TM-006 序号 column (unique)
        TM-007 评分依据 column (placeholder terms)
      The material enters once (file | material -> parseTable -> header +
      rows[]); the rule pack is the ruler attached to the matrix, not another
      flow node.  Two exits leave the matrix: `issues[]` (TM-002, row 1,
      32 > 30) and `skipped[]` (TM-003 / TM-004, target 0).  No verdict.

Every label is measured before it is drawn; a label that would overflow aborts
the run instead of shipping clipped text.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow, and the Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-tender-matrix"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")
os.makedirs(OUT, exist_ok=True)

RADIUS = 20
SHADOW = 24

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", edge="#e6e2ef", band="#f5f2fb",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", pill="#ece7f9",
        mark="#b45309", mark_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        grid="#e7e4f0", dot="#d8d1e8",
        shadow=(38, 30, 72), glow=34,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", edge="#2e374b", band="#202839",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", pill="#242d42",
        mark="#d9a441", mark_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        grid="#2b3348", dot="#2a3346",
        shadow=(0, 0, 0), glow=48,
    ),
}


def font(size: float, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], int(round(size)))


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.12 * (y / h) + 0.88 * (y / h) ** 1.3
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: str,
         alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = hx(color)
    for i in range(10, 0, -1):
        rr = r * i / 10
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=rgb + (int(alpha * (1 - i / 11)),))
    return Image.alpha_composite(
        img.convert("RGBA"),
        layer.filter(ImageFilter.GaussianBlur(26)),
    ).convert("RGB")


def card(img: Image.Image, box: tuple[int, int, int, int], s: dict,
         radius: int = RADIUS, shadow: int = SHADOW,
         fill: str | None = None, edge: str | None = None) -> Image.Image:
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -2):
        sd.rounded_rectangle(
            [x0 - i // 6, y0 + i // 2, x1 + i // 6, y1 + i],
            radius=radius + i // 6,
            fill=s["shadow"] + (int(10 * (1 - i / shadow)),),
        )
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(11)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(edge or s["edge"]), width=2)
    return base.convert("RGB")


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: float, kind: str) -> float:
    return _MEASURE.textlength(text, font=font(size, kind))


def require_w(text: str, size: float, kind: str, max_w: float,
              what: str) -> None:
    got = measure(text, size, kind)
    if got > max_w + 0.4:
        raise SystemExit(
            f"FATAL: {what} overflows: {text!r} needs {got:.1f}px > "
            f"{max_w:.0f}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(
        f"FATAL: text does not fit {max_w}px at >= {minimum}px: {text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold") -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + 30, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + 15, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + 30)


def chip_right(img: Image.Image, right: int, y: int, text: str, fg: str,
               bg: str, size: float = 11, height: int = 20,
               kind: str = "cjk_bold") -> int:
    d = ImageDraw.Draw(img)
    w = d.textlength(text, font=font(size, kind)) + 18
    x = right - w
    d.rounded_rectangle([x, y, right, y + height], radius=height / 2,
                        fill=hx(bg))
    d.text((x + 9, y + height / 2), text, font=font(size, kind),
           fill=hx(fg), anchor="lm")
    return int(x)


def dash_round_rect(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                    color: str, radius: int = 8, width: int = 2) -> None:
    x0, y0, x1, y1 = box
    for x in range(int(x0 + radius), int(x1 - radius), 10):
        d.line([(x, y0), (min(x + 6, x1 - radius), y0)], fill=hx(color),
               width=width)
        d.line([(x, y1), (min(x + 6, x1 - radius), y1)], fill=hx(color),
               width=width)
    for y in range(int(y0 + radius), int(y1 - radius), 10):
        d.line([(x0, y), (x0, min(y + 6, y1 - radius))], fill=hx(color),
               width=width)
        d.line([(x1, y), (x1, min(y + 6, y1 - radius))], fill=hx(color),
               width=width)
    d.arc([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360,
          fill=hx(color), width=width)
    d.arc([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90,
          fill=hx(color), width=width)


# --------------------------------------------------------------------------- hero
# The fixture is the TM-002 one.  Every string below is either that material,
# the report fields from a real run, or the rule pack's own vocabulary.
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 评标矩阵核对器",
        value=["七条规则，逐行核对评分矩阵",
               "只指出差异，不替评标委员会下结论"],
        sub="读表头与每行评分，核对上限、合计与依据。",
        meta="tender_matrix · TM-001…TM-007 · rules v2026.1",
        foot="Apache-2.0 · 只读材料 · 不联网 · 不调用模型",
        card_title="评分矩阵 · 只读",
        rule_label="七条规则 · 本次运行",
        rule_state="1 命中 · 2 未执行",
        doc_meta="某某工程施工招标 · 综合评估法 · ZB-2026-018",
        headers=["序号", "评审因素", "分值", "A", "B", "C"],
        row=["1", "施工组织设计", "30", "32", "24", "28"],
        ghost="rows[2…n] · 逐行套用同一组规则",
        callout="TM-002 · 32 > 30 · bidderA 对 maxScore",
        finding_title="定位差异 · TM-002",
        finding_chip="warn",
        locator="第 1 行 · field bidderA",
        found="第 1 行「bidderA」为 32，「maxScore」为 30",
        expected="「bidderA」应不大于「maxScore」",
        fix="核对评分是否抄错；本条只核对是否超出分值上限",
        count="issues[] 1 · skipped[] 2 · 4 clean",
        verdict="不判合规",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · scoring-matrix checker",
        value=["Seven rules, one scoring matrix —",
               "differences only, never the verdict"],
        sub="Header plus rows; checks caps, totals and basis.",
        meta="tender_matrix · TM-001…TM-007 · rules v2026.1",
        foot="Apache-2.0 · read-only material · no network · no model call",
        card_title="Scoring matrix · read-only",
        rule_label="Seven rules · this run",
        rule_state="1 hit · 2 skipped",
        doc_meta="some works tender · comprehensive evaluation · ZB-2026-018",
        headers=["seq", "criterion", "max", "A", "B", "C"],
        row=["1", "Construction plan", "30", "32", "24", "28"],
        ghost="rows[2…n] · same seven rules, row by row",
        callout="TM-002 · 32 > 30 · bidderA vs maxScore",
        finding_title="Finding · TM-002",
        finding_chip="warn",
        locator="row 1 · field bidderA",
        found="row 1 · bidderA 32 > maxScore 30",
        expected="bidderA should be ≤ maxScore",
        fix="check the entered score; this check only reads the cap",
        count="issues[] 1 · skipped[] 2 · 4 clean",
        verdict="no verdict",
    ),
}

HERO_STATES = ["clean", "warn", "skip", "skip", "clean", "clean", "clean"]


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    h = HERO[lang]
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1160, 70, 390, s["accent"], s["glow"])
    img = glow(img, 150, 560, 320, s["accent"], max(8, s["glow"] // 3))
    d = ImageDraw.Draw(img)
    m = 52
    col_w = 760

    # ---- left column --------------------------------------------------------
    pill(img, (m, 56), h["kicker"], s, size=20)
    d = ImageDraw.Draw(img)

    title_size = 80
    d.text((m - 1, 120), NAME, font=font(title_size, "mono_bold"),
           fill=hx(s["text"]))
    require_w(NAME, title_size, "mono_bold", col_w, "hero title")

    value_size = fit_lines(h["value"], "cjk_bold", col_w,
                           36 if lang == "zh" else 34, 30)
    for i, line in enumerate(h["value"]):
        d.text((m, 244 + i * 50), line, font=font(value_size, "cjk_bold"),
               fill=hx(s["text"]))
        require_w(line, value_size, "cjk_bold", col_w, "hero value line")

    require_w(h["sub"], 26, "cjk", col_w, "hero subtitle")
    d.text((m, 356), h["sub"], font=font(26, "cjk"), fill=hx(s["sub"]))

    require_w(h["meta"], 20, "mono", col_w, "hero meta")
    d.text((m + 1, 406), h["meta"], font=font(20, "mono"), fill=hx(s["faint"]))

    d.line([m + 1, 452, m + col_w - 4, 452], fill=hx(s["grid"]), width=2)
    require_w(h["foot"], 20, "cjk", col_w, "hero footer")
    d.text((m + 1, 474), h["foot"], font=font(20, "cjk"), fill=hx(s["faint"]))

    # ---- right card ---------------------------------------------------------
    img = card(img, (848, 48, 1388, 528), s, radius=22, shadow=30)
    d = ImageDraw.Draw(img)
    d.text((870, 70), h["card_title"], font=font(18, "cjk_bold"),
           fill=hx(s["text"]))
    require_w(h["card_title"], 18, "cjk_bold", 300, "hero card title")
    chip_right(img, 1366, 66, "JSON / YAML", s["accent"], s["pill"], size=12)
    d = ImageDraw.Draw(img)

    d.text((870, 101), h["rule_label"], font=font(12.5, "cjk_bold"),
           fill=hx(s["sub"]))
    require_w(h["rule_label"], 12.5, "cjk_bold", 280, "hero rule label")
    d.text((1366, 101), h["rule_state"], font=font(11.5, "cjk"),
           fill=hx(s["faint"]), anchor="rt")
    require_w(h["rule_state"], 11.5, "cjk", 210, "hero rule state")

    pw, gap, py, ph = 65, 6, 121, 24
    for i, (rid, state) in enumerate(zip(
            [f"TM-00{i}" for i in range(1, 8)], HERO_STATES)):
        x = 870 + i * (pw + gap)
        if state == "clean":
            d.rounded_rectangle([x, py, x + pw, py + ph], radius=12,
                                fill=hx(s["ok_bg"]))
            colour = s["ok"]
        elif state == "warn":
            d.rounded_rectangle([x, py, x + pw, py + ph], radius=12,
                                fill=hx(s["mark_bg"]),
                                outline=hx(s["mark"]), width=2)
            colour = s["mark"]
        else:
            d.rounded_rectangle([x, py, x + pw, py + ph], radius=12,
                                fill=hx(s["card"]))
            dash_round_rect(d, (x, py, x + pw, py + ph), s["faint"],
                            radius=12, width=1)
            colour = s["faint"]
        d.text((x + pw / 2, py + ph / 2), rid,
               font=font(11, "mono_bold"), fill=hx(colour), anchor="mm")

    require_w(h["doc_meta"], 12.5, "cjk", 430, "hero document meta")
    d.text((870, 158), h["doc_meta"], font=font(12.5, "cjk"),
           fill=hx(s["sub"]))
    d.line([870, 178, 1366, 178], fill=hx(s["grid"]), width=1)

    # ---- the real fixture, as a small matrix --------------------------------
    xs = [870, 914, 1080, 1144, 1222, 1286, 1350]  # 6 column edges
    widths = [44, 166, 64, 78, 64, 64]
    d.rounded_rectangle([870, 186, 1350, 212], radius=8, fill=hx(s["band"]))
    for i, head in enumerate(h["headers"]):
        require_w(head, 12, "cjk_bold", widths[i] - 10, "hero table header")
        d.text((xs[i] + 8, 199), head, font=font(12, "cjk_bold"),
               fill=hx(s["sub"]), anchor="lm")

    d.rounded_rectangle([1146, 218, 1218, 258], radius=10,
                        fill=hx(s["mark_bg"]))
    dash_round_rect(d, (1146, 218, 1218, 258), s["mark"], radius=10, width=2)
    for i, cell in enumerate(h["row"]):
        if i == 3:
            d.text((1152, 242), cell, font=font(15, "mono_bold"),
                   fill=hx(s["mark"]), anchor="lm")
            continue
        require_w(cell, 13.5, "cjk", widths[i] - 14, "hero table cell")
        d.text((xs[i] + 8, 242), cell, font=font(13.5, "cjk"),
               fill=hx(s["text"]), anchor="lm")
    d.line([870, 280, 1350, 280], fill=hx(s["grid"]), width=1)

    require_w(h["ghost"], 11, "cjk", 470, "hero ghost row")
    d.text((870, 292), h["ghost"], font=font(11, "cjk"), fill=hx(s["faint"]))

    # ---- the located finding ------------------------------------------------
    d.rounded_rectangle([870, 310, 1366, 342], radius=10,
                        fill=hx(s["mark_bg"]))
    require_w(h["callout"], 12.5, "cjk", 470, "hero callout")
    d.text((886, 326), h["callout"], font=font(12.5, "cjk"),
           fill=hx(s["mark"]), anchor="lm")

    img = card(img, (870, 352, 1366, 506), s, radius=18, shadow=20)
    d = ImageDraw.Draw(img)
    d.text((890, 368), h["finding_title"], font=font(15, "cjk_bold"),
           fill=hx(s["text"]))
    require_w(h["finding_title"], 15, "cjk_bold", 270, "hero finding title")
    chip_right(img, 1352, 364, h["finding_chip"], s["mark"], s["mark_bg"],
               size=11)
    d = ImageDraw.Draw(img)

    require_w(h["locator"], 11.5, "cjk", 430, "hero locator")
    d.text((890, 392), h["locator"], font=font(11.5, "cjk"),
           fill=hx(s["faint"]))
    require_w(h["found"], 13.5, "cjk", 456, "hero found")
    d.text((890, 414), h["found"], font=font(13.5, "cjk"),
           fill=hx(s["text"]))
    require_w(h["expected"], 12.5, "cjk", 456, "hero expected")
    d.text((890, 438), h["expected"], font=font(12.5, "cjk"),
           fill=hx(s["sub"]))
    require_w(h["fix"], 11.5, "cjk", 456, "hero fix")
    d.text((890, 462), h["fix"], font=font(11.5, "cjk"), fill=hx(s["sub"]))

    require_w(h["count"], 11, "cjk", 300, "hero count")
    d.text((890, 486), h["count"], font=font(11, "cjk"), fill=hx(s["faint"]))
    require_w(h["verdict"], 11, "cjk", 110, "hero verdict")
    d.text((1352, 486), h["verdict"], font=font(11, "cjk"),
           fill=hx(s["mark"]), anchor="rt")

    out = f"{NAME}-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, out), "WEBP", quality=92, method=6)
    print(f"wrote {out} ({W}x{H})")


# --------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", edge="#e6e2ef", band="#f5f2fb", pill="#ece7f9",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", mark="#b45309", mark_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        grid="#e7e4f0", dot="#cfc8e2",
        shadow="#2b2440", shadow_op="0.13",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", edge="#2e374b", band="#202839", pill="#242d42",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", mark="#d9a441", mark_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        grid="#2b3348", dot="#2a3346",
        shadow="#000000", shadow_op="0.50",
    ),
}

FONT_CSS_SANS = ("'Microsoft YaHei','Segoe UI','PingFang SC',"
                 "'Noto Sans CJK SC',sans-serif")
FONT_CSS_MONO = "Consolas,'Microsoft YaHei',ui-monospace,monospace"


class Svg:
    """Small SVG writer that measures every label before it is emitted."""

    def __init__(self, s: dict) -> None:
        self.s = s
        self.parts: list[str] = []
        self.overflows: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def width(self, content: str, size: float, mono: bool = False,
              bold: bool = False, spacing: float | None = None) -> float:
        if mono and content.isascii():
            kind = "mono_bold" if bold else "mono"
        elif any(ord(c) > 127 for c in content):
            kind = "cjk_bold" if bold else "cjk"
        elif mono:
            kind = "mono_bold" if bold else "mono"
        else:
            kind = "cjk_bold" if bold else "cjk"
        got = _MEASURE.textlength(
            content, font=ImageFont.truetype(FONT_FILES[kind], int(round(size)))
        )
        if spacing:
            got += spacing * max(len(content) - 1, 0)
        return got

    def text(self, x: float, y: float, content: str, size: float, fill: str, *,
             anchor: str = "start", mono: bool = False, bold: bool = False,
             max_w: float | None = None, opacity: float | None = None,
             spacing: float | None = None) -> None:
        got = self.width(content, size, mono, bold, spacing)
        if max_w is not None and got > max_w:
            self.overflows.append(f"{content!r} needs {got:.1f} > {max_w:.1f}")
        family = FONT_CSS_MONO if mono else FONT_CSS_SANS
        attrs = ""
        if anchor != "start":
            attrs += f' text-anchor="{anchor}"'
        if bold:
            attrs += ' font-weight="700"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        if spacing is not None:
            attrs += f' letter-spacing="{spacing}"'
        self.add(f'<text x="{x}" y="{y}" fill="{fill}" '
                 f'font-family="{family}" font-size="{size}"{attrs}>'
                 f'{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, rx: float,
             fill: str, stroke: str | None = None, sw: float = 1.4,
             opacity: float | None = None, shadow: bool = False,
             dash: str | None = None) -> None:
        attrs = ""
        if stroke:
            attrs += f' stroke="{stroke}" stroke-width="{sw}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        if shadow:
            attrs += ' filter="url(#soft)"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                 f'fill="{fill}"{attrs}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, stroke: str,
             width: float = 1, opacity: float | None = None,
             dash: str | None = None, marker: str | None = None) -> None:
        attrs = f' stroke-width="{width}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if marker:
            attrs += f' marker-end="url(#{marker})"'
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                 f'stroke="{stroke}"{attrs}/>')

    def path(self, d: str, stroke: str, width: float = 2,
             marker: str | None = None, dash: str | None = None) -> None:
        attrs = f' fill="none" stroke="{stroke}" stroke-width="{width}"'
        if marker:
            attrs += f' marker-end="url(#{marker})"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        self.add(f'<path d="{d}"{attrs}/>')

    def pill_right(self, right: float, cy: float, content: str, fg: str,
                   bg: str, size: float = 11, height: float = 22) -> float:
        w = self.width(content, size, mono=True, bold=True) + 18
        x = right - w
        self.rect(x, cy - height / 2, w, height, height / 2, bg)
        self.add(f'<text x="{x + w / 2}" y="{cy + size * 0.35}" fill="{fg}" '
                 f'font-family="{FONT_CSS_MONO}" font-size="{size}" '
                 f'font-weight="700" text-anchor="middle">'
                 f'{escape(content)}</text>')
        return x

    def chip(self, x: float, y: float, content: str, state: str,
             w: float = 54, h: float = 18, size: float = 11) -> None:
        s = self.s
        if state == "clean":
            fill, stroke, fg = s["ok_bg"], s["ok"], s["ok"]
            dash = None
        elif state == "warn":
            fill, stroke, fg = s["mark_bg"], s["mark"], s["mark"]
            dash = None
        else:
            fill, stroke, fg = s["panel"], s["faint"], s["faint"]
            dash = "4 3"
        self.rect(x, y, w, h, h / 2, fill, stroke, 1.2, dash=dash)
        self.add(f'<text x="{x + w / 2}" y="{y + h * 0.72}" fill="{fg}" '
                 f'font-family="{FONT_CSS_MONO}" font-size="{size}" '
                 f'font-weight="700" text-anchor="middle">'
                 f'{escape(content)}</text>')


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    svg = Svg(s)

    svg.add('<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="660" '
            'viewBox="0 0 1100 660" role="img" '
            'aria-labelledby="figTitle figDesc">')
    svg.add('<title id="figTitle">dsh-tender-matrix structure: one scoring '
            'matrix, seven rule locators, two exits</title>')
    svg.add('<desc id="figDesc">The material (file or material, JSON or YAML) '
            'is parsed into a header plus rows. The scoring matrix is the '
            'object under audit: TM-001 reads the project and method header, '
            'TM-006 reads seq, TM-003 reads the maxScore column, TM-002 '
            'compares bidderA with maxScore, TM-004 reads the bidderA column, '
            'and TM-005 plus TM-007 read the basis column. On the real TM-002 '
            'fixture, TM-002 fires on row 1 with 32 greater than 30, while '
            'TM-003 and TM-004 are skipped because target is 0. Two exits: '
            'issues[] and skipped[]. The report passes no compliance verdict.'
            '</desc>')

    # ---- background ---------------------------------------------------------
    svg.add('<defs>')
    svg.add('<linearGradient id="bg" x1="0" y1="0" x2="0.25" y2="1">'
            f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
            f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    svg.add(f'<filter id="soft" x="-30%" y="-30%" width="170%" height="185%">'
            f'<feDropShadow dx="0" dy="7" stdDeviation="10" '
            f'flood-color="{s["shadow"]}" flood-opacity="{s["shadow_op"]}"/>'
            f'</filter>')
    svg.add(f'<pattern id="dots" width="26" height="26" '
            f'patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" '
            f'r="1.2" fill="{s["dot"]}"/></pattern>')
    svg.add(f'<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    svg.add(f'<marker id="arrfaint" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{s["faint"]}"/></marker>')
    svg.add('</defs>')
    svg.add('<rect width="1100" height="660" rx="22" fill="url(#bg)"/>')
    svg.add('<rect width="1100" height="660" rx="22" fill="url(#dots)" '
            'opacity="0.5"/>')

    # ---- header -------------------------------------------------------------
    svg.text(44, 58, NAME, 30, s["text"], mono=True, bold=True, max_w=520)
    svg.text(
        44, 86,
        "One scoring matrix, seven rules; hits go to issues[], checks that cannot run to skipped[]. No verdict.",
        14.5, s["sub"], max_w=790,
    )
    svg.pill_right(1056, 48, "rules 2026.1 · 7 rules", s["accent"], s["pill"])
    svg.text(44, 108, "IN · file | material · JSON / YAML · aliases → fields",
             11, s["faint"], mono=True, max_w=520)
    svg.text(1056, 108, "OUT · issues[] + skipped[] · no verdict", 11,
             s["faint"], anchor="end", mono=True, max_w=360)
    svg.line(44, 122, 1056, 122, s["grid"], 1)

    # ---- material intake (one channel) -------------------------------------
    svg.rect(44, 136, 700, 62, 16, s["panel"], s["edge"], 1.4, shadow=True)
    svg.text(60, 154, "MATERIAL · READ-ONLY", 11, s["faint"], bold=True,
             spacing=1.1, max_w=600)
    svg.text(60, 174, "file | material", 13, s["text"], mono=True, bold=True,
             max_w=130)
    svg.line(170, 169, 196, 169, s["sub"], 1.6, marker="arrfaint")
    svg.text(204, 174, "parseTable", 12, s["text"], mono=True, bold=True,
             max_w=100)
    svg.line(282, 169, 308, 169, s["sub"], 1.6, marker="arrfaint")
    svg.text(316, 174, "header + rows[]", 12, s["text"], mono=True, bold=True,
             max_w=160)
    svg.text(60, 190, "JSON / YAML · column aliases → canonical fields", 11,
             s["sub"], max_w=650)

    # ---- the rule pack is the ruler, not another flow node ------------------
    svg.rect(764, 136, 292, 62, 16, s["panel"], s["edge"], 1.4, shadow=True)
    svg.text(780, 154, "AUDIT FRAME · RULE PACK", 11, s["faint"], bold=True,
             spacing=1.1, max_w=260)
    svg.text(780, 174, "rules/tender-matrix.yaml", 12, s["text"], mono=True,
             bold=True, max_w=260)
    svg.text(780, 190, "v2026.1 · 7 rules · load guard", 11, s["sub"],
             max_w=260)
    svg.line(80, 198, 80, 212, s["accent"], 1.6, marker="arr")
    svg.line(910, 198, 910, 212, s["faint"], 1.4, dash="4 4")

    # ---- the scoring matrix under audit ------------------------------------
    svg.rect(44, 214, 1012, 286, 20, s["panel"], s["edge"], 1.4,
             shadow=True)
    svg.text(64, 238, "Scoring matrix · read-only", 16, s["text"], bold=True,
             max_w=240)
    svg.text(1036, 238,
             "sample · tests/fixtures/TM-002/TM-002-unsafe.json", 11,
             s["faint"], anchor="end", mono=True, max_w=330)

    # header band: project / method / tenderNo, read by TM-001
    svg.rect(64, 252, 972, 34, 10, s["band"])
    svg.text(76, 274, "project", 11, s["faint"], mono=True, max_w=46)
    svg.text(126, 274, "some works tender", 11.5, s["text"], max_w=140)
    svg.text(250, 274, "method", 11, s["faint"], mono=True, max_w=42)
    svg.text(298, 274, "comprehensive evaluation", 11.5, s["text"], max_w=160)
    svg.text(470, 274, "tenderNo", 11, s["faint"], mono=True, max_w=55)
    svg.text(532, 274, "ZB-2026-018", 11.5, s["text"], mono=True, max_w=90)
    svg.chip(958, 260, "TM-001", "clean", w=54)

    # table geometry: seq | criterion | category | maxScore | A | B | C | basis
    xs = [64, 118, 304, 384, 462, 528, 592, 656, 1036]
    svg.rect(64, 294, 972, 166, 10, "none", s["edge"], 1.2)
    svg.rect(64, 294, 972, 50, 10, s["band"])
    for x in xs[1:-1]:
        svg.line(x, 294, x, 460, s["grid"], 1)
    for y in (344, 432):
        svg.line(64, y, 1036, y, s["grid"], 1)

    heads = ["seq", "criterion", "category", "maxScore", "bidderA",
             "bidderB", "bidderC", "basis"]
    for i, head in enumerate(heads):
        svg.text(xs[i] + 8, 312, head, 12, s["text"], bold=True,
                 max_w=xs[i + 1] - xs[i] - 14)

    svg.chip(72, 320, "TM-006", "clean", w=54)
    svg.chip(392, 320, "TM-003", "skip", w=54)
    svg.chip(470, 320, "TM-004", "skip", w=54)
    svg.chip(664, 320, "TM-005", "clean", w=54)
    svg.chip(722, 320, "TM-007", "clean", w=54)

    # the real fixture row
    svg.text(72, 370, "1", 14, s["text"], mono=True, max_w=36)
    svg.text(126, 370, "construction plan", 13, s["text"], max_w=168)
    svg.text(312, 370, "technical", 13, s["text"], max_w=64)
    svg.text(400, 370, "30", 14, s["text"], mono=True, max_w=50)
    svg.rect(464, 350, 62, 32, 8, s["mark_bg"], s["mark"], 1.6, dash="4 3")
    svg.text(476, 372, "32", 15, s["mark"], mono=True, bold=True, max_w=40)
    svg.text(536, 370, "24", 13, s["text"], mono=True, max_w=48)
    svg.text(600, 370, "28", 13, s["text"], mono=True, max_w=48)
    svg.text(664, 370, "tender method art. 3.2 · completeness 26 pts", 13,
             s["text"], max_w=366)

    # the cell-level comparison sits on the cell; column-level checks sit in
    # the column header, so no rule chip is drawn twice.
    svg.chip(470, 394, "TM-002", "warn", w=54)
    svg.text(470, 426, "32 > 30", 11, s["mark"], mono=True, bold=True,
             max_w=56)
    svg.text(392, 426, "target 0", 11, s["faint"], mono=True, max_w=56)
    svg.text(664, 426, "filled · no placeholder", 11, s["faint"], max_w=180)

    # ghost continuation rows
    svg.rect(64, 432, 972, 28, 0, s["band"])
    svg.line(64, 432, 1036, 432, s["grid"], 1, dash="3 4")
    svg.text(72, 450, "rows[2…n] · same rules, row by row", 11, s["faint"],
             max_w=320)
    svg.text(1036, 450, "aliases → fields · row by row", 11, s["faint"],
             anchor="end", max_w=260)

    svg.text(64, 482, "legend: green = clean · amber = hit · dashed = skipped",
             11, s["faint"], max_w=520)
    svg.text(1036, 482, "this run: 4 clean · 1 warn · 2 skipped", 11,
             s["sub"], anchor="end", max_w=300)

    # ---- two exits ----------------------------------------------------------
    svg.line(300, 500, 300, 512, s["mark"], 1.6, marker="arr")
    svg.line(800, 500, 800, 512, s["faint"], 1.4, marker="arrfaint")

    svg.rect(44, 514, 600, 100, 18, s["panel"], s["edge"], 1.4, shadow=True)
    svg.rect(52, 524, 4, 80, 2, s["mark"])
    svg.text(68, 538, "issues[] · 1", 12.5, s["mark"], bold=True, max_w=160)
    svg.text(626, 538, "warn", 11, s["mark"], anchor="end", mono=True,
             max_w=44)
    svg.text(68, 560, "TM-002 · row 1 · field bidderA", 13, s["text"],
             mono=True, bold=True, max_w=560)
    svg.text(68, 580, "32 > 30 · bidderA should be ≤ maxScore", 11.5,
             s["sub"], max_w=560)
    svg.text(68, 600,
             "check the entered score; no judgement on the score itself",
             11, s["faint"], max_w=560)

    svg.rect(660, 514, 396, 100, 18, s["panel"], s["edge"], 1.4, shadow=True)
    svg.rect(668, 524, 4, 80, 2, s["faint"])
    svg.text(684, 538, "skipped[] · 2", 12.5, s["faint"], bold=True,
             max_w=170)
    svg.text(1040, 538, "unset", 11, s["faint"], anchor="end", max_w=56)
    svg.text(684, 560, "TM-003 · target 0", 12, s["text"], mono=True,
             max_w=340)
    svg.text(684, 578, "TM-004 · target 0", 12, s["text"], mono=True,
             max_w=340)
    svg.text(684, 600, "unset ≠ passed · reason returned with the entry", 11,
             s["mark"], max_w=350)

    # ---- footer -------------------------------------------------------------
    svg.text(44, 640, "7 rules = 4 clean · 1 warn · 2 skipped", 11,
             s["faint"], mono=True, max_w=420)
    svg.rect(800, 620, 256, 30, 15, s["pill"], s["accent"], 1.4)
    svg.text(928, 640, "NO VERDICT · differences only", 11, s["accent"],
             anchor="middle", bold=True, max_w=236)

    if svg.overflows:
        raise SystemExit("FATAL: SVG label overflow:\n  " +
                         "\n  ".join(svg.overflows))
    svg.add('</svg>')
    return "\n".join(svg.parts) + "\n"


def main() -> None:
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"{NAME}-flow-v5-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG flow assets to docs/assets/ "
          f"(CJK font: {os.path.basename(FONT_FILES['cjk'])})")


if __name__ == "__main__":
    main()
