"""ornamentos.texturas — família "TEXTURAS": grão (claro/escuro, fino/médio/grosso), papel, papel amassado/dobrado,
xerox, borda rasgada, tinta de carimbo, risografia, scanlines, poeira/arranhões, degradê com grão.

Valores (references/elementos.md "Acabamento premium"; pesquisa 4 §3.7 e §5.1; pesquisa 13 §1.1–1.6):
  - grão CLARO (fundo claro) = grão escuro em multiply 14–18% (fractalNoise 0,8, 2 oitavas, ladrilho 180 px, 16%);
  - grão ESCURO = grão claro esparso em screen 15–18% + feComponentTransfer gamma 3 ("poeira de luz");
  - UM grão só por peça, por último, nunca sobre o texto; baseFrequency nunca inteiro; stitchTiles="stitch".
Como as camadas saem em ALFA (preto ou branco com opacidade = ruído), "multiply" e "screen" ficam EXATOS em mistura
normal: preto·α(1−n) = multiply de n a α; branco·α·n = screen de n a α. Funcionam em <img>, no palco e no site.
Filtros: color-interpolation-filters="sRGB"; região = o próprio ladrilho (userSpaceOnUse) para emendar sem costura.
Raster (xerox) só onde o vetor não dá: PNG de paleta de 2 cores (leve).

  grao · papel · amassado · xerox · borda_rasgada · filtro_carimbo / carimbo · riso · scanlines · poeira ·
  gradiente_grao     (+ oklch_mix para degradês entre cores vizinhas em OKLCH)
"""
import base64
import io
import math

import numpy as np

from .nucleo import amostra, elemento
from .linhas import semente, rng, nprng, caminho, curva, claro, campo_ruido, _cheio

FAM = "texturas"
NOTA_GRAO = "UM grão por peça, por último, sobre fundo+foto+elementos e NUNCA sobre o texto"


# ================================================================ cor (OKLab) — degradê só entre vizinhas
def _hex(c):
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def _lin(v):
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def _gam(v):
    v = np.clip(v, 0, 1)
    return np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1 / 2.4) - 0.055)


def _oklab(c):
    r, g, b = _lin(_hex(c))
    l_ = np.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m_ = np.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s_ = np.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return np.array([0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
                     1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
                     0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_])


def _de_oklab(L):
    l_ = L[0] + 0.3963377774 * L[1] + 0.2158037573 * L[2]
    m_ = L[0] - 0.1055613458 * L[1] - 0.0638541728 * L[2]
    s_ = L[0] - 0.0894841775 * L[1] - 1.2914855480 * L[2]
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    rgb = _gam(np.array([4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
                         -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
                         -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s]))
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in rgb)


def oklch_mix(c0, c1, t):
    """Mistura perceptual (OKLab) de duas cores HEX."""
    return _de_oklab(_oklab(c0) * (1 - t) + _oklab(c1) * t)


def clarear(c, dL):
    L = _oklab(c)
    L[0] = min(1.0, max(0.0, L[0] + dL))
    return _de_oklab(L)


def _paradas(c0, c1, n=9, curva_=lambda t: t):
    return "".join(f'<stop offset="{t:.3f}" stop-color="{oklch_mix(c0, c1, curva_(t))}"/>' for t in np.linspace(0, 1, n))


# ================================================================ 1. grão
def filtro_grao(id_, w, h, fundo="claro", freq=0.8, oit=2, forca=0.16, gama=3.0, contraste=1.6, seed=7):
    """<filter> de grão em ALFA. fundo claro → preto α = forca·(1−n) (= multiply); escuro → branco α = forca·n^gama
    (= screen + gamma: só os picos acendem). Aplicar num <rect> do tamanho do ladrilho."""
    fq = f"{freq:.4g}" if not float(freq).is_integer() else f"{freq + 0.013:.4g}"
    st = (f'<feComponentTransfer in="n" result="c"><feFuncR type="linear" slope="{contraste}" '
          f'intercept="{0.5 - contraste / 2:.3f}"/></feComponentTransfer>')
    if fundo == "claro":
        mat = f"0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  {-forca:.4f} 0 0 0 {forca:.4f}"
        corpo = st + f'<feColorMatrix in="c" type="matrix" values="{mat}"/>'
    else:
        corpo = (st + f'<feComponentTransfer in="c" result="g"><feFuncR type="gamma" amplitude="1" exponent="{gama}" '
                 f'offset="0"/></feComponentTransfer>'
                 f'<feColorMatrix in="g" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  {forca:.4f} 0 0 0 0"/>')
    return (f'<filter id="{id_}" filterUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}" '
            f'color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency="{fq}" '
            f'numOctaves="{oit}" seed="{seed}" stitchTiles="stitch" result="n"/>{corpo}</filter>')


TAMANHOS = {"fino": (0.9, 2), "medio": (0.62, 3), "grosso": (0.38, 3)}


def grao(f, fundo="escuro", tamanho="fino", forca=None, lado=360, seed=0, gama=3.0, nome=None):
    """Ladrilho de grão (sem costura). fundo: claro (multiply 16%) · escuro (screen 17% + gamma 3)."""
    fq, oit = TAMANHOS[tamanho]
    forca = forca if forca is not None else (0.16 if fundo == "claro" else 0.17)
    s = semente(f, "grao", fundo, tamanho, seed) % 1000
    flt = filtro_grao("g", lado, lado, fundo, fq, oit, forca, gama, seed=s)
    el = elemento(lado, lado, f'<rect width="{lado}" height="{lado}" filter="url(#g)"/>',
                  nome or f"grão {tamanho} · fundo {fundo}", FAM, defs=flt,
                  css=(f".grao{{position:absolute;inset:0;pointer-events:none;background:url(grao-{fundo}-{tamanho}.svg) "
                       f"repeat;background-size:{lado}px}}"),
                  nota=f"{'multiply' if fundo == 'claro' else 'screen + gamma ' + format(gama, 'g')} {forca * 100:.0f}% · "
                       f"freq {fq} · ladrilho {lado}px; " + NOTA_GRAO)
    return claro(el) if fundo == "claro" else el


