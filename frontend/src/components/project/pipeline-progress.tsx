'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Check, Loader2, X, ChevronDown, ChevronUp } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

const STAGES = [
  { id: 'Parse', label: 'Parse Intent', agent: 'IntentParserAgent' },
  { id: 'Draw', label: 'Generate Drawings', agent: 'DrawingGeneratorAgent' },
  { id: 'Model', label: 'Synthesize 3D Model', agent: 'ModelSynthesizerAgent' },
  { id: 'Render', label: '4K Rendering', agent: 'RenderEngineAgent' },
  { id: 'Animate', label: 'Create Animation', agent: 'AnimationAgent' },
  { id: 'XR', label: 'Prepare WebXR', agent: 'XRAgent' },
  { id: 'Simulate', label: 'FEA Simulation', agent: 'SimulationAgent' },
  { id: 'BOM', label: 'Generate BOM', agent: 'BOMAgent' },
  { id: 'Validate', label: 'Final Validation', agent: 'Finalizer' },
]

interface Event {
  event: string
  agent: string
  progress_pct: number
  timestamp: string
  message?: string
}

export function PipelineProgress({ projectId, jobId }: { projectId: string; jobId?: string }) {
  const [events, setEvents] = useState<Event[]>([])
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const [completedAgents, setCompletedAgents] = useState<Set<string>>(new Set())
  const [failedAgents, setFailedAgents] = useState<Set<string>>(new Set())
  const [overallProgress, setOverallProgress] = useState(0)
  const [showLogs, setShowLogs] = useState(false)
  const [estimatedSeconds, setEstimatedSeconds] = useState(120)
  const logEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!jobId) return

    const eventSource = new EventSource(`http://localhost:8000/api/jobs/${jobId}/stream`)

    eventSource.onmessage = (event) => {
      const data: Event = JSON.parse(event.data)
      setEvents((prev) => [...prev, data])
      
      if (data.event === 'agent_started') {
        setCurrentAgent(data.agent)
      } else if (data.event === 'agent_completed') {
        setCompletedAgents((prev) => new Set([...prev, data.agent]))
        setCurrentAgent(null)
      } else if (data.event === 'agent_failed') {
        setFailedAgents((prev) => new Set([...prev, data.agent]))
        setCurrentAgent(null)
      } else if (data.event === 'pipeline_complete') {
        setOverallProgress(100)
        eventSource.close()
      }

      if (data.progress_pct !== undefined) {
        setOverallProgress(data.progress_pct)
      }
    }

    eventSource.onerror = () => {
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [jobId])

  useEffect(() => {
    if (overallProgress < 100 && estimatedSeconds > 0) {
      const timer = setInterval(() => {
        setEstimatedSeconds((prev) => Math.max(0, prev - 1))
      }, 1000)
      return () => clearInterval(timer)
    }
  }, [overallProgress, estimatedSeconds])

  useEffect(() => {
    if (showLogs) {
      logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [events, showLogs])

  return (
    <Card className="border-2 shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle className="text-xl font-bold flex items-center gap-2">
            Forging Pipeline
            {overallProgress < 100 && <Loader2 className="h-4 w-4 animate-spin text-blue-500" />}
          </CardTitle>
          <div className="text-right">
            <p className="text-xs text-muted-foreground uppercase font-bold tracking-tighter">Est. Time Remaining</p>
            <p className="text-lg font-mono font-bold text-primary">
              {Math.floor(estimatedSeconds / 60)}:{(estimatedSeconds % 60).toString().padStart(2, '0')}
            </p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <div className="flex justify-between text-sm font-medium">
            <span>Overall Progress</span>
            <span>{overallProgress}%</span>
          </div>
          <Progress value={overallProgress} className="h-2" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {STAGES.map((stage) => {
            const isDone = completedAgents.has(stage.agent)
            const isFailed = failedAgents.has(stage.agent)
            const isRunning = currentAgent === stage.agent
            
            return (
              <div 
                key={stage.id} 
                className={`p-3 rounded-lg border flex items-center justify-between transition-all ${
                  isRunning ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800 ring-1 ring-blue-400' : 
                  isDone ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800' :
                  isFailed ? 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800' :
                  'bg-slate-50 border-slate-200 dark:bg-slate-900/50 dark:border-slate-800 grayscale opacity-70'
                }`}
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className={`flex-shrink-0 w-6 h-6 rounded-md flex items-center justify-center ${
                    isRunning ? 'bg-blue-500 text-white' : 
                    isDone ? 'bg-green-500 text-white' : 
                    isFailed ? 'bg-red-500 text-white' : 
                    'bg-slate-200 dark:bg-slate-700 text-slate-500'
                  }`}>
                    {isDone ? <Check className="h-3 w-3" /> : 
                     isFailed ? <X className="h-3 w-3" /> : 
                     isRunning ? <Loader2 className="h-3 w-3 animate-spin" /> : 
                     <div className="h-1 w-1 rounded-full bg-current" />}
                  </div>
                  <span className="text-[11px] font-bold truncate">{stage.label}</span>
                </div>
                {isRunning && <Badge variant="secondary" className="text-[9px] h-4 px-1 animate-pulse ml-1">LIVE</Badge>}
              </div>
            )
          })}
        </div>

        <div className="border rounded-md overflow-hidden">
          <button 
            onClick={() => setShowLogs(!showLogs)}
            type="button"
            className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-900 flex justify-between items-center text-sm font-medium hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <span className="flex items-center gap-2">
              Pipeline Logs 
              <Badge variant="outline" className="text-[10px] font-mono">{events.length}</Badge>
            </span>
            {showLogs ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          
          {showLogs && (
            <div className="bg-slate-950 text-green-500 p-4 font-mono text-[10px] h-48 overflow-y-auto">
              {events.map((e, i) => (
                <div key={i} className="mb-1 leading-relaxed border-l border-slate-800 pl-2">
                  <span className="text-slate-500">[{e.timestamp.split(' ')[1]}]</span>{' '}
                  <span className="text-blue-400">{e.agent}</span>{' '}
                  <span className={e.event === 'agent_failed' ? 'text-red-400' : 'text-slate-300'}>
                    {e.event.toUpperCase()}
                  </span>
                  {e.message && <span className="text-white">: {e.message}</span>}
                </div>
              ))}
              {events.length === 0 && <div className="text-slate-600 italic">Waiting for pipeline events...</div>}
              <div ref={logEndRef} />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
