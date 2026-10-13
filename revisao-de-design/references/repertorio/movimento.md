# Repertório · Movimento

Referências públicas que o estúdio julgou bom ou premium, destiladas em princípio + medida. Formato e regras:
`LEIAME.md`. Referência é régua, não molde: extrair o princípio e superar, nunca copiar a forma.

### MV-01 · Intro-contador que vira porta — premium
- Fonte: https://gsaweb.com.br/ · licença/uso: só estudo
- O que é: tela branca com logo, número 0→100 enorme e barra de cor na base; sai subindo como cortina.
- Princípio: o carregamento vira apresentação da marca e dá tempo da cena pesada chegar; 1 vez por visita.
- Medidas: logo surge a 92% em 0,4 s; contador 1,1 s com ease-out cúbico; número 176 px (72 no celular), "%" 38 px na cor; barra 5 px; espera 120 ms; saída −100% em 0,62 s `(.22,1,.36,1)`; a palavra do título só começa a girar 2,4 s depois.
- Por que converte/encanta: Ch · Cr (sem tela vazia). Falha: logo branco no fundo branco.
- Como aplicar na nossa versão: `v=round(100*(1-(1-k)**3))` por rAF; `sessionStorage` marca "visto"; reduzido = só esmaece.
- Não copiar: o número gigante na fonte deles.
- Tags: web · carregamento · entrada

### MV-02 · Palavra-carimbo que gira no título — premium
- Fonte: https://gsaweb.com.br/ · licença/uso: só estudo
- O que é: última palavra do H1 troca entre 4 promessas, cada uma "batendo" como carimbo, sempre na cor de ação.
- Princípio: 4 promessas num título só sem crescer a dobra; o gesto (carimbar = aprovar) conta a ideia; na página-irmã o gesto muda para "sobe".
- Medidas: ciclo 2,6 s; entra escala 1,06→1 em 0,56 s `(.22,1,.36,1)` + opacidade 0,3 s `(.33,1,.68,1)`; sai escala .94; variante sobe ±.2em em 0,42 s.
- Receita: `.g{display:inline-grid}.g i{grid-area:1/1;opacity:0;transform:scale(1.06);transform-origin:left;transition:opacity .3s cubic-bezier(.33,1,.68,1),transform .56s cubic-bezier(.22,1,.36,1)}.g i.on{opacity:1;transform:none}.g i.out{transform:scale(.94)}` + `setInterval(troca,2600)`; inativas `aria-hidden`.
- Por que converte/encanta: Ch · Fu (promessa múltipla sem crescer a dobra).
- Como aplicar na nossa versão: o verbo do gesto vem do assunto do cliente (carimbar, acender, encaixar).
- Não copiar: as 4 palavras.
- Tags: título · rotação de palavra · tipografia cinética

### MV-03 · Tudo se mexe como objeto (botão, acordeão, mapa, pasta) — premium
- Fonte: https://gsaweb.com.br/ · licença/uso: só estudo
- O que é: 3 curvas nomeadas e gestos físicos: botão que afunda, item que se solta da pilha, quadrados que surgem em onda, capa que aproxima.
- Princípio: cada componente imita um objeto real; ESTADO ABERTO VIRA OBJETO (ganha cantos, sombra e distância próprios; o resto vira pilha).
- Medidas: curvas saída `(.2,.8,.2,1)` · entrada `(.22,1,.36,1)` · mola `(.34,1.56,.64,1)`; botão 0,16 s: hover −1/−2 px e sombra 3→5, clique +2 px e sombra 1; acordeão: altura `grid-template-rows 0fr→1fr` 0,45 s, solta 14 px com mola 0,6 s, cantos 26, sombra 4, "+"→"×" girando 45° em 0,55 s mola; mapa: escala .2→1 em 0,5 s com atraso 14 ms × semana; pasta: capa 1,06 em 0,9 s, seta −45° em 0,35 s; revelar 0,6 s subindo 14 px, grupo com 70 ms entre itens; esteiras 90 s (logos) e 110 s (depoimentos), param no hover, máscara 6–8% nas pontas.
- Receita: `.item{margin-top:-2px;transition:margin-top .6s var(--mola),border-radius .45s var(--saida)}.item.aberto{border-radius:26px;box-shadow:4px 4px 0 var(--tinta);z-index:1}.item.aberto+.item{margin-top:14px}.corpo{display:grid;grid-template-rows:0fr;transition:grid-template-rows .45s var(--saida)}.aberto .corpo{grid-template-rows:1fr}`
- Por que converte/encanta: Ch · Cr (sistema "tátil" coerente). Reduzido: esteiras 2× mais lentas, resto só esmaece.
- Não copiar: a sombra dura em tudo (cansa no fim da página).
- Tags: microinteração · física de objeto · lista que abre

