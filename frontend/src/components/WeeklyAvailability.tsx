import type {
  Weekday,
  TimeRange,
  WeeklyAvailability as Schedule,
} from '../crm/types'

interface Props {
  value: Schedule
  onChange: (value: Schedule) => void
}

const days: Weekday[] = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
]

function formatTime(time: string): string {
  const [hours, minutes] = time.split(':').map(Number)
  return `${hours % 12 || 12}:${String(minutes).padStart(2, '0')} ${hours < 12 ? 'AM' : 'PM'}`
}

export default function WeeklyAvailability({ value, onChange }: Props) {
  const selectedDays = days.filter((day) => value[day])

  function toggleDay(day: Weekday, checked: boolean) {
    const next = { ...value }

    if (checked) {
      next[day] = { start: '09:00', end: '17:00' }
    } else {
      delete next[day]
    }

    onChange(next)
  }

  function updateTime(day: Weekday, changes: Partial<TimeRange>) {
    const current = value[day]
    if (!current) return

    onChange({
      ...value,
      [day]: { ...current, ...changes },
    })
  }

  return (
    <details className="weekly-availability">
      <summary>
        {selectedDays.length
          ? `${selectedDays.length} day(s) specified`
          : 'Set availability'}
      </summary>

      {days.map((day) => {
        const range = value[day]

        return (
          <div key={day}>
            <label>
              <input
                type="checkbox"
                checked={Boolean(range)}
                onChange={(event) =>
                  toggleDay(day, event.target.checked)
                }
              />
              {day.charAt(0).toUpperCase() + day.slice(1)}
            </label>

            {range && (
              <div>
                <input
                  type="time"
                  aria-label={`${day} start time`}
                  value={range.start}
                  required
                  onChange={(event) => {
                    if (event.target.value) {
                      updateTime(day, { start: event.target.value })
                    }
                  }}
                />
                {' – '}
                <input
                  type="time"
                  aria-label={`${day} end time`}
                  value={range.end}
                  required
                  onChange={(event) => {
                    if (event.target.value) {
                      updateTime(day, { end: event.target.value })
                    }
                  }}
                />
                {range.end <= range.start && (
                  <small role="alert">
                    End time must be after start time.
                  </small>
                )}
              </div>
            )}
          </div>
        )
      })}

      {selectedDays.map((day) => {
        const range = value[day]!
        return (
          <div key={day}>
            {day.slice(0, 3).toUpperCase()}:
            {' '}{formatTime(range.start)} – {formatTime(range.end)}
          </div>
        )
      })}
    </details>
  )
}
