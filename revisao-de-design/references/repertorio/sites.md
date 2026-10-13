# Repertório · Sites e páginas

Referências públicas que o estúdio julgou bom ou premium, destiladas em princípio + medida. Formato e regras:
`LEIAME.md`. Referência é régua, não molde: extrair o princípio e superar, nunca copiar a forma.

### ST-01 · Home de estúdio de branding com cena de IA "que liga" — premium
- Fonte: https://gsaweb.com.br/ · licença/uso: só estudo
- O que é: 1ª dobra emoldurada como um aparelho; dentro, cena de IA de uma TV de tubo acesa no alto de um morro florido ao fim da tarde, sob o título "sair do improviso / construir com sistema".
- Princípio: a IA não faz "fundo bonito", faz o OBJETO-METÁFORA do título (uma tela que liga sozinha no meio do caminho = marca que chama atenção) e entra como CAMADA do sistema: céu removido (PNG transparente), céu em degradê de código, véu de código, grão de código. A moldura do site é a "carcaça"; a TV de IA é a tela dentro da tela.
- Medidas: moldura 1416×876 (`max(760, 100dvh−24)`), borda 6, raio 32; céu 180° #A9BFD3→#C9D7E3 34%→#E9E5DE 66%→#DDD2C3; imagem 3232×1504 a 140% da largura, presa à esquerda, base −9vw → TV cai a ~62% da largura; véu de baixo transparente até 46%, 38% a 72%, 82% no pé; título começa 184 px abaixo da borda (cabeçalho 84 + `clamp(48,7vw,110)`), 92 px, 2 linhas; base 1fr|380 (prova à esquerda, cartão de vidro à direita); faixa de 12 logos em 22 px. Celular: a MESMA imagem vira bloco "recorte da TV" (proporção 1,2; imagem a 140% da altura, centrada) que se dissolve no fundo escuro da base (degradê 58%→#0A0C0A).
- Por que converte/encanta: Id/Df/Ch — ninguém do setor mostra "TV no morro"; Le — o céu vazio é o papel do título em qualquer largura; Co — a luz da tela é a cor do botão.
- Como aplicar na nossa versão: achar 1 objeto do assunto do cliente que "acende/funciona" sozinho num lugar improvável; gerar só chão+objeto (céu/fundo liso para recortar), montar céu, véu e grão em código; definir 2 enquadramentos do MESMO arquivo (cena larga × recorte do objeto).
- Não copiar: TV de tubo, morro florido, moldura com aba, laranja.
- Tags: serviço criativo · IA como camada recortada · janela/aparelho

### ST-02 · Página "sobre" que troca a cena e mantém a moldura — bom
- Fonte: https://gsaweb.com.br/sobre · licença/uso: só estudo
- O que é: mesma moldura da home, agora com retrato REAL em estúdio escuro (luz de recorte azul) + 6 números em vidro.
- Princípio: página-irmã muda o conteúdo da tela, nunca a carcaça; IA fez o cenário da home, a pessoa é foto real; o texto que aponta para a foto muda com o layout ("do lado" no desktop, "embaixo" no celular).
- Medidas: foco da foto 74% 30% (rosto no terço direito); véu da esquerda 94%→60% a 36%→0 a 60% + véu de baixo 0→90%; título limitado a 58% da largura; números em grade 3×2 (780 máx.), número 52 px com sinal "+"/"×" laranja a ½ do tamanho encostado em cima; celular: foto vira 1:1 (foco 70% 22%) e o vidro vira branco 4% sem desfoque.
- Por que converte/encanta: Le (véu calculado, 4,0–8,8:1) · Fu (currículo vira prova) · Ch (mesma língua da home).
- Como aplicar na nossa versão: capa do professor/fundador com a moldura da marca, foto real dirigida para o terço livre; números que respondem "quem é" em vidro; microcopy espacial com 2 versões.
- Não copiar: luz azul de recorte, frase do "esse cara aí do lado".
- Tags: autoridade · retrato + painel de números · retrato + coluna

