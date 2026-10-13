"""Verificador de PÁGINA DE CAPTURA (contrato: references/paginas-de-captura.md §3–4).

  python check_pagina.py <index.html> [-o pasta] [--copy copy.json]

Renderiza em 360×740, 390×844 (celular), 390 com barra de rolagem de 15 px (janela estreita de desktop),
768×1024, 1024×768 e 1440×900 (Chrome/Playwright, barras de rolagem reais) e mede, por largura:
  - rolagem horizontal (scrollWidth > largura)         → erro
  - menor fonte renderizada de texto visível            → aviso < 14 px; corpo (p, li) < 16 px → erro
  - alvos de toque (a, button, input, summary) < 44 px  → aviso (48 recomendado)
  - rótulo de botão/CTA em 2+ linhas (medido nos retângulos do texto) → ERRO
  - PADRÃO DE DOBRA: a 1ª seção ([data-hero]) tem que preencher a tela (fim ≥ 96% da altura) → ERRO
  - margens ESQUERDA × DIREITA desiguais em qualquer bloco de coluna (1,5 px+) → aviso
  - CSS com 100vw em medida de layout (erra a barra de rolagem) → aviso
  - com movimento reduzido ligado: texto invisível ou cortado nas bordas → ERRO
  - imagens sem alt, links sem texto                    → aviso
  - texto proibido na página (notas de orientação, colchetes, "confirmar"…) → erro
  - pop-up: botão [data-open-modal] abre <dialog>, foco entra, ESC fecha → erro se falhar
  - DENSIDADE (regra: clean, respiro, 1 mensagem por tela): blocos por altura de tela (> 8 mobile,
    > 11 desktop), respiro vertical das seções (< 72/112 px), blocos colados (< 10 px) e telas com < 38% de área vazia
  - AUTOCRÍTICA DA 1ª TELA (descobrir sozinho, sem o cliente apontar): mais de 1 logo, texto repetido (trigramas),
    CTA principal fora da tela ou baixo demais, texto sobre foto, foto das pessoas pequena, logo depois do H1
  - ALINHAMENTO da 1ª tela (o 'quase': 1–14 px): bordas esquerda/direita/topo/base quase iguais, margens do cabeçalho ×
    conteúdo, topo/base das colunas texto × imagem, vãos verticais quase iguais
  - ESPAÇAMENTO da 1ª tela: margem lateral ≥ 20 px (mobile) / 40 px, nada a < 12 px do topo, vãos < 12 px, > 4 valores
    diferentes de vão
  - peso: soma dos arquivos referenciados (img/css/js/fonte) e do HTML
Saída: <pasta>/<largura>.png (página inteira), <largura>-dobra.png (1ª tela), _folha.jpg (4 larguras) e
_relatorio.json. Código de saída 1 se houver erro.
"""
import argparse
import json
import os
import re
import sys

VIEWS = [("360", 360, 740), ("390", 390, 844), ("390-barra", 390, 844), ("768", 768, 1024), ("1024", 1024, 768),
         ("1440", 1440, 900)]   # 390-barra = janela estreita de DESKTOP: barra de rolagem de 15 px (onde 100vw erra)
PROIBIDO = [r"\[", r"\]", r"confirmar", r"convenção", r"o que evitar", r"variações? de h1", r"teste a/b", r"hipótese",
            r"lorem", r"undefined", r"\bnull\b", r"garanta sua vaga", r"últimas vagas", r"desconto", r"segunda pós grátis"]

