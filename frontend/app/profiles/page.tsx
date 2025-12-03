'use client'

import { useEffect, useState } from 'react'
import { getProfiles } from '@/lib/api'
import type { Profile } from '@/lib/api'
import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function ProfilesPage() {
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [companyFilter, setCompanyFilter] = useState<string>('')

  const fetchProfiles = async () => {
    setLoading(true)
    try {
      const data = await getProfiles(statusFilter || undefined, companyFilter || undefined)
      setProfiles(data)
    } catch (error) {
      console.error('Failed to fetch profiles:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProfiles()
  }, [statusFilter, companyFilter])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Profiles</h1>
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

      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted">
              <tr>
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
                  <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                    No profiles found
                  </td>
                </tr>
              ) : (
                profiles.map((profile) => (
                  <tr key={profile.id} className="border-t">
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
                          href={`/messages?connection_id=${profile.id}`}
                          className="text-primary hover:underline text-sm"
                        >
                          Messages
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
    </div>
  )
}



