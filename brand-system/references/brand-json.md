# brand.json — a fonte da verdade (todos os scripts leem daqui)

Um arquivo por marca, na raiz da pasta do projeto. `palette.py`, `typesys.py`, `tokens.py`, `manual.py`, `modelos.py`…
leem e escrevem aqui; nada se decide fora dele (uma fonte da verdade por decisão — se
o código, o `campanha.json` e o `brand.json` dizem pesos de fonte diferentes, alinhe os três e escreva o dia).
**O texto é do cliente**: o script só diagrama; dado que falta aparece como `[a definir]` (nunca texto de exemplo).

## Esqueleto (campos clássicos)

```jsonc
{
  "name": "Nome", "slug": "nome", "client": "Cliente (pasta em biblioteca/)", "status": "teste", "mode": "antes",
  "briefing": {"what": "", "audience": "", "promise": "", "touchpoints": [], "competitors": [], "references": [],
               "must": [], "must_not": [], "assumptions": []},
  "platform": {
    "onlyness": "Nome é a única … que … para … em … numa era de …",
    "idea": "frase com verbo", "enemy": "o que recusamos",
    "zag": {"keep": "código mantido", "break": ["código quebrado 1", "código quebrado 2"]},
    "tension": [["preciso", "frio"], ["intenso", "agressivo"]], "personality": ["…"],
    "principles": [{"name": "", "rule": "com número", "do": "", "avoid": "", "test": ""}],
    "jobs": {"funcional": "", "emocional": "", "social": ""},
    "assets": ["ativo distintivo 1", "ativo 2"],
    "voice": {"is": [], "is_not": [], "examples": ["frase real"],
              "matrix": {"canais": ["anúncio", "aula", "suporte", "redes"],
                         "linhas": [{"principio": "direto", "niveis": ["alto", "médio", "alto", "alto"]}]}}
  },
  "logo": {"primary": "logo/x-horizontal.svg", "secondary": "", "symbol": "", "secondary_symbol": "", "wordmark": "",
           "clearspace": 0.5, "clearspace_rule": "texto", "min_px": 24, "min_mm": 8, "min_px_rule": "texto",
           "min_px_symbol": 32, "construction": "texto curto", "dont": ["…"],
           "concepts": [{"id": "", "name": "", "idea": "", "symbol_idea": "", "font_in_curves": ""}],
           "variants": {"nome": "…"}, "colorways": {"kit_completo": "…"}},
  "color": {"seeds": {"brand": {"hex": "#…", "name": "Nome próprio"}, "ink": {…}, "paper": {…}, "accent": {…}},
            "proportion": {"paper": 50, "ink": 30, "brand": 15, "accent": 5}, "rules": ["…"],
            "accent_decisao": "texto", "proportion_rule": "texto",
            "error": {"escuro": "#FFB4AB", "papel": "#9E1B32", "regra": "texto", "status": "proposta — …"},
            "palette": "← escrito por palette.py (ramps, roles light/dark, seed_step)"},
  "type": {"display": {"family": "Família Google Fonts", "weight": 800}, "text": {"family": "", "weight": 400},
           "mono": {"family": "", "weight": 400}, "anchor": {"family": "", "weights": [600, 700]},
           "scale": {"base": 16, "ratio": 1.25}, "tracking_display": -0.02,
           "rules": ["…"], "custom": "letra/numeral próprio (arquivo)", "levels": "← typesys.py"},
  "grid": {"columns": 12, "margin": 0.06, "gutter": 0.02, "baseline": 8, "angle": 45,
           "web": {"breakpoints": {"mobile": 390, "tablet": 768, "desktop": 1440}, "container": {"max": 1200}}},
  "primitives": [{"id": "simbolo", "src": "primitivas/simbolo.svg", "note": ""}],
  "devices": [{"id": "eco", "name": "Eco", "op": "contour", "src": "primitivas/simbolo.svg",
               "params": {"n": 5, "step": 0.03}, "rule": "onde, quanto, com o quê",
               "colorways": ["brand-ink", "ink-paper"]}],
  "icons": {"base": "", "stroke": 2, "cap": "square", "join": "miter", "grid": 24, "rules": []},
  "imagery": {"style": "", "treatment": "", "crop": "", "prompt_style": "", "dont": []},
  "texture": {"fx": ["grain:0.04"], "rule": ""},
  "motion": {"principles": [], "easing": {"expressivo": [0.4, 0.14, 0.3, 1], "produtivo": [0.2, 0, 0.38, 0.9]},
             "easing_notes": {"produtivo": "tarefa de interface; origem IBM Carbon"},
             "durations": {"rapido": 150, "base": 300, "lento": 500}},
  "applications": [{"recipe": "supergrafico", "headline": "", "sub": "", "cta": "", "number": "", "label": "",
                    "photo": "", "formats": ["post", "story"]}],
  "templates": [{"id": "janela", "model": "janela", "name": "Janela", "rule": "1 frase", "measures": ["…"],
                 "colors": {"bg": "brand", "fg": "ink"}, "foto": "imagem/x.png",
                 "sample": {"texto": "…", "info": "…", "foto": "imagem/x.png"},
                 "examples": "← modelos.py kit", "command": "← modelos.py kit"}],
  "board": {"symbol": "logo/x-simbolo.svg", "elements": ["elementos/a-ink-brand.png", "…×4"],
            "feed": "aplicacoes/x/pecas/x-1080x1350.png", "story": "…-1080x1920.png"},
  "mockups": {"poster-noite": {"art": "aplicacoes/x/pecas/x-1080x1350.png"},
              "fachada": {"prompt": "…", "aspect": "4:5", "art": "…", "quad": [0, 0, 0, 0, 0, 0, 0, 0]}},
  "patterns": [{"id": "", "name": "", "src": "elementos/x.svg", "mundo": "", "rule": ""}],
  "elements": {"intro": "", "unit": "u = …", "rules": ["…"]}
}
```

