const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function handleResponse(res) {
  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`
    try {
      const body = await res.json()
      if (body.detail) detail = body.detail
    } catch {
      // response wasn't JSON — fall back to the generic message
    }
    throw new Error(detail)
  }
  return res.json()
}

export async function uploadDocuments(files, sessionId) {
  const formData = new FormData()
  for (const file of files) {
    formData.append('files', file)
  }
  if (sessionId) {
    formData.append('session_id', sessionId)
  }
  const res = await fetch(`${API_BASE_URL}/documents`, {
    method: 'POST',
    body: formData,
  })
  return handleResponse(res)
}

export async function askQuestion(sessionId, question) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question }),
  })
  return handleResponse(res)
}

export async function getHistory(sessionId) {
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/history`)
  return handleResponse(res)
}
