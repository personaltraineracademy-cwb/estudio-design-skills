# Sistema — cor, tipo, forma, grid, ícones, movimento, tokens

## Cor (`palette.py`)
- Sementes (brand, ink, paper, accent…) em `color.seeds` com **nome próprio** (o nome é ativo: "Brasa", não
  "laranja"). Proporção de uso em `color.proportion` (ex.: papel 50 · tinta 30 · marca 15 · acento 5).
- `palette.py build`: escalas OKLCH 50–950 (a semente exata fica dentro da escala), neutros tingidos com o matiz da
  tinta, papéis light/dark (`bg, surface, border, text, text-muted, brand, on-brand, brand-text, accent…`), matriz
  de contraste **WCAG 2 + APCA** e aviso de cor quase igual às de marcas irmãs do mesmo cliente.
- Regras: WCAG 2.2 AA é a norma (4,5:1 texto, 3:1 grande/UI); APCA como guia (Lc 90/75 texto, 60 médio, 45 títulos).
  Cor de marca clara (lima, amarelo) **nunca** como texto sobre claro → use `roles.brand-text`.
- `palette.py harmonize <hex> --client X`: acentos por relação OKLCH (complementar, split, tríade, análoga, tensão).
- CMYK é aproximado (sem perfil ICC): o manual avisa "aprovar prova com a gráfica"; cores muito vivas (lima, neon)
  podem exigir cor especial (Pantone) — confirme no guia físico, não existe base Pantone livre confiável.
- Paleta "contra a categoria" (Peloton, ITVX) é dispositivo: mapeie as cores dos concorrentes e mire a região vazia.
- **Trocou a paleta?** Varra os HEX antigos em código, temas e peças (`grep`) e olhe a folha: cor retirada pela
  pessoa sobreviveu num painel. Cor reprovada vale para o contexto onde foi reprovada; ela pode voltar
  com função (o roxo reprovado como logo voltou como cor de produto).
- **Nomes de cor são proposta** enquanto a pessoa não disser "sim": `products[].color_name.status` começa com
  "proposta" e o manual, o DESIGN.md e a demo marcam. Nome de cor também é decisão do cliente, não do estúdio.

## Tipografia (`typesys.py`, `direcao-de-arte/scripts/tipos.py`)
- Máx. 2 famílias com papéis claros (display × texto) + 1 mono só para o relógio grande; contraste de estrutura
  (grotesca × humanista/serifa), altura-x e época compatíveis. Teste acentos (ã õ ç ê), números tabulares e preços
  (R$ 1.997,00), itálico real, e a confusão I/l/1 e O/0 medida no tamanho de celular.
- Escala modular base × razão (1,2 · 1,25 · 1,333 · 1,5 · 1,618); níveis display→caption com entrelinha e tracking.
- Evite as "fontes de IA" (Inter, Roboto, Space Grotesk, Poppins, Montserrat, DM Sans…) — se usar, justifique em
  `type.rules`. Prefira OFL (uso comercial, embutir em PDF/app, redistribuir com a licença) — `fonts.py get`.
- Diferencial forte: **letra/numeral próprio** ou fonte display derivada do DNA (dispositivo 13). Use fontTools/
  fontmake quando o projeto pedir; lettering do logo sempre em curvas.
- Adobe (conector): `font_recommend`, `suggest_type_palettes` como segunda opinião de pares (Adobe Fonts não pode
  ser distribuída — indique substituta OFL).
- **Uma fonte da verdade por decisão**: peso e largura de cada papel (voz, texto, dado, relógio)
  valem igual no código das peças, no `campanha.json` e em `brand.json.type`. Se divergir, vale o que as peças
  APROVADAS usam; corrija os outros e escreva a data em `type.alinhamento`.
- Trocou a fonte → refazer os kits de elemento e todo texto de elemento em PT-BR (nada de "ADMIT").

## Forma (raios) — `shape` + `direcao-de-arte/references/forma.md`
- **Duas camadas**: escala (`none · sm · md · lg · full` — arte 1080: 0 · 16 · 28 · 44 · pílula; site: 0 · 6 · 10 ·
  16 · pílula; arte ≈ 2,75 × site) e **papéis** (`card, tarja, button, field, media, avatar, focus…`). O componente usa
  só o papel; trocar a semente da escala muda a personalidade da marca inteira.
- **Linguagem A (padrão testado)**: o reto é o sinal, a curva é a escola — o que é assinatura (logo, tarja, visor,
  relógio, grade de telas, rótulo AO VIVO) fica 0 e é raro, por isso salta; conteúdo e gente (cartão, painel, lower
  third, foto solta, etiqueta) ganham a curva da família. B = tudo macio com um corte; C = tudo reto com uma pílula.
  Mostrar A/B/C numa folha e deixar a pessoa escolher; até lá, `shape.status` = "proposta".
