import type { MetadataRoute } from 'next'
import { config } from '@/lib/config'

export const dynamic = 'force-static' // obrigatório com output: 'export'

/** robots.txt gerado no build: segue NEXT_PUBLIC_NOINDEX (padrão 1 = não indexar). */
export default function robots(): MetadataRoute.Robots {
  return config.noindex
    ? { rules: { userAgent: '*', disallow: '/' } }
    : { rules: { userAgent: '*', allow: '/' } }
}
