import { Accordion } from '@/components/Accordion'
import { copy } from '@/lib/copy'

/** FAQ acessível (<details> nativo, 0 JS) sobre papel. Máx. 8 perguntas. */
export function Faq() {
  const s = copy.faq
  if (!s || s.itens.length === 0) return null
  return (
    <section className="sec est-paper pg-faq" id="perguntas" aria-labelledby="faq-t">
      <div className="wrap pg-faq__in">
        <h2 id="faq-t" className="pg-titulo">
          {s.titulo}
        </h2>
        <Accordion items={s.itens} exclusive />
      </div>
    </section>
  )
}
