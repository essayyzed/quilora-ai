import { useState, useEffect, useRef } from 'react'
import { listDocuments, uploadDocument, deleteDocument, deleteAllDocuments } from '../api.js'

function TrashIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6M14 11v6" />
      <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
    </svg>
  )
}

function UploadIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  )
}

function FileIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 shrink-0 text-gray-500" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  )
}

export default function DocumentPanel({ onDocsChange }) {
  const [docs, setDocs] = useState([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState(null)
  const fileInputRef = useRef(null)

  async function fetchDocs() {
    try {
      const data = await listDocuments()
      setDocs(data.documents || [])
      onDocsChange?.(data.documents?.length > 0)
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => {
    fetchDocs()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleFileChange(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError('')
    try {
      await uploadDocument(file)
      await fetchDocs()
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
      // reset input so same file can be re-uploaded
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  async function handleDelete(id) {
    setDeletingId(id)
    setError('')
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
    const confirmed = window.confirm(
      `Delete all ${docs.length} document${docs.length !== 1 ? 's' : ''}? This cannot be undone.`
    )
    if (!confirmed) return
    setError('')
    try {
      await deleteAllDocuments()
      await fetchDocs()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="flex flex-col flex-1 min-h-0 p-3 gap-3">
      {/* Upload button */}
      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.rst,.pdf,.docx,.xlsx,.xls,.pptx,.csv,.json,.yaml,.yml,.html,.htm"
          className="hidden"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg
            bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
            text-white text-sm font-medium transition-colors"
        >
          <UploadIcon />
          {uploading ? 'Uploading…' : 'Upload Document'}
        </button>

        {/* Upload progress indicator */}
        {uploading && (
          <div className="mt-2 w-full h-1 bg-gray-700 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full animate-pulse w-full" />
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="px-3 py-2 rounded-lg bg-red-950 border border-red-800 text-red-300 text-xs">
          {error}
          <button onClick={() => setError('')} className="ml-2 text-red-400 hover:text-red-200">✕</button>
        </div>
      )}

      {/* Docs list */}
      <div className="flex-1 min-h-0 overflow-y-auto space-y-1.5 pr-0.5">
        {docs.length === 0 && !uploading && (
          <p className="text-gray-500 text-xs text-center mt-4">No documents yet</p>
        )}
        {docs.map((doc) => {
          const filename = doc.metadata?.filename || doc.metadata?.source || 'Unnamed'
          const preview = doc.content_preview || ''
          const isDeleting = deletingId === doc.id

          return (
            <div
              key={doc.id}
              className="group flex items-start gap-2 p-2.5 rounded-lg bg-gray-800 border border-gray-700
                hover:border-gray-600 transition-colors"
            >
              <FileIcon />
              <div className="flex-1 min-w-0">
                <p className="text-gray-100 text-xs font-medium truncate leading-tight">{filename}</p>
                {preview && (
                  <p className="text-gray-500 text-xs mt-0.5 line-clamp-2 leading-relaxed">{preview}</p>
                )}
              </div>
              <button
                onClick={() => handleDelete(doc.id)}
                disabled={isDeleting}
                title="Delete document"
                className="shrink-0 p-1 rounded text-gray-600 hover:text-red-400 hover:bg-red-950
                  disabled:opacity-40 transition-colors opacity-0 group-hover:opacity-100"
              >
                {isDeleting ? (
                  <span className="block w-4 h-4 border-2 border-gray-500 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <TrashIcon />
                )}
              </button>
            </div>
          )
        })}
      </div>

      {/* Clear all */}
      {docs.length > 0 && (
        <button
          onClick={handleClearAll}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg
            bg-gray-700 hover:bg-red-600 text-gray-300 hover:text-white text-xs font-medium
            transition-colors border border-gray-600 hover:border-red-500"
        >
          <TrashIcon />
          Clear all ({docs.length})
        </button>
      )}
    </div>
  )
}
