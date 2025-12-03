'use client'

import { useEffect, useState } from 'react'
import { StatsCard } from '@/components/StatsCard'
import { CSVUpload } from '@/components/CSVUpload'
import { Button } from '@/components/ui/button'
import { getStats, startConnections } from '@/lib/api'
import type { Stats } from '@/lib/api'

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState(false)

  const fetchStats = async () => {
    try {
      const data = await getStats()
      setStats(data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleStartConnections = async () => {
    setStarting(true)
    try {
      await startConnections()
      await fetchStats()
      alert('Connection process started!')
    } catch (error) {
      alert('Failed to start connections: ' + (error instanceof Error ? error.message : 'Unknown error'))
    } finally {
      setStarting(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  if (!stats) {
    return <div className="text-center py-8">Failed to load stats</div>
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="flex gap-4">
          <CSVUpload onUploadComplete={fetchStats} />
          <Button onClick={handleStartConnections} disabled={starting}>
            {starting ? 'Starting...' : 'Start Connections'}
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Profiles"
          value={stats.total_profiles}
          description="Profiles imported from CSV"
        />
        <StatsCard
          title="Connections Sent"
          value={stats.total_connections}
          description="Connection requests sent"
        />
        <StatsCard
          title="Connected"
          value={stats.connections_connected}
          description="Successfully connected"
        />
        <StatsCard
          title="Response Rate"
          value={`${stats.response_rate}%`}
          description="Follow-up engagement rate"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <StatsCard
          title="Pending"
          value={stats.connections_pending}
          description="Awaiting connection"
        />
        <StatsCard
          title="Failed"
          value={stats.connections_failed}
          description="Connection attempts failed"
        />
        <StatsCard
          title="Total Messages"
          value={stats.total_messages}
          description={`${stats.initial_messages} initial, ${stats.followup_messages} follow-ups`}
        />
      </div>

      <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
        <h3 className="font-semibold text-yellow-800 mb-2">Important Notice</h3>
        <p className="text-sm text-yellow-700">
          This tool automates LinkedIn interactions. Please ensure you comply with LinkedIn's Terms of Service.
          Use rate limiting and be respectful of other users. Automated actions may result in account restrictions.
        </p>
      </div>
    </div>
  )
}



