# IA de imagem e vídeo: regras congeladas

Base: pesquisa de imagem e vídeo com IA (15) e de anúncios Meta (5 §1.3), mais `camadas.md`, `qualidade.md` e
`../brand-studio/references/composicao.md`.
Origem entre parênteses: "(15 §3.1)" = pesquisa 15, seção 3.1; "(5 §1.3)" = pesquisa 5. Número sem fonte =
**[ponto de partida]**. São REGRAS: peça que quebra uma é refeita, ou o porquê vai para o diário.

## 1. Regra-mãe: IA = cenário, metáfora, textura. Foto real = prova (15 §0.1, §4.2)

1. **Prova é sempre real:** professor, aluno, turma, depoimento, resultado, bastidor, estrutura, certificado, produto.
   O olhar vai para "pessoas reais da empresa"; foto genérica é ignorada (15 §4.1, §4.2).
2. **Nunca pessoa inventada como prova.** Gente realista de IA só como figurante distante ou desfocado, nunca como
   "aluno", "depoimento", "resultado" ou "especialista" (15 §3.4.2; CONAR Anexo Q 5.1 em 15 §3.2).
3. **Ideia antes da ferramenta:** a peça se explica em 1 frase sem a palavra "IA". O backlash (Coca-Cola, McDonald's,
   Svedka) vem de IA no lugar da ideia e no lugar de pessoas e emoção (15 §1.1, §1.3).
4. **IA no impossível ou caro demais**, junto com material real e o mesmo acabamento (padrão "ANCESTRA") (15 §1.1).
5. **Confiança de alto risco** (saúde, corpo, dinheiro — curso de educação física está perto) → ainda mais foto real
   (15 §4.2).
6. **Não vender "feito com IA"** (a palavra reduz a intenção de compra); declarar onde a regra exige e nunca negar
   (15 §4.1, §4.2).

## 2. IA × foto real × código: quem faz cada imagem

| Tipo de imagem | Quem faz | Regra | Origem |
|---|---|---|---|
| Professor, especialista | **foto real** dirigida para o layout | IA só no cenário em volta do recorte; nunca no rosto | 15 §3.4.1, §2.6 |
| Aluno, turma, depoimento, resultado, antes/depois, bastidor, academia, produto | **foto/vídeo real** | é prova; nunca IA, nem "parecido" | 15 §3.4.2–4, §4.2 |
| Fundo de hero, cenário vazio, bokeh para tipografia | **IA** (Nano Banana 2.1) | espaço do texto já no prompt | 15 §2.7 (1, 2, 8) |
| Ambiente para pessoa recortada | **IA** + composição em código | luz do prompt = luz da foto | 15 §2.6, §2.7 (3–4) |
| Objeto-símbolo fotográfico, cena surreal de campanha | **IA** | objeto que "funciona" (§5); uma luz com motivo | 15 §1.1, §2.7 (5, 7) |
| Textura fotográfica (borracha, giz, concreto) | **IA** | luz chapada, sem perspectiva, para repetir | 15 §2.7 (6) |
| Textura gráfica (grão, papel, meio-tom, estática) | **código** (`fundos.py`, `efeitos.py`) | grão único da série | camadas.md §3.5 |
| Objeto/número 3D da marca (cromo, vidro, neon) | **código** (`render3d.py`) | forma exata da marca | composicao.md |
| Logo, elemento, padrão, ícone | **código** (`elements.py`, `pattern.py`) | IA não gera vetor nem é exclusiva | 15 §3.3 |
| Texto, preço, data, número, botão, selo, contador | **código** | sempre por cima (L7–L8) | 15 §3.4.5 |
| Mockup de celular/notebook | **IA** com tela verde `#00FF00` | a tela real entra em código | 15 §2.7 (9–10) |
| Mockup com a marca (cartaz, outdoor) | `mockup.py` | IA faz a cena; o código encaixa a arte | `../brand-system/scripts/mockup.py` |
| Multidão | IA só **desfocada** ao fundo | rosto de multidão é onde a IA mais erra | 15 §1.3 (9) |
| Quadro-chave de vídeo | **IA** (Nano Banana → Veo/Omni) | 1º = último quadro para loop | 15 §2.7 (12) |
| Famoso, sósia, "parecido com", pessoa morta | **ninguém** | proibido (§8) | 15 §3.4.3 |

## 3. Receita de prompt para o Gemini (imagem)

**Estrutura fixa, nesta ordem, em UM parágrafo narrativo em inglês** (15 §2.4, §2.7):

