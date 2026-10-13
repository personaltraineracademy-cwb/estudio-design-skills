# Receitas de dobra aprovadas (com os parâmetros reais)

> Cada receita é uma **ideia gráfica** para a 1ª dobra dentro do MESMO
> contrato (`padrao-de-pagina.md` §2: tela inteira · imagem → título → apoio + linha → botão → micro · um eixo ·
> mesma composição em todas as larguras). Receita = **ponto de partida e princípio, nunca cópia**: a ideia nasce
> do assunto/logo do cliente novo. Antes de adotar uma, responder por escrito (em `docs/decisoes-do-projeto.md`):
> "qual é a UMA ideia da tela?" e "se eu tirar a foto, o resto ainda é uma composição?".
>
> Medidas em px de CSS. `cqw` = % da largura do contêiner (`container-type: inline-size` na moldura da imagem):
> nunca `vw` em layout (a barra de rolagem de 15 px estraga a conta). Vãos da dobra: **12 · 24 · 40**.

## Como escolher

| Receita | Quando serve | Evitar quando |
|---|---|---|
| **Holofote** (padrão do template) | 1 pessoa ou grupo recortado; marca com uma cor forte; quer simetria e conversão | foto sem recorte limpo; muita cópia na dobra |
| **Sala de controle** | ao vivo, transmissão, tecnologia; texto + imagem em 2 colunas no desktop | marca delicada/acolhedora |
| **Placar** | 2–4 pessoas/produtos/noites com cor própria cada | uma pessoa só |
| **Dossiê (faixa)** | documento, bastidor, "confidencial"; papel × preto | foto larga demais para a faixa |

Nenhuma receita aceita: logo repetida na dobra, eyebrow, selos, etiqueta com o nome da campanha, faixa/ticker dentro
da 1ª tela, camada solta sem origem no grid ("listra", painel escuro flutuando).

---

## 1. Holofote (aprovada: "esse ficou muito bommmm")

**Ideia:** um disco da cor de destaque (o holofote) atrás da(s) pessoa(s), que o rompem (cabeças e ombros saem do
disco), com um anel fino afastado. Abaixo, título, apoio, botão. Tudo no eixo central.

**Ordem:** IMAGEM → H1 → apoio + linha mono → BOTÃO → micro. Uma coluna, todas as larguras.

**Parâmetros reais (v2, 8ª versão):**

| Peça | Valor |
|---|---|
| Imagem (largura) | `min(100%, 940px, max(520px, (100svh − 465px) × 1,8))` — a ALTURA da janela manda: título e botão sempre na 1ª tela (1024×768 → 1920×1080) |
| Disco | ø **48cqw**, `top: −3cqw`, `left: 50%`, `translateX(−50%)`, atrás do tronco (nunca aparece o arco embaixo, entre os braços) |
| Preenchimento | `radial-gradient(circle at 50% 32%, destaque+80% branco 0%, destaque 56%, destaque+82% preto 100%)` |
| Anel | `box-shadow: 0 0 0 1.4cqw <fundo>, 0 0 0 calc(1.4cqw + 2px) <tinta>` |
| Movimento | `v2-holofote`: opacity 0→1 + escala .55→1 em **0,9 s**, `cubic-bezier(.2,.7,.2,1)`, atraso .05 s, **backwards**, uma vez; a foto NÃO anima (LCP) |
| Vãos | cabeçalho↔imagem **24** · imagem↔H1 **32** (celular) · H1↔apoio **16** · apoio↔linha **12** · linha↔botão **24** · botão↔micro **12** |
| H1 | `clamp(2.5rem, .8rem + 3.2vw, 3.5rem)`, `max-width: 21em`, `text-box: trim-both cap alphabetic`, centrado |
| Botão | `min-height: 60`, `white-space: nowrap`, largura total < 600, centrado ≥ 600 |
| Respiro | `padding: 24px topo · 72px base` (todas as larguras) |
| Foto | recorte com alfa, **centrado pela tinta**, base com fade que some no fundo (sem faixa/chão) |

