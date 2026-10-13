# Composições: armações, estruturas e regras congeladas (artes)

> Regras para compor PEÇAS (post, story, banner, capa, anúncio). Números entre parênteses
> ("(12 §x)") apontam a seção da pesquisa de origem. Número sem fonte = "[ponto de partida]". A parte de SITES está em `site.md` (12 §3).
> Não repete: movimentos (`movimentos.md`), camadas (`camadas.md`), série/campanha (`sistema-de-campanha.md`),
> portões (`qualidade.md`). Aqui fica o "onde vai cada coisa" antes de montar.

## 1. O que tem prova e o que é mito
| Afirmação | Veredito | Regra para nós | Origem |
|---|---|---|---|
| φ é a proporção "mais bonita" | **mito** como fórmula (preferência fraca ou nula; Partenon e Mondrian são falsos) | φ e raízes servem só como linha de ALINHAMENTO | (12 §1.1) |
| Terços melhoram a peça | **mito** como regra geral (em escolha forçada, o centro ganhou) | terços = ferramenta de decisão rápida, não argumento | (12 §1.1) |
| Objeto único fica melhor no centro | **prova** (Palmer; Hoh 2023: centrado + borda vazia) | herói único → centro DE PROPÓSITO (G01), com respiro em volta | (12 §1.1) |
| Fora do centro, o herói aponta para dentro | **prova** (viés para dentro, Palmer) | herói fora do centro olha/anda para o centro ou para o texto | (12 §1.1, C11) |
| Pesado embaixo, leve em cima | **prova** (viés ecológico) | objeto apoiado vai para baixo; título no vazio de cima | (12 §1.1) |
| Borda vazia em volta do herói | **prova** (Hoh 2023) | herói respira (≥ 5% do lado menor) ou sangra de verdade (≥ 8% dele fora) | (12 §6.2 C12) |
| Terço ou áureo? | **irrelevante**: diferem ~53 px num 1080 (360 × 413) | decidir só "no centro" × "fora do centro"; "quase no centro" = erro | (12 §1.5) |
| Centro de massa equilibrado (Arnheim) | **fraca** (McManus 2011 preferiu fora do eixo) | equilíbrio é DECLARADO (estável ou tensão); medida = aviso | (12 §4.1, §8 4c) |
| "7 ± 2 elementos" | **mal citado**; o limite real é 3–5 "pedaços" (Cowan) | contar GRUPOS, não objetos (§4) | (12 §4.2a) |
| Bagunça = muitos elementos | **errado**: bagunça = VARIAÇÃO de cor, ângulo e contraste | 30 parecidos + 1 herói funciona; 8 todos diferentes, não | (12 §4.2h) |
| "+20% de compreensão com branco", "regra dos ímpares", "1 efeito por peça" | **sem fonte primária** | não usar como argumento; ficam como [ponto de partida] | (12 §8 4b) |
| Primeira impressão | **prova**: decide em 50–500 ms; complexidade pesa mais que cor | a peça tem que ler a 25% e de relance | (12 §6.1) |

**Conclusão:** a armação escolhe ONDE. O que o motor garante é o que tem prova: um foco, viés para dentro, tamanho
coerente e borda de respiro em volta do herói (12 §1.1).

## 2. Armações prontas em px, por formato
Fórmulas (12 §1.5): terços = L/3 · φ = 0,382 L e 0,618 L · rebatimento = lado curto medido de cada ponta · recíproca =
S²/L dos cantos · "olho" = pé da perpendicular do canto na diagonal. 2000×590 e 800×800 = [derivado] (mesmas fórmulas).
**T** = cabe texto · **I** = cai fora da zona de texto, serve só para imagem/fundo.

### 2.1 Linhas por formato
| Linha | 1:1 (1080²) | 4:5 (1080×1350) | 9:16 (1080×1920) | 16:9 (1920×1080) | 2000×590 | 800² |
|---|---|---|---|---|---|---|
| Zona de texto | x 80–1000 · y 80–870 | x 80–1000 · y 80–1140 | x 108–972 · y 240–1248; x ≤ 852 se y ≥ 936 | x 96–1824 · y 54–1026 | 80% central: x 200–1800 · y 59–531 | 80% central: 80–720 |
| Terços x | 360 · 720 T | 360 · 720 T | 360 · 720 T | 640 · 1280 T | 667 · 1333 T | 267 · 533 T |
| Terços y | 360 · 720 T | 450 · 900 T | 640 T · **1280 I** | 360 · 720 T | 197 · 393 T | 267 · 533 T |
| φ x | 413 · 667 T | 413 · 667 T | 413 · 667 T | 733 · 1187 T | 764 · 1236 T | 306 · 494 T |
| φ y | 413 · 667 T | 516 · 834 T | 733 T · 1187 T (x ≤ 852) | 413 · 667 T | 225 · 365 T | 306 · 494 T |
| Rebatimento | — | y 270 · 1080 T | y 840 T · 1080 T (x ≤ 852) | x 840 · 1080 T | x 590 · 1410 T | — |
| Recíprocas | — | y 486 · 864 T | y 608 T · **1312 I** | x 608 · 1312 T | **x 174 · 1826 I** | — |
| 4 "olhos" | centro (540, 540) | (421,527) (659,527) (421,823) (659,823) T | (260,461) (820,461) T · **(260,1459) (820,1459) I** | (461,260) (1459,260) (461,820) (1459,820) T | **(160,47) (1840,47) (160,543) (1840,543) I** | centro (400, 400) |
| Quartos (armadura) | 270 · 810 T | x 270 · 810 · y 338 · 1012 T | y 480 T · **1440 I** | x 480 · 1440 · y 270 · 810 T | x 500 · 1500 · y 148 · 442 T | 200 · 600 T |

