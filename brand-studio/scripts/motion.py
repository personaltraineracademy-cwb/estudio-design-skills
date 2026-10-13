"""Logo animation (sting) with HyperFrames (HTML + GSAP → MP4). Each top-level shape of the symbol animates in.

Usage:
  python motion.py --symbol sym.svg --wordmark kit/svg/x-wordmark-escuro.svg --bg "#1A1A1A" -o out/sting
  python motion.py --symbol sym.svg --wordmark wm.svg --size 1080x1920 --style spin --seconds 5 -o out/story
  python motion.py ... --no-render        # only write the project (edit index.html, then `npx hyperframes render`)
Styles: pop (parts scale in, staggered) · spin (parts rotate in from the centre) · drop (parts fall in with bounce)
The symbol should be coloured already (e.g. the 'escuro' colourway). Output: <o>/ (project) and <o>.mp4.
Needs Node 22+ and FFmpeg (found automatically under WinGet). First run downloads the HyperFrames CLI via npx.
"""
import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import find_ffmpeg, svg_inner, viewbox, write  # noqa: E402

HF = "hyperframes@0.8.143"
SVGNS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVGNS)

STYLES = {
    "pop": "{scale: 0, rotation: (i) => (i % 2 ? 25 : -25), transformOrigin: '50% 50%', duration: 0.55, "
           "ease: 'back.out(2.2)', stagger: 0.09}",
    "spin": "{scale: 0.2, rotation: (i) => -180 + i * 40, opacity: 0, transformOrigin: '50% 50%', duration: 0.8, "
            "ease: 'expo.out', stagger: 0.07}",
    "drop": "{y: -420, opacity: 0, duration: 0.7, ease: 'bounce.out', stagger: 0.08}",
}


def parts_of(svg_text):
    """Split the symbol into top-level parts (each becomes an animated <g>)."""
    root = ET.fromstring(svg_text)
    out = []
    for el in list(root):
        tag = el.tag.split("}")[-1]
        if tag in ("title", "desc", "defs", "metadata", "style"):
            continue
        out.append(ET.tostring(el, encoding="unicode"))
    if len(out) == 1 and out[0].startswith("<g"):   # single group → animate its children instead
        g = ET.fromstring(out[0])
        kids = [ET.tostring(k, encoding="unicode") for k in g]
        if len(kids) > 1:
            attrs = " ".join(f'{k}="{v}"' for k, v in g.attrib.items())
            return [f"<g {attrs}>{k}</g>" for k in kids]
    return out


