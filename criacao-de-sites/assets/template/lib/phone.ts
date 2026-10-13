/**
 * WhatsApp brasileiro: normalização, validação e formatação (sem dependências).
 * Regras (pesquisa 18 §2.2): 67 DDDs válidos · celular = 11 dígitos com 9 depois do DDD ·
 * aceita +55 / 55 / 0 antes do DDD · NUNCA type="number" · formatar ao sair do campo (não a cada tecla).
 */

/** Os 67 DDDs válidos no Brasil (Anatel). */
export const DDD_REGEX = /^(1[1-9]|2[12478]|3[1-578]|4[1-9]|5[1345]|6[1-9]|7[134579]|8[1-9]|9[1-9])$/

/**
 * Só dígitos, sem +55/55 (apenas se sobrar mais de 11 dígitos: o DDD 55 existe) e sem zeros à esquerda.
 * Corta em 11 dígitos.
 */
export function toDigits(value: string): string {
  let d = value.replace(/\D/g, '')
  if (d.length > 11 && d.startsWith('55')) d = d.slice(2)
  d = d.replace(/^0+/, '')
  return d.slice(0, 11)
}

/** Celular válido: 11 dígitos, DDD válido e 9 na frente do número. */
export function isValidMobile(digits: string): boolean {
  return digits.length === 11 && DDD_REGEX.test(digits.slice(0, 2)) && digits[2] === '9'
}

/** "(11) 91234-5678" (aceita parcial: "(11) 9123"). */
export function formatMobile(digits: string): string {
  const d = digits.slice(0, 11)
  if (d.length <= 2) return d
  if (d.length <= 7) return `(${d.slice(0, 2)}) ${d.slice(2)}`
  return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`
}

/** Formato internacional só com dígitos, para enviar ao servidor: "5511912345678". */
export function toInternational(digits: string): string {
  return `55${digits}`
}
