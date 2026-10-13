"""ornamentos.assunto — família "instrumentos do assunto": educação física, saúde e treino (exemplo de assunto).

Regra-mãe (references/elementos.md; pesquisa 14b §5): o elemento é o INSTRUMENTO REAL da área, desenhado fiel — escala,
número e proporção certos. Quem é da área reconhece na hora; um Borg de 1 a 10 ou uma anilha na cor errada reprova.
Cada função diz a origem no `nota` (de onde vem · quando usar). Valores de leitura (ângulo, carga, rodada, pico) são
PARÂMETROS — a amostra mostra um exemplo neutro, nunca um "resultado" inventado.

Fontes dos números (pesquisa 14b §5): goniômetro 5.3 · prumo de Kendall 5.2 · Borg 6–20 5.4 (rótulos do Borg 1998:
6, 7, 9, 11, 13, 15, 17, 19, 20) · RIR 5.5 · zonas de FC 5.6 · periodização 5.18 · tempo 3-1-2-0 5.19 · Tabata 5.20 ·
dobras J&P 5.21 · Jamar 5.22 · Wells 5.23 · marcha 5.12 · anilhas IWF 5.15 · barra 5.16 · proporções segmentares de
Drillis & Contini (1966, em Winter, "Biomechanics and Motor Control of Human Movement") para a figura esquemática.
Ficaram de fora de propósito: simetrógrafo (grade postural) e coluna em pílulas — assinatura do FennerLab (14b §5.27);
o prumo entra só na versão lateral com os 5 pontos (5.2), sem grade.

Também ficam aqui os utilitários comuns às famílias C (dados, colagem, tipograficos, codigos): `justo` (viewBox justo
medido na tinta renderizada), `mistura`, `polar`, `setor`, `rot`, `semente` (determinística, crc32).
"""
import io
import math
import random
import zlib

from .nucleo import amostra, elemento, texto, largura, cap, ret, poligono, polilinha, suave

FAM = "assunto"


# ================================================================ utilitários comuns (famílias C)
def _rgb(c):
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(x * 2 for x in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mistura(a, b, t):
    """Cor entre a e b (t = 0 → a, 1 → b), em sRGB. Rampa da marca sem sair da ficha."""
    ra, rb = _rgb(a), _rgb(b)
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(ra, rb))


def luminancia(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(c)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def semente(f, *salt):
    """Random determinístico (crc32 — o hash() do Python muda a cada processo)."""
    return random.Random(zlib.crc32(repr((f.seed,) + tuple(salt)).encode("utf-8")))


def uid(*salt):
    return "o" + format(zlib.crc32(repr(salt).encode("utf-8")), "08x")


def polar(cx, cy, r, ang):
    """Ponto no círculo; ang em graus, 0 = direita, sentido horário (y para baixo)."""
    a = math.radians(ang)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def arco(cx, cy, r, a0, a1):
    """Arco de a0 até a1 (graus, horário, a1 > a0)."""
    if a1 - a0 >= 359.99:
        x0, y0 = polar(cx, cy, r, a0)
        x1, y1 = polar(cx, cy, r, a0 + 180)
        return (f"M{x0:.2f} {y0:.2f}A{r:.2f} {r:.2f} 0 1 1 {x1:.2f} {y1:.2f}"
                f"A{r:.2f} {r:.2f} 0 1 1 {x0:.2f} {y0:.2f}")
    x0, y0 = polar(cx, cy, r, a0)
    x1, y1 = polar(cx, cy, r, a1)
    return f"M{x0:.2f} {y0:.2f}A{r:.2f} {r:.2f} 0 {1 if a1 - a0 > 180 else 0} 1 {x1:.2f} {y1:.2f}"


def setor(cx, cy, r0, r1, a0, a1):
    """Setor de anel (r0 < r1) de a0 a a1 (graus, horário)."""
    p0, p1 = polar(cx, cy, r1, a0), polar(cx, cy, r1, a1)
    p2, p3 = polar(cx, cy, r0, a1), polar(cx, cy, r0, a0)
    lg = 1 if a1 - a0 > 180 else 0
    return (f"M{p0[0]:.2f} {p0[1]:.2f}A{r1:.2f} {r1:.2f} 0 {lg} 1 {p1[0]:.2f} {p1[1]:.2f}"
            f"L{p2[0]:.2f} {p2[1]:.2f}A{r0:.2f} {r0:.2f} 0 {lg} 0 {p3[0]:.2f} {p3[1]:.2f}Z")


def circ(cx, cy, r):
    return f"M{cx - r:.2f} {cy:.2f}A{r:.2f} {r:.2f} 0 1 0 {cx + r:.2f} {cy:.2f}A{r:.2f} {r:.2f} 0 1 0 {cx - r:.2f} {cy:.2f}Z"


def rot(f, s, size, x, base, fill, spec=None, tr=0.0, anchor="start"):
    """Texto em curvas (mono da ficha por padrão)."""
    svg, _ = texto(spec or f.fonte_mono, s, size, x, base, fill, tr, anchor)
    return svg


def rot_c(f, s, size, cx, cy, fill, spec=None, tr=0.0, ang=0.0):
    """Texto centrado (horizontal e na altura da maiúscula) em (cx, cy), com rotação opcional."""
    spec = spec or f.fonte_mono
    svg = rot(f, s, size, cx, cy + cap(spec) * size / 2, fill, spec, tr, "middle")
    if ang:
        svg = f'<g transform="rotate({ang:.2f} {cx:.2f} {cy:.2f})">{svg}</g>'
    return svg


def num(v, casas=0):
    """Número em pt-BR (vírgula decimal)."""
    s = f"{v:.{casas}f}" if casas else f"{v:g}"
    return s.replace(".", ",")


def _alfa(svg, area, z):
    import numpy as np
    import resvg_py
    from PIL import Image
    x, y, w, h = area
    doc = svg.replace("__VB__", f'viewBox="{x:.3f} {y:.3f} {w:.3f} {h:.3f}" width="{max(1, round(w * z))}" '
                                f'height="{max(1, round(h * z))}"')
    png = resvg_py.svg_to_bytes(svg_string=doc)
    a = np.array(Image.open(io.BytesIO(bytes(png))).convert("RGBA"))[..., 3]
    ys, xs = np.nonzero(a > 6)
    if not len(xs):
        raise ValueError("elemento sem tinta")
    return x + xs.min() / z, y + ys.min() / z, x + (xs.max() + 1) / z, y + (ys.max() + 1) / z


def justo(corpo, nome, nota="", familia=FAM, defs="", pad=0.0, css="", area=(-1600, -1600, 3200, 3200),
          caixa=None, fundo_claro=False):
    """Elemento com viewBox JUSTO na tinta: renderiza (resvg), mede o alfa e recorta (precisão ≈ 0,5 px).
    `caixa` opcional = caixa do objeto em coordenadas do desenho (ex.: sem a sombra)."""
    doc = '<svg xmlns="http://www.w3.org/2000/svg" __VB__>' + (f"<defs>{defs}</defs>" if defs else "") + corpo + "</svg>"
    x0, y0, x1, y1 = _alfa(doc, area, 0.25)
    m = 8
    x0, y0, x1, y1 = _alfa(doc, (x0 - m, y0 - m, x1 - x0 + 2 * m, y1 - y0 + 2 * m), 2.0)
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    w, h = x1 - x0, y1 - y0
    if w > 484 or h > 364:
        print(f"  [aviso] {nome}: {w:.0f}×{h:.0f} (cartão do catálogo = 484×364)")
    g = f'<g transform="translate({-x0:.2f} {-y0:.2f})">{corpo}</g>'
    cx = (caixa[0] - x0, caixa[1] - y0, caixa[2] - x0, caixa[3] - y0) if caixa else (pad, pad, w - pad, h - pad)
    el = elemento(w, h, g, nome, familia, defs=defs, caixa=cx, css=css, nota=nota)
    if fundo_claro:
        el.fundo_claro = True
    return el


def _p(d, fill="none", stroke=None, sw=None, extra=""):
    s = f'<path d="{d}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw:.2f}"'
    return s + (f" {extra}" if extra else "") + "/>"


# ---- helpers locais da revisão 10/2026 (só desta família; não mudam os helpers comuns acima)
def _contraste(a, b):
    la, lb = luminancia(a), luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _txt_sobre(cor, claro, escuro):
    """Cor de texto pelo MAIOR contraste medido (o corte fixo de luminância deixava branco sobre dourado médio)."""
    return claro if _contraste(cor, claro) >= _contraste(cor, escuro) else escuro


def _kg_da_cor(cor, tabela, lim=100.0):
    """Peso cujo código de cor (IWF, kettlebell de competição) se parece com `cor` (distância RGB < lim), ou None.
    Serve para a peça na cor da marca não contradizer o código: dourado ≈ amarelo = 15 kg (anilha) / 16 kg (KB)."""
    r, g, b = _rgb(cor)
    melhor = None
    for kg, c in tabela.items():
        r2, g2, b2 = _rgb(c)
        d = math.sqrt((r - r2) ** 2 + (g - g2) ** 2 + (b - b2) ** 2)
        if d < lim and (melhor is None or d < melhor[0]):
            melhor = (d, kg)
    return melhor[1] if melhor else None


def _sob_braco(a_txt, r, meia, bracos):
    """True se um rótulo (centro no ângulo a_txt, raio r, meia-dimensão `meia`) fica embaixo de algum braço/ponteiro
    [(ângulo, meia largura)] — número coberto não é desenhado (nada de numeral 'fantasma' nem riscado)."""
    for ab, hb in bracos:
        da = math.radians((a_txt - ab + 180) % 360 - 180)
        if abs(da) < math.pi / 2 and r * abs(math.sin(da)) < hb + meia:
            return True
    return False


def _folgas(spec, s, size, tr=0.0):
    """(esquerda, direita): quanto a TINTA do 1º/último glifo fica para dentro da caixa de avanço, em px.
    Alinhar pela tinta (e não pela caixa da fonte) tira o 'quase alinhado' de 1–2 px do texto vs. fio/barra (D9)."""
    from fontTools.pens.boundsPen import BoundsPen
    from .nucleo import _font as _fonte
    fnt = _fonte(spec)
    names, adv = fnt.advances(s, size, tr)
    k = size / fnt.upm

    def limites(g):
        bp = BoundsPen(fnt.gs)
        fnt.gs[g].draw(bp)
        return bp.bounds
    b0, b1 = limites(names[0]), limites(names[-1])
    esq = (b0[0] * k) if b0 else 0.0
    dir_ = (sum(adv) - (sum(adv[:-1]) + b1[2] * k)) if b1 else 0.0
    return esq, dir_


def rot_tinta(f, s, size, x, base, fill, spec=None, tr=0.0, anchor="start"):
    """Como `rot`, mas alinhado pela TINTA: com anchor start a tinta começa em x; com end, termina em x
    (middle não muda). Local desta família — `rot` comum continua igual para as outras famílias."""
    spec = spec or f.fonte_mono
    if anchor != "middle" and s.strip():
        e, d = _folgas(spec, s, size, tr)
        x = x - e if anchor == "start" else x + d
    return rot(f, s, size, x, base, fill, spec, tr, anchor)


# ================================================================ goniômetro (14b 5.3)
def goniometro(f, angulo=90, modo="contorno", completo=False, rotulo=True, R=140.0):
    """Transferidor 0–180° (ou círculo), tracinho a 5°, longo a 10°, número a 30° (dupla numeração no meio anel),
    braço fixo + braço móvel com janela e índice, fulcro no centro. modo: contorno | cheio | minimo.
    Revisão 10/2026: braços OPACOS em pílula que nascem no centro do fulcro (nenhuma ponta aparece atrás do pivô);
    número coberto por um braço não é desenhado (nada de numeral 'fantasma'); no círculo, os números da metade de
    baixo ficam em pé; 0° e 180° são a própria linha de base (sem tique em cima do braço); o arco do ângulo passa por
    BAIXO dos braços e só aparece no vão entre eles."""
    t = f.traco
    ink, ac = f.tinta, f.acento
    cheio, minimo = modo == "cheio", modo == "minimo"
    tick = f.sobre_acento if cheio else ink
    aw, L = R * 0.17, R * 1.62
    lmaior, lmenor = R * 0.11, R * 0.06
    hw = t if minimo else aw / 2 + t / 2          # meia largura do braço (com o contorno)
    bracos = [(180, hw), (180 + angulo, hw)]
    o = []

    def braco(ang, movel):
        if minimo:
            return (f'<g transform="rotate({ang:.2f})">'
                    + _p(f"M0 0H{L:.2f}", stroke=ink, sw=2 * t, extra='stroke-linecap="round"') + "</g>")
        d = ret(-aw / 2, -aw / 2, L + aw / 2, aw, aw / 2)          # pílula; a ponta redonda é o centro do fulcro
        if movel:   # janela sobre a escala (furo de verdade) — evenodd
            d += ret(R - lmaior - aw * 0.5, -aw * 0.24, lmaior + aw * 0.62, aw * 0.48, aw * 0.24)
        if cheio:
            return (f'<path d="{d}" fill="{ink if movel else ac}" fill-rule="evenodd" '
                    f'transform="rotate({ang:.2f})"/>')
        return (f'<path d="{d}" fill="{f.fundo}" fill-rule="evenodd" stroke="{ink}" stroke-width="{t:.2f}" '
                f'transform="rotate({ang:.2f})"/>')

    if not minimo:
        if completo:
            d = circ(0, 0, R)
        else:
            d = f"M{-R:.2f} 0A{R:.2f} {R:.2f} 0 0 1 {R:.2f} 0Z"
        o.append(_p(d, fill=ac) if cheio else _p(d, fill=f.fundo, stroke=ink, sw=t, extra='stroke-linejoin="round"'))
    # escala (0° e 180° são a linha de base; no círculo o 0° fica sob o braço fixo)
    vmax = 360 if completo else 180
    edge = R - (0 if (cheio or minimo) else t / 2)
    dm, dM = "", ""
    for v in range(0, vmax + (0 if completo else 1), 5):
        if not completo and v in (0, 180):
            continue
        a = 180 + v
        lng = v % 10 == 0
        p0, p1 = polar(0, 0, edge - (lmaior if lng else lmenor), a), polar(0, 0, edge, a)
        seg = f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}"
        if lng:
            dM += seg
        else:
            dm += seg
    o.append(_p(dm, stroke=tick, sw=t * 0.5))
    o.append(_p(dM, stroke=tick, sw=t * 0.75))
    if minimo and not completo:     # linha de base do lado do 180° (o lado do 0° é o braço fixo)
        o.append(_p(f"M0 0H{edge:.2f}", stroke=ink, sw=t * 0.5, extra='stroke-opacity="0.55"'))
    if not minimo:
        o.append(_p(arco(0, 0, edge - lmaior, 180, 180 + vmax) if not completo else circ(0, 0, edge - lmaior),
                    stroke=tick, sw=t * 0.4, extra='stroke-opacity="0.55"'))
    ns = R * 0.085
    rn = edge - lmaior - ns * 1.05
    for v in range(0, vmax + (0 if completo else 1), 30):
        lab = v if v <= 180 else 360 - v
        if not completo and v in (0, 180):   # 0 e 180 em pé, logo acima da base (como no transferidor impresso)
            wl = largura(f.fonte_mono, str(lab), ns)
            x = (edge - lmaior - wl / 2 - ns * 0.15) * (-1 if v == 0 else 1)
            yl = -(aw / 2 + t / 2 + ns * 0.45 + cap(f.fonte_mono) * ns / 2)
            o.append(rot_c(f, str(lab), ns, x, yl, tick))
            continue
        wl = largura(f.fonte_mono, str(lab), ns)
        if _sob_braco(180 + v, rn, wl / 2 + t, bracos):
            continue
        giro = v - 90 + (180 if v > 180 else 0)     # metade de baixo do círculo: número em pé
        o.append(rot_c(f, str(lab), ns, *polar(0, 0, rn, 180 + v), tick, ang=giro))
    if not completo and not minimo:     # numeração dupla (lê nos dois sentidos)
        ns2 = R * 0.07
        rn2 = rn - ns * 1.25
        for v in range(30, 180, 30):
            wl = largura(f.fonte_mono, str(180 - v), ns2)
            if _sob_braco(180 + v, rn2, wl / 2 + t, bracos):
                continue
            o.append('<g opacity="0.55">' + rot_c(f, str(180 - v), ns2, *polar(0, 0, rn2, 180 + v), tick,
                                                  ang=v - 90) + "</g>")
    # ângulo medido: setor + arco por BAIXO dos braços (o que aparece é só o vão entre eles — nunca um "toco")
    if angulo:
        ra = R * 0.5
        hwa = aw / 2 + t if not minimo else t * 1.5
        if angulo - 2 * math.degrees(math.asin(min(1.0, hwa / ra))) >= 12:
            a0, a1 = 180, 180 + angulo
            p0, p1 = polar(0, 0, ra, a0), polar(0, 0, ra, a1)
            setor_d = f"M0 0L{p0[0]:.2f} {p0[1]:.2f}A{ra:.2f} {ra:.2f} 0 {1 if angulo > 180 else 0} 1 {p1[0]:.2f} {p1[1]:.2f}Z"
            if not minimo:
                o.append(_p(setor_d, fill=mistura(f.fundo, ac, 0.3) if not cheio else mistura(ac, f.fundo, 0.3)))
            o.append(_p(arco(0, 0, ra, a0, a1), stroke=ac if not cheio else tick, sw=2 * t,
                        extra='stroke-linecap="butt"'))
    o.append(braco(180, False))
    o.append(braco(180 + angulo, True))
    if not minimo:   # índice de leitura na janela
        p0, p1 = polar(0, 0, R - lmaior - aw * 0.45, 180 + angulo), polar(0, 0, R + aw * 0.05, 180 + angulo)
        o.append(_p(f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}", stroke=ac if not cheio else f.fundo,
                    sw=t * 0.8))
    # fulcro
    rf = aw * 0.36
    o.append(f'<circle r="{rf:.2f}" fill="{f.fundo if not cheio else ink}" stroke="{ink}" stroke-width="{t:.2f}"/>'
             f'<circle r="{rf * 0.34:.2f}" fill="{ac if not cheio else f.fundo}"/>')
    if rotulo and not completo:
        sz = R * 0.56
        wn, wg = largura(f.fonte_display, str(angulo), sz), largura(f.fonte_display, "°", sz)
        x0 = -(wn + wg * 0.55) / 2
        base = aw / 2 + R * 0.16 + cap(f.fonte_display) * sz
        o.append(rot_tinta(f, str(angulo), sz, x0, base, ink, f.fonte_display))
        o.append(rot_tinta(f, "°", sz, x0 + wn - wg * 0.3, base, ac, f.fonte_display))
    nome = f"goniômetro {'360' if completo else '180'}° · {modo}" + (f" · {angulo}°" if angulo else "")
    return justo("".join(o), nome, "transferidor real: 5° / 10° / número a 30°, 2 braços no fulcro · moldura de "
                 "número, carregamento (braço gira), selo de precisão")


