"""ornamentos.mao — família "MARCAÇÃO À MÃO": a camada humana por cima da base técnica (elementos.md, "vivo 2026").

Motor: traço com PRESSÃO no estilo perfect-freehand (MIT, Steve Ruiz) reescrito em Python — a linha central vira um
polígono de largura variável: pouso da caneta (mais grosso no início), afina na saída (ponta longa), engrossa nas
curvas (a mão desacelera), tremor de pressão por semente; contorno limpo por união (skia-pathops), vetor puro.
O desenho de cada marca NUNCA é fórmula perfeita: o círculo não fecha (passa da largada), o sublinhado sobe no fim,
a cabeça da seta é um "V" de um traço só com braços desiguais (pesquisa 11 E33; pesquisa 13 §4.1–4.2).

Regras de uso (elementos.md, "Orçamento"): 1–2 marcas por peça; espessura 1,5–2× o fio do sistema; 1 cor (a de ação);
na ordem foto → vetor → rabisco. Espessuras: fina = 1,5× · média = 2,4× · grossa = 3,6× ficha.traco.

  traco_mao(pontos, tam, ...)        -> lista de polígonos (o motor; use para qualquer gesto novo)
  sublinhado · circulo · marca_texto · riscado · seta · colchete · asterisco · check · rabisco · chaves
"""
import math

import numpy as np

from .nucleo import amostra, elemento, ruido1d
from .linhas import caminho, rng, claro

FAM = "mao"
PESOS = {"fina": 1.5, "media": 2.4, "grossa": 3.6}
NOTA = "1–2 por peça; cor de ação; por cima da foto e do vetor"


# ================================================================ motor de traço
def _cr(ctrl, n=24, fechado=False):
    """Catmull-Rom denso pelos pontos de controle."""
    P = np.asarray(ctrl, float)
    if fechado:
        P = np.vstack([P[-1], P, P[0], P[1]])
    else:
        P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2][None])
    return np.vstack(out)


def _quebrada(pts, n=10, bojo=0.0, r=None):
    """Polilinha com cantos vivos (segmentos levemente arqueados): para colchete, check, estrela, cabeça de seta."""
    out = []
    P = np.asarray(pts, float)
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        t = np.linspace(0, 1, n, endpoint=False)[:, None]
        seg = a + (b - a) * t
        if bojo:
            d = b - a
            nrm = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
            k = bojo * (r.uniform(0.4, 1.0) if r else 1.0)
            seg = seg + nrm * (np.hypot(*d) * k * 4 * t * (1 - t))
        out.append(seg)
    out.append(P[-1][None])
    return np.vstack(out)


def _canto(P, raio):
    """Arredonda cantos vivos de uma polilinha com raio ~`raio` px (reamostra a 1,5 px + média móvel)."""
    Q = _reamostra(P, 1.5)
    k = max(1, int(raio / 1.5))
    S = _media(Q, k)
    S[0], S[-1] = Q[0], Q[-1]
    return S


def _reamostra(P, passo):
    P = np.asarray(P, float)
    d = np.hypot(*np.diff(P, axis=0).T)
    P = np.vstack([P[0], P[1:][d > 1e-6]])
    d = np.hypot(*np.diff(P, axis=0).T)
    s = np.concatenate([[0], np.cumsum(d)])
    m = max(3, int(s[-1] / passo) + 1)
    t = np.linspace(0, s[-1], m)
    return np.stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])], 1)


