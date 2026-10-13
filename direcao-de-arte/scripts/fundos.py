"""fundos.py — FUNDOS e TEXTURAS por código (numpy + PIL), sem faixas de degradê (dither + grão).

Uso em Python:  from fundos import *;  im = estudio(1080, 1350, "#04163F", luz="#FEBD10", x=0.7, y=0.25)
                im = grao(im, 0.05); im.save("fundo.png")
CLI:            python fundos.py folha <saida.png> --cores "#04163F,#FEBD10,#FFFFFF"   (amostra de tudo)

Receitas (todas devolvem PIL.Image RGB; tamanho em px; cores em HEX):
  liso(W,H,cor)                                   cor chapada
  estudio(W,H,cor,luz=None,x,y,raio,forca)        "ciclorama": poça de luz suave + vinheta, sem banding
  degrade(W,H,c0,c1,angulo)                       linear com dither
  vinheta(im,forca)                               escurece as bordas (elíptica)
  grao(im,qtd=0.04,tam=1.0,mono=True)             grão de filme (gaussiano), 2–8% = premium; > 10% = sujo
  linhas(im,periodo=4,opac=0.06,cor="#000")       linhas de varredura (tela/transmissão)
  papel(W,H,cor,fibras=0.5)                       papel com fibra e leve variação (tema claro, "documento")
  estatica(W,H,cor0,cor1,densidade)              chuvisco de sinal (usar pequeno, como faixa ou transição)
  barras(W,H,cores)                               barras de teste (SMPTE) reinterpretadas nas cores da marca
  meio_tom(img,celula,angulo,tinta,papel)         retícula de uma foto (usa fx.py)
Regras: grão por cima de TUDO menos do texto pequeno (texto fica nítido: aplique o grão no fundo e depois componha o
SVG por cima); luz sempre fora do centro (terço), nunca no meio; vinheta ≤ 0,35.
"""
import os
import sys

import numpy as np
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):  # console do Windows (cp1252) quebra com acentos e setas
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


HERE = os.path.dirname(os.path.abspath(__file__))


def _rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def _out(a, dither=True, seed=7):
    """float 0–255 → uint8 com dither (ruído triangular de ±0,5 nível): mata as faixas do degradê."""
    if dither:
        rng = np.random.default_rng(seed)
        a = a + (rng.random(a.shape) - rng.random(a.shape))
    return Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8))


def liso(W, H, cor):
    return Image.new("RGB", (W, H), cor)


def _campo(W, H, x, y, raio):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    d = np.hypot((xx - x * W) / (raio * max(W, H)), (yy - y * H) / (raio * max(W, H)))
    return np.clip(1 - d, 0, 1) ** 2.2            # queda suave (não linear: luz real)


def estudio(W, H, cor, luz=None, x=0.68, y=0.28, raio=0.75, forca=0.22, vinh=0.28, seed=7):
    """Fundo de estúdio: cor base + poça de luz (cor da luz ou a base clareada) + vinheta. Sem banding."""
    base = _rgb(cor)
    lc = _rgb(luz) if luz else np.minimum(255, base * 1.9 + 18)
    f = _campo(W, H, x, y, raio)[..., None] * forca
    a = base * (1 - f) + lc * f
    im = _out(a, seed=seed)
    return vinheta(im, vinh) if vinh else im


def degrade(W, H, c0, c1, angulo=90, seed=7):
    t = np.radians(angulo)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    p = (xx / W - 0.5) * np.cos(t) + (yy / H - 0.5) * np.sin(t)
    p = (p - p.min()) / (p.max() - p.min())
    a = _rgb(c0) * (1 - p[..., None]) + _rgb(c1) * p[..., None]
    return _out(a, seed=seed)


def vinheta(im, forca=0.28):
    W, H = im.size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    d = np.hypot((xx / W - 0.5) * 2, (yy / H - 0.5) * 2) / np.sqrt(2)
    k = 1 - forca * np.clip(d, 0, 1) ** 2.4
    return _out(np.asarray(im).astype(np.float64) * k[..., None])


def grao(im, qtd=0.04, tam=1.0, mono=True, seed=11):
    """Grão de filme: ruído gaussiano (σ = qtd × 255), tamanho do grão por reamostragem. Mais forte nos meios-tons
    (como filme), quase nada no preto e no branco puros."""
    W, H = im.size
    rng = np.random.default_rng(seed)
    w, h = max(1, int(W / tam)), max(1, int(H / tam))
    n = rng.normal(0, 1, (h, w) if mono else (h, w, 3))
    if tam != 1.0:
        n = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize(
            (W, H), Image.BILINEAR)).astype(np.float64) / 255 * 2 - 1
        n *= 1.7
    a = np.asarray(im.convert("RGB")).astype(np.float64)
    lum = a.mean(axis=2, keepdims=True) / 255
    peso = 0.35 + 0.65 * (4 * lum * (1 - lum))      # meios-tons recebem mais
    nn = n[..., None] if mono else n
    return _out(a + nn * qtd * 255 * peso, dither=False)


