export interface AuthSession {
  authenticated: boolean
  email: string | null
}

async function authRequest<T>(
  endpoint: string,
  body?: object,
  method = 'POST',
): Promise<T> {
  const response = await fetch(`/api/auth/${endpoint}`, {
    method,
    credentials: 'same-origin',
    cache: 'no-store',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      typeof data.detail === 'string'
        ? data.detail
        : 'Unable to complete your request.',
    )
  }

  return data as T
}

export function requestSignIn(email: string) {
  return authRequest<{ message: string }>('request', { email })
}

export function verifyEmail(token: string) {
  return authRequest<AuthSession>('verify', { token })
}

export function fetchSession() {
  return authRequest<AuthSession>('session', undefined, 'GET')
}

export function signOut() {
  return authRequest<{ authenticated: boolean }>('logout')
}
