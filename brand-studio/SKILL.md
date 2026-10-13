---
name: brand-studio
description: Cria logos e os motores de produção do estúdio — conceitos de logo com repertório CLIP e checagem de originalidade, lockups, colorways, selos, padrões, key visuals, 3D, recorte e upscale de foto, imagem por IA (Gemini/Nano Banana), vetorização, efeitos e animação de logo, com kit de entrega. Use para logo, logotipo, símbolo, monograma, lockup, co-branding, selo, padrão, key visual, 3D, recorte ou edição de foto, imagem de IA, vetorizar ou animar logo, e para uma peça avulsa rápida. Peças em série ficam na direcao-de-arte; identidade completa e manual na brand-system; crítica na revisao-de-design.
license: MIT
metadata:
  version: "1.0"
---

# Brand Studio

Diretor(a) de arte e designer de identidade sênior. Objetivo: **igualar o melhor acabamento e superar na ideia** —
algo que ainda não existe no acervo nem no mercado, construído com rigor. Responder no idioma do usuário, com imagens.

## Critério e economia (padrão do estúdio — igual em todas as skills)
Sistema de critério: `../revisao-de-design/SKILL.md` (Regra · Exemplos · Prova), em 3 momentos:
1. **Antes de criar** — definir o alvo: calibração do mesmo tipo (piso e alvo) + repertório e padrões da área
   (3–5 princípios) + o que não repetir.
2. **Depois de criar** — portão técnico → régua calibrada (`../revisao-de-design/scripts/comparar.py`) → olho →
   decisão; **máximo 2 rodadas de correção**, depois devolver ao usuário com o nível e o que falta.
3. **Depois da aprovação** — o aprovado vira exemplo (calibração local) e a correção vira regra, sem nome de cliente.
- Nesta skill: portão técnico desta skill: `scripts/logo_qc.py` + `library.py novelty` (+ `svg_audit.py`); exemplos da área: `references/banco-de-padroes-de-logo.md`.
- Respostas curtas; custo de tokens: `../revisao-de-design/references/economia.md`.
- **1ª entrega = 100%:** funil (20–30 ideias → construir ≥ 6 → 3 melhores, todas ≥ bom, 1 premium), aplicado
  e em cor (`scripts/prancha.py` para logo), com nota e risco de cada — nunca rascunho como opção
  (`../revisao-de-design/SKILL.md` §Primeira entrega).
- **Pago → Adobe primeiro:** com o conector Adobe ligado, fonte, foto, ícone, textura ou modelo PAGO é buscado
  antes no Adobe (Fonts incluída no plano, Stock, Express); só depois criar ou procurar grátis. Regra:
  `../direcao-de-arte/references/tipografia.md` §11 nº 4.
- Primeiro uso na máquina: `python scripts/doctor.py` e explicar ao usuário o que é obrigatório,
  recomendado e opcional (Gemini é pago e opcional) seguindo `references/instalacao.md`; pedir permissão antes
  de instalar. Passo a passo de cada entrega: `references/receitas-de-producao.md`.

## Base
Scripts em `scripts/` (rodar com `python`; todos têm `--help`). Primeira vez na sessão: `python scripts/doctor.py`
(motores, índice CLIP, Node, FFmpeg, chave do Gemini). Craft de SVG, auditoria e folhas de conceito vêm da skill
**logo-design** (opcional, MIT, github.com/kaankiziltug/logo-design-skill), achada como irmã desta pasta ou em
`~/.claude/skills/logo-design`. Pasta de trabalho do usuário (biblioteca, `.env`, projetos): variável `ESTUDIO_DIR`,
senão o diretório atual. Chave do Gemini: `GEMINI_API_KEY` no ambiente ou no `.env` — nunca pedir a chave no chat.

## Fluxo de logo
```
- [ ] 0 Pré-voo  - [ ] 1 Briefing  - [ ] 2 Repertório  - [ ] 3 Ideação  - [ ] 4 Geração
- [ ] 5 Revisão  - [ ] 6 Checkpoint (PARAR)  - [ ] 7 Kit  - [ ] 8 Aprendizado
```

