# Técnicas avançadas — social, composição, sites e identidade

Técnicas medidas de estúdios e sites premiados que ainda não estavam nas outras references, cada uma com medida,
como fazer na stack do estúdio (HTML/CSS/GSAP no Chrome, Python/PIL, SVG) e erro comum. Grau de prova: P = fonte
primária · S = secundária · D = derivada nossa. Use na ideação para SUPERAR o repertório, nunca para copiar.

## Contents
- Técnicas (social e peças · composição · sites · identidade)
- Arquétipos novos (A1–A6)
- Aplicação imediata
- Fontes

## Técnicas
### Social e peças

**T1 · Carrossel panorâmico com ponte** [S]
- O que é: uma arte-mestra larga, cortada em n slides; UM objeto atravessa a emenda e puxa o dedo para o próximo.
- Medida: tela-mestra (1080·n) × 1350; emenda em x = 1080·k; nada de rosto, texto ou logo a ± 60 px da emenda;
  só o objeto-ponte cruza (1 por emenda, ≥ 25% dele de cada lado); 5–10 slides; o 1º slide se sustenta sozinho
  (é a capa na grade).
- Na nossa stack: `palco.py` monta a tela larga como uma página só (grade de n colunas de 1080) e o Python/PIL
  fatia; o verificador mede a faixa de ± 60 px em volta de cada emenda (só pixels do objeto-ponte).
- Erro comum: panorâmico para conteúdo de lista (quem salva quer 1 slide com 1 dica; o print corta a ideia).
- Exemplo: guias de carrossel contínuo (krumzi, blendnow — §5).

**T2 · Espiada (peek) do próximo slide** [S, D]
- O que é: 8–15% do próximo slide aparece na borda direita do slide 1 (o objeto-ponte de T1 ou um canto de cor).
- Medida: espiada 86–162 px na borda direita; nunca texto cortado; seta/"arraste" opcional e pequena (≤ 1 por série).
- Stack: parte do T1; num carrossel não panorâmico, desenhar só a espiada (forma da marca a 0–16 px da borda).
- Erro: espiada que parece arte vazada sem querer (D-erro de corte) — tem que ser forma inteira reconhecível.

**T3 · Formato 3:4 e a grade do perfil** [S]
- O que é: desde jan/2025 a grade do perfil é 3:4; o feed aceita 1080×1440 (mais 90 px de altura que o 4:5).
- Medida: 4:5 na grade perde ~34 px de cada lado (sobra x 34–1046); capa de Reels 9:16 na grade = y 240–1680
  (perde 240 em cima e embaixo); 3:4 nativo aparece inteiro. Agendadores pela API podem cortar 3:4 para 4:5.
- Stack: acrescentar 3:4 (1080×1440) às zonas de `interface.py` (texto até ~y 1296 = 90%, a medir na interface
  real antes de virar regra); capa de Reels exportada à parte em 1080×1440.
- Erro: título da capa do Reels acima de y 240 (some na grade).

**T4 · Série pensada em trincas (linha da grade)** [D]
- O que é: a grade tem 3 colunas e cada post novo empurra tudo uma casa; publicar em blocos de 3 faz a linha
  ler como um compasso (ex.: herói · prova · respiro).
- Medida: 1 linha = 3 papéis diferentes; vizinhas nunca com a mesma estrutura (já é regra); o respiro tem
  ≥ 60% de vazio; a trinca é julgada numa folha 3×3 a 25%.
- Stack: folha de contato 3:4 em 3 colunas no `palco.py` (simula o perfil) antes de aprovar a série.
- Erro: mosaico que só faz sentido junto (um post gigante fatiado em 3) — morre no feed, onde cada um aparece sozinho.

**T5 · Arte-mestra + janelas (sistema que não parece template)** [P, D]
- O que é: um único supergráfico grande da marca; cada peça é uma JANELA diferente dele (posição e escala), não
  um layout repetido. Parente da "stage" elástica da CW (DixonBaxi) e do fio da LDF 2025 (Pentagram).
- Medida: janelas em 3 escalas (1×, 2,5×, 6× do mestre); ≥ 30% da forma reconhecível em toda janela; o tipo e a
  margem não mudam (constantes da série).
- Stack: mestre em SVG 4000–8000 px; `palco.py` recebe `viewBox` por peça; sorteio por sha256 do conteúdo, nunca
  `hash()`; lint: CLIP ≤ 0,92 entre vizinhas.
- Erro: janela que só mostra textura sem forma (vira papel de parede, perde a marca).

**T6 · Quadro 0 = capa = fim do loop (Reels/Stories)** [D, S]
- O que é: o 1º quadro já é um pôster completo (título + rosto/objeto), porque é a capa, a prévia sem som e o que
  aparece em economia de dados; o último quadro devolve ao 1º para o replay não ter emenda.
