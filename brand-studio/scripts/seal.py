"""Circular seal: text on the arc around a centre symbol (e.g. endorsement or sub-brand seals).

Usage:
  python seal.py --top "CLUBE DE CORRIDA · NOITE" --bottom "DESDE 2024" --symbol sym.svg --font "Montserrat:800" \
                 --style ring --fg "#1A1A1A" --bg "#F5F5F5" -o out/selo
  python seal.py --top "NOME DA EMPRESA" --loop --symbol sym.svg --style solid --fg "#2F6BFF" -o out/selo2

Styles:
  ring    thin double ring, text in the band                  solid   filled ring, text knocked out
  open    text only, no rings (bare arc)                         stamp   ring + inner ring + star separators
--loop     repeat the top text all the way round (separator " · " added automatically)
--sep "★"  separator glyph between top and bottom texts (default "•")
Writes <o>.svg/.png (fg on transparent) plus <o>-<colourway>.png previews on --bg and inverted.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Font, font_path, recolor, svg_inner, svg_to_png, viewbox, wrap_svg, write  # noqa: E402


def circle(cx, cy, r):
    return f"M{cx - r:.2f},{cy:.2f} a{r:.2f},{r:.2f} 0 1,0 {2 * r:.2f},0 a{r:.2f},{r:.2f} 0 1,0 {-2 * r:.2f},0 Z"


def separator(kind, x, y, cap):
    """Geometric separator so it never depends on the font: ★/* star, ◆ diamond, anything else a dot."""
    import math
    if kind in ("★", "*", "star"):
        R, r = cap * 0.34, cap * 0.14
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = R if i % 2 == 0 else r
            pts.append(f"{x + rr * math.cos(a):.2f},{y + rr * math.sin(a):.2f}")
        return "M" + " L".join(pts) + " Z"
    if kind in ("◆", "diamond"):
        d = cap * 0.22
        return f"M{x:.2f},{y - d:.2f} L{x + d:.2f},{y:.2f} L{x:.2f},{y + d:.2f} L{x - d:.2f},{y:.2f} Z"
    return circle(x, y, cap * 0.12)


def build(a):
    S = 1000.0
    c = S / 2
    f = Font(font_path(a.font))
    R = S / 2 - 6                       # outer edge
    band = S * a.band                   # text band thickness
    cap = band * 0.52
    size = cap / f.cap
    t = S * 0.006                       # thin rule
    parts_fill, parts_knock = [], []
    r_text_out = R - (band - cap) / 2 - cap   # baseline radius for top text (glyphs grow outward)
    r_text_in = R - (band - cap) / 2          # baseline radius for bottom text (glyphs grow inward)
    if a.style in ("ring", "stamp"):
        parts_fill.append(circle(c, c, R) + " " + circle(c, c, R - t))
        parts_fill.append(circle(c, c, R - band) + " " + circle(c, c, R - band - t))
    if a.style == "stamp":
        parts_fill.append(circle(c, c, R - band - S * 0.025) + " " + circle(c, c, R - band - S * 0.025 - t))
    import math
    circ = 2 * math.pi * r_text_out
    tr = a.tracking
    if a.loop:
        unit = a.top.strip() + f" {a.sep} "
        n = max(1, int(circ / f.width(unit, size, tr)))
        text = unit * n
        # spread to close the loop exactly
        w = f.width(text, size, tr)
        extra = (circ - w) / (len(text) * size)
        top_d = f.path_on_circle(text, size, c, c, r_text_out, -90, tr + extra, outside=True, centre=True)
        bottom_d = ""
    else:
        top_d = f.path_on_circle(a.top, size, c, c, r_text_out, -90, tr, outside=True)
        bottom_d = f.path_on_circle(a.bottom, size, c, c, r_text_in, 90, tr, outside=False) if a.bottom else ""
        if a.bottom and a.sep:
            r_mid = (r_text_out + r_text_in) / 2
            for ang in (math.pi, 0.0):          # separators at 9 and 3 o'clock, drawn (fonts may lack ★)
                parts_fill.append(separator(a.sep, c + r_mid * math.cos(ang), c + r_mid * math.sin(ang), cap))
    text_d = top_d + " " + bottom_d
    inner_r = R - band - (S * 0.05 if a.style == "stamp" else S * 0.03)
    sym = ""
    if a.symbol:
        s = open(a.symbol, encoding="utf-8").read()
        vx, vy, vw, vh = viewbox(s)
        box = inner_r * 2 * a.symbol_scale
        k = box / max(vw, vh)
        sym = (f'<g transform="translate({c - vw * k / 2:.2f},{c - vh * k / 2:.2f}) scale({k:.5f}) '
               f'translate({-vx:g},{-vy:g})" fill="{a.fg}">{svg_inner(recolor(s, a.fg))}</g>')
    if a.style == "solid":
        ring = circle(c, c, R) + " " + circle(c, c, R - band)
        body = f'<path fill="{a.fg}" fill-rule="evenodd" d="{ring} {text_d}"/>'
    else:
        body = f'<path fill="{a.fg}" d="{text_d}"/>'
    body += "".join(f'<path fill="{a.fg}" fill-rule="evenodd" d="{d}"/>' for d in parts_fill) + sym
    svg = wrap_svg(S, S, body, a.title or a.top)
    write(a.out + ".svg", svg)
    svg_to_png(svg=svg, out=a.out + ".png", width=1000)
    svg_to_png(svg=svg, out=a.out + "-fundo.png", width=1000, background=a.bg)
    inv = recolor(svg, a.bg)
    write(a.out + "-invertido.svg", inv)
    svg_to_png(svg=inv, out=a.out + "-invertido.png", width=1000, background=a.fg)
    print(a.out + ".svg")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", required=True); ap.add_argument("--bottom", default="")
    ap.add_argument("--symbol"); ap.add_argument("--symbol-scale", type=float, default=0.62)
    ap.add_argument("--font", default="Montserrat:800"); ap.add_argument("--tracking", type=float, default=0.08)
    ap.add_argument("--style", default="ring", choices=["ring", "solid", "open", "stamp"])
    ap.add_argument("--band", type=float, default=0.13, help="band thickness as fraction of diameter")
    ap.add_argument("--loop", action="store_true"); ap.add_argument("--sep", default="•")
    ap.add_argument("--fg", default="#1A1A1A"); ap.add_argument("--bg", default="#F5F5F5")
    ap.add_argument("--title"); ap.add_argument("-o", "--out", required=True)
    build(ap.parse_args())


if __name__ == "__main__":
    main()
