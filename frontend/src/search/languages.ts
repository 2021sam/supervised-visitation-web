import type { Supervisor } from '../types/supervisor'

export function parseLanguages(
  value?: string | null,
): string[] {
  return (value ?? '')
    .split(/[,;/&▪•]+|\s+and\s+/i)
    .flatMap(language =>
      language.trim().split(/\s+(?=Farsi$|Tagalog$)/i)
    )
    .map(language => {
      const value = language.trim()

      switch (value.toLowerCase()) {
        case 'geman':
          return 'German'
        case 'limited mandarin capacity':
          return 'Mandarin'
        case 'other languages with an interpreter (upon request)':
          return ''
        default:
          return value
      }
    })
    .filter(Boolean)
}

export function getAvailableLanguages(
  supervisors: Supervisor[],
): string[] {
  const languages = new Map<string, string>([['english', 'English']])

  for (const supervisor of supervisors) {
    for (const language of parseLanguages(supervisor.languages)) {
      const key = language.toLowerCase()

      if (!languages.has(key)) {
        languages.set(key, language)
      }
    }
  }

  return [...languages.values()].sort(
    (a, b) =>
      a === 'English' ? -1 :
      b === 'English' ? 1 :
      a.localeCompare(b),
  )
}

export function filterByLanguages(
  supervisors: Supervisor[],
  selectedLanguages: string[],
): Supervisor[] {
  if (selectedLanguages.length === 0) return supervisors

  const required = selectedLanguages.map(
    language => language.toLowerCase(),
  )

  return supervisors.filter(supervisor => {
    const available = new Set(
      parseLanguages(supervisor.languages).map(
        language => language.toLowerCase(),
      ),
    )

    if (available.size === 0) {
      available.add('english')
    }

    return required.every(language => available.has(language))
  })
}
