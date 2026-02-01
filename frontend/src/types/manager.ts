export interface ManagerWithStats {
  id: number
  name: string
  email: string | null
  created_at: string
  updated_at: string
  project_count: number
  deliverable_count: number
}

export interface ManagerCreate {
  name: string
  email?: string
}
