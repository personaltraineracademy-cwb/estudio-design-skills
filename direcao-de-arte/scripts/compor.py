"""compor.py — biblioteca de COMPOSIÇÃO com craft verificável (usada pelos modelos de peça de qualquer marca).

Tudo é medido na TINTA (o contorno real renderizado), nunca na caixa da fonte. Texto sempre em curvas.
Importe:  sys.path.insert(0, r"<skills>/direcao-de-arte/scripts"); from compor import *

Primitivas
  ink(spec, texto, tr)                 caixa de tinta por unidade de corpo (esq, topo, dir, base; topo negativo)
  linha(spec, texto, x, base, ...)     uma linha com a BORDA DA TINTA em x (largura OU maiúscula; justify)
  tx(spec, texto, x, base, cap, fill, tr, anchor)   linha por maiúscula, anchor start|middle|end (pela tinta)
  quebra(spec, texto, max_w, cap, tr)  quebra pelas regras de leitura do português (menos linhas, mais iguais)
  quebra_sep(texto, spec, max_w, cap, tr, sep=" · ")  listas: quebra só nos separadores
  entrelinha(spec, linhas, cap, ...)   entrelinha uniforme MEDIDA na tinta (acento nunca encosta)
  bloco(...) / altura_bloco(...)       bloco de texto com as duas regras acima
  iguala(spec, texto, ..., alvo)       linha QUASE da largura alvo (< 6%) vira exatamente o alvo (micro-espaçamento)
  palavra(spec, texto, ...)            espaçamento ÓPTICO por par de letras (área), para títulos e logos
  poe(master, x, y, w|h, anchor)       coloca um master (moldura = tinta + 2%) com a tinta exatamente em x,y
  poe_livre(svg, ...)                  coloca SVG de terceiros pela caixa
  recorte(png, cx, base, h)            foto recortada (RGBA) embutida + alfa (o verificador usa)
  Peca(W, H, fundo, formato)           peça com registro de elementos + qa() (margem, zona segura, colisão,
                                       texto sobre a pessoa, bordas QUASE alinhadas)
  FORMATOS                             tamanhos e zonas seguras por canal (Stories, Reels, feed, WhatsApp, live…)
"""
import base64
import io
import os
import re
import sys
import tempfile
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SKILLS, "brand-system", "scripts"))
from _base import font, svg_inner, svg_to_png, viewbox, wrap_svg  # noqa: E402,F401

CURTA = 2      # palavras com até 2 letras não terminam linha (a, é, o, de, um, em…)

