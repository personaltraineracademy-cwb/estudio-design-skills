"""ornamentos.faixas — família FAIXAS, LISTRAS E SINAIS (superfície, ritmo, herói tipográfico).

Origem (references/elementos.md "12 famílias", "Tipografia como imagem"; pesquisa 11 E03, E10, E36, E39, E40, E46,
E47, E52, E102; 1 M05):
  - faixa: ângulo e largura fixos no sistema (o da ficha), sangra em 2 bordas, carrega texto; listras 1:1 ou 1:2;
  - bolinhas/listras como sistema: tamanho e passo fixos; nunca bolinhas de vários tamanhos soltas;
  - tarja: texto VAZADO (o fundo aparece pela letra) com a família de raios 0 · ficha · 2× · pílula;
  - sinal gigante: glifo DA fonte display (nunca de outra), ≥ 60% da altura, cortado 15–40% pela borda, contorno
    por fora (2,5–4% do corpo), eco de 3–5 cópias com passo de 4–8% da altura, fatiado em 3–7 tiras.
Textos só do cliente; nada de "OFERTA"/preço inventado.
"""
import math

from .nucleo import amostra, elemento
from .formas import (rotulo, larg_rotulo, mistura, claro, no_claro, corpo, caixa_texto, path_texto, p_cantos, uid)

FAM = "faixas"


# =====================================================================================================================
# utilitários
# =====================================================================================================================
def _clip(id_, d):
    return f'<clipPath id="{id_}"><path d="{d}"/></clipPath>'


def _rect_d(w, h):
    return f"M0 0H{w:.2f}V{h:.2f}H0Z"


def _sep(tipo, x, cy, tam, cor):
    """Separador DESENHADO entre repetições (não depende da fonte)."""
    if tipo == "losango":
        r = tam * 0.5
        return f'<path d="M{x:.2f} {cy - r:.2f}L{x + r:.2f} {cy:.2f}L{x:.2f} {cy + r:.2f}L{x - r:.2f} {cy:.2f}Z" fill="{cor}"/>'
    if tipo == "ponto":
        return f'<circle cx="{x:.2f}" cy="{cy:.2f}" r="{tam * 0.32:.2f}" fill="{cor}"/>'
    if tipo == "barra":
        a = math.radians(-70)
        dx, dy = math.cos(a) * tam * 0.62, math.sin(a) * tam * 0.62
        return (f'<line x1="{x - dx:.2f}" y1="{cy - dy:.2f}" x2="{x + dx:.2f}" y2="{cy + dy:.2f}" stroke="{cor}" '
                f'stroke-width="{tam * 0.16:.2f}"/>')
    if tipo == "seta":
        r = tam * 0.45
        return (f'<path d="M{x - r:.2f} {cy:.2f}H{x + r * 0.6:.2f}M{x + r * 0.05:.2f} {cy - r * 0.55:.2f}L{x + r * 0.6:.2f} {cy:.2f}'
                f'L{x + r * 0.05:.2f} {cy + r * 0.55:.2f}" fill="none" stroke="{cor}" stroke-width="{tam * 0.14:.2f}"/>')
    return ""


def _encaixe(f, txt, a, b, cy, capx, cor, spec, sep, tracking=0.06, alterna=False, sw=None, k0=0):
    """Texto repetido que CABE inteiro no trecho [a, b] da faixa: n repetições, o vão é ajustado para fechar a conta e
    cada ponta do trecho cai no MEIO de um vão de separador (o separador da ponta não é desenhado) → nenhuma letra
    cortada pela borda nem pelo cruzamento com outra faixa (D8/D15). Devolve (svg, n)."""
    L = b - a
    tw = larg_rotulo(f, txt, capx, spec, tracking)
    stam = capx * 0.55
    g0 = capx * 0.75
    melhor = None
    for n in range(1, max(2, int(L / (tw + stam)) + 2)):
        g = (L / n - tw - stam) / 2
        if g < capx * 0.45:
            break
        if n == 1 or g <= capx * 1.4:
            if melhor is None or abs(g - g0) < abs(melhor[1] - g0):
                melhor = (n, g)
    if melhor is None:
        return "", 0
    n, g = melhor
    unid = tw + 2 * g + stam
    s = ""
    for i in range(n):
        x = a + g + stam / 2 + i * unid
        t_, _ = rotulo(f, txt, x, cy, cor, capx, spec, tracking)
        if alterna and (i + k0) % 2:
            t_ = t_.replace(f'fill="{cor}"', f'fill="none" stroke="{cor}" stroke-width="{sw or capx * 0.045:.2f}"')
        s += t_
        if i < n - 1:
            s += _sep(sep, x + tw + g + stam / 2, cy, stam, cor)
    return s, n


def _cap_para_n(f, txt, L, hb, spec, tracking, n_min=2, lo=0.34, hi=0.46):
    """Corpo (maiúscula, em fração `lo`–`hi` da altura da faixa) em que o texto se repete ao menos `n_min` vezes
    com vão confortável (0,45–1,4 × o corpo, ideal 0,75). Um marquee com UMA palavra só parece etiqueta."""
    melhor = None
    c = hi
    while c >= lo - 1e-9:
        capx = hb * c
        tw = larg_rotulo(f, txt, capx, spec, tracking)
        stam = capx * 0.55
        for n in range(n_min, 7):
            g = (L / n - tw - stam) / 2
            if capx * 0.45 <= g <= capx * 1.4:
                sc = abs(g - capx * 0.75)
                if melhor is None or sc < melhor[0]:
                    melhor = (sc, capx)
        c -= 0.01
    return melhor[1] if melhor else hb * 0.38


def _repete(f, txt, L, cy, capx, cor, spec, sep, tracking=0.06, fase=0.35, alterna=False, sw=None, x_ini=None):
    """Texto repetido ao longo de [−L/2, L/2] na linha cy, com separador desenhado; fase = onde o ciclo começa."""
    tw = larg_rotulo(f, txt, capx, spec, tracking)
    gap = capx * 0.75
    stam = capx * 0.55
    unid = tw + 2 * gap + stam
    x = (x_ini if x_ini is not None else -L / 2) - fase * unid
    s, k = "", 0
    while x < L / 2 + unid:
        t, _ = rotulo(f, txt, x, cy, cor, capx, spec, tracking)
        if alterna and k % 2:
            t = t.replace(f'fill="{cor}"', f'fill="none" stroke="{cor}" stroke-width="{sw or capx * 0.045:.2f}"')
        s += t + _sep(sep, x + tw + gap + stam / 2, cy, stam, cor)
        x += unid
        k += 1
    return s


