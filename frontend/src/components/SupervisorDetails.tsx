import type { Supervisor } from '../types/supervisor'

interface Props {
  supervisor: Supervisor
}

export default function SupervisorDetails({ supervisor }: Props) {
  const fields = [
    ['Service areas', supervisor.service_area],
    ['Counties served', supervisor.service_counties],
    ['Languages', supervisor.languages],
    ['Additional information', supervisor.additional_info],
  ].filter(([, value]) => value?.trim())

  if (fields.length === 0) {
    return null
  }

  return (
    <details style={{ marginTop: '6px' }}>
      <summary style={{ cursor: 'pointer' }}>
        Details
      </summary>

      <div style={{
        whiteSpace: 'pre-wrap',
        minWidth: '240px',
        maxWidth: '400px',
        fontSize: '0.9rem',
        overflowWrap: 'anywhere',
      }}>
        {fields.map(([label, value]) => (
          <p key={label}>
            <strong>{label}</strong>
            {'\n'}
            {value}
          </p>
        ))}
      </div>
    </details>
  )
}
