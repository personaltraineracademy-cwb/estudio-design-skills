"""ornamentos.selos — família SELOS E CARIMBOS (dizer status, data, condição; carimbar).

Origem (references/elementos.md "Sigilo/documento", "10 regras" n.º 8; pesquisa 11 E06, E31, E32; 4 §carimbo):
  - selo circular: texto em curvas no arco (espaçamento óptico), separadores DESENHADOS, vão = assinatura;
  - estrela/explosão: selo 16–32 pontas com razão 0,82–0,90; explosão 8–14 pontas, razão 0,40–0,60, pontas
    irregulares por semente; 1 por peça, com função (status, condição), texto reto dentro;
  - carimbo DA MARCA: moldura dupla, tinta falhada (filtro sRGB), inclinado no ângulo da ficha; nada de brasão,
    órgão oficial ou "100% garantido";
  - tampinha: 21 dentes (a tampa coroa real tem 21) — detalhe fiel ao objeto.
Textos só do cliente (AO VIVO · 20H30 · 3 NOITES · NOITE 1 · PÓS-GRADUAÇÃO): nada de preço/oferta/"reservado até"
inventados e nenhuma explosão de varejo (oferta e explosões não viram selo).
"""
import math

from .nucleo import amostra, elemento, filtro
from .formas import (rotulo, larg_rotulo, mistura, claro, no_claro, corpo, caixa_texto, circulo_d, p_cantos, uid,
                     path_texto)
from .nucleo import _font

FAM = "selos"


# =====================================================================================================================
# utilitários
# =====================================================================================================================
def arco_texto(f, s, cx, cy, r_meio, capx, fill, pos="topo", spec=None, tracking=0.14):
    """Texto em curvas no arco, com a MAIÚSCULA centrada no raio r_meio. pos: topo (lê em cima) · base (lê embaixo)."""
    spec = spec or f.fonte_texto
    sz = corpo(spec, capx)
    F = _font(spec)
    if pos == "topo":
        d = F.path_on_circle(s, sz, cx, cy, r_meio - capx / 2, -90, tracking, True, True)
    else:
        d = F.path_on_circle(s, sz, cx, cy, r_meio + capx / 2, 90, tracking, False, True)
    return f'<path d="{d}" fill="{fill}"/>'


def _fundo_claro(f):
    h = f.fundo.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5


def varredura(f, s, r, capx, spec=None, tracking=0.14):
    """Ângulo (graus) que o texto ocupa no arco de raio r."""
    spec = spec or f.fonte_texto
    return math.degrees(larg_rotulo(f, s, capx, spec, tracking) / r)


def arco_caber(f, s, r, capx, spec=None, tracking=0.14, max_deg=135.0, min_cap=19.0, min_tr=0.04):
    """(capx, tracking) em que o texto ocupa <= max_deg no arco de raio r (D21: arco > ~150° encosta no separador).
    Primeiro aperta o espaçamento (até min_tr), depois reduz o corpo (até min_cap)."""
    cap_, tr = capx, tracking
    for _ in range(80):
        if varredura(f, s, r, cap_, spec, tr) <= max_deg:
            break
        if tr > min_tr + 1e-9:
            tr = max(min_tr, tr - 0.02)
        elif cap_ > min_cap:
            cap_ -= 1.0
        else:
            break
    return cap_, tr


def anel_ajustado(f, unidade, R_base, capxs=(24, 23, 22, 21, 20, 19, 18), reps=(1, 2, 3, 4, 5, 6), alvo=0.11,
                  faixa=(0.05, 0.20), spec=None):
    """Escolhe (capx, repetições, tracking) para fechar o anel de 360° SEM letra solta (D20): tracking entre 0,05 e
    0,20 em, preferindo o maior corpo. rb = raio da linha de base = R_base - capx."""
    spec = spec or f.fonte_texto
    F = _font(spec)
    melhor = None
    for capx in capxs:
        sz = corpo(spec, capx)
        C = 2 * math.pi * (R_base - capx)
        for rep in reps:
            txt = unidade * rep
            w0 = F.width(txt, sz, 0)
            tr = (C - w0) / (len(txt) * sz)
            if faixa[0] <= tr <= faixa[1]:
                return capx, rep, tr
            d = abs(tr - alvo)
            if melhor is None or d < melhor[0]:
                melhor = (d, capx, rep, tr)
    return melhor[1], melhor[2], melhor[3]


def anel_texto(f, s, cx, cy, r_meio, capx, fill, spec=None):
    """Texto CONTÍNUO em 360°: o espaçamento é calculado para fechar o anel sem emenda."""
    spec = spec or f.fonte_texto
    sz = corpo(spec, capx)
    F = _font(spec)
    rb = r_meio - capx / 2
    C = 2 * math.pi * rb
    w0 = F.width(s, sz, 0)
    tr = (C - w0) / (len(s) * sz)
    d = F.path_on_circle(s, sz, cx, cy, rb, -90, tr, True, False)
    return f'<path d="{d}" fill="{fill}"/>', tr


def centro_tinta(spec, s, size, cx, cy, fill, tracking=0.0):
    """Texto centrado pela TINTA (não pela caixa) em (cx, cy)."""
    x0, y0, x1, y1 = caixa_texto(spec, s, size, 0, 0, tracking)
    d, _ = path_texto(spec, s, size, 0, 0, tracking)
    return f'<path transform="translate({cx - (x0 + x1) / 2:.2f} {cy - (y0 + y1) / 2:.2f})" d="{d}" fill="{fill}"/>'


