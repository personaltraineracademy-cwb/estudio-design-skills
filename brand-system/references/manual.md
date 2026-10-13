# Manual da marca — útil, não decorativo

`python manual.py build <marca>` monta páginas 16:9 com as fontes da marca → `manual/manual.pdf`, `manual.html`
(web), `paginas/NN.png`, `folha.png`. `--inline` embute imagens (HTML único, ex.: publicar como Artifact).
`--qa-only` gera só o HTML e roda o verificador de layout (rápido: use no laço de correção).
O script só diagrama: **o texto é do cliente**, escrito em `brand.json`. Capítulo sem dados é pulado **com aviso**.
Rode antes `palette.py build`, `typesys.py build` e `tokens.py build` (o capítulo Design system lê `tokens/`).

## Capítulos e de onde vem cada um (ordem do manual)
| Capítulo | Campos/arquivos |
|---|---|
| Capa | `platform.idea`, símbolo/primitiva, logo; título só na coluna escura (nunca sobre o símbolo gigante: texto claro sobre a cor da marca dava ~2:1); faixa com as cores dos produtos |
| **Comece por aqui** (pág. 2) | `logo.*`, `color.seeds`, `type.*`, `templates`, `governance.contact` — as 5 perguntas da semana (qual logo, quais cores, quais fontes, quais modelos, os 5 nãos) + a quem pedir |
| Índice | montado no fim, com os capítulos que saíram de verdade |
| Essência | `platform.onlyness, idea, enemy, zag, jobs, tension, personality, principles` (3 princípios por página quando têm fazer/evitar/teste) |
| Logo | `logo.primary/secondary/symbol/…` (SVG), `logo.concepts`, `variants`, `colorways`, `clearspace` (× altura) + `clearspace_rule`, `min_px`/`min_mm`/`min_px_rule`, `construction`, `dont` (+ 8 usos incorretos gerados; a lista longa de "nãos" vai para página própria) |
| Cor | `color.seeds` (com nomes), `proportion`, `rules`, `accent_decisao`, `proportion_rule`, `cores/contraste.png`, escalas |
| **Produtos** | `products[]` + `products_rule` + `architecture`: abertura; **como a marca se organiza** (endossante → marca → produtos → selos); **o que nunca muda × o que muda**; marca-mãe e produtos lado a lado; **qual cor usar?** (árvore); **matriz produto × papel** (fundo, tinta, destaque, texto no destaque, ao vivo, visor, erro, com contraste); **cor e acessibilidade** (visão normal · P&B · deuteranopia · protanopia + pares que confundem); por produto: abertura no fundo dele, logos no `bg` de cada um + símbolos como avatar de 48 px reais, cor (HEX/RGB/CMYK + pares de contraste principal e alt), aplicações na mesma escala e regras / não fazer / código (ao lado das peças só se CABE, senão em páginas próprias) |
| Tipografia | `type.display/text`, `levels` (typesys.py), `rules` (as regras entram inteiras no texto de abertura, nunca cortadas no meio da frase) |
| Elementos gráficos | `devices` **ou** `elements` + `patterns` + `elementos/catalogo/*.png` — medidas, regras de uso, folha do kit, uma ficha por elemento |
| **Forma** | `shape` — regra em 1 frase, escala em tamanho real (arte e site), elemento → papel → raio, conta do aninhado, 3 certos × 3 errados, "o logo não arredonda" |
| Grid | `grid.*` (desenha as colunas em 4 formatos + zonas seguras do story) |
| Imagem | `imagery.*` + `texture.*` + `imagem/*.png|jpg` (a lista longa de "evitar" vai para página própria) |
| Ícones | `icons.*` + `icones/*.svg` |
| Movimento | `motion.principles, easing, easing_notes, durations` (curvas desenhadas; produtivo × expressivo) |
| Voz | `platform.voice.is, is_not, examples, matrix{canais, linhas[{principio, niveis}]}` |
| **Canais** | `channels.instagram` (avatar 110/48/32 px, handle, destaques, grade, legenda) e `channels.whatsapp` (foto redonda do grupo com a área do essencial, nome, descrição, mensagens, figurinhas, frases do documento) |
| Modelos de peça | `templates[]` (nome, regra, medidas, exemplos, comando) — uma página por modelo; é o capítulo que permite a qualquer pessoa replicar as peças (references/modelos.md) |
| Aplicações | `mockups/*.png|jpg`, `aplicacoes/*/pecas/*.png` (pastas com "_" ficam de fora), `aplicacoes/estresse.png` |
| **Acessibilidade** | `accessibility.*` — as 12 regras padrão + as da marca, foco e alvo medidos em tamanho real, o que o verificador mede |
| **Páginas e sites** | `pages.items[]` — método fixo (o que é igual), mapa das páginas, as individuais lado a lado (linha = produto, coluna = versão) e, por página, 2 telas: prints (dobra no computador e no celular + página inteira em 3 tiras) e anatomia (blocos × papel de marketing, elementos do kit × onde entram × por quê, CTA, oferta). Com `prints_claro`, cada página ganha uma tela a mais no tema claro e o lado a lado ganha uma tela no
claro. **Vale para a página-mãe E para cada página individual** (cliente pediu, 11/10/2026) |
| Design system | lista dos arquivos de `tokens/` que existem + trecho do CSS + a demonstração em tamanho real (`tokens/demo/blocos.json`): marca-mãe completa e resumo por produto, cada pedaço com os tokens que usa |
| **Canais oficiais e jurídico** | `official.*`, `legal.*` — canais, o que nunca pedimos, registro e ®/™ (® só com `trademark_status: concedido`), titular, CNPJ, autorizações de imagem, créditos, licenças |
| **Governança** | `governance.*` — versão, status, dono, contato, quem aprova o quê, o que mudou, como pedir uma peça, nome de arquivo, exportar para cada uso, onde baixar |
| **Decisões pendentes** | `decisions.itens[]` — o que ainda precisa do sim da cliente: o que o manual usa hoje × o que muda se mudar. O estúdio registra; não decide |
| Recursos | estrutura de pastas, versão, aviso de INPI |

