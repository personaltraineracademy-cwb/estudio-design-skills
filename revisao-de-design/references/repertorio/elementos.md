# Repertório · Elementos

Referências públicas que o estúdio julgou bom ou premium, destiladas em princípio + medida. Formato e regras:
`LEIAME.md`. Referência é régua, não molde: extrair o princípio e superar, nunca copiar a forma.

### EL-01 · Moldura-aparelho com raio amarrado — premium
- Fonte: https://gsaweb.com.br/ · licença/uso: só estudo
- O que é: borda grossa arredondada que transforma a 1ª dobra (e o painel final) em "tela/aparelho".
- Princípio: a moldura é o contêiner da cena trocável (IA, retrato, arte do cliente) e o que persiste entre páginas.
- Medidas: 12 px da borda da tela, borda 6, raio 32 (28 ≤ 720), conteúdo interno raio 26; `overflow:hidden; isolation:isolate`; painel final com cantos 36 só em cima, continuado pelo rodapé sem emenda.
- Por que converte/encanta: Ch · Co (abre e fecha a página com a mesma peça).
- Como aplicar na nossa versão: derivar a carcaça de um objeto do cliente (visor, lousa, placar) e usar só em abertura e fechamento.
- Não copiar: a medida 6/32 + aba.
- Tags: web · contêiner de cena · janela/aparelho

### EL-02 · Forma que significa: aba, pasta e vidro — premium
- Fonte: https://gsaweb.com.br/ · licença/uso: só estudo
- O que é: navegação numa aba de pasta virada pendurada no topo; projetos em cartões com forma de pasta e frente de vidro.
- Princípio: o contêiner tem a forma do que contém (navegar = aba; projeto = pasta; dado = etiqueta); a forma é RECALCULADA no tamanho real, nunca esticada.
- Medidas: aba 532×74, laterais em curva S; pasta 5:4, `clamp(300px,32vw,480px)`, aba 46% da largura, curva 52, degrau 40, sombra 5; frente de vidro 112 px + 7% da largura, degrau 28, desfoque 20 + saturação 1,6; título 6,2% da largura (unidade de contêiner).
- Por que converte/encanta: Id/Df (explica sem texto) · Fu (corte do último cartão pede rolagem).
- Como aplicar na nossa versão: perguntar "qual objeto do assunto guarda isto?" e desenhar o cartão com essa silhueta em SVG calculado por largura.
- Não copiar: pasta + aba.
- Tags: web · contêiner com forma · arquivo/gaveta

### EL-03 · Dado real como ornamento, com um único ponto de cor — premium
- Fonte: https://gsaweb.com.br/ · licença/uso: só estudo
- O que é: mapa de contribuições de 365 dias (53×7) do repositório do autor, com o DIA DE HOJE em laranja.
- Princípio: textura feita de dado verdadeiro prova "trabalho diário"; o único ponto colorido vira assinatura (depois virou o ponto do monograma).
- Medidas: célula 11–16 px calculada para caber, raio 3; 5 níveis de tinta 7·20·42·68·100% (faixas 0 / 1–4 / 5–9 / 10–17 / ≥ 18); legenda "Menos ■■■■■ Mais"; hover 1,4× com anel e balão.
- Por que converte/encanta: Df · Fu (objeção "entrega mesmo?").
- Como aplicar na nossa versão: achar o dado diário do cliente (aulas dadas, alunos atendidos, treinos registrados) e fazer dele grade/ritmo; 1 ponto de cor = hoje/agora.
- Não copiar: o calendário do GitHub.
- Tags: prova · dado como textura · tabela + cartão de dado

### EL-04 · Ficha de vidro + véu com vão — bom
- Fonte: https://gsaweb.com.br/projects/congresso-brasileiro-de-treinamento-feminino · licença/uso: só estudo
- O que é: lista rótulo×valor em vidro sobre foto, alinhada pela base com o resumo.
- Princípio: dado objetivo em formato de etiqueta de catálogo ancora a promessa; vidro só sobre imagem (sobre liso não aparece); no celular o vidro vira cor chapada leve (desempenho).
- Medidas: rótulo 10 px 600 +0,24em 66% · valor 13,5 px 600 à direita · linhas de 50 px com fio 8%; fundo rgba(18,20,18,.3).
- Por que converte/encanta: Le · Fu.
- Como aplicar na nossa versão: ficha do curso/evento (formato · data · carga · certificado) sobre a foto da capa.
- Não copiar: medidas exatas do vidro deles.
- Tags: caso/oferta · etiqueta · palco com etiqueta

