# Receitas de produção — o passo a passo que chegou nos resultados do estúdio

Cada receita = ordem real usada, comandos e onde estão as regras. Caminhos relativos à pasta `skills/`.
Antes de tudo: `python brand-studio/scripts/doctor.py` (o que falta: `references/instalacao.md`).
Toda receita termina no protocolo `revisao-de-design/SKILL.md` (máx. 2 rodadas de correção).

## Contents
1. Logo do zero até o kit
2. Identidade completa (sistema, manual, design system)
3. Kit de elementos gráficos
4. Foto de pessoa pronta para peça ou site
5. Imagem de IA (cenário, textura, complemento)
6. Peça premium em camadas (post, story, anúncio)
7. Série sem template
8. Mockups
9. Animação de logo
10. Site / página de captura
11. Entrega para outros designers
12. Quanto custa e quanto demora

## 1. Logo do zero até o kit (brand-studio)
1. Briefing ≤ 6 perguntas; "carta branca" → suposições escritas.
2. Repertório: `library.py search "<descrição>" --sheet r.png` + referências do cliente com `library.py similar`.
3. 20–30 ideias em 4 territórios → 3–4 conceitos; logo de curso/produto: 10 saberes do assunto (`logo-anticliche.md`).
4. Construir em curvas: `fonts.py get "Família:peso"` → `lockup.py spec.json` (texto vira curva, kerning GPOS);
   símbolo à mão em SVG ou `sketch.py run <sketch> --seeds 1-36` e redesenhar o melhor acidente.
5. Portão: `library.py novelty cand.png` (< 0,93) · `logo_qc.py "*.svg" --sheet qc.png` · `svg_audit.py` · 16 px.
6. Folha de conceitos → **parar e esperar a escolha**.
7. Kit: `lockup.py` (5 colorways) → `pattern.py` → `seal.py` → `keyvisual.py` → `motion.py` → `export_variants.py`.

## 2. Identidade completa (brand-system)
`brand.py init` → pesquisa → plataforma (sem cor) → **primeiro impacto em 15–20 min** (3–4 símbolos, `palette.py
build`, `typesys.py try`, `elements.py build`, `modelos.py kit`, `board.py`) → logo aprovado → sistema (`palette.py`,
`typesys.py`, `elements.py`, `brand.json.products` se houver linhas) → **kit de elementos (receita 3)** → modelos de
peça (`modelos.py kit`) → variações com teto (`variacoes.py`) → `apply.py stress` → `mockup.py make` →
`tokens.py build` (olhar `tokens/demo.png`) → `manual.py build --qa-only` até zerar → `manual.py build`.
Regra de ouro: `brand.json` é a fonte da verdade; nada retocado à mão.

## 3. Kit de elementos gráficos (direcao-de-arte) — ANTES de qualquer peça
1. Ficha da marca: uma função que devolve `Ficha(fundo, tinta, acento, sobre_acento, raio, …)` (campos em
   `direcao-de-arte/scripts/ornamentos/nucleo.py`; exemplo pronto: `ficha_exemplo`). Prévia do catálogo:
   `python -m ornamentos.catalogo -o <pasta> --revisao` (dentro de `direcao-de-arte/scripts`).
2. Revisar **um a um**, grande (~760 px) e em miniatura no fundo oposto, com `ornamentos/_revisao/CRITERIOS.md`;
   efeito que parece erro sai. Quantidade média: só o que as peças vão usar.
3. Inventário "elemento → onde entra" → `python -m ornamentos.exportar <saida> --ficha meu_modulo:minha_ficha --zip`.

## 4. Foto de pessoa pronta para peça ou site
1. Pedir foto **solta, da cintura para cima, com espaço em volta, fundo simples** (retrato fechado não cabe no 9:16).
2. Recorte: `imaging.py cutout foto.jpg -o p.png --model u2net_human_seg` (cabelo difícil: `birefnet-portrait`).
3. Foto pequena: `imaging.py upscale p.png -o p4x.png` (Real-ESRGAN).
4. Várias pessoas na mesma peça: normalizar ANTES de compor — mesmo tamanho de rosto (YuNet), mesmo P&B
   (percentis 2–99, mesma curva), corte na mesma linha com fade de alfa na base.
5. Centrar pela tinta (contorno real), sem halo; grão único na série (`fx.py in.png out.png grain:0.05`; site: 0,55,
   0,38 em fundo escuro).
6. Edição de rosto por IA só com termo de imagem que cite IA. Nunca gerar pessoa.

## 5. Imagem de IA (cenário, textura, complemento) — opcional, pago
1. Ideia gráfica primeiro; IA só onde o código não alcança (cenário complexo, ilustração técnica).
2. Prompt de diretor de arte (assunto, luz, lente, material, espaço livre para texto, "sem texto"); modelos e 12
   prompts prontos: `direcao-de-arte/references/ia-imagem-video.md`.
