# Estúdio de Design — skills para Claude Code

Cinco skills em português do Brasil que trabalham juntas como um estúdio de identidade visual feito em código:

| Skill | Faz |
|---|---|
| `brand-studio` | logo, lockups, selos, padrões, key visuals, 3D, recorte, IA de imagem, animação de logo |
| `brand-system` | identidade completa: pesquisa, plataforma, cores, tipografia, elementos, modelos de peça, design system, manual |
| `direcao-de-arte` | peças e séries (posts, stories, anúncios, banners) com composição verificada por código |
| `criacao-de-sites` | páginas de conversão em Next.js estático (Vercel/Hostinger) com verificadores |
| `revisao-de-design` | protocolo único de crítica: portão técnico → régua de 8 critérios → olho → **máx. 2 rodadas** |

Fluxo típico: logo (`brand-studio`) → sistema e manual (`brand-system`) → kit de elementos e peças
(`direcao-de-arte`) → site (`criacao-de-sites`). Tudo passa pela `revisao-de-design` antes de ser mostrado.

## Arquitetura (como as skills pensam)
```
            brand-studio ── brand-system ── direcao-de-arte ── criacao-de-sites      ← CRIAM
                 \______________ todas usam ______________/
                              revisao-de-design                                     ← JULGA
             REGRA (régua + gosto) · EXEMPLOS (calibração, repertório, padrões) · PROVA (scripts, comparação, arena)
```
Toda entrega segue o mesmo passo a passo, em qualquer skill:
1. **Primeiro uso:** `doctor.py` diz o que falta (obrigatório / recomendado / opcional).
2. **Antes de criar:** definir o alvo — exemplos calibrados do mesmo tipo (piso e alvo), repertório e padrões da área,
   o que não repetir.
3. **Criar** pelo fluxo da skill (receitas em `brand-studio/references/receitas-de-producao.md`).
4. **Revisar:** portão técnico (scripts) → régua de 8 critérios calibrada (`comparar.py`) → olho → decisão;
   **máximo 2 rodadas**, depois devolve ao usuário com o nível e o que falta.
5. **Depois da aprovação:** o aprovado vira exemplo da calibração local e a correção vira regra — o sistema cresce.
Diagrama: `revisao-de-design/assets/arquitetura-do-criterio.svg`.

### Onde fica cada coisa
| Tipo de conteúdo | Pasta (em cada skill) |
|---|---|
| Fluxo e regras curtas | `SKILL.md` (≤ 200 linhas) |
| Conhecimento detalhado | `references/*.md` (um assunto por arquivo, índice no topo) |
| Ferramentas | `scripts/*.py` (todos com `--help`) |
| Diagramas, templates, fontes OFL | `assets/` |
| Critério compartilhado | `revisao-de-design/` (régua, gosto, calibração, repertório, arena, economia, comparar.py) |
| Dados do usuário (biblioteca, chaves, projetos) | fora das skills, na pasta de trabalho (`ESTUDIO_DIR`) |

## Instalar

### Como plugin (recomendado — já vem com o modo econômico)
No Claude Code:
```
/plugin marketplace add JuliusBrussee/caveman
/plugin marketplace add <usuario>/<repositorio-destas-skills>
/plugin install estudio-design@estudio-design
```
O plugin depende do [caveman](https://github.com/JuliusBrussee/caveman) (respostas curtas, ~65% menos tokens de
saída). As skills também trazem regras próprias de economia (`revisao-de-design/references/economia.md`): padrão antes
de montar, script mede antes do olho, uma folha de contato por rodada, máximo 2 rodadas de correção, subagente só
quando vale a pena.

### Como skills soltas
Copie as cinco pastas para `~/.claude/skills/` (mantenha-as lado a lado: elas se referenciam por `../<skill>/`).

### Opcional
- [logo-design](https://github.com/kaankiziltug/logo-design-skill) (MIT) ao lado das outras: auditoria de SVG,
  folhas de conceito e biblioteca de logos de mercado usada no teste de originalidade.

## Requisitos (o agente explica sozinho no primeiro uso)
Na primeira vez, a skill roda `brand-studio/scripts/doctor.py` e diz o que falta, separado em três níveis.
Guia completo: [`brand-studio/references/instalacao.md`](brand-studio/references/instalacao.md).

| Nível | O quê | Custo |
|---|---|---|
| **Obrigatório** | Python 3.11+, pacotes de `brand-studio/requirements.txt`, Google Chrome | grátis |
| **Recomendado** | Node.js 22+, FFmpeg, modelos locais (CLIP, recorte, YuNet), skill logo-design, plugin caveman | grátis |
| **Opcional** | API do Gemini (imagem por IA), Real-ESRGAN (upscale, GPU), conector Adobe, Vercel/Hostinger | Gemini é **pago** (~US$ 0,03–0,11 por imagem); o resto grátis/conta própria |

Instalar o que é Python e os modelos pequenos (com a sua permissão):
```
python brand-studio/scripts/instalar.py          # + --upscale  + --modelos  ou  --tudo
python brand-studio/scripts/doctor.py            # confere de novo
```
Sem Gemini tudo funciona com motores grátis; a IA é um extra para cenários e composições difíceis.
Passo a passo de cada entrega (logo, identidade, elementos, foto, peça, série, mockup, animação, site):
[`brand-studio/references/receitas-de-producao.md`](brand-studio/references/receitas-de-producao.md).

## Onde ficam os SEUS arquivos
As skills não guardam nada seu. A pasta de trabalho é definida por `ESTUDIO_DIR` (ou o diretório atual) e contém:
```
biblioteca/<Cliente>/<Projeto>/   trabalhos aprovados + _perfil.md + _fichas.json (modelo em brand-studio/references/perfil-modelo.md)
biblioteca/_catalogo/             índice CLIP (gerado por library.py index)
.env                              chaves de API (nunca publicar)
<projetos>/                       um por marca/peça/site
```
Caches de modelos e fontes ficam em `~/.cache/brand-studio/`.

## Gosto e padrões
As skills foram treinadas com o que um estúdio aprovou e reprovou, transformado em regras neutras:
`revisao-de-design/references/gosto.md` (princípios), `regua.md` (como dar nota) e diagramas SVG em
`revisao-de-design/assets/`, `direcao-de-arte/assets/diagramas/` e `criacao-de-sites/assets/diagramas/`
(zonas seguras, escala de raios, escala de espaço, camadas, dobra padrão, ciclo de revisão).
Para regenerar os diagramas: `python _ferramentas/diagramas.py`.

## Antes de publicar uma versão nova
```
python _ferramentas/validar.py --termos <arquivo-privado-com-nomes-de-clientes.txt>
claude plugin validate .
```
O validador confere formato das skills (padrão Agent Skills), caminhos quebrados, `--help` dos scripts e vazamento de
dados privados (caminhos de usuário, e-mails, chaves e os termos do seu arquivo privado, que nunca vai no pacote).

## Licenças
Skills: MIT (`LICENSE`). Fontes em `assets/` sob OFL (licença ao lado de cada uma). Bibliotecas JS em
`direcao-de-arte/assets/web/vendor/` sob as licenças de cada projeto (GSAP: licença gratuita "standard no-charge").
