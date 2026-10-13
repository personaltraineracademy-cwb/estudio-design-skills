"""Colour system: OKLCH tonal ramps, light/dark roles, WCAG 2 + APCA contrast, CMYK approx, collision check vs house.

Usage:
  python palette.py build <brand_dir>                 # reads color.seeds from brand.json → writes color.palette,
                                                      # cores/paleta.json, cores/paleta.png, rampas.png, contraste.png
  python palette.py ramp "#3D5AFE"                    # print an 11-step ramp (50…950)
  python palette.py check "#FFFFFF" "#3D5AFE"         # text-on-background: WCAG ratio + APCA Lc + verdict
  python palette.py harmonize "#3D5AFE" [--n 8] [--client Acme]   # accent candidates (OKLCH relations)
  python palette.py collide "#20F0A0" --client Acme    # near-duplicates of colours that client already uses

brand.json → "client": "Acme" (optional: checks sibling-brand colour collisions), "color": {
  "seeds": {"brand": {"hex": "#3D5AFE", "name": "Azul Sinal"}, "ink": {"hex": "#0F1411", "name": "Grafite"},
            "paper": {"hex": "#F3F1EA", "name": "Papel"}, "accent": {"hex": "#FF5B2E", "name": "Brasa"}},
  "proportion": {"paper": 50, "ink": 32, "brand": 14, "accent": 4}
}
Seeds may also be plain HEX strings. Roles are semantic (light + dark mode) and become design tokens (tokens.py).
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import (UI_FONT_BOLD, contrast, ink_on, load_brand, rgb_to_cmyk, svg_to_png, text_path,  # noqa: E402
                   text_width, wrap_svg, write)

STEPS = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950"]
L_TARGET = [0.975, 0.94, 0.885, 0.815, 0.735, 0.645, 0.555, 0.47, 0.385, 0.305, 0.225]
C_SHAPE = [0.10, 0.24, 0.46, 0.70, 0.90, 1.00, 0.96, 0.86, 0.74, 0.62, 0.50]

_USED = {}


def used_colours(client):
    """Colours already used by the client's approved projects (biblioteca/<Cliente>/_fichas.json)."""
    if client not in _USED:
        try:
            from library import used_colours as lib_used   # brand-studio/scripts (on sys.path via _base)
            _USED[client] = lib_used(client) if client else []
        except Exception:
            _USED[client] = []
    return _USED[client]


# ------------------------------------------------------------------ OKLab / OKLCH
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def hex_rgb01(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb01_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c * 255))) for c in rgb)


