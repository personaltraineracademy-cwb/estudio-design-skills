import type { Metadata, Viewport } from 'next'
import type { ReactNode } from 'react'
import './globals.css'
import { fontVariables } from './fonts'
import { config } from '@/lib/config'
import { withBase } from '@/lib/url'
import { copy } from '@/lib/copy'
import { UI } from '@/lib/ui-text'
import marca from '@/content/marca.json'
import { LeadModalProvider } from '@/components/LeadModal'
import { RevealObserver } from '@/components/RevealObserver'
import { SmoothScroll } from '@/components/SmoothScroll'

const TITLE = copy.meta?.titulo ?? copy.hero.h1
const DESC = copy.meta?.descricao ?? copy.hero.sub ?? ''
const NOME = copy.meta?.nome ?? marca.nome
const OG = `${config.siteUrl}${withBase('/og.png')}` // com subpasta, a URL da imagem OG inclui o BASE_PATH

export const metadata: Metadata = {
  metadataBase: new URL(config.siteUrl),
  title: TITLE,
  description: DESC,
  applicationName: NOME,
  robots: config.noindex ? { index: false, follow: false } : { index: true, follow: true },
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    siteName: NOME,
    title: TITLE,
    description: DESC,
    images: [{ url: OG, width: 1200, height: 630, alt: copy.hero.h1 }],
  },
  twitter: { card: 'summary_large_image', title: TITLE, description: DESC, images: [OG] },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: marca.cores.ink,
  colorScheme: 'dark',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html
      lang="pt-BR"
      className={fontVariables}
      data-movimento="total"
      suppressHydrationWarning
      style={{ ['--grain-url' as string]: `url(${withBase('/img/grao-128.png')})` }}
    >
      <head>
        {/* movimento SEMPRE ligado: 'total' (padrão), 'suave' se o sistema pede menos movimento, 'parado' só por ?movimento=parado */}
        <script
          dangerouslySetInnerHTML={{
            __html:
              "(function(){try{var d=document.documentElement,q=new URLSearchParams(location.search).get('movimento'),m=(q==='parado'||q==='suave'||q==='total')?q:(matchMedia('(prefers-reduced-motion: reduce)').matches?'suave':'total');d.setAttribute('data-movimento',m)}catch(e){}})()",
          }}
        />
      </head>
      <body>
        <a className="est-skip" href="#conteudo">
          {UI.skip}
        </a>
        <LeadModalProvider>{children}</LeadModalProvider>
        <RevealObserver />
        <SmoothScroll />
      </body>
    </html>
  )
}
