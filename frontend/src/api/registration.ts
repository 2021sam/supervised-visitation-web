export type ProfileValue = string | number | null
export type Profile = Record<string, ProfileValue>

export interface RegistrationResponse {
  account_email: string
  profile: Profile | null
  prefill?: Profile | null
  publication_success?: boolean | null
}

async function request(values?: Profile): Promise<RegistrationResponse> {
  const response = await fetch('/api/registration/profile', {
    method: values ? 'PATCH' : 'GET',
    credentials: 'same-origin',
    cache: 'no-store',
    headers: { 'Content-Type': 'application/json' },
    body: values ? JSON.stringify(values) : undefined,
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      typeof data.detail === 'string'
        ? data.detail
        : 'Unable to load or save your profile.',
    )
  }

  return data
}

export const fetchProfile = () => request()
export const saveProfile = (values: Profile) => request(values)

export type PublicationAction = 'publish' | 'hide' | 'delete'

export async function changePublication(
  action: PublicationAction,
): Promise<RegistrationResponse> {
  const response = await fetch('/api/registration/profile/action', {
    method: 'POST',
    credentials: 'same-origin',
    cache: 'no-store',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      typeof data.detail === 'string'
        ? data.detail
        : 'Unable to update your listing.',
    )
  }

  return data
}
