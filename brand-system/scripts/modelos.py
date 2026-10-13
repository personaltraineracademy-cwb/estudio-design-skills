"""Modelos de peça: o motor que REPLICA qualquer peça com fidelidade. Cada marca define, no brand.json "templates",
os seus modelos (tipo + cores + gesto + medidas). Mesmo texto + mesmo modelo = mesma peça, por qualquer pessoa.
Tudo em curvas (fontes da marca) → SVG + PNG por formato.

Uso:
  python modelos.py tipos                                   # os 7 tipos de modelo e os parâmetros de cada um
  python modelos.py list <brand_dir>                        # modelos desta marca
  python modelos.py render <brand_dir> <id> --texto "TERÇA, 20H. A CIDADE TROCA DE ~PÉ." --info "Praça · grátis" \
         [--formatos post,feed,story,banner,outdoor] [--foto imagem/x.png] [--numero 3] [-o pasta]
  python modelos.py kit <brand_dir> [--formatos …]          # renderiza o "sample" de cada modelo em aplicacoes/<id>/
                                                            # e grava examples + command no brand.json (o manual usa)
Texto: "|" força quebra de linha; sem "|", a quebra é automática pelo MAIOR corpo, com regras de leitura em português
(nenhuma linha termina em palavra de 1–2 letras; a última linha nunca é só "DE"/"A"). "~" antes de UMA palavra = o
gesto do modelo (girar 180°, mudar de cor, acender…). Cores: papéis do brand.json (brand, ink, paper, accent,
brand.300…) ou HEX.

brand.json "templates": [{"id": "palavra", "model": "tipo", "name": "Palavra deslocada", "rule": "…",
  "measures": ["…"], "colors": {"bg": "brand", "fg": "ink"}, "gesture": "girar", "giant_last": true,
  "sample": {"texto": "…", "info": "…", "formatos": ["feed", "story"]}}, …]   — campos de cada tipo: `modelos.py tipos`
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import font, load_brand, svg_inner, svg_to_png, viewbox, wrap_svg, write  # noqa: E402

FORMATS = {"post": (1080, 1080), "feed": (1080, 1350), "story": (1080, 1920), "banner": (1920, 1080),
           "a4": (1240, 1754), "outdoor": (3000, 1000), "slide": (1920, 1080), "thumb": (1280, 720)}
SHORT = 2            # palavras com até 2 letras não terminam linha (a, é, o, de, um, em…)


# ------------------------------------------------------------------ contexto da marca
class Ctx:
    """Tudo o que um modelo precisa saber da marca. `over` troca fontes/cores/logo (usado por variacoes.py)."""

    def __init__(self, b, over=None):
        over = over or {}
        self.b = b
        self.colors = over.get("colors") or {}
        self.display = over.get("display") or b.font_spec("display", 900, "Bricolage Grotesque")
        self.text = b.font_spec("text", 400) or self.display
        fam = self.text.split(":")[0] if ":" in self.text and not os.path.isfile(self.text) else None
        self.text_b = f"{fam}:700" if fam else self.text
        sym = over.get("symbol") or b.symbol() or b.primitive()
        self.sym = open(sym, encoding="utf-8").read() if sym else None
        lp = over.get("logo") or b.path(b.get("logo.primary"))
        if not lp or not os.path.exists(lp):
            import apply
            lp = apply.logo_path(b)
        self.logo = open(lp, encoding="utf-8").read()
        self.m = (b.get("grid") or {}).get("margin", 0.065)
        self.lead = (b.get("type") or {}).get("lead", 1.42)

    def col(self, role, default="ink"):
        role = role or default
        if role.startswith("#"):
            return role
        return self.colors.get(role) or self.b.colour(role, self.b.colour(default))

    def svg(self, rel):
        p = self.b.path(rel)
        return open(p, encoding="utf-8").read() if p and os.path.exists(p) else None


def achatar_classes(svg):
    """SVG de terceiro pinta por classe (`<style>.cls-1{fill:#…}</style>`): embutido várias vezes na mesma página, a
    ÚLTIMA cor vence em todas as cópias (senão o logo some nas versões claras).
    Copia as propriedades de cada classe para atributos do elemento e remove o <style>."""
    import re
    regras = {}
    for bloco in re.findall(r"<style[^>]*>(.*?)</style>", svg, flags=re.S):
        bloco = re.sub(r"/\*.*?\*/", "", bloco, flags=re.S)
        for sel, corpo in re.findall(r"([^{}]+)\{([^{}]*)\}", bloco):
            props = dict((k.strip(), v.strip()) for k, v in
                         (d.split(":", 1) for d in corpo.split(";") if ":" in d))
            for c in re.findall(r"\.([\w-]+)", sel):
                regras.setdefault(c, {}).update(props)
    if not regras:
        return svg

    def aplica(mt):
        tag = mt.group(0)
        cls = re.search(r'class="([^"]*)"', tag)
        if not cls:
            return tag
        props = {}
        for c in cls.group(1).split():
            props.update(regras.get(c, {}))
        attrs = "".join(f' {k}="{v}"' for k, v in props.items() if f' {k}="' not in tag)
        tag = re.sub(r'\s*class="[^"]*"', "", tag)
        return tag[:-2] + attrs + "/>" if tag.endswith("/>") else tag[:-1] + attrs + ">"
    svg = re.sub(r"<style[^>]*>.*?</style>", "", svg, flags=re.S)
    return re.sub(r'<[a-zA-Z][^<>]*\bclass="[^"]*"[^<>]*>', aplica, svg)


def _recolor(svg, fill):
    """Troca toda cor sólida (preenchimento E traço) pela cor pedida; 'none' fica. Classes CSS achatadas antes."""
    import re
    inner = svg_inner(achatar_classes(svg))
    inner = re.sub(r'(fill|stroke)="#[0-9A-Fa-f]{3,8}"', lambda mt: f'{mt.group(1)}="{fill}"', inner)
    return re.sub(r"(fill|stroke):\s*#[0-9A-Fa-f]{3,8}", lambda mt: f"{mt.group(1)}:{fill}", inner)


def place(svg, x, y, w=None, h=None, fill="#000", rot=0, mirror=False):
    """SVG (símbolo/logo/elemento) por altura ou largura, recolorido; rot gira e mirror espelha em torno do centro."""
    vx, vy, vw, vh = viewbox(svg)
    k = (h / vh) if h else (w / vw)
    cx, cy = x + vw * k / 2, y + vh * k / 2
    r = f"rotate({rot} {cx:.1f} {cy:.1f}) " if rot else ""
    if mirror:
        r += f"translate({2 * cx:.1f} 0) scale(-1 1) "
    return (f'<g transform="{r}translate({x:.1f} {y:.1f}) scale({k:.5f}) translate({-vx} {-vy})" fill="{fill}">'
            f'{_recolor(svg, fill)}</g>'), vw * k, vh * k


def text(s, size, x, y, fill, spec, tracking=0.0, anchor="start"):
    f = font(spec)
    w = f.width(s, size, tracking)
    x = x - w if anchor == "end" else x - w / 2 if anchor == "middle" else x
    d = f.path(s, size, x, y, tracking)
    return f'<path d="{d}" fill="{fill}"/>' if d else "", w


def _bad_break(lines):
    """Regras de leitura em português para a quebra automática."""
    for ln in lines[:-1]:
        if len(ln.split(" ")[-1].strip(".,;:!?~")) <= SHORT:
            return True
    last = lines[-1].split(" ")
    return len(lines) > 1 and len(last) == 1 and len(last[0].strip(".,;:!?~")) <= SHORT


def best_breaks(spec, words, max_w, max_h, lead, tracking=-0.01, max_lines=6):
    """Quebra as palavras no número de linhas que dá o MAIOR corpo dentro de max_w × max_h."""
    from itertools import combinations
    f = font(spec)
    best, best_size = [" ".join(words)], 0
    for n in range(1, min(max_lines, len(words)) + 1):
        for cuts in combinations(range(1, len(words)), n - 1):
            idx = (0,) + cuts + (len(words),)
            lines = [" ".join(words[idx[i]:idx[i + 1]]) for i in range(n)]
            if _bad_break(lines):
                continue
            wmax = max(f.width(ln.replace("~", ""), 1, tracking) for ln in lines)
            size = min(max_w / wmax, max_h / (f.cap * (1 + (n - 1) * lead) + f.cap * 0.25))
            if size > best_size * 1.03:
                best, best_size = lines, size
    return best


def headline(ctx, lines, x, y_top, max_w, max_h, fill, gesture=None, gesture_color=None, spec=None, tracking=-0.01):
    """Título no maior corpo que cabe em max_w × max_h. A palavra com ~ recebe o gesto: "girar" (180° no próprio lugar;
    a pontuação não gira), "cor" (gesture_color) ou nada. Devolve (svg, corpo, y da base da última linha + folga)."""
    spec = spec or ctx.display
    f = font(spec)
    if len(lines) == 1 and " " in lines[0]:
        lines = best_breaks(spec, lines[0].split(" "), max_w, max_h, ctx.lead, tracking)
    wmax = max(f.width(ln.replace("~", ""), 1, tracking) for ln in lines)
    n = len(lines)
    size = min(max_w / wmax, max_h / (f.cap * (1 + (n - 1) * ctx.lead) + f.cap * 0.25))
    cap = f.cap * size
    out, y = [], y_top + cap * 1.12            # espaço para acento na 1ª linha
    for ln in lines:
        cx = x
        words = ln.split(" ")
        for i, word in enumerate(words):
            marked = word.startswith("~")
            word = word.lstrip("~")
            piece = word + (" " if i < len(words) - 1 else "")
            if marked and gesture == "girar":
                core = word.rstrip(".,!?;:")
                tail = word[len(core):]
                ww = f.width(core, size, tracking)
                out.append(f'<path d="{f.path(core, size, cx, y, tracking)}" fill="{fill}" '
                           f'transform="rotate(180 {cx + ww / 2:.1f} {y - cap / 2:.1f})"/>')
                if tail:
                    out.append(f'<path d="{f.path(tail, size, cx + ww, y, tracking)}" fill="{fill}"/>')
            else:
                c = gesture_color if (marked and gesture == "cor" and gesture_color) else fill
                out.append(f'<path d="{f.path(word, size, cx, y, tracking)}" fill="{c}"/>')
            cx += f.width(piece, size, tracking)
        y += cap * ctx.lead
    return "".join(out), size, y - cap * ctx.lead + cap * 0.2


def signature(ctx, W, H, fill, info, where="bottom", stack=False, max_info_w=None):
    """Assinatura (altura 4,2% do lado menor) + info (texto 700, caixa alta, 1,9%, espaço 0,06).
    where: bottom (assinatura à esq., info à dir.) · top · stack (info empilhada acima da assinatura, à esquerda)."""
    m = ctx.m * min(W, H)
    s = min(W, H)
    lh = 0.042 * s
    if where == "top":
        g = place(ctx.logo, m, m, h=lh, fill=fill)[0]
        if info:
            g += text(info.upper(), 0.019 * s, W - m, m + lh * 0.72, fill, ctx.text_b, 0.06, "end")[0]
        return g
    g = place(ctx.logo, m, H - m - lh, h=lh, fill=fill)[0]
    if not info:
        return g
    if stack:
        y = H - m - lh - 0.022 * s
        for part in reversed(info.upper().split(" · ")):
            sz = 0.019 * s
            w = font(ctx.text_b).width(part, sz, 0.06)
            if max_info_w and w > max_info_w:
                sz *= max_info_w / w
            g += text(part, sz, m, y, fill, ctx.text_b, 0.06)[0]
            y -= 0.028 * s
        return g
    return g + text(info.upper(), 0.019 * s, W - m, H - m - lh * 0.28, fill, ctx.text_b, 0.06, "end")[0]


def _wide(W, H):
    return W > H * 1.2


# ------------------------------------------------------------------ os 7 tipos
TYPES = {}


def model(name, doc_params):
    def deco(fn):
        TYPES[name] = (fn, doc_params)
        return fn
    return deco


@model("tipo", "colors{bg=brand, fg=ink, gesture} · gesture: girar|cor|nenhum · giant_last (bool, padrão true com "
               "girar) · symbol_fill (bool, padrão true): sobra ≥ 30% de H → símbolo na sobra")
def m_tipo(ctx, t, W, H, lines, info, **_):
    """O tipo é a imagem: título no maior corpo. Com gesture=girar e a ÚLTIMA palavra marcada, ela vira gigante
    (vertical: largura útil, cortada pela borda de baixo; paisagem: terço direito, altura da peça) — lê como gesto,
    não como erro de digitação. Palavra girada pequena no meio da frase confunde o público ("DE 3D"): evite."""
    c = t.get("colors") or {}
    bg, fg = ctx.col(c.get("bg"), "brand"), ctx.col(c.get("fg"), "ink")
    gest = t.get("gesture", "girar")
    gcol = ctx.col(c.get("gesture"), "accent")
    m = ctx.m * min(W, H)
    wide = _wide(W, H)
    body = f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    words = " ".join(lines).split(" ")
    if not wide and gest == "girar" and t.get("giant_last", True) and words[-1].startswith("~"):
        f = font(ctx.display)
        core = words[-1].lstrip("~").rstrip(".,!?;:")
        size = (W - 2 * m) / f.width(core, 1, -0.02)
        cap = f.cap * size
        gtop = H + 0.12 * cap - cap
        body += (f'<path d="{f.path(core, size, m, gtop + cap, -0.02)}" fill="{fg}" '
                 f'transform="rotate(180 {m + (W - 2 * m) / 2:.1f} {gtop + cap / 2:.1f})"/>')
        body += signature(ctx, W, H, fg, info, "top")
        top = m + 0.042 * min(W, H) + 0.05 * H
        g, _, bottom = headline(ctx, [" ".join(words[:-1])], m, top, W - 2 * m, gtop - 0.04 * H - top, fg)
        return body + f'<g transform="translate(0 {max(0, (gtop - 0.035 * H) - bottom):.1f})">{g}</g>'
    if wide and gest == "girar" and t.get("giant_last", True) and words[-1].startswith("~"):
        # paisagem: a palavra girada vira gigante no terço direito (altura da peça, cortada pela base); nunca pequena
        f = font(ctx.display)
        core = words[-1].lstrip("~").rstrip(".,!?;:")
        size = min((W * 0.46 - m) / f.width(core, 1, -0.02), H * 1.1 / f.cap)
        cap = f.cap * size
        gw = f.width(core, size, -0.02)
        gx, gtop = W - m - gw, H + 0.12 * cap - cap
        body += (f'<path d="{f.path(core, size, gx, gtop + cap, -0.02)}" fill="{fg}" '
                 f'transform="rotate(180 {gx + gw / 2:.1f} {gtop + cap / 2:.1f})"/>')
        g, _, _ = headline(ctx, [" ".join(words[:-1])], m, m, gx - 2 * m, H - 2 * m - 0.1 * min(W, H), fg)
        return body + g + signature(ctx, W, H, fg, info, stack=True, max_info_w=gx - 2 * m)
    bw = (W * 0.62 - m) if (wide and ctx.sym) else (W - 2 * m)
    g, _, bottom = headline(ctx, lines, m, m, bw, H - 2 * m - 0.1 * min(W, H), fg, gest, gcol)
    body += g
    if wide and ctx.sym and t.get("symbol_fill", True):
        body += place(ctx.sym, W * 0.68, -H * 0.06, h=H * 1.12, fill=fg)[0]
    elif ctx.sym and t.get("symbol_fill", True):
        free = (H - m - 0.1 * min(W, H)) - (bottom + m)
        if free >= 0.3 * H:
            vx, vy, vw, vh = viewbox(ctx.sym)
            sh = free + m + 0.1 * min(W, H)
            body += place(ctx.sym, W - vw * sh / vh * 0.78, H - sh, h=sh, fill=fg)[0]
            return body + signature(ctx, W, H, fg, info, stack=True)
    return body + signature(ctx, W, H, fg, info)


@model("janela", "colors{bg=brand, fg=ink} · foto (caminho; ou --foto) · symbol_h (vertical 0.66, story 0.62, "
                 "paisagem 1.1)")
def m_janela(ctx, t, W, H, lines, info, foto=None, **_):
    """O símbolo inteiro vira janela para a foto; fora dele, a cor da marca. Vertical: símbolo pousado na borda de
    baixo, sangrando 8% à direita (largura máx. 78% de W), título na largura útil encostado logo acima dele
    (o vazio fica no alto). Paisagem: símbolo à direita, título à esquerda.
    Assinatura + info empilhadas no canto livre de baixo à esquerda — nunca sobre a foto."""
    c = t.get("colors") or {}
    bg, fg = ctx.col(c.get("bg"), "brand"), ctx.col(c.get("fg"), "ink")
    foto = foto or (ctx.b.path(t["foto"]) if t.get("foto") else None)
    m = ctx.m * min(W, H)
    wide = _wide(W, H)
    vx, vy, vw, vh = viewbox(ctx.sym)
    if wide:
        sh = H * t.get("symbol_h_wide", 1.1)
        sw = vw * sh / vh
        sx, sy = W - sw - m * 0.4, H - sh * 0.96
    else:
        sh = H * (t.get("symbol_h_story", 0.62) if H > W * 1.5 else t.get("symbol_h", 0.66))
        sh = min(sh, W * 0.78 * vh / vw)          # largura máx. 78% de W: sobra canto livre para a assinatura
        sw = vw * sh / vh
        sx, sy = W - sw * 0.92, H - sh
    under = f'<rect width="{W}" height="{H}" fill="{bg}"/>' + place(ctx.sym, sx, sy, h=sh, fill=fg)[0]
    mask = f'<rect width="{W}" height="{H}" fill="#000"/>' + place(ctx.sym, sx, sy, h=sh, fill="#FFFFFF")[0]
    lh = 0.042 * min(W, H)
    bw, bh = (sx - 2 * m, H - 2 * m - lh * 2.6) if wide else (W - 2 * m, sy - 1.6 * m)
    g, _, bottom = headline(ctx, lines, m, m, bw, bh, fg)
    if not wide:   # a frase desce até encostar no símbolo: o peso fica embaixo, o vazio sobe (nada de buraco no meio)
        g = f'<g transform="translate(0 {max(0, (sy - 0.7 * m) - bottom):.1f})">{g}</g>'
    over = g + signature(ctx, W, H, fg, info, stack=True, max_info_w=sx - 2 * m)
    return {"under": under, "over": over, "mask": mask, "foto": foto}


@model("numeral", "numero (ex.: 20H; ou --numero) · device (svg de elementos/, atrás à direita) · "
                  "colors{bg=ink, fg=paper, device=brand, kicker=paper}")
def m_numeral(ctx, t, W, H, lines, info, numero=None, **_):
    """Um número/hora é o herói (88% da largura útil; 50% em paisagem) com o elemento da marca atrás, sangrando à
    direita. A 1ª linha do texto (ex.: o dia) cola em cima do número com 30% do corpo — dia e hora são um bloco."""
    c = t.get("colors") or {}
    bg, fg = ctx.col(c.get("bg"), "ink"), ctx.col(c.get("fg"), "paper")
    numero = numero or t.get("numero", "20H")
    m = ctx.m * min(W, H)
    wide = _wide(W, H)
    body = f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    dev = ctx.svg(t["device"]) if t.get("device") else None
    if dev:
        eh = H * (0.92 if not wide else 1.35)
        vx, vy, vw, vh = viewbox(dev)
        body += place(dev, W - vw * eh / vh * (0.78 if not wide else 0.9), H * 0.04 if not wide else -H * 0.18,
                      h=eh, fill=ctx.col(c.get("device"), "brand"))[0]
    f = font(ctx.display)
    tw = (W - 2 * m) * (0.88 if not wide else 0.5)
    size = tw / f.width(numero, 1, -0.02)
    base = H - m - 0.1 * min(W, H)
    body += f'<path d="{f.path(numero, size, m, base, -0.02)}" fill="{fg}"/>'
    if lines and lines[0]:
        kick = lines[0].replace("~", "")
        ks = min(size * 0.3, tw / max(f.width(kick, 1, -0.01), 1e-6))
        body += (f'<path d="{f.path(kick, ks, m, base - f.cap * size - f.cap * ks * 0.55, -0.01)}" '
                 f'fill="{ctx.col(c.get("kicker"), "paper")}"/>')
        if len(lines) > 1:
            g, _, _ = headline(ctx, lines[1:], m, m, (W - 2 * m) * (0.55 if not wide else 0.4), H * 0.16, fg)
            body += g
    return body + signature(ctx, W, H, fg, info)


@model("contagem", "numero (ou --numero) · texto 'RÓTULO|RÓTULO' (antes|depois do número) · "
                   "colors{bg=accent, fg=paper, number=brand}")
def m_contagem(ctx, t, W, H, lines, info, numero=None, **_):
    """Lê-se em ordem: rótulo · NÚMERO gigante · rótulo (ex.: FALTAM · 3 · NOITES). Vertical: rótulos na largura útil
    (máx. 11% de H), número no espaço entre eles. Paisagem: tudo numa linha, número com 80% de H."""
    c = t.get("colors") or {}
    bg, fg, nc = ctx.col(c.get("bg"), "accent"), ctx.col(c.get("fg"), "paper"), ctx.col(c.get("number"), "brand")
    numero = numero or t.get("numero", "16")
    m = ctx.m * min(W, H)
    body = f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    f = font(ctx.display)
    top = lines[0] if lines else ""
    rest = " ".join(lines[1:]) if len(lines) > 1 else ""
    foot = 0.1 * min(W, H)
    if not _wide(W, H):
        lab = min((W - 2 * m) / max(f.width(top, 1, -0.01), f.width(rest, 1, -0.01), 1e-6), H * 0.11 / f.cap)
        cl = f.cap * lab
        y1 = m + cl * 1.1
        yb = H - m - foot - cl * 0.4
        body += f'<path d="{f.path(top, lab, m, y1, -0.01)}" fill="{fg}"/>'
        body += f'<path d="{f.path(rest, lab, m, yb, -0.01)}" fill="{fg}"/>'
        a0, a1 = y1 + cl * 0.5, yb - cl * 1.5
        size = min((a1 - a0) / f.cap, (W - 2 * m) / f.width(numero, 1, -0.04))
        body += f'<path d="{f.path(numero, size, m, a1, -0.04)}" fill="{nc}"/>'
    else:
        size, lab, gap = H * 0.8 / f.cap, H * 0.13 / f.cap, 0.03 * W
        nw, wt, wr = f.width(numero, size, -0.04), f.width(top, lab, -0.01), f.width(rest, lab, -0.01)
        k = min(1.0, (W - 2 * m) / (wt + nw + wr + 2 * gap))
        size, lab, gap, nw, wt, wr = size * k, lab * k, gap * k, nw * k, wt * k, wr * k
        x = (W - (wt + gap + nw + gap + wr)) / 2
        base = H - m - foot - 0.02 * H
        body += f'<path d="{f.path(top, lab, x, base, -0.01)}" fill="{fg}"/>'
        body += f'<path d="{f.path(numero, size, x + wt + gap, base, -0.04)}" fill="{nc}"/>'
        body += f'<path d="{f.path(rest, lab, x + wt + gap + nw + gap, base, -0.01)}" fill="{fg}"/>'
    return body + signature(ctx, W, H, fg, info)


@model("padrao", "colors{bg=brand, fg=ink, panel=paper, text=ink} · alternate: espelho|girar|nenhum · cols (4; "
                 "8 em paisagem) · panel (fração da altura, 0.6)")
def m_padrao(ctx, t, W, H, lines, info, **_):
    """Padrão de pertencimento: o símbolo em grade (78% da célula), alternando em xadrez (espelho/girar), e um painel
    para a mensagem (60% da altura embaixo; metade esquerda em paisagem)."""
    c = t.get("colors") or {}
    bg, fg = ctx.col(c.get("bg"), "brand"), ctx.col(c.get("fg"), "ink")
    panel, tc = ctx.col(c.get("panel"), "paper"), ctx.col(c.get("text"), "ink")
    alt = t.get("alternate", "espelho")
    m = ctx.m * min(W, H)
    wide = _wide(W, H)
    cols = t.get("cols", 4) * (2 if wide else 1)
    cell = W / cols
    vx, vy, vw, vh = viewbox(ctx.sym)
    body = f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    for r in range(int(H / cell) + 2):
        for cc in range(cols):
            h = cell * 0.78
            w = vw * h / vh
            odd = bool((r + cc) % 2)
            body += place(ctx.sym, cc * cell + (cell - w) / 2, r * cell + (cell - h) / 2 - cell * 0.35, h=h, fill=fg,
                          mirror=odd and alt == "espelho", rot=180 if odd and alt == "girar" else 0)[0]
    ph = H * (t.get("panel", 0.6) if not wide else 1.0)
    pw = W if not wide else W * 0.46
    body += f'<rect x="0" y="{H - ph:.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="{panel}"/>'
    g, _, _ = headline(ctx, lines, m, H - ph + m, pw - 2 * m, ph - 2 * m - 0.07 * min(W, H), tc)
    return body + g + signature(ctx, W, H, tc, info if not wide else "")


@model("elemento", "device (svg de elementos/) · colors{bg=ink, fg=paper, device=brand} · device_h (0.52; "
                   "1.1 em paisagem)")
def m_elemento(ctx, t, W, H, lines, info, **_):
    """Um elemento da marca grande (52% de H no alto à direita; 110% sangrando em paisagem) + título de 60% de H para
    baixo (à esquerda em paisagem)."""
    c = t.get("colors") or {}
    bg, fg = ctx.col(c.get("bg"), "ink"), ctx.col(c.get("fg"), "paper")
    m = ctx.m * min(W, H)
    wide = _wide(W, H)
    dev = ctx.svg(t["device"]) if t.get("device") else ctx.sym
    body = f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    fh = H * (t.get("device_h", 0.52) if not wide else 1.1)
    vx, vy, vw, vh = viewbox(dev)
    fw = vw * fh / vh
    body += place(dev, W - fw - m * 0.2 if not wide else W * 0.95 - fw, m * 0.6 if not wide else -H * 0.05, h=fh,
                  fill=ctx.col(c.get("device"), "brand"))[0]
    if wide:
        g, _, _ = headline(ctx, lines, m, m, W * 0.5, H - 2 * m - 0.1 * H, fg)
    else:
        g, _, _ = headline(ctx, lines, m, H * 0.6, W - 2 * m, H * 0.4 - m - 0.09 * min(W, H), fg)
    return body + g + signature(ctx, W, H, fg, info)


def dots_from(svg_body, W, H, cell, fill, r=0.42):
    """Formas chapadas (fill #000) → esferas numa grade `cell`; esfera onde a forma cobre ≥ 50% da célula."""
    import numpy as np
    import tempfile
    from PIL import Image
    tmp = os.path.join(tempfile.gettempdir(), f"_dots_{os.getpid()}.png")
    svg_to_png(wrap_svg(W, H, svg_body), tmp)
    a = np.array(Image.open(tmp).convert("RGBA"))[:, :, 3] > 127
    os.remove(tmp)
    out = []
    y = cell / 2
    while y < H:
        x = cell / 2
        while x < W:
            blk = a[int(max(0, y - cell / 2)):int(y + cell / 2), int(max(0, x - cell / 2)):int(x + cell / 2)]
            if blk.size and blk.mean() >= 0.5:
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{cell * r:.2f}"/>')
            x += cell
        y += cell
    return f'<g fill="{fill}">{"".join(out)}</g>'


@model("pontilhado", "colors{bg=ink, dots=#9A9C9E, lit=brand, fg=paper} · font (peso menor, ex. 'Família:700', "
                     "para miolos abertos) · cell (11 = esfera é 1/11 da maiúscula)")
def m_pontilhado(ctx, t, W, H, lines, info, **_):
    """A frase 'apagada' em esferas e a palavra com ~ 'acesa' (chapada na cor lit). O símbolo apagado ocupa a sobra
    (≥ 12% de H) pousado na base; em paisagem, à direita. Só display grande; info sempre chapada."""
    c = t.get("colors") or {}
    bg, fg = ctx.col(c.get("bg"), "ink"), ctx.col(c.get("fg"), "paper")
    dots, lit_c = ctx.col(c.get("dots") or "#9A9C9E"), ctx.col(c.get("lit"), "brand")
    spec = t.get("font") or ctx.display
    m = ctx.m * min(W, H)
    wide = _wide(W, H)
    body = f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    vx, vy, vw, vh = viewbox(ctx.sym)
    wsx = W - vw * (H * 1.05) / vh * 0.92
    bw = (wsx - 2 * m) if wide else (W - 2 * m)
    bh = H - 2 * m - 0.12 * min(W, H)
    f = font(spec)
    if len(lines) == 1 and " " in lines[0]:
        lines = best_breaks(spec, lines[0].split(" "), bw, bh, ctx.lead)
    wmax = max(f.width(ln.replace("~", ""), 1, -0.01) for ln in lines)
    size = min(bw / wmax, bh / (f.cap * (1 + (len(lines) - 1) * ctx.lead) + f.cap * 0.25))
    cap = f.cap * size
    cell = max(cap / t.get("cell", 11), 0.007 * min(W, H))
    off, lit = [], []
    y = m + cap * 1.12
    for ln in lines:
        cx = m
        words = ln.split(" ")
        for i, word in enumerate(words):
            on = word.startswith("~")
            word = word.lstrip("~")
            (lit if on else off).append(f'<path d="{f.path(word, size, cx, y, -0.01)}" fill="#000"/>')
            cx += f.width(word + (" " if i < len(words) - 1 else ""), size, -0.01)
        y += cap * ctx.lead
    bottom = y - cap * ctx.lead + cap * 0.2
    free = (H - m - 0.1 * min(W, H)) - (bottom + m)
    sym_in = False
    if not wide and free >= 0.12 * H:
        sh = free + m + 0.1 * min(W, H)
        off.append(place(ctx.sym, W - vw * sh / vh * 0.8, H - sh, h=sh, fill="#000")[0])
        sym_in = True
    elif wide:
        off.append(place(ctx.sym, wsx, H - H * 1.05, h=H * 1.05, fill="#000")[0])
        sym_in = True
    body += dots_from("".join(off), W, H, cell, dots)
    body += "".join(x.replace('fill="#000"', f'fill="{lit_c}"') for x in lit)
    return body + signature(ctx, W, H, fg, info, stack=sym_in)


# ------------------------------------------------------------------ render
def composite_photo(png, parts, W, H):
    """Foto (cover) só dentro da máscara do símbolo; o texto volta por cima (nunca fica sob a foto)."""
    from PIL import Image
    base = Image.open(png).convert("RGB")
    tmp = png + ".mask.png"
    svg_to_png(wrap_svg(W, H, parts["mask"]), tmp)
    mask = Image.open(tmp).convert("L")
    im = Image.open(parts["foto"]).convert("RGB")
    k = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    base.paste(im.crop((l, t, l + W, t + H)), (0, 0), mask)
    svg_to_png(wrap_svg(W, H, parts["over"]), tmp)
    over = Image.open(tmp).convert("RGBA")
    base.paste(over, (0, 0), over)
    base.save(png)
    os.remove(tmp)


def template(b, tid):
    for t in b.get("templates") or []:
        if t.get("id") == tid:
            return t
    raise SystemExit(f"modelo '{tid}' não existe em brand.json templates (veja: modelos.py list {b.dir})")


def render_one(ctx, t, fmt, texto, info, foto=None, numero=None):
    """→ (svg, parts|None) de UMA peça; parts quando há foto a compor."""
    W, H = FORMATS[fmt]
    lines = [x for x in (texto or "").split("|") if x]
    fn = TYPES[t.get("model", "tipo")][0]
    body = fn(ctx, t, W, H, lines, info, foto=foto, numero=numero)
    if isinstance(body, dict):
        return wrap_svg(W, H, body["under"] + body["over"]), (body if body.get("foto") else None)
    return wrap_svg(W, H, body), None


def render(b, tid, texto, info, fmts, out_dir=None, foto=None, numero=None, ctx=None):
    t = template(b, tid)
    ctx = ctx or Ctx(b)
    out_dir = out_dir or os.path.join(b.dir, "aplicacoes", tid)
    os.makedirs(os.path.join(out_dir, "pecas"), exist_ok=True)
    outs = []
    for fm in fmts:
        W, H = FORMATS[fm]
        svg, parts = render_one(ctx, t, fm, texto, info, foto, numero)
        base = os.path.join(out_dir, "pecas", f"{tid}-{W}x{H}")
        write(base + ".svg", svg)
        svg_to_png(svg, base + ".png")
        if parts:
            composite_photo(base + ".png", parts, W, H)
        outs.append(base + ".png")
    return outs


def command_for(b, t, s):
    parts = [f'python modelos.py render <marca> {t["id"]}']
    if s.get("texto"):
        parts.append(f'--texto "{s["texto"]}"')
    if s.get("info"):
        parts.append(f'--info "{s["info"]}"')
    if s.get("numero"):
        parts.append(f'--numero {s["numero"]}')
    if s.get("foto"):
        parts.append(f'--foto {s["foto"]}')
    return " ".join(parts)


def cmd_kit(a):
    b = load_brand(a.brand)
    ctx = Ctx(b)
    fmts = a.formatos.split(",") if a.formatos else None
    for t in b.get("templates") or []:
        s = t.get("sample") or {}
        if not s:
            continue
        f = fmts or s.get("formatos") or ["post", "feed", "story", "banner", "outdoor"]
        foto = b.path(s["foto"]) if s.get("foto") else None
        outs = render(b, t["id"], s.get("texto", ""), s.get("info", ""), f, foto=foto, numero=s.get("numero"),
                      ctx=ctx)
        pick = [o for o in outs if any(k in o for k in ("1080x1350", "1080x1920", "1920x1080"))] or outs
        t["examples"] = [b.rel(o) for o in pick[:3]]
        t.setdefault("command", command_for(b, t, s))
        print(f"{t['id']:<12} {t.get('model', 'tipo'):<11} {len(outs)} peças")
    b.save()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("tipos").set_defaults(fn=lambda a: [print(f"{k:<11} {TYPES[k][0].__doc__.split(chr(10))[0]}\n"
                                                            f"{'':<11} {TYPES[k][1]}") for k in TYPES])
    p = sp.add_parser("list"); p.add_argument("brand")
    p.set_defaults(fn=lambda a: [print(f"{t['id']:<12} {t.get('model', 'tipo'):<11} {t.get('name', '')}")
                                 for t in load_brand(a.brand).get("templates") or []])
    p = sp.add_parser("render"); p.add_argument("brand"); p.add_argument("id")
    p.add_argument("--texto", default=""); p.add_argument("--info", default=""); p.add_argument("--foto")
    p.add_argument("--numero"); p.add_argument("--formatos", default="post,feed,story,banner,outdoor")
    p.add_argument("-o")
    p.set_defaults(fn=lambda a: print("\n".join(render(load_brand(a.brand), a.id, a.texto, a.info,
                                                       a.formatos.split(","), a.o, a.foto, a.numero))))
    p = sp.add_parser("kit"); p.add_argument("brand"); p.add_argument("--formatos"); p.set_defaults(fn=cmd_kit)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
