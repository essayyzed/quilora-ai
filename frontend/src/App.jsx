import { useState } from 'react'
import HealthBadge from './components/HealthBadge.jsx'
import DocumentPanel from './components/DocumentPanel.jsx'
import ChatPanel from './components/ChatPanel.jsx'

export default function App() {
  const [hasDocs, setHasDocs] = useState(false)

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gray-950 text-white">
      {/* Left sidebar */}
      <aside className="w-72 shrink-0 flex flex-col bg-gray-900 border-r border-gray-800">
        {/* Sidebar header */}
        <div className="shrink-0 px-4 py-5 border-b border-gray-800">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h1 className="text-lg font-semibold text-white tracking-tight leading-tight">
                Quilora AI
              </h1>
              <p className="text-xs text-gray-400 mt-0.5 leading-relaxed">
                RAG-powered document Q&amp;A
              </p>
            </div>
            <div className="pt-0.5">
              <HealthBadge />
            </div>
          </div>
        </div>

        {/* Documents section header */}
        <div className="shrink-0 px-4 pt-4 pb-2">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Documents
          </h2>
        </div>

        {/* Document panel — fills remaining sidebar space */}
        <div className="flex-1 min-h-0 flex flex-col">
          <DocumentPanel onDocsChange={setHasDocs} />
        </div>
      </aside>

      {/* Right chat area */}
      <main className="flex-1 min-w-0 flex flex-col">
        <ChatPanel hasDocs={hasDocs} />
      </main>
    </div>
  )
}
