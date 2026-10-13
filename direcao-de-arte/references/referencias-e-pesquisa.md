# Referências e pesquisa: como estudar, pesquisar e criar no mesmo nível (ou acima)

Regras que valem para todo cliente:
- **Nunca copiar; usar a referência para MODELAR.** Pensar por conta própria com base na biblioteca, nas referências
  e em tudo que o usuário manda.
- **Pesquisar fontes, elementos e composições de novo sempre que for criar.** O repertório antigo é ponto de partida,
  nunca o teto.
- **Criatividade sempre a serviço da experiência do cliente, da usabilidade, da leitura e da conversão.**
- Gemini (imagem) e vídeo podem ser usados à vontade quando somam.

Ferramenta: `scripts/referencia.py` (subcomandos `pdf`, `medir`, `folha`, `fontes`).

---

## Parte A. Estudar uma referência que o usuário mandou (PDF, print, link)

| # | Passo | Como | Sai |
|---|---|---|---|
| 1 | **Receber e converter** | Prints longos de página (FireShot) vêm em PDF de 1 página com várias imagens dentro. `referencia.py pdf <arquivos.pdf> -o <rascunho>` gera o PNG na resolução nativa + fatias de 2000 px para ler | `cNNN.png` + `cNNN-k.jpg` |
| 2 | **Ver tudo por partes** | Ler todas as fatias (Read), depois recortar em resolução nativa os detalhes: fonte, botão, borda, textura | anotações por seção |
| 3 | **MEDIR no código real** | Se o site está no ar: `referencia.py medir <url> -o tokens.json` lê fontes carregadas, estilos de texto, variáveis `:root`, raios, bordas, sombras, fundos (grão SVG, grades, máscaras), pseudo-elementos (`::before`/`::after`: traços, cantoneiras) e formas (`clip-path`, paths SVG). Abrir no navegador interno e conferir | `tokens.json` + `tokens.md` |
| 4 | **Separar em 3 camadas** | Para cada site/peça: (a) **o que faz**, medido; (b) **o PRINCÍPIO**, por que funciona, em 1 frase; (c) **o que NÃO repetir**: defeitos de leitura, contraste, UX e conversão que se veem | seção A/B/C… do estudo |
| 5 | **Achar o "elemento do assunto"** | A pergunta mais importante: de onde vem cada ornamento? (ex.: simetrógrafo = avaliação postural.) O que é do assunto vira princípio; o que é decoração genérica vira alerta | lista "derivado × genérico" |
| 6 | **Pesquisar o que não se sabe** | Fontes (quem fez, licença; se paga: primeiro no Adobe Fonts do plano, depois parecida no Adobe, por último grátis — `tipografia.md` §11 nº 4), técnicas (como se faz, custo, acessibilidade), evidência de UX/conversão. Disparar pesquisas em paralelo (Parte C) | `<projeto>/pesquisa/NN-*.md` |
| 7 | **Testar no olho** | Fontes: `referencia.py fontes <lista.json>`. Elementos: protótipo rápido no `palco.py` | folhas PNG |
| 8 | **Síntese: o que vale para QUALQUER peça** | Tabela "princípio → como aplicar no estúdio" | seção D do estudo |
| 9 | **Folha visual para o usuário** | `referencia.py folha <estudo.json>`: recortes numerados + princípio + o que não repetir | `_folha-estudo.png` (mostrar) |
| 10 | **Registrar** | Estudo em `<projeto>/pesquisa/NN-estudo-*.md`, recortes em `<projeto>/pesquisa/<estudo>/`, linha no índice da pesquisa, diário do projeto | — |

### A2. Página que o usuário mandou salva (pacote de captura) e pediu para REPLICAR para estudo
Réplica de estudo fica na pasta de testes e nunca vira peça; o "Proibido" abaixo vale para tudo que criamos.
- **A captura mente.** Ferramentas de salvar página perdem CSS, fontes e JS, gravam caminhos errados e congelam no
  tamanho da tela de captura o que é calculado (formas SVG, células de calendário, fontes `crossorigin` sem CORS).
  Servir a captura por um servidor de estudo que busca o que falta e guarda em cache; comparar com as telas reais
  salvas; consertar fonte e imagens na hora (sem tocar no original) antes de julgar a réplica ("comparação justa").
