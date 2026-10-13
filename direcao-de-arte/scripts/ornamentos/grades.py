"""ornamentos.grades — família "GRIDS VISÍVEIS": a estrutura vira elemento (tradição suíça, Crouwel, Gerstner).

Números (references/elementos.md "Grids"; pesquisa 4 §4): coluna = (L − 2·margem − (n−1)·gutter) / n;
feed 1080×1350 = 6 col × 8 lin, margem 60–80, gutter 24 · 1:1 = 6 × 6 · story 9:16 = zona de texto x 108–972,
y 240–1248 (x ≤ 852 abaixo de y 936 — coluna de ícones do Reels) · landing = container 1320, 12 col, gutter 24 ·
linha de base 8 px. Grid como marca: NO MÁXIMO 2 recursos por peça (cruzes "+" de 8–12 px a 15–25%, coordenadas
A1…F8 em mono 14–18 px na margem, marcas de corte, timecode como coordenada). Gutter padrão = ficha.unidade.
Texto sempre em curvas (nucleo.texto). Cores: tinta/apoio em fio fino; acento só para 1 destaque.

  modular · baseline · colunas_site · isometrica · polar · corte_sangria · milimetrado · registro
"""
import math

import numpy as np

from .nucleo import amostra, texto, ret
from .linhas import traco_attr, _campo, _ln, _cheio, _esp, _ret, pontos_d, claro

FAM = "grades"
NOTA = "grid visível = no máximo 2 recursos por peça; fio fino 15–25%; presa às margens da peça"
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _cruz(x, y, s):
    return f"M{x - s:.1f} {y:.1f}h{2 * s:.1f}M{x:.1f} {y - s:.1f}v{2 * s:.1f}"


def _hex_rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _mistura(a, b, t):
    """Cor sólida = a·(1−t) + b·t (para tirar a transparência de um preenchimento sobre fundo conhecido)."""
    ra, rb = _hex_rgb(a), _hex_rgb(b)
    return "#" + "".join(f"{round(x * (1 - t) + y * t):02X}" for x, y in zip(ra, rb))


def _mono(f, s, size, x, y, cor, anchor="start"):
    return texto(f.fonte_mono, s, size, x, y, cor, 0.02, anchor)[0]


# ================================================================ 1. grade modular
FORMATOS = {"feed": (1080, 1350, 6, 8, 72), "quadrado": (1080, 1080, 6, 6, 72), "story": (1080, 1920, 6, 7, None),
            "paisagem": (1920, 1080, 12, 6, 96)}


def _modulos(W, H, cols, rows, m, g, zona=None):
    x0, y0, x1, y1 = zona or (m, m, W - m, H - m)
    cw = (x1 - x0 - (cols - 1) * g) / cols
    rh = (y1 - y0 - (rows - 1) * g) / rows
    xs = [x0 + i * (cw + g) for i in range(cols)]
    ys = [y0 + j * (rh + g) for j in range(rows)]
    return xs, ys, cw, rh, (x0, y0, x1, y1)


def _nos(xs, ys, cw, rh, g, caixa):
    """Cruzamentos do grid = centro dos gutters + a moldura (onde as cruzes '+' vão)."""
    x0, y0, x1, y1 = caixa
    nx = [x0] + [x + cw + g / 2 for x in xs[:-1]] + [x1]
    ny = [y0] + [y + rh + g / 2 for y in ys[:-1]] + [y1]
    return nx, ny


