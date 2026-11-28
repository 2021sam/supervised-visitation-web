import type { Supervisor } from '../types/supervisor'

interface Props {
  supervisor: Supervisor
}

function yesNo(value?: number | null) {
  return value === 1 ? 'Yes' : value === 0 ? 'No' : null
}

function rate(value?: number | null, unit = '') {
  return value == null
    ? null
    : `$${(value / 1000).toFixed(3).replace(/(\.\d{2})0$/, '$1')}${unit}`
}

export default function SupervisorDetails({ supervisor: s }: Props) {
  const fields = [
    ['Professional title', s.professional_title],
    ['Provider type', s.provider_type],
    ['Service areas', s.service_area],
    ['Counties served', s.service_counties],
    ['Languages', s.languages],
    ['Public reference address', s.reference_point],
    ['Accepting new clients', yesNo(s.accepting_new_clients)],
    ['Supervised visitation', yesNo(s.supervised_visitation)],
    ['Supervised exchange', yesNo(s.supervised_exchange)],
    ['Transportation', yesNo(s.transportation)],
    ['Virtual visitation', yesNo(s.virtual_visitation)],
    ['On-site visitation', yesNo(s.on_site_visitation)],
    ['Off-site visitation', yesNo(s.off_site_visitation)],
    ['Handwritten reports', yesNo(s.handwritten_reports)],
    ['Typed reports', yesNo(s.typed_reports)],
    ['Smoker', yesNo(s.is_smoker)],
    ['Vaping', yesNo(s.uses_vape)],
    ['Cell phone', yesNo(s.phone_is_cell)],
    ['Mileage charge', rate(s.price_per_mile, ' / mile')],
    ['Driving time charge', rate(s.driving_hourly_rate, ' / hour')],
    ['Round-trip mileage charges', yesNo(s.charges_roundtrip_mileage)],
    ['Round-trip driving time charges', yesNo(s.charges_roundtrip_driving_time)],
    ['Additional information', s.additional_info],
  ].filter(([, value]) => value?.trim())

  const calendar = s.calendar_url?.trim()
  const safeCalendar = calendar && /^https?:\/\//i.test(calendar)
    ? calendar
    : null

  if (!fields.length && !safeCalendar && !s.profile_photo) {
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
        {s.profile_photo && (
          <img
            src={s.profile_photo}
            alt={s.name}
            loading="lazy"
            style={{
              width: '128px',
              height: '128px',
              objectFit: 'cover',
              borderRadius: '8px',
              marginTop: '10px',
            }}
          />
        )}

        {fields.map(([label, value]) => (
          <p key={label}>
            <strong>{label}</strong>
            {'\n'}
            {value}
          </p>
        ))}

        {safeCalendar && (
          <p>
            <a
              href={safeCalendar}
              target="_blank"
              rel="noopener noreferrer"
            >
              View calendar
            </a>
          </p>
        )}
      </div>
    </details>
  )
}
