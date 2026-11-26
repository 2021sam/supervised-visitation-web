import { useState } from 'react'
import { sortSupervisors } from '../crm/sorting'
import type { SortConfig, SortField } from '../crm/sorting'
import SortableHeader from './SortableHeader'
import type { Supervisor } from '../types/supervisor'
import { useCRM } from '../crm/useCRM'
import CRMFields from './CRMFields'
import './SupervisorTable.css'

interface Props {
  supervisors: Supervisor[]
}

export default function SupervisorTable({
  supervisors,
}: Props) {
  const { records, getEntry, updateEntry, storageError } = useCRM()

  const [sort, setSort] = useState<SortConfig>({
    field: 'name',
    direction: 'asc',
  })

  function handleSort(field: SortField) {
    setSort((previous) => ({
      field,
      direction:
        previous.field === field && previous.direction === 'asc'
          ? 'desc'
          : 'asc',
    }))
  }

  const sortedSupervisors = sortSupervisors(
    supervisors,
    records,
    sort,
  )

  if (supervisors.length === 0) {
    return <p>No supervisors found.</p>
  }

  return (
    <div className="supervisor-table-container">
      {storageError && (
        <p role="alert">
          Your changes could not be saved to browser storage.
        </p>
      )}

      <table className="supervisor-table">
        <thead>
          <tr>
            <SortableHeader
              label="Supervisor"
              field="name"
              sort={sort}
              onSort={handleSort}
            />
            <th scope="col">Phone</th>
            <th scope="col">Email</th>
            <th scope="col">Website</th>
            <SortableHeader
              label="Contact status"
              field="status"
              sort={sort}
              onSort={handleSort}
            />
            <SortableHeader
              label="Quote ($/hr)"
              field="hourlyQuote"
              sort={sort}
              onSort={handleSort}
            />
            <th scope="col">Meeting location</th>
            <SortableHeader
              label="Location fee ($)"
              field="locationFee"
              sort={sort}
              onSort={handleSort}
              title="Additional fee per visit at the agreed location"
            />
            <th scope="col">Availability</th>
            <SortableHeader
              label="Transports child"
              field="transportsChild"
              sort={sort}
              onSort={handleSort}
            />
            <th scope="col">Notes</th>
          </tr>
        </thead>

        <tbody>
          {sortedSupervisors.map((supervisor) => (
            <tr key={supervisor.supervisor_id}>
              <td>{supervisor.name}</td>
              <td>{supervisor.phone || '—'}</td>
              <td>{supervisor.email || '—'}</td>
              <td>{supervisor.website || '—'}</td>

              <CRMFields
                entry={getEntry(supervisor.supervisor_id)}
                onChange={(changes) =>
                  updateEntry(supervisor.supervisor_id, changes)
                }
              />
            </tr>
          ))}
        </tbody>
      </table>

      <p>
        Your CRM entries are saved in
        this browser. No account is required.
        Avoid entering confidential case or child information.
      </p>
    </div>
  )
}
