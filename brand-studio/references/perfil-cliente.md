# Perfil do cliente (estilo herdado de trabalhos aprovados)

O estúdio serve **qualquer pessoa, empresa ou projeto**. A biblioteca guarda os trabalhos aprovados separados por
cliente: `<pasta de trabalho>/biblioteca/<Cliente>/<Projeto>/` + `<Cliente>/_perfil.md` (DNA visual do cliente) +
`<Cliente>/_fichas.json` (ficha de cada projeto). O perfil só vale **para o próprio cliente**.

## No início de todo trabalho
1. Descubra de quem é o trabalho (cliente/empresa e, se houver, a marca-mãe).
2. `python scripts/library.py clients` — clientes que já existem.
3. **Cliente com perfil** → `library.py profile <Cliente>` + `library.py projects --client <Cliente>`: siga a
   linguagem (dispositivos, fórmula de cor, kit mínimo) e respeite a lista "não repetir".
4. **Cliente novo / sem acervo** → não herde o estilo de outro cliente. A linguagem nasce da pesquisa, do briefing e
   das referências que a pessoa mandar. A biblioteca inteira (todos os clientes + mercado) serve só como repertório e
   como filtro de originalidade (`library.py novelty`).
5. Sub-marca/campanha de uma marca-mãe já cadastrada → use o perfil da marca-mãe + co-branding/endosso dela.

## Como escrever o `_perfil.md` de um cliente (depois das primeiras aprovações)
Olhe `library.py sheet --client <Cliente> -o folha.png` e as fichas, e escreva (modelo: `references/perfil-modelo.md`):
1. Quem é o cliente + cores oficiais (fonte).
2. Gramática do lockup (como o nome, o símbolo e os endossos se organizam).
3. Dispositivos recorrentes (tabela: dispositivo · onde aparece · gerador).
4. Fórmula de cor + destaques já usados (HEX).
5. Kit mínimo que o cliente recebe.
6. Onde superar (o que o acervo ainda não faz).
7. Não repetir (símbolos/metáforas que já são do cliente).
Atualize o perfil quando um projeto novo for aprovado.

## Registrar aprovações
```
python scripts/library.py add "<kit>/svg/<nome>-horizontal-positivo.svg" --client "<Cliente>" --project "<Projeto>" --note "por que aprovou"
```
e acrescente a ficha do projeto em `biblioteca/<Cliente>/_fichas.json` (tipo, segmento, conceito, recursos, cores com
HEX, tipografia, porque_aprovado, evitar).
