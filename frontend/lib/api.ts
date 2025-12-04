import { API_URL } from './utils'

export interface Profile {
  id: number
  name: string
  linkedin_url: string
  company: string | null
  title: string | null
  notes: string | null
  tags: string | null
  created_at: string
  connection_status: string | null
}

export interface Connection {
  id: number
  profile_id: number
  profile_name: string
  profile_url: string
  status: string
  connected_at: string | null
  created_at: string
}

export interface Message {
  id: number
  connection_id: number
  profile_name: string
  profile_url: string
  content: string
  message_type: string
  sent_at: string
  created_at: string
}

export interface Stats {
  total_profiles: number
  total_connections: number
  connections_pending: number
  connections_connected: number
  connections_failed: number
  total_messages: number
  initial_messages: number
  followup_messages: number
  response_rate: number
}

export async function uploadCSV(file: File): Promise<{ message: string; profiles_created: number; errors: string[] }> {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${API_URL}/api/profiles/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to upload CSV: ${response.statusText}`)
    }

    return response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Network error: Failed to upload CSV file')
  }
}

export async function getProfiles(status?: string, company?: string): Promise<Profile[]> {
  const params = new URLSearchParams()
  if (status) params.append('status', status)
  if (company) params.append('company', company)

  try {
    const response = await fetch(`${API_URL}/api/profiles?${params.toString()}`)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to fetch profiles: ${response.statusText}`)
    }
    return response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Network error: Failed to fetch profiles')
  }
}

export async function getConnections(status?: string): Promise<Connection[]> {
  const params = new URLSearchParams()
  if (status) params.append('status', status)

  const response = await fetch(`${API_URL}/api/connections?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Failed to fetch connections')
  }
  return response.json()
}

export async function getMessages(connection_id?: number, message_type?: string): Promise<Message[]> {
  const params = new URLSearchParams()
  if (connection_id) params.append('connection_id', connection_id.toString())
  if (message_type) params.append('message_type', message_type)

  const response = await fetch(`${API_URL}/api/messages?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Failed to fetch messages')
  }
  return response.json()
}

export async function getStats(): Promise<Stats> {
  try {
    const response = await fetch(`${API_URL}/api/stats`)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to fetch stats: ${response.statusText}`)
    }
    return response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Network error: Failed to fetch stats')
  }
}

export async function startConnections(profile_ids?: number[]): Promise<{ message: string; profiles_count: number }> {
  try {
    const response = await fetch(`${API_URL}/api/connections/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ profile_ids }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to start connections: ${response.statusText}`)
    }

    return response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Network error: Failed to start connections')
  }
}

export async function sendFollowUp(connection_id: number): Promise<{ message: string }> {
  try {
    const response = await fetch(`${API_URL}/api/messages/send-followup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ connection_id }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to send follow-up: ${response.statusText}`)
    }

    return response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Network error: Failed to send follow-up')
  }
}

export async function scrapeLinkedInSearch(
  search_url: string,
  max_results: number = 50
): Promise<{ message: string; profiles_created: number; errors: string[] }> {
  try {
    const response = await fetch(`${API_URL}/api/profiles/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ search_url, max_results }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to scrape LinkedIn search: ${response.statusText}`)
    }

    return response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Network error: Failed to scrape LinkedIn search')
  }
}




