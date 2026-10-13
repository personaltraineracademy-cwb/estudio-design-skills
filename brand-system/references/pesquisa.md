# Pesquisa — imersão antes de qualquer forma

Saída: `<marca>/pesquisa/pesquisa.md` (+ folhas de imagem). Rode as frentes em **subagentes paralelos** (Agent) —
cada um devolve só a síntese. Tempo-alvo: o suficiente para achar o "espaço vazio", não um relatório acadêmico.

## Frentes (paralelas)
1. **Mapa de convenções da categoria** (WebSearch/WebFetch + `gemini.py ask "…" --search`): 20–30 marcas do setor e
   vizinhos. Para cada: cor, símbolo, tipo, foto, voz, movimento. Código usado por > 40% = **dominante**.
   Regra "mantém 1, quebra 2": manter um código de entrada (para ser lida como do setor), quebrar dois de propósito.
2. **Repertório de excelência**: 8–12 identidades premiadas do setor ou vizinhas (Brand New, It's Nice That,
   D&AD, estúdios em references/dispositivos.md) — o que fazem de **sistema** (não só logo).
3. **Público e cultura**: linguagem, rituais, objetos, lugares, gírias, referências brasileiras/locais que o público
   reconhece (vernacular, modernismo brasileiro, cultura do lugar). Fonte de metáforas (references/criacao.md).
4. **Referências da pessoa**: se mandou imagens, analise cada uma com a ficha abaixo (pode usar
   `gemini.py ask "…" --img ref.jpg --json` como segunda leitura). Roube o **princípio**, nunca a superfície.
5. **Acervo e mercado (CLIP)**: `library.py search "<descrição>" --source mercado --sheet` e `library.py similar
   ref.png --sheet` — o que já existe parecido; cliente com acervo: `library.py profile <Cliente>`.

## Ficha de análise de referência
```
REF # | fonte | serve à palavra-chave: __
FORMA       geometria (ortogonal/curva/orgânica/fraturada) · primitivas · cantos · terminais
CONSTRUÇÃO  grade? módulo? compasso? gesto? simetria?
RITMO       regular / sincopado / progressivo · intervalo · repetição
PESO        leve↔pesado · onde está a massa · massa × linha
CONTRASTE   escala (1:x) · claro/escuro · cheio×vazio · fino×grosso
TEXTURA     lisa / grão / impressão (riso, offset, serigrafia) / material
COR         temperatura · nº de cores · saturação · proporção · cor do "papel"
DENSIDADE   % de respiro · níveis de hierarquia
TIPO        classe · largura · caixa · espaçamento · tratamento
IMAGEM      foto/ilustração/3D/diagrama · recorte · luz
MOVIMENTO   real ou implícito · direção · velocidade
GESTO ÚNICO: __   ROUBAR (princípio): __   NÃO ROUBAR (superfície): __   clichê do setor? S/N
```
Painel de referências: 3–4 palavras-chave; ≥ 50% das refs de **fora** do design gráfico (arquitetura, objetos,
equipamento, sinalização, natureza, música); **nada de concorrentes** no painel de inspiração (só no mapa).

## Clichês por setor (proibidos salvo forma realmente nova)
- **Fitness/academia**: halter, kettlebell, anilha, bíceps, raio, chama, swoosh/check, boneco correndo, linha de
  batimento, itálico + linhas de velocidade, preto + neon com grunge, escudo/brasão, capacete espartano, leão/gorila,
  "BEAST" condensado, degradê laranja→vermelho, hexágonos, silhueta de fisiculturista posando, braço flexionado
  (💪, também em versão robô/mecânica), mulher de perfil com halter.
- **Fitness feminino**: rosa, lótus/flor, silhueta de cintura fina, laço, coração, traço "delicado" — testar força,
  ciência ou humor no lugar.
- **Saúde/bem-estar**: coração, cruz, folha, mãos acolhendo, caduceu, lótus, DNA, cápsula, azul-turquesa, sorriso
  de banco de imagem.
- **Educação/edtech/cursos**: capelo, livro aberto, coruja, lâmpada, lápis, maçã, foguete, cérebro, quebra-cabeça,
  escada/seta de crescimento, play sobre notebook, selo dourado "Método X", louros, preto + dourado "premium",
  especialista de braços cruzados, preço riscado.
- **Eventos/summits**: globo com nós, pontos conectados, blobs de degradê, confete, cidade isométrica, ano em
  contorno, montanha para "cúpula/evento de topo", palco com feixes de luz.
- **Tecnologia/IA**: gradiente roxo-azul, cérebro de circuito, órbita, spark de 4 pontas, blob 3D brilhante,
  Corporate Memphis.
- **Finanças**: azul de confiança, teal, seta/gráfico subindo, cofre, escudo, ilustração pastel.
- **Infoproduto/marketing digital**: foguete, alvo, megafone, play, coroa, dinheiro voando, preto e dourado.

## Formato de `pesquisa.md`
```
# Pesquisa — <marca>
## Códigos dominantes da categoria (tabela: código · % · exemplos)
## Espaço vazio (o que ninguém faz) · quadrante vazio (2 eixos)
## Mantém 1 / quebra 2
## Repertório de excelência (marca · estúdio · por que funciona · princípio a roubar)
## Público e cultura (metáforas candidatas com distância 3–5 passos)
## Referências da pessoa → princípios
## Clichês proibidos deste projeto
## Fontes (URLs)
```