Lista-modelo de um manual profissional (pesquisa 17b §4.1, lacunas priorizadas): comece por aqui · essência · logo
(+ parceiros/co-branding e impressos quando houver) · cor (+ por produto) · tipografia · superfície/forma ·
elementos · grid · imagem (direção de foto: casting, pauta de planos, luz, autorização) · ícones · movimento ·
voz (matriz por canal, glossário, microtexto) · canais (Instagram, WhatsApp, e-mail) · acessibilidade · jurídico e
canais oficiais · governança · design system. Ainda sem capítulo próprio: kit sonoro, parceiros, impressos,
certificado, medição, diagramas, dataviz (backlog; entram quando houver dado do cliente).

## Cobertura e caminhos (o manual se confere sozinho)
- **Cobertura**: toda chave preenchida do `brand.json` precisa aparecer em algum capítulo; o build
  imprime `cobertura: …` com o que ficou de fora (ex.: `icons (bloco inteiro)`). Um script que lê só um campo
  (`devices`) já fez o kit inteiro de elementos sumir do PDF — leia o aviso, não ignore.
- **Caminhos**: `aviso caminho: bloco.campo → arquivo (não existe)` para TODO arquivo citado. Moveu
  arquivo → atualize o `brand.json` na hora.
- **Layout (verificador no navegador)**: `layout pág NN: …` para texto que passa do pé (y > 992) ou da margem
  (x > 1802), textos sobrepostos, texto cortado pela caixa, caixa que passa do pé e corpo < 13,5 px. O alvo é
  "nenhuma página com texto fora da área" ANTES de olhar. Texto longo vai para outra página, nunca encolhe.
- **Copy**: nada de texto inventado — `[a definir]` tracejado + `aviso: bloco.campo = [a definir]`. Proposta do estúdio
  aparece como PROPOSTA (selo tracejado), nunca como decisão. Sem referência interna ("17c regra 9", nome de arquivo
  do estúdio, `.py`) em texto de manual: o leitor é o cliente.

## Imagem de IA com pessoa nunca fica em `imagem/`
O capítulo Imagem puxa TUDO de `imagem/*.png|jpg`. Pessoa inventada por IA (professor, aluno, depoimento) não entra
nem como "provisória" nem em prancha de exemplo: guarde em `imagem/_fora-do-manual/` (pastas com "_" ficam de fora).
Foto real editada pela IA (fundo, luz) só com termo de imagem que cite edição por IA (`legal.releases`).

## Como escrever regras que funcionam
- **Condição + sujeito + deve/não deve + valor**: "Em fundos escuros, o logo usa a versão negativa com área de
  proteção de 0,5x." Uma exigência por regra.
- Número em vez de adjetivo (proteção, mínimos px/mm, pares de contraste, % de uso).
- Faça/não faça com imagem; o **porquê** de cada regra (para decidir casos não previstos).
- Exemplo real para cada regra; aplicações nos formatos que a marca vai usar de verdade.
- Matriz tom × canal na voz (Monzo); exemplos de frase antes/depois.
- Versão com dono e data; e a versão para máquina (tokens + DESIGN.md).

## O que é decorativo (cortar)
Página de clima sem regra · "nossa voz é calorosa" sem exemplo · aplicações sonhadas que nunca vão existir ·
manifesto mais longo que as regras · PDF não pesquisável.

## Antes de entregar o manual
1. `manual.py build … --qa-only` até `layout: nenhuma página com texto fora da área…`; zere `caminho` e leia a
   `cobertura`.
2. Build completo; olhe `manual/folha.png` e abra com Read, UMA A UMA, as páginas novas e as de risco (capa, margem
   e rodapé das páginas densas, produtos, demonstração do design system); depois amostre o resto a 100%.
3. Critérios por página: nada cortado ou sobreposto, texto legível (contraste WCAG, corpo ≥ 15 px na página 1920),
   margens iguais, hierarquia, "nada parece erro", nada inventado. Corrija no `brand.json` ou no script e gere de novo.
4. Ofereça publicar a versão web (`--inline`) como Artifact privado para compartilhar com a equipe.
As imagens entram leves (lado ≤ 1600 px; JPEG quando não há transparência; cache em `manual/_img/`): o PDF fica em
poucos MB (sem isso, peças em 2K/3000 px passavam de 30 MB e não iam por mensagem).
Arquivo de produto que não existe (logo, símbolo, peça) é pulado com aviso no terminal (uma vez só).

## Capítulo "Páginas e sites": detalhes que custaram retrabalho
- **Tiras da página inteira:** cada tira é um ARQUIVO recortado (`_print_strip` grava em `manual/_img/paginas-tiras/`);
  recorte por `overflow:hidden` com `margin-top` negativo faz o verificador acusar "caixa passa do pé" em cada tira.
- **Prints com rolagem real** (reveal/lazy/contadores), 2 temas, 3 tamanhos; guardar em `paginas/` do projeto e citar
  em `pages.items[].prints` e `prints_claro`.
- **Texto do cliente, não do estúdio:** não escrever "(sem dourado)", "proposta do estúdio" ou nomes de arquivo nas
  frases; a regra vira "bloco na cor do professor".
- **Duas builds ao mesmo tempo corrompem `manual/paginas/`** (FileNotFound na folha): uma build por vez.
- Rebuildar o manual sempre que mudar página/elemento que aparece nos prints; PDF ~32 MB com 72 prints (lado ≤ 1600).
