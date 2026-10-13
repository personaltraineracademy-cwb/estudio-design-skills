"""Creative arena: blind tournament between territories/concepts, judged by a panel of personas (Claude subagents +
optional Gemini), each pair judged in BOTH orders (position-bias control), ranked with Bradley-Terry + bootstrap CI.
Also reads the official arena.ai leaderboards (CC-BY dataset) to pick the best image/text models.

Usage:
  python arena.py add <arena_dir> --board territorio-a.png --desc "ideia em 2 linhas" [--name "A"] [--author persona]
  python arena.py pair <arena_dir> [--all]         # next Swiss round → arena/r<k>/m01-AB.png, m01-BA.png, juizes.md
                                                   # --all: every pair at once (round-robin; best for ≤ 6 territories)
                                                   # also writes arena/confrontos.md (each image + full-size boards)
  python arena.py vote <arena_dir> --round 1 --match m01 --order AB --judge diretor --json '<veredito JSON>'
  python arena.py vote <arena_dir> --file votos.json     # bulk: [{"round":1,"match":"m01","order":"AB","judge":..,...}]
  python arena.py gemini <arena_dir> [--round k]   # Gemini (other model family) judges every match of the round
  python arena.py rank <arena_dir>                 # → ranking.json + ranking.png (+ consistency, judge agreement)
  python arena.py modelos [--board text_to_image|image_edit|text|vision|text_to_video] [--top 12]

Verdict JSON a judge returns (reason first, verdict last):
  {"criteria": {"ideia": "A|B|tie", "propriedade": "...", "adequacao": "...", "sistema": "...", "craft": "...",
                "memoria": "..."}, "absoluto": {"A": 0-10, "B": 0-10}, "evidence": "...", "overall": "A|B|tie",
   "confidence": 1-3}
"absoluto" (optional, recommended) = absolute quality bar (10 = top-studio portfolio); rank prints the mean per
entrant and warns when the winner is < 7 — a relative ranking alone crowns the best of weak options.
"""
import argparse
import json
import math
import os
import random
import secrets
import shutil
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import UI_FONT_BOLD, font_path  # noqa: E402

CRITERIA = {"ideia": 0.25, "propriedade": 0.25, "adequacao": 0.15, "sistema": 0.15, "craft": 0.10, "memoria": 0.10}
CRIT_TEXT = {
    "ideia": "a ideia é não óbvia, cabe em 1 frase e gera o sistema inteiro (não é o ícone literal do setor)",
    "propriedade": "só poderia ser desta marca: passa no teste da troca, foge dos clichês do setor, nada genérico",
    "adequacao": "serve ao público e à promessa do briefing (e reposiciona, se possível)",
    "sistema": "gera padrões, layouts, movimento e 10 aplicações coerentes por regra, não por enfeite",
    "craft": "construção limpa, tipografia cuidada, contraste e leitura em tamanhos pequenos",
    "memoria": "alguém redesenharia de memória depois de ver 5 segundos; tem um gesto que fica",
}
PERSONAS = {
    "diretor": "Diretor(a) de criação sênior de estúdio de identidade (Pentagram/Collins). Julga ideia e coragem; "
               "odeia o óbvio, o genérico e o 'cara de IA'.",
    "estrategista": "Estrategista de marca. Julga adequação ao briefing, ao público e o potencial de diferenciação "
                    "na categoria (mapa de convenções).",
    "tipografo": "Tipógrafo(a) e designer de craft. Julga construção, tipografia, espaçamento, detalhes ópticos e "
                 "leitura em 16 px.",
    "sistema": "Designer de sistemas/produção. Julga se o território vira kit de partes: padrões, grids, motion, "
               "aplicações de verdade (story 9:16, favicon, uniforme, sinalização).",
    "publico": "Pessoa do público-alvo vendo por 5 segundos num feed. Diz o que lembra, o que sentiu e se pararia "
               "o scroll. Sem jargão.",
}
LEADER = "https://datasets-server.huggingface.co/rows?dataset=lmarena-ai/leaderboard-dataset&config={b}&split=latest" \
         "&offset={o}&length=100"
GEMINI_REACHABLE = ("gemini", "nano-banana", "imagen", "veo")


