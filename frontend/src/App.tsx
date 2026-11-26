import { useEffect, useState } from 'react'
import { fetchSupervisors } from './api/supervisors'
import SupervisorList from './components/SupervisorList'
import type { Supervisor } from './types/supervisor'
import './App.css'

export default function App() {
  const [supervisors, setSupervisors] = useState<Supervisor[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    fetchSupervisors()
      .then((data) => {
        if (active) setSupervisors(data.supervisors)
      })
      .catch((error: Error) => {
        if (active) setError(error.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <main>
      <h1>Supervised Visitation Directory</h1>
      <p>Find supervised visitation providers nationwide.</p>

      {loading ? (
        <p>Loading supervisors...</p>
      ) : error ? (
        <p role="alert">{error}</p>
      ) : (
        <>
          <p>{supervisors.length} supervisors found</p>
          <SupervisorList supervisors={supervisors} />
        </>
      )}
    </main>
  )
}
