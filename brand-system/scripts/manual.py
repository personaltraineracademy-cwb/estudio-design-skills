"""Brand manual (brandbook): fixed-layout 16:9 pages in one HTML (brand fonts embedded) → PDF (headless Chrome) +
web version + one PNG per page + contact sheet. Content comes from brand.json and the files the other scripts made.

Usage:
  python manual.py build <brand_dir> [--inline] [--no-pdf] [--no-png]
     → manual/manual.html, manual/manual.pdf, manual/paginas/NN.png, manual/folha.png
  --inline   embed every image (self-contained single HTML, e.g. to publish as an Artifact; larger file)

Chapters (skipped automatically when there is no data): capa · índice · essência · logo · cor · PRODUTOS ·
tipografia · elementos gráficos · grid e layout · imagem · ícones · movimento · voz · modelos de peça · aplicações ·
design system (+ tokens/demo.png e os blocos de tokens/demo/) · recursos.
Produtos (brand.json "products" + "products_rule"): faixa com as cores na capa; abertura com todos lado a lado; por
produto: abertura no fundo dele, logos (+ símbolos como avatar redondo de 48 px reais), cor (HEX/RGB/CMYK + pares de
contraste com nota AA/AAA), aplicações em tamanho proporcional e regras / não fazer.
Write the TEXT in brand.json (platform.*, *.rules, imagery.*, motion.principles, voice.*) — the script only lays it
out. Every rule should carry a number or an example; vague adjectives make decorative manuals.
"""
import argparse
import base64
import datetime
import glob
import html
import math
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import (A_DEFINIR, ARTE_POR_SITE, PILL, STEP_NAMES, a_definir, brand_font_faces,  # noqa: E402
                   color_pairs_cvd, color_tree, contrast, find_chrome, fmt_ratio, font, html_screenshot, ink_on, load_brand,
                   luminance, never_round_labels, nested_radius, product_pairs, products, recolor, shape_spec,
                   simulate, slugify, solid, svg_inner, text_width, vazio, viewbox, write)

E = html.escape
# chaves do brand.json que não são conteúdo de manual (metadados, entrada de outros scripts) — fora da cobertura
COBERTURA_IGNORA = {"name", "slug", "client", "status", "mode", "primitives", "board", "mockups", "applications",
                    "demo", "briefing", "fontes_da_verdade", "nome_curto"}   # entrada do projeto / metadados
SUB_IGNORA = {"nota", "note", "fonte", "codigo", "aviso", "status", "decidido"}


# ------------------------------------------------------------------ helpers
class Ctx:
    def __init__(self, b, inline):
        self.b, self.inline = b, inline
        # cobertura: toda leitura de b.get("a.b…") marca "a.b"; ler o bloco inteiro ("a") marca "a.*"
        self.used = set()
        orig = b.get

        def tracked(dotted, default=None):
            parts = dotted.split(".")
            self.used.add(parts[0] + ".*" if len(parts) == 1 else ".".join(parts[:2]))
            return orig(dotted, default)
        b.get = tracked
        self.ink, self.paper = b.colour("ink"), b.colour("paper", "#F4F3EF")
        self.brand = b.colour("brand")
        self.accent = b.colour("accent", self.brand)
        self.mdir = os.path.join(b.dir, "manual")
        self.pages = []           # (chapter, html)
        self.chapters = []        # (num, title, page index)
        self.skipped = []         # capítulos pulados (sem dados) → avisados no fim

    def skip(self, chapter, why):
        self.skipped.append(chapter)
        print(f"  aviso: capítulo '{chapter}' pulado — {why}")

    def light(self, path, max_side=1600):
        """Cópia leve para o manual: lado maior ≤ 1600 px; sem transparência → JPEG 85. Mantém o PDF em poucos MB
        (as peças originais em PNG 2K/3000 px faziam o PDF passar de 30 MB)."""
        if path.lower().endswith(".svg"):
            return path
        from PIL import Image
        cache = os.path.join(self.mdir, "_img")
        os.makedirs(cache, exist_ok=True)
        key = os.path.relpath(path, self.b.dir).replace("\\", "_").replace("/", "_").replace(":", "")
        im = Image.open(path)
        has_alpha = im.mode in ("RGBA", "LA") and im.getextrema()[-1][0] < 255
        out = os.path.join(cache, os.path.splitext(key)[0] + (".png" if has_alpha else ".jpg"))
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(path):
            im.thumbnail((max_side, max_side))
            if has_alpha:
                im.save(out, optimize=True)
            else:
                im.convert("RGB").save(out, "JPEG", quality=85, optimize=True)
        return out

    def img(self, path, cls="", style=""):
        if not path or not os.path.exists(path):
            return ""
        path = self.light(path)
        if self.inline:
            ext = os.path.splitext(path)[1].lower().lstrip(".")
            mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "svg": "image/svg+xml"}.get(ext, "image/png")
            src = f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()
        else:
            src = os.path.relpath(path, self.mdir).replace("\\", "/")
        return f'<img src="{src}" class="{cls}" style="{style}" alt="">'


def svg_box(svg_text, w="100%", h="100%", colour=None, align="xMidYMid", style=""):
    s = solid(svg_text, colour) if colour else svg_text
    vx, vy, vw, vh = viewbox(s)
    return (f'<svg viewBox="{vx:g} {vy:g} {vw:g} {vh:g}" width="{w}" height="{h}" preserveAspectRatio="{align} meet" '
            f'style="{style}" xmlns="http://www.w3.org/2000/svg">{svg_inner(s)}</svg>')


def read(path):
    return open(path, encoding="utf-8").read() if path and os.path.exists(path) else None


def logo_files(b):
    out = {}
    for k in ("primary", "vertical", "symbol", "wordmark"):
        p = b.path(b.get(f"logo.{k}"))
        if p and os.path.exists(p):
            out[k] = read(p)
    if not out:
        prov = os.path.join(b.dir, "logo", "wordmark-provisorio.svg")
        if os.path.exists(prov):
            out["primary"] = read(prov)
    if "symbol" not in out:   # no symbol file: the first primitive is the brand's form
        for pr in b.get("primitives") or []:
            p = b.path(pr.get("src"))
            if p and os.path.exists(p):
                out["_form"] = read(p)
                break
    return out


CSS = """
@page { size: 1920px 1080px; margin: 0 }
* { box-sizing: border-box; margin: 0; padding: 0 }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact }
body { background: #C9C9C4; font-family: brand-text, system-ui, sans-serif; color: __INK__ }
.page { width: 1920px; height: 1080px; position: relative; overflow: hidden; background: __PAPER__;
        padding: 150px 120px 110px; break-after: page; page-break-after: always }
@media screen { .page { margin: 40px auto; box-shadow: 0 12px 48px rgba(0,0,0,.18) } }
.hdr, .ftr { position: absolute; left: 120px; right: 120px; display: flex; justify-content: space-between;
             font-size: 17px; letter-spacing: .06em; text-transform: uppercase; opacity: .62 }
.hdr { top: 56px } .ftr { bottom: 48px; text-transform: none; letter-spacing: .02em }
.dark { background: __INK__; color: __PAPER__ } .brand { background: __BRAND__; color: __ONBRAND__ }
h1 { font-family: brand-display; font-size: 150px; line-height: .92; letter-spacing: -.025em }
h2 { font-family: brand-display; font-size: 76px; line-height: .98; letter-spacing: -.015em; margin-bottom: 36px }
h3 { font-family: brand-display; font-size: 36px; line-height: 1.05; margin-bottom: 12px }
.lead { font-size: 34px; line-height: 1.32; max-width: 1180px }
p, li { font-size: 22px; line-height: 1.45 } .small { font-size: 17px; opacity: .72 }
.label { font-size: 15px; letter-spacing: .1em; text-transform: uppercase; opacity: .6; margin-bottom: 10px }
.row { display: flex; gap: 40px } .col { flex: 1; min-width: 0 }
.g2 { display: grid; grid-template-columns: 1fr 1fr; gap: 40px }
.g3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 36px }
.g4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 28px }
.card { border-top: 3px solid currentColor; padding-top: 22px }
.box { border-radius: 4px; overflow: hidden; position: relative }
.fill img { width: 100%; height: 100%; object-fit: contain; display: block }
.cover img { width: 100%; height: 100%; object-fit: cover; display: block }
.opener .num { font-family: brand-display; font-size: 640px; line-height: .78; position: absolute; right: 100px;
               bottom: 70px; letter-spacing: -.04em }
.opener h1 { position: absolute; left: 120px; bottom: 120px; max-width: 900px }
.no { position: relative } .no::after { content: ""; position: absolute; inset: 0;
      background: linear-gradient(to top right, transparent calc(50% - 2px), #E5322D calc(50% - 2px),
      #E5322D calc(50% + 2px), transparent calc(50% + 2px)) }
.tag { display: inline-block; font-size: 15px; padding: 6px 12px; border: 1.5px solid currentColor; border-radius: 99px }
.adef { border-bottom: 2px dashed currentColor; font-style: italic }
.status { display: inline-block; font-size: 15px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
          padding: 5px 12px; border: 1.5px dashed currentColor }
table.t { width: 100%; border-collapse: collapse; font-size: 19px; line-height: 1.3 }
table.t th { text-align: left; font-size: 14px; letter-spacing: .1em; text-transform: uppercase; opacity: .7;
             padding: 0 14px 10px 0; border-bottom: 2px solid currentColor; font-weight: 700 }
table.t td { padding: 10px 14px 10px 0; border-bottom: 1.5px solid rgba(0,0,0,.12); vertical-align: top }
.sw { display: inline-block; width: 26px; height: 26px; vertical-align: -6px; margin-right: 10px;
      box-shadow: inset 0 0 0 1.5px rgba(0,0,0,.25) }
.ok { font-weight: 700 } .ko { font-weight: 700; color: #B3261E }
code, pre { font-family: ui-monospace, Consolas, monospace; font-size: 17px; line-height: 1.5 }
pre { background: rgba(0,0,0,.06); padding: 28px; border-radius: 6px; white-space: pre-wrap }
.toc { columns: 2; column-gap: 120px } .toc div { display: flex; justify-content: space-between;
       font-size: 32px; padding: 14px 0; border-bottom: 1.5px solid rgba(0,0,0,.15); break-inside: avoid }
.toc b { font-family: brand-display; font-weight: inherit; margin-right: 22px }
"""


def page(ctx, chapter, body, cls="", hdr=True, style=""):
    b = ctx.b
    n = len(ctx.pages) + 1
    h = (f'<div class="hdr"><span>{E(chapter)}</span><span>{E(b.name)}</span></div>'
         f'<div class="ftr"><span>Manual da marca · {E(str(b.get("status") or "teste"))}</span><span>{n:02d}</span></div>'
         if hdr else "")
    st = f' style="{style}"' if style else ""
    ctx.pages.append((chapter, f'<section class="page {cls}"{st}>{h}{body}</section>'))


def nomes_proposta(prods):
    """True quando os nomes das cores dos produtos ainda são PROPOSTA (aguardam o "sim" da cliente)."""
    return any("proposta" in (p.get("color_name_status") or "").lower() for p in prods)


def h2_badge(title, badge="", sub=""):
    """Título de página com selo de status à direita (tracejado) — ex.: "nomes das cores: proposta"."""
    sub_html = f'<p class="lead" style="font-size:26px;margin:-8px 0 26px;max-width:1500px">{E(sub)}</p>' if sub else ""
    if not badge:
        return f'<h2>{E(title)}</h2>{sub_html}'
    return (f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:40px">'
            f'<h2>{E(title)}</h2><span class="status" style="margin-top:14px;flex:none">{E(badge)}</span></div>{sub_html}')


NOMES_BADGE = "nomes das cores: proposta, aguardando o sim"


def ink_overshoot(b, text, size, tracking=-0.04):
    """px que a TINTA do último glifo passa da caixa CSS do texto (espaçamento negativo + balanço do glifo): o "04"
    e o "01" gigantes das aberturas só alinham na margem direita se cada número for deslocado por este valor."""
    try:
        from fontTools.pens.boundsPen import BoundsPen
        f = font(b.font_spec("display", 800))
        names, adv = f.advances(text, size, tracking)
        k = size / f.upm
        bp = BoundsPen(f.gs)
        f.gs[names[-1]].draw(bp)
        xmax = bp.bounds[2] * k if bp.bounds else adv[-1]
        return sum(adv[:-1]) + xmax - (sum(adv) + tracking * size)
    except Exception:
        return 0.0


def whole_rules(rules, n=300):
    """Junta regras inteiras (nunca corta no meio da frase): entra cada regra enquanto couber em n caracteres; se nem a
    primeira cabe, corta no último ponto/vírgula/espaço e fecha com reticências. Usado nos textos de abertura."""
    rules = [str(r).strip().rstrip(".;") for r in (rules or []) if str(r).strip()]
    out = ""
    for r in rules:
        nxt = r if not out else out + "; " + r
        if len(nxt) > n:
            break
        out = nxt
    if out:
        return out + "."
    if not rules:
        return ""
    r = rules[0]
    cut = r[:n]
    for sep in (". ", "; ", ", ", " "):
        k = cut.rfind(sep)
        if k > n * 0.5:
            return cut[:k].rstrip(",;:") + "…"
    return cut.rstrip() + "…"


def opener(ctx, title, sub=""):
    num = len(ctx.chapters) + 1
    ctx.chapters.append((num, title, len(ctx.pages) + 1))
    ov = ink_overshoot(ctx.b, f"{num:02d}", 640)
    page(ctx, title, f'<div class="num" style="right:{120 + ov:.1f}px">{num:02d}</div><h1>{E(title)}</h1>'
                     + (f'<p class="lead" style="position:absolute;left:120px;top:150px;max-width:900px">{E(sub)}</p>'
                        if sub else ""), "opener brand")


# ------------------------------------------------------------------ chapters
COVER_SYM_LEFT = 1920 + 380 - 1500      # borda esquerda da caixa do símbolo gigante na capa (x = 800)
COVER_TEXT_W = COVER_SYM_LEFT - 120 - 40     # coluna do texto: da margem até 40 px antes do símbolo


def cover_title_px(b, s, max_px=132, min_px=84):
    """Corpo do título da capa: a palavra mais longa cabe na coluna escura (nunca passa por cima do símbolo —
    texto claro sobre a cor da marca dava ~2:1) e o texto todo cabe em até 4 linhas."""
    words = s.split() or [s]
    px = min(fit_px(b, w, COVER_TEXT_W, max_px, min_px=min_px) for w in words)
    # 4 linhas no máximo: reduz até a largura total / coluna ≤ 4 × 0,9
    while px > min_px:
        try:
            tw = text_width(s, px, b.font_spec("display", 800), -0.025)
        except Exception:
            tw = 0.5 * px * len(s)
        if tw / COVER_TEXT_W <= 2.7:
            break
        px -= 4
    return int(px)


def ch_cover(ctx, logos):
    b = ctx.b
    sym = logos.get("symbol") or logos.get("_form") or logos.get("primary")
    big = svg_box(sym, "1500px", "1500px", ctx.brand) if sym else ""
    lg = svg_box(logos.get("primary", ""), "560px", "160px", ctx.paper, "xMinYMax") if logos.get("primary") else ""
    body = (f'<div style="position:absolute;right:-380px;top:-260px;opacity:1">{big}</div>'
            f'<div style="position:absolute;left:120px;top:120px">{lg}</div>'
            f'<h1 style="position:absolute;left:120px;bottom:172px;max-width:{COVER_TEXT_W}px;font-size:'
            f'{cover_title_px(b, b.get("platform.idea") or b.name)}px">'
            f'{E(b.get("platform.idea") or b.name)}</h1>'
            + (f'<p class="small" style="position:absolute;left:120px;bottom:108px">{E(b.get("nome_completo"))}</p>'
               if b.get("nome_completo") and b.get("nome_completo") != b.name else "") +
            f'<p class="small" style="position:absolute;left:120px;bottom:80px">Manual da marca · '
            f'{datetime.date.today():%m/%Y} · {E(str(b.get("status") or "teste"))}</p>')
    prods = products(b)
    if prods:   # faixa com as cores dos produtos, de ponta a ponta no pé da capa
        # colunas iguais dentro das margens (120 px); o 1º e o último segmento esticam até a borda; o 1º nome começa
        # na margem, alinhado com o texto da capa
        w = 1680 / len(prods)
        segs = []
        for i, p in enumerate(prods):
            sw = w + (120 if i == 0 else 0) + (120 if i == len(prods) - 1 else 0)
            segs.append(f'<div style="width:{sw:.2f}px;flex:none;background:{p["colors"]["accent"]};'
                        f'color:{p["colors"]["on_accent"]};display:flex;align-items:center;'
                        f'padding:0 22px 0 {120 if i == 0 else 22}px;font-size:15px;font-weight:700;letter-spacing:.1em;'
                        f'text-transform:uppercase;white-space:nowrap;overflow:hidden">{E(p["name"])}</div>')
        body += ('<div style="position:absolute;left:0;right:0;bottom:0;height:52px;display:flex">' + "".join(segs)
                 + "</div>")
    page(ctx, "capa", body, "dark", hdr=False)


def ch_essence(ctx):
    b = ctx.b
    p = b.get("platform") or {}
    opener(ctx, "Essência", p.get("onlyness") or "")
    blocks = []
    if p.get("idea"):
        blocks.append(f'<div class="label" style="margin-bottom:26px">a ideia</div><h1 style="font-size:128px;'
                      f'margin-bottom:56px">'
                      f'{E(p["idea"])}</h1>')
    sub = []
    if p.get("enemy"):
        sub.append(f'<div class="col card"><div class="label">o que recusamos</div><p>{E(p["enemy"])}</p></div>')
    z = p.get("zag") or {}
    if z.get("keep") or z.get("break"):
        sub.append(f'<div class="col card"><div class="label">zag na categoria</div><p>Mantém: {E(z.get("keep", ""))}'
                   f'<br>Quebra: {E(" · ".join(z.get("break", [])))}</p></div>')
    j = p.get("jobs") or {}
    if any(j.values()):
        sub.append('<div class="col card"><div class="label">o que a marca faz pelas pessoas</div><p>' +
                   "<br>".join(f"<b>{E(k)}</b>: {E(v)}" for k, v in j.items() if v) + "</p></div>")
    page(ctx, "Essência", "".join(blocks) + (f'<div class="row">{"".join(sub)}</div>' if sub else ""))
    tens = p.get("tension") or []
    pers = p.get("personality") or []
    if tens or pers:
        items = "".join(f'<div class="card" style="padding-top:34px"><div style="font-family:brand-display;'
                        f'font-size:88px;line-height:1">{E(t[0] if isinstance(t, list) else t)}</div>'
                        f'<p style="font-size:40px;margin-top:18px;opacity:.55">mas não '
                        f'{E(t[1]) if isinstance(t, list) and len(t) > 1 else ""}</p></div>' for t in tens)
        page(ctx, "Essência", f'<h2>Isso, mas não aquilo</h2><div class="g2" style="row-gap:44px;margin-top:36px">'
                              f'{items}</div>' +
             (f'<p class="lead" style="margin-top:40px">{E(" · ".join(pers))}</p>' if pers else ""))
    pr = p.get("principles") or []
    if pr:
        cards = []
        for i, x in enumerate(pr, 1):
            if isinstance(x, dict):
                cards.append(f'<div class="card"><div class="label">princípio {i:02d}</div><h3>{E(x.get("name", ""))}</h3>'
                             f'<p>{E(x.get("rule", ""))}</p>'
                             + (f'<p style="font-size:19px;line-height:1.4;margin-top:14px"><b>Fazer:</b> {E(x["do"])}</p>' if x.get("do") else "")
                             + (f'<p style="font-size:19px;line-height:1.4;margin-top:8px"><b>Evitar:</b> {E(x["avoid"])}</p>' if x.get("avoid") else "")
                             + (f'<p style="font-size:19px;line-height:1.4;margin-top:8px"><b>Teste:</b> {E(x["test"])}</p>' if x.get("test") else "") + "</div>")
            else:
                cards.append(f'<div class="card"><div class="label">princípio {i:02d}</div><p>{E(x)}</p></div>')
        # 3 princípios por página quando têm fazer/evitar/teste (6 cartões num só 1080 estouravam o rodapé)
        detalhado = any(isinstance(x, dict) and (x.get("do") or x.get("avoid") or x.get("test")) for x in pr)
        por_pag = 3 if (detalhado or len(pr) > 4) else len(pr)
        paginas = [cards[i:i + por_pag] for i in range(0, len(cards), por_pag)]
        for k, grupo in enumerate(paginas, 1):
            tit = "Princípios de design" + (f" ({k}/{len(paginas)})" if len(paginas) > 1 else "")
            cols = "g3" if len(grupo) >= 3 else f"g{len(grupo)}"
            page(ctx, "Essência", f'<h2>{tit}</h2><div class="{cols}">{"".join(grupo)}</div>')


