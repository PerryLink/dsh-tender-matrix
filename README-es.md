# dsh-tender-matrix

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
pnpm pack
dsh plugin --profile <name> add ./*.tgz
dsh --profile <name> --dump-config | grep 'dsh-tender-matrix'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`. Las claves y los parámetros de cada regla están en [README.md](README.md#configuration) (versión principal en inglés).

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
