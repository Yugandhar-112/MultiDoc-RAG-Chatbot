import { useState } from 'react'
import UploadPanel from './components/UploadPanel.jsx'
import ChatWindow from './components/ChatWindow.jsx'
import { uploadDocuments, askQuestion } from './api/client.js'
import './App.css'

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [documents, setDocuments] = useState([])
  const [messages, setMessages] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [isAsking, setIsAsking] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [chatError, setChatError] = useState(null)

  async function handleUpload(files) {
    setIsUploading(true)
    setUploadError(null)
    try {
      const result = await uploadDocuments(files, sessionId)
      setSessionId(result.session_id)
      setDocuments((prev) => [...prev, ...result.documents])
    } catch (err) {
      setUploadError(err.message || 'Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  async function handleAsk(question) {
    setChatError(null)
    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setIsAsking(true)
    try {
      const result = await askQuestion(sessionId, question)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: result.answer,
          citations: result.citations,
          no_answer_found: result.no_answer_found,
        },
      ])
    } catch (err) {
      setChatError(err.message || 'Something went wrong answering that question.')
      // Roll back the optimistic user message's "pending" state by leaving
      // it in place — the error banner explains what happened, and the
      // person can just try asking again.
    } finally {
      setIsAsking(false)
    }
  }

  return (
    <div className="app-shell">
      <UploadPanel
        documents={documents}
        onUpload={handleUpload}
        isUploading={isUploading}
        error={uploadError}
      />
      <ChatWindow
        messages={messages}
        onAsk={handleAsk}
        isAsking={isAsking}
        hasDocuments={documents.length > 0}
        error={chatError}
      />
    </div>
  )
}
