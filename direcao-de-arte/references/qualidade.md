# Qualidade técnica: o que o motor mede

Este arquivo é a parte TÉCNICA (portão A) do protocolo único de revisão:
`../revisao-de-design/SKILL.md` (régua, olho, limite de 2 rodadas, formato do relatório).

Portões técnicos desta skill, nesta ordem; os dois primeiros têm que dar ZERO avisos:
1. **Verificador do palco** (`palco.Palco.render` → avisos): geometria.
2. **Prova de camadas** (`camadas.provar`): montagem camada a camada, notan, olhos apertados, mapa de destaque,
   espelho, grade + zonas + tinta + rostos.
3. **Simulador da interface** (`interface.py`): a interface do app por cima da peça, com as linhas oficiais e a área
   de texto.
4. **Inspeção a 100%** (`palco.inspecao`, 4 quadrantes) + miniatura a 25%.

## 1. Verificador do palco (geometria)
Cada elemento declara `data-qa` (rótulo), `data-tipo` (txt · logo · barra · foto · rotulo · fundo), `data-l`/`data-r`
(sobras laterais da tinta) e, quando for o caso, `data-ler="1"` (texto que PRECISA ser lido), `data-sangra="1"`,
`data-alinha="0"` e `data-heroi="1"`. A caixa de todo texto abraça a tinta (`width: fit-content`).

| Checagem | Regra |
|---|---|
| Margem | nada fora de `m` (7,4% do lado menor; mercado usa 5–8%, mínimo 72 px). A margem LATERAL nunca é menor que a zona lateral do app (9:16 → 108). Tolerância tipográfica: acento, sobra de letra redonda e descendente podem passar |
| Zona da interface do app | texto/logo/barra fora de `FORMATOS[fmt]["zona"]` (tabela abaixo) |
| Ícones do app | texto/logo/barra fora de `FORMATOS[fmt]["excl"]` (coluna do Reels: x > 852 com y > 936; cantos do feed) |
| Colisão | entre txt, logo e barra (1 px de folga mínima) |
| Moldura | texto/logo não encosta nos cantos do visor |
| Texto sobre a PESSOA | medido no alfa do recorte; rótulos "sobre-foto" são exceção declarada |
| Quase alinhado | bordas a 0,5 px–1,5% do lado menor = erro; alinhar de verdade ou separar claramente |
| Texto pequeno | maiúscula < 25 px (letra miúda, rótulos) num lado menor de 1080 |
| Texto que precisa ser lido | `data-ler="1"` com maiúscula < 34 px (= 48 px de corpo = 16 px CSS no celular de 360 px): data, hora, oferta, valor, frase de ação, nome do produto |

## 2. Prova de camadas (`camadas.py`): o olho sênior, automatizado
Camadas (`data-plano` 0–7; sem o atributo, deduzidas do tipo; o texto que tem uma foto pintada POR CIMA vira
"atrás" sozinho, porque a prova lê a ordem real de pintura do navegador):

`0 fundo · 1 textura · 2 atrás · 3 sujeito · 4 frente · 5 tarjas · 6 texto/logo · 7 acabamento`

| Id | Checa | Limite | Por quê |
|---|---|---|---|
| C1 | contraste REAL: peça com × sem texto; nos pixels da letra, texto × o que está embaixo | percentil 5 ≥ 4,5:1 (texto grande ≥ 72 px de corpo, ou ≥ 56 em negrito: 3:1) | a média esconde o pior trecho (grão, foto, luz) |
| C2 | tangente: bordas que quase se tocam (elemento × elemento, × silhueta da pessoa, pessoa × borda) | 0 < distância < 0,5 U (U = 2,2% do lado menor ≈ 24 px) | ou sobrepõe de propósito ou respira |
| C3 | rosto coberto por algo NA FRENTE da pessoa | 0% (detector YuNet) | rosto é o primeiro ponto de leitura |
| C7 | olhos e boca (pontos do YuNet) fora da área de TEXTO; cabeça (+10%) fora da área de HERÓI ou sob a coluna | 0 | rosto é núcleo do herói |
| C8 | herói (extensão PINTADA, inclusive filho que sangra) fora da área de herói ou sob a coluna | 0 | herói gráfico conta igual a texto |
| C4 | palavra ATRÁS da pessoa | palavra ≤ 30% · letra ≤ 50% · 1ª letra ≤ 15% | a palavra tem que continuar lida |
| C5 | ritmo: espaços entre vizinhos quase iguais | 0,5 < Δ ≤ 3 px = erro | igual ou claramente diferente |
| C6 | herói (`data-heroi="1"`) com o maior destaque | 1º no mapa de destaque | senão a hierarquia está errada |

Relatório (sem aviso): ordem de leitura estimada, equilíbrio (centro de massa do destaque), partilha
escuro/médio/claro (notan), espaços em U.

