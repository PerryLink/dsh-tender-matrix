# dsh-tender-matrix — Verificação aritmética da matriz de pontuação dos fatores de avaliação

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-tender-matrix` lê uma matriz de pontuação dos fatores de avaliação —o cabeçalho do processo mais uma linha por fator de avaliação— e verifica a aritmética e a completude dessa própria matriz: se declara o seu projeto e o seu método de avaliação, se nenhuma pontuação excede o máximo da sua rubrica, se os máximos das rubricas somam o valor que você configurar, se as pontuações de um concorrente somam o valor que você configurar, se cada pontuação regista o seu fundamento, se os números de fator são únicos e se não resta nenhum marcador de modelo por substituir na coluna do fundamento.

## Como é a saída

![Terminal demo of dsh-tender-matrix: real output over its TM-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-tender-matrix/main/docs/assets/dsh-tender-matrix-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `TM-001` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Todas as células da matriz estão preenchidas, por que motivo as duas regras de totais voltam como `skipped`? | Porque as duas vêm por configurar: `TM-003` compara a soma da coluna `maxScore` com o seu `target`, e `TM-004` soma as pontuações `bidderA` de um concorrente contra o seu `target`; ambas trazem `target: 0`, ou seja «não configurado», pelo que cada uma se reporta em `skipped` em vez de passar em silêncio até você inscrever o valor indicado no documento do concurso. Depois de configurada, uma ocorrência significa apenas que a soma difere do valor que você fixou, não que a escala de pontuação seja irregular; `TM-004` é uma soma pura e deliberadamente não está ligada a nenhuma coluna de total por concorrente. |
| Uma rubrica tem o máximo de 100 mas uma célula diz 105, e noutra linha a célula da pontuação diz `优良`. | `TM-002` reporta ambos os casos. Compara `bidderA` com `maxScore` rubrica a rubrica e reporta a linha cuja pontuação excede o máximo dessa rubrica; quando as duas células estão preenchidas mas nenhuma pode ser lida como número ou data, essa linha é reportada como não comparável em vez de ser omitida, ao passo que uma linha à qual falte uma das duas não é comparada de todo. É apenas uma comparação numérica e nunca julga se a pontuação é adequada; lê a coluna A por defeito, por isso cubra B e C com uma regra adicional ou com uma substituição de `leftField`. |
| Algumas linhas deixam vazia a coluna do fundamento da pontuação. Isso é reportado? | Sim. `TM-005` exige que a célula `basis` esteja preenchida em todas as linhas às quais o material dá essa coluna, e reporta cada uma que esteja em branco. Verifica apenas que algo está escrito, não se o fundamento registado se sustenta, é adequado ou corresponde à pontuação. Se a matriz não tiver nenhuma coluna `basis`, a regra reporta que não se aplica em vez de passar em silêncio. |
| O mesmo número de fator aparece em duas linhas da matriz. O que é reportado? | `TM-006` reporta o número repetido, comparando sem considerar os espaços. A unicidade é tudo o que estabelece, e importa porque uma repetição faz com que o total dos máximos saia errado: ou o mesmo fator foi registado duas vezes, ou dois fatores foram numerados por erro como um só. Não decide qual das duas linhas é a correta. |
| A célula do fundamento ainda diz `【】` ou `TBD`, porque a matriz foi copiada de um modelo. Isso é detetado? | `TM-007` reporta a célula `basis` que ainda contém algum dos seus termos de modelo —`【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例`—, uma lista ajustável ao seu próprio modelo. A falha que visa é um marcador ser lido como um motivo já registado. O seu título também menciona as observações, mas a verificação lê apenas a coluna `basis` e nunca julga a qualidade do fundamento. |
| O cabeçalho não diz a que projeto pertence esta matriz nem que método de avaliação segue. | `TM-001` exige que o cabeçalho do material traga `project` e `method` e reporta o que faltar; verifica apenas que o cabeçalho os declara, não que concordem com o documento do concurso. Se o formulário da sua instituição não tiver coluna de método de avaliação, ponha os `fields` dessa regra em `[project]` para deixar de pedir uma coluna que o seu formulário nunca traz. |

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 《中华人民共和国招标投标法》 | 1999年8月30日通过，2017年12月27日修正（全国人大常委会《关于修改〈中华人民共和国招标投标法〉、〈中华人民共和国计量法〉的决定》），本法自2000年1月1日起施行 | TM-001, TM-002, TM-003, TM-004, TM-005, TM-006, TM-007 |

**Boundary:** this plugin checks an **评标因素评分矩阵** for arithmetic — that the matrix names its project and
evaluation method, that no single score exceeds its item's maximum, that the maximum scores total what you
configure, that a bidder's scores total what you configure, that each score records its basis, that factor
numbers are unique, and that no placeholder survives. It does **not** decide whether a score is appropriate,
whether the evaluation was fair, or who should win. **Scoring is the evaluation committee's independent
judgement, and the weights and criteria are the tender document's.**

> ### ⚠️ Read this before trusting a citation in the report
>
> **Every `excerpt` in this plugin's rule pack says, in so many words, that the clause text was not
> obtained.** The regime lives in 《中华人民共和国招标投标法》and its implementing regulations, plus **each
> project's evaluation method inside the tender document**. The verification pass could not retrieve verbatim
> clause text, so rather than paraphrase a quotation the pack states the gap in the `excerpt` field itself and
> puts the honest reasoning in `note`. Every rule is therefore `warn` or `info`, and a test asserts that no
> rule claims a quotation it does not have. **When the texts are in hand, two things must be done: replace
> each `excerpt` with the real clause, and raise `kind` to `direct`.**
>
> **The plugin ships no scoring scale.** The two total checks ship with a target of `0`, meaning "not
> configured":
>
> - `TM-003` compares the sum of the items' maximum scores against `target`. 100 is common, but 120-point
>   scales and weighted schemes exist, so the total is your tender document's figure and the rule reports
>   that it could not run until you set it.
> - `TM-004` compares the sum of one bidder's scores against `target`. The check compares the column against
>   the figure **you** state; it is deliberately not wired to a per-bidder total column, so it stays a pure
>   addition check.
>
> `TM-002` checks column A by default (`bidderA` vs `maxScore`). Add a rule each for B and C, or override
> `leftField` per call.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-tender-matrix
dsh --profile <name> --dump-config | grep 'dsh-tender-matrix'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/tender-matrix.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-tender-matrix
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-matrix contributors.