@amostra(FAM, "goniômetro")
def _a_gonio(f):
    return [goniometro(f, 90, "contorno"), goniometro(f, 45, "cheio", rotulo=False),
            goniometro(f, 120, "minimo", rotulo=False), goniometro(f, 30, "contorno", completo=True, rotulo=False)]


# ================================================================ Borg 6–20 (14b 5.4)
BORG = {6: "Nenhum esforço", 7: "Extremamente leve", 9: "Muito leve", 11: "Leve", 13: "Um pouco intenso",
        15: "Intenso (pesado)", 17: "Muito intenso", 19: "Extremamente intenso", 20: "Esforço máximo"}


def _rampa(f, i, n, ini=0.16):
    """Rampa da marca: fundo clareado → acento (nunca arco-íris)."""
    base = mistura(f.fundo, f.tinta, ini)
    return mistura(base, f.acento, i / max(1, n - 1))


def borg(f, valor=None, modo="folha", passo=None):
    """Escala de Borg 6–20 (15 degraus). folha = vertical com os rótulos oficiais (6 no topo, como na folha impressa);
    barra = horizontal 6 → 20; degraus = 15 barras crescentes (mínimo)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    o = []
    passo = passo or (22.0 if modo == "folha" else 30.0)
    ns = passo * (0.6 if modo == "folha" else 0.52)
    if modo == "folha":
        xn, xc, cw, xl = passo * 1.5, passo * 1.85, passo * 1.2, passo * 3.5
        for i, n in enumerate(range(6, 21)):
            y = i * passo
            sel = valor == n
            cy = y + passo / 2
            cor_n = ac if sel else ((ink if n in BORG else apo) if valor is None else apo)
            o.append(rot_tinta(f, str(n), ns, xn, cy + cap(f.fonte_mono) * ns / 2, cor_n, anchor="end"))
            o.append(f'<path d="{ret(xc, y + 1, cw, passo - 2, 0)}" fill="{_rampa(f, i, 15)}"/>')
            if n in BORG:
                o.append(rot_tinta(f, BORG[n], ns, xl, cy + cap(f.fonte_texto) * ns / 2,
                             ac if sel else (ink if valor is None else apo), f.fonte_texto))
            if sel:
                o.append(_p(ret(xc + t / 2, y + 1 + t / 2, cw - t, passo - 2 - t, 0), stroke=ink, sw=t))
                tri = [(passo * 0.42, cy), (0, cy - passo * 0.26), (0, cy + passo * 0.26)]
                o.append(f'<path d="{poligono(tri)}" fill="{ac}"/>')
        nome = "Borg 6–20 · folha" + (f" · {valor}" if valor else "")
        nota = "15 degraus, rótulos do Borg 1998 só em 6-7-9-11-13-15-17-19-20 · progresso de série, divisor"
    elif modo == "barra":
        cw, ch = passo * 0.95, passo * 1.25
        for i, n in enumerate(range(6, 21)):
            x = i * cw
            sel = valor == n
            o.append(f'<path d="{ret(x + 1, 0, cw - 2, ch, 0)}" fill="{_rampa(f, i, 15)}"/>')
            cor = ac if sel else (ink if n in BORG else apo)
            o.append(rot_tinta(f, str(n), ns * 0.82, x + cw / 2, ch + passo * 0.42 + cap(f.fonte_mono) * ns * 0.82, cor,
                         anchor="middle"))
            if sel:
                o.append(_p(ret(x + 1 + t / 2, t / 2, cw - 2 - t, ch - t, 0), stroke=ink, sw=t))
                o.append(f'<path d="{poligono([(x + cw / 2, -t * 1.2), (x + cw / 2 - ch * 0.2, -t * 1.2 - ch * 0.3), (x + cw / 2 + ch * 0.2, -t * 1.2 - ch * 0.3)])}" fill="{ac}"/>')
        nome = "Borg 6–20 · barra" + (f" · {valor}" if valor else "")
        nota = "6 → 20 na horizontal; números com rótulo oficial em tinta, os outros em apoio · barra de intensidade"
    else:
        bw, gap, hmax = passo * 0.62, passo * 0.26, passo * 5.2
        for i, n in enumerate(range(6, 21)):
            h = hmax * (0.18 + 0.82 * i / 14)
            x = i * (bw + gap)
            cor = ac if (valor is not None and n <= valor) else (_rampa(f, i, 15) if valor is None else
                                                                   mistura(f.fundo, ink, 0.18))
            o.append(f'<path d="{ret(x, hmax - h, bw, h, 0)}" fill="{cor}"/>')
        o.append(rot_tinta(f, "6", ns, bw / 2, hmax + passo * 0.4 + cap(f.fonte_mono) * ns, ink, anchor="middle"))
        o.append(rot_tinta(f, "20", ns, 14 * (bw + gap) + bw / 2, hmax + passo * 0.4 + cap(f.fonte_mono) * ns, ink,
                     anchor="middle"))
        nome = "Borg 6–20 · degraus" + (f" · até {valor}" if valor else "")
        nota = "15 degraus crescentes (nunca 0–10: a CR10 é outra escala) · progresso, carregamento"
    return justo("".join(o), nome, nota)


@amostra(FAM, "Borg 6–20")
def _a_borg(f):
    return [borg(f), borg(f, 15), borg(f, None, "barra"), borg(f, 13, "barra"), borg(f, None, "degraus"),
            borg(f, 17, "degraus")]


# ================================================================ zonas de frequência cardíaca (14b 5.6)
ZONAS = [(50, 60, "Z1", "MUITO LEVE"), (60, 70, "Z2", "LEVE"), (70, 80, "Z3", "MODERADA"), (80, 90, "Z4", "INTENSA"),
         (90, 100, "Z5", "MÁXIMA")]


def zonas_fc(f, modo="faixa", ativa=None, w=470.0):
    """5 faixas IGUAIS de 50–100% da FCmáx, na rampa da marca. modo: faixa | pilha | arco | degraus.
    ativa = 1..5 destaca a zona (parâmetro; sem ela, só a rampa)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    o = []

    def cor(i):
        if ativa is None:
            return _rampa(f, i, 5, 0.2)
        return ac if i + 1 == ativa else mistura(f.fundo, ink, 0.12 + 0.05 * i)

    def cor_txt(i, sobre=True):
        c = cor(i)
        return _txt_sobre(c, ink, f.fundo)

    if modo == "faixa":
        sw, h = w / 5, u * 1.9
        for i, (a, b, z, nm) in enumerate(ZONAS):
            x = i * sw
            o.append(f'<path d="{ret(x + (1 if i else 0), 0, sw - (1 if i else 0) - (1 if i < 4 else 0), h, 0)}" fill="{cor(i)}"/>')
            o.append(rot_c(f, z, u * 0.72, x + sw / 2, h / 2, cor_txt(i), f.fonte_texto, 0.04))
        ns = u * 0.56
        for i in range(6):
            x = i * sw
            xt = min(max(x, t * 0.3), w - t * 0.3)
            o.append(_p(f"M{xt:.2f} {h:.2f}V{h + u * 0.45:.2f}", stroke=apo, sw=t * 0.6))
            o.append(rot_tinta(f, str(50 + 10 * i), ns, x, h + u * 0.6 + cap(f.fonte_mono) * ns, ink,
                         anchor="start" if i == 0 else "end" if i == 5 else "middle"))
        o.append(rot_tinta(f, "% DA FC MÁX", ns * 0.9, 0, -u * 0.55, apo, f.fonte_texto, 0.08))
        nome = "zonas de FC · faixa" + (f" · Z{ativa}" if ativa else "")
    elif modo == "pilha":
        rh, bw = u * 1.55, u * 2.2
        for k, (a, b, z, nm) in enumerate(reversed(ZONAS)):
            i = 4 - k
            y = k * rh
            o.append(f'<path d="{ret(u * 3.0, y + 1, bw, rh - 2, 0)}" fill="{cor(i)}"/>')
            o.append(rot_c(f, z, u * 0.62, u * 3.0 + bw / 2, y + rh / 2, cor_txt(i), f.fonte_texto, 0.04))
            o.append(rot_tinta(f, f"{a}–{b}%", u * 0.56, u * 2.55, y + rh / 2 + cap(f.fonte_mono) * u * 0.28,
                         ink if ativa in (None, i + 1) else apo, anchor="end"))
            o.append(rot_tinta(f, nm, u * 0.58, u * 3.0 + bw + u * 0.6, y + rh / 2 + cap(f.fonte_texto) * u * 0.29,
                         (ac if ativa == i + 1 else ink) if ativa in (None, i + 1) else apo, f.fonte_texto, 0.08))
        nome = "zonas de FC · pilha" + (f" · Z{ativa}" if ativa else "")
    elif modo == "arco":
        R, e = w * 0.42, w * 0.1
        for i, (a, b, z, nm) in enumerate(ZONAS):
            a0, a1 = 180 + i * 36 + 0.8, 180 + (i + 1) * 36 - 0.8
            o.append(f'<path d="{setor(0, 0, R - e, R, a0, a1)}" fill="{cor(i)}"/>')
            o.append(rot_c(f, z, u * 0.62, *polar(0, 0, R - e / 2, 180 + i * 36 + 18), cor_txt(i), f.fonte_texto,
                           0.02, ang=i * 36 + 18 - 90))
        for i in range(6):
            p = polar(0, 0, R + u * 0.95, 180 + i * 36)
            o.append(rot_c(f, str(50 + 10 * i), u * 0.56, *p, ink))
        o.append(rot_tinta(f, "% FC MÁX", u * 0.56, 0, -u * 0.2, apo, f.fonte_texto, 0.08, "middle"))
        if ativa:
            o.append(rot_tinta(f, ZONAS[ativa - 1][3], u * 0.9, 0, -u * 1.5, ac, f.fonte_texto, 0.04, "middle"))
        nome = "zonas de FC · arco" + (f" · Z{ativa}" if ativa else "")
    else:
        bw, gap = u * 1.6, u * 0.5
        hmax = u * 7
        for i, (a, b, z, nm) in enumerate(ZONAS):
            h = hmax * b / 100
            x = i * (bw + gap)
            o.append(f'<path d="{ret(x, hmax - h, bw, h, 0)}" fill="{cor(i)}"/>')
            o.append(rot_tinta(f, z, u * 0.56, x + bw / 2, hmax + u * 0.5 + cap(f.fonte_texto) * u * 0.56, ink,
                         f.fonte_texto, 0.04, "middle"))
        nome = "zonas de FC · degraus (altura = limite %)" + (f" · Z{ativa}" if ativa else "")
    return justo("".join(o), nome, "5 faixas iguais de 10 pontos (50–100% FCmáx), rampa da marca, nunca arco-íris · "
                 "fundo em faixas, ícone de intensidade")


@amostra(FAM, "zonas de FC")
def _a_zonas(f):
    return [zonas_fc(f), zonas_fc(f, "faixa", 4), zonas_fc(f, "pilha"), zonas_fc(f, "pilha", 3),
            zonas_fc(f, "arco"), zonas_fc(f, "arco", 5), zonas_fc(f, "degraus")]


