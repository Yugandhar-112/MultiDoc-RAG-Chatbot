import CitationBadge from './CitationBadge.jsx'

// Renders inline [n] markers as small superscript-style tags matching the
// citation badges below, so it's visually obvious which sentence a given
// source backs up.
function AnswerText({ text }) {
  const parts = text.split(/(\[\d+\])/g)
  return (
    <p className="message-text">
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+)\]$/)
        if (match) {
          return (
            <sup className="inline-marker" key={i}>
              {match[1]}
            </sup>
          )
        }
        return <span key={i}>{part}</span>
      })}
    </p>
  )
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`message-row ${isUser ? 'message-row-user' : ''}`}>
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
