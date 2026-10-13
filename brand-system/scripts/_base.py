"""Shared base for brand-system scripts: reuses brand-studio's core (fonts→curves, render, colour) + brand.json helpers."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
STUDIO_SCRIPTS = os.path.join(os.path.dirname(os.path.realpath(SKILL_DIR)), "brand-studio", "scripts")
if not os.path.isdir(STUDIO_SCRIPTS):
    STUDIO_SCRIPTS = os.path.join(os.path.expanduser("~"), ".claude", "skills", "brand-studio", "scripts")
sys.path.insert(0, STUDIO_SCRIPTS)

from common import (CACHE, LIBRARY_DIR, LOGO_SKILL, PROJECT_DIR, Font, contrast, find_chrome, font_path,  # noqa: E402,F401
                    hex_to_rgb, html_screenshot, luminance, recolor, rgb_to_cmyk, rgb_to_hex, svg_inner,
                    svg_to_png, viewbox, wrap_svg, write)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ASSETS = os.path.join(SKILL_DIR, "assets")
UI_FONT = "Space Grotesk:500"        # labels on sheets/manual pages (OFL)
UI_FONT_BOLD = "Space Grotesk:700"


# ------------------------------------------------------------------ brand.json
class Brand:
    """A brand project folder with brand.json as the single source of truth."""

    def __init__(self, path):
        path = os.path.abspath(path)
        self.file = path if path.endswith(".json") else os.path.join(path, "brand.json")
        self.dir = os.path.dirname(self.file)
        with open(self.file, encoding="utf-8") as fh:
            self.data = json.load(fh)

    def __getitem__(self, k):
        return self.data[k]

    def get(self, dotted, default=None):
        cur = self.data
        for part in dotted.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    def set(self, dotted, value):
        cur = self.data
        parts = dotted.split(".")
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = value

    def path(self, rel):
        if not rel:
            return None
        return rel if os.path.isabs(rel) else os.path.join(self.dir, rel)

    def rel(self, absolute):
        return os.path.relpath(absolute, self.dir).replace("\\", "/")

    def save(self):
        with open(self.file, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

    @property
    def name(self):
        return self.data.get("name", "Marca")

    @property
    def slug(self):
        return self.data.get("slug") or "".join(c for c in self.name.lower().replace(" ", "-") if c.isalnum() or c == "-")

    def colour(self, role, fallback="#111111"):
        """Resolve a colour role ('brand', 'ink', 'paper', 'accent', 'brand.700') to HEX."""
        pal = self.get("color.palette") or {}
        seeds = self.get("color.seeds") or {}
        if "." in role:
            r, step = role.split(".", 1)
            ramp = (pal.get("ramps") or {}).get(r) or {}
            if step in ramp:
                return ramp[step]["hex"]
        if role in seeds:
            v = seeds[role]
            return v["hex"] if isinstance(v, dict) else v
        if role.startswith("#"):
            return role
        return fallback

    def font_spec(self, role, default_weight=400, default_family=None):
        """Font spec for type.<role> that font_path() resolves: "Family:weight", or an absolute path when the brand
        uses its own font file (type.<role>.family/file = "fonte/Minha.ttf", relative to the project)."""
        e = (self.get("type") or {}).get(role)
        if not e:
            return f"{default_family}:{default_weight}" if default_family else None
        fam = e if isinstance(e, str) else (e.get("file") or e.get("family"))
        w = default_weight if isinstance(e, str) else e.get("weight", default_weight)
        if fam.lower().endswith((".ttf", ".otf")):
            p = self.path(fam)
            return p if os.path.isfile(p) else fam
        return fam if ":" in fam else f"{fam}:{w}"

    def primitive(self):
        """Main primitive (the shape devices derive from): primitives[] item with "main": true, else the first."""
        prims = [p for p in (self.get("primitives") or []) if p.get("src") and os.path.exists(self.path(p["src"]))]
        main = next((p for p in prims if p.get("main") or p.get("dna")), prims[0] if prims else None)
        if main:
            return self.path(main["src"])
        for k in ("logo.symbol", "logo.primary"):
            if self.get(k) and os.path.exists(self.path(self.get(k))):
                return self.path(self.get(k))
        return None

    def symbol(self):
        """Compact mark for favicon/avatar: logo.symbol, else a primitive with role "symbol" (or id simbolo/avatar/
        favicon/monograma), else None — never the long wordmark."""
        if self.get("logo.symbol") and os.path.exists(self.path(self.get("logo.symbol"))):
            return self.path(self.get("logo.symbol"))
        for p in self.get("primitives") or []:
            if (p.get("role") == "symbol" or p.get("id") in SYMBOL_IDS) and p.get("src") \
                    and os.path.exists(self.path(p["src"])):
                return self.path(p["src"])
        return None


SYMBOL_IDS = {"simbolo", "symbol", "avatar", "favicon", "monograma", "monogram", "icone"}


def vivid_on(bg, candidates, min_ratio=1.8):
    """First candidate colour that stands out on bg (contrast ≥ min_ratio); else the most contrasting one.
    Keeps a dark brand colour from vanishing on a dark ink background."""
    cands = [c for c in candidates if c]
    for c in cands:
        if contrast(c, bg) >= min_ratio:
            return c
    return max(cands, key=lambda c: contrast(c, bg)) if cands else ink_on(bg)


def load_brand(path):
    return Brand(path)


# ------------------------------------------------------------------ text helpers (sheets, manual)
_FONTS = {}


def font(spec=UI_FONT):
    if spec not in _FONTS:
        _FONTS[spec] = Font(font_path(spec))
    return _FONTS[spec]


def text_path(s, size, x, y, fill, spec=UI_FONT, tracking=0.0, anchor="start"):
    """Text as a <path> (outlines). anchor: start | middle | end; y = baseline."""
    f = font(spec)
    w = f.width(s, size, tracking)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    d = f.path(s, size, x, y, tracking)
    return f'<path d="{d}" fill="{fill}"/>' if d else ""


def text_width(s, size, spec=UI_FONT, tracking=0.0):
    return font(spec).width(s, size, tracking)


def ink_on(bg, light="#FFFFFF", dark="#111111"):
    """Best label colour on a background."""
    return light if contrast(bg, light) >= contrast(bg, dark) else dark


def sheet(out_png, items, cols=4, cell=360, label_h=40, bg="#F2F1EC", fg="#1A1A1A", title=None):
    """Contact sheet of SVG files/strings: items = [(label, svg_text_or_path), ...] → PNG."""
    rows = math.ceil(len(items) / cols) or 1
    top = 70 if title else 20
    W, H = cols * cell + 20, rows * (cell + label_h) + top + 10
    body = []
    if title:
        body.append(text_path(title, 30, 24, 48, fg, UI_FONT_BOLD))
    for i, (label, svg) in enumerate(items):
        if os.path.isfile(str(svg)):
            svg = open(svg, encoding="utf-8").read()
        x = 10 + (i % cols) * cell
        y = top + (i // cols) * (cell + label_h)
        vx, vy, vw, vh = viewbox(svg)
        # nested <svg> clips anything drawn outside the item's own viewBox
        body.append(f'<svg x="{x + 20}" y="{y + 20}" width="{cell - 40}" height="{cell - 40}" '
                    f'viewBox="{vx} {vy} {vw} {vh}" preserveAspectRatio="xMidYMid meet" overflow="hidden">'
                    f'{svg_inner(svg)}</svg>')
        body.append(text_path(label[:40], 15, x + 20, y + cell + 18, fg))
    svg = wrap_svg(W, H, "".join(body), bg=bg)
    svg_to_png(svg, out_png)
    return out_png


def slugify(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-").replace("--", "-")


def font_face(family, spec, weight=None, style="normal"):
    """@font-face with the font file embedded (base64) — HTML pages render with the real brand fonts offline."""
    import base64
    p = font_path(spec)
    fmt = "opentype" if p.lower().endswith(".otf") else "truetype"
    data = base64.b64encode(open(p, "rb").read()).decode()
    w = weight or (spec.split(":")[1].rstrip("i") if ":" in spec else "400")
    return (f"@font-face{{font-family:'{family}';src:url(data:font/{'otf' if fmt == 'opentype' else 'ttf'};base64,"
            f"{data}) format('{fmt}');font-weight:{w};font-style:{style};font-display:block}}")


def brand_font_faces(brand):
    """@font-face rules for the brand's display/text(/mono) fonts → (css, {role: css-family-name})."""
    t = brand.get("type") or {}
    css, names = [], {}
    for role in ("display", "text", "mono"):
        e = t.get(role)
        if not e:
            continue
        fam = e if isinstance(e, str) else (e.get("file") or e.get("family"))
        w = 400 if isinstance(e, str) else e.get("weight", 400)
        spec = brand.font_spec(role, w)
        name = f"brand-{role}"
        css.append(font_face(name, spec, w))
        if role == "text" and not fam.lower().endswith((".ttf", ".otf")):   # a bold cut for UI emphasis
            try:
                css.append(font_face(name, f"{fam}:700", 700))
            except Exception:
                pass
        names[role] = name
    return "\n".join(css), names