def _media(v, k):
    if k < 2:
        return v
    ker = np.ones(k) / k
    pad = np.pad(v, ((k // 2, k - 1 - k // 2),) + ((0, 0),) * (v.ndim - 1), mode="edge")
    if v.ndim == 1:
        return np.convolve(pad, ker, "valid")
    return np.stack([np.convolve(pad[:, j], ker, "valid") for j in range(v.shape[1])], 1)


def traco_mao(pontos, tam, afinar=0.42, ini=1.6, fim=7.0, pouso=0.10, ponta=0.10, tremor=0.14, curva_k=0.30,
              seed=0, suaviza=3):
    """Linha central → polígono do traço com pressão (perfect-freehand em Python).
    tam = diâmetro nominal; afinar = quanto a pressão muda a largura; ini/fim = comprimento das pontas em múltiplos de
    tam; pouso = gota do pouso da caneta; ponta = largura mínima na saída (fração); tremor = variação de pressão."""
    P = _reamostra(pontos, max(0.7, tam / 5))
    suaviza = max(suaviza, 5)          # caneta redonda: canto vivo vira curva de raio ~½ traço (sem "lasca" no contorno)
    if len(P) > 2 * suaviza:
        Q = _media(P, suaviza)
        Q[0], Q[-1] = P[0], P[-1]
        P = Q
    n = len(P)
    d = np.hypot(*np.diff(P, axis=0).T)
    s = np.concatenate([[0], np.cumsum(d)])
    L = max(s[-1], 1e-6)
    T = np.gradient(P, axis=0)
    T /= (np.hypot(T[:, 0], T[:, 1])[:, None] + 1e-9)
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    ang = np.unwrap(np.arctan2(T[:, 1], T[:, 0]))
    kap = np.abs(np.gradient(ang)) / (np.gradient(s) + 1e-9)
    kn = _media(np.clip(kap * tam * 2.2, 0, 1), max(1, int(2 * tam / max(0.7, tam / 5))))
    r = np.random.default_rng(seed)
    import random as _r
    rr = _r.Random(int(r.integers(1 << 30)))
    noi = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, 64), ruido1d(rr, 64, 3))
    p = np.clip(0.5 + tremor * noi + curva_k * kn, 0, 1)
    w = tam * (1 - afinar + 2 * afinar * p)
    T0, T1 = min(ini * tam, 0.35 * L), min(fim * tam, 0.55 * L)
    e = lambda t: 1 - (1 - np.clip(t, 0, 1)) ** 2  # noqa: E731
    w *= (0.45 + 0.55 * e(s / max(T0, 1e-6))) * (ponta + (1 - ponta) * e((L - s) / max(T1, 1e-6)))
    w *= 1 + pouso * np.exp(-(s / (tam * 1.2)) ** 2)
    w = np.maximum(w, tam * 0.06)
    Lf, Rt = P + N * w[:, None] / 2, P - N * w[:, None] / 2
    th = np.linspace(0, math.pi, 9)[1:-1, None]
    cap_f = P[-1] + (N[-1] * np.cos(th) + T[-1] * np.sin(th)) * w[-1] / 2
    cap_i = P[0] + (-N[0] * np.cos(th) - T[0] * np.sin(th)) * w[0] / 2
    return [np.vstack([Lf, cap_f, Rt[::-1], cap_i])]


def _path(poligonos):
    import pathops
    p = pathops.Path()
    for poly in poligonos:
        poly = np.asarray(poly)
        if len(poly) < 3:
            continue
        p.moveTo(*map(float, poly[0]))
        for q in poly[1:]:
            p.lineTo(*map(float, q))
        p.close()
    p.fillType = pathops.FillType.WINDING
    p.simplify()
    return p


def uniao(poligonos, menos=None):
    """União (regra nonzero) dos polígonos → contornos limpos (skia-pathops); `menos` = polígonos a subtrair."""
    import pathops
    p = _path(poligonos)
    if menos:
        p = pathops.op(p, _path(menos), pathops.PathOp.DIFFERENCE)
    out, cur = [], []
    for verb, pts in p.segments:
        if verb == "moveTo":
            cur = [pts[0]]
        elif verb in ("lineTo", "qCurveTo", "curveTo"):
            cur.append(pts[-1])
        elif verb in ("closePath", "endPath"):
            if len(cur) > 2:
                out.append(cur)
            cur = []
    return out


def _peca(camadas, nome, nota=NOTA, pad=None, fam=FAM):
    """camadas = [(polígonos, cor, opac)] → Elemento com viewBox justo (folga = pad) e caixa da tinta."""
    todos = [np.asarray(c) for cam in camadas for c in cam[0]]
    allp = np.vstack(todos)
    x0, y0 = allp.min(0)
    x1, y1 = allp.max(0)
    pad = pad if pad is not None else max(6.0, 0.04 * max(x1 - x0, y1 - y0))
    ox, oy = pad - x0, pad - y0
    W, H = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    corpo = ""
    for camada in camadas:
        polys, cor, op = camada[:3]
        menos = camada[3] if len(camada) > 3 else None
        cont = uniao([np.asarray(c) + (ox, oy) for c in polys],
                     [np.asarray(c) + (ox, oy) for c in menos] if menos else None)
        d = "".join(caminho(c, True) for c in cont)
        corpo += f'<path d="{d}" fill="{cor}"' + (f' fill-opacity="{op:.3g}"' if op < 1 else "") + "/>"
    return elemento(W, H, corpo, nome, fam, caixa=(pad, pad, W - pad, H - pad), nota=nota)


def _orienta(P):
    """Polígono cheio no mesmo sentido dos traços (área negativa) — senão a regra nonzero cancela a sobreposição."""
    P = np.asarray(P, float)
    a = np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])
    return P[::-1] if a > 0 else P


def _rot(P, ang, c=(0, 0)):
    a = math.radians(ang)
    P = np.asarray(P, float) - c
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return P @ R.T + c


def _tam(f, peso):
    return f.traco * (PESOS[peso] if isinstance(peso, str) else peso)


# ================================================================ marcas
def sublinhado(f, larg=560, peso="media", estilo="simples", cor=None, seed=0):
    """Sublinhado à mão. estilo: simples · duplo · onda · volta · vaievolta · arco."""
    r = rng(f, "sub", estilo, seed)
    tam, L = _tam(f, peso), larg
    j = lambda k=0.004: r.gauss(0, k * L)  # noqa: E731
    traços = []
    if estilo in ("simples", "duplo", "arco"):
        sag = 0.045 * L if estilo == "arco" else 0.006 * L
        xs = [0, .26, .52, .78, 1.0]
        ys = [0.004 * L, sag * 0.9, sag, sag * 0.55 - 0.004 * L, -0.02 * L]
        if estilo == "arco":
            ys = [-0.01 * L, sag * 0.8, sag, sag * 0.75, -0.018 * L]
        ctrl = [(x * L + j(.006), y + j()) for x, y in zip(xs, ys)]
        traços.append(dict(P=_cr(ctrl), fim=8))
        if estilo == "duplo":
            dy = 2.9 * tam
            ctrl2 = [(L * (.07 + .86 * x) + j(.006), y + dy + j() + 0.006 * L * x) for x, y in zip(xs, ys)]
            traços.append(dict(P=_cr(ctrl2), fim=7, ini=1.2))
    elif estilo == "onda":
        n = 4.5
        xs = np.linspace(0, L, int(n * 8) + 1)
        A = max(1.7 * tam, 0.02 * L)
        fase = np.cumsum(np.full(len(xs), 2 * math.pi * n / (len(xs) - 1)) * (1 + 0.06 * np.sin(np.arange(len(xs)) / 5)))
        ys = A * np.sin(fase) * (1 - 0.25 * xs / L) - 0.012 * L * xs / L
        traços.append(dict(P=_cr(list(zip(xs, ys)), 6), fim=6))
    elif estilo == "volta":
        ctrl = [(0, 0), (L * .35, .01 * L + j()), (L * .7, .004 * L + j()), (L * .955, -.012 * L), (L * .995, -.004 * L),
                (L * .95, .03 * L), (L * .7, .05 * L + j()), (L * .4, .058 * L + j())]
        traços.append(dict(P=_cr(ctrl), fim=12, suaviza=5))
    elif estilo == "vaievolta":
        h = max(3.4 * tam, 0.04 * L)
        ctrl = [(0, 0), (L * .5, h * .2 + j()), (L * .97 + j(.01), -h * .1), (L * 1.0, h * 0.55),
                (L * .55, h * 1.15 + j()), (L * .05 + j(.01), h * 1.4), (L * .03, h * 2.05),
                (L * .5, h * 2.35 + j()), (L * .9 + j(.01), h * 2.2)]
        traços.append(dict(P=_cr(ctrl, 30), fim=7, suaviza=5))
    polys = []
    for k, t in enumerate(traços):
        polys += traco_mao(t["P"], tam * (0.88 if k else 1), ini=t.get("ini", 1.6), fim=t.get("fim", 7),
                           seed=r.randrange(1 << 30), suaviza=t.get("suaviza", 3))
    polys = [_rot(p, r.uniform(-1.6, 0.4)) for p in polys]
    return _peca([(polys, cor or f.acento, 1)], f"sublinhado · {estilo} · {peso}",
                 "sob a palavra-chave; largura = a da palavra +4–8%; " + NOTA)


