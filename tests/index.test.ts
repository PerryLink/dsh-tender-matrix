import { describeTablePlugin } from './table-plugin-suite.ts'
import { Config } from '../src/config.ts'
import { parseMaterial, runCheck, SPEC } from '../src/model.ts'
import { buildView } from '../src/view.ts'
import { inject, name, resolvePackageFile, TOOL_NAME } from '../src/index.ts'

describeTablePlugin({
  name,
  inject,
  TOOL_NAME,
  resolvePackageFile,
  Config,
  rulesFile: 'rules/tender-matrix.yaml',
  parseMaterial,
  runCheck,
  buildView,
  columnNames: SPEC.columns,
  samples: {
    good: {
      project: '某某工程施工招标',
      tenderNo: 'ZB-2026-018',
      method: '综合评估法',
      rows: [
        {
          序号: '1',
          评审因素: '施工组织设计',
          分值: '30',
          投标人A: '26',
          投标人B: '24',
          投标人C: '28',
          评分依据: '按招标文件评标办法第 3.2 条',
        },
      ],
    },
    unknownColumn: { rows: [{ 备注: '甲' }] },
  },
})
