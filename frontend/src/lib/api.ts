import { createClient } from './supabase/client'

const API_BASE_URL = 'http://localhost:8000'

export interface Project {
  id: string
  name: string
  description?: string
  status: 'draft' | 'processing' | 'complete' | 'failed'
  version: string
  created_at: string
  updated_at: string
  type?: string
  thumbnail_url?: string
  job_id?: string
  tier?: string
  model_url?: string
  video_url?: string
  drawings_url?: string
  bom_url?: string
  fea_url?: string
}

export interface CreateProjectParams {
  name: string
  description?: string
  input_type: 'text' | 'voice' | 'sketch' | 'upload'
  input_data: string // text content, voice blob URL, sketch data URL, etc.
  settings?: Record<string, any>
}

export const api = {
  async getProjects(): Promise<Project[]> {
    const supabase = createClient()
    const { data: { session } } = await supabase.auth.getSession()
    
    const response = await fetch(`${API_BASE_URL}/api/projects`, {
      headers: {
        'Authorization': `Bearer ${session?.access_token}`,
      }
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch projects')
    }
    
    return response.json()
  },

  async getProject(id: string): Promise<Project> {
    const supabase = createClient()
    const { data: { session } } = await supabase.auth.getSession()
    
    const response = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
      headers: {
        'Authorization': `Bearer ${session?.access_token}`,
      }
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch project')
    }
    
    return response.json()
  },

  async createProject(params: CreateProjectParams): Promise<Project> {
    const supabase = createClient()
    const { data: { session } } = await supabase.auth.getSession()
    
    const response = await fetch(`${API_BASE_URL}/api/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session?.access_token}`,
      },
      body: JSON.stringify(params)
    })
    
    if (!response.ok) {
      throw new Error('Failed to create project')
    }
    
    return response.json()
  },

  getEventSource(jobId: string): EventSource {
    return new EventSource(`${API_BASE_URL}/api/jobs/${jobId}/stream`)
  }
}
