"""Catálogo visual da biblioteca de elementos: uma folha por família (cada elemento num cartão com nome e nota).

  cd scripts   # na raiz da skill
  python -m ornamentos.catalogo [-o pasta] [--produto todos|linha-a|linha-b|linha-c] [--familia nome] [--raio 28]
      [--revisao]   → também <pasta>/revisao/<familia>-NN.png: 6 por página, grandes, numerados (revisão um a um)
Saída: <pasta>/<familia>.png + _indice.png (contagem) + _avisos.txt (amostras que falharam).
"""
import argparse
import base64
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ornamentos import carregar_tudo, ficha_exemplo  # noqa: E402
from ornamentos.nucleo import REGISTRO  # noqa: E402


def _url(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


def conferir(el, M=40):
    """Tinta fora da caixa (viewBox), elemento vazio, alto demais para o cartão (> 364 px). Devolve lista de avisos."""
    import io
    import re
    import numpy as np
    import resvg_py
    from PIL import Image
    W, H = el.w, el.h
    svg = re.sub(r'viewBox="[^"]*" width="[^"]*" height="[^"]*"',
                 f'viewBox="{-M} {-M} {W + 2 * M:.2f} {H + 2 * M:.2f}" width="{W + 2 * M:.0f}" height="{H + 2 * M:.0f}"',
                 el.svg, count=1)
    try:
        png = bytes(resvg_py.svg_to_bytes(svg_string=svg))
    except Exception as e:
        return [f"ERRO resvg: {e}"]
    a = np.array(Image.open(io.BytesIO(png)).convert("RGBA"))[..., 3].astype(float)
    av = []
    fora = a.copy()
    fora[max(0, M - 1):M + int(round(H)) + 2, max(0, M - 1):M + int(round(W)) + 2] = 0
    n = int((fora > 40).sum())
    if n > 30:
        ys, xs = np.nonzero(fora > 40)
        lado = [n_ for n_, ok in (("esq", xs.min() < M), ("dir", xs.max() > M + W), ("topo", ys.min() < M),
                                  ("base", ys.max() > M + H)) if ok]
        av.append(f"tinta fora da caixa ({n} px · {','.join(lado)})")
    if a[M:M + int(H), M:M + int(W)].max() < 10:
        av.append("vazio")
    if H > 364 and W / max(H, 1) * 364 < 60:
        av.append(f"alto e fino demais para o cartão (h={H:.0f})")
    return av


def revisao(familia, itens, ficha, pasta, por_pagina=6):
    """Páginas de REVISÃO: 6 elementos por imagem (3 × 2), cada um grande (≈ 760 px), numerado, no fundo certo e
    também no fundo oposto (miniatura), com régua de caixa (tracejado = viewBox). Para olhar UM A UM."""
    from referencia import _png, _fontes_base
    os.makedirs(pasta, exist_ok=True)
    saidas = []
    for pg in range(0, len(itens), por_pagina):
        cards = []
        for k, el in enumerate(itens[pg:pg + por_pagina], pg + 1):
            claro = el.familia.endswith("-claro") or getattr(el, "fundo_claro", False)
            bg, bg2 = (ficha.papel, ficha.fundo) if claro else (ficha.fundo, ficha.papel)
            cards.append(f'<div class="c"><div class="v" style="background:{bg}"><img class="cx" src="{_url(el.svg)}">'
                         f'<div class="m" style="background:{bg2}"><img src="{_url(el.svg)}"></div></div>'
                         f'<div class="t"><b>{k:03d} · {el.nome}</b><span>{el.w:.0f} × {el.h:.0f} · {el.nota}</span></div></div>')
        html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{_fontes_base()}"
                "*{box-sizing:border-box;margin:0;padding:0}body{width:2400px;background:#EDEAE3;color:#121212;font-family:V;padding:40px}"
                "h1{font:800 40px/1 V;margin-bottom:24px}.g{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}"
                ".c{background:#fff;border:1.5px solid #cfcac0;border-radius:10px;overflow:hidden}"
                ".v{height:640px;display:grid;place-items:center;padding:40px;position:relative}"
                ".v img.cx{max-width:100%;max-height:560px;display:block;outline:1px dashed rgba(255,0,128,.55)}"
                ".m{position:absolute;right:10px;bottom:10px;width:150px;height:110px;display:grid;place-items:center;"
                "padding:8px;border-radius:6px;overflow:hidden}.m img{max-width:134px;max-height:94px;display:block}"
                ".t{padding:12px 16px 14px;border-top:1.5px solid #e2ddd3}.t b{font:700 22px/1.2 V;display:block}"
                ".t span{font:500 15px/1.35 V;color:#666;display:block;margin-top:4px}"
                f"</style></head><body><h1>{familia} · {pg + 1}–{min(len(itens), pg + por_pagina)} de {len(itens)}</h1>"
                f"<div class='g'>{''.join(cards)}</div></body></html>")
        out = os.path.join(pasta, f"{familia}-{pg // por_pagina + 1:02d}.png")
        _png(html, out)
        saidas.append(out)
    return saidas


