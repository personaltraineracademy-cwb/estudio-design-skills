# Modelos de peça — o produto que garante fidelidade (`scripts/modelos.py`)

Um **modelo de peça** é uma regra de composição escrita como código e medida: mesmo texto + mesmo modelo = mesma
peça, feita por qualquer pessoa, em qualquer formato. É o que transforma "uma identidade bonita" em "um sistema que
outra pessoa replica com extrema fidelidade". Num sistema, 5–8 modelos cobrem ~90% das peças do dia a dia.

Por que não só as receitas do `apply.py`? Receitas são genéricas (servem de base em minutos). Os modelos carregam o
**gesto próprio da marca** (o que só ela faz) e as **medidas** que impedem os erros que o olho pega (ver §5).

## 1. Os 7 tipos (`python modelos.py tipos`)
| Tipo | O que é | Parâmetros principais | Bom para |
|---|---|---|---|
| `tipo` | o texto é a imagem; maior corpo possível; a palavra com `~` recebe o gesto (girar/cor); com `giant_last`, a última palavra vira gigante cortada pela borda | colors{bg, fg, gesture} · gesture: girar\|cor\|nenhum · giant_last · symbol_fill | manifesto, lançamento, frase da campanha |
| `janela` | o símbolo inteiro vira janela para uma foto; fora dele, cor da marca; texto nunca sobre a foto | colors{bg, fg} · foto · symbol_h | foto de gente/produto com marca forte |
| `numeral` | número/hora herói (88% da largura) + elemento da marca atrás + "sobrenome" colado em cima | numero · device · colors{bg, fg, device, kicker} | convite, hora, preço, dado |
| `contagem` | rótulo · NÚMERO · rótulo, na ordem de leitura | numero · colors{bg, fg, number} | temporada, contagem regressiva, marcos |
| `padrao` | símbolo em grade alternando (espelho/girar) + painel da mensagem | colors{bg, fg, panel, text} · alternate · cols · panel | comunidade, camiseta, fundo de site |
| `elemento` | um elemento grande da marca + título | device · colors{bg, fg, device} · device_h | segurança, serviço, informação de rua |
| `pontilhado` | frase "apagada" em esferas + palavra "acesa" chapada; símbolo apagado na sobra | colors{bg, dots, lit, fg} · font (peso menor) · cell | comportamento de luz/estado, campanhas noturnas |

Todos: margem = `grid.margin` (padrão 6,5% do lado menor) · entrelinha = `type.lead` (padrão 1,42 × maiúscula) ·
assinatura 4,2% do lado menor + info em texto 700 caixa alta 1,9% · formatos post, feed, story, banner, a4, outdoor,
slide, thumb (cada tipo tem regra própria para vertical e paisagem).

## 2. Como declarar (brand.json "templates")
```jsonc
{"id": "janela", "model": "janela", "name": "Janela",
 "rule": "frase de 1–3 linhas que um designer entende sem ver o código",
 "colors": {"bg": "brand", "fg": "ink"},            // papéis (brand, ink, paper, accent, brand.300…) ou HEX
 "foto": "imagem/x.png",                            // + parâmetros do tipo
 "measures": ["símbolo = 66% de H, pousado na base", "…"],   // as medidas que o manual imprime
 "sample": {"texto": "TODA NOITE É UM TREINO NOVO.", "info": "terça e quinta · 20h", "foto": "imagem/x.png"}}
```
Marcação do texto: `|` força quebra de linha (sem `|`, a quebra é automática pelo maior corpo); `~PALAVRA` = o gesto
do modelo. `--numero` / `sample.numero` para numeral e contagem.