### 2.2 O que a tabela manda
1. **9:16:** a metade de baixo da armação (y 1280 · 1312 · 1440 · 1459) é só imagem: corpo, chão, objeto. Título e logo
   nos olhos de cima (y ≈ 461) ou na faixa φ/rebatimento (y 733–1080, x ≤ 852 abaixo de 936) (12 §1.5 nº 2).
2. **4:5:** o rebatimento y 1080 separa o quadrado (título + herói) da faixa de 270 px (só o que pode sumir:
   assinatura, textura). Se a peça também for recortada em 1:1 central, o essencial fica em **y 135–1080** (12 §1.5 nº 3).
3. **1:1:** a armadura cruza nos terços (360/720) e nos quartos (270/810) (12 §1.3); a faixa y 870–1080 é só imagem.
   Post que vai para a grade do perfil: essencial em x 171–909 (`qualidade.md`).
4. **16:9:** os terços coincidem com a subdivisão √3 (+2,6%) (12 §1.5 nº 4). Live vista no celular: preço/CTA ≥ 43 px de
   maiúscula (`qualidade.md`).
5. **2000×590 [derivado]:** quadrado | faixa central de 820 | quadrado; olhos e recíprocas caem FORA da área essencial →
   texto e herói em x 590–1410 (ou num quadrado, com x ≥ 200); texto lido ≥ 34 px de maiúscula [ponto de partida].
6. **800×800 [derivado]:** armadura do quadrado; texto lido ≥ 25 px de maiúscula (= 34/1080 × 800).
7. **O herói usa o PONTO da armação; o texto usa a COLUNA da grade (2.3).** Ponto fora da zona → vale a zona.

### 2.3 Grades modulares (módulo quase quadrado) [derivado de 12 §1.6]
Colunas dentro da ZONA de texto, gutters múltiplos de u = 12 (casa com E20); no feed, margem 84 = 7u (a zona permite
80; a pesquisa usou 72 com gutter 16, fora da unidade). Linhas repetidas para baixo; o que passa do limite é só imagem.
Formato: colunas × linhas · gutter · **módulo**.

| Formato (área das colunas) | Poucos campos (herói forte) | Médio (4–8 elementos) | Fino (muitos elementos, dados) | Só imagem |
|---|---|---|---|---|
| 1:1 (x 84–996, y desde 84) | 4×4 · 24 · **210** | 6×6 · 12 · **142** | 12×12 · 12 · **65** | linha 4 de 4 (y 786+) · 6 de 6 (854+) · 11–12 de 12 (854+) |
| 4:5 (x 84–996, y desde 84) | 4×5 · 24 · **210** | 6×7 · 12 · **142** | 12×15 · 12 · **65** | linha 5 de 5 (1020+) · 7 de 7 (1008+) · 14–15 de 15 (1085+); carrossel: nada em x > 888 com y < 156 |
| 9:16 zona (x 108–972, y 240–1248) | 5×6 · 36 · **144×138** | 6×7 · 12 · **134×133** | 12×14 · 12 · **61×60** | quando y ≥ 936: col. 5 de 5, 6 de 6, 11–12 de 12; tudo abaixo de 1248 |
| 9:16 arte inteira (margem 72) | 5×9 · 24 · 168×176 | 6×11 · 24 · 136×140 | 8×15 · 24 · **96×96** | é a grade da IMAGEM; o texto usa a de cima (12 §1.6) |
| 16:9 (x 96–1824, y 54–1026) | 5×3 · 12 · 336×316 | 12×7 · 24 · 122×118 | — | — |
| 2000×590 (x 202–1798, y 64–526) | — | 10×3 · 24 · **138** | 20×6 · 24 · **57** | x < 200 e x > 1800 |
| 800² (88–712) | 4×4 · 24 · **138** | 6×6 · 12 · **94** | 8×8 · 24 · **57** | borda de 88 |

- **Unidade:** u = 12 px no 1080; gutter, margens, alturas de bloco e fios em múltiplos ou frações simples de u; altura
  do módulo = N entrelinhas (12 §1.6, §4.2c).
- **Quantos campos:** peça simples 6–8 campos; peça densa 20–32 (12 §4.1). Fotos e recortes em só **3–4 tamanhos**
  tirados da grade; o tamanho = a importância (12 §4.1).
- **O texto pequeno herda os eixos do texto grande** (musica viva) (12 §1.6).
- **Grade composta** (séries que trocam o nº de colunas): 58 unidades de 16 px = 928 (margens 76) → 6 col = 128 · 5 =
  160 · 4 = 208 · 3 = 288 · 2 = 448, gutter 32; versão "barata" 28 unidades = 5 e 6 colunas (12 §1.7).
- **Quebrar a grade:** UMA coisa por peça e contra uma grade visível (herói que sangra, palavra que cruza 2 colunas);
  sem grade, pendurar tudo num eixo forte (12 §1.9).

## 3. Catálogo de estruturas de arte (G/F)
Esquemas, casos e erros de cada uma: (12 §2.A, §2.B). Parâmetros = [ponto de partida] da pesquisa. **★ = as 15 mais
úteis para campanha de curso/evento.** "Liga a" = movimento (M, `movimentos.md`) ou arquétipo (Arq., `sistema-de-campanha.md`).

