# Revisão UM A UM dos elementos

Regra: catálogos mostrados só com checagem automática tinham elementos QUEBRADOS; todo lote é analisado um a um. O verificador
automático (tinta fora da caixa) e a folha reduzida não pegam isso: só o olho, um por um, grande.

## Como revisar
1. `cd scripts` (na raiz da skill) → `python -m ornamentos.catalogo -o <pasta> --familia <f> --revisao`
   → `<pasta>/revisao/<f>-NN.png`: 6 por página, ~760 px, numerados, tracejado rosa = caixa (viewBox), miniatura no
   fundo oposto no canto. Olhar CADA card (Read na página; se precisar, recortar/ampliar o card).
2. Para cada elemento perguntar: **"um leigo diria que quebrou?"**, "um diretor de arte sênior aprovaria?",
   "funciona a 25% (miniatura)?", "funciona no fundo oposto?".
3. Corrigir no módulo da família (nunca em helper compartilhado de outro dono: crie variante local) OU remover.
   Na dúvida, REMOVER: poucos perfeitos > muitos com defeito.
4. Renderizar de novo e olhar de novo até zerar. Olhar também no **tamanho natural (100%)**: a página de revisão
   reduz ~0,4× e inventa moiré em fios de 8 px; o que parece trama só na página não é defeito, e o que só aparece a
   100% é (D33).
5. Registrar em `_revisao/<familia>.md`: nº · nome · veredito (ok / corrigido: o quê / removido: por quê), citando os
   códigos D abaixo (numeração ÚNICA; a tabela "numeração antiga → nova" no fim traduz logs antigos).
6. Elementos de textura/ruído: medir a periodicidade no Chrome (FFT do ladrilho renderizado; ver D44) além de olhar.

## O que conta como DEFEITO (lista viva — numeração única D1–D70; acrescente no FIM, nunca renumere)

### Efeito, camada e traço
- D1 Efeito que IMITA ERRO de render: palavra fatiada/glitch/deslocada que parece bug, não intenção.
- D2 Cópias (eco, rastro, zoom) embolando com o original → texto ilegível; contornos cruzando letras.
- D3 Risco/linha atravessando hora, data, preço ou nome → lê "cancelado".
- D4 Texto/números fora das caixas, colunas ou bandas que deveriam contê-los (medir na tinta, não na caixa da fonte).
- D5 Texto invadindo faixa, borda, aba, furo ou outro elemento; respiro interno < raio (F13 de forma.md).
- D6 Contorno, sombra ou FIO aparecendo POR DENTRO do preenchimento (ordem de camadas/máscara errada; fio de grade
  atravessando bloco sólido de acento ou barra de texto → o sólido vai por cima, na cor já misturada com o fundo).
- D7 Fio, régua ou linha encostando/tangenciando letra (tangente) — afastar ≥ 0,5 da altura do traço ou cruzar de propósito.
- D8 Glifo cortado, acento cortado, texto saindo da caixa; corte que não parece decidido.
- D9 Desalinhamento "quase": coisas a 1–6 px de alinhar (alinhar de verdade ou afastar de propósito). Inclui a borda de
  uma zona que cai a 4 px da borda da coluna e faixa de 17,6 px sobre fios de 8 px.
- D10 Espessuras de traço inconsistentes sem regra; pontas soltas; emendas visíveis; moiré acidental; serrilha
  regular que lê como máquina (fita crepe com dente igual); traço centrado EXATAMENTE na borda da caixa (y = 0 ou y = H
  perde metade da espessura → contorno inteiro para dentro da caixa).
- D11 Elemento quase invisível no fundo (contraste) ou some na miniatura. Marca de escala "apagada" a 16% de tinta some
  a 25%: mínimo ≈ 34–36% da tinta e traço não mais fino que o aceso.
- D12 Semântica errada: oferta em "explosão de varejo" (Black premium não usa), selo oficial/brasão, número ou texto
  inventado ("RESERVADO ATÉ"), número inventado sem "EXEMPLO/ESQUEMA", conteúdo que contradiz a copy do cliente,
  cor-código que contradiz o número escrito (anilha IWF, kettlebell: dourado = 15 kg com "25" escrito).
- D13 Raio fora da escala (0 · 16 · 28 · 44 · pílula; `f.raio_sm/raio/raio_lg`), raio > ½ do menor lado, dois raios
  quase iguais no mesmo elemento, "2 × raio" (use `f.raio_lg`).