- Medida: quadro 0 passa no portão de peça estática; loop 6–9 s; últimos 8–12 quadros (30 fps) convergem ao quadro 0.
- Stack: HyperFrames/GSAP com `timeline.to(...)` final igual ao estado inicial; `ffmpeg -ss 0 -frames:v 1` vira a capa.
- Erro: abrir com fade do preto (quadro 0 vazio = capa vazia).

### Composição

**T7 · Texto em trilho (a linha do sistema carrega a frase)** [D]
- O que é: a "linha de sistema" do kit (fio, picote, curva do objeto do assunto) vira o trilho de uma frase curta.
- Medida: ≤ 8 palavras; maiúscula ≥ 34 px; raio de curvatura ≥ 3× a altura da maiúscula; entreletra +2–4%;
  frase começa e termina a ≥ 1 U de qualquer borda; nunca o título principal.
- Stack: SVG `<textPath>` com o caminho do elemento; para master sem `<text>`, `common.Font` em curva ao longo do
  caminho (mesma rotina do texto em círculo do selo, generalizada para caminho).
- Erro: texto em curva apertada (letras se abrem em leque) ou em S com inversão (lê de cabeça para baixo).

**T8 · Plano tipográfico em perspectiva (tipo como chão ou parede)** [D]
- O que é: uma palavra gigante deitada num plano 3D, como pintura de quadra/pista; o resto da peça fica plano.
- Medida: `perspective` 900–1400 px; `rotateX` 50–65°; a linha mais próxima com maiúscula ≥ 34 px; o plano ocupa
  30–55% da altura; 1 por peça; a informação (data, CTA) sempre em plano frontal.
- Stack: CSS 3D no `palco.py` (Chrome), sombra de contato em camada separada; peça estática, sem custo de LCP.
- Erro: ler a informação no plano inclinado; perspectiva em 2 planos ao mesmo tempo.

### Sites

**T9 · Palco fixo de rolagem (scrollytelling com regra)** [P, S]
- O que é: um palco `position: sticky` muda UMA coisa por passo enquanto blocos de texto passam ao lado/embaixo.
- Medida: 3–5 passos; passo = 75–100 `svh`; gatilho no meio da tela (offset 0,5); 1 mudança por passo; linha de
  progresso de 1 px; celular: palco 50–60 `svh` em cima, texto embaixo; o conteúdo final existe sem animação.
- Stack: CSS `sticky` + `animation-timeline: view()` com `@supports`; sem suporte, IntersectionObserver de 1 KB
  (padrão Scrollama, sem escutar `scroll`).
- Erro: palco que muda 3 coisas por passo; passo curto (o visitante pula estados).
- Exemplo: Pudding (scrollytelling sticky).

**T10 · Eixo variável pela rolagem** [P, D]
- O que é: um H2 ganha peso/largura enquanto entra na tela (o tipo "se arma"), nome do movimento = o que ele conta.
- Medida: 1 eixo (no máx. 2), faixa útil `animation-range: entry 0% cover 40%`; peso final = peso do sistema (o
  estado natural do CSS é o final); 1 título por tela; nunca o H1 nem o LCP.
- Stack: `@keyframes` em `font-variation-settings` + `animation-timeline: view()`, `@supports` → peso final fixo;
  checar o eixo em wakamaifondue antes.
- Erro: animar parágrafo; fonte sem eixo real (o navegador sintetiza negrito).

**T11 · Molas em CSS com `linear()`** [P]
- O que é: curvas de mola/rebote sem JS (Chrome/Edge 113+, Firefox 112+, Safari 17.2+).
- Medida: só micro-interação tátil (aperto de botão, alternador, cartão que pousa); 350–600 ms; ultrapassagem
  ≤ 4%; 1 mola por componente; entrada de texto segue com a curva padrão do sistema.
- Stack: gerar no Linear Easing Generator (preset Spring, 30–40 pontos), guardar como token `--ease-mola`.
- Erro: mola em título/entrada de página (parece brinquedo).

**T12 · Transição entre páginas (View Transitions)** [P]
- O que é: o elemento comum (foto do cartão → hero da página do professor) viaja de uma página a outra.
- Medida: 250–400 ms; 1 elemento nomeado por navegação (`view-transition-name` único); entre páginas:
  `@view-transition { navigation: auto }` (Chrome/Edge 126+, Safari 18.2+; Firefox navega normal).
- Stack: no Next estático, `<Link>` é navegação do cliente → usar `document.startViewTransition` no roteador ou `<a>`
  comum para disparar a versão entre documentos; movimento reduzido = só dissolver 150 ms.
