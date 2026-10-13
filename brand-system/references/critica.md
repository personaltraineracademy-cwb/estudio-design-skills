# Crítica — perguntas de diretor e checklist de identidade

Nota, níveis, olho e limite de 2 rodadas: protocolo único em `../revisao-de-design/SKILL.md` (régua em `../revisao-de-design/references/regua.md`). Aqui ficam só as perguntas e o checklist próprios de identidade.

## Perguntas de diretor(a) de criação
1. Qual é **a única coisa** que fica? Dá para descrever ao telefone?
2. Eu gosto antes de alguém explicar? O acabamento esconde pensamento fraco?
3. Passa no teste da troca (com o nome do concorrente) e no do nome coberto?
4. A assinatura vem de uma verdade desta marca ou serviria a qualquer uma do setor?
5. A ideia mora no sistema ou só no logo? Funciona sem o logo?
6. O que o concorrente nunca faria? O que matamos agora?
7. Aguenta 16 px, uma cor, movimento, co-branding e uma submarca não prevista?
8. O que é fixo e o que varia — quem pode variar e até onde?
9. Ela se mexe e soa de um jeito próprio?
10. Daqui a 5 anos, uma equipe interna usa sem o estúdio?
11. Estou reagindo a gosto pessoal ou ao mérito?
12. O símbolo vem do que a marca **sabe/ensina** ou do corpo/objeto da categoria? (curso/pós: qual saber da ementa?)

## Checklist técnico antes de mostrar
- [ ] Masters em curvas: sem `<text>`, `<image>`, filtros (`logo-design/scripts/svg_audit.py`).
- [ ] `brand-studio/scripts/logo_qc.py`: cada colorway com **fundo declarado** (existe positivo e negativo), nada vaza
      do viewBox, borda ampliada sem letra cortada para justificar bloco, escada 24–64 px olhada.
- [ ] Texto do logo revisado como código: acentos, hífen × travessão, maiúsculas no meio da frase (ex.: acento faltando,
      travessão no lugar de hífen).
- [ ] Símbolo com uma linguagem só e peso compatível com o nome (traço ≥ peso do descritor); versão curta sem
      descritor para < 48 px.
- [ ] `library.py novelty` em símbolo/primitiva e boards: nada ≥ 0,93; 0,88–0,93 comparado no olho.
- [ ] `palette.py build` sem aviso de texto ilegível; cor de marca clara nunca como texto sobre claro.
- [ ] `apply.py stress` olhado: favicon, 1 cor, foto movimentada, story.
- [ ] Nenhum sinal de IA genérica (criacao.md §5); nenhuma fonte-padrão sem justificativa.
- [ ] Cada dispositivo com **nome e regra de uso**.
- [ ] Tudo foi renderizado e **olhado** (Read no PNG) — nunca mostre o que não viu.
- [ ] Composição (references/modelos.md §5): acento/cedilha/vírgula sem encostar na linha de baixo · nenhuma linha
      terminando em palavra de 1–2 letras · nada de palavra girada pequena · texto nunca sobre a foto · elemento sem
      colidir com o título · sem metade da peça vazia · letras em pontos legíveis (O ≠ D).
- [ ] Foto sem cara de banco de imagem: idade do público, gesto espontâneo, ninguém posando para a câmera.
- [ ] Toda peça saiu de um **modelo** (modelos.py) — refeita com outro texto, continua certa.
- [ ] Diário atualizado (o que mudou, por quê, o que falhou).
