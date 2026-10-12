'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { 
  Plus, 
  Search, 
  Filter, 
  MoreVertical, 
  Box, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  Loader2,
  ChevronRight,
  TrendingUp,
  History,
  Wand2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  DropdownMenu,
  DropdownMenuContent,
  SelectItem,
  DropdownMenuTrigger,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { api } from '@/lib/api'
import { createClient } from '@/lib/supabase/client'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'

export default function DashboardPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const supabase = createClient()
  const router = useRouter()

  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: () => api.getProjects(),
    retry: false
  })

  const { data: session } = useQuery({
    queryKey: ['session'],
    queryFn: async () => {
      const { data } = await supabase.auth.getSession()
      return data.session
    }
  })

  const [quickForge, setQuickForge] = useState('')
  const queryClient = useQueryClient()

  const handleQuickForge = async () => {
    if (!quickForge.trim()) return
    try {
      const project = await api.createProject({
        name: quickForge.trim(),
        input_type: 'text',
        input_data: quickForge.trim(),
      })
      setQuickForge('')
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      router.push(`/projects/${project.id}`)
    } catch (e) {
      console.error(e)
    }
  }

  const filteredProjects = projects?.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || p.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="p-8 space-y-10 animate-in fade-in duration-700">
      {/* Welcome Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Project Workspace</h1>
          <p className="text-muted-foreground mt-1">Manage and monitor your AI-generated prototypes.</p>
        </div>
        <Link href="/projects/new">
          <Button size="lg" className="bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-500/20 h-12 rounded-xl gap-2 font-bold">
            <Plus className="h-5 w-5" />
            New Prototype
          </Button>
        </Link>
      </div>

      {/* Stats / Usage Meter */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        <Card className="md:col-span-4 border-2 shadow-sm bg-blue-600 text-white">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-blue-100 text-xs font-bold uppercase tracking-widest">Monthly Usage</p>
                <h3 className="text-4xl font-bold mt-2">3 / 10</h3>
                <p className="text-blue-100 text-[10px] mt-1 font-medium">Starter Plan • Resets in 12 days</p>
              </div>
              <div className="h-10 w-10 rounded-full bg-white/10 flex items-center justify-center">
                <TrendingUp className="h-5 w-5" />
              </div>
            </div>
            <Progress value={30} className="h-2 bg-blue-800 mt-6" />
          </CardContent>
        </Card>

        <Card className="md:col-span-3 border-2 shadow-sm">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-muted-foreground text-xs font-bold uppercase tracking-widest">Active Jobs</p>
                <h3 className="text-4xl font-bold mt-2">1</h3>
                <div className="flex items-center gap-2 text-blue-500 text-[10px] mt-1 font-bold">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  Drone Frame V4 is being forged
                </div>
              </div>
              <div className="h-10 w-10 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center">
                <Box className="h-5 w-5" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-5 border-2 shadow-sm bg-slate-50 dark:bg-slate-900 border-dashed overflow-hidden group">
          <CardContent className="p-6 flex flex-col justify-center h-full space-y-4">
            <div className="flex items-center gap-2">
              <Wand2 className="h-4 w-4 text-blue-500" />
              <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Quick Forge</p>
            </div>
            <div className="flex gap-2">
              <Input 
                placeholder="Describe a part to forge instantly..." 
                className="bg-white dark:bg-slate-950 border-2 border-slate-200 dark:border-slate-800 rounded-xl h-11"
                value={quickForge}
                onChange={(e) => setQuickForge(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleQuickForge()}
              />
              <Button 
                onClick={handleQuickForge}
                disabled={!quickForge.trim()}
                className="bg-blue-600 hover:bg-blue-500 rounded-xl h-11 px-6 font-bold"
              >
                Forge
              </Button>
            </div>
            <p className="text-[10px] text-slate-400 italic">Press Enter to start synthesis with default settings.</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between bg-white dark:bg-slate-950 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search projects..." 
            className="pl-10 h-10 bg-slate-50 dark:bg-slate-900 border-none rounded-xl"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full sm:w-[160px] h-10 rounded-xl bg-slate-50 dark:bg-slate-900 border-none">
              <div className="flex items-center gap-2">
                <Filter className="h-3 w-3" />
                <SelectValue placeholder="Status" />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="complete">Complete</SelectItem>
              <SelectItem value="processing">Processing</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
            </SelectContent>
          </Select>
          
          <Select defaultValue="newest">
            <SelectTrigger className="w-full sm:w-[160px] h-10 rounded-xl bg-slate-50 dark:bg-slate-900 border-none">
              <div className="flex items-center gap-2">
                <History className="h-3 w-3" />
                <SelectValue />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newest">Newest First</SelectItem>
              <SelectItem value="oldest">Oldest First</SelectItem>
              <SelectItem value="name">Alphabetical</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Project Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3].map(i => <div key={i} className="h-80 bg-slate-100 dark:bg-slate-900 animate-pulse rounded-2xl border" />)}
        </div>
      ) : filteredProjects && filteredProjects.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <Link key={project.id} href={`/projects/${project.id}`}>
              <Card className="overflow-hidden group hover:border-blue-500 hover:shadow-xl transition-all duration-300 rounded-2xl border-2">
                <div className="aspect-[16/10] relative overflow-hidden bg-slate-100 dark:bg-slate-900">
                  <img 
                    src={project.thumbnail_url || 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=400'} 
                    alt={project.name} 
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                    <Button variant="secondary" size="sm" className="w-full bg-white text-black font-bold h-9">
                      Open Project
                    </Button>
                  </div>
                  <div className="absolute top-4 left-4">
                    {project.status === 'complete' && (
                      <Badge className="bg-green-500 border-none flex items-center gap-1 py-1 pr-3">
                        <CheckCircle2 className="h-3 w-3" /> Complete
                      </Badge>
                    )}
                    {project.status === 'processing' && (
                      <Badge className="bg-blue-500 border-none flex items-center gap-1 py-1 pr-3 animate-pulse">
                        <Loader2 className="h-3 w-3 animate-spin" /> Processing
                      </Badge>
                    )}
                    {project.status === 'draft' && (
                      <Badge variant="secondary" className="border-none flex items-center gap-1 py-1 pr-3">
                        <Box className="h-3 w-3" /> Draft
                      </Badge>
                    )}
                    {project.status === 'failed' && (
                      <Badge variant="destructive" className="border-none flex items-center gap-1 py-1 pr-3">
                        <AlertCircle className="h-3 w-3" /> Failed
                      </Badge>
                    )}
                  </div>
                </div>
                <CardContent className="p-5 space-y-4">
                  <div>
                    <h3 className="font-bold text-lg group-hover:text-blue-600 transition-colors line-clamp-1">{project.name}</h3>
                    <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                      <Clock className="h-3 w-3" />
                      Modified {new Date(project.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="flex items-center justify-between pt-2 border-t">
                    <Badge variant="outline" className="text-[10px] font-mono rounded-md">{project.type || 'General'}</Badge>
                    <div className="flex items-center -space-x-2">
                      <div className="h-6 w-6 rounded-full border-2 border-white bg-slate-200" />
                      <div className="h-6 w-6 rounded-full border-2 border-white bg-blue-500 text-[8px] flex items-center justify-center text-white font-bold">+2</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <div className="py-20 flex flex-col items-center justify-center text-center space-y-6">
          <div className="w-24 h-24 rounded-full bg-slate-100 dark:bg-slate-900 flex items-center justify-center">
            <Box className="h-10 w-10 text-slate-300" />
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-bold">No prototypes found</h3>
            <p className="text-muted-foreground max-w-xs">
              Start by creating your first AI-generated 3D prototype.
            </p>
          </div>
          <Link href="/projects/new">
            <Button className="bg-blue-600 hover:bg-blue-500 rounded-xl px-8 h-12 font-bold">
              Create Your First Prototype
            </Button>
          </Link>
        </div>
      )}

      {/* Pagination Mock */}
      <div className="flex justify-center pt-10">
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled>Previous</Button>
          <Button variant="secondary" size="sm" className="bg-blue-50 text-blue-600 border-blue-100">1</Button>
          <Button variant="outline" size="sm">2</Button>
          <Button variant="outline" size="sm">Next</Button>
        </div>
      </div>
    </div>
  )
}