def circulo(f, w=440, h=180, peso="media", estilo="oval", cor=None, seed=0):
    """Círculo/oval de destaque que NÃO fecha certinho. estilo: oval · circulo · duplo · aberto · rabiscado · caixa."""
    r = rng(f, "circ", estilo, seed)
    tam = _tam(f, peso)
    if estilo == "caixa":
        jx, jy = lambda: r.gauss(0, 0.008 * w), lambda: r.gauss(0, 0.025 * h)  # noqa: E731
        c = [(w * .07, 0.02 * h + jy()), (w + jx(), jy()), (w + jx() + 0.006 * w, h + jy()), (jx(), h + jy()),
             (jx() - 0.004 * w, jy() - 0.01 * h), (w * .26 + jx(), -0.035 * h + jy())]
        P = _canto(_quebrada(c, 24, 0.012, r), max(3.0, 1.2 * tam))
        polys = traco_mao(P, tam, fim=7, ini=1.2, curva_k=0.5, seed=r.randrange(1 << 30), suaviza=1)
        polys = [_rot(p, r.uniform(-1.5, 1.5)) for p in polys]
        return _peca([(polys, cor or f.acento, 1)], f"caixa à mão · {peso}", "contorna 1 bloco (preço, data); " + NOTA)
    voltas = {"oval": 1.2, "circulo": 1.17, "duplo": 1.95, "aberto": 0.86, "rabiscado": 2.6}[estilo]
    a, b = w / 2, (h / 2 if estilo != "circulo" else w / 2)
    m = int(260 * voltas)
    th0 = math.radians(r.uniform(-70, -42))
    th = th0 - np.linspace(0, 2 * math.pi * voltas, m)
    prog = np.linspace(0, 1, m)
    rr = __import__("random").Random(r.randrange(1 << 30))
    noi = np.interp(prog, np.linspace(0, 1, 40), ruido1d(rr, 40, 2))
    amp = 0.06 if estilo == "rabiscado" else 0.032
    drift = {"duplo": 0.14, "rabiscado": 0.16, "aberto": 0.03}.get(estilo, 0.13)
    ovo = 0.055 * np.cos(th - r.uniform(0, 6.28))
    k = 1 + amp * noi + drift * (prog - 0.5) + ovo
    topo = np.where(np.sin(th) < 0, 0.93, 1.0)          # o alto do oval sai mais achatado (gesto rápido)
    x = a * k * np.cos(th) + 0.035 * a * prog
    y = b * k * np.sin(th) * topo + 0.07 * b * prog
    if estilo == "rabiscado":
        x += 0.05 * a * np.sin(th * 2.3 + 1)
    P = np.stack([x, y], 1)
    P = _rot(P, r.uniform(-5, 3))
    polys = traco_mao(P, tam, fim=11, ini=1.3, seed=r.randrange(1 << 30), tremor=0.18)
    return _peca([(polys, cor or f.acento, 1)], f"{'círculo' if estilo == 'circulo' else 'oval'} · {estilo} · {peso}",
                 "envolve 1 palavra/número com sobra de 8–15%; " + NOTA)


def marca_texto(f, larg=520, alt=58, estilo="seco", cor=None, opac=1.0, passes=1, ang=-1.2, seed=0):
    """Marca-texto de ponta chanfrada: faixa de largura constante, ponta cortada em ângulo, rajadas secas no fim.
    estilo: seco (opaco, para fundo escuro, texto em sobre_acento por cima) · translucido (papel, 40–50%)."""
    r = rng(f, "mt", estilo, seed, larg, alt)
    camadas = []
    for ps in range(passes):
        chan = math.tan(math.radians(r.uniform(12, 20)))       # ponta chanfrada: a mesma inclinação no início e no fim
        bojo = r.gauss(0, 0.005 * larg)
        dy0 = ps * alt * 0.45
        xL = (larg * (0.04 if ps else 0)) + r.gauss(0, 2)
        n = 64
        t = np.linspace(0, 1, n)
        onda = bojo * 4 * t * (1 - t)
        rr = __import__("random").Random(r.randrange(1 << 30))
        b1 = np.interp(t, np.linspace(0, 1, 24), ruido1d(rr, 24, 3)) * 0.5
        b2 = np.interp(t, np.linspace(0, 1, 24), ruido1d(rr, 24, 3)) * 0.5
        x1 = larg * (1 - 0.03 * ps)
        topo = np.stack([xL + t * (x1 - xL), -alt / 2 + onda + b1 + dy0], 1)
        base = np.stack([xL + alt * chan + t * (x1 - xL), alt / 2 + onda + b2 + dy0], 1)
        # fim seco: cada "fio" de feltro termina num ponto (pente), alguns antes
        k = max(6, int(alt / 5))
        pente = []
        for i in range(k + 1):
            yy = -alt / 2 + i * alt / k
            fx = x1 + (yy + alt / 2) * chan + r.gauss(0, 1.0) - (r.uniform(0.01, 0.05) * larg if r.random() < 0.3 else 0)
            pente.append((fx, yy + onda[-1] + dy0))
            if i < k:
                pente.append((fx - r.uniform(1.0, 3.0) * (1 if estilo == "seco" else 0.5),
                              yy + alt / k / 2 + onda[-1] + dy0))
        poly = np.vstack([topo, np.asarray(pente[1:-1]), base[::-1]])
        menos = []
        if estilo == "seco":                                   # riscos secos: o feltro falha no fim do gesto
            for _ in range(r.randint(2, 3) if alt < 40 else r.randint(3, 6)):
                yy = r.uniform(-alt / 2 + 3, alt / 2 - 3) + dy0
                xa = larg * r.uniform(0.7, 0.9)
                xb = x1 + (yy - dy0 + alt / 2) * chan + 4
                lw = r.uniform(0.7, 1.8)
                menos.append(np.array([(xa, yy), (xb, yy - lw), (xb, yy + lw)]) + (0, onda[-1] * 0.5))
        poly = _rot(poly, ang)
        menos = [_rot(m_, ang) for m_ in menos]
        camadas.append(([poly], cor or f.acento, opac, menos))
    el = _peca(camadas, f"marca-texto · {estilo}" + (f" · {passes} passadas" if passes > 1 else ""),
               "atrás de 1 linha; altura = 1,1× a altura-x (ou ½ = 'meia-faixa'); " + NOTA, pad=4)
    return el


