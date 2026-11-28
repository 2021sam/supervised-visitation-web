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
import { fetchCounties } from '../api/counties'
import { fetchStates } from '../api/states'
import type { State } from '../types/state'
import type { County } from '../types/county'
import ProfilePhoto from './ProfilePhoto'
import PublicationActions from './PublicationActions'
import './RegistrationForm.css'

export default function RegistrationForm() {
  const [values, setValues] = useState<Profile>({})
  const [counties, setCounties] = useState<County[]>([])
  const [states, setStates] = useState<State[]>([])
  const [photo, setPhoto] = useState<string | null>(null)
  const [profileSaved, setProfileSaved] = useState(false)
  const [profileStatus, setProfileStatus] = useState('hidden')
  const [dirty, setDirty] = useState(false)
  const [accountEmail, setAccountEmail] = useState('')
  const [matchedName, setMatchedName] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    let active = true

    fetchStates()
      .then((data) => {
        if (active) setStates(data.states)
      })
      .catch((err: Error) => {
        if (active) setError(err.message)
      })

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

        initial.state_code = source.state_code || 'CA'
        initial.county = source.county ?? null
        initial.service_counties = source.service_counties ?? null
        initial.calendar_visibility ??= 'public'

        setValues(initial)
        setPhoto(
          typeof data.profile?.profile_photo === 'string'
            ? data.profile.profile_photo
            : null
        )
        setProfileSaved(data.profile !== null)
        setProfileStatus(String(data.profile?.status ?? 'hidden'))
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

  const stateCode = String(values.state_code ?? '')

  useEffect(() => {
    let active = true

    if (stateCode) {
      fetchCounties(stateCode)
        .then((data) => {
          if (active) setCounties(data.counties)
        })
        .catch((err: Error) => {
          if (active) setError(err.message)
        })
    }

    return () => { active = false }
  }, [stateCode])

  const selectedCounties = [...new Set([
    String(values.county ?? ''),
    ...String(values.service_counties ?? '').split(','),
  ].map((name) => name.trim()).filter(Boolean))]

  function update(field: string, value: ProfileValue) {
    setDirty(true)
    setValues((previous) => ({
      ...previous,
      [field]: value,
    }))
    setMessage('')
  }

  async function handleSave(event: FormEvent) {
    event.preventDefault()

    if (!selectedCounties.length) {
      setError('Please select at least one county.')
      return
    }

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

      const result = await saveProfile(payload)
      setProfileSaved(true)
      setProfileStatus(String(result.profile?.status ?? 'hidden'))
      setDirty(false)
      setMessage('Your profile has been saved.')

      if (result.publication_success === false) {
        setError(
          'Your changes were saved, but the directory could not be updated. Please save again to retry.'
        )
      }
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

  if (profileStatus === 'deleted') {
    return <p>Your directory listing has been deleted.</p>
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

        <label>
          State *
          <select
            required
            value={stateCode}
            onChange={(event) => {
              setCounties([])
              update('state_code', event.target.value || null)
              update('county', null)
              update('service_counties', null)
            }}
          >
            <option value="">Select state</option>
            {states.map((state) => (
              <option
                key={state.state_code}
                value={state.state_code}
              >
                {state.state_name}
              </option>
            ))}
          </select>
        </label>

        <details>
          <summary>
            Counties served * ({selectedCounties.length} selected)
          </summary>

          <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
            {counties.map((county) => (
              <label
                key={county.geoid}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <input
                  type="checkbox"
                  style={{ width: 'auto' }}
                  checked={selectedCounties.includes(county.county_name)}
                  onChange={(event) => {
                    const next = event.target.checked
                      ? [...selectedCounties, county.county_name]
                      : selectedCounties.filter(
                          (name) => name !== county.county_name
                        )

                    update('county', next[0] ?? null)
                    update('service_counties', next.join(', ') || null)
                  }}
                />
                {county.county_name}
              </label>
            ))}
          </div>
        </details>

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

      {profileSaved && (
        <>
          {dirty && (
            <p>Save your changes before updating your listing status.</p>
          )}

          <PublicationActions
            status={profileStatus}
            disabled={busy || dirty}
            onChange={setProfileStatus}
          />
        </>
      )}

      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}
    </form>
  )
}
