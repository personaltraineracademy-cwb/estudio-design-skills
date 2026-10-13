# Método de composição em camadas (nível Photoshop/Illustrator, ou acima)

Regra: composições avançadas com várias camadas, no nível de um designer sênior no Photoshop/Illustrator ou acima,
e planejadas antes de montar (para evitar retrabalho).

Base: planos, oclusão, tangentes, peso, notan, métricas, restrições e provas; compositing, efeitos, vetor, fundos e
marcas de amador; zonas, leitura e interface nativa.

Princípio: **a peça é uma RECEITA de camadas** (como um PSD com objetos inteligentes), não um desenho achatado. Cada
camada tem função, regra e checagem. O código ganha do trabalho manual em quatro pontos: reprodução idêntica em todos os
formatos, alinhamento medido na tinta, QA que não esquece e série consistente (mesmo grão, mesmo preto, mesma luz).

---

## 1. Ordem do trabalho (14 passos; nenhum pula)

**Planejar**
1. **Ideia em 1 frase** + arquétipo/movimento. Decidir qual palavra PODE ser coberta (só a conhecida: nome, marca).
2. **Restrições fechadas:** pesquisas que definem zona, tamanho e interface TERMINADAS antes de montar.
3. **Miniaturas de valor:** 3–6 estruturas em notan de 3 tons; escolher a que lê a 25%.
4. **Ficha + pré-voo** (`plano.py`):
   - formato e área útil (com respiro da interface);
   - grade;
   - pilha L0–L8;
   - hierarquia (herói = nível 1);
   - cada texto medido na coluna, com contraste previsto;
   - `tensao` declarada se o desequilíbrio for de propósito.

   **Pré-voo zerado.**

**Montar**

5. **Foto dirigida pelo layout:** pose, direção da luz, espaço do título. Recorte por matting (§3.1).
6. **Block-in:** L0 + L4 + títulos em manchas. Olhar notan, peso e herói ANTES de qualquer textura.
7. **Oclusão:** só nas letras declaradas; medir por palavra e por letra (§4).
8. **Integração:** preto, cor, luz, borda, sombra, grão (§3).
9. **Unificação (L6):** mapa de gradiente/grade + UM grão sobre L0–L5.
10. **Texto final (L7–L8):** nítido, sem efeito, contraste no pior pixel.

**Provar**

11. **Verificador do palco + prova de camadas** (`camadas.py`) até ZERO aviso. Aviso aceito = escrito, com o porquê.
12. **Folha de prova olhada de verdade** (§6, checagens do olho O1–O12).
13. **Inspeção a 100% e 25%** + medida de pixel nas bordas críticas.
14. **Série:** folha de contato; vizinhas com arquétipos diferentes; anotar no diário o que achou e corrigiu, e por que o
    plano não previu.

## 2. A pilha (L0–L8), cada camada com uma função

| # | Camada | Exemplos | Regra |
|---|---|---|---|
| L0 | Fundo | cor, degradê, foto de cenário | sangra; nada de texto; degradê em float + dither TPDF (sem degraus) |
| L1 | Textura do fundo | papel, meio-tom, padrão | ≤ 12% de contraste; só no fundo |
| L2 | Tipo "cenário" | palavra gigante atrás da pessoa | pode ser coberta (§4) |
| L3 | Elementos atrás | moldura, visor, faixas, painel | não tangenciar a pessoa (folga ≥ 16 px ou sobreposição ≥ 16 px) |
| L4 | Pessoa (recorte) | P&B da campanha | rosto e mãos nunca cobertos; rosto fora da interface do app |
| L5 | Elementos na frente | faixa que cruza, partículas | ≤ 1 elemento "costurando" por peça |
| L6 | Unificação | mapa de gradiente, grão único, vinheta | vale para L0–L5 JUNTOS; nunca sobre o texto |
| L7 | Texto de leitura + logo + CTA | título, oferta, data | nítido, sem filtro, por cima de tudo |
| L8 | Legal / interface | letra miúda | zona segura do formato |

**Teto:**
- 3 planos de profundidade + 1 de unificação;
- ≤ 2 texturas;
- ≤ 1 elemento costurando;
- ≤ 3 pessoas;
- ≤ 7 elementos distintos.

Camadas de IDEIA, sim; camadas de textura, poucas (Pieters 2010).