# =====================================================================================================================
# faixas com texto
# =====================================================================================================================
def _visivel(w, h, ang):
    """Comprimento da linha de centro de uma faixa (pelo centro do quadro, no ângulo `ang`) que fica dentro de w × h."""
    a = math.radians(abs(ang))
    c, s = math.cos(a), math.sin(a)
    return min(w / c if c > 1e-6 else 1e9, h / s if s > 1e-6 else 1e9)


def faixa_texto(f, w=480, h=300, txt="AO VIVO", sep="losango", ang=None, cor=None, tinta=None, hb=None,
                isolamento=False, alterna=False, spec=None, nome=None, nota="", vaos=()):
    """Faixa inclinada (ângulo da ficha) que sangra nas 2 bordas, com texto repetido e separador desenhado. O texto
    CABE no trecho visível (nenhuma letra cortada pela borda); `vaos` = trechos (centro, meia-largura) da linha de
    centro onde não entra texto (ex.: onde outra faixa passa por cima)."""
    ang = f.angulo if ang is None else ang
    cor = cor or f.acento
    tinta = tinta or (f.sobre_acento if cor == f.acento else f.fundo)
    hb = hb or f.unidade * 3
    spec = spec or f.fonte_display
    L = math.hypot(w, h) + 2 * hb
    s = f'<rect x="{-L / 2:.2f}" y="{-hb / 2:.2f}" width="{L:.2f}" height="{hb:.2f}" fill="{cor}"/>'
    capx = hb * 0.40
    if isolamento:
        e = hb * 0.17
        hz = ""
        p = e * 1.6
        x = -L / 2
        while x < L / 2:
            for yy in (-hb / 2, hb / 2 - e):
                hz += f'<path d="M{x:.2f} {yy + e:.2f}L{x + e:.2f} {yy:.2f}L{x + e + p / 2:.2f} {yy:.2f}L{x + p / 2:.2f} {yy + e:.2f}Z" fill="{tinta}"/>'
            x += p
        s += hz
        capx = (hb - 2 * e) * 0.46
    # trecho visível da linha de centro, menos a inclinação da letra na borda (a borda do quadro é vertical/horizontal)
    Lv = _visivel(w, h, ang) - 2 * capx * abs(math.tan(math.radians(ang)))
    corte = [(-Lv / 2, Lv / 2)]
    for c0, mw in sorted(vaos):
        novo = []
        for a0, b0 in corte:
            if c0 + mw <= a0 or c0 - mw >= b0:
                novo.append((a0, b0))
            else:
                novo += [x for x in ((a0, c0 - mw), (c0 + mw, b0)) if x[1] - x[0] > 1]
        corte = novo
    k = 0
    for a0, b0 in corte:
        txt_svg, n = _encaixe(f, txt, a0, b0, 0, capx, tinta, spec, sep, 0.04 if spec == f.fonte_display else 0.12,
                              alterna=alterna, k0=k)
        s += txt_svg
        k += n
    cid = uid("faixa", w, h, txt, ang, cor)
    corpo_svg = (f'<g clip-path="url(#{cid})"><g transform="translate({w / 2:.2f} {h / 2:.2f}) rotate({ang:.2f})">'
                 f'{s}</g></g>')
    return elemento(w, h, corpo_svg, nome or f"faixa · {txt.lower()}", FAM, defs=_clip(cid, _rect_d(w, h)),
                    nota=nota or f"inclinada no ângulo da ficha ({ang:g}°), sangra nas 2 bordas; separador desenhado")


def faixas_cruzadas(f, w=480, h=300, ang=None):
    """Duas fitas que se cruzam no ângulo da ficha e no espelho dele (± ângulo)."""
    ang = f.angulo if ang is None else ang
    hb = 58.0
    th = math.radians(abs(2 * ang * 2.5))            # ângulo entre as fitas
    capx = hb * 0.40
    # a fita de cima esconde, na linha de centro da de baixo, ±(hb/2)/sen θ — mais a inclinação da maiúscula e folga:
    # o texto da fita de baixo PARA antes do cruzamento (nada de palavra pela metade sumindo embaixo da outra)
    mw = (hb / 2) / math.sin(th) + (capx / 2) / math.tan(th) + capx * 0.3
    a = faixa_texto(f, w, h, "AO VIVO", "ponto", ang=-ang * 2.5, cor=f.tinta, hb=hb, vaos=[(0.0, mw)])
    b = faixa_texto(f, w, h, "20H30", "losango", ang=ang * 2.5, hb=hb, spec=f.fonte_mono)
    import re
    def miolo(el):
        return re.sub(r"^<svg[^>]*>", "", el.svg).replace("</svg>", "")
    corpo_svg = miolo(a) + miolo(b)
    el = elemento(w, h, corpo_svg, "fitas cruzadas (± ângulo)", FAM,
                  nota=f"duas fitas em ±{abs(ang * 2.5):g}° (2,5 × o ângulo da ficha): fecha/abre algo; 1 por série")
    el.svg = el.svg  # defs já vêm dentro de cada miolo
    return el


