import { useState } from 'react'
import { changePublication } from '../api/registration'
import type { PublicationAction } from '../api/registration'

interface Props {
  status: string
  disabled: boolean
  onChange: (status: string) => void
}

export default function PublicationActions({
  status,
  disabled,
  onChange,
}: Props) {
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function run(action: PublicationAction) {
    if (action === 'delete' &&
        !window.confirm('Permanently remove your directory listing?')) {
      return
    }

    setBusy(true)
    setMessage('')
    setError('')

    try {
      const result = await changePublication(action)
      onChange(String(result.profile?.status ?? status))

      setMessage({
        publish: 'Your profile has been published.',
        hide: 'Your profile is now hidden.',
        delete: 'Your directory listing has been deleted.',
      }[action])
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <fieldset>
      <legend>Directory listing</legend>

      <p>Status: {{
        active: 'Published',
        hidden: 'Not published',
        deleted: 'Deleted',
      }[status] ?? 'Not published'}</p>

      {status !== 'deleted' && (
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.75rem',
        }}>
          {status !== 'active' && (
            <button
              type="button"
              disabled={disabled || busy}
              onClick={() => run('publish')}
            >
              Publish Profile
            </button>
          )}

          {status === 'active' && (
            <button
              type="button"
              disabled={disabled || busy}
              onClick={() => run('hide')}
            >
              Hide Profile
            </button>
          )}

          <button
            type="button"
            disabled={disabled || busy}
            onClick={() => run('delete')}
          >
            Delete Profile
          </button>
        </div>
      )}

      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}
    </fieldset>
  )
}