| # | Bloco | Escrever | Origem |
|---|---|---|---|
| 0 | Verbo + finalidade | "Generate a … for the hero of a course website, text on the left" | 15 §2.4 (2, 6) |
| 1 | Cena | assunto + ação + lugar, hiperespecífico ("tweed azul-marinho", não "paletó") | 15 §2.4 (1) |
| 2 | Luz | UMA luz com motivo: de onde vem, dureza, hora ("window light from the left, late afternoon") | 15 §1.3 (3) |
| 3 | Lente/câmera | mm, f/, altura, ângulo, aparelho ou filme ("Fujifilm", "1980s color film, slight grain") | 15 §1.3 (2), §2.4 |
| 4 | Material | o material exato + imperfeição (poeira, marca de uso, tecido amassado) | 15 §1.3 (5) |
| 5 | Paleta | 2–3 HEX da marca + neutros (reforçada depois no mapa de cor em código) | 15 §1.3 (4) |
| 6 | Espaço do texto | lado/zona calma, escura, sem detalhe — pela zona do formato (`qualidade.md`) | 15 §1.3 (7) |
| 7 | Proibições | no POSITIVO ("empty street", não "no cars") + "no text, no letters, no logos, no watermark" | 15 §2.4 (4) |
| 8 | Formato | proporção final ("Aspect ratio 4:5"); nunca gerar quadrado para cortar | 15 §2.5 |

**Bloco fixo da série** (colar no fim de todos) (15 §2.7): `Shot on [Fujifilm GFX, 50mm, f/2.8]. [One motivated
light: …]. Color palette restricted to [#hex1], [#hex2] and neutral greys. Subtle natural film grain, real-world
imperfections, no text, no letters, no logos, no watermark.`

- **Edição = o que muda + o que fica igual** ("change only …, keep everything else exactly the same"); a saída copia a
  proporção da ÚLTIMA imagem enviada (15 §2.3, §2.4 (7)).
- **Gente que não parece banco de imagem:** idade do público, gesto no meio da ação, luz real, "candid, unposed,
  documentary, not stock photo" (composicao.md). **Mão:** "five fingers clearly separated"; 2 falhas → cena sem mão
  (15 §2.7). **Deriva** do rosto/estilo → recomeçar a conversa com a descrição completa (15 §2.4 (9)).
- Comando: `python gemini.py gen "<prompt>" -o out/cena --aspect 4:5 --size 1K --n 4 [--ref ancora.png] [--casa
  "Cliente/Projeto"]`; objeto isolado: `--element --cutout`. O script já soma "no text, no letters, no logos" (exceto
  com `--allow-text`, que peça final não usa) (`gemini.py --help`).

**Os 12 modelos** (texto completo em 15 §2.7; todos com o bloco fixo e sem texto):

| # | Para quê | Essência do prompt | Formato |
|---|---|---|---|
| 1 | Fundo de hero de site | sala vazia, interesse no terço direito, **2/3 da esquerda calmos e escuros** para título e botão; 35 mm | 21:9 / 16:9 |
| 2 | Hero no celular | mesma cena; objeto no terço de baixo, **55% de cima vazios** para 2 linhas; 50 mm | 9:16 / 4:5 |
| 3 | Estúdio para foto recortada | fundo infinito **sem pessoa**; luz igual à da foto (softbox 45°, contorno); 85 mm; poça de luz onde ela fica | 4:5 / 9:16 |
| 4 | Ambiente real para recorte | laboratório/academia vazios, desfocados mas reconhecíveis; luz da janela = luz da pessoa; desgaste real | 4:5 / 16:9 |
| 5 | Objeto-símbolo | um objeto em fundo liso, softbox + luz de recorte, foco no detalhe, poeira e digitais, folga para cortar | 1:1 |
| 6 | Textura/material | macro de cima, luz uniforme, sem perspectiva nem vinheta, para repetir | 1:1, 2K |
| 7 | Cena surreal | objeto-símbolo gigante num lugar real, figura humana minúscula para escala, céu limpo para o título | 4:5 |
| 8 | Bokeh para tipografia | desfoque 85 mm f/1.4, círculos em 2 cores, mais escuro onde o texto senta, sem foco | 9:16 |
| 9 | Mockup de celular | mão segurando o celular, **tela verde `#00FF00` lisa sem reflexo**, cinco dedos separados | 4:5 |
| 10 | Mockup de notebook | ¾ pela esquerda, tela verde lisa, fundo desfocado, sem pessoas | 16:9 |
| 11 | Black Friday premium | natureza-morta escura, **um feixe de luz duro em diagonal**, espaço para a oferta; sem balão, "SALE", confete, raio | 4:5 |
| 12 | Quadro-chave de loop | cena do modelo 1, nada encosta na borda, movimento suave contínuo, câmera parada → Veo/Omni (1º = último quadro) | 16:9 / 9:16 |

## 4. Série coerente sem seed

Não há `seed` documentado para imagem; a coerência vem de 4 travas (15 §2.3, §2.5):
1. **Receita fixa** (`receita.json`): modelo, proporção, resolução, câmera/lente, luz, paleta HEX, material,
   filme/grão, bloco "no text". Na série **só mudam assunto, ação e lugar**.
