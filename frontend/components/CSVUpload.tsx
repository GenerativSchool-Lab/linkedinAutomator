'use client'

import { useState, useRef, useCallback } from 'react'
import { Button } from './ui/button'
import { Progress } from './ui/progress'
import { uploadCSV } from '@/lib/api'
import { Upload, FileText, X } from 'lucide-react'
import toast from 'react-hot-toast'

interface CSVUploadProps {
  onUploadComplete?: () => void
}

export function CSVUpload({ onUploadComplete }: CSVUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!file.name.endsWith('.csv') && !file.type.includes('csv')) {
      return 'Please upload a CSV file'
    }
    
    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      return 'File size must be less than 10MB'
    }
    
    return null
  }

  const handleFile = useCallback(async (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      toast.error(validationError)
      return
    }

    setSelectedFile(file)
    setUploading(true)
    setProgress(0)

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      const response = await uploadCSV(file)
      
      clearInterval(progressInterval)
      setProgress(100)

      if (response.profiles_created > 0) {
        toast.success(`Successfully imported ${response.profiles_created} profile${response.profiles_created > 1 ? 's' : ''}`)
        if (response.errors.length > 0) {
          toast.error(`${response.errors.length} error${response.errors.length > 1 ? 's' : ''} occurred`, {
            duration: 5000
          })
        }
      } else {
        toast.error('No profiles were imported')
        if (response.errors.length > 0) {
          response.errors.forEach((error) => {
            toast.error(error, { duration: 4000 })
          })
        }
      }

      if (onUploadComplete) {
        onUploadComplete()
      }

      // Reset after success
      setTimeout(() => {
        setSelectedFile(null)
        setProgress(0)
      }, 2000)
    } catch (error) {
      setProgress(0)
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload CSV file'
      toast.error(errorMessage)
    } finally {
      setUploading(false)
    }
  }, [onUploadComplete])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }, [handleFile])

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }, [handleFile])

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setProgress(0)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-4">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-6 transition-colors
          ${dragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'}
          ${uploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer hover:border-primary/50'}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileInputChange}
          className="hidden"
          disabled={uploading}
        />

        {!selectedFile && !uploading && (
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="rounded-full bg-muted p-4">
              <Upload className="h-8 w-8 text-muted-foreground" />
            </div>
            <div className="text-center space-y-2">
              <p className="text-sm font-medium">
                Drag and drop your CSV file here, or
              </p>
              <Button
                type="button"
                variant="outline"
                onClick={handleButtonClick}
                disabled={uploading}
              >
                <FileText className="mr-2 h-4 w-4" />
                Browse Files
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              CSV files only, max 10MB
            </p>
          </div>
        )}

        {selectedFile && !uploading && (
          <div className="flex items-center justify-between p-3 bg-muted rounded-md">
            <div className="flex items-center space-x-2 flex-1 min-w-0">
              <FileText className="h-5 w-5 text-muted-foreground flex-shrink-0" />
              <span className="text-sm font-medium truncate">{selectedFile.name}</span>
              <span className="text-xs text-muted-foreground">
                ({(selectedFile.size / 1024).toFixed(1)} KB)
              </span>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={handleRemoveFile}
              className="h-6 w-6"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}

        {uploading && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">Uploading...</span>
              <span className="text-muted-foreground">{progress}%</span>
            </div>
            <Progress value={progress} />
            <p className="text-xs text-muted-foreground text-center">
              Processing CSV file...
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