### EL-05 · Instrumento em espelho: emblema do método × moldura do autor — premium
- Fonte: https://lab.rodrigofenner.com.br · licença/uso: só estudo
- O que é: prumo (símbolo + fio + peso + régua) numa seção e grade de avaliação atrás do retrato do autor em outra.
- Princípio: o mesmo instrumento aparece 2× em espelho (7|5 e 5|7): emblema do que se aprende e moldura de quem ensina — o especialista "dentro do método", nunca selfie.
- Medidas: emblema 336×422; fio 1 px sem escala até um peso triangular; 5 marcas de régua (10 u, branco 45%) na altura de cada peça; retrato 4:5 (378×473), grade 8×10 a 9%, fio no eixo, registro 14×14 em 2 cantos opostos a −8 px, etiqueta com o nome no pé, pessoa recortada pousada no pé.
- Por que converte/encanta: Id 4 · Fu 4 — elemento verdadeiro, lógico e bonito; autoridade sem dizer "autoridade".
- Como aplicar na nossa versão: instrumento de diagnóstico do cliente (gabarito, mapa, partitura, régua de cor) usado 2×; marcas batendo nas medidas reais do símbolo.
- Não copiar: prumo e grade de avaliação postural.
- Tags: saúde · instrumento como elemento · retrato instrumentado

### EL-06 · Grade com profundidade de campo — premium
- Fonte: https://rodrigofenner.com.br/comunidade · licença/uso: só estudo
- O que é: grade sobre a cor plena do herói, nítida nas bordas e desfocada atrás do texto.
- Princípio: efeito de lente com 2 cópias da mesma grade e máscaras radiais complementares — o olho vai ao texto sem véu nem sombra; a grade é o instrumento ampliado.
- Medidas: célula 64 px, linha carvão 13%; foco elipse 42%×48% em x 32% · y 52% (celular x 50%); transição da máscara de 45% a 100%; blur 3 px; grão multiply 35% por cima.
- Por que converte/encanta: Df 4 · Co 4 — fotografia feita em CSS, leve e ligada ao assunto.
- Como aplicar na nossa versão: `.g1{mask:radial-gradient(ellipse 42% 48% at 32% 52%,#0000 45%,#000)}` + `.g2{filter:blur(3px);mask:radial-gradient(ellipse 42% 48% at 32% 52%,#000 45%,#0000)}` — com a malha do cliente (pauta, mapa, gabarito), foco onde fica o texto.
- Não copiar: grade quadrada sobre laranja com retrato.
- Tags: educação · profundidade em CSS · fundo de herói

### EL-07 · Família de fios com comprimento-função — premium
- Fonte: https://lab.rodrigofenner.com.br · licença/uso: só estudo
- O que é: todo acento da página é um fio: régua, traço, sublinhado, barra de nota, cantoneira, nó.
- Princípio: o comprimento diz a função (48 abre título · 24 marca item/assinatura · 17,6 separa termos); 2 px só para "esta é a frase"; cantoneira só em 2 cantos opostos e só onde há medida.
- Medidas: régua 48×1 a 24 px do título; traço 24×1 na altura da 1ª linha (recuo 44); sublinhado 2 px a .22em, sem cortar descendentes, 1 por seção; barra de nota 2 px à esquerda, 50ch; cantoneira 12 (hover do cartão) / 14 (retrato), 7–8 px para fora; número 01–04 com régua do tamanho dele em cima; fios retos, todo o resto arredondado (6,4–20).
- Por que converte/encanta: Cr 4 · Ch 4 — o acento rende pela raridade (0,4% de área) e nunca vira enfeite.
- Como aplicar na nossa versão: no DS, 3 comprimentos-função + 1 espessura de ênfase; no fundo de acento, o fio vira a cor do texto.
- Não copiar: a escala 48/24/17,6 em laranja.
- Tags: educação · linha de sistema · hierarquia por comprimento