2. **Imagem âncora:** a 1ª aprovada vai como `--ref` em todas as seguintes ("use the attached image as the style,
   lighting and color reference; new scene: …"). 2.1: até 10 objetos + 5 pessoas; Pro: até 3 referências de estilo.
3. **Ajuste pequeno = mesma conversa; deriva = recomeçar** com a descrição completa + âncora.
4. **Mesmo acabamento em código** (iguala o que a IA não igualou): mesmo mapa de gradiente/casar cor
   (`efeitos.mapa_gradiente`, `efeitos.casa_cor`), **um grão** de σ fixo (`efeitos.pos_campanha`), uma nitidez no
   tamanho final (camadas.md §3.2, §3.5, §3.6).
- **Coerente não é repetido:** mesma receita e acabamento, arquétipos diferentes (par com CLIP ≤ 0,92) (qualidade.md).
- **Rastro:** guardar com a peça o `<saida>-prompt.json` que o `gemini.py` grava (modelo, prompt, refs) (15 §3.4 (7)).

## 5. Controle de qualidade da imagem de IA

**Escolher:** 4–8 variações por cena em 1K → folha a 25% e a 100% → critérios nesta ordem: (1) a ideia lê em 3 s;
(2) espaço do texto no lugar e calmo; (3) luz com motivo; (4) zero defeito abaixo; (5) combina com a âncora. Empate →
`arena.py`. A escolhida é refeita em 2K (4K só se o formato pedir) (15 §6 passos 5–7).

**Olhar a 100%, depois a 25%** (15 §6.1; famílias de defeito em 15 §1.2):

| O quê | Defeito | Falhou → fazer |
|---|---|---|
| Mãos | dedos a mais/a menos, juntas, unhas, mão fundida no objeto | inpainting só da mão; 2 falhas → cena sem mão |
| Rosto inventado / multidão | dentes, íris diferentes, **reflexo da luz diferente nos dois olhos**, orelha, óculos sem lógica | refazer; figurante e multidão → desfocar mais ou tirar |
| Rosto de pessoa REAL | qualquer diferença com a foto original, lado a lado a 100% | **descartar** (não retocar) |
| Pele | cera, plástico, brilho onde a luz não bate | refazer com poro, luz com motivo e grão |
| Texto e símbolos | letra, número, placa, tela ou logo falso; **logo de terceiro** (equipamento, roupa, carro) | inpainting ("remove only …") ou refazer; nunca publicar |
| Objeto e lugar ("saber do assunto") | barra com anilhas diferentes, presilha faltando, cabo solto; Brasil sem cara de Brasil (tomada, placa, carro) | refazer descrevendo o objeto e o lugar certos |
| Luz e física | sombra do lado errado, sem **sombra de contato**, reflexo, fuga e escala erradas; objeto que vira outro, padrão clonado | refazer com a luz escrita; sombra de contato em código (camadas.md §3.4) |
| Arquivo | tamanho real ≠ pedido; banding no escuro; halo de ampliação; franja do recorte | conferir o PNG; dither TPDF; Real-ESRGAN só se faltar pixel; matting (camadas.md §3.1) |
| Zona do texto | detalhe atrás das letras, contraste baixo | C1/C1b do `camadas.py`; véu ou outra variação |
| "Cara de IA" | brilho geral, simetria perfeita, limpo demais, céu de pôster, estilo "banal e polido" | rever luz, imperfeição, paleta e grão |

- **Imagem de IA não pula portão:** depois da lista, os 4 portões de `qualidade.md` como qualquer peça (15 §6 passo 10).
- **Parar de insistir:** 3 rodadas sem passar → outro caminho (cena mais simples, foto real ou código) [ponto de partida].

## 6. Texto em código, marca intocável

1. **Texto, logo, preço, data, botão, selo, contador e legal = código, por cima** (camadas L7–L8), nunca na imagem
   gerada — mesmo que o Pro ou o Omni escrevam legível (15 §3.4 (5), §2.4 (8), §5.c.3).
2. **A IA nunca redesenha a marca:** mockup com marca = `mockup.py`; tela de aparelho = verde `#00FF00` + captura real
   em código; imagem de IA nunca vira logo (o Google pode gerar igual para outros) (15 §2.7, §3.3).
3. **Pessoa real — a IA não toca no rosto** (15 §2.6): recortar (rembg + matting, camadas.md §3.1) → gerar o
   **cenário vazio** com a luz da foto (direção, dureza, cor, altura, lente) → compor em código (sombra de contato,
   cor casada, grão único) → se precisar integrar, inpainting **só na borda/ambiente** ("change only the background…
   keep the person exactly the same") e rosto conferido lado a lado.
4. `gemini.py edit foto-da-pessoa.jpg "mesma pessoa, …"` só com autorização escrita que **cite IA** + conferência do
   rosto; sem isso, o caminho do item 3 (15 §3.4 (1)).

## 7. Vídeo

**IA de vídeo = gancho visual (cena impossível, objeto-símbolo, transição, fundo); prova = filmagem real** (15 §5.b).

| Ferramenta | Quando | Regras | Origem |
|---|---|---|---|
| **Gemini Omni Flash** (`gemini-omni-1.1-flash`) | **padrão**; ajuste conversando ("troque o objeto") | pedir "**single continuous shot, no scene cuts**" (corta sozinho); negativo escrito no texto; pessoa reconhecível não é aceita | 15 §5.c.1, §5.c.3 |
| **Veo 3.1** (Fast = custo, Lite = rascunho) | **último quadro** (loop, "de A para B") ou **extensão** | 4, 6 ou 8 s; 1080p e 4K **só com 8 s**; 16:9 ou 9:16; áudio sempre; até 3 refs; +7 s até 148 s (720p); `seed` não garante; **baixar na hora** (apaga em 2 dias) | 15 §5.c.2 |
| **HyperFrames** (HTML/GSAP → MP4) | texto, logo, legenda, contador, texto cinético | Apache 2.0; logo: `python motion.py --symbol s.svg --wordmark w.svg --size 1080x1920 --style pop -o out/sting` | 15 §5.d.1 |
| **Remotion** | **NÃO usar** | grátis só até 3 funcionários | 15 §5.d |
| GSAP | no HyperFrames e em sites de clientes | grátis, não é open source; proibido fazer ferramenta "sem código" concorrente | 15 §5.d |
| **dotLottie** (MIT) | animação leve no SITE: ícone, selo, contador, logo | ou SVG + CSS | 15 §5.d |
| FFmpeg | loop, cor e grão da série, corte, compressão | já instalado | 15 §5.d.1 |

- **Prompt:** [Cinematografia] + [Assunto] + [Ação] + [Contexto] + [Estilo e clima], em inglês; `SFX: …`,
  `Ambient noise: …`; tomadas com `[00:00-00:02] …`; rosto: "portrait" (15 §5.c.4).
- **Fluxo:** quadro-chave no Nano Banana (passa pelo §5) → Veo/Omni com `image` (+ `lastFrame` = mesma imagem para
  loop), 8 s → **baixar** → FFmpeg (loop sem pulo, curva e grão das imagens, sem o áudio não usado, H.264 + WebM) →
  HyperFrames para texto e marca (15 §6).
- Veo e Omni só saem em 16:9 ou 9:16 → 4:5, 1:1 e 21:9 por recorte; assunto no núcleo comum [derivado de 15 §5.c.1].

**Hero de site com vídeo** (15 §5.a.1, §5.a.2):
- `<video autoplay muted loop playsinline poster>`, **WebM antes de MP4** (AV1 só com H.264 de reserva),
  `aspect-ratio` reservando o espaço. **O poster é o LCP:** ≤ 2,5 s, `fetchpriority="high"`, sem `loading="lazy"`.
- **Funciona 100% parado:** `video.play().catch(…)` → poster + play. `prefers-reduced-motion: reduce` ou `saveData`
  → sem autoplay, só poster.
- **WCAG 2.2.2 (nível A):** loop > 5 s → **botão pausar/tocar visível** (≥ 44 px, lembrado na sessão).
- Movimento lento e pequeno, **sem zoom grande** (enjoo); título, preço e botão em HTML; **contraste no pior quadro**
  (1 por segundo).
- **Sem vídeo no hero:** captura de tráfego pago no celular; vídeo que só enfeita; quando há vídeo do professor
  falando. Testar A/B poster × vídeo antes de adotar.

| Formato | Proporção · pixels | Duração | Regra | Origem |
|---|---|---|---|---|
| Reels / Stories (anúncio) | 9:16 · 1080×1920 (exportar 1440×2560) | **6 s** (gancho + oferta) e **15 s** (gancho + prova + oferta) | marca até 3 s; funciona mudo; legenda ≤ 2 linhas; zonas de `qualidade.md`; Stories: cada 15 s se sustenta sozinho | 15 §5.b; 5 §1.3 |
| Feed Instagram (vídeo) | 9:16 · 1080×1920 (zona do Reels) | aceita 1 s–60 min; usar 6 e 15 s | essencial DENTRO do vídeo | 5 §1.3 |
| Feed Facebook | 4:5 · 1440×1800 | aceita até 241 min; usar 6 e 15 s | rodapé (título, botão) pode sumir no celular | 5 §1.3 |
| In-stream | — | recomendado ≤ 15 s | marca e produto à vista | 15 §5.b |
| Loop de fundo Stories/Reels | 9:16 · 1080×1920 | 6 s (de um clipe de 8 s) | tipo e marca no HyperFrames | 15 §5.d.1 |
| Hero de site, celular | 9:16 ou 4:5 · 720p · **≤ 1,5 MB** [ponto de partida] | loop **6–10 s** sem emenda | sem áudio (`-an`); `<source media>` por tela | 15 §5.a.2 |
| Hero de site, computador | 16:9 ou 21:9 · 1080p · **≤ 3 MB** [ponto de partida] | loop 6–10 s | poster AVIF/WebP ≤ 120 KB [ponto de partida] | 15 §5.a.2 |
| Texto cinético | qualquer | — | ≤ 17 caracteres por segundo | 15 §5.d.1 |

- **Áudio:** anúncio de Reels sem música licenciada (5 §1.3); áudio da IA: tirar se não usar; se usar, não pode
  lembrar obra existente (15 §6.2).
- **Checar (1 quadro/s + 3 vezes em velocidade normal)** (15 §6.2): rosto e mãos iguais entre quadros · nada aparece,
  some ou "derrete" · sem corte não pedido · loop sem pulo · texto só no HyperFrames · movimento não briga com o título.

## 8. Lei e plataforma: pode / não pode

Leitura nossa, não é parecer jurídico; leis citadas sem abrir o Planalto — conferir antes de contrato (15 §7.6).

**Pode:** IA em fundo, cenário, objeto, textura, cena impossível, mockup e quadro-chave (15 §4.2) · uso comercial do
que a API gera (o Google não reivindica) (15 §3.3) · figurante inventado distante/desfocado (15 §3.4) · editar pessoa
real com IA **só** com termo escrito que cite IA, finalidade, campanha e prazo — rosto é dado biométrico sensível
(LGPD art. 11) — e **só com chave paga** (no grátis o Google usa o conteúdo) (15 §2.2, §3.2).

**Não pode**
- Aluno, depoimento, resultado ou especialista de IA apresentado como real (CONAR Anexo Q 5.1) (15 §3.2).
- **Antes/depois, corpo "ideal" ou resultado físico por IA** (CONAR art. 27; Meta saúde) (15 §3.1).
- Meta saúde: "inferioridade sobre a aparência", close beliscando gordura, resultado em prazo sem ressalva (15 §3.1).
- Famoso, sósia, "parecido com" (CONAR art. 27 §9), pessoa viva sem autorização prévia e expressa (art. 34), pessoa
  morta (Código Civil art. 20) (15 §3.2).
- Cena que não existiu apresentada como fato (caso A24) (15 §1.1, §3.1).
- Se passar por pessoa sem aviso, biometria sem consentimento, dizer "feito só por humano", **remover SynthID/C2PA**
  (Google 1.6, 4.2, 4.5) (15 §3.3).

**Declarar**
- **Meta, anúncio de tema social/eleição/política** com pessoa, evento ou imagem realista feita/alterada por IA →
  declarar no Gerenciador (desde 11/01/2024; "Informação de IA" desde 19/02/2026); "saúde pública" e "regulamentação
  da profissão" podem cair aqui (15 §3.1).
- **Post orgânico** com pessoa ou cena realista que não existiu → marcar "Informações de IA"; nunca esconder IA de
  propósito (15 §3.1).
- CONAR não exige aviso, mas o Código vale **inteiro** para IA e anunciante/agência respondem (15 §3.2).
- Rastro de cada imagem/vídeo usado: prompt, modelo, data, referências, custo (15 §3.4 (7)).

## 9. Custos de referência e registro

US$, plano pago (o grátis não gera imagem nem vídeo) (15 §2.2, §5.c.1):

| Imagem | 1K | 2K | 4K | | Vídeo, por segundo | 720p | 1080p | 4K |
|---|---|---|---|---|---|---|---|---|
| **Nano Banana 2.1** (padrão) | 0,034 | **0,050** | 0,113 | | Veo 3.1 | 0,40 | 0,40 | 0,60 |
| Nano Banana 2 (`flash`) | 0,067 | 0,101 | 0,151 | | Veo 3.1 Fast | 0,10 | 0,12 | 0,30 |
| Nano Banana Pro (`pro`) | 0,134 | 0,134 | 0,24 | | Veo 3.1 Lite | 0,05 | 0,08 | — |
| Lite (`lite`, só 1K) | 0,034 | — | — | | Omni Flash | ~0,10 | ? | ? |

- **Lote (Batch API):** metade do preço, entrega em até 24 h; o "pensamento" do modelo é cobrado à parte (15 §2.2).
- **Por cena:** 4–8 variações em 1K (US$ 0,13–0,27) + a escolhida em 2K (0,05) [derivado de 15 §6]. Pro só se
  precisar de muito detalhe.
- **Loop de 8 s em 1080p:** US$ 3,20 (Veo 3.1) · 0,96 (Fast) · 0,64 (Lite) · ~0,80 (Omni, 720p); 4 variações:
  ~US$ 4 (Fast) a ~13 (Veo 3.1) (15 §5.c.1).
- **Registrar:** `python gemini.py usage` soma `~/.cache/brand-studio/gemini-usage.csv`. **Atenção:** o `PRICE` do
  script ainda usa a estimativa antiga do 2.1 (0,067/0,101/0,151) → o `usage` mostra ~2× o real em 1K/2K. Vídeo não
  tem registro: anotar no diário.

## 10. Para virar ferramenta

1. **`video.py` (Omni/Veo):** imagem/texto → vídeo, `--last-frame`, 4/6/8 s, 16:9/9:16, resolução, "single continuous
   shot" automático, **download na hora**, `-prompt.json` e custo no CSV.
2. **`gemini.py`:** `PRICE` do `banana21` = 0,0336/0,0504/0,113; tirar "deprecated" do `flash` (15 §2.1, §7.13).
3. **`gemini.py --receita receita.json --ancora a.png`:** prompt = cena + bloco fixo; âncora como `--ref` na série.
4. **`gemini.py --batch`** para série grande (metade do preço) (15 §2.2).
5. **Edição em conversa** (`previous_interaction_id`) sem deriva + teste de `seed` no `generationConfig` (15 §7.4).
6. **Checagem automática:** tamanho real × pedido; OCR atrás de letra falsa; rosto antes × depois (YuNet +
   semelhança) ao editar pessoa real.
7. **Receita de hero em vídeo** (FFmpeg): loop sem emenda, curva e grão da série, H.264 + WebM sem áudio, poster,
   contraste C1 por quadro e o HTML com pausa e `prefers-reduced-motion`.
8. **`-prompt.json` completo:** + data, custo, versão da receita e papel (cenário/prova) — rastro CONAR.

## 11. Lacunas

- **Seed de imagem** não documentado: valem as 4 travas do §4 até testar (15 §7.4).
- **Sem A/B público** foto real × IA com conversão: quando houver tráfego, testar "foto do professor" × "cena de IA +
  recorte do professor" medindo clique e venda (15 §4.2, §7.2).
- **Meta:** testado: a imagem crua do Nano Banana 2.1 vem em JPEG com C2PA + SynthID; a composição/exportação apaga o
  C2PA (o SynthID fica nos pixels). Se a Meta lê C2PA ou só IPTC ainda não é confirmado → não contar com rótulo
  automático; marcar à mão quando for substancialmente IA. `gemini.py` guarda `*-original.jpg` intacto (não remover). **Omni:** duração base e preço de 1080p/4K não informados (15 §7.5).
- **Leis citadas de memória** e direito autoral de imagem de IA no Brasil sem regra verificada (15 §7.6, §7.7).
- **Pontos de partida:** pesos do hero (1,5 MB / 3 MB / 120 KB) e o limite de 3 rodadas do §5 (15 §7.11).
- **Conflito a resolver:** `../brand-studio/references/composicao.md` dá o exemplo `gemini.py edit professor.jpg "mesma
  pessoa, …"`; pelo §6 isso só vale com autorização que cite IA + conferência do rosto (15 §2.6).

## 12. IA como palco — padrões P1–P11 (cena de IA + conteúdo real em código + movimento que liga os dois)
Regra: a IA só entra com objeto-metáfora explicável em 1 frase; a superfície do objeto recebe conteúdo REAL em código.
Tela/placa/letreiro: gerar em verde chapado, medir os 4 cantos e encaixar por homografia, com o mesmo grão e reflexo.
Pós de série em ordem fixa: desfoque leve → curva/LUT a 50–70 % → grão por último. Exemplo de referência: `../../revisao-de-design/references/repertorio/sites.md` ST-01.

### P1 · Objeto-metáfora no cenário ("a tela que liga")
- **O quê:** um objeto concreto (TV, porta, janela, vitrine, caixa, mapa) num lugar onde não deveria estar; o objeto É a
  promessa da marca. O cenário é foto de IA; a "superfície" do objeto vira a página.
- **Quando:** hero de site institucional/estúdio/evento; KV de campanha; abertura de vídeo. Não em captura de tráfego pago.
- **Receita:** 1) frase-conceito sem "IA" (ex.: "uma tela que liga no meio do caminho"). 2) Nano Banana 2.1 (`--model banana21`,
  2K, 16:9 e 9:16 separados): objeto a ~60% da largura, céu/vazio do lado do título, superfície da tela em verde chapado.
  3) Céu sem detalhe → recortar e trocar por degradê em código (ajusta a qualquer largura). 4) Medir os 4 cantos da tela
  (OpenCV, `findContours` no verde) → gravar `tela.json`. 5) Por cima: UI real (`matrix3d`, P2). 6) Movimento: P7.
