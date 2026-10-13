"""ornamentos.fios — família FIOS E MARCAÇÕES DE SISTEMA (organizar, medir, ligar, apontar, enquadrar).

Origem (references/elementos.md "Fios", "Grids", "Construção"; pesquisa 11 E15–E18, E26–E29, E35, E110; 14 §A/B/D):
  - ≤ 2 espessuras: fino = traço da ficha, grosso = 2 × traço; pontas retas; começam e terminam em linha de coluna;
  - régua: traço maior a cada 5 ou 10, curto = 40–50% do longo; mede algo REAL (hora do evento, a própria peça);
  - cruzes "+" EXATAMENTE nos cruzamentos da grade (passo = unidade × n); braço = ½–1 módulo;
  - cantoneira só onde há medida/enquadramento (visor); callout com fio a 0/90° (ou o ângulo da ficha), ponto = 3× fio;
  - seta: ponta aberta a 45° (uma só no sistema), haste = fio; cotovelo com o raio da ficha.
Nada de dado inventado: os números são da própria peça (comprimento em px, U, R, ângulo) ou do cliente (20H30, 3 noites).
"""
import math

from .nucleo import amostra, elemento, texto, largura, cap, polilinha
from .formas import (rotulo, larg_rotulo, mistura, claro, no_claro, corpo, p_cantos)

FAM = "fios"
CAP = 25.0      # maiúscula mínima de rótulo que precisa ser lido (num lado de 1080)
MICRO = 15.0    # maiúscula de micrográfico (escala, coordenada): textura, não precisa ser lido no celular


def _ln(x1, y1, x2, y2, cor, sw, extra=""):
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{cor}" '
            f'stroke-width="{sw:.2f}"{(" " + extra) if extra else ""}/>')


def _pl(d, cor, sw, extra=""):
    return (f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="{sw:.2f}" stroke-linejoin="miter"'
            f'{(" " + extra) if extra else ""}/>')


def tracos(L, tr, vao):
    """dasharray com TRAÇO INTEIRO nas duas pontas: ajusta o vão para caber n traços exatos em L (sem toco no fim)."""
    n = max(2, round((L + vao) / (tr + vao)))
    return f"{tr:.2f} {(L - n * tr) / (n - 1):.2f}"


def ponta(x, y, ang, tam, cor, sw, cheia=False):
    """Ponta de seta no fim (x, y) apontando para `ang` (graus). Aberta = chevron a 45°; cheia = triângulo."""
    a = math.radians(ang)
    pts = [(x + math.cos(a + math.radians(s)) * tam, y + math.sin(a + math.radians(s)) * tam) for s in (135, -135)]
    if cheia:
        return (f'<path d="M{x:.2f} {y:.2f}L{pts[0][0]:.2f} {pts[0][1]:.2f}L{pts[1][0]:.2f} {pts[1][1]:.2f}Z" '
                f'fill="{cor}"/>')
    return _pl(f"M{pts[0][0]:.2f} {pts[0][1]:.2f}L{x:.2f} {y:.2f}L{pts[1][0]:.2f} {pts[1][1]:.2f}", cor, sw)


# =====================================================================================================================
# fios e divisórias
# =====================================================================================================================
def fio(f, comp=440, tipo="fino", cor=None):
    """Fio simples ou composto. tipo: fino · grosso · filete (grosso+fino, de jornal) · ponto (termina em ponto) ·
    tracejado (= em andamento, GitLab) · barras (fim em barrinha, como cota)."""
    t = f.traco
    cor = cor or f.tinta
    g = 2 * t
    h = 24.0
    y = h / 2
    s = ""
    if tipo == "fino":
        s = _ln(0, y, comp, y, cor, t)
    elif tipo == "grosso":
        s = _ln(0, y, comp, y, cor, g)
    elif tipo == "filete":
        s = _ln(0, y - g / 2 - t, comp, y - g / 2 - t, cor, g) + _ln(0, y + t, comp, y + t, cor, t)
    elif tipo == "ponto":
        r = (1.5 * t + 0.5) * 1.4                     # o ponto cabe na caixa (antes vazava 2 px à direita)
        s = _ln(0, y, comp - r, y, cor, t) + f'<circle cx="{comp - r:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{f.acento}"/>'
    elif tipo == "tracejado":
        s = _ln(0, y, comp, y, cor, t, f'stroke-dasharray="{tracos(comp, t * 4, t * 3)}"')
    elif tipo == "barras":
        s = _ln(0, y, comp, y, cor, t) + _ln(t / 2, y - 9, t / 2, y + 9, cor, t) + _ln(comp - t / 2, y - 9, comp - t / 2, y + 9, cor, t)
    notas = {"fino": f"fio fino = traço da ficha ({t:g} px); encosta na tinta, não na caixa",
             "grosso": f"fio grosso = 2 × traço ({g:g} px); no máximo 2 espessuras por peça",
             "filete": "grosso + fino (filete de jornal): abre seção, assina rodapé",
             "ponto": "fio que termina em ponto (acento): 'daqui sai uma legenda'",
             "tracejado": "tracejado = em andamento / ainda não aconteceu",
             "barras": "fio com barrinhas: medida, intervalo"}
    return elemento(comp, h, s, f"fio · {tipo}", FAM, css=f".fio{{height:0;border-top:{t:g}px solid {cor}}}",
                    nota=notas[tipo])


