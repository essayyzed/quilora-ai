import { useState } from 'react'
import HealthBadge from './components/HealthBadge.jsx'
import DocumentPanel from './components/DocumentPanel.jsx'
import ChatPanel from './components/ChatPanel.jsx'
import AdminPage from './pages/AdminPage.jsx'

function Logo() {
  return (
    <div className="flex items-center gap-2.5">
      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 shrink-0">
        <svg viewBox="0 0 24 24" className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
      </div>
      <div>
        <h1 className="text-sm font-semibold text-white tracking-tight leading-none">Quilora AI</h1>
        <p className="text-[10px] text-slate-500 mt-0.5 leading-none">Document Intelligence</p>
      </div>
    </div>
  )
}

export default function App() {
  const [view, setView] = useState('chat')
  const [hasDocs, setHasDocs] = useState(false)
  const [sessionQueries, setSessionQueries] = useState([])
  const [adminConfig, setAdminConfig] = useState(() => {
    try { return JSON.parse(localStorage.getItem('quilora_config') || '{}') }
    catch { return {} }
  })

  function updateConfig(updates) {
    const next = { ...adminConfig, ...updates }
    setAdminConfig(next)
    localStorage.setItem('quilora_config', JSON.stringify(next))
  }

  if (view === 'admin') {
    return (
      <AdminPage
        onBack={() => setView('chat')}
        sessionQueries={sessionQueries}
        config={adminConfig}
        onConfigChange={updateConfig}
      />
    )
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden" style={{ background: '#08080f' }}>
      {/* Sidebar */}
      <aside className="w-[260px] shrink-0 flex flex-col border-r" style={{ background: '#0e0e1a', borderColor: '#1e1e2e' }}>
        {/* Header */}
        <div className="shrink-0 px-4 py-4 flex items-center justify-between border-b" style={{ borderColor: '#1e1e2e' }}>
          <Logo />
          <HealthBadge />
        </div>

        {/* Documents label */}
        <div className="shrink-0 px-4 pt-5 pb-2 flex items-center gap-2">
          <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-600">Documents</span>
        </div>

        {/* Document panel */}
        <div className="flex-1 min-h-0 flex flex-col">
          <DocumentPanel onDocsChange={setHasDocs} />
        </div>

        {/* Admin link */}
        <div className="shrink-0 border-t px-3 py-3" style={{ borderColor: '#1e1e2e' }}>
          <button
            onClick={() => setView('admin')}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-xs text-slate-500 hover:text-slate-300 transition-all group"
            style={{ border: '1px solid transparent' }}
            onMouseEnter={e => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.04)'
              e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.borderColor = 'transparent'
            }}
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            Admin Panel
            {sessionQueries.length > 0 && (
              <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400">
                {sessionQueries.length}
              </span>
            )}
          </button>
        </div>
      </aside>

      {/* Chat */}
      <main className="flex-1 min-w-0 flex flex-col">
        <ChatPanel
          hasDocs={hasDocs}
          config={adminConfig}
          onQueryComplete={record => setSessionQueries(prev => [...prev, record])}
        />
      </main>
    </div>
  )
}
