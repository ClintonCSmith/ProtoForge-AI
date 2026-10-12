import { createClient } from '@/lib/supabase/server'

export async function createProject(formData: FormData) {
  const supabase = await createClient()
  const title = formData.get('title') as string
  const description = formData.get('description') as string

  const { data, error } = await supabase
    .from('projects')
    .insert([{ title, description }])
    .select()
    .single()

  if (error) {
    console.error('Error creating project:', error)
    return { error: error.message }
  }

  return { data }
}
