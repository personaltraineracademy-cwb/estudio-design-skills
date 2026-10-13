# Entrega para designers: pasta única, compacta, atual
Pedido típico: "SVG e outros formatos para qualquer outro designer baixar e usar, bem organizado e explicado, só o que foi
aprovado e usado, compacto, sem o que não agrega". Depois: "coloque tudo (sites, página-mãe, elementos do dourado,
fundos, efeitos)". Método e ferramentas:

**Ferramenta:** `brand-system/scripts/entrega.py <projeto> [--biblioteca]` (+ `entrega.json` com a curadoria).
Pastas: 01-logos · 02-cores · 03-tipografia · 04-elementos · 05-fotos · 06-pecas · 07-sites · 08-manual-e-tokens ·
09-fundos-e-texturas, cada uma com LEIA-ME.md e a raiz com `00-LEIA-ME.md` (regras em 1 minuto + pendências do cliente +
o que NÃO está aqui de propósito).

**Regras**
1. **Gerar do estado atual.** Prévia copiada de rodada antiga foi o erro nº 1 (a cliente abriu e viu o André v1 velho,
   sem as mães). Prévias de site: `criacao-de-sites/scripts/previas.py`; manual refeito por último.
2. **Dois níveis de elementos:** (a) *aplicados* — lista curada, nomes claros (`goniometro-circular-90__fundo-escuro.svg`),
   sem duplicata, com a explicação de cada uso; (b) *biblioteca completa* — `ornamentos.exportar --zip` (15 famílias ×
   produtos × 2 fundos = milhares de SVG): zip por produto + folha JPG por família + `_indice.csv`.
3. **Marca-mãe entra junto:** elementos/kit dourado, página-mãe e logos "todos"; não só os produtos.
4. **Compacto:** SVG em zip, folhas em JPG (≤ 1800 px), peças em JPG q94, `site.py pack` deixa só os zips
   (`--manter-pastas` se precisar das pastas). 470 MB → ~270 MB só com isso.
5. **Fora:** reprovados, testes, rascunhos, `_antigas`, logos de terceiros (pós oficiais), pessoa gerada por IA, código
   de trabalho. Cliente pediu "tire o que não agrega".
6. **Explicar o uso, não só listar:** para cada elemento, o que é e para que fundo serve; regras de cor/forma/logo no
   README; pendências do cliente (termo de imagem, INPI, canais) sem inventar.
7. **Conferir antes de dizer "pronto":** abrir 3 arquivos de cada pasta, contar arquivos e MB, ver se as mães e os
   dois temas estão lá.
