"""tipos.py — fontes com prova: ficha de leitura, checagem de PAR, histórico por cliente (rotação para inovar).

Por que: "fontes diferentes, mas que dê para ler claramente qualquer coisa" e "sempre inovar". Escolher no olho
deixa passar zero igual a O num preço, acento faltando, número que treme no contador e o mesmo par em toda campanha.

  python tipos.py ficha "Mona Sans:900:wdth=75"            # leitura de 1 fonte (texto + JSON com --json)
  python tipos.py par "Mona Sans:800:wdth=75" "Figtree:400" [--numeros "Mona Sans:700"] [--cliente X --projeto y]
  python tipos.py usar --cliente X --projeto campanha-y --titulo "Schibsted Grotesk:800" --texto "Schibsted Grotesk:400"
                      [--numeros "Martian Mono:700"] [--status teste|aprovado] [--nota "…"]
  python tipos.py historico --cliente X                    # registro + tipografia das fichas da biblioteca (só leitura)
  python tipos.py folha pares.json -o pares.png            # folha visual: cada par com tiras de confusão e veredito
  python tipos.py sugerir --voz "esportivo,evento" --cliente X [--campanha "Black Friday ao vivo"] [--n 6] [--folha sug.png]
      PROPÕE pares: lê assets/fontes/receitas.json (60 receitas da 16a + sistemas do cliente da 16d), testa cada um
      com `par`, dá nota (16a §7.4: contraste em ≥ 2 eixos, estrutura parecida, conflito, voz repetida, confusões) e
      devolve os melhores de GRUPOS diferentes (uma família · serifa × sem serifa · mono herói · largura × normal…)
  python tipos.py rotacao --cliente X [--fixar T7] [--video]   # 5 combinações da matriz de 10 eixos para a próxima
      campanha (muda 3–5 eixos, T sempre, descanso, distância ≥ 3 das últimas 3) · --matriz lista os eixos
      Registrar a escolhida: tipos.py usar … --eixos "T2,A1,E3,V2,I2,S0,X2,D2,C3" --tecnicas "1,8,18"
      pares.json = {"titulo", "cliente"?, "projeto"?, "pares": [{"nome", "titulo", "texto", "numeros"?, "frase"?, "nota"?}]}

Especificação de fonte: "Família[:peso][:eixo=valor,...]" (Google Fonts, baixa sozinho via fonts.py) ou caminho .ttf.
  Ex.: "Mona Sans:900:wdth=75" · "Big Shoulders Display:800" · "C:/fontes/x.ttf:700".

O que a FICHA mede (no desenho da fonte, na instância pedida):
  - licença (OFL/Apache/outra) · eixos variáveis · "padrão de IA" (proibida como voz, aviso como texto)
  - português: falta de glifo em ÁÀÂÃÉÊÍÓÔÕÚÜÇ áàâãéêíóôõúüç ºª R$ – — “ ” … ·
  - altura-x ÷ maiúscula (texto corrido pede ≥ 0,66) · largura média (condensada × larga) · peso (haste ÷ maiúscula)
  - números: alinhados ou de texto (oldstyle) por padrão; tem `tnum` (contador e preço não tremem); tem `zero`
  - CONFUSÃO no tamanho de celular: Il · l1 · I1 · O0 · rn×m · cl×d · 5S · 8B · 6b · 1 7 · 3 8 — cada par desenhado
    com a maiúscula a 11 px (texto pequeno no celular), borrado 0,6 px, e comparado pixel a pixel (1,00 = idênticos)
O PAR soma: parecidas demais sem ser a mesma família (conflito), contraste de largura/peso, altura-x na mesma linha,
fonte de números, licença, PT-BR e novidade contra o histórico do cliente.
Regras de combinação e receitas: references/tipografia.md · pesquisas 16a–16d.
"""
import argparse, datetime, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FONT_DIR = os.path.join(os.path.expanduser("~"), ".cache", "brand-studio", "fonts")
STUDIO = os.path.dirname(os.path.dirname(os.path.realpath(HERE)))   # pasta com as skills irmãs


def _pasta_trabalho():
    """Pasta de trabalho do usuário: ESTUDIO_DIR > pasta acima das skills (se tiver biblioteca/ ou .env) > atual."""
    if os.environ.get("ESTUDIO_DIR"):
        return os.path.abspath(os.environ["ESTUDIO_DIR"])
    up = os.path.dirname(STUDIO)
    if any(os.path.exists(os.path.join(up, n)) for n in ("biblioteca", ".env")):
        return up
    return os.getcwd()


BIBLIOTECA = os.environ.get("BRAND_LIBRARY") or os.path.join(_pasta_trabalho(), "biblioteca")
REGISTRO = os.path.join(BIBLIOTECA, "_registro-fontes.json")   # histórico de fontes por cliente (dado do usuário)

PADRAO_IA = {"inter", "roboto", "arial", "helvetica", "space grotesk", "open sans", "poppins", "montserrat", "lato",
             "dm sans", "plus jakarta sans", "manrope"}                 # mesma lista do brand-system/typesys.py
PT_BR = "ÁÀÂÃÉÊÍÓÔÕÚÜÇáàâãéêíóôõúüçºª"
SINAIS = "R$%–—“”‘’…·•@&()+−×"
CONFUSOES = [("I", "l"), ("l", "1"), ("I", "1"), ("O", "0"), ("rn", "m"), ("cl", "d"), ("5", "S"), ("8", "B"),
             ("6", "b"), ("1", "7"), ("3", "8")]
CRITICOS = {("O", "0"), ("l", "1"), ("I", "1"), ("rn", "m")}            # preço, telefone, cupom, e-mail
CRITICOS_NUM = {("O", "0"), ("l", "1"), ("I", "1")}                      # fonte de NÚMEROS: só o que muda dígito
# Limite POR PAR (calibrar(), 10/10/2026, 10 fontes): a semelhança "normal" muda de par para par (3 e 8 sempre se
# parecem mais que 1 e 7). Acima do limite = se confundem no celular. Casos de referência: Hubot Sans O/0 0,92,
# l/1 0,87, rn/m 0,85 (confusas no olho) · Big Shoulders O/0 0,90 · Mona/Big Shoulders I/l 1,00 (desenho idêntico).
LIMITE = {"I/l": 0.97, "l/1": 0.80, "I/1": 0.75, "O/0": 0.85, "rn/m": 0.80, "cl/d": 0.70, "5/S": 0.82,
          "8/B": 0.88, "6/b": 0.80, "1/7": 0.65, "3/8": 0.86}
FOLGA = 0.06           # até FOLGA abaixo do limite, em par crítico = "olhar no tamanho real"
CAP_PX = 11            # maiúscula de 11 px ≈ texto de 15–16 px no celular


# ---------------------------------------------------------------- abrir fonte na instância pedida
def resolver(spec):
    """'Família:peso:eixo=v,...' ou 'arquivo.ttf[:peso]' → (arquivo, {eixo: valor}, rótulo)."""
    m = re.match(r"^(.*?\.(?:ttf|otf))(?::(.*))?$", spec, re.I)
    if m:
        arq, resto = m.group(1), (m.group(2) or "")
        partes = [""] + resto.split(":") if resto else [""]
    else:
        partes = spec.split(":")
        arq = None
    fam = partes[0]
    eixos = {}
    if len(partes) > 1 and partes[1]:
        eixos["wght"] = float(partes[1].rstrip("i"))
    if len(partes) > 2 and partes[2]:
        for kv in partes[2].split(","):
            k, _, v = kv.partition("=")
            eixos[k.strip()] = float(v)
    if arq is None:
        from palco import fonte_variavel
        arq = fonte_variavel(fam)
        if not arq:                                                    # família só estática
            import compor as K
            arq = K.font(f"{fam}:{int(eixos.get('wght', 400))}").file
    return arq, eixos, spec


