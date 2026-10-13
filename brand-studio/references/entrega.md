# Entrega — estrutura do kit e checklist

## Pasta (no Desktop ou onde o usuário pedir — nunca só no scratch)
```
<Nome do Projeto>/
  GUIA-DE-USO.md          cores HEX/RGB/CMYK(+Pantone aprox.), fontes e licença, área de proteção, mínimos, não-faça
  apresentacao.html + slides/   presentation_board.py (mockups do setor)
  svg/  png/              lockup.py: horizontal · vertical · símbolo · wordmark × 5 colorways (+ co-branding)
  web/                    favicon.ico, ícones, webmanifest, head-snippet (export_variants.py --web-icons)
  padroes/                pattern.py (tile + aplicação)
  selos/                  seal.py (quando fizer sentido)
  kv/                     keyvisual.py 1080², 1080×1350, 1080×1920, 1920×1080 (+ fx opcionais)
  motion/                 sting.mp4 (+ projeto HyperFrames editável)
  fonte-editavel/         specs JSON, sketches .mjs, fontes OFL + OFL.txt — para regenerar tudo
<Nome do Projeto>.zip
```

## Checklist antes de entregar
- [ ] `svg_audit.py` nos masters: sem `<text>`, sem `<image>`, sem filtros; score ≥ 90.
- [ ] Símbolo legível a 16/32 px (corte simplificado se preciso) — veja `concept_sheet.py`/`preview_sheet.py`.
- [ ] Avisos de contraste do `lockup.py` resolvidos (ou documentados como "não usar").
- [ ] `library.py novelty` no símbolo e no horizontal: nada ≥ 0,93; itens 0,88–0,93 conferidos no olho.
- [ ] Nenhuma cor duplicada quase-igual; destaque não colide com marca irmã do mesmo cliente sem motivo.
- [ ] Guia de uso com licença das fontes; recomendação de busca no INPI se for marca permanente.
- [ ] Mostrou ao usuário: imagem principal + KVs + vídeo (SendUserFile), não só caminhos.

## Depois da aprovação (o sistema aprende)
```
python scripts/library.py add "<kit>/svg/<nome>-horizontal-positivo.svg" --client "<Cliente>" --project "<Nome>" --note "por que aprovou"
python scripts/library.py add "<kit>/svg/<nome>-symbol-positivo.svg" --client "<Cliente>" --project "<Nome>"
```
e acrescente a ficha do projeto em `design/biblioteca/<Cliente>/_fichas.json` (e atualize `<Cliente>/_perfil.md`) (tipo, conceito, recursos, cores,
tipografia, porque_aprovado, evitar). Se reprovou algo, registre com `--status reprovado --note "motivo"` — os
motivos de reprovação valem tanto quanto os de aprovação.

## Checklist de craft do logo antes do kit
- [ ] Alinhado e centrado pela TINTA (não pela caixa da fonte); linhas do bloco com a mesma largura de tinta.
- [ ] Uma unidade `u` (altura da maiúscula); todo espaço é múltiplo de `u`; espessuras = fração da haste.
- [ ] Kerning óptico dos pares críticos conferido a ≥ 400%.
- [ ] viewBox medido na tinta + margem (`logo_qc.py`: nada vaza; C/O/S não cortam).
- [ ] **Vazado = furo real** (`fill-rule="evenodd"`/caminho subtraído), testado sobre FOTO — texto pintado na cor do
      fundo não é vazado.
- [ ] SVG de terceiro embutido várias vezes: **achatar classes CSS (`.cls-1` em `<style>`) em atributos** antes, senão
      a última cor vence em todas as cópias.
- [ ] Kit = cores aprovadas + mono positivo e negativo + símbolo em avatar redondo; cor aplicada por PAPEL, nunca
      "pintar o logo inteiro".
- [ ] Prancha de estúdio: construção medida + logo em uso (não folha de teste).
