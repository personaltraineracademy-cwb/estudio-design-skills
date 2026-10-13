# Arena — comparar às cegas para ESCOLHER

A arena escolhe entre opções reais. Não é ferramenta de polimento (isso é o ciclo de 2 rodadas do SKILL.md).

## Quando usar (do mais barato ao mais caro)
| Uso | Compara | Quando | Custo |
|---|---|---|---|
| Antes × depois | versão anterior × corrigida (pares fixos) | dúvida se a correção melhorou | baixo |
| Composições | a MESMA mensagem em 2–6 modelos de peça | escolher modelos de um sistema | médio |
| Territórios | 3–4 rotas inteiras de identidade | usuário pede "arena"/"vários subagentes", ou marca nova sem direção | alto |

Limite: **uma arena por decisão + no máximo um antes × depois**. Arena de territórios sozinha tende a ranquear rotas
medianas — rode depois de um primeiro impacto forte, para achar a peça boa, não como processo inteiro.

## Regras
1. **Às cegas e nas duas ordens** (AB e BA). Consistência AB/BA < 70% = juízes sensíveis à posição → prompt mais concreto.
2. **Painel mínimo**: diretor(a) de criação + público (lê em 2 s no celular). Opcional: sistema/tipógrafo + juiz de outra
   família de modelo (`../brand-system/scripts/arena.py gemini`). O público é obrigatório: especialista premia conceito,
   público pega o que não se lê.
3. **Mesma régua** do protocolo ([regua.md](regua.md)): cada juiz dá as 8 notas 0–4 para cada lado + defeitos com o
   lugar exato + 1 correção concreta por opção.
4. **Portão absoluto**: se o 1º colocado tem nota absoluta < 7 (média < 2,8), **não seguir**: criar opções novas ou
   corrigir e rodar antes × depois (que conta como a rodada 1 ou 2 do ciclo).
5. **Empate técnico** (intervalos sobrepostos): levar os dois ao usuário, ou, com carta branca, o diretor decide e
   escreve por quê. Híbrido só se as forças caem em camadas diferentes (ex.: símbolo de um + comportamento do outro).
6. **Checkpoint humano**: mostrar ranking + 2–3 primeiros; a escolha do usuário é final e fica registrada como voto.

## Comandos (`../brand-system/scripts/arena.py`)
```
python arena.py add <dir>/arena --board <img> --name "A · nome" --desc "ideia" --author <persona>
python arena.py pair <dir>/arena --all        # até 6 opções: todos contra todos
python arena.py vote <dir>/arena --file votos-<persona>.json
python arena.py gemini <dir>/arena --round 1  # juiz de outra família
python arena.py rank <dir>/arena              # Bradley-Terry + IC90 + nota absoluta
```

## Prompt do juiz (subagente, curto)
```
Você é JUIZ <persona>. Leia <arena>/r1/juizes.md e confrontos.md (às cegas). Para cada imagem, compare A × B pelos
8 critérios de revisao-de-design/references/regua.md (0–4 cada), cite evidência visível e o lugar exato dos defeitos,
dê nota absoluta 0–10 de cada lado e 1 correção concreta por opção. Julgue cada ordem de forma independente.
Grave votos-<persona>.json e responda só "ok, N votos" + 3 linhas.
```

## Territórios com subagentes (só quando pedido)
4 subagentes, um por rota, escolas e paletas diferentes entre si, limite ~15 min cada, briefing com: plataforma da
marca, clichês proibidos, 2 restrições sorteadas, entregáveis (primitiva SVG em curvas, 4 elementos, paleta, par
tipográfico, board 1920×1080 via `../brand-system/scripts/board.py`). Roteiro completo em
`../brand-system/references/criacao.md`. Lembrete de custo: agentes longos em paralelo consomem o limite rápido —
preferir 2 rotas fortes a 4 medianas.