- **Prompt-modelo:** "Wide cinematic photo, 35mm, late-afternoon side light from left, a [old CRT television] standing alone
  on [a flowering hill], screen facing camera, screen is flat pure #00FF00, empty pale sky on the left third, film grain,
  muted [palette HEX], no text, no people."
- **Erro comum:** objeto pequeno demais no celular (vira ponto) → versão 9:16 própria com objeto maior, nunca só recorte.
- **Exemplo:** gsaweb.com.br (TV num morro, céu transparente sobre degradê CSS); Shader.se — câmera avança até a tela de
  um monitor na transição do hero (Codrops).

### P2 · Plate + UI em código encaixada na perspectiva (homografia)
- **O quê:** a tela/placa/outdoor da imagem recebe HTML vivo (texto, vídeo, contador) com a perspectiva exata.
- **Quando:** site (UI viva) e peças (texto nítido em superfície do cenário: placa, letreiro, tela, papel).
- **Receita web:** 4 cantos de destino (P1 passo 4) → resolver homografia 3×3 → `matrix3d` (16 valores, coluna-maior),
  `transform-origin:0 0` no elemento com o tamanho de origem (libs: PerspectiveTransform.js, fix-perspective; ou 40 linhas
  próprias). Recalcular no `resize` (a imagem usa `object-fit`, os cantos mudam).
