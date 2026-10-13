"""Variações COM LIMITE para comparar: até 4 opções por eixo (a atual + 3), uma folha por eixo, sem refino.
Aplica cada opção nos MESMOS modelos de peça da marca (modelos.py), então a comparação é justa.

Uso:
  python variacoes.py fontes <brand_dir> --opcoes "Anybody:900,Bricolage Grotesque:800,Chivo:900,Unbounded:800"
  python variacoes.py cores <brand_dir> --opcoes "Âmbar=#FFA51F,#151515,#F3EFE6,#2C4BFF;Vermelho=#FF4A2E,#151515,#F3EFE6,#2C4BFF"
                         (cada opção: Nome=brand,ink,paper,accent)
  python variacoes.py logo <brand_dir> --arquivos logo/a.svg,logo/b.svg,logo/c.svg
                         (cada assinatura sobre brand, ink e paper + como fica com 32 px de altura)
  python variacoes.py elementos <brand_dir> [--ops contour,slice,halftone,stack,modules,outline] [--n 4]
Opções comuns: --modelos id1,id2 (padrão: os 2 primeiros modelos com "sample") · --formato feed · --sem-limite
Saída: <brand_dir>/variacoes/<eixo>.png. Depois: a pessoa escolhe (ou a arena: arena.py add com cada coluna) e só o
escolhido é refinado. Avisos de contraste < 3:1 saem no terminal (texto sobre fundo de cada modelo).
"""
import argparse
import copy
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelos as MD  # noqa: E402
from _base import UI_FONT_BOLD, contrast, font_path, load_brand, sheet, svg_inner, svg_to_png, viewbox, wrap_svg  # noqa: E402

LIMIT = 4


def _font(size):
    from PIL import ImageFont
    return ImageFont.truetype(font_path(UI_FONT_BOLD), size)


def _limit(opts, a):
    if len(opts) > LIMIT and not a.sem_limite:
        print(f"limite: {len(opts)} opções → usando as {LIMIT} primeiras (--sem-limite para todas)")
        return opts[:LIMIT]
    return opts


def _templates(b, a):
    ts = [t for t in b.get("templates") or [] if t.get("sample")]
    if a.modelos:
        ids = a.modelos.split(",")
        ts = [t for t in b.get("templates") or [] if t.get("id") in ids]
    if not ts:
        raise SystemExit("defina brand.json templates (com sample) antes — veja modelos.py tipos")
    return ts if a.modelos else ts[:2]


def _png(svg, parts, W, H, w):
    import tempfile
    from PIL import Image
    tmp = os.path.join(tempfile.gettempdir(), f"_var_{os.getpid()}.png")
    svg_to_png(svg, tmp)
    if parts:
        MD.composite_photo(tmp, parts, W, H)
    im = Image.open(tmp).convert("RGB")
    os.remove(tmp)
    return im.resize((w, int(w * H / W)))


def grid(cols, out, w=420, label_h=56):
    """cols = [(rótulo, [PIL.Image, …]), …] → uma coluna por opção, uma linha por modelo."""
    from PIL import Image, ImageDraw
    rows = max(len(c[1]) for c in cols)
    hs = [max(c[1][r].height for c in cols if r < len(c[1])) for r in range(rows)]
    S = Image.new("RGB", (20 + len(cols) * (w + 20), label_h + 20 + sum(h + 20 for h in hs)), (226, 226, 222))
    d = ImageDraw.Draw(S)
    for ci, (name, ims) in enumerate(cols):
        x = 20 + ci * (w + 20)
        d.text((x, 16), name, fill=(20, 20, 20), font=_font(24))
        y = label_h + 20
        for r, im in enumerate(ims):
            S.paste(im, (x, y))
            y += hs[r] + 20
    os.makedirs(os.path.dirname(out), exist_ok=True)
    S.save(out)
    return out


def _check(ctx, t, label):
    c = t.get("colors") or {}
    bg, fg = ctx.col(c.get("bg"), "brand"), ctx.col(c.get("fg"), "ink")
    r = contrast(bg, fg)
    if r < 3:
        print(f"  aviso {label} · {t['id']}: texto {fg} sobre {bg} = {r:.1f}:1 (< 3) — ilegível, não é proposta")


def cmd_fontes(a):
    b = load_brand(a.brand)
    ts = _templates(b, a)
    W, H = MD.FORMATS[a.formato]
    cols = []
    for spec in _limit([o.strip() for o in a.opcoes.split(",") if o.strip()], a):
        ctx = MD.Ctx(b, {"display": spec})
        ims = []
        for t in ts:
            s = t["sample"]
            svg, parts = MD.render_one(ctx, t, a.formato, s.get("texto", ""), s.get("info", ""),
                                       b.path(s["foto"]) if s.get("foto") else None, s.get("numero"))
            ims.append(_png(svg, parts, W, H, 420))
        cols.append((spec, ims))
        print("ok", spec)
    print(grid(cols, os.path.join(b.dir, "variacoes", "fontes.png")))