## Blocos da camada "identidade completa"
Todos opcionais; sem o bloco, o capítulo correspondente é pulado **com aviso** (nunca em silêncio).

```jsonc
{
  "shape": {                                    // linguagem de forma (references: direcao-de-arte/references/forma.md)
    "escala": {"none": 0, "sm": 16, "md": 28, "lg": 44, "full": 9999},   // ARTE 1080 (px)
    "site":   {"none": 0, "sm": 6,  "md": 10, "lg": 16, "full": 9999},   // px CSS (sem ele: arte ÷ 2,75)
    "papeis": {"card": "md", "tarja": "none", "button": "full", "avatar": "circulo",
               "lower-third": {"passo": "md", "cantos": ["md", "md", "md", "none"], "nota": "texto"}},
    "nunca_arredonda": ["logo", "visor", "tarja"],   // ids de papel; o logo SEMPRE entra
    "combo": "A", "regra": "O reto é o sinal; a curva é a escola: …", "por_peca": "≤ 3 formas",
    "status": "proposta — aguardando a escolha do cliente entre A, B e C",
    "radius": 0                                  // marca antiga (sem escala): deriva md = r, lg = 2r, sm = r/2
  },
  "products": [{                                 // sub-identidades: produto, linha, noite, curso
    "id": "linha-a", "name": "Linha A", "tag": "Azul", "order": 1, "sub": "edição 1 · nome do responsável",
    "color_name": {"name": "Azul Chroma", "status": "proposta — aguardando o sim do cliente"},   // ou string
    "label": "EDIÇÃO 1 · Pessoa A · Linha A",            // rótulo escrito que acompanha a cor (sem ele: monta de "noite")
    "noite": {"n": 1, "professor": "Pessoa A"},
    "colors": {"bg": "#101010", "ink": "#FAFAF7", "accent": "#2F6BFF", "on_accent": "#101010",
               "dot": "#2F6BFF", "frame": "#2F6BFF",           // ponto ao vivo (--color-live) e visor
               "alt": {"bg": "#2F6BFF", "ink": "#FAFAF7", "accent": "#101010", "on_accent": "#2F6BFF"}},
    "swatches": [["#0057FF", "azul da marca-mãe"]],
    "logos": [{"src": "logo/a-tarja/linha-a/x-nome.svg", "name": "A · Tarja", "bg": "#2F6BFF"}],
    "symbols": [{"src": "…-simbolo.svg", "bg": "#2F6BFF"}],
    "pieces": ["serie/x-1080x1350.png"], "rules": ["…"], "dont": ["…"]
  }],
  "products_rule": "1–3 frases: como a marca-mãe e os produtos convivem",
  "architecture": {                              // 17c: quem é quem
    "status": "proposta — …", "modelo": "endossada por fora, monolítica por dentro: …",
    "endossante": {"nome": "", "como": "", "logo": "logo/…svg"},
    "marca": {"nome": "", "como": "", "logos": ["logo/…svg"]},
    "produtos": {"como": "", "ids": ["linha-a"]},
    "selos": {"nome": "logo oficial de cada pós", "como": "pequeno e monocromático", "arquivos": ["…svg"]},
    "constantes": ["o que nunca muda"], "variavel": "o que muda (só a cor, por papel)",
    "produto_mae": "todos",
    "qual_cor": [{"se": "pergunta", "entao": "resposta", "cor": "#… ou id do produto"}],   // ou use qual_cor_extra
    "qual_cor_extra": [{"se": "pergunta a mais", "entao": "resposta"}]
  },
  "accessibility": {                             // as 12 regras padrão vêm da skill; aqui só as da marca
    "status": "", "focus": {"width": 3, "offset": 2}, "target_min": 48,
    "rules": [{"name": "Cor nunca sozinha", "rule": "…"}],      // mesmo nome = substitui; nome novo = acrescenta
    "checks": ["o que o verificador mede"]
  },
  "channels": {
    "instagram": {"handle": "[a definir]", "avatar": "logo/…svg", "avatar_bg": "#101010", "highlights": "",
                  "grid": "", "caption": ""},
    "whatsapp": {"photo": "logo/…foto-grupo.png", "photo_rule": "foto redonda 640 × 640: …",
                 "group_name": "", "description": "", "messages": [], "stickers": [],
                 "copy_do_documento": ["frase do documento do cliente"]}
  },
  "official": {"instagram": "", "whatsapp": "", "site": "", "email": "", "never": ["nunca pedimos Pix por mensagem"],
               "sugestao": "texto que precisa do sim do cliente"},
  "legal": {"trademark_status": "", "titular": "", "cnpj": "", "mec": "", "credits": [{"o_que": "", "quem": ""}],
            "releases": [{"quem": "Pessoa", "autorizacao_imagem": ""}],
            "licenses": [{"o_que": "Big Shoulders, Archivo", "licenca": "SIL OFL 1.1"}]},
  "governance": {"version": "0.1", "status": "", "owner": "", "contact": "", "approvers": [{"o_que": "", "quem": ""}],
                 "changelog": [{"data": "", "o_que": "", "por_que": ""}],
                 "request": {"campos": ["modelo", "formato"], "onde": "", "prazo": ""},
                 "naming": {"padrao": "marca_<produto>_<peca>_<formato>_v<NN>.<ext>", "exemplo": "", "status": ""},
                 "exports": [{"uso": "feed", "formato": "PNG sRGB 1080 px"}], "downloads": ""},
  "decisions": {"intro": "o que ainda precisa do sim da cliente",
                "itens": [{"n": 1, "tema": "Forma", "pergunta": "A, B ou C?", "hoje": "A (proposta)",
                           "depois": "o que muda se mudar"}]},
  "pages": {"sub": "uma frase na abertura do capítulo", "regra": "o que é igual em toda página",
            "metodo": [{"t": "Dobra = tela inteira", "d": "min-height 100svh menos o cabeçalho"}],
            "items": [{"nome": "Página do André · v1", "grupo": "mae | individual", "produto": "id de products[]",
                       "versao": "v1", "rota": "/solo/pessoa-a/v1/", "papel": "papel no funil", "ideia_curta": "…",
                       "ideia": "uma frase", "cta": "texto do botão", "oferta": "…", "funil": "…",
                       "anatomia": [{"bloco": "Hero", "papel": "…"}],
                       "elementos": [{"nome": "goniômetro 90°", "onde": "dobra", "porque": "…"}],
                       "prints": {"dobra_desktop": "paginas/x-1440.jpg", "dobra_mobile": "paginas/x-390.jpg",
                                  "inteira_mobile": "paginas/x-390-inteira.jpg"},
                       "prints_claro": {"dobra_desktop": "…", "dobra_mobile": "…", "inteira_mobile": "…"}}]},
  "demo": {"cta": "texto do cliente", "link": "", "email": "ana@exemplo.com", "preco": null, "preco_de": null,
           "parcelas": null, "preco_aviso": "Os valores serão divulgados ao vivo.", "hora": "20h30", "tema": "dark",
           "botao_enviando": "Enviando…", "botao_sucesso": "Enviado",
           "estados": {"ao-vivo": {"chip": "Ao vivo agora", "valor": "agora", "texto": "…", "acao": "Assistir"}}}
}
```

