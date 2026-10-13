"""Graphic-element engine: derive an exclusive family of graphic devices from a brand's own primitives (symbol,
letters of the name, any SVG) with a shape grammar — then explore variations, pick, and build masters.

Usage:
  python elements.py dna simbolo.svg [-o dna.json]                  # geometry DNA: angles, stroke, symmetry, fill…
  python elements.py letters "Anton" "AR" -o prim/letras.svg          # letters of the name as a primitive (curves)
  python elements.py explore simbolo.svg -o explorar/ [--ops all] [--n 6] [--seed 7] [--fg #111 --bg #EEE]
        → one SVG per variation + explorar/folha.png (look at it, pick, note the params printed in each label)
  python elements.py make simbolo.svg --op contour --params '{"n":7,"step":0.035}' -o elementos/eco.svg [--fg ..]
  python elements.py build <brand_dir>                               # every entry of brand.json "devices" →
        elementos/<id>.svg (master, ink) + elementos/<id>-<colorway>.png previews + elementos/folha.png
        colorways = "<fg>-<bg>" roles (brand-ink, brand-paper, ink-paper, accent-ink, brand.300-ink…); default = the
        pairs that read (contrast ≥ 1.8). dna.json comes from the main primitive ("main": true in primitives[]).

Operations (the grammar; params in brackets):
  crop      supergraphic — primitive enlarged and cropped by the frame        [scale, cx, cy, rot, aspect]
  contour   echo lines — concentric offsets outward/inward                    [n, step, side=out|in|both, join]
  bands     alternate filled offset bands (topographic)                       [n, step]
  slice     cut into strips with gaps; optional shear/shift                   [n, angle, gap, shift]
  hatch     engraving — parallel lines clipped by the shape                   [spacing, angle, weight, cross]
  halftone  dots inside the shape, size by distance to edge or gradient       [cell, mode=edge|linear, angle]
  repeat    rhythm — step-and-repeat with scale decay / radial array          [mode=linear|radial|grid, n, ...]
  stack     extrusion — offset copies form a solid block (flat 3D)            [n, dx, dy]
  modules   kit of parts — shape cut by a grid, pieces exploded/recombined   [cols, rows, spread, rot]
  outline   line version of the shape (for icons/frames)                      [weight]
  morph     interpolation between two primitives (needs --to other.svg)        [steps]
  frame     corner brackets / edges derived from the primitive's angles        [len, weight]
Geometry is read by rendering the SVG and tracing it with sub-pixel accuracy (handles any SVG: strokes, transforms,
groups). Outputs are clean filled paths (fill-rule evenodd) or strokes — never <text>/<image>.
"""
import argparse
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import (contrast, font, load_brand, sheet, svg_to_png, wrap_svg, write)  # noqa: E402

UNIT = 1000.0          # primitives are normalised to fit a 1000-unit box
RES = 2400             # trace resolution (px)


# ------------------------------------------------------------------ geometry IO
def svg_geometry(svg_path_or_text, res=RES):
    """SVG → shapely (Multi)Polygon in a UNIT box (y down), traced from the rendered alpha with sub-pixel contours."""
    import io
    import numpy as np
    from PIL import Image
    from shapely.geometry import Polygon
    from skimage import measure
    txt = open(svg_path_or_text, encoding="utf-8").read() if os.path.isfile(svg_path_or_text) else svg_path_or_text
    png = svg_to_png(txt, width=res)
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    a = np.asarray(im)[:, :, 3].astype("float32") / 255.0
    if a.max() < 0.5:
        raise SystemExit("primitive renders empty (white on transparent? use a solid fill)")
    a = np.pad(a, 2)
    rings = measure.find_contours(a, 0.5)
    polys = []
    for r in rings:
        if len(r) < 8:
            continue
        p = Polygon([(x - 2, y - 2) for y, x in r]).buffer(0)
        if p.area > 4:
            polys.append(p)
    polys.sort(key=lambda p: -p.area)
    geom = None
    for p in polys:                                   # even-odd: holes cancel, islands in holes come back
        geom = p if geom is None else geom.symmetric_difference(p)
    geom = geom.buffer(0)
    minx, miny, maxx, maxy = geom.bounds
    k = UNIT / max(maxx - minx, maxy - miny)
    from shapely import affinity
    geom = affinity.translate(geom, -minx, -miny)
    geom = affinity.scale(geom, k, k, origin=(0, 0))
    return geom.simplify(0.35 * k * 0 + UNIT / 4000, preserve_topology=True)