# ------------------------------------------------------------------ produtos (sub-identidades por cor)
# Pares de contraste de cada produto: (nome, cor do texto, cor do fundo, mínimo WCAG, para quê).
# texto corrido pede 4,5:1 (AA); destaque = título grande / gráfico / ícone pede 3:1 (AA grande, 1.4.11);
# o texto do botão é pequeno (16–18 px) → 4,5:1.
PRODUCT_PAIRS = [("texto", "ink", "bg", 4.5, "texto corrido"),
                 ("destaque", "accent", "bg", 3.0, "título grande / gráfico"),
                 ("botão", "on_accent", "accent", 4.5, "texto no botão cheio")]


def grade(ratio):
    """Nota WCAG 2 de um par: AAA (≥ 7) · AA (≥ 4,5) · AA grande (≥ 3: título ≥ 24 px ou 18,7 px negrito,
    gráfico, ícone) · falha."""
    return "AAA" if ratio >= 7 else "AA" if ratio >= 4.5 else "AA grande" if ratio >= 3 else "falha"


def fmt_ratio(r):
    """4.5 → '4,5:1' (vírgula decimal, pt-BR). Trunca, nunca arredonda para cima: 4,47 vira 4,4 (e não um
    "4,5" que parece passar)."""
    return f"{math.floor(r * 10 + 1e-9) / 10:.1f}".replace(".", ",") + ":1"