def poligono_redondo(pts, raio):
    """Polígono com cantos amaciados (Bézier quadrática no vértice)."""
    n = len(pts)
    d = ""
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        k1, k2 = min(raio, l1 / 2) / l1, min(raio, l2 / 2) / l2
        a = (p1[0] + v1[0] * k1, p1[1] + v1[1] * k1)
        b = (p1[0] + v2[0] * k2, p1[1] + v2[1] * k2)
        d += ("M" if i == 0 else "L") + f"{a[0]:.2f} {a[1]:.2f}Q{p1[0]:.2f} {p1[1]:.2f} {b[0]:.2f} {b[1]:.2f}"
    return d + "Z"


def pontos_estrela(cx, cy, n, R, razao, rnd=None, jitter=0.0, rot=-90.0):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180.0 / n)
        rr = R if i % 2 == 0 else R * razao
        if rnd is not None and i % 2 == 0 and jitter:
            rr *= 1 - jitter * rnd.random()
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def _poli(pts):
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"


def _ponto(cx, cy, r, fill):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}"/>'


def _losango(cx, cy, r, fill):
    return f'<path d="M{cx:.2f} {cy - r:.2f}L{cx + r:.2f} {cy:.2f}L{cx:.2f} {cy + r:.2f}L{cx - r:.2f} {cy:.2f}Z" fill="{fill}"/>'


def tinta_leve(id_, seed):
    """Tinta de carimbo para ÁREA CHEIA grande (tarja): só borda levemente áspera + furinhos raros e finos.
    O filtro `tinta_carimbo` em área cheia vira mancha de sujeira (D19)."""
    return filtro(id_, (
        f'<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="{seed}" result="fino"/>'
        f'<feColorMatrix in="fino" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -14 0 0 0 10.9" result="masc"/>'
        f'<feDisplacementMap in="SourceGraphic" in2="fino" scale="1.4" xChannelSelector="R" yChannelSelector="G" result="aspero"/>'
        f'<feComposite in="aspero" in2="masc" operator="in"/>'))


def tinta_carimbo(id_, seed, forca=1.0):
    """Filtro de tinta de carimbo: falhas finas + pressão irregular + borda levemente áspera (sRGB, região ampliada)."""
    return filtro(id_, (
        f'<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed}" result="fino"/>'
        f'<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{seed + 3}" result="largo"/>'
        f'<feComposite in="fino" in2="largo" operator="arithmetic" k1="0" k2="0.62" k3="0.55" k4="0" result="mix"/>'
        f'<feColorMatrix in="mix" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -10 0 0 0 {10 * (0.72 + 0.08 * (1 - forca)):.2f}" result="masc"/>'
        f'<feDisplacementMap in="SourceGraphic" in2="fino" scale="1.6" xChannelSelector="R" yChannelSelector="G" result="aspero"/>'
        f'<feComposite in="aspero" in2="masc" operator="in"/>'))


def _caixa_girada(w, h, ang, m=0.0):
    a = math.radians(abs(ang))
    return w * math.cos(a) + h * math.sin(a) + 2 * m, w * math.sin(a) + h * math.cos(a) + 2 * m


# =====================================================================================================================
# selo circular
# =====================================================================================================================
def selo_circular(f, topo="AO VIVO", base="20H30", centro="3", sub="NOITES", estilo="contorno", R=170.0,
                  sep="ponto", nome=None):
    """Selo circular: aro duplo, texto em cima e embaixo no arco, separadores desenhados, centro em display."""
    t = f.traco
    m = t
    cx = cy = R + m
    band = 54.0
    capx = 24.0            # maiúscula do arco (antes 22; D-R4b: rótulo lido >= 24–25 px)
    if estilo == "cheio":
        bg, fg, acc = f.acento, f.sobre_acento, f.sobre_acento
    elif estilo == "tinta":
        bg, fg, acc = f.tinta, f.fundo, f.fundo
    else:
        bg, fg, acc = None, f.tinta, f.acento
    s = ""
    if bg:
        s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{R:.2f}" fill="{bg}"/>'
        s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{R - 8:.2f}" fill="none" stroke="{fg}" stroke-width="{t * 0.67:.2f}"/>'
    else:
        s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{R - t / 2:.2f}" fill="none" stroke="{fg}" stroke-width="{t:.2f}"/>'
    rin = R - 8 - band
    s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rin:.2f}" fill="none" stroke="{fg}" stroke-width="{t * 0.67:.2f}"/>'
    rm = (R - 8 + rin) / 2
    # cada texto do arco ocupa no máximo 135° (D21): o separador fica no meio do vão, nunca colado na letra
    ct, tt = arco_caber(f, topo, rm, capx, f.fonte_texto, 0.14)
    cb, tb = arco_caber(f, base, rm, capx, f.fonte_mono, 0.10)
    s += arco_texto(f, topo, cx, cy, rm, ct, fg, "topo", tracking=tt)
    s += arco_texto(f, base, cx, cy, rm, cb, fg, "base", f.fonte_mono, tb)
    for a in (180, 0):
        px, py = cx + rm * math.cos(math.radians(a)), cy + rm * math.sin(math.radians(a))
        s += _ponto(px, py, 4.5, acc) if sep == "ponto" else _losango(px, py, 7, acc)
    if centro:
        capc = rin * 0.78 if not sub else rin * 0.62
        spec = f.fonte_display
        larg1 = larg_rotulo(f, centro, 1.0, spec, 0.0)
        capc = min(capc, 1.45 * rin / max(larg1, 1e-6))        # o centro cabe dentro do aro (ex.: "AO VIVO" inteiro)
        sz = corpo(spec, capc)
        dy = -rin * 0.12 if sub else 0
        # acento sobre PAPEL dá ~2:1 (D11): em fundo claro o centro vai na cor da tinta
        cor_c = fg if (bg or _fundo_claro(f)) else acc
        s += centro_tinta(spec, centro, sz, cx, cy + dy, cor_c)
        if sub:
            s += centro_tinta(f.fonte_texto, sub, corpo(f.fonte_texto, 18), cx, cy + dy + capc / 2 + 26, fg, 0.14)
    W = 2 * (R + m)
    return elemento(W, W, s, nome or f"selo circular · {estilo}", FAM,
                    nota="texto no arco em curvas; separadores desenhados; centro na display")


