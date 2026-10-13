# Site: página de captura, venda e evento (regras congeladas)

Origem entre parênteses = pesquisa de origem e seção: **10** elementos para sites · **12** composições (parte
de sites) · **13** elementos em código · **14** estudo de sites (D e D2) · apoio: **5** (página de captura) e **15**
(licenças de vídeo). Número sem fonte = "[ponto de partida]". Não repete `qualidade.md` (zonas de peça social),
`elementos.md` (mundos, fundos, grão) nem `tipografia.md` (pares de fonte): só aponta para eles.

## 1. Prioridade
Ordem de decisão, sempre: **experiência → leitura → usabilidade → conversão → enfeite**. Se um elemento atrapalha
qualquer um dos quatro primeiros, ele sai, por mais bonito que seja.
- **Ousar nos elementos, não na estrutura.** Complexidade e layout "estranho para o tipo de site" derrubam a primeira
  impressão em 17–50 ms; simples + familiar vence (10 §3.1). A página de venda mantém a ordem reconhecível; o estilo
  mora na tipografia, no recorte, na textura, no selo e no elemento do assunto.
- **Uma ideia, um material, uma assinatura** (10 §5.1): uma ideia visual tirada do assunto; um elemento que só esta
  marca tem, repetido em escalas diferentes; no máximo **2–3 estilos** combinados (ex.: tipo gigante + adesivo + grão).
- **Velocidade vende mais que enfeite:** 0,1 s mais rápido = +8,4% de conversão no varejo e +21,6% de avanço em
  captação (10 §3.8). Todo efeito tem que caber no orçamento da seção 7.
- **Celular primeiro:** desenhar em 390 (conferir em 320–414) e depois abrir para 1440 (10 topo; 5 §4.2).
- **Medir o que as referências não medem:** contraste no pior pixel, tamanho mínimo, alvo de toque, LCP (14 D n.º 14).
- **Base do cliente primeiro:** o que já funciona na página anterior (urgência verdadeira, selo, prova numérica,
  professores reais, CTA repetido, forma derivada da marca) se MANTÉM; o resto se supera (14 D2).

## 2. Estrutura da página
### 2.1 Ordem das seções (o estilo muda, a ordem não)
| Tipo | Ordem (cada número = 1 seção) |
|---|---|
| Captura de aula gratuita (4–6 seções) | 1 hero com formulário ou botão · 2 as aulas (data, hora, tema, professor) · 3 professores · 4 para quem é · 5 depoimentos/números · 6 FAQ curto + CTA final + rodapé (5 §4.1; 12 §3.5 regra 10) |
| Curso, pós, mentoria (8–12) | 1 hero · 2 logos ou números · 3 problema → promessa · 4 para quem é · 5 método ou vídeo · 6 módulos · 7 professor · 8 depoimentos (1 gigante + parede) · 9 bônus · 10 preço + garantia colada · 11 FAQ · 12 CTA final + rodapé (12 §3.3) |
| Evento (8–12) | 1 hero com data, local e botão · 2 números da edição anterior · 3 por que ir · 4 palestrantes · 5 agenda · 6 vídeo + depoimentos · 7 ingressos/lotes + reembolso · 8 local · 9 patrocinadores em grupos · 10 FAQ · 11 CTA final · 12 rodapé (12 §3.3) |
| Página de obrigado | 1 passo gigante ("Entrar no grupo do WhatsApp") + "passo 1 de 2" + adicionar à agenda; nada competindo (5 §4.1; 10 §4.1 n.º 4) |

- **Teste dos títulos:** só pelos títulos das seções, dá para saber o que é vendido e para quem. **Prova social cedo e
  de novo perto do preço** (os dois picos de dúvida). A seção 2 nunca é "sobre nós" (12 §3.3, §3.5 regra 9).

### 2.2 Primeira tela
- Responde **o quê, quando e com quem** (+ preço ou "gratuito"), em texto HTML, nunca dentro da imagem (5 §4.7; 14 D2
  n.º 9). 74% do tempo de leitura fica nas duas primeiras telas: a ação principal mora ali (12 §3.5).
- **Hero com 85–92 svh** e **8–15% da seção seguinte aparecendo** (ou cartões que atravessam a borda, H17). Hero de tela
  cheia vira "fundo falso": 6 de 8 pessoas não rolaram (12 §3.5). Usar `svh`, nunca `vh`, no celular (12 §3.1).
- No celular, título + subtítulo + botão terminam em **y ≤ 600 px CSS** (360×800 e 1366×768) (5 §4.2, `qualidade.md`).
- Nada de fio horizontal cheio nem faixa branca enorme exatamente na dobra (parece fim de página) (12 §3.5 regra 7).

### 2.3 Uma ação principal
- **1 CTA primário** com o mesmo texto e o mesmo estilo na página toda, repetido em ≥ 3 pontos (hero, depois da prova,
  oferta/fim) (10 §4.1 n.º 1). Benchmark: 1 CTA converteu 13,5% × 11,9% com 2 × 10,5% com 3 (12 §3.5).
- Botão **cheio**, com forma de botão e cor reservada só para a ação: o vazado perdeu 20% dos cliques (10 §3.2).
  Altura ≥ 48 px (ideal 56), 100% da coluna no celular (5 §5.b). Estados: hover, foco, ativo, "Enviando…" (10 O12).