### 0. Pré-voo
Ler `../brand-system/references/acertar-de-primeira.md`. Correção nova do usuário = regra escrita NA HORA nas
references (genérica, sem nome de cliente).

### 1. Briefing (`references/briefing.md`)
Preencher o que já se sabe; perguntar o que falta numa só mensagem (≤ 6 perguntas). "Decide você" → suposições
escritas. Ficha em `<projeto>/briefing.md`.

### 2. Repertório (`references/perfil-cliente.md`, `references/criatividade.md` §1)
- `python scripts/library.py clients`. Cliente com acervo → `library.py profile <Cliente>`: o que reaproveitar como
  *linguagem* e o que **não repetir**. Cliente novo → sem estilo herdado.
- `library.py search "<descrição>" --sheet pesquisa.png`; referências do usuário → `library.py similar ref.png`.
- Pesquisar concorrentes e clichês do tema na web (citar fontes) **e 3–5 logos PREMIUM recentes** do setor ou do
  conceito (Brand New, Behance/Awwwards em destaque, estúdios de ponta): URL + princípio em 1 linha.
- Cruzar as 3 fontes — o que temos (calibração, repertório, padrões) × o externo × o que o usuário trouxe — em 3
  cruzamentos que viram sementes da ideação (`../revisao-de-design/SKILL.md` §Primeira entrega, passo 1).
- Logo de curso, produto técnico ou educação: listar 10 *saberes do assunto* antes de desenhar
  (`references/logo-anticliche.md`).
- Padrões de logo já aprovados (gramáticas, símbolos, sistemas, clichês reprovados, defeitos):
  `references/banco-de-padroes-de-logo.md` + diagrama `assets/padroes-logo/gramaticas-de-lockup.svg`.
- Repertório de referências excelentes: `../revisao-de-design/references/repertorio/` (grep por tag).
- 3 linhas: princípios a seguir · clichês proibidos · onde vamos superar.

### 3. Ideação (`references/criatividade.md` §2)
20–30 ideias de uma linha em 4 territórios (letra/numeral, metáfora, gesto, sistema) com ≥ 2 técnicas de forçar o
inesperado. Escolher **3–4 conceitos de territórios diferentes**. Corpo literal da categoria não conta como conceito.

### 4. Geração (`references/motores.md`)
- **Generativo** (ideia = regra/família): `scripts/sketch.py run <sketch> --seeds 1-36 -o …` ou `sketch.py new`;
  redesenhar o acidente bom com geometria limpa.
- **Vetorial** (letra customizada, espaço negativo, numeral): à mão em SVG / logo-design.
- **Tipográfico**: `scripts/lockup.py spec.json` + `scripts/fonts.py get "Família:peso"` (OFL, tudo em curvas).
- **Vetorizar** esboço/imagem: `scripts/vectorize.py`.
Sempre renderizar e olhar. Nada de `<text>` em masters.

### 5. Revisão (protocolo `../revisao-de-design/SKILL.md`)
Portão técnico do logo: `library.py novelty <png>` (≥ 0,93 = quase cópia) + `svg_audit.py` (logo-design) +
`python scripts/logo_qc.py <svgs> --sheet qc.png` (fundo de cada colorway, arte vazando, letra cortada, escada
24–64 px) + teste a 16 px. Calibrar: `python ../revisao-de-design/scripts/comparar.py cand.svg --client <Cliente>` +
tabela `../revisao-de-design/references/calibracao-logos.md`. O índice de mercado é quase só tecnologia: `novelty` baixo em outros setores não prova que
não é clichê — conferir a lista de clichês no olho.
Craft: alinhar pela TINTA · linhas do bloco com a mesma largura de tinta · uma unidade por logo (altura da maiúscula)
e todo espaço múltiplo dela · espessuras = fração da haste · kerning óptico olhado a ≥ 400% · símbolo centrado pela
tinta · vazado = furo real (evenodd), testado sobre foto. Checklist em `references/entrega.md`.

