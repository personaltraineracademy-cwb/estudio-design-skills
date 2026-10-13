"""Raster finishing effects (local, no upload): chain them on key visuals, posters, textures — never on the logo master.

Usage:
  python fx.py in.png out.png grain:0.06
  python fx.py kv.png kv-riso.png riso:#FF4D2A,#1A1A1A,6 grain:0.05
  python fx.py photo.jpg ht.png duotone:#1A1A1A,#F8C100 halftone:10,45,#1A1A1A,#F8C100
Effects (applied left→right):
  grain:AMOUNT                      film grain (0.02–0.12)
  halftone:CELL,ANGLE,INK,PAPER     AM halftone dots from luminance
  riso:INK1,INK2,OFFSET             two-ink risograph look with misregistration (px) on paper #F2EEE6
  dither:INK,PAPER[,bayer]          Floyd–Steinberg (or Bayer 8×8) 1-bit in two colours
  duotone:DARK,LIGHT                map luminance to a two-colour ramp
  posterize:LEVELS                  flat colour bands
  glow:RADIUS,STRENGTH              soft bloom from highlights
  vignette:STRENGTH                 darken edges
  paper:#HEX                        flatten transparency on a colour
"""
import math
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from common import hex_to_rgb  # noqa: E402


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def to_arr(im):
    return np.asarray(im.convert("RGB"), dtype=np.float32)


def from_arr(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def ramp(l, c0, c1):
    t = (l / 255.0)[..., None]
    return np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t


def grain(im, amount=0.06):
    a = to_arr(im)
    rng = np.random.default_rng(7)
    n = rng.normal(0, 255 * float(amount), a.shape[:2])[..., None]
    return from_arr(a + n)


def halftone(im, cell=10, angle=45, ink="#1A1A1A", paper="#F5F5F5"):
    cell, angle = int(cell), float(angle)
    g = im.convert("L")
    big = g.rotate(angle, expand=True, fillcolor=255)
    W, H = big.size
    small = big.resize((max(1, W // cell), max(1, H // cell)), Image.BILINEAR)
    s = np.asarray(small, np.float32) / 255.0
    yy, xx = np.mgrid[0:H, 0:W]
    cy, cx = (yy % cell) - cell / 2 + 0.5, (xx % cell) - cell / 2 + 0.5
    r = (1 - s[np.minimum(yy // cell, s.shape[0] - 1), np.minimum(xx // cell, s.shape[1] - 1)]) * cell * 0.72
    mask = (np.hypot(cx, cy) <= r).astype(np.uint8) * 255
    m = Image.fromarray(mask, "L").rotate(-angle, expand=True, fillcolor=0)
    mw, mh = m.size
    m = m.crop(((mw - im.width) // 2, (mh - im.height) // 2, (mw - im.width) // 2 + im.width,
                (mh - im.height) // 2 + im.height))
    out = Image.new("RGB", im.size, paper)
    out.paste(Image.new("RGB", im.size, ink), (0, 0), m)
    return out


def riso(im, ink1="#FF4D2A", ink2="#1A1A1A", offset=6):
    a = to_arr(im)
    l = lum(a) / 255.0
    paper = np.array(hex_to_rgb("#F2EEE6"), np.float32)
    d1 = np.clip(1.2 - l * 1.4, 0, 1)            # mid-tones → ink 1
    d2 = np.clip(0.55 - l, 0, 1) * 1.8           # shadows → ink 2
    o = int(offset)
    d2 = np.roll(np.roll(d2, o, axis=1), o // 2, axis=0)
    rng = np.random.default_rng(3)
    d1 *= rng.uniform(0.85, 1.0, d1.shape)
    out = paper.copy() * np.ones_like(a)
    for d, ink in ((d1, ink1), (d2, ink2)):      # multiply inks like real overprint
        c = np.array(hex_to_rgb(ink), np.float32) / 255.0
        out = out * (1 - d[..., None] * (1 - c))
    return from_arr(out)


def dither(im, ink="#1A1A1A", paper="#F5F5F5", mode="fs"):
    g = im.convert("L")
    if mode == "bayer":
        b = np.array([[0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26], [12, 44, 4, 36, 14, 46, 6, 38],
                      [60, 28, 52, 20, 62, 30, 54, 22], [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
                      [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21]], np.float32) / 64 * 255
        a = np.asarray(g, np.float32)
        t = np.tile(b, (a.shape[0] // 8 + 1, a.shape[1] // 8 + 1))[: a.shape[0], : a.shape[1]]
        m = a > t
    else:
        m = np.asarray(g.convert("1"), bool)
    c0, c1 = np.array(hex_to_rgb(ink), np.float32), np.array(hex_to_rgb(paper), np.float32)
    return from_arr(np.where(m[..., None], c1, c0))


def duotone(im, dark="#1A1A1A", light="#F8C100"):
    return from_arr(ramp(lum(to_arr(im)), hex_to_rgb(dark), hex_to_rgb(light)))


def posterize(im, levels=4):
    from PIL import ImageOps
    return ImageOps.posterize(im.convert("RGB"), max(1, int(math.log2(max(2, int(levels))))))


def glow(im, radius=30, strength=0.8):
    a = to_arr(im)
    hi = np.clip((lum(a) - 150) / 105, 0, 1)[..., None] * a
    b = to_arr(from_arr(hi).filter(ImageFilter.GaussianBlur(float(radius))))
    return from_arr(a + b * float(strength))


def vignette(im, strength=0.5):
    a = to_arr(im)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / math.sqrt(2)
    return from_arr(a * (1 - float(strength) * d[..., None] ** 2))


def paper(im, colour="#F5F5F5"):
    bg = Image.new("RGBA", im.size, colour)
    bg.alpha_composite(im.convert("RGBA"))
    return bg.convert("RGB")


FX = {"grain": grain, "halftone": halftone, "riso": riso, "dither": dither, "duotone": duotone,
      "posterize": posterize, "glow": glow, "vignette": vignette, "paper": paper}


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return
    im = Image.open(sys.argv[1])
    if im.mode in ("RGBA", "LA", "P"):
        im = paper(im, "#FFFFFF") if "paper:" not in " ".join(sys.argv[3:]) else im
    for spec in sys.argv[3:]:
        name, _, args = spec.partition(":")
        if name not in FX:
            raise SystemExit(f"efeito desconhecido: {name}")
        im = FX[name](im, *[x for x in args.split(",") if x]) if args else FX[name](im)
    im.save(sys.argv[2])
    print(sys.argv[2])


if __name__ == "__main__":
    main()
