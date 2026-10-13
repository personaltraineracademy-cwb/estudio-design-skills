"""Gemini engine — images (Nano Banana family: generate, edit with references, post-process, track cost) and
text/vision (ask: analyse references, critique/judge pieces, write prompts, research with Google Search).

Key: GEMINI_API_KEY in the .env of the working folder (ESTUDIO_DIR; the user pastes it there; loaded by common.py), or the environment variable
     GEMINI_API_KEY / GOOGLE_API_KEY, or ~/.config/brand-studio/gemini_key. Never paste keys in chat or commit them.

Usage:
  python gemini.py check                                     # validates the key, lists image models
  python gemini.py gen "anilha olímpica cromada flutuando, luz de estúdio" -o out/anilha --n 4 --aspect 1:1 \
                   --element --cutout                        # isolated element → transparent PNG
  python gemini.py gen "textura de fumaça amarela sobre preto" -o out/fumaca --aspect 9:16 --size 2K
  python gemini.py gen "ícone de halter, traço grosso, flat" -o out/icone --element --vector
  python gemini.py edit foto.jpg "troque o fundo por estúdio preto com luz amarela de recorte" -o out/foto-edit
  python gemini.py gen "mesmo personagem correndo" --ref personagem.png -o out/p2     # up to ~6–14 references
  python gemini.py usage                                     # images generated + estimated spend
  python gemini.py ask "descreva a linguagem visual destas referências" --img ref1.jpg ref2.png [--json]
  python gemini.py ask "concorrentes de academias premium em SP e seus logos" --search   # Google Search grounding
  python gemini.py ask "…" --system "Você é diretor de criação…" --model pro           # text model: flash|pro|<id>
Options (gen/edit):
  --model banana21 (default: gemini-nano-banana-2.1, best Gemini image model on arena.ai Oct/2026) |
          flash (gemini-3.1-flash-image, previous generation, still stable) | pro (gemini-3-pro-image) | lite (cheapest) | <model-id>
  --aspect 1:1 4:5 9:16 16:9 3:4 4:3 2:3 3:2 5:4 21:9   --size 1K|2K|4K   --n variations
  --casa "Cliente/Projeto"  prepend an approved project's colours/mood from its client's _fichas.json (style context)
  --element            ask for an isolated subject on flat white (easy cut-out), no text, no shadow
  --cutout / --vector / --upscale   post-process (imaging.py / vectorize.py)
  --dry                print the request without calling the API
The model writes images; put final TEXT on top with lockup.py/compose.py (model lettering can contain errors).
"""
import argparse
import base64
import csv
import datetime
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CACHE, CATALOG_DIR  # noqa: E402

BASE = "https://generativelanguage.googleapis.com/v1beta"
MODELS = {"banana21": "gemini-nano-banana-2.1", "flash": "gemini-3.1-flash-image", "pro": "gemini-3-pro-image",
          "lite": "gemini-3.1-flash-lite-image", "legacy": "gemini-2.5-flash-image"}
DEFAULT_IMAGE = "banana21"
# rough USD per image (public price snapshots, Sep 2026) — for budgeting only
PRICE = {("gemini-3.1-flash-image", "1K"): 0.067, ("gemini-3.1-flash-image", "2K"): 0.101,
         ("gemini-3.1-flash-image", "4K"): 0.151, ("gemini-3-pro-image", "1K"): 0.134,
         ("gemini-3-pro-image", "2K"): 0.134, ("gemini-3-pro-image", "4K"): 0.24,
         ("gemini-2.5-flash-image", "1K"): 0.039,
         # nano-banana-2.1: Google pricing page, Oct/2026 (pesquisa 15 §preço); Batch API = about half
         ("gemini-nano-banana-2.1", "1K"): 0.0336, ("gemini-nano-banana-2.1", "2K"): 0.0504,
         ("gemini-nano-banana-2.1", "4K"): 0.113}
USAGE = os.path.join(CACHE, "gemini-usage.csv")
HERE = os.path.dirname(os.path.abspath(__file__))


