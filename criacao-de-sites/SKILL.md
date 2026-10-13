---
name: criacao-de-sites
description: Cria sites e páginas de conversão premium (captura, vendas, evento, hotsite) para marcas que já têm identidade visual e logo — Next.js em exportação estática, Tailwind 4, GSAP sob demanda, hospedável na Vercel e na Hostinger (raiz, subpasta ou subdomínio). Parte de um template com o padrão de página do estúdio (espaçamento 12·24·40, dobra = tela inteira, movimento sempre ligado, pop-up acessível) e de receitas de dobra; aplica cores, fontes, raios, logo e a copy final; verifica com scripts (0 erros) e entrega 3 zips. Use para site, landing page, página de captura ou de vendas, hotsite, "colocar no ar". Identidade e tokens vêm da brand-system; crítica da revisao-de-design.
license: MIT
compatibility: Requer Node 20+, Python 3.11+, Chrome e playwright (pip) para os verificadores.
metadata:
  version: "1.0"
---

# Criação de Sites

Transforma **uma identidade visual pronta + uma copy final** numa página que converte, sem inventar nada fora do
sistema. Muda por cliente: cores, fontes, logo, elementos, composição da dobra, movimento. **Fixo**: o contrato de
página (espaçamento, dobra, responsividade, verificação). Responder simples e mostrar **imagens** (as 4 larguras).

## Critério e economia (padrão do estúdio — igual em todas as skills)
Sistema de critério: `../revisao-de-design/SKILL.md` (Regra · Exemplos · Prova), em 3 momentos:
1. **Antes de criar** — definir o alvo: calibração do mesmo tipo (piso e alvo) + repertório e padrões da área
   (3–5 princípios) + o que não repetir.
2. **Depois de criar** — portão técnico → régua calibrada (`../revisao-de-design/scripts/comparar.py`) → olho →
   decisão; **máximo 2 rodadas de correção**, depois devolver ao usuário com o nível e o que falta.
3. **Depois da aprovação** — o aprovado vira exemplo (calibração local) e a correção vira regra, sem nome de cliente.
- Nesta skill: portão técnico desta skill: `scripts/site.py check` (0 erros) + `scripts/varredura.py`; exemplos da área: `references/receitas-de-dobra.md` e a calibração de páginas.
- Respostas curtas; custo de tokens: `../revisao-de-design/references/economia.md`.
- **1ª entrega = 100%:** funil (20–30 ideias → construir ≥ 6 → 3 melhores, todas ≥ bom, 1 premium), aplicado
  e em cor (`../brand-studio/scripts/prancha.py` para logo), com nota e risco de cada — nunca rascunho como opção
  (`../revisao-de-design/SKILL.md` §Primeira entrega).
- **Pago → Adobe primeiro:** com o conector Adobe ligado, fonte, foto, ícone, textura ou modelo PAGO é buscado
  antes no Adobe (Fonts incluída no plano, Stock, Express); só depois criar ou procurar grátis. Regra:
  `../direcao-de-arte/references/tipografia.md` §11 nº 4.
- Primeiro uso na máquina: `python ../brand-studio/scripts/doctor.py` e explicar ao usuário o que é obrigatório,
  recomendado e opcional (Gemini é pago e opcional) seguindo `../brand-studio/references/instalacao.md`; pedir permissão antes
  de instalar. Passo a passo de cada entrega: `../brand-studio/references/receitas-de-producao.md`.

## Ferramentas
| O quê | Onde |
|---|---|
| **`scripts/site.py`** (`--help`) | `new` · `marca` · `check` · `pack` · `copy-diff` |
| Prints atuais (2 temas, 3 tamanhos) | `scripts/previas.py <url> <saida> --auto out/` |
| Checagem numérica (cor proibida, transbordo, botão fora da dobra) | `scripts/varredura.py <url> --rotas …` |
| Template Next.js limpo + página-exemplo neutra | `assets/template/` |
| Verificadores | `../direcao-de-arte/scripts/check_pagina.py` e `teste_pagina_total.py` |
| Padrão de página (contrato fixo) | `references/padrao-de-pagina.md` |
| Receitas de dobra | `references/receitas-de-dobra.md` |
| Stack, hospedagem, `.htaccess`, env | `references/contrato-tecnico.md` |
| Checklist de entrega | `references/checklist-entrega.md` |
| Lições de página (o que gera retrabalho) | `references/licoes-de-pagina.md` |
| Regras de página de captura | `../direcao-de-arte/references/paginas-de-captura.md` |