def divisoria(f, txt="AO VIVO", num="01", tipo="rotulo", comp=460, cor=None):
    """Divisória com rótulo (eyebrow): rótulo de seção + fio que corre até a margem (14 D n.º 7)."""
    t = f.traco
    cor = cor or f.tinta
    h = CAP + 26
    cy = h / 2
    gap = f.unidade * 0.6
    s = ""
    if tipo == "rotulo":
        a, wn = rotulo(f, num, 0, cy, f.acento, CAP, f.fonte_mono, 0.04)
        b, wt = rotulo(f, txt, wn + gap, cy, cor, CAP, f.fonte_texto, 0.12)
        s = a + b + _ln(wn + gap + wt + gap, cy, comp, cy, cor, t)
        nota = "número (acento) + rótulo + fio até a margem; o fio começa a 0,6 U da tinta"
    elif tipo == "centro":
        wt = larg_rotulo(f, txt, CAP, f.fonte_texto, 0.12)
        b, _ = rotulo(f, txt, comp / 2, cy, cor, CAP, f.fonte_texto, 0.12, "middle")
        s = _ln(0, cy, comp / 2 - wt / 2 - gap, cy, cor, t) + b + _ln(comp / 2 + wt / 2 + gap, cy, comp, cy, cor, t)
        nota = "rótulo centrado entre fios: pausa entre blocos"
    elif tipo == "pilula":
        wt = larg_rotulo(f, txt, CAP * 0.8, f.fonte_texto, 0.12)
        ph = CAP * 0.8 + 2 * 12
        pw = wt + 2 * CAP * 0.8 * 1.1
        s = f'<path d="{p_cantos(t / 2, cy - ph / 2, pw, ph, ph / 2)}" fill="none" stroke="{cor}" stroke-width="{t:.2f}"/>'
        b, _ = rotulo(f, txt, t / 2 + pw / 2, cy, cor, CAP * 0.8, f.fonte_texto, 0.12, "middle")
        s += b + _ln(t / 2 + pw, cy, comp, cy, cor, t)
        nota = "rótulo em pílula de contorno que vira fio (a pílula 'solta' o fio)"
    elif tipo == "barra":
        bw = f.unidade * 1.5
        s = f'<rect x="0" y="{cy - t:.2f}" width="{bw:.2f}" height="{2 * t:.2f}" fill="{f.acento}"/>'
        b, wt = rotulo(f, txt, bw + gap, cy, cor, CAP, f.fonte_texto, 0.12)
        comp = max(comp, bw + 2 * gap + wt + 3 * f.unidade)
        s += b + _ln(bw + gap + wt + gap, cy, comp, cy, mistura(cor, f.fundo, 0.5), t)
        nota = "barra grossa (acento) + rótulo + fio fino: 2 espessuras, 1 acento"
    else:   # sublinhado: rótulo em cima, fio grosso só sob o rótulo e fino até a margem
        b, wt = rotulo(f, txt, 0, cy - 6, cor, CAP, f.fonte_texto, 0.12)
        yb = cy - 6 + CAP / 2 + 12
        s = b + _ln(0, yb, wt, yb, f.acento, 2 * t) + _ln(wt, yb + t / 2, comp, yb + t / 2, cor, t)
        h = yb + 2 * t + 2
        nota = "aba sublinhada: grosso sob o rótulo (= item ativo), fino até a margem"
    return elemento(comp, h, s, f"divisória · {tipo}", FAM, nota=nota)


# =====================================================================================================================
# réguas
# =====================================================================================================================
def regua(f, comp=460, ini=0, fim=100, sub=1, medio=5, maior=10, rotulos=20, fmt="{:g}", cursor=None,
          cursor_txt=None, cor=None, vertical=False, nome=None, nota=""):
    """Régua graduada: traço maior a cada `maior`, médio a cada `medio`, curto a cada `sub` (curto = 45% do longo)."""
    t = f.traco
    cor = cor or f.tinta
    L = 30.0                              # traço longo
    n = int(round((fim - ini) / sub))
    pad = 30.0
    esc = (comp - 2 * pad) / (fim - ini)
    y0 = 64.0 if cursor is not None else 8.0
    s = _ln(pad, y0 + L, comp - pad, y0 + L, cor, t)
    for k in range(n + 1):
        v = ini + k * sub
        x = pad + (v - ini) * esc
        if abs((v - ini) / maior - round((v - ini) / maior)) < 1e-6:
            ll, sw = L, t
        elif abs((v - ini) / medio - round((v - ini) / medio)) < 1e-6:
            ll, sw = L * 0.7, t * 0.67
        else:
            ll, sw = L * 0.45, t * 0.5
        s += _ln(x, y0 + L - ll, x, y0 + L, cor, sw)
        if rotulos and abs((v - ini) / rotulos - round((v - ini) / rotulos)) < 1e-6:
            a, _ = rotulo(f, fmt.format(v), x, y0 + L + 14 + MICRO / 2, mistura(cor, f.fundo, 0.25), MICRO,
                          f.fonte_mono, 0.02, "middle")
            s += a
    h = y0 + L + 14 + MICRO + 6
    if cursor is not None:
        x = pad + (cursor - ini) * esc
        tri = 11.0
        ty = y0 - 12                          # ponta do triângulo: 12 px acima do traço mais alto
        s += (f'<path d="M{x - tri:.2f} {ty - tri * 1.3:.2f}L{x + tri:.2f} {ty - tri * 1.3:.2f}L{x:.2f} {ty:.2f}Z" '
              f'fill="{f.acento}"/>' + _ln(x, ty, x, y0 + L, f.acento, t))
        if cursor_txt:
            a, w_ = rotulo(f, cursor_txt, x + tri + 8, ty - tri * 0.65, f.acento, 18, f.fonte_mono, 0.04)
            s += a
    W, H = comp, h
    if vertical:
        s = f'<g transform="translate({h:.2f} 0) rotate(90)">{s}</g>'
        W, H = h, comp
    return elemento(W, H, s, nome or "régua", FAM, nota=nota or "traço maior a cada 10, médio a cada 5; mede algo real")


def regua_canto(f, w=440, h=300, passo=None, cor=None):
    """Réguas em L (topo + esquerda) medindo a própria área em px, de U em U — moldura de 'prova técnica'."""
    t = f.traco
    passo = passo or f.unidade
    cor = cor or f.tinta
    b = 34.0
    s = (f'<rect x="{b:.2f}" y="{b:.2f}" width="{w - b:.2f}" height="{h - b:.2f}" fill="none" stroke="{mistura(cor, f.fundo, 0.6)}" '
         f'stroke-width="{t * 0.67:.2f}" stroke-dasharray="2 6"/>')
    s += _ln(b, b, w, b, cor, t * 0.67) + _ln(b, b, b, h, cor, t * 0.67)
    k = 0
    while b + k * passo <= w + 0.1:
        x = b + k * passo
        ll = 16 if k % 5 == 0 else 8
        s += _ln(x, b - ll, x, b, cor, t * 0.67)
        if k % 5 == 0 and k:
            a, wn = rotulo(f, f"{k * passo:g}", x + 4, b - 22, mistura(cor, f.fundo, 0.3), 11, f.fonte_mono, 0.02)
            if x + 4 + wn <= w:                     # número que não cabe inteiro não entra (nada cortado na borda)
                s += a
        k += 1
    k = 0
    while b + k * passo <= h + 0.1:
        y = b + k * passo
        ll = 16 if k % 5 == 0 else 8
        s += _ln(b - ll, y, b, y, cor, t * 0.67)
        if k % 5 == 0 and k:
            # como no topo (número DEPOIS do traço, no sentido da medida): aqui, abaixo do traço, lido de baixo
            # para cima (antes ficava acima do traço — o oposto da régua de cima)
            a, wn = rotulo(f, f"{k * passo:g}", 0, 0, mistura(cor, f.fundo, 0.3), 11, f.fonte_mono, 0.02)
            if y + 4 + wn <= h:
                s += f'<g transform="translate({b - 22:.2f} {y + 4 + wn:.2f}) rotate(-90)">{a}</g>'
        k += 1
    s += f'<rect x="0" y="0" width="{b - 4:.2f}" height="{b - 4:.2f}" fill="{f.acento}"/>'
    return elemento(w, h, s, f"réguas em L · passo {passo:g} (U)", FAM,
                    nota="mede a própria área em px, de U em U; quadrado no canto = origem (acento)")


# =====================================================================================================================
# cruzes, registro, pontos
# =====================================================================================================================
def _cruz(cx, cy, b, cor, sw):
    return _ln(cx - b, cy, cx + b, cy, cor, sw) + _ln(cx, cy - b, cx, cy + b, cor, sw)


