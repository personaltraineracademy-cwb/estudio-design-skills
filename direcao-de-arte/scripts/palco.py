"""palco.py — monta peças em HTML/CSS e renderiza no Chrome (Playwright), com INSPEÇÃO no navegador.

Por que: posicionar elemento por coordenada à mão gera desalinhamento. O navegador tem layout de verdade:
- **Grade real**: CSS Grid (colunas, gutters, áreas) → alinhamentos exatos por construção.
- **`text-box: trim-both cap alphabetic`**: a caixa do texto vai do TOPO DA MAIÚSCULA à LINHA DE BASE → "topo do
  texto alinhado ao topo da imagem" passa a ser literal.
- **`text-wrap: balance`** (títulos) e **`pretty`** (texto): quebras equilibradas, sem viúva.
- Kerning e recursos OpenType da própria fonte (`font-feature-settings`, numerais tabulares `tnum`), eixos variáveis
  (`font-variation-settings: "wdth" 75`).
- Fontes EMBUTIDAS (arquivo variável completo, base64) → o render é idêntico em qualquer máquina.

Inspeção (`Palco.qa`): mede no próprio navegador cada elemento marcado com `data-qa="rótulo"` e
`data-tipo="txt|logo|barra|foto|visor|rotulo"` (texto com recuo óptico: `data-l`/`data-r` = sobras laterais em px,
para medir pela TINTA):
  margem/zona segura · colisão · texto sobre a PESSOA (lê o alfa do recorte no canvas) · bordas QUASE alinhadas ·
  maiúscula menor que o mínimo (25 px num lado menor de 1080).
Uso:
  from palco import Palco
  st = Palco(1080, 1350, formato="feed", fontes={"voz": ("Schibsted Grotesk", "<arquivo.ttf>"), ...})
  png, avisos = st.render(corpo_html, "saida.png", css_extra="...")
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compor as K  # noqa: E402

FONT_DIR = os.path.join(os.path.expanduser("~"), ".cache", "brand-studio", "fonts")


def fonte_variavel(familia):
    """Arquivo VARIÁVEL completo da família no cache (ex.: 'SchibstedGrotesk[wght].ttf'); baixa se faltar."""
    import glob
    slug = "".join(c for c in familia.lower() if c.isalnum())
    cand = glob.glob(os.path.join(FONT_DIR, slug, "*[[]*.ttf"))
    if not cand:
        K.font(f"{familia}:400")        # baixa a família (fonts.py guarda o arquivo variável na pasta)
        cand = glob.glob(os.path.join(FONT_DIR, slug, "*[[]*.ttf"))
    return sorted(cand)[0] if cand else None


def cap_ratio(arquivo):
    from fontTools.ttLib import TTFont
    f = TTFont(arquivo)
    upm = f["head"].unitsPerEm
    cap = getattr(f["OS/2"], "sCapHeight", 0) or 0.7 * upm
    return cap / upm


def data_url(path, mime):
    return f"data:{mime};base64,{base64.b64encode(open(path, 'rb').read()).decode()}"


JS_MEDIDAS = r"""
async () => {
  const peca = document.getElementById('peca');
  const R0 = peca.getBoundingClientRect();
  const out = [];
  for (const el of peca.querySelectorAll('[data-qa]')) {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const dl = parseFloat(el.dataset.l || 0), dr = parseFloat(el.dataset.r || 0);   // sobras laterais (tinta)
    out.push({r: el.dataset.qa, t: el.dataset.tipo || 'txt', sangra: el.dataset.sangra === '1',
              alinha: el.dataset.alinha !== '0', ler: el.dataset.ler === '1', area: el.dataset.area || '',
              c: [r.left - R0.left + dl, r.top - R0.top, r.right - R0.left - dr, r.bottom - R0.top],
              fs: parseFloat(cs.fontSize), fam: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim()});
  }
  // alfa das fotos (para "texto sobre a pessoa")
  const fotos = [];
  for (const img of peca.querySelectorAll('img[data-tipo="foto"]')) {
    await img.decode().catch(() => {});
    const r = img.getBoundingClientRect();
    const cv = document.createElement('canvas');
    cv.width = Math.round(r.width); cv.height = Math.round(r.height);
    const cx = cv.getContext('2d');
    cx.drawImage(img, 0, 0, cv.width, cv.height);
    fotos.push({r: img.dataset.qa, c: [r.left - R0.left, r.top - R0.top, r.right - R0.left, r.bottom - R0.top],
                w: cv.width, h: cv.height, id: fotos.length});
    window['__alfa' + (fotos.length - 1)] = cx.getImageData(0, 0, cv.width, cv.height).data;
  }
  window.__fotos = fotos;
  return {els: out, fotos};
}
"""

JS_OCUPA = r"""
([i, x0, y0, x1, y1]) => {
  const f = window.__fotos[i], a = window['__alfa' + i];
  let n = 0, tot = 0;
  for (let y = Math.max(0, Math.floor(y0)); y < Math.min(f.h, Math.ceil(y1)); y += 2)
    for (let x = Math.max(0, Math.floor(x0)); x < Math.min(f.w, Math.ceil(x1)); x += 2) {
      tot++; if (a[(y * f.w + x) * 4 + 3] > 40) n++;
    }
  return tot ? n / tot : 0;
}
"""


class Palco:
    def __init__(self, W, H, formato=None, margem=None, my=None, fontes=None, fundo="#111"):
        self.W, self.H = W, H
        self.s = min(W, H)
        m0 = round(0.074 * self.s)
        self.zona = K.FORMATOS.get(formato, {}).get("zona", (0, 0, 0, 0)) if formato else (0, 0, 0, 0)
        self.excl = K.FORMATOS.get(formato, {}).get("excl", []) if formato else []
        # margem lateral = a maior entre a padrão e a zona lateral do app (no 9:16, 108) → grade e texto na mesma borda
        self.m = max(m0, self.zona[2], self.zona[3]) if margem is None else margem
        self.formato = formato
        self.my = m0 if my is None else my
        self.fontes = {}           # alias → (família css, arquivo)
        self.caps = {}             # família css → cap/em
        for alias, (fam, arq) in (fontes or {}).items():
            arq = arq or fonte_variavel(fam)
            self.fontes[alias] = (fam, arq)
            self.caps[fam] = cap_ratio(arq)
        self.fundo = fundo

    def area(self):
        """Caixa onde texto/logo/CTA podem morar: margem ∩ fora da zona da interface do app (x0, y0, x1, y1)."""
        zt, zb, zl, zr = self.zona
        return (max(self.m, zl), max(self.my, zt), self.W - max(self.m, zr), self.H - max(self.my, zb))

    # ---------------------------------------------------------------- HTML
    def css_base(self):
        ff = "".join(f"@font-face{{font-family:'{fam}';src:url({data_url(arq, 'font/ttf')}) format('truetype');"
                     f"font-weight:100 1000;font-stretch:50% 200%;}}" for fam, arq in self.fontes.values())
        return ff + f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#777}}
#peca{{position:relative;width:{self.W}px;height:{self.H}px;overflow:hidden;background:{self.fundo};
  font-kerning:normal;text-rendering:geometricPrecision;-webkit-font-smoothing:antialiased}}
.cap{{text-box:trim-both cap alphabetic}}
.bal{{text-wrap:balance}}
.pretty{{text-wrap:pretty}}
.tnum{{font-variant-numeric:tabular-nums}}
[data-tipo="txt"]{{width:fit-content;white-space:nowrap}}   /* quebra só onde NÓS pomos <br> (regras do PT-BR) */
.bal,.pretty{{white-space:normal}}
.abs{{position:absolute}}
.full{{position:absolute;inset:0}}
"""

    def html(self, corpo, css_extra=""):
        return (f"<!doctype html><html><head><meta charset='utf-8'><style>{self.css_base()}{css_extra}</style></head>"
                f"<body><div id='peca'>{corpo}</div></body></html>")

    # ---------------------------------------------------------------- render + inspeção
    # CSS das duas passadas (como um PSD: imagem embaixo, tipo por cima)
    CSS_SO_IMAGEM = ("#peca *{color:transparent!important;text-shadow:none!important;-webkit-text-stroke:0!important}"
                     "#peca img[data-tipo=logo]{visibility:hidden!important}")
    CSS_SO_TIPO = ("html,body,#peca{background:transparent!important}"
                   "#peca *{background:transparent!important;border-color:transparent!important;"
                   "box-shadow:none!important;outline-color:transparent!important}"
                   "#peca img:not([data-tipo=logo]),#peca svg:not([data-tipo=logo]){visibility:hidden!important}"
                   "#peca [data-tipo=foto],#peca .full{visibility:hidden!important}")

    def render(self, corpo, out, css_extra="", escala=1, transparente=False, html_out=None, pos=None):
        """Render + verificador. Com `pos` (função numpy float 0–1 → float 0–1), DUAS PASSADAS:
        1) IMAGEM: fundo, foto e elementos SEM texto e sem logo → `pos` (grão único, halação, dither, cor…) → salva
           também `<out>-sem-texto.png` (é o 'textless' que a prova usa para o contraste real);
        2) TIPO: só texto e logos sobre transparente → colado por cima (alfa), nítido, sem efeito nenhum.
        Assim o efeito de imagem nunca toca a letra — a regra L6 × L7 da pilha."""
        from playwright.sync_api import sync_playwright
        doc = self.html(corpo, css_extra)
        if transparente:
            doc = doc.replace(f"background:{self.fundo};", "background:transparent;").replace(
                "html,body{background:#777}", "html,body{background:transparent}")
        if html_out:
            open(html_out, "w", encoding="utf-8").write(doc)
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome", headless=True)
            pg = b.new_page(viewport={"width": self.W + 40, "height": self.H + 40}, device_scale_factor=escala)
            pg.set_content(doc, wait_until="load")
            pg.evaluate("document.fonts.ready")
            med = pg.evaluate(JS_MEDIDAS)
            avisos = self._qa(med, pg)
            if pos is None:
                pg.locator("#peca").screenshot(path=out, omit_background=transparente)
            else:
                import io
                import numpy as np
                from PIL import Image
                t1 = pg.add_style_tag(content=self.CSS_SO_IMAGEM)
                img = np.asarray(Image.open(io.BytesIO(pg.locator("#peca").screenshot())).convert("RGB"))
                pg.evaluate("(e) => e.remove()", t1)
                pg.add_style_tag(content=self.CSS_SO_TIPO)
                tipo = np.asarray(Image.open(io.BytesIO(pg.locator("#peca").screenshot(omit_background=True)))
                                  .convert("RGBA")).astype(np.float32) / 255
                base = np.clip(pos(img.astype(np.float32) / 255), 0, 1)
                Image.fromarray(np.round(base * 255).astype(np.uint8)).save(out.replace(".png", "-sem-texto.png"))
                a = tipo[..., 3:4]
                fim = base * (1 - a) + tipo[..., :3] * a
                Image.fromarray(np.round(np.clip(fim, 0, 1) * 255).astype(np.uint8)).save(out)
            b.close()
        return out, avisos

    def _qa(self, med, pg):
        W, H, m, my = self.W, self.H, self.m, self.my
        zt, zb, zl, zr = self.zona
        out = []
        els = med["els"]
        for e in els:
            if e["t"] in ("rotulo", "fundo"):
                continue
            x0, y0, x1, y1 = e["c"]
            h = y1 - y0
            tv, th = (0.32 * h, 0.03 * h) if e["t"] == "txt" else (0.6, 0.6)
            if e.get("area") == "heroi":                 # corpo do herói: área de herói (pesquisa 9 §9)
                ha = K.FORMATOS.get(self.formato, {}).get("heroi") if self.formato else None
                hx = K.FORMATOS.get(self.formato, {}).get("heroi_excl", []) if self.formato else []
                if ha and (x0 < ha[0] - 0.6 or y0 < ha[1] - 0.6 or x1 > ha[2] + 0.6 or y1 > ha[3] + 0.6):
                    out.append(f"fora da área de herói: {e['r']} ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
                elif any(K._inter(e["c"], z, 0.6) for z in hx):
                    out.append(f"herói sob a coluna de ícones: {e['r']}")
            elif not e["sangra"]:
                if x0 < m - th or y0 < my - tv or x1 > W - m + th or y1 > H - my + tv:
                    out.append(f"fora da margem: {e['r']} ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
                elif e["t"] in ("txt", "logo", "barra") and (y0 < zt - tv or y1 > H - zb + tv or x0 < zl - th or
                                                              x1 > W - zr + th):
                    out.append(f"na zona da interface do app: {e['r']}")
                elif e["t"] in ("txt", "logo", "barra") and any(K._inter(e["c"], z, th + 0.5) for z in self.excl):
                    out.append(f"sob os ícones do app (coluna do Reels): {e['r']}")
            if e["t"] == "txt" and e["fam"] in self.caps:
                cap = e["fs"] * self.caps[e["fam"]]
                if cap < K.CAP_MIN * self.s - 0.5:
                    out.append(f"texto pequeno demais ({cap:.0f}px < {K.CAP_MIN * self.s:.0f}px): {e['r']}")
                elif e.get("ler") and cap < K.CAP_LER * self.s - 0.5:
                    out.append(f"texto que precisa ser lido pequeno ({cap:.0f}px < {K.CAP_LER * self.s:.0f}px): {e['r']}")
        cont = [e for e in els if e["t"] in ("txt", "logo", "barra") and not e["r"].startswith("dentro ")]
        for i, a in enumerate(cont):
            for b_ in cont[i + 1:]:
                if K._inter(a["c"], b_["c"], 1.0):
                    out.append(f"colisão: {a['r']} × {b_['r']}")
            for v in [e for e in els if e["t"] == "visor"]:
                if K._inter(a["c"], v["c"], 0.0):
                    out.append(f"encosta na moldura: {a['r']}")
            if a["t"] == "txt" and not a["r"].startswith("sobre-foto"):
                for f in med["fotos"]:
                    ic = K._inter(a["c"], f["c"], 0.0)
                    if ic:
                        fx, fy = f["c"][0], f["c"][1]
                        oc = pg.evaluate(JS_OCUPA, [f["id"], ic[0] - fx, ic[1] - fy, ic[2] - fx, ic[3] - fy])
                        if oc > 0.003:
                            out.append(f"texto sobre a pessoa ({oc:.0%}): {a['r']}")
        lim = 0.015 * self.s
        for nome, idx in (("esquerda", 0), ("direita", 2)):
            xs = [(e["c"][idx], e["r"]) for e in cont if e["alinha"] and not e["sangra"]]
            for i, (xa, ra) in enumerate(xs):
                for xb, rb in xs[i + 1:]:
                    if 0.5 < abs(xa - xb) < lim:
                        out.append(f"quase alinhado ({nome}, {abs(xa - xb):.1f}px): {ra} × {rb}")
        return out


def inspecao(png, out=None):
    """4 quadrantes a 100% + a peça a 25% numa folha só (para o olho)."""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    W, H = im.size
    q = [im.crop((0, 0, W // 2, H // 2)), im.crop((W // 2, 0, W, H // 2)), im.crop((0, H // 2, W // 2, H)),
         im.crop((W // 2, H // 2, W, H))]
    th = im.resize((W // 4, H // 4), Image.LANCZOS)
    S = Image.new("RGB", (W + th.width + 60, H + 40), (120, 120, 120))
    for i, c in enumerate(q):
        S.paste(c, (10 + (i % 2) * (W // 2 + 10), 10 + (i // 2) * (H // 2 + 10)))
    S.paste(th, (W + 40, 10))
    out = out or png.replace(".png", "-inspecao.png")
    S.save(out)
    return out


# ---------------------------------------------------------------- utilidades de craft
_LSB = {}


def lados(arquivo, texto, tamanho, wdth=None, wght=None):
    """Recuo ÓPTICO: (sobra esquerda da 1ª letra, sobra direita da última) em px no corpo `tamanho`, medido na
    instância CERTA (peso e largura usados no CSS). Use como margin-left/right negativos para alinhar pela TINTA."""
    from fontTools.ttLib import TTFont
    key = (arquivo, wdth, wght)
    if key not in _LSB:
        f = TTFont(arquivo)
        if "fvar" in f and (wdth or wght):
            from fontTools.varLib.instancer import instantiateVariableFont
            loc = {}
            axes = {a.axisTag for a in f["fvar"].axes}
            if wght and "wght" in axes:
                loc["wght"] = wght
            if wdth and "wdth" in axes:
                loc["wdth"] = wdth
            f = instantiateVariableFont(f, loc)
        _LSB[key] = f
    f = _LSB[key]
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    from fontTools.pens.boundsPen import BoundsPen

    def bounds(ch):
        g = cmap.get(ord(ch))
        if not g:
            return 0, 0, 0
        pen = BoundsPen(gs)
        gs[g].draw(pen)
        adv = f["hmtx"][g][0]
        if not pen.bounds:
            return 0, 0, adv
        return pen.bounds[0], adv - pen.bounds[2], adv

    t = texto.strip()
    l = bounds(t[0])[0] if t else 0
    r = bounds(t[-1])[1] if t else 0
    return l / upm * tamanho, r / upm * tamanho


def logo_tinta(master_svg, margem=0.02):
    """Master com moldura = tinta + margem → SVG cuja caixa É a tinta (para alinhar no layout por CSS)."""
    vx, vy, vw, vh = K.viewbox(master_svg)
    ih = vh / (1 + 2 * margem)
    pad = margem * ih
    import re
    s = re.sub(r'viewBox="[^"]*"', f'viewBox="{vx + pad:.3f} {vy + pad:.3f} {vw - 2 * pad:.3f} {vh - 2 * pad:.3f}"',
               master_svg, count=1)
    s = re.sub(r'\swidth="[^"]*"', "", s, count=1)
    s = re.sub(r'\sheight="[^"]*"', "", s, count=1)
    return s, (vw - 2 * pad) / (vh - 2 * pad)


def svg_url(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


def png_url(im, fmt="PNG", q=93):
    import io
    buf = io.BytesIO()
    im.save(buf, fmt, quality=q) if fmt == "JPEG" else im.save(buf, fmt)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(buf.getvalue()).decode()
