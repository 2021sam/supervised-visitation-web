interface Props {
  value: string
}

export default function EmailLink({ value }: Props) {
  if (!value.trim()) return <>—</>

  const pattern =
    /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g

  const parts = []
  let cursor = 0

  for (const match of value.matchAll(pattern)) {
    const start = match.index
    const email = match[0]

    parts.push(value.slice(cursor, start))

    parts.push(
      <a
        key={start}
        href={`mailto:${encodeURIComponent(email).replace('%40', '@')}`}
        className="contact-link"
      >
        {email}
      </a>,
    )

    cursor = start + email.length
  }

  parts.push(value.slice(cursor))

  return <>{parts}</>
}