def _norm_colors(c, fb):
    c = dict(c or {})
    bg = (c.get("bg") or fb["bg"]).upper()
    ink = (c.get("ink") or ink_on(bg, fb["paper"], fb["ink_dark"])).upper()
    accent = (c.get("accent") or fb["accent"]).upper()
    on = (c.get("on_accent") or c.get("on-accent") or ink_on(accent, fb["paper"], fb["ink_dark"])).upper()
    # live = ponto ao vivo / tally (pode diferir do destaque: num tema alternativo o destaque pode ser preto e o ponto,
    # vermelho); frame = visor/moldura. Sem eles, o destaque.
    live = (c.get("live") or c.get("dot") or accent).upper()
    frame = (c.get("frame") or accent).upper()
    return {"bg": bg, "ink": ink, "accent": accent, "on_accent": on, "live": live, "frame": frame}


def products(brand):
    """brand.json "products" normalizado e ordenado por "order": cada item ganha id, name e colors completas
    (bg, ink, accent, on_accent + alt opcional, com os mesmos 4 campos). Lista vazia quando não há produtos."""
    raw = brand.get("products") or []
    fb = {"bg": brand.colour("ink"), "paper": brand.colour("paper", "#F4F3EF"), "ink_dark": brand.colour("ink"),
          "accent": brand.colour("brand")}
    out = []
    for i, p in enumerate(raw):
        if not isinstance(p, dict) or not (p.get("id") or p.get("name")):
            continue
        q = dict(p)
        q["id"] = slugify(p.get("id") or p["name"])
        q["name"] = p.get("name") or q["id"]
        # nome próprio da cor (ex.: "Azul Chroma") — string ou {"name", "status"}; status "proposta…" = falta o sim
        cn = p.get("color_name")
        q["color_name"] = (cn.get("name") if isinstance(cn, dict) else cn) or ""
        q["color_name_status"] = (cn.get("status") if isinstance(cn, dict) else p.get("color_name_status")) or ""
        # rótulo escrito que acompanha a cor (WCAG 1.4.1: a cor nunca é o único sinal). Sem "label", monta
        # "NOITE N · Professor · Pós" a partir de products[].noite (dados do cliente; nada inventado)
        nt = p.get("noite") if isinstance(p.get("noite"), dict) else {}
        auto = " · ".join(str(x) for x in (f"NOITE {nt['n']}" if nt.get("n") else "", nt.get("professor"),
                                            p.get("name")) if x) if nt else ""
        q["label"] = p.get("label") or auto
        main = _norm_colors(p.get("colors"), fb)
        alt = (p.get("colors") or {}).get("alt")
        if alt:
            main["alt"] = _norm_colors(alt, {**fb, "bg": main["accent"], "accent": main["bg"]})
        q["colors"] = main
        q["_i"] = i
        out.append(q)
    out.sort(key=lambda q: (q.get("order") if isinstance(q.get("order"), (int, float)) else 1e9, q["_i"]))
    return out


