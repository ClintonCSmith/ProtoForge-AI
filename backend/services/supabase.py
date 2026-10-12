import { createClient } from '@supabase/supabase-js'
import os from 'os'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!

// Service role client — bypasses RLS, for server-side admin operations
export const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false,
  },
})

// Storage bucket names
export const STORAGE_BUCKETS = {
  ASSETS: 'protoforge-assets',
  RENDERS: 'protoforge-renders',
  MODELS: 'protoforge-models',
  DRAWINGS: 'protoforge-drawings',
} as const

export async function ensureStorageBuckets() {
  for (const bucket of Object.values(STORAGE_BUCKETS)) {
    const { data: existing } = await supabaseAdmin.storage.getBucket(bucket)
    if (!existing) {
      await supabaseAdmin.storage.createBucket(bucket, {
        public: true,
        fileSizeLimit: 524288000, // 500MB
      })
    }
  }
}

export async function uploadAsset(
  bucket: string,
  path: string,
  file: Buffer,
  contentType: string
) {
  const { data, error } = await supabaseAdmin.storage
    .from(bucket)
    .upload(path, file, { contentType, upsert: true })
  
  if (error) throw error
  
  const { data: { publicUrl } } = supabaseAdmin.storage
    .from(bucket)
    .getPublicUrl(data.path)
  
  return publicUrl
}