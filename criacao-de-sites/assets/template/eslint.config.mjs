import { defineConfig, globalIgnores } from 'eslint/config'
import nextVitals from 'eslint-config-next/core-web-vitals'
import nextTs from 'eslint-config-next/typescript'

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  globalIgnores(['.next/**', 'out/**', 'out-*/**', '_entrega/**', 'node_modules/**', '_scratch/**', '.check/**', 'next-env.d.ts', 'lib/logos.generated.ts']),
  {
    rules: {
      // Projeto 100% estático: usamos <img>/<picture> de propósito (art direction, srcset, sem servidor de imagem).
      '@next/next/no-img-element': 'off',
      // Links entre versões são <a> comuns de propósito (ver app/page.tsx): prefetch do <Link> dá 404 no export.
      '@next/next/no-html-link-for-pages': 'off',
    },
  },
])