def product_pairs(colors):
    """Pares de contraste de um jogo de cores {bg, ink, accent, on_accent} →
    [{"par", "fg", "bg", "ratio", "need", "uso", "ok", "nota"}]."""
    out = []
    for name, f, g, need, uso in PRODUCT_PAIRS:
        r = contrast(colors[f], colors[g])
        out.append({"par": name, "fg": colors[f], "bg": colors[g], "ratio": round(r, 2), "need": need, "uso": uso,
                    "ok": r >= need, "nota": grade(r)})
    return out


def solid(svg_text, colour):
    """Recolour an SVG to one colour robustly: fill attributes, styles AND inherited fills (root fill survives
    being inlined), returned as a clean standalone SVG."""
    s = recolor(svg_text, colour)
    vx, vy, vw, vh = viewbox(s)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:g} {vy:g} {vw:g} {vh:g}" width="{vw:g}" '
            f'height="{vh:g}"><g fill="{colour}">{svg_inner(s)}</g></svg>')


# ------------------------------------------------------------------ "[a definir]" (o que é do cliente e não existe)
A_DEFINIR = "[a definir]"
_AVISADOS = set()


def vazio(valor):
    """None, "", "[a definir…]", lista/dict vazios."""
    return valor is None or (isinstance(valor, str) and (not valor.strip() or valor.strip().lower().startswith(
        "[a definir"))) or (isinstance(valor, (list, dict)) and not valor)


def a_definir(valor, onde):
    """Valor do cliente (pessoa, canal, frase): devolve o valor, ou "[a definir]" com aviso no terminal (1 vez por
    campo). Nunca inventar — o script só diagrama."""
    if not vazio(valor):
        return valor
    if onde not in _AVISADOS:
        _AVISADOS.add(onde)
        print(f"  aviso: {onde} = {A_DEFINIR} (dado do cliente; preencher no brand.json)")
    return A_DEFINIR


