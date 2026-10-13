"""ornamentos.colagem — família "colagem e papel": fita adesiva, adesivo com borda, papel rasgado, recorte de jornal,
polaroide/filme, clipe, índice numerado, post-it e etiquetas de arquivo.

Regras (references/elementos.md; pesquisa 11 E69–E75): colagem = 3–6 fragmentos com UMA direção de sombra (luz de
cima-esquerda → sombra para baixo-direita), sombra de papel curta (2–6 px, 15–30%); adesivo com borda branca de
espessura constante (1,5–3% do lado); polaroide na proporção real; NADA de texto falso — coluna de jornal é
desenhada com barras (é esquema), e a área de foto fica vazia (é contêiner). Semente fixa: mesma ficha → mesmo
rasgo. Nunca fita + rasgo + rabisco + scan juntos ("imperfeito de kit").

Revisão um a um 10/2026 (R4 → colagem.md): furo/corte nunca é pintado com a cor do fundo (geometria, clip ou
evenodd); rótulo que precisa ser lido tem maiúscula ≥ 25,6 px no tamanho natural; raios só da escala da ficha;
padrão (retícula) só com peças inteiras; clipe prendedor removido (parecia bolsa).
"""
import math
import re

from .nucleo import amostra, largura, cap, ret, poligono, polilinha, suave, filtro, ruido1d
from .nucleo import _font
from .assunto import justo, mistura, polar, rot, rot_c, num, _p, luminancia, semente, uid, circ

FAM = "colagem"
CAP_LEGIVEL = 26.0     # maiúscula mínima (px, num 1080) de todo rótulo que precisa ser lido (25,6 = 34 px de corpo × 0,75)


def _sombra(id_, dx=2.0, dy=3.0, blur=2.5, op=0.35):
    """Sombra de papel (uma direção só: baixo-direita)."""
    return filtro(id_, f'<feDropShadow dx="{dx}" dy="{dy}" stdDeviation="{blur}" flood-color="#000" flood-opacity="{op}"/>')


def _borda_rasgada(rnd, p0, p1, amp, passo, salto=0.0):
    """Pontos de uma borda irregular de p0 a p1 (ruído suave + dente fino). A amplitude AFINA perto das pontas
    (12% de cada lado) — o canto do papel não vira espinho."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(4, int(L / passo))
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    rr = ruido1d(rnd, n + 1, 3)
    pts = []
    for i in range(n + 1):
        k = i / n
        env = min(1.0, k / 0.12, (1 - k) / 0.12)
        d = (rr[i] * amp + rnd.uniform(-amp, amp) * 0.35) * env + salto * env
        if i in (0, n):
            d = 0
        pts.append((x0 + (x1 - x0) * k + nx * d, y0 + (y1 - y0) * k + ny * d))
    return pts


def _borda_dente(rnd, p0, p1, amp, passo):
    """Ponta de fita rasgada: dente IRREGULAR (espaçamento e profundidade sorteados; um ou outro dente fundo) —
    nunca zigue-zague regular. p0 → p1 reta; o dente desloca na normal."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(5, int(L / passo))
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    ks = [0.0]
    for _ in range(n):
        ks.append(ks[-1] + rnd.uniform(0.5, 1.6))
    tot = ks[-1]
    pts = []
    for i, k in enumerate(ks):
        k /= tot
        if i in (0, n):
            d = rnd.uniform(-0.3, 0.3) * amp
        else:
            d = rnd.triangular(-amp, amp * 1.8, amp * 0.3)
            if rnd.random() < 0.2:      # um dente mais fundo de vez em quando
                d += rnd.choice((-1, 1)) * amp * 1.3
        pts.append((x0 + (x1 - x0) * k + nx * d, y0 + (y1 - y0) * k + ny * d))
    return pts


def _forma_fita(r, w, h):
    return (_borda_dente(r, (0, h), (0, 0), h * 0.07, h / 7)
            + _borda_dente(r, (w, 0), (w, h), h * 0.07, h / 7))


