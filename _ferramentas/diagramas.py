"""Gera os diagramas SVG neutros das skills (padrões aprovados, sem arte de cliente).

Uso: python _ferramentas/diagramas.py [--png]   (--png renderiza uma prévia com resvg, se instalado)
Saída:
  revisao-de-design/assets/ciclo-de-revisao.svg
  direcao-de-arte/assets/diagramas/{zonas-seguras,escala-de-raios,escala-de-espaco,camadas}.svg
  criacao-de-sites/assets/diagramas/dobra-padrao.svg
  brand-studio/assets/padroes-logo/gramaticas-de-lockup.svg
"""
import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TINTA, PAPEL, CINZA, LINHA, DESTAQUE, ALERTA = "#1A1A1A", "#F6F5F1", "#8A8A85", "#D5D3CC", "#3D5AFE", "#E5484D"
FONTE = "font-family='Inter, Helvetica, Arial, sans-serif'"


def svg(w, h, corpo):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONTE}>"
            f"<rect width='{w}' height='{h}' fill='{PAPEL}'/>{corpo}</svg>\n")


def txt(x, y, s, tam=14, cor=TINTA, peso=400, anc="start"):
    return f"<text x='{x}' y='{y}' font-size='{tam}' font-weight='{peso}' fill='{cor}' text-anchor='{anc}'>{s}</text>"


def rect(x, y, w, h, fill="none", stroke=TINTA, sw=1.5, rx=0, dash=None, op=1):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    return (f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' fill='{fill}' stroke='{stroke}' "
            f"stroke-width='{sw}' opacity='{op}'{d}/>")


def zonas():
    """Zonas seguras em 1080 px de largura, escala 1/4."""
    k, o = 0.25, ""
    formatos = [("9:16 Stories/Reels", 1080, 1920, (108, 240, 972, 1248), (852, 936)),
                ("4:5 Feed", 1080, 1350, (80, 80, 1000, 1140), None),
                ("1:1 Post", 1080, 1080, (80, 80, 1000, 870), None)]
    x0 = 40
    for nome, W, H, (zx1, zy1, zx2, zy2), dente in formatos:
        o += txt(x0, 40, nome, 16, peso=700)
        o += rect(x0, 56, W * k, H * k, fill="#FFFFFF", stroke=TINTA)
        o += rect(x0 + zx1 * k, 56 + zy1 * k, (zx2 - zx1) * k, (zy2 - zy1) * k, fill=DESTAQUE, stroke=DESTAQUE, op=0.12)
        o += rect(x0 + zx1 * k, 56 + zy1 * k, (zx2 - zx1) * k, (zy2 - zy1) * k, stroke=DESTAQUE, dash="5 4")
        if dente:
            dx, dy = dente
            o += rect(x0 + dx * k, 56 + dy * k, (zx2 - dx) * k, (zy2 - dy) * k, fill=PAPEL, stroke=ALERTA, dash="3 3")
            o += txt(x0 + W * k + 6, 56 + (dy + 120) * k, "ícones", 11, ALERTA)
        o += txt(x0, 56 + H * k + 22, f"texto: x {zx1}–{zx2} · y {zy1}–{zy2}", 12, CINZA)
        if dente:
            o += txt(x0, 56 + H * k + 40, f"abaixo de y {dente[1]}: x ≤ {dente[0]}", 12, CINZA)
        x0 += W * k + 60
    base = 56 + 1920 * k + 80
    o += txt(40, base, "Área azul = texto, logo, olhos e boca. Fundo e decoração podem sangrar.", 13)
    o += txt(40, base + 20, "Texto que precisa ser lido: maiúscula ≥ 34 px numa arte de 1080.", 13, CINZA)
    return svg(x0 - 20, base + 40, o)


