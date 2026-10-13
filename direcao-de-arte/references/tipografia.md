# Tipografia com voz própria: regras congeladas

Regras para escolher, combinar e usar fontes em QUALQUER peça (arte, anúncio, site, vídeo, identidade). Origem entre
parênteses: **2** e **16a–16d** = pesquisas de tipografia de origem; **14 §F** e **14b** = sites de
referência; **qualidade** = `references/qualidade.md`; **medido** = `tipos.py ficha`; **[ponto de
partida]** = número sem fonte, para testar. O resto mora nas pesquisas: casos (Spotify, Dropbox, Public Theater, Canal
Brasil, Globotipo) na 2; 60 receitas, legibilidade e escala na 16a; 230 fontes grátis com licença na 16b; tendências,
71 técnicas e rotação na 16c; marcas por setor, Brasil e psicologia na 16d.

**Ferramenta central:** `scripts/tipos.py` (ficha · par · folha · usar · historico · rotacao · calibrar · sugerir
(receitas)). Escolher no olho deixa passar o zero igual ao O num preço, o acento que falta e o mesmo par em toda campanha.

## 1. Processo obrigatório (toda peça, série, site ou identidade)
Faz parte da "pesquisa nova a cada criação" (`referencias-e-pesquisa.md`): a frente Fontes traz candidatos novos e
este processo prova cada um. Nenhuma fonte entra na peça sem passar pelos 7 passos.

| # | Passo | Como | Passa quando |
|---|---|---|---|
| 1 | **Voz do assunto** em 2–3 palavras + perfil força × velocidade | briefing, mundos e §6 | a voz sai de um FATO do assunto, não do gosto (16c §1.3; 16d §4.3) |
| 2 | **2–3 candidatos por papel** | `tipos.py sugerir` (receitas) · §6 · 16b §21 · pesquisa nova | ≥ 1 candidato de título fora do histórico do cliente |
| 3 | **Par com prova** | `tipos.py par "Título" "Texto" --numeros "Números"` | nenhum REPROVADO; cada ALERTA resolvido ou com motivo escrito |
| 4 | **Folha visual** | `tipos.py folha pares.json -o pares.png` com o TEXTO REAL da peça | olhar a 100% e a 25% (qualidade) |
| 5 | **Novidade** | `tipos.py par … --cliente X --projeto Y` | título novo para o cliente, ou motivo escrito (16a §4.13) |
| 6 | **Rotação** | `tipos.py rotacao --cliente X [--fixar T7] [--video]` | combinação a distância ≥ 3 das últimas 3 campanhas (§10) |
| 7 | **Registrar** | `tipos.py usar --cliente X --projeto Y --titulo … --texto … --numeros … --eixos "T2,A1,…" --tecnicas "1,8"` | linha gravada no registro de fontes do `tipos.py` |

- **REPROVADO** = qualquer VETO do `tipos.py`: licença não identificada no arquivo · "padrão de IA" no título · falta
  acento do português (ÁÀÂÃÉÊÍÓÔÕÚÜÇ, minúsculas, º ª) · na fonte de NÚMEROS, O/0, l/1 ou I/1 acima do limite.
- **ALERTA** (resolver ou escrever o motivo): conflito entre as fontes · altura-x diferente na mesma linha (Δ > 0,06) ·
  texto com altura-x < 0,66 da maiúscula · sem `tnum` · I igual a l · família já usada pelo cliente.
- **Limites de confusão** (calibrados com 10 fontes): O/0 0,85 · l/1 0,80 · I/1 0,75 · rn/m 0,80 ·
  8/B 0,88. Até 0,06 abaixo do limite, num par crítico = "olhar no tamanho real" (tipos.py).
- **Texto da folha:** sempre a linha PT-BR (16a §2.8) + o dado real da peça:
  `AÇÃO · PROMOÇÃO · ÚLTIMAS · NÃO PERCA · CORAÇÃO · INSCRIÇÕES · ação, pão, avó, você, três, açúcar ·
  R$ 1.997,00 · 1º 2ª · “aspas” — travessão`, mais cupom (BLACK10OFF), hora (20h30) e telefone.
- **Fonte de fora do Google Fonts** (arquivo .ttf, Fontshare, Velvetyne): primeiro `tipos.py ficha "caminho/x.ttf:700"`.

## 2. Combinar fontes: a regra-mãe
1. **Uma família primeiro.** Pesos, larguras, `opsz`, itálico e caixa da fonte principal vêm antes de trazer outra
   (16a §1.1). Uma variável com `wght` + `wdth` + `opsz` faz o papel de um par inteiro (16a §1.6).
2. **2ª família só com papel escrito:** dado/número; itálico, largura ou peso que a 1ª não tem; voz mais quente ou mais
   séria; glifos que faltam (16a §1.1).
3. **Limites:** arte e anúncio ≤ 2 famílias · site ≤ 2 (+ mono só com dado real) · identidade ≤ 3, cada uma com papel
   no `brand.json`; 3ª família sem papel escrito = VETO (16a §1.1). Com âncora (§12), a peça pode ter título
   + texto + acento = 3, e a âncora conta quando faz o texto (16d §5.2).
4. **Três relações** (16a §1.2): **concordante** (1 família) = calma, para institucional e texto longo;
   **contrastante** (claramente diferentes) = atenção, para arte, anúncio e capa; **conflitante** (parecidas sem ser
   iguais) = PROIBIDO, "parece erro". O `par` dá ALERTA quando o desenho das minúsculas é ≥ 0,80 parecido com
   Δlargura < 12% e Δpeso < 35%.
