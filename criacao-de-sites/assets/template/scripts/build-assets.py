#!/usr/bin/env python
"""Gera os ativos DA MARCA do site a partir de `content/marca.json` (uma só fonte de cores, fontes, forma e logo).

  fontes   woff2 em subconjunto Latin/PT-BR            -> app/fonts/*.woff2  +  app/fonts.ts
  tokens   cores, fontes, raios, grão (@theme)         -> styles/tokens.css
  logos    SVG em assets-src/logos/                    -> lib/logos.generated.ts  +  public/logos/*.svg
  grao     tile de granulado 128 px                    -> public/img/grao-128.png
  og       og.png 1200x630 + apple-icon + icon.svg     -> public/og.png, app/apple-icon.png, app/icon.svg
  licencas OFL das fontes usadas                       -> public/licencas/

Uso:  python scripts/build-assets.py [--so fontes,tokens,logos,grao,og] [--fonts-dir <pasta com as TTF>]
Requer: fonttools, brotli, pillow, numpy, resvg-py (já instalados no estúdio).
Fontes: procura em ~/.cache/brand-studio/fonts/<familia>/ (ou BRAND_FONTS_DIR); se faltar, baixa com
`brand-studio/scripts/fonts.py get "Familia:peso"`.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS_CACHE = Path(os.environ.get("BRAND_FONTS_DIR") or Path.home() / ".cache" / "brand-studio" / "fonts")

# Latin básico + Latin-1 (acentos do português) + pontuação tipográfica + setas.
UNICODES = (
    list(range(0x20, 0x7F))
    + list(range(0xA0, 0x100))
    + [0x131, 0x152, 0x153, 0x2C6, 0x2DA, 0x2DC]
    + [0x2013, 0x2014, 0x2018, 0x2019, 0x201A, 0x201C, 0x201D, 0x201E, 0x2022, 0x2026, 0x2030, 0x2039, 0x203A]
    + [0x20AC, 0x2122, 0x2190, 0x2191, 0x2192, 0x2193, 0x2212]
)
FEATURES = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "tnum", "lnum", "pnum", "case", "zero"]

DEFAULT_MARCA = {
    "nome": "Marca Exemplo",
    "slug": "marca-exemplo",
    "cores": {
        "ink": "#111315",
        "ink2": "#1a1d20",
        "tinta": "#fbfaf7",
        "papel": "#efece4",
        "destaque": "#ff5a1f",
        "sobre_destaque": "#111315",
        "acento": "#3b6cff",
        "mute": "#c9c6bd",
    },
    "fontes": {
        "display": {"familia": "Big Shoulders", "peso": 900, "caixa": "alta"},
        "texto": {"familia": "Archivo", "pesos": [500, 800]},
        "mono": {"familia": "Azeret Mono", "pesos": [500, 600]},
    },
    "forma": {"sinal": 0, "rotulo": 6, "cartao": 10, "moldura": 16},
    "grao": 0.55,
    "logo": {"principal": "logo", "simbolo": "logo-simbolo", "cor_arquivo": "tinta"},
}


# ----------------------------------------------------------------------------------------------- util
def load_marca() -> dict:
    p = ROOT / "content" / "marca.json"
    if not p.exists():
        return json.loads(json.dumps(DEFAULT_MARCA))
    m = json.loads(p.read_text(encoding="utf-8"))
    out = json.loads(json.dumps(DEFAULT_MARCA))
    for k, v in m.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    if m.get("fontes", {}).get("mono", "x") is None:
        out["fontes"]["mono"] = None
    return out


def slug_dir(family: str) -> str:
    return re.sub(r"[^a-z0-9]", "", family.lower())


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def baixar_fonte(family: str, peso: int) -> None:
    for base in (
        Path(__file__).resolve().parents[min(4, len(Path(__file__).resolve().parents) - 1)] / "brand-studio" / "scripts" / "fonts.py",
        Path.home() / ".claude" / "skills" / "brand-studio" / "scripts" / "fonts.py",
    ):
        if base.exists():
            print(f"  baixando {family}:{peso} com {base.name}")
            subprocess.run([sys.executable, str(base), "get", f"{family}:{peso}"], check=False, timeout=240)
            return


def achar_fonte(family: str, peso: int) -> tuple[str, Path] | None:
    """('estatica'|'variavel', arquivo) ou None."""
    d = FONTS_CACHE / slug_dir(family)
    for tentativa in range(2):
        if d.is_dir():
            for f in d.iterdir():
                if f.suffix.lower() == ".ttf" and f.name.lower() == f"{slug_dir(family)}-{peso}.ttf":
                    return "estatica", f
            for f in d.iterdir():
                if f.suffix.lower() == ".ttf" and "[" in f.name:
                    return "variavel", f
        if tentativa == 0:
            baixar_fonte(family, peso)
    return None


def to_woff2(font, out: Path) -> None:
    from fontTools import subset

    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = FEATURES
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
    opts.notdef_outline = True
    opts.hinting = False
    opts.desubroutinize = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    out.parent.mkdir(parents=True, exist_ok=True)
    font.flavor = "woff2"
    font.save(str(out))
    print(f"  {rel(out)}  {out.stat().st_size / 1024:.1f} KB")


def instanciar(path: Path, peso: int | tuple[int, int]):
    """Abre a TTF; se for variável, fixa wght (valor ou faixa) e wdth=100."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    f = TTFont(str(path))
    if "fvar" not in f:
        return f
    eixos = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in f["fvar"].axes}
    lim: dict = {}
    if "wght" in eixos:
        lo, _, hi = eixos["wght"]
        if isinstance(peso, tuple):
            lim["wght"] = (max(lo, peso[0]), min(hi, peso[1]))
        else:
            lim["wght"] = max(lo, min(hi, peso))
    for tag, (mn, df, mx) in eixos.items():
        if tag == "wght":
            continue
        lim[tag] = df if tag != "wdth" else max(mn, min(mx, 100))
    return instancer.instantiateVariableFont(f, lim)


