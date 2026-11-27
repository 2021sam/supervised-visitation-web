import { useRef, useState } from 'react'
import { createCRMEntry } from './types'
import type { CRMEntry } from './types'
import { loadCRMRecords, saveCRMRecords } from './storage'

export function useCRM() {
  const [records, setRecords] = useState(loadCRMRecords)
  const [storageError, setStorageError] = useState(false)
  const recordsRef = useRef(records)

  function getEntry(supervisorId: number): CRMEntry {
    return { ...createCRMEntry(), ...records[String(supervisorId)] }
  }

  function updateEntry(
    supervisorId: number,
    changes: Partial<Omit<CRMEntry, 'updatedAt'>>,
  ) {
    const key = String(supervisorId)
    const previous = recordsRef.current

    const nextRecords = {
      ...previous,
      [key]: {
        ...previous[key],
        ...changes,
        updatedAt: new Date().toISOString(),
      },
    }

    recordsRef.current = nextRecords
    setRecords(nextRecords)
    setStorageError(!saveCRMRecords(nextRecords))
  }

  return {
    records,
    getEntry,
    updateEntry,
    storageError,
  }
}