def marquee(f, w=520, txt="AO VIVO", tipo="simples", nome=None):
    """Faixa rolante estática (marquee): sangra dos 2 lados; no site anda 40–60 px/s."""
    hb = f.unidade * 2.6
    s = ""
    H = hb
    if tipo == "simples":
        s += f'<rect x="{-w / 2:.2f}" width="{w}" height="{hb:.2f}" fill="{f.tinta}"/>'
        cap_ = _cap_para_n(f, txt, w, hb, f.fonte_texto, 0.12)
        s += _encaixe(f, txt, -w / 2, w / 2, hb / 2, cap_, f.fundo, f.fonte_texto, "seta", 0.12)[0]
        s = f'<g transform="translate({w / 2:.2f} 0)">{s}</g>'
        nota = "1 faixa, texto + seta desenhada; o texto cabe inteiro (a faixa é que sangra); no site anda"
    elif tipo == "dupla":
        H = 2 * hb + 10
        s += f'<rect x="{-w / 2:.2f}" width="{w}" height="{hb:.2f}" fill="{f.acento}"/>'
        s += _encaixe(f, "3 NOITES", -w / 2, w / 2, hb / 2, hb * 0.40, f.sobre_acento, f.fonte_display, "losango", 0.03)[0]
        s += f'<rect x="{-w / 2 - 4:.2f}" y="{hb + 10 + f.traco / 2:.2f}" width="{w + 8}" height="{hb - f.traco:.2f}" fill="none" stroke="{f.tinta}" stroke-width="{f.traco:.2f}"/>'
        s += _encaixe(f, "20H30", -w / 2, w / 2, hb * 1.5 + 10, hb * 0.36, f.tinta, f.fonte_mono, "ponto", 0.06)[0]
        s = f'<g transform="translate({w / 2:.2f} 0)">{s}</g>'
        nota = "2 faixas em sentidos opostos (no site): cheia + contorno, texto inteiro nas 2"
    else:   # letreiro: a palavra INTEIRA na largura, maior que a faixa — corte decidido de 18% em cima e embaixo
        cid = uid("letreiro", w, txt)
        spec = f.fonte_display
        # a PALAVRA cabe na largura (com meia faixa de respiro de cada lado) e o corte é SEMPRE de 18% (≥ 15%, D25);
        # quem se ajusta é a altura da faixa: hb = 0,64 × a maiúscula
        x0, y0, x1, y1 = caixa_texto(spec, txt, corpo(spec, 100.0), 0, 0, 0.02)
        r1 = (x1 - x0) / 100.0                              # largura da tinta por 1 px de maiúscula
        capx = w / (r1 + 0.64)
        hb = capx * 0.64
        H = hb
        sz = corpo(spec, capx)
        x0, y0, x1, y1 = caixa_texto(spec, txt, sz, 0, 0, 0.02)
        d, _ = path_texto(spec, txt, sz, w / 2 - (x0 + x1) / 2, hb / 2 + capx / 2, 0.02)
        s += f'<rect width="{w}" height="{hb:.2f}" fill="{f.acento}"/><path d="{d}" fill="{f.sobre_acento}"/>'
        corte = (capx - hb) / 2 / capx
        return elemento(w, H, f'<g clip-path="url(#{cid})">{s}</g>', "marquee · letreiro cortado", FAM,
                        defs=_clip(cid, _rect_d(w, H)),
                        nota=f"palavra inteira na largura, maior que a faixa: corte simétrico de {corte * 100:.0f}% em "
                             "cima e embaixo (decidido, não acidente)")
    cid = uid("marquee", tipo, w, txt)
    return elemento(w, H, f'<g clip-path="url(#{cid})">{s}</g>', nome or f"marquee · {tipo}", FAM,
                    defs=_clip(cid, _rect_d(w, H)),
                    css="@keyframes mq{to{transform:translateX(-50%)}} .mq>div{display:flex;width:max-content;animation:mq 30s linear infinite}"
                        " @media (prefers-reduced-motion:reduce){.mq>div{animation:none}}",
                    nota=nota)


# =====================================================================================================================
# listras, bolinhas, xadrez
# =====================================================================================================================
def listras(f, w=420, h=260, ang=45.0, passo=None, razao=0.5, cores=None, forma="ret", r=None, nome=None, nota="",
            contorno=False, gira=None):
    """Listras num contêiner (ret · pilula · circulo): ângulo, passo e razão cheio:vazio fixos. O desenho é SIMÉTRICO
    (uma listra centrada no meio do contêiner → as 2 bordas cortam igual). contorno = fio da forma (quando não há
    fundo, o contorno é que diz a forma)."""
    passo = passo or f.unidade * 1.5
    c1, c2 = cores or (f.acento, None)
    if gira is not None:
        # o CONTÊINER é que gira (listras ficam paralelas às bordas): listras inclinadas dentro de um retângulo reto
        # deixam lascas finas nos cantos (D24). Nº PAR de passos → as 2 bordas passam pelo centro de uma listra.
        import re
        n = max(2, 2 * round(h / passo / 2))
        hh = n * passo
        el0 = listras(f, w, hh, ang=90, passo=passo, razao=razao, cores=cores, forma=forma, r=r, contorno=contorno,
                      nome=nome, nota=nota)
        W2, H2 = _caixa_girada(w, hh, gira, 4)
        miolo = re.sub(r"^<svg[^>]*>", "", el0.svg).replace("</svg>", "")
        corpo_svg = (f'<g transform="translate({W2 / 2:.2f} {H2 / 2:.2f}) rotate({gira:.2f}) '
                     f'translate({-w / 2:.2f} {-hh / 2:.2f})">{miolo}</g>')
        return elemento(W2, H2, corpo_svg, nome or f"listras no ângulo da ficha ({gira:g}°)", FAM,
                        css=el0.css, nota=nota or f"passo {passo:g}: o contêiner gira {gira:g}° (listras paralelas às bordas)")
    cid = uid("listras", w, h, ang, passo, razao, forma, c1, c2)
    if forma == "pilula":
        dshape = p_cantos(0, 0, w, h, h / 2)
    elif forma == "circulo":
        R = min(w, h) / 2
        dshape = f"M{w / 2 - R:.2f} {h / 2:.2f}a{R:.2f} {R:.2f} 0 1 0 {2 * R:.2f} 0a{R:.2f} {R:.2f} 0 1 0 {-2 * R:.2f} 0Z"
    else:
        dshape = p_cantos(0, 0, w, h, r or 0)
    L = math.hypot(w, h) + 2 * passo
    s = f'<path d="{dshape}" fill="{c2}"/>' if c2 else ""
    k = -int(L / passo) - 1
    e = passo * razao
    barras = ""
    while k * passo < L:
        barras += f'<rect x="{k * passo - e / 2:.2f}" y="{-L / 2:.2f}" width="{e:.2f}" height="{L:.2f}" fill="{c1}"/>'
        k += 1
    s += (f'<g clip-path="url(#{cid})"><g transform="translate({w / 2:.2f} {h / 2:.2f}) rotate({ang:.2f})">{barras}</g></g>')
    if contorno:
        t = f.traco
        din = p_cantos(t / 2, t / 2, w - t, h - t, (h - t) / 2) if forma == "pilula" else p_cantos(t / 2, t / 2, w - t, h - t, max(0, (r or 0) - t / 2))
        s += f'<path d="{din}" fill="none" stroke="{c1}" stroke-width="{t:.2f}"/>'
    css = (f".listras{{background:repeating-linear-gradient({90 + ang:g}deg,{c1} 0 {passo * razao:g}px,"
           f"{c2 or 'transparent'} {passo * razao:g}px {passo:g}px)}}")
    return elemento(w, h, s, nome or f"listras {ang:g}° · passo {passo:g}", FAM, defs=_clip(cid, dshape), css=css,
                    nota=nota or f"passo {passo:g} ({passo / f.unidade:g} U), cheio:vazio {razao:g}")


