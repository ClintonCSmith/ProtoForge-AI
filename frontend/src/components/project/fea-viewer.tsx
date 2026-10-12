'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  ShieldAlert, 
  Activity, 
  Thermometer, 
  Weight,
  Download,
  AlertTriangle
} from 'lucide-react'
import { Button } from '@/components/ui/button'

export function FEAViewer({ projectId, feaUrl }: { projectId: string, feaUrl?: string }) {
  // Mock data for FEA simulation
  const results = {
    maxStress: '145.2 MPa',
    yieldStrength: '240.0 MPa',
    safetyFactor: '1.65',
    maxDisplacement: '0.12 mm',
    status: 'pass'
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <Activity className="h-5 w-5 text-red-500" />
          FEA Stress Analysis
        </h3>
        <Button variant="outline" size="sm" className="gap-2">
          <Download className="h-4 w-4" />
          Full Report (PDF)
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-2">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center text-center space-y-2">
              <ShieldAlert className="h-5 w-5 text-blue-500" />
              <p className="text-xs font-bold uppercase text-slate-500">Max Stress</p>
              <h4 className="text-xl font-bold">{results.maxStress}</h4>
            </div>
          </CardContent>
        </Card>
        <Card className="border-2">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center text-center space-y-2">
              <Thermometer className="h-5 w-5 text-orange-500" />
              <p className="text-xs font-bold uppercase text-slate-500">Factor of Safety</p>
              <h4 className="text-xl font-bold text-green-600">{results.safetyFactor}</h4>
            </div>
          </CardContent>
        </Card>
        <Card className="border-2">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center text-center space-y-2">
              <Weight className="h-5 w-5 text-slate-500" />
              <p className="text-xs font-bold uppercase text-slate-500">Max Displacement</p>
              <h4 className="text-xl font-bold">{results.maxDisplacement}</h4>
            </div>
          </CardContent>
        </Card>
        <Card className="border-2">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center text-center space-y-2">
              <Activity className="h-5 w-5 text-purple-500" />
              <p className="text-xs font-bold uppercase text-slate-500">Analysis Status</p>
              <Badge className="bg-green-500">VERIFIED</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="relative aspect-video bg-slate-900 rounded-2xl border-2 overflow-hidden group">
        <img 
          src="https://images.unsplash.com/photo-1581092583537-20d51b4b4f1b?auto=format&fit=crop&q=80&w=1200" 
          alt="FEA Heatmap" 
          className="w-full h-full object-cover opacity-80"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex flex-col justify-end p-8">
          <h4 className="text-white font-bold text-lg">Von Mises Stress Distribution</h4>
          <p className="text-slate-300 text-sm">Linear static analysis under 500N vertical load.</p>
        </div>
        
        {/* Scale Legend */}
        <div className="absolute top-8 right-8 bg-black/40 backdrop-blur-md p-4 rounded-lg border border-white/20 text-white">
          <p className="text-[10px] font-bold uppercase mb-2">Stress (MPa)</p>
          <div className="h-32 w-4 bg-gradient-to-t from-blue-500 via-green-500 to-red-500 rounded-full" />
          <div className="flex flex-col justify-between h-32 ml-6 -mt-32 text-[10px] font-mono">
            <span>240</span>
            <span>180</span>
            <span>120</span>
            <span>60</span>
            <span>0</span>
          </div>
        </div>
      </div>

      <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/50 rounded-xl p-4 flex gap-3">
        <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0" />
        <div>
          <p className="text-sm font-bold text-amber-800 dark:text-amber-400">Simulation Warning</p>
          <p className="text-xs text-amber-700 dark:text-amber-500 leading-relaxed">
            Local stress concentrations detected at sharp corners. Consider adding fillets to improve fatigue life.
          </p>
        </div>
      </div>
    </div>
  )
}
