import type { SortConfig, SortField } from '../crm/sorting'

interface Props {
  label: string
  field: SortField
  sort: SortConfig
  onSort: (field: SortField) => void
  title?: string
}

export default function SortableHeader({
  label,
  field,
  sort,
  onSort,
  title,
}: Props) {
  const active = sort.field === field

  return (
    <th
      scope="col"
      title={title}
      aria-sort={
        active
          ? sort.direction === 'asc'
            ? 'ascending'
            : 'descending'
          : undefined
      }
    >
      <button
        type="button"
        className="sortable-header"
        onClick={() => onSort(field)}
      >
        {label}
        <span aria-hidden="true">
          {active
            ? sort.direction === 'asc'
              ? ' ↑'
              : ' ↓'
            : ' ↕'}
        </span>
      </button>
    </th>
  )
}