def _abrir(arq):
    from fontTools.ttLib import TTFont
    return TTFont(arq)


def _nome(f, i):
    r = f["name"].getDebugName(i)
    return r or ""


def _local(f, eixos):
    if "fvar" not in f:
        return {}
    loc = {}
    for a in f["fvar"].axes:
        v = eixos.get(a.axisTag, a.defaultValue)
        loc[a.axisTag] = max(a.minValue, min(a.maxValue, v))
    return loc


def _bbox(gs, cmap, ch):
    from fontTools.pens.boundsPen import BoundsPen
    g = cmap.get(ord(ch))
    if not g:
        return None
    p = BoundsPen(gs)
    gs[g].draw(p)
    return p.bounds


def _digitos_iguais(gs, cmap):
    """Algarismos já têm a mesma largura no desenho (mono ou tabular por padrão) → contador não treme sem `tnum`."""
    w = {gs[cmap[ord(d)]].width for d in "0123456789" if ord(d) in cmap}
    return len(w) == 1


def _features(f):
    tags = set()
    for t in ("GSUB", "GPOS"):
        if t in f and f[t].table.FeatureList:
            tags |= {r.FeatureTag for r in f[t].table.FeatureList.FeatureRecord}
    return tags


# ---------------------------------------------------------------- render para a confusão
def _pil(arq, loc, px):
    from PIL import ImageFont
    fo = ImageFont.truetype(arq, px)
    if loc:
        try:
            ax = fo.get_variation_axes()
            fo.set_variation_by_axes([loc.get(_tag(a), a.get("default", 0)) for a in ax])
        except Exception:
            pass
    return fo


def _tag(a):
    n = a.get("name", b"")
    n = n.decode() if isinstance(n, bytes) else str(n)
    return {"Weight": "wght", "Width": "wdth", "Optical size": "opsz", "Optical Size": "opsz", "Slant": "slnt",
            "Italic": "ital"}.get(n, n[:4])


