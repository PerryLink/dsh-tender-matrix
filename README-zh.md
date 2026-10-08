# dsh-tender-matrix — 评标因素评分矩阵核对

`dsh-tender-matrix` 读取一份评标因素评分矩阵——表头加每个评审因素一行——核对这份矩阵自身的算术与齐备：是否写明项目与评标办法、单项得分是否超过该项分值上限、各项分值上限合计是否等于你配置的总分、某个投标人的各项得分合计是否等于你配置的合计、每条评分是否填写评分依据、评审因素序号是否重复、评分依据栏是否残留未替换的占位符。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 矩阵每一格都填了，为什么两条合计规则都报 `skipped`？ | 因为两条合计规则出厂都未配置：`TM-003` 把 `maxScore` 一列之和与它的 `target` 相比，`TM-004` 把某个投标人 `bidderA` 一列之和与它的 `target` 相比，两者的 `target` 出厂都是 `0`，即「未配置」，所以在你填入招标文件规定的数字之前，它们各自报 `skipped`，而不是静默通过。配置之后命中只表示「合计与你配置的数字不等」，不代表分值设置不合规；`TM-004` 只做加法核对，刻意没有接到任何「投标人合计」栏上。 |
| 某项分值上限是 100，有一格写了 105；另一行的得分栏写的是「优良」。 | 两种都会报出。`TM-002` 逐项比较 `bidderA` 与 `maxScore`：得分超过该项分值上限的行会被报出；两栏都填了、却都读不出数字或日期时，该行报「无法比较」，不会被放过；两栏缺其一的行则根本不参与比较。它只做数值比较，不判断评分是否恰当；默认核对 A 列，B、C 列请各加一条规则，或覆盖 `leftField`。 |
| 有几行的评分依据栏是空的，会被报出吗？ | 会。`TM-005` 要求凡是携带 `basis` 栏的行都填写该栏，空的逐行报出。它只核对是否写了内容，不判断所记依据是否成立、是否恰当、是否与得分相称。矩阵若根本没有 `basis` 栏，本条报「不适用」，而不是静默通过。 |
| 同一个评审因素序号在矩阵里出现了两次。 | `TM-006` 会报出重复的序号，比较时忽略空白字符。它只核实「唯一」这一件事，而重复会让分值上限合计算错：要么同一个评分项被登记了两次，要么两个评分项被错编成同一号。哪一行才是对的，它不作判断。 |
| 矩阵是照模板抄的，评分依据栏还留着 `【】` 或 `TBD`。 | `TM-007` 会报出 `basis` 栏仍含占位符的行，术语清单为 `【`、`】`、`{{`、`}}`、`XXX`、`xxx`、`待填`、`待补充`、`TBD`、`todo`、`示例`，可按本机构模板调整。它针对的失效方式是：占位符被当成已经记录的理由。本条标题虽同时提到「备注」，核对只读 `basis` 一栏，也不判断依据本身好不好。 |
| 表头没有写明这是哪个项目的矩阵、依据哪份评标办法。 | `TM-001` 要求材料表头提供 `project` 与 `method`，缺哪个报哪个；它只核对表头是否声明这两项，不判断是否与招标文件一致。若本机构表式不含「评标办法」栏，把本条的 `fields` 改为 `[project]`，就不会再去要一栏你的表式本来就没有的字段。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-tender-matrix
dsh --profile <name> --dump-config | grep 'dsh-tender-matrix'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/tender-matrix.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-tender-matrix
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-matrix contributors.