# ------------------------------------------------------------------ forma: raios por papel (pesquisa 17a)
ARTE_POR_SITE = 2.75      # raio de arte 1080 ≈ 2,75 × raio de site (celular de 393 px CSS): o "10 das redes" = 28
SHAPE_STEPS = ("none", "sm", "md", "lg", "full")
PILL = 9999               # pílula = 9999 px (vira meia-altura); nunca 50% (num retângulo vira elipse)
CIRCLE_WORDS = {"circulo", "círculo", "circle", "ponto"}
# papel → (passo padrão, para quê). brand.json.shape.papeis sobrescreve e acrescenta (ex.: visor, relogio).
SHAPE_ROLES = {
    "button": ("md", "botão de ação do site — pílula OU a curva da família, nunca os dois na mesma hierarquia"),
    "field": ("sm", "campo de formulário — raio ≤ o do botão; nunca pílula em várias linhas"),
    "chip": ("full", "chip, filtro, rótulo de 1 linha com ≤ 3 palavras"),
    "live": ("full", "rótulo de status (AO VIVO, estado do evento)"),
    "card": ("md", "cartão que contém conteúdo; filho = pai − espaço"),
    "media": ("md", "foto solta em layout de app (0 se sangrada, tela cheia ou 'revista')"),
    "avatar": ("full", "pessoa = círculo (elemento quadrado)"),
    "modal": ("lg", "modal / folha (raio > o do cartão)"),
    "frame": ("lg", "moldura recuada / bloco grande"),
    "tarja": ("none", "tarja / faixa de texto: reta, como objeto impresso"),
    "progress": ("full", "barra de progresso (trilho e preenchimento)"),
    "section": ("none", "seção que encosta na borda da tela"),
    "divider": ("none", "fio, divisória, tabela, célula de grade"),
}
STEP_NAMES = {"none": "reto", "sm": "rótulo", "md": "cartão", "lg": "moldura", "full": "pílula"}


