export interface DeliverableCreate {
  project_id?: number
  project_name?: string
  description: string
  due_date: string
  frequency: string
  notes?: string
}

export interface DeliverableWithProject {
  id: number
  project_id: number
  description: string
  due_date: string
  frequency: string
  status: string
  notes: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
  project_name: string
  manager_name: string
  frequency_display: string
  days_until_due: number
  is_overdue: boolean
}