def ch_logo(ctx, logos):
    b = ctx.b
    if not logos:
        return
    opener(ctx, "Logo", b.get("logo.construction") or "")
    prim = logos["primary"]
    page(ctx, "Logo", f'<div class="row" style="height:760px">'
                      f'<div class="col box" style="background:{ctx.paper};border:1.5px solid rgba(0,0,0,.08);'
                      f'display:flex;align-items:center;justify-content:center;padding:120px">'
                      f'{svg_box(prim, "100%", "100%", ctx.ink)}</div>'
                      f'<div class="col box" style="background:{ctx.ink};display:flex;align-items:center;'
                      f'justify-content:center;padding:120px">{svg_box(prim, "100%", "100%", ctx.paper)}</div></div>'
                      f'<p class="small" style="margin-top:24px">Assinatura principal — positiva e negativa.</p>')
    vers = [(k, v) for k, v in logos.items() if not k.startswith("_")]
    if len(vers) > 1:
        cells = "".join(f'<div><div class="box" style="height:420px;background:rgba(0,0,0,.04);display:flex;'
                        f'align-items:center;justify-content:center;padding:70px">{svg_box(v, "100%", "100%", ctx.ink)}'
                        f'</div><p class="small" style="margin-top:12px">{E(k)}</p></div>' for k, v in vers)
        page(ctx, "Logo", f'<h2>Versões</h2><div class="g{min(4, len(vers))}">{cells}</div>')
    conc = [c for c in (b.get("logo.concepts") or []) if isinstance(c, dict)]
    var = b.get("logo.variants") or {}
    cw_ = b.get("logo.colorways") or {}
    if conc or var or cw_:
        cc = "".join(f'<div class="card" style="margin-bottom:22px"><h3>{E(c.get("name", c.get("id", "")))}</h3>'
                     f'<p style="font-size:20px">{E(c.get("idea", ""))}</p>'
                     + (f'<p class="small" style="margin-top:6px">símbolo: {E(c["symbol_idea"])}</p>' if c.get("symbol_idea") else "")
                     + (f'<p class="small">letra em curvas: {E(c["font_in_curves"])}</p>' if c.get("font_in_curves") else "")
                     + '</div>' for c in conc)
        vv = "".join(f'<li style="font-size:18px;margin-bottom:6px"><b>{E(k)}</b>: {E(str(v))}</li>' for k, v in var.items())
        cv = "".join(f'<li style="font-size:17px;margin-bottom:6px"><b>{E(k)}</b>: {E(str(v))}</li>' for k, v in cw_.items())
        page(ctx, "Logo", f'<h2>Conceitos e variantes</h2><div class="row" style="gap:70px"><div class="col">{cc}</div>'
                          f'<div class="col" style="flex:1.3">' + (f'<div class="label">variantes</div><ul style="margin:0 0 24px 22px">'
                                                                   f'{vv}</ul>' if vv else "")
                          + (f'<div class="label">cores e arquivos</div><ul style="margin-left:22px">{cv}</ul>' if cv else "")
                          + '</div></div>')
    # clear space + minimum size
    cs = float(b.get("logo.clearspace") or 0.5)
    vx, vy, vw, vh = viewbox(prim)
    # o desenho (logo + proteção nos 4 lados) cabe na coluna: largura ≤ 820 e altura ≤ 640
    W = min(900, 820 / (1 + 2 * cs * vh / vw), 640 / (vh / vw * (1 + 2 * cs)))
    H = W * vh / vw
    pad = cs * H
    mpx = b.get("logo.min_px") or 24
    _vx, _vy, _vw, _vh = viewbox(prim)
    lw_ = lambda h_: f"{h_ * _vw / _vh:.0f}px"  # noqa: E731
    num = lambda v: f"{v:g}".replace(".", ",")  # noqa: E731
    cap = lambda t_: f'<p class="small" style="margin-top:10px;white-space:nowrap">{t_}</p>'  # noqa: E731
    body = (f'<div class="row"><div class="col"><h2>Área de proteção</h2><p>Margem mínima = {num(cs)} × a altura da '
            f'assinatura (x) em todos os lados. Nada entra nesse espaço: texto, borda, outro logo.</p>'
            f'<h2 style="margin-top:56px">Tamanho mínimo</h2><p>Digital: {mpx} px de altura. '
            f'Impresso: {b.get("logo.min_mm") or 8} mm. Abaixo disso, use o símbolo.</p>'
            f'<div style="margin-top:32px;display:flex;gap:64px;align-items:flex-end">'
            f'<div>{svg_box(prim, lw_(mpx), str(mpx) + "px", ctx.ink, "xMinYMid")}{cap(f"{mpx} px · mínimo")}</div>'
            f'<div>{svg_box(prim, lw_(2 * mpx), str(2 * mpx) + "px", ctx.ink, "xMinYMid")}{cap(f"{2 * mpx} px")}</div></div></div>'
            f'<div class="col" style="display:flex;align-items:center;justify-content:center">'
            f'<div style="position:relative;padding:{pad:.0f}px;outline:2px dashed {ctx.brand};'
            f'background:repeating-linear-gradient(45deg,transparent 0 10px,rgba(0,0,0,.04) 10px 20px)">'
            f'<div style="background:{ctx.paper}">{svg_box(prim, f"{W}px", f"{H:.0f}px", ctx.ink)}</div>'
            f'<span class="small" style="position:absolute;left:8px;top:4px">x</span></div></div></div>')
    regras_medida = [(lab, b.get(k)) for lab, k in (("área de proteção", "logo.clearspace_rule"),
                                                      ("tamanho mínimo", "logo.min_px_rule")) if b.get(k)]
    if b.get("logo.min_px_symbol"):
        regras_medida.append(("símbolo", f"mínimo {b.get('logo.min_px_symbol')} px de altura"))
    if regras_medida:
        body += ('<div style="position:absolute;left:120px;right:120px;bottom:100px;display:flex;gap:40px">' + "".join(
            f'<p style="flex:1;font-size:17px;line-height:1.4"><b>{E(lab)}:</b> {E(str(v))}</p>' for lab, v in regras_medida)
            + "</div>")
    page(ctx, "Logo", body)
    # colourways
    ways = [(ctx.ink, ctx.paper, "positiva"), (ctx.paper, ctx.ink, "negativa"), (ctx.ink, ctx.brand, "sobre a cor"),
            (ctx.brand, ctx.ink, "cor sobre escuro")]
    ok = [(f, bg, n) for f, bg, n in ways if contrast(f, bg) >= 3]
    cells = "".join(f'<div><div class="box" style="height:380px;background:{bg};display:flex;align-items:center;'
                    f'justify-content:center;padding:70px">{svg_box(prim, "100%", "100%", f)}</div>'
                    f'<p class="small" style="margin-top:12px">{n} · contraste {contrast(f, bg):.1f}:1</p></div>'
                    for f, bg, n in ok)
    page(ctx, "Logo", f'<h2>Cores da assinatura</h2><div class="g{min(4, len(ok))}">{cells}</div>')
    # don'ts (generated)
    wrong = [("não distorcer", f'transform:scale(1.35,.7)', ctx.ink, ctx.paper),
             ("não girar", "transform:rotate(-14deg)", ctx.ink, ctx.paper),
             ("não trocar a cor", "", "#6FC7E8", ctx.paper),
             ("não usar contorno", "fill:none;stroke-width:1.5", None, ctx.paper),
             ("não aplicar efeitos", "filter:drop-shadow(10px 10px 0 rgba(0,0,0,.35))", ctx.ink, ctx.paper),
             ("não usar com pouco contraste", "", ctx.brand, b.colour("brand.300", ctx.brand)),
             ("não condensar", "transform:scaleX(.62)", ctx.ink, ctx.paper),
             ("não usar sobre fundo confuso", "", ctx.ink,
              f"repeating-linear-gradient(60deg,{ctx.brand} 0 18px,{ctx.accent} 18px 36px,{ctx.paper} 36px 54px)")]
    cells = []
    for label, style, col, bg in wrong:
        svg = recolor(prim, "none") if col is None else recolor(prim, col)
        inner = svg_box(svg, "100%", "100%", None, style=style + (f";stroke:{ctx.ink}" if col is None else ""))
        cells.append(f'<div><div class="box no" style="height:250px;background:{bg};display:flex;align-items:center;'
                     f'justify-content:center;padding:50px;border:1.5px solid rgba(0,0,0,.06)">{inner}</div>'
                     f'<p class="small" style="margin-top:10px">✕ {E(label)}</p></div>')
    dont = [x for x in (b.get("logo.dont") or []) if str(x).strip()]
    if len(dont) <= 2:
        extra = "".join(f"<li>{E(x)}</li>" for x in dont)
        page(ctx, "Logo", f'<h2>Usos incorretos</h2><div class="g4">{"".join(cells)}</div>' +
             (f'<ul style="margin:30px 0 0 24px">{extra}</ul>' if extra else ""))
    else:   # a grade dos 8 erros numa página e os "nãos" escritos em duas colunas na seguinte
        page(ctx, "Logo", f'<h2>Usos incorretos</h2><div class="g4" style="row-gap:36px">{"".join(cells)}</div>')
        half = math.ceil(len(dont) / 2)
        li_ = lambda xs: "".join(f'<li style="display:flex;gap:14px;list-style:none;margin-bottom:16px;font-size:21px">'  # noqa: E731
                                 f'<b style="flex:none">✕</b><span>{E(x)}</span></li>' for x in xs)
        page(ctx, "Logo", f'<h2>O que nunca fazer com o logo</h2><div class="row" style="gap:70px"><ul class="col" '
                          f'style="margin:0">{li_(dont[:half])}</ul><ul class="col" style="margin:0">{li_(dont[half:])}</ul></div>')


def ch_color(ctx):
    b = ctx.b
    seeds = b.get("color.seeds") or {}
    if not seeds:
        return
    opener(ctx, "Cor", whole_rules(b.get("color.rules")))
    order = [k for k in ("paper", "ink", "brand", "accent") if k in seeds] + \
            [k for k in seeds if k not in ("paper", "ink", "brand", "accent")]
    from palette import describe
    cells = []
    for k in order:
        v = seeds[k]
        hx = v["hex"] if isinstance(v, dict) else v
        d = describe(hx)
        fg = ink_on(hx, "#FFFFFF", "#141414")
        r, g, bb = d["rgb"]
        c, m, y, kk = d["cmyk"]
        cells.append(f'<div class="col box" style="background:{hx};color:{fg};padding:40px;height:680px;'
                     f'display:flex;flex-direction:column;justify-content:space-between;'
                     f'border:1.5px solid rgba(0,0,0,.06)"><div><h3>{E(v.get("name", k) if isinstance(v, dict) else k)}'
                     f'</h3><div class="label" style="opacity:.8">{E(k)}</div></div><p style="font-size:20px">'
                     f'HEX {hx}<br>RGB {r} {g} {bb}<br>CMYK {c} {m} {y} {kk}*<br>OKLCH {d["oklch"][0]} '
                     f'{d["oklch"][1]} {d["oklch"][2]:.0f}</p></div>')
    prop = b.get("color.proportion") or {}
    tot = sum(prop.get(k, 0) for k in order) or 1
    bar = "".join(f'<div style="flex:{prop.get(k, 0)};background:{seeds[k]["hex"] if isinstance(seeds[k], dict) else seeds[k]};'
                  f'height:70px"></div>' for k in order if prop.get(k))
    page(ctx, "Cor", f'<div class="row" style="gap:20px">{"".join(cells)}</div>'
                     f'<div style="display:flex;margin-top:30px;border:1.5px solid rgba(0,0,0,.06)">{bar}</div>'
                     f'<p class="small" style="margin-top:12px">Proporção de uso: ' +
         " · ".join(f"{k} {prop.get(k, 0) * 100 // tot}%" for k in order if prop.get(k)) +
         ' · *CMYK aproximado — aprovar prova de cor com a gráfica (cores muito vivas podem pedir cor especial).</p>')
    ramps = ctx.b.get("color.palette.ramps") or {}
    if ramps:
        rows = ""
        for role, ramp in ramps.items():
            nm = seeds.get(role, {}).get("name", role) if isinstance(seeds.get(role), dict) else role
            rows += (f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:14px"><div style="width:200px;'
                     f'font-size:22px">{E(nm)}</div>' +
                     "".join(f'<div style="flex:1;height:96px;background:{v["hex"]};color:{ink_on(v["hex"])};'
                             f'font-size:14px;padding:8px;display:flex;flex-direction:column;justify-content:flex-end">'
                             f'{s}<br>{v["hex"]}</div>' for s, v in ramp.items()) + "</div>")
        extra = "".join(f'<p style="font-size:19px;margin-top:10px"><b>{lab}:</b> {E(b.get(k))}</p>'
                        for lab, k in (("Acento", "color.accent_decisao"), ("Proporção medida", "color.proportion_rule"))
                        if b.get(k))
        page(ctx, "Cor", f'<h2>Escalas de tom</h2>{rows}<p class="small" style="margin-top:20px">Tons gerados em '
                         f'OKLCH a partir das cores-semente (a semente exata fica dentro da escala). Uso: fundos (50–200), '
                         f'bordas (300–400), cor sólida (500–600), texto (700–950).</p>{extra}')
    cpath = os.path.join(b.dir, "cores", "contraste.png")
    if os.path.exists(cpath):
        page(ctx, "Cor", f'<div class="row"><div class="col" style="flex:.8"><h2>Pares aprovados</h2>'
                         f'<p>Cada combinação texto × fundo com contraste WCAG 2 e APCA. Texto corrido só nos pares '
                         f'"texto corrido" ou "texto longo"; os marcados em vermelho nunca levam texto.</p></div>'
                         f'<div class="col fill" style="flex:1.2;height:800px">{ctx.img(cpath)}</div></div>')


# ------------------------------------------------------------------ produtos (sub-identidades por cor)
def fit_px(b, s, max_w, max_px, tracking=-0.025, min_px=40):
    """Maior corpo (px) em que a linha s cabe em max_w, medido na fonte display da marca."""
    try:
        w = text_width(s, 100, b.font_spec("display", 800), tracking) / 100
    except Exception:
        w = 0.62 * len(s)
    return int(max(min_px, min(max_px, max_w / max(w, 1e-6))))


def name_px(b, name, max_w, max_px, min_px=40):
    """Corpo do nome: a palavra mais longa cabe na largura (o nome pode quebrar em linhas, a palavra não)."""
    words = name.split() or [name]
    return min(fit_px(b, w, max_w, max_px, min_px=min_px) for w in words)


def _existing(ctx, items, what, pname):
    """Itens de products[] cujo arquivo existe; avisa no terminal os que faltam."""
    out = []
    for it in items or []:
        src = it if isinstance(it, str) else it.get("src")
        p = ctx.b.path(src)
        if p and os.path.exists(p):
            out.append((p, it if isinstance(it, dict) else {"src": it}))
        else:
            msg = f"  aviso: produto {pname} · {what} não encontrado: {src}"
            seen = ctx.__dict__.setdefault("_avisos", set())
            if msg not in seen:
                seen.add(msg)
                print(msg)
    return out


def avatar(svg, bg, px):
    """Símbolo recortado em círculo (foto de perfil/grupo) com diâmetro px; o símbolo ocupa 66% (cabe no círculo)."""
    return (f'<div style="width:{px}px;height:{px}px;border-radius:50%;background:{bg};display:flex;flex:none;'
            f'align-items:center;justify-content:center;overflow:hidden;box-shadow:0 0 0 1px rgba(0,0,0,.18)">'
            f'{svg_box(svg, "66%", "66%")}</div>')


def _overview_logo_index(ctx, prods):
    """Qual logo (posição em products[].logos) aparece nos cartões da visão geral: o que vive no fundo nativo do
    produto na maioria deles — assim os 4 cartões mostram o mesmo desenho e quase todos sem painel de cor."""
    best, best_n = 0, -1
    for i in range(max((len(p.get("logos") or []) for p in prods), default=1)):
        n = 0
        for p in prods:
            lg = p.get("logos") or []
            if i < len(lg) and isinstance(lg[i], dict) and (lg[i].get("bg") or "").lower() == p["colors"]["bg"].lower():
                n += 1
        if n > best_n:
            best, best_n = i, n
    return best


def est_h(items, fs, width, gap=14, lh=1.45):
    """Altura estimada (px) de uma lista de textos corridos: largura média da letra ≈ 0,53 × corpo (Archivo)."""
    per = max(8, int(width / (fs * 0.53)))
    return sum(math.ceil(len(str(x)) / per) * fs * lh + gap for x in items)


