"""Instala o que as skills do estúdio precisam (Python + modelos pequenos) e mostra o que falta no sistema.

Uso:
  python instalar.py                 # pacotes Python (requirements.txt) + YuNet (rosto, 230 KB) + diagnóstico
  python instalar.py --upscale       # + Real-ESRGAN (upscale 4×, ~45 MB, roda na GPU via Vulkan)
  python instalar.py --modelos       # + baixa já o CLIP (~580 MB) e o modelo de recorte (~180 MB), senão vêm no 1º uso
  python instalar.py --tudo          # tudo acima
  python instalar.py --so-diagnostico

Não instala programas do sistema (Node, Chrome, FFmpeg): mostra o comando certo para Windows, macOS e Linux.
Nada é instalado fora de: pip do Python atual e ~/.cache/brand-studio/.
"""
import argparse
import io
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REQ = os.path.join(os.path.dirname(HERE), "requirements.txt")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "brand-studio")
YUNET_URL = ("https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/"
             "face_detection_yunet_2023mar.onnx")
ESRGAN_BASE = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-"
SISTEMA = platform.system()   # Windows · Darwin · Linux


def baixar(url, destino):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    print(f"  baixando {url.rsplit('/', 1)[-1]} …")
    with urllib.request.urlopen(url, timeout=120) as r:
        dados = r.read()
    with open(destino, "wb") as f:
        f.write(dados)
    return dados


def pip():
    print("1) Pacotes Python")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQ])
    if r.returncode != 0:
        print("  pip falhou — veja a mensagem acima (Python 3.11+ e internet).")


def yunet():
    destino = os.path.join(CACHE, "models", "yunet", "yunet.onnx")
    if os.path.exists(destino):
        print("2) YuNet (detector de rosto): já existe"); return
    print("2) YuNet (detector de rosto, usado pela prova de camadas)")
    baixar(YUNET_URL, destino)


def esrgan():
    pasta = os.path.join(CACHE, "bin", "realesrgan")
    exe = os.path.join(pasta, "realesrgan-ncnn-vulkan" + (".exe" if SISTEMA == "Windows" else ""))
    if os.path.exists(exe):
        print("3) Real-ESRGAN: já existe"); return
    sufixo = {"Windows": "windows.zip", "Darwin": "macos.zip"}.get(SISTEMA, "ubuntu.zip")
    print("3) Real-ESRGAN (upscale 4×)")
    os.makedirs(pasta, exist_ok=True)
    tmp = os.path.join(pasta, "_download.zip")
    with zipfile.ZipFile(io.BytesIO(baixar(ESRGAN_BASE + sufixo, tmp))) as z:
        for m in z.namelist():                     # extrai só dentro da pasta (sem ../)
            alvo = os.path.realpath(os.path.join(pasta, m))
            if alvo.startswith(os.path.realpath(pasta)):
                z.extract(m, pasta)
    os.remove(tmp)
    if SISTEMA != "Windows" and os.path.exists(exe):
        os.chmod(exe, 0o755)


def modelos():
    print("4) Modelos grandes (CLIP e recorte)")
    try:
        sys.path.insert(0, HERE)
        from common import MODEL_DIR
        from fastembed import ImageEmbedding, TextEmbedding
        ImageEmbedding("Qdrant/clip-ViT-B-32-vision", cache_dir=MODEL_DIR)
        TextEmbedding("Qdrant/clip-ViT-B-32-text", cache_dir=MODEL_DIR)
        print("  CLIP ok")
    except Exception as e:  # o índice também baixa sozinho no 1º uso
        print("  CLIP não baixou agora:", e)
    try:
        from rembg import new_session
        new_session("isnet-general-use")
        print("  recorte ok")
    except Exception as e:
        print("  recorte não baixou agora:", e)


def sistema():
    print("5) Programas do sistema (instale você, se faltar)")
    cmds = {
        "Windows": {"node": "winget install OpenJS.NodeJS.LTS", "chrome": "winget install Google.Chrome",
                    "ffmpeg": "winget install Gyan.FFmpeg"},
        "Darwin": {"node": "brew install node", "chrome": "brew install --cask google-chrome", "ffmpeg": "brew install ffmpeg"},
    }.get(SISTEMA, {"node": "sudo apt install nodejs npm  (ou nvm, Node 22+)", "chrome": "instale o Google Chrome (.deb)",
                    "ffmpeg": "sudo apt install ffmpeg"})
    sys.path.insert(0, HERE)
    from common import find_chrome, find_ffmpeg
    tem = {"node": shutil.which("node"), "chrome": find_chrome(), "ffmpeg": find_ffmpeg()}
    for k, v in tem.items():
        print(f"  [{'ok' if v else 'FALTA'}] {k}" + ("" if v else f"  → {cmds[k]}"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--upscale", action="store_true")
    ap.add_argument("--modelos", action="store_true")
    ap.add_argument("--tudo", action="store_true")
    ap.add_argument("--so-diagnostico", action="store_true")
    a = ap.parse_args()
    if not a.so_diagnostico:
        pip()
        yunet()
        if a.upscale or a.tudo:
            esrgan()
        if a.modelos or a.tudo:
            modelos()
    sistema()
    print("\nDiagnóstico completo:")
    subprocess.run([sys.executable, os.path.join(HERE, "doctor.py")])


if __name__ == "__main__":
    main()