Projetos de teste em pasta curta (caminho longo quebra o build no Windows).

## Regras duras
1. **Copy FINAL do cliente.** Só texto aprovado (`content/copy.json`). Nunca inventar preço, "de/por", urgência,
   contador falso, depoimento. Pendências vão para `pendencias.md`, fora da página. `site.py copy-diff` acusa o resto.
2. **Foto de gente é real**, recortada e centrada pela tinta. **IA só para cenário/textura/forma**:
   `gemini.py gen … --model banana21`. Nunca gerar nem alterar pessoa.
3. **Movimento sempre ligado** (`total` · `suave` quando o sistema pede menos movimento · `parado` só por
   `?movimento=parado`). Só `transform`/`opacity`/`clip-path`; nunca no H1, na foto do LCP nem no CTA; estado natural
   do CSS = estado final (`forwards`, nunca `both`).
4. **Sem `100vw` em layout** (a barra de rolagem tem 15 px): `%`, `cqw` ou variável.
5. **Dobra = tela inteira**, centrada na altura; a seguinte não aparece. Imagem → título → apoio → botão → micro, num
   eixo. Logo UMA vez. Sem eyebrow, selos nem faixa na 1ª tela.
6. **Espaço é sistema**: 12 · 24 · 40, margem esquerda = direita, seção `--sec`, escala 4…200. Botão com rótulo em
   1 linha em toda largura (360 incluso).
7. **Pop-up só por clique**; foco no título; ESC fecha; fechar não apaga o digitado; erro com fio + ✕ + "Erro:".
8. **Estático de verdade**: `output:'export'`; sem API routes, middleware, Server Actions; `withBase()` em todo
   caminho que começa com `/`.
9. **Verificar como o usuário vê**: Chrome com barra de rolagem clássica, movimento reduzido ligado e desligado, 360
   e 390, rolando seção por seção. 0 erros nos DOIS verificadores antes de mostrar.
10. **Página CLEAN**: 1 mensagem por tela, ≥ 38–50% de área vazia; linguagem de forma do cliente; o logo nunca
    arredonda.

## Fluxo
```
- [ ] 0 Entradas  - [ ] 1 Pesquisa + ideia  - [ ] 1b Elementos  - [ ] 2 Projeto  - [ ] 3 Dobra
- [ ] 4 Seções    - [ ] 5 Movimento         - [ ] 6 Verificação + revisão       - [ ] 7 Documentação  - [ ] 8 Entrega
```

### 0. Entradas (sem elas, parar e pedir)
Identidade (`brand.json` ou cores + fontes + forma; logo SVG em curvas claro/escuro/símbolo) · **copy final** · fotos
reais recortadas (640 e 1100 px WebP) · objetivo (CTA único, campos, endpoint, link) · origem do tráfego (Instagram/Meta
→ mobile primeiro). `python scripts/site.py marca <brand.json>` mostra o que será usado e o contraste.

### 1. Pesquisa nova e ideia gráfica única
Repertório do estúdio (`../revisao-de-design/references/repertorio/`, arquivo de sites) + pesquisa curta
própria (`../direcao-de-arte/references/referencias-e-pesquisa.md`). UMA ideia gráfica para a dobra,
derivada do assunto ou do logo; receitas (`references/receitas-de-dobra.md`) como princípio, nunca cópia.
Teste: "qual é a UMA ideia da tela?" e "sem a foto, o resto ainda é composição?". Dúvida entre 2–3 ideias → arena
(`../revisao-de-design/references/arena.md`).

