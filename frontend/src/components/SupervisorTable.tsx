import LanguageSelector from './LanguageSelector'
import SupervisorDetails from './SupervisorDetails'
import SupervisorZip from './SupervisorZip'
import ProviderContact from './ProviderContact'
import { Fragment, useState } from 'react'
import { sortSupervisors } from '../crm/sorting'
import type { SortConfig, SortField } from '../crm/sorting'
import SortableHeader from './SortableHeader'
import type { Supervisor } from '../types/supervisor'
import { useCRM } from '../crm/useCRM'
import { getEffectiveEntry } from '../crm/effectiveEntry'
import CRMFields from './CRMFields'
import CostCalculator from './CostCalculator'
import ProviderVisibility from './ProviderVisibility'
import './SupervisorTable.css'

interface Props {
  supervisors: Supervisor[]
  showDistance?: boolean
  languages: string[]
  selectedLanguages: string[]
  onLanguageChange: (languages: string[]) => void
}

export default function SupervisorTable({
  supervisors,
  showDistance = false,
  languages,
  selectedLanguages,
  onLanguageChange,
}: Props) {
  const { records, updateEntry, storageError } = useCRM()

  const [showHidden, setShowHidden] = useState(false)
  const [languageFilterOpen, setLanguageFilterOpen] = useState(false)

  const [openCalculator, setOpenCalculator] = useState<number | null>(null)

  const [sort, setSort] = useState<SortConfig>({
    field: showDistance ? 'distance' : 'name',
    direction: 'asc',
  })

  function handleSort(field: SortField) {
    setSort((previous) => ({
      field,
      direction:
        previous.field === field && previous.direction === 'asc'
          ? 'desc'
          : 'asc',
    }))
  }

  const hiddenSupervisors = supervisors.filter(
    supervisor => records[String(supervisor.supervisor_id)]?.hidden === true
  )

  const visibleSupervisors = showHidden
    ? supervisors
    : supervisors.filter(
        supervisor => records[String(supervisor.supervisor_id)]?.hidden !== true
      )

  function toggleVisibility(supervisorId: number) {
    const hidden = records[String(supervisorId)]?.hidden === true
    updateEntry(supervisorId, { hidden: !hidden })

    if (!hidden && openCalculator === supervisorId) {
      setOpenCalculator(null)
    }
  }

  function restoreAll() {
    hiddenSupervisors.forEach(supervisor =>
      updateEntry(supervisor.supervisor_id, { hidden: false })
    )
  }

  const sortedSupervisors = sortSupervisors(
    visibleSupervisors,
    records,
    sort,
  )

  if (supervisors.length === 0 && selectedLanguages.length === 0) {
    return <p>No supervisors found.</p>
  }

  return (
    <div className="supervisor-table-container">

      {storageError && (
        <p role="alert">
          Your changes could not be saved to browser storage.
        </p>
      )}

      <div className="visibility-toolbar">
        <strong>
          {supervisors.length - hiddenSupervisors.length} of {supervisors.length} providers
        </strong>

        <div className="visibility-controls">
          <span className="hidden-count">
            <svg width="18" height="18" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" strokeWidth="1.6"
              aria-hidden="true">
              <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
              <circle cx="12" cy="12" r="3" />
              <path d="M3 3l18 18" />
            </svg>
            {hiddenSupervisors.length} hidden
          </span>

          <label>
            <input
              type="checkbox"
              checked={showHidden}
              onChange={event => setShowHidden(event.target.checked)}
            />
            Show hidden
          </label>

          <button
            type="button"
            className="restore-providers"
            disabled={hiddenSupervisors.length === 0}
            onClick={restoreAll}
          >
            Restore all
          </button>
        </div>
      </div>

      <table className="supervisor-table">
        <thead>
          <tr>
            <SortableHeader
              label="Supervisor"
              field="name"
              sort={sort}
              onSort={handleSort}
            />
            <th scope="col">ZIP code</th>
            {showDistance && (
              <SortableHeader
                label="Distance (mi)"
                field="distance"
                sort={sort}
                onSort={handleSort}
                title="Approximate straight-line distance"
              />
            )}
            <th scope="col" className="contact-column">Contact</th>
            <SortableHeader
              label="Contact status"
              field="status"
              sort={sort}
              onSort={handleSort}
            />
            <SortableHeader
              label="Total ($)"
              field="totalCost"
              sort={sort}
              onSort={handleSort}
              title="Hourly rate × hours + location fee"
            />
            <th scope="col">Availability</th>
            <SortableHeader
              label="Transports child"
              field="transportsChild"
              sort={sort}
              onSort={handleSort}
            />
            <SortableHeader
              label="Languages"
              field="languages"
              sort={sort}
              onSort={handleSort}
              filter={
                <LanguageSelector
                  languages={languages}
                  selectedLanguages={selectedLanguages}
                  onChange={onLanguageChange}
                  open={languageFilterOpen}
                  onToggle={() => setLanguageFilterOpen(previous => !previous)}
                />
              }
            />
            <th scope="col">Notes</th>
          </tr>
        </thead>

        <tbody>
          {languageFilterOpen && (
            <tr className="language-filter-row">
              <td colSpan={showDistance ? 10 : 9}>
                <LanguageSelector
                  panel
                  languages={languages}
                  selectedLanguages={selectedLanguages}
                  onChange={onLanguageChange}
                  open={languageFilterOpen}
                  onToggle={() => setLanguageFilterOpen(false)}
                />
              </td>
            </tr>
          )}
          {sortedSupervisors.length === 0 && (
            <tr>
              <td colSpan={showDistance ? 10 : 9}>
                {supervisors.length === 0
                  ? 'No providers match the required languages. Adjust the language filter.'
                  : 'All providers in these results are hidden. Select Show hidden or restore them.'}
              </td>
            </tr>
          )}
          {sortedSupervisors.map((supervisor) => (
            <Fragment key={supervisor.supervisor_id}>
            <tr className={
              records[String(supervisor.supervisor_id)]?.hidden
                ? 'hidden-provider'
                : undefined
            }>
              <td>
                <div className="provider-name">
                  <span>{supervisor.name}</span>
                  <ProviderVisibility
                    hidden={records[String(supervisor.supervisor_id)]?.hidden === true}
                    onToggle={() => toggleVisibility(supervisor.supervisor_id)}
                  />
                </div>
                <SupervisorDetails supervisor={supervisor} />
              </td>
              <td><SupervisorZip supervisor={supervisor} /></td>
              {showDistance && (
                <td>
                  {supervisor.distance_miles == null
                    ? '—'
                    : supervisor.distance_miles.toFixed(1)}
                </td>
              )}
              <td><ProviderContact supervisor={supervisor} /></td>

              <CRMFields
                languages={supervisor.languages}
                calculatorOpen={openCalculator === supervisor.supervisor_id}
                onToggleCalculator={() =>
                  setOpenCalculator(previous =>
                    previous === supervisor.supervisor_id
                      ? null
                      : supervisor.supervisor_id
                  )
                }
                entry={getEffectiveEntry(
                  supervisor,
                  records[String(supervisor.supervisor_id)],
                )}
                onChange={(changes) =>
                  updateEntry(supervisor.supervisor_id, changes)
                }
              />
            </tr>
            {openCalculator === supervisor.supervisor_id && (
              <tr className="calculator-row">
                <td colSpan={showDistance ? 10 : 9}>
                  <CostCalculator
                    onClose={() => setOpenCalculator(null)}
                    entry={getEffectiveEntry(
                      supervisor,
                      records[String(supervisor.supervisor_id)],
                    )}
                    onChange={(changes) =>
                      updateEntry(supervisor.supervisor_id, changes)
                    }
                  />
                </td>
              </tr>
            )}
            </Fragment>
          ))}
        </tbody>
      </table>

      <p>
        Your CRM entries are saved in
        this browser. No account is required.
        Avoid entering confidential case or child information.
      </p>
    </div>
  )
}
