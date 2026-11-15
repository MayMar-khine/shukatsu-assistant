// These mirror the Pydantic models in backend/app/schemas.py.
export type Lang = 'ja' | 'en'
export type Question = 'shiboudouki' | 'gakuchika'

export interface Doc {
  name: string
  text: string
}

export interface Evidence {
  source: string
  text: string
  score: number
}

export interface FitResult {
  score: number
  summary: string
  strengths: string[]
  gaps: string[]
  evidence: Evidence[]
}

export interface DraftResult {
  draft: string
  evidence: Evidence[]
}
