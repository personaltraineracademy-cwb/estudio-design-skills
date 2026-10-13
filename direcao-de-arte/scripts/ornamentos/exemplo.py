"""Família de EXEMPLO (modelo para as outras): pílulas/etiquetas — mostra o contrato em uso."""
from .nucleo import amostra, elemento, texto, largura, cap, ret


def pilula(f, txt="AO VIVO", cheia=True, ponto=True, corpo=34):
    cp = cap(f.fonte_texto) * corpo
    tw = largura(f.fonte_texto, txt, corpo, 0.08)
    ph, pv = corpo * 0.9, cp * 0.85
    pr = cp * 0.42 if ponto else 0
    w = tw + 2 * ph + (2 * pr + cp * 0.5 if ponto else 0)
    h = cp + 2 * pv
    bg, fg = (f.acento, f.sobre_acento) if cheia else ("none", f.tinta)
    corpo_svg = f'<path d="{ret(f.traco / 2, f.traco / 2, w - f.traco, h - f.traco, h / 2)}" fill="{bg}"' + (
        f' stroke="{f.tinta}" stroke-width="{f.traco}"/>' if not cheia else "/>")
    x = ph
    if ponto:
        corpo_svg += f'<circle cx="{x + pr:.2f}" cy="{h / 2:.2f}" r="{pr:.2f}" fill="{fg if cheia else f.acento}"/>'
        x += 2 * pr + cp * 0.5
    t, _ = texto(f.fonte_texto, txt, corpo, x, pv + cp, fg, 0.08)
    return elemento(w, h, corpo_svg + t, f"pílula {'cheia' if cheia else 'contorno'}", "exemplo",
                    nota="status curto (≤ 3 palavras); raio = metade da altura")


@amostra("exemplo", "pílulas")
def _amostras(f):
    return [pilula(f), pilula(f, cheia=False), pilula(f, "20H30", ponto=False)]