def _caixa_girada(w, h, ang, m=0.0):
    a = math.radians(abs(ang))
    return w * math.cos(a) + h * math.sin(a) + 2 * m, w * math.sin(a) + h * math.cos(a) + 2 * m


def toldo(f, w=440, h=240, n=8, cores=None):
    """Listras verticais de toldo com a barra em meias-luas (1 por listra)."""
    c1, c2 = cores or (f.acento, f.tinta)
    sw = w / n
    r = sw / 2
    h0 = h - r
    s = ""
    for i in range(n):
        x = i * sw
        c = c1 if i % 2 == 0 else c2
        s += (f'<path d="M{x:.2f} 0H{x + sw:.2f}V{h0:.2f}A{r:.2f} {r:.2f} 0 0 1 {x:.2f} {h0:.2f}Z" fill="{c}"/>')
    s += f'<rect width="{w}" height="{f.traco * 3:.2f}" fill="{mistura(c2, f.fundo, 0.35)}"/>'
    return elemento(w, h, s, "toldo (listras + meias-luas)", FAM,
                    nota=f"{n} listras verticais, 1 meia-lua por listra (raio = ½ listra): festa, feira, abertura")


def persiana(f, w=420, h=260, n=12, cor=None, r=None):
    """Fios horizontais que engrossam para baixo (aceleração / peso): 2 px → 70% do passo."""
    cor = cor or f.acento
    cid = uid("persiana", w, h, n, cor)
    passo = h / n
    s = ""
    for i in range(n):
        e = 2 + (passo * 0.72 - 2) * (i / (n - 1)) ** 1.35
        y = (i + 1) * passo - e
        s += f'<rect x="0" y="{y:.2f}" width="{w}" height="{e:.2f}" fill="{cor}"/>'
    d = p_cantos(0, 0, w, h, r if r is not None else f.raio_lg)
    return elemento(w, h, f'<g clip-path="url(#{cid})">{s}</g>', "persiana (fios que engrossam)", FAM,
                    defs=_clip(cid, d), nota="espessura cresce em curva (expoente 1,35): peso, aceleração, pôr do sol")


def bolinhas(f, w=420, h=260, passo=None, r=None, cor=None, tipo="quadrada", forma="ret", nome=None, nota=""):
    """Bolinhas no passo fixo: quadrada · alternada (pois clássico) · degrade (raio cresce) · disco."""
    passo = passo or f.unidade * 1.25
    r = r or passo * 0.26
    cor = cor or f.acento
    cid = uid("bolinhas", w, h, passo, r, cor, tipo, forma)
    R = min(w, h) / 2
    rc = f.raio if forma == "raio" else 0.0
    if forma == "circulo":
        dshape = f"M{w / 2 - R:.2f} {h / 2:.2f}a{R:.2f} {R:.2f} 0 1 0 {2 * R:.2f} 0a{R:.2f} {R:.2f} 0 1 0 {-2 * R:.2f} 0Z"
    else:
        dshape = p_cantos(0, 0, w, h, rc)
    rmax = passo * 0.48 if tipo == "degrade" else r
    folga = max(1.0, passo * 0.5 - rmax)               # a 1ª bolinha fica a meio vão da borda, como entre elas

    def dentro(x, y, rr):
        """Só bolinha INTEIRA (nada de lua/fatia na borda — D8)."""
        if forma == "circulo":
            return math.hypot(x - w / 2, y - h / 2) + rr <= R - folga + 1e-6
        if x - rr < folga - 1e-6 or x + rr > w - folga + 1e-6 or y - rr < folga - 1e-6 or y + rr > h - folga + 1e-6:
            return False
        if rc:   # canto arredondado do contêiner
            cx_, cy_ = min(max(x, rc), w - rc), min(max(y, rc), h - rc)
            return math.hypot(x - cx_, y - cy_) + rr <= rc - folga + 1e-6 or (cx_ == x or cy_ == y)
        return True
    # rede SIMÉTRICA em torno do centro (as bordas sobram iguais dos 2 lados)
    nx, ny = int(w / passo) + 3, int(h / passo) + 3
    pts = []
    for j in range(-ny, ny + 1):
        for i in range(-nx, nx + 1):
            x = w / 2 + (i + (0.5 if tipo == "alternada" and j % 2 else 0)) * passo
            y = h / 2 + j * passo
            pts.append((x, y))
    if tipo == "degrade":
        xs = [x for x, y in pts if dentro(x, y, rmax)]
        xa, xb = min(xs), max(xs)
    s = ""
    for x, y in pts:
        rr = r
        if tipo == "degrade":
            rr = rmax * max(0.0, (x - xa) / max(1.0, xb - xa)) ** 1.1
            if not dentro(x, y, rmax) or rr < 1.4:          # abaixo de 1,4 px vira poeira (sujeira), não degradê
                continue
        elif not dentro(x, y, rr):
            continue
        s += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rr:.2f}" fill="{cor}"/>'
        caixa = [min(caixa[0], x - rr), min(caixa[1], y - rr), max(caixa[2], x + rr), max(caixa[3], y + rr)] \
            if s.count("<circle") > 1 else [x - rr, y - rr, x + rr, y + rr]
    return elemento(w, h, f'<g clip-path="url(#{cid})">{s}</g>', nome or f"bolinhas · {tipo}", FAM,
                    defs=_clip(cid, dshape), caixa=tuple(caixa),
                    css=f".pois{{background:radial-gradient(circle,{cor} {r:g}px,transparent {r + 0.6:g}px) 0 0/{passo:g}px {passo:g}px}}",
                    nota=nota or f"passo {passo:g}, raio {r:g}: só bolinhas inteiras, rede centrada no contêiner")


