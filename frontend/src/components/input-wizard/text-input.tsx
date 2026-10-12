'use client'

import React from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { useWizardStore } from '@/lib/store/use-wizard-store'
import { Lightbulb } from 'lucide-react'

const SUGGESTIONS = [
  "Create a drone frame",
  "Design a phone case",
  "Model a gear assembly"
]

export function TextInput() {
  const { textInput, setTextInput } = useWizardStore()

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="space-y-2">
        <Textarea 
          placeholder="Describe your product in detail... e.g., 'An ergonomic bicycle water bottle holder that mounts to the frame, made of matte black aluminum, with a quick-release mechanism'"
          className="min-h-[200px] text-lg p-6 bg-white dark:bg-slate-950 border-2 focus:border-blue-500 transition-colors"
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
        />
        <div className="flex justify-between items-center px-1">
          <p className="text-xs text-muted-foreground">
            {textInput.length < 50 ? (
              <span className="text-amber-500 font-medium">Minimum 50 characters for better results ({textInput.length}/50)</span>
            ) : (
              <span className="text-green-500 font-medium">Description length optimal ({textInput.length} chars)</span>
            )}
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-slate-500">
          <Lightbulb className="h-3 w-3" />
          Quick Starts
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => setTextInput(s)}
              className="text-left p-4 rounded-xl border bg-slate-50 dark:bg-slate-900 hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all text-sm font-medium"
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
