# Lições de página — captura, vendas, evento

Regras genéricas que vieram de muitas rodadas de reprovação. Contrato técnico e dobras: `padrao-de-pagina.md`,
`receitas-de-dobra.md`, `contrato-tecnico.md`. Gosto: `../../revisao-de-design/references/gosto.md`.

## Conteúdo
- Só COPY FINAL na página — orientação, colchete, "o que evitar" e variações vão para um arquivo de pendências; nota interna na página é reprovação imediata.
- Nunca inventar preço, "de/por", urgência, contador ou número — porque é risco legal e quebra confiança.
- Logo sempre presente, UMA vez (no cabeçalho) — porque repetir o nome 3–5 vezes na 1ª tela soa prolixo.
- Número, resultado e prova sempre em HTML, nunca só dentro de imagem — porque não se lê no celular nem por leitor de tela; logo de cliente exibido nunca abaixo do tamanho mínimo dele.
- Número-título ao lado do título da seção (prazo, quantidade) responde a objeção antes da pergunta.
- Interação que vira dado (nome digitado num objeto do ritual) e reaparece mais abaixo vale mais que efeitos; a página funciona sem o dado salvo.
- Demo de produto: clique em conteúdo fechado abre aviso curto com o CTA, nunca link morto.

## Primeira dobra
- Dobra = tela inteira, conteúdo centrado na altura; a seção seguinte não aparece — porque dobra curta parece inacabada e 1/3 vazio embaixo também.
- Dobra = logo + imagem + título + 1 apoio (diferencial + data numa linha) + 1 botão; sem eyebrow, selo, carimbo ou parágrafo — porque cada extra rouba leitura.
- Ordem imagem → título → botão, um eixo, botão colado ao texto — porque foto e texto são parceiros, não camadas desligadas.
- Altura da imagem calculada pelo resto da dobra (clamp), nunca fração fixa da tela — porque em notebook baixo o botão sai da tela.
- Uma ideia gráfica forte e simples na dobra — porque cenário de IA genérico não substitui ideia.
- Dobra reprovada 2 vezes seguidas: parar de remendar e redesenhar do princípio (um eixo, uma ordem, uma ideia) — porque o 6º remendo de uma ideia fraca continua fraco.
- Trio/placar de pessoas: recortes normalizados pela caixa do rosto detectada (mesma altura de rosto e olhos) — porque cabeças de tamanhos diferentes leem como erro.
- Antes de codar: inventário (necessário · duplicado · decoração), um lugar por elemento, altura somada em px.
- Cena de IA como CAMADA: gerar só chão + objeto com fundo liso; céu/fundo em degradê de código, véu e grão em código (cabe em qualquer largura).
- Hero com cena de IA = 2 gerações (16:9 e 9:16, objeto maior no celular), ou 2 enquadramentos planejados do mesmo arquivo dissolvendo na cor do bloco seguinte; recorte improvisado não vale.

## Respiro e sistema
- Uma mensagem por tela, ≥ 38–50% vazio, seções com 96–200 px, ≤ 1 decorativo e ≤ 6 tamanhos de texto por tela.
- Espaço só da régua do sistema; margem esquerda = direita; cabeçalho e conteúdo no MESMO container.
- Texto de apoio ≥ 16 px; rótulo de botão em 1 linha em toda largura (360 px incluso).
- Mesma composição em todas as larguras — porque uma composição aprovada vale para todas.
- Toda correção reexecuta o sistema inteiro em todas as seções e larguras — porque consertar só o apontado comprime o resto.
- Uma cor de ação com papel único (ação ou dado), na ordem de 1% da área — porque o olho aprende "cor = importante" e a página vira mapa de prioridade.
- Virada de argumento = trocar o mundo de fundo (escuro × claro) a cada 1–2 dobras, sem elemento novo.
- Sistema amarrado numa conta: raio interno = raio externo − borda/recuo; uma família variável faz vários papéis só com peso e largura.
- Lista sem peso visual: grade de 1 px (vão de 1 px + fundo da cor da linha + raio só no contêiner).

## Páginas irmãs (família)
- O que não muda (dobra, espaços, ordem) é UM componente compartilhado, criado antes de variar — porque instrução em briefing não segura padrão; código segura.
- Só mudam arte, elementos, cor e fonte; espaçamento, dobra e método são fixos.
- Inovação só como proposta nomeada ao lado da base, com justificativa — porque "lançar e ver se dá certo" volta vermelho.

