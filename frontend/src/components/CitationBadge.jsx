import { useState } from 'react'

export default function CitationBadge({ citation, index }) {
  const [expanded, setExpanded] = useState(false)

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
        <div className="citation-card">
          <p className="citation-snippet">{citation.snippet}</p>
          <div className="citation-footer">
            <span>relevance {(citation.relevance_score * 100).toFixed(0)}%</span>
          </div>
        </div>
      )}
    </div>
  )
}
