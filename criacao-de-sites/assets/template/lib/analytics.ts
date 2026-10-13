/**
 * Medição (STUB): não envia nada por padrão.
 *
 * `track(event, data)` monta o evento com `event_id` (o MESMO id vai para o Pixel e para a API de Conversões,
 * assim a Meta deduplica), avisa os "trackers" registrados e dispara um CustomEvent `est:track` na janela.
 * Nunca recebe nome, e-mail ou telefone (PII): chaves proibidas são descartadas.
 *
 * Como ligar o Pixel da Meta (exemplo; coloque o <script> do Pixel no layout e então):
 *
 *   import { addTracker } from '@/lib/analytics'
 *   addTracker((e) => {
 *     if (e.event === 'envio_ok') window.fbq?.('track', 'Lead', {}, { eventID: e.event_id })
 *   })
 *
 * O servidor que recebe o POST usa o mesmo `event_id` na API de Conversões.
 * Eventos (pesquisa 18 §2.6): modal_aberto · campo_focado{campo} · erro{campo,tipo} · envio_tentado ·
 * envio_ok (= Lead) · envio_falha{status} · destino_clique · modal_fechado{com_dados} · cta_clique{origem}.
 */

export type TrackName =
  | 'modal_aberto'
  | 'campo_focado'
  | 'erro'
  | 'envio_tentado'
  | 'envio_ok'
  | 'envio_falha'
  | 'destino_clique'
  | 'modal_fechado'
  | 'cta_clique'

export type TrackData = Record<string, string | number | boolean | null | undefined>

export interface TrackEvent {
  event: TrackName
  event_id: string
  ts: number
  data: TrackData
}

export type Tracker = (e: TrackEvent) => void

const trackers = new Set<Tracker>()
const FORBIDDEN = /^(nome|name|email|e-mail|telefone|tel|whats|whatsapp|phone|cpf)$/i

/** UUID v4 (crypto.randomUUID quando existe). */
export function newEventId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') return crypto.randomUUID()
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
}

/** Registra um destino (Pixel, GA4, dataLayer…). Devolve a função que remove o destino. */
export function addTracker(fn: Tracker): () => void {
  trackers.add(fn)
  return () => {
    trackers.delete(fn)
  }
}

/**
 * Registra um evento. Devolve o `event_id` (passe `eventId` para reaproveitar o mesmo id, ex.: no POST do lead).
 */
export function track(event: TrackName, data: TrackData = {}, eventId?: string): string {
  const id = eventId ?? newEventId()
  const safe: TrackData = {}
  for (const [k, v] of Object.entries(data)) if (!FORBIDDEN.test(k)) safe[k] = v
  const payload: TrackEvent = { event, event_id: id, ts: Date.now(), data: safe }
  for (const t of trackers) {
    try {
      t(payload)
    } catch {
      /* um tracker com defeito nunca quebra a página */
    }
  }
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('est:track', { detail: payload }))
    if (process.env.NODE_ENV !== 'production') console.debug('[track]', payload)
  }
  return id
}
