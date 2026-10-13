'use client'
/**
 * Pop-up de captura — provedor + hook. O <dialog> em si fica em LeadModalDialog.tsx e é carregado
 * sob demanda (React.lazy): não pesa no JavaScript inicial; é pré-carregado quando o navegador fica ocioso.
 *
 * COMO USAR
 *   1. O layout já envolve a página com <LeadModalProvider>.
 *   2. Qualquer elemento com `data-open-modal` abre o pop-up (é o que <ButtonCta> renderiza):
 *        <button data-open-modal data-contexto="Item escolhido" data-origem="cartao-1">…</button>
 *   3. Ou por código, em componente cliente:  const { open } = useLeadModal();  open({ contexto: 'Item escolhido' })
 *
 * REGRAS (pesquisa 18 §2): abre SÓ por clique (nunca ao carregar nem ao sair) · foco no título · ESC fecha ·
 * clique fora NÃO fecha · fechar não apaga o que foi digitado · foco volta ao botão que abriu.
 */
import {
  createContext,
  lazy,
  Suspense,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { whenIdle } from '@/lib/idle'
import { track } from '@/lib/analytics'

const loadDialog = () => import('./LeadModalDialog')
const LeadModalDialog = lazy(loadDialog)

export interface OpenOptions {
  /** etiqueta mostrada no pop-up (ex.: o item escolhido) e enviada no payload */
  contexto?: string
  /** de onde veio o clique (hero, barra, cartao-1, final…) */
  origem?: string
}

export interface LeadModalApi {
  open: (options?: OpenOptions) => void
  close: () => void
  isOpen: boolean
}

const noop = () => {}
const LeadModalContext = createContext<LeadModalApi>({ open: noop, close: noop, isOpen: false })

export function useLeadModal(): LeadModalApi {
  return useContext(LeadModalContext)
}

interface State {
  mounted: boolean
  open: boolean
  contexto?: string
  origem?: string
}

export function LeadModalProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<State>({ mounted: false, open: false })
  const openerRef = useRef<HTMLElement | null>(null)

  const openFrom = useCallback((opener: HTMLElement | null, options?: OpenOptions) => {
    openerRef.current = opener
    setState({ mounted: true, open: true, contexto: options?.contexto, origem: options?.origem })
    track('modal_aberto', { origem: options?.origem ?? null, contexto: options?.contexto ?? null })
  }, [])

  const open = useCallback(
    (options?: OpenOptions) => openFrom(document.activeElement as HTMLElement | null, options),
    [openFrom],
  )

  const close = useCallback(() => {
    setState((s) => ({ ...s, open: false }))
  }, [])

  // delegação: qualquer [data-open-modal] da página abre o pop-up
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const el = (e.target as Element | null)?.closest<HTMLElement>('[data-open-modal]')
      if (!el) return
      e.preventDefault()
      track('cta_clique', { origem: el.dataset.origem ?? null })
      openFrom(el, { contexto: el.dataset.contexto, origem: el.dataset.origem })
    }
    document.addEventListener('click', onClick)
    return () => document.removeEventListener('click', onClick)
  }, [openFrom])

  // aquece o chunk do <dialog> quando o navegador estiver ocioso (1º clique abre sem espera)
  useEffect(() => whenIdle(() => void loadDialog(), 3000), [])

  const api = useMemo<LeadModalApi>(() => ({ open, close, isOpen: state.open }), [open, close, state.open])

  return (
    <LeadModalContext.Provider value={api}>
      {children}
      {state.mounted && (
        <Suspense fallback={null}>
          <LeadModalDialog
            open={state.open}
            contexto={state.contexto}
            origem={state.origem}
            getOpener={() => openerRef.current}
            onClose={close}
          />
        </Suspense>
      )}
    </LeadModalContext.Provider>
  )
}
