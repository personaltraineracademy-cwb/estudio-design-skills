"""Estudo de referências (sites, prints, PDFs) → medidas, folha visual e amostras de fontes.
Método completo: references/referencias-e-pesquisa.md

  python referencia.py pdf  "C:/FireShot/*.pdf" -o %TEMP%/proj-rascunho/refs
      PDF de print de página (FireShot: 1 página com várias imagens) → PNG na resolução nativa + fatias de 2000 px.
  python referencia.py medir https://site.com.br -o tokens.json
      Abre o site no Chrome e lê no código: fontes carregadas, estilos de texto, variáveis :root, raios, bordas,
      sombras duras, fundos (grão SVG, grades, máscaras), pseudo-elementos (traços, cantoneiras) e formas (clip-path).
      Grava tokens.json + tokens.md (resumo legível).
  python referencia.py folha estudo.json -o _folha-estudo.png
      Folha visual: por site, recortes numerados + princípios + o que não repetir. Formato do JSON no fim deste arquivo.
  python referencia.py fontes fontes.json -o _amostras-fontes.png
      Amostras lado a lado (título ajustado à mesma largura, número, preço, telefone, teste Il1/O0/rn×m, parágrafo).
"""
import argparse, base64, glob, json, os, sys

if hasattr(sys.stdout, "reconfigure"):  # console do Windows (cp1252) quebra com acentos e setas
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------- pdf
def pdf(arquivos, saida, fatia=2000, larg_fatia=1280):
    import pymupdf
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    os.makedirs(saida, exist_ok=True)
    feitos = []
    for f in arquivos:
        d = pymupdf.open(f)
        base = os.path.splitext(os.path.basename(f))[0][:60].replace(" ", "_")
        for i, p in enumerate(d):
            info = p.get_image_info(xrefs=True)
            z = (info[0]["width"] / p.rect.width) if info else 2.0       # escala nativa do print
            pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z))
            png = os.path.join(saida, f"{base}-p{i}.png")
            pix.save(png)
            im = Image.open(png).convert("RGB")
            k = 0
            for y in range(0, im.height, fatia):
                c = im.crop((0, y, im.width, min(im.height, y + fatia)))
                if c.width > larg_fatia:
                    c = c.resize((larg_fatia, round(c.height * larg_fatia / c.width)), Image.LANCZOS)
                c.save(png[:-4] + f"-{k}.jpg", quality=88)
                k += 1
            feitos.append((png, im.size, k))
            print(f"{png}  {im.size[0]}x{im.size[1]}  {k} fatias")
    return feitos


