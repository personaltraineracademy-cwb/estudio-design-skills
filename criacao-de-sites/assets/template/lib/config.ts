/**
 * Configuração em tempo de build (variáveis NEXT_PUBLIC_*).
 *
 * No build estático (`output: 'export'`) esses valores são GRAVADOS no JavaScript.
 * Mudou uma variável -> `npm run build` de novo e reenvie `out/`.
 * Atenção: o Next só troca `process.env.NEXT_PUBLIC_X` quando o nome aparece escrito por inteiro
 * (não use process.env[nome]).
 */

const clean = (value: string | undefined, fallback: string): string => {
  const t = (value ?? '').trim()
  return t === '' ? fallback : t
}

const leadEndpoint = clean(process.env.NEXT_PUBLIC_LEAD_ENDPOINT, '')

export const config = {
  /** URL que recebe o POST JSON do formulário. Vazio = modo demo (simula sucesso, não envia nada). */
  leadEndpoint,
  /** true quando não há endpoint: o formulário só simula o sucesso. */
  demoMode: leadEndpoint === '',
  /**
   * Destino do botão da tela de sucesso do pop-up (grupo do WhatsApp, página de obrigado, agenda…).
   * NEXT_PUBLIC_DESTINO_URL (novo) ou NEXT_PUBLIC_GROUP_URL (nome antigo, ainda aceito).
   */
  destinoUrl: clean(process.env.NEXT_PUBLIC_DESTINO_URL ?? process.env.NEXT_PUBLIC_GROUP_URL, '#destino'),
  /** URL pública final, sem barra no fim (og:image, canonical). */
  siteUrl: clean(process.env.NEXT_PUBLIC_SITE_URL, 'http://localhost:3000').replace(/\/+$/, ''),
  /** Lenis (rolagem suave) no desktop. */
  smoothScroll: process.env.NEXT_PUBLIC_SMOOTH_SCROLL === '1',
  /** Pede aos buscadores para não indexar (padrão até a versão final). */
  noindex: process.env.NEXT_PUBLIC_NOINDEX !== '0',
} as const

export type SiteConfig = typeof config
