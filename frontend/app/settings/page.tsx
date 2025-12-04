'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { getSettings, updateSettings } from '@/lib/api'
import toast from 'react-hot-toast'

interface Settings {
  company_name: string | null
  company_description: string | null
  value_proposition: string | null
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    company_name: null,
    company_description: null,
    value_proposition: null,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const fetchSettings = async () => {
    setLoading(true)
    try {
      const data = await getSettings()
      setSettings(data)
    } catch (error) {
      toast.error('Failed to load settings: ' + (error instanceof Error ? error.message : 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [])

  const handleSave = async () => {
    setSaving(true)
    const loadingToast = toast.loading('Saving settings...')
    
    try {
      await updateSettings(settings)
      toast.success('Settings saved successfully!', { id: loadingToast })
    } catch (error) {
      toast.error('Failed to save settings: ' + (error instanceof Error ? error.message : 'Unknown error'), {
        id: loadingToast
      })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Settings</h1>
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>

      <div className="space-y-6">
        <div className="p-6 border rounded-lg space-y-4">
          <h2 className="text-xl font-semibold">Company Information</h2>
          <p className="text-sm text-muted-foreground">
            Configurez les informations de votre entreprise pour personnaliser les messages de connexion.
          </p>

          <div className="space-y-4">
            <div>
              <label htmlFor="company_name" className="block text-sm font-medium mb-2">
                Company Name
              </label>
              <input
                id="company_name"
                type="text"
                value={settings.company_name || ''}
                onChange={(e) => setSettings({ ...settings, company_name: e.target.value || null })}
                placeholder="e.g., Chyll.ai"
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label htmlFor="company_description" className="block text-sm font-medium mb-2">
                Company Description
              </label>
              <textarea
                id="company_description"
                value={settings.company_description || ''}
                onChange={(e) => setSettings({ ...settings, company_description: e.target.value || null })}
                placeholder="Décrivez ce que fait votre entreprise..."
                rows={4}
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Description de votre entreprise qui sera utilisée pour personnaliser les messages
              </p>
            </div>

            <div>
              <label htmlFor="value_proposition" className="block text-sm font-medium mb-2">
                Value Proposition
              </label>
              <textarea
                id="value_proposition"
                value={settings.value_proposition || ''}
                onChange={(e) => setSettings({ ...settings, value_proposition: e.target.value || null })}
                placeholder="Votre proposition de valeur unique..."
                rows={3}
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Votre proposition de valeur qui sera mentionnée subtilement dans les messages
              </p>
            </div>
          </div>
        </div>

        <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
          <h3 className="font-semibold text-blue-800 mb-2">How it works</h3>
          <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
            <li>Ces informations sont utilisées par l'IA pour personnaliser les messages de connexion</li>
            <li>Les messages créent des liens naturels entre le profil du contact et votre entreprise</li>
            <li>Les changements prennent effet immédiatement pour les nouvelles connexions</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

