import type { NextConfig } from 'next'

/**
 * Exportação ESTÁTICA: `next build` gera a pasta `out/` (HTML + JS + CSS + imagens).
 * Serve em qualquer hospedagem de arquivos (Vercel, Hostinger/Apache, Netlify, S3…).
 *
 * Proibido neste projeto (quebra o export ou exige servidor): API routes, middleware/proxy,
 * Server Actions, `next/image` com otimização, `revalidate`, rotas dinâmicas sem generateStaticParams.
 */
const rawBase = (process.env.NEXT_PUBLIC_BASE_PATH ?? '').trim().replace(/^\/+|\/+$/g, '')
const basePath = rawBase === '' ? undefined : `/${rawBase}`

const nextConfig: NextConfig = {
  output: 'export',
  basePath, // hospedagem em subpasta (Hostinger): NEXT_PUBLIC_BASE_PATH=site no build (sem barra)
  trailingSlash: true, // /v1/ -> out/v1/index.html (funciona em Apache sem regra de rewrite)
  images: { unoptimized: true },
  reactStrictMode: true,
  productionBrowserSourceMaps: false,
}

export default nextConfig
