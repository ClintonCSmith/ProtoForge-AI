'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  FileText, 
  Mic, 
  Pencil, 
  Upload as UploadIcon,
  Settings2,
  Wand2,
  AlertCircle,
  ChevronRight,
  Info
} from 'lucide-react'
import { useWizardStore } from '@/lib/store/use-wizard-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'

// Tab Components
import { TextInput } from './text-input'
import { VoiceInput } from './voice-input'
import { SketchInput } from './sketch-input'
import { UploadInput } from './upload-input'

import { api } from '@/lib/api'

export function InputWizard() {
  const router = useRouter()
  const [isForging, setIsForging] = useState(false)
  const {
    activeTab,
    setActiveTab,
    projectName,
    setProjectName,
    description,
    setDescription,
    standard,
    setStandard,
    quality,
    setQuality,
    priority,
    setPriority,
    textInput,
    audioBlob,
    sketchData,
    uploadedFiles
  } = useWizardStore()

  const handleSubmit = async () => {
    setIsForging(true)

    try {
      let inputData = ''
      if (activeTab === 'text') inputData = textInput
      else if (activeTab === 'voice') inputData = 'voice_blob_placeholder' // In a real app, upload blob first
      else if (activeTab === 'sketch') inputData = sketchData || ''
      else if (activeTab === 'upload') inputData = uploadedFiles[0]?.name || ''

      const project = await api.createProject({
        name: projectName,
        description,
        input_type: activeTab as any,
        input_data: inputData,
        settings: { standard, quality, priority }
      })

      router.push(`/projects/${project.id}`)
    } catch (error) {
      console.error('Failed to create project:', error)
      setIsForging(false)
    }
  }

  const isFormValid = projectName.length > 0 && (
    (activeTab === 'text' && textInput.length >= 10) ||
    (activeTab === 'voice' && audioBlob !== null) ||
    (activeTab === 'sketch' && sketchData !== null) ||
    (activeTab === 'upload' && uploadedFiles.length > 0)
  )

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Step Header */}
      <div className="flex items-center gap-4 mb-8">
        <div className="h-10 w-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">1</div>
        <div>
          <h2 className="text-2xl font-bold">Forge Your Vision</h2>
          <p className="text-sm text-muted-foreground">Select an input method to begin the AI synthesis process.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 space-y-8">
          {/* Main Input Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-4 h-14 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-1 rounded-2xl">
              <TabsTrigger value="text" className="rounded-xl gap-2 font-bold data-[state=active]:bg-white dark:data-[state=active]:bg-slate-950 shadow-none">
                <FileText className="h-4 w-4" />
                <span className="hidden sm:inline">Text</span>
              </TabsTrigger>
              <TabsTrigger value="voice" className="rounded-xl gap-2 font-bold data-[state=active]:bg-white dark:data-[state=active]:bg-slate-950 shadow-none">
                <Mic className="h-4 w-4" />
                <span className="hidden sm:inline">Voice</span>
              </TabsTrigger>
              <TabsTrigger value="sketch" className="rounded-xl gap-2 font-bold data-[state=active]:bg-white dark:data-[state=active]:bg-slate-950 shadow-none">
                <Pencil className="h-4 w-4" />
                <span className="hidden sm:inline">Sketch</span>
              </TabsTrigger>
              <TabsTrigger value="upload" className="rounded-xl gap-2 font-bold data-[state=active]:bg-white dark:data-[state=active]:bg-slate-950 shadow-none">
                <UploadIcon className="h-4 w-4" />
                <span className="hidden sm:inline">Upload</span>
              </TabsTrigger>
            </TabsList>

            <div className="mt-8 bg-slate-50/50 dark:bg-slate-900/30 rounded-3xl border border-slate-200 dark:border-slate-800 p-8">
              <TabsContent value="text" className="mt-0 outline-none">
                <TextInput />
              </TabsContent>
              <TabsContent value="voice" className="mt-0 outline-none">
                <VoiceInput />
              </TabsContent>
              <TabsContent value="sketch" className="mt-0 outline-none">
                <SketchInput />
              </TabsContent>
              <TabsContent value="upload" className="mt-0 outline-none">
                <UploadInput />
              </TabsContent>
            </div>
          </Tabs>

          {/* Detailed Info */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="projectName" className="text-sm font-bold uppercase tracking-widest text-slate-500">Project Name</Label>
              <Input 
                id="projectName" 
                placeholder="e.g. Aerodynamic Bracket Assembly" 
                className="h-12 text-lg bg-white dark:bg-slate-950 border-2"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="desc" className="text-sm font-bold uppercase tracking-widest text-slate-500">Brief Description (Optional)</Label>
              <Textarea 
                id="desc" 
                placeholder="What is the primary function of this part?" 
                className="bg-white dark:bg-slate-950 border-2"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Right Sidebar: Settings & Submission */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm sticky top-24">
            <div className="flex items-center gap-2 font-bold text-lg mb-6">
              <Settings2 className="h-5 w-5 text-blue-500" />
              Forge Settings
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <Label className="text-xs font-bold text-slate-500">Engineering Standard</Label>
                <Select value={standard} onValueChange={setStandard}>
                  <SelectTrigger className="bg-slate-50 dark:bg-slate-900 border-slate-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ISO">ISO (International)</SelectItem>
                    <SelectItem value="ASME">ASME (USA)</SelectItem>
                    <SelectItem value="DIN">DIN (Germany)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label className="text-xs font-bold text-slate-500">Output Quality</Label>
                <Select value={quality} onValueChange={setQuality}>
                  <SelectTrigger className="bg-slate-50 dark:bg-slate-900 border-slate-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Preview">Preview (Fast)</SelectItem>
                    <SelectItem value="Production">Production (High Detail)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Accordion type="single" collapsible className="w-full">
                <AccordionItem value="advanced" className="border-none">
                  <AccordionTrigger className="text-xs font-bold text-slate-500 uppercase py-0 hover:no-underline">
                    Advanced Options
                  </AccordionTrigger>
                  <AccordionContent className="pt-4 space-y-4">
                    <div className="space-y-2">
                      <Label className="text-[10px] text-slate-400">Pipeline Priority</Label>
                      <Select value={priority} onValueChange={setPriority}>
                        <SelectTrigger className="h-8 text-xs">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Normal">Normal Queue</SelectItem>
                          <SelectItem value="High">Priority (Fast-track)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>

              <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
                <Button 
                  className={`w-full h-14 rounded-2xl font-bold text-lg transition-all duration-500 relative overflow-hidden ${
                    isForging ? 'bg-blue-600 scale-95' : 'bg-blue-600 hover:bg-blue-500 shadow-xl shadow-blue-500/20'
                  }`}
                  disabled={!isFormValid || isForging}
                  onClick={handleSubmit}
                >
                  {isForging ? (
                    <div className="flex items-center gap-3">
                      <Wand2 className="h-5 w-5 animate-spin" />
                      Forging...
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      Generate Prototype
                      <ChevronRight className="h-5 w-5" />
                    </div>
                  )}
                  {isForging && (
                    <div className="absolute inset-0 bg-white/10 animate-pulse" />
                  )}
                </Button>
                
                <p className="text-[10px] text-center text-muted-foreground mt-4 flex items-center justify-center gap-1">
                  <Info className="h-3 w-3" />
                  Synthesis usually takes 2-5 minutes
                </p>
              </div>
            </div>
          </div>

          <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/50 rounded-2xl p-4 flex gap-3">
            <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0" />
            <p className="text-xs text-amber-800 dark:text-amber-400 leading-relaxed">
              <strong>Tip:</strong> Providing both a sketch and a text description significantly improves the AI's structural understanding.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
