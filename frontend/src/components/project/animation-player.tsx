'use client'

import React, { useState, useRef } from 'react'
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Repeat, 
  Download, 
  Settings2,
  Maximize,
  Volume2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'

export function AnimationPlayer({ videoUrl }: { videoUrl?: string }) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState([0])
  const [speed, setSpeed] = useState('1')
  const [isLooping, setIsLooping] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    } else {
      setIsPlaying(!isPlaying) // Mock toggle
    }
  }

  return (
    <div className="space-y-4">
      <div className="relative aspect-video bg-black rounded-2xl overflow-hidden group border-2 border-slate-200 dark:border-slate-800 shadow-xl">
        {videoUrl ? (
          <video 
            ref={videoRef}
            src={videoUrl}
            className="w-full h-full object-contain"
            loop={isLooping}
            onTimeUpdate={(e) => {
              const current = e.currentTarget
              setProgress([(current.currentTime / current.duration) * 100])
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-slate-950">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 rounded-full bg-blue-600/20 border-2 border-blue-600/30 flex items-center justify-center mx-auto animate-pulse">
                <Play className="h-10 w-10 text-blue-500 fill-blue-500" />
              </div>
              <p className="text-slate-400 font-medium">Turntable Animation Preview</p>
              <Badge variant="outline" className="text-slate-500 border-slate-700">4K • 60FPS • MP4</Badge>
            </div>
          </div>
        )}

        {/* Overlay Controls */}
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-6 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="space-y-4">
            <Slider 
              value={progress} 
              max={100} 
              step={0.1} 
              className="cursor-pointer"
              onValueChange={setProgress}
            />
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Button size="icon" variant="ghost" className="text-white hover:bg-white/20" onClick={() => setProgress([0])}>
                  <SkipBack className="h-4 w-4" />
                </Button>
                <Button size="icon" variant="ghost" className="w-12 h-12 rounded-full bg-blue-600 hover:bg-blue-500 text-white" onClick={togglePlay}>
                  {isPlaying ? <Pause className="h-6 w-6 fill-white" /> : <Play className="h-6 w-6 fill-white" />}
                </Button>
                <Button size="icon" variant="ghost" className="text-white hover:bg-white/20">
                  <SkipForward className="h-4 w-4" />
                </Button>
                <div className="ml-4 text-xs font-mono text-slate-300">
                  0:12 / 0:30
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Select value={speed} onValueChange={setSpeed}>
                    <SelectTrigger className="w-20 h-8 text-[10px] bg-black/40 border-slate-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700 text-white">
                      <SelectItem value="0.25">0.25x</SelectItem>
                      <SelectItem value="0.5">0.5x</SelectItem>
                      <SelectItem value="1">1.0x</SelectItem>
                      <SelectItem value="1.5">1.5x</SelectItem>
                      <SelectItem value="2">2.0x</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  size="icon" 
                  variant="ghost" 
                  className={`h-8 w-8 ${isLooping ? 'text-blue-400 bg-blue-400/10' : 'text-slate-400 hover:bg-white/10'}`}
                  onClick={() => setIsLooping(!isLooping)}
                >
                  <Repeat className="h-4 w-4" />
                </Button>

                <Button size="icon" variant="ghost" className="h-8 w-8 text-slate-400 hover:bg-white/10">
                  <Volume2 className="h-4 w-4" />
                </Button>

                <Button size="icon" variant="ghost" className="h-8 w-8 text-slate-400 hover:bg-white/10">
                  <Maximize className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-dashed border-slate-300 dark:border-slate-800">
        <div>
          <h4 className="text-sm font-bold">Assembly Sequence Animation</h4>
          <p className="text-xs text-muted-foreground">Generated using Photorealistic Engine v2.4</p>
        </div>
        <Button variant="outline" size="sm" className="gap-2 border-slate-300 dark:border-slate-700">
          <Download className="h-4 w-4" />
          Download MP4
        </Button>
      </div>
    </div>
  )
}
