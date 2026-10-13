# Dispositivos — catálogo de elementos de identidade (e como gerar cada um)

## Modelos de identidade flexível (Irene van Nes, *Dynamic Identities*, 2012)
Regra: **fixe ≥ 1 componente reconhecível** (tipo, logo, cor, imagem, linguagem, elemento) e deixe os outros variar.
| Modelo | O que é | Como gerar aqui |
|---|---|---|
| Contêiner | forma fixa preenchida por textura/cor/foto (MTV, Melbourne) | silhueta do símbolo como janela (`elements crop`/máscara) + biblioteca de preenchimentos |
| Wallpaper | motivo e paleta fixos, fundo muda (Brooklyn Museum) | logo fixo + fundo gerado (`elements`, `sketch.py`, Gemini) |
| DNA | blocos que se recombinam | `elements modules` + regras de combinação |
| Fórmula | regra fixa gera variações (Google Doodles) | função conteúdo → layout (`apply.py` receitas) |
| Customizado | público/parceiros criam a sua versão (LA28) | template com "vaga" + limites |
| Generativo | dados movem a forma | dados → parâmetros (semente, amplitude, cor) em `sketch.py` |
Operadores de variação (Martins et al. 2019): cor · combinação · posição · repetição · rotação · escala ·
transformação de forma · conteúdo. Consistência por "ingredientes", "regra de variação" ou "control knobs".

## Os 38 dispositivos (→ gerador nesta stack)
**Estrutura e moldura**
1. Logo como contêiner/portal (Museu Nacional/Porto Rocha; Uber/Wolff Olins) → clipPath do símbolo + foto.
2. Palco/moldura paramétrica (The CW/DixonBaxi; GSK "signal") → retângulo/pílula com raios do logo; `elements frame`.
3. Grid modular de uma fonte real (Olympikus: pistas e bandeiras; NYBG: vidraças) → traçar a geometria da fonte →
   subdivisão recursiva.
4. Grid por número simbólico (Malingue: 3 traços = 3 palavras) → nº de letras/sílabas vira divisão.
5. Grid radial + programação criativa (Vanto/Tátil 2026) → grade polar anéis × setores com semente.
6. Grid de pontos/pixels (Nordic Energy Research) → matriz de pontos; raster→pontos (`elements halftone`).

**Forma e símbolo**
7. Biblioteca de formas de UM primitivo (Decathlon L'Orbit; Animade) → `elements explore` (ops booleanas, corte,
   rotação no ângulo do logo); limite N formas.
8. DNA de ângulo e raio (ITVX: raio do X nas 6 fontes) → `elements dna` → itálicos, cortes, cantos, diagonais,
   trajetórias de movimento.
9. Glifo/sinal como símbolo (+ girado = X; "4" próprio do JFK T4) → sinal desenhado em curvas, vira marcador e padrão.
10. Logo como personagem (Animade: laço vira olhos) → contraformas = olhos; pupila = direção.
11. Família de logos (QX: 5 marcas, um esqueleto) → N variantes que preservam a topologia.
12. Mascote feito com o sistema (Duo; Yazio "Yettie") → montado com as primitivas + poses.

**Tipografia**
13. Fonte display própria derivada do logo (Decathlon Sans, Feather Bold, Amazon Logo Sans, GoFundMe Sans) → fonte
    OFL base + terminais/cortes do DNA, glifos alternativos (fontTools FontBuilder/fontmake), tudo em curvas.
14. Tipo variável/elástico (Tempo/Dumbar; Canal Brasil: 6 masters, "caos controlado") → sortear estilo por letra
    dentro de conjunto finito; ≤ 3 estilos por palavra, sem vizinho igual.
15. Uma letra mutável (LA28: o "A" varia) → wordmark com "vaga" de glifo.
16. Tipografia radial/em arco (GoFundMe) → `common.Font.path_on_circle`, `seal.py`.
17. Lockup de frase/assinatura verbal ("Help adds up") → regra fixa de posição/proporção/quebra.

