import type { ButtonHTMLAttributes, ReactNode } from 'react'

/**
 * Botão de ação. Componente de SERVIDOR (zero JS próprio).
 *
 * - Abre o pop-up de captura: o `LeadModalProvider` escuta cliques em `[data-open-modal]`.
 * - `contexto` mostra uma etiqueta no pop-up (ex.: o item escolhido no cartão) e vai no payload do formulário.
 * - `origem` identifica o botão nos eventos (hero, barra, cartao-x, final…).
 * - Alvo >= 48 px (bar) ou >= 56 px (padrão). Sombra dura SÓ em elemento clicável (é este).
 * - Raio: 0 por padrão (reto = sinal da marca). Troque por versão com `--btn-radius`.
 * - Com `href` vira link (<a>) e NÃO abre o pop-up.
 */
export interface ButtonCtaProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'type' | 'children'> {
  children: ReactNode
  tone?: 'destaque' | 'papel' | 'tinta' | 'ink' | 'ghost'
  size?: 'md' | 'lg' | 'bar'
  /** seta no fim (padrão: sim, exceto size="bar") */
  arrow?: boolean
  block?: boolean
  contexto?: string
  origem?: string
  href?: string
  target?: string
  rel?: string
}

function Arrow() {
  return (
    <svg className="est-btn__arrow" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      <path d="M1 8h13M9 2.5 14.5 8 9 13.5" />
    </svg>
  )
}

export function ButtonCta({
  children,
  tone = 'destaque',
  size = 'md',
  arrow,
  block,
  contexto,
  origem,
  href,
  target,
  rel,
  className,
  ...rest
}: ButtonCtaProps) {
  const showArrow = arrow ?? size !== 'bar'
  const cls = [
    'est-btn',
    tone !== 'destaque' && `est-btn--${tone}`,
    size !== 'md' && `est-btn--${size}`,
    block && 'est-btn--block',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  if (href) {
    return (
      <a className={cls} href={href} target={target} rel={rel ?? (target === '_blank' ? 'noopener noreferrer' : undefined)}>
        {children}
        {showArrow && <Arrow />}
      </a>
    )
  }

  return (
    <button
      type="button"
      className={cls}
      data-open-modal=""
      data-contexto={contexto}
      data-origem={origem}
      aria-haspopup="dialog"
      {...rest}
    >
      {children}
      {showArrow && <Arrow />}
    </button>
  )
}
