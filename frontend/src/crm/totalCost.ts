import type { CRMEntry } from './types'

export function calculateTotal(entry: CRMEntry): number | null {
  const rate = String(entry.hourlyQuote ?? '').trim()
  const hours = entry.hours
  const locationFee = entry.locationFee ?? 0

  if (!/^\$?\d+(?:\.\d{1,2})?$/.test(rate)) {
    return null
  }

  if (hours == null || !Number.isFinite(hours) || hours <= 0) {
    return null
  }

  if (!Number.isFinite(locationFee) || locationFee < 0) {
    return null
  }

  const total = Number(rate.replace('$', '')) * hours + locationFee

  return Number.isFinite(total)
    ? Math.round(total * 100) / 100
    : null
}
