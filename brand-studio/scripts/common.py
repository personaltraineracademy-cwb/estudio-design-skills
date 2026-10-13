"""Shared helpers for brand-studio scripts: paths, rendering, fonts-as-outlines, colours."""
import glob
import json
import math
import os
import re
import shutil
import sys

HOME = os.path.expanduser("~")
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_ROOT = os.path.dirname(os.path.realpath(SKILL_DIR))   # pasta com as skills irmãs (repo, plugin ou ~/.claude/skills)
LOGO_SKILL = next((p for p in (os.environ.get("LOGO_DESIGN_SKILL"), os.path.join(SKILLS_ROOT, "logo-design"),
                               os.path.join(HOME, ".claude", "skills", "logo-design")) if p and os.path.isdir(p)),
                  os.path.join(HOME, ".claude", "skills", "logo-design"))


def _project_dir():
    """Pasta de trabalho do usuário (biblioteca/, .env, testes/): ESTUDIO_DIR > pasta acima das skills, se tiver
    biblioteca/ ou .env (layout do repositório de desenvolvimento) > diretório atual."""
    if os.environ.get("ESTUDIO_DIR"):
        return os.path.abspath(os.environ["ESTUDIO_DIR"])
    up = os.path.dirname(SKILLS_ROOT)
    if any(os.path.exists(os.path.join(up, n)) for n in ("biblioteca", ".env")):
        return up
    return os.getcwd()


PROJECT_DIR = _project_dir()
_lib = os.path.join(PROJECT_DIR, "biblioteca")
LIBRARY_DIR = os.environ.get("BRAND_LIBRARY") or (_lib if os.path.isdir(_lib) else
                                                  os.path.join(HOME, "Documents", "logos"))
CATALOG_DIR = os.path.join(LIBRARY_DIR, "_catalogo")


def _load_env(path=os.path.join(PROJECT_DIR, ".env")):
    """KEY=VALUE lines from design/.env → os.environ (empty values ignored; never overrides variables already set)."""
    if not os.path.isfile(path):
        return
    for line in open(path, encoding="utf-8-sig"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and v and not os.environ.get(k):
            os.environ[k] = v


_load_env()
CACHE = os.path.join(HOME, ".cache", "brand-studio")
FONT_DIR = os.path.join(CACHE, "fonts")
MODEL_DIR = os.path.join(CACHE, "models")

for d in (FONT_DIR, MODEL_DIR):
    os.makedirs(d, exist_ok=True)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------ tools on this machine
def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    pats = [os.path.join(HOME, "AppData", "Local", "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg*", "ffmpeg-*", "bin",
                         "ffmpeg.exe"),
            r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"]
    for p in pats:
        hits = glob.glob(p)
        if hits:
            return hits[0]
    return None


def find_chrome():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if os.path.exists(p):
            return p
    for n in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        if shutil.which(n):
            return shutil.which(n)
    return None


# ------------------------------------------------------------------ rendering
def svg_to_png(svg=None, out=None, width=None, height=None, background=None, svg_path=None):
    """Render an SVG (string or path) to PNG bytes with resvg; writes `out` if given."""
    import resvg_py
    kw = {"width": int(width) if width else None, "height": int(height) if height else None}
    if background:
        kw["background"] = background
    data = resvg_py.svg_to_bytes(svg_string=svg, svg_path=svg_path, **{k: v for k, v in kw.items() if v})
    data = bytes(data)
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "wb") as fh:
            fh.write(data)
    return data


def html_screenshot(html_path, png, width, height):
    """Screenshot an HTML file with headless Chrome (reuses logo-design's robust implementation)."""
    sys.path.insert(0, os.path.join(LOGO_SKILL, "scripts"))
    import render_png  # noqa: E402
    render_png.screenshot_html(html_path, png, width, height)


def viewbox(svg_text):
    m = re.search(r'viewBox="\s*([-\d.]+)[ ,]+([-\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)', svg_text)
    if m:
        return tuple(float(x) for x in m.groups())
    w = re.search(r'\bwidth="([\d.]+)', svg_text)
    h = re.search(r'\bheight="([\d.]+)', svg_text)
    return (0.0, 0.0, float(w[1]) if w else 256.0, float(h[1]) if h else 256.0)


def svg_inner(svg_text):
    """Inner markup of an SVG (without the root element and <title>), for embedding in <g>."""
    s = re.sub(r"<\?xml[^>]*>|<!DOCTYPE[^>]*>|<!--.*?-->", "", svg_text, flags=re.S)
    s = re.sub(r"^.*?<svg\b[^>]*>", "", s, count=1, flags=re.S)
    s = re.sub(r"</svg>\s*$", "", s.strip(), flags=re.S)
    return re.sub(r"<title>.*?</title>", "", s, flags=re.S)


def recolor(svg_text, colour):
    """Force every fill/stroke paint to one colour (keeps 'none'). Assumes real holes, not white fake cut-outs."""
    s = re.sub(r'(fill|stroke)="(?!none)[^"]*"', lambda m: f'{m[1]}="{colour}"', svg_text)
    s = re.sub(r'(fill|stroke)\s*:\s*(?!none)[^;"}]+', lambda m: f"{m[1]}:{colour}", s)
    s = re.sub(r'stop-color="[^"]*"', f'stop-color="{colour}"', s)
    if 'fill="' not in s.split(">", 1)[0]:
        s = re.sub(r"<svg\b", f'<svg fill="{colour}"', s, count=1)
    return s


def wrap_svg(w, h, body, title="", bg=None):
    rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    t = f"<title>{title}</title>" if title else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}">'
            f"{t}{rect}{body}</svg>\n")


