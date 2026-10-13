"""Generative exploration: run a JS sketch over many seeds → vector SVGs + one contact sheet to choose from.

Usage:
  python sketch.py list                                              # bundled sketches
  python sketch.py run radial-cuts --seeds 1-36 -o out/rc           # sheet: out/rc-sheet.png, SVGs in out/rc/
  python sketch.py run truchet --seeds 1-24 --params '{"n":3,"symmetry":"mirror"}' --pal accent=#F8C100 fg=#1A1A1A bg=#F5F5F5
  python sketch.py run my-sketch.mjs --seeds 7 --transparent -o out/pick   # one seed, transparent → use as symbol
  python sketch.py new nome                                          # copy a template to start a project sketch

Bundled sketches (assets/sketches): radial-cuts (shape split by cuts) · truchet (modular tile marks / monograms) ·
orbit-rings (kinetic ring segments) · superform (Gielis shapes) · flow-ribbons (energy lines for KVs) ·
halftone-field (vector halftone textures). Write new ones per project: export `meta` and `draw(ctx)` returning
SVG markup; ctx = {rnd, noise, w, h, params, pal, lib, seed}. Use `currentColor` for the main ink and pal.accent.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SKILL_DIR, svg_to_png  # noqa: E402

SK = os.path.join(SKILL_DIR, "assets", "sketches")


def resolve(name):
    if os.path.exists(name):
        return os.path.abspath(name)
    p = os.path.join(SK, name if name.endswith(".mjs") else name + ".mjs")
    if os.path.exists(p):
        return p
    raise SystemExit(f"sketch não encontrado: {name}")


def seeds(spec):
    if "-" in spec:
        a, b = spec.split("-")
        return int(a), int(b)
    return int(spec), int(spec)


def run(a):
    sk = resolve(a.sketch)
    s0, s1 = seeds(a.seeds)
    out_dir = a.out
    params = json.loads(a.params) if a.params else {}
    if a.pal:
        params["pal"] = dict(kv.split("=", 1) for kv in a.pal)
    if a.transparent:
        params["transparent"] = True
    if a.size:
        params["w"], params["h"] = (int(v) for v in a.size.lower().split("x"))
    # run.mjs imports lib.mjs relative to itself; project sketches import './lib.mjs' too → copy lib next to them
    if os.path.dirname(sk) != SK:
        shutil.copy(os.path.join(SK, "lib.mjs"), os.path.join(os.path.dirname(sk), "lib.mjs"))
    r = subprocess.run(["node", os.path.join(SK, "run.mjs"), sk, out_dir, str(s0), str(s1), json.dumps(params)],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    name = os.path.basename(sk)[:-4]
    files = sorted(glob.glob(os.path.join(out_dir, f"{name}-*.svg")),
                   key=lambda p: int(p.rsplit("-", 1)[1][:-4]))
    files = [p for p in files if s0 <= int(p.rsplit("-", 1)[1][:-4]) <= s1]
    from PIL import Image, ImageDraw, ImageFont
    import io
    cell, cols = 240, min(6, len(files))
    rows = -(-len(files) // cols)
    sheet = Image.new("RGB", (cols * (cell + 8) + 8, rows * (cell + 26) + 8), "white")
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        f = ImageFont.load_default()
    for n, p in enumerate(files):
        im = Image.open(io.BytesIO(svg_to_png(svg_path=p, width=cell * 2))).convert("RGBA")
        bg = Image.new("RGBA", im.size, (140, 140, 140, 255))
        bg.alpha_composite(im)
        im = bg.convert("RGB")
        im.thumbnail((cell, cell))
        x, y = 8 + (n % cols) * (cell + 8), 8 + (n // cols) * (cell + 26)
        sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        d.text((x + 2, y + cell + 5), f"seed {p.rsplit('-', 1)[1][:-4]}", fill="black", font=f)
    out = out_dir.rstrip("/\\") + "-sheet.png"
    sheet.save(out)
    print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list")
    r = sub.add_parser("run")
    r.add_argument("sketch"); r.add_argument("--seeds", default="1-24"); r.add_argument("--params")
    r.add_argument("--pal", nargs="*"); r.add_argument("--transparent", action="store_true")
    r.add_argument("--size"); r.add_argument("-o", "--out", required=True)
    n = sub.add_parser("new"); n.add_argument("name"); n.add_argument("--from", dest="src", default="radial-cuts")
    a = ap.parse_args()
    if a.cmd == "list":
        for p in sorted(glob.glob(os.path.join(SK, "*.mjs"))):
            if os.path.basename(p) not in ("lib.mjs", "run.mjs"):
                first = open(p, encoding="utf-8").readline().strip("/ \n")
                print(f"{os.path.basename(p)[:-4]:16s} {first}")
    elif a.cmd == "run":
        run(a)
    elif a.cmd == "new":
        dst = os.path.abspath(a.name if a.name.endswith(".mjs") else a.name + ".mjs")
        shutil.copy(resolve(a.src), dst)
        shutil.copy(os.path.join(SK, "lib.mjs"), os.path.join(os.path.dirname(dst), "lib.mjs"))
        print(dst)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
