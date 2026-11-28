interface Props {
  hidden: boolean
  onToggle: () => void
}

export default function ProviderVisibility({
  hidden,
  onToggle,
}: Props) {
  const label = hidden ? 'Restore provider' : 'Hide provider'

  return (
    <button
      type="button"
      className="provider-visibility"
      aria-label={label}
      title={label}
      onClick={onToggle}
    >
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
        <circle cx="12" cy="12" r="3" />
        {hidden && <path d="M3 3l18 18" />}
      </svg>
    </button>
  )
}