- **O logo nunca arredonda** sem a pessoa pedir ("arredonde os elementos" não é "arredonde o logo"); `nunca_arredonda`
  lista o logo e os sinais. Por peça: 1 valor da família + 0 + pílula/círculo = no máximo 3 formas; nunca dois raios
  quase iguais (razão < 1,5); aninhado = pai − (borda + espaço), nunca negativo (0 = reto dentro de redondo, conta certa).
- Saídas: `tokens.css` (`--radius-none…full` + `--radius-<papel>`; `[data-meio="arte"]` troca para a escala da arte),
  tokens DTCG `dimension` (arte em `$extensions`), DESIGN.md "Forma", página "Forma" do manual (regra, escala em
  tamanho real, elemento → papel → raio, conta do aninhado, 3 certos × 3 errados, prova de que o logo não arredonda).
- Checagens futuras F1–F14 (raio fora da escala, raio > ½ lado, `%` em retângulo, foco ≠ raio + afastamento…).

## Grid e layout (`apply.py`)
- `grid`: colunas, margem (fração da largura), calha, linha de base, **ângulo próprio** (do DNA); `grid.web`
  (breakpoints 390 · 768 · 1440 e container) vira `breakpoint-*` e `container-*` nos tokens.
- Müller-Brockmann: linha de base b = entrelinha do texto; calha = b; campo = k·b; margem = o que sobra.
- Stories 9:16: ~13% em cima e ~20% embaixo cobertos pela interface — nada de texto ali. Zonas medidas por formato:
  `direcao-de-arte/references/qualidade.md` §Zonas.
- Formatos: post 1:1 · feed 4:5 · story 9:16 · banner 16:9 · A4 · outdoor 3:1 · web 728×90/300×250 · slide · thumb.

## Ícones
Grid 24 · margem ≥ 1 px · traço = espessura do DNA escalada (`elements dna` dá a sugestão) · pontas/junções iguais
às do logo · 2 px entre elementos · mesma massa óptica. Desenhe a linha central e expanda o traço (skia-pathops
`stroke`) → pesos light/bold do mesmo esqueleto. Gemini só como rascunho (pictograma P&B) → esqueleto → retraçar.
Referências de estudo (não copiar): Lucide (ISC), Tabler/Phosphor (MIT). Ícones em `<marca>/icones/*.svg` entram no
manual automaticamente (bloco `icons` preenchido sem desenhos → capítulo pulado + aviso de cobertura).

## Movimento
Um **verbo** derivado da ideia (órbita, empilhar, inclinar, revelar) → 2–3 curvas com nome ligado ao conceito
(`motion.easing`), 3–5 durações em escala ×1,5 (`motion.durations`), stagger padrão, "assinatura" (vinheta do logo —
brand-studio `motion.py`), regra de movimento reduzido. No máximo 2 coisas se movendo ao mesmo tempo (Uber).
**Produtivo × expressivo**: o par produtivo (0,2 · 0 · 0,38 · 0,9, IBM Carbon) é para tarefa de interface (menu,
validar campo) e entra nos tokens mesmo sem estar na marca; o expressivo é só para o momento importante (a revelação
da tarja). `motion.easing_notes` diz a origem e o uso de cada curva.

## Acessibilidade (capítulo e tokens)
12 regras padrão (`tokens.A11Y_RULES`: contraste no pior pixel, interface 3:1, foco 2 px e 3:1, alvo ≥ 24 px com nosso
padrão 48, ≤ 3 piscadas/s, movimento > 5 s com pausa e `prefers-reduced-motion`, alt ≤ 2 frases, legenda queimada,
hashtag em Maiúsculas, ≤ 3 emojis, linguagem simples) + as da marca em `accessibility.rules`. Tokens:
`--focus-ring-width/offset/color`, `--target-min`, `--opacity-disabled`, `--state-hover` (8%), `--state-pressed`
(10%). **Cor nunca sozinha** (WCAG 1.4.1): todo produto traz rótulo escrito; azul e roxo iguais para deuteranopia —
`color_pairs_cvd` (ΔE2000 < 10 em visão normal/deutan/protan/P&B) lista os pares que confundem.

## Tokens (`tokens.py`)
DTCG 2025.10 (estável): `core.tokens.json` (cores com `{colorSpace, components, hex}`, dimensões `{value, unit}`,
`fontFamily`, `fontWeight`, `typography`, `duration`, `cubicBezier`) + `light/dark.tokens.json` (papéis com alias
`{color.brand}`) → `tokens.css` (variáveis + classes `.t-*`), `tailwind.css` (`@theme` v4), `figma/<modo>.tokens.json`
(importar como modo de variáveis: px, segundos, família única) e **`DESIGN.md`** (formato google-labs: YAML de cores/
tipografia/raios/espaços/componentes + seções Overview…Do's and Don'ts, e as nossas: Forma, Movimento, Acessibilidade,
Produtos com a árvore "qual cor usar" e o daltonismo, Canais oficiais) — qualquer IA/dev gera peças e telas dentro
da marca a partir dele.

