import type { CRMRecords } from './types'

const STORAGE_KEY = 'supervised-visitation.crm.v1'

export function loadCRMRecords(): CRMRecords {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)

    if (!stored) return {}

    const records = JSON.parse(stored)

    if (
      !records ||
      typeof records !== 'object' ||
      Array.isArray(records)
    ) {
      return {}
    }

    return records as CRMRecords
  } catch {
    return {}
  }
}

export function saveCRMRecords(records: CRMRecords): boolean {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(records),
    )

    return true
  } catch {
    return false
  }
}
