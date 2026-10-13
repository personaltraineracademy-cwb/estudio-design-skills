# Páginas de captura premium — contrato e base da skill de sites

Este arquivo guarda (1) o CONTRATO que toda página de captura tem que cumprir e (2) as regras de prática que valem
para QUALQUER marca que já tenha identidade e logo. Complementa `site.md` (34 checagens, heros H01–H18, seções
S01–S19). O fluxo de produção vigente (template, `site.py`) está em `../criacao-de-sites/SKILL.md`.

## 0. Falhas típicas da 1ª tentativa (não repetir)
| Falha | Causa | Regra |
|---|---|---|
| Sem logo | página montada só com tipografia | logo em 3 lugares: barra do topo, hero, rodapé; símbolo no favicon e no pop-up |
| Nota de orientação na página | o documento de copy colado inteiro: "[confirmar…]", "Convenção", "O que evitar", variações de H1 | a página só tem COPY FINAL. Orientação, hipóteses e pendências vão para `pendencias.md` FORA da página |
| Sem padrão premium | 1 bloco cinza após o outro, tudo do mesmo tamanho, sem ritmo | ritmo de 2–3 fundos do mesmo sistema; 1 herói por tela; escala tipográfica com saltos grandes (≥ 2×) |
| Ruim de ler | corpo 21–24 px num canvas de 1080, cinza sobre preto, hero com título de 7 linhas | corpo ≥ 17–18 px mobile (fluido com clamp), contraste ≥ 7:1 no corpo, título do hero ≤ 4 linhas no mobile |
| Não responsiva | largura fixa de 1080 px | 4 breakpoints testados (390 · 768 · 1024 · 1440), sem rolagem horizontal, imagens com art direction |
| Sem pop-up/CTA que leva a algum lugar | botão sem destino | CTA único abre `<dialog>` com formulário curto → estado de sucesso → botão do grupo |
| Pesquisa não aplicada | estudo de referências feito e não usado | ler a pesquisa ANTES de desenhar e citar quais princípios entraram |

## 1. Entradas obrigatórias (sem elas, parar e pedir)
1. **Identidade pronta:** `brand.json` + logo (SVG em curvas, versões claro/escuro/símbolo), cores por papel,
   fontes (com prova do `tipos.py`), forma (`forma.md`), elementos (`ornamentos/`).
2. **Copy FINAL** dividida em blocos; orientações separadas (o que evitar, confirmar). Nada inventado: sem preço,
   "de/por", urgência falsa. Pendência = `pendencias.md`, nunca dentro da página.
3. **Fotos reais** tratadas (P&B, recorte limpo) em 2 larguras (720 e 1280, WebP) — nunca pessoa inventada por IA.
4. **Objetivo e destino:** CTA único (ex.: entrar no grupo do WhatsApp), campos do formulário, link de destino, datas reais.
5. **Zonas e contexto:** de onde vem o tráfego (Instagram/Meta → mobile ≥ 85%), tema escuro ou claro.

## 2. Estrutura de página (ordem e funções)
| # | Seção | Função | Regra |
|---|---|---|---|
| 0 | Barra fixa | contexto + CTA sempre visível | logo + data/hora + botão; no mobile vira barra de baixo de 64 px |
| 1 | Hero | O QUÊ · QUANDO · COM QUEM + 1 CTA | ≤ 640 px no mobile; foto real; logo; selos; sem rolagem para o CTA |
| 2 | Prova rápida | selos/números reais | 3 itens; só dados da copy |
| 3 | Como funciona | 3 passos | números grandes (herói), 1 linha cada |
| 4 | Oferta / programação | cartões por pessoa ou dia | foto, nome, data; cada cartão leva ao MESMO formulário |
| 5 | A condição | ex.: "pague 1, leve 2" | tarja/numerais gigantes; valores só se a copy tiver |
| 6 | Bônus | lista | ícone/numeração; sem preço inventado |
| 7 | Por que a marca | prova | números + selo; foto do time só se real |
| 8 | FAQ | objeções | acordeão acessível; ≤ 8 perguntas |
| 9 | CTA final | fecha | repete H1 curto + botão; mesmo pop-up |
| 10 | Rodapé legal | confiança | logo, canais oficiais, aviso legal da copy; `[a definir]` só em pendencias |

