"""Applications: brand pieces in any format from layout recipes on the brand grid, plus the 10-application stress test.
Renders through brand-studio/compose.py (live text, Adobe Express HTML) — one spec per recipe, every format at once.

Usage:
  python apply.py build <brand_dir> [--recipes all|supergrafico,tipografico,...] [--formats post,feed,story,banner]
  python apply.py stress <brand_dir>                 # → aplicacoes/estresse.png (10-application test board)
  python apply.py list                               # recipes + formats

Content per piece comes from brand.json "applications": [{"recipe": "supergrafico", "headline": "…", "sub": "…",
"cta": "…", "photo": "fotos/x.jpg", "formats": ["post", "story"]}]; without it, sample copy from the platform.
Recipes use: logo.primary (or a provisional wordmark), the main primitive (primitives[] with "main": true, else the
first) / logo.symbol, devices (pattern-like ops), color roles, type.display/text (Google family or a .ttf in the
project), grid.margin. Devices on the ink background take the first of brand/accent/paper that stands out on it.
Stress favicon/avatar use logo.symbol or a primitive with "role": "symbol" (never the long wordmark if there is one).
Recipes are a starting point: when a territory needs its own layouts, build them by code in the project and keep
the recipe outputs as a baseline.
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import (STUDIO_SCRIPTS, UI_FONT, ink_on, load_brand, recolor, solid, svg_inner, svg_to_png, text_path,  # noqa: E402
                   viewbox, vivid_on, wrap_svg, write)

FORMATS = {"post": (1080, 1080), "feed": (1080, 1350), "story": (1080, 1920), "banner": (1920, 1080),
           "a4": (1240, 1754), "outdoor": (3000, 1000), "web-728": (728, 90), "web-300": (300, 250),
           "slide": (1920, 1080), "thumb": (1280, 720)}
RECIPES = {
    "supergrafico": "símbolo gigante cortado pela borda + título no grid + assinatura",
    "tipografico": "título enorme em bloco sobre a cor da marca; o tipo é a imagem",
    "padrao": "dispositivo/padrão em tela cheia + painel sólido com a mensagem",
    "moldura": "moldura derivada do ângulo da marca + título central",
    "numeral": "número herói (preço, %, dado) + rótulo",
    "foto": "foto em tela cheia + supergráfico por cima + título (precisa de photo)",
}


def device_svg(b, op, params, aspect, fg):
    import elements
    src = primitive(b)
    g = elements.svg_geometry(src)
    kw = dict(params)
    kw.setdefault("aspect", aspect)
    body, W, H = elements.OPS[op](g, fg, None, **kw)
    return wrap_svg(W, H, body)


def primitive(b):
    return b.primitive() or logo_path(b)


def logo_path(b):
    lp = b.get("logo.primary")
    if lp and os.path.exists(b.path(lp)):
        return b.path(lp)
    import elements
    spec = b.font_spec("display", 800, "Bricolage Grotesque")
    out = os.path.join(b.dir, "logo", "wordmark-provisorio.svg")
    if not os.path.exists(out):
        write(out, elements.letters_svg(spec, b.name))
        print(f"  (sem logo.primary: usando wordmark provisório {out})")
    return out


def balance(f, words, n):
    """Split words into n lines minimising the widest line (exhaustive for short headlines)."""
    from itertools import combinations
    if n <= 1 or len(words) <= 1:
        return [" ".join(words)]
    n = min(n, len(words))
    from modelos import _bad_break     # leitura em português: nada de linha terminando em "a", "de", "um"…
    best, best_w = None, 1e9
    for cuts in combinations(range(1, len(words)), n - 1):
        idx = (0,) + cuts + (len(words),)
        lines = [" ".join(words[idx[i]:idx[i + 1]]) for i in range(n)]
        if _bad_break(lines) and best is not None:
            continue
        w = max(f.width(l, 1) for l in lines)
        if w < best_w:
            best, best_w = lines, w
    return best


def headline(f, text, box, W, H, color, max_lines=4, lh=0.95, upper=False, align="left", valign="top",
             tracking=-0.01, font="display"):
    """Text layer whose line breaks maximise the type size inside box (% of canvas)."""
    text = text.upper() if upper else text
    bw, bh = box[2] * W / 100, box[3] * H / 100
    words = text.split()
    best = (0, text)
    for n in range(1, min(max_lines, len(words)) + 1):
        lines = balance(f, words, n)
        wmax = max(f.width(l, 1, tracking) for l in lines)
        size = min(bw / wmax, bh / (f.cap + (n - 1) * lh + 0.25))
        if size > best[0] * 1.04:      # prefer fewer lines unless more lines clearly enlarge the type
            best = (size, "\n".join(lines))
    return {"type": "text", "text": best[1], "font": font, "color": color, "box": box, "fit": "box", "align": align,
            "valign": valign, "line": lh, "tracking": tracking}


def content(b, recipe):
    for app in b.get("applications") or []:
        if app.get("recipe") == recipe:
            return app
    plat = b.get("platform") or {}
    ex = (plat.get("voice") or {}).get("examples") or []
    return {"headline": (ex[0] if ex else plat.get("idea") or b.name), "sub": plat.get("idea") or "",
            "cta": "saiba mais", "number": "50%", "label": "de desconto até domingo"}


def spec_for(b, recipe, fmts, work):
    """Build a compose.py spec for one recipe across formats; per-format assets go into work/."""
    from _base import Font, font_path
    ink, paper, brand = b.colour("ink"), b.colour("paper", "#F4F3EF"), b.colour("brand")
    accent = b.colour("accent", brand)
    fd_spec = b.font_spec("display", 800, "Bricolage Grotesque")
    ft_spec = b.font_spec("text", 400) or fd_spec
    pop = vivid_on(ink, [brand, accent, paper])     # device colour that does not vanish on the ink background
    fdisp = Font(font_path(fd_spec))
    c = content(b, recipe)
    m = (b.get("grid") or {}).get("margin", 0.06) * 100
    logo = logo_path(b)
    logo_txt = open(logo, encoding="utf-8").read()
    os.makedirs(work, exist_ok=True)
    write(os.path.join(work, "logo-ink.svg"), solid(logo_txt, ink))
    write(os.path.join(work, "logo-paper.svg"), solid(logo_txt, paper))
    sizes, layers_by_size = [], {}
    for fm in fmts:
        W, H = FORMATS[fm]
        sizes.append(f"{W}x{H}")
        my = m * W / H
        portrait = H > W * 1.1
        wide = W > H * 2
        asp = f"{W}:{H}"
        L = []
        lg = 5.5 if portrait else (7 if not wide else 12)          # logo height (% of H)
        on_brand = ink_on(brand, paper, ink)
        if recipe == "supergrafico":
            # symbol enlarged inside its own field (bleeding off the edges); headline owns the opposite field
            if wide or W > H * 1.3:
                dbox, tb = [50, 0, 50, 100], [m, my * 1.4, 44, 100 - 2.8 * my - lg - 4]
            elif portrait:
                dbox, tb = [0, 46, 100, 54], [m, my, 100 - 2 * m, 38]
            else:
                dbox, tb = [36, 40, 64, 60], [m, my, 100 - 2 * m, 34]
            dw, dh = dbox[2] * W / 100, dbox[3] * H / 100
            dev = device_svg(b, "crop", {"scale": 1.15, "cx": 0.72, "cy": 0.7, "rot": 0,
                                         "aspect": f"{dw:.0f}:{dh:.0f}"}, aspect=None, fg=pop)
            write(os.path.join(work, f"dev-{fm}.svg"), dev)
            L += [{"type": "bg", "color": ink},
                  {"type": "svg", "src": f"dev-{fm}.svg", "box": dbox},
                  headline(fdisp, c["headline"], tb, W, H, paper, 4),
                  {"type": "logo", "src": "logo-paper.svg", "box": [m, 100 - my - lg, 30, lg], "align": "left bottom"}]
        elif recipe == "tipografico":
            tb = [m, my, 100 - 2 * m, 100 - 2 * my - lg - 6]
            L += [{"type": "bg", "color": brand},
                  headline(fdisp, c["headline"], tb, W, H, on_brand, 5 if portrait else 3, lh=0.88, upper=True,
                           tracking=-0.02),
                  {"type": "text", "text": c.get("sub") or "", "font": "body", "color": on_brand,
                   "box": [m, 100 - my - lg, 50, lg * 0.6], "fit": "box", "align": "left", "valign": "bottom"},
                  {"type": "logo", "src": "logo-ink.svg" if on_brand == ink else "logo-paper.svg",
                   "box": [100 - m - 30, 100 - my - lg, 30, lg], "align": "right bottom"}]
        elif recipe == "padrao":
            pat = next((dv for dv in (b.get("devices") or []) if dv["op"] in ("halftone", "hatch", "repeat", "contour",
                                                                              "bands", "slice")), None)
            op, params = (pat["op"], pat.get("params", {})) if pat else ("repeat", {"mode": "grid", "n": 12})
            dev = device_svg(b, op, params, aspect=asp, fg=pop)
            write(os.path.join(work, f"pat-{fm}.svg"), dev)
            if portrait:
                pb, dvbox = [0, 54, 100, 46], [m, my, 100 - 2 * m, 50 - my]
            elif wide:
                pb, dvbox = [0, 0, 52, 100], [56, my, 44 - m, 100 - 2 * my]
            else:
                pb, dvbox = [0, 0, 50, 100], [52, my, 48 - m, 100 - 2 * my]
            pad = m
            padv = pad * W / H
            L += [{"type": "bg", "color": ink},
                  {"type": "svg", "src": f"pat-{fm}.svg", "box": dvbox},
                  {"type": "shape", "shape": "rect", "box": pb, "fill": paper},
                  headline(fdisp, c["headline"], [pb[0] + pad, pb[1] + padv, pb[2] - 2 * pad,
                                                  pb[3] - 2 * padv - lg - 4], W, H, ink, 4),
                  {"type": "logo", "src": "logo-ink.svg", "box": [pb[0] + pad, pb[1] + pb[3] - padv - lg, 30, lg],
                   "align": "left bottom"}]
        elif recipe == "moldura":
            dev = device_svg(b, "frame", {"length": 0.1, "weight": 0.01, "aspect": asp}, aspect=asp, fg=ink)
            write(os.path.join(work, f"frame-{fm}.svg"), dev)
            L += [{"type": "bg", "color": paper},
                  {"type": "svg", "src": f"frame-{fm}.svg", "box": [0, 0, 100, 100]},
                  headline(fdisp, c["headline"], [m * 2.5, 22 if portrait else 18, 100 - 5 * m, 40 if portrait else 46],
                           W, H, ink, 4, align="center", valign="middle"),
                  {"type": "text", "text": c.get("cta") or "", "font": "body",
                   "color": b.get("color.palette.roles.light.brand-text") or ink,
                   "box": [30, 72 if portrait else 74, 40, 2.6 if portrait else 4], "fit": "box", "align": "center",
                   "tracking": 0.14, "upper": True}]
        elif recipe == "numeral":
            on_acc = ink_on(accent, paper, ink)
            L += [{"type": "bg", "color": accent},
                  {"type": "text", "text": c.get("number", "50%"), "font": "display", "color": on_acc,
                   "box": [m, my, 100 - 2 * m, 48 if portrait else (58 if not wide else 70)], "fit": "box",
                   "align": "left", "valign": "top", "line": 0.85, "tracking": -0.03},
                  headline(fdisp, c.get("label", ""), [m, 56 if portrait else 66, 100 - 2 * m if not wide else 60,
                                                       14 if portrait else 14], W, H, on_acc, 2, font="body",
                           tracking=0),
                  {"type": "logo", "src": "logo-ink.svg" if on_acc == ink else "logo-paper.svg",
                   "box": [m, 100 - my - lg, 30, lg], "align": "left bottom"}]
        elif recipe == "foto":
            if not c.get("photo"):
                print("  receita 'foto' sem photo em applications → pulada")
                return None
            dev = device_svg(b, "crop", {"scale": 1.1, "cx": 1.0, "cy": 1.0, "aspect": asp}, aspect=asp, fg=brand)
            write(os.path.join(work, f"dev-{fm}.svg"), dev)
            L += [{"type": "bg", "color": ink},
                  {"type": "image", "src": os.path.relpath(b.path(c["photo"]), work).replace("\\", "/"),
                   "box": [0, 0, 100, 100], "fit": "cover"},
                  {"type": "svg", "src": f"dev-{fm}.svg", "box": [0, 0, 100, 100]},
                  headline(fdisp, c["headline"], [m, my, 70, 30], W, H, paper, 4),
                  {"type": "logo", "src": "logo-paper.svg", "box": [m, 100 - my - lg, 30, lg], "align": "left bottom"}]
        fx = (b.get("texture") or {}).get("fx") or []
        if fx:
            L.append({"type": "fx", "chain": fx})
        layers_by_size[f"{W}x{H}"] = L
    first = sizes[0]
    spec = {"name": recipe, "out_dir": "pecas", "sizes": sizes, "fonts": {"display": fd_spec, "body": ft_spec},
            "layers": layers_by_size[first], "overrides": {}}
    # different layer lists per size: compose.py takes one list + overrides → emit one spec per size instead
    return [dict(spec, sizes=[s], layers=layers_by_size[s], name=f"{recipe}") for s in sizes]


def run_compose(spec_path):
    r = subprocess.run([sys.executable, os.path.join(STUDIO_SCRIPTS, "compose.py"), spec_path], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stdout[-800:], r.stderr[-1500:])
        raise SystemExit("compose falhou")
    return [l for l in r.stdout.splitlines() if l.endswith(".png")]


def cmd_build(a):
    b = load_brand(a.brand)
    recipes = list(RECIPES) if a.recipes == "all" else a.recipes.split(",")
    fmts = a.formats.split(",")
    out = os.path.join(b.dir, "aplicacoes")
    pngs = []
    for r in recipes:
        work = os.path.join(out, r)
        specs = spec_for(b, r, fmts, work)
        if not specs:
            continue
        for s in specs:
            p = os.path.join(work, f"peca-{s['sizes'][0]}.json")
            write(p, json.dumps(s, ensure_ascii=False, indent=1))
            pngs += run_compose(p)
        print(f"ok {r}")
    board(pngs, os.path.join(out, "folha.png"), b.name)


def board(pngs, out, title, row_h=420):
    from PIL import Image
    if not pngs:
        return
    ims = [Image.open(p).convert("RGB") for p in pngs]
    ims = [im.resize((max(1, int(row_h * im.width / im.height)), row_h)) for im in ims]
    rows, cur, wmax = [], [], 2400
    for im in ims:
        if cur and sum(i.width + 16 for i in cur) + im.width > wmax:
            rows.append(cur)
            cur = []
        cur.append(im)
    rows.append(cur)
    W = max(sum(i.width + 16 for i in r) for r in rows) + 16
    canvas = Image.new("RGB", (W, len(rows) * (row_h + 16) + 16), (226, 226, 222))
    y = 16
    for r in rows:
        x = 16
        for im in r:
            canvas.paste(im, (x, y))
            x += im.width + 16
        y += row_h + 16
    canvas.save(out)
    print("folha:", out)


# ------------------------------------------------------------------ stress test
def cmd_stress(a):
    import elements
    b = load_brand(a.brand)
    ink, paper, brand = b.colour("ink"), b.colour("paper", "#F4F3EF"), b.colour("brand")
    sym = primitive(b)
    logo = logo_path(b)
    mark = b.symbol() or sym        # favicon/avatar: the compact mark, not the long wordmark
    st = open(sym, encoding="utf-8").read()
    mt = open(mark, encoding="utf-8").read()
    lt = open(logo, encoding="utf-8").read()
    S = 520
    cells = []

    def cell(title, body_svg, bg="#FFFFFF"):
        cells.append((title, wrap_svg(S, S, body_svg, bg=bg)))

    def place(svg_text, x, y, w, h, colour=None):
        s = solid(svg_text, colour) if colour else svg_text
        vx, vy, vw, vh = viewbox(s)
        return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vx} {vy} {vw} {vh}" '
                f'preserveAspectRatio="xMidYMid meet">{svg_inner(s)}</svg>')
    # 1 favicon 16/32/48 rendered as pixels
    import io
    from PIL import Image
    fav = []
    for i, px in enumerate((16, 32, 48)):
        png = svg_to_png(wrap_svg(100, 100, place(mt, 6, 6, 88, 88, ink), bg="#FFFFFF"), width=px)
        im = Image.open(io.BytesIO(png)).convert("RGB").resize((px * 4, px * 4), Image.NEAREST)
        tmp = os.path.join(b.dir, "aplicacoes", f"_fav{px}.png")
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        im.save(tmp)
        import base64
        fav.append(f'<image x="{30 + i * 160}" y="{200 - px * 2}" width="{px * 4}" height="{px * 4}" '
                   f'href="data:image/png;base64,{base64.b64encode(open(tmp, "rb").read()).decode()}" '
                   f'style="image-rendering:pixelated"/>')
        os.remove(tmp)
    cell("favicon 16·32·48 px", "".join(fav))
    cell("avatar redondo", f'<circle cx="{S / 2}" cy="{S / 2}" r="{S * 0.42}" fill="{brand}"/>' +
         place(mt, S * 0.24, S * 0.24, S * 0.52, S * 0.52, ink_on(brand, paper, ink)), "#E9E9E6")
    cell("carimbo 1 cor", place(lt, 40, S * 0.35, S - 80, S * 0.3, "#2B3A8C"), "#F1ECE0")
    cell("negativo sobre preto", place(lt, 40, S * 0.35, S - 80, S * 0.3, paper), ink)
    # 5 outdoor seen from far: wide canvas then shrunk
    g = elements.svg_geometry(sym)
    body, W, H = elements.op_crop(g, vivid_on(ink, [brand, b.colour("accent", brand), paper]), ink, scale=1.25,
                                  cx=0.85, cy=0.6, aspect="3:1")
    far = wrap_svg(W, H, f'<rect width="{W}" height="{H}" fill="{ink}"/>' + body + place(lt, 40, H * 0.6, W * 0.35, H * 0.3, paper))
    cell("outdoor 3:1 visto de longe", place(far, 60, S * 0.42, S - 120, (S - 120) / 3) +
         f'<rect x="60" y="{S * 0.42}" width="{S - 120}" height="{(S - 120) / 3}" fill="none" stroke="#999"/>', "#CFD6DA")
    # 6 story with app UI on top
    ui = (f'<rect x="150" y="20" width="220" height="480" rx="18" fill="{ink}"/>' +
          place(lt, 175, 230, 170, 60, paper) +
          f'<rect x="150" y="20" width="220" height="70" rx="18" fill="#000" opacity="0.35"/>'
          f'<rect x="150" y="410" width="220" height="90" rx="18" fill="#000" opacity="0.35"/>'
          f'<rect x="165" y="35" width="190" height="4" fill="#fff" opacity="0.8"/>'
          f'<circle cx="178" cy="62" r="11" fill="#fff" opacity="0.8"/>'
          f'<rect x="165" y="440" width="150" height="30" rx="15" fill="none" stroke="#fff" opacity="0.8"/>')
    cell("story com interface do app", ui, "#E9E9E6")
    cell("co-branding", place(lt, 40, S * 0.4, S * 0.4, S * 0.2, ink) +
         f'<rect x="{S / 2 - 1}" y="{S * 0.36}" width="2" height="{S * 0.28}" fill="{ink}"/>' +
         f'<rect x="{S * 0.56}" y="{S * 0.43}" width="{S * 0.36}" height="{S * 0.14}" fill="none" stroke="{ink}" '
         f'stroke-dasharray="6 6"/>' + text_path("PARCEIRO", 16, S * 0.74, S * 0.515, ink, UI_FONT, 0.1, "middle"))
    # 8 over a busy photo-like texture
    import random
    rnd = random.Random(3)
    noise = "".join(f'<circle cx="{rnd.random() * S:.0f}" cy="{rnd.random() * S:.0f}" r="{rnd.random() * 40 + 4:.0f}" '
                    f'fill="{rnd.choice(["#7A6A55", "#C9B8A0", "#3E4A3D", "#E8DCC8", "#2A2622"])}" opacity="0.8"/>'
                    for _ in range(260))
    cell("sobre foto movimentada", noise + place(lt, 50, S * 0.4, S - 100, S * 0.22, paper))
    # 9 merch: cap-ish front panel + tote outline
    cell("merch (bordado pequeno)", f'<path d="M80 330 Q260 120 440 330 Z" fill="{ink}"/>'
         f'<rect x="60" y="326" width="400" height="22" rx="11" fill="{ink}"/>' + place(st, 225, 230, 70, 70, brand))
    # 10 pattern on packaging
    pat = next((dv for dv in (b.get("devices") or []) if dv["op"] in ("halftone", "hatch", "repeat", "contour")), None)
    pbody, pw, ph = elements.OPS[pat["op"] if pat else "repeat"](g, brand, None, **(pat.get("params", {}) if pat else
                                                                                   {"mode": "grid", "n": 10}))
    cell("padrão na embalagem", f'<rect x="110" y="60" width="300" height="400" rx="10" fill="{ink}"/>' +
         f'<svg x="110" y="60" width="300" height="400" viewBox="0 0 {pw} {ph}" preserveAspectRatio="xMidYMid slice">'
         f'{pbody}</svg>' + f'<rect x="150" y="330" width="220" height="80" fill="{paper}"/>' +
         place(lt, 165, 345, 190, 50, ink))
    from _base import sheet
    out = os.path.join(b.dir, "aplicacoes", "estresse.png")
    sheet(out, cells, cols=5, cell=420, title=f"{b.name} · teste de estresse (10 aplicações)")
    print("folha:", out)


def cmd_list(a):
    for k, v in RECIPES.items():
        print(f"{k:<13} {v}")
    print("formatos:", ", ".join(f"{k} {w}×{h}" for k, (w, h) in FORMATS.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("build"); p.add_argument("brand"); p.add_argument("--recipes", default="all")
    p.add_argument("--formats", default="post,feed,story,banner"); p.set_defaults(fn=cmd_build)
    p = sp.add_parser("stress"); p.add_argument("brand"); p.set_defaults(fn=cmd_stress)
    p = sp.add_parser("list"); p.set_defaults(fn=cmd_list)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
