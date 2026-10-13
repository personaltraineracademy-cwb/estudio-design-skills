/**
 * FAQ acessível com <details>/<summary> nativos. Componente de SERVIDOR: zero JavaScript.
 *
 * - Teclado e leitor de tela de graça (Enter/Espaço abrem; foco visível no <summary>).
 * - `exclusive` usa o atributo `name` (grupo): abrir um fecha os outros (Chrome 120+, Safari 17.2+).
 * - Lista limpa com fios finos, não caixas (C10). Altura anima com ::details-content (Chrome 131+);
 *   nos demais abre sem animação.
 * - A resposta é <div> (não <p>) e some do layout quando fechada: o verificador não conta resposta fechada como bloco.
 * - Variáveis: --acc-line (fio de cima), --acc-line-soft (entre itens), --acc-text (resposta).
 */
export interface AccordionItem {
  q: string
  a: string
}

export interface AccordionProps {
  items: readonly AccordionItem[]
  exclusive?: boolean
  /** índice (0-based) do item que nasce aberto */
  defaultOpen?: number
  className?: string
}

export function Accordion({ items, exclusive = false, defaultOpen, className }: AccordionProps) {
  return (
    <div className={['est-acc', className].filter(Boolean).join(' ')}>
      {items.map((item, i) => (
        <details key={item.q} className="est-acc__item" name={exclusive ? 'faq' : undefined} open={defaultOpen === i || undefined}>
          <summary>
            <span>{item.q}</span>
            <span className="est-acc__icon" aria-hidden="true" />
          </summary>
          <div className="est-acc__body">{item.a}</div>
        </details>
      ))}
    </div>
  )
}