5. **Combinar pelo esqueleto, não pelo rótulo:**
   - **diferentes em ≥ 2 traços:** largura, peso, construção (grotesca/humanista/geométrica/serifa/mono), contraste do
     traço, estilo reto/itálico (2 §4; 16a §1.2);
   - **parecidas em ≥ 1 traço da estrutura:** altura-x (Δ x/cap ≤ 0,06), abertura ou proporção (16a §1.3);
   - **matriz de Kupferschmid** (16a §1.3): mesmo esqueleto (dinâmico, racional ou geométrico) com acabamento
     diferente = combina; esqueleto e acabamento diferentes = contraste de propósito; mesmo acabamento com esqueleto
     diferente = evitar.
6. **Atalhos seguros** (16a §1.5): superfamília (Plex, Source, Red Hat, Instrument, Sofia Sans, Mona/Hubot, Atkinson
   Next + Mono, Geist + Mono); mesmo desenhista (Epilogue + Anybody); mesma época com construção diferente.
7. **Contraste dentro de uma família:** Δ`wght` ≥ 300 **ou** Δ`wdth` ≥ 25, mais o salto de tamanho (16a §1.6).
   Misturar pesos na palavra: ≤ 2 pesos com Δ ≥ 300 (2 §2).
8. **Nunca** duas neo-grotescas de largura normal, e nunca uma fonte "séria" com uma "brincalhona" sem a ideia pedir
   (2 §4; 16a §1.2).
9. **Muitas fontes só viram marca com UMA regra por trás**: na LA28, a regra é a placa de rua (16c §1.3).

## 3. Papéis fixos
| Papel | Faz | Por peça | Regra |
|---|---|---|---|
| **Voz (título)** | título, oferta, frase-ideia | 1 | onde mora a personalidade: pode ser condensada, larga, preta, serifa expressiva — porque é grande e curta (16a §2.2) |
| **Texto** | sub, explicação, condição, parágrafo | 1 | aberta, largura normal, altura-x ≥ 0,66 da maiúscula, peso 400–500, sem condensação (16a §2.2; tipos.py) |
| **Números** | preço, contador, cupom, PIX, telefone, hora, lote | 0–1 | `tnum` + algarismos alinhados; zero que não vira O; **nunca condensada**; preto (800–900) só se a ficha passar; pode ser a própria fonte de texto (16a §2.7; 16c §1.3; medido) |
| **Acento** | 1–3 palavras de ênfase | 0–1 | itálico verdadeiro, serifa no meio da grotesca ou mão; nunca no preço, na data ou no CTA (16a §1.7, §5.1) |
| **Âncora de marca** | CTA, rodapé, legal, endosso, interface | em toda peça | a família constante do cliente; é o fio entre campanhas (16d §5.2) |

**Lições (com medida):**
- **Fonte de impacto precisa de uma "irmã" legível.** A da Copa 2026 (FWC26, ultra-condensada preta) falhou em
  estatística e siglas no celular; a FIFA passou placar e relógio para Noto Sans (16c §1.3). A Whoop também separa
  os números (16c §1.3).
- **Na largura condensada, O e 0 viram a mesma forma** (medido): Mona Sans 900 wdth 75 O/0 = 0,97 (VETO como
  números) · Big Shoulders 900 opsz 10 = 0,98 · Archivo 800 wdth 62 = 0,70 (perto do alerta) · Archivo 500 normal = 0,43.
- **O peso preto também fecha o zero:** Rubik 900, O/0 = 0,91 (VETO); Rubik 500 = 0,74 (medido).
- **Big Shoulders não tem `tnum`**, e nela e na Mona o I é igual ao l (1,00): número e sigla vão para a irmã (medido).
- **Hubot Sans:** o zero tem traço interno e "20h30" vira "28h38" — proibida em hora e preço. **Urbanist:** I, l e 1
  quase iguais — fora de código e cupom (14 §F).
- **Preço em PT-BR** (16a §2.7): "R$" a 60–70% do corpo do número, alinhado pelo topo ou pela base; centavos
  sobrescritos ou a 50–60%; vírgula decimal (R$ 1.997,00); o preço é o 2º elemento mais forte, depois do título.
- **Cupom e código PIX:** zero cortado (`zero`) ou uma fonte sem O/0 confuso (16a §2.6).

## 4. Legibilidade com evidência
Não existe "a fonte mais legível": depende de ser parágrafo, letra pequena ou olhada rápida (16a §2). O gosto não
prova leitura: 77% acharam que leriam mais rápido na fonte preferida, e isso valeu para 20% (16a §2.1).

