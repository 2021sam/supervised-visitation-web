import { useId } from 'react'

interface Props {
  value: string
  onChange: (value: string) => void
}

const locations = [
  'Library',
  'Park',
  "Supervisor's office",
  "Parent's home",
  'Shopping center',
  'Restaurant',
  'Community center',
]

export default function MeetingLocation({ value, onChange }: Props) {
  const listId = useId()

  return (
    <>
      <input
        type="text"
        list={listId}
        aria-label="Meeting location"
        placeholder="Select or enter location"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        maxLength={500}
      />
      <datalist id={listId}>
        {locations.map((location) => (
          <option key={location} value={location} />
        ))}
      </datalist>
    </>
  )
}
