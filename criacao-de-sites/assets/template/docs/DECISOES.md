# Decisões técnicas — base Next.js do template `criacao-de-sites`

Contexto: sair de páginas HTML puras para um projeto de tecnologia atual,
com potencial máximo de elementos e movimento, **hospedável na Vercel e na Hostinger (compartilhada = só arquivos
estáticos)**. Este arquivo é o "porquê" do stack; o que foi decidido para ESTE cliente vai em `decisoes-do-projeto.md`.

## Resumo

| Decisão | Escolha | Por quê (curto) |
|---|---|---|
| Framework | **Next.js 16.4 `output: 'export'`**, `trailingSlash: true`, `images.unoptimized` | build estático (`out/`) serve em Apache e na Vercel; mesmo código nas duas; componentes reaproveitados entre rotas |
| UI | React 19.3 + TypeScript **5.9.3** | TS 7 (nativo) ainda não é compatível com o ecossistema (eslint-config-next, typescript-eslint) |
| Estilo | **Tailwind v4** (`@theme static`) + CSS próprio `.est-*`/`.pg-*` | tokens viram variáveis CSS **e** utilidades (`bg-destaque`, `p-g2`); componentes complexos (dialog, scroll-driven) em CSS à mão |
| Movimento | **CSS scroll-driven** 1ª escolha; **GSAP 3.15** sob demanda; Lenis opcional | CSS não custa JS; GSAP só para pin/SplitText; licença "No Charge" vale (página gratuita) |
| Pop-up | `<dialog>` nativo, carregado por `React.lazy` | acessibilidade de graça; 0 KB no JS inicial; pré-aquecido em idle |
| Grão | tile PNG fixo (CSS) + WebGL próprio só em seções (`Grain`) | tile estático é barato no celular |
| Hospedagem | `vercel.json` + `public/.htaccess` + `NEXT_PUBLIC_BASE_PATH` | funciona em raiz, subpasta e subdomínio |

## 1. Por que Next.js em exportação estática (e não HTML puro, Astro ou Vite)

- **Compartilhar o sistema**: pop-up, máscara de WhatsApp, logos, fotos, tokens e verificador são iguais em toda
  rota. Em HTML puro cada versão tinha sua cópia e as correções (rodadas da cliente) eram repetidas à mão.
- **Estático de verdade**: com `output: 'export'` não existe servidor. O que é dinâmico (formulário, relógio)
  roda no navegador. Hostinger compartilhada hospeda sem Node.
- **Mesma saída na Vercel**: a Vercel detecta o export e serve `out/` na borda com `vercel.json`. Sem ISR/Edge.
- **Ecossistema**: TypeScript, ESLint, Tailwind, `next/font` (preload, fonte-reserva com métricas ajustadas, sem
  Google em tempo de execução), metadados e favicon por convenção.

Trade-offs aceitos:
- **Base de JS maior que HTML puro**: React + runtime do Next ≈ 120 KB gzip; orçamento 150 KB; ficamos em ~135 KB.
  Mitigação: modal em chunk lazy, GSAP/Lenis/WebGL em `import()` em idle, Logo/Photo/Accordion/Reveal em servidor.
- **Sem otimização de imagem em tempo real** (`next/image`): as imagens saem do estúdio em WebP com `srcset` próprio.
- **Pouca folga**: ~15 KB de JS. Regra: nada pesado no topo de arquivo; `npm run size` roda no `check`.

## 2. Alternativas descartadas

