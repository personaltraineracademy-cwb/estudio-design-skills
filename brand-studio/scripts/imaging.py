"""Image utilities (all local, free): cut-out, upscale, sticker/shadow, SVG cleanup.

Usage:
  python imaging.py cutout foto.jpg -o foto-recorte.png [--model isnet-general-use|u2net_human_seg|birefnet-portrait]
                   [--crop] [--outline 12 --outline-color "#FFFFFF"] [--shadow]
  python imaging.py upscale foto.png -o foto-4x.png [--scale 4] [--model realesrgan-x4plus|realesrgan-x4plus-anime]
  python imaging.py svgclean logo.svg -o logo.min.svg       # SVGO (npx), keeps viewBox
Models: isnet-general-use (default, objects+people) · u2net_human_seg (people) · birefnet-portrait (hair detail,
heavier download). Upscale runs Real-ESRGAN (ncnn/Vulkan) on the GPU; first cut-out downloads its model (~180 MB).
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CACHE, hex_to_rgb  # noqa: E402

ESRGAN = os.path.join(CACHE, "bin", "realesrgan", "realesrgan-ncnn-vulkan" + (".exe" if os.name == "nt" else ""))


def cutout(src, out, model="isnet-general-use", crop=False, outline=0, outline_color="#FFFFFF", shadow=False):
    from PIL import Image, ImageFilter
    from rembg import new_session, remove
    im = Image.open(src).convert("RGB")
    cut = remove(im, session=new_session(model), post_process_mask=True)
    if crop:
        bbox = cut.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if bbox:
            cut = cut.crop(bbox)
    if outline or shadow:
        pad = int(outline * 2 + (cut.width * 0.06 if shadow else 0))
        canvas = Image.new("RGBA", (cut.width + 2 * pad, cut.height + 2 * pad), (0, 0, 0, 0))
        alpha = Image.new("L", canvas.size, 0)
        alpha.paste(cut.getchannel("A"), (pad, pad))
        if shadow:
            sh = alpha.filter(ImageFilter.GaussianBlur(cut.width * 0.025)).point(lambda v: int(v * 0.45))
            layer = Image.new("RGBA", canvas.size, (0, 0, 0, 255))
            layer.putalpha(sh)
            canvas.alpha_composite(layer, (int(cut.width * 0.02), int(cut.width * 0.03)))
        if outline:   # sticker border: dilate the alpha
            grown = alpha.filter(ImageFilter.MaxFilter(outline * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
            border = Image.new("RGBA", canvas.size, hex_to_rgb(outline_color) + (255,))
            border.putalpha(grown)
            canvas.alpha_composite(border)
        canvas.alpha_composite(cut, (pad, pad))
        cut = canvas
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cut.save(out)
    print(out, cut.size)


def upscale(src, out, scale=4, model="realesrgan-x4plus"):
    if not os.path.exists(ESRGAN):
        raise SystemExit(f"Real-ESRGAN não encontrado em {ESRGAN} — rode: python instalar.py --upscale")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    tmp = os.path.join(tempfile.mkdtemp(), "in.png")
    from PIL import Image
    im = Image.open(src)
    alpha = im.getchannel("A") if im.mode == "RGBA" else None
    im.convert("RGB").save(tmp)
    r = subprocess.run([ESRGAN, "-i", tmp, "-o", out, "-n", model, "-s", str(scale)],
                       cwd=os.path.dirname(ESRGAN), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode or not os.path.exists(out):
        raise SystemExit(r.stderr[-800:])
    if alpha is not None:          # keep transparency (ESRGAN works on RGB)
        big = Image.open(out).convert("RGBA")
        big.putalpha(alpha.resize(big.size, Image.LANCZOS))
        big.save(out)
    print(out, Image.open(out).size)


def svgclean(src, out):
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    cmd = f'"{npx}" --yes svgo@3 "{src}" -o "{out}" --multipass'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((r.stdout or r.stderr).strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("cutout"); c.add_argument("src"); c.add_argument("-o", "--out", required=True)
    c.add_argument("--model", default="isnet-general-use"); c.add_argument("--crop", action="store_true")
    c.add_argument("--outline", type=int, default=0); c.add_argument("--outline-color", default="#FFFFFF")
    c.add_argument("--shadow", action="store_true")
    u = sub.add_parser("upscale"); u.add_argument("src"); u.add_argument("-o", "--out", required=True)
    u.add_argument("--scale", type=int, default=4); u.add_argument("--model", default="realesrgan-x4plus")
    s = sub.add_parser("svgclean"); s.add_argument("src"); s.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    if a.cmd == "cutout":
        cutout(a.src, a.out, a.model, a.crop, a.outline, a.outline_color, a.shadow)
    elif a.cmd == "upscale":
        upscale(a.src, a.out, a.scale, a.model)
    elif a.cmd == "svgclean":
        svgclean(a.src, a.out)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
