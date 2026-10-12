'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, History, GitBranch, ArrowRightLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

const MOCK_VERSIONS = [
  { v: 1, date: '2026-06-12', thumbnail: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=200', notes: 'Initial design from text prompt' },
  { v: 2, date: '2026-06-13', thumbnail: 'https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?auto=format&fit=crop&q=80&w=200', notes: 'Added mounting holes and rounded edges', active: true },
]

export function RevisionPanel({ projectId }: { projectId: string }) {
  return (
    <div className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800 py-3 px-6 overflow-x-auto">
      <div className="max-w-[1400px] mx-auto flex items-center gap-6">
        <div className="flex items-center gap-2 pr-6 border-r border-slate-200 dark:border-slate-800 flex-shrink-0">
          <History className="h-4 w-4 text-slate-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">History</span>
        </div>

        <div className="flex gap-4 items-center">
          {MOCK_VERSIONS.map((version) => (
            <button
              key={version.v}
              className={`flex items-center gap-3 p-1 pr-4 rounded-xl border-2 transition-all group flex-shrink-0 ${
                version.active 
                ? 'bg-white dark:bg-slate-950 border-blue-500 shadow-sm' 
                : 'bg-slate-100 dark:bg-slate-800 border-transparent hover:border-slate-300 dark:hover:border-slate-700'
              }`}
            >
              <div className="w-10 h-10 rounded-lg overflow-hidden border border-slate-200 dark:border-slate-800">
                <img src={version.thumbnail} alt={`v${version.v}`} className="w-full h-full object-cover" />
              </div>
              <div className="text-left">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold ${version.active ? 'text-blue-600' : 'text-slate-600'}`}>v0.{version.v}</span>
                  {version.active && <Badge className="h-4 px-1 text-[8px] bg-blue-100 text-blue-600 hover:bg-blue-100 border-none uppercase">Latest</Badge>}
                </div>
                <div className="flex items-center gap-1 text-[9px] text-slate-400">
                  <Calendar className="h-2.5 w-2.5" />
                  {version.date}
                </div>
              </div>
            </button>
          ))}

          <Button variant="ghost" size="sm" className="h-12 border-2 border-dashed border-slate-300 dark:border-slate-800 text-slate-400 hover:text-blue-500 rounded-xl px-4 flex flex-col items-center justify-center gap-0">
            <ArrowRightLeft className="h-4 w-4" />
            <span className="text-[8px] uppercase font-bold">Compare</span>
          </Button>
        </div>
      </div>
    </div>
  )
}