# ------------------------------------------------------------------ formatos + zonas seguras
# zona = (topo, baixo, esquerda, direita) em px que a interface do app cobre (ou o corte) — texto e logo ficam fora.
# excl = retângulos extras (x0, y0, x1, y1) onde texto/logo não entram (ex.: coluna de ícones do Reels).
# Fontes de cada número: references/qualidade.md (pesquisa de anúncios Meta e página de captura).
#   9:16 (Stories, Reels, Status, anúncio 9:16 no feed): Meta oficial 14% topo / 35% base / 6% laterais; em celular
#     mais alto que 9:16 a Meta pode dar ZOOM (corta ~10% de cada lado) → laterais robustas 108 px → texto em
#     x 108–972, y 269–1248; e a coluna de ícones do Reels (curtir/comentar/compartilhar) na metade de baixo à direita
#     → nada de texto em x > 950 quando y > 960 (o mesmo 9:16 roda em Stories E Reels no grupo de posicionamento).
#   Feed 4:5 (1080×1350): Meta pede base e laterais livres (sem %) → base 10% (135) + laterais 6% (65); também cobre o
#     corte 3:4 da grade do perfil (34). 1:1: base 10% (108) + laterais 65.
#   Live 1920×1080: área segura de TÍTULO (SMPTE/EBU) x 96–1824, y 54–1026.
#   WhatsApp: foto do grupo = círculo (essencial a ≤ 0,35 × lado do centro); Status = mesma zona do 9:16 (sem número
#     oficial; app põe nome/progresso no topo e resposta na base).
# Interface MEDIDA em pior caso + respiro de 36 px (pesquisa 9, tabela §11/§12):
#   9:16 (Stories + Reels, a mesma arte; padrão = anúncio): TEXTO/LOGO/núcleo do herói (olhos e boca) em
#     x 108–972, y 240–1248 (topo: a barra do Reels termina em y 210 medido + 30 de respiro = 10 módulos de 24;
#     a linha oficial de 269 tinha 59 px de folga, por isso o texto sobe até 240) e, para y ≥ 936, x ≤ 852 (coluna do Reels começa em x 889; −36 de respiro; dente oficial
#     853). CORPO do herói: x 72–1008, y 216–1440 e, para y ≥ 940, x ≤ 864. Fundo/decoração: sangram (pouco detalhe
#     e tom médio-escuro sob a interface — ela é branca).
#   4:5 feed: texto x 72–1008 (margem 80 cobre), y ≤ 1215; cantos de baixo livres (marcação/som: x < 200 ou > 880 com
#     y > 1140). Carrossel: nada em x > 888 com y < 156 (contador 1/N) → formato "feed-carrossel".
#   1:1: y ≤ 972; cantos x < 200 ou > 880 com y > 870. 1:1 que vai para a grade do perfil: x 171–909 ("post-perfil").
#   DECISÃO DO ESTÚDIO: como as nossas peças alinham à ESQUERDA, o canto de baixo (marcação/repost em x 49–164) cai
#   exatamente no rodapé → a área de texto termina em y 1140 (4:5) e 870 (1:1); os cantos continuam em `excl`.
_COLUNA = [(852, 936, 1080, 1920)]
_CANTOS_45 = [(0, 1140, 200, 1350), (880, 1140, 1080, 1350)]
_CANTOS_11 = [(0, 870, 200, 1080), (880, 870, 1080, 1080)]
_HEROI_916 = dict(heroi=(72, 216, 1008, 1440), heroi_excl=[(864, 940, 1080, 1920)])
FORMATOS = {
    "feed": dict(W=1080, H=1350, zona=(72, 210, 72, 72), excl=_CANTOS_45, heroi=(34, 0, 1046, 1290)),
    "feed-carrossel": dict(W=1080, H=1350, zona=(72, 210, 72, 72), excl=_CANTOS_45 + [(888, 0, 1080, 156)],
                           heroi=(34, 0, 1046, 1290)),
    "post": dict(W=1080, H=1080, zona=(72, 210, 72, 72), excl=_CANTOS_11, heroi=(0, 0, 1080, 1020)),
    "post-perfil": dict(W=1080, H=1080, zona=(72, 210, 171, 171), excl=_CANTOS_11, heroi=(135, 0, 945, 1020)),
    "story": dict(W=1080, H=1920, zona=(240, 672, 108, 108), excl=_COLUNA, **_HEROI_916),
    "reels": dict(W=1080, H=1920, zona=(240, 672, 108, 108), excl=_COLUNA, **_HEROI_916),
    "reels-aviso": dict(W=1080, H=1920, zona=(240, 768, 108, 108), excl=_COLUNA, **_HEROI_916),
    "capa-reels": dict(W=1080, H=1920, zona=(420, 420, 108, 108), excl=_COLUNA, heroi=(72, 270, 1008, 1500)),
    "status": dict(W=1080, H=1920, zona=(240, 672, 108, 108)),
    "whatsapp": dict(W=1080, H=1080, zona=(0, 0, 0, 0)),
    "live": dict(W=1920, H=1080, zona=(54, 54, 96, 96)),
    "pagina": dict(W=1920, H=1080, zona=(0, 0, 0, 0)),
    "pagina-celular": dict(W=1080, H=1920, zona=(0, 0, 0, 0)),
    "checkout-desktop": dict(W=2000, H=590, zona=(59, 59, 200, 200)),    # essencial nos 80% centrais
    "checkout-celular": dict(W=800, H=800, zona=(80, 80, 80, 80)),
    "banner": dict(W=1920, H=1080, zona=(0, 0, 0, 0)),
    "meta-191": dict(W=1080, H=566, zona=(34, 34, 65, 65)),              # coluna da direita/pesquisa: quase sem texto
}
# Tamanho mínimo de texto (altura da MAIÚSCULA) num lado menor de 1080 px — escala com o lado menor.
#   Conta: o menor celular comum no Brasil tem 360 px CSS (StatCounter set/2026) → 1080/360 = 3,0 px de arte por px de
#   tela. Corpo 16 px CSS (texto que PRECISA ser lido: data, hora, oferta, valor, frase de ação, nome do produto)
#   = 48 px → maiúscula ≈ 34 px. Letra miúda (rótulos) 12 px CSS = 36 px → maiúscula ≈ 25 px.
#   Live vista no celular (overlay 1920) ≥ 43 px de maiúscula para preço/CTA/link.
CAP_MIN = 25 / 1080
CAP_LER = 34 / 1080


