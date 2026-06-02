import { useState, useRef, useEffect, useCallback } from 'react'
import { streamQuery } from '../api.js'

let msgIdCounter = 0
const newId = () => ++msgIdCounter

// Minimal markdown renderer: bold, inline code, paragraphs, numbered/bullet lists
function Markdown({ text }) {
  if (!text) return null

  const blocks = text.split(/\n\n+/)
  return (
    <div className="space-y-2.5">
      {blocks.map((block, i) => {
        const trimmed = block.trim()
        if (!trimmed) return null

        // Numbered list
        if (/^(\d+)\.\s/.test(trimmed)) {
          const items = trimmed.split(/\n(?=\d+\.\s)/)
          return (
            <ol key={i} className="list-none space-y-1.5 pl-0">
              {items.map((item, j) => {
                const match = item.match(/^(\d+)\.\s(.+)/)
                if (!match) return null
                return (
                  <li key={j} className="flex gap-2.5 items-start">
                    <span className="shrink-0 w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] font-bold flex items-center justify-center mt-0.5">{match[1]}</span>
                    <span className="flex-1">{renderInline(match[2])}</span>
                  </li>
                )
              })}
            </ol>
          )
        }

        // Bullet list
        if (/^[-*•]\s/.test(trimmed)) {
          const items = trimmed.split(/\n(?=[-*•]\s)/)
          return (
            <ul key={i} className="space-y-1">
              {items.map((item, j) => {
                const content = item.replace(/^[-*•]\s/, '').trim()
                return (
                  <li key={j} className="flex gap-2 items-start">
                    <span className="shrink-0 w-1.5 h-1.5 rounded-full bg-indigo-400/60 mt-2" />
                    <span className="flex-1">{renderInline(content)}</span>
                  </li>
                )
              })}
            </ul>
          )
        }

        // Heading
        if (/^#{1,3}\s/.test(trimmed)) {
          const content = trimmed.replace(/^#{1,3}\s/, '')
          return <p key={i} className="font-semibold text-white">{renderInline(content)}</p>
        }

        // Regular paragraph
        return <p key={i} className="leading-relaxed">{renderInline(trimmed)}</p>
      })}
    </div>
  )
}

function CitationBadge({ num }) {
  return (
    <sup>
      <span className="inline-flex items-center justify-center min-w-[1.1rem] h-[1.1rem] rounded px-0.5 text-[9px] font-bold bg-indigo-500/20 text-indigo-300 mx-0.5 cursor-default select-none border border-indigo-500/20">
        {num}
      </span>
    </sup>
  )
}

function renderInline(text) {
  // Split on **bold**, *italic*, `code`, [N] citations
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[\d+\])/)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**'))
      return <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>
    if (part.startsWith('*') && part.endsWith('*'))
      return <em key={i} className="text-slate-300 italic">{part.slice(1, -1)}</em>
    if (part.startsWith('`') && part.endsWith('`'))
      return <code key={i} className="px-1.5 py-0.5 rounded text-[11px] font-mono text-violet-300 bg-violet-500/10">{part.slice(1, -1)}</code>
    if (/^\[\d+\]$/.test(part))
      return <CitationBadge key={i} num={part.slice(1, -1)} />
    return part
  })
}

function AiAvatar() {
  return (
    <div className="w-7 h-7 rounded-lg shrink-0 bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-500/20 mt-0.5">
      <svg className="w-3.5 h-3.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5" />
        <path d="M2 12l10 5 10-5" />
      </svg>
    </div>
  )
}

const EXT_COLORS = {
  pdf: 'text-red-400 bg-red-400/10', docx: 'text-blue-400 bg-blue-400/10',
  doc: 'text-blue-400 bg-blue-400/10', xlsx: 'text-emerald-400 bg-emerald-400/10',
  csv: 'text-teal-400 bg-teal-400/10', pptx: 'text-orange-400 bg-orange-400/10',
  json: 'text-yellow-400 bg-yellow-400/10', yaml: 'text-pink-400 bg-pink-400/10',
  yml: 'text-pink-400 bg-pink-400/10', html: 'text-violet-400 bg-violet-400/10',
  md: 'text-slate-300 bg-slate-300/10', txt: 'text-slate-400 bg-slate-400/10',
}