def cruzes(f, cols=6, rows=4, passo=None, braco=None, cor=None, destaque=None, tipo="cruz", coords=False, nome=None):
    """Cruzes "+" nos cruzamentos da grade (passo = 3 U por padrão). tipo: cruz · alterna (cruz/ponto) · ponto."""
    t = f.traco
    passo = passo or 3 * f.unidade
    braco = braco or f.unidade * 0.4
    cor = cor or mistura(f.tinta, f.fundo, 0.45)
    m = braco + t + (28 if coords else 0)
    W, H = m + (cols - 1) * passo + braco + t, m + (rows - 1) * passo + braco + t
    s = ""
    for j in range(rows):
        for i in range(cols):
            cx, cy = m + i * passo, m + j * passo
            c = f.acento if destaque == (i, j) else cor
            if tipo == "ponto" or (tipo == "alterna" and (i + j) % 2):
                s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{t * 0.9:.2f}" fill="{c}"/>'
            else:
                s += _cruz(cx, cy, braco, c, t * 0.67 if c == cor else t)
    if coords:
        for i in range(cols):
            a, _ = rotulo(f, "ABCDEFGHIJ"[i], m + i * passo, 10, mistura(f.tinta, f.fundo, 0.3), 12, f.fonte_mono, 0, "middle")
            s += a
        for j in range(rows):
            a, _ = rotulo(f, str(j + 1), 6, m + j * passo, mistura(f.tinta, f.fundo, 0.3), 12, f.fonte_mono, 0)
            s += a
    nota = (f"passo {passo:g} = {passo / f.unidade:g} U; braço {braco:g}; fio fino a 55%"
            + ("; o acento marca O lugar" if destaque else "") + ("; coordenadas A1… na margem" if coords else ""))
    return elemento(W, H, s, nome or f"cruzes de grade · {tipo}", FAM, nota=nota)


def prova_grafica(f, w=440, h=300, cor=None):
    """Marcas de corte (L fora do corte, afastadas 12 px) + alvos de registro no meio das bordas: 'prova de gráfica'."""
    t = f.traco * 0.67
    cor = cor or f.tinta
    # margem = afastamento + marca + 6: tudo DENTRO da caixa (antes as marcas e os alvos vazavam 2–4 px)
    off, L = 12.0, 28.0
    m = off + L + 6
    x0, y0, x1, y1 = m, m, w - m, h - m
    s = ""
    for (x, y, sx, sy) in ((x0, y0, -1, -1), (x1, y0, 1, -1), (x1, y1, 1, 1), (x0, y1, -1, 1)):
        s += _ln(x + sx * off, y, x + sx * (off + L), y, cor, t) + _ln(x, y + sy * off, x, y + sy * (off + L), cor, t)
    ra, ba = 8.0, 12.0                                   # alvo: anel 8 + cruz de braço 12, centrado na faixa da marca
    for (cx, cy) in (((x0 + x1) / 2, y0 - off - L / 2), ((x0 + x1) / 2, y1 + off + L / 2)):
        s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{ra:.2f}" fill="none" stroke="{cor}" stroke-width="{t:.2f}"/>'
        s += _cruz(cx, cy, ba, cor, t)
    s += (f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" height="{y1 - y0:.2f}" fill="none" '
          f'stroke="{mistura(cor, f.fundo, 0.7)}" stroke-width="{t:.2f}" stroke-dasharray="3 5"/>')
    # barra de cor da marca (fundo · tinta · acento · papel · apoio)
    cs = [f.fundo, f.tinta, f.acento, f.papel, f.apoio]
    bw = 16.0
    for k, c in enumerate(cs):
        s += f'<rect x="{x1 - off - 10 - len(cs) * bw + k * bw:.2f}" y="{y1 + off + 4:.2f}" width="{bw:.2f}" height="{bw:.2f}" fill="{c}" stroke="{mistura(cor, f.fundo, 0.5)}" stroke-width="1"/>'
    return elemento(w, h, s, "prova de gráfica (corte + registro + cores)", FAM,
                    nota="marcas de corte em L fora do corte (12 px), alvos de registro e a barra de cores DA marca")


def grade_pontos(f, cols=10, rows=6, passo=None, r=None, maior=None, destaque=None, cor=None, nome=None):
    """Grade de pontos no passo da unidade; `maior` = a cada N, ponto maior (grade principal)."""
    passo = passo or f.unidade * 1.5
    r = r or f.traco * 0.7
    cor = cor or mistura(f.tinta, f.fundo, 0.5)
    m = r * 3 + 2
    W, H = 2 * m + (cols - 1) * passo, 2 * m + (rows - 1) * passo
    s = ""
    for j in range(rows):
        for i in range(cols):
            rr = r * 1.9 if maior and i % maior == 0 and j % maior == 0 else r
            c = f.acento if destaque == (i, j) else cor
            if destaque == (i, j):
                rr = r * 2.6
            s += f'<circle cx="{m + i * passo:.2f}" cy="{m + j * passo:.2f}" r="{rr:.2f}" fill="{c}"/>'
    return elemento(W, H, s, nome or "grade de pontos", FAM,
                    css=f".pontos{{background:radial-gradient(circle,{cor} {r:g}px,transparent {r + 0.6:g}px) 0 0/{passo:g}px {passo:g}px}}",
                    nota=f"passo {passo:g} ({passo / f.unidade:g} U); só se o ponto significar algo (sensor, assento, vaga)")


# =====================================================================================================================
# cantoneiras, colchetes
# =====================================================================================================================
def cantoneiras(f, w=440, h=290, braco=None, r=0.0, peso=None, cor=None, quais=(0, 1, 2, 3), corte=False,
                visor=False, nome=None, nota=""):
    """Cantos de visor (L). r > 0 = a dobra do L arredondada; corte=True = marcas FORA do quadro (afastadas)."""
    t = peso or f.traco
    cor = cor or f.tinta
    braco = braco or 2 * f.unidade
    m = t / 2 + ((12 + braco * 0.6 + 2) if corte else 0)
    if visor:   # ● AO VIVO à esquerda e o timecode à direita com ≥ 3 U entre eles (antes quase se encostavam)
        u = 18.0
        precisa = (2 * braco * 0.75 + 0.84 * u + 10 + larg_rotulo(f, "AO VIVO", u, f.fonte_texto, 0.1)
                   + 3 * f.unidade + larg_rotulo(f, "20:30:00:00", u, f.fonte_mono, 0.02) + 2 * m)
        w = max(w, round(precisa))
    x0, y0, x1, y1 = m, m, w - m, h - m
    s = ""
    cantos = [(x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)]
    for k in quais:
        x, y, sx, sy = cantos[k]
        if corte:
            off = 12.0
            s += _ln(x - sx * off, y, x - sx * (off + braco * 0.6), y, cor, t) + _ln(x, y - sy * off, x, y - sy * (off + braco * 0.6), cor, t)
            continue
        rr = min(r, braco * 0.6)
        sweep = 1 if sx * sy > 0 else 0
        d = (f"M{x:.2f} {y + sy * braco:.2f}L{x:.2f} {y + sy * rr:.2f}"
             + (f"A{rr:.2f} {rr:.2f} 0 0 {sweep} {x + sx * rr:.2f} {y:.2f}" if rr else "")
             + f"L{x + sx * braco:.2f} {y:.2f}")
        s += _pl(d, cor, t, 'stroke-linecap="butt"')
    if corte:   # o "corte" imaginário, bem apagado, para a marca fazer sentido
        s += (f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" height="{y1 - y0:.2f}" fill="none" '
              f'stroke="{mistura(cor, f.fundo, 0.75)}" stroke-width="1" stroke-dasharray="3 5"/>')
    if visor:
        pr = 0.84 * u / 2
        gx = x0 + braco * 0.75
        gy = y0 + braco * 0.75 + u / 2
        s += f'<circle cx="{gx + pr:.2f}" cy="{gy:.2f}" r="{pr:.2f}" fill="{f.acento}"/>'
        a, _ = rotulo(f, "AO VIVO", gx + 2 * pr + 10, gy, cor, u, f.fonte_texto, 0.1)
        b, _ = rotulo(f, "20:30:00:00", x1 - braco * 0.75, gy, cor, u, f.fonte_mono, 0.02, "end")
        s += a + b + _cruz(w / 2, h / 2, 12, mistura(cor, f.fundo, 0.4), t * 0.67)
    return elemento(w, h, s, nome or "cantoneiras", FAM,
                    nota=nota or f"braço {braco:g} (2 U); enquadra UMA coisa; nunca em todo cartão")