**Armadilha do CSS:**
- `opacity < 1`, `transform`, `filter`, `mix-blend-mode`, `mask` e `isolation` criam um contexto de empilhamento novo.
- Por isso cada camada é irmã direta do `#peca`.
- Nunca pôr efeito num contêiner que tenha camadas de níveis diferentes.

## 3. Integração da pessoa (o que separa amador de sênior)

**3.1 Recorte por matting:**
- O alfa do rembg avança 1–2 px sobre o fundo antigo, e colar dá linha escura.
- Corroer esconde a linha, mas perde fio de cabelo. Só limpar a cor também não basta: alfa errado não tem cor certa.
- Receita:
  1. trimap a partir do alfa (certeza > 0,98 / < 0,02, corroída 2×7 px);
  2. `pymatting.estimate_alpha_cf`;
  3. `estimate_foreground_ml`;
  4. P&B.
- Conferir no olho a 400% sobre azul E papel: orelha, cabelo, ombro.

**3.2 Pretos e cor:**
- Os pretos da pessoa casam com os pretos da cena (o preto da cena raramente é 0).
- Em fundo colorido, aplicar **mapa de gradiente** (`efeitos.mapa_gradiente`, SVG em `sRGB`): escuro da cena → meio
  neutro-frio → claro.
- Na cena realista, `efeitos.casa_cor`: L por pontos preto e branco, a/b por Reinhard parcial na vizinhança.
- Pessoa em cena, limites de Xue 2012: luz ≤ 1,4 stop, temperatura ≤ 30 mired, saturação ≤ 0,45 stop.

**3.3 Luz:**
- Uma direção só. A luz de contorno (`efeitos.luz_de_borda`) só do lado da luz e fina (≤ 0,5% da altura da pessoa).
- **Light wrap** (`efeitos.light_wrap`) quando o fundo é claro ou colorido: a luz de trás contorna a silhueta.

**3.4 Sombra:**
- Contato onde a pessoa toca algo.
- Sombra projetada: cor = fundo escurecido (nunca preto puro), desfoque que CRESCE com a distância, 2 camadas
  (~50% / ~30%).
- Sombra pela silhueta: `efeitos.sombra_css`.

**3.5 Grão único:**
- Um grão da campanha (σ fixo, o mesmo em toda a série), aplicado UMA vez por cima de L0–L5 (`efeitos.grao_url`,
  overlay).
- Medir o σ pessoa × fundo em áreas lisas: razão 0,8–1,25.
- Grão só no fundo, ou só na foto, é marca de amador.

**3.6 Nitidez de saída:** só no L, só na foto, no tamanho final; uma reamostragem por foto.

## 4. Oclusão (texto × pessoa)
- **Palavra coberta:** só palavra conhecida. Tinta coberta ≤ 30%; nenhuma letra > 50%; 1ª letra ≤ 15% coberta
  (unificado com `qualidade.md` C4 e `composicoes.md`: vale o mais rígido de cada).
- **Cobrir pela BASE** das letras: o topo carrega a leitura (Javal, Fiset, Perea).
- **Intocáveis, 0% cobertos:** data, hora, preço, CTA, link, letra miúda (`data-ler="1"`).
- **Elemento que passa pelas letras:** 1 por peça. A troca frente/atrás acontece DENTRO de uma letra, nunca no espaço
  entre letras, onde vira tangente.
- **No HTML:** a palavra fica numa camada abaixo da foto. A prova lê a ordem real de pintura (`elementsFromPoint`) e mede
  a cobertura por letra.

## 5. Efeitos, elementos e fundos

**Efeitos:**
- Todo efeito = parâmetro + máscara.
- Rosto, olhos e caixa do texto ficam FORA, salvo quando o efeito é a ideia.
- Cada receita leva ferramenta, parâmetro, armadilha e checagem (tabela final).
- **Light leak:** screen ~50%, vindo da luz.
- **Halação:** em linear, laranja perto e vermelho longe, só no escuro.
- **Bloom:** mistura 0,03–0,15.
- **Aberração cromática:** 0,5–1,5 px no canto e zero no centro.
- **Duotone:** filtro SVG `sRGB`.
- **Meio-tom:** gerar no tamanho final.
- **Tipo deslocado:** `feDisplacementMap` em `sRGB`.