## 3. Contrato técnico (todo item é testado)
- **Protótipo** `index.html` + `assets/` (webp, svg): CSS com variáveis (tokens da marca); JS ≤ 4 KB (modal, máscara,
  contador, acordeão). Fontes locais (`@font-face`, `font-display:swap`), subset se possível. Produção: §4g.
- **Grid** de 12 colunas (desktop), 8 (tablet), 4 (mobile); container máx. 1280; margens fluidas (`clamp`).
- **Tipografia fluida** (`clamp`): H1 `clamp(2.6rem, 8.5vw, 8rem)`; corpo `clamp(1.0625rem, 1rem + .4vw, 1.25rem)`;
  medida do texto 45–75 caracteres; rótulo (eyebrow) em mono ≥ 13 px com fio.
- **Alvos de toque ≥ 48 px**; foco visível 2 px; contraste ≥ 4,5:1 (corpo ≥ 7:1 sobre escuro); sem texto sobre
  foto sem painel calmo (medir no pior pixel).
- **Pop-up** = `<dialog>` modal: foco preso, ESC fecha, rótulos visíveis, máscara de WhatsApp (DDD), erro inline,
  consentimento curto, `aria-live` no sucesso, scroll bloqueado, botão de fechar 48 px; sucesso mostra "Você está
  dentro" + botão do grupo (placeholder de demo).
- **Granulado único** fixo por cima (SVG feTurbulence; opacidade 0.55, 0.38 em página toda escura), **grid visível**
  como textura em 1–2 seções, elementos da biblioteca `ornamentos/` (tarja, visor, ingresso, cantoneiras, timecode,
  selo, régua) — no máx. 3 tipos por tela; forma A (reto = sinal, curva = conteúdo; arte 0·16·28·44 → site 0·6·10·16).
- **Movimento:** entrada .3–.5 s, 1 elemento principal por seção; nada piscando. Política completa no §7.
- **Performance:** LCP < 2,5 s; imagens WebP ≤ 150 KB (hero ≤ 220 KB); `loading=lazy`; CSS ≤ 40 KB; sem rolagem
  horizontal em nenhum breakpoint; `<meta viewport>`; `lang="pt-BR"`; `<title>` e descrição.
- **Contador honesto:** data real; depois da data troca de estado (hoje/ao vivo/encerrado) — nunca "00 dias".

## 4. Portão de qualidade (antes de entregar)
1. Renderizar em 390×844, 768×1024, 1024×768 e 1440×900 (Playwright, `full_page`); olhar cada um a 100% (seção por
   seção) e a 25% (ritmo da página).
2. Verificações automáticas: `scrollWidth <= clientWidth`; menor fonte renderizada ≥ 14 px (corpo ≥ 17); alvos de
   toque ≥ 48; contraste por trecho; imagens com `alt`; `<dialog>` abre/fecha por teclado; Lighthouse/peso.
3. Revisão de perfeccionismo (`qualidade.md` §Portão): quebrado? desalinhado? fora do padrão? leigo percebe?
4. Copy: `diff` contra `copy.json` — nenhuma palavra fora; nenhuma nota de orientação na página.
5. Entregar com imagens (as 4 larguras) + `pendencias.md` + `README` de como trocar o destino do botão.

## 4b. Diagramação CLEAN — regra permanente
Regra: página simples, bem espaçada, clean e premium — dá para ler, sabe-se o que está lendo, direto ao assunto
(captura e conversão). Premium é restrição, escala, respiro e leveza; menos seções, o dobro de espaço entre elas.
Composição ousada ≠ tela cheia: a ousadia vem de UMA coisa grande bem posicionada.