# ------------------------------------------------------------------ medida pela tinta
_M = {}


def ink(spec, text, tracking=0.0):
    """Caixa de TINTA do texto por unidade de corpo: (esq, topo, dir, base) relativos à origem (x=0, linha de base
    y=0; topo negativo). Renderiza em alta resolução (escala adaptada a textos longos)."""
    key = (spec, text, round(tracking, 5))
    if key in _M:
        return _M[key]
    from PIL import Image
    f = font(spec)
    s = 400.0
    W = f.width(text, s, tracking) + 2 * s
    H = 3 * s
    d = f.path(text, s, s, 2 * s, tracking)
    tmp = os.path.join(tempfile.gettempdir(), "_ink_compor.png")
    scale = min(3.0, 9000.0 / W)
    svg_to_png(wrap_svg(W, H, f'<path d="{d}" fill="#000"/>'), tmp, width=int(W * scale))
    a = Image.open(tmp).convert("RGBA").split()[-1]
    x0, y0, x1, y1 = a.getbbox()
    r = ((x0 / scale - s) / s, (y0 / scale - 2 * s) / s, (x1 / scale - s) / s, (y1 / scale - 2 * s) / s)
    _M[key] = r
    return r


def linha(spec, text, x, base, *, width=None, cap=None, tracking=0.0, fill="#111", justify=False):
    """Uma linha com a borda esquerda da TINTA em x. width → corpo que dá essa largura de tinta (ou, com justify e
    cap, o espaçamento que dá). Devolve (svg, caixa de tinta (x0, y0, x1, y1), corpo)."""
    f = font(spec)
    if justify and width and cap:
        size = cap / f.cap
        l0, t0, r0, b0 = ink(spec, text, tracking)
        l1, t1, r1, b1 = ink(spec, text, tracking + 0.05)
        w0, w1 = (r0 - l0) * size, (r1 - l1) * size
        tracking = tracking + 0.05 * (width - w0) / (w1 - w0) if w1 != w0 else tracking
    elif width:
        l, t, r, b = ink(spec, text, tracking)
        size = width / (r - l)
    else:
        size = cap / f.cap
    l, t, r, b = ink(spec, text, tracking)
    d = f.path(text, size, x - l * size, base, tracking)
    return f'<path d="{d}" fill="{fill}"/>', (x, base + t * size, x + (r - l) * size, base + b * size), size


def tx(spec, s, x, base, cap, fill, tr=0.0, anchor="start"):
    """Linha por altura de maiúscula, alinhada pela tinta. anchor start|middle|end. Devolve (svg, caixa)."""
    _, bb, _ = linha(spec, s, 0, base, cap=cap, tracking=tr, fill=fill)
    w = bb[2] - bb[0]
    x0 = x if anchor == "start" else x - w if anchor == "end" else x - w / 2
    svg, bb, _ = linha(spec, s, x0, base, cap=cap, tracking=tr, fill=fill)
    return svg, bb


def quebra_ruim(lines):
    """Regras de leitura: nenhuma linha (menos a última) termina em palavra de 1–2 letras; a última nunca é só uma
    palavra curta."""
    for ln in lines[:-1]:
        if len(ln.split(" ")[-1].strip(".,;:!?")) <= CURTA:
            return True
    last = lines[-1].split(" ")
    return len(lines) > 1 and len(last) == 1 and len(last[0].strip(".,;:!?")) <= CURTA


