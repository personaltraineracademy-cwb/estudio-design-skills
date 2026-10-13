/**
 * Modo de movimento da página (definido por um script em app/layout.tsx):
 *  - 'total'  : padrão, tudo anima.
 *  - 'suave'  : o sistema do visitante pede menos movimento; MESMA coreografia, sem parallax/tilt/magnético, curtas.
 *  - 'parado' : só por ?movimento=parado (impressão/teste): nada anima.
 */
export type MotionMode = 'total' | 'suave' | 'parado'

export function motionMode(): MotionMode {
  if (typeof document === 'undefined') return 'total'
  const m = document.documentElement.getAttribute('data-movimento')
  return m === 'suave' || m === 'parado' ? m : 'total'
}
