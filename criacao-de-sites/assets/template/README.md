# Site do cliente — Next.js 16 (exportação estática)

Projeto criado pela skill `criacao-de-sites` do estúdio (`python skills/criacao-de-sites/scripts/site.py new …`).
É **100% estático**: `npm run build` gera a pasta `out/` (HTML + JS + CSS + imagens), que roda em qualquer
hospedagem (Vercel, Hostinger, Netlify…). Marca = `content/marca.json`; texto = `content/copy.json`.

## Rodar

Requisitos: Node 22+ e npm 10+.

```bash
npm ci               # (ou npm install) instala as dependências
npm run dev          # http://localhost:3000
npm run build        # gera out/ (e copia .htaccess para out/)
npm run start:out    # serve out/ em http://localhost:4173 imitando produção (301 de /x para /x/, 404.html, gzip)
npm run lint         # ESLint
npm run typecheck    # tsc --noEmit
npm test             # máscara/validação do WhatsApp (node:test)
npm run size         # peso inicial (JS/CSS gzip) por rota vs orçamento
npm run assets       # refaz fontes, tokens, logos, grão, OG e ícones a partir de content/marca.json
npm run check        # build + servidor + check_pagina.py (+ --total: teste_pagina_total.py) + peso
```

`npm run check -- --no-build --total --rapido` reaproveita o `out/` e roda também a bateria completa. Relatórios e
PNGs ficam em `.check/<rota>/`. Os verificadores são os do estúdio (`skills/direcao-de-arte/scripts/`; outro
caminho em `CHECK_DIR`). **Precisam terminar com 0 erros**; avisos são perguntas a responder (corrigir ou
justificar em `docs/decisoes-do-projeto.md`). Atalho do estúdio: `python skills/criacao-de-sites/scripts/site.py check .`.

## Estrutura

```
content/
  copy.json           COPY FINAL (única fonte de texto comercial). Chaves com _ não vão para a página.
  marca.json          cores, fontes, raios, grão, nomes dos logos (gera styles/tokens.css e app/fonts.ts)
app/
  layout.tsx          lang pt-BR, metadados (da copy), viewport, provedor do pop-up, fontes, script de movimento
  globals.css         tokens FIXOS (quebras, escala de texto, 12·24·40, margem, respiro) + imports
  fonts.ts            GERADO (npm run assets)
  page.tsx            composição da página (só desenha as seções que a copy tem)
  not-found.tsx · robots.ts · icon.svg · apple-icon.png
components/
  secoes/             Cabecalho · Hero (holofote) · Passos · Destaques · Faq · CtaFinal · Rodape
  ButtonCta · Logo · Photo · Reveal(+RevealObserver) · Accordion · Marquee · Grain · StickyCta · SmoothScroll
  LeadModal(+LeadModalDialog)   pop-up de captura (<dialog> nativo, carregado sob demanda)
lib/
  copy.ts (tipos da copy) · ui-text.ts (rótulos neutros) · config.ts (NEXT_PUBLIC_*) · url.ts (BASE_PATH)
  phone.ts (WhatsApp BR) · analytics.ts (stub) · gsap.ts · motion.ts · idle.ts · logos.generated.ts (GERADO)
styles/
  tokens.css (GERADO) · base.css · components.css (.est-*) · pagina.css (.pg-*, a página-exemplo)
assets-src/logos/     SVG do cliente (logo.svg, logo-simbolo.svg)
public/               img/ (grão, fotos), logos/ (svg), og.png, licencas/, .htaccess
scripts/              build-assets.py · serve-out.mjs · check.mjs · size.mjs · postbuild.mjs
docs/                 DECISOES.md (stack) · decisoes-do-projeto.md (do projeto: ideia da dobra, rodadas)
vercel.json · .env.example
```

> O prefixo `.est-` das classes compartilhadas é histórico (1º cliente do estúdio). Os verificadores dependem dele:
> **não renomear**. As classes da página deste projeto usam `.pg-`.

## Trocar copy, marca, datas, endpoint e destino