- D14 Texto girado/rotacionado com letra pisando em outra; kerning quebrado; tracking irregular; numeral de escala
  circular de cabeça para baixo (girar 180° na metade de baixo).

### Geometria e contorno
- D15 Seta com "toco": a ponta quadrada da HASTE sai pela quina da ponta (miter) — haste com ponta cega (butt) terminando
  no vértice (`formas._seta_diag(..., limpa=True)`).
- D16 Contorno recuado NÃO concêntrico: meia-lua/entalhe/encaixe que desce junto com o recuo fica 2× mais funda na linha
  de dentro; fio interno não paralelo ao externo (escudo); detalhe (picote, fio) que cruza ou tangencia a linha de
  DENTRO do contorno duplo.
- D17 Número, rótulo ou MEDIDA que MENTE: escreve R112 onde o gerador prendeu 85; "raio 56" onde o desenho tem 17; ponta
  redonda de arco/barra passando do valor (2/3 que mede mais); marca de tempo no centro da célula em vez da borda;
  porcentagem sem sentido (67% de noite 2 de 3). O valor escrito sai da geometria final, depois de todo clamp.
- D18 Furo, corte, fio interrompido ou "abertura" PINTADO com a cor do fundo (retângulo tapando a linha, triângulo do
  canto descolando, picote, nó vazado, miolo de marcador): no fundo oposto vira caixa/mancha. Buraco = geometria,
  máscara, clip ou entalhe semicircular no próprio contorno; fio interrompido de verdade.
- D19 Tinta falhada (ruído) em ÁREA CHEIA grande vira mancha de sujeira → falha só na borda/fios ou bem fina.
- D20 Texto em anel fechado à força com tracking enorme (letras soltas) → ajustar corpo, raio ou repetições.
- D21 Texto em arco > ~150° encostando no separador/ponto do selo → limitar varredura; separador no meio do vão.
- D22 Ponta solta: cordão/fio que termina no ar sem motivo.
- D40 Concordância que não cabe: curva côncava + canto convexo (ou dois raios) que consomem mais que o comprimento
  disponível → contorno com bico/laço ("tinta fora da caixa" é o sintoma). A aba sai ≥ 2 raios e fica ≥ 2 raios longe
  dos cantos.

### Padrão, borda e texto repetido
- D23 Texto repetido em faixa/fita/marquee cortado pela borda ou sumindo embaixo de outra faixa no meio da palavra →
  o texto CABE no trecho visível (vão ajustado) e as pontas caem no meio de um vão.
- D24 Padrão (bolinha, ponto, hexágono, xadrez, losango, listra) com pedaço fatiado na borda ou corte assimétrico → só
  peças inteiras, rede centrada com margem; número inteiro de casas; borda passando pelo centro da fileira. Escala com
  linhas-mestras: as quatro existem (1, 10, 100, 1000) e nenhuma cai na borda cortada.
- D25 Corte "quase": letra cortada 5–10% só de um lado parece acidente → cortar ≥ 15% e simétrico, ou não cortar.
- D26 Ponta de seta/objeto aparecendo como lasca (< 30%) na borda → sangrar pelo outro lado ou mostrar ≥ 50%.

### Texto, rótulo e unidade
- D27 Rótulo que precisa ser lido com maiúscula < 25 px no tamanho natural (achado: 6 a 17 px em quase todos os dados).
  Medir a maiúscula de cada chamada; se não cabe: encurtar, usar a display condensada, tirar — ou a PEÇA CRESCE
  (cartão, etiqueta, módulo do código) para caber o texto; nunca o texto encolhe. (Numeração/coordenada de grade
  14–18 px é anotação técnica, não rótulo de leitura.)
- D28 Objeto que vira outro aos olhos do leigo (prendedor de papel que parece bolsa; cone de contorno que lê "A");
  objeto em posição fisicamente impossível (fio de prumo deitado) → remover ou redesenhar.
- D29 Folga de legenda contada da linha de base em vez da TINTA mais baixa: glifo que desce ("/" do numeral grande, Q,
  parênteses) risca a palavra de baixo ("NO|TES"). Medir pelo ponto mais baixo da tinta.
- D30 Cabeçalho centrado numa célula que o empurra para fora da borda do elemento e desalinha do título/letras de
  linha: cabeçalhos e título compartilham a MESMA borda esquerda; rótulos de linha de larguras diferentes vão
  centrados numa coluna fixa (não encostados à direita).