def _shape_px(v, table, art):
    """passo ('md'), número (px de SITE) ou palavra de círculo → px no meio pedido (site ou arte)."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return PILL if v >= PILL else (round(v * ARTE_POR_SITE) if art else v)
    s = str(v).lower()
    if s in CIRCLE_WORDS:
        return PILL
    return table.get(s, table.get("md", 0))


def shape_spec(brand):
    """brand.json.shape normalizado. Esquema novo (17a §8):
      {"escala": {"none":0,"sm":16,"md":28,"lg":44,"full":9999}   ← ARTE 1080
       "site":   {"none":0,"sm":6,"md":10,"lg":16,"full":9999}    ← px CSS (sem ele: arte ÷ 2,75)
       "papeis": {"card":"md", "tarja":"none", "button":"full", "avatar":"circulo",
                  "lower-third": {"passo":"md", "cantos":["md","md","md","none"], "nota":"…"}},
       "nunca_arredonda": ["logo", …], "combo": "A", "regra": "…", "status": "…"}
    Sem "escala"/"site" (marca antiga) → deriva de shape.radius (px de site) como antes: md = r, lg = 2r,
    sm = r/2. Devolve {arte, site, papeis{papel: {passo, site, arte, nota, cantos_site, cantos_arte, circulo,
    origem}}, nunca_arredonda, combo, regra, status, legado}. O papel "focus" = botão + afastamento do foco."""
    sh = brand.get("shape") or {}
    legado = not (sh.get("escala") or sh.get("site"))
    if legado:
        r = float(sh.get("radius", 0) or 0)
        site = {"none": 0, "sm": round(r / 2), "md": round(r), "lg": round(r * 2), "full": PILL}
        arte = {k: (PILL if k == "full" else round(v * ARTE_POR_SITE)) for k, v in site.items()}
    else:
        arte = {k: v for k, v in (sh.get("escala") or {}).items()}
        site = {k: v for k, v in (sh.get("site") or {}).items()}
        for k in SHAPE_STEPS:
            if k not in arte and k in site:
                arte[k] = PILL if k == "full" else round(site[k] * ARTE_POR_SITE)
            if k not in site and k in arte:
                site[k] = PILL if k == "full" else round(arte[k] / ARTE_POR_SITE)
        for t in (arte, site):
            t.setdefault("none", 0)
            t.setdefault("full", PILL)
            t.setdefault("md", t.get("sm", 0) or t.get("lg", 0))
            t.setdefault("sm", round(t["md"] * 0.57))
            t.setdefault("lg", round(t["md"] * 1.57))
    user = sh.get("papeis") or {}
    papeis = {}
    # ordem: os papéis da marca na ordem dela, depois os padrões que ela não citou
    for role in [k for k in user if k != "focus"] + [k for k in SHAPE_ROLES if k not in user]:
        v = user.get(role, SHAPE_ROLES.get(role, ("md", ""))[0])
        nota = SHAPE_ROLES.get(role, ("", ""))[1]
        cantos = None
        if isinstance(v, dict):
            nota = v.get("nota") or nota
            cantos = v.get("cantos")
            v = v.get("passo", v.get("raio", "none"))
        circ = isinstance(v, str) and v.lower() in CIRCLE_WORDS
        passo = "full" if circ else (v.lower() if isinstance(v, str) and v.lower() in site else None)
        papeis[slugify(role)] = {
            "passo": passo, "site": _shape_px(v, site, False), "arte": _shape_px(v, arte, True), "nota": nota,
            "cantos_site": [_shape_px(c, site, False) for c in cantos] if cantos else None,
            "cantos_arte": [_shape_px(c, arte, True) for c in cantos] if cantos else None,
            "circulo": circ, "origem": "marca" if role in user else "padrão"}
    acc = brand.get("accessibility") or {}
    off = ((acc.get("focus") or {}) if isinstance(acc, dict) else {}).get("offset", 2)
    bt = papeis["button"]
    papeis["focus"] = {"passo": "full" if bt["site"] >= PILL else None,
                       "site": PILL if bt["site"] >= PILL else bt["site"] + off,
                       "arte": PILL if bt["arte"] >= PILL else bt["arte"] + round(off * ARTE_POR_SITE),
                       "nota": f"anel de foco = raio do botão + {off} px (o afastamento do anel)", "cantos_site": None,
                       "cantos_arte": None, "circulo": False, "origem": "calculado"}
    return {"arte": {k: arte[k] for k in SHAPE_STEPS}, "site": {k: site[k] for k in SHAPE_STEPS}, "papeis": papeis,
            "nunca_arredonda": list(sh.get("nunca_arredonda") or []), "combo": sh.get("combo"),
            "regra": sh.get("regra") or sh.get("rule") or "", "status": sh.get("status") or "", "legado": legado,
            "foco_afastamento": off}


def never_round_labels(shp):
    """nunca_arredonda (ids de papel ou nomes) → nomes legíveis (a nota do papel até os dois-pontos)."""
    out = []
    for k in shp["nunca_arredonda"]:
        p = shp["papeis"].get(slugify(k))
        out.append(p["nota"].split(":")[0].strip() if p and p.get("nota") else k)
    return out


def nested_radius(r_pai, espaco, borda=0):
    """Conta do aninhado (17a §4.4): raio do filho = pai − (borda + espaço), nunca negativo. 0 = reto dentro de
    redondo, que é a conta certa (não erro)."""
    return max(0, r_pai - (borda + espaco))


# ------------------------------------------------------------------ cor: erro por fundo, daltonismo, ΔE2000 (17c)
ERROR_REDS = ["#B3261E", "#C5221F", "#FF8A80", "#FFB4AB"]   # padrão sem color.error (claro→escuro)


def error_on(bg, ink, cfg=None, surfaces=()):
    """Cor da mensagem de erro sobre bg → (cor, superfície ou None, nota).
    Com brand.json color.error {"escuro": "#FFB4AB", "papel": "#9E1B32"}: fundo escuro usa "escuro", claro usa
    "papel"; se nenhuma passa 4,5:1 (ex.: azul cheio), a mensagem vai numa TARJA (1ª superfície em que passa) —
    erro nunca é bloco cheio: fio 2 px + ✕ + "Erro:". Sem color.error: 1º vermelho padrão com ≥ 4,5:1, senão a tinta."""
    if cfg:
        dark = luminance(bg) < 0.18
        order = [x for x in ((cfg.get("escuro"), cfg.get("papel")) if dark else (cfg.get("papel"), cfg.get("escuro")))
                 if x]
        for c in order:
            if contrast(c, bg) >= 4.5:
                return c.upper(), None, f"erro {c.upper()} sobre {bg} {fmt_ratio(contrast(c, bg))}"
        for s in surfaces:
            for c in order:
                if contrast(c, s) >= 4.5:
                    return c.upper(), s.upper(), (f"nenhuma cor de erro passa 4,5:1 sobre {bg} → mensagem em tarja "
                                                  f"{s.upper()} ({c.upper()} {fmt_ratio(contrast(c, s))})")
        return ink, None, f"nenhuma cor de erro passa sobre {bg} → tinta + ícone ✕ + 'Erro:'"
    c = next((c for c in ERROR_REDS if contrast(c, bg) >= 4.5), ink)
    return c, None, (f"erro sobre bg {fmt_ratio(contrast(c, bg))}" + (
        " — nenhum vermelho passa 4,5:1 aqui: usa a tinta + ícone ✕" if c == ink else ""))


def focus_on(bg, accent, ink):
    """Cor do anel de foco: o destaque se tiver ≥ 3:1 sobre o fundo (WCAG 2.4.13 / 1.4.11), senão a tinta."""
    return accent if contrast(accent, bg) >= 3 else ink


MACHADO = {   # Machado, Oliveira & Fernandes 2009, severidade 1,0 — aplicar em RGB LINEAR
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}
VISOES = (("normal", "visão normal"), ("pb", "preto e branco"), ("deutan", "deuteranopia"), ("protan", "protanopia"))


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(v):
    v = min(1.0, max(0.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def simulate(hx, kind):
    """Cor como é vista: 'normal', 'pb' (mesma luminância, cinza), 'protan', 'deutan', 'tritan' (Machado 2009)."""
    if kind in (None, "normal"):
        return hx.upper()
    lin = [_lin(c) for c in hex_to_rgb(hx)]
    if kind == "pb":
        y = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
        out = [_gam(y)] * 3
    else:
        m = MACHADO[kind]
        out = [_gam(sum(m[i][j] * lin[j] for j in range(3))) for i in range(3)]
    return rgb_to_hex([c * 255 for c in out])


def svg_cvd_filters():
    """<svg> com filtros feColorMatrix (RGB linear) para mostrar a MESMA página como é vista: #cvd-pb, #cvd-deutan,
    #cvd-protan, #cvd-tritan (usar com CSS filter:url(#cvd-deutan))."""
    def vals(m):
        return " ".join(f"{m[i][0]:g} {m[i][1]:g} {m[i][2]:g} 0 0" for i in range(3)) + " 0 0 0 1 0"
    pb = ((0.2126, 0.7152, 0.0722),) * 3
    fs = "".join(f'<filter id="cvd-{k}" color-interpolation-filters="linearRGB"><feColorMatrix type="matrix" '
                 f'values="{vals(m)}"/></filter>' for k, m in (("pb", pb), *MACHADO.items()))
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{fs}</svg>'