3. Teste barato: `gemini.py gen "…" -o out/x --model banana21 --n 1 --size 1K`; escolhido → refazer em `2K`.
   Com referência: `gemini.py edit ref.jpg "…"`. Elemento isolado: `--element --cutout`.
4. Tratar: mesmo grão/contraste das fotos reais (`fx.py`); rótulos e números sempre em código por cima.
5. Mostrar como **proposta ao lado da base**. Custos: `gemini.py usage`.

## 6. Peça premium em camadas (direcao-de-arte)
1. Pesquisa nova curta + ficha de repertório (`direcao-de-arte/references/referencias-e-pesquisa.md`).
2. Plano por escrito (`plano.py`): área útil (margem ∩ zonas do app) → grade → camadas 0–7 → hierarquia; inventário
   de elementos; orçamento de altura somado.
3. Montar em HTML/CSS no `palco.py` (Chrome): texto aparado na maiúscula, fontes variáveis, numerais tabulares;
   fundo com `fundos.py` (sem banding) e efeitos com `efeitos.py`.
4. Portão: avisos do palco = 0 → `camadas.py peca.html --formato story` (contraste no pixel, tangentes, rosto,
   palavra atrás da pessoa, ritmo, herói) → `interface.py peca.png` (interface do app por cima).
5. Olho a 100% e 25% → régua → `julgar.py peca.png --tipo peca` (2ª opinião, opcional).

## 7. Série sem template
8–12 arquétipos de composição (`direcao-de-arte/references/composicoes.md`), vizinhas sempre diferentes, variação
com significado (produto, pessoa, edição). Uma folha de contato da série; CLIP entre pares < 0,92.

## 8. Mockups
`mockup.py make <marca> --presets poster,celular,outdoor --size 2K`: o Gemini gera só a cena com superfície em
branco; o código encaixa a arte exata com perspectiva e luz. A IA nunca redesenha a marca. Sem Gemini: `mockup.py
place cena-propria.png arte.png`.

## 9. Animação de logo
`motion.py --symbol s.svg --wordmark w.svg -o out/sting` (HyperFrames + GSAP → MP4 com FFmpeg). Uma linguagem de
movimento por marca, curta, e o quadro final = logo parado.

## 10. Site / página de captura (criacao-de-sites)
Entradas (identidade, copy final, fotos recortadas) → kit de elementos → `site.py new <pasta> --marca brand.json
--copy copy.json --install` → dobra pelo contrato (`criacao-de-sites/references/padrao-de-pagina.md`) → seções →
movimento → `site.py check <pasta>` (0 erros) + `varredura.py` + olhar rolando em 390/768/1024/1440 → `site.py pack`.

## 11. Entrega para outros designers
`brand-system/scripts/entrega.py <projeto>` (pasta única, atual, explicada) · elementos: `ornamentos.exportar --zip`
· prints atuais de páginas: `criacao-de-sites/scripts/previas.py`. Nunca entregar prévia de rodada antiga.

## 12. Quanto custa e quanto demora (referência)
| Etapa | Tempo-alvo | Custo |
|---|---|---|
| Primeiro impacto de identidade | 15–20 min | grátis |
| Logo: 3–4 conceitos revisados | 30–60 min | grátis |
| Peça premium em camadas | 20–40 min | grátis (+ ~US$ 0,05 por imagem de IA em 2K) |
| Mockups (4 cenas 2K) | 10 min | ~US$ 0,40 |
| Manual + design system | 1–2 h | grátis |
| Página de captura | 2–4 h | grátis (hospedagem à parte) |
Regra de custo de tokens: `revisao-de-design/references/economia.md`.

## IA como palco em peças (resumo; detalhes em `../../direcao-de-arte/references/ia-imagem-video.md` §12)
1. Cinemagraph: quadro-chave = primeiro = último quadro, câmera travada no prompt, máscara de borda suave sobre o PNG parado (FFmpeg `alphamerge` + `overlay`).
2. Pessoa real + cenário de IA: medir a luz da foto (direção, dureza, temperatura, altura de câmera) e escrever no prompt; fechar com sombra de contato, light wrap 6–10 px e cor casada em LAB.
3. Reels/anúncio: o evento visual acontece no 1º segundo; último quadro = primeiro; todo texto em código dentro da zona de anúncio Meta (14 % topo, 35 % base, 6 % lados).
5. Rótulo de IA (testado): a imagem crua do Nano Banana vem em JPEG com credencial C2PA (+ marca invisível SynthID nos
   pixels), mas `gemini.py` regrava com PIL e a composição/exportação também apagam o C2PA. Logo, NÃO contar com o
   rótulo automático da Meta: peça ou Reels feito em boa parte com IA (cena realista, pessoa, fato) → marcar à mão a
   opção "rótulo de IA" ao publicar. Cenário claramente ilustrativo sob arte em código: avaliar caso a caso.
4. Texto em superfície do cenário (placa, tela, papel): verde chapado na geração → `cv2.getPerspectiveTransform` + `warpPerspective` da arte renderizada em 2×.