- **Receita peça (PIL):** `cv2.getPerspectiveTransform(src, dst)` + `warpPerspective` da arte renderizada no `palco.py`
  em 2× → máscara do verde com borda 1 px suavizada → multiplicar pela luminância da tela original (reflexo/vinheta) a 15–25 %.
- **Erro comum:** UI chapada e nítida demais sobre foto granulada → mesmo grão, leve curvatura/vinheta, reflexo por cima.
- **Exemplo:** gist de Mike Bostock (matrix3d por 4 pontos); `mockup.py` já faz isso para marca em mockup.

### P3 · Transição imagem → interface ("liga", "abre", "entra")
- **O quê:** a rolagem leva a câmera para dentro do objeto; a tela cresce até ocupar a viewport e vira a seção seguinte.
- **Receita (GSAP ScrollTrigger, pin ~120–160 vh):** 1) palco fixo; 2) `scale` da imagem com `transform-origin` no centro
  da tela (calcular em px pelo `tela.json`); 3) o retângulo da tela vira `clip-path: inset()` animado até `inset(0)`;
  4) "ligar": faixa horizontal `inset(49.5% 0 49.5% 0)` → `inset(0)` em 0,35 s + flash de brilho 1→1.6→1 + linhas de
  varredura (repeating-linear-gradient 2 px, 8 % opacidade) que somem; 5) conteúdo real da seção já está atrás, sem cópia.
