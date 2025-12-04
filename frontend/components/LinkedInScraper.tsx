'use client'

import { useState } from 'react'
import { Button } from './ui/button'
import { Progress } from './ui/progress'
import { scrapeLinkedInSearch } from '@/lib/api'
import { Search, Link as LinkIcon } from 'lucide-react'
import toast from 'react-hot-toast'

interface LinkedInScraperProps {
  onScrapeComplete?: () => void
}

export function LinkedInScraper({ onScrapeComplete }: LinkedInScraperProps) {
  const [searchUrl, setSearchUrl] = useState('')
  const [scraping, setScraping] = useState(false)
  const [progress, setProgress] = useState(0)
  const [maxResults, setMaxResults] = useState(50)

  const validateUrl = (url: string): string | null => {
    if (!url.trim()) {
      return 'Please enter a LinkedIn search URL'
    }
    
    if (!url.includes('linkedin.com/search')) {
      return 'Please enter a valid LinkedIn search URL (must contain linkedin.com/search)'
    }
    
    return null
  }

  const handleScrape = async () => {
    const validationError = validateUrl(searchUrl)
    if (validationError) {
      toast.error(validationError)
      return
    }

    setScraping(true)
    setProgress(0)

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 500)

    try {
      const response = await scrapeLinkedInSearch(searchUrl, maxResults)
      
      clearInterval(progressInterval)
      setProgress(100)

      if (response.profiles_created > 0) {
        toast.success(`Successfully scraped ${response.profiles_created} profile${response.profiles_created > 1 ? 's' : ''}`)
        if (response.errors.length > 0) {
          toast.error(`${response.errors.length} error${response.errors.length > 1 ? 's' : ''} occurred`, {
            duration: 5000
          })
        }
        setSearchUrl('') // Clear input on success
      } else {
        toast.error('No profiles were scraped. Please check the search URL and try again.')
        if (response.errors.length > 0) {
          response.errors.forEach((error) => {
            toast.error(error, { duration: 4000 })
          })
        }
      }

      if (onScrapeComplete) {
        onScrapeComplete()
      }

      setTimeout(() => {
        setProgress(0)
      }, 2000)
    } catch (error) {
      setProgress(0)
      const errorMessage = error instanceof Error ? error.message : 'Failed to scrape LinkedIn search'
      toast.error(errorMessage)
    } finally {
      setScraping(false)
    }
  }

  return (
    <div className="space-y-4 p-6 border rounded-lg bg-card">
      <div className="flex items-center gap-2">
        <Search className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold">Scrape LinkedIn Search</h3>
      </div>
      
      <div className="space-y-3">
        <div>
          <label htmlFor="search-url" className="block text-sm font-medium mb-2">
            LinkedIn Search URL
          </label>
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <LinkIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                id="search-url"
                type="text"
                value={searchUrl}
                onChange={(e) => setSearchUrl(e.target.value)}
                placeholder="https://www.linkedin.com/search/results/people/..."
                className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                disabled={scraping}
              />
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Paste a LinkedIn search results URL (people search)
          </p>
        </div>

        <div>
          <label htmlFor="max-results" className="block text-sm font-medium mb-2">
            Maximum Results
          </label>
          <input
            id="max-results"
            type="number"
            min="1"
            max="100"
            value={maxResults}
            onChange={(e) => setMaxResults(Math.min(100, Math.max(1, parseInt(e.target.value) || 50)))}
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={scraping}
          />
          <p className="text-xs text-muted-foreground mt-1">
            Number of profiles to scrape (1-100)
          </p>
        </div>

        {scraping && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">Scraping profiles...</span>
              <span className="text-muted-foreground">{progress}%</span>
            </div>
            <Progress value={progress} />
          </div>
        )}

        <Button
          onClick={handleScrape}
          disabled={scraping || !searchUrl.trim()}
          className="w-full"
        >
          {scraping ? 'Scraping...' : 'Scrape Profiles'}
        </Button>
      </div>

      <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
        <p className="text-xs text-yellow-800">
          <strong>Note:</strong> You must be logged into LinkedIn for this to work. 
          Make sure your LinkedIn credentials are configured in the backend.
        </p>
      </div>
    </div>
  )
}

