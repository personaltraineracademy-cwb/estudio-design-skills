/**
 * Caminho base para hospedar em SUBPASTA (ex.: seudominio.com/site/).
 * Defina NEXT_PUBLIC_BASE_PATH=site ANTES do build (sem barra: o Git Bash do Windows converte "/site" em caminho
 * de disco; a barra é normalizada aqui); vazio = raiz do domínio.
 * `next/link` e os arquivos de /_next já recebem o prefixo sozinhos; `<img>` e `<a href>` comuns NÃO:
 * use `withBase('/img/arquivo.webp')` para qualquer caminho que comece com "/".
 */
const raw = (process.env.NEXT_PUBLIC_BASE_PATH ?? '').trim()
export const BASE_PATH = raw === '' || raw === '/' ? '' : `/${raw.replace(/^\/+|\/+$/g, '')}`

export function withBase(path: string): string {
  if (!path.startsWith('/') || path.startsWith('//')) return path
  return `${BASE_PATH}${path}`
}