| Regra | Número | Origem |
|---|---|---|
| Caixa-alta | só em 1–5 palavras (título, oferta, rótulo); > 7 palavras = caixa mista. Texto corrido em caixa-alta é ~13% mais lento; palavra solta de relance lê melhor em caixa-alta | 16a §2.3 (Tinker; NN/g/MIT) |
| Condensada | só no título curto: no relance custa +11,2% de tempo; a letra mais larga é reconhecida melhor | 16a §2.2 (NN/g 2017; Oderkerk & Beier 2022) |
| Formas abertas | a, c, e, s abertos vencem os fechados no relance; grotesca quadrada fechada ~30% pior | 16a §2.2 (Sawyer; Dobres 2016) |
| Altura-x | texto: x/cap ≥ 0,66; altura-x maior ajuda na letra pequena; alta demais confunde h/n e o/d | 16a §2.1–2.2; tipos.py |
| Itálico | acento de 1–3 palavras, nunca parágrafo. Trocar para itálico no meio da frase não atrapalhou; trocar para negrito ou expandida atrapalhou | 16a §2.3 |
| Peso | texto 400–500; peso < 400 só a partir de 2× o tamanho do texto (≥ 96 px na arte 1080, ≥ 32 px no site); preto e ultra só no título | 16a §2.2, §2.4 (Apple HIG) |
| Espaçamento | texto de apoio nunca abaixo de −0,02 em; título apertado em painel iluminado perdeu leitura (Bankwest) | 16c §1.3, §4.2 |
| Serifa | não muda a velocidade em tamanho normal → escolher serifa pela voz, não pela "legibilidade" | 16a §2.2 (Arditi & Cho 2005) |
| Público mais velho | serifa em negrito e maior; nada fino, condensado ou contorno no texto | 16a §2.1, §5.14 |
| Decisão e esforço | treino, preço, condição, formulário e botão em fonte fácil: instrução de exercício em fonte difícil fez o treino parecer 15,1 × 8,2 min e tirou a vontade | 16d §4.1 (Song & Schwarz 2008) |

**Tamanhos mínimos por meio:**

| Meio | Mínimo | Origem |
|---|---|---|
| Arte 1080 (lado menor) | texto que precisa ser lido: maiúscula ≥ 34 px (= corpo 48 = 16 px CSS no celular); letra miúda ≥ 25 px | qualidade §1 |
| Live vista no celular / lower third | preço, CTA e link: maiúscula ≥ 43 px; nome ≥ 4% da altura do quadro | qualidade |
| 1,91:1 (coluna, pesquisa) | ≤ 6 palavras, ≥ 72 px | qualidade |
| Site / app | corpo ≥ 16 px; app ≥ 11 pt/sp (Apple 17/11; Material Body L 16, Label S 11) | 16a §2.4 |
| Banner 300×250 | maiúscula ≥ 14 px; só 2 tamanhos | 16a §3.2 [ponto de partida] |
| Condensada em anúncio | ≥ 64 px de corpo; abaixo, a irmã de largura normal | 16c §4.2 |

**Contraste** (qualidade): WCAG 4,5:1; 3:1 só para texto ≥ 72 px de corpo (56 em negrito) num 1080; meta 7:1 no texto
pequeno (sol). APCA Lc ≥ 75 no corpo e ≥ 45 nos títulos. O contraste real no pixel é a checagem C1 de `camadas.py`.

**Português (PT-BR):**
- Falta de acento = VETO (tipos.py); fonte de fora do Google Fonts: testar acento cortado. Na folha, conferir
  (16a §2.8): til e agudo não colam na maiúscula · cedilha não bate na linha de baixo · Ç preto não vira borrão · o til
  tem curva visível em 34 px · aspas curvas e º/ª existem.
- **Entrelinha com acento:** medir na tinta — folga ≥ 4% do corpo entre a cedilha de cima e o acento de baixo (2 §4).
- **Quebra por sentido** ("ÚLTIMAS / HORAS"); nunca "de", "e", "a", "o", "com", "para" no fim da linha (16a §5.12).
  Site: `lang="pt-BR"` + `hyphens: auto` em coluna estreita (16a §2.8). Título em caixa-alta: ligar `case` (16a §5.6).

## 5. Escala e hierarquia
- **Uma razão por peça, pelo nº de níveis** (16a §3.1): 1,125–1,2 com 6+ níveis (app, painel); 1,2–1,25 em site e
  texto; 1,333–1,618 em arte, landing e pôster. Na arte, **pular degraus** (1º, 3º, 5º) até o salto pedido.
- **≤ 3 tamanhos por peça; salto título:texto ≥ 4:1 no social e ≥ 8:1 no pôster** (2 §4; qualidade).

| Arte 1080 (razão 1,5) | Corpo | | Site (Utopia) | Celular 360–390 | Desktop 1240–1440 |
|---|---|---|---|---|---|
| Miúda (legal, rodapé) | 36 px (maiúscula ≈ 25) | | legenda | 15 | 16 |
| Texto (base) | 48 px (maiúscula ≈ 34) | | texto | 18 | 20 |
| Chamada | 72–108 px | | sub / h3 | 21,6 / 26 | 25 / 31 |
| Título | 162–243 px · condensada 243–365 · larga 108–162 | | h2 | 31 | 39 |
| Herói (1 palavra/número) | 300–480 px, pela largura útil | | h1 (interno / topo) | 37 / 45–46 | 49 / 61 (84 se "de cartaz") |

[ponto de partida] (16a §3.2, §4.0). Serifa de alto contraste e peso < 400 nunca abaixo de 96 px; mono de dado ≥ 64 px.
No site, 390 ≈ o valor de 360 e 1440 = o máximo do `clamp()`.

**Entrelinha** (16a §3.4): `clamp(1.0, 1.5 − 0.12·log2(px/16), 1.6)` dá 1,5 em 16 px, 1,38 em 32, 1,26 em 64 e
1,14 em 128, e trava em 1,0 a partir de ~290 px. Ajustes: caixa-alta display sem acento 0,86–0,95 (2 §4), com
acento pela tinta (folga ≥ 4%) · altura-x alta +0,05 a +0,1 · texto claro sobre escuro +0,05 [ponto de partida] · com
3 linhas ou mais, nunca apertada (Apple, 16a §2.5).

**Espaço entre letras (tracking)** (2 §4; 16a §3.5):

