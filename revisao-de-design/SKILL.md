---
name: revisao-de-design
description: Sistema de critério do estúdio — define o que é bom (régua de 8 critérios, gosto), mostra exemplos calibrados (logos, peças, páginas reais com nota) e repertório de referências, e prova cada entrega (portão técnico, comparação com exemplos, segunda opinião, arena só para escolher, no máximo 2 rodadas de correção). Também define o modo econômico de tokens. Use para analisar, avaliar, criticar, dar nota, comparar ou aprovar qualquer logo, peça, elemento, página, site, manual ou imagem de IA; antes de criar (definir o alvo) e antes de mostrar qualquer resultado das skills brand-studio, brand-system, direcao-de-arte e criacao-de-sites.
license: MIT
metadata:
  version: "1.1"
---

# Revisão de design — o sistema de critério do estúdio

Todas as skills do estúdio usam ESTE sistema, do mesmo jeito. Ele tem 3 camadas e é aplicado em 3 momentos.
Diagrama: `assets/arquitetura-do-criterio.svg` · ciclo: `assets/ciclo-de-revisao.svg`.

## Modo econômico (vale para tudo)
Respostas curtas (caveman, se o plugin estiver ativo; código e documentos normais). Regras:
[references/economia.md](references/economia.md). As 4 que mais pesam: padrão antes de montar · script mede antes do
olho · uma folha pequena por rodada · subagente só curto e independente.
- Primeiro uso na máquina: `python ../brand-studio/scripts/doctor.py` e explicar ao usuário o que é obrigatório,
  recomendado e opcional (Gemini é pago e opcional) seguindo `../brand-studio/references/instalacao.md`; pedir
  permissão antes de instalar. Passo a passo de cada entrega: `../brand-studio/references/receitas-de-producao.md`.

## As 3 camadas
| Camada | Pergunta | Onde |
|---|---|---|
| **1. Regra** | o que é bom, em palavras? | [regua.md](references/regua.md) (8 critérios 0–4, níveis) · [gosto.md](references/gosto.md) (princípios aprovados/reprovados) |
| **2. Exemplos** | como é o bom, em casos reais? | **calibração** = trabalhos aprovados com nota: [calibracao-logos.md](references/calibracao-logos.md) e `references/calibracao-pecas-e-paginas.md` · **repertório** = referências públicas excelentes: [repertorio/LEIAME.md](references/repertorio/LEIAME.md) · **padrões** por área: `../brand-studio/references/banco-de-padroes-de-logo.md`, `../direcao-de-arte/references/composicoes.md`, `../criacao-de-sites/references/receitas-de-dobra.md` |
| **3. Prova** | isto está bom mesmo? | portão técnico (scripts por tipo, abaixo) · `scripts/comparar.py` (candidato × exemplos calibrados) · `../direcao-de-arte/scripts/julgar.py` (2ª opinião) · [arena.md](references/arena.md) (só para escolher) · limite de 2 rodadas |

Níveis em todo o sistema: **ruim** · **normal = aprovado (piso)** · **bom** · **premium (alvo)**. Só bom ou
premium é mostrado como entrega do estúdio.

