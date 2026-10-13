"""ornamentos.profundidade — família PROFUNDIDADE E SOMBRA (descolar, empilhar, dar peso).

Origem (references/elementos.md "Sombra dura", "Sombra de papel", "Adesivo"; pesquisa 11 E43, E69–E71; 14b §3.5;
13 #24–25):
  - sombra dura: cor sólida, deslocada SEM desfoque, borda de 2 px; 3–4% do lado menor do objeto; SEMPRE para o mesmo
    lado (direita-baixo = luz de cima-esquerda); mesma cor e deslocamento na série; nunca misturar com sombra suave;
  - sombra de papel (suave): 2–6 px, desfoque 0–6, 15–30% de preto, 1 receita só;
  - adesivo: borda branca 1,5–3% do lado, sombra 2–4 px a 20–30%;
  - extrusão: profundidade 8–20% da altura, 1 direção de luz;
  - relevo: filtro SVG em sRGB, região ampliada; tom sobre tom (o relevo É a cor do fundo);
  - botão neo-brutal: SÓ exemplo de site (clicável); fora de saúde/finanças como pacote inteiro.
"""
import math

from .nucleo import amostra, elemento, filtro
from .formas import (rotulo, larg_rotulo, mistura, claro, no_claro, corpo, caixa_texto, path_texto, p_cantos, uid,
                     p_ingresso)
from .selos import pontos_estrela, centro_tinta

FAM = "profundidade"


# =====================================================================================================================
# utilitários
# =====================================================================================================================
def _texto_d(f, s, capx, spec=None, tracking=0.02):
    """d do texto com a TINTA começando em (0, 0). Devolve (d, largura, altura)."""
    spec = spec or f.fonte_display
    sz = corpo(spec, capx)
    x0, y0, x1, y1 = caixa_texto(spec, s, sz, 0, 0, tracking)
    d, _ = path_texto(spec, s, sz, -x0, -y0, tracking)
    return d, x1 - x0, y1 - y0


def _dir(ang):
    a = math.radians(ang)
    return math.cos(a), math.sin(a)


def sombra_papel(id_, dx=2, dy=4, desf=3, op=0.25):
    """A receita ÚNICA de sombra de papel (token --sombra)."""
    return filtro(id_, f'<feDropShadow dx="{dx}" dy="{dy}" stdDeviation="{desf}" flood-color="#000" flood-opacity="{op}"/>')


def _rastro(id_, n, ux, uy, passo=1.0, cor=None):
    """Repete <use href=#id_> n vezes ao longo de (ux, uy): sombra longa / extrusão sem dependência."""
    return "".join(f'<use href="#{id_}" x="{ux * k * passo:.2f}" y="{uy * k * passo:.2f}"/>' for k in range(n, 0, -1))


