import CitationBadge from './CitationBadge.jsx'

// Renders [n] citation markers (including grouped ones like "[1, 4]") as
// small superscript tags matching the citation badges below, and quietly
// strips stray **bold** markers if the model emits them despite being
// told not to — belt-and-suspenders since instruction-following isn't
// perfectly reliable.
function AnswerText({ text }) {
  const cleaned = text.replace(/\*\*(.+?)\*\*/g, '$1')

  // Split on citation bracket groups — single "[1]" or grouped "[1, 4]" —
  // capturing the digits+commas inside so each number can become its own
  // superscript, matching how the backend now parses grouped citations.
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