def folha(familia, itens, ficha, out):
    from referencia import _png, _fontes_base
    cards = []
    for el in itens:
        claro = el.familia.endswith("-claro") or getattr(el, "fundo_claro", False)
        bg = ficha.papel if claro else ficha.fundo
        cards.append(f'<div class="c"><div class="v" style="background:{bg}"><img src="{_url(el.svg)}"></div>'
                     f'<div class="t"><b>{el.nome}</b><span>{el.nota}</span></div></div>')
    html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{_fontes_base()}"
            "*{box-sizing:border-box;margin:0;padding:0}body{width:2400px;background:#EDEAE3;color:#121212;font-family:V;padding:72px}"
            "h1{font:800 64px/1 V;letter-spacing:-.02em}p.s{font:500 22px/1.4 M;font-stretch:80%;color:#666;margin:14px 0 40px}"
            ".g{display:grid;grid-template-columns:repeat(4,1fr);gap:22px}.c{background:#fff;border:1.5px solid #cfcac0;border-radius:14px;overflow:hidden}"
            ".v{height:420px;display:grid;place-items:center;padding:28px}.v img{max-width:100%;max-height:364px;display:block}"
            ".t{padding:14px 18px 16px;border-top:1.5px solid #e2ddd3}.t b{font:700 19px/1.2 V;display:block}"
            ".t span{font:500 15px/1.35 V;color:#666;display:block;margin-top:4px}"
            f"</style></head><body><h1>{familia}</h1><p class='s'>{len(itens)} elementos · ficha: {ficha.nome} · raio {ficha.raio:g} · traço {ficha.traco:g} · unidade {ficha.unidade:g}</p>"
            f"<div class='g'>{''.join(cards)}</div></body></html>")
    _png(html, out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", default=os.path.join(os.environ.get("TEMP", "."), "ornamentos-catalogo"))
    ap.add_argument("--produto", default="todos")
    ap.add_argument("--familia")
    ap.add_argument("--raio", type=float, default=28.0)
    ap.add_argument("--revisao", action="store_true", help="páginas de 6 elementos grandes e numerados (olhar um a um)")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    carregar_tudo(a.familia)
    ficha = ficha_exemplo(a.produto, a.raio)
    os.makedirs(a.o, exist_ok=True)
    avisos, total = [], 0
    for fam, gens in sorted(REGISTRO.items()):
        if a.familia and fam != a.familia:
            continue
        itens = []
        for nome, fn in gens:
            try:
                itens += fn(ficha)
            except Exception as e:
                avisos.append(f"{fam}/{nome}: {e}\n{traceback.format_exc()}")
        for el in itens:
            avisos += [f"{fam}/{el.nome}: {x}" for x in conferir(el)]
        if itens and a.revisao:
            revisao(fam, itens, ficha, os.path.join(a.o, "revisao"))
        if itens:
            folha(fam, itens, ficha, os.path.join(a.o, f"{fam}.png"))
            total += len(itens)
            print(f"{fam}: {len(itens)}")
    open(os.path.join(a.o, "_avisos.txt"), "w", encoding="utf-8").write("\n".join(avisos) or "nenhum")
    print("TOTAL", total, "· avisos:", len(avisos), "→", a.o)