- **Movimento reduzido:** troca o zoom por fade cruzado de 400 ms (o movimento continua, suave). `forwards`, nunca `both`.
- **Erro comum:** `clip-path` com nº de pontos diferente entre estados (pula); área recortada não recebe clique.
- **Exemplo:** Codrops "SVG mask transitions on scroll" e "Rock the Stage" (shader na rolagem).

### P4 · Parallax por profundidade (2.5D)
- **O quê:** a foto de IA ganha volume com um mapa de profundidade (perto = branco): mexe 1–3 % com mouse/rolagem/giroscópio.
- **Receita:** 1) Depth Anything V2 (Small, CPU basta para 1 imagem; `transformers` pipeline "depth-estimation" ou
  Transformers.js) → PNG 16 bits, borrar 2–4 px, fechar buracos. 2) Site: 1 shader de UV `uv + (p-0.5)*depth*0.02`
  (Three.js ou WebGL puro, ~60 linhas), `<img>` com alt por baixo e canvas só após carregar. 3) Peça/Reels: DepthFlow
  (Python, exporta H.264/AV1; licença AGPL — usar só como ferramenta local) com dolly 3–5 % em 6–8 s → loop com ida e volta.
  4) Alternativa barata: 3 camadas recortadas (fundo/meio/objeto) e GSAP `y` diferente por camada.
