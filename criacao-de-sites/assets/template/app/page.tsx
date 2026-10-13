import { StickyCta } from '@/components/StickyCta'
import { Marquee } from '@/components/Marquee'
import { copy } from '@/lib/copy'
import { Cabecalho } from '@/components/secoes/Cabecalho'
import { Hero } from '@/components/secoes/Hero'
import { Passos } from '@/components/secoes/Passos'
import { Destaques } from '@/components/secoes/Destaques'
import { Faq } from '@/components/secoes/Faq'
import { CtaFinal } from '@/components/secoes/CtaFinal'
import { Rodape } from '@/components/secoes/Rodape'

/**
 * Página-exemplo NEUTRA do template: todo texto vem de content/copy.json (lib/copy.ts); a página só desenha as
 * seções que a copy tem. Ritmo: ink (dobra) · papel (passos) · ink (destaques) · faixa · papel (FAQ) · ink (final).
 * Dobra no contrato do padrão de página (§2): tela inteira, imagem → título → apoio + linha → botão → micro.
 * Para trocar a ideia gráfica da dobra, veja references/receitas-de-dobra.md (na skill criacao-de-sites).
 */
export default function Page() {
  return (
    <>
      <Cabecalho />
      <main id="conteudo">
        <Hero />
        <Passos />
        <Destaques />
        {copy.faixa && copy.faixa.length > 0 ? <Marquee items={copy.faixa} /> : null}
        <Faq />
        <CtaFinal />
      </main>
      <Rodape />
      <StickyCta>{copy.cabecalho?.botao ?? copy.hero.cta}</StickyCta>
    </>
  )
}
