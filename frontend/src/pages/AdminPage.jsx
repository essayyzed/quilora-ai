import { useState, useEffect, useCallback, useRef } from 'react'
import { getHealth, getConfig, listDocuments, uploadDocument, deleteDocument, deleteAllDocuments } from '../api.js'

const TABS = ['Health', 'Documents', 'Configuration', 'Analytics']

// ── Shared helpers ──────────────────────────────────────────────────────────

function Card({ children, className = '' }) {
  return (
    <div className={`rounded-xl p-4 ${className}`}
      style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)' }}>
      {children}
    </div>
  )
}

function SectionLabel({ children }) {
  return <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-600 mb-3">{children}</p>
}

function StatusDot({ status }) {
  const color = status === 'healthy' ? 'bg-emerald-400' : status === 'unhealthy' ? 'bg-red-500' : 'bg-slate-600'
  return (
    <span className="relative flex h-2 w-2 shrink-0">
      {status === 'healthy' && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-30" />}
      <span className={`relative inline-flex rounded-full h-2 w-2 ${color}`} />
    </span>
  )
}

function statusPill(status) {
  if (status === 'healthy') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
  if (status === 'unhealthy') return 'bg-red-500/10 text-red-400 border-red-500/20'
  return 'bg-slate-500/10 text-slate-500 border-slate-500/20'
}

function formatUptime(seconds) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}h ${m}m ${s}s`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

function formatTimeAgo(date) {
  const secs = Math.floor((Date.now() - new Date(date)) / 1000)
  if (secs < 60) return `${secs}s ago`
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  return `${Math.floor(secs / 3600)}h ago`
}

const EXT_COLORS = {
  pdf: 'text-red-400 bg-red-400/10',
  docx: 'text-blue-400 bg-blue-400/10', doc: 'text-blue-400 bg-blue-400/10',
  xlsx: 'text-emerald-400 bg-emerald-400/10', xls: 'text-emerald-400 bg-emerald-400/10',
  pptx: 'text-orange-400 bg-orange-400/10',
  csv: 'text-teal-400 bg-teal-400/10',
  json: 'text-yellow-400 bg-yellow-400/10',
  yaml: 'text-pink-400 bg-pink-400/10', yml: 'text-pink-400 bg-pink-400/10',
  html: 'text-violet-400 bg-violet-400/10', htm: 'text-violet-400 bg-violet-400/10',
  md: 'text-slate-300 bg-slate-300/10',
  txt: 'text-slate-400 bg-slate-400/10',
}

function ExtBadge({ filename }) {
  const ext = filename?.split('.').pop()?.toLowerCase() || 'txt'
  const color = EXT_COLORS[ext] || 'text-slate-400 bg-slate-400/10'
  return (
    <span className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${color} shrink-0`}>
      {ext}
    </span>
  )
}

// ── Health Tab ──────────────────────────────────────────────────────────────