| Alternativa | Por que não |
|---|---|
| **HTML puro + um `_shared.js`** | repete código; sem tipos; sem verificação de copy; sem tokens compartilhados |
| **Astro** | ótimo para estático e leve (ilhas); o ganho de ~100 KB de JS não compensa trocar o ferramental. Candidato forte se o orçamento apertar |
| **Next com servidor (SSR/ISR, API routes)** | impossível na Hostinger compartilhada |
| **three.js / React Three Fiber** | 130+ KB gzip para um efeito que um shader de 1,3 KB resolve; pesa no celular de entrada |
| **Framer Motion / Motion** | 40+ KB; CSS `view()` + GSAP sob demanda fazem o mesmo |
| **Remotion** | licença paga acima de 3 funcionários; não é para página |
| **Locomotive / ScrollSmoother** | sequestra a rolagem; atrapalha leitura, âncoras e acessibilidade |
| **Biblioteca de máscara (IMask, libphonenumber)** | 15–80 KB para o que 6 linhas próprias fazem |
| **Biblioteca de modal (Radix, Headless UI)** | `<dialog>` nativo tem foco preso, ESC, `inert`, `::backdrop` e `@starting-style` |
| **Formulário com Server Action** | não existe servidor; POST direto a webhook (Make/n8n) ou `lead.php` |
| **TypeScript 7 / ESLint 10** | peers dos plugins ainda não declaram suporte (mantidos em 5.9.3 e 9.39) |

## 3. Tailwind v4: como usamos

- `@import 'tailwindcss' source(none)` + `@source` explícito (`app`, `components`, `lib`).
- `@theme static` com **reset** das paletas (`--color-*: initial`, também breakpoints, raios e tamanhos): só existem
  as cores e escalas da marca. `static` garante que **todo** token vire variável CSS.
- Tokens da MARCA em `styles/tokens.css` (gerado de `content/marca.json`); tokens FIXOS (quebras, escala de texto,
  espaço 12·24·40, margem, respiro) em `app/globals.css`.
- Tipografia: 5 degraus (label 14, body 18→20, lead 28→44, h2 40→76, h1 40→84) + numerais gigantes. `clamp()` com
  termo em `rem` + `vw` (passa no zoom de 200%).
- Componentes complexos em `styles/components.css` com prefixo `.est-` e variáveis de ajuste (`--btn-radius`,
  `--mq-bg`, `--acc-line`…): a página sobrescreve variável, não o arquivo.

## 4. Movimento: política e custo

- **CSS `animation-timeline: view()`** (`Reveal`): thread do compositor, 0 KB de JS. Reserva por IO
  (`RevealObserver`, ~0,4 KB) só onde `view()` não existe; nada fica `opacity:0` sem JS.
- **GSAP 3.15 por `import()`** em idle (`lib/gsap.ts`, `useGsap`): contexto com cleanup, `?movimento=parado`
  respeitado, `ScrollTrigger.refresh()` após `document.fonts.ready`. ~47 KB gzip em chunks, fora do JS inicial.
- **Lenis** (5 KB, MIT): só desktop com mouse, `NEXT_PUBLIC_SMOOTH_SCROLL=1`. Desligado por padrão.
- **Grão**: o grão FIXO da página inteira é CSS (`body::after`), não WebGL (tile estático; nunca `feTurbulence` animado).
- **Modos**: `total` · `suave` (sistema pede menos movimento) · `parado` (`?movimento=parado`). Movimento SEMPRE ligado.

## 5. Pop-up de captura

- `<dialog>` + `showModal()`: abre **só por clique** (delegação em `[data-open-modal]`); foco no título; ESC fecha;
  clique fora só fecha se nada foi digitado; fechar não apaga os dados; foco volta ao botão.
- **Lazy**: `LeadModal.tsx` (provedor, ~1 KB) no layout; `LeadModalDialog.tsx` é `React.lazy` e aquecido em idle.
- **WhatsApp**: normaliza ao sair do campo, aceita `+55`/`55`/`0`, 67 DDDs, celular de 11 dígitos com 9;
  `type="tel"`, campo ≥ 16 px. Testes em `lib/phone.test.ts`.