def riscado(f, larg=480, alt=120, peso="media", estilo="simples", cor=None, seed=0):
    """Riscado/rasura. estilo: simples · duplo · ondulado · rasura · x · diagonal."""
    r = rng(f, "risc", estilo, seed)
    tam, L = _tam(f, peso), larg
    j = lambda k=0.005: r.gauss(0, k * L)  # noqa: E731
    tr = []
    if estilo in ("simples", "duplo"):
        tr.append(_cr([(0, 0.01 * L), (L * .35, j()), (L * .7, -0.012 * L + j()), (L, -0.03 * L + j())]))
        if estilo == "duplo":
            tr.append(_cr([(L * .04, 0.04 * L), (L * .4, 0.025 * L + j()), (L * .75, 0.012 * L + j()),
                           (L * .98, -0.008 * L)]))
    elif estilo == "ondulado":
        xs = np.linspace(0, L, 25)
        tr.append(_cr(list(zip(xs, 0.025 * L * np.sin(xs / L * 2 * math.pi * 2.2 + 0.5) - 0.02 * xs))))
    elif estilo == "rasura":
        n = int(L / (tam * 2.3))
        incl = alt * 0.32
        pts = []
        for i in range(n + 1):
            top = (i % 2 == 0)
            x = i * L / n + (incl if top else 0) + r.gauss(0, tam * 0.5)
            y = (-alt / 2 if top else alt / 2) * r.uniform(0.82, 1.0)
            pts.append((x, y))
        P = _media(_cr(pts, 12), 3)
        tr.append(_rot(P, r.uniform(-2.5, 0)))
    elif estilo == "x":
        tr.append(_quebrada([(0, 0), (L + j(), alt + j())], 30, 0.02, r))
        tr.append(_quebrada([(L * 0.98 + j(), -0.01 * L), (L * 0.02, alt * 1.02 + j())], 30, -0.02, r))
    elif estilo == "diagonal":
        tr.append(_quebrada([(0, alt), (L, 0)], 30, 0.025, r))
    polys = []
    for i, P in enumerate(tr):
        polys += traco_mao(P, tam * (0.9 if i else 1), fim=5, seed=r.randrange(1 << 30),
                           suaviza=1 if estilo == "rasura" else 3)
    return _peca([(polys, cor or f.acento, 1)], f"riscado · {estilo} · {peso}",
                 "risca o preço antigo/o 'não'; nunca o que precisa ser lido; " + NOTA)


def _cabeca(P, tam, r, tipo="aberta", ang=28.0, comp=None):
    """Cabeça da seta no fim da linha central P (devolve polígonos)."""
    P = np.asarray(P)
    d = np.hypot(*np.diff(P, axis=0).T)
    s = np.concatenate([[0], np.cumsum(d)])
    L = s[-1]
    hl = comp or float(np.clip(0.16 * L, 4.8 * tam, 13 * tam))
    k = np.searchsorted(s, L - max(2.5 * tam, hl * 0.5))
    tip = P[-1]
    v = tip - P[min(k, len(P) - 2)]
    v /= (np.hypot(*v) + 1e-9)
    a1, a2 = math.radians(ang + r.uniform(-4, 4)), math.radians(ang + r.uniform(-4, 4))
    rot = lambda v, a: np.array([v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a)])  # noqa
    b1 = tip - rot(v, a1) * hl * r.uniform(0.9, 1.08)
    b2 = tip - rot(v, -a2) * hl * r.uniform(0.82, 1.0)
    if tipo == "cheia":
        base = (b1 + b2) / 2 + v * hl * 0.12
        poly = np.vstack([_quebrada([b1, tip], 8, 0.015, r), _quebrada([tip, b2], 8, 0.015, r),
                          _quebrada([b2, base, b1], 6, 0.0, r)])
        return [_orienta(poly)] + traco_mao(np.vstack([b1, tip, b2, base, b1]), tam * 0.6, afinar=0.05, ini=0.3, fim=0.3,
                                  ponta=0.9, pouso=0, seed=r.randrange(1 << 30), suaviza=1)
    if tipo == "meia":
        return traco_mao(_quebrada([tip, b1], 12, 0.02, r), tam * 0.92, ini=0.6, fim=2.5, seed=r.randrange(1 << 30),
                         suaviza=1)
    V = np.vstack([_quebrada([b1, tip], 14, 0.03, r), _quebrada([tip, b2], 14, -0.03, r)])
    return traco_mao(V, tam * 0.92, ini=0.8, fim=2.8, pouso=0.1, curva_k=0.5, seed=r.randrange(1 << 30), suaviza=2)


