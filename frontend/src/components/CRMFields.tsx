import type { CRMEntry, ContactStatus } from '../crm/types'
import { calculateTotal } from '../crm/totalCost'
import WeeklyAvailability from './WeeklyAvailability'

interface Props {
  entry: CRMEntry
  calculatorOpen: boolean
  onToggleCalculator: () => void
  onChange: (changes: Partial<Omit<CRMEntry, 'updatedAt'>>) => void
}

const statuses: { value: ContactStatus; label: string }[] = [
  { value: 'not_contacted', label: 'Not contacted' },
  { value: 'no_answer', label: 'No answer' },
  { value: 'voicemail', label: 'Left voicemail' },
  { value: 'email_sent', label: 'Email sent' },
  { value: 'awaiting_response', label: 'Awaiting response' },
  { value: 'available', label: 'Available' },
  { value: 'unavailable', label: 'Unavailable' },
  { value: 'hired', label: 'Hired' },
]

export default function CRMFields({
  entry,
  calculatorOpen,
  onToggleCalculator,
  onChange,
}: Props) {
  const total = calculateTotal(entry)

  return (
    <>
      <td>
        <select
          aria-label="Contact status"
          value={entry.status}
          onChange={(event) =>
            onChange({
              status: event.target.value as ContactStatus,
            })
          }
        >
          {statuses.map((status) => (
            <option key={status.value} value={status.value}>
              {status.label}
            </option>
          ))}
        </select>
      </td>

      <td className="crm-total">
        <button
          type="button"
          className="calculator-toggle"
          aria-expanded={calculatorOpen}
          aria-label={calculatorOpen ? 'Close calculator' : 'Open calculator'}
          onClick={onToggleCalculator}
        >
          <span>{total == null ? '—' : '$' + total.toFixed(2)}</span>
          <svg width="18" height="18" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" strokeWidth="1.6"
            aria-hidden="true">
            <rect x="5" y="2" width="14" height="20" rx="2" />
            <path d="M8 6h8M8 10h2m4 0h2M8 14h2m4 0h2M8 18h2m4 0h2" />
          </svg>
          <span aria-hidden="true"> {calculatorOpen ? '▴' : '▾'}</span>
        </button>
      </td>

      <td>
        <WeeklyAvailability
          value={entry.availability ?? {}}
          onChange={(availability) =>
            onChange({ availability })
          }
        />
      </td>

      <td>
        <select
          aria-label="Transports child"
          value={
            entry.transportsChild == null
              ? 'unknown'
              : entry.transportsChild ? 'yes' : 'no'
          }
          onChange={(event) => {
            const value = event.target.value

            onChange({
              transportsChild:
                value === 'unknown' ? null : value === 'yes',
            })
          }}
        >
          <option value="unknown">Unknown</option>
          <option value="yes">Yes</option>
          <option value="no">No</option>
        </select>
      </td>

      <td>
        <textarea
          aria-label="Personal notes"
          placeholder="Add notes..."
          rows={2}
          maxLength={2000}
          value={entry.notes}
          onChange={(event) =>
            onChange({ notes: event.target.value })
          }
        />
      </td>
    </>
  )
}