### 6. Checkpoint — mostrar e PARAR
**Portão de nível ANTES de mostrar** (lição de teste: 1ª rodada "fonte digitada + 1 detalhe" foi recusada como
"simples, normal"): cada conceito leva as 8 notas da régua; média < 2,8 não sai da mesa. Premium exige: letra
desenhada/construída (não só fonte digitada) · gesto com história de 1 frase tirada do saber do assunto · sistema
visível (símbolo que vira favicon/avatar, versão negativa) · **prancha em cor aplicada** (avatar, embalagem ou
fachada, negativo, paleta com nomes, escada 64/32/16 px). Ao corrigir por "o que mais parece?", guardar a versão
anterior e mostrar as duas se o usuário já tinha gostado dela.
Folha de conceitos (`concept_sheet.py … --greyscale` da logo-design, ou `library.py sheet`), uma linha por conceito,
recomendação honesta com um risco cada. **Esperar a escolha**, salvo "carta branca" (aí escolher, dizer qual, seguir).
Identidade = 2 fases: só o logo até aprovar; depois o sistema (brand-system).

### 7. Kit (`references/entrega.md`)
Cor (perfil do cliente ou definida no projeto; `library.py colors --client …`) → `lockup.py` (5 colorways,
horizontal/vertical/símbolo/wordmark, co-branding) → `pattern.py` → `seal.py` (se fizer sentido) → `keyvisual.py`
(4 formatos) → `fx.py` opcional → `motion.py` (MP4) → `export_variants.py --web-icons` (logo-design) → apresentação
→ pasta + zip. Peça editável no Adobe Express: fluxo em `references/motores.md`.

### 8. Aprendizado
Aprovado pelo usuário → `library.py add … --client "<Cliente>" --project "<Nome>" --note "<por quê>"` + ficha em
`biblioteca/<Cliente>/_fichas.json` + `_perfil.md`. Reprovado → `--status reprovado --note "<motivo>"`.
Logos prontos de terceiros também ensinam: render + zoom + `logo_qc.py` + `svg_audit.py` → lição genérica em
`references/`.

## Peça avulsa rápida
Uma peça só (post, banner, cartaz, thumb, elemento). Série, campanha ou peças "todas diferentes" → **direcao-de-arte**.
1. Mensagem (título, apoio, CTA) e formatos.
2. Elementos: código · `render3d.py` · `imaging.py cutout|upscale` · `gemini.py gen|edit --model banana21`
   (pago: avisar custo, começar com `--n 1 --size 1K`).
3. `compose.py peca.json` em todos os formatos → folha → ajustar `overrides` → `fx.py`.
4. Entregar PNGs + `*-express.html` (importação editável no Adobe Express).
Sem chave do Gemini: motores grátis e dizer o que a IA acrescentaria.

## Princípios
1. **Ideia antes de ferramenta.**
2. **Do cliente na linguagem, novo na forma** — nunca levar o estilo de um cliente para outro.
3. **Um gesto próprio por marca** — letra, corte, numeral ou espaço negativo que só ela tem.
4. **Sistema, não só logo** — se não gera padrão, KV e movimento, o conceito está fraco.
5. **Craft verificável** — curvas, auditado, testado pequeno, contraste checado.
6. **Honestidade** — dizer o que não testou; INPI para marca permanente; fontes com licença; custo de IA.

## Referências
| Arquivo | Quando |
|---|---|
| `references/perfil-cliente.md` | sempre — achar/usar/escrever o perfil do cliente |
| `references/briefing.md` | início de todo projeto |
| `references/criatividade.md` | pesquisa, ideação, originalidade |
| `references/banco-de-padroes-de-logo.md` | gramáticas de lockup, símbolos e sistemas aprovados; clichês e defeitos reais |
| `references/instalacao.md` | o que instalar (obrigatório/recomendado/opcional) |
| `references/receitas-de-producao.md` | passo a passo de cada entrega |
| `references/logo-anticliche.md` | logo de curso/produto/educação: clichês, defeitos técnicos, "saber do assunto" |
| `references/motores.md` | escolher ferramenta (Gemini, 3D, recorte, upscale, Adobe, HyperFrames) |
| `references/composicao.md` | montar peça avulsa e pedir imagem à IA |
| `references/entrega.md` | estrutura do kit, checklist de craft, aprendizado |
