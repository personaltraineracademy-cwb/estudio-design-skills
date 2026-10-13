# Aplicações, composição, mockups e IA de imagem

**Peças do sistema saem dos MODELOS** (`modelos.py`, references/modelos.md): o gesto próprio da marca + medidas →
fidelidade em qualquer formato. As receitas abaixo são o ponto de partida genérico (minutos, sem gesto próprio) —
úteis no primeiro impacto e como base de comparação.

## Receitas (`apply.py build`; `apply.py list`)
| Receita | Quando |
|---|---|
| supergrafico | símbolo gigante em campo próprio sangrando a borda + título no campo oposto — assinatura da marca |
| tipografico | título enorme em bloco sobre a cor — campanhas, frases, manifesto |
| padrao | dispositivo em tela cheia + painel sólido com a mensagem — fundos ativos, eventos |
| moldura | cantoneiras no ângulo do DNA + título central — editorial, citação, convite |
| numeral | número herói (preço, %, dado) + rótulo — ofertas, resultados, contagem |
| foto | foto em tela cheia + supergráfico + título — precisa de `applications[].photo` |
Conteúdo por peça em `brand.json.applications` (`recipe, headline, sub, cta, number, label, photo, formats`).
Formatos: post, feed, story, banner, a4, outdoor, web-728, web-300, slide, thumb. As peças saem com texto vivo e um
`*-express.html` (fontes e imagens embutidas) para importar editável no Adobe Express.
Receitas são ponto de partida: crie layouts próprios com `brand-studio/compose.py` quando o território pedir.

## Regras de composição
- Um gesto grande por peça; o resto contido. Respiro 20–30%.
- Título é o maior possível no campo dele (as receitas quebram as linhas para maximizar o corpo).
- O supergráfico nunca cruza o título: campos separados no grid.
- Stories: nada nos ~13% de cima e ~20% de baixo (interface).
- Consistência de campanha: mesma família de fundo, mesmo herói, CTA no mesmo lugar em todos os formatos.

## Teste de estresse (`apply.py stress`) — 10 aplicações
favicon 16/32/48 px · avatar redondo · carimbo 1 cor · negativo · outdoor 3:1 visto de longe · story com interface ·
co-branding · sobre foto movimentada · merch (bordado pequeno) · padrão na embalagem. Somar: teste de desfoque (só
a forma dominante sobrevive?) e de memória (redesenhar de cabeça após 5 s). O que falhar → ajuste o sistema, não a
peça.

## Mockups (`mockup.py`)
Regra: **a IA nunca redesenha a marca**. Gemini gera a cena com a superfície **em branco**; o código encaixa a arte
exata com perspectiva + luz da foto (OpenCV: warp + multiply da luminância). Objetos rígidos (pôster, cartão,
placa, tela, caixa, sacola lisa) funcionam melhor; tecido amassado e pessoas, só como referência de clima.
Cenas típicas: pôster em parede de concreto · outdoor na rua · tela de celular na mão · cartão de visita sobre
mesa · sacola de papel · camiseta lisa dobrada · fachada/placa · tela de evento.
Presets: `poster`, `outdoor`, `celular`, `cartao`, `sacola`, `tela-evento` (dia) e `poster-noite`, `outdoor-noite`,
`celular-noite` (noite, LED branco, sem neon). Por marca, `brand.json.mockups` escolhe a arte exata e pode trocar o
prompt ou criar presets: `{"poster-noite": {"art": "aplicacoes/janela/pecas/janela-1080x1350.png"}, "fachada":
{"prompt": "…", "aspect": "4:5", "art": "…", "quad": [x1,y1,…]}}`. Sem `art`, usa a peça do formato certo (peças dos
modelos antes das receitas). Cenas ficam em cache em `mockups/cenas/` (refazer = apagar a cena).

## IA de imagem (Gemini — brand-studio/gemini.py, modelo padrão nano-banana-2.1)
Boas práticas (Google + comunidade, 2025–26):
- Frases, não lista de tags; diga **para que** é a imagem e para quem. Estrutura: sujeito + ação + lugar +
  composição + estilo + proporção + luz/câmera + material.