# =====================================================================================================================
# sombra dura
# =====================================================================================================================
def sombra_dura(f, alvo="cartao", r=None, dist=None, ang=45.0, claro_=False, nome=None):
    """Sombra dura (neo-brutal de tempero): o mesmo contorno deslocado, sem desfoque, borda de 2 px."""
    ff = claro(f) if claro_ else f
    r = ff.raio if r is None else r
    b = 2.0
    s = ""
    if alvo == "cartao":
        w, h = 360.0, 230.0
        dist = dist or round(min(w, h) * 0.035)
        ux, uy = _dir(ang)
        dx, dy = ux * dist * math.sqrt(2), uy * dist * math.sqrt(2)
        linha = ff.tinta                               # escuro: borda clara · papel: borda escura
        somb = ff.tinta if claro_ else ff.acento       # papel: sombra escura (gsaweb) · escuro: sombra no acento
        fundo_c = f.tinta if claro_ else ff.fundo      # papel: cartão branco · escuro: cartão do fundo
        s += f'<path d="{p_cantos(dx, dy, w, h, r)}" fill="{somb}"/>'
        s += f'<path d="{p_cantos(0, 0, w, h, r, b / 2)}" fill="{fundo_c}" stroke="{linha}" stroke-width="{b}"/>'
        a, _ = rotulo(ff, "NOITE 1", 26, 40, linha, 18, ff.fonte_mono, 0.06)
        s += a + f'<line x1="26" y1="64" x2="{w - 26:.2f}" y2="64" stroke="{linha}" stroke-width="{b}"/>'
        c, _ = rotulo(ff, "AO VIVO", 26, h - 52, linha, 44, ff.fonte_display, 0.02)
        s += c
        W, H = w + dx, h + dy
        nota = f"deslocamento {dist:g} px (3,5% do lado menor) para direita-baixo; borda 2 px; raio {r:g}"
    elif alvo == "pilula":
        capx = 25.0
        tw = larg_rotulo(ff, "20H30", capx, ff.fonte_mono, 0.04)
        h = capx + 2 * 18
        w = tw + 2 * capx
        dist = dist or 4.0
        dx = dy = dist
        s += f'<path d="{p_cantos(dx, dy, w, h, h / 2)}" fill="{ff.tinta}"/>'
        s += f'<path d="{p_cantos(0, 0, w, h, h / 2, b / 2)}" fill="{ff.acento}" stroke="{ff.tinta}" stroke-width="{b}"/>'
        a, _ = rotulo(ff, "20H30", w / 2, h / 2, ff.sobre_acento, capx, ff.fonte_mono, 0.04, "middle")
        s += a
        W, H = w + dx, h + dy
        nota = "rótulo 'colado': pílula + sombra dura de 4 px na cor da tinta"
    elif alvo == "circulo":
        R = 100.0
        dist = dist or 7.0
        s += f'<circle cx="{R + dist:.2f}" cy="{R + dist:.2f}" r="{R:.2f}" fill="{ff.tinta}"/>'
        s += f'<circle cx="{R:.2f}" cy="{R:.2f}" r="{R - b / 2:.2f}" fill="{ff.acento}" stroke="{ff.tinta}" stroke-width="{b}"/>'
        s += centro_tinta(ff.fonte_display, "3", corpo(ff.fonte_display, 110), R, R, ff.sobre_acento)
        W = H = 2 * R + dist
        nota = "disco + sombra dura (3,5% do diâmetro): número de etapa que 'salta'"
    else:   # texto
        d, tw, th = _texto_d(ff, "AO VIVO", 92)
        dist = dist or round(th * 0.06)
        s += f'<path transform="translate({dist:.2f} {dist:.2f})" d="{d}" fill="{ff.acento}"/>'
        s += f'<path d="{d}" fill="{ff.tinta}"/>'
        W, H = tw + dist, th + dist
        nota = f"texto com sombra dura no acento ({dist:g} px = 6% da altura da letra), sem desfoque"
    el = elemento(W, H, s, nome or f"sombra dura · {alvo}" + (" · papel" if claro_ else ""), FAM,
                  css=f".duro{{border:2px solid currentColor;box-shadow:{dist:g}px {dist:g}px 0 currentColor}}",
                  nota=nota)
    return no_claro(el) if claro_ else el


