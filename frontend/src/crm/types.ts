export type ContactStatus =
  | 'not_contacted'
  | 'no_answer'
  | 'voicemail'
  | 'email_sent'
  | 'awaiting_response'
  | 'available'
  | 'unavailable'
  | 'hired'

export type Weekday =
  | 'monday'
  | 'tuesday'
  | 'wednesday'
  | 'thursday'
  | 'friday'
  | 'saturday'
  | 'sunday'

export interface TimeRange {
  start: string
  end: string
}

export type WeeklyAvailability = Partial<Record<Weekday, TimeRange>>

export interface CRMEntry {
  status: ContactStatus
  hourlyQuote: number | null
  transportsChild?: boolean | null
  meetingLocation?: string
  locationFee?: number | null
  availability?: WeeklyAvailability
  notes: string
  updatedAt: string
}

export type CRMRecords = Record<string, Partial<CRMEntry>>

export function createCRMEntry(): CRMEntry {
  return {
    status: 'not_contacted',
    hourlyQuote: null,
    transportsChild: null,
    meetingLocation: '',
    locationFee: null,
    availability: {},
    notes: '',
    updatedAt: '',
  }
}