def _crepe(f, r, d, w, h, cid):
    """Corpo de fita crepe (fibras verticais) dentro do contorno `d`."""
    o = [f'<path d="{d}" fill="{mistura(f.papel, "#D9C9A3", 0.5)}" fill-opacity="0.96"/>',
         f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">']
    for k in range(max(6, int(w / 3.2))):
        x = r.uniform(0, w)
        o.append(_p(f"M{x:.2f} 0L{x + r.uniform(-3, 3):.2f} {h:.2f}", stroke="#8C7A55", sw=r.uniform(0.4, 1.0),
                    extra=f'stroke-opacity="{r.uniform(0.04, 0.14):.2f}"'))
    o.append("</g>")
    return "".join(o)


# ================================================================ fita adesiva
def fita(f, w=230.0, angulo=None, tipo="translucida", seed=1):
    """Pedaço de fita: pontas rasgadas em dente irregular (rasgo à mão), corpo translúcido (plástico com brilho e
    bordas), crepe (fibra) ou na cor de acento. ângulo padrão = ângulo da ficha."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    r = semente(f, "fita", seed, w, tipo)
    h = w * 0.27
    ang = f.angulo if angulo is None else angulo
    d = poligono(_forma_fita(r, w, h))
    sid = uid("sombra-fita", seed, w, tipo)
    defs = _sombra(sid, 0.8, 1.3, 1.0, 0.30)
    cid = uid("fita-clip", seed, w, tipo)
    o = []
    if tipo == "translucida":
        branco = mistura(f.papel, "#FFFFFF", 0.7)
        o.append(f'<path d="{d}" fill="{branco}" fill-opacity="0.27"/>')
        # brilho diagonal do plástico (duas faixas), recortado pelo contorno
        o.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">')
        o.append(f'<path d="{poligono([(w * 0.14, 0), (w * 0.27, 0), (w * 0.20, h), (w * 0.07, h)])}" fill="{branco}" fill-opacity="0.22"/>')
        o.append(f'<path d="{poligono([(w * 0.30, 0), (w * 0.33, 0), (w * 0.26, h), (w * 0.23, h)])}" fill="{branco}" fill-opacity="0.2"/>')
        # bordas: fio escuro por fora (aparece no claro) + fio claro por dentro (aparece no escuro)
        o.append(_p(f"M0 0.5H{w:.2f}M0 {h - 0.5:.2f}H{w:.2f}", stroke=f.fundo, sw=1.0, extra='stroke-opacity="0.30"'))
        o.append(_p(f"M0 1.6H{w:.2f}M0 {h - 1.6:.2f}H{w:.2f}", stroke=branco, sw=0.9, extra='stroke-opacity="0.45"'))
        o.append("</g>")
    elif tipo == "crepe":
        o.append(_crepe(f, r, d, w, h, cid))
    else:
        o.append(f'<path d="{d}" fill="{ac}" fill-opacity="0.9"/>')
    corpo = (f'<g filter="url(#{sid})"><g transform="rotate({ang:.2f} {w / 2:.2f} {h / 2:.2f})">{"".join(o)}</g></g>')
    return justo(corpo, f"fita · {tipo} · {ang:+.0f}°", "fita rasgada à mão (dente irregular nas pontas), no ângulo do "
                 "sistema · prende foto/papel na colagem; 1–2 por peça", defs=defs)


@amostra(FAM, "fita adesiva")
def _a_fita(f):
    return [fita(f), fita(f, 170, 38, seed=2), fita(f, tipo="crepe", seed=3), fita(f, 160, 4, "crepe", seed=4),
            fita(f, 200, -12, "acento", seed=5)]


# ================================================================ adesivo com borda branca
def _d_para_path(d):
    """d absoluto (M L H V Q Z) → pathops.Path (os caminhos de texto da `Font` só usam esses comandos)."""
    from pathops import Path
    p = Path()
    pen = p.getPen()
    tok = re.findall(r'[MLHVQZ]|-?\d+\.?\d*(?:[eE]-?\d+)?', d)
    i, cmd, cx, cy, aberto = 0, None, 0.0, 0.0, False
    while i < len(tok):
        if tok[i] in "MLHVQZ":
            cmd = tok[i]
            i += 1
            if cmd == "Z":
                if aberto:
                    pen.closePath()
                    aberto = False
                continue
        if cmd == "M":
            if aberto:
                pen.closePath()
            cx, cy = float(tok[i]), float(tok[i + 1])
            i += 2
            pen.moveTo((cx, cy))
            aberto, cmd = True, "L"
        elif cmd == "L":
            cx, cy = float(tok[i]), float(tok[i + 1])
            i += 2
            pen.lineTo((cx, cy))
        elif cmd == "H":
            cx = float(tok[i])
            i += 1
            pen.lineTo((cx, cy))
        elif cmd == "V":
            cy = float(tok[i])
            i += 1
            pen.lineTo((cx, cy))
        elif cmd == "Q":
            x1, y1, x, y = (float(v) for v in tok[i:i + 4])
            i += 4
            pen.qCurveTo((x1, y1), (x, y))
            cx, cy = x, y
        else:
            raise ValueError(f"comando {cmd}")
    if aberto:
        pen.closePath()
    return p


def _contorno_solido(d, esp):
    """Contorno de adesivo recortado (die-cut): o glifo + uma faixa de `esp` px por todos os lados, FUNDIDOS num só
    caminho SEM buracos (frestas e miolos viram papel branco, como o corte real). Devolve o `d` do contorno."""
    from pathops import Path, LineCap, LineJoin, union
    from fontTools.pens.svgPathPen import SVGPathPen
    p = _d_para_path(d)
    s = _d_para_path(d)
    s.stroke(2 * esp, LineCap.ROUND_CAP, LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads()
    u = Path()
    union([p, s], u.getPen())
    cs = list(u.contours)
    if not cs:
        return d
    maior = max(cs, key=lambda c: abs(c.area))
    sentido = maior.clockwise
    pen = SVGPathPen(None)
    for c in cs:
        if c.clockwise == sentido:        # descarta os buracos (sentido contrário ao do contorno externo)
            c.draw(pen)
    return pen.getCommands()


def adesivo(f, forma="circulo", txt="AO VIVO", cor=None, tam=200.0, angulo=0.0, dobra=False):
    """Adesivo: forma na cor de acento + texto em curvas + borda branca de espessura constante (3% do lado) +
    sombra curta. forma: circulo | pilula | retangulo | palavra (recorte acompanhando as letras, sem frestas).
    dobra: canto de baixo-direita descolando (o corte é GEOMETRIA — clip —, nunca tinta da cor do fundo)."""
    t, ink, ac = f.traco, f.tinta, f.acento
    cor = cor or ac
    tc = f.sobre_acento if cor == ac else (f.fundo if luminancia(cor) > 0.4 else ink)
    branco = mistura(f.papel, "#FFFFFF", 0.6)
    b = max(4.0, tam * 0.03)
    sid = uid("sombra-ad", forma, txt, tam)
    defs = _sombra(sid, 2.0, 3.0, 2.0, 0.4)
    o = []
    extra = ""
    if forma == "circulo":
        R = tam / 2
        o.append(f'<circle r="{R:.2f}" fill="{branco}"/><circle r="{R - b:.2f}" fill="{cor}"/>')
        o.append(f'<circle r="{R - b * 2.6:.2f}" fill="none" stroke="{tc}" stroke-width="{t * 0.5:.2f}" stroke-opacity="0.5"/>')
        # corpo do texto: o maior que cabe no miolo (largura ≤ 60% do lado) sem passar de 30% do lado
        sz = min(tam * 0.30, tam * 0.60 / max(0.01, largura(f.fonte_display, txt, 1.0, 0.02)))
        o.append(rot_c(f, txt, sz, 0, 0, tc, f.fonte_display, 0.02))
    elif forma == "pilula":
        tw = largura(f.fonte_display, txt, tam * 0.3, 0.02)
        hh = tam * 0.42
        W = tw + hh * 1.1
        o.append(f'<path d="{ret(-W / 2 - b, -hh / 2 - b, W + 2 * b, hh + 2 * b, hh / 2 + b)}" fill="{branco}"/>')
        o.append(f'<path d="{ret(-W / 2, -hh / 2, W, hh, hh / 2)}" fill="{cor}"/>')
        o.append(rot_c(f, txt, tam * 0.3, 0, 0, tc, f.fonte_display, 0.02))
    elif forma == "retangulo":
        W, H = tam, tam * 0.62
        rr = f.raio_sm        # 16; a borda branca é o recuo concêntrico (rr + b)
        o.append(f'<path d="{ret(-W / 2 - b, -H / 2 - b, W + 2 * b, H + 2 * b, rr + b)}" fill="{branco}"/>')
        o.append(f'<path d="{ret(-W / 2, -H / 2, W, H, rr)}" fill="{cor}"/>')
        o.append(rot_c(f, txt, tam * 0.24, 0, 0, tc, f.fonte_display, 0.02))
        if dobra:
            c = tam * 0.17
            x1, y1 = W / 2 + b, H / 2 + b
            K = x1 + y1 - c            # reta x + y = K: o que passa da reta foi descolado
            cid = uid("corte-dobra", tam, txt)
            big = 2000
            defs += (f'<clipPath id="{cid}"><path d="{poligono([(-big, -big), (big, -big), (big, K - big), (K - big, big), (-big, big)])}"/>'
                     f'</clipPath>')
            fid = uid("grad-dobra", tam, txt)
            defs += (f'<linearGradient id="{fid}" gradientUnits="userSpaceOnUse" x1="{x1 - c * 0.5:.2f}" y1="{y1 - c * 0.5:.2f}" '
                     f'x2="{x1 - c:.2f}" y2="{y1 - c:.2f}"><stop offset="0" stop-color="{mistura(branco, "#000000", 0.16)}"/>'
                     f'<stop offset="1" stop-color="{branco}"/></linearGradient>')
            did = uid("sombra-dobra", tam, txt)
            defs += _sombra(did, -1.0, -1.0, 1.6, 0.35)
            o = [f'<g clip-path="url(#{cid})">{"".join(o)}</g>']
            # o verso do canto dobrado: o canto (x1,y1) vai parar espelhado na reta, em (x1 - c, y1 - c)
            o.append(f'<path d="{poligono([(x1 - c, y1), (x1, y1 - c), (x1 - c, y1 - c)])}" fill="url(#{fid})" '
                     f'filter="url(#{did})"/>')
    else:   # palavra recortada
        sz = tam * 0.62
        fo = _font(f.fonte_display)
        wd = fo.width(txt, sz, 0.02)
        d = fo.path(txt, sz, -wd / 2, cap(f.fonte_display) * sz / 2, 0.02)
        o.append(f'<path d="{_contorno_solido(d, b * 1.3)}" fill="{branco}"/>')
        o.append(f'<path d="{d}" fill="{cor}"/>')
    corpo = f'<g filter="url(#{sid})"><g transform="rotate({angulo:.2f})">{"".join(o)}</g></g>'
    return justo(corpo, f"adesivo · {forma} · {txt}" + (" · canto descolando" if dobra else ""),
                 "borda branca constante (3% do lado), sombra curta 2–3 px · status, data, palavra-chave na colagem",
                 defs=defs)


@amostra(FAM, "adesivo")
def _a_adesivo(f):
    return [adesivo(f), adesivo(f, "pilula", "NOITE 1", angulo=-6), adesivo(f, "retangulo", "20H30", angulo=4, dobra=True),
            adesivo(f, "palavra", "BLACK", angulo=-6), adesivo(f, "palavra", "3", tam=260, cor=mistura(f.fundo, f.tinta, 0.16)),
            adesivo(f, "circulo", "PÓS", cor=mistura(f.fundo, f.tinta, 0.08), tam=170, angulo=8)]


# ================================================================ papel rasgado
def papel_rasgado(f, w=420.0, h=150.0, bordas="cima", cor=None, seed=1, angulo=0.0):
    """Pedaço de papel com borda RASGADA (ruído suave + dente) e a franja branca da fibra exposta SÓ onde rasgou
    (nas bordas retas a franja fica escondida embaixo do papel). bordas: cima | baixo | ambas | todas."""
    r = semente(f, "rasgo", seed, w, h, bordas)
    cor = cor or f.papel
    franja = mistura(cor, "#FFFFFF", 0.65) if luminancia(cor) < 0.75 else mistura(cor, "#FFFFFF", 0.85)
    amp, passo = h * 0.045, 5.0
    rasga = {"cima": "t", "baixo": "b", "ambas": "tb", "todas": "tblr"}[bordas]
    r2 = semente(f, "rasgo-f", seed, w, h)
    # lado: chave, ponto inicial, ponto final, normal PARA FORA
    lados = [("t", (0, 0), (w, 0), (0, -1)), ("r", (w, 0), (w, h), (1, 0)),
             ("b", (w, h), (0, h), (0, 1)), ("l", (0, h), (0, 0), (-1, 0))]
    pts, fr = [], []
    canto = {}                                  # deslocamento da franja em cada canto (soma das duas bordas)
    for ch, p0, p1, (nx, ny) in lados:
        k_c = r2.uniform(1.5, 4.0) if ch in rasga else -2.0       # borda reta: franja 2 px PARA DENTRO (escondida)
        for p in (p0, p1):
            ox, oy = canto.get(p, (0.0, 0.0))
            canto[p] = (ox + nx * k_c, oy + ny * k_c)
    for ch, p0, p1, (nx, ny) in lados:
        pts.append(p0)
        fr.append((p0[0] + canto[p0][0], p0[1] + canto[p0][1]))
        if ch in rasga:
            borda = _borda_rasgada(r, p0, p1, amp, passo)
            for x, y in borda[1:-1]:
                k = r2.uniform(1.5, 4.0)
                pts.append((x, y))
                fr.append((x + nx * k, y + ny * k))
    cx, cy = w / 2, h / 2
    sid = uid("sombra-papel", seed, w, h)
    defs = _sombra(sid, 1.5, 2.5, 2.0, 0.35)
    corpo = (f'<g filter="url(#{sid})" transform="rotate({angulo:.2f} {cx:.2f} {cy:.2f})">'
             f'<path d="{poligono(fr)}" fill="{franja}"/><path d="{poligono(pts)}" fill="{cor}"/></g>')
    tom = " · acento" if cor == f.acento else (" · escuro" if luminancia(cor) < 0.2 else "")
    return justo(corpo, f"papel rasgado · {bordas}{tom}",
                 "borda rasgada com franja de fibra (o branco de dentro do papel) e sombra curta · base de texto, "
                 "divisor de seção, colagem", defs=defs)


@amostra(FAM, "papel rasgado")
def _a_papel(f):
    return [papel_rasgado(f), papel_rasgado(f, 420, 110, "ambas", seed=2),
            papel_rasgado(f, 300, 220, "todas", seed=3, angulo=-4),
            papel_rasgado(f, 420, 140, "baixo", cor=mistura(f.fundo, f.tinta, 0.14), seed=4),
            papel_rasgado(f, 260, 200, "todas", cor=f.acento, seed=5, angulo=5)]


# ================================================================ recorte de jornal (esquema: barras, não texto)
def recorte_jornal(f, colunas=1, titulo=True, foto=False, seed=1, angulo=None, w=None):
    """Recorte de jornal: papel-jornal cortado à tesoura (bordas retas levemente tortas), manchete e coluna em BARRAS
    (o texto é esquema — nunca texto falso), fio entre colunas, foto em retícula opcional (pontos inteiros).
    As colunas terminam na mesma altura (a coluna sem foto ganha as linhas que a foto ocupa)."""
    r = semente(f, "jornal", seed, colunas, titulo, foto)
    ang = (f.angulo * 0.5 if angulo is None else angulo)
    w = w or (190.0 if colunas == 1 else 330.0)
    jornal = mistura(f.papel, "#BDB7A8", 0.35)
    tinta_j = mistura(f.fundo, jornal, 0.12)
    pad, gap, lh = 12.0, 10.0, 7.2
    o = []
    y = pad
    if titulo:
        for frac in (0.92, 0.58):
            o.append(f'<path d="{ret(pad, y, (w - 2 * pad) * frac, 13, 0)}" fill="{tinta_j}"/>')
            y += 18
        y += 6
    colw = (w - 2 * pad - (colunas - 1) * gap) / colunas
    n_base = 14 if colunas == 1 else 12
    foto_h = 0.0
    if foto:
        nx_ = max(2, round(colw / 5.0))
        s_ = colw / nx_                          # lado da célula da retícula: caixa = número INTEIRO de células
        ny_ = max(2, round(colw * 0.7 / s_))
        ph = ny_ * s_
        foto_h = ph + 6 + 10
    altura_col = 0.0
    for c in range(colunas):
        x0 = pad + c * (colw + gap)
        yy = y
        if foto and c == 0:
            pid = uid("ret", seed, colw)
            o.append(f'<pattern id="{pid}" x="{x0:.2f}" y="{yy:.2f}" width="{s_:.3f}" height="{s_:.3f}" patternUnits="userSpaceOnUse">'
                     f'<circle cx="{s_ * 0.25:.3f}" cy="{s_ * 0.25:.3f}" r="{s_ * 0.2:.3f}" fill="{tinta_j}"/>'
                     f'<circle cx="{s_ * 0.75:.3f}" cy="{s_ * 0.75:.3f}" r="{s_ * 0.2:.3f}" fill="{tinta_j}"/></pattern>')
            o.append(f'<path d="{ret(x0, yy, colw, ph, 0)}" fill="url(#{pid})"/>')
            o.append(f'<path d="{ret(x0, yy, colw, ph, 0)}" fill="none" stroke="{tinta_j}" stroke-width="0.8"/>')
            yy += ph + 6
            o.append(f'<path d="{ret(x0, yy, colw * 0.7, 3, 0)}" fill="{tinta_j}" fill-opacity="0.7"/>')
            yy += 10
        n = n_base + (round(foto_h / lh) if foto and c > 0 else 0)
        for i in range(n):
            ult = (i + 1) % 5 == 0 or i == n - 1
            ind = 8 if i % 5 == 0 and i else 0
            ww = (colw - ind) * (r.uniform(0.35, 0.7) if ult else 1.0)
            o.append(f'<path d="{ret(x0 + ind, yy, ww, 3.2, 0)}" fill="{tinta_j}" fill-opacity="0.8"/>')
            yy += lh
        altura_col = max(altura_col, yy - y)
    for c in range(1, colunas):      # fio entre colunas (depois, com a altura final)
        xf = pad + c * (colw + gap) - gap / 2
        o.append(_p(f"M{xf:.2f} {y:.2f}V{y + altura_col - 4:.2f}", stroke=tinta_j, sw=0.6))
    H = y + altura_col + pad - 3
    # tesoura: polígono de cantos levemente fora do esquadro
    j = lambda: r.uniform(-2.2, 2.2)  # noqa: E731
    borda = [(j(), j()), (w + j(), j()), (w + j(), H + j()), (j(), H + j())]
    sid = uid("sombra-jornal", seed, w)
    defs = _sombra(sid, 1.5, 2.5, 1.8, 0.35)
    corpo = (f'<g filter="url(#{sid})" transform="rotate({ang:.2f} {w / 2:.2f} {H / 2:.2f})">'
             f'<path d="{poligono(borda)}" fill="{jornal}"/>{"".join(o)}</g>')
    return justo(corpo, f"recorte de jornal · {colunas} col." + (" · manchete" if titulo else "") + (" · foto" if foto else ""),
                 "papel-jornal cortado à tesoura; texto em BARRAS (esquema, nunca texto falso) · bastidor, 'saiu na "
                 "imprensa' só com matéria real", defs=defs)


@amostra(FAM, "recorte de jornal")
def _a_jornal(f):
    return [recorte_jornal(f), recorte_jornal(f, 2, seed=2), recorte_jornal(f, 2, foto=True, seed=3, angulo=3),
            recorte_jornal(f, 1, titulo=False, seed=4, angulo=-2)]


# ================================================================ polaroide, filme
def polaroide(f, w=240.0, angulo=0.0, fita_=False, legenda=None, cor=None):
    """Moldura instantânea na medida REAL do filme (88 × 107 mm; imagem 79 × 79; lados 4,5; topo 6; base 22).
    A área da foto fica VAZIA (é contêiner: a foto real entra por máscara). Legenda curta na base, maiúscula
    ≥ 25 px. Canto reto (raio 0)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    cor = cor or mistura(f.papel, "#FFFFFF", 0.55)
    k = w / 88.0
    s, topo, img, base = 4.5 * k, 6 * k, 79 * k, 22 * k
    H = 107 * k
    sid = uid("sombra-pol", w, angulo)
    defs = _sombra(sid, 2.0, 3.5, 3.0, 0.4)
    o = [f'<path d="{ret(0, 0, w, H, 0)}" fill="{cor}"/>',
         f'<path d="{ret(s, topo, img, img, 0)}" fill="{mistura(f.fundo, ink, 0.07)}"/>',
         f'<path d="{ret(s, topo, img, img, 0)}" fill="none" stroke="{f.fundo}" stroke-opacity="0.5" stroke-width="1"/>']
    if legenda:
        spec = f.fonte_mono
        sz = base * 0.46 / cap(spec)             # maiúscula = 46% da base (≈ 26–27 px em w = 240)
        tw = largura(spec, legenda, sz, 0.06)
        if tw > img * 0.94:                      # não cabe: encolhe (e o registro avisa na nota)
            sz *= img * 0.94 / tw
        o.append(rot_c(f, legenda, sz, w / 2, topo + img + base / 2, mistura(f.fundo, cor, 0.15), spec, 0.06))
    g = f'<g filter="url(#{sid})" transform="rotate({angulo:.2f} {w / 2:.2f} {H / 2:.2f})">{"".join(o)}'
    if fita_:
        r = semente(f, "fita-pol", w)
        fw, fh = w * 0.36, w * 0.085           # cabe na borda de cima (6 mm = 0,068 × w): metade fora, metade dentro
        d = poligono(_forma_fita(r, fw, fh))
        cid = uid("fita-pol-clip", w)
        g += (f'<g transform="translate({w / 2 - fw / 2:.2f} {-fh / 2:.2f}) rotate(-3 {fw / 2:.2f} {fh / 2:.2f})">'
              f'{_crepe(f, r, d, fw, fh, cid)}</g>')
    g += "</g>"
    return justo(g, "polaroide" + (" · fita" if fita_ else "") + (f" · {legenda}" if legenda else "") + (f" · {angulo:+.0f}°" if angulo else ""),
                 "proporção real 88 × 107 mm (foto 79 × 79; base 22) · foto vazia = máscara · bastidor, 'foi assim', "
                 "prova de turma real", defs=defs)


def filme(f, quadros=3, w=440.0, numero_ini=12):
    """Tira de filme 35 mm: quadros de 36 × 24 mm (passo 38), 8 perfurações por quadro (passo 4,75 mm, simétricas em
    volta do centro do quadro), numeração de borda na margem de fora das perfurações. As perfurações são FUROS de
    verdade (evenodd): mostram o que está atrás. Quadros vazios = máscaras de foto."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    k = w / (quadros * 38.0)          # 36 mm + 2 mm de entrequadro
    H = 35 * k
    base = mistura(f.fundo, f.papel, 0.14)
    janela = mistura(f.fundo, f.papel, 0.30)
    pw, ph = 1.98 * k, 2.8 * k
    d = ret(0, 0, w, H, 0)
    for q in range(quadros):
        xc = 1.0 * k + q * 38 * k + 18 * k      # centro do quadro
        for j in range(8):
            x = xc + (j - 3.5) * 4.75 * k - pw / 2
            for y in (2.0 * k, H - 2.0 * k - ph):
                d += ret(x, y, pw, ph, f.raio_sm)   # raio da escala; em furo tão pequeno vira pílula
    o = [f'<path d="{d}" fill="{base}" fill-rule="evenodd"/>']
    for q in range(quadros):
        x = 1.0 * k + q * 38 * k
        o.append(f'<path d="{ret(x, 5.5 * k, 36 * k, 24 * k, 0)}" fill="{janela}"/>')
        n = numero_ini + q
        size = 1.0 * k / 0.698                   # maiúscula = 1 mm (textura de borda, não é lida)
        yc = H - 1.0 * k                         # centro da margem de fora das perfurações (0 a 2 mm)
        o.append(rot_c(f, str(n), size, x + 9 * k, yc, ac, tr=0.06))
        o.append(rot_c(f, f"{n}A", size, x + 27 * k, yc, ac, tr=0.06))
    return justo("".join(o), f"tira de filme 35 mm · {quadros} quadros", "película real (36 × 24 mm, 8 furos por quadro, "
                 "número de borda) · sequência de fotos, bastidor, cronofotografia")


@amostra(FAM, "polaroide e filme")
def _a_pol(f):
    return [polaroide(f), polaroide(f, angulo=-6, fita_=True), polaroide(f, 240, 5, legenda="NOITE 1"),
            filme(f), filme(f, 2, 360)]


# ================================================================ clipe
def clipe(f, L=170.0, angulo=-8.0, cor=None):
    """Clipe de papel nº 2 (Gem): 3 curvas em U — grande embaixo, média em cima, pequena dentro. (O clipe
    prendedor foi removido na revisão 10/2026: parecia uma bolsa.)"""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    cor = cor or mistura(apo, ink, 0.45)
    w = L / 3.1
    R1, R2, R3 = w / 2, w * 0.4, w * 0.3
    # caminho do arame (y para baixo): começa no fim interno esquerdo, desce, U grande, sobe, U de cima, desce, U pequeno, sobe
    xa, xb, xc, xd = 0.0, w, w - 2 * R2, w - 2 * R2 + 2 * R3
    d = (f"M{xa:.2f} {L * 0.24:.2f}V{L - R1:.2f}A{R1:.2f} {R1:.2f} 0 0 0 {xb:.2f} {L - R1:.2f}"
         f"V{R2:.2f}A{R2:.2f} {R2:.2f} 0 0 0 {xc:.2f} {R2:.2f}V{L - R1 - w * 0.32:.2f}"
         f"A{R3:.2f} {R3:.2f} 0 0 0 {xd:.2f} {L - R1 - w * 0.32:.2f}V{L * 0.3:.2f}")
    esp = max(2.5, w * 0.075)
    o = [_p(d, stroke=cor, sw=esp, extra='stroke-linecap="round" stroke-linejoin="round"'),
         _p(d, stroke="#FFFFFF", sw=esp * 0.28, extra='stroke-linecap="round" stroke-opacity="0.45" '
            f'transform="translate({-esp * 0.18:.2f} {-esp * 0.18:.2f})"')]
    cx, cy = w / 2, L / 2
    corpo = f'<g transform="rotate({angulo:.2f} {cx:.2f} {cy:.2f})">{"".join(o)}</g>'
    return justo(corpo, "clipe · gem" + (" · acento" if cor == ac else ""),
                 "clipe de verdade (Gem: 3 curvas em U) · prende foto/ficha na colagem, ícone de anexo")


@amostra(FAM, "clipe")
def _a_clipe(f):
    return [clipe(f), clipe(f, cor=f.acento, angulo=12)]


# ================================================================ índice numerado
def indice(f, n=1, modo="cheio", tam=84.0, digitos=2, fio=0.0):
    """Marcador de índice ("visual index"): número em círculo/quadrado, mono tabular; maiúscula ≥ 25 px (tam 84).
    fio = comprimento do fio de legenda (callout) com ponto na ponta (0 = sem fio). contorno/quadrado/etiqueta têm
    corpo escuro com fio claro: funcionam no fundo escuro E no claro."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    R = tam / 2
    s = f"{n:0{digitos}d}"
    o = []
    size = tam * (0.44 if digitos > 1 else 0.52)
    if modo == "cheio":
        o.append(f'<circle r="{R:.2f}" fill="{ac}"/>')
        tc = f.sobre_acento
        cy = 0.0
    elif modo == "contorno":
        o.append(f'<circle r="{R - t / 2:.2f}" fill="{f.fundo}" stroke="{ink}" stroke-width="{t:.2f}"/>')
        tc = ink
        cy = 0.0
    elif modo == "quadrado":
        o.append(f'<path d="{ret(-R, -R, tam, tam, f.raio_sm)}" fill="{ink}" stroke="{f.fundo}" stroke-opacity="0.6" '
                 f'stroke-width="{t * 0.5:.2f}"/>')
        tc = f.fundo
        cy = 0.0
    else:   # etiqueta: ficha escura com fio de acento em cima (canto reto = destaque)
        W, H = tam, tam * 0.78
        topo = -H / 2
        o.append(f'<path d="{ret(-W / 2, topo, W, H, 0)}" fill="{f.fundo}" stroke="{ink}" stroke-opacity="0.35" '
                 f'stroke-width="{t * 0.5:.2f}"/>')
        o.append(f'<path d="{ret(-W / 2, topo, W, t * 1.6, 0)}" fill="{ac}"/>')
        tc = ink
        cy = t * 0.8
    o.append(rot_c(f, s, size, 0, cy, tc, f.fonte_mono))
    if fio:
        x0 = R + t * 2
        o.append(_p(f"M{x0:.2f} 0H{x0 + fio:.2f}", stroke=apo, sw=t * 0.5))
        o.append(f'<circle cx="{x0 + fio:.2f}" r="{t * 1.5:.2f}" fill="{ac}"/>')
    return justo("".join(o), f"índice {s} · {modo}" + (" · com fio" if fio else ""),
                 "número de inventário (It's Nice That 2026: visual index) · lista de itens, legenda técnica com fio")


def indice_serie(f, n=4, modo="cheio", tam=84.0, passo=None):
    """Série de índices (01–n) numa linha — régua de capítulos/itens."""
    passo = passo or tam * 1.45
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    o = [_p(f"M0 0H{(n - 1) * passo:.2f}", stroke=apo, sw=t * 0.5)]
    R = tam / 2
    size = tam * 0.44
    for i in range(n):
        x = i * passo
        if modo == "cheio" and i == 0:
            o.append(f'<circle cx="{x:.2f}" r="{R:.2f}" fill="{ac}"/>')
            o.append(rot_c(f, f"{i + 1:02d}", size, x, 0, f.sobre_acento))
        else:
            o.append(f'<circle cx="{x:.2f}" r="{R - t / 2:.2f}" fill="{f.fundo}" stroke="{ink}" stroke-width="{t * 0.8:.2f}"/>')
            o.append(rot_c(f, f"{i + 1:02d}", size, x, 0, ink))
    return justo("".join(o), f"índice · série 01–{n:02d}", "índice numerado em linha · capítulos de carrossel, etapas")


@amostra(FAM, "índice numerado")
def _a_indice(f):
    return [indice(f, 1), indice(f, 2, "contorno"), indice(f, 3, "quadrado"), indice(f, 7, "etiqueta"),
            indice(f, 4, "cheio", 84, fio=150), indice_serie(f), indice_serie(f, 3, "contorno", 84)]


# ================================================================ post-it
def post_it(f, cor=None, txt=None, angulo=-3.0, tam=230.0, pautado=False):
    """Bloco adesivo 76 × 76 mm: faixa de cola no topo (um pouco mais escura), canto de baixo levantando (sombra que
    cresce para baixo). txt em curvas na fonte display (bilhete curto, ≤ 2 linhas). Canto reto (raio 0)."""
    t, ink, ac = f.traco, f.tinta, f.acento
    cor = cor or ac
    tc = f.sobre_acento if cor == ac else (f.fundo if luminancia(cor) > 0.4 else ink)
    sid = uid("sombra-postit", tam, angulo, cor)
    defs = (filtro(sid, '<feGaussianBlur stdDeviation="4"/>'))
    o = []
    o.append(f'<path d="{poligono([(tam * 0.06, tam * 0.3), (tam * 0.97, tam * 0.3), (tam * 1.01, tam * 1.04), (tam * 0.05, tam * 1.0)])}" '
             f'fill="#000" fill-opacity="0.45" filter="url(#{sid})"/>')
    o.append(f'<path d="{ret(0, 0, tam, tam, 0)}" fill="{cor}"/>')
    o.append(f'<path d="{ret(0, 0, tam, tam * 0.2, 0)}" fill="#000" fill-opacity="0.06"/>')
    gid = uid("grad-postit", tam, cor)
    defs += (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0.7" stop-color="#000" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="#000" stop-opacity="0.12"/></linearGradient>')
    o.append(f'<path d="{ret(0, 0, tam, tam, 0)}" fill="url(#{gid})"/>')
    if pautado:
        for k in range(5):
            y = tam * (0.36 + 0.13 * k)
            o.append(_p(f"M{tam * 0.08:.2f} {y:.2f}H{tam * 0.92:.2f}", stroke=tc, sw=0.8, extra='stroke-opacity="0.25"'))
    if txt:
        linhas = txt.split("\n")
        sz = tam * 0.2
        for i, ln in enumerate(linhas):
            o.append(rot(f, ln, sz, tam * 0.1, tam * 0.42 + i * sz * 1.05, tc, f.fonte_display, 0.01))
    corpo = f'<g transform="rotate({angulo:.2f} {tam / 2:.2f} {tam / 2:.2f})">{"".join(o)}</g>'
    return justo(corpo, "post-it" + (f" · {txt.splitlines()[0]}" if txt else "") + (" · pautado" if pautado else ""),
                 "bloco adesivo quadrado com faixa de cola e canto levantando · lembrete, bastidor de aula, 'anota aí'",
                 defs=defs)


@amostra(FAM, "post-it")
def _a_postit(f):
    return [post_it(f), post_it(f, txt="NOITE 1\n20H30", angulo=4), post_it(f, f.papel, pautado=True, angulo=-6),
            post_it(f, f.tinta, "AO VIVO", 2, 200)]


# ================================================================ etiquetas de arquivo / pasta
def etiqueta(f, tipo="aba", txt="NOITE 1", cor=None, angulo=0.0):
    """Etiquetas de papelaria (maiúscula do texto = 26 px; a peça cresce para o texto, não o contrário).
    aba = aba plástica de pasta suspensa com cartão, sobre o trilho; pasta = pasta com aba (ficha, dossiê — nunca
    promoção); pendurada = etiqueta com ilhós (furo de verdade) e barbante em laço; porta = porta-etiqueta de
    gaveta (placa com 2 parafusos). Cantos: reto (0) ou raio_sm; nunca raio fora da escala."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    cor = cor or ac
    spec = f.fonte_texto
    sz = CAP_LEGIVEL / cap(spec)
    tr = 0.06
    tw = largura(spec, txt, sz, tr)
    o = []
    if tipo == "aba":
        cw, ch = tw + 40, CAP_LEGIVEL + 28          # cartão
        m = 9.0                                     # moldura plástica em volta do cartão
        W, Ht = cw + 2 * m, ch + m + 6
        marg = 70.0                                 # o trilho passa igual dos dois lados
        yt = Ht - 10                                # a aba entra 10 px por cima do trilho
        o.append(f'<path d="{ret(-marg, yt, W + 2 * marg, 30, 0)}" fill="{cor}"/>')
        o.append(f'<path d="{ret(0, 0, W, Ht, 0, (f.raio_sm, f.raio_sm, 0, 0))}" fill="{mistura(ink, f.fundo, 0.35)}"/>')
        o.append(f'<path d="{ret(m, m, cw, ch, 0)}" fill="{f.papel}"/>')
        o.append(rot_c(f, txt, sz, W / 2, m + ch / 2, f.fundo, spec, tr))
    elif tipo == "pasta":
        acento_cima = any(ch in "ÃÕÁÉÍÓÚÂÊÔÀ" for ch in txt)      # til/acento sobe acima da maiúscula
        tab_h = CAP_LEGIVEL + (34 if acento_cima else 26)
        ab = tw + 56
        W = max(ab + 110, 320.0)
        H = W * 0.64
        # fundo da pasta (aparece como faixa atrás, à direita da aba), aba, frente
        o.append(f'<path d="{ret(0, tab_h * 0.4, W, H - tab_h * 0.4, f.raio)}" fill="{mistura(cor, f.fundo, 0.35)}"/>')
        o.append(f'<path d="{ret(0, 0, ab, tab_h + f.raio, 0, (f.raio_sm, f.raio_sm, 0, 0))}" fill="{cor}"/>')
        o.append(f'<path d="{ret(0, tab_h, W, H - tab_h, f.raio, (0, f.raio, f.raio, f.raio))}" fill="{cor}"/>')
        o.append(rot_c(f, txt, sz, ab / 2, tab_h / 2 + (4 if acento_cima else 0), f.sobre_acento if cor == ac else f.fundo, spec, tr))
    elif tipo == "pendurada":
        H = CAP_LEGIVEL + 66
        corte = H * 0.32
        ex, ey = corte * 0.85, H / 2                # ilhós
        W = corte * 1.5 + tw + 36
        forma = poligono([(corte, 0), (W, 0), (W, H), (corte, H), (0, H - corte), (0, corte)])
        furo = circ(ex, ey, 5.0)
        o.append(f'<path d="{forma}{furo}" fill="{cor}" fill-rule="evenodd"/>')               # furo = geometria
        o.append(f'<path d="{circ(ex, ey, 9.0)}{circ(ex, ey, 5.0)}" fill="{f.papel}" fill-rule="evenodd"/>')   # reforço
        o.append(rot_c(f, txt, sz, corte * 1.5 + (W - corte * 1.5) / 2, H / 2,
                       f.sobre_acento if cor == ac else f.fundo, spec, tr))
        # barbante: laço fechado que sai do ilhós (nenhuma ponta solta)
        laco = (f"M{ex:.2f} {ey:.2f}C{ex - 26:.2f} {ey - 34:.2f} {ex - 84:.2f} {ey - 34:.2f} {ex - 84:.2f} {ey:.2f}"
                f"C{ex - 84:.2f} {ey + 34:.2f} {ex - 26:.2f} {ey + 34:.2f} {ex:.2f} {ey:.2f}Z")
        o.append(_p(laco, stroke=mistura(apo, ink, 0.2), sw=t, extra='stroke-linecap="round" stroke-linejoin="round"'))
    else:   # porta-etiqueta
        zona = 36.0
        W, H = tw + 2 * zona + 28, CAP_LEGIVEL + 40
        metal = mistura(apo, ink, 0.4)
        o.append(f'<path d="{ret(0, 0, W, H, 0)}" fill="{metal}"/>')
        o.append(f'<path d="{ret(zona, 9, W - 2 * zona, H - 18, 0)}" fill="{f.papel}"/>')
        for x in (zona / 2, W - zona / 2):
            o.append(f'<circle cx="{x:.2f}" cy="{H / 2:.2f}" r="6" fill="{mistura(metal, "#000000", 0.35)}"/>'
                     f'<path d="M{x - 3.5:.2f} {H / 2:.2f}H{x + 3.5:.2f}" stroke="{metal}" stroke-width="1.4"/>')
        o.append(rot_c(f, txt, sz, W / 2, H / 2, f.fundo, spec, tr))
    corpo = f'<g transform="rotate({angulo:.2f})">{"".join(o)}</g>'
    return justo(corpo, f"etiqueta · {tipo} · {txt}", "papelaria real (aba de pasta suspensa, pasta, etiqueta com ilhós, "
                 "porta-etiqueta) · ficha, dossiê, data/local; forma conta o que é")


@amostra(FAM, "etiqueta de arquivo")
def _a_etiqueta(f):
    return [etiqueta(f), etiqueta(f, "pasta", "AVALIAÇÃO"), etiqueta(f, "pendurada", "20H30", angulo=-6),
            etiqueta(f, "porta", "BLACK FRIDAY"), etiqueta(f, "aba", "PÓS BLACK", cor=f.tinta)]