def polys_of(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]


def lines_of(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "MultiLineString":
        return list(g.geoms)
    if g.geom_type == "GeometryCollection":
        return [x for x in g.geoms if x.geom_type == "LineString"]
    return []


def d_of(g, prec=1):
    """Polygons → path data (evenodd); LineStrings → open subpaths."""
    out = []
    f = f"{{:.{prec}f}}"

    def ring(coords, close=True):
        pts = list(coords)
        if close and len(pts) > 1 and pts[0] == pts[-1]:
            pts = pts[:-1]
        s = "M" + " L".join(f.format(x) + " " + f.format(y) for x, y in pts)
        return s + ("Z" if close else "")
    for p in polys_of(g):
        out.append(ring(p.exterior.coords))
        out.extend(ring(i.coords) for i in p.interiors)
    for ln in lines_of(g):
        out.append(ring(ln.coords, close=False))
    return "".join(out)


def path_el(g, fill=None, stroke=None, width=None, cap="butt", join="miter", opacity=None):
    d = d_of(g)
    if not d:
        return ""
    if stroke:
        return (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width:.2f}" stroke-linecap="{cap}" '
                f'stroke-linejoin="{join}"' + (f' opacity="{opacity}"' if opacity else "") + "/>")
    return f'<path d="{d}" fill="{fill}" fill-rule="evenodd"' + (f' opacity="{opacity}"' if opacity else "") + "/>"


def fit(g, box):
    """Scale/translate geometry to fit box (x, y, w, h), centred."""
    from shapely import affinity
    minx, miny, maxx, maxy = g.bounds
    bw, bh = maxx - minx, maxy - miny
    x, y, w, h = box
    k = min(w / bw, h / bh)
    g = affinity.translate(g, -minx - bw / 2, -miny - bh / 2)
    g = affinity.scale(g, k, k, origin=(0, 0))
    return affinity.translate(g, x + w / 2, y + h / 2)


def canvas(aspect):
    a, b = (float(v) for v in str(aspect).split(":")) if ":" in str(aspect) else (1, 1)
    return (1000.0, 1000.0 * b / a) if a >= b else (1000.0 * a / b, 1000.0)


# ------------------------------------------------------------------ operations → (svg_body, W, H)
def op_crop(g, fg, bg, scale=2.6, cx=0.62, cy=0.58, rot=0, aspect="1:1", **_):
    from shapely import affinity
    from shapely.geometry import box
    W, H = canvas(aspect)
    side = max(W, H) * scale
    t = fit(g, (cx * W - side / 2, cy * H - side / 2, side, side))
    t = affinity.rotate(t, rot, origin=(cx * W, cy * H))
    return path_el(t.intersection(box(0, 0, W, H)), fill=fg), W, H


def op_contour(g, fg, bg, n=6, step=0.035, side="out", join="round", weight=None, **_):
    from shapely.geometry import JOIN_STYLE
    js = {"round": JOIN_STYLE.round, "mitre": JOIN_STYLE.mitre, "miter": JOIN_STYLE.mitre,
          "bevel": JOIN_STYLE.bevel}[join]
    pad = n * step * UNIT if side in ("out", "both") else 0
    g = fit(g, (pad + 40, pad + 40, UNIT - 2 * pad - 80, UNIT - 2 * pad - 80))
    w = weight or step * UNIT * 0.28
    body = [path_el(g, fill=fg)]
    for i in range(1, n + 1):
        for sgn in ((1,) if side == "out" else (-1,) if side == "in" else (1, -1)):
            r = g.buffer(sgn * i * step * UNIT, join_style=js, mitre_limit=3)
            if not r.is_empty:
                body.append(path_el(r.boundary, stroke=fg, width=w, join="round" if join == "round" else "miter"))
    return "".join(body), UNIT, UNIT


