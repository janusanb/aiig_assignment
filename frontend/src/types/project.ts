export interface ProjectSearchResult {
  id: number
  name: string
  manager_name: string
  deliverable_count: number
}

export interface ProjectWithManager {
  id: number
  name: string
  description: string | null
  manager_id: number
  created_at: string
  updated_at: string
  manager: { id: number; name: string; email: string | null }
}

export interface ProjectWithStats extends ProjectWithManager {
  total_deliverables: number
  pending_deliverables: number
  overdue_deliverables: number
  upcoming_7_days: number
}

export interface ProjectCreate {
  name: string
  description?: string
  manager_id?: number
  manager_name?: string
}
