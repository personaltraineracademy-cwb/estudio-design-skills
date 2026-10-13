"""previas.py — prints ATUAIS de um site (rolando de verdade) nos 2 temas e 3 tamanhos, para manual e entrega.

  python previas.py <url-base> <pasta-saida> --rotas /v1/ /solo/pessoa-a/v1/ ...      # lista explícita
  python previas.py <url-base> <pasta-saida> --auto <pasta-out>                    # rotas = pastas com index.html
  opções: --temas escuro,claro  --grade 3   (--grade N também monta grades lado a lado)

Saída por rota: <slug>-1440[-claro].jpg (dobra computador) · <slug>-390[-claro].jpg (dobra celular) ·
<slug>-390-inteira[-claro].jpg (página inteira no celular). O tema entra por `?tema=claro` (botão do template).
Lições: sem ROLAR antes do print, reveal/lazy-load/contadores saem vazios (placeholder cinza, "+0"); mostrar prévia
copiada de uma rodada antiga é o erro mais comum de entrega: gere de novo SEMPRE do build atual.
"""
import argparse, os, re, sys
from pathlib import Path


def slug(rota):
    s = rota.strip("/").replace("/", "-")
    return re.sub(r"[^a-z0-9\-]+", "-", s.lower()) or "home"


def rolar(pg):
    H = pg.evaluate("document.documentElement.scrollHeight"); y = 0
    while y < H:
        pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(170); y += 500
        H = pg.evaluate("document.documentElement.scrollHeight")
    pg.wait_for_timeout(400); pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base"); ap.add_argument("saida")
    ap.add_argument("--rotas", nargs="*", default=[])
    ap.add_argument("--auto")
    ap.add_argument("--temas", default="escuro,claro")
    ap.add_argument("--grade", type=int, default=0)
    a = ap.parse_args()
    rotas = list(a.rotas)
    if a.auto:
        o = Path(a.auto)
        for f in sorted(o.rglob("index.html")):
            rel = f.parent.relative_to(o).as_posix()
            if not rel.startswith(("_next", "404")):
                rotas.append("/" + rel + "/" if rel != "." else "/")
    rotas = ["/" + r.strip("/") + "/" if r.strip("/") else "/" for r in rotas]   # aceita "solo/x/v1" (Git Bash estraga "/solo")
    if not rotas:
        sys.exit("sem rotas")
    from playwright.sync_api import sync_playwright
    from PIL import Image
    out = Path(a.saida); out.mkdir(parents=True, exist_ok=True)
    temas = a.temas.split(",")
    tmp = out / "_t.png"
    shots = {}
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome", ignore_default_args=["--hide-scrollbars"])
        for rota in rotas:
            for tema in temas:
                suf = "" if tema == "escuro" else "-" + tema
                for w, h, tag in ((1440, 900, "1440"), (390, 844, "390")):
                    ctx = br.new_context(viewport={"width": w, "height": h}, is_mobile=w < 700, has_touch=w < 700)
                    pg = ctx.new_page()
                    url = a.base.rstrip("/") + rota + ("?tema=" + tema if tema != "escuro" else "")
                    pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(2200)
                    pg.screenshot(path=str(tmp))
                    Image.open(tmp).convert("RGB").save(out / f"{slug(rota)}-{tag}{suf}.jpg", "JPEG", quality=82, optimize=True)
                    shots[(rota, tema, tag)] = out / f"{slug(rota)}-{tag}{suf}.jpg"
                    if w == 390:
                        rolar(pg)
                        pg.screenshot(path=str(tmp), full_page=True)
                        Image.open(tmp).convert("RGB").save(out / f"{slug(rota)}-390-inteira{suf}.jpg", "JPEG", quality=82, optimize=True)
                    ctx.close()
            print("ok", rota, flush=True)
        br.close()
    tmp.unlink(missing_ok=True)
    if a.grade:
        for tema in temas:
            for tag, tw in (("1440", 640), ("390", 300)):
                ims = [Image.open(shots[(r, tema, tag)]) for r in rotas]
                th = int(ims[0].height * tw / ims[0].width); c = a.grade; rows = -(-len(ims) // c); g = 14
                sh = Image.new("RGB", (c * tw + g * (c + 1), rows * (th + g) + g), (60, 60, 60))
                for i, im in enumerate(ims):
                    sh.paste(im.resize((tw, th), Image.LANCZOS), (g + (i % c) * (tw + g), g + (i // c) * (th + g)))
                sh.save(out / f"_grade-{tag}-{tema}.png")


if __name__ == "__main__":
    main()
