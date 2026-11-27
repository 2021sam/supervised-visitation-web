export function getPublishedTransportation(
  additionalInfo?: string | null,
): boolean | null {
  const services = additionalInfo
    ?.split('\n')
    .find(line => /^Services:/i.test(line))

  if (!services) return null

  if (/\b(?:no transportation|no transport|does not transport|transportation not offered)\b/i.test(services)) {
    return false
  }

  if (/\b(?:minor transport(?:ation)?|child transport(?:ation)?|transportation|transporting children)\b/i.test(services)) {
    return true
  }

  return null
}
