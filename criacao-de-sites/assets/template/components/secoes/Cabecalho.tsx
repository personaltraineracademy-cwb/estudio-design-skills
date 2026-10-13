import { ButtonCta } from '@/components/ButtonCta'
import { Logo } from '@/components/Logo'
import { copy } from '@/lib/copy'
import { withBase } from '@/lib/url'
import { UI } from '@/lib/ui-text'

/**
 * Cabeçalho: logo à esquerda (a ÚNICA da dobra) · botão pequeno à direita. Mesma margem do conteúdo (.wrap).
 * Logo 32 px (celular) / 40 px (>= 768) com área de respiro; o link leva ao topo.
 */
export function Cabecalho() {
  return (
    <header className="pg-cab">
      <div className="wrap pg-cab__in">
        <a className="pg-cab__logo" href={withBase('/')} aria-label={copy.meta?.nome ?? UI.home}>
          <Logo tone="claro" label="" />
        </a>
        <ButtonCta size="bar" arrow={false} origem="cabecalho">
          {copy.cabecalho?.botao ?? copy.hero.cta}
        </ButtonCta>
      </div>
    </header>
  )
}
