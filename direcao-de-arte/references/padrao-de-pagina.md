# Padrão de página — metodologia fixa

> Origem: a MESMA classe de erro se repetia rodada após rodada (dobra curta, vazio embaixo, espaçamento diferente em
> cada página, margens desiguais, composição que muda de largura para largura). **Regra: página é um padrão, uma
> metodologia, um passo a passo; só mudam elementos, layout, identidade visual, cores e fonte; espaçamento, dobras e
> metodologia são padronizados.**
> Este documento é o contrato. `paginas-de-captura.md` explica o porquê; aqui está o **como**, igual para qualquer
> cliente, página ou peça web.

## 0. O que é FIXO e o que MUDA

| FIXO em toda página (não negociar) | MUDA por cliente / projeto |
|---|---|
| escala de espaçamento, margens, respiros de seção | identidade: cores, fontes, logo, grão, formas |
| contrato da 1ª dobra (altura, o que cabe, ordem) | o layout/composição escolhida para a dobra |
| mesma composição em TODAS as larguras (só escala) | os elementos gráficos e as fotos |
| um eixo, uma ordem de leitura, uma ideia por tela | a linguagem de movimento (assinatura) |
| grade de verificação (§6) e portão de entrega | a copy (sempre a final do cliente) |

## 1. Tokens (os mesmos em todo projeto; no código: `app/globals.css`)

| token | valor | uso |
|---|---|---|
| `--g1` | 12 px | mesmo grupo (sub↔data, botão↔micro) |
| `--g2` | 24 px | grupos relacionados (cabeçalho↔foto, H1↔sub) |
| `--g3` | 40 px | grupos separados (foto↔H1, data↔botão) |
| `--m` margem lateral | 24 px (< 600) · 40 px (≥ 600) · `clamp(48px, 6vw, 112px)` (≥ 1024) | esquerda = direita, sempre |
| `--gut` | 16 px (< 600) · 24 px | vão entre colunas/cartões |
| `--sec` | 72 px (< 600) · 112 px (≥ 600) · `clamp(112px, 9vw, 144px)` (≥ 1024) | respiro de cada lado da seção (vão entre seções = 2×) |
| `--header-h` | 64 px (< 768) · 72 px | cabeçalho |
| escala | 4·8·12·16·24·32·40·48·64·96·128·160·200 | nenhum outro valor de espaço |
| botão | altura ≥ 60 (principal) / 48 (barra); sombra dura conta na margem (`--sh-x`) | rótulo SEMPRE em 1 linha |
| texto | corpo ≥ 16 px; rótulo mono ≥ 14 px; ≤ 6 tamanhos por página | — |

## 2. A 1ª DOBRA (contrato)

1. **Altura = a tela inteira**: `<section class="est-dobra" data-hero>` = `min-height: 100svh − --header-h`, conteúdo
   **centrado na altura**. A seção seguinte NÃO aparece na 1ª tela (nem o eyebrow da seção). Verificador: erro "dobra 1 CURTA".
2. **Conteúdo único e na mesma ordem**: IMAGEM (a pessoa/produto) → TÍTULO → apoio + data → BOTÃO → micro. Logo só no
   cabeçalho (uma vez); nome da marca não repete no corpo da dobra.
3. **Um eixo**: ou tudo centrado, ou texto à esquerda + imagem à direita com a mesma altura/centro. Nunca camadas
   desligadas, faixa/tira sem origem, bloco solto, texto longe do botão.
4. **A imagem é o maior elemento** e cresce com a janela, limitada pela altura (título + botão sempre cabem):
   `width: min(100%, 940px, max(520px, (100svh − 465px) × 1.8))`.
5. **Mesma composição em celular, tablet e desktop**; muda só a escala e a coluna (botão em largura total < 600).
6. **Zona do polegar**: botão principal termina antes de 88% da altura da tela em 360×740.

## 3. Seções abaixo da dobra

- Padding vertical = `--sec` de cada lado; título da seção ↔ conteúdo = `--g3`; item ↔ item = `--g2`.
- Ritmo: fundo alterna (escuro/claro ou papel/tinta) a cada seção; uma mensagem por seção; ≥ 38% de área vazia por tela.
- Container único (`max-width` + `--m`); cabeçalho e conteúdo com a MESMA margem; colunas com topo e base alinhados.
- Listas/cartões: vão `--gut`; cartão com padding ≥ 24 (32 no desktop).
- Final: **uma ideia só** (frase + botão); sem textura atrás de texto.

