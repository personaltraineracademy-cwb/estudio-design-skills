#!/usr/bin/env python
"""site.py — fábrica de páginas/sites do estúdio (skill `criacao-de-sites`).

Uma página profissional (Next.js 16 exportação estática, Tailwind 4, GSAP sob demanda) para QUALQUER cliente que já
tenha identidade visual + logo. O contrato de página é o do estúdio (direcao-de-arte/references/padrao-de-pagina.md).

  new        cria o projeto a partir do template e aplica a marca do cliente (cores, fontes, raios, grão, logo, copy)
  marca      mostra (sem criar nada) as cores/fontes/raios derivados de um brand.json + tabela de contraste
  check      build + servidor estático + check_pagina.py + teste_pagina_total.py + peso + copy-diff (resumo)
  pack       gera 3 zips: raiz (domínio/subdomínio), subpasta e fonte (+ LEIA-ME.txt)
  copy-diff  acusa texto na página que NÃO está na copy final (nem nos rótulos neutros de interface)

Exemplos:
  python site.py new ./site-x --marca ./minha-marca \\
      --copy copy.json --logo logo/marca.svg --simbolo logo/marca-simbolo.svg --install
  python site.py new pasta --cores "ink=#111,papel=#eee,destaque=#f50" --fontes "display=Anybody:900,texto=Hanken Grotesk:400/700"
  python site.py check pasta                 # build + as duas baterias do estúdio (0 erros para entregar)
  python site.py check pasta --rapido --sem-total
  python site.py check http://localhost:4173/  # só as duas baterias, contra uma URL
  python site.py pack pasta --subpasta site --site-url https://cliente.com.br --indexar
  python site.py copy-diff pasta/content/copy.json pasta

Regras duras (ver SKILL.md): copy FINAL do cliente (nunca inventada), foto de gente é real (IA só cenário,
Nano Banana 2.1 `--model banana21`), movimento sempre ligado, sem 100vw em layout, dobra = tela inteira.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import zipfile
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
TEMPLATE = SKILL / "assets" / "template"
IGNORAR_COPIA = {"node_modules", ".next", ".check", "_scratch", "_entrega", ".vercel", "out"}
IGNORAR_PREFIXOS = ("out-",)
IGNORAR_ARQUIVOS = {"tsconfig.tsbuildinfo", "next-env.d.ts", ".env", ".env.local"}
ROLES = ("ink", "ink2", "tinta", "papel", "destaque", "sobre_destaque", "acento", "mute")


# ----------------------------------------------------------------------------------------------- util
def out(*a):
    print(*a, flush=True)


def erro(msg: str, code: int = 2):
    print(f"ERRO: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def npm() -> str:
    return shutil.which("npm") or shutil.which("npm.cmd") or "npm"


def run(cmd, cwd=None, env=None, check=False, capture=False, timeout=None):
    e = dict(os.environ)
    e.setdefault("PYTHONIOENCODING", "utf-8")
    if env:
        e.update(env)
    r = subprocess.run(
        cmd, cwd=cwd, env=e, text=True, encoding="utf-8", errors="replace",
        capture_output=capture, timeout=timeout,
    )
    if check and r.returncode != 0:
        erro(f"comando falhou ({r.returncode}): {' '.join(map(str, cmd))}")
    return r


def achar_verificadores() -> Path:
    cands = [
        os.environ.get("CHECK_DIR"),
        str(Path(os.environ["CHECK_PAGINA"]).parent) if os.environ.get("CHECK_PAGINA") else None,
        str(SKILL.parent / "direcao-de-arte" / "scripts"),
        str(Path.home() / ".claude" / "skills" / "direcao-de-arte" / "scripts"),
    ]
    for c in cands:
        if c and (Path(c) / "check_pagina.py").exists():
            return Path(c)
    erro("check_pagina.py não encontrado (defina CHECK_DIR com a pasta direcao-de-arte/scripts)")


def porta_livre() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


# ----------------------------------------------------------------------------------------------- cores
def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_hex(r, g, b) -> str:
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, int(round(v)))) for v in (r, g, b)))


def lum(h: str) -> float:
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = hex_rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contraste(a: str, b: str) -> float:
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mix(a: str, b: str, t: float) -> str:
    ra, rb = hex_rgb(a), hex_rgb(b)
    return rgb_hex(*(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


def norm_hex(h: str) -> str:
    h = h.strip()
    if not re.fullmatch(r"#?[0-9a-fA-F]{3}|#?[0-9a-fA-F]{6}", h):
        erro(f"cor inválida: {h!r}")
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h.lower()


# ----------------------------------------------------------------------------------------------- marca
def _g(d, *path, default=None):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def marca_de_brand(bj: dict) -> dict:
    """brand.json do estúdio -> content/marca.json do site."""
    seeds = _g(bj, "color", "seeds", default={}) or {}
    roles = _g(bj, "color", "palette", "roles", default={}) or {}
    dark, light = roles.get("dark", {}), roles.get("light", {})

    def seed(k):
        v = seeds.get(k)
        return v.get("hex") if isinstance(v, dict) else (v if isinstance(v, str) else None)

    ink = dark.get("bg") or seed("ink") or "#111315"
    papel = light.get("bg") or seed("paper") or "#efece4"
    tinta = dark.get("text") or papel
    ink2 = dark.get("surface") or mix(ink, tinta, 0.07)
    destaque = seed("brand") or dark.get("brand") or "#ff5a1f"
    acento = seed("accent") or dark.get("accent") or destaque
    mute = dark.get("text-muted") or mix(ink, tinta, 0.78)
    sobre = dark.get("on-brand")
    cores = {k: norm_hex(v) for k, v in dict(ink=ink, ink2=ink2, tinta=tinta, papel=papel, destaque=destaque,
                                             mute=mute, acento=acento).items()}
    if not sobre:
        sobre = cores["ink"] if contraste(cores["ink"], cores["destaque"]) >= contraste(cores["tinta"], cores["destaque"]) else cores["tinta"]
    cores["sobre_destaque"] = norm_hex(sobre)

    t = bj.get("type", {}) or {}
    texto_regras = json.dumps(t, ensure_ascii=False).lower()
    caixa = "alta" if re.search(r"caixa alta|maiúscul|maiuscul|uppercase", texto_regras) else "normal"
    d = t.get("display", {}) or {}
    x = t.get("text", {}) or {}
    m = t.get("mono", {}) or {}
    fontes = {
        "display": {"familia": d.get("family") or "Big Shoulders", "peso": int(d.get("weight") or 800), "caixa": caixa},
        "texto": {"familia": x.get("family") or "Archivo", "pesos": _pesos_texto(int(x.get("weight") or 400))},
        "mono": ({"familia": m["family"], "pesos": [int(m.get("weight") or 500)]} if m.get("family") else None),
    }
    r = _g(bj, "shape", "radius", default=0) or 0
    forma = {"sinal": 0, "rotulo": 0, "cartao": 0, "moldura": 0} if not r else {"sinal": 0, "rotulo": 6, "cartao": 10, "moldura": 16}
    fx = " ".join(_g(bj, "texture", "fx", default=[]) or [])
    grao = 0.55 if "grain" in fx else 0
    return {
        "nome": bj.get("name") or "Marca",
        "slug": bj.get("slug") or re.sub(r"[^a-z0-9]+", "-", (bj.get("name") or "marca").lower()).strip("-"),
        "cores": cores,
        "fontes": fontes,
        "forma": forma,
        "grao": grao,
        "logo": {"principal": "logo", "simbolo": "logo-simbolo", "cor_arquivo": "tinta"},
    }


def _pesos_texto(w: int) -> list[int]:
    return [w] if w >= 700 else [w, 700]


def aplicar_overrides(marca: dict, cores: str | None, fontes: str | None, raio: str | None, nome: str | None):
    if nome:
        marca["nome"] = nome
        marca["slug"] = re.sub(r"[^a-z0-9]+", "-", nome.lower()).strip("-")
    if cores:
        dados = set()
        for par in cores.split(","):
            k, _, v = par.partition("=")
            k = k.strip().replace("-", "_")
            if k not in ROLES:
                erro(f"papel de cor desconhecido: {k} (use {', '.join(ROLES)})")
            marca["cores"][k] = norm_hex(v)
            dados.add(k)
        c = marca["cores"]
        # o que não foi dado deriva do que foi (superfície 2, apoio e texto sobre o destaque)
        if "ink" in dados or "tinta" in dados:
            if "ink2" not in dados:
                c["ink2"] = mix(c["ink"], c["tinta"], 0.07)
            if "mute" not in dados:
                c["mute"] = mix(c["ink"], c["tinta"], 0.78)
        if "sobre_destaque" not in dados and ("destaque" in dados or "ink" in dados):
            c["sobre_destaque"] = c["ink"] if contraste(c["ink"], c["destaque"]) >= contraste(c["tinta"], c["destaque"]) else c["tinta"]
    if fontes:
        for par in fontes.split(","):
            k, _, v = par.partition("=")
            k = k.strip()
            partes = [p.strip() for p in v.split(":")]
            if k not in ("display", "texto", "mono"):
                erro(f"papel de fonte desconhecido: {k} (display, texto, mono)")
            if partes[0].lower() in ("", "nenhuma", "none") and k == "mono":
                marca["fontes"]["mono"] = None
                continue
            fam = partes[0]
            pesos = [int(p) for p in partes[1].split("/")] if len(partes) > 1 and partes[1] else None
            if k == "display":
                marca["fontes"]["display"].update({"familia": fam, "peso": (pesos or [800])[0]})
                if len(partes) > 2:
                    marca["fontes"]["display"]["caixa"] = partes[2]
            elif k == "texto":
                marca["fontes"]["texto"] = {"familia": fam, "pesos": pesos or [400, 700]}
            else:
                marca["fontes"]["mono"] = {"familia": fam, "pesos": pesos or [500]}
    if raio is not None:
        vals = [int(v) for v in raio.split(",")]
        if len(vals) == 1:
            vals = [0, vals[0], vals[0] * 2 if vals[0] else 0, vals[0] * 3 if vals[0] else 0]
        marca["forma"] = dict(zip(("sinal", "rotulo", "cartao", "moldura"), vals))


def tabela_contraste(m: dict) -> tuple[list[str], int]:
    c = m["cores"]
    pares = [
        ("texto (tinta) sobre ink", c["tinta"], c["ink"], 7.0),
        ("apoio (mute) sobre ink", c["mute"], c["ink"], 4.5),
        ("texto (tinta) sobre ink-2", c["tinta"], c["ink2"], 4.5),
        ("texto (ink) sobre papel", c["ink"], c["papel"], 7.0),
        ("botão: sobre-destaque sobre destaque", c["sobre_destaque"], c["destaque"], 4.5),
        ("destaque sobre ink (disco, fio, ícone)", c["destaque"], c["ink"], 3.0),
        ("destaque sobre papel (só área grande)", c["destaque"], c["papel"], 1.0),
    ]
    linhas, falhas = [], 0
    for nome, a, b, minimo in pares:
        r = contraste(a, b)
        ok = r >= minimo
        if not ok:
            falhas += 1
        linhas.append(f"  {'ok ' if ok else 'FALHA'}  {r:5.1f}:1  (mín. {minimo:g})  {nome}   {a} / {b}")
    return linhas, falhas


def ler_marca_de(arg: str) -> dict:
    p = Path(arg)
    if p.is_dir():
        p = p / "brand.json"
    if not p.exists():
        erro(f"brand.json não encontrado: {arg}")
    return json.loads(p.read_text(encoding="utf-8")), p.parent


# ----------------------------------------------------------------------------------------------- new
def _copiar_template(destino: Path):
    def ignorar(dirpath, names):
        res = []
        for n in names:
            if n in IGNORAR_COPIA or n in IGNORAR_ARQUIVOS or n.startswith(IGNORAR_PREFIXOS):
                res.append(n)
        return res

    shutil.copytree(TEMPLATE, destino, ignore=ignorar)


def _sem_proibidos_no_svg(svg: str, nome: str):
    if re.search(r"<text\b", svg):
        out(f"  AVISO: {nome} tem <text> vivo: converta em curvas (a fonte do logo não vai junto).")
    if re.search(r"<image\b", svg):
        out(f"  AVISO: {nome} tem <image> embutida: logo tem que ser vetor puro.")


def _processar_foto(foto: Path, alt: str, dest: Path) -> dict:
    from PIL import Image

    im = Image.open(foto).convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    if bbox is None:
        erro("a foto não tem canal alfa (recorte com alfa: use brand-studio/scripts/imaging.py cutout)")
    if bbox == (0, 0, im.width, im.height):
        out("  AVISO: a foto não tem transparência: ela vai aparecer como retângulo. Recorte antes (imaging.py cutout).")
    im = im.crop(bbox)  # centrada pela TINTA (bbox do alfa), nunca pela caixa
    arqs = []
    (dest / "public" / "img").mkdir(parents=True, exist_ok=True)
    for w in (640, 1100):
        if w > im.width and arqs:
            continue
        w_ = min(w, im.width)
        h_ = round(im.height * w_ / im.width)
        im2 = im.resize((w_, h_), Image.LANCZOS)
        nome = f"foto-hero-{w}.webp"
        im2.save(dest / "public" / "img" / nome, "WEBP", quality=82, method=6)
        arqs.append({"src": f"/img/{nome}", "w": w_, "h": h_})
    return {"alt": alt, "arquivos": arqs}


def cmd_new(a):
    dest = Path(a.pasta).resolve()
    if dest.exists() and any(dest.iterdir()):
        if not a.force:
            erro(f"{dest} já existe e não está vazia (use --force para sobrescrever)")
        shutil.rmtree(dest)
    # 1) marca
    base_dir = None
    if a.marca:
        bj, base_dir = ler_marca_de(a.marca)
        marca = marca_de_brand(bj)
    else:
        marca = json.loads((TEMPLATE / "content" / "marca.json").read_text(encoding="utf-8"))
        if not (a.cores or a.fontes):
            out("AVISO: sem --marca, --cores nem --fontes: ficam as cores/fontes neutras do template.")
    aplicar_overrides(marca, a.cores, a.fontes, a.raio, a.nome)
    linhas, falhas = tabela_contraste(marca)
    out(f"marca: {marca['nome']}  (slug {marca['slug']})")
    out("contraste:")
    for l in linhas:
        out(l)
    if falhas:
        out(f"  AVISO: {falhas} par(es) abaixo do mínimo: ajuste --cores antes de seguir (o verificador vai reclamar).")

    # 2) projeto
    _copiar_template(dest)
    (dest / "content").mkdir(exist_ok=True)
    (dest / "content" / "marca.json").write_text(json.dumps(marca, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 3) logo
    logo = a.logo
    simbolo = a.simbolo
    if base_dir and not logo:
        p = _g(bj, "logo", "primary") or _g(bj, "logo", "wordmark")
        logo = str(base_dir / p) if p else None
    if base_dir and not simbolo:
        p = _g(bj, "logo", "symbol")
        simbolo = str(base_dir / p) if p and (base_dir / p).exists() else None
    logos = dest / "assets-src" / "logos"
    logos.mkdir(parents=True, exist_ok=True)
    if logo:
        lp = Path(logo)
        if not lp.exists():
            erro(f"logo não encontrado: {logo}")
        txt = lp.read_text(encoding="utf-8", errors="replace")
        _sem_proibidos_no_svg(txt, lp.name)
        shutil.copy2(lp, logos / "logo.svg")
        if simbolo and Path(simbolo).exists():
            shutil.copy2(simbolo, logos / "logo-simbolo.svg")
        elif (logos / "logo-simbolo.svg").exists():
            (logos / "logo-simbolo.svg").unlink()  # placeholder do template: sem símbolo, o logo principal serve
        out(f"logo: {lp.name}" + (f" + símbolo {Path(simbolo).name}" if simbolo else ""))
    else:
        out("AVISO: sem --logo: ficou o logo de exemplo (palavra MARCA). Troque em assets-src/logos/ e rode `npm run assets`.")

    # 4) copy
    copy_path = dest / "content" / "copy.json"
    copy = json.loads(copy_path.read_text(encoding="utf-8"))
    if a.copy:
        src = Path(a.copy)
        if not src.exists():
            erro(f"copy não encontrada: {a.copy}")
        copy = json.loads(src.read_text(encoding="utf-8"))
        h = copy.get("hero", {})
        if not h.get("h1") or not h.get("cta"):
            erro("a copy precisa ter hero.h1 e hero.cta (schema em lib/copy.ts; veja content/copy.json do template)")
        conhecidas = {"meta", "cabecalho", "hero", "passos", "destaques", "faixa", "faq", "cta_final", "rodape", "modal"}
        extras = [k for k in copy if k not in conhecidas and not k.startswith("_")]
        if extras:
            out(f"  AVISO: chaves da copy sem seção na página-exemplo: {', '.join(extras)} (mapeie para passos/destaques/faq "
                f"ou crie a seção em components/secoes/ e use-a em app/page.tsx)")
        out(f"copy: {src.name}")
    else:
        out("AVISO: sem --copy: ficou o texto de EXEMPLO do template. A página final só pode ter a copy FINAL do cliente.")
    if a.foto:
        if not a.foto_alt:
            erro("--foto exige --foto-alt (texto alternativo da foto)")
        copy.setdefault("hero", {})["imagem"] = _processar_foto(Path(a.foto), a.foto_alt, dest)
        out(f"foto: {Path(a.foto).name} -> public/img/foto-hero-*.webp")
    copy_path.write_text(json.dumps(copy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 5) ativos da marca (fontes woff2, tokens, logos, grão, og, ícones)
    r = run([sys.executable, str(dest / "scripts" / "build-assets.py")], cwd=dest)
    if r.returncode != 0:
        erro("build-assets.py falhou (veja a mensagem acima)")

    # 6) registro
    doc = dest / "docs"
    doc.mkdir(exist_ok=True)
    (doc / "decisoes-do-projeto.md").write_text(
        f"# Decisões — {marca['nome']}\n\nCriado em {time.strftime('%d/%m/%Y')} por `site.py new`.\n\n"
        f"- Origem da marca: {a.marca or '(flags --cores/--fontes ou neutro)'}\n"
        f"- Cores: {json.dumps(marca['cores'], ensure_ascii=False)}\n"
        f"- Fontes: {json.dumps(marca['fontes'], ensure_ascii=False)}\n"
        f"- Forma (raios, px): {json.dumps(marca['forma'])} · grão {marca['grao']}\n\n## Contraste\n```\n" + "\n".join(linhas) + "\n```\n\n"
        "## Ideia gráfica da dobra\n(escrever: qual receita/ideia, por quê, parâmetros)\n\n"
        "## Rodadas e correções\n(cada correção do cliente vira regra aqui, na hora)\n",
        encoding="utf-8",
    )
    if a.install:
        out("npm ci …")
        r = run([npm(), "ci", "--no-audit", "--no-fund"], cwd=dest)
        if r.returncode != 0:
            out("npm ci falhou (rede?). Tente de novo: cd pasta && npm ci")
    out(f"\npronto: {dest}")
    out("próximos passos: ajustar copy/seções · `python site.py check <pasta>` · documentar em docs/decisoes-do-projeto.md")


# ----------------------------------------------------------------------------------------------- marca
def cmd_marca(a):
    bj, _ = ler_marca_de(a.brand)
    m = marca_de_brand(bj)
    aplicar_overrides(m, a.cores, a.fontes, a.raio, None)
    out(json.dumps(m, ensure_ascii=False, indent=2))
    linhas, falhas = tabela_contraste(m)
    out("\ncontraste:")
    for l in linhas:
        out(l)
    sys.exit(1 if falhas else 0)


# ----------------------------------------------------------------------------------------------- copy-diff
class _Texto(HTMLParser):
    SKIP = {"script", "style", "noscript", "template", "svg", "head"}
    ATTRS = ("alt", "aria-label", "title", "placeholder")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.buf: list[str] = []
        self.itens: list[tuple[str, str, str]] = []  # (tipo, texto, contexto)
        self.in_title = False

    def _flush(self, ctx=""):
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if t and not any(s in self.SKIP for s in self.stack if s != "head"):
            self.itens.append(("texto", t, ctx or (self.stack[-1] if self.stack else "")))

    def handle_starttag(self, tag, attrs):
        self._flush()
        d = dict(attrs)
        if tag == "meta":
            nome = d.get("name") or d.get("property") or ""
            if nome in ("description", "og:title", "og:description", "twitter:title", "twitter:description", "application-name"):
                if d.get("content"):
                    self.itens.append(("meta", d["content"].strip(), nome))
        if not any(s in self.SKIP for s in self.stack if s != "head") and tag not in self.SKIP:
            for k in self.ATTRS:
                if d.get(k) and d[k].strip():
                    self.itens.append(("atributo", d[k].strip(), f"{tag}[{k}]"))
        if tag not in ("meta", "link", "br", "img", "input", "hr", "source", "path"):
            self.stack.append(tag)
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
            t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            self.buf = []
            if t:
                self.itens.append(("meta", t, "title"))
            if "title" in self.stack:
                self.stack.remove("title")
            return
        self._flush()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.buf.append(data)


def _folhas(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).startswith("_"):
                continue
            _folhas(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _folhas(v, acc)
    elif isinstance(obj, str):
        acc.append(obj)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        acc.append(str(obj))


def _norm(t: str) -> str:
    t = t.replace("\u200b", "").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", t).strip().casefold()


def _strings_ts(p: Path) -> list[str]:
    if not p.exists():
        return []
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"//[^\n]*", "", s)
    return [m.group(2) for m in re.finditer(r"(['\"`])((?:\\.|(?!\1).)+)\1", s)]


def copy_diff(copy_json: Path, pasta: Path, todas: bool = False, permitir: list[str] | None = None, sil=False) -> list[str]:
    copy = json.loads(copy_json.read_text(encoding="utf-8"))
    permitidas: list[str] = []
    _folhas(copy, permitidas)
    permitidas += _strings_ts(pasta / "lib" / "ui-text.ts")
    marca = pasta / "content" / "marca.json"
    if marca.exists():
        mj = json.loads(marca.read_text(encoding="utf-8"))
        permitidas.append(str(mj.get("nome", "")))
    rot = pasta / "content" / "rotulos.txt"
    if rot.exists():
        permitidas += [l.strip() for l in rot.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    permitidas += permitir or []
    perm_n = [_norm(p) for p in permitidas if p and p.strip()]
    perm_set = set(perm_n)
    out_dir = pasta / "out"
    if not out_dir.exists():
        erro(f"{out_dir} não existe: rode o build antes (npm run build)")
    paginas = sorted(out_dir.rglob("index.html")) if todas else [out_dir / "index.html"]
    if todas and (out_dir / "404.html").exists():
        paginas.append(out_dir / "404.html")
    fora: list[str] = []
    for pg in paginas:
        pr = _Texto()
        pr.feed(pg.read_text(encoding="utf-8", errors="replace"))
        rota = "/" + str(pg.parent.relative_to(out_dir)).replace("\\", "/").strip(".") if pg.name == "index.html" else "/" + pg.name
        vistos = set()
        for tipo, texto, ctx in pr.itens:
            n = _norm(texto)
            if not n or not re.search(r"[a-zà-ÿ]", n):  # só números/pontuação: desenho
                continue
            if n in perm_set or any(n in p for p in perm_n):
                continue
            chave = (tipo, n)
            if chave in vistos:
                continue
            vistos.add(chave)
            fora.append(f"{rota} [{tipo}:{ctx}] «{texto[:90]}»")
    if not sil:
        if fora:
            out(f"copy-diff: {len(fora)} texto(s) na página que NÃO estão na copy final:")
            for f in fora[:60]:
                out("  - " + f)
        else:
            out("copy-diff: ok — todo texto da página está na copy (ou nos rótulos neutros de interface).")
    return fora


def cmd_copy_diff(a):
    pasta = Path(a.pasta).resolve()
    fora = copy_diff(Path(a.copy), pasta, a.todas, a.permitir or [])
    sys.exit(1 if fora else 0)


# ----------------------------------------------------------------------------------------------- check
def _resumo_rel(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def cmd_check(a):
    ver = achar_verificadores()
    alvo = a.alvo
    total = not a.sem_total
    if re.match(r"https?://", alvo):
        saida = Path(a.saida or (Path(os.environ.get("TEMP", ".")) / "site-check")).resolve()
        saida.mkdir(parents=True, exist_ok=True)
        out(f"=== check_pagina  {alvo}")
        r1 = run([sys.executable, str(ver / "check_pagina.py"), alvo, "-o", str(saida)])
        rel = _resumo_rel(saida / "_relatorio.json") or {}
        res = [("check_pagina", len(rel.get("erros", [])), len(rel.get("avisos", [])), r1.returncode)]
        if total:
            out(f"\n=== teste_pagina_total  {alvo}")
            cmd = [sys.executable, str(ver / "teste_pagina_total.py"), alvo, "-o", str(saida / "total")]
            if a.rapido:
                cmd.append("--rapido")
            r2 = run(cmd)
            rt = _resumo_rel(saida / "total" / "_teste-total.json") or {}
            res.append(("teste_total", len(rt.get("erros", [])), len(rt.get("avisos", [])), r2.returncode))
        out("\n=== resumo")
        falhou = False
        for n, e, av, rc in res:
            out(f"  {n:14s} erros={e} avisos={av}")
            falhou |= e > 0 or rc not in (0,)
        out(f"  relatórios em {saida}")
        sys.exit(1 if falhou else 0)

    pasta = Path(alvo).resolve()
    if not (pasta / "package.json").exists():
        erro(f"{pasta} não parece um projeto (sem package.json)")
    env = {}
    if a.subpasta:
        env["NEXT_PUBLIC_BASE_PATH"] = a.subpasta.strip("/")
    for k, v in (("NEXT_PUBLIC_SITE_URL", a.site_url),):
        if v:
            env[k] = v
    if not (pasta / "node_modules").exists() and not a.sem_instalar:
        out("npm ci … (node_modules ausente)")
        r = run([npm(), "ci", "--no-audit", "--no-fund"], cwd=pasta)
        if r.returncode != 0:
            erro("npm ci falhou (rede?). Tente de novo.")
    # as duas baterias + build + peso (scripts/check.mjs do projeto)
    cmd = ["node", str(pasta / "scripts" / "check.mjs"), "--routes", a.rotas]
    if a.no_build:
        cmd.append("--no-build")
    if total:
        cmd.append("--total")
    if a.rapido:
        cmd.append("--rapido")
    if a.subpasta:
        cmd += ["--base", a.subpasta.strip("/")]
    env["CHECK_DIR"] = str(ver)
    r = run(cmd, cwd=pasta, env=env)
    # copy-diff
    copy_json = pasta / "content" / "copy.json"
    fora = []
    if copy_json.exists() and (pasta / "out" / "index.html").exists():
        out("")
        fora = copy_diff(copy_json, pasta, todas=False)
    res = _resumo_rel(pasta / ".check" / "resumo.json") or {}
    out("\n================ RESUMO ================")
    falhou = r.returncode != 0
    for s in res.get("summary", []):
        c = s.get("check", {})
        t = s.get("total")
        linha = f"  {s['rota']:12s} check_pagina erros={c.get('erros')} avisos={c.get('avisos')}"
        if t:
            linha += f" | bateria erros={t.get('erros')} avisos={t.get('avisos')}"
        out(linha)
    out(f"  peso: {'dentro do orçamento' if res.get('sizeOk') else 'ACIMA do orçamento ou não medido'}")
    out(f"  copy-diff: {'ok' if not fora else str(len(fora)) + ' texto(s) fora da copy'}")
    out(f"  relatórios: {pasta / '.check'}")
    if fora:
        falhou = True
    out("  RESULTADO: " + ("REPROVADO" if falhou else "APROVADO (0 erros)"))
    sys.exit(1 if falhou else 0)


# ----------------------------------------------------------------------------------------------- pack
def _zip_dir(src: Path, destino: Path, prefixo: str = ""):
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(src.rglob("*")):
            if f.is_file():
                z.write(f, (Path(prefixo) / f.relative_to(src)).as_posix())


def _zip_fonte(pasta: Path, destino: Path, raiz: str):
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(pasta.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(pasta)
            partes = rel.parts
            if any(p in IGNORAR_COPIA or p.startswith(IGNORAR_PREFIXOS) for p in partes[:-1]) or partes[0] in IGNORAR_COPIA:
                continue
            if f.name in IGNORAR_ARQUIVOS or f.name.startswith(".env.local") or f.name.endswith(".tsbuildinfo"):
                continue
            z.write(f, (Path(raiz) / rel).as_posix())


def _build(pasta: Path, env: dict):
    nm = pasta / ".next"
    if nm.exists():
        shutil.rmtree(nm, ignore_errors=True)  # NEXT_PUBLIC_* é gravado no bundle: cache velho = valor velho
    r = run([npm(), "run", "build"], cwd=pasta, env=env)
    if r.returncode != 0:
        erro("build falhou")
    o = pasta / "out"
    if not (o / "index.html").exists():
        erro("out/index.html não existe depois do build")
    return o


def cmd_pack(a):
    pasta = Path(a.pasta).resolve()
    if not (pasta / "package.json").exists():
        erro(f"{pasta} não parece um projeto")
    marca = json.loads((pasta / "content" / "marca.json").read_text(encoding="utf-8")) if (pasta / "content" / "marca.json").exists() else {}
    slug = marca.get("slug") or pasta.name
    sub = (a.subpasta or slug).strip("/")
    saida = Path(a.saida).resolve() if a.saida else pasta / "_entrega"
    saida.mkdir(parents=True, exist_ok=True)
    if not (pasta / "node_modules").exists():
        out("npm ci …")
        run([npm(), "ci", "--no-audit", "--no-fund"], cwd=pasta, check=True)
    base_env = {"NEXT_PUBLIC_NOINDEX": "0" if a.indexar else "1"}
    if a.site_url:
        base_env["NEXT_PUBLIC_SITE_URL"] = a.site_url.rstrip("/")
    if a.endpoint:
        base_env["NEXT_PUBLIC_LEAD_ENDPOINT"] = a.endpoint
    if a.destino:
        base_env["NEXT_PUBLIC_DESTINO_URL"] = a.destino
    resultados = []
    # 1) raiz
    out(f"\n=== build RAIZ (domínio ou subdomínio)")
    o = _build(pasta, {**base_env, "NEXT_PUBLIC_BASE_PATH": ""})
    d_raiz = saida / "raiz"
    if d_raiz.exists():
        shutil.rmtree(d_raiz)
    shutil.move(str(o), str(d_raiz))
    z1 = saida / f"{slug}-raiz.zip"
    _zip_dir(d_raiz, z1)
    resultados.append(z1)
    # 2) subpasta
    out(f"\n=== build SUBPASTA /{sub}/")
    o = _build(pasta, {**base_env, "NEXT_PUBLIC_BASE_PATH": sub})
    d_sub = saida / f"subpasta-{sub}"
    if d_sub.exists():
        shutil.rmtree(d_sub)
    shutil.move(str(o), str(d_sub))
    z2 = saida / f"{slug}-subpasta-{sub}.zip"
    _zip_dir(d_sub, z2)
    resultados.append(z2)
    # 3) fonte
    z3 = saida / f"{slug}-fonte.zip"
    _zip_fonte(pasta, z3, slug)
    resultados.append(z3)
    # deixa um out/ de raiz para conferência local
    if not (pasta / "out").exists():
        shutil.copytree(d_raiz, pasta / "out")
    # a entrega são os ZIPS: as pastas extraídas só duplicam peso (pastas extraídas chegaram a 590 arquivos/42 MB à toa)
    if not getattr(a, "manter_pastas", False):
        shutil.rmtree(d_raiz, ignore_errors=True)
        shutil.rmtree(d_sub, ignore_errors=True)
    (pasta / ".next").exists() and shutil.rmtree(pasta / ".next", ignore_errors=True)
    # LEIA-ME
    leia = f"""ENTREGA — {marca.get('nome', slug)}  ({time.strftime('%d/%m/%Y')})

