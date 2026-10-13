"""ornamentos.pontos — família "PONTOS E CÉLULAS": Voronoi, pontilhado (estipulação de Voronoi ponderada), meio-tom
VETORIAL, dither (Bayer · ruído azul void-and-cluster gerado aqui · Floyd–Steinberg) como pixels vetoriais, grade de
pontos com máscara, mosaico (quadtree, tesselas) e meio-tom de linhas.

Origem (elementos.md, pesquisa 11 E95/E99, pesquisa 13 §1.9 e §8.2 #14–17, pesquisa 4 §5.1): meio-tom com raio
∝ √tom, célula ≥ 12 px num 1080 (senão vira moiré no celular), 45°; Voronoi com 12–60 células numa peça (aqui há
campos maiores para fundo); ruído azul gerado por nós (sem baixar textura); tudo vetor (imprime e escala sem moiré).
Peso: pontos num path só (m dx dy h0 + stroke-linecap round), pixels de dither fundidos em corridas.

  campo_tom(modo, w, h, ...)   tom 0–1 (1 = tinta cheia): linear · radial · esfera · nuvem · faixa · diagonal · borda
  voronoi · pontilhado · meio_tom · dither · grade_pontos · mosaico · meio_tom_linhas
"""
import math
from functools import lru_cache

import numpy as np

from .nucleo import amostra
from .linhas import (semente, rng, nprng, pontos_d, caminho, campo_ruido, fita, traco_attr, _campo, _cheio, _ln,
                     _esp, _ret)

FAM = "pontos"
NOTA = "tempero/fundo; célula ≥ 12 px num 1080; nunca sob texto pequeno; 1 cor (+ acento em 1 detalhe)"


# ================================================================ campos de tom
def campo_tom(modo, w, h, passo=4.0, seed=0, inverte=False, luz=(-0.55, -0.62, 0.56)):
    """Tom 0–1 numa grade (passo em px). esfera: luz de cima-esquerda; inverte=True → tom = sombra (papel claro)."""
    gh, gw = int(h / passo) + 1, int(w / passo) + 1
    yy, xx = np.mgrid[0:gh, 0:gw].astype(float) * passo
    u, v = xx / w, yy / h
    sm = lambda t: np.clip(t, 0, 1) ** 2 * (3 - 2 * np.clip(t, 0, 1))  # noqa: E731
    if modo == "linear":
        t = sm(u * 1.1 - 0.05)
    elif modo == "diagonal":
        t = sm((u + v) / 2 * 1.15 - 0.05)
    elif modo == "radial":
        t = sm(1 - np.hypot(u - 0.5, v - 0.5) / 0.62)
    elif modo == "borda":
        t = sm(np.hypot(u - 0.5, v - 0.5) / 0.62 * 1.25 - 0.25)
    elif modo == "faixa":
        t = np.exp(-((v - 0.5) / 0.18) ** 2)
    elif modo == "esfera":
        R = 0.4 * min(w, h)
        X, Y = (xx - w / 2) / R, (yy - h / 2) / R
        r2 = X ** 2 + Y ** 2
        Z = np.sqrt(np.clip(1 - r2, 0, 1))
        L = np.array(luz) / np.linalg.norm(luz)
        sh = np.clip(X * L[0] + Y * L[1] + Z * L[2], 0, 1) * 0.92 + 0.08
        borda = np.clip((1 - np.sqrt(r2)) / 0.035, 0, 1)            # some em 3,5% do raio (sem degrau no contorno)
        # sobre papel (inverte) o tom é SOMBRA: sem piso, a luz some no papel e a silhueta ganha uma "mordida" (D24);
        # piso de 0,16 = meia-tinta na luz, o contorno da esfera continua inteiro
        tom = np.maximum(1 - sh, 0.16) if inverte else sh
        return np.where(r2 < 1, tom * borda, 0.0)
    elif modo == "nuvem":
        n = campo_ruido(gw, gh, gw / 2.6, 4, seed, warp=3)
        t = sm(n * 0.9 + 0.5)
    else:
        raise ValueError(modo)
    return 1 - t if inverte else t


def _amostra_tom(T, passo, x, y):
    i = np.clip((np.asarray(y) / passo).astype(int), 0, T.shape[0] - 1)
    j = np.clip((np.asarray(x) / passo).astype(int), 0, T.shape[1] - 1)
    return T[i, j]


def _pontos_svg(xy, diam, cor, opac=1.0):
    o = f' stroke-opacity="{opac:.3g}"' if opac < 1 else ""
    return (f'<path d="{pontos_d(xy)}" fill="none" stroke="{cor}" stroke-width="{diam:.2f}" '
            f'stroke-linecap="round"{o}/>') if len(xy) else ""


def _pontos_varios(xy, raios, cor, q=0.25):
    """Pontos de raios variados: agrupa por raio quantizado (q px) → poucos paths."""
    xy, raios = np.asarray(xy), np.asarray(raios)
    out = ""
    k = np.round(raios / q).astype(int)
    for kk in np.unique(k):
        if kk <= 0:
            continue
        sel = k == kk
        out += _pontos_svg(xy[sel], 2 * kk * q, cor)
    return out


