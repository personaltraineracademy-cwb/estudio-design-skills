# Sistema de campanha: muitas peças variadas, únicas e coerentes

Casos de referência: Wrapped, Paris 2024, Copa 26, Whitney, Mailchimp, Google I/O, Itaú, Globo…

## Princípios
- **Núcleo fixo × camada solta.**
  - Fixo: logo, cores (por papel), tipografia, tratamento de foto e o DNA de forma.
  - Solto: composição, escala, corte, camadas, arquétipo.
- **A variação tem que SIGNIFICAR algo:** noite, pessoa, fase, produto. Variação aleatória (40 mil logos do MIT Media
  Lab) "parece tudo igual"; variação demais vira bagunça (algumas críticas ao Wrapped).
- **Kit simples** (Paula Scher): o kit é simples porque o trabalho dele é fazer uma coisa complexa.
- **Teste "qual não pertence":** olhe o kit como num teste de QI e ache a peça fora da família.
- **Foto e gráfico do mesmo mundo:** um tratamento só. Na Copa 26, o troféu fotográfico destoava do resto chapado.

## As 9 camadas de um sistema de campanha
1. Conceito.
2. Kit de peças.
3. Grades por formato.
4. **Arquétipos de composição.**
5. Regras de variação.
6. Direção de imagem.
7. Movimento.
8. Toolkit/modelos.
9. Governança (o que é fixo, o que é livre, quem aprova).

Composição é elemento próprio (a Uber lista composição ao lado do logo). **Tratar composição como UM template é o
erro mais comum.**

## 22 arquétipos de composição
Cada um tem: quando · regras · parâmetros · ligação com os dispositivos da marca.

| # | Arquétipo | Regra central |
|---|---|---|
| 1 | Palavra gigante cortada | 1 palavra a 120–200% da largura; corte num lado; ≥ 60% da letra legível |
| 2 | Pessoa rompendo a moldura | o recorte sai do visor/moldura por cima ou pelo lado (≤ 15% da altura) |
| 3 | Texto atrás da pessoa | 3 camadas; a cabeça cobre ≤ 25% da palavra; a palavra continua legível |
| 4 | Tela dividida | 50/50 ou 62/38 (nunca 55/45); cada lado com um tema |
| 5 | Grade de rostos | mesmo recorte, mesma altura de olhos, mesma luz |
| 6 | Número herói | o número ocupa 50–70% da altura; o resto é microtexto |
| 7 | Documento censurado | ficha da oferta com 30–60% das linhas tarjadas; o visível conta a história |
| 8 | Revelação antes/depois | 2 cards idênticos, só a tarja muda (mesma semente) |
| 9 | Ingresso/agenda | picote, canhoto, código; UMA informação dominante |
| 10 | Lower third como layout | a peça é um frame da transmissão: bug + REC + lower third |
| 11 | Contagem regressiva | o número é o foco; a unidade é pequena; formato de timecode |
| 12 | Citação | ≤ 12 palavras; aspas penduradas na margem; 1 palavra tarjada |
| 13 | Espaço negativo extremo | 80–90% vazio; 1 elemento pequeno; texto mínimo num canto |
| 14 | Visor em tela cheia | cantos do visor nas margens seguras; a pessoa vista pela câmera |
| 15 | Placar/torre | lista vertical com 1 linha destacada |
| 16 | Faixa "AO VIVO" | faixa que atravessa e sangra dos dois lados |
| 17 | Folha de contato | 4–9 frames P&B; 1 circulado/ampliado |
| 18 | Close extremo cortado | rosto cortado na testa e no queixo + faixa curta. **Nunca tarjar os olhos** (lembra suspeito) |
| 19 | Manchete tipográfica pura | só tipo e tarja; 3–6 palavras |
| 20 | Moldura/janela | estrutura igual, conteúdo diferente (container) |
| 21 | Padrão de tarjas | tarjas de comprimentos variados = "linhas censuradas" como textura |
| 22 | Mock de interface | bolha/notificação estilizada (sem copiar a UI real pixel a pixel) |

**Compatibilidade por formato:**
- 9:16 aceita 1, 3, 11, 14 e 16;
- checkout aceita 6, 9, 16 e 21;
- overlay aceita 10, 11 e 14;
- todos aceitam 13.