## 4. Responsividade (passo a passo)

1. Desenhar a composição UMA vez, em coluna central, a 390 px; ela é o padrão.
2. Escalar com `clamp()`/container queries (`cqw`), nunca `100vw` em layout (a barra de rolagem tem 15 px).
3. Em ≥ 1024 só aumentar escala e centralizar; se virar 2 colunas, justificar por escrito e manter foto/texto no mesmo
   centro e altura.
4. Testar: 320, 360, 375, 390, 414, 430, 600, 768, 1024, 1280, 1366, 1440, 1536, 1920, 2560 + paisagens 667×375…1024×600.
5. Foto recortada centrada pela TINTA (bbox do alfa), não pela caixa.

## 5. Movimento (padrão)

- Sempre ligado; `data-movimento` total/suave/parado (suave quando o sistema reduz); uma linguagem por página.
- Só `transform`/`opacity`/`clip-path`; entra uma vez; ≤ 0,7 s; nunca no H1, na foto do LCP nem no CTA (exceto a seta).
- Estado natural do CSS = estado final (`animation-fill-mode: forwards`, nunca `both`).

## 6. Passo a passo de produção (sempre nesta ordem)

1. Entradas: copy final, logo + variações, fotos reais recortadas (centradas pela tinta), cores/fontes do cliente.
1b. **ELEMENTOS ANTES DA PÁGINA**: se o kit de elementos do cliente (biblioteca `ornamentos`, séries, selos, faixas,
   números) ainda não está feito e revisado, fazer ANTES; depois inventariar o que serve para a página (fundo,
   divisores, selos, faixa, numerais, cantos) e usar. Página montada sem o kit refaz elemento no CSS e deixa o
   acervo sem uso. Quantidade MÉDIA: só o que a página vai usar.
2. Escolher UMA ideia gráfica da dobra (ex.: holofote, painéis, ficha) — IA só gera cenário/complemento (Nano Banana 2.1).
3. Montar a dobra no contrato do §2, em 390 px; escalar (§4).
4. Montar as seções no §3 com os tokens do §1.
5. Movimento (§5).
6. Verificar: `check_pagina.py` (0 erros) + `teste_pagina_total.py` (0 erros) + olhar as PNGs seção por seção.
7. Documentar o que foi decidido e o que o cliente corrigiu (regra na hora).

## 7. Verificador (o que já é ERRO)

dobra 1 curta · rolagem horizontal · texto fora da tela/cortado · blocos de texto sobrepostos · rótulo de botão em 2+ linhas ·
margens esquerda × direita desiguais (sombra do botão conta) · CSS com `100vw` em layout · texto invisível/cortado com
movimento reduzido · imagem quebrada/sem alt · h1 ≠ 1 · contraste < WCAG · pop-up que não abre/fecha/prende foco.

## Famílias de páginas (página-mãe + páginas individuais × versões)
Extensão do contrato para famílias de páginas (ex.: 3 produtos × 3 versões):
- **O que é igual (código compartilhado):** dobra (palco → H1 → destaque → dia/hora → botão), espaços 12·24·40, ordem
  imagem → título → botão, estrutura de seções (apoio, como funciona, o que vai ver, quem apresenta, produto, oferta,
  bônus/prova, perguntas, fecho), tema claro/escuro, movimento.
- **O que muda por versão:** arte do palco (1 elemento do kit), layout das seções abaixo da dobra, fonte e peso, ritmo
  papel × preto. **O que muda por produto:** cor, elementos do assunto, copy.
- **Cor:** a cor especial da oferta (ex.: dourado) só na página-mãe; individuais = cor do produto/pessoa em tudo que é
  acento. Nunca misturar.
- **Arte do palco que funciona:** instrumento do assunto INTEIRO e concêntrico ao busto (ex.: goniômetro circular com a
  escala em volta da pessoa, braços curtos, cruz de eixos) ou disco na cor do produto atrás do busto com régua polar
  fina, tudo contido — verdadeiro e logicamente posicionado.
- **Reprovado:** instrumento pela metade atrás do corpo, bloco sólido com braço saindo, carimbo+fita+bloco, objeto
  gigante cortado na borda, 2 colunas na dobra de uma versão e eixo central em outra.
- **Verificação numérica obrigatória:** cor especial fora da página-mãe (matiz no CSS e nos SVGs), transbordo
  horizontal, CTA dentro da dobra (reproduzível em Playwright).