- **1 primário por tela**; o secundário vira link de texto, nunca um 2º botão do mesmo peso (14 D2 n.º 3).
- **CTA fixo no celular** (opcional; testes opostos, +6,2% × −7,7%, 10 §3.8): aparece quando o botão do hero sai da
  vista, some com o formulário na tela; 64–72 px + `safe-area` e `scroll-padding-bottom` igual (WCAG 2.4.11) (5 §4.2).

### 2.4 Formulário
- Captura gratuita: **2–3 campos** (nome, WhatsApp, e-mail opcional) e **1 formulário só** por página, nunca um por
  cartão (5 §4.4; 14 D2 n.º 2: 5 formulários = 15 campos e 10 botões na mesma tela).
- **Rótulo visível ACIMA do campo**, sempre. Placeholder nunca é rótulo; rótulo flutuante também não (pequeno, apagado,
  sem lugar para o erro) (5 §4.4; 10 M11; 14 D2 n.º 4).
- `tel` + `inputmode="numeric"` + `autocomplete="tel-national"`, máscara de 11 dígitos `(DD) 9XXXX-XXXX`; `name`;
  `email`; campo com fonte ≥ 16 px (senão o iPhone dá zoom) (5 §4.3, §4.4).
- Validação **ao sair do campo**, ✓ quando válido, erro ligado ao campo (`aria-describedby`), nunca só em vermelho
  (10 M11). LGPD: caixa de mensagens **desmarcada**, finalidade escrita, link de privacidade junto do botão (5 §4.4).

### 2.5 Prova, preço e garantia
- **Prova perto do CTA:** no hero (foto real do professor, número real com unidade e origem) e colada na oferta;
  número pequeno sai pela culatra (12 §3.3; 5 §4.1; 10 T14, §3.7).
- Depoimento = rosto + nome + cidade/profissão + **resultado concreto** + data, mesma moldura para todos; autorização
  escrita (print de WhatsApp sem autorização gera indenização, STJ) (10 E12, §4.1 n.º 6).
- Preço em texto: **parcela em destaque, à vista ao lado**, "de" riscado discreto e verdadeiro; 1 número dominante
  (12 S13; 10 E15). Garantia (selo 96–140 px + frase clara) colada no preço e no botão (12 S14).

### 2.6 Contador: só com prazo real
- ~40% dos contadores em 11 mil lojas eram falsos; o genérico não mudou a conversão (14,3% × 14,8%); urgência só
  ajudou perto de um prazo **verdadeiro** (10 §3.6).
- Estados reais, pelo relógio do servidor, no fuso escrito: **faltam X dias → hoje, 20h30 → ● ao vivo agora →
  encerrado** (+ replay ou lista de espera). "Faltam 00 dias" com "já começou" mata a confiança (14 D2 n.º 1; 12 H09).
- Nunca reinicia por visitante nem ao recarregar; data e hora também em texto; `tabular-nums` (10 §3.6, T14). Mudando
  a cada segundo por mais de 5 s: botão de pausa, ou atualizar por minuto [proposta] (WCAG 2.2.2; 5 §4.6).

### 2.7 Lei (Brasil) — leitura nossa, não é parecer jurídico
- **Desconto sobre o menor preço dos últimos 60 dias** (recomendação Procon-SP 2025); "Black Fraude" = % sem preço
  final, sem preço anterior ou desconto maquiado (10 §3.6, §4.1 n.º 15).
- Preço total, condições e restrições "claras e ostensivas" perto do preço (Decreto 7.962/2013 art. 2º); parcelado
  mostra à vista, parcelas, juros e total (CONAR Súmula 7); CNPJ e endereço visíveis no rodapé (10 §3.6, E19).
- A oferta obriga (CDC art. 30): checkout = página. Arrependimento de 7 dias (CDC art. 49). Contador, vagas e "ao vivo"
  falsos = publicidade enganosa (CDC arts. 37 e 39) (10 §3.6, §4.1).
- "Antes/depois" de corpo e promessa de resultado: risco CONAR/CDC e Meta (10 I11). Resto: `qualidade.md` § Lei.

## 3. Catálogo de heros e seções
Esquemas em 12 §3.1–3.2. Quase todo hero bom é **split ou centrado + UMA variação** derivada do assunto (12 §3.1).
Desktop = janela 1440, conteúdo ~1200; celular = 390. Seção vizinha nunca repete o código (12 §5.2).

