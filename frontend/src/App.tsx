import { useEffect, useState } from 'react'
import { fetchSupervisors } from './api/supervisors'
import { fetchStates } from './api/states'
import { fetchCounties } from './api/counties'
import StateSelector from './components/StateSelector'
import CountySelector from './components/CountySelector'
import SearchMethodSelector from './components/SearchMethodSelector'
import type { SearchMethod } from './components/SearchMethodSelector'
import ZipRadiusSelector from './components/ZipRadiusSelector'
import { getAvailableLanguages, filterByLanguages } from './search/languages'
import SupervisorTable from './components/SupervisorTable'
import type { Supervisor } from './types/supervisor'
import type { State } from './types/state'
import type { County } from './types/county'
import AuthPanel from './auth/AuthPanel'
import './App.css'

export default function App() {
  const [states, setStates] = useState<State[]>([])
  const [counties, setCounties] = useState<County[]>([])
  const [selectedState, setSelectedState] = useState('')
  const [selectedCounty, setSelectedCounty] = useState('')
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>(['English'])
  const [searchMethod, setSearchMethod] =
    useState<SearchMethod>('county')

  const [radiusSearch, setRadiusSearch] = useState<{
    zipCode: string
    radiusMiles: number
  } | null>(null)

  const [supervisors, setSupervisors] = useState<Supervisor[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [stateError, setStateError] = useState('')
  const [countyError, setCountyError] = useState('')

  useEffect(() => {
    let active = true

    fetchStates()
      .then((data) => {
        if (active) setStates(data.states)
      })
      .catch((error: Error) => {
        if (active) setStateError(error.message)
      })

    return () => { active = false }
  }, [])

  useEffect(() => {
    if (!selectedState) return

    let active = true

    fetchCounties(selectedState)
      .then((data) => {
        if (active) setCounties(data.counties)
      })
      .catch((error: Error) => {
        if (active) setCountyError(error.message)
      })

    return () => { active = false }
  }, [selectedState])

  useEffect(() => {
    if (searchMethod === 'radius' && !radiusSearch) return

    let active = true

    const request = searchMethod === 'radius' && radiusSearch
      ? fetchSupervisors(
          selectedState,
          undefined,
          undefined,
          radiusSearch.zipCode,
          radiusSearch.radiusMiles,
        )
      : fetchSupervisors(
          selectedState,
          undefined,
          selectedCounty,
        )

    request
      .then((data) => {
        if (active) {
          setSupervisors(data.supervisors)
          setSelectedLanguages(['English'])
        }
      })
      .catch((error: Error) => {
        if (active) setError(error.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => { active = false }
  }, [
    selectedState,
    selectedCounty,
    searchMethod,
    radiusSearch,
  ])

  function handleStateChange(stateCode: string) {
    if (stateCode === selectedState) return

    setLoading(true)
    setError('')
    setCountyError('')
    setCounties([])
    setSelectedCounty('')
    setSearchMethod('county')
    setRadiusSearch(null)
    setSelectedState(stateCode)
  }

  function handleCountyChange(geoid: string) {
    if (geoid === selectedCounty) return

    setLoading(true)
    setError('')
    setSelectedCounty(geoid)
  }

  function handleSearchMethodChange(method: SearchMethod) {
    if (method === searchMethod) return

    setError('')
    setSelectedCounty('')
    setRadiusSearch(null)
    setLoading(method === 'county')
    setSearchMethod(method)
  }

  function handleRadiusSearch(
    zipCode: string,
    radiusMiles: number,
  ) {
    setLoading(true)
    setError('')
    setRadiusSearch({ zipCode, radiusMiles })
  }

  const languages = getAvailableLanguages(supervisors)
  const filteredSupervisors = filterByLanguages(
    supervisors,
    selectedLanguages,
  )

  return (
    <main>
      <AuthPanel />
      <h1>Supervised Visitation Directory</h1>
      <p>Find supervised visitation providers nationwide.</p>

      <StateSelector
        states={states}
        selectedState={selectedState}
        onChange={handleStateChange}
      />

      {selectedState && (
        <>
          <SearchMethodSelector
            method={searchMethod}
            onChange={handleSearchMethodChange}
          />

          {searchMethod === 'county' ? (
            <CountySelector
              counties={counties}
              selectedCounty={selectedCounty}
              onChange={handleCountyChange}
            />
          ) : (
            <ZipRadiusSelector
              key={selectedState}
              onSearch={handleRadiusSearch}
            />
          )}
        </>
      )}

      {stateError && <p role="alert">{stateError}</p>}

      {searchMethod === 'county' && countyError && (
        <p role="alert">{countyError}</p>
      )}

      {searchMethod === 'radius' && (
        <p>
          Distances are approximate straight-line distances.
          Supervisors without usable location information
          are excluded. County search may show more results.
        </p>
      )}

      {searchMethod === 'radius' && !radiusSearch ? (
        <p>Enter a ZIP code and select a search distance.</p>
      ) : loading ? (
        <p>Loading supervisors...</p>
      ) : error ? (
        <p role="alert">{error}</p>
      ) : (
        <>
          <p>{filteredSupervisors.length} supervisors found</p>
          <SupervisorTable
            key={searchMethod}
            supervisors={filteredSupervisors}
            languages={languages}
            selectedLanguages={selectedLanguages}
            onLanguageChange={setSelectedLanguages}
            showDistance={searchMethod === 'radius'}
          />
        </>
      )}
    </main>
  )
}