**Regras (medidas por `check_pagina.py`, bloco DENSIDADE):**
| # | Regra | Limite | Como medir |
|---|---|---|---|
| C1 | **Uma mensagem por tela:** 1 título + 1 apoio (≤ 2 linhas, ≤ 25 palavras) + 1 elemento visual OU 1 CTA | ≤ 8 blocos de conteúdo por altura de tela (mobile), ≤ 11 (desktop) | blocos por faixa de `innerHeight` |
| C2 | **Respiro de seção** | padding vertical ≥ `clamp(96px,16vw,200px)`; ≥ 72 px mobile / 112 px desktop | `padding-top/bottom` das `<section>` |
| C3 | **Espaço entre blocos** | título→apoio ≥ 24 px; apoio→CTA ≥ 40 px; blocos colados (< 10 px) = erro | menor vão vertical entre blocos sobrepostos em x |
| C4 | **Área vazia** | ≥ 38% de cada tela (alvo 50%) na cor de fundo dominante | % de pixels ≈ fundo, por tela |
| C5 | **Cartões** | padding ≥ 32 px, gap ≥ 32 px, ≤ 3 por linha, 1 por linha no mobile; sem borda+sombra em tudo | inspeção |
| C6 | **Decorativos** | ≤ 1 elemento gráfico (tarja, visor, selo, régua, grid, carimbo) por tela além do conteúdo | inspeção |
| C7 | **Tipografia** | ≤ 6 tamanhos; saltos ≥ 2×; corpo ≥ 18 px mobile, entrelinha 1.5, medida ≤ 62 caracteres | `check_pagina` (fonte mínima) |
| C8 | **Hero enxuto** | logo + H1 + 1 apoio curto + 1 CTA. O sub longo da copy vai para a seção seguinte | olho |
| C9 | **Teste dos 3 segundos** | cada tela: dá para dizer em 3 s o que a tela diz? | olho (perfeccionismo) |
| C10 | **Listas limpas** | FAQ e bônus como lista com linhas finas, não caixas | olho |
A copy NÃO muda: o que não cabe numa tela vai para a próxima (mais telas, cada uma mais simples).

## 4c. Primeira dobra enxuta — regra permanente
Regra: o nome da marca/campanha aparece UMA vez na dobra (na logo); repetir logo, nome e título 3–5 vezes é prolixo.
O básico bem feito vence o enfeite.
- **Dobra = logo + H1 + 1 subheadline + 1 CTA + foto.** Nada mais. Eyebrow, etiqueta com o nome da campanha, carimbo,
  selos, 2ª logo, texto de header extra: fora da dobra.
- **Subheadline** = o diferencial curto + a data numa linha mono (ex.: "Pague 1 e leve 2. · 9, 10 e 11/11 · 20h30").
  O parágrafo longo do sub e o microtexto descem para a seção seguinte.
- **Barra inferior fixa de CTA no mobile só aparece depois de rolar além do hero** (senão cobre as fotos e duplica o CTA).
- **Fotos de várias pessoas:** normalizar ANTES de compor — mesmo tamanho de rosto (detecção YuNet), mesmo P&B
  (percentis 2–99 + mesma curva), corte na MESMA linha com fade de alfa na base, sombra só onde há sobreposição
  (senão mancha em fundo claro). Gerar 2 composições: larga (3 lado a lado, desktop) e compacta (sobrepostos, mobile).
- **Orçamento da dobra mobile 390×844:** header 56 · logo 64 · H1 ≤ 4 linhas (40–44 px) · sub 26 · CTA 56 (full width) até
  y ≈ 620 · foto sangrando na base ~ 240 px (rostos ~ 75 px). **Desktop 1440×900:** texto col 1–6, foto col 6–12 ancorada
  embaixo (rostos ~ 140 px), nada de texto sobre rosto, respiro ≥ 48 px entre blocos.
- **Teste:** "em 3 segundos: o que é, quando e o que fazer?" nas 4 larguras (390, 768, 1024, 1440).
- **IA de imagem (opcional):** só para cenário/fundo/textura ou vídeo curto de ambiente, nunca para criar ou alterar
  pessoa. Fotos reais normalizadas costumam resolver a dobra.

## 4d. Como PENSAR a composição da dobra (método obrigatório)
Regra: compor com lógica, composição por composição, elemento por elemento. Erros típicos: logo grande duplicada
abaixo da logo do cabeçalho, sigla da campanha repetindo a logo, fotos longe do topo, nem tudo visível na dobra.