- **Erro comum:** força alta = borda esticada "derretida" atrás do objeto (D: parece erro) → limitar e preencher fundo.
- **Exemplo:** componente Framer "Spatial Scene"; depth-map-generator (GitHub, jasonyingling).

### P5 · Cinemagraph (foto parada com 1 coisa viva)
- **O quê:** tudo parado, só um detalhe se move (brilho da tela, nuvem, fumaça, grama). Lê como foto premium, pesa pouco.
- **Receita:** 1) quadro-chave aprovado do P1 → Omni Flash/Veo 3.1 com `image` = `lastFrame` = mesma imagem, câmera
  travada ("locked-off tripod shot, only the [screen flicker] moves"). 2) FFmpeg: `alphamerge` do vídeo com máscara
  cinza (borda suave 20–40 px) + `overlay` sobre o PNG parado → só a área mascarada mexe. 3) Emenda: crossfade de
  0,5 s entre fim e início, ou ida-e-volta. 4) 4–6 s, sem áudio.
- **Erro comum:** máscara dura (linha visível) ou câmera da IA "respirando" (tudo treme) → reforçar "static camera".
- **Exemplo:** guia Adobe Premiere "cinemagraph"; semi_automated_cinemagraph (GitHub).

### P6 · Vídeo em loop no herói (cenário vivo)
- **Receita:** já coberta na pesquisa 15 §5.a e regras §7. A mais: 6–10 s, poster = 1º quadro em AVIF/WebP pré-carregado
  (é o LCP), `preload="metadata"`, `aspect-ratio` fixo (CLS), WebM AV1 primeiro + MP4 H.264 `+faststart`, `-an`,
  CRF 23–28 duas passadas, alvo ≤ 2–3 MB em 1080p; versão 9:16 própria para celular.
- **Erro comum:** loop longo e pesado que ninguém assiste duas vezes.

### P7 · Vídeo controlado pela rolagem (scroll-scrub)
- **O quê:** a rolagem "dirige" o vídeo (a TV liga, a porta abre) — quadro N = posição N.
- **Receita:** gerar o plano no Veo 3.1 (primeiro + último quadro = estados A e B do P1, 4–8 s) → FFmpeg extrai 60–120
  quadros WebP (q 70, 1280 px; 720 px no celular) → canvas desenha o quadro do progresso do ScrollTrigger; carregar só os
  ~12 primeiros e o resto em segundo plano; `devicePixelRatio` máx. 1,5. Alternativa: WebCodecs decodifica antes
  (lib scrolly-video). `<video>` com `currentTime` só com keyframe a cada quadro (`-g 1`), e no iOS falha para trás.
- **Erro comum:** 12 MB de mídia baixados na entrada; travar no celular fraco → medir no `check_pagina.py`/peso.
- **Exemplo:** DEV "scroll-scrubbed video portfolio" (12,8 → 9,8 MB com WebP); scrolly-video (npm).

### P8 · Máscara de recorte animada (a marca como janela para o cenário)
- **O quê:** o cenário de IA só aparece por dentro de uma forma da marca (letra, símbolo, pílula) que cresce até tela inteira.
- **Receita:** SVG `<mask>` com o símbolo em curvas; GSAP anima `scale` da máscara 0,3 → 12 com o centro na contraforma;
  imagem com leve `scale` contrário (1,15 → 1) para dar profundidade. Peça: mesmo efeito no HyperFrames para Reels.
