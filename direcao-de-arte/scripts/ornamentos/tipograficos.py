"""ornamentos.tipograficos — família "texto como elemento": texto no caminho (círculo, arco, espiral, onda) com
espaçamento ÓPTICO, palavra em eco (opacidade · contorno empilhado), bloco justificado, numeral (contorno, linha dupla,
extrusão, tracejado), rótulo vertical (lombada) e datador.

Regras (references/elementos.md, tipografia.md; pesquisa 11 E37–E53): só palavras do cliente ou neutras (AO VIVO,
BLACK FRIDAY, NOITE 1, 20H30, PÓS-GRADUAÇÃO, NOME DA MARCA); texto SEMPRE em curvas; 1 deformação com regra
por peça (eco ou caminho — nunca as duas).

Revisão um a um (_revisao/tipograficos.md) — REMOVIDOS de propósito, não recriar:
  - palavra fatiada (horizontal, diagonal, vertical, fresta): parece erro de render; a fresta com barra lê "cancelado";
  - eco que SOBREPÕE cópias (contorno atrás, zoom, rastro): os contornos cruzam as letras e embolam;
  - numeral "sombra" em fio deslocado: o fio aparece por dentro do numeral → virou EXTRUSÃO sólida (união exata).
Medidas sempre na TINTA (acento e cedilha contam); fio a ≥ 0,5 U da letra; raios só da escala (0 · sm · md · lg).

Espaçamento óptico no caminho: numa curva, o topo das letras abre (texto por fora) ou fecha (texto por dentro). Cada
avanço é corrigido pela curvatura no meio da letra: a' = a / (1 + κ·h), h = meia altura da maiúscula, κ com sinal
(positivo quando o centro da curva fica ABAIXO da letra). No anel fechado, a sobra é distribuída por igual (o anel
fecha sem buraco nem encavalamento).
"""
import math

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

from .nucleo import amostra, cap, ret, _font
from .assunto import justo, mistura, polar, rot, _p, circ

FAM = "tipograficos"


# ================================================================ texto em caminho com espaçamento óptico
class _Caminho:
    """Polilinha densa com comprimento acumulado, ponto/ângulo/curvatura por comprimento de arco."""

    def __init__(self, pts, fechado=False):
        if fechado:
            pts = list(pts) + [pts[0]]
        self.p = pts
        self.s = [0.0]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            self.s.append(self.s[-1] + math.hypot(x1 - x0, y1 - y0))
        self.L = self.s[-1]
        self.fechado = fechado

    def _idx(self, s):
        if self.fechado:
            s %= self.L
        s = max(0.0, min(self.L - 1e-9, s))
        lo, hi = 0, len(self.s) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.s[m] <= s:
                lo = m
            else:
                hi = m
        return lo, s

    def ponto(self, s):
        i, s = self._idx(s)
        (x0, y0), (x1, y1) = self.p[i], self.p[i + 1]
        seg = self.s[i + 1] - self.s[i] or 1e-9
        k = (s - self.s[i]) / seg
        return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, math.atan2(y1 - y0, x1 - x0)

    def curvatura(self, s, ds=3.0):
        """κ com sinal: + quando o centro da curva fica abaixo da letra (texto por fora)."""
        _, _, a0 = self.ponto(s - ds)
        _, _, a1 = self.ponto(s + ds)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        return da / (2 * ds)      # giro horário (tela) = centro "abaixo" do vetor para cima (s, −c)