def linhas(im, periodo=4, opac=0.06, cor="#000000", espessura=1):
    a = np.asarray(im.convert("RGB")).astype(np.float64)
    H = a.shape[0]
    m = np.zeros(H)
    for k in range(espessura):
        m[k::periodo] = 1
    c = _rgb(cor)
    a = a * (1 - opac * m[:, None, None]) + c * (opac * m[:, None, None])
    return _out(a, dither=False)


def papel(W, H, cor="#ECE7DC", fibras=0.5, seed=5):
    """Papel: variação de baixa frequência (manchas leves) + fibras finas alongadas + grão fino."""
    rng = np.random.default_rng(seed)
    base = _rgb(cor)
    low = rng.normal(0, 1, (H // 64 + 2, W // 64 + 2))
    low = np.asarray(Image.fromarray(((low - low.min()) / (np.ptp(low) + 1e-9) * 255).astype(np.uint8)).resize(
        (W, H), Image.BICUBIC)).astype(np.float64) / 255 - 0.5
    fib = rng.normal(0, 1, (H // 2, W // 12))
    fib = np.asarray(Image.fromarray(((fib - fib.min()) / (np.ptp(fib) + 1e-9) * 255).astype(np.uint8)).resize(
        (W, H), Image.BILINEAR)).astype(np.float64) / 255 - 0.5
    a = base[None, None, :] * (1 + 0.035 * low[..., None] + 0.02 * fibras * fib[..., None])
    return grao(_out(a), 0.025, 1.0)


def estatica(W, H, cor0="#000000", cor1="#FFFFFF", densidade=0.5, seed=3):
    rng = np.random.default_rng(seed)
    n = rng.random((H, W // 2 + 1))
    n = np.repeat(n, 2, axis=1)[:, :W]
    t = (n > (1 - densidade)).astype(np.float64)[..., None]
    a = _rgb(cor0) * (1 - t) + _rgb(cor1) * t
    return _out(a, dither=False)


def barras(W, H, cores):
    """Barras de teste (SMPTE) reinterpretadas: as cores da marca em faixas verticais iguais; faixa inferior de 1/6
    com os tons invertidos (como o padrão original)."""
    im = Image.new("RGB", (W, H))
    n = len(cores)
    a = np.zeros((H, W, 3))
    for i, c in enumerate(cores):
        x0, x1 = int(i * W / n), int((i + 1) * W / n)
        a[: int(H * 5 / 6), x0:x1] = _rgb(c)
        a[int(H * 5 / 6):, x0:x1] = _rgb(cores[n - 1 - i])
    return _out(a, dither=False)


def meio_tom(src, celula=10, angulo=45, tinta="#111111", papel_="#F2EEE6"):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "brand-studio", "scripts"))
    import fx  # noqa: E402
    im = Image.open(src).convert("RGB") if isinstance(src, str) else src
    return fx.halftone(im, celula, angulo, tinta, papel_) if hasattr(fx, "halftone") else im


def folha(out, cores):
    """Amostra de todos os fundos nas cores dadas (1ª = base, 2ª = destaque, 3ª = claro)."""
    from PIL import ImageDraw
    base, dest, claro = (cores + ["#FFFFFF", "#FFFFFF"])[:3]
    w, h = 540, 675
    items = [("estúdio", estudio(w, h, base, dest, forca=0.18)),
             ("estúdio + grão 5%", grao(estudio(w, h, base, dest, forca=0.18), 0.05)),
             ("linhas de varredura", linhas(grao(estudio(w, h, base, None, forca=0.25), 0.04), 4, 0.10)),
             ("papel", papel(w, h, "#ECE7DC")),
             ("degradê com dither", grao(degrade(w, h, base, dest, 120), 0.03)),
             ("estática (faixa)", estatica(w, h, base, claro, 0.35)),
             ("barras (marca)", barras(w, h, [claro, dest, base, "#7A7A7A", dest, claro, base])),
             ("vinheta forte", vinheta(liso(w, h, base), 0.45))]
    S = Image.new("RGB", (4 * (w + 20) + 20, 2 * (h + 60) + 20), (226, 226, 222))
    dr = ImageDraw.Draw(S)
    for i, (lab, im) in enumerate(items):
        x, y = 20 + (i % 4) * (w + 20), 20 + (i // 4) * (h + 60)
        S.paste(im, (x, y + 40))
        dr.text((x, y + 10), lab, fill=(30, 30, 30))
    S.save(out)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    f = sub.add_parser("folha")
    f.add_argument("out")
    f.add_argument("--cores", default="#111111,#E5322D,#F4F3EF")
    a = ap.parse_args()
    if a.cmd == "folha":
        print(folha(a.out, a.cores.split(",")))
    else:
        print(__doc__)
