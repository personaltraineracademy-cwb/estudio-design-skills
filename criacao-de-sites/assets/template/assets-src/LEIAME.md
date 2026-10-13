# assets-src/logos

Coloque aqui os SVG do logo do cliente (em curvas; sem `<text>` nem `<image>`):

- `logo.svg`         logo principal (cabeçalho, rodapé, OG)
- `logo-simbolo.svg` símbolo (favicon, apple-icon, pop-up). Sem ele o logo principal é usado.

Rode `npm run assets` (ou `python scripts/build-assets.py --so logos`) para gerar `lib/logos.generated.ts` e
`public/logos/*.svg`. Logo monocromático vira `currentColor` (a cor sai do tom `claro | destaque | escuro`);
logo multicolor mantém as cores. O logo nunca arredonda, nunca recebe sombra nem efeito.
Os arquivos de exemplo (palavra "MARCA") são placeholders do template.