def modular(f, formato="feed", estilo="linhas", cor=None, gutter=None, seed=0, fundo_claro=False):
    """Grade modular (colunas × linhas, gutter = unidade da ficha). estilo: linhas · campos · cruzes · coordenadas ·
    destaque (1 bloco no acento) · zonas (story: zona de texto + coluna de ícones)."""
    W, H, cols, rows, m = FORMATOS[formato]
    g = gutter or f.unidade
    cor = cor or f.tinta
    e = _esp(f, 0.5)
    zona = (108, 240, 972, 1248) if formato == "story" else None
    xs, ys, cw, rh, (x0, y0, x1, y1) = _modulos(W, H, cols, rows, m or 0, g, zona)
    corpo = ""
    if estilo in ("linhas", "destaque", "coordenadas", "zonas"):
        rects = "".join(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{rh:.1f}"/>' for x in xs for y in ys)
        corpo += f'<g {traco_attr(cor, e, 0.55)}>{rects}</g>'
        corpo += f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" {traco_attr(cor, e, 0.9)}/>'
    if estilo == "campos":
        rects = "".join(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{rh:.1f}"/>' for x in xs for y in ys)
        corpo += f'<g fill="{cor}" fill-opacity="0.08">{rects}</g>'
    if estilo == "cruzes":
        nx, ny = _nos(xs, ys, cw, rh, g, (x0, y0, x1, y1))
        corpo += f'<path d="{"".join(_cruz(x, y, 6) for x in nx for y in ny)}" {traco_attr(cor, e * 1.2, 0.7)}/>'
    if estilo == "destaque":
        # bloco SÓLIDO por cima dos fios (fio atravessando o acento lia como "cruz" riscada dentro do bloco)
        i, j = 3, 2
        corpo += (f'<rect x="{xs[i]:.1f}" y="{ys[j]:.1f}" width="{2 * cw + g:.1f}" height="{2 * rh + g:.1f}" '
                  f'fill="{f.acento}"/>')
    if estilo == "coordenadas":
        tam = 18
        for i, x in enumerate(xs):
            corpo += _mono(f, LETRAS[i], tam, x + cw / 2, y0 - 22, f.apoio, "middle")
        for j, y in enumerate(ys):
            corpo += _mono(f, str(j + 1), tam, x0 - 20, y + rh / 2 + tam * 0.35, f.apoio, "end")
    if estilo == "zonas" and formato == "story":
        # coluna de ícones do Reels (texto x ≤ 852 abaixo de y 936): a borda cai na BORDA DA 6ª COLUNA (x 848 — 4 px
        # do lado seguro), não a 4 px da borda ("quase"); entre y 936 e 1248, sem faixa sobreposta
        xi = xs[-1]
        tracej = f' stroke-dasharray="{f.unidade * 0.5:.0f} {f.unidade * 0.4:.0f}"'
        corpo += (f'<rect x="{xi:.1f}" y="936" width="{W - xi:.1f}" height="312" fill="{f.acento}" fill-opacity="0.08"/>'
                  f'<path d="M{x1:.0f} 936H{xi:.1f}V1248" {traco_attr(f.acento, e * 1.6, extra=tracej)}/>'
                  f'<rect x="0" y="0" width="{W}" height="240" fill="{cor}" fill-opacity="0.05"/>'
                  f'<rect x="0" y="1248" width="{W}" height="{H - 1248}" fill="{cor}" fill-opacity="0.05"/>')
    nome = f"grade modular · {formato} {cols}×{rows} · {estilo}"
    nota = f"{W}×{H}; margem {m or 'zona segura'}; gutter {g:g}; coluna {cw:.1f} px; " + NOTA
    css = (f".grade{{display:grid;grid-template-columns:repeat({cols},1fr);grid-template-rows:repeat({rows},1fr);"
           f"gap:{g:g}px;padding:{m or 0}px}}")
    el = _campo(W, H, corpo, nome, nota, fam=FAM, fundo_claro=fundo_claro)
    el.css = css
    return el


# ================================================================ 2. linha de base
def baseline(f, estilo="linhas", w=1080, h=1350, passo=8, cor=None, fundo_claro=False):
    """Grade de linha de base (8 px). estilo: linhas (forte a cada 8) · fina (4 + 8) · numerada · colunas (2 col +
    base) · esquema (barras de texto alinhadas à base) · faixas (altura-x)."""
    cor = cor or f.tinta
    e = max(1.0, f.traco * 0.34)
    m = 72
    corpo = ""
    ys = np.arange(m, h - m + 0.1, passo)
    fortes = [[(m, y), (w - m, y)] for k, y in enumerate(ys) if k % 8 == 0]
    finas = [[(m, y), (w - m, y)] for k, y in enumerate(ys) if k % 8]
    if estilo == "fina":
        finas += [[(m, y), (w - m, y)] for y in np.arange(m + passo / 2, h - m, passo)]
    corpo += _ln(finas, cor, e, 0.22) + _ln(fortes, cor, e * 1.5, 0.5)
    if estilo == "numerada":
        for k, y in enumerate(ys):
            if k % 8 == 0:
                corpo += _mono(f, f"{int(y):04d}", 16, m - 10, y + 5.5, f.apoio, "end")
    if estilo in ("colunas", "esquema"):
        g = f.unidade
        cw = (w - 2 * m - g) / 2
        corpo += (f'<rect x="{m}" y="{m}" width="{cw:.1f}" height="{h - 2 * m}" fill="{cor}" fill-opacity="0.05"/>'
                  f'<rect x="{m + cw + g:.1f}" y="{m}" width="{cw:.1f}" height="{h - 2 * m}" fill="{cor}" fill-opacity="0.05"/>')
        if estilo == "esquema":
            import random
            r = random.Random(4)
            bars = []
            for col in range(2):
                xb = m + col * (cw + g)
                y = m + passo * 12
                while y < h - m - passo * 4:
                    L = cw * (r.uniform(0.55, 1.0) if r.random() > 0.15 else r.uniform(0.2, 0.5))
                    bars.append(ret(xb, y - passo, L, passo, passo * 0.5))   # barra = 1 entrelinha (bordas sobre fios)
                    y += passo * 3
                    if r.random() < 0.12:
                        y += passo * 3
            # barras SÓLIDAS (cor já misturada com o fundo): o fio de base não atravessa a barra ("riscado")
            fundo_ = f.papel if fundo_claro else f.fundo
            sobre_col = _mistura(fundo_, cor, 0.05)
            corpo += f'<path d="{"".join(bars)}" fill="{_mistura(sobre_col, cor, 0.32)}"/>'
    if estilo == "faixas":
        # altura-x = 2 linhas de base (16 px): bordas da faixa exatamente sobre fios (antes 17,6 px = "quase")
        bs = "".join(f'<rect x="{m}" y="{y - passo * 2:.1f}" width="{w - 2 * m}" height="{passo * 2:.1f}"/>'
                     for k, y in enumerate(ys) if k % 4 == 3)
        corpo += f'<g fill="{cor}" fill-opacity="0.07">{bs}</g>'
    nomes = {"linhas": "linha de base 8 px", "fina": "linha de base 4 + 8 px", "numerada": "linha de base numerada (y)",
             "colunas": "linha de base + 2 colunas", "esquema": "linha de base + texto esquemático",
             "faixas": "linha de base + faixas de altura-x"}
    el = _campo(w, h, corpo, nomes[estilo], f"corpos e entrelinhas múltiplos de {passo}; a entrelinha com acento é medida na "
                "tinta; " + NOTA, fam=FAM, fundo_claro=fundo_claro)
    el.css = (f".base{{background:repeating-linear-gradient(to bottom,transparent 0 {passo - 1}px,"
              f"rgba(255,255,255,.12) {passo - 1}px {passo}px)}}")
    return el


# ================================================================ 3. colunas de site
def colunas_site(f, tela="desktop", estilo="campos", cor=None, fundo_claro=False):
    """Layout grid de site. tela: desktop (1440, container 1320, 12 col, gutter 24) · tablet (768, 8 col, margem 32) ·
    mobile (390, 4 col, margem 16). estilo: campos (colunas a 8%) · contorno · gutters (só os vãos) · numerada."""
    W, H, n, cont, g = {"desktop": (1440, 900, 12, 1320, 24), "tablet": (768, 1024, 8, 704, 24),
                        "mobile": (390, 844, 4, 358, 16)}[tela]
    cor = cor or f.acento
    m = (W - cont) / 2
    cw = (cont - (n - 1) * g) / n
    xs = [m + i * (cw + g) for i in range(n)]
    corpo = ""
    if estilo in ("campos", "numerada"):
        corpo += f'<g fill="{cor}" fill-opacity="0.12">' + "".join(
            f'<rect x="{x:.2f}" y="0" width="{cw:.2f}" height="{H}"/>' for x in xs) + "</g>"
    if estilo == "contorno":
        # contorno inteiro dentro da caixa (a borda de cima/baixo em y=0/H perdia metade da espessura)
        ec = max(1.2, f.traco * 0.4)
        corpo += f'<g {traco_attr(cor, ec, 0.7)}>' + "".join(
            f'<rect x="{x:.2f}" y="{ec / 2:.2f}" width="{cw:.2f}" height="{H - ec:.2f}"/>' for x in xs) + "</g>"
    if estilo == "gutters":
        corpo += f'<g fill="{cor}" fill-opacity="0.22">' + "".join(
            f'<rect x="{x + cw:.2f}" y="0" width="{g}" height="{H}"/>' for x in xs[:-1]) + "</g>"
        corpo += _ln([[(m, 0), (m, H)], [(W - m, 0), (W - m, H)]], cor, 1.5, 0.8)
    if estilo == "numerada":
        for i, x in enumerate(xs):
            corpo += _mono(f, f"{i + 1:02d}", 16 if tela != "mobile" else 14, x + cw / 2, 36, cor, "middle")
    nomes = {"campos": "colunas a 12%", "contorno": "colunas em contorno", "gutters": "só os vãos (gutters)",
             "numerada": "colunas numeradas"}
    el = _campo(W, H, corpo, f"site · {tela} · {n} col · {nomes[estilo]}",
                f"container {cont}, gutter {g}, coluna {cw:.1f} px; foto em 5–6 col, título em 6–7 (landing)",
                fam=FAM, fundo_claro=fundo_claro)
    el.css = (f".container{{max-width:{cont}px;margin-inline:auto;display:grid;grid-template-columns:repeat({n},1fr);"
              f"column-gap:{g}px}}")
    return el


# ================================================================ 4. isométrica
def isometrica(f, estilo="linhas", w=1080, h=1080, passo=None, cor=None, fundo_claro=False):
    """Grade isométrica (30°/150°/90°). estilo: linhas · pontos · triangular (0/60/120) · hexagonal · cubo (1 cubo
    no acento) · degraus (escada de cubos)."""
    cor = cor or f.tinta
    p = passo or f.unidade * 2
    e = _esp(f, 0.45)
    L = math.hypot(w, h)
    corpo = ""

    def familia(ang, desloc):
        a = math.radians(ang)
        out = []
        for s in np.arange(-L, L, desloc):
            cx, cy = w / 2 - s * math.sin(a), h / 2 + s * math.cos(a)
            out.append([(cx - L * math.cos(a), cy - L * math.sin(a)), (cx + L * math.cos(a), cy + L * math.sin(a))])
        return out
    dx = p * math.cos(math.radians(30))
    if estilo in ("linhas", "cubo", "degraus"):
        corpo += _ln(familia(30, p * math.cos(math.radians(30))) + familia(150, p * math.cos(math.radians(30))) +
                     familia(90, dx), cor, e, 0.5)
    elif estilo == "triangular":
        corpo += _ln(familia(0, p * 0.866) + familia(60, p * 0.866) + familia(120, p * 0.866), cor, e, 0.5)
    elif estilo == "pontos":
        # só pontos inteiros, rede centrada com margem (antes: pontos cortados ao meio na borda esquerda/superior)
        mg = 24
        nx = int((w - 2 * mg) / dx) + 1
        ny = int((h - 2 * mg - p / 2) / p) + 1
        x0 = (w - (nx - 1) * dx) / 2
        y0 = (h - ((ny - 1) * p + p / 2)) / 2
        pts = [(x0 + i * dx, y0 + j * p + (i % 2) * p / 2) for i in range(nx) for j in range(ny)]
        corpo += (f'<path d="{pontos_d(pts)}" fill="none" stroke="{cor}" stroke-width="{max(3.0, f.traco * 1.2):.1f}" '
                  f'stroke-linecap="round" stroke-opacity="0.7"/>')
    elif estilo == "hexagonal":
        # favo de hexágonos INTEIROS, centrado com margem (antes: hexágonos fatiados ao meio em todas as bordas)
        R = p * 0.75
        mg = 72
        nc = int((w - 2 * mg - 2 * R) / (1.5 * R)) + 1
        nl = int((h - 2 * mg - R * 0.866) / (R * 1.732))
        larg = 2 * R + (nc - 1) * 1.5 * R
        alt = nl * R * 1.732 + R * 0.866
        ox, oy = (w - larg) / 2 + R, (h - alt) / 2 + R * 0.866
        hx = []
        for i in range(nc):
            for j in range(nl):
                cx = ox + i * 1.5 * R
                cy = oy + j * R * 1.732 + (i % 2) * R * 0.866
                hx.append([(cx + R * math.cos(math.radians(60 * k)), cy + R * math.sin(math.radians(60 * k))) for k in range(7)])
        corpo += _ln(hx, cor, e, 0.5)
    if estilo in ("cubo", "degraus"):
        fundo_ = f.papel if fundo_claro else f.fundo
        # faces SÓLIDAS (3 tons do acento sobre o fundo): o fio e as faces vizinhas não aparecem através do cubo
        tons = (_mistura(fundo_, f.acento, 0.95), _mistura(fundo_, f.acento, 0.62), _mistura(fundo_, f.acento, 0.36))

        def cubo(ox, oy, s):
            v = lambda a: (math.cos(math.radians(a)) * s, math.sin(math.radians(a)) * s)  # noqa: E731
            top = [(ox, oy), (ox + v(-30)[0], oy + v(-30)[1]), (ox, oy - s), (ox + v(-150)[0], oy + v(-150)[1])]
            esq = [(ox, oy), (ox + v(-150)[0], oy + v(-150)[1]), (ox + v(-150)[0], oy + v(-150)[1] + s), (ox, oy + s)]
            dir_ = [(ox, oy), (ox + v(-30)[0], oy + v(-30)[1]), (ox + v(-30)[0], oy + v(-30)[1] + s), (ox, oy + s)]
            return (_cheio([top], tons[0]) + _cheio([esq], tons[1]) + _cheio([dir_], tons[2]))
        s = p * 2
        if estilo == "cubo":
            corpo += cubo(w / 2, h / 2, s)
        else:                         # escada: colunas de cubos, desenhadas de trás para a frente
            bx, by = w * 0.3, h * 0.72
            for k in range(3, -1, -1):
                for z in range(k + 1):
                    corpo += cubo(bx + k * s * 0.866, by - k * s * 0.5 - z * s, s)
    nomes = {"linhas": "grade isométrica", "pontos": "grade isométrica de pontos", "triangular": "grade triangular",
             "hexagonal": "grade hexagonal", "cubo": "isométrica + 1 cubo no acento", "degraus": "isométrica + degraus"}
    return _campo(w, h, corpo, nomes[estilo], f"passo {p:g}px; diagrama/produto em 3D plano; " + NOTA, clip=_ret(w, h),
                  fam=FAM, fundo_claro=fundo_claro)


# ================================================================ 5. polar
def polar(f, estilo="completa", w=1080, h=1080, cor=None, fundo_claro=False):
    """Grade polar. estilo: completa (anéis + raios a 15°) · semi (meio círculo da base) · graduada (escala de 360° com
    números a cada 30°) · pontos · log (anéis em progressão) · setor (1 setor no acento) · alvo."""
    cor = cor or f.tinta
    e = _esp(f, 0.45)
    # meia: a linha de base (180°/360°) fica 1,5 px acima da borda para não perder metade da espessura
    cx, cy = w / 2, (h - 1.5 if estilo == "semi" else h / 2)
    R = (min(w, h) * 0.46) if estilo != "semi" else w * 0.47
    corpo = ""
    aneis = np.geomspace(R * 0.06, R, 9) if estilo == "log" else np.linspace(R / 8, R, 8)
    a0, a1 = (180, 360) if estilo == "semi" else (0, 360)
    if estilo != "pontos":
        cs = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}"/>' for r in aneis)
        corpo += f'<g {traco_attr(cor, e, 0.55)}>{cs}</g>'
        passo_a = 15 if estilo != "graduada" else 30
        # graduada: os raios param no anel de dentro da faixa dos números (o raio atravessava o "30", o "60"…)
        r_fim = aneis[-2] if estilo == "graduada" else R
        rs = [[(cx + aneis[0] * math.cos(math.radians(a)), cy + aneis[0] * math.sin(math.radians(a))),
               (cx + r_fim * math.cos(math.radians(a)), cy + r_fim * math.sin(math.radians(a)))]
              for a in range(a0, a1 + (1 if estilo == "semi" else 0), passo_a)]
        corpo += _ln(rs, cor, e, 0.4)
    else:
        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for r in aneis for a in range(0, 360, 10)]
        corpo += (f'<path d="{pontos_d(pts)}" fill="none" stroke="{cor}" stroke-width="{max(3.0, f.traco * 1.2):.1f}" '
                  f'stroke-linecap="round"/>')
    if estilo == "graduada":
        tk = []
        for a in range(0, 360):
            L = 16 if a % 10 == 0 else (10 if a % 5 == 0 else 5)
            ca, sa = math.cos(math.radians(a - 90)), math.sin(math.radians(a - 90))
            tk.append([(cx + R * ca, cy + R * sa), (cx + (R - L) * ca, cy + (R - L) * sa)])
        corpo += _ln(tk, cor, e, 0.9)
        for a in range(0, 360, 30):
            ca, sa = math.cos(math.radians(a - 90)), math.sin(math.radians(a - 90))
            corpo += _mono(f, f"{a}", 18, cx + (R - 31) * ca, cy + (R - 31) * sa + 6.5, f.apoio, "middle")
    if estilo == "setor":
        a_, b_ = math.radians(-60), math.radians(-30)
        poly = [(cx, cy)] + [(cx + R * math.cos(t), cy + R * math.sin(t)) for t in np.linspace(a_, b_, 30)]
        corpo = _cheio([poly], f.acento, 0.85) + corpo
    if estilo == "alvo":
        corpo += f'<circle cx="{cx}" cy="{cy}" r="{aneis[0]:.1f}" fill="{f.acento}"/>'
    nomes = {"completa": "grade polar (15°)", "semi": "grade polar · meia", "graduada": "grade polar graduada (360°)",
             "pontos": "grade polar de pontos", "log": "grade polar · anéis em progressão", "setor": "grade polar · setor no acento",
             "alvo": "grade polar · alvo"}
    return _campo(w, h, corpo, nomes[estilo], "radar/ciclo/alcance; graduação só se MEDIR algo real; " + NOTA,
                  clip=_ret(w, h), fam=FAM, fundo_claro=fundo_claro)


