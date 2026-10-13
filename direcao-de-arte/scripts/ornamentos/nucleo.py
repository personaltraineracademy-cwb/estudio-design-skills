"""ornamentos.nucleo — contrato comum da biblioteca de ELEMENTOS GRÁFICOS (peças, sites, artes).

Regra-mãe (references/elementos.md): todo elemento nasce da FICHA da marca (5 números do logo + cores + fontes) —
assim 150 elementos diferentes ainda parecem uma família só.

Contrato de toda função de elemento:
    f(ficha: Ficha, **params) -> Elemento(svg, caixa, css, nome, familia, nota)
  - svg   : documento SVG COMPLETO (viewBox = tamanho natural do elemento), texto SEMPRE em curvas (fonte → path),
            cores só da ficha (ou derivadas da ficha), semente fixa (ficha.seed + params) → reprodutível;
  - caixa : (x0, y0, x1, y1) da TINTA dentro do viewBox (para alinhar pela tinta no palco/compor);
  - css   : opcional — versão CSS/HTML para SITE quando fizer sentido (ex.: contêiner com border-radius);
  - nota  : 1 linha "quando usar / de onde vem".
Registro: cada módulo registra AMOSTRAS com @amostra("familia", "nome") — a função recebe a ficha e devolve uma lista
de Elementos (variações). `catalogo.py` renderiza tudo que está registrado, família por família.

Filtros SVG: sempre `color-interpolation-filters="sRGB"` e região ampliada (x=-20% y=-20% width=140% height=140%).
"""
import math
import os
import random
import sys
from dataclasses import dataclass, field, replace

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)
import compor as _K  # noqa: E402,F401  (põe brand-system/scripts no path)
from _base import font as _font  # noqa: E402


@dataclass
class Ficha:
    """5 números do logo + cores por papel + fontes. Valores em px num lado de 1080 (arte) — no site, as mesmas
    proporções em CSS."""
    unidade: float = 24.0          # módulo/grão do sistema (U = 0,022 × lado menor ≈ 24 px num 1080)
    traco: float = 3.0             # espessura padrão de fio/contorno (fino = traço; grosso = 2 × traço)
    raio: float = 28.0             # raio padrão dos elementos = `cartao` (md) da escala de forma (references/forma.md:
    #                                arte 1080 → 0 · 16 · 28 · 44; no celular 28 ≈ o "raio 10" das redes). O logo não arredonda.
    raio_sm: float = 16.0          # `rotulo` (etiqueta, campo, elemento pequeno)
    raio_lg: float = 44.0          # `moldura` (moldura recuada, bloco grande) — use no lugar de "2 × raio"
    angulo: float = -6.0           # ângulo do sistema (faixas, carimbos, inclinações)
    fundo: str = "#0C0B09"
    tinta: str = "#FEFEFC"
    acento: str = "#E2B04A"
    sobre_acento: str = "#0C0B09"
    papel: str = "#ECE7DC"
    apoio: str = "#8A8A86"         # cinza de apoio (fios finos, legendas)
    fonte_display: str = "Big Shoulders:900"
    fonte_texto: str = "Archivo:600"
    fonte_mono: str = "Azeret Mono:600"
    seed: int = 7
    nome: str = "padrão"

    def com(self, **kw):
        return replace(self, **kw)

    def rnd(self, *salt):
        """Sorteio reprodutível entre execuções (hash() de str muda a cada processo — PYTHONHASHSEED)."""
        import hashlib
        chave = "|".join([str(self.seed)] + [str(s) for s in salt]).encode("utf-8")
        return random.Random(int.from_bytes(hashlib.sha256(chave).digest()[:8], "big"))


@dataclass
class Elemento:
    svg: str
    caixa: tuple
    nome: str
    familia: str
    css: str = ""
    nota: str = ""
    w: float = 0.0
    h: float = 0.0


REGISTRO = {}          # familia -> list[(nome, fn)]


def amostra(familia, nome):
    """Decorator: registra um gerador de amostras `fn(ficha) -> list[Elemento]` no catálogo."""
    def deco(fn):
        REGISTRO.setdefault(familia, []).append((nome, fn))
        return fn
    return deco


def svg_doc(w, h, corpo, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}">' + (f"<defs>{defs}</defs>" if defs else "") + corpo + "</svg>")


def elemento(w, h, corpo, nome, familia, defs="", caixa=None, css="", nota=""):
    return Elemento(svg_doc(w, h, corpo, defs), caixa or (0, 0, w, h), nome, familia, css, nota, w, h)


