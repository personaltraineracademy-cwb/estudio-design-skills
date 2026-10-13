import { Reveal } from '@/components/Reveal'
import { copy } from '@/lib/copy'

/** Passos numerados sobre papel. Revelação por rolagem em CSS (0 JS). Numeral = desenho (aria-hidden). */
export function Passos() {
  const s = copy.passos
  if (!s || s.itens.length === 0) return null
  return (
    <section className="sec est-paper pg-passos" id="como" aria-labelledby="passos-t">
      <div className="wrap">
        <h2 id="passos-t" className="pg-titulo">
          {s.titulo}
        </h2>
        <ol className="pg-passos__lista">
          {s.itens.map((p, i) => (
            <Reveal as="li" key={p.t} index={i} className="pg-passo">
              <span className="pg-passo__n" aria-hidden="true">
                {String(i + 1).padStart(2, '0')}
              </span>
              <h3 className="pg-passo__t">{p.t}</h3>
              <p className="pg-passo__d">{p.d}</p>
            </Reveal>
          ))}
        </ol>
      </div>
    </section>
  )
}