# ================================================================ 2. papel
def papel(f, tipo="liso", w=900, h=900, cor=None, seed=0):
    """Papel (fundo opaco). tipo: liso (fibra + manchas) · aspero (relevo por luz difusa) · kraft · jornal · vinco ·
    cartao (papel escuro, para o tema escuro) · reciclado (pintinhas) · telado (fibra cruzada)."""
    s = semente(f, "papel", tipo, seed) % 1000
    base = cor or {"kraft": oklch_mix(f.papel, f.acento, 0.42), "jornal": oklch_mix(f.papel, f.apoio, 0.22),
                   "cartao": clarear(f.fundo, 0.035)}.get(tipo, f.papel)
    escuro = tipo == "cartao"
    tom = "#000000" if not escuro else "#FFFFFF"
    defs = (f'<filter id="mancha" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves="3" seed="{s}"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.09 0 0 0 -0.03"/></filter>'
            f'<filter id="fibra" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{"0.7 0.09" if tipo != "telado" else "0.3 0.3"}" '
            f'numOctaves="2" seed="{s + 1}"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.22 0 0 0 -0.09"/></filter>')
    corpo = f'<rect width="{w}" height="{h}" fill="{base}"/>'
    corpo += f'<rect width="{w}" height="{h}" filter="url(#mancha)" fill="{tom}"/>'
    if tipo in ("liso", "kraft", "jornal", "vinco", "reciclado", "telado"):
        corpo += f'<g opacity="{0.4 if tipo != "telado" else 0.7}"><rect width="{w}" height="{h}" filter="url(#fibra)"/></g>'
        if tipo == "telado":
            corpo += (f'<g opacity="0.7" transform="rotate(90 {w / 2} {h / 2})"><rect width="{w}" height="{h}" '
                      f'filter="url(#fibra)"/></g>')
    if tipo in ("aspero", "cartao", "kraft"):
        luz = "#FFFFFF"
        defs += (f'<filter id="relevo" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
                 f'<feTurbulence type="fractalNoise" baseFrequency="{0.045 if tipo == "aspero" else 0.08}" '
                 f'numOctaves="5" seed="{s + 2}" result="n"/>'
                 f'<feDiffuseLighting in="n" surfaceScale="{2.2 if tipo == "aspero" else 1.4}" lighting-color="{luz}" '
                 f'result="l"><feDistantLight azimuth="225" elevation="{52 if tipo == "aspero" else 60}"/></feDiffuseLighting>'
                 f'<feColorMatrix in="l" type="matrix" values="0 0 0 0 {0 if not escuro else 1}  0 0 0 0 {0 if not escuro else 1}  '
                 f'0 0 0 0 {0 if not escuro else 1}  {-0.5 if not escuro else 0.35} 0 0 0 {0.42 if not escuro else -0.22}"/>'
                 f'</filter>')
        corpo += f'<rect width="{w}" height="{h}" filter="url(#relevo)"/>'
    if tipo == "reciclado":
        r = rng(f, "recicl", seed)
        pts = []
        for _ in range(240):
            x, y, rr = r.uniform(0, w), r.uniform(0, h), r.uniform(0.5, 1.8)
            n = 6
            pts.append([(x + rr * r.uniform(0.6, 1.2) * math.cos(2 * math.pi * k / n),
                         y + rr * r.uniform(0.6, 1.2) * math.sin(2 * math.pi * k / n)) for k in range(n)])
        corpo += _cheio(pts, oklch_mix(base, f.fundo, 0.55), 0.55)
    if tipo == "vinco":
        x = w * 0.5
        defs += ('<linearGradient id="vc" x1="0" x2="1" y1="0" y2="0">'
                 '<stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="0.47" stop-color="#000" stop-opacity="0.07"/>'
                 '<stop offset="0.5" stop-color="#000" stop-opacity="0.13"/><stop offset="0.52" stop-color="#fff" stop-opacity="0.35"/>'
                 '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
        corpo += f'<rect x="{x - 14}" y="0" width="28" height="{h}" fill="url(#vc)"/>'
    nomes = {"liso": "papel · liso (fibra + manchas)", "aspero": "papel · áspero (algodão)", "kraft": "papel · kraft",
             "jornal": "papel · jornal", "vinco": "papel · com vinco", "cartao": "papel · cartão escuro",
             "reciclado": "papel · reciclado", "telado": "papel · telado"}
    el = elemento(w, h, corpo, nomes[tipo], FAM, defs=defs,
                  nota="off-white quente, nunca #FFF; texto e tarjas em vetor POR CIMA; grão do papel 2–4%")
    return el if escuro else claro(el)


# ================================================================ 3. papel amassado / dobrado (facetas vetoriais)
def amassado(f, modo="leve", w=900, h=900, sobre_papel=False, seed=0):
    """Dobras e amassado: cada VINCO é uma faixa com sombra de um lado e luz do outro (luz de cima-esquerda), que
    some nas pontas; o amassado é a soma de muitos vincos curtos em direções ao acaso. Vetor + gradientes (leve).
    modo: em4 (dobrado em 4) · em8 · vinco (1 diagonal) · leve/forte (EXPERIMENTAL: muitos vincos ainda leem como
    riscos de luz, não como amassado — fora do catálogo). Sai em alfa (preto/branco) — põe sobre
    qualquer fundo; sobre_papel=True inclui a folha."""
    r = rng(f, "amass", modo, seed)
    diag = math.hypot(w, h)
    vincos = []                     # (cx, cy, ângulo°, comprimento, meia-largura λ, força)
    if modo == "em4":
        vincos = [(w / 2 + r.gauss(0, 3), h / 2, 90 + r.gauss(0, 0.6), h * 1.1, 70, 0.16),
                  (w / 2, h / 2 + r.gauss(0, 3), r.gauss(0, 0.6), w * 1.1, 60, 0.12)]
    elif modo == "em8":
        vincos = [(w / 2, h / 2, 90.3, h * 1.1, 60, 0.14), (w / 2, h / 2, 0.4, w * 1.1, 55, 0.11),
                  (w / 4, h / 2, 89.6, h * 1.1, 45, 0.09), (3 * w / 4, h / 2, 90.5, h * 1.1, 45, 0.09)]
    elif modo == "vinco":
        vincos = [(w / 2, h / 2, -32, diag * 1.1, 90, 0.16)]
    else:
        n = 18 if modo == "leve" else 38
        for _ in range(n):
            vincos.append((r.uniform(0, w), r.uniform(0, h), r.uniform(0, 180), r.uniform(0.25, 0.75) * diag,
                           r.uniform(18, 70) if modo == "forte" else r.uniform(30, 90),
                           r.uniform(0.05, 0.11) if modo == "leve" else r.uniform(0.07, 0.15)))
    luz = np.array([-0.6, -0.8])
    defs = ('<linearGradient id="ao" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset="0.25" stop-color="#fff"/><stop offset="0.75" stop-color="#fff"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            '<mask id="pontas" maskContentUnits="objectBoundingBox"><rect width="1" height="1" fill="url(#ao)"/></mask>')
    grads, corpo_v = {}, ""
    for cx, cy, a, L, lam, k in vincos:
        nrm = np.array([-math.sin(math.radians(a)), math.cos(math.radians(a))])
        lado = 1 if float(np.dot(nrm, luz)) < 0 else -1        # o lado virado para a luz recebe o brilho
        kq = round(k, 2)
        gid = f"v{int(kq * 100)}{'a' if lado > 0 else 'b'}"
        if gid not in grads:
            c0, c1 = ("#000", "#fff") if lado > 0 else ("#fff", "#000")
            o0, o1 = (kq, kq * 0.9) if lado > 0 else (kq * 0.9, kq)
            grads[gid] = (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                          f'<stop offset="0" stop-color="{c0}" stop-opacity="0"/>'
                          f'<stop offset="0.5" stop-color="{c0}" stop-opacity="{o0:.3f}"/>'
                          f'<stop offset="0.5" stop-color="{c1}" stop-opacity="{o1:.3f}"/>'
                          f'<stop offset="1" stop-color="{c1}" stop-opacity="0"/></linearGradient>')
        mk = ' mask="url(#pontas)"' if modo in ("leve", "forte") else ""
        corpo_v += (f'<rect x="{-L / 2:.1f}" y="{-lam:.1f}" width="{L:.1f}" height="{2 * lam:.1f}" fill="url(#{gid})"{mk} '
                    f'transform="translate({cx:.1f} {cy:.1f}) rotate({a:.2f})"/>')
    defs += "".join(grads.values())
    corpo = f'<rect width="{w}" height="{h}" fill="{f.papel}"/>' if sobre_papel else ""
    corpo += corpo_v
    nomes = {"leve": "papel amassado · leve", "forte": "papel amassado · forte", "em4": "papel dobrado em 4",
             "em8": "papel dobrado em 8", "vinco": "vinco diagonal"}
    el = elemento(w, h, f'<g clip-path="url(#ca)">{corpo}</g>', nomes[modo] + (" · sobre papel" if sobre_papel else ""),
                  FAM, defs=defs + f'<clipPath id="ca"><rect width="{w}" height="{h}"/></clipPath>',
                  nota="1–4 vincos fortes > amassado em tudo; sob a arte; luz de cima-esquerda (sombra 5–15%)")
    return claro(el) if sobre_papel else el


# ================================================================ 4. xerox / fotocópia (raster leve, 2 cores)
def _png_2cores(mask, cor):
    from PIL import Image
    im = Image.fromarray(mask.astype(np.uint8), "P")
    rgb = _hex(cor)
    im.putpalette([0, 0, 0] + [int(v * 255) for v in rgb] + [0, 0, 0] * 254)
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True, transparency=0)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def xerox(f, modo="toner", w=1080, h=1080, cor=None, seed=0, fundo_claro=False):
    """Fotocópia: limiar → desfoque → limiar (gerações), manchas de toner, riscas do scanner, borda da cópia.
    modo: toner · riscas · bloco (preto de xerox com falhas) · borda (margem escura da cópia) · geracao."""
    from scipy.ndimage import gaussian_filter
    g = nprng(f, "xerox", modo, seed)
    cor = cor or (f.fundo if fundo_claro else f.tinta)
    yy, xx = np.mgrid[0:h, 0:w]
    u, v = xx / w, yy / h
    poeira = g.random((h, w))
    toner = campo_ruido(w // 6 + 1, h // 6 + 1, 30, 4, semente(f, "ton", seed))
    from PIL import Image
    toner = np.asarray(Image.fromarray(((toner + 1) * 127.5).astype(np.uint8)).resize((w, h), Image.BICUBIC)) / 127.5 - 1
    if modo == "toner":
        nuvem = np.clip((toner + 0.15) * 1.6, 0, 1) ** 3          # o pó junta em nuvens (não é "neve" uniforme)
        flecos = gaussian_filter(poeira, 1.6) < 0.385
        M = (poeira < 0.0006 + 0.07 * nuvem) | (flecos & (nuvem > 0.25)) | (gaussian_filter(poeira, 0.8) < 0.24)
    elif modo == "riscas":
        col = g.random(w)
        riscas = (col < 0.025)[None, :] & (g.random((h, 1)) < 0.85)
        riscas = gaussian_filter(riscas.astype(float), (6, 0.4)) > 0.35
        M = riscas | (poeira < 0.008)
    elif modo == "bloco":
        dentro = (u > 0.08) & (u < 0.92) & (v > 0.3) & (v < 0.62)
        falha = (gaussian_filter(poeira, 1.0) > 0.62 + 0.06 * toner) | (poeira > 0.985)
        borda = gaussian_filter(dentro.astype(float), 2.2) + (poeira - 0.5) * 0.35 > 0.5
        M = borda & ~falha
    elif modo == "borda":
        d = np.minimum.reduce([u, 1 - u, v, 1 - v])
        lim = 0.05 + 0.025 * toner + 0.01 * (poeira - 0.5)
        M = (d < lim) | ((d < lim + 0.05) & (poeira < 0.05 * (1 - (d - lim) / 0.05)))
    else:
        a = gaussian_filter(poeira, 2.0) + 0.06 * toner
        for _ in range(3):
            a = gaussian_filter((a > np.median(a) + 0.012).astype(float), 1.2) + (g.random((h, w)) - 0.5) * 0.12
        M = a > 0.55
    url = _png_2cores(M.astype(np.uint8), cor)
    corpo = f'<image href="{url}" width="{w}" height="{h}" style="image-rendering:pixelated"/>'
    nomes = {"toner": "xerox · toner e pó", "riscas": "xerox · riscas do scanner", "bloco": "xerox · preto de cópia (tarja)",
             "borda": "xerox · borda da cópia", "geracao": "xerox · 3ª geração"}
    el = elemento(w, h, corpo, nomes[modo], FAM, nota="em 1 elemento (foto, fundo, papel vazado) — nunca no logo/CTA; "
                  "o melhor ainda é copiar e escanear de verdade")
    return claro(el) if fundo_claro else el


# ================================================================ 5. borda rasgada
def _rasgo(x0, x1, y, r, amp=7.0, passo=3.0, grande=True):
    """Borda rasgada: ruído 1-D em 2 escalas + rasgos maiores ocasionais."""
    xs = np.arange(x0, x1 + passo, passo)
    n = len(xs)
    from .nucleo import ruido1d
    rr = __import__("random").Random(r.randrange(1 << 30))
    a = np.array(ruido1d(rr, n, 3)) * amp
    b = np.array([rr.gauss(0, 1) for _ in range(n)]) * amp * 0.16
    y_ = y + a + b
    if grande:
        for _ in range(max(1, int((x1 - x0) / 400))):
            c = rr.uniform(x0, x1)
            y_ += amp * 1.6 * np.exp(-((xs - c) / rr.uniform(20, 50)) ** 2) * rr.choice([-1, 1])
    return list(zip(xs, y_))


def borda_rasgada(f, modo="tira", w=1080, h=300, cor=None, seed=0, fibra=True, sombra=True):
    """Papel rasgado com FIBRA branca na borda e sombra curta. modo: tira (2 bordas) · topo · janela (rasgo que
    revela) · canto · mascara (forma preta p/ recorte) · vertical · dupla (2 tiras sobrepostas)."""
    r = rng(f, "rasg", modo, seed)
    cor = cor or f.papel
    fib = "#FFFFFF"
    camadas = []          # (polígono(s), cor, regra)

    def tira(y0, y1, cor_, dx=0.0):
        top = _rasgo(-20, w + 20, y0, r)
        bot = _rasgo(-20, w + 20, y1, r)[::-1]
        topf = [(x, y - r.uniform(1.5, 4.5)) for x, y in _rasgo(-20, w + 20, y0, r, amp=7.5)]
        botf = [(x, y + r.uniform(1.5, 4.5)) for x, y in _rasgo(-20, w + 20, y1, r, amp=7.5)][::-1]
        return [(topf + botf, fib), (top + bot, cor_)]
    defs = ('<filter id="sb" x="-10%" y="-20%" width="120%" height="140%" color-interpolation-filters="sRGB">'
            '<feGaussianBlur stdDeviation="2.5"/></filter>')
    corpo = ""
    clip = None
    if modo in ("tira", "dupla"):
        if modo == "dupla":
            camadas += tira(h * 0.12, h * 0.58, f.acento)
            camadas += tira(h * 0.42, h * 0.88, cor)
        else:
            camadas += tira(h * 0.22, h * 0.78, cor)
    elif modo == "topo":
        top = _rasgo(-20, w + 20, h * 0.18, r, amp=9)
        topf = [(x, y - r.uniform(2, 6)) for x, y in _rasgo(-20, w + 20, h * 0.18, r, amp=9)]
        camadas += [(topf + [(w + 20, h + 20), (-20, h + 20)], fib), (top + [(w + 20, h + 20), (-20, h + 20)], cor)]
    elif modo == "vertical":
        ed = [(y, x) for x, y in _rasgo(-20, h + 20, w * 0.62, r, amp=9)]
        edf = [(y + r.uniform(2, 6), x) for x, y in _rasgo(-20, h + 20, w * 0.62, r, amp=9)]
        camadas += [([(-20, -20)] + edf + [(-20, h + 20)], fib), ([(-20, -20)] + ed + [(-20, h + 20)], cor)]
    elif modo == "canto":            # folha inteira com o canto de cima arrancado
        ed0 = _rasgo(0, math.hypot(w, h) * 0.52, 0, r, amp=8)
        a = math.radians(-45)
        ox, oy = 0, h * 0.5
        ed = [(ox + x * math.cos(a) - y * math.sin(a), oy + x * math.sin(a) + y * math.cos(a)) for x, y in ed0]
        edf = [(x + r.uniform(2, 6), y + r.uniform(2, 6)) for x, y in ed]
        resto = [(w + 20, -20), (w + 20, h + 20), (-20, h + 20)]
        camadas += [(edf + resto, fib), (ed + resto, cor)]
    elif modo == "janela":
        cx, cy, R = w / 2, h / 2, min(w, h) * 0.3
        from .nucleo import ruido1d
        rr = __import__("random").Random(r.randrange(1 << 30))
        th = np.linspace(0, 2 * math.pi, 260, endpoint=False)
        n1 = sum(rr.uniform(0.4, 1) / k_ ** 0.9 * np.sin(k_ * th + rr.uniform(0, 6.3)) for k_ in range(2, 22))
        n1 = n1 / np.abs(n1).max()
        rad = R * (1 + 0.16 * n1) + np.array([rr.gauss(0, 1.4) for _ in th])
        buraco = [(cx + q * 1.3 * math.cos(t), cy + q * 0.85 * math.sin(t)) for q, t in zip(rad, th)]
        fibra_l = np.clip(np.array([rr.gauss(5, 2.2) for _ in th]), 1.5, 10)
        buraco_f = [(cx + (q - fl) * 1.3 * math.cos(t), cy + (q - fl) * 0.85 * math.sin(t))
                    for q, fl, t in zip(rad, fibra_l, th)]
        folha = [(0, 0), (w, 0), (w, h), (0, h)]
        defs += f'<clipPath id="bj"><path d="{caminho(buraco_f, True)}"/></clipPath>'
        corpo += (f'<g clip-path="url(#bj)"><g filter="url(#sb)" opacity="0.5" transform="translate(3 5)">'
                  f'<path d="{caminho(folha, True)}{caminho(buraco_f[::-1], True)}" fill="#000" fill-rule="evenodd"/></g></g>'
                  f'<path d="{caminho(folha, True)}{caminho(buraco_f[::-1], True)}" fill="{fib}" fill-rule="evenodd"/>'
                  f'<path d="{caminho(folha, True)}{caminho(buraco[::-1], True)}" fill="{cor}" fill-rule="evenodd"/>')
    elif modo == "mascara":
        top = _rasgo(-20, w + 20, h * 0.2, r, amp=9)
        bot = _rasgo(-20, w + 20, h * 0.8, r, amp=9)[::-1]
        camadas += [(top + bot, "#000000")]
        fibra = sombra = False
    if camadas:
        if sombra:
            corpo += f'<g filter="url(#sb)" opacity="0.4" transform="translate(2 4)">' + \
                     "".join(_cheio([p], "#000000") for p, c in camadas if c != fib) + "</g>"
        for p, c in camadas:
            if c == fib and not fibra:
                continue
            corpo += _cheio([p], c)
    nomes = {"tira": "papel rasgado · tira", "topo": "papel rasgado · borda de cima", "janela": "papel rasgado · janela",
             "canto": "papel rasgado · canto", "mascara": "rasgo · máscara (preto = mostra)", "vertical": "papel rasgado · lateral",
             "dupla": "papel rasgado · 2 tiras"}
    el = elemento(w, h, f'<g clip-path="url(#cr)">{corpo}</g>', nomes[modo], FAM,
                  defs=defs + f'<clipPath id="cr"><rect width="{w}" height="{h}"/></clipPath>',
                  nota="o rasgo REVELA algo que importa (antes/depois); fibra branca 2–6 px, sombra 2–4 px")
    return claro(el) if modo == "mascara" else el


# ================================================================ 6. tinta de carimbo
def filtro_carimbo(id_, desgaste=0.5, seed=3, espalha=1.2):
    """<filter> de tinta de carimbo para QUALQUER forma/texto em curvas: borda que treme (deslocamento), tinta
    irregular (manchas) e falhas finas (pó). desgaste 0 = novo (~98% de tinta), 0,5 ≈ 92%, 1 = gasto (~72%) —
    cobertura medida no Chrome (ruído opaco; k = 40; limiar = 0,66 − 0,13·desgaste)."""
    k = 40.0
    thr = 0.66 - 0.13 * desgaste
    op = "1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0 1"
    return (f'<filter id="{id_}" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="{seed}" result="m0"/>'
            f'<feColorMatrix in="m0" type="matrix" values="{op}" result="m"/>'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="1" seed="{seed + 1}" result="p0"/>'
            f'<feColorMatrix in="p0" type="matrix" values="{op}" result="p"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="m" scale="{3 + 4 * espalha:.1f}" xChannelSelector="R" '
            f'yChannelSelector="G" result="d"/>'
            f'<feComposite in="m" in2="p" operator="arithmetic" k1="0" k2="0.45" k3="0.55" k4="0" result="mix"/>'
            f'<feColorMatrix in="mix" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  {k:.1f} 0 0 0 {-k * thr:.3f}" '
            f'result="falha"/>'
            f'<feComposite in="d" in2="falha" operator="out"/></filter>')


def carimbo(f, modo="retangulo", w=520, h=260, desgaste=0.5, cor=None, ang=None, seed=0, fundo_claro=False):
    """Formas carimbadas (a TEXTURA de tinta; selos com texto ficam em selos.py). modo: retangulo (tarja) · moldura
    (dupla) · anel · circulo · barra · deslocado (2 batidas)."""
    from .nucleo import ret
    cor = cor or (f.acento if not fundo_claro else f.fundo)
    ang = f.angulo if ang is None else ang
    s = semente(f, "carimbo", modo, seed) % 997
    e = f.traco * 2.2
    cx, cy = w / 2, h / 2
    if modo == "retangulo":
        forma = f'<path d="{ret(w * 0.08, h * 0.2, w * 0.84, h * 0.6, f.raio_sm)}" fill="{cor}"/>'
    elif modo == "moldura":
        forma = (f'<path d="{ret(w * 0.06, h * 0.14, w * 0.88, h * 0.72, f.raio_sm)}" fill="none" stroke="{cor}" '
                 f'stroke-width="{e * 1.4:.1f}"/><path d="{ret(w * 0.06 + e * 2.6, h * 0.14 + e * 2.6, w * 0.88 - e * 5.2, h * 0.72 - e * 5.2, max(0.0, f.raio_sm - e * 2.6))}" '
                 f'fill="none" stroke="{cor}" stroke-width="{e * 0.7:.1f}"/>')
    elif modo == "anel":
        R = min(w, h) * 0.42
        forma = (f'<circle cx="{cx}" cy="{cy}" r="{R:.1f}" fill="none" stroke="{cor}" stroke-width="{e * 1.6:.1f}"/>'
                 f'<circle cx="{cx}" cy="{cy}" r="{R * 0.74:.1f}" fill="none" stroke="{cor}" stroke-width="{e * 0.7:.1f}"/>')
    elif modo == "circulo":
        forma = f'<circle cx="{cx}" cy="{cy}" r="{min(w, h) * 0.4:.1f}" fill="{cor}"/>'
    elif modo == "barra":
        forma = f'<rect x="{w * 0.04}" y="{h * 0.38}" width="{w * 0.92}" height="{h * 0.24}" fill="{cor}"/>'
    else:
        forma = (f'<g opacity="0.55" transform="translate(7 -5) rotate(1.4 {cx} {cy})"><path d="{ret(w * 0.08, h * 0.2, w * 0.84, h * 0.6, f.raio_sm)}" fill="{cor}"/></g>'
                 f'<path d="{ret(w * 0.08, h * 0.2, w * 0.84, h * 0.6, f.raio_sm)}" fill="{cor}"/>')
    corpo = f'<g filter="url(#ct)" transform="rotate({ang:.2f} {cx} {cy})">{forma}</g>'
    nomes = {"retangulo": "carimbo · tarja", "moldura": "carimbo · moldura dupla", "anel": "carimbo · anel",
             "circulo": "carimbo · disco", "barra": "carimbo · barra", "deslocado": "carimbo · 2 batidas"}
    el = elemento(w, h, corpo, f"{nomes[modo]} · desgaste {desgaste:g}", FAM, defs=filtro_carimbo("ct", desgaste, s),
                  nota="marca da MARCA (nunca selo oficial/órgão); ±4° do ângulo da ficha; filtro_carimbo() serve p/ texto")
    return claro(el) if fundo_claro else el


# ================================================================ 7. risografia
def _filtro_riso(id_, seed, cobertura=0.93, grao_=0.9):
    """Tinta de riso: cobertura quase cheia + pontinhos sem tinta (grão de estêncil) e leve variação (manchas).
    cobertura = fração com tinta, medida no Chrome (ruído opaco; k = 30)."""
    thr = float(np.interp(cobertura, [0.43, 0.6, 0.75, 0.865, 0.95, 0.99], [0.5, 0.54, 0.58, 0.62, 0.665, 0.72]))
    op = "1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0 1"
    return (f'<filter id="{id_}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{grao_}" numOctaves="2" seed="{seed}" result="p0"/>'
            f'<feColorMatrix in="p0" type="matrix" values="{op}" result="p"/>'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3" seed="{seed + 3}" result="m0"/>'
            f'<feColorMatrix in="m0" type="matrix" values="{op}" result="m"/>'
            f'<feComposite in="p" in2="m" operator="arithmetic" k2="0.7" k3="0.3" result="mix"/>'
            f'<feColorMatrix in="mix" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -30 0 0 0 {30 * thr:.3f}" '
            f'result="buracos"/><feComposite in="SourceGraphic" in2="buracos" operator="in"/></filter>')


def riso(f, modo="sobreposicao", w=900, h=900, seed=0):
    """Risografia sobre papel: 2 tintas planas, grão de estêncil, desregistro de 1–3 px NUMA direção.
    modo: chapado (só a textura de tinta) · sobreposicao (2 formas, multiply = 3ª cor) · degrade (degradê granulado de
    tinta) · desregistro (mesma forma nas 2 tintas, deslocada) · listras."""
    s = semente(f, "riso", modo, seed) % 997
    t1, t2 = f.acento, f.fundo
    dx, dy = 3, 2
    defs = _filtro_riso("r1", s) + _filtro_riso("r2", s + 11)
    corpo = f'<rect width="{w}" height="{h}" fill="{f.papel}"/>'
    if modo == "chapado":
        corpo += f'<rect x="{w * 0.1}" y="{h * 0.1}" width="{w * 0.8}" height="{h * 0.8}" fill="{t1}" filter="url(#r1)"/>'
    elif modo == "sobreposicao":
        corpo += (f'<g style="mix-blend-mode:multiply"><circle cx="{w * 0.4}" cy="{h * 0.42}" r="{w * 0.28}" fill="{t1}" '
                  f'filter="url(#r1)"/></g><g style="mix-blend-mode:multiply" transform="translate({dx} {dy})">'
                  f'<rect x="{w * 0.38}" y="{h * 0.38}" width="{w * 0.48}" height="{h * 0.48}" fill="{t2}" fill-opacity="0.9" '
                  f'filter="url(#r2)"/></g>')
    elif modo == "degrade":
        defs += (f'<linearGradient id="dg" x1="0" x2="1"><stop offset="0" stop-color="{t1}"/>'
                 f'<stop offset="1" stop-color="{t1}" stop-opacity="0"/></linearGradient>'
                 f'<filter id="dd" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
                 f'<feTurbulence type="fractalNoise" baseFrequency="0.95" numOctaves="1" seed="{s}" result="p"/>'
                 f'<feComposite in="SourceAlpha" in2="p" operator="arithmetic" k2="1.6" k3="-1.2" k4="0.05" result="th"/>'
                 f'<feColorMatrix in="th" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 30 -12" result="mk"/>'
                 f'<feFlood flood-color="{t1}"/><feComposite in2="mk" operator="in"/></filter>')
        corpo += f'<rect x="{w * 0.06}" y="{h * 0.2}" width="{w * 0.88}" height="{h * 0.6}" fill="url(#dg)" filter="url(#dd)"/>'
    elif modo == "desregistro":
        from .nucleo import ret
        d = ret(w * 0.18, h * 0.18, w * 0.64, h * 0.64, w * 0.32)
        corpo += (f'<g style="mix-blend-mode:multiply"><path d="{d}" fill="{t1}" filter="url(#r1)"/></g>'
                  f'<g style="mix-blend-mode:multiply" transform="translate({dx * 2} {dy * 2})"><path d="{d}" fill="none" '
                  f'stroke="{t2}" stroke-width="{f.traco * 3:.1f}" filter="url(#r2)"/></g>')
    elif modo == "listras":
        ls = "".join(f'<rect x="0" y="{y:.1f}" width="{w}" height="{h * 0.045:.1f}"/>' for y in np.arange(h * 0.08, h * 0.92, h * 0.09))
        corpo += (f'<g style="mix-blend-mode:multiply" fill="{t1}" filter="url(#r1)">{ls}</g>'
                  f'<g style="mix-blend-mode:multiply" transform="translate({dx} {dy}) rotate(90 {w / 2} {h / 2})" fill="{t2}" '
                  f'fill-opacity="0.85" filter="url(#r2)">{ls}</g>')
    nomes = {"chapado": "riso · tinta chapada", "sobreposicao": "riso · 2 tintas sobrepostas", "degrade": "riso · degradê granulado",
             "desregistro": "riso · desregistro", "listras": "riso · tramas cruzadas"}
    return claro(elemento(w, h, corpo, nomes[modo], FAM, defs=defs,
                          nota="2–3 tintas, desregistro 1–3 px numa direção só, papel; multiply; nunca foto em 8 cores"))


# ================================================================ 8. scanlines
def scanlines(f, modo="finas", w=480, h=360, cor=None, camada=False, seed=0):
    """Linhas de varredura — SÓ dentro do visor/tela. Padrão: uma TELA (visor com o raio grande da ficha, brilho de tela
    ligada na cor do fundo clareada, scanlines e vinheta). camada=True devolve só a camada de linhas (alfa) para pôr
    sobre uma foto/vídeo. modo: finas (1/3 px) · medias (1/4) · crt (2/6 + grade de abertura) · barra (faixa que rola)
    · claras (linhas claras sobre tela escura)."""
    from .nucleo import ret
    claras = modo == "claras"
    cl = cor or ("#FFFFFF" if claras else "#000000")
    per, esp_, op = {"finas": (3, 1, 0.32), "medias": (4, 1, 0.3), "crt": (6, 2, 0.4), "barra": (4, 1, 0.28),
                     "claras": (4, 1, 0.1)}[modo]
    defs = (f'<pattern id="sl" width="{w}" height="{per}" patternUnits="userSpaceOnUse">'
            f'<rect width="{w}" height="{esp_}" fill="{cl}" fill-opacity="{op}"/></pattern>')
    camada_ = f'<rect width="{w}" height="{h}" fill="url(#sl)"/>'
    if modo == "crt":
        defs += (f'<pattern id="ap" width="3" height="{h}" patternUnits="userSpaceOnUse">'
                 f'<rect width="1" height="{h}" fill="{cl}" fill-opacity="0.12"/></pattern>')
        camada_ += f'<rect width="{w}" height="{h}" fill="url(#ap)"/>'
    if modo == "barra":
        defs += ('<linearGradient id="bb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                 '<stop offset="0.5" stop-color="#fff" stop-opacity="0.16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
                 '</linearGradient>')
        camada_ += f'<rect y="{h * 0.56:.1f}" width="{w}" height="{h * 0.16:.1f}" fill="url(#bb)"/>'
    nomes = {"finas": "scanlines · 1 px a cada 3", "medias": "scanlines · 1 px a cada 4", "crt": "scanlines · CRT + abertura",
             "barra": "scanlines · barra que rola", "claras": "scanlines · claras (tela escura)"}
    css = (f"background:repeating-linear-gradient(0deg,rgba(0,0,0,{op}) 0 {esp_}px,transparent {esp_}px {per}px)")
    nota = f"{esp_} px a cada {per} px, {op * 100:.0f}%; só dentro do visor/tela, nunca na peça inteira"
    if camada:
        return claro(elemento(w, h, camada_, nomes[modo] + " · camada", FAM, defs=defs, css=css, nota=nota))
    m = 6.0
    tela = ret(m, m, w - 2 * m, h - 2 * m, f.raio)
    luz = clarear(f.fundo, 0.06 if claras else 0.34)
    defs += (f'<clipPath id="vs"><path d="{tela}"/></clipPath>'
             f'<radialGradient id="lg" cx="0.5" cy="0.45" r="0.7">{_paradas(luz, f.fundo, 9, lambda t: t ** 0.9)}</radialGradient>'
             '<radialGradient id="vg" cx="0.5" cy="0.5" r="0.7"><stop offset="0.55" stop-color="#000" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#000" stop-opacity="0.45"/></radialGradient>')
    corpo = (f'<g clip-path="url(#vs)"><rect width="{w}" height="{h}" fill="url(#lg)"/>{camada_}'
             f'<rect width="{w}" height="{h}" fill="url(#vg)"/></g>'
             f'<path d="{tela}" fill="none" stroke="{f.apoio}" stroke-opacity="0.6" stroke-width="{max(1.5, f.traco * 0.6):.2f}"/>')
    return elemento(w, h, corpo, nomes[modo] + " · tela", FAM, defs=defs, css=css, nota=nota)


# ================================================================ 9. poeira e arranhões
def poeira(f, modo="leve", w=1080, h=1080, cor=None, seed=0, fundo_claro=False):
    """Poeira e arranhões SUTIS em vetor (pontinhos irregulares, fios, riscos de película).
    modo: leve · fios · arranhoes · cantos · mistura · luz (pó desfocado)."""
    r = rng(f, "poeira", modo, seed)
    cor = cor or (f.fundo if fundo_claro else f.tinta)
    pts, fios, riscos = [], [], []
    n_p = {"leve": 260, "fios": 160, "arranhoes": 60, "cantos": 420, "mistura": 300, "luz": 140}[modo]
    for _ in range(n_p):
        if modo == "cantos":
            x = r.choice([r.betavariate(0.6, 3), 1 - r.betavariate(0.6, 3)]) * w
            y = r.choice([r.betavariate(0.6, 3), 1 - r.betavariate(0.6, 3)]) * h
        else:
            x, y = r.uniform(0, w), r.uniform(0, h)
        rr = r.choice([0.6, 0.8, 1.0, 1.2, 1.6, 2.2, 3.0]) * (2.4 if modo == "luz" else 1)
        k = r.randint(5, 8)
        pts.append([(x + rr * r.uniform(0.55, 1.25) * math.cos(2 * math.pi * i / k),
                     y + rr * r.uniform(0.55, 1.25) * math.sin(2 * math.pi * i / k)) for i in range(k)])
    if modo in ("fios", "mistura"):
        for _ in range(9 if modo == "fios" else 5):
            x, y, a = r.uniform(0, w), r.uniform(0, h), r.uniform(0, math.pi * 2)
            L = r.uniform(18, 60)
            P = [(x, y)]
            for i in range(8):
                a += r.gauss(0, 0.45)
                x, y = x + L / 8 * math.cos(a), y + L / 8 * math.sin(a)
                P.append((x, y))
            fios.append(P)
    if modo in ("arranhoes", "mistura"):
        for _ in range(10 if modo == "arranhoes" else 4):
            x = r.uniform(0, w)
            y0 = r.uniform(-0.2, 0.6) * h
            y1 = y0 + r.uniform(0.2, 0.9) * h
            ys = np.linspace(y0, y1, 12)
            riscos.append([(x + 1.6 * math.sin(yy / r.uniform(60, 160)) + r.gauss(0, 0.3), yy) for yy in ys])
    op = 0.45 if not fundo_claro else 0.38
    corpo = _cheio(pts, cor, op)
    if fios:
        corpo += f'<path d="{"".join(curva(p) for p in fios)}" fill="none" stroke="{cor}" stroke-width="1.1" stroke-opacity="{op}"/>'
    if riscos:
        corpo += f'<path d="{"".join(curva(p) for p in riscos)}" fill="none" stroke="{cor}" stroke-width="1.2" stroke-opacity="{op * 0.8:.2f}"/>'
    defs = f'<clipPath id="cpo"><rect width="{w}" height="{h}"/></clipPath>'     # riscos/fios nunca saem da caixa
    if modo == "luz":
        defs += ('<filter id="bl" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.6"/></filter>')
        corpo = f'<g filter="url(#bl)">{corpo}</g>'
    corpo = f'<g clip-path="url(#cpo)">{corpo}</g>'
    nomes = {"leve": "poeira · leve", "fios": "poeira · com fios", "arranhoes": "arranhões de película", "cantos": "poeira · nos cantos",
             "mistura": "poeira + fios + arranhões", "luz": "pó de luz (desfocado)"}
    el = elemento(w, h, corpo, nomes[modo], FAM, defs=defs, nota="1 defeito por peça (poeira OU dobra OU luz); fora do rosto e do "
                  "texto; real escaneado > simulado")
    return claro(el) if fundo_claro else el


# ================================================================ 10. degradê com grão
def gradiente_grao(f, modo="poca", w=1080, h=1350, seed=0):
    """Fundo com degradê ENTRE VIZINHAS (OKLCH, base clareada — luz na cor de destaque vira lama) + vinheta + grão
    por último (segura o banding). modo: poca (luz atrás do herói) · chao (ciclorama) · canto · duas (herói + chão) ·
    feixe (faixa de luz) · brasa (acento escurecido → fundo) · papel (claro)."""
    s = semente(f, "gg", modo, seed) % 997
    claro_ = modo == "papel"
    base = f.papel if claro_ else f.fundo
    luz = clarear(base, 0.21) if not claro_ else clarear(base, 0.03)
    escuro = clarear(base, -0.12 if claro_ else -0.02)
    defs, corpo = "", f'<rect width="{w}" height="{h}" fill="{base}"/>'
    if modo == "poca":
        defs += f'<radialGradient id="p1" cx="0.66" cy="0.3" r="0.62">{_paradas(luz, base, 9, lambda t: t ** 0.8)}</radialGradient>'
        corpo += f'<rect width="{w}" height="{h}" fill="url(#p1)"/>'
    elif modo == "chao":
        defs += (f'<linearGradient id="p1" x1="0" y1="0" x2="0" y2="1">{_paradas(base, clarear(base, 0.07), 7)}</linearGradient>'
                 f'<radialGradient id="p2" cx="0.5" cy="0.66" r="0.55" gradientTransform="translate(0 0.66) scale(1 0.4) translate(0 -0.66)">'
                 f'{_paradas(clarear(base, 0.11), base, 9, lambda t: t ** 0.7)}</radialGradient>')
        corpo += f'<rect width="{w}" height="{h}" fill="url(#p1)"/><rect width="{w}" height="{h}" fill="url(#p2)" style="mix-blend-mode:screen"/>'
    elif modo == "canto":
        defs += f'<radialGradient id="p1" cx="0" cy="0" r="1.1">{_paradas(luz, base, 9, lambda t: t ** 0.6)}</radialGradient>'
        corpo += f'<rect width="{w}" height="{h}" fill="url(#p1)"/>'
    elif modo == "duas":
        defs += (f'<radialGradient id="p1" cx="0.62" cy="0.28" r="0.5">{_paradas(luz, base, 9, lambda t: t ** 0.8)}</radialGradient>'
                 f'<radialGradient id="p2" cx="0.4" cy="0.92" r="0.5">{_paradas(clarear(base, 0.09), base, 9, lambda t: t ** 0.8)}</radialGradient>')
        corpo += (f'<rect width="{w}" height="{h}" fill="url(#p1)"/>'
                  f'<rect width="{w}" height="{h}" fill="url(#p2)" style="mix-blend-mode:screen"/>')
    elif modo == "feixe":
        defs += (f'<linearGradient id="p1" x1="0" y1="0" x2="1" y2="0.35" gradientUnits="objectBoundingBox">'
                 f'<stop offset="0.3" stop-color="{base}"/><stop offset="0.5" stop-color="{clarear(base, 0.09)}"/>'
                 f'<stop offset="0.7" stop-color="{base}"/></linearGradient>')
        corpo += f'<rect width="{w}" height="{h}" fill="url(#p1)"/>'
    elif modo == "brasa":
        quente = oklch_mix(f.fundo, f.acento, 0.38)
        defs += f'<radialGradient id="p1" cx="0.5" cy="1.0" r="0.9">{_paradas(quente, base, 11, lambda t: t ** 0.75)}</radialGradient>'
        corpo += f'<rect width="{w}" height="{h}" fill="url(#p1)"/>'
    elif modo == "papel":
        defs += f'<radialGradient id="p1" cx="0.5" cy="0.45" r="0.75">{_paradas(luz, escuro, 9, lambda t: t ** 1.6)}</radialGradient>'
        corpo += f'<rect width="{w}" height="{h}" fill="url(#p1)"/>'
    # vinheta + grão (sempre por último)
    defs += ('<radialGradient id="vn" cx="0.5" cy="0.5" r="0.75"><stop offset="0.55" stop-color="#000" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="#000" stop-opacity="{0.22 if not claro_ else 0.08}"/></radialGradient>')
    corpo += f'<rect width="{w}" height="{h}" fill="url(#vn)"/>'
    defs += filtro_grao("gr", w, h, "claro" if claro_ else "escuro", 0.82, 2, 0.12 if claro_ else 0.15, 2.6, seed=s)
    corpo += f'<rect width="{w}" height="{h}" filter="url(#gr)"/>'
    nomes = {"poca": "fundo · poça de luz + grão", "chao": "fundo · ciclorama (chão) + grão", "canto": "fundo · luz do canto + grão",
             "duas": "fundo · 2 poças + grão", "feixe": "fundo · feixe de luz + grão", "brasa": "fundo · brasa (acento → fundo) + grão",
             "papel": "fundo · papel com luz + grão"}
    el = elemento(w, h, corpo, nomes[modo], FAM, defs=defs,
                  nota="degradê só entre vizinhas, interpolado em OKLCH; luz fora do centro; vinheta ≤ 30%; grão por último")
    return claro(el) if claro_ else el


# ================================================================ amostras
@amostra(FAM, "grão")
def _a_grao(f):
    return [grao(f, "escuro", "fino"), grao(f, "escuro", "medio"), grao(f, "escuro", "grosso"),
            grao(f, "claro", "fino"), grao(f, "claro", "medio"), grao(f, "claro", "grosso"),
            grao(f, "escuro", "fino", forca=0.32, gama=5, nome="poeira de luz (esparsa)")]


@amostra(FAM, "papel")
def _a_papel(f):
    return [papel(f), papel(f, "aspero"), papel(f, "kraft"), papel(f, "jornal"), papel(f, "vinco"),
            papel(f, "cartao"), papel(f, "reciclado"), papel(f, "telado")]


@amostra(FAM, "amassado e dobras")
def _a_amass(f):
    return [amassado(f, "em4", sobre_papel=True, seed=3), amassado(f, "em8", sobre_papel=True),
            amassado(f, "vinco", sobre_papel=True)]


@amostra(FAM, "xerox")
def _a_xerox(f):
    return [xerox(f, "toner", fundo_claro=True, seed=3), xerox(f, "riscas", fundo_claro=True),
            xerox(f, "bloco", fundo_claro=True, seed=2), xerox(f, "borda", fundo_claro=True)]


@amostra(FAM, "papel rasgado")
def _a_rasg(f):
    return [borda_rasgada(f), borda_rasgada(f, "dupla"), borda_rasgada(f, "topo", h=600),
            borda_rasgada(f, "janela", w=900, h=700), borda_rasgada(f, "canto", w=700, h=700),
            borda_rasgada(f, "vertical", w=700, h=800), borda_rasgada(f, "mascara", cor="#000"),
            borda_rasgada(f, "tira", cor=f.acento, seed=4)]


@amostra(FAM, "tinta de carimbo")
def _a_carimbo(f):
    return [carimbo(f, desgaste=0.2), carimbo(f, desgaste=0.6, seed=2), carimbo(f, "moldura", desgaste=0.5),
            carimbo(f, "anel", w=360, h=360, desgaste=0.55), carimbo(f, "barra", desgaste=0.45),
            carimbo(f, "moldura", desgaste=0.7, fundo_claro=True, seed=3)]


@amostra(FAM, "risografia")
def _a_riso(f):
    return [riso(f, "chapado"), riso(f), riso(f, "degrade"), riso(f, "desregistro"), riso(f, "listras")]


@amostra(FAM, "scanlines")
def _a_scan(f):
    return [scanlines(f, "finas"), scanlines(f, "medias"), scanlines(f, "crt"), scanlines(f, "barra"),
            scanlines(f, "claras")]


@amostra(FAM, "poeira e arranhões")
def _a_poeira(f):
    # pontinhos sozinhos no escuro leem como CÉU ESTRELADO (D1) → só sobre o papel (sujeira de scanner); no escuro ficam
    # os modos com fio/risco (que identificam poeira de película). "pó de luz" desfocado removido: bokeh/estrelas.
    return [poeira(f, fundo_claro=True), poeira(f, "fios"), poeira(f, "arranhoes"),
            poeira(f, "cantos", fundo_claro=True, seed=3), poeira(f, "mistura"),
            poeira(f, "mistura", fundo_claro=True, seed=2)]


@amostra(FAM, "degradê com grão")
def _a_gg(f):
    return [gradiente_grao(f), gradiente_grao(f, "chao"), gradiente_grao(f, "canto"), gradiente_grao(f, "duas"),
            gradiente_grao(f, "feixe"), gradiente_grao(f, "brasa"), gradiente_grao(f, "papel")]