def _mascara(fo, txt, esc):
    """Texto renderizado em esc× e reduzido → máscara float na escala final (antialias real).
    Linha de base FIXA por fonte (altura medida em glifos altos/baixos, não só no hhea): fontes como a Coiny desenham
    fora do ascendente declarado e saíam cortadas."""
    import numpy as np
    from PIL import Image, ImageDraw
    asc, desc = fo.getmetrics()
    l, t, r, b = fo.getbbox("ÍÁÇjgl|1Ã", anchor="ls")
    cima, baixo = max(asc, -t) + 2 * esc, max(desc, b) + 2 * esc
    l2, _, r2, _ = fo.getbbox(txt, anchor="ls")
    w = int(max(fo.getlength(txt), r2) - min(0, l2)) + 8 * esc
    im = Image.new("L", (w, cima + baixo), 0)
    ImageDraw.Draw(im).text((4 * esc - min(0, l2), cima), txt, font=fo, fill=255, anchor="ls")
    im = im.resize((max(1, im.width // esc), max(1, im.height // esc)), Image.BOX)
    return np.asarray(im, dtype=np.float32) / 255


def _semelhanca(a, b, sigma=0.6):
    """1 = idênticos. Alinha pela tinta (esquerda) e linha de base comum; melhor de ±1 px; Jaccard ponderado."""
    import numpy as np
    from scipy.ndimage import gaussian_filter
    def corte(m):
        cols = np.where(m.max(0) > 0.08)[0]
        return m[:, cols[0]:cols[-1] + 1] if len(cols) else m
    a, b = corte(a), corte(b)
    h = max(a.shape[0], b.shape[0]); w = max(a.shape[1], b.shape[1]) + 4
    A = np.zeros((h, w), np.float32); B = np.zeros((h, w), np.float32)
    A[:a.shape[0], 2:2 + a.shape[1]] = a
    best = 0.0
    for dx in (-1, 0, 1):
        B[:] = 0
        B[:b.shape[0], 2 + dx:2 + dx + b.shape[1]] = b
        x, y = gaussian_filter(A, sigma), gaussian_filter(B, sigma)
        s = 1 - np.abs(x - y).sum() / max(np.maximum(x, y).sum(), 1e-6)
        best = max(best, float(s))
    return best


# ---------------------------------------------------------------- FICHA
def _runs(v, lim=0.5):
    """Corridas de tinta (início, comprimento) num vetor 1-D."""
    import numpy as np
    b = np.concatenate([[0], (v > lim).astype(int), [0]])
    d = np.diff(b)
    ini, fim = np.where(d == 1)[0], np.where(d == -1)[0]
    return list(zip(ini, fim - ini))


def _estrutura(arq, loc, upm, cap):
    """Esqueleto e 'carne' medidos no desenho grande (maiúscula = 200 px) — 16a §1.3 e §6 (regras 3, 5, 10):
    serifa (pé do I mais largo que a haste), contraste de traço (fino ÷ grosso no 'o'), abertura do 'c'."""
    import numpy as np
    fo = _pil(arq, loc, int(200 * upm / cap))
    out = {"serifa": None, "contraste_traco": None, "abertura_c": None, "densidade": None}
    # "cor" do texto (o peso que o olho vê): tinta ÷ área na faixa da altura-x, em "nonon" (condensada pesada = escura)
    nn = _mascara(fo, "nonon", 1)
    r_n, c_n = np.where(nn.max(1) > 0.5)[0], np.where(nn.max(0) > 0.5)[0]
    if len(r_n) > 5 and len(c_n) > 5:
        out["densidade"] = round(float(nn[r_n[0]:r_n[-1] + 1, c_n[0]:c_n[-1] + 1].mean()), 3)
    # serifa medida no pé da haste esquerda do H (no I muitas sem serifa têm barras: Tourney, Dela Gothic)
    H = _mascara(fo, "H", 1)
    rows = np.where(H.max(1) > 0.5)[0]
    if len(rows) > 10:
        alto = len(rows)
        haste = _runs(H[rows[0] + int(0.72 * alto)])                   # abaixo da barra do H
        pe = _runs(H[rows[-1] - max(1, alto // 40)])
        if haste and pe:
            out["serifa"] = bool(pe[0][1] > 1.6 * haste[0][1])
    o = _mascara(fo, "o", 1)
    r_o, c_o = np.where(o.max(1) > 0.5)[0], np.where(o.max(0) > 0.5)[0]
    if len(r_o) > 10 and len(c_o) > 10:
        lado = _runs(o[(r_o[0] + r_o[-1]) // 2])
        topo = _runs(o[:, (c_o[0] + c_o[-1]) // 2])
        if lado and topo:
            h, v = lado[0][1], topo[0][1]
            out["contraste_traco"] = round(min(h, v) / max(h, v), 2)
    c = _mascara(fo, "c", 1)
    r_c, c_c = np.where(c.max(1) > 0.5)[0], np.where(c.max(0) > 0.5)[0]
    if len(r_c) > 10 and len(c_c) > 10:
        col = c[r_c[0]:r_c[-1] + 1, c_c[0] + int(0.92 * (c_c[-1] - c_c[0]))]
        tinta = np.where(col > 0.5)[0]
        if len(tinta) >= 2:
            buracos = [b for b in np.diff(tinta) if b > 1]
            out["abertura_c"] = round(max(buracos, default=0) / (r_c[-1] - r_c[0] + 1), 2)
    return out


_CACHE = {}


def ficha(spec):
    if spec in _CACHE:
        return _CACHE[spec]
    _CACHE[spec] = r = _ficha(spec)
    return r


def _ficha(spec):
    arq, eixos, rot = resolver(spec)
    f = _abrir(arq)
    upm = f["head"].unitsPerEm
    loc = _local(f, eixos)
    gs = f.getGlyphSet(location=loc) if loc else f.getGlyphSet()
    cmap = f.getBestCmap()
    familia = _nome(f, 16) or _nome(f, 1)
    lic_txt = (_nome(f, 13) + " " + _nome(f, 14)).lower()
    pasta = os.path.dirname(arq)
    if "open font license" in lic_txt or "ofl" in lic_txt or os.path.exists(os.path.join(pasta, "OFL.txt")):
        lic = "OFL"
    elif "apache" in lic_txt or os.path.exists(os.path.join(pasta, "LICENSE.txt")):
        lic = "Apache"
    else:
        lic = "VERIFICAR"
    falta = [c for c in PT_BR + SINAIS if ord(c) not in cmap and c not in "−×"]
    bH, bx = _bbox(gs, cmap, "H"), _bbox(gs, cmap, "x")
    cap = (bH[3] if bH else getattr(f["OS/2"], "sCapHeight", 0.7 * upm))
    xh = (bx[3] if bx else getattr(f["OS/2"], "sxHeight", 0.5 * upm))
    adv = [gs[cmap[ord(c)]].width for c in "abcdefghijklmnopqrstuvwxyz" if ord(c) in cmap]
    larg = sum(adv) / len(adv) / upm if adv else 0
    advC = [gs[cmap[ord(c)]].width for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if ord(c) in cmap]
    largC = sum(advC) / len(advC) / upm if advC else 0
    # números: altura média dos dígitos ÷ maiúscula (< 0,9 = números de texto por padrão)
    alts = [(_bbox(gs, cmap, d) or (0, 0, 0, 0))[3] for d in "0123456789"]
    num_alinhados = min(alts) / cap > 0.9 if cap else True
    feats = _features(f)
    # peso: haste do I renderizada grande ÷ maiúscula
    import numpy as np
    big = _mascara(_pil(arq, loc, int(200 * upm / cap)), "I", 1) if cap else None
    haste = 0.0
    if big is not None:
        linha = big[big.shape[0] // 2] if big.max() else big[0]
        rows = big[np.where(big.max(1) > 0.5)[0]]
        if len(rows):
            linha = rows[len(rows) // 2]
            haste = float((linha > 0.5).sum()) / 200
    # confusões no tamanho de celular
    esc = 4
    fo = _pil(arq, loc, max(4, round(CAP_PX * esc * upm / cap)))
    conf = {}
    for p, q in CONFUSOES:
        if all(ord(c) in cmap for c in p + q):
            conf[f"{p}/{q}"] = round(_semelhanca(_mascara(fo, p, esc), _mascara(fo, q, esc)), 3)
    est = _estrutura(arq, loc, upm, cap)
    larg_i_m = {gs[cmap[ord(ch)]].width for ch in "imW" if ord(ch) in cmap}
    bA = _bbox(gs, cmap, "Á")
    asc_lim = max(f["hhea"].ascent, getattr(f["OS/2"], "usWinAscent", 0))
    pasta_it = any("Italic" in n for n in os.listdir(pasta))
    return {"spec": rot, "arquivo": arq, "familia": familia, "licenca": lic, "local": loc,
            "mono": len(larg_i_m) == 1, **est,
            "case": "case" in feats, "acento_cortado": bool(bA and bA[3] > asc_lim),
            "italico": ("fvar" in f and any(a.axisTag in ("ital", "slnt") for a in f["fvar"].axes)) or pasta_it,
            "eixos": {a.axisTag: [a.minValue, a.defaultValue, a.maxValue] for a in f["fvar"].axes} if "fvar" in f else {},
            "padrao_ia": familia.lower() in PADRAO_IA, "falta": falta,
            "x_sobre_cap": round(xh / cap, 3) if cap else None, "cap_upm": round(cap / upm, 3),
            "largura_min": round(larg, 3), "largura_mai": round(largC, 3), "haste_cap": round(haste, 3),
            "numeros_alinhados": num_alinhados, "tnum": "tnum" in feats or _digitos_iguais(gs, cmap),
            "tnum_desenho": _digitos_iguais(gs, cmap), "zero": "zero" in feats,
            "ss": sorted(t for t in feats if t.startswith("ss") or t.startswith("cv")),
            "confusoes": conf}


def avisos_ficha(fi, papel="texto"):
    """Lista (nível, mensagem). nível: VETO | ALERTA | ok."""
    out = []
    if fi["licenca"] == "VERIFICAR":
        out.append(("VETO", "licença não identificada no arquivo: confirmar antes de usar"))
    if fi["padrao_ia"]:
        out.append(("VETO" if papel == "titulo" else "ALERTA",
                    f"{fi['familia']} é 'padrão de IA': {'proibida como voz' if papel == 'titulo' else 'só com motivo escrito'}"))
    pt = [c for c in fi["falta"] if c in PT_BR]
    if pt:
        out.append(("VETO", "falta acento do português: " + "".join(pt)))
    si = [c for c in fi["falta"] if c not in PT_BR]
    if si:
        out.append(("ALERTA", "faltam sinais: " + " ".join(si)))
    if fi.get("acento_cortado"):
        out.append(("ALERTA", "acento de maiúscula passa do ascendente declarado: risco de corte no navegador (Á, Ê)"))
    if papel == "texto":
        if fi["largura_min"] and fi["largura_min"] < 0.42:
            out.append(("ALERTA", f"condensada ({fi['largura_min']:.2f}) em texto corrido: só para título (16a §6 r8)"))
        if fi["haste_cap"] and not (0.10 <= fi["haste_cap"] <= 0.19):
            out.append(("ALERTA", f"peso {'fino' if fi['haste_cap'] < 0.10 else 'preto'} demais para texto "
                                  f"(haste {fi['haste_cap']:.2f} da maiúscula; pede 0,10–0,19)"))
        if fi.get("abertura_c") is not None and fi["abertura_c"] < 0.12:
            out.append(("ALERTA", f"formas fechadas (abertura do c {fi['abertura_c']:.2f}): pior no relance e no pequeno"))
    if papel == "texto" and fi["x_sobre_cap"] and fi["x_sobre_cap"] < 0.66:
        out.append(("ALERTA", f"altura-x baixa para texto corrido ({fi['x_sobre_cap']:.2f} da maiúscula; pede ≥ 0,66)"))
    for k, v in fi["confusoes"].items():
        p, q = k.split("/")
        crit = (p, q) in (CRITICOS_NUM if papel == "numeros" else CRITICOS)
        lim = LIMITE.get(k, 0.85)
        if k == "I/l" and v >= lim:
            out.append(("ALERTA" if papel != "titulo" else "ok",
                        f"I e l idênticos ({v:.2f}): evitar em siglas, cupons e e-mail"))
            continue
        if papel == "titulo" and not crit:
            continue                       # título é grande: só pesa a confusão que muda número/código
        if papel == "titulo" and v >= lim:
            out.append(("ALERTA", f"{p} × {q} iguais no desenho ({v:.2f}): título com número/código (ex.: "
                                  "\"BLACK10OFF\") fica ambíguo; preço e cupom em outra fonte ou largura normal"))
            continue
        if v >= lim:
            out.append(("VETO" if crit and papel == "numeros" else "ALERTA",
                        f"{p} × {q} se confundem no celular ({v:.2f})" + (" — crítico em preço/telefone/cupom" if crit else "")))
        elif v >= lim - FOLGA and crit:
            out.append(("ALERTA", f"{p} × {q} parecidos ({v:.2f}): olhar no tamanho real"))
    if papel == "numeros":
        if fi["confusoes"].get("O/0", 0) >= LIMITE["O/0"] - FOLGA and fi["zero"]:
            out.append(("ok", "tem `zero` (zero cortado/pontuado): ligar em cupom/código"))
        if not fi["numeros_alinhados"]:
            out.append(("ALERTA", "números de texto (oldstyle) por padrão: ligar `lnum` em preço"))
        if not fi["tnum"]:
            out.append(("ALERTA", "sem `tnum`: contador e preço que mudam vão tremer"))
    return out


def _txt_ficha(fi, papel):
    linhas = [f"{fi['spec']}  →  {fi['familia']} · {fi['licenca']} · eixos {fi['eixos'] or 'estática'}",
              f"  altura-x/maiúscula {fi['x_sobre_cap']} · largura (minúsc.) {fi['largura_min']} · (maiúsc.) "
              f"{fi['largura_mai']} · haste/maiúscula {fi['haste_cap']}",
              f"  números {'alinhados' if fi['numeros_alinhados'] else 'de texto'} · tnum {'sim' if fi['tnum'] else 'NÃO'}"
              f" · zero {'sim' if fi['zero'] else 'não'} · alternativos {' '.join(fi['ss']) or '—'}",
              "  confusão (1 = iguais): " + "  ".join(f"{k} {v:.2f}" for k, v in fi["confusoes"].items())]
    for n, m in avisos_ficha(fi, papel):
        linhas.append(f"  [{n}] {m}")
    return "\n".join(linhas)


# ---------------------------------------------------------------- PAR
AMOSTRA = "hamburgefontsivxzkqpjwy"


def _parecidas(fa, fb):
    """Semelhança de desenho das minúsculas com a MESMA altura-x (1 = mesma forma)."""
    import numpy as np
    def m(fi):
        f = _abrir(fi["arquivo"]); upm = f["head"].unitsPerEm
        px = round(40 * 4 / (fi["x_sobre_cap"] * fi["cap_upm"]) if fi["x_sobre_cap"] else 160)
        return _mascara(_pil(fi["arquivo"], fi["local"], px), AMOSTRA, 4)
    a, b = m(fa), m(fb)
    # compara letra a letra seria o ideal; aqui: perfil de tinta normalizado na largura (forma + ritmo)
    from PIL import Image
    w = 600
    A = np.asarray(Image.fromarray((a * 255).astype("uint8")).resize((w, 60), Image.BOX), np.float32) / 255
    B = np.asarray(Image.fromarray((b * 255).astype("uint8")).resize((w, 60), Image.BOX), np.float32) / 255
    return _semelhanca(A, B, sigma=1.2)


def par(titulo, texto, numeros=None, cliente=None, projeto=None):
    ft, fx = ficha(titulo), ficha(texto)
    fn = ficha(numeros) if numeros else None
    res = {"titulo": ft, "texto": fx, "numeros": fn, "avisos": []}
    av = res["avisos"]
    av += [("titulo",) + a for a in avisos_ficha(ft, "titulo")]
    av += [("texto",) + a for a in avisos_ficha(fx, "texto")]
    if fn:
        av += [("numeros",) + a for a in avisos_ficha(fn, "numeros")]
    else:
        av += [("numeros(texto)",) + a for a in avisos_ficha(fx, "numeros") if a[0] != "ok"]
    mesma = ft["familia"].split(" ")[0].lower() == fx["familia"].split(" ")[0].lower()
    sem = _parecidas(ft, fx)
    res["semelhanca_desenho"] = round(sem, 3)
    # largura relativa à MAIÚSCULA (não ao UPM): fontes com maiúscula alta (Big Shoulders) parecem largas por UPM
    lt, lx = ft["largura_min"] / max(ft["cap_upm"], 1e-6), fx["largura_min"] / max(fx["cap_upm"], 1e-6)
    dl = abs(lt - lx) / max(lx, 1e-6)
    if ft.get("densidade") and fx.get("densidade"):                   # peso visto (cor), não só a haste
        dp = abs(ft["densidade"] - fx["densidade"]) / max(fx["densidade"], 1e-6)
    else:
        dp = abs(ft["haste_cap"] - fx["haste_cap"]) / max(fx["haste_cap"], 1e-6)
    res["contraste"] = {"largura": round(dl, 3), "peso": round(dp, 3)}
    if not mesma and sem >= 0.80 and dl < 0.12 and dp < 0.35:
        av.append(("par", "ALERTA", f"parecidas demais sem ser a mesma família (desenho {sem:.2f}): parece erro, "
                                    "não escolha — trocar uma ou usar uma só família"))
    if mesma and dl < 0.08 and dp < 0.25:
        av.append(("par", "ALERTA", "mesma família sem contraste de largura/peso: título não se separa do texto"))
    if not mesma and dl < 0.08 and dp < 0.25 and sem < 0.80:
        av.append(("par", "ok", "contraste vem do desenho (estrutura), não de peso/largura — bom se for intencional"))
    dx = abs((ft["x_sobre_cap"] or 0) - (fx["x_sobre_cap"] or 0))
    if dx > 0.06:
        av.append(("par", "ALERTA", f"altura-x diferente ({ft['x_sobre_cap']} × {fx['x_sobre_cap']}): na MESMA linha, "
                                    "ajustar o tamanho do título pela altura-x (`font-size-adjust: ex-height`)"))
    if cliente:
        nov = novidade(cliente, [ft["familia"], fx["familia"]] + ([fn["familia"]] if fn else []), projeto)
        av += [("cliente", n, m) for n, m in nov]
    return res


def _txt_par(r):
    out = ["TÍTULO  " + _txt_ficha(r["titulo"], "titulo").replace("\n  [", "\n  ["),
           "TEXTO   " + _txt_ficha(r["texto"], "texto")]
    if r["numeros"]:
        out.append("NÚMEROS " + _txt_ficha(r["numeros"], "numeros"))
    out.append(f"PAR: desenho {r['semelhanca_desenho']:.2f} (1 = iguais) · contraste largura {r['contraste']['largura']:.0%}"
               f" · peso {r['contraste']['peso']:.0%}")
    for papel, n, m in r["avisos"]:
        if papel in ("par", "cliente", "numeros(texto)"):
            out.append(f"  [{n}] {papel}: {m}")
    vetos = [a for a in r["avisos"] if a[1] == "VETO"]
    out.append("RESULTADO: " + ("REPROVADO — " + "; ".join(f"{p}: {m}" for p, _, m in vetos) if vetos
                                else f"passa ({sum(1 for a in r['avisos'] if a[1] == 'ALERTA')} alertas para olhar)"))
    return "\n".join(out)


# ---------------------------------------------------------------- HISTÓRICO por cliente (rotação)
def _reg():
    if os.path.exists(REGISTRO):
        return json.load(open(REGISTRO, encoding="utf-8"))
    return {"sobre": "Fontes usadas por cliente/projeto (tipos.py usar). Série = mesma tipografia em todas as peças; "
                     "projeto NOVO do mesmo cliente = trazer algo novo (ver tipos.py par --cliente).", "usos": []}


def usar(cliente, projeto, titulo, texto, numeros=None, status="teste", nota="", eixos=None, tecnicas=None):
    r = _reg()
    fam = lambda s: ficha(s)["familia"] if s else None
    r["usos"] = [u for u in r["usos"] if not (u["cliente"] == cliente and u["projeto"] == projeto)]
    u = {"cliente": cliente, "projeto": projeto, "data": datetime.date.today().isoformat(),
         "status": status, "titulo": titulo, "texto": texto, "numeros": numeros,
         "familias": list(dict.fromkeys(x for x in (fam(titulo), fam(texto), fam(numeros)) if x)), "nota": nota}
    if eixos:
        u["eixos"] = _eixos(eixos)
    if tecnicas:
        u["tecnicas"] = [int(t) for t in str(tecnicas).replace(" ", "").split(",") if t]
    r["usos"].append(u)
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    json.dump(r, open(REGISTRO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("registrado:", cliente, "/", projeto, "→", REGISTRO)


def historico(cliente):
    """Registro (o que o estúdio usou) + tipografia descrita nas fichas da biblioteca (o que o cliente já tem)."""
    usos = [u for u in _reg()["usos"] if u["cliente"].lower() == cliente.lower()]
    fichas = {}
    p = os.path.join(BIBLIOTECA, cliente, "_fichas.json")
    if os.path.exists(p):
        fichas = {k: v.get("tipografia", "") for k, v in json.load(open(p, encoding="utf-8")).items()}
    return usos, fichas


def novidade(cliente, familias, projeto=None):
    usos, fichas = historico(cliente)
    out = []
    outros = [u for u in usos if u["projeto"] != projeto]
    for fam in dict.fromkeys(familias):
        ja = [u["projeto"] for u in outros if fam in u["familias"]]
        if ja:
            out.append(("ALERTA", f"{fam} já usada em: {', '.join(ja)} — projeto novo pede voz nova (ou motivo escrito)"))
        cit = [k for k, t in fichas.items() if fam.lower().split(" ")[0] in t.lower()]
        if cit:
            out.append(("ALERTA", f"{fam} lembra a tipografia de {', '.join(cit)} (fichas da biblioteca)"))
    if not out:
        out.append(("ok", "voz nova para este cliente"))
    return out


# ---------------------------------------------------------------- ROTAÇÃO: "inovar sempre" sem perder a marca
# Matriz de eixos e regras: pesquisa 16c §5 (Public Theater/Pentagram: mesma fonte, tratamento novo por temporada;
# Lelis 2020: a tipografia é o vetor constante). Constantes do cliente (família da marca, cor-base, logo, irmã de dados,
# regras de leitura, grid) NÃO giram. Números das técnicas = catálogo da 16c §2.
MATRIZ = {
    "T": ("tratamento da fonte", {"T1": "limpo", "T2": "cortado/sangrado", "T3": "inclinado/faixas", "T4": "estêncil",
          "T5": "contorno/eco", "T6": "esticado (wdth)", "T7": "em caminho/círculo", "T8": "à mão por cima",
          "T9": "pixel/grade", "T10": "com fio/anotado"}),
    "A": ("arranjo", {"A1": "empilhado", "A2": "bloco justificado", "A3": "grade", "A4": "diagonal",
          "A5": "vertical/lombada", "A6": "bandeira à esquerda", "A7": "centrado simétrico", "A8": "espalhado nos cantos"}),
    "E": ("escala", {"E1": "1:2", "E2": "1:4", "E3": "1:8", "E4": "1:16 (numeral herói)"}),
    "V": ("voz secundária", {"V0": "nenhuma", "V1": "serifa itálica", "V2": "mono de dado", "V3": "versalete", "V4": "mão"}),
    "I": ("relação com imagem", {"I1": "sobre", "I2": "atrás da pessoa", "I3": "dentro (máscara)", "I4": "vazado",
          "I5": "ao lado", "I6": "em superfície"}),
    "S": ("superfície", {"S0": "limpo", "S1": "sombra dura", "S2": "misregistro", "S3": "grão", "S4": "extrusão",
          "S5": "cor/COLR"}),
    "X": ("eixo variável estrela", {"X0": "nenhum", "X1": "peso", "X2": "largura", "X3": "opsz", "X4": "arredondamento",
          "X5": "eixo de história"}),
    "M": ("movimento", {"M1": "linha", "M2": "palavra por batida", "M3": "troca de palavra", "M4": "contagem",
          "M5": "eixo", "M6": "legenda expressiva"}),
    "D": ("densidade", {"D1": "uma palavra", "D2": "3–7 palavras", "D3": "bloco"}),
    "C": ("cor do tipo", {"C1": "positivo", "C2": "negativo", "C3": "acento", "C4": "tom sobre tom", "C5": "gradiente tonal"}),
}
FIXOS_CAMPANHA = ("T", "X", "C")         # assinatura da campanha; A, E, I, D variam peça a peça (arquétipos)


def _eixos(e):
    """'T2,A1,E3' ou dict → {'T': 'T2', ...} (valida contra a MATRIZ)."""
    if isinstance(e, dict):
        itens = list(e.values())
    else:
        itens = [x.strip().upper() for x in str(e).split(",") if x.strip()]
    out = {}
    for v in itens:
        k = re.match(r"[A-Z]", v).group(0)
        if k not in MATRIZ or v not in MATRIZ[k][1]:
            raise SystemExit(f"eixo inválido: {v} (ver tipos.py rotacao --matriz)")
        out[k] = v
    return out


def _campanhas(cliente):
    usos, _ = historico(cliente)
    return sorted([u for u in usos if u.get("eixos")], key=lambda u: u["data"])


def distancia(a, b):
    """Nº de eixos diferentes (Hamming) entre duas combinações, só nos eixos que as duas declaram."""
    return sum(1 for k in set(a) & set(b) if a[k] != b[k])


def rotacao(cliente, n=5, fixar=None, mudar=(3, 5), descanso=3, semente=None, video=False):
    """Gera n combinações para a próxima campanha (16c §5.3):
    1. muda 3–5 eixos em relação à campanha anterior (menos = 'de novo a mesma coisa'; mais = deixa de ser a marca);
    2. T muda SEMPRE e não repete nas últimas 4 campanhas;
    3. valor usado em 2 campanhas seguidas descansa por 3;
    4. distância ≥ 3 de cada uma das últimas 3 campanhas;
    5. `fixar` = gatilho do assunto (ex.: {'T': 'T7'} porque o fato do briefing é circular)."""
    import random
    rnd = random.Random(semente)
    camps = _campanhas(cliente)
    fixar = _eixos(fixar) if fixar else {}
    eixos_usados = [k for k in MATRIZ if video or k != "M"]
    ult = camps[-1]["eixos"] if camps else {}
    ultimas3 = [c["eixos"] for c in camps[-3:]]
    t_proibidos = {c["eixos"].get("T") for c in camps[-4:]}
    descansando = set()
    for i in range(1, len(camps)):
        if i >= len(camps) - descanso:                      # só pesa o que aconteceu nas últimas campanhas
            for k, v in camps[i]["eixos"].items():
                if camps[i - 1]["eixos"].get(k) == v:
                    descansando.add(v)
    cands, tent = {}, 0
    while len(cands) < n * 6 and tent < 4000:
        tent += 1
        base = dict(ult) if ult else {k: rnd.choice(list(MATRIZ[k][1])) for k in eixos_usados}
        for k in eixos_usados:
            base.setdefault(k, rnd.choice(list(MATRIZ[k][1])))
        k_mudar = rnd.randint(*mudar) if ult else len(eixos_usados)
        outros = [k for k in eixos_usados if k != "T" and k not in fixar]
        trocar = {"T"} | set(rnd.sample(outros, min(len(outros), max(0, k_mudar - 1))))
        ok = True
        for k in trocar:
            if k in fixar:
                continue
            op = [v for v in MATRIZ[k][1] if v != ult.get(k) and v not in descansando
                  and not (k == "T" and v in t_proibidos)]
            if not op:
                ok = False; break
            base[k] = rnd.choice(op)
        base.update(fixar)
        if not ok or (ult and not (mudar[0] <= distancia(base, ult) <= mudar[1])):
            continue
        if any(distancia(base, c) < 3 for c in ultimas3):
            continue
        chave = ",".join(base[k] for k in eixos_usados)
        cands[chave] = (sum(distancia(base, c) for c in ultimas3), base)
    ordem = sorted(cands.values(), key=lambda x: -x[0])
    # variedade entre as opções: cada nova difere em ≥ 3 eixos das já escolhidas
    escolha = []
    for sc, c in ordem:
        if all(distancia(c, e) >= 3 for _, e in escolha):
            escolha.append((sc, c))
        if len(escolha) == n:
            break
    return camps, escolha


def _txt_rotacao(cliente, camps, escolha):
    lin = [f"Histórico com eixos ({len(camps)} campanha(s)): " +
           ("; ".join(f"{c['projeto']} = {','.join(c['eixos'].values())}" for c in camps[-4:]) or "nenhum (1ª campanha registrada)")]
    for i, (sc, c) in enumerate(escolha, 1):
        lin.append(f"\nOPÇÃO {i}  (distância somada às últimas 3: {sc})  →  --eixos \"{','.join(c.values())}\"")
        for k, v in c.items():
            lin.append(f"   {k} {MATRIZ[k][0]:22s} {v:4s} {MATRIZ[k][1][v]}")
    lin.append(f"\nNa campanha, {', '.join(FIXOS_CAMPANHA)} ficam fixos (assinatura); A, E, I, D variam peça a peça.")
    return "\n".join(lin)


# ---------------------------------------------------------------- SUGERIR: propor pares (não só avaliar)
RECEITAS = os.path.join(os.path.dirname(HERE), "assets", "fontes", "receitas.json")
CATALOGO = os.path.join(os.path.dirname(HERE), "assets", "fontes", "catalogo.json")


def pontuar(r):
    """Nota do par (16a §7.4) a partir do resultado de par(). VETO = None (fora).
    +2 por eixo de contraste (largura, peso, serifa, mono, contraste de traço), até 3 eixos · +2 parecidas na
    estrutura (altura-x ±0,06) · +2 mesma família (superfamília) · −5 conflito · −3 voz já usada pelo cliente ·
    −2 por confusão crítica em texto/números."""
    if any(a[1] == "VETO" for a in r["avisos"]):
        return None, ["VETO"]
    ft, fx = r["titulo"], r["texto"]
    mesma = ft["familia"].split(" ")[0].lower() == fx["familia"].split(" ")[0].lower()
    eixos = []
    if r["contraste"]["largura"] >= 0.12: eixos.append("largura")
    if r["contraste"]["peso"] >= 0.35: eixos.append("peso")
    if ft.get("serifa") is not None and ft.get("serifa") != fx.get("serifa"): eixos.append("serifa")
    if ft.get("mono") != fx.get("mono"): eixos.append("mono")
    ct, cx = ft.get("contraste_traco"), fx.get("contraste_traco")
    if ct is not None and cx is not None and abs(ct - cx) >= 0.25: eixos.append("contraste de traço")
    nota, porque = 2 * min(3, len(eixos)), []
    if eixos:
        porque.append("contraste em " + ", ".join(eixos))
    if ft["x_sobre_cap"] and fx["x_sobre_cap"] and abs(ft["x_sobre_cap"] - fx["x_sobre_cap"]) <= 0.06:
        nota += 2; porque.append("mesma altura-x (estrutura parecida)")
    if mesma:
        nota += 2; porque.append("mesma família: contraste por peso/largura")
    for papel, n, m in r["avisos"]:
        if papel == "par" and n == "ALERTA" and "parecidas demais" in m:
            nota -= 5; porque.append("CONFLITO: parecidas demais")
        if papel == "cliente" and n == "ALERTA" and ft["familia"] in m:
            nota -= 3; porque.append("voz já usada pelo cliente")
        if papel in ("texto", "numeros") and n == "ALERTA" and "crítico" in m:
            nota -= 2
    if len(eixos) < 2 and not mesma:
        porque.append("só %d eixo de contraste (pede ≥ 2)" % len(eixos))
    return nota, porque


def _grupo(r):
    ft, fx = r["titulo"], r["texto"]
    if ft["familia"].split(" ")[0].lower() == fx["familia"].split(" ")[0].lower():
        return "uma família (eixos)"
    if ft.get("mono"):
        return "mono herói"
    if ft.get("serifa") != fx.get("serifa"):
        return "serifa × sem serifa"
    if r["contraste"]["largura"] >= 0.25:
        return "largura × normal"
    return "contraste de desenho"


def sugerir(vozes=None, cliente=None, projeto=None, n=6, incluir_sistemas=True, todas=False, campanha=None):
    """Lê receitas.json (16a §4, 16d §5), testa cada par com par() e devolve os n melhores de GRUPOS diferentes."""
    if not os.path.exists(RECEITAS):
        raise SystemExit("falta assets/fontes/receitas.json")
    d = json.load(open(RECEITAS, encoding="utf-8"))
    cands = list(d.get("receitas", []))
    if incluir_sistemas and cliente:
        sc = d.get("sistemas_cliente", {}).get(cliente, {})
        indicados = set()
        if campanha:
            for k, ids in sc.get("mapa_campanhas", {}).items():
                if campanha.lower() in k.lower() or k.lower() in campanha.lower():
                    indicados |= set(ids)
        for sis in sc.get("sistemas", []):
            if campanha and indicados and sis.get("id") not in indicados:
                continue                                  # sistema do cliente feito para outro tipo de campanha
            c = {**sis, "voz": "sistema-" + cliente, "ref": sc.get("ref", ""), "_indicado": sis.get("id") in indicados}
            if not c.get("numeros") and sc.get("ancora"):              # preço na âncora da marca (16d §5)
                c["numeros"] = f"{sc['ancora']}:600"
            cands.append(c)
    if vozes:
        vz = [v.strip().lower() for v in vozes.split(",")]
        cands = [c for c in cands if c.get("voz", "").startswith("sistema-")       # sistemas do cliente: sempre
                 or any(v in (c.get("voz", "") + " " + c.get("nome", "")).lower() for v in vz)]
    evitar = {}
    if os.path.exists(CATALOGO):
        for f_ in json.load(open(CATALOGO, encoding="utf-8")).get("fontes", []):
            if f_.get("evitar_como_voz"):
                evitar[f_["familia"].lower()] = f_.get("motivo_evitar", "") or "lista de evitar (16b §20)"
    res, falhas = [], []
    for c in cands:
        try:
            r = par(c["titulo"], c["texto"], c.get("numeros"), cliente, projeto)
        except BaseException as e:                       # fonte fora do Google / sem arquivo
            falhas.append((c.get("id", c.get("nome")), str(e)[:90])); continue
        nota, porque = pontuar(r)
        if nota is not None and c.get("_indicado"):
            nota += 3; porque.append(f"sistema do cliente indicado para \"{campanha}\"")
        fam_t = c["titulo"].split(":")[0].strip().lower()
        if nota is not None and fam_t in evitar:
            nota -= 3; porque.append(f"catálogo manda evitar como voz ({evitar[fam_t][:60]})")
        res.append({"rec": c, "par": r, "nota": nota, "porque": porque, "grupo": _grupo(r)})
    ok = sorted([x for x in res if x["nota"] is not None], key=lambda x: -x["nota"])
    if todas:
        return ok, [x for x in res if x["nota"] is None], falhas
    escolha, grupos = [], {}
    for x in ok:                                         # diversidade: no máx. 2 por grupo na 1ª passada
        if grupos.get(x["grupo"], 0) < 2:
            escolha.append(x); grupos[x["grupo"]] = grupos.get(x["grupo"], 0) + 1
        if len(escolha) == n:
            break
    for x in ok:
        if len(escolha) >= n:
            break
        if x not in escolha:
            escolha.append(x)
    escolha.sort(key=lambda x: -x["nota"])
    return escolha, [x for x in res if x["nota"] is None], falhas


def _txt_sugerir(escolha, reprovados, falhas):
    lin = []
    for i, x in enumerate(escolha, 1):
        c = x["rec"]
        lin.append(f"{i}. [{x['nota']:+d}] {c.get('nome', '')} · {c.get('voz', '')} · {x['grupo']}  ({c.get('ref', '')})")
        lin.append(f"   título {c['titulo']} · texto {c['texto']}" + (f" · números {c['numeros']}" if c.get("numeros") else "")
                   + (f" · acento {c['acento']}" if c.get("acento") else ""))
        lin.append("   por quê: " + "; ".join(x["porque"]))
        al = [f"{p}: {m}" for p, nv, m in x["par"]["avisos"] if nv == "ALERTA"]
        if al:
            lin.append("   olhar: " + " | ".join(al[:4]))
    if reprovados:
        lin.append("\nREPROVADOS pelo medidor: " + "; ".join(
            f"{x['rec'].get('nome', '')} ({'; '.join(m for _, nv, m in x['par']['avisos'] if nv == 'VETO')[:80]})" for x in reprovados))
    if falhas:
        lin.append("\nNão testados (fonte fora do Google ou sem arquivo): " + "; ".join(f"{a}" for a, _ in falhas))
    return "\n".join(lin)


# ---------------------------------------------------------------- FOLHA de pares (prova visual)
def _css_inst(fi):
    """CSS da instância: wght → font-weight, wdth → font-stretch, demais eixos → font-variation-settings."""
    loc = dict(fi["local"])
    css = [f"font-weight:{int(loc.pop('wght', 400))}"]
    if "wdth" in loc:
        css.append(f"font-stretch:{loc.pop('wdth'):g}%")
    if loc:
        css.append("font-variation-settings:" + ",".join(f'"{k}" {v:g}' for k, v in loc.items()))
    return ";".join(css)


def _tira(fi, papel="texto", todas=False):
    """Pares de confusão desenhados como o medidor viu (maiúscula 11 px), ampliados 5× sem suavizar.
    Sem `todas`: só os pares que importam para o papel (críticos) e os que passaram perto do limite."""
    import base64, io
    from PIL import Image
    f = _abrir(fi["arquivo"]); upm = f["head"].unitsPerEm
    esc = 4
    fo = _pil(fi["arquivo"], fi["local"], max(4, round(CAP_PX * esc / fi["cap_upm"])))
    itens = []
    crit = CRITICOS_NUM if papel == "numeros" else CRITICOS
    for k, v in fi["confusoes"].items():
        p, q = k.split("/")
        lim = LIMITE.get(k, 0.85)
        if not todas and (p, q) not in crit and (papel != "texto" or v < lim - FOLGA):
            continue                   # título e números: só o que importa no papel; texto: + os perto do limite
        cor = "#D7261E" if v >= lim and k != "I/l" else ("#E39B12" if v >= lim - FOLGA else "#2E8B57")
        ims = []
        for t in (p, q):
            m = _mascara(fo, t, esc)
            im = Image.fromarray((255 - m * 255).astype("uint8")).resize((m.shape[1] * 5, m.shape[0] * 5), Image.NEAREST)
            b = io.BytesIO(); im.save(b, "PNG")
            ims.append("data:image/png;base64," + base64.b64encode(b.getvalue()).decode())
        itens.append(f'<div class="cf" style="border-color:{cor}"><div class="cfi"><img src="{ims[0]}"><img src="{ims[1]}">'
                     f'</div><span style="color:{cor}">{p} {q} · {v:.2f}</span></div>')
    return '<div class="tira">' + "".join(itens) + "</div>"


LEAD = ("Cada par com prova medida: as tiras mostram as letras que mais se confundem desenhadas no tamanho de um "
        "texto de celular (maiúscula de 11 px), ampliadas sem suavizar. Verde = separa bem · laranja = olhar · "
        "vermelho = se confundem. O número é a semelhança (1,00 = iguais).")

CSS_PARES = """*{box-sizing:border-box;margin:0;padding:0}
body{width:2400px;background:#EDEAE3;color:#121212;font-family:V;padding:96px}
h1{font-weight:800;font-size:88px;letter-spacing:-0.025em;line-height:1}
.lead{font:500 26px/1.45 V;color:#3a3a3a;margin:22px 0 64px;max-width:1700px}
.grade{display:grid;grid-template-columns:1fr 1fr;gap:28px}
.card{background:#fff;border:2px solid #121212;border-radius:22px;padding:30px 36px 34px;overflow:hidden}
.cab{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;border-bottom:2px solid #121212;padding-bottom:16px;margin-bottom:24px}
.nm{font:800 30px/1.1 V;display:block} .fs{font:500 18px/1.4 M;font-stretch:80%;color:#555}
.selo{font:700 17px/1 M;letter-spacing:.06em;border-radius:999px;padding:10px 16px;white-space:nowrap;color:#fff}
.selo.ok{background:#2E8B57} .selo.al{background:#E39B12} .selo.ve{background:#D7261E}
.t1{font-size:74px;line-height:.98;white-space:nowrap} .t2{font-size:38px;line-height:1.15;margin-top:14px;color:#C2410C}
.par{font-size:24px;line-height:1.5;margin-top:16px;color:#2a2a2a;max-width:1040px}
.num{font-size:28px;line-height:1.3;margin-top:16px;background:#121212;color:#F2EFE8;padding:12px 16px;border-radius:12px}
.med{font:500 18px/1.4 M;font-stretch:80%;color:#666;margin-top:16px}
.av{list-style:none;margin-top:10px;display:grid;gap:6px}
.av li{font:500 19px/1.35 V;padding-left:16px;border-left:4px solid #999} .av li.veto{border-color:#D7261E} .av li.alerta{border-color:#E39B12}
.av i{font:700 15px M;font-style:normal;color:#777;margin-right:10px;text-transform:uppercase}
.rt{font:700 15px/1 M;letter-spacing:.08em;color:#777;margin:18px 0 8px}
.tira{display:flex;flex-wrap:wrap;gap:8px}
.cf{border:2px solid;border-radius:10px;padding:6px 8px 4px;background:#fff}
.cfi{display:flex;gap:6px;align-items:flex-end} .cfi img{display:block;image-rendering:pixelated}
.cf span{font:700 13px/1.6 M;display:block;text-align:center}"""

JS_AJUSTE = """for (const e of document.querySelectorAll('.num')) { e.style.whiteSpace = 'nowrap';
  for (let i = 0; i < 3; i++) {                       // mede o texto num span (a caixa não diz quanto a tinta passa)
    const w = (e.clientWidth - 32) * 0.97, sp = document.createElement('span');
    sp.textContent = e.textContent; sp.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font:inherit;font-variant-numeric:inherit';
    e.appendChild(sp); const larg = sp.getBoundingClientRect().width; sp.remove();
    const fs = parseFloat(getComputedStyle(e).fontSize);
    if (larg > w) e.style.fontSize = (fs * w / larg) + 'px'; } }
for (const e of document.querySelectorAll('.t1,.t2')) { const w = (e.parentElement.clientWidth - 72) * 0.98;
  e.style.width = 'max-content';
  for (let i = 0; i < 3; i++) {                       // 3 passadas: eixos (opsz) mudam a largura com o tamanho
    const fs = parseFloat(getComputedStyle(e).fontSize), larg = e.getBoundingClientRect().width;
    if (larg > w || e.classList.contains('t1')) e.style.fontSize = Math.min(fs * 1.6, fs * w / larg) + 'px'; } }"""


def folha(spec, out):
    """spec = {"titulo", "lead"?, "cliente"?, "projeto"?, "pares": [{"nome", "titulo": "Fam:peso:eixos", "texto": "…",
    "numeros"?: "…", "nota"?, "frase"?}]}. Por par: título ajustado à largura, linha de apoio, parágrafo, números
    (preço, contador, telefone, cupom), tiras de confusão no tamanho de celular e o veredito do `par`."""
    from referencia import _png, _fontes_base, TIT, MIX, PAR
    from palco import data_url
    ff, cards, k = [], [], 0
    for pr in spec["pares"]:
        r = par(pr["titulo"], pr["texto"], pr.get("numeros"), spec.get("cliente"), spec.get("projeto"))
        fams = {}
        for papel in ("titulo", "texto", "numeros"):
            fi = r[papel]
            if not fi:
                continue
            ff.append(f"@font-face{{font-family:t{k};src:url({data_url(fi['arquivo'], 'font/ttf')});"
                      f"font-weight:100 1000;font-stretch:50% 200%}}")
            fams[papel] = (f"t{k}", _css_inst(fi)); k += 1
        ft, fx = fams["titulo"], fams["texto"]
        fn = fams.get("numeros", fx)
        vetos = [a for a in r["avisos"] if a[1] == "VETO"]
        alertas = [a for a in r["avisos"] if a[1] == "ALERTA"]
        if vetos:
            selo = '<b class="selo ve">REPROVADO</b>'
        elif alertas:
            selo = f'<b class="selo al">PASSA · {len(alertas)} alerta(s)</b>'
        else:
            selo = '<b class="selo ok">PASSA</b>'
        lis = "".join(f'<li class="{n.lower()}"><i>{p}</i>{m}</li>' for p, n, m in r["avisos"]
                      if n != "ok" or p in ("par", "cliente"))
        tiras = "".join(f'<p class="rt">{nm}: {r[pp]["familia"]}</p>{_tira(r[pp], pp, spec.get("tiras") == "todas")}'
                        for pp, nm in (("titulo", "TÍTULO"), ("texto", "TEXTO"), ("numeros", "NÚMEROS")) if r.get(pp))
        extra = (" + " + pr["numeros"]) if pr.get("numeros") else ""
        nota = (" · " + pr["nota"]) if pr.get("nota") else ""
        cards.append(f"""<div class="card"><div class="cab"><div><b class="nm">{pr['nome']}</b>
<span class="fs">{pr['titulo']} + {pr['texto']}{extra}</span></div>{selo}</div>
<p class="t1" style="font-family:{ft[0]};{ft[1]}">{pr.get('frase', TIT)}</p>
<p class="t2" style="font-family:{ft[0]};{ft[1]}">{MIX}</p>
<p class="par" style="font-family:{fx[0]};{fx[1]}">{PAR}</p>
<p class="num" style="font-family:{fn[0]};{fn[1]};font-variant-numeric:tabular-nums lining-nums">R$ 1.191,00 · 12x R$ 99,25 · 02:14:37 · (11) 98765-4321 · BLACK10OFF</p>
<p class="med">desenho {r['semelhanca_desenho']:.2f} · contraste largura {r['contraste']['largura']:.0%} · peso {r['contraste']['peso']:.0%}{nota}</p>
<ul class="av">{lis}</ul>{tiras}</div>""")
    html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{''.join(ff)}{_fontes_base()}{CSS_PARES}</style></head>"
            f"<body><h1>{spec.get('titulo', 'Pares de fontes com prova')}</h1><p class='lead'>{spec.get('lead', LEAD)}</p>"
            f"<div class='grade'>{''.join(cards)}</div></body></html>")
    _png(html, out, js=JS_AJUSTE)


# ---------------------------------------------------------------- calibração (rodar ao mexer nos limites)
def calibrar():
    """Fontes com confusão CONHECIDA × fontes conhecidas por separar bem. Imprime a tabela de confusões."""
    casos = ["Hubot Sans:700", "Mona Sans:700", "Urbanist:600", "Figtree:400", "Onest:400", "Schibsted Grotesk:400",
             "Big Shoulders Display:800", "Martian Mono:500", "Archivo:400", "Bebas Neue:400"]
    for c in casos:
        try:
            fi = ficha(c)
        except SystemExit as e:
            print(c, "→", e); continue
        print(f"{c:28s}", "  ".join(f"{k} {v:.2f}" for k, v in fi["confusoes"].items()))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")         # ajuda e saída com ≥, ×, → no console do Windows
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ficha"); a.add_argument("fonte"); a.add_argument("--papel", default="texto",
                                                                           choices=["titulo", "texto", "numeros"])
    a.add_argument("--json", action="store_true")
    a = sub.add_parser("par"); a.add_argument("titulo"); a.add_argument("texto"); a.add_argument("--numeros")
    a.add_argument("--cliente"); a.add_argument("--projeto"); a.add_argument("--json", action="store_true")
    a = sub.add_parser("usar"); a.add_argument("--cliente", required=True); a.add_argument("--projeto", required=True)
    a.add_argument("--titulo", required=True); a.add_argument("--texto", required=True); a.add_argument("--numeros")
    a.add_argument("--status", default="teste", choices=["teste", "aprovado", "reprovado"]); a.add_argument("--nota", default="")
    a.add_argument("--eixos", help='matriz de rotação, ex.: "T2,A1,E3,V2,I2,S0,X2,D2,C3"'); a.add_argument("--tecnicas", help="nºs do catálogo 16c §2")
    a = sub.add_parser("rotacao"); a.add_argument("--cliente"); a.add_argument("--n", type=int, default=5)
    a.add_argument("--fixar", help='gatilho do assunto, ex.: "T7" (fato circular)'); a.add_argument("--video", action="store_true")
    a.add_argument("--semente", type=int); a.add_argument("--matriz", action="store_true")
    a = sub.add_parser("historico"); a.add_argument("--cliente", required=True)
    sub.add_parser("calibrar")
    a = sub.add_parser("folha"); a.add_argument("spec"); a.add_argument("-o", required=True)
    a = sub.add_parser("sugerir"); a.add_argument("--voz", help='uma ou mais vozes, ex.: "esportivo,tecnico"')
    a.add_argument("--cliente"); a.add_argument("--projeto"); a.add_argument("--n", type=int, default=6)
    a.add_argument("--folha", help="grava a folha visual dos sugeridos (PNG)"); a.add_argument("--sem-sistemas", action="store_true")
    a.add_argument("--campanha", help='tipo de campanha do mapa do cliente, ex.: "Black Friday ao vivo"')
    x = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if x.cmd == "ficha":
        fi = ficha(x.fonte)
        print(json.dumps(fi, ensure_ascii=False, indent=1) if x.json else _txt_ficha(fi, x.papel))
    elif x.cmd == "par":
        r = par(x.titulo, x.texto, x.numeros, x.cliente, x.projeto)
        print(json.dumps(r, ensure_ascii=False, indent=1) if x.json else _txt_par(r))
    elif x.cmd == "usar":
        usar(x.cliente, x.projeto, x.titulo, x.texto, x.numeros, x.status, x.nota, x.eixos, x.tecnicas)
    elif x.cmd == "rotacao":
        if x.matriz or not x.cliente:
            for k, (nome, vals) in MATRIZ.items():
                print(f"{k} {nome}: " + " · ".join(f"{c} {v}" for c, v in vals.items()))
        else:
            camps, esc = rotacao(x.cliente, x.n, x.fixar, semente=x.semente, video=x.video)
            print(_txt_rotacao(x.cliente, camps, esc))
    elif x.cmd == "historico":
        usos, fichas = historico(x.cliente)
        print(f"REGISTRO ({len(usos)}):")
        for u in usos:
            print(f"  {u['data']} {u['projeto']} [{u['status']}]: {' + '.join(u['familias'])} {u['nota']}"
                  + (f" · eixos {','.join(u['eixos'].values())}" if u.get("eixos") else ""))
        print(f"BIBLIOTECA ({len(fichas)} fichas, só leitura):")
        for k, t in fichas.items():
            print(f"  {k}: {t}")
    elif x.cmd == "calibrar":
        calibrar()
    elif x.cmd == "folha":
        folha(json.load(open(x.spec, encoding="utf-8")), x.o)
    elif x.cmd == "sugerir":
        esc, rep_, fal = sugerir(x.voz, x.cliente, x.projeto, x.n, not x.sem_sistemas, campanha=x.campanha)
        print(_txt_sugerir(esc, rep_, fal))
        if x.folha and esc:
            folha({"titulo": f"Pares sugeridos · {x.voz or 'todas as vozes'}" + (f" · {x.cliente}" if x.cliente else ""),
                   "cliente": x.cliente, "projeto": x.projeto,
                   "pares": [{"nome": f"{i}. {e['rec'].get('nome', '')} [{e['nota']:+d}]", "titulo": e["rec"]["titulo"],
                              "texto": e["rec"]["texto"], "numeros": e["rec"].get("numeros"),
                              "nota": e["grupo"] + " · " + "; ".join(e["porque"][:2])}
                             for i, e in enumerate(esc, 1)]}, x.folha)