def op_bands(g, fg, bg, n=5, step=0.04, **_):
    pad = n * step * UNIT
    g = fit(g, (pad + 30, pad + 30, UNIT - 2 * pad - 60, UNIT - 2 * pad - 60))
    body = []
    for i in range(n, 0, -1):
        outer, inner = g.buffer(i * step * UNIT), g.buffer((i - 0.5) * step * UNIT)
        body.append(path_el(outer.difference(inner), fill=fg, opacity=f"{0.25 + 0.75 * (1 - i / (n + 1)):.2f}"))
    body.append(path_el(g, fill=fg))
    return "".join(body), UNIT, UNIT


def op_slice(g, fg, bg, n=7, angle=0, gap=0.35, shift=0.0, **_):
    from shapely import affinity
    from shapely.geometry import box
    g = fit(g, (80, 80, UNIT - 160, UNIT - 160))
    c = (UNIT / 2, UNIT / 2)
    r = affinity.rotate(g, -angle, origin=c)
    minx, miny, maxx, maxy = r.bounds
    h = (maxy - miny) / n
    parts = []
    for i in range(n):
        band = box(minx - 10, miny + i * h + h * gap / 2, maxx + 10, miny + (i + 1) * h - h * gap / 2)
        piece = r.intersection(band)
        dx = shift * UNIT * (0.5 - (i % 2)) if shift else 0
        parts.append(affinity.translate(piece, dx, 0))
    from shapely.ops import unary_union
    out = affinity.rotate(unary_union(parts), angle, origin=c)
    return path_el(out, fill=fg), UNIT, UNIT


def _hatch_lines(g, spacing, angle):
    from shapely import affinity
    from shapely.geometry import LineString, MultiLineString
    c = g.centroid
    r = affinity.rotate(g, -angle, origin=c)
    minx, miny, maxx, maxy = r.bounds
    ls, y = [], miny + spacing / 2
    while y < maxy:
        ls.append(LineString([(minx - 5, y), (maxx + 5, y)]))
        y += spacing
    cut = MultiLineString(ls).intersection(r)
    return affinity.rotate(cut, angle, origin=c)


def op_hatch(g, fg, bg, spacing=0.022, angle=45, weight=0.45, cross=False, outline=False, **_):
    g = fit(g, (60, 60, UNIT - 120, UNIT - 120))
    sp = spacing * UNIT
    body = [path_el(_hatch_lines(g, sp, angle), stroke=fg, width=sp * weight)]
    if cross:
        body.append(path_el(_hatch_lines(g, sp, angle + 90), stroke=fg, width=sp * weight))
    if outline:
        body.append(path_el(g.boundary, stroke=fg, width=sp * weight))
    return "".join(body), UNIT, UNIT


def op_halftone(g, fg, bg, cell=0.028, mode="edge", angle=0, gamma=0.8, **_):
    from shapely import affinity
    from shapely.geometry import Point
    from shapely.prepared import prep
    g = fit(g, (50, 50, UNIT - 100, UNIT - 100))
    pg = prep(g)
    cs = cell * UNIT
    maxd = max(1.0, max((p.exterior.distance(p.representative_point()) for p in polys_of(g)), default=1) * 0.9)
    dots = []
    c = (UNIT / 2, UNIT / 2)
    n = int(UNIT / cs) + 4
    for i in range(-2, n):
        for j in range(-2, n):
            x, y = (i + (0.5 if j % 2 else 0)) * cs, j * cs * 0.866
            px, py = affinity.rotate(Point(x, y), angle, origin=c).coords[0]
            pt = Point(px, py)
            if not pg.contains(pt):
                continue
            if mode == "edge":
                t = min(1.0, g.boundary.distance(pt) / maxd)
            else:   # linear gradient along the rotated axis
                t = min(1.0, max(0.0, py / UNIT))
            rad = cs * 0.5 * (0.18 + 0.82 * t ** gamma)
            dots.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rad:.2f}"/>')
    return f'<g fill="{fg}">{"".join(dots)}</g>', UNIT, UNIT


