const BASE = '/api'

export async function getHealth() {
  const res = await fetch(`${BASE}/health`)
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`)
  return res.json()
}

export async function listDocuments() {
  const res = await fetch(`${BASE}/documents`)
  if (!res.ok) throw new Error(`Failed to list documents: ${res.status}`)
  return res.json()
}

export async function uploadDocument(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/documents/upload`, {
    method: 'POST',
    body: form,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Upload failed: ${res.status}`)
  }
  return res.json()
}

export async function deleteDocument(id) {
  const res = await fetch(`${BASE}/documents/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Delete failed: ${res.status}`)
  }
  return res.json()
}

export async function deleteAllDocuments() {
  const res = await fetch(`${BASE}/documents?all=true`, {
    method: 'DELETE',
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Delete all failed: ${res.status}`)
  }
  return res.json()
}

/**
 * Async generator that yields parsed SSE event objects.
 * Each yielded object: { type, content?, count?, metadata? }
 */
export async function* streamQuery(query) {
  const res = await fetch(`${BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, stream: true }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Query failed: ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    // SSE lines end with \n; events are separated by \n\n
    const lines = buffer.split('\n')
    // Keep the last (potentially incomplete) line in the buffer
    buffer = lines.pop()

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed || !trimmed.startsWith('data:')) continue
      const jsonStr = trimmed.slice('data:'.length).trim()
      if (!jsonStr || jsonStr === '[DONE]') continue
      try {
        const event = JSON.parse(jsonStr)
        yield event
      } catch {
        // skip malformed lines
      }
    }
  }

  // Flush any remaining buffer content
  if (buffer.trim().startsWith('data:')) {
    const jsonStr = buffer.trim().slice('data:'.length).trim()
    if (jsonStr && jsonStr !== '[DONE]') {
      try {
        yield JSON.parse(jsonStr)
      } catch {
        // ignore
      }
    }
  }
}