def quebra(spec, s, max_w, cap, tr=0.0, max_lines=6):
    """Menor número de linhas que cabem em max_w; entre elas, as mais iguais (sem violar quebra_ruim).
    Texto longo (> 14 palavras): guloso + correção de palavra curta no fim de linha."""
    f = font(spec)
    size = cap / f.cap
    words = s.split(" ")
    if len(words) > 14:
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if f.width(t, size, tr) <= max_w or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        for i in range(len(lines) - 1):
            last = lines[i].split(" ")
            if len(last) > 1 and len(last[-1].strip(".,;:")) <= CURTA:
                lines[i] = " ".join(last[:-1])
                lines[i + 1] = last[-1] + " " + lines[i + 1]
        return lines
    for n in range(1, min(max_lines, len(words)) + 1):
        best, score = None, 1e18
        for cuts in combinations(range(1, len(words)), n - 1):
            idx = (0,) + cuts + (len(words),)
            lines = [" ".join(words[idx[i]:idx[i + 1]]) for i in range(n)]
            if n > 1 and quebra_ruim(lines):
                continue
            ws = [f.width(ln, size, tr) for ln in lines]
            if max(ws) > max_w:
                continue
            sc = max(ws) - min(ws)
            if sc < score:
                best, score = lines, sc
        if best:
            return best
    return [s]


def quebra_sep(s, spec, max_w, cap, tr, sep=" · "):
    """Quebra uma lista 'A · B · C' só nos separadores (uma linha nunca começa com '·')."""
    f = font(spec)
    size = cap / f.cap
    lines, cur = [], ""
    for part in s.split(sep):
        t = (cur + sep + part) if cur else part
        if f.width(t, size, tr) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = part
    lines.append(cur)
    return lines


def entrelinha(spec, lines, cap, tr=0.0, lead_min=1.18, folga=0.16):
    """Entrelinha UNIFORME medida na tinta: o maior par (parte de baixo da linha de cima — Ç, vírgula, descendente —
    + parte de cima da de baixo — Á É Ê, ascendente — + folga × maiúscula), nunca menos que lead_min × maiúscula."""
    f = font(spec)
    size = cap / f.cap
    need = cap * lead_min
    for a, b in zip(lines, lines[1:]):
        need = max(need, ink(spec, a, tr)[3] * size - ink(spec, b, tr)[1] * size + folga * cap)
    return need


def bloco(spec, s, x, y_top, max_w, cap, fill, lead=1.18, tr=0.0, anchor="start", max_lines=6, folga=0.16):
    """Bloco: topo da 1ª maiúscula em y_top; quebra + entrelinha pela tinta. Devolve (svg, base da última linha)."""
    lines = quebra(spec, s, max_w, cap, tr, max_lines)
    step = entrelinha(spec, lines, cap, tr, lead, folga)
    out, y = "", y_top + cap
    for ln in lines:
        out += tx(spec, ln, x, y, cap, fill, tr, anchor)[0]
        y += step
    return out, y - step


def altura_bloco(spec, s, max_w, cap, tr=0.0, lead=1.18, max_lines=6, folga=0.16):
    lines = quebra(spec, s, max_w, cap, tr, max_lines)
    return cap + (len(lines) - 1) * entrelinha(spec, lines, cap, tr, lead, folga)


def iguala(spec, text, x, base, cap, fill, tr, alvo, limite=0.06):
    """Linha QUASE da largura `alvo` (diferença < 6%) é igualada a ela por micro-espaçamento. Borda quase alinhada é o
    erro que o olho pega: ou alinha de verdade, ou fica claramente diferente."""
    g, bb = tx(spec, text, x, base, cap, fill, tr)
    w = bb[2] - bb[0]
    if 0.5 < abs(alvo - w) < limite * alvo:
        g, bb, _ = linha(spec, text, x, base, width=alvo, cap=cap, tracking=tr, fill=fill, justify=True)
    return g, bb


# ------------------------------------------------------------------ espaçamento óptico (títulos, logos)
_G = {}
_REF, _SC = 400.0, 2


