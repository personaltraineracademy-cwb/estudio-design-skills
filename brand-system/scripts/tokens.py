"""Design tokens: brand.json → DTCG 2025.10 (core + light/dark [+ produtos]) → CSS variables, Tailwind v4 @theme,
Figma import files, a DESIGN.md that any AI/dev tool can read to stay on-brand, and a component demo page.

Usage:
  python tokens.py build <brand_dir> [--no-png]
     → tokens/{core,light,dark}.tokens.json, tokens.css, tailwind.css, figma/{light,dark}.tokens.json, ../DESIGN.md,
       tokens/demo.html + tokens/demo.png e tokens/demo/NN-<bloco>.png (Chrome)
     com brand.json "products" (sub-identidades por cor), também:
       tokens/products.tokens.json (DTCG, um grupo por produto: bg, ink, accent, on-accent, error, live, focus
       [+ alt]), blocos [data-produto="<id>"] (+ [data-variante="alt"]) no tokens.css com o contraste WCAG comentado,
       figma/produto-<id>[-alt].tokens.json (um modo por produto), seção "Produtos" no DESIGN.md (com a árvore
       "qual cor?"), um bloco de componentes por produto na demo e a faixa "lado a lado" em P&B e com daltonismo —
       e avisa no terminal os pares que falham.
Run palette.py build and typesys.py build first (ramps, roles and type levels come from them).
Figma: right-click a variable mode → Import mode → pick figma/<mode>.tokens.json (px only, seconds, single family).

Cores de CONTEXTO (o que os componentes usam): --color-bg, --color-ink, --color-accent, --color-on-accent,
--color-error (+ --color-error-surface/-line), --color-live (ponto ao vivo), --color-focus (= --focus-ring-color).
Na marca-mãe = papéis do modo; cada produto troca todas.
FORMA (pesquisa 17a): primitivos radius-none/sm/md/lg/full (valor de SITE; o de ARTE 1080 vai em $extensions e no
bloco [data-meio="arte"]) + PAPÉIS radius-button/field/chip/live/card/media/avatar/modal/frame/tarja/… (+ os da
marca, ex.: visor, relogio) + radius-focus (= botão + afastamento). Componente usa SÓ papel.
Interface (pesquisa 17b): focus-ring-width/offset/color, target-min (48), state-hover 8 % / state-pressed 10 %,
opacity-disabled, breakpoint-*, container-*, motion-easing-produtivo (Carbon/IBM) ao lado do expressivo da marca.
Demo: botão × 7 estados, campo × 5 estados, estado do evento × 5 (brand.json demo.estados), forma, lado a lado
(normal · P&B · deutan · protan) e rodapé com os canais oficiais (brand.json official; sem dado → [a definir]).
"""
import argparse
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import (A_DEFINIR, ARTE_POR_SITE, PILL, STEP_NAMES, a_definir, brand_font_faces,  # noqa: E402
                   color_pairs_cvd, contrast, error_on, fmt_ratio, focus_on, hex_to_rgb, load_brand, luminance,
                   never_round_labels, product_pairs, products, shape_spec, svg_cvd_filters, text_width, vazio,
                   write)

SPACE = [0, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128]
E = html.escape
EXT = "br.brand-system"
# curvas (pesquisa 17b, E): o par PRODUTIVO (tarefa, interface) da Carbon/IBM ao lado do EXPRESSIVO da marca
PRODUTIVO = [0.2, 0, 0.38, 0.9]
PRODUTIVO_NOTA = ("produtivo — tarefas de interface (abrir menu, validar campo). Origem: IBM Carbon, "
                  "'standard productive' cubic-bezier(0.2, 0, 0.38, 0.9)")
# grade de SITE (direcao-de-arte/references/site.md): celular 390, tablet 768, desktop 1440; contêiner 1200–1320
WEB = {"breakpoints": {"mobile": 390, "tablet": 768, "desktop": 1440},
       "container": {"max": 1200, "wide": 1320, "margin-mobile": 20, "margin-desktop": 120},
       "columns": {"mobile": 4, "tablet": 8, "desktop": 12}}
STATE = {"hover": 0.08, "pressed": 0.10}      # camada da cor do texto por cima (Material: hover 8 %, pressionado 10 %)
OPACITY_DISABLED = 0.38
# estados do evento (17b H) — rótulos GENÉRICOS de interface; brand.json demo.estados sobrescreve por id
EVENT_STATES = [
    {"id": "em-breve", "chip": "Em breve", "valor": "em 3 dias", "texto": "faltam 3 dias", "acao": "Lembrar"},
    {"id": "hoje", "chip": "Hoje", "valor": "{hora}", "texto": "hoje às {hora}", "acao": "Lembrar"},
    {"id": "ao-vivo", "chip": "Ao vivo agora", "valor": "agora", "texto": "acontecendo agora", "acao": "Assistir"},
    {"id": "encerrado", "chip": "Encerrado", "valor": "encerrado", "texto": "a transmissão terminou", "acao": ""},
    {"id": "replay", "chip": "Replay", "valor": "replay", "texto": "gravação disponível", "acao": "Ver replay"},
]


def col(hx):
    r, g, b = (c / 255 for c in hex_to_rgb(hx))
    return {"colorSpace": "srgb", "components": [round(r, 4), round(g, 4), round(b, 4)], "hex": hx.lower()}


def dim(v, unit="px"):
    return {"value": v, "unit": unit}


def access(b):
    """Foco, alvo mínimo (brand.json accessibility; padrão: anel 3 px a 2 px, alvo 48 px)."""
    a = b.get("accessibility") or {}
    f = a.get("focus") or {}
    return {"width": f.get("width", 3), "offset": f.get("offset", 2), "target": a.get("target_min", 48)}


def web(b):
    w = (b.get("grid") or {}).get("web") or {}
    return {k: {**WEB[k], **(w.get(k) or {})} for k in WEB}


def error_cfg(b):
    e = b.get("color.error")
    return e if isinstance(e, dict) and (e.get("escuro") or e.get("papel")) else None


def ctx_colors(b, c, extra=()):
    """Cores derivadas de um contexto {bg, ink, accent, on_accent[, live]}: erro (+ tarja e fio), foco, live e o
    corpo mínimo do texto do botão (≥ 18,7 px negrito quando o par do botão fica entre 3 e 4,5:1)."""
    pal = [x for x in (c["bg"], c["ink"], c["accent"], c["on_accent"], *extra) if x]
    # tarja do erro: o preto do PRÓPRIO produto primeiro (cada produto tem o seu preto), depois o da marca
    surfaces = sorted({x.upper() for x in pal if luminance(x) < 0.03}, key=luminance) + [b.colour("ink").upper()]
    err, surf, nota = error_on(c["bg"], c["ink"], error_cfg(b), surfaces)
    line = err if contrast(err, c["bg"]) >= 3 else c["ink"]
    btn = contrast(c["on_accent"], c["accent"])
    return {"error": err, "error_surface": surf, "error_note": nota, "error_line": line,
            "focus": focus_on(c["bg"], c["accent"], c["ink"]), "live": c.get("live") or c["accent"],
            "btn_fs": 19 if 3 <= btn < 4.5 else None, "btn_ratio": btn}


def build_core(b, shp):
    pal = b.get("color.palette") or {}
    ramps = pal.get("ramps") or {}
    core = {"color": {"$type": "color"}}
    for role, ramp in ramps.items():
        core["color"][role] = {step: {"$value": col(v["hex"])} for step, v in ramp.items()}
    seeds = b.get("color.seeds") or {}
    for role, v in seeds.items():
        hx = v["hex"] if isinstance(v, dict) else v
        node = core["color"].setdefault(role, {})
        node["$root"] = {"$value": col(hx), "$description": (v.get("name") if isinstance(v, dict) else "") or role}
    t = b.get("type") or {}
    fam = {}
    for role in ("display", "text", "mono"):
        e = t.get(role)
        if e:
            name = e if isinstance(e, str) else e.get("family")
            fam[role] = {"$value": [name.split(":")[0], "system-ui", "sans-serif"] if role != "mono"
                         else [name.split(":")[0], "ui-monospace", "monospace"]}
    core["font"] = {"family": {"$type": "fontFamily", **fam},
                    "weight": {"$type": "fontWeight",
                               **{r: {"$value": (t[r].get("weight", 400) if isinstance(t[r], dict) else 400)}
                                  for r in fam}}}
    levels = t.get("levels") or {}
    core["typography"] = {"$type": "typography"}
    for name, lv in levels.items():
        core["typography"][name] = {"$value": {
            "fontFamily": "{font.family.%s}" % lv["role"], "fontWeight": "{font.weight.%s}" % lv["role"],
            "fontSize": dim(lv["size"]), "lineHeight": lv["line_height"],
            "letterSpacing": dim(round(lv["tracking"], 3), "em") if lv["tracking"] else dim(0)}}
    core["spacing"] = {"$type": "dimension", **{str(i): {"$value": dim(v)} for i, v in enumerate(SPACE)}}
    # ---- forma: primitivos (site) + papéis com alias; arte 1080 em $extensions
    rad = {"$type": "dimension", "$description": (shp["regra"] or "raios de canto") + (
        f" · combinação {shp['combo']}" if shp.get("combo") else "") + (f" · {shp['status']}" if shp.get("status") else "")}
    for k in ("none", "sm", "md", "lg", "full"):
        rad[k] = {"$value": dim(shp["site"][k]), "$description": f"{STEP_NAMES[k]} (primitivo)",
                  "$extensions": {f"{EXT}.arte1080": shp["arte"][k]}}
    rad["base"] = {"$value": "{radius.md}", "$description": "compatibilidade (marcas antigas): = radius.md"}
    for role, p in shp["papeis"].items():
        node = {"$value": "{radius.%s}" % p["passo"] if p["passo"] else dim(p["site"]),
                "$description": p["nota"] + (" (círculo: elemento quadrado)" if p["circulo"] else ""),
                "$extensions": {f"{EXT}.arte1080": p["arte"], f"{EXT}.papel": True, f"{EXT}.origem": p["origem"]}}
        if p["cantos_site"]:
            node["$extensions"][f"{EXT}.cantos"] = p["cantos_site"]
            node["$extensions"][f"{EXT}.cantos-arte1080"] = p["cantos_arte"]
        rad[role] = node
    core["radius"] = rad
    core["stroke"] = {"$type": "dimension", "hair": {"$value": dim(1)},
                      "base": {"$value": dim((b.get("icons") or {}).get("stroke", 2))},
                      "bold": {"$value": dim(round((b.get("icons") or {}).get("stroke", 2) * 1.75, 2))}}
    g = b.get("grid") or {}
    w = web(b)
    core["grid"] = {"columns": {"$type": "number", "$value": g.get("columns", 12)},
                    "margin": {"$type": "number", "$value": g.get("margin", 0.06),
                               "$description": "fração da largura do formato"},
                    "gutter": {"$type": "number", "$value": g.get("gutter", 0.02)},
                    "baseline": {"$type": "dimension", "$value": dim(g.get("baseline", 8))},
                    "angle": {"$type": "number", "$value": g.get("angle", 0), "$description": "ângulo próprio (DNA)"},
                    "web": {"$type": "number", "$description": "colunas do SITE por ponto de quebra",
                            **{k: {"$value": v} for k, v in w["columns"].items()}}}
    core["breakpoint"] = {"$type": "dimension", "$description": "largura mínima (celular primeiro)",
                          **{k: {"$value": dim(v)} for k, v in w["breakpoints"].items()}}
    core["container"] = {"$type": "dimension", **{k: {"$value": dim(v)} for k, v in w["container"].items()}}
    m = b.get("motion") or {}
    eas = dict(m.get("easing") or {})
    notes = m.get("easing_notes") or {}
    ease_tree = {"$type": "cubicBezier"}
    for k, v in eas.items():
        ease_tree[k] = {"$value": v, **({"$description": notes[k]} if notes.get(k) else {})}
    if not any(list(v) == PRODUTIVO for v in eas.values()):
        ease_tree["produtivo"] = {"$value": PRODUTIVO, "$description": notes.get("produtivo") or PRODUTIVO_NOTA}
    core["motion"] = {
        "duration": {"$type": "duration", **{k: {"$value": dim(v, "ms")} for k, v in (m.get("durations") or {}).items()}},
        "easing": ease_tree}
    a = access(b)
    core["focus"] = {"ring": {"$type": "dimension",
                              "$description": "anel de foco: ≥ 2 px e 3:1 (WCAG 2.4.13); a cor é de contexto "
                                              "(--focus-ring-color)",
                              "width": {"$value": dim(a["width"])}, "offset": {"$value": dim(a["offset"])}}}
    core["target"] = {"min": {"$type": "dimension", "$value": dim(a["target"]),
                              "$description": "alvo de toque mínimo (WCAG 2.5.8 pede 24; nosso padrão 48)"}}
    core["state"] = {"$type": "number", "$description": "camada da cor do texto por cima do fundo do componente",
                     **{k: {"$value": v} for k, v in STATE.items()}}
    core["opacity"] = {"$type": "number", "disabled": {"$value": OPACITY_DISABLED, "$description":
                                                      "componente desabilitado (sem exigência de contraste, WCAG 1.4.3)"}}
    return core


