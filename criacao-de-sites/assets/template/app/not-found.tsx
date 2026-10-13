import { Logo } from '@/components/Logo'
import { withBase } from '@/lib/url'
import { UI } from '@/lib/ui-text'

/** Vira out/404.html no export (Vercel e Apache usam como página de erro). Texto neutro de interface. */
export default function NotFound() {
  return (
    <main id="conteudo" className="wrap grid min-h-svh content-center gap-g2 py-secao">
      <Logo height={40} />
      <h1 className="mt-g3 max-w-[12ch] text-h2">{UI.notFound.titulo}</h1>
      <p className="text-mute">{UI.notFound.texto}</p>
      <p className="mt-g1">
        <a href={withBase('/')} className="est-btn">
          {UI.notFound.voltar}
        </a>
      </p>
    </main>
  )
}
