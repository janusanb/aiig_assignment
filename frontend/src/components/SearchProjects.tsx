import { type FormEvent, useState } from 'react'

interface SearchProjectsProps {
  onSearch: (query: string) => void
  loading?: boolean
}

export function SearchProjects({ onSearch, loading = false }: SearchProjectsProps) {
  const [query, setQuery] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = query.trim()
    if (trimmed) onSearch(trimmed)
  }

  return (
    <section className="section" aria-labelledby="search-heading">
      <h2 id="search-heading" className="section-title">
        Search projects
      </h2>
      <form onSubmit={handleSubmit} className="input-group">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type project name..."
          aria-label="Project search query"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>
    </section>
  )
}