def alias_of(hx, ramps):
    for role, ramp in ramps.items():
        for step, v in ramp.items():
            if v["hex"].lower() == hx.lower():
                return "{color.%s.%s}" % (role, step)
    return None


def mode_context(b, mode):
    """Contexto da marca-mãe num modo (light/dark) a partir dos papéis do palette.py."""
    roles = ((b.get("color.palette") or {}).get("roles") or {}).get(mode) or {}
    bg, ink = roles.get("bg", "#FFFFFF"), roles.get("text", "#111111")
    acc = roles.get("accent", roles.get("brand", ink))
    return {"bg": bg, "ink": ink, "accent": acc, "on_accent": roles.get("on-accent", roles.get("on-brand", bg)),
            "live": acc}


def build_mode(b, mode):
    pal = b.get("color.palette") or {}
    roles = (pal.get("roles") or {}).get(mode) or {}
    ramps = pal.get("ramps") or {}
    seeds = {k: (v["hex"] if isinstance(v, dict) else v) for k, v in (b.get("color.seeds") or {}).items()}
    out = {"role": {"$type": "color"}}
    for name, hx in roles.items():
        seed = next((k for k, v in seeds.items() if v.lower() == hx.lower()), None)
        ref = "{color.%s}" % seed if seed else alias_of(hx, ramps)
        out["role"][name] = {"$value": ref or col(hx)}
    cc = ctx_colors(b, mode_context(b, mode))
    out["role"]["error"] = {"$value": col(cc["error"]), "$description": "mensagem de erro (fio 2 px + ✕ + 'Erro:')"}
    out["role"]["focus"] = {"$value": col(cc["focus"]), "$description": "anel de foco (≥ 3:1 sobre o fundo)"}
    out["role"]["live"] = {"$value": col(cc["live"]), "$description": "ponto ao vivo / tally"}
    return out


def flat(tree, prefix=""):
    """Yield (path, token) for every token (node with $value)."""
    for k, v in tree.items():
        if k.startswith("$") and k != "$root":
            continue
        if isinstance(v, dict) and "$value" in v:
            yield (prefix if k == "$root" else (f"{prefix}-{k}" if prefix else k)), v
        elif isinstance(v, dict):
            yield from flat(v, f"{prefix}-{k}" if prefix else k)


def resolve(val, index):
    if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
        key = val[1:-1].replace(".", "-")
        tok = index.get(key)
        return resolve(tok["$value"], index) if tok else val
    return val


def css_value(v, index):
    v = resolve(v, index)
    if isinstance(v, dict) and "hex" in v:
        return v["hex"]
    if isinstance(v, dict) and "unit" in v:
        return f"{v['value']}{v['unit']}"
    if isinstance(v, list) and len(v) == 4 and all(isinstance(x, (int, float)) for x in v):
        return "cubic-bezier(%s)" % ", ".join(f"{x:g}" for x in v)
    if isinstance(v, list):
        return ", ".join(f'"{x}"' if " " in str(x) else str(x) for x in v)
    return str(v)


def product_label(p, alt=False):
    return f"{p['name']}" + (f" · {p['tag']}" if p.get("tag") else "") + (" (alt)" if alt else "")


def _extra(p, alt=False):
    """Cores do produto que podem virar tarja de erro (as escuras de principal e alt)."""
    c = p["colors"]
    xs = [c["bg"], c["ink"], c["accent"], c["on_accent"]]
    if c.get("alt"):
        xs += [c["alt"]["bg"], c["alt"]["ink"], c["alt"]["accent"], c["alt"]["on_accent"]]
    return xs


def build_products(b, prods):
    """DTCG 2025.10: grupo "produto" → um grupo por produto (bg, ink, accent, on-accent, error, live, focus [+ alt]).
    O contraste vai em $extensions (o par, a razão, a nota e se passa no mínimo do uso)."""
    def group(c, extra):
        pairs = {p["par"]: p for p in product_pairs(c)}
        ext = lambda pr: {f"{EXT}.contrast": {  # noqa: E731
            "sobre": "accent" if pr["par"] == "botão" else "bg", "ratio": pr["ratio"], "nota": pr["nota"],
            "minimo": pr["need"], "uso": pr["uso"], "ok": pr["ok"]}}
        cc = ctx_colors(b, c, extra)
        err_ext = {"sobre": cc["error_surface"] or "bg",
                   "ratio": round(contrast(cc["error"], cc["error_surface"] or c["bg"]), 2), "nota": cc["error_note"]}
        g = {"bg": {"$value": col(c["bg"])},
             "ink": {"$value": col(c["ink"]), "$extensions": ext(pairs["texto"])},
             "accent": {"$value": col(c["accent"]), "$extensions": ext(pairs["destaque"])},
             "on-accent": {"$value": col(c["on_accent"]), "$extensions": ext(pairs["botão"])},
             "error": {"$value": col(cc["error"]), "$description": "mensagem de erro: fio 2 px + ✕ + 'Erro:', nunca "
                                                                  "bloco cheio", "$extensions": {f"{EXT}.contrast": err_ext}},
             "live": {"$value": col(cc["live"]), "$description": "ponto ao vivo / tally",
                      "$extensions": {f"{EXT}.contrast": {"sobre": "bg", "ratio": round(contrast(cc["live"], c["bg"]), 2)}}},
             "focus": {"$value": col(cc["focus"]), "$description": "anel de foco (≥ 3:1 sobre o fundo)"}}
        if cc["error_surface"]:
            g["error-surface"] = {"$value": col(cc["error_surface"]), "$description": "tarja atrás da mensagem de erro"}
        return g
    tree = {"produto": {"$type": "color"}}
    if b.get("products_rule"):
        tree["produto"]["$description"] = b.get("products_rule")
    for p in prods:
        desc = product_label(p) + (f" — {p['sub']}" if p.get("sub") else "")
        if p.get("color_name"):
            desc += f" · cor: {p['color_name']}" + (f" ({p['color_name_status']})" if p.get("color_name_status") else "")
        g = {"$description": desc, **group(p["colors"], _extra(p))}
        if p.get("label"):
            g["$extensions"] = {f"{EXT}.label": p["label"]}
        if p["colors"].get("alt"):
            g["alt"] = {"$description": "versão alternativa", **group(p["colors"]["alt"], _extra(p, True))}
        tree["produto"][p["id"]] = g
    return tree


def _decl(name, value, note=""):
    d = f"  --{name}: {value};"
    return f"{d:<38}/* {note} */" if note else d


def _note(pr):
    return (f"{pr['par']}: {pr['fg']} sobre {pr['bg']} {fmt_ratio(pr['ratio'])} {pr['nota']} — "
            + ("ok" if pr["ok"] else "FALHA") + f" (mín. {fmt_ratio(pr['need'])} p/ {pr['uso']})")


def ctx_decls(cc, c):
    """Declarações de erro, live, foco e botão de um contexto."""
    L = [_decl("color-error", cc["error"], cc["error_note"]),
         _decl("color-error-surface", cc["error_surface"] or "transparent",
               "tarja atrás da mensagem de erro" if cc["error_surface"] else ""),
         _decl("color-error-line", cc["error_line"], f"fio do campo com erro {fmt_ratio(contrast(cc['error_line'], c['bg']))}"),
         _decl("error-pad", "6px 10px" if cc["error_surface"] else "0"),
         _decl("color-live", cc["live"], f"ponto ao vivo {fmt_ratio(contrast(cc['live'], c['bg']))}"),
         _decl("color-focus", cc["focus"], f"anel de foco {fmt_ratio(contrast(cc['focus'], c['bg']))} (mín. 3:1)"),
         _decl("focus-ring-color", cc["focus"])]
    if cc["btn_fs"]:
        L.append(_decl("btn-fs", f"{cc['btn_fs']}px", f"texto do botão {fmt_ratio(cc['btn_ratio'])} < 4,5:1 → "
                                                     "≥ 18,7 px negrito (texto grande WCAG)"))
    return L


def context_css(selector, c, comment, b, extra=()):
    """Bloco com as cores de contexto de um produto (valores literais + contraste WCAG comentado)."""
    pairs = {p["par"]: p for p in product_pairs(c)}
    cc = ctx_colors(b, c, extra)
    return "\n".join([f"{selector} {{  /* {comment} */",
                      _decl("color-bg", c["bg"]),
                      _decl("color-ink", c["ink"], _note(pairs["texto"])),
                      _decl("color-accent", c["accent"], _note(pairs["destaque"])),
                      _decl("color-on-accent", c["on_accent"], _note(pairs["botão"])),
                      *ctx_decls(cc, c), "}"])


def products_css(b, prods):
    L = ["", "/* ---- produtos: cada [data-produto] troca as cores de contexto; [data-variante=\"alt\"] = versão "
             "alternativa. Contraste WCAG 2: texto >= 4,5:1 (AA) · titulo grande/grafico >= 3:1 ---- */"]
    for p in prods:
        sub = f" — {p['sub']}" if p.get("sub") else ""
        L.append(context_css(f'[data-produto="{p["id"]}"]', p["colors"], product_label(p) + sub, b, _extra(p)))
        if p["colors"].get("alt"):
            L.append(context_css(f'[data-produto="{p["id"]}"][data-variante="alt"]', p["colors"]["alt"],
                                 product_label(p, alt=True), b, _extra(p, True)))
    return "\n".join(L) + "\n"


def _radius_css(core, index, meio="site"):
    """Declarações dos raios: primitivos com valor do meio; papéis apontam para o primitivo (var) ou trazem os 4
    cantos. No meio "arte" os papéis são redeclarados (var() resolve onde é declarada)."""
    L = []
    rad = core["radius"]
    for k in ("none", "sm", "md", "lg", "full"):
        v = rad[k]["$extensions"][f"{EXT}.arte1080"] if meio == "arte" else rad[k]["$value"]["value"]
        L.append(f"  --radius-{k}: {v}px;")
    for k, tok in rad.items():
        if k.startswith("$") or k in ("none", "sm", "md", "lg", "full"):
            continue
        ext = tok.get("$extensions") or {}
        cant = ext.get(f"{EXT}.cantos-arte1080" if meio == "arte" else f"{EXT}.cantos")
        if cant:
            L.append(f"  --radius-{k}: {' '.join(f'{x}px' for x in cant)};")
        elif isinstance(tok["$value"], str):
            L.append(f"  --radius-{k}: var(--radius-{tok['$value'][1:-1].split('.')[-1]});")
        else:
            v = ext.get(f"{EXT}.arte1080") if meio == "arte" else tok["$value"]["value"]
            L.append(f"  --radius-{k}: {v}px;")
    return L


