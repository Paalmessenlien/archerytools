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
      const api = useApi()
      const result = await api.calculateSpine(bowConfig.value)
      recommendedSpine.value = result.recommended_spine
      lastCalculation.value = new Date()
    } catch (error) {
      console.error('Error calculating spine:', error)
      console.warn('API failed, falling back to client-side calculation')
      
      // Fallback to client-side calculation
      recommendedSpine.value = calculateSpineClientSide()
      lastCalculation.value = new Date()
    } finally {
      isLoading.value = false
    }
  }

  // Client-side spine calculation fallback
  const calculateSpineClientSide = () => {
    const drawWeight = bowConfig.value.draw_weight || 45  // Bow's marked draw weight
    const arrowLength = bowConfig.value.arrow_length || 29  // Physical arrow length
    const pointWeight = bowConfig.value.point_weight || 125
    const bowType = bowConfig.value.bow_type || 'compound'
    const arrowMaterial = bowConfig.value.arrow_material || 'carbon'
    // NOTE: draw_length is NOT used in spine calculations - only for archer information
    
    // Check if wood material is specifically selected - use wood calculation
    if (arrowMaterial && arrowMaterial.toLowerCase() === 'wood') {
      // Wood arrow calculation (returns spine in pounds)
      let baseSpine = drawWeight
      
      // Adjust for arrow length - wood arrows are less sensitive to length
      const lengthAdjustment = (arrowLength - 28) * 2
      baseSpine += lengthAdjustment
      
      // Wood arrow point weight adjustment (much more sensitive)
      // Point weight adjustment table: 30gn=1, 70gn=2, 100gn=3, 125gn=4
      const pointWeightTable = { 30: 1, 70: 2, 100: 3, 125: 4 }
      const closestWeight = Object.keys(pointWeightTable).reduce((prev, curr) => 
        Math.abs(curr - pointWeight) < Math.abs(prev - pointWeight) ? curr : prev
      )
      const pointAdjustmentValue = pointWeightTable[closestWeight]
      const baselineAdjustment = 3 // 100gn baseline
      const pointAdjustment = (pointAdjustmentValue - baselineAdjustment) * 2.5
      baseSpine += pointAdjustment
      
      return Math.round(baseSpine) + '#' // Wood spine notation
    } else {
      // Carbon/aluminum arrow calculation
      let baseSpine = drawWeight * 12.5
      
      // Adjust for arrow length (longer = weaker/higher spine number)
      const lengthAdjustment = (arrowLength - 28) * 25
      baseSpine += lengthAdjustment
      
      // Adjust for point weight (heavier = weaker/higher spine number)
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