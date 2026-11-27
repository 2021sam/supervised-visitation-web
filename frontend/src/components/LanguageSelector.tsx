interface Props {
  languages: string[]
  selectedLanguage: string
  onChange: (language: string) => void
}

export default function LanguageSelector({
  languages,
  selectedLanguage,
  onChange,
}: Props) {
  return (
    <label>
      Language:{' '}
      <select
        value={selectedLanguage}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">All languages</option>

        {languages.map((language) => (
          <option key={language} value={language}>
            {language}
          </option>
        ))}
      </select>
    </label>
  )
}