def ttf_estatica(family: str, peso: int) -> Path | None:
    """TTF de um peso (para o OG): estática do cache ou instância gerada em pasta temporária."""
    r = achar_fonte(family, peso)
    if not r:
        return None
    tipo, p = r
    if tipo == "estatica":
        return p
    tmp = Path(tempfile.gettempdir()) / "site-fontes"
    tmp.mkdir(exist_ok=True)
    out = tmp / f"{slug_dir(family)}-{peso}.ttf"
    if not out.exists():
        instanciar(p, peso).save(str(out))
    return out


# ----------------------------------------------------------------------------------------------- fontes
def build_fontes(marca: dict) -> dict:
    print("fontes")
    out = ROOT / "app" / "fonts"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.woff2"):
        old.unlink()
    f = marca["fontes"]
    info: dict = {"display": None, "texto": None, "mono": None}
    usadas: list[str] = []

    d = f["display"]
    r = achar_fonte(d["familia"], int(d["peso"]))
    if not r:
        raise SystemExit(f"fonte não encontrada: {d['familia']} {d['peso']}")
    to_woff2(instanciar(r[1], int(d["peso"])), out / "display.woff2")
    info["display"] = {"arquivo": "display.woff2", "peso": int(d["peso"])}
    usadas.append(d["familia"])

    t = f["texto"]
    pesos = sorted(int(x) for x in t.get("pesos", [400, 700]))
    r = achar_fonte(t["familia"], pesos[0])
    if not r:
        raise SystemExit(f"fonte não encontrada: {t['familia']}")
    if len(pesos) >= 3 and r[0] == "estatica":
        d_ = FONTS_CACHE / slug_dir(t["familia"])
        var = next((f for f in d_.iterdir() if f.suffix.lower() == ".ttf" and "[" in f.name), None) if d_.is_dir() else None
        if var:
            r = ("variavel", var)
    feito = False
    if r[0] == "variavel":
        lo, hi = pesos[0], pesos[-1]
        try:
            to_woff2(instanciar(r[1], (lo, hi)), out / "texto.woff2")
            info["texto"] = {"arquivos": [{"arquivo": "texto.woff2", "peso": f"{lo} {hi}"}]}
            feito = True
        except Exception as e:  # noqa: BLE001 — algumas variáveis falham no subset da faixa (.notdef): usa instâncias fixas
            print(f"  aviso: faixa variável de {t['familia']} não subsetou ({type(e).__name__}); usando pesos fixos")
            (out / "texto.woff2").unlink(missing_ok=True)
    if not feito:
        arqs = []
        for w in pesos:
            rr = achar_fonte(t["familia"], w)
            if not rr:
                raise SystemExit(f"peso {w} não encontrado: {t['familia']}")
            to_woff2(instanciar(rr[1], w), out / f"texto-{w}.woff2")
            arqs.append({"arquivo": f"texto-{w}.woff2", "peso": str(w)})
        info["texto"] = {"arquivos": arqs}
    usadas.append(t["familia"])

    m = f.get("mono")
    if m:
        arqs = []
        for w in sorted(int(x) for x in m.get("pesos", [500])):
            rr = achar_fonte(m["familia"], w)
            if not rr:
                print(f"  aviso: {m['familia']} {w} não encontrada; mono ignorada")
                arqs = []
                break
            to_woff2(instanciar(rr[1], w), out / f"mono-{w}.woff2")
            arqs.append({"arquivo": f"mono-{w}.woff2", "peso": str(w)})
        if arqs:
            info["mono"] = {"arquivos": arqs}
            usadas.append(m["familia"])

    # fonts.ts
    L = [
        "/**",
        " * Fontes da marca, locais (nada de Google Fonts em tempo de execução), woff2 em subconjunto Latin/PT-BR.",
        " * ARQUIVO GERADO por scripts/build-assets.py a partir de content/marca.json — não editar à mão",
        f" *   display  {d['familia']} {d['peso']}",
        f" *   text     {t['familia']} {'/'.join(str(p) for p in pesos)}",
        f" *   mono     {m['familia'] if info['mono'] else '(sem mono: usa a fonte de texto)'}",
        " * next/font/local gera @font-face com `font-display: swap`, preload e fonte-reserva com métricas ajustadas.",
        " */",
        "import localFont from 'next/font/local'",
        "",
        "export const display = localFont({",
        "  src: './fonts/display.woff2',",
        f"  weight: '{d['peso']}',",
        "  style: 'normal',",
        "  display: 'swap',",
        "  variable: '--font-display-next',",
        "  fallback: ['system-ui', 'sans-serif'],",
        "})",
        "",
    ]

    def src_list(arqs):
        if len(arqs) == 1:
            return f"'./fonts/{arqs[0]['arquivo']}'"
        itens = ", ".join(f"{{ path: './fonts/{a['arquivo']}', weight: '{a['peso']}', style: 'normal' }}" for a in arqs)
        return f"[{itens}]"

    ta = info["texto"]["arquivos"]
    L += ["export const text = localFont({", f"  src: {src_list(ta)},"]
    if len(ta) == 1:
        L.append(f"  weight: '{ta[0]['peso']}',")
        L.append("  style: 'normal',")
    L += [
        "  display: 'swap',",
        "  variable: '--font-text-next',",
        "  fallback: ['system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],",
        "})",
        "",
    ]
    if info["mono"]:
        ma = info["mono"]["arquivos"]
        L += ["export const mono = localFont({", f"  src: {src_list(ma)},"]
        if len(ma) == 1:
            L.append(f"  weight: '{ma[0]['peso']}',")
            L.append("  style: 'normal',")
        L += [
            "  display: 'swap',",
            "  variable: '--font-mono-next',",
            "  preload: false,",
            "  fallback: ['ui-monospace', 'Consolas', 'monospace'],",
            "})",
            "",
            "/** Classes das 3 variáveis para o <html>. */",
            "export const fontVariables = `${display.variable} ${text.variable} ${mono.variable}`",
        ]
    else:
        L += ["/** Classes das variáveis para o <html> (sem mono). */", "export const fontVariables = `${display.variable} ${text.variable}`"]
    (ROOT / "app" / "fonts.ts").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("  app/fonts.ts")

    # licenças
    lic = ROOT / "public" / "licencas"
    lic.mkdir(parents=True, exist_ok=True)
    for old in lic.glob("OFL-*.txt"):
        old.unlink()
    for fam in usadas:
        src = FONTS_CACHE / slug_dir(fam) / "OFL.txt"
        if src.exists():
            shutil.copy2(src, lic / f"OFL-{slug_dir(fam)}.txt")
    return info