def selo_giratorio(f, txt="AO VIVO • 20H30 • 3 NOITES • ", R=150.0, estilo="contorno", miolo="seta", nome=None):
    """Selo de texto contínuo (360°); miolo = seta, ponto ou número. A frase `txt` é repetida N vezes e o corpo
    escolhido para o espaçamento ficar entre 0,05 e 0,20 em (antes +0,43 em: letras soltas — D20)."""
    t = f.traco
    cx = cy = R + t
    s = ""
    fg = f.tinta if estilo == "contorno" else f.sobre_acento
    if estilo == "cheio":
        s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{R:.2f}" fill="{f.acento}"/>'
    capx, rep, _ = anel_ajustado(f, txt, R - 14)
    spec = f.fonte_texto
    sz = corpo(spec, capx)
    rb = R - 14 - capx                       # linha de base do texto (= r_meio - capx/2)
    F = _font(spec)
    full = txt * rep
    tr = (2 * math.pi * rb - F.width(full, sz, 0)) / (len(full) * sz)
    s += f'<path d="{F.path_on_circle(full, sz, cx, cy, rb, -90, tr, True, False)}" fill="{fg}"/>'
    rin = R - 8 - capx - 20
    if estilo == "contorno":
        s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rin:.2f}" fill="none" stroke="{f.tinta}" stroke-width="{t * 0.67:.2f}"/>'
    if miolo == "seta":
        from .formas import _seta_diag
        s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rin * 0.62:.2f}" fill="{f.acento if estilo == "contorno" else f.sobre_acento}"/>'
        s += _seta_diag(cx, cy, rin * 0.55, f.sobre_acento if estilo == "contorno" else f.acento, t * 2, limpa=True)
    elif miolo == "ponto":
        s += _ponto(cx, cy, rin * 0.3, f.acento if estilo == "contorno" else f.sobre_acento)
        for k, op in ((1, 0.5), (2, 0.22)):
            s += (f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rin * (0.3 + 0.2 * k):.2f}" fill="none" '
                  f'stroke="{f.acento if estilo == "contorno" else f.sobre_acento}" stroke-width="{t:.2f}" opacity="{op}"/>')
    else:
        s += centro_tinta(f.fonte_display, miolo, corpo(f.fonte_display, rin * 0.9), cx, cy, fg)
    W = 2 * (R + t)
    return elemento(W, W, s, nome or f"selo giratório · {estilo} · miolo {miolo}", FAM,
                    nota=f"texto em 360° com espaçamento fechado ({tr:+.3f} em); no site gira a 1 volta/20 s")


# =====================================================================================================================
# estrela / explosão / serrilhado / tampinha / roseta
# =====================================================================================================================
def estrela(f, pontas=24, razao=0.88, R=170.0, jitter=0.0, linhas=("AO VIVO",), estilo="cheio", arred=0.0,
            capx=None, nome=None, nota=""):
    """Estrela/explosão: `pontas` (8–32), `razao` raio interno/externo, `jitter` (0–0,3) pontas irregulares por semente,
    `arred` = amaciar os vértices (raio)."""
    t = f.traco
    m = t * 2
    cx = cy = R + m
    rnd = f.rnd("estrela", pontas, razao, jitter)
    pts = pontos_estrela(cx, cy, pontas, R, razao, rnd, jitter)
    if arred:
        # selo ONDULADO: curva senoidal contínua (n lóbulos iguais) — o polígono amaciado deixava lóbulos desiguais
        # e "derretidos" (revisão 10/2026)
        rm_ = R * (1 + razao) / 2
        am_ = R * (1 - razao) / 2
        q = [(cx + (rm_ + am_ * math.cos(pontas * th)) * math.cos(th - math.pi / 2),
              cy + (rm_ + am_ * math.cos(pontas * th)) * math.sin(th - math.pi / 2))
             for th in (2 * math.pi * i / (pontas * 24) for i in range(pontas * 24))]
        d = _poli(q)
    else:
        d = _poli(pts)
    if estilo == "cheio":
        s = f'<path d="{d}" fill="{f.acento}"/>'
        fg = f.sobre_acento
    elif estilo == "tinta":
        s = f'<path d="{d}" fill="{f.tinta}"/>'
        fg = f.fundo
    else:
        s = f'<path d="{d}" fill="none" stroke="{f.tinta}" stroke-width="{t:.2f}" stroke-linejoin="round"/>'
        fg = f.tinta
    if linhas:
        rin = R * razao * (1 - jitter) * math.cos(math.pi / pontas) ** 0.5
        spec = f.fonte_display
        if capx is None:
            larg1 = max(larg_rotulo(f, ln, 1.0, spec, 0.01) for ln in linhas)      # largura por 1 px de maiúscula
            n = len(linhas)
            capx = min(2 * rin * 0.72 / larg1, 2 * rin * 0.66 / (n + (n - 1) * 0.28), rin * 0.5)
        lh = capx * 1.28
        y0 = cy - lh * (len(linhas) - 1) / 2
        for k, ln in enumerate(linhas):
            s += centro_tinta(spec, ln, corpo(spec, capx), cx, y0 + k * lh, fg, 0.01)
    W = 2 * (R + m)
    return elemento(W, W, s, nome or f"estrela {pontas} pontas · razão {razao:g}", FAM, nota=nota)