def to_css(b, core, light, dark, prods=None):
    index = dict(flat(core))
    lines = [":root {"]
    for path, tok in flat(core):
        if "typography" in path or path.startswith("radius-"):
            continue
        lines.append(f"  --{path}: {css_value(tok['$value'], index)};")
    lines += _radius_css(core, index)
    for path, tok in flat(light):
        lines.append(f"  --{path}: {css_value(tok['$value'], index)};")
    lines.append("}")
    lines.append('[data-theme="dark"] {')
    for path, tok in flat(dark):
        lines.append(f"  --{path}: {css_value(tok['$value'], index)};")
    lines.append("}")
    lines.append('[data-meio="arte"] {  /* peças 1080 (palco.py): MESMOS nomes, raio de arte (≈ 2,75 × o de site) */')
    lines += _radius_css(core, index, "arte")
    lines.append("}")
    # cores de contexto (componentes usam só estas): marca-mãe = papéis do modo; produtos sobrescrevem
    for sel, mode in ((':root, [data-theme="light"]', "light"), ('[data-theme="dark"]', "dark")):
        c = mode_context(b, mode)
        lines.append(f"{sel} {{  /* cores de contexto da marca-mãe — componentes usam só estas */")
        lines += [_decl("color-bg", "var(--role-bg)"), _decl("color-ink", "var(--role-text)"),
                  _decl("color-accent", "var(--role-accent)"), _decl("color-on-accent", "var(--role-on-accent)"),
                  *ctx_decls(ctx_colors(b, c), c), "}"]
    if prods:
        lines.append(products_css(b, prods))
    for name, tok in (core.get("typography") or {}).items():
        if name.startswith("$"):
            continue
        v = tok["$value"]
        lines.append(f".t-{name} {{ font-family: var(--{v['fontFamily'][1:-1].replace('.', '-')}); "
                     f"font-weight: var(--{v['fontWeight'][1:-1].replace('.', '-')}); "
                     f"font-size: {v['fontSize']['value']}px; line-height: {v['lineHeight']}; "
                     f"letter-spacing: {v['letterSpacing']['value']}{v['letterSpacing']['unit']}; }}")
    return "\n".join(lines) + "\n"


def to_tailwind(core, light):
    index = dict(flat(core))
    L = ["@theme {"]
    for path, tok in flat(core):
        v = css_value(tok["$value"], index)
        if path.startswith("color-"):
            L.append(f"  --{path}: {v};")
        elif path.startswith("font-family-"):
            L.append(f"  --font-{path[len('font-family-'):]}: {v};")
        elif path.startswith("radius-"):
            ext = (tok.get("$extensions") or {}).get(f"{EXT}.cantos")
            L.append(f"  --{path}: {' '.join(f'{x}px' for x in ext) if ext else v};")
        elif path.startswith("motion-easing-"):
            L.append(f"  --ease-{path[len('motion-easing-'):]}: {v};")
        elif path.startswith(("breakpoint-", "container-")):
            L.append(f"  --{path}: {v};")
    for name, tok in (core.get("typography") or {}).items():
        if name.startswith("$"):
            continue
        v = tok["$value"]
        L.append(f"  --text-{name}: {v['fontSize']['value'] / 16:g}rem;")
        L.append(f"  --text-{name}--line-height: {v['lineHeight']};")
    L.append("  --spacing: 4px;")
    for path, tok in flat(light):
        L.append(f"  --color-{path.replace('role-', '')}: {css_value(tok['$value'], index)};")
    L.append("}")
    return "\n".join(L) + "\n"


def to_figma(core, mode_tree):
    """Figma import constraints: px only, durations in s, single font family, resolved colours."""
    index = dict(flat(core))

    def conv(node):
        if isinstance(node, dict) and "$value" in node:
            v = resolve(node["$value"], index)
            t = node.get("$type")
            if isinstance(v, dict) and v.get("unit") == "ms":
                v = {"value": v["value"] / 1000, "unit": "s"}
            if isinstance(v, dict) and v.get("unit") == "em":
                return None
            if isinstance(v, list) and v and isinstance(v[0], str):
                v = v[0]
            out = {"$value": v}
            if t:
                out["$type"] = t
            return out
        if isinstance(node, dict):
            res = {}
            for k, x in node.items():
                if k == "$type":
                    res[k] = x
                    continue
                if k.startswith("$") and k != "$root":
                    continue
                c = conv(x)
                if c is not None:
                    res[k] = c
            return res
        return node
    keep = {k: core[k] for k in ("color", "spacing", "radius", "stroke", "font", "motion", "focus", "target",
                                 "breakpoint", "container", "state", "opacity") if k in core}
    merged = conv(keep)
    merged.update(conv(mode_tree))
    # propagate group $type to children (Figma reads per-token types)
    def push(node, t=None):
        if isinstance(node, dict):
            t = node.get("$type", t)
            if "$value" in node and t:
                node["$type"] = t
            for k, v in node.items():
                if isinstance(v, dict):
                    push(v, t)
    push(merged)
    return merged


# ------------------------------------------------------------------ DESIGN.md
A11Y_RULES = [   # 17b §4.1 — padrão da skill (WCAG 2.2 / ABNT NBR 17225:2025); brand.json accessibility sobrescreve
    ("Contraste de texto", "texto ≥ 4,5:1 no pior pixel; 3:1 só para texto grande (≥ 24 px, ou 18,7 px negrito)"),
    ("Contraste de interface", "ícone, borda de campo, gráfico e anel de foco ≥ 3:1 contra o vizinho"),
    ("Foco visível", "anel de 2 px ou mais, ≥ 3:1, nunca escondido por outro elemento"),
    ("Alvo de toque", "≥ 24 × 24 px (WCAG 2.5.8); nosso padrão é 48 px de altura"),
    ("Piscar", "nada pisca mais de 3 vezes por segundo; nunca um fundo inteiro piscando"),
    ("Movimento", "o que se move por mais de 5 s tem pausa; respeitar prefers-reduced-motion"),
    ("Texto alternativo", "toda imagem com alt próprio de até 2 frases, sem 'imagem de'"),
    ("Legenda no vídeo", "vídeo com legenda queimada por padrão"),
    ("Arte e legenda", "o texto da arte também está na legenda do post"),
    ("Hashtag", "Maiúscula Em Cada Palavra (#ComoEsta) para o leitor de tela"),
    ("Emoji", "no máximo 3 por post e nunca no meio da frase; nada de letras 'estilizadas' unicode"),
    ("Linguagem simples", "frase curta; sigla explicada na primeira vez"),
]


def a11y_rules(b):
    """As 12 regras padrão + brand.json accessibility.rules (mesmo nome = substitui; nome novo = acrescenta)."""
    acc = b.get("accessibility") or {}
    rules = [list(r) for r in A11Y_RULES]
    for r in acc.get("rules") or []:
        name, txt = (r.get("name", ""), r.get("rule", "")) if isinstance(r, dict) else (None, str(r))
        hit = next((x for x in rules if name and x[0].lower() == name.lower()), None)
        if hit:
            hit[1] = txt
        else:
            rules.append([name or "Regra da marca", txt])
    return rules


def design_md(b, core, shp, prods):
    pal = b.get("color.palette") or {}
    roles = (pal.get("roles") or {}).get("light", {})
    t = b.get("type") or {}
    lv = t.get("levels") or {}
    seeds = b.get("color.seeds") or {}
    plat = b.get("platform") or {}
    y = ["---", f"name: {b.name}", "colors:"]
    for k, v in seeds.items():
        y.append(f"  {k}: \"{v['hex'] if isinstance(v, dict) else v}\"")
    for k, v in roles.items():
        y.append(f"  {k}: \"{v}\"")
    y.append("typography:")
    for name, l in lv.items():
        y.append(f"  {name}: {{fontFamily: \"{l['family']}\", fontWeight: {l.get('weight') or 400}, "
                 f"fontSize: {l['size']}px, lineHeight: {l['line_height']}, letterSpacing: {l['tracking']}em}}")
    y += ["rounded:"] + [f"  {k}: {shp['site'][k]}px" for k in ("none", "sm", "md", "lg", "full")]
    y += [f"  {k}: \"{{rounded.{p['passo']}}}\"" if p["passo"] else f"  {k}: {p['site']}px"
          for k, p in shp["papeis"].items()]
    y += ["spacing:"] + [f"  s{i}: {v}px" for i, v in enumerate(SPACE) if v]
    y += ["components:",
          "  button-primary: {background: \"{colors.brand}\", color: \"{colors.on-brand}\", rounded: \"{rounded.button}\", "
          f"height: {access(b)['target']}px}}",
          "  input: {rounded: \"{rounded.field}\", borderWidth: 2px}",
          "  card: {rounded: \"{rounded.card}\"}",
          "  tarja: {rounded: \"{rounded.tarja}\"}",
          "  text-link: {color: \"{colors.brand-text}\"}", "---", ""]
    md = [f"# {b.name} — design system", "", "## Overview"]
    md.append(plat.get("idea") and f"Ideia: **{plat['idea']}**." or "")
    if plat.get("principles"):
        md += ["", "Princípios:"] + [f"- **{p.get('name', '')}** — {p.get('rule', '')}" if isinstance(p, dict)
                                     else f"- {p}" for p in plat["principles"]]
    md += ["", "## Colors", "Proporção: " + ", ".join(f"{k} {v}%" for k, v in (b.get("color.proportion") or {}).items())]
    md += [f"- {r_}" for r_ in (b.get("color.rules") or [])]
    if error_cfg(b):
        e = error_cfg(b)
        md += [f"- Erro (status, nunca cor de produto): `{e.get('escuro', '')}` nos fundos escuros · `{e.get('papel', '')}`"
               " no papel; onde nenhuma passa 4,5:1, a mensagem vai numa tarja escura. Erro = fio 2 px + ✕ + 'Erro:',"
               " nunca bloco cheio."]
    md += ["", "## Typography", f"Display: {t.get('display', {}).get('family', '')} · Texto: "
           f"{t.get('text', {}).get('family', '')}"] + [f"- {r_}" for r_ in (t.get("rules") or [])]
    g = b.get("grid") or {}
    w = web(b)
    md += ["", "## Layout", f"Arte: {g.get('columns', 12)} colunas · margem {g.get('margin', 0.06):.0%} da largura · "
           f"calha {g.get('gutter', 0.02):.0%} · linha de base {g.get('baseline', 8)}px · ângulo {g.get('angle', 0)}°",
           "Site: pontos de quebra " + " · ".join(f"{k} {v}px" for k, v in w["breakpoints"].items()) +
           " · colunas " + " / ".join(str(v) for v in w["columns"].values()) +
           f" · contêiner {w['container']['max']}–{w['container']['wide']}px"]
    md += design_md_shape(shp)
    md += ["", "## Graphic devices"] + [f"- **{d.get('name', d['id'])}** ({d['op']}): {d.get('rule', '')}"
                                        for d in (b.get("devices") or [])]
    md += ["", "## Motion"]
    for k, v in (core["motion"]["easing"] or {}).items():
        if not k.startswith("$"):
            md.append(f"- `{k}` cubic-bezier({', '.join(f'{x:g}' for x in v['$value'])})"
                      + (f" — {v['$description']}" if v.get("$description") else ""))
    md += [f"- {x}" for x in (b.get("motion.principles") or [])]
    a = access(b)
    md += ["", "## Accessibility", f"Tokens: anel de foco {a['width']} px a {a['offset']} px (`--focus-ring-*`, cor de "
           f"contexto ≥ 3:1) · alvo mínimo {a['target']} px (`--target-min`) · hover {STATE['hover']:.0%} · pressionado "
           f"{STATE['pressed']:.0%} · desabilitado opacidade {OPACITY_DISABLED:g}. Base: WCAG 2.2 AA / ABNT NBR 17225:2025."]
    md += [f"- **{n}**: {r_}" for n, r_ in a11y_rules(b)]
    md += design_md_products(b, prods)
    off = b.get("official") or {}
    if off:
        md += ["", "## Official channels"] + [f"- {k}: {v}" for k, v in off.items() if isinstance(v, str)]
        md += [f"- Nunca: {x}" for x in (off.get("never") or []) if isinstance(x, str)]
    md += ["", "## Do's and Don'ts"]
    md += [f"- Não: {x}" for x in (b.get("logo.dont") or []) + (b.get("imagery.dont") or [])]
    md += [f"- Voz é: {', '.join((plat.get('voice') or {}).get('is', []))}",
           f"- Voz não é: {', '.join((plat.get('voice') or {}).get('is_not', []))}"]
    return "\n".join(y + md) + "\n"