### ST-03 · Modelo de página de caso "arquivo aberto" — bom
- Fonte: https://gsaweb.com.br/projects/congresso-brasileiro-de-treinamento-feminino · licença/uso: só estudo
- O que é: capa = moldura com a arte do cliente + logo no "vão" do véu + título-cartaz + ficha de vidro; corpo = pranchas 16:9 em fila; fim = 2 pastas "ver mais".
- Princípio: um modelo único de caso (capa+etiqueta → pranchas → próximos → pedido); o véu deixa um VÃO limpo exatamente onde fica o protagonista; dado frio (categoria, data, site) em ficha ao lado do texto quente.
- Medidas: véu de 5 paradas (42% topo → limpo 22–48% → 50% a 74% → 86% pé); H1 900/50 `clamp(56,9vw,170)` = 130 px; ficha ≥ 300 px, 4 linhas de 50, vidro desfoque 16 + saturação 1,4, borda branca 22%, raio 18; pranchas 1288×725, vão 23, raio 28, hover 1,02 em 0,9 s; imagem acende 0→1 em 0,3 s com espaço reservado.
- Por que converte/encanta: Fu/Ch — trocar o projeto é trocar dados; Ac — lightbox com teclado e foco.
- Como aplicar na nossa versão: capa de caso com ficha "o quê · para quem · quando · link verificável"; usar o símbolo reduzido do cliente quando o slot é pequeno (ali o logo ficou 38 px no celular).
- Não copiar: a moldura e a forma de pasta deles.
- Tags: portfólio · véu com vão · palco com etiqueta

### ST-04 · Catálogo de marcas em espécime neutro (página de caso do mesmo site; endereço omitido) — bom
- Fonte: site público do estúdio · licença/uso: só estudo
- O que é: ~20 logos de um mesmo ecossistema, um por prancha, uma cor só, papel liso, centrado.
- Princípio: tirar cor e aplicação prova o TRAÇO e faz o conjunto parecer família; para ser justo, equalizar por ÁREA de tinta e centro óptico, não por largura.
- Medidas: tinta ocupa 15–33% da largura da prancha; 20 de 21 centradas a ±1 px; área de tinta variou 2,9× (falha); 3 pretos diferentes (falha); papel da prancha ≈ papel da página → borda some (falha).
- Por que converte/encanta: Fu (vende "várias marcas para um ecossistema") · Cr quando equalizado.
- Como aplicar na nossa versão: grade de 3 colunas com legenda HTML (nome · ano), famílias agrupadas com título curto, pausa a cada 6–8 itens, papel da prancha diferente do da página.
- Não copiar: os logos (são de terceiros).
- Tags: portfólio de logo · espécime · grade/mural

### ST-05 · Plataforma de estudo em saúde — página de venda escura — bom
- Fonte: https://lab.rodrigofenner.com.br · licença/uso: só estudo
- O que é: página de venda longa (11 seções, 1 fonte) de plataforma de biomecânica, toda contada como "sair do escuro".
- Princípio: o ritmo de fundo É o argumento: público "no escuro" → única seção clara no preço → fecho "pare de fazer no escuro"; respiro de cada seção escolhido pela intenção (denso · normal · decisão).
- Medidas: 8972 px a 1440; conteúdo 1008 (x 216–1224); respiros 86 · 115 · 144 px; colunas 5|7 ↔ 7|5 alternando o lado pesado, vão 86–101; espaço 4·8·12·16·24·32·40·48·64·80; área carvão 75% · navy 12% · claro 12% · acento 0,4%; rotina em 6 cartões 158×341 com chip "HOJE" lido do relógio; demo do app 1008×883 clicável, todo link fechado abre aviso com cadeado e "ver planos".
- Por que converte/encanta: Id 4 · Fu 4 · Ch 4 — a ideia cabe numa frase e toda seção a serve; o "proibido" da demo vira CTA.
- Como aplicar na nossa versão: achar a metáfora de estado do público do cliente (ruído→silêncio, bagunça→ordem, escuro→luz) e fazer a sequência de fundos contá-la; 3 respiros nomeados por intenção.
- Não copiar: escuro + laranja + navy, prumo, a frase do "escuro".
- Tags: educação em saúde · ritmo de cor como narrativa · venda longa

