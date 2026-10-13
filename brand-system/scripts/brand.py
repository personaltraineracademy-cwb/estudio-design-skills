"""Brand project: scaffold, status and validation. brand.json is the single source of truth every script reads.

Usage:
  python brand.py init <dir> --name "Nome" [--client "Cliente"] [--mode antes|durante|depois]
  python brand.py status <dir>          # what is done / missing, in workflow order
  python brand.py show <dir> [key]      # print brand.json (or one dotted key, e.g. platform.idea)

Modes: antes = system first, logo comes out of it · durante = logo and system together · depois = system derived
from an existing logo (run elements.py dna on it first).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import load_brand, slugify, write  # noqa: E402

TEMPLATE = {
    "name": "", "slug": "", "client": "", "status": "teste", "mode": "antes",
    "briefing": {"what": "", "audience": "", "promise": "", "touchpoints": [], "competitors": [], "references": [],
                 "must": [], "must_not": [], "assumptions": []},
    "platform": {
        "onlyness": "", "idea": "", "enemy": "",
        "zag": {"keep": "", "break": []},
        "tension": [], "personality": [],
        "principles": [], "jobs": {"funcional": "", "emocional": "", "social": ""},
        "assets": [],
        "voice": {"is": [], "is_not": [], "examples": []}
    },
    "logo": {"primary": "", "vertical": "", "symbol": "", "wordmark": "", "clearspace": 0.5, "min_px": 24,
             "construction": "", "dont": []},
    "color": {"seeds": {}, "proportion": {"paper": 50, "ink": 30, "brand": 15, "accent": 5}, "rules": []},
    "type": {"display": {"family": "", "weight": 800, "use": "títulos"},
             "text": {"family": "", "weight": 400, "use": "texto corrido"},
             "scale": {"base": 16, "ratio": 1.25}, "tracking_display": -0.01, "rules": [], "custom": ""},
    "grid": {"columns": 12, "margin": 0.06, "gutter": 0.02, "baseline": 8, "angle": 0},
    "primitives": [], "devices": [], "patterns": [],
    "icons": {"base": "lucide", "stroke": 2, "cap": "square", "join": "miter", "grid": 24, "rules": []},
    "imagery": {"style": "", "treatment": "", "crop": "", "prompt_style": "", "dont": []},
    "texture": {"fx": [], "rule": ""},
    "motion": {"principles": [], "easing": {"standard": [0.2, 0, 0, 1], "enter": [0, 0, 0, 1], "exit": [0.3, 0, 1, 1]},
               "durations": {"fast": 120, "base": 240, "slow": 480}},
    "applications": []
}

BRIEF_MD = """# Briefing — {name}

Cliente: {client} · Modo: {mode} · Status: teste

## O que é / para quem / promessa
-

## Onde vai viver (pontos de contato)
-

## Concorrentes e referências (amadas / odiadas)
-

## Obrigatório / proibido
-

## Suposições (quando a pessoa disse "decide você")
-
"""

PLATFORM_MD = """# Plataforma — {name}

**Frase de unicidade:** {name} é a única ___ que ___ para ___ em ___ que ___ numa era de ___.
(teste da troca: com o nome de um concorrente, a frase ainda é verdadeira? então reescreva)

**Ideia em uma frase (com verbo):**

**Inimigo (o que a marca recusa):**

**Zag:** mantém ___ (código de entrada da categoria) · quebra ___ e ___

**Tensões ("isso, mas não aquilo"):**
-

**Princípios de design (nome — regra mensurável — fazer/evitar — teste):**
1.

**Jobs:** funcional ___ · emocional ___ · social ___ (→ ativos de exibição: selo, certificado, moldura…)

**Ativos distintivos-alvo (≥ 2 reconhecíveis com o nome coberto):**
-
"""

STEPS = [
    ("briefing", lambda b: bool(b.get("briefing.what")), "preencha briefing.* (brand.json) e briefing.md"),
    ("pesquisa", lambda b: os.path.exists(os.path.join(b.dir, "pesquisa", "pesquisa.md")),
     "pesquisa/pesquisa.md — mapa de convenções, clichês, espaço vazio (references/pesquisa.md)"),
    ("plataforma", lambda b: bool(b.get("platform.idea")) and len(b.get("platform.principles") or []) >= 3,
     "platform.idea + ≥3 platform.principles (references/estrategia.md)"),
    ("arena", lambda b: os.path.exists(os.path.join(b.dir, "arena", "ranking.json")),
     "arena de territórios → arena/ranking.json (references/arena.md)"),
    ("logo", lambda b: bool(b.get("logo.primary")) and os.path.exists(b.path(b.get("logo.primary"))),
     "logo.primary → SVG (brand-studio / logo-design)"),
    ("cores", lambda b: bool(b.get("color.palette")), "python palette.py build <dir>"),
    ("tipografia", lambda b: bool(b.get("type.display.family")) and bool(b.get("type.text.family")),
     "type.display/type.text + python typesys.py build <dir>"),
    ("elementos", lambda b: len(b.get("devices") or []) + len(b.get("patterns") or []) >= 3
     and os.path.isdir(os.path.join(b.dir, "elementos")),
     "≥3 devices/patterns + python elements.py build <dir> (elementos feitos por código próprio → patterns[])"),
    ("tokens", lambda b: os.path.exists(os.path.join(b.dir, "tokens", "tokens.json")), "python tokens.py build <dir>"),
    ("aplicações", lambda b: os.path.isdir(os.path.join(b.dir, "aplicacoes")), "python apply.py build <dir>"),
    ("manual", lambda b: os.path.exists(os.path.join(b.dir, "manual", "manual.pdf")), "python manual.py build <dir>"),
]


def cmd_init(a):
    d = os.path.abspath(a.dir)
    if os.path.exists(os.path.join(d, "brand.json")):
        raise SystemExit(f"já existe: {d}\\brand.json")
    data = json.loads(json.dumps(TEMPLATE))
    data.update(name=a.name, slug=slugify(a.name), client=a.client or "", mode=a.mode)
    write(os.path.join(d, "brand.json"), json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    fmt = {"name": a.name, "client": a.client or "(novo)", "mode": a.mode}
    write(os.path.join(d, "briefing.md"), BRIEF_MD.format(**fmt))
    write(os.path.join(d, "plataforma.md"), PLATFORM_MD.format(**fmt))
    for sub in ("pesquisa", "referencias", "primitivas", "logo"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    print(f"projeto criado: {d}")
    cmd_status(a)


def cmd_status(a):
    b = load_brand(a.dir)
    print(f"{b.name} ({b.get('client') or 'cliente novo'}) · modo {b.get('mode')} · status {b.get('status')}")
    nxt = None
    for name, ok, how in STEPS:
        try:
            done = ok(b)
        except Exception:
            done = False
        print(f"  [{'x' if done else ' '}] {name}" + ("" if done else f"  → {how}"))
        if not done and nxt is None:
            nxt = name
    print(f"próximo: {nxt}" if nxt else "tudo feito — revise e entregue")


def cmd_show(a):
    b = load_brand(a.dir)
    v = b.get(a.key) if a.key else b.data
    print(json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (dict, list)) else v)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("dir"); p.add_argument("--name", required=True)
    p.add_argument("--client"); p.add_argument("--mode", default="antes", choices=["antes", "durante", "depois"])
    p.set_defaults(fn=cmd_init)
    p = sp.add_parser("status"); p.add_argument("dir"); p.set_defaults(fn=cmd_status)
    p = sp.add_parser("show"); p.add_argument("dir"); p.add_argument("key", nargs="?"); p.set_defaults(fn=cmd_show)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
