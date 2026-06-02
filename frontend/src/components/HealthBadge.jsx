import { useState, useEffect } from 'react'
import { getHealth } from '../api.js'

export default function HealthBadge() {
  const [status, setStatus] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function check() {
      try {
        const data = await getHealth()
        if (!cancelled) setStatus(data.status === 'healthy' ? 'healthy' : 'unhealthy')
      } catch {
        if (!cancelled) setStatus('unhealthy')
      }
    }
    check()
    const id = setInterval(check, 10_000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])

  if (status === null) return (
    <span className="w-1.5 h-1.5 rounded-full bg-slate-600 inline-block" />
  )

  return (
    <div className="flex items-center gap-1.5" title={`Backend ${status}`}>
      <span className="relative flex h-2 w-2">
        {status === 'healthy' && (
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-30" />
        )}
        <span className={`relative inline-flex rounded-full h-2 w-2 ${status === 'healthy' ? 'bg-emerald-400' : 'bg-red-500'}`} />
      </span>
    </div>
  )
}
