'use client'

import React, { useEffect, useRef, useState } from 'react'
import * as BABYLON from '@babylonjs/core'
import '@babylonjs/loaders'
import { 
  Maximize2, 
  RotateCcw, 
  Camera, 
  Ruler, 
  Layers, 
  Box, 
  Sun, 
  Smartphone,
  MessageSquare
} from 'lucide-react'
import { Slider } from '@/components/ui/slider'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

export function ThreeDViewer({ modelUrl }: { modelUrl?: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const engineRef = useRef<BABYLON.Engine | null>(null)
  const sceneRef = useRef<BABYLON.Scene | null>(null)
  const [explode, setExplode] = useState([0])
  const [material, setMaterial] = useState('metal')
  const [lighting, setLighting] = useState('studio')
  const [isMeasuring, setIsMeasuring] = useState(false)
  const [isAnnotating, setIsAnnotating] = useState(false)

  useEffect(() => {
    if (!canvasRef.current) return

    const engine = new BABYLON.Engine(canvasRef.current, true)
    engineRef.current = engine
    const scene = new BABYLON.Scene(engine)
    sceneRef.current = scene

    // Camera
    const camera = new BABYLON.ArcRotateCamera(
      "camera",
      Math.PI / 4,
      Math.PI / 3,
      10,
      BABYLON.Vector3.Zero(),
      scene
    )
    camera.attachControl(canvasRef.current, true)
    camera.wheelPrecision = 50
    camera.pinchPrecision = 50

    // Lighting
    const light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), scene)
    light.intensity = 0.7

    // Default Environment
    scene.createDefaultEnvironment({
      createGround: true,
      createSkybox: true,
      skyboxSize: 100,
      groundSize: 100,
    })

    // Load Model if URL exists
    if (modelUrl) {
      BABYLON.SceneLoader.ImportMesh(
        "",
        "",
        modelUrl,
        scene,
        () => {
          scene.createDefaultCameraOrLight(true, true, true)
          const cam = scene.activeCamera as BABYLON.ArcRotateCamera
          if (cam) {
            cam.alpha = Math.PI / 4
            cam.beta = Math.PI / 3
            cam.attachControl(canvasRef.current, true)
          }
        }
      )
    } else {
      // Mock cube for placeholder
      const box = BABYLON.MeshBuilder.CreateBox("box", { size: 2 }, scene)
      const mat = new BABYLON.StandardMaterial("boxMat", scene)
      mat.diffuseColor = new BABYLON.Color3(0.2, 0.4, 0.8)
      box.material = mat
    }

    engine.runRenderLoop(() => {
      scene.render()
    })

    const handleResize = () => {
      engine.resize()
    }
    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)
      engine.dispose()
    }
  }, [modelUrl])

  const handleScreenshot = () => {
    if (!canvasRef.current) return
    const dataUrl = canvasRef.current.toDataURL("image/png")
    const link = document.createElement("a")
    link.download = "protoforge-screenshot.png"
    link.href = dataUrl
    link.click()
  }

  const handleResetCamera = () => {
    if (!sceneRef.current) return
    const camera = sceneRef.current.activeCamera as BABYLON.ArcRotateCamera
    if (camera) {
      camera.alpha = Math.PI / 4
      camera.beta = Math.PI / 3
      camera.radius = 10
      camera.setTarget(BABYLON.Vector3.Zero())
    }
  }

  const toggleFullscreen = () => {
    if (canvasRef.current?.parentElement) {
      if (!document.fullscreenElement) {
        canvasRef.current.parentElement.requestFullscreen()
      } else {
        document.exitFullscreen()
      }
    }
  }

  return (
    <div className="relative w-full aspect-video bg-slate-900 rounded-xl overflow-hidden group border-2 border-slate-200 dark:border-slate-800">
      <canvas ref={canvasRef} className="w-full h-full outline-none touch-none" />
      
      {/* Top Left - Scene Info */}
      <div className="absolute top-4 left-4 pointer-events-none">
        <Badge variant="secondary" className="bg-slate-900/80 text-white border-slate-700 backdrop-blur-md px-3 py-1">
          <Box className="w-3 h-3 mr-2" />
          {modelUrl ? "STEP/GLB Model Active" : "Sample Assembly"}
        </Badge>
      </div>

      {/* Floating Control Panel - Bottom Right */}
      <div className="absolute bottom-6 right-6 flex flex-col gap-3">
        <div className="bg-slate-900/90 backdrop-blur-xl border border-slate-700 p-4 rounded-2xl shadow-2xl flex flex-col gap-4 w-64">
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="text-[10px] font-bold uppercase text-slate-500 tracking-widest flex items-center gap-2">
                <Layers className="w-3 h-3" /> Explode View
              </label>
              <span className="text-[10px] font-mono text-blue-400 font-bold">{explode[0]}%</span>
            </div>
            <Slider 
              value={explode} 
              onValueChange={setExplode} 
              max={100} 
              step={1} 
              className="py-1"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold uppercase text-slate-500 tracking-widest flex items-center gap-2">
                <Box className="w-3 h-3" /> Material
              </label>
              <Select value={material} onValueChange={setMaterial}>
                <SelectTrigger className="h-8 text-[10px] bg-slate-800 border-slate-700 text-slate-200">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700 text-slate-200">
                  <SelectItem value="plastic">ABS Plastic</SelectItem>
                  <SelectItem value="metal">Brushed Metal</SelectItem>
                  <SelectItem value="rubber">Rubber</SelectItem>
                  <SelectItem value="glass">Tempered Glass</SelectItem>
                  <SelectItem value="carbon">Carbon Fiber</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold uppercase text-slate-500 tracking-widest flex items-center gap-2">
                <Sun className="w-3 h-3" /> Lighting
              </label>
              <Select value={lighting} onValueChange={setLighting}>
                <SelectTrigger className="h-8 text-[10px] bg-slate-800 border-slate-700 text-slate-200">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700 text-slate-200">
                  <SelectItem value="studio">Studio Light</SelectItem>
                  <SelectItem value="outdoor">Natural Light</SelectItem>
                  <SelectItem value="warehouse">Warehouse</SelectItem>
                  <SelectItem value="dramatic">Dramatic</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button size="icon" variant="outline" className={`w-9 h-9 border-slate-700 bg-slate-800 hover:bg-slate-700 hover:text-white ${isMeasuring ? 'bg-blue-600 text-white' : 'text-slate-400'}`} onClick={() => setIsMeasuring(!isMeasuring)}>
                    <Ruler className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Measure tool</TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button size="icon" variant="outline" className={`w-9 h-9 border-slate-700 bg-slate-800 hover:bg-slate-700 hover:text-white ${isAnnotating ? 'bg-amber-600 text-white' : 'text-slate-400'}`} onClick={() => setIsAnnotating(!isAnnotating)}>
                    <MessageSquare className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Annotation mode</TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button size="icon" variant="outline" className="w-9 h-9 border-slate-700 bg-slate-800 hover:bg-slate-700 hover:text-white text-slate-400" onClick={handleResetCamera}>
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Reset Camera</TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button size="icon" variant="outline" className="w-9 h-9 border-slate-700 bg-slate-800 hover:bg-slate-700 hover:text-white text-slate-400" onClick={handleScreenshot}>
                    <Camera className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Take Screenshot</TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button size="icon" variant="outline" className="w-9 h-9 border-slate-700 bg-slate-800 hover:bg-slate-700 hover:text-white text-slate-400">
                    <Smartphone className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>View in AR</TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button size="icon" variant="outline" className="w-9 h-9 border-slate-700 bg-slate-800 hover:bg-slate-700 hover:text-white text-slate-400" onClick={toggleFullscreen}>
                    <Maximize2 className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Fullscreen</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </div>
    </div>
  )
}
