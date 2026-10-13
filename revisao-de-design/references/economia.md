# Modo econômico — gastar menos tokens e errar menos

Gasto alto + erro alto = processo ruim, não falta de esforço. Estas regras valem para todas as skills do estúdio.
**Economia nunca corta qualidade nem o esforço da primeira entrega** (funil completo antes de mostrar): o que se corta é repetição, leitura inútil e retrabalho — nunca o portão técnico,
a régua, o olhar final nem a pesquisa nova.

## Contents
- Conversa
- Criação
- Ferramentas
- Orçamento e roteamento (avançado)
- Checklist de 30 segundos

## Conversa
- **Resposta curta.** Sem saudação, sem repetir o pedido, sem narrar cada ferramenta. Fragmentos ok.
  Com o plugin caveman instalado, ele já faz isso (`/plugin marketplace add JuliusBrussee/caveman` →
  `/plugin install caveman@caveman`). Código, commits, documentos e avisos de segurança: escrita normal.
- **Uma pergunta por vez só quando bloqueia.** Com padrão razoável, decidir e dizer o que decidiu.

## Criação
1. **Padrão antes de montar**: decidir o componente/contrato das peças irmãs e construir num lugar só. N edições
   independentes custam N× e saem N vezes diferentes.
2. **Script mede antes do olho**: transbordo, contraste, cor fora da paleta, texto cortado, tamanhos. O olho fica para
   gosto, padrão e função.
3. **Olhar pouco e pequeno**: 1 folha de contato por rodada (miniaturas); zoom só no suspeito. Imagem grande repetida
   é o maior custo isolado. Imagem enviada ≤ 8000 px de lado (folha alta vira páginas).
4. **Verificador completo só no fim** (1 vez). No laço de correção: build + checagem rápida do que mudou.
5. **Máximo 2 rodadas de correção** e devolver ao usuário (protocolo do SKILL.md).
6. **Quantidade média**: gerar só o que a peça real vai usar; variações com teto (≤ 4 por eixo, 1 folha por eixo).

## Ferramentas
7. **Não reler nem reescrever**: buscar com `grep`, ler com faixa de linhas, editar cirúrgico. Patch longo vai num
   arquivo `.py`, não em heredoc (heredoc perde barras invertidas).
8. **Subagente só para trabalho independente e curto**, com briefing de 10–20 linhas: padrão, critérios de aceite,
   limite de 2 rodadas, formato de resposta curto. Nunca 3+ agentes longos em paralelo sem o usuário pedir. Gravar
   estado em arquivo. Todo briefing começa com: "Modo econômico: respostas no estilo caveman (curtas, sem enfeite),
   leia por faixa/grep, edite cirurgicamente, relatório final ≤ 10 linhas." Preferir `caveman:cavecrew-*` quando servirem.
9. **IA de imagem/vídeo só onde o código não resolve**: 1 teste pequeno (1K, n=1) antes de gerar lote.
10. **Estimar antes de frente grande**: quantas peças/imagens/agentes; se passa do razoável, reduzir escopo ou perguntar.

## Orçamento e roteamento (avançado)
11. **Modelo certo para cada trabalho** (quando o ambiente permite escolher o modelo do subagente):
    | Trabalho | Modelo |
    |---|---|
    | achar arquivo, listar, grep, renomear, conferir formato | o mais leve (ex.: Haiku) ou `caveman:cavecrew-investigator` |
    | ler muito material e resumir, pesquisar na web, reescrever no formato | intermediário (ex.: Sonnet) |
    | decidir conceito, julgar nível, revisar o que vai para o usuário, integrar | o mais forte (o principal) |
    Julgamento nunca desce de nível; leitura e coleta sobem só se o resultado veio fraco.
12. **Resultado vai para ARQUIVO, não para a conversa**: o subagente grava a saída completa num arquivo de rascunho e
    devolve ≤ 10 linhas; o principal lê por `grep`/faixa só a parte que vai integrar.
13. **Destilar uma vez, reusar sempre**: material grande (site capturado, pesquisa, PDF) vira um resumo de ≤ 200
    linhas gravado; as próximas tarefas leem o resumo, nunca a fonte bruta de novo.
14. **Imagem barata**: reduzir para ≤ 1024 px ou recortar a região antes de abrir; 1 folha de contato em vez de N
    imagens; nunca abrir a mesma imagem duas vezes na mesma rodada.
15. **Chamadas em lote**: ferramentas independentes na MESMA mensagem; um script que faz 5 checagens > 5 chamadas.
    Saída de comando sempre cortada (`| tail -n 5`, `Select-Object -Last 5`) — só a linha que decide.
16. **Prefixo estável**: instruções fixas (SKILL.md, references) lidas uma vez no começo; nada de reler o mesmo
    arquivo para "lembrar". Estado de trabalho longo em `ESTADO.md` para retomar sem reler tudo.
17. **Orçamento por tarefa** (anunciar em 1 linha antes de começar frente grande): P = 1 peça/edição (sem subagente,
    ≤ 2 imagens abertas) · M = série/página (≤ 1 subagente, 1 folha por rodada) · G = identidade/site/estudo (≤ 3
    subagentes em paralelo, cada um com arquivo de saída). Passou do orçamento → parar, resumir, perguntar.
18. **Profundidade proporcional ao risco**: entrega final para o cliente = revisão completa; rascunho interno =
    portão técnico + 1 olhada na folha.

## Checklist de 30 segundos (antes de cada passo caro)
```
- [ ] Já existe resumo/arquivo pronto? (ler ele, não a fonte)
- [ ] Dá para medir por script em vez de abrir imagem?
- [ ] Este subagente precisa do modelo forte? Saída vai para arquivo?
- [ ] As chamadas independentes estão no mesmo lote?
- [ ] O que eu cortar aqui reduz qualidade? Se sim, não cortar.
```