def _glyph(spec, ch):
    key = (spec, ch)
    if key in _G:
        return _G[key]
    import numpy as np
    from PIL import Image
    f = font(spec)
    pad = _REF
    W = f.width(ch, _REF, 0) + 2 * pad
    H = _REF * 2.2
    base = _REF * 1.5
    tmp = os.path.join(tempfile.gettempdir(), "_glyph_compor.png")
    svg_to_png(wrap_svg(W, H, f'<path d="{f.path(ch, _REF, pad, base, 0)}" fill="#000"/>'), tmp, width=int(W * _SC))
    a = np.array(Image.open(tmp).convert("RGBA"))[:, :, 3] > 110
    capH = f.cap * _REF
    rows = a[int((base - capH) * _SC):int(base * _SC)]
    left, right = np.full(len(rows), np.nan), np.full(len(rows), np.nan)
    for i, r in enumerate(rows):
        xs = np.nonzero(r)[0]
        if xs.size:
            left[i] = xs[0] / _SC - pad
            right[i] = (xs[-1] + 1) / _SC - pad
    allx = np.nonzero(a.any(axis=0))[0]
    ink_l = allx[0] / _SC - pad if allx.size else 0.0
    ink_r = (allx[-1] + 1) / _SC - pad if allx.size else 0.0
    _G[key] = (f.width(ch, _REF, 0), left, right, ink_l, ink_r)
    return _G[key]


def _gap(ra, lb, dx, depth):
    import numpy as np
    g = (lb + dx) - ra
    return float(np.where(np.isnan(g), depth, np.clip(g, 0, depth)).mean())


def _pair(a, b, target, depth, min_gap):
    import numpy as np
    ra, lb = a[2], b[1]
    lo, hi = -_REF * 2, _REF * 3
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _gap(ra, lb, mid, depth) < target else (lo, mid)
    dx = (lo + hi) / 2
    both = ~np.isnan(ra) & ~np.isnan(lb)
    if both.any():
        dx = max(dx, float(np.max(ra[both] - lb[both])) + min_gap)
    return dx


def palavra(spec, text, x=0.0, base=0.0, cap=None, aperto=1.0, fill="#111", largura=None, profundidade=0.22,
            espaco=0.3):
    """Palavra com espaçamento ÓPTICO por par (método de área: vazio médio igual entre letras, limitado a
    `profundidade` × maiúscula; distância mínima 0,055 × maiúscula). largura=W justifica somando o MESMO espaço em
    todos os pares. Devolve (svg, caixa de tinta, extra)."""
    f = font(spec)
    capH = f.cap * _REF
    depth = profundidade * capH
    ref = _glyph(spec, "H")
    target = _gap(ref[2], ref[1], ref[0], depth) * aperto
    min_gap = 0.055 * capH * min(1.0, aperto)
    k = cap / capH

    def lay(extra):
        out, last, sp = [], None, False
        for ch in text:
            if ch == " ":
                sp = True
                continue
            g = _glyph(spec, ch)
            if last is None:
                px = -g[3]
            elif sp:
                px = last[0] + last[1][4] + espaco * capH - g[3]
            else:
                px = last[0] + _pair(last[1], g, target, depth, min_gap) + extra * capH
            out.append((ch, px, g))
            last, sp = (px, g), False
        return (out[-1][1] + out[-1][2][4]) * k, out

    extra = 0.0
    if largura:
        lo, hi = -0.15, 1.5
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if lay(mid)[0] < largura else (lo, mid)
        extra = (lo + hi) / 2
    w, out = lay(extra)
    size = _REF * k
    paths = "".join(f'<path d="{f.path(ch, size, x + px * k, base, 0)}"/>' for ch, px, g in out)
    return f'<g fill="{fill}">{paths}</g>', (x, base - cap, x + w, base), extra


