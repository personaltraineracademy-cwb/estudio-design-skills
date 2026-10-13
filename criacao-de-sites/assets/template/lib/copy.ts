/**
 * COPY FINAL — única fonte de texto comercial da página.
 *
 * Fonte: content/copy.json. Regras: nada fora deste arquivo/JSON é "texto de venda". Rótulos de interface neutros
 * (Fechar, Enviando…, Erro:) ficam em lib/ui-text.ts. Notas de orientação, hipóteses e pendências NUNCA entram
 * na página (vão para `pendencias.md`, fora do projeto). Chaves que começam com `_` são metadados e não são lidas.
 *
 * Todas as seções são opcionais, menos `hero.h1` e `hero.cta`: a página só desenha o que existe na copy.
 */
import raw from '@/content/copy.json'
import { UI } from './ui-text'

export interface ModalField {
  id: 'nome' | 'whats' | 'email'
  rotulo: string
  tipo: 'text' | 'tel' | 'email'
  mascara?: string
  opcional?: boolean
}

export interface ImagemArquivo {
  /** caminho que começa com "/" (ex.: /img/hero-1100.webp); o prefixo de subpasta é aplicado em runtime */
  src: string
  w: number
  h: number
}

export interface Item {
  t: string
  d: string
}

export interface Copy {
  meta?: { nome?: string; titulo?: string; descricao?: string }
  cabecalho?: { botao?: string }
  hero: {
    h1: string
    sub?: string
    /** linha mono curta (data, local, formato) */
    data?: string
    cta: string
    micro?: string
    /** foto real recortada (alfa), 1–3 larguras, da menor para a maior */
    imagem?: { alt: string; arquivos: ImagemArquivo[] } | null
  }
  passos?: { titulo: string; itens: Item[] }
  destaques?: { titulo: string; itens: Item[] }
  faixa?: string[]
  faq?: { titulo: string; itens: { q: string; a: string }[] }
  cta_final?: { titulo: string; botao: string }
  rodape?: string
  modal?: Partial<{
    titulo: string
    campos: ModalField[]
    botao: string
    consentimento: string
    sucesso_titulo: string
    sucesso_texto: string
    sucesso_botao: string
  }>
}

export const copy = raw as unknown as Copy

const DEFAULT_CAMPOS: ModalField[] = [
  { id: 'nome', rotulo: 'Nome', tipo: 'text' },
  { id: 'whats', rotulo: 'WhatsApp', tipo: 'tel', mascara: '(00) 00000-0000' },
  { id: 'email', rotulo: 'E-mail (opcional)', tipo: 'email', opcional: true },
]

/** Textos do pop-up já completos (copy do cliente por cima dos neutros). */
export const modal = {
  ...UI.modalDefault,
  ...copy.modal,
  campos: copy.modal?.campos ?? DEFAULT_CAMPOS,
}
