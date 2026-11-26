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
  const { getEntry, updateEntry, storageError } = useCRM()

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
            <th scope="col">Supervisor</th>
            <th scope="col">Phone</th>
            <th scope="col">Email</th>
            <th scope="col">Website</th>
            <th scope="col">Contact status</th>
            <th scope="col">Quote ($/hr)</th>
            <th scope="col">Meeting location</th>
            <th scope="col" title="Additional fee per visit at the agreed location">
              Location fee ($)
            </th>
            <th scope="col">Availability</th>
            <th scope="col">Transports child</th>
            <th scope="col">Notes</th>
          </tr>
        </thead>

        <tbody>
          {supervisors.map((supervisor) => (
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
