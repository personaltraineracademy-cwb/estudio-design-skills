#!/usr/bin/env node
/**
 * Servidor estático mínimo para `out/` (sem dependências) que imita o comportamento de produção:
 *  - /v1  ->  301 para /v1/  (como o Apache faz com DirectorySlash On e a Vercel com trailingSlash)
 *  - /v1/ ->  out/v1/index.html
 *  - inexistente -> 404.html com status 404
 *  - gzip nos tipos de texto, Cache-Control imutável em /_next/static
 *
 * Uso:  node scripts/serve-out.mjs [--port 4173] [--dir out] [--base /black]
 *       --port 0 escolhe uma porta livre. --base site (sem barra: o Git Bash do Windows converte "/site" em caminho).
 * Importável: import { startServer } from './serve-out.mjs'
 */
import http from 'node:http'
import { createReadStream, existsSync, statSync, readFileSync } from 'node:fs'
import { extname, join, normalize, resolve, sep, dirname } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { gzipSync } from 'node:zlib'

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.map': 'application/json',
}
const COMPRESSIBLE = new Set(['.html', '.js', '.mjs', '.css', '.json', '.txt', '.svg', '.map'])

export function startServer({ dir = 'out', port = 0, base = '' } = {}) {
  const root = resolve(dir)
  // aceita "black" ou "/black" (no Git Bash do Windows o "/black" vira um caminho do disco: prefira "black")
  const prefix = base.replace(/^\/+|\/+$/g, '') === '' ? '' : `/${base.replace(/^\/+|\/+$/g, '')}`
  const server = http.createServer((req, res) => {
    try {
      let pathname = decodeURIComponent(new URL(req.url ?? '/', 'http://x').pathname)
      if (prefix) {
        if (pathname === prefix) {
          res.writeHead(301, { Location: `${prefix}/` }).end()
          return
        }
        if (!pathname.startsWith(`${prefix}/`)) return notFound(req, res)
        pathname = pathname.slice(prefix.length)
      }
      let file = normalize(join(root, pathname))
      if (file !== root && !file.startsWith(root + sep)) return notFound(req, res)
      if (existsSync(file) && statSync(file).isDirectory()) {
        if (!pathname.endsWith('/')) {
          res.writeHead(301, { Location: `${prefix}${pathname}/${new URL(req.url, 'http://x').search}` }).end()
          return
        }
        file = join(file, 'index.html')
      }
      if (!existsSync(file) || !statSync(file).isFile()) return notFound(req, res)
      send(req, res, file, 200)
    } catch {
      res.writeHead(400).end('Bad request')
    }
  })

  function notFound(req, res) {
    const page = join(root, '404.html')
    if (existsSync(page)) return send(req, res, page, 404)
    res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }).end('404')
  }

  function send(req, res, file, status) {
    const ext = extname(file).toLowerCase()
    const headers = { 'content-type': MIME[ext] ?? 'application/octet-stream' }
    if (/[\\/]_next[\\/]static[\\/]/.test(file)) headers['cache-control'] = 'public, max-age=31536000, immutable'
    else if (ext === '.html') headers['cache-control'] = 'no-cache'
    else headers['cache-control'] = 'public, max-age=3600'
    const wantsGzip = /\bgzip\b/.test(req.headers['accept-encoding'] ?? '') && COMPRESSIBLE.has(ext)
    if (wantsGzip) {
      const body = gzipSync(readFileSync(file))
      headers['content-encoding'] = 'gzip'
      headers['content-length'] = body.length
      headers.vary = 'Accept-Encoding'
      res.writeHead(status, headers)
      res.end(req.method === 'HEAD' ? undefined : body)
      return
    }
    headers['content-length'] = statSync(file).size
    res.writeHead(status, headers)
    if (req.method === 'HEAD') return res.end()
    createReadStream(file).pipe(res)
  }

  return new Promise((resolvePromise, reject) => {
    server.once('error', reject)
    server.listen(port, '127.0.0.1', () => {
      const actual = server.address().port
      resolvePromise({ server, port: actual, url: `http://localhost:${actual}${prefix}`, close: () => new Promise((r) => server.close(() => r())) })
    })
  })
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href
if (isMain) {
  const arg = (name, fallback) => {
    const i = process.argv.indexOf(`--${name}`)
    return i >= 0 ? process.argv[i + 1] : fallback
  }
  const here = dirname(fileURLToPath(import.meta.url))
  const dir = resolve(here, '..', arg('dir', 'out'))
  if (!existsSync(dir)) {
    console.error(`Pasta ${dir} não existe. Rode "npm run build" antes.`)
    process.exit(1)
  }
  const { url } = await startServer({ dir, port: Number(arg('port', '4173')), base: arg('base', '') })
  console.log(`Servindo ${dir}\n${url}/  (Ctrl+C para parar)`)
}
