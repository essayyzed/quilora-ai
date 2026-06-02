import { useState, useEffect, useRef } from 'react'
import { listDocuments, uploadDocument, deleteDocument, deleteAllDocuments } from '../api.js'

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

function UploadZone({ onFile, uploading }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) onFile(file)
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !uploading && inputRef.current?.click()}
      className={`
        relative cursor-pointer rounded-xl border-2 border-dashed px-3 py-4
        flex flex-col items-center gap-2 transition-all duration-150 select-none
        ${dragging
          ? 'border-indigo-500 bg-indigo-500/10'
          : 'border-slate-700 hover:border-slate-500 hover:bg-white/[0.02]'}
        ${uploading ? 'opacity-60 cursor-not-allowed' : ''}
      `}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept=".txt,.md,.rst,.pdf,.docx,.xlsx,.xls,.pptx,.csv,.json,.yaml,.yml,.html,.htm"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); e.target.value = '' }}
        disabled={uploading}
      />

      {uploading ? (
        <span className="w-5 h-5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
      ) : (
        <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center">
          <svg className="w-4 h-4 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>
      )}

      <div className="text-center">
        <p className="text-xs font-medium text-slate-300">
          {uploading ? 'Uploading…' : 'Drop file or click to upload'}
        </p>
        <p className="text-[10px] text-slate-600 mt-0.5">PDF, DOCX, XLSX, CSV, MD + more</p>
      </div>
    </div>
  )
}

export default function DocumentPanel({ onDocsChange }) {
  const [docs, setDocs] = useState([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState(null)

  async function fetchDocs() {
    try {
      const data = await listDocuments()
      const list = data.documents || []
      // dedupe by filename so each uploaded file shows once
      const seen = new Set()
      const unique = list.filter((d) => {
        const key = d.metadata?.filename || d.id
        if (seen.has(key)) return false
        seen.add(key)
        return true
      })
      setDocs(unique)
      onDocsChange?.(unique.length > 0)
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => { fetchDocs() }, []) // eslint-disable-line

  async function handleFile(file) {
    setUploading(true)
    setError('')
    try {
      await uploadDocument(file)
      await fetchDocs()
    } catch (e) {
      setError(e.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  async function handleDelete(id) {
    setDeletingId(id)
    try {
      await deleteDocument(id)
      await fetchDocs()
    } catch (e) {
      setError(e.message)
    } finally {
      setDeletingId(null)
    }
  }

  async function handleClearAll() {
    if (!window.confirm(`Remove all ${docs.length} document${docs.length !== 1 ? 's' : ''}? This cannot be undone.`)) return
    try {
      await deleteAllDocuments()
      await fetchDocs()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="flex flex-col flex-1 min-h-0 px-3 pb-3 gap-3">
      <UploadZone onFile={handleFile} uploading={uploading} />

      {error && (
        <div className="px-3 py-2 rounded-lg text-xs text-red-300 flex items-start justify-between gap-2"
          style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
          <span>{error}</span>
          <button onClick={() => setError('')} className="text-red-400 hover:text-red-200 shrink-0 leading-none">✕</button>
        </div>
      )}

      <div className="flex-1 min-h-0 overflow-y-auto scrollbar-thin space-y-1.5">
        {docs.length === 0 && !uploading && (
          <div className="flex flex-col items-center gap-2 py-8 text-center">
            <svg className="w-8 h-8 text-slate-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <p className="text-xs text-slate-600">No documents yet</p>
          </div>
        )}

        {docs.map((doc) => {
          const filename = doc.metadata?.filename || 'Unnamed'
          const isDeleting = deletingId === doc.id
          return (
            <div
              key={doc.id}
              className="group flex items-center gap-2.5 px-2.5 py-2 rounded-lg transition-colors"
              style={{ background: 'rgba(255,255,255,0.03)' }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
              onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
            >
              <ExtBadge filename={filename} />
              <p className="flex-1 min-w-0 text-xs text-slate-300 truncate leading-tight">{filename}</p>
              <button
                onClick={() => handleDelete(doc.id)}
                disabled={isDeleting}
                title="Remove"
                className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-slate-600 hover:text-red-400 disabled:opacity-30"
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

      {docs.length > 0 && (
        <button
          onClick={handleClearAll}
          className="w-full text-[11px] text-slate-600 hover:text-red-400 transition-colors py-1"
        >
          Clear all ({docs.length})
        </button>
      )}
    </div>
  )
}