## Primeira entrega = 100% (regra-mãe)
O usuário julga o estúdio pela PRIMEIRA coisa que vê; rascunho nunca é mostrado como opção. Vale para logo, peça,
página, elemento e identidade. Antes de QUALQUER checkpoint:
```
- [ ] 1 Pesquisa curta de 3 fontes (≤ 3 buscas, ~10 min), gravada em `<projeto>/pesquisa.md`:
      INTERNA (calibração + repertório + padrões da área) · EXTERNA (3–5 exemplos PREMIUM recentes do mesmo tipo ou
      conceito — Brand New, Behance/Awwwards em destaque, It's Nice That, Type Directors Club, estúdios de ponta —
      cada um: URL + princípio em 1 linha; nunca copiar a forma) · DO USUÁRIO (briefing, referências que mandou,
      materiais, perfil do cliente). Fechar com 3 CRUZAMENTOS "princípio interno × achado externo × dado do usuário"
      → viram sementes da ideação. Achado externo premium e transferível → entrada no repertório (formato do LEIAME).
- [ ] 1b Alvo escrito: piso e alvo da calibração do mesmo tipo + 3–5 princípios escolhidos + o que não repetir
- [ ] 2 Funil: 20–30 ideias de 1 linha → CONSTRUIR ≥ 6 (desenho próprio: letra construída, gesto, sistema — não só
      fonte digitada ou template) → revisão interna de cada (portão + 8 notas + "o que mais isto parece?")
- [ ] 3 Mostrar só as 3 melhores, todas ≥ bom e ao menos 1 premium (Id/Df/Fu = 4), de territórios diferentes
- [ ] 4 Mostrar APLICADO e em cor (logo: `../brand-studio/scripts/prancha.py`; peça: no formato real; página: nas
      larguras reais), com nota, história de 1 frase e 1 risco honesto cada
- [ ] 5 Nenhuma chegou a bom depois de 2 rodadas internas → dizer isso e mostrar a melhor com o que falta; nunca
      apresentar "normal" como opção
```
Economia corta repetição e leitura inútil — **nunca** o esforço da primeira entrega. Rodadas internas do funil não
contam no limite de 2 rodadas (que vale para correções DEPOIS de mostrar).

## Exemplo é régua, não molde
Calibração, repertório e padrões dizem o NÍVEL (piso e alvo) e o que JÁ EXISTE — nunca a forma da próxima criação.
Trabalho novo = nota igual ou acima E gesto diferente. Repetir a forma de um exemplo bem notado derruba Diferença.
Cada criação traz ao menos 1 gesto que não está em nenhum exemplo; padrão pode ser combinado ou quebrado de propósito.
| Usar | Quando | Para quê |
|---|---|---|
| Régua + gosto | sempre | dar nota e decidir |
| Padrões + repertório | ideação | extrair princípios para combinar, torcer ou romper (nunca copiar a forma) |
| Calibração | antes de dar nota | acertar o número e saber piso/alvo; não é ponto de partida da ideia |
| `comparar.py` | depois de criar | semelhança (≥ 0,93 refazer · 0,88–0,93 olhar) e nível dos vizinhos |
| Arena | 2+ opções reais | escolher, só isso |

## Os 3 momentos
### 1. Antes de criar — definir o alvo (5 min)
```
- [ ] Ler as linhas da calibração do mesmo tipo (logo, peça, página): qual é o PISO e qual é o ALVO
- [ ] grep no repertório e nos padrões da área por tag/assunto → 3–5 princípios
- [ ] Escrever: alvo (nível + 1 frase) · princípios escolhidos · o que NÃO repetir (exemplos, clichês)
```
### 2. Depois de criar — ciclo de revisão (A–D, máx. 2 rodadas)
```
Revisão · <peça> · rodada _/2
- [ ] A. Portão técnico (script) = 0 erros
- [ ] B. Régua: 8 notas 0–4, calibradas pelos exemplos + comparar.py
- [ ] C. Olho: 100% e 25%, testes rápidos
- [ ] D. Decisão: entregar · corrigir (se rodada < 2) · devolver ao usuário
```
### 3. Depois da aprovação — aprender (o sistema cresce)
- Aprovado pelo usuário → vira **exemplo**: linha na calibração local (`biblioteca/<Cliente>/_calibracao.md` ou
  `biblioteca/_calibracao-estudio.md`: `ID · caminho · nível`) e, se ensinar algo novo, 1 linha neutra no padrão ou no
  gosto (sem nome de cliente).
- Reprovado → 1 linha em "sinais de reprovação" (gosto.md) ou no anticlichê da área.
- Correção do usuário → regra escrita NA HORA no arquivo da camada certa (Regra, Exemplo ou Prova).