| Cód | Estrutura | Quando usar | Herói | Onde vai o texto | Liga a |
|---|---|---|---|---|---|
| G01 ★ | Centro absoluto | a mensagem é UMA coisa que vira ícone | 35–55% da largura; centro ótico 3–5% acima | mesmo eixo, embaixo; ≤ 3 níveis | M04 · M23 |
| G02 | Simetria quebrada | "só uma coisa muda" | metades idênticas; diferença ≤ 10–15% da área | faixa embaixo | M10 · Arq. 8 |
| G03 | Pirâmide | hierarquia, "subir de nível" | rosto/produto no ápice (terço de cima) | na base, fora do triângulo | — |
| G04 | Diagonal 15–35° | velocidade, esporte (pouco) | ao longo do eixo | só o título no ângulo | M11 |
| G05 | Radial | lançamento, energia | centro num terço ou na borda | fora dos raios | — |
| G06 ★ | Gangorra (steelyard) | oferta com 1 detalhe precioso | massa 25–40% + peso 2–6% (≥ 6:1), cantos opostos | junto do peso pequeno | M03 · Arq. 13 |
| G07 ★ | Faixa / sanduíche horizontal | anúncio direto; cor por categoria | na faixa (25–40% da altura) | na faixa | M15 · Arq. 16 |
| G08 | Tríptico 1:2:1 | antes / durante / depois | painel central | embaixo, comum; no 9:16 empilhar | Arq. 4 · M08 |
| G09 | Grade preenchida irregular | muitos itens com ordem | bloco ≥ 3×3; 30–60% das células cheias | células do alto | M07 · M08 |
| G10 ★ | Mosaico / bento | o que o curso tem (módulos, bônus) | célula 2× a 2ª; 4–7 células | célula própria | M06 · M08 |
| G11 | Repetição + 1 diferente | 1 entre muitos (12–50) | o diferente, perto de um terço | embaixo | M10 · Arq. 21 |
| G12 ★ | Sequência de painéis | passo a passo, carrossel | último painel (clímax) | painel final | Arq. 17 |
| G13 | Tipo como arquitetura | nome forte sem foto | as letras (60–90% da área) | é o próprio herói | M19 · Arq. 19 |
| G14 ★ | Escala de choque ≥ 10:1 | número, data, nome curto | o enorme; o minúsculo ≥ 2% da altura | no vazio, perto do minúsculo | M01 · Arq. 1 · 6 |
| G15 | Moldura dentro de moldura | série-container | centro; 2–4 níveis, recuo 6–10% | entre molduras | M27 · M28 · Arq. 20 |
| G16 ★ | L/C/U de texto em volta da foto | professor + chamadas | foto 55–70% da área | braços de 10–18% | M06 (≈ F21) |
| G17 | Texto vira textura | manifesto, programa longo | forma recortada ≥ 30% | título por cima; a textura não é lida | Arq. 7 · 21 |
| G18 | Dados como cena | resultado, número real (com fonte) | o gráfico, sem eixos | 1 número-legenda | M21 · M26 |
| G19 | Espiral / S | jornada, percurso | centro num terço | início ou fim do S | — |
| G20 | Círculo + texto em órbita | selo, evento | círculo 50–75% da largura | em 2 arcos, ≥ 34 px de maiúscula | `seal.py` |
| G21 | Horizonte baixo/alto | calma, escala | figura no horizonte (céu ≈ 75%) | no campo vazio | M03 · Arq. 13 |
| G22 | Xadrez deformado | fundo com movimento | a região que quebra | fora do xadrez (vibra) | M10 |
| G23 | Ponte | parceria, mentor e aluno | 2 massas 1:1–1:3, vão 3–8% | embaixo | — |
| G24 ★ | Lista / índice | agenda, programação, módulos | a linha em destaque (5–12 linhas) | é o corpo | Arq. 9 · 15 |
| G25 | Constelação | rede, conexão | 4–7 pontos ligados de 15–60 | no vazio | M21 |
| G26 | Tipo vertical (coluna) | lombada, informação lateral | o resto do quadro | coluna 8–15%, à ESQUERDA no 9:16 | M12 |
| G27 | Cruz *(sem caso verificado)* | — | no cruzamento, num terço | num braço | — |
| G28 | Túnel *(sem caso verificado)* | foco dramático | abertura 30–50% | borda de baixo | ≈ Arq. 14 |
| G29 | Três pontos | trio (3 dias, 3 professores) | tamanhos 4:2:1, escaleno | embaixo | — |
| F01 ★ | Sanduíche tipográfico | capa, KV de evento, nome + rosto | pessoa entre a palavra de trás e as chamadas | trás 80–95% da largura; frente ≤ 40% da largura | M13 · Arq. 3 |
| F02 ★ | Close extremo cortado | intensidade, depoimento | rosto 110–150% da altura | ≤ 15% da área, 1 linha | Arq. 18 |
| F03 ★ | Rompendo o quadro | ação saindo da moldura | 15–25% da figura fora (1–2 saídas) | fora do quadro | Arq. 2 |
| F04 | Cascata de cartões | vários depoimentos | o cartão de cima (3–5 cartões) | ao lado | M09 |
| F05 | Colagem estruturada | bastidores, arquivo | 1 foto 2×2 na grade 3×3/4×4 | atravessa a grade | M17 |
| F06 ★ | Recorte + forma de cor | professor com a marca | forma da MARCA, 50–70% da largura | lado livre | M30 |
| F07 | Elenco em hierarquia (cuidado) | palestrantes | protagonista 40–50% da altura; ≤ 5 rostos | título + bloco mini | Arq. 5 |
| F08 | Figura minúscula no vazio | silêncio, escala | figura 2–8% e ≥ 50 px | pequeno, no vazio | M03 |
| F09 ★ | Olhar para o texto | toda peça com pessoa + oferta | perfil ou 3/4 | na linha do olhar (§5) | regra §5 |
| F10 | Foto dividida | duelo, antes/depois | 2 metades, olhos ± 2% | o único que cruza a divisão | Arq. 4 |
| F11 | Foto dentro da letra | palavra de 3–8 letras | as letras | rodapé | M14 |
| F12 | Fotomontagem surreal | metáfora forte | UMA ruptura (escala, contexto ou física) | discreto | — |
| F13 | Produto em órbita | material, kit | 35–50% da altura; 5–9 elementos em 3 profundidades | marca + 1 palavra | M18 |
| F14 | Herói + faixa de miniaturas | módulos, galeria | 50–65% da área; 3–5 miniaturas | célula final | Arq. 17 |
| F15 | Tiras deslocadas | transformação | tira dos olhos intacta | numa fresta | — |
| F16 | Silhueta chapada | gesto, atleta | 60–85% da altura, membros afastados | 1 linha | M24 |
| F17 | Duotone + tipo gigante | manifesto, energia | foto em 2 cores de luminosidade distante | 40–70% da largura, na borda | M16 |
| F18 | Anotação sobre foto | explicar técnica, corrigir execução | foto limpa + 3–6 marcas | notas que apontam fatos reais | M09 |
| F19 | Moldura de objeto/interface | bastidor, "print" | a foto | base da moldura | Arq. 10 · 22 |
| F20 ★ | Pessoa + número gigante | data, contagem, vagas | número 70–90% da altura | nome/data embaixo | M05 · M13 · Arq. 6 |
| F21 | Retrato + coluna lateral | capa editorial, entrevista | retrato 60–70% da largura | coluna no terço livre, 1 margem | G16 |
| F22 ★ | Estroboscópico | execução do exercício, progressão | pose final a 100% (4–9 repetições) | no fim do arco | M10 · M35 |
| F23 | Sombra como 2ª leitura | duplo sentido | a sombra (1 detalhe diferente) | embaixo | — |
| F24 | Sticker de borda branca | tom jovem | recorte com borda 2–4% | ao lado | — |
| F25 | KV esportivo | competição, evento esportivo | atleta 60–80% no pico do gesto, diagonal 15–30° | palavra condensada | M11 |
| F26 | Capa de álbum | foto excepcional | foto sangrada 100% | ≤ 10–15% da área, canto ou L | M04 · M12 |

