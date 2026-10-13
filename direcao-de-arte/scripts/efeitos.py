"""EFEITOS DE INTEGRAÇÃO — o que um compositor sênior faz no Photoshop para a pessoa recortada "morar" na peça,
como camadas paramétricas do palco (HTML/CSS/SVG) ou pré-cálculo em numpy quando precisa do fundo.

  grao_url(W, H, forca)              grão ÚNICO da peça (cinza médio + ruído gaussiano), para uma camada em overlay
                                     POR CIMA de fundo + foto (mesma textura nos dois = mesma "película")
  mapa_gradiente(id, paradas)        <filter> SVG: mapa de gradiente (Photoshop "Gradient Map") — P&B → cores do tema
  light_wrap(pessoa, fundo, x, y)    a luz do fundo "abraça" a borda da pessoa (Nuke/AE LightWrap)
  luz_de_borda(pessoa, angulo, …)    rim light do lado da luz, pela distância à borda do alfa
  sombra_css(dx, dy, desfoque, …)    sombra projetada pela silhueta (CSS drop-shadow usa o alfa)

Todas as receitas, com parâmetros e armadilhas: references/camadas.md.
"""
import base64
import io

import numpy as np


def _png(im):
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def grao_url(W, H, forca=0.06, seed=11, tamanho=1.0):
    """Grão monocromático: cinza 50% + ruído gaussiano (desvio = forca × 255). Usar com mix-blend-mode: overlay
    (ou soft-light, mais suave) numa camada acima do fundo e da foto e ABAIXO do texto. `tamanho` > 1 = grão maior."""
    from PIL import Image
    rng = np.random.default_rng(seed)
    w, h = max(8, round(W / tamanho)), max(8, round(H / tamanho))
    n = np.clip(128 + rng.normal(0, forca * 255, (h, w)), 0, 255).astype(np.uint8)
    im = Image.fromarray(n, "L")
    if tamanho != 1.0:
        im = im.resize((W, H), Image.BICUBIC)
    return _png(im)


def mapa_gradiente(fid, paradas):
    """Filtro SVG 'mapa de gradiente': luminância (Rec. 709) → tabela por canal. `paradas` = lista de cores hex do
    escuro ao claro (2 = duotone, 3 = tritone…). Uso: <svg width=0 height=0>{filtro}</svg> e style="filter:url(#id)".
    color-interpolation-filters=sRGB para a tabela casar com os hex."""
    rgb = [tuple(int(c.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)) for c in paradas]
    tab = [" ".join(f"{c[k]:.4f}" for c in rgb) for k in range(3)]
    return (f'<filter id="{fid}" color-interpolation-filters="sRGB">'
            f'<feColorMatrix type="matrix" values="0.2126 0.7152 0.0722 0 0 0.2126 0.7152 0.0722 0 0 '
            f'0.2126 0.7152 0.0722 0 0 0 0 0 1 0"/>'
            f'<feComponentTransfer><feFuncR type="table" tableValues="{tab[0]}"/>'
            f'<feFuncG type="table" tableValues="{tab[1]}"/><feFuncB type="table" tableValues="{tab[2]}"/>'
            f'</feComponentTransfer></filter>')


def _alfa(rgba):
    return rgba[..., 3].astype(np.float32) / 255.0