### 3.1 Heros (H)
| Código | Quando usar | Desktop 1440 | Celular 390 |
|---|---|---|---|
| H01 split 50/50 | mensagem e foto com o mesmo peso; o mais seguro | 6+6 col; título ≤ 30 car., texto ≤ 25 palavras | pilha: título → botão → imagem 4:3 |
| H02 split 5/7 sangrando | foto forte do assunto, texto curto | texto 5 col; imagem 7 col até a borda | imagem 16:10 sangrando em cima |
| H03 centrado + mídia | produto/aula a mostrar logo abaixo | título ≤ 20ch; mídia começa a 70–80% da altura | título 3–5 linhas; mídia cortada embaixo |
| H04 tipo gigante | nome curto (1–2 palavras) é a ideia | palavra de margem a margem medida na tinta | quebra manual; data e local legíveis |
| H05 pessoa saindo do quadro | o professor é a prova (curso, mentoria) | pessoa 105–120% da caixa; ≤ 2 formas; ≤ 2 bordas | pessoa acima, botão abaixo do recorte |
| H06 vídeo de fundo | evento com filmagem real e boa | 80–90 svh; gradiente até 4,5:1; botão de pausa | vídeo 4:5 ou pôster; pausa visível |
| H07 bento-hero | oferta com peças de naturezas diferentes | célula 2×2 da mensagem + 4–6 células | mensagem primeiro, células 2 por linha |
| H08 colagem/objetos | lançamento "com cara de gente", comunidade | 5–9 objetos; zona limpa = título + 24–48 px | 3–4 objetos, só acima e abaixo do título |
| H09 contador/data | live ou evento com prazo real | título + data/local + dígitos 0,6–1× o título | data em texto + dígitos `tabular-nums` |
| H10 print real | plataforma/área de membros real | print 55–75% da largura, passa da dobra | recortar 1 detalhe do print, não encolher |
| H11 editorial | conteúdo de autor/revista de verdade | título serifado 3 linhas + foto que passa da coluna | foto 4:5 em cima, título, linha fina |
| H12 letreiro | evento com muitos nomes/fotos | 1–2 faixas a 30–60 px/s, pausa | 1 faixa; data nunca só dentro da faixa |
| H13 grade de rostos | evento com palestrantes | 6–12 rostos, olhos na mesma altura | carrossel com o último cortado ou 2×2 + "ver todos" |
| H14 palco preso (sticky) | método em etapas, só se houver imagem que muda | palco preso 200–400 vh; 3–5 paradas | lista simples com palco de 60 svh |
| H15 com formulário | captura gratuita | texto à esquerda, formulário à direita | formulário acima da dobra (foto não empurra) |
| H16 mínimo | marca forte, teaser | frase ≤ 10–12 palavras; 60–75 svh | dica de rolagem obrigatória (fundo falso) |
| H17 padrão + cartões na borda | marca com elemento-assinatura | cartões invadem 64–120 px a seção seguinte | 1 cartão atravessando |
| H18 régua de prova | prova forte (logos ou números) | régua de 72–120 px colada no hero; 5–8 logos | logos em 2 linhas + 2 números |

### 3.2 Seções (S)
| Código | Quando usar | Desktop 1440 | Celular 390 |
|---|---|---|---|
| S01 bento | entrega de naturezas diferentes | ≤ 9 células; líder ≈ metade; gap 16–24 = raio | 1 coluna na ordem de prioridade |
| S02 lista com ícones | 3, 4, 6 ou 8 benefícios parecidos | 3–4 col; título ≤ 5 palavras, texto ≤ 20 | ícone à esquerda, 1 coluna |
| S03 zig-zag | 2–3 blocos com imagem informativa | texto 5/12, imagem 6/12; ≤ 3 linhas | sempre a mesma ordem (título → imagem) |
| S04 agenda | evento, turma com datas | hora em coluna fixa 80–100 px; 5–8 itens/dia; fuso escrito | cartões por item; abas por dia |
| S05 depoimentos | prova; escolher carrossel, parede ou gigante | carrossel ≤ 5 sem avanço; parede 6–9; gigante 36–48 px | 1 cartão + 15% do próximo; gigante 26–30 px |
| S06 faixa de logos | onde os alunos trabalham, imprensa | 5–8 logos de 1 cor, mesma área óptica, legenda da relação | 3 por linha |
| S07 números | prova numérica verificável | 3–4 números 56–96 px + linha de fonte e data | 2×2 |
| S08 professor | autoridade real | foto 4:5 em 40–50% olhando para o texto; 3–5 credenciais | foto largura total, bio curta + "ler mais" |
| S09 palestrantes | evento | 4–6 col; 8–12 visíveis; mesmo tratamento de foto | 2 col, 6 visíveis + "ver todos" |
| S10 módulos | conteúdo do curso | ≤ 6 → cartões; 7–15 → acordeão com o 1º aberto; totais no topo | acordeão |
| S11 para quem é | filtrar o público | 2 colunas: é (4–6 ✓) / não é (3–4 ×, fundo neutro) | empilhado |
| S12 comparação | sem × com o método | tabela 5–9 linhas, células curtas | 1 critério por bloco, 2 colunas |
| S13 oferta | preço | card único ou 3 planos alinhados pela linha do preço; destaque 4–8% maior | card recomendado primeiro |
| S14 garantia | logo depois do preço | selo 96–140 px + texto ≤ 40 palavras | selo em cima, texto embaixo |
| S15 FAQ | objeções reais | 6–10 perguntas em 1 coluna (720–800 px) | 1 coluna; > 10 → grupos por tema |
| S16 CTA final | fechamento | bloco de cor 50–70% da tela; promessa + oferta + 1 botão | botão 100% |
| S17 bônus | pilha de valor | lista com valores só se comprováveis | valores à direita, total + botão |
| S18 vídeo | mostrar uma aula | pôster representativo + duração perto do play; sem autoplay | pôster 16:9 + legenda + transcrição |
| S19 rodapé | links legais | enxuto em página de venda; CNPJ, termos, privacidade | 2 col + linha legal |

**Muitos itens** (12 §3.4): 12+ módulos → fases com acordeão; 20+ palestrantes → 8–12 + "ver todos (42)"; 30+
depoimentos → 1 gigante + 6–9 + link externo; 40+ logos → grupos rotulados de ≤ 15; FAQ longo → 6 na página.