# ================================================================ 6. marcas de corte e sangria
def corte_sangria(f, estilo="corte", W=1080, H=1350, sangria=36, folga=96, cor=None, fundo_claro=False):
    """Marcas de impressão em volta de uma página W×H: corte, sangria (tracejada), área de segurança, registro,
    dobra (folder 3 painéis) e imposição (cartões 2×4). Tudo fora da página real, como na gráfica."""
    cor = cor or f.tinta
    e = max(1.2, f.traco * 0.4)
    s = folga
    w, h = W + 2 * s, H + 2 * s
    corpo = ""
    tr = f' stroke-dasharray="10 7"'

    def marcas(x0, y0, x1, y1, comp=26, gap=10):
        ls = []
        for (x, sx) in ((x0, -1), (x1, 1)):
            for (y, sy) in ((y0, -1), (y1, 1)):
                ls.append([(x + sx * gap, y), (x + sx * (gap + comp), y)])
                ls.append([(x, y + sy * gap), (x, y + sy * (gap + comp))])
        return ls
    if estilo == "imposicao":
        cols, rows = 2, 4
        cw, ch = (W - 24) / cols, (H - 72) / rows
        ls = []
        for i in range(cols):
            for j in range(rows):
                x0, y0 = s + 12 + i * cw, s + 36 + j * ch
                corpo += f'<rect x="{x0 + 6:.1f}" y="{y0 + 6:.1f}" width="{cw - 12:.1f}" height="{ch - 12:.1f}" fill="{cor}" fill-opacity="0.06"/>'
        for x in [s + 12 + i * cw for i in range(cols + 1)]:
            ls += [[(x, s - 40), (x, s - 8)], [(x, s + H + 8), (x, s + H + 40)]]
        for y in [s + 36 + j * ch for j in range(rows + 1)]:
            ls += [[(s - 40, y), (s - 8, y)], [(s + W + 8, y), (s + W + 40, y)]]
        corpo += _ln(ls, cor, e)
    else:
        corpo += f'<rect x="{s}" y="{s}" width="{W}" height="{H}" fill="{cor}" fill-opacity="0.05"/>'
        corpo += _ln(marcas(s, s, s + W, s + H, 28, sangria * 0.3 + 6), cor, e)
        if estilo in ("sangria", "seguranca", "registro", "dobra"):
            corpo += (f'<rect x="{s - sangria * 0.3:.1f}" y="{s - sangria * 0.3:.1f}" width="{W + sangria * 0.6:.1f}" '
                      f'height="{H + sangria * 0.6:.1f}" {traco_attr(f.acento, e, 0.9, extra=tr)}/>')
        if estilo in ("seguranca", "registro"):
            corpo += (f'<rect x="{s + 60}" y="{s + 60}" width="{W - 120}" height="{H - 120}" '
                      f'{traco_attr(cor, e, 0.45, extra=tr)}/>')
        if estilo == "registro":
            for x, y in ((s + W / 2, s / 2 - 4), (s + W / 2, s + H + s / 2 + 4), (s / 2 - 4, s + H / 2), (s + W + s / 2 + 4, s + H / 2)):
                corpo += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" {traco_attr(cor, e)}/>'
                          f'<path d="{_cruz(x, y, 19)}" {traco_attr(cor, e)}/>')
        if estilo == "dobra":
            g_, c_ = sangria * 0.3 + 6, 28      # mesmas distâncias das marcas de corte (não encostam na sangria)
            for x in (s + W / 3, s + 2 * W / 3):
                corpo += _ln([[(x, s - g_ - c_), (x, s - g_)], [(x, s + H + g_), (x, s + H + g_ + c_)]], cor, e)
                corpo += _ln([[(x, s), (x, s + H)]], cor, e, 0.35, extra=' stroke-dasharray="3 6"')
    nomes = {"corte": "marcas de corte", "sangria": "corte + sangria", "seguranca": "corte + sangria + segurança",
             "registro": "corte + registro", "dobra": "marcas de dobra (3 painéis)", "imposicao": "imposição 2×4 (cartões)"}
    return _campo(w, h, corpo, nomes[estilo], "só onde há MEDIDA/impressão (dossiê, prova, ingresso), nunca em todo "
                  "cartão; " + NOTA, fam=FAM, fundo_claro=fundo_claro)


