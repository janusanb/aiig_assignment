import { type FormEvent, useState } from 'react'
import { createManager, ApiError } from '../services/api'

export function AddManagerForm() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmedName = name.trim()
    if (!trimmedName) return
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      await createManager({ name: trimmedName, email: email.trim() || undefined })
      setSuccess(`Manager "${trimmedName}" created.`)
      setName('')
      setEmail('')
    } catch (err) {
      if (err instanceof ApiError && err.isConflict) {
        setError('Already exists — a manager with this name already exists.')
      } else {
        setError(err instanceof Error ? err.message : 'Could not create manager.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="section" aria-labelledby="add-manager-heading">
      <h2 id="add-manager-heading" className="section-title">
        Add manager
      </h2>
      <form onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="manager-name">Name (required)</label>
          <input
            id="manager-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            disabled={loading}
          />
        </div>
        <div className="form-field">
          <label htmlFor="manager-email">Email (optional)</label>
          <input
            id="manager-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
          />
        </div>
        <button type="submit" disabled={loading || !name.trim()}>
          {loading ? 'Creating…' : 'Create manager'}
        </button>
        {error && <p className="error-message" role="alert">{error}</p>}
        {success && <p className="success-message" role="status">{success}</p>}
      </form>
    </section>
  )
}
