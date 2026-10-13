"""Lockup builder: text block (outlined) + symbol + divider + co-brand, in every colourway, from one JSON spec.

Usage:
  python lockup.py spec.json            # writes <out_dir>/svg/*.svg, <out_dir>/png/*.png and <out_dir>/lockups.png
  python lockup.py --example            # prints an example spec

Spec (paths relative to the spec file):
{
  "name": "evento",
  "out_dir": "kit",
  "colors": {"accent": "#F8C100", "dark": "#1A1A1A", "light": "#F5F5F5"},
  "symbol": "symbol.svg",                    # optional; recoloured per colourway unless "symbol_keep_colors": true
  "symbol_scale": 1.0,                       # symbol height relative to block height (horizontal layout)
  "divider": true,                           # vertical rule between symbol and text
  "block": {"width": 700, "gap": 16, "align": "justify"},   # or omit width and give the first line a "cap"
  "lines": [
    {"text": "ENCONTRO", "font": "Anton", "cap": 120, "role": "primary", "tracking": 0.0},
    {"text": "NOME DA EMPRESA", "font": "Montserrat:700", "role": "secondary", "tracking": 0.5,
     "rule": "above"},                          # thin rule above the line (endorsement)
    {"text": "VIRTUAL", "font": "Montserrat:800", "role": "accent", "bar": true},        # knocked-out label bar
    {"text": "ONLINE", "font": "Anton", "role": "primary", "fill_bar": "right"},       # bar fills the rest of the line
    {"text": "FRIDAY", "font": "Montserrat:800", "role": "primary", "pill": true}       # outlined pill around the line
  ],
  "cobrand": {"svg": "marca-mae.svg", "scale": 0.55},   # optional: campaign | product lockup
  "layouts": ["horizontal", "vertical", "wordmark", "symbol"],
  "colorways": ["escuro", "positivo", "branco", "mono", "misto"]
}
Line sizing: a line with "cap" (cap height, px) is set at that size; other lines are fitted to the block width
("align": "justify") or keep "cap" and align left/center. "bar" lines get a filled bar with knocked-out text.
Roles: primary / secondary / accent — mapped to colours by the colourway (see COLORWAYS).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Font, contrast, font_path, recolor, svg_inner, svg_to_png, viewbox, wrap_svg, write  # noqa: E402

# role → colour key per colourway; "bg" is the preview background (None = transparent file, preview on it anyway)
COLORWAYS = {
    "escuro":   {"primary": "light", "secondary": "accent", "accent": "accent", "symbol": "accent", "rule": "light",
                 "bg": "dark"},
    "positivo": {"primary": "dark", "secondary": "dark", "accent": "dark", "symbol": "dark", "rule": "dark",
                 "bg": "light"},
    "branco":   {"primary": "light", "secondary": "light", "accent": "light", "symbol": "light", "rule": "light",
                 "bg": "dark"},
    "mono":     {"primary": "accent", "secondary": "accent", "accent": "accent", "symbol": "accent", "rule": "accent",
                 "bg": "dark"},
    "misto":    {"primary": "dark", "secondary": "dark", "accent": "accent", "symbol": "accent", "rule": "dark",
                 "bg": "light"},
}

EXAMPLE = __doc__.split("Spec (paths relative to the spec file):")[1].split("Line sizing")[0]


class Block:
    """Lays out the text lines; returns SVG fragments per role so colourways only swap fills."""

    def __init__(self, spec, base):
        self.spec = spec
        self.lines = spec["lines"]
        b = spec.get("block", {})
        self.gap = b.get("gap", 16)
        self.align = b.get("align", "justify")
        self.fonts = {}
        for ln in self.lines:
            ln.setdefault("tracking", 0.0)
            ln.setdefault("role", "primary")
            f = ln.get("font", "Montserrat:800")
            if f not in self.fonts:
                p = os.path.join(base, f) if os.path.exists(os.path.join(base, f)) else font_path(f)
                self.fonts[f] = Font(p)
        first = self.lines[0]
        f0 = self.fonts[first.get("font", "Montserrat:800")]
        if b.get("width"):
            self.width = b["width"]
        elif first.get("cap"):
            self.width = f0.width(first["text"], first["cap"] / f0.cap, first["tracking"])
        else:
            raise SystemExit("block.width or a 'cap' on the first line is required")
        self.layout()

    def layout(self):
        y = 0.0
        self.parts = []  # (role, kind, d) kind: fill | knock (evenodd with bar) | rule
        for i, ln in enumerate(self.lines):
            f = self.fonts[ln.get("font", "Montserrat:800")]
            tr = ln["tracking"]
            text = ln["text"]
            if ln.get("rule") == "above":
                t = max(1.5, self.width * 0.004)
                self.parts.append(("rule", "fill", f"M0,{y:.2f} h{self.width:.2f} v{t:.2f} h{-self.width:.2f} Z"))
                y += t + self.gap * 0.6
            if ln.get("bar"):
                cap = ln.get("cap") or self.width * 0.035
                pad = cap * 0.55
                bh = cap + 2 * pad
                size = cap / f.cap
                w = f.width(text, size, tr)
                if w > self.width - 2 * pad:          # shrink to fit the bar
                    size = f.fit_size(text, self.width - 2 * pad, tr)
                    cap, w = size * f.cap, f.width(text, size, tr)
                bw = self.width if self.align == "justify" or ln.get("full", True) else w + 2 * pad * 1.6
                bx = 0 if self.align != "center" else (self.width - bw) / 2
                tx = bx + (bw - w) / 2
                d = f.path(text, size, tx, y + (bh + cap) / 2, tr)
                bar = f"M{bx:.2f},{y:.2f} h{bw:.2f} v{bh:.2f} h{-bw:.2f} Z"
                self.parts.append((ln["role"], "knock", bar + " " + d))
                y += bh
            else:
                if ln.get("cap") and (i == 0 or self.align != "justify" or ln.get("fill_bar")):
                    size = ln["cap"] / f.cap
                else:
                    size = f.fit_size(text, self.width, tr)
                cap = size * f.cap
                if ln.get("pill"):   # leave room for the pill outline inside the block width
                    room = 2 * (cap * 0.45 + cap * 0.09)
                    if f.width(text, size, tr) + room > self.width:
                        size = f.fit_size(text, self.width - room * 1.02, tr)
                        cap = size * f.cap
                w = f.width(text, size, tr)
                if ln.get("fill_bar") and w > self.width * 0.92:   # too long for a bar: shrink to leave room
                    size = f.fit_size(text, self.width * 0.62, tr)
                    cap, w = size * f.cap, f.width(text, size, tr)
                x = {"center": (self.width - w) / 2, "right": self.width - w}.get(self.align, 0.0)
                if ln.get("fill_bar"):
                    x = 0.0 if ln["fill_bar"] == "right" else self.width - w
                pill = ln.get("pill")
                if pill:
                    t = cap * 0.09
                    px, py = cap * 0.45, cap * 0.38
                    if self.align == "justify":
                        x = (self.width - w) / 2
                    elif self.align != "center":
                        x = max(x, px + t)
                    y += py + t
                self.parts.append((ln["role"], "fill", f.path(text, size, x, y + cap, tr)))
                if ln.get("fill_bar"):
                    g = cap * 0.35
                    bx0 = (w + g) if ln["fill_bar"] == "right" else 0.0
                    bw = self.width - w - g
                    ch = cap * 0.45                     # chamfer
                    if bw > ch * 2:
                        if ln["fill_bar"] == "right":
                            d = (f"M{bx0 + ch:.2f},{y:.2f} H{self.width:.2f} V{y + cap - ch:.2f} "
                                 f"L{self.width - ch:.2f},{y + cap:.2f} H{bx0:.2f} V{y + ch:.2f} Z")
                        else:
                            d = (f"M{bx0:.2f},{y:.2f} H{bw - ch:.2f} L{bw:.2f},{y + ch:.2f} V{y + cap:.2f} "
                                 f"H{bx0 + ch:.2f} L{bx0:.2f},{y + cap - ch:.2f} Z")
                        self.parts.append((ln.get("bar_role", "accent"), "fill", d))
                if pill:
                    rx0, ry0 = x - px, y - py
                    rw, rh = w + 2 * px, cap + 2 * py
                    r = rh / 2
                    outer = _rrect(rx0 - t, ry0 - t, rw + 2 * t, rh + 2 * t, r + t)
                    inner = _rrect(rx0, ry0, rw, rh, r)
                    self.parts.append((ln.get("pill_role", ln["role"]), "knock", outer + " " + inner))
                    y += cap + py + t
                else:
                    y += cap
            y += self.gap
        self.height = y - self.gap

    def svg(self, colors, cw):
        out = []
        for role, kind, d in self.parts:
            c = colors[COLORWAYS[cw].get(role, COLORWAYS[cw]["primary"])]
            rule = ' fill-rule="evenodd"' if kind == "knock" else ""
            out.append(f'<path fill="{c}"{rule} d="{d}"/>')
        return "".join(out)


def _rrect(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return (f"M{x + r:.2f},{y:.2f} H{x + w - r:.2f} A{r:.2f},{r:.2f} 0 0 1 {x + w:.2f},{y + r:.2f} "
            f"V{y + h - r:.2f} A{r:.2f},{r:.2f} 0 0 1 {x + w - r:.2f},{y + h:.2f} H{x + r:.2f} "
            f"A{r:.2f},{r:.2f} 0 0 1 {x:.2f},{y + h - r:.2f} V{y + r:.2f} A{r:.2f},{r:.2f} 0 0 1 {x + r:.2f},{y:.2f} Z")


def placed(svg_text, x, y, h, colour=None):
    """Embed an SVG scaled to height h at (x, y); returns (fragment, width)."""
    vx, vy, vw, vh = viewbox(svg_text)
    k = h / vh
    body = svg_inner(recolor(svg_text, colour) if colour else svg_text)
    if colour:
        body = f'<g fill="{colour}">{body}</g>'
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({k:.5f}) translate({-vx:g},{-vy:g})">{body}</g>', vw * k


def build(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(spec_path))
    out = os.path.join(base, spec.get("out_dir", "kit"))
    name = spec.get("name", "logo")
    colors = spec["colors"]
    sym = open(os.path.join(base, spec["symbol"]), encoding="utf-8").read() if spec.get("symbol") else None
    keep = spec.get("symbol_keep_colors", False)
    cob = spec.get("cobrand")
    cob_svg = open(os.path.join(base, cob["svg"]), encoding="utf-8").read() if cob else None
    blk = Block(spec, base)
    H, W = blk.height, blk.width
    layouts = spec.get("layouts", ["horizontal", "vertical", "wordmark", "symbol"])
    cws = spec.get("colorways", list(COLORWAYS))
    files = []
    for cw in cws:
        role = COLORWAYS[cw]
        sc = None if (keep and cw in ("escuro", "misto")) else colors[role["symbol"]]
        for lay in layouts:
            if lay == "symbol":
                if not sym:
                    continue
                frag, sw = placed(sym, 0, 0, 512, sc)
                doc = wrap_svg(sw, 512, frag, name)
            elif lay == "wordmark":
                doc = wrap_svg(W, H, blk.svg(colors, cw), name)
            elif lay == "horizontal":
                parts, x = [], 0.0
                if sym:
                    sh = H * spec.get("symbol_scale", 1.0)
                    frag, sw = placed(sym, 0, (H - sh) / 2, sh, sc)
                    parts.append(frag)
                    x = sw + H * 0.14
                    if spec.get("divider"):
                        t = max(1.5, H * 0.012)
                        parts.append(f'<rect x="{x:.2f}" y="0" width="{t:.2f}" height="{H:.2f}" '
                                     f'fill="{colors[role["rule"]]}"/>')
                        x += t + H * 0.14
                parts.append(f'<g transform="translate({x:.2f},0)">{blk.svg(colors, cw)}</g>')
                x += W
                if cob_svg:
                    ch = H * cob.get("scale", 0.55)
                    t = max(1.5, H * 0.012)
                    x += H * 0.16
                    parts.append(f'<rect x="{x:.2f}" y="0" width="{t:.2f}" height="{H:.2f}" '
                                 f'fill="{colors[role["rule"]]}"/>')
                    x += t + H * 0.16
                    cc = None if (cob.get("keep_colors") and cw in ("escuro", "misto")) else colors[role["primary"]]
                    frag, cwid = placed(cob_svg, x, (H - ch) / 2, ch, cc)
                    parts.append(frag)
                    x += cwid
                doc = wrap_svg(x, H, "".join(parts), name)
            elif lay == "vertical":
                if not sym:
                    continue
                sh = H * spec.get("stack_symbol", 0.9)
                vx, vy, vw, vh = viewbox(sym)
                sw = vw * sh / vh
                frag, _ = placed(sym, (W - sw) / 2, 0, sh, sc)
                doc = wrap_svg(W, sh + H * 0.18 + H, frag +
                               f'<g transform="translate(0,{sh + H * 0.18:.2f})">{blk.svg(colors, cw)}</g>', name)
            else:
                continue
            p = os.path.join(out, "svg", f"{name}-{lay}-{cw}.svg")
            write(p, doc)
            files.append((p, colors[role["bg"]] if role.get("bg") else None, cw, lay))
    # previews
    previews = []
    for p, bg, cw, lay in files:
        vx, vy, vw, vh = viewbox(open(p, encoding="utf-8").read())
        k = 1600 / max(vw, vh)
        png = p.replace(os.sep + "svg" + os.sep, os.sep + "png" + os.sep)[:-4] + ".png"
        svg_to_png(svg_path=p, out=png, width=vw * k)
        previews.append((png, bg, f"{lay} · {cw}"))
    sheet(previews, os.path.join(out, f"{name}-lockups.png"))
    # contrast warnings
    for cw in cws:
        role = COLORWAYS[cw]
        bg = colors[role["bg"]]
        for r in ("primary", "accent", "symbol"):
            c = colors[role[r]]
            if c != bg and contrast(c, bg) < 3:
                print(f"aviso: {cw}: {r} {c} sobre {bg} tem contraste {contrast(c, bg):.1f}:1 (<3)")
    print(f"{len(files)} SVGs em {os.path.join(out, 'svg')}")


def sheet(previews, out, cols=3, cell=(520, 300)):
    from PIL import Image, ImageDraw, ImageFont
    import io
    rows = -(-len(previews) // cols)
    W, H = cols * (cell[0] + 12) + 12, rows * (cell[1] + 34) + 12
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        f = ImageFont.load_default()
    for n, (png, bg, label) in enumerate(previews):
        x, y = 12 + (n % cols) * (cell[0] + 12), 12 + (n // cols) * (cell[1] + 34)
        tile = Image.new("RGB", cell, bg or "#8C8C8C")
        lg = Image.open(png).convert("RGBA")
        lg.thumbnail((cell[0] - 60, cell[1] - 60))
        tile.paste(lg, ((cell[0] - lg.width) // 2, (cell[1] - lg.height) // 2), lg)
        im.paste(tile, (x, y))
        d.text((x, y + cell[1] + 8), label, fill=(40, 40, 40), font=f)
    im.save(out)
    print(f"folha: {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
    elif sys.argv[1] == "--example":
        print(EXAMPLE)
    else:
        build(sys.argv[1])
