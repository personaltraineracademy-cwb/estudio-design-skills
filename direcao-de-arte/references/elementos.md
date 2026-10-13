# Elementos, fundos, texturas e grids (regras congeladas)

Entre parênteses = seção da pesquisa de origem (4: casos Channel 4, MIT Media Lab, Picfair, Public Theater, Holzer…;
11: catálogo E01–E124; 13: elementos em código e licenças; 14/14b: técnicas medidas em sites de referência e
vocabulário de educação física). "[ponto de partida]" = número sem fonte, calibrar no olho a 100% e 25%.
Não repete: `camadas.md` (pilha L0–L8, integração, efeitos), `qualidade.md` (portões, zonas, cartão de bolso),
`tipografia.md` (tratamento de letra, vetos de fonte), `site.md` (botão, faixa rolante, bento e outros blocos de página).

## Regra-mãe: todo elemento tem origem
Antes de desenhar, cada elemento diz de onde vem. Sem uma destas origens = **alerta** (decoração genérica) e sai:
1. **Assunto do cliente** — instrumento, objeto ou regra técnica da área. Ex.: o simetrógrafo do FennerLab é a grade
   real da avaliação postural (14 B; 14b §5.0); OSESP usa a pauta, não a clave de sol (11 §4.7); Paris 2024, o
   paralelepípedo da rua (11 §3.4 tipo 4).
2. **Logo/marca** — um pedaço do símbolo solto ou a geometria dele (Channel 4, Herman Miller, Nubank; 11 §3.4 tipos 1, 2 e 5).
3. **Dado real** — número, curva ou mapa do próprio cliente (Oi, OSESP; 11 §3.4 tipo 3; 14b §4.8).
4. **Acabamento** — grão, papel, sombra de sistema: não carrega ideia, só une as camadas (ver "Acabamento premium").

- Tirar do assunto a **estrutura**, nunca o clichê: pauta sim, clave de sol não; papel milimetrado sim, traçado de
  ECG não (11 §4.7; 14b 5.7).
- **Fiel ao real:** escala, número e proporção certos. Um Borg de 1 a 10 ou uma anilha na cor errada mostra, para quem
  é da área, que a marca não sabe do assunto (14b §5.0 n.º 2).
- Cada elemento declara **função** (enquadra, aponta, mede, informa, separa) e **frase** (o que diz). Sem resposta,
  sai (11 §3.5 n.º 2; 14b §5.0 n.º 3). Checagem proposta para o palco: `data-funcao`; sem ela = erro (11 §5).
- **Dado de enfeite = dado verdadeiro ou esquema assumido** (rotulado). Proibido: gráfico "fake" que parece resultado,
  código de barras/QR que não lê, coordenada ou "REF-0042-X" inventados (11 E103–E105; 14b §4.8).
- **Modelar, nunca copiar:** a assinatura de uma referência fica com a referência; partir de outro instrumento (14b §5.0 n.º 4).

**Derivação dentro de uma campanha** (kit atual): todo elemento novo é (a) um pedaço do dispositivo A da marca, (b) um
pedaço do dispositivo B, ou (c) o encontro dos dois. Ex.: timecode impresso num dossiê; tarja que vira lower third.
Sem banco de texturas. Precedente: Channel 4 2015, o "4" quebrado em 9 blocos usados soltos e nunca inteiro (4).

**Cada peça tem UM mundo dominante.** O outro entra com no máximo 1 detalhe. No total, ≤ 3 elementos de interface por
peça. Elemento sem função sai: o timecode marca a hora real, a bateria conta os dias, o carimbo diz o status.

## Família coerente: 5 números tirados do logo
Antes de criar qualquer elemento, fixar 5 números no `brand.json` (bloco `familia`), medidos num lado menor de 1080
(11 §3.3). Todo elemento nasce deles; o verificador recusa raio, traço ou ângulo fora da ficha (11 §3.3, §5).

| Número | Como medir no logo | Como aplicar |
|---|---|---|
| `modulo` (unidade) | a medida que se repete no símbolo: altura da maiúscula do logotipo, lado do módulo ou largura da haste (`elements.py dna`) | margens, passos, gutters, braço de cantoneira e tamanho de elemento = múltiplos (ou ½) do módulo |
| `traco` fino + grosso | o traço mais fino do símbolo e a haste | ≤ 2 espessuras por peça; fino = 2 px num 1080 (some no celular abaixo disso; 1,5 px é o mínimo absoluto) (11 E15) |
| `raio` | o canto do símbolo/logotipo; sem canto: 10% do lado de um quadrado com ≥ ½ do lado maior do formato (Odido, 11 E12) | 1 raio de canto por peça, fora a pílula (GitLab, 11 §3.1); aninhado = externo − (borda + espaço) (14b §4.3) |
| `angulo` | o ângulo de corte/inclinação do logo; sem ele, 0/45/90 | faixas, fatias, hachuras, setas e rotações só nesse ângulo (11 E03, E10, E17) |
| `acento` | a cor de ação da marca | < 5% da área: CTA, palavra-chave e marcas mínimas (traço, cantoneira, ponto) (14 A, D n.º 2) |

- **Família de raios do SISTEMA** (kit, site): 3–5 valores com nome, repetidos (gsaweb: pílula 999 · moldura 32 ·
  cartão 26 · pasta 20 · rótulo 6) (14 A, D n.º 4); cada peça usa 1. Raio ≤ ½ da menor aresta (`camadas.md` §5).
- **Pílula e balão** (Odido, 11 E04, E34): raio = 50% da altura; ≤ 2 tamanhos por peça; respiro H = 100% do corpo e
  V = 67%; rótulo ≤ 3 palavras (GitLab); balão ≤ 3 linhas e só para fala de verdade. **Contêiner:** respiro = raio (11 E12).