- Erro: nomear vários elementos (tudo voa); transição que atrasa o clique > 400 ms.

**T13 · Interface como ilustração (produto/prova em HTML)** [D, P]
- Completa o princípio "produto/prova em código": receita medida.
- Medida: 1 tela de produto, escala 0,82–0,9, 3 estados em ciclo de 2,4–3,2 s cada, 1 cursor-fantasma no máximo,
  texto real ≥ 12 px CSS, dados reais (com fonte); `aria-hidden` + frase equivalente em texto; pausa fora da tela.
- Stack: componente React com estados em CSS (`@starting-style`) e um `setInterval` parado por IntersectionObserver.
- Erro: print de tela (borra, pesa, não anima, não traduz); dado inventado como "prova".

**T14 · WebGL leve com degraus de qualidade** [S]
- O que é: o efeito escala pelo aparelho, e quem não aguenta recebe o pôster.
- Medida: DPR limitado a 1,5 (celular) / 2 (desktop); laço de rolagem ≤ 4 ms por quadro; 60 fps em aparelho médio;
  3 degraus por `hardwareConcurrency`/`deviceMemory` + 1 s de prova de fps; o pôster é o LCP.
- Stack: o shader de grão de ~1,3 KB já adotado + estes degraus; testar com CPU 4× mais lenta no DevTools.
- Erro: decidir a qualidade só pelo tamanho de tela.

### Identidade

**T15 · Logo responsivo por contêiner** [S, D]
- O que é: assinatura completa → compacta → símbolo, trocadas pela LARGURA DO ESPAÇO, não da tela.
- Medida: 3 estados no máximo; a troca acontece onde a escada de tamanhos do QC de logo reprova o estado maior;
  o símbolo nunca desce de 24 px.
- Stack: `@container (width < Npx)` alternando 3 `<svg>` (ou `<use>` de um sprite); manual com tabela "estado × largura".
- Erro: 5 estados (ninguém lembra) ou troca por breakpoint de tela (o cabeçalho estreito no desktop quebra).

**T16 · Eixo como dado (tipografia que responde a algo real)** [P]
- O que é: um eixo da fonte variável preso a UMA variável real do cliente (som na Sinfônica de SF/COLLINS; tempo no
  mostrador Flux da Apple, TDC71). Extensão de M20/M26: o valor vem do mundo, não de semente.
- Medida: 1 dado → 1 eixo, monotônico (mais = mais); legenda explicada 1 vez no manual; leitura garantida no pior valor.
- Stack: `tipos.py` acha a fonte com o eixo; `palco.py` recebe o dado por peça; site anima com `@property`.
- Erro: mapear dado sem sentido para o público (ninguém decodifica).

**T17 · Dispositivo multifunção** [P]
- O que é: um elemento da marca com 3 papéis declarados (moldura de conteúdo · navegação · lente/zoom), como o
  "stage" da CW (expande e contrai; vira claquete, navegação, lente).
- Medida: 3 papéis, cada um com 1 exemplo no manual; espessura e raio fixos em todos.
- Stack: componente único (SVG/CSS) com variantes `moldura|nav|lente`; vai ao `brand.json` como modelo.
- Erro: o dispositivo virar enfeite em todas as peças (papel sem função = sai).

## Arquétipos novos (A1–A6)

- **A1 Ponte panorâmica** · tela n×1080; objeto-ponte em cada emenda; slide 1 = capa autônoma; texto centrado por
  slide · leitura: capa → ponte → clímax no último · quando: história em etapas, antes/depois, lançamento.
- **A2 Trilho** · linha do kit atravessa 60–90% da peça; frase curta no trilho; título frontal no maior vazio ·
  leitura: título → trilho → assinatura · quando: manifesto curto, jornada, programa.
- **A3 Chão tipográfico** · palavra em plano 3D no terço de baixo (30–55% da altura); pessoa/objeto de pé sobre ela;
  info frontal em cima · leitura: figura → palavra → info · quando: evento esportivo, arena, palco.
- **A4 Palco fixo (dobra)** · palco sticky 60% da largura (desktop) / 50–60 svh (celular) + 3–5 passos de texto ·
  leitura: passo → palco muda → próximo · quando: método, "como funciona", programa do curso.
- **A5 Janela do mestre** · supergráfico recortado em escala 2,5–6×; tipo fixo no mesmo canto em toda a série ·
  leitura: forma → título · quando: série longa com pouca foto.
- **A6 Produto vivo** · tela de produto em HTML (0,82–0,9) ao lado do título, 3 estados em ciclo · leitura:
  título → estado que muda → botão · quando: curso/plataforma/ferramenta com algo para mostrar.