def raios():
    o = txt(40, 44, "Escala de raios (arte 1080 px)  ·  site = arte ÷ 2,75", 18, peso=700)
    itens = [("0", 0, "sinal / destaque"), ("16", 16, "chip, rótulo"), ("28", 28, "cartão, foto"),
             ("44", 44, "painel grande"), ("pílula", 60, "botão, tag")]
    x = 40
    for nome, r, papel in itens:
        if nome == "pílula":
            o += rect(x, 112, 120, 56, fill="#FFFFFF", stroke=TINTA, sw=2, rx=28)
        else:
            o += rect(x, 80, 120, 120, fill=TINTA if r == 0 else "#FFFFFF", stroke=TINTA, sw=2, rx=r)
        o += txt(x + 60, 230, nome, 16, peso=700, anc="middle") + txt(x + 60, 250, papel, 12, CINZA, anc="middle")
        x += 160
    o += txt(40, 300, "O reto é o sinal, a curva é a escola: elementos levemente arredondados por padrão;", 13)
    o += txt(40, 320, "canto reto só como destaque com função. O logo nunca arredonda sem pedido.", 13)
    return svg(x, 345, o)


def espaco():
    o = txt(40, 44, "Espaço é sistema: 12 · 24 · 40", 18, peso=700)
    escala = [4, 8, 12, 16, 24, 32, 40, 48, 64, 96, 128, 160, 200]
    x = 40
    for v in escala:
        cor = DESTAQUE if v in (12, 24, 40) else CINZA
        o += rect(x, 220 - v, 28, v, fill=cor, stroke="none", op=0.85)
        o += txt(x + 14, 240, str(v), 11, TINTA if v in (12, 24, 40) else CINZA, anc="middle")
        x += 44
    o += txt(40, 280, "12 = dentro do grupo (título → apoio)  ·  24 = entre grupos  ·  40 = entre blocos", 13)
    o += txt(40, 300, "Margem esquerda = direita. Seção com respiro ≥ 96 px. Nada \"no olho\".", 13, CINZA)
    return svg(max(x, 640), 325, o)


def camadas():
    nomes = ["0 fundo", "1 textura / grão", "2 atrás (palavra atrás da pessoa)", "3 sujeito (foto recortada)",
             "4 frente", "5 tarjas", "6 texto e logo (sempre nítidos)", "7 acabamento"]
    o = txt(40, 44, "Pilha de camadas de uma peça", 18, peso=700)
    for i, n in enumerate(reversed(nomes)):
        y = 70 + i * 44
        o += rect(40 + i * 6, y, 420, 34, fill="#FFFFFF", stroke=TINTA, rx=6)
        o += txt(56 + i * 6, y + 22, n, 13)
    o += txt(40, 440, "Contraste medido no pixel da letra (pior trecho), não na média.", 13, CINZA)
    return svg(560, 460, o)


def dobra():
    o = txt(40, 40, "1ª dobra padrão = tela inteira", 18, peso=700)
    # celular 390x844 a 0,5
    x, y, w, h = 40, 70, 195, 422
    o += rect(x, y, w, h, fill="#FFFFFF", rx=18)
    o += rect(x + 12, y + 14, 50, 12, fill=TINTA, stroke="none", rx=2) + rect(x + w - 62, y + 12, 50, 16, rx=8)
    o += txt(x + 18, y + 24, "LOGO", 8, PAPEL, 700)
    c, d = x + w / 2, 30   # eixo central; d desce o bloco para centrar na altura
    o += rect(x + 12, y + 48 + d, w - 24, 120, fill=LINHA, stroke="none", rx=10) + txt(c, y + 112 + d, "imagem", 11, CINZA, anc="middle")
    for i, ww in enumerate((150, 160, 110)):
        o += rect(c - ww / 2, y + 184 + d + i * 22, ww, 14, fill=TINTA, stroke="none", rx=2)
    o += rect(c - 70, y + 258 + d, 140, 8, fill=CINZA, stroke="none", rx=2)
    o += rect(x + 12, y + 290 + d, w - 24, 28, fill=DESTAQUE, stroke="none", rx=14) + txt(c, y + 308 + d, "botão (1 linha)", 10, "#FFFFFF", 700, "middle")
    o += rect(c - 45, y + 330 + d, 90, 6, fill=LINHA, stroke="none", rx=2)
    o += txt(x, y + h + 22, "celular 390 × 844", 12, CINZA)
    # desktop 1440x900 a 0,3: MESMA composição do celular (eixo central), só escala
    X, Y, W, H = 280, 70, 432, 270
    cx = X + W / 2
    o += rect(X, Y, W, H, fill="#FFFFFF", rx=8)
    o += rect(X + 16, Y + 14, 56, 12, fill=TINTA, stroke="none", rx=2) + rect(X + W - 78, Y + 11, 62, 18, rx=9)
    o += txt(X + 22, Y + 24, "LOGO", 8, PAPEL, 700)
    o += rect(cx - 90, Y + 42, 180, 96, fill=LINHA, stroke="none", rx=10) + txt(cx, Y + 94, "imagem", 11, CINZA, anc="middle")
    for i, ww in enumerate((220, 180)):
        o += rect(cx - ww / 2, Y + 152 + i * 22, ww, 15, fill=TINTA, stroke="none", rx=2)
    o += rect(cx - 80, Y + 200, 160, 7, fill=CINZA, stroke="none", rx=2)
    o += rect(cx - 60, Y + 220, 120, 24, fill=DESTAQUE, stroke="none", rx=12)
    o += txt(X, Y + H + 22, "desktop 1440 × 900: mesma composição, só a escala muda", 12, CINZA)
    regras = ["Ordem: imagem → título → apoio → botão → micro, num eixo só.",
              "Logo UMA vez (cabeçalho). Sem eyebrow, selos ou faixa na 1ª tela.",
              "A seção seguinte não aparece. Conteúdo centrado na altura.",
              "≥ 38–50% de área vazia. Botão com rótulo em 1 linha até 360 px."]
    for i, r in enumerate(regras):
        o += txt(280, 380 + i * 22, r, 13, TINTA if i == 0 else CINZA)
    return svg(760, 520, o)