### ST-06 · Comunidade gratuita do especialista — captura com retrato em cor plena — premium
- Fonte: https://rodrigofenner.com.br/comunidade · licença/uso: só estudo
- O que é: captura grátis da marca pessoal, mesma linguagem do produto pago, mas com a cor de ação virando fundo.
- Princípio: quando o acento vira fundo, o botão inverte (vira a cor do texto) em vez de clarear; a grade técnica vira profundidade; a prova interativa fica presa ao lado do texto longo.
- Medidas: 6660 px; herói 910 px; foto recortada 634×819 (90% da altura), presa ao pé, saindo 128 px da caixa; texto ≤ min(672 px, 55%); H1 44 (o produto usa 56: aqui divide a tela com o rosto); botão carvão sobre laranja 15,8:1; topo laranja chapado até rolar 8 px; celular 352×576 sticky a 104 px do topo, filtros e curtidas que funcionam; 7 portas para 1 janela (3 campos + consentimento); área laranja 12% (no produto 0,4%).
- Por que converte/encanta: Df 4 · Co 4 · Fu 4 — rosto grande + cor plena + grade em foco = inconfundível; uma ação, nenhuma saída da página.
- Como aplicar na nossa versão: página da pessoa = cor-assinatura como fundo e rosto real; prova do produto do cliente (feed, agenda, painel) como objeto sticky ao lado do texto.
- Não copiar: laranja chapado com retrato de braços cruzados; feed de comunidade.
- Tags: educação · retrato em cor plena · captura gratuita

### ST-07 · SaaS de gestão de clínicas — palco de produto em camadas — bom
- Fonte: https://jdpmed.com.br · licença/uso: só estudo
- O que é: home de software clínico; entram o herói, a vitrine e a grade (a página inteira é normal-alto).
- Princípio: o produto é a prova, empilhado em 4 camadas de profundidade; as interfaces secundárias são HTML vivo.
- Medidas: texto centrado ≤ 860, H1 48/1,08, CTA 32 abaixo, palco 64 abaixo e sem respiro embaixo (encosta na faixa seguinte); c0 brilho do acento radial 60×60% a 26%, blur 60; c1 halo branco 70%, blur 40, 40 px além da janela; c2 dois satélites ±4° (300/280 px, opacidade .9, flutuam 10 px em 7 s, defasagem 1,4 s, endireitam no hover); c3 janela raio 32, sombra tingida 0 30 80 verde 14%. Vitrine: CTA ANTES do título; abas giram a cada 4,5 s.
- Por que converte/encanta: Fu 3 · Le 3 — mostra em vez de ilustrar; Df 2 (SaaS verde comum) segura a nota.
- Como aplicar na nossa versão: atrás do objeto-prova do cliente, 1 brilho da cor-sinal + 1 halo do fundo; 2 satélites inclinados com 2 funções reais.
- Não copiar: dashboard verde, satélites de kanban/WhatsApp.
- Tags: saas saúde · camadas de profundidade · palco de produto