# ------------------------------------------------------------------ colocar artes
def poe(master, x, y, w=None, h=None, anchor="start", margem=0.02):
    """Coloca um MASTER cuja moldura = tinta + `margem` × altura de tinta nos 4 lados, com a TINTA em x (start|middle|
    end) e o topo da tinta em y, pela largura OU altura de tinta. Devolve (svg, caixa de tinta)."""
    vx, vy, vw, vh = viewbox(master)
    ih = vh / (1 + 2 * margem)
    pad = margem * ih
    iw = vw - 2 * pad
    k = (w / iw) if w else (h / ih)
    W_, H_ = iw * k, ih * k
    x0 = x if anchor == "start" else x - W_ if anchor == "end" else x - W_ / 2
    g = (f'<g transform="translate({x0 - pad * k:.2f} {y - pad * k:.2f}) scale({k:.5f}) translate({-vx} {-vy})">'
         f'{svg_inner(master)}</g>')
    return g, (x0, y, x0 + W_, y + H_)


def altura_poe(master, w, margem=0.02):
    vx, vy, vw, vh = viewbox(master)
    ih = vh / (1 + 2 * margem)
    return w * ih / (vw - 2 * margem * ih)


def poe_livre(svg, x, y, w=None, h=None, anchor="start"):
    """Coloca SVG de terceiros pela caixa (viewBox)."""
    vx, vy, vw, vh = viewbox(svg)
    k = (w / vw) if w else (h / vh)
    x0 = x if anchor == "start" else x - vw * k if anchor == "end" else x - vw * k / 2
    return (f'<g transform="translate({x0:.2f} {y:.2f}) scale({k:.5f}) translate({-vx} {-vy})">{svg_inner(svg)}</g>',
            (x0, y, x0 + vw * k, y + vh * k))


def mono(svg_path_or_text, fill):
    """SVG de terceiros (ex.: logo de produto) em UMA cor: tira <style>/classes e pinta tudo. Evita o vazamento de
    CSS entre cópias embutidas na mesma página."""
    svg = open(svg_path_or_text, encoding="utf-8").read() if os.path.exists(svg_path_or_text) else svg_path_or_text
    inner = re.sub(r"<style[^>]*>.*?</style>", "", svg_inner(svg), flags=re.S)
    inner = re.sub(r'class="[^"]*"', "", inner)
    inner = re.sub(r'(fill|stroke)="#[0-9A-Fa-f]{3,8}"', lambda m_: f'{m_.group(1)}="{fill}"', inner)
    vx, vy, vw, vh = viewbox(svg)
    return wrap_svg(vw, vh, f'<g transform="translate({-vx} {-vy})" fill="{fill}">{inner}</g>')


_IMG = {}