# ----------------------------------------------------------------------------------------------- tokens
def build_tokens(marca: dict, fontes_info: dict | None) -> None:
    print("tokens")
    c = marca["cores"]
    fm = marca["forma"]
    tem_mono = bool(marca["fontes"].get("mono")) and (fontes_info is None or fontes_info.get("mono") is not None)
    if fontes_info is None:
        tem_mono = bool(marca["fontes"].get("mono")) and any((ROOT / "app" / "fonts").glob("mono-*.woff2"))
    mono_stack = (
        "var(--font-mono-next), ui-monospace, Consolas, monospace"
        if tem_mono
        else "var(--font-text-next), ui-monospace, Consolas, monospace"
    )
    caixa = marca["fontes"]["display"].get("caixa", "alta")
    css = f"""/* ARQUIVO GERADO por scripts/build-assets.py a partir de content/marca.json — não editar à mão.
   Marca: {marca.get('nome', '')}. Para mudar cores, fontes ou raios: edite content/marca.json e rode `npm run assets`. */
@theme static {{
  /* cores (texto pequeno só em tinta/papel/ink; destaque = fundo de ação, tarja, disco) */
  --color-*: initial;
  --color-ink: {c['ink']}; /* fundo escuro */
  --color-ink-2: {c['ink2']}; /* superfície 2 (cartões, modal) */
  --color-tinta: {c['tinta']}; /* texto no escuro */
  --color-papel: {c['papel']}; /* fundo claro */
  --color-destaque: {c['destaque']}; /* ação primária, disco, tarja */
  --color-sobre-destaque: {c['sobre_destaque']}; /* texto sobre o destaque */
  --color-acento: {c['acento']}; /* 2ª cor: só áreas grandes */
  --color-mute: {c['mute']}; /* texto de apoio sobre ink */
  --color-erro: #ffb4ab;
  --color-erro-papel: #9e1b32;

  --font-display: var(--font-display-next), system-ui, sans-serif;
  --font-sans: var(--font-text-next), system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono: {mono_stack};

  /* raios (forma): sinal = peça de destaque com função; os outros = conteúdo. O logo nunca arredonda. */
  --radius-*: initial;
  --radius-sinal: {fm['sinal']}px;
  --radius-rotulo: {fm['rotulo']}px;
  --radius-cartao: {fm['cartao']}px;
  --radius-moldura: {fm['moldura']}px;
  --radius-pilula: 9999px;
}}
:root {{
  --grao-op: {marca.get('grao', 0.55)};
  --display-peso: {marca['fontes']['display']['peso']};
  --texto-peso: {min(int(x) for x in marca['fontes']['texto'].get('pesos', [400]))};
  --display-caixa: {'uppercase' if caixa == 'alta' else 'none'};
}}
"""
    (ROOT / "styles").mkdir(exist_ok=True)
    (ROOT / "styles" / "tokens.css").write_text(css, encoding="utf-8")
    print("  styles/tokens.css")


