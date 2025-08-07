# State Management - Pinia Stores & Composables

Comprehensive documentation for state management in the Archery Tools frontend using Pinia stores and Vue 3 composables.

## Table of Contents
- [Pinia Store Architecture](#pinia-store-architecture)
- [Bow Configuration Store](#bow-configuration-store)
- [Composables](#composables)
- [State Persistence](#state-persistence)
- [Usage Patterns](#usage-patterns)
- [Best Practices](#best-practices)

---

## Pinia Store Architecture

### Overview
The frontend uses Pinia for centralized state management, providing reactive state that persists across components and pages. The architecture follows Vue 3 Composition API patterns with TypeScript support.

### Store Structure
```
stores/
└── bowConfig.ts        # Bow configuration and calculations
```

### Key Benefits
- **Reactive State**: Automatic UI updates when state changes
- **TypeScript Support**: Full type safety and IntelliSense
- **Modular Design**: Focused stores for specific domains
- **DevTools Integration**: Vue DevTools support for debugging
- **SSR Compatible**: Works with Nuxt 3 server-side rendering

---

## Bow Configuration Store

### Store Definition (`stores/bowConfig.ts`)

#### State Management
```typescript
import { defineStore } from 'pinia'
import type { BowConfiguration, ArrowRecommendation } from '~/types/arrow'

export const useBowConfigStore = defineStore('bowConfig', () => {
  // Core state
  const bowConfig = ref<BowConfiguration>({
    draw_weight: 45,
    draw_length: user.value?.draw_length || 28,
    bow_type: 'compound',
    arrow_length: 29,
    point_weight: 125,
    arrow_material: 'carbon',
    arrow_rest_type: 'drop-away',
    nock_type: 'pin',
    vane_type: 'plastic',
    vane_length: 4,
    number_of_vanes: 3,
    insert_weight: 0,
    vane_weight_per: 5,
    vane_weight_override: false,
    bushing_weight: 0,
    nock_weight: 10
  })

  const recommendedSpine = ref<number | string | null>(null)
  const recommendations = ref<ArrowRecommendation[]>([])
  const isLoading = ref(false)
  const lastCalculation = ref<Date | null>(null)
})
```

#### Computed Properties (Getters)
```typescript
// Getters for derived state
const isCompoundBow = computed(() => bowConfig.value.bow_type === 'compound')
const isTraditionalBow = computed(() => ['longbow', 'traditional'].includes(bowConfig.value.bow_type))

const arrowSetupDescription = computed(() => {
  const material = bowConfig.value.arrow_material
  const materialText = material ? material : 'any material'
  return `${bowConfig.value.arrow_length}" ${materialText} arrow with ${bowConfig.value.point_weight}gn point`
})

const configSummary = computed(() => {
  const drawLength = bowConfig.value.draw_length || 28
  return `${bowConfig.value.draw_weight}lbs bow, ${drawLength}" draw`
})
```

#### Actions (Methods)
```typescript
// Configuration updates
const updateBowConfig = (updates: Partial<BowConfiguration>) => {
  const newConfig = { ...bowConfig.value, ...updates }
  bowConfig.value = newConfig
}

// User profile synchronization
const syncWithUserProfile = () => {
  if (user.value?.draw_length && !bowConfig.value.draw_length) {
    updateBowConfig({ draw_length: user.value.draw_length })
  }
}

// Reset configuration
const resetBowConfig = () => {
  bowConfig.value = {
    draw_weight: 45,
    draw_length: user.value?.draw_length || 28,
    bow_type: 'compound',
    // ... default values
  }
  recommendedSpine.value = null
  recommendations.value = []
}
```

#### API Integration
```typescript
// Spine calculation with fallback
const calculateRecommendedSpine = async () => {
  if (isLoading.value) return

  isLoading.value = true
  try {
    const api = useApi()
    const result = await api.calculateSpine(bowConfig.value)
    recommendedSpine.value = result.recommended_spine
    lastCalculation.value = new Date()
  } catch (error) {
    console.error('Error calculating spine:', error)
    // Fallback to client-side calculation
    recommendedSpine.value = calculateSpineClientSide()
    lastCalculation.value = new Date()
  } finally {
    isLoading.value = false
  }
}

// Arrow recommendations
const getArrowRecommendations = async () => {
  if (isLoading.value) return

  isLoading.value = true
  try {
    const api = useApi()
    const result = await api.getArrowRecommendations(bowConfig.value)
    recommendations.value = result.recommended_arrows
    recommendedSpine.value = result.recommended_spine
    lastCalculation.value = new Date()
  } catch (error) {
    console.error('Error getting recommendations:', error)
    throw error
  } finally {
    isLoading.value = false
  }
}
```

#### Client-Side Calculations
```typescript
// Fallback spine calculation
const calculateSpineClientSide = () => {
  const drawWeight = bowConfig.value.draw_weight || 45
  const arrowLength = bowConfig.value.arrow_length || 29
  const pointWeight = bowConfig.value.point_weight || 125
  const bowType = bowConfig.value.bow_type || 'compound'
  const arrowMaterial = bowConfig.value.arrow_material || 'carbon'
  
  // Wood arrow calculation
  if (arrowMaterial && arrowMaterial.toLowerCase() === 'wood') {
    let baseSpine = drawWeight
    const lengthAdjustment = (arrowLength - 28) * 2
    baseSpine += lengthAdjustment
    
    // Point weight adjustment for wood arrows
    const pointWeightTable = { 30: 1, 70: 2, 100: 3, 125: 4 }
    const closestWeight = Object.keys(pointWeightTable).reduce((prev, curr) => 
      Math.abs(curr - pointWeight) < Math.abs(prev - pointWeight) ? curr : prev
    )
    const pointAdjustmentValue = pointWeightTable[closestWeight]
    const baselineAdjustment = 3
    const pointAdjustment = (pointAdjustmentValue - baselineAdjustment) * 2.5
    baseSpine += pointAdjustment
    
    return Math.round(baseSpine) + '#'
  } else {
    // Carbon/aluminum calculation
    let baseSpine = drawWeight * 12.5
    const lengthAdjustment = (arrowLength - 28) * 25
    baseSpine += lengthAdjustment
    const pointAdjustment = (pointWeight - 125) * 0.5
    baseSpine += pointAdjustment
    
    // Bow type adjustments
    if (bowType === 'recurve') {
      baseSpine += 50
    } else if (bowType === 'traditional' || bowType === 'longbow') {
      baseSpine += 100
    }
    
    return Math.round(baseSpine)
  }
}
```

#### Reactive Watchers
```typescript
// Automatic recalculation on config changes
const shouldRecalculate = computed(() => {
  return [
    bowConfig.value.draw_weight,
    bowConfig.value.draw_length,
    bowConfig.value.bow_type,
    bowConfig.value.arrow_length,
    bowConfig.value.point_weight
  ]
})

watch(shouldRecalculate, async () => {
  await nextTick()
  // Debounced automatic calculation
  setTimeout(() => {
    calculateRecommendedSpine()
  }, 500)
}, { deep: true })

// User profile synchronization
watch(user, () => {
  syncWithUserProfile()
}, { immediate: true })
```

#### Store Export
```typescript
return {
  // State (readonly to prevent direct mutation)
  bowConfig: readonly(bowConfig),
  recommendedSpine: readonly(recommendedSpine),
  recommendations: readonly(recommendations),
  isLoading: readonly(isLoading),
  lastCalculation: readonly(lastCalculation),

  // Getters
  isCompoundBow,
  isTraditionalBow,
  arrowSetupDescription,
  configSummary,

  // Actions
  updateBowConfig,
  syncWithUserProfile,
  resetBowConfig,
  calculateRecommendedSpine,
  getArrowRecommendations,
  createTuningSession
}
```

### Store Usage in Components

#### Basic Usage
```vue
<template>
  <div>
    <p>Current Configuration: {{ configSummary }}</p>
    <p>Recommended Spine: {{ recommendedSpine || 'Calculating...' }}</p>
    
    <md-slider
      :value="bowConfig.draw_weight"
      @input="updateBowConfig({ draw_weight: parseFloat($event.target.value) })"
      min="20"
      max="80"
      step="0.5"
    ></md-slider>
  </div>
</template>

<script setup>
import { useBowConfigStore } from '~/stores/bowConfig'

const bowConfigStore = useBowConfigStore()

// Reactive references
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)
const configSummary = computed(() => bowConfigStore.configSummary)

// Actions
const { updateBowConfig } = bowConfigStore
</script>
```

#### Advanced Usage with Loading States
```vue
<template>
  <div>
    <div v-if="isLoading" class="loading-spinner">
      Calculating recommendations...
    </div>
    
    <div v-else-if="recommendations.length > 0">
      <h3>Recommended Arrows</h3>
      <div v-for="rec in recommendations" :key="rec.arrow.id">
        {{ rec.arrow.manufacturer }} {{ rec.arrow.model_name }}
        ({{ rec.compatibility_score }}% match)
      </div>
    </div>
    
    <CustomButton 
      @click="getArrowRecommendations"
      :disabled="isLoading"
    >
      Get Recommendations
    </CustomButton>
  </div>
</template>

<script setup>
const bowConfigStore = useBowConfigStore()

const isLoading = computed(() => bowConfigStore.isLoading)
const recommendations = computed(() => bowConfigStore.recommendations)

const { getArrowRecommendations } = bowConfigStore
</script>
```

---

## Composables

### `useApi.ts` - API Communication

#### Purpose
Centralized API communication with authentication, error handling, and type safety.

#### Core Structure
```typescript
export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase as string

  // Generic API request with authentication
  const apiRequest = async <T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> => {
    const url = `${baseURL}${endpoint}`
    
    // Get token for authentication
    const token = process.client ? localStorage.getItem('token') : null
    
    const headers: Record<string, string> = {
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    }
    
    // Handle FormData vs JSON
    const isFormData = options.body instanceof FormData
    if (!isFormData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json'
    }
    
    const response = await fetch(url, { ...options, headers })
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`)
    }
    
    return response.json()
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

  return { get, post, put, delete: del }
}
```

#### Specialized API Methods
```typescript
// Arrow database methods
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

// Tuning calculations
const calculateSpine = async (bowConfig: BowConfiguration) => {
  return apiRequest<{
    recommended_spine: number | string
    spine_range: { min: number | string, max: number | string }
    calculations: any
  }>('/tuning/calculate-spine', {
    method: 'POST',
    body: JSON.stringify(bowConfig)
  })
}
```

---

### `useAuth.ts` - Authentication Management

#### Purpose
Handle user authentication, token management, and user profile data.

#### Global State Management
```typescript
// Global state (outside composable function for sharing)
const token = ref<string | null>(null)
const user = ref<UserProfile | null>(null)

export const useAuth = () => {
  // Initialize auth state from localStorage
  const initializeAuth = () => {
    if (process.client) {
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        token.value = storedToken
        fetchUser()
      }
    }
  }

  // Google OAuth login
  const loginWithGoogle = async (tokenResponse: any) => {
    try {
      const api = useApi()
      const response = await api.post('/auth/google', {
        token: tokenResponse.access_token
      })
      
      token.value = response.token
      user.value = response.user
      
      if (process.client) {
        localStorage.setItem('token', response.token)
      }
      
      return { needsProfileCompletion: response.needsProfileCompletion }
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  // Fetch current user profile
  const fetchUser = async () => {
    if (!token.value) return null
    
    try {
      const api = useApi()
      const userData = await api.get('/user')
      user.value = userData
      return userData
    } catch (error) {
      console.error('Failed to fetch user:', error)
      logout()
      return null
    }
  }

  // Logout and clear state
  const logout = () => {
    token.value = null
    user.value = null
    if (process.client) {
      localStorage.removeItem('token')
    }
    navigateTo('/login')
  }

  // Update user profile
  const updateUserProfile = async (updates: Partial<UserProfile>) => {
    try {
      const api = useApi()
      const updatedUser = await api.put('/user/profile', updates)
      user.value = { ...user.value, ...updatedUser }
      return updatedUser
    } catch (error) {
      console.error('Failed to update profile:', error)
      throw error
    }
  }

  return {
    token: readonly(token),
    user: readonly(user),
    loginWithGoogle,
    logout,
    fetchUser,
    updateUserProfile,
    initializeAuth
  }
}
```

---

### `useDarkMode.js` - Theme Management

#### Purpose
Manage dark/light theme with persistence and system preference detection.

#### Implementation
```javascript
export const useDarkMode = () => {
  const isDark = ref(false)

  const toggleDarkMode = () => {
    isDark.value = !isDark.value
    document.documentElement.classList.toggle('dark', isDark.value)
    
    // Persist preference
    if (process.client) {
      localStorage.setItem('darkMode', isDark.value ? 'dark' : 'light')
    }
  }

  const setDarkMode = (dark) => {
    isDark.value = dark
    document.documentElement.classList.toggle('dark', dark)
    
    if (process.client) {
      localStorage.setItem('darkMode', dark ? 'dark' : 'light')
    }
  }

  // Initialize theme on client
  const initializeDarkMode = () => {
    if (process.client) {
      const stored = localStorage.getItem('darkMode')
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      
      const shouldBeDark = stored ? stored === 'dark' : prefersDark
      setDarkMode(shouldBeDark)
    }
  }

  return {
    isDark: readonly(isDark),
    toggleDarkMode,
    setDarkMode,
    initializeDarkMode
  }
}
```

---

## State Persistence

### localStorage Integration
```typescript
// Persist bow configuration
const persistBowConfig = () => {
  if (process.client) {
    localStorage.setItem('bowConfig', JSON.stringify(bowConfig.value))
  }
}

// Restore bow configuration
const restoreBowConfig = () => {
  if (process.client) {
    const stored = localStorage.getItem('bowConfig')
    if (stored) {
      try {
        const config = JSON.parse(stored)
        bowConfig.value = { ...bowConfig.value, ...config }
      } catch (error) {
        console.error('Failed to restore bow config:', error)
      }
    }
  }
}
```

### Session Storage for Temporary State
```typescript
// Store temporary navigation state
const setNavigationState = (state: NavigationState) => {
  if (process.client) {
    sessionStorage.setItem('navigationState', JSON.stringify(state))
  }
}

const getNavigationState = (): NavigationState | null => {
  if (process.client) {
    const stored = sessionStorage.getItem('navigationState')
    return stored ? JSON.parse(stored) : null
  }
  return null
}
```

---

## Usage Patterns

### Component Integration Pattern
```vue
<template>
  <div>
    <!-- Use computed properties for reactive UI -->
    <h2>{{ configSummary }}</h2>
    
    <!-- Direct store method calls -->
    <CustomButton @click="handleCalculate">
      Calculate Spine
    </CustomButton>
    
    <!-- Conditional rendering based on store state -->
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="recommendedSpine">
      Recommended Spine: {{ recommendedSpine }}
    </div>
  </div>
</template>

<script setup>
// Import store
import { useBowConfigStore } from '~/stores/bowConfig'

// Get store instance
const bowConfigStore = useBowConfigStore()

// Extract reactive properties
const configSummary = computed(() => bowConfigStore.configSummary)
const isLoading = computed(() => bowConfigStore.isLoading)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)

// Extract actions
const { calculateRecommendedSpine } = bowConfigStore

// Component methods
const handleCalculate = async () => {
  await calculateRecommendedSpine()
}
</script>
```

### Cross-Component Communication
```vue
<!-- Component A: Update state -->
<script setup>
const bowConfigStore = useBowConfigStore()
const { updateBowConfig } = bowConfigStore

const handleUpdate = () => {
  updateBowConfig({ draw_weight: 50 })
}
</script>

<!-- Component B: React to state changes -->
<script setup>
const bowConfigStore = useBowConfigStore()
const bowConfig = computed(() => bowConfigStore.bowConfig)

// Automatically reactive to changes from Component A
watch(bowConfig, (newConfig) => {
  console.log('Config updated:', newConfig)
}, { deep: true })
</script>
```

---

## Best Practices

### Store Organization
1. **Single Responsibility**: Each store handles one domain
2. **Readonly State**: Prevent direct mutations outside store
3. **Computed Properties**: Use getters for derived state
4. **Action Methods**: Centralize business logic in store actions

### Performance Optimization
1. **Debounced Updates**: Prevent excessive API calls
2. **Selective Reactivity**: Watch only necessary properties
3. **Client-Side Fallbacks**: Provide fallback calculations
4. **Lazy Loading**: Load data only when needed

### Error Handling
```typescript
const handleError = (error: Error, context: string) => {
  console.error(`Error in ${context}:`, error)
  
  // User-friendly error display
  showNotification({
    type: 'error',
    message: 'Something went wrong. Please try again.',
    details: error.message
  })
}
```

### Type Safety
```typescript
// Define strong types for store state
interface BowConfigState {
  bowConfig: BowConfiguration
  recommendedSpine: number | string | null
  recommendations: ArrowRecommendation[]
  isLoading: boolean
  lastCalculation: Date | null
}

// Use type guards for safe property access
const hasRecommendations = (state: BowConfigState): boolean => {
  return state.recommendations && state.recommendations.length > 0
}
```

This state management documentation provides a complete understanding of how data flows through the application and how to effectively use Pinia stores and composables for reactive, type-safe state management.