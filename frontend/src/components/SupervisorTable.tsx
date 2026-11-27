import SupervisorDetails from './SupervisorDetails'
import SupervisorZip from './SupervisorZip'
import PhoneLink from './contacts/PhoneLink'
import EmailLink from './contacts/EmailLink'
import WebsiteLink from './contacts/WebsiteLink'
import { useState } from 'react'
import { sortSupervisors } from '../crm/sorting'
import type { SortConfig, SortField } from '../crm/sorting'
import SortableHeader from './SortableHeader'
import type { Supervisor } from '../types/supervisor'
import { useCRM } from '../crm/useCRM'
import { getEffectiveEntry } from '../crm/effectiveEntry'
import CRMFields from './CRMFields'
import './SupervisorTable.css'

interface Props {
  supervisors: Supervisor[]
  showDistance?: boolean
}

export default function SupervisorTable({
  supervisors,
  showDistance = false,
}: Props) {
  const { records, updateEntry, storageError } = useCRM()

  const [sort, setSort] = useState<SortConfig>({
    field: showDistance ? 'distance' : 'name',
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
            <th scope="col">ZIP code</th>
            {showDistance && (
              <SortableHeader
                label="Distance (mi)"
                field="distance"
                sort={sort}
                onSort={handleSort}
                title="Approximate straight-line distance"
              />
            )}
            <th scope="col">Phone</th>
            <th scope="col">Email</th>
            <th scope="col">Website</th>
            <SortableHeader
              label="Languages"
              field="languages"
              sort={sort}
              onSort={handleSort}
            />
            <SortableHeader
              label="Contact status"
              field="status"
              sort={sort}
              onSort={handleSort}
            />
            <SortableHeader
              label="Rate ($/hr)"
              title="Published hourly rate or your confirmed quote"
              field="hourlyQuote"
              sort={sort}
              onSort={handleSort}
            />
            <SortableHeader
              label="Hours"
              field="hours"
              sort={sort}
              onSort={handleSort}
            />
            <SortableHeader
              label="Location fee ($)"
              field="locationFee"
              sort={sort}
              onSort={handleSort}
              title="Additional fee per visit at the agreed location"
            />
            <SortableHeader
              label="Total ($)"
              field="totalCost"
              sort={sort}
              onSort={handleSort}
              title="Hourly rate × hours + location fee"
            />
            <th scope="col">Meeting location</th>
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
              <td>
                {supervisor.name}
                <SupervisorDetails supervisor={supervisor} />
              </td>
              <td><SupervisorZip supervisor={supervisor} /></td>
              {showDistance && (
                <td>
                  {supervisor.distance_miles == null
                    ? '—'
                    : supervisor.distance_miles.toFixed(1)}
                </td>
              )}
              <td><PhoneLink value={supervisor.phone} /></td>
              <td><EmailLink value={supervisor.email} /></td>
              <td><WebsiteLink value={supervisor.website} /></td>
              <td>{supervisor.languages?.trim() || '—'}</td>

              <CRMFields
                entry={getEffectiveEntry(
                  supervisor,
                  records[String(supervisor.supervisor_id)],
                )}
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
