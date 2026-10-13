"""Compara um logo, peça ou página candidato com os EXEMPLOS calibrados do usuário (o que é bom).

Uso:
  python comparar.py candidato.svg|png [--client Cliente] [--k 6] [-o comparacao.png] [--mercado 3]

Faz:
  1. acha na biblioteca os projetos mais parecidos (CLIP, 1 por projeto) e, se pedir, logos de mercado;
  2. lê o nível de cada projeto em biblioteca/<Cliente>/_calibracao.md (Cxx · pasta · nível) e as notas públicas
     de references/calibracao-logos.md;
  3. monta uma folha: candidato grande + vizinhos com "Cxx · nível · média · semelhança";
  4. diz a régua mínima: o candidato tem que igualar a melhor média vizinha e não pode ser quase cópia (≥ 0,93).
Sem biblioteca ou sem índice: avisa e manda calibrar só pela tabela de references/calibracao-logos.md.
Precisa de: brand-studio (library.py, CLIP via fastembed) e um índice (`library.py index`).
"""
import argparse
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
STUDIO = os.path.join(os.path.dirname(os.path.realpath(SKILL)), "brand-studio", "scripts")
sys.path.insert(0, STUDIO)
QUASE_COPIA = 0.93   # mesma faixa do library.py novelty (cópia vetorizada de um logo ≈ 0,99)


def notas_publicas():
    """ID → (média, nível) de todas as tabelas references/calibracao-*.md (logos, peças, páginas, elementos)."""
    out = {}
    pasta = os.path.join(SKILL, "references")
    for nome in sorted(os.listdir(pasta)):
        if not (nome.startswith("calibracao") and nome.endswith(".md")):
            continue
        for linha in open(os.path.join(pasta, nome), encoding="utf-8"):
            m = re.match(r"\|\s*([A-Z]+\d+)\s*\|.*\|\s*([\d,]+)\s*\|\s*\*\*([^*]+)\*\*", linha)
            if m:
                out[m.group(1)] = (float(m.group(2).replace(",", ".")), m.group(3).strip())
    return out


def manifestos(lib):
    """Arquivos de calibração local por caminho: biblioteca/_calibracao*.md → [(ID, caminho, nível)]."""
    out = []
    for nome in sorted(os.listdir(lib)) if os.path.isdir(lib) else []:
        if nome.startswith("_calibracao") and nome.endswith(".md"):
            for linha in open(os.path.join(lib, nome), encoding="utf-8"):
                m = re.match(r"\s*([A-Z]+\d+)\s*·\s*(.+?)\s*·\s*(.+)$", linha)
                if m and os.path.isfile(m.group(2)):
                    out.append((m.group(1), m.group(2), m.group(3).strip()))
    return out