**Como usar o catálogo:**
- **1 estrutura por peça** + até 2 movimentos de apoio (`movimentos.md`). Registrar no plano: `estrutura`, `centro`
  (cêntrica = núcleo + órbita · excêntrica = fluxo com direção) e `equilibrio` (estável · tensão) (12 §4.1, §4.3).
- **No 9:16:** G08 empilha; G26 só à esquerda (ícones do Reels); G07 deixa o campo de baixo absorver a interface;
  herói embaixo (G03, G21, G29) → texto na metade de cima (12 §2.A).
- **Sem caso forte de estúdio** (G20, G22, G27, G28, F14, F19, F20, F24): só com prova extra na arena (12 §8 nº 5).
- **Estrutura × arquétipo:** o arquétipo é o "o quê" (cena, slots, palavras); a estrutura é o "onde" (o esqueleto).
  Trocar a estrutura renova o arquétipo sem mudar o sistema (Venn da Economist, 12 §5.1).

## 4. Compor com muitos elementos
A bagunça vem da VARIAÇÃO, não da quantidade (Rosenholtz, Reinecke, Tuch) (12 §4.2h). O teto de `camadas.md` §2 continua
valendo (≤ 7 elementos distintos, ≤ 2 texturas, ≤ 1 elemento costurando).
1. **Orçamento de GRUPOS:** 1 herói + 2–3 apoios (título, logo, chamada) + até 3 grupos de tempero (ícones, dados, fios,
   selos) = 5–7 grupos. Vinte ícones alinhados num bloco = 1 grupo. Conta = manchas que sobram com desfoque de 2% da
   largura (12 §4.2a; Cowan: 3–5 pedaços). Post ≤ 4 grupos de texto (story ≤ 5) e ≤ 3 áreas de imagem (12 C14–C15).
2. **Concentrar:** a densidade num ponto, numa faixa ou num quadrante; o resto vazio. Espalhar por igual
   ("desconcentração", Wong) é a receita da bagunça; a anomalia (1 por peça) é o foco (12 §4.1).
3. **Vazio contínuo:** peça cheia = 25–40% da área sem tinta numa zona SÓ, não em frestas iguais (12 §4.2f); densidade
   0,35–0,55 salvo declarada (12 C7–C8).
4. **Uniformizar o resto:** apoios e temperos com pouca variação de matiz, ângulo e contraste. Separar níveis vizinhos =
   mudar UM eixo (tamanho OU peso OU cor); separar o herói = mudar 2–3 (12 §4.2g).
5. **Proximidade:** espaço dentro do grupo ≤ 0,5× o espaço entre grupos; entre seções ≥ 3× o interno [ponto de partida];
   título mais perto do próprio texto que do bloco de cima (12 §4.2d, C22). Eixos: ≤ 3 verticais fortes + 2 horizontais.
