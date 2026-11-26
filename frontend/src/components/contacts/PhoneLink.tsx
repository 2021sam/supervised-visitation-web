interface Props {
  value: string
}

export default function PhoneLink({ value }: Props) {
  if (!value.trim()) return <>—</>

  const pattern =
    /(?<!\d)(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]?\d{3}[ .-]?\d{4}(?!\d)(?:\s*(?:ext\.?|x)\s*\d+)?/gi

  const parts = []
  let cursor = 0

  for (const match of value.matchAll(pattern)) {
    const start = match.index
    const original = match[0]

    parts.push(value.slice(cursor, start))

    const extension = original.match(
      /(?:ext\.?|x)\s*(\d+)$/i,
    )

    const number = extension
      ? original.slice(0, extension.index)
      : original

    const digits = number.replace(/\D/g, '')

    const normalized =
      digits.length === 10 ? `+1${digits}` : `+${digits}`

    const href = extension
      ? `tel:${normalized};ext=${extension[1]}`
      : `tel:${normalized}`

    parts.push(
      <a key={start} href={href} className="contact-link">
        {original}
      </a>,
    )

    cursor = start + original.length
  }

  parts.push(value.slice(cursor))

  return <>{parts}</>
}
