"""Type system: modular scale + hierarchy + specimens, everything rendered in curves with the brand's real fonts.

Usage:
  python typesys.py build <brand_dir>          # → type.levels in brand.json + tipografia/{especime,hierarquia,par}.png
  python typesys.py scale 16 1.25              # print a modular scale
  python typesys.py try "Fraunces:700" "Instrument Sans:400" -o par.png --text "Título de teste"
        # quick pairing proof before committing to brand.json

brand.json → "type": {"display": {"family": "Bricolage Grotesque", "weight": 800},
                      "text": {"family": "Instrument Sans", "weight": 400},
                      "scale": {"base": 16, "ratio": 1.25}, "tracking_display": -0.02}
Fonts come from Google Fonts (OFL) via brand-studio/fonts.py, or a local .ttf/.otf path (licence is your call).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import (UI_FONT, Font, font_path, ink_on, load_brand, svg_to_png, text_path, wrap_svg)  # noqa: E402

# overused / "AI default" faces — allowed only with a reason written in type.rules
GENERIC = {"inter", "roboto", "arial", "helvetica", "space grotesk", "open sans", "poppins", "montserrat", "lato",
           "dm sans", "plus jakarta sans", "manrope"}

LEVELS = [  # name, step on the scale, role (display|text), line-height, tracking (em)
    ("display", 6, "display", 0.95, None), ("h1", 5, "display", 1.0, None), ("h2", 4, "display", 1.05, None),
    ("h3", 3, "display", 1.1, None), ("h4", 2, "text", 1.2, 0.0), ("lead", 1, "text", 1.4, 0.0),
    ("body", 0, "text", 1.5, 0.0), ("small", -1, "text", 1.45, 0.01), ("caption", -2, "text", 1.35, 0.04),
]
SAMPLE = {"display": "Força em forma", "h1": "Um sistema que pensa", "h2": "Título de seção",
          "h3": "Subtítulo com respiro", "h4": "Chamada curta",
          "lead": "Texto de abertura que apresenta a ideia em uma ou duas linhas.",
          "body": "Texto corrido para explicar com calma: a hierarquia nasce da escala, do peso e do espaço. "
                  "Cada nível tem um papel e uma medida.",
          "small": "Notas, legendas e informações de apoio.", "caption": "LEGENDA · CRÉDITO · 2026"}


def spec_of(entry, default_weight):
    if isinstance(entry, str):
        return entry
    fam = entry.get("family") or entry.get("file")
    w = entry.get("weight", default_weight)
    return fam if fam.lower().endswith((".ttf", ".otf")) else f"{fam}:{w}"


def scale(base, ratio):
    return {name: round(base * ratio ** step, 1) for name, step, *_ in LEVELS}


def wrap(f, s, size, width, tracking=0.0):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and f.width(t, size, tracking) > width:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def block(f, s, size, x, y, width, fill, lh=1.3, tracking=0.0, upper=False):
    """Paragraph as paths; returns (svg, height)."""
    s = s.upper() if upper else s
    out, yy = [], y + size * f.cap
    for ln in wrap(f, s, size, width, tracking):
        out.append(f'<path d="{f.path(ln, size, x, yy, tracking)}" fill="{fill}"/>')
        yy += size * lh
    return "".join(out), (yy - size * lh) - y + size * 0.3


def specimen(fd, ft, name_d, name_t, ink, paper, accent, out):
    W, H = 1600, 1000
    body = [f'<rect width="{W}" height="{H}" fill="{paper}"/>']
    body.append(f'<path d="{fd.path("Aa", 520, 60, 470, -0.02)}" fill="{ink}"/>')
    body.append(text_path(name_d, 26, 70, 540, ink, UI_FONT))
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, ln in enumerate((alpha[:13], alpha[13:], "abcdefghijklm", "nopqrstuvwxyz", "0123456789 &%@#!?ÁÇÉÕÜ")):
        body.append(f'<path d="{fd.path(ln, 56, 760, 120 + i * 78, 0.01)}" fill="{ink}"/>')
    body.append(f'<rect x="60" y="600" width="{W - 120}" height="2" fill="{ink}" opacity="0.15"/>')
    body.append(f'<path d="{ft.path("Aa", 300, 60, 900)}" fill="{accent}"/>')
    body.append(text_path(name_t, 26, 70, 960, ink, UI_FONT))
    para = ("Texto corrido com a fonte de leitura. Ela precisa funcionar em parágrafos longos, legendas e interfaces; "
            "números 0123456789 e acentos: ação, coração, pão, você.")
    svg, _ = block(ft, para, 30, 520, 660, W - 600, ink, 1.45)
    body.append(svg)
    svg_to_png(wrap_svg(W, H, "".join(body)), out)


def hierarchy(fd, ft, sizes, levels_cfg, ink, paper, accent, out, k=1.6):
    W = 1600
    body, y = [], 70
    for name, step, role, lh, tr in LEVELS:
        f = fd if role == "display" else ft
        size = sizes[name] * k
        trk = levels_cfg[name]["tracking"]
        upper = name == "caption"
        body.append(text_path(f"{name} · {sizes[name]:g}px", 16, 60, y + 18, ink, UI_FONT))
        svg, h = block(f, SAMPLE[name], size, 320, y, W - 380, accent if name == "display" else ink, lh, trk, upper)
        body.append(svg)
        y += max(h, 30) + 34
    H = y + 40
    svg_to_png(wrap_svg(W, H, "".join(body), bg=paper), out)


def pairing(fd, ft, ink, paper, accent, out, title="Uma ideia forte cabe numa linha"):
    W, H = 1600, 900
    body = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="{ink}"/>']
    svg, h = block(fd, title, 130, 80, 120, W - 160, paper, 1.0, -0.01)
    body.append(svg)
    sub = ("A fonte de texto acompanha o título sem competir: contraste de peso, de largura ou de época — nunca "
           "duas vozes iguais.")
    svg2, _ = block(ft, sub, 34, 80, 140 + h + 40, 900, paper, 1.45)
    body.append(svg2)
    body.append(f'<rect x="80" y="{H - 140}" width="300" height="64" rx="0" fill="{accent}"/>')
    lab = "QUERO SABER MAIS"
    body.append(f'<path d="{ft.path(lab, 22, 80 + (300 - ft.width(lab, 22, 0.08)) / 2, H - 100, 0.08)}" '
                f'fill="{ink_on(accent, paper, ink)}"/>')
    svg_to_png(wrap_svg(W, H, "".join(body)), out)


def cmd_build(a):
    b = load_brand(a.brand)
    t = b.get("type") or {}
    if not (t.get("display") and t.get("text")):
        raise SystemExit("defina type.display e type.text no brand.json")
    sd, st = spec_of(t["display"], 800), spec_of(t["text"], 400)
    fd, ft = Font(font_path(sd)), Font(font_path(st))
    sc = t.get("scale", {})
    base, ratio = sc.get("base", 16), sc.get("ratio", 1.25)
    sizes = scale(base, ratio)
    td = t.get("tracking_display", -0.01)
    levels = {}
    for name, step, role, lh, tr in LEVELS:
        levels[name] = {"role": role, "size": sizes[name], "line_height": lh,
                        "tracking": td if tr is None else tr,
                        "family": (t[role] if isinstance(t[role], str) else t[role].get("family")),
                        "weight": (t[role].get("weight") if isinstance(t[role], dict) else None)}
    b.set("type.levels", levels)
    b.save()
    ink, paper, brand = b.colour("ink"), b.colour("paper", "#F4F3EF"), b.colour("brand")
    accent = brand
    out = os.path.join(b.dir, "tipografia")
    os.makedirs(out, exist_ok=True)
    specimen(fd, ft, sd, st, ink, paper, accent, os.path.join(out, "especime.png"))
    hierarchy(fd, ft, sizes, levels, ink, paper, b.get("color.palette.roles.light.brand-text") or ink,
              os.path.join(out, "hierarquia.png"))
    pairing(fd, ft, ink, paper, accent, os.path.join(out, "par.png"), b.get("platform.idea") or
            "Uma ideia forte cabe numa linha")
    print(f"ok → {out} (especime.png, hierarquia.png, par.png)")
    for role, spec in (("display", sd), ("text", st)):
        fam = spec.split(":")[0].lower()
        if fam in GENERIC and not t.get("rules"):
            print(f"  aviso: {spec} é uma fonte muito usada/'padrão de IA' — justifique em type.rules ou troque")
    print("escala:", ", ".join(f"{k} {v:g}" for k, v in sizes.items()))


def cmd_scale(a):
    for k, v in scale(a.base, a.ratio).items():
        print(f"{k:<8} {v:g}px")


def cmd_try(a):
    fd, ft = Font(font_path(a.display)), Font(font_path(a.text))
    pairing(fd, ft, a.ink, a.paper, a.accent, a.o, a.title)
    print(a.o)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("build"); p.add_argument("brand"); p.set_defaults(fn=cmd_build)
    p = sp.add_parser("scale"); p.add_argument("base", type=float); p.add_argument("ratio", type=float)
    p.set_defaults(fn=cmd_scale)
    p = sp.add_parser("try"); p.add_argument("display"); p.add_argument("text"); p.add_argument("-o", required=True)
    p.add_argument("--title", default="Uma ideia forte cabe numa linha"); p.add_argument("--ink", default="#141414")
    p.add_argument("--paper", default="#F3F1EA"); p.add_argument("--accent", default="#FF5B2E")
    p.set_defaults(fn=cmd_try)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
