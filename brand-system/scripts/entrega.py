"""entrega.py — pasta ENTREGA-PARA-DESIGNERS de um projeto de marca: só o que foi aprovado e usado, compacto,
explicado e gerado do estado ATUAL (nunca copiar prévia antiga).

  python entrega.py <projeto> [--saida pasta] [--biblioteca] [--produtos todos linha-a ...]

Estrutura (cada pasta tem LEIA-ME.md; a raiz tem 00-LEIA-ME.md com as regras em 1 minuto):
  01-logos      logo/<conceito>/<cor>/*.svg|png (sem _antigas)         02-cores     paleta.json/.css/.png (brand.json)
  03-tipografia fontes livres usadas (cache de fontes) + OFL            04-elementos curados (entrega.json) + biblioteca
  05-fotos      recortes finais                                         06-pecas     série aprovada (JPG q94)
  07-sites      zips do `site.py pack` + prévias (`previas.py`)          08-manual-e-tokens  PDF + tokens/
  09-fundos     fundos/texturas aprovados
Tudo que NÃO entra: reprovados, testes, rascunhos, pastas `_antigas`, logos de terceiros, pessoa gerada por IA.

`<projeto>/entrega.json` (opcional) curadoria explícita:
  {"elementos": {"<produto>": {"titulo": "...", "itens": [["origem relativa", "destino.svg", "descrição"]]}},
   "fotos": ["imagem/x-recorte.png", ...], "pecas_glob": "serie/*.png", "fundos": ["imagem/fundo.jpg"],
   "manual": "manual/manual.pdf", "sites_zips": "site/_entrega", "sites_previas": "paginas"}
Sem ele, usa padrões (logo/, serie/*.png, manual/manual.pdf, tokens/).
`--biblioteca` roda `ornamentos.exportar --zip` para os produtos (SVG de todas as famílias em 2 fundos).
Lições de projeto real: 1) prévia copiada de rodada antiga = erro nº 1 → gerar de novo; 2) SVG da biblioteca são
milhares → zip por produto + folhas JPG; 3) página-mãe e elementos da marca-mãe entram junto, não só os dos produtos;
4) `pack` do site deixa só os zips (pastas extraídas duplicavam peso).
"""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # console do Windows (cp1252) quebra com acentos e setas
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
FONTES = Path.home() / ".cache" / "brand-studio" / "fonts"


