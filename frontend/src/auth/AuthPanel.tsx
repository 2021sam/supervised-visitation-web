import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import {
  fetchSession,
  requestSignIn,
  verifyEmail,
  signOut,
} from '../api/auth'
import type { AuthSession } from '../api/auth'
import './AuthPanel.css'

export default function AuthPanel() {
  const [session, setSession] = useState<AuthSession | null>(null)
  const [email, setEmail] = useState('')
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const [token, setToken] = useState(() =>
    window.location.pathname === '/verify'
      ? new URLSearchParams(
          window.location.hash.slice(1),
        ).get('token') || ''
      : '',
  )

  useEffect(() => {
    let active = true

    fetchSession()
      .then((data) => {
        if (active) setSession(data)
      })
      .catch(() => {
        if (active) setSession({
          authenticated: false,
          email: null,
        })
      })

    return () => { active = false }
  }, [])

  useEffect(() => {
    if (token) {
      window.history.replaceState(null, '', '/verify')
    }
  }, [token])

  async function handleRequest(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setMessage('')

    try {
      const result = await requestSignIn(email.trim())
      setMessage(result.message)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function handleVerify() {
    setBusy(true)
    setError('')

    try {
      const result = await verifyEmail(token)
      setSession(result)
      setToken('')
      setOpen(false)
      window.history.replaceState(null, '', '/')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function handleLogout() {
    setBusy(true)
    setError('')

    try {
      await signOut()
      setSession({ authenticated: false, email: null })
      setMessage('')
      setEmail('')
      setOpen(false)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="auth-panel">
      {token ? (
        <div className="auth-form">
          <h2>Confirm sign-in</h2>
          <p>Continue to verify your email and sign in.</p>
          <button
            disabled={busy}
            onClick={handleVerify}
          >
            {busy ? 'Verifying...' : 'Confirm sign-in'}
          </button>
          <button
            disabled={busy}
            onClick={() => {
              setToken('')
              setError('')
              setOpen(true)
              window.history.replaceState(null, '', '/')
            }}
          >
            Request a new link
          </button>
        </div>
      ) : session?.authenticated ? (
        <div className="auth-toolbar">
          <span>{session.email}</span>
          <button disabled={busy} onClick={handleLogout}>
            Sign out
          </button>
        </div>
      ) : (
        <>
          <div className="auth-toolbar">
            <button onClick={() => setOpen(!open)}>
              {open ? 'Close' : 'Sign in / Register'}
            </button>
          </div>

          {open && (
            <form
              className="auth-form"
              onSubmit={handleRequest}
            >
              <h2>Sign in or register</h2>
              <p>No password required.</p>

              <label htmlFor="auth-email">
                Email address
              </label>

              <input
                id="auth-email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                maxLength={254}
                required
              />

              <button type="submit" disabled={busy}>
                {busy ? 'Please wait...' : 'Continue with email'}
              </button>

              <small>
                We'll send you a secure sign-in link.
              </small>

              {message && <p role="status">{message}</p>}
            </form>
          )}
        </>
      )}

      {error && <p role="alert">{error}</p>}
    </section>
  )
}
