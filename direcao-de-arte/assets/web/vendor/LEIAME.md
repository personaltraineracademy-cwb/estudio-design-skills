# Bibliotecas de movimento (vendor) — funcionam OFFLINE, abrindo por arquivo (`file://`)

Baixadas em 10/10/2026 do registro npm (versão FIXA, nunca "latest"). Todas em formato **UMD/IIFE**: `<script src>` comum.
Motivo: no Chrome, `<script type="module">` **não carrega por `file://`** (testado: bloqueio de origem, `ERR_FAILED`).
Bibliotecas que só têm versão ESM (OGL, Paper Shaders) foram empacotadas aqui com esbuild em IIFE.

| Pasta | Arquivo | Versão | Licença | min | gzip | Usar? |
|---|---|---|---|---|---|---|
| `gsap/3.15.0/` | `gsap.min.js` | 3.15.0 (13/04/2026) | GSAP Standard "No Charge" (`LICENSE-standard-no-charge.txt`) | 72,9 KB | 28,3 KB | sim, **só em página sem cobrança de acesso** (ver pesquisa 19 §2) |
| `gsap/3.15.0/` | `ScrollTrigger.min.js` | 3.15.0 | idem | 44,6 KB | 18,0 KB | sim, só para pin/scrub que o CSS não faz |
| `gsap/3.15.0/` | `SplitText.min.js` | 3.15.0 | idem | 7,7 KB | 3,7 KB | sim (acessível: `aria`, `autoSplit`, `mask`) |
| `gsap/3.15.0/` | `Flip.min.js` | 3.15.0 | idem | 25,5 KB | 9,7 KB | só se houver reordenação de layout animada |
| `lenis/1.3.26/` | `lenis.min.js` + `lenis.css` | 1.3.26 (2.0 está em `dev`) | MIT (`LICENSE`) | 18,7 KB | 5,4 KB | só desktop, sutil; opcional |
| `splitting/1.1.0/` | `splitting.min.js` + `splitting.css` | 1.1.0 | MIT (`LICENSE.md`) | 3,9 KB | 1,8 KB | sim, se o GSAP não estiver na página (divide em `--word-index`, `--char-index`) |
| `countup/2.10.1/` | `countUp.umd.js` | 2.10.1 | MIT (`LICENSE.md`) | 7,1 KB | 2,3 KB | só se precisar de separador/decimal; o CSS `@property` conta inteiros de graça |
| `animejs/4.5.0/` | `anime.umd.min.js` | 4.5.0 | MIT (`LICENSE.md`) | 118 KB | 40,6 KB | evitar (pesado para o que a página usa); alternativa ao GSAP onde a licença preocupa |
| `rough-notation/0.5.1/` | `rough-notation.iife.js` | 0.5.1 | MIT (`LICENSE`) | 10,8 KB | 4,0 KB | enfeite pontual (sublinhado à mão); raro na marca (reto = sinal) |
| `ogl/1.0.11/` | `ogl-min.iife.js` | 1.0.11 (Renderer, Program, Mesh, Triangle) | Unlicense (`LICENSE`) | 44,8 KB | 13,0 KB | **evitar**: o shader próprio de `snippets/shader-grao.js` faz o mesmo em 1,3 KB gzip |
| `paper-shaders/0.0.81/` | `mesh-gradient.iife.js` | 0.0.81 (só o mesh gradient) | Apache-2.0 (`LICENSE`) | 19,7 KB | 6,0 KB | sim, para fundo "fumaça de ouro" pontual; `speed=0` + `frame` = imagem parada |

Não baixados (de propósito): **three.js** (MIT; 529 KB min / 132 KB gzip mesmo com tree-shaking — só para 3D real),
**Motion** (MIT; build UMD completo 145 KB / 48 KB gzip), **NumberFlow** (MIT; só ESM), **Remotion** (pago acima de 3 pessoas),
**LYGIA** (não comercial), **Trianglify** (GPLv3), **Typed.js** (GPL), **Vanta** (cara de template), **Locomotive Scroll** (sequestra a rolagem).

## Como usar
```html
<script src="../vendor/gsap/3.15.0/gsap.min.js"></script>
<script src="../vendor/gsap/3.15.0/ScrollTrigger.min.js"></script>
```
Carregar com `defer` e SÓ nas páginas que precisam. Cada página lista no comentário do topo o que usa e por quê.

## Antes de usar em cliente
1. Reler a licença do GSAP (`https://gsap.com/standard-license/`): a Webflow pode mudar a qualquer momento.
2. Copiar a pasta da versão inteira junto com a página (a licença precisa acompanhar).
3. Conferir o peso total de JS da página contra o orçamento (pesquisa 19 §4, regra 9).