def seta(f, estilo="curva", w=420, h=220, peso="media", cabeca="aberta", cor=None, seed=0):
    """Seta à mão (corpo + cabeça). estilo: curva · s · laco · reta · gancho · curta · dupla · volta."""
    r = rng(f, "seta", estilo, seed, cabeca)
    tam = _tam(f, peso)
    j = lambda k=0.02: r.gauss(0, k * min(w, h))  # noqa: E731
    forma = {
        "curva": [(0, h * .95), (w * .16, h * .5), (w * .48, h * .16), (w * .97, h * .08)],
        "s": [(0, h * .2), (w * .28, h * .02), (w * .52, h * .45), (w * .74, h * .92), (w, h * .72)],
        "laco": [(0, h * .82), (w * .3, h * .78), (w * .56, h * .45), (w * .5, h * .1), (w * .32, h * .22),
                 (w * .38, h * .6), (w * .66, h * .76), (w, h * .55)],
        "reta": [(0, h * .62), (w * .5, h * .42), (w, h * .3)],
        "gancho": [(0, h * .3), (w * .42, h * .02), (w * .82, h * .18), (w * .96, h * .58), (w * .84, h * .98)],
        "curta": [(0, h * .7), (w * .55, h * .5), (w, h * .2)],
        "dupla": [(0, h * .7), (w * .3, h * .25), (w * .7, h * .22), (w, h * .65)],
        "volta": None,
    }[estilo]
    if estilo == "volta":
        th = np.linspace(math.radians(160), math.radians(160 - 290), 120)
        rr = 0.5 * min(w, h)
        P = np.stack([rr * np.cos(th) * (1 + 0.05 * np.linspace(0, 1, 120)), rr * np.sin(th)], 1)
    else:
        P = _cr([(x + j(), y + j()) for x, y in forma], 28)
    polys = traco_mao(P, tam, ini=1.4, fim=3.0, ponta=0.35, seed=r.randrange(1 << 30))
    polys += _cabeca(P, tam, r, cabeca)
    if estilo == "dupla":
        polys += _cabeca(P[::-1], tam, r, cabeca)
    return _peca([(polys, cor or f.acento, 1)], f"seta · {estilo} · {cabeca}",
                 "liga a chamada ao objeto (da esquerda p/ a direita); " + NOTA)


def colchete(f, estilo="lateral", w=60, h=300, peso="media", cor=None, seed=0):
    """Colchetes e cantos à mão. estilo: lateral · par · inferior · cantos · duplo."""
    r = rng(f, "colch", estilo, seed)
    tam = _tam(f, peso)
    j = lambda k=1.0: r.gauss(0, k * tam * 0.35)  # noqa: E731
    tr = []
    if estilo == "lateral":
        tr.append(_quebrada([(w + j(), j()), (j(), j()), (j(), h + j()), (w * 1.05 + j(), h + j())], 14, 0.01, r))
    elif estilo == "par":
        W, a = w, 0.2 * h
        tr.append(_quebrada([(a + j(), j()), (j(), j()), (j(), h + j()), (a * 1.05 + j(), h + j())], 14, 0.01, r))
        tr.append(_quebrada([(W - a + j(), j()), (W + j(), j()), (W + j(), h + j()), (W - a * 1.05 + j(), h + j())],
                            14, 0.01, r))
    elif estilo == "inferior":
        tr.append(_quebrada([(j(), -h), (j(), j()), (w + j(), j(2)), (w + j(), -h * 0.9 + j())], 16, 0.006, r))
    elif estilo == "cantos":
        a = 0.16 * min(w, h)
        for cx, cy, sx, sy in ((0, 0, 1, 1), (w, 0, -1, 1), (w, h, -1, -1), (0, h, 1, -1)):
            tr.append(_quebrada([(cx + j(), cy + sy * a + j()), (cx + j(), cy + j()), (cx + sx * a * 1.1 + j(), cy + j())],
                                12, 0.02, r))
    elif estilo == "duplo":
        tr.append(_quebrada([(j(), j()), (j(), h + j())], 30, 0.006, r))
        tr.append(_quebrada([(tam * 2.4 + j(), h * .04 + j()), (tam * 2.4 + j(), h * .96 + j())], 30, -0.006, r))
    polys = []
    for P in tr:
        polys += traco_mao(P, tam, ini=1.0, fim=2.2, ponta=0.4, curva_k=0.45, seed=r.randrange(1 << 30), suaviza=3)
    return _peca([(polys, cor or f.acento, 1)], f"colchete · {estilo} · {peso}",
                 "agrupa linhas / marca o trecho que importa; " + NOTA)


