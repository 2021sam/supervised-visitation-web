import type { Supervisor } from '../types/supervisor'
import type { CRMRecords } from './types'

export type SortField =
  | 'name'
  | 'hourlyQuote'
  | 'locationFee'
  | 'status'
  | 'transportsChild'

export type SortDirection = 'asc' | 'desc'

export interface SortConfig {
  field: SortField
  direction: SortDirection
}

function getSortValue(
  supervisor: Supervisor,
  records: CRMRecords,
  field: SortField,
): string | number | null {
  const entry = records[String(supervisor.supervisor_id)]

  switch (field) {
    case 'name':
      return supervisor.name

    case 'hourlyQuote':
      return entry?.hourlyQuote ?? null

    case 'locationFee':
      return entry?.locationFee ?? null

    case 'status':
      return entry?.status ?? 'not_contacted'

    case 'transportsChild':
      return entry?.transportsChild == null
        ? null
        : Number(entry.transportsChild)
  }
}

export function sortSupervisors(
  supervisors: Supervisor[],
  records: CRMRecords,
  config: SortConfig,
): Supervisor[] {
  const direction = config.direction === 'asc' ? 1 : -1

  return [...supervisors].sort((a, b) => {
    const left = getSortValue(a, records, config.field)
    const right = getSortValue(b, records, config.field)

    let comparison = 0

    if (left === null && right !== null) return 1
    if (right === null && left !== null) return -1

    if (typeof left === 'number' && typeof right === 'number') {
      comparison = left - right
    } else if (left !== null && right !== null) {
      comparison = String(left).localeCompare(
        String(right),
        undefined,
        { sensitivity: 'base', numeric: true },
      )
    }

    return (
      comparison * direction ||
      a.name.localeCompare(b.name) ||
      a.supervisor_id - b.supervisor_id
    )
  })
}
