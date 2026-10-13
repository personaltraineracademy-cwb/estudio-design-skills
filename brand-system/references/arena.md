# Arena na identidade visual

Regras, painel, régua, portão absoluto (≥ 7), limite e comandos: `../revisao-de-design/references/arena.md`.
Este arquivo guarda só o que é próprio da brand-system.

## Ordem de uso
1. **Primeiro impacto** (metodo.md) — sempre antes de qualquer arena.
2. **Composições**: a mesma mensagem em cada modelo de peça (modelos.md), formato feed:
   ```
   python modelos.py render <marca> <id> --texto "<mesma frase>" --info "…" --formatos feed -o <marca>/arena-pecas/entradas/<id>
   python arena.py add <marca>/arena-pecas --board <…>/<id>-1080x1350.png --name <id> --desc "modelo <id>"
   python arena.py pair <marca>/arena-pecas --all
   ```
3. **Antes × depois** depois de aplicar as correções dos juízes (conta como rodada do ciclo de revisão).
4. **Territórios** só quando o usuário pede ou a marca não tem direção nenhuma.

## Briefing de designer-subagente (territórios)
```
Você é <persona> da escola <escola> (regras formais: criacao.md §4).
Projeto: <brand.json: briefing + platform (idea, tension, principles, enemy, zag)> · Clichês proibidos: <lista>.
Restrições sorteadas: <2 cartas>. Domínio de metáfora: <a 3–5 passos do assunto>.
Entregue em <dir>/territorios/<letra>/:
 1. territorio.md — nome, ideia em 1 frase, por que é desta marca, assinatura, DNA (ângulo/raio/traço), 3 riscos.
 2. primitiva(s) SVG em curvas (sem <text>), à mão ou com elements.py/sketch.py.
 3. elementos: `python elements.py explore` na primitiva → escolha 4 → `make`.
 4. paleta (3–4 HEX, diferente das outras rotas) e par tipográfico OFL (evite fontes-padrão de IA).
 5. board: `python board.py <dir>/territorios/<letra>`; olhe (Read) e refaça o fraco.
Revisão: protocolo revisao-de-design, máx. 2 rodadas. Limite ~15 min.
Devolva (≤ 6 linhas): caminho do board, ideia, 3 riscos, problemas nos scripts.
```
Personas (escolas diferentes): suíço-sistêmico · tipógrafo de letras próprias · modernista/vernacular brasileiro ·
generativo/dados · cartaz polonês · brutalista.

## Portões antes de julgar (sem IA)
`library.py novelty` (< 0,93; 0,88–0,93 olhar no olho) · `palette.py check` nos pares · `apply.py stress` no
vencedor (16 px, 1 cor) · nada da lista de clichês. Reprovou → fora da arena.

## Escolher modelo de IA de imagem
`python arena.py modelos --board text_to_image --category commercial_design` (lê o dataset público do ranking
arena.ai, CC-BY-4.0; o site em si não pode ser automatizado pelos termos de uso).