def design_md_shape(shp):
    md = ["", "## Forma (raios)", (shp["regra"] or "Raios por papel.") +
          (f" Combinação {shp['combo']}." if shp.get("combo") else "") + (f" Status: {shp['status']}." if shp.get("status") else ""),
          "", "Componente usa SÓ papel (`--radius-<papel>`), nunca o primitivo. Raio de arte 1080 ≈ 2,75 × o de site "
              "(`[data-meio=\"arte\"]` troca os valores com os mesmos nomes). Pílula = 9999 px, nunca 50 %.", "",
          "| Papel | Passo | Site | Arte 1080 | Para quê |", "|---|---|---|---|---|"]
    for k, p in shp["papeis"].items():
        sv = "/".join(str(x) for x in p["cantos_site"]) if p["cantos_site"] else ("pílula" if p["site"] >= PILL else p["site"])
        av = "/".join(str(x) for x in p["cantos_arte"]) if p["cantos_arte"] else ("pílula" if p["arte"] >= PILL else p["arte"])
        md.append(f"| `{k}` | {p['passo'] or '—'} | {sv} | {av} | {p['nota']} |")
    if shp["nunca_arredonda"]:
        md += ["", "Nunca arredonda: " + ", ".join(never_round_labels(shp)) + "."]
    md += ["", "Aninhado: raio do filho = pai − (borda + espaço), nunca negativo (espaço ≥ raio → 0: reto dentro de "
               "redondo é a conta certa). Por peça: 1 valor da família + 0 + pílula/círculo = no máximo 3 formas; "
               "nunca dois raios quase iguais (razão < 1,5)."]
    return md


def design_md_products(b, prods):
    """Seção "Produtos" do DESIGN.md: regra de convivência, árvore "qual cor?", tabela de cores com contraste e
    regras por produto."""
    if not prods:
        return []
    from _base import color_tree
    md = ["", "## Produtos"]
    if b.get("products_rule"):
        md.append(b.get("products_rule"))
    tree = color_tree(b)
    if tree:
        md += ["", "Qual cor usar?"] + [f"{i}. {q} → {a}" for i, (q, a, _) in enumerate(tree, 1)]
    md += ["", "Em código: `<section data-produto=\"<id>\">` troca as cores de contexto (`--color-bg`, `--color-ink`, "
               "`--color-accent`, `--color-on-accent`, `--color-error`, `--color-live`, `--color-focus`); "
               "`data-variante=\"alt\"` usa a versão alternativa. Componentes usam só essas variáveis. Contraste "
               "WCAG 2: texto ≥ 4,5:1 · título grande/gráfico ≥ 3:1 · texto do botão ≥ 4,5:1.", "",
           "| Produto | Cor | Rótulo escrito | Fundo | Texto | Destaque | No destaque | Erro | Ao vivo | texto/fundo | "
           "destaque/fundo | botão |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]

    def row(p, c, alt):
        prs = product_pairs(c)
        cc = ctx_colors(b, c, _extra(p, alt))
        cells = " | ".join(f"{fmt_ratio(x['ratio'])} {x['nota']}" + ("" if x["ok"] else " ✗") for x in prs)
        nome = (p.get("color_name") or "") + (" (proposta)" if "proposta" in (p.get("color_name_status") or "") else "")
        return (f"| {product_label(p, alt)} | {nome} | {p.get('label') or ''} | `{c['bg']}` | `{c['ink']}` | "
                f"`{c['accent']}` | `{c['on_accent']}` | `{cc['error']}`" + (f" em `{cc['error_surface']}`"
                                                                              if cc["error_surface"] else "") +
                f" | `{cc['live']}` | {cells} |")
    for p in prods:
        md.append(row(p, p["colors"], False))
        if p["colors"].get("alt"):
            md.append(row(p, p["colors"]["alt"], True))
    md.append("")
    md.append("✗ = abaixo do mínimo para aquele uso (ex.: texto corrido num par de 3,9:1 → só título grande; botão "
              "< 4,5:1 → texto do botão ≥ 18,7 px negrito).")
    cvd = color_pairs_cvd({p.get("color_name") or p["name"]: p["colors"]["accent"] for p in prods})
    bad = [r for r in cvd if r["confunde"]]
    if bad:
        md += ["", "Daltonismo (simulação Machado 2009, ΔE2000 < 10 = confunde; P&B = contraste entre elas < 1,5:1):"]
        br = lambda x: f"{x:.1f}".replace(".", ",")  # noqa: E731
        vis = {"pb": "P&B", "deutan": "deuteranopia", "protan": "protanopia", "tritan": "tritanopia", "normal": "visão normal"}
        md += [f"- {r['a']} × {r['b']}: confunde em {', '.join(vis[k] for k in r['confunde'])} (deutan ΔE {br(r['deutan'])} · protan "
               f"{br(r['protan'])} · contraste entre elas {fmt_ratio(r['luz'])}) → sempre o rótulo escrito junto da cor"
               for r in bad]
    for p in prods:
        if p.get("sub") or p.get("rules") or p.get("dont"):
            md += ["", f"### {product_label(p)}" + (f" — {p['sub']}" if p.get("sub") else "")]
            md += [f"- {r}" for r in p.get("rules") or []]
            md += [f"- {r}" if r.lower().startswith(("não", "nunca", "evite")) else f"- Não: {r}"
                   for r in p.get("dont") or []]
    return md


# ------------------------------------------------------------------ demo: componentes do design system
# Componentes usam SÓ variáveis de tokens.css (cores de contexto, fontes, PAPÉIS de raio, foco, estados, durações).
# Largura fixa de 1280 px no PNG: conteúdo 1104 px em 3 colunas de 352 px (calha 24) — os tamanhos de texto que
# dependem do nome (tarja, cartão, estados) são MEDIDOS com a fonte real da marca para caber.
DEMO_W = 1280
DEMO_CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--role-bg);color:var(--role-text);font:400 16px/1.5 var(--font-family-text);
  font-synthesis:none;-webkit-font-smoothing:antialiased}
.ds-wrap{max-width:1200px;margin:0 auto;padding:0 48px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.ds-topo{padding:64px 0 56px;background:var(--color-bg);color:var(--color-ink)}
.ds-topo h1{margin:14px 0 18px;max-width:1000px}
.ds-topo .t-lead{max-width:860px;margin:0 0 28px}
.ds-eyebrow{margin:0;font:700 13px/1.3 var(--font-family-text);letter-spacing:.12em;text-transform:uppercase}
.ds-rot{margin:0 0 18px;font:700 12px/1.3 var(--font-family-text);letter-spacing:.12em;text-transform:uppercase}
.ds-sec{padding:56px 0;background:var(--color-bg);color:var(--color-ink);border-top:1px solid var(--role-border)}
.ds-sec>.ds-wrap>h2,.ds-head h2{margin:0;font-family:var(--font-family-display);font-weight:var(--font-weight-display);
  font-size:40px;line-height:1.02;letter-spacing:-.01em}
.ds-sec>.ds-wrap>h2{margin-bottom:28px}
.ds-tipo-l{display:flex;align-items:baseline;gap:32px;padding:12px 0;
  border-bottom:1px solid color-mix(in srgb,var(--color-ink) 16%,transparent)}
.ds-tipo-l .rot{width:200px;flex:none;font-size:13px;font-weight:700;font-variant-numeric:tabular-nums}
.ds-tipo-l p{margin:0;min-width:0}
.ramp{display:flex;gap:4px;align-items:stretch;margin:0 0 6px}
.ramp b{width:150px;flex:none;font-size:14px;align-self:center}
.ramp span{flex:1;height:48px;font-size:11px;display:flex;align-items:flex-end;padding:4px 6px}
.ds-prods{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;margin-top:32px}
.ds-prod{border:1px solid color-mix(in srgb,var(--color-ink) 18%,transparent);border-radius:var(--radius-card);
  overflow:hidden;background:var(--color-bg);color:var(--color-ink)}
.ds-prod>b{display:block;padding:14px 14px 0;font-size:15px}
.ds-prod .cores b{font-weight:700}
.ds-prod .cores{display:flex;flex-direction:column;gap:8px;padding:12px 14px 16px}
.ds-prod .cores span{display:grid;grid-template-columns:28px minmax(0,1fr) auto;gap:10px;align-items:center;
  font-size:13px;line-height:1.2;font-variant-numeric:tabular-nums;white-space:nowrap}
.ds-prod .cores i{display:block;height:28px;box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--color-ink) 30%,transparent)}
.ds-regra{margin:0 0 24px;max-width:900px;font-size:16px}
.ds-bloco{padding:56px 0 64px;background:var(--color-bg);color:var(--color-ink)}
.ds-head{display:flex;justify-content:space-between;align-items:last baseline;gap:32px;padding-bottom:18px;
  margin-bottom:32px;border-bottom:3px solid var(--color-accent)}
.ds-head .ds-eyebrow{margin-bottom:10px}
.ds-sub{margin:0;max-width:440px;text-align:right;font-size:15px}
.ds-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
.ds-cel{border:1px solid color-mix(in srgb,var(--color-ink) 22%,transparent);border-radius:var(--radius-section);
  padding:24px;min-width:0}
.span2{grid-column:span 2}.span3{grid-column:1/-1}
.ds-pilha{display:flex;flex-direction:column;align-items:flex-start;gap:18px}
.ds-nota{margin:16px 0 0;font-size:13px;line-height:1.45}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:var(--target-min);padding:0 26px;
  border:0;border-radius:var(--radius-button);background:var(--color-accent);color:var(--color-on-accent);
  font:700 var(--btn-fs,15px)/1.1 var(--font-family-text);letter-spacing:.06em;text-transform:uppercase;
  text-decoration:none;white-space:nowrap;cursor:pointer}
.btn.longo{text-transform:none;letter-spacing:0;font-size:var(--btn-fs,16px)}  /* CTA > 5 palavras: caixa-alta só p/ 1–5 */
.btn:hover,.btn.is-hover{background:color-mix(in srgb,var(--color-on-accent) calc(var(--state-hover) * 100%),var(--color-accent))}
.btn:active,.btn.is-pressed{background:color-mix(in srgb,var(--color-on-accent) calc(var(--state-pressed) * 100%),var(--color-accent));
  transform:translateY(1px)}
