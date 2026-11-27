import type { SupervisorResponse } from '../types/supervisor'

export async function fetchSupervisors(
  stateCode?: string,
  county?: string,
  countyGeoid?: string,
  zipCode?: string,
  radiusMiles?: number,
): Promise<SupervisorResponse> {
  const params = new URLSearchParams()

  if (stateCode) {
    params.set('state_code', stateCode)
  }

  if (county) {
    params.set('county', county)
  }

  if (countyGeoid) {
    params.set('county_geoid', countyGeoid)
  }

  if (zipCode) {
    params.set('zip_code', zipCode)
  }

  if (radiusMiles !== undefined) {
    params.set('radius_miles', String(radiusMiles))
  }

  const query = params.toString()
  const url = `/api/supervisors${query ? `?${query}` : ''}`

  const response = await fetch(url)

  if (!response.ok) {
    const error = await response.json().catch(() => null)

    throw new Error(
      typeof error?.detail === 'string'
        ? error.detail
        : 'Unable to load supervisors'
    )
  }

  return response.json()
}
