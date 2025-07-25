// Arrow Types and Interfaces

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
  draw_length: number
  bow_type: 'compound' | 'recurve' | 'longbow' | 'traditional'
  arrow_length: number
  arrow_material: 'carbon' | 'aluminum' | 'wood' | 'fiberglass' | 'carbon-aluminum'
  arrow_type?: string
  arrow_rest_type?: 'drop-away' | 'whisker-biscuit' | 'blade'
  point_weight: number
  nock_type: 'pin' | 'press-fit' | 'over-nock' | 'lighted' | 'half-moon'
  vane_type: 'plastic' | 'feather' | 'hybrid' | 'blazer' | 'helical'
  vane_length: number
  number_of_vanes: number
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
  archer_name: string
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