"""3D elements from vectors or text (three.js in headless Chrome) → transparent PNG. Free, local.

Usage:
  python render3d.py --svg simbolo.svg --material chrome -o out/simbolo-3d.png
  python render3d.py --text "50%" --font Anton --material gold --rot 18,-28,0 --depth 0.35 -o out/50-3d.png
  python render3d.py --svg simbolo.svg --material plastic --color "#FF5A1F" --rim "#FFFFFF" --size 1600x1600 -o out/x.png
  python render3d.py --svg simbolo.svg --all-materials -o out/teste      # one image per material + sheet
Materials: chrome · gold · plastic · matte · glass · neon (emissive) · clay
Options: --rot X,Y,Z degrees (default 15,-25,0) · --depth (extrusion, fraction of height, default 0.12) ·
         --bevel 0.02 · --color (base colour) · --rim (rim-light colour) · --bg "#hex" (default transparent)
Vectors: every filled path is extruded (holes respected). Text is converted to outlines first (fonts.py).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Font, find_chrome, font_path, recolor, svg_inner, viewbox, wrap_svg  # noqa: E402

THREE = "https://cdn.jsdelivr.net/npm/three@0.170.0"
MATERIALS = ["chrome", "gold", "plastic", "matte", "glass", "neon", "clay"]

HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:transparent;overflow:hidden}</style>
<script type="importmap">{"imports":{"three":"__THREE__/build/three.module.js","three/addons/":"__THREE__/examples/jsm/"}}</script>
</head><body><script type="module">
import * as THREE from 'three';
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const P = __PARAMS__;
const W = P.w, H = P.h;
const renderer = new THREE.WebGLRenderer({antialias: true, alpha: true, preserveDrawingBuffer: true});
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
if (P.bg) renderer.setClearColor(P.bg, 1); else renderer.setClearColor(0x000000, 0);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
const col = new THREE.Color(P.color);
const mats = {
  chrome: new THREE.MeshPhysicalMaterial({color: 0xffffff, metalness: 1, roughness: 0.08, clearcoat: 1}),
  gold:   new THREE.MeshPhysicalMaterial({color: 0xf5c04a, metalness: 1, roughness: 0.18, clearcoat: 0.6}),
  plastic:new THREE.MeshPhysicalMaterial({color: col, metalness: 0, roughness: 0.28, clearcoat: 1, clearcoatRoughness: 0.08}),
  matte:  new THREE.MeshStandardMaterial({color: col, metalness: 0, roughness: 0.85}),
  glass:  new THREE.MeshPhysicalMaterial({color: col, metalness: 0, roughness: 0.04, transmission: 1, thickness: 1.2, ior: 1.45, attenuationColor: col, attenuationDistance: 2}),
  neon:   new THREE.MeshStandardMaterial({color: col, emissive: col, emissiveIntensity: 1.6, roughness: 0.4}),
  clay:   new THREE.MeshStandardMaterial({color: col, metalness: 0, roughness: 1}),
};
const mat = mats[P.material] || mats.plastic;
const metal = P.material === 'chrome' || P.material === 'gold';
scene.environmentIntensity = metal ? 1.0 : 0.45;
const data = new SVGLoader().parse(P.svg);
const group = new THREE.Group();
for (const path of data.paths) {
  const fill = path.userData?.style?.fill;
  if (fill === 'none') continue;
  const shapes = SVGLoader.createShapes(path);
  for (const s of shapes) {
    const geo = new THREE.ExtrudeGeometry(s, {depth: P.depth, bevelEnabled: P.bevel > 0, bevelThickness: P.bevel,
      bevelSize: P.bevel * 0.8, bevelSegments: 6, curveSegments: 48});
    group.add(new THREE.Mesh(geo, mat));
  }
}
// centre, flip Y (SVG y-down), normalise to unit height
const box = new THREE.Box3().setFromObject(group); const c = box.getCenter(new THREE.Vector3()); const sz = box.getSize(new THREE.Vector3());
group.children.forEach(m => m.geometry.translate(-c.x, -c.y, -c.z));
const k = 2 / Math.max(sz.x, sz.y); group.scale.set(k, -k, k);
group.rotation.set(THREE.MathUtils.degToRad(P.rot[0]), THREE.MathUtils.degToRad(P.rot[1]), THREE.MathUtils.degToRad(P.rot[2]));
scene.add(group);
const key = new THREE.DirectionalLight(0xffffff, metal ? 2.2 : 1.6); key.position.set(3, 4, 5); scene.add(key);
const rim = new THREE.DirectionalLight(new THREE.Color(P.rim), 3.0); rim.position.set(-4, 2, -3); scene.add(rim);
scene.add(new THREE.AmbientLight(0xffffff, metal ? 0.25 : 0.1));
const cam = new THREE.PerspectiveCamera(28, W / H, 0.1, 100);
// fit: distance so the rotated bounding sphere fills ~80% of the frame
const r = new THREE.Box3().setFromObject(group).getBoundingSphere(new THREE.Sphere()).radius;
const fov = THREE.MathUtils.degToRad(cam.fov); const dist = r / Math.sin(fov / 2) * (W >= H ? 1.0 : W / H) * 1.02;
cam.position.set(0, 0, dist); cam.lookAt(0, 0, 0);
renderer.render(scene, cam);
document.title = 'done';
</script></body></html>"""