def xadrez(f, w=420, h=260, cel=None, tipo="plano", c1=None, c2=None, nome=None, nota=""):
    """Xadrez: plano · faixa de chegada (2 linhas) · losangos (45°) · chão em perspectiva."""
    cel = cel or f.unidade * 2
    c1 = c1 or f.tinta
    s = ""
    if tipo == "plano":       # número INTEIRO de casas nos 2 sentidos (nada de fileira fatiada na borda)
        nx = max(2, round(w / cel))
        cel = w / nx
        ny = max(2, round(h / cel))
        h = ny * cel
        for j in range(ny):
            for i in range(nx):
                if (i + j) % 2 == 0:
                    s += f'<rect x="{i * cel:.2f}" y="{j * cel:.2f}" width="{cel:.2f}" height="{cel:.2f}" fill="{c1}"/>'
        if c2:
            s = f'<rect width="{w}" height="{h:.2f}" fill="{c2}"/>' + s
    elif tipo == "chegada":
        nx = max(2, round(w / (f.unidade * 1.1)))
        cel = w / nx
        h = cel * 3
        s += f'<rect width="{w}" height="{h:.2f}" fill="{c2 or f.fundo}"/>'
        for j in range(3):
            for i in range(nx):
                if (i + j) % 2 == 0:
                    s += f'<rect x="{i * cel:.2f}" y="{j * cel:.2f}" width="{cel:.2f}" height="{cel:.2f}" fill="{c1}"/>'
    elif tipo == "losango":
        # arlequim: losangos de largura D e altura 0,62 D; as 4 bordas passam pelo CENTRO de uma fileira/coluna de
        # losangos → a borda vira um zigue-zague limpo de meios-losangos (nada de lasquinha de triângulo — D10)
        D = cel * math.sqrt(2)
        Dv = D * 0.62
        nx, ny = 2 * max(1, round(w / D)), 2 * max(1, round(h / Dv))     # pares → as 2 bordas iguais
        w, h = nx * D / 2, ny * Dv / 2
        cid = uid("losango", w, h, cel)
        q = ""
        for j in range(ny + 1):
            for i in range(nx + 1):
                if i % 2 == 0 and j % 2 == 0:        # 1 cor só nos (par, par); os (ímpar, ímpar) são o fundo
                    x, y = i * D / 2, j * Dv / 2
                    q += (f'<path d="M{x:.2f} {y - Dv / 2:.2f}L{x + D / 2:.2f} {y:.2f}L{x:.2f} {y + Dv / 2:.2f}'
                          f'L{x - D / 2:.2f} {y:.2f}Z" fill="{c1}"/>')
        return elemento(w, h, f'<g clip-path="url(#{cid})">{q}</g>', nome or "xadrez · losangos", FAM,
                        defs=_clip(cid, _rect_d(w, h)),
                        nota=nota or "arlequim (losango 1 : 0,62); bordas no centro dos losangos = zigue-zague limpo")
    else:   # perspectiva: linha 0 = perto (embaixo, maior), última = longe (perto do horizonte)
        cols, rows = 10, 7
        hy = h * 0.06
        k = 0.42
        zmax = 1 + rows * k

        def P(u, v):
            z = 1 + v * k
            y = hy + (h - hy) * (1 / z - 1 / zmax) / (1 - 1 / zmax)
            return (w / 2 + (u - cols / 2) * (w * 0.15) / z, y)
        for j in range(rows):
            for i in range(-4, cols + 4):
                if (i + j) % 2 == 0:
                    pts = [P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)]
                    s += f'<path d="M{"L".join(f"{x:.2f} {y:.2f}" for x, y in pts)}Z" fill="{c1}"/>'
        cid = uid("persp", w, h)
        gid, mid = cid + "g", cid + "m"
        # névoa no horizonte: as fileiras distantes somem (antes viravam um tracejado de 3 px — moiré)
        fade = (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0.04" stop-color="#fff" stop-opacity="0"/>'
                f'<stop offset="0.5" stop-color="#fff"/></linearGradient>'
                f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">'
                f'<rect width="{w}" height="{h}" fill="url(#{gid})"/></mask>')
        s = f'<g clip-path="url(#{cid})"><g mask="url(#{mid})">{s}</g></g>'
        return elemento(w, h, s, nome or "xadrez · chão em perspectiva", FAM, defs=_clip(cid, _rect_d(w, h)) + fade,
                        nota=nota or "chão de chegada em perspectiva (1 ponto de fuga) com névoa no horizonte: linha final, largada")
    cid = uid("xadrez", tipo, w, h, cel)
    return elemento(w, h, f'<g clip-path="url(#{cid})">{s}</g>', nome or f"xadrez · {tipo}", FAM,
                    defs=_clip(cid, _rect_d(w, h)), nota=nota or f"célula {cel:.1f} px ({cel / f.unidade:.2f} U)")


# =====================================================================================================================
# tarjas
# =====================================================================================================================
def tarja(f, txt="AO VIVO", r=0.0, vazado=True, cor=None, tinta=None, capx=60.0, spec=None, nome=None, nota=""):
    """Tarja com texto VAZADO (evenodd: o fundo aparece pela letra) ou cheio; raio 0 · ficha · 2× · pílula."""
    spec = spec or f.fonte_display
    cor = cor or f.tinta
    tinta = tinta or f.fundo
    sz = corpo(spec, capx)
    x0, y0, x1, y1 = caixa_texto(spec, txt, sz, 0, 0, 0.02)
    ph = capx * 0.55
    pv = max(capx * 0.42, -y0 - capx + 8, y1 + 8)          # acento/cedilha a >= 8 px da borda (pela TINTA)
    w, h = (x1 - x0) + 2 * ph, capx + 2 * pv
    rr = h / 2 if r == "pilula" else r
    if r != "pilula" and rr > ph:                          # respiro lateral >= raio (F13)
        ph = rr
        w = (x1 - x0) + 2 * ph
    if rr == h / 2:
        w += h * 0.35
    d_txt, _ = path_texto(spec, txt, sz, (w - (x1 - x0)) / 2 - x0, pv + capx, 0.02)
    caixa = p_cantos(0, 0, w, h, rr)
    if vazado:
        s = f'<path d="{caixa}{d_txt}" fill="{cor}" fill-rule="evenodd"/>'
    else:
        s = f'<path d="{caixa}" fill="{cor}"/><path d="{d_txt}" fill="{tinta}"/>'
    rot = "pílula" if r == "pilula" else f"raio {rr:g}"
    return elemento(w, h, s, nome or f"tarja {'vazada' if vazado else 'cheia'} · {rot}", FAM,
                    css=f".tarja{{border-radius:{rr:g}px;padding:{pv:g}px {ph:g}px}}",
                    nota=nota or "texto vazado: a foto/fundo aparece pela letra; respiro H = 0,55 da maiúscula")