JS = r"""
() => {
  const out = {w: document.documentElement.clientWidth, sw: document.documentElement.scrollWidth, fontes: {}, pequenos: [],
               alvos: [], semAlt: 0, linksVazios: 0, texto: document.body.innerText};
  const vis = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0.05; };
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const n = walker.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || !vis(el) || el.closest('dialog:not([open])')) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    const tag = el.tagName.toLowerCase();
    if (fs < 14) out.pequenos.push({t: n.textContent.trim().slice(0, 40), fs, tag});
    if ((tag === 'p' || tag === 'li') && fs < 16) out.pequenos.push({t: n.textContent.trim().slice(0, 40), fs, tag, corpo: true});
  }
  document.querySelectorAll('a,button,input,select,summary,textarea').forEach(el => {
    if (!vis(el) || el.closest('dialog:not([open])')) return;
    const r = el.getBoundingClientRect();
    if (Math.min(r.width, r.height) < 44 && !(el.tagName === 'A' && el.closest('p,li') && r.height < 44))
      out.alvos.push({t: (el.innerText || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 30), w: Math.round(r.width), h: Math.round(r.height)});
    if (el.tagName === 'A' && !(el.innerText || '').trim() && !el.getAttribute('aria-label') && !el.querySelector('img[alt]')) out.linksVazios++;
  });
  out.ctaQuebra = [];
  document.querySelectorAll('[data-open-modal], [class*=btn], [class*=cta]').forEach(el => {
    if (!vis(el) || el.closest('dialog:not([open])')) return;
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const tops = new Set(); let n;
    while ((n = tw.nextNode())) {
      if (!n.textContent.trim()) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const q of rg.getClientRects()) if (q.width > 2) tops.add(Math.round(q.top / 6));
    }
    if (tops.size > 1 && (el.innerText || '').trim().length < 50)
      out.ctaQuebra.push({t: el.innerText.trim().slice(0, 40), linhas: tops.size});
  });
  document.querySelectorAll('img').forEach(i => { if (!i.hasAttribute('alt')) out.semAlt++; });
  // densidade: blocos de conteúdo por altura de tela; respiro vertical das seções
  const sel = 'h1,h2,h3,h4,h5,p,li,a.btn,button,img,summary,figure,dt,dd,[data-bloco]';
  const blocos = [];
  document.querySelectorAll(sel).forEach(el => {
    if (!vis(el) || el.closest('dialog')) return;
    if (el.tagName === 'LI' && el.querySelector('p,h1,h2,h3,h4')) return;
    const r = el.getBoundingClientRect();
    blocos.push({y: r.top + scrollY, h: r.height, x: r.left, w: r.width, tag: el.tagName.toLowerCase(),
                 t: (el.innerText || el.alt || '').trim().slice(0, 28)});
  });
  out.blocos = blocos;
  out.secoes = [...document.querySelectorAll('body > section, main > section, body > main > section, body > header, body > footer')]
    .filter(vis).map(s => { const cs = getComputedStyle(s); const r = s.getBoundingClientRect();
      return {id: s.id || s.className.toString().slice(0, 24) || s.tagName.toLowerCase(), top: parseFloat(cs.paddingTop),
              bottom: parseFloat(cs.paddingBottom), h: Math.round(r.height), y: Math.round(r.top + scrollY)}; });
  out.vh = innerHeight;
  // ---- DOBRA: tudo que aparece na primeira tela ----
  const VH = innerHeight, VW = innerWidth;
  const dobra = [];
  document.querySelectorAll('h1,h2,h3,p,span,small,a,button,li,img,svg,picture,time,div').forEach(el => {
    if (!vis(el) || el.closest('dialog')) return;
    const r = el.getBoundingClientRect();
    if (r.bottom <= 0 || r.top >= VH || r.right <= 0 || r.left >= VW) return;
    const tag = el.tagName.toLowerCase();
    const kids = [...el.children].filter(c => vis(c));
    let txt = '';
    if (tag === 'img') txt = (el.alt || '').trim();
    else if (kids.length === 0 || ['h1','h2','h3','p','a','button','li','span','small','time'].includes(tag)) txt = (el.innerText || '').trim();
    const eLogo = (tag === 'img' && /logo|tarja|rec|black.?friday|simbolo|símbolo/i.test((el.alt || '') + ' ' + (el.currentSrc || el.src || '')))
                  || el.hasAttribute('data-logo');   // logo em SVG inline: o componente <Logo> marca data-logo
    const eFoto = tag === 'img' && /trio|pessoa|prof|foto|pb|recorte/i.test((el.alt || '') + ' ' + (el.currentSrc || el.src || ''));
    if (tag === 'div' && !el.hasAttribute('data-bloco')) return;
    // a sombra dura de botão (ex.: 4px 4px 0) faz parte do botão visualmente: a borda direita medida inclui o deslocamento
    const sm = getComputedStyle(el).boxShadow.match(/(-?[0-9.]+)px\s+(-?[0-9.]+)px\s+0px/); const sdx = sm ? Math.max(0, parseFloat(sm[1])) : 0;
    dobra.push({tag, t: txt.slice(0, 90), x: r.left, y: r.top, w: r.width + sdx, h: r.height, b: r.bottom, logo: eLogo, foto: eFoto,
                cta: el.hasAttribute('data-open-modal'), sf: !!el.closest('[data-sobre-foto]'), hd: !!el.closest('header,[role=banner],.topo,.hdr,.bar'), fs: parseFloat(getComputedStyle(el).fontSize)});
  });
  out.dobra = dobra;
  // PADRÃO DE DOBRA: a 1ª seção (data-hero) tem que terminar no fundo da tela; a seguinte não pode aparecer
  const hero = document.querySelector('[data-hero]') || document.querySelector('main section');
  out.heroBottom = hero ? Math.round(hero.getBoundingClientRect().bottom) : null;
  return out;
}
"""