- **Erro**: fio de 2 px + ✕ + "Erro:" (nunca só cor), `aria-invalid` + `aria-describedby`, foco no 1º inválido.
- **Envio**: JSON ao endpoint com timeout; 2ª tentativa `no-cors` com o **mesmo `event_id`**; após 2 falhas,
  "Continuar mesmo assim". Modo demo sem endpoint. Isca (honeypot). UTM/fbclid no payload.
- **Consentimento**: texto curto da copy sob o botão, sem caixa (entrega a pedido do titular). Se houver marketing
  posterior, adicionar caixa desmarcada. Confirmar com advogado.
- Safari/iOS **não foi testado** em aparelho: foco ao fechar tem reserva (`opener.focus()`).

## 6. Logo, fotos, fontes

- **Logo**: SVG inline como componente de **servidor** (`currentColor` quando monocromático). `npm run assets` gera
  a tabela a partir de `assets-src/logos/`.
- **Foto**: `<img>` com `srcset`; `priority` = `loading=eager` + `fetchpriority=high` + `decoding=sync`. Largura e
  altura sempre declaradas (CLS 0). Foto recortada é centrada pela TINTA (bbox do alfa).
- **Fontes**: woff2 em subconjunto Latin/PT-BR (`npm run assets`), `font-display: swap`, fonte-reserva com métricas
  ajustadas pelo `next/font`. Fonte "padrão de IA" (Inter, Roboto, Poppins…) não passa na revisão.

## 7. Verificação automática

- `npm run check`: build → servidor estático em porta livre (imita Apache: 301 para barra final, 404.html, gzip) →
  `check_pagina.py` (+ `teste_pagina_total.py` com `--total`) → peso. Código de saída 1 com qualquer erro.
- O `check_pagina.py` reconhece logo em SVG inline pelo atributo `data-logo` e desliga `.est-reveal` antes da
  captura de página inteira (senão tudo abaixo da dobra sai invisível por causa do `view()`).

## 8. Armadilhas encontradas (não repetir)

1. `next/link` + `output: 'export'` + `trailingSlash: true` no Next 16.4: o prefetch pede
   `__next.x.__PAGE__.txt` e o arquivo gerado é `__next.x/__PAGE__.txt` → 404 no console. Usar `<a>`.
2. O Next **não copia** `public/.htaccess` (arquivo oculto): `scripts/postbuild.mjs` copia.
3. Git Bash no Windows converte `/site` em caminho de disco (`NEXT_PUBLIC_BASE_PATH=/site` quebra o build com
   "Missing parameter name"). Use `site` sem a barra (a base normaliza).
4. Servidor estático e `spawnSync` no mesmo processo travam o loop de eventos: o `check` usa `spawn` assíncrono.
5. Grid de uma coluna com filho `nowrap` estoura o container (min-width:auto): usar `minmax(0,1fr)`.
6. `<p>`/`<li>` < 16 px = erro no verificador; rótulos de 14 px vão em `<span>/<small>/<div>`.
7. Provedor do pop-up importando a copy inteira puxava o JSON para todo bundle: chaves e ids ficam em módulos sem texto.
8. `node_modules` como junção para fora da pasta derruba o Turbopack ("Symlink … leaves the filesystem root").
9. `overflow: hidden` prende a linha do tempo `view()`; use `overflow: clip`.
10. `NEXT_PUBLIC_*` é gravado no bundle: ao trocar de variável, apague `.next` (o `site.py pack` já faz).

## 9. O que fica de fora de propósito

Pixel/CAPI reais (só o stub `track()` com `event_id`), QR do grupo no desktop, botão "adicionar à agenda", `.ics`,
página de obrigado separada, JSON-LD. Todos cabem em componentes novos sobre esta base. Relógio/contador de evento:
peça ao estúdio o componente Countdown + lib/event.ts (testado nos 5 estados) ou escreva-o seguindo esta seção.
Teste em Safari/iOS e Firefox: a base usa recursos com reserva (`view()`, `@starting-style`, `::details-content`,
`text-box`) que degradam sem quebrar, mas **não foram vistos** nesses navegadores.
