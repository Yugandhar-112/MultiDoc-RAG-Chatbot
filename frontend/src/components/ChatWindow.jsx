import { useEffect, useRef, useState } from 'react'
import MessageBubble from './MessageBubble.jsx'

// A small custom illustration built from the app's own "index card" motif —
// a stack of cards with a stamped mark — instead of a generic icon glyph.
// This is drawn once inline rather than pulled from an icon library, so it
// doesn't read as a stock/default asset.
function EmptyStateMark() {
  return (
    <svg width="96" height="72" viewBox="0 0 96 72" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="14" width="60" height="42" rx="2" transform="rotate(-6 10 14)" fill="#1c212e" stroke="#2a3040" />
      <rect x="16" y="10" width="60" height="42" rx="2" transform="rotate(-2 16 10)" fill="#1c212e" stroke="#2a3040" />
      <rect x="22" y="8" width="60" height="42" rx="2" fill="#151923" stroke="#333b4d" />
      <line x1="30" y1="20" x2="66" y2="20" stroke="#333b4d" strokeWidth="1.5" />
      <line x1="30" y1="27" x2="72" y2="27" stroke="#333b4d" strokeWidth="1.5" />
      <line x1="30" y1="34" x2="58" y2="34" stroke="#333b4d" strokeWidth="1.5" />
      <circle cx="70" cy="40" r="9" fill="none" stroke="#c9a04e" strokeWidth="1.5" />
      <text x="70" y="44" fontSize="11" fill="#c9a04e" textAnchor="middle" fontFamily="Fraunces, serif">
        §
      </text>
    </svg>
  )
}

export default function ChatWindow({ messages, onAsk, isAsking, hasDocuments, error }) {
  const [input, setInput] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isAsking])

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || isAsking) return
    onAsk(trimmed)
    setInput('')
  }

  return (
    <main className="chat">
      <div className="chat-scroll" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="chat-empty">
            <EmptyStateMark />
            <h2>{hasDocuments ? 'Ask your first question' : 'Upload a source to begin'}</h2>
            <p>
              {hasDocuments
                ? 'Answers are grounded in your uploaded documents, with citations you can expand.'
                : 'Add a PDF, DOCX, or TXT file on the left, then ask anything about it.'}
            </p>
          </div>
        )}

        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} index={i} />
        ))}

        {isAsking && (
          <div className="message-row">
            <div className="message-bubble message-bubble-assistant message-bubble-thinking">
              <span className="thinking-dot" />
              <span className="thinking-dot" />
              <span className="thinking-dot" />
            </div>
          </div>
        )}
      </div>

      {error && <div className="chat-error">{error}</div>}

      <form className="chat-input-row" onSubmit={handleSubmit}>
        <input
          className="chat-input"
          type="text"
          placeholder={hasDocuments ? 'Ask a question about your documents…' : 'Upload a document first…'}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!hasDocuments || isAsking}
        />
        <button
          type="submit"
          className="chat-send"
          disabled={!hasDocuments || isAsking || !input.trim()}
        >
          Ask
        </button>
      </form>
    </main>
  )
}