def ch_products(ctx):
    """Produtos (brand.json "products"): abertura com a regra de convivência e todos lado a lado; depois, por
    produto, abertura no fundo dele, logos (+ símbolos como avatar de 48 px reais), cor com contraste, aplicações
    em tamanho proporcional e regras / não fazer."""
    b = ctx.b
    prods = products(b)
    if not prods:
        return
    from PIL import Image
    from palette import describe
    n = len(prods)
    opener(ctx, "Produtos", f"Uma marca-mãe e {n} produto{'s' if n > 1 else ''}: cada um com a sua cor, todos com "
                            f"as mesmas regras.")
    pg_architecture(ctx, prods)
    # --- visão geral: regra + produtos lado a lado (mesma altura, mesmo painel de logo em todos os cartões)
    colw = (1680 - (n - 1) * 28) / n
    idx = _overview_logo_index(ctx, prods)
    cells = []
    for i, p in enumerate(prods, 1):
        c = p["colors"]
        logos = _existing(ctx, p.get("logos"), "logo", p["id"])
        lg = ""
        if logos:
            path, it = logos[min(idx, len(logos) - 1)]
            pbg = it.get("bg") or c["bg"]
            edge = "rgba(255,255,255,.16)" if luminance(pbg) < 0.2 else "rgba(0,0,0,.12)"
            lg = (f'<div style="height:190px;flex:none;margin:0 28px;background:{pbg};display:flex;align-items:center;'
                  f'justify-content:center;padding:26px;border:1.5px solid {edge}">{svg_box(read(path), "100%", "100%")}</div>')
        num = p.get("order") if isinstance(p.get("order"), int) else i
        cells.append(
            f'<div style="flex:1;min-width:0;background:{c["bg"]};color:{c["ink"]};display:flex;flex-direction:column;'
            f'border:1.5px solid rgba(0,0,0,.08)"><div style="background:{c["accent"]};color:{c["on_accent"]};'
            f'padding:14px 28px;display:flex;justify-content:space-between;align-items:baseline;gap:18px">'
            f'<span style="font-family:brand-display;font-size:64px;line-height:1">{num:02d}</span>'
            f'<span style="font-size:16px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;text-align:right;'
            f'line-height:1.25">'
            f'{E(p.get("tag") or "")}</span></div><div style="height:24px;flex:none"></div>{lg}'
            f'<div style="padding:22px 28px 26px"><h3 style="font-size:{name_px(b, p["name"], colw - 60, 46, min_px=24)}px;'
            f'line-height:1.02;margin-bottom:10px">{E(p["name"])}</h3><p style="font-size:20px;line-height:1.35">'
            f'{E(p.get("sub") or "")}</p></div></div>')
    rule = b.get("products_rule") or ""
    page(ctx, "Produtos", f'<h2>Marca-mãe e produtos</h2>' +
         (f'<p class="lead" style="font-size:26px;max-width:1680px;margin:-6px 0 34px">{E(rule)}</p>' if rule else "") +
         f'<div style="display:flex;gap:28px;height:{590 if rule else 700}px">{"".join(cells)}</div>')
    pg_color_tree(ctx)
    pg_matrix(ctx, prods)
    if len(prods) > 1:
        pg_color_a11y(ctx, prods)
    # --- por produto
    for i, p in enumerate(prods, 1):
        c = p["colors"]
        num = p.get("order") if isinstance(p.get("order"), int) else i
        chap = f"Produtos · {p['name']}"
        # abertura no fundo do produto
        npx = name_px(b, p["name"], 1500, 190, min_px=60)
        body = (f'<div class="label" style="opacity:.8">produto {num:02d}</div>'
                + (f'<span class="tag" style="font-size:20px;padding:8px 18px;border-color:{c["accent"]};'
                   f'margin-top:8px">{E(p["tag"])}</span>' if p.get("tag") else "") +
                f'<div style="position:absolute;right:{120 + ink_overshoot(b, f"{num:02d}", 420):.1f}px;top:154px;font-family:brand-display;font-size:420px;'
                f'line-height:1;text-box:trim-both cap alphabetic;letter-spacing:-.04em;color:{c["accent"]}">'
                f'{num:02d}</div>'
                f'<div style="position:absolute;left:120px;right:120px;bottom:130px">'
                f'<h1 style="font-size:{npx}px;max-width:1500px">{E(p["name"])}</h1>'
                + (f'<p class="lead" style="margin-top:28px">{E(p["sub"])}</p>' if p.get("sub") else "") + "</div>"
                f'<div style="position:absolute;left:0;right:0;bottom:0;height:24px;background:{c["accent"]}"></div>')
        page(ctx, chap, body, style=f'background:{c["bg"]};color:{c["ink"]}')
        # logos + símbolos (avatar de 48 px reais)
        logos = _existing(ctx, p.get("logos"), "logo", p["id"])
        syms = _existing(ctx, p.get("symbols"), "símbolo", p["id"])
        for k in range(0, max(len(logos), 1), 3):
            chunk = logos[k:k + 3]
            last_page = k + 3 >= len(logos)
            if not chunk and not syms:
                break
            lh = 440 if (syms and last_page) else 640
            cells = "".join(
                f'<div style="flex:1;min-width:0"><div class="box" style="height:{lh}px;background:{it.get("bg") or c["bg"]};'
                f'display:flex;align-items:center;justify-content:center;padding:{lh * .14:.0f}px;'
                f'border:1.5px solid rgba(0,0,0,.08)">{svg_box(read(path), "100%", "100%")}</div>'
                f'<p class="small" style="margin-top:12px">{E(it.get("name") or os.path.splitext(os.path.basename(path))[0])}'
                f' · fundo {E((it.get("bg") or c["bg"]).upper())}</p></div>' for path, it in chunk)
            sym_row = ""
            if syms and last_page:
                sym_row = ('<div style="display:flex;gap:64px;align-items:flex-end;margin-top:44px">' + "".join(
                    f'<div style="display:flex;gap:28px;align-items:flex-end">'
                    f'{avatar(read(path), it.get("bg") or c["bg"], 48)}{avatar(read(path), it.get("bg") or c["bg"], 120)}'
                    f'</div>' for path, it in syms) + '</div><p class="small" style="margin-top:14px">Símbolo como '
                    'avatar redondo (foto de perfil / grupo): o menor está em 48 px reais; o maior é ampliação.</p>')
            page(ctx, chap, f'<h2>Logos</h2>' + (f'<div style="display:flex;gap:28px">{cells}</div>' if cells else "")
                 + sym_row)
        # cor: amostras grandes + pares de contraste (principal | alternativa)
        sw = [(h.upper(), nm) for h, nm in (p.get("swatches") or [])] or \
            [(c["accent"], "destaque"), (c["bg"], "fundo"), (c["ink"], "texto"), (c["on_accent"], "sobre o destaque")]
        seen, uniq = set(), []
        for h, nm in sw:
            if h not in seen:
                seen.add(h)
                uniq.append((h, nm))
        scells = []
        for h, nm in uniq[:6]:
            d = describe(h)
            fg = ink_on(h, "#FFFFFF", "#141414")
            r, g, bb = d["rgb"]
            cy, m, y, kk = d["cmyk"]
            scells.append(f'<div class="col box" style="background:{h};color:{fg};padding:30px;height:360px;display:flex;'
                          f'flex-direction:column;justify-content:space-between;border:1.5px solid rgba(0,0,0,.08)">'
                          f'<h3>{E(nm)}</h3><p style="font-size:20px">HEX {h}<br>RGB {r} {g} {bb}<br>'
                          f'CMYK {cy} {m} {y} {kk}*</p></div>')
        groups = []
        for alt, cc in ((False, c), (True, c.get("alt"))):
            if not cc:
                continue
            cards = "".join(
                f'<div style="min-width:0"><div style="background:{pr["bg"]};color:{pr["fg"]};height:130px;'
                f'padding:18px 20px;display:flex;align-items:flex-end;justify-content:space-between;gap:12px;'
                f'border:1.5px solid rgba(0,0,0,.08)"><span style="font-family:brand-display;font-size:60px;'
                f'line-height:.9">Aa</span><span style="font-size:19px;font-weight:700;text-align:right;line-height:1.2">'
                f'{E(pr["par"])}</span></div><p style="font-size:18px;line-height:1.35;margin-top:10px">'
                f'<b>{fmt_ratio(pr["ratio"])} · {pr["nota"]}</b><br><span style="color:'
                f'{"inherit" if pr["ok"] else "#C62828"}">{"✓" if pr["ok"] else "✕ pede"} mín. {fmt_ratio(pr["need"])} · '
                f'{E(pr["uso"])}</span></p></div>' for pr in product_pairs(cc))
            groups.append(f'<div style="flex:1;min-width:0"><div class="label">contraste · '
                          f'{"versão alternativa (data-variante=alt)" if alt else "versão principal"}</div>'
                          f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px">{cards}</div></div>')
        page(ctx, chap, f'<h2 style="margin-bottom:28px">Cor</h2><div class="row" style="gap:20px">{"".join(scells)}</div>'
                        f'<div style="display:flex;gap:48px;margin-top:36px">{"".join(groups)}</div>'
                        f'<p class="small" style="margin-top:22px">WCAG 2: texto corrido ≥ 4,5:1 (AA) · título grande '
                        f'(≥ 24 px, ou 18,7 px negrito) e gráfico ≥ 3:1 · AAA ≥ 7:1. *CMYK aproximado — aprovar prova '
                        f'de cor com a gráfica.</p>')
        # aplicações em tamanho proporcional (mesma escala na página) + regras / não fazer / código ao lado quando
        # CABE (estimado); senão, páginas próprias — nada passa do rodapé
        rules, dont = p.get("rules") or [], p.get("dont") or []
        li = lambda xs, mark, fs: "".join(  # noqa: E731
            f'<li style="display:flex;gap:14px;margin-bottom:14px;list-style:none;font-size:{fs}px"><span style="flex:none;'
            f'font-weight:700">{mark}</span><span>{E(x)}</span></li>' for x in xs)
        code = (f'&lt;section data-produto="{p["id"]}"&gt;\n  … componentes …\n&lt;/section&gt;\n\n'
                f'--color-bg: {c["bg"]}\n--color-ink: {c["ink"]}\n--color-accent: {c["accent"]}\n'
                f'--color-on-accent: {c["on_accent"]}' +
                (f'\n\n+ data-variante="alt" → fundo {c["alt"]["bg"]}' if c.get("alt") else ""))
        side_done = not (rules or dont)
        pieces = _existing(ctx, p.get("pieces"), "peça", p["id"])
        gap = 36
        n_pg = math.ceil(len(pieces) / 4) if pieces else 0
        base_, extra_ = divmod(len(pieces), n_pg) if n_pg else (0, 0)
        sizes_ = [base_ + 1] * extra_ + [base_] * (n_pg - extra_)      # páginas equilibradas (4·3·3·3, nunca 4·4·4·1)
        starts_ = [sum(sizes_[:j]) for j in range(n_pg)]
        for k, per_pg in zip(starts_, sizes_):
            chunk = pieces[k:k + per_pg]
            dims = [Image.open(path).size for path, _ in chunk]
            s = min(740 / max(h for _, h in dims), (1680 - gap * (len(dims) - 1)) / sum(w for w, _ in dims))
            used = sum(w * s for w, _ in dims) + gap * (len(dims) - 1)
            side_w = min(640, 1680 - used - 80)
            side = ""
            if not side_done and k + per_pg >= len(pieces) and side_w >= 560:
                cap = 35   # legenda sob as peças (10 de margem + 1 linha de 17 px): topo/pé da coluna = topo/pé das peças
                tall = max(h for _, h in dims) * s
                tw = side_w - 40
                need = ((60 + est_h(rules, 21, tw)) if rules else 0) + ((60 + est_h(dont, 21, tw)) if dont else 0) \
                    + 40 * 2 + 270
                if need <= tall - 10:
                    top = 790 - tall - cap
                    h3t = 'style="text-box:trim-both cap alphabetic;margin-bottom:22px"'
                    side = (f'<div style="width:{side_w:.0f}px;flex:none;margin-left:auto;align-self:stretch;display:flex;'
                            f'flex-direction:column;gap:40px;padding:{top:.0f}px 0 {cap}px">'
                            + (f'<div><h3 {h3t}>Regras</h3><ul style="margin:0">{li(rules, "→", 21)}</ul></div>' if rules else "")
                            + (f'<div><h3 {h3t}>Não fazer</h3><ul style="margin:0">{li(dont, "✕", 21)}</ul></div>' if dont else "")
                            + f'<div style="margin-top:auto"><div class="label">em código (tokens.css)</div>'
                              f'<pre style="font-size:15px;padding:22px;margin:0">{code}</pre></div></div>')
                    side_done = True
            cells = "".join(
                f'<div style="width:{w * s:.0f}px;flex:none;align-self:flex-end"><div class="box fill" style="height:'
                f'{h * s:.0f}px;border:1.5px solid rgba(0,0,0,.08)">{ctx.img(path)}</div><p class="small" '
                f'style="margin-top:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'
                f'{E(os.path.splitext(os.path.basename(path))[0])}</p></div>'
                for (path, _), (w, h) in zip(chunk, dims))
            page(ctx, chap, f'<div class="label">aplicações · {E(p["name"])} · mesma escala (tamanho proporcional)</div>'
                            f'<div style="display:flex;gap:{gap}px;height:790px">{cells}{side}</div>')
        if not side_done:
            pre = (f'<div class="label" style="margin-top:28px">em código (tokens.css)</div><pre style="font-size:16px;'
                   f'padding:22px;max-width:760px">{code}</pre>')
            colw3 = (1680 - 440 - 2 * 56) / 2
            code_col = (f'<div style="width:440px;flex:none"><div class="label">em código (tokens.css)</div>'
                        f'<pre style="font-size:15px;padding:20px">{code}</pre></div>')
            if max(est_h(rules, 21, colw3 - 40, 14), est_h(dont, 21, colw3 - 40, 14)) + 110 <= 760:
                page(ctx, chap, f'<div class="row" style="gap:56px"><div class="col"><h2>Regras</h2><ul style="margin:0">'
                                f'{li(rules, "→", 21)}</ul></div><div class="col"><h2>Não fazer</h2><ul style="margin:0">'
                                f'{li(dont, "✕", 21)}</ul></div>{code_col}</div>')
                continue
            colw2 = (1680 - 70) / 2 - 36
            h_r = est_h(rules, 23, colw2, 16)
            h_d = est_h(dont, 23, colw2, 16)
            if max(h_r, h_d) + 120 + 250 <= 790:   # cabe numa página: duas colunas + código embaixo
                page(ctx, chap, f'<div class="row" style="gap:70px"><div class="col"><h2>Regras</h2><ul style="margin:0">'
                                f'{li(rules, "→", 23)}</ul></div><div class="col"><h2>Não fazer</h2><ul style="margin:0">'
                                f'{li(dont, "✕", 23)}</ul></div></div>{pre}')
            else:                                    # senão: uma página de regras e outra de nãos + código
                for tit, xs, mark in (("Regras", rules, "→"), ("Não fazer", dont, "✕")):
                    if not xs:
                        continue
                    half = math.ceil(len(xs) / 2)
                    last = tit == "Não fazer" or not dont
                    page(ctx, chap, f'<h2>{tit}</h2><div class="row" style="gap:70px"><ul class="col" style="margin:0">'
                                    f'{li(xs[:half], mark, 23)}</ul><ul class="col" style="margin:0">'
                                    f'{li(xs[half:], mark, 23)}</ul></div>' + (pre if last else ""))


def ch_type(ctx):
    b = ctx.b
    t = b.get("type") or {}
    if not (t.get("display") and t.get("text")):
        return
    opener(ctx, "Tipografia", whole_rules(t.get("rules")))
    d, x = t["display"], t["text"]
    dn = d if isinstance(d, str) else d.get("family")
    xn = x if isinstance(x, str) else x.get("family")
    page(ctx, "Tipografia",
         f'<div class="row"><div class="col"><div class="label">títulos · {E(dn)}</div>'
         f'<div style="font-family:brand-display;font-size:330px;line-height:.9">Aa</div>'
         f'<div style="font-family:brand-display;font-size:56px;line-height:1.15;margin-top:30px;word-break:break-all">'
         f'ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz<br>0123456789 ÁÉÍÓÚÇÃÕ&%</div></div>'
         f'<div class="col"><div class="label">texto · {E(xn)}</div>'
         f'<div style="font-family:brand-text;font-size:330px;line-height:.9">Aa</div>'
         f'<p class="lead" style="margin-top:30px">Texto corrido com a fonte de leitura: parágrafos, legendas e '
         f'interfaces. Números 0123456789, acentos (ação, coração, você) e o símbolo R$.</p></div></div>')
    lv = t.get("levels") or {}
    if lv:
        rows = ""
        short = " ".join((b.get("platform.idea") or b.name).split()[:3])   # amostra curta: não corta na página
        for name, l in lv.items():
            fam = "brand-display" if l["role"] == "display" else "brand-text"
            sz = max(14, min(l["size"] * 1.3, 100))   # a amostra nunca abaixo de 14 px (legível na página)
            sample = short if l["role"] == "display" else "Texto que explica com calma e ritmo."
            rows += (f'<div style="display:flex;align-items:baseline;gap:40px;border-bottom:1.5px solid rgba(0,0,0,.1);'
                     f'padding:7px 0"><div class="small" style="width:260px;flex:none">{name} · {l["size"]:g}px / '
                     f'{l["line_height"]}</div><div style="flex:1;min-width:0;font-family:{fam};font-size:{sz:.0f}px;'
                     f'line-height:1.05;letter-spacing:{l["tracking"]}em;white-space:nowrap;overflow:hidden;'
                     f'text-overflow:ellipsis">{E(sample)}</div></div>')
        sc = t.get("scale") or {}
        page(ctx, "Tipografia", f'<h2>Hierarquia</h2>{rows}<p class="small" style="margin-top:18px">Escala modular: '
                                f'base {sc.get("base", 16)}px × {sc.get("ratio", 1.25)}. Fontes com licença OFL '
                                f'(uso comercial e incorporação livres; manter o OFL.txt junto dos arquivos).</p>')


def _elements_kit(ctx):
    """Capítulo de elementos quando a marca não tem `devices` (gerados do símbolo) mas tem `elements` (intro/unidade/
    regras) + `patterns` (lista de elementos com regra e, opcional, `src` = imagem) e/ou folhas de catálogo em
    `elementos/catalogo/*.png` (ornamentos). Sem isto, o kit inteiro sumia do manual."""
    b = ctx.b
    el = b.get("elements") if isinstance(b.get("elements"), dict) else {}
    pats = [p for p in (b.get("patterns") or []) if isinstance(p, dict)]
    folhas = sorted(glob.glob(os.path.join(b.dir, "elementos", "catalogo", "*.png")))
    folhas = [f for f in folhas if not os.path.basename(f).startswith("_")]
    if not (el or pats or folhas):
        return False
    opener(ctx, "Elementos gráficos", el.get("intro") or "Uma família de elementos que nasce do logo e do assunto — "
                                                         "não decoração aplicada por cima.")
    regras = "".join(f"<li>{E(r)}</li>" for r in (el.get("rules") or []))
    if el.get("unit") or regras:
        page(ctx, "Elementos gráficos",
             (f'<h2>Medidas</h2><p class="lead">{E(el["unit"])}</p>' if el.get("unit") else "")
             + (f'<h2 style="margin-top:36px">Regras de uso</h2><ul style="margin:12px 0 0 24px">{regras}</ul>'
                if regras else ""))
    for f in folhas:
        nome = os.path.splitext(os.path.basename(f))[0].replace("-", " ").capitalize()
        page(ctx, "Elementos gráficos", f'<h2>{E(nome)}</h2><div class="box" style="height:820px;display:flex;'
                                        f'align-items:center;justify-content:center">'
                                        f'{ctx.img(f, style="max-width:100%;max-height:100%;object-fit:contain")}</div>')
    com_img = [p for p in pats if p.get("src") and os.path.exists(os.path.join(b.dir, p["src"]))]
    for p in com_img:
        src = os.path.join(b.dir, p["src"])
        nome = p.get("name", p.get("id", ""))
        from PIL import Image
        iw, ih = Image.open(src).size
        if src.lower().endswith(".png") and iw >= 1800 and ih / iw > 0.55:
            # folha grande (kit 2400 × 1650): em faixas de linha inteira, uma por página, na largura da página
            parts = split_tall(src, 1680, 470, os.path.join(ctx.mdir, "_img", "kit-partes"), faixa_min=8)
            for j, (f, hh) in enumerate(parts):
                page(ctx, "Elementos gráficos",
                     f'<h2>{E(nome)}{f" ({j + 1}/{len(parts)})" if len(parts) > 1 else ""}</h2>'
                     + (f'<p style="max-width:1500px">{E(p.get("rule", ""))}</p>' if j == 0 else "")
                     + f'<div class="box fill" style="height:{hh:.0f}px;margin-top:24px">{ctx.img(f)}</div>')
            continue
        page(ctx, "Elementos gráficos", f'<h2>{E(nome)}</h2><p>{E(p.get("rule", ""))}</p>'
                                        f'<div class="box" style="height:620px;margin-top:20px;display:flex;'
                                        f'align-items:center;justify-content:center">'
                                        f'{ctx.img(src, style="max-width:100%;max-height:100%;object-fit:contain")}'
                                        f'</div>')
    so_txt = [p for p in pats if p not in com_img]
    for i in range(0, len(so_txt), 8):
        cards = "".join(f'<div style="border-top:3px solid {ctx.brand};padding:14px 0 0"><h3>'
                        f'{E(p.get("name", p.get("id", "")))}</h3><p class="small">'
                        f'{E(p.get("mundo") or "")}</p>'
                        f'<p>{E(p.get("rule", ""))}</p></div>' for p in so_txt[i:i + 8])
        page(ctx, "Elementos gráficos", f'<h2>Ficha de cada elemento</h2><div style="display:grid;'
                                        f'grid-template-columns:repeat(4,1fr);gap:28px 36px;margin-top:24px">{cards}</div>')
    return True


def ch_elements(ctx, logos):
    b = ctx.b
    devs = b.get("devices") or []
    if not devs:
        _elements_kit(ctx)
        return
    opener(ctx, "Elementos gráficos", "Uma família de elementos que nasce do próprio símbolo — não decoração "
                                      "aplicada por cima.")
    dna_p = os.path.join(b.dir, "elementos", "dna.json")
    if os.path.exists(dna_p):
        import json
        dna = json.load(open(dna_p, encoding="utf-8"))
        tips = "".join(f"<li>{E(x)}</li>" for x in dna.get("dicas", []))
        sym = logos.get("symbol") or logos.get("_form") or logos.get("primary")
        page(ctx, "Elementos gráficos",
             f'<div class="row"><div class="col"><h2>DNA da forma</h2><p>Ângulos dominantes: '
             f'{", ".join(f"{a:g}°" for a in dna.get("angulos_dominantes", [])) or "0°/90°"} · espessura do traço '
             f'{dna.get("espessura_traco", 0) * 100:.1f}% da altura · retas {dna.get("retas_vs_curvas", 0) * 100:.0f}% · '
             f'simetria {max(dna.get("simetria_vertical", 0), dna.get("simetria_horizontal", 0)) * 100:.0f}%</p>'
             f'<ul style="margin:24px 0 0 24px">{tips}</ul></div><div class="col" style="height:760px;display:flex;'
             f'align-items:center;justify-content:center">{svg_box(sym, "80%", "80%", ctx.ink) if sym else ""}</div></div>')
    for i in range(0, len(devs), 2):
        pair = devs[i:i + 2]
        cols = []
        for dv in pair:
            hero = os.path.join(b.dir, "elementos", f"{dv['id']}-brand-ink.png")
            if not os.path.exists(hero):
                hero = next(iter(sorted(glob.glob(os.path.join(b.dir, "elementos", f"{dv['id']}-*.png")))), "")
            minis = sorted(glob.glob(os.path.join(b.dir, "elementos", f"{dv['id']}-*.png")))[:4]
            cols.append(f'<div class="col"><div class="box cover" style="height:560px">{ctx.img(hero)}</div>'
                        f'<div class="row" style="gap:10px;margin-top:10px">' +
                        "".join(f'<div class="col box cover" style="height:110px">{ctx.img(m)}</div>' for m in minis) +
                        f'</div><h3 style="margin-top:26px">{E(dv.get("name", dv["id"]))}</h3>'
                        f'<p>{E(dv.get("rule", ""))}</p></div>')
        page(ctx, "Elementos gráficos", f'<div class="row">{"".join(cols)}</div>')


def ch_grid(ctx):
    b = ctx.b
    g = b.get("grid") or {}
    cols = g.get("columns", 12)
    m = g.get("margin", 0.06)
    gut = g.get("gutter", 0.02)
    fmts = [("Post 1:1", 1080, 1080), ("Feed 4:5", 1080, 1350), ("Story 9:16", 1080, 1920), ("Banner 16:9", 1920, 1080)]
    cells = []
    for name, W, H in fmts:
        k = 300 / max(W, H) * (1.5 if W > H else 1)
        w, h = W * k, H * k
        mm, gg = m * W * k, gut * W * k
        cw = (w - 2 * mm - (cols - 1) * gg) / cols
        bars = "".join(f'<rect x="{mm + i * (cw + gg):.1f}" y="{m * W * k:.1f}" width="{cw:.1f}" '
                       f'height="{h - 2 * m * W * k:.1f}" fill="{ctx.brand}" opacity=".28"/>' for i in range(cols))
        safe = ""
        if H > W * 1.5:
            safe = (f'<rect x="0" y="0" width="{w:.0f}" height="{h * .13:.0f}" fill="{ctx.ink}" opacity=".18"/>'
                    f'<rect x="0" y="{h * .8:.0f}" width="{w:.0f}" height="{h * .2:.0f}" fill="{ctx.ink}" opacity=".18"/>')
        cells.append(f'<div><svg width="{w:.0f}" height="{h:.0f}" style="background:{ctx.paper};border:1.5px solid '
                     f'rgba(0,0,0,.15)">{bars}{safe}</svg><p class="small">{name}</p></div>')
    page(ctx, "Grid e layout", f'<h2>Grid</h2><p class="lead" style="margin-bottom:40px">{cols} colunas · margem '
                               f'{m * 100:.0f}% da largura · calha {gut * 100:.0f}% · linha de base '
                               f'{g.get("baseline", 8)}px' + (f' · ângulo da marca {g["angle"]}°' if g.get("angle") else "")
         + f'. Stories: faixas escuras = área coberta pela interface do app (não colocar texto).</p>'
           f'<div style="display:flex;gap:50px;align-items:flex-end">{"".join(cells)}</div>')


def ch_imagery(ctx):
    b = ctx.b
    im = b.get("imagery") or {}
    files = sorted(glob.glob(os.path.join(b.dir, "imagem", "*.png")) + glob.glob(os.path.join(b.dir, "imagem", "*.jpg")))
    if not (any(im.values()) or files):
        return
    opener(ctx, "Imagem", im.get("style") or "")
    txt = "".join(f'<div class="card"><div class="label">{E(k)}</div><p>{E(v)}</p></div>'
                  for k, v in (("tratamento", im.get("treatment")), ("enquadramento", im.get("crop")),
                               ("imagens geradas por IA", im.get("prompt_style"))) if v)
    donts = [x for x in (im.get("dont") or []) if str(x).strip()]
    ex = [b.path(x) for x in (im.get("examples") or []) if os.path.exists(b.path(x))]
    if ex:      # fotos reais de subpastas (a pasta imagem/ só lista o que está na raiz): painel escuro, foto inteira
        grid = "".join(f'<div class="box fill" style="height:430px;background:{ctx.ink}">{ctx.img(f)}</div>'
                       for f in ex[:3])
    else:
        grid = "".join(f'<div class="box cover" style="height:330px">{ctx.img(f)}</div>' for f in files[:6])
    short = len(donts) <= 3
    dont_html = "".join(f"<li>{E(x)}</li>" for x in donts)
    page(ctx, "Imagem", f'<div class="row"><div class="col" style="flex:.8">{txt}'
                        + (f'<div class="card"><div class="label">evitar</div><ul style="margin-left:24px">{dont_html}</ul></div>'
                           if donts and short else "") + f'</div><div class="col g3" style="flex:1.2;align-content:start">{grid}</div></div>')
    if donts and not short:
        half = math.ceil(len(donts) / 2)
        li_ = lambda xs: "".join(f'<li style="display:flex;gap:14px;list-style:none;margin-bottom:16px;font-size:22px">'  # noqa: E731
                                 f'<b style="flex:none">✕</b><span>{E(x)}</span></li>' for x in xs)
        page(ctx, "Imagem", f'<h2>O que evitar na imagem</h2><div class="row" style="gap:70px"><ul class="col" '
                            f'style="margin:0">{li_(donts[:half])}</ul><ul class="col" style="margin:0">{li_(donts[half:])}</ul></div>')
    tx = b.get("texture") or {}
    if tx.get("rule") or tx.get("fx"):
        itens = [("regra", tx.get("rule")), ("efeitos", " · ".join(tx.get("fx") or [])),
                 ("grão", " · ".join(f"{k} {v}" for k, v in (tx.get("grao") or {}).items()) if isinstance(tx.get("grao"), dict)
                  else tx.get("grao")),
                 ("fundos", tx.get("fundos") if isinstance(tx.get("fundos"), str) else " · ".join(map(str, tx.get("fundos") or [])))]
        page(ctx, "Imagem", '<h2>Textura</h2>' + "".join(f'<div class="card" style="margin-bottom:26px;max-width:1500px">'
                                                         f'<div class="label">{lab}</div><p>{E(str(v))}</p></div>'
                                                         for lab, v in itens if v))


def ch_icons(ctx):
    b = ctx.b
    files = sorted(glob.glob(os.path.join(b.dir, "icones", "*.svg")))
    if not files:
        return
    ic = b.get("icons") or {}
    cells = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:10px">'
                    f'{svg_box(read(f), "96px", "96px", ctx.ink)}<span class="small">{E(os.path.basename(f)[:-4])}</span>'
                    f'</div>' for f in files[:24])
    page(ctx, "Ícones", f'<h2>Ícones</h2><p class="lead" style="margin-bottom:50px">Grid de {ic.get("grid", 24)}px · '
                        f'traço {ic.get("stroke", 2)}px · pontas {ic.get("cap", "square")} · junções '
                        f'{ic.get("join", "miter")}. ' + "; ".join(ic.get("rules") or []) + '</p>'
                        f'<div style="display:grid;grid-template-columns:repeat(8,1fr);gap:40px">{cells}</div>')