def text_svg(text, font):
    f = Font(font_path(font))
    size = 100 / f.cap
    w = f.width(text, size, 0.0)
    return wrap_svg(w, 100, f'<path fill="#000" d="{f.path(text, size, 0, 100, 0.0)}"/>')


def render(svg, out, a, material):
    W, H = (int(v) for v in a.size.lower().split("x"))
    vx, vy, vw, vh = viewbox(svg)
    depth = a.depth * vh
    params = {"w": W, "h": H, "svg": svg, "material": material, "color": a.color, "rim": a.rim, "bg": a.bg,
              "rot": [float(v) for v in a.rot.split(",")], "depth": depth, "bevel": a.bevel * vh}
    page = HTML.replace("__THREE__", THREE).replace("__PARAMS__", json.dumps(params))
    tmp = tempfile.mkdtemp()
    hp = os.path.join(tmp, "scene.html")
    open(hp, "w", encoding="utf-8").write(page)
    chrome = find_chrome()
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    shot = os.path.join(tmp, "shot.png")
    cmd = [chrome, "--headless=new", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
           "--enable-unsafe-swiftshader", "--use-angle=swiftshader", "--ignore-gpu-blocklist",
           "--default-background-color=00000000", f"--window-size={W},{H}", "--virtual-time-budget=20000",
           f"--user-data-dir={os.path.join(tmp, 'p')}", f"--screenshot={shot}", "file:///" + hp.replace("\\", "/")]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    if not os.path.exists(shot):
        raise SystemExit("falha ao renderizar 3D (sem screenshot)")
    from PIL import Image
    im = Image.open(shot).convert("RGBA")
    if not a.bg and im.getchannel("A").getextrema()[1] == 0:
        raise SystemExit("render vazio — WebGL indisponível?")
    bbox = im.getchannel("A").getbbox() if not a.bg else None
    if bbox and a.trim:
        im = im.crop(bbox)
    im.save(out)
    print(out, im.size)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--svg"); ap.add_argument("--text"); ap.add_argument("--font", default="Anton")
    ap.add_argument("--material", default="plastic", choices=MATERIALS); ap.add_argument("--all-materials", action="store_true")
    ap.add_argument("--color", default="#FF5A1F"); ap.add_argument("--rim", default="#FFFFFF")
    ap.add_argument("--rot", default="15,-25,0"); ap.add_argument("--depth", type=float, default=0.12)
    ap.add_argument("--bevel", type=float, default=0.02); ap.add_argument("--bg")
    ap.add_argument("--size", default="1200x1200"); ap.add_argument("--no-trim", dest="trim", action="store_false")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    if a.text:
        svg = text_svg(a.text, a.font)
    elif a.svg:
        svg = open(a.svg, encoding="utf-8").read()
        svg = recolor(svg, "#000000")   # material decides colour; keep geometry only
    else:
        raise SystemExit("use --svg ou --text")
    if a.all_materials:
        outs = [render(svg, f"{a.out}-{m}.png", a, m) for m in MATERIALS]
        from PIL import Image
        ims = [Image.open(p).convert("RGBA") for p in outs]
        th = 360
        ims = [im.resize((max(1, int(th * im.width / im.height)), th)) for im in ims]
        sheet = Image.new("RGBA", (sum(i.width for i in ims) + 20 * (len(ims) + 1), th + 40), (40, 40, 40, 255))
        x = 20
        for im in ims:
            sheet.alpha_composite(im, (x, 20))
            x += im.width + 20
        sheet.save(a.out + "-sheet.png")
        print(a.out + "-sheet.png")
    else:
        render(svg, a.out if a.out.endswith(".png") else a.out + ".png", a, a.material)


if __name__ == "__main__":
    main()
