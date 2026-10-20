# dsh-tender-matrix — Tender evaluation-factor scoring matrix arithmetic self-consistency check

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-tender-matrix?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-tender-matrix?ref=badge)

`dsh-tender-matrix` reads one 评标因素评分矩阵 — a tender's evaluation-factor scoring matrix: the package header plus one row per evaluation factor — and checks that matrix's own arithmetic and completeness: that it names its project and its evaluation method, that no single score exceeds that item's maximum, that the item maximum scores total the figure you configure, that one bidder's scores total the figure you configure, that every score records its basis, that factor numbers are unique, and that no unreplaced placeholder survives in the basis column.

## Install

```sh
dsh plugin --profile <name> add dsh-tender-matrix
dsh --profile <name> --dump-config | grep 'dsh-tender-matrix'
```

## What it looks like

![Workflow diagram for dsh-tender-matrix: call → plugin → result.](docs/assets/dsh-tender-matrix-flow.svg)

*Workflow overview: call → plugin → result. The examples below use the real command surface.*



## What it answers

### Examples

The table below is the example set: the first row is the detailed walkthrough, the remaining rows are short cases.

#### Detailed output

**Tool** `tender_matrix`

**Input**

~~~json
{"rows":[{"评审因素":"施工组织设计","分值":"30","投标人A":"32"}]}
~~~
 
**Output**

~~~json
{
  "id": "dsh-tender-matrix.TM-002.de09b5a6",
  "ruleId": "TM-002",
  "severity": "warn",
  "locator": {
    "row": 1,
    "field": "bidderA"
  },
  "found": "第 1 行「bidderA」为 32，「maxScore」为 30，不满足不大于关系",
  "expected": "「bidderA」应不大于「maxScore」",
  "fix": "核对评分是否抄错；本条只核对是否超出分值上限，不判断评分是否恰当"
}
~~~

*Observed from `dsh-tender-matrix/tests/fixtures/TM-002/TM-002-unsafe.json`*

| You ask | What it answers |
|---|---|
| Every cell of the matrix is filled in, so why do both total checks report `skipped`? | Because both totals ship unconfigured: `TM-003` compares the sum of the `maxScore` column against its `target`, and `TM-004` adds up one bidder's `bidderA` scores against its `target`; both carry `target: 0`, meaning “not configured”, so each reports itself in `skipped` rather than passing quietly until you enter the figure your tender document states. Once configured, a hit means only that the sum differs from the figure you set — not that the score scale is non-compliant; `TM-004` is pure addition and is deliberately not wired to any per-bidder total column. |
| One item's maximum is 100 but a cell says 105, and another row's score cell reads `优良`. | `TM-002` reports both. It compares `bidderA` with `maxScore` item by item and reports a row whose score is above that item's maximum; when both cells are filled but neither can be read as a number or a date, that row is reported as uncomparable instead of being passed over, while a row missing one of the two is not compared at all. It is a numeric comparison only and never judges whether a score is appropriate, and it reads column A by default — cover B and C with an extra rule or a `leftField` override. |
| Some rows leave the scoring-basis column empty. Is that reported? | Yes. `TM-005` requires the `basis` cell to be filled on every row the material gives that column, and reports each blank one. It checks only that something is written there — not whether the recorded basis holds, is appropriate, or matches the score. If the matrix carries no `basis` column at all, the rule reports that it does not apply rather than passing silently. |
| The same factor number appears on two rows of the matrix. What is reported? | `TM-006` reports the repeated number, comparing with whitespace ignored. Uniqueness is all it establishes, and it matters because a repeat makes the maximum-score total come out wrong: either the same factor was registered twice or two factors were mis-numbered as one. It does not decide which of the two rows is the correct one. |
| The basis cell still reads `【】` or `TBD`, because the matrix was copied from a template. Is that caught? | `TM-007` reports a `basis` cell that still contains any of its placeholder terms — `【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例` — a list you can adjust to your own template. The failure it targets is a placeholder being read as a reason already recorded. Its title also names remarks, but the check reads the `basis` column only, and it never judges the quality of the basis itself. |
| The header does not say which project this matrix belongs to, nor which evaluation method it follows. | `TM-001` requires the material's header to carry `project` and `method` and reports whichever is missing; it checks only that the header declares them, not that they agree with the tender document. If your institution's form has no evaluation-method column, set that rule's `fields` to `[project]` so it stops asking for a column your form never carries. |

## Standards it follows