| Situação | Tracking |
|---|---|
| Texto 11–16 px | 0 a +0,045 em |
| Caixa-alta pequena (rótulo) | +0,05 a +0,12 em |
| Caixa-baixa ≥ 48 px | ≈ −0,02 em (curva da Inter) |
| Caixa-baixa display ≥ 120 px | −0,01 a −0,04 em, conferido na tinta [ponto de partida] |
| Caixa-alta display ≥ 120 px | 0 a +0,02 em |
| Condensada display | 0 a +0,01 em (já é apertada) |
| Fonte com `opsz` | ≈ 0 (o tamanho óptico já corrige) |

**Medida de linha** (16a §2.5, §3.6): site 45–75 caracteres (`max-width: 60–66ch`); celular 28–40; arte e legenda
≤ 42 × 2 linhas; nunca < 25.

**CSS de site** (16a §3.7–3.9; 16c nº 54–57):
- `:root{font-size:100%}`, texto em `rem`, media query em `em`; título fluido como
  `clamp(2.8rem, 1.8rem + 4.45vw, 5.25rem)`. Fonte só em `vw` não cresce com o zoom e reprova a WCAG 1.4.4.
  **Teste:** zoom 200% a 1240 px — o corpo dobra; se o h1 ficar < 2× o corpo ampliado, aumentar o termo em `rem`.
- **WCAG 1.4.12:** nada quebra com entrelinha 1,5, parágrafo 2×, letras 0,12 e palavras 0,16 → caixa de texto nunca
  tem altura fixa.
- **`opsz`:** `font-optical-sizing: auto` no site. No nosso motor em curvas não é automático: instanciar
  `opsz ≈ corpo na arte ÷ 3` (título de 240 px num 1080 → `opsz` 72–80).
- **Duas famílias na mesma linha:** `font-size-adjust: ex-height` (palavra-acento: `cap-height`). O `par` avisa
  quando Δ x/cap > 0,06.
- **Alinhar título e texto de famílias diferentes pelo topo da maiúscula:** `text-box: trim-both cap alphabetic`.
- `text-wrap: balance` no título e `pretty` no parágrafo; `font-synthesis: none` (nunca itálico ou negrito falso).
- Fontes da 1ª tela ≤ ~150 KB de woff2 (subset latin + variável) [ponto de partida] (16a §6 nº 27).

## 6. Voz → fontes grátis (ponto de partida, nunca a resposta pronta)
**Escolher por congruência** (16d §4): a fonte "no tom" do produto foi escolhida **2× mais** (Doyle & Bottomley 2004)
— dar nota de força e de velocidade à peça e escolher uma fonte com o mesmo perfil. **Redondo acolhe, reto empurra**
(Jiang 2016; Velasco 2015). Letra incompleta (estêncil, recorte, glitch) = inovadora, mas **menos confiável**
(Hagtvedt 2011): lançamento sim, checkout e garantia não. **Manuscrita = pessoa, nunca método** (Schroll 2018).

| Voz | Título + texto/dado (2–3 opções) | Evitar |
|---|---|---|
| Técnica / científica | IBM Plex Sans Cond. + Plex Mono · Martian Mono + Atkinson Next · Chivo + Chivo Mono | Orbitron; mono em parágrafo |
| Atlética / explosiva | Big Shoulders 900 + Archivo 500 · Saira (wdth 50–125) · Sofia Sans Extra Cond. + Sofia Sans | Bebas/Anton/Oswald no automático; condensada pequena |
| Premium / luxo | Bodoni Moda (opsz 96) + Hanken Grotesk · Gloock + Host Grotesk · Playfair 2.0 + Albert Sans | didone fina pequena; Cinzel/Trajan |
| Editorial / autoridade | Newsreader + Schibsted Grotesk · Literata + Libre Franklin · Source Serif 4 + Source Sans 3 | Playfair Display "de blog" |
| Jovem / irreverente | Syne + Onest · Unbounded + Instrument Sans · Darker Grotesque + Reddit Sans | 2 fontes "esquisitas" na mesma peça |
| Acolhedora / humana | Fraunces* (SOFT) + Figtree · Young Serif + Karla · Alegreya Sans | arredondada em tudo; bege + serifa macia + planta |
| Institucional / confiável | Public Sans + Source Serif 4 · Libre Franklin + Libre Caslon Text · Noto Sans | Arial/Calibri; brasão com Trajan |
| Tecnológica | Geist + Geist Mono · Mona/Hubot Sans (wdth 75–125) · Science Gothic · Tomorrow | Orbitron/Exo em neon; roxo + Inter |
| Artesanal | Caprasimo + Figtree · Fraunces* WONK · Londrina Solid | fonte "gasta" pequena; 2 manuscritas |
| Urgente / varejo | Archivo 900 (wdth 62) + Archivo 500 · Bowlby One + Rubik 500 · Dela Gothic One + Golos | 5 fontes num banner; Impact; preço sem `tnum` |
| Ao vivo / transmissão | Saira Condensed + Azeret Mono · Barlow Semi Cond. + JetBrains Mono | peso fino (some no vídeo); número sem `tnum` |
| Documento / sigilo | Big Shoulders Stencil ou Saira Stencil + Courier Prime · IBM Plex Mono | máquina "suja" pequena; carimbo torto |
| Clínica / saúde | Atkinson Hyperlegible Next + Newsreader · Inclusive Sans · Figtree + Fragment Mono | cinza claro + fino; "fonte que trata dislexia" (mito) |
| Educativa / didática | Gabarito + Literata · Lexend + Atkinson Next · Andika | decorativa no enunciado; cursiva no conteúdo técnico |
| Comunidade | Familjen Grotesk (+ Permanent Marker em 1 palavra) · Gabarito + Rubik | grafite em texto que precisa ser lido |
| Popular brasileira | Coiny + Rubik 500 · Londrina Solid + Figtree | produto premium |
| Retrô esportivo | Graduate + Archivo · Big Shoulders Inline + Big Shoulders · Jersey 10 (número) | muito texto; fantasia americana sem motivo |
| Calma / bem-estar | Instrument Serif* itálico + Hanken Grotesk · Jost 300 + 400 · Newsreader Light Italic | peso 200–300 pequeno ou sobre foto; > 2 itálicos |

