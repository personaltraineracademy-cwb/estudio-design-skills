"""Controle de qualidade de logo pronto (nosso ou de terceiros): o que o olho esquece.

Nasceu do estudo de logos reais de terceiros (references/logo-anticliche.md): um O cortado na borda, arte vazando
do viewBox, uma versão que só funciona em fundo de cor média e símbolo em traço fino que some pequeno.

Para cada SVG:
  1. Bordas — arte que VAZA do viewBox (vai ser cortada no navegador/Express) e arte ENCOSTADA na borda (a folha
     mostra a faixa da borda ampliada: confira se nenhuma letra redonda ficou reta = cortada para justificar).
  2. Cores reais (renderizadas — pega as que estão em <style>/classe) e em que FUNDO cada versão funciona:
     branco, claro, médio, escuro + cores da marca (--bg). "some parte" = alguma cor do logo < 1,5:1 com o fundo.
  3. Folha PNG: o logo em cada fundo, a escada 24/32/48/64 px (pixel real, ampliado 2×) e as bordas ampliadas.

Uso
  python logo_qc.py a.svg b.svg [--bg "#DD2A1B,#0071BC"] [--sheet qc.png]
  python logo_qc.py "pasta/*.svg" --sheet qc.png      (aceita curinga)
"""
import argparse
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import contrast, rgb_to_hex, svg_to_png, viewbox  # noqa: E402

FUNDOS = {"branco": "#FFFFFF", "claro": "#F5F5F2", "medio": "#808080", "escuro": "#1A1A1A"}


def _img(svg_text, width=None, height=None):
    from PIL import Image
    return Image.open(io.BytesIO(svg_to_png(svg=svg_text, width=width, height=height))).convert("RGBA")


def _com_viewbox(svg_text, vb, px_w):
    """Same SVG with a new viewBox and an explicit pixel size (resvg rounds small intrinsic sizes — this avoids
    measuring errors). Returns (svg, scale px per unit)."""
    x, y, w, h = vb
    px_h = max(1, round(px_w * h / w))
    m = re.search(r"<svg\b[^>]*>", svg_text)
    tag = re.sub(r'\s(?:width|height|viewBox|preserveAspectRatio)="[^"]*"', "", m[0])
    tag = tag.replace("<svg", f'<svg viewBox="{x} {y} {w} {h}" width="{px_w}" height="{px_h}" '
                              f'preserveAspectRatio="none"', 1)
    return svg_text[:m.start()] + tag + svg_text[m.end():], px_w / w


def bordas(svg_text):
    import numpy as np
    x, y, w, h = viewbox(svg_text)
    pad = 0.15
    big, k = _com_viewbox(svg_text, (x - w * pad, y - h * pad, w * (1 + 2 * pad), h * (1 + 2 * pad)), 3000)
    a = np.array(_img(big))[:, :, 3] > 8
    if not a.any():
        return {}
    ys, xs = np.where(a)
    ky = a.shape[0] / (h * (1 + 2 * pad))
    bx0, bx1 = xs.min() / k + x - w * pad, (xs.max() + 1) / k + x - w * pad
    by0, by1 = ys.min() / ky + y - h * pad, (ys.max() + 1) / ky + y - h * pad
    tol = 0.002 * max(w, h)
    vaza = {lado: round(float(v), 2) for lado, v in (("esq", x - bx0), ("dir", bx1 - (x + w)), ("topo", y - by0),
                                              ("base", by1 - (y + h))) if v > tol}
    n = np.array(_img(_com_viewbox(svg_text, (x, y, w, h), 1600)[0]))[:, :, 3] > 128
    enc = {"esq": n[:, 0].mean(), "dir": n[:, -1].mean(), "topo": n[0, :].mean(), "base": n[-1, :].mean()}
    return {"vaza": vaza, "encosta": {k2: round(float(v) * 100) for k2, v in enc.items() if v > 0.04}}