### MV-04 · Troca de página em que a carcaça não sai — premium
- Fonte: https://gsaweb.com.br/sobre · licença/uso: só estudo
- O que é: View Transitions com nome próprio para moldura e aba; só o conteúdo apaga e sobe.
- Princípio: o que é estrutura persiste, o que é conteúdo troca → o site parece um aparelho trocando de canal.
- Medidas: conteúdo velho apaga 0,42 s e sobe −8 px `(.33,1,.68,1)`; novo acende 0,42 s e sobe de 14 px com desfoque 3→0 em 0,6 s `(.22,1,.36,1)`; moldura passa por desfoque 2 px a 40%; barra de 2 px no topo cresce até 80% em 2,4 s ao clicar.
- Receita: `.moldura{view-transition-name:moldura}.aba{view-transition-name:aba}::view-transition-old(root){animation:apaga .42s both}::view-transition-new(root){animation:acende .42s both,sobe .6s cubic-bezier(.22,1,.36,1) both}@keyframes sobe{0%{transform:translateY(14px);filter:blur(3px)}}`
- Por que converte/encanta: Ch · Cr. Como aplicar: nomear 1–2 peças fixas da marca (cabeçalho, moldura) e só elas persistem.
- Não copiar: a aba.
- Tags: web multipágina · continuidade · CSS puro

### MV-05 · Movimento de evento "sempre em frente" — bom
- Fonte: https://gsaweb.com.br/projects/congresso-brasileiro-de-treinamento-feminino (marca reconstruída) · licença/uso: só estudo
- O que é: a fita corre, as barras entram uma a uma, um brilho atravessa a palavra importante, as telas de palco trocam subindo.
- Princípio: o movimento repete o DESENHO do logo (direção única, para a frente) e nunca pula.
- Medidas: fita laço 24 s linear; barras 0,4 s cada, cascata 60 ms, da esquerda para a direita; brilho 1,6 s a cada 4 s; troca de tela 0,5 s subindo 24 px; chips 0,3 s, um por vez, 80 ms (data → hora → formato); curva `(.22,1,.36,1)`; reduzido: fita a 1/3, resto esmaece.
- Por que converte/encanta: Ch · Fu (tela de intervalo que vira oferta com QR).
- Como aplicar na nossa versão: listar os traços do logo e dar a cada um 1 verbo e 1 sentido de direção; nada anima contra essa direção.
- Não copiar: brilho no degradê deles.
- Tags: evento · telas de palco · movimento derivado do logo

### MV-06 · Movimento com nome: "alinhar" — premium
- Fonte: https://lab.rodrigofenner.com.br e https://rodrigofenner.com.br/comunidade · licença/uso: só estudo
- O que é: 4 gestos (recortar · assentar · traçar · chegar), 3 curvas nomeadas e tempos fixos, tirados do verbo do assunto (corrigir postura).
- Princípio: as coisas entram tortas e se endireitam; textos e fios são "traçados" como com régua; a ênfase (traço, sublinhado) chega 200 ms DEPOIS do texto que marca.
- Medidas: ajuste (.3,0,.1,1) · régua (.6,0,.2,1) · saída (.4,0,1,1); recortar 520 · assentar 560 · traçar 480 · chegar 420 (6–8 px) · hover 180 entra / 120 sai · toque 90 (desce 1 px) · passo 60 ms (máx. 5); herói: chapéu 0 → régua 80 → linha 1 assenta (−1,2°, −10 px) 160 → linha 2 recortada 600 → sub/CTA/apoio 820/880/940 ms; emblema: figura −2,5° assenta, fio desce +420, marcas em cascata 700→860; rolagem dispara a −10% do pé; botão = preenchimento scaleX da esquerda; janela 220 ms (y 8, escala .98); barra fixa sobe 240 ms quando o herói sai.
- Por que converte/encanta: Id 4 · Ch 4 — cada entrada repete o gesto do produto; nada se mexe sem explicar.
```css
@keyframes assenta{from{opacity:0;transform:translateX(-10px) rotate(-1.2deg)}}
@keyframes recorta{from{clip-path:inset(-1em 100% -1em -1em)}to{clip-path:inset(-1em)}}
@keyframes traca{from{transform:scaleX(0)}} /* origin left; estado natural = final */
```
- Como aplicar na nossa versão: nomear o verbo do cliente (encaixar, acender, medir, florescer) → 3–4 gestos + 2–3 curvas; reduzido = mesmos gestos sem deslocamento, só opacidade (o original parava tudo).
- Não copiar: linha torta −1,2° + recorte como assinatura "alinhar".
- Tags: educação · movimento com nome · coreografia de entrada

