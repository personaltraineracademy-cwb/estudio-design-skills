"""Compositor: build design pieces (posts, banners, ads, posters, thumbnails) from layers, in every size at once.

Usage:
  python compose.py peca.json            # → <out_dir>/<name>-<WxH>.png, -sheet.png, and -express.html per size
  python compose.py --example            # example spec

Spec (paths relative to the spec file; boxes are [x, y, w, h] in % of the canvas):
{
  "name": "bf-professor", "out_dir": "pecas",
  "sizes": ["1080x1080", "1080x1350", "1080x1920", "1920x1080"],
  "fonts": {"display": "Anton", "body": "Montserrat:700"},
  "layers": [
    {"type": "bg", "color": "#0A0A0A"},
    {"type": "bg", "gradient": ["#0A0A0A", "#2A2A00"], "angle": 160},
    {"type": "image", "src": "fumaca.png", "box": [0, 0, 100, 100], "fit": "cover", "opacity": 0.6, "blend": "screen"},
    {"type": "svg", "src": "simbolo.svg", "box": [55, -10, 70, 70], "color": "#FF5A1F", "rotate": -12, "opacity": 0.9},
    {"type": "image", "src": "professor-recorte.png", "box": [30, 18, 70, 82], "fit": "contain", "align": "center bottom",
     "shadow": true},
    {"type": "shape", "shape": "pill", "box": [6, 78, 40, 7], "fill": "#FF5A1F"},
    {"type": "text", "text": "ATÉ 50% OFF", "font": "display", "color": "#FFFFFF", "box": [6, 52, 50, 20],
     "fit": "width", "align": "left", "valign": "bottom", "tracking": 0.01, "upper": true},
    {"type": "text", "text": "SÓ ATÉ DOMINGO", "font": "body", "color": "#0A0A0A", "box": [6, 78, 40, 7],
     "fit": "box", "align": "center", "valign": "middle", "tracking": 0.12},
    {"type": "logo", "src": "lockup.svg", "box": [6, 5, 40, 12], "align": "left top"},
    {"type": "fx", "chain": ["grain:0.05", "vignette:0.35"]}
  ],
  "overrides": {"1080x1920": {"4": {"box": [5, 35, 90, 65]}, "6": {"box": [6, 18, 88, 14]}}}
}
Layer types: bg (color | gradient | image) · image (photo/cut-out: fit contain|cover, align, shadow, blend, opacity,
rotate, flip) · svg (vector element, optional single "color") · logo (= svg, never recoloured) · shape (rect | pill |
circle | ring; fill, stroke, radius) · text (fit: width | box | none with "size" in px; multi-line with "\\n") · fx
(raster effects from fx.py, applied after rendering).
Text is real live text (editable after Adobe Express import); sizes are fitted in Python with the real font metrics.
"""
import base64
import copy
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Font, font_path, html_screenshot, recolor, svg_inner, viewbox  # noqa: E402

EXAMPLE = __doc__.split("Spec (paths relative to the spec file; boxes are [x, y, w, h] in % of the canvas):")[1] \
    .split("Layer types:")[0]


def data_uri(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "svg": "image/svg+xml", "webp": "image/webp",
            "ttf": "font/ttf", "otf": "font/otf"}.get(ext, "image/png")
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


def px_box(box, W, H):
    x, y, w, h = box
    return x * W / 100, y * H / 100, w * W / 100, h * H / 100


def fit_text(font, lines, bw, bh, mode, tracking, line_h, size=None):
    """Return font-size (px) so the text block fits the box (fontTools metrics)."""
    if mode == "none" and size:
        return size
    widest = max(font.width(l, 1.0, tracking) for l in lines) or 1
    s_w = bw / widest
    if mode == "width":
        return s_w
    n = len(lines)
    s_h = bh / (font.cap * 1.0 + (n - 1) * line_h + 0.25)   # cap + leading + a little descender room
    return min(s_w, s_h)