def write(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


# ------------------------------------------------------------------ colour
def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def luminance(h):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = hex_to_rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def rgb_to_cmyk(h):
    r, g, b = (c / 255 for c in hex_to_rgb(h))
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    return tuple(round(x * 100) for x in ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k), (1 - b - k) / (1 - k), k))


# ------------------------------------------------------------------ fonts → outlines
class Font:
    """A TTF/OTF font that turns text into SVG path data (no live <text> in deliverables)."""

    def __init__(self, path):
        from fontTools.ttLib import TTFont
        self.file = path
        self.tt = TTFont(path)
        self._clean = set()
        self.gs = self.tt.getGlyphSet()
        self.cmap = self.tt.getBestCmap()
        self.upm = self.tt["head"].unitsPerEm
        os2 = self.tt["OS/2"]
        self.cap = (getattr(os2, "sCapHeight", 0) or int(self.upm * 0.7)) / self.upm
        self.xh = (getattr(os2, "sxHeight", 0) or int(self.upm * 0.5)) / self.upm
        self.kern = self._kern_pairs()

    def _kern_pairs(self):
        """Pair kerning from GPOS PairPos (format 1 pairs and format 2 classes), first value wins."""
        self._class_kern = []
        pairs = {}
        try:
            gpos = self.tt["GPOS"].table
        except KeyError:
            return pairs
        for lookup in gpos.LookupList.Lookup:
            for st in lookup.SubTable:
                if getattr(st, "ExtSubTable", None):
                    st = st.ExtSubTable
                fmt = getattr(st, "Format", None)
                if fmt == 1 and hasattr(st, "PairSet"):
                    for g1, ps in zip(st.Coverage.glyphs, st.PairSet):
                        for rec in ps.PairValueRecord:
                            v = getattr(rec.Value1, "XAdvance", 0) if rec.Value1 else 0
                            if v:
                                pairs.setdefault((g1, rec.SecondGlyph), v)
                elif fmt == 2 and hasattr(st, "Class1Record"):
                    self._class_kern.append((set(st.Coverage.glyphs), st.ClassDef1.classDefs,
                                             st.ClassDef2.classDefs, st.Class1Record))
        return pairs

    def kern_value(self, a, b):
        v = self.kern.get((a, b))
        if v is not None:
            return v
        for cov, cd1, cd2, recs in self._class_kern:
            if a in cov:
                r = recs[cd1.get(a, 0)].Class2Record[cd2.get(b, 0)]
                x = getattr(r.Value1, "XAdvance", 0) if r.Value1 else 0
                if x:
                    return x
        return 0

    def glyph(self, ch):
        g = self.cmap.get(ord(ch))
        if g is None:
            g = self.cmap.get(ord("?"), ".notdef")
        return g

    def _remove_overlaps(self, names):
        """Fonts (variable ones especially) have overlapping contours; knock-outs (evenodd) would show holes."""
        todo = [n for n in set(names) if n not in self._clean]
        if not todo:
            return
        try:
            from fontTools.ttLib.removeOverlaps import removeOverlaps
            removeOverlaps(self.tt, glyphNames=todo)
            self.gs = self.tt.getGlyphSet()
        except Exception:
            pass
        self._clean.update(todo)

    def advances(self, s, size, tracking=0.0):
        k = size / self.upm
        names = [self.glyph(c) for c in s]
        self._remove_overlaps(names)
        adv = []
        for i, g in enumerate(names):
            a = self.gs[g].width * k
            if i + 1 < len(names):
                a += self.kern_value(g, names[i + 1]) * k + tracking * size
            adv.append(a)
        return names, adv

    def width(self, s, size, tracking=0.0):
        return sum(self.advances(s, size, tracking)[1])

    def fit_size(self, s, width, tracking=0.0):
        return width / self.width(s, 1.0, tracking)

    def path(self, s, size, x, baseline, tracking=0.0):
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen
        pen = SVGPathPen(self.gs)
        k = size / self.upm
        names, adv = self.advances(s, size, tracking)
        cx = x
        for g, a in zip(names, adv):
            self.gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, baseline)))
            cx += a
        return pen.getCommands()

    def path_on_circle(self, s, size, cx, cy, r, start_deg=-90, tracking=0.0, outside=True, centre=True):
        """Text along a circle. outside=True reads clockwise on top; False reads counter-clockwise (bottom arc)."""
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen
        pen = SVGPathPen(self.gs)
        k = size / self.upm
        names, adv = self.advances(s, size, tracking)
        total = sum(adv)
        sweep = math.degrees(total / r)
        a = start_deg - (sweep / 2 if centre else 0) if outside else start_deg + (sweep / 2 if centre else 0)
        for g, w in zip(names, adv):
            mid = a + math.degrees((w / 2) / r) * (1 if outside else -1)
            t = math.radians(mid)
            if outside:   # glyph baseline on the circle, glyph pointing outward
                rot = t + math.pi / 2
                px, py = cx + r * math.cos(t), cy + r * math.sin(t)
            else:         # bottom arc, glyph upright reading left→right, baseline on circle
                rot = t - math.pi / 2
                px, py = cx + r * math.cos(t), cy + r * math.sin(t)
            c, sn = math.cos(rot), math.sin(rot)
            # local glyph space: x centred on advance, y up → rotate & place
            ox = -w / 2
            m = (k * c, k * sn, k * sn, -k * c, px + ox * c, py + ox * sn)
            self.gs[g].draw(TransformPen(pen, m))
            a += math.degrees(w / r) * (1 if outside else -1)
        return pen.getCommands()


def font_path(name_or_path):
    """Resolve a font: existing file path, a file in the font cache, or a Google Fonts family (downloaded)."""
    if os.path.isfile(name_or_path):
        return name_or_path
    if name_or_path.lower().endswith((".ttf", ".otf")):
        cand = [p for p in glob.glob(os.path.join(FONT_DIR, "**", name_or_path), recursive=True) if os.path.isfile(p)]
        if cand:
            return cand[0]
    from fonts import get_font  # noqa: E402
    return get_font(name_or_path)


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
