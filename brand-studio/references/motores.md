# Motores — qual ferramenta para quê

Todos os scripts ficam em `scripts/` (rode com `python`, nunca `python3` no Windows). Renderize e **olhe** cada
resultado (Read no PNG) antes de mostrar.

## Criar formas
| Motor | Quando | Comando |
|---|---|---|
| Construção vetorial (skill logo-design) | símbolo preciso, letra customizada, refinamento final | escreva SVG à mão seguindo `~/.claude/skills/logo-design/references/svg-construction.md`; audite com `svg_audit.py` |
| Generativo (Node, vetor) | explorar famílias de forma, achar acidentes bons, texturas vetoriais | `sketch.py run radial-cuts --seeds 1-36 -o out/rc`; `sketch.py new meu-sketch` para escrever um novo |
| Tipografia em curvas | wordmarks, blocos, faixas, selos | `lockup.py`, `seal.py`, `fonts.py get "Família:peso"` (Google Fonts, OFL) |
| Vetorização local | esboço do usuário, foto de rascunho, imagem de IA, logo antigo em PNG | `vectorize.py in.png out.svg --preset logo` |

Sketches incluídos: `radial-cuts` (forma cortada) · `truchet` (módulos/monogramas) · `orbit-rings` (anéis cinéticos)
· `superform` (formas de Gielis) · `flow-ribbons` (energia para KVs) · `halftone-field` (meio-tom vetorial).
Para um projeto, **escreva um sketch próprio** (copie com `sketch.py new`) quando a ideia pedir uma regra específica
— é aí que nasce o que não existe. API: `export function draw({rnd, noise, w, h, params, pal, lib})` retorna
markup SVG; use `currentColor` para a tinta e `pal.accent` para o destaque; helpers em `assets/sketches/lib.mjs`.

## Imagem, foto, 3D e IA
| Motor | Quando | Comando |
|---|---|---|
| **Gemini (Nano Banana)** — pago por imagem | foto, ilustração, textura, cenário, objeto realista; editar foto com instrução; manter pessoa/estilo com referências | `gemini.py gen "…" --n 3` · `gemini.py edit foto.jpg "…"` · `--element --cutout` · `--vector` · `gemini.py usage` |
| Recorte (rembg) — grátis | tirar fundo de pessoa/produto; sticker com contorno; sombra | `imaging.py cutout foto.jpg -o x.png --crop [--outline 12] [--shadow]` |
| Upscale (Real-ESRGAN, GPU) — grátis | foto ou imagem pequena/ruim → 4× | `imaging.py upscale x.png -o x-4x.png` |
| 3D (three.js) — grátis | símbolo, número ou palavra em 3D (cromado, dourado, plástico, vidro, neon) | `render3d.py --svg simbolo.svg --material chrome` · `--text "50%" --font Anton` |
| Montador de peças — grátis | posts, banners, anúncios, cartazes em todos os formatos; versão editável p/ Express | `compose.py peca.json` (exemplo: `compose.py --example`) — ver `references/composicao.md` |
| SVGO — grátis | limpar/otimizar SVG final | `imaging.py svgclean in.svg -o out.svg` |

## Aplicar e sistematizar
| Peça | Comando |
|---|---|
| Lockups + 5 colorways + co-branding | `lockup.py spec.json` (exemplo: `lockup.py --example`) |
| Padrão | `pattern.py --motif simbolo.svg --all ...` (7 modos) ou `--word` |
| Selo circular | `seal.py --top ... --bottom ... --style ring|solid|open|stamp` |
| Key visuals 1:1, 4:5, 9:16, 16:9 | `keyvisual.py --lockup-dark ... --lockup-light ... --headline ...` |
| Ícones web/app/favicon | `~/.claude/skills/logo-design/scripts/export_variants.py simbolo.svg --web-icons ...` |
| Apresentação com mockups | `~/.claude/skills/logo-design/scripts/presentation_board.py spec.json --png-dir slides` |

## Acabamento raster
`fx.py in.png out.png grain:0.06 vignette:0.4` — também `riso`, `halftone`, `dither`, `duotone`, `glow`,
`posterize`. **Só em KVs, fundos, posters — nunca no master do logo** (meio-tom destrói a leitura do símbolo).
Riso funciona melhor em artes claras.

## Movimento
`motion.py --symbol simbolo-escuro.svg --wordmark texto-escuro.svg --bg "#1A1A1A" -o out/sting` → MP4 via
HyperFrames (HTML + GSAP; 1ª vez baixa o CLI via npx). Estilos `pop`, `spin`, `drop`; `--size 1080x1920` para
stories. O projeto fica editável em `out/sting/index.html` (timeline GSAP) — para algo mais elaborado, edite e
renderize com `npx --yes hyperframes@0.8.143 render` dentro da pasta. Defina `HYPERFRAMES_SKIP_SKILLS=1`.

## Adobe (conector "Adobe for creativity") — quando vale
Sempre chame `adobe_mandatory_init` uma vez antes. O conector **não gera imagem por texto**; use para:
- **Tipografia**: `font_recommend` / `suggest_type_palettes` para achar pares tipográficos por intenção;
  `font_search` / `font_preview`. Fontes Adobe não podem ser convertidas em curvas por nós sem o arquivo — use-as
  para descobrir a direção e escolha um equivalente OFL via `fonts.py`, ou peça ao usuário o arquivo licenciado.
- **Vetorização de fotos/ilustrações difíceis**: `image_vectorize` (precisa enviar o arquivo: `asset_add_file`).
- **Tratamento de fotos** para KVs: remover fundo, selecionar sujeito, ajustes, meio-tom/grão/glitch do Photoshop.
- **Entregar editável no Adobe Express**: monte a peça em HTML (KV/post) e exporte com
  `create_visual_design_express_skill` → `html_export_readiness_skill` → `export_html_to_express` — só quando o
  usuário quiser o arquivo editável no Express (conta Adobe completa; verifique com `get_account_type`).
- **Moodboard**: `create_firefly_board` com assets já na nuvem Adobe.
Arquivos locais exigem upload (picker `asset_add_file`); não prometa processamento Adobe sem esse passo.