def api_key():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not k:
        p = os.path.join(os.path.expanduser("~"), ".config", "brand-studio", "gemini_key")
        if os.path.exists(p):
            k = open(p, encoding="utf-8").read().strip()
    if not k:
        raise SystemExit("Sem chave do Gemini: defina GEMINI_API_KEY ou crie um .env na pasta de trabalho com a chave depois de "
                         "GEMINI_API_KEY= (crie em https://aistudio.google.com/apikey e ative o faturamento).")
    return k


def http(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"x-goog-api-key": api_key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code}: {msg[:1200]}")


def _b64(s):
    return base64.b64decode(s + "=" * (-len(s) % 4))


def find_images(obj, out=None, texts=None):
    """Collect base64 images from any response shape (Interactions steps/content or generateContent parts)."""
    out = [] if out is None else out
    texts = [] if texts is None else texts
    if isinstance(obj, dict):
        inline = obj.get("inlineData") or obj.get("inline_data")
        if isinstance(inline, dict) and inline.get("data"):
            out.append((_b64(inline["data"]), inline.get("mimeType") or inline.get("mime_type", "image/png")))
        elif obj.get("type") == "image" and isinstance(obj.get("data"), str) and len(obj["data"]) > 200:
            out.append((_b64(obj["data"]), obj.get("mime_type") or obj.get("mimeType") or "image/png"))
        elif obj.get("type") == "text" and isinstance(obj.get("text"), str):
            texts.append(obj["text"])
        for v in obj.values():
            if isinstance(v, (dict, list)):
                find_images(v, out, texts)
    elif isinstance(obj, list):
        for v in obj:
            find_images(v, out, texts)
    return out, texts


def b64file(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
    return mime, base64.b64encode(open(path, "rb").read()).decode()


def call(model, prompt, refs, aspect, size, dry=False):
    blocks = [{"type": "text", "text": prompt}]
    parts = [{"text": prompt}]
    for r in refs:
        mime, data = b64file(r)
        blocks.append({"type": "image", "mime_type": mime, "data": data})
        parts.append({"inline_data": {"mime_type": mime, "data": data}})
    fmt = {"type": "image", "mime_type": "image/png", "image_size": size}
    if aspect:
        fmt["aspect_ratio"] = aspect
    inter = {"model": model, "input": blocks, "response_format": fmt, "store": False}
    if dry:
        show = json.loads(json.dumps(inter))
        for b in show["input"]:
            if b.get("data"):
                b["data"] = f"<{len(b['data'])} bytes b64>"
        print(json.dumps(show, ensure_ascii=False, indent=2))
        return [], []
    try:
        res = http("POST", f"{BASE}/interactions", inter)
    except RuntimeError as e:
        if "HTTP 404" not in str(e) and "HTTP 400" not in str(e):
            raise
        gc = {"contents": [{"parts": parts}],
              "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"imageSize": size,
                                                                                    **({"aspectRatio": aspect} if aspect else {})}}}
        res = http("POST", f"{BASE}/models/{model}:generateContent", gc)
    return find_images(res)


def casa_context(project):
    """Style context from an approved project's ficha: "Cliente/Projeto" or just "Projeto" (searched in every client)."""
    from library import load_fichas
    fichas = load_fichas()
    fi = fichas.get(project) or next((v for k, v in fichas.items() if k.split("/", 1)[-1] == project), {})
    if not fi:
        return ""
    cores = ", ".join(fi.get("cores", []))
    return (f"Brand context: colour palette {cores}; mood/devices: {', '.join(fi.get('recursos', [])[:3])}. "
            "Keep strictly to this palette. ")


def log_usage(model, size, n, prompt):
    os.makedirs(CACHE, exist_ok=True)
    new = not os.path.exists(USAGE)
    with open(USAGE, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["data", "modelo", "tamanho", "imagens", "usd_estimado", "prompt"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), model, size, n,
                    round(PRICE.get((model, size), 0.1) * n, 3), prompt[:120]])


def post(path, a):
    base = path[:-4]
    if a.cutout or a.vector:
        subprocess.run([sys.executable, os.path.join(HERE, "imaging.py"), "cutout", path, "-o", base + "-recorte.png",
                        "--crop"], check=False)
    if a.vector:
        src = base + "-recorte.png" if os.path.exists(base + "-recorte.png") else path
        subprocess.run([sys.executable, os.path.join(HERE, "vectorize.py"), src, base + ".svg", "--preset",
                        "logo" if a.element else "poster"], check=False)
    if a.upscale:
        subprocess.run([sys.executable, os.path.join(HERE, "imaging.py"), "upscale", path, "-o", base + "-4x.png"],
                       check=False)


