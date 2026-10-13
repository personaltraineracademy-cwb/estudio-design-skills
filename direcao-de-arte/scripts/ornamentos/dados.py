"""ornamentos.dados — família "dados e esquemas": progresso, contadores, linha do tempo, heatmap, comparação, curvas,
tabelas e ícones de status.

Regra (references/elementos.md; pesquisa 11 E103–E110, 14b §4.8): DADO DE ENFEITE É VERDADEIRO OU É ESQUEMA ROTULADO.
- dado real entra por PARÂMETRO (valor, total, datas, matriz, linhas); a amostra usa só o que é verdadeiro sem consulta
  (3 noites, o calendário de novembro de 2026, o protocolo Tabata, a tabela de zonas, as anilhas IWF);
- curva sem dado real = ESQUEMA, com a palavra "ESQUEMA" desenhada; contagem sem a hora real = "EXEMPLO" desenhado;
- nunca: gráfico subindo de banco de imagem, "REF-0042-X", porcentagem inventada.

Revisão um a um (`_revisao/dados.md`): todo texto que precisa ser LIDO tem maiúscula ≥ 25,6 px no tamanho
natural (elementos.md: "rótulo ≥ 25 px num lado de 1080") — por isso os rótulos usam `R()` (corpo calculado pela altura
da maiúscula) e são alinhados pela TINTA (`tinta=True`), não pela caixa da fonte. Onde a fonte de texto não cabe, o
rótulo usa a display condensada da ficha. Raios só da escala (0 · raio_sm · raio · raio_lg · pílula); célula, tabela e
dado = 0 (references/forma.md). Nada de "furo" pintado com a cor do fundo: buraco é buraco (máscara/geometria).
"""
import calendar
import functools
import math

from . import nucleo as _N
from .nucleo import amostra, largura, cap, ret, poligono, polilinha, suave, _font
from .assunto import justo as _justo, mistura, polar, arco, setor, num, _p, semente, circ, uid, DISCO, IWF, ZONAS

FAM = "dados"
LER = 25.6          # altura mínima da MAIÚSCULA (px num lado de 1080) de texto que precisa ser lido


def justo(corpo, nome, nota="", **kw):
    kw.setdefault("familia", FAM)
    return _justo(corpo, nome, nota, **kw)


# ================================================================ rótulos legíveis, alinhados pela tinta
def corpo(spec, cap_px=LER):
    """Corpo (px) cuja maiúscula mede cap_px."""
    return cap_px / cap(spec)


@functools.lru_cache(maxsize=4096)
def _tinta_x(spec, s, size, tr):
    """(x0, x1, avanço) da tinta do texto, relativos à origem (sem âncora)."""
    from fontTools.pens.boundsPen import BoundsPen
    fo = _font(spec)
    names, adv = fo.advances(s, size, tr)
    k = size / fo.upm
    x, x0, x1 = 0.0, None, None
    for g, a in zip(names, adv):
        bp = BoundsPen(fo.gs)
        fo.gs[g].draw(bp)
        if bp.bounds:
            gx0, _, gx1, _ = bp.bounds
            x0 = x + gx0 * k if x0 is None else min(x0, x + gx0 * k)
            x1 = x + gx1 * k if x1 is None else max(x1, x + gx1 * k)
        x += a
    return (x0 if x0 is not None else 0.0), (x1 if x1 is not None else x), x


def R(f, s, x, base, fill, spec=None, anchor="start", tr=0.04, cap_px=LER, tinta=True):
    """Rótulo em curvas com maiúscula = cap_px. anchor start|middle|end; tinta=True alinha a TINTA em x."""
    spec = spec or f.fonte_texto
    size = corpo(spec, cap_px)
    x0, x1, adv = _tinta_x(spec, s, round(size, 4), tr)
    if anchor == "start":
        xo = x - x0 if tinta else x
    elif anchor == "end":
        xo = x - x1 if tinta else x - adv
    else:
        xo = x - (x0 + x1) / 2 if tinta else x - adv / 2
    svg, _ = _N.texto(spec, s, size, xo, base, fill, tr, "start")
    return svg


def RC(f, s, cx, cy, fill, spec=None, tr=0.04, cap_px=LER):
    """Rótulo centrado nos dois eixos (centro da maiúscula em cy)."""
    return R(f, s, cx, cy + cap_px / 2, fill, spec, "middle", tr, cap_px)


def RW(f, s, spec=None, tr=0.04, cap_px=LER):
    """Largura da TINTA do rótulo."""
    spec = spec or f.fonte_texto
    x0, x1, _ = _tinta_x(spec, s, round(corpo(spec, cap_px), 4), tr)
    return x1 - x0


@functools.lru_cache(maxsize=1024)
def _desce(spec, s, size):
    """Quanto a TINTA do texto desce abaixo da linha de base (px; ≥ 0). A barra "/" do display passa da base: o que
    vier embaixo precisa de folga a partir daí, não da base."""
    from fontTools.pens.boundsPen import BoundsPen
    fo = _font(spec)
    names, _ = fo.advances(s, size, 0.0)
    k = size / fo.upm
    baixo = 0.0
    for g in names:
        bp = BoundsPen(fo.gs)
        fo.gs[g].draw(bp)
        if bp.bounds:
            baixo = max(baixo, -bp.bounds[1] * k)
    return baixo


def exemplo(f, x, base, anchor="start"):
    """Selo 'EXEMPLO' (número sem dado real ainda — tirar quando entrar o valor de verdade)."""
    return R(f, "EXEMPLO", x, base, f.acento, f.fonte_mono, anchor, tr=0.12)


def _trilho(f):
    return mistura(f.fundo, f.tinta, 0.16)


