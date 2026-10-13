# Criação — como chegar no que ainda não existe

Princípio: **a primeira ideia é a ideia da categoria.** IA melhora cada peça e deixa todas parecidas (Doshi & Hauser
2024; "Artificial Hivemind", NeurIPS 2025). Por isso o processo força divergência antes de convergir.

## 1. Procedimento anti-colapso (rodar em toda ideação)
1. Escreva as 5 ideias óbvias da categoria e **proíba-as** explicitamente.
2. **Verbalized Sampling**: "liste 15 conceitos com a probabilidade de um designer médio propor cada um" → fique com
   os < 10% (aumenta diversidade 1,6–2,1×).
3. **Gere 20, mate 17**: morre o que está na lista de clichês, falha no teste da troca, CLIP ≥ 0,88 contra o mercado
   (`library.py novelty`), ou não gera sistema.
4. **Quadrante vazio**: concorrentes em 2 eixos (geométrico↔orgânico, silencioso↔ruidoso) → mire o vazio.
5. **Restrições sorteadas**: 2 cartas (abaixo) por território, semente registrada. 2–3 restrições duras, nunca 10
   (curva em U invertido — Acar et al. 2019).
6. **Uma escola por território** (lista abaixo), sem repetir.
7. **Cruzar domínios distantes** (§2.1). Proibido adjetivo vago ("moderno", "clean", "futurista", "vibrante"):
   troque por material, processo, época ou regra formal.
8. **Imagem só depois do conceito.** Conceito em palavras + esboço vetorial; Gemini/3D depois.
9. **Ciclo de crítica visual**: renderizar → ler o PNG → rubrica + sinais de IA → mudar UMA variável → repetir.
10. **Documento de decisões** (brand.json) reenviado a cada etapa, para o genérico não voltar.
11. **Teste "cola em qualquer marca"**: se o elemento iria para outra marca sem mudar nada, é genérico.

## 2. Métodos de conceito (escolha 2+ por projeto)
1. **Mistura conceitual** (Fauconnier/Turner): entrada A = verdade da marca; entrada B = domínio a 3–5 passos
   (música, cartografia, tipografia de jornal, engenharia de pontes); espaço genérico = estrutura comum (sequência,
   tensão, repetição, carga); mistura = algo novo ("treino como partitura" → pautas e compassos). Perto demais =
   clichê; longe demais = ruído. Só fica se gerar **sistema**.
2. **Lateral (de Bono)**: provocação "PO" (fuga, inversão, exagero, distorção, desejo — "academia sem peso"),
   extraia o movimento/princípio, 3 formulações antes de julgar. **Entrada aleatória**: substantivo concreto →
   5 propriedades → ligar cada uma ao problema.
3. **Cartas (estilo Oblique Strategies, adaptadas)**: trate o erro como intenção · use uma cor "inaceitável" para a
   categoria · troque o específico por ambiguidade · só um elemento de cada tipo · amplie o defeito · faça a versão
   chata e subtraia · inverta figura e fundo · troque a escala · o que a categoria nunca faria? · só tipografia ·
   uma única primitiva · 1 cor + papel · tudo numa grade 5×5 · use o ângulo do nome · o símbolo é um verbo ·
   o logo é um contêiner · a regra é o logo · dados reais viram forma · uma letra muda, o resto fica.
4. **SCAMPER no código dominante**: substituir (o halter pelo som dele) · combinar (letra + gesto) · adaptar (de outro
   domínio) · ampliar (recorte gigante) · dar outro uso (o logo vira grade) · eliminar (sem símbolo) · inverter
   (espaço negativo).
5. **Caixa de Zwicky**: colunas — tipo de marca · origem da forma (letra, numeral, objeto, gesto, diagrama, dado,
   lugar) · construção (grade, compasso, corte, dobra, traço manual, pixel) · tratamento (sólido, linha, vazado,
   faixa, textura) · movimento (estático, cinético, variável) · cor · classe tipográfica. Sorteie, elimine o
   incoerente, pergunte "por que isso não existe?".
6. **Gerstner — programas, não soluções**: desenhe a **regra paramétrica** que gera as peças (`sketch.py`,
   `elements.py`), não uma peça.
7. **Saber do assunto** (obrigatório em curso, pós, produto técnico, serviço especializado): ementa → 10 coisas que só
   quem estuda isso conhece (ferramenta, medida/razão, lei, protocolo, gesto técnico, erro clássico, número, gíria) →
   cada uma vira letra, símbolo de 3–5 formas ou sistema (estados, módulos, animação). Ex.: acento de uma letra como
   instrumento de medida; proporção famosa; sigla com duplo sentido. Checklist: `../brand-studio/references/logo-anticliche.md`.

