import type { Supervisor } from '../types/supervisor'
import PhoneLink from './contacts/PhoneLink'
import EmailLink from './contacts/EmailLink'
import WebsiteLink from './contacts/WebsiteLink'

interface Props {
  supervisor: Supervisor
}

export default function ProviderContact({ supervisor }: Props) {
  return (
    <div className="provider-contact">
      {supervisor.phone?.trim() && (
        <div className="contact-row">
          <svg viewBox="0 0 24 24" aria-label="Phone" role="img">
            <path d="M22 16.9v3a2 2 0 0 1-2.2 2
              19.8 19.8 0 0 1-8.6-3.1
              19.5 19.5 0 0 1-6-6
              19.8 19.8 0 0 1-3.1-8.7
              A2 2 0 0 1 4.1 2h3
              a2 2 0 0 1 2 1.7
              c.1 1 .4 1.9.7 2.8
              a2 2 0 0 1-.5 2.1L8 9.9
              a16 16 0 0 0 6 6l1.3-1.3
              a2 2 0 0 1 2.1-.5
              c.9.3 1.8.6 2.8.7
              a2 2 0 0 1 1.8 2.1Z" />
          </svg>
          <span><PhoneLink value={supervisor.phone} /></span>
        </div>
      )}

      {supervisor.email?.trim() && (
        <div className="contact-row">
          <svg viewBox="0 0 24 24" aria-label="Email" role="img">
            <rect x="2" y="4" width="20" height="16" rx="2" />
            <path d="m2 6 10 7L22 6" />
          </svg>
          <span><EmailLink value={supervisor.email} /></span>
        </div>
      )}

      {supervisor.website?.trim() && (
        <div className="contact-row">
          <svg viewBox="0 0 24 24" aria-label="Website" role="img">
            <circle cx="12" cy="12" r="10" />
            <ellipse cx="12" cy="12" rx="4" ry="10" />
            <path d="M2 12h20" />
          </svg>
          <span><WebsiteLink value={supervisor.website} /></span>
        </div>
      )}
    </div>
  )
}
