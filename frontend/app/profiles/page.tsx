'use client'

import { useEffect, useState } from 'react'
import { getProfiles, startConnections } from '@/lib/api'
import type { Profile } from '@/lib/api'
import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

export default function ProfilesPage() {
  const router = useRouter()
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [companyFilter, setCompanyFilter] = useState<string>('')
  const [selectedProfiles, setSelectedProfiles] = useState<Set<number>>(new Set())
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)
  const [starting, setStarting] = useState(false)

  const fetchProfiles = async () => {
    setLoading(true)
    try {
      const data = await getProfiles(statusFilter || undefined, companyFilter || undefined)
      setProfiles(data)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch profiles'
      toast.error(errorMessage)
      console.error('Failed to fetch profiles:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProfiles()
  }, [statusFilter, companyFilter])

  const toggleProfileSelection = (profileId: number) => {
    setSelectedProfiles(prev => {
      const newSet = new Set(prev)
      if (newSet.has(profileId)) {
        newSet.delete(profileId)
      } else {
        newSet.add(profileId)
      }
      return newSet
    })
  }

  const selectAll = () => {
    const pendingProfiles = profiles.filter(p => !p.connection_status || p.connection_status === 'pending')
    setSelectedProfiles(new Set(pendingProfiles.map(p => p.id)))
  }

  const clearSelection = () => {
    setSelectedProfiles(new Set())
  }

  const handleStartSelectedConnections = () => {
    if (selectedProfiles.size === 0) {
      toast.error('Please select at least one profile to connect')
      return
    }
    setShowConfirmDialog(true)
  }

  const handleConfirmStart = async () => {
    setShowConfirmDialog(false)
    setStarting(true)
    
    const profileIds = Array.from(selectedProfiles)
    const loadingToast = toast.loading(`Starting connections for ${profileIds.length} profile${profileIds.length > 1 ? 's' : ''}...`)
    
    try {
      await startConnections(profileIds)
      toast.success(`Connection process started for ${profileIds.length} profile${profileIds.length > 1 ? 's' : ''}!`, {
        id: loadingToast
      })
      clearSelection()
      fetchProfiles()
      router.push('/')
    } catch (error) {
      toast.error('Failed to start connections: ' + (error instanceof Error ? error.message : 'Unknown error'), {
        id: loadingToast
      })
    } finally {
      setStarting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Profiles</h1>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex gap-4 items-center flex-wrap">
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
          <div>
            <label className="text-sm font-medium mr-2">Company:</label>
            <input
              type="text"
              value={companyFilter}
              onChange={(e) => setCompanyFilter(e.target.value)}
              placeholder="Filter by company"
              className="border rounded-md px-3 py-2"
            />
          </div>
          <Button onClick={fetchProfiles} variant="outline">
            Refresh
          </Button>
        </div>
        {selectedProfiles.size > 0 && (
          <div className="flex items-center gap-2 p-3 bg-muted rounded-md">
            <span className="text-sm font-medium">{selectedProfiles.size} profile{selectedProfiles.size > 1 ? 's' : ''} selected</span>
            <Button variant="outline" size="sm" onClick={clearSelection}>
              Clear Selection
            </Button>
            <Button size="sm" onClick={handleStartSelectedConnections} disabled={starting}>
              {starting ? 'Starting...' : `Start Connections (${selectedProfiles.size})`}
            </Button>
          </div>
        )}
      </div>

      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium w-12">
                  <input
                    type="checkbox"
                    onChange={(e) => e.target.checked ? selectAll() : clearSelection()}
                    checked={selectedProfiles.size > 0 && selectedProfiles.size === profiles.filter(p => !p.connection_status || p.connection_status === 'pending').length}
                    className="rounded"
                  />
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Title</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Company</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {profiles.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                    No profiles found
                  </td>
                </tr>
              ) : (
                profiles.map((profile) => {
                  const isSelectable = !profile.connection_status || profile.connection_status === 'pending'
                  const isSelected = selectedProfiles.has(profile.id)
                  return (
                    <tr key={profile.id} className={`border-t ${isSelected ? 'bg-muted/50' : ''}`}>
                      <td className="px-4 py-3">
                        {isSelectable && (
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleProfileSelection(profile.id)}
                            className="rounded"
                          />
                        )}
                      </td>
                      <td className="px-4 py-3">{profile.name}</td>
                      <td className="px-4 py-3">{profile.title || '-'}</td>
                      <td className="px-4 py-3">{profile.company || '-'}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={profile.connection_status || 'pending'} />
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <Link
                            href={profile.linkedin_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline text-sm"
                          >
                            View Profile
                          </Link>
                          <Link
                            href="/messages"
                            className="text-primary hover:underline text-sm"
                          >
                            Messages
                          </Link>
                        </div>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Start Connection Process?</DialogTitle>
            <DialogDescription>
              You are about to start sending connection requests to {selectedProfiles.size} selected profile{selectedProfiles.size > 1 ? 's' : ''}.
              This action will begin the automated connection process.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-muted-foreground">
              The system will:
            </p>
            <ul className="list-disc list-inside text-sm text-muted-foreground mt-2 space-y-1">
              <li>Generate personalized connection messages using AI</li>
              <li>Send connection requests with rate limiting (45s delay between requests)</li>
              <li>Track connection status and messages</li>
              <li>Schedule automatic follow-ups after 7 days</li>
            </ul>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleConfirmStart} disabled={starting}>
              Start Connections
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}