def ch_motion(ctx):
    b = ctx.b
    mo = b.get("motion") or {}
    if not (mo.get("principles") or mo.get("easing")):
        ctx.skip("Movimento", "sem motion.principles / motion.easing")
        return
    from tokens import PRODUTIVO, PRODUTIVO_NOTA
    eas = dict(mo.get("easing") or {})
    notes = dict(mo.get("easing_notes") or {})
    if not any(list(v) == PRODUTIVO for v in eas.values()):   # o par produtivo entra mesmo sem estar na marca
        eas["produtivo"] = PRODUTIVO
        notes.setdefault("produtivo", PRODUTIVO_NOTA + " (padrão da skill)")
    curves = []
    for name, (x1, y1, x2, y2) in eas.items():
        pts = []
        for i in range(41):
            t = i / 40
            x = 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t ** 2 * x2 + t ** 3
            y = 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t ** 2 * y2 + t ** 3
            pts.append(f"{20 + x * 260:.1f},{280 - y * 240:.1f}")
        curves.append(f'<div style="width:300px"><svg width="300" height="300" style="border:1.5px solid rgba(0,0,0,.12)">'
                      f'<polyline points="{" ".join(pts)}" fill="none" stroke="{ctx.brand}" stroke-width="5"/></svg>'
                      f'<p class="small" style="font-size:15px;opacity:.85"><b>{E(name)}</b> · cubic-bezier({x1:g}, {y1:g}, '
                      f'{x2:g}, {y2:g})' + (f'<br>{E(notes[name])}' if notes.get(name) else "") + '</p></div>')
    dmax = max((mo.get("durations") or {"x": 1}).values()) or 1
    durs = "".join(f'<div style="display:flex;align-items:center;gap:20px;margin:10px 0"><div style="width:210px;flex:none;'
                   f'font-size:19px">{E(k)}</div><div style="height:22px;flex:none;width:{v / dmax * 380:.0f}px;'
                   f'background:{ctx.ink}"></div><span class="small" style="white-space:nowrap">{v} ms</span></div>'
                   for k, v in (mo.get("durations") or {}).items())
    prs = mo.get("principles") or []
    pr = "".join(f'<li>{E(x)}</li>' for x in prs)
    if sum(len(x) for x in prs) <= 600 and len(curves) <= 2:
        page(ctx, "Movimento", f'<h2>Movimento</h2><div class="row"><div class="col"><ul style="margin-left:24px">{pr}</ul>'
                               f'<div style="margin-top:40px">{durs}</div></div><div class="col" style="display:flex;'
                               f'gap:30px;flex-wrap:wrap">{"".join(curves)}</div></div>')
        return
    # muitos princípios: uma página só para eles (2 colunas) e outra para curvas e durações
    half = math.ceil(len(prs) / 2)
    ul = lambda xs: "".join(f'<li style="font-size:21px;margin-bottom:12px">{E(x)}</li>' for x in xs)  # noqa: E731
    page(ctx, "Movimento", f'<h2>Movimento</h2><div class="row" style="gap:70px"><ul class="col" style="margin-left:24px">'
                           f'{ul(prs[:half])}</ul><ul class="col" style="margin-left:24px">{ul(prs[half:])}</ul></div>')
    page(ctx, "Movimento", f'<h2 style="margin-bottom:24px">Curvas e durações</h2><div style="display:flex;flex-wrap:wrap;'
                           f'gap:24px 28px">{"".join(curves)}</div><div style="margin-top:28px"><div class="label">'
                           f'durações</div>{durs}<p class="small" style="margin-top:16px">Produtivo = tarefa (rápido, '
                           f'sem chamar atenção); expressivo = momento importante. Movimento reduzido: deslizar vira '
                           f'esmaecer curto.</p></div>')


def ch_voice(ctx):
    b = ctx.b
    v = (b.get("platform") or {}).get("voice") or {}
    if not any(v.values()):
        return
    opener(ctx, "Voz", "Como a marca fala — a mesma voz, com tons diferentes para cada situação.")
    is_ = "".join(f"<li>{E(x)}</li>" for x in v.get("is") or [])
    not_ = "".join(f"<li>{E(x)}</li>" for x in v.get("is_not") or [])
    ex = "".join(f'<p style="font-family:brand-display;font-size:44px;line-height:1.1;margin-bottom:26px">'
                 f'“{E(x)}”</p>' for x in (v.get("examples") or [])[:4])
    page(ctx, "Voz", f'<div class="row"><div class="col card"><div class="label">somos</div>'
                     f'<ul style="margin-left:24px">{is_}</ul></div><div class="col card"><div class="label">não somos</div>'
                     f'<ul style="margin-left:24px">{not_}</ul></div><div class="col" style="flex:1.6">{ex}</div></div>')
    mat = v.get("matrix")   # {"canais": [...], "linhas": [{"principio": "...", "niveis": ["alto", ...]}]}
    if mat:
        head = "".join(f"<th style='text-align:left;padding:14px'>{E(c)}</th>" for c in mat.get("canais", []))
        rows = "".join(f"<tr><td style='padding:14px;font-weight:700'>{E(r['principio'])}</td>" +
                       "".join(f"<td style='padding:14px'>{E(n)}</td>" for n in r.get("niveis", [])) + "</tr>"
                       for r in mat.get("linhas", []))
        page(ctx, "Voz", f'<h2>Tom por canal</h2><table style="width:100%;border-collapse:collapse;font-size:24px">'
                         f'<tr><th></th>{head}</tr>{rows}</table>')


def ch_applications(ctx):
    b = ctx.b
    apps = [p for p in sorted(glob.glob(os.path.join(b.dir, "aplicacoes", "*", "pecas", "*.png")))
            if not p.endswith("-sheet.png") and not os.path.basename(os.path.dirname(os.path.dirname(p))).startswith("_")]
    mocks = sorted(glob.glob(os.path.join(b.dir, "mockups", "*.png")) + glob.glob(os.path.join(b.dir, "mockups", "*.jpg")))
    if not (apps or mocks):
        return
    opener(ctx, "Aplicações", "O sistema em uso: peças reais em formatos reais.")
    for i in range(0, len(mocks), 2):
        pair = mocks[i:i + 2]
        page(ctx, "Aplicações", '<div class="row" style="height:820px">' +
             "".join(f'<div class="col box cover">{ctx.img(m)}</div>' for m in pair) + "</div>")
    by = {}
    for p in apps:
        by.setdefault(os.path.basename(os.path.dirname(os.path.dirname(p))), []).append(p)
    for recipe, files in by.items():
        cells = ""
        for f in files[:5]:
            from PIL import Image
            w, h = Image.open(f).size
            hh = 700 if h >= w else 700 * h / w * 1.0
            cells += (f'<div class="box fill" style="height:{hh:.0f}px;flex:{w / h:.3f}">{ctx.img(f)}</div>')
        page(ctx, "Aplicações", f'<div class="label">{E(recipe)}</div><div style="display:flex;gap:28px;'
                                f'align-items:flex-end;height:760px">{cells}</div>')
    st = os.path.join(b.dir, "aplicacoes", "estresse.png")
    if os.path.exists(st):
        page(ctx, "Aplicações", f'<h2>Teste de estresse</h2><div class="box fill" style="height:640px">{ctx.img(st)}</div>')


def _print_strip(ctx, path, h, cols=3, cap=170):
    """Página inteira (imagem muito alta) cortada em `cols` tiras lado a lado: mostra o ritmo da página sem ficar
    ilegível numa coluna fina. Cada tira é um ARQUIVO recortado (o verificador de layout mede a caixa da imagem; recorte
    por overflow estourava o pé). Cada tira tem altura h; a largura sai da proporção da imagem."""
    import hashlib
    from PIL import Image
    if not path or not os.path.exists(path):
        return "", 0
    im = Image.open(path).convert("RGB")
    w, hh = im.size
    c = min(cap, h * cols * w / hh)
    # px do original por px da página: cada tira cobre h * (w / c) px de altura do original
    passo = int(round(h * w / c))
    pasta = os.path.join(ctx.mdir, "_img", "paginas-tiras")
    os.makedirs(pasta, exist_ok=True)
    tag = hashlib.sha256(f"{path}|{os.path.getmtime(path)}|{cols}|{h}|{cap}".encode()).hexdigest()[:12]
    partes = []
    for k in range(cols):
        dst = os.path.join(pasta, f"{tag}-{k}.jpg")
        if not os.path.exists(dst):
            y0 = k * passo
            crop = im.crop((0, y0, w, min(hh, y0 + passo)))
            if crop.height < 2:
                crop = Image.new("RGB", (w, 2), (255, 255, 255))
            crop.save(dst, "JPEG", quality=84, optimize=True)
        ch = int(round(Image.open(dst).height * c / w))
        partes.append(f'<div style="width:{c:.0f}px;height:{ch}px;flex:none">'
                      f'{ctx.img(dst, style=f"width:{c:.0f}px;height:{ch}px;display:block")}</div>')
    return f'<div style="display:flex;gap:10px;align-items:flex-start">{"".join(partes)}</div>', c * cols + 10 * (cols - 1)


def ch_pages(ctx):
    """Páginas e sites (brand.json "pages"): o método fixo das páginas, o mapa das páginas (mãe + individuais), as
    individuais lado a lado e, por página, 2 telas: prints (dobra no computador e no celular + página inteira) e a
    anatomia (blocos e papel de marketing, elementos do kit e onde entram, CTA e oferta)."""
    b = ctx.b
    pg = b.get("pages") or {}
    items = [it for it in (pg.get("items") or []) if isinstance(it, dict)]
    if not items:
        return
    from PIL import Image
    chap = "Páginas e sites"
    opener(ctx, chap, pg.get("sub") or "Cada página tem um papel no funil, uma ideia gráfica e um conjunto de elementos.")
    prods = {p["id"]: p for p in products(b)}

    def cor(it):
        p = prods.get(it.get("produto"))
        return (p or {}).get("colors") or {"bg": ctx.ink, "ink": ctx.paper, "accent": ctx.accent,
                                              "on_accent": ink_on(ctx.accent, "#FFFFFF", "#141414")}

    def pth(it, k):
        v = (it.get("prints") or {}).get(k)
        return b.path(v) if v else None

    # 1) método fixo
    met = pg.get("metodo") or []
    if met:
        cells = "".join(f'<div class="card"><h3>{E(m.get("t", ""))}</h3><p>{E(m.get("d", ""))}</p></div>'
                        if isinstance(m, dict) else f'<div class="card"><p>{E(str(m))}</p></div>' for m in met[:6])
        page(ctx, chap, f'<h2>O que é igual em toda página</h2>'
                        + (f'<p class="lead" style="font-size:26px;margin:-8px 0 30px;max-width:1500px">'
                           f'{E(pg["regra"])}</p>' if pg.get("regra") else "")
                        + f'<div class="g3" style="row-gap:34px">{cells}</div>')

    # 2) mapa: uma linha por página
    rows = ""
    for it in items:
        c = cor(it)
        rows += (f'<tr><td><span class="sw" style="background:{c["accent"]}"></span><b>{E(it.get("nome", ""))}</b></td>'
                 f'<td>{E(it.get("versao", ""))}</td><td><code>{E(it.get("rota", ""))}</code></td>'
                 f'<td>{E(it.get("papel", ""))}</td><td>{E(it.get("ideia_curta", ""))}</td></tr>')
    page(ctx, chap, f'<h2>Mapa das páginas</h2><table class="t" style="font-size:18px"><tr><th>página</th><th>versão</th>'
                    f'<th>endereço</th><th>papel no funil</th><th>ideia gráfica</th></tr>{rows}</table>')

    # 3) as individuais lado a lado: 1 grupo por produto, 1 imagem por versão, dobra do celular (390 × 844).
    #    Uma tela no tema escuro e, se houver prints_claro, outra no claro (mesma ordem, para comparar).
    solo = [it for it in items if it.get("produto") and it.get("grupo") == "individual"]
    vers = sorted({it.get("versao") for it in solo})
    prod_ids = []
    for it in solo:
        if it["produto"] not in prod_ids:
            prod_ids.append(it["produto"])

    def lado_a_lado(claro):
        ng, nv = len(prod_ids), len(vers)
        gap_in, gap_g = 10, 44
        wimg = (1680 - (ng - 1) * gap_g - ng * (nv - 1) * gap_in) / (ng * nv)
        himg = min(wimg / 0.462, 640)
        wimg = himg * 0.462
        grupos = ""
        for pid in prod_ids:
            imgs = ""
            for v in vers:
                it = next((x for x in solo if x["produto"] == pid and x.get("versao") == v), None)
                src = ((it or {}).get("prints_claro") if claro else (it or {}).get("prints")) or {}
                im = b.path(src.get("dobra_mobile")) if src.get("dobra_mobile") else None
                bg = cor(it)["bg"]
                if claro:
                    bg = ((prods.get(pid) or {}).get("colors") or {}).get("alt", {}).get("bg") or "#ECE7DC"
                imgs += (f'<div style="width:{wimg:.0f}px;flex:none"><div class="box fill" style="width:{wimg:.0f}px;'
                         f'height:{himg:.0f}px;background:{bg};border:1.5px solid rgba(0,0,0,.12)">{ctx.img(im)}</div>'
                         f'<p class="small" style="margin-top:8px;font-size:15px">{E(v)}</p></div>')
            nome_p = (prods.get(pid) or {}).get("name") or pid
            c = cor({"produto": pid})
            grupos += (f'<div><div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">'
                       f'<span class="sw" style="margin:0;background:{c["accent"]}"></span>'
                       f'<span class="label" style="margin:0;opacity:1">{E(nome_p)}</span></div>'
                       f'<div style="display:flex;gap:{gap_in}px">{imgs}</div></div>')
        titulo = f"As {len(solo)} individuais lado a lado" + (" · tema claro" if claro else " · tema escuro")
        page(ctx, chap, f'<h2 style="font-size:60px">{E(titulo)}</h2>'
                        f'<div style="display:flex;gap:{gap_g}px;align-items:flex-start">{grupos}</div>')

    if solo and vers:
        lado_a_lado(False)
        if any((x.get("prints_claro") or {}).get("dobra_mobile") for x in solo):
            lado_a_lado(True)

    # 4) por página: prints + anatomia
    for it in items:
        c = cor(it)
        nome = it.get("nome", "")
        def tela_prints(src, claro, c=c, it=it, nome=nome):
            def g(k):
                v = (src or {}).get(k)
                return b.path(v) if v else None
            dsk, mob, inteira = g("dobra_desktop"), g("dobra_mobile"), g("inteira_mobile")
            fundo = c["bg"]
            if claro:
                fundo = ((prods.get(it.get("produto")) or {}).get("colors") or {}).get("alt", {}).get("bg") or "#ECE7DC"
            H = 520
            parts = []
            for path in (dsk, mob):
                if path and os.path.exists(path):
                    w, hh = Image.open(path).size
                    parts.append((path, H * w / hh))
            strip, sw = _print_strip(ctx, inteira, H)
            total = sum(w for _, w in parts) + sw + 28 * (len(parts) + (1 if strip else 0) - 1)
            if total > 1680:
                k = 1680 / total
                H = int(H * k)
                parts = [(p_, w_ * k) for p_, w_ in parts]
                strip, sw = _print_strip(ctx, inteira, H)
            prints = "".join(f'<div class="box fill" style="width:{w_:.0f}px;height:{H}px;flex:none;background:{fundo};'
                             f'border:1.5px solid rgba(0,0,0,.12)">{ctx.img(p_)}</div>' for p_, w_ in parts)
            tags = "".join(f'<span class="tag" style="margin-right:10px">{E(t)}</span>'
                           for t in (it.get("versao"), it.get("rota"), it.get("papel"),
                                     "tema claro" if claro else "tema escuro") if t)
            page(ctx, f"{chap} · {nome}",
                 f'<div style="display:flex;align-items:center;gap:22px;margin-bottom:6px"><span class="sw" '
                 f'style="width:40px;height:40px;background:{c["accent"]};margin:0"></span><h2 style="margin:0;'
                 f'font-size:64px">{E(nome)}</h2></div><div style="margin:6px 0 14px">{tags}</div>'
                 f'<p class="lead" style="font-size:24px;max-width:1500px;margin-bottom:20px">{E(it.get("ideia", ""))}</p>'
                 f'<div style="display:flex;gap:28px;align-items:flex-start">{prints}{strip}</div>'
                 f'<p class="small" style="margin-top:10px">Dobra no computador (1440) · dobra no celular (390) · '
                 f'página inteira no celular, em 3 tiras</p>')

        tela_prints(it.get("prints"), False)
        if it.get("prints_claro"):
            tela_prints(it.get("prints_claro"), True)
        anat = "".join(f'<tr><td><b>{E(a.get("bloco", ""))}</b></td><td>{E(a.get("papel", ""))}</td></tr>'
                       for a in it.get("anatomia") or [])
        elem = "".join(f'<tr><td><b>{E(e.get("nome", ""))}</b></td><td>{E(e.get("onde", ""))}</td>'
                       f'<td>{E(e.get("porque", ""))}</td></tr>' for e in it.get("elementos") or [])
        ext = "".join(f'<p style="font-size:19px;margin-top:12px"><span class="label" style="display:block;margin:0">'
                      f'{E(lab)}</span>{E(it.get(k))}</p>'
                      for k, lab in (("cta", "botão (CTA)"), ("oferta", "oferta"), ("funil", "marketing")) if it.get(k))
        page(ctx, f"{chap} · {nome}",
             f'<h2 style="font-size:56px;margin-bottom:24px">{E(nome)} · anatomia</h2>'
             f'<div class="g2" style="align-items:start"><div><div class="label">blocos, em ordem · papel de marketing</div>'
             f'<table class="t" style="font-size:17px"><tr><th>bloco</th><th>papel</th></tr>{anat}</table></div>'
             f'<div><div class="label">elementos do kit · onde entram · por quê</div>'
             f'<table class="t" style="font-size:17px"><tr><th>elemento</th><th>onde</th><th>por quê</th></tr>{elem}'
             f'</table>{ext}</div></div>')