| Document | Number | Cited by rules |
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
> **Every `excerpt` in this plugin's rule pack is a verbatim quotation of the clause it cites, and**
> **the citation gate re-checks each segment against the record in `rules/evidence/`.** 《中华人民共和国招标投标法》and its implementing regulations, plus each project's evaluation method inside the tender document. The
> pack states a requirement verbatim when the clause states it, and stops at `warn` when the clause only
> implies it: a check that rests on a general principle is capped below `error` and says so in its own
> `note`. What the pack will not do is paraphrase a clause and present the paraphrase as a quotation.
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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-rc.2`. `engines.dsh` is declared as `>=0.2.1-0 <0.3.0` and is enforced by the host since 0.2.1 |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native` and `ptc`; for several packages use `ptc` |

## What it does

Registers the `tender_matrix` tool. It reads one scoring matrix — the package header plus one row per
evaluation factor — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `TM-001` | the matrix names its project and method | warn | principle |
| `TM-002` | no score exceeds its item's maximum | warn | direct |
| `TM-003` | the maximum scores total your configured figure (off by default) | info | local |
| `TM-004` | a bidder's scores total your configured figure (off by default) | warn | principle |
| `TM-005` | every score records its basis | warn | principle |
| `TM-006` | factor numbers are unique | warn | principle |
| `TM-007` | the basis column holds no unreplaced placeholder | warn | principle |
## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/tender-matrix.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `TM-002` `leftField` / `rightField` / `relation` — the comparison, `bidderA <= maxScore` by default.
- `TM-003` `target` — the total the items' maximum scores must reach. `0` means the rule does not run.
- `TM-004` `field` / `target` — the bidder column and the total it must reach. `0` means the rule does not run.
- `TM-007` `terms` — the placeholders to look for.

## Material format

The tool accepts JSON or YAML:

```yaml
project: 某某工程施工招标
tenderNo: ZB-2026-018
method: 综合评估法
rows:
  - { 序号: '1', 评审因素: 施工组织设计, 分值: '30', 投标人A: '26',
      投标人B: '24', 投标人C: '28', 评分依据: '按招标文件评标办法第 3.2 条' }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens, so `投标人A` and
`bidderA` resolve to the same field; the matrix's own column names are kept, so a finding names the column it
read.

## Rule sources

Rule data lives in `rules/tender-matrix.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an
excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`TM-003` or `TM-004` reports itself as skipped.** Its target is `0`. Set your package's total, or the
  bidder's total, and the check runs.
- **`TM-002` fires on a score above the maximum.** That is the check: the arithmetic does not hold, so the
  cell is either mis-keyed or the item's maximum is wrong.
- **`TM-002` does not check bidders B and C.** It checks column A by default. Add a rule per column, or
  override `leftField` for the call.
- **`TM-004` fires although the matrix has a total row.** The rule adds the column and compares against the
  configured target; a total that lives in a header field is not read. Set `target` to the figure you expect.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-tender-matrix@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-tender-matrix   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## PerryLink DSH Plugin Family