- Réplica escrita do zero, com tokens; o que depende de tamanho é recalculado, nunca congelado.
- Prova = original × réplica **em imagem lado a lado na 1ª entrega**, não só números: o usuário julga pelo olho.
- Cada marca estudada sai com: análise (conceito, composições dobra por dobra, elementos com função, régua),
  identidade reconstruída (logo em curvas, tokens, elementos SVG) e manual curto com 2 peças NOVAS.
- Recurso pago (fonte, foto): checagem centralizada no agente principal, por NOME (busca descritiva erra), gravada em
  arquivo; subagentes só leem o resultado.
- Revisão do agente principal olha cada peça nova grande: os agentes não viram botão encostando no rosto, traço
  lido como acento e fonte paga sem checar.

**Proibido:**
- copiar layout, ilustração, frase ou cor exata de uma referência;
- usar fonte paga sem licença;
- baixar arquivo de conteúdo sem autorização do usuário.

Reaproveitar é permitido: princípios, técnicas (sombra dura, grão em SVG, forma de pasta) e medidas genéricas.

---

## Parte B. Pesquisa NOVA a cada criação (sempre, antes de montar)

Toda peça, série, site, campanha ou identidade começa com uma rodada de pesquisa própria daquele trabalho, mesmo que
já exista pesquisa parecida. Isso entra no passo 0b do `SKILL.md`, antes da ficha e do pré-voo.

### B1. As 6 frentes (rodar em paralelo, com subagentes)
| Frente | Pergunta | Arquivo |
|---|---|---|
| **Fontes** | Quais fontes (grátis/OFL) dão a VOZ deste assunto e público, diferentes mas legíveis em celular? Pares título + texto, eixos variáveis, PT-BR, números | `<projeto>/pesquisa/NN-<trabalho>-fontes.md` |
| **Elementos** | Qual o vocabulário visual do ASSUNTO do cliente (instrumentos, documentos, gestos, lugares, dados) + tendências atuais de elementos para o tipo de peça? | `…-elementos.md` |
| **Composições** | Que estruturas de composição servem a este objetivo e formato (artes e/ou seções de site)? Cases reais recentes | `…-composicoes.md` |
| **Imagem / IA** | Que imagens contam a ideia? Onde a IA soma (cena-metáfora, cenário, textura) e onde precisa ser foto real? Receitas de prompt | `…-imagem.md` |
| **Movimento** (quando houver site ou vídeo) | Que movimento tem significado aqui? Vídeo de hero, loop para Stories, microinterações | `…-movimento.md` |
| **UX e conversão** (sempre que houver ação) | O que a evidência diz para este tipo de peça e público (formulário, CTA, prova, urgência legal) | `…-ux.md` |

Pode juntar frentes num arquivo só quando o trabalho é pequeno. Para uma peça avulsa, basta uma pesquisa curta com
as 6 perguntas.

### B2. Modelo de pedido para o subagente (copiar e preencher)
```
Pesquisa na web, só leitura (não instale, não baixe arquivos, não faça login). Português do Brasil, simples, URL ao
lado de cada afirmação; selos [oficial] [pesquisa] [mercado] [proposta]; número sem fonte = "[ponto de partida]".
GRAVE O ARQUIVO AOS POUCOS (crie já e acrescente seção por seção) em <caminho>.
Contexto: <cliente, assunto, público, peça/formato, objetivo, ideia em 1 frase, o que já existe na biblioteca>.
Antes de começar, leia os títulos de <pesquisas existentes> para NÃO repetir.
Perguntas: <frente B1 + itens específicos>.
Para cada item: o que é · 1–3 casos reais com URL · premium × cafona · custo (leitura, desempenho, acessibilidade)
· como fazer no nosso stack (HTML/CSS/SVG/numpy/Gemini) · licença.
Termine com: "Para virar ferramenta" (funções a implementar) e "Lacunas".
No fim responda: caminho do arquivo + 10 descobertas principais.
```
Cada arquivo de pesquisa cita no topo o pedido que o gerou.

