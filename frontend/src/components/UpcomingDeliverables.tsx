import { useState, useMemo } from 'react'
import type { DeliverableWithProject } from '../types'

const DAYS_OPTIONS = [30, 60, 90] as const

const FREQUENCY_ORDER = ['M', 'Q', 'SA', 'A', 'OT']

interface UpcomingDeliverablesProps {
  projectId: number | null
  days: number
  deliverables: DeliverableWithProject[]
  onDaysChange: (days: number) => void
  loading?: boolean
  error?: string | null
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateStr
  }
}

function getDueUrgencyClass(daysUntilDue: number): string {
  if (daysUntilDue < 10) return 'due-urgent'
  if (daysUntilDue >= 11 && daysUntilDue <= 29) return 'due-warning'
  return ''
}

export function UpcomingDeliverables({
  projectId,
  days,
  deliverables,
  onDaysChange,
  loading = false,
  error = null,
}: UpcomingDeliverablesProps) {
  const [sortByFrequency, setSortByFrequency] = useState(false)

  const displayedDeliverables = useMemo(() => {
    if (!sortByFrequency) return deliverables
    return [...deliverables].sort((a, b) => {
      const i = FREQUENCY_ORDER.indexOf(a.frequency)
      const j = FREQUENCY_ORDER.indexOf(b.frequency)
      const orderA = i === -1 ? FREQUENCY_ORDER.length : i
      const orderB = j === -1 ? FREQUENCY_ORDER.length : j
      return orderA - orderB
    })
  }, [deliverables, sortByFrequency])

  if (projectId == null) {
    return (
      <section className="section" aria-labelledby="upcoming-heading">
        <h2 id="upcoming-heading" className="section-title">
          Upcoming deliverables
        </h2>
        <p className="select-project-hint">Select a project above to view upcoming deliverables.</p>
      </section>
    )
  }

  return (
    <section className="section" aria-labelledby="upcoming-heading">
      <h2 id="upcoming-heading" className="section-title">
        Upcoming deliverables (next {days} days)
      </h2>
      <div className="days-selector">
        <div className="days-selector-group">
          {DAYS_OPTIONS.map((d) => (
            <button
              key={d}
              type="button"
              className={days === d ? 'active' : ''}
              onClick={() => onDaysChange(d)}
            >
              {d} days
            </button>
          ))}
        </div>
        <button
          type="button"
          className={sortByFrequency ? 'active' : ''}
          onClick={() => setSortByFrequency((prev) => !prev)}
          title="Order by frequency: Monthly, Quarterly, Semi-Annual, Annual, One-Time"
        >
          Sort by frequency
        </button>
      </div>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {loading && (
        <p className="loading">Loading…</p>
      )}

      {!loading && !error && deliverables.length === 0 && (
        <p className="empty-message">No upcoming deliverables in this window.</p>
      )}

      {!loading && !error && deliverables.length > 0 && (
        <table className="deliverables-table">
          <thead>
            <tr>
              <th>Description</th>
              <th>Due date</th>
              <th>Responsible</th>
              <th>Frequency</th>
              <th>Days until due</th>
            </tr>
          </thead>
          <tbody>
            {displayedDeliverables.map((d) => (
              <tr key={d.id}>
                <td>{d.description}</td>
                <td>{formatDate(d.due_date)}</td>
                <td>{d.manager_name}</td>
                <td>{d.frequency_display}</td>
                <td className={getDueUrgencyClass(d.days_until_due)}>
                  <span className={d.is_overdue ? 'deliverable-overdue' : ''}>
                    {d.is_overdue ? `Overdue (${-d.days_until_due} days)` : d.days_until_due}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
