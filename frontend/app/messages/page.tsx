'use client'

import { useEffect, useState } from 'react'
import { getMessages, sendFollowUp } from '@/lib/api'
import type { Message } from '@/lib/api'
import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import { format } from 'date-fns'
import Link from 'next/link'

export default function MessagesPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [messageTypeFilter, setMessageTypeFilter] = useState<string>('')
  const [connectionIdFilter, setConnectionIdFilter] = useState<string>('')

  const fetchMessages = async () => {
    setLoading(true)
    try {
      const data = await getMessages(
        connectionIdFilter ? parseInt(connectionIdFilter) : undefined,
        messageTypeFilter || undefined
      )
      setMessages(data)
    } catch (error) {
      console.error('Failed to fetch messages:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMessages()
  }, [messageTypeFilter, connectionIdFilter])

  const handleSendFollowUp = async (connectionId: number) => {
    try {
      await sendFollowUp(connectionId)
      alert('Follow-up message queued!')
      fetchMessages()
    } catch (error) {
      alert('Failed to send follow-up: ' + (error instanceof Error ? error.message : 'Unknown error'))
    }
  }

  // Group messages by connection
  const groupedMessages = messages.reduce((acc, msg) => {
    if (!acc[msg.connection_id]) {
      acc[msg.connection_id] = []
    }
    acc[msg.connection_id].push(msg)
    return acc
  }, {} as Record<number, Message[]>)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Messages</h1>
      </div>

      <div className="flex gap-4 items-center">
        <div>
          <label className="text-sm font-medium mr-2">Type:</label>
          <select
            value={messageTypeFilter}
            onChange={(e) => setMessageTypeFilter(e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="">All</option>
            <option value="initial">Initial</option>
            <option value="followup">Follow-up</option>
          </select>
        </div>
        <div>
          <label className="text-sm font-medium mr-2">Connection ID:</label>
          <input
            type="number"
            value={connectionIdFilter}
            onChange={(e) => setConnectionIdFilter(e.target.value)}
            placeholder="Filter by connection ID"
            className="border rounded-md px-3 py-2"
          />
        </div>
        <Button onClick={fetchMessages} variant="outline">
          Refresh
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedMessages).map(([connectionId, msgs]) => (
            <div key={connectionId} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-semibold">{msgs[0].profile_name}</h3>
                  <Link
                    href={msgs[0].profile_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline"
                  >
                    View Profile
                  </Link>
                </div>
                <Button
                  onClick={() => handleSendFollowUp(parseInt(connectionId))}
                  variant="outline"
                  size="sm"
                >
                  Send Follow-up
                </Button>
              </div>
              <div className="space-y-3">
                {msgs.map((msg) => (
                  <div key={msg.id} className="border-l-2 border-primary pl-4">
                    <div className="flex items-center gap-2 mb-1">
                      <StatusBadge status={msg.message_type} />
                      <span className="text-sm text-muted-foreground">
                        {format(new Date(msg.sent_at), 'PPp')}
                      </span>
                    </div>
                    <p className="text-sm">{msg.content}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
          {messages.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No messages found
            </div>
          )}
        </div>
      )}
    </div>
  )
}