# ================================================================ barra de progresso
def barra_progresso(f, valor=2, total=3, modo="continua", rotulo="NOITE", w=440.0):
    """Progresso valor/total (medido: 2/3 = 2/3 da largura). continua (pílula), segmentos (1 por etapa), degraus
    (etapas crescentes), fina (fio + marcador). Rótulo legível "NOITE 2 DE 3" em cima, alinhado pela tinta."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    trilho = _trilho(f)
    o = []
    lab = f"{rotulo} {valor} DE {total}"
    if modo in ("continua", "segmentos"):
        o.append(R(f, lab, 0, 0, ink))
        y, h = u * 0.7, u * 0.6
        if modo == "continua":
            o.append(f'<path d="{ret(0, y, w, h, h / 2)}" fill="{trilho}"/>')
            if valor:
                o.append(f'<path d="{ret(0, y, w * valor / total, h, h / 2)}" fill="{ac}"/>')
        else:
            gap = u * 0.3
            sw = (w - gap * (total - 1)) / total
            for i in range(total):
                o.append(f'<path d="{ret(i * (sw + gap), y, sw, h, h / 2)}" fill="{ac if i < valor else trilho}"/>')
    elif modo == "degraus":
        gap = u * 0.25
        sw = (w - gap * (total - 1)) / total
        hmax = u * 3.2
        for i in range(total):
            x = i * (sw + gap)
            h = hmax * (i + 1) / total
            cor = ac if i < valor else trilho
            o.append(f'<path d="{ret(x, hmax - h, sw, h, 0)}" fill="{cor}"/>')
            o.append(R(f, str(i + 1), x, hmax - h - u * 0.35, ink if i < valor else apo, f.fonte_display, tr=0))
        o.append(R(f, lab, 0, hmax + u * 0.6 + LER, ink))
    else:   # fina
        o.append(R(f, lab, 0, -u * 1.0, ink))
        o.append(_p(f"M0 0H{w:.2f}", stroke=trilho, sw=t))
        if valor:
            o.append(_p(f"M0 0H{w * valor / total:.2f}", stroke=ac, sw=t))
        for i in range(total + 1):
            x = w * i / total
            o.append(_p(f"M{x:.2f} {-u * 0.3:.2f}V{u * 0.3:.2f}", stroke=ac if i <= valor else apo, sw=t * 0.6))
        o.append(f'<circle cx="{w * valor / total:.2f}" r="{u * 0.42:.2f}" fill="{ac}"/>')
    return justo("".join(o), f"barra de progresso · {modo} · {valor}/{total}",
                 "valor/total vêm da campanha (ex.: 3 noites) — nunca % inventada · topo de story, página, série")


@amostra(FAM, "barra de progresso")
def _a_barra(f):
    return [barra_progresso(f, 2, 3), barra_progresso(f, 1, 3, "segmentos"), barra_progresso(f, 3, 3, "segmentos"),
            barra_progresso(f, 2, 3, "degraus"), barra_progresso(f, 1, 3, "fina"),
            barra_progresso(f, 5, 8, "segmentos", "RODADA")]


# ================================================================ anel de progresso
def anel_progresso(f, valor=2, total=3, modo="anel", centro=None, legenda="NOITES", R0=150.0):
    """Anel valor/total. anel (arco com ponta redonda — as pontas NÃO passam do valor: o arco é encurtado pelo raio
    da ponta, então 2/3 é 2/3 medido), segmentado (1 setor por etapa), tiques (1 tique por unidade)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    trilho = _trilho(f)
    o = []
    e = R0 * 0.13
    rm = R0 - e / 2
    if modo == "anel":
        o.append(_p(circ(0, 0, rm), stroke=trilho, sw=e))
        if valor >= total:
            o.append(_p(circ(0, 0, rm), stroke=ac, sw=e))
        elif valor:
            d = math.degrees((e / 2) / rm)
            a0, a1 = -90 + d, -90 + 360 * valor / total - d
            if a1 > a0:
                o.append(_p(arco(0, 0, rm, a0, a1), stroke=ac, sw=e, extra='stroke-linecap="round"'))
    elif modo == "segmentado":
        gap = 6.0
        for i in range(total):
            a0 = -90 + i * 360 / total + gap / 2
            o.append(f'<path d="{setor(0, 0, R0 - e, R0, a0, a0 + 360 / total - gap)}" fill="{ac if i < valor else trilho}"/>')
    else:
        apagado = mistura(f.fundo, ink, 0.36)     # tique ainda não cumprido: visível a 25% (D11), sem competir
        for i in range(total):
            a = -90 + i * 360 / total
            lng = i % 5 == 0
            p0, p1 = polar(0, 0, R0 - e * (1.0 if lng else 0.6), a), polar(0, 0, R0, a)
            o.append(_p(f"M{p0[0]:.2f} {p0[1]:.2f}L{p1[0]:.2f} {p1[1]:.2f}", stroke=ac if i < valor else apagado,
                        sw=t * (1.3 if lng else 0.9)))
    txt = centro or f"{valor}/{total}"
    capn = R0 * 0.4
    # a barra "/" do display desce abaixo da base: a legenda começa depois da barra (antes cruzava o "NOITES")
    gap = max(u * 0.5, _desce(f.fonte_display, txt, round(corpo(f.fonte_display, capn), 4)) + u * 0.5)
    topo = -(capn + (gap + LER if legenda else 0)) / 2
    o.append(R(f, txt, 0, topo + capn, ink, f.fonte_display, "middle", 0.0, capn))
    if legenda:
        o.append(R(f, legenda, 0, topo + capn + gap + LER, apo, f.fonte_texto, "middle", 0.1))
    return justo("".join(o), f"anel de progresso · {modo} · {valor}/{total}",
                 "anel com valor real (etapas; segundos do Tabata) · carregamento, contagem, selo de etapa")


@amostra(FAM, "anel de progresso")
def _a_anel(f):
    return [anel_progresso(f), anel_progresso(f, 1, 3, "segmentado"), anel_progresso(f, 3, 3, "segmentado"),
            anel_progresso(f, 20, 30, "tiques", "20 s", "ESFORÇO")]


