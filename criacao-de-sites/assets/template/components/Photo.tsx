import type { ImagemArquivo } from '@/lib/copy'
import { withBase } from '@/lib/url'

/**
 * Foto real em <img> com srcset. Componente de SERVIDOR.
 *
 *   <Photo files={copy.hero.imagem.arquivos} alt={copy.hero.imagem.alt} priority sizes="(min-width:1024px) 940px, 100vw" />
 *
 * - `files`: 1–3 larguras, da menor para a maior (WebP; recorte com alfa quando for pessoa/produto).
 * - `priority`: imagem do LCP (hero) -> loading="eager" + fetchpriority="high" + decoding="sync". Todas as outras: lazy.
 * - Largura/altura SEMPRE declaradas (CLS 0). `sizes` = o que o CSS realmente dá à imagem.
 * - NUNCA gerar pessoa por IA: foto de gente é sempre real. IA só para cenário/textura/forma.
 */
export interface PhotoProps {
  files: readonly ImagemArquivo[]
  alt: string
  priority?: boolean
  sizes?: string
  className?: string
}

export function Photo({ files, alt, priority, sizes = '100vw', className }: PhotoProps) {
  if (files.length === 0) return null
  const last = files[files.length - 1]!
  const first = files[0]!
  const srcSet = files.map((f) => `${withBase(f.src)} ${f.w}w`).join(', ')
  return (
    <img
      className={['est-photo', className].filter(Boolean).join(' ')}
      src={withBase(files.length > 1 ? last.src : first.src)}
      srcSet={files.length > 1 ? srcSet : undefined}
      sizes={files.length > 1 ? sizes : undefined}
      width={last.w}
      height={last.h}
      alt={alt}
      loading={priority ? 'eager' : 'lazy'}
      decoding={priority ? 'sync' : 'async'}
      fetchPriority={priority ? 'high' : 'auto'}
    />
  )
}
