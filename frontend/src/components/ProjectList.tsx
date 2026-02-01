import type { ProjectSearchResult } from '../types'

interface ProjectListProps {
  projects: ProjectSearchResult[]
  selectedProjectId: number | null
  onSelectProject: (id: number) => void
  loading?: boolean
  error?: string | null
}

export function ProjectList({
  projects,
  selectedProjectId,
  onSelectProject,
  loading = false,
  error = null,
}: ProjectListProps) {
  if (error) {
    return (
      <section className="section" aria-labelledby="projects-heading">
        <h2 id="projects-heading" className="section-title">
          Select a project
        </h2>
        <p className="error-message" role="alert">
          {error}
        </p>
      </section>
    )
  }

  if (loading) {
    return (
      <section className="section" aria-labelledby="projects-heading">
        <h2 id="projects-heading" className="section-title">
          Select a project
        </h2>
        <p className="loading">Loading…</p>
      </section>
    )
  }

  if (projects.length === 0) {
    return (
      <section className="section" aria-labelledby="projects-heading">
        <h2 id="projects-heading" className="section-title">
          Select a project
        </h2>
        <p className="empty-message">No projects found. Try a different search.</p>
      </section>
    )
  }

  return (
    <section className="section" aria-labelledby="projects-heading">
      <h2 id="projects-heading" className="section-title">
        Select a project
      </h2>
      <ul className="project-list" role="list">
        {projects.map((project) => (
          <li key={project.id}>
            <button
              type="button"
              className={`project-item ${selectedProjectId === project.id ? 'selected' : ''}`}
              onClick={() => onSelectProject(project.id)}
            >
              <span className="project-name">{project.name}</span>
              <div className="project-meta">
                Manager: {project.manager_name} · {project.deliverable_count} deliverable
                {project.deliverable_count !== 1 ? 's' : ''}
              </div>
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}