def texto_no_caminho(spec, s, size, cam, fill, inicio=0.0, tracking=0.0, otico=True, centro=False, encher=False,
                     sep=" · "):
    """Coloca o texto ao longo de `cam` (_Caminho). encher=True (caminho fechado): repete s+sep até fechar o anel e
    distribui a sobra por igual. Devolve (svg, comprimento usado)."""
    fo = _font(spec)
    if encher:   # n repetições inteiras; o corpo ajusta (±) para fechar o anel sem abrir o espaçamento
        unid = s + sep
        w1 = fo.width(unid, size, tracking)
        n = max(1, round(cam.L / w1))
        size *= cam.L / (n * w1) * 0.985
        s = unid * n
    names, adv = fo.advances(s, size, tracking)
    h = fo.cap * size / 2
    k = size / fo.upm
    # avanços ópticos (1ª passada usa a posição aproximada)
    pos = inicio
    adv2 = []
    for a in adv:
        kap = cam.curvatura(pos + a / 2) if otico else 0.0
        adv2.append(a / max(0.4, 1 + kap * h))
        pos += adv2[-1]
    total = sum(adv2)
    if encher:
        extra = (cam.L - total) / len(adv2)
        adv2 = [a + extra for a in adv2]
        total = cam.L
    if centro:
        inicio = inicio - total / 2
    pen = SVGPathPen(fo.gs)
    pos = inicio
    for g, a, a0 in zip(names, adv2, adv):
        x, y, ang = cam.ponto(pos + a / 2)
        c, sn = math.cos(ang), math.sin(ang)
        ox = -a0 / 2
        fo.gs[g].draw(TransformPen(pen, (k * c, k * sn, k * sn, -k * c, x + ox * c, y + ox * sn)))
        pos += a
    return f'<path d="{pen.getCommands()}" fill="{fill}"/>', total


def _circulo(R, a0=-90.0, n=720, horario=True):
    return [polar(0, 0, R, a0 + (360 * i / n) * (1 if horario else -1)) for i in range(n)]


def anel_texto(f, txt="NOME DA MARCA", R=150.0, sep=" · ", corpo=None, duplo=False, otico=True, spec=None,
               cor=None):
    """Texto que fecha o anel (repete com separador e distribui a sobra). duplo = 2º anel interno no sentido
    contrário com outra palavra. spec/cor = fonte e cor do anel (padrão: texto da ficha na tinta)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    sp = spec or f.fonte_texto
    sz = corpo or R * 0.13
    cam = _Caminho(_circulo(R), fechado=True)
    svg, _ = texto_no_caminho(sp, txt, sz, cam, cor or ink, tracking=0.12 if sp != f.fonte_display else 0.05,
                              otico=otico, encher=True, sep=sep)
    o = [svg]
    if duplo:
        R2 = R - sz * 1.9
        cam2 = _Caminho(_circulo(R2, 90, horario=True), fechado=True)
        s2, _ = texto_no_caminho(f.fonte_mono, "AO VIVO", sz * 0.8, cam2, ac, tracking=0.2, otico=otico, encher=True,
                                 sep=" ● ")
        o.append(s2)
        o.append(_p(circ(0, 0, R - sz * 0.55), stroke=apo, sw=t * 0.4, extra='stroke-opacity="0.6"'))
    return justo("".join(o), "anel de texto" + (" · duplo" if duplo else "") + (" · display" if sp == f.fonte_display else ""),
                 "texto fecha o anel com espaço igual (sobra distribuída) e correção óptica · selo, moldura de foto, "
                 "carregamento que gira")


def arco_texto(f, txt="AO VIVO", R=125.0, lado="cima", abertura=None, corpo=None, cor=None):
    """Texto num arco: cima (lê por fora, horário) ou baixo (lê da esquerda para a direita por dentro)."""
    ink = cor or f.tinta
    sz = corpo or R * 0.4
    if lado == "cima":
        cam = _Caminho([polar(0, 0, R, a) for a in [180 + i * 0.25 for i in range(721)]])
        meio = cam.L / 2
    else:
        cam = _Caminho([polar(0, 0, R, a) for a in [180 - i * 0.25 for i in range(721)]])
        meio = cam.L / 2
    svg, _ = texto_no_caminho(f.fonte_display, txt, sz, cam, ink, inicio=meio, tracking=0.06, centro=True)
    return justo(svg, f"arco de texto · {lado} · {txt}", "palavra curta num arco, centrada e com correção óptica "
                 "(por dentro abre, por fora fecha) · selo, chamada sobre foto, topo de moldura")


def espiral_texto(f, txt="NOITE 1 · NOITE 2 · NOITE 3 · BLACK FRIDAY · ", voltas=3.2, R=170.0, passo=None, corpo=None):
    """Texto em espiral de Arquimedes, de fora para dentro, lendo no sentido horário; o corpo diminui com o raio
    (mantém a proporção letra/curvatura)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    sz0 = corpo or R * 0.11
    passo = passo or sz0 * 1.45
    o = []
    pts = []
    n = int(voltas * 360)
    for i in range(n):
        th = i
        r = R - passo * i / 360
        if r < R * 0.18:
            break
        pts.append(polar(0, 0, r, -90 + th))
    cam = _Caminho(pts)
    fo = _font(f.fonte_texto)
    s = txt * 6
    names, adv = fo.advances(s, sz0, 0.1)
    pen = SVGPathPen(fo.gs)
    pos = 0.0
    postos = []                      # (glifo, matriz) — desenha só até o fim da última frase INTEIRA
    for g, a in zip(names, adv):
        if pos + a > cam.L:
            break
        x, y, ang = cam.ponto(pos + a / 2)
        r = math.hypot(x, y)
        esc = max(0.45, r / R)
        k = sz0 * esc / fo.upm
        aa = a * esc
        kap = cam.curvatura(pos + aa / 2)
        aa = aa / (1 + kap * fo.cap * sz0 * esc / 2)
        x, y, ang = cam.ponto(pos + aa / 2)
        c, sn = math.cos(ang), math.sin(ang)
        ox = -a * esc / 2
        postos.append((g, (k * c, k * sn, k * sn, -k * c, x + ox * c, y + ox * sn)))
        pos += aa
    fins = [i for i in range(len(postos)) if s[i] not in " ·" and s[i + 1:i + 3] in (" ·", "")]
    corte = fins[-1] + 1 if fins else len(postos)      # nunca termina em "·" nem em palavra cortada
    for g, m in postos[:corte]:
        fo.gs[g].draw(TransformPen(pen, m))
    o.append(f'<path d="{pen.getCommands()}" fill="{ink}"/>')
    o.append(f'<circle r="{t * 1.6:.2f}" fill="{ac}"/>')
    return justo("".join(o), "espiral de texto", "espiral de Arquimedes com corpo proporcional ao raio · fundo de capa, "
                 "carregamento, 'as 3 noites' girando")


