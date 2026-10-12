import { create } from 'zustand'

interface WizardState {
  projectName: string
  description: string
  standard: string
  quality: string
  priority: string
  activeTab: string
  
  // Tab-specific data
  textInput: string
  audioBlob: Blob | null
  sketchData: string | null // base64
  uploadedFiles: File[]
  
  // Actions
  setProjectName: (name: string) => void
  setDescription: (desc: string) => void
  setStandard: (std: string) => void
  setQuality: (q: string) => void
  setPriority: (p: string) => void
  setActiveTab: (tab: string) => void
  setTextInput: (text: string) => void
  setAudioBlob: (blob: Blob | null) => void
  setSketchData: (data: string | null) => void
  setUploadedFiles: (files: File[]) => void
  reset: () => void
}

export const useWizardStore = create<WizardState>((set) => ({
  projectName: '',
  description: '',
  standard: 'ISO',
  quality: 'Production',
  priority: 'Normal',
  activeTab: 'text',
  
  textInput: '',
  audioBlob: null,
  sketchData: null,
  uploadedFiles: [],

  setProjectName: (projectName) => set({ projectName }),
  setDescription: (description) => set({ description }),
  setStandard: (standard) => set({ standard }),
  setQuality: (quality) => set({ quality }),
  setPriority: (priority) => set({ priority }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setTextInput: (textInput) => set({ textInput }),
  setAudioBlob: (audioBlob) => set({ audioBlob }),
  setSketchData: (sketchData) => set({ sketchData }),
  setUploadedFiles: (uploadedFiles) => set({ uploadedFiles }),
  reset: () => set({
    projectName: '',
    description: '',
    standard: 'ISO',
    quality: 'Production',
    priority: 'Normal',
    activeTab: 'text',
    textInput: '',
    audioBlob: null,
    sketchData: null,
    uploadedFiles: []
  })
}))
