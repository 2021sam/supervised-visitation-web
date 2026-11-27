import type { Supervisor } from '../types/supervisor'

interface Props {
  supervisor: Supervisor
}

export default function SupervisorZip({
  supervisor,
}: Props) {
  const zipCode =
    supervisor.resolved_zip_code ||
    supervisor.service_zip_code ||
    supervisor.zip_code

  if (!zipCode) {
    return <span>—</span>
  }

  if (supervisor.distance_basis === 'service_area_city') {
    return (
      <span title="Estimated from the first listed service-area city">
        {zipCode} (est.)
      </span>
    )
  }

  return <span>{zipCode}</span>
}