- Comece pelo verbo (Render, Combine, Transform, Remove). Descreva o que deve aparecer ("rua vazia"), não o que falta.
- Texto final **sempre** por cima com compose/lockup (letra miúda e ortografia falham).
- Referências: até 14 por pedido; nomeie o papel de cada uma ("Image 1 = forma, Image 2 = material").
- 80% certo → edite em vez de gerar de novo; mude uma variável por vez; diga o que fica idêntico.
- Sem transparência real: fundo liso de cor ausente do objeto (#00B140 ou #D9D9D9) → `--cutout` (rembg).
- Padrões contínuos: vista ortográfica de cima, sem sombra, "quatro bordas casam" — **teste em mosaico**.
- Séries consistentes: fixe traço, raio, grade, nível de detalhe; HEX no prompt e confira a cor no resultado.
- Proporções: 1:1 3:2 2:3 3:4 4:3 4:5 5:4 9:16 16:9 21:9; tamanhos 1K/2K/4K (K maiúsculo). Saída leva SynthID.

### Modelos de prompt (EN; campos entre colchetes)
- **T1 objeto isolado (`--element --cutout`)**: Render a single [object] made of [material + finish], [form details].
  Studio product shot, three-quarter view from slightly above, soft key light top-left, subtle rim light. Centered
  with generous margin on a perfectly flat uniform [#00B140] background, nothing else in frame. Purpose: isolated
  asset for a [brand/audience] campaign. 1:1, 2K.
- **T2 padrão contínuo**: Create a seamless tileable repeat pattern for [brand] built only from [motif described
  geometrically]. Flat 2D, top-down orthographic, no perspective, shadows or gradients, no text. Exactly [2–3]
  colours: [#HEX] on [#HEX]. Even density; motifs crossing an edge continue on the opposite edge. 1:1.
- **T3 textura**: Full-frame macro of [uncoated paper fibres / risograph ink on newsprint / brushed aluminium], flat
  diffuse light, no vignette, uniform, seamless, background overlay. Neutral [colour]. 1:1, 2K.
- **T4 exploração de forma (→ vectorize.py)**: A sheet of 9 flat graphic marks in a 3×3 grid on white, each built
  only from [constraint], solid [#HEX], hard clean edges, no outlines, gradients, 3D or text, equal visual weight.
  Each explores [metaphor] differently. Swiss modernist precision. 1:1.
- **T5 ícones (rascunho)**: A set of 12 icons for [brand] in a 4×3 grid on [#HEX]: [list]. Rules: 24-unit grid,
  uniform monoline stroke, [square] terminals, [2-unit] radius, one accent fill [#HEX] once per icon, no text.
- **T6 material 3D**: A 3D render of the number "[50]" as a solid object made of [polished chrome / matte ceramic /
  resin], bold condensed letterforms, front view, slight tilt, single softbox, flat [#D9D9D9] background. 1:1, 2K.
  (Tipografia exata: brand-studio `render3d.py`.)
- **T7 foto com espaço para título**: A [low-angle] photograph of [subject + action] for a [brand] campaign aimed at
  [audience], in [location], [hard late-afternoon side light], [85mm, f/2], [muted, warm shadows]. Subject on the
  right third; the left two thirds is an empty [concrete wall] reserved for headline text. No text. 4:5.
- **T8 cena para mockup (superfície em branco)**: A photograph of [a blank white poster on a raw concrete wall /
  a blank white business card on a dark wood desk], [front-on / slight angle], natural [soft daylight], the
  [poster] is completely blank and matte, sharp edges, fills about [40]% of the frame. No text or logos. [4:5]
- **T9 série com estilo travado**: Use Image 1 and Image 2 as style reference only: match palette ([#HEX], [#HEX]),
  grain, light direction and shape language; do not copy their subjects. Create [new subject] as part [3] of a
  consistent series. [1:1]
- **T10 fundo abstrato para KV**: Abstract campaign background for [brand]: [light through ribbed glass / folded
  paper relief] in [#HEX] and [#HEX], soft depth, no recognisable objects, no text, low detail in the [left] where
  logo and headline sit. [16:9 / 9:16], 2K.
- **T11 foto de gente que não parece banco de imagem**:
  Candid [night street] photography in [city], [direct on-camera flash], a small group of [young people in their
  twenties and early thirties], diverse, [casual mismatched clothes], mid-[action] crossing the frame, caught
  mid-laugh **not looking at the camera**, [one foot in the air], slight motion blur in background lights,
  [white LED street lamps], grainy 35mm film look, documentary, unposed, **not stock photo**, no [neon], no lens
  flare, no logos, no text. [4:5], 2K. Diga sempre a idade do público e "não olha para a câmera".
- **Edição**: Keep composition, camera angle, object shape and background exactly the same. Change only [one thing].
