import { type FormEvent, useEffect, useState } from 'react'
import { createDeliverable, listProjects, ApiError } from '../services/api'
import type { ProjectWithStats } from '../types/project'

const FREQUENCIES = [
  { value: 'M', label: 'Monthly' },
  { value: 'Q', label: 'Quarterly' },
  { value: 'SA', label: 'Semi-Annual' },
  { value: 'A', label: 'Annual' },
  { value: 'OT', label: 'One-Time' },
] as const

export function AddDeliverableForm() {
  const [projectId, setProjectId] = useState<string>('')
  const [description, setDescription] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [frequency, setFrequency] = useState('OT')
  const [notes, setNotes] = useState('')
  const [projects, setProjects] = useState<ProjectWithStats[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    listProjects().then(setProjects).catch(() => {})
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmedDesc = description.trim()
    if (!trimmedDesc || !projectId || !dueDate) return
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      await createDeliverable({
        project_id: parseInt(projectId, 10),
        description: trimmedDesc,
        due_date: dueDate,
        frequency,
        notes: notes.trim() || undefined,
      })
      setSuccess('Deliverable created.')
      setDescription('')
      setDueDate('')
      setNotes('')
    } catch (err) {
      if (err instanceof ApiError && err.isConflict) {
        setError('Already exists — a deliverable for this project with the same due date, frequency, and description already exists.')
      } else {
        setError(err instanceof Error ? err.message : 'Could not create deliverable.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="section" aria-labelledby="add-deliverable-heading">
      <h2 id="add-deliverable-heading" className="section-title">
        Add deliverable
      </h2>
      <form onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="deliverable-project">Project (required)</label>
          <select
            id="deliverable-project"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            required
            disabled={loading}
          >
            <option value="">— Select project —</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="deliverable-description">Description (required)</label>
          <input
            id="deliverable-description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            disabled={loading}
          />
        </div>
        <div className="form-field">
          <label htmlFor="deliverable-due">Due date (required)</label>
          <input
            id="deliverable-due"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            required
            disabled={loading}
          />
        </div>
        <div className="form-field">
          <label htmlFor="deliverable-frequency">Frequency</label>
          <select
            id="deliverable-frequency"
            value={frequency}
            onChange={(e) => setFrequency(e.target.value)}
            disabled={loading}
          >
            {FREQUENCIES.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="deliverable-notes">Notes (optional)</label>
          <input
            id="deliverable-notes"
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            disabled={loading}
          />
        </div>
        <button type="submit" disabled={loading || !description.trim() || !projectId || !dueDate}>
          {loading ? 'Creating…' : 'Create deliverable'}
        </button>
        {error && <p className="error-message" role="alert">{error}</p>}
        {success && <p className="success-message" role="status">{success}</p>}
      </form>
    </section>
  )
}
