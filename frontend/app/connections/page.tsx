'use client'

import { useEffect, useState } from 'react'
import { getConnections } from '@/lib/api'
import type { Connection } from '@/lib/api'
import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import { format } from 'date-fns'
import Link from 'next/link'
import toast from 'react-hot-toast'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [selectedMessage, setSelectedMessage] = useState<Connection | null>(null)

  const fetchConnections = async () => {
    setLoading(true)
    try {
      const data = await getConnections(statusFilter || undefined)
      setConnections(data)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch connections'
      toast.error(errorMessage)
      console.error('Failed to fetch connections:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConnections()
    const interval = setInterval(fetchConnections, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [statusFilter])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Connections</h1>
        <Button onClick={fetchConnections} variant="outline" disabled={loading}>
          Refresh
        </Button>
      </div>

      <div className="flex gap-4 items-center">
        <div>
          <label className="text-sm font-medium mr-2">Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="connecting">Connecting</option>
            <option value="connected">Connected</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Profile</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Connection Message</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Connected At</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {connections.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                    No connections found
                  </td>
                </tr>
              ) : (
                connections.map((connection) => (
                  <tr key={connection.id} className="border-t">
                    <td className="px-4 py-3">
                      <div>
                        <div className="font-medium">{connection.profile_name}</div>
                        <Link
                          href={connection.profile_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary hover:underline"
                        >
                          View Profile
                        </Link>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="space-y-1">
                        <StatusBadge status={connection.status} />
                        {connection.status === 'failed' && connection.failure_reason && (
                          <div className="text-xs text-red-600 mt-1" title={connection.failure_reason}>
                            {connection.failure_reason.length > 50
                              ? `${connection.failure_reason.substring(0, 50)}...`
                              : connection.failure_reason}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {connection.connection_message ? (
                        <div>
                          <button
                            onClick={() => setSelectedMessage(connection)}
                            className="text-sm text-primary hover:underline text-left max-w-md truncate block"
                          >
                            {connection.connection_message.length > 50
                              ? `${connection.connection_message.substring(0, 50)}...`
                              : connection.connection_message}
                          </button>
                          {connection.connection_message_sent_at && (
                            <div className="text-xs text-muted-foreground mt-1">
                              {format(new Date(connection.connection_message_sent_at), 'PPp')}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-muted-foreground">No message sent</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {connection.connected_at ? (
                        <span className="text-sm">
                          {format(new Date(connection.connected_at), 'PPp')}
                        </span>
                      ) : (
                        <span className="text-sm text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <Link
                          href={`/messages?connection_id=${connection.id}`}
                          className="text-primary hover:underline text-sm"
                        >
                          View Messages
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={!!selectedMessage} onOpenChange={() => setSelectedMessage(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Connection Message</DialogTitle>
            <DialogDescription>
              Message sent to {selectedMessage?.profile_name}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            {selectedMessage?.connection_message ? (
              <div className="space-y-2">
                <div className="p-4 bg-muted rounded-md">
                  <p className="text-sm whitespace-pre-wrap">{selectedMessage.connection_message}</p>
                </div>
                {selectedMessage.connection_message_sent_at && (
                  <div className="text-xs text-muted-foreground">
                    Sent: {format(new Date(selectedMessage.connection_message_sent_at), 'PPp')}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-muted-foreground">No message available</p>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