def cmd_cores(a):
    b = load_brand(a.brand)
    ts = _templates(b, a)
    W, H = MD.FORMATS[a.formato]
    cols = []
    for opt in _limit([o.strip() for o in a.opcoes.split(";") if o.strip()], a):
        name, hexes = opt.split("=", 1)
        hx = [h.strip() for h in hexes.split(",")]
        roles = dict(zip(("brand", "ink", "paper", "accent"), hx))
        ctx = MD.Ctx(b, {"colors": roles})
        ims = []
        for t in ts:
            _check(ctx, t, name)
            s = t["sample"]
            svg, parts = MD.render_one(ctx, t, a.formato, s.get("texto", ""), s.get("info", ""),
                                       b.path(s["foto"]) if s.get("foto") else None, s.get("numero"))
            ims.append(_png(svg, parts, W, H, 380))
        cols.append((name, ims))
        print("ok", name)
    print(grid(cols, os.path.join(b.dir, "variacoes", "cores.png"), w=380))


def cmd_logo(a):
    """Uma linha por assinatura: sobre brand, ink e paper + 32 px de altura ampliado 3× (teste de tamanho mínimo)."""
    from PIL import Image, ImageDraw
    b = load_brand(a.brand)
    files = _limit([b.path(f.strip()) for f in a.arquivos.split(",") if f.strip()], a)
    bgs = [(b.colour("brand"), b.colour("ink")), (b.colour("ink"), b.colour("paper")),
           (b.colour("paper"), b.colour("ink"))]
    cw, ch, lw = 760, 300, 240
    rows = []
    for f in files:
        svg = open(f, encoding="utf-8").read()
        vx, vy, vw, vh = viewbox(svg)
        cells = []
        for bg, fg in bgs:
            k = min((cw - 120) / vw, (ch - 100) / vh)
            body = (f'<rect width="{cw}" height="{ch}" fill="{bg}"/><g transform="translate({(cw - vw * k) / 2:.1f} '
                    f'{(ch - vh * k) / 2:.1f}) scale({k:.5f}) translate({-vx} {-vy})" fill="{fg}">'
                    f'{MD._recolor(svg, fg)}</g>')
            cells.append(_png(wrap_svg(cw, ch, body), None, cw, ch, cw))
        small = _png(wrap_svg(vw, vh, f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="#fff"/>'
                              f'<g fill="#111">{MD._recolor(svg, "#111")}</g>'), None, vw, vh, max(8, int(vw * 32 / vh)))
        small = small.resize((small.width * 3, small.height * 3), Image.NEAREST)
        rows.append((os.path.basename(f), cells, small))
    W = lw + 3 * (cw + 20) + max(r[2].width for r in rows) + 40
    S = Image.new("RGB", (W, 20 + len(rows) * (ch + 20)), (226, 226, 222))
    d = ImageDraw.Draw(S)
    for i, (name, cells, small) in enumerate(rows):
        y = 20 + i * (ch + 20)
        d.text((20, y + ch / 2 - 14), name[:22], fill=(20, 20, 20), font=_font(24))
        for j, c in enumerate(cells):
            S.paste(c, (lw + j * (cw + 20), y))
        S.paste(small, (lw + 3 * (cw + 20), int(y + ch / 2 - small.height / 2)))
    out = os.path.join(b.dir, "variacoes", "logo.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    S.save(out)
    print(out)


def cmd_elementos(a):
    import subprocess
    b = load_brand(a.brand)
    prim = b.primitive()
    out = os.path.join(b.dir, "variacoes", "elementos")
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "elements.py"),
                    "explore", prim, "-o", out, "--ops", a.ops, "--n", str(a.n), "--fg", b.colour("ink"),
                    "--bg", b.colour("brand")], check=True)
    fs = sorted(glob.glob(os.path.join(out, "*.svg")))
    print(sheet(os.path.join(b.dir, "variacoes", "elementos.png"), [(os.path.basename(f)[:-4], f) for f in fs],
                cols=min(5, len(fs)), cell=300, title=f"{b.name} · elementos (explorar)"))
    print("escolha até 3 novos → brand.json devices (op + params do rótulo) → elements.py build")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name, fn, need in (("fontes", cmd_fontes, "--opcoes"), ("cores", cmd_cores, "--opcoes"),
                           ("logo", cmd_logo, "--arquivos"), ("elementos", cmd_elementos, None)):
        p = sp.add_parser(name)
        p.add_argument("brand")
        if need:
            p.add_argument(need, required=True)
        p.add_argument("--modelos")
        p.add_argument("--formato", default="feed", choices=list(MD.FORMATS))
        p.add_argument("--sem-limite", action="store_true")
        if name == "elementos":
            p.add_argument("--ops", default="contour,slice,halftone,stack,modules,outline")
            p.add_argument("--n", type=int, default=4)
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