def recorte(png, cx, base, h, ancora="centro"):
    """Foto recortada (RGBA) cortada na tinta, altura h, centro em cx (ou borda esq./dir.), base em `base` (sangra).
    Devolve (svg <image>, caixa, alfa numpy) — o alfa deixa o verificador ver a PESSOA, não a caixa."""
    import numpy as np
    from PIL import Image
    key = (png, int(h))
    if key not in _IMG:
        im = Image.open(png).convert("RGBA")
        bb = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        im = im.crop(bb)
        k = h / im.height
        im = im.resize((max(1, int(im.width * k)), int(h)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "PNG", optimize=True)
        _IMG[key] = (base64.b64encode(buf.getvalue()).decode(), im.width, im.height, np.asarray(im.getchannel("A")))
    b64, w, hh, al = _IMG[key]
    x0 = cx - w / 2 if ancora == "centro" else cx if ancora == "esq" else cx - w
    y0 = base - hh
    return (f'<image href="data:image/png;base64,{b64}" x="{x0:.1f}" y="{y0:.1f}" width="{w}" height="{hh}"/>',
            (x0, y0, x0 + w, base), al)


def largura_recorte(png, h):
    from PIL import Image
    im = Image.open(png)
    bb = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox() if im.mode == "RGBA" else None
    w, hh = (bb[2] - bb[0], bb[3] - bb[1]) if bb else im.size
    return h * w / hh


# ------------------------------------------------------------------ peça + verificador
def _inter(a, b, tol):
    x0, y0 = max(a[0], b[0]) + tol, max(a[1], b[1]) + tol
    x1, y1 = min(a[2], b[2]) - tol, min(a[3], b[3]) - tol
    return (x0, y0, x1, y1) if x1 > x0 and y1 > y0 else None


class Peca:
    """Uma peça. add(svg, caixa, rótulo, tipo) registra a caixa de TINTA de cada elemento.
    Tipos: txt · logo · barra (tarjas, botões) · foto (com alfa) · visor (cantos de moldura) · rotulo (dentro de
    barra/visor; fora das checagens de colisão) · fundo (nada).
    qa() aponta: fora da margem/zona segura (tolerância tipográfica), colisão, texto sobre a PESSOA (alfa), elementos
    encostando em cantos de moldura e bordas QUASE alinhadas (0,5 px < Δ < 1,5% do lado menor)."""

    def __init__(self, W, H, fundo="#111", formato=None, margem=None):
        self.W, self.H, self.fundo = W, H, fundo
        self.s = min(W, H)
        self.m = round(0.074 * self.s) if margem is None else margem
        self.my = None
        self.zona = FORMATOS.get(formato, {}).get("zona", (0, 0, 0, 0)) if formato else (0, 0, 0, 0)
        self.excl = FORMATOS.get(formato, {}).get("excl", []) if formato else []
        self.body, self.regs, self.defs = [], [], ""

    def add(self, g, caixa=None, rotulo="", tipo="txt", sangra=False, alfa=None, alinha=True, cap=None):
        self.body.append(g)
        if caixa is not None:
            self.regs.append(dict(r=rotulo, c=caixa, t=tipo, sangra=sangra, alfa=alfa, alinha=alinha, cap=cap))

    def texto(self, spec, s, x, base, cap, fill, tr=0.0, anchor="start", rotulo=None, **kw):
        """Linha de texto já registrada (com a maiúscula, para o verificador de tamanho mínimo)."""
        g, bb = tx(spec, s, x, base, cap, fill, tr, anchor)
        self.add(g, bb, rotulo or s[:24], "txt", cap=cap, **kw)
        return bb

    def qa(self):
        m = self.m
        my = self.my if self.my is not None else m
        zt, zb, zl, zr = self.zona
        W, H = self.W, self.H
        out = []
        for e in self.regs:
            if e["t"] in ("rotulo", "fundo"):
                continue
            x0, y0, x1, y1 = e["c"]
            h = y1 - y0
            tv, th = (0.32 * h, 0.03 * h) if e["t"] == "txt" else (0.6, 0.6)
            if not e["sangra"]:
                if x0 < m - th or y0 < my - tv or x1 > W - m + th or y1 > H - my + tv:
                    out.append(f"fora da margem: {e['r']} ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
                elif e["t"] in ("txt", "logo", "barra") and (y0 < zt - tv or y1 > H - zb + tv or x0 < zl or
                                                              x1 > W - zr):
                    out.append(f"na zona da interface do app: {e['r']}")
                elif e["t"] in ("txt", "logo", "barra") and any(_inter(e["c"], z, 1.0) for z in self.excl):
                    out.append(f"sob os ícones do app (coluna do Reels): {e['r']}")
        cont = [e for e in self.regs if e["t"] in ("txt", "logo", "barra")]
        for i, a in enumerate(cont):
            for b in cont[i + 1:]:
                if _inter(a["c"], b["c"], 1.0):
                    out.append(f"colisão: {a['r']} × {b['r']}")
            for v in [e for e in self.regs if e["t"] == "visor"]:
                if _inter(a["c"], v["c"], 0.0):
                    out.append(f"encosta na moldura: {a['r']}")
            for fo in [e for e in self.regs if e["t"] == "foto"]:
                ic = _inter(a["c"], fo["c"], 0.0)
                if ic and fo["alfa"] is not None and not a["r"].startswith("sobre-foto"):
                    fx0, fy0 = fo["c"][0], fo["c"][1]
                    ix0, iy0, ix1, iy1 = [int(round(v)) for v in (ic[0] - fx0, ic[1] - fy0, ic[2] - fx0, ic[3] - fy0)]
                    sub = fo["alfa"][max(0, iy0):max(0, iy1), max(0, ix0):max(0, ix1)]
                    if sub.size and (sub > 40).mean() > 0.003:
                        out.append(f"texto sobre a pessoa: {a['r']}")
        for e in self.regs:
            if e.get("cap") and e["t"] == "txt" and e["cap"] < CAP_MIN * self.s - 0.5:
                out.append(f"texto pequeno demais ({e['cap']:.0f}px < {CAP_MIN * self.s:.0f}px): {e['r']}")
        lim = 0.015 * self.s
        for nome, idx in (("esquerda", 0), ("direita", 2)):
            xs = [(e["c"][idx], e["r"]) for e in cont if e["alinha"] and not e["sangra"]]
            for i, (xa, ra) in enumerate(xs):
                for xb, rb in xs[i + 1:]:
                    if 0.5 < abs(xa - xb) < lim:
                        out.append(f"quase alinhado ({nome}, {abs(xa - xb):.1f}px): {ra} × {rb}")
        return out

    def svg(self, transparente=False):
        bg = "" if transparente else f'<rect width="{self.W}" height="{self.H}" fill="{self.fundo}"/>'
        return wrap_svg(self.W, self.H, self.defs + bg + "".join(self.body))

    def png(self, out, transparente=False, escala=1):
        svg_to_png(self.svg(transparente), out, width=int(self.W * escala))
        return out


if __name__ == "__main__":
    print(__doc__)


# ------------------------------------------------------------------ glifo assinatura: til que vira tarja
_TIL = {}


def _til_caixa(spec, ch="Ã"):
    """Caixa de tinta do TIL (por unidade de corpo, relativa à origem do glifo): renderiza 'Ã' e 'A' e pega só o que
    fica acima da tinta do 'A'."""
    key = (spec, ch)
    if key in _TIL:
        return _TIL[key]
    import numpy as np
    from PIL import Image
    f = font(spec)
    s, pad = 400.0, 400.0
    base_ch = {"Ã": "A", "Õ": "O", "ã": "a", "õ": "o"}[ch]
    W = f.width(ch, s, 0) + 2 * pad
    H = 3 * s
    tmp = os.path.join(tempfile.gettempdir(), "_til.png")
    svg_to_png(wrap_svg(W, H, f'<path d="{f.path(ch, s, pad, 2 * s, 0)}" fill="#000"/>'), tmp, width=int(W * 2))
    a = np.array(Image.open(tmp).convert("RGBA"))[:, :, 3] > 100
    top_base = ink(spec, base_ch)[1] * s + 2 * s            # topo da letra-base (px no canvas 1×)
    rows = a[: int((top_base - 0.03 * s) * 2)]
    ys, xs = np.nonzero(rows)
    r = ((xs.min() / 2 - pad) / s, (ys.min() / 2 - 2 * s) / s, ((xs.max() + 1) / 2 - pad) / s, ((ys.max() + 1) / 2 - 2 * s) / s)
    _TIL[key] = r
    return r


def til_tarja(spec, text, x, base, cap, fill, tarja, tr=0.0, anchor="start", altura=0.62):
    """Linha em que o TIL de Ã/Õ vira uma TARJA (retângulo na caixa do til, altura = `altura` × altura do til,
    centrado nela). Assinatura tipográfica em português: a marca que esconde está dentro da própria língua.
    Devolve (svg, caixa de tinta da linha)."""
    f = font(spec)
    size = cap / f.cap
    plain = text.translate(str.maketrans("ÃÕãõ", "AOao"))
    g, bb = tx(spec, plain, x, base, cap, fill, tr, anchor)
    l0 = ink(spec, plain, tr)[0] * size
    ox = bb[0] - l0                                          # origem da linha (antes do recuo da tinta)
    out = ""
    for i, ch in enumerate(text):
        if ch in "ÃÕãõ":
            gx = ox + f.width(plain[:i], size, tr) + (tr * size * 0 if i == 0 else 0)
            tl, tt, trr, tb = _til_caixa(spec, ch)
            h = (tb - tt) * size
            hh = h * altura
            out += (f'<rect x="{gx + tl * size:.2f}" y="{base + tt * size + (h - hh) / 2:.2f}" '
                    f'width="{(trr - tl) * size:.2f}" height="{hh:.2f}" fill="{tarja}"/>')
    return g + out, (bb[0], min(bb[1], base + _til_caixa(spec)[1] * size), bb[2], bb[3])
