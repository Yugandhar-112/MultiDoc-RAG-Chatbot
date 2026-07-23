import { useMemo, useState } from 'react'

export default function CitationBadge({ citation, index }) {
  const [expanded, setExpanded] = useState(false)

  // A tiny per-card rotation variance (rather than the same fixed angle
  // on every card) avoids the "every element behaves identically" tell —
  // computed once per citation via useMemo so it doesn't reshuffle on
  // every re-render.
  const tilt = useMemo(() => (Math.random() * 1.6 - 0.8).toFixed(2), [])

  return (
    <div className="citation">
      <button
        className="citation-tab"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
      >
        <span className="citation-number">{index}</span>
        <span className="citation-source">
          {citation.filename}
          {citation.page_number ? ` · p.${citation.page_number}` : ''}
        </span>
        <span className="citation-chevron">{expanded ? '−' : '+'}</span>
      </button>
      {expanded && (
        <div className="citation-card" style={{ '--tilt': `${tilt}deg` }}>
          <p className="citation-snippet">{citation.snippet}</p>
          <div className="citation-footer">
            <span>relevance {(citation.relevance_score * 100).toFixed(0)}%</span>
          </div>
        </div>
      )}
    </div>
  )
}