def op_repeat(g, fg, bg, mode="linear", n=6, decay=0.82, dx=0.13, dy=-0.06, rot=0.0, radius=0.3, **_):
    from shapely import affinity
    body = []
    if mode == "radial":
        s = UNIT * 0.26
        base = fit(g, (UNIT / 2 - s / 2, UNIT / 2 - radius * UNIT - s / 2, s, s))
        for i in range(n):
            body.append(path_el(affinity.rotate(base, 360 * i / n, origin=(UNIT / 2, UNIT / 2)), fill=fg))
    elif mode == "grid":
        k = max(2, int(round(math.sqrt(n * 2))))
        cs = UNIT / k
        for i in range(k):
            for j in range(k):
                t = fit(g, (i * cs + cs * 0.12, j * cs + cs * 0.12, cs * 0.76, cs * 0.76))
                body.append(path_el(affinity.rotate(t, 90 * ((i + j) % 4) if rot == 0 else rot * (i + j),
                                                    origin="centroid"), fill=fg))
    else:   # echo trail: copies grow along a vector; the whole trail is then fitted into the frame
        from shapely.ops import unary_union
        s, x, y, geoms = 100.0, 0.0, 0.0, []
        for i in range(n):
            geoms.append(affinity.rotate(fit(g, (x, y, s, s)), rot * i, origin="centroid"))
            x += dx * 1000
            y += dy * 1000
            s /= decay
        minx, miny, maxx, maxy = unary_union(geoms).bounds
        k = (UNIT - 120) / max(maxx - minx, maxy - miny)
        ox = 60 + ((UNIT - 120) - (maxx - minx) * k) / 2 - minx * k
        oy = 60 + ((UNIT - 120) - (maxy - miny) * k) / 2 - miny * k
        for i, t in enumerate(geoms):
            t = affinity.translate(affinity.scale(t, k, k, origin=(0, 0)), ox, oy)
            op = 1.0 if i == n - 1 else 0.18 + 0.6 * i / n
            body.append(path_el(t, fill=fg, opacity=f"{op:.2f}"))
    return "".join(body), UNIT, UNIT


def op_stack(g, fg, bg, n=10, dx=0.012, dy=0.012, shade=None, **_):
    from shapely import affinity
    from shapely.ops import unary_union
    g = fit(g, (60, 60, UNIT - 120 - n * dx * UNIT, UNIT - 120 - n * dy * UNIT))
    side = unary_union([affinity.translate(g, i * dx * UNIT, i * dy * UNIT) for i in range(n + 1)])
    front = affinity.translate(g, 0, 0)
    return (path_el(side, fill=shade or fg, opacity=None if shade else "0.45") +
            path_el(front.buffer(0), fill=fg)), UNIT, UNIT


def op_modules(g, fg, bg, cols=3, rows=3, spread=0.06, rot=0.0, seed=1, **_):
    from shapely import affinity
    from shapely.geometry import box
    rnd = random.Random(seed)
    g = fit(g, (150, 150, UNIT - 300, UNIT - 300))
    minx, miny, maxx, maxy = g.bounds
    cw, ch = (maxx - minx) / cols, (maxy - miny) / rows
    body = []
    for i in range(cols):
        for j in range(rows):
            piece = g.intersection(box(minx + i * cw, miny + j * ch, minx + (i + 1) * cw, miny + (j + 1) * ch))
            if piece.is_empty or piece.area < 1:
                continue
            ox = (i - (cols - 1) / 2) * spread * UNIT
            oy = (j - (rows - 1) / 2) * spread * UNIT
            piece = affinity.translate(piece, ox, oy)
            if rot:
                piece = affinity.rotate(piece, rnd.choice([-1, 1]) * rot * rnd.random(), origin="centroid")
            body.append(path_el(piece, fill=fg))
    return "".join(body), UNIT, UNIT


def op_outline(g, fg, bg, weight=0.035, **_):
    g = fit(g, (80, 80, UNIT - 160, UNIT - 160))
    w = weight * UNIT
    ring = g.buffer(w / 2, join_style=2).difference(g.buffer(-w / 2, join_style=2))
    return path_el(ring, fill=fg), UNIT, UNIT


