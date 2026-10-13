/**
 * GSAP sob demanda (dynamic import) — nunca entra no JavaScript inicial da rota.
 *
 * LICENÇA: GSAP 3.15 (core, ScrollTrigger, SplitText…) é gratuito sob a licença "Standard No Charge" da
 * Webflow, que vale enquanto o site NÃO cobra pelo acesso (esta página de captura é gratuita).
 * Se algum dia a página passar a cobrar entrada/assinatura, reler https://gsap.com/standard-license/
 * ou trocar por CSS puro. Cópia da licença: ver README (seção "Licenças").
 *
 * Uso típico dentro de um componente cliente:
 *
 *   const root = useRef<HTMLElement>(null)
 *   useGsap(root, ({ gsap, ScrollTrigger, SplitText }, scope) => {
 *     gsap.from('.titulo', { y: 32, opacity: 0, duration: .5 })
 *   })
 *
 * O setup roda SEMPRE (movimento ligado para todos), exceto em ?movimento=parado (aí roda `reduced`). Dentro do
 * setup, use `motionMode() === 'suave'` para tirar parallax/tilt/magnético e encurtar distâncias.
 */
import { useEffect, type RefObject } from 'react'
import { whenIdle } from './idle'
import { motionMode } from './motion'

export interface GsapApi {
  gsap: typeof import('gsap').gsap
  ScrollTrigger: typeof import('gsap/ScrollTrigger').ScrollTrigger
  SplitText: typeof import('gsap/SplitText').SplitText
}

let loading: Promise<GsapApi> | null = null

/** Carrega GSAP + ScrollTrigger + SplitText uma única vez. */
export function loadGsap(): Promise<GsapApi> {
  loading ??= Promise.all([import('gsap'), import('gsap/ScrollTrigger'), import('gsap/SplitText')]).then(
    ([g, st, sp]) => {
      g.gsap.registerPlugin(st.ScrollTrigger, sp.SplitText)
      return { gsap: g.gsap, ScrollTrigger: st.ScrollTrigger, SplitText: sp.SplitText }
    },
  )
  return loading
}

export interface UseGsapOptions {
  /** Quando carregar: 'idle' (padrão, requestIdleCallback) ou 'now' (logo após montar). */
  when?: 'idle' | 'now'
  /** Roda no lugar do setup quando o visitante pediu menos movimento (estado final, sem animar). */
  reduced?: (scope: HTMLElement) => void
}

/**
 * Executa `setup` com GSAP carregado, dentro de um `gsap.context` ligado ao elemento `scope`
 * (tudo é desfeito ao desmontar). Respeita prefers-reduced-motion.
 */
export function useGsap(
  scope: RefObject<HTMLElement | null>,
  setup: (api: GsapApi, scope: HTMLElement) => void,
  options: UseGsapOptions = {},
): void {
  const { when = 'idle', reduced } = options
  // `setup`/`reduced` costumam ser funções inline: de propósito, só rodam na montagem.
  useEffect(() => {
    const el = scope.current
    if (!el) return
    let cancelled = false
    let revert: (() => void) | undefined
    const run = () => {
      if (motionMode() === 'parado') {
        reduced?.(el)
        return
      }
      loadGsap().then((api) => {
        if (cancelled) return
        const ctx = api.gsap.context(() => setup(api, el), el)
        revert = () => ctx.revert()
        // fontes mudam as medidas: recalcula os gatilhos quando carregarem
        document.fonts?.ready.then(() => {
          if (!cancelled) api.ScrollTrigger.refresh()
        })
      })
    }
    const cancel = when === 'now' ? (run(), () => {}) : whenIdle(run)
    return () => {
      cancelled = true
      cancel()
      revert?.()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
}
