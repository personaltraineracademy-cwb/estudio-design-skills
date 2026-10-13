'use client'
import { useState } from 'react'
import { UI } from '@/lib/ui-text'

/**
 * Faixa rolante (costura entre seções). Movimento em CSS puro; o único estado é o botão de pausa.
 *
 * - WCAG 2.2.2: tudo que se move por mais de 5 s tem pausa visível (alvo >= 48 px) — o botão à direita.
 * - prefers-reduced-motion: não anima; o texto quebra linha e a 2ª cópia some (CSS).
 * - Leitor de tela lê UMA vez: a cópia do loop é aria-hidden.
 * - Só abaixo da dobra (nunca dentro da 1ª tela; >= 48 px de ar até o hero).
 * - Variáveis: --mq-bg, --mq-fg, --dur (duração do ciclo; maior = mais lento).
 */
export interface MarqueeProps {
  items: readonly string[]
  /** segundos por ciclo (padrão 40) */
  duration?: number
  className?: string
}

export function Marquee({ items, duration = 40, className }: MarqueeProps) {
  const [paused, setPaused] = useState(false)
  const group = (hidden: boolean) => (
    <div className="est-marquee__group" aria-hidden={hidden || undefined}>
      {items.map((t) => (
        <span key={`${hidden}-${t}`} className="contents">
          <span className="est-marquee__item">{t}</span>
          <i className="est-marquee__sep" aria-hidden="true" />
        </span>
      ))}
    </div>
  )
  return (
    <div
      className={['est-marquee', className].filter(Boolean).join(' ')}
      data-paused={paused}
      style={{ ['--dur' as string]: `${duration}s` }}
    >
      <div className="est-marquee__viewport">
        <div className="est-marquee__track">
          {group(false)}
          {group(true)}
        </div>
      </div>
      <button
        type="button"
        className="est-marquee__pause"
        aria-pressed={paused}
        aria-label={paused ? UI.resumeMotion : UI.pauseMotion}
        onClick={() => setPaused((p) => !p)}
      />
    </div>
  )
}