- **Erro comum:** forma arredondando o logo (proibido) — usar o logo intacto ou um elemento do kit.

### P9 · Foto real recortada + cenário de IA (composição crível)
- **Receita:** 1) Medir a luz da foto real ANTES: direção (lado mais claro do rosto), dureza (sombra nítida ou mole),
  temperatura → escrever no prompt do cenário ("key light from camera-left, soft, 4500K, eye level, 50mm"). 2) Mesma
  altura de câmera: horizonte do cenário na altura dos olhos da pessoa. 3) Recorte (rembg + matting) com borda 1–2 px
  desfocada igual à profundidade de campo. 4) Sombra de contato: elipse preta borrada, multiply 35–55 %, + sombra
  projetada na direção da luz. 5) Casar cor: transferência Reinhard em LAB (média/desvio do cenário → pessoa a 30–50 %),
  "light wrap" 6–10 px na borda com a cor do fundo. 6) Mesmo pós nos dois juntos (P10). Nunca mandar a pessoa para a IA.
- **Erro comum:** pessoa nítida e fria num cenário quente e granulado (colagem) → é o sinal nº 1 de "montagem".

### P10 · Série coerente sem seed (o que acrescentar às 4 travas já escritas)
- **Grade de câmera/luz fixa:** 3 planos só (geral 24 mm · médio 50 mm · detalhe 85 mm) e 1 luz (direção + hora) por série.
- **Pós único em código, nesta ordem:** desfoque 0,3–0,6 px → curva/LUT a 50–70 % → duotone/mapa de gradiente se for o
  estilo → grão 8–15 % por último (grão antes do desfoque vira "plástico"). Grão igual une imagens de gerações diferentes.
- **Igualar à âncora, não ao olho:** sombra, realce, saturação e contraste medidos na imagem-âncora e aplicados por script.

### P11 · Vídeo de IA em peça social (Reels/Stories/anúncio)
- **Receita:** gancho no 1º segundo (o "evento" do P1 — a tela liga — acontece em 0,5–1 s, nada de abertura lenta);
  7–15 s para alcance, ~20 s para conversão; texto, logo e legenda em código (HyperFrames) por cima do plano de IA; zona
  de anúncio Meta: livre 14 % em cima, 35 % embaixo, 6 % nas laterais (mais rígida que a nossa orgânica); 1º quadro
  já é capa válida (9:16 e recorte 1:1/4:5 legíveis); loop: último quadro = primeiro; H.264 1080×1920, 30 fps, sem áudio
  da IA se houver música licenciada.
- **Erro comum:** texto queimado no vídeo da IA (não dá para corrigir/traduzir) e capa que vira borrão no grid.

## Imagem de IA com pessoa
- **Imagem de IA com pessoa NUNCA fica na pasta `imagem/` do projeto** (nem como exemplo): o `manual.py` puxa tudo de
  lá e uma pessoa INVENTADA pode entrar no manual. Rascunho de IA com gente vai para `%TEMP%\<projeto>-rascunho`
  ou `imagem/_fora-do-manual/`.
- Nunca propor gente inventada no lugar de pessoa real; a 1ª busca é o material oficial do cliente.

## Elemento ou cenário por IA para página: prompt profissional + tratamento
Quando o código não chega ao nível (ex.: diagrama de planos anatômicos com boneco de palito foi reprovado), usar a IA
a sério: a IA de imagem (Nano Banana 2.1) faz em 1 chamada o que o código não faz.
1. **Prompt = parágrafo de diretor de arte, não lista:** sujeito concreto (material, cor em hex), ação/estado, lente e
   abertura (85 mm f/5.6), luz com origem (key à esquerda, rim azul), fundo com hex, estilo ("product-render
   clarity"), composição com margem e **zona vazia dita** (onde a foto real entra), e o negativo no fim ("no text,
   letters, numbers, logos, watermarks or people"). Variante clara = mesmo prompt trocando fundo/luz ("warm off-white
   #ECE7DC, high-key").
2. **Referências:** foto da pessoa (cutout sobre cinza) só para ESCALA/LUZ, com a ordem "não desenhe a pessoa";
   elemento do kit como forma de referência quando precisa da geometria.
3. **Um conceito por imagem quando a clareza importa:** trio de planos anatômicos saiu com o painel central errado (2
   planos) → regerar só o plano que falhou e montar o trio em código (os rótulos SAGITAL/FRONTAL/TRANSVERSAL entram em
   texto, nunca na IA).
4. **Tratamento (obrigatório antes de usar):** levar o fundo a preto/branco puros (mediana da borda → 0/255), vinheta
   embutida, grão fino, e **cor → alfa** (preto vira transparência no escuro; branco no claro) para a imagem assentar em
   qualquer fundo/versão. `mix-blend-mode: screen/multiply` falha quando o pai cria contexto de empilhamento (animação
   de entrada): preferir alfa real em WebP (alpha_quality 70, ~160–190 KB) ou SVG com imagem embutida + rótulos.
5. **Rede:** `IncompleteRead` acontece em 2K; repetir só a imagem que falhou.
Custo do lote (10 imagens 2K): ~US$ 0,5 (15 §2.4).
