import { useState } from 'react'
import { uploadPreview, uploadImport, getUploadTemplate } from '../services/api'
import type { ExcelPreviewResult, ExcelUploadResult, ExcelTemplateResponse } from '../types/excel'

const ALLOWED_EXT = '.xlsx,.xls,.csv'

export function ExcelImport() {
  const [file, setFile] = useState<File | null>(null)
  const [previewResult, setPreviewResult] = useState<ExcelPreviewResult | null>(null)
  const [importResult, setImportResult] = useState<ExcelUploadResult | null>(null)
  const [template, setTemplate] = useState<ExcelTemplateResponse | null>(null)
  const [showTemplate, setShowTemplate] = useState(false)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [importLoading, setImportLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const chosen = e.target.files?.[0] ?? null
    setFile(chosen)
    setPreviewResult(null)
    setImportResult(null)
    setError(null)
  }

  async function handlePreview() {
    if (!file) return
    setPreviewLoading(true)
    setError(null)
    setImportResult(null)
    try {
      const result = await uploadPreview(file)
      setPreviewResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Preview failed.')
    } finally {
      setPreviewLoading(false)
    }
  }

  async function handleImport() {
    if (!file) return
    setImportLoading(true)
    setError(null)
    try {
      const result = await uploadImport(file, { skipInvalid: true })
      setImportResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed.')
    } finally {
      setImportLoading(false)
    }
  }

  async function handleShowTemplate() {
    if (template) {
      setShowTemplate((s) => !s)
      return
    }
    try {
      const data = await getUploadTemplate()
      setTemplate(data)
      setShowTemplate(true)
    } catch {
      setError('Could not load template info.')
    }
  }

  return (
    <section className="section excel-import-section" aria-labelledby="excel-import-heading">
      <h2 id="excel-import-heading" className="section-title">
        Import from Excel
      </h2>

      <div className="input-group">
        <input
          type="file"
          accept={ALLOWED_EXT}
          onChange={handleFileChange}
          aria-label="Choose Excel or CSV file"
        />
      </div>

      <div className="excel-import-actions">
        <button
          type="button"
          onClick={handlePreview}
          disabled={!file || previewLoading}
          aria-busy={previewLoading}
        >
          {previewLoading ? 'Loading…' : 'Preview'}
        </button>
        <button
          type="button"
          onClick={handleImport}
          disabled={!file || importLoading}
          aria-busy={importLoading}
        >
          {importLoading ? 'Importing…' : 'Import'}
        </button>
        <button type="button" onClick={handleShowTemplate} className="button-secondary">
          {showTemplate ? 'Hide template' : 'View template'}
        </button>
      </div>

      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}

      {showTemplate && template && (
        <div className="excel-template-box">
          <p className="excel-template-notes">
            {template.notes.map((n, i) => (
              <span key={i}>{n} </span>
            ))}
          </p>
          <dl className="excel-template-cols">
            {Object.entries(template.columns).map(([name, col]) => (
              <div key={name}>
                <dt>{name}</dt>
                <dd>
                  {col.description}
                  {col.valid_values && (
                    <span> — {Object.entries(col.valid_values).map(([k, v]) => `${k}: ${v}`).join(', ')}</span>
                  )}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {previewResult && (
        <div className="excel-preview-result">
          <h3 className="excel-result-heading">Preview</h3>
          <p>
            <strong>{previewResult.filename}</strong>: {previewResult.total_rows} rows —{' '}
            <span className="valid-count">{previewResult.valid_rows} valid</span>,{' '}
            <span className="invalid-count">{previewResult.invalid_rows} invalid</span>
          </p>
          {previewResult.preview_data.length > 0 && (
            <div className="table-wrap">
              <table className="excel-preview-table">
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Project</th>
                    <th>Deliverable</th>
                    <th>Due date</th>
                    <th>Freq</th>
                    <th>Manager</th>
                    <th>Valid</th>
                    <th>Errors</th>
                  </tr>
                </thead>
                <tbody>
                  {previewResult.preview_data.map((row) => (
                    <tr key={row.row_number} className={row.is_valid ? '' : 'row-invalid'}>
                      <td>{row.row_number}</td>
                      <td>{row.project}</td>
                      <td>{row.deliverable}</td>
                      <td>{row.due_date}</td>
                      <td>{row.frequency}</td>
                      <td>{row.project_manager}</td>
                      <td>{row.is_valid ? 'Yes' : 'No'}</td>
                      <td>{row.validation_errors.length ? row.validation_errors.join('; ') : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {importResult && (
        <div className="excel-import-result">
          <h3 className="excel-result-heading">Import result</h3>
          <p>
            {importResult.success ? (
              <>
                <strong>{importResult.filename}</strong>: {importResult.imported_rows} imported,{' '}
                {importResult.skipped_rows} skipped. Created: {importResult.managers_created} managers,{' '}
                {importResult.projects_created} projects, {importResult.deliverables_created} deliverables.
              </>
            ) : (
              <>Import failed.</>
            )}
          </p>
          {importResult.errors.length > 0 && (
            <ul className="excel-errors-list">
              {importResult.errors.slice(0, 20).map((e, i) => (
                <li key={i}>
                  Row {e.row}, {e.column}: {e.error}
                </li>
              ))}
              {importResult.errors.length > 20 && (
                <li>… and {importResult.errors.length - 20} more</li>
              )}
            </ul>
          )}
        </div>
      )}
    </section>
  )
}
