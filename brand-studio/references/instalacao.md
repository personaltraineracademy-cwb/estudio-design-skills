# Instalação e ferramentas — o que é obrigatório, recomendado e opcional

Vale para as 5 skills do estúdio (brand-studio, brand-system, direcao-de-arte, criacao-de-sites, revisao-de-design).
Tudo aqui foi o que realmente se usou para chegar aos resultados do estúdio. Total em disco: ~1,5 GB com os modelos.

## Contents
- Protocolo de primeiro uso (para o agente)
- Obrigatório
- Recomendado
- Opcional (alguns pagos)
- Contas e serviços externos
- Variáveis e pastas
- Testado e descartado (não instale)
- Problemas comuns

## Protocolo de primeiro uso (para o agente)
Na primeira vez que qualquer skill do estúdio for usada numa máquina (ou quando um script falhar por falta de algo):
1. Rodar `python <brand-studio>/scripts/doctor.py --json`.
2. Explicar ao usuário, em linguagem simples, em 3 blocos curtos:
   - **Precisa** (obrigatório faltando): o que é, para que serve, o comando.
   - **Recomendo** (recomendado faltando): o que melhora; tudo grátis.
   - **Opcional** (extras): o que acrescenta e **quanto custa** quando é pago (Gemini).
3. **Pedir permissão antes de instalar.** Com o sim: `python <brand-studio>/scripts/instalar.py` (Python + YuNet);
   `--upscale` e `--modelos` só se ele quiser. Programas do sistema (Chrome, Node, FFmpeg): mostrar o comando do
   sistema dele e deixar ele rodar ou pedir para rodar.
4. **Nunca pedir chave de API no chat.** Explicar onde ela fica (`.env` na pasta de trabalho) e que o usuário cola sozinho.
5. Faltou algo opcional → seguir com o que existe e dizer o que ficou de fora. Não travar o trabalho.
6. Rodar o diagnóstico uma vez por sessão no máximo (economia de tokens).

## Obrigatório
| Ferramenta | Para quê | Como instalar | Licença |
|---|---|---|---|
| Python 3.11+ | todos os scripts | python.org · `winget install Python.Python.3.12` · `brew install python` | PSF |
| Pacotes Python do núcleo | render de SVG (resvg), texto em curvas (fonttools + skia-pathops), imagem (pillow, numpy), woff2 (brotli) | `python scripts/instalar.py` (usa `requirements.txt`) | MIT/BSD/Apache |
| Pacotes de composição | Chrome dirigido (playwright), medidas no pixel e rosto (opencv), geometria (shapely, scipy, scikit-image), QR real (segno + zxing-cpp), PDF de referência (pymupdf) | idem | Apache/BSD/MIT; pymupdf AGPL |
| Google Chrome (ou Edge) | peças em HTML/CSS, verificadores medidos no navegador, manual, demo do design system, sites, 3D | chrome.google.com · `winget install Google.Chrome` · `brew install --cask google-chrome` | — |

O Playwright usa o **Chrome já instalado** (`channel="chrome"`): **não** rode `playwright install` (baixaria ~1,4 GB
de navegadores que as skills não usam).

## Recomendado (grátis, local)
| Ferramenta | Sem ela | Como instalar | Tamanho |
|---|---|---|---|
| Node.js 22+ | sem sketches generativos, SVGO (limpeza de SVG), animação de logo, sites Next.js | nodejs.org · `winget install OpenJS.NodeJS.LTS` · `brew install node` | ~80 MB |
| FFmpeg | sem MP4 da animação de logo | `winget install Gyan.FFmpeg` · `brew install ffmpeg` · `apt install ffmpeg` | ~100 MB |
| fastembed (CLIP ViT-B/32) | sem busca por imagem no acervo e sem teste de originalidade | pacote Python; modelo baixa no 1º uso ou `instalar.py --modelos` | ~580 MB |
| rembg (recorte) | sem recorte automático de pessoa/objeto | pacote Python; modelo baixa no 1º uso | ~180 MB/modelo |
| vtracer | sem raster → SVG | pacote Python | pequeno |
| YuNet (OpenCV Zoo) | prova de camadas não confere rosto/olhos | `instalar.py` (baixa para `~/.cache/brand-studio/models/yunet/`) | 230 KB |
| Skill logo-design (MIT) | sem auditoria de SVG, folha de conceitos e ~1.400 logos de mercado do teste de originalidade | copiar github.com/kaankiziltug/logo-design-skill ao lado das skills | ~15 MB |
| Plugin caveman (MIT) | respostas longas, limite de uso acaba mais rápido | já vem como dependência do plugin `estudio-design`; solto: `/plugin marketplace add JuliusBrussee/caveman` | pequeno |

