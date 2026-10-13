#!/usr/bin/env node
/**
 * Roda depois do `next build`:
 *  - copia public/.htaccess para out/.htaccess (o Next não copia arquivos que começam com ponto);
 *  - com NEXT_PUBLIC_BASE_PATH (subpasta), troca o `ErrorDocument 404` do .htaccess pelo caminho com a subpasta;
 *  - confere que o export tem o essencial (index.html, 404.html).
 */
import { copyFileSync, existsSync, readFileSync, writeFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const out = join(root, 'out')

if (!existsSync(out)) {
  console.error('postbuild: out/ não existe (o build falhou ou output:"export" saiu do next.config.ts).')
  process.exit(1)
}
const base = (process.env.NEXT_PUBLIC_BASE_PATH ?? '').trim().replace(/^\/+|\/+$/g, '')
const ht = join(root, 'public', '.htaccess')
if (existsSync(ht)) {
  const dest = join(out, '.htaccess')
  copyFileSync(ht, dest)
  if (base !== '') {
    const t = readFileSync(dest, 'utf8').replace(/^ErrorDocument 404 .*$/m, `ErrorDocument 404 /${base}/404.html`)
    writeFileSync(dest, t)
    console.log(`postbuild: .htaccess copiado (ErrorDocument 404 -> /${base}/404.html)`)
  } else {
    console.log('postbuild: .htaccess copiado para out/')
  }
}
const must = ['index.html', '404.html']
const missing = must.filter((f) => !existsSync(join(out, f)))
if (missing.length) {
  console.error('postbuild: faltam no export:', missing.join(', '))
  process.exit(1)
}
console.log('postbuild: export ok (' + must.length + ' arquivos essenciais)')
