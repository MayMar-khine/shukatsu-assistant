import { useState } from 'react'
import { api } from '../api'
import type { Doc } from '../types'

interface Props {
  docs: Doc[]
  onChange: (docs: Doc[]) => void
}

/** Lets the user upload a resume/ES file or paste text. */
export function DocumentList({ docs, onChange }: Props) {
  const [pasted, setPasted] = useState('')
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    setError('')
    setUploading(true)
    try {
      onChange([...docs, await api.extract(file)])
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setUploading(false)
    }
  }

  function addPasted() {
    if (!pasted.trim()) return
    onChange([...docs, { name: `Pasted text ${docs.length + 1}`, text: pasted }])
    setPasted('')
  }

  return (
    <div className="space-y-3">
      <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium hover:bg-slate-100">
        {uploading ? 'Reading file…' : 'Upload PDF or .txt'}
        <input type="file" accept=".pdf,.txt,.md" className="hidden" onChange={handleFile} />
      </label>
      <textarea
        value={pasted}
        onChange={(e) => setPasted(e.target.value)}
        placeholder="…or paste a past ES answer, resume text, project notes"
        className="h-28 w-full rounded-lg border border-slate-300 p-3 text-sm"
      />
      <button
        onClick={addPasted}
        disabled={!pasted.trim()}
        className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-100 disabled:opacity-50"
      >
        Add pasted text
      </button>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <ul className="space-y-1">
        {docs.map((d, i) => (
          <li key={i} className="flex items-center justify-between rounded-md bg-slate-100 px-3 py-1.5 text-sm">
            <span className="truncate">
              {d.name} <span className="text-slate-500">· {d.text.length} chars</span>
            </span>
            <button
              onClick={() => onChange(docs.filter((_, j) => j !== i))}
              className="ml-2 text-slate-500 hover:text-red-600"
              aria-label={`Remove ${d.name}`}
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