def asterisco(f, estilo="tres", R=60, peso="media", cor=None, seed=0):
    """Asteriscos, estrela de um traço, brilho e tracinhos de ênfase. estilo: tres · quatro · estrela · brilho · enfase · leque."""
    r = rng(f, "ast", estilo, seed)
    tam = _tam(f, peso)
    polys = []
    if estilo in ("tres", "quatro"):
        n = 3 if estilo == "tres" else 4
        a0 = r.uniform(-10, 10)
        for i in range(n):
            a = math.radians(90 + a0 + i * 180 / n + r.uniform(-7, 7))
            l1, l2 = R * r.uniform(0.85, 1.08), R * r.uniform(0.85, 1.08)
            c = np.array([r.gauss(0, R * 0.05), r.gauss(0, R * 0.05)])
            v = np.array([math.cos(a), math.sin(a)])
            polys += traco_mao(_quebrada([c - v * l1, c + v * l2], 20, 0.02, r), tam, ini=1.0, fim=2.6,
                               seed=r.randrange(1 << 30))
    elif estilo == "estrela":
        vs = []
        for k in range(6):
            a = math.radians(-90 + 144 * k + 162 + r.uniform(-5, 5))
            rr = R * r.uniform(0.9, 1.06)
            vs.append((rr * math.cos(a), rr * math.sin(a)))
        vs[-1] = (vs[-1][0] + R * 0.12, vs[-1][1] - R * 0.08)
        P = _media(_quebrada(vs, 18, 0.012, r), 3)
        polys += traco_mao(P, tam, ini=1.2, fim=4, curva_k=0.5, seed=r.randrange(1 << 30), suaviza=1)
    elif estilo == "brilho":
        # brilho de 4 pontas com lados côncavos, desenhado cheio (marcador), pontas desiguais
        for (cx, cy, s) in ((0, 0, 1.0), (R * 0.95, -R * 0.75, 0.38)):
            ry, rx = R * s * r.uniform(0.95, 1.05), R * s * r.uniform(0.58, 0.68)
            tips = [np.array(p) for p in ((0, -ry), (rx, 0), (0, ry * r.uniform(0.85, 0.95)), (-rx * r.uniform(0.9, 1), 0))]
            pts = []
            for i in range(4):
                A, B = tips[i], tips[(i + 1) % 4]
                C = (A + B) / 2 * r.uniform(0.1, 0.18)
                t = np.linspace(0, 1, 18, endpoint=False)[:, None]
                pts.append((1 - t) ** 2 * A + 2 * (1 - t) * t * C + t ** 2 * B)
            poly = _rot(np.vstack(pts), r.uniform(-6, 6)) + (cx, cy)
            polys.append(_orienta(poly))
    elif estilo in ("enfase", "leque"):
        angs = [-75, -45, -15] if estilo == "enfase" else [-150, -120, -90, -60, -30]
        for a in angs:
            a = math.radians(a + r.uniform(-6, 6))
            v = np.array([math.cos(a), math.sin(a)])
            r0, l = R * r.uniform(0.45, 0.55), R * r.uniform(0.5, 0.75)
            polys += traco_mao(_quebrada([v * r0, v * (r0 + l)], 14, 0.02, r), tam, ini=1.0, fim=2.5,
                               seed=r.randrange(1 << 30))
    nomes = {"tres": "asterisco · 3 traços", "quatro": "asterisco · 4 traços", "estrela": "estrela de 1 traço",
             "brilho": "brilho de 4 pontas", "enfase": "ênfase · 3 tracinhos", "leque": "ênfase · leque"}
    return _peca([(polys, cor or f.acento, 1)], f"{nomes[estilo]} · {peso}",
                 "chama o olho para 1 canto/1 número; nunca mais de 1; " + NOTA)


def check(f, estilo="check", w=120, h=110, peso="media", cor=None, seed=0):
    """Check e X à mão. estilo: check · longo · x · caixa."""
    r = rng(f, "chk", estilo, seed)
    tam = _tam(f, peso)
    j = lambda k=0.03: r.gauss(0, k * w)  # noqa: E731
    polys = []
    if estilo in ("check", "longo"):
        if estilo == "check":
            pts = [(0 + j(), h * .55 + j()), (w * .36 + j(), h + j()), (w * .62, h * .45), (w + j(), j())]
            P = np.vstack([_quebrada(pts[:2], 14, 0.02, r), _cr(pts[1:], 16)])
        else:
            pts = [(0, h * .62), (w * .26, h), (w * .6, h * .5), (w * 1.25, h * .02), (w * 1.6, -h * .12)]
            P = np.vstack([_quebrada(pts[:2], 14, 0.02, r), _cr([(x + j(), y + j()) for x, y in pts[1:]], 20)])
        polys += traco_mao(P, tam, ini=1.0, fim=6, curva_k=0.6, seed=r.randrange(1 << 30), suaviza=2)
    elif estilo == "x":
        polys += traco_mao(_quebrada([(j(), j()), (w + j(), h + j())], 30, 0.03, r), tam, fim=3,
                           seed=r.randrange(1 << 30))
        polys += traco_mao(_quebrada([(w + j(), j()), (j(), h + j())], 30, -0.03, r), tam * 0.92, fim=3,
                           seed=r.randrange(1 << 30))
    elif estilo == "caixa":
        s = w * 0.78
        bx = [(j(), j()), (s + j(), j()), (s + j(), s + j()), (j(), s + j()), (j(), j() + s * 0.06)]
        polys += traco_mao(_media(_quebrada(bx, 16, 0.01, r), 3), tam * 0.62, ini=0.8, fim=1.5,
                           seed=r.randrange(1 << 30), suaviza=1)
        pts = [(s * .18, s * .5), (s * .45, s * .82), (s * .75, s * .2), (s * 1.12, -s * .3)]
        P = np.vstack([_quebrada(pts[:2], 12, 0.02, r), _cr(pts[1:], 16)])
        polys += traco_mao(P, tam, ini=1.0, fim=5, curva_k=0.6, seed=r.randrange(1 << 30), suaviza=2)
    return _peca([(polys, cor or f.acento, 1)], f"{'X' if estilo == 'x' else 'check'} · {estilo} · {peso}",
                 "lista do que entra/não entra; 1 marca por item; " + NOTA)