# =====================================================================================================================
# sombra longa e extrusão (rastro de cópias)
# =====================================================================================================================
def sombra_longa(f, alvo="numeral", ang=45.0, comp=None, esvai=False, nome=None):
    """Sombra longa a 45° (rastro do contorno até a borda do ladrilho); tom 1 passo acima do fundo."""
    t = f.traco
    W = H = 320.0
    R = f.raio_lg
    pid = uid("longa", alvo, ang, esvai, f.acento)
    ux, uy = _dir(ang)
    comp = comp or 260
    tile = mistura(f.fundo, f.tinta, 0.10)
    somb = mistura(f.fundo, f.tinta, 0.04)
    defs = ""
    if alvo == "numeral":
        d, gw, gh = _texto_d(f, "3", 190)
        tx, ty = (W - gw) / 2 - 18, (H - gh) / 2 - 18
        forma = f'<path id="{pid}" transform="translate({tx:.2f} {ty:.2f})" d="{d}"/>'
        frente = f'<path transform="translate({tx:.2f} {ty:.2f})" d="{d}" fill="{f.acento}"/>'
    elif alvo == "selo":
        cx = cy = W / 2 - 22
        rr = 92.0
        forma = f'<circle id="{pid}" cx="{cx:.2f}" cy="{cy:.2f}" r="{rr:.2f}"/>'
        frente = f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rr:.2f}" fill="{f.tinta}"/>' + \
            centro_tinta(f.fonte_display, "AO", corpo(f.fonte_display, 52), cx, cy - 26, f.fundo) + \
            centro_tinta(f.fonte_display, "VIVO", corpo(f.fonte_display, 52), cx, cy + 34, f.fundo)
    else:   # texto
        W, H = 460.0, 230.0
        d, tw, th = _texto_d(f, "20H30", 110)
        tx, ty = (W - tw) / 2 - 22, (H - th) / 2 - 22
        forma = f'<path id="{pid}" transform="translate({tx:.2f} {ty:.2f})" d="{d}"/>'
        # letra ESCURA sobre o ladrilho no acento (branco sobre dourado dava ~2:1 — D11); sombra = acento mais fundo
        frente = f'<path transform="translate({tx:.2f} {ty:.2f})" d="{d}" fill="{f.sobre_acento}"/>'
        tile = f.acento
        somb = mistura(f.acento, f.fundo, 0.30)
    cid = uid("tile", W, H, R)
    defs += f'<clipPath id="{cid}"><path d="{p_cantos(0, 0, W, H, R)}"/></clipPath>' + forma.replace("/>", "/>", 1)
    rastro = f'<g fill="{somb}">{_rastro(pid, int(comp), ux, uy)}</g>'
    if esvai:
        gid, mid = pid + "g", pid + "m"
        defs += (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0.25" stop-color="#fff"/>'
                 f'<stop offset="0.95" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                 f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                 f'<rect width="{W}" height="{H}" fill="url(#{gid})"/></mask>')
        rastro = f'<g mask="url(#{mid})">{rastro}</g>'
    s = f'<g clip-path="url(#{cid})"><path d="{p_cantos(0, 0, W, H, R)}" fill="{tile}"/>{rastro}{frente}</g>'
    return elemento(W, H, s, nome or f"sombra longa · {alvo}" + (" · esvai" if esvai else ""), FAM, defs=defs,
                    nota="sombra longa a 45°, tom 1 passo do ladrilho (baixo contraste)" + ("; esvai com a distância" if esvai else ""))


def extrusao(f, alvo="numeral", prof=None, ang=45.0, frente=None, lado=None, nome=None):
    """Extrusão sólida (bloco 3D chapado): rastro curto na cor do lado + face na frente; 1 direção de luz."""
    ux, uy = _dir(ang)
    frente = frente or f.tinta
    lado = lado or mistura(f.acento, f.fundo, 0.25)
    pid = uid("extr", alvo, ang, frente, lado)
    if alvo == "numeral":
        d, gw, gh = _texto_d(f, "1", 250)
        prof = prof or gh * 0.12
        forma = f'<path id="{pid}" d="{d}"/>'
        W, H = gw + prof * ux + 2, gh + prof * uy + 2
        face = f'<path d="{d}" fill="{frente}"/>'
    elif alvo == "texto":
        d, gw, gh = _texto_d(f, "AO VIVO", 96)
        prof = prof or gh * 0.16
        forma = f'<path id="{pid}" d="{d}"/>'
        W, H = gw + prof * ux + 2, gh + prof * uy + 2
        face = f'<path d="{d}" fill="{frente}"/>'
    else:   # pilula
        capx = 25.0
        tw = larg_rotulo(f, "AO VIVO", capx, f.fonte_texto, 0.12)
        h = capx + 36
        w = tw + 2 * capx
        prof = prof or 14.0
        dd = p_cantos(0, 0, w, h, h / 2)
        forma = f'<path id="{pid}" d="{dd}"/>'
        a, _ = rotulo(f, "AO VIVO", w / 2, h / 2, f.sobre_acento, capx, f.fonte_texto, 0.12, "middle")
        face = f'<path d="{dd}" fill="{frente}"/>' + a
        W, H = w + prof * ux + 1, h + prof * uy + 1
    s = f'<g fill="{lado}">{_rastro(pid, int(prof * 2), ux, uy, 0.5)}</g>' + face
    return elemento(W, H, s, nome or f"extrusão · {alvo}", FAM, defs=forma,
                    nota=f"profundidade {prof:.0f} px ({'12' if alvo == 'numeral' else '16'}% da altura), lado no tom escuro do acento")


def camadas(f, tipo="circulo", n=5, passo=None, nome=None):
    """Extrusão em CAMADAS: cópias separadas (contorno ou cheias alternadas) andando em degrau."""
    passo = passo or f.unidade * 0.42
    s = ""
    if tipo == "circulo":
        R = 110.0
        W = H = 2 * R + passo * (n - 1) + 4
        for k in range(n - 1, -1, -1):
            # só tons do acento escurecendo (as camadas na cor do fundo viravam "buraco" com fio — leitura confusa)
            c = f.acento if k == 0 else mistura(f.acento, f.fundo, 0.30 + 0.13 * k)
            s += (f'<circle cx="{R + 2 + k * passo:.2f}" cy="{R + 2 + k * passo:.2f}" r="{R:.2f}" fill="{c}" '
                  f'stroke="{f.tinta}" stroke-width="{f.traco * 0.67:.2f}"/>')
        s += centro_tinta(f.fonte_display, "3", corpo(f.fonte_display, 120), R + 2, R + 2, f.sobre_acento)
        nota = f"{n} discos em degrau de {passo:.0f} px, fio fino separa as camadas: papel cortado empilhado"
    else:   # cartões
        w, h = 300.0, 190.0
        W, H = w + passo * (n - 1) + 4, h + passo * (n - 1) + 4
        for k in range(n - 1, -1, -1):
            c = f.tinta if k == 0 else f.fundo
            s += (f'<path d="{p_cantos(2 + k * passo, 2 + k * passo, w, h, f.raio)}" fill="{c}" stroke="{f.tinta}" '
                  f'stroke-width="{f.traco * 0.67:.2f}"/>')
        a, _ = rotulo(f, "3 NOITES", 2 + 26, 2 + h - 50, f.fundo, 40, f.fonte_display, 0.02)
        s += a
        nota = f"pilha de {n} cartões em contorno, degrau {passo:.0f} px: 'tem mais embaixo'"
    return elemento(W, H, s, nome or f"camadas · {tipo}", FAM, nota=nota)


# =====================================================================================================================
# papel sobreposto, adesivo
# =====================================================================================================================
def papel(f, tipo="folhas", nome=None):
    """Papel sobreposto com UMA receita de sombra de papel (2/4 px, desfoque 3, 25%)."""
    fid = uid("papel", tipo, f.seed)
    defs = sombra_papel(fid)
    s = ""
    if tipo == "folhas":
        w, h = 250.0, 320.0
        W, H = 380.0, 380.0
        tons = [mistura(f.papel, f.fundo, 0.12), mistura(f.papel, f.fundo, 0.05), f.papel]
        for k, (a, c) in enumerate(zip((f.angulo * 1.3, -f.angulo * 0.8, 0), tons)):
            s += (f'<g transform="translate({W / 2:.2f} {H / 2:.2f}) rotate({a:.2f}) translate({-w / 2:.2f} {-h / 2:.2f})">'
                  f'<path d="{p_cantos(0, 0, w, h, f.raio_sm)}" fill="{c}" filter="url(#{fid})"/></g>')
        a, _ = rotulo(f, "NOITE 1", W / 2 - w / 2 + 28, H / 2 - h / 2 + 44, f.fundo, 25, f.fonte_mono, 0.04)
        s += a + (f'<line x1="{W / 2 - w / 2 + 28:.2f}" y1="{H / 2 - h / 2 + 74:.2f}" x2="{W / 2 + w / 2 - 28:.2f}" '
                  f'y2="{H / 2 - h / 2 + 74:.2f}" stroke="{f.fundo}" stroke-width="1.5"/>')
        nota = "3 folhas giradas (±ângulo da ficha), a de cima reta; tons do papel; 1 receita de sombra"
    elif tipo == "leque":
        w, h = 200.0, 280.0
        W, H = 380.0, 350.0
        cores = [f.tinta, f.acento, f.papel]
        for k, (a, c) in enumerate(zip((-14, -3, 9), cores)):
            # pivô deslocado (+9, -11) para a tinta ficar CENTRADA na caixa (antes: 31/30 de um lado e 50/8 do outro)
            s += (f'<g transform="translate({W / 2 + 9:.2f} {H - 41:.2f}) rotate({a:.2f}) translate({-w / 2:.2f} {-h:.2f})">'
                  f'<path d="{p_cantos(0, 0, w, h, f.raio)}" fill="{c}" filter="url(#{fid})"/></g>')
        nota = "3 cartões em leque girando na base: opções/módulos; raio da ficha"
    else:   # ingressos
        w, h = 300.0, 130.0
        W, H = 380.0, 300.0
        for k in range(3):
            a = f.angulo * (1 - k) * 0.9
            c = [mistura(f.acento, f.fundo, 0.35), mistura(f.acento, f.fundo, 0.15), f.acento][k]
            g = (f'<g transform="translate({W / 2 + (k - 1) * 14:.2f} {H / 2 + (k - 1) * 44:.2f}) rotate({a:.2f}) '
                 f'translate({-w / 2:.2f} {-h / 2:.2f})">'
                 f'<path d="{p_ingresso(0, 0, w, h, f.raio, 0, canhoto=0.26, entalhe=11, furo=3)}" fill="{c}" '
                 f'fill-rule="evenodd" filter="url(#{fid})"/>')
            a_, _ = rotulo(f, f"NOITE {3 - k}", 22, h / 2, f.sobre_acento, 34, f.fonte_display, 0.02)
            s += g + a_ + "</g>"
        nota = "3 ingressos (1 por noite) empilhados; o da frente no acento cheio"
    return elemento(W, H, s, nome or f"papel sobreposto · {tipo}", FAM, defs=defs, nota=nota)


def adesivo(f, tipo="texto", nome=None):
    """Adesivo: recorte com borda branca constante (2,5% do lado) + sombra curta (3 px, 25%)."""
    fid = uid("adesivo", tipo, f.seed)
    defs = sombra_papel(fid, 2, 3, 1.5, 0.3)
    branco = f.tinta
    s = ""
    if tipo == "texto":
        d, tw, th = _texto_d(f, "AO VIVO", 84)
        bw = max(10.0, tw * 0.03)
        m = bw + 6
        g = f'<g transform="translate({m:.2f} {m:.2f})">'
        s += (g + f'<path d="{d}" fill="{branco}" stroke="{branco}" stroke-width="{2 * bw:.2f}" stroke-linejoin="round" '
              f'filter="url(#{fid})"/><path d="{d}" fill="{f.acento}"/></g>')
        W, H = tw + 2 * m, th + 2 * m
        ang = f.angulo
        nota = f"letra recortada com borda branca de {bw:.0f} px (as bordas se fundem) + sombra curta"
    elif tipo == "estrela":
        R = 130.0
        m = 16.0
        cx = cy = R + m
        pts = pontos_estrela(cx, cy, 14, R, 0.74)
        dd = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"
        s += (f'<path d="{dd}" fill="{branco}" stroke="{branco}" stroke-width="{2 * 9:.2f}" stroke-linejoin="round" '
              f'filter="url(#{fid})"/><path d="{dd}" fill="{f.acento}"/>')
        # "NOITES" subiu de 14 para 22 px de maiúscula (D-R4b); o numeral sobe para dar o mesmo respiro
        s += centro_tinta(f.fonte_display, "3", corpo(f.fonte_display, 84), cx, cy - 20, f.sobre_acento)
        s += centro_tinta(f.fonte_texto, "NOITES", corpo(f.fonte_texto, 22), cx, cy + 44, f.sobre_acento, 0.10)
        W = H = 2 * (R + m)
        ang = -f.angulo * 1.5
        nota = "estrela-adesivo: borda branca de 9 px seguindo as pontas (junção redonda)"
    elif tipo == "canto":
        w, h = 300.0, 190.0
        c = 52.0
        m = 10.0
        r = f.raio
        corpo_d = (f"M{m + r:.2f} {m:.2f}H{m + w - r:.2f}A{r} {r} 0 0 1 {m + w:.2f} {m + r:.2f}V{m + h - c:.2f}"
                   f"L{m + w - c:.2f} {m + h:.2f}H{m + r:.2f}A{r} {r} 0 0 1 {m:.2f} {m + h - r:.2f}V{m + r:.2f}"
                   f"A{r} {r} 0 0 1 {m + r:.2f} {m:.2f}Z")
        s += f'<path d="{corpo_d}" fill="{f.acento}" stroke="{branco}" stroke-width="12" stroke-linejoin="round" filter="url(#{fid})"/>'
        s += f'<path d="{corpo_d}" fill="{f.acento}"/>'
        aba = f"M{m + w - c:.2f} {m + h:.2f}L{m + w:.2f} {m + h - c:.2f}L{m + w - c:.2f} {m + h - c:.2f}Z"
        s += (f'<path d="{aba}" fill="{mistura(branco, f.fundo, 0.12)}" stroke="{mistura(branco, f.fundo, 0.12)}" '
              f'stroke-width="6" stroke-linejoin="round" filter="url(#{fid})"/>')
        # texto CENTRADO no corpo (antes colado à esquerda: 30 px de um lado, ~80 do outro)
        a, _ = rotulo(f, "20H30", m + w / 2, m + h / 2 - 6, f.sobre_acento, 60, f.fonte_display, 0.02, "middle")
        s += a
        W, H = w + 2 * m, h + 2 * m
        ang = f.angulo * 0.7
        nota = "adesivo com canto levantado (aba no verso da borda branca): 'acabou de ser colado'"
    else:   # pilula
        capx = 25.0
        tw = larg_rotulo(f, "3 NOITES", capx, f.fonte_texto, 0.12)
        h = capx + 34
        w = tw + 2 * capx
        m = 12.0
        dd = p_cantos(m, m, w, h, h / 2)
        s += f'<path d="{dd}" fill="{branco}" stroke="{branco}" stroke-width="14" filter="url(#{fid})"/>'
        s += f'<path d="{dd}" fill="{f.fundo}"/>'
        a, _ = rotulo(f, "3 NOITES", m + w / 2, m + h / 2, f.tinta, capx, f.fonte_texto, 0.12, "middle")
        s += a
        W, H = w + 2 * m, h + 2 * m
        ang = -f.angulo
        nota = "pílula-adesivo escura com borda branca de 7 px: rótulo 'colado' em cima da foto"
    a = math.radians(abs(ang))
    W2, H2 = W * math.cos(a) + H * math.sin(a) + 8, W * math.sin(a) + H * math.cos(a) + 8
    s = (f'<g transform="translate({W2 / 2:.2f} {H2 / 2:.2f}) rotate({ang:.2f}) translate({-W / 2:.2f} {-H / 2:.2f})">{s}</g>')
    return elemento(W2, H2, s, nome or f"adesivo · {tipo}", FAM, defs=defs, nota=nota)


# =====================================================================================================================
# relevo (filtros), contorno deslocado, botão
# =====================================================================================================================
def _f_alto(id_, luz="#FFFFFF", sombra="#000000", d=2.0, desf=1.2, ol=0.75, os_=0.28):
    return filtro(id_, (
        f'<feGaussianBlur in="SourceAlpha" stdDeviation="{desf}" result="b"/>'
        f'<feOffset in="b" dx="{-d}" dy="{-d}" result="bl"/><feFlood flood-color="{luz}" flood-opacity="{ol}"/>'
        f'<feComposite in2="bl" operator="in" result="luz"/>'
        f'<feOffset in="b" dx="{d}" dy="{d}" result="bs"/><feFlood flood-color="{sombra}" flood-opacity="{os_}"/>'
        f'<feComposite in2="bs" operator="in" result="somb"/>'
        f'<feMerge><feMergeNode in="luz"/><feMergeNode in="somb"/><feMergeNode in="SourceGraphic"/></feMerge>'))


def _f_baixo(id_, luz="#FFFFFF", sombra="#000000", d=2.0, desf=1.2, ol=0.7, os_=0.45):
    """Baixo-relevo (letterpress): sombra INTERNA em cima-esquerda + luz interna embaixo-direita."""
    return filtro(id_, (
        f'<feComponentTransfer in="SourceAlpha" result="inv"><feFuncA type="table" tableValues="1 0"/></feComponentTransfer>'
        f'<feGaussianBlur in="inv" stdDeviation="{desf}" result="ib"/>'
        f'<feOffset in="ib" dx="{d}" dy="{d}" result="o1"/><feFlood flood-color="{sombra}" flood-opacity="{os_}"/>'
        f'<feComposite in2="o1" operator="in"/><feComposite in2="SourceAlpha" operator="in" result="sombIn"/>'
        f'<feOffset in="ib" dx="{-d}" dy="{-d}" result="o2"/><feFlood flood-color="{luz}" flood-opacity="{ol}"/>'
        f'<feComposite in2="o2" operator="in"/><feComposite in2="SourceAlpha" operator="in" result="luzIn"/>'
        f'<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="sombIn"/><feMergeNode in="luzIn"/></feMerge>'))


def relevo(f, tipo="alto-papel", nome=None):
    """Relevo tom sobre tom com filtro SVG (sRGB): o desenho tem a MESMA cor da superfície; só luz e sombra o mostram."""
    fid = uid("relevo", tipo, f.seed)
    if tipo in ("alto-papel", "baixo-papel"):
        sup = f.papel
        W, H = 420.0, 260.0
        base = f'<rect width="{W}" height="{H}" fill="{sup}"/>'
        d, tw, th = _texto_d(f, "AO VIVO", 100)
        tx, ty = (W - tw) / 2, (H - th) / 2
        defs = (_f_alto(fid, "#FFFFFF", "#000000", 2.2, 1.2, 0.9, 0.34) if tipo == "alto-papel"
                else _f_baixo(fid, "#FFFFFF", "#000000", 2.4, 1.3, 0.85, 0.52))
        s = base + f'<path transform="translate({tx:.2f} {ty:.2f})" d="{d}" fill="{sup}" filter="url(#{fid})"/>'
        el = elemento(W, H, s, nome or ("alto-relevo · papel" if tipo == "alto-papel" else "baixo-relevo · papel"),
                      FAM, defs=defs,
                      nota="tom sobre tom no papel: luz em cima-esquerda, sombra embaixo-direita (filtro sRGB)")
        return no_claro(el)
    if tipo == "placa":
        W, H = 420.0, 220.0
        sup = f.acento
        d, tw, th = _texto_d(f, "3 NOITES", 84)
        tx, ty = (W - tw) / 2, (H - th) / 2
        defs = _f_baixo(fid, "#FFFFFF", f.fundo, 2.4, 1.4, 0.55, 0.55)
        s = (f'<path d="{p_cantos(0, 0, W, H, f.raio_lg)}" fill="{sup}"/>'
             f'<path d="{p_cantos(0, 0, W, H, f.raio_lg, 10)}" fill="none" stroke="{mistura(sup, f.fundo, 0.25)}" stroke-width="1.5"/>'
             f'<path transform="translate({tx:.2f} {ty:.2f})" d="{d}" fill="{sup}" filter="url(#{fid})"/>')
        for (x, y) in ((22, 22), (W - 22, 22), (22, H - 22), (W - 22, H - 22)):
            s += (f'<circle cx="{x}" cy="{y}" r="5" fill="{mistura(sup, f.fundo, 0.35)}"/>'
                  f'<circle cx="{x - 1}" cy="{y - 1}" r="2" fill="{mistura(sup, f.tinta, 0.5)}"/>')
        return elemento(W, H, s, nome or "placa com baixo-relevo", FAM, defs=defs,
                        nota="placa no acento, letra estampada (mesma cor), 4 rebites: troféu/placa de conquista")
    # alto-escuro
    W, H = 420.0, 240.0
    sup = mistura(f.fundo, f.tinta, 0.07)
    d, tw, th = _texto_d(f, "20H30", 110)
    tx, ty = (W - tw) / 2, (H - th) / 2
    defs = _f_alto(fid, "#FFFFFF", "#000000", 1.8, 1.0, 0.24, 0.75)
    s = (f'<path d="{p_cantos(0, 0, W, H, f.raio_lg)}" fill="{sup}"/>'
         f'<path transform="translate({tx:.2f} {ty:.2f})" d="{d}" fill="{sup}" filter="url(#{fid})"/>')
    return elemento(W, H, s, nome or "alto-relevo · escuro", FAM, defs=defs,
                    nota="no escuro a luz é fraca (24%) e a sombra forte (75%): relevo discreto, 'grafite'")


def deslocado(f, alvo="texto", d=None, nome=None):
    """Contorno duplo DESLOCADO: forma cheia + o mesmo contorno deslocado (desregistro intencional, 1 direção)."""
    t = f.traco
    s = ""
    if alvo == "texto":
        dd, tw, th = _texto_d(f, "AO VIVO", 92)
        d = d or round(th * 0.08)
        s += f'<path transform="translate({d:.2f} {d:.2f})" d="{dd}" fill="none" stroke="{f.acento}" stroke-width="{t:.2f}"/>'
        s += f'<path d="{dd}" fill="{f.tinta}"/>'
        W, H = tw + d + t, th + d + t
        nota = f"contorno no acento deslocado {d:g} px (8% da altura): risografia com desregistro de propósito"
    elif alvo == "pilula":
        capx = 25.0
        tw = larg_rotulo(f, "NOITE 1", capx, f.fonte_texto, 0.12)
        h = capx + 36
        w = tw + 2 * capx
        d = d or 8.0
        s += f'<path d="{p_cantos(d + t / 2, d + t / 2, w - t, h - t, (h - t) / 2)}" fill="none" stroke="{f.tinta}" stroke-width="{t:.2f}"/>'
        s += f'<path d="{p_cantos(0, 0, w, h, h / 2)}" fill="{f.acento}"/>'
        a, _ = rotulo(f, "NOITE 1", w / 2, h / 2, f.sobre_acento, capx, f.fonte_texto, 0.12, "middle")
        s += a
        W, H = w + d, h + d
        nota = "pílula cheia + contorno deslocado 8 px: 'sombra' sem preencher"
    elif alvo == "cartao":
        r = f.raio_lg
        capx = 25.0
        tw = larg_rotulo(f, "PÓS-GRADUAÇÃO", capx, f.fonte_texto, 0.06)
        w, h = tw + 2 * r, 220.0                       # respiro lateral = raio (F13); texto >= 25 px de maiúscula
        d = d or 12.0
        s += f'<path d="{p_cantos(d + t / 2, d + t / 2, w - t, h - t, r - t / 2)}" fill="none" stroke="{f.acento}" stroke-width="{t:.2f}"/>'
        s += f'<path d="{p_cantos(0, 0, w, h, r)}" fill="{f.tinta}"/>'
        a, _ = rotulo(f, "PÓS-GRADUAÇÃO", r, h - r - capx / 2, f.fundo, capx, f.fonte_texto, 0.06)
        s += a
        W, H = w + d, h + d
        nota = f"cartão + contorno deslocado 12 px no acento; mesmo raio ({r:g})"
    else:   # circulo
        R = 100.0
        d = d or 10.0
        s += f'<circle cx="{R + d:.2f}" cy="{R + d:.2f}" r="{R - t / 2:.2f}" fill="none" stroke="{f.tinta}" stroke-width="{t:.2f}"/>'
        s += f'<circle cx="{R:.2f}" cy="{R:.2f}" r="{R:.2f}" fill="{f.acento}"/>'
        s += centro_tinta(f.fonte_display, "1", corpo(f.fonte_display, 110), R, R, f.sobre_acento)
        W = H = 2 * R + d
        nota = "disco cheio + aro deslocado: número de etapa com 'eco'"
    return elemento(W, H, s, nome or f"contorno deslocado · {alvo}", FAM, nota=nota)


def botao_brutal(f, estado="normal", forma="pilula", escuro=False, nome=None):
    """Botão neo-brutal (EXEMPLO DE SITE): borda 2 px, sombra dura 3 px; pressionado = anda 3 px e a sombra zera."""
    ff = f if escuro else claro(f)
    b, dsh = 2.0, 3.0
    capx = 20.0
    lab = "AO VIVO · 20H30"
    tw = larg_rotulo(ff, lab, capx, ff.fonte_texto, 0.1)
    h = capx + 2 * 20
    circ = h - 14
    w = 28 + tw + 18 + circ + 7
    linha = ff.tinta
    fundo_b = f.tinta if not escuro else f.fundo
    if forma == "pilula":
        r = h / 2
        fundo_b = f.acento
    else:
        r = f.raio_sm
    off = dsh if estado == "pressionado" else 0.0
    s = ""
    if estado != "pressionado":
        s += f'<path d="{p_cantos(dsh, dsh, w, h, r)}" fill="{linha}"/>'
    g = f'<g transform="translate({off:.2f} {off:.2f})">'
    s += g + f'<path d="{p_cantos(0, 0, w, h, r, b / 2)}" fill="{fundo_b}" stroke="{linha}" stroke-width="{b}"/>'
    txt_cor = f.sobre_acento if fundo_b == f.acento else linha
    a, _ = rotulo(ff, lab, 28, h / 2, txt_cor, capx, ff.fonte_texto, 0.1)
    cx = w - 7 - circ / 2
    s += a + f'<circle cx="{cx:.2f}" cy="{h / 2:.2f}" r="{circ / 2:.2f}" fill="{linha}"/>'
    from .formas import _seta_diag
    s += _seta_diag(cx, h / 2, circ * 0.42, fundo_b, 2.5, 0, limpa=True) + "</g>"
    if estado == "foco":
        s = (f'<path d="{p_cantos(-6, -6, w + dsh + 12, h + dsh + 12, r + 6, 1.5)}" fill="none" stroke="{linha}" '
             f'stroke-width="3"/>') + s
        s = f'<g transform="translate(6 6)">{s}</g>'
        W, H = w + dsh + 12, h + dsh + 12
    else:
        W, H = w + dsh, h + dsh
    css = (f".btn{{border:{b:g}px solid {linha};border-radius:{r:g}px;box-shadow:{dsh:g}px {dsh:g}px 0 {linha};"
           "transition:transform .1s,box-shadow .1s}"
           f".btn:active{{transform:translate({dsh:g}px,{dsh:g}px);box-shadow:0 0 0 {linha}}}"
           ".btn:focus-visible{outline:3px solid currentColor;outline-offset:3px}")
    el = elemento(W, H, s, nome or f"botão neo-brutal · {estado}" + (" · escuro" if escuro else ""), FAM, css=css,
                  nota={"normal": "SITE: borda 2 px + sombra dura 3 px; só em clicável",
                        "pressionado": "SITE :active — anda 3 px e a sombra vai a 0 (animar só transform)",
                        "foco": "SITE :focus-visible — anel de 3 px afastado 3 px (o foco não some na borda)"}[estado])
    return el if escuro else no_claro(el)


# =====================================================================================================================
# amostras
# =====================================================================================================================
@amostra(FAM, "sombra dura")
def _a_dura(f):
    return [sombra_dura(f, "cartao", r=0), sombra_dura(f, "cartao", r=f.raio_lg, claro_=True),
            sombra_dura(f, "pilula"), sombra_dura(f, "circulo"), sombra_dura(f, "texto")]


@amostra(FAM, "sombra longa e extrusão")
def _a_longa(f):
    return [sombra_longa(f, "numeral"), sombra_longa(f, "selo", esvai=True), sombra_longa(f, "texto"),
            extrusao(f, "numeral"), extrusao(f, "texto", frente=f.acento, lado=mistura(f.acento, f.fundo, 0.55)),
            extrusao(f, "pilula", frente=f.acento, lado=mistura(f.acento, f.fundo, 0.5)),
            camadas(f, "circulo"), camadas(f, "cartoes")]


@amostra(FAM, "papel e adesivo")
def _a_papel(f):
    return [papel(f, "folhas"), papel(f, "leque"), papel(f, "ingressos"),
            adesivo(f, "texto"), adesivo(f, "estrela"), adesivo(f, "canto"), adesivo(f, "pilula")]


@amostra(FAM, "relevo e contorno deslocado")
def _a_relevo(f):
    return [relevo(f, "alto-papel"), relevo(f, "baixo-papel"), relevo(f, "placa"), relevo(f, "alto-escuro"),
            deslocado(f, "texto"), deslocado(f, "pilula"), deslocado(f, "cartao"), deslocado(f, "circulo")]


@amostra(FAM, "botão neo-brutal (site)")
def _a_botao(f):
    return [botao_brutal(f, "normal"), botao_brutal(f, "pressionado"), botao_brutal(f, "foco", forma="ret"),
            botao_brutal(f, "normal", forma="ret", escuro=True)]
