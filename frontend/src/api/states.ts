import type { StateResponse } from '../types/state'

export async function fetchStates(): Promise<StateResponse> {
  const response = await fetch('/api/states')

  if (!response.ok) {
    throw new Error(`States API error: ${response.status}`)
  }

  return response.json()
}