### 1b. Elementos ANTES da página
O kit de elementos do cliente existe e foi revisado um a um (`../direcao-de-arte/SKILL.md`, ornamentos)? Se não, fazer
primeiro, só o que a página vai usar. Inventário "elemento → onde entra"; CSS só para o que o kit não tem.

### 2. Criar o projeto
```bash
python scripts/site.py new <pasta> --marca <brand.json|pasta> --copy <copy.json> \
       [--logo x.svg --simbolo s.svg] [--foto recorte.png --foto-alt "…"] [--install]
```
Sem `--marca`: `--cores "ink=#…,papel=#…,destaque=#…"` e `--fontes "display=Família:900,texto=Família:400/700"`.
A copy precisa de `hero.h1` e `hero.cta`.

### 3. Dobra no contrato
Inventário por escrito (elemento · papel · fica/sai) em `docs/decisoes-do-projeto.md`; orçamento de altura em px para
360×740, 390×844, 768×1024, 1024×768, 1440×900. Montar a 390 px e escalar. Template traz o **holofote**
(`components/secoes/Hero.tsx` + `styles/pagina.css`); outra receita → trocar o Hero e o bloco `.pg-hero`.

### 4. Seções
Cabeçalho · dobra · passos · destaques · faixa · FAQ · fecho · rodapé — só o que a copy tem. Nova seção = componente
em `components/secoes/` + linha em `app/page.tsx` + chave em `lib/copy.ts`. Fundo alterna; listas com fios, não caixas.
**Páginas irmãs** (produto × versão): um componente de dobra único; cor do produto manda; cor da marca-mãe só na
página-mãe; varrer cor por script (`varredura.py`). Tema claro/escuro por tokens.

### 5. Movimento
Uma linguagem assinatura do conceito repetida com variações, mesma curva e tempos. `Reveal` (CSS `view()`, 0 JS);
GSAP só onde precisa (import dinâmico em idle); nada que prenda a rolagem. Testar `total`, `suave` e `parado`.

### 6. Verificação + revisão
```bash
python scripts/site.py check <pasta>              # build + check_pagina + teste_pagina_total + peso + copy-diff
python scripts/site.py check <pasta> --rapido     # menos larguras (no laço de correção)
```
`APROVADO (0 erros)`; cada AVISO = corrigir ou justificar por escrito. Depois: 1 folha com as PNGs de `.check/`
(390, 768, 1024, 1440) → régua → decisão (protocolo de revisão, máx. 2 rodadas). Ao corrigir, reexecutar o sistema
inteiro (espaço, margem, alinhamento, hierarquia) em todas as larguras — corrigir "só o apontado" cria outro erro.

### 7. Documentação
`docs/decisoes-do-projeto.md` (ideia da dobra, parâmetros, correções = regra). Lição que serve a outros clientes →
`references/licoes-de-pagina.md` (genérica, sem nome de cliente). `pendencias.md` para o cliente.

### 8. Entrega
```bash
python scripts/site.py pack <pasta> --subpasta <nome> --site-url https://… [--endpoint …] [--destino …] [--indexar]
```
Gera `<slug>-raiz.zip`, `<slug>-subpasta-<nome>.zip` e `<slug>-fonte.zip` + `LEIA-ME.txt`. Conferir
`references/checklist-entrega.md`. Endpoint, destino e URL são gravados NO BUILD: mudou → refazer. Dizer o que NÃO
foi testado (Safari/iOS, Firefox em aparelho real).

## Armadilhas já resolvidas
Botão `nowrap` alarga a trilha da grade (`minmax(0,1fr)`) · `overflow:hidden` prende o `view()` (`clip`) ·
`text-wrap: balance` + SplitText muda quebras (medir) · `}` fora do lugar em `@media` apaga o desktop (build +
verificador a cada edição de CSS) · `NEXT_PUBLIC_BASE_PATH=/site` no Git Bash vira caminho de disco (usar `site`;
rotas sem barra inicial) · `node_modules` como junção derruba o Turbopack · cache `.next` guarda `NEXT_PUBLIC_*` velho
· `<p>` < 16 px = erro · prévia de rodada antiga nunca vai para entrega (`previas.py` gera de novo).