def ciclo():
    o = txt(40, 44, "Ciclo de revisão — máximo 2 rodadas", 18, peso=700)
    caixas = [("A · Portão técnico", "script = 0 erros"), ("B · Régua", "8 notas 0–4"), ("C · Olho", "100% e 25%"),
              ("D · Decisão", "entregar / corrigir / devolver")]
    x = 40
    for i, (t1, t2) in enumerate(caixas):
        o += rect(x, 80, 170, 70, fill="#FFFFFF", rx=12)
        o += txt(x + 85, 110, t1, 14, peso=700, anc="middle") + txt(x + 85, 130, t2, 11, CINZA, anc="middle")
        if i < 3:
            o += f"<path d='M{x + 172} 115 h22' stroke='{TINTA}' stroke-width='1.5' marker-end='url(#s)'/>"
        x += 196
    o = (f"<defs><marker id='s' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto'>"
         f"<path d='M0 0L10 5L0 10z' fill='{TINTA}'/></marker></defs>") + o
    niveis = [("ruim", ALERTA), ("normal", CINZA), ("bom", DESTAQUE), ("premium", TINTA)]
    for i, (n, c) in enumerate(niveis):
        o += rect(40 + i * 120, 190, 108, 30, fill=c, stroke="none", rx=15, op=0.9)
        o += txt(94 + i * 120, 210, n, 13, "#FFFFFF", 700, "middle")
    o += txt(540, 210, "só bom ou premium é mostrado", 13, CINZA)
    passos = ["rodada 1: revisar → corrigir", "rodada 2: revisar → corrigir",
              "depois: revisar → entregar ou DEVOLVER ao usuário (nível + o que falta)"]
    for i, p in enumerate(passos):
        o += txt(40, 265 + i * 24, p, 14, TINTA if i < 2 else ALERTA, 700 if i == 2 else 400)
    return svg(x + 10, 350, o)