def _resample(ring, n):
    from shapely.geometry import LineString
    ln = LineString(ring.coords)
    return [ln.interpolate(i / n, normalized=True).coords[0] for i in range(n)]


def op_morph(g, fg, bg, to=None, steps=5, **_):
    from shapely.geometry import Polygon
    if to is None:
        raise SystemExit("morph needs --to other.svg")
    h = svg_geometry(to)
    N = 400
    a = _resample(max(polys_of(g), key=lambda p: p.area).exterior, N)
    b = _resample(max(polys_of(h), key=lambda p: p.area).exterior, N)
    # align start point + direction for the smoothest blend
    best = None
    for rev in (False, True):
        bb = b[::-1] if rev else b
        for off in range(0, N, 4):
            d = sum(math.dist(a[i], bb[(i + off) % N]) for i in range(0, N, 10))
            if best is None or d < best[0]:
                best = (d, rev, off)
    _, rev, off = best
    bb = (b[::-1] if rev else b)
    bb = bb[off:] + bb[:off]
    cell = UNIT / steps
    body = []
    for k in range(steps):
        t = k / (steps - 1)
        pts = [(a[i][0] * (1 - t) + bb[i][0] * t, a[i][1] * (1 - t) + bb[i][1] * t) for i in range(N)]
        p = Polygon(pts).buffer(0)
        body.append(path_el(fit(p, (k * cell + cell * 0.1, UNIT / 2 - cell * 0.4, cell * 0.8, cell * 0.8)), fill=fg))
    return "".join(body), UNIT, UNIT


def op_frame(g, fg, bg, length=0.1, weight=0.01, aspect="4:5", mark=True, **_):
    """Corner brackets; when the primitive has its own angle (DNA), bracket ends are cut at that angle."""
    W, H = canvas(aspect)
    ang = next((a for a in dna_of(g)["angulos_dominantes"] if a % 90), None)
    L, w, m = length * min(W, H), weight * min(W, H), 0.05 * min(W, H)
    cut = w * math.tan(math.radians(ang % 90)) if ang else 0
    body = []
    for sx, sy, x, y in ((1, 1, m, m), (-1, 1, W - m, m), (1, -1, m, H - m), (-1, -1, W - m, H - m)):
        # L-shaped bracket as one filled polygon (outer corner at x,y), ends sheared by the brand angle
        pts = [(x, y), (x + sx * L, y), (x + sx * (L - cut), y + sy * w), (x + sx * w, y + sy * w),
               (x + sx * w, y + sy * (L - cut)), (x, y + sy * L)]
        body.append(f'<polygon points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" fill="{fg}"/>')
    if mark:
        s = min(W, H) * 0.07
        body.append(path_el(fit(g, (W / 2 - s / 2, H - m - s, s, s)), fill=fg))
    return "".join(body), W, H


OPS = {"crop": op_crop, "contour": op_contour, "bands": op_bands, "slice": op_slice, "hatch": op_hatch,
       "halftone": op_halftone, "repeat": op_repeat, "stack": op_stack, "modules": op_modules,
       "outline": op_outline, "morph": op_morph, "frame": op_frame}

