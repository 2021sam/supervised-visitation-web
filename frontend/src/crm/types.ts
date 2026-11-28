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
  hidden?: boolean
  status: ContactStatus
  hourlyQuote: string | number | null
  transportsChild?: boolean | null
  meetingLocation?: string
  locationFee?: number | null
  hours?: number | null
  availability?: WeeklyAvailability
  notes: string
  updatedAt: string
}

export type CRMRecords = Record<string, Partial<CRMEntry>>

export function createCRMEntry(): CRMEntry {
  return {
    hidden: false,
    status: 'not_contacted',
    hourlyQuote: null,
    transportsChild: null,
    meetingLocation: '',
    locationFee: null,
    hours: 2,
    availability: {},
    notes: '',
    updatedAt: '',
  }
}