# ================================================================ contador (dias/horas/min)
def contador(f, dias=2, horas=14, minutos=30, segundos=None, modo="caixas", exemplo_=True):
    """Contagem regressiva com algarismos TABULARES. Valores = a contagem REAL até o evento, calculada na hora de
    gerar; sem ela, exemplo_=True desenha "EXEMPLO". Segundos só em tela viva (peça parada mente no segundo
    seguinte). modo: caixas | linha | placas (flip, com fenda de verdade entre as metades)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    com_seg = segundos is not None
    vals = [(dias, "DIAS"), (horas, "HORAS"), (minutos, "MIN")] + ([(segundos, "SEG")] if com_seg else [])
    n = len(vals)
    o, defs = [], []
    if exemplo_:
        o.append(exemplo(f, 0, -u * 0.6))
    if modo == "caixas":
        gap = u * 0.8
        bw = min(150.0, (468 - gap * (n - 1)) / n)
        sz = (bw - 2 * f.raio) / largura(f.fonte_mono, "00", 1.0)
        capn = cap(f.fonte_mono) * sz
        bh = capn + 2 * f.raio
        for i, (v, lab) in enumerate(vals):
            x = i * (bw + gap)
            o.append(f'<path d="{ret(x, 0, bw, bh, f.raio)}" fill="{mistura(f.fundo, ink, 0.1)}"/>')
            o.append(R(f, f"{v:02d}", x + bw / 2, bh / 2 + capn / 2, ac if i == 0 else ink, f.fonte_mono, "middle", 0, capn))
            o.append(R(f, lab, x + bw / 2, bh + u * 0.6 + LER, apo, f.fonte_texto, "middle", 0.06))
    elif modo == "linha":
        capn = 44.0
        x = 0.0
        for i, (v, lab) in enumerate(vals):
            o.append(R(f, f"{v:02d}", x, capn, ac if i == 0 else ink, f.fonte_mono, "start", 0, capn))
            x += RW(f, f"{v:02d}", f.fonte_mono, 0, capn) + u * 0.4
            un = {"DIAS": "d", "HORAS": "h", "MIN": "min", "SEG": "s"}[lab]     # símbolos SI/usuais, minúsculos
            o.append(R(f, un, x, capn, apo, f.fonte_mono, "start", 0))
            x += RW(f, un, f.fonte_mono, 0) + u * 1.2
    else:   # placas
        cw, ch, gi, gp = 68.0, 100.0, 4.0, u * 1.0
        capn = ch * 0.62
        x = 0.0
        for i, (v, lab) in enumerate(vals[:3]):
            x_par = x
            for d in f"{v:02d}":
                top, bot = mistura(f.fundo, ink, 0.16), mistura(f.fundo, ink, 0.12)
                rs = f.raio_sm
                o.append(f'<path d="{ret(x, 0, cw, ch / 2 - 1, rs, (rs, rs, 0, 0))}" fill="{top}"/>')
                o.append(f'<path d="{ret(x, ch / 2 + 1, cw, ch / 2 - 1, rs, (0, 0, rs, rs))}" fill="{bot}"/>')
                for meia, (y0, y1) in (("a", (0, ch / 2 - 1)), ("b", (ch / 2 + 1, ch))):
                    cid = uid("placa", f.seed, i, x, meia)
                    defs.append(f'<clipPath id="{cid}"><path d="{ret(x, y0, cw, y1 - y0, 0)}"/></clipPath>')
                    o.append(f'<g clip-path="url(#{cid})">'
                             + R(f, d, x + cw / 2, ch / 2 + capn / 2, ink, f.fonte_display, "middle", 0, capn) + "</g>")
                x += cw + gi
            x -= gi
            o.append(R(f, lab, (x_par + x) / 2, ch + u * 0.6 + LER, apo, f.fonte_texto, "middle", 0.04))
            x += gp
    el = justo("".join(o), f"contador · {modo}" + (" · EXEMPLO" if exemplo_ else ""),
               "algarismos tabulares; os valores são a contagem real até o evento (calcular na hora; sem ela, "
               "aparece EXEMPLO) · story de contagem, faixa de site", defs="".join(defs))
    return el


@amostra(FAM, "contador")
def _a_contador(f):
    return [contador(f), contador(f, modo="linha"), contador(f, modo="placas")]


# ================================================================ linha do tempo das 3 noites
def linha_tempo(f, itens=("NOITE 1", "NOITE 2", "NOITE 3"), datas=None, hora="20H30", ativo=None, modo="horizontal",
                w=440.0):
    """Linha do tempo de etapas. datas = parâmetro (lista); ativo = índice da etapa de hoje (acento cheio); antes =
    tinta cheia, depois = contorno VAZADO (o fio para na borda do nó; nada pintado com a cor do fundo).
    modo: horizontal | vertical | trilho (setas com folga paralela constante)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    n = len(itens)
    o = []
    r = u * 0.45
    rh = r * 1.5

    def raio_vis(i):
        return rh if (ativo is not None and i == ativo) else r

    def no(x, y, i):
        if ativo is not None and i == ativo:
            return (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rh:.2f}" fill="{ac}" fill-opacity="0.25"/>'
                    f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{ac}"/>')
        if ativo is not None and i < ativo:
            return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{ink}"/>'
        return (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r - t * 0.4:.2f}" fill="none" stroke="{ink}" '
                f'stroke-width="{t * 0.8:.2f}"/>')

    def sub(i):
        return (datas[i] + " · " if datas else "") + (hora or "")

    if modo == "horizontal":
        xs = [rh + i * (w - 2 * rh) / (n - 1) for i in range(n)]
        for i in range(n - 1):
            a, b = xs[i] + raio_vis(i), xs[i + 1] - raio_vis(i + 1)
            feito = ativo is not None and i < ativo
            o.append(_p(f"M{a:.2f} 0H{b:.2f}", stroke=ink if feito else apo, sw=t * (0.9 if feito else 0.6)))
        for i, it in enumerate(itens):
            x = xs[i]
            anc, xa = ("start", x - raio_vis(i)) if i == 0 else ("end", x + raio_vis(i)) if i == n - 1 else ("middle", x)
            o.append(no(x, 0, i))
            o.append(R(f, it, xa, -(rh + u * 0.5), ac if i == ativo else ink, f.fonte_display, anc, 0.04))
            if sub(i):
                o.append(R(f, sub(i), xa, rh + u * 0.5 + LER, apo, f.fonte_mono, anc, 0.02))
    elif modo == "vertical":
        passo = u * 4.2
        for i in range(n - 1):
            o.append(_p(f"M0 {i * passo + raio_vis(i):.2f}V{(i + 1) * passo - raio_vis(i + 1):.2f}", stroke=apo, sw=t * 0.6))
        for i, it in enumerate(itens):
            y = i * passo
            o.append(no(0, y, i))
            o.append(R(f, it, rh + u * 0.6, y + LER / 2, ac if i == ativo else ink, f.fonte_texto, tr=0.04))
            if sub(i):
                o.append(R(f, sub(i), rh + u * 0.6, y + LER / 2 + u * 0.5 + LER, apo, f.fonte_mono, tr=0.02))
    else:   # trilho: setas; ponta e entalhe paralelos, folga horizontal G constante
        h = LER + u * 1.2
        d = h * 0.3
        G = u * 0.35
        s = (w + (n - 1) * (d - G)) / n
        for i, it in enumerate(itens):
            L = i * (s - d + G)
            Rr = L + s
            pts = [(L, 0)]
            pts += [(Rr - d, 0), (Rr, h / 2), (Rr - d, h)] if i < n - 1 else [(Rr, 0), (Rr, h)]
            pts += [(L, h)] + ([(L + d, h / 2)] if i else [])
            cheio = ativo is not None and i <= ativo
            cor = ac if (ativo is not None and i == ativo) else (ink if cheio else mistura(f.fundo, ink, 0.14))
            o.append(f'<path d="{poligono(pts)}" fill="{cor}"/>')
            tc = f.sobre_acento if i == ativo else (f.fundo if cheio else ink)
            o.append(R(f, it, L + (d if i else 0) + u * 0.5, h / 2 + LER / 2, tc, f.fonte_display, tr=0.04))
        if hora:
            o.append(R(f, f"TODAS ÀS {hora}" if not datas else " · ".join(datas), 0, h + u * 0.6 + LER, apo,
                       f.fonte_mono, tr=0.02))
    return justo("".join(o), f"linha do tempo · {modo}" + (f" · ativo {itens[ativo]}" if ativo is not None else ""),
                 "etapas reais da campanha; datas e hora por parâmetro · agenda, story de série, faixa de site")