- **Detalhe diminui com a escala** (GitLab, 11 §3.1). **Variação com teto:** conjunto fechado, ≤ 4 por eixo
  (`variacoes.py`); o MIT trocou 40 mil variações por uma grade 7×7 (11 §3.4).

## Construção (exemplo: campanha com live; uma unidade para tudo)
- **u** = altura da maiúscula da voz de dados. **Proporções:** fio = 0,14u (mín. 1,5 px); ponto "ao vivo" = 0,84u;
  braço do canto do visor = 2,6u, e o respiro dos rótulos = 2 × braço (como no logo REC); espaço entre itens de uma
  barra = 1,6u.
- **Tamanho:** a maiúscula de qualquer rótulo é ≥ 25 px num lado menor de 1080.

## Orçamento por peça
| Papel / item | Limite | Origem |
|---|---|---|
| **Herói** (lido a 25%, a 3 m, em 0,5 s) | exatamente 1; ≥ 30% da área **ou** o maior contraste | 11 §3.1–3.2 |
| **Apoios** (fio, contêiner, grade visível, rótulo) | 1–2; contraste médio; presos à grade | 11 §3.2 |
| **Temperos** (grão, textura, micrográfico, rabisco) | 0–2; ≤ 10% de contraste de luminância; nunca sob texto pequeno | 11 §3.2, §3.5 n.º 4 |
| Famílias de elemento (ex.: forma-mãe + fios + grão) | ≤ 3 | 11 §3.1 |
| Elementos distintos / principais | ≤ 7 / ≤ 3 | `camadas.md` §2; `qualidade.md` cartão n.º 6 |
| **Efeito de destaque** (glow, 3D, cromado, holográfico, aberração) | 1 por peça, só no herói ou numa palavra | 11 E63, E76, E78 |
| Marcas à mão (círculo, sublinhado, seta) | 1–2; traço 1,5–2× o fio; na cor de ação | 11 E33 |
| Elemento que passa pela frente ("costura") | ≤ 1 | `camadas.md` §2 |
| Estilos combinados (ex.: tipo gigante + adesivo + grão) | 2–3, nunca o cardápio todo | 10 §5.1 |
| Direção de sombra / receita de sombra | 1 / 1 | 11 §5, E71 |

- **Herói primeiro**, apoios depois: somar enfeite "até parecer cheio" é o erro n.º 1 (11 §3.5).
- **Teste do tirar:** tirar cada elemento um por vez; se a peça não piora, ele sai (11 §3.1; `camadas.md` O12).
- O papel é da peça: o mesmo elemento pode ser herói numa e tempero noutra, mas só 1 herói por peça (11 §3.2).

## As 12 famílias de elementos (catálogo completo em 11 §2)
"Custo de leitura" [proposta] = quanto a família disputa atenção e contraste com o texto.

| Família (itens) | Serve para | Premium × cafona | Custo de leitura |
|---|---|---|---|
| Primitivas geométricas (E01–E14) | herói gráfico, recorte, contêiner | 1 forma enorme cortada ou cruzamento de cor calculado × bolinhas a 10% e blob pastel | médio |
| Linhas e fios (E15–E25) | organizar, medir, ligar | 1–2 espessuras presas às colunas, régua que mede algo real × fio "só para separar", "rede neural" | baixo |
| Molduras e marcações (E26–E36) | enquadrar, rotular, carimbar | visor que enquadra 1 coisa, etiqueta que informa × cantoneira em tudo, selo "100% garantido" | baixo |
| Tipografia como imagem (E37–E53) | herói tipográfico, superfície | 1 deformação com regra, glifo da fonte da marca × "warp" do editor, aspas de outra fonte | alto (regras em `tipografia.md`) |
| Texturas e acabamentos (E54–E68) | superfície, "mão" | defeito real (impresso, escaneado), 1 por peça × overlay de poeira baixado, xerox no CTA | médio |
| Colagem e mídia mista (E69–E75) | prova, bastidor, voz humana | 3–6 fragmentos, sombras iguais, foto → vetor → rabisco × 20 pedaços sem hierarquia | alto |
| Luz e cor (E76–E84) | clima, código de contexto | glow só no que emite luz, tabela contexto → cor × outer glow em texto, mesh roxo-rosa | médio |
| 3D (E85–E92) | objeto-herói | 1 objeto, 1 luz, sombra de contato + projetada × objeto "colado" sem sombra, clay liso de IA | médio |
| Padrões e generativo (E93–E102) | fundo, campo, série | parâmetros travados, campo nascido do logo/dado × Perlin padrão, labirinto genérico | alto sob texto |
| Informação como ornamento (E103–E110) | prova, profundidade técnica | dado verdadeiro na grade + 1 título que lê × número inventado, QR em story | médio |
| Ícones, pictogramas, mascote (E111–E115) | lista, etapa, reação | mesma grade, traço e raio do logo × ícones de 3 bancos, emoji do sistema | baixo |
| Tratamentos de foto (E116–E124) | unificar fotos de terceiros | 1 tratamento na série (duotone, flash direto) × filtro "vintage", 2 fotos a 50% | alto (C1/C1b de `camadas.md`) |

## Cor com FUNÇÃO (exemplo validado na pesquisa; adapte a cada marca)
| Cor | Função |
|---|---|
| Vermelho | NO AR agora (tally vermelha). Nunca enfeite |
| Verde/lima | PREVIEW, "você é o próximo" (tally verde) → tudo antes da hora da live |
| Amarelo | interface de câmera (UI de DSLR) |
| Ouro/champagne | tarja de luxo (Holzer pinta tarjas em folha de ouro) → revelação |
| Azul institucional | lower thirds, página, legendas |

