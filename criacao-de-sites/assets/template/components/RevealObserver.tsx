'use client'
/**
 * Reserva do <Reveal> para navegadores sem `animation-timeline: view()` (ex.: Firefox sem a flag).
 * Onde o CSS resolve, este componente não faz nada (nem cria observador). Montado uma vez no layout.
 */
import { useEffect } from 'react'
import { usePathname } from 'next/navigation'

export function RevealObserver() {
  const pathname = usePathname()

  useEffect(() => {
    if (typeof CSS !== 'undefined' && CSS.supports('animation-timeline: view()')) return
    if (document.documentElement.getAttribute('data-movimento') === 'parado') return

    const els = Array.from(document.querySelectorAll<HTMLElement>('.est-reveal'))
    if (els.length === 0) return
    const vh = window.innerHeight
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (!e.isIntersecting) continue
          const el = e.target as HTMLElement
          el.dataset.io = 'done'
          io.unobserve(el)
        }
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.08 },
    )
    for (const el of els) {
      // o que já está na tela ao carregar nasce visível (sem piscar)
      if (el.getBoundingClientRect().top < vh) {
        el.dataset.io = 'done'
        continue
      }
      el.dataset.io = 'pending'
      io.observe(el)
    }
    return () => io.disconnect()
  }, [pathname])

  return null
}