.btn:focus-visible,.btn.is-foco,.link:focus-visible,.link.is-foco{outline:var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset:var(--focus-ring-offset)}
.btn[aria-disabled="true"]{opacity:var(--opacity-disabled);cursor:not-allowed}
.btn[aria-busy="true"]{cursor:progress}
.gira{width:16px;height:16px;flex:none;border-radius:50%;border:2.5px solid currentColor;border-right-color:transparent;
  animation:gira .8s linear infinite}
@keyframes gira{to{transform:rotate(360deg)}}
.link{color:var(--color-ink);font-weight:700;text-decoration:underline;text-decoration-color:var(--color-accent);
  text-decoration-thickness:2px;text-underline-offset:6px}
.estados-btn{display:grid;gap:14px 40px}
.eb{display:flex;align-items:center;gap:18px;min-width:0}
.eb-rot{width:118px;flex:none;font-size:13px;font-weight:700;letter-spacing:.04em}
.estados-campo{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px 32px}
.campo{display:flex;flex-direction:column;gap:8px;min-width:0}
.campo .eb-rot{width:auto;margin-bottom:2px;text-transform:uppercase;letter-spacing:.1em;font-size:12px}
.campo label{font-weight:700;font-size:14px}
.campo input{font:400 16px/1.4 var(--font-family-text);color:var(--color-ink);background:transparent;
  min-height:var(--target-min);padding:0 14px;border:2px solid color-mix(in srgb,var(--color-ink) 62%,var(--color-bg));
  border-radius:var(--radius-field);min-width:0}
.campo input:focus-visible,.campo input.is-foco{outline:var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset:var(--focus-ring-offset)}
.campo input:disabled{opacity:var(--opacity-disabled);cursor:not-allowed}
.campo .ajuda{margin:0;font-size:14px;line-height:1.4}
.campo.erro input{border-color:var(--color-error-line)}
.campo .msg{margin:0;align-self:flex-start;color:var(--color-error);background:var(--color-error-surface);
  padding:var(--error-pad);font-size:14px;font-weight:700;line-height:1.4}
.chip{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 14px;border:1.5px solid currentColor;
  border-radius:var(--radius-chip);font:700 13px/1 var(--font-family-text);letter-spacing:.1em;text-transform:uppercase;
  white-space:nowrap}
.chip.live{border-radius:var(--radius-live)}
.ponto{width:10px;height:10px;flex:none;border-radius:50%;background:var(--color-live);animation:pulso 1s steps(2,jump-none) infinite}
@keyframes pulso{50%{opacity:.25}}
.eventos{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px}
.evento{min-height:210px;padding:16px;display:flex;flex-direction:column;align-items:flex-start;gap:12px;min-width:0;
  border:1.5px solid color-mix(in srgb,var(--color-ink) 30%,transparent);border-radius:var(--radius-card)}
.evento .val{margin:4px 0 0;font-family:var(--font-family-display);font-weight:var(--font-weight-display);line-height:1;
  white-space:nowrap;font-variant-numeric:tabular-nums}
.evento .ev-txt{margin:0;font-size:14px;line-height:1.35}
.evento .acao{margin-top:auto}
.evento .btn{min-height:40px;padding:0 18px}
.evento[data-estado="ao-vivo"]{border-color:var(--color-live);box-shadow:inset 0 0 0 1.5px var(--color-live)}
.evento[data-estado="encerrado"]{border-style:dashed}
.preco-aviso{margin:18px 0 0;font-family:var(--font-family-display);font-weight:var(--font-weight-display);font-size:28px;
  line-height:1.05;color:var(--color-ink)}
.pilula{display:inline-flex;align-items:baseline;gap:12px;margin:18px 0 0;padding:10px 20px;border-radius:var(--radius-chip);
  background:var(--color-ink);color:var(--color-bg);font-variant-numeric:tabular-nums;white-space:nowrap}
.pilula s{font-size:15px}.pilula strong{font-family:var(--font-family-display);font-weight:var(--font-weight-display);
  font-size:24px;line-height:1}
.parcelas{margin:8px 0 0;font-size:14px;font-variant-numeric:tabular-nums}
.tarja{background:var(--color-accent);color:var(--color-bg);font-family:var(--font-family-display);
  border-radius:var(--radius-tarja);font-weight:var(--font-weight-display);line-height:1;padding:.3em .3em;
  text-transform:uppercase;text-box:trim-both cap alphabetic;letter-spacing:-.01em;white-space:nowrap;overflow:hidden}
.cartao{border:1.5px solid color-mix(in srgb,var(--color-ink) 26%,transparent);border-radius:var(--radius-card);overflow:hidden}
.cartao-faixa{height:12px;background:var(--color-accent)}
.cartao-corpo{padding:20px 20px 22px}
.cartao h3{margin:10px 0 8px;font-family:var(--font-family-display);font-weight:var(--font-weight-display);
  line-height:1.02;letter-spacing:-.01em}
.cartao-sub{margin:0 0 18px;font-size:15px}
.escala{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:24px;margin-bottom:40px}
.esc .am{height:96px;background:var(--color-accent)}
.esc b,.pap b{display:block;margin-top:12px;font-size:15px}
.esc span,.pap span{display:block;font-size:13px;line-height:1.4;font-variant-numeric:tabular-nums}
.papeis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:28px 24px;margin-bottom:36px}
.pap .am{height:64px;width:120px;background:color-mix(in srgb,var(--color-accent) 85%,var(--color-bg));
  border:2px solid var(--color-accent)}
.pap .am.q{width:64px}
.pap .nota{margin-top:4px;font-size:12.5px;line-height:1.35}
.nunca{display:flex;flex-wrap:wrap;gap:10px;margin:0;padding:0;list-style:none}
.nunca li{padding:6px 12px;border:1.5px solid currentColor;border-radius:var(--radius-tarja);font-size:14px;font-weight:700}
.faixa-rot{margin:28px 0 10px;font:700 12px/1.3 var(--font-family-text);letter-spacing:.12em;text-transform:uppercase}
.faixa{display:grid;gap:12px}
.fx{background:var(--color-bg);color:var(--color-ink);padding:16px;display:flex;flex-direction:column;gap:12px;min-width:0;
  border:1px solid color-mix(in srgb,var(--color-ink) 18%,transparent)}
.fx-tarja{background:var(--color-accent);color:var(--color-on-accent);font-family:var(--font-family-display);
  font-weight:var(--font-weight-display);font-size:26px;line-height:1;padding:10px 12px;border-radius:var(--radius-tarja);
  text-transform:uppercase;white-space:nowrap;overflow:hidden}
.fx-rot{margin:0;font-size:13px;font-weight:700;line-height:1.35}
.alerta{margin:24px 0 0;padding:14px 18px;border-left:4px solid var(--color-ink);font-size:15px;max-width:980px}
.rodape{padding:48px 0 56px;background:var(--color-bg);color:var(--color-ink);border-top:3px solid var(--color-accent)}
.rodape .cols{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;margin:20px 0 28px}
.rodape dt{font:700 12px/1.3 var(--font-family-text);letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px}
.rodape dd{margin:0;font-size:16px;font-weight:700;overflow-wrap:anywhere}
.rodape .legal{margin:0;font-size:14px;line-height:1.5;max-width:900px}
.adef{font-style:italic}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""


def fit(s, max_w, max_size, spec, tracking=0.0, min_size=12):
    """Maior corpo (px) em que a linha s cabe em max_w px, medido na fonte real (fallback: 0,62 em/letra)."""
    try:
        w = text_width(s, 100, spec, tracking) / 100
    except Exception:
        w = 0.62 * len(s)
    return int(max(min_size, min(max_size, max_w / max(w, 1e-6))))


def width_at(s, size, spec, tracking=0.0):
    try:
        return text_width(s, size, spec, tracking)
    except Exception:
        return 0.62 * len(s) * size


def demo_txt(b):
    """Textos da demo: SÓ a copy da cliente, de brand.json `demo` (cta, link, preco, preco_de, parcelas,
    preco_aviso, hora). Sem copy → "[a definir]" com aviso — nunca CTA, oferta ou preço "de/por" de exemplo.
    `preco: null` (cliente sem preço público, ex.: "valores ao vivo") → mostra `preco_aviso`. Rótulos de interface
    (Enviando…, Enviado, estados do evento) e o e-mail de exemplo do campo são genéricos da skill."""
    d = b.get("demo") or {}
    cta = a_definir(d.get("cta"), "demo.cta")
    return {"cta": cta, "link": a_definir(d.get("link"), "demo.link"),
            "email": d.get("email", "nome@email.com"),
            "preco": d.get("preco"), "preco_de": d.get("preco_de") if d.get("preco") else None,
            "parcelas": d.get("parcelas") if d.get("preco") else None,
            "preco_aviso": d.get("preco_aviso") or (None if d.get("preco") else a_definir(None, "demo.preco_aviso")),
            "enviando": d.get("botao_enviando", "Enviando…"), "sucesso": d.get("botao_sucesso", "Enviado"),
            "hora": d.get("hora") or a_definir(None, "demo.hora"),
            "btn_cls": " longo" if len(str(cta).split()) > 5 else ""}


def event_states(b):
    """Os 5 estados do evento: padrão genérico da skill + brand.json demo.estados ({id: {chip, valor, texto,
    acao}} ou lista com id)."""
    T = demo_txt(b)
    user = (b.get("demo") or {}).get("estados") or {}
    if isinstance(user, list):
        user = {u.get("id"): u for u in user if isinstance(u, dict)}
    out = []
    for st in EVENT_STATES:
        s = {**st, **(user.get(st["id"]) or {})}
        out.append({k: (v.replace("{hora}", T["hora"]) if isinstance(v, str) else v) for k, v in s.items()})
    return out


def text_spec(b, w=700):
    t = (b.get("type") or {}).get("text")
    fam = (t if isinstance(t, str) else (t or {}).get("family")) or "Archivo"
    return b.font_spec("text", w) if fam.lower().endswith((".ttf", ".otf")) else f"{fam.split(':')[0]}:{w}"


def button_states(b, ident, fs):
    T = demo_txt(b)
    spec = text_spec(b)
    up = not T["btn_cls"]
    label_w = width_at(T["cta"].upper() if up else T["cta"], fs, spec, 0.06 if up else 0) + 52 + 4
    cols = 2 if label_w <= (1056 - 40) / 2 - 136 else 1
    cta = E(T["cta"])
    rows = [("padrão", f'<a class="btn{T["btn_cls"]}" href="#">{cta}</a>'),
            ("hover", f'<a class="btn{T["btn_cls"]} is-hover" href="#">{cta}</a>'),
            ("foco", f'<a class="btn{T["btn_cls"]} is-foco" href="#">{cta}</a>'),
            ("pressionado", f'<a class="btn{T["btn_cls"]} is-pressed" href="#">{cta}</a>'),
            ("desabilitado", f'<a class="btn{T["btn_cls"]}" aria-disabled="true" role="link">{cta}</a>'),
            ("enviando", f'<button class="btn{T["btn_cls"]}" type="button" aria-busy="true" aria-live="polite">'
                         f'<span class="gira" aria-hidden="true"></span>{E(T["enviando"])}</button>'),
            ("sucesso", f'<button class="btn{T["btn_cls"]}" type="button" aria-live="polite"><span aria-hidden="true">'
                        f'✓</span>{E(T["sucesso"])}</button>')]
    return (f'<div class="estados-btn" style="grid-template-columns:repeat({cols},minmax(0,1fr))">' +
            "".join(f'<div class="eb"><span class="eb-rot">{E(n)}</span>{h}</div>' for n, h in rows) + "</div>")


