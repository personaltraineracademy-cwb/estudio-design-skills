"""Valida o pacote de skills do estúdio antes de publicar.

Confere, em cada skill listada em .claude-plugin/plugin.json:
  1. frontmatter (Agent Skills): name = pasta, minúsculas/números/hífen, ≤ 64; description 1–1024, sem < >
  2. SKILL.md ≤ 500 linhas
  3. caminhos citados em `crase` ou [link](…) existem (relativos à raiz da skill ou ao arquivo)
  4. privacidade: caminhos de usuário, e-mails, chaves de API e os termos de um arquivo PRIVADO
     (--termos arquivo.txt ou variável ESTUDIO_TERMOS_PRIVADOS; uma palavra/regex por linha; nunca vai no pacote)
  5. scripts/*.py respondem a --help (exit 0)
  6. texto com CRLF ou caractere de controle

Uso:
  python _ferramentas/validar.py                    # tudo
  python _ferramentas/validar.py --sem-scripts      # pula o teste de --help (mais rápido)
  python _ferramentas/validar.py --termos ../privado/termos.txt
Saída: lista de ERROS e AVISOS; exit 1 se houver erro.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
TEXTO = {".md", ".py", ".json", ".mjs", ".js", ".ts", ".tsx", ".css", ".html", ".txt", ".svg"}
IGNORAR = {"node_modules", "__pycache__", ".next", "out", ".check", "_entrega"}
SEM_PRIVACIDADE = {"vendor", "licencas"}   # código e licenças de terceiros (têm e-mail do autor)
# módulos importados por outros scripts (não são CLI)
NAO_CLI = {"common.py", "_base.py", "__init__.py", "lib.py"}
# caminhos de usuário, e-mail, chaves: nunca em pacote público
PRIV_GERAL = [
    (r"[A-Za-z]:[/\\]+Users[/\\]+[A-Za-z]", "caminho de usuário do Windows"),
    (r"/(?:home|Users)/[a-z][\w.-]+/", "caminho de usuário Unix/macOS"),
    (r"[\w.+-]+@(?!example\.|exemplo\.|email\.com)[A-Za-z][\w-]*\.[A-Za-z]{2,}\b", "e-mail"),
    (r"AIza[0-9A-Za-z_-]{30,}", "chave de API do Google"),
    (r"sk-[A-Za-z0-9]{20,}", "chave de API"),
]
REF = re.compile(r"`((?:\.\./[\w-]+/)?(?:references|scripts|assets|SKILL\.md)[^`\s]*)`|\]\(((?!https?:|#)[^)\s]+)\)")


def frontmatter(txt):
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        return None
    d = {}
    for linha in m.group(1).splitlines():
        if re.match(r"^[\w-]+:", linha):
            k, v = linha.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def resolve(ref, skill, arquivo):
    ref = ref.split("#")[0].split(" ")[0].rstrip(".,;:)")
    ref = re.sub(r"[<>*].*$", "", ref)          # placeholders: <dir>, *.md
    if not ref or ref.endswith("/") and not ref.strip("./"):
        return True
    cands = [skill / ref] + [d / ref for d in [arquivo.parent, *arquivo.parent.parents] if skill in (d, *d.parents)]
    return any(c.exists() for c in cands) or ref.endswith("/") and any((c.parent).exists() for c in cands)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--termos", default=os.environ.get("ESTUDIO_TERMOS_PRIVADOS"),
                    help="arquivo com termos privados (um por linha, regex aceita)")
    ap.add_argument("--sem-scripts", action="store_true")
    a = ap.parse_args()

    manifesto = json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    skills = [RAIZ / s.strip("./") for s in manifesto.get("skills", [])]
    termos = []
    if a.termos and Path(a.termos).is_file():
        termos = [(t.strip(), "termo privado") for t in Path(a.termos).read_text(encoding="utf-8").splitlines()
                  if t.strip() and not t.startswith("#")]
    erros, avisos = [], []

    for sk in skills:
        md = sk / "SKILL.md"
        if not md.is_file():
            erros.append(f"{sk.name}: sem SKILL.md"); continue
        txt = md.read_text(encoding="utf-8")
        fm = frontmatter(txt)
        if not fm:
            erros.append(f"{sk.name}: SKILL.md sem frontmatter"); continue
        nome, desc = fm.get("name", ""), fm.get("description", "")
        if nome != sk.name or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nome) or len(nome) > 64:
            erros.append(f"{sk.name}: name inválido ({nome!r})")
        if not (1 <= len(desc) <= 1024) or re.search(r"[<>]", desc):
            erros.append(f"{sk.name}: description com {len(desc)} caracteres ou com < >")
        n = txt.count("\n") + 1
        if n > 500:
            erros.append(f"{sk.name}: SKILL.md com {n} linhas (máx. 500)")
        elif n > 300:
            avisos.append(f"{sk.name}: SKILL.md com {n} linhas (ideal ≤ 300)")

        for f in sk.rglob("*"):
            if not f.is_file() or IGNORAR & set(f.parts) or f.suffix.lower() not in TEXTO:
                continue
            rel = f.relative_to(RAIZ).as_posix()
            b = f.read_bytes()
            if b"\r\n" in b:
                avisos.append(f"{rel}: quebras de linha CRLF")
            t = b.decode("utf-8", "replace")
            if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", t):
                erros.append(f"{rel}: caractere de controle (barra invertida perdida?)")
            for pad, oque in ([] if SEM_PRIVACIDADE & set(f.parts) else PRIV_GERAL + termos):
                for m in re.finditer(pad, t, re.I if oque == "termo privado" else 0):
                    ln = t.count("\n", 0, m.start()) + 1
                    erros.append(f"{rel}:{ln}: {oque}: {m.group(0)[:40]!r}")
            if f.suffix == ".md":
                for m in REF.finditer(t):
                    ref = m.group(1) or m.group(2)
                    if not resolve(ref, sk, f):
                        ln = t.count("\n", 0, m.start()) + 1
                        erros.append(f"{rel}:{ln}: caminho não existe: {ref}")

        if not a.sem_scripts:
            for py in sorted((sk / "scripts").glob("*.py")):
                if py.name in NAO_CLI:
                    continue
                try:
                    r = subprocess.run([sys.executable, str(py), "--help"], capture_output=True, timeout=60,
                                       encoding="utf-8", errors="replace", cwd=str(py.parent))
                    if r.returncode != 0:
                        ult = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["?"]
                        erros.append(f"{py.relative_to(RAIZ).as_posix()}: --help falhou: {ult[0][:120]}")
                except subprocess.TimeoutExpired:
                    avisos.append(f"{py.relative_to(RAIZ).as_posix()}: --help passou de 60 s")

    for e in erros:
        print("ERRO ", e)
    for w in avisos:
        print("AVISO", w)
    print(f"\n{len(skills)} skills · {len(erros)} erros · {len(avisos)} avisos")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
