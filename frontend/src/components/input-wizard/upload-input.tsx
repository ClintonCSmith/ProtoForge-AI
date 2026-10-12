'use client'

import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { 
  Upload, 
  File, 
  X, 
  FileText, 
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useWizardStore } from '@/lib/store/use-wizard-store'
import { Badge } from '@/components/ui/badge'

export function UploadInput() {
  const { uploadedFiles, setUploadedFiles } = useWizardStore()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setUploadedFiles([...uploadedFiles, ...acceptedFiles])
  }, [uploadedFiles, setUploadedFiles])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf'],
      'image/vnd.dwg': ['.dwg'],
      'image/vnd.dxf': ['.dxf']
    },
    maxSize: 52428800 // 50MB
  })

  const removeFile = (index: number) => {
    const next = [...uploadedFiles]
    next.splice(index, 1)
    setUploadedFiles(next)
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all cursor-pointer group ${
          isDragActive 
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
          : 'border-slate-200 dark:border-slate-800 hover:border-blue-400 hover:bg-slate-50 dark:hover:bg-slate-900/50'
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-4">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
            isDragActive ? 'bg-blue-500 text-white scale-110' : 'bg-slate-100 dark:bg-slate-800 text-slate-400 group-hover:scale-105 group-hover:text-blue-500'
          }`}>
            <Upload className="h-8 w-8" />
          </div>
          <div>
            <p className="text-lg font-bold">
              {isDragActive ? 'Drop your files here' : 'Drag & drop technical specs'}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Supports DWG, DXF, PDF, PNG, JPG (Max 50MB)
            </p>
          </div>
          <Button variant="secondary" size="sm" className="mt-2">
            Browse Files
          </Button>
        </div>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <p className="text-xs font-bold uppercase tracking-widest text-slate-500">
              Files to Process ({uploadedFiles.length})
            </p>
            <button className="text-xs text-red-500 hover:underline" onClick={() => setUploadedFiles([])}>Clear All</button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {uploadedFiles.map((file, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl border bg-white dark:bg-slate-950 group">
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
                    {file.type.startsWith('image/') ? <ImageIcon className="h-5 w-5 text-blue-500" /> : <FileText className="h-5 w-5 text-slate-500" />}
                  </div>
                  <div className="overflow-hidden">
                    <p className="text-sm font-bold truncate">{file.name}</p>
                    <p className="text-[10px] text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-8 w-8 text-slate-400 hover:text-red-500"
                    onClick={() => removeFile(i)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {uploadedFiles.length === 0 && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 text-slate-500">
          <AlertCircle className="h-5 w-5" />
          <p className="text-xs">
            Upload engineering drawings or reference photos to give our AI more context for the geometry.
          </p>
        </div>
      )}
    </div>
  )
}