### B3. Ficha de repertório da criação (sai da pesquisa, entra no plano)
Antes de montar, escrever em `<projeto>/sistema/repertorio-<trabalho>.md`:
1. **Fontes:**
   - 2–3 pares candidatos, testados na folha `referencia.py fontes`;
   - o par escolhido e o porquê;
   - os vetos (ex.: zero com traço em fonte de preço).
2. **Elementos:** 8–12 elementos derivados do assunto (origem em 1 frase cada) + 2–3 de acabamento (grão, raios,
   fios), com tokens: unidade, espessura, raios, acento.
3. **Composições:** 4–6 estruturas escolhidas, uma por peça, nunca repetidas em sequência.
4. **Imagens:** quais vêm do Gemini (com receita de prompt) e quais são fotos reais.
5. **Movimento** (se houver).
6. **UX/conversão:**
   - 1 CTA primário;
   - prova;
   - urgência só verdadeira;
   - campos do formulário;
   - leitura mínima.
7. **Referências de nível:** 2–4 imagens (do usuário ou da pesquisa) contra as quais o resultado vai ser comparado (Parte D).

---

## Parte C. Como rodar a pesquisa sem perder trabalho
- Subagentes em paralelo, um por frente, todos em segundo plano.
- **Sempre gravar aos poucos.** Se o limite de uso cortar pesquisas que só iam gravar no fim, tudo se perde. A retomada foi com `SendMessage` (o agente volta com o contexto), pedindo também que ele retome os
  sub-agentes dele em vez de criar novos.
- Enquanto pesquisam: trabalho que não depende delas (folha de estudo, amostras de fontes, conversão de PDFs).
- Ao terminar: ler o resumo de cada arquivo → congelar as regras em `references/` → atualizar o índice da pesquisa do projeto.
- Pesquisa no ar com risco de corte: deixar o estado em `<projeto>/sistema/continuar-aqui.md`.

---

## Parte D. "Mesmo nível ou acima": como provar
1. **Folha lado a lado:** a nossa peça/página ao lado de 2–4 referências de nível, no mesmo tamanho (miniatura e
   100%).
2. **Nota de 0 a 3 por critério**, para a referência E para a nossa. A nossa tem que empatar ou ganhar em todos:

| Critério | O que olhar |
|---|---|
| Tipografia com voz | fonte diferente mas legível; hierarquia clara; título que se lê a 25% |
| Cor com função | 1 acento com papel; nada de cor solta |
| Elemento do assunto | ornamentos com origem explicável; zero decoração genérica |
| Grid e ritmo | alinhamentos compartilhados; ritmo de seções/peças; respiro |
| Acabamento | grão único; família de raios; fios e espessuras coerentes; borda limpa |
| Imagem | metáfora clara; luz crível; nada de "cara de IA"; pessoa real quando é a prova (professor, cliente, equipe) |
| Leitura e UX (medido) | contraste no pior pixel, texto mínimo, zonas da interface, 1 CTA primário, formulário curto |
| Conversão | o que, quando, com quem na 1ª tela; prova perto do CTA; urgência verdadeira |

3. Onde a referência ganha: escrever por quê e corrigir antes de mostrar.
4. O nosso diferencial obrigatório é **medir o que eles não mediram**: contraste, tamanho mínimo e zonas.

---

## Parte E. Onde guardar
| O quê | Onde |
|---|---|
| Estudo de referência | `<projeto>/pesquisa/NN-estudo-<tema>.md` + `<projeto>/pesquisa/<estudo>/` (recortes e folhas) |
| Pesquisa de uma criação | `<projeto>/pesquisa/NN-<trabalho>-<frente>.md` |
| Ficha de repertório | `<projeto>/sistema/repertorio-<trabalho>.md` |
| Regras que servem a todos | `references/*.md` desta skill |
| Índice | `<projeto>/pesquisa/LEIAME.md` (uma linha por arquivo: data, o que responde, onde virou regra) |
| Rascunhos e PDFs convertidos | `%TEMP%\<projeto>-rascunho\` (fora do projeto) |
