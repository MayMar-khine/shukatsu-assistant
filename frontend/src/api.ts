import type { Doc, DraftResult, FitResult, Lang, Question } from './types'

const BASE = import.meta.env.VITE_API_URL ?? ''

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    const detail = typeof body.detail === 'string' ? body.detail : `Request failed (${res.status})`
    throw new Error(detail)
  }
  return body as T
}

const postJson = <T>(path: string, data: unknown) =>
  request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

export const api = {
  extract(file: File) {
    const form = new FormData()
    form.append('file', file)
    return request<Doc>('/api/extract', { method: 'POST', body: form })
  },
  fit(job_posting: string, documents: Doc[], language: Lang) {
    return postJson<FitResult>('/api/fit', { job_posting, documents, language })
  },
  draft(job_posting: string, documents: Doc[], question: Question, language: Lang, max_chars: number) {
    return postJson<DraftResult>('/api/draft', { job_posting, documents, question, language, max_chars })
  },
}
