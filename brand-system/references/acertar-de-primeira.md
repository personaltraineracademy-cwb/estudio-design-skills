# Acertar de primeira — pré-voo de projeto novo

Vale para identidade, campanha, série de peças ou site. Leia antes da 1ª mensagem ao cliente e de novo antes de cada
checkpoint. Cada item abaixo já custou uma rodada de retrabalho em algum projeto. Gosto do estúdio:
`../../revisao-de-design/references/gosto.md`. Protocolo de revisão: `../../revisao-de-design/SKILL.md`.

## 1. Perguntas da 1ª conversa (até 6, numa mensagem, com opções e uma recomendada)
- [ ] **De quem é e é do zero?** Cliente, marca-mãe, grafia exata do nome. "Do zero" = perguntas neutras, nada herdado
      (nem perfil, nem cor, nem teste antigo) — porque pré-preencher o que o cliente mandou zerar é a 1ª reprovação.
- [ ] **Arquitetura:** há produtos, linhas, cursos, turmas ou pessoas que pedem cor ou logo próprio? Como a marca-mãe
      aparece (endosso, ao lado, por extenso)? — porque descobrir isso no meio refaz cor, kit e manual.
- [ ] **Onde vive e quando:** lista de peças, formatos (1:1, 4:5, 9:16, página, apresentação, mensageiro), datas.
- [ ] **Copy oficial e proibições:** documento, oferta, CTA, o que não pode ser dito.
- [ ] **Pessoas reais:** quem aparece, há fotos soltas, há termo de imagem que cite IA?
- [ ] **Cor e personalidade:** livre, cores da marca, herdar campanha anterior?
Regras: pergunte só o que muda a FASE atual (na fase do logo, nada de copy nem peças). Sem resposta ou "você decide" →
siga a recomendada, diga qual e escreva a suposição no briefing. "Só pesquise" → só leitura até aprovar. Exemplo que o
cliente cita (ferramenta, estilo) é ilustração, não regra. Quando o cliente não sabe → folha de variações com limite.

## 2. Materiais a pedir logo no início
- [ ] Documento da campanha / copy final (nome, frase, oferta, CTA, datas, horários).
- [ ] Logos oficiais em SVG (marca-mãe, produtos, parceiros), com versão monocromática.
- [ ] Fotos de cada pessoa: soltas, da cintura para cima, fundo limpo, com espaço em volta — porque retrato fechado não
      serve para formato vertical.
- [ ] Campanhas anteriores: o que funcionou e o que o público já reconhece.
- [ ] Referências que o cliente ama e odeia (para modelar, nunca copiar).
- [ ] Canais oficiais, dados jurídicos de rodapé, medidas de banner da plataforma de venda.
- [ ] Fontes já usadas e licenças.
- [ ] Autorização para baixar o que estiver só na web (dizer nome, origem e tamanho de cada arquivo).

## 3. Pesquisas ANTES de desenhar (em paralelo, gravando aos poucos)
Nenhuma peça começa com pesquisa de restrição ainda rodando — porque zonas descobertas depois refazem a série inteira.
- [ ] Categoria: códigos e clichês do setor, espaço vazio, o que não repetir.
- [ ] Referências do cliente: princípio de cada uma, medido, e o que não repetir.
- [ ] Fontes: voz nova, legível no celular, números seguros, licença.
- [ ] Elementos do assunto: instrumentos, documentos, medidas e dados reais do tema.
- [ ] Composições: 8–12 arquétipos para a série.
- [ ] Forma: régua de raios, bordas, sombra, quando o reto é destaque.
- [ ] Cor e arquitetura: função de cada cor, cor por produto, erro fixo, daltonismo.
- [ ] Zonas e tamanhos: interface de cada plataforma e formato.
- [ ] Imagem e IA: o que é foto real (prova) e o que é cenário.
- [ ] UX e conversão (se houver página): 1ª tela, 1 CTA, formulário.
- [ ] O que o cliente NÃO pediu mas um sistema profissional tem (forma, estados, acessibilidade, canais, jurídico,
      governança) — porque "isso você já deveria ter pesquisado" é reprovação de método.
- [ ] Lei e plataforma: publicidade, defesa do consumidor, privacidade, regras de anúncio.
Saída: uma ficha de repertório curta, antes do plano.

## 4. Decisões que o cliente toma (o estúdio propõe, não decide)
Sempre por folha comparativa: até 4–6 opções, uma recomendada com o porquê.
- Quais conceitos de logo seguem → todos os que passaram no portão seguem juntos até o checkpoint.
- Cor do logo e paleta → versões aplicadas por papel, clichês marcados.
- Cor por produto → uma por produto + uma para "todos juntos"; onde a cor-mãe NÃO aparece, escrito.
- Sistema de fontes → folha de pares + a mesma peça em cada sistema.
- Forma → folha com 2–3 combinações de raio.
- Frase com risco legal → avisar UMA vez, por escrito, manter a do cliente e registrar a decisão.
- Nome de cor, cor de erro, exceções → entram como PROPOSTA em "Decisões pendentes" até o "sim".