# ================================================================ 1. Voronoi
def _sementes(w, h, n, g, dens=None, it=2):
    """n pontos bem espalhados (rejeição pela densidade + relaxamento de Lloyd)."""
    from scipy.spatial import cKDTree
    pts = []
    while len(pts) < n:
        c = g.uniform(0, 1, (n * 3, 2)) * (w, h)
        if dens is not None:
            c = c[g.random(len(c)) < dens(c[:, 0], c[:, 1])]
        pts += list(c)
    pts = np.array(pts[:n])
    gy, gx = np.mgrid[0:h:6, 0:w:6]
    P = np.stack([gx.ravel(), gy.ravel()], 1).astype(float)
    wts = np.ones(len(P)) if dens is None else dens(P[:, 0], P[:, 1])
    for _ in range(it):
        _, lab = cKDTree(pts).query(P)
        sw = np.bincount(lab, wts, n)
        ok = sw > 1e-9
        pts[ok] = np.stack([np.bincount(lab, wts * P[:, 0], n)[ok] / sw[ok],
                            np.bincount(lab, wts * P[:, 1], n)[ok] / sw[ok]], 1)
    return pts


def _celulas(pts, w, h, folga=0.0):
    import shapely
    from shapely.geometry import MultiPoint, box
    caixa = box(-folga, -folga, w + folga, h + folga)
    vor = shapely.voronoi_polygons(MultiPoint([tuple(p) for p in pts]), extend_to=caixa)
    return [g.intersection(caixa) for g in vor.geoms]


def _anel(poly):
    return list(poly.exterior.coords) if poly.geom_type == "Polygon" and not poly.is_empty else []


def voronoi(f, modo="linhas", w=1080, h=1080, n=110, cor=None, k=0.6, seed=0, fundo_claro=False):
    """Voronoi. modo: linhas · seixos (células arredondadas) · gradiente (densidade) · tons · centros · delaunay ·
    craquelado · lente (1 célula no acento, recorte circular)."""
    g = nprng(f, "vor", modo, seed)
    cor = cor or f.tinta
    e = _esp(f, k)
    dens = (lambda x, y: 0.08 + 0.92 * (1 - x / w) ** 2.2) if modo == "gradiente" else None
    pts = _sementes(w, h, n if modo != "gradiente" else int(n * 1.8), g, dens, it=3)
    cells = _celulas(pts, w, h, folga=0 if modo in ("seixos", "craquelado", "tons") else 40)
    corpo, clip = "", _ret(w, h)
    if modo in ("linhas", "gradiente", "centros", "lente"):
        corpo = _ln([_anel(c) for c in cells], cor if modo != "centros" else f.apoio, e, fechadas=True)
        if modo == "centros":
            corpo += _pontos_svg([c.centroid.coords[0] for c in cells], f.traco * 2.2, cor)
        if modo == "lente":
            alvo = min(cells, key=lambda c: c.centroid.distance(__import__("shapely").geometry.Point(w * 0.56, h * 0.44)))
            corpo = _cheio([_anel(alvo)], f.acento) + corpo
            # recorte circular + o próprio aro (fio do mesmo traço): sem ele as arestas terminam no ar, em "galhos"
            rl = min(w, h) / 2 - e
            clip = f'<circle cx="{w / 2}" cy="{h / 2}" r="{rl + e:.2f}"/>'
            corpo += f'<circle cx="{w / 2}" cy="{h / 2}" r="{rl:.2f}" {traco_attr(cor, e)}/>'
    elif modo in ("seixos", "craquelado", "tons"):
        gap = {"seixos": f.unidade * 0.32, "craquelado": f.unidade * 0.12, "tons": 0}[modo]
        rr = f.unidade * 0.55 if modo == "seixos" else 0
        grupos = {}
        for c in cells:
            p = c.buffer(-gap - rr, join_style="mitre").buffer(rr) if gap or rr else c
            if p.is_empty:
                continue
            nivel = 1.0 if modo == "craquelado" else (g.choice([0.07, 0.13, 0.22, 0.34]) if modo == "tons" else
                                                      g.choice([0.16, 0.28, 0.42]))
            grupos.setdefault(nivel, []).append(_anel(p) if p.geom_type == "Polygon" else _anel(max(p.geoms, key=lambda q: q.area)))
        for nivel, polys in grupos.items():
            corpo += _cheio(polys, cor, nivel)
    elif modo == "delaunay":
        from scipy.spatial import Delaunay
        borda = [(x, y) for x in np.linspace(-80, w + 80, 7) for y in (-80, h + 80)] +                 [(x, y) for y in np.linspace(-80, h + 80, 7)[1:-1] for x in (-80, w + 80)]
        P = np.vstack([pts, borda])
        tri = Delaunay(P)
        ares = set()
        for s in tri.simplices:
            for a, b in ((s[0], s[1]), (s[1], s[2]), (s[2], s[0])):
                ares.add((min(a, b), max(a, b)))
        corpo = _ln([[tuple(P[a]), tuple(P[b])] for a, b in ares], cor, e)
        corpo += _pontos_svg(pts, f.traco * 1.8, cor)
    nomes = {"linhas": "Voronoi · células", "seixos": "Voronoi · seixos", "gradiente": "Voronoi · densidade em degradê",
             "tons": "Voronoi · mosaico de tons", "centros": "Voronoi · células + centros", "delaunay": "Delaunay · malha",
             "craquelado": "Voronoi · craquelado", "lente": "Voronoi · lente com 1 célula no acento"}
    return _campo(w, h, corpo, nomes[modo], "premium quando os pontos SÃO dados (alunos, cidades, lojas); " + NOTA,
                  clip=clip, fam=FAM, fundo_claro=fundo_claro)


