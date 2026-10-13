"""ornamentos.formas — família CONTÊINERES E FORMAS (a forma que segura conteúdo).

Origem (references/elementos.md "Raios e bordas estilizadas"; pesquisa 11 E12/E34/E107; 14b §4.1–4.3; 14 A/D):
  - 1 raio por peça (fora a pílula); respiro = raio (Odido); aninhado = externo − (borda + espaço) (14b §4.3);
  - cantos por tipo como o `corner-shape` do CSS: r = round · c = bevel (chanfro) · s = squircle · i = scoop
    (côncavo) · n = notch (degrau) — o SVG e o CSS saem da MESMA receita;
  - a forma conta o que é: pasta = ficha/dossiê · entalhe = etiqueta pendurada · ingresso = vaga · balão = fala.
Função principal: conteiner(f, w, h, forma=…, estilo=cheio|contorno|duplo|passe) → Elemento (svg + css).

Também guarda os UTILITÁRIOS COMPARTILHADOS da família A (fios, selos, faixas, profundidade importam daqui):
mistura, claro, no_claro, uid, caixa_texto, rotulo, circulo_d, _P (construtor de path com espelho/transposição).
"""
import hashlib
import math

from .nucleo import amostra, elemento, texto, largura, cap, _font

FAM = "formas"


# =====================================================================================================================
# utilitários compartilhados
# =====================================================================================================================
def _rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mistura(a, b, t):
    """Cor entre a (t=0) e b (t=1), em sRGB — tons derivados da ficha (nunca cor de fora)."""
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ra, rb))


def claro(f):
    """A mesma ficha para fundo CLARO (papel): tinta vira o escuro da marca; o acento continua."""
    return f.com(fundo=f.papel, tinta=f.fundo, sobre_acento=f.fundo, papel=f.tinta,
                 apoio=mistura(f.fundo, f.papel, 0.45))


def no_claro(el):
    """Marca o elemento para o catálogo mostrar sobre o papel."""
    el.fundo_claro = True
    return el


def uid(*partes):
    return "o" + hashlib.md5("|".join(map(str, partes)).encode()).hexdigest()[:8]


def caixa_texto(spec, s, size, x=0.0, baseline=0.0, tracking=0.0):
    """Caixa da TINTA do texto (x0, y0, x1, y1) — para centrar pelo desenho, não pela caixa da fonte."""
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.transformPen import TransformPen
    F = _font(spec)
    names, adv = F.advances(s, size, tracking)
    k = size / F.upm
    bp = BoundsPen(F.gs)
    cx = x
    for g, a in zip(names, adv):
        F.gs[g].draw(TransformPen(bp, (k, 0, 0, -k, cx, baseline)))
        cx += a
    return bp.bounds or (x, baseline, x, baseline)


def path_texto(spec, s, size, x, baseline, tracking=0.0, anchor="start"):
    """Só o `d` do texto em curvas (para juntar com outras formas num path evenodd = texto vazado)."""
    F = _font(spec)
    w = F.width(s, size, tracking)
    x0 = x if anchor == "start" else x - w / 2 if anchor == "middle" else x - w
    return F.path(s, size, x0, baseline, tracking), w


def corpo(spec, cap_px):
    """Corpo da fonte para uma altura de maiúscula em px."""
    return cap_px / cap(spec)


def rotulo(f, s, x, cy, fill, cap_px=25.0, spec=None, tracking=0.1, anchor="start"):
    """Rótulo em caixa-alta CENTRADO na linha cy pela altura da maiúscula. Devolve (svg, largura)."""
    spec = spec or f.fonte_texto
    return texto(spec, s, corpo(spec, cap_px), x, cy + cap_px / 2, fill, tracking, anchor)


def larg_rotulo(f, s, cap_px=25.0, spec=None, tracking=0.1):
    spec = spec or f.fonte_texto
    return largura(spec, s, corpo(spec, cap_px), tracking)


def circulo_d(cx, cy, r, horario=False):
    """Círculo como subpath (para furos em evenodd)."""
    s = 1 if horario else 0
    return (f"M{cx - r:.2f} {cy:.2f}a{r:.2f} {r:.2f} 0 1 {s} {2 * r:.2f} 0"
            f"a{r:.2f} {r:.2f} 0 1 {s} {-2 * r:.2f} 0Z")


class _P:
    """Construtor de path com espelho horizontal/vertical e transposição (o arco troca de sentido sozinho)."""

    def __init__(self, mx=None, my=None, tr=False):
        self.c, self.mx, self.my, self.tr = [], mx, my, tr
        self.flip = ((mx is not None) + (my is not None) + bool(tr)) % 2 == 1

    def _xy(self, x, y):
        if self.mx is not None:
            x = 2 * self.mx - x
        if self.my is not None:
            y = 2 * self.my - y
        return (y, x) if self.tr else (x, y)

    def M(self, x, y):
        X, Y = self._xy(x, y)
        self.c.append(f"M{X:.2f} {Y:.2f}")
        return self

    def L(self, x, y):
        X, Y = self._xy(x, y)
        self.c.append(f"L{X:.2f} {Y:.2f}")
        return self

    def C(self, x1, y1, x2, y2, x, y):
        a, b = self._xy(x1, y1)
        c, d = self._xy(x2, y2)
        X, Y = self._xy(x, y)
        self.c.append(f"C{a:.2f} {b:.2f} {c:.2f} {d:.2f} {X:.2f} {Y:.2f}")
        return self

    def A(self, r, x, y, sweep=1, grande=0):
        if r <= 0.01:
            return self.L(x, y)
        s = (1 - sweep) if self.flip else sweep
        X, Y = self._xy(x, y)
        self.c.append(f"A{r:.2f} {r:.2f} 0 {grande} {s} {X:.2f} {Y:.2f}")
        return self

    def Z(self):
        self.c.append("Z")
        return self

    def d(self):
        return "".join(self.c)


def _attrs(fill="none", stroke=None, sw=None, extra=""):
    a = f'fill="{fill}"'
    if stroke:
        a += f' stroke="{stroke}" stroke-width="{sw:.2f}" stroke-linejoin="round"'
    return a + (" " + extra if extra else "")


# =====================================================================================================================
# geometria das formas: fn(x, y, w, h, r, d, **kw) -> path  (d = recuo para dentro: contorno e contorno duplo)
# =====================================================================================================================
_K = math.tan(math.radians(30))     # deslocamento horizontal da curva-S quando o contorno recua d (≈ 0,58 d)
_CSS_CANTO = {"r": "round", "c": "bevel", "s": "squircle", "i": "scoop", "n": "notch", "q": "square"}


def _norm_cantos(cantos, r):
    if cantos is None:
        return [("r", r)] * 4
    out = []
    for c in cantos:
        if isinstance(c, (int, float)):
            out.append(("r", float(c)))
        else:
            out.append((c[0], float(c[1])))
    return out


