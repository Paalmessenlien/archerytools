import type { 
  ArrowSpecification, 
  ArrowSearchFilters, 
  BowConfiguration, 
  ArrowRecommendation,
  TuningSession,
  DatabaseStats,
  ComponentData,
  ComponentStatistics,
  CompatibilityResult
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
    
    // Get token from localStorage for authentication
    const token = process.client ? localStorage.getItem('token') : null
    
    // Build headers, but don't set Content-Type for FormData (browser will set it with boundary)
    const headers: Record<string, string> = {
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    }
    
    // Only set Content-Type if it's not FormData
    const isFormData = options.body instanceof FormData
    if (!isFormData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json'
    }
    
    const defaultOptions: RequestInit = {
      headers,
    }
    
    const response = await fetch(url, { ...defaultOptions, ...options })
    
    if (!response.ok) {
      const errorData = await response.text();
      // Log errors for debugging but don't spam console for successful requests
      if (response.status >= 400) {
        console.error(`API Error ${response.status}:`, errorData);
      }
      throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorData}`)
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

  // Components API
  const getComponents = async (params: {
    category?: string
    manufacturer?: string
    limit?: number
  } = {}) => {
    const queryParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString())
      }
    })
    
    const queryString = queryParams.toString()
    const endpoint = `/components${queryString ? `?${queryString}` : ''}`
    
    return apiRequest<{
      components: ComponentData[]
      total: number
      filters: Record<string, any>
    }>(endpoint)
  }

  const getComponentCategories = async () => {
    return apiRequest<{
      categories: Array<{
        name: string
        count: number
      }>
      total_categories: number
    }>('/components/categories')
  }

  const getComponentStatistics = async () => {
    return apiRequest<ComponentStatistics>('/components/statistics')
  }

  const getCompatibleComponents = async (arrowId: number, params: {
    category?: string
    limit?: number
  } = {}) => {
    const queryParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString())
      }
    })
    
    const queryString = queryParams.toString()
    const endpoint = `/arrows/${arrowId}/compatible-components${queryString ? `?${queryString}` : ''}`
    
    return apiRequest<{
      arrow_id: number
      compatible_components: ComponentData[]
      total: number
      category_filter?: string
    }>(endpoint)
  }

  const checkCompatibility = async (arrowId: number, componentId: number) => {
    return apiRequest<CompatibilityResult>('/compatibility/check', {
      method: 'POST',
      body: JSON.stringify({ arrow_id: arrowId, component_id: componentId })
    })
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

  // HTTP method helpers
  const get = async <T>(endpoint: string, options: RequestInit = {}) => {
    return apiRequest<T>(endpoint, { ...options, method: 'GET' })
  }

  const post = async <T>(endpoint: string, data?: any, options: RequestInit = {}) => {
    return apiRequest<T>(endpoint, {
      method: 'POST',
      body: data instanceof FormData ? data : (data ? JSON.stringify(data) : undefined),
      ...options
    })
  }

  const put = async <T>(endpoint: string, data?: any, options: RequestInit = {}) => {
    return apiRequest<T>(endpoint, {
      method: 'PUT',
      body: data instanceof FormData ? data : (data ? JSON.stringify(data) : undefined),
      ...options
    })
  }

  const del = async <T>(endpoint: string, options: RequestInit = {}) => {
    return apiRequest<T>(endpoint, { ...options, method: 'DELETE' })
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
    
    // Components
    getComponents,
    getComponentCategories,
    getComponentStatistics,
    getCompatibleComponents,
    checkCompatibility,
    
    // System
    healthCheck,
    
    // HTTP methods
    get,
    post,
    put,
    delete: del,
    
    // Generic request
    apiRequest
  }
}