def colchetes(f, w=440, h=200, tipo="reto", cor=None, txt=None, nome=None):
    """Colchetes que enquadram uma palavra/área. tipo: reto · curvo (parênteses) · fonte (glifo da display) · grupo."""
    t = f.traco
    cor = cor or f.tinta
    s = ""
    nota = ""
    if tipo == "reto":
        b = h * 0.16
        s += _pl(f"M{b + t:.2f} {t:.2f}H{t:.2f}V{h - t:.2f}H{b + t:.2f}", cor, 2 * t)
        s += _pl(f"M{w - b - t:.2f} {t:.2f}H{w - t:.2f}V{h - t:.2f}H{w - b - t:.2f}", cor, 2 * t)
        nota = "[ ] desenhados no fio grosso; braço = 16% da altura"
    elif tipo == "curvo":
        b = h * 0.16
        s += _pl(f"M{b + 2:.2f} {t:.2f}Q{t:.2f} {h / 2:.2f} {b + 2:.2f} {h - t:.2f}", cor, 2 * t)
        s += _pl(f"M{w - b - 2:.2f} {t:.2f}Q{w - t:.2f} {h / 2:.2f} {w - b - 2:.2f} {h - t:.2f}", cor, 2 * t)
        nota = "( ) em curva única: aparte, comentário"
    if txt:
        capx = min(h * 0.38, 70)
        a, _ = rotulo(f, txt, w / 2, h / 2, cor, capx, f.fonte_display, 0.02, "middle")
        s += a
    if tipo == "fonte":
        spec = f.fonte_display
        capx = h * 0.42
        wb1 = largura(spec, "[", corpo(spec, 1) * 1.55)
        wt1 = larg_rotulo(f, txt or "AO VIVO", 1.0, spec, 0.02)
        capx = min(capx, (w - 24) / (wt1 + 2 * wb1))          # colchetes + palavra cabem na largura
        sz = corpo(spec, capx)
        palavra = txt or "AO VIVO"
        a, wt = rotulo(f, palavra, w / 2, h / 2, cor, capx, spec, 0.02, "middle")
        szb = sz * 1.55
        lb, _ = texto(spec, "[", szb, 0, 0, f.acento)
        rb, _ = texto(spec, "]", szb, 0, 0, f.acento)
        # alinhado pela TINTA: o centro do colchete = o centro da maiúscula (antes o glifo "[" desce abaixo da
        # linha de base e o par ficava ~8 px mais baixo que a palavra); vão colchete↔palavra = 0,18 × maiúscula
        from .formas import caixa_texto
        ix0, _, ix1, _ = caixa_texto(spec, palavra, sz, w / 2 - wt / 2, 0, 0.02)
        lx0, ly0, lx1, ly1 = caixa_texto(spec, "[", szb)
        rx0, _, rx1, _ = caixa_texto(spec, "]", szb)
        yb = h / 2 - (ly0 + ly1) / 2
        vao = capx * 0.18
        s = a + lb.replace("<path ", f'<path transform="translate({ix0 - vao - lx1:.2f} {yb:.2f})" ') \
            + rb.replace("<path ", f'<path transform="translate({ix1 + vao - rx0:.2f} {yb:.2f})" ')
        nota = "colchetes DA fonte display (nunca de outra fonte), 1,5× a palavra; centrados na maiúscula pela tinta"
    if tipo == "grupo":
        # os DOIS colchetes com a mesma altura (da maiúscula da 1ª linha − respiro até a base da última + respiro)
        # e o mesmo braço; a caixa abraça o grupo (antes o "[" ia do topo ao pé da caixa e o "]" era mais curto)
        capx, pad, lh, arm = 22.0, 12.0, 50.0, 14.0
        y_ini, y_fim = t / 2, t / 2 + 2 * pad + capx + 2 * lh
        h = y_fim + t / 2
        x = t / 2
        s += _pl(f"M{x + arm:.2f} {y_ini:.2f}H{x:.2f}V{y_fim:.2f}H{x + arm:.2f}", cor, t)
        ys = [y_ini + pad + capx / 2 + k * lh for k in range(3)]
        wmax = 0.0
        for k, yy in enumerate(ys):
            a, wk = rotulo(f, f"NOITE {k + 1}", x + 34, yy, cor, capx, f.fonte_texto, 0.1)
            wmax = max(wmax, wk)
            s += a
        xb = x + 34 + wmax + 20                     # "]" a 20 px da linha mais longa
        cy = (y_ini + y_fim) / 2
        a, _ = rotulo(f, "3 NOITES", w - 4, cy, f.acento, capx, f.fonte_texto, 0.1, "end")
        wl = larg_rotulo(f, "3 NOITES", capx, f.fonte_texto, 0.1)
        s += a + _ln(xb, cy, w - 4 - wl - 14, cy, f.acento, t)
        s += _pl(f"M{xb - arm:.2f} {y_ini:.2f}H{xb:.2f}V{y_fim:.2f}H{xb - arm:.2f}", f.acento, t)
        nota = "agrupador: colchete junta itens e aponta o total (fio no acento); os 2 colchetes da mesma altura"
    return elemento(w, h, s, nome or f"colchetes · {tipo}", FAM, nota=nota)