def to_oklab(h):
    r, g, b = (_lin(c) for c in hex_rgb01(h))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def oklab_to_rgb01(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def to_oklch(h):
    L, a, b = to_oklab(h)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def oklch_hex(L, C, H):
    """OKLCH → HEX, reducing chroma until the colour fits sRGB (keeps L and hue)."""
    def rgb(c):
        return oklab_to_rgb01(L, c * math.cos(math.radians(H)), c * math.sin(math.radians(H)))

    def inside(v):
        return all(-1e-4 <= x <= 1 + 1e-4 for x in v)
    lo, hi = 0.0, C
    if inside(rgb(C)):
        lo = C
    else:
        for _ in range(28):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inside(rgb(mid)) else (lo, mid)
    return rgb01_hex(tuple(_gam(max(0.0, min(1.0, x))) for x in rgb(lo)))


def delta_e(h1, h2):
    a, b = to_oklab(h1), to_oklab(h2)
    return math.dist(a, b)


# ------------------------------------------------------------------ contrast
def apca(text, bg):
    """APCA-W3 0.0.98G-4g lightness contrast Lc (positive = dark text on light bg)."""
    def Y(h):
        r, g, b = hex_rgb01(h)
        y = 0.2126729 * r ** 2.4 + 0.7151522 * g ** 2.4 + 0.0721750 * b ** 2.4
        return y + (0.022 - y) ** 1.414 if y < 0.022 else y
    yt, yb = Y(text), Y(bg)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:
        s = (yb ** 0.56 - yt ** 0.57) * 1.14
        return 0.0 if s < 0.1 else (s - 0.027) * 100
    s = (yb ** 0.65 - yt ** 0.62) * 1.14
    return 0.0 if s > -0.1 else (s + 0.027) * 100


def verdict(text, bg):
    r, lc = contrast(text, bg), abs(apca(text, bg))
    if r >= 7 and lc >= 90:
        v = "texto longo (AAA)"
    elif r >= 4.5 and lc >= 75:
        v = "texto corrido (AA)"
    elif r >= 4.5 or lc >= 60:
        v = "títulos e textos curtos"
    elif r >= 3 or lc >= 45:
        v = "títulos grandes / ícones"
    elif lc >= 30:
        v = "só elementos decorativos"
    else:
        v = "NÃO usar junto"
    return {"wcag": round(r, 2), "apca": round(apca(text, bg), 1), "uso": v}


# ------------------------------------------------------------------ ramps, names, roles
def ramp(seed, chroma_scale=1.0, neutral=False):
    L0, C0, H0 = to_oklch(seed)
    C0 = 0.014 if neutral else max(C0, 0.02) * chroma_scale
    out = {}
    for step, L, k in zip(STEPS, L_TARGET, C_SHAPE):
        if neutral:
            c = C0 * (0.55 + 0.45 * k)
        else:   # chroma peaks at the seed's own lightness and fades toward the extremes; step 50 stays a tint
            c = C0 * max(0.12, 1 - (abs(L - L0) / 0.8) ** 1.5)
            if step == "50" and L0 < 0.95:
                c = min(c, 0.3 * C0)
        out[step] = oklch_hex(L, c, H0)
    if not neutral:   # the exact seed replaces its nearest step, so the brand colour lives inside the ramp
        near = min(STEPS, key=lambda s: abs(L_TARGET[STEPS.index(s)] - L0))
        out[near] = seed.upper()
    return {s: describe(h) for s, h in out.items()}, (near if not neutral else None)


def describe(h):
    r, g, b = (round(c * 255) for c in hex_rgb01(h))
    L, C, H = to_oklch(h)
    c, m, y, k = rgb_to_cmyk(h)
    return {"hex": h.upper(), "rgb": [r, g, b], "cmyk": [c, m, y, k],
            "oklch": [round(L, 3), round(C, 3), round(H, 1)]}


def auto_name(h):
    L, C, H = to_oklch(h)
    if C < 0.03:
        return ("Branco Gelo" if L > 0.95 else "Névoa" if L > 0.85 else "Cinza" if L > 0.45 else
                "Grafite" if L > 0.2 else "Carvão")
    bands = [(20, "Vermelho"), (45, "Coral"), (70, "Laranja"), (95, "Âmbar"), (112, "Amarelo"), (128, "Lima"),
             (160, "Verde"), (190, "Jade"), (215, "Turquesa"), (240, "Ciano"), (275, "Azul"), (305, "Índigo"),
             (330, "Violeta"), (355, "Magenta"), (361, "Vermelho")]
    name = next(n for lim, n in bands if H < lim)
    if (H < 20 or H > 340) and L > 0.62:
        name = "Rosa"
    mod = " Profundo" if L < 0.4 else " Claro" if L > 0.88 else " Elétrico" if C > 0.2 else ""
    return name + mod


def collisions(h, client=None, limit=0.09):
    """Near-duplicates of colours the same client already uses (sibling brands should not collide by accident)."""
    hits = sorted(((delta_e(h, hx), f"{proj} {label}".strip(), hx) for hx, proj, label in used_colours(client)),
                  key=lambda t: t[0])
    seen, out = set(), []
    for d, n, v in hits:
        if d < limit and v not in seen:
            seen.add(v)
            out.append({"projeto": n, "hex": v, "dE": round(d, 3)})
    return out


def seeds_of(brand):
    seeds = {}
    for role, v in (brand.get("color.seeds") or {}).items():
        hx = v["hex"] if isinstance(v, dict) else v
        nm = v.get("name") if isinstance(v, dict) else None
        seeds[role] = {"hex": hx.upper(), "name": nm or auto_name(hx)}
    for need, default in (("ink", "#141414"), ("paper", "#F4F3EF")):
        seeds.setdefault(need, {"hex": default, "name": auto_name(default)})
    if "brand" not in seeds:
        raise SystemExit("color.seeds.brand is required")
    return seeds


def roles(seeds, ramps):
    """Semantic roles for light and dark modes (become tokens)."""
    ink, paper, brand = seeds["ink"]["hex"], seeds["paper"]["hex"], seeds["brand"]["hex"]
    n = ramps["neutral"]
    acc = seeds.get("accent", {}).get("hex", brand)
    light = {"bg": paper, "surface": n["100"]["hex"], "surface-strong": n["200"]["hex"], "border": n["300"]["hex"],
             "text": ink, "text-muted": n["700"]["hex"], "brand": brand, "on-brand": ink_on(brand, paper, ink),
             "accent": acc, "on-accent": ink_on(acc, paper, ink)}
    dark = {"bg": ink, "surface": n["900"]["hex"], "surface-strong": n["800"]["hex"], "border": n["700"]["hex"],
            "text": paper, "text-muted": n["300"]["hex"], "brand": brand, "on-brand": ink_on(brand, paper, ink),
            "accent": acc, "on-accent": ink_on(acc, paper, ink)}
    # brand-as-text must be legible: on light bg fall back to the darkest step that passes 4.5:1
    for mode, bg in ((light, paper), (dark, ink)):
        r = ramps["brand"]
        ok = [s for s in STEPS if contrast(r[s]["hex"], bg) >= 4.5]
        mode["brand-text"] = brand if contrast(brand, bg) >= 4.5 else (
            r[ok[0] if bg == paper else ok[-1]]["hex"] if ok else mode["text"])
    return {"light": light, "dark": dark}


def build_palette(seeds, client=None):
    ramps, exact = {}, {}
    for role, s in seeds.items():
        if role in ("ink", "paper"):
            continue
        ramps[role], exact[role] = ramp(s["hex"])
    ramps["neutral"], _ = ramp(seeds["ink"]["hex"], neutral=True)
    keys = {k: v["hex"] for k, v in seeds.items()}
    keys.update({"branco": "#FFFFFF", "preto": "#000000"})
    pairs = []
    names = list(keys)
    for a in names:
        for b in names:
            if a != b and not (a in ("branco", "preto") and b in ("branco", "preto")):
                pairs.append({"texto": a, "fundo": b, **verdict(keys[a], keys[b])})
    return {"seeds": {k: {**v, **describe(v["hex"]), "colisoes": collisions(v["hex"], client)}
                      for k, v in seeds.items()},
            "ramps": ramps, "seed_step": exact, "roles": roles(seeds, ramps), "contrast": pairs}


# ------------------------------------------------------------------ sheets
def sheet_palette(seeds, proportion, out):
    order = [k for k in ("paper", "ink", "brand", "accent") if k in seeds] + \
            [k for k in seeds if k not in ("paper", "ink", "brand", "accent")]
    W, H = 1600, 900
    body, x = [], 60
    cw = (W - 120 - 20 * (len(order) - 1)) / len(order)
    for k in order:
        s = seeds[k]
        hx = s["hex"]
        fg = ink_on(hx, "#FFFFFF", "#141414")
        body.append(f'<rect x="{x:.1f}" y="60" width="{cw:.1f}" height="560" rx="6" fill="{hx}" '
                    f'stroke="#00000014"/>')
        body.append(text_path(s["name"], 30, x + 24, 110, fg, UI_FONT_BOLD))
        body.append(text_path(k.upper(), 14, x + 24, 140, fg, tracking=0.12))
        r, g, b = s["rgb"]
        c, m, y, kk = s["cmyk"]
        for i, line in enumerate([f"HEX {hx}", f"RGB {r} {g} {b}", f"CMYK {c} {m} {y} {kk}",
                                  "OKLCH %.3f %.3f %.0f" % tuple(s["oklch"])]):
            body.append(text_path(line, 17, x + 24, 520 + i * 24, fg))
        x += cw + 20
    # proportion bar
    tot = sum(proportion.get(k, 0) for k in order) or 1
    x = 60
    body.append(text_path("PROPORÇÃO DE USO", 14, 60, 680, "#141414", tracking=0.12))
    for k in order:
        w = (W - 120) * proportion.get(k, 0) / tot
        if w <= 0:
            continue
        hx = seeds[k]["hex"]
        body.append(f'<rect x="{x:.1f}" y="700" width="{w:.1f}" height="120" fill="{hx}" stroke="#00000014"/>')
        lab = f"{proportion[k]}%"
        if w > text_width(lab, 20) + 20:
            body.append(text_path(lab, 20, x + 14, 790, ink_on(hx, "#FFFFFF", "#141414"), UI_FONT_BOLD))
        x += w
    svg_to_png(wrap_svg(W, H, "".join(body), bg="#FFFFFF"), out)


def sheet_ramps(pal, seeds, out):
    rows = list(pal["ramps"].items())
    W, cw, ch = 1600, (1600 - 260) / len(STEPS), 92
    H = 60 + len(rows) * (ch + 26) + 40
    body = []
    for i, step in enumerate(STEPS):
        body.append(text_path(step, 14, 230 + i * cw + cw / 2, 44, "#555555", anchor="middle"))
    for r, (role, rmp) in enumerate(rows):
        y = 60 + r * (ch + 26)
        nm = seeds[role]["name"] if role in seeds else "Neutro"
        body.append(text_path(nm, 19, 30, y + ch / 2 + 7, "#141414", UI_FONT_BOLD))
        for i, step in enumerate(STEPS):
            hx = rmp[step]["hex"]
            x = 230 + i * cw
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{cw - 4:.1f}" height="{ch}" fill="{hx}"/>')
            if pal["seed_step"].get(role) == step:
                body.append(f'<circle cx="{x + cw / 2 - 2:.1f}" cy="{y + 18}" r="5" fill="{ink_on(hx)}"/>')
            body.append(text_path(hx, 12, x + cw / 2 - 2, y + ch - 12, ink_on(hx), anchor="middle"))
    svg_to_png(wrap_svg(W, H, "".join(body), bg="#FFFFFF"), out)


def sheet_contrast(pal, seeds, out):
    keys = list(seeds) + ["branco", "preto"]
    hexes = {k: seeds[k]["hex"] for k in seeds}
    hexes.update({"branco": "#FFFFFF", "preto": "#000000"})
    n = len(keys)
    cell = 150
    W, H = 220 + n * cell + 40, 120 + n * cell + 40
    body = [text_path("TEXTO (linha) SOBRE FUNDO (coluna) · WCAG · APCA", 15, 40, 40, "#141414", tracking=0.06)]
    lookup = {(p["texto"], p["fundo"]): p for p in pal["contrast"]}
    for j, b in enumerate(keys):
        body.append(text_path(b, 14, 220 + j * cell + cell / 2, 100, "#141414", anchor="middle"))
    for i, a in enumerate(keys):
        y = 120 + i * cell
        body.append(text_path(a, 15, 40, y + cell / 2 + 5, "#141414", UI_FONT_BOLD))
        for j, b in enumerate(keys):
            x = 220 + j * cell
            p = lookup.get((a, b))
            body.append(f'<rect x="{x}" y="{y}" width="{cell - 6}" height="{cell - 6}" fill="{hexes[b]}" '
                        f'stroke="#00000018"/>')
            if not p:
                continue
            body.append(text_path("Aa", 44, x + 16, y + 62, hexes[a], UI_FONT_BOLD))
            lab = ink_on(hexes[b])
            body.append(text_path(f"{p['wcag']}:1  Lc {abs(p['apca']):.0f}", 13, x + 16, y + 92, lab))
            bad = p["uso"].startswith("NÃO") or p["uso"].startswith("só")
            body.append(text_path(p["uso"][:24], 11, x + 16, y + 116, "#D11" if bad else lab))
    svg_to_png(wrap_svg(W, H, "".join(body), bg="#FFFFFF"), out)


# ------------------------------------------------------------------ commands
def cmd_build(a):
    b = load_brand(a.brand)
    seeds = seeds_of(b)
    pal = build_palette(seeds, b.get("client"))
    out_dir = os.path.join(b.dir, "cores")
    write(os.path.join(out_dir, "paleta.json"), json.dumps(pal, ensure_ascii=False, indent=2))
    b.set("color.palette", {"ramps": pal["ramps"], "roles": pal["roles"], "seed_step": pal["seed_step"]})
    for k, s in seeds.items():
        cur = (b.get("color.seeds") or {}).get(k)
        if isinstance(cur, str) or cur is None:
            b.set(f"color.seeds.{k}", {"hex": s["hex"], "name": s["name"]})
    b.save()
    prop = b.get("color.proportion") or {"paper": 50, "ink": 30, "brand": 15, "accent": 5}
    sheet_palette(pal["seeds"], prop, os.path.join(out_dir, "paleta.png"))
    sheet_ramps(pal, pal["seeds"], os.path.join(out_dir, "rampas.png"))
    sheet_contrast(pal, pal["seeds"], os.path.join(out_dir, "contraste.png"))
    print(f"ok → {out_dir}  (paleta.png, rampas.png, contraste.png, paleta.json)")
    for k, s in pal["seeds"].items():
        if s["colisoes"]:
            print(f"  aviso: {k} {s['hex']} parecida com cor já usada por {b.get('client')}: " +
                  ", ".join(f"{c['projeto']} {c['hex']} (dE {c['dE']})" for c in s["colisoes"]))
    warn = [p for p in pal["contrast"] if p["texto"] in ("brand", "accent") and p["fundo"] in ("paper", "branco")
            and p["uso"].startswith(("NÃO", "só"))]
    for p in warn:
        print(f"  aviso: {p['texto']} sobre {p['fundo']} = {p['wcag']}:1 → {p['uso']} (use roles.brand-text)")


def cmd_ramp(a):
    r, near = ramp(a.hex)
    for s in STEPS:
        print(f"{s:>4} {r[s]['hex']}  oklch {r[s]['oklch']}" + ("  ← seed" if s == near else ""))


def cmd_check(a):
    print(json.dumps(verdict(a.text, a.bg), ensure_ascii=False))


def cmd_harmonize(a):
    L, C, H = to_oklch(a.hex)
    rel = [("complementar", 180), ("split +150", 150), ("split -150", -150), ("tríade +120", 120),
           ("tríade -120", -120), ("análoga +35", 35), ("análoga -35", -35), ("tensão +95", 95), ("tensão -95", -95)]
    out = []
    for name, dh in rel[: a.n + 1]:
        for Lx in (0.62, 0.72):
            hx = oklch_hex(Lx, max(C, 0.15), (H + dh) % 360)
            col = collisions(hx, a.client)
            out.append((name, hx, auto_name(hx), col))
    for name, hx, nm, col in out:
        flag = ("  ≈ já usada: " + ", ".join(f"{c['projeto']} dE {c['dE']}" for c in col)) if col else ""
        print(f"{name:<13} {hx}  {nm:<18} contraste c/ seed {contrast(hx, a.hex):.2f}:1{flag}")


def cmd_collide(a):
    hits = collisions(a.hex, a.client, limit=0.15)
    print(json.dumps(hits, ensure_ascii=False, indent=1) if hits else f"sem colisão com cores de {a.client} (dE ≥ 0.15)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("build"); p.add_argument("brand"); p.set_defaults(fn=cmd_build)
    p = sp.add_parser("ramp"); p.add_argument("hex"); p.set_defaults(fn=cmd_ramp)
    p = sp.add_parser("check"); p.add_argument("text"); p.add_argument("bg"); p.set_defaults(fn=cmd_check)
    p = sp.add_parser("harmonize"); p.add_argument("hex"); p.add_argument("--n", type=int, default=8)
    p.add_argument("--client", help="flag colours this client already uses")
    p.set_defaults(fn=cmd_harmonize)
    p = sp.add_parser("collide"); p.add_argument("hex"); p.add_argument("--client", required=True)
    p.set_defaults(fn=cmd_collide)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
