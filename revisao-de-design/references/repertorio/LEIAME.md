# Repertório do estúdio — referências que o estúdio considera excelentes

Banco de referências PÚBLICAS (sites, logos, identidades, manuais, elementos, peças) que o estúdio julgou bom ou
premium, destiladas em princípios medidos. Serve para pesquisar antes de criar, calibrar a régua e inovar a partir do
princípio — **nunca copiar**.

## Arquivos (um por domínio, cada um ≤ 200 linhas)
| Arquivo | Domínio |
|---|---|
| `logos.md` | logos, símbolos, wordmarks, monogramas |
| `identidades.md` | sistemas de identidade, comportamento de marca, cor, tipografia |
| `manuais.md` | manuais de marca e design systems (estrutura, regras bem escritas) |
| `elementos.md` | elementos gráficos, padrões, texturas, grids, ícones |
| `pecas.md` | posts, anúncios, cartazes, key visuals, séries |
| `sites.md` | sites e páginas de conversão (dobra, ritmo, movimento, CTA) |
| `tipografia.md` | pares e usos de fonte notáveis |
| `movimento.md` | animações de site, logo e peça (gatilho, duração, curva, que história conta) |
Diagramas próprios (esquemas redesenhados, nunca print): `../../assets/repertorio/<dominio>-<id>.svg`.

## Formato de cada entrada (copiar)
```
### <ID> · <nome da referência> — <nível: bom | premium>
- Fonte: <URL pública> · <autor/estúdio, ano> · licença/uso: só estudo
- O que é: <1 linha>
- Princípio: <1–2 linhas: a regra por trás, transferível>
- Medidas: <números medidos: proporções, tamanhos, espaçamentos, nº de cores, tempos de movimento>
- Por que converte/encanta: <1 linha ligada à régua (Id, Df, Le, Co, Cr, Fu, Ch, Ac)>
- Como aplicar na nossa versão: <1–2 linhas: derivar do assunto do cliente>
- Não copiar: <o que é assinatura deles>
- Tags: <setor> · <técnica> · <arquétipo>
```
IDs: `LG-01` logos · `ID-01` identidades · `MN-01` manuais · `EL-01` elementos · `PC-01` peças · `ST-01` sites ·
`TP-01` tipografia · `MV-01` movimento.

## Regras
1. **Sem prints, logos ou arquivos de terceiros no pacote** (direito autoral e marca registrada): só link, princípio,
   medida e, se ajudar, um esquema SVG redesenhado em blocos neutros.
2. Só entra o que é **bom ou premium** na régua (`../regua.md`); "normal" não entra.
3. Princípio > descrição. Uma entrada que não ensina a fazer algo novo sai.
4. Sem nomes de clientes do estúdio, sem dados pessoais, sem datas no texto.
5. Duplicado: fundir na entrada existente (acrescentar medida ou exemplo), não criar outra.
6. Limite: ~25 entradas por arquivo; acima disso, cortar as mais fracas.

## Como as skills usam
- Pesquisa antes de criar (brand-studio, brand-system, direcao-de-arte, criacao-de-sites): `grep -i "<tag>"` nos
  arquivos do domínio → escolher 3–5 princípios → a peça nova tem que ser **diferente** de todas (critério Df).
- Revisão: comparar a peça com as entradas premium do domínio para calibrar a nota.