# =====================================================================================================================
# callouts, listas
# =====================================================================================================================
def callout(f, tipo="reto", cor=None, nome=None):
    """Legenda técnica com fio: ponto (3× fio) → fio a 0/90° (ou no ângulo da ficha) → rótulo alinhado."""
    t = f.traco
    cor = cor or f.tinta
    s = ""
    w, h = 440.0, 220.0
    pr = 1.5 * t + 0.5
    if tipo == "reto":
        px, py = 30.0, h / 2
        s += f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr * 1.3:.2f}" fill="{f.acento}"/>'
        s += _ln(px, py, 250, py, cor, t)
        a, wt = rotulo(f, "AO VIVO", 268, py, cor, CAP, f.fonte_texto, 0.1)
        s += a
        w = 268 + wt + 4
        nota = "ponto → fio horizontal → rótulo; o fio para a 0,75 U da tinta"
    elif tipo == "cotovelo":
        px, py = 40.0, h - 40
        ang = math.radians(-45)
        kx, ky = px + 90 * math.cos(ang), py + 90 * math.sin(ang)
        s += f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr * 3:.2f}" fill="none" stroke="{f.acento}" stroke-width="{t:.2f}"/>'
        s += f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr:.2f}" fill="{f.acento}"/>'
        s += _pl(polilinha([(px + pr * 3 * math.cos(ang), py + pr * 3 * math.sin(ang)), (kx, ky), (260, ky)]), cor, t)
        a, wt = rotulo(f, "20H30", 278, ky, cor, CAP, f.fonte_mono, 0.04)
        s += a
        w = 278 + wt + 4
        nota = "alvo (anel) + cotovelo a 45° + horizontal: aponta para um detalhe da foto"
    elif tipo == "coluna":
        pts = [(70, 50), (150, 120), (40, 185)]
        labs = ["AO VIVO", "20H30", "3 NOITES"]
        lx = 290
        wmax = 0.0
        for (px, py), lb in zip(pts, labs):
            s += f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr * 1.2:.2f}" fill="{f.acento}"/>'
            s += _ln(px, py, lx - 14, py, mistura(cor, f.fundo, 0.25), t * 0.67)
            a, wk = rotulo(f, lb, lx, py, cor, 20, f.fonte_texto, 0.1)
            wmax = max(wmax, wk)
            s += a
        w = lx + wmax + 4
        nota = "várias legendas: rótulos numa COLUNA só, fios paralelos (2–5 legendas)"
    else:   # pílula
        px, py = 36.0, h / 2 + 30
        s += f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr * 1.3:.2f}" fill="{cor}"/>'
        qx, qy = 150.0, h / 2 - 40
        s += _pl(polilinha([(px, py), (qx, py), (qx, qy), (210, qy)]), cor, t)
        capx = 20.0
        wt = larg_rotulo(f, "3 NOITES", capx, f.fonte_texto, 0.1)
        ph = capx + 24
        s += f'<path d="{p_cantos(210, qy - ph / 2, wt + capx * 2.2, ph, ph / 2)}" fill="{f.acento}"/>'
        a, _ = rotulo(f, "3 NOITES", 210 + capx * 1.1, qy, f.sobre_acento, capx, f.fonte_texto, 0.1)
        s += a
        w = 210 + wt + capx * 2.2 + 4
        nota = "fio em degrau (0/90°, cantos vivos) terminando numa pílula de acento"
    return elemento(w, h, s, nome or f"callout · {tipo}", FAM, nota=nota)


def lista(f, tipo="traco", itens=("NOITE 1 · 20H30", "NOITE 2 · 20H30", "NOITE 3 · 20H30"), cor=None):
    """Lista com marcador do sistema: traço curto no acento (FennerLab), numeração 01/02 ou quadrado."""
    t = f.traco
    cor = cor or f.tinta
    capx = 22.0
    lh = capx * 2.4
    w = 440.0
    s = ""
    for k, it in enumerate(itens):
        cy = lh / 2 + k * lh
        if tipo == "traco":
            s += _ln(0, cy, f.unidade, cy, f.acento, 2 * t)
            a, _ = rotulo(f, it, f.unidade * 1.75, cy, cor, capx, f.fonte_texto, 0.08)
        elif tipo == "numero":
            n, wn = rotulo(f, f"{k + 1:02d}", 0, cy, f.acento, capx, f.fonte_mono, 0.02)
            a, _ = rotulo(f, it, wn + f.unidade, cy, cor, capx, f.fonte_texto, 0.08)
            a = n + a
            if k < len(itens) - 1:
                s += _ln(0, cy + lh / 2, w, cy + lh / 2, mistura(cor, f.fundo, 0.65), t * 0.67)
        else:
            q = capx * 0.62
            s += f'<rect x="{t / 2:.2f}" y="{cy - q / 2:.2f}" width="{q:.2f}" height="{q:.2f}" fill="{"none" if k else f.acento}" stroke="{f.acento}" stroke-width="{t:.2f}"/>'
            a, _ = rotulo(f, it, q + f.unidade * 0.9, cy, cor, capx, f.fonte_texto, 0.08)
        s += a
    nomes = {"traco": "lista · traço no acento", "numero": "lista · 01/02/03 + fios", "quadrado": "lista · quadrado (feito/a fazer)"}
    notas = {"traco": "marcador = traço curto grosso no acento; recuo = 1,75 U",
             "numero": "números mono no acento + fio fino entre itens (tabular)",
             "quadrado": "quadrado cheio = já aconteceu / atual; vazio = próximo"}
    return elemento(w, lh * len(itens), s, nomes[tipo], FAM, nota=notas[tipo])


