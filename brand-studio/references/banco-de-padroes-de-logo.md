# Banco de padrões de logo (aprovados em projetos reais, anonimizados)

Padrões que passaram pela aprovação de clientes reais num ecossistema de educação (marca-mãe + cursos, campanhas,
eventos, produtos digitais). Use como **gramática**, nunca como forma pronta: o símbolo de cada marca nasce do
assunto dela. Diagramas: `assets/padroes-logo/gramaticas-de-lockup.svg` e `assets/padroes-logo/key-visuals.svg`.

## Contents
- Gramáticas de lockup (L01–L14)
- Símbolos: o que funcionou (S01–S07)
- Sistemas que multiplicam um logo (M01–M04)
- Key visuals que funcionaram (K01–K05)
- Clichês já reprovados
- Defeitos de craft achados em logos reais
- Fórmula de cor que funcionou

## Gramáticas de lockup
| Id | Padrão | Por que foi aprovado | Quando usar | Armadilha | Gerar |
|---|---|---|---|---|---|
| L01 | **Nome manda**: sans pesada, caixa alta, 2–3 linhas formando bloco justificado | lê de longe, ocupa o espaço como um bloco só | marca tipográfica, campanha, evento | justificar cortando letra ou esticando a 3ª linha | `lockup.py` |
| L02 | **Etiqueta com texto vazado** na mesma linha do nome | a mesma palavra vira evento, edição virtual, congresso só trocando a etiqueta | marcas com várias edições/versões | etiqueta abaixo de 48 px vira textura → versão curta | `lockup.py` `"bar": true` |
| L03 | **Barras que justificam o bloco** (chanfradas ou retas) | bloco fecha retangular, muito "ownable" | nome com linhas de larguras diferentes | barra competindo com o nome (deve ser mais leve) | `lockup.py` `"fill_bar"` |
| L04 | **Linha vertical divisória** símbolo \| nome ou campanha \| produto | co-branding limpo, escala para dezenas de produtos | campanhas sobre vários produtos | divisória mais pesada que o traço do texto | `lockup.py` `"cobrand"` |
| L05 | **Endosso espaçado** da marca-mãe em caixa alta sob uma linha | diz "de quem é" sem disputar com o nome | sub-marca, evento, curso | endosso grande demais; letterspacing que vira letras soltas | `lockup.py` |
| L06 | **Quebra de palavra em grade** (PALA / VRA) | impacto de cartaz, símbolo nasce da grade | evento, nome curto de 6–8 letras | quebra que forma outra palavra ou som estranho | spec manual |
| L07 | **Condensada × estendida**: nome alto e condensado, descritores largos | tensão volume × largura dá corpo ao bloco | nome longo + descritor | descritor em tamanho ilegível | `fonts.py` + `lockup.py` |
| L08 | **Contorno em pílula entrelaçado** ao texto | luxo acessível, vira padrão de fundo | campanha sazonal premium | virou assinatura de uma marca — não repetir no mesmo cliente | `lockup.py` `"pill"` |
| L09 | **Numeral próprio** (algarismos desenhados: terminais cortados, 0 como anel) | o número vira o ícone da campanha | campanha anual, aniversário, edição | numeral genérico de fonte = sem ganho | construção manual |
| L10 | **Entalhe na haste** de letras-chave (ex.: V que vira articulação) | gesto tipográfico próprio, ligado ao saber do assunto | quando o assunto tem uma forma técnica | entalhe some pequeno → testar a 24 px | construção manual (logo-design) |
| L11 | **Símbolo na altura exata do bloco** à esquerda | lockup horizontal estável | símbolo + nome de 2–3 linhas | símbolo em traço fino ao lado de nome pesado (peso desigual) | `lockup.py` |
| L12 | **Palavra-chave em cor** (só 1 palavra) | a promessa salta na leitura | produto digital, oferta | duas cores competindo | `lockup.py` |
| L13 | **Palavra vazada numa tarja de censura** (furo real; símbolo = a tarja com as iniciais vazadas) | o logo esconde/revela; a tarja vira elemento (valor tarjado, data em tarja) | oferta secreta, revelação, lançamento | letras "afundadas"/cortadas na tarja perdem leitura → vazar inteiras com respiro igual | `lockup.py` `"bar": true` |
| L14 | **Nome dentro de visor de câmera** (cantoneiras + ponto de gravação no lugar de um sinal) | diz "ao vivo" sem ícone; o visor vira moldura de peça e de página | evento transmitido, live | rótulo dentro da curva da cantoneira; "ao vivo" estourando a moldura → linha própria | spec manual |

## Símbolos: o que funcionou
| Id | Padrão | Por que funcionou | Cuidado |
|---|---|---|---|
| S01 | Geometria sólida com **um corte/gesto** (forma + linhas que irradiam de um ponto) | simples, funciona do favicon ao painel | não virar ícone genérico de setor |
| S02 | **Símbolo que substitui uma letra** do nome | integração forte, memória | a letra precisa continuar legível |
| S03 | **Ilustração monolinear narrativa** (mito/história do nome) | o mais autoral; feminino/masculino sem clichê de silhueta | só quando o conceito pede; testar a 32 px |
| S04 | **Figura que completa a forma** (metade do símbolo é outra coisa) | duas ideias num símbolo só | máx. uma linguagem (não misturar contorno + sólido + anel) |
| S05 | **Símbolo do saber do assunto** (instrumento, medida, lei, protocolo) | só aquele curso/produto pode ter | o público técnico percebe erro técnico (pose, ângulo, escala) |
| S06 | **Monograma em traço espesso** | escala bem, vira avatar | traço ≥ peso da haste do nome |
| S07 | **Letra + a mesma letra girada na mesma haste**, entrando no lugar da letra do nome e descendo abaixo da linha | gesto próprio que gera elementos (eco, padrão espelhado, janela de foto) | girada pequena no meio do texto lê como erro de digitação |

