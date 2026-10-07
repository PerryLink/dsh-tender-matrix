/**
 * dsh-tender-matrix — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'tender_matrix'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  seq: ['序号', '评审因素序号', '编号', 'seq', 'no'],
  criterion: ['评审因素', '评分因素', '评审项', 'criterion', 'factor'],
  category: ['评审类别', '类别', '评分项分类', 'category'],
  maxScore: ['分值', '满分', '标准分值', 'maxScore'],
  bidderA: ['投标人A', '投标人一', 'A', 'bidderA'],
  bidderB: ['投标人B', '投标人二', 'B', 'bidderB'],
  bidderC: ['投标人C', '投标人三', 'C', 'bidderC'],
  basis: ['评分依据', '评审依据', '评分标准', 'basis'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'criteria', '评审因素'],
  columns: COLUMNS,
  header: {
  project: ['project', '项目名称', '招标项目名称'],
  tenderNo: ['tenderNo', '招标编号', '项目编号'],
  evaluator: ['evaluator', '评审人', '评标委员会'],
  method: ['method', '评标办法', '评审方法'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '评审因素',
  'criterion',
  '分值',
  'maxScore',
  '评分依据',
  'basis',
  '序号',
  'seq',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