# =====================================================================================================================
# setas e cotas
# =====================================================================================================================
def seta(f, tipo="reta", cor=None, cheia=False, nome=None):
    """Setas do sistema: ponta aberta a 45° (ou cheia), haste = fio. reta · dupla · cotovelo · curva · retorno ·
    angulo (no ângulo da ficha) · fonte (o glifo → da display)."""
    t = 2 * f.traco
    cor = cor or f.tinta
    tam = t * 3.2
    s = ""
    w, h = 440.0, 160.0
    if tipo == "reta":
        s = _ln(0, h / 2, w - (t if not cheia else tam * 0.7), h / 2, cor, t) + ponta(w - t * 0.7, h / 2, 0, tam, cor, t, cheia)
        nota = "ponta " + ("cheia" if cheia else "aberta a 45°") + f"; haste = fio grosso ({t:g})"
    elif tipo == "dupla":
        s = _ln(t, h / 2, w - t, h / 2, cor, t) + ponta(w - t * 0.7, h / 2, 0, tam, cor, t) + ponta(t * 0.7, h / 2, 180, tam, cor, t)
        nota = "ida e volta / intervalo"
    elif tipo == "cotovelo":
        r = f.raio_lg
        x0, y0, x1, y1 = 40.0, 8.0, w - t, h - 30
        s = _pl(f"M{x0:.2f} {y0:.2f}V{y1 - r:.2f}A{r:.2f} {r:.2f} 0 0 0 {x0 + r:.2f} {y1:.2f}H{x1 - t * 0.6:.2f}", cor, t)
        s += ponta(x1 - t * 0.7, y1, 0, tam, cor, t)
        nota = f"cotovelo no raio lg da escala ({r:g}); desce e segue (leitura em L)"
    elif tipo == "curva":
        x0, y0, x1, y1 = 10.0, h - 20, w - 40, 30.0
        s = _pl(f"M{x0:.2f} {y0:.2f}C{w * 0.45:.2f} {y0:.2f} {w * 0.55:.2f} {y1:.2f} {x1 - t:.2f} {y1:.2f}", cor, t)
        s += ponta(x1 - t * 0.6, y1, 0, tam, cor, t)
        nota = "curva-S com tangente horizontal nas pontas: 'passa para o próximo'"
    elif tipo == "retorno":
        cx, cy, r = w / 2, h / 2 + 4, 56.0
        a0, a1 = math.radians(150), math.radians(150 + 285)
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        da = tam * 0.9 / r                                   # trecho do arco "coberto" pela ponta
        ae = a1 - (t * 0.6) / r                              # o arco para um pouco antes do vértice
        pe = (cx + r * math.cos(ae), cy + r * math.sin(ae))
        s = _pl(f"M{p0[0]:.2f} {p0[1]:.2f}A{r:.2f} {r:.2f} 0 1 1 {pe[0]:.2f} {pe[1]:.2f}", cor, t, 'stroke-linecap="butt"')
        s += ponta(p1[0], p1[1], math.degrees(a1 - da / 2) + 90, tam, cor, t)
        nota = "giro de 285°: repetição, 'toda noite', ciclo"
    elif tipo == "angulo":
        a = f.angulo
        L = w - 20
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        x0, y0 = 10.0, h / 2 - sa * L / 2
        x1, y1 = x0 + ca * L, y0 + sa * L
        s = _ln(x0, y0, x1 - ca * t * 0.7, y1 - sa * t * 0.7, cor, t) + ponta(x1, y1, a, tam, cor, t)
        nota = f"no ângulo da ficha ({a:g}°): faixas, carimbo e seta inclinam igual"
    else:   # fonte
        spec = f.fonte_display
        from .formas import caixa_texto
        bx0, _, bx1, _ = caixa_texto(spec, "→", 100)
        sz = 100 * (w * 0.8) / (bx1 - bx0)
        d, wt = texto(spec, "→", sz, 0, 0, cor)
        x0, y0b, x1, y1b = caixa_texto(spec, "→", sz)
        s = d.replace("<path ", f'<path transform="translate({(w - (x1 - x0)) / 2 - x0:.2f} {h / 2 - (y0b + y1b) / 2:.2f})" ')
        nota = "a seta DA fonte display (desenho casado com as letras)"
    return elemento(w, h, s, nome or f"seta · {tipo}" + (" · cheia" if cheia else ""), FAM, nota=nota)


def cota(f, tipo="horizontal", comp=360, cor=None):
    """Cota de medida (desenho técnico): linhas de chamada + linha de cota com pontas + valor no meio, com vão."""
    t = f.traco * 0.67
    cor = cor or f.tinta
    s = ""
    capx = 18.0
    tam = 11.0
    if tipo in ("horizontal", "barras"):
        w, h = comp + 40, 110.0
        x0, x1, y = 20.0, 20.0 + comp, 64.0
        s += _ln(x0, 10, x0, y + 16, cor, t) + _ln(x1, 10, x1, y + 16, cor, t)
        val = f"{comp:g}"
        wt = larg_rotulo(f, val, capx, f.fonte_mono, 0.04)
        gap = 10.0
        mid = (x0 + x1) / 2
        s += _ln(x0, y, mid - wt / 2 - gap, y, cor, t) + _ln(mid + wt / 2 + gap, y, x1, y, cor, t)
        if tipo == "horizontal":
            s += ponta(x0, y, 180, tam, cor, t, True) + ponta(x1, y, 0, tam, cor, t, True)
        else:
            for x in (x0, x1):
                s += _ln(x - 8, y + 8, x + 8, y - 8, cor, t * 1.6)
        a, _ = rotulo(f, val, mid, y, f.acento, capx, f.fonte_mono, 0.04, "middle")
        s += a
        nota = ("cota com pontas cheias; o valor é o comprimento real (px)" if tipo == "horizontal"
                else "cota de arquitetura: traços a 45° no lugar das pontas")
    elif tipo == "vertical":
        w, h = 140.0, comp * 0.8 + 40
        y0, y1, x = 20.0, 20.0 + comp * 0.8, 40.0
        s += _ln(x - 16, y0, w, y0, cor, t) + _ln(x - 16, y1, w, y1, cor, t)
        val = f"{comp * 0.8:g}"
        a, wt = rotulo(f, val, 0, 0, f.acento, capx, f.fonte_mono, 0.04, "middle")
        mid, gap = (y0 + y1) / 2, 10.0
        s += (_ln(x, y0, x, mid - wt / 2 - gap, cor, t) + _ln(x, mid + wt / 2 + gap, x, y1, cor, t)
              + ponta(x, y0, -90, tam, cor, t, True) + ponta(x, y1, 90, tam, cor, t, True))
        s += f'<g transform="translate({x:.2f} {mid:.2f}) rotate(-90)">{a}</g>'
        nota = "cota vertical; valor deitado, lido de baixo para cima"
    elif tipo == "raio":
        # cota de raio VERDADEIRA: o canto desenhado tem o raio escrito (antes "R112" num canto que o gerador
        # prendia em 85 — número mentindo e a seta parando fora da curva)
        R = f.raio_lg
        w, h = 380.0, 230.0
        x0, y0 = 120.0, 52.0
        s += f'<path d="{p_cantos(x0, y0, 250, 170, R)}" fill="none" stroke="{mistura(cor, f.fundo, 0.45)}" stroke-width="{f.traco:.2f}"/>'
        cx, cy = x0 + R, y0 + R
        a = math.radians(225)
        px, py = cx + R * math.cos(a), cy + R * math.sin(a)
        s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="2.5" fill="{cor}"/>' + _ln(cx, cy, px, py, cor, t) + ponta(px, py, 225, tam, cor, t, True)
        lx, ly = px - 26, py - 26
        s += _ln(px, py, lx, ly, cor, t) + _ln(lx, ly, lx - 14, ly, cor, t)
        b, _ = rotulo(f, f"R{R:g}", lx - 22, ly, f.acento, capx, f.fonte_mono, 0.02, "end")
        s += b
        nota = "cota de raio (R) num canto: documenta o raio do sistema no manual"
    else:   # angulo
        w, h = 420.0, 150.0
        a = f.angulo
        x0, y0 = 20.0, 110.0
        L = 380.0
        s += _ln(x0, y0, x0 + L, y0, mistura(cor, f.fundo, 0.45), t)
        ex, ey = x0 + L * math.cos(math.radians(a)), y0 + L * math.sin(math.radians(a))
        s += _ln(x0, y0, ex, ey, cor, f.traco)
        # arco na PONTA dos fios e o valor fora da cunha, depois do arco (antes o "6°" ficava espremido entre os
        # dois fios, a 7 px de cada um — tangente)
        R = L
        ax, ay = x0 + R * math.cos(math.radians(a)), y0 + R * math.sin(math.radians(a))
        s += _pl(f"M{x0 + R:.2f} {y0:.2f}A{R:.2f} {R:.2f} 0 0 0 {ax:.2f} {ay:.2f}", f.acento, t)
        b, wb = rotulo(f, f"{abs(a):g}°", x0 + R + 14, (y0 + ay) / 2, f.acento, capx, f.fonte_texto, 0.02)
        s += b
        w = x0 + R + 14 + wb + 4
        nota = f"cota de ângulo: o ângulo do sistema ({a:g}°) como medida visível"
    return elemento(w, h, s, f"cota · {tipo}", FAM, nota=nota)