def layer_html(L, i, W, H, base, fonts, embed):
    t = L["type"]
    style = []
    if "box" in L:
        x, y, w, h = px_box(L["box"], W, H)
        style += [f"left:{x:.1f}px", f"top:{y:.1f}px", f"width:{w:.1f}px", f"height:{h:.1f}px"]
    if L.get("rotate"):
        style.append(f"transform:rotate({L['rotate']}deg)")
    if "opacity" in L:
        style.append(f"opacity:{L['opacity']}")
    if L.get("blend"):
        style.append(f"mix-blend-mode:{L['blend']}")
    src = lambda p: data_uri(os.path.join(base, p)) if embed else "file:///" + os.path.abspath(  # noqa: E731
        os.path.join(base, p)).replace("\\", "/")
    if t == "bg":
        if L.get("gradient"):
            g = ", ".join(L["gradient"])
            bg = f"linear-gradient({L.get('angle', 180)}deg, {g})"
        elif L.get("image"):
            bg = f"url('{src(L['image'])}') center/cover no-repeat"
        else:
            bg = L.get("color", "#000")
        return f'<div class="layer" id="L{i}" style="inset:0;background:{bg};{";".join(style)}"></div>'
    if t == "image":
        fit = L.get("fit", "contain")
        pos = L.get("align", "center center")
        filt = "filter:drop-shadow(0 30px 40px rgba(0,0,0,.45));" if L.get("shadow") else ""
        flip = "transform:scaleX(-1);" if L.get("flip") else ""
        return (f'<div class="layer" id="L{i}" style="{";".join(style)}"><img src="{src(L["src"])}" '
                f'style="width:100%;height:100%;object-fit:{fit};object-position:{pos};{filt}{flip}"></div>')
    if t in ("svg", "logo"):
        s = open(os.path.join(base, L["src"]), encoding="utf-8").read()
        if t == "svg" and L.get("color"):
            s = recolor(s, L["color"])
        vx, vy, vw, vh = viewbox(s)
        par = {"left top": "xMinYMin", "left": "xMinYMid", "right": "xMaxYMid", "top": "xMidYMin",
               "bottom": "xMidYMax", "left bottom": "xMinYMax", "right top": "xMaxYMin"}.get(L.get("align", ""),
                                                                                           "xMidYMid")
        fill = f' fill="{L["color"]}"' if (t == "svg" and L.get("color")) else ""
        return (f'<div class="layer" id="L{i}" style="{";".join(style)}"><svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="{vx:g} {vy:g} {vw:g} {vh:g}" preserveAspectRatio="{par} meet" width="100%" '
                f'height="100%" style="overflow:visible"{fill}>{svg_inner(s)}</svg></div>')
    if t == "shape":
        x, y, w, h = px_box(L["box"], W, H)
        sh = L.get("shape", "rect")
        r = {"pill": h / 2, "circle": "50%", "ring": "50%"}.get(sh, L.get("radius", 0))
        r = f"{r}px" if isinstance(r, (int, float)) else r
        fill = "transparent" if sh == "ring" else L.get("fill", "#000")
        border = ""
        if sh == "ring" or L.get("stroke"):
            sw = L.get("stroke_width", max(2, min(w, h) * 0.06))
            border = f"border:{sw:.1f}px solid {L.get('stroke', L.get('fill', '#000'))};"
        return f'<div class="layer" id="L{i}" style="{";".join(style)};background:{fill};border-radius:{r};{border}"></div>'
    if t == "text":
        x, y, w, h = px_box(L["box"], W, H)
        f = fonts[L.get("font", "display")]
        text = L["text"].upper() if L.get("upper") else L["text"]
        lines = text.split("\n")
        tr = L.get("tracking", 0.0)
        lh = L.get("line", 1.0)
        size = fit_text(f["font"], lines, w, h, L.get("fit", "box"), tr, lh, L.get("size"))
        size *= L.get("scale", 0.98)
        just = {"left": "flex-start", "center": "center", "right": "flex-end"}[L.get("align", "left")]
        val = {"top": "flex-start", "middle": "center", "bottom": "flex-end"}[L.get("valign", "middle")]
        body = "<br>".join(html.escape(l) for l in lines)
        return (f'<div class="layer" id="L{i}" style="{";".join(style)};display:flex;flex-direction:column;'
                f'justify-content:{val};align-items:{just}"><div style="font-family:\'{f["family"]}\';'
                f'font-size:{size:.1f}px;line-height:{lh};letter-spacing:{tr}em;color:{L.get("color", "#fff")};'
                f'text-align:{L.get("align", "left")};white-space:nowrap">{body}</div></div>')
    return ""


