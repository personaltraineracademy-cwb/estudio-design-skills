# Repertório · Tipografia

Referências públicas que o estúdio julgou bom ou premium, destiladas em princípio + medida. Formato e regras:
`LEIAME.md`. Referência é régua, não molde: extrair o princípio e superar, nunca copiar a forma.

### TP-01 · Uma família variável fazendo todas as vozes — premium
- Fonte: https://gsaweb.com.br/ · licença/uso: só estudo
- O que é: display unicase variável (peso 200–900, largura 50–150) para todos os títulos + sem-serifa geométrica no texto.
- Princípio: hierarquia por EIXO (peso × largura), não por troca de fonte; a 1ª linha do título "fantasma" (tinta 32%) e a 2ª cheia criam leitura em 2 tempos; o sinal "+" ganha largura 100 para não sumir.
- Medidas: H1 900/50 `clamp(48,6.4vw,140)` entrelinha .88 · H2 700/70 76 px .92 · H3 500/90 30 px · número 800/85 63 px · sinal 700/100 a ½ do número · corpo 15–17/1.5 · rótulo 10–10,5 600 +.2–.3em · botão 10,5 700 +.2em.
- Por que converte/encanta: Ch · Id (4 papéis, 1 arquivo).
- Como aplicar na nossa versão: escolher display variável com eixo de largura (checar no Adobe antes); mapear papel → (peso, largura) numa tabela de tokens.
- Não copiar: o par exato.
- Tags: tipografia · eixo variável · título em 2 tempos

### TP-02 · Uma família larga faz todos os papéis — bom
- Fonte: https://lab.rodrigofenner.com.br · licença/uso: só estudo
- O que é: grotesca larga de cantos superelípticos (Kurdis, comercial; no Adobe a parecida é Termina; grátis Hubot Sans wdth 125) em 400/600/700.
- Princípio: largura = voz (larga = técnica e estável); varia só peso, tamanho e caixa; título com 2 linhas forçadas vira bloco; o token "apagado" muda de tom em cada fundo para manter AA.
- Medidas: H1 56→33,6 · H2 41,6→28 · número-herói 60 (−0,03em) · depoimento 33,6/600 · afirmação 28,8 · corpo 16 · chapéu 12 +0,22em; títulos 1,08 e −0,02/−0,03em; texto 1,6; 3 cinzas; apagado 5,8:1 no carvão cairia a 3,6 no navy → troca para 6,7:1; único título fino (400) mora dentro do mockup do app.
- Por que converte/encanta: Le 4 · Ch 4 — uma voz, zero ruído.
- Como aplicar na nossa versão: escolher a largura da família pela personalidade do cliente; 1 token "apagado" por fundo.
- Não copiar: a combinação fonte larga + laranja.
- Tags: educação · fonte única · largura como voz

### TP-03 · Números de painel e palavra-chave viva — bom
- Fonte: https://jdpmed.com.br · licença/uso: só estudo
- O que é: Inter variável com `ss01`+`cv01` (dígitos abertos, 1 com base) e 1 palavra por título em itálico com brilho que corre.
- Princípio: a variante de glifo dá "sotaque" de painel aos números sem trocar de fonte; quem lê só os destaques entende a página.
- Medidas: H1 48/1,08 · H2 38/1,12 peso 500 −0,03em balance · número 44/600 · rótulos 10,5–11 +0,14–0,2em; brilho: degradê 220% em `background-clip:text`, 7 s ease-in-out; defeitos: itálico sintético (~14°, sem arquivo) e destaque `inline-block` solta o ponto final no celular.
- Por que converte/encanta: Le 3 · Ch 3.
- Como aplicar na nossa versão: procurar variantes ss/cv da fonte do cliente para números; carregar o itálico real; destaque `inline`; sobre escuro a palavra vira o acento.
- Não copiar: o degradê verde→oliva.
- Tags: saas · variantes OpenType · destaque de palavra

### TP-04 · Serif display com 1 trecho em folha metálica — premium
- Fonte: https://timmeventos.com.br/ · licença/uso: só estudo
- O que é: títulos em serif display com o 2º trecho em itálico pintado de degradê metálico (texto recortado).
- Princípio: acabamento especial só no trecho de valor de cada título; folga de pintura para o itálico não ser cortado pela caixa.
- Medidas: Meno Banner 700 (Adobe Fonts, incluída); títulos clamp(38, 4.8vw, 64), entrelinha 1,05, −.015 em; H1 .95 / −.025 em; número herói 320 px, entrelinha .8, −.04 em; folga padding .12/.14 em + margem negativa igual + box-decoration-break: clone (cada linha quebrada repete a folga); rótulos 11–13 px, .16–.3 em.
- Por que converte/encanta: Ch — o metálico marca sentido, não decoração.
- Como aplicar na nossa versão: 1 trecho por título no acabamento de prestígio da marca; conferir itálico e acento cortados a 360/390.
- Não copiar: Meno + folha de ouro.
- Tags: serif · texto recortado · itálico

### TP-05 · "Grito condensado, conversa redonda" — bom
- Fonte: https://combo.brandsdecoded.com.br/black-brands/b · licença/uso: só estudo
- O que é: display condensado 900 caixa alta + corpo geométrico minúsculo e arejado.
- Princípio: tamanho do título = % da largura da coluna com quebra manual (bloco sem viúva); número herói em pirâmide de 3 andares com a mesma largura.
- Medidas: H1 15,5% da coluna (81,8 px em 528), 14% no celular, entrelinha .8; "2 ANOS" 160 px entre linhas de 40 e 38,4 px (0,24 × = mesma largura, salto 4:1); corpo 18–25 px / 1,4–1,6, −.01 em; botão 800 caixa alta +.02 em; escala fluida passo 1,25; títulos balance, parágrafos pretty, ≤ 65 caracteres.
- Por que converte/encanta: Le 4 — lê em 1 s.
- Como aplicar na nossa versão: título em cqw da coluna com quebras escolhidas pelo português; pirâmide para o número do cliente.
- Não copiar: Fixture Condensed (paga e fora do Adobe; no plano: Roc Grotesk Compressed ou Bebas Neue Pro).
- Tags: condensado · título na largura · pirâmide
