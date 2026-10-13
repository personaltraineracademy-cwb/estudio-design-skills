#!/usr/bin/env python
"""teste_pagina_total.py — bateria COMPLETA de uma página web (captura/landing) no navegador real.

Complementa `check_pagina.py` (contrato de design). Aqui: o que quebra em produção.
Roda no Chrome com BARRA DE ROLAGEM real (como no Windows) e mede, por largura e por modo de movimento:

  LAYOUT (18 larguras 320–2560 + 4 paisagens de celular)
    · rolagem horizontal · elemento/texto fora da tela · texto cortado por overflow · sobreposição de blocos de texto
    · margens esquerda × direita desiguais · fonte < 14 · alvo de toque < 44 · imagem quebrada ou ampliada (borrada)
    · h1 único · linha com > 90 caracteres · contraste de texto sobre fundo sólido (WCAG)
  INTERAÇÃO (celular, 360, 768 e 1440)
    · pop-up: abre por todos os CTAs, foco entra, Tab não escapa, ESC fecha e devolve o foco, clique no fundo fecha,
      envio vazio / telefone inválido mostram erro, envio válido mostra sucesso, rolagem do fundo travada e liberada,
      cabe na altura da tela
    · foco visível em todos os controles (primeiros 30 da ordem do Tab)
  RELÓGIO: 5 estados por ?agora=…, sem NaN / "00 dias", sem salto de altura entre estados
  MOVIMENTO: modos total / suave / parado (?movimento=…): nº de animações, nada permanece invisível depois de rolar,
    faixa anda e pausa, CLS, LCP, tarefas longas, tempo de quadro na rolagem
  REDE/CONSOLE: erros, requisições ≥ 400

Uso:  python teste_pagina_total.py http://localhost:4173/v1/ -o PASTA [--rapido] [--agora ISO]
Saída: PASTA/_teste-total.json, PASTA/_teste-total.md e PNGs de cada largura. Código 1 se houver ERRO.
"""
import argparse
import json
import os
import sys
import time

LARGURAS = [320, 360, 375, 390, 414, 430, 540, 600, 768, 820, 1024, 1180, 1280, 1366, 1440, 1536, 1920, 2560]
PAISAGEM = [(667, 375), (844, 390), (926, 428), (1024, 600)]
ESTADOS_RELOGIO = {
    "antes": "2026-10-20T12:00:00-03:00",
    "hoje-antes": "2026-11-09T18:00:00-03:00",
    "noite1-ao-vivo": "2026-11-09T21:00:00-03:00",
    "entre-noites": "2026-11-10T12:00:00-03:00",
    "encerrado": "2026-11-12T12:00:00-03:00",
}

