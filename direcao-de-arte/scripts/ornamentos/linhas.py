"""ornamentos.linhas — família "LINHAS E CAMPOS" (+ ferramentas comuns de traço usadas por mao/pontos/texturas/grades).

Origem (references/elementos.md, pesquisa 11 §2.2 e §2.9, pesquisa 13 §4): topografia (E22), ondas, espiral, campo de
fluxo (E94), guilloché (E21), moiré calculado (E96), hachura (E20), op-art (E97), grade distorcida (E100), pauta (E24),
linhas de velocidade (E23), raios, círculos concêntricos, chão em perspectiva, linha de ritmo (pulso).

Regras que o código segue: 1–2 espessuras por elemento (fino = ficha.traco·k, nunca < 1,5 px; grosso ≈ 2×); semente
fixa; o campo "nasce de algo" sempre que dá (escoamento REAL em volta de um cilindro, linhas de campo de 2 polos,
hipotrocoide de torno de cédula, moiré pela fórmula α = p/D); NUNCA sob texto pequeno (op-art, guilloché, moiré e
hachura fina vibram). Tudo vetor, sem dependências novas (ruído próprio em numpy/scipy; contornos pelo scikit-image).
"""
import math
import random
import zlib

import numpy as np

from .nucleo import amostra, elemento

FAM = "linhas"


# ================================================================ ferramentas comuns (importadas pelos outros módulos)
def semente(f, *salt):
    """Semente estável entre execuções (o hash() de str do Python muda a cada processo)."""
    return zlib.crc32(repr((f.seed,) + tuple(str(s) for s in salt)).encode()) & 0xFFFFFFFF


def rng(f, *salt):
    return random.Random(semente(f, *salt))


def nprng(f, *salt):
    return np.random.default_rng(semente(f, *salt))


def _n(v):
    """Inteiro em décimos de px → número curto ('12', '1.5', '-.5')."""
    if v % 10 == 0:
        return str(v // 10)
    s = f"{v / 10:.1f}"
    if s.startswith("0."):
        return s[1:]
    if s.startswith("-0."):
        return "-" + s[2:]
    return s


def _junta(tok):
    out = tok[0]
    for t in tok[1:]:
        out += t if t[0] == "-" else " " + t
    return out


def caminho(pts, fechado=False):
    """Polilinha compacta: M absoluto + l relativo, precisão 0,1 px (sem erro acumulado)."""
    q = [(int(round(x * 10)), int(round(y * 10))) for x, y in pts]
    if not q:
        return ""
    nums, (px, py) = [], q[0]
    for x, y in q[1:]:
        if x == px and y == py:
            continue
        nums += [_n(x - px), _n(y - py)]
        px, py = x, y
    d = "M" + _junta([_n(q[0][0]), _n(q[0][1])])
    if nums:
        d += "l" + _junta(nums)
    return d + ("z" if fechado else "")


def caminhos(lista, fechado=False):
    return "".join(caminho(p, fechado) for p in lista if len(p) > 1)


def curva(pts, fechado=False, tensao=1.0):
    """Catmull-Rom → Bézier cúbica relativa compacta (0,1 px). Use com poucos pontos (já simplificados)."""
    P = [tuple(p) for p in pts]
    n = len(P)
    if n < 3:
        return caminho(P, fechado)
    if fechado and P[0] == P[-1]:
        P = P[:-1]
        n = len(P)
    r = lambda v: int(round(v * 10))  # noqa: E731
    segs = range(n) if fechado else range(n - 1)
    cx, cy = r(P[0][0]), r(P[0][1])
    d = "M" + _junta([_n(cx), _n(cy)]) + "c"
    nums = []
    for i in segs:
        p0 = P[(i - 1) % n] if (fechado or i > 0) else P[0]
        p1, p2 = P[i], P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (fechado or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * tensao / 6, p1[1] + (p2[1] - p0[1]) * tensao / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * tensao / 6, p2[1] - (p3[1] - p1[1]) * tensao / 6)
        for x, y in (c1, c2, p2):
            nums += [_n(r(x) - cx), _n(r(y) - cy)]
        cx, cy = r(p2[0]), r(p2[1])
    return d + _junta(nums) + ("z" if fechado else "")


def pontos_d(xy):
    """Muitos pontos num path só: 'm dx dy h0' (desenhar com stroke-linecap=round e stroke-width = diâmetro)."""
    q = [(int(round(x * 10)), int(round(y * 10))) for x, y in xy]
    if not q:
        return ""
    out = ["M" + _junta([_n(q[0][0]), _n(q[0][1])]) + "h0"]
    px, py = q[0]
    for x, y in q[1:]:
        out.append("m" + _junta([_n(x - px), _n(y - py)]) + "h0")
        px, py = x, y
    return "".join(out)


def campo_ruido(w, h, escala, oitavas=4, seed=0, persist=0.5, lacun=2.0, warp=0.0):
    """Ruído suave 2-D (fBm de valores com interpolação cúbica), normalizado para [-1, 1].
    w, h = amostras; escala = período da 1ª oitava em amostras; warp = deformação de domínio (em amostras)."""
    from scipy.ndimage import map_coordinates
    g = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)

    def fbm(yy, xx, g):
        tot, amp, per, soma = np.zeros(yy.shape), 1.0, float(escala), 0.0
        for _ in range(oitavas):
            gh, gw = int((yy.max() + 8) / per) + 6, int((xx.max() + 8) / per) + 6
            grid = g.normal(0, 1, (gh, gw))
            oy, ox = g.uniform(1, 2, 2)
            tot += amp * map_coordinates(grid, [yy / per + oy, xx / per + ox], order=3, mode="nearest")
            soma += amp
            amp *= persist
            per /= lacun
        return tot / soma
    if warp:
        dy = fbm(yy, xx, g)
        dx = fbm(yy, xx, g)
        yy = np.clip(yy + warp * dy, 0, None)
        xx = np.clip(xx + warp * dx, 0, None)
    v = fbm(yy, xx, g)
    v -= v.mean()
    return v / (np.abs(v).max() + 1e-9)


def contornos(campo, niveis, passo=1.0, tol=0.35, min_pts=6, min_comp=0.0):
    """Isolinhas (marching squares do scikit-image) → listas de pontos em px (campo amostrado a cada `passo` px).
    min_comp = comprimento mínimo (px) — descarta ilhas minúsculas."""
    from skimage.measure import find_contours, approximate_polygon
    out = []
    for lv in niveis:
        cs = []
        for c in find_contours(campo, lv):
            if min_comp and np.sum(np.hypot(*np.diff(c, axis=0).T)) * passo < min_comp:
                continue
            c = approximate_polygon(c, tol)
            if len(c) >= min_pts:
                cs.append([(x * passo, y * passo) for y, x in c])
        out.append(cs)
    return out


def recorta(linhas_, x0, y0, x1, y1):
    """Corta polilinhas num retângulo (descarta o que sai; quebra a linha nas saídas)."""
    out = []
    for ln in linhas_:
        cur = []
        for x, y in ln:
            if x0 <= x <= x1 and y0 <= y <= y1:
                cur.append((x, y))
            else:
                if len(cur) > 1:
                    out.append(cur)
                cur = []
        if len(cur) > 1:
            out.append(cur)
    return out


def caixa_de(listas, folga=0.0):
    xs = [x for ln in listas for x, _ in ln]
    ys = [y for ln in listas for _, y in ln]
    if not xs:
        return (0, 0, 0, 0)
    return (min(xs) - folga, min(ys) - folga, max(xs) + folga, max(ys) + folga)


def traco_attr(cor, esp, opac=1.0, cap="butt", join="round", extra=""):
    o = f' stroke-opacity="{opac:.3g}"' if opac < 1 else ""
    return (f'fill="none" stroke="{cor}" stroke-width="{esp:.3g}" stroke-linecap="{cap}" '
            f'stroke-linejoin="{join}"{o}{extra}')


def claro(el):
    """Marca o elemento para ser mostrado sobre o papel (tema claro) no catálogo."""
    el.fundo_claro = True
    return el


def fita(P, larg):
    """Polígono de largura variável ao longo da polilinha P (pontas retas). `larg` = número ou array por ponto."""
    P = np.asarray(P, float)
    lw = np.broadcast_to(np.asarray(larg, float), (len(P),))
    T = np.gradient(P, axis=0)
    T /= (np.hypot(T[:, 0], T[:, 1])[:, None] + 1e-9)
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    return np.vstack([P + N * lw[:, None] / 2, (P - N * lw[:, None] / 2)[::-1]])


def _fechada(p):
    return len(p) > 3 and abs(p[0][0] - p[-1][0]) < 1e-6 and abs(p[0][1] - p[-1][1]) < 1e-6


def _ln(listas, cor, esp, opac=1.0, fechadas=False, suave=False, cap="butt", extra=""):
    listas = [p for p in listas if len(p) > 1]
    if not listas:
        return ""
    fn = curva if suave else caminho
    d = "".join(fn(p, fechadas or _fechada(p)) for p in listas)
    return f'<path d="{d}" {traco_attr(cor, esp, opac, cap, extra=extra)}/>'


def _cheio(polys, cor, opac=1.0, regra="nonzero"):
    d = "".join(caminho(p, True) for p in polys if len(p) > 2)
    o = f' fill-opacity="{opac:.3g}"' if opac < 1 else ""
    return f'<path d="{d}" fill="{cor}" fill-rule="{regra}"{o}/>'


def _campo(w, h, corpo, nome, nota, defs="", clip=None, caixa=None, fam=FAM, fundo_claro=False):
    if clip:
        defs += f'<clipPath id="cl">{clip}</clipPath>'
        corpo = f'<g clip-path="url(#cl)">{corpo}</g>'
    if caixa:
        caixa = (max(0.0, caixa[0]), max(0.0, caixa[1]), min(float(w), caixa[2]), min(float(h), caixa[3]))
    el = elemento(w, h, corpo, nome, fam, defs=defs, caixa=caixa or (0, 0, w, h), nota=nota)
    return claro(el) if fundo_claro else el


def _esp(f, k=0.6):
    """Espessura de fio de campo: k × ficha.traco, nunca abaixo de 1,5 px (some no celular)."""
    return max(1.5, f.traco * k)


def _ret(w, h):
    return f'<rect width="{w}" height="{h}"/>'


NOTA_CAMPO = "tempero de fundo: ≤ 10% de contraste sob texto; nunca sob texto pequeno"


# ================================================================ 1. topografia (curvas de nível)
def _relevo(w, h, passo, picos, seed, rugosidade=0.35, warp=6.0):
    gh, gw = int(h / passo) + 1, int(w / passo) + 1
    g = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:gh, 0:gw].astype(float)
    z = np.zeros((gh, gw))
    for _ in range(picos):
        cx, cy = g.uniform(0.1, 0.9) * gw, g.uniform(0.1, 0.9) * gh
        s = g.uniform(0.14, 0.3) * max(gw, gh)
        z += g.uniform(0.6, 1.0) * np.exp(-(((xx - cx) / s) ** 2 + ((yy - cy) / (s * g.uniform(0.7, 1.3))) ** 2))
    z += rugosidade * campo_ruido(gw, gh, max(gw, gh) / 3.2, 4, seed + 1, warp=warp)
    return (z - z.min()) / (np.ptp(z) + 1e-9)


