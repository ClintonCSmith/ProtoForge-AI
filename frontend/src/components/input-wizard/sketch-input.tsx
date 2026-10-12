'use client'

import React, { useRef, useState, useEffect } from 'react'
import { 
  Pencil, 
  Eraser, 
  Trash2, 
  Undo, 
  Download, 
  Camera, 
  Image as ImageIcon,
  MousePointer2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useWizardStore } from '@/lib/store/use-wizard-store'
import { Badge } from '@/components/ui/badge'

export function SketchInput() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [color, setColor] = useState('#3b82f6')
  const [brushSize, setBrushSize] = useState(3)
  const [mode, setMode] = useState<'pencil' | 'eraser'>('pencil')
  const { setSketchData } = useWizardStore()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    ctx.strokeStyle = color
    ctx.lineWidth = brushSize

    const handleResize = () => {
      const parent = canvas.parentElement
      if (parent) {
        const temp = ctx.getImageData(0, 0, canvas.width, canvas.height)
        canvas.width = parent.clientWidth
        canvas.height = parent.clientHeight
        ctx.putImageData(temp, 0, 0)
        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [color, brushSize])

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const rect = canvas.getBoundingClientRect()
    const x = ('touches' in e) ? e.touches[0].clientX - rect.left : e.clientX - rect.left
    const y = ('touches' in e) ? e.touches[0].clientY - rect.top : e.clientY - rect.top

    ctx.beginPath()
    ctx.moveTo(x, y)
    setIsDrawing(true)
  }

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const rect = canvas.getBoundingClientRect()
    const x = ('touches' in e) ? e.touches[0].clientX - rect.left : e.clientX - rect.left
    const y = ('touches' in e) ? e.touches[0].clientY - rect.top : e.clientY - rect.top

    ctx.globalCompositeOperation = mode === 'eraser' ? 'destination-out' : 'source-over'
    ctx.lineTo(x, y)
    ctx.stroke()
  }

  const stopDrawing = () => {
    setIsDrawing(false)
    if (canvasRef.current) {
      setSketchData(canvasRef.current.toDataURL())
    }
  }

  const clear = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    setSketchData(null)
  }

  return (
    <div className="space-y-4 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 p-1 rounded-xl border border-slate-200 dark:border-slate-800">
          <Button 
            variant={mode === 'pencil' ? 'secondary' : 'ghost'} 
            size="sm" 
            className="h-8 w-8 p-0" 
            onClick={() => setMode('pencil')}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button 
            variant={mode === 'eraser' ? 'secondary' : 'ghost'} 
            size="sm" 
            className="h-8 w-8 p-0" 
            onClick={() => setMode('eraser')}
          >
            <Eraser className="h-4 w-4" />
          </Button>
          <div className="h-4 w-[1px] bg-slate-300 dark:bg-slate-700 mx-1" />
          <div className="flex gap-1 px-2">
            {['#000000', '#3b82f6', '#ef4444', '#22c55e'].map(c => (
              <button
                key={c}
                className={`w-4 h-4 rounded-full border border-white/20 transition-transform ${color === c ? 'scale-125 ring-2 ring-blue-500/20' : 'hover:scale-110'}`}
                style={{ backgroundColor: c }}
                onClick={() => {
                  setColor(c)
                  setMode('pencil')
                }}
              />
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="h-9 gap-2">
            <Camera className="h-4 w-4" />
            Photo
          </Button>
          <Button variant="outline" size="sm" className="h-9 gap-2">
            <ImageIcon className="h-4 w-4" />
            Import
          </Button>
          <div className="h-8 w-[1px] bg-slate-200 dark:bg-slate-800 mx-1" />
          <Button variant="ghost" size="sm" className="h-9 w-9 p-0 hover:text-red-500" onClick={clear}>
            <Trash2 className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" className="h-9 w-9 p-0">
            <Undo className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="relative aspect-video w-full bg-white dark:bg-slate-950 border-2 border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-inner cursor-crosshair">
        <canvas
          ref={canvasRef}
          className="w-full h-full touch-none"
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
        <div className="absolute top-4 right-4 pointer-events-none">
          <Badge variant="outline" className="bg-white/50 backdrop-blur-sm text-[10px] uppercase font-mono">
            Interactive Pad
          </Badge>
        </div>
        {!isDrawing && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
            <div className="text-center">
              <MousePointer2 className="h-12 w-12 mx-auto mb-2" />
              <p className="text-sm font-medium">Draw your 2D sketch here</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
