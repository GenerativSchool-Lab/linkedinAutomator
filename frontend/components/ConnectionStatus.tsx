'use client'

import { useEffect, useState } from 'react'
import { getConnections } from '@/lib/api'
import type { Connection } from '@/lib/api'
import { StatusBadge } from './StatusBadge'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Progress } from './ui/progress'

interface ConnectionStatusProps {
  refreshInterval?: number // in seconds
}

export function ConnectionStatus({ refreshInterval = 10 }: ConnectionStatusProps) {
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)

  const fetchConnections = async () => {
    try {
      const data = await getConnections()
      setConnections(data)
    } catch (error) {
      console.error('Failed to fetch connections:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConnections()
    const interval = setInterval(fetchConnections, refreshInterval * 1000)
    return () => clearInterval(interval)
  }, [refreshInterval])

  const statusCounts = {
    pending: connections.filter(c => c.status === 'pending').length,
    connecting: connections.filter(c => c.status === 'connecting').length,
    connected: connections.filter(c => c.status === 'connected').length,
    failed: connections.filter(c => c.status === 'failed').length,
  }

  const total = connections.length
  const completed = statusCounts.connected + statusCounts.failed
  const progress = total > 0 ? (completed / total) * 100 : 0

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Connection Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4 text-muted-foreground">Loading...</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Connection Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Overall Progress</span>
            <span className="font-medium">{completed} / {total}</span>
          </div>
          <Progress value={progress} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Pending</div>
            <div className="text-2xl font-bold">{statusCounts.pending}</div>
          </div>
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Connecting</div>
            <div className="text-2xl font-bold text-blue-600">{statusCounts.connecting}</div>
          </div>
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Connected</div>
            <div className="text-2xl font-bold text-green-600">{statusCounts.connected}</div>
          </div>
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Failed</div>
            <div className="text-2xl font-bold text-red-600">{statusCounts.failed}</div>
          </div>
        </div>

        {connections.length > 0 && (
          <div className="pt-4 border-t">
            <div className="text-sm font-medium mb-2">Recent Connections</div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {connections.slice(0, 5).map((connection) => (
                <div key={connection.id} className="flex items-center justify-between text-sm">
                  <span className="truncate flex-1">{connection.profile_name}</span>
                  <StatusBadge status={connection.status} />
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