## Mundos de referência e seus elementos (exemplo: campanha com live e revelação; desenhar em `elementos.py` do projeto)
- **Transmissão / câmera:** visor (4 cantos) · ● AO VIVO / ● PREVIEW · timecode `HH:MM:SS:FF` (tabular; `:` e não
  `;`) · barra de status (bateria = dias, contador = noite n/3) · medidor de áudio (segmentos, os 2 de cima no acento) ·
  guias de área segura (93/90%, fio a 25%) · multiview (programa + câmeras, tally) · lower third · bug do canal · barras
  de cor da marca (+ PLUGE) · leader de contagem · legenda SDH (≤ 42 caracteres por linha, caixa preta) · scanlines só
  dentro do visor.
- **Sigilo / documento:** família de tarjas (sólida, vazada com o logo, parágrafo redigido, tarja que deixa escapar 1
  letra) · tarja metálica (só no tema de ouro) · marcação de sigilo (faixa "RESERVADO ATÉ 20H30") · carimbo da MARCA
  (moldura dupla, tinta falhada, ±4°) · dossiê com aba · código de barras válido (Code 128) + série · marcas de
  corte/registro · marca d'água a 4% · papel.

## 10 regras para não ficar cafona
1. Um mundo manda, o outro tempera; ≤ 3 elementos de interface por peça.
2. Elemento sem função sai.
3. Cor funcional é sagrada (vermelho = no ar).
4. Glitch, RGB deslocado, VHS e estática só como tempero de transição (1 palavra, poucos quadros).
5. Grão mono, baixo e UM só: 3–8%, o mesmo no fundo, na foto e nos elementos, zero no texto (ver "Acabamento
   premium"; substitui o antigo "~60% na foto", que contradizia `camadas.md` §3.5).
6. Fino e alinhado: fios, cantos e tarjas presos ao grid. Sem bisel, brilho, sombra 3D ou neon.
7. Regra real, detalhe certo: timecode correto, legenda de 42 caracteres, código que escaneia, áreas seguras reais.
   O detalhe certo separa referência de pastiche.
8. Sigilo DE MARCA, não documento falso: nada de brasão, selo oficial, nome de órgão ou polícia.
9. **Tarja nunca no rosto** (lê como réu). Ela esconde preço e informação.
10. Mostrar pedaços, guardar o todo para o momento (preço e logo completo na revelação).

## O que está vivo × o que cansou (2026)
**Vivo: "técnico + humano"** — base disciplinada (grade, dados, micrográficos) + UMA camada claramente feita à mão
(11 §0 n.º 1, §1.1). Foge da cara de IA (polido demais) e do "imperfeito de kit" (bagunça sem motivo).
- Mão de verdade: tinta, papel, colagem, costura, argila com marca de dedo, **feitos e fotografados** em luz natural
  (Landor "Anti-AI Crafting"; 11 §1.1 A, E61, E68, E92). Rabisco e textura reais (impressos/escaneados) > simulados (11 §0 n.º 13).
- Papel e impressão: fotocópia/scanner, riso com desregistro de 1–3 px numa direção só, preto de xerox (It's Nice That
  "Make me a copy"; bares de SP; 11 §1.1 B e H, E54–E57).
- Marcação à mão (círculo, sublinhado, seta): traço real escaneado, ou `perfect-freehand` com semente; nunca fórmula
  perfeita (11 E33; 13 §4.2).
- Inventário numerado ("visual index") com objetos reais do assunto (11 E35); diagrama técnico verdadeiro (11 E19).
- Micrográficos: rótulos e métricas **verdadeiros** como textura + 1 título que lê (11 E103). Só quando o assunto é
  técnico; não é a "mono < 32 px espalhada" vetada em `tipografia.md`.
- Mídia mista em ordem fixa: foto (verdade) → vetor (marca) → rabisco (voz) (11 E73).

**Proibidos** (alerta no plano; sai antes de montar):
- "Kit IA": Inter sem escolha + degradê índigo→roxo + 3 cartões iguais + brilho atrás do título + botão em degradê +
  ícones de traço fino genéricos (10 §1.2; 14b §4.6).
- Corporate Memphis; blob vetorial pastel "segurando" a página (11 §1.2, E14).
- Degradê granulado genérico como "fundo bonito"; mesh roxo-rosa-laranja de app de meditação (11 E79–E80).
- Glassmorphism/neumorfismo como estilo; vidro só em 1–2 elementos com contraste medido no pior pixel (11 §1.2; 10 §1.2).
- "Imperfeito de kit": fita + rasgo + rabisco + scan juntos, digitais e perfeitos demais (11 §1.2, §3.5 n.º 5).
- Prateleira de template: pontos com máscara radial, glow no CTA, grade com brilho em todas as seções, Vanta.js
  (14 C; 14b §4.5–4.6; 13 §3.3) — salvo se o ponto/luz significar algo do assunto.
- Elemento que imita interface: botão desenhado em anúncio, ▶, ✕, emoji do sistema, QR em story (11 §3.5 n.º 8, E113).
- Clichê do assunto (traçado de ECG + coração em saúde; clave de sol em música) (14b 5.7; 11 §4.7).
- IA imitando "feito à mão" com perfeição suspeita; clay liso; mascote 3D genérico (11 E68, E92, E114).
- Op-art, guilloché, meio-tom fino ou textura sob texto pequeno (11 §3.5 n.º 4); glitch/RGB fora de transição (regra 4).

## Vocabulário do assunto: educação física e saúde
> **Exemplo de assunto (curso de educação física).** Para outro cliente, derivar do assunto dele pelo mesmo método: listar instrumentos,
> escalas, protocolos e gráficos reais da área; desenho fiel; função + frase; risco de clichê (14b §5.0).

| Elemento (14b) | Origem em 1 frase (desenho fiel) | Uso · risco de clichê |
|---|---|---|
| Planos anatômicos (5.1) | sagital, frontal e transversal, perpendiculares entre si | ícone de módulo de biomecânica · médio |
| Prumo lateral + 5 pontos (5.2) | meato, acrômio, trocânter, à frente do joelho e do maléolo (Kendall) | régua onde o título encosta · médio (perto do FennerLab) |
| Goniômetro (5.3) | transferidor 0–180°, tracinho a 5°, longo a 10°, número a 30°, braços fixo e móvel no fulcro | moldura de número "90°" · baixo |
| Borg 6–20 (5.4) | 15 degraus; rótulo só em 6, 7, 9, 11, 13, 15, 17, 19 e 20 (Borg 1998) | progresso de série · baixo |
| RPE/RIR (5.5) | RPE 10 = 0 repetições em reserva; contagem 4-3-2-1-0 | contador regressivo · baixo |
| Zonas de FC (5.6) | 5 faixas iguais de 50–100% da FCmáx, na rampa da marca (nunca arco-íris) | fundo em faixas · médio |
| Papel do ECG (5.7) | grade fina a cada 1 mm, grossa a cada 5 mm — só a grade | textura técnica · **alto** com traçado |
| Curva de lactato (5.8) | guias em 2 e 4 mmol/L, pontos de coleta de teste real | "antes/depois do limiar" · baixo |
| Hill força × velocidade (5.9) | hipérbole: mais carga, menos velocidade (nunca reta) | fundo de força/potência · baixo |
| Força vertical (5.10) | curva em "M" ~1,0–1,5× o peso andando; guia em 1,0 | divisor-onda · baixo |
| Vetor de reação do solo (5.11) | seta saindo da sola + componentes tracejadas | seta de CTA com sentido · médio |
| Ciclo da marcha (5.12) | apoio 60% / balanço 40%; pés defasados 50% | linha do tempo · baixo |
| Marcadores Plug-in Gait (5.13) | 16 esferas; coxa/tíbia assimétricas de propósito | carregamento, fundo de laboratório · médio |
| Trajetória da barra (5.14, 5.26) | só de rastreio real de vídeo; no arranco a barra recua | assinatura de técnica · baixo se real |
| Anilhas IWF (5.15) | 25 vermelha, 20 azul, 15 amarela, 10 verde, 5 branca; ≥ 10 kg = 450 mm de diâmetro | pilha-gráfico, numeral "kg" · médio |
| Barra + marcas de pegada (5.16) | 2,2 m e 20 kg; marcas a 910 mm (41% do comprimento) | sublinhado entre as marcas · baixo |
| Pista (5.17) | 8 raias de até 1,22 m; raio da raia 1 = 36,80 m | moldura de foto, corrida · médio |
| Régua de periodização (5.18) | micro (semana) · meso (2–6 micro) · macro, como mm/cm/dm | cronograma, rodapé · baixo |
| Tempo 3-1-2-0 (5.19) | descida–pausa–subida–pausa; o 1º número é sempre a descida | divisor rítmico, 1 tracinho/s · baixo |
| Tabata (5.20) | 20 s/10 s × 8 = anel de 8 × (30° cheio + 15° vazio) | carregamento, selo · médio |
| 7 dobras + adipômetro (5.21) | Jackson & Pollock: 7 pontos marcados com "×" | lista de 7 itens · médio |
| Dinamômetro de preensão (5.22) | mostrador kg dentro / lb fora + ponteiro de pico em outra cor | moldura de KPI de força · baixo |
| Banco de Wells (5.23) | régua em cm; pés em 23 ou 26 cm (declarar o protocolo) | régua de progresso · baixo |
| Pressão plantar (5.24) | pegada em grade de sensores, 5–7 níveis da rampa, picos no calcanhar e antepé | textura de dado real · médio |
| EMG (5.25) | bruto (±) → retificado → envelope suave | "do ruído ao sinal" · médio |

Do catálogo geral, também do assunto: cronofotografia (Muybridge/Marey) com grade e quadros numerados para explicar um
movimento (11 E120); pictogramas de esporte na grade, só 0/45/90° (Aicher, 11 E111); inventário numerado das ferramentas
do curso (11 E35); linhas de velocidade no ângulo do movimento, comprimentos 1:4 (11 E23).
- **Não usar:** simetrógrafo, coluna em pílulas e "alinha/assenta" (assinatura do FennerLab) (14b §5.27); silhueta
  "antes/depois" de corpo (constrangimento) (14b 5.21); escala errada = reprova (14b §5.0).

## Acabamento premium (valores)
**Grão — UM só por peça**, mono, σ fixo na série, sobre fundo + foto + elementos (L0–L5) e nunca no texto; razão σ
pessoa × fundo 0,8–1,25 (`camadas.md` §3.5, L6). Amplitude 3–8% (escuro 4–6%, papel 2–4%), grão de 1–1,5 px (4);
na arte: `efeitos.grao_np` σ 0,018 (14 D n.º 6) ou `efeitos.grao_url` (padrão 0,06, em overlay/soft-light).

| Fundo | Receita | Origem |
|---|---|---|
| Claro | grão escuro em `multiply`, camada a 14–18% (gsaweb: `fractalNoise` 0,8, 2 oitavas, ladrilho 180 px, 16%) | 14 A, D n.º 6; 14b §4.4 |
| Escuro | grão claro e esparso em `screen` 15–18% + `feComponentTransfer` gamma 3 (0,5³ = 0,125: só os picos ficam = "poeira de luz") | 14 B; 14b §4.4b |

- Ladrilho repetido = `stitchTiles="stitch"`; `baseFrequency` nunca inteiro (sai vazio); ≤ 3–4 oitavas (13 §1.0; 14b §4.4b).
- Filtro em camada própria (nunca no elemento com texto: dissolve a letra), com `color-interpolation-filters="sRGB"`;
  grão sempre por último, depois do degradê — é o que segura o banding no escuro e na compressão do Instagram (14b §4.4).

**Raios e bordas estilizadas**
- `corner-shape` (Chrome 139+, só com `border-radius`): `squircle` = superelipse 2 · `bevel` = chanfro · `scoop` =
  côncavo · `notch`; fundo, borda e sombra seguem a forma. Na peça (Chrome do motor) à vontade; no site, só como
  enfeite com `border-radius` de reserva (13 §2.1–2.2; 14b §4.2).
- **Pasta** (aba) e **entalhe** (aba pendurada, cantos côncavos): `clip-path: path()` gerado no tamanho final (path em
  px não escala) ou `shape()` (%, Baseline 02/2026); sombra de forma recortada = `drop-shadow` no pai (14b §4.1–4.2; 13 §2.2).
- **A forma conta o que é:** pasta = ficha, avaliação, dossiê (não promoção); entalhe = etiqueta pendurada de
  data/local, fora de y < 240 no 9:16; ingresso = vaga (14 D n.º 12; 14b §4.1–4.2).
- Cantoneira/marca de corte (no site do FennerLab: L de 12 px, fio 1 px) só onde há MEDIDA (foto de avaliação, dado),
  nunca em todo cartão (14 B; 14b §4.9).

**Fios:** fino 2 px num 1080 (mín. 1,5), grosso 6–10 px, pontas retas, começam e terminam em linha de coluna, encostam na tinta e
não na caixa (11 E15 [ponto de partida]). Hachura: passo 6–12 px, traço 1,5–3 px, 1–2 ângulos (11 E20). Régua: traço
maior a cada 5 ou 10, curto = 40–50% do longo (11 E16). Marcador de lista = traço curto no acento (14 B).

**Sombra dura (neo-brutalismo só de tempero):** cor sólida, deslocada, SEM desfoque, com borda de 2 px; site 3–4 px; na
peça 3–4% do lado menor do objeto; sempre para o mesmo lado (direita-baixo = luz de cima-esquerda); mesma cor e
deslocamento na série; só em clicável, item ativo ou objeto "recortado e colado"; nunca misturada com sombra suave
(14 A; 14b §3.5). O pacote inteiro (bordas grossas + cores em choque + mono) fica fora de saúde e finanças (14b §3.3).
Sombra de papel (suave): 2–6 px, desfoque 0–6 px, 15–30% de preto, 1 token `--sombra` (11 E71). Adesivo: borda
branca 1,5–3% do lado, sombra 2–4 px a 20–30% (11 E69). Símbolo desfocado ao fundo: só o símbolo, nunca o logotipo
com letras, pré-renderizado (14 D n.º 11; 14b §4.7).

## Fundos (`scripts/fundos.py`)
- **Escuro premium:**
  - base quase preta (nunca #000);
  - 1–2 poças de luz atrás do herói e no "chão", na COR DE BASE clareada (luz na cor de destaque vira lama);
  - vinheta de 15–30%;
  - grão mono de 4–6%;
  - tudo em float, com dither no fim (sem degrau).
- **Ciclorama:** parede → piso com horizonte suave a 62–68% da altura. Em foto real: estúdio vazio pelo Gemini + recorte
  por cima.
- **Degradê:** só entre cores vizinhas; interpolar em OKLCH. O resvg NÃO faz mesh nem `fr`: empilhe radiais ou gere em
  numpy.
- **Foto de fundo:**
  - duotone por paleta;
  - meio-tom com célula de 8–14 px a 45°, só no fundo ou em ampliação gigante, nunca no rosto principal.
- **Tipográfico:** palavra gigante cortada ou parágrafo redigido. Ou fica a ≤ 12% de contraste do fundo, ou vira o
  título; nunca no meio-termo.
- **Papel:** off-white quente (nunca #FFF), fibras + manchas + grão de 2–4%; texto e tarjas em vetor POR CIMA.

## Ordem das camadas (texto sempre nítido)
1. Fundo raster (degradê, luz, vinheta, textura).
2. Foto.
3. Elementos e tarjas em vetor.
4. Unificação: UM grão sobre 1–3 juntos (razão σ pessoa × fundo 0,8–1,25; `camadas.md` L6).
5. Texto, logo e CTA em curvas por último (nunca recebem efeito).
6. Uma reamostragem só: renderizar no tamanho final, ou 2× e reduzir uma vez (13 §6.1); conferir a 100% no celular.

## Grids (coluna = (L − 2·margem − (n−1)·gutter) / n)
| Formato | Margens | Módulos | Gutter |
|---|---|---|---|
| Feed 4:5 1080×1350 | 60–80 | 6 col × 8 lin | 24 |
| 1:1 1080×1080 | 60–80 | 6 × 6 | 24 |
| Story 9:16 | zona de texto x 108–972 · y 240–1248 (x ≤ 852 abaixo de y 936); abaixo de 1248 só imagem | 6 col × 7 lin na zona (módulo 134) ou 8 × 15 na tela (96) — `composicoes.md` §2.3 | 24 |
| Landing | container 1320 | 12 col | 24 |
| Live 16:9 | título seguro 96/54; ação 67/38 | 12 col dentro do título seguro | 24 |

- **Linha de base:** 8 px; corpos e entrelinhas múltiplos de 8, mas a entrelinha com acento é medida na tinta.
- **Grade mono** (peças-documento): célula = avanço da mono × entrelinha (medir no `hmtx`).
- **Grid visível como marca (no máximo 2 recursos por peça):**
  - cruzes "+" de 8–12 px a 15–25% nos cruzamentos;
  - coordenadas A1…F8 em mono na margem;
  - marcas de corte;
  - timecode como coordenada.

## Texturas (`fundos.py` + brand-studio `fx.py`)
| Efeito | Premium quando | Parâmetros |
|---|---|---|
| Grão de filme | mono, fino, mais nos meios-tons | 3–8% (escuro 4–6%, papel 2–4%), 1–1,5 px |
| Risografia | 2 tintas, papel, leve desregistro | desregistro 1–3 px, multiply |
| Meio-tom | pontos grandes assumidos, 1 cor | célula 8–14 px, 45° |
| Dither Bayer | "pixel de tela" ampliado 2–4× | 4×4 / 8×8; estável em vídeo |
| Fotocópia | em 1 elemento | limiar → desfoque 0,6 px → limiar |
| Tinta que espalha | carimbo e tarja de papel | dilatar 0,5–1 px + deslocamento 1–2 |
| Scanlines | só dentro do visor | 1 px a cada 3–4 px, 4–8% |

## Movimento (para animar depois)
| Elemento | Comportamento |
|---|---|
| Ponto ao vivo | pisca a 1 Hz (nunca mais de 3 vezes por segundo; nunca um fundo inteiro piscando) |
| Preview → ao vivo | verde vira vermelho no corte da hora |
| Timecode | quadros de 00 a 29 |
| Tarja, revelação | da esquerda para a direita em 400–700 ms, `cubic-bezier(0.4,0.14,0.3,1)` |
| Tarja, teaser | levanta 2–4% e volta em 240 ms |
| Lower third | entra em 240 ms e sai em 150 ms |
| Legenda | ≤ 17 caracteres por segundo |

## Biblioteca `scripts/ornamentos/` (usar antes de desenhar elemento à mão)

Pacote com ~15 famílias e 700+ elementos, todos gerados da FICHA da marca (5 números + cores + fontes + semente):
trocar a ficha = a biblioteca inteira na cara de outra marca/produto.

**Usar**
```
cd scripts   # a partir da raiz da skill
python -m ornamentos.catalogo -o <pasta> [--produto todos|linha-a|linha-b|linha-c] [--familia f] [--raio 28]
python -m ornamentos.catalogo -o <pasta> --familia f --revisao     # 6 por página, grandes, numerados (revisão um a um)
```
Em código: `from ornamentos import carregar_tudo, Ficha` → `from ornamentos import formas` → `formas.conteiner(ficha,
w, h, …)` devolve `Elemento(svg, caixa, nome, familia, css, nota, w, h)`. SVG em curvas (fonte → path), caixa = TINTA,
CSS quando serve ao site. Cliente novo: `Ficha(unidade, traco, raio, angulo, fundo, tinta, acento, sobre_acento, papel,
apoio, fonte_display, fonte_texto, fonte_mono, seed)` — os números vêm do logo (seção "Família coerente").

**Ficha e forma:** `raio_sm` 16 · `raio` 28 · `raio_lg` 44 (escala de `references/forma.md`; arte 1080 ≈ 2,75 × site).
Nunca "2 × raio". Sorteio reprodutível: `ficha.rnd(...)` (sha256; `hash()` do Python muda a cada execução).

**Famílias (arquivo → o que tem)**
| Família | Módulo | Conteúdo |
|---|---|---|
| formas | `formas.py` | contêiner com cantos por tipo (redondo · chanfro · squircle · côncavo · degrau = nomes do `corner-shape`), pasta, entalhe, aba pendurada, recorte com botão, ingresso com picote, balões, etiqueta de bagagem, molduras concêntricas, janela, monitor, celular; helpers de canto/rótulo usados por outras famílias |
| fios | `fios.py` | fios, divisórias com rótulo, réguas (0–100, horário com cursor), cruzes, prova de gráfica, grade de pontos, cantoneiras, colchetes, callouts, listas, setas, cotas, linha do tempo, numeração |
| selos | `selos.py` | selo circular/giratório (texto 360° sem emenda), estrela/explosão, tampinha, roseta, carimbo, AO VIVO, medalha, etiqueta de preço sem preço |
| faixas | `faixas.py` | faixa com texto, fita de isolamento, fitas cruzadas, marquee, listras, toldo, persiana, bolinhas, xadrez, tarjas, sinais gigantes (%, numerais, aspas, +, setas) |
| profundidade | `profundidade.py` | sombra dura/longa, extrusão, camadas, papel sobreposto, adesivo, relevo, contorno deslocado, botão neo-brutal com estados |
| assunto | `assunto.py` | educação física fiel: goniômetro, Borg 6–20 (1998), zonas de FC, Tabata, cronômetro, dinamômetro, proporções, 7 dobras, prumo, barra/anilhas IWF, halter, kettlebell, periodização, fita métrica, Wells, adipômetro, ficha de treino, cones, escada, T-test, apito, cadência, RIR, marcha, planos; helpers `justo()` (recorta na tinta) e `semente()` |
| dados | `dados.py` | barras/anéis de progresso, contadores, linha do tempo, calendário real, heatmap, "pague 1 leve 2" em diagrama, curvas ESQUEMA, tabelas com dado verdadeiro, status |
| colagem | `colagem.py` | fita adesiva, adesivo, papel rasgado, recorte de jornal, polaroide, filme 35 mm, clipe, índice, post-it, etiquetas |
| tipograficos | `tipograficos.py` | texto em anel/arco/espiral/onda com correção óptica, eco, bloco justificado, numeral em contorno, lombada, datador |
| codigos | `codigos.py` | QR (segno) e Code 128 LIDOS DE VOLTA (zxing-cpp) — se não lê, é recusado; numeração de série |
| mao | `mao.py` | marcação à mão: sublinhado, círculo, marca-texto, riscado, seta, colchete, asterisco, check, rabisco, chaves |
| linhas | `linhas.py` | topografia, ondas, espiral, fluxo, guilloché, moiré, hachura, op-art, grade distorcida, pauta, velocidade, raios, concêntricos, perspectiva |
| pontos | `pontos.py` | Voronoi, pontilhado, meio-tom, ruído azul, dither, grade de pontos, mosaico |
| texturas | `texturas.py` | grão, papel, amassado, xerox, borda rasgada, carimbo, riso, scanlines, poeira, gradiente com grão |
| grades | `grades.py` | grids visíveis: modular, linha de base, colunas de site, isométrica, polar, corte/sangria, milimetrado, registro (56, revisados um a um) |

**Trocou a fonte ou a cor da marca → refazer os kits** (kit antigo fica na fonte anterior). **Todo texto de elemento
em português do Brasil** (nada de "ADMIT" em inglês no ingresso).

**Contrato para família nova:** `@amostra("familia", "nome")` numa função `f(ficha) -> list[Elemento]`; texto sempre
em curvas; cores só da ficha (ou derivadas); filtro SVG com `sRGB` e região ampliada; caixa = tinta medida
(`assunto.justo`); nota de 1 linha "quando usar · de onde vem"; dado real ou rótulo EXEMPLO/ESQUEMA.

**Portão antes de mostrar (um catálogo mostrado só com checagem automática tinha elementos QUEBRADOS):**
1. `catalogo.py` sem avisos (tinta fora da caixa, vazio, alto demais);
2. **revisão UM A UM** com `--revisao` (6 por página, ~760 px + miniatura no fundo oposto), critérios D1–D44 (numeração única) em
   `scripts/ornamentos/_revisao/CRITERIOS.md`, registro por elemento em `_revisao/<familia>.md`;
3. pergunta-chave: "um leigo diria que quebrou?" — efeito que imita erro (fatiado, glitch, desalinho) só entra se lê
   como intencional a 25%; risco sobre hora/data/preço = "cancelado"; na dúvida, remover;
4. conferir em 2+ fichas de cor (ex.: um produto vermelho e outro roxo) — código de barras/contraste mudam.

## Plano original das 20 funções (referência histórica; hoje coberto pela biblioteca acima)
Contrato de toda função: recebe a `ficha` (5 números) e devolve **SVG em curvas + caixa da tinta** (e CSS quando serve
ao site); raster só para textura, com máscara que protege texto e rosto; semente fixa; filtro SVG com `sRGB` e região
ampliada; licença de cada biblioteca no cabeçalho (11 §5; 13 §1.0, §8; 10 §6). Ordem = prioridade.

| # | Função | Entrada → saída | Uso | Junta |
|---|---|---|---|---|
| 1 | `ficha_familia` | logo SVG → 5 números + `confere(svg)` (raio/traço/ângulo fora = erro) | ambos | 11 #1, §3.3 |
| 2 | `conteiner` | w, h, forma (raio · squircle · chanfro · pasta · entalhe · moldura concêntrica · ingresso com picote) → path no tamanho final + CSS com reserva | ambos | 11 #4, #41; 14b §4.1–4.3 |
| 3 | `pilula` | texto, tipo (pílula · balão · etiqueta), cheia/contorno → regras Odido | ambos | 11 #2, #3, #13 |
| 4 | `fios` | grade, tipo (fio · régua com dado · cruzes "+" · cantoneiras · callout · lista com traço) | ambos | 11 #9–12; 14 §E |
| 5 | `profundidade` | alvo, tipo (dura · papel · longa · extrusão · símbolo desfocado) → 1 token, 1 direção | ambos | 11 #17; 13 #24–25; 14b §3.5, §4.7 |
| 6 | `grao` | fundo claro/escuro, força, seed → ladrilho `multiply` ou `screen`+gamma 3 (embrulha `efeitos.grao_url`) | ambos | 14 D n.º 6; 14b §4.4 |
| 7 | `marcacao_mao` | alvo, tipo (sublinhado · círculo · marca-texto · riscado · seta), seed → traço com pressão | ambos | 13 #18–20; 10 #5–6 |
| 8 | `selo` | texto, tipo (estrela · explosão · circular via `seal.py`), pontas do DNA | ambos | 11 #5; 10 #7–8 |
| 9 | `instrumento` | nome + dado → desenho fiel do vocabulário do assunto (goniômetro, Borg, régua de periodização, barra com pegada, anel Tabata…), plug-in por cliente | ambos | 14b §5; 14 §E |
| 10 | `dado_ornamento` | dado real → heatmap, pilha, curva; sem dado = só esquema rotulado | ambos | 14b §4.8; 11 E109 |
| 11 | `faixa` | ângulo da ficha, largura, texto → faixa, listras, bolinhas | arte | 11 #6–7 |
| 12 | `sinal_gigante` | glifo da fonte da marca, modo (cheio · contorno por fora · eco 3–5×) | arte | 11 #14–15 |
| 13 | `transformar` | SVG/PNG, op (fatiar · envelope · áspero · zigue-zague · derreter · tinta acabando · pixelar) | arte | 11 #8, #23–25; 13 #21–22 |
| 14 | `colagem` | PNGs recortados, modo (adesivo · fita · rasgo · índice numerado) | arte | 11 #16, #18, #20–21 |
| 15 | `texto_no_caminho` | texto, path (círculo, arco, espiral) → curvas com espaçamento óptico | arte | 11 #19; 13 #23 |
| 16 | `textura` | tipo (papel · nuvem · mármore · fibra · xerox · borda rasgada) → filtro SVG ou numpy | ambos | 13 #1, #6; 11 #22 |
| 17 | `linhas` | campo/dado, tipo (topografia · onda · espiral · fluxo · guilloché · moiré · hachura · op-art · grade distorcida · pauta · velocidade) | arte | 11 #27–31, #33–35, #37–39; 13 #13 |
| 18 | `pontos_celulas` | imagem/dado, tipo (Voronoi · pontilhado Poisson · meio-tom vetor · dither azul · grade de pontos) | ambos | 11 #36; 13 #14–17; 14 §E |
| 19 | `filtro_camada` | estilo de camada do PS (bisel · relevo · sombra interna · brilho · gooey · contorno duplo · tons) → `<filter>` | arte | 13 #2–5, #7–8 |
| 20 | `codigo` | conteúdo → código de barras/QR válido, margem de 4 módulos, teste de leitura | arte | 11 #42 |

Fica fora (já existe ou cabe em outro script): superforma e Truchet → `sketch.py`; 3D → `render3d.py`; malha de
gradiente, shader, distorção, mesclar, máscara suave → `fundos.py`/`efeitos.py`; captura, cor sRGB e regressão →
`palco.py`/`qa()`; recolorir SVG → paleta da brand-system; botão, faixa rolante, bento, contador, pilha de avatares →
`../criacao-de-sites/scripts/site.py`; caligrama, cronofotografia, pictogramas, ícones do DNA, letras de remendo → P3, só se um cliente pedir (11 §5).

## Bibliotecas: permitidas × proibidas (licenças: reconferir antes de usar; 13 §3.3, §4, §8.4)
- **Permitidas — Python:** opensimplex, coloraide, svgpathtools (MIT); pixelmatch (ISC); shapely (BSD-3; GEOS LGPL
  como biblioteca dinâmica); vpype (MIT) e skia-python (BSD-3), opcionais; já instaladas: skia-pathops, scikit-image,
  OpenCV (Apache-2.0), scipy.
- **Permitidas — Node** (`node_modules` da skill): roughjs, rough-notation, perfect-freehand, simplex-noise, flubber,
  svg-path-commander, culori, three.js, PixiJS, Two.js, Matter.js (MIT); d3-delaunay, d3-contour (ISC);
  @paper-design/shaders (Apache-2.0); ogl (Unlicense). Ruído azul: texturas CC0 ou gerado por nós.
- **Ícones** (só funcionais, peso casado com a fonte, NUNCA em logo, selo ou elemento de marca): Lucide (ISC),
  Phosphor, Tabler, Iconoir (MIT), Material Symbols (Apache-2.0) (13 §4.2).
- **Livres de direito:** padrões históricos (Truchet, guilloché, op-art, moiré); kits e fontes de marcas citadas não —
  só o princípio (11 §6 n.º 7). Fontes OFL à vontade; ITF FFL (Fontshare) em peça e site, sem embutir o arquivo em
  repositório público (14b §2.0).
- **Com cuidado:** GSAP (grátis e comercial, mas proprietário: proibido em ferramenta visual que concorra com a
  Webflow; rever antes de cada site) (13 §5.1); Hero Patterns (CC BY 4.0, exige crédito; só estudo); `alea` e a porta
  Python do perfect-freehand (licença a conferir) (13 §4.1, §9).
- **Proibidas:** LYGIA (não comercial sem licença paga); Trianglify (GPLv3 → refazer com d3-delaunay); Remix Icon
  (desde 01/2026 proíbe uso como logo/marca); Typed.js (GPL); "Stripe gradient" (sem licença); fonte "demo só para uso
  pessoal" (14b §1.3); por escolha: Vanta.js (visual de template), p5.js (LGPL, redundante), pycairo (redundante)
  (13 §3.3, §8.4; 10 §0 n.º 15).

## Elemento verdadeiro, lógico e bonito
Regra: elemento tem que ser verdadeiro, lógico e bonito. Três testes antes de um elemento ir para a página:
1. **Verdadeiro:** é o instrumento/forma real do assunto (goniômetro com escala 0–180/360, planos anatômicos com
   a pessoa em posição anatômica), com nomes certos. Rótulo cortado pelo viewBox = defeito (`FRONTAL` saiu como `FRONTAI`).
2. **Lógico:** mede ou organiza algo que está na tela. Instrumento pela metade atrás do corpo, plano flutuando sem
   figura, numeral coberto = "estranho". Centro da escala = centro do retrato; escala inteira visível.
3. **Bonito:** traço com peso coerente, sem pictograma de palito quando o assunto pede ilustração. Se o código não chega,
   usar IA + tratamento (ver `ia-imagem-video.md`) e manter o texto em código.
Aplicado: `assunto.goniometro(modo='minimo', completo=True)` com braços curtos e viewBox simétrico no fulcro; planos
anatômicos por IA (mannequin + plano de vidro, um plano por painel, rótulos em código).
