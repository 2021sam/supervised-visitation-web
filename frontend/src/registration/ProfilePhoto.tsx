import { useState } from 'react'

interface Props {
  photo: string | null
  profileSaved: boolean
  onChange: (photo: string | null) => void
}

export default function ProfilePhoto({
  photo,
  profileSaved,
  onChange,
}: Props) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function changePhoto(file?: File) {
    setError('')

    if (file && file.size > 5 * 1024 * 1024) {
      setError('Maximum photo size is 5 MB.')
      return
    }

    setBusy(true)

    try {
      const response = await fetch('/api/registration/photo', {
        method: file ? 'PUT' : 'DELETE',
        credentials: 'same-origin',
        cache: 'no-store',
        headers: file
          ? { 'Content-Type': 'application/octet-stream' }
          : undefined,
        body: file,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Unable to update photo.',
        )
      }

      onChange(data.profile_photo)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <fieldset>
      <legend>Profile photo</legend>

      <div className="profile-photo-controls">
        {photo ? (
          <img
            className="profile-photo-preview"
            src={photo}
            alt="Your profile photo"
          />
        ) : (
          <div className="profile-photo-placeholder">
            No photo
          </div>
        )}

        <div>
          <label>
            {photo ? 'Replace Photo' : 'Upload Photo'}
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              disabled={busy || !profileSaved}
              onChange={(event) => {
                const file = event.target.files?.[0]
                if (file) void changePhoto(file)
                event.target.value = ''
              }}
            />
          </label>

          {photo && (
            <button
              type="button"
              disabled={busy}
              onClick={() => void changePhoto()}
            >
              Remove Photo
            </button>
          )}

          <small>JPEG, PNG or WebP. Maximum 5 MB.</small>

          {!profileSaved && (
            <p>Save your profile to enable photo uploads.</p>
          )}

          {busy && <p role="status">Updating photo...</p>}
          {error && <p role="alert">{error}</p>}
        </div>
      </div>
    </fieldset>
  )
}