## Detalhes e regras de cada bloco
- `primitives[]`: `"main": true` marca a forma-mãe (DNA e elementos derivam da forma-mãe); `"role": "symbol"` marca o
  símbolo compacto (favicon, avatar; nunca a palavra longa).
- `type.<papel>.family` aceita um arquivo `.ttf/.otf` do projeto (letra própria); `type.lead` = entrelinha dos
  títulos dos modelos (padrão 1,42 × maiúscula). `type.anchor` = a âncora do cliente (preço, botão, rótulo).
- `templates`: tipos e parâmetros em references/modelos.md (`modelos.py tipos`).
- `board`/`mockups`: escolhas exatas; sem elas os scripts escolhem sozinhos (peças dos modelos antes das receitas).
- `patterns` + `elements`: elementos feitos por código próprio (contam no `brand.py status`). Quando `devices` está
  vazio, o manual lê `elements` (intro/unit/rules) + `patterns[]` (uma ficha por elemento; `src` = imagem em página
  própria) + `elementos/catalogo/*.png` (folhas da biblioteca ornamentos). Sem isso o kit sumia do PDF.
- `logo.dont`: 6–8 proibições concretas (o manual gera os exemplos; lista longa vai para página própria).
  `logo.clearspace` é fração da altura (0,17), o manual formata com vírgula. Logo de terceiro (pós, parceiro) entra
  na versão oficial monocromática e pequena (`architecture.selos`).