6. **Escala:** peça de impacto, razão 1,5–1,618; peça densa, 1,25–1,333; o herói pode pular 2–3 degraus; diferença
   pequena parece erro (14 × 16 pt) (12 §4.2b).
7. **Tokens de forma:** 1 raio (ou zero + 1), 1–2 espessuras de fio, 0°/90° + no máximo 1 diagonal fixa, 1 estilo de ícone;
   1 destaque de cor num só lugar; 1 efeito especial por peça (3D, brilho, grão forte, duotone) (12 §4.2e–g).
8. **Declarar os polos (Dondis):** ex. "assimetria + regularidade + profusão + unidade"; profusão só funciona com
   regularidade e unidade; nivelar ou aguçar, nunca ambíguo (12 §4.1).
9. **Cor por papel E por área (Albers):** hierarquia por valor, identidade por matiz; nunca texto entre duas cores de
   mesmo valor e matizes opostos (a borda vibra) (12 §4.1).
10. **Esqueleto do gênero reconhecível**, inovação nos elementos; público acima de 45 anos → menos complexidade (12 §4.2h).

**Receita (12 §4.3):** estrutura (§3) → orçamento → u + grade (§2.3) → ponto de densidade + vazio → escala → tokens →
uniformizar o resto → medir (§8) → bateria do olho: desfoque 5/10/20 px no 1080 (o de 20 px revela foco não planejado),
notan, espelho, de cabeça para baixo, 25% (12 §4.2i).

## 5. Pessoa na peça
Compatível com `camadas.md` (§3 integração, §4 oclusão, C3/C4/C7) — lá ficam os limites de pixel; aqui, o "onde".
1. **Olhar para o texto (F09):** rosto em 3/4 ou perfil virado para o título; **55–65% da largura livre** do lado do olhar;
   título na linha dos olhos ± 10% (rastreamento com 106 pessoas). Olhar para a câmera só quando a peça é SOBRE a
   pessoa (depoimento, F02), não sobre a oferta (12 F09).
2. **Viés para dentro:** pessoa fora do centro virada para o centro ou para o texto; para fora só com motivo escrito
   (12 C11). Nunca texto atrás da nuca (12 F09).
3. **Rosto nunca coberto:** 0% do rosto sob algo na frente; olhos e boca dentro da zona de texto; cabeça fora da interface
   (`camadas.md` C3, `qualidade.md` C7). No 9:16: olhos em y 240–1248 e x ≤ 852 quando y ≥ 936.
4. **Palavra atrás da pessoa (F01 · Arq. 3):** só palavra conhecida (nome, marca); a cabeça cobre ≤ 1/3 da altura das
   letras e **nunca o começo da palavra**; cobrir pela base; data, hora, preço, CTA e link 0% cobertos; números de
   cobertura = `camadas.md` §4 (12 F01).
5. **Corte do rosto (F02):** na testa e no queixo, nunca no olho; olhos a ~1/3 do topo; ponta do nariz nunca encostando
   na borda; tarja nunca nos olhos (Arq. 18) (12 F02).
6. **Duas ou mais pessoas:** olhos na mesma altura ± 2% e mesma luz (F10); elenco em ≤ 3 níveis, o 2º com 50–60% do
   protagonista, ≥ 2 olhares que se cruzam (F07). Teto: 3 pessoas (`camadas.md` §2); os 5 rostos do F07 só com exceção escrita.
7. **Pessoa + número (F20)** cobre 20–40% do número, nunca o traço que diferencia o dígito (3/8, 1/7); **figura pequena
   (F08)** com 2–8% da altura e ≥ 50 px num 1080; **silhueta (F16)** com braços e pernas afastados do tronco.
8. **Forma atrás da cabeça (F06):** forma tirada da marca; centro deslocado 5–15% do centro da cabeça; a cabeça passa
   5–15% acima da forma. Círculo centrado atrás da cabeça = auréola de santo (proibido).
9. **Expressão e gesto:** a expressão conta quem é a pessoa; atleta no pico do gesto, nunca parado posando (F07, F25).
   Foto escolhida pelo layout (lado do olhar, espaço do título, luz) ANTES de montar (`camadas.md` passo 5).

## 6. Séries
Eixos e limites por eixo ficam em `sistema-de-campanha.md`; aqui, o que é fixo × livre (12 §5).
1. **Declarar 3–4 constantes:** **voz tipográfica** (nº 1: 84% de 50 identidades dinâmicas mantêm o tipo; quanto mais
   o fundo varia, mais o tipo trava) · logo e posição · margem/grade · família de cor (12 §5.3–5.4).
2. **Por peça: 1 mudança grande + até 2 pequenas** [derivado: iPod 3 fixos × ~3 livres; LA28 3 × 1]. Eixos: escala ·
   corte/pose · cor/humor · imagem · posição e forma do tipo · **estrutura (§3)** · rotação/repetição · densidade ·
   técnica · tom · dados (12 §5.4).
3. **A variação vem do CONTEÚDO** (noite, pessoa, fase, dado real), nunca de sorteio; Melbourne, dinâmico por moda,
   envelheceu (12 §5.5 nº 4).
4. **O logo nunca muda:** a Tate com 70–75 versões confundiu a própria equipe (12 §5.5 nº 2).
5. **Nunca a mesma estrutura (G/F) nem o mesmo arquétipo em peças vizinhas**; nunca mexer numa constante dentro da série;
   cada peça se sustenta sozinha; a variação nunca fere a leitura (Wrapped 2021) (12 §5.5 nº 1, 3 e 8).