MARGENS_JS = r"""
() => {
  const cw = document.documentElement.clientWidth, out = [], vistos = new Set();
  document.querySelectorAll('main *, header *, section > *').forEach(e => {
    const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
    if (r.width < 0.62 * cw || r.width > 0.985 * cw || r.height < 12 || cs.display === 'none' || cs.visibility === 'hidden') return;
    // só caixas "de coluna" (imagem, cartão, botão, painel com fundo/borda); texto com max-width/ch é ragged por desenho
    const tag = e.tagName.toLowerCase();
    const temCaixa = cs.backgroundImage !== 'none' || (cs.backgroundColor && !/rgba\(0, 0, 0, 0\)|transparent/.test(cs.backgroundColor))
                     || parseFloat(cs.borderTopWidth) + parseFloat(cs.borderLeftWidth) > 0;
    if (!(['img', 'picture', 'figure', 'article', 'button', 'video', 'canvas'].includes(tag) || (['a', 'div', 'section', 'li'].includes(tag) && temCaixa))) return;
    if (e.closest('[data-sobre-foto],[aria-hidden=true],dialog,[class*=marquee]')) return;
    let sdx = 0; const sm = cs.boxShadow.match(/(-?[0-9.]+)px\s+(-?[0-9.]+)px\s+0px/); if (sm) sdx = Math.max(0, parseFloat(sm[1]));
    const L = r.left, R = cw - r.right - sdx;
    if (L < 6 || R < 6) return;   // sangria/encosta na borda: decisão, não margem
    if (Math.abs(L - R) > 1.5 && Math.abs(L - R) < cw * 0.2) {
      const k = Math.round(L) + '|' + Math.round(R);
      if (vistos.has(k)) return; vistos.add(k);
      out.push({t: (e.tagName.toLowerCase() + '.' + (e.className.toString().split(' ')[0] || '')).slice(0, 30), L: Math.round(L * 10) / 10,
                R: Math.round(R * 10) / 10, y: Math.round(r.top + scrollY)});
    }
  });
  return out;
}
"""