**Procedimento (fazer por escrito ANTES de codar, em `decisoes.md`, para cada largura):**
1. **Inventário:** liste TODO elemento que aparece na dobra (logo, símbolo, botão, H1, sub, data, micro, selos, fotos,
   nomes, numerais…) com a altura/largura que ocupa.
2. **Papel de cada um:** necessário (responde O QUÊ · QUANDO · O QUE FAZER) · duplicado (diz o que outro já diz) ·
   decoração. **Duplicado e decoração saem.** Uma coisa que o usuário já viu em outro lugar da tela não se repete
   (ex.: a logo no cabeçalho + a logo grande abaixo; a sigla da campanha + a logo; o nome da campanha na etiqueta + no H1).
3. **Um lugar para cada elemento, na ordem de leitura:** topo = identidade + ação (logo à esquerda, botão à direita);
   depois a prova visual (pessoas); depois a mensagem (H1 → sub → data); por último o CTA grande e a micro.
   No desktop, texto de um lado e pessoas do outro, ambos alinhados ao mesmo topo.
4. **Orçamento de altura (mobile 390×844) somado em px**, com sobra ≥ 40 px: cabeçalho 64 · pessoas 200–240 · H1
   (4 linhas × 44) 176 · sub 28 · data 22 · CTA 56 · micro 20 + vãos 16–24 ≈ 700. Se estourar, reduza a FOTO, não o
   texto, e nunca empurre o CTA para baixo de y ≈ 640.
5. **Conferir olhando** as 4 larguras (390, 768, 1024, 1440) e comparar com a regra: tudo visível sem rolar? nada
   repetido? cada coisa onde o olho espera? Se o cliente precisar apontar o óbvio, o procedimento não foi feito.

**Layout-padrão da dobra (muda só o arquétipo):**
- **Mobile:** [cabeçalho: LOGO (versão com nome) à esquerda · botão pequeno à direita] → [faixa de pessoas, ~ 200–240 px,
  largura total] → [H1] → [sub + data] → [CTA largura total] → [micro]. Sem sigla extra, sem segunda logo, sem eyebrow.
- **Desktop:** [cabeçalho: LOGO à esquerda · botão à direita] → duas colunas alinhadas ao topo: texto (H1, sub, data,
  CTA, micro) e pessoas (maiores, ancoradas embaixo/à direita). Nada de logo grande dentro do hero.
- A logo do cabeçalho tem altura 32–40 px (mobile) / 40–48 px (desktop), com área de respiro; é a ÚNICA logo da dobra.

## 4e. Descobrir sozinho: autocrítica automática da 1ª tela
A autocrítica não depende do cliente apontar: o `check_pagina.py` faz a **autocrítica da 1ª tela** e acusa sem ajuda
2 logos na tela, texto repetido, CTA baixo demais, subheadline sobre a foto:
| Pergunta que um diretor de arte se faz | Como o verificador responde |
|---|---|
| Algo aparece mais de uma vez? | mais de 1 logo na tela; trigramas de texto repetidos (inclui `alt` das imagens) |
| A ação está onde o dedo alcança? | CTA principal terminando abaixo de 76% (mobile) / 92% (desktop) da altura |
| Dá para ler sem atrito? | texto sobre foto (exceto `data-sobre-foto` declarado), blocos > 8/11 por tela, vãos < 10 px |
| As pessoas aparecem de verdade? | foto detectada na dobra e com ≥ 20% da altura da tela |
| A ordem de leitura faz sentido? | logo antes do H1; H1 antes do CTA |
| Cabe tudo na tela? | blocos fora da tela, rolagem horizontal, fonte < 14 px |
| Está alinhado, centralizado, harmônico? ("falta pouco") | bordas esquerda/direita/topo/base a 1–14 px de distância (quase alinhado); cabeçalho × conteúdo com a mesma margem; topo e base das colunas texto × imagem; vãos verticais quase iguais |