def tampinha(f, R=160.0, centro="3", sub="NOITES", estilo="cheio", nome=None):
    """Tampa coroa: 21 dentes arredondados (a tampa real tem 21), saia sombreada e disco liso no meio."""
    t = f.traco
    cx = cy = R + t
    N, A = 21, R * 0.075
    pts = []
    M = N * 24
    for i in range(M):
        th = 2 * math.pi * i / M - math.pi / 2
        u = (1 - math.cos(N * th)) / 2
        rr = R - A * (u ** 0.85)
        pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    d = _poli(pts)
    cor = f.acento if estilo == "cheio" else f.tinta
    fg = f.sobre_acento if estilo == "cheio" else f.fundo
    s = f'<path d="{d}" fill="{cor}"/>'
    rd = R - A - 14
    s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rd + 5:.2f}" fill="none" stroke="{mistura(cor, f.fundo, 0.28)}" stroke-width="7"/>'
    s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rd - 4:.2f}" fill="none" stroke="{mistura(cor, f.tinta, 0.35)}" stroke-width="1.5"/>'
    capc = rd * 0.95
    s += centro_tinta(f.fonte_display, centro, corpo(f.fonte_display, capc), cx, cy - rd * 0.16, fg)
    s += centro_tinta(f.fonte_texto, sub, corpo(f.fonte_texto, 18), cx, cy + capc / 2 - rd * 0.16 + 28, fg, 0.16)
    W = 2 * (R + t)
    return elemento(W, W, s, nome or f"tampinha (21 dentes) · {estilo}", FAM,
                    nota="tampa coroa: 21 dentes, saia sombreada (tom da própria cor), disco liso no meio")


def roseta(f, R=136.0, n=22, centro="1", sub="NOITE", fitas=True, estilo="cheio", nome=None):
    """Roseta: borda em ondas (n arcos para fora), aro interno, número; fitas com corte em V (opcional)."""
    t = f.traco
    cor = f.acento if estilo == "cheio" else f.tinta
    fg = f.sobre_acento if estilo == "cheio" else f.fundo
    cx = R + 30
    cy = R + t + 2
    s = ""
    H = 2 * R + 2 * t + 4
    if fitas:
        fl, fw = R * 1.05, R * 0.42
        for sx, cfita in ((-1, mistura(cor, f.fundo, 0.35)), (1, mistura(cor, f.fundo, 0.18))):
            ang = math.radians(90 + sx * 24)
            ux, uy = math.cos(ang), math.sin(ang)
            px, py = -uy, ux
            x0, y0 = cx, cy
            x1, y1 = cx + ux * (R + fl * 0.55), cy + uy * (R + fl * 0.55)
            v = fw * 0.45
            poly = [(x0 + px * fw / 2, y0 + py * fw / 2), (x1 + px * fw / 2, y1 + py * fw / 2),
                    (x1 - ux * v, y1 - uy * v), (x1 - px * fw / 2, y1 - py * fw / 2), (x0 - px * fw / 2, y0 - py * fw / 2)]
            s += f'<path d="{_poli(poly)}" fill="{cfita}"/>'
            H = max(H, max(y for _, y in poly) + 3)
    pts = [(cx + R * 0.94 * math.cos(2 * math.pi * i / n - math.pi / 2), cy + R * 0.94 * math.sin(2 * math.pi * i / n - math.pi / 2))
           for i in range(n)]
    corda = math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])
    d = f"M{pts[0][0]:.2f} {pts[0][1]:.2f}" + "".join(
        f"A{corda * 0.56:.2f} {corda * 0.56:.2f} 0 0 1 {pts[(i + 1) % n][0]:.2f} {pts[(i + 1) % n][1]:.2f}" for i in range(n)) + "Z"
    s += f'<path d="{d}" fill="{cor}"/>'
    ri = R * 0.72
    s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{ri:.2f}" fill="none" stroke="{fg}" stroke-width="{t * 0.67:.2f}"/>'
    s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{ri - 7:.2f}" fill="none" stroke="{fg}" stroke-width="{t * 0.67:.2f}"/>'
    capc = ri * 0.8
    s += centro_tinta(f.fonte_display, centro, corpo(f.fonte_display, capc), cx, cy - ri * 0.12, fg)
    s += centro_tinta(f.fonte_texto, sub, corpo(f.fonte_texto, 16), cx, cy + capc / 2 - ri * 0.12 + 26, fg, 0.14)
    return elemento(2 * cx, H, s, nome or ("roseta com fitas" if fitas else "roseta"), FAM,
                    nota=f"{n} ondas; aro duplo; fitas com corte em V em 2 tons da própria cor")