6. **Dois níveis:** regras duras dentro da edição/temporada; o sistema pode mudar entre edições. Renovar = estrutura nova
   dentro das regras (Venn da Economist), não outro sistema (12 §5.5 nº 5 e 7).
7. **Escolher o tipo de série** (van Nes): *container* (forma fixa, recheio livre) · *wallpaper* (marca + paleta fixas,
   fundo muda; o tipo trava 100%) · *fórmula* (grade e posição fixas) · *generativa* (cada variante forte sozinha) (12 §5.3).
8. **Coerência medida, regra dentro de ferramenta:** colorfulness ± 15%; complexidade nos percentis 20–80 das aprovadas
   (12 C16, C18); CLIP ≤ 0,92 entre vizinhas (`qualidade.md`); "um manual pode ser ignorado, um programa faz o que
   mandam" (Lorenz, 12 §5.3) → gerador `serie` (§9).

## 7. Clichês de pôster e capa a evitar
Antes de aprovar peça com pessoa, conferir esta lista; caiu num clichê → justificar (a categoria pede) ou trocar de
estrutura. Antídoto: expressão que conta quem é a pessoa, interação entre pessoas e uma ideia visual própria (12 §2.B.1).
- **Cor:** laranja e azul; tudo cinza com uma cor só; dourado ou amarelo de filme indie; azul de natureza.
- **Gente e rosto:** cabeças flutuantes de rosto neutro (F07); costas com costas; herói de costas olhando a destruição;
  gente pequena na praia + cabeças nas nuvens (F08); olho gigante; correndo na rua; "rostão + parede de texto azulada"
  (F02); rosto dividido para tudo (F10); auréola (F06); tarja nos olhos (Arq. 18); "rosca" de chamadas em volta do rosto (F21).
- **Geometria pronta:** espiral de Fibonacci colada (G19); "plexo" de banco de imagem (G25); triângulo equilátero (G03);
  cruz centrada = alvo (G27); raios perfeitos até o centro (G05); xadrez regular atrás de texto (G22).
- **Efeito de categoria:** linhas de velocidade, faíscas e fumaça no esporte (F25); confete uniforme (F13); "fantasia de
  IA" sem metáfora (F12); silhueta enganosa (F23); sticker sem motivo (F24); fitas adesivas falsas (F05); tiras
  deslocadas ao acaso = filtro de glitch (F15).
- **Template de social:** "logo no alto + pilha de texto + foto à direita + barra de CTA" em > 20% da série
  (`sistema-de-campanha.md`).

## 8. Regras computáveis
Prefixo **E** para não confundir com C1–C14 de `camadas.md` nem com C1–C26 da pesquisa ("12 C9"). Medidas nas caixas
de TINTA do `palco.py`, alinhamento com tolerância de 2 px num 1080 (12 §6.2). Onde: **P** = `compor.Peca.qa()` ·
**K** = `camadas.py` · **S** = futuro `estruturas.py`. **Portão** reprova; **aviso** pode ser aceito se a ficha DECLARAR
a escolha (vazio extremo, mosaico, tensão). Não se repetem aqui: margem, zona, ícones, colisão, quase alinhado, texto
pequeno (`qualidade.md` §1) nem contraste, tangente, rosto, oclusão, ritmo, herói, notan, DCM (`camadas.md` C1–C14).

