import type { County } from '../types/county'

interface Props {
  counties: County[]
  selectedCounty: string
  onChange: (geoid: string) => void
}

export default function CountySelector({
  counties,
  selectedCounty,
  onChange,
}: Props) {
  return (
    <div className="county-selector">
      <label htmlFor="county">County</label>

      <select
        id="county"
        value={selectedCounty}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">All counties</option>

        {counties.map((county) => (
          <option
            key={county.geoid}
            value={county.geoid}
          >
            {county.county_name}
          </option>
        ))}
      </select>
    </div>
  )
}