# =====================================================================================================================
# carimbos
# =====================================================================================================================
def carimbo(f, tipo="retangulo", cor=None, ang=None, linhas=None, nome=None, forca=1.0, r=None):
    """Carimbo da MARCA, inclinado no ângulo da ficha, moldura dupla e tinta falhada (filtro)."""
    t = f.traco
    cor = cor or f.acento
    ang = f.angulo if ang is None else ang
    fid = uid("carimbo", tipo, cor, ang, f.seed)
    s = ""
    if tipo == "retangulo":
        w, h = 380.0, 204.0
        r = 0.0 if r is None else r
        s += f'<path d="{p_cantos(0, 0, w, h, r, t)}" fill="none" stroke="{cor}" stroke-width="{2 * t:.2f}"/>'
        s += f'<path d="{p_cantos(0, 0, w, h, r, 2 * t + 7 + t / 2)}" fill="none" stroke="{cor}" stroke-width="{t:.2f}"/>'
        top, mid, bot = linhas or ("NOITE 1", "AO VIVO", "20H30")
        # níveis: rótulo (18) · fio · display (50) · fio · hora (17); folga fio↔tinta ≥ 10 px
        s += centro_tinta(f.fonte_texto, top, corpo(f.fonte_texto, 18), w / 2, 46, cor, 0.24)
        s += centro_tinta(f.fonte_display, mid, corpo(f.fonte_display, 50), w / 2, 102, cor, 0.02)
        s += centro_tinta(f.fonte_mono, bot, corpo(f.fonte_mono, 17), w / 2, 158, cor, 0.12)
        for yy in (66.0, 138.0):
            s += f'<line x1="{w * 0.18:.2f}" y1="{yy:.2f}" x2="{w * 0.82:.2f}" y2="{yy:.2f}" stroke="{cor}" stroke-width="{t * 0.67:.2f}"/>'
        nota = "moldura dupla (grossa + fina), 3 níveis de texto, tinta falhada; inclinado no ângulo da ficha"
    elif tipo == "oval":
        w, h = 400.0, 210.0
        s += f'<ellipse cx="{w / 2:.2f}" cy="{h / 2:.2f}" rx="{w / 2 - t:.2f}" ry="{h / 2 - t:.2f}" fill="none" stroke="{cor}" stroke-width="{2 * t:.2f}"/>'
        s += f'<ellipse cx="{w / 2:.2f}" cy="{h / 2:.2f}" rx="{w / 2 - 3 * t - 7:.2f}" ry="{h / 2 - 3 * t - 7:.2f}" fill="none" stroke="{cor}" stroke-width="{t:.2f}"/>'
        top, mid, bot = linhas or ("AO VIVO", "3 NOITES", "20H30")
        s += centro_tinta(f.fonte_texto, top, corpo(f.fonte_texto, 20), w / 2, 50, cor, 0.26)
        s += centro_tinta(f.fonte_display, mid, corpo(f.fonte_display, 58), w / 2, h / 2 + 2, cor, 0.02)
        s += centro_tinta(f.fonte_mono, bot, corpo(f.fonte_mono, 20), w / 2, h - 48, cor, 0.12)
        for sx in (-1, 1):
            s += _losango(w / 2 + sx * 100, 50, 4, cor)
        nota = "oval de duplo aro: carimbo de 'recebido'; texto em 3 níveis"
    elif tipo == "circular":
        R = 150.0
        w = h = 2 * R
        cx = cy = R
        s += f'<circle cx="{cx}" cy="{cy}" r="{R - t:.2f}" fill="none" stroke="{cor}" stroke-width="{2 * t:.2f}"/>'
        s += f'<circle cx="{cx}" cy="{cy}" r="{R - 52:.2f}" fill="none" stroke="{cor}" stroke-width="{t:.2f}"/>'
        top, mid, bot = linhas or ("PÓS-GRADUAÇÃO", "20H30", "AO VIVO")
        rm = (R - 2 * t + R - 52) / 2
        ct, tt = arco_caber(f, top, rm, 20, f.fonte_texto, 0.12)       # <= 135° (D21): ponto separador no meio do vão
        cb, tb = arco_caber(f, bot, rm, 20, f.fonte_texto, 0.2)
        s += arco_texto(f, top, cx, cy, rm, ct, cor, "topo", tracking=tt)
        s += arco_texto(f, bot, cx, cy, rm, cb, cor, "base", tracking=tb)
        for a in (180, 0):
            s += _ponto(cx + rm * math.cos(math.radians(a)), cy + rm * math.sin(math.radians(a)), 4, cor)
        s += f'<line x1="{cx - 62:.2f}" y1="{cy - 30:.2f}" x2="{cx + 62:.2f}" y2="{cy - 30:.2f}" stroke="{cor}" stroke-width="{t:.2f}"/>'
        s += f'<line x1="{cx - 62:.2f}" y1="{cy + 30:.2f}" x2="{cx + 62:.2f}" y2="{cy + 30:.2f}" stroke="{cor}" stroke-width="{t:.2f}"/>'
        s += centro_tinta(f.fonte_mono, mid, corpo(f.fonte_mono, 30), cx, cy, cor, 0.04)
        nota = "carimbo postal: arco em cima e embaixo, data/hora entre fios no meio"
    else:   # faixa (tarja carimbada)
        txt = (linhas or ("AO VIVO · 20H30",))[0]      # só texto do cliente (antes "RESERVADO ATÉ…", inventado)
        w, h = larg_rotulo(f, txt, 24, f.fonte_texto, 0.14) + 2 * 40, 96.0
        s += f'<path d="{p_cantos(0, 0, w, h, r or 0)}" fill="{cor}"/>'
        s += f'<path d="{p_cantos(0, 0, w, h, r or 0, 7)}" fill="none" stroke="{f.fundo}" stroke-width="{t * 0.67:.2f}"/>'
        s += centro_tinta(f.fonte_texto, txt, corpo(f.fonte_texto, 24), w / 2, h / 2, f.fundo, 0.14)
        nota = "tarja carimbada (sigilo DE MARCA): cheia, texto vazado no fundo, fio interno; tinta leve (borda áspera, sem mancha)"
    defs = tinta_leve(fid, f.seed + 11) if tipo == "faixa" else tinta_carimbo(fid, f.seed + 11, forca)
    W, H = _caixa_girada(w, h, ang, 8)
    corpo_svg = (f'<g filter="url(#{fid})"><g transform="translate({W / 2:.2f} {H / 2:.2f}) rotate({ang:.2f}) '
                 f'translate({-w / 2:.2f} {-h / 2:.2f})">{s}</g></g>')
    return elemento(W, H, corpo_svg, nome or f"carimbo · {tipo}", FAM, defs=defs, nota=nota)


