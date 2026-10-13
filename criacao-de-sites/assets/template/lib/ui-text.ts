/**
 * Rótulos de INTERFACE (neutros). Não são texto de venda: nada de promessa, preço, urgência ou nome de campanha.
 * Todo texto comercial vem de content/copy.json (lib/copy.ts). O `copy-diff` do estúdio aceita este arquivo.
 */
export const UI = {
  skip: 'Pular para o conteúdo',
  home: 'Início',
  notFound: { titulo: 'Página não encontrada', texto: 'O endereço não existe ou mudou de lugar.', voltar: 'Voltar ao início' },
  close: 'Fechar',
  sending: 'Enviando…',
  retry: 'Tentar de novo',
  errorPrefix: 'Erro:',
  /** Erros de campo (linguagem simples, sem culpar). */
  errors: {
    nome: 'Digite seu nome.',
    whats: 'Digite o DDD e o número, por exemplo (11) 91234-5678.',
    email: 'Confira o e-mail.',
  },
  network: 'Sem conexão. Seus dados continuam aqui. Tente de novo.',
  continueAnyway: 'Continuar mesmo assim',
  pauseMotion: 'Pausar animação',
  resumeMotion: 'Retomar animação',
  placeholders: { nome: 'Seu nome', whats: '(11) 91234-5678', email: 'voce@exemplo.com' },
  /** Textos do pop-up quando a copy não define `modal` (neutros). */
  modalDefault: {
    titulo: 'Preencha seus dados',
    botao: 'Enviar',
    consentimento: 'Usaremos seus dados só para dar andamento a este pedido.',
    sucesso_titulo: 'Recebemos seus dados.',
    sucesso_texto: 'Agora é só seguir para o próximo passo.',
    sucesso_botao: 'Continuar',
  },
} as const
