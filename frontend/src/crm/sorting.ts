import { calculateTotal } from './totalCost'
import type { Supervisor } from '../types/supervisor'
import type { CRMRecords } from './types'
import { getEffectiveEntry } from './effectiveEntry'

export type SortField =
  | 'name'
  | 'distance'
  | 'languages'
  | 'hourlyQuote'
  | 'locationFee'
  | 'hours'
  | 'totalCost'
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
  const entry = getEffectiveEntry(
    supervisor,
    records[String(supervisor.supervisor_id)],
  )

  switch (field) {
    case 'name':
      return supervisor.name

    case 'languages':
      return supervisor.languages?.trim() || null

    case 'distance':
      return supervisor.distance_miles ?? null

    case 'hourlyQuote':
      return entry?.hourlyQuote ?? null

    case 'hours':
      return entry.hours ?? null

    case 'totalCost':
      return calculateTotal(entry)

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
