'use client'

import React, { use } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  ChevronLeft, 
  Settings, 
  Download, 
  Trash2, 
  Wand2, 
  Info,
  Clock,
  ShieldCheck,
  Package,
  FileText,
  Video,
  Box as BoxIcon,
  Activity,
  AlertCircle
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'

import { api } from '@/lib/api'

// Supporting Components
import { PipelineProgress } from '@/components/project/pipeline-progress'
import { ThreeDViewer } from '@/components/project/3d-viewer'
import { RenderGallery } from '@/components/project/render-gallery'
import { DrawingViewer } from '@/components/project/drawing-viewer'
import { BOMTable } from '@/components/project/bom-table'
import { AnimationPlayer } from '@/components/project/animation-player'
import { FEAViewer } from '@/components/project/fea-viewer'
import { RevisionPanel } from '@/components/project/revision-panel'
import { ShareModal } from '@/components/project/share-modal'

interface ProjectPageProps {
  params: Promise<{ id: string }>
}

export default function ProjectWorkspacePage({ params }: ProjectPageProps) {
  const { id } = use(params)

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => api.getProject(id)
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen space-y-4">
        <AlertCircle className="h-12 w-12 text-red-500" />
        <h2 className="text-xl font-bold">Project Not Found</h2>
        <p className="text-muted-foreground">The project you are looking for does not exist or you don't have access.</p>
        <Link href="/dashboard">
          <Button variant="outline">Back to Dashboard</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 flex flex-col">
      {/* Version History / Revision Panel */}
      <RevisionPanel projectId={id} />

      {/* Workspace Header */}
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-[1400px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <h1 className="text-lg font-bold tracking-tight">{project?.name}</h1>
              <Badge variant="outline" className="text-[10px] uppercase font-mono">v{project?.version}</Badge>
              <Badge className="bg-blue-600/10 text-blue-600 hover:bg-blue-600/10 border-blue-200 dark:border-blue-900 text-[10px] uppercase">
                Professional
              </Badge>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="gap-2 text-slate-500 hover:text-slate-900">
              <Settings className="h-4 w-4" />
              Config
            </Button>
            <ShareModal projectId={id} />
            <Button size="sm" className="bg-blue-600 hover:bg-blue-500 gap-2">
              <Wand2 className="h-4 w-4" />
              Refine with AI
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-[1400px] mx-auto w-full p-6 grid grid-cols-1 xl:grid-cols-12 gap-8">
        
        {/* Left Column: Visuals & Progress */}
        <div className="xl:col-span-8 space-y-8">
          
          {/* Main 3D Viewer */}
          <section className="space-y-4">
            <ThreeDViewer modelUrl={project?.model_url} />
          </section>

          {/* Pipeline Progress */}
          <section>
            <PipelineProgress projectId={id} jobId={project?.job_id} />
          </section>

          {/* Multi-Output Tabs */}
          <section className="bg-white dark:bg-slate-950 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <Tabs defaultValue="renders" className="w-full">
              <div className="px-6 pt-4 border-b bg-slate-50/50 dark:bg-slate-900/20">
                <TabsList className="bg-transparent h-auto p-0 gap-8">
                  <TabsTrigger value="renders" className="tab-trigger">
                    <BoxIcon className="h-4 w-4 mr-2" />
                    4K Renders
                  </TabsTrigger>
                  <TabsTrigger value="drawings" className="tab-trigger">
                    <FileText className="h-4 w-4 mr-2" />
                    Technical Drawings
                  </TabsTrigger>
                  <TabsTrigger value="animation" className="tab-trigger">
                    <Video className="h-4 w-4 mr-2" />
                    Animation
                  </TabsTrigger>
                  <TabsTrigger value="bom" className="tab-trigger">
                    <Package className="h-4 w-4 mr-2" />
                    BOM & Costs
                  </TabsTrigger>
                  <TabsTrigger value="fea" className="tab-trigger">
                    <Activity className="h-4 w-4 mr-2" />
                    FEA Results
                  </TabsTrigger>
                </TabsList>
              </div>

              <div className="p-6">
                <TabsContent value="renders" className="mt-0 outline-none">
                  <RenderGallery projectId={id} />
                </TabsContent>
                <TabsContent value="drawings" className="mt-0 outline-none">
                  <DrawingViewer projectId={id} drawingUrl={project?.drawings_url} />
                </TabsContent>
                <TabsContent value="animation" className="mt-0 outline-none">
                  <AnimationPlayer videoUrl={project?.video_url} />
                </TabsContent>
                <TabsContent value="bom" className="mt-0 outline-none">
                  <BOMTable projectId={id} bomUrl={project?.bom_url} />
                </TabsContent>
                <TabsContent value="fea" className="mt-0 outline-none">
                  <FEAViewer projectId={id} feaUrl={project?.fea_url} />
                </TabsContent>
              </div>
            </Tabs>
          </section>
        </div>

        {/* Right Column: Metadata & Actions */}
        <aside className="xl:col-span-4 space-y-6">
          
          {/* Project Info Card */}
          <div className="bg-slate-50 dark:bg-slate-900/50 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-6">
            <div className="space-y-2">
              <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500">About this Prototype</h3>
              <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                {project?.description}
              </p>
            </div>

            <Separator className="bg-slate-200 dark:bg-slate-800" />

            <div className="space-y-4">
              <div className="flex justify-between items-center text-xs">
                <div className="flex items-center gap-2 text-slate-500">
                  <Clock className="h-3 w-3" />
                  Created
                </div>
                <span className="font-medium">{project ? new Date(project.created_at).toLocaleDateString() : ''}</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <div className="flex items-center gap-2 text-slate-500">
                  <ShieldCheck className="h-3 w-3" />
                  Quality Standard
                </div>
                <Badge variant="outline" className="text-[10px]">ISO 9001:2015</Badge>
              </div>
              <div className="flex justify-between items-center text-xs">
                <div className="flex items-center gap-2 text-slate-500">
                  <Info className="h-3 w-3" />
                  Primary Material
                </div>
                <span className="font-medium">AL 6061-T6</span>
              </div>
            </div>

            <Separator className="bg-slate-200 dark:border-slate-800" />

            <div className="space-y-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Export Assets</p>
              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" className="w-full gap-2 text-xs">
                  <Download className="h-3.5 w-3.5" />
                  STEP
                </Button>
                <Button variant="outline" className="w-full gap-2 text-xs">
                  <Download className="h-3.5 w-3.5" />
                  STL
                </Button>
                <Button variant="outline" className="w-full gap-2 text-xs">
                  <Download className="h-3.5 w-3.5" />
                  OBJ
                </Button>
                <Button variant="outline" className="w-full gap-2 text-xs">
                  <Download className="h-3.5 w-3.5" />
                  GLTF
                </Button>
              </div>
              <Button variant="outline" className="w-full gap-2 text-xs text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 border-slate-200 dark:border-slate-800 mt-4">
                <Trash2 className="h-3.5 w-3.5" />
                Delete Project
              </Button>
            </div>
          </div>

          {/* Quick Actions / AI Assistance */}
          <div className="bg-blue-600 rounded-2xl p-6 text-white space-y-4 shadow-lg shadow-blue-500/20">
            <h3 className="text-lg font-bold">Ready for Production?</h3>
            <p className="text-sm text-blue-100 leading-relaxed">
              Our AI can automatically request quotes from verified manufacturing partners based on your BOM and technical specs.
            </p>
            <Button className="w-full bg-white text-blue-600 hover:bg-blue-50 font-bold">
              Get Manufacturing Quotes
            </Button>
          </div>

          {/* Support Widget */}
          <div className="border border-slate-200 dark:border-slate-800 rounded-2xl p-6 flex items-center gap-4 hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors cursor-pointer group">
            <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-500 group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
              <Info className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-bold">Engineering Review</p>
              <p className="text-[10px] text-muted-foreground">Chat with an expert about this design</p>
            </div>
          </div>
        </aside>
      </main>

      <style jsx global>{`
        .tab-trigger {
          @apply relative pb-4 px-1 text-slate-500 font-bold text-sm transition-all hover:text-slate-900 dark:hover:text-white border-b-2 border-transparent !shadow-none;
        }
        .tab-trigger[data-state="active"] {
          @apply text-blue-600 dark:text-blue-500 border-blue-600 dark:border-blue-500 bg-transparent rounded-none;
        }
      `}</style>
    </div>
  )
}