def topografia(f, w=1080, h=1080, niveis=18, picos=3, mestre=5, cor=None, k=0.55, acento_nivel=None,
               terraco=False, rugosidade=0.2, circulo=False, seed=0, fundo_claro=False):
    """Curvas de nível de um relevo (morros gaussianos + ruído deformado). Cada `mestre`-ésima mais grossa (convenção
    de mapa). acento_nivel = índice de 1 curva no acento ('a cota da meta'); terraco = degraus preenchidos."""
    passo = 4.0
    z = _relevo(w, h, passo, picos, semente(f, "topo", seed), rugosidade)
    cor = cor or f.tinta
    lv = np.linspace(0.04, 0.96, niveis)
    corpo = ""
    if terraco:
        zp = np.pad(z, 1, constant_values=-1)
        for c in contornos(zp, lv[2:], passo, tol=0.4, min_comp=90):
            corpo += _cheio([[(x - passo, y - passo) for x, y in p] for p in c], cor, 0.075)
        corpo += _ln([p for c in contornos(z, lv[2:], passo, tol=0.4, min_comp=90) for p in c], cor, _esp(f, 0.4), 0.5,
                     suave=True)
    else:
        cs = contornos(z, lv, passo, tol=0.4, min_comp=110)
        finas = [p for i, c in enumerate(cs) for p in c if (i + 1) % mestre and i != acento_nivel]
        grossas = [p for i, c in enumerate(cs) for p in c if not (i + 1) % mestre and i != acento_nivel]
        corpo += _ln(finas, cor, _esp(f, k), suave=True) + _ln(grossas, cor, _esp(f, k) * 2.2, suave=True)
        if acento_nivel is not None:
            corpo += _ln(cs[acento_nivel], f.acento, _esp(f, k) * 2.2, suave=True)
    clip = f'<circle cx="{w / 2}" cy="{h / 2}" r="{min(w, h) / 2 - 2}"/>' if circulo else _ret(w, h)
    nome = f"topografia · {niveis} níveis" + (" · terraços" if terraco else "") + (" · lente" if circulo else "") + \
        (" · cota no acento" if acento_nivel is not None else "")
    return _campo(w, h, corpo, nome, "relevo REAL do lugar > ruído; 8–20 níveis, mestra a cada 5; " + NOTA_CAMPO,
                  clip=clip, fundo_claro=fundo_claro)


# ================================================================ 2. ondas
def ondas(f, modo="paralelas", w=1080, h=1080, n=34, ciclos=3.0, amp=None, cor=None, k=0.6, seed=0,
          fundo_claro=False):
    """Ondas paralelas. modo: paralelas · fase · pulso · amortecida · interferencia · relevo · faixas · vertical."""
    r = nprng(f, "ondas", modo, seed)
    cor = cor or f.tinta
    vert = modo == "vertical"
    W, H = (h, w) if vert else (w, h)
    gap = H / (n + 1)
    A = amp if amp is not None else gap * 1.1
    xs = np.linspace(-20, W + 20, 300)
    u = xs / W
    linhas_ = []
    nz = campo_ruido(300, n, 46, 3, int(r.integers(1 << 30))) if modo == "relevo" else None
    for i in range(n):
        y0 = (i + 1) * gap
        if modo in ("paralelas", "vertical"):
            y = y0 + A * np.sin(2 * math.pi * ciclos * u)
        elif modo == "fase":
            y = y0 + A * np.sin(2 * math.pi * ciclos * u + i * 0.22)
        elif modo == "pulso":
            env = np.exp(-((u - 0.5) / 0.16) ** 2) * np.exp(-((i - n / 2) / (n / 3.2)) ** 2)
            y = y0 + A * 2.6 * env * np.sin(2 * math.pi * 6 * u)
        elif modo == "amortecida":
            y = y0 + A * 2.2 * np.exp(-3.2 * u) * np.sin(2 * math.pi * 7 * u)
        elif modo == "interferencia":
            y = y0 + A * 0.7 * (np.sin(2 * math.pi * ciclos * u) + np.sin(2 * math.pi * ciclos * 1.27 * u + i * 0.15))
        elif modo == "faixas":
            y = y0 + A * np.sin(2 * math.pi * ciclos * u + i * 0.18)
        else:  # relevo (linhas de cumeada)
            env = np.exp(-((u - 0.5) / 0.2) ** 2)
            y = y0 - gap * 9.0 * env * np.clip(nz[i] + 0.2, 0, None) ** 1.3 - gap * 0.6 * nz[i]
        linhas_.append(np.stack([xs, y], 1))
    corpo = ""
    if modo == "faixas":
        corpo = _cheio([np.vstack([linhas_[i], linhas_[i + 1][::-1]]) for i in range(0, n - 1, 2)], cor)
    elif modo == "relevo":
        # OCLUSÃO GEOMÉTRICA (antes: cada linha era um polígono pintado com a cor do fundo → no fundo oposto vira bloco
        # preto, D18). Agora só fica o trecho de cada linha que está ACIMA de todas as da frente: só traços.
        n_ = len(linhas_)
        frente = np.full(len(xs), np.inf)
        visiveis = []
        for ln in linhas_[::-1]:                       # da frente para trás
            d = frente - ln[:, 1]                       # > 0 = a linha está acima das da frente → visível
            runs, cur = [], []
            for kk in range(len(xs)):
                if d[kk] > 0.4:
                    if not cur and kk > 0 and d[kk - 1] <= 0.4 and np.isfinite(d[kk - 1]):
                        t = d[kk - 1] / (d[kk - 1] - d[kk])      # entra: cruzamento por interpolação linear
                        cur.append((xs[kk - 1] + t * (xs[kk] - xs[kk - 1]), ln[kk - 1, 1] + t * (ln[kk, 1] - ln[kk - 1, 1])))
                    cur.append((xs[kk], ln[kk, 1]))
                else:
                    if cur and np.isfinite(d[kk]):
                        t = d[kk - 1] / (d[kk - 1] - d[kk]) if d[kk - 1] != d[kk] else 0.0
                        cur.append((xs[kk - 1] + t * (xs[kk] - xs[kk - 1]), ln[kk - 1, 1] + t * (ln[kk, 1] - ln[kk - 1, 1])))
                    if len(cur) > 1:
                        runs.append(cur)
                    cur = []
            if len(cur) > 1:
                runs.append(cur)
            visiveis += runs
            frente = np.minimum(frente, ln[:, 1])
        corpo = _ln([r for r in visiveis if sum(abs(b[0] - a_[0]) for a_, b in zip(r, r[1:])) > 6], cor, _esp(f, k))
    else:
        if vert:
            linhas_ = [np.stack([ln[:, 1], ln[:, 0]], 1) for ln in linhas_]
        corpo = _ln(linhas_, cor, _esp(f, k))
    nomes = {"paralelas": "ondas paralelas", "fase": "ondas em fase deslocada", "pulso": "ondas · pulso",
             "amortecida": "onda amortecida", "interferencia": "ondas · interferência", "relevo": "relevo de linhas",
             "faixas": "faixas onduladas", "vertical": "ondas verticais"}
    nota = "linhas ocultas calculadas (só traço, funciona em qualquer fundo); " if modo == "relevo" else ""
    return _campo(w, h, corpo, nomes[modo], nota + NOTA_CAMPO, clip=_ret(w, h), fundo_claro=fundo_claro)


# ================================================================ 3. espiral
def espiral(f, modo="arquimedes", w=1080, h=1080, voltas=16, cor=None, k=0.7, seed=0, fundo_claro=False):
    """Espirais. modo: arquimedes · afinando · dupla · logaritmica · quadrada · perspectiva · tracejada · fermat."""
    cor = cor or f.tinta
    cx, cy = w / 2, h / 2
    R = 0.48 * min(w, h)
    corpo = ""
    if modo in ("arquimedes", "afinando", "dupla", "tracejada", "perspectiva", "fermat"):
        m = int(voltas * 150)
        t = np.linspace(0, 2 * math.pi * voltas, m)
        u = t / t[-1]
        rad = R * (np.sqrt(u) if modo == "fermat" else u)
        sy = 0.34 if modo == "perspectiva" else 1.0
        P = np.stack([cx + rad * np.cos(t), cy + rad * np.sin(t) * sy], 1)
        if modo == "afinando":
            corpo = _cheio([fita(P, _esp(f, k) * (0.3 + 4.2 * u ** 1.3))], cor)
        elif modo == "tracejada":
            corpo = _ln([P], cor, _esp(f, k),
                        extra=f' stroke-dasharray="{f.unidade * 0.5:.1f} {f.unidade * 0.4:.1f}"')
        else:
            corpo = _ln([P], cor, _esp(f, k))
        if modo == "dupla":
            corpo += _ln([np.stack([2 * cx - P[:, 0], 2 * cy - P[:, 1]], 1)], f.acento, _esp(f, k))
    elif modo == "logaritmica":
        t = np.linspace(-8 * math.pi, 0.62 * math.pi, 1800)
        b = math.log(1.618) / (math.pi / 2)
        rad = R * 0.62 * np.exp(b * t)
        P = np.stack([cx + rad * np.cos(t), cy + rad * np.sin(t)], 1)
        corpo = _ln([P], cor, _esp(f, k) * 1.5)
    elif modo == "quadrada":
        passo = R / voltas
        pts = [(cx, cy)]
        x, y, L = cx, cy, passo
        for i in range(int(voltas * 4)):
            dx, dy = [(1, 0), (0, 1), (-1, 0), (0, -1)][i % 4]
            x, y = x + dx * L, y + dy * L
            pts.append((x, y))
            if i % 2:
                L += passo
        corpo = _ln([pts], cor, _esp(f, k), extra=' stroke-linejoin="miter"').replace('stroke-linejoin="round"', "")
    nomes = {"arquimedes": "espiral de Arquimedes", "afinando": "espiral que engrossa", "dupla": "espiral dupla",
             "logaritmica": "espiral logarítmica (φ)", "quadrada": "espiral quadrada", "perspectiva": "espiral em perspectiva",
             "tracejada": "espiral tracejada", "fermat": "espiral de Fermat"}
    return _campo(w, h, corpo, nomes[modo], "herói de 1 peça ou fundo ≤ 10%; centro = o assunto; " + NOTA_CAMPO,
                  clip=_ret(w, h), fundo_claro=fundo_claro)