**Régua de alinhamento da dobra:** (a) UM container: borda esquerda da logo = do H1; borda direita do botão do
cabeçalho = do bloco de imagem; sangria só em fundo, nunca em metade dos elementos; (b) topo do bloco de imagem = topo
das MAIÚSCULAS do H1 (±1 px, pela tinta, não pela caixa); (c) base do bloco de imagem = base da coluna de texto
(±1 px); (d) rostos do mesmo tamanho e na mesma linha; (e) vãos verticais com no máximo 2 valores; (f) nada colado
(< 48 px) entre a dobra e o próximo elemento (faixa, ticker). Se algo difere de 1 a 14 px, é erro: igualar ou afastar
de verdade.
**Como usar:** rodar a cada rodada e tratar CADA aviso como pergunta a responder (corrigir ou justificar em
`decisoes.md`). Sobreposição proposital (nome sobre painel) se declara com `data-sobre-foto`. O verificador cobre o que é
mensurável; o resto é olhar e pensar: "se eu fosse o cliente vendo isto no celular, o que me incomodaria?" antes de
mostrar. Quando o cliente apontar algo que o verificador não pegou, transformar em checagem nova.

## 4f. Sistema de espaçamento (corrigir uma coisa sem criar outro erro)
Regra: toda correção passa de novo pelo sistema inteiro (espaçamento, alinhamento, hierarquia), não só pelo que foi
apontado. Erro típico: "pôr tudo na dobra" e deixar tudo comprimido, colado entre si e perto das bordas.

| Papel | Valor (px) | Onde |
|---|---|---|
| Escala base | 4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 · 64 · 96 · 128 · 160 · 200 | todo espaçamento é um destes |
| Margem lateral da página | mobile 24 · tablet 40 · desktop `clamp(48px, 6vw, 112px)` (mín. 20 / 40 aceito) | header e conteúdo no MESMO container |
| Cabeçalho | altura 64–72; logo 32–40 (mobile) / 40–48 (desktop); folga ≥ 12 em cima/baixo | topo |
| Vãos dentro da dobra | 12 (mesmo grupo: sub↔data, CTA↔micro) · 24 (grupos relacionados: header↔foto, H1↔sub) · 40 (grupos separados: foto↔H1, data↔CTA) | no máx. 3 valores por tela |
| Fim da dobra | ≥ 40 de ar antes do próximo elemento (nunca faixa/ticker dentro da 1ª tela) | hero |
| Seções | mobile 96–128 · desktop 128–200 entre seções | verticais |
| Título → conteúdo | 40–56 | seções |
| Cartões | padding ≥ 24 (mobile) / 32 (desktop); gap ≥ 16 (mobile) / 24–32 | grades |
| Alvos de toque | ≥ 48 de altura; ≥ 8 de distância entre alvos | botões/links |
Orçamento da dobra mobile (390×844) com este sistema: header 64 + 24 + foto 170–190 + 40 + H1 (4×44) 176 + 24 + sub 32 +
12 + data 20 + 40 + CTA 56 + 12 + micro 20 + 40 de ar ≈ 740 → cabe com sobra; se não couber, **diminui a foto**, nunca os
vãos. O `check_pagina.py` mede margem lateral, folga do topo, vãos < 12 px e número de valores de vão diferentes.