Fontes: 16d §2 e 16a §4.13. \* = está na lista das "cansadas" (16b §20): só com o eixo que a tira do clichê (SOFT,
WONK), nunca em creme + terracota.

**Catálogo da casa por gênero** (2 §3.2; 16b §21):

| Gênero | Famílias |
|---|---|
| Grotesca com caráter | Schibsted Grotesk (só peso: precisa de recurso próprio) · Geologica (SHRP) · Funnel Display · Epilogue · Host Grotesk · Ojuju · Stack Sans · Zalando Sans · Special Gothic |
| Mono / dados | Martian Mono (wdth 75–112,5) · Recursive (MONO/CASL) · Sixtyfour · Doto · Handjet · Kode Mono · Monaspace · Departure Mono |
| Condensada / pôster | Big Shoulders (+ Stencil) · Sofia Sans Extra Cond. (1–1000) · Pathway Extreme (opsz + wdth) · Saira · League Gothic · Rajdhani |
| Larga / estendida | Anybody (wdth 50–150) · Archivo (62–125) · Mona/Hubot (75–125) · Science Gothic (50–200) · Strichpunkt Sans · Dela Gothic One |
| Serifa editorial | Newsreader · Bodoni Moda · Playfair 2.0 (opsz até 1200) · Gloock · Young Serif · Roboto Serif · Platypi · Wittgenstein · Montagu Slab |
| Display expressiva | Tilt Warp (giro 3D) · Roboto Flex · Tomorrow · Bungee · Kalnia · Sinistre · Texturina · Karrik |

**Top 40 pouco batidas** (16b §21; as de 2026 ainda sem prova renderizada — folha antes de propor): Zalando Sans,
Special Gothic, Stack Sans, Nata Sans, Mozilla Headline/Text, Scoutie Sans, Strichpunkt Sans, Valley Sans,
Atkinson Hyperlegible Next, Savate, Ysabeau, Asap Sharp, Gabarito, Elms Sans, Science Gothic, Pathway Extreme,
Caacupé One, Ancizar Sans/Serif, Labrada, Platypi, Wittgenstein, Playfair 2.0, Roboto Serif, Gloock, Kalnia, Sprat,
Montagu Slab, Monaspace, Departure Mono, Datatype, Recursive, Shantell Sans, Geologica, Commissioner, Playpen Sans,
Sinistre, Texturina, Saira Stencil, Handjet, Karrik.

**No lugar das pagas dos sites de referência** (14 §F; 14b §0, §2):

| Paga | Grátis | Cuidado medido |
|---|---|---|
| CoFo Peshka (condensada quadrada) | Rajdhani · Saira Extra Cond. · Big Shoulders Display · Tektur | "%" da Tektur é estranho; League Gothic estreita demais para ler |
| Gilroy (texto geométrico) | Urbanist · Outfit · Figtree ou Onest (as melhores no celular) · Hanken Grotesk | Urbanist I = l = 1; Plus Jakarta e Poppins são "padrão de IA" |
| Kurdis (larga técnica) | Mona Sans wdth 125 · Hubot Sans 125 · Familjen Grotesk · Archivo 125 | zero da Hubot ("28h38"); Mona 75 O/0 = 0,97 → números nunca nela |

### 6.1 Vetos
- **"Padrão de IA": proibidas como VOZ.** O `tipos.py` dá VETO no título e ALERTA no texto (só com motivo escrito):
  Inter, Poppins, Montserrat, Roboto, Open Sans, Lato, Plus Jakarta Sans, Space Grotesk, Manrope, DM Sans, mais
  Arial/Helvetica/fontes do sistema (16a §4.0; tipos.py).
- **Cansadas em 2026: evitar como voz** (16b §20; 16c §1.2; 2 §3.1): Bebas Neue, Oswald, Anton e os clones da Druk ·
  Bricolage Grotesque · Raleway · Satoshi, General Sans, Cabinet Grotesk, Clash Display ("visual startup") · Neue
  Montreal, Diatype, Söhne ("o Inter dos estúdios") · Playfair Display, DM Serif Display, Abril Fatface, Cormorant
  ("luxo de modelo") · Nunito, Quicksand, Comfortaa, Varela Round, Fredoka ("app infantil") · Lobster, Pacifico,
  Dancing Script, Great Vibes, Caveat como voz · Orbitron, Audiowide, Exo 2, Press Start 2P, VT323, Black Ops One,
  Stardos Stencil. Atalho: se está no topo do Google Fonts "Popular" ou num modelo do Canva, no máximo é texto de apoio.