## 4. Ritmo e grid
| Item | Regra |
|---|---|
| 1440 (tablet: 8 col) | 12 colunas; container 1200 (margem 120) até 1320 (= `elementos.md`); gutter 24 → coluna 78 (12 §1.8) |
| 390 | 4 colunas, margem 20–24, gutter 16 → coluna ≈ 74 [ponto de partida, 12 §1.8]; nunca < 16 de margem |
| Escala de espaço | 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 128 (5 §5.b); todo espaço sai daqui |
| Entre seções (desktop / celular) | cada seção recebe UM: **P 56/40 · M 96/64 · G 128/80 · GG 160/96** (GG só em imagem ou pausa), em `clamp()` entre 390 e 1440 (12 §3.5 regra 1) |
| Dentro da seção | ≤ **0,5×** o espaço entre seções; dentro do grupo ≤ 0,5× entre grupos (12 §3.5 regra 2, C22) |
| Linha de texto | corrido `max-width` 60–66ch (limite 75); colunas 40–50ch; títulos 12–22ch com `text-wrap: balance` (12 §3.5 regra 8) |
| Raios / fios / sombras | ≤ 3 raios, ≤ 2 espessuras de fio, 3 elevações, 1 estilo de cartão (12 C20; 10 §5.2) |

**Ritmo (vizinhas nunca iguais):**
1. Alternar 3 eixos: **claro/escuro**, **denso/vazio**, **largo/estreito**; vizinhas nunca iguais nos três (10 §5.3).
2. **Nunca 3 seções cheias seguidas** (grade, lista, preço); depois de uma cheia vem uma que respira (12 §3.5 regra 3).
3. **Nunca 2 escuras seguidas** (salvo se uma é só imagem); no máximo 3 tons de fundo na página (12 §3.5 regra 5).
4. **Seção de respiro** a cada 3–4 seções: uma frase grande ou um número, muito espaço (10 §5.3).
5. **Zig-zag ≤ 3 linhas**; para continuar, trocar de código (12 §3.5 regra 6).
6. **Trilho fixo, palco variável:** escala, módulo de texto, cor de ação e grade fixos; a seção troca o palco (12 §5.2).
7. **Quebrar UMA coisa por seção, contra uma grade visível**; às vezes 1 elemento atravessa a divisa (12 §1.9; 10 §5.3).

**Orçamento por seção (1 tela de celular)** (10 §5.2, [ponto de partida]): 1 herói · ≤ 2 ornamentos · 1 cor de destaque
+ 1 de apoio · 2 famílias (+ mono) · 1 movimento acontecendo · 1 botão principal · 1 título + 1 subtítulo + ≤ 3 itens.

## 5. Tipografia de site (pares, vozes e vetos: `tipografia.md`)

| Item | Regra |
|---|---|
| Corpo | 16–18 px no celular · 18–20 no desktop · entrelinha 1,5; **campos ≥ 16 px** (5 §5.b, §4.3) |
| Título H1 | 32–40 px no celular · 48–64 no desktop · entrelinha 1,05–1,15, acentos medidos (5 §5.b) |
| Hero tipográfico | até `clamp(44px, 5vw + 1rem, 96px)`, `max-width` 20ch (12 H03); tipo gigante ≈ `clamp(72px, 17vw, 320px)`, entrelinha 0,82–0,9, tracking −0,02 a −0,04 em, encostado nas margens **na tinta**, contêiner com `overflow-x: clip` (12 H04; 10 T1) |
| Mínimo | nada que precise ser lido < 16 px; rótulo, legenda e nome ≥ 14 px; < 14 só rótulo de ≤ 4 palavras em caixa-alta espaçada [ponto de partida, 12 S06/S07/H13; 10 T10]. 8–13 px em cinza = defeito medido nas referências (14 A, B) |
| Escala | ≤ 6 tamanhos por página; razão ≥ 1,25 entre níveis vizinhos; fluida com `clamp()` entre 390 e 1440 (12 C4, C5, §3.5) |
| Famílias | ≤ 2 (+ mono do mesmo sistema); display com caráter só em textos de ≤ 6 palavras, fonte muito legível no resto (ou 1 família larga só) (12 C6; 14 D n.º 1, B n.º 2) |
| Pesos | ≤ 3 pesos por família na página; corpo 400–500; nunca peso fino (< 400) em texto pequeno, sobre foto ou em contorno [ponto de partida; 10 T3, 14 A] |
| Contraste | **4,5:1** (3:1 só ≥ 24 px, ou ≥ 18,5 px em negrito), medido no **pior pixel** atrás (foto, grão, degradê); borda de campo, ícone e anel de foco 3:1; nada de cinza claro "elegante" (10 §3.8; 5 §4.6) |
| Na tinta | `text-box: trim-both cap alphabetic` em títulos, rótulos e botões: a caixa vai da maiúscula à linha de base, e o espaço medido é o real (13 §2.6) |
| Quebra | `text-wrap: balance` nos títulos, `pretty` nos parágrafos; zero palavra sozinha na última linha do título a 360 px (10 A11) |
| Números | `font-variant-numeric: tabular-nums` em preço, data, hora, contador e prova (10 T14; 12 H09). Fonte com zero cortado ou I/l/1 iguais nunca em hora, preço ou cupom (14 F) |
| Contorno, girado | texto que precisa ser lido nunca só em contorno (`paint-order: stroke fill` no eco); texto girado/vertical some ou desvira abaixo de 768 px (10 T3, T15) |
| Robustez | o layout aguenta espaçamento WCAG 1.4.12 (entrelinha 1,5, parágrafo 2×, letras +0,12 em, palavras +0,16 em), zoom de 200% e 320 px sem rolagem lateral (5 §4.3, §4.6) |

## 6. Elementos: premium × cafona (2–3 estilos por página, origem explicável; catálogo: 10 §2)