# ================================================================ 2. pontilhado (estipulação de Voronoi ponderada)
def _estipula(T, passo, w, h, n, g, it=36):
    from scipy.spatial import cKDTree
    yy, xx = np.nonzero(T > 0.02)
    P = np.stack([xx * passo + passo / 2, yy * passo + passo / 2], 1)
    wts = T[yy, xx]
    idx = g.choice(len(P), n, p=wts / wts.sum())
    pts = P[idx] + g.uniform(-passo / 2, passo / 2, (n, 2))
    pw = wts / wts.sum()
    for k in range(it):
        _, lab = cKDTree(pts).query(P)
        sw = np.bincount(lab, wts, n)
        ok = sw > 1e-9
        pts[ok] = np.stack([np.bincount(lab, wts * P[:, 0], n)[ok] / sw[ok],
                            np.bincount(lab, wts * P[:, 1], n)[ok] / sw[ok]], 1)
        orf = ~ok                                    # ponto sem célula (empilhado num vizinho) = grumo → renasce
        if k < it - 4 and orf.any():
            pts[orf] = P[g.choice(len(P), int(orf.sum()), p=pw)] + g.uniform(-passo / 2, passo / 2, (int(orf.sum()), 2))
    # pontos colados (< 40% do espaçamento médio local) também são grumos: descarta o mais novo
    d, j = cKDTree(pts).query(pts, k=2)
    med = np.median(d[:, 1])
    tira = (d[:, 1] < 0.4 * med) & (np.arange(n) > j[:, 1])
    return pts[~tira]


def pontilhado(f, modo="linear", w=1080, h=1080, n=5200, diam=None, cor=None, tamanho_var=False, seed=0,
               fundo_claro=False):
    """Pontilhado (estipulação de Voronoi ponderada, Secord 2002): densidade = tom; pontos sempre do mesmo tamanho
    (ou variando com o tom). modo do tom: linear · radial · esfera · nuvem · faixa · diagonal · borda."""
    g = nprng(f, "stip", modo, seed)
    cor = cor or f.tinta
    passo = 2.0
    T = campo_tom(modo, w, h, passo, semente(f, "stipT", seed), inverte=fundo_claro and modo == "esfera") ** 1.2
    pts = _estipula(T, passo, w, h, n, g)
    d = diam or max(2.4, f.traco * 1.1)
    if tamanho_var:
        tom = _amostra_tom(T, passo, pts[:, 0], pts[:, 1])
        corpo = _pontos_varios(pts, d / 2 * (0.45 + 0.9 * tom), cor)
    else:
        corpo = _pontos_svg(pts, d, cor)
    nomes = {"linear": "pontilhado · degradê", "radial": "pontilhado · centro", "esfera": "pontilhado · esfera (volume)",
             "nuvem": "pontilhado · nuvem", "faixa": "pontilhado · faixa", "diagonal": "pontilhado · diagonal",
             "borda": "pontilhado · bordas (vinheta)"}
    return _campo(w, h, corpo, nomes[modo] + (" · tamanho variável" if tamanho_var else ""),
                  "degradê feito de pontos (sem banding); " + NOTA, clip=_ret(w, h), fam=FAM, fundo_claro=fundo_claro)