## Cor por produto
- Cor da marca-mãe só na página principal; nas irmãs, a cor do produto (botão, sublinhado, bloco de oferta, elementos).
- Texto corrido em tinta/papel; cor do produto só em área ou numeral grande.
- Varrer cor proibida também em SVG com cor assada e no arquivo do logo — porque a cor retirada sobrevive em arquivo esquecido.
- Página escura: a ÚNICA seção clara é a do preço (contraste máximo na decisão).
- Na página da marca-mãe, o produto entra numa seção da cor DELE e o CTA continua o da página (produto como próximo passo).

## Elementos e imagem
- Kit de elementos revisado ANTES da página; inventário "elemento → onde entra".
- Elemento só com função: verdadeiro, lógico, bonito; decoração solta sai.
- Pessoa = foto real recortada, centrada pela tinta (contorno), sem halo; recorte mais fechado em vez de zoom por CSS.
- IA só para cenário/complemento, com prompt profissional e tratamento; rótulos em código; proposta ao lado da base.
- Produto digital como herói: telas/mockups feitos em código (animáveis, nítidos), com brilho e sombra tingida da marca; o dado real (contagem, histórico) pode ser prova e ornamento ao mesmo tempo.
- Grão sutil (mais leve em página toda escura); escuro nasce de faixa de borda a borda, nunca bloco flutuando.

## Movimento
- Movimento SEMPRE ligado, linguagem única e simples por página.
- Para quem reduz movimento: mesma coreografia em versão suave, nunca parada.
- Estado natural do CSS = estado final; animação de rolagem com `forwards`, nunca `both` — porque bloco some em captura e sem JS.
- Movimento com nome e poucos gestos com tempos fixos; cada animação explica uma ideia (etapa acende = processo avança), senão é enfeite.
- Esteira (faixa em laço): cópias suficientes para cobrir 2× a largura e deslocamento de exatamente uma cópia — porque número errado de cópias dá pulo no fim do laço.
- Transição imagem→interface: `clip-path: inset()` com o mesmo nº de valores nos dois estados; reduzido = fade de 400 ms.
- Vídeo pela rolagem = sequência de WebP em canvas (≤ 120 quadros, DPR ≤ 1,5, carga em etapas), nunca `currentTime` em MP4 comum.
- Parallax de profundidade ≤ 2–3 % com `<img>` + alt por baixo do canvas; borda esticada = defeito.
- Receitas completas (homografia, cinemagraph, scroll-scrub, máscara): `../../direcao-de-arte/references/ia-imagem-video.md` §12.
- Eixo variável na rolagem: 1 título por tela, estado final = peso do sistema, nunca no H1/LCP. Mola (`linear()`) só em micro-interação tátil, 350–600 ms, ultrapassagem ≤ 4%.
- View Transition: 1 elemento nomeado por navegação, 250–400 ms. No Next estático, `<Link>` não troca de documento: usar `document.startViewTransition` ou `<a>` comum.
- Logo no site troca por largura do CONTÊINER (`@container`), no máx. 3 estados, símbolo ≥ 24 px.

## Testar como o cliente vê
- Navegador real com barra de rolagem clássica (15 px) e movimento reduzido ligado e desligado — porque o headless esconde os dois.
- Nunca `100vw` em layout — porque a barra empurra conteúdo para fora da coluna.
- Larguras: 360, 390, 768, 1024, 1280×720, 1440×900; paisagem no celular.
- Captura de página inteira só depois de rolar até o fim (reveal, lazy e contador disparam ao rolar).
- Olhar rolando seção por seção; "passou no verificador" ≠ organizado.
- Tema claro/escuro: pares de tokens desde o 1º componente; conferir a página INTEIRA nos dois temas, contraste medido nos dois.
- Correção que o cliente apontou e o verificador não pegou vira checagem nova, na hora.
- Contraste medido no ESTADO FINAL de cada componente (hover, herdado, sobre foto): texto de botão herdado e acento claro sobre fundo claro passam despercebidos.
- Palavra destacada em `inline-block` não quebra junto com a pontuação: o ponto final cai sozinho na linha no celular — conferir quebras a 360/390.
- Varredura numérica própria (cor proibida, transbordo, botão dentro da dobra) antes do olho; no máximo 2 rodadas de correção (`../../revisao-de-design/SKILL.md`).

## Entrega
- Tecnologia de produção (site estático que sobe em hospedagem comum), não arquivo solto.
- Build + verificadores depois de TODA edição de CSS; instalação limpa do zero antes de empacotar.
- Testar raiz E subpasta com zero requisição falha.
- Pacote enxuto: zips (raiz, subpasta, fonte) + prévias regeneradas na hora — nunca prévia copiada de rodada antiga.
- Pop-up de captura só por clique, acessível (foco, ESC, erro claro), fechar não apaga o que foi digitado.