REDUZIDO_JS = r"""
() => {
  const out = {escondido: [], cortado: []};
  document.querySelectorAll('h1,h2,h3,p,li,button,a,span,div').forEach(e => {
    const t = (e.childNodes.length && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) ? e.innerText.trim() : '';
    if (!t || e.closest('dialog:not([open])')) return;
    const cs = getComputedStyle(e), r = e.getBoundingClientRect();
    if (r.width < 4) return;
    let op = 1, n = e; while (n && n !== document.body) { op *= +getComputedStyle(n).opacity; n = n.parentElement; }
    if (op < 0.1 && cs.visibility !== 'hidden' && cs.display !== 'none') out.escondido.push(t.slice(0, 30));
    const ox = cs.overflowX;
    if ((ox === 'clip' || ox === 'hidden') && e.scrollWidth > e.clientWidth + 3 && e.clientWidth > 40)
      out.cortado.push(t.slice(0, 30) + ' (' + e.scrollWidth + '>' + e.clientWidth + ')');
  });
  return out;
}
"""


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # --help e acentos no console cp1252 do Windows
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("-o", default=None)
    ap.add_argument("--copy", default=None, help="copy.json: palavras que NÃO estão na copy final são listadas")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    from playwright.sync_api import sync_playwright
    from PIL import Image
    if a.html.startswith(("http://", "https://")):
        url = a.html
        html = None
        out = a.o or os.path.join(os.environ.get("TEMP", "."), "_check_pagina")
    else:
        html = os.path.abspath(a.html)
        out = a.o or os.path.join(os.path.dirname(html), "_check")
        url = "file:///" + html.replace("\\", "/")
    os.makedirs(out, exist_ok=True)
    rel = {"arquivo": html or url, "larguras": {}, "erros": [], "avisos": []}
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", args=["--allow-file-access-from-files"],
                              ignore_default_args=["--hide-scrollbars"])   # barras de rolagem reais, como no Windows
        for nome, w, h in VIEWS:
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                is_mobile=(w < 700 and "barra" not in nome), has_touch=(w < 1100 and "barra" not in nome))
            pg = ctx.new_page()
            css_txt = []
            pg.on("response", lambda r_, L=css_txt: L.append(r_) if "css" in (r_.headers.get("content-type", "")) else None)
            erros_js = []
            pg.on("pageerror", lambda e, L=erros_js: L.append(str(e)))
            pg.on("console", lambda m, L=erros_js: L.append(m.text) if m.type == "error" else None)
            pg.goto(url)
            pg.wait_for_load_state("networkidle")
            pg.wait_for_timeout(700)
            # rola a página inteira para disparar animações de entrada / lazy-load
            H = pg.evaluate("document.documentElement.scrollHeight")
            y = 0
            while y < H:
                pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(120); y += h // 2
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
            # revelações ligadas à rolagem (CSS view()) deixam o que está abaixo da dobra invisível na captura de
            # página inteira: desliga só para a medida/captura (o que o visitante vê rolando não muda)
            pg.add_style_tag(content="[class*=reveal]{animation:none!important;opacity:1!important;transform:none!important}")
            m = pg.evaluate(JS)
            pg.screenshot(path=os.path.join(out, f"{nome}-dobra.png"))
            pg.screenshot(path=os.path.join(out, f"{nome}.png"), full_page=True)
            # --- MARGENS ESQUERDA × DIREITA em toda a página (não só na dobra): "um lado maior que o outro"
            pg.wait_for_timeout(700)   # depois da captura de página inteira o viewport volta ao normal: esperar antes de medir
            sim = pg.evaluate(MARGENS_JS)
            for q in sim[:4]:
                rel["avisos"].append(f"{nome}: margens desiguais «{q['t']}» esquerda {q['L']} × direita {q['R']} px (y={q['y']})")
            # CSS que mede pela janela inteira (100vw inclui a barra de rolagem: 15 px a mais no Windows)
            if nome == VIEWS[0][0]:
                vw_uso = []
                for resp in css_txt:
                    try:
                        txt = resp.text()
                    except Exception:
                        continue
                    for mm in re.finditer(r"[^;{}]*(?<![-\w])100d?vw[^;{}]*", txt):
                        trecho = mm.group(0).strip()
                        if re.search(r"(inset|left|right)\s*:[^;]*-100d?vw", trecho) and "calc" not in trecho:
                            continue   # sangria de fundo (esticar para fora): inofensivo
                        vw_uso.append(trecho[:90])
                for t in vw_uso[:6]:
                    rel["avisos"].append(f"CSS usa 100vw em medida de layout (erra 15 px com barra de rolagem; usar % ou cqw): {t}")
            r = {"altura": H, "scrollWidth": m["sw"], "pequenos": m["pequenos"][:12], "alvos_pequenos": m["alvos"][:12],
                 "imagens_sem_alt": m["semAlt"], "links_vazios": m["linksVazios"], "erros_js": erros_js[:5]}
            if m["sw"] > m["w"] + 1:
                rel["erros"].append(f"{nome}: rolagem horizontal ({m['sw']} > {m['w']})")
            for q in m["pequenos"]:
                (rel["erros"] if q.get("corpo") else rel["avisos"]).append(f"{nome}: fonte {q['fs']:.0f}px em <{q['tag']}> «{q['t']}»")
            if m.get("heroBottom") is not None and m["heroBottom"] < 0.96 * m["vh"]:
                rel["erros"].append(f"{nome}: dobra 1 CURTA: a 1ª seção termina em y={m['heroBottom']} de {m['vh']} px "
                                    f"(deve preencher a tela; a seção seguinte não pode aparecer na 1ª tela)")
            for q in m["alvos"][:6]:
                rel["avisos"].append(f"{nome}: alvo de toque {q['w']}×{q['h']} «{q['t']}»")
            for q in m.get("ctaQuebra", [])[:4]:
                rel["erros"].append(f"{nome}: rótulo do botão em {q['linhas']} linhas «{q['t']}» (CTA sempre em 1 linha: reduzir padding/corpo ou alargar)")
            # --- densidade (regra: nada de muita coisa junta; simplificar e dar respiro)
            mob = w < 700
            vh = m["vh"]
            fat = {}
            for bl in m["blocos"]:
                fat[int(bl["y"] // vh)] = fat.get(int(bl["y"] // vh), 0) + 1
            lim = 8 if mob else 11
            cheias = {k: v for k, v in fat.items() if v > lim}
            for k, v in sorted(cheias.items()):
                rel["avisos"].append(f"{nome}: tela {k + 1} com {v} blocos de conteúdo (> {lim}): simplificar / dividir")
            r["blocos_por_tela_max"] = max(fat.values()) if fat else 0
            minpad = 72 if mob else 112
            for sc in m["secoes"]:
                if sc.get("id") and sc["id"] in ("hero", "topo") and m.get("heroBottom") is not None and m["heroBottom"] >= 0.96 * vh:
                    continue   # 1ª dobra que preenche a tela: o respiro vem do centramento na altura (padrão de dobra)
                if sc["h"] > 300 and (sc["top"] < minpad or sc["bottom"] < minpad):
                    rel["avisos"].append(f"{nome}: seção «{sc['id']}» com respiro {sc['top']:.0f}/{sc['bottom']:.0f} px (< {minpad})")
            bs = sorted(m["blocos"], key=lambda b: b["y"])
            apertos = 0
            for a_, b_ in zip(bs, bs[1:]):
                gap = b_["y"] - (a_["y"] + a_["h"])
                lado = a_["x"] < b_["x"] + b_["w"] and b_["x"] < a_["x"] + a_["w"]
                if lado and 0 <= gap < 10 and a_["tag"] not in ("li", "dt", "dd") and b_["tag"] not in ("li", "dt", "dd"):
                    apertos += 1
                    if apertos <= 3:
                        rel["avisos"].append(f"{nome}: blocos colados ({gap:.0f} px) «{a_['t']}» / «{b_['t']}»")
            r["secoes"] = [(sc["id"], sc["top"], sc["bottom"]) for sc in m["secoes"]][:14]
            # área vazia por tela (fração de pixels ≈ cor de fundo dominante)
            try:
                import numpy as np
                im = Image.open(os.path.join(out, f"{nome}.png")).convert("RGB")
                arr = np.asarray(im)
                vazias = []
                for k in range(0, arr.shape[0], vh):
                    fat_ = arr[k:k + vh:2, ::2, :].reshape(-1, 3)
                    if len(fat_) < 1000:
                        continue
                    q = (fat_ // 8).astype(np.int32)
                    key = q[:, 0] * 1024 + q[:, 1] * 32 + q[:, 2]
                    vals, cnt = np.unique(key, return_counts=True)
                    dom = vals[cnt.argmax()]
                    d = np.abs(fat_.astype(np.int16) - np.array([(dom // 1024) * 8, ((dom // 32) % 32) * 8, (dom % 32) * 8])).max(axis=1)
                    vazias.append(float((d <= 14).mean()))
                r["vazio_por_tela"] = [round(v, 2) for v in vazias]
                cheia = [i + 1 for i, v in enumerate(vazias) if v < 0.38]
                if cheia:
                    rel["avisos"].append(f"{nome}: telas com pouca área vazia (< 38%): {cheia[:8]} — dar respiro")
            except Exception as e:  # noqa: BLE001
                r["vazio_por_tela"] = f"n/d ({e})"
            # --- AUTOCRÍTICA DA DOBRA (descobrir sozinho: repetição, logo duplicada, CTA fora da tela, sobreposição)
            db = m.get("dobra", [])
            vh_ = m["vh"]
            logos = [d for d in db if d["logo"] and d["w"] > 20]
            if len(logos) > 1:
                rel["avisos"].append(f"{nome}: {len(logos)} logos na 1ª tela (deve haver UMA): " +
                                     " | ".join(f"({d['x']:.0f},{d['y']:.0f}) {d['w']:.0f}×{d['h']:.0f}" for d in logos[:4]))
            def norm(t):
                return re.sub(r"[^a-z0-9áàâãéêíóôõúç ]", " ", t.lower())
            frases = [(norm(d["t"]).split(), d) for d in db if d["t"] and d["tag"] not in ("a", "button") or (d["t"] and d["tag"] in ("a", "button") and len(d["t"]) > 40)]
            visto = {}
            for ws, d in frases:
                for k in range(0, max(0, len(ws) - 2)):
                    tri = " ".join(ws[k:k + 3])
                    if len(tri) < 11:
                        continue
                    visto.setdefault(tri, set()).add((round(d["x"]), round(d["y"])))
            rep = [t for t, pos in visto.items() if len(pos) > 1]
            if rep:
                rel["avisos"].append(f"{nome}: texto repetido na 1ª tela: " + "; ".join(f"«{t}»" for t in rep[:4]))
            ctas = [d for d in db if d["cta"]]
            todos_cta = pg.evaluate("[...document.querySelectorAll('[data-open-modal]')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0}).map(e=>e.getBoundingClientRect().bottom)")
            if not ctas:
                rel["erros"].append(f"{nome}: nenhum CTA (data-open-modal) visível na 1ª tela")
            else:
                prim = max(ctas, key=lambda d: d["w"] * d["h"])
                lim = 0.82 * vh_ if mob else 0.92 * vh_
                if prim["b"] > lim:
                    rel["avisos"].append(f"{nome}: CTA principal termina em y={prim['b']:.0f} (> {lim:.0f}): subir ou enxugar a dobra")
            # sobreposição entre blocos de texto e imagens/fotos
            textos = [d for d in db if d["t"] and not d.get("sf") and d["tag"] in ("h1", "h2", "p", "span", "small", "li", "time")]
            fotos = [d for d in db if d["foto"]]
            for t_ in textos[:40]:
                for f_ in fotos:
                    ix = min(t_["x"] + t_["w"], f_["x"] + f_["w"]) - max(t_["x"], f_["x"])
                    iy = min(t_["y"] + t_["h"], f_["y"] + f_["h"]) - max(t_["y"], f_["y"])
                    if ix > 12 and iy > 12 and t_["w"] < f_["w"] * 0.9:
                        rel["avisos"].append(f"{nome}: texto «{t_['t'][:28]}» sobre a foto ({ix:.0f}×{iy:.0f} px)")
                        break
            # tamanho da foto das pessoas na dobra (rosto legível?)
            if fotos:
                maior = max(fotos, key=lambda d: d["w"] * d["h"])
                r["foto_dobra"] = {"w": round(maior["w"]), "h": round(maior["h"]), "frac_altura": round(maior["h"] / vh_, 2)}
                if maior["h"] < 0.20 * vh_:
                    rel["avisos"].append(f"{nome}: foto das pessoas muito pequena na 1ª tela ({maior['h']:.0f}px = {maior['h'] / vh_:.0%} da altura)")
            else:
                rel["avisos"].append(f"{nome}: nenhuma foto de pessoas detectada na 1ª tela (nome do arquivo/alt sem 'foto|prof|recorte|trio')")
            # ordem de leitura: a logo deve vir antes do H1, e o H1 antes do CTA
            h1 = [d for d in db if d["tag"] == "h1"]
            if h1 and logos:
                if min(l["y"] for l in logos) > h1[0]["y"]:
                    rel["avisos"].append(f"{nome}: a logo vem DEPOIS do H1 na ordem de leitura")
            # --- ALINHAMENTO (o "quase": 1–14 px de diferença é erro; igual ou claramente diferente é decisão)
            VW_ = m["w"]
            leaf = [d for d in db if d["w"] > 24 and d["h"] > 8 and d["w"] < 0.97 * VW_
                    and (d["logo"] or d["foto"] or d["cta"] or d["tag"] in ("h1", "h2", "p", "time", "button", "img"))]
            def quase(chave, nome_borda, tol=14.0, minimo=1.5):
                vals = sorted((((d[chave] if chave != "r" else d["x"] + d["w"]) if chave != "b" else d["y"] + d["h"], d) for d in leaf), key=lambda t: t[0])
                grupos, atual = [], []
                for v, d in vals:
                    if atual and v - atual[-1][0] > tol:
                        grupos.append(atual); atual = []
                    atual.append((v, d))
                grupos.append(atual)
                for g in grupos:
                    if len(g) < 2:
                        continue
                    vs = [v for v, _ in g]
                    spread = max(vs) - min(vs)
                    if minimo <= spread <= tol:
                        nomes = " | ".join(f"«{(d['t'] or d['tag'])[:16]}»{v:.0f}" for v, d in g[:4])
                        rel["avisos"].append(f"{nome}: quase alinhado ({nome_borda}, {spread:.0f} px): {nomes}")
            for chave, nb in (("x", "esquerda"), ("r", "direita")):
                quase(chave, nb)
            if not mob:
                quase("y", "topo", tol=10.0)
                quase("b", "base", tol=10.0)
            # cabeçalho × conteúdo: mesma margem esquerda e direita
            hdr = [d for d in db if d.get("hd") and d["w"] > 20 and d["w"] < 0.97 * VW_]
            cont = [d for d in db if not d.get("hd") and d["w"] > 24 and d["w"] < 0.97 * VW_ and (d["foto"] or d["tag"] in ("h1", "p", "img", "a", "button"))]
            if hdr and cont:
                hl, hr = min(d["x"] for d in hdr), max(d["x"] + d["w"] for d in hdr)
                cl, cr = min(d["x"] for d in cont), max(d["x"] + d["w"] for d in cont)
                for lado, a_, b_ in (("esquerda", hl, cl), ("direita", hr, cr)):
                    if abs(a_ - b_) > 2:
                        rel["avisos"].append(f"{nome}: cabeçalho e conteúdo com margens diferentes na {lado} ({a_:.0f} × {b_:.0f} px): usar o mesmo container")
            # colunas lado a lado (desktop): topo e base do bloco de texto × bloco de imagem
            if not mob:
                esq = [d for d in leaf if not d.get("hd") and d["x"] + d["w"] / 2 < VW_ * 0.5]
                dirr = [d for d in leaf if not d.get("hd") and d["x"] + d["w"] / 2 >= VW_ * 0.5 and (d["foto"] or d["tag"] == "img")]
                if esq and dirr:
                    et, eb = min(d["y"] for d in esq), max(d["y"] + d["h"] for d in esq)
                    dt, dbm = min(d["y"] for d in dirr), max(d["y"] + d["h"] for d in dirr)
                    if abs(et - dt) > 6:
                        rel["avisos"].append(f"{nome}: topo das colunas desalinhado (texto {et:.0f} × imagem {dt:.0f}, {abs(et - dt):.0f} px)")
                    if abs(eb - dbm) > 6 and abs(eb - dbm) < 160:
                        rel["avisos"].append(f"{nome}: base das colunas desalinhada (texto {eb:.0f} × imagem {dbm:.0f}, {abs(eb - dbm):.0f} px)")
            # ritmo vertical: vãos "quase iguais" na mesma coluna
            col = sorted([d for d in db if not d.get("hd") and d["w"] > 24 and d["tag"] in ("h1", "p", "time", "button", "a", "img") and d["w"] < 0.97 * VW_ and d["x"] < VW_ * 0.5], key=lambda d: d["y"])
            gaps = [(col[i + 1]["y"] - (col[i]["y"] + col[i]["h"])) for i in range(len(col) - 1)]
            gaps = [g for g in gaps if g >= 6]
            for i in range(len(gaps)):
                for j in range(i + 1, len(gaps)):
                    if 2 <= abs(gaps[i] - gaps[j]) <= 8 and gaps[i] > 12:
                        rel["avisos"].append(f"{nome}: vãos verticais quase iguais ({gaps[i]:.0f} × {gaps[j]:.0f} px): igualar")
                        break
                else:
                    continue
                break
            # --- ESPAÇAMENTO do sistema de design: margens laterais, folga do topo/base, vãos, conjunto de valores
            lado_min = 20 if mob else 40
            for d in db:
                if d["w"] < 0.97 * VW_ and d["w"] > 24 and d["tag"] in ("h1", "h2", "p", "time", "button", "a", "img", "li", "span", "small") and not d.get("bg"):
                    if d["x"] < lado_min - 0.5 or d["x"] + d["w"] > VW_ - lado_min + 0.5:
                        lado = "esquerda" if d["x"] < lado_min - 0.5 else "direita"
                        dist = d["x"] if lado == "esquerda" else VW_ - d["x"] - d["w"]
                        rel["avisos"].append(f"{nome}: «{(d['t'] or d['tag'])[:22]}» a {dist:.0f} px da borda {lado} (mín. {lado_min}): margem lateral")
                        break
            topo_ = [d for d in db if d["w"] > 24 and d["w"] < 0.97 * VW_ and d["y"] < 12 and d["tag"] not in ("div",)]
            if topo_ and not any(d.get("hd") for d in topo_):
                d = min(topo_, key=lambda t: t["y"])
                rel["avisos"].append(f"{nome}: «{(d['t'] or d['tag'])[:22]}» a {d['y']:.0f} px do topo da tela")
            # vãos entre blocos consecutivos (qualquer coluna): < 12 px = comprimido; conjunto de valores ≤ 3
            seq = sorted([d for d in db if d["w"] > 24 and d["h"] > 8 and d["w"] < 0.97 * VW_ and d["tag"] in ("h1", "h2", "p", "time", "button", "a", "img", "li")], key=lambda d: d["y"])
            vaos = []
            for a_, b_ in zip(seq, seq[1:]):
                if a_["x"] < b_["x"] + b_["w"] and b_["x"] < a_["x"] + a_["w"]:
                    gv = b_["y"] - (a_["y"] + a_["h"])
                    if 0 <= gv < 160:
                        vaos.append(round(gv))
            apert = [g for g in vaos if g < 12]
            if apert:
                rel["avisos"].append(f"{nome}: {len(apert)} vão(s) < 12 px entre blocos da 1ª tela (comprimido; mín. 12 no mesmo grupo, 24 entre grupos)")
            distintos = []
            for g in sorted(vaos):
                if g >= 12 and (not distintos or g - distintos[-1] > 4):
                    distintos.append(g)
            if len(distintos) > 4:
                rel["avisos"].append(f"{nome}: {len(distintos)} valores de vão diferentes na 1ª tela ({distintos}): usar 3 (12 · 24 · 40)")
            r["vaos_dobra"] = distintos
            r["dobra_blocos"] = len(db)
            if m["semAlt"]:
                rel["avisos"].append(f"{nome}: {m['semAlt']} imagem(ns) sem alt")
            if m["linksVazios"]:
                rel["avisos"].append(f"{nome}: {m['linksVazios']} link(s) sem texto")
            for e in erros_js[:3]:
                rel["erros"].append(f"{nome}: erro de console/JS: {e[:120]}")
            if nome in ("390", "1440"):
                low = m["texto"].lower()
                for pat in PROIBIDO:
                    mm = re.search(pat, low)
                    if mm:
                        rel["erros"].append(f"{nome}: texto proibido na página: «{low[max(0, mm.start() - 25):mm.end() + 25].strip()}»")
                # pop-up
                try:
                    gat = pg.locator("[data-open-modal]").first
                    gat.scroll_into_view_if_needed()
                    gat.click()
                    pg.wait_for_timeout(350)
                    aberto = pg.evaluate("!!document.querySelector('dialog[open]')")
                    foco = pg.evaluate("!!document.activeElement && !!document.activeElement.closest('dialog')")
                    pg.screenshot(path=os.path.join(out, f"{nome}-modal.png"))
                    pg.keyboard.press("Escape"); pg.wait_for_timeout(250)
                    fechou = pg.evaluate("!document.querySelector('dialog[open]')")
                    r["modal"] = {"abriu": aberto, "foco_dentro": foco, "esc_fecha": fechou}
                    if not aberto:
                        rel["erros"].append(f"{nome}: o botão [data-open-modal] não abre o <dialog>")
                    elif not foco:
                        rel["avisos"].append(f"{nome}: foco não entra no pop-up")
                    if aberto and not fechou:
                        rel["erros"].append(f"{nome}: ESC não fecha o pop-up")
                except Exception as e:  # noqa: BLE001
                    rel["erros"].append(f"{nome}: pop-up não testável ({str(e)[:80]})")
            rel["larguras"][nome] = r
            ctx.close()
        # --- movimento reduzido ligado no sistema (muita gente tem sem saber): nada some, nada fica cortado, faixa legível
        for nome, w, h in (("390", 390, 844), ("1440", 1440, 900)):
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="reduce")
            pg = ctx.new_page()
            pg.goto(url)
            pg.wait_for_load_state("networkidle")
            pg.wait_for_timeout(800)
            H2 = pg.evaluate("document.documentElement.scrollHeight")
            y = 0
            while y < H2:
                pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(60); y += h // 2
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
            red = pg.evaluate(REDUZIDO_JS)
            if red["escondido"]:
                rel["erros"].append(f"{nome} (movimento reduzido): texto invisível «{red['escondido'][0]}» (+{len(red['escondido']) - 1})")
            if red["cortado"]:
                rel["erros"].append(f"{nome} (movimento reduzido): texto cortado nas bordas «{red['cortado'][0]}»")
            pg.screenshot(path=os.path.join(out, f"{nome}-reduzido.png"), full_page=True)
            ctx.close()
        b.close()
    # peso
    if html is None:
        import urllib.request
        data = urllib.request.urlopen(url).read()
        base = None
        src = data.decode('utf-8', 'replace')
        tot = len(data)
    else:
        base = os.path.dirname(html)
        src = open(html, encoding="utf-8").read()
        tot = os.path.getsize(html)
    refs = set(re.findall(r'(?:src|href)="([^":#?]+\.(?:webp|jpg|jpeg|png|svg|css|js|woff2?|ttf))"', src))
    for rf in refs:
        if base is None:
            try:
                import urllib.parse
                tot += len(urllib.request.urlopen(urllib.parse.urljoin(url, rf)).read())
            except Exception:
                pass
            continue
        f = os.path.normpath(os.path.join(base, rf))
        if os.path.exists(f):
            tot += os.path.getsize(f)
    rel["peso_kb"] = round(tot / 1024)
    if tot > 1_800_000:
        rel["avisos"].append(f"peso total {tot // 1024} KB (> 1800 KB)")
    # folha das 4 larguras
    ims = [Image.open(os.path.join(out, f"{n}-dobra.png")).convert("RGB") for n, _, _ in VIEWS]
    hh = 760
    ims = [im.resize((round(im.width * hh / im.height), hh)) for im in ims]
    sheet = Image.new("RGB", (sum(i.width for i in ims) + 30 * (len(ims) + 1), hh + 60), "#222")
    x = 30
    for im in ims:
        sheet.paste(im, (x, 30)); x += im.width + 30
    sheet.save(os.path.join(out, "_folha.jpg"), quality=88)
    json.dump(rel, open(os.path.join(out, "_relatorio.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ERROS:", len(rel["erros"]), "· AVISOS:", len(rel["avisos"]), "· peso:", rel["peso_kb"], "KB")
    for e in rel["erros"]:
        print("  ERRO", e)
    for w in rel["avisos"][:25]:
        print("  aviso", w)
    print("→", out)
    sys.exit(1 if rel["erros"] else 0)


if __name__ == "__main__":
    main()