# parameter spaces for exploration
SPACE = {
    "crop": lambda r: {"scale": round(r.uniform(1.6, 3.8), 2), "cx": round(r.uniform(0.2, 0.9), 2),
                       "cy": round(r.uniform(0.25, 0.95), 2), "rot": r.choice([0, 0, 0, 90, -15, 30, 180])},
    "contour": lambda r: {"n": r.randint(3, 10), "step": round(r.uniform(0.015, 0.05), 3),
                          "side": r.choice(["out", "out", "in", "both"]), "join": r.choice(["round", "mitre"])},
    "bands": lambda r: {"n": r.randint(3, 7), "step": round(r.uniform(0.025, 0.06), 3)},
    "slice": lambda r: {"n": r.randint(4, 14), "angle": r.choice([0, 0, 90, 45, -30, 15]),
                        "gap": round(r.uniform(0.15, 0.6), 2), "shift": r.choice([0, 0, 0.02, 0.05])},
    "hatch": lambda r: {"spacing": round(r.uniform(0.012, 0.035), 3), "angle": r.choice([0, 45, 90, -30, 60]),
                        "weight": round(r.uniform(0.3, 0.6), 2), "cross": r.random() < 0.25,
                        "outline": r.random() < 0.4},
    "halftone": lambda r: {"cell": round(r.uniform(0.018, 0.045), 3), "mode": r.choice(["edge", "edge", "linear"]),
                           "angle": r.choice([0, 15, 45])},
    "repeat": lambda r: {"mode": r.choice(["linear", "radial", "grid"]), "n": r.randint(4, 9),
                         "decay": round(r.uniform(0.75, 0.92), 2), "dx": round(r.uniform(0.05, 0.14), 2),
                         "dy": round(r.uniform(-0.08, 0.02), 2), "rot": r.choice([0, 0, 8, -12, 20]),
                         "radius": round(r.uniform(0.18, 0.34), 2)},
    "stack": lambda r: {"n": r.randint(6, 18), "dx": round(r.uniform(-0.016, 0.016), 3),
                        "dy": round(r.uniform(0.006, 0.018), 3)},
    "modules": lambda r: {"cols": r.randint(2, 4), "rows": r.randint(2, 4), "spread": round(r.uniform(0.02, 0.1), 3),
                          "rot": r.choice([0, 0, 8, 20]), "seed": r.randint(1, 99)},
    "outline": lambda r: {"weight": round(r.uniform(0.015, 0.06), 3)},
    "frame": lambda r: {"length": round(r.uniform(0.08, 0.22), 2), "weight": round(r.uniform(0.008, 0.025), 3),
                        "aspect": r.choice(["4:5", "9:16", "1:1"])},
}


def render_op(g, op, params, fg, bg, to=None):
    body, W, H = OPS[op](g, fg, bg, to=to, **params)
    return wrap_svg(W, H, body, title=f"{op} {json.dumps(params)}", bg=bg)


# ------------------------------------------------------------------ DNA
def dna_of(g):
    """Measure the primitive: dominant angles, stroke thickness, symmetry, fill ratio, curvature, parts."""
    import numpy as np
    from shapely import affinity
    minx, miny, maxx, maxy = g.bounds
    size = max(maxx - minx, maxy - miny)
    s = g.simplify(size * 0.006)
    hist = {}
    per = 0.0
    straight = 0.0
    for p in polys_of(s):
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)
            for (x1, y1), (x2, y2) in zip(c, c[1:]):
                L = math.hypot(x2 - x1, y2 - y1)
                per += L
                if L > size * 0.04:
                    straight += L
                    a = round(math.degrees(math.atan2(-(y2 - y1), x2 - x1)) % 180 / 7.5) * 7.5 % 180
                    hist[a] = hist.get(a, 0) + L
    tot = sum(hist.values()) or 1
    dom = [a for a, v in sorted(hist.items(), key=lambda kv: -kv[1]) if v / tot > 0.12][:4]
    # symmetry by IoU with mirrored self
    def iou(a, b):
        u = a.union(b).area
        return a.intersection(b).area / u if u else 0
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    sym_v = iou(g, affinity.scale(g, -1, 1, origin=(cx, cy)))
    sym_h = iou(g, affinity.scale(g, 1, -1, origin=(cx, cy)))
    # stroke thickness ≈ 2 × mean distance-to-edge along the skeleton (raster)
    from skimage.morphology import skeletonize
    from scipy import ndimage
    from PIL import Image, ImageDraw
    R = 600
    k = R / size
    im = Image.new("L", (R + 4, R + 4), 0)
    dr = ImageDraw.Draw(im)
    for p in polys_of(g):
        dr.polygon([((x - minx) * k + 2, (y - miny) * k + 2) for x, y in p.exterior.coords], fill=255)
        for i in p.interiors:
            dr.polygon([((x - minx) * k + 2, (y - miny) * k + 2) for x, y in i.coords], fill=0)
    m = np.asarray(im) > 127
    dist = ndimage.distance_transform_edt(m)
    sk = skeletonize(m)
    stroke = float(2 * np.median(dist[sk])) / R if sk.any() else 0
    n_parts = len(polys_of(g))
    n_holes = sum(len(p.interiors) for p in polys_of(g))
    return {"proporcao_wh": round((maxx - minx) / (maxy - miny), 3),
            "preenchimento": round(g.area / ((maxx - minx) * (maxy - miny)), 3),
            "angulos_dominantes": dom,
            "retas_vs_curvas": round(straight / per, 2) if per else 0,
            "espessura_traco": round(stroke, 3),
            "simetria_vertical": round(sym_v, 2), "simetria_horizontal": round(sym_h, 2),
            "partes": n_parts, "furos": n_holes}


