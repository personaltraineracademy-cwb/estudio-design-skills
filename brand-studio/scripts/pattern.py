"""Seamless brand patterns from a symbol or a word.

Usage:
  python pattern.py --motif symbol.svg --mode brick --fg "#F8C100" --bg "#1A1A1A" -o out/pattern
  python pattern.py --word "BLACK" --font Anton --mode diagonal --angle -30 --fg "#2A2A2A" --bg "#1A1A1A" -o out/p2
  python pattern.py --motif symbol.svg --all --fg "#F8C100" --bg "#1A1A1A" -o out/explore   # every mode → one sheet

Modes:  grid · brick (half-offset rows) · alternate (0°/180° checker) · mirror (mirrored checker) ·
        scatter (seeded random rotation/position, seamless) · diagonal (grid rotated by --angle) · stripes (word rows,
        alternating direction)
Options: --cell 120 (tile cell px) --scale 0.55 (motif size in cell) --angle 0 --seed 1 --fg2 "#hex" (second motif
         colour for alternate cells) --opacity 1 --size 1080x1080 (canvas)
Writes <o>-tile.svg (seamless tile, use as a swatch/pattern fill), <o>.svg + <o>.png (filled canvas).
Tone-on-tone (fg close to bg) is the house way to use patterns behind logos; full contrast for merch/packaging.
"""
import argparse
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Font, font_path, recolor, svg_inner, svg_to_png, viewbox, wrap_svg, write  # noqa: E402

MODES = ["grid", "brick", "alternate", "mirror", "scatter", "diagonal", "stripes"]


def motif_def(args):
    """Return (inner_svg, w, h) of the motif normalised to height 100."""
    if args.word:
        f = Font(font_path(args.font))
        size = 100 / f.cap
        w = f.width(args.word, size, args.tracking)
        return f'<path d="{f.path(args.word, size, 0, 100, args.tracking)}"/>', w, 100.0
    s = open(args.motif, encoding="utf-8").read()
    vx, vy, vw, vh = viewbox(s)
    k = 100 / vh
    inner = svg_inner(recolor(s, "currentColor"))
    return f'<g transform="scale({k:.5f}) translate({-vx:g},{-vy:g})">{inner}</g>', vw * k, 100.0


def use(cx, cy, scale, rot, colour, mw, mh, flip=False):
    fx = -1 if flip else 1
    return (f'<g transform="translate({cx:.2f},{cy:.2f}) rotate({rot:.2f}) scale({scale * fx:.4f},{scale:.4f}) '
            f'translate({-mw / 2:.2f},{-mh / 2:.2f})" fill="{colour}" color="{colour}"><use href="#m"/></g>')


def tile(args, mode, mw, mh):
    c = args.cell
    k = args.scale * c / max(mw, mh)
    if mode == "stripes":
        k = args.scale * c / mh
    fg, fg2 = args.fg, args.fg2 or args.fg
    els = []
    if mode in ("grid", "diagonal"):
        tw, th = c, c
        els.append(use(c / 2, c / 2, k, 0, fg, mw, mh))
    elif mode == "brick":
        tw, th = c, 2 * c
        els += [use(c / 2, c / 2, k, 0, fg, mw, mh), use(0, 1.5 * c, k, 0, fg2, mw, mh),
                use(c, 1.5 * c, k, 0, fg2, mw, mh)]
    elif mode in ("alternate", "mirror"):
        tw, th = 2 * c, 2 * c
        for i in range(2):
            for j in range(2):
                odd = (i + j) % 2
                rot = 180 if (mode == "alternate" and odd) else 0
                els.append(use(c / 2 + i * c, c / 2 + j * c, k, rot, fg2 if odd else fg, mw, mh,
                               flip=(mode == "mirror" and odd)))
    elif mode == "scatter":
        rnd = random.Random(args.seed)
        tw = th = 4 * c
        pts = []
        tries = 0
        while len(pts) < 14 and tries < 4000:   # Poisson-ish: keep a minimum distance (wrapped)
            tries += 1
            x, y = rnd.uniform(0, tw), rnd.uniform(0, th)
            if all(min(abs(x - px), tw - abs(x - px)) ** 2 + min(abs(y - py), th - abs(y - py)) ** 2 > (0.95 * c) ** 2
                   for px, py in pts):
                pts.append((x, y))
        for x, y in pts:
            rot = rnd.choice([0, 15, 30, 45, -15, -30, -45, 90, 180])
            sc = k * rnd.uniform(0.75, 1.1)
            col = fg if rnd.random() > 0.3 else fg2
            for dx in (-tw, 0, tw):          # wrap copies so the tile is seamless
                for dy in (-th, 0, th):
                    els.append(use(x + dx, y + dy, sc, rot, col, mw, mh))
    elif mode == "stripes":
        w = mw * k
        gap = c * 0.35
        tw, th = w + gap, 2 * c
        els += [use(tw / 2, c / 2, k, 0, fg, mw, mh), use(tw / 2, 1.5 * c, k, 180, fg2, mw, mh)]
    else:
        raise SystemExit(f"modo desconhecido: {mode}")
    return tw, th, "".join(els)


