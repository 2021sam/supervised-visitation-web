export function getPublishedHourlyRate(
  additionalInfo?: string | null,
): number | null {
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
    /\$(\d+(?:\.\d{1,2})?)(?:\s*[-–—]\s*\$?\d+(?:\.\d{1,2})?)?\s*\+?\s*\(?\s*(?:per\s*\/?\s*|\/\s*)(?:hour|hr)\b/gi

  const rates: number[] = []

  for (const match of text.matchAll(pattern)) {
    const after = text.slice(
      match.index + match[0].length,
    )

    // Exclude monitored calls and other non-visit rates.
    if (/^\s*(?:monitored calls?|phone calls?|telephone calls?|court reports?)/i.test(after)) {
      continue
    }

    rates.push(Number(match[1]))
  }

  return rates.length > 0
    ? Math.min(...rates)
    : null
}
