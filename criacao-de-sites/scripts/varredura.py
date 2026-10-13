"""varredura.py — checagem NUMÉRICA do que o verificador de layout não pega (rodar antes de olhar).

  python varredura.py <url-base> --rotas /v1/ /solo/x/ [--temas escuro,claro] [--larguras 1440x900,1280x720,390x844]
        [--matiz-proibido 34-52] [--rotas-sem-regra /v1/]

Por rota × tema × largura mede: (1) cor com MATIZ proibido (padrão 34–52° = dourado) em color/background/borda/
sublinhado/fill/stroke de elementos visíveis; (2) rolagem horizontal; (3) botão principal (#cta-hero ou .sf__cta .est-btn)
fora da dobra; (4) SVG/imagem em uso com cor assada proibida (ex.: a cor reservada à marca-mãe). Saída: lista dos que
falham e código de saída 1 se houver. Rolar a página antes de medir (reveal) já está incluído.
Origem: "cor da marca-mãe só na página-mãe" e dobra fora da tela custaram 3 rodadas de correção porque só o olho pegava.
"""
import argparse, json, re, sys

JS = """([lo, hi]) => {
  const out = {gold: [], sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth};
  const parse = (c) => { const m = c.match(/rgba?\\(([^)]+)\\)/); if (!m) return null; const p = m[1].split(/[ ,\\/]+/).map(Number); return {r:p[0], g:p[1], b:p[2], a: p.length > 3 ? p[3] : 1}; };
  const hsl = (r,g,b) => { r/=255; g/=255; b/=255; const mx=Math.max(r,g,b), mn=Math.min(r,g,b), l=(mx+mn)/2; let h=0, s=0;
    if (mx!==mn) { const d=mx-mn; s = l>.5 ? d/(2-mx-mn) : d/(mx+mn); if (mx===r) h=((g-b)/d+(g<b?6:0)); else if (mx===g) h=(b-r)/d+2; else h=(r-g)/d+4; h*=60; } return {h,s,l}; };
  const bad = (c) => { const p = parse(c); if (!p || p.a < 0.2) return false; const x = hsl(p.r,p.g,p.b); return x.h>=lo && x.h<=hi && x.s>=0.35 && x.l>=0.12 && x.l<=0.8; };
  const seen = new Set();
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el); if (cs.display==='none' || cs.visibility==='hidden') continue;
    const r = el.getBoundingClientRect(); if (r.width<2 || r.height<2) continue;
    const props = [['color', cs.color], ['background-color', cs.backgroundColor],
      ['border-top-color', cs.borderTopWidth!=='0px'?cs.borderTopColor:''], ['border-left-color', cs.borderLeftWidth!=='0px'?cs.borderLeftColor:''],
      ['text-decoration-color', cs.textDecorationLine!=='none'?cs.textDecorationColor:''],
      ['fill', el instanceof SVGElement ? cs.fill : ''], ['stroke', el instanceof SVGElement ? cs.stroke : '']];
    for (const [k,v] of props) if (v && bad(v)) { const id = el.tagName.toLowerCase()+'.'+String(el.className?.baseVal ?? el.className).split(' ').slice(0,2).join('.')+' '+k+' '+v;
      if (!seen.has(id)) { seen.add(id); out.gold.push(id + ' "' + (el.textContent||'').trim().slice(0,24) + '"'); } }
  }
  const cta = document.querySelector('#cta-hero, .sf__cta .est-btn, [data-hero] .est-btn'); out.cta = cta ? Math.round(cta.getBoundingClientRect().bottom) : null; out.vh = innerHeight;
  return out; }"""

JS_SVG = """async (pat) => { const rx = new RegExp(pat, 'i'); const urls = new Set();
  for (const el of document.querySelectorAll('img')) if (el.currentSrc && /svg/.test(el.currentSrc)) urls.add(el.currentSrc);
  const bad = []; for (const u of urls) { try { const t = await (await fetch(u)).text(); if (rx.test(t)) bad.push(u.split('/').slice(-2).join('/')); } catch (e) {} }
  return bad; }"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base"); ap.add_argument("--rotas", nargs="+", required=True)
    ap.add_argument("--temas", default="escuro,claro"); ap.add_argument("--larguras", default="1440x900,1280x720,390x844")
    ap.add_argument("--matiz-proibido", default="34-52"); ap.add_argument("--sem-regra", nargs="*", default=[])
    ap.add_argument("--svg-proibido", default="", help="regex de HEX proibidos em SVG, ex.: \"c9a45c|7c5f1c\" (vazio = não checa)")
    a = ap.parse_args()
    a.rotas = ["/" + r.strip("/") + "/" if r.strip("/") else "/" for r in a.rotas]   # aceita "solo/x/v1" (Git Bash estraga "/solo")
    lo, hi = (float(x) for x in a.matiz_proibido.split("-"))
    from playwright.sync_api import sync_playwright
    falhas = 0
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome", ignore_default_args=["--hide-scrollbars"])
        for rota in a.rotas:
            for tema in a.temas.split(","):
                for lw in a.larguras.split(","):
                    w, h = (int(x) for x in lw.split("x"))
                    ctx = br.new_context(viewport={"width": w, "height": h}, is_mobile=w < 700, has_touch=w < 700)
                    pg = ctx.new_page()
                    pg.goto(a.base.rstrip("/") + rota + ("?tema=claro" if tema == "claro" else ""), wait_until="networkidle")
                    pg.wait_for_timeout(1500)
                    H = pg.evaluate("document.documentElement.scrollHeight"); y = 0
                    while y < H:
                        pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(80); y += 700
                    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
                    r = pg.evaluate(JS, [lo, hi])
                    probs = []
                    if r["sw"] > r["cw"]:
                        probs.append(f"transbordo {r['sw']}>{r['cw']}")
                    if r["cta"] and r["cta"] > r["vh"]:
                        probs.append(f"botão fora da dobra {r['cta']}>{r['vh']}")
                    if rota not in a.sem_regra:
                        if r["gold"]:
                            probs.append(f"cor proibida x{len(r['gold'])}: " + " | ".join(r["gold"][:3]))
                        svgs = pg.evaluate(JS_SVG, a.svg_proibido) if a.svg_proibido else []
                        if svgs:
                            probs.append("svg com cor proibida: " + ", ".join(svgs[:3]))
                    if probs:
                        falhas += 1; print(f"{rota} {tema} {lw} -> " + "; ".join(probs))
                    ctx.close()
        br.close()
    print("falhas:", falhas)
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