def cores(im, minimo=0.02):
    import numpy as np
    px = np.array(im)
    px = px[px[:, :, 3] > 250][:, :3].astype(int)
    if not len(px):
        return []
    q = (px // 12) * 12 + 6
    vals, cnt = np.unique(q, axis=0, return_counts=True)
    out = []
    for i in np.argsort(-cnt):
        if cnt[i] / len(px) < minimo:
            break
        c = vals[i]
        if all(abs(c - o[0]).sum() > 40 for o in out):
            out.append((c, cnt[i] / len(px)))
    return [(rgb_to_hex(c), round(float(s) * 100)) for c, s in out]


def veredito(cs, fundo):
    r = [(c, s, contrast(c, fundo)) for c, s in cs]
    if not r:
        return "vazio", r
    if all(x[2] < 1.5 for x in r):
        return "invisível", r
    if any(x[2] < 1.5 for x in r):
        return "some parte", r
    if min(x[2] for x in r) < 3:
        return "fraco (<3:1)", r
    return "ok", r


def folha(itens, fundos, out):
    from PIL import Image, ImageDraw, ImageFont
    try:
        f = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        f = ImageFont.load_default()
    linhas = []
    for nome, svg_text, res in itens:
        cel = []
        for fn, hx in fundos.items():
            lg = _img(svg_text, height=90)
            b = Image.new("RGBA", (lg.width + 24, 114), hx)
            b.alpha_composite(lg, (12, 12))
            cel.append((b, f"{fn}: {res['fundos'][fn]}"))
        linhas.append((nome, cel))
        cel = []
        melhor = next((hx for fn, hx in fundos.items() if res["fundos"][fn] == "ok"), list(fundos.values())[0])
        esc = []
        for hh in (24, 32, 48, 64):
            lg = _img(svg_text, height=hh)
            b = Image.new("RGBA", (lg.width + 6, hh + 6), melhor)
            b.alpha_composite(lg, (3, 3))
            esc.append(b.resize((b.width * 2, b.height * 2), Image.NEAREST))
        ew = sum(e.width for e in esc) + 12 * len(esc)
        escada = Image.new("RGBA", (ew, max(e.height for e in esc)), (200, 200, 200, 255))
        xx = 0
        for e in esc:
            escada.alpha_composite(e, (xx, 0))
            xx += e.width + 12
        cel.append((escada, "24/32/48/64 px (2×)"))
        big = _img(svg_text, height=900)
        for lado, box in (("borda esq", (0, 0, int(big.width * 0.06), big.height)),
                          ("borda dir", (int(big.width * 0.94), 0, big.width, big.height))):
            c = big.crop(box)
            b = Image.new("RGBA", c.size, melhor)
            b.alpha_composite(c)
            b.thumbnail((400, 300))
            cel.append((b, lado))
        linhas.append(("", cel))
    W = max(sum(c.width + 16 for c, _ in cel) for _, cel in linhas) + 20
    H = sum(max(c.height for c, _ in cel) + 42 + (22 if nome else 0) for nome, cel in linhas) + 10
    sh = Image.new("RGB", (W, H), (210, 210, 210))
    d = ImageDraw.Draw(sh)
    y = 10
    for nome, cel in linhas:
        if nome:
            d.text((10, y), nome, fill=(0, 0, 0), font=f)
            y += 22
        x = 10
        for c, lab in cel:
            sh.paste(c.convert("RGB"), (x, y))
            d.text((x, y + c.height + 3), lab, fill=(40, 40, 40), font=f)
            x += c.width + 16
        y += max(c.height for c, _ in cel) + 42
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sh.save(out)
    print(f"folha: {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--bg", default="", help="cores extras de fundo, ex. '#DD2A1B,#0071BC'")
    ap.add_argument("--sheet", help="salvar folha PNG")
    a = ap.parse_args()
    fundos = dict(FUNDOS)
    for c in filter(None, (s.strip() for s in a.bg.split(","))):
        fundos[c.upper()] = c
    itens = []
    arquivos = [g for p in a.files for g in (sorted(glob.glob(p)) or [p])]
    for p in arquivos:
        t = open(p, encoding="utf-8").read()
        res = {"bordas": bordas(t), "cores": cores(_img(t, width=1200)), "fundos": {}}
        print(f"\n== {os.path.basename(p)}")
        print("  cores (% da arte): " + ", ".join(f"{c} {s}%" for c, s in res["cores"]))
        for fn, hx in fundos.items():
            v, r = veredito(res["cores"], hx)
            res["fundos"][fn] = v
            print(f"  fundo {fn:8s} {v:13s} " + " · ".join(f"{c} {k:.1f}:1" for c, _, k in r))
        b = res["bordas"]
        if b.get("vaza"):
            print(f"  ATENÇÃO arte vaza do viewBox (será cortada): {b['vaza']} unidades")
        if b.get("encosta"):
            print(f"  encosta na borda (% do lado): {b['encosta']} — olhe a borda ampliada: letra redonda reta = cortada")
        ok = [fn for fn, v in res["fundos"].items() if v == "ok"]
        print(f"  funciona em: {', '.join(ok) if ok else 'NENHUM dos fundos testados'}")
        itens.append((os.path.basename(p), t, res))
    if a.sheet:
        folha(itens, fundos, a.sheet)


if __name__ == "__main__":
    main()