## 5. Ordem dos passos
1. Enquadrar: perguntas, materiais, briefing, diário.
2. Pesquisas em paralelo; enquanto isso, folhas de estudo.
3. **Logo sozinho até aprovar:** conceitos em P&B → acabamento → checkpoint → cores por papel → checkpoint → kit
   (cores + mono positivo e negativo, assinaturas, símbolo em avatar, vetor em curvas) → aprovação.
4. **Sistema:** forma → cor (com produtos) → tipo → kit de elementos revisado um a um → fundos, grão, grids → arquétipos.
5. Inventário "elemento → onde entra" antes de qualquer peça ou página.
6. **Peças uma por vez:** ficha + pré-voo zerado → montar → portões → próxima.
7. Série: folha de contato por produto, vizinhas com arquétipos diferentes, interface simulada por cima.
8. Design system e manual por último, conferidos página a página.
9. Fechar: cada correção do cliente vira regra escrita na skill NA HORA.

## 6. Erros que geram retrabalho → como evitar
- Logo "torto, desalinhado" → medir pela tinta, uma unidade (altura da maiúscula) para todos os espaços, kerning óptico a ≥ 400%.
- Letra redonda cortada no arquivo → moldura medida na tinta, não nas métricas da fonte.
- Parte do logo some numa versão → achatar classes CSS de SVG de terceiro em atributos antes de embutir.
- "Vazado" que não mostra a foto → furo real (evenodd), testado sobre foto.
- Cliente vê peça quebrada → rascunho fora da pasta do projeto; só o pronto entra lá.
- Desalinhamento sem fim → grade de verdade (layout por restrição), nunca coordenada à mão.
- Série refeita → zonas e tamanhos pesquisados antes; pré-voo rodado em TODOS os textos.
- Contraste aprovado que falha → medir o pior trecho da letra.
- Cor antiga ainda aparece → ao trocar paleta, procurar os códigos antigos em código, temas, peças e SVG com cor assada.
- Texto inventado em demo, mockup ou exemplo → só copy do cliente; sem copy, "[a definir]"; nunca preço de exemplo.
- Pessoa de IA indo para o manual → imagem de IA com pessoa nunca fica na pasta de imagens oficiais.
- Logo arredondado sem pedido → "arredondar" vale para elementos.
- Raio invisível no celular → raio de arte ≈ 2,75 × raio de site.
- Lote com itens quebrados → revisão um a um, grande, antes de mostrar.
- Duas fontes da verdade (documento × código) → uma só por decisão; trocou fonte = refazer kits.
- Arquivo movido, caminho morto → atualizar a ficha da marca e conferir todos os caminhos.
- Capítulo sumido do manual → conferir cobertura: todo bloco da ficha vira página.
- Páginas ou peças irmãs com estruturas diferentes → componente único para o que não muda, ANTES de variar.
- Tema claro como "inversão" → pares de tokens por tema desde o 1º componente, kit nas duas variantes.
- Pesquisa perdida num corte → gravar aos poucos e manter um arquivo de retomada.
- Sub-agentes em paralelo queimando limite e voltando sem padrão → 1 por vez, briefing curto, critério de aceite, estado em arquivo.
- "Zero erros" e reprovado → verificador mede layout, não gosto; somar varredura própria (cor proibida, transbordo, CTA) e olho.
- Laço infinito de correção → no máximo 2 rodadas; depois devolver dizendo o que está fraco.
- Correção que cria outro erro → reexecutar o sistema inteiro (espaçamento, margens, hierarquia) em todas as telas.

## 7. NUNCA
- Inventar ou reescrever copy, preço, número, depoimento, selo.
- Preço "de" falso, desconto inexistente, contagem ou vagas falsas.
- Alterar, arredondar ou recolorir o logo sem pedido; logo de terceiro entra oficial, monocromático e pequeno.
- Pessoa inventada por IA no lugar de pessoa real, nem como provisória.
- Levar estilo de um cliente para outro, ou de um projeto antigo para um "do zero".
- Apagar sem confirmação; baixar sem autorização; pôr teste em acervo aprovado sem pedido.
- Copiar layout, ilustração, frase ou elemento que é marca de outra empresa.
- Fonte sem prova de leitura; mais de 2 famílias por arte; zero ou O ambíguos em preço, data e cupom.
- Texto interno do estúdio (regra, nome de arquivo, código) no manual do cliente.
- Mostrar rascunho, lote sem revisão um a um ou algo não renderizado e olhado.

## 8. Como mostrar
Sempre imagem (folha de contato + 2–3 itens a 100% + miniatura a 25%), uma folha por eixo, o que foi achado e
corrigido, o que NÃO foi testado, antes × depois de qualquer mudança por conta própria, pergunta fechada com
recomendação — e PARAR no checkpoint. Imagem com até 8000 px de lado; folha alta vira várias páginas.