This project is part of the DeepSeek Harness plugin family from [PerryLink](https://github.com/PerryLink). The roster stays collapsed below so every README keeps a short first screen; expand it to see every row and its status.

<details>
<summary>Expand all plugins</summary>

| Plugin | Status |
|---|---|
| **[dsh-aqua-input-check](https://github.com/PerryLink/dsh-aqua-input-check)** |  |
| **[dsh-archive-check](https://github.com/PerryLink/dsh-archive-check)** |  |
| **[dsh-auto-review](https://github.com/PerryLink/dsh-auto-review)** |  |
| **[dsh-autotier](https://github.com/PerryLink/dsh-autotier)** |  |
| **[dsh-bid-ca-precheck](https://github.com/PerryLink/dsh-bid-ca-precheck)** |  |
| **[dsh-bid-qual-check](https://github.com/PerryLink/dsh-bid-qual-check)** |  |
| **[dsh-cert-mcp](https://github.com/PerryLink/dsh-cert-mcp)** |  |
| **[dsh-checkpoint-rewind](https://github.com/PerryLink/dsh-checkpoint-rewind)** |  |
| **[dsh-click](https://github.com/PerryLink/dsh-click)** |  |
| **[dsh-composer-history](https://github.com/PerryLink/dsh-composer-history)** |  |
| **[dsh-contract-stance](https://github.com/PerryLink/dsh-contract-stance)** |  |
| **[dsh-customs-doc-check](https://github.com/PerryLink/dsh-customs-doc-check)** |  |
| **[dsh-data-quality](https://github.com/PerryLink/dsh-data-quality)** |  |
| **[dsh-demurrage-ledger](https://github.com/PerryLink/dsh-demurrage-ledger)** |  |
| **[dsh-doublecheck](https://github.com/PerryLink/dsh-doublecheck)** |  |
| **[dsh-drill-script-check](https://github.com/PerryLink/dsh-drill-script-check)** |  |
| **[dsh-eia-guide-check](https://github.com/PerryLink/dsh-eia-guide-check)** |  |
| **[dsh-emergency-plan](https://github.com/PerryLink/dsh-emergency-plan)** |  |
| **[dsh-essay-rubric-check](https://github.com/PerryLink/dsh-essay-rubric-check)** |  |
| **[dsh-evidence-check](https://github.com/PerryLink/dsh-evidence-check)** |  |
| **[dsh-export-ctl-check](https://github.com/PerryLink/dsh-export-ctl-check)** |  |
| **[dsh-fast](https://github.com/PerryLink/dsh-fast)** |  |
| **[dsh-fmea-table-check](https://github.com/PerryLink/dsh-fmea-table-check)** |  |
| **[dsh-forecast-penalty](https://github.com/PerryLink/dsh-forecast-penalty)** |  |
| **[dsh-fund-research](https://github.com/PerryLink/dsh-fund-research)** |  |
| **[dsh-github](https://github.com/PerryLink/dsh-github)** |  |
| **[dsh-gongwen-flow-check](https://github.com/PerryLink/dsh-gongwen-flow-check)** |  |
| **[dsh-gongwen-word-check](https://github.com/PerryLink/dsh-gongwen-word-check)** |  |
| **[dsh-guard-plan-qc](https://github.com/PerryLink/dsh-guard-plan-qc)** |  |
| **[dsh-hazchem-check](https://github.com/PerryLink/dsh-hazchem-check)** |  |
| **[dsh-hazplan-check](https://github.com/PerryLink/dsh-hazplan-check)** |  |
| **[dsh-hidden-risk-map](https://github.com/PerryLink/dsh-hidden-risk-map)** |  |
| **[dsh-hs-classify](https://github.com/PerryLink/dsh-hs-classify)** |  |
| **[dsh-icd-rule-check](https://github.com/PerryLink/dsh-icd-rule-check)** |  |
| **[dsh-industry-research](https://github.com/PerryLink/dsh-industry-research)** |  |
| **[dsh-lawcite-adapter](https://github.com/PerryLink/dsh-lawcite-adapter)** |  |
| **[dsh-laya](https://github.com/PerryLink/dsh-laya)** |  |
| **[dsh-lc-doc-check](https://github.com/PerryLink/dsh-lc-doc-check)** |  |
| **[dsh-learning-gap-check](https://github.com/PerryLink/dsh-learning-gap-check)** |  |
| **[dsh-library](https://github.com/PerryLink/dsh-library)** |  |
| **[dsh-local-ai](https://github.com/PerryLink/dsh-local-ai)** |  |
| **[dsh-lsp-actions](https://github.com/PerryLink/dsh-lsp-actions)** |  |
| **[dsh-mask](https://github.com/PerryLink/dsh-mask)** |  |
| **[dsh-mcp-panel](https://github.com/PerryLink/dsh-mcp-panel)** |  |
| **[dsh-medrec-qc](https://github.com/PerryLink/dsh-medrec-qc)** |  |
| **[dsh-memento](https://github.com/PerryLink/dsh-memento)** |  |
| **[dsh-nsfc-form-check](https://github.com/PerryLink/dsh-nsfc-form-check)** |  |
| **[dsh-nurse-record-check](https://github.com/PerryLink/dsh-nurse-record-check)** |  |
| **[dsh-observe](https://github.com/PerryLink/dsh-observe)** |  |
| **[dsh-origin-rvc-check](https://github.com/PerryLink/dsh-origin-rvc-check)** |  |
| **[dsh-ota-review-check](https://github.com/PerryLink/dsh-ota-review-check)** |  |
| **[dsh-output-styles](https://github.com/PerryLink/dsh-output-styles)** |  |
| **[dsh-paper-doc-adapter](https://github.com/PerryLink/dsh-paper-doc-adapter)** |  |
| **[dsh-permission-rules](https://github.com/PerryLink/dsh-permission-rules)** |  |
| **[dsh-permit-report-check](https://github.com/PerryLink/dsh-permit-report-check)** |  |
| **[dsh-pipeline-check](https://github.com/PerryLink/dsh-pipeline-check)** |  |
| **[dsh-pleading-draft](https://github.com/PerryLink/dsh-pleading-draft)** |  |
| **[dsh-plugin-doctor](https://github.com/PerryLink/dsh-plugin-doctor)** |  |
| **[dsh-plugin-guide](https://github.com/PerryLink/dsh-plugin-guide)** |  |
| **[dsh-plugin-kit](https://github.com/PerryLink/dsh-plugin-kit)** |  |
| **[dsh-plugin-upgrade](https://github.com/PerryLink/dsh-plugin-upgrade)** |  |
| **[dsh-policy-brief-draft](https://github.com/PerryLink/dsh-policy-brief-draft)** |  |
| **[dsh-power-loss-split](https://github.com/PerryLink/dsh-power-loss-split)** |  |
| **[dsh-power-ticket-check](https://github.com/PerryLink/dsh-power-ticket-check)** |  |
| **[dsh-ppap-check](https://github.com/PerryLink/dsh-ppap-check)** |  |
| **[dsh-protest-deadline](https://github.com/PerryLink/dsh-protest-deadline)** |  |
| **[dsh-railway-window](https://github.com/PerryLink/dsh-railway-window)** |  |
| **[dsh-repair-order-qc](https://github.com/PerryLink/dsh-repair-order-qc)** |  |
| **[dsh-research-report](https://github.com/PerryLink/dsh-research-report)** |  |
| **[dsh-review-reply-check](https://github.com/PerryLink/dsh-review-reply-check)** |  |
| **[dsh-rulefile-check](https://github.com/PerryLink/dsh-rulefile-check)** |  |
| **[dsh-safety-brief-check](https://github.com/PerryLink/dsh-safety-brief-check)** |  |
| **[dsh-score](https://github.com/PerryLink/dsh-score)** |  |
| **[dsh-session-sync](https://github.com/PerryLink/dsh-session-sync)** |  |
| **[dsh-site-log-check](https://github.com/PerryLink/dsh-site-log-check)** |  |
| **[dsh-skill-pack-security](https://github.com/PerryLink/dsh-skill-pack-security)** |  |
| **[dsh-soe-decision-check](https://github.com/PerryLink/dsh-soe-decision-check)** |  |
| **[dsh-soilwater-check](https://github.com/PerryLink/dsh-soilwater-check)** |  |
| **[dsh-sop-sync-check](https://github.com/PerryLink/dsh-sop-sync-check)** |  |
| **[dsh-spc-gbt-adapter](https://github.com/PerryLink/dsh-spc-gbt-adapter)** |  |
| **[dsh-talk](https://github.com/PerryLink/dsh-talk)** |  |
| **[dsh-tender-extract](https://github.com/PerryLink/dsh-tender-extract)** |  |
| **[dsh-tender-matrix](https://github.com/PerryLink/dsh-tender-matrix)** |  |
| **[dsh-test-drive](https://github.com/PerryLink/dsh-test-drive)** |  |
| **[dsh-ticktick](https://github.com/PerryLink/dsh-ticktick)** |  |
| **[dsh-translate](https://github.com/PerryLink/dsh-translate)** |  |
| **[dsh-warranty-calc](https://github.com/PerryLink/dsh-warranty-calc)** |  |
| **[dsh-budget](https://github.com/PerryLink/dsh-budget)** | 🧊 FROZEN — see the repo README |
| **[dsh-claude-move](https://github.com/PerryLink/dsh-claude-move)** | 🧊 FROZEN — see the repo README |
| **[dsh-defend](https://github.com/PerryLink/dsh-defend)** | 🧊 FROZEN — see the repo README |
| **[dsh-draw](https://github.com/PerryLink/dsh-draw)** | 🧊 FROZEN — see the repo README |
| **[dsh-reach](https://github.com/PerryLink/dsh-reach)** | 🧊 FROZEN — see the repo README |
| **[dsh-background-agents](https://github.com/PerryLink/dsh-background-agents)** | 🚫 RETIRED — see the repo README |
| **[dsh-session-pin](https://github.com/PerryLink/dsh-session-pin)** | 🚫 RETIRED — see the repo README |
| **[dsh-team-rooms](https://github.com/PerryLink/dsh-team-rooms)** | 🚫 RETIRED — see the repo README |

</details>

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-matrix contributors.