- **Vetos de uso (cara de template/IA)** (2 §6; 16d §3.2):
  - "sobrancelha" em CAIXA-ALTA espaçada acima de cada título · "A · B · C" ligados por ponto · "→" no fim de botão;
  - **mono abaixo de 64 px de corpo na arte como etiqueta de dado espalhada**; a mono só como protagonista (timecode
    grande, contagem, ficha que É a ideia) (16a §4.0, §6 nº 23);
  - fundo quase preto + 1 acento ácido sem outra ideia · serifa de alto contraste em creme + terracota · roxo + Inter;
  - a fórmula do infoproduto BR: fundo escuro + condensada em caixa-alta + Montserrat/Poppins + dourado ou neon + "%"
    gigante · contorno + sombra + 3D juntos · esticar sem eixo (`scaleX`) além de ±3% (use `wdth`) · 5–8 famílias.

## 7. Voz própria e técnicas para inovar sem perder a leitura
**O que torna a tipografia PRÓPRIA sem desenhar uma fonte** (2 §1.3; 16d §3.3):
- **3–5 glifos assinatura** tirados do logo ou do assunto (o til de Ã/Õ vira uma mini-TARJA; o "0" vira visor; o
  "%" da oferta). A OFL deixa modificar, mas a versão modificada não usa o nome reservado: renomear.
- **1 deformação** em toda a campanha (fatiar, esticar pelo eixo, estêncil, tarjar), como no Public Theater; **1
  detalhe repetido** (um corte em todas as letras do título); **eixo com regra**: larguras programadas por palavra
  (nunca sorteio; `fonts.py "Família:peso:wdth=75"`) ou movidas por dado (o timecode "respira" a cada segundo).
- **Recursos tipográficos** (tarja, colchetes, cantos de visor) com regra de onde entram e do que nunca cobrem (CTA,
  preço revelado). O movimento segue a mesma regra do estático.
- **Receita:** regra de deformação tirada do conceito → voz + no máximo 1 parceira → glifos assinatura → escala (§5) →
  2–3 recursos com regra → estresse ("PROMOÇÃO / ÚLTIMAS HORAS / NÃO PERCA / AÇÃO" empilhado, 10 formatos, versão em
  1 cor, foto com scrim medido).

**Regra-mãe da técnica** (16c §2; 16a §5): no máximo 1 técnica expressiva por camada de leitura (título 1–2; texto de
apoio e CTA, 0); com 3+ técnicas, uma é a estrela e as outras ficam com ≤ 30% da presença; mudar UMA variável por vez,
só no título, por uma regra com sentido; teste dos 2 segundos: a palavra-chave se lê a 25%.

| Nº 16c | Técnica | Regra | Anúncio |
|---|---|---|---|
| 1 | Larguras misturadas na palavra (`wdth`) | rampa com sentido; letra mais estreita ≥ 60% da média | seguro |
| 6 · 7 | Itálico de acento · serifa + grotesca na frase | 1–3 palavras; igualar pela maiúscula, mesma linha de base | título ≥ 120 px |
| 8 · 9 | Display + irmã legível · mono como dado | número e texto pequeno na irmã; mono ≥ 64 px | seguro |
| 10 | Glifos alternativos (`ss01`…) | trocar 1–3 glifos frequentes no sistema todo; nunca o que muda a leitura | marca/site |
| 13 · 24 | Numerais com intenção · numeral herói | `tnum` se muda, `pnum` se parado; símbolo a 55–70% | seguro |
| 18 | Empilhado com quebra de sentido | linha nunca só com artigo; acento medido entre linhas | seguro |
| 19 | Bloco justificado por largura | a haste varia ≤ 10% entre linhas | título |
| 22 | Entrelinha negativa com encaixe | nenhuma letra fundida que vire outra | título |
| 23 | Escala extrema (≥ 1:8) | ≤ 3 tamanhos | seguro |
| 27 | Tipo em caminho/círculo | raio ≥ 3× a altura da letra | título |
| 29 | Marcador (highlight) | texto × faixa ≥ 4,5:1 | seguro |
| 36 | Foto dentro da letra | haste ≥ 18% da maiúscula; maiúscula ≥ 200 px | só letra pesada |
| 38 | Vazado (knockout) | máscara limpa em curvas | seguro |
| 39 | Letra atrás da pessoa | palavra ≤ 30% coberta, letra ≤ 50%, 1ª letra ≤ 15% (camadas C4) | título |
| 43 | Contorno + preenchida | traço ≥ 2% da maiúscula e ≥ 3 px, só ≥ 120 px, por trás; nunca a única versão da informação | seguro |
| 44 | Sombra dura | mesmo ângulo em toda a série | seguro |
| 46 | Misregistro (riso) | deslocamento ≤ 4% da maiúscula | título |

Outros limites (2, tabela b): rotação 0°, ±90° ou o ângulo do logo · corte fora do quadro ≥ 60% de cada letra, 1ª letra
inteira, nunca cortar acento/til · repetição (eco) 3–7×, passo linear num só eixo, 1 repetição herói.

**Quando NÃO inovar** (16a §5.14; 16d §4.3; 16c §4.3):
- preço, data, hora, endereço, cupom, telefone, legal, campo de formulário e botão: fonte de texto/âncora, sem efeito;
- saúde, finanças, governo, checkout, garantia e pós séria: inovação só no título, o resto concordante; nada de
  estêncil, recorte ou glitch;
- plano de treino, passo a passo e "como funciona": fonte fluente; público mais velho: nada fino ou condensado;
  anúncio pequeno: evitar as técnicas 20, 26, 31, 37, 47, 48, 50, 51, 52, 63 e 66–68.

## 8. Tipo em movimento e em vídeo
- **Tempo parado:** `máx(1,2 s; 0,35 s × palavras + 0,5 s)`; número ou preço conta como 2 palavras; a animação de
  entrada não conta. 4 palavras → 1,9 s; 8 → 3,3 s (16c §3.2; substitui o "≥ 1,5 s" fixo de 2 §2). Lower third
  ≥ 4 s (qualidade). Legenda: 0,33–0,375 s por palavra, ≤ 17 caracteres/s, ≤ 42 caracteres × 2 linhas (16c §3.2; 2 §5).