def ch_templates(ctx):
    """Modelos de peça (brand.json "templates"): a receita exata de cada tipo de peça — regra, medidas, exemplo e o
    comando que a refaz. É o que permite replicar qualquer peça com fidelidade."""
    b = ctx.b
    tps = b.get("templates") or []
    if not tps:
        return
    opener(ctx, "Modelos de peça", "Cada peça nasce de um modelo com regra e medida. Mesmo texto + mesmo modelo = "
                                   "mesma peça, feita por qualquer pessoa.")
    for t in tps:
        ex = [b.path(x) for x in (t.get("examples") or []) if os.path.exists(b.path(x))]
        from PIL import Image
        cells = ""
        for f in ex[:3]:
            w, h = Image.open(f).size
            cells += (f'<div class="box fill" style="height:{(580 if h >= w else 580 * h / w):.0f}px;flex:{w / h:.3f}">'
                      f'{ctx.img(f)}</div>')
        meas = "".join(f"<li>{E(m)}</li>" for m in t.get("measures") or [])
        cmd = (f'<div class="label" style="margin-top:22px">como refazer</div><pre style="font-size:15px;padding:18px 22px">'
               f'{E(t["command"])}</pre>' if t.get("command") else "")
        page(ctx, "Modelos de peça",
             f'<div class="row" style="gap:70px"><div style="width:640px;flex:none"><div class="label">modelo</div>'
             f'<h2>{E(t.get("name", t.get("id", "")))}</h2><p class="lead" style="font-size:26px">{E(t.get("rule", ""))}'
             f'</p><ul style="margin:26px 0 0 24px">{meas}</ul></div>'
             f'<div style="flex:1;min-width:0"><div style="display:flex;gap:24px;align-items:flex-end;height:600px">'
             f'{cells}</div>{cmd}</div></div>')


def ch_system(ctx):
    b = ctx.b
    css = os.path.join(b.dir, "tokens", "tokens.css")
    if not os.path.exists(css):
        return
    lines = open(css, encoding="utf-8").read().splitlines()
    tdir = os.path.join(b.dir, "tokens")
    has = lambda rel: os.path.exists(os.path.join(tdir, rel))  # noqa: E731
    pblock = []
    for i, l in enumerate(lines):   # 1º bloco de produto, sem os comentários longos (cabe na coluna)
        if l.startswith("[data-produto="):
            pblock = [re.sub(r"\s*/\*.*?\*/", "", x) for x in lines[i:i + 7]]
            break
    pick = [l for l in lines if "--role-" in l][:8] + ["  …"] + (pblock or [l for l in lines if "--color-brand-" in l][:5])
    files = [("core.tokens.json", "padrão DTCG 2025.10 (fonte da verdade)"),
             ("light.tokens.json", "light|dark.tokens.json — papéis por modo"),
             ("products.tokens.json", "cores de cada produto (bg, ink, accent, on-accent, error + alt) com o "
                                      "contraste em $extensions"),
             ("tokens.css", "variáveis CSS, classes .t-* e blocos [data-produto]" if pblock
              else "variáveis CSS (+ classes .t-*)"),
             ("tailwind.css", "tema Tailwind v4"),
             ("figma", "figma/*.tokens.json — importar como modo de variáveis no Figma" +
              (" (um modo por produto: produto-<id>.tokens.json)" if pblock else "")),
             ("demo.html", "página com os componentes usando só os tokens" + (" (um bloco por produto)" if pblock else "")
              + (" · demo.png = foto da página" if has("demo.png") else ""))]
    items = [f"tokens/{f} — {d}" if not d.startswith(("light|", "figma/")) else f"tokens/{d}" for f, d in files if has(f)]
    items.append("DESIGN.md — a marca em texto para qualquer IA/dev gerar telas e peças dentro do sistema")
    page(ctx, "Design system", f'<div class="row"><div class="col"><h2>Design system</h2><p class="lead">Todas as '
                               f'decisões viram tokens: cor, tipo, espaço, raio, traço, grid e movimento. Muda o token, '
                               f'muda tudo.</p><ul style="margin:40px 0 0 24px">' +
         "".join(f"<li>{E(f)}</li>" for f in items) + f'</ul></div><div class="col"><pre>{E(chr(10).join(pick))}</pre>'
                                                       f'</div></div>')
    # a demo: pedaços fotografados em tamanho real (tokens/demo/blocos.json) — texto legível, nunca cortado no meio de
    # um componente; cada pedaço com a legenda dos tokens que ele usa. Sem blocos.json: blocos inteiros em 2 colunas.
    shots = [f for f in sorted(glob.glob(os.path.join(tdir, "demo", "*.png"))) if not os.path.basename(f)[3:].startswith("topo")]
    meta_p = os.path.join(tdir, "demo", "blocos.json")
    if shots and os.path.exists(meta_p):
        pg_demo_pieces(ctx, meta_p, os.path.join(tdir, "demo"))
    elif shots:
        from PIL import Image
        CW, CH, GAP = 820, 780, 24
        cols, cur, h_cur = [], [], 0
        partes = []
        for f in shots:   # bloco mais alto que a coluna: cortado em partes numa faixa vazia (não encolhe o texto)
            partes += split_tall(f, CW, CH, os.path.join(ctx.mdir, "_img", "demo-partes"))
        for f, hh in partes:
            if cur and h_cur + GAP + hh > CH:
                cols.append(cur)
                cur, h_cur = [], 0
            cur.append((f, hh))
            h_cur += (GAP if len(cur) > 1 else 0) + hh
        if cur:
            cols.append(cur)
        for k in range(0, len(cols), 2):
            html_cols = "".join(
                f'<div style="width:{CW}px;display:flex;flex-direction:column;gap:{GAP}px">' + "".join(
                    f'<div class="box fill" style="height:{hh:.0f}px;border:1.5px solid rgba(0,0,0,.1)">{ctx.img(f)}</div>'
                    for f, hh in col) + "</div>" for col in cols[k:k + 2])
            page(ctx, "Design system", f'<div class="label">tokens/demo.html · componentes feitos só com as '
                                       f'variáveis</div><div style="display:flex;gap:40px;align-items:flex-start">'
                                       f'{html_cols}</div>')
    elif has("demo.png"):
        page(ctx, "Design system", f'<div class="label">tokens/demo.png</div><div class="box" style="height:800px;'
                                   f'border:1.5px solid rgba(0,0,0,.1)">'
                                   f'{ctx.img(os.path.join(tdir, "demo.png"), style="width:100%;height:100%;object-fit:cover;object-position:top")}</div>')


DEMO_TITULOS = {"tipografia": "Escala tipográfica", "rodape": "Rodapé · canais oficiais",
                "paleta": "Paleta", "forma": "Forma", "lado-a-lado": "As cores lado a lado"}


def pg_demo_pieces(ctx, meta_path, ddir):
    """Páginas do design system com os pedaços da demo em tamanho real (1 px da demo = 1 px da página). A marca-mãe
    mostra todos os componentes; cada produto, só o resumo (botão + tarja/cartão) — os outros repetem em outra cor.
    Pedaços de um mesmo bloco ficam juntos; blocos curtos (versão alternativa) dividem a página. À direita de cada
    pedaço, o que ele é e quais tokens usa."""
    import json
    from PIL import Image
    meta = json.load(open(meta_path, encoding="utf-8"))
    meta = [m for m in meta if m["shot"] != "topo" and os.path.exists(os.path.join(ddir, m["file"]))]
    completo = "marca" if any(m["shot"] == "marca" for m in meta) else (meta[0]["shot"] if meta else "")
    ents = []
    for m in meta:
        if not (m["resumo"] or m["shot"] == completo):
            continue
        w, h = Image.open(os.path.join(ddir, m["file"])).size
        w, h = w / 2, h / 2              # os PNGs são 2×
        k = min(1.0, 1100 / w, 740 / h)      # nunca mais alto que a página (a tipografia da demo passava do pé)
        ents.append({**m, "w": w * k, "h": h * k, "path": os.path.join(ddir, m["file"])})
    BUDGET, GAP = 760, 22
    # grupos (um por bloco da demo, em ordem)
    groups = []
    for e in ents:
        if not groups or groups[-1][0] != e["shot"]:
            groups.append((e["shot"], []))
        groups[-1][1].append(e)
    pages, cur, used = [], [], 0
    for shot, es in groups:
        tot = sum(e["h"] for e in es) + GAP * (len(es) - 1)
        if cur and tot <= BUDGET and used + GAP + tot > BUDGET:   # grupo que cabe numa página mas não na sobra: página nova
            pages.append(cur)
            cur, used = [], 0
        for j_, e in enumerate(es):
            # o cabeçalho de um bloco nunca fica sozinho no pé da página: sai junto com o 1º componente
            need_ = e["h"] + ((GAP + es[j_ + 1]["h"]) if e["sub"] == "cabecalho" and j_ + 1 < len(es) else 0)
            if cur and used + GAP + need_ > BUDGET:   # grupo maior que uma página: segue na próxima
                pages.append(cur)
                cur, used = [], 0
            used += (GAP if cur else 0) + e["h"]
            cur.append(e)
    if cur:
        pages.append(cur)
    for pg_ in pages:
        rows = []
        for e in pg_:
            tit = e["titulo"] or DEMO_TITULOS.get(e["shot"], e["shot"])
            if e["sub"] == "cabecalho" and e["shot"] not in ("lado-a-lado",):
                tit = "Contexto: " + tit
            toks = [x.strip() for x in (e["tokens"] or "").split(",") if x.strip()]
            leg = (f'<div class="label" style="margin-bottom:6px">{E(DEMO_TITULOS.get(e["shot"], e["shot"]) if e["shot"] in DEMO_TITULOS else e["shot"])}</div>'
                   f'<p style="font-size:21px;font-weight:700;line-height:1.25">{E(tit)}</p>')
            if e["produto"] and e["sub"] == "cabecalho":
                leg += f'<p style="font-size:16px;margin-top:8px"><code>data-produto="{E(e["produto"])}"</code></p>'
            if toks:
                leg += ('<p class="small" style="margin-top:10px;font-size:15px;line-height:1.6;opacity:.85">tokens:<br>'
                        + " ".join(f"<code>{E(t)}</code>" for t in toks) + "</p>")
            rows.append(f'<div style="display:flex;gap:44px;align-items:flex-start"><div style="width:{e["w"]:.0f}px;'
                        f'height:{e["h"]:.0f}px;flex:none;border:1.5px solid rgba(0,0,0,.1)">{ctx.img(e["path"], style=f"width:100%;height:100%;display:block")}'
                        f'</div><div style="flex:1;min-width:0;padding-top:4px">{leg}</div></div>')
        page(ctx, "Design system", f'<div class="label" style="margin-bottom:12px">demo do design system · tamanho real'
                                   f' · só variáveis do tokens.css</div><div style="display:flex;flex-direction:column;'
                                   f'gap:{GAP}px">{"".join(rows)}</div>')


def split_tall(path, cw, ch, outdir, faixa_min=None):
    """Imagem que, na largura cw, passa da altura ch → partes cortadas no meio de faixas vazias (linhas de cor
    única, como o espaço entre células), cada uma ≤ ch. Devolve [(arquivo, altura na página)]."""
    from PIL import Image
    import numpy as np
    im = Image.open(path).convert("RGB")
    w, h = im.size
    k = cw / w
    max_h = int(ch / k)
    if h <= max_h:
        return [(path, h * k)]
    arr = np.asarray(im).astype(np.int16)
    vazia = (np.abs(arr - arr[:, :1, :]).max(axis=(1, 2)) <= 3)   # linha toda da cor do 1º pixel
    os.makedirs(outdir, exist_ok=True)
    faixa = faixa_min or max(24, int(w * 0.012))
    out, y, n = [], 0, 0
    base = os.path.splitext(os.path.basename(path))[0]
    while h - y > max_h:
        alvo, lo = y + max_h, y + int(max_h * 0.45)
        cut = alvo
        r = alvo
        while r > lo:   # a faixa vazia mais baixa que cabe: corta no meio dela
            if vazia[r - 1]:
                fim = r
                while r > lo and vazia[r - 1]:
                    r -= 1
                if fim - r >= faixa:   # faixa de verdade (entre células), não o vão entre 2 linhas de texto
                    cut = (r + fim) // 2
                    break
            r -= 1
        n += 1
        f = os.path.join(outdir, f"{base}-{n}.png")
        im.crop((0, y, w, cut)).save(f)
        out.append((f, (cut - y) * k))
        y = cut
    n += 1
    f = os.path.join(outdir, f"{base}-{n}.png")
    im.crop((0, y, w, h)).save(f)
    out.append((f, (h - y) * k))
    return out


def ch_resources(ctx):
    b = ctx.b
    page(ctx, "Recursos", f'<h2>Arquivos</h2><div class="g3">' +
         "".join(f'<div class="card"><h3>{E(t)}</h3><p>{E(d)}</p></div>' for t, d in (
             ("logo/", "assinaturas em SVG (curvas) e PNG, positivas e negativas"),
             ("elementos/", "masters SVG dos elementos gráficos + prévias"),
             ("cores/", "paleta, escalas e matriz de contraste"),
             ("tipografia/", "espécimes; fontes OFL com licença"),
             ("aplicacoes/", "peças em todos os formatos + HTML editável no Adobe Express"),
             ("tokens/ + DESIGN.md", "design system para web, app, Figma e IA"))) +
         f'</div><p class="small" style="margin-top:80px">Versão '
         f'{E(str(b.get("governance.version") or ""))}{" · " if b.get("governance.version") else ""}'
         f'{datetime.date.today():%d/%m/%Y} · status: '
         f'{E(str(b.get("status") or "teste"))}. Marca permanente: fazer busca de anterioridade no INPI antes do '
         f'registro.</p>')


# ------------------------------------------------------------------ novos capítulos (pesquisas 17a · 17b · 17c)
def adef(v, onde):
    """Valor do cliente na página: o valor, ou "[a definir]" marcado (tracejado) + aviso no terminal."""
    v = a_definir(v, onde)
    return f'<span class="adef">{A_DEFINIR}</span>' if v == A_DEFINIR else E(str(v))


def first_clause(s, n=110):
    """Primeira oração de uma regra (até ':' ou ';'), para listas curtas ("5 nãos")."""
    s = re.split(r"[:;]", str(s))[0].strip()
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"


def svg_fill(svg):
    m = re.search(r'fill="(#[0-9A-Fa-f]{6})"', svg or "")
    return m.group(1) if m else None


def logo_bg(ctx, rel):
    """Fundo em que um arquivo de logo foi desenhado: products[].logos/symbols[].bg com o mesmo src; senão, o fundo
    que dá mais contraste com a 1ª cor do SVG."""
    for p in products(ctx.b):
        for it in (p.get("logos") or []) + (p.get("symbols") or []):
            if isinstance(it, dict) and it.get("src") == rel and it.get("bg"):
                return it["bg"]
    f = svg_fill(read(ctx.b.path(rel)))
    if f:
        return ctx.ink if contrast(f, ctx.ink) >= contrast(f, ctx.paper) else ctx.paper
    return ctx.paper


def ink_box(svg):
    """Caixa da TINTA do SVG em % do viewBox (esq, topo, dir, base) — para recortar exatamente o desenho (ex.: mostrar
    "logo arredondado" errado sem depender da margem do arquivo)."""
    import io
    from PIL import Image
    from _base import svg_to_png
    im = Image.open(io.BytesIO(svg_to_png(svg, width=600))).convert("RGBA")
    bb = im.getchannel("A").getbbox()
    if not bb:
        return 0, 0, 0, 0
    W, H = im.size
    return bb[0] / W * 100, bb[1] / H * 100, (W - bb[2]) / W * 100, (H - bb[3]) / H * 100


def rect_svg(w, h, r, fill, stroke=None, cantos=None, extra=""):
    """Retângulo SVG com raio preso a ½ do menor lado (no SVG não há a trava do navegador — 17a F6). cantos =
    (tl, tr, br, bl) para raio por canto."""
    if cantos:
        tl, tr, br, bl = (min(c, w / 2, h / 2) for c in cantos)
        d = (f"M{tl},0H{w - tr}A{tr},{tr} 0 0 1 {w},{tr}V{h - br}A{br},{br} 0 0 1 {w - br},{h}H{bl}"
             f"A{bl},{bl} 0 0 1 0,{h - bl}V{tl}A{tl},{tl} 0 0 1 {tl},0Z")
        shape = f'<path d="{d}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="2"' if stroke else "") + "/>"
    else:
        rr = min(r, w / 2, h / 2)
        shape = (f'<rect width="{w}" height="{h}" rx="{rr:g}" fill="{fill}"' +
                 (f' stroke="{stroke}" stroke-width="2"' if stroke else "") + "/>")
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block;overflow:visible">{shape}{extra}</svg>'


