import { useState } from 'react'
import { api } from './api'
import { DocumentList } from './components/DocumentList'
import { DraftCard } from './components/DraftCard'
import { FitCard } from './components/FitCard'
import type { Doc, DraftResult, FitResult, Lang, Question } from './types'

const field = 'rounded-lg border border-slate-300 p-3 text-sm'
const input = `w-full ${field}`
const primary =
  'rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50'

export default function App() {
  const [job, setJob] = useState('')
  const [docs, setDocs] = useState<Doc[]>([])
  const [lang, setLang] = useState<Lang>('ja')
  const [question, setQuestion] = useState<Question>('shiboudouki')
  const [maxChars, setMaxChars] = useState(400)
  const [fit, setFit] = useState<FitResult | null>(null)
  const [draft, setDraft] = useState<DraftResult | null>(null)
  const [loading, setLoading] = useState<'fit' | 'draft' | null>(null)
  const [error, setError] = useState('')

  const ready = job.trim().length >= 20 && docs.length > 0

  async function run(kind: 'fit' | 'draft') {
    setError('')
    setLoading(kind)
    try {
      if (kind === 'fit') setFit(await api.fit(job, docs, lang))
      else setDraft(await api.draft(job, docs, question, lang, maxChars))
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Shukatsu Assistant</h1>
        <p className="text-slate-600">
          Check how well you fit a job posting and draft ES answers grounded in your own documents.
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        <section className="space-y-2">
          <h2 className="font-semibold">1. Job posting</h2>
          <textarea
            value={job}
            onChange={(e) => setJob(e.target.value)}
            placeholder="Paste the job description (募集要項) here"
            className={`${input} h-64`}
          />
        </section>
        <section className="space-y-2">
          <h2 className="font-semibold">2. Your documents</h2>
          <DocumentList docs={docs} onChange={setDocs} />
        </section>
      </div>

      <section className="mt-6 grid gap-4 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-2">
        <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm">
          Language
          <select value={lang} onChange={(e) => setLang(e.target.value as Lang)} className={`${field} mt-1 block py-2`}>
            <option value="ja">日本語</option>
            <option value="en">English</option>
          </select>
        </label>
        <button onClick={() => run('fit')} disabled={!ready || loading !== null} className={primary}>
          {loading === 'fit' ? 'Checking…' : 'Check fit'}
        </button>
        </div>
        <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm">
          ES question
          <select
            value={question}
            onChange={(e) => setQuestion(e.target.value as Question)}
            className={`${field} mt-1 block py-2`}
          >
            <option value="shiboudouki">志望動機 (motivation)</option>
            <option value="gakuchika">ガクチカ (student achievement)</option>
          </select>
        </label>
        <label className="text-sm">
          Max chars
          <input
            type="number"
            min={100}
            max={2000}
            step={50}
            value={maxChars}
            onChange={(e) => setMaxChars(Number(e.target.value))}
            className={`${field} mt-1 block w-24 py-2`}
          />
        </label>
        <button onClick={() => run('draft')} disabled={!ready || loading !== null} className={primary}>
          {loading === 'draft' ? 'Writing…' : 'Draft answer'}
        </button>
        </div>
      </section>

      {!ready && (
        <p className="mt-3 text-sm text-slate-500">Add a job posting and at least one document to start.</p>
      )}
      {error && <p className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        {fit && <FitCard result={fit} />}
        {draft && <DraftCard result={draft} />}
      </div>

      <footer className="mt-12 text-center text-xs text-slate-400">
        Your documents are sent only to the API for this request and are not stored.
      </footer>
    </div>
  )
}
