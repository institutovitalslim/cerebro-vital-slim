import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

export const supabaseEnabled = Boolean(supabaseUrl && supabaseAnonKey)

export function getSupabaseBrowserClient() {
  if (!supabaseEnabled) return null
  return createClient(supabaseUrl, supabaseAnonKey)
}