**Elementos (Illustrator → código):**
- booleanas e offsets: `skia-pathops`;
- cantos: raio ≤ ½ da menor aresta, igual na família;
- repetição: 360/n exato;
- compensação de traço: horizontais 2–5% mais finas;
- nós nos extremos, nada "quase" (`svg_audit.py`).

**Fundos:**
- **Orçamento de contraste:** atrás do texto, fundo calmo (C_RMS ≤ 0,10 texto pequeno, ≤ 0,20 título; Scharff).
- Acentos máximos do fundo fora da zona de leitura.
- Degradê em OKLab, float, dither TPDF.
- Poça de luz do mesmo lado da luz da pessoa.

## 6. Provas (o olho sênior) e checagens

**Folha de prova** (`camadas.provar`):
- montagem camada a camada;
- final, notan, olhos apertados, mapa de destaque, espelho;
- grade + zonas + caixas de tinta + rostos.

**Automáticas:**

| Id | O quê | Limite |
|---|---|---|
| C1 | contraste no pior trecho (textless, percentil 5) | ≥ 4,5:1 (3:1 texto grande: ≥ 72 px de corpo, ou ≥ 56 em negrito) |
| C1b | fundo calmo sob o texto (C_RMS, Scharff) | ≤ 0,10 pequeno · ≤ 0,20 título |
| C2 | tangente: elemento × elemento × pessoa × borda; sobreposição tímida | 0 < folga < 16 px (1,5% do lado menor) = erro |
| C3 | rosto (YuNet, +10%) coberto por algo NA FRENTE | 0% |
| C4 | palavra atrás da pessoa | 30% / 50% / 1ª letra ≤ 15% coberta · base > topo · intocáveis 0% |
| C5 | ritmo: espaços quase iguais | 0,5 < Δ ≤ 3 px = erro |
| C6 | herói = maior peso visual no "olho apertado" | 1º |
| C7 | rosto sob a interface do app | 0% |
| C8 | herói (mesmo decorativo/sangrando) sob a interface | 0% |
| C9 | halo do recorte | só relatório (confunde luz de contorno); olho a 400% |
| C10 | grão pessoa × fundo (σ Immerkær, áreas lisas) | razão 0,8–1,25 |
| C11 | pretos e dominante das sombras pessoa × vizinhança | relatório; usar mapa de gradiente |
| C12 | banding (degraus por mil px) | relatório; conferir também no JPEG exportado |
| C13 | notan: valor dominante | ≥ 45% da área |
| C14 | equilíbrio DCM (Hübner & Fillinger) | ≤ 25% ou `tensao` declarada com o porquê |

**Do olho, antes de mostrar:**

| Id | Olhar | Passa quando |
|---|---|---|
| O1 | montagem | cada camada que entra melhora a peça; tirar qualquer uma piora |
| O2 | desfoque + 25% | a mancha dominante é o herói |
| O3 | cinza | a hierarquia sobrevive sem cor |
| O4 | espelho | nada pende |
| O5 | profundidade | frente, meio e fundo óbvios |
| O6 | oclusão | lê de primeira; o pedaço coberto não forma outra palavra |
| O7 | luz | uma luz só |
| O8 | borda a 400% | sem franja |
| O9 | corte | sem membro amputado; olhar para a mensagem |
| O10 | tangentes | nenhuma |
| O11 | mundo | o mesmo para foto e gráfico |
| O12 | camada | dá para apagar uma? Então apagar |

## 7. Ferramentas
| Arquivo | Papel |
|---|---|
| `scripts/plano.py` | ficha + pré-voo, ANTES de montar |
| `scripts/palco.py` | montagem HTML/CSS no Chrome + verificador geométrico |
| `scripts/efeitos.py` | grão único, mapa de gradiente, light wrap, luz de borda, sombra, casar cor, medidas (σ, halo, banding, luz), dither TPDF |
| `scripts/camadas.py` | prova de camadas C1–C14 + folha |
| Conector Adobe | seleção por prompt, lens blur, expandir com `seeds`, ajustes de Camera Raw (conferir pela nossa medição) |
| Gemini | placas fotográficas (fumaça, céu, estúdio, textura sobre preto); reiluminar só com conferência de rosto |

## 8. O que ainda perdemos e como compensar
Máscara de cabelo muito difícil, retoque fino de pele, reiluminação generativa (Harmonize) e liquify com julgamento:
o conector ou o Gemini geram, **a nossa medição aprova**. Se não passar, refazer ou declarar.
