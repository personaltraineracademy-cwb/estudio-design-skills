# Linguagem de forma — raio 0 × curva × pílula (regras congeladas)

Regra: evitar excesso de quadrado; elementos levemente arredondados (nas redes a maioria usa raio ~10) e raio 0 só em
coisas específicas, onde se destaca. A forma muda nos ELEMENTOS, nunca no logo nem na identidade: **o logo nunca
arredonda** sem o cliente pedir.

## 1. O que a evidência permite dizer
- Preferência por curva existe, mas é **média** (meta-análise de 61 estudos, g = 0,39), forte no relance e **some em
  designers/arquitetos** e em ambientes. Gosto do estúdio ≠ gosto do público.
- **Canto vivo é mais saliente** e, no feed, é raro (2,9% de 514 design systems com botão reto) → o reto salta 2 vezes
  (forma + raridade). Isso é DESTAQUE, não "leitura mais fácil" ("redondo é mais fácil de processar" = mito).
- Curva → maciez, cuidado, calor humano. Reto → durabilidade, competência, premium (este último só para quem compra
  por status). Se texto e forma brigam, o texto vence.
- Não existe estudo de raio × clique/venda em anúncio: o único jeito de saber é anúncio A × B.

## 2. Arte ≠ site (a conta que muda tudo)
- **Raio de arte 1080 ≈ 2,75 × raio de site** (celular de 393 px CSS; 3,0 no de 360).
- O "raio 10 das redes" = **28 px na arte**. 8/12/16 de arte viram 3/4/6 px no celular (quase invisível).
- Contraste 0 × curva só aparece no celular se a curva for **≥ 24 px de arte** (F9).
- Story 9:16: a tela do celular já arredonda ≈ 151 px de arte; moldura recuada 108 px → raio ≈ 43 (concêntrica).

## 3. Escala padrão (ponto de partida para qualquer marca; trocar a semente muda a personalidade)

| Token | Arte 1080 | Site (px CSS) | Papel |
|---|---|---|---|
| `vivo` (none) | 0 | 0 | sinal/assinatura, dado, foto sangrada, borda da tela |
| `rotulo` (sm) | 16 | 6 | etiqueta, rótulo de dado, campo de formulário |
| `cartao` (md) | 28 | 10 | cartão, painel, foto em cartão, lower third, monitor |
| `moldura` (lg) | 44 | 16 | moldura recuada, modal, bloco grande, moldura 9:16 |
| `pilula` (full) | 9999 | 9999 | botão de ação do site, filtro, rótulo de 1 linha ≤ 3 palavras |
| `ponto` (círculo) | 50% de um quadrado | 50% | ponto ao vivo, avatar de PESSOA, furo |

Geração: semente md × (0,57 · 1 · 1,57) → sm/md/lg; site = arte ÷ 2,75. Pílula = `9999px`, nunca `50%` (vira
elipse em retângulo). Raio em `%` num retângulo = canto oval (F7).

## 4. Regras por elemento (resumo da 17a §4.2)
- **Tarja / faixa de texto / marca-texto:** reto (objeto impresso, urgente). Várias linhas = mesmo raio em todas ou 0;
  pílula só em 1 linha ≤ 3 palavras.
- **Botão (site):** pílula OU raio da família; **nunca** pílula num e reto noutro da mesma hierarquia. Raio ≈ 15–25%
  da altura. **Anúncio não desenha botão** (frase de ação como texto, pesquisa 5).
- **Campo:** ≤ raio do botão (sm). Nunca pílula em campo de várias linhas.
- **Cartão:** md fixo pelo token; ≤ ½ do menor lado; filho = pai − espaço.
- **Foto:** 0 se tela cheia/sangrada/"revista"/produto; md se solta em layout de app; **pessoa = círculo** (avatar);
  foto encostada num lado do cartão herda o raio só daquele lado (12/12/0/0).
- **Tabela, célula, fio, divisória, grade:** 0.
- **Modal/folha:** md–lg; folha de baixo só em cima (28/28/0/0).
- **Selo:** círculo ou estrela; não pode parecer clicável.
- **Borda do post:** sempre reta (a plataforma corta em retângulo).

