import type { ProjectSearchResult, ProjectWithStats, ProjectWithManager, ProjectCreate } from '../types/project'
import type { DeliverableWithProject, DeliverableCreate } from '../types/deliverable'
import type { ManagerWithStats, ManagerCreate } from '../types/manager'
import type { ExcelPreviewResult, ExcelUploadResult, ExcelTemplateResponse } from '../types/excel'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'
const API_PREFIX = '/api/v1'

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly statusCode: number
  ) {
    super(message)
    this.name = 'ApiError'
  }

  get isConflict(): boolean {
    return this.statusCode === 409
  }
}

async function fetchApi<T>(url: string, options?: { signal?: AbortSignal }): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, { signal: options?.signal })
  if (!response.ok) {
    const text = await response.text()
    let message = `Request failed: ${response.status} ${response.statusText}`
    try {
      const body = JSON.parse(text)
      if (body.detail) {
        message = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
      }
    } catch {
      if (text) message = text
    }
    throw new ApiError(message, response.status)
  }
  return response.json() as Promise<T>
}

async function fetchApiPost<T>(url: string, body: object): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const text = await response.text()
    let message = `Request failed: ${response.status} ${response.statusText}`
    try {
      const data = JSON.parse(text)
      if (data.detail) {
        message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      }
    } catch {
      if (text) message = text
    }
    throw new ApiError(message, response.status)
  }
  return response.json() as Promise<T>
}

export async function searchProjects(
  q: string,
  limit: number = 10
): Promise<ProjectSearchResult[]> {
  const params = new URLSearchParams({ q, limit: String(limit) })
  return fetchApi<ProjectSearchResult[]>(
    `${API_PREFIX}/projects/search?${params.toString()}`
  )
}

export async function getUpcomingDeliverables(
  projectId: number,
  days: number,
  options?: { signal?: AbortSignal; includeOverdue?: boolean }
): Promise<DeliverableWithProject[]> {
  const params = new URLSearchParams({
    project_id: String(projectId),
    days: String(days),
  })
  if (options?.includeOverdue === true) {
    params.set('include_overdue', 'true')
  }
  return fetchApi<DeliverableWithProject[]>(
    `${API_PREFIX}/deliverables/upcoming?${params.toString()}`,
    { signal: options?.signal }
  )
}

export async function listProjects(): Promise<ProjectWithStats[]> {
  return fetchApi<ProjectWithStats[]>(`${API_PREFIX}/projects`)
}

export async function listManagers(): Promise<ManagerWithStats[]> {
  return fetchApi<ManagerWithStats[]>(`${API_PREFIX}/managers`)
}

export async function createProject(body: ProjectCreate): Promise<ProjectWithManager> {
  return fetchApiPost<ProjectWithManager>(`${API_PREFIX}/projects`, body)
}

export async function createManager(body: ManagerCreate): Promise<{ id: number; name: string; email: string | null; created_at: string; updated_at: string }> {
  return fetchApiPost(`${API_PREFIX}/managers`, body)
}

export async function createDeliverable(body: DeliverableCreate): Promise<DeliverableWithProject> {
  return fetchApiPost<DeliverableWithProject>(`${API_PREFIX}/deliverables`, body)
}

async function fetchApiFormData<T>(url: string, formData: FormData): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    const text = await response.text()
    let message = `Request failed: ${response.status} ${response.statusText}`
    try {
      const data = JSON.parse(text)
      if (data.detail) {
        message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      }
    } catch {
      if (text) message = text
    }
    throw new ApiError(message, response.status)
  }
  return response.json() as Promise<T>
}

export async function uploadPreview(file: File): Promise<ExcelPreviewResult> {
  const formData = new FormData()
  formData.append('file', file)
  return fetchApiFormData<ExcelPreviewResult>(`${API_PREFIX}/upload/preview`, formData)
}

export async function uploadImport(
  file: File,
  options?: { skipInvalid?: boolean }
): Promise<ExcelUploadResult> {
  const formData = new FormData()
  formData.append('file', file)
  const params = new URLSearchParams()
  if (options?.skipInvalid !== false) params.set('skip_invalid', 'true')
  else params.set('skip_invalid', 'false')
  return fetchApiFormData<ExcelUploadResult>(
    `${API_PREFIX}/upload/import?${params.toString()}`,
    formData
  )
}

export async function getUploadTemplate(): Promise<ExcelTemplateResponse> {
  return fetchApi<ExcelTemplateResponse>(`${API_PREFIX}/upload/template`)
}
