# Checklist de entrega

Só se entrega (ou mostra) quando TODOS os itens abaixo estão marcados. Um item falhando = corrigir e repetir;
2 itens falhando = nem mostrar. Dizer ao cliente o que foi achado e corrigido (honestidade > pressa).

## A. Entradas (antes de começar)
- [ ] `brand.json` (ou cores + fontes + forma) e logo SVG em curvas (claro/escuro/símbolo). `site.py marca` sem FALHA de contraste.
- [ ] **Copy FINAL** do cliente em `content/copy.json`; orientações/hipóteses em `pendencias.md` (fora do projeto).
- [ ] Fotos reais recortadas (alfa), em 640 e 1100 px WebP; pessoa nunca gerada por IA.
- [ ] Objetivo e destino: CTA único, campos, endpoint, link de destino, datas reais.
- [ ] Pesquisa NOVA feita e ficha de repertório (`../direcao-de-arte/references/referencias-e-pesquisa.md`).

## B. Dobra e composição (olho)
- [ ] Inventário da dobra por escrito em `docs/decisoes-do-projeto.md`; duplicado e decoração fora; UMA ideia gráfica.
- [ ] Dobra = tela inteira; a seção seguinte não aparece; CTA a ≤ 82% (celular) / ≤ 92% (desktop) da altura.
- [ ] Logo UMA vez (cabeçalho); nome da marca não repete; sem eyebrow, selos nem faixa na 1ª tela.
- [ ] Mesma composição em 360, 390, 768, 1024, 1440, 1920; só muda a escala.
- [ ] Olhei rolando de verdade, seção por seção, a 100% e a 25%; "um leigo diria que quebrou?" = não.
- [ ] Teste dos 3 segundos nas 4 larguras: o que é, quando, o que fazer.

## C. Verificação automática (0 erros)
- [ ] `python site.py check <pasta>` → **APROVADO (0 erros)**: `check_pagina.py` + `teste_pagina_total.py` + peso + copy-diff.
- [ ] Cada AVISO respondido: corrigido ou justificado em `docs/decisoes-do-projeto.md` (falsos positivos conhecidos em `references/licoes-de-pagina.md`).
- [ ] `npm run typecheck`, `npm run lint`, `npm test` sem erro.
- [ ] Copy-diff: nenhum texto na página fora da copy (nem nota de orientação).
- [ ] Peso: JS ≤ 150 KB gzip, CSS ≤ 40 KB, LCP < 2,5 s, CLS ≤ 0,1.

## D. Interação e movimento
- [ ] Pop-up: só abre por clique (todos os CTAs); foco no título; Tab preso; ESC fecha e devolve o foco; envio vazio →
      erro inline; telefone inválido → erro; válido → sucesso com botão de destino; rolagem do fundo travada.
- [ ] Movimento nos 3 modos: `total`, `suave` (movimento reduzido do sistema) e `?movimento=parado` — nada invisível,
      nada cortado, faixa legível; H1, foto do LCP e CTA não animam; nada pisca > 3×/s; faixa com botão de pausa.
- [ ] Sem JS: todo o texto e os botões presentes.
- [ ] Sem `100vw` em layout; sem rolagem horizontal em 320–2560 (inclui 390 com barra de 15 px).

## E. Hospedagem
- [ ] `site.py pack <pasta> --subpasta <nome> --site-url <url> [--indexar] [--endpoint …] [--destino …]` gerou os 3 zips.
- [ ] Raiz **e** subpasta testadas: 0 requisição com falha, 0 imagem quebrada, pop-up abre, GSAP carrega do prefixo.
- [ ] `.htaccess` dentro do zip (oculto) e 404 da marca; `/x` redireciona para `/x/`.
- [ ] `NEXT_PUBLIC_NOINDEX=0` só na versão final; og.png e favicon corretos; `<title>`/descrição da copy.
- [ ] Endpoint e destino gravados no build conferidos (mudou → refazer os zips).

## F. Documentação (na hora, não no fim)
- [ ] `docs/decisoes-do-projeto.md`: ideia da dobra, parâmetros, rodadas e correções do cliente (cada correção virou regra).
- [ ] README do projeto atualizado (variáveis, como trocar copy/foto/endpoint).
- [ ] Lição nova → `references/licoes-de-pagina.md` (genérica, sem nome de cliente).
- [ ] `pendencias.md` entregue ao cliente: o que falta confirmar (preço, datas, endpoint, link, domínio, SSL).
- [ ] Aviso honesto do que NÃO foi testado (Safari/iOS e Firefox em aparelho real, se for o caso).

## G. O que entregar
`<slug>-raiz.zip` · `<slug>-subpasta-<nome>.zip` · `<slug>-fonte.zip` · `LEIA-ME.txt` (gerado) · `pendencias.md` ·
imagens das 4 larguras (390, 768, 1024, 1440) da dobra e da página inteira · resumo do `check` (erros/avisos).