def light_wrap(pessoa, fundo, x, y, raio=None, forca=0.55):
    """`pessoa` RGBA (PIL) já no tamanho final; `fundo` RGB (PIL) da peça inteira; (x, y) = canto da pessoa na peça.
    Faixa INTERNA da borda recebe o fundo desfocado em 'tela' (screen) — a luz de trás contorna a silhueta, como na
    câmera de verdade. raio padrão = 1,2% da altura da pessoa. Devolve RGBA (PIL)."""
    import cv2
    from PIL import Image
    p = np.asarray(pessoa.convert("RGBA")).astype(np.float32)
    h, w = p.shape[:2]
    raio = raio or max(2.0, 0.012 * h)
    F = np.asarray(fundo.convert("RGB")).astype(np.float32)
    H, W = F.shape[:2]
    # pedaço do fundo atrás da pessoa (com borda preenchida se a pessoa sangra)
    pad = int(3 * raio) + 2
    Fp = cv2.copyMakeBorder(F, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
    x0, y0 = int(round(x)) + pad, int(round(y)) + pad
    sub = np.zeros((h, w, 3), np.float32)
    ys, xs = slice(max(0, y0), min(Fp.shape[0], y0 + h)), slice(max(0, x0), min(Fp.shape[1], x0 + w))
    sub[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0] = Fp[ys, xs]
    a = _alfa(p)
    # fundo desfocado só onde NÃO há pessoa (a luz vem de fora) → espalha para dentro
    fora = sub * (1 - a)[..., None]
    k = cv2.GaussianBlur(fora, (0, 0), raio)
    n = cv2.GaussianBlur(1 - a, (0, 0), raio)[..., None] + 1e-4
    luz = k / n
    borda = np.clip(cv2.GaussianBlur(1 - a, (0, 0), raio), 0, 1) * a          # faixa interna da borda
    m = (forca * borda)[..., None]
    rgb = p[..., :3] / 255.0
    rgb = 1 - (1 - rgb) * (1 - m * luz / 255.0)                                 # tela
    out = np.dstack([np.clip(rgb * 255, 0, 255), p[..., 3]]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def luz_de_borda(pessoa, angulo=135, largura=None, cor="#FFFFFF", forca=0.6):
    """Rim light: faixa de luz na borda do lado de onde vem a luz (`angulo` em graus, 0 = luz da direita, 90 = de
    cima, 180 = da esquerda). Largura padrão = 0,6% da altura. Soma em 'tela'. Devolve RGBA (PIL)."""
    import cv2
    from PIL import Image
    p = np.asarray(pessoa.convert("RGBA")).astype(np.float32)
    h = p.shape[0]
    largura = largura or max(1.5, 0.006 * h)
    a = (p[..., 3] > 127).astype(np.uint8)
    d = cv2.distanceTransform(a, cv2.DIST_L2, 5)
    faixa = np.clip(1 - d / largura, 0, 1) * _alfa(p)
    # direção da borda: gradiente do alfa desfocado aponta para FORA da pessoa
    ab = cv2.GaussianBlur(_alfa(p), (0, 0), largura * 2)
    gx, gy = cv2.Sobel(ab, cv2.CV_32F, 1, 0), cv2.Sobel(ab, cv2.CV_32F, 0, 1)
    nx, ny = -gx, -gy
    nn = np.sqrt(nx * nx + ny * ny) + 1e-6
    lx, ly = np.cos(np.radians(angulo)), -np.sin(np.radians(angulo))
    lado = np.clip((nx * lx + ny * ly) / nn, 0, 1) ** 1.5
    m = (forca * faixa * lado)[..., None]
    c = np.array([int(cor.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0
    rgb = p[..., :3] / 255.0
    rgb = 1 - (1 - rgb) * (1 - m * c)
    return Image.fromarray(np.dstack([np.clip(rgb * 255, 0, 255), p[..., 3]]).astype(np.uint8), "RGBA")


def sombra_css(dx, dy, desfoque, cor="#000000", opac=0.45):
    """Sombra pela SILHUETA (o drop-shadow do CSS usa o alfa da imagem). Regra: a sombra cai do lado oposto à luz
    da foto; desfoque ≥ 3× o deslocamento para parecer luz de estúdio difusa, nunca carimbo duro."""
    r, g, b = (int(cor.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return f"drop-shadow({dx:.1f}px {dy:.1f}px {desfoque:.1f}px rgba({r},{g},{b},{opac}))"


# ====================================================================== medidas de compositing (pesquisa 8 §5.2)
# Testadas pela pesquisa com dados sintéticos (luz 90°/0°/180°; ruído σ=5 → 5,08; anel claro detectado; banding
# ≈ 30× sem dither). Limites [proposta] calibrados em folha de contato antes de virar portão.

def sigma_ruido(cinza255, lisas=None):
    """Desvio do ruído/grão (Immerkær 1996), só nas áreas lisas (30% menores gradientes, se não vier máscara)."""
    import cv2
    M = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], np.float32)
    g = cinza255.astype(np.float32)
    r = np.abs(cv2.filter2D(g, -1, M))
    if lisas is None:
        gm = cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))
        lisas = gm < np.percentile(gm, 30)
    if lisas.sum() < 100:
        return None
    return float(np.sqrt(np.pi / 2) * r[lisas].mean() / 6)


def halo(L, alfa, r=4, lim=4.0):
    """L (0–100) da peça pronta + alfa da pessoa → (fração da borda com halo CLARO, com franja ESCURA)."""
    import cv2
    a = (alfa > 0.5).astype(np.uint8)
    di, do = cv2.distanceTransform(a, cv2.DIST_L2, 3), cv2.distanceTransform(1 - a, cv2.DIST_L2, 3)
    borda = ((di > 0) & (di <= 1.5)) | ((do > 0) & (do <= 1.5))

    def media(mk):
        mk = mk.astype(np.float32)
        return cv2.GaussianBlur(L * mk, (0, 0), 2 * r) / (cv2.GaussianBlur(mk, (0, 0), 2 * r) + 1e-6)
    Li, Lo = media((di > r) & (di <= 2 * r)), media((do > r) & (do <= 2 * r))
    if not borda.any():
        return 0.0, 0.0
    return (float(((L - np.maximum(Li, Lo))[borda] > lim).mean()),
            float(((np.minimum(Li, Lo) - L)[borda] > lim).mean()))


def banding(rgb8, corrida=16):
    """Degraus por mil px em degradês lentos (platôs longos + saltos de 1–2 níveis). Rodar na imagem e na transposta."""
    import cv2

    def um(img):
        Y = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.int16)
        dx = np.diff(Y, axis=1)
        suave = cv2.blur(np.abs(dx).astype(np.float32), (31, 31)) < 1.5
        plato = cv2.filter2D((dx == 0).astype(np.float32), -1, np.ones((1, corrida), np.float32) / corrida) > .999
        perto = cv2.dilate(plato.astype(np.uint8), np.ones((1, corrida + 3), np.uint8)) > 0
        degrau = (np.abs(dx) >= 1) & (np.abs(dx) <= 2)
        return 1000 * float((degrau & perto & suave).sum()) / max(int(suave.sum()), 1)
    rgb8 = np.ascontiguousarray(rgb8.astype(np.uint8))
    return max(um(rgb8), um(np.ascontiguousarray(rgb8.transpose(1, 0, 2))))


def casa_cor(suj, alfa, placa, viz, kL=0.7, kab=0.6):
    """Casa o sujeito com a cena (ordem do compositor): L por pontos preto/branco (percentis 1/99) e a/b por Reinhard
    PARCIAL, com a estatística só na VIZINHANÇA (`viz`, bool) da placa. RGB float32 0–1."""
    import cv2
    S = cv2.cvtColor(suj.astype(np.float32), cv2.COLOR_RGB2Lab)
    P = cv2.cvtColor(placa.astype(np.float32), cv2.COLOR_RGB2Lab)
    m = alfa > 0.5
    s0, s1 = np.percentile(S[..., 0][m], [1, 99])
    p0, p1 = np.percentile(P[..., 0][viz], [1, 99])
    S[..., 0] += kL * ((S[..., 0] - s0) / max(s1 - s0, 1e-3) * (p1 - p0) + p0 - S[..., 0])
    for c in (1, 2):
        ms, ss = S[..., c][m].mean(), S[..., c][m].std() + 1e-6
        S[..., c] += kab * ((S[..., c] - ms) * P[..., c][viz].std() / ss + P[..., c][viz].mean() - S[..., c])
    return np.clip(cv2.cvtColor(S, cv2.COLOR_Lab2RGB), 0, 1)


def direcao_luz(L, alfa, faixa=3):
    """Ângulo da luz (graus; 0 = da direita, 90 = de cima) estimado no contorno (Johnson & Farid 2005). Indício."""
    import cv2
    d = cv2.distanceTransform((alfa > .5).astype(np.uint8), cv2.DIST_L2, 5)
    gy, gx = np.gradient(cv2.GaussianBlur(d, (0, 0), 1.5))
    n = -np.dstack([gx, gy])
    n = n / (np.linalg.norm(n, axis=2, keepdims=True) + 1e-6)
    m = (d > 1) & (d <= faixa)
    if m.sum() < 50:
        return None
    (lx, ly, _), *_ = np.linalg.lstsq(np.c_[n[m], np.ones(m.sum())], L[m], rcond=None)
    return float(np.degrees(np.arctan2(-ly, lx)))


def dither_tpdf(rgb_float01, seed=3):
    """Dither TPDF ±1 LSB antes de quantizar em 8 bits (mata o banding de degradê lento)."""
    rng = np.random.default_rng(seed)
    x = rgb_float01 * 255.0 + rng.random(rgb_float01.shape) - rng.random(rgb_float01.shape)
    return np.clip(np.round(x), 0, 255).astype(np.uint8)


def grao_np(rgb, sigma=0.018, seed=7, tamanho=1.0):
    """Grão ÚNICO da peça (passada de imagem do palco): ruído gaussiano MONO de média zero, σ constante (0–1),
    o mesmo em fundo, foto e elementos — a 'película' que une as camadas (pesquisa 7 L6, pesquisa 8 §1.5).
    `tamanho` > 1 = grão maior (borra o ruído e renormaliza o σ). Use o MESMO σ e semente em toda a série."""
    import cv2
    h, w = rgb.shape[:2]
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (h, w)).astype(np.float32)
    if tamanho > 1.0:
        n = cv2.GaussianBlur(n, (0, 0), 0.5 * (tamanho - 1) + 0.35)
        n /= n.std() + 1e-6
    return rgb + sigma * n[..., None]


def pos_campanha(sigma=0.018, seed=7, tamanho=1.0):
    """Função de pós da passada de IMAGEM (palco.render(pos=...)): só o grão único da campanha por enquanto."""
    return lambda rgb: grao_np(rgb, sigma, seed, tamanho)