**No template** (`components/secoes/Hero.tsx` + `styles/pagina.css`): `--holo-f = 1/(1/proporção + 0,045)` (o ar de
4,5cqw do topo guarda o anel), `--holo-resto` 590 px (celular) / 520 px (≥ 600): é a soma do que sobra além da
foto. **Calibrar o `resto` para a copy do cliente** (H1 de 2–4 linhas): CTA termina em ≤ 82% (celular) / ≤ 92%
(desktop) da altura. Sem foto: o disco sozinho, a mesma composição.

**Por que as 6 anteriores foram reprovadas (não repetir):** faixa fina cortando as pessoas no peito; título e apoio
lado a lado; título monumental com trio no entalhe; 2 colunas; trio sobre o preto da seção seguinte; PALCO de
estúdio gerado por IA ("faixa larga e chapada 3:1 = banner genérico; trio cortado; texto pequeno embaixo; sem
ideia"). Cenário de IA sem uma ideia gráfica não vira composição.

**Aviso conhecido (justificado):** em 768/1024/1440 o `check_pagina.py` pode dizer "topo das colunas desalinhado"
(entende a foto centrada como coluna da direita). É o falso positivo documentado do holofote.

---

## 2. Sala de controle (v1, "perfeita")

**Ideia:** a dobra é um VISOR de câmera: moldura com 4 cantoneiras que "travam foco" sobre a foto; ao vivo, timecode
de estado real. Mobile empilhado; desktop em 2 colunas.

| Peça | Mobile (< 768) | ≥ 768 | ≥ 1024 |
|---|---|---|---|
| Ordem | foto (`order:-1`) → H1 → destaque → data → botão → micro | idem; foto `width: min(100%, 480px)` | **12 colunas**, gap 24: texto `1/7`, foto `7/13` (`object-fit: contain`), alinhadas pelo topo das MAIÚSCULAS do H1 e pela base do micro |
| Respiro vertical | `96 topo · 128 base` | `112 · 112` | `112 · 112`, `min-height: 100svh − 72px`, centrado na altura |
| H1 | `min(var(--fs-h1), 11cqi)` medido pela coluna (3 linhas) | idem | `min(5vw, 10vh, 4.75rem, 11cqi)`, `text-wrap: wrap`, `text-box: trim-both cap alphabetic` |
| Destaque (diferencial) | margem 24, 700, cor de destaque, `text-wrap: balance` | idem | margem 40 |
| Data (mono) | margem 12 | idem | idem |
| Botão | largura total | `min(100%, 420px)` à esquerda | 1024–1199: coluna inteira (borda direita = a do H1); ≥ 1200: 420; `min-height: 64` |
| Micro | margem 12, 16 px | idem | `text-box: trim-both cap text` |

**Visor:** `::after` com 8 `linear-gradient` (2 por canto), `--l: 16px` (26 px em painéis grandes), `--t: 3px`,
`inset: 0`, `z-index: 4`. **Movimento:** `v1-travar` 0,65 s, atraso 0,15 s — as cantoneiras entram ~8% maiores,
passam 1,5% e assentam; foto e H1 não se mexem. Repete no fecho (cantoneiras fecham o quadro) e no hover.

**Armadilhas medidas:** barra do monitor `nowrap` alarga a trilha `1fr` (usar `minmax(0,1fr)`); `text-box` com
quebra em 3 linhas depende de peso 500 vs 400 (compensar com `letter-spacing: −0,009em`); janela do título por
linha tem que preservar til/acento (folga de 0,2em só em cima).

---

## 3. Placar (v3)

**Ideia:** 3 painéis lado a lado (01 · 02 · 03), cada um na cor do produto, com o rosto inteiro, numeral grande
ACIMA da cabeça e nome + dia ao pé. O placar "acende" de baixo para cima e o dígito "vira".

| Peça | Mobile | ≥ 1024 |
|---|---|---|
| Faixa de painéis | grid `repeat(3, minmax(0,1fr))`, gap 8 (12 ≥ 600), `margin-bottom: 40`, **vem antes do texto** | coluna `8/−1` (texto `1/8`; em 1024–1279: `7/−1` e `1/7`), `contain: size`, altura = a do texto |
| Painel | `container-type: inline-size`; altura = `var(--ph) × 1cqw + var(--band)`; `--ph: 126` (168 < 768 para o rosto crescer); `--band: 52px` | `--band: 56px`, altura `auto` (flex) |
| Cor | `::before` na cor do produto, `inset: 0 0 var(--band) 0`, sobe de baixo (`v3-enche` 0,62 s, atrasos 0 / 0,1 / 0,2 s) | idem |
| Pessoa | `<img>` `object-fit: cover; object-position: 50% 0`, recorte de busto próprio para celular (`*-bust-m`, 370×641) e desktop (`*-bust-d`) | idem |
| Fade ao pé | `linear-gradient(180deg, transparent calc(100% − band − 14cqw), fundo calc(100% − band))` | idem |
| Numeral | `font: 900 40cqw/0.8 display`, `top: 4cqw`, centrado, cor do fundo (tinta sobre cor); recuar a folga da fonte (`--hb`) | `46cqw`, `top: 6cqw` |
| Nome | `text-lead`, `text-box: trim-both cap alphabetic`; data em mono na cor de destaque | idem |
| Texto | H1 `clamp(2.5rem, 11.4vw, 3.25rem)` (celular); tarja de destaque `900 clamp(1.25rem, 5.6vw, 1.75rem)/1.3`, `padding: .04em .3em`; `.acao` margem 28; botão margem 40 | grid de 12 colunas, `padding-block: --sec`, texto centrado na altura |

**Fecho:** o placar fecha como abriu (3 painéis + frase + botão), sem listras nem segunda camada. **Rosto pequeno
no celular** (~65 px): não dar zoom por CSS (corta o queixo); refazer o recorte mais fechado (`bust-m`, rosto ~45%
maior, mesma caixa, centrado pelo ROSTO com YuNet, fade de 14% embaixo).

---

## 4. Dossiê — faixa de borda a borda (v2, proposta 1)

**Ideia:** faixa preta (a tarja do documento) de borda a borda ATRÁS do tronco, imagem centrada por cima; a faixa
nasce da forma, não é um painel solto. Servia a dobra antes do holofote e continua válida para "documento".

| Peça | Valor |
|---|---|
| Imagem | `width: min(100%, 420px)` (celular) · `min(100%, 560px)` (tablet) · desktop `min(100%, 680px, max(460px, (100svh − 470px) × 1,8))`; centrada pela tinta |
| Faixa | `::before` com `top: 30.5cqw` (ombro), `bottom: 0`, `left/right: −200cqw` (sangra pela medida da imagem, **sem `100vw`**), `overflow-x: clip` na seção; piso de `3cqw` sob a imagem (é onde ela "afunda" ao rolar) |
| Texto | H1 e apoio (sub · data · botão) lado a lado no desktop, alinhados pelo TOPO das maiúsculas e pela BASE (`text-box: trim`); celular empilhado |
| Vãos | 24 (cabeçalho↔imagem, H1↔apoio) · 40 (imagem↔H1, data↔botão) · 12 (sub↔data, botão↔micro) |
| Movimento | a faixa sobe atrás (0,8 s) e a imagem sobe 28 px com fade .35→1 (**nunca de 0**: o LCP pinta no 1º quadro); ao rolar a imagem afunda até 9% (`scroll()`, só total) |

**O que reprovou outras versões desta dobra (reconhecer):** painel escuro retangular solto no canto da área clara
("quadradão preto no meio do quadrado branco"); duas camadas desligadas (foto pequena em cima, texto embaixo, 40%
vazio nos lados); hierarquia quebrada (título embaixo, botão longe). O mobile aprovado NÃO escala por esticamento:
no desktop, recompor.

---

## 5. Arquétipos do repertório (dobras premium medidas; escolher pelo argumento, nunca copiar)
Fichas completas com medidas: `../../revisao-de-design/references/repertorio/sites.md`; técnicas: `../../direcao-de-arte/references/tecnicas-avancadas.md`.
| Arquétipo | Esquema | Quando |
|---|---|---|
| Aparelho com cena | moldura de tela inteira; título no terço de cima à esquerda; objeto-metáfora (IA) a ~62% na diagonal; base 1fr\|380 (prova \| cartão) | herói de estúdio/marca com ideia forte |
| Palco de promessa | coluna única; H1 2 linhas → régua 48×1 → sub 60ch → CTA → prova colada ao CTA; vazio escuro em volta | captura direta |
| Retrato em cor plena | texto ≤ 55% à esquerda; pessoa recortada presa ao pé (90% da altura) saindo da caixa; grade atrás | página da pessoa/autor |
| Holofote + objeto pessoal | 62/38; H1 de 3 palavras; objeto do ritual pendurado no terço direito | evento, inscrição |
| Palco de produto em camadas | texto centrado 40% em cima; janela do produto (60%) encostando na dobra seguinte; 2 satélites ±4° | SaaS, plataforma |
| Coluna fixa + lista | 45/55; esquerda sticky (título, lead 40ch, CTA); direita 4–5 itens | serviços, benefícios |
| Texto longo × prova presa | 7\|5; prova sticky a ~104 px do topo enquanto o texto rola | argumento longo |
| Palco fixo (A4) | palco sticky 60% + 3–5 passos de 75–100 svh; 1 mudança por passo | método, como funciona |
| Título + número que responde | título 16ch à esquerda, número 63 px à direita; 3 cartões com pílula | objeção de prazo/quantidade |
| Placar-pirâmide | 40/160/38 px na mesma largura (salto 4:1) + mural de prova a 7% | prova numérica |
| Grade de lâminas | problemas numa grade de 1 px 3×2 com número pequeno | dores/sintomas |
| Sintomas + virada | título ≤ 12ch; alertas em 2 colunas; bloco escuro largo com rótulo vertical | virada de tom |
| Fluxo → destino | 7 nós ao redor, raios para o centro; o fio mais longo desce até a oferta | "tudo leva ao produto" |
| Espinha de decisão | 1fr · 96 · 1fr: o que a ferramenta faz × a decisão humana; nó no eixo | IA/ferramenta × pessoa |
| Lista riscada em escada | 4 palavras gigantes centradas, larguras diferentes, riscadas uma a uma | alívio, "o que some" |
| Objeto de trabalho do público | 37/63; ficha/prancheta girada 0,6° com marcas só nas etapas feitas | conteúdo do curso |
| Esteira sangrando · Gaveta de pastas | cartões cortados nas 2 bordas (110 s) · pastas sangrando à direita | portfólio, quantidade |
| Luz na decisão | única seção clara da página escura; 2 cartões, o recomendado com sombra e pílula metade para fora | preço |
| Palco central + objeto especial | cartão de preço 560 no eixo com halo; bônus 320 girado 2,4° ao lado | oferta |
| Fita de costura | faixa da cor de ação a −1,4°, 104% de largura, sobe 26 px sobre a dobra anterior | passagem escuro → claro |
| Cofre | painel escuro arredondado só para tese, segurança e fechamento | assunto sério |
| Fechamento que reencontra o herói | única composição simétrica; par simbólico + display ≤ 15ch + botão | última dobra |

## Antes de adotar qualquer receita

1. Inventário da dobra por escrito (elemento · papel necessário/duplicado/decoração · fica/sai) — `paginas-de-captura.md` §4d.
2. Orçamento de altura somado em px para 360×740, 390×844, 768×1024, 1024×768, 1440×900; sobra ≥ 40 px.
3. Foto: recorte limpo, centrada pela tinta, 2 larguras (640/1100) em WebP; pessoas reais, nunca IA.
4. Rodar `site.py check` e olhar rolando de verdade (a captura de página inteira recorta a barra de rolagem).