def tarjas_empilhadas(f, linhas=("3 NOITES", "AO VIVO"), r=0.0, cor=None):
    """Uma tarja por linha, cada uma do tamanho da SUA linha (alinhadas à esquerda, degrau = respiro). Todas com a
    mesma altura: o respiro vertical sai da TINTA mais alta/baixa (acento, til, cedilha) das linhas, >= 8 px."""
    cor = cor or f.acento
    spec = f.fonte_display
    capx = 54.0
    sz = corpo(spec, capx)
    caixas = [caixa_texto(spec, ln, sz, 0, 0, 0.02) for ln in linhas]
    pv = max([capx * 0.3] + [-c[1] - capx + 8 for c in caixas] + [c[3] + 8 for c in caixas])
    ph, gap = max(capx * 0.4, r), 6.0
    s, y, W = "", 0.0, 0.0
    for ln in linhas:
        x0, _, x1, _ = caixa_texto(spec, ln, sz, 0, 0, 0.02)
        w, h = (x1 - x0) + 2 * ph, capx + 2 * pv
        s += f'<path d="{p_cantos(0, y, w, h, r)}" fill="{cor}"/>'
        d, _ = path_texto(spec, ln, sz, ph - x0, y + pv + capx, 0.02)
        s += f'<path d="{d}" fill="{f.sobre_acento if cor == f.acento else f.fundo}"/>'
        y += h + gap
        W = max(W, w)
    return elemento(W, y - gap, s, f"tarjas empilhadas · raio {r:g}", FAM,
                    nota="1 tarja por linha (cada uma do tamanho da linha), degrau à direita, 6 px entre elas")


def redacao(f, w=440, cor=None):
    """Parágrafo redigido (sigilo DE MARCA): barras de comprimentos variados; 1 informação escapa."""
    cor = cor or f.tinta
    rnd = f.rnd("redacao")
    lh, bh = 40.0, 26.0
    s = ""
    linhas = 5
    for j in range(linhas):
        y = j * lh
        x = 0.0
        fim = w if j < linhas - 1 else w * 0.55
        while x < fim - 1:
            if j == 2 and x == 0.0:
                # o dado que escapa vai numa barra de ACENTO com texto escuro (acento sobre papel dava ~2:1 — D11)
                tw = larg_rotulo(f, "20H30", 20, f.fonte_mono, 0.04)
                s += f'<rect x="0" y="{y:.2f}" width="{tw + 20:.2f}" height="{bh:.2f}" fill="{f.acento}"/>'
                a, _ = rotulo(f, "20H30", 10, y + bh / 2, f.sobre_acento, 20, f.fonte_mono, 0.04)
                s += a
                x += tw + 20 + 12
                continue
            seg = rnd.uniform(60, 190)
            if fim - (x + seg + 12) < 60:                  # a última barra da linha vai até o fim (borda direita igual)
                seg = fim - x
            s += f'<rect x="{x:.2f}" y="{y:.2f}" width="{seg:.2f}" height="{bh:.2f}" fill="{cor}"/>'
            x += seg + 12
    return elemento(w, (linhas - 1) * lh + bh, s, "parágrafo redigido · 1 dado escapa", FAM,
                    nota="tarjas de palavra (vão 12 px), 1 informação no acento escapa: curiosidade sem mentir")


# =====================================================================================================================
# sinais gigantes
# =====================================================================================================================
def _glifo(f, g, alt, spec=None):
    """d do glifo com a TINTA começando em (0,0) e altura de tinta = alt. Devolve (d, largura, altura)."""
    spec = spec or f.fonte_display
    bx0, by0, bx1, by1 = caixa_texto(spec, g, 100)
    sz = 100 * alt / (by1 - by0)
    x0, y0, x1, y1 = caixa_texto(spec, g, sz)
    d, _ = path_texto(spec, g, sz, -x0, -y0)
    return d, x1 - x0, y1 - y0


def sinal(f, g="%", modo="cheio", w=440, h=340, alt=None, pos=(0.5, 0.5), cor=None, n_eco=4, passo=None,
          fatias=5, nome=None, nota="", sangra=None):
    """Glifo gigante DA fonte display. modo: cheio · contorno (por fora) · eco (3–5 cópias) · anel (cheio + contorno
    afastado) · fatiado (3–7 tiras deslocadas). pos = onde fica o CENTRO da tinta (fração; >1 corta pela borda)."""
    cor = cor or f.acento
    alt = alt or h * 0.82
    d, gw, gh = _glifo(f, g, alt)
    if modo == "eco":       # o eco inteiro (glifo + cópias) tem que caber: encolhe e centra o CONJUNTO
        passo = passo or alt * 0.06
        ext = (n_eco - 1) * passo
        k = min(1.0, (h * 0.84) / (gh + ext), (w * 0.86) / (gw + ext))
        if k < 1:
            alt *= k
            passo *= k
            d, gw, gh = _glifo(f, g, alt)
            ext = (n_eco - 1) * passo
        cx = min(max(w * pos[0] - ext / 2, gw / 2 + 2), w - gw / 2 - ext - 2)
        cy = min(max(h * pos[1] - ext / 2, gh / 2 + 2), h - gh / 2 - ext - 2)
    elif sangra:            # sangra = (fração do glifo cortada à direita, fração cortada embaixo): corte DECIDIDO
        cx, cy = w - gw / 2 + sangra[0] * gw, h - gh / 2 + sangra[1] * gh
    else:
        cx, cy = w * pos[0], h * pos[1]
    tx, ty = cx - gw / 2, cy - gh / 2
    G = f'<path transform="translate({tx:.2f} {ty:.2f})" d="{d}"'
    sw = max(3.0, alt * 0.03)
    s, defs = "", ""
    if modo == "cheio":
        s = G + f' fill="{cor}"/>'
        nota = nota or ("glifo da display ≥ 60% da altura; cortado pela borda quando passa de 1" if not sangra else
                        f"glifo da display, cortado {sangra[0] * 100:.0f}% à direita e {sangra[1] * 100:.0f}% embaixo "
                        "(corte decidido, nunca tangente)")
    elif modo == "contorno":
        mid = uid("cont", g, w, h, alt, pos)
        defs = (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">'
                f'<rect width="{w}" height="{h}" fill="#fff"/>{G} fill="#000"/></mask>')
        s = f'<g mask="url(#{mid})">{G} fill="none" stroke="{cor}" stroke-width="{2 * sw:.2f}" stroke-linejoin="round"/></g>'
        nota = nota or f"contorno POR FORA ({sw:.0f} px ≈ 3% da altura): o glifo mantém o tamanho do cheio"
    elif modo == "eco":
        passo = passo or alt * 0.06
        for k in range(n_eco - 1, 0, -1):
            s += (f'<path transform="translate({tx + k * passo:.2f} {ty + k * passo:.2f})" d="{d}" fill="none" '
                  f'stroke="{mistura(cor, f.fundo, 0.18 * k)}" stroke-width="{sw * 0.6:.2f}"/>')
        s += G + f' fill="{cor}"/>'
        nota = nota or f"eco: {n_eco} cópias, passo {passo:.0f} px (6% da altura), só a da frente cheia"
    elif modo == "anel":
        mid = uid("anel", g, w, h, alt, pos)
        gap = sw * 1.6
        defs = (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">'
                f'{G} fill="none" stroke="#fff" stroke-width="{2 * (gap + sw):.2f}" stroke-linejoin="round"/>'
                f'{G} fill="none" stroke="#000" stroke-width="{2 * gap:.2f}" stroke-linejoin="round"/>{G} fill="#000"/></mask>')
        s = G + f' fill="{f.tinta}"/>' + f'<rect width="{w}" height="{h}" fill="{cor}" mask="url(#{mid})"/>'
        nota = nota or "cheio + contorno afastado (folga 1,6× o traço): letreiro, néon apagado"
    elif modo == "fatiado":
        cid = uid("fat", g, w, h, alt, pos, fatias)
        fh = gh / fatias
        desl = alt * 0.045
        for k in range(fatias):
            y0 = ty + k * fh
            defs += f'<clipPath id="{cid}{k}"><rect x="0" y="{y0 - 0.3:.2f}" width="{w}" height="{fh + 0.6:.2f}"/></clipPath>'
            dx = (k - (fatias - 1) / 2) * desl * 0.6        # degraus progressivos: a forma continua lendo
            s += f'<g clip-path="url(#{cid}{k})"><g transform="translate({dx:.2f} 0)">{G} fill="{cor}"/></g></g>'
        nota = nota or f"{fatias} tiras em degrau ({desl * 0.6:.0f} px por tira ≈ 2,7% da altura); a do meio fica parada"
    vx0, vy0 = max(0, tx), max(0, ty)
    caixa = (vx0, vy0, min(w, tx + gw), min(h, ty + gh))
    cid = uid("sinal", g, modo, w, h, alt, pos)
    defs += _clip(cid, _rect_d(w, h))          # cortado pela borda = cortado em qualquer palco
    return elemento(w, h, f'<g clip-path="url(#{cid})">{s}</g>', nome or f"sinal '{g}' · {modo}", FAM, defs=defs,
                    caixa=caixa, nota=nota)