| Elemento | Premium (pode) | Cafona / "cara de IA" (não) | Por quê |
|---|---|---|---|
| Ornamento | derivado do assunto ou da marca (forma do símbolo, transmissão, ficha) | neon de "pista", planeta, partículas, blobs 3D, bolhas | decoração genérica não diz nada (14 D2 n.º 7; 10 F15) |
| "Kit IA" | escolhas próprias | Inter sem escolha + degradê índigo→roxo + 3 cartões iguais + brilho atrás do título centrado + botão em degradê | é o que todo gerador médio faz (10 §1.2) |
| Cor | 1 acento com função, < 5% da área; 2–3 fundos do MESMO sistema | 5 cores competindo; cada bloco de uma cor; amarelo × ciano | cor sem função apaga a ação (14 D n.º 2, D2 n.º 6; 10 §1.1) |
| Título | 1–3 palavras ajustadas à largura; troca de estilo só na palavra-promessa | frase longa gigante em 6 linhas; Instrument Serif itálica numa palavra de todo título | o clichê novo de site feito por IA (10 T1, T11) |
| Selo / starburst | 1 por página, geometria da marca, texto real, parado ou girando devagar com pausa | 3 starbursts amarelos, vermelho piscando, "100% GARANTIDO" com louros | o que parece anúncio é pulado (10 O2, O15, §3.7) |
| Marcação à mão, seta | 1 por seção, mesma "caneta" no site todo | 4 marcações por tela; seta vermelha de infoproduto em toda seção | perde a ênfase (10 T8, O4) |
| Textura analógica | adesivo, fita, colagem, papel, grão único e baixo: 1–3 por tela, sem cobrir rosto ou texto | emoji; grão grosso sobre o texto; adesivo de banco | é o antídoto atual contra a "cara de IA" (10 §0 n.º 14, O3, F1) |
| Cartões | bento com hierarquia (1 líder, conteúdos diferentes), mesmo respiro | 3 cartões arredondados iguais; 9 caixas de ícone + frase genérica | sem hierarquia não há entrada (10 E1) |
| Foto | pessoa real (professor, aluno, aula), recorte limpo, 1 tratamento no site | foto de banco, "Corporate Memphis", recorte com halo, mockup com tela inventada | foto genérica é ignorada; real é estudada (10 §3.2, I2, I7) |
| Sombra, profundidade | 3 elevações com luz única; sombra dura só em clicável/ativo; logo desfocado em profundidade | `0 0 20px #000`; sombra dura em tudo; neumorfismo (botão some) | sombra marca o que se clica (10 A3, §1.2; 14 A, C) |
| Vidro, brilho | vidro em 1–2 elementos, opaco ≥ 80%; luz com motivo (holofote) | cartões de vidro sobre roxo borrado; aurora roxa; glow e grade em toda seção | leitura e "template de SaaS" (10 A5, F3; 14 C) |
| Faixa rolante | 1 por página, informação real, lenta (30–60 px/s), com pausa | 4 faixas; duas cruzadas inclinadas; a data só dentro da faixa | movimento contínuo exige pausa (10 E7; 12 H12) |
| Ícones | 1 família no peso da fonte, ou desenhados do DNA do logo | traço fino genérico, famílias misturadas, emoji, 3D de banco | "ícone genérico" está na lista de IA (10 O10) |
| Rótulo, divisória | rótulo mono com informação real no mesmo lugar; 1 espessura de fio | colchetes e "//" em tudo; onda SVG de gerador em toda divisa | "cara de dev" e de template (10 T10, O9, F12) |
| Prova | depoimentos na mesma moldura; números com fonte | mural de prints tortos; número inventado; "valor R$ 12.997" | prova falsa é ilegal (10 E12, E15) |

## 7. Desempenho = conversão
**Metas** (celular, percentil 75): **LCP ≤ 2,5 s · INP ≤ 200 ms · CLS ≤ 0,1**; LCP 31% melhor = +8% de vendas (10 §3.8).
- **Elemento LCP nunca começa invisível:** nada de fade-in, `opacity: 0` ou carregador no hero (opacidade 0 não conta
  como LCP); no máximo um deslocamento ≤ 300 ms com texto visível e botão clicável (10 §2, M10, M12).
- **Imagem:** hero sem `loading="lazy"`, com `fetchpriority="high"` (máx. 1–2), pré-carregada se vier do CSS; `width`/
  `height` (ou `aspect-ratio`) em TODA imagem e vídeo; AVIF/WebP + `srcset`; `<picture>` com recorte por tela (alto no
  celular, largo no desktop); hero ≤ **150 KB** no celular e ≤ **250 KB** no desktop (5 §4.5, §4.7; 10 A17).
- **Fontes:** ≤ 2 famílias em WOFF2 com subconjunto latino; `font-display: swap` [ponto de partida] + `size-adjust` na
  reserva para o texto não pular; variável só se usar ≥ 2 pesos (pesa menos que 4 arquivos) (5 §4.5; 10 T1, T7).
- **JS de enfeite ≤ 30–50 kB gzip no total** (GSAP sozinho = 27 kB); bibliotecas pesadas (GSAP, three.js) só por
  `import()` quando a seção aparece; scripts de terceiros (pixel da Meta) com `defer` (10 §5.2; 13 §5.2; 5 §4.5).
