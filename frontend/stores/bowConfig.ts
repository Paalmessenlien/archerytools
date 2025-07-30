import { defineStore } from 'pinia'
import type { BowConfiguration, ArrowRecommendation } from '~/types/arrow'

export const useBowConfigStore = defineStore('bowConfig', () => {
  // State
  const bowConfig = ref<BowConfiguration>({
    draw_weight: 45,
    draw_length: 28,
    bow_type: 'compound',
    arrow_length: 29,
    point_weight: 125,
    arrow_material: 'carbon',
    arrow_rest_type: 'drop-away',
    nock_type: 'pin',
    vane_type: 'plastic',
    vane_length: 4,
    number_of_vanes: 3
  })

  const recommendedSpine = ref<number | string | null>(null)
  const recommendations = ref<ArrowRecommendation[]>([])
  const isLoading = ref(false)
  const lastCalculation = ref<Date | null>(null)

  // Getters
  const isCompoundBow = computed(() => bowConfig.value.bow_type === 'compound')
  const isTraditionalBow = computed(() => ['longbow', 'traditional'].includes(bowConfig.value.bow_type))
  const arrowSetupDescription = computed(() => {
    return `${bowConfig.value.arrow_length}" arrow with ${bowConfig.value.point_weight}gn point`
  })

  const configSummary = computed(() => {
    return `${bowConfig.value.draw_weight}lbs @ ${bowConfig.value.draw_length}"`
  })

  // Actions
  const updateBowConfig = (updates: Partial<BowConfiguration>) => {
    // Apply the updates first
    const newConfig = { ...bowConfig.value, ...updates }
    
    // Auto-select appropriate arrow material based on bow type
    if ('bow_type' in updates) {
      if (updates.bow_type === 'longbow' || updates.bow_type === 'traditional') {
        // Automatically set to Wood for traditional bows (unless material was explicitly set)
        if (!('arrow_material' in updates)) {
          newConfig.arrow_material = 'Wood'
        }
      } else if (updates.bow_type === 'compound' || updates.bow_type === 'recurve') {
        // Automatically set to Carbon for modern bows (unless material was explicitly set)
        if (!('arrow_material' in updates)) {
          newConfig.arrow_material = 'Carbon'
        }
      }
    }
    
    bowConfig.value = newConfig
  }

  const resetBowConfig = () => {
    bowConfig.value = {
      draw_weight: 45,
      draw_length: 28,
      bow_type: 'compound',
      arrow_length: 29,
      point_weight: 125,
      arrow_material: 'carbon',
      arrow_rest_type: 'drop-away',
      nock_type: 'pin',
      vane_type: 'plastic',
      vane_length: 4,
      number_of_vanes: 3
    }
    recommendedSpine.value = null
    recommendations.value = []
    lastCalculation.value = null
  }

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
      throw error
    } finally {
      isLoading.value = false
    }
  }

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
    resetBowConfig,
    calculateRecommendedSpine,
    getArrowRecommendations,
    createTuningSession
  }
})