| O quê | Onde | Depois |
|---|---|---|
| Texto da página | `content/copy.json` (nunca no JSX) | `npm run build` |
| Rótulos de interface (Fechar, Enviando…) | `lib/ui-text.ts` | build |
| Cores, fontes, raios, grão | `content/marca.json` | `npm run assets` + build |
| Logo | `assets-src/logos/logo.svg` (+ `logo-simbolo.svg`) | `npm run assets` + build |
| Foto da dobra | `content/copy.json` → `hero.imagem` + arquivos em `public/img/` | build |
| Endpoint do formulário | `NEXT_PUBLIC_LEAD_ENDPOINT` | build |
| Destino do botão de sucesso | `NEXT_PUBLIC_DESTINO_URL` | build |
| URL final / OG | `NEXT_PUBLIC_SITE_URL` | build |
| Subpasta | `NEXT_PUBLIC_BASE_PATH=site` (sem barra) | build |
| Indexação | `NEXT_PUBLIC_NOINDEX=0` na versão final (padrão 1 = `noindex` + `robots.txt` bloqueando) | build |
| Rolagem suave (Lenis, desktop) | `NEXT_PUBLIC_SMOOTH_SCROLL=1` | build |

Copie `.env.example` para `.env.local` (dev) ou cadastre as variáveis no painel da Vercel. **No build estático os
valores são gravados no JavaScript**: mudou uma variável, rode o build de novo e reenvie `out/`.

### Formulário: o que o servidor recebe

`POST` com `Content-Type: application/json` para `NEXT_PUBLIC_LEAD_ENDPOINT`:

```json
{
  "event_id": "2f0c…",                  // o MESMO id vai para o Pixel e para a API de Conversões (deduplicação)
  "nome": "Maria Souza",
  "whatsapp": "5511912345678",          // só dígitos, com 55
  "whatsapp_formatado": "(11) 91234-5678",
  "email": "",
  "contexto": null,                     // etiqueta do botão que abriu o pop-up (data-contexto), se houver
  "origem": "hero",                     // cabecalho | hero | barra-fixa | final | …
  "pagina": "/",
  "utm": { "utm_source": "instagram", "fbclid": "…" },
  "consentimento": "Usaremos seus dados só para…",
  "enviado_em": "2026-10-10T20:11:05.123Z"
}
```

Timeout de 8 s; se o navegador bloquear a leitura da resposta (CORS) ou a rede falhar, há uma 2ª tentativa
`no-cors` (`text/plain`, **mesmo `event_id`**): o servidor deve **deduplicar por `event_id`**. Depois de 2 falhas
aparece "Continuar mesmo assim". Sem endpoint (vazio) o formulário só **simula** o sucesso (`data-demo`).

Exemplos de endpoint: **Make** (cenário "Custom webhook" → Google Sheets / WhatsApp / API de Conversões),
**n8n** (nó Webhook POST, "Respond: Immediately") ou **PHP simples** na Hostinger (`public_html/lead.php`, mesma
origem, sem CORS; **envie o `lead.php` junto com `out/`**, ele não faz parte do build):

```php
<?php
// lead.php — recebe o JSON, grava uma linha em leads.csv (fora de public_html é melhor) e responde 204.
header('Content-Type: application/json; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }
$d = json_decode(file_get_contents('php://input'), true);
if (!is_array($d) || empty($d['event_id']) || empty($d['whatsapp'])) { http_response_code(400); exit; }
$arquivo = __DIR__ . '/../leads.csv';               // ajuste: pasta NÃO pública
$ja = is_file($arquivo) ? file_get_contents($arquivo) : '';
if (strpos($ja, $d['event_id']) !== false) { http_response_code(204); exit; }   // deduplica
$f = fopen($arquivo, 'ab');
fputcsv($f, [date('c'), $d['event_id'], $d['nome'] ?? '', $d['whatsapp'], $d['email'] ?? '', $d['contexto'] ?? '', $d['origem'] ?? '']);
fclose($f);
http_response_code(204);
```

## Deploy

### Vercel
1. Suba esta pasta para um repositório (ou use a CLI: `npm i -g vercel` → `vercel`).
2. "Add New Project" → importe → *Framework Preset*: Next.js (detecta `output: 'export'`; saída `out`).
3. *Settings → Environment Variables*: as `NEXT_PUBLIC_*` (Production e Preview). Domínio: *Settings → Domains*.
4. `vercel.json` já define cache imutável para `/_next/static`, 30 dias para `/img` e `/logos` e cabeçalhos de segurança.

### Hostinger (compartilhada, só arquivos estáticos)
1. No computador: `npm ci` e `npm run build` (com as variáveis em `.env.local`) — ou use `site.py pack` (3 zips).
2. Painel → *Gerenciador de arquivos* (ou FTP) → `public_html`.
3. **Raiz** (`dominio.com.br`): envie o **conteúdo** de `out/` (não a pasta `out`) para `public_html/`. Confirme que o
   `.htaccess` foi junto (arquivo oculto: ative "mostrar ocultos").
