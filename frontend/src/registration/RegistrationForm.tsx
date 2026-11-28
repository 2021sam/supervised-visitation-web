import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import {
  fetchProfile,
  saveProfile,
} from '../api/registration'
import type { Profile, ProfileValue } from '../api/registration'
import {
  requiredFields,
  preferredFields,
  booleanFields,
} from './fields'
import ProfilePhoto from './ProfilePhoto'
import './RegistrationForm.css'

export default function RegistrationForm() {
  const [values, setValues] = useState<Profile>({})
  const [photo, setPhoto] = useState<string | null>(null)
  const [profileSaved, setProfileSaved] = useState(false)
  const [accountEmail, setAccountEmail] = useState('')
  const [matchedName, setMatchedName] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    let active = true

    fetchProfile()
      .then((data) => {
        if (!active) return

        const source = data.profile ?? data.prefill ?? {}
        const initial: Profile = {}

        for (const [field] of [
          ...requiredFields,
          ...preferredFields,
          ...booleanFields,
        ]) {
          initial[field] = source[field] ?? null
        }

        for (const field of [
          'provider_type',
          'business_name',
          'additional_info',
          'price_per_mile',
          'driving_hourly_rate',
          'calendar_visibility',
        ]) {
          initial[field] = source[field] ?? null
        }

        for (const field of [
          'price_per_mile',
          'driving_hourly_rate',
        ]) {
          initial[field] = initial[field] == null
            ? null
            : Number(initial[field]) / 1000
        }

        initial.calendar_visibility ??= 'public'

        setValues(initial)
        setPhoto(
          typeof data.profile?.profile_photo === 'string'
            ? data.profile.profile_photo
            : null
        )
        setProfileSaved(data.profile !== null)
        setAccountEmail(data.account_email)
        setMatchedName(String(data.prefill?.name ?? ''))
      })
      .catch((err: Error) => {
        if (active) setError(err.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => { active = false }
  }, [])

  function update(field: string, value: ProfileValue) {
    setValues((previous) => ({
      ...previous,
      [field]: value,
    }))
    setMessage('')
  }

  async function handleSave(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setMessage('')

    try {
      const payload = { ...values }

      for (const field of [
        'price_per_mile',
        'driving_hourly_rate',
      ]) {
        const value = values[field]

        payload[field] = value === null || value === ''
          ? null
          : Math.round(Number(value) * 1000)
      }

      await saveProfile(payload)
      setProfileSaved(true)
      setMessage('Your profile has been saved.')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  function textField(
    field: string,
    label: string,
    required = false,
  ) {
    return (
      <label key={field}>
        {label}{required && ' *'}
        <input
          value={String(values[field] ?? '')}
          required={required}
          onChange={(event) =>
            update(field, event.target.value || null)
          }
        />
      </label>
    )
  }

  if (loading) return <p>Loading your profile...</p>

  if (!accountEmail) {
    return <p role="alert">{error}</p>
  }

  return (
    <form className="registration-form" onSubmit={handleSave}>
      <h2>Provider registration</h2>

      <ProfilePhoto
        photo={photo}
        profileSaved={profileSaved}
        onChange={setPhoto}
      />

      {matchedName && (
        <p>Existing directory listing found: {matchedName}</p>
      )}

      <fieldset className="registration-required">
        <legend>Required information</legend>

        <label>
          Verified account email
          <input value={accountEmail} readOnly />
        </label>

        <label>
          Provider type *
          <select
            required
            value={String(values.provider_type ?? '')}
            onChange={(event) =>
              update('provider_type', event.target.value || null)
            }
          >
            <option value="">Select provider type</option>
            <option value="individual">Individual</option>
            <option value="agency">Agency</option>
          </select>
        </label>

        {requiredFields.map(([field, label]) =>
          textField(field, label, true)
        )}

        {values.provider_type === 'agency' &&
          textField('business_name', 'Business name', true)}
      </fieldset>

      <fieldset>
        <legend>Preferred information</legend>

        {preferredFields.map(([field, label]) =>
          textField(field, label)
        )}

        <small>
          Use a nearby public landmark, shopping center or
          intersection as your reference point, rather than
          your private home address.
        </small>

        <label>
          Calendar link visibility
          <select
            value={String(values.calendar_visibility ?? 'public')}
            onChange={(event) =>
              update('calendar_visibility', event.target.value)
            }
          >
            <option value="public">Public</option>
            <option value="verified">Verified users only</option>
            <option value="hidden">Hidden</option>
          </select>
        </label>

        <label>
          Additional information
          <textarea
            rows={4}
            value={String(values.additional_info ?? '')}
            onChange={(event) =>
              update('additional_info', event.target.value || null)
            }
          />
        </label>
      </fieldset>

      <fieldset>
        <legend>Travel charges</legend>

        {[
          ['price_per_mile', 'Price per mile ($)'],
          ['driving_hourly_rate', 'Driving hourly rate ($)'],
        ].map(([field, label]) => (
          <label key={field}>
            {label}
            <input
              type="number"
              min="0"
              step="0.001"
              value={String(values[field] ?? '')}
              onChange={(event) =>
                update(field, event.target.value || null)
              }
            />
          </label>
        ))}

        <small>
          Leave blank if unspecified. Enter 0 for no charge.
        </small>

        {[
          ['charges_roundtrip_mileage', 'Charge round-trip mileage'],
          ['charges_roundtrip_driving_time', 'Charge round-trip driving time'],
        ].map(([field, label]) => (
          <label key={field}>
            {label}
            <select
              value={String(values[field] ?? '')}
              onChange={(event) =>
                update(field, event.target.value === ''
                  ? null
                  : Number(event.target.value))
              }
            >
              <option value="">Not specified</option>
              <option value="1">Yes</option>
              <option value="0">No</option>
            </select>
          </label>
        ))}
      </fieldset>

      <details>
        <summary>Services and contact preferences</summary>

        {booleanFields.filter(([field]) =>
          field !== 'charges_roundtrip_mileage' &&
          field !== 'charges_roundtrip_driving_time'
        ).map(([field, label]) => (
          <label key={field}>
            {label}
            <select
              value={String(values[field] ?? '')}
              onChange={(event) =>
                update(
                  field,
                  event.target.value === ''
                    ? null
                    : Number(event.target.value),
                )
              }
            >
              <option value="">Not specified</option>
              <option value="1">Yes</option>
              <option value="0">No</option>
            </select>
          </label>
        ))}
      </details>

      <button type="submit" disabled={busy}>
        {busy ? 'Saving...' : 'Save Profile'}
      </button>

      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}
    </form>
  )
}