# ----------------------------------------------------------------------------------------------- logos
def _round_nums(s: str) -> str:
    def r(m):
        t = f"{float(m.group(0)):.2f}".rstrip("0").rstrip(".")
        return "0" if t in ("-0", "") else t

    return re.sub(r"-?\d+\.\d{3,}", r, s)


def parse_logo(svg: str) -> dict:
    s = re.sub(r"<\?xml[^>]*\?>", "", svg)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<title>.*?</title>|<desc>.*?</desc>", "", s, flags=re.S)
    m = re.search(r"<svg\b([^>]*)>", s, flags=re.S)
    if not m:
        raise ValueError("SVG sem <svg>")
    attrs = m.group(1)
    vb = re.search(r'viewBox="([^"]+)"', attrs)
    if vb:
        viewbox = " ".join(vb.group(1).replace(",", " ").split())
    else:
        w = re.search(r'width="([\d.]+)', attrs)
        h = re.search(r'height="([\d.]+)', attrs)
        if not (w and h):
            raise ValueError("SVG sem viewBox nem width/height")
        viewbox = f"0 0 {w.group(1)} {h.group(1)}"
    inner = s[m.end():]
    inner = inner[: inner.rfind("</svg>")]
    inner = re.sub(r"\s+", " ", inner).strip()
    inner = re.sub(r">\s+<", "><", inner)
    if "url(#" not in inner:
        inner = re.sub(r'\s(id|data-name)="[^"]*"', "", inner)
    inner = _round_nums(inner)
    # cores
    cores = set()
    for mm in re.finditer(r'\b(fill|stroke)="([^"]+)"', inner):
        v = mm.group(2).strip().lower()
        if v not in ("none", "currentcolor", "inherit", "transparent") and not v.startswith("url("):
            cores.add(v)
    for mm in re.finditer(r"style=\"([^\"]*)\"", inner):
        for km in re.finditer(r"(?:fill|stroke)\s*:\s*([^;]+)", mm.group(1)):
            v = km.group(1).strip().lower()
            if v not in ("none", "currentcolor", "inherit", "transparent") and not v.startswith("url("):
                cores.add(v)
    mono = len(cores) <= 1 and "<style" not in inner and "<linearGradient" not in inner and "<radialGradient" not in inner
    if mono and cores:
        inner = re.sub(r'\s(fill|stroke)="(?!none|currentColor)[^"]*"', lambda mo: f' {mo.group(1)}="currentColor"' if mo.group(1) == "stroke" else "", inner)
        inner = re.sub(r"(fill|stroke)\s*:\s*(?!none)[^;\"]+;?", "", inner)
    nums = [float(x) for x in viewbox.split()]
    return {"viewBox": viewbox, "w": round(nums[2], 2), "h": round(nums[3], 2), "inner": inner, "mono": mono}