def field_states(b, ident):
    T = demo_txt(b)
    i = ident
    return f"""<div class="estados-campo">
<div class="campo"><span class="eb-rot">vazio</span><label for="c1-{i}">E-mail</label>
<input id="c1-{i}" type="email" autocomplete="email" aria-describedby="c1-{i}-a"><p class="ajuda" id="c1-{i}-a">Ex.: nome@email.com</p></div>
<div class="campo"><span class="eb-rot">preenchido</span><label for="c2-{i}">E-mail</label>
<input id="c2-{i}" type="email" autocomplete="email" value="{E(T['email'])}"></div>
<div class="campo"><span class="eb-rot">foco</span><label for="c3-{i}">E-mail</label>
<input id="c3-{i}" class="is-foco" type="email" autocomplete="email" value="{E(T['email'])}"></div>
<div class="campo erro"><span class="eb-rot">erro</span><label for="c4-{i}">WhatsApp com DDD</label>
<input id="c4-{i}" type="tel" autocomplete="tel" value="1191234" aria-invalid="true" aria-describedby="c4-{i}-m">
<p class="msg" id="c4-{i}-m"><span aria-hidden="true">✕ </span>Erro: faltam números. Ex.: 11 91234-5678</p></div>
<div class="campo"><span class="eb-rot">desabilitado</span><label for="c5-{i}">E-mail</label>
<input id="c5-{i}" type="email" value="{E(T['email'])}" disabled></div>
</div>"""


def event_block(b):
    sts = event_states(b)
    sd = b.font_spec("display", 800)
    val_px = min(fit(s["valor"], 166, 40, sd) for s in sts)
    cards = []
    for s in sts:
        dot = '<span class="ponto" aria-hidden="true"></span>' if s["id"] == "ao-vivo" else ""
        if not s.get("acao"):
            act = ""
        elif s["id"] == "ao-vivo":
            act = f'<a class="btn acao" href="#">{E(s["acao"])}</a>'
        else:
            act = f'<a class="link acao" href="#">{E(s["acao"])}</a>'
        cards.append(f'<article class="evento" data-estado="{E(s["id"])}" aria-label="{E(s["texto"])}">'
                     f'<span class="chip live">{dot}{E(s["chip"])}</span><p class="val" style="font-size:{val_px}px">'
                     f'{E(s["valor"])}</p><p class="ev-txt">{E(s["texto"])}</p>{act}</article>')
    return f'<div class="eventos">{"".join(cards)}</div>'


def comp_block(b, key, nome, eyebrow, sub, attrs, num=None, tag="", label="", fs=15, completo=True):
    """Bloco com todos os componentes num contexto de cor (marca-mãe ou [data-produto])."""
    sd = b.font_spec("display", 800)
    up = nome.upper()
    tarja_px = fit(up, 600, 72, sd, -0.01)
    longest = max(nome.split(), key=len) if nome.split() else nome
    card_px = min(fit(longest, 290, 34, sd, -0.01), 34)
    ident = re.sub(r"[^a-z0-9-]", "", key)
    T = demo_txt(b)
    if T["preco"]:
        preco_html = (f'<p class="pilula">' + (f'<span class="sr">de</span><s>{E(T["preco_de"])}</s><span class="sr">por</span>'
                      if T["preco_de"] else "") + f'<strong>{E(T["preco"])}</strong></p>'
                      + (f'<p class="parcelas">{E(T["parcelas"])}</p>' if T["parcelas"] else ""))
    else:
        preco_html = f'<p class="preco-aviso">{E(T["preco_aviso"])}</p>'
    card_eb = label or (f"{num:02d} · {tag}" if isinstance(num, int) and tag else tag or "marca-mãe")
    acc = access(b)
    # data-sub = pedaço que o manual fotografa à parte (em tamanho real, legível); data-resumo="nao" = só na
    # marca-mãe (os produtos repetem o mesmo componente em outra cor)
    rs = "" if completo else ' data-resumo="nao"'
    return f"""<section class="ds-bloco" {attrs} data-shot="{key}"><div class="ds-wrap">
<header class="ds-head" data-sub="cabecalho" data-titulo="{E(nome)}"><div><p class="ds-eyebrow">{E(eyebrow)}</p><h2>{E(nome)}</h2></div>
<p class="ds-sub">{E(sub)}</p></header>
<div class="ds-grid">
<div class="ds-cel span3" data-sub="botao" data-titulo="Botão · 7 estados"
 data-tokens="--color-accent, --color-on-accent, --radius-button, --btn-fs, --state-hover, --state-pressed, --focus-ring-*, --opacity-disabled, --target-min"><p class="ds-rot">Botão · 7 estados</p>{button_states(b, ident, fs)}
<p class="ds-nota">Hover = camada de {STATE['hover']:.0%} da cor do texto por cima · pressionado {STATE['pressed']:.0%} ·
foco = anel de {acc['width']} px afastado {acc['offset']} px, na cor de foco (≥ 3:1) · desabilitado = opacidade
{str(OPACITY_DISABLED).replace('.', ',')} · "enviando" trava o clique (aria-busy). Alvo ≥ {acc['target']} px.
Secundário = link sublinhado: <a class="link" href="#">{E(T["link"])}</a></p></div>
<div class="ds-cel span3" data-sub="campo" data-titulo="Campo · 5 estados"{rs}
 data-tokens="--radius-field, --color-error, --color-error-surface, --color-error-line, --focus-ring-*, --target-min"><p class="ds-rot">Campo · 5 estados</p>{field_states(b, ident)}
<p class="ds-nota">Rótulo sempre visível acima do campo (nunca o placeholder como rótulo). Erro = fio de 2 px + ✕ +
"Erro:" na cor de erro, perto do campo, guardando o que a pessoa digitou — nunca bloco cheio.</p></div>
<div class="ds-cel span3" data-sub="evento" data-titulo="Estado do evento · 5 estados"{rs}
 data-tokens="--color-live, --radius-live, --radius-card, --color-ink"><p class="ds-rot">Estado do evento · 5 estados</p>{event_block(b)}
<p class="ds-nota">Chip, valor, texto e ação mudam juntos. Números tabulares (mesma largura). O ponto ao vivo pisca a
1 Hz e para com movimento reduzido.</p></div>
<div class="ds-cel span2" data-sub="tarja-cartao" data-titulo="Tarja, preço e cartão"
 data-tokens="--radius-tarja, --radius-card, --color-accent, --color-bg, --font-family-display"><p class="ds-rot">Tarja e preço</p><div class="tarja" style="font-size:{tarja_px}px">{E(up)}</div>
{preco_html}<p class="ds-nota">Faixa na cor de destaque com o texto vazado (a letra tem a cor do fundo).</p></div>
<div class="ds-cel" data-sub="tarja-cartao"><p class="ds-rot">Cartão</p><article class="cartao">
<div class="cartao-faixa" aria-hidden="true"></div><div class="cartao-corpo"><p class="ds-eyebrow">{E(card_eb)}</p>
<h3 style="font-size:{card_px}px">{E(nome)}</h3><p class="cartao-sub">{E(sub)}</p>
<a class="link" href="#">{E(T["link"])}</a></div></article></div>
</div></div></section>"""


def alt_block(b, p):
    sd = b.font_spec("display", 800)
    T = demo_txt(b)
    up = p["name"].upper()
    return f"""<section class="ds-bloco" data-produto="{p['id']}" data-variante="alt" data-shot="{p['id']}-alt">
<div class="ds-wrap"><header class="ds-head" data-sub="alt" data-titulo="{E(p['name'])} · versão alternativa"
 data-tokens="data-variante=alt"><div><p class="ds-eyebrow">{E(p.get('tag') or '')} · versão alternativa</p>
<h2>{E(p['name'])}</h2></div><p class="ds-sub">data-produto="{p['id']}" data-variante="alt"</p></header>
<div class="ds-grid"><div class="ds-cel span3"><p class="ds-rot">Tarja</p>
<div class="tarja" style="font-size:{fit(up, 1000, 72, sd, -0.01)}px">{E(up)}</div></div>
<div class="ds-cel span3"><p class="ds-rot">Ação e status</p><div style="display:flex;flex-wrap:wrap;align-items:center;gap:20px 32px">
<a class="btn{T['btn_cls']}" href="#">{E(T["cta"])}</a><a class="btn{T['btn_cls']} is-foco" href="#">{E(T["cta"])}</a>
<span class="chip live"><span class="ponto" aria-hidden="true"></span>Ao vivo</span><a class="link" href="#">{E(T["link"])}</a>
</div></div></div></div></section>"""


def shape_section(b, shp):
    def px(v):
        return "pílula" if v >= PILL else f"{v} px"
    esc = "".join(f'<div class="esc"><div class="am" style="border-radius:var(--radius-{k})"></div><b>radius-{k} · '
                  f'{STEP_NAMES[k]}</b><span>site {px(shp["site"][k])} · arte {px(shp["arte"][k])}</span>'
                  + (f'<span>arte {shp["arte"][k]} vira ≈ {shp["arte"][k] / ARTE_POR_SITE:.0f} px no celular</span>'
                     if 0 < shp["arte"][k] < PILL else "") + "</div>" for k in ("none", "sm", "md", "lg", "full"))
    paps = []
    for k, p in shp["papeis"].items():
        sv = "/".join(str(x) for x in p["cantos_site"]) + " px" if p["cantos_site"] else px(p["site"])
        av = "/".join(str(x) for x in p["cantos_arte"]) if p["cantos_arte"] else px(p["arte"])
        q = " q" if p["circulo"] or k == "avatar" else ""
        paps.append(f'<div class="pap" data-sub="papeis-{len(paps) // 8}" data-titulo="Papéis de raio" data-tokens="--radius-*"><div class="am{q}" style="border-radius:var(--radius-{k})"></div>'
                    f'<b>radius-{E(k)}</b><span>{E(p["passo"] or "calculado")} · site {E(sv)} · arte {E(av)}</span>'
                    f'<span class="nota">{E(p["nota"])}</span></div>')
    nunca = "".join(f"<li>{E(x)}</li>" for x in never_round_labels(shp))
    head = E(shp["regra"]) if shp["regra"] else "Raios por papel."
    meta = " · ".join(x for x in (f"combinação {shp['combo']}" if shp.get("combo") else "", shp.get("status") or "",
                                  "derivado de shape.radius (marca antiga)" if shp["legado"] else "") if x)
    return f"""<section class="ds-sec" data-shot="forma"><div class="ds-wrap"><h2 data-sub="regra" data-titulo="Forma · a regra">Forma</h2>
<p class="ds-regra" data-sub="regra"><b>{head}</b>{(' <span class="ds-nota" style="display:block">' + E(meta) + '</span>') if meta else ''}</p>
<p class="ds-rot" data-sub="escala" data-titulo="Escala de raios (primitivos)" data-tokens="--radius-none, --radius-sm, --radius-md, --radius-lg, --radius-full">Escala (primitivos) — o componente nunca usa direto</p><div class="escala" data-sub="escala">{esc}</div>
<p class="ds-rot" data-sub="papeis-0" data-titulo="Papéis de raio" data-tokens="--radius-*">Papéis — o que os componentes usam</p><div class="papeis">{"".join(paps)}</div>
{('<p class="ds-rot" data-sub="nunca" data-titulo="Nunca arredonda">Nunca arredonda</p><ul class="nunca" data-sub="nunca">' + nunca + '</ul>') if nunca else ''}
<p class="ds-nota" data-sub="nunca">Aninhado: filho = pai − (borda + espaço), nunca negativo — espaço ≥ raio dá 0 (reto dentro de redondo é a
conta certa). Por peça: 1 valor da família + 0 + pílula/círculo, no máximo 3 formas. Pílula = 9999 px, nunca 50 %.</p>
</div></section>"""


