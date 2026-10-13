/**
 * Executa `cb` quando o navegador estiver ocioso (requestIdleCallback; setTimeout no Safari).
 * Devolve a função que cancela. Só no cliente.
 */
export function whenIdle(cb: () => void, timeout = 1500): () => void {
  if (typeof window === 'undefined') return () => {}
  const ric = (window as Window & { requestIdleCallback?: typeof window.requestIdleCallback }).requestIdleCallback
  if (typeof ric === 'function') {
    const id = ric.call(window, cb, { timeout })
    return () => window.cancelIdleCallback(id)
  }
  const id = window.setTimeout(cb, 200)
  return () => window.clearTimeout(id)
}