def build_logos(marca: dict) -> dict:
    print("logos")
    src = ROOT / "assets-src" / "logos"
    out = ROOT / "public" / "logos"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    cor_arq = marca["cores"].get(marca.get("logo", {}).get("cor_arquivo", "tinta"), marca["cores"]["tinta"])
    tabela: dict = {}
    for f in sorted(src.glob("*.svg")) if src.exists() else []:
        try:
            lg = parse_logo(f.read_text(encoding="utf-8"))
        except ValueError as e:
            print(f"  {f.name}: {e}")
            continue
        key = f.stem
        tabela[key] = lg
        fill = f' fill="{cor_arq}"' if lg["mono"] else ""
        (out / f.name).write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{lg["viewBox"]}"{fill}>{lg["inner"]}</svg>', encoding="utf-8"
        )
        print(f"  {f.name:34s} {f.stat().st_size / 1024:.1f} KB -> {len(lg['inner']) / 1024:.1f} KB  {'monocromática' if lg['mono'] else 'multicor'}")
    header = (
        "// ARQUIVO GERADO por scripts/build-assets.py — não editar à mão.\n"
        "// Fonte: assets-src/logos/*.svg (monocromáticas viram currentColor; multicolores mantêm as cores).\n"
    )
    body = f"export const LOGOS = {json.dumps(tabela, indent=1, ensure_ascii=False)} as const\nexport type LogoKey = keyof typeof LOGOS\n"
    (ROOT / "lib").mkdir(exist_ok=True)
    (ROOT / "lib" / "logos.generated.ts").write_text(header + body, encoding="utf-8")
    print(f"  lib/logos.generated.ts  {(len(header) + len(body)) / 1024:.1f} KB")
    return tabela


# ----------------------------------------------------------------------------------------------- grão, og
def build_grao() -> None:
    import numpy as np
    from PIL import Image

    print("granulado")
    rng = np.random.default_rng(1109)
    n = 128
    alpha = (rng.random((n, n)) ** 2.2 * 40).astype(np.uint8)
    light = rng.random((n, n)) > 0.5
    lum = np.where(light, 255, 0).astype(np.uint8)
    img = Image.fromarray(np.dstack([lum, lum, lum, alpha]), "RGBA")
    out = ROOT / "public" / "img" / "grao-128.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    print(f"  {rel(out)}  {out.stat().st_size / 1024:.1f} KB")


def _hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _lum(h: str) -> float:
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = _hex_rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contraste(a: str, b: str) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _svg_cor(lg: dict, cor: str) -> str:
    fill = f' fill="{cor}"' if lg["mono"] else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{lg["viewBox"]}"{fill}>{lg["inner"]}</svg>'


def _render(svg: str, largura: int, fundo: str):
    import resvg_py
    from PIL import Image

    data = resvg_py.svg_to_bytes(svg_string=svg, width=largura, background=fundo)
    return Image.open(io.BytesIO(bytes(data))).convert("RGBA")


