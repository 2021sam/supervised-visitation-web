import type { CRMEntry } from '../crm/types'
import { calculateTotal } from '../crm/totalCost'
import MeetingLocation from './MeetingLocation'

interface Props {
  entry: CRMEntry
  onClose: () => void
  onChange: (changes: Partial<Omit<CRMEntry, 'updatedAt'>>) => void
}

export default function CostCalculator({ entry, onChange, onClose }: Props) {
  const total = calculateTotal(entry)

  return (
    <div className="cost-calculator">
      <header className="calculator-heading">
        <strong>Cost calculator</strong>
        <button
          type="button"
          aria-label="Close calculator"
          onClick={onClose}
        >×</button>
      </header>
      <div>
        <label>Hourly rate ($)</label>
        <input
          aria-label="Hourly quote in dollars"
          type="text"
          placeholder="$ / hr"
          value={entry.hourlyQuote ?? ''}
          onChange={(event) =>
            onChange({
              hourlyQuote: event.target.value || null,
            })
          }
        />
      </div>



      <div>
        <label>Hours</label>
        <input
          aria-label="Visitation hours"
          type="number"
          min="0"
          step="any"
          placeholder="Hours"
          value={entry.hours ?? ''}
          onChange={(event) => {
            const hours = event.target.valueAsNumber

            if (event.target.value === '') {
              onChange({ hours: null })
            } else if (Number.isFinite(hours) && hours >= 0) {
              onChange({ hours })
            }
          }}
        />
      </div>



      <div>
        <label>Location fee ($)</label>
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
      </div>

      <div className="crm-total">
        <label>Estimated total ($)</label>
        {total == null ? '' : total.toFixed(2)}
      </div>

      <div>
        <label>Meeting location</label>
        <MeetingLocation
          value={entry.meetingLocation ?? ''}
          onChange={(meetingLocation) =>
            onChange({ meetingLocation })
          }
        />
      </div>

    </div>
  )
}