## 4g. Tecnologia: stack avançado, hospedável em qualquer lugar
Regra: página de produção não é arquivo HTML solto; usar a tecnologia mais avançada que ainda rode em hospedagem
estática (Hostinger, Vercel e similares).
| Camada | Escolha | Por quê / limite |
|---|---|---|
| Framework | **Next.js 16 (App Router) + React 19 + TypeScript 5** | `output:'export'` gera arquivos estáticos: Vercel (nativo) e Hostinger compartilhada (enviar `out/` para `public_html`) |
| Estilo | **Tailwind CSS v4** com `@theme` = tokens da marca | variáveis CSS, sem runtime |
| Movimento | **CSS scroll-driven** (1ª escolha) + **GSAP 3.15** (ScrollTrigger/SplitText, só onde precisa, `dynamic import`) + Lenis opcional (desktop) | GSAP "No Charge" só em página SEM cobrança de acesso |
| Efeitos | shader WebGL de grão (~1,3 KB) com pausa fora da tela e fallback | sem three.js/R3F (pesados) |
| Pop-up | `<dialog>` nativo em componente React | a11y, 0 KB de biblioteca |
| Formulário | POST JSON para `NEXT_PUBLIC_LEAD_ENDPOINT` (Make/n8n/PHP); vazio = demo | funciona em qualquer hospedagem estática |
| Verificação | `scripts/check_pagina.py <url ou arquivo>` (4 larguras + autocrítica) | roda contra o build servido |
**Restrições de hospedagem estática:** sem API routes, sem middleware, sem Server Actions, sem `next/image` de servidor
(`images.unoptimized`), `trailingSlash:true`, `.htaccess` (gzip, cache, 404) e `vercel.json`. "Tecnologia avançada" não
é peso: orçamento de JS inicial ≤ 150 KB gzip por rota e LCP < 2,5 s; a 1ª tela é HTML estático hidratado.

## 5. Skill `criacao-de-sites`
Template Next.js limpo, receitas de dobra, `site.py new|check|pack|copy-diff|marca`: `../criacao-de-sites/SKILL.md`.
Componentes a ter no template: barra fixa, hero, selo, passo numerado, cartão de pessoa, bloco de oferta, lista de
bônus, acordeão FAQ, modal de captura, contador, rodapé, faixa rolante, régua de seção.

## §6 Do HTML aprovado para o site de verdade (Next.js) — ordem do porte
1. HTML aprovado nos 3 portões (0 erros no `check_pagina.py`) ANTES de portar. O porte não redesenha: compara
   retângulo a retângulo com o aprovado nas larguras (diferença ≤ 1 px).
2. Base compartilhada primeiro (logo, foto, botão, pop-up, relógio, fontes, copy em JSON, tokens). Cada versão em
   `app/vN`, `components/vN`, `public/img/vN`; agentes em PARALELO em cópias (`site-v1/2/3`) e só essas pastas
   voltam para a base (diff antes de mesclar: nada de arquivo compartilhado alterado).
3. Texto SEMPRE da copy final (JSON): o porte lê a copy e pega palavra perdida no HTML.
4. Depois de mesclar: typecheck + lint + testes + build + verificador em cada rota + olhar **rolando de verdade, seção
   por seção** + varredura de botões em 11 larguras + build de raiz E de subpasta (`NEXT_PUBLIC_BASE_PATH=<pasta>`) com
   zero requisição falha + `npm ci` e build num diretório limpo.

Regras (cada uma nasceu de um defeito real):
- **Animação ligada à rolagem usa `animation-fill-mode: forwards`, nunca `both`.** Com `both` a peça fica escondida
  antes da faixa; captura de página inteira, impressão e leitor sem rolagem viam blocos "vazios". O estado natural do
  CSS tem que ser o estado FINAL.
- Foto pequena de seção abaixo da dobra sobre painel colorido: `loading="eager"` + `fetchpriority="low"`.
- **Rótulo de botão sempre em 1 linha**, em toda largura (360 px incluso). Largura mínima de botão `nowrap` alarga a
  trilha da grade e empurra título e tarja. Medir pelos retângulos do TEXTO, não pela altura do botão.
- Editar CSS por troca de trecho dentro de `@media` pode fechar o bloco antes da hora. Build + verificador depois de
  TODA edição de CSS; o verificador acha o que o olho não vê.
- Verificador mede também 360 × 740 e dá ERRO para CTA em 2+ linhas. Screenshot no meio da animação de entrada engana:
  se a dobra "parece quebrada", conferir se é movimento ainda rodando antes de mexer.
- Mesclar não é o fim: conferir `?agora=ISO` (5 estados do relógio), pop-up (teclado, ESC, foco), `.htaccess` e 404.

> **Metodologia fixa (tokens, dobra, responsividade, produção): `padrao-de-pagina.md`.**