### MV-07 · Revelar com foco de câmera — bom
- Fonte: https://jdpmed.com.br · licença/uso: só estudo
- O que é: blocos entram desfocados e "focam" ao rolar; contadores sobem; cartões levantam.
- Princípio: entrada = ajuste de foco (desfoque + escala mínima), coerente com "tudo sob controle".
- Medidas: opacidade 0 · blur 14 · y 22 · escala .985 → 900 ms (.16,1,.3,1), cascata 50–90 ms; gatilho threshold .08, margem −8%/−12%; hover-lift 400 ms (y −4 + sombra); imagem 1,015 em 700; contador 1,6 s easeOutCubic com opacidade .75→1.
- Por que converte/encanta: Ch 3 — calmo e caro de ver; defeitos: re-esconde ao subir (pisca) e blur 14 pesa.
- Como aplicar na nossa versão: uma vez só; blur ≤ 6 px e só em título (regra de desempenho do site) ou trocar por escala; reduzido = só opacidade.
- Não copiar: a curva + blur 14 em todo bloco.
- Tags: saas · revelar ao rolar · contador

### MV-08 · Interface viva em laço narrativo — bom
- Fonte: https://jdpmed.com.br · licença/uso: só estudo
- O que é: chat que digita, pulso que corre no trilho de etapas, abas que trocam sozinhas, vídeo que toca ao aparecer.
- Princípio: laço só no que representa algo vivo (conversa, dado passando); o resto entra uma vez.
- Medidas: chat 1 mensagem a cada 1,5 s precedida de 3 pontos (pulo 1 s, defasagem 140 ms), pausa 4,2 s, recomeça; pulso 1/3 da largura × 3 px, 5 s ease-in-out, aparece em 12% e some em 88%; abas 4,5 s (clique fixa); vídeo mudo a 50% visível; fitas opostas −2°/+1,6° a 46/42 s = única quebra de grade.
```css
@keyframes flow{0%{transform:translateX(0);opacity:0}12%,88%{opacity:1}100%{transform:translateX(200%);opacity:0}}
.pulso{width:33.3%;height:3px;animation:flow 5s ease-in-out infinite}
```
- Por que converte/encanta: Fu 3 — prova que conversa; defeito: abas numa esteira = alvo que foge do clique.
- Como aplicar na nossa versão: a "coisa viva" do cliente (fila andando, agenda enchendo, nota subindo) em HTML; alvo clicável nunca em movimento.
- Não copiar: chat de IA com nome e rosto.
- Tags: saas · prova animada · laço narrativo

### MV-09 · Pêndulo amortecido (objeto pendurado) — premium
- Fonte: https://combo.brandsdecoded.com.br/black-brands/b · licença/uso: só estudo
- O que é: a etiqueta entra balançando em volta do furo e para; no hover balança curto.
- Princípio: objeto físico gira pelo ponto real de fixação e perde energia em 4 oscilações; física verdadeira = objeto verdadeiro.
- Medidas: gatilho entrar na tela (1 vez); 1,6 s, cubic-bezier(.3,.7,.4,1), atraso .15 s; +14° → −6° → +3° → −1,2° → repouso (−6°); hover 1,2 s (4 · −2 · .8°). Receita: `.obj{rotate:var(--inc);transform-origin:15.9% 50%}` · `.obj.in{animation:pend 1.6s cubic-bezier(.3,.7,.4,1)}` · `@keyframes pend{0%{rotate:calc(var(--inc) + 14deg)}28%{rotate:calc(var(--inc) - 6deg)}52%{rotate:calc(var(--inc) + 3deg)}74%{rotate:calc(var(--inc) - 1.2deg)}}` (estado natural = repouso).
- Por que converte/encanta: Ac — chama o olho para a oferta uma vez e se cala.
- Como aplicar na nossa versão: medir o ponto de fixação do objeto do cliente (furo, cordão, alça) e usar como origem; reduzido = amplitude ÷ 3, nunca parado.
- Não copiar: a etiqueta.
- Tags: objeto · física · entrada

### MV-10 · Palco que respira (contínuo lento) — premium
- Fonte: https://timmeventos.com.br/ · licença/uso: só estudo
- O que é: 2 feixes de luz varrendo, crachá balançando, brilho correndo na folha, selo girando.
- Princípio: o cenário vive devagar e em períodos diferentes, então nunca sincroniza nem repete visivelmente; entrada de bloco curta e única.
- Medidas: feixes rotate ±6° em 9 s (alternate) e 11 s (alternate-reverse), ease-in-out, origem no topo, desfoque 18 px; crachá ±2,5° em 5 s pela borda de cima (origin 50% 0); brilho: fundo 220% indo e voltando em 6 s; selo 360° em 60 s linear; letreiro 32 s; entrada .8 s / 22 px cubic-bezier(.2,.7,.2,1) a 8% do pé da tela; reduzido = metade da amplitude e mais lento.
- Por que converte/encanta: Co — vivo sem disputar com o texto.
- Como aplicar na nossa versão: animar a luz/objeto do assunto do cliente com 5–60 s e períodos primos entre si (9/11, 7/13).
- Não copiar: refletores dourados + crachá.
- Tags: ambiente · loop lento · palco

