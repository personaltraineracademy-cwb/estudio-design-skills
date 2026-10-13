# Ideação e crítica — como chegar em algo novo

## 1. Pesquisa antes de desenhar (15 min, não 2 h)
- `library.py profile <Cliente>` + `library.py projects --client <Cliente>`: o que o cliente já tem e o que não
  pode repetir (cliente novo: pule).
- `library.py search "<descrição visual>" --source mercado --k 18 --sheet pesquisa.png` e
  `library.py similar <referência do usuário> --sheet sim.png`: o que já existe parecido.
- Referências do usuário: extraia **princípios** (contraste, ritmo, peso, gesto, humor), nunca formas.
- Web (WebSearch/WebFetch): concorrentes, clichês do setor, símbolos culturais do tema. Cite fontes.
- Escreva a lista de **clichês proibidos** do tema (ex. Black Friday: etiqueta, sacola, raio, %, contagem genérica)
  — só podem voltar com uma forma realmente nova.
- **Curso, pós, mentoria ou produto técnico**: leia a ementa (ou pergunte) e liste **10 saberes do assunto** —
  ferramenta, medida/razão, lei, protocolo, gesto técnico, erro clássico, número famoso, gíria. É daí que sai o
  símbolo que só esse curso pode ter (checklist: `references/logo-anticliche.md`).

## 2. Divergir — 20 a 30 ideias de uma linha, em 4 territórios
| Território | Pergunta | Exemplo |
|---|---|---|
| **Letra/numeral** | qual letra/numeral pode carregar a ideia? | um "2026" com numeral próprio; um F que vira barra |
| **Metáfora** | o que a marca *faz* parece com o quê? | escala → degraus; consultoria → mapa dobrado |
| **Gesto/movimento** | qual ação física resume? | puxar, empurrar, girar, subir, quebrar |
| **Sistema/forma** | qual regra geométrica gera a família? | cortes radiais, módulos 3×3, anéis |

Técnicas para forçar o inesperado (use pelo menos duas por projeto):
- **Combinação forçada**: objeto do setor × objeto aleatório (sorteie um substantivo) → ache a forma comum.
- **Inversão**: o oposto do clichê (Black Friday *calmo e premium*; fitness *sem músculo*).
- **Troca de material/escala**: e se fosse costurado, carimbado, neon, recortado em papel, dobrado?
- **Restrição**: só 3 formas · só retas a 45° · só um círculo e um corte · cabe numa grade 4×4.
- **Espaço negativo**: o que aparece *entre* duas formas?
- **Saber do assunto** (obrigatória em curso/produto): um saber da lista vira letra, símbolo ou sistema — ex.: o acento
  de uma letra vira o instrumento de medida do assunto; uma proporção famosa da área vira o símbolo; uma sigla
  com duplo sentido (elemento químico × palavra) vira o monograma. Proibido usar o corpo literal da categoria no lugar disso.
- **Figura que completa a forma**: se houver figura, ela é metade do símbolo (não um ícone ao lado).
- **Generativo**: rode um sketch (ou escreva um novo) com 24–36 seeds e procure acidentes bons — depois
  redesenhe à mão o melhor acidente com geometria limpa.

Filtre para **3–4 conceitos** que sejam de territórios diferentes, cada um com uma frase de defesa.

## 3. Crítica — rubrica (0–3 cada; aprova com ≥ 12/15 e nenhum 0)
| Critério | 3 = |
|---|---|
| Ideia | explicável em 1 frase, com uma virada própria (em curso: vem de um saber do assunto) |
| Distinção | `novelty` ok + não usa nada da lista "não repetir" do cliente nem corpo literal da categoria |
| Leitura | entende em 1 s; nome legível; funciona a 16 px (símbolo); cada colorway com fundo declarado e existe positivo |
| Craft | geometria limpa, ângulos/raios consistentes, sem `<text>`, junções limpas; uma linguagem por símbolo, peso compatível com o nome; nenhuma letra cortada; texto revisado (acentos, hífen) — `logo_qc.py` |
| Sistema | gera padrão, selo, KV e movimento sem esforço |

## 4. Originalidade (CLIP)
`library.py novelty candidato.png` compara com todo o acervo (todos os clientes) + mercado:
- **≥ 0,93 quase cópia** → descarte ou mude a forma de verdade.
- **0,88–0,93 parecido** → abra os dois lado a lado e julgue; símbolos simples pequenos têm base alta (~0,85)
  porque o CLIP vê "ícone preto", então decida pelo olho.
- Variações do *mesmo* projeto pontuam alto de propósito.
- **Ponto cego**: o mercado do índice é quase todo de tecnologia. Silhuetas de academia deram ~0,70 ("ok") — em
  fitness, saúde e educação o `novelty` não pega clichê de categoria; quem pega é a lista de clichês + o olho.
O filtro não substitui busca de marca registrada (INPI) — recomende quando a marca for permanente.