# ================================================================ 7. papel milimetrado
def milimetrado(f, estilo="mm", w=1080, h=1080, mm=6.0, cor=None, fundo_claro=False):
    """Papel milimetrado (1 mm = `mm` px): fio de 1 mm, médio a 5, forte a 10. estilo: mm · quadriculado (5 mm) ·
    pontos · semilog (y em décadas) · acento (grade de engenharia na cor de acento)."""
    cor = cor or (f.acento if estilo == "acento" else f.tinta)
    e = max(1.0, f.traco * 0.3)
    xs = np.arange(0, w + 0.1, mm)
    ys = np.arange(0, h + 0.1, mm)
    corpo = ""
    if estilo in ("mm", "acento"):
        fino = [[(x, 0), (x, h)] for i, x in enumerate(xs) if i % 5] + [[(0, y), (w, y)] for i, y in enumerate(ys) if i % 5]
        med = [[(x, 0), (x, h)] for i, x in enumerate(xs) if i % 5 == 0 and i % 10] + \
              [[(0, y), (w, y)] for i, y in enumerate(ys) if i % 5 == 0 and i % 10]
        forte = [[(x, 0), (x, h)] for i, x in enumerate(xs) if i % 10 == 0] + [[(0, y), (w, y)] for i, y in enumerate(ys) if i % 10 == 0]
        corpo = _ln(fino, cor, e, 0.18) + _ln(med, cor, e, 0.38) + _ln(forte, cor, e * 1.6, 0.6)
    elif estilo == "quadriculado":
        q = mm * 5
        corpo = _ln([[(x, 0), (x, h)] for x in np.arange(0, w + 0.1, q)] + [[(0, y), (w, y)] for y in np.arange(0, h + 0.1, q)],
                    cor, e, 0.4)
    elif estilo == "pontos":
        pts = [(x, y) for x in np.arange(mm * 5, w, mm * 5) for y in np.arange(mm * 5, h, mm * 5)]
        corpo = (f'<path d="{pontos_d(pts)}" fill="none" stroke="{cor}" stroke-width="3" stroke-linecap="round" '
                 f'stroke-opacity="0.6"/>')
        cr = [(x, y) for x in np.arange(mm * 50, w, mm * 50) for y in np.arange(mm * 50, h, mm * 50)]
        corpo += f'<path d="{"".join(_cruz(x, y, 7) for x, y in cr)}" {traco_attr(cor, e * 1.4, 0.8)}/>'
    elif estilo == "semilog":
        # 3 décadas COMPLETAS (1→1000) dentro de uma margem de 5 mm: as 4 linhas-mestras (1, 10, 100, 1000) existem
        # e nenhuma fica na borda cortada (antes faltava a de cima e a de baixo perdia metade).
        dec, mg = 3, mm * 5
        hd = (h - 2 * mg) / dec
        hs = []
        for d in range(dec):
            for k in range(1, 10):
                y = h - mg - (d + math.log10(k)) * hd
                hs.append(([(mg, y), (w - mg, y)], 0.6 if k == 1 else 0.2))
        hs.append(([(mg, mg), (w - mg, mg)], 0.6))
        corpo = "".join(_ln([ln], cor, e * (1.6 if op > 0.5 else 1), op) for ln, op in hs)
        xs_ = np.arange(mg, w - mg + 0.1, mm * 5)
        corpo += _ln([[(x, mg), (x, h - mg)] for x in xs_], cor, e, 0.25)
    nomes = {"mm": "papel milimetrado (1/5/10 mm)", "quadriculado": "quadriculado 5 mm", "pontos": "pontos a 5 mm + cruzes a 50",
             "semilog": "papel semilog (3 décadas)", "acento": "milimetrado de engenharia (acento)"}
    return _campo(w, h, corpo, nomes[estilo], f"1 mm = {mm:g} px; medida/precisão (só a grade — nunca traçado fake); "
                  + NOTA, fam=FAM, fundo_claro=fundo_claro)


