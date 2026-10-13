# Variações com limite (`scripts/variacoes.py`)

Para a pessoa poder **comparar sem esperar horas**: poucas opções, todas aplicadas nas MESMAS peças.

## Regra do limite
- **Até 4 opções por eixo** (a atual + 3 novas). Mais que isso vira cardápio e ninguém decide.
- **Uma folha por eixo**, com cada opção aplicada nos mesmos 2 modelos de peça (ou no mesmo logo × 3 fundos).
- **Sem refino** nesta etapa. Só o escolhido é refinado.
- Tempo-alvo: ~30 min para todos os eixos.

## Eixos e comandos
| Eixo | Comando | O que sai |
|---|---|---|
| Fonte de títulos | `variacoes.py fontes <dir> --opcoes "A:900,B:800,C:900,D:800"` | colunas = fontes, linhas = modelos |
| Cor | `variacoes.py cores <dir> --opcoes "Nome=#brand,#ink,#paper,#accent;…"` | colunas = paletas; **avisa contraste < 3:1** (combinação ilegível não é proposta) |
| Logo | `variacoes.py logo <dir> --arquivos a.svg,b.svg,c.svg` | cada assinatura sobre brand, ink, paper + com 32 px de altura |
| Elementos | `variacoes.py elementos <dir> [--ops …] [--n 4]` | `elements.py explore` na forma-mãe → escolha até 3 novos |
| Composição | arena de composições (references/arena.md) | mesma mensagem nos modelos de peça |
Saída: `<dir>/variacoes/<eixo>.png`. Opções comuns: `--modelos id1,id2`, `--formato feed`, `--sem-limite`.

## Como gerar opções que valem a pena
- **Logo**: varie a *relação* entre símbolo e palavra (lado a lado · empilhado · **integrado** — o símbolo dentro
  da palavra · só tipografia com o gesto). Integrar o símbolo na palavra costuma ser a descoberta.
- **Fonte**: a atual + uma de mais personalidade + uma mais neutra + uma de outra largura (condensada/larga).
  Recuse as "padrão de IA" (criacao.md §5) e a fonte do último projeto.
- **Cor**: mantenha os papéis (brand/ink/paper/accent) e troque a cor-assinatura por uma que tenha **história**
  (Vermelho Pare, Âmbar de Sódio, Prata Refletiva) — nunca uma cor "bonita" sem motivo.
- **Elementos**: as 6 operações mais produtivas (contour, slice, halftone, stack, modules, outline), 4 variações
  cada → escolha até 3 que acrescentam função (rastro, desmonte, versão 1 cor).

## Depois da folha
Mostre as folhas (SendUserFile) com **uma recomendação por eixo e o porquê**; a escolha é da pessoa. Registre no
diário (references/metodo.md §Documentar) o que foi escolhido e o que morreu.

## Trocou a paleta? Varredura das cores antigas
Ao retirar uma cor (ou colorway), procurar os HEX antigos em TODO o projeto — código, temas, CSS, SVG, `brand.json`,
peças (`grep -ri "#hex"`), inclusive degradês e opacidades derivadas — e conferir a folha de contato. Num caso real, o
degradê de uma cor já retirada sobreviveu num painel.
