# Contrato técnico (stack, hospedagem, ambiente)

Pedido típico: "não em HTML solto; tecnologia atual, que dê para colocar na Hostinger, na Vercel e afins". Justificativa completa e alternativas descartadas:
`assets/template/docs/DECISOES.md`. Detalhe de contrato de página: `../direcao-de-arte/references/paginas-de-captura.md` §4g.

## Stack

| Camada | Escolha (versões do template) | Observação |
|---|---|---|
| Framework | **Next.js 16.4** App Router, `output: 'export'`, `trailingSlash: true`, `images.unoptimized` | estático: `out/` roda em Apache e na Vercel |
| UI | React 19.3 + TypeScript 5.9.3 | TS 7 e ESLint 10 ainda não (peers dos plugins) |
| Estilo | **Tailwind CSS 4.3** (`@theme static`) + CSS próprio `.est-*` / `.pg-*` | tokens = variáveis CSS; sem `bg-blue-500` |
| Movimento | CSS scroll-driven (1ª escolha) · **GSAP 3.15** sob demanda (`import()` em idle) · Lenis 1.3 opcional | GSAP "No Charge": só em página SEM cobrança de acesso |
| Efeitos | grão fixo em CSS (tile PNG) · `Grain` WebGL (~1,3 KB) só em seção | sem three.js/R3F |
| Pop-up | `<dialog>` nativo em componente React lazy | 0 KB de biblioteca |
| Formulário | POST JSON para `NEXT_PUBLIC_LEAD_ENDPOINT` (Make/n8n/PHP); vazio = demo | funciona em hospedagem estática |
| Verificação | `check_pagina.py` + `teste_pagina_total.py` (Playwright + Chrome) | 0 erros para entregar |

**Node 22+ / npm 10+.** Python do estúdio para `site.py` e `build-assets.py` (fonttools, brotli, pillow, numpy,
resvg-py, playwright).

## Restrições de hospedagem estática (quebram o `export`)

Sem API routes · sem middleware/proxy · sem Server Actions · sem `next/image` de servidor · sem `revalidate` ·
sem rotas dinâmicas sem `generateStaticParams` · `<a>` em vez de `next/link` entre rotas (prefetch dá 404 com
`trailingSlash`) · imagens por `withBase()` / `Photo` / `Logo` (senão quebram em subpasta).

## Variáveis de ambiente (`NEXT_PUBLIC_*`, gravadas NO BUILD)

| Variável | Padrão | Uso |
|---|---|---|
| `NEXT_PUBLIC_LEAD_ENDPOINT` | vazio (demo) | URL do POST do formulário |
| `NEXT_PUBLIC_DESTINO_URL` (ou `NEXT_PUBLIC_GROUP_URL`) | `#destino` | botão da tela de sucesso (grupo, obrigado, agenda) |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000` | `metadataBase`, og:image, canonical (sem barra no fim) |
| `NEXT_PUBLIC_BASE_PATH` | vazio | subpasta, **sem barra** (`site`): no Git Bash `/site` vira caminho de disco |
| `NEXT_PUBLIC_NOINDEX` | `1` | `0` só na versão final (liga `index,follow` e `robots.txt` allow) |
| `NEXT_PUBLIC_SMOOTH_SCROLL` | `0` | Lenis no desktop |

Mudou variável → `npm run build` de novo e reenviar `out/` inteiro (apague `.next`: o cache guarda o valor velho).
Nada secreto no navegador: chaves ficam no servidor que recebe o POST.

## Hospedagem

### Vercel
Importar o repositório (ou `vercel` na pasta); *Framework Preset* Next.js; saída `out`; variáveis em *Settings →
Environment Variables* (Production e Preview). `vercel.json` já traz `trailingSlash`, cache imutável de
`/_next/static`, 30 dias para `/img` e `/logos`, e cabeçalhos de segurança (nosniff, Referrer-Policy,
X-Frame-Options, Permissions-Policy, HSTS).

### Hostinger (compartilhada = só arquivos)
- **Raiz** (`dominio.com.br`): enviar o CONTEÚDO de `out/` para `public_html/`, com o `.htaccess` (oculto).
- **Subpasta** (`dominio.com.br/site/`): build com `NEXT_PUBLIC_BASE_PATH=site`; enviar para `public_html/site/`;
  o `postbuild.mjs` já troca o `ErrorDocument 404` do `.htaccess` por `/site/404.html`.
- **Subdomínio**: criar no painel, apontar para pasta própria, enviar `out/` lá (sem `BASE_PATH`) — o caminho mais simples.
- SSL gratuito → descomentar o bloco "forçar HTTPS" do `.htaccess`.
- `lead.php` (se usar PHP) vai junto, na mesma origem: não faz parte do build.

### `.htaccess` (`public/.htaccess`, copiado para `out/` pelo postbuild)
`Options -MultiViews -Indexes`, `DirectorySlash On`, UTF-8, `ErrorDocument 404`, tipos (woff2, webp, avif, svg,
js), compressão (brotli quando existe; gzip), cache (`/_next/static` e `.js/.css/.woff2` 1 ano imutável; imagens 30
dias; HTML sempre revalida), cabeçalhos de segurança, bloqueio de `.env*`, `package*.json`, `.md/.ts/.map`.
Se der erro 500 depois de enviar, apagar os blocos `<IfModule>` um a um (o módulo pode não existir).

## Orçamento

JS inicial da rota ≤ **150 KB gzip** (React + runtime ≈ 120 KB) · CSS ≤ 40 KB gzip · HTML ≤ 120 KB bruto ·
LCP < 2,5 s · imagens WebP ≤ 150 KB (hero ≤ 220 KB) · CLS ≤ 0,1 · sem rolagem horizontal 320–2560.
`npm run size` / `site.py check` medem. O que é novo e pesado entra por `import()` em idle.

## Acessibilidade e leitura (tudo testado)

Alvos ≥ 44 px (48 recomendado) e ≥ 8 px entre alvos · foco visível 2–3 px · corpo ≥ 16 px (rótulo mono ≥ 14, só em
`span/small/div`) · contraste texto ≥ 4,5:1 (corpo sobre escuro ≥ 7:1) · `lang="pt-BR"`, `<title>` e descrição ·
`alt` em toda imagem · um `<h1>` · `aria-live` no sucesso do pop-up · FAQ em `<details>` · "pular para o conteúdo".

## Dados e privacidade

Consentimento curto sob o botão (entrega a pedido do titular); se houver marketing depois, caixa desmarcada.
Confirmar com advogado. `track()` nunca recebe nome/e-mail/telefone (chaves proibidas são descartadas); o
`event_id` é o mesmo no navegador e no servidor (deduplicação com a API de Conversões da Meta). Pixel/CAPI reais
não vêm no template (só o stub).

## Licenças que acompanham a entrega

GSAP "Standard No Charge" (texto em `public/licencas/`) · fontes OFL (`public/licencas/OFL-*.txt`, geradas por
`npm run assets`) · Next/React/Tailwind/Lenis MIT. Foto de gente é cedida pelo cliente; nunca IA.
