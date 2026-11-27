import type { CRMEntry, ContactStatus } from '../crm/types'
import MeetingLocation from './MeetingLocation'
import WeeklyAvailability from './WeeklyAvailability'

interface Props {
  entry: CRMEntry
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
  onChange,
}: Props) {
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

      <td>
        <input
          aria-label="Hourly quote in dollars"
          type="number"
          min="0"
          step="1"
          placeholder="$ / hr"
          value={entry.hourlyQuote ?? ''}
          onChange={(event) => {
            const value = event.target.value
            const quote = event.target.valueAsNumber

            if (value === '') {
              onChange({ hourlyQuote: null })
            } else if (Number.isFinite(quote) && quote >= 0) {
              onChange({ hourlyQuote: quote })
            }
          }}
        />
      </td>



      <td>
        <MeetingLocation
          value={entry.meetingLocation ?? ''}
          onChange={(meetingLocation) =>
            onChange({ meetingLocation })
          }
        />
      </td>

      <td>
        <input
          aria-label="Location fee per visit"
          type="number"
          min="0"
          step="1"
          placeholder="$"
          value={entry.locationFee ?? ''}
          onChange={(event) => {
            const value = event.target.value
            const fee = event.target.valueAsNumber

            if (value === '') {
              onChange({ locationFee: null })
            } else if (Number.isFinite(fee) && fee >= 0) {
              onChange({ locationFee: fee })
            }
          }}
        />
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
