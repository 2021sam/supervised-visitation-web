import { useState } from 'react'

const RADIUS_OPTIONS = [
  5, 10, 15, 20, 25, 30, 50, 75, 100, 500, 1000,
]

interface Props {
  onSearch: (zipCode: string, radiusMiles: number) => void
}

export default function ZipRadiusSelector({
  onSearch,
}: Props) {
  const [zipCode, setZipCode] = useState('')
  const [radiusMiles, setRadiusMiles] = useState(25)

  const validZip = /^[0-9]{5}$/.test(zipCode)

  return (
    <form
      className="zip-radius-selector"
      onSubmit={(event) => {
        event.preventDefault()

        if (validZip) {
          onSearch(zipCode, radiusMiles)
        }
      }}
    >
      <label>
        ZIP code
        <input
          type="text"
          inputMode="numeric"
          autoComplete="postal-code"
          maxLength={5}
          placeholder="Enter ZIP code"
          value={zipCode}
          onChange={(event) =>
            setZipCode(
              event.target.value.replace(/[^0-9]/g, '')
            )
          }
          required
        />
      </label>

      <label>
        Distance
        <select
          value={radiusMiles}
          onChange={(event) =>
            setRadiusMiles(Number(event.target.value))
          }
        >
          {RADIUS_OPTIONS.map((miles) => (
            <option key={miles} value={miles}>
              {miles} miles
            </option>
          ))}
        </select>
      </label>

      <button type="submit" disabled={!validZip}>
        Search
      </button>
    </form>
  )
}
