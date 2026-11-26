import type { State } from '../types/state'

interface Props {
  states: State[]
  selectedState: string
  onChange: (stateCode: string) => void
}

export default function StateSelector({
  states,
  selectedState,
  onChange,
}: Props) {
  return (
    <div className="state-selector">
      <label htmlFor="state">State</label>

      <select
        id="state"
        value={selectedState}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">Nationwide</option>

        {states.map((state) => (
          <option
            key={state.state_code}
            value={state.state_code}
          >
            {state.state_name}
          </option>
        ))}
      </select>
    </div>
  )
}