## Sistemas que multiplicam um logo
- **M01 Selo com texto em arco** (marca + nome da área): gera sub-marcas (pós, suporte, lançamentos) **sem logo novo**
  — `seal.py`.
- **M02 Etiquetas modulares** (L02): mesmo nome, várias edições.
- **M03 Co-branding com divisória** (L04): uma campanha, dezenas de produtos.
- **M04 Padrão do símbolo/palavra** e **key visual com formas gigantes cortadas do símbolo**: fundos que não disputam
  com o logo — `pattern.py`, `keyvisual.py`.
Módulo comum para família de produtos (ex.: todos os cursos): mesmo lugar, fonte e proporção do descritor + um gesto
próprio por produto.

## Key visuals que funcionaram (K01–K05)
| Id | Padrão | Por que funcionou | Gerar |
|---|---|---|---|
| K01 | **Logo central sobre luz de estúdio**: cor chapada da edição com poça de luz suave + vinheta; troca só a cor por edição | uma arte vira 3–4 edições sem redesenho | `../direcao-de-arte/scripts/fundos.py` (estudio) + `compose.py` |
| K02 | **Escuro com brilho de canto** + padrão do elemento-assinatura em contorno, tom sobre tom | luxo sem disputar com o logo | `fundos.py` + `pattern.py` (contorno, opacidade baixa) |
| K03 | **Forma gigante cortada do símbolo** atravessando a tela na diagonal, logo no centro; 3 colorways (cor/escuro/claro) | reconhecível no feed só pela forma | `keyvisual.py` (crop/split) |
| K04 | **Símbolo central + padrão tom sobre tom** do próprio símbolo; frase curta em cima à esquerda e assinatura embaixo | sistema simples que aguenta campanha inteira | `keyvisual.py` (pattern/center) |
| K05 | **Formas do símbolo cortadas nas bordas** como moldura (entram pelos cantos/lados), centro livre | enquadra qualquer mensagem mantendo a marca | `keyvisual.py` (frame) |
Selo com texto em arco (M01) também vira peça: o mesmo símbolo com o nome de cada área ao redor = família de avatares.

## Clichês já reprovados (não propor em marca nova)
Montanha para evento "de topo" · punho/foguete/chama para energia · seta saindo de quadrados para crescimento ·
loop de repost para Instagram · C com check para consultoria · casa com linhas de velocidade para consumidor ·
hexágono com linhas · silhueta de atleta posando · braço flexionado (mecânico ou não) · lótus (+ mulher de perfil com
halter) para feminino · rosa "porque é feminino" · repetir o mesmo azul/vermelho de outras marcas do mesmo cliente.
Campanha de desconto: peso de academia como etiqueta de preço (vira cadeado/pavio) · cronômetro "acabando" · faixa de
arte marcial com nó (o nó vira calça) · só o contraste de pesos da fonte (elegante, mas não gera elementos).
O índice CLIP de mercado é quase só tecnologia: em fitness/saúde/educação, `novelty` baixo **não** prova originalidade
— conferir esta lista no olho. Mais em `references/logo-anticliche.md`.

## Defeitos de craft achados em logos reais (checar sempre)
Texto vivo (`<text>`) ou imagem embutida no SVG · letras cortadas para justificar bloco · colisão de kerning em
etiqueta · acento faltando · travessão no lugar de hífen · maiúscula no meio do descritor · bloco meio justificado
(1ª linha solta, 3ª esticada) · silhueta com cara de foto vetorizada (contorno irregular, dedos somem pequenos) ·
símbolo em traço mais leve que o nome (vira ruído < 48 px) · só versões para fundo escuro (falta positivo para
branco) · cor de destaque sobre claro com 2,8:1 · duas cores quase iguais duplicadas (`#EDAC3E` × `#ECAC40`).
Ferramenta: `python scripts/logo_qc.py "*.svg" --sheet qc.png` + `svg_audit.py` (logo-design).

## Fórmula de cor que funcionou
**1 destaque saturado + quase-preto (~#1A1A1A) + claro (branco frio ou creme).** Todo logo em 4 colorways (cor sobre
escuro, positivo, branco, destaque mono) + misto, cada um com o **fundo em que funciona declarado**. Num ecossistema,
listar os destaques já usados e fugir de quase-iguais (5 azuis parecidos = nenhum é da marca).

## Kit mínimo que foi aprovado
Horizontal · vertical · símbolo · wordmark · 4 colorways · padrão · selo (quando fizer sentido) · co-branding com a
marca-mãe · key visual em 1080×1080, 1080×1920 e 1920×1080 · paleta HEX/RGB/CMYK · versão positiva para documento ·
versão curta sem descritor para < 48 px · símbolo testado a 16–32 px · animação curta (campanha/evento).