def build(a):
    W, H = (int(v) for v in a.size.lower().split("x"))
    sym = open(a.symbol, encoding="utf-8").read()
    svx, svy, svw, svh = viewbox(sym)
    parts = parts_of(sym)
    wm = open(a.wordmark, encoding="utf-8").read() if a.wordmark else None
    tall = H > W * 1.2
    sym_h = (W * 0.42) if not wm else (H * 0.36 if not tall else W * 0.42)
    sym_w = svw * sym_h / svh
    if wm:
        wvx, wvy, wvw, wvh = viewbox(wm)
        if tall:      # stacked: symbol above wordmark
            wm_w = W * 0.7
            wm_h = wvh * wm_w / wvw
            gap = H * 0.04
            total = sym_h + gap + wm_h
            sx_end, sy_end = (W - sym_w) / 2, (H - total) / 2
            wx, wy = (W - wm_w) / 2, sy_end + sym_h + gap
        else:         # side by side
            wm_h = sym_h * 0.9
            wm_w = wvw * wm_h / wvh
            if sym_w + wm_w + W * 0.05 > W * 0.86:
                k = (W * 0.86) / (sym_w + wm_w + W * 0.05)
                sym_h, sym_w, wm_h, wm_w = sym_h * k, sym_w * k, wm_h * k, wm_w * k
            gap = W * 0.05
            total = sym_w + gap + wm_w
            sx_end, sy_end = (W - total) / 2, (H - sym_h) / 2
            wx, wy = sx_end + sym_w + gap, (H - wm_h) / 2
    sx0, sy0 = (W - sym_w) / 2, (H - sym_h) / 2
    groups = "".join(f'<g class="part">{p}</g>' for p in parts)
    wm_html = ""
    if wm:
        wm_html = (f'<div id="wm" class="clip" data-start="0" data-duration="{a.seconds}" data-track-index="1" '
                   f'style="position:absolute;left:{wx:.1f}px;top:{wy:.1f}px;width:{wm_w:.1f}px;height:{wm_h:.1f}px;'
                   f'clip-path:inset(0 100% 0 0)">'
                   f'<svg xmlns="{SVGNS}" viewBox="{wvx:g} {wvy:g} {wvw:g} {wvh:g}" width="100%" height="100%">'
                   f'{svg_inner(wm)}</svg></div>')
    t_in = 0.35 + 0.09 * len(parts) + 0.5
    move = ""
    if wm:
        move = (f"tl.to('#sym', {{x: {sx_end - sx0:.1f}, y: {sy_end - sy0:.1f}, duration: 0.7, ease: 'expo.inOut'}}, "
                f"{t_in:.2f});\n      tl.to('#wm', {{clipPath: 'inset(0 0% 0 0)', duration: 0.8, ease: 'expo.out'}}, "
                f"{t_in + 0.35:.2f});")
    accent = f"tl.fromTo('#flash', {{opacity: 0.0}}, {{opacity: 0.12, duration: 0.12, yoyo: true, repeat: 1}}, {t_in:.2f});"
    html = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {a.bg}; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #flash {{ position: absolute; inset: 0; background: {a.flash}; opacity: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{a.seconds}" data-width="{W}" data-height="{H}">
      <div id="flash" class="clip" data-start="0" data-duration="{a.seconds}" data-track-index="2"></div>
      <div id="symwrap" class="clip" data-start="0" data-duration="{a.seconds}" data-track-index="0"
           style="position:absolute;left:{sx0:.1f}px;top:{sy0:.1f}px;width:{sym_w:.1f}px;height:{sym_h:.1f}px">
        <svg id="sym" xmlns="{SVGNS}" viewBox="{svx:g} {svy:g} {svw:g} {svh:g}" width="100%" height="100%"
             style="overflow:visible">{groups}</svg>
      </div>
      {wm_html}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.from('#sym .part', {STYLES[a.style]}, 0.25);
      {accent}
      {move}
      tl.to({{}}, {{duration: 0.01}}, {a.seconds - 0.01});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    proj = a.out
    os.makedirs(proj, exist_ok=True)
    write(os.path.join(proj, "index.html"), html)
    write(os.path.join(proj, "package.json"),
          '{"name":"brand-sting","private":true,"type":"module","scripts":{"render":"npx --yes %s render",'
          '"check":"npx --yes %s check"}}\n' % (HF, HF))
    write(os.path.join(proj, "meta.json"), '{"id":"brand-sting","name":"brand sting"}\n')
    print(os.path.join(proj, "index.html"))
    if a.no_render:
        return
    env = dict(os.environ, HYPERFRAMES_SKIP_SKILLS="1")
    ff = find_ffmpeg()
    if ff:
        env["PATH"] = os.path.dirname(ff) + os.pathsep + env.get("PATH", "")
    out_mp4 = os.path.abspath(a.out.rstrip("/\\") + ".mp4")
    cmd = f'npx --yes {HF} render -q {a.quality} -f {a.fps} -o "{out_mp4}"'
    r = subprocess.run(cmd, cwd=proj, env=env, shell=True, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-8:]
    print("\n".join(tail))
    if r.returncode == 0 and os.path.exists(out_mp4):
        print(out_mp4)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbol", required=True); ap.add_argument("--wordmark")
    ap.add_argument("--bg", default="#1A1A1A"); ap.add_argument("--flash", default="#FFFFFF")
    ap.add_argument("--size", default="1920x1080"); ap.add_argument("--seconds", type=float, default=4.5)
    ap.add_argument("--style", default="pop", choices=list(STYLES))
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--quality", default="high")
    ap.add_argument("--no-render", action="store_true"); ap.add_argument("-o", "--out", required=True)
    build(ap.parse_args())


if __name__ == "__main__":
    main()