- D31 Número e unidade em colunas misturadas: o número de uma linha cai na coluna da unidade das outras. Número =
  coluna própria alinhada à direita; unidade = coluna colada (vão curto fixo).
- D32 Tabela mais estreita que o próprio título (ou título invadindo a margem): fios e colunas na largura da tabela e
  título menor que ela (ou fios na largura do título).
- D33 Código/rótulo que só lê ampliado: conferir a leitura (e o scanner, nos códigos) também no tamanho natural, zoom 1.
- D34 Legendas vizinhas que se encostam ao trocar abreviação por palavra por extenso ("HORAS"+"MINUTOS"): medir a
  largura da legenda contra a coluna ANTES de trocar.
- D35 Unidade ou abreviação errada: SI em maiúscula em legenda (MM, KG, CM, S → mm, kg, cm, s; "L" de litro e "mmol/L"
  são exceção), letra única ambígua ("M" = minuto, metro, mês → d, h, min, s), abreviação inventada por truncamento
  ("TRAN.", "DELO.") → nome inteiro ou a forma usual.
- D42 Hierarquia de texto invertida: palavra de apoio grande e a de ação pequena ("AO" enorme + "VIVO" pequeno).

### Instrumentos, peças reais e leitura
- D36 Ponteiro, braço ou raio da grade atravessando o numeral; peça semitransparente deixando numeral ou fio
  "fantasma" aparecer através da peça (braços opacos; sem número sob braço; raios param antes da faixa de números).
- D37 Ponta de peça aparecendo no pivô/encaixe (braço fixo saindo pelo fulcro; haste pela quina).
- D38 Chamadas cruzando outras chamadas ou membros; contorno de seleção invadindo as células vizinhas.
- D39 Bordas coincidentes de formas diferentes (contínuo sobre tracejado): projeção que separa as duas.
- D41 Objeto real com medida/proporção errada (polaroide 88 × 107 mm, anilha IWF 450 mm, goniômetro, prancheta):
  usar a medida da fonte e citá-la no log.
- D43 Efeito que lê como OUTRA COISA: pontinhos brancos sozinhos no escuro = céu estrelado (xerox escuro, poeira leve,
  pó de luz desfocado), vincos curtos = feixes de luz, carimbo disco = lua, tinta de papel 2–4% = nada. Em dúvida,
  trocar de fundo (sujeira escura sobre papel) ou usar um modo que traga assinatura (fio, risco).
- D44 Textura de ruído com trama periódica: `feTurbulence` com `baseFrequency` perto de 1 faz o ruído amostrado em pixels
  "bater" (alias → trama de ~10 px). Medir no Chrome: energia dos 8 maiores picos do espectro (FFT) do ladrilho
  renderizado; ≤ ~1% da energia total e amplitude < 2 níveis = ok (o grão atual mede ≈ 1% a 0,3% por pico).

