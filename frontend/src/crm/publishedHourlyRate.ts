export function getPublishedHourlyRate(
  additionalInfo?: string | null,
): string | number | null {
  const line = additionalInfo
    ?.split('\n')
    .find((line) => /^Published rates:/i.test(line))

  if (!line) return null

  const text = line
    .replace(/^Published rates:\s*/i, '')
    .trim()

  if (/^\$?0(?:\.00)?$|^free$/i.test(text)) {
    return 0
  }

  const pattern =
    /\$(\d+(?:\.\d{1,2})?)(?:\s*[-–—]\s*\$?(\d+(?:\.\d{1,2})?))?\s*(\+)?\s*\(?\s*(?:per\s*\/?\s*|\/\s*)(?:hour|hr)\b/gi

  for (const match of text.matchAll(pattern)) {
    const after = text.slice(
      match.index + match[0].length,
    )

    if (/^\s*(?:monitored calls?|phone calls?|telephone calls?|court reports?)/i.test(after)) {
      continue
    }

    const minimum = Number(match[1])

    if (/up to\s*$/i.test(text.slice(0, match.index))) {
      return `Up to ${minimum}`
    }

    if (match[2]) {
      return `${minimum}-${Number(match[2])}`
    }

    if (match[3] || /starting at\s*$/i.test(
      text.slice(0, match.index),
    )) {
      return `${minimum}+`
    }

    return minimum
  }

  const allServices = text.match(
    /^\$(\d+(?:\.\d{1,2})?)\s+for all services including intake and supervision\s*\/\s*hour$/i,
  )

  if (allServices) {
    return Number(allServices[1])
  }

  return null
}
