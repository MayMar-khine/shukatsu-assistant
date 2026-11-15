import { useState } from 'react'
import type { DraftResult } from '../types'
import { EvidenceList } from './EvidenceList'

export function DraftCard({ result }: { result: DraftResult }) {
  const [copied, setCopied] = useState(false)
  async function copy() {
    await navigator.clipboard.writeText(result.draft)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Draft · {result.draft.length} chars</h3>
        <button onClick={copy} className="text-sm text-indigo-600 hover:underline">
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <p className="mt-2 whitespace-pre-wrap leading-relaxed">{result.draft}</p>
      <EvidenceList items={result.evidence} />
    </section>
  )
}