4. **Subpasta** (`dominio.com.br/site/`): build com `NEXT_PUBLIC_BASE_PATH=site` (PowerShell:
   `$env:NEXT_PUBLIC_BASE_PATH="site"; npm run build`; no Git Bash use `site` **sem a barra**), envie o conteúdo de
   `out/` para `public_html/site/`. O `ErrorDocument 404` do `.htaccess` já sai apontando para `/site/404.html`.
5. **Subdomínio**: crie no painel, aponte para uma pasta própria e envie `out/` lá (sem `BASE_PATH`).
6. Ative o SSL gratuito e descomente o bloco "forçar HTTPS" do `.htaccess`.
7. Teste: `/` abre; `/x` redireciona para `/x/`; URL inexistente mostra o 404 da marca; pop-up abre e envia.
   Depois de qualquer novo build, reenvie `out/` inteiro (os arquivos `/_next/static/*` mudam de nome).

## Orçamento de desempenho (`npm run size`)

| Item | Limite |
|---|---|
| JS inicial da rota (gzip, sem polyfill `noModule`) | ≤ 150 KB (React + runtime do Next ≈ 120 KB; o resto é nosso) |
| CSS (gzip) | ≤ 40 KB |
| LCP | foto do hero com `fetchpriority="high"` (`<Photo priority>`) |
| Rolagem horizontal | nenhuma em 320–2560 |

Sobra pouca folga de JS: **o que é novo e pesado entra por `import()` em idle** (ver `lib/gsap.ts`).

## Política de movimento

- O movimento roda **sempre**, para todos. `<html data-movimento="total | suave | parado">` (script em
  `app/layout.tsx`): `total` padrão; `suave` quando o sistema do visitante pede menos movimento (MESMA coreografia,
  curta, sem parallax/tilt, faixa mais lenta com botão de pausa); `parado` só por `?movimento=parado`.
- Só `transform`/`opacity`/`clip-path`; entra uma vez; ≤ 0,7 s; nunca no H1, na foto do LCP nem no CTA.
  Estado natural do CSS = estado final (`animation-fill-mode: forwards`/`backwards`, **nunca `both`**).

## O que NÃO fazer

- API routes, middleware, Server Actions, `next/image` com otimização, `revalidate`, rotas dinâmicas sem
  `generateStaticParams`: quebram o `output: 'export'` ou exigem servidor (Hostinger não tem).
- Texto de venda no JSX (tudo vem de `content/copy.json`). Nada de "últimas vagas", contador falso, preço inventado,
  "de/por". Notas de orientação ficam em `pendencias.md`, fora do projeto.
- Abrir o pop-up sozinho (ao carregar, ao sair, por tempo). Só por clique.
- `<p>`/`<li>` com menos de 16 px (o verificador reprova); rótulos de 14 px vão em `<span>/<small>/<div>`.
- `next/link` entre rotas (prefetch dá 404 no export com `trailingSlash`); use `<a href={withBase('/x/')}>`.
- Imagem por `/img/x.webp` solto: use `withBase()` ou os componentes `Photo`/`Logo` (senão quebra em subpasta).
- `100vw` em medida de layout (a barra de rolagem tem 15 px): use `%`, `cqw` ou variável.
- `import gsap` no topo de um componente (entra no JS inicial): use `loadGsap()`/`useGsap`.
- Editar `lib/logos.generated.ts`, `app/fonts.ts` ou `styles/tokens.css` à mão (são gerados por `npm run assets`).
- Pessoa gerada por IA. Foto de gente é real; IA só para cenário/textura/forma (Nano Banana 2.1, `--model banana21`).
- Subir `.env`, `node_modules`, `.check`, `_scratch`.

## Licenças

- **GSAP 3.15**: licença gratuita "Standard No Charge" da Webflow. Vale **enquanto o site não cobra pelo acesso**
  (página de captura gratuita). Se passar a cobrar, trocar por CSS puro ou revisar a licença. Texto em
  `public/licencas/GSAP-standard-no-charge.txt`.
- Lenis (MIT), Next.js e React (MIT), Tailwind CSS (MIT).
- Fontes: SIL OFL 1.1 (arquivos em `public/licencas/`).
