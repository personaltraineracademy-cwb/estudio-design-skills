"""PROVA DE CAMADAS — o "olho" de um diretor de arte sênior, automatizado, para peças montadas no palco.py.

Lê o HTML salvo pelo palco (st.render(..., html_out=...)), abre no Chrome e faz o que um sênior faz no Photoshop antes
de entregar: liga/desliga camadas, aperta os olhos, vê em P&B, espelha, mede o contraste no pixel e procura
tangentes. Saída: lista de avisos (zerar antes de mostrar) + relatório + FOLHA DE PROVA (png).

CAMADAS (data-plano, 0–7; sem o atributo, deduzido do data-tipo):
  0 fundo · 1 textura/atmosfera · 2 elemento atrás (inclui texto ATRÁS da pessoa) · 3 sujeito (foto recortada)
  4 elemento na frente / rótulos · 5 tarjas, barras, painéis · 6 texto e logo · 7 acabamento (grão global, overlay)

CHECAGENS (cada uma com o porquê):
  C1 contraste REAL: compara a peça com e sem texto; nos pixels da letra, mede texto × o que está embaixo de verdade
     (grão, foto, degradê). Usa o percentil 5 (o pior trecho), não a média. Limite WCAG: 4,5:1; texto grande
     (≥ 72 px de corpo, ou ≥ 56 px em negrito, no canvas de 1080) 3:1.
  C2 tangente: duas bordas que QUASE se tocam (0 < distância < τ) — o defeito clássico de composição; ou encosta de
     propósito (sobrepõe) ou respira. τ = 0,5 U (U = 2,2% do lado menor ≈ 24 px). Vale entre elementos, entre elemento
     e pessoa (pela silhueta real) e entre a pessoa e a borda da peça.
  C3 rosto: nada pintado NA FRENTE da pessoa (tarja, texto, logo) pode cobrir o rosto (detector YuNet, OpenCV).
  C4 palavra atrás da pessoa: % de cada letra escondida pela silhueta. Limites (unificados, camadas.md §4):
     palavra ≤ 30%, letra ≤ 50%, 1ª letra ≤ 15% (a 1ª letra ancora a leitura).
  C5 ritmo: espaços verticais/horizontais entre vizinhos que são QUASE iguais (0,5 < Δ ≤ 3 px) — ou iguais ou
     claramente diferentes (mesma lógica do "quase alinhado").
  C6 herói: o elemento marcado data-heroi="1" precisa ter o MAIOR destaque (mapa de destaque = saliência espectral +
     contraste local); senão a hierarquia está errada.
  Relatório (sem aviso): ordem de leitura estimada, equilíbrio (centro de massa do destaque), partilha de valores
  claro/médio/escuro (notan), espaços em U.

python camadas.py <peca.html> [--formato story] [--saida pasta]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compor as K  # noqa: E402

YUNET = os.path.join(os.path.expanduser("~"), ".cache", "brand-studio", "models", "yunet", "yunet.onnx")
NOMES = ["fundo", "textura", "atrás", "sujeito", "frente", "tarjas", "texto", "acabamento"]

JS_PLANOS = r"""
() => {
  const peca = document.getElementById('peca');
  const porTipo = {fundo: 2, foto: 3, rotulo: 4, visor: 4, barra: 5, txt: 6, logo: 6};
  const els = [...peca.querySelectorAll('*')];
  for (const el of els) {
    let p = el.dataset.plano;
    if (p === undefined) {
      const pai = el.parentElement;
      if (el.dataset.tipo && el.dataset.tipo in porTipo) p = porTipo[el.dataset.tipo];
      else if (pai !== peca && pai.dataset.planoCalc !== undefined) p = pai.dataset.planoCalc;
      else if (el.classList.contains('full')) p = 0;
      else p = 1;
    }
    el.dataset.planoCalc = +p;
  }
  return [...new Set(els.map(e => +e.dataset.planoCalc))].sort((a, b) => a - b);
}
"""

JS_ATRAS = r"""
() => {
  // ordem REAL de pintura: um texto com uma foto pintada POR CIMA dele (no centro de alguma letra) está ATRÁS da
  // pessoa → plano 2 (ele e os filhos). Não depende de declaração: lê o que o navegador desenha.
  const fotos = new Set(document.querySelectorAll('#peca img[data-tipo="foto"]'));
  const atras = [];
  for (const el of document.querySelectorAll('#peca [data-tipo="txt"]')) {
    const nos = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim());
    let achou = false;
    for (const n of nos) { for (let i = 0; i < n.textContent.length && !achou; i++) {
      if (!n.textContent[i].trim()) continue;
      const q = document.createRange(); q.setStart(n, i); q.setEnd(n, i + 1);
      const b = q.getBoundingClientRect();
      const r = el.getBoundingClientRect();              // altura da maiúscula (caixa aparada), não a da linha
      const y0 = Math.max(b.top, r.top), y1 = Math.min(b.bottom, r.bottom);
      for (const fy of [0.15, 0.4, 0.65, 0.9]) for (const fx of [0.25, 0.5, 0.75]) {
        if (achou) break;
        const pilha = document.elementsFromPoint(b.left + fx * (b.right - b.left), y0 + fy * (y1 - y0));
        for (const e of pilha) { if (e === el || el.contains(e)) break; if (fotos.has(e)) { achou = true; break; } }
      }
    } }
    if (achou) { el.dataset.planoCalc = 2; for (const f of el.querySelectorAll('*')) f.dataset.planoCalc = 2;
                 atras.push(el.dataset.qa || el.className); }
  }
  return atras;
}
"""

JS_MOSTRA = r"""
(k) => { for (const el of document.querySelectorAll('#peca *'))
           el.style.visibility = (+el.dataset.planoCalc <= k) ? 'visible' : 'hidden'; }