### MV-11 · Fluxo para o centro + foco por hover (diagrama) — premium
- Fonte: https://combo.brandsdecoded.com.br/black-brands/b · licença/uso: só estudo
- O que é: raios tracejados correm dos 7 produtos para o centro; passar o mouse num nó isola o caminho dele.
- Princípio: o sentido do movimento é o argumento ("tudo desemboca aqui"); hover apaga o resto em vez de acender um.
- Medidas: raios dash 5/7, 1,5 px, vector-effect non-scaling-stroke; `@keyframes flui{to{stroke-dashoffset:24}}` 2,4 s linear infinito (linha desenhada do nó para o centro); hover (:has): raio coral 2,5 px e 0,8 s, outros nós a 40%, centro scale 1,06, ponto do nó 1,8× com halo 22%, nó anda 6 px para fora; entrada dos nós .5 s (.23,1,.32,1), 70 ms entre eles; celular sem apagar.
- Por que converte/encanta: Fu 4 — o diagrama diz algo, não só organiza.
- Como aplicar na nossa versão: em "o que está incluso" do cliente, fazer o fluxo andar na direção da oferta.
- Não copiar: constelação com estrela no centro.
- Tags: diagrama · fluxo · hover

### MV-12 · Riscos que se desenham em sequência + botão que enche — bom
- Fonte: https://combo.brandsdecoded.com.br/black-brands/b · licença/uso: só estudo
- O que é: cada tarefa é riscada da esquerda para a direita, uma depois da outra; o botão se enche da esquerda no hover.
- Princípio: o gesto acontece na frente do leitor (o esforço "some" item a item); a mesma curva de saída em tudo que é feedback.
- Medidas: risco `scale:0 1 → 1`, origem à esquerda, .5 s cubic-bezier(.23,1,.32,1), atraso 300 + 160 ms × i; hover do item: bloco −3/−3 px, sombra dura 7 px, ícone −8°, .18 s; botão background-size 0 → 100% em .32 s, clique scale .98 em .16 s.
- Por que converte/encanta: Ac — microgestos com tempo de produto.
- Como aplicar na nossa versão: riscar/marcar/preencher o que o produto do cliente elimina ou entrega, em cascata de 120–180 ms.
- Não copiar: riscos coral sobre condensado.
- Tags: lista · desenho progressivo · feedback

### MV-13 · Etapas que acendem na faixa central da tela — premium
- Fonte: https://www.thiagor.net/dgia · licença/uso: só estudo
- O que é: linha do tempo de 9 etapas; cada nó acende ao cruzar o meio da tela e fica aceso.
- Princípio: o progresso da leitura = o progresso do processo; nunca apaga ao voltar.
- Medidas: IntersectionObserver rootMargin "-40% 0px -34% 0px"; nó 9 px cinza #333 → laranja com `box-shadow:0 0 0 5px <fundo>, 0 0 18px <laranja .9>`; textos sobem um nível de cinza; .5 s ease; acender também o que já passou (rolagem rápida); entradas gerais .7 s / 24 px cubic-bezier(.16,1,.3,1), cascata de 60 ms — uma curva só na página.
- Por que converte/encanta: Fu 4 — o movimento explica o método.
- Como aplicar na nossa versão: em qualquer passo a passo do cliente (jornada, protocolo, trilha), o nó acende na faixa central.
- Não copiar: espinha "IA ajuda | você decide".
- Tags: processo · rolagem · estado

### MV-14 · Gesto completado pela rolagem (fechamento) — premium
- Fonte: https://www.thiagor.net/dgia · licença/uso: só estudo
- O que é: duas mãos (humana e robótica) começam afastadas e se aproximam com a rolagem até quase tocar.
- Princípio: o fim da página completa o gesto aberto no herói; movimento ligado à rolagem, sem tempo fixo.
- Medidas: separação inicial 110 px → +122 px quando o bloco chega ao terço de cima; `p = clamp(0, (innerHeight − top) / (innerHeight × .72), 1)`, `--aproxima: p × 122px`, rAF + scroll passivo; mesclagem lighten para sumir o fundo preto das imagens.
- Por que converte/encanta: Id — a promessa do herói vira o último gesto antes do botão.
- Como aplicar na nossa versão: escolher o par do conceito do cliente (aluno × professor, pergunta × resposta) e fazê-lo se encontrar no fechamento.
- Não copiar: as mãos.
- Tags: fechamento · scroll-linked · metáfora