## 3. Fluxo
1. Escolha 5–8 tipos que a ideia da marca pede (não use todos). Dê nome próprio a cada um (ex.: "Janela", "Vinte
   horas") e uma regra de 1 frase.
2. Declare em `brand.json.templates` com `sample` (texto real da marca, nunca lorem ipsum).
3. `python modelos.py kit <dir>` → `aplicacoes/<id>/pecas/*.png|svg` em todos os formatos + `examples` e `command`
   gravados no brand.json.
4. **Olhe tudo** (montagem lado a lado por formato). Corrija pelo parâmetro do modelo, nunca editando a peça à mão.
5. Rode a arena de composições (references/arena.md §Composições) com a mesma mensagem em todos os modelos.
6. `manual.py build` → capítulo **Modelos de peça** (regra, medidas, exemplos, comando de cada um).
Peça nova depois: `python modelos.py render <dir> <id> --texto "…" --info "…" --formatos feed,story`.

## 4. Quando o tipo não existe
Se a ideia pede um comportamento que nenhum dos 7 cobre, escreva um gerador no projeto (`<marca>/codigo/`), com a
mesma disciplina: função por modelo, medidas em constantes nomeadas, docstring = regra. Se servir a outras marcas,
leve para `modelos.py` como tipo novo (decorador `@model("nome", "parâmetros")`) e documente aqui.

## 5. Erros que o olho pega (e as regras que nasceram deles)
| Erro visto | Regra no motor |
|---|---|
| vírgula/cedilha da linha de cima batendo na de baixo ("À CIDADE") | entrelinha ≥ 1,42 × maiúscula |
| linha terminando em "A", "UM", "DE"; "DE" sozinho na última linha | quebra automática proíbe palavra de 1–2 letras no fim e sozinha no fim |
| palavra girada pequena lida como erro de digitação ("DE 3D") | girar só como gesto gigante (`giant_last`); pequena, nunca |
| pontuação girando junto com a palavra | só as letras giram |
| símbolo gigante demais deixa de ser lido | janela: símbolo inteiro (66% de H), pousado na base |
| no story o símbolo ficou largo e cobriu a assinatura | janela: largura do símbolo ≤ 78% de W |
| buraco entre o título e o símbolo (story) | o título desce até encostar no símbolo; o vazio fica no alto |
| palavra girada pequena em paisagem | em paisagem a palavra girada vira gigante no terço direito |
| elemento SVG recolorido pela metade (traço ficou preto) | recolorir troca preenchimento E traço |
| info por cima da foto | info empilhada no canto livre, nunca sobre a foto |
| metade da peça vazia | sobra ≥ 30% (tipo) / ≥ 12% (pontilhado) → o símbolo ocupa a sobra |
| texto da mesma cor das linhas do elemento some | "sobrenome" do numeral em cor de texto, não de destaque |
| letras em esferas fechando o miolo ("0" vira "D") | pontilhado com peso menor (700) e esfera = 1/11 da maiúscula |
| elemento colidindo com o título | campos separados: elemento ≤ 52% de H, título de 60% para baixo |
| foto "de banco de imagem" | direção de foto com idade, espontaneidade e luz definidas (aplicacoes.md T11) |

## 6. Checklist de um modelo pronto
- [ ] Lê em 2 segundos no celular (teste com o juiz "público").
- [ ] Nenhuma colisão (acentos, pontuação, elemento × texto, info × foto) em post, feed, story, banner e outdoor.
- [ ] Contraste do texto ≥ 4,5:1 (≥ 3:1 só em corpo muito grande).
- [ ] Um gesto ousado por peça; o resto contido.
- [ ] Regra em 1 frase + medidas com número no brand.json; `sample` com texto real.
- [ ] Gerado pelo motor (sem retoque manual); refeito com outro texto e continua certo.

## SVG de terceiro embutido
Logo de terceiro (pós, parceiro) costuma pintar por classe CSS (`.cls-1{fill:…}` num `<style>`). Embutido várias vezes
na mesma página/folha, a última cor vence em TODAS as cópias (o logo some nas versões claras). Antes de embutir:
achatar as classes em atributos `fill`/`stroke` e prefixar ids. Entra na versão oficial MONOCROMÁTICA e pequena.