# =====================================================================================================================
# ao vivo, medalha, escudo, etiquetas
# =====================================================================================================================
def ao_vivo(f, tipo="pilula", nome=None):
    """Selo 'ao vivo': ponto (0,84 u) + ondas congeladas; tally; dividido com horário; circular com texto em anel."""
    t = f.traco
    capx = 25.0
    s = ""
    if tipo == "pilula":
        tw = larg_rotulo(f, "AO VIVO", capx, f.fonte_texto, 0.12)
        h = capx + 2 * 17
        pr = 0.84 * capx / 2
        ondas = pr * 2 + 14
        trail = corpo(f.fonte_texto, capx) * 0.12              # tracking depois da última letra
        w = h / 2 + ondas + 10 + tw - trail + h / 2            # respiro direito = raio da pílula (= esquerdo)
        s += f'<path d="{p_cantos(t / 2, t / 2, w - t, h - t, (h - t) / 2)}" fill="none" stroke="{f.tinta}" stroke-width="{t:.2f}"/>'
        cx, cy = h / 2 + pr, h / 2
        s += _ponto(cx, cy, pr, f.acento)
        for k, op in ((1, 0.6), (2, 0.3)):
            rr = pr + 6 * k
            a0, a1 = math.radians(-50), math.radians(50)
            s += (f'<path d="M{cx + rr * math.cos(a0):.2f} {cy + rr * math.sin(a0):.2f}A{rr:.2f} {rr:.2f} 0 0 1 '
                  f'{cx + rr * math.cos(a1):.2f} {cy + rr * math.sin(a1):.2f}" fill="none" stroke="{f.acento}" '
                  f'stroke-width="{t * 0.8:.2f}" stroke-linecap="round" opacity="{op}"/>')
        a, _ = rotulo(f, "AO VIVO", h / 2 + ondas + 10, cy, f.tinta, capx, f.fonte_texto, 0.12)
        s += a
        nota = "ponto = 0,84 da maiúscula; 2 ondas congeladas (no vídeo, pulsam a 1 Hz)"
    elif tipo == "tally":
        tw = larg_rotulo(f, "AO VIVO", capx, f.fonte_texto, 0.12)
        h = capx + 2 * 18
        pr = 0.84 * capx / 2
        w = 22 + 2 * pr + 14 + tw + 22
        s += f'<rect width="{w:.2f}" height="{h:.2f}" fill="{f.acento}"/>'
        s += _ponto(22 + pr, h / 2, pr, f.sobre_acento)
        a, _ = rotulo(f, "AO VIVO", 22 + 2 * pr + 14, h / 2, f.sobre_acento, capx, f.fonte_texto, 0.12)
        s += a
        nota = "tally de estúdio: bloco reto (raio 0) na cor de 'no ar'"
    elif tipo == "dividido":
        h = capx + 2 * 18
        tw = larg_rotulo(f, "AO VIVO", capx, f.fonte_texto, 0.12)
        hw = larg_rotulo(f, "20H30", 22, f.fonte_mono, 0.04)
        bw = h
        r = f.raio
        w = bw + 18 + tw + 18 + t + 18 + hw + r                 # respiro direito = raio (antes 18 < 28)
        s += f'<path d="{p_cantos(0, 0, bw, h, cantos=[r, 0, 0, r])}" fill="{f.acento}"/>'
        s += _ponto(bw / 2, h / 2, 0.84 * capx / 2, f.sobre_acento)
        s += f'<path d="{p_cantos(bw - t / 2, t / 2, w - bw, h - t, cantos=[0, r - t / 2, r - t / 2, 0])}" fill="none" stroke="{f.tinta}" stroke-width="{t:.2f}"/>'
        a, _ = rotulo(f, "AO VIVO", bw + 18, h / 2, f.tinta, capx, f.fonte_texto, 0.12)
        x = bw + 18 + tw + 18
        s += a + f'<line x1="{x:.2f}" y1="{t:.2f}" x2="{x:.2f}" y2="{h - t:.2f}" stroke="{f.tinta}" stroke-width="{t:.2f}"/>'
        b, _ = rotulo(f, "20H30", x + 18 + t, h / 2, f.acento, 22, f.fonte_mono, 0.04)
        s += b
        nota = "bloco do ponto (acento) + rótulo + hora: status e horário numa peça só"
    else:   # circular
        el = selo_giratorio(f, "AO VIVO • ", R=120, miolo="ponto",
                            nome="ao vivo · circular")
        el.nota = "anel de texto contínuo + ponto com 2 ondas: canto de story/hero"
        return el
    return elemento(w, h, s, nome or f"ao vivo · {tipo}", FAM, nota=nota)


