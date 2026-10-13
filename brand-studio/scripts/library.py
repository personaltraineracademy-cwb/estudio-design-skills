"""Brand library: the house collection (approved work) + the market reference library, searchable by CLIP.

Sources
  casa     — approved identities of every client: <BRAND_LIBRARY>/<Cliente>/<Projeto>/*.svg|png
             (default: design/biblioteca next to the skills folder, else ~/Documents/logos). Each client folder may
             hold _perfil.md (its style profile) and _fichas.json (identity cards per project).
  mercado  — ~1,400 classified real-world logos from the logo-design skill, kept in <BRAND_LIBRARY>/_mercado
             (study only, never trace)

Usage
  python library.py index [--source casa|mercado|all] [--force]
  python library.py stats
  python library.py clients                          # clients in the library (+ projects, profile yes/no)
  python library.py projects [--client Acme]          # projects + their fichas (identity cards)
  python library.py profile Acme                      # print the client's style profile (_perfil.md)
  python library.py colors [--client Acme]            # colours already used by approved work (avoid near-duplicates)
  python library.py search "bold black wordmark with a badge" [--source casa] [--client Acme] [--k 12] [--where mark_type=wordmark] [--sheet out.png]
  python library.py similar ref.png [--source all] [--client Acme] [--k 12] [--sheet out.png]
  python library.py novelty cand1.svg cand2.png      # originality check vs. every client + market
  python library.py add file.svg --client "Cliente" --project "Nome" [--status aprovado|reprovado] [--note "por quê"]
  python library.py sheet --project "Acme/Lancamento" -o lancamento.png   # contact sheet of a project (or --client Acme)

Index lives in <BRAND_LIBRARY>/_catalogo/ (catalog.sqlite, thumbs/); projects are stored as "Cliente/Projeto". Thumbnails are rendered on mid-grey so
white, black and colour marks are all visible to the eye and to CLIP.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CATALOG_DIR, LIBRARY_DIR, LOGO_SKILL, MODEL_DIR, svg_to_png  # noqa: E402

DB = os.path.join(CATALOG_DIR, "catalog.sqlite")
THUMBS = os.path.join(CATALOG_DIR, "thumbs")
FICHAS = os.path.join(CATALOG_DIR, "fichas.json")      # legacy single file (pre multi-client); read if present
# market logos live in <BRAND_LIBRARY>/_mercado (moved out of logo-design; its assets/library is a junction to it)
MARKET_DIR = (os.path.join(LIBRARY_DIR, "_mercado") if os.path.isdir(os.path.join(LIBRARY_DIR, "_mercado"))
              else os.path.join(LOGO_SKILL, "assets", "library"))
GREY = (140, 140, 140)
TSIZE = 256

# Cosine-similarity bands (CLIP ViT-B/32 on logo thumbnails), calibrated on colour variants of the same mark.
NEAR_COPY = 0.93
CLOSE = 0.88


def db():
    os.makedirs(CATALOG_DIR, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("""create table if not exists items(
        id text primary key, source text, project text, file text, kind text, width real, height real,
        colors text, live_text int, images int, status text, note text, meta text, added text, mtime real)""")
    con.execute("create table if not exists emb(id text primary key, vec blob)")
    return con


# ------------------------------------------------------------------ models
_img_model = _txt_model = None


def img_model():
    global _img_model
    if _img_model is None:
        from fastembed import ImageEmbedding
        _img_model = ImageEmbedding("Qdrant/clip-ViT-B-32-vision", cache_dir=MODEL_DIR)
    return _img_model


def txt_model():
    global _txt_model
    if _txt_model is None:
        from fastembed import TextEmbedding
        _txt_model = TextEmbedding("Qdrant/clip-ViT-B-32-text", cache_dir=MODEL_DIR)
    return _txt_model


def norm(v):
    import numpy as np
    v = np.asarray(v, dtype="float32")
    return v / (np.linalg.norm(v) + 1e-9)


# ------------------------------------------------------------------ thumbnails & features
def thumb_image(path):
    """Render any SVG/PNG/JPG to a TSIZE square PIL image on mid-grey."""
    from PIL import Image
    ext = os.path.splitext(path)[1].lower()
    if ext == ".svg":
        raw = svg_to_png(svg_path=path, width=TSIZE * 2)
        im = Image.open(io.BytesIO(raw)).convert("RGBA")
    else:
        im = Image.open(path).convert("RGBA")
    im.thumbnail((TSIZE - 16, TSIZE - 16))
    canvas = Image.new("RGBA", (TSIZE, TSIZE), GREY + (255,))
    canvas.alpha_composite(im, ((TSIZE - im.width) // 2, (TSIZE - im.height) // 2))
    return canvas.convert("RGB"), im


def colours_of(path, rgba=None, k=6):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".svg":
        s = open(path, encoding="utf-8", errors="ignore").read()
        found = [c.upper() for c in re.findall(r"#[0-9a-fA-F]{6}\b", s)]
        out = []
        for c in found:
            if c not in out:
                out.append(c)
        return out[:k]
    from PIL import Image
    im = (rgba or Image.open(path).convert("RGBA")).copy()
    im.thumbnail((128, 128))
    px = [p[:3] for p in im.getdata() if p[3] > 200]
    if not px:
        return []
    q = Image.new("RGB", (len(px), 1))
    q.putdata(px)
    q = q.quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[: 3 * k]
    counts = sorted(q.getcolors(), reverse=True)
    return ["#%02X%02X%02X" % tuple(pal[3 * i: 3 * i + 3]) for _, i in counts][:k]


def svg_flags(path):
    if not path.lower().endswith(".svg"):
        return 0, 0
    s = open(path, encoding="utf-8", errors="ignore").read()
    return s.count("<text"), s.count("<image")


def item_id(source, path):
    return source + ":" + hashlib.sha1(os.path.abspath(path).lower().encode()).hexdigest()[:16]


# ------------------------------------------------------------------ indexing
IMG_EXT = (".svg", ".png", ".jpg", ".jpeg")


def iter_casa():
    """<LIBRARY>/<Cliente>/<Projeto>/** ; loose files in a client folder belong to '<Cliente>/_geral'."""
    if not os.path.isdir(LIBRARY_DIR):
        return
    for client in sorted(os.listdir(LIBRARY_DIR)):
        cp = os.path.join(LIBRARY_DIR, client)
        if not os.path.isdir(cp) or client.startswith(("_", ".")):
            continue
        for entry in sorted(os.listdir(cp)):
            ep = os.path.join(cp, entry)
            if entry.startswith(("_", ".")):
                continue
            if os.path.isdir(ep):
                for root, _, files in os.walk(ep):
                    for f in sorted(files):
                        if f.lower().endswith(IMG_EXT):
                            yield f"{client}/{entry}", os.path.join(root, f), {}
            elif entry.lower().endswith(IMG_EXT):
                yield f"{client}/_geral", ep, {}


def clients_list():
    if not os.path.isdir(LIBRARY_DIR):
        return []
    return [c for c in sorted(os.listdir(LIBRARY_DIR))
            if os.path.isdir(os.path.join(LIBRARY_DIR, c)) and not c.startswith(("_", "."))]


def load_fichas(client=None):
    """{"Cliente/Projeto": ficha} from every <Cliente>/_fichas.json (+ legacy global fichas.json)."""
    out = {}
    if os.path.exists(FICHAS):
        for k, v in json.load(open(FICHAS, encoding="utf-8")).items():
            out[k if "/" in k else f"?/{k}"] = v
    for c in clients_list():
        p = os.path.join(LIBRARY_DIR, c, "_fichas.json")
        if os.path.exists(p):
            for k, v in json.load(open(p, encoding="utf-8")).items():
                out[f"{c}/{k}"] = v
    if client:
        out = {k: v for k, v in out.items() if k.split("/")[0].lower() == client.lower()}
    return out


def used_colours(client=None):
    """HEX colours declared in the fichas of approved projects -> [(hex, 'Cliente/Projeto', label)]."""
    out = []
    for proj, fi in load_fichas(client).items():
        for c in fi.get("cores", []):
            m = re.match(r"\s*(#[0-9A-Fa-f]{6})\s*(.*)", c)
            if m:
                out.append((m[1].upper(), proj, m[2].strip()))
    return out


def iter_mercado():
    cat = os.path.join(MARKET_DIR, "catalog.json")
    if not os.path.exists(cat):
        return
    for m in json.load(open(cat, encoding="utf-8")):
        yield m.get("brand", ""), os.path.join(MARKET_DIR, "svg", m["file"]), m


def index(source="all", force=False):
    con = db()
    sources = ["casa", "mercado"] if source == "all" else [source]
    todo = []
    for src in sources:
        it = iter_casa() if src == "casa" else iter_mercado()
        seen = set()
        for proj, path, meta in it:
            iid = item_id(src, path)
            seen.add(iid)
            mt = os.path.getmtime(path)
            row = con.execute("select mtime from items where id=?", (iid,)).fetchone()
            has = con.execute("select 1 from emb where id=?", (iid,)).fetchone()
            if row and has and row[0] == mt and not force:
                continue
            todo.append((src, proj, path, meta, iid, mt))
        # forget files that disappeared
        for (iid,) in con.execute("select id from items where source=?", (src,)).fetchall():
            if iid not in seen:
                con.execute("delete from items where id=?", (iid,))
                con.execute("delete from emb where id=?", (iid,))
    print(f"to index: {len(todo)}")
    batch = []
    for n, (src, proj, path, meta, iid, mt) in enumerate(todo, 1):
        try:
            th, rgba = thumb_image(path)
        except Exception as e:  # unreadable file: skip but report
            print(f"  skip {path}: {e}")
            continue
        tp = os.path.join(THUMBS, src, iid.split(":")[1] + ".png")
        os.makedirs(os.path.dirname(tp), exist_ok=True)
        th.save(tp)
        lt, ims = svg_flags(path)
        cols = colours_of(path, rgba)
        old = con.execute("select status, note, added from items where id=?", (iid,)).fetchone()
        status, note, added = old if old else ("aprovado" if src == "casa" else "referencia", "",
                                               datetime.date.today().isoformat())
        con.execute("insert or replace into items values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (iid, src, proj, os.path.abspath(path), os.path.splitext(path)[1][1:].lower(), rgba.width,
                     rgba.height, json.dumps(cols), lt, ims, status, note, json.dumps(meta, ensure_ascii=False),
                     added, mt))
        batch.append((iid, tp))
        if len(batch) == 64 or n == len(todo):
            vecs = list(img_model().embed([b[1] for b in batch], batch_size=32))
            for (bid, _), v in zip(batch, vecs):
                con.execute("insert or replace into emb values(?,?)", (bid, norm(v).tobytes()))
            con.commit()
            print(f"  {n}/{len(todo)}")
            batch = []
    con.commit()
    stats(con)


# ------------------------------------------------------------------ queries
def load_matrix(con, source="all", where=None, client=None):
    import numpy as np
    q = "select i.id, i.source, i.project, i.file, i.status, i.meta, e.vec from items i join emb e on e.id=i.id"
    args = []
    if source != "all":
        q += " where i.source=?"
        args.append(source)
    rows = con.execute(q, args).fetchall()
    if client:
        rows = [r for r in rows if r[1] != "casa" or r[2].split("/")[0].lower() == client.lower()]
    if where:
        k, _, v = where.partition("=")
        def ok(meta):
            val = json.loads(meta or "{}").get(k)
            return (v in val) if isinstance(val, list) else (str(val) == v)
        rows = [r for r in rows if ok(r[5])]
    if not rows:
        return [], None
    mat = np.stack([np.frombuffer(r[6], dtype="float32") for r in rows])
    return rows, mat


def embed_query_image(path):
    th, _ = thumb_image(path)
    tmp = os.path.join(CATALOG_DIR, "_query.png")
    th.save(tmp)
    return norm(list(img_model().embed([tmp]))[0])


def ranked(rows, mat, qv, k):
    import numpy as np
    sims = mat @ qv
    order = np.argsort(-sims)[:k]
    return [(float(sims[i]), rows[i]) for i in order]


def show(results, sheet=None, title=""):
    for s, r in results:
        meta = json.loads(r[5] or "{}")
        extra = meta.get("mark_type") or ""
        print(f"{s:.3f}  [{r[1]}] {r[2]} — {os.path.basename(r[3])}  {extra}")
    if sheet:
        contact_sheet([(r[0], f"{r[2]} · {s:.2f}") for s, r in results], sheet, title)


def contact_sheet(items, out, title="", cols=6):
    """items: [(item_id, label)] → one PNG grid of thumbnails."""
    from PIL import Image, ImageDraw, ImageFont
    cell, lab = TSIZE, 22
    rows = max(1, -(-len(items) // cols))
    W, H = cols * (cell + 8) + 8, rows * (cell + lab + 8) + 48
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("arial.ttf", 13)
        ft = ImageFont.truetype("arialbd.ttf", 20)
    except OSError:
        f = ft = ImageFont.load_default()
    d.text((10, 12), title, fill=(0, 0, 0), font=ft)
    for n, (iid, label) in enumerate(items):
        src, h = iid.split(":")
        tp = os.path.join(THUMBS, src, h + ".png")
        x, y = 8 + (n % cols) * (cell + 8), 44 + (n // cols) * (cell + lab + 8)
        if os.path.exists(tp):
            im.paste(Image.open(tp), (x, y))
        d.text((x + 2, y + cell + 3), label[:38], fill=(60, 60, 60), font=f)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    im.save(out)
    print(f"sheet: {out}")


def stats(con=None):
    con = con or db()
    for src, n in con.execute("select source, count(*) from items group by source"):
        print(f"{src}: {n} itens")
    for proj, n in con.execute("select project, count(*) from items where source='casa' group by project"):
        print(f"  casa/{proj}: {n}")
    lt = con.execute("select count(*) from items where source='casa' and (live_text>0 or images>0)").fetchone()[0]
    if lt:
        print(f"  atenção: {lt} arquivos do acervo com texto vivo ou imagem embutida (converter para curvas na entrega)")


def clients():
    con = db()
    counts = dict(con.execute("select project, count(*) from items where source='casa' group by project").fetchall())
    for c in clients_list():
        projs = sorted(p for p in counts if p.split("/")[0] == c)
        n = sum(counts[p] for p in projs)
        prof = "sim" if os.path.exists(os.path.join(LIBRARY_DIR, c, "_perfil.md")) else "não"
        print(f"{c}: {len(projs)} projetos, {n} arquivos, perfil: {prof}")
        for p in projs:
            print(f"   - {p.split('/', 1)[1]} ({counts[p]})")
    if not clients_list():
        print(f"biblioteca vazia: crie {LIBRARY_DIR}/<Cliente>/<Projeto>/ com os SVG/PNG aprovados")


def profile(client):
    p = os.path.join(LIBRARY_DIR, client, "_perfil.md")
    if not os.path.exists(p):
        print(f"cliente '{client}' sem perfil ({p}).\nCliente novo: não herde estilo de outro cliente. Depois da "
              "primeira aprovação, escreva o _perfil.md (veja brand-studio/references/perfil-cliente.md).")
        return
    print(f"# {p}\n")
    print(open(p, encoding="utf-8").read())


def projects(client=None):
    fichas = load_fichas(client)
    con = db()
    for proj, n in con.execute("select project, count(*) from items where source='casa' group by project"):
        if client and proj.split("/")[0].lower() != client.lower():
            continue
        fi = fichas.get(proj, {})
        print(f"\n## {proj}  ({n} arquivos)")
        for k in ("tipo", "segmento", "conceito", "recursos", "cores", "tipografia", "porque_aprovado", "evitar"):
            if fi.get(k):
                v = fi[k]
                print(f"  {k}: {', '.join(v) if isinstance(v, list) else v}")


def novelty(paths, k=3):
    con = db()
    rows, mat = load_matrix(con, "all")
    worst = 0.0
    for p in paths:
        qv = embed_query_image(p)
        res = ranked(rows, mat, qv, 40)
        print(f"\n{os.path.basename(p)}")
        shown = {"casa": 0, "mercado": 0}
        for s, r in res:
            if shown[r[1]] >= k:
                continue
            shown[r[1]] += 1
            flag = "QUASE CÓPIA" if s >= NEAR_COPY else ("parecido" if s >= CLOSE else "ok")
            print(f"  {s:.3f} {flag:11s} [{r[1]}] {r[2]} — {os.path.basename(r[3])}")
            worst = max(worst, s)
    verdict = "REPROVADO: refazer" if worst >= NEAR_COPY else ("ATENÇÃO: comparar lado a lado" if worst >= CLOSE
                                                             else "original")
    print(f"\nveredito: {verdict} (máx {worst:.3f}; quase cópia ≥ {NEAR_COPY}, parecido ≥ {CLOSE})")
    print("obs.: variações de cor do MESMO projeto pontuam alto de propósito — compare com outros projetos.")


def add(path, project, client=None, status="aprovado", note=""):
    if "/" in project and not client:
        client, project = project.split("/", 1)
    if not client:
        raise SystemExit("informe --client (pasta do cliente em biblioteca/)")
    dest_dir = os.path.join(LIBRARY_DIR, client, project)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(path))
    if os.path.abspath(dest) != os.path.abspath(path):
        if os.path.exists(dest):
            base, ext = os.path.splitext(dest)
            dest = f"{base}-{datetime.date.today().isoformat()}{ext}"
        shutil.copy2(path, dest)
    index("casa")
    con = db()
    con.execute("update items set status=?, note=? where id=?", (status, note, item_id("casa", dest)))
    con.commit()
    print(f"adicionado: {dest} ({status})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("index"); a.add_argument("--source", default="all"); a.add_argument("--force", action="store_true")
    sub.add_parser("stats"); sub.add_parser("clients")
    a = sub.add_parser("projects"); a.add_argument("--client")
    a = sub.add_parser("profile"); a.add_argument("client")
    a = sub.add_parser("colors"); a.add_argument("--client")
    a = sub.add_parser("search"); a.add_argument("text"); a.add_argument("--source", default="all")
    a.add_argument("--k", type=int, default=12); a.add_argument("--where"); a.add_argument("--sheet")
    a.add_argument("--client")
    a = sub.add_parser("similar"); a.add_argument("image"); a.add_argument("--source", default="all")
    a.add_argument("--k", type=int, default=12); a.add_argument("--sheet"); a.add_argument("--client")
    a = sub.add_parser("novelty"); a.add_argument("files", nargs="+")
    a = sub.add_parser("add"); a.add_argument("file"); a.add_argument("--project", required=True)
    a.add_argument("--client"); a.add_argument("--status", default="aprovado"); a.add_argument("--note", default="")
    a = sub.add_parser("sheet"); a.add_argument("--project"); a.add_argument("--client")
    a.add_argument("-o", required=True)
    args = ap.parse_args()
    if args.cmd == "index":
        index(args.source, args.force)
    elif args.cmd == "stats":
        stats()
    elif args.cmd == "clients":
        clients()
    elif args.cmd == "projects":
        projects(args.client)
    elif args.cmd == "profile":
        profile(args.client)
    elif args.cmd == "colors":
        for hx, proj, label in used_colours(args.client):
            print(f"{hx}  {proj}  {label}")
    elif args.cmd == "search":
        con = db()
        rows, mat = load_matrix(con, args.source, args.where, args.client)
        qv = norm(list(txt_model().embed([args.text]))[0])
        show(ranked(rows, mat, qv, args.k), args.sheet, args.text)
    elif args.cmd == "similar":
        con = db()
        rows, mat = load_matrix(con, args.source, client=args.client)
        show(ranked(rows, mat, embed_query_image(args.image), args.k), args.sheet, os.path.basename(args.image))
    elif args.cmd == "novelty":
        novelty(args.files)
    elif args.cmd == "add":
        add(args.file, args.project, args.client, args.status, args.note)
    elif args.cmd == "sheet":
        con = db()
        rows = con.execute("select id, file, project from items where source='casa' order by project, file").fetchall()
        if args.project:
            sel = [r for r in rows if r[2] == args.project or r[2].split("/", 1)[-1] == args.project]
        elif args.client:
            sel = [r for r in rows if r[2].split("/")[0].lower() == args.client.lower()]
        else:
            raise SystemExit('use --project "Cliente/Projeto" ou --client Cliente')
        contact_sheet([(i, os.path.basename(f)) for i, f, _ in sel], args.o, args.project or args.client)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
