import type { 
  ArrowSpecification, 
  ArrowSearchFilters, 
  BowConfiguration, 
  ArrowRecommendation,
  TuningSession,
  DatabaseStats 
} from '~/types/arrow'

export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase as string

  // Generic API request function
  const apiRequest = async <T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> => {
    const url = `${baseURL}${endpoint}`
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    }
    
    const response = await fetch(url, { ...defaultOptions, ...options })
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`)
    }
    
    return response.json()
  }

  // Arrow Database API
  const getArrows = async (filters: ArrowSearchFilters = {}) => {
    const params = new URLSearchParams()
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    
    const queryString = params.toString()
    const endpoint = `/arrows${queryString ? `?${queryString}` : ''}`
    
    return apiRequest<{
      arrows: ArrowSpecification[]
      total: number
      page: number
      per_page: number
      total_pages: number
    }>(endpoint)
  }

  const getArrowDetails = async (arrowId: number) => {
    return apiRequest<ArrowSpecification>(`/arrows/${arrowId}`)
  }

  const getDatabaseStats = async () => {
    return apiRequest<DatabaseStats>('/database/stats')
  }

  // Tuning API
  const calculateSpine = async (bowConfig: BowConfiguration) => {
    return apiRequest<{
      recommended_spine: number | string
      spine_range: {
        min: number | string
        max: number | string
      }
      calculations: {
        base_spine: number
        adjustments: Record<string, number>
        final_spine: number | string
      }
    }>('/tuning/calculate-spine', {
      method: 'POST',
      body: JSON.stringify(bowConfig)
    })
  }

  const getArrowRecommendations = async (bowConfig: BowConfiguration) => {
    return apiRequest<{
      recommended_arrows: ArrowRecommendation[]
      total_compatible: number
      bow_config: BowConfiguration
      recommended_spine: number | string
    }>('/tuning/recommendations', {
      method: 'POST',
      body: JSON.stringify(bowConfig)
    })
  }

  const createTuningSession = async (sessionData: Omit<TuningSession, 'id' | 'created_at'>) => {
    return apiRequest<TuningSession>('/tuning/sessions', {
      method: 'POST',
      body: JSON.stringify(sessionData)
    })
  }

  const getTuningSession = async (sessionId: string) => {
    return apiRequest<TuningSession>(`/tuning/sessions/${sessionId}`)
  }

  const getTuningSessions = async () => {
    return apiRequest<TuningSession[]>('/tuning/sessions')
  }

  // Manufacturer API
  const getManufacturers = async () => {
    return apiRequest<Array<{ 
      manufacturer: string 
      count: number 
      arrow_types: string[]
    }>>('/manufacturers')
  }
  
  // Materials API
  const getMaterials = async () => {
    return apiRequest<Array<{ 
      material: string 
      count: number 
    }>>('/materials')
  }

  const getGroupedMaterials = async () => {
    return apiRequest<Array<{ 
      material: string 
      count: number 
    }>>('/materials/grouped')
  }

  const getArrowTypes = async () => {
    return apiRequest<Array<{ 
      arrow_type: string 
      count: number 
    }>>('/arrow-types')
  }

  // Health check
  const healthCheck = async () => {
    return apiRequest<{ 
      status: string
      timestamp: string
      version: string
      database_status: string
    }>('/health')
  }

  return {
    // Arrow Database
    getArrows,
    getArrowDetails,
    getDatabaseStats,
    
    // Tuning
    calculateSpine,
    getArrowRecommendations,
    createTuningSession,
    getTuningSession,
    getTuningSessions,
    
    // Manufacturers
    getManufacturers,
    getMaterials,
    getGroupedMaterials,
    getArrowTypes,
    
    // System
    healthCheck,
    
    // Generic request
    apiRequest
  }
}