@amostra(FAM, "linha do tempo")
def _a_linha(f):
    return [linha_tempo(f), linha_tempo(f, ativo=1), linha_tempo(f, modo="vertical", ativo=0),
            linha_tempo(f, modo="trilho", w=460), linha_tempo(f, modo="trilho", ativo=2, w=460)]


# ================================================================ heatmap / grade de dado
def _nivel(f, q):
    """Cor do nível q (0..1) na rampa da marca: 0 = célula apagada; os níveis acesos começam em 40% do acento para
    o passo 0 → 1 ser visível no escuro."""
    base = mistura(f.fundo, f.tinta, 0.12)
    return base if q <= 0 else mistura(base, f.acento, 0.2 + 0.8 * q)


def heatmap(f, matriz, cel=None, gap=None, rot_lin=None, rot_col=None, col_bordas=False, titulo=None, niveis=None,
            titulo_cor=None, col_esq=False):
    """Grade de quadradinhos a partir de uma MATRIZ de valores 0..1 (None = vazio), células com raio 0 (dado).
    rot_lin = rótulos das linhas (display, à esquerda); rot_col = {índice: rótulo} — no centro da coluna ou, com
    col_bordas=True, na BORDA (marca de tempo: "0", "20", "30 S"). Todo rótulo com maiúscula legível (≥ 25,6 px).
    titulo = str ou lista [(texto, cor)] (display). Devolve o SVG (sem justo)."""
    ink, apo = f.tinta, f.apoio
    u = f.unidade
    lin, col = len(matriz), max(len(r) for r in matriz)
    cel = cel or min(u * 1.3, 440 / col)
    gap = cel * 0.16 if gap is None else gap
    niveis = niveis or 5
    o = []
    wl = max(RW(f, s, f.fonte_display) for s in rot_lin) if rot_lin else 0
    x0 = (wl + u * 0.5) if rot_lin else 0
    for i, r in enumerate(matriz):
        for j, v in enumerate(r):
            if v is None:
                continue
            q = round(v * (niveis - 1)) / (niveis - 1)
            o.append(f'<path d="{ret(x0 + j * cel, i * cel, cel - gap, cel - gap, 0)}" fill="{_nivel(f, q)}"/>')
    if rot_lin:
        for i, s in enumerate(rot_lin):
            o.append(R(f, s, (x0 - u * 0.5) - wl / 2, i * cel + (cel - gap) / 2 + LER / 2, apo, f.fonte_display,
                       "middle", 0.02))
    ytop = 0.0
    if rot_col:
        yb = -u * 0.45
        for j, s in rot_col.items():
            if col_esq:       # um cabeçalho só, na borda esquerda do elemento (mesma do título)
                o.append(R(f, s, 0, yb, apo, f.fonte_display, "start", 0.04))
                continue
            if col_bordas:
                x = x0 + (0 if j == 0 else (col * cel - gap) if j >= col else j * cel - gap / 2)
                anc = "start" if j == 0 else "end" if j >= col else "middle"
            else:
                x, anc = x0 + j * cel + (cel - gap) / 2, "middle"
            o.append(R(f, s, x, yb, apo, f.fonte_mono, anc, 0.02))
        ytop = yb - LER
    if titulo:
        partes = [(titulo, ink)] if isinstance(titulo, str) else titulo
        x = 0.0
        for s, cor in partes:
            o.append(R(f, s, x, ytop - u * 0.9, cor, f.fonte_display, tr=0.04))
            x += RW(f, s, f.fonte_display) + u * 0.4
    return "".join(o)