- **`shape`** (17a §8; regras em `direcao-de-arte/references/forma.md`): duas camadas — escala (`none, sm, md, lg,
  full`) e PAPÉIS (`card, tarja, button, field, media, avatar, …`); o componente usa só papel, nunca o número. `cantos`
  = raio por canto (sup. esq., sup. dir., inf. dir., inf. esq.). O papel `focus` é calculado (botão + afastamento do
  foco). `nunca_arredonda` precisa listar o logo. Arte ≈ 2,75 × site. `status` começa por "proposta" até a cliente
  escolher A/B/C. Saída: `tokens.py` (`radius-*` primitivos + papéis, `[data-meio="arte"]`), página "Forma" do manual
  e bloco "Forma" da demo.
- **`color.error`**: erro é token FIXO da campanha, nunca cor de produto (cor de produto como cor de erro está na lista
  NUNCA do pré-voo). `escuro` vale nos fundos escuros, `papel` nos claros; se nenhuma passa 4,5:1 (ex.: azul cheio) o
  `tokens.py` põe a mensagem numa tarja escura e avisa. Formato do erro: fio 2 px + ✕ + "Erro:", nunca bloco cheio.
- **`products[]`**: `colors` = 4 cores de CONTEXTO (`bg`, `ink`, `accent`, `on_accent`) + `alt`; `dot` (ponto
  ao vivo → `--color-live`) e `frame` (visor). Contraste exigido: `ink`/`bg` ≥ 4,5:1, `accent`/`bg` ≥ 3:1,
  `on_accent`/`accent` ≥ 4,5:1 (par entre 3 e 4,5 → botão com texto ≥ 18,7 px negrito: `--btn-fs` 19 px) — o
  `tokens.py build` avisa o que falha. `color_name` com `status` "proposta…" aparece marcado como PROPOSTA no manual,
  no DESIGN.md e na demo até a cliente dar o sim. `label` é o texto que acompanha a cor (WCAG 1.4.1; azul e roxo são
  iguais para deuteranopia). O capítulo Produtos mostra também a matriz produto × papel, a árvore "qual cor usar?" e
  a prova de daltonismo (Machado 2009) com os pares que confundem.