def _titulo_h1() -> str:
    try:
        copy = json.loads((ROOT / "content" / "copy.json").read_text(encoding="utf-8"))
        return str(copy.get("hero", {}).get("h1", "")).strip()
    except Exception:
        return ""


def build_og(marca: dict, tabela: dict) -> None:
    from PIL import Image, ImageDraw, ImageFont

    print("og + ícones")
    c = marca["cores"]
    ink = _hex_rgb(c["ink"])
    W, H = 1200, 630
    og = Image.new("RGBA", (W, H), ink + (255,))
    lcfg = marca.get("logo", {})
    principal = tabela.get(lcfg.get("principal", "logo"))
    simbolo = tabela.get(lcfg.get("simbolo", "logo-simbolo")) or principal
    if principal:
        alvo_h = 150
        larg = min(880, int(alvo_h * principal["w"] / principal["h"]))
        lg = _render(_svg_cor(principal, c["tinta"]), larg, c["ink"])
        og.alpha_composite(lg, (80, 84))
    d = ImageDraw.Draw(og)
    d.rectangle([80, 396, 1120, 398], fill=_hex_rgb(c["destaque"]) + (255,))
    titulo = _titulo_h1() or marca.get("nome", "")
    disp = marca["fontes"]["display"]
    ttf = ttf_estatica(disp["familia"], int(disp["peso"]))
    if disp.get("caixa", "alta") == "alta":
        titulo = titulo.upper()
    if ttf and titulo:
        for size in (88, 76, 64, 54, 46):
            fnt = ImageFont.truetype(str(ttf), size)
            linhas, atual = [], ""
            for w in titulo.split():
                t = (atual + " " + w).strip()
                if fnt.getlength(t) <= 1040 or not atual:
                    atual = t
                else:
                    linhas.append(atual)
                    atual = w
            linhas.append(atual)
            if len(linhas) <= 2:
                break
        y = 420
        for ln in linhas[:2]:
            d.text((80, y), ln, font=fnt, fill=_hex_rgb(c["tinta"]) + (255,))
            y += int(size * 1.08)
    (ROOT / "public").mkdir(exist_ok=True)
    og.convert("RGB").save(ROOT / "public" / "og.png", optimize=True)
    print(f"  public/og.png  {(ROOT / 'public' / 'og.png').stat().st_size / 1024:.1f} KB")

    cor_simbolo = c["destaque"] if contraste(c["destaque"], c["ink"]) >= 3 else c["tinta"]
    icon = Image.new("RGBA", (180, 180), ink + (255,))
    if simbolo:
        s = _render(_svg_cor(simbolo, cor_simbolo), 120 if simbolo["w"] >= simbolo["h"] else int(120 * simbolo["w"] / simbolo["h"]), c["ink"])
        if s.height > 120:
            s = s.resize((int(s.width * 120 / s.height), 120))
        icon.alpha_composite(s, ((180 - s.width) // 2, (180 - s.height) // 2))
        (ROOT / "app" / "icon.svg").write_text(_svg_cor(simbolo, cor_simbolo), encoding="utf-8")
    icon.convert("RGB").save(ROOT / "app" / "apple-icon.png", optimize=True)
    print("  app/apple-icon.png · app/icon.svg")


# ----------------------------------------------------------------------------------------------- main
def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--so", default="fontes,tokens,logos,grao,og", help="etapas separadas por vírgula")
    ap.add_argument("--fonts-dir", type=Path, default=None)
    a = ap.parse_args()
    global FONTS_CACHE
    if a.fonts_dir:
        FONTS_CACHE = a.fonts_dir
    etapas = {x.strip() for x in a.so.split(",")}
    marca = load_marca()
    info = None
    if "fontes" in etapas:
        info = build_fontes(marca)
    if "tokens" in etapas:
        build_tokens(marca, info)
    tabela = None
    if "logos" in etapas:
        tabela = build_logos(marca)
    if "grao" in etapas:
        build_grao()
    if "og" in etapas:
        if tabela is None:
            tabela = build_logos(marca)
        build_og(marca, tabela)
    return 0


if __name__ == "__main__":
    sys.exit(main())
