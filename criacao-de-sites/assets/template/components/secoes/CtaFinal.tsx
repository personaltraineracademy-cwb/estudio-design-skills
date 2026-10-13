import { ButtonCta } from '@/components/ButtonCta'
import { Reveal } from '@/components/Reveal'
import { copy } from '@/lib/copy'

/** Fecho: UMA ideia só (frase + botão). Sem textura atrás do texto, sem numerais, sem segunda camada. */
export function CtaFinal() {
  const s = copy.cta_final
  if (!s) return null
  return (
    <section className="sec pg-final" id="final" aria-labelledby="final-t">
      <div className="wrap pg-final__in">
        <Reveal as="h2" id="final-t" className="pg-final__t">
          {s.titulo}
        </Reveal>
        <ButtonCta size="lg" arrow={false} origem="final">
          {s.botao}
        </ButtonCta>
      </div>
    </section>
  )
}
