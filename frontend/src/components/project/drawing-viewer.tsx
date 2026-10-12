'use client'

import React, { useEffect, useRef, useState } from 'react'
import svgPanZoom from 'svg-pan-zoom'
import { 
  Maximize2, 
  Download, 
  Layers, 
  MousePointer2, 
  ZoomIn, 
  ZoomOut,
  FileOutput,
  Eye,
  EyeOff
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'

export function DrawingViewer({ projectId, drawingUrl }: { projectId: string, drawingUrl?: string }) {
  const svgWrapperRef = useRef<HTMLDivElement>(null)
  const [panZoom, setPanZoom] = useState<SvgPanZoom.Instance | null>(null)
  const [activeTab, setActiveTab] = useState('front')
  const [showAnnotations, setShowAnnotations] = useState(true)

  useEffect(() => {
    if (svgWrapperRef.current) {
      const svgElement = svgWrapperRef.current.querySelector('svg')
      if (svgElement) {
        const pz = svgPanZoom(svgElement as SVGElement, {
          zoomEnabled: true,
          controlIconsEnabled: false,
          fit: true,
          center: true,
        })
        setPanZoom(pz)
        return () => {
          pz.destroy()
        }
      }
    }
  }, [activeTab])

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full sm:w-auto">
          <TabsList className="bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <TabsTrigger value="front">Front</TabsTrigger>
            <TabsTrigger value="side">Side</TabsTrigger>
            <TabsTrigger value="top">Top</TabsTrigger>
            <TabsTrigger value="iso">Isometric</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          <Button 
            variant="outline" 
            size="sm" 
            className={`gap-2 h-9 ${showAnnotations ? 'text-blue-600 border-blue-200 bg-blue-50' : ''}`}
            onClick={() => setShowAnnotations(!showAnnotations)}
          >
            {showAnnotations ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
            Annotations
          </Button>
          <div className="h-8 w-[1px] bg-slate-200 dark:bg-slate-800 mx-1" />
          <Button variant="outline" size="sm" className="h-9 gap-2">
            <FileOutput className="h-4 w-4" />
            Export DXF
          </Button>
          <Button variant="default" size="sm" className="h-9 gap-2 bg-blue-600 hover:bg-blue-500">
            <Download className="h-4 w-4" />
            PDF
          </Button>
        </div>
      </div>

      <div className="relative aspect-[1.414/1] w-full bg-white dark:bg-slate-950 border-2 border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-inner group">
        {/* SVG Drawing Canvas */}
        <div ref={svgWrapperRef} className="w-full h-full p-8 flex items-center justify-center">
          <svg viewBox="0 0 841 594" className="w-full h-full text-slate-900 dark:text-slate-100 font-mono">
            {/* Border and Title Block */}
            <rect x="20" y="20" width="801" height="554" fill="none" stroke="currentColor" strokeWidth="2" />
            <line x1="600" y1="454" x2="821" y2="454" stroke="currentColor" strokeWidth="2" />
            <line x1="600" y1="454" x2="600" y2="574" stroke="currentColor" strokeWidth="2" />
            
            {/* Content Mock based on tab */}
            <g className="drawing-content">
              {activeTab === 'front' && (
                <path d="M200,150 L641,150 L641,400 L200,400 Z M200,200 L641,200" fill="none" stroke="currentColor" strokeWidth="1.5" />
              )}
              {activeTab === 'side' && (
                <rect x="350" y="150" width="141" height="250" fill="none" stroke="currentColor" strokeWidth="1.5" />
              )}
              {activeTab === 'top' && (
                <rect x="200" y="200" width="441" height="150" fill="none" stroke="currentColor" strokeWidth="1.5" />
              )}
              {activeTab === 'iso' && (
                <path d="M300,200 L500,150 L600,250 L400,300 Z M300,200 L300,350 L400,450 L400,300" fill="none" stroke="currentColor" strokeWidth="1.5" />
              )}
            </g>

            {/* Annotations Layer */}
            {showAnnotations && (
              <g className="annotations text-[12px] text-blue-500">
                <line x1="200" y1="130" x2="641" y2="130" stroke="currentColor" strokeWidth="1" strokeDasharray="4" />
                <path d="M200,125 L200,135 M641,125 L641,135" stroke="currentColor" strokeWidth="1" />
                <text x="400" y="120" fill="currentColor" textAnchor="middle">441.00 mm</text>
                
                <line x1="180" y1="150" x2="180" y2="400" stroke="currentColor" strokeWidth="1" strokeDasharray="4" />
                <path d="M175,150 L185,150 M175,400 L185,400" stroke="currentColor" strokeWidth="1" />
                <text x="170" y="275" fill="currentColor" textAnchor="middle" transform="rotate(-90 170,275)">250.00 mm</text>
              </g>
            )}

            {/* Title Block Text */}
            <g className="title-block text-[10px]">
              <text x="610" y="475" fill="currentColor" className="font-bold">PROJECT ID:</text>
              <text x="610" y="490" fill="currentColor">PROTO-{projectId.slice(0, 8).toUpperCase()}</text>
              <text x="610" y="515" fill="currentColor" className="font-bold">DESCRIPTION:</text>
              <text x="610" y="530" fill="currentColor">ALUMINUM BRACKET ASSEMBLY</text>
              <text x="750" y="475" fill="currentColor" className="font-bold">SHEET:</text>
              <text x="750" y="490" fill="currentColor">1 OF 1</text>
              <text x="610" y="560" fill="currentColor" className="font-bold">DATE:</text>
              <text x="650" y="560" fill="currentColor">2026-06-13</text>
              <text x="750" y="560" fill="currentColor" className="font-bold">REV:</text>
              <text x="780" y="560" fill="currentColor">B</text>
            </g>
          </svg>
        </div>

        {/* Toolbar Overlay */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-slate-900/90 backdrop-blur-md border border-slate-700 p-1 rounded-full shadow-2xl flex items-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <Button variant="ghost" size="icon" className="text-white hover:bg-white/20 h-8 w-8" onClick={() => panZoom?.zoomIn()}>
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="text-white hover:bg-white/20 h-8 w-8" onClick={() => panZoom?.zoomOut()}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <div className="w-[1px] h-4 bg-slate-700 mx-1" />
          <Button variant="ghost" size="icon" className="text-white hover:bg-white/20 h-8 w-8" onClick={() => panZoom?.reset()}>
            <Maximize2 className="h-4 w-4" />
          </Button>
          <div className="w-[1px] h-4 bg-slate-700 mx-1" />
          <Button variant="ghost" size="icon" className="text-white hover:bg-white/20 h-8 w-8">
            <MousePointer2 className="h-4 w-4" />
          </Button>
        </div>

        <div className="absolute top-6 right-6">
          <Badge variant="secondary" className="bg-slate-900/60 text-white backdrop-blur-md border-slate-700 px-3 py-1">
            ISO 128 COMPLIANT
          </Badge>
        </div>
      </div>
    </div>
  )
}
