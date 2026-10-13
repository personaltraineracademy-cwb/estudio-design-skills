import { ButtonCta } from '@/components/ButtonCta'
import { Photo } from '@/components/Photo'
import { copy } from '@/lib/copy'

/**
 * 1ª DOBRA — receita "holofote" (padrao-de-pagina.md §2 + receitas-de-dobra.md):
 * uma coluna, eixo central. IMAGEM (rompendo um disco de destaque) → H1 → apoio → linha mono → BOTÃO → micro.
 * Sem foto: o disco sozinho (a mesma composição). A seção ocupa a tela inteira (.est-dobra + data-hero).
 * Logo só no cabeçalho; nome da marca não repete aqui. Foto = LCP: priority, tamanho declarado, sem animação.
 */
export function Hero() {
  const h = copy.hero
  const img = h.imagem && h.imagem.arquivos.length > 0 ? h.imagem : null
  // proporção da foto (trio largo = 1,8; retrato < 1): a largura da imagem acompanha a altura da janela por ela
  const maior = img ? img.arquivos[img.arquivos.length - 1]! : null
  const ratio = maior ? maior.w / maior.h : 1.8
  // f = 1 / (1/proporção + 0,045): largura que dá ao bloco (foto + ar do topo) a altura (100svh − resto)
  const f = Math.round((1 / (1 / ratio + 0.045)) * 1000) / 1000
  return (
    <section className="est-dobra pg-hero" id="topo" data-hero aria-labelledby="h1">
      <div className="wrap pg-hero__in">
        <div className="pg-holofote" style={{ ['--holo-f' as string]: f }}>
          <div className="pg-holofote__in" data-foto={img ? '' : undefined}>
            <span className="pg-disco" aria-hidden="true" />
            {img ? (
              <Photo
                files={img.arquivos}
                alt={img.alt}
                priority
                sizes="(min-width: 1024px) 940px, (min-width: 600px) 560px, 100vw"
                className="pg-holofote__foto"
              />
            ) : null}
          </div>
        </div>
        <h1 id="h1" className="pg-h1">
          {h.h1}
        </h1>
        {h.sub ? <p className="pg-sub">{h.sub}</p> : null}
        {h.data ? <span className="mono pg-data">{h.data}</span> : null}
        <div className="pg-cta">
          <ButtonCta size="lg" arrow={false} block origem="hero" id="cta-hero">
            {h.cta}
          </ButtonCta>
          {h.micro ? <small className="pg-micro">{h.micro}</small> : null}
        </div>
      </div>
    </section>
  )
}