### EL-08 · Crachá com campo de nome (produtora de eventos) — premium
- Fonte: https://timmeventos.com.br/ · licença/uso: só estudo
- O que é: crachá pendurado no herói em que o visitante escreve o próprio nome; o nome volta na ficha da jornada.
- Princípio: elemento que é interface — o objeto do ritual vira campo e o dado viaja pela página (pertencimento antes de ler).
- Medidas: cartão 300 px, raio 22, sombra 0 40 80 −30; campo serif 40 px que cai para 32/26 com nome longo, máx. 18 letras, placeholder "Você"; dica 12 px some quando há nome; foco = fundo cor de ação a 16%; salvo no navegador com falha silenciosa; o balanço pausa ao editar.
- Por que converte/encanta: Ac 4 e Fu 4 — uma interação com significado vale mais que dez animações.
- Como aplicar na nossa versão: achar o objeto do cliente que leva nome (ficha, carteirinha, certificado, comanda, prontuário) e deixar o leitor preenchê-lo; reaparecer uma vez adiante (jornada ou oferta).
- Não copiar: crachá + cordão + "passe livre".
- Tags: eventos · elemento interativo · pertencimento

### EL-09 · Canhoto com slot variável (campanha de Black Friday) — premium
- Fonte: https://combo.brandsdecoded.com.br/black-brands/b · licença/uso: só estudo
- O que é: etiqueta-assinatura com canhoto picotado reservado a um dado que muda.
- Princípio: o objeto-assinatura tem uma área cujo conteúdo segue a fase (data na captação → contagem nos lembretes → preço no carrinho): uma forma serve 3 momentos da campanha sem redesenho.
- Medidas: inclinada −6°, gira pelo furo (origem 15,9% 50%); picote 5 px (traço 14 · vão 12); versão "material" (papel, ilhós, barbante) só ≥ 300 px, lisa abaixo; versão 1 cor para lembrete; sombra dupla: contato 1 px + ambiente 14/18 px.
- Por que converte/encanta: Ch 4 — a série inteira se reconhece; "R$ ???" no canhoto vira pergunta que pede o clique.
- Como aplicar na nossa versão: marcar no kit qual parte do objeto do cliente é o slot e escrever os estados (data · contagem · preço · encerrado).
- Não copiar: etiqueta de preço pendurada com barbante.
- Tags: varejo · slot · objeto-assinatura

### EL-10 · Picote como linha única + "preço riscado" transposto para as tarefas — bom
- Fonte: https://combo.brandsdecoded.com.br/black-brands/b · licença/uso: só estudo
- O que é: toda divisória, borda, raio de diagrama e fio é o tracejado de cupom; a lista "você não vai mais precisar" é riscada como preço velho.
- Princípio: a linha do objeto vira a única linha do sistema; um gesto do mundo do cliente (riscar o preço) é aplicado a outro alvo (o esforço que some).
- Medidas: tracejado 2 px creme 14% no escuro · 1 px na cor do texto no claro · 3 px na faixa · 5 px no objeto; risco = barra 0,09 em a 57% da altura, −2°, sobra 0,1 em dos lados, palavra a 40%; bloco-ícone 0,9 em, ícone 24 px traço 2,5 ponta reta, sombra dura 4/4 px (7 px no hover).
- Por que converte/encanta: Fu 4 — o vocabulário de oferta chega a cada canto sem enfeite novo.
- Como aplicar na nossa versão: escolher a linha do objeto do cliente (costura, pauta, régua, trilho) e usá-la em tudo que separa ou liga; transpor um gesto do mundo dele para o argumento (nunca riscar data/preço).
- Não copiar: tracejado + palavras riscadas em condensado coral.
- Tags: varejo · linha do sistema · gesto transposto

### EL-11 · Relevo seco do símbolo — bom
- Fonte: https://combo.brandsdecoded.com.br/black-brands/b · licença/uso: só estudo
- O que é: o símbolo "prensado" no fundo, alto-relevo no claro e baixo-relevo no escuro.
- Princípio: textura feita do próprio símbolo, profundidade sem cor nova; fecha dobras longas.
- Medidas: 520–980 px, sangrando no canto, girado −8° / +4°; luz de cima-esquerda, sombra para baixo-direita; 1 por dobra, máx. 2 na página; pequeno lê como sujeira (o próprio site o afastou no celular).
- Por que converte/encanta: Cr — acabamento de papel impresso, não de tela.
- Como aplicar na nossa versão: símbolo do cliente como relevo em dobra de fechamento; testar a 25% se não vira mancha.
- Não copiar: a estrela de oferta.
- Tags: textura · relevo · fundo
