"""ornamentos.codigos — família "códigos": QR code VÁLIDO, código de barras Code 128 VÁLIDO e numeração de série.

Regras (references/elementos.md; pesquisa 11 E104–E106): código que aparece tem que LER — cada elemento desta família é
renderizado e lido de volta (zxing-cpp) na hora de gerar; se não ler, dá erro (não vai para a peça). QR com margem livre
de 4 módulos (Denso Wave), módulo escuro sobre fundo claro (leitores antigos não leem invertido); Code 128 com zona livre
de 10 módulos. Conteúdo = PARÂMETRO (o link/código real da campanha); a amostra usa example.com (domínio reservado
para exemplos) e textos da campanha — nunca "REF-0042-X" inventado. QR em story/anúncio de celular é cafona (a pessoa
já está no celular): usar em impresso, telão, slide de live.

Bibliotecas: segno (BSD-3) gera o QR; zxing-cpp (Apache-2.0) gera os módulos do Code 128 e confere a leitura.

Revisão um a um (10/2026, `_revisao/codigos.md`): todo texto que precisa ser LIDO tem maiúscula ≥ 25,6 px no tamanho
natural (`_R`, alinhado pela TINTA); o cartão/etiqueta cresce para caber a legenda (nunca o contrário); raios só da
escala (0 · raio_sm · raio · raio_lg); furo é geometria (picote do canhoto = entalhes no caminho, nunca tinta da cor do
fundo); nenhum fio atravessa algarismo; a leitura é conferida em zoom 3 e também no TAMANHO NATURAL (zoom 1).
"""
import functools
import io

from .nucleo import amostra, largura, cap, ret, poligono, _font
from . import nucleo as _N
from .assunto import justo, mistura, rot, rot_c, _p, luminancia, uid

FAM = "codigos"
LER = 25.6          # altura mínima da MAIÚSCULA (px num lado de 1080) de texto que precisa ser lido


# ================================================================ rótulo legível, alinhado pela tinta
@functools.lru_cache(maxsize=1024)
def _tinta_x(spec, s, size, tr):
    """(x0, x1, avanço) da tinta do texto, relativos à origem."""
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


def _R(f, s, x, base, fill, spec=None, anchor="start", tr=0.04, cap_px=LER):
    """Texto em curvas com maiúscula = cap_px; a TINTA fica em x (start | middle | end)."""
    spec = spec or f.fonte_texto
    size = round(cap_px / cap(spec), 4)
    x0, x1, _ = _tinta_x(spec, s, size, tr)
    xo = x - x0 if anchor == "start" else x - x1 if anchor == "end" else x - (x0 + x1) / 2
    svg, _ = _N.texto(spec, s, size, xo, base, fill, tr, "start")
    return svg


def _RW(f, s, spec=None, tr=0.04, cap_px=LER):
    """Largura da TINTA do rótulo."""
    spec = spec or f.fonte_texto
    x0, x1, _ = _tinta_x(spec, s, round(cap_px / cap(spec), 4), tr)
    return x1 - x0


# ================================================================ conferência de leitura
def ler(svg_doc, zoom=3.0):
    """Renderiza o SVG (resvg) sobre branco e lê com zxing-cpp. Devolve lista de textos lidos (ou None se o
    zxing-cpp não estiver instalado)."""
    try:
        import zxingcpp
    except ImportError:
        return None
    import numpy as np
    import resvg_py
    from PIL import Image
    png = resvg_py.svg_to_bytes(svg_string=svg_doc, zoom=zoom, background="#FFFFFF")
    im = Image.open(io.BytesIO(bytes(png))).convert("L")
    pad = Image.new("L", (im.width + 80, im.height + 80), 255)
    pad.paste(im, (40, 40))
    return [r.text for r in zxingcpp.read_barcodes(np.array(pad))]


def _confere(el, esperado):
    """Lê em zoom 3 E no tamanho natural (zoom 1): um código que só lê ampliado não serve na peça."""
    lidos = ler(el.svg)
    if lidos is None:
        el.nota += " · leitura NÃO conferida (instale zxing-cpp)"
        return el
    if esperado not in lidos:
        raise ValueError(f"{el.nome}: o código NÃO lê (lido: {lidos!r}) — não usar")
    nat = ler(el.svg, zoom=1.0)
    if nat is not None and esperado not in nat:
        raise ValueError(f"{el.nome}: o código lê ampliado mas NÃO no tamanho natural (lido: {nat!r}) — aumentar o módulo")
    el.nota += " · leitura conferida (zxing-cpp, zoom 3 e 1)"
    return el


