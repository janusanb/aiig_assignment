export interface ExcelValidationError {
  row: number
  column: string
  value: string | null
  error: string
}

export interface ExcelUploadResult {
  success: boolean
  filename: string
  total_rows: number
  imported_rows: number
  skipped_rows: number
  errors: ExcelValidationError[]
  projects_created: number
  managers_created: number
  deliverables_created: number
}

export interface ExcelPreviewRow {
  row_number: number
  project: string
  deliverable: string
  due_date: string
  frequency: string
  project_manager: string
  is_valid: boolean
  validation_errors: string[]
}

export interface ExcelPreviewResult {
  filename: string
  total_rows: number
  valid_rows: number
  invalid_rows: number
  preview_data: ExcelPreviewRow[]
  column_mapping: Record<string, string>
}

export interface ExcelTemplateResponse {
  columns: Record<string, { description: string; type: string; required?: boolean; valid_values?: Record<string, string>; default?: string; example?: string; format?: string }>
  notes: string[]
}
