"""julgar.py — segunda opinião crítica: o Gemini (outra família de modelo) avalia uma imagem na RÉGUA DE EXCELÊNCIA
(../revisao-de-design/references/regua.md): 8 critérios 0–4, veredito ruim/normal/bom/premium, defeitos e correções.

  python julgar.py <imagem> [--tipo pagina|peca|elemento|logo|arte] [--marca "contexto"] [--ref outra.png] [--json]

- `--ref`: peça anterior da série/cliente (critério "diferença": parece a mesma com outra cor?).
- Custo: 1 chamada de texto+visão (modelo `pro` por padrão). Nunca manda chave; usa o .env do projeto via gemini.py.
- O juiz NÃO substitui o olho: confira os defeitos que ele cita; o veredito final é do estúdio.
"""
import argparse, json, subprocess, sys
from pathlib import Path

GEMINI = Path(__file__).resolve().parents[2] / "brand-studio" / "scripts" / "gemini.py"

CRIT = ["ideia", "diferenca", "hierarquia", "composicao", "craft", "verdade_funcao", "coerencia", "acabamento"]

PROMPT = """Você é um diretor de arte sênior, rígido e justo. Avalie a imagem ({tipo}) numa régua de 4 níveis:
RUIM = defeito visível, quebrado, desalinhado, ilegível, elemento sem função ou cor/fonte fora da regra.
NORMAL = correto e limpo mas genérico (parece template; trocando o logo serviria a qualquer marca).
BOM = correto + ideia própria legível em 3 segundos, hierarquia forte, elementos com função; falta refinar detalhes.
PREMIUM = bom + assinatura inconfundível e acabamento medido; nada a tirar nem a acrescentar.
Dê nota 0–4 para cada critério: ideia, diferenca, hierarquia, composicao, craft, verdade_funcao (o elemento é o objeto
real, lógico e bonito?), coerencia, acabamento. Contexto da marca: {marca}.{ref}
Responda SOMENTE JSON: {{"notas": {{"ideia":0,"diferenca":0,"hierarquia":0,"composicao":0,"craft":0,"verdade_funcao":0,
"coerencia":0,"acabamento":0}}, "defeitos_de_portao": ["..."], "nivel": "ruim|normal|bom|premium",
"pontos_fortes": ["..."], "problemas": ["..."], "correcoes": ["... (concretas, em ordem de impacto)"]}}"""


def veredito(notas, portao):
    v = [float(notas.get(k, 0)) for k in CRIT]
    media = sum(v) / len(v)
    if portao:
        return "ruim", media
    if media >= 3.5 and min(v) >= 3 and all(float(notas.get(k, 0)) >= 4 for k in ("ideia", "diferenca", "verdade_funcao")):
        return "premium", media
    if media >= 2.8 and min(v) >= 2:
        return "bom", media
    if media >= 2 and min(v) >= 1:
        return "normal", media
    return "ruim", media


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("imagem")
    ap.add_argument("--tipo", default="peca", choices=["pagina", "peca", "elemento", "logo", "arte"])
    ap.add_argument("--marca", default="marca sem contexto adicional")
    ap.add_argument("--ref", default="")
    ap.add_argument("--model", default="pro")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    ref = (" Há uma imagem de REFERÊNCIA (peça anterior): penalize 'diferenca' se esta for a mesma ideia com outra cor.") if a.ref else ""
    prompt = PROMPT.format(tipo=a.tipo, marca=a.marca, ref=ref)
    cmd = [sys.executable, str(GEMINI), "ask", prompt, "--img", a.imagem, "--json", "--model", a.model]
    if a.ref:
        cmd += ["--img", a.ref]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = (r.stdout or "").strip()
    try:
        i, j = txt.index("{"), txt.rindex("}") + 1
        d = json.loads(txt[i:j])
    except Exception:
        print("resposta não é JSON:\n", txt[:800], r.stderr[-300:]); sys.exit(2)
    nivel, media = veredito(d.get("notas", {}), bool(d.get("defeitos_de_portao")))
    d["nivel_calculado"] = nivel; d["media"] = round(media, 2)
    if a.json:
        print(json.dumps(d, ensure_ascii=False, indent=2)); return
    print(f"NÍVEL: {nivel.upper()}  (média {media:.2f}; o juiz disse: {d.get('nivel')})")
    print("notas:", " · ".join(f"{k} {d['notas'].get(k)}" for k in CRIT))
    for t, k in (("portão", "defeitos_de_portao"), ("fortes", "pontos_fortes"), ("problemas", "problemas"), ("corrigir", "correcoes")):
        for x in d.get(k, []) or []:
            print(f"  [{t}] {x}")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