# ================================================================ 4. campo de fluxo
def _psi(modo, X, Y, w, h, ang):
    """Função de corrente de escoamentos REAIS (potencial): as linhas de corrente são as curvas de nível de ψ."""
    a = math.radians(ang)
    Xr = (X - w / 2) * math.cos(a) + (Y - h / 2) * math.sin(a)
    Yr = -(X - w / 2) * math.sin(a) + (Y - h / 2) * math.cos(a)
    if modo == "cilindro":
        R = 0.17 * min(w, h)
        r2 = Xr ** 2 + Yr ** 2
        psi = Yr * (1 - R ** 2 / np.maximum(r2, 1e-6))
        return np.where(r2 < R ** 2, np.nan, psi), R
    if modo == "dipolo":     # 2 polos (+/−): ψ = cos θ1 − cos θ2 (linhas de campo do dipolo, sem corte de ramo)
        d = 0.16 * min(w, h)
        c1 = (Xr - d) / (np.hypot(Xr - d, Yr) + 1e-9)
        c2 = (Xr + d) / (np.hypot(Xr + d, Yr) + 1e-9)
        return c1 - c2, d
    r2 = Xr ** 2 + Yr ** 2 + 1e-6     # ralo: ψ = a·ln r + b·θ → derivadas analíticas (sem a costura do arctan)
    a_, b_ = 0.9, 0.35
    ca, sa = math.cos(a), math.sin(a)
    dXr, dYr = (a_ * Xr - b_ * Yr) / r2, (a_ * Yr + b_ * Xr) / r2
    return (dXr * ca - dYr * sa, dXr * sa + dYr * ca), 0