def generate(a, prompt, refs):
    model = MODELS.get(a.model, a.model)
    full = ""
    if a.casa:
        full += casa_context(a.casa)
    full += prompt
    if a.element:
        full += (" — single isolated subject, centred, on a perfectly flat pure white (#FFFFFF) background, no "
                 "cast shadow on the background, no text, no watermark, no frame, generous margin.")
    elif not a.allow_text:
        full += " — no text, no letters, no logos, no watermark."
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    saved = []
    for i in range(a.n):
        imgs, texts = call(model, full + (f" (variation {i + 1})" if a.n > 1 else ""), refs, a.aspect, a.size, a.dry)
        if a.dry:
            return
        if not imgs:
            print(f"sem imagem na resposta {i + 1}. Texto do modelo: {' '.join(texts)[:400]}")
            continue
        for j, (data, mime) in enumerate(imgs):
            path = f"{a.out}-{i + 1}{'' if j == 0 else '-' + str(j)}.png"
            from PIL import Image
            import io
            Image.open(io.BytesIO(data)).save(path)
            # original intacto ao lado: guarda a credencial C2PA da Google (remover é proibido pelos termos)
            ext = (mime or "image/png").split("/")[-1].replace("jpeg", "jpg")
            with open(path[:-4] + "-original." + ext, "wb") as fo:
                fo.write(data)
            saved.append(path)
            print(path)
            post(path, a)
        log_usage(model, a.size, len(imgs), prompt)
    if saved:
        with open(a.out + "-prompt.json", "w", encoding="utf-8") as fh:
            json.dump({"model": model, "prompt": full, "refs": refs, "aspect": a.aspect, "size": a.size,
                       "files": saved}, fh, ensure_ascii=False, indent=2)
        if len(saved) > 1:
            sheet(saved, a.out + "-sheet.png")


# ------------------------------------------------------------------ text / vision
SKIP = ("image", "tts", "embedding", "live", "audio", "banana", "robotics", "computer", "native", "veo", "lyria",
        "imagen", "aqa", "learnlm", "gemma")


def list_models(force=False):
    """Model list from the API, cached for a day in ~/.cache/brand-studio/gemini-models.json."""
    cache = os.path.join(CACHE, "gemini-models.json")
    if not force and os.path.exists(cache) and (datetime.datetime.now().timestamp() - os.path.getmtime(cache)) < 86400:
        return json.load(open(cache, encoding="utf-8"))
    res = http("GET", f"{BASE}/models?pageSize=500")
    models = [{"name": m.get("name", "").split("/")[-1], "methods": m.get("supportedGenerationMethods", []),
               "display": m.get("displayName", "")} for m in res.get("models", [])]
    os.makedirs(CACHE, exist_ok=True)
    json.dump(models, open(cache, "w", encoding="utf-8"), indent=1)
    return models


def pick_text_model(tier="flash"):
    """Newest stable gemini-<ver>-<tier> text model the key can use (preview only if nothing stable)."""
    import re
    names = {m["name"] for m in list_models()}
    if tier == "pro" and "gemini-pro-latest" in names:     # Google keeps this alias on the newest Pro
        return "gemini-pro-latest"
    best = []
    for m in list_models():
        n = m["name"]
        if "generateContent" not in m["methods"] or any(x in n for x in SKIP):
            continue
        r = re.match(r"gemini-(\d+(?:\.\d+)?)-(pro|flash-lite|flash)(-preview)?(?:-[\w.-]+)?$", n)
        if r and r[2] == tier:
            best.append((r[3] is None, float(r[1]), n == f"gemini-{r[1]}-{r[2]}", n))
    if not best:
        raise SystemExit(f"nenhum modelo de texto '{tier}' disponível para esta chave (rode: gemini.py check)")
    return max(best)[3]