def rabisco(f, estilo="espiral", w=300, h=120, peso="fina", cor=None, seed=0):
    """Rabiscos de atenção. estilo: espiral · lacadas · zigue · bola · mola · risquinhos · ondinha."""
    r = rng(f, "rab", estilo, seed)
    tam = _tam(f, peso)
    rr = __import__("random").Random(r.randrange(1 << 30))
    polys = []
    if estilo == "espiral":
        t = np.linspace(0, 2 * math.pi * 3.2, 420)
        u = t / t[-1]
        noi = np.interp(u, np.linspace(0, 1, 40), ruido1d(rr, 40, 3))
        rad = (0.06 + 0.94 * u ** 0.8) * h / 2 * (1 + 0.14 * noi)
        P = np.stack([rad * np.cos(-t) * 1.22 + 0.08 * h * u, rad * np.sin(-t) + 0.05 * h * u], 1)
        polys += traco_mao(_rot(P, r.uniform(-10, 10)), tam, fim=8, seed=r.randrange(1 << 30), tremor=0.2)
    elif estilo in ("lacadas", "mola"):
        n = 6 if estilo == "lacadas" else 9
        t = np.linspace(0, 2 * math.pi * n, 70 * n)
        noi = np.interp(t / t[-1], np.linspace(0, 1, 50), ruido1d(rr, 50, 2))
        a = w / (2 * math.pi * n)
        if estilo == "lacadas":
            x = a * t - a * 1.9 * np.sin(t)
            x = x + a * 0.5 * noi
            y = -h * 0.42 * np.cos(t) * (1 + 0.18 * noi) + h * 0.3 * (1 - np.cos(t)) * 0.2
        else:
            x = a * t + a * 2.2 * np.cos(t)
            y = h * 0.4 * np.sin(t) * (1 + 0.08 * noi)
        polys += traco_mao(np.stack([x, y], 1), tam, fim=6, seed=r.randrange(1 << 30))
    elif estilo == "zigue":
        n = 9
        pts = [(i * w / n + r.gauss(0, w * 0.012) + (h * 0.18 if i % 2 == 0 else 0),
                (h / 2 if i % 2 else -h / 2) * r.uniform(0.62, 1.0)) for i in range(n + 1)]
        polys += traco_mao(_quebrada(pts, 10, 0.02, r), tam, fim=4, curva_k=0.5, seed=r.randrange(1 << 30), suaviza=2)
    elif estilo == "bola":
        t = np.linspace(0, 2 * math.pi * 5.5, 1100)
        u = t / t[-1]
        n1, n2, n3, n4 = (np.interp(u, np.linspace(0, 1, 30), ruido1d(rr, 30, 2)) for _ in range(4))
        cx, cy = 0.14 * w * n1, 0.14 * h * n2
        rx, ry = w / 2 * (0.72 + 0.22 * n3), h / 2 * (0.72 + 0.22 * n4)
        ph = 0.9 * n1 + 0.4 * n3
        x = cx + rx * np.cos(-t) * np.cos(ph) - ry * np.sin(-t) * np.sin(ph)
        y = cy + rx * np.cos(-t) * np.sin(ph) + ry * np.sin(-t) * np.cos(ph)
        polys += traco_mao(np.stack([x, y], 1), tam, fim=8, seed=r.randrange(1 << 30))
    elif estilo == "risquinhos":
        for i in range(6):
            x = i * w / 6 + r.gauss(0, 2)
            polys += traco_mao(_quebrada([(x + h * .3, -h / 2 + r.gauss(0, 3)), (x - h * .1, h / 2 + r.gauss(0, 3))],
                                         14, 0.03, r), tam, ini=0.8, fim=2, seed=r.randrange(1 << 30))
    elif estilo == "ondinha":
        x = np.linspace(0, w, 80)
        y = h * 0.28 * np.sin(x / w * 2 * math.pi * 2.5) * (1 + 0.1 * np.sin(x / 40))
        polys += traco_mao(np.stack([x, y], 1), tam, fim=5, seed=r.randrange(1 << 30))
    nomes = {"espiral": "espiral rabiscada", "lacadas": "laçadas", "zigue": "zigue-zague", "bola": "bola de rabisco",
             "mola": "mola", "risquinhos": "risquinhos", "ondinha": "ondinha"}
    return _peca([(polys, cor or f.acento, 1)], f"{nomes[estilo]} · {peso}",
                 "rabisco de atenção ou divisor de voz; tempero, nunca sob texto; " + NOTA)


def chaves(f, estilo="vertical", w=50, h=300, peso="media", cor=None, seed=0):
    """Chaves { } à mão. estilo: vertical · horizontal · par · direita."""
    r = rng(f, "chv", estilo, seed)
    tam = _tam(f, peso)
    j = lambda: r.gauss(0, tam * 0.3)  # noqa: E731

    def brace(h, w):
        c = [(w, 0), (w * .5, h * .03), (w * .45, h * .2), (w * .42, h * .4), (w * .12, h * .485), (0, h * .5)]
        c2 = [(0, h * .5), (w * .12, h * .515), (w * .42, h * .6), (w * .45, h * .8), (w * .5, h * .97), (w, h)]
        c = [(x + j(), y + j()) for x, y in c]
        c2 = [c[-1]] + [(x + j(), y + j()) for x, y in c2[1:]]
        return _canto(np.vstack([_cr(c, 18), _cr(c2, 18)[1:]]), max(4.0, tam * 1.5))
    polys = []
    if estilo in ("vertical", "direita", "par"):
        B = brace(h, w)
        if estilo == "direita":
            B = np.stack([-B[:, 0], B[:, 1]], 1)
        polys += traco_mao(B, tam, ini=1.2, fim=3, ponta=0.25, curva_k=0.5, seed=r.randrange(1 << 30), suaviza=3)
        if estilo == "par":
            B2 = brace(h, w)
            B2 = np.stack([-B2[:, 0] + h * 1.4, B2[:, 1]], 1)
            polys += traco_mao(B2, tam, ini=1.2, fim=3, ponta=0.25, curva_k=0.5, seed=r.randrange(1 << 30), suaviza=3)
    elif estilo == "horizontal":
        B = brace(h, w)
        B = np.stack([B[:, 1], -B[:, 0]], 1)[::-1]
        B = np.stack([B[:, 0], -B[:, 1]], 1)
        polys += traco_mao(B, tam, ini=1.2, fim=3, ponta=0.25, curva_k=0.5, seed=r.randrange(1 << 30), suaviza=3)
    return _peca([(polys, cor or f.acento, 1)], f"chaves · {estilo} · {peso}",
                 "junta itens de uma lista num resumo; ponta aponta para a nota; " + NOTA)