def side_by_side(b, prods):
    """As cores dos produtos lado a lado e a MESMA faixa vista em P&B e com daltonismo (filtros feColorMatrix em RGB
    linear, Machado 2009) — a cor ajuda a achar, o texto confirma (WCAG 1.4.1)."""
    n = len(prods)
    sd = b.font_spec("display", 800)
    colw = (1104 - 12 * (n - 1)) / n - 32
    names = [(p.get("color_name") or p.get("tag") or p["name"]).split("·")[0].strip() for p in prods]
    tpx = min([fit(x.upper(), colw - 24, 26, sd) for x in names] + [26])
    cols = "".join(
        f'<div class="fx" data-produto="{p["id"]}"><div class="fx-tarja" style="font-size:{tpx}px">{E(nm)}</div>'
        f'<span class="chip live" style="align-self:flex-start"><span class="ponto" aria-hidden="true"></span>Ao vivo</span>'
        f'<p class="fx-rot">{E(p.get("label") or p["name"])}</p></div>' for p, nm in zip(prods, names))
    rows = "".join(f'<p class="faixa-rot" data-sub="faixa-{k}" data-titulo="Visão: {E(t)}" data-tokens="--color-accent, --color-live">{E(t)}</p>'
                   f'<div class="faixa" data-sub="faixa-{k}" style="grid-template-columns:repeat({n},minmax(0,1fr))'
                   + (f';filter:url(#cvd-{k})' if k != "normal" else "") + f'" aria-hidden="{str(k != "normal").lower()}">'
                   f'{cols}</div>' for k, t in (("normal", "visão normal"), ("pb", "preto e branco (mesma luminância)"),
                                                  ("deutan", "deuteranopia (simulação Machado 2009)"),
                                                  ("protan", "protanopia (simulação Machado 2009)")))
    cvd = color_pairs_cvd({nm: p["colors"]["accent"] for p, nm in zip(prods, names)})
    bad = [r for r in cvd if r["confunde"]]
    alert = ("".join(f'<p class="alerta" data-sub="alertas" data-titulo="Pares que confundem"><b>Par confunde: {E(r["a"])} × {E(r["b"])}</b> — '
                     + ", ".join({"deutan": f"deuteranopia ΔE {r['deutan']:.1f}".replace(".", ","),
                                  "protan": f"protanopia ΔE {r['protan']:.1f}".replace(".", ","),
                                  "tritan": f"tritanopia ΔE {r['tritan']:.1f}".replace(".", ","),
                                  "normal": f"visão normal ΔE {r['normal']:.1f}".replace(".", ","),
                                  "pb": f"P&B (contraste entre elas {fmt_ratio(r['luz'])})"}[k] for k in r["confunde"])
                     + ". Sempre o rótulo escrito junto da cor; nunca uma encostada na outra sem texto.</p>" for r in bad)
             if bad else '<p class="alerta" data-sub="alertas" data-titulo="Pares que confundem">Nenhum par abaixo de ΔE2000 10 em nenhuma das visões simuladas.</p>')
    nome_nota = ""
    if any("proposta" in (p.get("color_name_status") or "").lower() for p in prods):
        nome_nota = " Os nomes das cores são PROPOSTA: aguardam o sim da cliente."
    return f"""<section class="ds-sec" data-shot="lado-a-lado"><div class="ds-wrap"><h2 data-sub="cabecalho" data-titulo="As {n} cores lado a lado">As {n} cores lado a lado</h2>
<p class="ds-regra" data-sub="cabecalho">A mesma faixa vista em preto e branco e com daltonismo. A cor ajuda a achar; o rótulo escrito confirma
(WCAG 1.4.1: a cor nunca é o único sinal).{nome_nota}</p>{rows}{alert}</div></section>"""


def footer_block(b):
    off = b.get("official") or {}
    legal = b.get("legal") or {}
    canais = [("Instagram", "instagram"), ("WhatsApp", "whatsapp"), ("Site", "site"), ("E-mail", "email")]
    cells = "".join(f'<div><dt>{n}</dt><dd>{_adef(a_definir(off.get(k), f"official.{k}"))}</dd></div>'
                    for n, k in canais)
    never = [x for x in (off.get("never") or []) if not vazio(x)]
    never_html = ("<b>Nunca pedimos:</b> " + " · ".join(E(x) for x in never)) if never else \
        f'<b>Nunca pedimos:</b> {_adef(a_definir(None, "official.never"))}'
    st = (legal.get("trademark_status") or "").strip().lower()
    marca = (b.get("name") or "") + ("®" if st == "concedido" else "")
    titular = _adef(a_definir(legal.get("titular"), "legal.titular"))
    cnpj = _adef(a_definir(legal.get("cnpj"), "legal.cnpj"))
    reg = ("marca registrada (®)" if st == "concedido" else
           "registro de marca: " + (E(legal.get("trademark_status")) if not vazio(legal.get("trademark_status"))
                                    else _adef(a_definir(None, "legal.trademark_status"))) + " — sem ®")
    return f"""<footer class="rodape" data-shot="rodape"><div class="ds-wrap"><p class="ds-rot">Rodapé · canais oficiais</p>
<dl class="cols">{cells}</dl><p class="legal">{never_html}</p>
<p class="legal">© {E(marca)} · {titular} · CNPJ {cnpj} · {reg}.</p></div></footer>"""


def _adef(v):
    return f'<span class="adef">{A_DEFINIR}</span>' if v == A_DEFINIR else E(str(v))


def demo_html(b, css, shp, prods=()):
    pal = b.get("color.palette") or {}
    ramps = pal.get("ramps") or {}
    seeds = b.get("color.seeds") or {}
    faces, names = brand_font_faces(b)
    fams = "".join(f"--font-family-{r}:{n},{'ui-monospace,monospace' if r == 'mono' else 'system-ui,sans-serif'};"
                   for r, n in names.items())
    plat = b.get("platform") or {}
    idea = plat.get("idea") or b.name
    lv = b.get("type.levels") or {}
    body_s = "Texto que explica com calma: 0123456789 · R$ · 20h30 · ação, coração, você."
    tipo = "".join(f'<div class="ds-tipo-l"><span class="rot">{E(n)} · {l["size"]:g} px / '
                   f'{str(l["line_height"]).replace(".", ",")}</span>'
                   f'<p class="t-{n}">{E(idea if l["role"] == "display" else body_s)}</p></div>'
                   for n, l in lv.items())
    sw = "".join(f'<div class="ramp"><b>{E(seeds.get(role, {}).get("name", role) if isinstance(seeds.get(role), dict) else role)}</b>' + "".join(
        f'<span style="background:var(--color-{role}-{s});color:{"#111" if contrast(v["hex"], "#111111") >= contrast(v["hex"], "#FFFFFF") else "#FFF"}">{s}</span>'
        for s, v in ramp.items()) + "</div>" for role, ramp in ramps.items())
    pcards = "".join(
        f'<div class="ds-prod" data-produto="{p["id"]}"><b>{E(product_label(p))}</b><div class="cores">' +
        "".join(f'<span><i style="background:var(--color-{k})"></i>{lab}<b>{v}</b></span>'
                for k, v, lab in (("bg", p["colors"]["bg"], "fundo"), ("ink", p["colors"]["ink"], "texto"),
                                  ("accent", p["colors"]["accent"], "destaque"),
                                  ("on-accent", p["colors"]["on_accent"], "sobre o destaque"),
                                  ("live", ctx_colors(b, p["colors"], _extra(p))["live"], "ao vivo"),
                                  ("error", ctx_colors(b, p["colors"], _extra(p))["error"], "erro"))) + "</div></div>"
        for p in prods)
    mae = "marca-mãe" if prods else "marca"
    fs_mae = ctx_colors(b, mode_context(b, demo_theme(b)))["btn_fs"] or (16 if demo_txt(b)["btn_cls"] else 15)
    blocks = comp_block(b, "marca", b.name, mae, idea, "", tag=mae, fs=fs_mae)
    for p in prods:
        fs = ctx_colors(b, p["colors"], _extra(p))["btn_fs"] or (16 if demo_txt(b)["btn_cls"] else 15)
        blocks += comp_block(b, p["id"], p["name"], " · ".join(x for x in (f"produto {p.get('order', '')}".strip(),
                                                                           p.get("tag")) if x),
                             p.get("sub") or "", f'data-produto="{p["id"]}"',
                             p.get("order") if isinstance(p.get("order"), int) else None, p.get("tag") or "",
                             p.get("label") or "", fs, completo=False)
        if p["colors"].get("alt"):
            blocks += alt_block(b, p)
    rule = b.get("products_rule") or ""
    theme = demo_theme(b)
    return f"""<!doctype html><html lang="pt-BR"{' data-theme="dark"' if theme == 'dark' else ''}><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(b.name)} · design system</title>
<style>{faces}
{css}
:root{{{fams}}}
{DEMO_CSS}</style></head><body>{svg_cvd_filters()}
<header class="ds-topo" data-shot="topo"><div class="ds-wrap"><p class="ds-eyebrow">Design system · {E(b.name)}</p>
<h1 class="t-display">{E(idea)}</h1><p class="t-lead">Página gerada a partir de tokens.css. Os componentes usam só as
variáveis de contexto (<code>--color-bg</code>, <code>--color-ink</code>, <code>--color-accent</code>,
<code>--color-on-accent</code>, <code>--color-error</code>, <code>--color-live</code>, <code>--color-focus</code>) e os
PAPÉIS de raio (<code>--radius-button</code>, <code>--radius-card</code>…){'; cada produto troca as cores com <code>data-produto</code>' if prods else ''}.</p>
<button class="btn" type="button" aria-pressed="{str(theme == 'dark').lower()}" onclick="var h=document.documentElement,d=h.dataset.theme==='dark';
h.dataset.theme=d?'light':'dark';this.setAttribute('aria-pressed',String(!d))">Alternar modo claro/escuro</button></div></header>
<main>
<section class="ds-sec" data-shot="tipografia"><div class="ds-wrap"><h2>Escala tipográfica</h2>{tipo}</div></section>
<section class="ds-sec" data-shot="paleta"><div class="ds-wrap"><h2 data-sub="rampas" data-titulo="Paleta · escalas de tom" data-tokens="--color-*-50 … 950">Paleta</h2><div data-sub="rampas">{sw}</div>
{('<p class="ds-rot" data-sub="produtos" data-titulo="Cores por produto" data-tokens="[data-produto]" style="margin-top:48px">Produtos</p>' + ('<p class="ds-regra" data-sub="produtos">' + E(rule) + '</p>' if rule else '') + '<div class="ds-prods" data-sub="produtos">' + pcards + '</div>') if prods else ''}
</div></section>
{shape_section(b, shp)}
{side_by_side(b, prods) if len(prods) > 1 else ''}
{blocks}
</main>{footer_block(b)}</body></html>"""


def demo_theme(b):
    """brand.json demo.tema = "dark" abre a demo no modo escuro (marca que vive no preto: ouro sobre papel falha)."""
    return "dark" if str((b.get("demo") or {}).get("tema", "")).lower() in ("dark", "escuro") else "light"