# =====================================================================================================================
# linha do tempo, numeração
# =====================================================================================================================
def linha_tempo(f, tipo="horizontal", atual=0, cor=None):
    t = f.traco
    cor = cor or f.tinta
    marcos = ["NOITE 1", "NOITE 2", "NOITE 3"]
    s = ""
    if tipo == "horizontal":
        w, h = 460.0, 130.0
        y = 58.0
        mg = larg_rotulo(f, "NOITE 1", 20, f.fonte_texto, 0.1) / 2 + 4
        xs = [mg, w / 2, w - mg]
        s += _ln(xs[0], y, xs[-1], y, mistura(cor, f.fundo, 0.5), t)
        s += _ln(xs[0], y, xs[atual], y, f.acento, t * 2) if atual else ""
        for k, x in enumerate(xs):
            if k == atual:
                s += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="12" fill="{f.acento}"/>'
            elif k < atual:
                s += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="9" fill="{cor}"/>'
            else:
                s += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="9" fill="{f.fundo}" stroke="{cor}" stroke-width="{t:.2f}"/>'
            a, _ = rotulo(f, marcos[k], x, y + 46, cor if k != atual else f.acento, 20, f.fonte_texto, 0.1, "middle")
            b, _ = rotulo(f, "20H30", x, y - 38, mistura(cor, f.fundo, 0.35), 14, f.fonte_mono, 0.04, "middle")
            s += a + b
        nota = "marco atual cheio no acento; passado cheio; futuro vazado"
    elif tipo == "vertical":
        w, h = 360.0, 300.0
        x = 22.0
        ys = [30.0, h / 2, h - 30]
        s += _ln(x, ys[0], x, ys[-1], mistura(cor, f.fundo, 0.5), t)
        for k, y in enumerate(ys):
            if k == atual:
                s += f'<rect x="{x - 12:.2f}" y="{y - 12:.2f}" width="24" height="24" fill="{f.acento}"/>'
            else:
                s += f'<rect x="{x - 8:.2f}" y="{y - 8:.2f}" width="16" height="16" fill="{f.fundo}" stroke="{cor}" stroke-width="{t:.2f}"/>'
            a, wa = rotulo(f, marcos[k], x + 34, y, cor, CAP, f.fonte_texto, 0.1)
            b, _ = rotulo(f, "20H30", x + 34 + wa + 16, y, f.acento if k == atual else mistura(cor, f.fundo, 0.4), 18, f.fonte_mono, 0.04)
            s += a + b
        nota = "vertical, marcos quadrados (raio 0): agenda, cronograma"
    else:   # segmentos
        w, h = 460.0, 80.0
        n, gap = 3, 10.0
        sw_ = (w - gap * (n - 1)) / n
        for k in range(n):
            x = k * (sw_ + gap)
            c = f.acento if k <= atual else mistura(cor, f.fundo, 0.75)
            s += f'<path d="{p_cantos(x, 16, sw_, 10, 5)}" fill="{c}"/>'      # pílula (½ da altura)
            a, _ = rotulo(f, marcos[k], x, 52, cor if k <= atual else mistura(cor, f.fundo, 0.45), 16, f.fonte_texto, 0.1)
            s += a
        nota = "progresso em 3 segmentos (1 por noite); cheio = já começou"
    return elemento(w, h, s, f"linha do tempo · {tipo}", FAM, nota=nota)


def numeracao(f, tipo="grande", n=1, total=3, cor=None):
    """Numeração de seção: 01 grande + /03 · Nº 01 · número no anel · fração 1/3 no ângulo · 001 em caixa."""
    t = f.traco
    cor = cor or f.tinta
    s = ""
    if tipo == "grande":
        spec = f.fonte_display
        capx = 150.0
        a, wa = rotulo(f, f"{n:02d}", 0, capx / 2 + 6, cor, capx, spec, 0.0)
        b, wb = rotulo(f, f"/{total:02d}", wa + 10, capx + 6 - 11, f.acento, 22, f.fonte_mono, 0.02)
        s = a + b
        w, h = wa + 10 + wb + 4, capx + 12
        nota = "numeral display + total mono alinhado na BASE (não no meio)"
    elif tipo == "no":
        a, wa = rotulo(f, f"Nº {n:02d}", 0, 30, cor, CAP, f.fonte_mono, 0.04)
        s = a + _ln(0, 62, wa, 62, f.acento, 2 * t)
        w, h = wa, 66.0
        nota = "Nº + 2 dígitos, sublinhado no grosso: edição/turma/noite"
    elif tipo == "anel":
        r = 56.0
        s = f'<circle cx="{r + t:.2f}" cy="{r + t:.2f}" r="{r:.2f}" fill="none" stroke="{cor}" stroke-width="{t:.2f}"/>'
        # número centrado pela TINTA no anel (o "1" tem bandeira à esquerda: pela largura de avanço ficava torto)
        from .formas import caixa_texto
        spec = f.fonte_display
        sz = corpo(spec, r * 0.95)
        ix0, iy0, ix1, iy1 = caixa_texto(spec, str(n), sz)
        a, _ = texto(spec, str(n), sz, r + t - (ix0 + ix1) / 2, r + t - (iy0 + iy1) / 2, cor)
        s += a
        w = h = 2 * (r + t)
        nota = "número no anel: etapa, passo de um processo"
    elif tipo == "fracao":
        spec = f.fonte_display
        capx = 110.0
        a, wa = rotulo(f, str(n), 0, capx / 2, cor, capx, spec, 0)
        # barra a 12 px da TINTA do numerador (antes encostava no pé do "1") e denominador a 14 px da barra
        from .formas import caixa_texto
        _, _, ix1, _ = caixa_texto(spec, str(n), corpo(spec, capx))
        xb0 = ix1 + 12                                       # pé da barra (embaixo, à esquerda)
        s = a + _ln(xb0, capx + 4, xb0 + 44, -4, f.acento, 2 * t)
        cd = capx * 0.45
        x_den = xb0 + 44 * (capx + 4 - (capx - cd)) / (capx + 8) + 14
        dx0, _, _, _ = caixa_texto(spec, str(total), corpo(spec, cd))
        b, wb = rotulo(f, str(total), x_den - dx0, capx - cd / 2, cor, cd, spec, 0)
        s += b
        w, h = x_den - dx0 + wb + 4, capx + 20
        s = f'<g transform="translate(0 10)">{s}</g>'
        nota = "fração 1/3 com a barra no acento: 'noite 1 de 3'"
    else:   # caixa
        a, wa = rotulo(f, f"{n:03d}", 14, 26, f.fundo, 22, f.fonte_mono, 0.06)
        s = f'<rect x="0" y="0" width="{wa + 28:.2f}" height="52" fill="{cor}"/>' + a
        b, wb = rotulo(f, "NOITE", wa + 28 + 14, 26, cor, 22, f.fonte_texto, 0.12)
        s += b + f'<rect x="{t / 2:.2f}" y="{t / 2:.2f}" width="{wa + 28 + 14 + wb + 14 - t:.2f}" height="{52 - t:.2f}" fill="none" stroke="{cor}" stroke-width="{t:.2f}"/>'
        w, h = wa + 28 + 14 + wb + 14, 52.0
        nota = "001 em bloco + rótulo: etiqueta de arquivo (raio 0)"
    return elemento(w, h, s, f"numeração · {tipo}", FAM, nota=nota)