## §7 Testar como o visitante real vê
O teste headless esconde coisas que o navegador real mostra:
| Sintoma | Causa | Regra |
|---|---|---|
| "faltam animações; a faixa não passa" | o sistema do visitante tem **movimento reduzido LIGADO** (`prefers-reduced-motion: reduce`); toda animação some e a faixa fica parada com palavra cortada | testar SEMPRE nos dois estados; o movimento roda sempre (suave para quem reduz, política abaixo) |
| "um lado maior que o outro" (mobile) | (a) **barra de rolagem de 15 px**: `100vw` inclui a barra; (b) **recorte** com a tinta deslocada no arquivo | (a) nunca `100vw` em medida de layout: usar `%`, `cqw` (container) ou variável medida; (b) foto recortada em moldura/coluna é centrada pela TINTA (bbox do alfa), canvas igual |
| granulado forte demais | grão global a 0.8 de opacidade | 0.55 padrão; 0.38 em página toda escura; papel (multiply 0.12) funciona |
| bloco escuro solto na área clara | painel escuro retangular "flutuando" | o escuro nasce de uma faixa de borda a borda ou de uma coluna inteira |
| bloco final estranho | numerais gigantes + listras de fundo + CTA: três ideias numa tela | uma ideia por bloco final; sem textura listrada atrás de texto |

### Política de movimento: SEMPRE ligado
- O movimento roda para TODOS. Nada atrás de `prefers-reduced-motion: no-preference`.
- `<html data-movimento="total|suave|parado">` (script em `app/layout.tsx`): `total` padrão; `suave` quando o sistema do
  visitante pede menos movimento = MESMA coreografia, distâncias ≤ 8–12 px, sem parallax/tilt/magnético/escala grande,
  durações ≤ 0,4 s, loops mais lentos, faixa a ×1,8 com botão de pausa visível, nada piscando > 3×/s; `parado` só por
  `?movimento=parado` (impressão/teste). JS: `motionMode()` em `lib/motion.ts`.
- Linguagem de movimento ÚNICA e SIMPLES por página: uma ideia assinatura do conceito repetida com variações, mesma
  curva e tempos, poucos gestos bem escolhidos (não um catálogo de efeitos).
- Verificador: a passagem com `reduced_motion="reduce"` exige conteúdo visível/não cortado E que a página anime no modo suave.
- Ligar/desligar "Efeitos de animação" do sistema muda só a versão (total × suave), nunca zera.

### Dobra desktop: sinais de composição desligada
Tecnicamente limpa (0 erros) e mesmo assim estranha. Reconhecer:
- **Faixa decorativa sem origem**: tira escura cortando as pessoas, que não nasce do grid nem do conteúdo. Elemento
  escuro precisa ter função e origem (a seção seguinte, uma coluna inteira, um cartão), nunca uma "listra".
- **Duas camadas desligadas**: foto pequena no topo e texto embaixo, 40% do papel vazio nos lados; foto e texto não
  compartilham linha de base nem centro. Foto e texto são PARCEIROS na mesma composição.
- **Hierarquia/ordem quebrada**: o botão tem que estar colado ao bloco de texto (24–40 px) e perto da foto. Ordem
  única: título → apoio → botão.
- **Mobile aprovado ≠ desktop**: o empilhado do mobile NÃO escala por esticamento; recompor no desktop.
Teste: olhar a dobra como um leigo ("onde meu olho vai primeiro, segundo, terceiro?") em 1024/1280/1440/1920. Passa no
verificador ≠ organizado.

### Hero "holofote" (receita de dobra aprovada)
Cenário de IA sem uma ideia gráfica não vira composição (faixa larga e chapada 3:1 = banner genérico). O que funciona:
**uma ideia gráfica forte e simples** — um disco na cor de destaque atrás das pessoas, que o rompem (cabeças e ombros
saem do disco), anel fino afastado, sobre o papel; abaixo, título, apoio, botão; tudo no mesmo eixo central.
1. Ordem: IMAGEM → TEXTO → BOTÃO, uma coluna, eixo central (simetria = alinhamento garantido).
2. O disco nasce do eixo da foto: diâmetro ≈ 48–56% da largura do grupo, terminando ATRÁS do tronco (o arco não
   aparece entre os braços), centro no eixo; gradiente radial (claro no alto), anel `box-shadow` em papel + tinta.
