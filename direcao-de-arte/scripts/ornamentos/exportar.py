"""Exporta a biblioteca de elementos como SVG (um arquivo por elemento), por produto e por fundo, com folha por família
(JPG) e índice CSV. É o que o designer de fora precisa: o catálogo (`catalogo.py`) só gera folhas PNG.

  cd scripts   # na raiz da skill
  python -m ornamentos.exportar <pasta-saida> [--produtos todos linha-a linha-b linha-c] [--zip]

Saída: <saida>/<produto>/fundo-escuro|fundo-claro/<familia>/NN-nome.svg + _folha-<familia>.jpg + _indice.csv.
--zip: junta os SVG de cada produto em <produto>-svg.zip e apaga as pastas (o conjunto completo tem ~6 mil arquivos).
Ficha padrão: `ficha_exemplo` (ficha de exemplo do catálogo). Para outra marca, passe `--ficha modulo:funcao` (mesma assinatura).
Fundo claro = a ficha com fundo papel e tinta escura. Ordem de grandeza: ~800 elementos por produto e fundo.
"""
import argparse, csv, importlib, os, re, shutil, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ornamentos import carregar_tudo, ficha_exemplo  # noqa: E402
from ornamentos.nucleo import REGISTRO  # noqa: E402
from ornamentos.catalogo import folha  # noqa: E402


def san(s):
    return (re.sub(r"[^\w\-]+", "-", s.lower()).strip("-") or "elemento")[:80]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("saida")
    ap.add_argument("--produtos", nargs="*", default=["todos", "linha-a", "linha-b", "linha-c"])
    ap.add_argument("--ficha", default="")
    ap.add_argument("--papel", default="#ECE7DC"); ap.add_argument("--tinta", default="#0C0B09"); ap.add_argument("--apoio", default="#4A463C")
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args()
    mk = ficha_exemplo
    if a.ficha:
        mod, fn = a.ficha.split(":"); mk = getattr(importlib.import_module(mod), fn)
    carregar_tudo()
    for prod in a.produtos:
        for fundo in ("escuro", "claro"):
            f = mk(prod, 28.0)
            if fundo == "claro":
                f = f.com(fundo=a.papel, tinta=a.tinta, apoio=a.apoio)
            base = os.path.join(a.saida, prod, f"fundo-{fundo}")
            linhas = []
            for fam, gens in sorted(REGISTRO.items()):
                itens = []
                for nome, fn_ in gens:
                    try:
                        itens += fn_(f)
                    except Exception as e:
                        print("falhou", prod, fundo, fam, nome, str(e)[:80])
                if not itens:
                    continue
                d = os.path.join(base, fam); os.makedirs(d, exist_ok=True)
                for i, el in enumerate(itens, 1):
                    n = f"{i:02d}-{san(el.nome)}.svg"
                    open(os.path.join(d, n), "w", encoding="utf-8").write(el.svg)
                    linhas.append((fam, n, el.nome, el.nota, round(el.w), round(el.h)))
                try:
                    png = os.path.join(base, f"_folha-{fam}.png")
                    folha(fam, itens, f, png)
                    from PIL import Image
                    im = Image.open(png).convert("RGB")
                    if im.width > 1800:
                        im = im.resize((1800, int(im.height * 1800 / im.width)), Image.LANCZOS)
                    im.save(png[:-4] + ".jpg", "JPEG", quality=84, optimize=True); os.remove(png)
                except Exception as e:
                    print("folha falhou", fam, str(e)[:80])
            os.makedirs(base, exist_ok=True)
            with open(os.path.join(base, "_indice.csv"), "w", encoding="utf-8-sig", newline="") as fh:
                w = csv.writer(fh, delimiter=";")
                w.writerow(["familia", "arquivo", "nome", "nota", "largura", "altura"]); w.writerows(linhas)
            print(prod, fundo, len(linhas), flush=True)
        if a.zip:
            zp = os.path.join(a.saida, f"{prod}-svg.zip")
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                for fundo in ("fundo-escuro", "fundo-claro"):
                    for dp, dn, fn_ in os.walk(os.path.join(a.saida, prod, fundo)):
                        for x in fn_:
                            if x.endswith(".svg"):
                                full = os.path.join(dp, x); z.write(full, os.path.relpath(full, os.path.join(a.saida, prod)).replace(os.sep, "/"))
            for fundo in ("fundo-escuro", "fundo-claro"):
                b = os.path.join(a.saida, prod, fundo)
                for fam in os.listdir(b):
                    if os.path.isdir(os.path.join(b, fam)):
                        shutil.rmtree(os.path.join(b, fam))


if __name__ == "__main__":
    main()
