# 35 movimentos de composição (com parâmetros de código)

Detalhes, porquês perceptivos e exemplos: pesquisa de papel e composição (1 §2).

**Regra de série:** registre os movimentos de cada peça (`plano.json`). Peças vizinhas nunca repetem o mesmo par.
Cada peça usa 1 movimento principal + no máximo 2 de apoio.

| ID | Movimento | Parâmetros de código | Quando |
|---|---|---|---|
| M01 | **Salto de escala** | maiúscula do título ÷ maiúscula do corpo ≥ 6 (social ≥ 4); 3 tamanhos; ≤ 2 itens no maior | chamada de 1–4 palavras, número, nome |
| M02 | **Corte fora do quadro** | 15–40% do elemento fora; 1–2 bordas; ≥ 60% de cada letra visível; nunca cortar acento/til; 1ª letra inteira | marca já reconhecível; séries |
| M03 | **Vazio extremo** | herói ≤ 12% da área; vazio ≥ 60%; herói fora do centro | categoria barulhenta (Black Friday) |
| M04 | **Uma imagem, zero penduricalho** | ≤ 3 elementos (imagem, frase, assinatura) | a ideia cabe numa imagem |
| M05 | **Numeral-herói** | numeral ≥ 60% da altura; + corte ou foto dentro | datas, contagem, preço, "1 = 2" |
| M06 | **Grade assimétrica** | 12 col; divisão 5\|7, 4\|8 ou 3\|9; margem externa = 2× interna | sempre que o reflexo for centralizar |
| M07 | **Grade à mostra** | linhas a 8–20% de opacidade; formas nos módulos | sistema, dados, transmissão |
| M08 | **Modular + 1 quebra** | N×M módulos; exatamente 1 quebra num atributo | grades de professores, agenda |
| M09 | **Camada de comentário** | base na grade; 2ª camada ±3–8°, sobrepõe 10–30%, cor de ação | comparativo, antes/depois |
| M10 | **Repetição com 1 quebra** | 8–40×; 1 diferente, fora do centro | fundos, padrões, ritmo |
| M11 | **Diagonal/cunha** | 15–35°; texto no mesmo ângulo | esporte, velocidade (usar pouco) |
| M12 | **Rotação 90° / lombada** | 90°, colado à borda (0–2%) | informação lateral, moldura |
| M13 | **Sujeito na frente do título** | camadas fundo → título → recorte → assinatura; o recorte cobre ≤ 25–35% do título, nunca a 1ª letra | retrato + nome |
| M14 | **Imagem dentro da forma** | máscara = glifo/símbolo; haste ≥ 18% da maiúscula; título ≥ 200 px de maiúscula | letra grossa + foto forte |
| M15 | **Faixa de enunciado sobre foto** | foto dessaturada; 1 faixa que cruza o sujeito; 3–7 palavras | manifesto, frase direta |
| M16 | **Sobreimpressão** | multiply; 2–3 cores; registro deslocado 0,5–2% | textura gráfica, riso |
| M17 | **Colagem** | 3–6 fragmentos; recorte duro; 1 fio condutor | arquivo, documento |
| M18 | **Objeto 3D herói** | `render3d.py`; 3–5 câmeras como eixo da série | símbolo físico |
| M19 | **Tipografia mista "de rua"** | 2–3 larguras; caixa-alta; entrelinha 0,8–0,9 (com acento: pela tinta); linhas justificadas | cartaz tipográfico |
| M20 | **Larguras programadas** | eixo `wdth`/`wght` por palavra = f(semente, comprimento) | fonte variável com eixo |
| M21 | **Forma que nasce do assunto** | contorno real → simplificar → glifos/símbolo | dado, mapa, objeto do tema |
| M22 | **Símbolo do logo vira palavra** | 1 substituição por peça | logo com glifo forte |
| M23 | **Neutralidade deliberada** | 1 família neutra, 2 pesos; o contraste vem da escala | quando a ideia é a imagem |
| M24 | **Paleta curta** | ≤ 3 cores + neutro; hierarquia funciona em cinza | sempre |
| M25 | **Par improvável** | par pré-aprovado com contraste medido; 1 por peça | quebrar o código da categoria |
| M26 | **Cor como dado** | cor = f(variável real: noite, fase) | séries com sentido |
| M27 | **Moldura responsiva** | linha que encosta nas caixas do conteúdo; espessura fixa | sistemas editoriais |
| M28 | **Visor/colchetes** | 2–4 cantos; cor = contexto | enquadrar UMA coisa |
| M29 | **Logo-gerador com limite** | semente + restrições; conjunto aprovado de 12–48 | convites, séries grandes |
| M30 | **Forma-mãe → padrão** | `elements.py explore` do símbolo; 2–3 operações só | fundos e padrões |
| M31 | **Primitiva estirada** | 1 forma × {largura, altura, cor} | vinhetas, motion |
| M32 | **Supergráfico** | ângulo e proporção fixos; sangra em 2+ bordas | ambientes, fundos |
| M33 | **Logo que reage ao momento** | estados do símbolo; teste em 16 px | datas, fases |
| M34 | **Amador de propósito** | flash, 2–5° torto, sem retoque | autenticidade (raro) |
| M35 | **Movimento com intenção** | easing tirado do assunto; mesma curva em todas | vídeo, live |

## Combinações propostas (a confirmar na prática; marcar aqui quando aprovadas por cliente)
- **M13 + M02:** nome gigante cortado atrás do professor recortado.
- **M05 + M14:** "1 = 2" com foto dentro do numeral.
- **M03 + M28:** campo vazio do tema com um visor pequeno e ● AO VIVO no canto.
- **M07 + M08:** multiview: grade de monitores + o monitor "no ar" como quebra.
- **M17 + M15:** documento com tarjas sobre papel + uma faixa de enunciado.
