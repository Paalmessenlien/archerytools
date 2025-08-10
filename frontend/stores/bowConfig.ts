import { defineStore } from 'pinia'
import type { BowConfiguration, ArrowRecommendation } from '~/types/arrow'

export const useBowConfigStore = defineStore('bowConfig', () => {
  // Get user data to initialize with profile draw_length
  const { user } = useAuth()
  
  // State - initialize with user profile data when available
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
    // Arrow component weights with defaults set to 0 unless picked
    insert_weight: 0,       // Grains - no insert by default
    vane_weight_per: 5,     // Grains per vane - typical plastic vane
    vane_weight_override: false, // Boolean - whether to use manual vane weight
    bushing_weight: 0,      // Grains - no bushing by default
    nock_weight: 10         // Grains - typical nock weight
  })

  const recommendedSpine = ref<number | string | null>(null)
  const recommendations = ref<ArrowRecommendation[]>([])
  const isLoading = ref(false)
  const lastCalculation = ref<Date | null>(null)

  // Getters
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

  // Actions
  const updateBowConfig = (updates: Partial<BowConfiguration>) => {
    // Apply the updates directly - let users choose any material for any bow type
    const newConfig = { ...bowConfig.value, ...updates }
    bowConfig.value = newConfig
  }

  const syncWithUserProfile = () => {
    // Update bow config with user profile draw_length if no specific bow setup is loaded
    if (user.value?.draw_length && !bowConfig.value.draw_length) {
      updateBowConfig({ draw_length: user.value.draw_length })
    } else if (user.value?.draw_length && bowConfig.value.draw_length === 28) {
      // Update if still using default value
      updateBowConfig({ draw_length: user.value.draw_length })
    }
  }

  const resetBowConfig = () => {
    bowConfig.value = {
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
      // Arrow component weights with defaults set to 0 unless picked
      insert_weight: 0,       // Grains - no insert by default
      vane_weight_per: 5,     // Grains per vane - typical plastic vane
      vane_weight_override: false, // Boolean - whether to use manual vane weight
      bushing_weight: 0,      // Grains - no bushing by default
      nock_weight: 10         // Grains - typical nock weight
    }
    recommendedSpine.value = null
    recommendations.value = []
    lastCalculation.value = null
  }

  const calculateRecommendedSpine = async () => {
    if (isLoading.value) return

    isLoading.value = true
    try {
      // Use the centralized calculation system
      const { calculateSpineAPI } = await import('~/utils/spineCalculation')
      const api = useApi()
      const result = await calculateSpineAPI(bowConfig.value, api)
      recommendedSpine.value = result.recommended_spine
      lastCalculation.value = new Date()
    } catch (error) {
      console.error('Error calculating spine:', error)
      console.warn('API failed, falling back to deprecated client-side calculation')
      
      // Use the deprecated fallback from centralized system
      const { calculateSpineFallback } = await import('~/utils/spineCalculation')
      recommendedSpine.value = calculateSpineFallback(bowConfig.value)
      lastCalculation.value = new Date()
    } finally {
      isLoading.value = false
    }
  }

  // Note: Client-side calculation moved to ~/utils/spineCalculation.ts
  // This ensures consistent calculation logic across the entire application

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

  const createTuningSession = async (archerName: string, notes?: string) => {
    const api = useApi()
    return api.createTuningSession({
      archer_name: archerName,
      bow_config: bowConfig.value,
      recommended_spine: recommendedSpine.value || 0,
      recommended_arrows: recommendations.value,
      notes
    })
  }

  // Watchers for automatic recalculation
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
    // Debounce automatic calculation
    setTimeout(() => {
      calculateRecommendedSpine()
    }, 500)
  }, { deep: true })

  // Watch for user changes and sync bow config
  watch(user, () => {
    syncWithUserProfile()
  }, { immediate: true })

  return {
    // State
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
})