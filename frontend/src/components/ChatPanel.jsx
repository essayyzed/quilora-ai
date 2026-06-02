import { useState, useRef, useEffect, useCallback } from 'react'
import { streamQuery } from '../api.js'

let msgIdCounter = 0
function newId() {
  return ++msgIdCounter
}

function SendIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  )
}

function ChevronIcon({ open }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg"
      className={`w-3.5 h-3.5 transition-transform ${open ? 'rotate-180' : ''}`}
      viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round">
      <polyline points="6 9 12 15 18 9" />
    </svg>
  )
}

function ProviderBadge({ provider }) {
  if (!provider) return null
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
      bg-gray-700 text-gray-300 border border-gray-600">
      {provider}
    </span>
  )
}

function SourcesSection({ sources }) {
  const [open, setOpen] = useState(false)
  if (!sources || sources.count === 0) return null

  const docs = sources.documents || []

  return (
    <div className="mt-2 border-t border-gray-700 pt-2">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-200 transition-colors"
      >
        <ChevronIcon open={open} />
        {sources.count} source{sources.count !== 1 ? 's' : ''}
      </button>
      {open && docs.length > 0 && (
        <div className="mt-2 space-y-1.5">
          {docs.map((doc, i) => {
            const filename = doc.metadata?.filename || doc.metadata?.source || `Source ${i + 1}`
            const preview = doc.content_preview || ''
            return (
              <div key={i} className="p-2 rounded-lg bg-gray-800 border border-gray-700">
                <p className="text-gray-300 text-xs font-medium truncate">{filename}</p>
                {preview && (
                  <p className="text-gray-500 text-xs mt-0.5 line-clamp-2">{preview}</p>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function UserMessage({ message }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[75%] px-4 py-2.5 rounded-2xl rounded-tr-sm bg-blue-600 text-white text-sm
        leading-relaxed shadow-sm whitespace-pre-wrap break-words">
        {message.content}
      </div>
    </div>
  )
}

function AssistantMessage({ message, streaming }) {
  const hasMetadata = message.metadata && !streaming
  const totalSec = message.metadata?.total_ms
    ? (message.metadata.total_ms / 1000).toFixed(1)
    : null

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-gray-800 border border-gray-700
        shadow-sm overflow-hidden">
        <div className="px-4 py-3">
          <p className="text-gray-100 text-sm leading-relaxed whitespace-pre-wrap break-words">
            {message.content}
            {streaming && (
              <span className="inline-block w-1.5 h-4 bg-blue-400 ml-0.5 animate-pulse rounded-sm align-middle" />
            )}
          </p>
        </div>

        {!streaming && (
          <>
            <SourcesSection sources={message.sources} />
            {hasMetadata && (
              <div className="px-4 py-2 border-t border-gray-700 bg-gray-850 flex items-center gap-2 flex-wrap">
                <ProviderBadge provider={message.metadata.provider_used} />
                {totalSec && (
                  <span className="text-xs text-gray-500">{totalSec}s</span>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default function ChatPanel({ hasDocs }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)
  const streamingIdRef = useRef(null)

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    const lineHeight = 24
    const maxHeight = lineHeight * 4 + 16
    ta.style.height = Math.min(ta.scrollHeight, maxHeight) + 'px'
  }, [input])

  const handleSubmit = useCallback(async () => {
    const query = input.trim()
    if (!query || streaming) return

    setInput('')
    setError('')

    const userMsg = { id: newId(), role: 'user', content: query }
    const assistantId = newId()
    streamingIdRef.current = assistantId

    setMessages((prev) => [
      ...prev,
      userMsg,
      { id: assistantId, role: 'assistant', content: '', sources: null, metadata: null },
    ])
    setStreaming(true)

    try {
      for await (const event of streamQuery(query)) {
        if (event.type === 'documents') {
          const sourcesData = {
            count: event.count || 0,
            documents: event.metadata ? Object.values(event.metadata) : [],
          }
          // If metadata is an object of docs
          if (event.metadata && typeof event.metadata === 'object' && !Array.isArray(event.metadata)) {
            sourcesData.documents = Object.values(event.metadata)
          }
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, sources: sourcesData } : m
            )
          )
        } else if (event.type === 'token') {
          const token = event.content || ''
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + token } : m
            )
          )
        } else if (event.type === 'done') {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, metadata: event.metadata || null } : m
            )
          )
        }
      }
    } catch (e) {
      setError(e.message || 'Query failed. Please try again.')
      // Remove the empty assistant message on error
      setMessages((prev) => prev.filter((m) => m.id !== assistantId))
    } finally {
      setStreaming(false)
      streamingIdRef.current = null
    }
  }, [input, streaming])

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const isEmpty = messages.length === 0

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Error banner */}
      {error && (
        <div className="shrink-0 mx-4 mt-4 px-4 py-2.5 rounded-lg bg-red-950 border border-red-800
          text-red-300 text-sm flex items-start justify-between gap-2">
          <span>{error}</span>
          <button onClick={() => setError('')} className="text-red-400 hover:text-red-200 shrink-0">✕</button>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4">
        {isEmpty ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-2">
              <div className="text-4xl select-none">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-12 h-12 mx-auto text-gray-700"
                  viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
                  strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <p className="text-gray-500 text-sm">Upload a document and ask anything</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4 max-w-3xl mx-auto">
            {messages.map((msg) => {
              const isStreaming = streaming && msg.id === streamingIdRef.current
              return msg.role === 'user' ? (
                <UserMessage key={msg.id} message={msg} />
              ) : (
                <AssistantMessage key={msg.id} message={msg} streaming={isStreaming} />
              )
            })}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="shrink-0 border-t border-gray-800 px-4 py-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-2 rounded-2xl bg-gray-800 border border-gray-700
            focus-within:border-gray-600 px-4 py-3 transition-colors">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={streaming}
              placeholder={hasDocs ? 'Ask a question about your documents…' : 'Upload a document first…'}
              rows={1}
              className="flex-1 bg-transparent resize-none text-gray-100 text-sm placeholder-gray-500
                focus:outline-none leading-6 max-h-24 disabled:opacity-60"
            />
            <button
              onClick={handleSubmit}
              disabled={streaming || !input.trim()}
              className="shrink-0 p-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40
                disabled:cursor-not-allowed text-white transition-colors"
              aria-label="Send"
            >
              {streaming ? (
                <span className="block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <SendIcon />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-600 mt-1.5 text-center">
            Enter to send · Shift+Enter for newline
          </p>
        </div>
      </div>
    </div>
  )
}