- **Vídeo no hero:** só mudo e `playsinline`; o **pôster é o LCP** (AVIF, bonito, legível sozinho); `preload="metadata"`;
  versão menor no celular; loop de 6–15 s; pausa fora da tela; **botão de pausa visível** (passa de 5 s → WCAG 2.2.2);
  com `prefers-reduced-motion`, só o pôster (10 F10; 12 H06). No único teste achado, a foto venceu o vídeo (10 §3.5).
- **Fundo vivo (shader):** imagem estática por baixo (o shader congelado), DPR 1, 30 fps, pausa fora da tela (13 §3.4).
  **Grão:** PNG de 128–256 px em mosaico, nunca sobre o texto nem `feTurbulence` animado (10 F1). **Vidro** pesa: 1–2
  elementos com reserva opaca (10 A5). Reservar a altura de barras fixas, contador e embeds (10 E16).

## 8. Movimento
**Pode** (curto, com propósito, desligável — 10 §3.3):
- Durações 100–500 ms (resposta ~100; mudança grande 200–300); 3 por página (~150 · ~300 · ~500) e 1–2 curvas (10 §5.5).
- No máximo **3 tipos por página**: 1 entrada padrão para blocos-chave (sobe 16–24 px, 400–600 ms, uma vez, conteúdo
  visível sem JS), 1 movimento-assinatura, microinterações de 150–250 ms também no `:focus-visible` (10 §5.2, M1, M13).
- **1 efeito acontecendo por tela** e **1 loop visível por vez** (10 §5.2). Movimento que explica: cronograma que se
  preenche até "hoje", frase-chave que acende, número que conta 1–1,5 s uma vez com o valor final no HTML (10 M2, M7).
- Só `transform`/`opacity`, nunca `top/left/width/height`, `box-shadow` ou `blur` grande (13 §5.2). Ponto "ao vivo" a
  ~1 Hz; nunca mais de 3 piscadas por segundo (`elementos.md`; 5 §4.6).

**Não pode:** scrolljacking (1ª tela e texto); rolagem horizontal presa no celular (vira pilha); parallax forte (≤ 10–15%
da altura; objetos ≤ 8–16 px); carregador de abertura; carrossel que avança sozinho; letra por letra em parágrafo;
cada bloco entrando de um lado; cursor que esconde o nativo; informação só com mouse (hover, holofote, tilt,
magnético); distorção WebGL em página de venda; Lenis no celular (10 §1.2, §2.6, I4, E3; 12 H08).
- **Tudo que se move sozinho por mais de 5 s** (marquee, selo ou borda girando, ponto pulsando, vídeo, contador por
  segundo) tem **botão de pausa visível**; "pausar só enquanto tem foco" não vale (WCAG 2.2.2, nível A) (13 §5.2).
- **`prefers-reduced-motion`** em todo efeito; reduzido ≠ nada: deslizamento vira fade curto e o loop para (13 §5.2).

| Ferramenta | Licença | Uso no estúdio |
|---|---|---|
| CSS puro (`animation-timeline`, `@starting-style`, `sibling-index()`, View Transitions) | — | **primeira escolha** (13 §2.7) |
| Motion (motion.dev) · anime.js v4 | MIT | animação JS leve (13 §5.1) |
| GSAP + plugins (SplitText, ScrollTrigger) | grátis, **não é open source** (licença Webflow): ok em site de cliente; proibido dentro de construtor visual nosso; rever a licença antes de cada site | linha do tempo e texto dividido, sob demanda (13 §5.1) |
| Lenis | MIT; respeita reduced-motion | só desktop, sutil (10 M3; 13 §5.1) |
| dotLottie (player `dotlottie-web`) | MIT | ícone, selo ou logo animado leve no site (15 §5.d) |
| HyperFrames | Apache 2.0, grátis em qualquer escala | vídeo/loop em código (MP4), não no site (15) |
| Paper Shaders · OGL · three.js | Apache-2.0 · Unlicense · MIT | fundo vivo (com reserva estática); 3D só pontual (13 §3.3) |
| Rough Notation · CountUp · NumberFlow · Splitting | MIT | marcação à mão, contador, texto dividido (10 T6, T8, M7) |
| **Remotion** | **NÃO**: grátis só até 3 funcionários | — (15) |
| **Não usar** | "Stripe gradient"/MiniGL (sem licença), Typed.js (GPL), Trianglify (GPLv3), LYGIA (não comercial), Vanta (cara de template), Remix Icon como marca; demo antiga da Codrops sem conferir o LICENSE (as novas são MIT) | (10 §0 n.º 15, §2.5; 13 §8.4) |

## 9. CSS moderno com fallback (site: Baseline + `@supports`; peça estática no Chrome: pode tudo — 13 §2)

| Recurso | Situação (10/2026) | Usar para | Fallback |
|---|---|---|---|
| `text-box: trim-both cap alphabetic` | Baseline 2026 | caixa do texto = maiúscula até a linha de base → alinhar e espaçar na tinta | sem ele, só sobra o espaço da fonte (aceitável) (13 §2.6) |
| `clip-path: shape()` | Baseline 02/2026 | recorte responsivo (%, rem, `calc()`): divisa de seção, foto em forma da marca | `polygon()` (13 §2.2) |
| `corner-shape` (squircle, bevel, scoop, notch) | só Chrome 139+ | canto de marca em selo/etiqueta/cartão | `@supports` → `border-radius` comum; chanfro com `clip-path` + `drop-shadow` (13 §2.2; 10 O13) |
| `sibling-index()` | Baseline 08/2026 | cascata sem JS: `transition-delay: calc(sibling-index() * 60ms)` | sem atraso (13 §2.7) |
| `animation-timeline: scroll()/view()` | Chrome e Safari; Firefox não | revelar, preencher, encolher ao rolar | `@supports` → estático (o conteúdo já está lá) (13 §2.1) |
| `text-wrap: balance` / `pretty` | balance Baseline; pretty sem Firefox | títulos sem palavra sozinha / parágrafo sem órfã | quebra normal (13 §2.1) |
| `background-clip: text` | escrever também `-webkit-` | foto/textura dentro da letra | cor sólida via `@supports` (10 T5) |
| `@starting-style`, `<details name>` + `::details-content`, `@property`, gradiente `in oklch` | Baseline / amplos | entrada sem JS; FAQ "um aberto por vez"; animar ângulo; degradê sem meio barrento | abre sem animação (10 E11; 13 §2.5) |