# ================================================================ 3. meio-tom vetorial
def meio_tom(f, modo="linear", w=1080, h=1080, celula=16.0, ang=45.0, forma="ponto", cor=None, seed=0,
             fundo_claro=False, duas_telas=False, hexagonal=False):
    """Meio-tom em VETOR: grade girada, raio ∝ √tom (imprime e escala sem moiré). forma: ponto · quadrado · cruz.
    duas_telas: tinta a 15° + acento a 75° (sobreposição tipo riso)."""
    cor = cor or f.tinta
    passo = 4.0
    T = campo_tom(modo, w, h, passo, semente(f, "mt", seed), inverte=fundo_claro and modo == "esfera")

    def tela(a, cor_, Tm, deslo=(0.0, 0.0)):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        L = math.hypot(w, h) / 2 + celula
        rng_ = np.arange(-L, L, celula)
        I, J = np.meshgrid(rng_, rng_)
        if hexagonal:
            I = I + (np.round(J / celula) % 2) * celula / 2
            J = J * 0.866
        X = w / 2 + I * ca - J * sa + deslo[0]
        Y = h / 2 + I * sa + J * ca + deslo[1]
        ok = (X > -celula) & (X < w + celula) & (Y > -celula) & (Y < h + celula)
        X, Y = X[ok], Y[ok]
        tom = _amostra_tom(Tm, passo, np.clip(X, 0, w - 1), np.clip(Y, 0, h - 1))
        if forma == "ponto":
            rr = celula * 0.47 * np.sqrt(tom)
            return _pontos_varios(np.stack([X, Y], 1), rr, cor_, q=0.35)
        if forma == "quadrado":
            s = celula * np.sqrt(tom) * 0.92
            d = "".join(f"M{x - si / 2:.1f} {y - si / 2:.1f}h{si:.1f}v{si:.1f}h-{si:.1f}z"
                        for x, y, si in zip(X, Y, s) if si > 0.8)
            return f'<path d="{d}" fill="{cor_}"/>'
        # cruz: traço com espessura proporcional
        s = celula * 0.42 * np.sqrt(tom)
        sel = s > 0.8
        d = "".join(f"M{x - si:.1f} {y:.1f}h{2 * si:.1f}M{x:.1f} {y - si:.1f}v{2 * si:.1f}"
                    for x, y, si in zip(X[sel], Y[sel], s[sel]))
        return f'<path d="{d}" fill="none" stroke="{cor_}" stroke-width="{max(1.5, celula * 0.16):.2f}"/>'
    if duas_telas:
        T2 = campo_tom("radial" if modo != "radial" else "linear", w, h, passo)
        corpo = tela(15, cor, T) + f'<g style="mix-blend-mode:screen">{tela(75, f.acento, T2, (2, 1))}</g>'
    else:
        corpo = tela(ang, cor, T)
    nome = f"meio-tom · {modo} · {forma}" + (" · hexagonal" if hexagonal else "") + (" · 2 telas" if duas_telas else "")
    return _campo(w, h, corpo, nome, f"célula {celula:g}px a {ang:g}° (≥ 12 px num 1080); só no fundo/ampliação, nunca "
                  "no rosto principal", clip=_ret(w, h), fam=FAM, fundo_claro=fundo_claro)


# ================================================================ 4. dither como pixels vetoriais
_BAYER2 = np.array([[0, 2], [3, 1]])


def _bayer(n):
    m = _BAYER2
    while m.shape[0] < n:
        m = np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])
    return (m + 0.5) / m.size


