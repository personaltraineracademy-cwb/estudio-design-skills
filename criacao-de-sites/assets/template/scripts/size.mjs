#!/usr/bin/env node
/**
 * Mede o peso INICIAL de cada rota do export (out/): JS e CSS referenciados pelo HTML, em gzip,
 * mais o HTML, as fontes e a imagem do hero. Compara com o orçamento:
 *   JS inicial <= 150 KB gzip · CSS <= 40 KB gzip · (HTML <= 120 KB bruto com a logo inline)
 *
 * Uso: node scripts/size.mjs [rota ...]      (padrão: /)
 * Saída: tabela + JSON em .check/size.json. Código de saída 1 se estourar o orçamento.
 */
import { readFileSync, existsSync, mkdirSync, writeFileSync } from 'node:fs'
import { gzipSync } from 'node:zlib'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const out = join(root, 'out')
const BUDGET = { js: 150, css: 40 }
const routes = process.argv.slice(2).length ? process.argv.slice(2) : ['/']

if (!existsSync(out)) {
  console.error('out/ não existe. Rode `npm run build` antes.')
  process.exit(2)
}

const gz = (buf) => gzipSync(buf, { level: 9 }).length
const kb = (n) => (n / 1024).toFixed(1)
const fileOf = (url) => join(out, decodeURIComponent(url.split('?')[0]).replace(/^\//, ''))

const rows = []
let failed = false
for (const route of routes) {
  const htmlPath = join(out, route.replace(/^\//, ''), 'index.html')
  if (!existsSync(htmlPath)) {
    console.error(`sem ${htmlPath}`)
    continue
  }
  const html = readFileSync(htmlPath, 'utf8')
  const js = new Set()
  const css = new Set()
  const fonts = new Set()
  // scripts `noModule` (polyfills) só baixam em navegador antigo: fora da conta
  for (const m of html.matchAll(/<script[^>]+src="([^"]+\.js[^"]*)"[^>]*>/g)) if (!/noModule/i.test(m[0])) js.add(m[1])
  for (const m of html.matchAll(/<link[^>]+rel="preload"[^>]+as="script"[^>]+href="([^"]+)"/g)) js.add(m[1])
  for (const m of html.matchAll(/<link[^>]+href="([^"]+\.css[^"]*)"[^>]*>/g)) css.add(m[1])
  for (const m of html.matchAll(/<link[^>]+as="font"[^>]+href="([^"]+)"/g)) fonts.add(m[1])
  for (const m of html.matchAll(/<link[^>]+href="([^"]+\.woff2)"[^>]*>/g)) fonts.add(m[1])

  const sum = (set) => [...set].reduce((a, u) => (existsSync(fileOf(u)) ? a + gz(readFileSync(fileOf(u))) : a), 0)
  const jsGz = sum(js)
  const cssGz = sum(css)
  const fontsRaw = [...fonts].reduce((a, u) => (existsSync(fileOf(u)) ? a + readFileSync(fileOf(u)).length : a), 0)
  const row = {
    route,
    html_kb: +kb(Buffer.byteLength(html)),
    html_gz_kb: +kb(gz(Buffer.from(html))),
    js_files: js.size,
    js_gz_kb: +kb(jsGz),
    css_gz_kb: +kb(cssGz),
    fonts_preloaded_kb: +kb(fontsRaw),
  }
  row.ok = row.js_gz_kb <= BUDGET.js && row.css_gz_kb <= BUDGET.css
  if (!row.ok) failed = true
  rows.push(row)
}

const pad = (v, n) => String(v).padEnd(n)
console.log(`${pad('rota', 8)}${pad('HTML kb', 10)}${pad('HTML gz', 10)}${pad('JS gz', 10)}${pad('CSS gz', 10)}${pad('fontes pré', 12)}orçamento`)
for (const r of rows) {
  console.log(
    `${pad(r.route, 8)}${pad(r.html_kb, 10)}${pad(r.html_gz_kb, 10)}${pad(r.js_gz_kb, 10)}${pad(r.css_gz_kb, 10)}${pad(r.fonts_preloaded_kb, 12)}${r.ok ? 'ok' : 'ESTOUROU'}`,
  )
}
console.log(`\norçamento: JS <= ${BUDGET.js} KB gzip · CSS <= ${BUDGET.css} KB gzip`)

mkdirSync(join(root, '.check'), { recursive: true })
writeFileSync(join(root, '.check', 'size.json'), JSON.stringify({ budget: BUDGET, rows }, null, 2))
process.exit(failed ? 1 : 0)