function SourceCard({ doc, index }) {
  const [expanded, setExpanded] = useState(false)
  const num = index + 1
  const filename = doc.metadata?.filename || `Source ${num}`
  const ext = filename.split('.').pop()?.toLowerCase() || 'txt'
  const extColor = EXT_COLORS[ext] || 'text-slate-400 bg-slate-400/10'
  const page = doc.metadata?.page_number
  const score = doc.score
  const content = doc.content || ''
  const preview = content.slice(0, 180)
  const hasMore = content.length > 180

  return (
    <div className="rounded-lg overflow-hidden" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
      <div className="flex items-start gap-2.5 px-3 py-2.5">
        {/* Citation number */}
        <span className="shrink-0 w-5 h-5 rounded bg-indigo-500/15 text-indigo-300 text-[10px] font-bold flex items-center justify-center mt-0.5 border border-indigo-500/20">
          {num}
        </span>
        <div className="flex-1 min-w-0">
          {/* Header row */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className={`inline-block px-1 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider ${extColor}`}>{ext}</span>
            <p className="text-[11px] text-slate-300 font-medium truncate flex-1">{filename}</p>
            {page != null && (
              <span className="shrink-0 text-[10px] text-slate-600">p.{page}</span>
            )}
          </div>
          {/* Relevance bar */}
          {score != null && (
            <div className="flex items-center gap-2 mt-1.5">
              <div className="h-1 flex-1 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                <div className="h-full rounded-full transition-all" style={{ width: `${Math.min(score * 100, 100)}%`, background: score > 0.7 ? '#6366f1' : score > 0.4 ? '#818cf8' : '#6b7280' }} />
              </div>
              <span className="shrink-0 text-[10px] text-slate-600 tabular-nums">{(score * 100).toFixed(0)}%</span>
            </div>
          )}
          {/* Content */}
          <p className="text-[11px] text-slate-500 mt-1.5 leading-relaxed">
            {expanded ? content : preview}{!expanded && hasMore ? '…' : ''}
          </p>
          {hasMore && (
            <button
              onClick={() => setExpanded(e => !e)}
              className="text-[10px] text-indigo-400/70 hover:text-indigo-300 mt-1 transition-colors"
            >
              {expanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function SourcesSection({ sources }) {
  const [collapsed, setCollapsed] = useState(false)
  if (!sources || sources.count === 0) return null
  const docs = sources.documents || []
  if (docs.length === 0) return null

  return (
    <div className="mt-3 pt-3 border-t border-white/5">
      <button
        onClick={() => setCollapsed(c => !c)}
        className="flex items-center gap-1.5 w-full mb-2.5 group"
      >
        <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-600 group-hover:text-slate-400 transition-colors">
          {sources.count} source{sources.count !== 1 ? 's' : ''}
        </p>
        <svg className={`w-3 h-3 text-slate-700 group-hover:text-slate-500 transition-all ml-auto ${collapsed ? '' : 'rotate-180'}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
      {!collapsed && (
        <div className="space-y-1.5">
          {docs.map((doc, i) => <SourceCard key={i} doc={doc} index={i} />)}
        </div>
      )}
    </div>
  )
}

function MetaFooter({ metadata }) {
  if (!metadata) return null
  const sec = metadata.total_ms ? (metadata.total_ms / 1000).toFixed(1) : null
  return (
    <div className="mt-3 pt-2.5 border-t border-white/5 flex items-center gap-2 flex-wrap">
      {metadata.provider_used && (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium text-slate-400 border border-white/8" style={{ background: 'rgba(255,255,255,0.04)' }}>
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 inline-block" />
          {metadata.provider_used}
          {metadata.provider_fallback && <span className="text-amber-400 ml-0.5">↩</span>}
        </span>
      )}
      {sec && <span className="text-[10px] text-slate-600">{sec}s</span>}
    </div>
  )
}

function UserMessage({ message }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[78%] px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm leading-relaxed text-white whitespace-pre-wrap break-words"
        style={{ background: 'linear-gradient(135deg, #6366f1, #7c3aed)', boxShadow: '0 2px 12px rgba(99,102,241,0.25)' }}>
        {message.content}
      </div>
    </div>
  )
}

function AssistantMessage({ message, streaming }) {
  return (
    <div className="flex items-start gap-2.5">
      <AiAvatar />
      <div className="flex-1 min-w-0 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-slate-300"
        style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)' }}>
        {streaming && !message.content ? (
          <div className="flex gap-1 items-center h-5">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        ) : (
          <>
            <Markdown text={message.content} />
            {streaming && <span className="inline-block w-0.5 h-4 bg-indigo-400 ml-0.5 cursor-blink rounded-sm align-middle" />}
          </>
        )}
        {!streaming && (
          <>
            <SourcesSection sources={message.sources} />
            <MetaFooter metadata={message.metadata} />
          </>
        )}
      </div>
    </div>
  )
}

const EXAMPLES = [
  'Summarize this document',
  'What are the key findings?',
  'List the main conclusions',
  'Explain the methodology used',
]

function EmptyState({ onExample }) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 pb-12 select-none">
      <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-violet-600/20 flex items-center justify-center border border-indigo-500/20">
        <svg className="w-7 h-7 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </div>
      <div className="text-center space-y-1.5">
        <p className="text-base font-semibold text-slate-200">Ask anything about your documents</p>
        <p className="text-sm text-slate-600">Upload a file on the left, then start a conversation</p>
      </div>
      <div className="flex flex-wrap justify-center gap-2 max-w-sm">
        {EXAMPLES.map((q) => (
          <button
            key={q}
            onClick={() => onExample(q)}
            className="px-3 py-1.5 rounded-full text-xs text-slate-400 hover:text-slate-200 transition-colors border border-white/8 hover:border-white/20"
            style={{ background: 'rgba(255,255,255,0.03)' }}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function ChatPanel({ hasDocs, config = {}, onQueryComplete }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)
  const streamingIdRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 120) + 'px'
  }, [input])

  const submit = useCallback(async (query) => {
    const q = (query || input).trim()
    if (!q || streaming) return
    setInput('')
    setError('')

    const userMsg = { id: newId(), role: 'user', content: q }
    const aId = newId()
    streamingIdRef.current = aId
    setMessages(prev => [...prev, userMsg, { id: aId, role: 'assistant', content: '', sources: null, metadata: null }])
    setStreaming(true)

    const startTime = Date.now()
    try {
      let finalMetadata = null
      for await (const event of streamQuery(q, { topK: config.topK, provider: config.provider || undefined })) {
        if (event.type === 'documents') {
          setMessages(prev => prev.map(m => m.id === aId
            ? { ...m, sources: { count: event.count || 0, documents: event.documents || [] } } : m))
        } else if (event.type === 'token') {
          setMessages(prev => prev.map(m => m.id === aId
            ? { ...m, content: m.content + (event.content || '') } : m))
        } else if (event.type === 'done') {
          finalMetadata = event.metadata || null
          setMessages(prev => prev.map(m => m.id === aId
            ? { ...m, metadata: finalMetadata } : m))
        }
      }
      onQueryComplete?.({
        query: q,
        provider: finalMetadata?.provider_used || null,
        totalMs: finalMetadata?.total_ms || (Date.now() - startTime),
        timestamp: new Date(),
      })
    } catch (e) {
      setError(e.message || 'Something went wrong. Please try again.')
      setMessages(prev => prev.filter(m => m.id !== aId))
    } finally {
      setStreaming(false)
      streamingIdRef.current = null
    }
  }, [input, streaming, config, onQueryComplete])

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit() }
  }

  return (
    <div className="flex flex-col h-full min-h-0">
      {error && (
        <div className="shrink-0 mx-4 mt-4 px-4 py-2.5 rounded-xl text-sm text-red-300 flex items-start justify-between gap-2"
          style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
          <span>{error}</span>
          <button onClick={() => setError('')} className="text-red-400 hover:text-red-200 shrink-0">✕</button>
        </div>
      )}

      <div className="flex-1 min-h-0 overflow-y-auto scrollbar-thin px-6 py-6">
        {messages.length === 0
          ? <EmptyState onExample={(q) => submit(q)} />
          : (
            <div className="space-y-5 max-w-2xl mx-auto">
              {messages.map((msg) => {
                const isStreaming = streaming && msg.id === streamingIdRef.current
                return msg.role === 'user'
                  ? <UserMessage key={msg.id} message={msg} />
                  : <AssistantMessage key={msg.id} message={msg} streaming={isStreaming} />
              })}
              <div ref={bottomRef} />
            </div>
          )
        }
      </div>

      {/* Input */}
      <div className="shrink-0 px-6 py-4">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-end gap-3 rounded-2xl px-4 py-3 transition-all"
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.09)' }}
            onFocus={() => {}} // handled by CSS
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={streaming}
              placeholder={hasDocs ? 'Ask a question about your documents…' : 'Upload a document to get started…'}
              rows={1}
              className="flex-1 bg-transparent resize-none text-sm text-slate-100 placeholder-slate-600 focus:outline-none leading-6 max-h-28 disabled:opacity-50"
            />
            <button
              onClick={() => submit()}
              disabled={streaming || !input.trim()}
              className="shrink-0 w-8 h-8 rounded-xl flex items-center justify-center transition-all disabled:opacity-30"
              style={{ background: 'linear-gradient(135deg, #6366f1, #7c3aed)' }}
              aria-label="Send"
            >
              {streaming
                ? <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                : <svg className="w-3.5 h-3.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
              }
            </button>
          </div>
          <p className="text-center text-[10px] text-slate-700 mt-2">Enter to send · Shift+Enter for newline</p>
        </div>
      </div>
    </div>
  )
}