def onda_texto(f, txt="BLACK FRIDAY · AO VIVO · ", w=460.0, amp=None, periodos=1.0, corpo=None):
    """Texto numa onda (seno) com correção óptica nas cristas e vales."""
    ink = f.tinta
    sz = corpo or 38.0
    amp = amp or sz * 0.55
    pts = [(w * i / 600, -amp * math.sin(2 * math.pi * periodos * i / 600)) for i in range(601)]
    cam = _Caminho(pts)
    fo = _font(f.fonte_display)
    frase = txt.strip(" ·")
    unid = frase + " · "
    n = max(1, int((cam.L * 0.97 + fo.width(" · ", sz, 0.04)) / fo.width(unid, sz, 0.04)))
    s_ = (unid * n)[: -len(" · ")]
    svg, _ = texto_no_caminho(f.fonte_display, s_, sz, cam, ink, inicio=cam.L / 2, tracking=0.04, centro=True)
    return justo(svg, "onda de texto", "frase curta repetida inteira numa onda, com correção óptica · faixa animável, "
                 "divisor de seção")


@amostra(FAM, "texto no caminho")
def _a_caminho(f):
    return [anel_texto(f), anel_texto(f, "BLACK FRIDAY", 140, duplo=True),
            anel_texto(f, "PÓS-GRADUAÇÃO", 120, corpo=120 * 0.2, spec=f.fonte_display, cor=f.acento),
            arco_texto(f), arco_texto(f, "20H30", lado="baixo", cor=f.acento), espiral_texto(f), onda_texto(f)]


