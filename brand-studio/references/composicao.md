# Composição de peças + pedidos ao Gemini

## Pipeline de uma peça (post, banner, anúncio, cartaz, thumb)
1. **Mensagem**: 1 ideia, 1 número/benefício, 1 CTA. Escreva o texto final antes de desenhar.
2. **Elementos** — escolha o motor:
   - forma/símbolo/padrão → código (`sketch.py`, `pattern.py`, símbolo da marca)
   - objeto/texto em 3D → `render3d.py` (chrome, gold, plastic, glass, neon, clay, matte)
   - foto de pessoa/produto → `imaging.py cutout` (+ `upscale` se pequena)
   - foto, ilustração, textura, cenário que não existe → `gemini.py gen` (custa por imagem)
   - edição de foto (trocar fundo, luz, roupa) → `gemini.py edit`
3. **Montagem**: `compose.py peca.json` gera todos os formatos; ajuste `overrides` por formato.
4. **Acabamento**: camada `fx` (grão leve, vinheta) — nada que reduza a leitura do texto.
5. **Olhe** a folha (`-sheet.png`), corrija, e só então mostre.
6. **Entrega**: PNGs + `*-express.html` para importar no Adobe Express (editável) via conector Adobe
   (`create_visual_design_express_skill` → `html_export_readiness_skill` → `export_html_to_express`).

## Regras de composição (o que separa amador de profissional)
- **Um herói por peça** (pessoa, objeto 3D ou número) ocupando 35–60 % da área; o resto serve a ele.
- **Hierarquia de 3 níveis**: título enorme (número/benefício) → apoio (1 linha) → CTA em pílula. Logo pequeno.
- **Grade**: margens de 5–7 % e alinhamento comum à esquerda (ou centro). Tudo encosta na mesma linha.
- **Contraste**: texto sobre área calma (degradê escuro por baixo se o fundo for agitado). Teste ≥ 4,5:1.
- **Sobreposição intencional**: herói pode cruzar o título ou sair da borda — dá profundidade; nunca cobrir o logo
  ou o CTA.
- **Respiro**: 20–30 % de área vazia. Se tudo grita, nada grita.
- **Stories (1080×1920)**: deixe livres os 14 % de cima e 20 % de baixo (interface do app); herói no meio.
- **Banner 16:9**: texto num lado, herói no outro; nunca centralizar tudo.
- **Consistência de campanha**: mesma família de fundo, mesmo herói, mesma posição do CTA em todas as peças.
- **Cores**: as do perfil do cliente (`library.py profile <Cliente>`) ou do projeto. Destaque só onde o olho deve ir.

## Pedidos ao Gemini (gemini.py)
Estrutura do prompt: **sujeito + ação/pose + cenário + luz + câmera/lente + estilo + paleta + restrições**.
- Elemento isolado para recorte: use `--element` (fundo branco liso, sem sombra, sem texto) + `--cutout`.
- Fundo/textura: diga a proporção (`--aspect 9:16`) e "espaço vazio à esquerda para texto".
- Pessoas reais da marca: **só com termo de imagem por escrito que cite edição por IA** (`direcao-de-arte/
  references/ia-imagem-video.md`); sem termo, a IA não toca na pessoa — edite só fundo/luz em código ou recorte.
  Com termo: mande a foto com `--ref` e descreva só o que muda ("mesma pessoa, agora…") e confira a fidelidade.
- Estilo de campanha consistente: reutilize as mesmas referências de estilo em todas as gerações.
- **Nunca peça o texto final ao modelo** — o texto vai por cima, no `compose.py`/`lockup.py`.
- **Gente que não parece banco de imagem**: diga a idade do público ("in their twenties and early thirties"), o gesto
  espontâneo ("caught mid-laugh, not looking at the camera", "mid-stride"), a luz real ("direct on-camera flash",
  "white LED street lamps") e escreva "candid, unposed, documentary, not stock photo". Sem isso o modelo devolve
  gente madura posando e sorrindo para a câmera. Modelo completo: brand-system
  references/aplicacoes.md T11.
- Comece com `--n 3 --size 1K` (barato) e só refaça em `2K/4K` a escolhida. Veja gastos com `gemini.py usage`.
- Modelo: sempre `--model banana21` (Nano Banana 2.1, padrão). Outro modelo só se o usuário pedir.
Exemplos:
```
gemini.py gen "anilha olímpica de borracha preta com detalhes verde-limão, flutuando, luz de estúdio dramática, render 3D realista" --element --cutout -o out/anilha --n 3
gemini.py gen "fumaça densa verde-limão e preta, fundo preto, iluminação lateral, textura de alta resolução, espaço vazio à esquerda" --aspect 9:16 -o out/fundo
# só com termo de imagem que cite IA (ver acima):
gemini.py edit professor.jpg "mesma pessoa, fundo de estúdio preto com luz de recorte verde-limão nas bordas, braços cruzados" -o out/prof
```