# ================================================================ amostras (catálogo)
@amostra(FAM, "sublinhados")
def _a_sub(f):
    return [sublinhado(f, peso="fina"), sublinhado(f, peso="media", seed=2), sublinhado(f, peso="grossa", seed=3),
            sublinhado(f, estilo="duplo"), sublinhado(f, estilo="onda", peso="fina"),
            sublinhado(f, estilo="volta"), sublinhado(f, estilo="vaievolta", peso="fina"),
            sublinhado(f, estilo="arco", cor=f.tinta),
            claro(sublinhado(f, estilo="simples", peso="media", cor=f.fundo, seed=5))]


@amostra(FAM, "círculos e ovais")
def _a_circ(f):
    return [circulo(f, peso="fina"), circulo(f, seed=3), circulo(f, estilo="circulo", w=260, h=260, peso="grossa"),
            circulo(f, estilo="duplo", peso="fina"), circulo(f, estilo="aberto"),
            circulo(f, estilo="rabiscado", w=360, h=200, peso="fina"),
            circulo(f, estilo="caixa", w=420, h=150), circulo(f, w=620, h=150, cor=f.tinta, seed=8),
            claro(circulo(f, cor=f.fundo, seed=4))]


@amostra(FAM, "marca-texto")
def _a_mt(f):
    return [marca_texto(f), marca_texto(f, larg=300, alt=64, seed=2), marca_texto(f, cor=f.tinta, seed=3),
            marca_texto(f, alt=26, larg=480, estilo="seco", seed=4),
            marca_texto(f, larg=300, alt=30, ang=-90, seed=5),
            claro(marca_texto(f, estilo="translucido", opac=0.45)),
            claro(marca_texto(f, estilo="translucido", opac=0.4, passes=2, seed=7)),
            claro(marca_texto(f, estilo="translucido", opac=0.5, alt=28, ang=0.6, seed=8))]


@amostra(FAM, "riscados")
def _a_risc(f):
    return [riscado(f, peso="fina"), riscado(f), riscado(f, estilo="duplo"), riscado(f, estilo="ondulado"),
            riscado(f, estilo="rasura", larg=380, alt=90, peso="fina"), riscado(f, estilo="x", larg=260, alt=200),
            riscado(f, estilo="diagonal", larg=300, alt=180, cor=f.tinta),
            claro(riscado(f, estilo="simples", peso="grossa", cor=f.fundo, seed=3))]


@amostra(FAM, "setas")
def _a_seta(f):
    return [seta(f), seta(f, cabeca="cheia", seed=2), seta(f, "s", w=380, h=260), seta(f, "laco", w=440, h=260),
            seta(f, "reta", w=440, h=120, peso="fina"), seta(f, "gancho", w=300, h=260),
            seta(f, "curta", w=180, h=110, peso="grossa"), seta(f, "dupla", w=460, h=160, peso="fina", cor=f.tinta),
            seta(f, "volta", w=240, h=240), claro(seta(f, "curva", cor=f.fundo, seed=5))]


@amostra(FAM, "colchetes")
def _a_colch(f):
    return [colchete(f), colchete(f, peso="grossa", seed=2), colchete(f, "par", w=440, h=180, peso="fina"),
            colchete(f, "inferior", w=440, h=90), colchete(f, "cantos", w=420, h=260, peso="fina"),
            claro(colchete(f, "cantos", w=360, h=240, cor=f.fundo, seed=3)),     # "duplo" fora: dois traços retos = "||" (pausa)
            colchete(f, "inferior", w=300, h=70, peso="grossa", cor=f.tinta, seed=4)]


@amostra(FAM, "asteriscos e estrelas")
def _a_ast(f):
    return [asterisco(f), asterisco(f, "quatro", R=70), asterisco(f, "estrela", R=90),
            asterisco(f, "estrela", R=90, peso="grossa", cor=f.tinta, seed=3), asterisco(f, "brilho", R=80),
            asterisco(f, "enfase", R=90), asterisco(f, "leque", R=100, peso="fina"),
            claro(asterisco(f, "tres", R=70, cor=f.fundo, seed=4))]


@amostra(FAM, "check e X")
def _a_chk(f):
    return [check(f), check(f, peso="grossa", seed=2), check(f, "longo", w=140), check(f, "x"),
            check(f, "x", peso="grossa", cor=f.tinta, seed=3), check(f, "caixa", w=140),
            check(f, "caixa", w=140, cor=f.tinta, peso="fina", seed=5), claro(check(f, cor=f.fundo, seed=6))]


@amostra(FAM, "rabiscos de atenção")
def _a_rab(f):
    return [rabisco(f), rabisco(f, "lacadas", w=420, h=90), rabisco(f, "zigue", w=360, h=60, peso="media"),
            rabisco(f, "bola", w=200, h=160), rabisco(f, "mola", w=460, h=80, cor=f.tinta),
            rabisco(f, "risquinhos", w=150, h=110, peso="media"), rabisco(f, "ondinha", w=260, h=60, peso="media"),
            claro(rabisco(f, "lacadas", w=420, h=90, cor=f.fundo, seed=3))]


@amostra(FAM, "chaves")
def _a_chv(f):
    return [chaves(f), chaves(f, h=380, seed=2), chaves(f, "direita", h=360, peso="fina"),
            chaves(f, "horizontal", w=46, h=460), chaves(f, "par", w=44, h=200, cor=f.tinta),
            chaves(f, "horizontal", w=40, h=320, peso="fina", seed=4),
            claro(chaves(f, "vertical", h=240, cor=f.fundo, seed=5))]
