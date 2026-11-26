import type { SupervisorResponse } from '../types/supervisor'

export async function fetchSupervisors(
  stateCode?: string,
  county?: string,
  countyGeoid?: string,
): Promise<SupervisorResponse> {
  const params = new URLSearchParams()

  if (stateCode) params.set('state_code', stateCode)
  if (county) params.set('county', county)
  if (countyGeoid) params.set('county_geoid', countyGeoid)

  const response = await fetch(`/api/supervisors?${params}`)

  if (!response.ok) {
    throw new Error(`Supervisor API error: ${response.status}`)
  }

  return response.json()
}
