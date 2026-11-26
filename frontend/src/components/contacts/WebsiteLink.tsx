interface Props {
  value: string
}

function normalizeWebsite(value: string): string | null {
  const candidate = /^https?:\/\//i.test(value)
    ? value
    : `https://${value}`

  try {
    const url = new URL(candidate)

    if (
      !['http:', 'https:'].includes(url.protocol) ||
      !/\.[a-z]{2,}$/i.test(url.hostname) ||
      url.username ||
      url.password
    ) {
      return null
    }

    return url.href
  } catch {
    return null
  }
}

export default function WebsiteLink({ value }: Props) {
  if (!value.trim()) return <>—</>

  const parts = value.split(/([;\s]+)/)

  return (
    <>
      {parts.map((part, index) => {
        const href = normalizeWebsite(part)

        if (!href) return part

        return (
          <a
            key={index}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="contact-link"
          >
            {part}
          </a>
        )
      })}
    </>
  )
}
