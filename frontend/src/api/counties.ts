import type { CountyResponse } from '../types/county'

export async function fetchCounties(
  stateCode: string,
): Promise<CountyResponse> {
  const params = new URLSearchParams({
    state_code: stateCode,
  })

  const response = await fetch(`/api/counties?${params}`)

  if (!response.ok) {
    throw new Error(`Counties API error: ${response.status}`)
  }

  return response.json()
}