LAYOUT_JS = r"""
() => {
  const cw = document.documentElement.clientWidth, ch = window.innerHeight;
  const out = {cw, sw: document.documentElement.scrollWidth, fora: [], cortado: [], sobrep: [], margens: [], pequeno: [],
               alvos: [], imgs: [], h1: document.querySelectorAll('h1').length, longas: [], contraste: []};
  const vis = (e) => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
    return r.width > 1 && r.height > 1 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0.05; };
  const ignora = (e) => e.closest('[aria-hidden="true"],dialog:not([open]),[class*=marquee],[data-sobre-foto],svg,noscript,script,style')
    || (e.closest('details:not([open])') && !e.closest('summary') && e.tagName !== 'SUMMARY');
  const fixo = (e) => { let a = e; while (a && a !== document.documentElement) { const p = getComputedStyle(a).position; if (p === 'fixed' || p === 'sticky') return true; a = a.parentElement; } return false; };
  const nome = (e) => (e.tagName.toLowerCase() + '.' + (e.className && e.className.toString ? e.className.toString().split(' ')[0] : '')).slice(0, 30);
  const textoDireto = (e) => [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();

  const els = [...document.querySelectorAll('body *')].filter(e => vis(e) && !ignora(e));
  // fora da tela / cortado por overflow do ancestral
  els.forEach(e => {
    const r = e.getBoundingClientRect(); const t = textoDireto(e);
    if (!t && e.tagName !== 'IMG' && e.tagName !== 'BUTTON') return;
    if (r.right > cw + 1.5 || r.left < -1.5) {
      let clip = false, a = e.parentElement;
      while (a && a !== document.documentElement) {
        const o = getComputedStyle(a); if (/(hidden|clip)/.test(o.overflowX) && a.getBoundingClientRect().width <= cw + 1) { clip = true; break; } a = a.parentElement;
      }
      out.fora.push({e: nome(e), t: t.slice(0, 24), L: Math.round(r.left), R: Math.round(r.right), recortadoPorAncestral: clip});
    }
    let a = e.parentElement;
    while (a && a !== document.body) {
      const o = getComputedStyle(a), ra = a.getBoundingClientRect();
      if (/(hidden|clip)/.test(o.overflowX) && ra.width > 30 && t && (r.right > ra.right + 2 || r.left < ra.left - 2) && ra.right <= cw + 1) {
        out.cortado.push({e: nome(e), t: t.slice(0, 24), em: nome(a)}); break;
      }
      a = a.parentElement;
    }
    const fs = parseFloat(getComputedStyle(e).fontSize);
    if (t && fs < 14) out.pequeno.push({e: nome(e), t: t.slice(0, 24), fs});
    // linha longa
    const cs = getComputedStyle(e);
    if (t.length > 120 && (e.tagName === 'P' || e.tagName === 'LI')) {
      const cpl = r.width / (fs * 0.5);
      if (cpl > 95) out.longas.push({e: nome(e), cpl: Math.round(cpl)});
    }
  });
  // sobreposição entre blocos de texto (folhas)
  const folhas = els.filter(e => textoDireto(e) && !e.querySelector('h1,h2,h3,p,li,button,a')).slice(0, 220);
  for (let i = 0; i < folhas.length; i++) for (let j = i + 1; j < folhas.length; j++) {
    const a = folhas[i], b = folhas[j]; if (a.contains(b) || b.contains(a)) continue;
    if (fixo(a) || fixo(b)) continue;
    const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
    const w = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), h = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
    if (w > 2 && h > 2) {
      const area = w * h, menor = Math.min(ra.width * ra.height, rb.width * rb.height);
      if (area / menor > 0.18) out.sobrep.push({a: nome(a) + ':' + textoDireto(a).slice(0, 16), b: nome(b) + ':' + textoDireto(b).slice(0, 16), pct: Math.round(100 * area / menor)});
    }
  }
  // margens desiguais (caixas de coluna)
  document.querySelectorAll('main *, header *').forEach(e => {
    if (!vis(e) || ignora(e) || e.closest('header,[role=banner]') || fixo(e)) return;
    const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
    if (r.width < 0.62 * cw || r.width > 0.985 * cw || r.height < 12) return;
    const tag = e.tagName.toLowerCase();
    if ((tag === 'button' || tag === 'a') && r.width < 0.9 * cw) return;   // botão alinhado à esquerda numa coluna maior é desenho
    const caixa = cs.backgroundImage !== 'none' || !/rgba\(0, 0, 0, 0\)|transparent/.test(cs.backgroundColor) || parseFloat(cs.borderTopWidth) + parseFloat(cs.borderLeftWidth) > 0;
    if (!(['img', 'picture', 'figure', 'article', 'button', 'video', 'canvas'].includes(tag) || (['a', 'div', 'section', 'li'].includes(tag) && caixa))) return;
    let sx = 0; const mb = cs.boxShadow.match(/(-?\d+(?:\.\d+)?)px\s+(-?\d+(?:\.\d+)?)px\s+0px/);  // sombra dura desloca a borda visual
    if (mb) sx = Math.max(0, parseFloat(mb[1]));
    const L = r.left, R = cw - r.right - sx; if (L < 6 || R < 6) return;
    if (Math.abs(L - R) > 1.5 && Math.abs(L - R) < cw * 0.2) out.margens.push({e: nome(e), L: Math.round(L * 10) / 10, R: Math.round(R * 10) / 10, y: Math.round(r.top + scrollY)});
  });
  // alvos de toque
  document.querySelectorAll('a[href],button,input,select,textarea,summary').forEach(e => {
    if (!vis(e) || ignora(e)) return; const r = e.getBoundingClientRect();
    if (Math.min(r.width, r.height) < 44 && !(e.tagName === 'A' && e.closest('p,li') && r.height < 44))
      out.alvos.push({e: nome(e), t: (e.innerText || e.getAttribute('aria-label') || '').trim().slice(0, 20), w: Math.round(r.width), h: Math.round(r.height)});
  });
  // imagens
  document.querySelectorAll('img').forEach(i => {
    if (!vis(i)) return;
    if (i.complete && i.naturalWidth === 0) out.imgs.push({src: i.src.slice(-40), problema: 'quebrada'});
    else if (i.naturalWidth && i.getBoundingClientRect().width > i.naturalWidth * 1.6 && !/svg/.test(i.src))
      out.imgs.push({src: i.src.slice(-40), problema: 'ampliada ' + Math.round(i.getBoundingClientRect().width) + '>' + i.naturalWidth});
    if (!i.hasAttribute('alt')) out.imgs.push({src: i.src.slice(-40), problema: 'sem alt'});
  });
  // contraste (fundo sólido)
  const lum = (c) => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  const rgba = (s) => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  let n = 0;
  for (const e of els) {
    if (n > 140) break; const t = textoDireto(e); if (t.length < 3) continue;
    let a = e, bg = null, indet = false;
    while (a && a !== document.documentElement) {
      const cs = getComputedStyle(a);
      if (cs.backgroundImage !== 'none' && !/^none/.test(cs.backgroundImage) && !/url\(.*(grao|grain)/.test(cs.backgroundImage)) { indet = true; break; }
      const c = rgba(cs.backgroundColor); if (c && c[3] > 0.95) { bg = c; break; }
      a = a.parentElement;
    }
    if (indet || !bg) continue;
    const cs = getComputedStyle(e); const fg = rgba(cs.color); if (!fg) continue;
    let op = 1, z = e; while (z && z !== document.body) { op *= +getComputedStyle(z).opacity; z = z.parentElement; }
    const fa = fg[3] * op, mix = [0, 1, 2].map(i => fg[i] * fa + bg[i] * (1 - fa));
    const L1 = lum(mix), L2 = lum(bg), ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const fs = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700;
    const grande = fs >= 24 || (fs >= 18.66 && bold), min = grande ? 3 : 4.5;
    n++;
    if (ratio < min) out.contraste.push({e: nome(e), t: t.slice(0, 22), ratio: Math.round(ratio * 100) / 100, min});
  }
  return out;
}
"""