# ---------------------------------------------------------------- texto em curvas
def texto(spec, s, size, x, baseline, fill, tracking=0.0, anchor="start"):
    """Texto → <path> (curvas, kerning da fonte). anchor: start | middle | end. Devolve (svg, largura)."""
    f = _font(spec)
    w = f.width(s, size, tracking)
    x0 = x if anchor == "start" else x - w / 2 if anchor == "middle" else x - w
    d = f.path(s, size, x0, baseline, tracking)
    return f'<path d="{d}" fill="{fill}"/>', w


def cap(spec):
    """Altura da maiúscula em fração do corpo."""
    return _font(spec).cap


def largura(spec, s, size, tracking=0.0):
    return _font(spec).width(s, size, tracking)


def texto_circulo(spec, s, size, cx, cy, r, fill, start_deg=-90, tracking=0.0, outside=True):
    d = _font(spec).path_on_circle(s, size, cx, cy, r, start_deg, tracking, outside, True)
    return f'<path d="{d}" fill="{fill}"/>'


# ---------------------------------------------------------------- geometria útil
def ret(x, y, w, h, r=0.0, cantos=None):
    """Retângulo como path; r único ou `cantos` = (te, td, bd, be) — permite pasta, aba, balão, assimetria."""
    te, td, bd, be = cantos if cantos else (r, r, r, r)
    m = min(w, h) / 2
    te, td, bd, be = (max(0.0, min(v, m)) for v in (te, td, bd, be))

    def arco(rr, x1, y1):
        return f"A{rr:.2f} {rr:.2f} 0 0 1 {x1:.2f} {y1:.2f}" if rr else f"L{x1:.2f} {y1:.2f}"
    return (f"M{x + te:.2f} {y:.2f}H{x + w - td:.2f}" + arco(td, x + w, y + td) + f"V{y + h - bd:.2f}"
            + arco(bd, x + w - bd, y + h) + f"H{x + be:.2f}" + arco(be, x, y + h - be) + f"V{y + te:.2f}"
            + arco(te, x + te, y) + "Z")


def poligono(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"


def polilinha(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def suave(pts, fechado=False, tensao=0.5):
    """Catmull-Rom → Bézier (curva suave passando pelos pontos)."""
    if len(pts) < 3:
        return polilinha(pts)
    P = list(pts) + ([pts[0], pts[1], pts[2]] if fechado else [])
    d = f"M{P[0][0]:.2f} {P[0][1]:.2f}"
    n = len(pts) if fechado else len(pts) - 1
    for i in range(n):
        p0 = P[i - 1] if i > 0 else (P[-3] if fechado else P[0])
        p1, p2 = P[i], P[i + 1]
        p3 = P[i + 2] if i + 2 < len(P) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * tensao / 3, p1[1] + (p2[1] - p0[1]) * tensao / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tensao / 3, p2[1] - (p3[1] - p1[1]) * tensao / 3)
        d += f" C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}"
    return d + ("Z" if fechado else "")


def ruido1d(rnd, n, oit=3):
    """Ruído suave 1-D em [-1, 1] (soma de senos com fases sorteadas) — sem dependências."""
    fs = [(rnd.uniform(0.5, 1.5) * (2 ** k), rnd.uniform(0, 2 * math.pi), 0.5 ** k) for k in range(oit)]
    tot = sum(a for _, _, a in fs)
    return [sum(a * math.sin(f * 2 * math.pi * i / n + ph) for f, ph, a in fs) / tot for i in range(n)]


def filtro(id_, corpo):
    return (f'<filter id="{id_}" x="-20%" y="-20%" width="140%" height="140%" '
            f'color-interpolation-filters="sRGB">{corpo}</filter>')


# ---------------------------------------------------------------- fichas prontas (teste e catálogo)
def ficha_exemplo(produto="todos", raio=28.0):
    """Ficha de exemplo do catálogo (4 produtos com cores próprias) — um produto por vez."""
    cores = {"todos": ("#101010", "#FAFAF7", "#C9A45C", "#101010"),
             "linha-a": ("#101010", "#FAFAF7", "#2F6BFF", "#101010"),
             "linha-b": ("#101010", "#FAFAF7", "#F2542D", "#101010"),
             "linha-c": ("#101010", "#FAFAF7", "#7A5CFF", "#101010")}[produto]
    return Ficha(fundo=cores[0], tinta=cores[1], acento=cores[2], sobre_acento=cores[3], raio=raio,
                 nome=f"exemplo · {produto}")