def seta_bloco(f, w=440, h=300, ang=None, cor=None, contorno=False, corta=False):
    """Seta gigante em bloco (haste grossa + ponta a 90°), no ângulo da ficha; pode sangrar pela direita."""
    ang = f.angulo if ang is None else ang
    cor = cor or f.acento
    L = w * (1.15 if corta else 0.86)
    hs = h * 0.26
    ph = h * 0.62
    pl = ph * 0.55
    pts = [(0, -hs / 2), (L - pl, -hs / 2), (L - pl, -ph / 2), (L, 0), (L - pl, ph / 2), (L - pl, hs / 2), (0, hs / 2)]
    d = "M" + "L".join(f"{x - L / 2:.2f} {y:.2f}" for x, y in pts) + "Z"
    # corta: a PONTA fica inteira (a 7% da borda direita) e a CAUDA sangra pela esquerda (antes: só 16% da ponta — D26)
    cx = (0.93 * w - (L / 2) * math.cos(math.radians(ang))) if corta else w / 2
    if contorno:
        s = (f'<path transform="translate({cx:.2f} {h / 2:.2f}) rotate({ang:.2f})" d="{d}" fill="none" stroke="{cor}" '
             f'stroke-width="{f.traco * 2:.2f}" stroke-linejoin="miter"/>')
    else:
        s = f'<path transform="translate({cx:.2f} {h / 2:.2f}) rotate({ang:.2f})" d="{d}" fill="{cor}"/>'
    cid = uid("setab", w, h, ang, corta, contorno)
    return elemento(w, h, f'<g clip-path="url(#{cid})">{s}</g>', "seta gigante" + (" · sangra" if corta else "")
                    + (" · contorno" if contorno else ""), FAM, defs=_clip(cid, _rect_d(w, h)),
                    nota=f"bloco: haste 26% da altura, ponta a 90°; no ângulo da ficha ({ang:g}°)")


def mais(f, w=300, h=300, cor=None, contorno=False, r=0.0):
    """'+' gigante desenhado (braço = 1/3 do lado, proporção suíça); r = canto das pontas."""
    cor = cor or f.acento
    a = min(w, h) * 0.86
    b = a / 3
    x0, y0 = (w - a) / 2, (h - a) / 2
    pts = [(x0 + b, y0), (x0 + 2 * b, y0), (x0 + 2 * b, y0 + b), (x0 + a, y0 + b), (x0 + a, y0 + 2 * b), (x0 + 2 * b, y0 + 2 * b),
           (x0 + 2 * b, y0 + a), (x0 + b, y0 + a), (x0 + b, y0 + 2 * b), (x0, y0 + 2 * b), (x0, y0 + b), (x0 + b, y0 + b)]
    if r:
        from .selos import poligono_redondo
        d = poligono_redondo(pts, r)
    else:
        d = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"
    if contorno:
        s = f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="{f.traco * 2:.2f}" stroke-linejoin="miter"/>'
    else:
        s = f'<path d="{d}" fill="{cor}"/>'
    return elemento(w, h, s, "'+' gigante" + (" · contorno" if contorno else "") + (f" · raio {r:g}" if r else ""), FAM,
                    nota="braço = 1/3 do lado; 'mais' de verdade (bônus, soma), nunca enfeite solto")


def numeral_heroi(f, n="1", rot="NOITE", sub="20H30", cor=None):
    """Numeral herói: dígito gigante + rótulo e hora alinhados à ALTURA da maiúscula do dígito (topo e base)."""
    cor = cor or f.tinta
    alt = 300.0
    d, gw, gh = _glifo(f, n, alt)
    gap = 22.0
    capx = 25.0
    s = f'<path transform="translate(0 0)" d="{d}" fill="{cor}"/>'
    a, _ = rotulo(f, rot, gw + gap, capx / 2, f.acento, capx, f.fonte_texto, 0.14)
    b, _ = rotulo(f, sub, gw + gap, gh - capx / 2, mistura(cor, f.fundo, 0.25), capx, f.fonte_mono, 0.04)
    # largura pela TINTA (a largura da fonte inclui o espaçamento depois da última letra)
    ia = caixa_texto(f.fonte_texto, rot, corpo(f.fonte_texto, capx), 0, 0, 0.14)
    ib = caixa_texto(f.fonte_mono, sub, corpo(f.fonte_mono, capx), 0, 0, 0.04)
    wink = max(ia[2], ib[2]) - min(ia[0], ib[0])
    x_l = gw + gap
    s += a + b
    s += (f'<line x1="{x_l:.2f}" y1="{capx + 16:.2f}" x2="{x_l + wink:.2f}" y2="{capx + 16:.2f}" '
          f'stroke="{cor}" stroke-width="{f.traco:.2f}"/>')
    return elemento(x_l + wink, gh, s, f"numeral herói · {n}", FAM,
                    nota="rótulo encosta no TOPO da tinta do dígito, hora na BASE; fio fino separa")


