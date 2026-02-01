import { useCallback, useEffect, useState } from 'react'
import {
  SearchProjects,
  ProjectList,
  UpcomingDeliverables,
  AddManagerForm,
  AddProjectForm,
  AddDeliverableForm,
  ExcelImport,
} from './components'
import { searchProjects, getUpcomingDeliverables } from './services/api'
import type { ProjectSearchResult, DeliverableWithProject } from './types'

type AddDataTab = 'manager' | 'project' | 'deliverable' | 'excel'

const DEFAULT_UPCOMING_DAYS = 30

export default function App() {
  const [searchResults, setSearchResults] = useState<ProjectSearchResult[]>([])
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)

  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
  const [upcomingDays, setUpcomingDays] = useState(DEFAULT_UPCOMING_DAYS)
  const [upcomingDeliverables, setUpcomingDeliverables] = useState<DeliverableWithProject[]>([])
  const [upcomingLoading, setUpcomingLoading] = useState(false)
  const [upcomingError, setUpcomingError] = useState<string | null>(null)

  const [addDataTab, setAddDataTab] = useState<AddDataTab>('manager')

  const handleSearch = useCallback(async (query: string) => {
    setSearchLoading(true)
    setSearchError(null)
    setSelectedProjectId(null)
    setUpcomingDeliverables([])
    setUpcomingError(null)
    try {
      const results = await searchProjects(query)
      setSearchResults(results)
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : 'Could not load projects. Please try again.')
      setSearchResults([])
    } finally {
      setSearchLoading(false)
    }
  }, [])

  const handleSelectProject = useCallback((id: number) => {
    setSelectedProjectId(id)
    setUpcomingError(null)
  }, [])

  const handleDaysChange = useCallback((days: number) => {
    setUpcomingDays(days)
  }, [])

  useEffect(() => {
    if (selectedProjectId == null) {
      setUpcomingDeliverables([])
      return
    }
    const controller = new AbortController()
    setUpcomingLoading(true)
    setUpcomingError(null)
    ;(async () => {
      let aborted = false
      try {
        const data = await getUpcomingDeliverables(selectedProjectId!, upcomingDays, {
          signal: controller.signal,
          includeOverdue: true,
        })
        setUpcomingDeliverables(data)
      } catch (err) {
        if ((err as Error).name === 'AbortError') {
          aborted = true
        } else {
          setUpcomingError(
            err instanceof Error ? err.message : 'Could not load upcoming deliverables. Please try again.'
          )
          setUpcomingDeliverables([])
        }
      } finally {
        if (!aborted) setUpcomingLoading(false)
      }
    })()
    return () => controller.abort()
  }, [selectedProjectId, upcomingDays])

  return (
    <div>
      <header className="app-header">
        <h1>AIIG Deliverables Tracker</h1>
      </header>

      <SearchProjects onSearch={handleSearch} loading={searchLoading} />

      <ProjectList
        projects={searchResults}
        selectedProjectId={selectedProjectId}
        onSelectProject={handleSelectProject}
        loading={searchLoading}
        error={searchError}
      />

      <UpcomingDeliverables
        projectId={selectedProjectId}
        days={upcomingDays}
        deliverables={upcomingDeliverables}
        onDaysChange={handleDaysChange}
        loading={upcomingLoading}
        error={upcomingError}
      />

      <section className="add-data-section" aria-labelledby="add-data-heading">
        <h2 id="add-data-heading" className="section-title">
          Add data
        </h2>
        <div className="add-data-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={addDataTab === 'manager'}
            aria-controls="add-data-panel"
            id="tab-manager"
            className={addDataTab === 'manager' ? 'active-tab' : ''}
            onClick={() => setAddDataTab('manager')}
          >
            Add manager
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={addDataTab === 'project'}
            aria-controls="add-data-panel"
            id="tab-project"
            className={addDataTab === 'project' ? 'active-tab' : ''}
            onClick={() => setAddDataTab('project')}
          >
            Add project
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={addDataTab === 'deliverable'}
            aria-controls="add-data-panel"
            id="tab-deliverable"
            className={addDataTab === 'deliverable' ? 'active-tab' : ''}
            onClick={() => setAddDataTab('deliverable')}
          >
            Add deliverable
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={addDataTab === 'excel'}
            aria-controls="add-data-panel"
            id="tab-excel"
            className={addDataTab === 'excel' ? 'active-tab' : ''}
            onClick={() => setAddDataTab('excel')}
          >
            Import Excel
          </button>
        </div>
        <div id="add-data-panel" role="tabpanel" aria-labelledby={`tab-${addDataTab}`}>
          {addDataTab === 'manager' && <AddManagerForm />}
          {addDataTab === 'project' && <AddProjectForm />}
          {addDataTab === 'deliverable' && <AddDeliverableForm />}
          {addDataTab === 'excel' && <ExcelImport />}
        </div>
      </section>
    </div>
  )
}
