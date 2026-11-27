import type { Supervisor } from '../types/supervisor'
import type { CRMEntry } from './types'
import { createCRMEntry } from './types'
import { getPublishedHourlyRate } from './publishedHourlyRate'


import { getPublishedTransportation } from './publishedTransportation'

import { getPublishedMeetingLocation } from './publishedMeetingLocation'

export function getEffectiveEntry(
  supervisor: Supervisor,
  savedEntry?: Partial<CRMEntry>,
): CRMEntry {
  return {
    ...createCRMEntry(),
    hourlyQuote: getPublishedHourlyRate(
      supervisor.additional_info,
    ),
    transportsChild: getPublishedTransportation(
      supervisor.additional_info,
    ),
    meetingLocation: getPublishedMeetingLocation(
      supervisor.additional_info,
    ),
    ...savedEntry,
  }
}