def porcentagem_heroi(f, cor=None):
    """% herói SEM número inventado: o sinal sozinho, cheio, com eco em contorno (o número entra da oferta real)."""
    return sinal(f, "%", "eco", 440, 340, pos=(0.44, 0.47), cor=cor or f.acento, n_eco=5,
                 nome="porcentagem herói · eco 5×",
                 nota="o % sozinho (o número vem da condição real do cliente); eco de 5 contornos")


# =====================================================================================================================
# amostras
# =====================================================================================================================
@amostra(FAM, "faixas com texto")
def _a_faixas(f):
    return [
        faixa_texto(f, txt="AO VIVO", sep="losango"),
        faixa_texto(f, txt="3 NOITES", sep="barra", cor=f.tinta, nome="faixa · tinta · barra"),
        faixa_texto(f, txt="AO VIVO", sep="ponto", isolamento=True, hb=90, nome="fita de isolamento",
                    nota="bordas zebradas a 45° + texto: 'área reservada', contagem regressiva"),
        faixa_texto(f, txt="20H30", sep="seta", spec=f.fonte_display, alterna=True, ang=f.angulo * 2,
                    nome="faixa · cheio/contorno alternados", nota="repetição alterna cheio e contorno: ritmo sem cor nova"),
        faixas_cruzadas(f),
    ]


@amostra(FAM, "marquee")
def _a_marquee(f):
    # "letreiro cortado" saiu da amostra (revisão 10/2026): com o corte decidido de 18% a palavra deixa de ler
    # (parece falha de render, D1); o modo continua no código para uso consciente.
    return [marquee(f, tipo="simples"), marquee(f, tipo="dupla")]


@amostra(FAM, "listras")
def _a_listras(f):
    fc = claro(f)
    return [
        listras(f, ang=45, razao=0.5, cores=(f.acento, f.fundo), nome="zebrado 45° (1:1)",
                nota="perigo/atenção, borda de faixa; 1:1 a 45°"),
        listras(f, 420, 120, ang=-45, razao=0.33, cores=(f.tinta, None), forma="pilula", nome="listras na pílula (1:2)",
                nota="barra de carregamento / reservado; 1:2; o fio da pílula desenha a forma", contorno=True),
        listras(f, passo=f.unidade * 2, razao=0.5, cores=(f.tinta, None), r=f.raio_lg, gira=f.angulo,
                nome=f"listras no ângulo da ficha ({f.angulo:g}°)",
                nota="o contêiner gira no ângulo das faixas do sistema; listras paralelas às bordas (sem lascas)"),
        listras(f, 300, 300, ang=45, passo=9, razao=0.3, cores=(f.tinta, None), forma="circulo",
                nome="hachura no disco (passo 9)", nota="hachura de sistema: passo 6–12 px, traço ~3 px, 1 ângulo"),
        toldo(f),
        persiana(f),
        no_claro(listras(fc, ang=0, passo=f.unidade, razao=0.5, cores=(fc.tinta, None), nome="listras verticais · papel",
                         nota="pauta grossa 1:1 (passo = 1 U)")),
    ]


@amostra(FAM, "bolinhas e xadrez")
def _a_bolinhas(f):
    fc = claro(f)
    return [
        bolinhas(f, tipo="alternada", nome="bolinhas · pois alternado"),
        bolinhas(f, tipo="quadrada", cor=f.tinta, r=4, passo=f.unidade, forma="raio", nome="bolinhas · grade fina"),
        bolinhas(f, tipo="degrade", passo=f.unidade * 1.2, nome="bolinhas · degradê de raio",
                 nota="raio cresce da esquerda para a direita (passo fixo): movimento, chegada"),
        bolinhas(f, 300, 300, tipo="alternada", forma="circulo", cor=f.tinta, nome="bolinhas no disco"),
        xadrez(f, tipo="plano", nome="xadrez · plano"),
        xadrez(f, 460, tipo="chegada", nome="xadrez · faixa de chegada", nota="3 fileiras: bandeira de chegada (célula 1,1 U)"),
        xadrez(f, tipo="losango", c1=f.acento),
        no_claro(xadrez(fc, 440, 300, tipo="perspectiva", c1=fc.tinta)),
    ]


@amostra(FAM, "tarjas")
def _a_tarjas(f):
    fc = claro(f)
    return [
        tarja(f, "AO VIVO", 0),
        tarja(f, "AO VIVO", f.raio, cor=f.acento),
        tarja(f, "20H30", f.raio_sm, spec=f.fonte_mono, capx=44),
        tarja(f, "3 NOITES", "pilula", cor=f.acento),
        tarja(f, "NOITE 1", f.raio, vazado=False, cor=f.acento, tinta=f.sobre_acento, nome="tarja cheia · raio da ficha",
              nota="texto na cor de contraste (não vazado): quando o fundo atrás é movimentado"),
        tarjas_empilhadas(f),
        tarjas_empilhadas(f, ("PÓS-", "GRADUAÇÃO"), r=f.raio, cor=f.tinta),
        no_claro(redacao(fc)),
    ]


@amostra(FAM, "sinais gigantes")
def _a_sinais(f):
    fc = claro(f)
    return [
        sinal(f, "%", "cheio", alt=380, sangra=(0.22, 0.25), nome="'%' gigante cortado"),
        sinal(f, "%", "contorno", nome="'%' contorno por fora", cor=f.tinta),
        sinal(f, "1", "anel", nome="numeral '1' · cheio + anel"),
        numeral_heroi(f),
        sinal(f, "“", "cheio", 300, 300, alt=170, pos=(0.5, 0.45), nome="aspas gigantes (da fonte)",
              nota="depoimento: aspas DA display, 3–6× o corpo do texto, alinhadas à tinta"),
        no_claro(sinal(fc, "“", "contorno", 300, 300, alt=170, pos=(0.5, 0.45), cor=fc.tinta, nome="aspas · contorno · papel")),
        sinal(f, "+", "cheio", 300, 300, alt=220, nome="'+' da fonte", cor=f.tinta),
        mais(f),
        mais(f, contorno=True, r=f.raio, cor=f.tinta),
        seta_bloco(f),
        seta_bloco(f, corta=True, cor=f.tinta),
        seta_bloco(f, contorno=True, cor=f.tinta),
    ]
