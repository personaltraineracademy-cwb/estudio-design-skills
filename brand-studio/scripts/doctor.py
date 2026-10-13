"""Diagnóstico das skills do estúdio: o que está pronto, o que é OBRIGATÓRIO, RECOMENDADO ou OPCIONAL.

Uso:
  python doctor.py            # relatório para ler (o agente explica ao usuário o que falta)
  python doctor.py --json     # mesmo relatório em JSON

Guia completo (o que é cada item, custo, como instalar): ../references/instalacao.md
Instalador: python instalar.py
"""
import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (CACHE, CATALOG_DIR, LIBRARY_DIR, LOGO_SKILL, MODEL_DIR, PROJECT_DIR,  # noqa: E402
                    find_chrome, find_ffmpeg)

itens = []


def item(nivel, nome, ok, perde, como):
    itens.append({"nivel": nivel, "nome": nome, "ok": bool(ok), "sem_isso": perde, "como": como})


def modulo(nome):
    try:
        importlib.import_module(nome)
        return True
    except Exception:
        return False


PIP = "python instalar.py   (ou: python -m pip install -r ../requirements.txt)"
# --- OBRIGATÓRIO: sem isso as skills não rodam
for mod, pacote in (("resvg_py", "resvg-py"), ("fontTools", "fonttools"), ("pathops", "skia-pathops"),
                    ("PIL", "pillow"), ("numpy", "numpy")):
    item("obrigatório", f"Python: {pacote}", modulo(mod), "nada renderiza (SVG → PNG, texto em curvas)", PIP)
ver = sys.version_info
item("obrigatório", f"Python {ver.major}.{ver.minor}", ver >= (3, 11), "scripts não rodam", "instale Python 3.11+")
chrome = find_chrome()
item("obrigatório", "Google Chrome (ou Edge)", chrome, "sem peças em HTML, verificadores, manual, demo do DS e sites",
     "instale o Chrome (Windows: winget install Google.Chrome · macOS: brew install --cask google-chrome)")
for mod, pacote in (("playwright", "playwright"), ("cv2", "opencv-python"), ("scipy", "scipy"),
                    ("skimage", "scikit-image"), ("shapely", "shapely"), ("segno", "segno"), ("zxingcpp", "zxing-cpp"),
                    ("pymupdf", "pymupdf"), ("brotli", "brotli")):
    item("obrigatório", f"Python: {pacote}", modulo(mod),
         "direção de arte, manual, verificadores de página ou elementos param", PIP)

# --- RECOMENDADO: grátis, local, melhora muito o resultado
node = shutil.which("node")
nver = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip() if node else ""
item("recomendado", f"Node.js 22+ {nver}", node and int(nver.lstrip("v").split(".")[0]) >= 22,
     "sem sketches generativos, SVGO, animação de logo (HyperFrames) e sites (Next.js)",
     "Windows: winget install OpenJS.NodeJS.LTS · macOS: brew install node")
item("recomendado", "FFmpeg", find_ffmpeg(), "sem animação de logo em MP4",
     "Windows: winget install Gyan.FFmpeg · macOS: brew install ffmpeg · Linux: apt install ffmpeg")
item("recomendado", "Python: fastembed (CLIP)", modulo("fastembed"), "sem repertório por imagem nem teste de originalidade", PIP)
item("recomendado", "Python: rembg (recorte)", modulo("rembg"), "sem recorte automático de foto", PIP)
item("recomendado", "Python: vtracer", modulo("vtracer"), "sem vetorizar imagem (raster → SVG)", PIP)
item("recomendado", "Detector de rosto YuNet", os.path.exists(os.path.join(CACHE, "models", "yunet", "yunet.onnx")),
     "a prova de camadas não confere rosto coberto/olhos na zona segura", "python instalar.py")
item("recomendado", "Modelo CLIP em cache", os.path.isdir(MODEL_DIR) and any("clip" in n.lower() for n in os.listdir(MODEL_DIR)),
     "1ª busca/originalidade vai baixar ~580 MB na hora", "python instalar.py --modelos")
item("recomendado", "Skill logo-design (MIT)", os.path.isdir(LOGO_SKILL),
     "sem auditoria de SVG, folha de conceitos e biblioteca de mercado para originalidade",
     "copie github.com/kaankiziltug/logo-design-skill ao lado das outras skills")

# --- OPCIONAL: extras (alguns pagos)
esr = os.path.join(CACHE, "bin", "realesrgan", "realesrgan-ncnn-vulkan" + (".exe" if os.name == "nt" else ""))
item("opcional", "Real-ESRGAN (upscale 4×)", os.path.exists(esr), "sem ampliar foto pequena (precisa GPU com Vulkan)",
     "python instalar.py --upscale")
chave = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.path.exists(
    os.path.join(os.path.expanduser("~"), ".config", "brand-studio", "gemini_key"))
item("opcional", "Chave da API do Gemini (PAGO, ~US$ 0,03–0,11 por imagem)", chave,
     "sem imagem por IA (cenários, mockups, texturas) e sem juiz de outra família; o resto funciona",
     "crie em aistudio.google.com/apikey, ative o faturamento e ponha GEMINI_API_KEY=… no .env da pasta de trabalho")
item("opcional", f"Biblioteca de clientes ({LIBRARY_DIR})", os.path.isdir(LIBRARY_DIR),
     "sem acervo próprio (cliente novo funciona sem)", "crie a pasta biblioteca/ na pasta de trabalho ou defina BRAND_LIBRARY")
item("opcional", "Índice CLIP da biblioteca", os.path.exists(os.path.join(CATALOG_DIR, "catalog.sqlite")),
     "sem busca no acervo", "python library.py index  (depois de ter logos na biblioteca)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a.json:
        print(json.dumps({"pasta_de_trabalho": PROJECT_DIR, "itens": itens}, ensure_ascii=False, indent=1))
        return
    print(f"Pasta de trabalho: {PROJECT_DIR}\n")
    for nivel in ("obrigatório", "recomendado", "opcional"):
        print(nivel.upper())
        for i in (x for x in itens if x["nivel"] == nivel):
            if i["ok"]:
                print(f"  [ok]    {i['nome']}")
            else:
                marca = "FALTA" if nivel == "obrigatório" else "–"
                print(f"  [{marca}] {i['nome']}\n          sem isso: {i['sem_isso']}\n          como: {i['como']}")
        print()
    falta = [i for i in itens if i["nivel"] == "obrigatório" and not i["ok"]]
    print("Pronto para usar." if not falta else f"{len(falta)} item(ns) OBRIGATÓRIO(S) faltando: rode python instalar.py")
    print("Fora do computador (o agente confere/pergunta): plugin caveman (respostas curtas) e conector Adobe (opcional).")


if __name__ == "__main__":
    main()