def calendario(f, ano=2026, mes=11, destaques=(27,), marcados=(), rotulo=True):
    """Calendário real do mês (semana começando no domingo; dias do `calendar`), números legíveis centrados na
    célula (raio 0: grade de dado), destaque no acento (ex.: Black Friday 27/11/2026)."""
    ink, apo, ac = f.tinta, f.apoio, f.acento
    u = f.unidade
    c = calendar.Calendar(firstweekday=6)
    semanas = c.monthdayscalendar(ano, mes)
    cel, gap = 56.0, 6.0
    o = []
    for j, d in enumerate("DSTQQSS"):
        o.append(R(f, d, j * cel + (cel - gap) / 2, -u * 0.5, apo, f.fonte_display, "middle", 0))
    for i, sem in enumerate(semanas):
        for j, d in enumerate(sem):
            if not d:
                continue
            x, y = j * cel, i * cel
            dest, marc = d in destaques, d in marcados
            fill = ac if dest else (mistura(f.fundo, ink, 0.28) if marc else mistura(f.fundo, ink, 0.09))
            o.append(f'<path d="{ret(x, y, cel - gap, cel - gap, 0)}" fill="{fill}"/>')
            o.append(RC(f, str(d), x + (cel - gap) / 2, y + (cel - gap) / 2,
                        f.sobre_acento if dest else (ink if marc else mistura(f.fundo, ink, 0.7)), f.fonte_display, 0))
    if rotulo:
        nomes = ["", "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO",
                 "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
        o.append(R(f, f"{nomes[mes]} {ano}", 0, -u * 0.5 - LER - u * 0.75, ink, f.fonte_texto, tr=0.06))
    return justo("".join(o), f"calendário {mes:02d}/{ano}" + (f" · destaque {', '.join(map(str, destaques))}" if destaques else ""),
                 "calendário verdadeiro (calendar do Python); destaque = data real (27/11/2026 Black Friday; 15/03 Dia "
                 "do Consumidor) · agenda, contagem")


def legenda_rampa(f, niveis=5, sw=40.0, menos="MENOS", mais="MAIS"):
    """Legenda da rampa: MENOS ▢▢▢▢▢ MAIS — acompanha qualquer heatmap de dado real."""
    u = f.unidade
    g = 6.0
    o = [R(f, menos, 0, sw / 2 + LER / 2, f.apoio, f.fonte_display, tr=0.04)]
    x = RW(f, menos, f.fonte_display) + u * 0.6
    for k in range(niveis):
        o.append(f'<path d="{ret(x, 0, sw, sw, 0)}" fill="{_nivel(f, k / (niveis - 1))}"/>')
        x += sw + g
    o.append(R(f, mais, x - g + u * 0.6, sw / 2 + LER / 2, f.apoio, f.fonte_display, tr=0.04))
    return justo("".join(o), f"heatmap · legenda {niveis} níveis (menos → mais)",
                 "legenda dos níveis da rampa — acompanha qualquer heatmap de dado real")


@amostra(FAM, "heatmap e calendário")
def _a_heat(f):
    u = f.unidade
    tab = [[1.0 if s < 20 else 0.0 for s in range(30)] for _ in range(8)]
    e1 = justo(heatmap(f, tab, cel=14.0, gap=2.0, rot_col={0: "0", 20: "20", 30: "30 s"}, col_bordas=True,
                       titulo="TABATA · 8 × 30 s", niveis=2),
               "heatmap · protocolo Tabata 8 × 30 s", "o próprio protocolo como dado (1 célula = 1 s; aceso = 20 s de "
               "esforço, apagado = 10 s de pausa; 8 linhas = 8 rodadas) · textura técnica, fundo")
    semanas = 12
    esq = [[0.75 if d in (1, 3, 5) else 0.0 for d in range(7)] for _ in range(semanas)]
    esq_t = [list(r) for r in zip(*esq)]
    e2 = justo(heatmap(f, esq_t, cel=32.0, gap=5.0, rot_lin=list("DSTQQSS"), rot_col={0: "SEMANAS 1–12"}, col_esq=True,
                       titulo=[("ESQUEMA", f.acento), ("3× POR SEMANA", f.tinta)], niveis=5),
               "heatmap · frequência (esquema)", "esquema rotulado (seg-qua-sex, 12 semanas); com dado real da turma "
               "vira mapa de frequência · fundo, prova")
    return [calendario(f), calendario(f, 2027, 3, destaques=(15,)), e1, e2, legenda_rampa(f)]


# ================================================================ pague 1, leve 2
def _seta(f, x0, x1, y, cor):
    t, u = f.traco, f.unidade
    c = u * 0.45
    return (_p(f"M{x0:.2f} {y:.2f}H{x1 - t:.2f}", stroke=cor, sw=t * 1.2, extra='stroke-linecap="round"')
            + _p(f"M{x1 - c:.2f} {y - c:.2f}L{x1:.2f} {y:.2f}L{x1 - c:.2f} {y + c:.2f}", stroke=cor, sw=t * 1.2,
                 extra='stroke-linecap="round" stroke-linejoin="round"'))


def pilha_1_2(f, modo="blocos", pague="PAGUE 1", leve="LEVE 2"):
    """Oferta "pague 1, leve 2" (condição de oferta) como DIAGRAMA (Isotype: figuras do mesmo tamanho, base
    comum; seta = 'paga isto → leva isto'). modo: blocos | pontos | cartoes | barras."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    o = []
    D = f.fonte_display
    if modo in ("blocos", "pontos"):
        s, gap = u * 4.0, u * 0.5
        forma = (lambda x, y, c: f'<path d="{ret(x, y, s, s, f.raio)}" fill="{c}"/>') if modo == "blocos" else \
                (lambda x, y, c: f'<circle cx="{x + s / 2:.2f}" cy="{y + s / 2:.2f}" r="{s / 2:.2f}" fill="{c}"/>')
        o.append(forma(0, s + gap, ink))
        x2 = s + u * 4.0
        o.append(_seta(f, s + u * 0.9, x2 - u * 0.9, s + gap + s / 2, apo))
        o.append(forma(x2, 0, ac))
        o.append(forma(x2, s + gap, ac))
        yb = 2 * s + gap + u * 0.6 + LER
        o.append(R(f, pague, s / 2, yb, ink, D, "middle"))
        o.append(R(f, leve, x2 + s / 2, yb, ac, D, "middle"))
    elif modo == "cartoes":
        cw, ch = u * 4.2, u * 5.6
        o.append(f'<path d="{ret(t / 2, t / 2, cw - t, ch - t, f.raio - t / 2)}" fill="none" stroke="{ink}" stroke-width="{t:.2f}"/>')
        o.append(RC(f, "1", cw / 2, ch / 2, ink, D, 0, cap_px=u * 2.1))
        x2 = cw + u * 3.6
        o.append(_seta(f, cw + u * 0.8, x2 - u * 0.6, ch / 2, apo))
        o.append(f'<g transform="rotate(-6 {x2 + cw / 2:.2f} {ch:.2f})"><path d="{ret(x2, 0, cw, ch, f.raio)}" fill="{mistura(f.fundo, ac, 0.45)}"/></g>')
        o.append(f'<g transform="rotate(5 {x2 + u * 0.9 + cw / 2:.2f} {ch:.2f})"><path d="{ret(x2 + u * 0.9, 0, cw, ch, f.raio)}" fill="{ac}"/>'
                 + RC(f, "2", x2 + u * 0.9 + cw / 2, ch / 2, f.sobre_acento, D, 0, cap_px=u * 2.1) + "</g>")
        yb = ch + u * 1.0 + LER
        o.append(R(f, pague, cw / 2, yb, ink, D, "middle"))
        o.append(R(f, leve, x2 + u * 0.45 + cw / 2, yb, ac, D, "middle"))
    else:   # barras
        w1, h = u * 7, u * 1.4
        g = u * 0.25
        o.append(f'<path d="{ret(0, 0, w1, h, 0)}" fill="{ink}"/>')
        o.append(f'<path d="{ret(0, h + u * 0.9, w1, h, 0)}" fill="{ac}"/>')
        o.append(f'<path d="{ret(w1 + g, h + u * 0.9, w1, h, 0)}" fill="{ac}"/>')
        o.append(R(f, pague, -u * 0.6, h / 2 + LER / 2, ink, D, "end"))
        o.append(R(f, leve, -u * 0.6, h * 1.5 + u * 0.9 + LER / 2, ac, D, "end"))
    return justo("".join(o), f"pague 1 leve 2 · {modo}", "a oferta pague 1, leve 2 como diagrama de "
                 "mesma escala (Isotype) · explicar a oferta sem texto longo, anúncio, página de preço")


@amostra(FAM, "pague 1 leve 2")
def _a_pilha(f):
    return [pilha_1_2(f), pilha_1_2(f, "pontos"), pilha_1_2(f, "cartoes"), pilha_1_2(f, "barras")]


# ================================================================ curvas esquemáticas (rotuladas)
def _eixos(f, w, h, rx, ry, o):
    t, ink, apo = f.traco, f.tinta, f.apoio
    u = f.unidade
    o.append(_p(f"M0 {-h:.2f}V0H{w:.2f}", stroke=ink, sw=t * 0.6, extra='stroke-linejoin="round"'))
    o.append(f'<path d="{poligono([(0, -h - u * 0.4), (-u * 0.18, -h), (u * 0.18, -h)])}" fill="{ink}"/>')
    o.append(f'<path d="{poligono([(w + u * 0.4, 0), (w, -u * 0.18), (w, u * 0.18)])}" fill="{ink}"/>')
    o.append(R(f, rx, w + u * 0.4, u * 0.6 + LER, apo, f.fonte_display, "end"))
    o.append(R(f, ry, u * 0.6, -h - u * 0.4 + LER, apo, f.fonte_display))


def curva(f, tipo="hill", w=400.0, h=230.0):
    """Curvas do assunto como ESQUEMA (a palavra 'ESQUEMA' vai desenhada, legível): hill (força × velocidade,
    hipérbole, + potência tracejada), lactato (guias em 2 e 4 mmol/L), forca (força vertical ao andar, "M" ~1,1 ×
    peso), emg (bruto → retificado → envelope). Com dado real de teste, passe os pontos e tire o rótulo."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    D = f.fonte_display
    o = []
    topo_rot = -h - u * 0.4 + LER        # linha de base dos rótulos de cima (eixo y e ESQUEMA)
    if tipo == "hill":
        _eixos(f, w, h, "VELOCIDADE", "FORÇA", o)
        a = 0.25
        pts = []
        for i in range(101):
            F = 1 - i / 100
            v = (a * (1 - F)) / (F + a)        # (F + a)(v + b) = b(F0 + a), com F0 = 1, b = a·v0, v0 = 1
            pts.append((v * w * 0.92, -F * h * 0.82))
        o.append(_p(polilinha(pts), stroke=ac, sw=t, extra='stroke-linecap="round"'))
        pot = [(x, -(-y / (h * 0.82)) * (x / (w * 0.92)) * h * 0.82 * 3.2) for x, y in pts]
        o.append(_p(polilinha(pot), stroke=ink, sw=t * 0.6, extra='stroke-dasharray="5 4"'))
        xl, yl = w * 0.46, -h * 0.5
        o.append(_p(f"M{xl:.2f} {yl - LER / 2:.2f}h{u * 1.4:.2f}", stroke=ink, sw=t * 0.6, extra='stroke-dasharray="5 4"'))
        o.append(R(f, "POTÊNCIA", xl + u * 1.4 + u * 0.4, yl, ink, D))
        nome = "curva força × velocidade (Hill)"
    elif tipo == "lactato":
        _eixos(f, w, h, "INTENSIDADE", "LACTATO", o)
        ymax = 8.0
        Y = lambda mm: -mm / ymax * h  # noqa: E731
        for g in (2, 4):
            o.append(_p(f"M0 {Y(g):.2f}H{w:.2f}", stroke=apo, sw=t * 0.5, extra='stroke-dasharray="4 4"'))
            o.append(R(f, f"{g} mmol/L", u * 0.6, Y(g) - u * 0.45, apo, D))
        pts = [(w * (0.08 + 0.13 * i), Y(1.0 + 0.12 * math.exp(0.62 * i))) for i in range(7)]
        o.append(_p(suave(pts, tensao=0.5), stroke=ac, sw=t, extra='stroke-linecap="round"'))
        for x, y in pts:
            o.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{t * 1.3:.2f}" fill="{ac}"/>')
        nome = "curva de lactato (esquema)"
    elif tipo == "forca":
        _eixos(f, w, h, "% DO APOIO", "× PESO CORPORAL", o)
        Y = lambda k: -k / 1.5 * h  # noqa: E731
        o.append(_p(f"M0 {Y(1.0):.2f}H{w:.2f}", stroke=apo, sw=t * 0.5, extra='stroke-dasharray="4 4"'))
        o.append(R(f, "1,0", -u * 0.45, Y(1.0) + LER / 2, apo, f.fonte_mono, "end", 0))
        ks = [0, 0.55, 1.05, 1.12, 0.95, 0.78, 0.8, 0.98, 1.1, 1.02, 0.6, 0]
        pts = [(w * 0.92 * i / (len(ks) - 1), Y(k)) for i, k in enumerate(ks)]
        o.append(_p(suave(pts, tensao=0.55), stroke=ac, sw=t, extra='stroke-linecap="round"'))
        nome = "força vertical ao andar (esquema)"
    else:   # emg: 3 faixas (rótulo em cima, sinal embaixo — nunca um sobre o outro)
        h = max(h, 300.0)
        r = semente(f, "emg")
        n = 220
        lh = h / 3
        faixa = LER + u * 0.5           # altura da faixa do rótulo
        env = [math.exp(-((i - n * 0.5) / (n * 0.17)) ** 2) * 0.9 + 0.08 for i in range(n)]
        bruto = [env[i] * r.uniform(-1, 1) for i in range(n)]
        mb = max(abs(b) for b in bruto)
        jan = 22
        ret_ = [abs(b) for b in bruto]
        sm = [sum(ret_[max(0, i - jan):i + jan]) / len(ret_[max(0, i - jan):i + jan]) for i in range(n)]
        ms = max(sm)
        for nome_l, k in (("BRUTO", 0), ("RETIFICADO", 1), ("ENVELOPE", 2)):
            y0 = k * lh
            o.append(R(f, nome_l, 0, y0 + LER, apo, D))
            sig0, sig1 = y0 + faixa + u * 0.2, y0 + lh - u * 0.3     # área do sinal
            if k == 0:
                yb = (sig0 + sig1) / 2
                amp = (sig1 - sig0) / 2
                o.append(_p(f"M0 {yb:.2f}H{w:.2f}", stroke=apo, sw=t * 0.35))
                o.append(_p(polilinha([(w * i / (n - 1), yb - bruto[i] / mb * amp) for i in range(n)]), stroke=ink, sw=t * 0.35))
            else:
                yb, amp = sig1, sig1 - sig0
                o.append(_p(f"M0 {yb:.2f}H{w:.2f}", stroke=apo, sw=t * 0.35))
                if k == 1:
                    o.append(_p(polilinha([(w * i / (n - 1), yb - ret_[i] / mb * amp) for i in range(n)]), stroke=ink, sw=t * 0.35))
                else:
                    pts = [(w * i / (n - 1), yb - sm[i] / ms * amp * 0.9) for i in range(0, n, 2)]
                    o.append(_p(suave(pts, tensao=0.5), stroke=ac, sw=t, extra='stroke-linecap="round"'))
        topo_rot = LER
        nome = "EMG: bruto → retificado → envelope (esquema)"
    o.append(R(f, "ESQUEMA", w + (u * 0.4 if tipo != "emg" else 0), topo_rot, ac, D, "end", 0.08))
    return justo("".join(o), nome, "forma certa da curva (hipérbole, guias 2/4, 'M', envelope); SEM dado real → "
                 "rotulada ESQUEMA · conteúdo de fisiologia, divisor-onda")


@amostra(FAM, "curvas esquemáticas")
def _a_curvas(f):
    return [curva(f, "hill"), curva(f, "lactato"), curva(f, "forca"), curva(f, "emg")]


# ================================================================ tabela minimalista
def tabela(f, linhas, cabecalho=None, alinhar=None, titulo=None, w=None, cores=None, destaque=None, fontes=None,
           vaos=None):
    """Tabela com fios finos (raio 0), ≤ 6 linhas, TUDO legível (maiúscula ≥ 25,6 px). alinhar = 'l'/'r' por
    coluna (número à direita, pela tinta); fontes = 'M' (mono, número tabular) | 'D' (display) | 'T' (texto) por
    coluna; cores = disco de cor por linha (anilha: cor IWF) antes da 1ª coluna; destaque = linha no acento.
    Largura = conteúdo + vãos ≥ 1 U (ou w, se maior). vaos = vão ANTES de cada coluna a partir da 2ª (None = 1 U e
    elástico): unidade colada ao número ("20" "s") usa vão curto fixo; o excedente vai só para os vãos elásticos."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    nc = len(linhas[0])
    alinhar = alinhar or (["l"] + ["r"] * (nc - 1))
    fontes = fontes or (["D"] + ["M"] * (nc - 1))
    spec = {"M": f.fonte_mono, "D": f.fonte_display, "T": f.fonte_texto}
    tr = {"M": 0.0, "D": 0.04, "T": 0.04}
    larg = []
    for j in range(nc):
        ws = [RW(f, str(r[j]), spec[fontes[j]], tr[fontes[j]]) for r in linhas]
        if cabecalho:
            ws.append(RW(f, cabecalho[j], f.fonte_display))
        larg.append(max(ws))
    rr = LER * 0.42
    sw = (2 * rr + u * 0.5) if cores else 0
    vao = u * 1.0
    vaos = list(vaos) if vaos else [None] * (nc - 1)
    base = [vao if v is None else v for v in vaos]
    W = max(w or 0, sw + sum(larg) + sum(base))
    elast = [k for k, v in enumerate(vaos) if v is None] or list(range(nc - 1))
    sobra = W - sw - sum(larg) - sum(base)
    gaps = [b + (sobra / len(elast) if k in elast else 0.0) for k, b in enumerate(base)]
    xs, x = [], sw
    for j in range(nc):
        xs.append(x)
        x += larg[j] + (gaps[j] if j < nc - 1 else 0.0)
    o = []
    y = 0.0
    if titulo:
        o.append(R(f, titulo, 0, y + LER, ink, f.fonte_display, tr=0.06))
        y += LER + u * 0.9
    lh = LER * 2.0
    if cabecalho:
        for j, c in enumerate(cabecalho):
            xx = xs[j] + (larg[j] if alinhar[j] == "r" else 0)
            o.append(R(f, c, xx, y + LER, apo, f.fonte_display, "end" if alinhar[j] == "r" else "start", 0.04))
        y += LER + u * 0.5
        o.append(_p(f"M0 {y:.2f}H{W:.2f}", stroke=ink, sw=t * 0.6))
    for i, r in enumerate(linhas):
        base = y + lh / 2 + LER / 2
        cor = ac if destaque == i else ink
        if cores:
            o.append(f'<circle cx="{rr:.2f}" cy="{y + lh / 2:.2f}" r="{rr:.2f}" fill="{cores[i]}"/>')
        for j, c in enumerate(r):
            if str(c) == "":
                continue
            xx = xs[j] + (larg[j] if alinhar[j] == "r" else 0)
            o.append(R(f, str(c), xx, base, cor, spec[fontes[j]], "end" if alinhar[j] == "r" else "start", tr[fontes[j]]))
        y += lh
        if i < len(linhas) - 1:
            o.append(_p(f"M0 {y:.2f}H{W:.2f}", stroke=apo, sw=t * 0.35, extra='stroke-opacity="0.7"'))
    return justo("".join(o), "tabela · " + (titulo or "dados").lower(),
                 "≤ 6 linhas, fios finos, algarismos alinhados pela tinta; só dado verdadeiro · ficha técnica, prova, site")


@amostra(FAM, "tabela")
def _a_tabela(f):
    zon = [[z, f"{a}–{b}%", nm] for a, b, z, nm in ZONAS]
    ani = [[num(k), str(DISCO[k][0])] for k in (25, 20, 15, 10, 5)]
    return [tabela(f, zon, ["ZONA", "% FC MÁX", "INTENSIDADE"], ["l", "r", "r"], "ZONAS DE FREQUÊNCIA CARDÍACA",
                   destaque=3, fontes=["D", "M", "D"]),
            tabela(f, ani, ["CARGA (kg)", "DIÂMETRO (mm)"], ["r", "r"], "ANILHAS IWF · COMPETIÇÃO",
                   cores=[IWF[k] for k in (25, 20, 15, 10, 5)], fontes=["M", "M"]),
            tabela(f, [["ESFORÇO", "20", "s"], ["PAUSA", "10", "s"], ["RODADAS", "8", ""], ["TOTAL", "4", "min"]], None,
                   ["l", "r", "l"], "PROTOCOLO TABATA", fontes=["D", "M", "M"], w=300, vaos=[None, 12.0])]


# ================================================================ ícones de status (sinal, bateria, ao vivo)
def status(f, tipo="sinal", valor=3, total=4, rotulo=None, escala=1.0):
    """Ícones de interface com FUNÇÃO: sinal (barras = força), bateria (segmentos = noites que faltam), rec (ponto +
    rótulo; ponto = 0,84 × a maiúscula, elementos.md). valor = parâmetro. Rótulo com maiúscula ≥ 25,6 px."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade * escala
    o = []
    apag = mistura(f.fundo, ink, 0.22)
    if tipo == "sinal":
        bw, gap = u * 0.5, u * 0.25
        for i in range(total):
            h = u * (0.6 + 0.55 * i)
            o.append(f'<path d="{ret(i * (bw + gap), u * 2.3 - h, bw, h, 0)}" fill="{ink if i < valor else apag}"/>')
        x, hy = total * (bw + gap) + u * 0.3, u * 2.3
    elif tipo == "bateria":
        bw, bh = u * 3.6, u * 1.7
        rs = f.raio_sm
        o.append(f'<path d="{ret(t / 2, t / 2, bw - t, bh - t, rs - t / 2)}" fill="none" stroke="{ink}" stroke-width="{t:.2f}"/>')
        o.append(f'<path d="{ret(bw + t * 0.6, bh * 0.3, u * 0.28, bh * 0.4, 0, (0, u * 0.14, u * 0.14, 0))}" fill="{ink}"/>')
        pad = t * 1.9
        ri = max(0.0, rs - pad)              # aninhado: interno = externo − espaço (forma.md §6)
        sw = (bw - 2 * pad - (total - 1) * t) / total
        for i in range(total):
            x = pad + i * (sw + t)
            cs = (ri if i == 0 else 0, ri if i == total - 1 else 0, ri if i == total - 1 else 0, ri if i == 0 else 0)
            o.append(f'<path d="{ret(x, pad, sw, bh - 2 * pad, 0, cs)}" fill="{(ac if valor <= 1 else ink) if i < valor else apag}"/>')
        x, hy = bw + u * 0.9, bh
    else:
        r = 0.84 * LER / 2
        o.append(f'<circle cx="{r:.2f}" cy="0" r="{r:.2f}" fill="{ac}"/>')
        lab = rotulo or "REC"
        o.append(R(f, lab, 2 * r + u * 0.45, LER / 2, ink, f.fonte_mono, tr=0.02))
        rotulo = None
        x = hy = 0
    if rotulo:
        o.append(R(f, rotulo, x, hy / 2 + LER / 2, ink, f.fonte_mono, tr=0.02))
    nome = f"status · {tipo}" + (f" · {valor}/{total}" if tipo != "rec" else "") + (f" · {rotulo}" if rotulo else "")
    if tipo == "rec":
        nome = f"status · rec · {lab}"
    return justo("".join(o), nome, "ícone com função (bateria = noites que faltam, sinal = força, rec/ao vivo = "
                 "transmitindo) · ≤ 3 por peça, barra de câmera")


@amostra(FAM, "status")
def _a_status(f):
    return [status(f, "sinal", 4, 4), status(f, "bateria", 3, 3, rotulo="3 NOITES"),
            status(f, "bateria", 1, 3, rotulo="ÚLTIMA NOITE"), status(f, "rec"), status(f, "rec", rotulo="AO VIVO · 20H30")]
