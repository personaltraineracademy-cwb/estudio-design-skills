"""Raster → SVG locally with vtracer (sketches on paper, AI/Firefly images, old logos, textures).

Usage:
  python vectorize.py in.png out.svg --preset logo        # 1–2 flat colours, smooth curves, few anchors
  python vectorize.py in.png out.svg --preset poster      # up to ~8 colour layers
  python vectorize.py in.png out.svg --preset detailed    # textures/illustrations
  python vectorize.py in.png out.svg --preset logo --threshold 140 --invert
Presets tune vtracer; --threshold binarises first (logo preset) for clean marks from photos of sketches.
Afterwards run the logo-design audit:  python ~/.claude/skills/logo-design/scripts/svg_audit.py out.svg
Adobe alternative (cloud, often cleaner on photos): Adobe connector `image_vectorize` — needs the image uploaded
to Adobe first (asset_add_file / presigned URL).
"""
import argparse
import os
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):  # console do Windows (cp1252) quebra com acentos e setas
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


PRESETS = {
    "logo": dict(colormode="binary", hierarchical="cutout", mode="spline", filter_speckle=8, color_precision=6,
                 layer_difference=16, corner_threshold=60, length_threshold=6.0, max_iterations=10,
                 splice_threshold=45, path_precision=3),
    "poster": dict(colormode="color", hierarchical="stacked", mode="spline", filter_speckle=6, color_precision=5,
                   layer_difference=28, corner_threshold=60, length_threshold=5.0, max_iterations=10,
                   splice_threshold=45, path_precision=3),
    "detailed": dict(colormode="color", hierarchical="stacked", mode="spline", filter_speckle=2, color_precision=7,
                     layer_difference=12, corner_threshold=45, length_threshold=3.5, max_iterations=10,
                     splice_threshold=45, path_precision=3),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--preset", default="logo", choices=list(PRESETS))
    ap.add_argument("--threshold", type=int, help="binarise at this luminance (0–255) before tracing")
    ap.add_argument("--invert", action="store_true", help="trace light shapes on dark ground")
    ap.add_argument("--max-size", type=int, default=1600, help="downscale large inputs first (px)")
    a = ap.parse_args()
    import vtracer
    from PIL import Image, ImageOps
    im = Image.open(a.inp)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im.convert("RGBA"))
        im = bg
    im = im.convert("RGB")
    im.thumbnail((a.max_size, a.max_size))
    if a.threshold is not None or a.preset == "logo":
        g = ImageOps.grayscale(im)
        t = a.threshold if a.threshold is not None else 128
        g = g.point(lambda v: 255 if v > t else 0)
        if a.invert:
            g = ImageOps.invert(g)
        im = g.convert("RGB")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    tmp = os.path.join(tempfile.mkdtemp(), "in.png")
    im.save(tmp)
    vtracer.convert_image_to_svg_py(tmp, a.out, **PRESETS[a.preset])
    s = open(a.out, encoding="utf-8").read()
    print(f"{a.out}  ({s.count('<path')} paths, {len(s) // 1024} KB)")


if __name__ == "__main__":
    main()