{z1.name}
  Domínio ou subdomínio (https://dominio.com.br/). Envie o CONTEÚDO do zip (não a pasta) para public_html/
  (Hostinger: Gerenciador de arquivos > public_html > enviar > extrair aqui). O arquivo oculto .htaccess vai junto
  (ative "mostrar arquivos ocultos"). Vercel: suba o projeto-fonte (abaixo) e use `npm run build`; saída = out/.
{z2.name}
  Subpasta (https://dominio.com.br/{sub}/). Envie o CONTEÚDO para public_html/{sub}/. Já vem com o 404 apontando
  para /{sub}/404.html.
{z3.name}
  Código-fonte (sem node_modules). `npm ci` e `npm run build` geram out/. Variáveis em .env.example.

Depois de enviar: abrir / e /nada (404 da marca); testar o botão (pop-up), o formulário e o link de destino;
ativar o SSL gratuito e descomentar o bloco "forçar HTTPS" do .htaccess.
Endpoint do formulário, destino do botão e URL final são gravados NO BUILD: mudou, gere os zips de novo.
Indexação nos buscadores: {'LIGADA' if a.indexar else 'DESLIGADA (noindex) — use --indexar na versão final'}.
Variáveis usadas: {json.dumps({k: v for k, v in base_env.items()}, ensure_ascii=False)}
"""
    (saida / "LEIA-ME.txt").write_text(leia, encoding="utf-8")
    out("\n=== entrega")
    for z in resultados:
        h = hashlib.sha256(z.read_bytes()).hexdigest()[:12]
        out(f"  {z.name:48s} {z.stat().st_size / 1024:9.0f} KB   sha256 {h}")
    out(f"  {saida / 'LEIA-ME.txt'}")


# ----------------------------------------------------------------------------------------------- main
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog="site.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    n = sp.add_parser("new", help="cria o projeto a partir do template e aplica a marca")
    n.add_argument("pasta")
    n.add_argument("--marca", help="brand.json (ou a pasta do projeto de marca que tem brand.json)")
    n.add_argument("--cores", help='sobrescreve papéis: "ink=#111,papel=#eee,destaque=#f50,tinta=..,sobre_destaque=..,acento=..,mute=..,ink2=.."')
    n.add_argument("--fontes", help='"display=Anybody:900[:alta|normal],texto=Hanken Grotesk:400/700,mono=Azeret Mono:500" (mono=nenhuma)')
    n.add_argument("--raio", help="raios em px do site: um valor (rótulo; cartão 2x; moldura 3x) ou 4 (sinal,rotulo,cartao,moldura)")
    n.add_argument("--nome", help="nome da marca (padrão: brand.json name)")
    n.add_argument("--copy", help="copy.json FINAL do cliente (schema em lib/copy.ts)")
    n.add_argument("--logo", help="SVG do logo em curvas (padrão: brand.json logo.primary)")
    n.add_argument("--simbolo", help="SVG do símbolo (favicon, apple-icon)")
    n.add_argument("--foto", help="foto real recortada (PNG/WebP com alfa) para o holofote da dobra")
    n.add_argument("--foto-alt", help="texto alternativo da foto (obrigatório com --foto)")
    n.add_argument("--install", action="store_true", help="roda npm ci no fim")
    n.add_argument("--force", action="store_true", help="sobrescreve a pasta se já existir")
    n.set_defaults(fn=cmd_new)

    m = sp.add_parser("marca", help="mostra a marca derivada de um brand.json + contraste (não cria nada)")
    m.add_argument("brand")
    m.add_argument("--cores")
    m.add_argument("--fontes")
    m.add_argument("--raio")
    m.set_defaults(fn=cmd_marca)

    c = sp.add_parser("check", help="build + servidor + check_pagina + teste_pagina_total + peso + copy-diff")
    c.add_argument("alvo", help="pasta do projeto ou URL (http://…)")
    c.add_argument("--rotas", default="/", help="rotas separadas por vírgula (padrão: /)")
    c.add_argument("--rapido", action="store_true", help="bateria com menos larguras")
    c.add_argument("--sem-total", action="store_true", help="só check_pagina (sem a bateria teste_pagina_total)")
    c.add_argument("--no-build", action="store_true", help="reaproveita out/")
    c.add_argument("--sem-instalar", action="store_true", help="não roda npm ci se faltar node_modules")
    c.add_argument("--subpasta", help="build e serviço em /<subpasta>/ (NEXT_PUBLIC_BASE_PATH)")
    c.add_argument("--site-url")
    c.add_argument("--saida", help="(URL) pasta dos relatórios")
    c.set_defaults(fn=cmd_check)

    p = sp.add_parser("pack", help="zips: raiz, subpasta e fonte (+ LEIA-ME.txt)")
    p.add_argument("pasta")
    p.add_argument("--subpasta", help="nome da subpasta (padrão: slug da marca)")
    p.add_argument("--saida", help="pasta de saída (padrão: <pasta>/_entrega)")
    p.add_argument("--site-url", help="URL pública final (og:image, canonical)")
    p.add_argument("--endpoint", help="URL que recebe o POST do formulário (vazio = demo)")
    p.add_argument("--destino", help="destino do botão da tela de sucesso (grupo, obrigado…)")
    p.add_argument("--indexar", action="store_true", help="NOINDEX=0 (versão final)")
    p.add_argument("--manter-pastas", action="store_true", help="não apaga raiz/ e subpasta-*/ depois de zipar")
    p.set_defaults(fn=cmd_pack)

    d = sp.add_parser("copy-diff", help="texto na página que não está na copy final")
    d.add_argument("copy", help="copy.json")
    d.add_argument("pasta", help="projeto (com out/ já gerado)")
    d.add_argument("--todas", action="store_true", help="todas as rotas + 404")
    d.add_argument("--permitir", action="append", help="texto extra permitido (repita)")
    d.set_defaults(fn=cmd_copy_diff)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