@lru_cache(maxsize=4)
def ruido_azul(n=32, sigma=1.5, seed=7):
    """Matriz de ruído azul n×n por void-and-cluster (Ulichney 1993), toroidal — gerada aqui (sem baixar textura)."""
    g = np.random.default_rng(seed)
    m = n * n
    yy, xx = np.mgrid[0:n, 0:n]
    d2 = np.minimum(xx, n - xx) ** 2 + np.minimum(yy, n - yy) ** 2
    K = np.fft.fft2(np.exp(-d2 / (2 * sigma ** 2)))
    en = lambda b: np.real(np.fft.ifft2(np.fft.fft2(b.astype(float)) * K))  # noqa: E731
    bp = np.zeros((n, n), bool)
    bp.flat[g.choice(m, m // 10, replace=False)] = True
    for _ in range(4 * m):
        e = en(bp)
        c = np.argmax(np.where(bp, e, -np.inf))
        bp.flat[c] = False
        e = en(bp)
        v = np.argmin(np.where(~bp, e, np.inf))
        bp.flat[v] = True
        if v == c:
            break
    rank = np.zeros(m, int)
    ones = int(bp.sum())
    b = bp.copy()
    for r in range(ones - 1, -1, -1):
        c = np.argmax(np.where(b, en(b), -np.inf))
        b.flat[c] = False
        rank[c] = r
    b = bp.copy()
    for r in range(ones, m):
        v = np.argmin(np.where(~b, en(b), np.inf))
        b.flat[v] = True
        rank[v] = r
    return (rank.reshape(n, n) + 0.5) / m


def _fs(T):
    """Floyd–Steinberg (1976): 7/16, 3/16, 5/16, 1/16."""
    a = T.astype(float).copy()
    H, W = a.shape
    out = np.zeros_like(a, bool)
    for y in range(H):
        for x in range(W):
            o = a[y, x] >= 0.5
            out[y, x] = o
            err = a[y, x] - o
            if x + 1 < W:
                a[y, x + 1] += err * 7 / 16
            if y + 1 < H:
                if x > 0:
                    a[y + 1, x - 1] += err * 3 / 16
                a[y + 1, x] += err * 5 / 16
                if x + 1 < W:
                    a[y + 1, x + 1] += err * 1 / 16
    return out


def _pixels(B, px, cor, opac=1.0):
    """Matriz booleana → 1 path com corridas horizontais fundidas."""
    d = []
    for i, row in enumerate(B):
        j, W = 0, len(row)
        while j < W:
            if row[j]:
                k = j
                while k < W and row[k]:
                    k += 1
                d.append(f"M{j * px:g} {i * px:g}h{(k - j) * px:g}v{px:g}h-{(k - j) * px:g}z")
                j = k
            else:
                j += 1
    o = f' fill-opacity="{opac:.3g}"' if opac < 1 else ""
    return f'<path d="{"".join(d)}" fill="{cor}"{o}/>' if d else ""


def dither(f, modo="linear", metodo="bayer8", w=1080, h=1080, px=8, cor=None, seed=0, fundo_claro=False, teto=0.84):
    """Dither assumido como 'pixel de tela' ampliado (px = tamanho do pixel). metodo: bayer2 · bayer4 · bayer8 · azul
    (void-and-cluster) · fs (Floyd–Steinberg). teto = tom máximo (< 1: nunca vira placa chapada)."""
    cor = cor or f.tinta
    gw, gh = int(math.ceil(w / px)), int(math.ceil(h / px))
    T = campo_tom(modo, gw * px, gh * px, px, semente(f, "dt", seed), inverte=fundo_claro and modo == "esfera")[:gh, :gw]
    T = np.minimum(T, teto)
    if metodo.startswith("bayer"):
        M = _bayer(int(metodo[5:]))
    elif metodo == "azul":
        M = ruido_azul(32)
    else:
        M = None
    if M is None:
        B = _fs(T)
    else:
        thr = np.tile(M, (gh // M.shape[0] + 1, gw // M.shape[1] + 1))[:gh, :gw]
        B = T > thr
    corpo = _pixels(B, px, cor)
    nomes = {"bayer2": "Bayer 2×2", "bayer4": "Bayer 4×4", "bayer8": "Bayer 8×8", "azul": "ruído azul",
             "fs": "Floyd–Steinberg"}
    return _campo(w, h, corpo, f"dither · {nomes[metodo]} · {modo}",
                  f"pixel de {px}px assumido (tela ampliada); Bayer é estável em vídeo, FS 'ferve'; " + NOTA,
                  clip=_ret(w, h), fam=FAM, fundo_claro=fundo_claro)


# ================================================================ 5. grade de pontos com máscara
def grade_pontos(f, modo="linear", w=1080, h=1080, passo=None, diam=None, cor=None, seed=0, fundo_claro=False):
    """Grade de pontos que SOME num degradê (raio ou presença). modo: linear · diagonal · dissolve (presença por
    ruído azul) · cruzes · hexagonal · onda · reserva (vazio retangular p/ texto) · indice (1 ponto no acento).
    Máscara radial genérica ('prateleira de template') fica de fora de propósito."""
    cor = cor or f.tinta
    passo = passo or f.unidade * 1.5
    d0 = diam or max(3.0, passo * 0.16)
    xs = np.arange(passo / 2, w, passo)
    ys = np.arange(passo / 2, h, passo)
    X, Y = np.meshgrid(xs, ys)
    if modo == "hexagonal":
        Y = Y * 0.866
        X = X + (np.arange(len(ys))[:, None] % 2) * passo / 2
        ok = Y < h
        X, Y = X[ok], Y[ok]
    X, Y = X.ravel(), Y.ravel()
    u, v = X / w, Y / h
    corpo = ""
    if modo in ("linear", "hexagonal"):
        t = np.clip(1.15 - u * 1.2, 0, 1)
        corpo = _pontos_varios(np.stack([X, Y], 1), d0 / 2 * t ** 0.8, cor, q=0.2)
    elif modo == "diagonal":
        t = np.clip(1.2 - (u + v) * 0.75, 0, 1)
        corpo = _pontos_varios(np.stack([X, Y], 1), d0 / 2 * t, cor, q=0.2)
    elif modo == "dissolve":
        B = ruido_azul(32)
        ii, jj = (Y / passo).astype(int) % 32, (X / passo).astype(int) % 32
        keep = (1 - u) ** 1.3 > B[ii, jj]
        corpo = _pontos_svg(np.stack([X[keep], Y[keep]], 1), d0, cor)
    elif modo == "cruzes":
        t = np.clip(1.1 - v * 1.15, 0, 1)
        s = passo * 0.18 * t
        sel = s > 0.6
        d = "".join(f"M{x - si:.1f} {y:.1f}h{2 * si:.1f}M{x:.1f} {y - si:.1f}v{2 * si:.1f}"
                    for x, y, si in zip(X[sel], Y[sel], s[sel]))
        corpo = f'<path d="{d}" {traco_attr(cor, max(1.5, f.traco * 0.6))}/>'
    elif modo == "onda":
        t = 0.5 + 0.5 * np.sin(2 * math.pi * (u * 2.2 + 0.25 * np.sin(2 * math.pi * v)))
        corpo = _pontos_varios(np.stack([X, Y], 1), d0 / 2 * (0.25 + 0.95 * t), cor, q=0.2)
    elif modo == "reserva":
        dentro = (u > 0.14) & (u < 0.74) & (v > 0.3) & (v < 0.62)
        corpo = _pontos_svg(np.stack([X[~dentro], Y[~dentro]], 1), d0, cor)
    elif modo == "indice":
        corpo = _pontos_svg(np.stack([X, Y], 1), d0, cor)
        k = int(len(X) * 0.58) + 7
        corpo += _pontos_svg([(X[k], Y[k])], d0 * 3.2, f.acento)
    nomes = {"linear": "grade de pontos · some à direita", "diagonal": "grade de pontos · some na diagonal",
             "dissolve": "grade de pontos · dissolve (ruído azul)", "cruzes": "grade de cruzes · some para baixo",
             "hexagonal": "grade hexagonal · some", "onda": "grade de pontos · onda de tamanho",
             "reserva": "grade de pontos · reserva para texto", "indice": "grade de pontos · 1 no acento"}
    return _campo(w, h, corpo, nomes[modo], f"passo = unidade da ficha ({passo:g}px); a máscara tem direção (nunca "
                  "radial genérica); " + NOTA, clip=_ret(w, h), fam=FAM, fundo_claro=fundo_claro)


# ================================================================ 6. mosaico
def mosaico(f, modo="quadtree", w=1080, h=1080, cor=None, seed=0, fundo_claro=False):
    """Mosaico de quadrados. modo: quadtree (contorno) · quadtree_tons · pixel (tamanho ∝ tom) · tesselas (andamento) ·
    falhado (xadrez com faltas) · escala (quadrados crescendo) · blocos (2 tintas)."""
    g = nprng(f, "mos", modo, seed)
    r = rng(f, "mos", modo, seed)
    cor = cor or f.tinta
    e = _esp(f, 0.55)
    corpo = ""
    if modo.startswith("quadtree") or modo == "blocos":
        N = campo_ruido(int(w / 8) + 1, int(h / 8) + 1, 40, 3, semente(f, "qt", seed), warp=2)
        quads = []

        def div(x, y, s, d):
            sub = N[int(y / 8):int((y + s) / 8) + 1, int(x / 8):int((x + s) / 8) + 1]
            if d < 6 and s > 20 and (sub.std() > 0.07 + 0.02 * d or d < 1):
                hs = s / 2
                for dx in (0, hs):
                    for dy in (0, hs):
                        div(x + dx, y + dy, hs, d + 1)
            else:
                quads.append((x, y, s, float(sub.mean())))
        S = max(w, h)
        div(0, 0, S, 0)
        if modo == "quadtree":       # escala para dentro de meia espessura: o fio da borda fica inteiro como os outros
            k_ = (S - e) / S
            corpo = "".join(f'<rect x="{e / 2 + x * k_:.1f}" y="{e / 2 + y * k_:.1f}" width="{s * k_:.1f}" '
                            f'height="{s * k_:.1f}"/>' for x, y, s, _ in quads)
            corpo = f'<g {traco_attr(cor, e)}>{corpo}</g>'
        else:
            gap = 3.0
            medios = [q for q in quads if 60 < q[2] < 200]
            excecao = medios[len(medios) * 3 // 5] if medios else None
            for x, y, s, m in quads:
                if modo == "blocos":
                    c_ = f.acento if (x, y, s, m) == excecao else cor
                    op = r.choice([0.1, 0.18, 0.3]) if c_ == cor else 1
                else:
                    c_, op = cor, float(np.clip(0.06 + (m + 1) * 0.22, 0.04, 0.5))
                corpo += (f'<rect x="{x + gap / 2:.1f}" y="{y + gap / 2:.1f}" width="{s - gap:.1f}" height="{s - gap:.1f}" '
                          f'fill="{c_}" fill-opacity="{op:.2f}"/>')
    elif modo == "pixel":
        c = f.unidade * 1.2
        T = campo_tom("radial", w, h, 4.0)
        d = ""
        for y in np.arange(0, h, c):
            for x in np.arange(0, w, c):
                t = _amostra_tom(T, 4.0, x + c / 2, y + c / 2)
                s = c * 0.94 * math.sqrt(float(t))
                if s > 1.2:
                    d += f"M{x + (c - s) / 2:.1f} {y + (c - s) / 2:.1f}h{s:.1f}v{s:.1f}h-{s:.1f}z"
        corpo = f'<path d="{d}" fill="{cor}"/>'
    elif modo == "tesselas":
        c = f.unidade * 1.5
        grupos = {}
        N = campo_ruido(int(w / c) + 2, int(h / c) + 2, 6, 2, semente(f, "tess", seed))
        for i, y in enumerate(np.arange(c / 2, h + c / 2, c * 1.08)):
            for j, x in enumerate(np.arange(c / 2, w + c / 2, c * 1.08)):
                a = r.gauss(0, 6) + 9 * math.sin(y / 140 + x / 300)
                s = c * r.uniform(0.8, 0.92)
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                pts = [(x + (px * ca - py * sa) * s / 2 + r.gauss(0, 0.8), y + (px * sa + py * ca) * s / 2 + r.gauss(0, 0.8))
                       for px, py in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
                op = [0.22, 0.4, 0.62, 0.85][int(np.clip((N[min(i, N.shape[0] - 1), min(j, N.shape[1] - 1)] + 1) * 2, 0, 3))]
                grupos.setdefault(op, []).append(caminho(pts, True))
        corpo = "".join(f'<path d="{"".join(v)}" fill="{cor}" fill-opacity="{k_}"/>' for k_, v in grupos.items())
    elif modo == "falhado":
        c = f.unidade * 1.5
        d = ""
        for i, y in enumerate(np.arange(0, h, c)):
            for j, x in enumerate(np.arange(0, w, c)):
                if (i + j) % 2 == 0 and r.random() > 0.18 + 0.6 * (x / w) ** 2:
                    d += f"M{x:.1f} {y:.1f}h{c:.1f}v{c:.1f}h-{c:.1f}z"
        corpo = f'<path d="{d}" fill="{cor}"/>'
    elif modo == "escala":           # colunas de 5 quadrados, centradas, crescendo 12% — nenhuma cortada
        cols, s = [], 6.0
        while True:
            cols.append(s)
            s *= 1.12
            if 5 * s + 4 * 0.25 * s > h - 24:
                break
        larg = sum(c * 1.25 for c in cols) - cols[-1] * 0.25
        x = (w - larg) / 2
        d = ""
        for s in cols:
            alt = 5 * s + 4 * 0.25 * s
            for k in range(5):
                d += f"M{x:.1f} {h / 2 - alt / 2 + k * s * 1.25:.1f}h{s:.1f}v{s:.1f}h-{s:.1f}z"
            x += s * 1.25
        corpo = f'<path d="{d}" fill="{cor}"/>'
    nomes = {"quadtree": "mosaico · quadtree", "quadtree_tons": "mosaico · quadtree em tons", "pixel": "mosaico · pixel (tamanho = tom)",
             "tesselas": "mosaico · tesselas", "falhado": "mosaico · xadrez que falha", "escala": "mosaico · quadrados em escala",
             "blocos": "mosaico · blocos + acento"}
    return _campo(w, h, corpo, nomes[modo], "grade rígida + 1 exceção > enfeite; " + NOTA, clip=_ret(w, h), fam=FAM,
                  fundo_claro=fundo_claro)


# ================================================================ 7. meio-tom de linhas
def meio_tom_linhas(f, modo="linear", w=1080, h=1080, passo=14.0, ang=0.0, deslocar=False, circular=False, cor=None,
                    seed=0, fundo_claro=False):
    """Meio-tom de LINHAS: espessura ∝ tom (gravura) ou deslocamento ∝ tom (relevo; só horizontal, opaco: pinta com a
    cor do fundo para cada linha tampar as de trás). circular = anéis."""
    cor = cor or f.tinta
    tp = 4.0
    T = np.minimum(campo_tom(modo, w, h, tp, semente(f, "mtl", seed), inverte=fundo_claro and modo == "esfera"), 0.86)
    polys, ls = [], []

    def pedacos(X, Y, t):
        """Fita de largura ∝ tom, partida onde o tom some (sem fio-fantasma sobre o vazio)."""
        on = t > 0.03
        k = 0
        while k < len(t):
            if on[k]:
                m = k
                while m < len(t) and on[m]:
                    m += 1
                if m - k > 1:
                    polys.append(fita(np.stack([X[k:m], Y[k:m]], 1), passo * 0.9 * t[k:m]))
                k = m
            else:
                k += 1
    if circular:
        for R in np.arange(passo / 2, math.hypot(w, h) / 2, passo):
            th = np.linspace(0, 2 * math.pi, max(60, int(2 * math.pi * R / 7)))
            X, Y = w / 2 + R * np.cos(th), h / 2 + R * np.sin(th)
            t = _amostra_tom(T, tp, np.clip(X, 0, w - 1), np.clip(Y, 0, h - 1))
            if (t > 0.03).all():             # anel inteiro: 2 bordas fechadas (sem costura em 0°)
                lw = passo * 0.9 * t / 2
                fora = np.stack([w / 2 + (R + lw) * np.cos(th), h / 2 + (R + lw) * np.sin(th)], 1)[:-1]
                dentro = np.stack([w / 2 + (R - lw) * np.cos(th), h / 2 + (R - lw) * np.sin(th)], 1)[:-1]
                polys.append(fora)
                polys.append(dentro[::-1])
            else:
                pedacos(X, Y, t)
    else:
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        L = math.hypot(w, h) / 2 + passo
        tt = np.linspace(-L, L, int(2 * L / 6))
        for off in np.arange(-L, L, passo):
            X = w / 2 + tt * ca - off * sa
            Y = h / 2 + tt * sa + off * ca
            ok = (X > -passo) & (X < w + passo) & (Y > -passo) & (Y < h + passo)
            if ok.sum() < 2:
                continue
            X, Y = X[ok], Y[ok]
            t = _amostra_tom(T, tp, np.clip(X, 0, w - 1), np.clip(Y, 0, h - 1))
            if deslocar:                     # (horizontal) suaviza o tom ao longo da linha: sem degrau na borda da forma
                from scipy.ndimage import gaussian_filter1d
                t = gaussian_filter1d(t.astype(float), 3.0, mode="nearest")
                ls.append(np.stack([X + t * passo * 3.2 * sa, Y - t * passo * 3.2 * ca], 1))
            else:
                pedacos(X, Y, t)
    if polys:
        corpo = _cheio(polys, cor, regra="evenodd" if circular else "nonzero")
    else:                                # deslocamento com OCLUSÃO: cada linha tampa as de trás (relevo), sem cruzar fios
        fundo = f.papel if fundo_claro else f.fundo
        corpo = ""
        for ln in ls:
            poly = np.vstack([ln, [[ln[-1][0], h + 40], [ln[0][0], h + 40]]])
            corpo += (f'<path d="{caminho(poly, True)}" fill="{fundo}" stroke="{cor}" stroke-width="{_esp(f, 0.6):.3g}" '
                      f'stroke-linejoin="round"/>')
    nome = f"meio-tom de linhas · {modo}" + (" · deslocamento" if deslocar else "") + (" · anéis" if circular else "") + \
        (f" · {ang:g}°" if ang else "")
    return _campo(w, h, corpo, nome, f"passo {passo:g}px; gravura/tela de TV; " + NOTA, clip=_ret(w, h), fam=FAM,
                  fundo_claro=fundo_claro)


# ================================================================ amostras
@amostra(FAM, "Voronoi")
def _a_vor(f):
    return [voronoi(f), voronoi(f, "seixos", n=70), voronoi(f, "gradiente", cor=f.apoio), voronoi(f, "tons", n=90),
            voronoi(f, "centros", n=60), voronoi(f, "delaunay", n=70, cor=f.apoio), voronoi(f, "craquelado", n=160),
            voronoi(f, "lente", n=48, seed=2), voronoi(f, "seixos", n=60, cor=f.fundo, seed=2, fundo_claro=True)]


@amostra(FAM, "pontilhado")
def _a_stip(f):
    return [pontilhado(f), pontilhado(f, "radial", n=4200), pontilhado(f, "esfera", n=4800),
            pontilhado(f, "nuvem", n=5200, cor=f.apoio), pontilhado(f, "faixa", n=3200),
            pontilhado(f, "diagonal", n=4200, tamanho_var=True), pontilhado(f, "borda", n=4200, cor=f.acento),
            pontilhado(f, "esfera", n=5000, cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "meio-tom")
def _a_mt(f):
    return [meio_tom(f), meio_tom(f, "radial"), meio_tom(f, "esfera", celula=14), meio_tom(f, "nuvem", cor=f.apoio),
            meio_tom(f, "linear", forma="quadrado", ang=0, celula=20), meio_tom(f, "diagonal", forma="cruz", ang=0, celula=22),
            meio_tom(f, "faixa", hexagonal=True, ang=0, celula=18),
            meio_tom(f, "esfera", cor=f.fundo, celula=14, fundo_claro=True)]


@amostra(FAM, "dither")
def _a_dit(f):
    return [dither(f), dither(f, "radial", "bayer4", px=10), dither(f, "linear", "azul", px=6),
            dither(f, "esfera", "fs", px=6), dither(f, "nuvem", "bayer8", px=12, cor=f.apoio),
            dither(f, "faixa", "bayer2", px=12),
            dither(f, "diagonal", "azul", px=8, cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "grade de pontos")
def _a_gp(f):
    return [grade_pontos(f), grade_pontos(f, "diagonal"), grade_pontos(f, "dissolve"), grade_pontos(f, "cruzes"),
            grade_pontos(f, "hexagonal"), grade_pontos(f, "onda"), grade_pontos(f, "reserva", cor=f.apoio),
            grade_pontos(f, "indice", cor=f.apoio), grade_pontos(f, "dissolve", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "mosaico")
def _a_mos(f):
    return [mosaico(f), mosaico(f, "quadtree_tons"), mosaico(f, "pixel"), mosaico(f, "tesselas", cor=f.apoio),
            mosaico(f, "falhado"), mosaico(f, "escala", w=1080, h=540), mosaico(f, "blocos"),
            mosaico(f, "quadtree", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "meio-tom de linhas")
def _a_mtl(f):
    return [meio_tom_linhas(f), meio_tom_linhas(f, "esfera"), meio_tom_linhas(f, "esfera", deslocar=True, passo=16),
            meio_tom_linhas(f, "radial", circular=True), meio_tom_linhas(f, "linear", ang=f.angulo + 45 + 6),

            meio_tom_linhas(f, "esfera", passo=12, cor=f.fundo, fundo_claro=True)]