"""

JS_SO_FOTOS = r"""
() => { const p = document.getElementById('peca'); p.style.background = 'transparent';
        document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent';
        for (const el of document.querySelectorAll('#peca *'))
          el.style.visibility = (el.dataset.tipo === 'foto') ? 'visible' : 'hidden'; }
"""

JS_TEXTOS = r"""
() => {
  // todo elemento com texto próprio (inclui os sem data-qa, ex.: o "2." dentro da tarja)
  const R0 = document.getElementById('peca').getBoundingClientRect();
  const out = [];
  for (const el of document.querySelectorAll('#peca *')) {
    const nos = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim());
    if (!nos.length) continue;
    const rg = document.createRange(); rg.selectNodeContents(el);
    const r = el.getBoundingClientRect();
    const rt = rg.getBoundingClientRect();          // caixa só das LETRAS (sem padding da barra)
    const cs = getComputedStyle(el);
    let rot = el.dataset.qa, a = el;
    while (!rot && a.parentElement) { a = a.parentElement; rot = a.dataset.qa; }
    // retângulo de cada letra (para a checagem C4)
    const letras = [];
    for (const n of nos) for (let i = 0; i < n.textContent.length; i++) {
      const ch = n.textContent[i]; if (!ch.trim()) continue;
      const q = document.createRange(); q.setStart(n, i); q.setEnd(n, i + 1);
      const b = q.getBoundingClientRect();
      letras.push({ch, c: [b.left - R0.left, b.top - R0.top, b.right - R0.left, b.bottom - R0.top]});
    }
    out.push({r: (el.dataset.qa ? '' : '(texto em) ') + (rot || el.className || el.tagName),
              c: [r.left - R0.left, r.top - R0.top, r.right - R0.left, r.bottom - R0.top],
              ct: [Math.max(r.left, rt.left) - R0.left, Math.max(r.top, rt.top) - R0.top,
                   Math.min(r.right, rt.right) - R0.left, Math.min(r.bottom, rt.bottom) - R0.top],
              fundo_proprio: (() => { let e = el; while (e && e.id !== 'peca') { const c = getComputedStyle(e);
                  if (c.backgroundImage !== 'none' || !/rgba\(.*,\s*0\)|transparent/.test(c.backgroundColor)) {
                    const q = e.getBoundingClientRect();
                    return [q.left - R0.left, q.top - R0.top, q.right - R0.left, q.bottom - R0.top]; }
                  e = e.parentElement; } return null; })(),
              fs: parseFloat(cs.fontSize), fw: parseInt(cs.fontWeight), plano: +el.dataset.planoCalc,
              heroi: el.dataset.heroi === '1', ler: !!el.closest('[data-ler="1"]'), letras});
  }
  return out;
}
"""


def _np(png_bytes, alfa=False):
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(png_bytes)).convert("RGBA" if alfa else "RGB")
    return np.asarray(im).astype(np.float32)


def _lum(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def _contraste(l1, l2):
    a, b = np.maximum(l1, l2), np.minimum(l1, l2)
    return (a + 0.05) / (b + 0.05)


def destaque(rgb):
    """Mapa de destaque 0–1: saliência espectral (Hou & Zhang 2007) + contraste local de luminância (o 'apertar os
    olhos'). Modelo simples e local — serve para ORDENAR elementos, não para prever olhar com precisão."""
    import cv2
    h, w = rgb.shape[:2]
    g = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    sw = 96
    sm = cv2.resize(g, (sw, max(8, round(sw * h / w))), interpolation=cv2.INTER_AREA)
    F = np.fft.fft2(sm)
    A, P = np.log(np.abs(F) + 1e-6), np.angle(F)
    S = np.abs(np.fft.ifft2(np.exp((A - cv2.blur(A, (3, 3))) + 1j * P))) ** 2
    S = cv2.GaussianBlur(S.astype(np.float32), (0, 0), 2.5)
    S = cv2.resize(S, (w, h), interpolation=cv2.INTER_CUBIC)
    L = g / 255.0
    lc = np.abs(L - cv2.GaussianBlur(L, (0, 0), w / 18))
    lc = cv2.GaussianBlur(lc, (0, 0), w / 90)
    n = lambda x: (x - x.min()) / (np.ptp(x) + 1e-9)  # noqa: E731
    return n(0.5 * n(S) + 0.5 * n(lc))


def peso_visual(rgb):
    """Peso visual do 'olho apertado': desfoca (σ = 0,8% da largura) e mede o contraste de luminosidade (L*) contra o
    entorno amplo (σ = 12% da largura). Bloco chapado grande e contrastado pesa muito; texto miúdo vira mancha leve —
    como o diretor de arte vê de longe. Serve para conferir o HERÓI (C6); o mapa espectral fica para a folha."""
    import cv2
    w = rgb.shape[1]
    L = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32) / 255.0
    perto = cv2.GaussianBlur(L, (0, 0), 0.008 * w)
    longe = cv2.GaussianBlur(L, (0, 0), 0.12 * w)
    return np.abs(perto - longe)


