import type { CSSProperties, ElementType, ReactNode } from 'react'

/**
 * Revelação ao rolar. Componente de SERVIDOR (só marca o elemento com a classe).
 *
 * 1ª escolha: CSS scroll-driven (`animation-timeline: view()`), sem JavaScript, na thread do compositor.
 * Reserva: `RevealObserver` (montado no layout) usa IntersectionObserver só onde `view()` não existe.
 * Com prefers-reduced-motion: nada anima, o conteúdo já está no lugar. Sem JS: tudo visível.
 *
 * Regras (pesquisa 19 §4): só opacity + transform; <= 600 ms; NUNCA no elemento do LCP (foto/título do hero)
 * nem em texto legal; `index` escalona itens irmãos (cada +1 atrasa a entrada em ~6% do trecho visível).
 */
export interface RevealProps {
  as?: ElementType
  index?: number
  className?: string
  children: ReactNode
  id?: string
}

export function Reveal({ as: Tag = 'div', index = 0, className, children, id }: RevealProps) {
  const style = index > 0 ? ({ ['--rv' as string]: Math.min(index, 8) } as CSSProperties) : undefined
  return (
    <Tag id={id} className={['est-reveal', className].filter(Boolean).join(' ')} style={style}>
      {children}
    </Tag>
  )
}
