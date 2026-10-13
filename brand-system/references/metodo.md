# Método — do briefing ao sistema (como os grandes estúdios fazem)

Síntese de Pentagram, Collins, Koto, DixonBaxi, Wolff Olins, Porto Rocha, Studio Dumbar/DEPT, Order, Base, Tátil,
FutureBrand SP, Ana Couto (pesquisa de 10/2026). O que se repete em todos:

| Etapa | O que acontece | Artefato (nesta skill) | Tempo-alvo |
|---|---|---|---|
| 0. Enquadrar | cliente, ambição, modo (antes/durante/depois do logo), restrições | `brand.py init`, `briefing.md` | 5 min |
| 1. Imersão | concorrência, categoria, público, cultura, referências | `pesquisa/pesquisa.md` (references/pesquisa.md) | 15–20 min |
| 2. Plataforma | unicidade, ideia em 1 frase, inimigo, zag, tensões, princípios, jobs — **sem decidir cor nem estilo** | `plataforma.md` + `brand.json.platform` | 10 min |
| 3. **Primeiro impacto** | 3–4 símbolos rápidos, cor viva, fonte forte, elementos, 3 modelos de peça → **mostrar** | `elements.py`, `modelos.py` | 15–20 min |
| 4. Territórios / arena | divergir de verdade e julgar às cegas (com público e nota absoluta) | `arena.py` (references/arena.md) | 10 min (composições) · 40+ (territórios, só se pedido) |
| 5. Sistema | assinatura + DNA + kit de partes: cor, tipo, elementos, grid, imagem, ícones, motion, voz | `palette/typesys/elements` | 20 min |
| 6. **Modelos de peça** | 5–8 modelos com regra + medidas + comando → kit em todos os formatos | `modelos.py kit` (references/modelos.md) | 20 min |
| 7. **Variações com limite** | até 4 opções por eixo (logo, fonte, cor, elementos), 1 folha por eixo → a pessoa escolhe | `variacoes.py` (references/variacoes.md) | 30 min |
| 8. Codificar | mockups, tokens, manual (com "Modelos de peça"), DESIGN.md | `mockup.py`, `tokens.py`, `manual.py` | 15 min |
| 9. **Documentar** e cuidar | diário do processo; aprovar, registrar, evoluir | `diario.md`, `library.py add`, `_perfil.md` | contínuo |

## Uma ideia, muitas expressões (o mecanismo central)
1. **Ideia em uma frase**, ancorada numa verdade própria (do produto, da história, do lugar) — não num símbolo da
   categoria. Ex.: GoFundMe "Help adds up" (a barra de meta do produto vira o Progress Circle); Decathlon "move people
   through the wonders of sport" (L'Orbit); Olympikus (módulos de pista e bandeira).
2. **Assinatura (signature device)**: um elemento ou comportamento que encarna a ideia.
3. **DNA geométrico** da assinatura: ângulo, raio, espessura de traço, proporção, verbo de movimento
   (`elements.py dna`). O ângulo do Orbit vem do wordmark; as fontes da ITVX herdam o raio do X.
4. **Espalhar o DNA** por tipo, ícones, grid, movimento, foto, padrões (`elements.py explore/build`).
5. **Teste de estresse**: do favicon à fachada, produto, movimento, submarcas, co-branding (`apply.py stress`).
6. **Matriz constantes × variáveis**: o que nunca muda (≥ 1 componente reconhecível) e o que varia, com limites.

## Modos (quando a skill entra em relação ao logo)
- **antes** — sistema primeiro: plataforma → territórios → o logo nasce do território vencedor (feito com
  brand-studio/logo-design usando o DNA do sistema). Melhor para marcas novas: o logo já sai "sistêmico".
- **durante** — logo e sistema evoluem juntos: cada conceito de logo da brand-studio vira um território na arena,
  com elementos e aplicações; o que não gera sistema morre cedo ("se não gera padrão, KV e movimento, está fraco").
- **depois** — logo existe (do cliente ou aprovado): `elements.py dna logo.svg` → o sistema deriva do DNA do logo.
  Nunca redesenhe o logo sem pedido; evolua o valor de marca antes de substituir.

## Primeiro impacto (a lição mais cara)
Antes de qualquer arena longa, mostre **uma imagem forte em 15–20 min**: um símbolo simples que seja criativo de
verdade (nasce da verdade própria da marca), uma cor viva com história, uma fonte com personalidade, os elementos
gerados pelo `elements.py` e 3 modelos de peça com texto real. Simples só vale se for muito criativo; conceito que
não se vê em 2 segundos não conta. Depois aprofunde (arena, variações, sistema). Processo longo sem nada para
mostrar no meio = a pessoa perde a confiança.

## Checkpoints com a pessoa (pare e mostre imagens)
1. **Primeiro impacto** (15–20 min de trabalho) — sempre.
2. Depois da arena — top 2–3 com nota relativa E absoluta e o risco de cada um. Obrigatório, salvo "carta branca"
   (aí siga com o 1º e diga por quê; empate técnico → references/arena.md).
3. **Folhas de variação** — a escolha de logo, fonte e cor é da pessoa (recomende uma por eixo, com o porquê).
4. Antes do manual — kit de modelos + aplicações + teste de estresse + mockups.

## Documentar (sempre)
Mantenha `<marca>/diario.md` desde o início: cada pedido ou feedback da pessoa → o que foi feito → o que falhou
(com autocrítica honesta) → o que mudou → números (tempo, custo, arenas). Guarde provas leves em
`<marca>/historico/` (JPEG ≤ 2000 px) antes de apagar qualquer coisa reprovada (sempre para a Lixeira). Lições que
servem para outras marcas vão para as references desta skill — o diário é do projeto; a skill é de todo mundo.

## Oito entregas que provam que é sistema (não só logo)
plataforma em 1 página · frase-ideia · ficha da assinatura · folha de DNA · inventário do kit de partes ·
matriz constantes/variáveis · verbo de movimento · matriz de teste de estresse.

## Regras de ofício
- Nunca pular do briefing direto para o desenho (o "meio passo" de Michael Johnson é onde mais se falha).
- Conceito nasce em **palavras e esboços**; imagem de IA só depois (IA na ideação aumenta fixação — CHI 2024).
- Seja crítico com o próprio trabalho a cada render: colisões, leitura em 2 s, vazio sem função, cara de banco de
  imagem. Corrija na regra (modelo/sistema), nunca retocando a peça.
- Tempo é parte da qualidade: limite de tempo por subagente (≤ 15 min) e de opções por eixo (≤ 4).
- Tudo que é master em curvas, auditado; tudo renderizado e **olhado** antes de mostrar.
- O perfil de um cliente só vale para ele (`library.py profile`); cliente novo começa sem estilo herdado.
- Honestidade: diga o que não testou; recomende INPI para marca permanente; fontes com licença.

## Identidade em 2 fases
Projeto de identidade começa SÓ pelo logo: conceitos → checkpoint → acabamento → kit, até ela aprovar. Só depois o
sistema (cores por papel, tipografia, elementos, modelos, manual, design system). "Do zero" = perguntas neutras, nada
herdado (`brand-studio/references/briefing.md`). Pré-voo de todo projeto: `references/acertar-de-primeira.md`.
