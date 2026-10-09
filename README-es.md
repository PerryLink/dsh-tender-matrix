# dsh-tender-matrix — Verificación aritmética de la matriz de puntuación de los factores de evaluación

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-tender-matrix` lee una matriz de puntuación de los factores de evaluación —la cabecera del expediente más una fila por factor de evaluación— y comprueba la aritmética y la integridad de esa propia matriz: que declare su proyecto y su método de evaluación, que ninguna puntuación supere el máximo de su partida, que los máximos de las partidas sumen la cifra que usted configure, que las puntuaciones de un licitador sumen la cifra que usted configure, que cada puntuación registre su fundamento, que los números de factor sean únicos y que no quede ningún marcador de plantilla sin sustituir en la columna del fundamento.

## Cómo se ve la salida

![Terminal demo of dsh-tender-matrix: real output over its TM-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-tender-matrix/main/docs/assets/dsh-tender-matrix-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `TM-001` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Todas las casillas de la matriz están rellenas, así que ¿por qué las dos reglas de totales devuelven `skipped`? | Porque las dos vienen sin configurar: `TM-003` compara la suma de la columna `maxScore` con su `target`, y `TM-004` suma las puntuaciones `bidderA` de un licitador contra su `target`; ambas traen `target: 0`, es decir «sin configurar», así que cada una se informa en `skipped` en lugar de pasar en silencio hasta que usted escriba la cifra que indica su pliego. Una vez configurada, una coincidencia solo significa que la suma difiere de la cifra que usted fijó, no que la escala de puntuación sea improcedente; `TM-004` es una suma pura y deliberadamente no está conectada a ninguna columna de total por licitador. |
| Una partida tiene un máximo de 100 pero una casilla dice 105, y en otra fila la casilla de puntuación dice `优良`. | `TM-002` informa de ambos casos. Compara `bidderA` con `maxScore` partida por partida e informa de la fila cuya puntuación supera el máximo de esa partida; cuando las dos casillas están rellenas pero ninguna se puede leer como número o fecha, esa fila se informa como no comparable en lugar de omitirse, mientras que una fila a la que le falta una de las dos no se compara en absoluto. Es solo una comparación numérica y nunca juzga si la puntuación es adecuada; lee la columna A por defecto, así que cubra B y C con una regla adicional o con una anulación de `leftField`. |
| Algunas filas dejan vacía la columna del fundamento de la puntuación. ¿Se informa de eso? | Sí. `TM-005` exige que la casilla `basis` esté rellena en todas las filas a las que el material da esa columna, e informa de cada una que esté en blanco. Solo comprueba que haya algo escrito, no si el fundamento registrado se sostiene, es adecuado o corresponde a la puntuación. Si la matriz no trae ninguna columna `basis`, la regla informa de que no se aplica en lugar de pasar en silencio. |
| El mismo número de factor aparece en dos filas de la matriz. ¿Qué se informa? | `TM-006` informa del número repetido, comparando sin tener en cuenta los espacios. La unicidad es todo lo que establece, y importa porque una repetición hace que el total de máximos salga mal: o el mismo factor se registró dos veces, o dos factores se numeraron por error como uno solo. No decide cuál de las dos filas es la correcta. |
| La casilla del fundamento todavía dice `【】` o `TBD`, porque la matriz se copió de una plantilla. ¿Se detecta? | `TM-007` informa de la casilla `basis` que aún contiene alguno de sus términos de plantilla —`【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例`—, una lista ajustable a su propia plantilla. El fallo que persigue es que un marcador se lea como un motivo ya registrado. Su título también menciona las observaciones, pero la comprobación lee solo la columna `basis` y nunca juzga la calidad del fundamento. |
| La cabecera no dice a qué proyecto pertenece esta matriz ni qué método de evaluación sigue. | `TM-001` exige que la cabecera del material traiga `project` y `method` e informa del que falte; solo comprueba que la cabecera los declare, no que concuerden con el pliego. Si el formulario de su institución no tiene columna de método de evaluación, ponga los `fields` de esa regla en `[project]` para que deje de pedir una columna que su formulario nunca trae. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-tender-matrix
dsh --profile <name> --dump-config | grep 'dsh-tender-matrix'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/tender-matrix.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-tender-matrix
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-matrix contributors.