def medalha(f, tipo="fitas", nome=None):
    t = f.traco
    s = ""
    defs = ""
    if tipo == "fitas":
        R = 96.0
        cx, cy = 130.0, R + 6
        fl, fw = 140.0, 64.0
        for sx, c in ((-1, mistura(f.tinta, f.fundo, 0.25)), (1, f.tinta)):
            ang = math.radians(90 + sx * 18)
            ux, uy = math.cos(ang), math.sin(ang)
            px, py = -uy, ux
            x1, y1 = cx + ux * (R + fl * 0.5), cy + uy * (R + fl * 0.5)
            v = fw * 0.42
            poly = [(cx + px * fw / 2, cy + py * fw / 2), (x1 + px * fw / 2, y1 + py * fw / 2), (x1 - ux * v, y1 - uy * v),
                    (x1 - px * fw / 2, y1 - py * fw / 2), (cx - px * fw / 2, cy - py * fw / 2)]
            s += f'<path d="{_poli(poly)}" fill="{c}"/>'
        s += _ponto(cx, cy, R, f.acento)
        s += f'<circle cx="{cx}" cy="{cy}" r="{R - 12:.2f}" fill="none" stroke="{f.sobre_acento}" stroke-width="{t * 0.67:.2f}"/>'
        s += centro_tinta(f.fonte_display, "1", corpo(f.fonte_display, 92), cx, cy - 8, f.sobre_acento)
        s += centro_tinta(f.fonte_texto, "NOITE", corpo(f.fonte_texto, 16), cx, cy + 56, f.sobre_acento, 0.18)
        w, h = 260.0, cy + R + fl * 0.5 + 10
        nota = "disco + 2 fitas com corte em V (tons da própria tinta); conquista, etapa vencida"
    elif tipo == "pendurada":
        R = 92.0
        cx = 130.0
        top, cy = 4.0, 220.0 - 4
        cy = 150.0 + R * 0.0
        fw = 56.0
        listras = [f.tinta, f.acento, f.tinta]
        for sx in (-1, 1):
            xa, xb = cx + sx * 70, cx + sx * 10
            for k, c in enumerate(listras):
                o0, o1 = -fw / 2 + k * fw / 3, -fw / 2 + (k + 1) * fw / 3
                poly = [(xa + o0, top), (xa + o1, top), (xb + o1 * 0.6, cy - R * 0.6), (xb + o0 * 0.6, cy - R * 0.6)]
                s += f'<path d="{_poli(poly)}" fill="{c}"/>'
        s += _ponto(cx, cy, R, f.acento)
        s += f'<circle cx="{cx}" cy="{cy}" r="{R - 10:.2f}" fill="none" stroke="{f.sobre_acento}" stroke-width="{t * 0.67:.2f}"/>'
        s += centro_tinta(f.fonte_display, "3", corpo(f.fonte_display, 86), cx, cy - 8, f.sobre_acento)
        s += centro_tinta(f.fonte_texto, "NOITES", corpo(f.fonte_texto, 15), cx, cy + 52, f.sobre_acento, 0.14)
        w, h = 260.0, cy + R + 4
        nota = "medalha pendurada: fita em V com 3 listras (tinta · acento · tinta)"
    else:   # escudo
        w, h = 230.0, 270.0
        def esc(x0, y0, W, H, r):
            return (f"M{x0 + r:.2f} {y0:.2f}H{x0 + W - r:.2f}Q{x0 + W:.2f} {y0:.2f} {x0 + W:.2f} {y0 + r:.2f}"
                    f"V{y0 + H * 0.52:.2f}C{x0 + W:.2f} {y0 + H * 0.80:.2f} {x0 + W * 0.66:.2f} {y0 + H * 0.92:.2f} {x0 + W / 2:.2f} {y0 + H:.2f}"
                    f"C{x0 + W * 0.34:.2f} {y0 + H * 0.92:.2f} {x0:.2f} {y0 + H * 0.80:.2f} {x0:.2f} {y0 + H * 0.52:.2f}"
                    f"V{y0 + r:.2f}Q{x0:.2f} {y0:.2f} {x0 + r:.2f} {y0:.2f}Z")
        D = esc(0, 0, w, h, f.raio)
        cid = uid("escudo", f.seed)
        defs += f'<clipPath id="{cid}"><path d="{D}"/></clipPath>'
        s += f'<path d="{D}" fill="{f.tinta}"/>'
        g = 14.0   # fio a g px da borda, em TODO o contorno (traço largo recortado + traço menor na cor do fundo)
        s += (f'<g clip-path="url(#{cid})"><path d="{D}" fill="none" stroke="{f.acento}" stroke-width="{2 * (g + t / 2):.2f}" '
              f'stroke-linejoin="round"/><path d="{D}" fill="none" stroke="{f.tinta}" stroke-width="{2 * (g - t / 2):.2f}" '
              f'stroke-linejoin="round"/></g>')
        s += centro_tinta(f.fonte_texto, "NOITE", corpo(f.fonte_texto, 20), w / 2, 64, f.fundo, 0.2)
        s += centro_tinta(f.fonte_display, "1", corpo(f.fonte_display, 104), w / 2, 140, f.fundo)
        s += f'<line x1="{w / 2 - 30:.2f}" y1="{204:.2f}" x2="{w / 2 + 30:.2f}" y2="{204:.2f}" stroke="{f.acento}" stroke-width="{2 * t:.2f}"/>'
        nota = "escudo geométrico (sem brasão nem órgão): distintivo de etapa; aro interno no acento"
    return elemento(w, h, s, nome or f"medalha · {tipo}", FAM, defs=defs, nota=nota)