## A. Portão técnico (binário, automático)
Erro → corrigir e rodar de novo (até 3 execuções; não conta como rodada). Ainda com erro → D como "devolver".
| Entrega | Verificador |
|---|---|
| Logo / SVG | `../brand-studio/scripts/logo_qc.py` + `svg_audit.py` (logo-design, se instalada) + `../brand-studio/scripts/library.py novelty` |
| Peça (post, story, banner) | avisos do `../direcao-de-arte/scripts/palco.py` = 0 + `../direcao-de-arte/scripts/camadas.py` |
| Página / site | `../direcao-de-arte/scripts/check_pagina.py` + `../criacao-de-sites/scripts/varredura.py` |
| Cores | `../brand-system/scripts/palette.py check` |
| Manual | `../brand-system/scripts/manual.py build <dir> --qa-only` |
| Lote de elementos | `../direcao-de-arte/scripts/ornamentos/_revisao/CRITERIOS.md`, item por item |
Todo portão confere: nada quebrado/cortado/vazando; alinhamento na TINTA (quase alinhado 1–6 px = defeito); cores,
fontes e raios só da escala; zonas seguras; texto legível no tamanho mínimo.

## B. Régua calibrada
8 notas 0–4 (Ideia · Diferença · Leitura · Composição · Craft · Função · Coerência · Acabamento), âncoras em
[regua.md](references/regua.md). **Calibrar antes de dar nota:** achar na calibração a linha mais parecida
("está mais perto de qual exemplo?") e, com biblioteca local,
`python scripts/comparar.py candidato.png --client <Cliente> [--mercado 2]` → folha lado a lado com os exemplos
mais parecidos, nível e média de cada um. Régua mínima: igualar a melhor média vizinha e ser diferente dela;
semelhança ≥ 0,93 = quase cópia (refazer).
- **Ruim**: defeito de portão ou média < 2 · **Normal / aprovado (piso)**: média ≥ 2 · **Bom**: média ≥ 2,8 e
  nenhum < 2 · **Premium**: média ≥ 3,5, nenhum < 3, Ideia/Diferença/Função = 4. Nota 0–10 = média × 2,5.

## C. Olho
Uma folha de contato; 100% (detalhe) e 25% (miniatura). Testes de 1 minuto: troca de logo · 3 segundos · remover
elemento · diferença da peça anterior · "um leigo diria que quebrou?" · **"o que mais isto parece?"** (listar 5
leituras indesejadas: riscado/cancelado, placa de proibido, alvo, queijo, pata, cifrão, símbolo de app… — se uma
pega à primeira vista, mudar a forma). Na dúvida, remover. 2ª opinião opcional:
`../direcao-de-arte/scripts/julgar.py <img> --tipo …`.

## D. Decisão — LIMITE DE 2 RODADAS
`rodada 1: revisar → corrigir · rodada 2: revisar → corrigir · depois: revisar → PARAR`
- Bom/premium em qualquer ponto → entregar.
- Depois da 2ª correção, abaixo de bom → **devolver ao usuário**: nível, o que está fraco, se dá para melhorar e
  como. Nunca abrir rodada 3 sozinho. Novo pedido zera a contagem; vale para subagentes.
- Relatório de subagente é afirmação, não prova: quem entrega olha as imagens antes de dizer "pronto".

## Arena (só para ESCOLHER)
2+ opções reais e escolha não óbvia. Uma arena por decisão + no máximo um antes × depois.
[references/arena.md](references/arena.md).

## Formato do relatório (sempre este, curto)
```
Revisão · <peça> · rodada n/2
Alvo: <nível> (exemplo mais próximo: <ID>, média <x>)
Portão: 0 erros (<verificador>)
Régua: Id 3 · Df 3 · Le 4 · Co 3 · Cr 4 · Fu 3 · Ch 4 · Ac 3 = 3,4 → bom
Corrigido: <lista curta>
Fraco ainda: <lista curta ou "nada">
Decisão: entregar | rodada 2 | devolver
```

## Por que este formato
- Autocrítica rende quase tudo nas 1–2 primeiras voltas; depois gasta tokens e pode piorar (Self-Refine, Madaan et
  al., 2023).
- Juiz de IA tem viés de posição e de autopreferência: às cegas, AB/BA, juiz de outra família (Zheng et al., 2023).
- Nota absoluta com âncoras e exemplos escritos evita "coroar o melhor dos fracos" (Kim et al., 2023, Prometheus).
