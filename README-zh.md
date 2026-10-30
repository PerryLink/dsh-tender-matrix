# dsh-tender-matrix — 评标因素评分矩阵核对

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

<!-- topblock:v1 -->
> **这是什么**　评标评分矩阵核对。输出一份「哪一行、哪一栏、差什么」的清单。
> **给谁用**　评标辅助、招标代理；不用懂命令行。
> **你交什么**　这项核对用到的原始材料（表格、清单或文书）；不改原件。Excel 可先转成 JSON/YAML，对话里也能代转。
> **它不做什么**　不判合规、不认定责任、不替代审核人；只列材料内部能逐条指认的差异。
> **怎么开始**　在 WorkBuddy / 扣子搜「投标合规核对包」（本检查是其中一项；上架以商城为准）；或命令行：
> `dsh plugin --profile <name> add dsh-tender-matrix`
<!-- /topblock:v1 -->

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-tender-matrix?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-tender-matrix?ref=badge)

`dsh-tender-matrix` 读取一份评标因素评分矩阵——表头加每个评审因素一行——核对这份矩阵自身的算术与齐备：是否写明项目与评标办法、单项得分是否超过该项分值上限、各项分值上限合计是否等于你配置的总分、某个投标人的各项得分合计是否等于你配置的合计、每条评分是否填写评分依据、评审因素序号是否重复、评分依据栏是否残留未替换的占位符。

## Install

```sh
dsh plugin --profile <name> add dsh-tender-matrix
dsh --profile <name> --dump-config | grep 'dsh-tender-matrix'
```

## 实际输出长什么样

![dsh-tender-matrix 工作流图：调用 → 插件 → 结果。](docs/assets/dsh-tender-matrix-flow.svg)

*工作流概览：调用 → 插件 → 结果。下面的示例使用实际命令面。*


下面这张图说明流程，**不是**某次运行的输出；正文见下。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

### 示例

下表是示例集：第一行是详细走查，其余行是简短案例。

#### 详细输出

**工具** `tender_matrix`

**输入**

~~~json
{"rows":[{"评审因素":"施工组织设计","分值":"30","投标人A":"32"}]}
~~~
 
**输出**

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

*来源 `dsh-tender-matrix/tests/fixtures/TM-002/TM-002-unsafe.json`*

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

**边界（中文译文，以英文原文为准）：** 本插件核对一份**评标因素评分矩阵**的算术——矩阵是否写明项目与评标办法，单项得分是否不超过该项分值上限，各分值上限合计是否等于你配置的数字，某投标人的得分合计是否等于你配置的数字，每项得分是否记录评分依据，评审因素序号是否唯一，以及是否残留占位符。它**不**判定评分是否恰当、评标是否公平，也不判定谁应当中标。**评分是评标委员会的独立判断，权重与评审标准属于招标文件。**

> ### ⚠️ 在相信报告中的引文之前，请先读这一节（以英文原文为准）
>
> **本插件规则库中的每一个 `excerpt` 都是它所引条款的逐字引文，且引文门会逐段回到 `rules/evidence/` 的记录里复核。**
> 条款怎么写，规则就怎么引；条款只是隐含，规则就停在 `warn`：由原则性条款推出的检查封顶在 `error` 之下，
> 并在自己的 `note` 里说明。规则库不会做的事是——转述一段条款，然后把转述当成引文。


## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-rc.2`。**已声明 `engines.dsh`**：0.2.1 起由宿主单独裁决，范围为 `>=0.2.1-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

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

## PerryLink DSH Plugin Family

完整清单（62 个核查器 + 通用插件）见 [按材料选核查器](https://perrylink.github.io/zh/checkers/choose/)；本仓只是其中一个。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-matrix contributors.