def dna_advice(d):
    tips = []
    ang = set(d["angulos_dominantes"])
    if ang and ang <= {0.0, 90.0}:
        tips.append("ângulos 0°/90° → grid ortogonal, cortes retos, frames retangulares")
    elif any(a % 90 for a in ang):
        odd = sorted(a for a in ang if a % 90)
        tips.append(f"ângulo próprio {odd} → use esse ângulo em cortes, faixas, diagonais do grid e no itálico da marca")
    tips.append("formas curvas → cantos arredondados no sistema (raio proporcional ao traço)" if d["retas_vs_curvas"] < 0.35
                else "formas retas → cantos vivos/chanfros; evite pílulas e arredondados genéricos")
    if d["espessura_traco"]:
        tips.append(f"traço ≈ {d['espessura_traco'] * 100:.1f}% da altura → espessura base de ícones, fios e frames "
                    f"(ícone 24 px ≈ {max(1.5, d['espessura_traco'] * 24):.1f} px)")
    sym = max(d["simetria_vertical"], d["simetria_horizontal"])
    tips.append("muito simétrico → layouts podem centralizar; quebre com recorte assimétrico para ganhar tensão"
                if sym > 0.85 else "assimétrico → layouts em diagonal/alinhados a um lado; direção de leitura importa")
    tips.append("cheio/pesado → contraste com tipografia leve e muito respiro" if d["preenchimento"] > 0.6
                else "leve/aberto → aguenta fundos ativos (padrão, foto) sem perder leitura")
    return tips


# ------------------------------------------------------------------ letters as primitives
def letters_svg(font_spec, text, size=1000, tracking=0.0):
    f = font(font_spec)
    d = f.path(text, size, 0, size * f.cap, tracking)
    w = f.width(text, size, tracking)
    return wrap_svg(w, size * f.cap, f'<path d="{d}" fill="#000"/>')


# ------------------------------------------------------------------ commands
def cmd_dna(a):
    g = svg_geometry(a.svg)
    d = dna_of(g)
    print(json.dumps(d, ensure_ascii=False, indent=1))
    for t in dna_advice(d):
        print(" -", t)
    if a.o:
        write(a.o, json.dumps({**d, "dicas": dna_advice(d)}, ensure_ascii=False, indent=2))


def cmd_letters(a):
    write(a.o, letters_svg(a.font, a.text))
    print(a.o)


def cmd_explore(a):
    g = svg_geometry(a.svg)
    rnd = random.Random(a.seed)
    ops = list(SPACE) if a.ops == "all" else a.ops.split(",")
    os.makedirs(a.o, exist_ok=True)
    items = []
    for op in ops:
        for i in range(a.n):
            params = SPACE[op](rnd) if op in SPACE else {}
            try:
                svg = render_op(g, op, params, a.fg, a.bg, a.to)
            except Exception as e:   # a param combo can collapse the geometry — skip it, keep exploring
                print(f"  skip {op} {params}: {e}")
                continue
            name = f"{op}-{i + 1:02d}"
            write(os.path.join(a.o, name + ".svg"), svg)
            items.append((name, svg))
            print(f"{name}: --op {op} --params '{json.dumps(params)}'")
    out = os.path.join(a.o, "folha.png")
    sheet(out, items, cols=min(6, max(3, a.n)), cell=300, bg="#DADAD5", title=f"exploração · {os.path.basename(a.svg)}")
    print("folha:", out)


