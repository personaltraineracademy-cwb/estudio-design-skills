# Briefing — perguntas e ficha

Pergunte **numa única mensagem**, no máximo 6 perguntas (use AskUserQuestion quando houver opções claras). Antes de
perguntar, preencha o que já dá para inferir (nome, cliente, contexto da conversa, perfil e fichas do cliente) e pergunte só o que falta.
**Exceção — "do zero" / "iniciar do 0":** perguntas NEUTRAS, nada pré-preenchido do perfil, de testes antigos ou de
campanhas passadas (nem cor, nem estilo, nem elemento). O perfil vira só repertório e filtro de originalidade depois
(senão o projeto novo herda, sem querer, a cara do antigo).
Se o usuário disser "decide você", siga com suposições explícitas.

## Perguntas essenciais (escolha as que faltam)
0. **Cliente/empresa** (já está na biblioteca? tem marca-mãe?).
1. **Nome exato** (grafia, acentos, caixa) e **linhas secundárias** (tagline, endosso, edição/ano).
2. **O que é**: marca nova · sub-marca de uma marca-mãe · campanha sazonal · evento · curso/pós/mentoria · produto digital.
3. **Público e promessa** em uma frase (para quem, que transformação).
4. **3–5 adjetivos** de personalidade (ex.: urgente, premium, acolhedor, técnico, rebelde).
5. **Onde vai viver**: feed/stories, site, tela de evento, camiseta, certificado, impresso, vídeo.
6. **Restrições**: cor obrigatória/proibida, endosso da marca-mãe obrigatório?, prazo, referências que ama/odeia
   (pode mandar imagens/links).

## Perguntas de aprofundamento (só para marca nova ou quando o briefing for vago)
- Concorrentes ou marcas que o público já conhece (para fugir).
- Existe uma história/origem/ritual que só essa marca tem? (fonte de conceitos não literais)
- Precisa de co-branding com quais marcas?
- Vai precisar de animação, padrão, selo, mascote?

## Ficha do briefing (escreva em `<projeto>/briefing.md` e mostre resumida)
```
Nome: …            Tipo: …            Público/promessa: …
Adjetivos: …       Usos principais: …  Endosso/co-branding: …
Cores: proposta … (fórmula do perfil do cliente, se houver; checar `library.py colors --client …`)
Restrições: …      Referências: …      Suposições: …
Critério de sucesso: lido em 1 s · reconhecível a 16 px · funciona em 1 cor · não parece nada do acervo nem do mercado
```

## Lições de projetos reais
- **Pergunte só o que muda a FASE atual** (fase de logo não pergunta de peça, preço ou manual).
- **Arquitetura logo no início:** "há produtos, linhas, cursos, noites ou edições que pedem cor/variação própria? há
  marca-mãe que endossa? há logos de terceiros (pós, parceiros) que entram?" (uma cor reprovada pode voltar
  como cor de produto se isso não for perguntado cedo).
- **Peça logo os materiais:** copy oficial (documento da campanha), datas, logos oficiais de terceiros em SVG, e
  **fotos SOLTAS de cada pessoa** (da cintura para cima, com espaço em volta, fundo simples) — retrato fechado não cabe
  no 9:16; + termo de imagem que cite IA se a foto for editada.
- **Copy do cliente é intocável.** Risco legal (CONAR, Meta, CDC) se avisa UMA vez, por escrito, com a fonte; a
  decisão do cliente fica registrada no projeto (ex.: `campanha.json → observacao`) e não se volta ao assunto.
- **Quando o cliente não souber responder:** folha de variações com limite e a recomendação marcada (`../brand-system/
  references/variacoes.md`).
- **Usuário leigo / "decide você" em tudo / "nada me chamou atenção":** leigo não sabe dizer o que quer, mas sabe
  ESCOLHER entre opções prontas. Antes (ou depois de uma rodada recusada) mostrar um **teste de gosto**: o MESMO nome
  em 6 "caras" bem diferentes (clássica · minimalista · artesanal/carimbo · ousada/cartaz · divertida · tradicional),
  cada uma com fonte + cor + 1 detalhe, numeradas, e pedir "qual você levaria? e qual nunca?" (2 respostas). O
  escolhido e o rejeitado viram o briefing de estilo; os conceitos novos nascem DENTRO da cara escolhida. Só pergunta
  obrigatória: "o que você vende/faz?" — o resto vira suposição escrita.
- **Leigo não julga desenho em preto e branco solto**: no checkpoint, mostrar cada conceito também aplicado em 1 lugar
  real (fachada, embalagem ou avatar do Instagram) e na cor provisória da cara escolhida.
