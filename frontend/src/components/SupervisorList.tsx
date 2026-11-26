import type { Supervisor } from '../types/supervisor'

interface Props {
  supervisors: Supervisor[]
}

export default function SupervisorList({ supervisors }: Props) {
  if (supervisors.length === 0) {
    return <p>No supervisors found.</p>
  }

  return (
    <div className="supervisor-list">
      {supervisors.map((supervisor) => (
        <article
          key={supervisor.supervisor_id}
          className="supervisor-card"
        >
          <h2>{supervisor.name}</h2>

          {supervisor.phone && (
            <p>Phone: {supervisor.phone}</p>
          )}

          {supervisor.email && (
            <p>Email: {supervisor.email}</p>
          )}

          {supervisor.website && (
            <p>Website: {supervisor.website}</p>
          )}
        </article>
      ))}
    </div>
  )
}
