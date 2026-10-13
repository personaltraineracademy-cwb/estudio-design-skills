"""Key visuals for social/ads in the house style: giant cropped symbol, diagonal splits, side frames, tone-on-tone
pattern, centred — every size from one command.

Usage:
  python keyvisual.py --lockup-dark kit/svg/x-horizontal-escuro.svg --lockup-light kit/svg/x-horizontal-positivo.svg \
      --symbol symbol.svg --accent "#F8C100" --dark "#1A1A1A" --light "#F5F5F5" \
      --headline "ATÉ 50% OFF" --sub "SÓ ATÉ DOMINGO" --font Anton -o out/kv
Options:
  --layouts crop split frame pattern center      (default: all)
  --sizes 1080x1080 1080x1350 1080x1920 1920x1080 (default: all four)
  --seed 3            varies corner/angle choices   --vertical-lockup v.svg   used on tall formats if given
Writes <o>-<layout>-<WxH>.svg/.png and <o>-sheet.png. Lockups must already be coloured for their background:
--lockup-dark = version for dark backgrounds, --lockup-light = version for light backgrounds.
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Font, font_path, recolor, svg_inner, svg_to_png, viewbox, wrap_svg, write  # noqa: E402

LAYOUTS = ["crop", "split", "frame", "pattern", "center"]
SIZES = ["1080x1080", "1080x1350", "1080x1920", "1920x1080"]


def place(svg_text, cx, cy, max_w, max_h, colour=None):
    vx, vy, vw, vh = viewbox(svg_text)
    k = min(max_w / vw, max_h / vh)
    body = svg_inner(recolor(svg_text, colour) if colour else svg_text)
    fill = f' fill="{colour}"' if colour else ""
    return (f'<g transform="translate({cx - vw * k / 2:.2f},{cy - vh * k / 2:.2f}) scale({k:.5f}) '
            f'translate({-vx:g},{-vy:g})"{fill}>{body}</g>'), vw * k, vh * k


def text_block(a, W, cx, y_top, colour, max_w):
    """Headline (+ sub) centred, outlined. Returns (svg, height)."""
    if not a.headline:
        return "", 0
    f = Font(font_path(a.font))
    size = min(f.fit_size(a.headline, max_w, 0.01), (W * 0.11) / f.cap)
    w = f.width(a.headline, size, 0.01)
    cap = size * f.cap
    out = f'<path fill="{colour}" d="{f.path(a.headline, size, cx - w / 2, y_top + cap, 0.01)}"/>'
    h = cap
    if a.sub:
        fs = Font(font_path(a.sub_font))
        s2 = min(fs.fit_size(a.sub, max_w * 0.8, 0.12), (cap * 0.28) / fs.cap)
        w2 = fs.width(a.sub, s2, 0.12)
        c2 = s2 * fs.cap
        y2 = y_top + cap + cap * 0.35
        out += f'<path fill="{a.accent}" d="{fs.path(a.sub, s2, cx - w2 / 2, y2 + c2, 0.12)}"/>'
        h += cap * 0.35 + c2
    return out, h


def compose(a, layout, W, H, rnd):
    tall = H / W > 1.4
    wide = W / H > 1.4
    lock_d = a.vertical_dark if (tall and a.vertical_dark) else a.lockup_dark
    lock_l = a.vertical_light if (tall and a.vertical_light) else a.lockup_light
    m = min(W, H)
    parts = []
    bg = a.dark
    head_col = a.light
    lock = lock_d
    lw, lh = (m * 0.72, m * 0.42) if not tall else (W * 0.78, H * 0.3)
    lcx, lcy = W / 2, H * 0.42
    if layout == "crop":
        # giant symbol bleeds off one side; content sits in the free half
        side = rnd.choice(["end", "start"])
        big = m * rnd.uniform(1.3, 1.6)
        if wide:
            cx = W - big * 0.18 if side == "end" else big * 0.18
            cy = H * rnd.uniform(0.35, 0.65)
            lcx, lcy, lw, lh = (W * 0.3 if side == "end" else W * 0.7), H / 2, W * 0.42, H * 0.38
        else:
            big = m * rnd.uniform(1.15, 1.35)
            cx = W * rnd.uniform(0.35, 0.65)
            cy = -big * 0.14 if side == "end" else H + big * 0.14     # centre beyond the edge: only a slice shows
            lcx, lw, lh = W / 2, W * (0.8 if tall else 0.72), H * (0.27 if tall else 0.24)
            lcy = H * (0.72 if side == "end" else 0.28)
        s, _, _ = place(a.sym, cx, cy, big, big, a.accent)
        parts.append(f'<g opacity="{a.crop_opacity}">{s}</g>')
    elif layout == "split":
        r = m * 0.12
        up = rnd.random() > 0.5
        if up:
            parts.append(f'<path fill="{a.accent}" d="M{W * 0.55},0 H{W} V{H * 0.45} L{W * 0.55 + r},{r} Z"/>')
            parts.append(f'<path fill="{a.accent}" d="M0,{H * 0.55} L{W * 0.45 - r},{H - r} L{W * 0.45},{H} H0 Z"/>')
        else:
            parts.append(f'<path fill="{a.accent}" d="M0,0 H{W * 0.45} L{r},{H * 0.45 - r} L0,{H * 0.45} Z"/>')
            parts.append(f'<path fill="{a.accent}" d="M{W},{H * 0.55} V{H} H{W * 0.55} L{W - r},{H * 0.55 + r} Z"/>')
        lcy = H / 2 if not a.headline else H * 0.44
    elif layout == "frame":
        bg, lock, head_col = a.light, lock_l, a.dark
        d = W * 0.2 if not tall else W * 0.14
        notch = H * 0.5
        parts.append(f'<path fill="{a.accent}" d="M0,0 H{d} L{d * 0.35},{notch} L{d},{H} H0 Z"/>')
        parts.append(f'<path fill="{a.accent}" d="M{W},0 H{W - d} L{W - d * 0.35},{notch} L{W - d},{H} H{W} Z"/>')
        parts.append(f'<rect x="0" y="{notch - m * 0.006}" width="{d * 0.45}" height="{m * 0.012}" fill="{a.light}"/>')
        parts.append(f'<rect x="{W - d * 0.45}" y="{notch - m * 0.006}" width="{d * 0.45}" height="{m * 0.012}" '
                     f'fill="{a.light}"/>')
        lw = (W - 2 * d) * 0.82
    elif layout == "pattern":
        cell = m / rnd.choice([6, 7, 8])
        sym_tile, _, _ = place(a.sym, cell / 2, cell / 2, cell * 0.5, cell * 0.5, a.tone)
        parts.append(f'<defs><pattern id="pp" width="{cell:.2f}" height="{cell:.2f}" patternUnits="userSpaceOnUse" '
                     f'patternTransform="rotate({rnd.choice([0, -20, -30])})">{sym_tile}</pattern></defs>'
                     f'<rect width="{W}" height="{H}" fill="url(#pp)"/>')
        pad = m * 0.07
        parts.append(f'<rect x="{W / 2 - lw / 2 - pad}" y="{lcy - lh / 2 - pad}" width="{lw + 2 * pad}" '
                     f'height="{lh + 2 * pad}" fill="{a.dark}"/>')
    elif layout == "center":
        s, _, _ = place(a.sym, W * 0.5, H * 0.5, m * 1.1, m * 1.1, a.tone)
        parts.append(s)
        parts.append(f'<rect x="{W * 0.06}" y="{H * 0.06}" width="{W * 0.88}" height="{H * 0.88}" fill="none" '
                     f'stroke="{a.accent}" stroke-width="{m * 0.006}"/>')
    # measure lockup + headline as one group, centre it on (lcx, lcy) and keep it inside the safe margins
    _, _, real_h = place(lock, 0, 0, lw, lh)
    gap = m * 0.06
    _, th = text_block(a, W, lcx, 0, head_col, lw)
    group = real_h + (gap + th if th else 0)
    margin = m * 0.08
    top = min(max(lcy - group / 2, margin), H - margin - group)
    lg, _, _ = place(lock, lcx, top + real_h / 2, lw, lh)
    parts.append(lg)
    if th:
        tb, _ = text_block(a, W, lcx, top + real_h + gap, head_col, lw)
        parts.append(tb)
    return wrap_svg(W, H, "".join(parts), a.title, bg)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lockup-dark", required=True); ap.add_argument("--lockup-light", required=True)
    ap.add_argument("--vertical-dark"); ap.add_argument("--vertical-light")
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--accent", required=True); ap.add_argument("--dark", default="#1A1A1A")
    ap.add_argument("--light", default="#F5F5F5"); ap.add_argument("--tone", help="tone-on-tone colour (default: auto)")
    ap.add_argument("--headline", default=""); ap.add_argument("--sub", default="")
    ap.add_argument("--font", default="Anton"); ap.add_argument("--sub-font", default="Montserrat:700")
    ap.add_argument("--layouts", nargs="+", default=LAYOUTS); ap.add_argument("--sizes", nargs="+", default=SIZES)
    ap.add_argument("--crop-opacity", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--title", default="key visual")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    rd = lambda p: open(p, encoding="utf-8").read() if p else None  # noqa: E731
    a.lockup_dark, a.lockup_light = rd(a.lockup_dark), rd(a.lockup_light)
    a.vertical_dark, a.vertical_light = rd(a.vertical_dark), rd(a.vertical_light)
    a.sym = rd(a.symbol)
    if not a.tone:   # 6 % lighter than dark
        from common import hex_to_rgb, rgb_to_hex
        r, g, b = hex_to_rgb(a.dark)
        a.tone = rgb_to_hex((r + (255 - r) * 0.07, g + (255 - g) * 0.07, b + (255 - b) * 0.07))
    pngs = []
    for size in a.sizes:
        W, H = (int(v) for v in size.lower().split("x"))
        for lay in a.layouts:
            svg = compose(a, lay, W, H, random.Random(f"{a.seed}-{lay}"))
            p = f"{a.out}-{lay}-{W}x{H}"
            write(p + ".svg", svg)
            svg_to_png(svg=svg, out=p + ".png", width=W)
            pngs.append((p + ".png", f"{lay} {W}x{H}"))
    from PIL import Image, ImageDraw, ImageFont
    th = 360
    rows = []
    for size in a.sizes:
        rows.append([x for x in pngs if x[1].endswith(size)])
    widths = [sum(int(th * Image.open(p).width / Image.open(p).height) + 10 for p, _ in r) + 10 for r in rows]
    sheet = Image.new("RGB", (max(widths), len(rows) * (th + 34) + 10), "white")
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        f = ImageFont.load_default()
    y = 10
    for r in rows:
        x = 10
        for p, label in r:
            im = Image.open(p).convert("RGB")
            im = im.resize((int(th * im.width / im.height), th))
            sheet.paste(im, (x, y))
            d.text((x, y + th + 6), label, fill="black", font=f)
            x += im.width + 10
        y += th + 34
    sheet.save(a.out + "-sheet.png")
    print(a.out + "-sheet.png")


if __name__ == "__main__":
    main()