JS_QA = """() => {
  const out = [], seen = new Set();
  const shot = el => (el.closest('[data-shot]') || {dataset: {shot: '?'}}).dataset.shot;
  document.querySelectorAll('.ds-cel, .evento, .val, .tarja, .cartao, .pilula, .btn, .chip, .campo input, .ds-head h2, ' +
                            '.fx-tarja, .msg, .rodape dd')
    .forEach(el => { if (el.scrollWidth > el.clientWidth + 1) out.push(shot(el) + ': .' + el.className.split(' ')[0] +
      ' estoura ' + (el.scrollWidth - el.clientWidth) + ' px'); });
  document.querySelectorAll('.ds-cel, .evento, .fx').forEach(c => { const r = c.getBoundingClientRect();
    c.querySelectorAll('*').forEach(k => { const q = k.getBoundingClientRect();
      if (q.width && (q.right > r.right + 1 || q.left < r.left - 1)) { const m = shot(c) + ': ' + k.tagName.toLowerCase() +
        '.' + (k.className || '') + ' sai da caixa'; if (!seen.has(m)) { seen.add(m); out.push(m); } } }); });
  document.querySelectorAll('.btn').forEach(bt => { const h = bt.getBoundingClientRect().height;
    if (h && h < 40 - 0.5) out.push(shot(bt) + ': botão com ' + h.toFixed(0) + ' px de altura (< 40)'); });
  ['brand-display', 'brand-text'].forEach(f => { if (!document.fonts.check('16px ' + f)) out.push('fonte não carregou: ' + f); });
  return out;
}"""


JS_SUBS = """() => {
  const out = [];
  document.querySelectorAll('[data-shot]').forEach(sec => {
    const shot = sec.dataset.shot;
    const prod = (sec.dataset.produto || '');
    const groups = new Map();
    sec.querySelectorAll('[data-sub]').forEach(el => {
      const k = el.dataset.sub;
      if (!groups.has(k)) groups.set(k, {sub: k, els: [], titulo: '', tokens: '', resumo: true});
      const g = groups.get(k);
      g.els.push(el);
      if (el.dataset.titulo && !g.titulo) g.titulo = el.dataset.titulo;
      if (el.dataset.tokens && !g.tokens) g.tokens = el.dataset.tokens;
      if (el.dataset.resumo === 'nao') g.resumo = false;
    });
    const subs = [];
    groups.forEach(g => {
      let l = 1e9, t = 1e9, r = -1e9, bt = -1e9;
      g.els.forEach(e => { const q = e.getBoundingClientRect();
        l = Math.min(l, q.left + scrollX); t = Math.min(t, q.top + scrollY);
        r = Math.max(r, q.right + scrollX); bt = Math.max(bt, q.bottom + scrollY); });
      const S = sec.getBoundingClientRect(), AIR = 16;   // um respiro dentro da própria seção (mesmo fundo)
      l = Math.max(S.left + scrollX, l - AIR); r = Math.min(S.right + scrollX, r + AIR);
      t = Math.max(S.top + scrollY, t - AIR); bt = Math.min(S.bottom + scrollY, bt + AIR);
      subs.push({sub: g.sub, titulo: g.titulo, tokens: g.tokens, resumo: g.resumo, x: l, y: t, w: r - l, h: bt - t});
    });
    out.push({shot, produto: prod, subs});
  });
  return out;
}"""


def render_demo(html_path, png, sec_dir):
    """demo.html → demo.png (página inteira, 1280 px, movimento reduzido) + PNGs 2× em sec_dir: um por pedaço
    marcado com data-sub (legíveis em tamanho real no manual) ou, sem data-sub, um por bloco data-shot; mais
    blocos.json (arquivo, título, tokens usados). Devolve os avisos do verificador (texto estourando a caixa,
    botão baixo, fonte que não carregou)."""
    import glob
    from playwright.sync_api import sync_playwright
    os.makedirs(sec_dir, exist_ok=True)
    for old in glob.glob(os.path.join(sec_dir, "*.png")) + glob.glob(os.path.join(sec_dir, "blocos.json")):
        os.remove(old)
    url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome", headless=True)
        pg = br.new_page(viewport={"width": DEMO_W, "height": 900}, device_scale_factor=1, reduced_motion="reduce")
        pg.goto(url, wait_until="load")
        pg.evaluate("document.fonts.ready.then(() => true)")
        avisos = pg.evaluate(JS_QA)
        pg.screenshot(path=png, full_page=True)
        pg.close()
        pg = br.new_page(viewport={"width": DEMO_W, "height": 900}, device_scale_factor=2, reduced_motion="reduce")
        pg.goto(url, wait_until="load")
        pg.evaluate("document.fonts.ready.then(() => true)")
        info = pg.evaluate(JS_SUBS)
        shots = pg.query_selector_all("[data-shot]")
        meta, n = [], 0
        for el, inf in zip(shots, info):
            n += 1
            if not inf["subs"]:
                f = f"{n:02d}-{inf['shot']}.png"
                el.screenshot(path=os.path.join(sec_dir, f))
                meta.append({"file": f, "shot": inf["shot"], "produto": inf["produto"], "sub": "", "titulo": "",
                             "tokens": "", "resumo": True})
                continue
            for j, sb in enumerate(inf["subs"], 1):
                f = f"{n:02d}-{inf['shot']}--{j}-{re.sub(r'[^a-z0-9-]', '', sb['sub'])}.png"
                pg.screenshot(path=os.path.join(sec_dir, f), full_page=True,
                              clip={"x": sb["x"], "y": sb["y"], "width": sb["w"], "height": sb["h"]})
                meta.append({"file": f, "shot": inf["shot"], "produto": inf["produto"], "sub": sb["sub"],
                             "titulo": sb["titulo"], "tokens": sb["tokens"], "resumo": sb["resumo"]})
        br.close()
    with open(os.path.join(sec_dir, "blocos.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    return avisos


def cmd_build(a):
    b = load_brand(a.brand)
    if not b.get("color.palette"):
        raise SystemExit("rode antes: python palette.py build <dir>")
    out = os.path.join(b.dir, "tokens")
    shp = shape_spec(b)
    core = build_core(b, shp)
    light, dark = build_mode(b, "light"), build_mode(b, "dark")
    prods = products(b)
    dump = lambda x: json.dumps(x, ensure_ascii=False, indent=2) + "\n"  # noqa: E731
    write(os.path.join(out, "core.tokens.json"), dump(core))
    write(os.path.join(out, "light.tokens.json"), dump(light))
    write(os.path.join(out, "dark.tokens.json"), dump(dark))
    allt = {"core": core, "light": light, "dark": dark}
    ptree = build_products(b, prods) if prods else None
    if ptree:
        write(os.path.join(out, "products.tokens.json"), dump(ptree))
        allt["products"] = ptree
    write(os.path.join(out, "tokens.json"), dump(allt))
    css = to_css(b, core, light, dark, prods)
    write(os.path.join(out, "tokens.css"), css)
    write(os.path.join(out, "tailwind.css"), to_tailwind(core, light))
    write(os.path.join(out, "figma", "light.tokens.json"), dump(to_figma(core, light)))
    write(os.path.join(out, "figma", "dark.tokens.json"), dump(to_figma(core, dark)))
    for p in prods:   # um arquivo = um modo da coleção "produto" no Figma (mesmos nomes em todos)
        for suf, c, alt in (("", p["colors"], False), ("-alt", p["colors"].get("alt"), True)):
            if c:
                cc = ctx_colors(b, c, _extra(p, alt))
                tree = {"produto": {k: {"$type": "color", "$value": col(v)} for k, v in (
                    ("bg", c["bg"]), ("ink", c["ink"]), ("accent", c["accent"]), ("on-accent", c["on_accent"]),
                    ("error", cc["error"]), ("live", cc["live"]), ("focus", cc["focus"]))}}
                write(os.path.join(out, "figma", f"produto-{p['id']}{suf}.tokens.json"), dump(tree))
    write(os.path.join(b.dir, "DESIGN.md"), design_md(b, core, shp, prods))
    demo = os.path.join(out, "demo.html")
    write(demo, demo_html(b, css, shp, prods))
    n = sum(1 for _ in flat(core))
    print(f"ok → {out}: {n} tokens base + {len(light['role']) - 1} papéis de cor × 2 modos; tokens.css, tailwind.css, "
          f"figma/, demo.html, ../DESIGN.md")
    print(f"forma: {len(shp['papeis'])} papéis de raio" + (" (derivados de shape.radius — marca antiga)" if shp["legado"]
                                                          else f" · site {shp['site']} · arte {shp['arte']}"))
    if not shp["legado"]:
        for k in shp["nunca_arredonda"]:
            p = shp["papeis"].get(k)
            if p and p["site"] != 0:
                print(f"  aviso forma: '{k}' está em nunca_arredonda mas o papel tem raio {p['site']} px")
    if prods:
        print(f"produtos: {len(prods)} ({', '.join(p['id'] for p in prods)}) → products.tokens.json, "
              f"[data-produto] no tokens.css, figma/produto-*.tokens.json, seção Produtos no DESIGN.md")
        for p in prods:
            for alt, c in ((False, p["colors"]), (True, p["colors"].get("alt"))):
                for pr in product_pairs(c) if c else []:
                    if not pr["ok"]:
                        if pr["par"] == "botão":
                            dica = ("texto do botão ≥ 18,7 px negrito (texto grande WCAG; a demo já usa 19 px "
                                    "nesse produto), ou troque on_accent" if pr["ratio"] >= 3
                                    else "troque on_accent (ilegível)")
                        elif pr["par"] == "texto":
                            dica = ("só título grande (≥ 24 px ou 18,7 px negrito); texto corrido em outra cor"
                                    if pr["ratio"] >= 3 else "troque ink (ilegível)")
                        else:
                            dica = "destaque some no fundo: não usar em ícone/gráfico/título sobre esse bg"
                        print(f"  aviso: {product_label(p, alt)} · {pr['par']} {pr['fg']} sobre {pr['bg']} = "
                              f"{fmt_ratio(pr['ratio'])} < {fmt_ratio(pr['need'])} ({pr['uso']}) → {dica}")
                if c:
                    cc = ctx_colors(b, c, _extra(p, alt))
                    if cc["error_surface"]:
                        print(f"  aviso: {product_label(p, alt)} · {cc['error_note']}")
        cvd = color_pairs_cvd({p.get("color_name") or p["name"]: p["colors"]["accent"] for p in prods})
        br = lambda x: f"{x:.1f}".replace(".", ",")  # noqa: E731
        for r in cvd:
            if r["confunde"]:
                vis = {"pb": "P&B", "deutan": "deuteranopia", "protan": "protanopia", "tritan": "tritanopia",
                       "normal": "visão normal"}
                print(f"  aviso cor: {r['a']} × {r['b']} confundem em {', '.join(vis[k] for k in r['confunde'])} (deutan ΔE "
                      f"{br(r['deutan'])}, protan {br(r['protan'])}, contraste entre elas {fmt_ratio(r['luz'])}) → "
                      f"rótulo escrito sempre junto da cor")
        if not error_cfg(b):
            print("  dica: brand.json color.error {\"escuro\": …, \"papel\": …} separa o erro das cores de produto "
                  "(17c §5.1)")
    if not a.no_png:
        try:
            avisos = render_demo(demo, os.path.join(out, "demo.png"), os.path.join(out, "demo"))
            print(f"demo: {os.path.join(out, 'demo.png')} + blocos em {os.path.join(out, 'demo')}")
            for x in avisos:
                print(f"  aviso demo: {x}")
            if not avisos:
                print("  verificador da demo: nada estourando, botões ≥ 40 px, fontes carregadas")
        except Exception as e:   # sem Playwright/Chrome: a demo.html continua válida
            print(f"  demo.png não gerado ({type(e).__name__}: {str(e)[:160]}) — abra tokens/demo.html no navegador")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("build"); p.add_argument("brand")
    p.add_argument("--no-png", action="store_true", help="não renderiza demo.png (só o HTML)")
    p.set_defaults(fn=cmd_build)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
