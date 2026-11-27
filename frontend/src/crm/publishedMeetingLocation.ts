export function getPublishedMeetingLocation(
  additionalInfo?: string | null,
): string {
  if (!additionalInfo) return ''

  const text = additionalInfo
    .split('\n')
    .filter(line =>
      !/^(Published rates|Intake fee):/i.test(line)
    )
    .join(' ')

  const locations: string[] = []

  if (/\bon[-\s]?site\b/i.test(text)) {
    locations.push('On-site')
  }

  if (/\boff[-\s]?site\b/i.test(text)) {
    locations.push('Off-site')
  }

  if (
    /\bhome visits?\b/i.test(text) &&
    !/\bno home visits?\b/i.test(text)
  ) {
    locations.push('Home visits')
  }

  return locations.join(', ')
}
