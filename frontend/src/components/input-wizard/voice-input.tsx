'use client'

import React, { useState, useRef, useEffect } from 'react'
import RecordRTC from 'recordrtc'
import { Mic, Square, Play, RotateCcw, Volume2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useWizardStore } from '@/lib/store/use-wizard-store'
import { Badge } from '@/components/ui/badge'

export function VoiceInput() {
  const { setAudioBlob } = useWizardStore()
  const [isRecording, setIsRecording] = useState(false)
  const [recorder, setRecorder] = useState<RecordRTC | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [duration, setDuration] = useState(0)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const newRecorder = new RecordRTC(stream, { type: 'audio' })
    newRecorder.startRecording()
    setRecorder(newRecorder)
    setIsRecording(true)
    setDuration(0)
    
    intervalRef.current = setInterval(() => {
      setDuration(prev => prev + 1)
    }, 1000)
  }

  const stopRecording = () => {
    if (recorder) {
      recorder.stopRecording(() => {
        const blob = recorder.getBlob()
        setAudioBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
        setIsRecording(false)
        if (intervalRef.current) clearInterval(intervalRef.current)
      })
    }
  }

  const resetRecording = () => {
    setAudioUrl(null)
    setAudioBlob(null)
    setDuration(0)
  }

  // Simple waveform animation mock
  useEffect(() => {
    if (isRecording && canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d')
      if (!ctx) return
      
      let animationId: number
      const render = () => {
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height)
        ctx.fillStyle = '#3b82f6'
        for (let i = 0; i < 50; i++) {
          const h = Math.random() * ctx.canvas.height * 0.8
          ctx.fillRect(i * 6, (ctx.canvas.height - h) / 2, 4, h)
        }
        animationId = requestAnimationFrame(render)
      }
      render()
      return () => cancelAnimationFrame(animationId)
    }
  }, [isRecording])

  return (
    <div className="flex flex-col items-center justify-center space-y-8 py-12 animate-in fade-in zoom-in-95 duration-500">
      <div className="relative">
        <div className={`absolute inset-0 rounded-full bg-blue-500/20 blur-2xl transition-all duration-500 ${isRecording ? 'scale-150 opacity-100' : 'scale-100 opacity-0'}`} />
        
        {audioUrl ? (
          <div className="relative bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 p-8 rounded-3xl flex flex-col items-center gap-4 w-64 shadow-xl">
            <Volume2 className="h-12 w-12 text-blue-500" />
            <div className="text-center">
              <p className="font-bold">Recording Saved</p>
              <p className="text-xs text-muted-foreground">Approx. 1.2MB</p>
            </div>
            <audio src={audioUrl} controls className="h-8 w-full" />
            <Button variant="ghost" size="sm" className="text-slate-500 hover:text-red-500 gap-2" onClick={resetRecording}>
              <RotateCcw className="h-3 w-3" />
              Re-record
            </Button>
          </div>
        ) : (
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`relative h-32 w-32 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl ${
              isRecording 
              ? 'bg-red-500 hover:bg-red-600 scale-110' 
              : 'bg-blue-600 hover:bg-blue-700 hover:scale-105'
            }`}
          >
            {isRecording ? (
              <Square className="h-10 w-10 text-white fill-white" />
            ) : (
              <Mic className="h-10 w-10 text-white" />
            )}
            
            {isRecording && (
              <div className="absolute -bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
                <Badge className="bg-red-500 animate-pulse border-none">RECORDING</Badge>
                <span className="font-mono text-xl font-bold">
                  {Math.floor(duration / 60)}:{(duration % 60).toString().padStart(2, '0')}
                </span>
              </div>
            )}
          </button>
        )}
      </div>

      {isRecording && (
        <canvas 
          ref={canvasRef} 
          width={300} 
          height={60} 
          className="rounded-lg opacity-50"
        />
      )}

      {!audioUrl && !isRecording && (
        <div className="text-center space-y-2">
          <p className="text-lg font-bold">Describe your idea verbally</p>
          <p className="text-sm text-muted-foreground max-w-xs mx-auto">
            Speak clearly about materials, dimensions, and usage. Max recording: 2 minutes.
          </p>
        </div>
      )}
    </div>
  )
}