# ================================================================ QR code
def qr(f, conteudo="https://example.com/campanha", modo="quadrado", modulo=8.0, erro="q", legenda=None,
       claro=None, escuro=None, raio_cartao=True):
    """QR válido (segno). modo: quadrado (padrão, lê em tudo) | arredondado (módulos com canto) | pontos (módulos
    redondos, olhos inteiros) | moldura (cartão + legenda). Margem livre de 4 módulos SEMPRE. erro: l/m/q/h.
    Legenda curta (maiúscula ≥ 25,6 px): o cartão ganha uma faixa embaixo para ela."""
    import segno
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    claro = claro or mistura(f.papel, "#FFFFFF", 0.4)
    escuro = escuro or f.fundo
    q = segno.make(conteudo, error=erro, micro=False)
    mat = [list(r) for r in q.matrix]
    n = len(mat)
    m = modulo
    borda = 4
    lado = (n + 2 * borda) * m
    o = []
    rc = f.raio if raio_cartao else 0
    com_leg = bool(legenda or modo == "moldura")
    gap_leg, pad_b = 14.0, 20.0
    extra_h = gap_leg + LER + pad_b if com_leg else 0
    o.append(f'<path d="{ret(0, 0, lado, lado + extra_h, rc)}" fill="{claro}"/>')

    def finder(r, c):
        return (r < 7 and c < 7) or (r < 7 and c >= n - 7) or (r >= n - 7 and c < 7)
    x0 = y0 = borda * m
    d = ""
    if modo in ("quadrado", "moldura"):
        for r in range(n):
            c = 0
            while c < n:
                if mat[r][c]:
                    c1 = c
                    while c1 < n and mat[r][c1]:
                        c1 += 1
                    d += f"M{x0 + c * m:.2f} {y0 + r * m:.2f}h{(c1 - c) * m:.2f}v{m:.2f}h{-(c1 - c) * m:.2f}z"
                    c = c1
                else:
                    c += 1
        o.append(f'<path d="{d}" fill="{escuro}" shape-rendering="crispEdges"/>')
    else:
        for r in range(n):
            for c in range(n):
                if not mat[r][c] or finder(r, c):
                    continue
                x, y = x0 + c * m, y0 + r * m
                if modo == "pontos":
                    o.append(f'<circle cx="{x + m / 2:.2f}" cy="{y + m / 2:.2f}" r="{m * 0.46:.2f}" fill="{escuro}"/>')
                else:
                    o.append(f'<path d="{ret(x + m * 0.04, y + m * 0.04, m * 0.92, m * 0.92, m * 0.3)}" fill="{escuro}"/>')
        for (r, c) in ((0, 0), (0, n - 7), (n - 7, 0)):   # olhos: anel 7×7 + miolo 3×3, com canto
            x, y = x0 + c * m, y0 + r * m
            o.append(f'<path d="{ret(x, y, 7 * m, 7 * m, m * 1.6)}{ret(x + m, y + m, 5 * m, 5 * m, m * 1.0)}" '
                     f'fill="{escuro}" fill-rule="evenodd"/>')
            o.append(f'<path d="{ret(x + 2 * m, y + 2 * m, 3 * m, 3 * m, m * 0.8)}" fill="{escuro}"/>')
    if com_leg:
        txt = legenda or "ESCANEIE"
        o.append(_R(f, txt, lado / 2, lado + gap_leg + LER, escuro, f.fonte_texto, "middle", 0.1))
    el = justo("".join(o), f"QR · {modo} · v{q.version}-{q.error}", f"QR válido de '{conteudo}' com margem de 4 módulos; "
               "conteúdo = parâmetro · impresso, telão, slide de live (nunca em story)")
    return _confere(el, conteudo)


@amostra(FAM, "QR code")
def _a_qr(f):
    return [qr(f), qr(f, modo="arredondado"), qr(f, modo="pontos", erro="h"),
            qr(f, modo="moldura", modulo=7.0), qr(f, "https://example.com/campanha/noite-1", modulo=6.5,
                                                   legenda="NOITE 1")]