# ================================================================ 8. pontos de registro
def registro(f, estilo="cruzes", w=1080, h=1350, cor=None, fundo_claro=False):
    """Grade de pontos de registro nas interseções do grid (feed 6×8). estilo: cruzes (+ de 10 px a 25%) · miras
    (círculo + cruz nos 4 cantos) · cantoneiras (L em cada módulo) · pontos · cruzes_coord (com A1…) · acento
    (1 mira no acento marcando o foco)."""
    cor = cor or f.tinta
    e = max(1.2, f.traco * 0.5)
    xs, ys, cw, rh, (x0, y0, x1, y1) = _modulos(w, h, 6, 8, 72, f.unidade)
    nos_x, nos_y = _nos(xs, ys, cw, rh, f.unidade, (x0, y0, x1, y1))
    corpo = ""
    foco = (nos_x[4], nos_y[2])
    if estilo in ("cruzes", "cruzes_coord", "acento"):
        corpo += (f'<path d="{"".join(_cruz(x, y, 6) for x in nos_x for y in nos_y if not (estilo == "acento" and (x, y) == foco))}" '
                  f'{traco_attr(cor, e, 0.6)}/>')
    if estilo == "cruzes_coord":
        for i, x in enumerate(xs):
            corpo += _mono(f, LETRAS[i], 18, x + cw / 2, y0 - 24, f.apoio, "middle")
        for j, y in enumerate(ys):
            corpo += _mono(f, f"{j + 1:02d}", 18, x0 - 18, y + rh / 2 + 6.5, f.apoio, "end")
    if estilo == "pontos":
        pts = [(x, y) for x in nos_x for y in nos_y]
        corpo += (f'<path d="{pontos_d(pts)}" fill="none" stroke="{cor}" stroke-width="4" stroke-linecap="round" '
                  f'stroke-opacity="0.55"/>')
    if estilo == "cantoneiras":
        a = 10
        d = ""
        for x in xs:
            for y in ys:
                d += (f"M{x:.1f} {y + a:.1f}V{y:.1f}H{x + a:.1f}M{x + cw - a:.1f} {y:.1f}H{x + cw:.1f}V{y + a:.1f}"
                      f"M{x + cw:.1f} {y + rh - a:.1f}V{y + rh:.1f}H{x + cw - a:.1f}M{x + a:.1f} {y + rh:.1f}H{x:.1f}V{y + rh - a:.1f}")
        corpo += f'<path d="{d}" {traco_attr(cor, e, 0.5, cap="square")}/>'
    if estilo in ("miras", "acento"):
        alvos = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)] if estilo == "miras" else [foco]
        for x, y in alvos:
            c_ = f.acento if estilo == "acento" else cor
            corpo += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" {traco_attr(c_, e * 1.3)}/>'
                      f'<path d="{_cruz(x, y, 22)}" {traco_attr(c_, e * 1.3)}/>')
    nomes = {"cruzes": "registro · cruzes nas interseções", "miras": "registro · miras nos cantos",
             "cantoneiras": "registro · cantoneiras por módulo", "pontos": "registro · pontos nas interseções",
             "cruzes_coord": "registro · cruzes + coordenadas", "acento": "registro · 1 mira no acento"}
    return _campo(w, h, corpo, nomes[estilo], "cruzes 8–12 px a 15–25%; marca o grid sem desenhá-lo; " + NOTA,
                  fam=FAM, fundo_claro=fundo_claro)