def ch_start(ctx, logos):
    """Comece por aqui (pág. 2, antes do índice): qual logo, quais cores, quais fontes, quais modelos, 5 nãos e a
    quem pedir — as 5 perguntas de toda semana (17b T)."""
    b = ctx.b
    seeds = b.get("color.seeds") or {}
    if not (logos or seeds):
        ctx.skip("Comece por aqui", "sem logo e sem cores no brand.json")
        return
    gov = b.get("governance") or {}
    # logos: principal, secundário (se houver) e símbolo, cada um no fundo em que foi desenhado
    items = [(k, b.get(f"logo.{k}")) for k in ("primary", "secondary", "symbol", "secondary_symbol")]
    nomes = {"primary": "principal", "secondary": "secundário", "symbol": "símbolo (avatar, abaixo do mínimo)",
             "secondary_symbol": "símbolo secundário"}
    cells = []
    for k, rel in items:
        p = b.path(rel) if rel else None
        if not (p and os.path.exists(p)):
            continue
        bg = logo_bg(ctx, rel)
        cells.append(f'<div style="display:flex;gap:16px;align-items:center;margin-bottom:14px"><div style="width:164px;'
                     f'height:92px;flex:none;background:{bg};display:flex;align-items:center;justify-content:center;'
                     f'padding:12px;border:1.5px solid rgba(0,0,0,.08)">{svg_box(read(p), "100%", "100%")}</div>'
                     f'<div style="min-width:0"><b style="font-size:18px">{E(nomes[k])}</b><div class="small" style="'
                     f'font-size:14px;overflow-wrap:anywhere">{E(rel)}</div></div></div>')
    order = [k for k in ("brand", "ink", "paper", "accent") if k in seeds] + [k for k in seeds if k not in
                                                                              ("brand", "ink", "paper", "accent")]
    cores = "".join(f'<div style="display:flex;gap:12px;align-items:center;margin-bottom:14px"><span class="sw" '
                    f'style="background:{(seeds[k]["hex"] if isinstance(seeds[k], dict) else seeds[k])};width:40px;'
                    f'height:40px;margin:0"></span><div><b style="font-size:17px">'
                    f'{E(seeds[k].get("name", k) if isinstance(seeds[k], dict) else k)}</b><div class="small" '
                    f'style="font-size:15px">{(seeds[k]["hex"] if isinstance(seeds[k], dict) else seeds[k])}</div></div></div>'
                    for k in order[:7])
    t = b.get("type") or {}
    fontes = ""
    for role, fam_css, lab in (("display", "brand-display", "títulos"), ("text", "brand-text", "texto"),
                               ("mono", "brand-mono", "números")):
        e = t.get(role)
        if not e:
            continue
        fam = e if isinstance(e, str) else e.get("family")
        fontes += (f'<div style="display:flex;gap:16px;align-items:baseline;margin-bottom:12px"><span style="'
                   f'font-family:{fam_css};font-size:54px;line-height:1;width:84px;flex:none">Aa</span><div><b style="'
                   f'font-size:18px">{E(fam)}</b><div class="small" style="font-size:15px">{lab} · OFL (Google Fonts)'
                   f'</div></div></div>')
    tps = b.get("templates") or []
    modelos = "".join(f'<li style="font-size:17px;margin-bottom:4px">{E(x.get("name", x.get("id", "")))}</li>'
                      for x in tps[:9])
    cmd = ""
    if tps and tps[0].get("command"):
        cmd = (f'<div class="small" style="font-size:14px;margin-top:10px">refazer: <code style="font-size:14px">'
               f'{E(tps[0]["command"].splitlines()[0].split("#")[0].strip())}</code></div>')
    naos = [first_clause(x) for x in (gov.get("naos") or b.get("logo.dont") or [])][:5]
    naos_html = "".join(f'<li style="display:flex;gap:12px;font-size:18px;margin-bottom:8px;list-style:none">'
                        f'<b>✕</b><span>{E(x)}</span></li>' for x in naos)
    col = lambda t_, c: (f'<div style="flex:1;min-width:0"><div class="label">{t_}</div>{c}</div>')  # noqa: E731
    page(ctx, "comece por aqui",
         f'<h2 style="margin-bottom:28px">Comece por aqui</h2>'
         f'<div style="display:flex;gap:44px;height:470px">'
         + col("1 · qual logo usar", "".join(cells) or '<p class="small">sem arquivo de logo</p>')
         + col("2 · quais cores", cores)
         + col("3 · quais fontes", fontes)
         + (col("4 · quais modelos de peça", f'<ul style="margin-left:22px">{modelos}</ul>{cmd}') if tps else "")
         + '</div><div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:44px;margin-top:20px;'
           'border-top:3px solid currentColor;padding-top:22px">'
         + f'<div style="grid-column:span 3;min-width:0"><div class="label">5 · os nãos que mais acontecem</div>'
           f'<ul style="margin:0">{naos_html}</ul></div>'
         + f'<div style="min-width:0"><div class="label">6 · a quem pedir</div><p style="font-size:24px">'
           f'{adef(gov.get("contact") or gov.get("owner"), "governance.contact")}</p><p class="small" style="'
           f'margin-top:10px">versão {adef(gov.get("version"), "governance.version")}</p></div></div>')


# ---------- arquitetura e cor (17c §4.2): entram no capítulo Produtos
def pg_architecture(ctx, prods):
    b = ctx.b
    arch = b.get("architecture") or {}
    if not arch:
        print("  aviso: página 'Como a marca se organiza' pulada — sem brand.json architecture")
        return
    def logo_cell(rel, h=110, mono=False):
        p = b.path(rel) if rel else None
        if not (p and os.path.exists(p)):
            print(f"  aviso: arquitetura · arquivo não encontrado: {rel}")
            return ""
        bg = ctx.ink if mono else logo_bg(ctx, rel)
        return (f'<div style="height:{h}px;min-width:{h * 2}px;background:{bg};display:flex;align-items:center;'
                f'justify-content:center;padding:16px 22px;border:1.5px solid rgba(0,0,0,.08)">'
                f'{svg_box(read(p), "auto", "100%", ctx.paper if mono else None)}</div>')
    rows = []
    end = arch.get("endossante") or {}
    if end:
        rows.append(("endossa", end.get("nome", ""), end.get("como", ""), logo_cell(end.get("logo"))))
    mar = arch.get("marca") or {}
    if mar:
        rows.append(("a marca", mar.get("nome", ""), mar.get("como", ""),
                     '<div style="display:flex;gap:16px">' + "".join(logo_cell(x) for x in mar.get("logos") or []) + "</div>"))
    chips = "".join(f'<div style="width:250px;flex:none;background:{p["colors"]["bg"]};color:{p["colors"]["ink"]};'
                    f'border:1.5px solid rgba(0,0,0,.08)"><div style="background:{p["colors"]["accent"]};height:46px"></div>'
                    f'<div style="padding:10px 12px 12px"><b style="font-size:18px;line-height:1.2;display:block">'
                    f'{E(p.get("color_name") or p.get("tag") or p["name"])}</b><span style="font-size:15px;line-height:1.3;'
                    f'display:block;margin-top:4px">{E(p.get("label") or p["name"])}</span></div></div>' for p in prods)
    pr = arch.get("produtos") or {}
    rows.append(("produtos", f"{len(prods)} cor{'es' if len(prods) > 1 else ''}",
                 (pr.get("como", "").rstrip(" .") + "." + (" Os nomes das cores são proposta: aguardam o sim da cliente."
                                                           if nomes_proposta(prods) else "")).strip(),
                 f'<div style="display:flex;gap:14px">{chips}</div>'))
    se = arch.get("selos") or {}
    if se:
        rows.append(("selos", se.get("nome", ""), se.get("como", ""),
                     '<div style="display:flex;gap:16px">' + "".join(logo_cell(x, 84, mono=True)
                                                                     for x in se.get("arquivos") or []) + "</div>"))
    body = "".join(f'<div style="display:flex;gap:40px;align-items:center;padding:16px 0;border-top:2px solid '
                   f'currentColor"><div style="width:520px;flex:none"><div class="label" style="margin-bottom:4px">'
                   f'{i + 1} · {E(a)}</div><h3 style="font-size:30px;margin-bottom:6px">{E(n)}</h3><p style="'
                   f'font-size:18px;line-height:1.35">{E(c)}</p></div><div style="flex:1;min-width:0;display:flex">{v}</div>'
                   f'</div>' for i, (a, n, c, v) in enumerate(rows))
    st = arch.get("status") or ""
    page(ctx, "Produtos", f'<div style="display:flex;justify-content:space-between;align-items:baseline;gap:40px">'
                          f'<h2 style="margin-bottom:12px">Como a marca se organiza</h2>'
                          + (f'<span class="status">{E(st.split("—")[0].strip())}</span>' if st else "") + '</div>'
                          + (f'<p style="font-size:21px;max-width:1500px;margin-bottom:18px">{E(arch.get("modelo", ""))}</p>'
                             if arch.get("modelo") else "") + body)
    if arch.get("constantes") or arch.get("variavel"):
        cons = "".join(f'<li style="font-size:22px;margin-bottom:8px">{E(x)}</li>' for x in arch.get("constantes") or [])
        por_prod = [(p, _existing(ctx, p.get("symbols"), "símbolo", p["id"])) for p in prods]
        n_lin = max((len(x) for _, x in por_prod), default=0)
        syms = []
        for k in range(min(n_lin, 2)):   # 1 linha por desenho (ex.: Tarja e REC): mesma forma, só a cor muda
            row = "".join(
                f'<div style="flex:1;min-width:0"><div style="height:180px;background:{it.get("bg") or p["colors"]["bg"]};'
                f'display:flex;align-items:center;justify-content:center;padding:28px;border:1.5px solid '
                f'rgba(0,0,0,.08)">{svg_box(read(path), "100%", "100%")}</div>'
                + (f'<p class="small" style="margin-top:8px">{E(p.get("color_name") or p["name"])}</p>' if k == min(n_lin, 2) - 1
                   else "") + '</div>'
                for p, xs in por_prod for path, it in xs[k:k + 1])
            syms.append(f'<div style="display:flex;gap:20px;margin-bottom:20px">{row}</div>')
        page(ctx, "Produtos", h2_badge("O que nunca muda × o que muda", NOMES_BADGE if nomes_proposta(prods) else "") +
                              f'<div class="row" style="gap:70px">'
                              f'<div class="col card"><div class="label">nunca muda (a mãe)</div><ul style="margin-left:24px">'
                              f'{cons}</ul></div><div class="col card" style="flex:1.4"><div class="label">muda (o produto)</div>'
                              f'<p class="lead" style="font-size:28px;margin-bottom:30px">{E(arch.get("variavel", ""))}</p>'
                              f'{"".join(syms)}</div></div>')


def pg_color_tree(ctx):
    tree = color_tree(ctx.b)
    if not tree:
        return
    rows = []
    for i, (q, a, hx) in enumerate(tree, 1):
        sw = (f'<span style="display:inline-block;width:44px;height:44px;background:{hx};flex:none;'
              f'box-shadow:inset 0 0 0 1.5px rgba(0,0,0,.2)"></span>' if hx else
              '<span style="display:inline-block;width:44px;height:44px;flex:none;border:2px dashed currentColor"></span>')
        rows.append(f'<div style="display:flex;align-items:center;gap:28px;padding:12px 0;border-bottom:1.5px solid '
                    f'rgba(0,0,0,.14)"><span style="font-family:brand-display;font-size:40px;width:60px;flex:none;'
                    f'line-height:1">{i}</span><p style="flex:1.25;min-width:0;font-size:22px;line-height:1.3">{E(q)}</p>'
                    f'<span style="font-size:30px;flex:none">→</span><div style="flex:1;min-width:0;display:flex;gap:16px;'
                    f'align-items:center">{sw}<p style="font-size:22px;line-height:1.3;font-weight:700">{E(a)}</p></div></div>')
    page(ctx, "Produtos", h2_badge("Qual cor usar?", NOMES_BADGE if nomes_proposta(products(ctx.b)) else "") +
                          f'<p style="font-size:21px;margin:-10px 0 22px">'
                          f'Pergunte na ordem; a primeira resposta "sim" decide. A cor ajuda a achar; o texto escrito '
                          f'confirma.</p>{"".join(rows)}')


def pg_matrix(ctx, prods):
    """Matriz produto × papel: cada célula com o HEX e o contraste (truncado) contra o fundo (ou contra o destaque,
    no texto-sobre-destaque); erro com a tarja quando nenhuma cor passa."""
    from tokens import ctx_colors, _extra
    b = ctx.b
    head = ["produto", "fundo", "tinta", "destaque", "no destaque", "ao vivo", "visor", "erro"]
    trs = []

    def cell(hx, sobre, need):
        r = contrast(hx, sobre)
        cls = "ok" if r >= need else "ko"
        return (f'<td><span class="sw" style="background:{hx}"></span>{hx}<br><span class="{cls}" style="font-size:16px">'
                f'{fmt_ratio(r)}{"" if r >= need else " ✕"}</span></td>')
    for p in prods:
        for alt, c in ((False, p["colors"]), (True, p["colors"].get("alt"))):
            if not c:
                continue
            cc = ctx_colors(b, c, _extra(p, alt))
            err = (f'<td><span class="sw" style="background:{cc["error"]}"></span>{cc["error"]}<br><span class="ok" '
                   f'style="font-size:16px">{fmt_ratio(contrast(cc["error"], cc["error_surface"] or c["bg"]))}'
                   + (f' em tarja {cc["error_surface"]}' if cc["error_surface"] else "") + "</span></td>")
            trs.append(f'<tr><td><b>{E(p.get("color_name") or p["name"])}</b><br><span class="small" style="font-size:15px">'
                       f'{"alternativa" if alt else "principal"}</span></td>'
                       f'<td><span class="sw" style="background:{c["bg"]}"></span>{c["bg"]}</td>'
                       + cell(c["ink"], c["bg"], 4.5) + cell(c["accent"], c["bg"], 3) + cell(c["on_accent"], c["accent"], 4.5)
                       + cell(cc["live"], c["bg"], 3) + cell(c.get("frame") or c["accent"], c["bg"], 3) + err + "</tr>")
    page(ctx, "Produtos", h2_badge("Matriz produto × papel", NOMES_BADGE if nomes_proposta(prods) else "") +
                          f'<table class="t" style="font-size:17px">'
                          f'<tr>{"".join(f"<th>{h}</th>" for h in head)}</tr>{"".join(trs)}</table>'
                          f'<p class="small" style="margin-top:14px">Contraste WCAG 2, truncado (4,47 vira 4,4). Mínimos: '
                          f'tinta 4,5:1 · destaque, ao vivo e visor 3:1 (gráfico, título grande) · texto no destaque 4,5:1 '
                          f'(✕ = só com texto ≥ 18,7 px negrito). Erro é token fixo, nunca a cor de um produto.</p>')


def pg_color_a11y(ctx, prods):
    """Cor e acessibilidade: as cores dos produtos em visão normal, P&B, deuteranopia e protanopia (Machado 2009) +
    pares que confundem (ΔE2000 < 10) — a prova de por que o rótulo escrito é obrigatório."""
    names = [(p.get("color_name") or p.get("tag") or p["name"]).split("·")[0].strip() for p in prods]
    cols = {nm: p["colors"]["accent"] for nm, p in zip(names, prods)}
    vis = (("normal", "visão normal"), ("pb", "preto e branco"), ("deutan", "deuteranopia"), ("protan", "protanopia"))
    nomes_vis = {"normal": "visão normal", "pb": "P&B", "deutan": "deuteranopia", "protan": "protanopia",
                 "tritan": "tritanopia"}
    w = min(190, (900 - 14 * (len(prods) - 1)) / len(prods))
    head = ('<div style="display:flex;gap:14px;margin-bottom:10px"><div style="width:150px;flex:none"></div>' + "".join(
        f'<div style="width:{w:.0f}px;flex:none;font-size:16px;font-weight:700;line-height:1.2">{E(nm)}</div>'
        for nm in cols) + "</div>")
    grid = head + "".join(
        f'<div style="display:flex;gap:14px;align-items:center;margin-bottom:14px"><div class="label" style="'
        f'width:150px;flex:none;margin:0">{lab}</div>' + "".join(
            f'<div style="width:{w:.0f}px;height:112px;flex:none;background:{simulate(hx, k)};'
            f'box-shadow:inset 0 0 0 1.5px rgba(0,0,0,.15)"></div>' for hx in cols.values()) + "</div>"
        for k, lab in vis)
    pairs = color_pairs_cvd(cols)
    br = lambda x: f"{x:.1f}".replace(".", ",")  # noqa: E731
    trs = "".join(f'<tr><td>{E(r["a"])} × {E(r["b"])}</td><td>{br(r["normal"])}</td><td class="{"ko" if r["deutan"] < 10 else ""}">'
                  f'{br(r["deutan"])}</td><td class="{"ko" if r["protan"] < 10 else ""}">{br(r["protan"])}</td>'
                  f'<td class="{"ko" if r["luz"] < 1.5 else ""}">{fmt_ratio(r["luz"])}</td></tr>' for r in pairs)
    bad = [r for r in pairs if r["confunde"]]
    alerta = ("".join(f'<p style="font-size:18px;margin-top:8px"><b>Par confunde:</b> {E(r["a"])} × {E(r["b"])} '
                      f'({", ".join(nomes_vis[k] for k in r["confunde"])})</p>' for r in bad) if bad else
              '<p style="font-size:18px;margin-top:10px">Nenhum par abaixo de ΔE 10.</p>')
    page(ctx, "Produtos", h2_badge("Cor e acessibilidade", NOMES_BADGE if nomes_proposta(prods) else "") +
                          f'<p style="font-size:19px;margin:-10px 0 24px">'
                          f'As mesmas cores como são vistas. Simulação Machado, Oliveira & Fernandes (2009), severidade '
                          f'total, em RGB linear — modelo, não pessoa.</p><div style="display:flex;gap:56px">'
                          f'<div style="flex:none">{grid}</div><div style="flex:1;min-width:0"><table class="t" style="font-size:16px">'
                          f'<tr><th>par (ΔE2000)</th><th>normal</th><th>deutan</th><th>protan</th><th>P&amp;B</th></tr>{trs}'
                          f'</table>{alerta}<p style="font-size:18px;margin-top:14px">ΔE abaixo de 10 = confunde; P&amp;B = '
                          f'contraste entre as duas (abaixo de 1,5:1 viram o mesmo cinza). Por isso a cor nunca vai '
                          f'sozinha: toda peça e seção de um produto traz o rótulo escrito (WCAG 1.4.1).</p></div></div>')