# ================================================================ Tabata 20/10 × 8 (14b 5.20)
def tabata(f, rodada=None, modo="anel", R=150.0, centro=True):
    """240 s em 360° = 1,5°/s → 8 × (30° de esforço + 15° de pausa), começando no topo. rodada = 1..8 (parâmetro):
    feitas no acento, a atual em contorno, as que faltam apagadas. modo: anel | linha (240 s em régua)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    o = []
    apag = mistura(f.fundo, ink, 0.2)
    if modo == "anel":
        e = R * 0.2
        for i in range(8):
            a0 = -90 + i * 45
            d = setor(0, 0, R - e, R, a0, a0 + 30)
            if rodada is None or i + 1 < rodada:
                o.append(f'<path d="{d}" fill="{ac}"/>')
            elif i + 1 == rodada:
                o.append(f'<path d="{d}" fill="{mistura(f.fundo, ac, 0.25)}" stroke="{ac}" stroke-width="{t:.2f}"/>')
            else:
                o.append(f'<path d="{d}" fill="{apag}"/>')
            o.append(_p(arco(0, 0, R - e / 2, a0 + 30 + 3, a0 + 45 - 3), stroke=apo, sw=t * 0.6))
        for k in range(24):     # tique a cada 10 s (15°)
            p0, p1 = polar(0, 0, R + u * 0.3, -90 + k * 15), polar(0, 0, R + u * (0.3 + (0.5 if k % 6 == 0 else 0.25)), -90 + k * 15)
            o.append(_p(f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}", stroke=ink if k % 6 == 0 else apo,
                        sw=t * 0.6))
        if centro:
            sz = R * 0.42
            o.append(rot_tinta(f, "20/10", sz, 0, cap(f.fonte_display) * sz * 0.32, ink, f.fonte_display, 0.0, "middle"))
            lab = f"RODADA {rodada}/8" if rodada else "× 8 · 4 min"
            o.append(rot_tinta(f, lab, R * 0.1, 0, cap(f.fonte_display) * sz * 0.32 + R * 0.24, ac if rodada else apo,
                         tr=0.06, anchor="middle"))
        nome = "Tabata · anel" + (f" · rodada {rodada}" if rodada else "") + ("" if centro else " · mínimo")
    else:
        W = R * 3.2
        k = W / 240
        h = u * 1.1
        for i in range(8):
            x = i * 30 * k
            if rodada is None or i + 1 < rodada:
                o.append(f'<path d="{ret(x, 0, 20 * k, h, 0)}" fill="{ac}"/>')
            elif i + 1 == rodada:
                o.append(f'<path d="{ret(x + t / 2, t / 2, 20 * k - t, h - t, 0)}" fill="none" stroke="{ac}" stroke-width="{t:.2f}"/>')
            else:
                o.append(f'<path d="{ret(x, 0, 20 * k, h, 0)}" fill="{apag}"/>')
            o.append(_p(f"M{x + 20 * k + 3:.2f} {h / 2:.2f}H{x + 30 * k - (3 if i < 7 else 0):.2f}", stroke=apo, sw=t * 0.6))
        for s in range(0, 241, 10):
            x = s * k
            lng = s % 60 == 0
            xt = min(max(x, t * 0.3), W - t * 0.3)
            o.append(_p(f"M{xt:.2f} {h + u * 0.3:.2f}V{h + u * (0.3 + (0.55 if lng else 0.25)):.2f}",
                        stroke=ink if lng else apo, sw=t * 0.6))
            if lng:
                o.append(rot_tinta(f, f"{s // 60}:00", u * 0.5, x, h + u * 1.45 + cap(f.fonte_mono) * u * 0.5, ink,
                             anchor="start" if s == 0 else "end" if s == 240 else "middle"))
        o.append(rot_tinta(f, "20 s ESFORÇO · 10 s PAUSA · × 8", u * 0.5, 0, -u * 0.45, apo, tr=0.04))
        nome = "Tabata · régua 240 s" + (f" · rodada {rodada}" if rodada else "")
    return justo("".join(o), nome, "protocolo Tabata (1996): 20 s + 10 s × 8 = 4 min; anel 30° + 15° · "
                 "carregamento, contagem regressiva, selo")


@amostra(FAM, "Tabata")
def _a_tabata(f):
    return [tabata(f), tabata(f, 3), tabata(f, centro=False), tabata(f, None, "linha"), tabata(f, 5, "linha")]


# ================================================================ cronômetro (intervalo)
def cronometro(f, segundos=20, modo="contorno", R=128.0):
    """Cronômetro analógico: mostrador de 60 s (tique a 1 s, longo a 5 s, número a 5 s com 60 no topo), contador de
    minutos 0–30, coroa e botão de zerar. segundos = parâmetro (o arco no acento marca o trecho decorrido).
    Revisão 10/2026: números POR FORA dos tiques (anel externo) e o ponteiro termina na ponta dos tiques — nunca
    atravessa um número; submostrador menor, fora do caminho do arco; unidade 'min' em minúscula (SI)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    cheio = modo == "cheio"
    face = ink if cheio else f.fundo
    tk = f.fundo if cheio else ink
    o = []
    # coroa + botão
    o.append(f'<path d="{ret(-R * 0.07, -R - R * 0.16, R * 0.14, R * 0.18, 0)}" fill="{ink}"/>')
    o.append(f'<path d="{ret(-R * 0.17, -R - R * 0.3, R * 0.34, R * 0.15, R * 0.05)}" fill="{ink}"/>')
    o.append(f'<g transform="rotate(42)"><path d="{ret(-R * 0.055, -R - R * 0.12, R * 0.11, R * 0.15, 0)}" fill="{ink}"/>'
             f'<path d="{ret(-R * 0.1, -R - R * 0.2, R * 0.2, R * 0.09, R * 0.03)}" fill="{ink}"/></g>')
    o.append(f'<circle r="{R:.2f}" fill="{face}" stroke="{ink}" stroke-width="{2 * t:.2f}"/>')
    ns = R * 0.105
    r_in = R - t                                  # borda interna do aro
    r_num = r_in - t * 1.7 - ns * 0.62            # centro dos números (anel externo)
    re = r_num - ns * 0.62 - t * 2.2              # ponta externa dos tiques (folga p/ o número de 2 dígitos)
    lg, cu = R * 0.1, R * 0.05
    dm = dM = ""
    for s in range(60):
        a = -90 + s * 6
        lng = s % 5 == 0
        p0, p1 = polar(0, 0, re - (lg if lng else cu), a), polar(0, 0, re, a)
        seg = f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}"
        if lng:
            dM += seg
        else:
            dm += seg
    o.append(_p(dm, stroke=tk, sw=t * 0.45) + _p(dM, stroke=tk, sw=t * 0.85))
    for s in range(5, 61, 5):
        o.append(rot_c(f, str(s), ns, *polar(0, 0, r_num, -90 + s * 6), tk))
    # contador de minutos (0–30): pequeno, abaixo do centro, dentro do arco
    sc, sr = R * 0.38, R * 0.16
    o.append(f'<circle cy="{sc:.2f}" r="{sr:.2f}" fill="none" stroke="{tk}" stroke-width="{t * 0.5:.2f}"/>')
    d = ""
    for m in range(30):
        p0, p1 = polar(0, sc, sr - (sr * 0.28 if m % 5 == 0 else sr * 0.14), -90 + m * 12), polar(0, sc, sr, -90 + m * 12)
        d += f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}"
    o.append(_p(d, stroke=tk, sw=t * 0.4))
    o.append(f'<path d="M0 {sc:.2f}L0 {sc - sr * 0.74:.2f}" stroke="{tk}" stroke-width="{t * 0.6:.2f}" stroke-linecap="round"/>')
    # trecho decorrido + ponteiro (a ponta chega na ponta dos tiques, antes dos números)
    if segundos:
        o.append(_p(arco(0, 0, re - lg - t * 2.4, -90, -90 + segundos * 6), stroke=ac, sw=t * 1.4,
                    extra='stroke-linecap="butt"'))
    a = -90 + segundos * 6
    p0, p1 = polar(0, 0, -R * 0.2, a), polar(0, 0, re, a)
    o.append(_p(f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}", stroke=ac, sw=t * 0.9, extra='stroke-linecap="round"'))
    o.append(f'<circle r="{R * 0.05:.2f}" fill="{ac}"/><circle r="{R * 0.018:.2f}" fill="{face}"/>')
    return justo("".join(o), f"cronômetro · {modo} · {segundos} s",
                 "mostrador 60 s real (1 s / 5 s), contador 0–30 min · tempo de intervalo, contagem, 'cada segundo conta'")


@amostra(FAM, "cronômetro")
def _a_crono(f):
    return [cronometro(f, 20), cronometro(f, 45, "cheio"), cronometro(f, 0)]


# ================================================================ dinamômetro de preensão (Jamar) (14b 5.22)
def dinamometro(f, pico=None, R=150.0):
    """Mostrador duplo do dinamômetro hidráulico: kg dentro (0–90, tique a 2 kg) e lb fora (0–200, tique a 5 lb), 0 no
    topo; ponteiro principal + ponteiro de PICO no acento (é o que fica parado depois do teste). pico = parâmetro.
    Revisão 10/2026: números de kg e de lb por FORA dos tiques e em pé; os ponteiros terminam nos tiques de kg (nunca
    alcançam um número); sem fio cinza por baixo dos números; 'kg' e 'lb' na folga entre o 90 e o 0."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    gk = 3.5                    # graus por kg (90 kg = 315°)
    gl = gk * 0.45359237        # graus por lb (mesma escala física)
    o = [f'<circle r="{R:.2f}" fill="{f.fundo}" stroke="{ink}" stroke-width="{2 * t:.2f}"/>']
    rl = R - 2.5 * t                       # ponta externa dos tiques de lb
    r_lbn, r_kgn = R * 0.80, R * 0.656     # anel dos números de lb e de kg
    rk_out = R * 0.575                     # ponta externa dos tiques de kg
    d1 = d2 = ""
    for lb in range(0, 201, 5):
        a = -90 + lb * gl
        lng = lb % 20 == 0
        p0, p1 = polar(0, 0, rl - (R * 0.075 if lng else R * 0.04), a), polar(0, 0, rl, a)
        d1 += f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}"
        if lng:
            o.append(rot_c(f, str(lb), R * 0.07, *polar(0, 0, r_lbn, a), apo))
    for kg in range(0, 91, 2):
        a = -90 + kg * gk
        lng = kg % 10 == 0
        p0, p1 = polar(0, 0, rk_out - (R * 0.09 if lng else R * 0.045), a), polar(0, 0, rk_out, a)
        d2 += f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}"
        if lng:
            o.append(rot_c(f, str(kg), R * 0.09, *polar(0, 0, r_kgn, a), ink))
    o.append(_p(d1, stroke=apo, sw=t * 0.5) + _p(d2, stroke=ink, sw=t * 0.7))
    a_u = -90 + 337.5                      # meio da folga entre o 90 kg (315°) e o 0
    o.append(rot_c(f, "kg", R * 0.085, *polar(0, 0, r_kgn, a_u), ink, f.fonte_texto))
    o.append(rot_c(f, "lb", R * 0.085, *polar(0, 0, r_lbn, a_u), apo, f.fonte_texto))

    def ponteiro(kg, cor, larg, comp):
        a = -90 + kg * gk
        p0, p1 = polar(0, 0, -R * 0.14, a), polar(0, 0, comp, a)
        return _p(f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}", stroke=cor, sw=larg, extra='stroke-linecap="round"')
    if pico:
        o.append(ponteiro(pico, ac, t * 1.1, rk_out - R * 0.005))
    o.append(ponteiro(0, ink, t * 1.1, rk_out - R * 0.05))
    o.append(f'<circle r="{R * 0.06:.2f}" fill="{ink}"/><circle r="{R * 0.025:.2f}" fill="{ac}"/>')
    return justo("".join(o), "dinamômetro (Jamar)" + (f" · pico {pico} kg" if pico else " · em repouso"),
                 "kg dentro / lb fora, ponteiro de pico em outra cor; nunca velocímetro · moldura de KPI de força")


@amostra(FAM, "dinamômetro")
def _a_dina(f):
    return [dinamometro(f), dinamometro(f, 38)]


# ================================================================ corpo esquemático (proporções reais)
# Drillis & Contini (1966), em Winter: alturas em fração da estatura H (do chão)
ALT = {"topo": 1.0, "queixo": 0.870, "ombro": 0.818, "torax": 0.720, "cotovelo": 0.630, "trocanter": 0.530,
       "punho": 0.485, "dedos": 0.377, "joelho": 0.285, "tornozelo": 0.039}
LARG = {"ombros": 0.259, "quadril": 0.191}


def _figura(f, H, x0=0.0, costas=False, cor=None, sw=None):
    """Figura de frente (ou de costas) em segmentos + articulações, nas proporções de Drillis & Contini.
    Devolve (svg, pontos). Chaves *_d = lado DIREITO do sujeito (de frente fica à esquerda de quem olha)."""
    ink = cor or f.tinta
    sw = sw or f.traco
    y = lambda fr: (1 - fr) * H  # noqa: E731
    P = {}
    for lado in ("d", "e"):
        s = -1 if lado == "d" else 1
        if costas:
            s = -s
        P["ombro_" + lado] = (x0 + s * LARG["ombros"] / 2 * H, y(ALT["ombro"]))
        P["cotovelo_" + lado] = (x0 + s * 0.15 * H, y(ALT["cotovelo"]))
        P["punho_" + lado] = (x0 + s * 0.163 * H, y(ALT["punho"]))
        P["dedos_" + lado] = (x0 + s * 0.17 * H, y(ALT["dedos"]))
        P["quadril_" + lado] = (x0 + s * LARG["quadril"] / 2 * H, y(ALT["trocanter"]))
        P["joelho_" + lado] = (x0 + s * 0.082 * H, y(ALT["joelho"]))
        P["tornozelo_" + lado] = (x0 + s * 0.075 * H, y(ALT["tornozelo"]))
    P["queixo"] = (x0, y(ALT["queixo"]))
    P["pescoco"] = (x0, y(ALT["ombro"]))
    o = []
    ry = ((1 - ALT["queixo"]) * H - sw / 2) / 2          # a elipse vai do topo (1,000 H) ao queixo (0,870 H)
    o.append(f'<ellipse cx="{x0:.2f}" cy="{sw / 2 + ry:.2f}" rx="{ry * 0.74:.2f}" ry="{ry:.2f}" fill="none" '
             f'stroke="{ink}" stroke-width="{sw:.2f}"/>')
    segs = [("queixo", "pescoco"), ("ombro_d", "ombro_e"), ("ombro_d", "quadril_d"), ("ombro_e", "quadril_e"),
            ("quadril_d", "quadril_e")]
    for l in ("d", "e"):
        segs += [(f"ombro_{l}", f"cotovelo_{l}"), (f"cotovelo_{l}", f"punho_{l}"), (f"punho_{l}", f"dedos_{l}"),
                 (f"quadril_{l}", f"joelho_{l}"), (f"joelho_{l}", f"tornozelo_{l}")]
    d = "".join(f"M{P[a][0]:.2f} {P[a][1]:.2f}L{P[b][0]:.2f} {P[b][1]:.2f}" for a, b in segs)
    for l in ("d", "e"):
        ax, ay = P[f"tornozelo_{l}"]
        d += f"M{ax:.2f} {ay:.2f}L{ax:.2f} {H:.2f}M{ax - 0.024 * H:.2f} {H:.2f}H{ax + 0.024 * H:.2f}"
    o.append(_p(d, stroke=ink, sw=sw, extra='stroke-linecap="round" stroke-linejoin="round"'))
    rj = H * 0.011
    for k in ("ombro_d", "ombro_e", "cotovelo_d", "cotovelo_e", "punho_d", "punho_e", "quadril_d", "quadril_e",
              "joelho_d", "joelho_e", "tornozelo_d", "tornozelo_e"):
        o.append(f'<circle cx="{P[k][0]:.2f}" cy="{P[k][1]:.2f}" r="{rj:.2f}" fill="{f.fundo}" stroke="{ink}" '
                 f'stroke-width="{sw * 0.8:.2f}"/>')
    return "".join(o), P


def proporcoes(f, H=330.0, escala=True):
    """Figura esquemática com as alturas segmentares de Drillis & Contini (fração da estatura H) numa régua lateral."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    fig, P = _figura(f, H, 0, sw=t * 0.8)
    o = [fig]
    if escala:
        xs = H * 0.27
        o.append(_p(f"M{xs:.2f} 0V{H:.2f}", stroke=apo, sw=t * 0.5))
        ns = H * 0.036
        marcas = [("topo", None), ("queixo", "queixo"), ("ombro", "ombro_e"), ("cotovelo", "cotovelo_e"),
                  ("trocanter", "quadril_e"), ("punho", "punho_e"), ("dedos", "dedos_e"), ("joelho", "joelho_e"),
                  ("tornozelo", "tornozelo_e")]
        for k, ponto in marcas:
            yy = (1 - ALT[k]) * H
            o.append(_p(f"M{xs:.2f} {yy:.2f}H{xs + H * 0.03:.2f}", stroke=ink, sw=t * 0.6))
            if ponto:
                px = P[ponto][0] + H * 0.02
                o.append(_p(f"M{px:.2f} {yy:.2f}H{xs - H * 0.01:.2f}", stroke=apo, sw=t * 0.35,
                            extra='stroke-dasharray="1.5 3"'))
            o.append(rot_tinta(f, num(ALT[k], 3) + " H", ns, xs + H * 0.045,
                         yy + cap(f.fonte_mono) * ns / 2, ac if k in ("ombro", "trocanter", "joelho") else ink))
        o.append(_p(f"M{xs:.2f} {H:.2f}H{xs + H * 0.03:.2f}", stroke=ink, sw=t * 0.6))
        o.append(rot_tinta(f, "0", ns, xs + H * 0.045, H + cap(f.fonte_mono) * ns / 2, ink))
    return justo("".join(o), "proporções segmentares" + (" · com régua" if escala else ""),
                 "Drillis & Contini (1966): alturas em fração da estatura H — figura de ESQUEMA, não corpo real · "
                 "biomecânica, avaliação")


def dobras7(f, H=300.0):
    """Jackson & Pollock (1978), 7 dobras, marcadas com × no lado DIREITO do sujeito (frente: peitoral, axilar média,
    abdominal, suprailíaca, coxa; costas: tríceps, subescapular). O número fica COLADO ao seu × (sem chamadas
    cruzando membros). Locais (J&P 1978 + ACSM): peitoral = dobra diagonal a meio caminho entre a linha axilar
    anterior e o mamilo; axilar média = linha axilar média, no nível do apêndice xifoide; abdominal = vertical,
    3 cm ao lado do umbigo; suprailíaca = diagonal logo acima da crista ilíaca; coxa = vertical, no meio da
    coxa; tríceps = vertical, no ponto médio acrômio–olécrano (atrás); subescapular = diagonal, abaixo do ângulo
    inferior da escápula."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    gap = H * 0.62
    f1, P1 = _figura(f, H, 0, sw=t * 0.75)
    f2, P2 = _figura(f, H, gap, costas=True, sw=t * 0.75)
    y = lambda fr: (1 - fr) * H  # noqa: E731
    od, qd = P1["ombro_d"], P1["quadril_d"]

    def borda(fr):   # x da borda do tronco (lado direito do sujeito, de frente) na altura fr
        k = (y(fr) - od[1]) / (qd[1] - od[1])
        return od[0] + (qd[0] - od[0]) * k

    def meio(a, b):
        return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    # (número, ponto, lado do número: +1 = à direita do ×, -1 = à esquerda)
    pts = [("1", (-H * 0.080, y(0.735)), 1),
           ("2", (borda(0.69) * 0.72, y(0.69)), 1),
           ("3", (-H * 0.017, y(0.615)), 1),
           ("4", (-H * 0.062, y(0.565)), 1),
           ("5", meio(P1["quadril_d"], P1["joelho_d"]), 1),
           ("6", meio(P2["ombro_d"], P2["cotovelo_d"]), 1),
           ("7", (gap + H * 0.055, y(0.705)), -1)]
    o = [f1, f2]
    xs = H * 0.014
    ns = H * 0.042
    for n, (px, py), lado in pts:
        o.append(_p(f"M{px - xs:.2f} {py - xs:.2f}L{px + xs:.2f} {py + xs:.2f}M{px - xs:.2f} {py + xs:.2f}L{px + xs:.2f} {py - xs:.2f}",
                    stroke=ac, sw=t * 0.9, extra='stroke-linecap="round"'))
        o.append(rot_tinta(f, n, ns, px + lado * (xs + H * 0.016), py + cap(f.fonte_mono) * ns / 2, ink,
                     anchor="start" if lado > 0 else "end"))
    o.append(rot_tinta(f, "FRENTE", H * 0.04, 0, H + H * 0.1, apo, f.fonte_texto, 0.1, "middle"))
    o.append(rot_tinta(f, "COSTAS", H * 0.04, gap, H + H * 0.1, apo, f.fonte_texto, 0.1, "middle"))
    return justo("".join(o), "7 dobras (Jackson & Pollock) · frente e costas",
                 "7 pontos do protocolo J&P no lado direito do sujeito; figura esquemática, sem corpo real · lista "
                 "de 7 itens, avaliação")


def dobras_lista(f, colunas=1):
    """As 7 dobras como LISTA numerada com × (ícone de lista de 7 itens). A tinta do × começa em x = 0, igual ao
    título e aos fios (nada a 2 px de alinhar)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    nomes = ["PEITORAL", "AXILAR MÉDIA", "TRÍCEPS", "SUBESCAPULAR", "ABDOMINAL", "SUPRAILÍACA", "COXA"]
    o = []
    lh = u * 1.35
    ns = u * 0.62
    por = 7 if colunas == 1 else 4
    sw = t * 0.9
    for i, n in enumerate(nomes):
        c, r = divmod(i, por)
        x, yb = c * u * 10.5, r * lh
        k = u * 0.26
        cx, cy = x + k + sw / 2, yb + lh / 2
        o.append(_p(f"M{cx - k:.2f} {cy - k:.2f}L{cx + k:.2f} {cy + k:.2f}M{cx - k:.2f} {cy + k:.2f}L{cx + k:.2f} {cy - k:.2f}",
                    stroke=ac, sw=sw, extra='stroke-linecap="round"'))
        o.append(rot_tinta(f, f"{i + 1:02d}", ns, x + u * 1.25, cy + cap(f.fonte_mono) * ns / 2, apo))
        o.append(rot_tinta(f, n, ns, x + u * 2.6, cy + cap(f.fonte_texto) * ns / 2, ink, f.fonte_texto, 0.06))
        if r < (por - 1) and i < 6:
            o.append(_p(f"M{x:.2f} {yb + lh:.2f}H{x + u * 9.2:.2f}", stroke=apo, sw=t * 0.35, extra='stroke-opacity="0.6"'))
    o.append(rot_tinta(f, "JACKSON & POLLOCK · 7 DOBRAS", u * 0.48, 0, -u * 0.5, apo, tr=0.06))
    return justo("".join(o), f"7 dobras · lista ({colunas} col.)", "ordem do protocolo J&P com × de marcação na pele · "
                 "lista de 7 itens, checklist de avaliação")


@amostra(FAM, "corpo esquemático")
def _a_corpo(f):
    return [proporcoes(f), proporcoes(f, escala=False), dobras7(f), dobras_lista(f), dobras_lista(f, 2)]


# ================================================================ prumo lateral (Kendall) (14b 5.2)
PRUMO = [("meato", 0.935, "MEATO ACÚSTICO", 0.0), ("acromio", ALT["ombro"], "ACRÔMIO", 0.0),
         ("trocanter", ALT["trocanter"], "TROCÂNTER MAIOR", 0.0), ("joelho", ALT["joelho"], "À FRENTE DO JOELHO", -1.35),
         ("maleolo", 0.06, "À FRENTE DO MALÉOLO", -1.35)]


def prumo(f, H=318.0, rotulos=True, cor_fio=None):
    """Linha de prumo lateral com os 5 pontos (Kendall): meato, acrômio, trocânter maior, à frente do joelho e à
    frente do maléolo lateral (joelho e maléolo ficam ATRÁS do fio — o detalhe que quem é da área confere).
    Alturas pelas proporções de Drillis & Contini. Sem grade (a grade é assinatura do FennerLab).
    Revisão 10/2026: peso menor e mais fino, afastado do ponto do maléolo; a versão 'deitada' foi REMOVIDA (fio de
    prumo é sempre vertical — pendurado na gravidade, deitado é fisicamente impossível)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    fio = cor_fio or ac
    o = []
    yb = H
    a = H * 0.013
    topo = -H * 0.06
    y1 = yb - a * 3.0                 # o peso encosta quase no chão
    o.append(_p(f"M0 {topo:.2f}V{y1:.2f}", stroke=fio, sw=t * 0.7))
    o.append(f'<circle cx="0" cy="{topo:.2f}" r="{t * 1.3:.2f}" fill="none" stroke="{fio}" stroke-width="{t * 0.7:.2f}"/>')
    bob = (f"M{-a * 0.45:.2f} {y1:.2f}H{a * 0.45:.2f}V{y1 + a * 0.5:.2f}L{a:.2f} {y1 + a * 0.9:.2f}"
           f"L0 {y1 + a * 3.0:.2f}L{-a:.2f} {y1 + a * 0.9:.2f}L{-a * 0.45:.2f} {y1 + a * 0.5:.2f}Z")
    o.append(f'<path d="{bob}" fill="{fio}"/>')
    o.append(_p(f"M{-H * 0.12:.2f} {yb + a * 0.6:.2f}H{H * 0.12:.2f}", stroke=apo, sw=t * 0.6))
    ns = H * 0.042
    for k, fr, nome, desloc in PRUMO:
        yy = (1 - fr) * H
        x = desloc * H * 0.036
        o.append(f'<circle cx="{x:.2f}" cy="{yy:.2f}" r="{H * 0.016:.2f}" fill="{f.fundo}" stroke="{ink}" '
                 f'stroke-width="{t * 0.8:.2f}"/><circle cx="{x:.2f}" cy="{yy:.2f}" r="{H * 0.006:.2f}" fill="{ink}"/>')
        if rotulos:
            o.append(_p(f"M{H * 0.03:.2f} {yy:.2f}H{H * 0.07:.2f}", stroke=apo, sw=t * 0.4))
            o.append(rot_tinta(f, nome, ns, H * 0.085, yy + cap(f.fonte_texto) * ns / 2, ink, f.fonte_texto, 0.06))
    return justo("".join(o), "prumo lateral (Kendall)" + (" · rótulos" if rotulos else " · mínimo"),
                 "fio de prumo + 5 pontos na altura real; joelho e maléolo atrás do fio · régua vertical onde o "
                 "título encosta, divisor")


@amostra(FAM, "prumo lateral")
def _a_prumo(f):
    return [prumo(f), prumo(f, rotulos=False)]


# ================================================================ carga: barra, anilhas, halter, kettlebell (14b 5.15–5.16)
# Código de cores da IWF (exceção consciente às cores da ficha: aqui a cor É o dado — 25 vermelha, 20 azul…)
IWF = {25: "#C8102E", 20: "#0057B8", 15: "#F6C324", 10: "#00843D", 5: "#F2F2F2", 2.5: "#C8102E", 2: "#0057B8",
       1.5: "#F6C324", 1: "#00843D", 0.5: "#F2F2F2"}
# diâmetro × espessura (mm): ≥ 10 kg = 450 mm (regra IWF); espessuras e anilhas de troco ≈ catálogo de competição
DISCO = {25: (450, 54), 20: (450, 44), 15: (450, 35), 10: (450, 27), 5: (230, 22), 2.5: (210, 19), 2: (190, 19),
         1.5: (175, 17), 1: (160, 15), 0.5: (135, 12)}
BARRA = {"masculina": dict(total=2200, luva=415, kg=20, pega=28, centro=True),
         "feminina": dict(total=2010, luva=320, kg=15, pega=25, centro=False)}


def anilhas_por_lado(total, barra_kg=20, presilhas=True):
    """Carga total → anilhas de um lado (maior por dentro), com presilhas de 2,5 kg cada (competição)."""
    resto = (total - barra_kg - (5 if presilhas else 0)) / 2
    if resto < -1e-9:
        raise ValueError(f"carga {total} kg menor que barra + presilhas")
    out = []
    for kg in (25, 20, 15, 10, 5, 2.5, 2, 1.5, 1, 0.5):
        while resto >= kg - 1e-9:
            out.append(kg)
            resto -= kg
    if resto > 1e-6:
        raise ValueError(f"carga {total} kg não fecha com anilhas IWF")
    return out


def _kg_marca(f):
    """Peso IWF cuja cor casa com o acento da marca (dourado ≈ amarelo = 15; azul = 20; vermelho = 25); 20 se o
    acento não é uma cor IWF (roxo). Só ESSA anilha usa o acento no modo ficha — as outras ficam neutras, para a cor
    não contradizer o código de peso (D-cor-código)."""
    return _kg_da_cor(f.acento, IWF) or 20


def _cor_anilha(f, kg, modo):
    if modo == "iwf":
        return IWF[kg], ("#111111" if kg in (5, 0.5, 15, 1.5) else None)
    if modo == "ficha":
        if kg == _kg_marca(f):
            return f.acento, None
        return mistura(f.fundo, f.tinta, 0.14), f.tinta
    if modo == "treino":
        return mistura(f.fundo, f.tinta, 0.14), f.tinta
    return f.fundo, f.tinta


def barra(f, carga=None, modo="treino", tipo="masculina", w=470.0, rotulo=True, presilhas=True, cota=False):
    """Barra olímpica de lado, em escala: 2,2 m / 20 kg (fem. 2,01 m / 15 kg), luvas de 50 mm, pegada 28 (25) mm,
    marcas de pegada a 910 mm, recartilhado central só na masculina. carga = total em kg (parâmetro) → anilhas
    calculadas (maior por dentro). modo: treino (bumper preta) | ficha | contorno | iwf (cores oficiais)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    B = BARRA[tipo]
    k = w / B["total"]
    meia = B["total"] / 2
    haste = 655                                # metade da haste entre os colares internos (1310 mm)
    o = []
    pid = uid("recart", tipo, w)
    defs = (f'<pattern id="{pid}" width="{2.2:.2f}" height="{2.2:.2f}" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(45)"><rect width="1" height="2.2" fill="{f.fundo}" fill-opacity="0.55"/></pattern>')
    X = lambda mm: mm * k  # noqa: E731
    pega, luva = X(B["pega"]), X(50)
    # haste + recartilhado
    o.append(f'<path d="{ret(X(-haste), -pega / 2, X(2 * haste), pega, 0)}" fill="{ink}"/>')
    zonas = [(200, 452), (458, 640)]
    for a, b in zonas:
        for s in (-1, 1):
            x0 = X(min(s * a, s * b))
            o.append(f'<path d="{ret(x0, -pega / 2, X(b - a), pega, 0)}" fill="url(#{pid})"/>')
    if B["centro"]:
        o.append(f'<path d="{ret(X(-60), -pega / 2, X(120), pega, 0)}" fill="url(#{pid})"/>')
    # colares internos + luvas
    for s in (-1, 1):
        o.append(f'<path d="{ret(X(min(s * haste, s * (haste + 30))), -X(38), X(30), X(76), 1)}" fill="{ink}"/>')
        x0 = X(min(s * (haste + 30), s * meia))
        o.append(f'<path d="{ret(x0, -luva / 2, X(B["luva"]), luva, 1)}" fill="{mistura(ink, f.fundo, 0.18)}"/>')
    # anilhas
    if carga:
        lado = anilhas_por_lado(carga, B["kg"], presilhas)
        if sum(DISCO[a][1] for a in lado) + (60 if presilhas else 0) > B["luva"] - 5:
            raise ValueError(f"{carga} kg não cabe na luva")
        for s in (-1, 1):
            pos = haste + 30
            for kgd in lado:
                dia, esp = DISCO[kgd]
                fill, stroke = _cor_anilha(f, kgd, modo)
                x0 = X(pos) if s > 0 else X(-pos - esp)
                st = f' stroke="{stroke}" stroke-width="{t * 0.5:.2f}"' if stroke else ""
                o.append(f'<path d="{ret(x0, -X(dia) / 2, X(esp), X(dia), min(X(esp) * 0.3, 2.5))}" fill="{fill}"{st}/>')
                pos += esp
            if presilhas:
                x0 = X(pos) if s > 0 else X(-pos - 60)
                o.append(f'<path d="{ret(x0, -X(45), X(60), X(90), 1.5)}" fill="{apo}"/>')
                o.append(f'<path d="{ret(x0 + X(18), -X(45) - X(28), X(10), X(30), 1)}" fill="{apo}"/>')
    # marcas de pegada (910 mm): anéis no acento que abraçam a haste (≈ 13 px de altura; antes 4 px sumiam)
    if cota or not carga:
        for s in (-1, 1):
            o.append(f'<path d="{ret(X(s * 455) - t / 2, -pega / 2 - t * 1.2, t, pega + t * 2.4, 0)}" fill="{ac}"/>')
    if cota:
        yc = pega / 2 + X(60)
        o.append(_p(f"M{X(-455):.2f} {yc:.2f}H{X(455):.2f}"
                    f"M{X(-455):.2f} {pega / 2 + t * 1.2 + 1:.2f}V{yc + 5:.2f}"
                    f"M{X(455):.2f} {pega / 2 + t * 1.2 + 1:.2f}V{yc + 5:.2f}", stroke=apo, sw=t * 0.5))
        o.append(rot_tinta(f, "910 mm", f.unidade * 0.5, 0, yc + f.unidade * 0.9, ink, tr=0.06, anchor="middle"))
    if carga and rotulo:
        sz = X(450) * 0.42
        o.append(rot_tinta(f, f"{num(carga)} kg", sz, 0, -X(225) + sz * 0.15, ink, f.fonte_display, 0.02, "middle"))
    nome = f"barra {tipo}" + (f" · {num(carga)} kg · {modo}" if carga else " · vazia") + (" · cota 910" if cota else "")
    return justo("".join(o), nome, "barra e anilhas em escala real; carga calculada em anilhas IWF (maior por dentro) · "
                 "divisor, sublinhado entre as marcas de pegada, numeral de carga", defs=defs)


@amostra(FAM, "barra olímpica")
def _a_barra(f):
    return [barra(f, 140), barra(f, 100, "iwf"),
            barra(f, 15 + 5 + 2 * _kg_marca(f), "ficha", tipo="feminina", rotulo=False),
            barra(f, 183, "contorno", rotulo=False), barra(f), barra(f, cota=True, tipo="feminina")]


def anilha(f, kg=20, modo="contorno", R=150.0, marca="NOME DA MARCA", numeral=True):
    """Anilha de frente: aro, faixa de texto, inserto de aço com parafusos e furo de 50 mm — tudo na proporção do
    disco de 450 mm (anilhas < 10 kg ficam menores, como na vida real). modo: contorno | cheio | iwf | treino."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    if modo == "cheio":     # a peça na cor da marca só pode dizer o peso que essa cor significa no código IWF
        kg = _kg_da_cor(f.acento, IWF) or kg
    dia = DISCO[kg][0]
    R = R * dia / 450
    if modo == "iwf":
        fill, txt = IWF[kg], ("#111111" if kg in (5, 0.5, 15, 1.5) else "#F2F2F2")
    elif modo == "cheio":
        fill, txt = ac, f.sobre_acento
    elif modo == "treino":
        fill, txt = mistura(f.fundo, ink, 0.14), ink
    else:
        fill, txt = "none", ink
    rh, rf = R * 0.30 * 450 / dia if dia < 450 else R * 0.30, R * 0.112 * 450 / dia
    rh = min(rh, R * 0.55)
    # o furo (50 mm) é FURO de verdade (evenodd): em qualquer fundo se vê o fundo por dentro, nunca uma tinta
    o = [f'<path d="{circ(0, 0, R)}{circ(0, 0, rf)}" fill-rule="evenodd" fill="{fill if fill != "none" else f.fundo}" '
         + (f'stroke="{ink}" stroke-width="{t:.2f}"' if modo == "contorno" else "") + "/>"]
    linha = txt
    o.append(f'<circle r="{R * 0.93:.2f}" fill="none" stroke="{linha}" stroke-width="{t * 0.45:.2f}" stroke-opacity="0.6"/>')
    o.append(f'<path d="{circ(0, 0, rh)}{circ(0, 0, rf)}" fill-rule="evenodd" '
             f'fill="{mistura(f.tinta, f.fundo, 0.35) if modo != "contorno" else f.fundo}" '
             f'stroke="{linha}" stroke-width="{t * 0.6:.2f}"/>')
    o.append(f'<circle r="{rh * 0.8:.2f}" fill="none" stroke="{f.fundo if modo != "contorno" else linha}" '
             f'stroke-width="{t * 0.4:.2f}" stroke-opacity="0.7"/>')
    for i in range(6):
        x, y = polar(0, 0, rh * 0.9, -90 + i * 60)
        o.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rh * 0.045:.2f}" fill="{f.fundo if modo != "contorno" else linha}"/>')
    kgs = num(kg)
    if dia >= 450:
        ts = R * 0.085
        if marca:
            from .nucleo import texto_circulo
            o.append(texto_circulo(f.fonte_texto, marca, ts, 0, 0, R * 0.80, txt, -90, 0.14, True))
        from .nucleo import texto_circulo as tc
        o.append(tc(f.fonte_mono, f"{kgs} kg", ts, 0, 0, R * 0.80 + cap(f.fonte_mono) * ts, txt, 90, 0.2, False))
        if numeral:
            sz = R * 0.34
            for s in (-1, 1):
                o.append(rot_c(f, kgs, sz, s * (rh + (R * 0.72 - rh) / 2 + R * 0.02), 0, txt, f.fonte_display))
    else:
        ts = R * 0.30                       # numeral legível mesmo na anilha pequena (antes 0,16 R sumia a 25%)
        o.append(rot_c(f, kgs, ts, 0, -(rh + (R * 0.93 - rh) / 2), txt, f.fonte_display))
        o.append(rot_c(f, "kg", R * 0.16, 0, rh + (R * 0.93 - rh) / 2, txt, f.fonte_texto, 0.06))
    return justo("".join(o), f"anilha {kgs} kg · {modo}", "disco de 450 mm com furo de 50 mm, inserto e aro; < 10 kg "
                 "menor · numeral de carga, selo, carregamento (gira)")


@amostra(FAM, "anilha")
def _a_anilha(f):
    return [anilha(f, 20), anilha(f, _kg_marca(f), "cheio"), anilha(f, 20, "iwf"), anilha(f, 15, "treino", numeral=False),
            anilha(f, 5, "contorno"), anilha(f, 10, "iwf", marca=None)]


def halter(f, kg=None, tipo="sextavado", modo="contorno", w=420.0):
    """Halter de lado. sextavado: cabeças de borracha com 2 arestas visíveis (faces do hexágono), pegada recartilhada
    de 33 mm; anilhado: barra curta de 35 cm, anilhas pequenas e presilha de rosca."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    o = []
    pid = uid("hrec", w, tipo)
    defs = (f'<pattern id="{pid}" width="2.4" height="2.4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="1.1" height="2.4" fill="{f.fundo}" fill-opacity="0.55"/></pattern>')
    cheio = modo == "cheio"
    fc = ac if cheio else f.fundo
    if tipo == "sextavado":
        L = 390.0
        k = w / L
        hl, hh, pl, pd = 112 * k, 150 * k, (L - 224) * k, 33 * k
        o.append(f'<path d="{ret(-pl / 2 - 4 * k, -pd / 2, pl + 8 * k, pd, 0)}" fill="{ink}"/>')
        o.append(f'<path d="{ret(-pl / 2 + 14 * k, -pd / 2, pl - 28 * k, pd, 0)}" fill="url(#{pid})"/>')
        for s in (-1, 1):
            x0 = s * pl / 2 if s > 0 else -pl / 2 - hl
            o.append(f'<path d="{ret(x0, -hh / 2, hl, hh, 6 * k)}" fill="{fc}" stroke="{ink}" stroke-width="{t:.2f}"/>')
            for yy in (-hh / 4, hh / 4):
                o.append(_p(f"M{x0 + t / 2:.2f} {yy:.2f}H{x0 + hl - t / 2:.2f}", stroke=f.sobre_acento if cheio else ink,
                            sw=t * 0.5, extra='stroke-opacity="0.6"'))
            if kg:
                o.append(rot_c(f, num(kg), hh * 0.2, x0 + hl / 2, 0, f.sobre_acento if cheio else ink, f.fonte_display))
    else:
        L = 400.0
        k = w / L
        pl, pd, ld = 140 * k, 30 * k, 28 * k
        o.append(f'<path d="{ret(-L / 2 * k, -ld / 2, L * k, ld, 1)}" fill="{mistura(ink, f.fundo, 0.18)}"/>')
        o.append(f'<path d="{ret(-pl / 2, -pd / 2, pl, pd, 0)}" fill="{ink}"/>')
        o.append(f'<path d="{ret(-pl / 2 + 10 * k, -pd / 2, pl - 20 * k, pd, 0)}" fill="url(#{pid})"/>')
        discos = [(200, 26), (200, 26), (160, 20), (130, 16)]
        for s in (-1, 1):
            pos = pl / 2 + 6 * k
            for dia, esp in discos:
                x0 = pos if s > 0 else -pos - esp * k
                o.append(f'<path d="{ret(x0, -dia * k / 2, esp * k, dia * k, 1.5)}" fill="{fc}" stroke="{ink}" '
                         f'stroke-width="{t * 0.7:.2f}"/>')
                pos += esp * k + 1.5 * k
            x0 = pos if s > 0 else -pos - 34 * k
            o.append(f'<path d="{ret(x0, -24 * k, 34 * k, 48 * k, 3 * k)}" fill="{apo}"/>')
            for j in range(4):
                xx = x0 + (6 + j * 7.5) * k
                o.append(_p(f"M{xx:.2f} {-24 * k:.2f}V{24 * k:.2f}", stroke=f.fundo, sw=t * 0.35, extra='stroke-opacity="0.6"'))
    return justo("".join(o), f"halter {tipo} · {modo}" + (f" · {num(kg)} kg" if kg else ""),
                 "proporção real de halter (pegada 33 mm, cabeças sextavadas) · ícone de força, divisor curto",
                 defs=defs)


KB_COR = {8: "#E86FA6", 12: "#2D6CC0", 16: "#F2C230", 20: "#7B4FA8", 24: "#3C9A4A", 28: "#EE7A26", 32: "#D2312C"}


def kettlebell(f, kg=16, modo="contorno", H=300.0, cores_competicao=False):
    """Kettlebell de COMPETIÇÃO: mesmo tamanho para todos os pesos (altura 280 mm, corpo 210 mm, alça 35 mm); a cor
    diz o peso (8 rosa, 12 azul, 16 amarelo, 20 roxo, 24 verde, 28 laranja, 32 vermelho).
    Revisão 10/2026: base da alça DENTRO do corpo (nenhuma ponta vaza); no modo cheio o número vem da cor da marca
    (dourado ≈ amarelo = 16), para a cor não contradizer o código."""
    t, ink, ac = f.traco, f.tinta, f.acento
    if modo == "cheio" and not cores_competicao:
        kg = _kg_da_cor(ac, KB_COR) or kg
    k = H / 280.0
    rc = 105 * k
    yc = H - rc * 0.94
    base = H
    hw = rc * 1.04                  # metade da largura externa da alça
    ht = 0.0
    aw = 35 * k
    corpo = (f"M{-rc * 0.34:.2f} {base:.2f}"
             f"A{rc:.2f} {rc:.2f} 0 1 1 {rc * 0.34:.2f} {base:.2f}Z")
    # alça (chifres) — contorno externo e janela interna; a base fica a 0,55 rc acima do centro do corpo, onde o
    # corpo já é mais largo (0,835 rc) que a alça (0,80 rc): as quinas ficam por dentro do círculo
    yo = yc - rc * 0.55
    alca_ext = (f"M{-rc * 0.80:.2f} {yo:.2f}C{-hw:.2f} {yo - rc * 0.55:.2f} {-hw:.2f} {ht + aw * 0.2:.2f} {-hw * 0.55:.2f} {ht:.2f}"
                f"H{hw * 0.55:.2f}C{hw:.2f} {ht + aw * 0.2:.2f} {hw:.2f} {yo - rc * 0.55:.2f} {rc * 0.80:.2f} {yo:.2f}Z")
    hi = hw - aw
    yi = yo + aw * 0.05
    janela = (f"M{-rc * 0.80 + aw:.2f} {yi:.2f}C{-hi:.2f} {yi - rc * 0.45:.2f} {-hi:.2f} {ht + aw * 1.15:.2f} {-hi * 0.52:.2f} {ht + aw:.2f}"
              f"H{hi * 0.52:.2f}C{hi:.2f} {ht + aw * 1.15:.2f} {hi:.2f} {yi - rc * 0.45:.2f} {rc * 0.80 - aw:.2f} {yi:.2f}Z")
    if cores_competicao:
        fill = KB_COR.get(kg, ac)
        txt = _txt_sobre(fill, "#F5F5F5", "#111111")
    elif modo == "cheio":
        fill, txt = ac, f.sobre_acento
    else:
        fill, txt = f.fundo, ink
    st = f'stroke="{ink}" stroke-width="{t:.2f}" stroke-linejoin="round"' if modo == "contorno" and not cores_competicao else ""
    o = [f'<path d="{alca_ext} {janela}" fill="{fill}" fill-rule="evenodd" {st}/>',
         f'<path d="{corpo}" fill="{fill}" {st}/>']
    sz = rc * 0.62
    o.append(rot_c(f, str(kg), sz, 0, yc + rc * 0.02, txt, f.fonte_display))
    o.append(rot_c(f, "kg", sz * 0.28, 0, yc + sz * 0.62, txt, f.fonte_texto, 0.1))
    return justo("".join(o), f"kettlebell {kg} kg · " + ("cores de competição" if cores_competicao else modo),
                 "kettlebell de competição (tamanho único 280 × 210 mm; cor = peso) · ícone, numeral de carga")


@amostra(FAM, "halter e kettlebell")
def _a_halter(f):
    return [halter(f), halter(f, 20, modo="cheio"), halter(f, tipo="anilhado"), kettlebell(f),
            kettlebell(f, 16, "cheio"), kettlebell(f, 24, cores_competicao=True)]


# ================================================================ periodização (14b 5.18)
FASES = [("PREPARAÇÃO GERAL", 10), ("ESPECÍFICA", 6), ("COMPETITIVA", 5), ("TRANSIÇÃO", 3)]
MESOS = [5, 5, 6, 3, 2, 3]


def periodizacao(f, fases=None, mesos=None, semana=None, modo="completa", w=470.0):
    """Régua de periodização: micro = semana (tracinho curto), meso = bloco de 2–6 micro (médio), macro = temporada
    (longo), como mm/cm/dm. Padrão = esquema de 24 semanas (preparação 2/3, transição 3 sem.). semana = parâmetro:
    a CÉLULA da semana fica no acento, dentro da régua (nada cruza a faixa de fases).
    Revisão 10/2026: nome de fase que não cabe na faixa vai INTEIRO abaixo da faixa (nunca 'TRAN.'/'DELO.')."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    fases, mesos = fases or FASES, mesos or MESOS
    n = sum(m for m in mesos)
    assert n == sum(s for _, s in fases), "mesos e fases precisam somar as mesmas semanas"
    k = w / n
    o = []
    y0 = u * 1.1
    o.append(_p(f"M0 {y0:.2f}H{w:.2f}", stroke=ink, sw=t * 0.7))
    limites = [0]
    for m in mesos:
        limites.append(limites[-1] + m)
    for s in range(n + 1):
        if s in (0, n):
            h = u * 1.1
        elif s in limites:
            h = u * 0.7
        else:
            h = u * 0.32
        swt = t * (0.8 if s in limites else 0.5)
        xt = min(max(s * k, swt / 2), w - swt / 2)       # tiques das pontas por dentro: a tinta fica em [0, w]
        o.append(_p(f"M{xt:.2f} {y0:.2f}V{y0 - h:.2f}", stroke=ink, sw=swt))
    if semana:      # célula da semana no acento, entre os tracinhos de micro
        ins = min(2.5, k * 0.18)
        o.append(f'<path d="{ret((semana - 1) * k + ins, y0 - u * 0.62, k - 2 * ins, u * 0.62 - t * 0.35, 0)}" fill="{ac}"/>')
    if modo == "completa":
        for i, (a, b) in enumerate(zip(limites, limites[1:])):
            o.append(rot_tinta(f, f"M{i + 1}", u * 0.5, (a + b) / 2 * k, y0 - u * 0.95, apo, tr=0.04, anchor="middle"))
        yb = y0 + u * 0.45
        hb = u * 1.15
        x = 0
        abaixo = False
        for i, (nome, sem) in enumerate(fases):
            cor = _rampa(f, i, len(fases), 0.22)
            o.append(f'<path d="{ret(x * k + (1 if i else 0), yb, sem * k - (1 if i else 0), hb, 0)}" fill="{cor}"/>')
            ns = u * 0.46
            lw = largura(f.fonte_texto, nome, ns, 0.06)
            if lw < sem * k - u * 0.5:      # cabe: dentro da faixa, cor pelo maior contraste
                o.append(rot_tinta(f, nome, ns, x * k + u * 0.3, yb + hb / 2 + cap(f.fonte_texto) * ns / 2,
                             _txt_sobre(cor, ink, f.fundo), f.fonte_texto, 0.06))
            else:                           # não cabe: nome inteiro logo abaixo da faixa, preso à célula
                abaixo = True
                xe = (x + sem) * k
                ancora_fim = x * k + u * 0.3 + lw > w
                xt = xe if ancora_fim else x * k
                o.append(rot_tinta(f, nome, ns, xt, yb + hb + u * 0.3 + cap(f.fonte_texto) * ns, ink, f.fonte_texto, 0.06,
                             "end" if ancora_fim else "start"))
            x += sem
        yleg = yb + hb + (u * 1.55 if abaixo else u * 0.75)
        leg = f"MACROCICLO · {n} SEMANAS" + (f" · SEMANA {semana}" if semana else "") + " · ESQUEMA"
        o.append(rot_tinta(f, leg, u * 0.48, 0, yleg, apo, tr=0.05))
    else:
        yl = y0 + u * 1.0
        x = 0.0
        yd = yl + u * 1.15                           # linha de base da descrição (e pé dos tracinhos)
        yn = yd - u * 0.46 * 0.7 - u * 0.35          # nome: entrelinha de 0,35 u acima da descrição
        for nome, h, desc in (("MICRO", 0.32, "1 SEMANA"), ("MESO", 0.7, "2–6 MICRO"), ("MACRO", 1.1, "TEMPORADA")):
            o.append(_p(f"M{max(x, t * 0.35):.2f} {yd:.2f}V{yd - u * h:.2f}", stroke=ink, sw=t * 0.7))
            o.append(rot_tinta(f, nome, u * 0.48, x + u * 0.35, yn, ac if nome == "MACRO" else ink, f.fonte_texto, 0.06))
            o.append(rot_tinta(f, desc, u * 0.46, x + u * 0.35, yd, apo, tr=0.04))
            x += u * 5.2
    return justo("".join(o), f"régua de periodização · {modo} · {n} semanas" + (f" · semana {semana}" if semana else ""),
                 "micro/meso/macro como mm/cm/dm (Matveyev); fases em faixas · cronograma de curso, rodapé, calendário")


@amostra(FAM, "periodização")
def _a_period(f):
    return [periodizacao(f), periodizacao(f, semana=7), periodizacao(f, modo="regua"),
            periodizacao(f, fases=[("BASE", 4), ("FORÇA", 4), ("POTÊNCIA", 3), ("DELOAD", 1)], mesos=[4, 4, 3, 1])]


# ================================================================ fita métrica / Wells
def _regua_cm(f, ini, fim, k, h, cor_fundo, cor_tick, numeros=True, mm=True):
    o = [f'<path d="{ret(0, 0, (fim - ini) * k, h, 0)}" fill="{cor_fundo}"/>'] if cor_fundo else []
    d1 = d2 = d3 = ""
    t = 1.0
    for i in range(int(round((fim - ini) * 10)) + 1):
        x = i * k / 10
        cm = ini + i / 10
        if i % 10 == 0:
            d3 += f"M{x:.2f} 0V{h * 0.46:.2f}"
        elif i % 5 == 0:
            d2 += f"M{x:.2f} 0V{h * 0.3:.2f}"
        elif mm:
            d1 += f"M{x:.2f} 0V{h * 0.18:.2f}"
    return o, d1, d2, d3


def fita_metrica(f, ini=0, fim=15, modo="reta", w=460.0, cor=None):
    """Fita métrica (cm/mm): tique de mm, meio cm e cm numerado. reta = trena com gancho no zero; curva = fita
    antropométrica contornando um arco (tiques seguem a normal)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    fundo = cor or ac
    tk = f.sobre_acento if fundo == ac else (f.fundo if luminancia(fundo) > 0.35 else ink)
    o = []
    if modo == "reta":
        k = w / (fim - ini)
        h = u * 1.7
        base, d1, d2, d3 = _regua_cm(f, ini, fim, k, h, fundo, tk)
        o += base
        o.append(_p(d1, stroke=tk, sw=t * 0.32) + _p(d2, stroke=tk, sw=t * 0.45) + _p(d3, stroke=tk, sw=t * 0.6))
        for c in range(int(ini) + 1, int(fim)):
            o.append(rot_tinta(f, str(c), u * 0.55, (c - ini) * k, h * 0.82, tk, anchor="middle"))
        if ini == 0:   # gancho da trena
            o.append(f'<path d="{ret(-u * 0.35, -u * 0.25, u * 0.35, h + u * 0.5, 1.5)}" fill="{apo}"/>')
        nome = f"fita métrica · reta · {ini}–{fim} cm"
    else:
        R = w * 0.5
        h = u * 1.4
        a0, a1 = 200, 340
        comp = math.radians(a1 - a0) * R
        k = comp / (fim - ini)
        o.append(f'<path d="{setor(0, 0, R - h, R, a0, a1)}" fill="{fundo}"/>')
        d = {1: "", 2: "", 3: ""}
        for i in range(int(round((fim - ini) * 10)) + 1):
            ang = a0 + math.degrees(i * k / 10 / R)
            lv = 3 if i % 10 == 0 else 2 if i % 5 == 0 else 1
            ln = {3: 0.46, 2: 0.3, 1: 0.18}[lv] * h
            p0, p1 = polar(0, 0, R, ang), polar(0, 0, R - ln, ang)
            d[lv] += f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}"
            if lv == 3 and 0 < i < (fim - ini) * 10:
                c = ini + i // 10
                o.append(rot_c(f, str(c), u * 0.5, *polar(0, 0, R - h * 0.72, ang), tk, ang=ang + 90))
        o.append(_p(d[1], stroke=tk, sw=t * 0.32) + _p(d[2], stroke=tk, sw=t * 0.45) + _p(d[3], stroke=tk, sw=t * 0.6))
        nome = f"fita métrica · curva · {ini}–{fim} cm"
    return justo("".join(o), nome, "escala real em cm/mm (mm curto, 0,5 cm médio, cm longo e numerado) · régua de "
                 "progresso, perímetro, divisor")