Baixados sob demanda pelos próprios scripts (precisam de internet na hora): fontes OFL do Google Fonts
(`fonts.py`, cache em `~/.cache/brand-studio/fonts`), SVGO (`npx svgo@3`), HyperFrames (`npx hyperframes@0.8.143`,
Apache 2.0), three.js e GSAP via CDN jsdelivr no `render3d.py` e no `motion.py`, dependências npm do site
(`site.py new --install`: Next.js 16, React 19, Tailwind 4, GSAP, Lenis).

## Opcional (alguns pagos)
| Extra | Acrescenta | Custo | Como |
|---|---|---|---|
| **API do Gemini** (Nano Banana 2.1) | imagem por IA: cenários, texturas, complementos, mockups realistas; juiz de outra família de modelo na arena; pesquisa com Google Search | **pago**: ~US$ 0,034 (1K) · 0,050 (2K) · 0,113 (4K) por imagem; vídeo ~US$ 0,10/s | criar chave em aistudio.google.com/apikey, **ativar faturamento**, pôr `GEMINI_API_KEY=…` no `.env` da pasta de trabalho; testar com `python scripts/gemini.py check` e um `gen --n 1 --size 1K` |
| Real-ESRGAN ncnn-vulkan | upscale 4× de foto pequena | grátis; precisa GPU com Vulkan | `python scripts/instalar.py --upscale` |
| Conector Adobe (no Claude) | impulsiona as skills: com ele ligado, **todo recurso pago (fonte, foto, ícone, textura, modelo) é buscado primeiro no Adobe** (Fonts incluídas no plano, Stock, Express) antes de criar ou usar grátis; também recomendação de fontes, tratamento de foto, vetorização em nuvem, exportação editável para o Adobe Express | conta Adobe | ligar o conector no app do Claude; chamar `adobe_mandatory_init` uma vez por sessão |
| Vercel / Hostinger | publicar os sites | planos grátis ou pagos | `site.py pack` gera os zips; Vercel: `npx vercel` na pasta |
| Biblioteca de clientes | acervo próprio para repertório e "não repetir" | — | `biblioteca/<Cliente>/<Projeto>/` + `python scripts/library.py index` |

Sem Gemini as skills funcionam inteiras com motores grátis (código, sketches, 3D em three.js, recorte, efeitos); a IA
é um plus para cenário e composição difícil. Pessoas são sempre fotos reais (IA nunca cria nem altera pessoa).

## Variáveis e pastas
| Nome | Para quê | Padrão |
|---|---|---|
| `ESTUDIO_DIR` | pasta de trabalho do usuário (biblioteca, `.env`, projetos) | pasta acima das skills se tiver `biblioteca/` ou `.env`; senão a atual |
| `BRAND_LIBRARY` | biblioteca em outro lugar | `<ESTUDIO_DIR>/biblioteca` |
| `GEMINI_API_KEY` | chave do Gemini | lida do ambiente ou do `.env` |
| `LOGO_DESIGN_SKILL` | logo-design em outro lugar | irmã das skills ou `~/.claude/skills/logo-design` |
| `CHECK_DIR` | pasta dos verificadores de página | `../direcao-de-arte/scripts` |
Cache (pode apagar; baixa de novo): `~/.cache/brand-studio/` (modelos, fontes, binários, custo do Gemini em
`gemini-usage.csv`) e `~/.u2net` ou `~/.rembg` (modelos de recorte).

## Testado e descartado (não instale)
- IA de imagem local (Stable Diffusion etc.): pesada para GPU comum e pior que o Gemini para este uso.
- `playwright install` (navegadores próprios): desnecessário, as skills usam o Chrome instalado.
- Remotion: grátis só até 3 funcionários — usar HyperFrames.
- Canva, Recraft, Replicate, Moda, Orshot e apps de desktop (Illustrator, Inkscape): fora da stack (pagos ou
  manuais); o render é resvg + Chrome.
- picosvg, pyclipr, svgpathtools, pyfastnoiselite, kiwisolver: testados em pesquisa, nenhum script depende deles.
- Imagen (Google): desligado na API do Gemini; usar Nano Banana 2.1 (`--model banana21`, padrão).

## Problemas comuns
- Windows: rodar com `python` (não `python3`); console em cp1252 quebra acentos → os scripts já forçam UTF-8.
- Caminho muito longo quebra build e vtracer → trabalhar em pasta curta.
- Git Bash troca `/rota` por caminho do Windows → passar rotas sem a barra inicial.
- `node_modules` como junção/symlink derruba o Turbopack → instalar dentro da pasta do site.
- 3D sem imagem: o Chrome precisa de WebGL por software (`render3d.py` já usa SwiftShader).
- Script reclamou de algo faltando → `python scripts/doctor.py` diz o quê e o comando.
