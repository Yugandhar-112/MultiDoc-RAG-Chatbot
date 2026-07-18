import { useEffect, useRef, useState } from 'react'
import MessageBubble from './MessageBubble.jsx'

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
            <div className="chat-empty-mark">§</div>
            <h2>
              {hasDocuments
                ? 'Ask your first question'
                : 'Upload a source to begin'}
            </h2>
            <p>
              {hasDocuments
                ? 'Answers are grounded in your uploaded documents, with citations you can expand.'
                : 'Add a PDF, DOCX, or TXT file on the left, then ask anything about it.'}
            </p>
          </div>
        )}

        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
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