# ================================================================ palavra em eco
def _d(spec, s, size, x, base, tracking=0.0):
    return _font(spec).path(s, size, x, base, tracking)


def eco(f, palavra="AO VIVO", n=5, modo="opacidade", corpo=110.0):
    """Palavra repetida em PILHA — as cópias nunca se sobrepõem (passo = 1,14 × maiúscula, vão medido na tinta).
    opacidade = cópias de cima somem (0,12 → 1), a de baixo no acento; contorno = cópias só no fio, a de baixo cheia.
    (Eco com cópias SOBREPOSTAS — contorno atrás, zoom, rastro — foi removido: os fios cruzam as letras e embolam.)"""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    sp = f.fonte_display
    xa, xb, ya, yb = _caixa_txt(sp, palavra, corpo, 0.02)
    passo = (yb - ya) * 1.14                      # altura da TINTA + 14% de vão: as linhas nunca se tocam
    o = []
    for i in range(n):
        d = _d(sp, palavra, corpo, 0, i * passo, 0.02)
        if i == n - 1:
            o.append(f'<path d="{d}" fill="{ac}"/>')
        elif modo == "opacidade":
            o.append(f'<path d="{d}" fill="{ink}" fill-opacity="{0.12 + 0.6 * i / (n - 1):.2f}"/>')
        else:   # contorno empilhado (fio por dentro do desenho: o vão entre linhas continua o mesmo)
            o.append(f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{t * 0.6:.2f}" stroke-linejoin="round" '
                     f'stroke-opacity="{0.35 + 0.55 * i / (n - 1):.2f}"/>')
    return justo("".join(o), f"eco · {modo} · {palavra}", "repetição empilhada sem sobrepor (vão de 14% medido na "
                 "tinta) · título que 'ecoa' a transmissão, 1 por peça")


@amostra(FAM, "eco")
def _a_eco(f):
    return [eco(f, "AO VIVO", 4, "opacidade", 88), eco(f, "BLACK", 4, "contorno", 96)]