def lockups():
    """Gramáticas de lockup aprovadas (banco-de-padroes-de-logo.md), em blocos neutros."""
    W, H, cw, ch = 4, 3, 230, 170
    o = txt(30, 36, "Gramáticas de lockup (blocos = texto; nada de marca real)", 17, peso=700)
    B = lambda x, y, w, h, c=TINTA, r=2: rect(x, y, w, h, fill=c, stroke="none", rx=r)

    def cel(i, rot, desenho):
        cx, cy = 30 + (i % W) * (cw + 14), 56 + (i // W) * (ch + 14)
        return rect(cx, cy, cw, ch, fill="#FFFFFF", stroke=LINHA, rx=10) + desenho(cx + 20, cy + 22) + txt(cx + 14, cy + ch - 12, rot, 11, CINZA)

    d = [
        ("L01 bloco justificado", lambda x, y: B(x, y, 190, 30) + B(x, y + 36, 190, 30) + B(x, y + 72, 190, 22)),
        ("L02 etiqueta vazada", lambda x, y: B(x, y + 6, 60, 22, DESTAQUE, 4) + B(x + 68, y, 122, 34) + B(x, y + 44, 190, 34)),
        ("L03 barra justifica", lambda x, y: B(x, y, 190, 28) + B(x, y + 36, 120, 28) + B(x + 128, y + 44, 62, 12, CINZA) + B(x, y + 72, 90, 28) + B(x + 98, y + 80, 92, 12, CINZA)),
        ("L04 divisória co-branding", lambda x, y: B(x, y + 18, 70, 44) + f"<path d='M{x+95} {y+6} v74' stroke='{TINTA}' stroke-width='2'/>" + B(x + 118, y + 24, 72, 14) + B(x + 118, y + 44, 72, 14)),
        ("L05 endosso espaçado", lambda x, y: B(x, y, 190, 40) + f"<path d='M{x} {y+56} h190' stroke='{TINTA}' stroke-width='1.5'/>" + "".join(B(x + i * 19, y + 66, 12, 8, CINZA, 1) for i in range(10))),
        ("L06 quebra em grade", lambda x, y: B(x, y, 90, 40) + B(x + 100, y + 44, 90, 40) + rect(x + 100, y, 90, 40, fill=LINHA, stroke="none", rx=2) + rect(x, y + 44, 90, 40, fill=LINHA, stroke="none", rx=2)),
        ("L07 condensada × estendida", lambda x, y: B(x + 40, y, 110, 52) + B(x, y + 60, 190, 12, CINZA) + B(x, y + 78, 190, 12, CINZA)),
        ("L09 numeral próprio", lambda x, y: f"<circle cx='{x+95}' cy='{y+40}' r='34' fill='none' stroke='{TINTA}' stroke-width='14'/>" + B(x, y + 6, 40, 68) + B(x + 150, y + 6, 40, 68)),
        ("L11 símbolo na altura do bloco", lambda x, y: B(x, y, 70, 94, DESTAQUE, 8) + B(x + 82, y, 108, 28) + B(x + 82, y + 34, 108, 28) + B(x + 82, y + 68, 108, 26, CINZA)),
        ("L12 palavra-chave em cor", lambda x, y: B(x, y + 14, 100, 30) + B(x + 108, y + 14, 82, 30, DESTAQUE) + B(x, y + 52, 190, 16, CINZA)),
        ("M01 selo com texto em arco", lambda x, y: f"<circle cx='{x+95}' cy='{y+46}' r='44' fill='none' stroke='{TINTA}' stroke-width='2'/><circle cx='{x+95}' cy='{y+46}' r='32' fill='none' stroke='{TINTA}' stroke-width='1'/><circle cx='{x+95}' cy='{y+46}' r='16' fill='{DESTAQUE}'/>" + "".join(f"<circle cx='{x+95+38*__import__('math').cos(a/10*6.283)}' cy='{y+46+38*__import__('math').sin(a/10*6.283)}' r='3' fill='{CINZA}'/>" for a in range(10))),
        ("M04 padrão do símbolo", lambda x, y: "".join(B(x + c * 40 + (r % 2) * 20, y + r * 24, 18, 18, DESTAQUE if (r + c) % 3 == 0 else LINHA, 9) for r in range(4) for c in range(5))),
    ]
    for i, (rot, f) in enumerate(d):
        o += cel(i, rot, f)
    return svg(30 + W * (cw + 14) + 16, 56 + H * (ch + 14) + 20, o)


def kvs():
    """Key visuals aprovados (K01–K05), em blocos neutros, formato 4:5."""
    cw, ch = 176, 220
    o = txt(30, 36, "Key visuals que funcionaram (blocos neutros)", 17, peso=700)
    B = lambda x, y, w, h, c=TINTA, r=2, op=1: rect(x, y, w, h, fill=c, stroke="none", rx=r, op=op)
    logo = lambda cx, cy, c="#FFFFFF": B(cx - 36, cy - 10, 72, 20, c, 3)
    def k1(x, y):
        return (B(x, y, cw, ch, DESTAQUE, 0) + f"<ellipse cx='{x+cw/2}' cy='{y+ch*0.45}' rx='90' ry='90' fill='url(#luz)'/>" + logo(x + cw / 2, y + ch / 2))
    def k2(x, y):
        s = B(x, y, cw, ch, TINTA, 0) + f"<ellipse cx='{x+cw}' cy='{y+ch}' rx='120' ry='120' fill='url(#brilho)'/>"
        s += "".join(rect(x + 12 + c * 54, y + 16 + r * 40, 40, 14, stroke="#FFFFFF", sw=1, rx=7, op=.18) for r in range(5) for c in range(3))
        return s + logo(x + cw / 2, y + ch / 2, "#E2B04A")
    def k3(x, y):
        return (B(x, y, cw, ch, TINTA, 0) + f"<path d='M{x} {y+ch} L{x+cw*0.55} {y+ch*0.35} L{x+cw*0.55} {y} L{x} {y} Z' fill='{ALERTA}'/>"
                + f"<path d='M{x+cw} {y} L{x+cw*0.45} {y+ch*0.65} L{x+cw*0.45} {y+ch} L{x+cw} {y+ch} Z' fill='{ALERTA}'/>" + logo(x + cw / 2, y + ch / 2))
    def k4(x, y):
        s = B(x, y, cw, ch, DESTAQUE, 0)
        s += "".join(f"<circle cx='{x+22+c*44}' cy='{y+52+r*44}' r='14' fill='#FFFFFF' opacity='.09'/>" for r in range(4) for c in range(4))
        return s + B(x + 14, y + 14, 70, 8, "#FFFFFF") + B(x + 14, y + 26, 50, 8, "#FFFFFF") + f"<circle cx='{x+cw/2}' cy='{y+ch/2}' r='30' fill='#FFFFFF'/>" + B(x + cw / 2 - 30, y + ch - 30, 60, 8, "#FFFFFF")
    def k5(x, y):
        return (B(x, y, cw, ch, PAPEL, 0) + rect(x, y, cw, ch, stroke=LINHA) + f"<path d='M{x} {y} L{x+60} {y} L{x} {y+80} Z' fill='{DESTAQUE}'/>"
                + f"<path d='M{x+cw} {y+ch} L{x+cw-60} {y+ch} L{x+cw} {y+ch-80} Z' fill='{DESTAQUE}'/>" + f"<path d='M{x+cw} {y} L{x+cw} {y+50} L{x+cw-40} {y} Z' fill='{DESTAQUE}'/>" + logo(x + cw / 2, y + ch / 2, DESTAQUE))
    nomes = ["K01 luz de estúdio", "K02 escuro + brilho + contorno", "K03 forma gigante diagonal", "K04 padrão tom sobre tom", "K05 formas na borda"]
    o += ("<defs><radialGradient id='luz'><stop offset='0' stop-color='#FFFFFF' stop-opacity='.35'/>"
          "<stop offset='1' stop-color='#FFFFFF' stop-opacity='0'/></radialGradient>"
          "<radialGradient id='brilho'><stop offset='0' stop-color='#E2B04A' stop-opacity='.55'/>"
          "<stop offset='1' stop-color='#E2B04A' stop-opacity='0'/></radialGradient></defs>")
    for i, (f, n) in enumerate(zip((k1, k2, k3, k4, k5), nomes)):
        x = 30 + i * (cw + 16)
        o += (f"<clipPath id='k{i}'><rect x='{x}' y='56' width='{cw}' height='{ch}'/></clipPath>"
              f"<g clip-path='url(#k{i})'>{f(x, 56)}</g>" + txt(x, 56 + ch + 20, n, 11, CINZA))
    return svg(30 + 5 * (cw + 16) + 14, 56 + ch + 40, o)


def arquitetura():
    """Sistema de critério: 3 camadas × 3 momentos, com o aprendizado voltando para os exemplos."""
    o = txt(30, 38, "Sistema de critério do estúdio", 18, peso=700)
    o += txt(30, 60, "3 camadas, usadas igual por todas as skills, em 3 momentos", 12, CINZA)
    cam = [("1 · REGRA", "o que é bom, em palavras", ["régua: 8 critérios 0–4", "gosto: aprovado / reprovado"]),
           ("2 · EXEMPLOS", "como é o bom, em casos", ["calibração: aprovados com nota", "repertório: referências públicas", "padrões por área"]),
           ("3 · PROVA", "isto está bom mesmo?", ["portão técnico (scripts)", "comparar com exemplos", "2ª opinião · arena p/ escolher"])]
    for i, (t1, t2, it) in enumerate(cam):
        x = 30 + i * 250
        o += rect(x, 80, 230, 150, fill="#FFFFFF", rx=12)
        o += txt(x + 16, 106, t1, 14, DESTAQUE, 700) + txt(x + 16, 124, t2, 11, CINZA)
        for j, s in enumerate(it):
            o += f"<circle cx='{x+22}' cy='{146+j*22}' r='3' fill='{TINTA}'/>" + txt(x + 32, 150 + j * 22, s, 12)
    mom = [("ANTES DE CRIAR", "definir alvo: piso, alvo, princípios, o que não repetir"),
           ("DEPOIS DE CRIAR", "portão → régua calibrada → olho → decisão (máx. 2 rodadas)"),
           ("DEPOIS DA APROVAÇÃO", "o aprovado vira exemplo; correção vira regra")]
    for i, (t1, t2) in enumerate(mom):
        x = 30 + i * 250
        o += rect(x, 262, 230, 74, fill=TINTA, stroke="none", rx=12)
        o += txt(x + 16, 288, t1, 12, PAPEL, 700)
        palavras, linha, ys = t2.split(" "), "", 308
        for w in palavras:
            if len(linha + w) > 34:
                o += txt(x + 16, ys, linha.strip(), 11, PAPEL); ys += 15; linha = ""
            linha += w + " "
        o += txt(x + 16, ys, linha.strip(), 11, PAPEL)
        if i < 2:
            o += f"<path d='M{x+232} 299 h16' stroke='{TINTA}' stroke-width='2' marker-end='url(#s)'/>"
    o += (f"<path d='M{530+115} 338 v26 H145 v-26' fill='none' stroke='{DESTAQUE}' stroke-width='2' "
          f"stroke-dasharray='5 4' marker-end='url(#a)'/>")
    o += txt(395, 382, "o sistema cresce: cada aprovação vira exemplo para a próxima criação", 11, DESTAQUE, anc="middle")
    o = (f"<defs><marker id='s' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto'>"
         f"<path d='M0 0L10 5L0 10z' fill='{TINTA}'/></marker><marker id='a' viewBox='0 0 10 10' refX='9' refY='5' "
         f"markerWidth='7' markerHeight='7' orient='auto'><path d='M0 0L10 5L0 10z' fill='{DESTAQUE}'/></marker></defs>") + o
    return svg(790, 400, o)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--png", action="store_true", help="também gera PNG de prévia (precisa de resvg-py)")
    a = ap.parse_args()
    saidas = {
        "revisao-de-design/assets/ciclo-de-revisao.svg": ciclo(),
        "revisao-de-design/assets/arquitetura-do-criterio.svg": arquitetura(),
        "direcao-de-arte/assets/diagramas/zonas-seguras.svg": zonas(),
        "direcao-de-arte/assets/diagramas/escala-de-raios.svg": raios(),
        "direcao-de-arte/assets/diagramas/escala-de-espaco.svg": espaco(),
        "direcao-de-arte/assets/diagramas/camadas.svg": camadas(),
        "criacao-de-sites/assets/diagramas/dobra-padrao.svg": dobra(),
        "brand-studio/assets/padroes-logo/gramaticas-de-lockup.svg": lockups(),
        "brand-studio/assets/padroes-logo/key-visuals.svg": kvs(),
    }
    for rel, conteudo in saidas.items():
        p = RAIZ / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(conteudo, encoding="utf-8", newline="\n")
        print("ok", rel)
        if a.png:
            try:
                import resvg_py
                png = resvg_py.svg_to_bytes(svg_string=conteudo)
                (p.with_suffix(".png")).write_bytes(bytes(png))
            except Exception as e:  # prévia é opcional
                print("  sem PNG:", e, file=sys.stderr)


if __name__ == "__main__":
    main()