# ---------------------------------------------------------------- medir
JS_MEDIR = r"""
async () => {
  await document.fonts.ready;
  const txt = new Map();
  for (const el of document.querySelectorAll('body *')) {
    if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    const c = getComputedStyle(el);
    if (c.display === 'none' || c.visibility === 'hidden') continue;
    const k = [c.fontFamily.split(',')[0].replace(/"/g,''), c.fontWeight, c.fontSize, c.lineHeight, c.letterSpacing,
               c.textTransform, c.color].join(' | ');
    if (!txt.has(k)) txt.set(k, el.textContent.trim().replace(/\s+/g,' ').slice(0, 50));
  }
  const fontes = [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/"/g,'') + ' ' + f.weight + ' ' + f.style))];
  const raiz = [...document.styleSheets].flatMap(s => { try { return [...s.cssRules] } catch (e) { return [] } })
                 .filter(r => r.selectorText === ':root').map(r => r.cssText);
  const sel = el => (el.tagName.toLowerCase() + '.' + (typeof el.className === 'string' ? el.className : '').trim().split(/\s+/).slice(0,3).join('.')).slice(0, 80);
  const caixa = el => { const r = el.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top + scrollY), Math.round(r.width), Math.round(r.height)]; };
  const vis = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; });
  const conta = (lista) => { const m = new Map(); for (const v of lista) m.set(v, (m.get(v) || 0) + 1); return [...m.entries()].sort((a,b) => b[1]-a[1]).slice(0, 25); };
  const cs = vis.map(e => [e, getComputedStyle(e)]);
  const raios = conta(cs.map(([e,c]) => c.borderRadius).filter(v => v !== '0px'));
  const bordas = conta(cs.map(([e,c]) => c.borderTopWidth !== '0px' && c.borderTopStyle !== 'none' ? c.borderTopWidth + ' ' + c.borderTopStyle + ' ' + c.borderTopColor : null).filter(Boolean));
  const sombras = cs.filter(([e,c]) => c.boxShadow !== 'none').slice(0, 30).map(([e,c]) => ({sel: sel(e), sombra: c.boxShadow, raio: c.borderRadius, borda: c.borderTopWidth + ' ' + c.borderTopColor, texto: (e.innerText||'').trim().slice(0,30)}));
  const fundos = cs.filter(([e,c]) => c.backgroundImage !== 'none').slice(0, 30).map(([e,c]) => ({sel: sel(e), imagem: c.backgroundImage.slice(0, 600), tamanho: c.backgroundSize, mistura: c.mixBlendMode, opacidade: c.opacity, posicao: c.position, mascara: (c.maskImage || c.webkitMaskImage || 'none').slice(0, 200), caixa: caixa(e)}));
  const formas = cs.filter(([e,c]) => c.clipPath !== 'none' || (c.maskImage && c.maskImage !== 'none')).slice(0, 20).map(([e,c]) => ({sel: sel(e), clip: c.clipPath.slice(0, 400), mascara: (c.maskImage||'').slice(0,200), filtro: c.backdropFilter}));
  const svgs = [...document.querySelectorAll('svg path')].filter(p => (p.getAttribute('d')||'').length > 40 && p.closest('svg').getBoundingClientRect().width > 120).slice(0, 12).map(p => ({svg: sel(p.closest('svg')), d: p.getAttribute('d').slice(0, 400)}));
  const pseudo = [];
  for (const [e,c] of cs) for (const ps of ['::before','::after']) { const p = getComputedStyle(e, ps);
    if (p.content === 'none' || p.content === 'normal') continue;
    const marca = p.backgroundColor !== 'rgba(0, 0, 0, 0)' || p.borderTopStyle !== 'none' || p.borderLeftStyle !== 'none' || p.backgroundImage !== 'none';
    if (marca) pseudo.push({sel: sel(e) + ps, conteudo: p.content.slice(0,30), w: p.width, h: p.height, fundo: p.backgroundColor, bordaTopo: p.borderTopWidth + ' ' + p.borderTopColor, bordaEsq: p.borderLeftWidth + ' ' + p.borderLeftColor, imagem: p.backgroundImage.slice(0,200), pos: [p.top, p.left, p.right, p.bottom].join(' ')});
    if (pseudo.length > 40) break; }
  const botoes = [...document.querySelectorAll('a,button')].filter(b => { const c = getComputedStyle(b); return c.backgroundColor !== 'rgba(0, 0, 0, 0)' && b.getBoundingClientRect().width > 60; }).slice(0, 10).map(b => { const c = getComputedStyle(b); return {texto: (b.innerText||'').trim().slice(0,30), fundo: c.backgroundColor, cor: c.color, raio: c.borderRadius, borda: c.borderTopWidth + ' ' + c.borderTopColor, sombra: c.boxShadow, preench: c.padding, fonte: c.fontFamily.split(',')[0] + ' ' + c.fontWeight + ' ' + c.fontSize, tt: c.textTransform, ls: c.letterSpacing, caixa: caixa(b)}; });
  const coresFundo = conta(cs.map(([e,c]) => c.backgroundColor).filter(v => v !== 'rgba(0, 0, 0, 0)'));
  const coresTexto = conta(cs.map(([e,c]) => c.color));
  const secoes = [...document.querySelectorAll('section, main > div, footer, header')].filter(e => e.getBoundingClientRect().height > 200).slice(0, 25).map(e => { const c = getComputedStyle(e); return {sel: sel(e), fundo: c.backgroundColor, imagem: c.backgroundImage.slice(0,80), caixa: caixa(e), preench: c.padding}; });
  return {url: location.href, titulo: document.title, largura: innerWidth, fontes, estilosTexto: [...txt.entries()], raiz, raios, bordas, sombras, fundos, formas, svgs, pseudo, botoes, coresFundo, coresTexto, secoes};
}
"""