def calibracao_local(lib, cliente):
    """pasta do projeto → Cxx, lendo biblioteca/<Cliente>/_calibracao.md."""
    mapa = {}
    for c in ([cliente] if cliente else [d for d in os.listdir(lib) if not d.startswith("_")]):
        p = os.path.join(lib, c, "_calibracao.md")
        if not os.path.isfile(p):
            continue
        for linha in open(p, encoding="utf-8"):
            m = re.match(r"\s*(C\d+)\s*·\s*([^·/]+)", linha)
            if m:
                mapa[f"{c}/{m.group(2).strip()}".lower()] = m.group(1)
    return mapa


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("candidato")
    ap.add_argument("--client")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--mercado", type=int, default=0, help="quantos logos de mercado mostrar também")
    ap.add_argument("--exemplos", type=int, default=4,
                    help="quantos exemplos do estúdio (biblioteca/_calibracao*.md: peças, páginas, logos de teste)")
    ap.add_argument("-o", "--saida", default="comparacao.png")
    a = ap.parse_args()

    try:
        import library as L
    except Exception as e:
        sys.exit(f"brand-studio/scripts/library.py não encontrado ou sem dependências ({e}). "
                 "Calibre pela tabela de references/calibracao-logos.md.")
    if not os.path.exists(os.path.join(L.CATALOG_DIR, "catalog.sqlite")):
        sys.exit("Sem índice da biblioteca. Rode: python ../brand-studio/scripts/library.py index "
                 "(ou calibre só pela tabela de references/calibracao-logos.md).")

    con = L.db()
    qv = L.embed_query_image(a.candidato)
    rows, mat = L.load_matrix(con, "casa", client=a.client)
    vistos, viz = set(), []
    for s, r in (L.ranked(rows, mat, qv, 200) if rows else []):
        if r[2] in vistos:
            continue
        vistos.add(r[2]); viz.append((s, r))
        if len(viz) == a.k:
            break
    merc = []
    if a.mercado:
        mrows, mmat = L.load_matrix(con, "mercado")
        merc = L.ranked(mrows, mmat, qv, a.mercado) if mrows else []

    notas, local = notas_publicas(), calibracao_local(L.LIBRARY_DIR, a.client)
    print(f"Candidato: {a.candidato}\n")
    melhor = None
    itens = []
    for s, r in viz:
        cid = local.get(r[2].lower())
        media, nivel = notas.get(cid, (None, "sem calibração"))
        if media and (melhor is None or media > melhor[0]):
            melhor = (media, cid, r[2])
        alerta = "  ← QUASE CÓPIA" if s >= QUASE_COPIA else ""
        rot = f"{cid or '—'} · {nivel} · {media if media else '?'} · {s:.2f}"
        print(f"  {s:.3f}  {r[2]:<34} {cid or '—':<4} {nivel:<14} média {media if media else '?'}{alerta}")
        itens.append((r[3], rot))
    for s, r in merc:
        print(f"  {s:.3f}  [mercado] {os.path.basename(r[3])}")
        itens.append((r[3], f"mercado · {s:.2f}"))

    # exemplos do estúdio listados por caminho (peças, páginas, logos aprovados fora do índice)
    est = []
    if a.exemplos:
        import numpy as np
        for cid, arq, nivel in manifestos(L.LIBRARY_DIR):
            try:
                est.append((float(np.dot(L.embed_query_image(arq), qv)), cid, arq, nivel))
            except Exception:
                continue
        est = sorted(est, reverse=True)[:a.exemplos]
    for s, cid, arq, nivel in est:
        media = notas.get(cid, (None,))[0]
        if media and (melhor is None or media > melhor[0]):
            melhor = (media, cid, os.path.basename(arq))
        print(f"  {s:.3f}  [estúdio] {os.path.basename(arq):<26} {cid:<5} {nivel:<14} média {media if media else '?'}")
        itens.append((arq, f"{cid} · {nivel} · {media if media else '?'} · {s:.2f}"))

    copia = [s for s, _ in viz + list(merc) if s >= QUASE_COPIA]
    print()
    if copia:
        print(f"REPROVA: semelhança {max(copia):.2f} ≥ {QUASE_COPIA} com um logo existente — refazer.")
    if melhor:
        print(f"Régua mínima: igualar ou superar {melhor[1]} ({melhor[2]}, média {melhor[0]}) e ser diferente dele "
              "(critério Df). Dar as 8 notas ao candidato e comparar com a linha da tabela. "
              "Exemplo é piso, não molde: superar e inovar.")
    else:
        print("Vizinhos sem calibração local: comparar com a tabela de references/calibracao-logos.md.")
    folha(a.candidato, itens, a.saida, L)


def fonte(tam):
    """Fonte com acentos: Arial (Windows), Helvetica (macOS) ou DejaVu (Linux); senão a padrão do Pillow."""
    from PIL import ImageFont
    for nome in ("arial.ttf", "Arial.ttf", "/System/Library/Fonts/Helvetica.ttc", "DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nome, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def folha(cand, itens, saida, L):
    from PIL import Image, ImageDraw
    cel, lab = 240, 22
    c, _ = L.thumb_image(cand)
    c = c.convert("RGB").resize((cel * 2, cel * 2))
    cols = 3
    linhas = max(2, -(-len(itens) // cols))
    W, H = cel * 2 + 24 + cols * (cel + 8) + 8, max(cel * 2 + 60, 44 + linhas * (cel + lab + 8))
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f = fonte(14)
    d.text((10, 12), "candidato × exemplos calibrados (nível · média · semelhança)", fill="black", font=fonte(18))
    im.paste(c, (10, 44))
    for n, (arq, rot) in enumerate(itens):
        x = cel * 2 + 24 + (n % cols) * (cel + 8)
        y = 44 + (n // cols) * (cel + lab + 8)
        try:
            t, _ = L.thumb_image(arq)
            im.paste(t.convert("RGB").resize((cel, cel)), (x, y))
        except Exception:
            d.rectangle([x, y, x + cel, y + cel], outline="#999")
        d.text((x + 2, y + cel + 4), rot[:40], fill="#333", font=f)
    os.makedirs(os.path.dirname(os.path.abspath(saida)), exist_ok=True)
    im.save(saida)
    print(f"folha: {saida}")


if __name__ == "__main__":
    main()