def p_cantos(x, y, w, h, r=0.0, d=0.0, cantos=None, n=4.0, **_):
    """Retângulo com cada canto do seu tipo (te, td, bd, be). Tipos: r · c · s · i · n (ver _CSS_CANTO)."""
    cs = _norm_cantos(cantos, r)
    X0, Y0, W, H = x + d, y + d, w - 2 * d, h - 2 * d
    lim = min(W, H) / 2
    ajust = []
    for t, s in cs:
        if s <= 0 or t == "q":
            ajust.append(("q", 0.0))
            continue
        s2 = {"r": s - d, "c": s - d * (2 - math.sqrt(2)), "s": s - d, "i": s + d, "n": s}[t]
        ajust.append((t, max(0.0, min(s2, lim))))
    P = [(X0, Y0), (X0 + W, Y0), (X0 + W, Y0 + H), (X0, Y0 + H)]
    U_OUT = [(1, 0), (0, 1), (-1, 0), (0, -1)]          # direção da aresta que SAI de cada canto (horário)
    U_IN = [(0, -1), (1, 0), (0, 1), (-1, 0)]           # direção da aresta que CHEGA
    p = _P()
    for i, ((t, s), (px, py)) in enumerate(zip(ajust, P)):
        ux, uy = U_OUT[i]
        vx, vy = U_IN[i]
        a = (px - s * vx, py - s * vy)                  # ponto na aresta que chega
        b = (px + s * ux, py + s * uy)                  # ponto na aresta que sai
        (p.M if i == 0 else p.L)(*a)
        if t == "q" or s == 0:
            continue
        if t == "r":
            p.A(s, *b, sweep=1)
        elif t == "c":
            p.L(*b)
        elif t == "i":
            p.A(s, *b, sweep=0)
        elif t == "n":
            p.L(a[0] + s * ux, a[1] + s * uy)
            p.L(*b)
        elif t == "s":
            cx, cy = px - s * vx + s * ux, py - s * vy + s * uy
            N = 28
            for k in range(1, N + 1):
                tt = (math.pi / 2) * k / N
                e1, e2 = abs(math.cos(tt)) ** (2 / n), abs(math.sin(tt)) ** (2 / n)
                p.L(cx - s * ux * e1 + s * vx * e2, cy - s * uy * e1 + s * vy * e2)
    return p.Z().d()


def css_cantos(cantos, r):
    cs = _norm_cantos(cantos, r)
    rad = " ".join(f"{s:g}px" for _, s in cs)
    tipos = [_CSS_CANTO.get(t, "round") for t, _ in cs]
    if len(set(tipos)) == 1 and tipos[0] == "round":
        return f"border-radius:{rad};"
    return (f"border-radius:{rad};corner-shape:{' '.join(tipos)};"
            "/* corner-shape: Chrome 139+; sem suporte vira canto redondo (reserva aceitável) */")


def _curva_s(p, x0, y0, x1, y1):
    """Curva-S da aba (proporções medidas no menu do gsaweb: alças a 39,6% e 47,2% do ombro)."""
    s = x1 - x0
    p.C(x0 + 0.396 * s, y0, x0 + 0.472 * s, y1, x1, y1)


def p_pasta(x, y, w, h, r=12.0, d=0.0, aba=0.42, alt=56.0, lado="esq", **_):
    """Pasta (ficha/dossiê): aba que sobe com curva-S; alt = altura da aba; aba = largura da aba (fração)."""
    p = _P(mx=(x + w / 2) if lado == "dir" else None)
    X0, Y0, W, H = x + d, y + d, w - 2 * d, h - 2 * d
    s = alt * 1.06
    xa = x + aba * w - d * _K
    # o canto da aba é o MESMO raio do cartão (a borda esquerda continua até embaixo; nada de prender em alt/2,
    # que dava 2 raios quase iguais — 24,5 × 28); só não pode passar do começo da curva-S
    R = max(0.0, min(r - d, xa - X0, H / 2))
    Rb = max(0.0, r - d)
    p.M(X0, Y0 + R).A(R, X0 + R, Y0).L(xa, Y0)
    _curva_s(p, xa, Y0, xa + s, Y0 + alt)
    p.L(X0 + W - Rb, Y0 + alt).A(Rb, X0 + W, Y0 + alt + Rb).L(X0 + W, Y0 + H - Rb).A(Rb, X0 + W - Rb, Y0 + H)
    p.L(X0 + Rb, Y0 + H).A(Rb, X0, Y0 + H - Rb)
    return p.Z().d()


def p_entalhe(x, y, w, h, r=12.0, d=0.0, boca=0.40, fundo=48.0, **_):
    """Cartão com ENTALHE no topo (o negativo da aba pendurada): boca = largura de baixo (fração), fundo = profundidade."""
    X0, Y0, W, H = x + d, y + d, w - 2 * d, h - 2 * d
    R = max(0.0, r - d)
    s = fundo * 1.06
    nx0 = x + (w - boca * w) / 2 - s - d * _K
    nx1 = x + (w + boca * w) / 2 + s + d * _K
    p = _P().M(X0 + R, Y0).L(nx0, Y0)
    _curva_s(p, nx0, Y0, nx0 + s, Y0 + fundo)
    p.L(nx1 - s, Y0 + fundo)
    p.C(nx1 - 0.472 * s, Y0 + fundo, nx1 - 0.396 * s, Y0, nx1, Y0)
    p.L(X0 + W - R, Y0).A(R, X0 + W, Y0 + R).L(X0 + W, Y0 + H - R).A(R, X0 + W - R, Y0 + H)
    p.L(X0 + R, Y0 + H).A(R, X0, Y0 + H - R).L(X0, Y0 + R).A(R, X0 + R, Y0)
    return p.Z().d()


def p_aba_pendurada(x, y, w, h, r=0.0, d=0.0, **_):
    """A aba pendurada em si (topo inteiro, base mais estreita; ombros côncavos)."""
    s = h * 1.06
    X0, W = x + d * _K, w - 2 * d * _K
    p = _P().M(X0, y + d).L(X0 + W, y + d)
    p.C(X0 + W - 0.396 * s, y + d, X0 + W - 0.472 * s, y + h - d, X0 + W - s, y + h - d)
    p.L(X0 + s, y + h - d)
    p.C(X0 + 0.472 * s, y + h - d, X0 + 0.396 * s, y + d, X0, y + d)
    return p.Z().d()


def p_recorte(x, y, w, h, r=12.0, d=0.0, corte=96.0, canto="td", **_):
    """Cartão com RECORTE de canto (raio invertido): o canto vira um encaixe quadrado para um botão/selo."""
    p = _P(mx=(x + w / 2) if canto in ("te", "be") else None, my=(y + h / 2) if canto in ("bd", "be") else None)
    X0, Y0, W, H = x + d, y + d, w - 2 * d, h - 2 * d
    c = corte
    # côncavo do encaixe CONCÊNTRICO com o botão (centro no meio do corte): folga constante em volta
    # (externo = interno + afastamento). Raio 0 = encaixe reto.
    Ri = (c / 2 + d) if r > 0 else min(d, c / 2)
    R = max(0.0, min(r - d, c - Ri))
    XR, YB = X0 + W, Y0 + H
    p.M(X0 + R, Y0).L(XR - c - R, Y0).A(R, XR - c, Y0 + R).L(XR - c, Y0 + c - Ri).A(Ri, XR - c + Ri, Y0 + c, sweep=0)
    p.L(XR - R, Y0 + c).A(R, XR, Y0 + c + R).L(XR, YB - R).A(R, XR - R, YB).L(X0 + R, YB).A(R, X0, YB - R)
    p.L(X0, Y0 + R).A(R, X0 + R, Y0)
    return p.Z().d()