### ST-08 · Produtora de eventos de Educação Física — home — premium
- Fonte: https://timmeventos.com.br/ · licença/uso: só estudo
- O que é: home em que a página É o credenciamento do visitante.
- Princípio: contar o serviço na ordem do ritual, com os objetos que o cliente segura (crachá → fita da entrada → palco → ficha → ingresso); cada dobra é um objeto, não um cartão genérico.
- Medidas: 11 439 px a 1440; container 1240, lateral clamp(16, 5vw, 64); H1 de 3 palavras em 3 linhas, 140/60 px, entrelinha .95; seções 90–150 px; ~55% escuro · 35% papel · 7% cor chapada · 3% metálico; 15 dobras: promessa → pertencimento → dor → virada → número → prova → pós-venda → benefícios → pessoa → processo → oferta → prova → FAQ.
- Por que converte/encanta: Id 4 e Fu 4 — entende-se o serviço pelo que se segura; Ac 4 — o nome digitado no crachá reaparece na ficha.
- Como aplicar na nossa versão: listar o que a pessoa recebe, assina ou carrega do 1º contato ao pós-venda do cliente e dar um desses objetos a cada dobra.
- Não copiar: crachá com cordão listrado, coroa, navy + folha de ouro, o lema de 3 palavras.
- Tags: eventos/educação · objeto do ritual · página-jornada

### ST-09 · Escola de conteúdo — inscrição para live de Black Friday — bom (alto)
- Fonte: https://combo.brandsdecoded.com.br/black-brands/b · licença/uso: só estudo
- O que é: página-túnel de inscrição gratuita (sem menu, sem rodapé de navegação); 6 botões iguais abrem 1 pop-up.
- Princípio: curiosidade como oferta — o preço fica escondido, data e canal ficam explícitos; o kit inteiro sai de UMA liquidação de loja (etiqueta, estrela de oferta, picote, letreiro, preço riscado).
- Medidas: herói = tela − 60 px (a faixa corrida fecha a 1ª tela); coluna 1200, texto do herói 528; H1 81,8 px = 15,5% da coluna, entrelinha .8; 70 preto · 20 creme · 10 coral; raio único 4 px ("etiqueta, não app"); claro/escuro alterna 3× em 10 dobras; regra de altura (≤ 940 e ≤ 800 px) mantém o botão sem rolar.
- Por que converte/encanta: Fu 4 e Ch 4 — nada é enfeite; Le 4 — data + canal num selo legível ao lado do botão.
- Como aplicar na nossa versão: pegar o objeto comercial da categoria do cliente (cupom, ficha, rótulo, recibo, pulseira) e derivar dele forma, linha, selo e gesto.
- Não copiar: etiqueta pendurada com canhoto, estrela de 11 pontas, coral + preto, itálico condensado.
- Tags: infoproduto · kit de um objeto · página-túnel

### ST-10 · Curso de IA para designers — página de venda — bom (beira premium)
- Fonte: https://www.thiagor.net/dgia · licença/uso: só estudo
- O que é: venda de curso com o par "humano + IA" em que o humano fica sempre por cima (título, decisão, rosto).
- Princípio: a metáfora mora na tipografia e no movimento, não em ilustração — ícones de rosto e robô dentro da linha do H1, 1 palavra em degradê por título, etapas que acendem, mãos que se encontram no fim.
- Medidas: 14 277 px a 1440; wrap 1264 (1200 + 2×32); espaço base 4 (… 24 · 32 · 48 · 96 de seção); H1 74,9 px, entrelinha .94, tracking −4%; ícone na linha .74 em, raio .18 em, base −.06 em; 10 papéis de texto; 3 níveis de cinza (#F9F9F9 · #A7A7A7 · #646464); 1 inversão clara só antes da oferta; 7 botões, todos com o preço no texto.
- Por que converte/encanta: Le 4 e Ch 4 — sistema escrito e obedecido; o botão responde "quanto custa" em todo ponto de saída.
- Como aplicar na nossa versão: achar o par de opostos do assunto do cliente e pôr os dois DENTRO da linha do título, com ícone desenhado no traço da marca (não emoji).
- Não copiar: preto + degradê laranja, ícones rosto/robô, a cena das duas mãos, a metáfora do chef.
- Tags: curso/IA · metáfora tipográfica · venda longa