3. Foto real do grupo (centrada pela tinta), tamanho pela altura da janela: `width: min(100%, 940px,
   max(520px, (100svh − 465px) × 1.8))` → título e botão sempre na 1ª tela (1024×768 a 1920×1080).
4. Movimento: o disco abre do centro (escala .55→1 + opacidade, 0,9 s, uma vez) e as pessoas ficam por cima.
5. Base da foto: o fade do arquivo some no papel (sem faixa/chão).
Regra: uma composição aprovada vale para TODAS as larguras; só a escala muda. Testes de organização: "se eu tirar a
foto, o resto ainda é uma composição?" e "qual é a UMA ideia da tela?". IA gera só CENÁRIO/textura/forma.

### Rostos pequenos no celular
Dobra que não preenche a tela deixa ~1/3 vazio embaixo. Usar `.est-dobra` (tela inteira, conteúdo centrado), painéis
mais altos, título maior com `clamp`. Para aumentar rosto, refazer o recorte (mesma caixa, rosto maior, centrado pelo
ROSTO com YuNet, fade de 14% embaixo); nunca ampliar com CSS `scale` dentro da moldura (o queixo some atrás da faixa).

### Bateria completa de teste (`scripts/teste_pagina_total.py`)
Roda no Chrome com barra de rolagem real: 18 larguras (320–2560) + 4 paisagens de celular + emulação de celular;
rolagem horizontal, texto fora da tela/cortado, **blocos de texto sobrepostos**, margens esquerda × direita (a sombra
dura do botão conta), fonte < 14, alvo < 44, imagem quebrada/ampliada/sem alt, h1 único, linha > 90 caracteres,
**contraste WCAG**; pop-up inteiro (todos os CTAs, foco, Tab, ESC, fundo, envio vazio/inválido/válido, cabe na tela,
rolagem travada); foco visível; relógio nos 5 estados (`?agora=`); movimento total/suave/parado (animações, nada
invisível, CLS, LCP, tarefas longas, quadro p95, faixa anda). `--so layout,foco,popup,relogio,movimento` escolhe seções.
Rodar além do `check_pagina.py`; ambos precisam fechar com 0 erros.
Falsos positivos já resolvidos no teste (não "corrigir" a página por causa deles): conteúdo de `<details>` fechado,
elementos `fixed`/`sticky`, botão alinhado à esquerda numa coluna maior, LCP medido DEPOIS de rolar, Tab que sai do
`<dialog>` para o navegador (comportamento normal do modal nativo).
Defeitos típicos em 320 px: título/data/botão cortados; sombra do botão passando da margem.

### Verificar do jeito que o visitante vê (obrigatório, vira erro no `check_pagina.py`)
1. Chrome **com barra de rolagem clássica** (não headless que esconde) em janela estreita de desktop (vista `390-barra`).
2. Passagem com `reduced_motion="reduce"`: nada invisível, nada cortado, faixa legível.
3. Simetria esquerda × direita em toda caixa de coluna (imagem, cartão, botão, painel), 1,5 px de tolerância.
4. CSS com `100vw` em medida de layout = aviso (sangria `inset:0 -100vw` é inofensiva).
5. Olhar as imagens em 360, 390, 390-barra, 768, 1024 e 1440, seção por seção, antes de dizer que está pronto.

### Movimento premium (princípios)
- Movimento serve à leitura ou à marca: entra uma vez, curto (≤ 0,7 s), só `transform`/`opacity`; um efeito de
  destaque por tela; nunca no H1, na foto do LCP nem no CTA principal.
- Funciona SEM movimento: o estado natural do CSS é o final; no reduzido, só fades curtos de opacidade.
- Momentos "diferenciados" que o conteúdo pede (não enfeite): contagem que vira dígito a dígito, tarja que se
  abre/fecha como cortina, ingresso que se destaca ao passar o mouse, faixa de selos com velocidade ligada à rolagem,
  numeral que "imprime", cursor que acende o granulado, botão magnético (só ponteiro fino).
