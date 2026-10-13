import { Reveal } from '@/components/Reveal'
import { copy } from '@/lib/copy'

/** Lista limpa (fios finos, não caixas — regra C10): título à esquerda, texto à direita no desktop. */
export function Destaques() {
  const s = copy.destaques
  if (!s || s.itens.length === 0) return null
  return (
    <section className="sec pg-destaques" id="detalhes" aria-labelledby="dest-t">
      <div className="wrap">
        <h2 id="dest-t" className="pg-titulo">
          {s.titulo}
        </h2>
        <ul className="pg-lista">
          {s.itens.map((it, i) => (
            <Reveal as="li" key={it.t} index={i} className="pg-lista__item">
              <h3>{it.t}</h3>
              <p>{it.d}</p>
            </Reveal>
          ))}
        </ul>
      </div>
    </section>
  )
}