def cmd_make(a):
    g = svg_geometry(a.svg)
    params = json.loads(a.params) if a.params else {}
    svg = render_op(g, a.op, params, a.fg, a.bg, a.to)
    write(a.o, svg)
    svg_to_png(svg, os.path.splitext(a.o)[0] + ".png", width=1600)
    print(a.o)


def cmd_build(a):
    b = load_brand(a.brand)
    devices = b.get("devices") or []
    if not devices:
        raise SystemExit('brand.json has no "devices": [{"id","name","op","src","params","rule"}]')
    # colorways are "<fg>-<bg>" colour roles (ink, paper, brand, accent, or ramp steps like brand.300);
    # default = the preferred pairs that read (contrast ≥ 1.8), brand-led first
    prefs = ["brand-ink", "brand-paper", "ink-paper", "paper-ink", "ink-brand", "paper-brand", "accent-ink",
             "accent-paper"]
    if "accent" not in (b.get("color.seeds") or {}):
        prefs = [p for p in prefs if "accent" not in p]
    default = [p for p in prefs if contrast(b.colour(p.split("-")[0]), b.colour(p.split("-")[1])) >= 1.8][:4]
    out_dir = os.path.join(b.dir, "elementos")
    items = []
    for dv in devices:
        g = svg_geometry(b.path(dv["src"]))
        to = b.path(dv.get("to")) if dv.get("to") else None
        master = render_op(g, dv["op"], dv.get("params", {}), "#000000", None, to)
        write(os.path.join(out_dir, f"{dv['id']}.svg"), master)
        wanted = dv.get("colorways") or default
        for i, wname in enumerate(wanted):
            fg_role, bg_role = wname.split("-", 1)
            fg, bg = b.colour(fg_role), b.colour(bg_role)
            if contrast(fg, bg) < 1.3:
                print(f"  aviso {dv['id']} {wname}: contraste {contrast(fg, bg):.2f}:1 — o elemento some")
            svg = render_op(g, dv["op"], dv.get("params", {}), fg, bg, to)
            svg_to_png(svg, os.path.join(out_dir, f"{dv['id']}-{wname}.png"), width=1200)
            if i == 0:
                items.append((dv.get("name", dv["id"]), svg))
        print(f"ok {dv['id']} ({dv['op']}): {', '.join(wanted)}")
    # DNA from the main primitive (primitives[] with "main": true), not from whatever is listed first
    src0 = b.primitive()
    if src0:
        d = dna_of(svg_geometry(src0))
        write(os.path.join(out_dir, "dna.json"), json.dumps({**d, "dicas": dna_advice(d)}, ensure_ascii=False, indent=2))
    sheet(os.path.join(out_dir, "folha.png"), items, cols=min(4, len(items)), cell=420, title=f"{b.name} · elementos")
    print("folha:", os.path.join(out_dir, "folha.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("dna"); p.add_argument("svg"); p.add_argument("-o"); p.set_defaults(fn=cmd_dna)
    p = sp.add_parser("letters"); p.add_argument("font"); p.add_argument("text"); p.add_argument("-o", required=True)
    p.set_defaults(fn=cmd_letters)
    for name, fn in (("explore", cmd_explore), ("make", cmd_make)):
        p = sp.add_parser(name); p.add_argument("svg"); p.add_argument("-o", required=True)
        p.add_argument("--fg", default="#141414"); p.add_argument("--bg", default="#F2F1EC")
        p.add_argument("--to", help="second primitive (morph)")
        if name == "explore":
            p.add_argument("--ops", default="all"); p.add_argument("--n", type=int, default=6)
            p.add_argument("--seed", type=int, default=7)
        else:
            p.add_argument("--op", required=True, choices=list(OPS)); p.add_argument("--params")
        p.set_defaults(fn=fn)
    p = sp.add_parser("build"); p.add_argument("brand"); p.set_defaults(fn=cmd_build)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