def notan(rgb):
    """3 valores (escuro < 1/3 ≤ médio < 2/3 ≤ claro) pela luminosidade L* — a estrutura que sobrevive à miniatura."""
    import cv2
    lab = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32) / 255.0
    q = np.where(lab < 1 / 3, 30, np.where(lab < 2 / 3, 128, 235)).astype(np.uint8)
    return q, {"escuro": float((lab < 1 / 3).mean()), "médio": float(((lab >= 1 / 3) & (lab < 2 / 3)).mean()),
               "claro": float((lab >= 2 / 3).mean())}


def _dist_caixas(a, b):
    gx = max(b[0] - a[2], a[0] - b[2], 0)
    gy = max(b[1] - a[3], a[1] - b[3], 0)
    return (gx * gx + gy * gy) ** 0.5


def provar(html, formato=None, saida=None, heroi=None, tensao=False):
    """Roda a prova. Retorna (avisos, relatorio, caminho_da_folha). `heroi` = rótulo ou LISTA de rótulos (herói duplo
    declarado, ex.: o encaixe nome × pessoa)."""
    herois_decl = list(heroi) if isinstance(heroi, (list, tuple)) else ([heroi] if heroi else [])
    import cv2
    import palco as PL
    from playwright.sync_api import sync_playwright
    doc = open(html, encoding="utf-8").read()
    saida = saida or os.path.dirname(html)
    base = os.path.splitext(os.path.basename(html))[0]
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page(viewport={"width": 2200, "height": 2200})
        pg.set_content(doc, wait_until="load")
        pg.evaluate("document.fonts.ready")
        loc = pg.locator("#peca")
        W, H = pg.evaluate("[document.getElementById('peca').offsetWidth, document.getElementById('peca').offsetHeight]")
        pg.evaluate(JS_PLANOS)
        atras = pg.evaluate(JS_ATRAS)
        planos = pg.evaluate("[...new Set([...document.querySelectorAll('#peca *')].map(e => +e.dataset.planoCalc))]"
                             ".sort((a, b) => a - b)")
        med = pg.evaluate(PL.JS_MEDIDAS)
        textos = pg.evaluate(JS_TEXTOS)
        # extensão PINTADA do herói = união da caixa dele com a de todos os filhos (ex.: tarja que sangra por um filho)
        heroi_cxs = {h_: pg.evaluate("""(h) => { const el = [...document.querySelectorAll('#peca [data-qa]')]
            .find(e => e.dataset.qa === h); if (!el) return null;
          const R0 = document.getElementById('peca').getBoundingClientRect();
          let [a, b, c, d] = [1e9, 1e9, -1e9, -1e9];
          for (const e of [el, ...el.querySelectorAll('*')]) { const r = e.getBoundingClientRect();
            if (!r.width || !r.height) continue;
            a = Math.min(a, r.left); b = Math.min(b, r.top); c = Math.max(c, r.right); d = Math.max(d, r.bottom); }
          return [a - R0.left, b - R0.top, Math.min(c, R0.right) - R0.left, Math.min(d, R0.bottom) - R0.top]; }""",
            h_) for h_ in herois_decl}
        A = _np(loc.screenshot())
        # peça FINAL e versão sem texto da passada de imagem (grão/efeitos), se o palco gerou: as medidas de pixel
        # (contraste real, grão, pretos, banding, peso) usam a peça como ela sai, não o HTML cru
        png_fim, png_sem = html[:-5] + ".png", html[:-5] + "-sem-texto.png"
        final = (os.path.exists(png_fim) and os.path.exists(png_sem)
                 and os.path.getmtime(png_sem) >= os.path.getmtime(html) - 5)
        if final:
            from PIL import Image
            A = np.asarray(Image.open(png_fim).convert("RGB")).astype(np.float32)
        passos = []
        for k in planos:
            pg.evaluate(JS_MOSTRA, k)
            passos.append((k, _np(loc.screenshot())))
        pg.evaluate(JS_MOSTRA, 99)
        pg.add_style_tag(content="#peca *{color:transparent!important;text-shadow:none!important;"
                                 "-webkit-text-stroke:0!important}")
        B = _np(loc.screenshot())
        if final:
            B = np.asarray(Image.open(png_sem).convert("RGB")).astype(np.float32)
        pg.set_content(doc, wait_until="load")
        pg.evaluate("document.fonts.ready")
        pg.evaluate(JS_PLANOS)
        pg.evaluate(JS_SO_FOTOS)
        M = _np(loc.screenshot(omit_background=True), alfa=True)
        b.close()

    s = min(W, H)
    U = 0.022 * s
    tau = 0.015 * s                    # tangente: folga mínima 1,5% do lado menor (16 px no 1080) — pesquisa 7 §1.7
    avisos, rel = [], {"W": W, "H": H, "planos": [NOMES[k] if k < len(NOMES) else str(k) for k in planos],
                       "atras_da_pessoa": atras}
    pessoa = (M[..., 3] > 40).astype(np.uint8)

    # ---------------- C1 contraste real (pior 5% dos pixels da letra)
    d = np.abs(A - B).sum(axis=2)
    LA, LB = _lum(A), _lum(B)
    rel["contraste"] = []
    for t in textos:
        x0, y0, x1, y1 = [int(round(v)) for v in t["ct"]]      # caixa das letras (não a do elemento com padding)
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if x1 <= x0 or y1 <= y0:
            continue
        dd = d[y0:y1, x0:x1]
        if dd.max() < 40:
            continue                                   # texto escondido (ex.: atrás da pessoa por inteiro)
        nucleo = dd > max(40, 0.6 * dd.max())
        lt = np.median(LA[y0:y1, x0:x1][nucleo])       # cor real da letra (já com opacidade)
        cr = _contraste(lt, LB[y0:y1, x0:x1][nucleo])
        p5, p50 = float(np.percentile(cr, 5)), float(np.percentile(cr, 50))
        grande = t["fs"] * 1080 / s >= 72 or (t["fs"] * 1080 / s >= 56 and t["fw"] >= 700)
        lim = 3.0 if grande else 4.5
        # fundo calmo sob o texto (Scharff 1999): C_RMS do fundo SEM texto na caixa dilatada; luminância com o
        # mesmo +0,05 de "reflexo" do WCAG para não explodir em fundo escuro. ≤ 0,10 texto pequeno, ≤ 0,20 título.
        dl = int(round(min(0.1 * t["fs"], 0.012 * s)))   # tinta dilatada ~1 traço (pesquisa 7 §5.5), com teto
        ja, jb, jc, jd = x0 - dl, y0 - dl, x1 + dl, y1 + dl
        if t.get("fundo_proprio"):             # texto numa barra/tarja: o fundo dele é a barra (não o vizinho)
            fa, fb, fc, fd = t["fundo_proprio"]
            ja, jb, jc, jd = max(ja, fa), max(jb, fb), min(jc, fc), min(jd, fd)
        jan = (slice(max(0, int(jb)), min(H, int(jd))), slice(max(0, int(ja)), min(W, int(jc))))
        Yb = LB[jan]
        if t["plano"] < 3:                 # texto ATRÁS da pessoa: o fundo dele é só o que não é pessoa
            Yb = Yb[(M[..., 3][jan] <= 40)] if (M[..., 3][jan] <= 40).any() else Yb.ravel()
        crms = float(Yb.std() / (Yb.mean() + 0.05))
        lim_rms = 0.20 if t["fs"] * 1080 / s >= 2 * 25 / 0.72 else 0.10
        rel["contraste"].append((t["r"], round(p5, 2), round(p50, 2), lim, round(crms, 3)))
        if p5 < lim:
            avisos.append(f"C1 contraste baixo no pior trecho ({p5:.1f}:1 < {lim}:1; mediana {p50:.1f}): {t['r']}")
        if crms > lim_rms:
            avisos.append(f"C1b fundo agitado atrás do texto (C_RMS {crms:.2f} > {lim_rms}): {t['r']}")

    # ---------------- C2 tangentes
    cont = [e for e in med["els"] if e["t"] in ("txt", "logo", "barra") and not e["r"].startswith("dentro ")]
    for i, a in enumerate(cont):
        for b_ in cont[i + 1:]:
            if K._inter(a["c"], b_["c"], 0.0):
                continue
            dist = _dist_caixas(a["c"], b_["c"])
            if 0 < dist < tau:
                avisos.append(f"C2 tangente ({dist:.1f}px < {tau:.0f}): {a['r']} × {b_['r']}")
    if pessoa.any():
        dt = cv2.distanceTransform((1 - pessoa).astype(np.uint8), cv2.DIST_L2, 5)
        dti = cv2.distanceTransform(pessoa.astype(np.uint8), cv2.DIST_L2, 5)
        for e in cont:
            x0, y0, x1, y1 = [int(round(v)) for v in e["c"]]
            x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
            if x1 <= x0 or y1 <= y0:
                continue
            dm = float(dt[y0:y1, x0:x1].min())
            if 0 < dm < tau:
                avisos.append(f"C2 tangente com a pessoa ({dm:.1f}px < {tau:.0f}): {e['r']}")
            elif dm == 0:                                   # sobrepõe: tem de ser de verdade, não "raspando"
                fundo_p = float(dti[y0:y1, x0:x1].max())
                if 0 < fundo_p < tau:
                    avisos.append(f"C2 sobreposição tímida com a pessoa ({fundo_p:.1f}px < {tau:.0f}): {e['r']}")
        ys, xs = np.nonzero(pessoa)
        bordas = {"topo": ys.min(), "esquerda": xs.min(), "direita": W - 1 - xs.max(), "base": H - 1 - ys.max()}
        for lado, g in bordas.items():
            if 0 < g < tau:
                avisos.append(f"C2 pessoa quase tocando a borda ({lado}, {g:.0f}px): corte decidido ou respiro")

    # ---------------- C3 rosto coberto por algo NA FRENTE da pessoa
    rostos, nucleos = [], []
    if pessoa.any() and os.path.exists(YUNET):
        a = M[..., 3:4] / 255.0
        rgb = (M[..., :3] * a + 128 * (1 - a)).astype(np.uint8)
        esc = 960 / max(W, H)
        sm = cv2.resize(rgb, (round(W * esc), round(H * esc)), interpolation=cv2.INTER_AREA)
        det = cv2.FaceDetectorYN.create(YUNET, "", (sm.shape[1], sm.shape[0]), 0.7)
        _, f = det.detect(cv2.cvtColor(sm, cv2.COLOR_RGB2BGR))
        if f is not None:
            for r in f:
                x, y, w, h = (r[:4] / esc).tolist()
                rostos.append((x - 0.05 * w, y - 0.05 * h, x + 1.05 * w, y + 1.05 * h))     # +10% (pesquisa 7)
                pts = (r[4:14] / esc).reshape(5, 2)          # olho dir., olho esq., nariz, boca dir., boca esq.
                nucleos.append([tuple(pts[i]) for i in (0, 1, 3, 4)])
        frente = [e for e in med["els"] if e["t"] in ("txt", "logo", "barra")]
        planos_qa = {t["r"]: t["plano"] for t in textos}
        planos_qa.update({r: 2 for r in atras})
        for (fx0, fy0, fx1, fy1) in rostos:
            for e in frente:
                if planos_qa.get(e["r"], 6) < 3:
                    continue                            # elemento ATRÁS da pessoa não cobre o rosto
                ic = K._inter(e["c"], (fx0, fy0, fx1, fy1), 0.0)
                if ic:
                    area = (ic[2] - ic[0]) * (ic[3] - ic[1]) / ((fx1 - fx0) * (fy1 - fy0))
                    if area > 0.01:
                        avisos.append(f"C3 cobre o rosto ({area:.0%}): {e['r']}")
    rel["rostos"] = [tuple(round(v) for v in r) for r in rostos]

    # ---------------- C7 núcleo do rosto (olhos e boca) fora da área de TEXTO · C8 herói fora da área de HERÓI
    # (pesquisa 9 §9: texto e "herói" seguem a mesma regra; olhos e boca = núcleo; o corpo do herói pode ir até a área
    # de herói, nunca sob um retângulo da interface; fundo e decoração sangram)
    f_ = K.FORMATOS.get(formato, {}) if formato else {}
    zt, zb, zl, zr = f_.get("zona", (0, 0, 0, 0))
    excl = list(f_.get("excl", []))
    for pts in nucleos:
        fora = [p_ for p_ in pts if not (zl <= p_[0] <= W - zr and zt <= p_[1] <= H - zb)
                or any(z[0] <= p_[0] <= z[2] and z[1] <= p_[1] <= z[3] for z in excl)]
        if fora:
            avisos.append(f"C7 olhos/boca fora da área de texto (sob a interface do app): {len(fora)} de 4 pontos")
    # a CABEÇA inteira (caixa do rosto +10%) fica na área de herói e longe da coluna de ícones; o corpo pode sangrar
    for r in rostos:
        ha, hx = f_.get("heroi"), f_.get("heroi_excl", [])
        if ha and (r[0] < ha[0] or r[1] < ha[1] or r[2] > ha[2] or r[3] > ha[3]):
            avisos.append(f"C7 rosto sai da área de herói {ha}: {tuple(round(v) for v in r)}")
        for z in hx:
            if K._inter(r, z, 1.0):
                avisos.append(f"C7 rosto sob a coluna de ícones {z}")
    for heroi, heroi_cx in heroi_cxs.items():
        if not heroi_cx:
            continue
        for e in med["els"]:
            if e["r"] != heroi or e["t"] == "foto":
                continue
            ha = f_.get("heroi")
            hx = f_.get("heroi_excl", [])
            if ha and (heroi_cx[0] < ha[0] - 0.5 or heroi_cx[1] < ha[1] - 0.5 or heroi_cx[2] > ha[2] + 0.5
                       or heroi_cx[3] > ha[3] + 0.5):
                avisos.append(f"C8 o herói ({heroi}) sai da área de herói {ha} — elemento principal fica dentro, "
                              f"mesmo decorativo ({tuple(round(v) for v in heroi_cx)})")
            for z in hx:
                if K._inter(heroi_cx, z, 1.0):
                    avisos.append(f"C8 o herói ({heroi}) entra sob a coluna de ícones {z}")
    rel["rosto_nucleo"] = [[tuple(round(v) for v in p_) for p_ in pts] for pts in nucleos]

    # ---------------- integração da pessoa (pesquisa 8): C9 halo · C10 grão · C11 pretos/dominante · C12 banding
    import efeitos as EF
    lab = cv2.cvtColor(A.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    Lx = lab[..., 0] * 100 / 255
    rel["integracao"] = {}
    if pessoa.any():
        hc, he = EF.halo(Lx, pessoa.astype(np.float32))
        rel["integracao"]["halo_claro"], rel["integracao"]["franja_escura"] = round(hc, 3), round(he, 3)
        # C9 fica só no RELATÓRIO: calibrado em 24 peças, o número confunde a luz de contorno
        # proposital e o cabelo escuro com halo. A borda é conferida no OLHO (recortes a 400% na folha de prova).
        # grão: áreas lisas DENTRO da pessoa × FORA da pessoa (sem texto/logo)
        cinza = cv2.cvtColor(A.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        livre = np.ones((H, W), bool)
        for e in cont:
            x0, y0, x1, y1 = [int(round(v)) for v in e["c"]]
            livre[max(0, y0 - 8):y1 + 8, max(0, x0 - 8):x1 + 8] = False
        dentro = cv2.erode(pessoa, np.ones((9, 9), np.uint8)).astype(bool) & livre
        fora = (cv2.dilate(pessoa, np.ones((9, 9), np.uint8)) == 0) & livre
        gm = cv2.magnitude(cv2.Sobel(cinza.astype(np.float32), cv2.CV_32F, 1, 0),
                           cv2.Sobel(cinza.astype(np.float32), cv2.CV_32F, 0, 1))
        sd = EF.sigma_ruido(cinza, dentro & (gm < np.percentile(gm[dentro], 30))) if dentro.sum() > 500 else None
        sf = EF.sigma_ruido(cinza, fora & (gm < np.percentile(gm[fora], 30))) if fora.sum() > 500 else None
        rel["integracao"]["grao_pessoa_fundo"] = (sd and round(sd, 2), sf and round(sf, 2))
        if sd and sf and not 0.8 <= sd / sf <= 1.25:
            avisos.append(f"C10 grão diferente na pessoa ({sd:.2f}) e no fundo ({sf:.2f}); razão fora de 0,8–1,25")
        # pretos e dominante: P1 do L e a/b das sombras, pessoa × vizinhança (anel de 3% do lado)
        anel = (cv2.dilate(pessoa, np.ones((int(0.06 * s) | 1,) * 2, np.uint8)) > 0) & ~pessoa.astype(bool) & livre
        if anel.sum() > 500:
            Lp, Lv = np.percentile(Lx[pessoa.astype(bool)], 1), np.percentile(Lx[anel], 1)
            sp = pessoa.astype(bool) & (Lx <= np.percentile(Lx[pessoa.astype(bool)], 10))
            sv = anel & (Lx <= np.percentile(Lx[anel], 10))
            dab = float(np.hypot(lab[..., 1][sp].mean() - lab[..., 1][sv].mean(),
                                 lab[..., 2][sp].mean() - lab[..., 2][sv].mean()) * 100 / 255)
            rel["integracao"]["pretos_L_pessoa_viz"] = (round(float(Lp), 1), round(float(Lv), 1))
            rel["integracao"]["dominante_sombras_dab"] = round(dab, 1)
    bd = EF.banding(A.astype(np.uint8))
    rel["integracao"]["banding_por_mil"] = round(bd, 2)

    # ---------------- C6 herói + ordem de leitura + equilíbrio + notan
    D = destaque(A)
    PV = peso_visual(A)
    cands = [(e["r"], e["c"], None) for e in cont] + [(f["r"], f["c"], "foto") for f in med["fotos"]]
    massa = []
    for r, c, tipo in cands:
        x0, y0, x1, y1 = [int(round(v)) for v in c]
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if x1 > x0 and y1 > y0:
            pv = PV[y0:y1, x0:x1]
            if tipo == "foto":                       # a pessoa pesa pela silhueta, não pela caixa da imagem
                pv = pv * pessoa[y0:y1, x0:x1]
            massa.append((float(pv.sum()) / (W * H), r))
    massa.sort(reverse=True)
    rel["ordem_de_leitura"] = [(r, round(m, 4)) for m, r in massa[:8]]
    herois = [t["r"] for t in textos if t["heroi"]] + herois_decl
    if herois and massa and massa[0][1] not in herois:
        avisos.append(f"C6 o herói ({herois[0]}) não é o que mais chama atenção — quem chama: {massa[0][1]}")
    yy, xx = np.mgrid[0:H, 0:W]
    cm = (float((D * xx).sum() / D.sum()) / W - 0.5, float((D * yy).sum() / D.sum()) / H - 0.5)
    rel["equilibrio"] = (round(cm[0], 3), round(cm[1], 3))
    N, partilha = notan(A)
    rel["notan"] = {k: round(v, 2) for k, v in partilha.items()}
    if max(partilha.values()) < 0.45:
        avisos.append(f"C13 sem valor dominante no notan ({rel['notan']}; um valor ≥ 45%)")
    # equilíbrio DCM (Hübner & Fillinger 2016): massa = |L* − L* do fundo| (o que contrasta pesa)
    Ls = cv2.cvtColor(A.astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32) * 100 / 255
    mass = np.abs(Ls - np.median(Ls)) / 100
    bx, by = float((mass * xx).sum() / mass.sum() / W), float((mass * yy).sum() / mass.sum() / H)
    dcm = float(np.hypot(0.5 - bx, 0.5 - by) / 0.5 * 100)
    rel["DCM"] = round(dcm, 1)
    if dcm > 25 and not tensao:
        avisos.append(f"C14 desequilíbrio (DCM {dcm:.0f}% > 25%) sem tensão declarada")

    folha = _folha(A, passos, N, D, med, formato, W, H, os.path.join(saida, base + "-prova.png"), rostos)
    return avisos, rel, folha


def _folha(A, passos, N, D, med, formato, W, H, out, rostos):
    """Folha de prova: linha 1 = montagem camada por camada; linha 2 = final · notan · olhos apertados · destaque ·
    espelho · grade/zonas/caixas de tinta."""
    import cv2
    from PIL import Image, ImageDraw, ImageFont
    th = 420
    tw = round(W * th / H)

    def mini(x):
        return Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)).resize((tw, th), Image.LANCZOS)
    linha1 = [(f"{i + 1}. +{NOMES[k] if k < len(NOMES) else k}", mini(im)) for i, (k, im) in enumerate(passos)]
    blur = cv2.GaussianBlur(A, (0, 0), W / 60)
    heat = cv2.applyColorMap((D * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)[..., ::-1]
    heat = 0.45 * A + 0.55 * heat
    esp = A[:, ::-1]
    gr = Image.fromarray(A.astype(np.uint8)).convert("RGB")
    dr = ImageDraw.Draw(gr, "RGBA")
    zona = K.FORMATOS.get(formato, {}).get("zona", (0, 0, 0, 0)) if formato else (0, 0, 0, 0)
    excl = K.FORMATOS.get(formato, {}).get("excl", []) if formato else []
    zt, zb, zl, zr = zona
    for r in ((0, 0, W, zt), (0, H - zb, W, H), (0, 0, zl, H), (W - zr, 0, W, H), *excl):
        if r[2] > r[0] and r[3] > r[1]:
            dr.rectangle(r, fill=(255, 0, 60, 70))
    m = round(0.074 * min(W, H))
    x0, x1 = max(m, zl), W - max(m, zr)
    col = (x1 - x0 - 5 * 24) / 6
    for i in range(6):
        cx = x0 + i * (col + 24)
        dr.rectangle((cx, 0, cx + col, H), fill=(0, 200, 255, 22))
    for e in med["els"]:
        if e["t"] in ("txt", "logo", "barra"):
            dr.rectangle(e["c"], outline=(0, 255, 120, 255), width=2)
    for r in rostos:
        dr.rectangle(r, outline=(255, 210, 0, 255), width=3)
    linha2 = [("final", mini(A)), ("notan (3 valores)", mini(N[..., None].repeat(3, 2))),
              ("olhos apertados", mini(blur)), ("destaque", mini(heat)), ("espelho", mini(esp)),
              ("grade · zonas · tinta · rostos", gr.resize((tw, th), Image.LANCZOS))]
    try:
        fnt = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        fnt = ImageFont.load_default()
    n = max(len(linha1), len(linha2))
    S = Image.new("RGB", (n * (tw + 16) + 16, 2 * (th + 44) + 16), (34, 34, 34))
    d = ImageDraw.Draw(S)
    for li, linha in enumerate((linha1, linha2)):
        for i, (rot, im) in enumerate(linha):
            x, y = 16 + i * (tw + 16), 16 + li * (th + 44)
            S.paste(im, (x, y))
            d.text((x, y + th + 6), rot, fill=(230, 230, 230), font=fnt)
    S.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("html")
    ap.add_argument("--formato")
    ap.add_argument("--saida")
    ap.add_argument("--heroi")
    a = ap.parse_args()
    av, rel, folha = provar(a.html, a.formato, a.saida, a.heroi)
    import json
    print(json.dumps(rel, ensure_ascii=False, indent=1, default=str)[:4000])
    print("\n".join(av) or "PROVA ok")
    print(folha)
