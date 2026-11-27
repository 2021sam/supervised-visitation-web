import type { Supervisor } from '../types/supervisor'

export function parseLanguages(
  value?: string | null,
): string[] {
  return (value ?? '')
    .split(',')
    .map((language) => language.trim())
    .filter(Boolean)
}

export function getAvailableLanguages(
  supervisors: Supervisor[],
): string[] {
  const languages = new Map<string, string>()

  for (const supervisor of supervisors) {
    for (const language of parseLanguages(supervisor.languages)) {
      languages.set(language.toLowerCase(), language)
    }
  }

  return [...languages.values()].sort(
    (a, b) => a.localeCompare(b),
  )
}

export function filterByLanguage(
  supervisors: Supervisor[],
  selectedLanguage: string,
): Supervisor[] {
  if (!selectedLanguage) return supervisors

  const target = selectedLanguage.toLowerCase()

  return supervisors.filter((supervisor) =>
    parseLanguages(supervisor.languages).some(
      (language) => language.toLowerCase() === target,
    ),
  )
}