### Rodada de 11/10 (tarde): assunto, colagem, profundidade, selos, faixas
- D45 Número de escala circular de cabeça para baixo (metade de baixo do círculo, lb no relógio). Texto sempre em pé: gira-se 180° na metade de baixo.
- D46 Abreviação inventada por truncamento ("TRAN.", "DELO."). Nome inteiro (abaixo da faixa se não couber) ou rótulo mais curto REAL; nunca cortar a palavra.
- D47 Traço centrado na borda "sangra" 0,5–1,5 px para fora do alinhamento (tique/marcador da ponta, selo, pílula) e texto com bearing de 1–2 px parece 'quase alinhado'. Tiques e marcadores das pontas por dentro; texto alinhado pela TINTA (esquerda no x, direita no x), não pela caixa da fonte.
- D48 Parte do corpo solta da articulação (cabeça-círculo que não encosta no pescoço, 0,016 H de vão). Peça articulada encosta: elipse de topo ao queixo.
- D49 Rótulo de fase de duração zero empurrado para fora do seu segmento, ou rótulo tangente a um fio vizinho. Fase zero vai para uma 2ª linha presa ao marcador por fio; o rótulo que começa no mesmo x ganha folga.
- D50 Tabela com colunas de largura fixa: texto longo invade a coluna vizinha ("LEVANTAMENTO TERRA" encostando no "3"). Colunas medidas pelo conteúdo; o corpo encolhe até a coluna de preencher caber.
- D51 Peça encostando em outra por 0–1 px (peso do prumo × maléolo; cursor × rótulo). Folga ≥ 3 px ou lado oposto — 'encosta' lê como erro de render.
- D52 Marcas de medida de 4 px que somem (pegada da barra a 910 mm). Marca que precisa ser vista tem ≥ 12 px de altura (anel que abraça a haste) e linhas de chamada.
- D53 Base de alça/aba vazando para fora do corpo (kettlebell: a quina da alça saía do círculo por 2 px). Pontos de junção dentro do corpo (checar a largura do corpo na altura da junção).
- D54 Ícone/seta na MESMA cor do disco ou do botão que a contém (sumiu) e anel/estado de foco sem contraste: conferir cor do glifo contra o fundo IMEDIATO de cada estado (normal · pressionado · foco). Texto branco sobre acento dourado e acento sobre papel dão ~2:1 → texto escuro (`sobre_acento`) ou barra de acento com texto escuro.
- D55 Corte decidido de palavra/letreiro que tira a leitura (≥ 15% de cada lado vira "AU VIVU" e parece falha de render, D1): testar a 100% e a 25%; se não lê, não cortar nem fatiar — remover. Corte "decidido" só vale se a palavra continua legível.
- D56 Fio/aro "paralelo" feito com uma 2ª forma menor não é paralelo (escudo: na ponta fica mais perto que nos lados) → traço largo da própria forma recortado por clipPath e um traço menor na cor do fundo por cima (fio concêntrico em todo o contorno).
- D57 "Repetição" com UMA ocorrência só (marquee de 520 px com uma palavra) lê como etiqueta, não como faixa corrida: escolher o corpo para ≥ 2 repetições com vão de 0,45–1,4 × o corpo (`_cap_para_n`).
- D58 Listras inclinadas dentro de um retângulo reto (ou círculo) deixam lascas finas e longas nos cantos (D24): girar o CONTÊINER, deixando as listras paralelas às bordas, com nº par de passos (bordas no centro de uma listra).
- D59 Anel de foco/contorno externo calculado só em volta do corpo fica tangente à sombra dura de um lado (1,5 px) e folgado do outro (3,5): o anel envolve corpo + sombra, folga igual dos 2 lados (D9).
- D60 Gradiente de padrão: pontos < 1,4 px viram poeira/sujeira e fileiras distantes de perspectiva viram tracejado (moiré) → piso mínimo de raio e névoa no horizonte; acento/til/cedilha: respiro vertical medido pela TINTA (≥ 8 px), nunca pela altura da maiúscula; texto em arco ≤ 135° (separador no meio do vão) e anel fechado por corpo+repetição (tracking 0,05–0,20), nunca esticando o espaçamento.
- D61 Material translúcido (fita, vidro) com "linhas internas" regulares: lê pauta de caderno; e sem borda some no fundo oposto. → brilho em 1–2 faixas diagonais + borda dupla (fio escuro por fora, claro por dentro) + sombra curta.
- D62 Rasgo com dente em zigue-zague regular (mesmo passo e fundura). → espaçamento e profundidade sorteados, um dente fundo de vez em quando; nunca passo fixo.
- D63 Contorno de adesivo recortado com FRESTAS (sliver de fundo dentro do bojo, entre terminal e corpo da letra: stroke + fill deixam vazar). → união glifo + faixa (skia-pathops), descartar os contornos de sentido contrário (buracos): o corte real cobre o miolo.
- D64 Franja/contorno claro aparecendo por baixo do papel em borda RETA (anti-aliasing do mesmo contorno duplicado). → o contorno de baixo só existe onde há rasgo; nas bordas retas recuar ≥ 2 px para dentro.
- D65 Espinho no canto de papel rasgado: o canto fica parado enquanto a vizinhança é deslocada. → amplitude do rasgo com envelope que vai a zero nos ~12% de cada ponta.
- D66 Esquema de jornal com colunas de alturas diferentes ou retícula de foto com ponto cortado na borda. → a coluna sem foto ganha as linhas que a foto ocupa; retícula com caixa = número inteiro de células (ladrilho alinhado à origem da caixa, pontos inteiros).
- D67 Furo pintado de cor (perfuração do filme, ilhós) em vez de furo. → caminho composto evenodd (corpo + furos); perfurações simétricas em volta do centro do quadro (8 por quadro, passo 4,75 mm); numeração de borda centrada na margem de fora (0–2 mm) com folga ≥ 0,5 mm dos furos.
- D68 Cordão/barbante que termina no ar e é da cor do papel (some no claro). → laço fechado saindo do ilhós, em cinza de apoio (aparece nos dois fundos), espessura ≥ traço.
- D69 Marcador "só de fio claro/branco" (índice contorno, quadrado, etiqueta) que some no fundo claro. → corpo escuro (cor do fundo da ficha) + fio claro; quando o corpo é claro, contorno escuro a 50–60% (invisível no escuro).
- D70 Raio de aba/pasta maior que a metade da altura (clampa em silêncio e vira outro raio). → usar `raio_sm` só onde cabe (≤ metade do menor lado); tab de pasta com altura calculada pelo texto. Raio concêntrico de borda de adesivo (corpo + espessura) conta como derivado, não como raio fora da escala; o corpo é que tem de estar na escala (raio_sm = 16).

