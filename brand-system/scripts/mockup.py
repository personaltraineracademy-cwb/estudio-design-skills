"""Mockups without Photoshop: Gemini makes the SCENE with a blank surface; code places the exact artwork on it
(perspective warp + the photo's own light/shadow). The AI never redraws the brand.

Usage:
  python mockup.py presets                                   # scene presets
  python mockup.py scene poster -o cenas/poster.png         # generate a blank scene (Gemini, ~US$0.10 at 2K)
  python mockup.py place cena.png arte.png -o out.png [--quad x1,y1,x2,y2,x3,y3,x4,y4]   # tl,tr,br,bl
  python mockup.py make <brand_dir> [--presets poster,celular,outdoor,cartao] [--size 2K]
        → mockups/<preset>.png (scenes cached in mockups/cenas/, reused next time)
The blank surface is found automatically (largest bright, low-saturation quadrilateral); pass --quad if it misses.
Per brand, brand.json "mockups" overrides or adds presets: {"poster-noite": {"art": "aplicacoes/x/pecas/x-1080x1350.png",
"prompt": "…", "aspect": "4:5", "quad": [x1,y1,…]}} — any field is optional for a built-in preset (e.g. only "art"
to choose the exact piece). Without "art", the piece of the right size is taken from designer-made folders first,
then the recipes (folders starting with "_" are ignored). Night presets: poster-noite, outdoor-noite, celular-noite.
"""
import argparse
import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _base import STUDIO_SCRIPTS, load_brand, solid, svg_to_png  # noqa: E402

PRESETS = {
    "poster": ("4:5", "feed", "A photograph of a single blank white matte poster pasted flat on a raw grey concrete "
               "wall, front-on view, soft natural daylight from the left with a gentle shadow gradient on the wall, "
               "the poster is completely blank with sharp straight edges and fills about 45% of the frame, centred. "
               "No text, no logos, no people."),
    "outdoor": ("16:9", "outdoor", "A photograph of a large blank white billboard (3:1 proportion) on a tall metal "
                "structure above a Brazilian city avenue at golden hour, seen slightly from below, the billboard face "
                "is completely blank and evenly lit, sharp edges, occupies about 40% of the frame width. No text, no "
                "logos anywhere."),
    "celular": ("4:5", "story", "A photograph of a hand holding a modern smartphone vertically against a softly "
                "blurred gym interior, the phone screen is fully blank bright white and facing the camera almost "
                "front-on, thin bezels, natural light. No text, no icons, no logos on the screen or elsewhere."),
    "cartao": ("4:3", "cartao", "A top-down photograph of two blank white business cards (85x55mm) lying on a dark "
               "walnut desk next to a black pen, soft diffused window light, the cards are completely blank, matte, "
               "sharp edges, the front card is fully visible and slightly rotated. No text or logos."),
    "sacola": ("4:5", "post", "A photograph of a blank white paper shopping bag standing on a light concrete floor "
               "against a plain wall, front face of the bag facing the camera, soft studio light, the front face is "
               "completely blank and flat, sharp edges. No text, no logos."),
    "tela-evento": ("16:9", "banner", "A photograph of a dark conference stage with a large blank white LED screen "
                    "(16:9) behind an empty podium, audience heads softly blurred in the foreground, the screen is "
                    "completely blank and evenly bright. No text, no logos."),
    "poster-noite": ("4:5", "feed", "A night street photograph in a Brazilian city: a single blank white matte poster "
                     "pasted flat on a raw concrete pillar, lit by a cool white LED street lamp from above, wet asphalt "
                     "reflections and soft city bokeh in the background, front-on view, the poster is completely "
                     "blank, evenly lit, sharp straight edges, about 40% of the frame, centred. No text, no logos, no "
                     "people, no neon."),
    "outdoor-noite": ("16:9", "outdoor", "A night photograph of a large blank white backlit billboard (3:1 "
                      "proportion) on a tall metal structure above an elevated urban expressway in São Paulo, white "
                      "LED street lights, a few blurred car light trails below, the billboard face is completely blank "
                      "and evenly glowing, sharp edges, about 40% of the frame width. No text, no logos, no neon."),
    "celular-noite": ("4:5", "story", "A night photograph of a runner's hand holding a modern smartphone vertically "
                      "on a city street, white LED street light and soft blurred city lights behind, the phone screen "
                      "is fully blank bright white, facing the camera almost front-on, thin bezels. No text, no icons, "
                      "no logos, no neon."),
}


