import CitationBadge from './CitationBadge.jsx'

function AnswerText({ text }) {
  const cleaned = text.replace(/\*\*(.+?)\*\*/g, '$1')
  const parts = cleaned.split(/(\[\d+(?:\s*,\s*\d+)*\])/g)

  return (
    <p className="message-text">
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+(?:\s*,\s*\d+)*)\]$/)
        if (match) {
          const numbers = match[1].split(',').map((n) => n.trim())
          return (
            <span key={i}>
              {numbers.map((n, ni) => (
                <sup className="inline-marker" key={`${i}-${ni}`}>
                  {n}
                </sup>
              ))}
            </span>
          )
        }
        return <span key={i}>{part}</span>
      })}
    </p>
  )
}

export default function MessageBubble({ message, index }) {
  const isUser = message.role === 'user'
  // Numbering each turn gives the margin something concrete to anchor on —
  // like a manuscript's marginal folio number — rather than the message
  // simply floating in empty space.
  const turnLabel = String(index + 1).padStart(2, '0')

  return (
    <div className={`message-row ${isUser ? 'message-row-user' : ''}`}>
      {!isUser && <span className="turn-label">{turnLabel}</span>}
      <div className={`message-bubble ${isUser ? 'message-bubble-user' : 'message-bubble-assistant'}`}>
        {message.no_answer_found && <div className="no-answer-flag">No confident match found</div>}
        <AnswerText text={message.content} />

        {!isUser && message.citations?.length > 0 && (
          <div className="citation-list">
            {message.citations.map((c) => (
              <CitationBadge
                key={`${c.doc_id}-${c.chunk_index}`}
                citation={c}
                index={c.citation_number}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}