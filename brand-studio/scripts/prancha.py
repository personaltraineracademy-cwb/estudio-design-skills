"""Prancha de conceito de logo: o logo APLICADO e em cor, pronto para o checkpoint (regra "1ª entrega = 100%").

Monta 1920×1080 com: logo principal no fundo da marca · avatar do Instagram (símbolo) · saco de papel kraft ·
versão negativa (fachada/toldo) · paleta com nomes e HEX · escada do símbolo 64/32/16 px · nome do conceito,
história de 1 frase e nota. Logos de 1 cor são recoloridos por papel (tinta, fundo, acento).

Uso:
  python prancha.py --logo logo.svg --simbolo simbolo.svg --nome "B · Lâmina" \
      --paleta "Tinta:#1E2A38,Farinha:#F6F3EC,Ocre:#D59B3A" \
      --frase "Os 4 cortes da lâmina desenham o M." --nota "3,6 · premium" -o prancha-b.png
  (--paleta: 1ª = tinta do logo, 2ª = fundo, 3ª = acento do avatar, 4ª opcional = papel da embalagem)
"""
import argparse
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

W, H = 1920, 1080


def miolo_svg(caminho, cor):
    """viewBox + conteúdo do SVG com todo preenchimento/traço trocado por `cor` (logo-master de 1 cor)."""
    t = open(caminho, encoding="utf-8").read()
    vb = re.search(r'viewBox="([^"]+)"', t)
    if not vb:
        w = re.search(r'width="([\d.]+)', t); h = re.search(r'height="([\d.]+)', t)
        vb = f"0 0 {w.group(1)} {h.group(1)}"
    else:
        vb = vb.group(1)
    corpo = re.sub(r"(?s)^.*?<svg[^>]*>|</svg>\s*$", "", t)
    corpo = re.sub(r'<rect[^>]*width="100%"[^>]*/>', "", corpo)
    corpo = re.sub(r'(fill|stroke)="(?!none)[^"]*"', lambda m: f'{m.group(1)}="{cor}"', corpo)
    corpo = re.sub(r"(fill|stroke):\s*(?!none)[^;\"]+", lambda m: f"{m.group(1)}:{cor}", corpo)
    if 'fill="' not in corpo and "fill:" not in corpo:
        corpo = f'<g fill="{cor}">{corpo}</g>'
    return vb, corpo


def caixa(caminho, cor, x, y, w, h):
    vb, corpo = miolo_svg(caminho, cor)
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" '
            f'preserveAspectRatio="xMidYMid meet">{corpo}</svg>')


def rotulo(fonte, s, tam, cor, x, y, tracking=0.04):
    return f'<path fill="{cor}" d="{fonte.path(s, tam, x, y, tracking)}"/>'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logo", required=True)
    ap.add_argument("--simbolo", help="símbolo/monograma (padrão: o próprio logo)")
    ap.add_argument("--nome", default="Conceito")
    ap.add_argument("--paleta", required=True, help='"Nome:#HEX,Nome:#HEX,Nome:#HEX[,Nome:#HEX]"')
    ap.add_argument("--frase", default="", help="a história do conceito em 1 frase")
    ap.add_argument("--nota", default="", help='ex.: "3,6 · premium"')
    ap.add_argument("--fonte", default="DM Sans:600", help="fonte dos rótulos da prancha")
    ap.add_argument("-o", "--saida", default="prancha.png")
    a = ap.parse_args()

    cores = [c.split(":", 1) for c in a.paleta.split(",")]
    if len(cores) < 3:
        sys.exit("--paleta precisa de pelo menos 3 cores: tinta, fundo, acento")
    tinta, fundo, acento = cores[0][1], cores[1][1], cores[2][1]
    kraft = cores[3][1] if len(cores) > 3 else "#C9A27A"
    sim = a.simbolo or a.logo
    F = C.Font(C.font_path(a.fonte))

    t = [f'<rect width="{W}" height="{H}" fill="{fundo}"/>',
         rotulo(F, a.nome.upper(), 30, tinta, 110, 140, 0.08),
         caixa(a.logo, tinta, 110, 300, 1000, 420)]
    if a.frase:
        t.append(rotulo(F, a.frase[:110], 22, tinta, 110, 800, 0.0))
    if a.nota:
        t.append(rotulo(F, "NOTA " + a.nota.upper(), 20, tinta, 110, 840, 0.08))
    for i, tam in enumerate((64, 32, 16)):
        t.append(caixa(sim, tinta, 110 + i * 100, 900, tam, tam))
    t.append(f'<rect x="1220" y="0" width="700" height="{H}" fill="#FFFFFF"/>')
    t.append(f'<circle cx="1400" cy="230" r="140" fill="{acento}"/>')
    t.append(caixa(sim, fundo, 1310, 140, 180, 180))
    sx, sy, sw, sh = 1600, 90, 230, 330
    dente = "".join(f"L{sx + i * sw / 12:.1f},{sy + (8 if i % 2 else 0)}" for i in range(13))
    t.append(f'<path d="M{sx},{sy + 8} {dente} L{sx + sw},{sy + sh} L{sx},{sy + sh} Z" fill="{kraft}"/>')
    t.append(f'<rect x="{sx}" y="{sy + 40}" width="{sw}" height="3" fill="#00000018"/>')
    t.append(caixa(a.logo, tinta, sx + 25, sy + 150, sw - 50, 90))
    t.append(f'<rect x="1270" y="500" width="600" height="230" fill="{tinta}"/>')
    t.append(caixa(a.logo, fundo, 1330, 545, 480, 140))
    for i, (nome, cor) in enumerate(cores[:4]):
        x = 1270 + i * 152
        t.append(f'<rect x="{x}" y="800" width="136" height="136" fill="{cor}" stroke="#00000022"/>')
        t.append(rotulo(F, nome.upper()[:12], 16, "#333333", x, 962))
        t.append(rotulo(F, cor.upper(), 16, "#777777", x, 984))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{"".join(t)}</svg>'
    os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
    C.svg_to_png(svg=svg, out=a.saida, width=W)
    print(a.saida)


if __name__ == "__main__":
    main()