def build(spec_path, sizes_only=None):
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(spec_path))
    out = os.path.join(base, spec.get("out_dir", "pecas"))
    os.makedirs(out, exist_ok=True)
    name = spec.get("name", "peca")
    fonts = {}
    for key, fspec in spec.get("fonts", {"display": "Anton", "body": "Montserrat:700"}).items():
        p = os.path.join(base, fspec) if os.path.exists(os.path.join(base, fspec)) else font_path(fspec)
        fonts[key] = {"font": Font(p), "path": p, "family": f"bs-{key}"}
    pngs = []
    for size in spec.get("sizes", ["1080x1080"]):
        if sizes_only and size not in sizes_only:
            continue
        W, H = (int(v) for v in size.lower().split("x"))
        layers = copy.deepcopy(spec["layers"])
        for idx, patch in spec.get("overrides", {}).get(size, {}).items():
            layers[int(idx)].update(patch)
        fx = [c for L in layers if L["type"] == "fx" for c in L.get("chain", [])]
        for embed in (False, True):
            ff = "".join(f"@font-face{{font-family:'{v['family']}';src:url('"
                         f"{data_uri(v['path']) if embed else 'file:///' + v['path'].replace(chr(92), '/')}')}}"
                         for v in fonts.values())
            body = "".join(layer_html(L, i, W, H, base, fonts, embed) for i, L in enumerate(layers) if L["type"] != "fx")
            doc = (f"<!doctype html><html><head><meta charset='utf-8'>"
                   f"<meta name='hz:slide-selector' content='.slide'><style>{ff}"
                   f"*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:{W}px;height:{H}px;overflow:hidden;"
                   f"background:#000}}.slide{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}"
                   f".layer{{position:absolute}}</style></head><body><div class='slide' data-canvas-width='{W}' "
                   f"data-canvas-height='{H}'>{body}</div></body></html>")
            hp = os.path.join(out, f"{name}-{W}x{H}{'-express' if embed else ''}.html")
            open(hp, "w", encoding="utf-8").write(doc)
            if not embed:
                png = os.path.join(out, f"{name}-{W}x{H}.png")
                html_screenshot(hp, png, W, H)
                if fx:
                    import fx as fxmod
                    from PIL import Image
                    im = Image.open(png).convert("RGB")
                    for c in fx:
                        n, _, args = c.partition(":")
                        im = fxmod.FX[n](im, *[a for a in args.split(",") if a]) if args else fxmod.FX[n](im)
                    im.save(png)
                os.remove(hp)
                pngs.append(png)
                print(png)
    if len(pngs) > 1:
        from PIL import Image
        th = 420
        ims = [Image.open(p).convert("RGB") for p in pngs]
        ims = [im.resize((int(th * im.width / im.height), th)) for im in ims]
        s = Image.new("RGB", (sum(i.width for i in ims) + 10 * (len(ims) + 1), th + 20), "white")
        x = 10
        for im in ims:
            s.paste(im, (x, 10))
            x += im.width + 10
        s.save(os.path.join(out, f"{name}-sheet.png"))
        print(os.path.join(out, f"{name}-sheet.png"))
    print("versões para Adobe Express: *-express.html (fontes e imagens embutidas)")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
    elif sys.argv[1] == "--example":
        print(EXAMPLE)
    else:
        build(sys.argv[1], sys.argv[2:] or None)