FOCO_JS = r"""
() => {
  const sel = 'a[href],button,input,select,textarea,summary,[tabindex]:not([tabindex="-1"])';
  const els = [...document.querySelectorAll(sel)].filter(e => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
    return r.width > 1 && r.height > 1 && cs.visibility !== 'hidden' && cs.display !== 'none' && !e.closest('dialog:not([open])') && !e.closest('[aria-hidden="true"]'); });
  return els.length;
}
"""

COUNTDOWN_JS = r"""
() => {
  const c = document.querySelector('[class*=-cd], [class*=contador], [class*=relogio], [class*=tc], [class*=countdown]');
  const t = c ? c.innerText.replace(/\s+/g, ' ').trim() : '';
  const b = c ? c.getBoundingClientRect() : null;
  return {texto: t.slice(0, 140), h: b ? Math.round(b.height) : 0, w: b ? Math.round(b.width) : 0};
}
"""

INSTR_JS = r"""
() => {
  window.__m = {cls: 0, lcp: 0, longas: 0, tbt: 0};
  try { new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) window.__m.cls += e.value; })).observe({type: 'layout-shift', buffered: true}); } catch (e) {}
  try { new PerformanceObserver(l => l.getEntries().forEach(e => { window.__m.lcp = Math.round(e.startTime); })).observe({type: 'largest-contentful-paint', buffered: true}); } catch (e) {}
  try { new PerformanceObserver(l => l.getEntries().forEach(e => { window.__m.longas++; window.__m.tbt += Math.max(0, e.duration - 50); })).observe({type: 'longtask', buffered: true}); } catch (e) {}
}
"""


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("-o", default=None)
    ap.add_argument("--rapido", action="store_true", help="menos larguras (320, 360, 390, 768, 1024, 1440) e sem paisagem")
    ap.add_argument("--so", default="layout,foco,popup,relogio,movimento", help="seções a rodar, separadas por vírgula")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright

    url = a.url if a.url.endswith("/") or "?" in a.url else a.url + "/"
    out = a.o or os.path.join(os.environ.get("TEMP", "."), "_teste_total")
    os.makedirs(out, exist_ok=True)
    sel = set(x.strip() for x in a.so.split(","))
    larguras = [320, 360, 390, 768, 1024, 1440] if a.rapido else LARGURAS
    paisagem = [] if a.rapido else PAISAGEM
    erros, avisos, info = [], [], {}
    t0 = time.time()

    def add(lst, w, msg):
        s = f"{w}: {msg}"
        if s not in lst:
            lst.append(s)

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", ignore_default_args=["--hide-scrollbars"])

        def nova(w, h, mobile=False, reduce=False, dpr=1):
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dpr, is_mobile=mobile, has_touch=mobile,
                                reduced_motion="reduce" if reduce else "no-preference")
            ctx.add_init_script(INSTR_JS.replace("() => {", "(function(){").rstrip().rstrip("}") + "})();")
            return ctx

        # ---------- 1) LAYOUT por largura ----------
        todas = [(w, 740 if w < 700 else 900, False, f"{w}") for w in larguras] + \
                [(w, h, True, f"{w}x{h}-paisagem") for (w, h) in paisagem] + \
                [(w, 844, True, f"{w}-celular") for w in (360, 390, 430)]
        for w, h, mob, nome in todas:
            ctx = nova(w, h, mobile=mob, reduce=True)  # modo reduzido: sistema pede menos movimento
            pg = ctx.new_page()
            logs, falhas = [], []
            pg.on("console", lambda m, L=logs: L.append(m.text) if m.type in ("error",) else None)
            pg.on("pageerror", lambda e, L=logs: L.append("pageerror: " + str(e)[:100]))
            pg.on("response", lambda r, L=falhas: L.append((r.status, r.url[-60:])) if r.status >= 400 else None)
            pg.goto(url, wait_until="networkidle")
            pg.wait_for_timeout(1400)
            H = pg.evaluate("document.documentElement.scrollHeight")
            y = 0
            while y < H:
                pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(70); y += max(200, h // 2)
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)
            d = pg.evaluate(LAYOUT_JS)
            if d["sw"] > d["cw"] + 1:
                add(erros, nome, f"rolagem horizontal ({d['sw']} > {d['cw']})")
            for q in d["fora"][:3]:
                (avisos if q["recortadoPorAncestral"] else erros).append(f"{nome}: «{q['t']}» <{q['e']}> fora da tela (L={q['L']} R={q['R']})")
            for q in d["cortado"][:3]:
                add(erros, nome, f"texto cortado «{q['t']}» <{q['e']}> por overflow de <{q['em']}>")
            for q in d["sobrep"][:4]:
                add(erros, nome, f"blocos de texto sobrepostos {q['pct']}%: «{q['a']}» × «{q['b']}»")
            for q in d["margens"][:3]:
                add(avisos, nome, f"margens desiguais <{q['e']}> esquerda {q['L']} × direita {q['R']} (y={q['y']})")
            for q in d["pequeno"][:3]:
                add(avisos, nome, f"fonte {q['fs']:.0f}px «{q['t']}»")
            if (mob or w <= 430) and d["alvos"]:
                for q in d["alvos"][:3]:
                    add(avisos, nome, f"alvo de toque {q['w']}×{q['h']} «{q['t']}»")
            for q in d["imgs"][:4]:
                add(erros if q["problema"] in ("quebrada", "sem alt") else avisos, nome, f"imagem {q['problema']} {q['src']}")
            if d["h1"] != 1:
                add(erros, nome, f"{d['h1']} <h1> (deve ser 1)")
            for q in d["longas"][:2]:
                add(avisos, nome, f"linha longa (~{q['cpl']} caracteres) <{q['e']}>")
            for q in d["contraste"][:4]:
                add(erros if q["ratio"] < 3 else avisos, nome, f"contraste {q['ratio']}:1 (mín. {q['min']}) «{q['t']}» <{q['e']}>")
            for l in logs[:3]:
                add(erros, nome, f"console: {l[:90]}")
            for f in falhas[:3]:
                add(erros, nome, f"requisição {f[0]} {f[1]}")
            if w in (360, 390, 768, 1024, 1440) and not mob:
                pg.screenshot(path=os.path.join(out, f"{nome}-dobra.png"))
                pg.screenshot(path=os.path.join(out, f"{nome}.png"), full_page=True)
            info[nome] = {"altura": H, "cw": d["cw"]}
            ctx.close()

        # ---------- 2) FOCO VISÍVEL + ORDEM DO TAB (desktop 1440 e 390) ----------
        for w in ((1440, 390) if "foco" in sel else ()):
            ctx = nova(w, 900 if w > 700 else 844, reduce=True)
            pg = ctx.new_page()
            pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(1200)
            n = pg.evaluate(FOCO_JS)
            sem_anel, vistos = [], 0
            for i in range(min(30, n + 2)):
                pg.keyboard.press("Tab"); pg.wait_for_timeout(40)
                r = pg.evaluate("""() => { const e = document.activeElement; if (!e || e === document.body) return null;
                  const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
                  const anel = (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || (cs.boxShadow && cs.boxShadow !== 'none');
                  return {t: (e.innerText || e.getAttribute('aria-label') || e.tagName).trim().slice(0, 24), anel, noView: r.bottom > 0 && r.top < innerHeight}; }""")
                if r:
                    vistos += 1
                    if not r["anel"]:
                        sem_anel.append(r["t"])
            if sem_anel:
                add(avisos, f"{w}-foco", f"{len(sem_anel)} controle(s) sem anel de foco visível: {', '.join(sem_anel[:4])}")
            info[f"{w}-foco"] = {"focaveis": n, "percorridos": vistos}
            ctx.close()

        # ---------- 3) POP-UP: fluxo completo ----------
        for w, h, mob in (((360, 740, True), (390, 844, False), (768, 1024, False), (1440, 900, False)) if "popup" in sel else ()):
            nome = f"popup-{w}{'-celular' if mob else ''}"
            ctx = nova(w, h, mobile=mob, reduce=True)
            pg = ctx.new_page()
            logs = []
            pg.on("console", lambda m, L=logs: L.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e, L=logs: L.append(str(e)[:100]))
            pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(1200)
            qtd = pg.evaluate("document.querySelectorAll('[data-open-modal]').length")
            info[nome] = {"ctas": qtd}
            if qtd == 0:
                add(erros, nome, "nenhum [data-open-modal] na página")
                ctx.close(); continue
            # abre por TODOS os CTAs (rola até cada um)
            for idx in range(qtd):
                try:
                    pg.evaluate(f"""() => {{ const e = document.querySelectorAll('[data-open-modal]')[{idx}]; e.scrollIntoView({{block:'center'}}); }}""")
                    pg.wait_for_timeout(250)
                    el = pg.locator("[data-open-modal]").nth(idx)
                    if not el.is_visible():
                        continue
                    el.click(timeout=2500)
                    pg.wait_for_timeout(950)   # a folha do celular ainda sobe nos primeiros ~600 ms
                    aberto = pg.evaluate("!!document.querySelector('dialog[open]')")
                    if not aberto:
                        add(erros, nome, f"CTA #{idx} não abriu o pop-up")
                        continue
                    if idx in (0, qtd - 1):
                        foco = pg.evaluate("!!document.activeElement && !!document.activeElement.closest('dialog')")
                        if not foco:
                            add(avisos, nome, f"CTA #{idx}: foco não entrou no pop-up")
                        caber = pg.evaluate("""() => { const d = document.querySelector('dialog[open]'); const r = d.getBoundingClientRect();
                           return {top: r.top, bottom: r.bottom, h: innerHeight, left: r.left, right: r.right, w: document.documentElement.clientWidth,
                                   rol: d.scrollHeight > d.clientHeight + 2, travado: getComputedStyle(document.body).overflow}; }""")
                        if caber["top"] < -1 or caber["bottom"] > caber["h"] + 1 or caber["left"] < -1 or caber["right"] > caber["w"] + 16:
                            add(erros, nome, f"pop-up não cabe na tela: {caber}")
                        if caber["travado"] not in ("hidden", "clip"):
                            add(avisos, nome, f"rolagem do fundo não travada com pop-up aberto (overflow={caber['travado']})")
                        # Tab não escapa
                        escapou = False
                        for _ in range(14):
                            pg.keyboard.press("Tab"); pg.wait_for_timeout(25)
                            if pg.evaluate("!!document.activeElement && document.activeElement !== document.body && !document.activeElement.closest('dialog')"):
                                escapou = True; break   # body = foco foi para o navegador (comportamento normal do <dialog> modal)
                        if escapou:
                            add(erros, nome, "Tab escapa do pop-up (foco não fica preso)")
                        if idx == 0:
                            # envio vazio
                            pg.keyboard.press("Enter") if False else None
                            btn = pg.locator("dialog[open] button[type=submit], dialog[open] form button").last
                            try:
                                btn.click(timeout=2000); pg.wait_for_timeout(350)
                                tem_erro = pg.evaluate("""() => { const d = document.querySelector('dialog[open]');
                                  return !!d.querySelector('[aria-invalid=true],.erro,[class*=error],[role=alert]:not(:empty),[class*=err]'); }""")
                                if not tem_erro:
                                    add(erros, nome, "envio vazio não mostra erro")
                            except Exception as e:  # noqa: BLE001
                                add(avisos, nome, f"botão de envio não testável: {str(e)[:60]}")
                            # preenche válido
                            try:
                                campos = pg.locator("dialog[open] input:visible")
                                n_in = campos.count()
                                if n_in >= 2:
                                    campos.nth(0).fill("Teste Automático")
                                    campos.nth(n_in - 1).fill("123")
                                    btn.click(timeout=2000); pg.wait_for_timeout(300)
                                    inval = pg.evaluate("!!document.querySelector('dialog[open] [aria-invalid=true]')")
                                    if not inval:
                                        add(avisos, nome, "telefone inválido (123) não marcou erro")
                                    campos.nth(n_in - 1).fill("11912345678")
                                    pg.wait_for_timeout(100)
                                    btn.click(timeout=2000); pg.wait_for_timeout(1800)
                                    ok = pg.evaluate("""() => { const d = document.querySelector('dialog[open]'); return d ? d.innerText.slice(0, 200) : ''; }""")
                                    info[nome]["pos_envio"] = ok.replace("\n", " ")[:90]
                            except Exception as e:  # noqa: BLE001
                                add(avisos, nome, f"preenchimento não testável: {str(e)[:70]}")
                    # fecha por ESC e confere devolução do foco
                    pg.keyboard.press("Escape"); pg.wait_for_timeout(450)
                    if pg.evaluate("!!document.querySelector('dialog[open]')"):
                        add(erros, nome, f"CTA #{idx}: ESC não fecha o pop-up")
                        pg.evaluate("document.querySelector('dialog[open]').close()")
                    elif idx == 0:
                        f2 = pg.evaluate("document.activeElement && document.activeElement.hasAttribute('data-open-modal')")
                        if not f2:
                            add(avisos, nome, "foco não volta ao botão que abriu o pop-up")
                except Exception as e:  # noqa: BLE001
                    add(avisos, nome, f"CTA #{idx}: {str(e)[:80]}")
            # clique no fundo fecha
            try:
                pg.reload(wait_until="networkidle"); pg.wait_for_timeout(900)
                pg.evaluate("window.scrollTo(0,0)")
                first = pg.locator("[data-open-modal]:visible").first
                first.click(timeout=2500); pg.wait_for_timeout(400)
                pg.mouse.click(4, 4); pg.wait_for_timeout(400)
                if pg.evaluate("!!document.querySelector('dialog[open]')"):
                    add(avisos, nome, "clique no fundo não fecha o pop-up")
                    pg.keyboard.press("Escape")
                pg.screenshot(path=os.path.join(out, f"{nome}.png"))
            except Exception:
                pass
            if w in (360, 1440):
                # screenshot do pop-up aberto
                try:
                    pg.locator("[data-open-modal]:visible").first.click(timeout=2500); pg.wait_for_timeout(500)
                    pg.screenshot(path=os.path.join(out, f"{nome}-aberto.png"))
                    pg.keyboard.press("Escape")
                except Exception:
                    pass
            for l in logs[:2]:
                add(erros, nome, f"console: {l[:90]}")
            ctx.close()

        # ---------- 4) RELÓGIO: 5 estados ----------
        alturas = {}
        for nome_e, iso in (ESTADOS_RELOGIO.items() if "relogio" in sel else ()):
            for w in (390, 1440):
                ctx = nova(w, 844 if w < 700 else 900, reduce=True)
                pg = ctx.new_page()
                sep = "&" if "?" in url else "?"
                pg.goto(f"{url}{sep}agora={iso}", wait_until="networkidle"); pg.wait_for_timeout(1000)
                c = pg.evaluate(COUNTDOWN_JS)
                alturas.setdefault(w, []).append((nome_e, c["h"]))
                tx = c["texto"]
                if not tx:
                    info.setdefault("relogio", {})[f"{nome_e}-{w}"] = "(sem contador nesta página)"
                    continue
                if "NaN" in tx or "undefined" in tx or "00 dias" in tx.lower() or "-" in tx.split(" ")[0:1] and False:
                    add(erros, f"relogio-{w}", f"estado {nome_e}: texto inválido «{tx[:50]}»")
                info.setdefault("relogio", {})[f"{nome_e}-{w}"] = tx[:70]
                ctx.close()
        for w, lst in alturas.items():
            hs = [x[1] for x in lst if x[1] and x[0] != "encerrado"]
            if hs and max(hs) - min(hs) > 6:
                add(avisos, f"relogio-{w}", f"altura do contador muda entre estados ({min(hs)}–{max(hs)} px): {lst}")

        # ---------- 5) MOVIMENTO: total / suave / parado ----------
        for w, h in (((390, 844), (1440, 900)) if "movimento" in sel else ()):
            for modo in ("total", "suave", "parado"):
                nome = f"movimento-{modo}-{w}"
                ctx = nova(w, h, reduce=(modo == "suave"))
                pg = ctx.new_page()
                sep = "&" if "?" in url else "?"
                pg.goto(f"{url}{sep}movimento={modo}", wait_until="networkidle"); pg.wait_for_timeout(1500)
                m0 = pg.evaluate("window.__m || {}")   # LCP/CLS do carregamento, ANTES de rolar
                n_anim = pg.evaluate("document.getAnimations().length")
                n_run = pg.evaluate("document.getAnimations().filter(a=>a.playState==='running').length")
                H = pg.evaluate("document.documentElement.scrollHeight")
                # rolagem medindo quadros
                quadros = pg.evaluate("""async (H) => { const dt = []; let last = performance.now(); let y = 0;
                    return await new Promise(res => { function f(t) { dt.push(t - last); last = t; y += 14; window.scrollTo(0, y);
                      if (y < Math.min(H, 4200)) requestAnimationFrame(f); else res(dt); } requestAnimationFrame(f); }); }""", H)
                pg.wait_for_timeout(300)
                y = 0
                while y < H:
                    pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(55); y += 320
                pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)
                invisiveis = pg.evaluate("""() => { const o = [];
                    document.querySelectorAll('h1,h2,h3,p,li,button,a,figure,img').forEach(e => { if (e.closest('dialog:not([open])') || e.closest('[aria-hidden=true]')) return;
                      let op = 1, n = e; while (n && n !== document.body) { op *= +getComputedStyle(n).opacity; n = n.parentElement; }
                      const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
                      if (op < 0.1 && r.width > 4 && cs.display !== 'none' && cs.visibility !== 'hidden') o.push((e.innerText || e.alt || e.tagName).trim().slice(0, 24)); });
                    return o.slice(0, 6); }""")
                m = pg.evaluate("window.__m || {}")
                m["lcp"] = m0.get("lcp", 0)   # o LCP real é o do carregamento
                m["cls_carga"] = m0.get("cls", 0)
                dt = sorted(quadros)
                p95 = round(dt[int(len(dt) * 0.95)], 1) if dt else 0
                marq = pg.evaluate("""async () => { const t = document.querySelector('[class*=marquee__track]'); if (!t) return null;
                    const a = getComputedStyle(t).transform; await new Promise(r => setTimeout(r, 700)); const b = getComputedStyle(t).transform;
                    return {muda: a !== b, anim: getComputedStyle(t).animationName}; }""")
                info[nome] = {"animacoes": n_anim, "correndo": n_run, "cls": round(m.get("cls", 0), 3), "lcp_ms": m.get("lcp"),
                              "tarefas_longas": m.get("longas"), "tbt_ms": round(m.get("tbt", 0)), "quadro_p95_ms": p95, "faixa": marq}
                if modo in ("total", "suave") and n_anim < 5:
                    add(erros, nome, f"quase nenhuma animação ativa ({n_anim}) no modo {modo}: a página parece parada")
                if modo == "parado" and n_run > 3:
                    add(avisos, nome, f"{n_run} animações ainda correndo em modo parado")
                if invisiveis:
                    add(erros, nome, f"conteúdo invisível depois de rolar: {invisiveis[:3]}")
                if m.get("cls", 0) > 0.1:
                    add(erros, nome, f"CLS {m['cls']:.3f} (> 0,1)")
                elif m.get("cls", 0) > 0.02:
                    add(avisos, nome, f"CLS {m['cls']:.3f}")
                if m.get("lcp", 0) > 2500:
                    add(avisos, nome, f"LCP {m['lcp']} ms")
                if p95 > 60:
                    add(avisos, nome, f"tempo de quadro p95 {p95} ms na rolagem (headless/CPU)")
                if marq and modo == "total" and not marq["muda"]:
                    add(avisos, nome, "faixa não anda em modo total")
                ctx.close()
        b.close()

    # ---------- relatório ----------
    rel = {"url": url, "segundos": round(time.time() - t0), "erros": erros, "avisos": avisos, "info": info}
    json.dump(rel, open(os.path.join(out, "_teste-total.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = [f"# Teste total — {url}", f"{len(erros)} erro(s) · {len(avisos)} aviso(s) · {rel['segundos']} s", "", "## Erros"]
    md += [f"- {e}" for e in erros] or ["- nenhum"]
    md += ["", "## Avisos"] + ([f"- {e}" for e in avisos] or ["- nenhum"])
    md += ["", "## Medidas", "```", json.dumps(info, ensure_ascii=False, indent=1)[:6000], "```"]
    open(os.path.join(out, "_teste-total.md"), "w", encoding="utf-8").write("\n".join(md))
    print(f"ERROS: {len(erros)} · AVISOS: {len(avisos)} · {rel['segundos']} s")
    for e in erros[:40]:
        print("  ERRO", e)
    for e in avisos[:40]:
        print("  aviso", e)
    print("→", out)
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