| # | Regra | O que medir | Reprova quando | Tipo · onde | Origem |
|---|---|---|---|---|---|
| E01 | Poucos eixos | bordas esq./centro/dir. e topo/meio/base agrupadas (2 px) | eixos x > ⌈n/2⌉ + 2 ou eixos y > ⌈n/2⌉ + 3 (n = caixas) | portão · P | 12 C1 |
| E02 | Nada órfão | cada caixa divide ≥ 1 eixo com outra | texto < 100% ou demais < 80% (exceção declarada: M09) | portão · P | 12 C2 |
| E03 | Poucos tamanhos de tipo | corpos distintos (± 2%) | social > 3 (+ letra miúda legal) | portão · P | 12 C4 |
| E04 | Saltos claros | razão entre tamanhos vizinhos; maior ÷ corpo | vizinhos < 1,25; maior ÷ corpo < 4 no social (< 6 em M01) | portão · P | 12 C5 · `qualidade.md` |
| E05 | Poucas famílias | famílias usadas | > 2 (+ 1 mono utilitária) | portão · P | 12 C6 |
| E06 | Densidade no meio | tinta (sem fundo) ÷ área útil | fora de 0,35–0,55 sem declarar (vazio ≤ 0,15 · bento ≤ 0,75) | aviso · S | 12 C7 |
| E07 | Um vazio que respira | maior retângulo sem tinta nem textura forte ÷ área | < 0,12 feed · < 0,10 story | aviso · S | 12 C8 |
| E08 | Equilíbrio sem "quase" | distância centro de massa visual → centro ÷ meia-diagonal | entre 0,10 e 0,20; ou declarado "estável" com ≥ 0,20 | aviso · K | 12 C9 (soma ao C14) |
| E09 | Quadrantes coerentes | tinta por quadrante | simétrica: max/min > 2 · assimétrica: quadrante vazio > 15% | aviso · S | 12 C10 |
| E10 | Olhar para dentro | direção do rosto (YuNet olhos × nariz) ou da forma-seta | herói fora do centro virado para fora, sem motivo escrito | aviso · K | 12 C11 |
| E11 | Espaço à frente do rosto | largura livre do lado do olhar; centro do título × linha dos olhos | livre < 55% ou > 65%; título fora de ± 10% da linha | aviso · K | 12 F09 |
| E12 | Herói respira ou sangra | menor distância do herói à borda | 0,5–5% do lado menor sem sangrar ≥ 8% do herói | portão · P | 12 C12 |
| E13 | Herói domina | área do maior ÷ 2º | < 2 (< 4 em peça de uma ideia só) | aviso · P | 12 C13 |
| E14 | Poucos grupos de texto | blocos separados por > 1,5× a entrelinha | post > 4 · story > 5 | aviso · P | 12 C14 |
| E15 | Poucas áreas de imagem | fotos/ilustrações separadas | post > 3 (exceto mosaico/sequência declarados) | aviso · P | 12 C15 |
| E16 | Orçamento de grupos | manchas após desfoque de 2% da largura | > 7 | aviso · K | 12 §4.2a |
| E17 | Fundo calmo de BORDAS atrás do texto | densidade de bordas (Canny) num halo de 1 corpo | > ½ da média da peça | aviso · K | 12 C17 |
| E18 | Poucos ângulos | rotações e diagonais (± θ conta 1; 0°/90° não) | > 2 ângulos; ou 2 ângulos a < 10° um do outro [ponto de partida] | aviso · P | 12 C19, G04 |
| E19 | Família de raios e fios | raios de canto e espessuras distintos | raios > 3 · fios > 2 | aviso · P | 12 C20 |
| E20 | Espaços da unidade | espaço entre caixas vizinhas ÷ u (12 px) | não múltiplo (± 1 px) ou > 5 valores distintos | portão · P | 12 C21 |
| E21 | Proximidade agrupa | espaço interno ÷ espaço entre grupos | > 0,5 | aviso · P | 12 C22 |
| E22 | Blocos em proporção nomeada | razão de cada foto/cartão | fora de 1 · 4:5 · 3:4 · 2:3 · 16:9 · √2 · φ · 2:1 (± 2%) | aviso · P | 12 C23 |
| E23 | Leitura = destaque | ranking do mapa de destaque × hierarquia da ficha | os 3 primeiros não batem | aviso · K | 12 C24 |
| E24 | Simetria sem ambiguidade | IoU da tinta com o espelho vertical | 0,60–0,85 ("quase simétrico") | aviso · K | 12 C25 |
| E25 | Um efeito por peça | tipos: sombra projetada, brilho, desfoque de fundo, gradiente, contorno, 3D (grão não conta) | > 1 dominante | portão · P | 12 C26 |
| E26 | Centro ou fora, nunca quase | centro x do herói × centro da largura | desvio entre 1% e 5% da largura [ponto de partida] | aviso · P | 12 §1.5 nº 1 |
| E27 | Série coerente | colorfulness (Hasler & Süsstrunk); folhas da decomposição espacial | colorfulness fora de ± 15%; complexidade fora dos percentis 20–80 das aprovadas | aviso · S | 12 C16, C18 |
| E28 | Vizinhas diferentes | estrutura (G/F) e arquétipo no plano da série | igual à peça anterior ou seguinte | portão · S | 12 §5.5 nº 8 |
| E29 | Constantes intocadas | família, logo (arquivo + posição na grade), margem | qualquer diferença entre peças da série | portão · S | 12 §5.4 |
| E30 | Contrato da estrutura | parâmetros da estrutura declarada (ex.: G06 ≥ 6:1 · G02 metades IoU ≥ 0,95 fora da diferença ≤ 15% · G14 ≥ 10:1 · F04 3–12°, ângulos diferentes · F10 olhos ± 2% · F20 cobertura 20–40% · F08 ≥ 50 px) | fora da faixa da tabela §3 / (12 §2) | aviso · S | 12 §2, §7 |

## 9. Para virar ferramenta (geradores priorizados)
Módulo sugerido (ainda não existe): `estruturas.py`. Cada gerador devolve **caixas nomeadas** (herói, título, apoio, CTA, logo,
vazio) + **eixos declarados** para o `plano.py`; o HTML só é montado depois que o plano fecha; o `qa()` e o
`camadas.py` só confirmam (12 §7). Os 12 de maior impacto, na ordem de construção:

| # | Função | Entrada | Saída | Serve |
|---|---|---|---|---|
| 1 | `armacao` | formato, tipos (`tercos, phi, rebatimento, reciproca, olhos, quartos`), zona | linhas e pontos com T/I + camada SVG para a folha de prova | §2.1 |
| 2 | `grade_modular` | formato, colunas, gutter, densidade (`poucos · medio · fino`) | colunas/linhas com a marca "só imagem", CSS grid, guias | §2.3, G09, G10, F05 |
| 3 | `medidor` | peça renderizada (caixas do palco + máscara de tinta), ficha declarada | E01–E27 e E30 com valor, limite, portão/aviso (JSON + camada na folha) | §8 |
| 4 | `escala_tipo` | corpo base, razão, nº de níveis, linha de base | tamanhos arredondados na linha de base; avisos E03–E04 | §4 nº 6 |
| 5 | `orcamento` | lista de elementos, formato | herói/apoio/tempero, nº de grupos, avisos E14–E16 | §4 nº 1 |
| 6 | `ficha_estrutura` | código G/F, constantes, eixos variados | bloco do `plano.json`: estrutura, cêntrica/excêntrica, estável/tensão, polos, contrato E30 | §3, §6 |
| 7 | `olhar_para_texto` | foto recortada, formato | lado do olhar (YuNet) + caixa do título na linha dos olhos com 55–65% livre; E10–E11 | F09, F02, §5 |
| 8 | `sanduiche` | palavra, recorte, formato | caixas: palavra de trás 80–95% da largura, pessoa, chamadas ≤ 40%; começo da palavra protegido; oclusão pelo C4 | F01, Arq. 3 |
| 9 | `texto_em_L` | foto, lados (L, C ou U), braço | braço 10–18%, foto 55–70% da área; checa E10 | G16, F21 |
| 10 | `modular` | modo (`bento · mosaico`), nº de células, semente | células (líder 2× a 2ª; 30–60% cheias, 60–75% na colagem; herói ≥ 3×3) + ordem no celular | G10, G09, F05 |
| 11 | `serie` | plano, constantes, eixos, N | N fichas com 1 mudança grande + ≤ 2 pequenas, sem estrutura repetida em vizinhas; folha lado a lado; E27–E29 | §6 |
| 12 | `reflow` | peça, formatos | a mesma composição em 1:1 · 4:5 · 9:16 · 16:9 · 2000×590 · 800² por restrições (`kiwisolver`), dentro das zonas; troca a estrutura quando não cabe (ex.: G26 → G07 no 1:1) | todos os formatos |

Ordem: 1 → 6 (fundação) · 7 → 10 (estruturas ★ de curso/evento) · 11–12. Os outros 14 geradores de arte (`gangorra`,
`diagonal`, `cascata`, `orbita`, `anticliche`…) estão em 12 §7; os de site (`hero`, `secao`, `ritmo_pagina`) em `site.md`.

## 10. Lacunas
1. **Os limites de E01–E30 são ponto de partida:** as fórmulas completas de Ngo et al. e os limiares de Rosenholtz para
   peça social não foram lidos; calibrar com peças aprovadas e com a nota da arena (12 §8 nº 1–3).
2. **2000×590 e 800×800:** "essencial nos 80% centrais" não tem medida pública; as linhas da §2 são derivadas e o
   mínimo de texto no 2000×590 não foi medido na tela real → confirmar no painel do checkout.
3. **Oclusão (RESOLVIDO):** `camadas.md` §4 e `qualidade.md` C4 unificados no mais rígido de cada:
   **30% · 50% · 1ª letra ≤ 15% coberta**.
4. **Grades antigas (RESOLVIDO):** a linha do 9:16 na tabela "Grids" de `elementos.md` passou para as
   zonas atuais; as grades completas por formato ficam na §2.3 deste arquivo.
5. **Divergências resolvidas aqui:** salto de escala no social ≥ 4 (`qualidade.md`/M01), não ≥ 3 (12 C5); quase alinhado
   pelo verificador (0,5 px–1,5% do lado menor), não 3–12 px (12 C3); grade do feed com margem 84 e gutters de 12/24,
   não margem 72 com gutter 16 (12 §1.6).
6. **Duas medidas de equilíbrio** (DCM ≤ 25% em `camadas.md` C14 × faixa proibida 0,10–0,20 em E08): ver qual prevê
   melhor a nota da arena e ficar com uma.
7. **Sem caso forte:** G20, G22, G27, G28, F14, F19, F20, F24; Loomis não confirmado (12 §8 nº 5–6). **Quantos eixos
   variar:** sem regra publicada; "1 grande + ≤ 2 pequenas" é contagem nossa (12 §8 nº 9).
8. **Nenhum gerador existe ainda:** o `medidor` depende das caixas de tinta do `palco.py` e da máscara do `camadas.py`.

## 11. Regras de prática (redes e técnicas avançadas)
Técnicas completas: `tecnicas-avancadas.md` (17 técnicas, arquétipos A1–A6).
- Carrossel panorâmico: nada de rosto, texto ou logo a ± 60 px de uma emenda; só o objeto-ponte cruza; o slide 1 passa sozinho no portão (é a capa da grade).
- Grade do perfil é 3:4 (várias fontes; sem página oficial). Conta: 4:5 (1080×1350) aparece 1012×1350 na grade =
  −34 px por lado; capa de Reels 9:16 aparece de y 240 a 1680. Padrão continua 4:5 com o essencial no 3:4 central;
  1080×1440 só quando a peça inteira precisa aparecer na grade (o feed aceitar 3:4 ainda é disputado). Série julgada numa folha 3×3 de 3:4 a 25% (linha = trinca com papéis diferentes).
- Quadro 0 de vídeo é um pôster completo; vídeo nunca abre no preto.
- Texto em caminho: ≤ 8 palavras, raio ≥ 3× a maiúscula, nunca o título. Tipo em perspectiva só como imagem; data, preço e CTA sempre de frente.

## Regras de prática (peças com pessoa)
- **Faixa de baixo do 9:16** (abaixo de y 1248 e a coluna de ícones): sem INFORMAÇÃO, mas não vazia — imagem, foto ou
  textura continuam até a borda; vazia parece peça incompleta.
- **Foto da pessoa pede espaço:** retrato fechado (rosto ≈ 40% da foto) não cabe no 9:16 sem bater no texto ou na
  interface — pedir fotos soltas no briefing; sem elas, escolher armação que não dependa de corpo inteiro
  e avisar. Ampliar a foto para "encher" foi reprovado no olho.
- **Encolher a foto para o herói tipográfico aparecer** deixou o meio vazio e foi reprovado: declarar herói duplo
  (`st.heroi = [..]`) em vez de enfraquecer a imagem.