def etiqueta_preco(f, tipo="ponta", linhas=("AO VIVO", "20H30"), cor=None, ang=None, nome=None):
    """Etiqueta SEM preço e SEM oferta inventada: ponta de seta com furo (sem cordão — D22); bandeirola com corte em V.
    A largura acompanha o texto (respiro lateral >= raio)."""
    t = f.traco
    cor = cor or f.acento
    fg = f.sobre_acento if cor == f.acento else f.fundo
    ang = f.angulo if ang is None else ang
    s = ""
    if tipo == "ponta":
        h = 170.0
        pw = h * 0.42
        r = f.raio
        capx = 46.0
        lh = capx * 1.3
        tw = max(larg_rotulo(f, ln, capx, f.fonte_display, 0.01) for ln in linhas)
        x0 = pw + 28
        w = x0 + tw + max(r, 28.0) + 4
        d = (f"M0 {h / 2:.2f}L{pw:.2f} 0H{w - r:.2f}A{r} {r} 0 0 1 {w} {r}V{h - r:.2f}A{r} {r} 0 0 1 {w - r:.2f} {h}"
             f"H{pw:.2f}Z")
        fr = 10.0
        d += circulo_d(pw * 0.62, h / 2, fr)
        s += f'<path d="{d}" fill="{cor}" fill-rule="evenodd"/>'
        s += f'<circle cx="{pw * 0.62:.2f}" cy="{h / 2:.2f}" r="{fr + 4:.2f}" fill="none" stroke="{fg}" stroke-width="1.5" opacity="0.5"/>'
        for k, ln in enumerate(linhas):
            a, _ = rotulo(f, ln, x0, h / 2 + (k - (len(linhas) - 1) / 2) * lh, fg, capx, f.fonte_display, 0.01)
            s += a
        nota = "etiqueta com furo (texto do CLIENTE, nunca preço/oferta inventada); inclinada no ângulo; largura = texto"
    else:   # bandeirola
        h = 110.0
        v = h * 0.32
        capx = 40.0
        tw = larg_rotulo(f, linhas[0], capx, f.fonte_display, 0.02)
        w = 12 + 30 + tw + 30 + v                    # tarja de 12 + respiro + texto + respiro + fundo do corte em V
        d = f"M0 0H{w:.2f}L{w - v:.2f} {h / 2:.2f}L{w:.2f} {h:.2f}H0Z"
        s += f'<path d="{d}" fill="{cor}"/>'
        s += f'<rect x="0" y="0" width="{12:.2f}" height="{h:.2f}" fill="{mistura(cor, f.fundo, 0.3)}"/>'
        a, _ = rotulo(f, linhas[0], 12 + 30, h / 2, fg, capx, f.fonte_display, 0.02)
        s += a
        nota = "bandeirola com corte em V (rabo de andorinha): aviso curto; largura acompanha o texto"
    W, H = _caixa_girada(w, h, ang, 6)
    corpo_svg = (f'<g transform="translate({W / 2:.2f} {H / 2:.2f}) rotate({ang:.2f}) '
                 f'translate({-w / 2:.2f} {-h / 2:.2f})">{s}</g>')
    return elemento(W, H, corpo_svg, nome or f"etiqueta · {tipo}", FAM, nota=nota)


# =====================================================================================================================
# amostras
# =====================================================================================================================
@amostra(FAM, "selos circulares")
def _a_circ(f):
    fc = claro(f)
    return [
        selo_circular(f, estilo="contorno"),
        selo_circular(f, estilo="cheio", sep="losango"),
        selo_circular(f, "PÓS-GRADUAÇÃO", "AO VIVO", "1", "NOITE", estilo="tinta", nome="selo circular · tinta"),
        no_claro(selo_circular(fc, "3 NOITES", "20H30", "AO VIVO", None, estilo="contorno", nome="selo circular · papel")),
        selo_giratorio(f),
        selo_giratorio(f, "PÓS-GRADUAÇÃO • AO VIVO • ", estilo="cheio", miolo="3",
                       nome="selo giratório · cheio · número"),
    ]


@amostra(FAM, "estrelas e explosões")
def _a_estrelas(f):
    fc = claro(f)
    return [
        estrela(f, 24, 0.88, linhas=("AO VIVO",), nome="serrilhado 24 pontas (0,88)",
                nota="selo de 24 pontas, razão 0,88: borda serrilhada sem virar 'oferta'"),
        estrela(f, 12, 0.82, arred=f.raio, linhas=("NOITE", "1"), nome="selo ondulado 12 lóbulos",
                nota="12 lóbulos senoidais iguais (razão 0,82): flor/lacre, tom mais leve que a explosão"),
        no_claro(estrela(fc, 32, 0.9, linhas=("AO VIVO",), estilo="tinta", nome="serrilhado 32 · papel",
                         nota="32 pontas finas, quase um selo de lacre")),
        tampinha(f),
        tampinha(f, centro="1", sub="NOITE", estilo="tinta", nome="tampinha · tinta"),
        roseta(f),
        roseta(f, centro="3", sub="NOITES", fitas=False, estilo="tinta", nome="roseta sem fitas · tinta"),
    ]


@amostra(FAM, "carimbos")
def _a_carimbos(f):
    fc = claro(f)
    return [
        carimbo(f, "retangulo"),
        carimbo(f, "retangulo", cor=f.tinta, r=f.raio, ang=4, linhas=("PÓS-GRADUAÇÃO", "3 NOITES", "20H30"),
                nome="carimbo · raio da ficha · +4°"),
        carimbo(f, "oval"),
        no_claro(carimbo(fc, "circular", cor=fc.acento, nome="carimbo circular · papel")),
        no_claro(carimbo(fc, "retangulo", cor=fc.tinta, ang=-3, forca=0.8, nome="carimbo · papel · tinta escura")),
        carimbo(f, "faixa", ang=-4, nome="tarja carimbada"),
    ]


@amostra(FAM, "ao vivo")
def _a_aovivo(f):
    return [ao_vivo(f, "pilula"), ao_vivo(f, "tally"), ao_vivo(f, "dividido"), ao_vivo(f, "circular")]


@amostra(FAM, "medalhas e etiquetas")
def _a_medalhas(f):
    return [medalha(f, "fitas"), medalha(f, "pendurada"), medalha(f, "escudo"), etiqueta_preco(f, "ponta"),
            etiqueta_preco(f, "bandeirola", linhas=("AO VIVO",), cor=f.tinta, ang=0),
            etiqueta_preco(f, "ponta", linhas=("3 NOITES",), cor=f.tinta, ang=4, nome="etiqueta · tinta · +4°")]