## Numeração antiga → nova (para ler logs e commits antigos)
| era | agora | assunto |
|---|---|---|
| D1–D14 | D1–D14 | iguais (D6, D9, D10, D11, D12, D14 ganharam exemplos) |
| D15 (R2) | D15 | seta com toco |
| D16 (R2) | D16 | contorno recuado não concêntrico |
| D17 (R2) | D17 | número/rótulo que mente (+ D-R4c) |
| D18 (R2) | D18 | máscara na cor do fundo (+ D-R4a, D79 dados) |
| D19–D22 (R3) | D19–D22 | tinta falhada · anel · arco · ponta solta |
| D23–D26 (R1) | D23–D26 | faixa cortada · padrão fatiado · corte quase · lasca |
| D-R4a | D18 | furo/corte pintado com a cor do fundo |
| D-R4b | D27 | rótulo < 25 px |
| D-R4c | D17 | medida que mente |
| D-R4d | D28 | objeto que vira outro |
| D70 (dados) | D29 | folga pela tinta, não pela base |
| D71 | D30 | cabeçalho e título sem borda comum |
| D72 | D31 | número e unidade em colunas misturadas |
| D73 | D32 | tabela mais estreita que o título |
| D74 | D27 | peça cresce, texto não encolhe |
| D75 | D33 | só lê ampliado |
| D76 | D34 | legendas que se encostam |
| D77 | D11 | marca apagada some a 25% |
| D78 | D35 | abreviação de uma letra ambígua |
| D79 | D18 | picote = entalhe no contorno |
| "defeitos novos" de assunto.md | D12, D14, D28, D35–D39, D41 | ver acima |
| (texturas/grades, 11/10) | D6, D9, D10, D24, D36, D43, D44 | ver acima |

## Numeração dos logs de 11/10 (tarde) → oficial
Cada log em `_revisao/<família>.md` usou numeração local (agentes em paralelo). O número oficial é o da coluna da direita.

| log | número no log | oficial |
|---|---|---|
| assunto | D27 · D29 · D34 · D35 · D37 | D36 · D37 · D38 · D39 · D38 |
| assunto | D30 · D42 (número/cor que mente) | D17 |
| assunto | D31 (unidade SI minúscula) | D35 |
| assunto | D32 · D33 · D49 (vira outra coisa / silhueta errada) | D28 |
| assunto | D44 (arestas que param antes) | D22 |
| assunto | D47 · D48 (texto pequeno / espremido) | D27 |
| assunto | D28 · D36 · D38 · D39 · D40 · D41 · D43 · D45 · D46 | D45 · D46 · D47 · D48 · D49 · D50 · D51 · D52 · D53 |
| profundidade · selos · faixas | D50–D56 | D54–D60 |
| colagem | D53 (canto com triângulo da cor do fundo) | D18 |
| colagem | D57 (medida errada) · D59 (texto da etiqueta) | D41 · D27 |
| colagem | D50 · D51 · D52 · D54 · D55 · D56 · D58 · D60 · D61 · D62+D63 | D61 · D62 · D63 · D64 · D65 · D66 · D67 · D68 · D69 · D70 |
| dados | D27–D35 (já oficiais) | iguais |

(Na tabela "era → agora" acima, `D70`–`D79` são os números ANTIGOS do log de dados, não os oficiais D70.)