## Aplicação imediata
**Série de posts:** (1) trocar 1 post único por carrossel-ponte de 6 (A1) em que o objeto-ponte é o objeto do assunto
do kit; (2) montar a série em trincas e aprovar pela folha 3×3 do perfil (T4); (3) migrar posts de foto para 3:4
1080×1440 e exportar capa de Reels à parte (T3), com quadro 0 pôster (T6).

**Site de evento/curso:** (1) a seção "como funciona" vira palco fixo de 4 passos (A4), cada passo acende uma parte do
objeto-kit; (2) os títulos de seção "se armam" no eixo de peso ao entrar (T10), com o nome do movimento ligado ao tema;
(3) a página do professor herda a foto do cartão por View Transition (T12) e o botão usa a mola só no aperto (T11).

**Identidade:** (1) declarar um dispositivo multifunção (T17) no manual com os 3 papéis; (2) mapear 1 eixo variável a
1 dado real do cliente (T16: fase, tempo restante, intensidade) e mostrar a legenda; (3) entregar o logo responsivo
em 3 estados com tabela estado × largura e o snippet `@container` (T15).

## Fontes
- https://www.awwwards.com/sites/lando-norris — SOTD 17/11/2025 (8,18; animações 8,60) e selo SOTY 2025 (OFF+BRAND).
- https://designrush.com/best-designs/websites/lando-norris-website-design — hero com manchas que reagem ao cursor, paleta curta do capacete.
- https://80.lv/articles/deliver-mail-on-tiny-colorful-planet-in-this-relaxing-web-game — Messenger (abeto), WebGL/Three.js no navegador; selo SOTY 2025 visto em listagem, não conferido.
- https://www.hontran.dev/blog/best-award-winning-websites-2026 — casos SOTD (grade que quebra em momentos-chave, tipo cinético que não bloqueia leitura); autor = construtor (autodeclarado).
- https://digitalstrategyforce.com/journal/why-are-immersive-experiences-dominating-the-2026-awwwards/ — linha do tempo 0–1, degraus de qualidade, ≤ 4 ms/quadro (fonte secundária).
- https://pudding.cool/process/scrollytelling-sticky/ — `position: sticky` no lugar de JS para o palco.
- https://pudding.cool/process/introducing-scrollama/ — gatilho por IntersectionObserver, offset 0,5.
- https://developer.chrome.com/docs/web-platform/view-transitions/cross-document — `@view-transition`, Chrome 126 / Safari 18.2.
- https://developer.chrome.com/docs/css-ui/css-linear-easing-function — `linear()` para mola e rebote; suporte.
- https://developer.mozilla.org/en-US/docs/Web/CSS/animation-timeline/view — `view()` e `animation-range`.
- https://blog.fontlab.com/2026/02/03/animating-font-variation-settings/ — animar eixos sem travar.
- https://www.debugbear.com/blog/opacity-animation-poor-lcp — opacidade 0 adia o LCP (confirma regra já existente).
- https://www.krumzi.com/blog/seamless-instagram-carousel — carrossel contínuo: tela n×1080, emendas.
- https://www.blendnow.com/blog/hwo-to-create-seamless-instagram-carousel — montar a tela inteira antes de fatiar.
- https://www.inro.social/blog/instagram-post-size — grade 3:4 desde jan/2025, 1080×1440.
- https://socialk.it/de/blog/instagram-reel-covers-guide — capa de Reels perde 240 px em cima/embaixo na grade.
- https://www.creativereview.co.uk/dixonbaxi-rebrand-us-tv-network-the-cw/ — "stage" elástico com papéis de claquete/navegação/lente.
- https://www.pentagram.com/news/london-design-festival-2025-identity-by-domenic-lippa-and-team-2 — fio tipográfico como dispositivo, vermelho mantido.
- https://wearecollins.com/case-studies/san-francisco-symphony — fonte variável que reage ao som (TDC67 Best in Show).
- https://tdc.org/news/tdc71-best-of-discipline-winners-announced — TDC71 (2025): NYCFC (Gretel + Frere-Jones Type), Flux Watch Face em tipo cinético.
- https://gretelny.com/nycfc — tipo do clube a partir da sinalização antiga do metrô; sistema modular de assinaturas.
- https://rive.app/blog/spotify-used-rive-for-spotify-wrapped-2025 — Wrapped 2025: movimento prototipado com dado falso e depois ligado ao dado real (fonte do fornecedor).
- https://pentagram.com/work/london-design-festival-2025 — página do projeto.

Lacunas: lista oficial dos SOTY 2025 da Awwwards não abriu (404); medidas de interface do 3:4 no feed ainda a medir
com `interface.py`; It's Nice That/Brand New sem resumo do ano encontrado.