def ask(prompt, images=(), system=None, model="flash", as_json=False, search=False, temperature=None):
    """Text (+ images) → text answer. Returns the answer string (and prints sources when grounded)."""
    mid = pick_text_model(model) if model in ("flash", "pro", "flash-lite") else model
    parts = [{"text": prompt}]
    for im in images:
        mime, data = b64file(im)
        parts.append({"inline_data": {"mime_type": mime, "data": data}})
    body = {"contents": [{"role": "user", "parts": parts}]}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    cfg = {}
    if as_json and not search:
        cfg["responseMimeType"] = "application/json"
    if temperature is not None:
        cfg["temperature"] = temperature
    if cfg:
        body["generationConfig"] = cfg
    if search:
        body["tools"] = [{"google_search": {}}]
    res = http("POST", f"{BASE}/models/{mid}:generateContent", body)
    cand = (res.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    srcs = [c.get("web", {}) for c in cand.get("groundingMetadata", {}).get("groundingChunks", [])]
    if srcs:
        text += "\n\nFontes:\n" + "\n".join(f"- {w.get('title', '')}: {w.get('uri', '')}" for w in srcs if w)
    return text, mid


def sheet(paths, out, h=360):
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in paths]
    ims = [im.resize((int(h * im.width / im.height), h)) for im in ims]
    s = Image.new("RGB", (sum(i.width for i in ims) + 10 * (len(ims) + 1), h + 20), "white")
    x = 10
    for im in ims:
        s.paste(im, (x, 10))
        x += im.width + 10
    s.save(out)
    print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("check"); sub.add_parser("usage")
    p = sub.add_parser("ask"); p.add_argument("prompt"); p.add_argument("--img", nargs="*", default=[])
    p.add_argument("--system"); p.add_argument("--model", default="flash"); p.add_argument("--json", action="store_true")
    p.add_argument("--search", action="store_true"); p.add_argument("--temperature", type=float)
    p.add_argument("-o", "--out", help="also save the answer to this file")
    for name in ("gen", "edit"):
        p = sub.add_parser(name)
        if name == "edit":
            p.add_argument("image")
        p.add_argument("prompt"); p.add_argument("-o", "--out", required=True)
        p.add_argument("--model", default=DEFAULT_IMAGE); p.add_argument("--n", type=int, default=1)
        p.add_argument("--aspect"); p.add_argument("--size", default="1K"); p.add_argument("--ref", nargs="*", default=[])
        p.add_argument("--casa"); p.add_argument("--element", action="store_true")
        p.add_argument("--allow-text", action="store_true")
        p.add_argument("--cutout", action="store_true"); p.add_argument("--vector", action="store_true")
        p.add_argument("--upscale", action="store_true"); p.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    if a.cmd == "check":
        models = list_models(force=True)
        names = [m["name"] for m in models]
        img = [n for n in names if "image" in n or "banana" in n]
        print("chave OK —", len(names), "modelos")
        print("  imagem:", ", ".join(img) or "(nenhum listado)")
        for alias, mid in MODELS.items():
            print(f"  --model {alias:<9} {mid:<32} {'disponível' if mid in names else 'NÃO listado para esta chave'}")
        for tier in ("flash", "pro"):
            try:
                print(f"  texto {tier}: {pick_text_model(tier)}")
            except SystemExit as e:
                print(f"  texto {tier}: {e}")
        other = [n for n in names if any(x in n for x in ("veo", "tts", "lyria", "embedding"))]
        if other:
            print("  outros (vídeo/voz/música/embeddings):", ", ".join(other))
    elif a.cmd == "ask":
        text, mid = ask(a.prompt, a.img, a.system, a.model, a.json, a.search, a.temperature)
        print(f"[{mid}]\n{text}")
        if a.out:
            os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
            open(a.out, "w", encoding="utf-8").write(text)
    elif a.cmd == "usage":
        if not os.path.exists(USAGE):
            print("nenhum uso registrado")
            return
        rows = list(csv.DictReader(open(USAGE, encoding="utf-8")))
        n = sum(int(r["imagens"]) for r in rows)
        usd = sum(float(r["usd_estimado"]) for r in rows)
        print(f"{n} imagens · ~US$ {usd:.2f} estimados (confira o valor real no Google AI Studio)")
    elif a.cmd == "gen":
        generate(a, a.prompt, a.ref)
    elif a.cmd == "edit":
        a.allow_text = True
        generate(a, a.prompt, [a.image] + a.ref)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
