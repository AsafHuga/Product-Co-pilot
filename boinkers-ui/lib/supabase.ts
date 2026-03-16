import { createClient } from '@supabase/supabase-js'

const supabaseUrl  = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey  = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseKey)

export interface Feature {
  id:          number
  name:        string
  date:        string
  description: string
  cat:         string
  status:      string
  impact:      string
  owner:       string
}

export type FeatureInput = Omit<Feature, 'id'>