def _lab(hx):
    r, g, b = (_lin(c) for c in hex_to_rgb(hx))
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116  # noqa: E731
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(h1, h2):
    """ΔE2000 entre duas cores HEX (≈ 2,3 = mínimo que se nota; > 10 = claramente diferentes; > 20 = categorias
    distintas — limiares de ponto de partida, 17c §2.4)."""
    L1, a1, b1 = _lab(h1)
    L2, a2, b2 = _lab(h2)
    cb = (math.hypot(a1, b1) + math.hypot(a2, b2)) / 2
    g = 0.5 * (1 - math.sqrt(cb ** 7 / (cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dl, dc = L2 - L1, c2p - c1p
    d = h2p - h1p
    dh = 0 if c1p * c2p == 0 else (d - 360 if d > 180 else d + 360 if d < -180 else d)
    dH = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dh / 2))
    lb, cbp = (L1 + L2) / 2, (c1p + c2p) / 2
    if c1p * c2p == 0:
        hb = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hb = (h1p + h2p) / 2
    else:
        hb = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    t = (1 - 0.17 * math.cos(math.radians(hb - 30)) + 0.24 * math.cos(math.radians(2 * hb))
         + 0.32 * math.cos(math.radians(3 * hb + 6)) - 0.20 * math.cos(math.radians(4 * hb - 63)))
    dth = 30 * math.exp(-((hb - 275) / 25) ** 2)
    rc = 2 * math.sqrt(cbp ** 7 / (cbp ** 7 + 25 ** 7))
    sl = 1 + 0.015 * (lb - 50) ** 2 / math.sqrt(20 + (lb - 50) ** 2)
    sc, shh = 1 + 0.045 * cbp, 1 + 0.015 * cbp * t
    rt = -math.sin(math.radians(2 * dth)) * rc
    return math.sqrt((dl / sl) ** 2 + (dc / sc) ** 2 + (dH / shh) ** 2 + rt * (dc / sc) * (dH / shh))


def color_tree(brand):
    """Árvore "qual cor usar?" → [(pergunta, resposta, hex ou None)]. brand.json architecture.qual_cor
    ([{"se": …, "entao": …, "cor": "#…" ou id de produto}]) manda; sem ela, monta das regras estruturais (17c §6
    regra 4): um produto → a cor dele; mais de um / a marca toda → a cor do produto-mãe (architecture.produto_mae)
    ou a cor da marca; mensagem de sistema → cor de status, nunca cor de produto."""
    prods = products(brand)
    if not prods:
        return []
    arch = brand.get("architecture") or {}
    by_id = {p["id"]: p for p in prods}
    user = arch.get("qual_cor") or []
    if user:
        out = []
        for r in user:
            if isinstance(r, dict):
                c = r.get("cor")
                c = by_id[c]["colors"]["accent"] if c in by_id else c
                out.append((r.get("se", ""), r.get("entao", ""), c if isinstance(c, str) and c.startswith("#") else None))
        return out
    mae = by_id.get(arch.get("produto_mae") or "")
    # mensagem de sistema vem primeiro: um erro na página de um produto continua sendo erro, não a cor do produto
    out = [("É mensagem de sistema (erro, aviso, sucesso no site ou formulário)?",
            "cor de status (--color-error), nunca a cor de um produto", None)]
    for p in prods:
        if p is mae:
            continue
        nome = p.get("color_name") or p.get("tag") or p["name"]
        out.append((f"A peça fala só de {p.get('label') or p['name']}?", f"{nome} {p['colors']['accent']}",
                    p["colors"]["accent"]))
    if mae:
        out.append(("Fala de mais de um produto, da oferta ou da marca inteira?",
                    f"{mae.get('color_name') or mae.get('tag') or mae['name']} {mae['colors']['accent']}",
                    mae["colors"]["accent"]))
    else:
        out.append(("Fala de mais de um produto ou da marca inteira?", f"cor da marca {brand.colour('brand')}",
                    brand.colour("brand")))
    for r in arch.get("qual_cor_extra") or []:   # perguntas a mais da marca, depois das automáticas
        if isinstance(r, dict):
            out.append((r.get("se", ""), r.get("entao", ""), r.get("cor") if str(r.get("cor", "")).startswith("#") else None))
    return out


def color_pairs_cvd(colors, limite=10.0):
    """Todos os pares de {nome: hex} em cada visão → [{a, b, ha, hb, normal, deutan, protan, tritan, luz,
    confunde: [visões]}]. 'confunde' = ΔE2000 < limite (10 = ponto de partida 17c); 'pb' entra quando o contraste
    entre as duas < 1,5:1 (em P&B viram o mesmo cinza → exigir rótulo escrito)."""
    import itertools
    out = []
    for (na, a), (nb, b) in itertools.combinations(colors.items(), 2):
        row = {"a": na, "b": nb, "ha": a, "hb": b}
        for k in ("normal", "deutan", "protan", "tritan"):
            row[k] = round(delta_e(simulate(a, k), simulate(b, k)), 1)
        row["luz"] = round(contrast(a, b), 2)
        row["confunde"] = [k for k in ("normal", "deutan", "protan", "tritan") if row[k] < limite]
        if row["luz"] < 1.5:
            row["confunde"].append("pb")
        out.append(row)
    return out