# ---------- forma (17a §6.2)
def ch_shape(ctx, logos):
    b = ctx.b
    if not b.get("shape"):
        ctx.skip("Forma", "sem brand.json shape")
        return
    shp = shape_spec(b)
    regra = shp["regra"] or "Raios por papel: o componente usa o papel, nunca o número."
    cabeca, _, resto = regra.partition(":")
    resto = resto.strip()
    resto = resto[:1].upper() + resto[1:]
    opener(ctx, "Forma", "Que canto cada elemento tem — e por quê. O raio é decidido pelo PAPEL do elemento.")
    meta = " · ".join(x for x in (f"combinação {shp['combo']}" if shp.get("combo") else "", shp.get("status") or "",
                                  "derivado de shape.radius" if shp["legado"] else "") if x)
    # página 1: a regra em 1 frase + a escala desenhada em tamanho real (arte 1080 e site)
    cols = []
    for k in ("none", "sm", "md", "lg", "full"):
        a, s = shp["arte"][k], shp["site"][k]
        cel = (f"vira ≈ {a / ARTE_POR_SITE:.0f} px no celular" if 0 < a < PILL else
               "meia altura" if a >= PILL else "reto em qualquer tela")
        cols.append(f'<div style="flex:1;min-width:0"><div class="label">{k} · {STEP_NAMES[k]}</div>'
                    f'{rect_svg(260, 150, a, ctx.ink)}<p style="font-size:18px;margin-top:10px"><b>arte 1080:</b> '
                    f'{"pílula" if a >= PILL else f"{a} px"}<br><span class="small" style="font-size:15px">{cel}</span></p>'
                    f'<div style="margin-top:14px">{rect_svg(120, 44, s, ctx.brand)}</div><p style="font-size:18px;'
                    f'margin-top:8px"><b>site:</b> {"pílula" if s >= PILL else f"{s} px"}</p></div>')
    page(ctx, "Forma", (f'<span class="status" style="margin-bottom:22px">{E(meta)}</span>' if meta else "")
         + f'<h1 style="font-size:96px;margin:18px 0 18px;max-width:1500px">{E(cabeca.strip())}</h1>'
         + (f'<p class="lead" style="font-size:26px;max-width:1500px">{E(resto)}</p>' if resto else "")
         + f'<div style="display:flex;gap:40px;margin-top:44px">{"".join(cols)}</div>'
         + f'<p class="small" style="margin-top:22px">Desenho em tamanho real. Raio de arte 1080 ≈ '
           f'{str(ARTE_POR_SITE).replace(".", ",")} × o de site (celular de 393 px): o "raio 10 das redes" é o 28 da arte. '
           f'Pílula = 9999 px, nunca 50 %.</p>'
         + (f'<div class="label" style="margin-top:28px">nunca arredonda</div><div style="display:flex;flex-wrap:wrap;'
            f'gap:10px">' + "".join(
                f'<span style="font-size:17px;font-weight:700;padding:6px 12px;border:1.5px solid currentColor">{E(x)}</span>'
                for x in never_round_labels(shp)) + "</div>" if shp["nunca_arredonda"] else ""))
    # página 2: mapa elemento → papel → raio (inclusive o que é sempre 0)
    rows = []
    for k, p in shp["papeis"].items():
        mini = rect_svg(88, 44, p["site"], ctx.brand if p["site"] else ctx.ink,
                        cantos=p["cantos_site"]) if not p["circulo"] else rect_svg(44, 44, PILL, ctx.brand)
        sv = "/".join(str(x) for x in p["cantos_site"]) if p["cantos_site"] else ("pílula" if p["site"] >= PILL else p["site"])
        av = "/".join(str(x) for x in p["cantos_arte"]) if p["cantos_arte"] else ("pílula" if p["arte"] >= PILL else p["arte"])
        rows.append(f'<div style="display:flex;gap:16px;align-items:center;padding:5px 0;border-bottom:1.5px solid '
                    f'rgba(0,0,0,.12);min-height:50px"><div style="width:92px;flex:none;display:flex">{mini}</div>'
                    f'<div style="flex:1;min-width:0;font-size:15px;line-height:1.25">{E(p["nota"])}</div>'
                    f'<code style="font-size:14px;width:170px;flex:none">radius-{E(k)}</code><div style="width:118px;'
                    f'flex:none;font-size:15px;text-align:right">{"<b>0</b>" if p["site"] == 0 and not p["cantos_site"] else E(str(sv))} · '
                    f'<span class="small" style="font-size:14px">{E(str(av))}</span></div></div>')
    for i in range(0, len(rows), 24):
        chunk = rows[i:i + 24]
        h = math.ceil(len(chunk) / 2)
        hd = ('<div class="label" style="display:flex;gap:16px;margin:0 0 4px;padding-bottom:6px;border-bottom:2px solid '
              'currentColor"><span style="width:92px;flex:none"></span><span style="flex:1">elemento</span>'
              '<span style="width:170px;flex:none">papel (token)</span><span style="width:118px;flex:none;text-align:right">'
              'site · arte</span></div>')
        page(ctx, "Forma", f'<h2 style="margin-bottom:16px">Elemento → papel → raio</h2><div style="display:flex;gap:56px">'
                           f'<div style="flex:1;min-width:0">{hd}{"".join(chunk[:h])}</div><div style="flex:1;min-width:0">'
                           f'{hd}{"".join(chunk[h:])}</div></div><p class="small" style="margin-top:12px">Coluna da direita: '
                           f'site (px CSS) · arte 1080. Quatro números = cantos (sup. esq., sup. dir., inf. dir., inf. esq.).'
                           f' 0 em negrito = sempre reto.</p>')
    # página 3: conta do aninhado + 3 certos × 3 errados + o logo não arredonda
    md = shp["arte"]["md"] or 28
    big = max(md, 24)
    def nested(esp):
        r_in = nested_radius(big, esp)
        W, H = 270, 190
        inner = f'<g transform="translate({esp},{esp})">{rect_svg(W - 2 * esp, H - 2 * esp, r_in, ctx.brand)}</g>'
        return (f'<div><svg width="{W}" height="{H}" style="display:block"><rect width="{W}" height="{H}" rx="{big}" '
                f'fill="{ctx.ink}"/>{inner}</svg><p style="font-size:17px;margin-top:8px">pai {big} · espaço {esp} → '
                f'<b>filho {r_in}</b>{" (reto: conta certa)" if r_in == 0 else ""}</p></div>')
    ink, acc, pap = ctx.ink, ctx.brand, ctx.paper
    sm = shp["arte"]["sm"] or 16
    def tile(svg_inner_, ok, cap):
        return (f'<div><svg viewBox="0 0 310 170" width="100%" style="display:block;background:{ink}">{svg_inner_}</svg>'
                f'<p style="font-size:16px;margin-top:8px;line-height:1.3"><b>{"✓" if ok else "✕"}</b> {E(cap)}</p></div>')
    r = lambda x, y, w, h, rr, f: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(rr, w / 2, h / 2):g}" fill="{f}"/>'  # noqa: E731
    certo = [tile(r(24, 30, 160, 110, md, pap) + r(200, 30, 86, 40, 0, acc) + r(200, 96, 86, 40, PILL, acc), True,
                  f"raios bem diferentes: {md} + reto + pílula"),
             tile(r(24, 60, 126, 50, PILL, acc) + f'<rect x="162" y="60" width="124" height="50" rx="25" fill="none" '
                  f'stroke="{pap}" stroke-width="3"/>', True, "botões da mesma hierarquia com a mesma forma"),
             tile("".join(r(24 + i * 92, 30, 78, 110, md, pap) for i in range(3)) + r(24, 72, 262, 30, 0, acc), True,
                  "o reto raro vira o destaque")]
    errado = [tile(r(24, 30, 125, 110, md, pap) + r(162, 30, 125, 110, round(md * 1.25), pap), False,
                   f"dois raios quase iguais ({md} e {round(md * 1.25)}): parece erro"),
              tile(r(24, 60, 126, 50, PILL, acc) + r(162, 60, 124, 50, 0, acc), False,
                   "pílula e reto na mesma hierarquia"),
              tile("".join(r(24 + i * 92, 30, 78, 50, 0, pap) for i in range(3)) + "".join(
                  r(24 + i * 92, 90, 78, 50, 0, pap) for i in range(2)) + r(208, 90, 78, 50, sm, acc), False,
                   "o reto virou maioria: perdeu o destaque")]
    sym = logos.get("symbol") or logos.get("primary")
    logo_row = ""
    if sym:
        bg = logo_bg(ctx, b.get("logo.symbol") or b.get("logo.primary"))
        l_, t_, r_, b_ = ink_box(sym)
        rr = round(md * 0.5)
        def box(clip, cap, ok):
            return (f'<div style="width:250px"><div class="{"" if ok else "no"}" style="width:250px;height:140px;'
                    f'background:{bg};display:flex;align-items:center;justify-content:center;padding:24px">'
                    f'<div style="width:100%;height:100%;{clip}">{svg_box(sym, "100%", "100%")}</div></div>'
                    f'<p style="font-size:16px;margin-top:8px;line-height:1.3"><b>{"✓" if ok else "✕"}</b> {E(cap)}</p></div>')
        vx, vy, vw, vh = viewbox(sym)
        # o svg ocupa a caixa com "meet": recorte em % da caixa calculado pela proporção do viewBox
        bw, bh = 202, 92
        k = min(bw / vw, bh / vh)
        ox, oy = (bw - vw * k) / 2, (bh - vh * k) / 2
        il, it_ = ox + vw * k * l_ / 100, oy + vh * k * t_ / 100
        ir, ib = ox + vw * k * r_ / 100, oy + vh * k * b_ / 100
        clip = f"clip-path:inset({it_:.1f}px {ir:.1f}px {ib:.1f}px {il:.1f}px round {rr}px)"
        logo_row = (f'<div class="label" style="margin-top:30px">o logo não arredonda</div><div style="display:flex;'
                    f'gap:20px;align-items:flex-start">{box("", "como foi desenhado", True)}'
                    f'{box(clip, "cantos do logo arredondados (nunca)", False)}</div>')
    page(ctx, "Forma", f'<div style="display:flex;gap:64px"><div style="width:600px;flex:none"><h2 style="font-size:52px;'
                       f'margin-bottom:18px">A conta do aninhado</h2><p style="font-size:18px;margin-bottom:16px">Raio do '
                       f'filho = raio do pai − (borda + espaço), nunca negativo.</p><div style="display:flex;gap:30px">'
                       f'{nested(12 if big > 12 else 4)}{nested(big)}</div>{logo_row}</div>'
                       f'<div style="flex:1;min-width:0"><h2 style="font-size:52px;margin-bottom:18px">Certo × errado</h2>'
                       f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px 24px">{"".join(certo)}'
                       f'{"".join(errado)}</div><p class="small" style="margin-top:14px">Por peça: 1 valor da família + 0 + '
                       f'pílula/círculo = no máximo 3 formas. Nunca dois raios com razão menor que 1,5.</p></div></div>')


# ---------- acessibilidade (17b §D, §4.1)
A11Y_CHECKS = ["contraste no pior pixel da letra e de cada par de cor (peças, tokens e paleta)",
               "texto estourando a caixa, botão com menos de 40 px de altura e fonte que não carregou (página de demonstração)",
               "alvo de toque, foco visível e movimento reduzido (verificador das páginas)",
               "zonas da interface do Instagram/Reels — texto fora das áreas cobertas",
               "pares de cor que confundem com daltonismo e em P&B (capítulo Produtos · Cor e acessibilidade)"]


def limpa_refs(x):
    """Tira de um texto de manual as referências internas de pesquisa — "(17c regra 9)", "(pesquisa 17a §7.5)"."""
    return re.sub(r"\s*\((?:pesquisa\s*)?17[abc][^)]*\)", "", str(x)).strip()


def ch_accessibility(ctx):
    from tokens import a11y_rules, access, STATE, OPACITY_DISABLED
    b = ctx.b
    rules = a11y_rules(b)
    acc = b.get("accessibility") or {}
    opener(ctx, "Acessibilidade", "Regras para todo mundo ler, enxergar e usar — base WCAG 2.2 AA e ABNT NBR 17225:2025.")
    base = rules[:12]
    cards = "".join(f'<div class="card" style="padding-top:14px"><div class="label" style="margin-bottom:6px">{i:02d}</div>'
                    f'<h3 style="font-size:27px;margin-bottom:6px">{E(n)}</h3><p style="font-size:18px;line-height:1.35">'
                    f'{E(r_)}</p></div>' for i, (n, r_) in enumerate(base, 1))
    page(ctx, "Acessibilidade", f'<h2 style="margin-bottom:22px">As regras</h2><div class="g4" style="row-gap:26px">{cards}</div>')
    a = access(b)
    shp = shape_spec(b)
    rb, rf = shp["papeis"]["button"]["site"], shp["papeis"]["focus"]["site"]
    extra = rules[12:]
    ex = "".join(f'<li style="font-size:20px;margin-bottom:10px"><b>{E(n)}:</b> {E(limpa_refs(r_))}</li>' for n, r_ in extra)
    foco = (f'<div style="display:flex;gap:40px;align-items:flex-end"><div><div style="display:inline-flex;align-items:center;'
            f'height:{a["target"]}px;padding:0 26px;background:{ctx.ink};color:{ctx.paper};font-weight:700;font-size:17px;'
            f'outline:{a["width"]}px solid {ctx.ink};outline-offset:{a["offset"]}px;border-radius:{min(rb, 999)}px">'
            f'Botão com foco</div>'
            f'<p class="small" style="margin-top:14px">anel {a["width"]} px, afastado {a["offset"]} px, ≥ 3:1; raio do anel '
            f'= botão + {a["offset"]}{" (pílula)" if rf >= PILL else f" = {rf} px"}</p></div>'
            f'<div style="display:flex;gap:18px;align-items:flex-end"><div style="width:{a["target"]}px;height:{a["target"]}px;'
            f'border:2px solid currentColor;display:flex;align-items:center;justify-content:center;font-size:14px">'
            f'{a["target"]}</div><div style="width:24px;height:24px;border:2px dashed currentColor"></div></div>'
            f'<p class="small">alvo {a["target"]} px (nosso padrão) · 24 px (mínimo WCAG 2.5.8), tamanho real</p></div>')
    checks = "".join(f"<li style='font-size:19px;margin-bottom:6px'>{E(x)}</li>" for x in (acc.get("checks") or A11Y_CHECKS))
    page(ctx, "Acessibilidade", f'<div class="row" style="gap:80px"><div class="col">'
                                + (f'<h2 style="font-size:56px">Regras da marca</h2><ul style="margin-left:24px">{ex}</ul>'
                                   if extra else "")
                                + f'<h2 style="font-size:56px;margin-top:{40 if extra else 0}px">Em token</h2>{foco}'
                                  f'<p style="font-size:19px;margin-top:22px">hover = camada de {STATE["hover"]:.0%} · pressionado '
                                  f'{STATE["pressed"]:.0%} · desabilitado = opacidade {str(OPACITY_DISABLED).replace(".", ",")}</p>'
                                  f'<p style="font-size:17px;margin-top:10px">tokens: <code style="white-space:nowrap">'
                                  f'--focus-ring-*</code> · <code style="white-space:nowrap">--target-min</code></p></div>'
                                  f'<div class="col"><h2 style="font-size:56px">O que o verificador mede</h2>'
                                  f'<ul style="margin-left:24px">{checks}</ul>'
                                + (f'<p class="small" style="margin-top:24px">{E(limpa_refs(acc["status"]))}</p>' if acc.get("status") else "")
                                + '</div></div>')


# ---------- canais (17b §K, §M): só diagrama o que existe em brand.json channels
def ch_channels(ctx):
    b = ctx.b
    ch = b.get("channels") or {}
    if not ch:
        ctx.skip("Canais", "sem brand.json channels (instagram, whatsapp)")
        return
    opener(ctx, "Canais", "Instagram e WhatsApp: o uniforme do perfil e do grupo.")
    cols = []
    wa = ch.get("whatsapp") or {}
    if wa:
        foto = b.path(wa.get("photo")) if wa.get("photo") else None
        diag = ""
        if foto and os.path.exists(foto):
            img = ctx.img(foto, style="width:100%;height:100%;object-fit:cover;display:block")
            diag = (f'<div style="display:flex;gap:36px;align-items:flex-end"><div style="position:relative;width:320px;'
                    f'height:320px;flex:none">{img}<svg width="320" height="320" style="position:absolute;left:0;top:0">'
                    f'<path d="M0,0H320V320H0Z M160,0A160,160 0 1 0 160.01,0Z" fill="{ctx.paper}" fill-opacity=".86" '
                    f'fill-rule="evenodd"/><circle cx="160" cy="160" r="159" fill="none" stroke="{ctx.ink}" stroke-width="1.5"/>'
                    f'<circle cx="160" cy="160" r="{0.35 * 320:.0f}" fill="none" stroke="#fff" stroke-width="2" '
                    f'stroke-dasharray="8 6"/></svg></div><div style="display:flex;gap:22px;align-items:flex-end">'
                    + "".join(f'<div style="text-align:center"><div style="width:{s}px;height:{s}px;border-radius:50%;'
                              f'overflow:hidden">{ctx.img(foto, style="width:100%;height:100%;object-fit:cover")}</div>'
                              f'<p class="small" style="margin-top:6px">{s} px</p></div>' for s in (110, 48, 32))
                    + '</div></div><p class="small" style="margin-top:12px">Recorte redondo do app (fora dele, clareado) e, '
                      'tracejado, a área do essencial. Os círculos pequenos estão em tamanho real.</p>')
        elif wa.get("photo"):
            print(f"  aviso: canais · foto do grupo não encontrada: {wa['photo']}")
        slots = "".join(f'<div style="display:flex;gap:16px;padding:8px 0;border-bottom:1.5px solid rgba(0,0,0,.12)">'
                        f'<b style="width:220px;flex:none;font-size:18px">{lab}</b><span style="font-size:18px">'
                        f'{adef(wa.get(k), f"channels.whatsapp.{k}") if not isinstance(wa.get(k), list) else (E(" · ".join(map(str, wa[k]))) if wa.get(k) else adef(None, f"channels.whatsapp.{k}"))}'
                        f'</span></div>' for lab, k in (("nome do grupo", "group_name"), ("descrição", "description"),
                                                        ("mensagens-modelo", "messages"), ("figurinhas", "stickers")))
        bal = "".join(f'<div style="background:#fff;color:#111;padding:12px 16px;margin-top:10px;max-width:560px;'
                      f'font-size:18px;line-height:1.35;border:1.5px solid rgba(0,0,0,.14);border-radius:0 12px 12px 12px">{E(x)}</div>'
                      for x in wa.get("copy_do_documento") or [])
        cols.append(f'<div class="col"><h2 style="font-size:56px;margin-bottom:20px">WhatsApp</h2>{diag}'
                    + (f'<p style="font-size:17px;margin-top:10px">{E(wa["photo_rule"])}</p>' if wa.get("photo_rule") else "")
                    + f'<div style="margin-top:18px">{slots}</div>'
                    + (f'<div class="label" style="margin-top:20px">frases do documento sobre o grupo</div>{bal}' if bal else "")
                    + "</div>")
    ig = ch.get("instagram") or {}
    if ig:
        av = b.path(ig.get("avatar")) if ig.get("avatar") else None
        avh = ""
        if av and os.path.exists(av):
            svg = read(av) if av.lower().endswith(".svg") else None
            bgc = ig.get("avatar_bg") or ctx.ink
            avh = '<div style="display:flex;gap:24px;align-items:flex-end;margin-bottom:20px">' + "".join(
                f'<div style="text-align:center">{avatar(svg, bgc, s) if svg else ""}<p class="small">{s} px</p></div>'
                for s in (110, 48, 32)) + "</div>"
        rows = "".join(f'<div style="display:flex;gap:16px;padding:8px 0;border-bottom:1.5px solid rgba(0,0,0,.12)">'
                       f'<b style="width:200px;flex:none;font-size:18px">{lab}</b><span style="font-size:18px">'
                       f'{adef(ig.get(k), f"channels.instagram.{k}")}</span></div>'
                       for lab, k in (("perfil (@)", "handle"),) + tuple((l_, k_) for l_, k_ in (
                           ("destaques", "highlights"), ("regra da grade", "grid"), ("modelo de legenda", "caption"))
                           if k_ in ig))
        cols.append(f'<div class="col" style="flex:.8"><h2 style="font-size:56px;margin-bottom:20px">Instagram</h2>{avh}{rows}'
                    f'<p class="small" style="margin-top:14px">Só o que existe no brand.json é desenhado; o resto fica '
                    f'"{A_DEFINIR}" até a cliente decidir.</p></div>')
    page(ctx, "Canais", f'<div class="row" style="gap:80px">{"".join(cols)}</div>')


# ---------- canais oficiais e jurídico (17b §R, §X)
def ch_legal(ctx):
    b = ctx.b
    off, legal = b.get("official") or {}, b.get("legal") or {}
    if not (off or legal):
        ctx.skip("Canais oficiais e jurídico", "sem brand.json official / legal")
        return
    opener(ctx, "Canais oficiais e jurídico", "Onde a marca está de verdade, o que ela nunca pede e o que protege o uso.")
    lista = "".join(f'<div style="display:flex;gap:20px;padding:12px 0;border-bottom:1.5px solid rgba(0,0,0,.12)">'
                    f'<b style="width:200px;flex:none;font-size:22px">{lab}</b><span style="font-size:22px">'
                    f'{adef(off.get(k), f"official.{k}")}</span></div>'
                    for lab, k in (("Instagram", "instagram"), ("WhatsApp", "whatsapp"), ("Site", "site"), ("E-mail", "email")))
    never = [x for x in off.get("never") or [] if not vazio(x)]
    nv = ("".join(f'<li style="font-size:22px">{E(x)}</li>' for x in never) if never else
          f'<li style="font-size:22px;list-style:none">{adef(None, "official.never")}</li>')
    st = (legal.get("trademark_status") or "").strip()
    reg = "concedido" == st.lower()
    simbolo = ("® liberado (registro concedido no INPI)" if reg else
               "sem ® — o ® só entra com o registro concedido no INPI; antes disso, ™ ou nada")
    page(ctx, "Canais oficiais e jurídico",
         f'<div class="row" style="gap:80px"><div class="col"><h2 style="font-size:60px">Canais oficiais</h2>{lista}'
         f'<div class="label" style="margin-top:28px">nunca pedimos</div><ul style="margin-left:24px">{nv}</ul>'
         + (f'<div style="margin-top:24px;padding:18px 22px;border:2px dashed currentColor"><div class="label">sugestão — '
            f'precisa do sim da cliente</div><p style="font-size:19px">{E(off["sugestao"])}</p></div>' if off.get("sugestao") else "")
         + f'</div><div class="col"><h2 style="font-size:60px">Marca</h2><div style="display:flex;gap:20px;padding:12px 0;'
           f'border-bottom:1.5px solid rgba(0,0,0,.12)"><b style="width:200px;flex:none;font-size:22px">registro</b>'
           f'<span style="font-size:22px">{adef(st, "legal.trademark_status")}</span></div>'
           f'<p style="font-size:22px;margin-top:16px"><b>{"®" if reg else "Símbolo"}:</b> {E(simbolo)}</p>'
           + "".join(f'<div style="display:flex;gap:20px;padding:12px 0;border-bottom:1.5px solid rgba(0,0,0,.12)">'
                     f'<b style="width:200px;flex:none;font-size:22px">{lab}</b><span style="font-size:22px">'
                     f'{adef(legal.get(k), f"legal.{k}")}</span></div>' for lab, k in (("titular", "titular"), ("CNPJ", "cnpj")))
         + (f'<p style="font-size:20px;margin-top:18px">{E(legal["mec"])}</p>' if legal.get("mec") else "")
         + '<p class="small" style="margin-top:24px">Marca permanente: busca de anterioridade no INPI antes do registro.</p>'
           '</div></div>')
    rel = "".join(f'<tr><td>{E(r.get("quem", ""))}</td><td>{adef(r.get("autorizacao_imagem"), "legal.releases." + slugify(r.get("quem", "")))}</td></tr>'
                  for r in legal.get("releases") or [])
    cred = "".join(f'<tr><td>{E(r.get("o_que", ""))}</td><td>{adef(r.get("quem"), "legal.credits")}</td></tr>'
                   for r in legal.get("credits") or [])
    lic = "".join(f'<tr><td>{E(r.get("o_que", ""))}</td><td>{E(r.get("licenca", ""))}</td></tr>'
                  for r in legal.get("licenses") or [])
    if rel or cred or lic:
        page(ctx, "Canais oficiais e jurídico",
             '<div class="row" style="gap:80px"><div class="col">'
             + (f'<h2 style="font-size:56px">Autorização de imagem</h2><table class="t"><tr><th>pessoa</th><th>autorização</th>'
                f'</tr>{rel}</table>' if rel else "")
             + (f'<h2 style="font-size:56px;margin-top:40px">Créditos</h2><table class="t"><tr><th>o quê</th><th>de quem</th>'
                f'</tr>{cred}</table>' if cred else "")
             + '</div><div class="col">'
             + (f'<h2 style="font-size:56px">Licenças</h2><table class="t"><tr><th>o quê</th><th>licença</th></tr>{lic}</table>'
                if lic else "") + '</div></div>')