- **Palavra a palavra ou linha a linha > letra a letra:** a compreensão foi bem maior em tela pequena. Letra a letra
  só em logo ou numa palavra (16c §3.1). Do mais seguro ao mais arriscado: linha (62) · bloco + 1 palavra que troca
  (64) · contagem (69) · palavra por batida · eixo (65) · letra a letra (63) · zoom no tipo / glitch.
- **Durações** [ponto de partida] (16c §3.2): linha 500–800 ms (80–150 entre linhas) · palavra 300–450 ms (60–100) ·
  letra 250–400 ms (25–45) · eixo variável 300–600 ms, ≤ 2 eixos ao mesmo tempo · saída 50–100 ms mais curta.
- **Vídeo curto:** 1ª palavra legível até 0,5 s e texto parado aos ~1 s (16c §3.2).
- **Regras de ouro** (16c §3.5): um movimento por frase; o tipo para antes de ser lido; a palavra-chave chega primeiro
  ou por último; a entrada tem o sentido do assunto; o quadro-chave congelado vira a arte estática.
- **Acessibilidade** (16c §3.3): `prefers-reduced-motion` → corte seco ou fade ≤ 200 ms; o que se move sozinho por
  > 5 s junto de outro conteúdo precisa de pausa (WCAG 2.2.2); nada pisca > 3×/s (WCAG 2.3.1); SplitText com
  `aria:"auto"`, depois de `document.fonts.ready`; se o JS falhar, o texto aparece parado.
- Contador e preço que mudam: `tnum` sempre (2 §4). Animar `wght`/`wdth` numa fonte que muda de largura empurra a
  linha: travar a caixa (16a §5.2; 14b §2.1). Animar eixo está em ~0,3% das páginas — já é o 1% que se destaca (16c §1.0).

## 9. Anúncio no celular: o que muda (16c §4.2, a partir de 4.1)
| | Peça de marca / site | Anúncio no celular |
|---|---|---|
| Palavras na arte | até ~25 | título ≤ 7 palavras (< 40 caracteres) + oferta + marca; o resto no texto do anúncio |
| Níveis de leitura | 3–4 | 2 (gancho + prova/oferta); o CTA é o botão do app |
| Texto de apoio | peso 300–500 | peso ≥ 500; preto/ultra só no título grande |
| Largura | condensada ok | condensada só ≥ 64 px; abaixo, a irmã normal |
| Técnicas expressivas | 2–3 | 1, a que carrega a ideia |
| Movimento | entrada elegante | texto parado e legível até ~1 s; 1 palavra-chave por corte; legenda sempre (som desligado) |
| Prova | WCAG | WCAG + miniatura a 25% + teste borrado (simula a tela pequena) |
| Versões | 1 | 1:1 · 4:5 · 9:16 + 1 SEM texto (Google PMax; essencial nos 80% centrais) |

Não existe estudo público que isole a fonte em anúncio de celular: a prova final é A/B próprio (mesma arte, só a
tipografia muda) (16c §4.1; 16d §4.2).

## 10. Inovar sempre: rotação entre campanhas, constância dentro da série
Modelo: o Public Theater usa a mesma fonte com um tratamento novo por temporada, ligado a um fato da temporada; nas
identidades dinâmicas, o tipo é o vetor constante (16c §5.1). **Não giram:** família(s) da marca e a âncora,
cor-base, logo, a irmã de dados, as regras de leitura e o grid (16c §5.2).
Matriz de 10 eixos (`tipos.py rotacao --matriz`): **T** tratamento · **A** arranjo · **E** escala · **V** voz
secundária · **I** imagem · **S** superfície · **X** eixo variável estrela · **M** movimento (com `--video`) ·
**D** densidade · **C** cor do tipo.

| Regra (16c §5.3) | Como o `tipos.py rotacao` aplica |
|---|---|
| Mudar 3–5 eixos em relação à campanha anterior (< 3 = "de novo"; > 5 = deixa de ser a marca) | sorteia só combinações a 3–5 eixos da última |
| T muda sempre e não repete nas últimas 4 campanhas (ou 12 meses) | T entra sempre na troca; os 4 últimos T ficam proibidos |
| Valor usado em 2 campanhas seguidas descansa por 3 | some das opções enquanto descansa |
| Distância ≥ 3 de cada uma das últimas 3 campanhas | descarta o resto; as 5 opções diferem ≥ 3 entre si |
| O T sai de um fato do briefing (reforma circular → círculo) | `--fixar T7`; sem fato, as opções vêm da mais diferente das últimas 3 para a menos |
| 1 em cada 4 campanhas pode trocar a voz inteira por um ciclo (logo e cores seguram a marca) | decisão manual |
| Combinação que falha no verificador (tamanho, colisão, contraste, tempo de leitura) sai antes da arena | portões de `qualidade.md` |

- Projeto novo do mesmo cliente: `par --cliente` alerta família já usada em outro projeto ou citada nas fichas da
  biblioteca. A mesma receita não vira voz principal de dois clientes (16a §4.13). Prova visual extra:
  `library.py novelty` contra as peças anteriores (≥ 0,93 = quase cópia) (16c §5.4).