**Cor**
18. Cor por zonas (MotoGP: mãe neutra, submarca ganha faixa do círculo) → faixas de matiz OKLCH por submarca.
19. Paleta contra a categoria (Peloton: lima/lilás/ultramar; ITVX) → mapa de cores dos concorrentes → região vazia.
20. Pares de cor/color-blocking (Jeugdfonds/Dumbar) → pares pré-aprovados com contraste ≥ 4,5 (`palette.py`).
21. Sistema de degradês (Vonage) → interpolar em OKLab; direção = ângulo do logo.
22. Cor por contexto/hora (Paddington Central) → parâmetro t → cor/posição.

**Padrão, dados e geração**
23. Padrão a partir do símbolo (Herman Miller "M"; Penta+) → `pattern.py` (grade, hex, tijolo, meia-volta) e
    `elements repeat`.
24. Rede/linha conectora (rɘ―inc/Pentagram) → nós no grid + arestas no ângulo do logo (Delaunay/árvore mínima).
25. Letras de dados geográficos (Amazônia/FutureBrand) → vetores reais (rios, trilhas de GPS) casados com esqueletos.
26. Gráfico da verdade do produto (Progress Circle) → arco = progresso real.
27. Linguagem de dataviz (Goalkeepers; SCDH/Base) → gramática de gráficos com as primitivas.
28. Formas generativas/evolutivas (Eppo/Moving Brands) → `sketch.py` com sementes e dados.
29. Elementos de patrimônio/arquitetura (MASP: concreto; Museu Nacional) → traçar a geometria → primitivas.

**Imagem**
30. Regras de fotografia (Decathlon sem retoque; Peloton só membros reais, bike fora do centro) → corte fora do
    centro, inclinação = ângulo do logo, LUT, recorte (`imaging.py`), direção no `imagery`.
31. Imagem tratada pelo dispositivo (All 4: a barra de play recorta imagens) → máscara + revelação.
32. Regras de ilustração (Duolingo) → só formas da biblioteca, traço fixo, paleta limitada; Gemini com folha de estilo.
33. Ícones e ilustração técnica (Olympikus: ícones + mono) → grid 24, traço proporcional ao DNA, chamadas + mono.
34. Textura/impressão (riso, desregistro, xerox) → `fx.py`; com parcimônia (riso virou clichê).

**Comportamento**
35. Princípio de movimento = um verbo (órbita; "keep climbing"; inclinar) → curva de easing, direção, duração para
    tudo (`motion` no brand.json; `motion.py`).
36. Dispositivo que vira interface (Transavia: logo como cursor; ITVX) → traço do logo vira sublinhado, divisor,
    barra de progresso, CTA.
37. Contagem/dispositivo numérico (KOKO "Countdown to Live") → numerais próprios como herói (`apply numeral`).
38. Identidade cocriada + arquitetura de submarcas (LA28; Decathlon 85→1) → template de lockup + zona de cor + regra
    de nome.
Também: identidade sonora · filme da marca · selo de certificação (`seal.py`) · sinalização.

## As 12 operações do `elements.py` (gramática de forma)
crop (supergráfico) · contour (eco) · bands (topográfico) · slice (fatias/glitch) · hatch (gravura) · halftone
(retícula por distância à borda) · repeat (rastro, radial, grade) · stack (extrusão chapada) · modules (kit de
partes) · outline (versão linha) · morph (metamorfose entre duas primitivas) · frame (cantoneiras no ângulo do DNA).
Fluxo: `explore` (folha com dezenas de variações) → olhar → escolher 3–6 → registrar em `brand.json.devices` com
**nome próprio + regra de uso** → `build`. Cada dispositivo precisa de regra ("onde, quanto, com o quê"), senão é
enfeite.

## O que faz um sistema "ownable" (dos casos)
Verdade própria, não símbolo da categoria · evoluir o valor de marca antes de trocar · **um movimento ousado e o
resto contido** (Nike Run: 3 âncoras) · contenção (formas que apoiam, não competem) · tensão/contraste · fugir do
"mar de igualdade" de propósito e recusar tropos por escrito · comportamento (movimento, som) acima do desenho
estático · o "estranho" como ativo (&Walsh).