# ================================================================ Code 128
def code128(f, dados="BLACK FRIDAY 2026", altura=None, modulo=2.4, legivel=True, modo="padrao", cor=None, fundo_cor=None):
    """Code 128 VÁLIDO (módulos do zxing-cpp; zona livre de 10 módulos). modo: padrao | alto (barras altas,
    estreito) | vertical (girado 90°) | etiqueta (com faixa de cima no acento e rótulo). Texto legível em mono
    (maiúscula ≥ 25,6 px): o módulo CRESCE até as barras serem tão largas quanto o texto. fundo_cor precisa ser CLARO
    (luminância > 0,35): no vermelho/roxo da ficha a câmera não separa barra de fundo — a conferência recusa."""
    import zxingcpp
    import numpy as np
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    b = zxingcpp.create_barcode(dados, zxingcpp.BarcodeFormat.Code128)
    linha = np.array(b.to_image(scale=1, add_quiet_zones=False))[0]
    bits = [1 if v < 128 else 0 for v in linha]
    q = 10
    m = modulo
    if legivel:                       # texto legível não pode ser mais largo que as barras
        m = max(m, _RW(f, dados, f.fonte_mono, 0.04) / len(bits))
    W = (len(bits) + 2 * q) * m
    pt = max(4 * m, 14.0)             # respiro de cima (ou sob a faixa)
    H = altura or (W * (0.32 if modo != "alto" else 0.55))
    escuro = cor or f.fundo
    claro = fundo_cor or mistura(f.papel, "#FFFFFF", 0.4)
    rs = f.raio_sm
    topo = (LER + 2 * 10.0) if modo == "etiqueta" else 0.0
    gap_t, pad_b = 12.0, 14.0
    h_total = topo + pt + H + (gap_t + LER + pad_b if legivel else pt)
    o = []
    o.append(f'<path d="{ret(0, 0, W, h_total, rs)}" fill="{claro}"/>')
    if modo == "etiqueta":
        o.append(f'<path d="{ret(0, 0, W, topo, rs, (rs, rs, 0, 0))}" fill="{ac}"/>')
        o.append(_R(f, "BLACK FRIDAY", q * m, topo / 2 + LER / 2, f.sobre_acento, f.fonte_texto, "start", 0.1))
    d = ""
    i = 0
    y = topo + pt
    while i < len(bits):
        if bits[i]:
            j = i
            while j < len(bits) and bits[j]:
                j += 1
            d += f"M{(q + i) * m:.2f} {y:.2f}h{(j - i) * m:.2f}v{H:.2f}h{-(j - i) * m:.2f}z"
            i = j
        else:
            i += 1
    o.append(f'<path d="{d}" fill="{escuro}" shape-rendering="crispEdges"/>')
    if legivel:
        o.append(_R(f, dados, W / 2, y + H + gap_t + LER, escuro, f.fonte_mono, "middle", 0.04))
    corpo = "".join(o)
    if modo == "vertical":
        corpo = f'<g transform="rotate(-90)">{corpo}</g>'
    el = justo(corpo, f"Code 128 · {modo} · {dados}", "Code 128 válido, zona livre de 10 módulos, texto legível embaixo; "
               "conteúdo = parâmetro (código real) · ingresso, etiqueta, dossiê")
    return _confere(el, dados)


@amostra(FAM, "Code 128")
def _a_code(f):
    return [code128(f, modulo=1.9), code128(f, "NOITE 1 20H30", modo="alto", modulo=2.2),
            code128(f, "AO VIVO", modo="vertical", modulo=2.6),
            code128(f, "CAMPANHA-2026", modo="etiqueta", modulo=2.2),
            code128(f, "27/11/2026", modulo=2.8, cor=f.fundo,
                    fundo_cor=f.acento if luminancia(f.acento) > 0.35 else None)]   # acento escuro (vermelho, roxo) não lê


