'use client'
import { useEffect, useState, type ReactNode } from 'react'
import { ButtonCta } from './ButtonCta'

/**
 * Barra de CTA fixa no rodapé do MOBILE (< 768 px). Só aparece depois de rolar além do hero
 * (senão cobre as fotos e duplica o botão da dobra — paginas-de-captura.md §4c).
 *
 * - `after`: seletor do elemento do hero (padrão `[data-hero]`). Enquanto ele estiver na tela, a barra fica oculta.
 * - Some sozinha com o pop-up aberto (CSS `body:has(dialog[open])`) e respeita a área segura do iPhone.
 * - Oculta de verdade (visibility + inert): não entra na ordem de foco quando está escondida.
 * - Reserve espaço no fim da página com a classe `pb-sticky` (no rodapé) para não cobrir o conteúdo.
 */
export interface StickyCtaProps {
  children: ReactNode
  after?: string
  origem?: string
}

export function StickyCta({ children, after = '[data-hero]', origem = 'barra-fixa' }: StickyCtaProps) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const hero = document.querySelector(after)
    if (!hero) {
      const onScroll = () => setVisible(window.scrollY > window.innerHeight * 0.8)
      onScroll()
      window.addEventListener('scroll', onScroll, { passive: true })
      return () => window.removeEventListener('scroll', onScroll)
    }
    const io = new IntersectionObserver(([entry]) => {
      if (!entry) return
      // fora da tela E acima do viewport (já passou) = mostra
      setVisible(!entry.isIntersecting && entry.boundingClientRect.bottom < 0)
    })
    io.observe(hero)
    return () => io.disconnect()
  }, [after])

  return (
    <div className="est-sticky" data-visible={visible} inert={!visible}>
      <ButtonCta size="bar" arrow={false} block origem={origem} tone="destaque">
        {children}
      </ButtonCta>
    </div>
  )
}