def find_quad(img):
    """Largest bright, uniform, low-saturation quadrilateral → 4 corners (tl, tr, br, bl)."""
    import cv2
    import numpy as np
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v, s = hsv[:, :, 2], hsv[:, :, 1]
    area = img.shape[0] * img.shape[1]
    vf = v.astype("float32")
    mu = cv2.blur(vf, (9, 9))
    std = np.sqrt(np.maximum(cv2.blur(vf * vf, (9, 9)) - mu * mu, 0))   # printed/blank surfaces are smooth
    smooth = std < 6
    best, best_score = None, 0
    for vt in (240, 230, 220, 210, 200, 190, 180):
        mask = ((v > vt) & (s < 40) & smooth).astype("uint8") * 255
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((15, 15), "uint8"))   # cut thin leaks
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), "uint8"))
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:3]:
            ca = cv2.contourArea(c)
            if ca < 0.02 * area:
                continue
            hull = cv2.convexHull(c).reshape(-1, 2).astype("float32")
            sm, df = hull.sum(1), np.diff(hull, axis=1).ravel()
            q = np.array([hull[sm.argmin()], hull[df.argmin()], hull[sm.argmax()], hull[df.argmax()]], "float32")
            qa = cv2.contourArea(q)
            fill = ca / qa if qa else 0                      # how rectangular the blob really is
            score = fill ** 4 * (ca / area)                  # big AND rectangular wins, across thresholds
            if fill > 0.88 and score > best_score:
                best, best_score = q, score
    if best is None:
        raise SystemExit("não achei a superfície em branco — passe --quad x1,y1,… (tl,tr,br,bl)")
    return best


def place(scene_path, art_path, out, quad=None, inset=-0.008):
    import cv2
    import numpy as np
    scene = cv2.imread(scene_path)
    art = cv2.imread(art_path, cv2.IMREAD_UNCHANGED)
    if art.shape[2] == 4:   # flatten alpha on white
        a = art[:, :, 3:] / 255.0
        art = (art[:, :, :3] * a + 255 * (1 - a)).astype("uint8")
    q = np.array(quad, "float32").reshape(4, 2) if quad else find_quad(scene)
    c = q.mean(0)
    q = c + (q - c) * (1 - inset)          # detection sits a few px inside the edge → grow slightly
    h, w = art.shape[:2]
    src = np.array([[0, 0], [w, 0], [w, h], [0, h]], "float32")
    M = cv2.getPerspectiveTransform(src, q)
    H, W = scene.shape[:2]
    warped = cv2.warpPerspective(art, M, (W, H), flags=cv2.INTER_CUBIC)
    mask = cv2.warpPerspective(np.full((h, w), 255, "uint8"), M, (W, H))
    mask = cv2.GaussianBlur(mask, (3, 3), 0).astype("float32") / 255.0
    # light of the blank surface: luminance normalised to its bright level → multiply (keeps shadows/folds)
    gray = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY).astype("float32")
    inside = gray[mask > 0.5]
    ref = np.percentile(inside, 95) if inside.size else 255
    shade = np.clip(gray / max(ref, 1), 0, 1.15)
    shade = cv2.GaussianBlur(shade, (0, 0), 1.2)[:, :, None]
    lit = np.clip(warped.astype("float32") * shade, 0, 255)
    # a touch of the photo's grain so the print sits in the scene
    noise = (np.random.default_rng(1).normal(0, 2.0, lit.shape)).astype("float32")
    lit = np.clip(lit + noise, 0, 255)
    m3 = mask[:, :, None]
    outimg = (lit * m3 + scene.astype("float32") * (1 - m3)).astype("uint8")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cv2.imwrite(out, outimg)
    return out