## 3. Quatro territórios (internos) → 2–3 rotas (para a pessoa)
Cada território = ideia + escola + metáfora + 2 restrições sorteadas, e **testado em peças reais** (não só logo).
Territórios típicos: letra/numeral próprio · metáfora/gesto · sistema/regra · lugar/dado/cultura.

## 4. Dezesseis escolas e suas regras formais (uma por território)
1. **Bauhaus** — primitivas + primárias, construção à vista, zero ornamento.
2. **Construtivismo russo** — diagonais fortes, vermelho/preto, fotomontagem, tipo em blocos.
3. **Suíço (Müller-Brockmann)** — grade modular rígida, grotesca, alinhado à esquerda, assimetria, foto objetiva.
4. **Ulm/sistêmico (Aicher)** — programa total, grade, pictogramas à essência, paleta testada com intenção.
5. **Holandês funcional (Crouwel/Total Design)** — grade às vezes visível, letras modulares; desvia quando melhora.
6. **Japonês moderno (Tanaka, Hara)** — vazio como ativo, formas planas, cor chapada, assimetria calma, papel.
7. **Concretismo brasileiro (Wollner, Ruptura)** — geometria como clareza, signo que funciona sem o nome.
8. **Modernismo cultural brasileiro (Aloísio Magalhães)** — rigor moderno + repertório brasileiro, sistema total.
9. **Vernacular brasileiro (letreiramento popular; Finizola)** — letra pintada, cor saturada, sombra chapada, filetes.
10. **Tropicália/psicodelia brasileira** — curvas líquidas, cores vibrando, letra deformada, colagem.
11. **Escola polonesa de cartaz** — metáfora visual pintada, letra manual, humor sombrio, uma imagem central.
12. **New Wave/pós-moderno (Weingart, Greiman)** — camadas, espaçamento extremo, quebra de grade, textura.
13. **Memphis** — padrões geométricos, pastel+primárias em choque, ironia (nunca a versão corporativa).
14. **Punk/DIY/xerox** — recorte, colagem, alto contraste, grão de fotocópia.
15. **Brutalismo gráfico** — grotesca crua, grade exposta, cor de sistema, hierarquia por tamanho bruto.
16. **Op Art/cinetismo (Vasarely, Palatnik)** — padrões que vibram, ilusão de movimento, P&B preciso.

## 5. Sinais de "IA genérica" (reprovar na crítica)
- Fontes-padrão: Inter, Roboto, Arial, Space Grotesk, Poppins, Montserrat sem motivo; a mesma escolha toda vez.
- Cor: gradiente roxo sobre branco; creme + serifa + terracota; **quase-preto + um único destaque ácido** (atenção:
  é a fórmula de alguns clientes — se usar, a marca precisa de outro ativo próprio forte); gradiente neon; blob 3D.
- Layout: número grande + rótulo pequeno + gradiente; cards iguais de canto arredondado com sombra cinza; rótulos
  em CAIXA ALTA espaçada em tudo; "·" entre metadados; seta no fim de todo link; destacar 1 palavra do título.
- Logo: ícones de banco recombinados; espaçamento perfeito demais; tipografia sem nenhuma intervenção; dois ícones
  empilhados; **corpo literal da categoria** (silhueta de atleta, mulher de perfil com halter, braço flexionado) ou
  figura com cara de foto vetorizada; três linguagens no mesmo símbolo (contorno + sólido + anel).

## 6. Repertório brasileiro (fonte de originalidade)
Cultura de fonte própria (Plau: Canal Brasil, Guanabara Sans; FK Olympikus; fonte do MASP tirada do concreto) ·
herança modernista (Niemeyer, Brasília, Burle Marx) · sistemas tirados do lugar (FutureBrand: rios da Amazônia viram
letras) · vernacular (placas pintadas, rótulos de cachaça, caixas de feira em flexografia, carrancas — cuidado com
pesquisa rasa "estilo Pinterest" e riso em excesso).

## 7. Lições que viram regra
Rand: o logo identifica, não precisa contar tudo · Olins: identidade é tudo que a organização faz · Bierut: a
resposta está escondida no problema e só aparece quando a 1ª ideia é rejeitada · Scher: repertório acumulado é
insumo · Sagmeister: o conceito precisa provocar reação · Crouwel: sistema primeiro, desvio consciente depois ·
Aicher: cor tem significado, testar e justificar · Wollner: teste o símbolo sozinho · Gerstner: critérios explícitos
antes de desenhar · Vignelli: 1–2 famílias, corte o modismo · Chermayeff & Geismar & Haviv: apropriada, distintiva,
simples — com uma estranheza controlada · Hara: o vazio é ativo · Albers: cor muda com a vizinha — teste em contexto.
