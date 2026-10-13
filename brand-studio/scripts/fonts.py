"""Get open-licence fonts from the Google Fonts repository (OFL/Apache/UFL) into the local cache.

Usage:
  python fonts.py get "Montserrat:800"        # family[:weight]; variable fonts are instanced at that weight
  python fonts.py get "Anton"
  python fonts.py get "Martian Mono:800:wdth=75"   # outros eixos de fonte variável (wdth, opsz, slnt, GRAD…)
  python fonts.py list                        # cached fonts
Prints the path of the .ttf. Weight names: 100..900 (default 400). Italic: "Montserrat:800i".
Licence files are saved next to each font (OFL.txt / LICENSE.txt) — keep them with any deliverable that ships fonts.
"""
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FONT_DIR  # noqa: E402

API = "https://api.github.com/repos/google/fonts/contents/{lic}/{slug}"
RAW = "https://raw.githubusercontent.com/google/fonts/main/{lic}/{slug}/{name}"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "brand-studio"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _list(slug):
    for lic in ("ofl", "apache", "ufl"):
        try:
            return lic, json.loads(_get(API.format(lic=lic, slug=slug)))
        except Exception:
            continue
    raise SystemExit(f"font family not found in google/fonts: {slug}")


def get_font(spec):
    parts = spec.split(":")
    fam, wt = parts[0], (parts[1] if len(parts) > 1 else "")
    extra = {}
    if len(parts) > 2 and parts[2]:
        for kv in parts[2].split(","):
            k, _, v = kv.partition("=")
            extra[k.strip()] = float(v)
    italic = wt.endswith("i")
    weight = int(wt.rstrip("i") or 400)
    slug = re.sub(r"[^a-z0-9]", "", fam.lower())
    folder = os.path.join(FONT_DIR, slug)
    tag = f"{weight}{'i' if italic else ''}" + "".join(f"-{k}{v:g}" for k, v in sorted(extra.items()))
    out = os.path.join(folder, f"{slug}-{tag}.ttf")
    if os.path.exists(out):
        return out
    os.makedirs(folder, exist_ok=True)
    lic, items = _list(slug)
    files = [i["name"] for i in items if i["name"].endswith(".ttf")]
    for i in items:
        if i["name"].upper() in ("OFL.TXT", "LICENSE.TXT", "UFL.TXT"):
            with open(os.path.join(folder, i["name"]), "wb") as fh:
                fh.write(_get(RAW.format(lic=lic, slug=slug, name=i["name"])))
    want_italic = [f for f in files if ("Italic" in f) == italic]
    var = [f for f in want_italic if "[" in f]
    names = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold",
             700: "Bold", 800: "ExtraBold", 900: "Black"}
    static = [f for f in want_italic if "[" not in f and names[weight] in f.replace("Italic", "")]
    if static and not extra:
        src = static[0]
    elif var:
        src = var[0]
    elif want_italic:
        src = want_italic[0]
    else:
        raise SystemExit(f"no TTF found for {spec}")
    raw = os.path.join(folder, src)
    if not os.path.exists(raw):
        with open(raw, "wb") as fh:
            fh.write(_get(RAW.format(lic=lic, slug=slug, name=urllib.request.quote(src))))
    if "[" in src:
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont
        f = TTFont(raw)
        axes = {a.axisTag: (a.minValue, a.maxValue) for a in f["fvar"].axes}
        loc = {}
        for tagname, (lo, hi) in axes.items():
            if tagname == "wght":
                loc["wght"] = max(lo, min(hi, weight))
            elif tagname in extra:
                loc[tagname] = max(lo, min(hi, extra[tagname]))
            else:
                loc[tagname] = None  # drop other axes at default
        instantiateVariableFont(f, {k: v for k, v in loc.items() if v is not None}, inplace=True)
        f.save(out)
    else:
        os.replace(raw, out) if not os.path.exists(out) else None
    return out


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "get":
        for s in sys.argv[2:]:
            print(get_font(s))
    elif len(sys.argv) >= 2 and sys.argv[1] == "list":
        for root, _, fs in os.walk(FONT_DIR):
            for f in fs:
                if f.endswith(".ttf"):
                    print(os.path.join(root, f))
    else:
        print(__doc__)
