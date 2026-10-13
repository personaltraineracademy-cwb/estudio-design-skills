import { Logo } from '@/components/Logo'
import { copy } from '@/lib/copy'

/** Rodapé: logo pequena + texto legal da copy. `.pb-sticky` reserva espaço para a barra fixa do celular. */
export function Rodape() {
  return (
    <footer className="pg-rodape pb-sticky">
      <div className="wrap pg-rodape__in">
        <Logo tone="claro" height={28} label={copy.meta?.nome ?? ''} />
        {copy.rodape ? <p className="pg-rodape__t">{copy.rodape}</p> : null}
      </div>
    </footer>
  )
}