### Demonstração (`tokens/demo.html`, `demo.png`, `demo/*.png`, `demo/blocos.json`)
- Componentes feitos SÓ com variáveis: **botão × 7 estados** (padrão, hover, foco, pressionado, desabilitado,
  enviando, sucesso), **campo × 5** (vazio, preenchido, foco, erro, desabilitado), **estado do evento × 5** (em breve,
  hoje, ao vivo, encerrado, replay), tarja e preço, cartão, chip ● ao vivo, escala tipográfica, paleta, forma, as N
  cores lado a lado (normal · P&B · deutan · protan) e rodapé de canais oficiais. Modo escuro; `prefers-reduced-motion`.
- **Copy da demo = só a do cliente** (`brand.json.demo`). Sem copy → "[a definir]"; nunca CTA nem
  preço "de/por" de exemplo. Rótulos de interface ("Enviando…", "Enviado") e o e-mail de exemplo são genéricos.
- Tamanhos que dependem do nome (tarja, cartão, contador) são medidos com a fonte real para caber; o verificador
  roda no navegador (texto estourando a célula, botão < 40 px, fonte que não carregou) — OLHE `tokens/demo.png`.
- **Pedaços em tamanho real**: cada componente tem `data-sub`/`data-titulo`/`data-tokens`; o `render_demo`
  fotografa cada pedaço (2×) e grava `demo/blocos.json`. O manual mostra a marca-mãe completa e, por produto, só o
  resumo (botão + tarja/cartão), 1 px da demo = 1 px da página, com a legenda dos tokens ao lado. Nunca cortar um
  bloco no meio de um componente (o corte automático por "faixa vazia" partia o cartão entre o desenho e o texto).

## Cores de contexto e produtos (marca-mãe + sub-identidades)
Componentes usam só variáveis de contexto: `--color-bg`, `--color-ink`, `--color-accent`, `--color-on-accent`,
`--color-error` (+ `-surface`, `-line`), `--color-live`, `--color-focus` (na marca-mãe = papéis do modo light/dark).
**Erro** é token FIXO da campanha (`color.error`: `escuro` nos fundos escuros, `papel` nos claros; nunca a cor do
produto); sem cor que passe 4,5:1 (azul cheio), a mensagem vai numa tarja escura; formato: fio 2 px + ✕ + "Erro:".
**Ao vivo** = `colors.dot` do produto (ponto que pisca a 1 Hz). **Foco** = a 1ª cor com ≥ 3:1 contra o fundo.
Com `brand.json.products`, cada produto troca as variáveis: `<section data-produto="<id>">` (+ `data-variante="alt"`),
e o tokens.css traz o contraste WCAG comentado ao lado de cada cor (texto ≥ 4,5:1 · destaque/título grande/gráfico ≥
3:1 · texto do botão ≥ 4,5:1; razão TRUNCADA, nunca arredondada para cima). Par do botão entre 3 e 4,5:1 → o botão
usa `--btn-fs` ≥ 18,7 px em negrito (texto grande WCAG) ou troca-se `on_accent`.
Também: `products.tokens.json` (DTCG, contraste em `$extensions`), `figma/produto-<id>.tokens.json` (um modo por
produto na coleção "produto"), seção "Produtos" no DESIGN.md e um bloco de componentes por produto na demo. O
terminal avisa cada par que falha com a correção.
Secundário = link sublinhado na cor de destaque com texto na tinta (o destaque como cor de texto pequeno costuma
falhar); rótulos e notas na tinta cheia (mistura "atenuada" cai abaixo de 4,5:1 em fundo de cor média).
**Texto pequeno nunca na cor do produto** (vermelho sobre preto 4,44:1 e roxo 4,47:1 só servem para título grande,
logo, tarja e ponto): rótulos pequenos usam tinta ou papel; o kit de elementos trata isso com `legivel()`.
**Um preto por produto?** Quatro pretos quase iguais (#101010, #111111, #0B0B0B, #0C0B09) são quatro valores de token
sem ganho visível: decida UM preto no início; se já divergiram, registre em `decisions` e unifique com as peças.
Opcional: Style Dictionary 5 / Terrazzo leem o mesmo DTCG para Android/iOS/Flutter.

## Logo de terceiros (pós, parceiro, instituição)
Entra SEMPRE na versão oficial MONOCROMÁTICA (branco ou preto, conforme o fundo), PEQUENA e nunca na cor da campanha
nem competindo com o logo da marca; sem alteração de proporção. Vive em `architecture.selos` e em `legal.licenses`
("da marca; só monocromático"). Se o terceiro não tem versão para o fundo (ex.: sem versão para branco), confira a
monocromática no fundo real antes de usar e peça o arquivo ao cliente.
