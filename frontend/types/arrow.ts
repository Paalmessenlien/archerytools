// Arrow Types and Interfaces

export interface UserProfile {
  id: number
  google_id: string
  email: string
  name?: string
  profile_picture_url?: string
  is_admin: boolean
  draw_length: number
  skill_level: 'beginner' | 'intermediate' | 'advanced'
  shooting_style: 'target' | 'hunting' | 'traditional' | '3d'
  preferred_manufacturers: string[]
  notes?: string
  created_at: string
}

export interface SpineSpecification {
  spine: number
  outer_diameter: number
  gpi_weight: number
  inner_diameter?: number
  length_options?: number[]
}

export interface ArrowSpecification {
  id: number
  manufacturer: string
  model_name: string
  spine_specifications: SpineSpecification[]
  material?: string
  carbon_content?: string
  arrow_type?: 'hunting' | 'target' | 'indoor' | 'outdoor' | '3d' | 'recreational'
  recommended_use?: string[]
  description?: string
  primary_image_url?: string
  gallery_images?: string[]
  saved_images?: string[]
  straightness_tolerance?: string
  weight_tolerance?: string
  price_range?: string
  availability?: string
  source_url: string
  scraped_at: string
  scraper_version: string
}

export interface BowConfiguration {
  draw_weight: number
  bow_type: 'compound' | 'recurve' | 'longbow' | 'traditional'
  arrow_material: 'carbon' | 'aluminum' | 'wood' | 'fiberglass' | 'carbon-aluminum'
  arrow_type?: string
  arrow_rest_type?: 'drop-away' | 'whisker-biscuit' | 'blade'
  nock_type: 'pin' | 'press-fit' | 'over-nock' | 'lighted' | 'half-moon'
  vane_type: 'plastic' | 'feather' | 'hybrid' | 'blazer' | 'helical'
  vane_length: number
  number_of_vanes: number
  // Note: draw_length removed - now part of user profile
}

export interface ArrowConfiguration {
  id?: number
  name: string
  arrow_length: number
  point_weight: number
  nock_weight?: number
  fletching_weight?: number
  insert_weight?: number
  total_weight?: number
  calculated_foc?: number
  arrow_spine?: number
  shaft_model?: string
  shaft_manufacturer?: string
  notes?: string
  created_at?: string
}

export interface BowSetup {
  id?: number
  name: string
  bow_config: BowConfiguration
  arrow_configurations: ArrowConfiguration[]
  created_at?: string
  updated_at?: string
  description?: string
  user_id?: number
}

export interface ArrowSearchFilters {
  manufacturer?: string
  arrow_type?: string
  spine_min?: number
  spine_max?: number
  gpi_min?: number
  gpi_max?: number
  diameter_min?: number
  diameter_max?: number
  search?: string
}

export interface ArrowRecommendation {
  arrow: ArrowSpecification
  spine_specification: SpineSpecification
  compatibility_score: number
  compatibility_rating: 'excellent' | 'good' | 'poor'
  match_percentage: number
  reasons: string[]
  price_per_arrow?: number
}

export interface TuningSession {
  id: string
  archer_profile: UserProfile
  bow_config: BowConfiguration
  recommended_spine: number | string
  recommended_arrows: ArrowRecommendation[]
  created_at: string
  notes?: string
}

export interface DatabaseStats {
  total_arrows: number
  total_manufacturers: number
  manufacturers: Array<{
    manufacturer: string
    count: number
  }>
  spine_range: {
    min: number
    max: number
  }
  diameter_range: {
    min: number
    max: number
  }
  gpi_range: {
    min: number
    max: number
  }
}

// Component Types
export interface ComponentSpecification {
  [key: string]: any
  // Common fields across all components
  weight?: string
  material?: string
  // Point-specific
  thread_type?: string
  diameter?: number
  length?: number
  point_type?: 'field' | 'broadhead' | 'blunt' | 'judo'
  // Nock-specific
  nock_size?: string
  fit_type?: 'push_in' | 'snap_on' | 'pin'
  colors?: string[]
  throat_size?: number
  // Fletching-specific
  height?: number
  profile?: 'low' | 'high' | 'parabolic'
  attachment?: 'adhesive' | 'wrap'
  // Insert-specific
  outer_diameter?: number
  inner_diameter?: number
  thread?: string
  type?: 'insert' | 'outsert' | 'combo'
}

export interface ComponentData {
  id: number
  category_id: number
  category_name: string
  manufacturer: string
  model_name: string
  specifications: ComponentSpecification
  compatibility_rules?: any
  image_url?: string
  local_image_path?: string
  price_range?: string
  description?: string
  source_url?: string
  scraped_at?: string
  created_at: string
}

export interface ComponentCategory {
  id: number
  name: string
  description: string
  count: number
}

export interface ComponentStatistics {
  total_components: number
  categories: ComponentCategory[]
  compatibility_stats: {
    [key: string]: number
  }
  manufacturers: Array<{
    manufacturer: string
    component_count: number
  }>
}

export interface CompatibilityResult {
  arrow_id: number
  component_id: number
  compatibility_type: 'direct' | 'universal' | 'adapter_required' | 'incompatible'
  score: number
  matching_rules: string[]
  notes: string
  compatible: boolean
}