# ---------- governança (17b §S)
def ch_governance(ctx):
    b = ctx.b
    g = b.get("governance") or {}
    if not g:
        ctx.skip("Governança", "sem brand.json governance (versão, dono, quem aprova, changelog…)")
        return
    opener(ctx, "Governança", "Quem cuida da marca, como pedir uma peça e como os arquivos se chamam.")
    stat = "".join(f'<div class="card"><div class="label">{lab}</div><p style="font-size:30px;line-height:1.2">'
                   f'{adef(g.get(k), f"governance.{k}")}</p></div>'
                   for lab, k in (("versão", "version"), ("status", "status"), ("dono da marca", "owner"),
                                  ("contato", "contact")))
    apr = "".join(f'<tr><td>{E(r.get("o_que", ""))}</td><td>{adef(r.get("quem"), "governance.approvers")}</td></tr>'
                  for r in g.get("approvers") or [])
    log = "".join(f'<tr><td style="white-space:nowrap">{E(r.get("data", ""))}</td><td>{E(r.get("o_que", ""))}</td>'
                  f'<td>{E(r.get("por_que", ""))}</td></tr>' for r in (g.get("changelog") or [])[-6:])
    page(ctx, "Governança", f'<div class="g4" style="margin-bottom:40px">{stat}</div><div class="row" style="gap:70px">'
                            + (f'<div style="width:620px;flex:none"><h3>Quem aprova o quê</h3><table class="t"><tr><th>o quê'
                               f'</th><th>quem</th></tr>{apr}</table></div>' if apr else
                               f'<div style="width:620px;flex:none"><h3>Quem aprova o quê</h3><p>{adef(None, "governance.approvers")}</p></div>')
                            + (f'<div class="col"><h3>O que mudou</h3><table class="t" style="font-size:17px"><tr><th>quando'
                               f'</th><th>o quê</th><th>por quê</th></tr>{log}</table></div>' if log else "") + '</div>')
    rq = g.get("request") or {}
    campos = "".join(f'<li style="font-size:20px">{E(x)}</li>' for x in rq.get("campos") or [])
    nm = g.get("naming") or {}
    exp = "".join(f'<tr><td>{E(r.get("uso", ""))}</td><td>{E(r.get("formato", ""))}</td></tr>' for r in g.get("exports") or [])
    page(ctx, "Governança",
         f'<div class="row" style="gap:70px"><div style="width:560px;flex:none"><h3>Como pedir uma peça</h3>'
         + (f'<ol style="margin-left:26px">{campos}</ol>' if campos else f'<p>{adef(None, "governance.request")}</p>')
         + (f'<p style="font-size:19px;margin-top:14px"><b>onde:</b> {adef(rq.get("onde"), "governance.request.onde")} · '
            f'<b>prazo:</b> {adef(rq.get("prazo"), "governance.request.prazo")}</p>' if rq else "")
         + f'<h3 style="margin-top:36px">Onde baixar</h3><p style="font-size:20px">{adef(g.get("downloads"), "governance.downloads")}</p>'
           f'</div><div class="col">'
         + (f'<h3>Nome de arquivo</h3><pre style="font-size:20px;padding:20px">{E(nm.get("padrao", ""))}\n'
            f'ex.: {E(nm.get("exemplo", ""))}</pre>' + (f'<p class="small">{E(nm["status"])}</p>' if nm.get("status") else "")
            if nm else "")
         + (f'<h3 style="margin-top:30px">Exportar para cada uso</h3><table class="t" style="font-size:17px"><tr><th>uso</th>'
            f'<th>formato</th></tr>{exp}</table>' if exp else "") + '</div></div>')


def ch_decisions(ctx):
    """Decisões pendentes (brand.json decisions.itens): o que ainda precisa do sim da cliente, o que o manual usa hoje e
    o que muda depois. O estúdio registra; quem decide é a cliente."""
    d = ctx.b.get("decisions") or {}
    itens = [x for x in (d.get("itens") or []) if isinstance(x, dict)]
    if not itens:
        ctx.skip("Decisões pendentes", "sem brand.json decisions")
        return
    opener(ctx, "Decisões pendentes", d.get("intro") or "O que ainda precisa do sim da cliente.")
    por_pag = 4
    n_pag = math.ceil(len(itens) / por_pag)
    for k in range(0, len(itens), por_pag):
        rows = []
        for it in itens[k:k + por_pag]:
            rows.append(
                f'<div style="display:grid;grid-template-columns:64px minmax(0,1.25fr) minmax(0,1fr) minmax(0,1fr);gap:36px;'
                f'padding:16px 0;border-top:2px solid currentColor;align-items:start">'
                f'<div style="font-family:brand-display;font-size:52px;line-height:.95">{int(it.get("n", 0)):02d}</div>'
                f'<div><h3 style="font-size:32px;margin-bottom:8px">{E(it.get("tema", ""))}</h3>'
                f'<p style="font-size:22px;line-height:1.35">{E(it.get("pergunta", ""))}</p></div>'
                f'<div><div class="label" style="margin-bottom:4px">hoje no manual</div>'
                f'<p style="font-size:21px;line-height:1.35">{E(it.get("hoje", ""))}</p></div>'
                f'<div><div class="label" style="margin-bottom:4px">se mudar</div>'
                f'<p style="font-size:21px;line-height:1.35">{E(it.get("depois", ""))}</p></div></div>')
        tit = "Decisões pendentes" + (f" ({k // por_pag + 1}/{n_pag})" if n_pag > 1 else "")
        page(ctx, "Decisões pendentes", f'<h2 style="margin-bottom:20px">{tit}</h2>{"".join(rows)}')


def coverage(ctx):
    """Cobertura do manual: chaves preenchidas do brand.json que nenhum capítulo leu (17b §4.3)."""
    data = ctx.b.data
    used = ctx.used
    faltam = []
    for k, v in data.items():
        if k in COBERTURA_IGNORA or k.endswith(("_note", "_nota")) or vazio(v):
            continue
        if f"{k}.*" in used:
            continue
        if isinstance(v, dict):
            subs = [s for s, sv in v.items() if s not in SUB_IGNORA and not vazio(sv)]
            fora = [s for s in subs if f"{k}.{s}" not in used]
            if fora and len(fora) == len(subs):     # bloco inteiro fora do manual
                faltam.append(f"{k} (bloco inteiro, {len(subs)} campos)")
            else:
                faltam += [f"{k}.{s}" for s in fora]
        elif not any(u.startswith(k + ".") for u in used):
            n = len(v) if isinstance(v, list) else 1
            faltam.append(k + (f" ({n} itens)" if isinstance(v, list) else ""))
    if faltam:
        print(f"  cobertura: {len(faltam)} chave(s) preenchida(s) do brand.json sem capítulo no manual: "
              + ", ".join(faltam))
    else:
        print("  cobertura: toda chave preenchida do brand.json aparece em algum capítulo")
    return faltam


PATH_EXT = (".svg", ".png", ".jpg", ".jpeg", ".webp", ".pdf", ".json", ".md", ".txt", ".py", ".ttf", ".otf", ".mp4")


def check_paths(b):
    """Todo caminho de arquivo citado no brand.json existe? (moveu arquivo → atualizar o brand.json; não só o logo
    principal). Avisa os que faltam, uma linha por caminho."""
    faltam = []

    def walk(node, onde):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{onde}.{k}" if onde else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{onde}[{i}]")
        elif isinstance(node, str):
            v = node.strip()
            if (v.lower().endswith(PATH_EXT) and "/" in v and v.count(" ") <= 2 and ": " not in v
                    and not v.startswith(("http", "<", "%"))):   # "pasta/Arquivo 15.svg" sim; frase não
                p = b.path(v)
                if not os.path.exists(p):
                    faltam.append(f"{onde} → {v}")
    walk(b.data, "")
    for x in faltam:
        print(f"  aviso caminho: {x} (não existe)")
    if not faltam:
        print("  caminhos: todo arquivo citado no brand.json existe")
    return faltam


# ------------------------------------------------------------------ build
def cmd_build(a):
    b = load_brand(a.brand)
    ctx = Ctx(b, a.inline)
    logos = logo_files(b)
    if not logos:
        try:
            import apply
            apply.logo_path(b)
            logos = logo_files(b)
        except Exception:
            pass
    ctx.used.clear()   # cobertura conta só o que os capítulos leem
    ch_cover(ctx, logos)
    ch_start(ctx, logos)
    page(ctx, "índice", "__TOC__")          # o índice é montado no fim, com os capítulos que saíram de verdade
    toc_at = len(ctx.pages) - 1
    # capítulos antigos não avisam quando pulam: o build compara as páginas antes/depois e avisa
    for nome, fn, why in (
            ("Essência", lambda: ch_essence(ctx), "sem platform.*"),
            ("Logo", lambda: ch_logo(ctx, logos), "sem logo.primary (SVG)"),
            ("Cor", lambda: ch_color(ctx), "sem color.seeds"),
            ("Produtos", lambda: ch_products(ctx), "sem products"),
            ("Tipografia", lambda: ch_type(ctx), "sem type.display e type.text"),
            ("Elementos gráficos", lambda: ch_elements(ctx, logos), "sem devices, elements, patterns ou "
                                                                   "elementos/catalogo/*.png"),
            ("Forma", lambda: ch_shape(ctx, logos), "sem shape"),
            ("Grid e layout", lambda: ch_grid(ctx), "sem grid"),
            ("Imagem", lambda: ch_imagery(ctx), "sem imagery.* nem imagem/*.png|jpg"),
            ("Ícones", lambda: ch_icons(ctx), "sem icones/*.svg"),
            ("Movimento", lambda: ch_motion(ctx), "sem motion"),
            ("Voz", lambda: ch_voice(ctx), "sem platform.voice"),
            ("Canais", lambda: ch_channels(ctx), "sem channels"),
            ("Modelos de peça", lambda: ch_templates(ctx), "sem templates"),
            ("Aplicações", lambda: ch_applications(ctx), "sem mockups/ nem aplicacoes/*/pecas/*.png"),
            ("Páginas e sites", lambda: ch_pages(ctx), "sem pages.items"),
            ("Acessibilidade", lambda: ch_accessibility(ctx), "—"),
            ("Design system", lambda: ch_system(ctx), "sem tokens/tokens.css (rode tokens.py build antes)"),
            ("Canais oficiais e jurídico", lambda: ch_legal(ctx), "sem official / legal"),
            ("Governança", lambda: ch_governance(ctx), "sem governance"),
            ("Decisões pendentes", lambda: ch_decisions(ctx), "sem decisions"),
            ("Recursos", lambda: ch_resources(ctx), "—")):
        antes = len(ctx.pages)
        fn()
        if len(ctx.pages) == antes and nome not in ctx.skipped:
            ctx.skip(nome, why)
    rows = "".join(f'<div><span><b>{n:02d}</b>{E(t)}</span></div>' for n, t, _ in ctx.chapters)
    ch, h = ctx.pages[toc_at]
    ctx.pages[toc_at] = (ch, h.replace("__TOC__", f'<h2>Índice</h2><div class="toc">{rows}</div>'))
    coverage(ctx)
    check_paths(b)
    faces, _ = brand_font_faces(b)
    css = (CSS.replace("__INK__", ctx.ink).replace("__PAPER__", ctx.paper).replace("__BRAND__", ctx.brand)
           .replace("__ONBRAND__", ink_on(ctx.brand, ctx.paper, ctx.ink)))
    doc = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{E(b.name)} — manual da marca</title>'
           f'<meta name="viewport" content="width=1920"><style>{faces}\n{css}</style></head><body>'
           + "".join(h for _, h in ctx.pages) + "</body></html>")
    os.makedirs(ctx.mdir, exist_ok=True)
    out_html = os.path.join(ctx.mdir, "manual.html")
    write(out_html, doc)
    print(f"html: {out_html} ({len(ctx.pages)} páginas)")
    qa_layout(out_html)
    if a.qa_only:
        return
    if not a.no_pdf:
        chrome = find_chrome()
        pdf = os.path.join(ctx.mdir, "manual.pdf")
        r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            "--virtual-time-budget=15000", f"--print-to-pdf={pdf}",
                            "file:///" + out_html.replace("\\", "/")], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        print(f"pdf: {pdf}" if os.path.exists(pdf) else f"pdf falhou: {r.stderr[-400:]}")
    if not a.no_png:
        pdir = os.path.join(ctx.mdir, "paginas")
        os.makedirs(pdir, exist_ok=True)
        for old in glob.glob(os.path.join(pdir, "*.png")):
            os.remove(old)
        # margem/sombra da tela desligadas por regra CSS (um 2º atributo style na <section> seria ignorado e
        # apagaria o fundo próprio das páginas de produto)
        head = (doc.split("<body>")[0].replace("</head>", "<style>.page{margin:0!important;box-shadow:none!important}"
                                                          "</style></head>") + "<body style='background:none'>")
        pngs = []
        for i, (_, h) in enumerate(ctx.pages, 1):
            tmp = os.path.join(ctx.mdir, f"_p{i:02d}.html")
            write(tmp, head + h + "</body></html>")
            png = os.path.join(pdir, f"{i:02d}.png")
            html_screenshot(tmp, png, 1920, 1080)
            os.remove(tmp)
            pngs.append(png)
        sheet_pages(pngs, os.path.join(ctx.mdir, "folha.png"))
        print(f"páginas: {pdir} · folha: {os.path.join(ctx.mdir, 'folha.png')}")


QA_JS = r"""
() => {
  const out = [];
  const pages = Array.from(document.querySelectorAll('section.page'));
  pages.forEach((pg, idx) => {
    const P = pg.getBoundingClientRect();
    const opener = pg.classList.contains('opener');
    const has_hdr = !!pg.querySelector('.hdr');
    const items = [];
    const walker = document.createTreeWalker(pg, NodeFilter.SHOW_ELEMENT);
    let el = walker.currentNode;
    const skipSel = '.hdr, .ftr';
    while (el) {
      if (el !== pg && !el.closest(skipSel)) {
        const cs = getComputedStyle(el);
        if (cs.display !== 'none' && cs.visibility !== 'hidden') {
          // texto direto
          let txt = '';
          let rects = [];
          el.childNodes.forEach(n => {
            if (n.nodeType === 3 && n.textContent.trim()) {
              txt += n.textContent;
              const rg = document.createRange();
              rg.selectNodeContents(n);
              rects = rects.concat(Array.from(rg.getClientRects()).filter(r => r.width > 0 && r.height > 0));
            }
          });
          txt = txt.trim();
          if (txt) {
            rects.forEach(r => {
              items.push({tag: el.tagName, txt: txt.slice(0, 40), l: r.left - P.left, t: r.top - P.top,
                          r: r.right - P.left, b: r.bottom - P.top, fs: parseFloat(cs.fontSize)});
            });
          }
        }
      }
      el = walker.nextNode();
    }
    // limite de uma caixa que corta (overflow hidden) o conteúdo
    const boxes = Array.from(pg.querySelectorAll('*')).filter(e => !e.closest(skipSel));
    const clipped = [];
    boxes.forEach(e => {
      const cs = getComputedStyle(e);
      if ((cs.overflow === 'hidden' || cs.overflowX === 'hidden') && e.scrollWidth > e.clientWidth + 2 &&
          e.textContent.trim() && cs.textOverflow !== 'clip') {
        clipped.push(e.textContent.trim().slice(0, 40));
      }
    });
    const probs = [];
    items.forEach(it => {
      if (!opener && has_hdr && it.b > 992) probs.push(`texto passa de y=992 (fundo/rodapé): "${it.txt}" até y=${it.b.toFixed(0)}`);
      if (it.r > 1802 && has_hdr && !opener) probs.push(`texto passa da margem direita: "${it.txt}" até x=${it.r.toFixed(0)}`);
      if (it.l < 118 && has_hdr && !opener) probs.push(`texto antes da margem esquerda: "${it.txt}" x=${it.l.toFixed(0)}`);
      if (it.fs < 13.5) probs.push(`corpo pequeno ${it.fs.toFixed(1)}px: "${it.txt}"`);
    });
    // sobreposição de textos (caixa real das linhas)
    for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) {
      const a = items[i], b = items[j];
      const ox = Math.min(a.r, b.r) - Math.max(a.l, b.l), oy = Math.min(a.b, b.b) - Math.max(a.t, b.t);
      if (a.fs > 150 || b.fs > 150) continue;
      const mh = Math.min(a.b - a.t, b.b - b.t);
      if (ox > 3 && oy > 0.3 * mh && oy > 3) probs.push(`textos sobrepostos: "${a.txt}" × "${b.txt}" (${ox.toFixed(0)}×${oy.toFixed(0)} px)`);
    }
    clipped.forEach(c => probs.push(`texto cortado pela caixa: "${c}"`));
    // qualquer caixa/imagem (fora do fluxo absoluto) que passa do pé ou da margem direita
    if (has_hdr && !opener) {
      boxes.forEach(e => {
        const cs = getComputedStyle(e);
        if (cs.position === 'absolute' || cs.position === 'fixed') return;
        if (e.closest('[style*="position:absolute"]')) return;
        const q = e.getBoundingClientRect();
        if (!q.width || !q.height) return;
        if (q.bottom - P.top > 1002) probs.push(`caixa passa do pé: <${e.tagName.toLowerCase()}> até y=${(q.bottom - P.top).toFixed(0)}`);
        if (q.right - P.left > 1803) probs.push(`caixa passa da margem direita: <${e.tagName.toLowerCase()}> até x=${(q.right - P.left).toFixed(0)}`);
      });
    }
    if (probs.length) out.push({page: idx + 1, probs: Array.from(new Set(probs))});
  });
  return out;
}
"""


def qa_layout(html_path, verbose=True):
    """Verificador de layout do manual (no navegador): texto que passa do pé da página ou da margem, textos
    sobrepostos, texto cortado pela caixa, corpo < 13,5 px. Imprime uma linha por problema; devolve a lista."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("  aviso: playwright ausente — verificador de layout pulado")
        return []
    res = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome")
        pg = br.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto("file:///" + html_path.replace("\\", "/"))
        pg.wait_for_timeout(1500)
        pg.evaluate("document.fonts.ready")
        res = pg.evaluate(QA_JS)
        br.close()
    if verbose:
        for r in res:
            for p in r["probs"]:
                print(f"  layout pág {r['page']:02d}: {p}")
        if not res:
            print("  layout: nenhuma página com texto fora da área, sobreposto ou cortado")
    return res


def sheet_pages(pngs, out, cols=4, w=480):
    from PIL import Image
    h = int(w * 1080 / 1920)
    rows = math.ceil(len(pngs) / cols)
    s = Image.new("RGB", (cols * (w + 14) + 14, rows * (h + 14) + 14), (205, 205, 200))
    for i, p in enumerate(pngs):
        im = Image.open(p).convert("RGB").resize((w, h))
        s.paste(im, (14 + (i % cols) * (w + 14), 14 + (i // cols) * (h + 14)))
    s.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("build"); p.add_argument("brand"); p.add_argument("--inline", action="store_true")
    p.add_argument("--no-pdf", action="store_true"); p.add_argument("--no-png", action="store_true")
    p.add_argument("--qa-only", action="store_true", help="gera o HTML e roda só o verificador de layout")
    p.set_defaults(fn=cmd_build)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
