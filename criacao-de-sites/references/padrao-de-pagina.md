# Padrão de página — resumo (fonte da verdade: `../direcao-de-arte/references/padrao-de-pagina.md`)

> O contrato completo (só mudam elementos, layout, identidade, cores e fonte; espaçamento, dobras e metodologia são
> padronizados) vive em `../direcao-de-arte/references/padrao-de-pagina.md`. Complemento
> com o porquê de cada regra: `../direcao-de-arte/references/paginas-de-captura.md` §0–§7. Aqui só o que precisa estar à mão ao montar.
> No código do template os números abaixo são os tokens de `app/globals.css`.

## FIXO × MUDA

| FIXO em toda página | MUDA por cliente |
|---|---|
| escala de espaçamento, margens, respiros | cores, fontes, logo, grão, formas |
| contrato da 1ª dobra (altura, o que cabe, ordem) | o layout/composição escolhida para a dobra |
| mesma composição em TODAS as larguras (só escala) | elementos gráficos e fotos |
| um eixo, uma ordem de leitura, uma ideia por tela | linguagem de movimento (assinatura) |
| grade de verificação e portão de entrega | a copy (sempre a final do cliente) |

## Tokens

| token | valor | uso |
|---|---|---|
| `--g1` / `--g2` / `--g3` | 12 / 24 / 40 | mesmo grupo / grupos relacionados / grupos separados |
| `--m` | 24 (< 600) · 40 (≥ 600) · `clamp(48px, 6vw, 112px)` (≥ 1024) | margem lateral, esquerda = direita |
| `--gut` | 16 (< 600) · 24 | vão entre colunas/cartões |
| `--sec` | 72 (< 600) · 112 (≥ 600) · `clamp(112px, 9vw, 144px)` (≥ 1024) | respiro de cada lado da seção (vão entre seções = 2×) |
| `--header-h` | 64 (< 768) · 72 | cabeçalho |
| escala | 4·8·12·16·24·32·40·48·64·96·128·160·200 | nenhum outro valor de espaço |
| botão | ≥ 60 (principal) / 48 (barra); sombra dura conta na margem | rótulo SEMPRE em 1 linha |
| texto | corpo ≥ 16; rótulo mono ≥ 14; ≤ 6 tamanhos | — |

## A 1ª dobra (contrato)

1. **Altura = a tela inteira**: `<section class="est-dobra" data-hero>` = `min-height: 100svh − --header-h`, conteúdo
   centrado na altura. A seção seguinte NÃO aparece (nem o eyebrow).
2. **Conteúdo único e na mesma ordem**: IMAGEM → TÍTULO → apoio + data → BOTÃO → micro. Logo só no cabeçalho.
3. **Um eixo**: tudo centrado, ou texto à esquerda + imagem à direita com mesma altura/centro. Nunca camadas
   desligadas, faixa sem origem, bloco solto, texto longe do botão.
4. **A imagem é o maior elemento** e cresce com a janela, limitada pela altura (título + botão sempre cabem).
5. **Mesma composição em celular, tablet e desktop**; muda só a escala (botão em largura total < 600).
6. **Zona do polegar**: botão principal termina antes de 88% da altura em 360×740 (verificador: 82% celular, 92% desktop).

## Abaixo da dobra

Padding vertical = `--sec` de cada lado · título ↔ conteúdo = `--g3` · item ↔ item = `--g2` · fundo alterna a cada
seção (escuro/claro) · uma mensagem por seção · ≥ 38% de área vazia por tela · container único com a MESMA margem do
cabeçalho · cartões padding ≥ 24 (32 desktop) · final = uma ideia só (frase + botão), sem textura atrás de texto.

## Responsividade (passo a passo)

Desenhar UMA vez em coluna central a 390 px → escalar com `clamp()`/`cqw` (nunca `100vw`) → em ≥ 1024 só aumentar a
escala (2 colunas só com justificativa por escrito, mesmo centro e altura) → testar 320, 360, 375, 390, 414, 430,
600, 768, 1024, 1280, 1366, 1440, 1536, 1920, 2560 + paisagens 667×375…1024×600 → foto centrada pela TINTA.

## Movimento

Sempre ligado; `data-movimento` total/suave/parado · só `transform`/`opacity`/`clip-path` · entra uma vez, ≤ 0,7 s ·
nunca no H1, na foto do LCP nem no CTA (exceto a seta) · estado natural do CSS = estado final (`forwards`).

## Produção (sempre nesta ordem)

1. Entradas (copy final, logo, fotos reais, cores/fontes). 1b. ELEMENTOS ANTES DA PÁGINA (kit do cliente feito e revisado; inventariar o que a página reutiliza; quantidade
média). 2. UMA ideia gráfica da dobra (IA só cenário/complemento,
Nano Banana 2.1). 3. Dobra no contrato, a 390 px, escalar. 4. Seções com os tokens. 5. Movimento. 6. Verificar
(`check_pagina.py` + `teste_pagina_total.py`, 0 erros) e olhar as PNGs. 7. Documentar o que foi decidido e corrigido.

## O que o verificador já acusa como ERRO

dobra 1 curta · rolagem horizontal · texto fora da tela/cortado · blocos de texto sobrepostos · rótulo de botão em
2+ linhas · margens esquerda × direita desiguais (sombra do botão conta) · `100vw` em layout (aviso) · texto
invisível/cortado com movimento reduzido · imagem quebrada/sem alt · h1 ≠ 1 · contraste < WCAG · pop-up que não
abre/fecha/prende foco · texto proibido ("lorem", "[", "confirmar", "últimas vagas"…).