# ================================================================ número de série / lote / edição
def serie(f, numero=1, total=3, rotulo="NOITE", modo="fracao", digitos=2):
    """Numeração REAL (noite n de 3, edição, turma). modo: fracao (rótulo + 01/03) | numerador (bandas de numerador
    mecânico, 3 casas) | canhoto (picote real + texto na vertical) | edicao (rótulo + ano em caixa dupla).
    Todo texto com maiúscula ≥ 25,6 px; nenhum fio atravessa algarismo; furo = entalhe no caminho."""
    t, ink, apo, ac = f.traco, f.tinta, f.apoio, f.acento
    u = f.unidade
    o = []
    defs = ""
    M = f.fonte_mono
    if modo == "fracao":
        capn = u * 2.3                                     # algarismo grande (≈ 55 px)
        n = f"{numero:0{digitos}d}"
        tot = f"/{total:0{digitos}d}"
        cap_t = capn * 0.5                                 # "/03" em ~27,6 px (≥ 25,6)
        y_n = LER + 14 + capn
        o.append(_R(f, rotulo, 0, LER, apo, f.fonte_texto, "start", 0.12))
        o.append(_R(f, n, 0, y_n, ink, M, "start", 0.0, capn))
        x = _RW(f, n, M, 0.0, capn) + u * 0.3
        o.append(_R(f, tot, x, y_n, ac, M, "start", 0.0, cap_t))
        o.append(_p(f"M0 {y_n + u * 0.6:.2f}H{x + _RW(f, tot, M, 0.0, cap_t):.2f}", stroke=apo, sw=t * 0.5))
    elif modo == "numerador":
        casas = max(3, digitos)
        s = f"{numero:0{casas}d}"
        cap_txt = f"{rotulo} {numero}/{total}"
        wcap = _RW(f, cap_txt, f.fonte_texto, 0.12)
        g = 5.0
        cw = (wcap - g * (casas - 1)) / casas              # o numerador tem a MESMA largura da legenda (alinhado)
        ch = cw * 1.35
        capd = min(cw * 0.78, ch * 0.5)
        for i, c in enumerate(s):
            x = i * (cw + g)
            o.append(f'<path d="{ret(x, 0, cw, ch, 0)}" fill="{mistura(f.fundo, ink, 0.12)}"/>')
            o.append(_R(f, c, x + cw / 2, ch / 2 + capd / 2, ac if c != "0" else ink, M, "middle", 0.0, capd))
        o.append(_R(f, cap_txt, 0, ch + 14 + LER, apo, f.fonte_texto, "start", 0.12))
    elif modo == "canhoto":
        W, H = u * 4.2, u * 11
        rs = f.raio_sm
        r = u * 0.13
        passo = u * 0.62
        k = int((H - u * 0.8) / passo) + 1
        y0 = (H - (k - 1) * passo) / 2                    # picote centrado na altura
        # contorno: canto superior-esquerdo e inferior-esquerdo arredondados; borda direita com entalhes semicirculares
        d = f"M{rs:.2f} 0H{W:.2f}"
        for i in range(k):
            cy = y0 + i * passo
            d += f"V{cy - r:.2f}A{r:.2f} {r:.2f} 0 0 0 {W:.2f} {cy + r:.2f}"
        d += f"V{H:.2f}H{rs:.2f}A{rs:.2f} {rs:.2f} 0 0 1 0 {H - rs:.2f}V{rs:.2f}A{rs:.2f} {rs:.2f} 0 0 1 {rs:.2f} 0Z"
        o.append(f'<path d="{d}" fill="{ac}"/>')
        n = f"{numero}"
        txt = f"{rotulo} {n}/{total}"
        # texto na vertical, centrado na faixa (descontado o picote da borda direita)
        cx = (W - r * 2) / 2
        o.append(f'<g transform="rotate(-90 {cx:.2f} {H / 2:.2f})">'
                 + _R(f, txt, cx, H / 2 + LER / 2, f.sobre_acento, M, "middle", 0.04) + "</g>")
    else:
        txt = f"{rotulo} {numero}"
        w = _RW(f, txt, M, 0.1) + u * 2.4
        h = LER * 2.4
        o.append(f'<path d="{ret(0, 0, w, h, 0)}" fill="none" stroke="{ac}" stroke-width="{t:.2f}"/>')
        o.append(f'<path d="{ret(t * 1.7, t * 1.7, w - t * 3.4, h - t * 3.4, 0)}" fill="none" stroke="{ac}" '
                 f'stroke-width="{t * 0.45:.2f}"/>')
        o.append(_R(f, txt, w / 2, h / 2 + LER / 2, ink, M, "middle", 0.1))
    nome_m = {"fracao": "fração", "edicao": "edição"}.get(modo, modo)
    return justo("".join(o), f"série · {nome_m} · {rotulo} {numero}" + (f"/{total}" if total else ""),
                 "numeração verdadeira (noite n de 3, turma, edição) em algarismos tabulares · nunca 'limitado' falso",
                 defs=defs)


@amostra(FAM, "número de série")
def _a_serie(f):
    return [serie(f), serie(f, 2, 3, modo="numerador"), serie(f, 3, 3, modo="canhoto", digitos=1),
            serie(f, 2026, 0, "EDIÇÃO", modo="edicao")]