## Zonas seguras e tamanhos
| Formato | Área para texto/logo |
|---|---|
| 9:16 (Stories + Reels: a MESMA arte; padrão = anúncio) | **texto, logo e núcleo do herói (olhos e boca): x 108–972 · y 240–1248, e para y ≥ 936, x ≤ 852.** Topo 240 = fim medido da barra do Reels (210) + 30 de respiro (a linha oficial de 269 sobrava 59 px). A coluna de ícones do Reels começa em x 889 e y 974 (medido); o "dente" oficial é 853; o respiro é 36 px; o zoom do Reels corta 43–98 px de cada lado. **Corpo do herói** (tarja principal, cabeça inteira): x 72–1008 · y 216–1440, e para y ≥ 940, x ≤ 864. Fundo e decoração sangram (sob a interface: pouco detalhe, tom médio-escuro) |
| Reels com aviso/rótulo | base 40% → y ≤ 1152 |
| Capa de Reels | texto em y 420–1500 (e x ≤ 852 para y ≥ 936) |
| Feed 4:5 (1080×1350) | **texto x 80–1000 · y 80–1140.** Os cantos de baixo têm o ícone de marcação/repost (x 49–164, y 1178–1294) e o de som, e as nossas peças alinham à esquerda. Carrossel: nada em x > 888 com y < 156 (contador 1/N) |
| Post 1:1 | **texto x 80–1000 · y 80–870** (mesmos cantos); 1:1 que vai para a grade do perfil: x 171–909 |
| Núcleo universal (só se a arte puder ir para outro posicionamento) | 9:16 x 108–972 · y 485–1248; 4:5 y 200–963; 1:1 y 65–828. Preferir DESLIGAR a "mídia flexível" e entregar as 4 proporções |
| 1,91:1 (coluna da direita/pesquisa) | logo + ≤ 6 palavras ≥ 72 px; nada de texto pequeno |
| Capa de Reels | título em y 420–1500 (única faixa visível no Reels, no feed, na grade e no 1:1) |
| WhatsApp foto do grupo | círculo; essencial a ≤ 0,35 × lado do centro (640×640) |
| WhatsApp Status | mesma zona do 9:16 (sem número oficial) |
| Imagem no chat | 1:1 ou 4:5; essencial no quadrado central |
| Live 1920×1080 | título seguro x 96–1824 · y 54–1026; ação x 67–1853 · y 38–1042 |
| Live vista no celular | preço/CTA/link com maiúscula ≥ 43 px (≥ 61 px de corpo) |
| Lower third | ≤ 240 px de altura; nome ≥ 4% da altura; ≥ 4 s na tela |
| Página (celular 360×800 e 1366×768) | título + sub + botão até y ≈ 600 CSS; corpo e campos ≥ 16 px; botão ≥ 48×48; linha 45–75 caracteres |
| Checkout | sem medida pública; 2000×590 (desktop) / 800×800 (celular); essencial nos 80% centrais; ≤ 300 KB; **confirmar no painel** |

- **Contraste:** WCAG 4,5:1 (3:1 para texto ≥ 72 px de corpo, ou 56 px em negrito, num 1080; meta de 7:1 no texto
  pequeno, por causa do sol). APCA Lc ≥ 75 no corpo, ≥ 45 nos títulos.
- **Quanto texto [proposta]:** título ≤ 7 palavras; feed ≤ 20; Story ≤ 25; capa ≤ 5.
- **Escala de espaço :** 12 · 24 · 36 · 48 · 72 · 96 · 144 · 192 (grade 4/8 do Material).
- **Anúncio:** uma frase de ação, escrita como TEXTO (nunca botão desenhado, ▶, ✕, sino ou ☐); exportar em 1440 de
  largura. Desligar no Gerenciador: sobreposições, retoques, expandir imagem, reescrita de texto e mídia flexível
  (se entregar as 4 proporções), e "testar novos recursos" no nível da conta.

## Regras de craft que o olho confere (o motor não pega tudo)
- **Uma entrada:** desfoque a peça (olho semicerrado); o foco certo continua aparecendo?
- **Salto de escala** ≥ 4:1 (social); ≤ 3 tamanhos.
- **Margem óptica:** aspas e pontuação penduradas; A/V/T diagonais levemente para fora.
- **Proporção de cor** perto de 60-30-10; a hierarquia funciona em cinza.
- **Série:** folha de contato; vizinhas com arquétipos e movimentos diferentes; nenhum par com CLIP > 0,92.
- **Miniatura:** olhe a 25% (feed). A ideia ainda bate?
- **Mesmo mundo:** foto e gráfico com o mesmo tratamento (P&B, grão, contraste).

## Lote (elementos, variações, séries)
Revisar UM A UM: cada item grande (~760 px) + miniatura no fundo oposto; efeito que imita erro é defeito; na dúvida,
remover. Critérios D1–D44: `scripts/ornamentos/_revisao/CRITERIOS.md`; ferramenta:
`python -m ornamentos.catalogo --revisao`. Desconfie da miniatura: antes de "corrigir" algo que parece torto, meça.

## Lei (Brasil — leitura de designer, não é parecer jurídico)
- Permitido: esconder o preço até um evento, como teaser (CONAR art. 9º §2º).
- Proibido: preço "de" falso; "até X%" que não existe; contagem ou vagas falsas; preço no checkout diferente do
  anunciado (CDC arts. 30, 31, 35 e 37). WhatsApp só com opt-in.
- Risco legal na copy do cliente: avisar UMA vez, por escrito, com a fonte; registrar a decisão; não reescrever a copy.
