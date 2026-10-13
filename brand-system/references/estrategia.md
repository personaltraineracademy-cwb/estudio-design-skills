# Estratégia — plataforma em uma página

Saída: `plataforma.md` + `brand.json.platform`. Curta, concreta, testável. Cada campo vira decisão visual.

## 1. Frase de unicidade (Neumeier, *Zag*) — sempre
"[Marca] é a única [categoria] que [diferencial] para [quem] em [onde] que [precisa/por quê] numa era de [tendência]."
**Teste da troca**: com o nome de um concorrente, ainda é verdade? Então está fraca — reescreva.

## 2. Ideia em uma frase (com verbo, que gere imagem)
"Treino é composição", não "excelência em treino". Ancorada numa verdade **desta** marca. Ela precisa gerar o
sistema inteiro (assinatura, padrão, layout, movimento) — se só gera um símbolo, é metáfora rasa.

## 3. Inimigo e zag
- Inimigo em 1 linha: o que a marca recusa (Equinox: "We don't speak January").
- Zag: do mapa de convenções (references/pesquisa.md) — mantém 1 código de entrada, quebra 2.

## 4. Quadrado semiótico (categorias saturadas)
Ache a oposição que governa a categoria (fitness: disciplina × prazer). Cantos: S1, S2, não-S1, não-S2 + complexo
(S1+S2) e neutro. Posicione concorrentes; cantos vazios/termo complexo = territórios. Alternativa: quadrado de valores
de Floch (prático/utópico/lúdico/crítico).

## 5. Arquétipos — só diagnóstico
Sem base empírica; viram persona de banco de imagem. Use para ver qual arquétipo **toda a categoria** veste (fitness:
Herói e Rebelde) e evitar, ou combinar com o oposto (Herói × Cuidador).

## 6. Tensões ("isso, mas não aquilo")
3–5 pares: "preciso, mas não frio". Cada par vira regra visual que mostra os dois polos (grade rígida + um corte
feito à mão). Fuja de atributos que toda marca tem (qualidade, honestidade). → `platform.tension: [["preciso","frio"],…]`

## 7. Princípios de design (3–5, mensuráveis)
Formato: **Nome — regra com número — fazer — evitar — teste**.
Ex.: "Peso embaixo — 70% da massa no terço inferior — ancorar na base — composição flutuando — desfoque a peça: o
peso cai?" → `platform.principles: [{"name","rule","do","avoid","test"}]`
**Princípios descrevem comportamento, não decidem cor nem estilo.** "Luz devolvida: prata, âmbar, LED, zero neon"
vira paleta obrigatória e todos os territórios saem escuros e iguais.
Escreva o princípio como comportamento ("a marca responde à luz da cidade") e deixe a cor nascer nos territórios ou
no primeiro impacto. Proibições de cor (ex.: "nada de neon") podem ficar; prescrições, não.

## 8. Jobs-to-be-done da marca
Funcional (o que precisa ficar claro de imediato) · emocional (tom) · **social** (o que o cliente quer mostrar aos
outros) → o job social gera **ativos de exibição**: selo, certificado, moldura de post, crachá, camiseta.

## 9. Ativos distintivos (Romaniuk; Sharp — Ehrenberg-Bass)
Grade **exclusividade × fama**: usar-ou-perder (famoso e exclusivo) · investir (exclusivo, ainda não famoso) ·
nunca sozinho (famoso, compartilhado — ex.: lima no fitness) · ignorar/testar.
Regra: cada identidade precisa de **≥ 2 ativos que identificam a marca com o nome coberto** (forma, cor própria,
letra, padrão, movimento, som, personagem, frase). Distintividade pesa mais que "diferenciação declarada", mas
significado também importa. → `platform.assets`

## 10. Voz
Voz fixa (`is` / `is_not`) + tom que muda por canal: **matriz tom × canal** (Monzo) com nível alto/médio/baixo de
cada princípio em anúncio, aula, suporte, redes… + 3–6 exemplos reais de frase (antes/depois). → `platform.voice`

## 11. Arquitetura (quando há marca-mãe)
Monolítica · endossada · casa de marcas. Defina lockup de submarca, regra de nome, zona de cor por submarca
(MotoGP), endosso. Cliente com perfil na biblioteca: siga o `_perfil.md` dele.