def cp(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def w(base, rel, txt):
    f = base / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(txt.strip("\n") + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projeto")
    ap.add_argument("--saida")
    ap.add_argument("--biblioteca", action="store_true")
    ap.add_argument("--produtos", nargs="*")
    a = ap.parse_args()
    P = Path(a.projeto).resolve()
    K = Path(a.saida).resolve() if a.saida else P / "ENTREGA-PARA-DESIGNERS"
    b = json.loads((P / "brand.json").read_text(encoding="utf-8"))
    cfg = json.loads((P / "entrega.json").read_text(encoding="utf-8")) if (P / "entrega.json").exists() else {}
    nome = b.get("nome_completo") or b.get("name") or P.name
    conta = {}
    for sub in ("01-logos", "02-cores", "03-tipografia", "05-fotos-professores", "06-pecas-aprovadas", "08-manual-e-tokens",
                "09-fundos-e-texturas"):
        shutil.rmtree(K / sub, ignore_errors=True)

    # 01 logos
    n = 0
    for conceito in sorted((P / "logo").glob("*/")) if (P / "logo").exists() else []:
        if not conceito.is_dir() or conceito.name.startswith("_"):
            continue
        for cor in sorted(conceito.iterdir()):
            if not cor.is_dir() or cor.name.startswith("_"):
                continue
            for f in sorted(cor.iterdir()):
                if f.suffix in (".svg", ".png") and not f.name.startswith("_"):
                    cp(f, K / "01-logos" / conceito.name / cor.name / f.name); n += 1
    conta["logos"] = n
    lg = b.get("logo", {})
    w(K, "01-logos/LEIA-ME.md", f"""
# 01 · Logos (aprovados)
SVG = vetor (use este); PNG = prévia. Uma pasta por conceito e por cor. Área de proteção {lg.get('clearspace', '?')} × a altura;
mínimo {lg.get('min_px', '?')} px de altura. O logo não arredonda, não gira e não muda de cor fora destas versões.
{lg.get('clearspace_rule', '')}
""")

    # 02 cores
    seeds = (b.get("color") or {}).get("seeds") or {}
    if seeds:
        paleta = {k: v.get("hex") for k, v in seeds.items()}
        w(K, "02-cores/paleta.json", json.dumps({"base": seeds, "por_produto": {p.get("id"): p.get("colors") for p in b.get("products", [])}},
                                               ensure_ascii=False, indent=2))
        w(K, "02-cores/cores.css", ":root {\n" + "".join(f"  --cor-{k}: {v};\n" for k, v in paleta.items()) + "}")
        try:
            from PIL import Image, ImageDraw
            im = Image.new("RGB", (max(600, 245 * len(seeds) + 20), 320), (236, 231, 220)); d = ImageDraw.Draw(im)
            for i, (k, v) in enumerate(seeds.items()):
                x = 20 + i * 245
                d.rectangle([x, 20, x + 225, 230], fill=v["hex"], outline=(120, 120, 120))
                d.text((x, 242), v.get("name", k), fill=(12, 11, 9)); d.text((x, 264), v["hex"], fill=(12, 11, 9))
            (K / "02-cores").mkdir(parents=True, exist_ok=True); im.save(K / "02-cores" / "paleta.png")
        except Exception as e:
            print("paleta.png:", e)
        linhas = "\n".join(f"| {v.get('name', k)} | `{v['hex']}` |" for k, v in seeds.items())
        w(K, "02-cores/LEIA-ME.md", f"# 02 · Cores\n\n| cor | hex |\n|---|---|\n{linhas}\n\nRegras de uso e contraste: manual (capítulo Cor).")
        conta["cores"] = len(seeds)

    # 03 tipografia (fontes livres do cache; só as famílias do brand.json)
    fams = {}
    for papel, d in (b.get("type") or {}).items():
        if isinstance(d, dict) and d.get("family"):
            fams[papel] = d["family"]
    usadas = set()
    for fam in set(fams.values()):
        slug = fam.lower().replace(" ", "")
        pasta = FONTES / slug
        if pasta.exists():
            for f in pasta.iterdir():
                if f.suffix == ".ttf" or f.name == "OFL.txt":
                    cp(f, K / "03-tipografia" / slug / f.name)
            usadas.add(fam)
    linhas = "\n".join(f"| {p} | {f} |" for p, f in fams.items())
    w(K, "03-tipografia/LEIA-ME.md", f"# 03 · Tipografia\nFontes livres (OFL): pode instalar e redistribuir.\n\n| papel | fonte |\n|---|---|\n{linhas}\n")
    conta["fontes"] = len(usadas)

    # 04 elementos
    cur = cfg.get("elementos") or {}
    for pid, d in cur.items():
        for orig, dest, desc in d.get("itens", []):
            f = P / orig
            if f.exists():
                cp(f, K / "04-elementos" / pid / dest)
    if cur:
        sec = "".join(f"\n## {d.get('titulo', pid)} — `{pid}/`\n| arquivo | o que é |\n|---|---|\n" +
                      "".join(f"| `{dest}` | {desc} |\n" for _, dest, desc in d.get("itens", [])) for pid, d in cur.items())
        w(K, "04-elementos/LEIA-ME.md", "# 04 · Elementos aplicados (lista curada)\nCada elemento tem a cor do seu produto.\n" + sec)
    if a.biblioteca:
        prods = a.produtos or [p.get("id") for p in b.get("products", [])] or ["todos"]
        scripts = HERE.parent.parent / "direcao-de-arte" / "scripts"
        subprocess.run([sys.executable, "-m", "ornamentos.exportar", str(K / "04-elementos" / "biblioteca-completa"),
                        "--produtos", *prods, "--zip"], cwd=str(scripts), check=False)

    # 05 fotos
    for f in cfg.get("fotos", []):
        if (P / f).exists():
            cp(P / f, K / "05-fotos-professores" / Path(f).name)
    # 06 peças
    try:
        from PIL import Image
        n = 0
        for f in sorted(P.glob(cfg.get("pecas_glob", "serie/*.png"))):
            if f.name.startswith("_") or "interface" in f.name:
                continue
            out = K / "06-pecas-aprovadas" / (f.stem + ".jpg"); out.parent.mkdir(parents=True, exist_ok=True)
            Image.open(f).convert("RGB").save(out, "JPEG", quality=94, optimize=True, subsampling=0); n += 1
        conta["pecas"] = n
    except Exception as e:
        print("pecas:", e)
    # 07 sites (zips do site.py pack + prévias)
    zips = P / cfg.get("sites_zips", "site/_entrega")
    if zips.exists():
        for f in zips.iterdir():
            if f.suffix in (".zip", ".txt"):
                cp(f, K / "07-sites" / f.name)
    prev = P / cfg.get("sites_previas", "paginas")
    if prev.exists():
        for f in prev.glob("*.jpg"):
            cp(f, K / "07-sites" / "previas" / f.name)
    # 08 manual e tokens
    m = P / cfg.get("manual", "manual/manual.pdf")
    if m.exists():
        cp(m, K / "08-manual-e-tokens" / "manual-da-marca.pdf")
    for f in (P / "tokens").glob("*") if (P / "tokens").exists() else []:
        if f.is_file():
            cp(f, K / "08-manual-e-tokens" / "tokens" / f.name)
    if (P / "tokens" / "figma").exists():
        shutil.copytree(P / "tokens" / "figma", K / "08-manual-e-tokens" / "tokens" / "figma", dirs_exist_ok=True)
    # 09 fundos
    for f in cfg.get("fundos", []):
        if (P / f).exists():
            cp(P / f, K / "09-fundos-e-texturas" / Path(f).name)

    w(K, "00-LEIA-ME.md", f"""
# {nome} · material para designers
Só o que foi aprovado e usado. Formatos abertos (SVG, PNG/JPG, PDF, CSS/JSON, TTF livre).
Pastas: 01-logos · 02-cores · 03-tipografia · 04-elementos · 05-fotos · 06-pecas · 07-sites · 08-manual-e-tokens · 09-fundos.
Regras em 1 minuto e pendências do cliente: ver `08-manual-e-tokens/manual-da-marca.pdf`.
Gerado por `brand-system/scripts/entrega.py` do estado atual do projeto.
""")
    print(json.dumps(conta, ensure_ascii=False))


if __name__ == "__main__":
    main()