function HealthTab() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(null)

  const refresh = useCallback(async () => {
    try {
      const data = await getHealth()
      setHealth(data)
      setLastRefresh(new Date())
    } catch {
      // keep stale data on error
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, 10_000)
    return () => clearInterval(id)
  }, [refresh])

  if (loading) return <div className="text-center py-20 text-slate-600 text-sm">Loading health data…</div>
  if (!health) return <div className="text-center py-20 text-red-400 text-sm">Failed to reach backend</div>

  const providers = health.providers || {}

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <p className="text-[10px] uppercase tracking-wider text-slate-600 mb-2.5">API Status</p>
          <div className="flex items-center gap-2 mb-1.5">
            <StatusDot status={health.status === 'healthy' ? 'healthy' : 'unhealthy'} />
            <span className="text-sm font-semibold text-slate-200 capitalize">{health.status}</span>
          </div>
          <p className="text-[11px] text-slate-600">Version {health.api_version}</p>
        </Card>
        <Card>
          <p className="text-[10px] uppercase tracking-wider text-slate-600 mb-2.5">Vector Store</p>
          <div className="flex items-center gap-2 mb-1.5">
            <StatusDot status={health.qdrant === 'connected' ? 'healthy' : 'unhealthy'} />
            <span className="text-sm font-semibold text-slate-200 capitalize">{health.qdrant}</span>
          </div>
          <p className="text-[11px] text-slate-600">{health.document_count} chunks · {health.qdrant_collection}</p>
        </Card>
        <Card>
          <p className="text-[10px] uppercase tracking-wider text-slate-600 mb-2.5">Uptime</p>
          <p className="text-sm font-semibold text-slate-200">{formatUptime(health.uptime || 0)}</p>
          {lastRefresh && (
            <p className="text-[11px] text-slate-600 mt-1">Refreshed {formatTimeAgo(lastRefresh)}</p>
          )}
        </Card>
      </div>

      <div>
        <SectionLabel>LLM Providers</SectionLabel>
        <div className="space-y-2.5">
          {Object.entries(providers).map(([name, p]) => (
            <Card key={name}>
              <div className="flex items-start gap-3">
                <StatusDot status={p.status} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span className="text-sm font-medium text-slate-200 capitalize">{name}</span>
                    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border capitalize ${statusPill(p.status)}`}>
                      {p.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-2 flex-wrap">
                    <span className="text-[11px] text-slate-500">{p.total_requests} requests</span>
                    <span className="text-[11px] text-slate-500">{p.failed_requests} errors</span>
                    <span className={`text-[11px] font-medium ${p.error_rate > 0 ? 'text-red-400' : 'text-slate-500'}`}>
                      {(p.error_rate * 100).toFixed(0)}% error rate
                    </span>
                    {p.last_success && (
                      <span className="text-[11px] text-slate-600">
                        Last success: {new Date(p.last_success).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                  {p.last_error && (
                    <p className="mt-1.5 text-[10px] text-red-400/80 font-mono truncate">{p.last_error.slice(0, 120)}</p>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── Documents Tab ───────────────────────────────────────────────────────────

function DocumentsTab() {
  const [docs, setDocs] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [uploading, setUploading] = useState(false)
  const [deletingId, setDeletingId] = useState(null)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const fetchDocs = useCallback(async () => {
    try {
      const data = await listDocuments()
      const list = data.documents || []
      const seen = new Set()
      setDocs(list.filter(d => {
        const key = d.metadata?.filename || d.id
        if (seen.has(key)) return false
        seen.add(key); return true
      }))
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchDocs() }, [fetchDocs])

  const filtered = docs.filter(d =>
    (d.metadata?.filename || '').toLowerCase().includes(search.toLowerCase())
  )

  async function handleFile(file) {
    setUploading(true); setError('')
    try { await uploadDocument(file); await fetchDocs() }
    catch (e) { setError(e.message || 'Upload failed') }
    finally { setUploading(false) }
  }

  async function handleDelete(id) {
    setDeletingId(id)
    try { await deleteDocument(id); await fetchDocs() }
    catch (e) { setError(e.message) }
    finally { setDeletingId(null) }
  }

  async function handleClearAll() {
    if (!window.confirm(`Remove all ${docs.length} document${docs.length !== 1 ? 's' : ''}? This cannot be undone.`)) return
    try { await deleteAllDocuments(); await fetchDocs() }
    catch (e) { setError(e.message) }
  }

  return (
    <div className="space-y-4">
      <input ref={fileInputRef} type="file" className="hidden"
        accept=".txt,.md,.rst,.pdf,.docx,.xlsx,.xls,.pptx,.csv,.json,.yaml,.yml,.html,.htm"
        onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f); e.target.value = '' }}
        disabled={uploading}
      />

      {/* Action bar */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => !uploading && fileInputRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium text-white transition-all disabled:opacity-50"
          style={{ background: 'linear-gradient(135deg, #6366f1, #7c3aed)' }}
        >
          {uploading
            ? <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            : <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
              </svg>
          }
          {uploading ? 'Uploading…' : 'Upload'}
        </button>

        <div className="flex-1 relative">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search documents…"
            className="w-full pl-9 pr-3 py-2 rounded-lg text-xs text-slate-300 placeholder-slate-600 focus:outline-none"
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
          />
        </div>

        {docs.length > 0 && (
          <button onClick={handleClearAll} className="px-3 py-2 rounded-lg text-xs text-slate-600 hover:text-red-400 transition-colors"
            style={{ border: '1px solid rgba(255,255,255,0.07)' }}>
            Clear all ({docs.length})
          </button>
        )}
      </div>

      {error && (
        <div className="px-3 py-2 rounded-lg text-xs text-red-300 flex items-start justify-between gap-2"
          style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
          <span>{error}</span>
          <button onClick={() => setError('')} className="text-red-400 hover:text-red-200 shrink-0">✕</button>
        </div>
      )}

      {/* Stats bar */}
      {!loading && (
        <div className="flex items-center gap-4 text-[11px] text-slate-600 px-1">
          <span>{docs.length} document{docs.length !== 1 ? 's' : ''}</span>
          {search && <span>· {filtered.length} match{filtered.length !== 1 ? 'es' : ''}</span>}
        </div>
      )}

      {/* Document list */}
      {loading ? (
        <div className="text-center py-16 text-slate-600 text-sm">Loading…</div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16">
          <svg className="w-10 h-10 text-slate-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
          </svg>
          <p className="text-sm text-slate-600">{search ? 'No documents match your search' : 'No documents yet'}</p>
        </div>
      ) : (
        <div className="space-y-1.5">
          {filtered.map(doc => {
            const filename = doc.metadata?.filename || 'Unnamed'
            const isDeleting = deletingId === doc.id
            return (
              <div key={doc.id}
                className="group flex items-center gap-3 px-3.5 py-3 rounded-xl transition-colors"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}
                onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.06)' }}
                onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.03)' }}
              >
                <ExtBadge filename={filename} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-slate-300 font-medium truncate">{filename}</p>
                  {doc.content_preview && (
                    <p className="text-[10px] text-slate-600 truncate mt-0.5">{doc.content_preview.slice(0, 100)}</p>
                  )}
                </div>
                {doc.chunk_count != null && (
                  <span className="shrink-0 text-[10px] text-slate-600">{doc.chunk_count} chunks</span>
                )}
                <button
                  onClick={() => handleDelete(doc.id)}
                  disabled={isDeleting}
                  title="Remove"
                  className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-slate-600 hover:text-red-400 disabled:opacity-30 ml-1"
                >
                  {isDeleting
                    ? <span className="block w-3.5 h-3.5 border border-slate-500 border-t-transparent rounded-full animate-spin" />
                    : <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" /><path d="M10 11v6M14 11v6" />
                      </svg>
                  }
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ── Configuration Tab ───────────────────────────────────────────────────────

function ConfigTab({ config, onConfigChange }) {
  const [serverConfig, setServerConfig] = useState(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getConfig().then(setServerConfig).catch(() => {})
  }, [])

  function handleTopK(value) {
    onConfigChange({ topK: Number(value) })
  }

  function handleProvider(value) {
    onConfigChange({ provider: value === 'auto' ? null : value })
  }

  function flashSaved() {
    setSaved(true)
    setTimeout(() => setSaved(false), 1500)
  }

  const selectedProvider = config.provider || 'auto'
  const topK = config.topK ?? 5

  const serverRow = (label, value) => (
    <div key={label} className="flex items-center justify-between py-2.5 border-b last:border-0"
      style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
      <span className="text-xs text-slate-500">{label}</span>
      <span className="text-xs font-mono text-slate-300">{String(value)}</span>
    </div>
  )

  return (
    <div className="space-y-6">
      <div>
        <SectionLabel>Session Overrides</SectionLabel>
        <p className="text-xs text-slate-600 mb-4">Saved in your browser and applied to all queries while this tab is open.</p>
        <Card className="space-y-6">
          {/* Top-K */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-xs font-medium text-slate-300">Retrieval Top-K</p>
                <p className="text-[11px] text-slate-600 mt-0.5">How many document chunks to retrieve per query</p>
              </div>
              <span className="text-sm font-bold text-indigo-400 tabular-nums w-6 text-right">{topK}</span>
            </div>
            <input
              type="range" min={1} max={20} step={1}
              value={topK}
              onChange={e => { handleTopK(e.target.value); flashSaved() }}
              className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
              style={{ accentColor: '#6366f1', background: `linear-gradient(to right, #6366f1 ${((topK - 1) / 19) * 100}%, rgba(255,255,255,0.1) 0%)` }}
            />
            <div className="flex justify-between text-[10px] text-slate-700 mt-1">
              <span>1</span><span>10</span><span>20</span>
            </div>
          </div>

          {/* Provider override */}
          <div>
            <p className="text-xs font-medium text-slate-300 mb-1">Provider Override</p>
            <p className="text-[11px] text-slate-600 mb-3">Force a specific LLM for all queries, or let the router decide</p>
            <div className="flex gap-2 flex-wrap">
              {['auto', 'openai', 'groq', 'anthropic'].map(p => (
                <button
                  key={p}
                  onClick={() => { handleProvider(p); flashSaved() }}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
                    selectedProvider === p
                      ? 'text-white'
                      : 'text-slate-500 hover:text-slate-300'
                  }`}
                  style={selectedProvider === p
                    ? { background: 'linear-gradient(135deg, #6366f1, #7c3aed)' }
                    : { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }
                  }
                >
                  {p === 'auto' ? '✦ Auto' : p}
                </button>
              ))}
            </div>
          </div>

          {saved && (
            <p className="text-[11px] text-emerald-400">✓ Saved</p>
          )}
        </Card>
      </div>

      {serverConfig && (
        <div>
          <SectionLabel>Server Configuration</SectionLabel>
          <p className="text-xs text-slate-600 mb-4">Current values loaded from <code className="text-violet-400">.env</code>. Changes require a server restart.</p>
          <Card className="divide-y divide-white/5">
            {[
              ['Chunk Size', `${serverConfig.chunk_size} tokens`],
              ['Chunk Overlap', `${serverConfig.chunk_overlap} tokens`],
              ['Default Top-K', serverConfig.retrieval_top_k],
              ['Similarity Threshold', serverConfig.min_similarity_score],
              ['LLM Temperature', serverConfig.llm_temperature],
              ['Max Tokens', serverConfig.llm_max_tokens],
              ['Provider Strategy', serverConfig.llm_provider_strategy],
              ['Primary Provider', serverConfig.primary_llm_provider],
              ['Fallback Provider', serverConfig.fallback_llm_provider],
              ['Premium Provider', serverConfig.premium_llm_provider],
              ['Embedding Model', serverConfig.embedding_model],
              ['Max File Size', `${serverConfig.max_file_size_mb} MB`],
            ].map(([label, value]) => serverRow(label, value))}
          </Card>
        </div>
      )}
    </div>
  )
}

// ── Analytics Tab ───────────────────────────────────────────────────────────

function AnalyticsTab({ queries }) {
  const totalQueries = queries.length
  const avgMs = totalQueries
    ? Math.round(queries.reduce((s, q) => s + (q.totalMs || 0), 0) / totalQueries)
    : 0

  const providerCounts = {}
  queries.forEach(q => {
    if (q.provider) providerCounts[q.provider] = (providerCounts[q.provider] || 0) + 1
  })
  const topProvider = Object.entries(providerCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '—'

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <p className="text-[10px] uppercase tracking-wider text-slate-600 mb-2">Queries</p>
          <p className="text-3xl font-bold text-slate-100 tabular-nums">{totalQueries}</p>
          <p className="text-[11px] text-slate-600 mt-1">this session</p>
        </Card>
        <Card>
          <p className="text-[10px] uppercase tracking-wider text-slate-600 mb-2">Avg Response</p>
          <p className="text-3xl font-bold text-slate-100 tabular-nums">
            {avgMs > 0 ? (avgMs / 1000).toFixed(1) : '—'}
            {avgMs > 0 && <span className="text-lg font-normal text-slate-500 ml-1">s</span>}
          </p>
        </Card>
        <Card>
          <p className="text-[10px] uppercase tracking-wider text-slate-600 mb-2">Top Provider</p>
          <p className="text-3xl font-bold text-slate-100 truncate">{topProvider}</p>
          {topProvider !== '—' && (
            <p className="text-[11px] text-slate-600 mt-1">{providerCounts[topProvider]} queries</p>
          )}
        </Card>
      </div>

      {Object.keys(providerCounts).length > 0 && (
        <div>
          <SectionLabel>Provider Breakdown</SectionLabel>
          <Card className="space-y-3">
            {Object.entries(providerCounts).sort((a, b) => b[1] - a[1]).map(([name, count]) => {
              const pct = Math.round((count / totalQueries) * 100)
              return (
                <div key={name}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-slate-300 capitalize">{name}</span>
                    <span className="text-xs text-slate-500">{count} ({pct}%)</span>
                  </div>
                  <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.07)' }}>
                    <div className="h-full rounded-full" style={{ width: `${pct}%`, background: 'linear-gradient(90deg, #6366f1, #7c3aed)' }} />
                  </div>
                </div>
              )
            })}
          </Card>
        </div>
      )}

      <div>
        <SectionLabel>Query History</SectionLabel>
        {queries.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-sm text-slate-600">No queries yet this session</p>
            <p className="text-[11px] text-slate-700 mt-1">Go back to chat and ask something</p>
          </div>
        ) : (
          <div className="space-y-2">
            {[...queries].reverse().map((q, i) => (
              <Card key={i}>
                <div className="flex items-start gap-3">
                  <span className="shrink-0 text-[10px] text-slate-700 tabular-nums mt-0.5 w-4 text-right">{queries.length - i}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-slate-300 leading-relaxed">{q.query}</p>
                    <div className="flex items-center gap-3 mt-1.5 flex-wrap">
                      {q.provider && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full border text-indigo-400 bg-indigo-500/10 border-indigo-500/20 capitalize">{q.provider}</span>
                      )}
                      {q.totalMs && (
                        <span className="text-[10px] text-slate-600">{(q.totalMs / 1000).toFixed(1)}s</span>
                      )}
                      <span className="text-[10px] text-slate-700">{formatTimeAgo(q.timestamp)}</span>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Main AdminPage ──────────────────────────────────────────────────────────

function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-500/20 shrink-0">
        <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
        </svg>
      </div>
      <span className="text-sm font-semibold text-white">Quilora AI</span>
    </div>
  )
}

export default function AdminPage({ onBack, sessionQueries = [], config = {}, onConfigChange }) {
  const [tab, setTab] = useState('Health')

  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col" style={{ background: '#08080f' }}>
      {/* Header */}
      <div className="shrink-0 flex items-center justify-between px-6 h-14 border-b"
        style={{ background: '#0e0e1a', borderColor: '#1e1e2e' }}>
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors py-1.5 px-2.5 rounded-lg hover:bg-white/5"
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Back to Chat
          </button>
          <span className="text-slate-700 text-sm">·</span>
          <span className="text-sm font-medium text-slate-400">Admin Panel</span>
        </div>
        <Logo />
      </div>

      {/* Tab bar */}
      <div className="shrink-0 flex items-center gap-0 px-6 border-b" style={{ background: '#0e0e1a', borderColor: '#1e1e2e' }}>
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-3.5 text-xs font-medium transition-colors border-b-2 -mb-px ${
              tab === t
                ? 'text-indigo-400 border-indigo-500'
                : 'text-slate-500 border-transparent hover:text-slate-300 hover:border-slate-600'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 min-h-0 overflow-y-auto scrollbar-thin">
        <div className="max-w-3xl mx-auto px-6 py-7">
          {tab === 'Health' && <HealthTab />}
          {tab === 'Documents' && <DocumentsTab />}
          {tab === 'Configuration' && <ConfigTab config={config} onConfigChange={onConfigChange} />}
          {tab === 'Analytics' && <AnalyticsTab queries={sessionQueries} />}
        </div>
      </div>
    </div>
  )
}
