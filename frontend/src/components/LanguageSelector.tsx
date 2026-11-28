interface Props {
  languages: string[]
  open: boolean
  onToggle: () => void
  panel?: boolean
  selectedLanguages: string[]
  onChange: (languages: string[]) => void
}

export default function LanguageSelector({
  languages,
  open,
  onToggle,
  panel = false,
  selectedLanguages,
  onChange,
}: Props) {

  function toggleLanguage(language: string) {
    onChange(
      selectedLanguages.includes(language)
        ? selectedLanguages.filter(value => value !== language)
        : [...selectedLanguages, language],
    )
  }

  return (
    <div className="language-filter">
      {!panel && <button
        type="button"
        className={
          selectedLanguages.length
            ? 'language-filter-toggle active'
            : 'language-filter-toggle'
        }
        title="Filter languages"
        aria-label="Filter languages"
        aria-expanded={open}
        onClick={onToggle}
      >
        <svg width="16" height="16" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" strokeWidth="1.8"
          strokeLinecap="round" strokeLinejoin="round"
          aria-hidden="true">
          <path d="M3 4h18l-7 8v6l-4 2v-8Z" />
        </svg>
        {selectedLanguages.length > 0 && (
          <span>{selectedLanguages.length}</span>
        )}
      </button>}

      {panel && open && (
        <div className="language-filter-menu">
          <strong>Required languages</strong>

          <div className="language-filter-options">
            {languages.map(language => (
              <label key={language}>
                <input
                  type="checkbox"
                  checked={selectedLanguages.includes(language)}
                  onChange={() => toggleLanguage(language)}
                />
                {language}
              </label>
            ))}
          </div>

          <div className="language-filter-actions">
            <button type="button" onClick={() => onChange([])}>
              Clear
            </button>
            <button type="button" onClick={onToggle}>
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
