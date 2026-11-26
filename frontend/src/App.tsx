import { useEffect, useState } from 'react'
import { fetchSupervisors } from './api/supervisors'
import { fetchStates } from './api/states'
import { fetchCounties } from './api/counties'
import StateSelector from './components/StateSelector'
import CountySelector from './components/CountySelector'
import SupervisorTable from './components/SupervisorTable'
import type { Supervisor } from './types/supervisor'
import type { State } from './types/state'
import type { County } from './types/county'
import './App.css'

export default function App() {
  const [states, setStates] = useState<State[]>([])
  const [counties, setCounties] = useState<County[]>([])
  const [selectedState, setSelectedState] = useState('')
  const [selectedCounty, setSelectedCounty] = useState('')
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
    let active = true

    fetchSupervisors(selectedState, undefined, selectedCounty)
      .then((data) => {
        if (active) setSupervisors(data.supervisors)
      })
      .catch((error: Error) => {
        if (active) setError(error.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => { active = false }
  }, [selectedState, selectedCounty])

  function handleStateChange(stateCode: string) {
    if (stateCode === selectedState) return

    setLoading(true)
    setError('')
    setCountyError('')
    setCounties([])
    setSelectedCounty('')
    setSelectedState(stateCode)
  }

  function handleCountyChange(geoid: string) {
    if (geoid === selectedCounty) return

    setLoading(true)
    setError('')
    setSelectedCounty(geoid)
  }

  return (
    <main>
      <h1>Supervised Visitation Directory</h1>
      <p>Find supervised visitation providers nationwide.</p>

      <StateSelector
        states={states}
        selectedState={selectedState}
        onChange={handleStateChange}
      />

      {selectedState && (
        <CountySelector
          counties={counties}
          selectedCounty={selectedCounty}
          onChange={handleCountyChange}
        />
      )}

      {stateError && <p role="alert">{stateError}</p>}
      {countyError && <p role="alert">{countyError}</p>}

      {loading ? (
        <p>Loading supervisors...</p>
      ) : error ? (
        <p role="alert">{error}</p>
      ) : (
        <>
          <p>{supervisors.length} supervisors found</p>
          <SupervisorTable supervisors={supervisors} />
        </>
      )}
    </main>
  )
}