def build(args, mode, out):
    md, mw, mh = motif_def(args)
    tw, th, body = tile(args, mode, mw, mh)
    defs = f'<defs><g id="m">{md}</g></defs>'
    op = f' opacity="{args.opacity}"' if args.opacity < 1 else ""
    tile_svg = wrap_svg(tw, th, f"{defs}<g{op}>{body}</g>", "pattern tile", args.bg)
    write(out + "-tile.svg", tile_svg)
    W, H = (int(v) for v in args.size.lower().split("x"))
    ang = args.angle if mode in ("diagonal", "stripes", "scatter") else 0
    if mode == "diagonal" and not ang:
        ang = -30
    pat = (f'<defs><g id="m">{md}</g><pattern id="p" width="{tw:.2f}" height="{th:.2f}" '
           f'patternUnits="userSpaceOnUse" patternTransform="rotate({ang})"><g{op}>{body}</g></pattern></defs>'
           f'<rect width="{W}" height="{H}" fill="{args.bg}"/><rect width="{W}" height="{H}" fill="url(#p)"/>')
    write(out + ".svg", wrap_svg(W, H, pat, "pattern"))
    svg_to_png(svg_path=out + ".svg", out=out + ".png", width=W)
    return out + ".png"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--motif"); ap.add_argument("--word"); ap.add_argument("--font", default="Anton")
    ap.add_argument("--tracking", type=float, default=0.02)
    ap.add_argument("--mode", default="grid", choices=MODES); ap.add_argument("--all", action="store_true")
    ap.add_argument("--fg", default="#1A1A1A"); ap.add_argument("--fg2"); ap.add_argument("--bg", default="#F5F5F5")
    ap.add_argument("--cell", type=float, default=120); ap.add_argument("--scale", type=float, default=0.55)
    ap.add_argument("--angle", type=float, default=0); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--opacity", type=float, default=1.0); ap.add_argument("--size", default="1080x1080")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()
    if not (args.motif or args.word):
        raise SystemExit("use --motif arquivo.svg ou --word TEXTO")
    if args.all:
        from PIL import Image, ImageDraw, ImageFont
        pngs = [(m, build(args, m, f"{args.out}-{m}")) for m in MODES if not (m == "stripes" and not args.word)]
        cell = 360
        sheet = Image.new("RGB", (len(pngs) * (cell + 10) + 10, cell + 40), "white")
        d = ImageDraw.Draw(sheet)
        try:
            f = ImageFont.truetype("arial.ttf", 16)
        except OSError:
            f = ImageFont.load_default()
        for i, (m, p) in enumerate(pngs):
            im = Image.open(p).convert("RGB").resize((cell, cell))
            sheet.paste(im, (10 + i * (cell + 10), 10))
            d.text((12 + i * (cell + 10), cell + 16), m, fill="black", font=f)
        sheet.save(args.out + "-modos.png")
        print(args.out + "-modos.png")
    else:
        print(build(args, args.mode, args.out))


if __name__ == "__main__":
    main()
