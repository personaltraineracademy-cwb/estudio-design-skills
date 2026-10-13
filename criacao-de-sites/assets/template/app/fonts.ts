/**
 * Fontes da marca, locais (nada de Google Fonts em tempo de execução), woff2 em subconjunto Latin/PT-BR.
 * ARQUIVO GERADO por scripts/build-assets.py a partir de content/marca.json — não editar à mão
 *   display  Big Shoulders 900
 *   text     Archivo 500/800
 *   mono     Azeret Mono
 * next/font/local gera @font-face com `font-display: swap`, preload e fonte-reserva com métricas ajustadas.
 */
import localFont from 'next/font/local'

export const display = localFont({
  src: './fonts/display.woff2',
  weight: '900',
  style: 'normal',
  display: 'swap',
  variable: '--font-display-next',
  fallback: ['system-ui', 'sans-serif'],
})

export const text = localFont({
  src: [{ path: './fonts/texto-500.woff2', weight: '500', style: 'normal' }, { path: './fonts/texto-800.woff2', weight: '800', style: 'normal' }],
  display: 'swap',
  variable: '--font-text-next',
  fallback: ['system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
})

export const mono = localFont({
  src: [{ path: './fonts/mono-500.woff2', weight: '500', style: 'normal' }, { path: './fonts/mono-600.woff2', weight: '600', style: 'normal' }],
  display: 'swap',
  variable: '--font-mono-next',
  preload: false,
  fallback: ['ui-monospace', 'Consolas', 'monospace'],
})

/** Classes das 3 variáveis para o <html>. */
export const fontVariables = `${display.variable} ${text.variable} ${mono.variable}`
