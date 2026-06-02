import { useState, useEffect } from 'react'
import { getHealth } from '../api.js'

export default function HealthBadge() {
  const [status, setStatus] = useState(null) // null = loading, 'healthy' | 'unhealthy'

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
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  const dotColor =
    status === null ? 'bg-gray-500' :
    status === 'healthy' ? 'bg-green-400' :
    'bg-red-500'

  const label =
    status === null ? '...' :
    status === 'healthy' ? 'healthy' :
    'unhealthy'

  const textColor =
    status === null ? 'text-gray-400' :
    status === 'healthy' ? 'text-green-400' :
    'text-red-400'

  return (
    <div className="flex items-center gap-1.5">
      <span className={`inline-block w-2 h-2 rounded-full ${dotColor} shrink-0`} />
      <span className={`text-xs font-medium ${textColor}`}>{label}</span>
    </div>
  )
}
