import type { FitResult } from '../types'
import { EvidenceList } from './EvidenceList'

export function FitCard({ result }: { result: FitResult }) {
  const color = result.score >= 75 ? 'text-emerald-600' : result.score >= 50 ? 'text-amber-600' : 'text-red-600'
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-baseline gap-3">
        <span className={`text-4xl font-bold ${color}`}>{result.score}</span>
        <span className="text-slate-500">/ 100 fit</span>
      </div>
      <p className="mt-2 text-slate-700">{result.summary}</p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <h3 className="font-semibold text-emerald-700">Strengths</h3>
          <ul className="mt-1 list-disc pl-5 text-sm">
            {result.strengths.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </div>
        <div>
          <h3 className="font-semibold text-amber-700">Gaps</h3>
          <ul className="mt-1 list-disc pl-5 text-sm">
            {result.gaps.map((g, i) => <li key={i}>{g}</li>)}
          </ul>
        </div>
      </div>
      <EvidenceList items={result.evidence} />
    </section>
  )
}
