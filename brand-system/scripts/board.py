"""Territory board: one standard 1920×1080 board per creative territory, so arena judges compare IDEAS, not
presentation polish. A territory is a mini brand project (its own brand.json) inside <brand>/territorios/<x>/.

Usage:
  python board.py <territory_dir>          # → <territory_dir>/board.png
Reads: name, platform.idea, platform.onlyness (as "por que é desta marca"), logo.symbol / main primitive,
color.seeds, type.display/text, elementos/*.png (first colorway of each device), aplicacoes/*/pecas/*-1080x1350.png
and *-1080x1920.png. Designer-made folders in aplicacoes/ win over the automatic recipes; folders starting with "_"
are ignored. Exact picks: brand.json "board": {"symbol": "…svg", "elements": ["…png" ×4], "feed": "…png",
"story": "…png"}. Elements are shown whole (contain) on their own background colour. Missing parts are left as empty
slots (that itself tells the judges something).
"""
import argparse
import glob
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import brand_font_faces, html_screenshot, ink_on, load_brand, solid, svg_inner, viewbox, write  # noqa: E402

RECIPES = ["supergrafico", "foto", "tipografico", "padrao", "numeral", "moldura"]


def corner_colour(path):
    """Background colour of an element preview (top-left pixel) so 'contain' letterboxes blend in."""
    try:
        from PIL import Image
        r, g, b_ = Image.open(path).convert("RGB").getpixel((2, 2))
        return f"#{r:02x}{g:02x}{b_:02x}"
    except Exception:
        return "#d2d2cd"

E = html.escape


def rel(p, base):
    return os.path.relpath(p, base).replace("\\", "/")


def build(tdir):
    b = load_brand(tdir)
    ink, paper, brand = b.colour("ink"), b.colour("paper", "#F4F3EF"), b.colour("brand")
    faces, _ = brand_font_faces(b)
    pick_cfg = b.get("board") or {}
    prim = None
    for cand in [pick_cfg.get("symbol"), b.get("logo.symbol"), b.primitive(), b.get("logo.primary")]:
        if cand and os.path.exists(b.path(cand)):
            prim = open(b.path(cand), encoding="utf-8").read()
            break
    sym = ""
    if prim:
        s = solid(prim, ink_on(brand, paper, ink))     # the more legible of paper/ink on the brand colour
        vx, vy, vw, vh = viewbox(s)
        sym = (f'<svg viewBox="{vx:g} {vy:g} {vw:g} {vh:g}" width="100%" height="100%" '
               f'preserveAspectRatio="xMidYMid meet">{svg_inner(s)}</svg>')
    if pick_cfg.get("elements"):
        els = [b.path(p) for p in pick_cfg["elements"] if os.path.exists(b.path(p))]
    else:   # first colorway of each device (elements.py build), then any other element preview
        els = []
        for dv in b.get("devices") or []:
            ways = dv.get("colorways") or []
            exact = os.path.join(tdir, "elementos", f"{dv['id']}-{ways[0]}.png") if ways else None
            first = [exact] if exact and os.path.exists(exact) else \
                sorted(glob.glob(os.path.join(tdir, "elementos", f"{dv['id']}-*.png")))
            els += first[:1]
        if len(els) < 4:
            taken = {os.path.basename(e).split("-")[0] for e in els}
            more = sorted(p for p in glob.glob(os.path.join(tdir, "elementos", "*.png"))
                          if "folha" not in p and p not in els and os.path.basename(p).split("-")[0] not in taken)
            els += more[:4 - len(els)]

    def folder(p):
        return os.path.basename(os.path.dirname(os.path.dirname(p)))

    def pick(size, skip=None):
        found = [p for p in glob.glob(os.path.join(tdir, "aplicacoes", "*", "pecas", f"*-{size}.png"))
                 if not folder(p).startswith("_")]
        # designer-made folders first (they exist because the recipes were not enough), then recipes in order
        found = sorted(found, key=lambda p: (RECIPES.index(folder(p)) + 1) if folder(p) in RECIPES else 0)
        diff = [p for p in found if skip is None or os.path.dirname(p) != os.path.dirname(skip)]
        return (diff or found)[:1]
    feed = [b.path(pick_cfg["feed"])] if pick_cfg.get("feed") else pick("1080x1350")
    story = [b.path(pick_cfg["story"])] if pick_cfg.get("story") else pick("1080x1920", feed[0] if feed else None)
    seeds = b.get("color.seeds") or {}
    sw = "".join(f'<div style="flex:1;height:70px;background:{(v["hex"] if isinstance(v, dict) else v)}"></div>'
                 for v in seeds.values())
    t = b.get("type") or {}
    dn = (t.get("display") or {}).get("family", "") if isinstance(t.get("display"), dict) else t.get("display", "")
    tn = (t.get("text") or {}).get("family", "") if isinstance(t.get("text"), dict) else t.get("text", "")
    img = lambda p, fit="cover": (f'<img src="{rel(p, tdir)}" style="width:100%;height:100%;object-fit:{fit};'  # noqa
                                  f'display:block">' if p else "")
    cells = "".join(f'<div class="c" style="background:{corner_colour(p)}">{img(p, "contain")}</div>'
                    for p in els[:4]) + \
        "".join('<div class="c empty"></div>' for _ in range(max(0, 4 - len(els[:4]))))
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{faces}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1920px;height:1080px;background:#E4E4E0;
font-family:brand-text,sans-serif;color:#151515;overflow:hidden}}
.wrap{{display:grid;grid-template-columns:600px 560px 1fr;gap:28px;padding:40px;height:1080px}}
.wrap>div{{min-height:0}}
.c{{background:#d2d2cd;overflow:hidden}} .empty{{background:repeating-linear-gradient(45deg,#d8d8d3 0 12px,#cfcfca 12px 24px)}}
h1{{font-family:brand-display;font-size:64px;line-height:.95;margin-bottom:22px}}
.idea{{font-family:brand-display;font-size:34px;line-height:1.1;margin-bottom:22px}}
p{{font-size:20px;line-height:1.4}} .lab{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;opacity:.55;
margin:18px 0 8px}}</style></head><body><div class="wrap">
<div><h1>{E(b.name)}</h1><div class="idea">{E(b.get("platform.idea") or "")}</div>
<p>{E(b.get("platform.onlyness") or "")}</p>
<div class="lab">paleta</div><div style="display:flex;border:1px solid #0002">{sw}</div>
<div class="lab">tipografia · {E(dn)} / {E(tn)}</div>
<div style="display:flex;gap:30px;align-items:baseline"><span style="font-family:brand-display;font-size:150px;line-height:1">Aa</span>
<span style="font-family:brand-text;font-size:90px;line-height:1">Aa</span></div></div>
<div style="display:grid;grid-template-rows:560px 1fr;gap:28px"><div style="background:{brand};padding:70px">{sym}</div>
<div style="display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:28px;height:412px;min-height:0">{cells}</div></div>
<div style="display:grid;grid-template-columns:1.1fr .9fr;gap:28px"><div class="c">{img(feed[0] if feed else "", "contain")}</div>
<div class="c">{img(story[0] if story else "", "contain")}</div></div>
</div></body></html>"""
    hp = os.path.join(tdir, "_board.html")
    write(hp, doc)
    out = os.path.join(tdir, "board.png")
    html_screenshot(hp, out, 1920, 1080)
    os.remove(hp)
    print(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("territory")
    build(ap.parse_args().territory)


if __name__ == "__main__":
    main()