def medir(url, saida, largura=1440, celular=False):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        vp = {"width": 390, "height": 844} if celular else {"width": largura, "height": 900}
        pg = b.new_page(viewport=vp, device_scale_factor=2 if celular else 1)
        pg.goto(url, wait_until="networkidle", timeout=60000)
        pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")      # dispara carregamento preguiçoso
        pg.wait_for_timeout(1200)
        pg.evaluate("window.scrollTo(0, 0)")
        dados = pg.evaluate(JS_MEDIR)
        shot = os.path.splitext(saida)[0] + ("-celular" if celular else "") + ".png"
        pg.screenshot(path=shot, full_page=True)
        b.close()
    json.dump(dados, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = [f"# Medidas de {dados['url']}", "", f"Título: {dados['titulo']} · largura {dados['largura']} px · print: `{os.path.basename(shot)}`", "",
          "## Fontes carregadas", *[f"- {f}" for f in dados["fontes"]], "",
          "## Estilos de texto (família | peso | tamanho | entrelinha | espaçamento | caixa | cor → exemplo)",
          *[f"- {k} → \"{v}\"" for k, v in dados["estilosTexto"][:60]], "",
          "## Variáveis :root", *[f"```\n{r[:3000]}\n```" for r in dados["raiz"][:4]], "",
          "## Raios mais usados", *[f"- {r} ×{n}" for r, n in dados["raios"]], "",
          "## Bordas", *[f"- {r} ×{n}" for r, n in dados["bordas"]], "",
          "## Botões", *[f"- {json.dumps(x, ensure_ascii=False)}" for x in dados["botoes"]], "",
          "## Sombras", *[f"- {x['sel']}: `{x['sombra']}` raio {x['raio']} borda {x['borda']} \"{x['texto']}\"" for x in dados["sombras"]], "",
          "## Fundos (grão, grades, degradês, máscaras)", *[f"- {x['sel']}: `{x['imagem'][:300]}` tam {x['tamanho']} mistura {x['mistura']} opac {x['opacidade']} {x['posicao']} máscara `{x['mascara'][:100]}`" for x in dados["fundos"]], "",
          "## Formas (clip-path, máscara)", *[f"- {x['sel']}: `{x['clip'][:300]}` {x['filtro']}" for x in dados["formas"]], "",
          "## Paths SVG grandes", *[f"- {x['svg']}: `{x['d'][:300]}`" for x in dados["svgs"]], "",
          "## Pseudo-elementos com marca (traços, cantoneiras, aspas)", *[f"- {json.dumps(x, ensure_ascii=False)}" for x in dados["pseudo"]], "",
          "## Cores de fundo", *[f"- {c} ×{n}" for c, n in dados["coresFundo"]], "",
          "## Cores de texto", *[f"- {c} ×{n}" for c, n in dados["coresTexto"]], "",
          "## Seções (ritmo)", *[f"- {x['sel']}: fundo {x['fundo']} {x['imagem']} caixa {x['caixa']} preench {x['preench']}" for x in dados["secoes"]]]
    open(os.path.splitext(saida)[0] + ".md", "w", encoding="utf-8").write("\n".join(md))
    print(saida, "+", os.path.splitext(saida)[0] + ".md", "+", shot)
    return dados


# ---------------------------------------------------------------- folha e fontes (HTML → PNG)
def _png(html, out, largura=2400, js=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page(viewport={"width": largura, "height": 1200})
        pg.set_content(html, wait_until="load")
        pg.evaluate("document.fonts.ready")
        if js:
            pg.evaluate(js)
        pg.screenshot(path=out, full_page=True)
        b.close()
    print(out)


def _fontes_base():
    from palco import data_url, fonte_variavel
    return (f"@font-face{{font-family:V;src:url({data_url(fonte_variavel('Schibsted Grotesk'), 'font/ttf')});font-weight:100 1000}}"
            f"@font-face{{font-family:M;src:url({data_url(fonte_variavel('Martian Mono'), 'font/ttf')});font-weight:100 1000;font-stretch:50% 200%}}")


CSS_FOLHA = """*{box-sizing:border-box;margin:0;padding:0}
body{width:2400px;background:#EDEAE3;color:#121212;font-family:V;padding:96px}
header{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid #121212;padding-bottom:40px;margin-bottom:72px}
h1{font-weight:800;font-size:92px;letter-spacing:-0.025em;line-height:1}
header p{font:500 26px/1.4 V;max-width:760px;text-align:right;color:#3a3a3a}
section{margin-bottom:96px}
.cab{display:flex;gap:28px;align-items:center;margin-bottom:28px}
.let{font:800 30px/1 M;background:#121212;color:#EDEAE3;width:64px;height:64px;display:grid;place-items:center;border-radius:14px}
h2{font-weight:800;font-size:52px;letter-spacing:-0.02em;line-height:1}
.url{font:500 21px/1.4 M;font-stretch:80%;color:#555;margin-top:10px}
.figs{display:grid;gap:24px;align-items:start}
figure{background:#fff;border:2px solid #121212;border-radius:18px;overflow:hidden}
figure img{display:block;width:100%;height:330px;object-fit:cover;object-position:50% 0%}
figcaption{font:500 22px/1.35 V;padding:18px 20px;display:flex;gap:14px;border-top:2px solid #121212}
figcaption b{font:800 18px/1 M;background:#E8520A;color:#fff;border-radius:999px;min-width:30px;height:30px;display:grid;place-items:center;flex:none}
.rodape{display:grid;grid-template-columns:2fr 1fr;gap:24px;margin-top:24px}
.pr,.nao{border-radius:18px;padding:28px 32px}
.pr{background:#121212;color:#EDEAE3} .nao{background:#fff;border:2px dashed #B33A1A}
.rot{font:700 17px/1 M;letter-spacing:.12em;margin-bottom:18px;color:#E8520A}
.nao .rot{color:#B33A1A}
ul{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:12px 36px}
li{font:500 23px/1.35 V;padding-left:36px;position:relative}
li::before{content:"";position:absolute;left:0;top:.62em;width:22px;height:2px;background:#E8520A}
.nao p:last-child{font:500 23px/1.4 V}"""


def folha(spec, out):
    """spec = {"titulo", "subtitulo", "pasta" (dos recortes), "sites": [{"letra","nome","url","tokens",
    "recortes": [{"arquivo","legenda","ajuste" (css object-fit/position, opcional)}], "principios": [...], "nao": "..."}]}"""
    pasta = spec.get("pasta", ".")

    def img(n):
        ext = os.path.splitext(n)[1].lower().strip(".").replace("jpg", "jpeg")
        return f"data:image/{ext};base64," + base64.b64encode(open(os.path.join(pasta, n), "rb").read()).decode()

    blocos = []
    for s in spec["sites"]:
        rec = s["recortes"]
        cols = "1.25fr " + " ".join(["1fr"] * (len(rec) - 1)) if len(rec) > 1 else "1fr"
        figs = "".join(f'<figure><img src="{img(r["arquivo"])}" style="{("object-fit:" + r["ajuste"]) if r.get("ajuste") else ""}">'
                       f'<figcaption><b>{i + 1}</b>{r["legenda"]}</figcaption></figure>' for i, r in enumerate(rec))
        li = "".join(f"<li>{p}</li>" for p in s["principios"])
        blocos.append(f"""<section><div class="cab"><span class="let">{s['letra']}</span><div><h2>{s['nome']}</h2>
<p class="url">{s.get('url', '')} · {s.get('tokens', '')}</p></div></div>
<div class="figs" style="grid-template-columns:{cols}">{figs}</div>
<div class="rodape"><div class="pr"><p class="rot">PRINCÍPIO (o que modelar)</p><ul>{li}</ul></div>
<div class="nao"><p class="rot">O QUE NÃO REPETIR</p><p>{s['nao']}</p></div></div></section>""")
    html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{_fontes_base()}{CSS_FOLHA}</style></head><body>"
            f"<header><h1>{spec['titulo']}</h1><p>{spec.get('subtitulo', '')}</p></header>{''.join(blocos)}</body></html>")
    _png(html, out)


TIT = "A BLACK QUE SÓ SE REVELA AO VIVO"
MIX = "3 noites · 20h30 · Bolsas de 36%"
TEST = "Il1 O0 rn m · ÃÕÇ ãõç · R$ 1.191,00 · WhatsApp (11) 98765-4321"
PAR = ("Cadastre-se e entre no grupo do WhatsApp. O preço só aparece ao vivo, às 20h30, "
       "e as vagas com bônus são limitadas para quem estiver dentro.")


def fontes(spec, out):
    """spec = {"titulo", "texto_titulo"?, "texto_mix"?, "paragrafo"?, "grupos": [{"nome","sub","modo": cond|larga|texto,
    "fontes": [{"nome", "familia" (Google, p/ fonte_variavel) ou "arquivo", "css": "font-weight:800;font-stretch:75%", "nota"}]}]}
    Fontes que faltam: python <brand-studio>/scripts/fonts.py get "Família:peso"."""
    from palco import data_url, fonte_variavel
    tit, mix, par = spec.get("texto_titulo", TIT), spec.get("texto_mix", MIX), spec.get("paragrafo", PAR)
    ff, secs, k = [], [], 0
    for g in spec["grupos"]:
        cards = []
        for f in g["fontes"]:
            arq = f.get("arquivo") or fonte_variavel(f["familia"])
            if not arq or not os.path.exists(arq):
                print("FALTA a fonte:", f["nome"], "→ fonts.py get")
                continue
            ff.append(f"@font-face{{font-family:f{k};src:url({data_url(arq, 'font/ttf')});font-weight:100 1000;font-stretch:50% 200%}}")
            css = f.get("css", "font-weight:700")
            if g.get("modo") == "texto":
                corpo = (f'<p class="t2" style="font-family:f{k};font-weight:700">{mix}</p>'
                         f'<p class="par" style="font-family:f{k};{css}">{par}</p><p class="tst" style="font-family:f{k};{css}">{TEST}</p>')
            else:
                corpo = (f'<p class="t1" style="font-family:f{k};{css}">{tit}</p><p class="t2" style="font-family:f{k};{css}">{mix}</p>'
                         f'<p class="tst" style="font-family:f{k};{css}">{TEST}</p>')
            cards.append(f'<div class="card"><div class="cab"><b>{f["nome"]}</b><span>{f.get("nota", "")}</span></div>{corpo}</div>')
            k += 1
        secs.append(f'<section><h2>{g["nome"]} <small>{g.get("sub", "")}</small></h2><div class="grade">{"".join(cards)}</div></section>')
    css = """*{box-sizing:border-box;margin:0;padding:0}
body{width:2400px;background:#EDEAE3;color:#121212;font-family:V;padding:96px}
h1{font-weight:800;font-size:92px;letter-spacing:-0.025em;line-height:1;margin-bottom:64px}
section{margin-bottom:80px}
h2{font-weight:800;font-size:46px;letter-spacing:-0.02em;border-bottom:3px solid #121212;padding-bottom:18px;margin-bottom:28px}
h2 small{font:500 22px M;font-stretch:80%;color:#E8520A;margin-left:16px}
.grade{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.card{background:#141414;color:#F2EFE8;border-radius:22px;padding:30px 36px 32px;overflow:hidden}
.cab{display:flex;justify-content:space-between;align-items:baseline;gap:20px;margin-bottom:22px;border-bottom:1px solid #333;padding-bottom:14px}
.cab b{font:700 22px M;font-stretch:85%} .cab span{font:500 18px V;color:#9a968c;text-align:right}
.t1{font-size:74px;line-height:.98;white-space:nowrap} .t2{font-size:40px;line-height:1.15;margin-top:16px;color:#FF6A2A}
.par{font-size:24px;line-height:1.5;margin-top:14px;color:#E6E2D9} .tst{font-size:21px;line-height:1.4;margin-top:16px;color:#9a968c}"""
    js = """for (const e of document.querySelectorAll('.t1,.t2')) { const w = e.parentElement.clientWidth - 72;
      const fs = parseFloat(getComputedStyle(e).fontSize); e.style.width='max-content';
      if (e.scrollWidth > w || e.classList.contains('t1')) e.style.fontSize = Math.min(fs * 1.6, fs * w / e.scrollWidth) + 'px'; }"""
    html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{''.join(ff)}{_fontes_base()}{css}</style></head><body>"
            f"<h1>{spec.get('titulo', 'Amostras de fontes')}</h1>{''.join(secs)}</body></html>")
    _png(html, out, js=js)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("pdf"); a.add_argument("arquivos", nargs="+"); a.add_argument("-o", required=True)
    a = sub.add_parser("medir"); a.add_argument("url"); a.add_argument("-o", required=True)
    a.add_argument("--largura", type=int, default=1440); a.add_argument("--celular", action="store_true")
    a = sub.add_parser("folha"); a.add_argument("spec"); a.add_argument("-o", required=True)
    a = sub.add_parser("fontes"); a.add_argument("spec"); a.add_argument("-o", required=True)
    x = ap.parse_args()
    if x.cmd == "pdf":
        pdf([f for g in x.arquivos for f in (glob.glob(g) or [g])], x.o)
    elif x.cmd == "medir":
        medir(x.url, x.o, x.largura, x.celular)
    elif x.cmd == "folha":
        folha(json.load(open(x.spec, encoding="utf-8")), x.o)
    elif x.cmd == "fontes":
        fontes(json.load(open(x.spec, encoding="utf-8")), x.o)

# Exemplo de estudo.json para `folha`:
# {"titulo": "Estudo de 3 sites:<br>o que modelar", "subtitulo": "Medido no código real…", "pasta": "estudo/recortes",
#  "sites": [{"letra": "A", "nome": "GSA Studio", "url": "gsaweb.com.br", "tokens": "Cofo Peshka + Gilroy · #E8520A",
#             "recortes": [{"arquivo": "gsa-01-hero-moldura.jpg", "legenda": "Hero emoldurado…"},
#                          {"arquivo": "gsa-02-acordeao-sombra-dura.jpg", "legenda": "…", "ajuste": "contain;background:#F2F2F2"}],
#             "principios": ["…", "…"], "nao": "…"}]}
