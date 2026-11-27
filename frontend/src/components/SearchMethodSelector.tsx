export type SearchMethod = 'county' | 'radius'

interface Props {
  method: SearchMethod
  onChange: (method: SearchMethod) => void
}

export default function SearchMethodSelector({
  method,
  onChange,
}: Props) {
  return (
    <fieldset className="search-method-selector">
      <legend>Search by</legend>

      <label>
        <input
          type="radio"
          name="search-method"
          checked={method === 'county'}
          onChange={() => onChange('county')}
        />
        County
      </label>

      <label>
        <input
          type="radio"
          name="search-method"
          checked={method === 'radius'}
          onChange={() => onChange('radius')}
        />
        ZIP code / Distance
      </label>
    </fieldset>
  )
}
