'use client'
import { useEffect } from 'react'
import { config } from '@/lib/config'
import { whenIdle } from '@/lib/idle'

/**
 * Rolagem suave (Lenis 1.3, MIT) — OPCIONAL e só no desktop.
 *
 * Liga somente se: NEXT_PUBLIC_SMOOTH_SCROLL=1 (ou prop `enabled`), tela >= 1024 px, ponteiro fino com hover
 * e sem prefers-reduced-motion. Carregado por import dinâmico em idle (0 KB no JS inicial).
 * Lenis só interpola a rolagem nativa: animações CSS `view()` e ScrollTrigger continuam funcionando.
 * Dentro do pop-up (`data-lenis-prevent`) a rolagem é a nativa.
 */
export function SmoothScroll({ enabled = config.smoothScroll }: { enabled?: boolean }) {
  useEffect(() => {
    if (!enabled) return
    const mq = window.matchMedia('(min-width: 1024px) and (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)')
    let stop: (() => void) | undefined
    let cancelled = false

    const start = async () => {
      if (!mq.matches || stop) return
      const { default: Lenis } = await import('lenis')
      if (cancelled || !mq.matches) return
      const lenis = new Lenis({ lerp: 0.1, wheelMultiplier: 1, smoothWheel: true })
      let raf = 0
      const loop = (t: number) => {
        lenis.raf(t)
        raf = requestAnimationFrame(loop)
      }
      raf = requestAnimationFrame(loop)
      document.documentElement.classList.add('lenis', 'lenis-smooth')
      stop = () => {
        cancelAnimationFrame(raf)
        lenis.destroy()
        document.documentElement.classList.remove('lenis', 'lenis-smooth')
        stop = undefined
      }
    }

    const cancelIdle = whenIdle(() => void start())
    const onChange = () => {
      if (mq.matches) void start()
      else stop?.()
    }
    mq.addEventListener('change', onChange)
    return () => {
      cancelled = true
      cancelIdle()
      mq.removeEventListener('change', onChange)
      stop?.()
    }
  }, [enabled])

  return null
}