- **`architecture`**: o manual desenha a página "Como a marca se organiza" (endossante → marca → produtos → selos) e
  "O que nunca muda × o que muda". `qual_cor` manda; sem ele a árvore é montada dos produtos.
- **`accessibility`**: foco (anel `width`/`offset`), alvo mínimo (nosso 48 px; WCAG 2.5.8 = 24) e regras próprias da
  marca; o capítulo traz as 12 regras padrão + as da marca + "o que o verificador mede".
- **`channels` / `official` / `legal` / `governance`**: só o que existir é desenhado; o resto aparece como
  `[a definir]` tracejado e vira aviso no terminal. `legal.trademark_status` só libera "®" com valor "concedido".
- **`decisions`**: o estúdio REGISTRA o que a cliente ainda precisa decidir (hoje no manual × se mudar); nunca
  decide por ela. Vira o capítulo "Decisões pendentes" no fim do manual.
- **`demo`** (design system): a demonstração usa SÓ a copy do cliente — `cta`, `link`, `preco`, `preco_de`,
  `parcelas`, `preco_aviso`, `hora`, `estados`, `botao_enviando`, `botao_sucesso`. Sem copy → "[a definir]";
  **nunca** preço "de/por" ou CTA de exemplo. `tema: "dark"` abre a demo no escuro (ouro sobre papel falha).
- **`motion.easing_notes`**: uma frase por curva (origem e uso); o par produtivo (0,2 · 0 · 0,38 · 0,9) entra mesmo
  sem estar na marca. **`grid.web`**: breakpoints e container do site (viram `breakpoint-*` e `container-*`).
- **Caminhos**: relativos à pasta do projeto. Moveu ou apagou arquivo → atualize o `brand.json` na hora:
  o `manual.py build` confere TODO caminho citado (`aviso caminho: …`) e o `brand.py status` cobre o essencial.
  Arquivo antigo vai para `_antigas/`, nunca para o lixo sem confirmação.
- **Cobertura**: o `manual.py` lista toda chave preenchida que nenhum capítulo leu (`cobertura: …`). Chave nova no
  `brand.json` → capítulo novo, ou fica fora do manual de propósito (`COBERTURA_IGNORA` no script).

Caminhos são relativos à pasta do projeto. `colorways` válidos: ink-paper, paper-ink, brand-ink, ink-brand,
accent-paper. Ops de `devices`: crop, contour, bands, slice, hatch, halftone, repeat, stack, modules, outline, morph
(precisa de `"to"`), frame.
Estrutura de pastas: `briefing.md plataforma.md pesquisa/ referencias/ territorios/ arena/ primitivas/ logo/ cores/
tipografia/ elementos/ icones/ imagem/ aplicacoes/ mockups/ tokens/ manual/ DESIGN.md`.
`imagem/` só guarda foto REAL e arte aprovada: imagem de IA com pessoa NUNCA fica ali (o manual puxa tudo da pasta); vai para `imagem/_fora-do-manual/`.