## 5. Por contexto (o que o canto diz)
Urgência/ao vivo → 0 no elemento de urgência + círculo só no ponto · Preço/oferta → 0 ou sem caixa (nunca balão
estourado) · Autoridade/editorial → 0 em foto, moldura, grade · Acolhimento (depoimento, aluno, FAQ) → md + avatar
círculo · Dado/técnico → 0 · Luxo → 0 + fio fino + respiro · Esporte → 0 na foto + pílula no controle (Nike) ou 0 em
tudo (adidas).

## 6. Combinar de propósito (o que vira hierarquia e o que vira bagunça)
- Por peça: **1 valor da família** + `vivo` (0) + `ponto`/`pilula` = **no máximo 3 formas de canto**. Site: ≤ 3
  valores de família por tela.
- Cada forma tem UMA função; o raro tem que continuar raro (se o 0 virar maioria, perde o destaque).
- Bagunça: dois raios quase iguais na mesma peça (razão entre 1 e 1,5 — F8); duas formas para o mesmo papel (F4);
  pílula em várias linhas (F11); respiro interno < raio em contêiner com texto (F13).
- **Aninhado:** interno = externo − (borda + espaço), nunca negativo. Espaço ≥ raio externo → interno 0 = **reto
  dentro de redondo é a conta certa**, não erro. Para fora (foco, moldura externa): externo = interno + afastamento.
- Raio > ½ do menor lado: o navegador reduz TODOS os raios calado; no SVG quebra → prender no gerador (F6).

## 7. Três combinações-padrão para testar numa marca (folha A/B/C)
| | Nome | Regra |
|---|---|---|
| **A** | o reto é o sinal, a curva é o conteúdo | o que é ASSINATURA da campanha (logo, tarja, visor, relógio, grade de telas, rótulo AO VIVO) fica 0; conteúdo e gente ganham a curva da família |
| **B** | tudo macio, um corte | tudo com a curva; só o HERÓI de cada peça fica 0 (máxima saliência) |
| **C** | reto editorial, uma pílula | tudo 0 + 1 pílula por peça (controle; é o "muito quadrado") |
Julgar a 100% e a 25% (miniatura da grade), olhos apertados (`camadas.py`), "onde o olho para primeiro?". Teste real:
anúncio A × B com o mesmo texto e público. Na implementação, guardar a escala em `FORMA`, as combinações em `COMBOS`
e gerar uma folha 5 × 6 de variações para comparar.

## 8. Documentar (design system e manual)
- Tokens DTCG 2025.10: tipo `dimension` (px/rem; não existe `%`); **duas camadas** — escala (`radius.none/sm/md/lg/
  full`, com o valor de arte em `$extensions`) e **papéis** (`radius.card`, `radius.tarja`, `radius.button`,
  `radius.field`, `radius.media`, `radius.avatar`, `radius.focus` = papel + 2). Componente usa só PAPEL.
- `brand.json.shape`: `{escala, site, papeis, nunca_arredonda, combo, regra}` (17a §8).
- Página "Forma" do manual: regra em 1 frase · escala em tamanho real (arte e site) · mapa elemento → papel → raio
  (inclusive o que é sempre 0) · conta do aninhado · 3 certos × 3 errados · prova a 100%/25% · "o logo não
  arredonda".

## 9. Checagens (F1–F14, para `forma.py`/`palco.qa`)
F1 raio fora da escala · F2 valores de família por peça (≤ 1) / tela (≤ 3) · F3 formas por peça ≤ 3 · F4 mesmo papel,
forma diferente · F5 aninhado errado · F6 raio > ½ lado · F7 `%` em retângulo · F8 raios quase iguais · F9 contraste
0 × curva < 24 px de arte · F10 tinta no canto da tela 9:16 (< 151 px) · F11 pílula em várias linhas · F12 logo/tarja/
visor arredondado (quando a marca diz que não) · F13 respiro < raio · F14 foco ≠ raio + afastamento.