# =====================================================================================================================
# amostras
# =====================================================================================================================
@amostra(FAM, "fios")
def _a_fios(f):
    fc = claro(f)
    return [fio(f, tipo="fino"), fio(f, tipo="grosso"), fio(f, tipo="filete"), fio(f, tipo="ponto"),
            fio(f, tipo="tracejado", cor=f.acento), no_claro(fio(fc, tipo="barras"))]


@amostra(FAM, "divisórias")
def _a_div(f):
    fc = claro(f)
    return [divisoria(f, tipo="rotulo"), divisoria(f, "3 NOITES", tipo="centro"), divisoria(f, "20H30", tipo="pilula"),
            divisoria(f, "PÓS-GRADUAÇÃO", tipo="barra"), no_claro(divisoria(fc, "NOITE 1", tipo="sublinhado"))]


@amostra(FAM, "réguas")
def _a_reguas(f):
    fc = claro(f)
    return [
        regua(f, 460, 0, 100, 1, 5, 10, 20, "{:g}", nome="régua 0–100", nota="escala de %: 101 traços, número a cada 20"),
        regua(f, 460, 18, 24, 1 / 6, 0.5, 1, 1, "{:g}H", cursor=20.5, cursor_txt="20H30",
              nome="régua de horário 18H–24H", nota="1 traço a cada 10 min; cursor no acento na hora REAL (20H30)"),
        no_claro(regua(fc, 460, 0, 50, 1, 5, 10, 10, "{:g}", nome="régua 0–50 · papel",
                       nota="sobre papel, tinta escura; números = micrográfico (textura)")),
        regua(f, 330, 0, 30, 1, 5, 10, 10, "{:g}", vertical=True, nome="régua vertical",
              nota="margem de peça, lateral de tela; números lidos de cima para baixo"),
        regua_canto(f),
    ]


@amostra(FAM, "cruzes e registro")
def _a_cruzes(f):
    fc = claro(f)
    return [
        cruzes(f, 6, 4),
        cruzes(f, 6, 4, destaque=(3, 1), nome="cruzes · 1 no acento"),
        cruzes(f, 7, 5, passo=2 * f.unidade, tipo="alterna", nome="cruzes e pontos alternados"),
        no_claro(cruzes(fc, 6, 4, coords=True, cor=mistura(fc.tinta, fc.fundo, 0.35), nome="cruzes + coordenadas · papel")),
        prova_grafica(f),
    ]


@amostra(FAM, "grade de pontos")
def _a_pontos(f):
    fc = claro(f)
    return [grade_pontos(f), grade_pontos(f, 13, 9, passo=f.unidade, maior=4, nome="pontos · principal a cada 4"),
            grade_pontos(f, destaque=(6, 2), nome="pontos · 1 no acento"),
            no_claro(grade_pontos(fc, cor=mistura(fc.tinta, fc.fundo, 0.4), nome="pontos · papel"))]


@amostra(FAM, "cantoneiras")
def _a_cantos(f):
    fc = claro(f)
    return [
        cantoneiras(f, nome="cantoneiras retas"),
        cantoneiras(f, r=f.raio, cor=f.acento, nome=f"cantoneiras · dobra raio {f.raio:g}",
                    nota="L com a dobra arredondada no raio da ficha; acento = 'medido'"),
        cantoneiras(f, visor=True, nome="visor ao vivo", nota="● AO VIVO + timecode 20:30:00:00 (hora real) + mira central"),
        cantoneiras(f, quais=(0, 2), peso=2 * f.traco, braco=3 * f.unidade, nome="2 cantos diagonais · grosso",
                    nota="enquadra sem fechar; 2 cantos opostos bastam"),
        no_claro(cantoneiras(fc, corte=True, nome="marcas de corte · papel",
                             nota="L FORA do quadro, afastadas 12 px: 'prova de impressão'")),
        cantoneiras(f, r=f.raio_sm, braco=f.unidade * 1.2, peso=2 * f.traco,
                    nome=f"cantos curtos grossos · raio {f.raio_sm:g}",
                    nota="braço 1,2 U, grosso, dobra no raio sm (o raio cabe no braço): moldura de ícone/avatar"),
    ]


@amostra(FAM, "colchetes")
def _a_colchetes(f):
    return [colchetes(f, tipo="reto", txt="AO VIVO"), colchetes(f, tipo="curvo", cor=f.acento, txt="20H30"),
            colchetes(f, tipo="fonte", txt="3 NOITES"), colchetes(f, 440, 200, tipo="grupo")]


@amostra(FAM, "callouts")
def _a_callouts(f):
    return [callout(f, "reto"), callout(f, "cotovelo"), callout(f, "coluna"), callout(f, "pilula")]


@amostra(FAM, "listas")
def _a_listas(f):
    fc = claro(f)
    return [lista(f, "traco"), lista(f, "numero"), no_claro(lista(fc, "quadrado"))]


@amostra(FAM, "setas")
def _a_setas(f):
    return [seta(f, "reta"), seta(f, "reta", cheia=True, cor=f.acento), seta(f, "dupla"), seta(f, "cotovelo"),
            seta(f, "curva", cor=f.acento), seta(f, "retorno"), seta(f, "angulo"), seta(f, "fonte")]


@amostra(FAM, "cotas")
def _a_cotas(f):
    fc = claro(f)
    return [cota(f, "horizontal"), no_claro(cota(fc, "barras", 300)), cota(f, "vertical", 300), cota(f, "raio"),
            cota(f, "angulo")]


@amostra(FAM, "linha do tempo")
def _a_tempo(f):
    return [linha_tempo(f, "horizontal", 0), linha_tempo(f, "vertical", 1), linha_tempo(f, "segmentos", 0)]


@amostra(FAM, "numeração")
def _a_num(f):
    fc = claro(f)
    return [numeracao(f, "grande"), numeracao(f, "no"), numeracao(f, "anel", cor=f.acento), numeracao(f, "fracao"),
            no_claro(numeracao(fc, "caixa", 1))]