## Eixos de variação (com limite)
| Eixo | Valores | Limite |
|---|---|---|
| Arquétipo | os 22 | compatível com o formato; nunca igual em sequência |
| Escala do herói | pequeno 8–20% · médio 35–50% · gigante 120–200% (sangra) | só 1 gigante por peça |
| Corte | inteiro · 1 lado · 2 lados | ≥ 60% da palavra legível; nunca cortar o rosto nos olhos |
| Âncora | 9 da grade 3×3 + sangra | logo só nos 4 cantos ou no eixo central |
| Papel de cor | fundo/figura/acento trocam dentro do tema | trabalhar com PAPÉIS, não com hex; medir contraste |
| Tema | aprovados | pode amarrar tema a noite/pessoa/fase |
| Camadas | texto atrás/na frente da pessoa | a tarja sempre na camada de cima |
| Rotação | 0 · ±4° · 90° | no máximo 1 elemento girado |
| Tipografia | display gigante · manchete · ficha · timecode | ≤ 2 famílias, ≤ 3 tamanhos |
| Dispositivo de sigilo | nº, comprimento, estado (tarjado/revelado) | SEMPRE cobre texto real; nunca enfeite vazio |
| Dispositivo de transmissão | cantos, ●, timecode, bateria; inteiro ou parcial | ≤ 1 visor por peça; timecode coerente com a hora real |
| Foto | busto, close, corpo; olhar | olhar para dentro da peça; mesmo tratamento em todas |
| Densidade | 1 · 2 · 3 blocos | limites de texto por formato |

## Gerar muito, publicar pouco
1. **Plano:** peça × formato × arquétipo × tema × semente. Semente hierárquica: campanha → peça → formato. A peça
   aprovada vira receita e é refeita em todos os formatos.
2. **Gerar** 3–10× o necessário.
3. **Filtro automático:** `Peca.qa()` zerado, além de contraste, limite de palavras e foco único.
4. **Arena** (brand-system `arena.py`): juízes diretor + público, às cegas, nota absoluta ≥ 7.
5. **Seleção com diversidade:** os melhores, penalizando o parecido (mesmo arquétipo + mesmo tema, ou CLIP > 0,9).
6. **Folha de contato da SÉRIE:** a pessoa aprova o conjunto.

## Transmissão ao vivo (pacote mínimo e como vaza para o estático)
- **Durante a aula:** movimento PRODUTIVO (discreto): bug no canto, lower third só nas entradas.
- **Na revelação:** movimento EXPRESSIVO, um momento só: a tarja desliza ou rasga e revela, e a tela de oferta usa o
  mesmo layout do checkout.
- **Pacote mínimo:**
  - bug;
  - lower third (2 linhas; nome ≥ 4% da altura);
  - tela de espera com contagem;
  - stinger da tarja (1–2 s);
  - tela de oferta;
  - "voltamos já";
  - end card com a próxima noite.
- **Área segura:** título em 90% (96 × 54 px em 1080p), ação em 93%.
- **Vazar para o estático:** timecode real no lugar da data; bug como assinatura; lower third como bloco de nome;
  frame de stinger congelado como transição de carrossel.

## Proibições (lint)
- O template "logo no alto + pilha de texto + foto à direita + barra de CTA" em mais de 20% da série.
- 2 focos.
- Texto na zona da interface do app.
- Tarja sem texto embaixo.
- Foto colorida misturada às P&B.
- Mais de 2 famílias.
- Contraste < 4,5:1 no texto pequeno.
- Olhos tarjados.
- Mesmo arquétipo em sequência.
- Selos de desconto em estrela.
- Glow em texto.
- Sombra genérica.

## Mapa de arquivos do sistema (no projeto)
| Arquivo | O que contém |
|---|---|
| `sistema/campanha.json` | fatos, copy aprovada, fases, proibições |
| `sistema/formatos.json` | tamanhos e zonas seguras (`compor.FORMATOS`) |
| `sistema/grid.json` | colunas, margem, linha de base, âncoras e posições permitidas do logo, por formato |
| `sistema/temas.json` | temas por PAPEL |
| `codigo/elementos.py` | o kit |
| `codigo/arquetipos/` | 1 função por arquétipo (slots, foco, palavras, formatos, eixos) |
| `sistema/plano.json` | matriz da série com sementes |
| `qa/` | relatórios do verificador |
| `manual/` | o guia |

## Uma fonte da verdade por decisão
Cada decisão (fonte e peso, cor por papel, raio, copy) mora em UM lugar e o resto lê de lá: `brand.json` (marca) →
código (`pecas.py` lê os temas) → `campanha.json` só para a copy e o calendário. Erro típico: `campanha.json` diz
peso 500 e o código usa 800 — ao decidir, atualizar a fonte da verdade e procurar as cópias.