# ================================================================ amostras
@amostra(FAM, "grade modular")
def _a_mod(f):
    return [modular(f), modular(f, "feed", "campos"), modular(f, "feed", "cruzes"), modular(f, "feed", "coordenadas"),
            modular(f, "quadrado", "destaque", cor=f.apoio), modular(f, "story", "zonas", cor=f.apoio),
            modular(f, "paisagem", "linhas", cor=f.apoio), modular(f, "feed", "coordenadas", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "linha de base")
def _a_base(f):
    return [baseline(f), baseline(f, "numerada"), baseline(f, "colunas"), baseline(f, "esquema"),
            baseline(f, "faixas"), baseline(f, "esquema", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "colunas de site")
def _a_site(f):
    return [colunas_site(f), colunas_site(f, estilo="numerada"), colunas_site(f, estilo="contorno", cor=f.tinta),
            colunas_site(f, estilo="gutters"), colunas_site(f, "tablet"), colunas_site(f, "mobile", "numerada"),
            colunas_site(f, "desktop", "campos", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "isométrica")
def _a_iso(f):
    return [isometrica(f), isometrica(f, "pontos"), isometrica(f, "triangular", cor=f.apoio), isometrica(f, "hexagonal"),
            isometrica(f, "cubo", cor=f.apoio), isometrica(f, "degraus", cor=f.apoio),
            isometrica(f, "linhas", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "polar")
def _a_polar(f):
    return [polar(f), polar(f, "semi", w=1080, h=560), polar(f, "graduada"), polar(f, "pontos"), polar(f, "log", cor=f.apoio),
            polar(f, "setor"), polar(f, "alvo", cor=f.apoio), polar(f, "graduada", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "corte e sangria")
def _a_corte(f):
    return [corte_sangria(f), corte_sangria(f, "sangria"), corte_sangria(f, "seguranca"), corte_sangria(f, "registro"),
            corte_sangria(f, "dobra", W=1350, H=900), corte_sangria(f, "imposicao"),
            corte_sangria(f, "registro", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "milimetrado")
def _a_mm(f):
    return [milimetrado(f), milimetrado(f, "quadriculado", cor=f.apoio), milimetrado(f, "pontos"), milimetrado(f, "semilog"),
            milimetrado(f, "acento"), milimetrado(f, "mm", cor=f.fundo, fundo_claro=True),
            milimetrado(f, "acento", cor=f.acento, fundo_claro=True)]


@amostra(FAM, "pontos de registro")
def _a_reg(f):
    return [registro(f), registro(f, "miras"), registro(f, "cantoneiras"), registro(f, "cruzes_coord"),
            registro(f, "acento"), registro(f, "cantoneiras", cor=f.fundo, fundo_claro=True)]