def _streamlines(cosf, sinf, w, h, esc, dsep, passo=2.0, dtest=0.55, min_len=30, max_pts=900, seed=0):
    """Linhas de corrente igualmente espaçadas (Jobard–Lefer simplificado) num campo de direções dado na grade de
    `esc` px (cosf, sinf)."""
    g = np.random.default_rng(seed)
    cel = dsep
    grade = {}
    H_, W_ = cosf.shape

    def dir_(x, y):
        fx, fy = min(max(x / esc, 0), W_ - 1.001), min(max(y / esc, 0), H_ - 1.001)
        i, j = int(fy), int(fx)
        ty, tx = fy - i, fx - j
        c = (cosf[i, j] * (1 - tx) + cosf[i, j + 1] * tx) * (1 - ty) + (cosf[i + 1, j] * (1 - tx) + cosf[i + 1, j + 1] * tx) * ty
        s = (sinf[i, j] * (1 - tx) + sinf[i, j + 1] * tx) * (1 - ty) + (sinf[i + 1, j] * (1 - tx) + sinf[i + 1, j + 1] * tx) * ty
        n = math.hypot(c, s) + 1e-9
        return c / n, s / n

    def livre(x, y, lim):
        i, j = int(x // cel), int(y // cel)
        l2 = lim * lim
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for (px, py) in grade.get((i + di, j + dj), ()):
                    if (px - x) ** 2 + (py - y) ** 2 < l2:
                        return False
        return True

    def integra(x, y, sinal):
        pts = []
        for _ in range(max_pts):
            c, s = dir_(x, y)
            c, s = dir_(x + sinal * c * passo / 2, y + sinal * s * passo / 2)
            x, y = x + sinal * c * passo, y + sinal * s * passo
            if not (-2 <= x <= w + 2 and -2 <= y <= h + 2) or not livre(x, y, dsep * dtest):
                break
            if len(pts) > 14 and (pts[-14][0] - x) ** 2 + (pts[-14][1] - y) ** 2 < (passo * 3) ** 2:
                break
            pts.append((x, y))
        return pts
    sementes = [(x, y) for x in np.arange(dsep / 2, w, dsep) for y in np.arange(dsep / 2, h, dsep)]
    g.shuffle(sementes)
    linhas_ = []
    for x, y in sementes:
        x += g.uniform(-dsep / 3, dsep / 3)
        y += g.uniform(-dsep / 3, dsep / 3)
        if not livre(x, y, dsep):
            continue
        ln = integra(x, y, -1)[::-1] + [(x, y)] + integra(x, y, 1)
        if len(ln) * passo < min_len:
            continue
        linhas_.append(ln[::2] + ([ln[-1]] if len(ln) % 2 == 0 else []))
        for px, py in ln:
            grade.setdefault((int(px // cel), int(py // cel)), []).append((px, py))
    return linhas_


def _quebra_saltos(linhas_, lim):
    out = []
    for p in linhas_:
        cur = [p[0]]
        for q in p[1:]:
            if (q[0] - cur[-1][0]) ** 2 + (q[1] - cur[-1][1]) ** 2 > lim * lim:
                if len(cur) > 3:
                    out.append(cur)
                cur = []
            cur.append(q)
        if len(cur) > 3:
            out.append(cur)
    return out


def fluxo(f, modo="cilindro", w=1080, h=1080, dsep=None, cor=None, k=0.6, mostra=False, seed=0, fundo_claro=False):
    """Campo de fluxo. Física de verdade: cilindro (escoamento em volta de um obstáculo), dipolo (linhas de campo entre
    2 polos), ralo (vórtice + sorvedouro). Ruído: ruido (no ângulo da ficha), quantizado (π/10), pelos (traços curtos)."""
    cor = cor or f.tinta
    dsep = dsep or f.unidade * 0.62
    corpo = ""
    if modo in ("cilindro", "dipolo", "ralo"):
        passo = 3.0
        gy, gx = np.mgrid[0:int(h / passo) + 2, 0:int(w / passo) + 2].astype(float) * passo
        psi, R = _psi(modo, gx, gy, w, h, f.angulo)
        if modo == "cilindro":
            # sem os 2 níveis de |ψ| = dsep/2: colados ao disco (R + 3,7 px) eram engolidos pelo recorte e deixavam só
            # fiapos com gancho junto aos pontos de estagnação (esq./dir.)
            niv = np.arange(-h, h, dsep) + dsep / 2
            cs = contornos(np.nan_to_num(psi, nan=0.0), niv[np.abs(niv) > dsep], passo, tol=0.3)
            # a linha QUEBRA onde entra no obstáculo (antes: filtrava os pontos e a curva suave ligava os dois lados
            # por uma corda atravessando o círculo; as linhas coladas ao eixo viravam fiapo/gancho junto ao disco)
            r2min = (R * 1.03) ** 2
            fora = []
            for c in cs:
                for p in c:
                    cur = []
                    for q in p:
                        if (q[0] - w / 2) ** 2 + (q[1] - h / 2) ** 2 > r2min:
                            cur.append(q)
                        else:
                            if len(cur) > 2:
                                fora.append(cur)
                            cur = []
                    if len(cur) > 2:
                        fora.append(cur)
            def _comp(p):
                return sum(math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in zip(p, p[1:]))

            def _toca(p):          # ponta encostada no obstáculo (a linha foi cortada por ele)
                return any((q[0] - w / 2) ** 2 + (q[1] - h / 2) ** 2 < (R * 1.12) ** 2 for q in (p[0], p[-1]))
            # fiapos curtos nascidos do eixo de estagnação (pontas soltas com gancho junto ao disco) saem
            fora = [p for p in fora if _comp(p) > (10 * dsep if _toca(p) else 3 * dsep)]
            corpo += _ln(fora, cor, _esp(f, k), suave=True)
            if mostra:
                corpo += f'<circle cx="{w / 2}" cy="{h / 2}" r="{R:.1f}" fill="{f.acento}"/>'
        elif modo == "dipolo":
            lv = [v for v in np.linspace(-1.94, 1.94, 28)]
            cs = contornos(psi, lv, passo, tol=0.3)
            corpo += _ln([p for c in cs for p in c], cor, _esp(f, k), suave=True)
            if mostra:
                a = math.radians(f.angulo)
                for s_ in (-1, 1):
                    corpo += (f'<circle cx="{w / 2 + s_ * R * math.cos(a):.1f}" cy="{h / 2 + s_ * R * math.sin(a):.1f}" '
                              f'r="{f.unidade * 0.5:.1f}" fill="{f.acento}"/>')
        else:
            dpx, dpy = psi
            corpo += _ln(_streamlines(dpy, -dpx, w, h, passo, dsep, seed=semente(f, "ralo", seed)), cor, _esp(f, k),
                         cap="round")
    else:
        esc = 6.0
        gw, gh = int(w / esc) + 2, int(h / esc) + 2
        nz = campo_ruido(gw, gh, gw / 2.2, 3, semente(f, "fluxo", modo, seed), warp=4)
        base = math.radians(f.angulo)
        if modo == "quantizado":
            ang = np.round((base + nz * math.pi * 0.9) / (math.pi / 10)) * (math.pi / 10)
        elif modo == "pelos":
            ang = base + nz * math.pi * 1.2
        else:
            ang = base + nz * math.pi * 0.55
        cosf, sinf = np.cos(ang), np.sin(ang)
        if modo == "pelos":
            g = nprng(f, "pelos", seed)
            linhas_ = []
            for x, y in g.uniform(0, 1, (1500, 2)) * (w, h):
                ln = [(x, y)]
                for _ in range(int(g.uniform(7, 17))):
                    i, j = int(min(max(y / esc, 0), gh - 1)), int(min(max(x / esc, 0), gw - 1))
                    x, y = x + cosf[i, j] * 2, y + sinf[i, j] * 2
                    ln.append((x, y))
                linhas_.append(ln)
            corpo += _ln(linhas_, cor, _esp(f, k), cap="round")
        else:
            linhas_ = _streamlines(cosf, sinf, w, h, esc, dsep, seed=semente(f, "fl", modo, seed),
                                   min_len=60 if modo == "ruido" else 40)
            corpo += _ln(linhas_, cor, _esp(f, k), cap="round")
    nomes = {"cilindro": "fluxo · escoamento em volta do cilindro", "dipolo": "fluxo · linhas de campo (2 polos)",
             "ralo": "fluxo · vórtice + ralo", "ruido": "fluxo · ruído no ângulo da ficha",
             "quantizado": "fluxo · ângulos quantizados (π/10)", "pelos": "fluxo · traços curtos (pelo)"}
    nota = {"cilindro": "o obstáculo é o assunto (foto/logo no lugar do círculo); ",
            "dipolo": "liga 2 coisas (antes → depois, professor ↔ aluno); "}.get(modo, "campo com origem > Perlin solto; ")
    return _campo(w, h, corpo, nomes[modo] + (" · com obstáculo" if mostra else ""), nota + NOTA_CAMPO,
                  clip=_ret(w, h), fundo_claro=fundo_claro)


# ================================================================ amostras
@amostra(FAM, "topografia")
def _a_topo(f):
    return [topografia(f), topografia(f, niveis=34, cor=f.apoio, k=0.5, seed=2),
            topografia(f, niveis=10, k=0.9, picos=2, seed=3), topografia(f, acento_nivel=11, seed=4),
            topografia(f, circulo=True, niveis=22, seed=5), topografia(f, w=1080, h=360, niveis=14, picos=4, seed=6),
            topografia(f, terraco=True, niveis=14, seed=7),
            topografia(f, cor=f.fundo, niveis=20, seed=8, fundo_claro=True)]


@amostra(FAM, "ondas")
def _a_ondas(f):
    return [ondas(f), ondas(f, modo="fase", n=40), ondas(f, modo="pulso", n=30), ondas(f, modo="amortecida", n=22),
            ondas(f, modo="interferencia", n=36, cor=f.apoio), ondas(f, modo="relevo", n=40),
            ondas(f, modo="faixas", n=28, ciclos=2.2, amp=26), ondas(f, modo="vertical", n=26, ciclos=1.5),
            ondas(f, modo="fase", n=30, cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "espirais")
def _a_esp(f):
    return [espiral(f), espiral(f, "afinando", voltas=11), espiral(f, "dupla", voltas=10),
            espiral(f, "logaritmica"), espiral(f, "quadrada", voltas=14), espiral(f, "perspectiva", voltas=14),
            espiral(f, "tracejada", voltas=9, cor=f.acento), espiral(f, "fermat", voltas=18, cor=f.apoio),
            espiral(f, voltas=22, cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "campo de fluxo")
def _a_fluxo(f):
    return [fluxo(f), fluxo(f, mostra=True), fluxo(f, "dipolo"), fluxo(f, "dipolo", mostra=True, cor=f.apoio),
            fluxo(f, "ralo"), fluxo(f, "ruido"), fluxo(f, "quantizado"), fluxo(f, "pelos", cor=f.apoio),
            fluxo(f, "ruido", cor=f.fundo, seed=3, fundo_claro=True)]


# ================================================================ 5. guilloché (padrão de cédula)
def _hipo(R, r, d, m=None, epi=False):
    """Hipotrocoide (ou epitrocoide) fechada: o torno de gravação de cédula / Espirógrafo."""
    per = r // math.gcd(R, r)
    m = m or int(per * R * 26)
    t = np.linspace(0, 2 * math.pi * per, m)
    if epi:
        x = (R + r) * np.cos(t) - d * np.cos((R + r) * t / r)
        y = (R + r) * np.sin(t) - d * np.sin((R + r) * t / r)
    else:
        x = (R - r) * np.cos(t) + d * np.cos((R - r) * t / r)
        y = (R - r) * np.sin(t) - d * np.sin((R - r) * t / r)
    return np.stack([x, y], 1)


def _copias(id_, d, cor, e, n, passo, cx, cy, modo="rot"):
    """1 curva no <defs> + N cópias por <use> (girar uma curva periódica = deslocar a fase): arquivo leve."""
    defs = f'<path id="{id_}" d="{d}"/>'
    uses = "".join(f'<use href="#{id_}" transform="rotate({i * passo:.4g} {cx:g} {cy:g})"/>' if modo == "rot" else
                   f'<use href="#{id_}" transform="translate({i * passo:.4g} 0)"/>' for i in range(n))
    return defs, f'<g {traco_attr(cor, e)}>{uses}</g>'


def guilloche(f, modo="roseta", w=1080, h=1080, cor=None, k=0.5, seed=0, fundo_claro=False):
    """Guilloché (torno de cédula): 1 curva periódica girada N vezes = trama fina com profundidade.
    modo: roseta · roseta2 · renda (hipotrocoide girada) · epitrocoide · anel · anel2 · faixa · medalhao."""
    cor = cor or f.tinta
    cx, cy = w / 2, h / 2
    R = 0.47 * min(w, h)
    e = _esp(f, k)
    th = np.linspace(0, 2 * math.pi, 2400)

    def polar(rr):
        return np.stack([cx + rr * np.cos(th), cy + rr * np.sin(th)], 1)
    defs, corpo = "", ""
    if modo in ("roseta", "roseta2", "medalhao"):
        n_p, M = 16, 22
        a, b = (0.6, 0.36) if modo == "roseta" else (0.72, 0.24)
        d0, u0 = _copias("g0", caminho(polar(R * (a + b * np.cos(n_p * th))), True), cor, e, M, 360 / n_p / M, cx, cy)
        defs += d0
        corpo += u0
        if modo == "roseta2":
            d1, u1 = _copias("g1", caminho(polar(R * (0.3 + 0.16 * np.cos(10 * th))), True), f.acento, e, 18,
                             360 / 10 / 18, cx, cy)
            defs, corpo = defs + d1, corpo + u1
        if modo == "medalhao":
            d1, u1 = _copias("g1", caminho(polar(R * (0.36 + 0.1 * np.sin(22 * th))), True), f.acento, e, 14,
                             360 / 22 / 14, cx, cy)
            defs, corpo = defs + d1, corpo + u1
    elif modo == "renda":
        P = _hipo(29, 10, 9) * (R / 28) + (cx, cy)
        d0, u0 = _copias("g0", caminho(P, True), cor, e, 8, 360 / 29 / 8, cx, cy)
        defs, corpo = d0, u0
    elif modo == "epitrocoide":
        P = _hipo(24, 7, 6, epi=True) * (R / 37) + (cx, cy)
        d0, u0 = _copias("g0", caminho(P, True), cor, e, 3, 360 / 24 / 3, cx, cy)
        defs, corpo = d0, u0
    elif modo in ("anel", "anel2"):
        aneis = [(0.8, 0.12, 30, 20)] if modo == "anel" else [(0.84, 0.1, 40, 16), (0.52, 0.09, 26, 14)]
        for i, (Rc, A, kk, M) in enumerate(aneis):
            rr = R * (Rc + A * np.sin(kk * th) + A * 0.35 * np.sin(kk * 2 * th + 1.0))
            d0, u0 = _copias(f"g{i}", caminho(polar(rr), True), cor, e, M, 360 / kk / M, cx, cy)
            defs, corpo = defs + d0, corpo + u0
    elif modo == "faixa":
        lam = w / 8
        xs = np.linspace(-lam, w + lam, 1400)
        y = h / 2 + h * 0.3 * np.sin(2 * math.pi * xs / lam) + h * 0.08 * np.sin(2 * math.pi * xs / lam * 3)
        M = 12
        d0, u0 = _copias("g0", caminho(np.stack([xs - lam, y], 1)), cor, e, M, lam / M, cx, cy, modo="tr")
        defs, corpo = d0, u0
    nomes = {"roseta": "guilloché · roseta", "roseta2": "guilloché · roseta em 2 tintas", "renda": "guilloché · renda (hipotrocoide)",
             "epitrocoide": "guilloché · epitrocoide", "anel": "guilloché · anel trançado",
             "anel2": "guilloché · anéis concêntricos", "faixa": "guilloché · faixa de borda", "medalhao": "guilloché · medalhão"}
    return _campo(w, h, corpo, nomes[modo], "certificado, ingresso, 'valor', premium; 1 cor fina, contraste baixo; "
                  "nunca sob texto pequeno", defs=defs, clip=_ret(w, h), fundo_claro=fundo_claro)


# ================================================================ 6. moiré calculado
def moire(f, modo="linhas", w=1080, h=1080, p=9.0, D=260.0, cor=None, cor2=None, seed=0, fundo_claro=False):
    """Moiré pela fórmula: 2 grades de passo p, a 2ª girada α = p/D (rad) → faixas de largura D.
    modo: linhas · escala (p e p·(1+p/D): batimento a cada D) · circulos · radial · onda · grade · cores."""
    cor = cor or f.tinta
    cor2 = cor2 or (f.acento if modo == "cores" else cor)
    e = max(1.5, p * 0.36)
    cx, cy = w / 2, h / 2
    L = math.hypot(w, h)

    def grade_(passo, ang, ondula=0.0):
        a = math.radians(ang)
        ls = []
        n = int(L / passo) + 2
        ts = np.linspace(-L / 2, L / 2, 220 if ondula else 2)
        for i in range(-n // 2, n // 2 + 1):
            off = i * passo
            ys = off + (ondula * np.sin(ts / 60.0) if ondula else 0 * ts)
            x = cx + ts * math.cos(a) - ys * math.sin(a)
            y = cy + ts * math.sin(a) + ys * math.cos(a)
            ls.append(np.stack([x, y], 1))
        return ls
    alfa = math.degrees(p / D)
    corpo = ""
    if modo in ("linhas", "cores"):
        corpo = _ln(grade_(p, f.angulo), cor, e) + _ln(grade_(p, f.angulo + alfa), cor2, e)
    elif modo == "escala":
        corpo = _ln(grade_(p, 90), cor, e) + _ln(grade_(p * (1 + p / D), 90), cor2, e)
    elif modo == "onda":
        xs = np.linspace(-20, w + 20, 300)
        base = caminho(np.stack([xs, p * 1.4 * np.sin(xs / 60.0)], 1))
        uses = "".join(f'<use href="#mo" transform="translate(0 {y:.1f})"/>' for y in np.arange(-p, h + 2 * p, p))
        corpo = (_ln(grade_(p, 0), cor, e) + f'<defs><path id="mo" d="{base}"/></defs>'
                 f'<g {traco_attr(cor2, e)}>{uses}</g>')
    elif modo == "grade":
        corpo = (_ln(grade_(p * 1.4, 0) + grade_(p * 1.4, 90), cor, e * 0.8)
                 + _ln(grade_(p * 1.4, alfa * 1.4) + grade_(p * 1.4, 90 + alfa * 1.4), cor2, e * 0.8))
    elif modo == "circulos":
        for dx in (-1.6 * p, 1.6 * p):
            cs = "".join(f'<circle cx="{cx + dx:.1f}" cy="{cy:g}" r="{r:.1f}"/>' for r in np.arange(p, L / 1.6, p))
            corpo += f'<g {traco_attr(cor if dx < 0 else cor2, e)}>{cs}</g>' 
    elif modo == "radial":
        n = 180
        for dx in (-p * 2.2, p * 2.2):
            r0 = p * 9                   # sem miolo: os raios não empastam num borrão branco no centro
            ls = [[(cx + dx + r0 * math.cos(2 * math.pi * i / n), cy + r0 * math.sin(2 * math.pi * i / n)),
                   (cx + dx + L * math.cos(2 * math.pi * i / n), cy + L * math.sin(2 * math.pi * i / n))] for i in range(n)]
            corpo += _ln(ls, cor if dx < 0 else cor2, e * 0.8)
    nomes = {"linhas": "moiré · 2 grades (α = p/D)", "escala": "moiré · batimento de passos",
             "circulos": "moiré · círculos deslocados", "radial": "moiré · raios deslocados", "onda": "moiré · reta × onda",
             "grade": "moiré · grade cruzada", "cores": "moiré · 2 tintas"}
    return _campo(w, h, corpo, nomes[modo], f"calculado: p={p:g}px, faixas de {D:g}px; exportar SEM reamostrar; "
                  "herói/transição, nunca sob texto", clip=_ret(w, h), fundo_claro=fundo_claro)


# ================================================================ 7. hachura
def _paralelas(w, h, ang, posicoes):
    a = math.radians(ang)
    L = math.hypot(w, h)
    cx, cy = w / 2, h / 2
    out = []
    for s in posicoes:
        x0, y0 = cx - L / 2 * math.cos(a) - s * math.sin(a), cy - L / 2 * math.sin(a) + s * math.cos(a)
        x1, y1 = cx + L / 2 * math.cos(a) - s * math.sin(a), cy + L / 2 * math.sin(a) + s * math.cos(a)
        out.append([(x0, y0), (x1, y1)])
    return out


def hachura(f, modo="paralela", w=1080, h=1080, passo=10.0, ang=45.0, cor=None, k=0.65, seed=0, fundo_claro=False):
    """Hachura. modo: paralela · sistema (no ângulo da ficha) · cruzada · tom (passo variável) · esfera (segue o
    volume, gravura) · mao (traço solto) · bloco (sombra chapada) · tracejada."""
    cor = cor or f.tinta
    e = _esp(f, k)
    L = math.hypot(w, h)
    corpo, clip, caixa = "", _ret(w, h), None
    if modo in ("paralela", "sistema", "tracejada"):
        a = f.angulo + 90 if modo == "sistema" else ang
        ls = _paralelas(w, h, a, np.arange(-L / 2, L / 2, passo))
        extra = f' stroke-dasharray="{passo * 1.6:.1f} {passo * 0.9:.1f}"' if modo == "tracejada" else ""
        corpo = _ln(ls, cor, e, extra=extra)
    elif modo == "cruzada":
        pos = np.arange(-L / 2, L / 2, passo)
        corpo = _ln(_paralelas(w, h, ang, pos) + _paralelas(w, h, ang + 90, pos), cor, e)
    elif modo == "tom":
        pos, s = [], -L / 2
        while s < L / 2:
            pos.append(s)
            u = (s + L / 2) / L
            s += 4.5 + 26 * u ** 1.6
        corpo = _ln(_paralelas(w, h, ang, pos), cor, e)
    elif modo == "esfera":        # gravura: anéis de "latitude" de um eixo inclinado, só onde há sombra (ou luz)
        R = 0.4 * min(w, h)
        cx, cy = w / 2, h / 2
        Lz = np.array([-0.55, -0.62, 0.56])
        Lz /= np.linalg.norm(Lz)
        ls = []
        for fam_, (ax, lims) in enumerate((((math.radians(ang), 0.95), (0.8, 0.55, 0.32)),
                                            ((math.radians(ang + 90), 0.95), (0.14, 0.14, 0.08)))):
            a_, b_ = ax
            n = np.array([math.cos(a_) * math.sin(b_), math.sin(a_) * math.sin(b_), math.cos(b_)])
            u = np.cross(n, [0, 0, 1.0])
            u /= np.linalg.norm(u)
            v = np.cross(n, u)
            phi = np.linspace(0, 2 * math.pi, 420)
            for i, c_ in enumerate(np.arange(-0.98, 0.98, passo / R)):
                rho = math.sqrt(max(0.0, 1 - c_ * c_))
                P3 = c_ * n + rho * (np.cos(phi)[:, None] * u + np.sin(phi)[:, None] * v)
                luz = np.clip(P3 @ Lz, 0, 1)
                val = luz if not fundo_claro else 1 - luz
                ok = (P3[:, 2] > (0.04 if fam_ == 0 else 0.3)) & (val > 1 - lims[i % 3])
                cur = []
                for q, k_ in zip(P3, ok):
                    if k_:
                        cur.append((cx + q[0] * R, cy + q[1] * R))
                    elif len(cur) > 1:
                        ls.append(cur)
                        cur = []
                    else:
                        cur = []
                if len(cur) > 1:
                    ls.append(cur)
        corpo = _ln(ls, cor, e, cap="round") + f'<circle cx="{cx}" cy="{cy}" r="{R:.1f}" {traco_attr(cor, e * 0.8, 0.85)}/>'
        caixa = (cx - R - e, cy - R - e, cx + R + e, cy + R + e)
    elif modo == "mao":
        r = rng(f, "hach-mao", seed)
        bw, bh = w * 0.8, h * 0.5
        x0, y0 = (w - bw) / 2, (h - bh) / 2
        ls = []
        s = 0
        while s < bw + bh:
            p0 = (x0 + min(s, bw) + r.gauss(0, 2), y0 + max(0, s - bw) + r.gauss(0, 2))
            p1 = (x0 + max(0, s - bh) + r.gauss(0, 2), y0 + min(s, bh) + r.gauss(0, 2))
            mx, my = (p0[0] + p1[0]) / 2 + r.gauss(0, 2.5), (p0[1] + p1[1]) / 2 + r.gauss(0, 2.5)
            ls.append([p0, (mx, my), p1])
            s += passo * r.uniform(0.85, 1.25)
        corpo = _ln(ls, cor, e, cap="round", suave=True)
        caixa = (x0 - 6, y0 - 6, x0 + bw + 6, y0 + bh + 6)
    elif modo == "bloco":
        bw, bh = w * 0.7, h * 0.42
        x0, y0 = (w - bw) / 2, (h - bh) / 2
        defs_clip = f'<rect x="{x0}" y="{y0}" width="{bw}" height="{bh}"/>'
        corpo = (f'<g clip-path="url(#blk)">{_ln(_paralelas(w, h, ang, np.arange(-L / 2, L / 2, passo)), cor, e)}</g>'
                 f'<rect x="{x0}" y="{y0}" width="{bw}" height="{bh}" {traco_attr(cor, e * 1.6)}/>')
        corpo = f'<defs><clipPath id="blk">{defs_clip}</clipPath></defs>' + corpo
        caixa = (x0 - e, y0 - e, x0 + bw + e, y0 + bh + e)
    nomes = {"paralela": f"hachura {ang:g}°", "sistema": "hachura no ângulo da ficha", "cruzada": "hachura cruzada",
             "tom": "hachura com tom (passo variável)", "esfera": "hachura que segue o volume (gravura)",
             "mao": "hachura solta à mão", "bloco": "hachura · sombra chapada em bloco", "tracejada": "hachura tracejada"}
    return _campo(w, h, corpo, nomes[modo], f"passo {passo:g}px (6–12), traço {e:.3g}px; 1–2 ângulos; " + NOTA_CAMPO,
                  clip=clip, caixa=caixa, fundo_claro=fundo_claro)


# ================================================================ 8. op-art
def _bojo(P, c, R, k):
    """Lente esférica: aproxima/afasta pontos do centro (k > 0 amplia o meio)."""
    d = P - c
    r = np.hypot(d[:, 0], d[:, 1])[:, None]
    g = np.where(r < R, (r / R) ** (1 - k) * R / np.maximum(r, 1e-9), 1.0)
    return c + d * g


def op_art(f, modo="bojo", w=1080, h=1080, cor=None, seed=0, fundo_claro=False):
    """Op-art (Vasarely/Riley como princípio, nunca cópia). modo: bojo · corrente · tabuleiro · aneis · torcidas ·
    quadrados · pinwheel."""
    cor = cor or f.tinta
    c = np.array([w / 2, h / 2])
    corpo, polys = "", []
    if modo == "bojo":
        n = 36
        ys = np.linspace(-10, h + 10, 240)
        bords = []
        for i in range(n + 1):
            x0 = i * w / n
            P = _bojo(np.stack([np.full_like(ys, x0), ys], 1), c, 0.46 * w, 0.32)
            bords.append(P)
        polys = [np.vstack([bords[i], bords[i + 1][::-1]]) for i in range(0, n, 2)]
    elif modo == "corrente":
        ls = []
        n = 46
        xs = np.linspace(-10, w + 10, 500)
        for i in range(n):
            y0 = (i + 0.5) * h / n
            lam = 260 - 200 * (i / n)
            ls.append(np.stack([xs, y0 + 9 * np.sin(2 * math.pi * xs / lam + i * 0.3)], 1))
        corpo = _ln(ls, cor, _esp(f, 1.0))
    elif modo == "tabuleiro":
        n = 16
        s = w / n
        for i in range(n):
            for j in range(n):
                if (i + j) % 2:
                    continue
                t = np.linspace(0, 1, 8)[:, None]
                a, b, cc, d = np.array([j * s, i * s]), np.array([(j + 1) * s, i * s]), \
                    np.array([(j + 1) * s, (i + 1) * s]), np.array([j * s, (i + 1) * s])
                P = np.vstack([a + (b - a) * t, b + (cc - b) * t, cc + (d - cc) * t, d + (a - d) * t])
                polys.append(_bojo(P, c, 0.5 * w, 0.33))
    elif modo == "aneis":
        n = 24
        th = np.linspace(0, 2 * math.pi, 300)
        R = 0.5 * math.hypot(w, h)
        for i in range(0, n, 2):
            r1, r2 = (n - i) * R / n, (n - i - 1) * R / n
            d1, d2 = (i / n) * 0.25 * w, ((i + 1) / n) * 0.25 * w
            o = np.stack([c[0] - d1 + r1 * np.cos(th), c[1] + r1 * np.sin(th)], 1)
            inn = np.stack([c[0] - d2 + r2 * np.cos(th), c[1] + r2 * np.sin(th)], 1)
            polys.append(o)
            polys.append(inn[::-1])
    elif modo == "torcidas":
        ls = []
        n = 52
        xs = np.linspace(-10, w + 10, 400)
        for i in range(n):
            y0 = (i + 0.5) * h / n
            amp = 42 * math.sin(math.pi * y0 / h) ** 2
            ls.append(np.stack([xs, y0 + amp * np.sin(2 * math.pi * xs / 360 + y0 / 90)], 1))
        corpo = _ln(ls, cor, _esp(f, 1.0))
    elif modo == "quadrados":
        n, d = 30, math.radians(3.6)
        ls, meio, a = [], 0.48 * min(w, h), 0.0
        for i in range(n):
            sq = [(c[0] + meio * math.sqrt(2) * math.cos(a + q), c[1] + meio * math.sqrt(2) * math.sin(a + q))
                  for q in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4, math.pi / 4)]
            ls.append(sq)
            meio /= (math.cos(d) + math.sin(d))
            a += d
        corpo = _ln(ls, cor, _esp(f, 0.8)).replace('stroke-linejoin="round"', 'stroke-linejoin="miter"')
    elif modo == "pinwheel":
        n = 40
        rs = np.linspace(0, 0.75 * w, 120)
        for i in range(0, n, 2):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            tw = rs / (0.75 * w) * 1.4
            e1 = np.stack([c[0] + rs * np.cos(a0 + tw), c[1] + rs * np.sin(a0 + tw)], 1)
            e2 = np.stack([c[0] + rs * np.cos(a1 + tw), c[1] + rs * np.sin(a1 + tw)], 1)
            polys.append(np.vstack([e1, e2[::-1]]))
    if polys:
        corpo = _cheio(polys, cor, regra="evenodd" if modo == "aneis" else "nonzero")
    nomes = {"bojo": "op-art · listras com bojo", "corrente": "op-art · corrente (frequência crescente)",
             "tabuleiro": "op-art · tabuleiro com lente", "aneis": "op-art · anéis excêntricos",
             "torcidas": "op-art · linhas torcidas", "quadrados": "op-art · quadrados girando",
             "pinwheel": "op-art · cata-vento torcido"}
    return _campo(w, h, corpo, nomes[modo], "P&B ou 2 cores, UMA deformação, fundo de 1 peça-herói; vibra: nunca atrás "
                  "de texto", clip=_ret(w, h), fundo_claro=fundo_claro)


# ================================================================ 9. grade distorcida
def grade_distorcida(f, modo="poco", w=1080, h=1080, passo=36.0, cor=None, k=0.5, seed=0, fundo_claro=False):
    """Grade regular deformada — a deformação É o conceito (peso afundando = força). modo: poco · lente · onda ·
    torcao · massa3d · dois · impacto."""
    cor = cor or f.tinta
    c = np.array([w / 2, h / 2])
    s = 0.24 * min(w, h)

    def deforma(P):
        d = P - c
        r2 = (d ** 2).sum(1)[:, None]
        g = np.exp(-r2 / (2 * s * s))
        if modo == "poco":
            return P - d * 0.55 * g
        if modo == "lente":
            return _bojo(P, c, 0.42 * min(w, h), 0.42)
        if modo == "onda":
            return P + np.stack([14 * np.sin(2 * math.pi * P[:, 1] / 260), 14 * np.sin(2 * math.pi * P[:, 0] / 260)], 1)
        if modo == "torcao":
            th = 1.4 * g[:, 0]
            co, si = np.cos(th), np.sin(th)
            return c + np.stack([d[:, 0] * co - d[:, 1] * si, d[:, 0] * si + d[:, 1] * co], 1)
        if modo == "dois":
            out = P.copy()
            for cc in (c + (-0.22 * w, -0.1 * h), c + (0.24 * w, 0.14 * h)):
                dd = out - cc
                gg = np.exp(-(dd ** 2).sum(1)[:, None] / (2 * (0.16 * w) ** 2))
                out = out - dd * 0.5 * gg
            return out
        if modo == "impacto":       # anel de impacto: onda radial que amortece (salto, pancada, aterrissagem)
            r = np.sqrt(r2)
            return P + d / np.maximum(r, 1e-6) * (24 * np.sin(r / 40.0) * np.exp(-r / (0.4 * min(w, h))))
        return P
    ls = []
    e = _esp(f, k)
    if modo == "massa3d":         # a massa afunda o plano (gravidade/força): grade 3D em perspectiva
        N = 30
        u = np.linspace(-3.2, 3.2, 300)
        tilt, foco, zc0 = math.radians(44), w * 1.4, 3.0
        sig, prof = 0.36, 0.62

        def proj(X, Y, Z=None):
            Z = -prof * np.exp(-(X ** 2 + Y ** 2) / (2 * sig ** 2)) if Z is None else Z
            yc = Y * math.cos(tilt) - Z * math.sin(tilt)
            zc = Y * math.sin(tilt) + Z * math.cos(tilt) + zc0
            return np.stack([w / 2 + X / zc * foco, h * 0.36 + yc / zc * foco], 1), zc
        vy = np.linspace(-2.3, 2.7, 260)
        for v in np.arange(-3.2, 3.21, 0.2):
            ls.append(proj(np.full_like(vy, v), vy)[0])
        for v in np.arange(-2.3, 2.71, 0.2):
            ls.append(proj(u, np.full_like(u, v))[0])
        corpo = _ln(ls, cor, e)
        rb = 0.17
        (pc,), zc = proj(np.array([0.0]), np.array([0.0]), np.array([-prof + rb]))
        corpo += f'<circle cx="{pc[0]:.1f}" cy="{pc[1]:.1f}" r="{rb / zc[0] * foco:.1f}" fill="{f.acento}"/>'
    else:
        xs = np.arange(-passo * 2, w + passo * 2.1, 4.0)
        for v in np.arange(-passo * 2, w + passo * 2.1, passo):
            ls.append(deforma(np.stack([xs, np.full_like(xs, v)], 1)))
            ls.append(deforma(np.stack([np.full_like(xs, v), xs], 1)))
        corpo = _ln(ls, cor, e)
    nomes = {"poco": "grade · poço (peso afunda)", "lente": "grade · lente", "onda": "grade · onda",
             "torcao": "grade · torção", "massa3d": "grade · massa curvando o plano (3D)", "dois": "grade · 2 poços",
             "impacto": "grade · impacto (onda radial)"}
    return _campo(w, h, corpo, nomes[modo], "a deformação é a ideia (força, falta, foco); grade presa à ficha; "
                  + NOTA_CAMPO, clip=_ret(w, h), fundo_claro=fundo_claro)


@amostra(FAM, "guilloché")
def _a_guil(f):
    return [guilloche(f), guilloche(f, "roseta2"), guilloche(f, "renda"), guilloche(f, "epitrocoide", cor=f.apoio),
            guilloche(f, "anel"), guilloche(f, "anel2", cor=f.acento), guilloche(f, "faixa", w=1080, h=240),
            guilloche(f, "medalhao"), guilloche(f, "roseta", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "moiré")
def _a_moire(f):
    return [moire(f), moire(f, "escala"), moire(f, "circulos"), moire(f, "radial"), moire(f, "onda"),
            moire(f, "cores"), moire(f, cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "hachuras")
def _a_hach(f):
    return [hachura(f), hachura(f, "sistema", passo=12), hachura(f, "cruzada", passo=14, cor=f.apoio),
            hachura(f, "tom"), hachura(f, "esfera", passo=11), hachura(f, "mao", passo=14, cor=f.acento),
            hachura(f, "bloco", passo=9), hachura(f, "tracejada", passo=12, ang=-45, cor=f.apoio),
            hachura(f, "esfera", passo=10, cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "op-art")
def _a_op(f):
    return [op_art(f), op_art(f, "corrente"), op_art(f, "tabuleiro"), op_art(f, "aneis"), op_art(f, "torcidas"),
            op_art(f, "quadrados"), op_art(f, "pinwheel", cor=f.acento), op_art(f, "bojo", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "grade distorcida")
def _a_gd(f):
    return [grade_distorcida(f), grade_distorcida(f, "lente"), grade_distorcida(f, "onda", cor=f.apoio),
            grade_distorcida(f, "torcao"), grade_distorcida(f, "massa3d"), grade_distorcida(f, "dois"),
            grade_distorcida(f, "impacto"), grade_distorcida(f, "poco", cor=f.fundo, fundo_claro=True)]


# ================================================================ 10. pauta / linhas de notação
def pauta(f, modo="musica", w=1080, h=1080, cor=None, k=0.6, seed=0, fundo_claro=False):
    """Linhas que 'seguram' coisas (pauta, caderno, caligrafia, planilha, numerada). O espaçamento sai da ficha
    (entrelinha = unidade); a pauta vem do ASSUNTO (música, aula, planilha), nunca solta."""
    from .nucleo import texto
    cor = cor or f.tinta
    e = _esp(f, k)
    m = 60.0
    corpo = ""
    ls, fortes, acento_ls = [], [], []
    if modo in ("musica", "compassos"):
        s = f.unidade * 0.75
        y = m + s
        while y + 4 * s < h - m:
            for i in range(5):
                ls.append([(m, y + i * s), (w - m, y + i * s)])
            fortes.append([(m, y), (m, y + 4 * s)])
            fortes.append([(w - m, y), (w - m, y + 4 * s)])
            if modo == "compassos":
                for x in np.linspace(m, w - m, 5)[1:-1]:
                    ls.append([(x, y), (x, y + 4 * s)])
            y += 4 * s + f.unidade * 2.6
    elif modo == "caderno":
        s = f.unidade * 1.34
        for y in np.arange(m * 2.2, h - m * 0.5, s):
            ls.append([(0, y), (w, y)])
        acento_ls += [[(m * 2, 0), (m * 2, h)], [(m * 2 + 6, 0), (m * 2 + 6, h)]]
    elif modo == "caligrafia":
        x_h = f.unidade * 1.2
        y = m + x_h
        while y + 2 * x_h < h - m:
            fortes.append([(m, y + x_h), (w - m, y + x_h)])                 # linha de base
            ls.append([(m, y - x_h * 0.7), (w - m, y - x_h * 0.7)])         # ascendente
            ls.append([(m, y + x_h * 1.7), (w - m, y + x_h * 1.7)])         # descendente
            corpo += _ln([[(m, y), (w - m, y)]], cor, e, 0.7,
                         extra=f' stroke-dasharray="{f.unidade * 0.4:.1f} {f.unidade * 0.3:.1f}"')   # altura-x
            y += x_h * 5.0
    elif modo == "planilha":
        s = f.unidade * 1.66
        for i, y in enumerate(np.arange(m, h - m + 1, s)):
            (fortes if i in (0, 1) else ls).append([(m, y), (w - m, y)])
        y_fim = m + s * int((h - 2 * m) / s)
        for x in (m, m + 0.34 * (w - 2 * m), m + 0.56 * (w - 2 * m), m + 0.78 * (w - 2 * m), w - m):
            ls.append([(x, m), (x, y_fim)])
    elif modo == "numerada":
        s = f.unidade * 1.66
        tam = f.unidade * 0.75          # anotação técnica (D27): número de linha lê a 100%, não vira pontinho
        for i, y in enumerate(np.arange(m + s, h - m + 1, s)):
            ls.append([(m * 1.9, y), (w - m, y)])
            t, _ = texto(f.fonte_mono, f"{i + 1:02d}", tam, m * 1.55, y - e * 1.5, f.apoio, anchor="end")
            corpo += t
    corpo = _ln(ls, cor, e) + _ln(fortes, cor, e * 2) + _ln(acento_ls, f.acento, e) + corpo
    nomes = {"musica": "pauta de 5 linhas", "compassos": "pauta com compassos", "caderno": "pauta de caderno + margem",
             "caligrafia": "pauta de caligrafia (base, x, asc., desc.)", "planilha": "pauta de planilha",
             "numerada": "linhas numeradas"}
    return _campo(w, h, corpo, nomes[modo], "a pauta vem do assunto; entrelinha = a do texto; números são textura "
                  "(não para ler)", fundo_claro=fundo_claro)


# ================================================================ 11. linhas de velocidade
def velocidade(f, modo="horizontal", w=1080, h=600, n=10, ang=None, cor=None, k=1.6, seed=0, fundo_claro=False):
    """Linhas de velocidade: poucas, comprimentos 1:4, mesmo ângulo, afinam na cauda (fio de largura variável).
    modo: horizontal · angulo · foco · curvas · grupo · vertical · acento."""
    r = rng(f, "vel", modo, seed)
    cor = cor or f.tinta
    e = _esp(f, k)
    polys, polys_ac, corpo = [], [], ""

    def risco(x0, y0, x1, y1, larg):
        t = np.linspace(0, 1, 40)
        P = np.stack([x0 + (x1 - x0) * t, y0 + (y1 - y0) * t], 1)
        return fita(P, larg * (0.04 + 0.96 * t ** 0.9))
    if modo in ("horizontal", "angulo", "vertical", "acento", "grupo"):
        a = {"angulo": f.angulo - 14, "vertical": 90}.get(modo, 0) if ang is None else ang
        cx, cy = w / 2, h / 2
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        L = (w if modo != "vertical" else h) * 0.84
        nn = 3 if modo == "grupo" else (7 if modo == "vertical" else n)
        alt = (h if modo != "vertical" else w) * (0.42 if modo == "grupo" else (0.5 if modo == "vertical" else 0.74))
        for i in range(nn):
            off = -alt / 2 + alt * (i + 0.5) / nn + r.gauss(0, alt / nn * 0.12)
            comp = L * (r.uniform(0.25, 0.92) if modo != "grupo" else (0.62, 0.95, 0.45)[i])
            fim = L / 2 - r.uniform(0, L * 0.22) - (L * 0.12 if modo == "vertical" else 0)
            ini = fim - comp
            p0 = (cx + ini * ca - off * sa, cy + ini * sa + off * ca)
            p1 = (cx + fim * ca - off * sa, cy + fim * sa + off * ca)
            larg = e * r.uniform(0.7, 1.3)
            (polys_ac if (modo == "acento" and i == nn // 2) else polys).append(risco(*p0, *p1, larg))
    elif modo == "foco":
        cx, cy, R0 = w / 2, h / 2, min(w, h) * 0.3
        for i in range(90):
            a = 2 * math.pi * i / 90 + r.uniform(-0.02, 0.02)
            r0 = R0 * r.uniform(1.0, 1.5)
            r1 = math.hypot(w, h) / 2 + 10
            polys.append(risco(cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r0 * math.cos(a), cy + r0 * math.sin(a),
                               e * r.uniform(0.8, 2.2))[::-1])
    elif modo == "curvas":
        cx, cy = w * 0.2, h * 1.35
        for i in range(7):
            R = h * (0.9 + 0.12 * i)
            a1 = math.radians(-58 + r.uniform(-3, 3))
            a0 = a1 - math.radians(r.uniform(14, 34))
            t = np.linspace(0, 1, 60)
            th = a0 + (a1 - a0) * t
            P = np.stack([cx + R * np.cos(th), cy + R * np.sin(th)], 1)
            polys.append(fita(P, e * (0.04 + 0.96 * t ** 0.9)))
    if modo != "foco":                 # cabe inteiro na caixa, com folga de 24 px (cauda nunca cortada na borda)
        todos_ = np.vstack(polys + polys_ac)
        x0_, y0_ = todos_.min(0)
        x1_, y1_ = todos_.max(0)
        k_ = min(1.0, (w - 48) / max(x1_ - x0_, 1), (h - 48) / max(y1_ - y0_, 1))
        mv = lambda P: (np.asarray(P) - ((x0_ + x1_) / 2, (y0_ + y1_) / 2)) * k_ + (w / 2, h / 2)  # noqa: E731
        polys, polys_ac = [mv(p) for p in polys], [mv(p) for p in polys_ac]
    corpo = _cheio(polys, cor) + (_cheio(polys_ac, f.acento) if polys_ac else "")
    nomes = {"horizontal": "velocidade · horizontais", "angulo": "velocidade · no ângulo do movimento",
             "foco": "velocidade · foco (zoom)", "curvas": "velocidade · arco (balanço)", "grupo": "velocidade · trio curto",
             "vertical": "velocidade · queda/salto", "acento": "velocidade · 1 no acento"}
    todos = polys + polys_ac
    return _campo(w, h, corpo, nomes[modo], "atrás de algo que SE MOVE (nunca de texto parado); 5–12 linhas, "
                  "comprimentos 1:4, afinam na cauda", clip=_ret(w, h),
                  caixa=caixa_de(todos) if modo not in ("foco",) else None, fundo_claro=fundo_claro)


# ================================================================ 12. raios (sunburst)
def raios(f, modo="cunhas", w=1080, h=1080, n=None, cor=None, k=0.7, seed=0, fundo_claro=False):
    """Raios. modo: cunhas · linhas · meio (nascente) · canto · miolo (centro livre p/ logo) · irregular · afinando ·
    tracejados."""
    r = rng(f, "raios", modo, seed)
    cor = cor or f.tinta
    e = _esp(f, k)
    cx, cy = {"meio": (w / 2, h), "canto": (0, 0)}.get(modo, (w / 2, h / 2))
    Rf = math.hypot(w, h) + 20
    a0, a1 = {"meio": (math.pi, 2 * math.pi), "canto": (math.radians(5), math.radians(85))}.get(modo, (0, 2 * math.pi))
    n = n or {"cunhas": 32, "linhas": 96, "meio": 22, "canto": 36, "miolo": 48, "irregular": 40, "afinando": 40,
              "tracejados": 48}[modo]
    polys, ls, corpo = [], [], ""
    for i in range(n):
        a = a0 + (a1 - a0) * (i + 0.5) / n
        da = (a1 - a0) / n / 2
        if modo in ("cunhas", "meio") and i % 2 == 0:
            polys.append([(cx, cy), (cx + Rf * math.cos(a - da), cy + Rf * math.sin(a - da)),
                          (cx + Rf * math.cos(a + da), cy + Rf * math.sin(a + da))])
        elif modo in ("linhas", "canto", "tracejados"):
            ri = min(w, h) * {"canto": 0.14, "tracejados": 0.2}.get(modo, 0.06)
            ls.append([(cx + ri * math.cos(a), cy + ri * math.sin(a)), (cx + Rf * math.cos(a), cy + Rf * math.sin(a))])
        elif modo == "miolo":
            ri = min(w, h) * 0.24
            polys.append([(cx + ri * math.cos(a), cy + ri * math.sin(a)),
                          (cx + Rf * math.cos(a - da * 0.5), cy + Rf * math.sin(a - da * 0.5)),
                          (cx + Rf * math.cos(a + da * 0.5), cy + Rf * math.sin(a + da * 0.5))])
        elif modo == "irregular":
            ri, rr = min(w, h) * r.uniform(0.1, 0.16), min(w, h) * r.uniform(0.26, 0.5)
            t = np.linspace(0, 1, 30)
            P = np.stack([cx + (ri + (rr - ri) * t) * math.cos(a), cy + (ri + (rr - ri) * t) * math.sin(a)], 1)
            polys.append(fita(P, e * 2.6 * (1 - t) ** 0.8 + 0.3))
        elif modo == "afinando":
            dd = da * 0.45
            polys.append([(cx, cy), (cx + Rf * math.cos(a - dd), cy + Rf * math.sin(a - dd)),
                          (cx + Rf * math.cos(a + dd), cy + Rf * math.sin(a + dd))])
    if polys:
        corpo += _cheio(polys, cor)
    if ls:
        extra = f' stroke-dasharray="{f.unidade * 0.9:.1f} {f.unidade * 0.6:.1f}"' if modo == "tracejados" else ""
        corpo += _ln(ls, cor, e, extra=extra)
    if modo == "miolo":
        corpo += f'<circle cx="{cx}" cy="{cy}" r="{min(w, h) * 0.2:.1f}" {traco_attr(f.acento, e * 1.5)}/>'
    nomes = {"cunhas": "raios · cunhas alternadas", "linhas": "raios · linhas finas", "meio": "raios · nascente",
             "canto": "raios · do canto", "miolo": "raios · centro livre", "irregular": "raios · explosão irregular",
             "afinando": "raios · cunhas finas", "tracejados": "raios · tracejados"}
    return _campo(w, h, corpo, nomes[modo], "o centro dos raios = o herói (produto, número, rosto); tempero retrô — "
                  "1 por série", clip=_ret(w, h), fundo_claro=fundo_claro)


# ================================================================ 13. círculos concêntricos
def concentricos(f, modo="iguais", w=1080, h=1080, cor=None, k=0.7, seed=0, fundo_claro=False):
    """Concêntricos. modo: iguais · geometrica · excentricos (anéis de árvore) · arco (arco-íris da base) · agua
    (ondulação) · radar (arcos com falhas) · quadrados (raio da ficha) · alternados."""
    r = rng(f, "conc", modo, seed)
    cor = cor or f.tinta
    e = _esp(f, k)
    cx, cy = w / 2, h / 2
    corpo = ""
    if modo == "iguais":
        corpo = "".join(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}"/>' for rr in np.arange(f.unidade, 0.75 * w, f.unidade))
        corpo = f'<g {traco_attr(cor, e)}>{corpo}</g>'
    elif modo == "geometrica":
        rr, cs = 6.0, ""
        while rr < 0.75 * w:
            cs += f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}"/>'
            rr *= 1.16
        corpo = f'<g {traco_attr(cor, e)}>{cs}</g>'
    elif modo == "excentricos":        # anéis de árvore: forma comum que evolui devagar → nunca se cruzam
        th = np.linspace(0, 2 * math.pi, 300)
        rr = __import__("random").Random(r.randrange(1 << 30))
        forma = sum(rr.uniform(0.4, 1) / kk * np.sin(kk * th + rr.uniform(0, 6.3)) for kk in range(2, 6))
        forma /= np.abs(forma).max()
        esp_ = 0.0145 * w
        ls = []
        for i in range(1, 31):
            R = i * esp_
            amp = 0.42 * esp_ * math.sqrt(i)
            rad = R + amp * forma
            ox, oy = i * 1.9, -i * 0.8
            ls.append(np.stack([cx - 0.03 * w + ox + rad * np.cos(th), cy + oy + rad * np.sin(th)], 1))
        corpo = _ln([np.vstack([p, p[:1]]) for p in ls], cor, e)
    elif modo == "arco":
        polys = []
        n = 12
        th = np.linspace(math.pi, 2 * math.pi, 160)
        for i in range(0, n, 2):
            r1, r2 = (n - i) / n * 0.5 * w, (n - i - 1) / n * 0.5 * w
            polys.append(np.vstack([np.stack([cx + r1 * np.cos(th), h + r1 * np.sin(th)], 1),
                                    np.stack([cx + r2 * np.cos(th[::-1]), h + r2 * np.sin(th[::-1])], 1)]))
        corpo = _cheio(polys, cor)
    elif modo == "agua":
        for i in range(1, 22):
            rr = 18 * i ** 1.25
            corpo += (f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="none" stroke="{cor}" '
                      f'stroke-width="{e * (1.8 - i * 0.06):.2f}" stroke-opacity="{max(0.08, 1 - i * 0.045):.2f}"/>')
    elif modo == "radar":
        ls = []
        for i in range(2, 22):
            R = i * 0.022 * w
            a = r.uniform(0, 2 * math.pi)
            for _ in range(r.randint(1, 3)):
                span = r.uniform(0.4, 2.2)
                th = np.linspace(a, a + span, max(8, int(span * R / 6)))
                ls.append(np.stack([cx + R * np.cos(th), cy + R * np.sin(th)], 1))
                a += span + r.uniform(0.3, 1.2)
        corpo = _ln(ls, cor, e, cap="round")
    elif modo == "quadrados":
        from .nucleo import ret
        ds = ""
        lados = list(np.arange(f.unidade * 2, 0.98 * w, f.unidade * 1.5))
        for i, s in enumerate(lados):          # raio aninhado: o de fora = raio_lg; cada anel de dentro perde o vão
            rr = max(0.0, min(f.raio_lg - (lados[-1] - s) / 2, s / 2))
            ds += f'<path d="{ret(cx - s / 2, cy - s / 2, s, s, rr)}"/>'
        corpo = f'<g {traco_attr(cor, e)}>{ds}</g>'
    elif modo == "alternados":
        cs = "".join(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" stroke-width="{e * (3.2 if i % 4 == 0 else 1):.2f}"/>'
                     for i, rr in enumerate(np.arange(f.unidade, 0.75 * w, f.unidade * 0.8)))
        corpo = f'<g fill="none" stroke="{cor}">{cs}</g>'
    nomes = {"iguais": "concêntricos · passo igual", "geometrica": "concêntricos · progressão geométrica",
             "excentricos": "concêntricos · anéis de crescimento", "arco": "concêntricos · arco da base",
             "agua": "concêntricos · ondulação", "radar": "concêntricos · arcos com falhas",
             "quadrados": "concêntricos · quadrados (raio da ficha)", "alternados": "concêntricos · fino/grosso"}
    return _campo(w, h, corpo, nomes[modo], "centro = o assunto (alvo, ponto de impacto); " + NOTA_CAMPO,
                  clip=_ret(w, h), fundo_claro=fundo_claro)


# ================================================================ 14. grade em perspectiva (chão)
def perspectiva(f, modo="chao", w=1080, h=1080, cor=None, k=0.6, seed=0, fundo_claro=False):
    """Chão em perspectiva (1 ponto de fuga). modo: chao · fade (some no horizonte) · tunel · deslocado · curvo ·
    pontos · horizonte (linha no acento) · teto."""
    cor = cor or f.tinta
    e = _esp(f, k)
    yh = h * (0.4 if modo != "teto" else 0.6)
    vx = w * (0.68 if modo == "deslocado" else 0.5)
    foco, Hc = h * 0.9, 1.0
    zs, ult = [], None
    for i in range(60):                 # profundidades; só as que ficam a ≥ 11 px da anterior na tela
        z = 0.45 * 1.15 ** i
        yv = foco / z
        if yv < 30:
            break
        if ult is None or ult - yv >= 11:
            zs.append(z)
            ult = yv
    zfar = zs[-1]
    Xs = np.arange(-2.4, 2.41, 0.2)        # fuga: só ângulos ≥ ~22° (as rasantes viravam cunhas brancas nas laterais)
    sinal = -1 if modo == "teto" else 1

    def P(X, z):
        return vx + foco * X / z, yh + sinal * foco * Hc / z
    ls, corpo, defs = [], "", ""
    if modo == "pontos":
        grupos = {}
        for z in zs:
            for X in np.arange(-8, 8.01, 0.4):
                x, y = P(X, z)
                if -5 < x < w + 5 and 0 < y < h + 5:
                    rad = max(1.0, 9.0 / z)
                    grupos.setdefault(round(rad * 2) / 2, []).append((x, y))
        for rad, pts in grupos.items():
            corpo += f'<path d="{pontos_d(pts)}" fill="none" stroke="{cor}" stroke-width="{rad * 2:.2f}" stroke-linecap="round"/>'
    else:
        for z in zs:
            y = P(0, z)[1]
            if (sinal > 0 and y < h + 2) or (sinal < 0 and y > -2):
                xa, xb = max(0.0, P(Xs[0], z)[0]), min(float(w), P(Xs[-1], z)[0])   # o chão é o trapézio do leque
                if modo == "curvo":
                    xs = np.linspace(xa, xb, 60)
                    ls.append(np.stack([xs, y + (xs - vx) ** 2 * 0.00042 * (y - yh) / h * 3], 1))
                else:
                    ls.append([(xa, y), (xb, y)])
        for X in Xs:
            ls.append([P(X, 0.3), P(X, zfar)])
        if modo == "tunel":
            sinal2 = -1
            for z in zs:
                y = yh + sinal2 * foco * 0.8 / z
                if y > -2:
                    ls.append([(max(0.0, vx - foco * Xs[-1] / z), y), (min(float(w), vx + foco * Xs[-1] / z), y)])
            for X in Xs:
                ls.append([(vx + foco * X / 0.3, yh - foco * 0.8 / 0.3), (vx + foco * X / zfar, yh - foco * 0.8 / zfar)])
        if modo == "fade":
            defs = ('<linearGradient id="fd" x1="0" y1="0" x2="0" y2="1">'
                    f'<stop offset="{yh / h:.3f}" stop-color="#fff" stop-opacity="0"/>'
                    '<stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>'
                    f'<mask id="mk"><rect width="{w}" height="{h}" fill="url(#fd)"/></mask>')
            corpo = f'<g mask="url(#mk)">{_ln(ls, cor, e)}</g>'
        else:
            corpo = _ln(ls, cor, e)
        if modo == "horizonte":
            corpo += _ln([[(0, yh), (w, yh)]], f.acento, e * 2.2)
    if modo != "tunel" and modo != "pontos":
        cl = f'<rect y="{yh if sinal > 0 else 0:.1f}" width="{w}" height="{(h - yh) if sinal > 0 else yh:.1f}"/>'
    else:
        cl = _ret(w, h)
    nomes = {"chao": "perspectiva · chão", "fade": "perspectiva · chão que some", "tunel": "perspectiva · corredor",
             "deslocado": "perspectiva · fuga deslocada", "curvo": "perspectiva · horizonte curvo",
             "pontos": "perspectiva · pontos no chão", "horizonte": "perspectiva · horizonte no acento",
             "teto": "perspectiva · teto"}
    return _campo(w, h, corpo, nomes[modo], "palco para objeto/pessoa recortada; fio fino, sem neon (synthwave = "
                  "clichê)", defs=defs, clip=cl, fundo_claro=fundo_claro)


# ================================================================ 15. linha de ritmo (pulso)
def ritmo(f, modo="triangular", w=1080, h=240, cor=None, k=1.0, seed=0, fundo_claro=False):
    """Linha de RITMO (pulso estilizado) — compasso, batida, séries/descanso. NÃO é gráfico médico: sem PQRST, sem
    coração, sem número. modo: triangular · quadrado · batida · crescente · series · suave · empilhado · sublinhado."""
    cor = cor or f.tinta
    e = _esp(f, k)
    y0 = h / 2
    A = h * 0.36
    ls, ac = [], []

    def pulso(x, a, larg):
        return [(x, y0), (x + larg * 0.4, y0 - a), (x + larg * 0.8, y0)]
    if modo in ("triangular", "crescente"):
        pts = [(0, y0)]
        n = 7
        for i in range(n):
            x = (i + 0.5) * w / n - 18
            a = A if modo == "triangular" else A * (0.2 + 0.8 * i / (n - 1))
            pts += pulso(x, a, 36)
        ls.append(pts + [(w, y0)])
    elif modo == "quadrado":
        pts = [(0, y0)]
        per = w / 8
        for i in range(8):
            x = i * per + per * 0.3
            pts += [(x, y0), (x, y0 - A * 0.7), (x + per * 0.4, y0 - A * 0.7), (x + per * 0.4, y0)]
        ls.append(pts + [(w, y0)])
    elif modo == "batida":
        x = w * 0.58
        pk = [(x, y0), (x + 20, y0 - A * 1.15), (x + 40, y0)]
        ls.append([(0, y0)] + pk + [(w, y0)])
        ac.append(pk)
    elif modo == "series":
        pts = [(0, y0)]
        x = w * 0.06
        for s in range(3):
            for i in range(4):
                pts += pulso(x, A * 0.9, 30)
                x += 46
            x += w * 0.14
        ls.append(pts + [(w, y0)])
    elif modo == "suave":
        xs = np.linspace(0, w, 600)
        y = y0 - A * sum(np.exp(-((xs - c) / 16) ** 2) for c in np.linspace(w * 0.1, w * 0.9, 6))
        ls.append(np.stack([xs, y], 1))
    elif modo == "empilhado":
        for j in range(4):
            yy = h * (j + 0.5) / 4
            pts = [(0, yy)]
            per = w / (4 + j * 2)
            for i in range(4 + j * 2):
                x = i * per + per * 0.4
                a = h / 4 * 0.38
                pts += [(x, yy), (x + 10, yy - a), (x + 20, yy)]
            ls.append(pts + [(w, yy)])
    elif modo == "sublinhado":
        x = w * 0.78
        pk = [(x, y0), (x + 16, y0 - A * 0.9), (x + 32, y0)]
        ls.append([(0, y0)] + pk + [(w, y0)])
        ac.append(pk)
    corpo = _ln(ls, cor, e, cap="butt") + _ln(ac, f.acento, e, cap="round")
    nomes = {"triangular": "ritmo · pulso regular", "quadrado": "ritmo · pulso quadrado (sinal)",
             "batida": "ritmo · 1 batida no acento", "crescente": "ritmo · carga crescente", "series": "ritmo · séries e descanso",
             "suave": "ritmo · pulsos suaves", "empilhado": "ritmo · polirritmo", "sublinhado": "ritmo · sublinhado com pulso"}
    return _campo(w, h, corpo, nomes[modo], "RITMO estilizado, nunca traçado médico (sem PQRST/coração/números): "
                  "divisor, sublinhado, linha do tempo", caixa=caixa_de(ls + ac, e), fundo_claro=fundo_claro)


@amostra(FAM, "pautas")
def _a_pauta(f):
    return [pauta(f), pauta(f, "compassos", cor=f.apoio), pauta(f, "caderno", cor=f.apoio), pauta(f, "caligrafia"),
            pauta(f, "planilha", cor=f.apoio), pauta(f, "numerada", cor=f.apoio),
            pauta(f, "caderno", cor=f.fundo, fundo_claro=True), pauta(f, "musica", w=1080, h=420, cor=f.acento)]


@amostra(FAM, "velocidade")
def _a_vel(f):
    return [velocidade(f), velocidade(f, "angulo"), velocidade(f, "foco", w=1080, h=1080, cor=f.apoio, k=1.0),
            velocidade(f, "curvas", w=900, h=700), velocidade(f, "grupo", w=600, h=300, k=2.4),
            velocidade(f, "vertical", w=600, h=900), velocidade(f, "acento"),
            velocidade(f, cor=f.fundo, seed=4, fundo_claro=True)]


@amostra(FAM, "raios")
def _a_raios(f):
    return [raios(f, cor=f.apoio), raios(f, "linhas"), raios(f, "meio", w=1080, h=540), raios(f, "canto"),
            raios(f, "miolo", cor=f.apoio), raios(f, "irregular", w=900, h=900), raios(f, "afinando", cor=f.acento),
            raios(f, "tracejados", cor=f.apoio), raios(f, "cunhas", cor=f.fundo, n=24, fundo_claro=True)]


@amostra(FAM, "concêntricos")
def _a_conc(f):
    return [concentricos(f), concentricos(f, "geometrica"), concentricos(f, "excentricos"),
            concentricos(f, "arco", w=1080, h=540), concentricos(f, "agua"), concentricos(f, "radar", cor=f.acento),
            concentricos(f, "quadrados", cor=f.apoio), concentricos(f, "alternados"),
            concentricos(f, "iguais", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "perspectiva")
def _a_persp(f):
    return [perspectiva(f), perspectiva(f, "fade"), perspectiva(f, "tunel", cor=f.apoio), perspectiva(f, "deslocado"),
            perspectiva(f, "curvo"), perspectiva(f, "pontos"), perspectiva(f, "horizonte", cor=f.apoio),
            perspectiva(f, "teto"), perspectiva(f, "chao", cor=f.fundo, fundo_claro=True)]


@amostra(FAM, "ritmo (pulso)")
def _a_ritmo(f):
    return [ritmo(f), ritmo(f, "quadrado"), ritmo(f, "batida"), ritmo(f, "crescente"), ritmo(f, "series"),
            ritmo(f, "suave", cor=f.acento), ritmo(f, "empilhado", h=480, cor=f.apoio), ritmo(f, "sublinhado", w=640, h=120)]      # "1 batida" no papel removida: o acento claro sobre papel quase some a 25% (D11); a do escuro basta
