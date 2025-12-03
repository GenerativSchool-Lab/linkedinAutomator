'use client'

import { useState } from 'react'
import { Button } from './ui/button'
import { uploadCSV } from '@/lib/api'

interface CSVUploadProps {
  onUploadComplete?: () => void
}

export function CSVUpload({ onUploadComplete }: CSVUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<{ message: string; profiles_created: number; errors: string[] } | null>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setResult(null)

    try {
      const response = await uploadCSV(file)
      setResult(response)
      if (onUploadComplete) {
        onUploadComplete()
      }
    } catch (error) {
      setResult({
        message: 'Upload failed',
        profiles_created: 0,
        errors: [error instanceof Error ? error.message : 'Unknown error']
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <label htmlFor="csv-upload" className="cursor-pointer">
          <span className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
            {uploading ? 'Uploading...' : 'Upload CSV'}
          </span>
        </label>
        <input
          id="csv-upload"
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="hidden"
          disabled={uploading}
        />
      </div>
      {result && (
        <div className={`p-4 rounded-md ${result.profiles_created > 0 ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
          <p className="font-medium">{result.message}</p>
          {result.profiles_created > 0 && (
            <p className="text-sm mt-1">Successfully imported {result.profiles_created} profiles</p>
          )}
          {result.errors.length > 0 && (
            <div className="mt-2">
              <p className="text-sm font-medium">Errors:</p>
              <ul className="text-sm list-disc list-inside">
                {result.errors.map((error, idx) => (
                  <li key={idx}>{error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}