# ================================================================ bloco justificado
def bloco(f, linhas=("BLACK", "FRIDAY", "AO VIVO", "3 NOITES"), w=280.0, acento=None, fios=False, entre=None,
          legenda=None):
    """Palavras empilhadas, cada uma no corpo que preenche a mesma largura (justificado pela tinta). acento = índice
    da linha no acento; fios = fio fino entre as linhas; legenda = linha mono pequena no pé."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    sp = f.fonte_display
    fo = _font(sp)
    entre = entre if entre is not None else w * 0.025
    if fios:   # fio no meio do vão, com folga ≥ 0,5 U da TINTA de cima e de baixo (nunca encostar na letra)
        entre = max(entre, 2 * f.unidade * 0.5 + t * 0.5)
    o = []
    y = 0.0
    for i, ln in enumerate(linhas):
        # corpo que dá a largura w NA TINTA (sem as laterais do 1º/último glifo)
        xa, xb, _, _ = _caixa_txt(sp, ln, 100.0, 0.01)
        sz = 100.0 * w / (xb - xa)
        xa, xb, ya, yb = _caixa_txt(sp, ln, sz, 0.01)
        d = fo.path(ln, sz, 0, 0, 0.01)
        y += (-ya) if i == 0 else (-ya + entre)
        o.append(f'<path d="{d}" fill="{ac if i == acento else ink}" transform="translate({-xa:.2f} {y:.2f})"/>')
        y_fim = y + yb
        if fios and i < len(linhas) - 1:
            o.append(_p(f"M0 {y_fim + entre / 2:.2f}H{w:.2f}", stroke=apo, sw=t * 0.5))
        y = y_fim
    if legenda:   # alinhada à esquerda pela TINTA (a lateral do 1º glifo não conta)
        lx, _, _, _ = _caixa_txt(f.fonte_mono, legenda, w * 0.04, 0.08)
        o.append(rot(f, legenda, w * 0.04, -lx, y + w * 0.08, apo, tr=0.08))
    return justo("".join(o), "bloco justificado" + (" · fios" if fios else "") + (f" · acento {acento + 1}" if acento is not None else ""),
                 "cada linha no corpo que dá a mesma largura NA TINTA · cartaz tipográfico, capa de carrossel")


def _caixa_txt(spec, s, size, tracking=0.0):
    """Caixa da TINTA do texto (x0, x1, y0, y1; y para baixo, linha de base em 0) pelas curvas dos glifos."""
    from fontTools.pens.boundsPen import BoundsPen
    fo = _font(spec)
    names, adv = fo.advances(s, size, tracking)
    k = size / fo.upm
    bp = BoundsPen(fo.gs)
    x = 0.0
    for g, a in zip(names, adv):
        fo.gs[g].draw(TransformPen(bp, (k, 0, 0, -k, x, 0)))
        x += a
    x0, y0, x1, y1 = bp.bounds
    return x0, x1, y0, y1


@amostra(FAM, "bloco justificado")
def _a_bloco(f):
    return [bloco(f), bloco(f, ("PERSONAL", "TRAINER", "ACADEMY"), acento=2, fios=True),
            bloco(f, ("PÓS-", "GRADUAÇÃO"), 340, acento=0, legenda="BLACK FRIDAY · 20H30"),
            bloco(f, ("NOITE 1", "NOITE 2", "NOITE 3"), 300, acento=0, fios=True)]


# ================================================================ numeral com contorno
def extrusao_d(spec, s, size, dx, dy, x=0.0, base=0.0, tracking=0.0, passo=0.5):
    """Lateral de uma EXTRUSÃO (sombra sólida em bloco): união exata (skia-pathops) das cópias do texto deslocadas de
    0 até (dx, dy) a cada `passo` px → 1 path só, sem degrau, sem fio aparecendo por dentro do desenho."""
    import pathops
    fo = _font(spec)
    names, adv = fo.advances(s, size, tracking)
    k = size / fo.upm
    n = max(1, int(math.ceil(math.hypot(dx, dy) / passo)))
    b = pathops.OpBuilder(fix_winding=True, keep_starting_points=False)
    for i in range(n + 1):
        ox, oy = dx * i / n, dy * i / n
        p = pathops.Path()
        pen = p.getPen()
        cx = x
        for g, a in zip(names, adv):
            fo.gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx + ox, base + oy)))
            cx += a
        b.add(p, pathops.PathOp.UNION)
    sp = SVGPathPen(None)
    b.resolve().draw(sp)
    return sp.getCommands()


def tracejado_svg(spec, s, size, x, base, cor, sw, traco, vao, tracking=0.0):
    """Texto em fio TRACEJADO sem emenda: cada contorno vira 1 path e o passo do tracejado é ajustado ao perímetro dele
    (número inteiro de traços); o traço fica centrado no ponto inicial (não sobra pedacinho no fechamento)."""
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.perimeterPen import PerimeterPen
    fo = _font(spec)
    names, adv = fo.advances(s, size, tracking)
    k = size / fo.upm
    rec = RecordingPen()
    cx = x
    for g, a in zip(names, adv):
        fo.gs[g].draw(TransformPen(rec, (k, 0, 0, -k, cx, base)))
        cx += a
    contornos, cur = [], []
    for op, args in rec.value:
        cur.append((op, args))
        if op in ("closePath", "endPath"):
            contornos.append(cur)
            cur = []
    per = traco + vao
    o = []
    for c in contornos:
        pm, sp = PerimeterPen(None), SVGPathPen(None)
        for op, args in c:
            getattr(pm, op)(*args)
            getattr(sp, op)(*args)
        e = pm.value / (max(2, round(pm.value / per)) * per)
        o.append(f'<path d="{sp.getCommands()}" fill="none" stroke="{cor}" stroke-width="{sw:.2f}" '
                 f'stroke-dasharray="{traco * e:.3f} {vao * e:.3f}" stroke-dashoffset="{traco * e / 2:.3f}" '
                 f'stroke-linejoin="round"/>')
    return "".join(o)


def numeral(f, n="1", modo="contorno", corpo=300.0):
    """Numeral grande da fonte display. contorno = só o fio; duplo = fio grosso vazado (linha dupla); extrusao = cheio
    no acento + lateral sólida em bloco (tom escuro do acento, baixo-direita); tracejado = fio tracejado sem emenda."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    sp = f.fonte_display
    d = _d(sp, n, corpo, 0, 0, 0.0)
    o = []
    if modo == "contorno":
        o.append(f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{t:.2f}" stroke-linejoin="round"/>')
    elif modo == "duplo":
        o.append(f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{t * 3.4:.2f}" stroke-linejoin="round"/>')
        o.append(f'<path d="{d}" fill="none" stroke="{f.fundo}" stroke-width="{t * 1.4:.2f}" stroke-linejoin="round"/>')
    elif modo == "extrusao":
        dx = corpo * 0.04
        o.append(f'<path d="{extrusao_d(sp, n, corpo, dx, dx)}" fill="{mistura(ac, f.fundo, 0.55)}"/>')
        o.append(f'<path d="{d}" fill="{ac}"/>')
    else:
        o.append(tracejado_svg(sp, n, corpo, 0, 0, ink, t * 0.8, t * 3, t * 2))
    return justo("".join(o), f"numeral {n} · {modo}", "numeral da fonte display (1 efeito por peça) · número da "
                 "noite, contagem, data")


@amostra(FAM, "numeral")
def _a_numeral(f):
    return [numeral(f, "1"), numeral(f, "2", "duplo"), numeral(f, "3", "extrusao"), numeral(f, "27", "tracejado", 260),
            numeral(f, "20H30", "contorno", 150)]


# ================================================================ texto centrado pela tinta
def _txt_tinta(spec, s, size, cx, cy, fill, tr=0.0, ang=0.0, vertical="tinta"):
    """Texto centrado pela TINTA em (cx, cy): horizontal sempre pela tinta; vertical 'tinta' (acento e cedilha contam)
    ou 'cap' (centro da maiúscula — linha de base estável). Rotação opcional em torno do centro."""
    xa, xb, ya, yb = _caixa_txt(spec, s, size, tr)
    my = (ya + yb) / 2 if vertical == "tinta" else -cap(spec) * size / 2
    giro = f" rotate({ang:.2f})" if ang else ""
    return (f'<path d="{_d(spec, s, size, 0, 0, tr)}" fill="{fill}" transform="translate({cx:.2f} {cy:.2f}){giro} '
            f'translate({-(xa + xb) / 2:.2f} {-my:.2f})"/>')


# ================================================================ rótulo vertical (lombada)
def lombada(f, txt="BLACK FRIDAY", numero="01", modo="cheio", H=340.0):
    """Rótulo vertical como lombada: número no topo e texto lendo de baixo para cima, tudo medido na TINTA (acento e
    cedilha contam) com respiro lateral ≥ 0,2 da largura e de cabeça/pé ≥ raio. modo: cheio (barra no acento, raio sm)
    | contorno (fio, raio sm) | livro (raio 0, faixas de cabeça e pé no acento) | solto (só texto + régua à direita)."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    W = u * 2.1                        # coluna do texto
    lat = W * 0.2                      # respiro lateral mínimo da tinta
    m = max(f.raio_sm, W * 0.3)        # respiro de cabeça e pé (≥ raio do canto, F13)
    topo, pe = 0.0, H
    nc = tc = ink
    o = []
    if modo == "cheio":
        o.append(f'<path d="{ret(0, 0, W, H, f.raio_sm)}" fill="{ac}"/>')
        nc = tc = f.sobre_acento
    elif modo == "contorno":
        o.append(f'<path d="{ret(t / 2, t / 2, W - t, H - t, f.raio_sm - t / 2)}" fill="none" stroke="{ink}" '
                 f'stroke-width="{t:.2f}"/>')
        lat += t
        topo, pe = t, H - t
    elif modo == "livro":
        o.append(f'<path d="{ret(0, 0, W, H, 0)}" fill="{mistura(f.fundo, ink, 0.14)}"/>')
        hb = H * 0.025
        for y in (H * 0.05, H * 0.95 - hb):
            o.append(f'<path d="{ret(0, y, W, hb, 0)}" fill="{ac}"/>')
        topo, pe = H * 0.05 + hb, H * 0.95 - hb
        nc, m = ac, W * 0.36
    else:   # solto: régua FORA da coluna do texto (6 px + traço maior)
        xr = W + 6 + u * 0.5
        o.append(_p(f"M{xr:.2f} 0V{H:.2f}", stroke=apo, sw=t * 0.5))
        for k in range(0, 11):
            y = min(H - t * 0.25, max(t * 0.25, H * k / 10))
            o.append(_p(f"M{xr - (u * 0.5 if k % 5 == 0 else u * 0.25):.2f} {y:.2f}H{xr:.2f}", stroke=apo, sw=t * 0.5))
    mono = f.fonte_mono
    # número: maiúscula = 0,34 W, cabe na coluna
    capn = W * 0.34
    szn = capn / cap(mono)
    xa, xb, _, _ = _caixa_txt(mono, numero, szn, 0.02)
    if xb - xa > W - 2 * lat:
        szn *= (W - 2 * lat) / (xb - xa)
        capn = cap(mono) * szn
    yn = topo + m + capn / 2
    o.append(_txt_tinta(mono, numero, szn, W / 2, yn, nc, 0.02, vertical="cap"))
    # texto: ocupa o vão entre o número e o pé, centrado nele
    ya_, yb_ = yn + capn / 2 + W * 0.4, pe - m
    xa, xb, ya, yb = _caixa_txt(f.fonte_texto, txt, 100.0, 0.14)
    sz = 100.0 * min((yb_ - ya_) / (xb - xa), (W - 2 * lat) / (yb - ya), W * 0.46 / 100.0)
    o.append(_txt_tinta(f.fonte_texto, txt, sz, W / 2, (ya_ + yb_) / 2, tc, 0.14, ang=-90))
    return justo("".join(o), f"lombada · {modo} · {txt}", "rótulo vertical lendo de baixo para cima (padrão de lombada "
                 "brasileiro), medido na tinta · borda de peça, menu lateral, coleção de módulos")


@amostra(FAM, "lombada")
def _a_lombada(f):
    return [lombada(f), lombada(f, "PÓS-GRADUAÇÃO", "02", "contorno"), lombada(f, "NOME DA MARCA", "03", "livro"),
            lombada(f, "AO VIVO · 20H30", "N1", "solto")]


# ================================================================ datador (carimbo de data em mono)
def datador(f, linha="27 NOV 2026", cima="BLACK FRIDAY", baixo="AO VIVO · 20H30", modo="bandas", angulo=-4.0):
    """Datador de borracha (objeto mecânico → raio 0). bandas = um caractere por banda (as rodinhas do datador),
    cada caractere centrado pela TINTA na sua banda, vão ≥ 1,2 traço entre bandas, rótulos de cima e de baixo, moldura
    dupla; caixa = a data grande na moldura dupla com o rótulo DENTRO; linha = a data entre 2 fios medidos na tinta.
    Data = parâmetro (27/11/2026 = Black Friday de verdade)."""
    t, ac = f.traco, f.acento
    u = f.unidade
    cor = ac
    mono, tx = f.fonte_mono, f.fonte_texto
    capd = u * 0.95                     # maiúscula da data
    szd = capd / cap(mono)
    capl = u * 0.4                      # maiúscula dos rótulos
    szl = capl / cap(tx)
    o = []
    if modo == "linha":
        xa, xb, ya, yb = _caixa_txt(mono, linha, szd, 0.1)
        g = capd * 0.45
        o.append(_p(f"M{xa:.2f} {ya - g:.2f}H{xb:.2f}M{xa:.2f} {yb + g:.2f}H{xb:.2f}", stroke=cor, sw=t * 0.7))
        o.append(f'<path d="{_d(mono, linha, szd, 0, 0, 0.1)}" fill="{cor}"/>')
    else:
        # linha principal (y = 0 é o centro da maiúscula)
        if modo == "bandas":
            chars = [c for c in linha if c != " "]
            lw = max(_caixa_txt(mono, c, szd)[1] - _caixa_txt(mono, c, szd)[0] for c in chars)
            bw, bh = lw + capd * 0.4, capd * 1.56
            gap, esp = max(t * 1.2, capd * 0.14), capd * 0.55
            x, princ = 0.0, []
            for c in linha:
                if c == " ":
                    x += esp
                    continue
                princ.append(f'<path d="{ret(x, -bh / 2, bw, bh, 0)}" fill="none" stroke="{cor}" '
                             f'stroke-width="{t * 0.45:.2f}" stroke-opacity="0.75"/>')
                princ.append(_txt_tinta(mono, c, szd, x + bw / 2, 0, cor, vertical="cap"))
                x += bw + gap
            wl, hl = x - gap, bh
        else:   # caixa
            xa, xb, _, _ = _caixa_txt(mono, linha, szd, 0.08)
            wl, hl = xb - xa, capd
            princ = [_txt_tinta(mono, linha, szd, wl / 2, 0, cor, 0.08, vertical="cap")]
        rot_w = [(_caixa_txt(tx, s, szl, 0.14)[1] - _caixa_txt(tx, s, szl, 0.14)[0]) for s in (cima, baixo) if s]
        Wc = max([wl] + rot_w)
        g = capl * 1.3                                   # vão rótulo ↔ linha principal
        y0 = -hl / 2 - g - capl                          # topo do conteúdo
        y1 = hl / 2 + ((g + capl) if (modo == "bandas" and baixo) else 0)
        dx = (Wc - wl) / 2
        o.append(f'<g transform="translate({dx:.2f} 0)">{"".join(princ)}</g>')
        if cima:
            o.append(_txt_tinta(tx, cima, szl, Wc / 2, y0 + capl / 2, cor, 0.14, vertical="cap"))
        if modo == "bandas" and baixo:
            o.append(_txt_tinta(tx, baixo, szl, Wc / 2, y1 - capl / 2, cor, 0.14, vertical="cap"))
        P = u * 0.6                                      # respiro interno até o fio fino
        e1, e2, vao = t * 0.5, t * 1.1, t * 1.5          # fio fino, fio grosso, vão entre eles
        x0, x1, yt, yb2 = -P, Wc + P, y0 - P, y1 + P
        o.append(f'<path d="{ret(x0, yt, x1 - x0, yb2 - yt, 0)}" fill="none" stroke="{cor}" stroke-width="{e1:.2f}"/>')
        k = e1 / 2 + vao + e2 / 2
        o.append(f'<path d="{ret(x0 - k, yt - k, x1 - x0 + 2 * k, yb2 - yt + 2 * k, 0)}" fill="none" stroke="{cor}" '
                 f'stroke-width="{e2:.2f}"/>')
    corpo = f'<g transform="rotate({angulo:.2f})">{"".join(o)}</g>'
    return justo(corpo, f"datador · {modo} · {linha}", "data em mono como carimbo de data (bandas do datador), medida "
                 "na tinta · data real da campanha; 1 carimbo por peça")


@amostra(FAM, "datador")
def _a_datador(f):
    return [datador(f), datador(f, "NOITE 1", modo="caixa", cima="AO VIVO · 20H30", angulo=3),
            datador(f, "27.11.2026", modo="linha", angulo=0), datador(f, "20H30", cima="NOITE 1", baixo="AO VIVO", angulo=-6)]
