"""SIMULADOR DA INTERFACE NATIVA: desenha por cima da peça o que o app mostra (Stories, Reels, Feed, anúncio), para
conferir NO OLHO, como um revisor riscando a folha: nada importante embaixo e respiro em volta.

  python interface.py peca.png --modos story-anuncio,reels-anuncio  → peca-interface.png (lado a lado)
  simular(png, modos) → caminho da folha

A GEOMETRIA (retângulos no canvas de 1080 de largura, pior caso) vem da pesquisa de interface nativa (Instagram/Meta), medida em pior caso.
Cada elemento: (tipo, x0, y0, x1, y1, rótulo). Tipos: barra (faixa escura), texto (linhas cinza), icone (círculo),
botao (pílula), progresso (fio), corte (área cortada, hachurada). Mudou o app? Mude só a tabela INTERFACE.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------- geometria
# Pesquisa 9 §11: retângulos MEDIDOS, pior caso de 20 aparelhos, canvas de 1080. Tipos: barra (sombreado),
# progresso, icone (círculo), texto (linha), botao (pílula), corte (zoom/grade). "oficial" = linhas da Meta (amarelo);
# "area" = área de texto do estúdio (verde tracejado, já com 36 px de respiro).
_OFICIAL_916 = [("oficial", 0, 269, 1080, 269, ""), ("oficial", 0, 1248, 1080, 1248, ""),
                ("oficial", 65, 0, 65, 1920, ""), ("oficial", 1015, 0, 1015, 1920, ""),
                ("oficial", 853, 1152, 853, 1920, ""), ("oficial", 853, 1152, 1080, 1152, "")]
_AREA_916 = [("area", 108, 240, 972, 936, ""), ("area", 108, 936, 852, 1248, "")]
INTERFACE = {
    "story-anuncio": dict(H=1920, els=[
        ("barra", 0, 0, 1080, 220, ""),
        ("progresso", 30, 26, 1050, 37, ""),                       # ST1
        ("icone", 30, 52, 136, 163, ""),                            # ST2
        ("texto", 148, 70, 560, 112, "nomedaempresa"),             # ST3
        ("texto", 148, 120, 360, 152, "Anúncio"),
        ("icone", 836, 78, 900, 142, ""),                           # ST4 "…"
        ("icone", 965, 78, 1029, 142, ""),                          # ST5 X
        ("botao", 284, 1642, 796, 1802, "SAIBA MAIS"),             # ST6
    ] + _OFICIAL_916 + _AREA_916),
    "reels-anuncio": dict(H=1920, els=[
        ("barra", 0, 0, 1080, 210, ""),                             # R1+R2
        ("texto", 60, 130, 300, 180, "Reels"),
        ("icone", 912, 1355, 987, 1430, ""), ("icone", 912, 1478, 987, 1553, ""),        # RA3 (4 itens)
        ("icone", 916, 1601, 983, 1668, ""), ("icone", 916, 1716, 983, 1783, ""),
        ("barra", 0, 1440, 1080, 1920, ""),
        ("icone", 75, 1473, 175, 1573, ""), ("texto", 190, 1495, 461, 1550, "nomedoperfil"),   # RA4
        ("botao", 76, 1592, 871, 1746, "Saiba mais  >"),           # RA5
        ("texto", 93, 1755, 877, 1800, "legenda do anúncio…"),     # RA6
        ("texto", 75, 1818, 361, 1893, "Anúncio"),                 # RA7
        ("corte", 0, 0, 71, 1920, ""), ("corte", 1009, 0, 1080, 1920, ""),               # RC zoom
    ] + _OFICIAL_916 + _AREA_916),
    "reels-organico": dict(H=1920, els=[
        ("barra", 0, 0, 1080, 210, ""),
        ("texto", 60, 130, 360, 180, "Reels · Amigos"),
        ("icone", 905, 974, 985, 1054, ""), ("icone", 905, 1124, 985, 1204, ""),          # R3 (6 itens)
        ("icone", 909, 1274, 981, 1346, ""), ("icone", 909, 1424, 981, 1496, ""),
        ("icone", 909, 1574, 981, 1646, ""), ("icone", 900, 1745, 990, 1835, ""),
        ("barra", 0, 1600, 1080, 1920, ""),
        ("icone", 76, 1684, 197, 1806, ""), ("texto", 210, 1700, 703, 1745, "perfil  Seguir"),   # R4/R5
        ("texto", 210, 1755, 600, 1795, "♫ Áudio original"),
        ("texto", 78, 1817, 834, 1867, "legenda… mais"),          # R6
        ("corte", 0, 0, 71, 1920, ""), ("corte", 1009, 0, 1080, 1920, ""),
    ] + _AREA_916),
    "story-organico": dict(H=1920, els=[
        ("barra", 0, 0, 1080, 210, ""),
        ("progresso", 30, 26, 1050, 37, ""),
        ("icone", 30, 52, 136, 163, ""), ("texto", 148, 90, 520, 130, "perfil · 2 h"),
        ("icone", 836, 78, 900, 142, ""), ("icone", 965, 78, 1029, 142, ""),
    ] + _AREA_916),
    "feed-45": dict(H=1350, els=[
        ("icone", 49, 1178, 164, 1294, ""), ("icone", 916, 1178, 1031, 1294, ""),        # F1, F2
        ("corte", 0, 0, 34, 1350, ""), ("corte", 1046, 0, 1080, 1350, ""),               # F4 grade 3:4
        ("area", 80, 80, 1000, 1140, ""), ("area", 200, 1140, 880, 1215, ""),
    ]),
    "feed-11": dict(H=1080, els=[
        ("icone", 49, 908, 164, 1024, ""), ("icone", 916, 908, 1031, 1024, ""),           # Q1, Q2
        ("corte", 0, 0, 135, 1080, ""), ("corte", 945, 0, 1080, 1080, ""),               # Q4 grade 3:4
        ("area", 80, 80, 1000, 870, ""), ("area", 200, 870, 880, 972, ""),
    ]),
}


def _fonte(px):
    for f in ("seguisb.ttf", "segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(f, px)
        except OSError:
            continue
    return ImageFont.load_default()


def sobrepor(im, modo):
    """Desenha a interface `modo` por cima da imagem (cópia). A peça deve ter 1080 de largura."""
    g = INTERFACE[modo]
    k = im.width / 1080
    im = im.convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for tipo, x0, y0, x1, y1, rot in g["els"]:
        x0, y0, x1, y1 = (round(v * k) for v in (x0, y0, x1, y1))
        if tipo == "barra":                       # sombreado do app (degradê para dar contraste aos ícones)
            for i in range(y1 - y0):
                t = i / max(1, y1 - y0)
                a = int(120 * (1 - t) if y0 == 0 else 150 * t)
                d.line((x0, y0 + i, x1, y0 + i), fill=(0, 0, 0, a))
        elif tipo == "progresso":
            d.rounded_rectangle((x0, y0, x1, y1), radius=3, fill=(255, 255, 255, 200))
        elif tipo == "icone":
            d.ellipse((x0, y0, x1, y1), outline=(255, 255, 255, 235), width=max(2, round(4 * k)))
        elif tipo == "texto":
            d.rounded_rectangle((x0, y0, x1, y1), radius=round(8 * k), fill=(255, 255, 255, 170))
        elif tipo == "botao":
            d.rounded_rectangle((x0, y0, x1, y1), radius=round((y1 - y0) / 2), fill=(255, 255, 255, 235))
        elif tipo == "oficial":
            d.line((x0, y0, x1, y1), fill=(255, 214, 0, 220), width=max(2, round(3 * k)))
        elif tipo == "area":
            for i in range(x0, x1, round(24 * k)):
                d.line((i, y0, min(i + round(12 * k), x1), y0), fill=(0, 230, 120, 255), width=max(2, round(3 * k)))
                d.line((i, y1, min(i + round(12 * k), x1), y1), fill=(0, 230, 120, 255), width=max(2, round(3 * k)))
            for j in range(y0, y1, round(24 * k)):
                d.line((x0, j, x0, min(j + round(12 * k), y1)), fill=(0, 230, 120, 255), width=max(2, round(3 * k)))
                d.line((x1, j, x1, min(j + round(12 * k), y1)), fill=(0, 230, 120, 255), width=max(2, round(3 * k)))
        elif tipo == "corte":                     # hachura SÓ dentro do retângulo cortado
            hz = Image.new("RGBA", (x1 - x0, y1 - y0), (255, 40, 80, 60))
            dh = ImageDraw.Draw(hz)
            for x in range(-(y1 - y0), x1 - x0, round(14 * k)):
                dh.line((x, y1 - y0, x + (y1 - y0), 0), fill=(255, 40, 80, 150), width=max(1, round(2 * k)))
            ov.alpha_composite(hz, (x0, y0))
        if rot and tipo in ("texto", "botao", "icone", "corte"):
            f = _fonte(max(12, round(26 * k)))
            cor = (20, 20, 20, 255) if tipo in ("botao", "texto") else (255, 255, 255, 255)
            d.text((x0 + round(16 * k), y0 + round(10 * k)), rot, fill=cor, font=f)
    return Image.alpha_composite(im, ov)


def simular(png, modos, out=None):
    im = Image.open(png).convert("RGB")
    vs = [im] + [sobrepor(im, m).convert("RGB") for m in modos]
    h = 900
    vs = [v.resize((round(v.width * h / v.height), h), Image.LANCZOS) for v in vs]
    S = Image.new("RGB", (sum(v.width for v in vs) + 20 * (len(vs) + 1), h + 70), (34, 34, 34))
    d = ImageDraw.Draw(S)
    x = 20
    for v, rot in zip(vs, ["peça"] + list(modos)):
        S.paste(v, (x, 20))
        d.text((x, h + 32), rot, fill=(230, 230, 230), font=_fonte(22))
        x += v.width + 20
    out = out or png.replace(".png", "-interface.png")
    S.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("png")
    ap.add_argument("--modos", default="story-anuncio,reels-anuncio,reels-organico")
    a = ap.parse_args()
    print(simular(a.png, a.modos.split(",")))