def p_ingresso(x, y, w, h, r=12.0, d=0.0, canhoto=0.26, entalhe=14.0, furo=3.5, vertical=False, furos=True, **_):
    """Ingresso: meia-lua no topo e na base da linha do canhoto + picote (furos de 7 px, passo 2× o diâmetro)."""
    if vertical:
        x, y, w, h = y, x, h, w
    p = _P(tr=vertical)
    X0, Y0, W, H = x + d, y + d, w - 2 * d, h - 2 * d
    R = max(0.0, r - d)
    pn = entalhe + d
    # meia-lua CONCÊNTRICA no recuo (centro fica na borda original): a corda na linha recuada é ±√(pn² − d²)
    # (antes ±pn com o centro descendo junto → no contorno duplo a meia-lua de dentro ficava 2× mais funda)
    ch = math.sqrt(max(0.0, pn * pn - d * d))
    sx = x + w * (1 - canhoto)
    XR, YB = X0 + W, Y0 + H
    p.M(X0 + R, Y0).L(sx - ch, Y0).A(pn, sx + ch, Y0, sweep=0).L(XR - R, Y0).A(R, XR, Y0 + R).L(XR, YB - R)
    p.A(R, XR - R, YB).L(sx + ch, YB).A(pn, sx - ch, YB, sweep=0).L(X0 + R, YB).A(R, X0, YB - R).L(X0, Y0 + R)
    p.A(R, X0 + R, Y0).Z()
    dd = p.d()
    if furos and d == 0:
        passo = furo * 4
        y0, y1 = y + entalhe + passo * 0.9, y + h - entalhe - passo * 0.9
        n = max(1, int((y1 - y0) // passo))
        off = (y1 - y0 - n * passo) / 2
        for k in range(n + 1):
            cy = y0 + off + k * passo
            dd += circulo_d(*((cy, sx) if vertical else (sx, cy)), furo)
    return dd


def linha_picote(x, y, w, h, canhoto=0.26, entalhe=14.0, vertical=False):
    """Segmento do picote (para o estilo contorno: tracejado no lugar dos furos)."""
    if vertical:
        sy = y + h * (1 - canhoto)
        return (x + entalhe + 6, sy, x + w - entalhe - 6, sy)
    sx = x + w * (1 - canhoto)
    return (sx, y + entalhe + 6, sx, y + h - entalhe - 6)


def p_balao(x, y, w, h, r=12.0, d=0.0, cauda="esq", rabo=34.0, **_):
    """Balão de fala (Odido): o canto vivo aponta para baixo; cauda esq · dir · centro. h inclui o rabo."""
    p = _P(mx=(x + w / 2) if cauda == "dir" else None)
    X0, Y0, W = x + d, y + d, w - 2 * d
    hb = h - rabo
    YB = y + hb - d
    R = max(0.0, min(r - d, (hb - 2 * d) / 2))
    XR = X0 + W
    p.M(X0 + R, Y0).L(XR - R, Y0).A(R, XR, Y0 + R).L(XR, YB - R).A(R, XR - R, YB)
    if cauda == "centro":
        cx, tw = x + w / 2, rabo * 1.25
        p.L(cx + tw / 2 - d * 0.4, YB).L(cx, y + h - d * 2.2).L(cx - tw / 2 + d * 0.4, YB)
        p.L(X0 + R, YB).A(R, X0, YB - R)
    else:
        tw = rabo * 1.15
        p.L(X0 + tw - d * 0.4, YB).L(X0, y + h - d * 2.4)
    p.L(X0, Y0 + R).A(R, X0 + R, Y0)
    return p.Z().d()


def p_etiqueta(x, y, w, h, r=12.0, d=0.0, chanfro=None, furo=None, vertical=False, **_):
    """Etiqueta de bagagem: ponta chanfrada com furo (ilhós). vertical = ponta para cima."""
    if vertical:
        x, y, w, h = y, x, h, w
    c = (chanfro if chanfro is not None else h * 0.30) - d * (2 - math.sqrt(2))
    p = _P(tr=vertical)
    X0, Y0, W, H = x + d, y + d, w - 2 * d, h - 2 * d
    R = max(0.0, r - d)
    XR, YB = X0 + W, Y0 + H
    p.M(X0 + c, Y0).L(XR - R, Y0).A(R, XR, Y0 + R).L(XR, YB - R).A(R, XR - R, YB).L(X0 + c, YB).L(X0, YB - c)
    p.L(X0, Y0 + c).Z()
    dd = p.d()
    if d == 0:
        fr = furo or h * 0.085
        cx, cy = x + (chanfro if chanfro is not None else h * 0.30) + fr * 1.2, y + h / 2
        dd += circulo_d(*((cy, cx) if vertical else (cx, cy)), fr)
    return dd


def centro_furo_etiqueta(x, y, w, h, chanfro=None, furo=None, vertical=False):
    if vertical:
        x, y, w, h = y, x, h, w
    fr = furo or h * 0.085
    cx, cy = x + (chanfro if chanfro is not None else h * 0.30) + fr * 1.2, y + h / 2
    return ((cy, cx) if vertical else (cx, cy)), fr


def aba_lugar(h, r, pos=0.16, aba_c=None):
    """Início e comprimento REAIS da aba lateral: o topo da aba fica ≥ 2 raios abaixo do canto do cartão (canto +
    concordância côncava sem se atropelar) e o fim ≥ 2 raios acima do canto de baixo. Devolve (início, comprimento)."""
    ac = aba_c if aba_c is not None else h * 0.34
    y0 = min(max(pos * h, 2 * r), max(2 * r, h - 2 * r - ac))
    return y0, ac


def p_aba(x, y, w, h, r=12.0, d=0.0, aba_l=44.0, aba_c=None, pos=0.16, **_):
    """Cartão com ABA LATERAL (divisória de fichário): aba_l = quanto a aba sai, aba_c = comprimento, pos = início.
    Concordância côncava (r + d) + canto da aba (r − d) cabem na saída da aba: se aba_l < 2r, os dois encolhem juntos
    (antes se atropelavam → bico/laço no contorno)."""
    X0, Y0, W, H = x + d, y + d, w - 2 * d, h - 2 * d
    XR, YB = X0 + W, Y0 + H
    xb = XR - aba_l
    py, ac = aba_lugar(h, r, pos, aba_c)
    ty0, ty1 = y + py + d, y + py + ac - d
    R = max(0.0, r - d)
    Rt = max(0.0, min(r - d, (ty1 - ty0) / 2))
    Rf = r + d if r > 0 else 0.0
    if Rf + Rt > aba_l:
        k = aba_l / (Rf + Rt)
        Rf, Rt = Rf * k, Rt * k
    p = _P().M(X0 + R, Y0).L(xb - R, Y0).A(R, xb, Y0 + R).L(xb, ty0 - Rf).A(Rf, xb + Rf, ty0, sweep=0)
    p.L(XR - Rt, ty0).A(Rt, XR, ty0 + Rt).L(XR, ty1 - Rt).A(Rt, XR - Rt, ty1).L(xb + Rf, ty1)
    p.A(Rf, xb, ty1 + Rf, sweep=0).L(xb, YB - R).A(R, xb - R, YB).L(X0 + R, YB).A(R, X0, YB - R).L(X0, Y0 + R)
    p.A(R, X0 + R, Y0)
    return p.Z().d()


FORMAS = {"cantos": p_cantos, "pasta": p_pasta, "entalhe": p_entalhe, "recorte": p_recorte, "ingresso": p_ingresso,
          "balao": p_balao, "etiqueta": p_etiqueta, "aba": p_aba, "aba_pendurada": p_aba_pendurada}


# =====================================================================================================================
# conteiner(): a função pública
# =====================================================================================================================
def conteiner(f, w, h, forma="cantos", r=None, estilo="cheio", cor=None, linha=None, folga=None, miolo=None,
              nome=None, nota="", conteudo="", margem=0.0, **kw):
    """Contêiner no tamanho final. estilo: cheio · contorno · duplo (2 contornos concêntricos) · passe (contorno +
    miolo cheio concêntrico). r = raio da ficha por padrão; folga = espaço entre os contornos (padrão = unidade/3).
    Devolve Elemento com svg (+ css quando a forma tem equivalente)."""
    r = f.raio if r is None else r
    t = f.traco
    g = folga if folga is not None else max(2 * t, f.unidade / 3)
    fn = FORMAS[forma]
    cor = cor or (f.acento if estilo == "cheio" else f.tinta)
    linha = linha or cor
    m = margem
    W, H = w + 2 * m, h + 2 * m
    corpo_svg = ""
    if estilo == "cheio":
        corpo_svg += f'<path d="{fn(m, m, w, h, r, 0, **kw)}" fill="{cor}" fill-rule="evenodd"/>'
    elif estilo == "contorno":
        corpo_svg += f'<path d="{fn(m, m, w, h, r, t / 2, **kw)}" {_attrs("none", linha, t)}/>'
    elif estilo == "duplo":
        corpo_svg += f'<path d="{fn(m, m, w, h, r, t / 2, **kw)}" {_attrs("none", linha, t)}/>'
        corpo_svg += f'<path d="{fn(m, m, w, h, r, t * 1.5 + g, **kw)}" {_attrs("none", linha, t)}/>'
    elif estilo == "passe":
        corpo_svg += f'<path d="{fn(m, m, w, h, r, t / 2, **kw)}" {_attrs("none", linha, t)}/>'
        corpo_svg += f'<path d="{fn(m, m, w, h, r, t + g, **kw)}" fill="{miolo or cor}"/>'
    if forma == "ingresso" and estilo != "cheio":
        # o picote começa DEPOIS da meia-lua mais funda (no duplo, a de dentro) + 2 traços de folga — nunca cruza
        # nem tangencia o contorno; tracejado com traço inteiro nas duas pontas (sem toco)
        dm = {"contorno": t / 2, "duplo": t * 1.5 + g, "passe": t / 2}[estilo]
        ent = kw.get("entalhe", 14.0)
        x0, y0, x1, y1 = linha_picote(m, m, w, h, kw.get("canhoto", 0.26), ent, kw.get("vertical", False))
        folga_p = ent + dm + t / 2 + 2 * t
        if kw.get("vertical", False):
            x0, x1 = m + folga_p, m + w - folga_p
        else:
            y0, y1 = m + folga_p, m + h - folga_p
        L = math.hypot(x1 - x0, y1 - y0)
        tr, vao = t * 2, t * 2.4
        n = max(2, round((L + vao) / (tr + vao)))
        vao = (L - n * tr) / (n - 1)
        corpo_svg += (f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="{linha}" '
                      f'stroke-width="{t:.2f}" stroke-dasharray="{tr:.2f} {vao:.2f}"/>')
    corpo_svg += conteudo
    # ---- CSS (site)
    if forma == "cantos":
        geo = css_cantos(kw.get("cantos"), r)
    else:
        geo = (f"clip-path:path('{fn(0, 0, w, h, r, 0, **kw)}');"
               "/* path em px: gerar no tamanho final; sombra = filter:drop-shadow no PAI */")
    pinta = {"cheio": f"background:{cor};", "contorno": f"border:{t:g}px solid {linha};",
             "duplo": f"border:{t:g}px solid {linha};box-shadow:inset 0 0 0 {g:g}px {f.fundo},"
                      f"inset 0 0 0 {g + t:g}px {linha};",
             "passe": f"border:{t:g}px solid {linha};padding:{g:g}px;background:{miolo or cor} content-box;"}[estilo]
    css = f".el{{width:{w:g}px;height:{h:g}px;{pinta}{geo}}}"
    if forma != "cantos" and estilo != "cheio":
        css += " /* contorno em forma recortada: desenhar o SVG (clip-path corta a borda) */"
    return elemento(W, H, corpo_svg, nome or f"{forma} {estilo}", FAM, css=css, nota=nota)


# =====================================================================================================================
# elementos compostos (moldura, janela, telas, aba pendurada, recorte com botão)
# =====================================================================================================================
def moldura(f, w, h, tipo="dupla", R=None, cor=None, miolo=None, nome=None):
    """Moldura CONCÊNTRICA: todo raio interno = externo − (borda + espaço) — a conta do gsaweb (32 − 6 = 26).
    R = raio do aro de FORA (padrão `raio_lg`, a "moldura" da escala); no passe-partout R = raio da JANELA (padrão
    `raio`, foto em cartão) e o de fora = janela + margem (moldura externa: externo = interno + afastamento)."""
    if R is None:
        R = f.raio if tipo == "passe" else f.raio_lg
    t = f.traco
    cor = cor or f.tinta
    g = f.unidade / 2
    corpo_svg, conta = "", ""
    if tipo == "dupla":
        corpo_svg += f'<path d="{p_cantos(0, 0, w, h, R, t / 2)}" {_attrs("none", cor, t)}/>'
        corpo_svg += f'<path d="{p_cantos(0, 0, w, h, R, 1.5 * t + g)}" {_attrs("none", cor, t)}/>'
        conta = f"externo {R:g} → interno {max(0, R - t - g):g} (− borda {t:g} − espaço {g:g})"
    elif tipo == "aninhada":
        b = 2 * t
        g = f.unidade / 2
        corpo_svg += f'<path d="{p_cantos(0, 0, w, h, R, b / 2)}" {_attrs("none", cor, b)}/>'
        corpo_svg += f'<path d="{p_cantos(0, 0, w, h, R, b + g)}" fill="{miolo or f.acento}"/>'
        conta = f"moldura {R:g} · borda {b:g} · espaço {g:g} → painel {max(0, R - b - g):g}"
    elif tipo == "tripla":
        passo = f.unidade * 0.75
        for k in range(3):
            corpo_svg += (f'<path d="{p_cantos(0, 0, w, h, R, t / 2 + k * passo)}" '
                          f'{_attrs("none", cor if k == 0 else (f.apoio if k == 1 else f.acento), t)}/>')
        conta = f"3 aros, passo {passo:g}: {R:g} → {max(0, R - passo):g} → {max(0, R - 2 * passo):g}"
    elif tipo == "passe":
        mg = f.unidade * 1.5
        Ro = R + mg                                  # externo = janela + margem (concêntrico)
        janela_ = p_cantos(0, 0, w, h, Ro, mg)
        corpo_svg += f'<path d="{p_cantos(0, 0, w, h, Ro)}{janela_}" fill="{f.papel}" fill-rule="evenodd"/>'
        fi = mg + f.unidade * 0.5
        corpo_svg += f'<path d="{p_cantos(0, 0, w, h, Ro, fi)}" {_attrs("none", f.acento, t * 0.67)}/>'
        conta = f"passe-partout {mg:g}: externo {Ro:g} → janela {R:g} → filete {max(0, Ro - fi):g}"
    el = elemento(w, h, corpo_svg, nome or f"moldura {tipo}", FAM,
                  css=f".el{{border-radius:{(R + f.unidade * 1.5) if tipo == 'passe' else R:g}px}} /* {conta} */",
                  nota=f"enquadra 1 coisa (foto, dado, tela); {conta}")
    return el


def aba_pendurada(f, txt="20H30 · NOITE 1", cor=None, tinta=None, w=None, alt=None, invertida=False,
                  com_fio=True, nome=None):
    """Etiqueta pendurada (entalhe do gsaweb, proporções 1,06 × altura no ombro): data/local no topo de uma tela."""
    cor = cor or f.acento
    tinta = tinta or f.sobre_acento
    capx = 25.0
    alt = alt or capx + 2 * f.unidade * 0.9
    tw = larg_rotulo(f, txt, capx, f.fonte_mono, 0.06)
    base = tw + 2 * f.unidade * 1.2
    s = alt * 1.06
    w = w or base + 2 * s
    fio = f.traco * 2 if com_fio else 0
    H = alt + fio
    d = p_aba_pendurada(0, fio, w, alt)
    forma = ""
    if com_fio:
        forma += f'<rect x="0" y="0" width="{w:.2f}" height="{fio + 0.5:.2f}" fill="{cor}"/>'
    forma += f'<path d="{d}" fill="{cor}"/>'
    if invertida:     # sobe da base: espelho vertical só da forma; o texto continua de pé
        forma = f'<g transform="matrix(1 0 0 -1 0 {H:.2f})">{forma}</g>'
    cy = (H - fio - alt / 2) if invertida else (fio + alt / 2)
    t, _ = rotulo(f, txt, w / 2, cy, tinta, capx, f.fonte_mono, 0.06, "middle")
    corpo_svg = forma + t
    return elemento(w, H, corpo_svg, nome or ("aba pendurada" + (" invertida (sobe da base)" if invertida else "")),
                    FAM, css=f".aba{{clip-path:path('{p_aba_pendurada(0, 0, w, alt)}')}}",
                    nota=("sobe da base: rótulo de rodapé/tela (acima de y 1248 no 9:16)" if invertida else
                          "data/local pendurado no topo (fora de y<240 no 9:16)") + "; ombro côncavo = 1,06 × altura")


def _seta_diag(cx, cy, tam, cor, sw, ang=-45.0, limpa=False):
    """Seta ↗ desenhada (haste + ponta a 90°), pontas retas — para o botão do recorte.
    limpa=True: haste com ponta CEGA (butt) terminando no vértice — sem o "toco" que a ponta quadrada da haste
    deixava saindo da quina da seta (D15). Padrão False = desenho antigo (outros módulos usam)."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    x0, y0 = cx - ux * tam / 2, cy - uy * tam / 2
    x1, y1 = cx + ux * tam / 2, cy + uy * tam / 2
    ph = tam * 0.48
    pts = []
    for da in (135, -135):
        b = a + math.radians(da)
        pts.append((x1 + math.cos(b) * ph, y1 + math.sin(b) * ph))
    if limpa:
        return (f'<path d="M{x0:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}" fill="none" stroke="{cor}" stroke-width="{sw:.2f}" '
                f'stroke-linecap="butt"/>'
                f'<path d="M{pts[0][0]:.2f} {pts[0][1]:.2f}L{x1:.2f} {y1:.2f}L{pts[1][0]:.2f} {pts[1][1]:.2f}" '
                f'fill="none" stroke="{cor}" stroke-width="{sw:.2f}" stroke-linecap="square" stroke-linejoin="miter"/>')
    return (f'<path d="M{x0:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}M{pts[0][0]:.2f} {pts[0][1]:.2f}L{x1:.2f} {y1:.2f}'
            f'L{pts[1][0]:.2f} {pts[1][1]:.2f}" fill="none" stroke="{cor}" stroke-width="{sw:.2f}" '
            f'stroke-linecap="square" stroke-linejoin="miter"/>')


def recorte_botao(f, w=440, h=300, corte=104, r=None, cor=None, botao=None, estilo="cheio", canto="td", nome=None):
    """Cartão com recorte de canto + botão redondo encaixado (espaço = folga constante em volta)."""
    r = f.raio if r is None else r
    cor = cor or f.tinta
    botao = botao or f.acento
    gap = f.unidade / 2
    cx = w - corte / 2 if canto in ("td", "bd") else corte / 2
    cy = corte / 2 if canto in ("td", "te") else h - corte / 2
    br = corte / 2 - gap / 2
    seta = _seta_diag(cx + 0.0, cy, br * 0.78, f.sobre_acento, f.traco * 1.6,
                      -45 if canto in ("td",) else (-135 if canto == "te" else (45 if canto == "bd" else 135)),
                      limpa=True)
    conteudo = f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{br:.2f}" fill="{botao}"/>' + seta
    el = conteiner(f, w, h, "recorte", r, estilo, cor=cor, corte=corte, canto=canto, conteudo=conteudo,
                   nome=nome or f"recorte de canto + botão · raio {r:g}",
                   nota="raio invertido: o botão encaixa no canto; encaixe concêntrico ao botão = folga constante de ¼ U em volta")
    return el


def janela(f, w=440, h=300, r=None, estilo="barra", titulo="NOITE 1", direita="20H30", nome=None):
    """Bloco "janela" com barra de título (prova de produto por dentro; sem os 3 botões de sistema operacional)."""
    r = f.raio if r is None else r
    t = f.traco
    capx = 18.0
    bh = capx + f.unidade * 1.3
    c = f.tinta
    s = ""
    # a barra é a FAIXA DE CIMA da própria janela (recorte pela forma da janela): mesmo raio, mesma curva —
    # (antes: retângulo com cantos [r, r, 0, 0] numa barra mais baixa que 2r → o raio encolhia e a barra
    # escapava do canto da janela)
    cid = uid("janela", w, h, r, bh)
    defs = f'<clipPath id="{cid}"><path d="{p_cantos(0, 0, w, h, r)}"/></clipPath>'
    barra_ = lambda cor: f'<rect x="0" y="0" width="{w:.2f}" height="{bh:.2f}" fill="{cor}" clip-path="url(#{cid})"/>'
    if estilo == "barra":
        s += f'<path d="{p_cantos(0, 0, w, h, r, t / 2)}" {_attrs("none", c, t)}/>'
        s += barra_(c)
        fg = f.fundo
    elif estilo == "acento":
        s += f'<path d="{p_cantos(0, 0, w, h, r)}" fill="{mistura(f.fundo, f.tinta, 0.10)}"/>'
        s += barra_(f.acento)
        fg = f.sobre_acento
    else:   # contorno + fio
        s += f'<path d="{p_cantos(0, 0, w, h, r, t / 2)}" {_attrs("none", c, t)}/>'
        s += f'<line x1="0" y1="{bh:.2f}" x2="{w}" y2="{bh:.2f}" stroke="{c}" stroke-width="{t:.2f}"/>'
        fg = c
    pad = max(r, f.unidade * 0.75)
    a, _ = rotulo(f, titulo, pad, bh / 2, fg, capx, f.fonte_mono, 0.06)
    b, _ = rotulo(f, direita, w - pad, bh / 2, fg, capx, f.fonte_mono, 0.06, "end")
    s += a + b
    return elemento(w, h, s, nome or f"janela · {estilo}", FAM, defs=defs,
                    css=f".janela{{border-radius:{r:g}px;overflow:hidden}}.janela>header{{height:{bh:g}px}}",
                    nota="mostra o produto por dentro (aula, plataforma); a barra informa (nome · hora), nunca ✕ ▶")


def tela(f, tipo="monitor", estilo="cheio", nome=None):
    """Telas com raios concêntricos (moldura → tela = raio − borda): monitor de laboratório e celular."""
    t = f.traco
    if tipo == "monitor":
        w, hs = 440.0, 270.0
        R, b = f.raio_lg, round(f.unidade * 0.5)          # corpo = moldura (lg); tela = corpo − borda
        pe_h, pe_w = 40.0, 140.0
        H = hs + pe_h + 10
        corpo_ = p_cantos(0, 0, w, hs, R)
        scr = p_cantos(0, 0, w, hs, R, b)
        pe = (f'M{w / 2 - 30:.2f} {hs:.2f}L{w / 2 + 30:.2f} {hs:.2f}L{w / 2 + 38:.2f} {hs + pe_h:.2f}'
              f'L{w / 2 - 38:.2f} {hs + pe_h:.2f}Z')
        # no contorno o pé é SÓ as 2 laterais (do fio do corpo ao fio da base): sem fio de cima/baixo dobrado
        # encostando no corpo e na base (dava linha dupla de 1 px de vão)
        pe_aberto = (f'M{w / 2 - 30:.2f} {hs - t / 2:.2f}L{w / 2 - 38 + 0.2 * t:.2f} {hs + pe_h - 1 + t / 2:.2f}'
                     f'M{w / 2 + 30:.2f} {hs - t / 2:.2f}L{w / 2 + 38 - 0.2 * t:.2f} {hs + pe_h - 1 + t / 2:.2f}')
        base_ = p_cantos(w / 2 - pe_w / 2, hs + pe_h - 1, pe_w, 11, 5.5)
        base_c = p_cantos(w / 2 - pe_w / 2, hs + pe_h - 1, pe_w, 11, 5.5, t / 2)
        conta = f"moldura {R:g} − borda {b:g} = tela {R - b:g}"
    else:   # celular
        w, hs = 170.0, 350.0
        R, b = f.raio, round(f.unidade * 0.38)             # corpo = cartão (md); tela = corpo − borda
        H = hs
        corpo_ = p_cantos(0, 0, w, hs, R)
        scr = p_cantos(0, 0, w, hs, R, b)
        conta = f"corpo {R:g} − borda {b:g} = tela {R - b:g}"
    s = ""
    if estilo == "cheio":
        s += f'<path d="{corpo_}{scr}" fill="{f.tinta}" fill-rule="evenodd"/>'
        s += f'<path d="{scr}" fill="{mistura(f.fundo, f.tinta, 0.07)}"/>'
        if tipo == "monitor":
            s += f'<path d="{pe}" fill="{mistura(f.fundo, f.tinta, 0.7)}"/><path d="{base_}" fill="{f.tinta}"/>'
        else:
            s += f'<path d="{p_cantos(w / 2 - 25, b + 9, 50, 15, 7.5)}" fill="{f.fundo}"/>'
    else:
        s += f'<path d="{p_cantos(0, 0, w, hs, R, t / 2)}" {_attrs("none", f.tinta, t)}/>'
        s += f'<path d="{p_cantos(0, 0, w, hs, R, b)}" {_attrs("none", f.acento, t)}/>'
        if tipo == "monitor":
            s += (f'<path d="{pe_aberto}" fill="none" stroke="{f.tinta}" stroke-width="{t:.2f}" stroke-linecap="butt"/>'
                  f'<path d="{base_c}" {_attrs("none", f.tinta, t)}/>')
        else:
            s += f'<path d="{p_cantos(w / 2 - 25, b + 9, 50, 15, 7.5)}" fill="{f.tinta}"/>'
    m = t
    s = f'<g transform="translate({m:.2f} {m:.2f})">{s}</g>'
    return elemento(w + 2 * m, H + 2 * m, s, nome or f"{tipo} · {estilo}", FAM,
                    css=f".tela{{border-radius:{R:g}px;padding:{b:g}px}}.tela>*{{border-radius:{R - b:g}px}}",
                    nota=f"prova visual (aula, app, dado) dentro de um objeto; {conta}")


# =====================================================================================================================
# amostras do catálogo
# =====================================================================================================================
@amostra(FAM, "raios 0 · md · lg")
def _a_raios(f):
    """A escala de forma (references/forma.md): 0 (vivo) · raio (md, cartão) · raio_lg (lg, moldura)."""
    out = []
    escala = ((0, "raio 0 (vivo)"), (f.raio, f"raio {f.raio:g} (md · cartão)"),
              (f.raio_lg, f"raio {f.raio_lg:g} (lg · moldura)"))
    for r, rot in escala:
        out.append(conteiner(f, 420, 270, r=r, estilo="cheio", nome=f"cheio · {rot}",
                             nota="respiro interno ≥ raio (F13); 1 valor da escala por peça"))
    for r, rot in escala:
        out.append(conteiner(f, 420, 270, r=r, estilo="contorno", nome=f"contorno · {rot}",
                             nota=f"fio = traço da ficha ({f.traco:g} px), centrado por dentro"))
    for r, rot in escala:
        out.append(conteiner(f, 420, 270, r=r, estilo="duplo", linha=f.acento if r else f.tinta,
                             nome=f"contorno duplo · {rot}",
                             nota="interno = externo − (traço + folga); com raio 0 os dois ficam retos"))
    return out


@amostra(FAM, "reto + arredondado")
def _a_combos(f):
    L = f.raio_lg
    fc = claro(f)
    out = [
        conteiner(f, 420, 270, cantos=[0, 0, L, 0], nome=f"1 canto curvo (lg {L:g})",
                  nota="3 cantos retos + 1 curvo: direção de leitura para baixo-direita"),
        conteiner(f, 420, 270, cantos=[135, 0, 135, 0], cor=f.tinta, nome="folha (2 cantos pílula)",
                  nota="2 cantos opostos em pílula (½ do lado menor): reto + arredondado na mesma forma"),
        conteiner(f, 420, 270, cantos=[L, L, 0, 0], estilo="contorno", linha=f.acento, nome="topo arredondado · base reta",
                  nota="aba/arco: assenta numa linha de base (rodapé, régua, chão)"),
        conteiner(f, 420, 150, cantos=[75, 0, 0, 75], nome="meia-pílula + reto",
                  nota="ponta de pílula de um lado só: etiqueta que 'sai' de uma borda"),
        conteiner(f, 420, 270, cantos=[("c", L), ("r", L), ("c", L), ("r", L)], cor=f.tinta,
                  nome="chanfro + raio alternados", nota=f"corner-shape: bevel round bevel round (os dois {L:g})"),
        no_claro(conteiner(fc, 420, 270, cantos=[("i", L), 0, ("i", L), 0], cor=fc.tinta,
                           nome="côncavo (scoop) + reto · papel", nota="corner-shape: scoop; cara de ingresso/placa")),
    ]
    return out


@amostra(FAM, "squircle · chanfro · degrau")
def _a_cantos(f):
    L = f.raio_lg
    out = [
        conteiner(f, 300, 300, cantos=[("s", 150)] * 4, nome="squircle inteiro (superelipse n=4)",
                  nota="superelipse inteira (corner-shape: squircle; raio = ½ lado): ícone/selo de app. "
                       "Squircle com raio da escala (16–44) não se distingue do redondo: não usar"),
        conteiner(f, 420, 270, cantos=[("c", L)] * 4, cor=f.tinta, nome=f"chanfro {L:g} (bevel)",
                  nota="45°: placa industrial, etiqueta técnica"),
        conteiner(f, 420, 270, cantos=[("c", L), 0, ("c", L), 0], estilo="contorno",
                  linha=f.acento, nome="chanfro em 2 cantos", nota="diagonal: movimento sem inclinar a caixa"),
        conteiner(f, 420, 270, cantos=[("n", f.raio)] * 4, nome=f"degrau {f.raio:g} (notch)",
                  nota="corner-shape: notch; cantos 'mordidos' = selo/medalha retangular"),
        conteiner(f, 420, 270, cantos=[("i", L)] * 4, estilo="contorno", nome="côncavo nos 4 (scoop)",
                  nota="placa de rua / cartela; raio côncavo cresce no contorno (s + d)"),
    ]
    return out


@amostra(FAM, "pasta (ficha)")
def _a_pasta(f):
    fc = claro(f)
    lab = "PÓS-GRADUAÇÃO"
    capx = 18.0
    tw = larg_rotulo(f, lab, capx, f.fonte_texto, 0.08)

    def pad(r):        # respiro do rótulo na aba ≥ raio do canto (F13); com raio 0, ¾ U
        return max(r, f.unidade * 0.75)

    def aba(w, r):     # largura da aba (fração) = rótulo + respiro dos dois lados (antes da curva)
        return (tw + 2 * pad(r)) / w

    def com_rotulo(ff, w, alt, cor_txt, r, lado="esq"):
        x = pad(r) if lado == "esq" else w - pad(r)
        t, _ = rotulo(ff, lab, x, alt / 2, cor_txt, capx, ff.fonte_texto, 0.08, "start" if lado == "esq" else "end")
        return t
    W, H, A = 440, 300, 50
    r, L = f.raio, f.raio_lg
    out = [
        conteiner(f, W, H, "pasta", r=r, aba=aba(W, r), alt=A, nome=f"pasta · raio {r:g}",
                  conteudo=com_rotulo(f, W, A, f.sobre_acento, r),
                  nota="ficha/dossiê/avaliação (nunca promoção); aba = rótulo + respiro ≥ raio; curva-S do gsaweb"),
        conteiner(f, W, H, "pasta", r=0, aba=aba(W, 0), alt=A, cor=f.tinta, nome="pasta · raio 0",
                  conteudo=com_rotulo(f, W, A, f.fundo, 0), nota="aba reta + curva: arquivo técnico"),
        conteiner(f, W, H, "pasta", r=L, aba=aba(W, L), alt=A, estilo="contorno", lado="dir",
                  nome=f"pasta · raio {L:g} · aba à direita",
                  conteudo=com_rotulo(f, W, A, f.tinta, L, "dir"), nota="espelhada; contorno = traço da ficha"),
        conteiner(f, W, H, "pasta", r=r, aba=0.30, alt=36, estilo="duplo", linha=f.acento,
                  nome="pasta · contorno duplo", nota="aba baixa (36) sem rótulo: divisória discreta"),
        no_claro(conteiner(fc, W, H, "pasta", r=r, aba=aba(W, r), alt=A, cor=fc.tinta, nome="pasta · papel",
                           conteudo=com_rotulo(fc, W, A, fc.papel, r),
                           nota="sobre papel; sombra (se houver) = drop-shadow no pai")),
    ]
    return out


@amostra(FAM, "entalhe")
def _a_entalhe(f):
    out = [
        conteiner(f, 440, 300, "entalhe", r=f.raio, boca=0.34, fundo=44, nome="cartão com entalhe no topo",
                  nota="o negativo da aba pendurada: o rótulo 'encaixa' no vão"),
        conteiner(f, 440, 300, "entalhe", r=f.raio_lg, boca=0.34, fundo=44, estilo="contorno",
                  nome=f"entalhe · contorno · raio {f.raio_lg:g}", nota="ombros côncavos com as alças do gsaweb"),
        aba_pendurada(f),
        aba_pendurada(f, "AO VIVO", cor=f.tinta, tinta=f.fundo, invertida=True),
    ]
    return out


@amostra(FAM, "recorte de canto")
def _a_recorte(f):
    fc = claro(f)
    return [
        recorte_botao(f, r=f.raio),
        recorte_botao(f, r=f.raio_lg, estilo="contorno", canto="bd",
                      nome=f"recorte embaixo · contorno · raio {f.raio_lg:g}"),
        recorte_botao(f, r=0, cor=f.acento, botao=f.tinta, nome="recorte · raio 0"),
        no_claro(recorte_botao(fc, r=f.raio, cor=fc.tinta, botao=fc.acento, canto="te", nome="recorte à esquerda · papel")),
    ]


@amostra(FAM, "ingresso")
def _a_ingresso(f):
    capx = 25.0
    can = 0.24

    def txt(ff, w, h, cor, vertical=False):
        if vertical:       # canhoto embaixo: título no corpo, hora no canhoto (deitada, como em ingresso real)
            sy = h * (1 - can)
            a, _ = rotulo(ff, "NOITE 1", w / 2, sy / 2, cor, capx * 1.5, ff.fonte_display, 0.02, "middle")
            b, _ = rotulo(ff, "20H30", w / 2, sy + (h - sy) / 2, cor, 18, ff.fonte_mono, 0.04, "middle")
            return a + b
        sx = w * (1 - can)
        a, _ = rotulo(ff, "NOITE 1", max(ff.raio, ff.unidade * 1.2), h / 2, cor, capx * 1.6, ff.fonte_display, 0.02)
        b, _ = rotulo(ff, "20H30", 0, 0, cor, 18, ff.fonte_mono, 0.04, "middle")
        return a + f'<g transform="translate({sx + (w - sx) / 2:.2f} {h / 2:.2f}) rotate(-90)">{b}</g>'
    fc = claro(f)
    return [
        conteiner(f, 460, 200, "ingresso", r=f.raio, canhoto=can, conteudo=txt(f, 460, 200, f.sobre_acento),
                  nome="ingresso · cheio",
                  nota="vaga/noite; canhoto 24% com a hora deitada; furos de 7 px a cada 14 px (2× o diâmetro)"),
        conteiner(f, 460, 200, "ingresso", r=0, canhoto=can, estilo="contorno", conteudo=txt(f, 460, 200, f.tinta),
                  nome="ingresso · contorno · raio 0",
                  nota="no contorno o picote vira tracejado (traço inteiro nas pontas, longe da meia-lua)"),
        conteiner(f, 200, 350, "ingresso", r=f.raio_lg, canhoto=can, vertical=True, cor=f.tinta,
                  conteudo=txt(f, 200, 350, f.fundo, True), nome=f"ingresso vertical · raio {f.raio_lg:g}",
                  nota="canhoto embaixo: pilha de ingressos, story"),
        no_claro(conteiner(fc, 460, 200, "ingresso", r=f.raio, canhoto=can, estilo="duplo", linha=fc.tinta,
                           conteudo=txt(fc, 460, 200, fc.tinta), nome="ingresso · contorno duplo · papel",
                           nota="borda dupla de bilhete impresso; meia-lua de dentro concêntrica; picote abaixo da meia-lua")),
    ]


@amostra(FAM, "molduras concêntricas")
def _a_molduras(f):
    return [moldura(f, 420, 280, "dupla"), moldura(f, 420, 280, "aninhada"), moldura(f, 420, 280, "tripla"),
            moldura(f, 420, 280, "passe")]


@amostra(FAM, "balões")
def _a_baloes(f):
    fc = claro(f)
    return [
        conteiner(f, 420, 230, "balao", r=f.raio, cauda="esq", nome="balão · canto vivo à esquerda",
                  nota="só para fala de verdade (depoimento, pergunta); ≤ 3 linhas"),
        conteiner(f, 420, 230, "balao", r=f.raio_lg, cauda="dir", estilo="contorno",
                  nome=f"balão · direita · contorno · raio {f.raio_lg:g}",
                  nota="espelhado = a outra pessoa da conversa"),
        conteiner(f, 420, 170, "balao", r=(170 - 34) / 2, cauda="centro", cor=f.tinta, nome="balão-pílula · cauda central",
                  nota="pílula (raio = ½ altura) + cauda: reação curta, 1 linha"),
        no_claro(conteiner(fc, 420, 230, "balao", r=0, cauda="esq", cor=fc.tinta, nome="balão reto · papel",
                           nota="raio 0: voz seca, de documento")),
    ]


def _cordao(hx, hy, m, cor, sw, vertical=False):
    """Cordão em laço: 2 fios saem do ilhós e se juntam num nó DENTRO da caixa (+ ponta curta) — nunca corta no ar."""
    def P(x, y):
        return (y, x) if vertical else (x, y)
    kx, ky = hx - m * 0.62 - 40, hy - m * 0.55 - 14   # nó: longe da borda chanfrada (≥ 20 px, nunca tangente)
    ds = []
    for dy in (-3.0, 3.0):
        p0 = P(hx, hy + dy)
        c1 = P(hx - 30, hy + dy * 4)
        c2 = P(kx + 18, ky + 14 + dy * 3)
        p3 = P(kx, ky)
        ds.append(f"M{p0[0]:.2f} {p0[1]:.2f}C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p3[0]:.2f} {p3[1]:.2f}")
    t0, q, t1 = P(kx, ky), P(kx - 2, ky - 12), P(kx - 16, ky - 14)
    ds.append(f"M{t0[0]:.2f} {t0[1]:.2f}Q{q[0]:.2f} {q[1]:.2f} {t1[0]:.2f} {t1[1]:.2f}")
    no = P(kx, ky)
    return (f'<path d="{"".join(ds)}" fill="none" stroke="{cor}" stroke-width="{sw:.2f}" stroke-linecap="round"/>'
            f'<circle cx="{no[0]:.2f}" cy="{no[1]:.2f}" r="{sw * 1.3:.2f}" fill="{cor}"/>')


@amostra(FAM, "etiquetas")
def _a_etiquetas(f):
    def tag(ff, w, h, estilo, cor, txt_cor, vertical=False, nome="", r=None, rot="NOITE 1"):
        rr = ff.raio if r is None else r
        (cx, cy), fr = centro_furo_etiqueta(0, 0, w, h, vertical=vertical)
        m = 64.0
        hx, hy = (cx + m, cy + m)
        anel = (f'<circle cx="{hx:.2f}" cy="{hy:.2f}" r="{fr + ff.traco * 1.3:.2f}" fill="none" '
                f'stroke="{ff.apoio}" stroke-width="{ff.traco:.2f}"/>')
        capx = 25 * 1.3
        if vertical:
            # respiro lateral do rótulo ≥ raio (F13): a maiúscula encolhe até caber em w − 2·raio
            lw = larg_rotulo(ff, rot, capx, ff.fonte_display, 0.02)
            capx = min(capx, capx * (w - 2 * max(rr, ff.unidade)) / lw)
            a, _ = rotulo(ff, rot, m + w / 2, m + h * 0.62, txt_cor, capx, ff.fonte_display, 0.02, "middle")
            cord = _cordao(hy, hx, m, ff.apoio, ff.traco, True)
        else:
            a, _ = rotulo(ff, rot, m + h * 0.30 + fr * 2.4 + ff.unidade * 0.9, m + h / 2, txt_cor, capx,
                          ff.fonte_display, 0.02)
            cord = _cordao(hx, hy, m, ff.apoio, ff.traco)
        el = conteiner(ff, w, h, "etiqueta", r=rr, estilo=estilo, cor=cor, vertical=vertical,
                       margem=m, conteudo=anel + a + cord, nome=nome,
                       nota="etiqueta de bagagem/arquivo: ilhós com anel, cordão com nó fora da etiqueta; ponta chanfrada")
        el.caixa = (0, 0, m + w, m + h)
        return el
    fc = claro(f)
    return [
        tag(f, 330, 150, "cheio", f.acento, f.sobre_acento, nome="etiqueta de bagagem · cheia"),
        tag(f, 330, 150, "contorno", f.tinta, f.tinta, nome="etiqueta · contorno · raio 0", r=0),
        no_claro(tag(fc, 140, 240, "cheio", fc.tinta, fc.papel, vertical=True, nome="etiqueta vertical · papel",
                     rot="20H30")),
    ]


@amostra(FAM, "aba lateral")
def _a_aba(f):
    def lab(ff, w, h, cor, r, pos=0.16, aba_c=None, aba_l=48):
        py, ac = aba_lugar(h, r, pos, aba_c)          # o MESMO lugar que a geometria usa (aba presa ≥ 2 raios)
        cx, cy = w - aba_l / 2, py + ac / 2
        t, _ = rotulo(ff, "01", 0, 0, cor, 22, ff.fonte_mono, 0.04, "middle")
        return f'<g transform="translate({cx:.2f} {cy:.2f}) rotate(90)">{t}</g>'
    fc = claro(f)
    r = f.raio
    al = 2 * r            # a aba sai 2 raios: concordância côncava (r) + canto da aba (r) sem se atropelar
    return [
        conteiner(f, 440, 300, "aba", r=r, aba_l=al, pos=0.2, conteudo=lab(f, 440, 300, f.sobre_acento, r, 0.2, aba_l=al),
                  nome="aba lateral (divisória)",
                  nota=f"seção numerada de fichário; aba sai 2 × raio ({al:g}): côncava {r:g} + canto {r:g}"),
        conteiner(f, 440, 300, "aba", r=r, aba_l=al, pos=0.45, estilo="contorno",
                  conteudo=lab(f, 440, 300, f.tinta, r, 0.45, aba_l=al), nome=f"aba lateral · contorno · raio {r:g}",
                  nota="aba na 2ª posição: sequência 01/02/03 descendo"),
        no_claro(conteiner(fc, 440, 300, "aba", r=0, aba_l=48, cor=fc.tinta,
                           conteudo=lab(fc, 440, 300, fc.papel, 0, aba_l=48),
                           nome="aba lateral · raio 0 · papel", nota="reta: fichário técnico")),
    ]


@amostra(FAM, "janelas")
def _a_janelas(f):
    return [janela(f, estilo="barra"),
            janela(f, estilo="acento", r=f.raio_lg, nome=f"janela · acento · raio {f.raio_lg:g}"),
            janela(f, estilo="fio", r=0, nome="janela · fio · raio 0")]


@amostra(FAM, "telas")
def _a_telas(f):
    return [tela(f, "monitor", "cheio"), tela(f, "monitor", "contorno"), tela(f, "celular", "cheio"),
            tela(f, "celular", "contorno")]