def wells(f, pes=23, alcance=None, w=470.0):
    """Banco de Wells (sentar e alcançar): régua em cm com a linha dos pés no protocolo declarado (23 cm =
    FitnessGram; 26 cm = normas canadenses). alcance = parâmetro (cursor).
    Revisão 10/2026: cursor em triângulo apontando a escala; o rótulo dos pés fica do lado OPOSTO ao cursor (nunca
    encostam); unidade 'cm' em minúscula."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    fim = 50
    k = w / fim
    h = u * 1.3
    o = [_p(f"M0 0H{w:.2f}", stroke=ink, sw=t * 0.6)]
    d = ""
    for i in range(fim + 1):
        ln = h * (0.7 if i % 10 == 0 else 0.45 if i % 5 == 0 else 0.22)
        d += f"M{min(max(i * k, t * 0.225), w - t * 0.225):.2f} 0V{ln:.2f}"
        if i % 10 == 0:
            o.append(rot_tinta(f, str(i), u * 0.5, i * k, h + u * 0.55, ink, anchor="start" if i == 0 else "end" if i == fim else "middle"))
    o.append(_p(d, stroke=ink, sw=t * 0.45))
    xp = pes * k
    o.append(_p(f"M{xp:.2f} {-u * 1.6:.2f}V{h * 0.9:.2f}", stroke=ac, sw=t * 0.9))
    esq = alcance is not None and alcance > pes     # cursor à direita da linha → rótulo à esquerda
    o.append(rot_tinta(f, f"PÉS · {pes} cm", u * 0.5, xp + (-u * 0.3 if esq else u * 0.3), -u * 1.0, ac, f.fonte_texto, 0.08,
                 "end" if esq else "start"))
    if alcance is not None:
        xa = alcance * k
        tri = [(xa, -t * 0.4), (xa - u * 0.3, -u * 0.85), (xa + u * 0.3, -u * 0.85)]
        o.append(f'<path d="{poligono(tri)}" fill="{ink}"/>')
    prot = {23: "FITNESSGRAM", 26: "NORMAS CANADENSES"}.get(pes, "PROTOCOLO")
    o.append(rot_tinta(f, f"SENTAR E ALCANÇAR · {prot}", u * 0.46, 0, h + u * 1.9, apo, tr=0.05))
    return justo("".join(o), f"banco de Wells · pés a {pes} cm" + (f" · cursor {alcance}" if alcance is not None else ""),
                 "régua em cm com a linha dos pés do protocolo declarado (nunca misturar) · régua de progresso 'alcance'")


@amostra(FAM, "fita métrica e Wells")
def _a_fita(f):
    return [fita_metrica(f), fita_metrica(f, 84, 96, cor=f.tinta), fita_metrica(f, 0, 20, "curva"),
            fita_metrica(f, 60, 75, "curva", cor=f.papel), wells(f), wells(f, 26, 31)]


# ================================================================ adipômetro (14b 5.21)
def adipometro(f, leitura=12.4, modo="contorno", dobra=True, R=66.0):
    """Adipômetro de mostrador (tipo Harpenden) pinçando a dobra cutânea: relógio de 0–20 mm por volta em divisões de
    0,2 mm, dois braços ARQUEADOS de compasso e pastilhas paralelas. leitura = espessura da dobra em mm (parâmetro):
    abre as pontas e move o ponteiro.
    Revisão 10/2026 (redesenho): braços curvos (antes retos = 'relógio em palafitas'); numerais 0-5-10-15 por FORA
    dos tiques e o ponteiro termina na ponta dos tiques — nunca risca um número; 'mm' minúsculo."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    cheio = modo == "cheio"
    k = R / 30.0                      # px por mm (mostrador de 60 mm)
    g = max(leitura, 1.0) * k         # abertura entre as pastilhas
    aw = R * 0.15                     # espessura do braço
    pw, ph = aw * 1.3, R * 0.5        # pastilha
    yj = R * 2.95                     # altura do centro das pastilhas
    xp = g / 2 + pw / 2               # centro da pastilha
    o = []
    if dobra:
        ys = yj + R * 0.98
        ya = yj - ph * 0.62
        W = R * 2.1
        lado = [(-W, ys), (-R * 1.1, ys), (-R * 0.5, ys - R * 0.08), (-g / 2 - pw - R * 0.04, yj + ph * 0.5 + R * 0.25),
                (-g / 2, yj + ph * 0.1), (-g * 0.42, ya + R * 0.07), (0, ya)]
        pts = lado + [(-x, y) for x, y in reversed(lado[:-1])]
        d = suave(pts, tensao=0.55)
        o.append(f'<path d="{d}Z" fill="{mistura(f.fundo, ac, 0.3)}"/>')
        o.append(_p(d, stroke=ink, sw=t * 0.8, extra='stroke-linecap="round"'))
    # braços arqueados: tubo = traço grosso + miolo na cor do corpo (contorno) ou traço único (cheio)
    for s in (-1, 1):
        S = (s * R * 0.42, R * 0.9)
        C1, C2 = (s * R * 0.95, R * 1.5), (s * R * 0.62, R * 2.35)
        E = (s * xp, yj - ph * 0.5)
        d = f"M{S[0]:.2f} {S[1]:.2f}C{C1[0]:.2f} {C1[1]:.2f} {C2[0]:.2f} {C2[1]:.2f} {E[0]:.2f} {E[1]:.2f}"
        if cheio:
            o.append(_p(d, stroke=ac, sw=aw, extra='stroke-linecap="butt"'))
        else:
            o.append(_p(d, stroke=ink, sw=aw + 2 * t * 0.8, extra='stroke-linecap="butt"'))
            o.append(_p(d, stroke=f.fundo, sw=aw, extra='stroke-linecap="butt"'))
        # pastilha: pílula de tinta, face voltada para a dobra
        o.append(f'<path d="{ret(s * xp - pw / 2, yj - ph / 2, pw, ph, pw / 2)}" fill="{ink}"/>')
    # mostrador
    o.append(f'<circle r="{R:.2f}" fill="{f.fundo}" stroke="{ink}" stroke-width="{t * 1.3:.2f}"/>')
    re = R * 0.62                      # ponta externa dos tiques (e do ponteiro)
    d1 = d2 = ""
    for i in range(100):
        a = -90 + i * 3.6
        lng = i % 5 == 0
        p0, p1 = polar(0, 0, re - R * (0.12 if lng else 0.06), a), polar(0, 0, re, a)
        if lng:
            d2 += f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}"
        else:
            d1 += f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}"
    o.append(_p(d1, stroke=ink, sw=t * 0.28) + _p(d2, stroke=ink, sw=t * 0.5))
    r_num = R * 0.80
    for mm in (0, 5, 10, 15):
        o.append(rot_c(f, str(mm), R * 0.2, *polar(0, 0, r_num, -90 + mm * 18), ink))
    o.append(rot_c(f, "mm", R * 0.17, *polar(0, 0, r_num, -45), apo, f.fonte_texto, 0.04))
    a = -90 + (leitura % 20) * 18
    p0, p1 = polar(0, 0, -R * 0.12, a), polar(0, 0, re, a)
    o.append(_p(f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}", stroke=ac, sw=t * 0.8, extra='stroke-linecap="round"'))
    o.append(f'<circle r="{R * 0.07:.2f}" fill="{ac}"/>')
    return justo("".join(o), f"adipômetro · {modo}" + (" · na dobra" if dobra else "") + f" · {num(leitura)} mm",
                 "relógio 0–20 mm/volta em 0,2 mm, braços de compasso e pastilhas paralelas pinçando a dobra · "
                 "avaliação física, protocolo")


@amostra(FAM, "adipômetro")
def _a_adip(f):
    # (a variante sem dobra foi REMOVIDA: sem a dobra entre as pastilhas, os braços viravam um estetoscópio/pinça)
    return [adipometro(f), adipometro(f, 8.0, "cheio")]


# ================================================================ ficha de treino (prancheta)
FICHA_EXEMPLO = [("AGACHAMENTO", "4", "8", "90 s"), ("SUPINO", "4", "8", "90 s"),
                 ("REMADA", "3", "10", "60 s"), ("TERRA", "3", "5", "120 s"),
                 ("PRANCHA", "3", "40 s", "45 s")]


def _tabela_treino(f, x, y, w, linhas, cor, apo, ac, ns, esquema=False, titulo="TREINO A"):
    """Tabela EXERCÍCIO · SÉR. · REP. · CARGA · PAUSA. CARGA fica em branco (a ficha é para preencher).
    Revisão 10/2026: as colunas são MEDIDAS pelo conteúdo (maior texto de cada coluna + folga) — nada encosta no
    vizinho; o corpo do texto encolhe até a coluna CARGA (linha de preencher) caber. Devolve (svg, altura, ns)."""
    o = []
    cab = ["EXERCÍCIO", "SÉR.", "REP.", "CARGA", "PAUSA"]

    def colunas(n_):
        nh = n_ * 0.8
        gap = n_ * 1.15
        cw = [max([largura(f.fonte_texto, cab[0], nh, 0.08)] + [largura(f.fonte_texto, r[0], n_, 0.02) for r in linhas]),
              max([largura(f.fonte_texto, cab[1], nh, 0.08)] + [largura(f.fonte_mono, r[1], n_) for r in linhas]),
              max([largura(f.fonte_texto, cab[2], nh, 0.08)] + [largura(f.fonte_mono, r[2], n_) for r in linhas]),
              0.0,
              max([largura(f.fonte_texto, cab[4], nh, 0.08)] + [largura(f.fonte_mono, r[3], n_) for r in linhas])]
        cw[3] = w - (cw[0] + cw[1] + cw[2] + cw[4] + 4 * gap)
        return cw, gap

    while True:
        cw, gap = colunas(ns)
        if cw[3] >= ns * 3.2 or ns <= 4:
            break
        ns -= 0.2
    xs = [0.0, cw[0] + gap]
    xs.append(xs[1] + cw[1] + gap)
    xs.append(xs[2] + cw[2] + gap)
    xs.append(xs[3] + cw[3] + gap)      # início da coluna PAUSA (o texto é alinhado à direita em x + w)
    lh = ns * 2.35
    o.append(rot_tinta(f, titulo, ns * 1.45, x, y + cap(f.fonte_display) * ns * 1.45, cor, f.fonte_display, 0.02))
    tw = largura(f.fonte_mono, "EXEMPLO", ns * 0.8, 0.1)
    sw_ = max(1.0, ns * 0.09)
    o.append(_p(ret(x + w - tw - ns * 1.2 + sw_ / 2, y + sw_ / 2, tw + ns * 1.2 - sw_, ns * 1.6 - sw_, (ns * 1.6 - sw_) / 2),
                stroke=ac, sw=sw_))
    o.append(rot_tinta(f, "EXEMPLO", ns * 0.8, x + w - tw / 2 - ns * 0.6, y + ns * 0.8 + cap(f.fonte_mono) * ns * 0.4, ac,
                 tr=0.1, anchor="middle"))
    yy = y + ns * 2.9
    for j, h in enumerate(cab):
        if j == 4:
            o.append(rot_tinta(f, h, ns * 0.8, x + w, yy, apo, f.fonte_texto, 0.08, "end"))
        else:
            o.append(rot_tinta(f, h, ns * 0.8, x + xs[j], yy, apo, f.fonte_texto, 0.08))
    yy += ns * 0.7
    o.append(_p(f"M{x:.2f} {yy:.2f}H{x + w:.2f}", stroke=cor, sw=max(1.0, ns * 0.12)))
    for nome, ser, rep, pausa in linhas:
        base = yy + lh * 0.62
        if esquema:
            bw = largura(f.fonte_texto, nome, ns, 0.02)
            o.append(f'<path d="{ret(x, base - cap(f.fonte_texto) * ns, min(bw, cw[0]), cap(f.fonte_texto) * ns, 1)}" fill="{cor}" fill-opacity="0.85"/>')
        else:
            o.append(rot_tinta(f, nome, ns, x, base, cor, f.fonte_texto, 0.02))
        o.append(rot_tinta(f, ser, ns, x + xs[1], base, cor))
        o.append(rot_tinta(f, rep, ns, x + xs[2], base, cor))
        o.append(_p(f"M{x + xs[3]:.2f} {base + 1:.2f}H{x + xs[3] + cw[3]:.2f}", stroke=apo, sw=max(0.8, ns * 0.08)))
        o.append(rot_tinta(f, pausa, ns, x + w, base, cor, anchor="end"))
        yy += lh
        o.append(_p(f"M{x:.2f} {yy:.2f}H{x + w:.2f}", stroke=apo, sw=max(0.6, ns * 0.06), extra='stroke-opacity="0.7"'))
    return "".join(o), yy - y, ns


def ficha_treino(f, linhas=None, modo="prancheta", titulo="TREINO A"):
    """Ficha de treino como TABELA (séries × repetições × carga × pausa). linhas = parâmetro; a amostra traz um
    exemplo rotulado "EXEMPLO" e a coluna CARGA em branco. modo: prancheta | folha | esquema (barras no lugar dos
    nomes)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    linhas = linhas or FICHA_EXEMPLO
    o = []
    if modo == "prancheta":
        W, H = 280.0, 330.0
        o.append(f'<path d="{ret(0, 0, W, H, f.raio)}" fill="{mistura(f.fundo, ink, 0.2)}"/>')
        pad = W * 0.06
        px0, pw = pad * 2, W - 4 * pad
        o.append(f'<path d="{ret(pad, pad * 1.6, W - 2 * pad, H - pad * 2.6, 2)}" fill="{f.papel}"/>')
        cinza = mistura(f.papel, f.fundo, 0.55)
        y = pad * 1.6 + W * 0.15
        ns = 11.0
        for i, rot_ in enumerate(("ALUNO", "DATA")):
            xx = px0 + (0 if i == 0 else pw * 0.66)
            o.append(rot_tinta(f, rot_, ns * 0.8, xx, y, cinza, f.fonte_texto, 0.08))
            x1 = xx + largura(f.fonte_texto, rot_, ns * 0.8, 0.08) + ns * 0.5
            o.append(_p(f"M{x1:.2f} {y + 1:.2f}H{(px0 + pw * 0.6) if i == 0 else px0 + pw:.2f}", stroke=cinza, sw=0.8))
        tab, th, ns = _tabela_treino(f, px0, y + ns * 1.6, pw, linhas, f.fundo, cinza,
                                     ac if luminancia(ac) < 0.5 else mistura(ac, f.fundo, 0.35), ns, titulo=titulo)
        o.append(tab)
        yo = y + 11.0 * 1.6 + th + ns * 2.4
        o.append(rot_tinta(f, "OBSERVAÇÕES", ns * 0.8, px0, yo, cinza, f.fonte_texto, 0.08))
        for j in range(3):
            yy = yo + ns * 2.2 * (j + 1)
            if yy < H - pad * 1.6:
                o.append(_p(f"M{px0:.2f} {yy:.2f}H{px0 + pw:.2f}", stroke=cinza, sw=0.7, extra='stroke-opacity="0.7"'))
        cw, ch = W * 0.42, W * 0.13       # prendedor
        o.append(f'<path d="{ret(W / 2 - cw / 2, -ch * 0.35, cw, ch, ch * 0.3)}" fill="{apo}"/>')
        o.append(f'<path d="{ret(W / 2 - cw * 0.3, -ch * 0.75, cw * 0.6, ch * 0.55, ch * 0.25)}" fill="none" '
                 f'stroke="{apo}" stroke-width="{t * 1.2:.2f}"/>')
        o.append(f'<path d="{ret(W / 2 - cw * 0.36, ch * 0.4, cw * 0.72, ch * 0.18, 1)}" fill="{mistura(apo, f.fundo, 0.3)}"/>')
        el = justo("".join(o), "ficha de treino · prancheta", "tabela real de prescrição (séries × reps × carga × pausa), "
                   "rotulada EXEMPLO, carga em branco · bastidor, conteúdo de método")
        return el
    W = 470.0
    tab, h, _ = _tabela_treino(f, 0, 0, W, linhas, ink, apo, ac, 13.0, esquema=modo == "esquema", titulo=titulo)
    return justo(tab, f"ficha de treino · {modo}", "tabela de prescrição com fios finos e números alinhados; "
                 + ("nomes como barras (esquema)" if modo == "esquema" else "exemplo rotulado") + " · post de conteúdo, site")


@amostra(FAM, "ficha de treino")
def _a_ficha(f):
    return [ficha_treino(f), ficha_treino(f, modo="folha"), ficha_treino(f, modo="esquema", titulo="TREINO B")]


# ================================================================ agilidade: cone, pratinho, escada, T-test
def cone(f, modo="cheio", H=150.0, listra=False):
    """Cone de agilidade de lado (base quadrada de aba, corpo cônico, topo arredondado com furo).
    listra = 2 faixas refletivas (com UMA só, o contorno virava a letra "A")."""
    t, ink, ac = f.traco, f.tinta, f.acento
    cheio = modo == "cheio"
    fill = ac if cheio else f.fundo
    st = "" if cheio else f'stroke="{ink}" stroke-width="{t:.2f}" stroke-linejoin="round"'
    bw, bh = H * 0.86, H * 0.07
    tw = H * 0.15
    r = bh * 0.35
    corpo = (f"M{-bw / 2 + r:.2f} {H - bh:.2f}H{-bw * 0.36:.2f}L{-tw / 2:.2f} {H * 0.07:.2f}"
             f"Q0 {-H * 0.02:.2f} {tw / 2:.2f} {H * 0.07:.2f}L{bw * 0.36:.2f} {H - bh:.2f}H{bw / 2 - r:.2f}"
             f"Q{bw / 2:.2f} {H - bh:.2f} {bw / 2:.2f} {H - bh + r:.2f}V{H - r:.2f}Q{bw / 2:.2f} {H:.2f} {bw / 2 - r:.2f} {H:.2f}"
             f"H{-bw / 2 + r:.2f}Q{-bw / 2:.2f} {H:.2f} {-bw / 2:.2f} {H - r:.2f}V{H - bh + r:.2f}"
             f"Q{-bw / 2:.2f} {H - bh:.2f} {-bw / 2 + r:.2f} {H - bh:.2f}Z")
    o = [f'<path d="{corpo}" fill="{fill}" {st}/>']
    if listra:
        def xa(y):
            k = (y - H * 0.07) / (H - bh - H * 0.07)
            return tw / 2 + (bw * 0.36 - tw / 2) * k
        for y0, y1 in ((H * 0.30, H * 0.40), (H * 0.50, H * 0.60)):
            o.append(f'<path d="{poligono([(-xa(y0), y0), (xa(y0), y0), (xa(y1), y1), (-xa(y1), y1)])}" '
                     f'fill="{f.fundo if cheio else ac}"/>')
    return justo("".join(o), f"cone de agilidade · {modo}" + (" · listra" if listra else ""),
                 "cone de treino (aba quadrada + corpo cônico) · marcador de etapa, percurso, lista")


def pratinhos(f, n=7, modo="cheio", w=460.0, ativo=None):
    """Fileira de cones-pratinho (chapéu chinês) de lado: domo baixo com furo no topo — divisor de percurso.
    ativo = índice destacado (parâmetro)."""
    t, ink, ac = f.traco, f.tinta, f.acento
    pw = w / (n * 1.6 - 0.6)
    ph = pw * 0.36
    o = []
    for i in range(n):
        x = i * pw * 1.6
        cor = ac if (ativo is None or i == ativo) else mistura(f.fundo, ink, 0.3)
        d = (f"M{x:.2f} {ph:.2f}C{x + pw * 0.08:.2f} {ph * 0.25:.2f} {x + pw * 0.3:.2f} 0 {x + pw * 0.4:.2f} 0"
             f"H{x + pw * 0.6:.2f}C{x + pw * 0.7:.2f} 0 {x + pw * 0.92:.2f} {ph * 0.25:.2f} {x + pw:.2f} {ph:.2f}Z")
        if modo == "cheio":
            o.append(f'<path d="{d}" fill="{cor}"/>')
        else:
            o.append(f'<path d="{d}" fill="none" stroke="{cor if ativo is not None else ink}" stroke-width="{t * 0.8:.2f}" stroke-linejoin="round"/>')
    return justo("".join(o), f"pratinhos · {n} · {modo}" + (f" · {ativo + 1}º ativo" if ativo is not None else ""),
                 "cone-pratinho de treino em fileira · divisor de percurso, etapas, progresso")


def escada(f, n=8, feitos=None, w=460.0):
    """Escada de agilidade vista de cima: degraus de 45 cm, largura 50 cm (proporção real). feitos = quantos
    quadrados já foram (progresso, parâmetro)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    sp = w / n
    lw = sp * 50 / 45
    o = []
    if feitos:
        for i in range(feitos):
            o.append(f'<path d="{ret(i * sp + t, t, sp - 2 * t, lw - 2 * t, 0)}" fill="{ac}" fill-opacity="0.85"/>')
    o.append(_p(f"M{-sp * 0.15:.2f} 0H{w + sp * 0.15:.2f}M{-sp * 0.15:.2f} {lw:.2f}H{w + sp * 0.15:.2f}", stroke=apo, sw=t * 0.9))
    for i in range(n + 1):
        o.append(f'<path d="{ret(i * sp - t * 0.9, -t * 0.5, t * 1.8, lw + t, t * 0.6)}" fill="{ink}"/>')
    return justo("".join(o), f"escada de agilidade · {n}" + (f" · {feitos} feitos" if feitos else ""),
                 "escada de agilidade de cima (45 × 50 cm) · barra de progresso, linha do tempo, divisor")


def t_test(f, k=27.0):
    """T-test de agilidade (Semenick, 1990): cones A→B a 9,14 m (10 jardas), C e D a 4,57 m (5 jardas) de B.
    Corrida A→B, deslocamento lateral B→C→D→B, de costas B→A. Esquema com distâncias reais."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    L, M = 9.14 * k, 4.57 * k
    A, B, C, D = (0, 0), (0, -L), (-M, -L), (M, -L)
    o = []
    seta = lambda x, y, ang: poligono([polar(x, y, 0, 0), polar(x, y, u * 0.42, ang + 155), polar(x, y, u * 0.42, ang - 155)])  # noqa: E731
    off = u * 0.42
    o.append(_p(f"M{-off:.2f} {-u * 0.6:.2f}V{-L + u * 0.9:.2f}", stroke=ac, sw=t * 0.8))
    o.append(f'<path d="{seta(-off, -L + u * 0.7, -90)}" fill="{ac}"/>')
    o.append(_p(f"M{off:.2f} {-L + u * 0.6:.2f}V{-u * 0.9:.2f}", stroke=ink, sw=t * 0.7, extra='stroke-dasharray="2 5" stroke-linecap="round"'))
    o.append(f'<path d="{seta(off, -u * 0.7, 90)}" fill="{ink}"/>')
    yl = -L - u * 0.75
    o.append(_p(f"M{-M + u * 0.8:.2f} {yl:.2f}H{M - u * 0.8:.2f}", stroke=ink, sw=t * 0.7, extra='stroke-dasharray="7 4"'))
    o.append(f'<path d="{seta(-M + u * 0.6, yl, 180)}" fill="{ink}"/><path d="{seta(M - u * 0.6, yl, 0)}" fill="{ink}"/>')
    for nome, (x, y) in zip("ABCD", (A, B, C, D)):
        # cone visto de cima: anel com furo de verdade (evenodd), não um ponto pintado com a cor do fundo
        o.append(f'<path d="{circ(x, y, u * 0.42)}{circ(x, y, u * 0.12)}" fill-rule="evenodd" '
                 f'fill="{ac if nome == "A" else ink}"/>')
        dy = u * 1.25 if nome == "A" else -u * 1.6
        o.append(rot_c(f, nome, u * 0.62, x, y + dy, ink, f.fonte_texto))
    o.append(rot_tinta(f, "9,14 m", u * 0.5, -off - u * 0.5, -L / 2, apo, anchor="end"))
    o.append(rot_tinta(f, "4,57 m", u * 0.5, -M / 2, -L + u * 1.0, apo, anchor="middle"))
    o.append(rot_tinta(f, "4,57 m", u * 0.5, M / 2, -L + u * 1.0, apo, anchor="middle"))
    o.append(rot_tinta(f, "T-TEST · SEMENICK (1990)", u * 0.46, M * 0.35, -u * 0.1, apo, tr=0.05))
    return justo("".join(o), "T-test de agilidade · esquema", "teste real com distâncias reais (10 e 5 jardas) · "
                 "percurso, etapas, diagrama de método")


@amostra(FAM, "agilidade")
def _a_agil(f):
    return [cone(f), cone(f, "contorno", listra=True), pratinhos(f), pratinhos(f, 7, "contorno", ativo=2),
            escada(f), escada(f, 8, 3), t_test(f)]


# ================================================================ apito
def apito(f, modo="cheio", R=58.0):
    """Apito de bolinha de lado: bocal reto, câmara redonda, janela com lâmina no topo e argola do cordão.
    (A versão com cordão foi REMOVIDA em 10/2026: o fio saía do centro da argola e terminava cortado, no ar.)"""
    t, ink, ac = f.traco, f.tinta, f.acento
    cheio = modo == "cheio"
    fill = ac if cheio else f.fundo
    st = "" if cheio else f'stroke="{ink}" stroke-width="{t:.2f}" stroke-linejoin="round"'
    yb = -R + R * 0.5                        # fundo do bocal
    xb = -math.sqrt(R * R - yb * yb)         # onde o bocal encontra a câmara
    n0, n1 = -R * 0.06, R * 0.34
    yn1 = -math.sqrt(R * R - n1 * n1)
    a_n1 = math.degrees(math.atan2(yn1, n1))
    a_b = math.degrees(math.atan2(yb, xb)) + 360
    p_end = polar(0, 0, R, a_b)
    lg = 1 if (a_b - a_n1) > 180 else 0
    corpo = (f"M{-R * 2.25 + R * 0.12:.2f} {-R:.2f}H{n0:.2f}L{n0 + R * 0.04:.2f} {-R * 0.8:.2f}L{n1:.2f} {yn1:.2f}"
             f"A{R:.2f} {R:.2f} 0 {lg} 1 {p_end[0]:.2f} {p_end[1]:.2f}H{-R * 2.25 + R * 0.12:.2f}"
             f"Q{-R * 2.25:.2f} {yb:.2f} {-R * 2.25:.2f} {yb - R * 0.12:.2f}V{-R + R * 0.12:.2f}Q{-R * 2.25:.2f} {-R:.2f} "
             f"{-R * 2.25 + R * 0.12:.2f} {-R:.2f}Z")
    o = []
    ax, ay = polar(0, 0, R * 1.12, 38)
    o.append(f'<circle cx="{ax:.2f}" cy="{ay:.2f}" r="{R * 0.2:.2f}" fill="none" stroke="{ink if not cheio else ac}" '
             f'stroke-width="{t * 1.3:.2f}"/>')
    o.append(f'<path d="{corpo}" fill="{fill}" {st}/>')
    o.append(_p(f"M{-R * 2.0:.2f} {-R * 0.75:.2f}H{-R * 1.15:.2f}", stroke=f.fundo if cheio else ink, sw=t * 0.6,
                extra='stroke-linecap="round" stroke-opacity="0.6"'))
    return justo("".join(o), f"apito · {modo}",
                 "apito de bolinha (bocal + câmara + janela) · voz do professor, chamada, início de prova")


@amostra(FAM, "apito")
def _a_apito(f):
    return [apito(f), apito(f, "contorno")]


# ================================================================ tempo 3-1-2-0, RIR, marcha, planos
def _rotulos_linha(f, itens, w, size, y, spec, gap):
    """Rótulos numa linha sem colisão: cada um começa no seu x (ou logo depois do anterior); se o último passar de w,
    a fila é empurrada da direita para a esquerda. itens = [(x, texto, cor)]."""
    larg = [largura(spec, s, size, 0.06) for _, s, _ in itens]
    xs = []
    for (x, s, c), lw in zip(itens, larg):
        x = max(x, (xs[-1] + larg[len(xs) - 1] + gap) if xs else x)
        xs.append(x)
    lim = w
    for j in range(len(xs) - 1, -1, -1):
        if xs[j] + larg[j] > lim:
            xs[j] = lim - larg[j]
        lim = xs[j] - gap
    return "".join(rot_tinta(f, s, size, x, y, c, spec, 0.06) for x, (_, s, c) in zip(xs, itens))


def tempo(f, fases=(3, 1, 2, 0), modo="barra", w=450.0):
    """Tempo de execução: descida–pausa–subida–pausa (o 1º número é SEMPRE a excêntrica). 0 vira tracinho no acento,
    "X" = subida explosiva (meio segundo no desenho). barra = segmentos proporcionais; metronomo = 1 ponto por segundo."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    nomes = ["DESCE", "PAUSA", "SOBE", "PAUSA"]
    vals = [0.5 if v == "X" else float(v) for v in fases]
    total = sum(vals)
    k = w / total
    o = []
    rot_t = "-".join(str(v) for v in fases)
    o.append(rot_tinta(f, rot_t, u * 1.5, 0, -u * 1.25, ink, f.fonte_display, 0.02))
    seg = sum(v for v in vals)
    o.append(rot_tinta(f, f"{num(seg)} s POR REPETIÇÃO" if "X" not in fases else "X = SUBIDA EXPLOSIVA", u * 0.46, w, -u * 1.25,
                 apo, tr=0.05, anchor="end"))
    x = 0.0
    h = u * 0.95
    itens, zeros = [], []
    zero_xs, acum = [], 0.0
    for vv_ in vals:
        if vv_ == 0:
            zero_xs.append(acum * k)
        acum += vv_
    for i, (v, vv) in enumerate(zip(fases, vals)):
        cor_t = ink if i in (0, 2) else apo
        if vv == 0:
            o.append(_p(f"M{min(max(x, t * 0.45), w - t * 0.45):.2f} {-u * 0.25:.2f}V{h + u * 0.25:.2f}", stroke=ac, sw=t * 0.9))
            zeros.append((x, f"0 {nomes[i]}"))      # fase de duração zero: rótulo na 2ª linha, preso ao marcador
            continue
        cor = ac if i == 0 else (ink if i == 2 else mistura(f.fundo, ink, 0.3))
        if modo == "barra":
            o.append(f'<path d="{ret(x + (1.5 if i else 0), 0, vv * k - (1.5 if i else 0), h, 0)}" fill="{cor}"/>')
        else:
            n = max(1, int(vv))
            for s_ in range(n):
                xs = x + (s_ + 0.5) * vv * k / n
                o.append(f'<circle cx="{xs:.2f}" cy="{h / 2:.2f}" r="{u * 0.28:.2f}" fill="{cor}"/>')
            o.append(_p(f"M{x + 2:.2f} {h + u * 0.25:.2f}H{x + vv * k - 2:.2f}", stroke=apo, sw=t * 0.5))
        # o fio da fase zero desce ao lado: o rótulo que começa no mesmo x ganha folga (nada tangente)
        itens.append((x + (u * 0.22 if any(abs(x - zx) < 0.5 for zx in zero_xs) else 0.0), f"{v} {nomes[i]}", cor_t))
        x += vv * k
    o.append(_rotulos_linha(f, itens, w, u * 0.5, h + u * 1.0, f.fonte_texto, u * 0.6))
    yz = h + u * 1.0 + u * 1.0
    for xz, tz in zeros:
        fim = xz >= w - 1
        o.append(_p(f"M{min(xz, w - t * 0.25):.2f} {h + u * 0.25:.2f}V{yz - cap(f.fonte_texto) * u * 0.5:.2f}", stroke=ac, sw=t * 0.5))
        o.append(rot_tinta(f, tz, u * 0.5, xz + (-u * 0.15 if fim else u * 0.15), yz, ac, f.fonte_texto, 0.06,
                     "end" if fim else "start"))
    if modo == "barra":
        for s_ in range(int(total) + 1):
            xt = min(max(s_ * k, t * 0.25), w - t * 0.25)
            o.append(_p(f"M{xt:.2f} {-u * 0.3:.2f}V{-u * 0.08:.2f}", stroke=apo, sw=t * 0.5))
    return justo("".join(o), f"tempo {rot_t} · {modo}", "cadência real (excêntrica primeiro; 1 tracinho = 1 s) · "
                 "divisor rítmico, legenda de vídeo, animação no compasso")


def rir(f, destaque=None):
    """RPE pela escala de repetições em reserva (Zourdos et al., 2016): 10 = 0 RIR, 9 = 1, 8 = 2, 7 = 3,
    5–6 = 4–6. Quadradinhos vazios = o que sobra. destaque = RPE (parâmetro)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    linhas = [(10, 0, "0 RIR"), (9, 1, "1 RIR"), (8, 2, "2 RIR"), (7, 3, "3 RIR"), (6, 4, "4–6 RIR")]
    o = []
    lh = u * 1.3
    q = u * 0.62
    for i, (rpe, n, lab) in enumerate(linhas):
        y = i * lh
        sel = destaque == rpe
        cor = ac if sel else (ink if destaque is None else apo)
        o.append(rot_tinta(f, f"RPE {'5–6' if rpe == 6 else rpe}", u * 0.6, 0, y + cap(f.fonte_mono) * u * 0.3, cor))
        x0 = u * 4.2
        for j in range(4):
            xq = x0 + j * (q + u * 0.22)
            if j < n:
                o.append(f'<path d="{ret(xq + t * 0.3, y - q / 2 + t * 0.3, q - t * 0.6, q - t * 0.6, 1)}" fill="none" '
                         f'stroke="{cor}" stroke-width="{t * 0.6:.2f}"/>')
            else:
                o.append(f'<path d="{ret(xq + q * 0.3, y - t * 0.3, q * 0.4, t * 0.6, 0)}" fill="{mistura(f.fundo, ink, 0.25)}"/>')
        if rpe == 6:
            o.append(rot_tinta(f, "+", u * 0.6, x0 + 4 * (q + u * 0.22) - u * 0.05, y + cap(f.fonte_mono) * u * 0.3, cor))
        o.append(rot_tinta(f, lab, u * 0.6, x0 + 4 * (q + u * 0.22) + u * 0.8, y + cap(f.fonte_mono) * u * 0.3, cor))
    return justo("".join(o), "RPE × repetições em reserva" + (f" · RPE {destaque}" if destaque else ""),
                 "escala RIR real (não é a Borg 6–20) · contador regressivo, ícone de lista, 'perto da falha'")


def marcha(f, w=390.0):
    """Ciclo da marcha (Perry, "Gait Analysis", 1992): pé direito apoio 0–60% / balanço 60–100%; esquerdo
    defasado 50%; dois duplos apoios de 10% (0–10 e 50–60). Cheio = apoio, contorno = balanço."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    k = w / 100
    h = u * 0.95
    o = []
    for a in (0, 50):
        o.append(f'<path d="{ret(a * k, -u * 0.4, 10 * k, 2 * h + u * 1.2, 0)}" fill="{ac}" fill-opacity="0.22"/>')
    for row, (nome, apoio) in enumerate((("DIREITO", [(0, 60)]), ("ESQUERDO", [(50, 100), (0, 10)]))):
        y = row * (h + u * 0.4)
        for a, b in apoio:
            xa_, xb_ = a * k + (1 if a > 0 else 0), b * k - (1 if b < 100 else 0)
            o.append(f'<path d="{ret(xa_, y, xb_ - xa_, h, 0)}" fill="{ink}"/>')
        bal = [(60, 100)] if row == 0 else [(10, 50)]
        for a, b in bal:
            xa_, xb_ = a * k + (1 if a > 0 else 0), b * k - (1 if b < 100 else 0)
            o.append(f'<path d="{ret(xa_ + t * 0.35, y + t * 0.35, xb_ - xa_ - t * 0.7, h - t * 0.7, 0)}" '
                     f'fill="none" stroke="{ink}" stroke-width="{t * 0.7:.2f}"/>')
        o.append(rot_tinta(f, nome, u * 0.48, -u * 0.4, y + h / 2 + cap(f.fonte_texto) * u * 0.24, apo, f.fonte_texto, 0.08, "end"))
    yb = 2 * h + u * 0.4 + u * 0.9
    for p in range(0, 101, 10):
        xt = min(max(p * k, t * 0.25), w - t * 0.25)
        o.append(_p(f"M{xt:.2f} {yb - u * 0.45:.2f}V{yb - u * 0.2:.2f}", stroke=apo, sw=t * 0.5))
        if p % 50 == 0:
            o.append(rot_tinta(f, f"{p}%", u * 0.46, p * k, yb + u * 0.35, ink, anchor="start" if p == 0 else "end" if p == 100 else "middle"))
    o.append(rot_tinta(f, "APOIO 60%", u * 0.44, 30 * k, -u * 0.75, ink, f.fonte_texto, 0.06, "middle"))
    o.append(rot_tinta(f, "BALANÇO 40%", u * 0.44, 82 * k, -u * 0.75, apo, f.fonte_texto, 0.06, "middle"))
    o.append(rot_tinta(f, "DUPLO APOIO", u * 0.44, 55 * k, -u * 0.75, ac, f.fonte_texto, 0.06, "middle"))
    return justo("".join(o), "ciclo da marcha", "fases reais (60/40, pé oposto a 50%, duplos apoios de 10%) · linha do "
                 "tempo em fases, barra de progresso, divisor")


def planos(f, destaque=None, s=138.0):
    """Planos anatômicos em projeção dimétrica: frontal (cheio, LARGO), sagital (tracejado, em profundidade),
    transversal (pontilhado), perpendiculares e cruzando no centro. destaque = 'frontal' | 'sagital' | 'transversal'
    (no acento). Revisão 10/2026: antes, na isométrica, a borda do frontal coincidia com a do sagital (contínuo sobre
    tracejado, parecia erro); agora o eixo da profundidade é encurtado e as bordas nunca se sobrepõem."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    ex = (math.cos(math.radians(12)), math.sin(math.radians(12)))          # esquerda → direita (quase horizontal)
    ey = (0.60 * math.cos(math.radians(35)), -0.60 * math.sin(math.radians(35)))   # profundidade (encurtada)

    def P(x, y, z):
        return (x * ex[0] + y * ey[0], x * ex[1] + y * ey[1] - z)
    a, b = s * 0.62, s * 0.82
    PL = {"frontal": [(-a, 0, -b), (a, 0, -b), (a, 0, b), (-a, 0, b)],
          "sagital": [(0, -a, -b), (0, a, -b), (0, a, b), (0, -a, b)],
          "transversal": [(-a, -a, 0), (a, -a, 0), (a, a, 0), (-a, a, 0)]}
    estilo = {"frontal": "", "sagital": 'stroke-dasharray="8 5"', "transversal": 'stroke-dasharray="1.5 4" stroke-linecap="round"'}
    o = []
    for nome in ("sagital", "frontal", "transversal"):
        pts = [P(*p) for p in PL[nome]]
        sel = destaque == nome
        fill = f'fill="{ac}" fill-opacity="0.32"' if sel else f'fill="{ink}" fill-opacity="0.05"'
        o.append(f'<path d="{poligono(pts)}" {fill} stroke="{ac if sel else ink}" stroke-width="{t * (0.9 if sel else 0.7):.2f}" '
                 f'{estilo[nome]} stroke-linejoin="round"/>')
    for p0, p1 in (((-a, 0, 0), (a, 0, 0)), ((0, -a, 0), (0, a, 0)), ((0, 0, -b), (0, 0, b))):
        q0, q1 = P(*p0), P(*p1)
        o.append(_p(f"M{q0[0]:.2f} {q0[1]:.2f}L{q1[0]:.2f} {q1[1]:.2f}", stroke=apo, sw=t * 0.4))
    o.append(f'<circle r="{t * 1.4:.2f}" fill="{ac}"/>')
    # cada nome sai de um canto livre do seu plano (fora dos outros planos), para a direita ou a esquerda
    labs = {"frontal": (P(a, 0, -b), 1), "sagital": (P(0, a, b), 1), "transversal": (P(-a, -a, 0), -1)}
    for nome, ((x, y), lado) in labs.items():
        dx = lado * u * 1.6
        o.append(_p(f"M{x:.2f} {y:.2f}H{x + dx:.2f}", stroke=apo, sw=t * 0.4))
        o.append(rot_tinta(f, nome.upper(), u * 0.48, x + dx + lado * u * 0.3, y + cap(f.fonte_texto) * u * 0.24,
                     ac if destaque == nome else ink, f.fonte_texto, 0.08, "start" if lado > 0 else "end"))
    return justo("".join(o), "planos anatômicos" + (f" · {destaque}" if destaque else ""),
                 "3 planos perpendiculares com os nomes certos (não existe 'plano lateral') · ícone de biomecânica, capa")


@amostra(FAM, "ritmo e movimento")
def _a_ritmo(f):
    return [tempo(f), tempo(f, (3, 0, "X", 1)), tempo(f, (4, 1, 1, 0), "metronomo"), rir(f), rir(f, 8), marcha(f),
            planos(f), planos(f, "sagital")]
