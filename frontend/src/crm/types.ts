export type ContactStatus =
  | 'not_contacted'
  | 'no_answer'
  | 'voicemail'
  | 'email_sent'
  | 'awaiting_response'
  | 'available'
  | 'unavailable'
  | 'hired'

export interface CRMEntry {
  status: ContactStatus
  hourlyQuote: number | null
  transportsChild?: boolean | null
  notes: string
  updatedAt: string
}

export type CRMRecords = Record<string, CRMEntry>

export function createCRMEntry(): CRMEntry {
  return {
    status: 'not_contacted',
    hourlyQuote: null,
    transportsChild: null,
    notes: '',
    updatedAt: '',
  }
}