- **Filtros SVG:** `color-interpolation-filters="sRGB"` em todo `<filter>` que mexe em cor, limiar, deslocamento ou
  mapa (o padrão `linearRGB` desloca os tons); `linearRGB` só em desfoque e brilho; ampliar a região (padrão +10%) em
  sombra longa e deslocamento; no site, rasterizar o resultado (WebP/AVIF) em vez de filtro ao vivo (13 §1.0).
- `mix-blend-mode` sempre num grupo com `isolation: isolate` e no HTML, não dentro do SVG (Safari); ancestral com
  `opacity`/`filter`/`mask` corta o `backdrop-filter`; título vazado grande vai em curvas (13 §2.3, §2.4, §2.6).

## 10. Checklist do verificador (`../criacao-de-sites/scripts/site.py`)
Playwright (Chrome) em **320 · 360 · 390 · 768 · 1440** (+ 1366×768), celular com CPU 4× e 4G simulados; a página marca
`data-papel="h1|sub|cta|preco|data|form|hero|secao|ornamento|logo"`. **P** = portão (reprova); **A** = aviso (decidir e
justificar). "Amador X" = erro n.º X de 10 §5.6; o n.º 21 (foto de banco, mockup inventado) fica para o olho.

| # | Checa | Como medir | Limite | Tipo / origem |
|---|---|---|---|---|
| 1 | Rolagem lateral | `scrollWidth > clientWidth` do `<html>` | qualquer px | P · amador 2; 5 P2 |
| 2 | 1ª tela responde | `getBoundingClientRect().bottom` de h1 + sub + cta | > 600 px em 360×800 e 1366×768 | P · 5 P1 |
| 3 | Fundo falso | altura do hero ÷ `innerHeight`; topo da seção 2 | hero fora de 0,85–0,92 sem cartões na borda; fio cheio ou branco > 120 px na dobra | A · 12 §3.5 |
| 4 | LCP invisível | elemento do `largest-contentful-paint` + `getComputedStyle().opacity` no 1º quadro + `getAnimations()` nele; elemento fixo cobrindo a tela no carregamento | opacidade < 1, animação de opacidade ou carregador | P · amador 4; 10 M10 |
| 5 | Vitals de laboratório | `PerformanceObserver` (LCP, layout-shift) + TBT | LCP > 2,5 s · CLS > 0,1 · TBT > 200 ms | P · amador 3; 5 P9 |
| 6 | Imagem e vídeo | atributos de `<img>`/`<video>`; rede | sem `width/height` ou `aspect-ratio`; hero com `lazy` ou sem `fetchpriority`; hero > 150 KB (celular) / 250 KB; `autoplay` sem `muted`, `playsinline` ou `poster` | P · amador 3, 26; 5 P10; 10 F10 |
| 7 | Peso e fontes | rede (bytes gzip por script de efeito); `document.fonts` + `fonts.check()` de cada fonte declarada | JS de enfeite > 50 kB; > 2 famílias (+ mono); fonte caiu na reserva | P · amador 26; 13 §6.1 |
| 8 | Contraste real | captura com × sem o texto (`color: transparent`); percentil 5 dos pixels da letra × fundo | < 4,5:1 (< 3:1 em ≥ 24 px ou ≥ 18,5 negrito); borda de campo, ícone e foco < 3:1 | P · amador 6; 5 P5 |
| 9 | Texto sobre foto agitada | densidade de bordas (Canny) num halo de 1 corpo ao redor do texto | > metade da média da seção | A · amador 7; 12 C17 |
| 10 | Tamanho | `font-size` computado de `p, li, input, select, textarea` e de todo texto visível | corpo/campo < 16 px; texto < 14 fora de rótulo declarado; qualquer < 12 | P · 5 P3 |
| 11 | Linha de leitura | caracteres por linha (`Range.getClientRects` por linha) | > 75 (A > 66) | P · 5 P12 |
| 12 | Alvo de toque | caixa de `a, button, input, summary, label, [role=button]` | < 24×24 (P); CTA < 48 de altura no celular (A) | amador 17; 5 P4 |
| 13 | Um CTA primário | `data-papel="cta"`: estilos distintos, fundo, nº por página e por tela | > 1 estilo; fundo transparente (vazado) ou em degradê; < 3 na página de venda; 2 primários na mesma tela | P · amador 5; 14 D2 n.º 3 |
| 14 | Formulário | `input`s, `<label for>` visível (não `sr-only`), `placeholder`, `type/inputmode/autocomplete`, `checked` | captura > 3 campos; campo sem rótulo visível; tel sem `inputmode=numeric` ou máscara ≠ 11 dígitos; consentimento marcado; sem link de privacidade | P · 5 P7, P8 |
| 15 | Foco | Tab por todos os focáveis; `outline`/`box-shadow` com × sem foco; `elementFromPoint` no centro | sem mudança visível; contorno < 2 px ou < 3:1; foco 100% sob barra fixa | P · amador 16; 5 P6 |
| 16 | Movimento | `document.getAnimations()`: propriedades, duração, curvas | anima `top/left/width/height` (P); > 500 ms fora de loop declarado, > 3 tipos ou > 2 curvas (A) | amador 10; 13 §8.3 |
| 17 | Reduzir movimento | contexto com `reduced_motion="reduce"` | algo ainda desliza ou um loop continua | P · amador 11 |
| 18 | Pausa | animação infinita, vídeo `autoplay` ou contador por segundo × botão com `aria-label` de pausar | loop > 5 s sem controle; > 1 loop na mesma tela (A) | P · amador 12; 5 P13 |
| 19 | Carrossel automático | captura da 1ª tela em t = 0 e t = 6 s sem interação, fora dos loops declarados | mudou | P · amador 13 |
| 20 | Contador | recarregar 2× e comparar o alvo (`data-fim`); texto com relógio no futuro | alvo mudou; "00 dias" ou zero sem estado novo; data/hora não estão em texto | P · amador 14; 14 D2 n.º 1 |
| 21 | Texto em imagem | h1, preço, data e CTA são nós de texto? OCR nas imagens da 1ª tela | algum é pixel | P · amador 15; 5 P11 |
| 22 | Palavra sozinha | última linha de h1–h3 a 360 px (`getClientRects` por palavra) | 1 palavra | P · amador 18 |
| 23 | Quase alinhado | bordas esquerda/direita na tinta (`text-box`) entre si e com as colunas | 0,5 px a 1,5% da largura | P · amador 19; 12 C3 |
| 24 | Família de forma e cor | `border-radius` (fora 0 e pílula), `box-shadow`, cores saturadas (OKLCH C > 0,1) | > 3 raios; > 3 sombras; > 2 cores de destaque | P · amador 8, 9; 12 C20 |
| 25 | "Kit IA" | 1ª família em `tipografia.md` § vetos; degradê com matiz 250–290° em fundo ou botão; ≥ 3 irmãos de mesma caixa; brilho radial atrás de h1 centrado | ≥ 3 sinais (P); 1–2 (A) | amador 1; 10 §1.2 |
| 26 | Logos da faixa | área de tinta de cada logo | ± 15% da mediana [ponto de partida] | A · amador 20 |
| 27 | Só com mouse | `cursor: none`; conteúdo que só aparece em `:hover` | qualquer um | P · amador 22 |
| 28 | Orçamento por tela | `data-papel="ornamento"` e heróis por janela de `innerHeight` | > 2 ornamentos; > 1 herói | A · amador 23; 10 §5.2 |
| 29 | Ritmo | por seção: luminância média do fundo, densidade de tinta, largura do conteúdo | vizinhas iguais nos 3 eixos; 3 cheias (> 0,55) seguidas; 2 escuras seguidas; > 3 tons de fundo | P · amador 24; 12 §3.5 |
| 30 | Espaços e escala | `padding`/`margin`/`gap` e `font-size` computados; grupos de texto por seção | espaço fora da escala 4/8 ou de P/M/G/GG; interno > 0,5× externo; > 6 tamanhos de tipo; razão < 1,25; > 6 grupos | A · 12 C4, C5, C14, C21, C22 |
| 31 | Compartilhar | `og:image` (1200×630), `og:title`, `og:description`, `theme-color`, favicon | falta algum | P · amador 25; 10 A13 |
| 32 | Restos de outra edição | anos e datas no texto (`20\d\d`) × ano da campanha | ano divergente | A · amador 27 |
| 33 | Lei | CNPJ (regex) no rodapé; `<s>/<del>` de preço × `data-base-60d`; parcelado com à vista e total | falta CNPJ; "de" sem base declarada; parcela sem total | P · 10 §3.6, E19 |
| 34 | Barra fixa | elemento `fixed/sticky` embaixo: `scroll-padding-bottom`, `safe-area`, visibilidade com o formulário na tela | padding < altura da barra; cobre o formulário | P · 5 §4.2 |

Saída: relatório por largura + folha da página com caixas e avisos (como o `camadas.py`). Só se mostra com **zero P**.

## 11. Lacunas
- **Nenhum elemento de estilo tem teste A/B publicado** (vídeo de fundo, grão, marquee, bento, adesivo, título gigante);
  botão fixo no celular tem testes opostos; nº de seções e alternância de fundo só têm guias, não estudos (10 §7; 12 §8).
- **Números a calibrar** com páginas aprovadas: orçamento (10 §5.2) e os limites "[ponto de partida]" do checklist
  (densidade 0,55, ± 15% nos logos, 120 px de branco, 14 px de rótulo, 3 pesos, `font-display: swap`).
- Custo de `backdrop-filter`, filtros SVG e shaders em celular barato: sem número (10 §7; 13 §9) → medir.
- `text-box` no Firefox: a 10 não confirmou; a 13 (dados BCD) dá Baseline com o Firefox 154 → vale a 13.
- OCR (checagem 21) não está instalado: usar o Gemini (visão) ou instalar o Tesseract [proposta]. "Foto de banco" por
  CLIP é hipótese (10 §7). Licenças que podem mudar: GSAP, Remix Icon (13 §9). Lei: leitura nossa, não é parecer.
