'use client'

import React, { useState } from 'react'
import Image from 'next/image'
import { Download, ZoomIn, Maximize2, Layers } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogTrigger,
} from "@/components/ui/dialog"

const MOCK_RENDERS = [
  { id: '1', title: 'Front Isometric', url: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=800', type: 'iso' },
  { id: '2', title: 'Rear Isometric', url: 'https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?auto=format&fit=crop&q=80&w=800', type: 'iso' },
  { id: '3', title: 'Top View', url: 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&q=80&w=800', type: 'ortho' },
  { id: '4', title: 'Left View', url: 'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?auto=format&fit=crop&q=80&w=800', type: 'ortho' },
  { id: '5', title: 'Right View', url: 'https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&q=80&w=800', type: 'ortho' },
]

export function RenderGallery({ projectId }: { projectId: string }) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <Layers className="h-5 w-5 text-blue-500" />
          Photo-realistic Renders
        </h3>
        <Button variant="outline" size="sm" className="gap-2">
          <Download className="h-4 w-4" />
          Download All (ZIP)
        </Button>
      </div>

      <div className="columns-1 sm:columns-2 lg:columns-3 gap-4 space-y-4">
        {MOCK_RENDERS.map((render) => (
          <Card key={render.id} className="overflow-hidden group break-inside-avoid border-2 hover:border-blue-500 transition-all duration-300 shadow-sm">
            <CardContent className="p-0 relative">
              <Dialog>
                <DialogTrigger asChild>
                  <div className="relative cursor-zoom-in overflow-hidden">
                    <img 
                      src={render.url} 
                      alt={render.title}
                      className="w-full h-auto object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <ZoomIn className="text-white h-8 w-8" />
                    </div>
                  </div>
                </DialogTrigger>
                <DialogContent className="max-w-5xl p-0 bg-black border-none overflow-hidden">
                  <div className="relative w-full h-[80vh] flex items-center justify-center">
                    <img 
                      src={render.url} 
                      alt={render.title}
                      className="max-w-full max-h-full object-contain"
                    />
                    <div className="absolute top-4 left-4">
                      <Badge variant="secondary" className="bg-black/60 text-white backdrop-blur-md">
                        4K ULTRA HD
                      </Badge>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>

              <div className="p-4 bg-white dark:bg-slate-900 border-t flex justify-between items-center">
                <div>
                  <p className="text-sm font-bold">{render.title}</p>
                  <p className="text-[10px] text-muted-foreground uppercase font-mono">{render.type}</p>
                </div>
                <Button size="icon" variant="ghost" className="h-8 w-8 hover:bg-blue-50 hover:text-blue-600">
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