# ------------------------------------------------------------------ state
def state_path(d):
    return os.path.join(d, "arena.json")


def load(d):
    p = state_path(d)
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {"entrants": [], "rounds": []}


def save(d, st):
    os.makedirs(d, exist_ok=True)
    json.dump(st, open(state_path(d), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def votes(d):
    p = os.path.join(d, "votos.jsonl")
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


# ------------------------------------------------------------------ images
def _font(size):
    from PIL import ImageFont
    return ImageFont.truetype(font_path(UI_FONT_BOLD), size)


def fit_board(path, w=1200, h=900, bg=(217, 217, 214)):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((w, h))
    c = Image.new("RGB", (w, h), bg)
    c.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return c


def versus(left, right, out):
    from PIL import Image, ImageDraw
    a, b = fit_board(left), fit_board(right)
    W = a.width + b.width + 60
    im = Image.new("RGB", (W, a.height + 120), (245, 245, 242))
    im.paste(a, (20, 100))
    im.paste(b, (40 + a.width, 100))
    d = ImageDraw.Draw(im)
    f = _font(64)
    d.text((24, 14), "A", fill=(20, 20, 20), font=f)
    d.text((44 + a.width, 14), "B", fill=(20, 20, 20), font=f)
    im.save(out)


# ------------------------------------------------------------------ commands
def cmd_add(a):
    st = load(a.arena)
    code = secrets.token_hex(2)
    os.makedirs(os.path.join(a.arena, "boards"), exist_ok=True)
    dest = os.path.join(a.arena, "boards", code + os.path.splitext(a.board)[1].lower())
    shutil.copy2(a.board, dest)
    st["entrants"].append({"code": code, "name": a.name or code, "author": a.author or "", "desc": a.desc or "",
                           "board": os.path.relpath(dest, a.arena)})
    save(a.arena, st)
    print(f"inscrito {a.name or ''} como {code}")


def standings(st, vs):
    pts = {e["code"]: 0.0 for e in st["entrants"]}
    for m in outcomes(st, vs):
        if m["winner"]:
            pts[m["winner"]] += 1
        else:
            pts[m["a"]] += 0.5
            pts[m["b"]] += 0.5
    return pts


def cmd_pair(a):
    st = load(a.arena)
    codes = [e["code"] for e in st["entrants"]]
    if len(codes) < 2:
        raise SystemExit("inscreva ao menos 2 territórios (arena.py add)")
    played = {frozenset((m["a"], m["b"])) for r in st["rounds"] for m in r["matches"]}
    pts = standings(st, votes(a.arena))
    rnd = random.Random(len(st["rounds"]) + 11)
    order = sorted(codes, key=lambda c: (-pts[c], rnd.random()))
    matches, used = [], set()
    if getattr(a, "all", False):   # round-robin: every pair not met yet, in one round
        from itertools import combinations
        for x, y in combinations(order, 2):
            if frozenset((x, y)) not in played:
                x, y = (x, y) if rnd.random() < 0.5 else (y, x)
                matches.append({"id": f"m{len(matches) + 1:02d}", "a": x, "b": y})
        if not matches:
            raise SystemExit("todos os pares já se enfrentaram")
    for c in ([] if matches else order):   # Swiss: pair with the closest-scored opponent not met yet
        if c in used:
            continue
        opp = next((o for o in order if o != c and o not in used and frozenset((c, o)) not in played), None)
        if opp is None:
            opp = next((o for o in order if o != c and o not in used), None)
        if opp is None:
            print(f"folga nesta rodada: {c}")
            used.add(c)
            continue
        used.update((c, opp))
        matches.append({"id": f"m{len(matches) + 1:02d}", "a": c, "b": opp})
    k = len(st["rounds"]) + 1
    rd = os.path.join(a.arena, f"r{k}")
    os.makedirs(rd, exist_ok=True)
    board = {e["code"]: os.path.join(a.arena, e["board"]) for e in st["entrants"]}
    desc = {e["code"]: e["desc"] for e in st["entrants"]}
    lines = []
    for m in matches:
        versus(board[m["a"]], board[m["b"]], os.path.join(rd, f"{m['id']}-AB.png"))
        versus(board[m["b"]], board[m["a"]], os.path.join(rd, f"{m['id']}-BA.png"))
        lines.append(f"- {m['id']}: `r{k}/{m['id']}-AB.png` (A: {desc[m['a']]} | B: {desc[m['b']]})\n"
                     f"         `r{k}/{m['id']}-BA.png` (A: {desc[m['b']]} | B: {desc[m['a']]})")
    st["rounds"].append({"k": k, "matches": matches})
    save(a.arena, st)
    write_brief(a.arena, k, lines)
    write_confrontos(a.arena, st)
    print(f"rodada {k}: {len(matches)} confrontos → {rd}  (brief dos juízes: {rd}\\juizes.md)")


def write_confrontos(d, st):
    """One list of every image the judges must open, with the full-size boards (blind: boards are named by code)."""
    board = {e["code"]: os.path.abspath(os.path.join(d, e["board"])) for e in st["entrants"]}
    L = ["# Confrontos — abra a imagem; para detalhe, abra também os boards cheios (A = esquerda, B = direita)", ""]
    for r in st["rounds"]:
        for m in r["matches"]:
            for o in ("AB", "BA"):
                left, right = (m["a"], m["b"]) if o == "AB" else (m["b"], m["a"])
                img = os.path.abspath(os.path.join(d, f"r{r['k']}", f"{m['id']}-{o}.png"))
                L += [f"- round {r['k']} · match {m['id']} · order {o}: imagem `{img}`",
                      f"    - A (esquerda, cheio): `{board[left]}`", f"    - B (direita, cheio): `{board[right]}`"]
    with open(os.path.join(d, "confrontos.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def write_brief(d, k, lines):
    brief = ""
    bj = os.path.join(os.path.dirname(os.path.abspath(d)), "brand.json")
    if os.path.exists(bj):
        b = json.load(open(bj, encoding="utf-8"))
        brief = (f"Marca: {b.get('name')}. Briefing: {json.dumps(b.get('briefing', {}), ensure_ascii=False)}\n"
                 f"Plataforma: {json.dumps({k2: b.get('platform', {}).get(k2) for k2 in ('idea', 'onlyness', 'tension', 'principles')}, ensure_ascii=False)}")
    crit = "\n".join(f"  - {c} (peso {w:.0%}): {CRIT_TEXT[c]}" for c, w in CRITERIA.items())
    per = "\n".join(f"  - `{k2}`: {v}" for k2, v in PERSONAS.items())
    txt = f"""# Arena — rodada {k}: instruções para os juízes

Cada juiz é um subagente com UMA persona. Ele abre cada imagem (Read), compara A e B e devolve só JSON.
Os mesmos dois territórios aparecem nas duas ordens (AB e BA): julgue cada imagem de forma independente.

## Contexto do projeto
{brief or "(sem brand.json ao lado da pasta da arena — descreva o briefing no prompt do juiz)"}

## Personas
{per}

## Critérios (compare A × B em cada um)
{crit}

## Regras
- Raciocine primeiro, veredito no fim. Cite evidência visível (onde, qual elemento).
- Ignore a ordem (A/B), o acabamento de apresentação, a riqueza de cor e a quantidade de texto.
- Penalize clichê do setor e "cara de IA" (gradientes genéricos, fontes padrão, ícones literais, pílulas e cards iguais).
- Se forem equivalentes num critério, responda "tie". Confiança: 1 (dúvida) a 3 (claro).

## Saída (um JSON por imagem)
{{"criteria": {{"ideia": "A|B|tie", "propriedade": "...", "adequacao": "...", "sistema": "...", "craft": "...", "memoria": "..."}},
 "absoluto": {{"A": 0, "B": 0}}, "evidence": "frases curtas com evidência", "overall": "A|B|tie", "confidence": 1}}
"absoluto" = nota de 0 a 10 para cada lado, sem comparar (10 = portfólio de estúdio top, pararia o scroll; 5 = competente
e esquecível; 0 = amador).

## Confrontos
{chr(10).join(lines)}

Registrar: `python arena.py vote <arena> --round {k} --match m01 --order AB --judge <persona> --json '<JSON>'`
"""
    with open(os.path.join(d, f"r{k}", "juizes.md"), "w", encoding="utf-8") as fh:
        fh.write(txt)


def cmd_vote(a):
    rows = []
    if a.file:
        rows = json.load(open(a.file, encoding="utf-8"))
    else:
        v = json.loads(a.json)
        v.update(round=a.round, match=a.match, order=a.order.upper(), judge=a.judge)
        rows = [v]
    with open(os.path.join(a.arena, "votos.jsonl"), "a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} voto(s) registrado(s)")


def cmd_gemini(a):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                    "brand-studio", "scripts"))
    import gemini
    st = load(a.arena)
    k = a.round or len(st["rounds"])
    rd = os.path.join(a.arena, f"r{k}")
    brief = open(os.path.join(rd, "juizes.md"), encoding="utf-8").read().split("## Confrontos")[0]
    rnd = next(r for r in st["rounds"] if r["k"] == k)
    n = 0
    for m in rnd["matches"]:
        for order in ("AB", "BA"):
            img = os.path.join(rd, f"{m['id']}-{order}.png")
            text, mid = gemini.ask("Compare A (esquerda) e B (direita). Responda só o JSON pedido.", [img],
                                   system=brief + "\nPersona: diretor(a) de criação independente.", model=a.model,
                                   as_json=True, temperature=0.2)
            try:
                v = json.loads(text[text.find("{"): text.rfind("}") + 1])
            except Exception:
                print(f"  {m['id']}-{order}: resposta não-JSON, ignorada")
                continue
            v.update(round=k, match=m["id"], order=order, judge=f"gemini:{mid}")
            with open(os.path.join(a.arena, "votos.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(v, ensure_ascii=False) + "\n")
            n += 1
    print(f"gemini: {n} vereditos")


# ------------------------------------------------------------------ scoring
def share_left(v):
    """Fraction (0..1) of the weighted criteria won by the LEFT image of that order."""
    cr = v.get("criteria") or {}
    if cr:
        s = 0.0
        for c, w in CRITERIA.items():
            x = str(cr.get(c, "tie")).strip().upper()
            s += w * (1.0 if x == "A" else 0.0 if x == "B" else 0.5)
        return s / sum(CRITERIA.values())
    x = str(v.get("overall", "tie")).strip().upper()
    return 1.0 if x == "A" else 0.0 if x == "B" else 0.5


def outcomes(st, vs):
    """One outcome per (round, match, judge): both orders combined → winner code or None (tie)."""
    idx = {(r["k"], m["id"]): m for r in st["rounds"] for m in r["matches"]}
    groups = {}
    for v in vs:
        key = (int(v["round"]), v["match"], v["judge"])
        groups.setdefault(key, {})[v["order"]] = v
    out = []
    for (k, mid, judge), by in groups.items():
        m = idx.get((k, mid))
        if not m:
            continue
        sa = []   # share for entrant a
        if "AB" in by:
            sa.append(share_left(by["AB"]))
        if "BA" in by:
            sa.append(1 - share_left(by["BA"]))
        s = sum(sa) / len(sa)
        consistent = len(sa) == 2 and ((sa[0] - 0.5) * (sa[1] - 0.5) > 0)
        if len(sa) == 2 and not consistent:
            winner = None
        else:
            winner = m["a"] if s > 0.55 else m["b"] if s < 0.45 else None
        out.append({"round": k, "match": mid, "judge": judge, "a": m["a"], "b": m["b"], "share_a": round(s, 3),
                    "winner": winner, "orders": len(sa), "consistent": consistent})
    return out


def bradley_terry(codes, obs, iters=300, prior=0.5):
    """obs: [(i, j, result)] result 1 = i wins, 0.5 tie. MM algorithm with a weak prior (virtual ties)."""
    p = {c: 1.0 for c in codes}
    pairs = list(obs)
    wins = {c: 0.0 for c in codes}
    n = {}
    for i, j, r in pairs:
        wins[i] += r
        wins[j] += 1 - r
        n[(i, j)] = n.get((i, j), 0) + 1
        n[(j, i)] = n.get((j, i), 0) + 1
    for i in codes:   # prior: one virtual tie against a reference player of strength 1
        wins[i] += prior
    for _ in range(iters):
        new = {}
        for i in codes:
            den = sum(n.get((i, j), 0) / (p[i] + p[j]) for j in codes if j != i) + 2 * prior / (p[i] + 1.0)
            new[i] = wins[i] / den if den else p[i]
        g = math.exp(sum(math.log(v) for v in new.values()) / len(new))
        p = {c: v / g for c, v in new.items()}
    return {c: 1500 + 400 * math.log10(v) for c, v in p.items()}


def cmd_rank(a):
    st = load(a.arena)
    vs = votes(a.arena)
    oc = outcomes(st, vs)
    if not oc:
        raise SystemExit("sem votos ainda")
    codes = [e["code"] for e in st["entrants"]]
    obs = [(o["a"], o["b"], 1.0 if o["winner"] == o["a"] else 0.0 if o["winner"] == o["b"] else 0.5) for o in oc]
    score = bradley_terry(codes, obs)
    rnd = random.Random(7)
    boots = {c: [] for c in codes}
    for _ in range(200):
        sample = [rnd.choice(obs) for _ in obs]
        s = bradley_terry(codes, sample, iters=120)
        for c in codes:
            boots[c].append(s[c])
    ci = {c: (sorted(v)[10], sorted(v)[189]) for c, v in boots.items()}
    both = [o for o in oc if o["orders"] == 2]
    consist = sum(o["consistent"] for o in both) / len(both) if both else 0
    # judge agreement with the panel majority per match
    maj = {}
    for o in oc:
        maj.setdefault((o["round"], o["match"]), []).append(o["winner"])
    agree = {}
    for o in oc:
        ws = [w for w in maj[(o["round"], o["match"])] if w]
        top = max(set(ws), key=ws.count) if ws else None
        agree.setdefault(o["judge"], []).append(1 if o["winner"] == top else 0)
    ent = {e["code"]: e for e in st["entrants"]}
    # nota ABSOLUTA (0–10) quando os juízes deram "absoluto": {"A": n, "B": n} — o ranking é relativo; isto diz se o
    # 1º é bom de verdade (portão: média ≥ 7)
    idx = {(r["k"], m["id"]): m for r in st["rounds"] for m in r["matches"]}
    absol = {c: [] for c in codes}
    for v in vs:
        ab = v.get("absoluto") or {}
        m = idx.get((int(v["round"]), v["match"]))
        if not ab or not m:
            continue
        left, right = (m["a"], m["b"]) if v["order"].upper() == "AB" else (m["b"], m["a"])
        for side, c in (("A", left), ("B", right)):
            try:
                absol[c].append(float(ab.get(side)))
            except (TypeError, ValueError):
                pass
    table = sorted(codes, key=lambda c: -score[c])
    res = {"ranking": [{"code": c, "name": ent[c]["name"], "author": ent[c]["author"], "score": round(score[c]),
                        "ci90": [round(x) for x in ci[c]], "desc": ent[c]["desc"],
                        "absoluto": round(sum(absol[c]) / len(absol[c]), 1) if absol[c] else None} for c in table],
           "consistencia_ordem": round(consist, 2),
           "concordancia_juizes": {j: round(sum(v) / len(v), 2) for j, v in agree.items()},
           "partidas": len(oc)}
    json.dump(res, open(os.path.join(a.arena, "ranking.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"{'#':<3}{'código':<8}{'nome':<22}{'nota':>6}  IC90        abs/10  autor")
    for i, r in enumerate(res["ranking"], 1):
        ab = f"{r['absoluto']:.1f}" if r["absoluto"] is not None else "–"
        print(f"{i:<3}{r['code']:<8}{r['name'][:21]:<22}{r['score']:>6}  {r['ci90'][0]}–{r['ci90'][1]:<6} {ab:>6}  "
              f"{r['author']}")
    top_abs = res["ranking"][0]["absoluto"]
    if top_abs is not None and top_abs < 7:
        print(f"PORTÃO ABSOLUTO: o 1º tem {top_abs:.1f}/10 (< 7) — ganhou entre opções fracas; crie novas antes de seguir")
    print(f"consistência entre ordens AB/BA: {consist:.0%} · partidas: {len(oc)}")
    print("concordância de cada juiz com a maioria:", ", ".join(f"{j} {v:.0%}" for j, v in
                                                             res["concordancia_juizes"].items()))
    top2 = res["ranking"][:2]
    if len(top2) == 2 and top2[1]["ci90"][1] >= top2[0]["ci90"][0]:
        print("1º e 2º estão empatados dentro da margem → rodada final de debate ou decisão humana")
    ranking_sheet(a.arena, res, ent)


def ranking_sheet(d, res, ent):
    from PIL import Image, ImageDraw
    items = res["ranking"]
    w, h = 600, 450
    W = len(items) * (w + 20) + 20
    im = Image.new("RGB", (W, h + 140), (245, 245, 242))
    dr = ImageDraw.Draw(im)
    for i, r in enumerate(items):
        b = fit_board(os.path.join(d, ent[r["code"]]["board"]), w, h)
        im.paste(b, (20 + i * (w + 20), 20))
        dr.text((20 + i * (w + 20), h + 34), f"{i + 1}º  {r['name']}  ·  {r['score']}", fill=(20, 20, 20),
                font=_font(30))
        dr.text((20 + i * (w + 20), h + 80), f"IC90 {r['ci90'][0]}–{r['ci90'][1]}", fill=(90, 90, 90),
                font=_font(22))
    im.save(os.path.join(d, "ranking.png"))
    print("folha:", os.path.join(d, "ranking.png"))


# ------------------------------------------------------------------ public leaderboards (arena.ai dataset, CC-BY-4.0)
def cmd_modelos(a):
    rows, off = [], 0
    while True:
        url = LEADER.format(b=a.board, o=off)
        req = urllib.request.Request(url, headers={"User-Agent": "brand-system"})
        data = json.loads(urllib.request.urlopen(req, timeout=60).read())
        batch = [r["row"] for r in data.get("rows", [])]
        rows += batch
        off += 100
        if len(batch) < 100 or off >= 2000:
            break
    if not rows:
        raise SystemExit("sem dados (board inválido?)")
    cats = sorted({r.get("category") for r in rows})
    cat = a.category or ("overall" if "overall" in cats else cats[0])
    sel = sorted((r for r in rows if r.get("category") == cat), key=lambda r: -float(r.get("rating") or 0))
    date = max((str(r.get("leaderboard_publish_date", "")) for r in rows), default="")
    print(f"arena.ai · {a.board} · categoria {cat} · publicado {date}  (fonte: lmarena-ai/leaderboard-dataset, CC-BY-4.0)")
    for i, r in enumerate(sel[: a.top], 1):
        name = r.get("model_name", "")
        mark = "  ← Gemini API" if any(g in name.lower() for g in GEMINI_REACHABLE) else ""
        print(f"{i:>2}. {name:<42} {float(r.get('rating', 0)):7.1f}  votos {r.get('vote_count', '')}{mark}")
    print("categorias:", ", ".join(c for c in cats if c))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("add"); p.add_argument("arena"); p.add_argument("--board", required=True)
    p.add_argument("--desc"); p.add_argument("--name"); p.add_argument("--author"); p.set_defaults(fn=cmd_add)
    p = sp.add_parser("pair"); p.add_argument("arena"); p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_pair)
    p = sp.add_parser("vote"); p.add_argument("arena"); p.add_argument("--round", type=int)
    p.add_argument("--match"); p.add_argument("--order"); p.add_argument("--judge"); p.add_argument("--json")
    p.add_argument("--file"); p.set_defaults(fn=cmd_vote)
    p = sp.add_parser("gemini"); p.add_argument("arena"); p.add_argument("--round", type=int)
    p.add_argument("--model", default="pro"); p.set_defaults(fn=cmd_gemini)
    p = sp.add_parser("rank"); p.add_argument("arena"); p.set_defaults(fn=cmd_rank)
    p = sp.add_parser("modelos"); p.add_argument("--board", default="text_to_image"); p.add_argument("--category")
    p.add_argument("--top", type=int, default=12); p.set_defaults(fn=cmd_modelos)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
