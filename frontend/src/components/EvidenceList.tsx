import type { Evidence } from '../types'

/** Shows which parts of the user's documents the answer was based on. */
export function EvidenceList({ items }: { items: Evidence[] }) {
  if (!items.length) return null
  return (
    <details className="mt-4 text-sm">
      <summary className="cursor-pointer font-medium text-slate-600">
        Based on {items.length} excerpts from your documents
      </summary>
      <ol className="mt-2 space-y-2">
        {items.map((e, i) => (
          <li key={i} className="rounded-md border border-slate-200 bg-slate-50 p-2">
            <div className="mb-1 text-xs text-slate-500">
              [{i + 1}] {e.source} · relevance {e.score.toFixed(2)}
            </div>
            <p className="whitespace-pre-wrap">{e.text}</p>
          </li>
        ))}
      </ol>
    </details>
  )
}
