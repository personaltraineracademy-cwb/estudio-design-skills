#!/usr/bin/env node
/**
 * Verificação completa: build -> servidor estático em porta livre -> check_pagina.py (contrato de design)
 * [-> teste_pagina_total.py (bateria: larguras, pop-up, movimento)] -> peso.
 *
 *   npm run check                       build + check_pagina em "/"
 *   npm run check -- --no-build         reaproveita o out/ existente
 *   npm run check -- --total            também roda a bateria teste_pagina_total.py (mais lenta)
 *   npm run check -- --total --rapido   bateria com menos larguras
 *   npm run check -- --routes /,/obrigado/   outras rotas
 *   npm run check -- --base site        serve em /site/ (build com NEXT_PUBLIC_BASE_PATH=site: use `site.py check --subpasta`)
 *
 * Saída: .check/<rota>/ (PNGs por largura, _relatorio.json, _teste-total.json) + .check/resumo.json.
 * Código de saída 1 se houver ERRO (avisos são perguntas a responder, não reprovam).
 * Verificadores do estúdio: CHECK_PAGINA (arquivo check_pagina.py) ou CHECK_DIR (pasta com os dois .py).
 */
import { spawn, spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { startServer } from './serve-out.mjs'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

/** Roda um processo SEM travar o loop de eventos (o servidor estático vive neste mesmo processo). */
function run(cmd, args, options = {}) {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, options)
    let stdout = ''
    let stderr = ''
    child.stdout?.on('data', (d) => (stdout += d))
    child.stderr?.on('data', (d) => (stderr += d))
    child.on('close', (status) => resolve({ status, stdout, stderr }))
    child.on('error', (e) => resolve({ status: 1, stdout, stderr: String(e) }))
  })
}
const args = process.argv.slice(2)
const flag = (n) => args.includes(`--${n}`)
const opt = (n, d) => {
  const i = args.indexOf(`--${n}`)
  return i >= 0 ? args[i + 1] : d
}

function acharDir() {
  const cands = [
    process.env.CHECK_DIR,
    process.env.CHECK_PAGINA ? dirname(process.env.CHECK_PAGINA) : null,
    join(homedir(), '.claude', 'skills', 'direcao-de-arte', 'scripts'),
  ].filter(Boolean)
  return cands.find((d) => existsSync(join(d, 'check_pagina.py'))) ?? null
}

const dir = acharDir()
const routes = opt('routes', '/').split(',').map((s) => s.trim()).filter(Boolean)
const base = opt('base', '')
const outDir = join(root, '.check')
mkdirSync(outDir, { recursive: true })

if (!flag('no-build')) {
  console.log('> npm run build')
  const b = spawnSync('npm', ['run', 'build'], { cwd: root, stdio: 'inherit', shell: true })
  if (b.status !== 0) {
    console.error('Build falhou.')
    process.exit(1)
  }
}
if (!existsSync(join(root, 'out', 'index.html'))) {
  console.error('out/ não existe.')
  process.exit(1)
}
if (!dir) {
  console.error('check_pagina.py não encontrado (defina CHECK_DIR ou CHECK_PAGINA).')
  process.exit(1)
}

const { url, close, port } = await startServer({ dir: join(root, 'out'), port: 0, base })
console.log(`\nservidor estático em ${url} (porta ${port})`)

const env = { ...process.env, PYTHONIOENCODING: 'utf-8' }
const lerJson = (p) => {
  try {
    return JSON.parse(readFileSync(p, 'utf8'))
  } catch {
    return null
  }
}
const summary = []
let failed = false
for (const r of routes) {
  const clean = r.replace(/^\/+|\/+$/g, '')
  const slug = clean === '' ? 'home' : clean.replace(/\//g, '_')
  const target = `${url}/${clean === '' ? '' : clean + '/'}`
  const dest = join(outDir, slug)
  mkdirSync(dest, { recursive: true })

  console.log(`\n=== ${slug}: check_pagina  ${target}`)
  const p = await run('python', [join(dir, 'check_pagina.py'), target, '-o', dest], { env })
  process.stdout.write(p.stdout ?? '')
  if (p.stderr) process.stderr.write(p.stderr)
  const rel = lerJson(join(dest, '_relatorio.json'))
  const row = {
    rota: r,
    check: { erros: rel?.erros?.length ?? (p.status === 0 ? 0 : 1), avisos: rel?.avisos?.length ?? 0, saida: p.status },
  }
  if (row.check.erros > 0 || p.status !== 0) failed = true

  if (flag('total') && existsSync(join(dir, 'teste_pagina_total.py'))) {
    console.log(`\n=== ${slug}: teste_pagina_total`)
    const targs = [join(dir, 'teste_pagina_total.py'), target, '-o', join(dest, 'total')]
    if (flag('rapido')) targs.push('--rapido')
    const t = await run('python', targs, { env })
    process.stdout.write(t.stdout ?? '')
    if (t.stderr) process.stderr.write(t.stderr)
    const rt = lerJson(join(dest, 'total', '_teste-total.json'))
    row.total = { erros: rt?.erros?.length ?? (t.status === 0 ? 0 : 1), avisos: rt?.avisos?.length ?? 0, saida: t.status }
    if (row.total.erros > 0 || t.status !== 0) failed = true
  }
  summary.push(row)
}
await close()

console.log('\n=== peso por rota')
const size = spawnSync('node', [join(root, 'scripts', 'size.mjs'), ...routes.map((r) => (r.endsWith('/') ? r : r + '/'))], {
  cwd: root,
  stdio: 'inherit',
}) // servidor já fechado
if (size.status !== 0) failed = true

writeFileSync(join(outDir, 'resumo.json'), JSON.stringify({ summary, sizeOk: size.status === 0 }, null, 2))
console.log('\n=== resumo')
for (const s of summary) {
  const tot = s.total ? `  · bateria: erros=${s.total.erros} avisos=${s.total.avisos}` : ''
  console.log(`${s.rota.padEnd(10)} check_pagina: erros=${s.check.erros} avisos=${s.check.avisos}${tot}`)
}
console.log(`peso: ${size.status === 0 ? 'dentro do orçamento' : 'ACIMA do orçamento'}`)
process.exit(failed ? 1 : 0)