- **Série (dentro da campanha):** a tipografia é constante — mesmas famílias, mesmos papéis e os mesmos T, X e C em
  todas as peças (16c §5.3 nº 3; `composicoes.md` §6 nº 1). Variam peça a peça A, E, I e D (os arquétipos); duas peças
  seguidas nunca com o mesmo A + I. Nunca dois sistemas tipográficos na mesma campanha (16d §5.2); na Black Friday não
  se troca de fonte: muda cor, peso, tamanho e composição (16d §3.3).

## 11. Licenças (16b §0, §22; 14b §2.0; 16d §3.4)
| Licença | Pode | Não pode |
|---|---|---|
| **OFL 1.1** (quase todo o Google Fonts) | logo, arte, site via `@font-face`, app, PDF, vender a peça; embutir o arquivo no projeto; modificar | vender a fonte sozinha; versão modificada com o nome reservado (RFN) |
| **Apache 2.0** | quase tudo, mantendo o aviso de licença | — |
| **ITF FFL** (Fontshare) | uso pessoal e comercial, logo e site | redistribuir, revender ou alterar o arquivo; subir o `.woff2` em repositório público (quem quiser baixa em fontshare.com) |
| **Adobe Fonts** (plano do usuário) | imagem, vetor, logo; no site só pelo Web Project da Adobe | passar o arquivo adiante; hospedar por conta própria |

1. **Subset de OFL** (cortar glifos para a web) = modificação → pode exigir renomear se a fonte tiver RFN (OFL FAQ
   2.6). Converter para WOFF2 sem mexer no desenho = ok (FAQ 2.2.1). Texto em curvas num logo = uso; a arte não vira OFL.
2. **"Grátis" que não é:** Pangram Pangram (comercial é pago), Lost Type, versões "demo/personal use" de lojas. Ler o
   OFL.txt/LICENSE **do pacote**, nunca o do site agregador (dafont, 1001 fonts).
3. **Arquivo "Trial" nunca**, nem em teste publicado (16d §3.2). Velvetyne e Collletttivo: ler a licença de cada
   fonte (algumas Velvetyne têm a CUTE; a Collletttivo pede crédito) e testar o PT-BR. Fontshare: ler o FFL.txt antes
   de hospedar; no nosso motor, preferir OFL.
4. **Pago → Adobe primeiro (regra do usuário):** fonte, elemento, foto, ícone ou textura PAGA → antes de criar ou
   buscar algo grátis, checar no conector Adobe se o plano do usuário já cobre: `font_search` (com `font_query=true`)
   → `font_details` (`library_availability.full = true` = incluída, não é teste). Não está → procurar PARECIDA dentro
   do Adobe (busca por nome de candidatas; a busca descritiva costuma errar) e comparar no olho lado a lado com a
   original; só depois a grátis, como 2ª opção. Site usa kit web (`font_create_kit`); app/arte, `font_activate`.
   Fotos/recursos: `asset_search` no Adobe Stock (licenciar gasta crédito → pedir autorização antes).
5. **Checagem:** `tipos.py ficha` lê a licença (name 13/14) e dá VETO se não identificar; no Google Fonts, a pasta diz
   a licença (`ofl/`, `apache/`, `ufl/`). Registrar nome, versão, licença, origem e data em `fontes/LICENCAS.md` do
   projeto (16b §22 nº 8). Marca permanente: busca no INPI também.

## 12. Vários sistemas tipográficos numa mesma marca (por linha de produto)
Quando uma marca tem várias linhas (curso, evento, mentoria, conteúdo), cada linha pode ter seu sistema de título,
desde que a marca segure a constância:
- **Âncora fixa:** uma família de texto/interface (ex.: Archivo, wdth 62–125) em CTA, preço, rodapé, legal, interface
  e endosso, em todos os sistemas; logo, endossos e cores oficiais não mudam.
- **Preço SEMPRE na largura normal** da âncora (wdth 100, peso 500–700, `tnum`). Medido: condensada pesada fecha o
  zero (O/0 sobe de ~0,5 para 0,7+; fontes como Mona 75 e Rubik 900 dão VETO).
- **Mapa linha → sistema** escrito (ex.: ciência → serifa editorial; ao vivo/contagem → condensada em caixa-alta +
  mono de relógio; acolhimento → serifa suave + manuscrita em 1–3 palavras), proposto e testado com `tipos.py`.
- Antes de fixar: 1 peça-teste por sistema nos portões de `qualidade.md` e um A/B na Meta. Cuidados medidos: fonte sem
  `tnum` ou com I = l → número na mono ou na âncora; texto abaixo de 400 pede 2× o tamanho; mono de dado ≥ 64 px na
  arte; estêncil nunca em preço ou checkout.

## 13. Lacunas
- `tipos.py` ainda não mede esqueleto (matriz), contraste do traço, abertura, serifa, acento de maiúscula (`.case`),
  itálico verdadeiro nem acento cortado pelas métricas (16a §6 nº 5, 7, 10, 13, 14, 16). Os limites de confusão foram
  calibrados com só 10 fontes.
- Fonte em anúncio de celular no Brasil: nenhum estudo público → A/B próprio (16c §7; 16d §6).
- Tempos de movimento: ciência pequena; calibrar vendo a 1× no celular (16c §7).
- A relação `opsz` × px no Chrome não está documentada: testar com régua (16a §8).
- Banner de display sem tamanho mínimo oficial (16a §8). O texto exato da FFL da Fontshare não foi lido (16b §23).
- Fontes de 2026 e "pouco batidas" ainda sem folha renderizada; "cansada" e "pouco batida" são inferências de mercado
  (rankings sem método) (16b §23; 16c §7).