def gen_scene(preset, out, size="2K", over=None):
    aspect, _, prompt = PRESETS.get(preset, ("4:5", "feed", ""))
    over = over or {}
    aspect, prompt = over.get("aspect", aspect), over.get("prompt", prompt)
    if not prompt:
        raise SystemExit(f"preset '{preset}' sem prompt (defina em brand.json mockups.{preset}.prompt)")
    base = os.path.splitext(out)[0]
    r = subprocess.run([sys.executable, os.path.join(STUDIO_SCRIPTS, "gemini.py"), "gen", prompt, "-o", base,
                        "--aspect", aspect, "--size", size], capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    made = sorted(glob.glob(base + "-1.png"))
    if not made:
        raise SystemExit(f"Gemini não gerou a cena: {r.stdout[-500:]} {r.stderr[-500:]}")
    os.replace(made[0], out)
    return out


def art_for(b, kind, work):
    """Pick/render the artwork for a preset: an application piece of the right format, or the logo on paper."""
    if kind == "cartao":
        lp = b.path(b.get("logo.primary")) or os.path.join(b.dir, "logo", "wordmark-provisorio.svg")
        txt = solid(open(lp, encoding="utf-8").read(), b.colour("ink"))
        from _base import svg_inner, viewbox, wrap_svg
        vx, vy, vw, vh = viewbox(txt)
        W, H = 1700, 1100
        k = min(W * 0.6 / vw, H * 0.3 / vh)
        body = (f'<rect width="{W}" height="{H}" fill="{b.colour("paper", "#F4F3EF")}"/>'
                f'<g transform="translate({(W - vw * k) / 2:.1f} {(H - vh * k) / 2:.1f}) scale({k:.4f}) '
                f'translate({-vx} {-vy})">{svg_inner(txt)}</g>')
        p = os.path.join(work, "_cartao.png")
        svg_to_png(wrap_svg(W, H, body), p)
        return p
    size = {"feed": "1080x1350", "story": "1080x1920", "outdoor": "3000x1000", "post": "1080x1080",
            "banner": "1920x1080"}[kind]
    def folder(p):
        return os.path.basename(os.path.dirname(os.path.dirname(p)))
    recipes = ["supergrafico", "foto", "tipografico", "padrao", "numeral", "moldura"]
    cands = [c for c in glob.glob(os.path.join(b.dir, "aplicacoes", "*", "pecas", f"*-{size}.png"))
             if not folder(c).startswith("_")]
    # designer-made pieces first, then recipes in order
    pref = sorted(cands, key=lambda c: (recipes.index(folder(c)) + 1 if folder(c) in recipes else 0, c))
    if not pref:
        raise SystemExit(f"sem peça {size} — rode apply.py build com esse formato")
    return pref[0]


def cmd_make(a):
    b = load_brand(a.brand)
    out = os.path.join(b.dir, "mockups")
    cen = os.path.join(out, "cenas")
    os.makedirs(cen, exist_ok=True)
    custom = b.get("mockups") or {}
    for p in a.presets.split(","):
        over = custom.get(p) or {}
        if p not in PRESETS and not over:
            raise SystemExit(f"preset desconhecido: {p} (veja 'mockup.py presets' ou defina brand.json mockups.{p})")
        scene = os.path.join(cen, f"{p}.png")
        if not os.path.exists(scene):
            print(f"cena {p}: gerando no Gemini…")
            gen_scene(p, scene, a.size, over)
        kind = over.get("kind") or PRESETS.get(p, (None, "feed"))[1]
        art = b.path(over["art"]) if over.get("art") else art_for(b, kind, out)
        res = place(scene, art, os.path.join(out, f"{p}.png"), over.get("quad"))
        print("ok", res)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("presets").set_defaults(fn=lambda a: [print(f"{k:<12} {v[0]:<5} arte: {v[1]}") for k, v in
                                                       PRESETS.items()])
    p = sp.add_parser("scene"); p.add_argument("preset", choices=list(PRESETS)); p.add_argument("-o", required=True)
    p.add_argument("--size", default="2K"); p.set_defaults(fn=lambda a: print(gen_scene(a.preset, a.o, a.size)))
    p = sp.add_parser("place"); p.add_argument("scene"); p.add_argument("art"); p.add_argument("-o", required=True)
    p.add_argument("--quad"); p.set_defaults(fn=lambda a: print(place(a.scene, a.art, a.o, [float(x) for x in
                                                                                         a.quad.split(",")]
                                                                      if a.quad else None)))
    p = sp.add_parser("make"); p.add_argument("brand"); p.add_argument("--presets", default="poster,celular,outdoor")
    p.add_argument("--size", default="2K"); p.set_defaults(fn=cmd_make)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
