import { type FormEvent, useEffect, useState } from 'react'
import { createProject, listManagers, ApiError } from '../services/api'
import type { ManagerWithStats } from '../types/manager'

export function AddProjectForm() {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [managerId, setManagerId] = useState<string>('')
  const [managerName, setManagerName] = useState('')
  const [managers, setManagers] = useState<ManagerWithStats[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    listManagers().then(setManagers).catch(() => {})
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmedName = name.trim()
    if (!trimmedName) return
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const body: { name: string; description?: string; manager_id?: number; manager_name?: string } = {
        name: trimmedName,
        description: description.trim() || undefined,
      }
      if (managerId) {
        body.manager_id = parseInt(managerId, 10)
      } else if (managerName.trim()) {
        body.manager_name = managerName.trim()
      }
      await createProject(body)
      setSuccess(`Project "${trimmedName}" created.`)
      setName('')
      setDescription('')
      setManagerId('')
      setManagerName('')
    } catch (err) {
      if (err instanceof ApiError && err.isConflict) {
        setError('Project with that name already exists.')
      } else {
        setError(err instanceof Error ? err.message : 'Could not create project.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="section" aria-labelledby="add-project-heading">
      <h2 id="add-project-heading" className="section-title">
        Add project
      </h2>
      <form onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="project-name">Name (required)</label>
          <input
            id="project-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            disabled={loading}
          />
        </div>
        <div className="form-field">
          <label htmlFor="project-description">Description (optional)</label>
          <input
            id="project-description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={loading}
          />
        </div>
        <div className="form-field">
          <label htmlFor="project-manager">Manager (select or type name)</label>
          <select
            id="project-manager"
            value={managerId}
            onChange={(e) => {
              setManagerId(e.target.value)
              if (e.target.value) setManagerName('')
            }}
            disabled={loading}
          >
            <option value="">— Select manager —</option>
            {managers.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Or type manager name"
            value={managerName}
            onChange={(e) => {
              setManagerName(e.target.value)
              if (e.target.value) setManagerId('')
            }}
            disabled={loading}
            style={{ marginTop: '0.5rem' }}
          />
        </div>
        <button type="submit" disabled={loading || !name.trim()}>
          {loading ? 'Creating…' : 'Create project'}
        </button>
        {error && <p className="error-message" role="alert">{error}</p>}
        {success && <p className="success-message" role="status">{success}</p>}
      </form>
    </section>
  )
}
