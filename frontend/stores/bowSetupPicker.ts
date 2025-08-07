import { defineStore } from 'pinia'
import { useAuth } from '~/composables/useAuth'
import type { BowSetup, BowConfiguration } from '~/types/arrow'

export const useBowSetupPickerStore = defineStore('bowSetupPicker', () => {
  // State
  const selectedBowSetup = ref<BowSetup | null>(null)
  const availableBowSetups = ref<BowSetup[]>([])
  const isLoading = ref(false)

  // Getters
  const hasSelectedBow = computed(() => selectedBowSetup.value !== null)
  const selectedBowName = computed(() => selectedBowSetup.value?.name || 'No Bow Selected')
  const selectedBowConfig = computed(() => {
    if (!selectedBowSetup.value) return null
    
    const setup = selectedBowSetup.value
    
    // Return nested bow_config if it exists, otherwise create from flattened structure
    return setup.bow_config || {
      draw_weight: setup.draw_weight,
      draw_length: setup.draw_length,
      bow_type: setup.bow_type,
      arrow_length: setup.arrow_length || 29,
      point_weight: setup.point_weight || 125,
      arrow_material: setup.arrow_material || 'carbon'
    }
  })
  
  const bowDisplayText = computed(() => {
    if (!selectedBowSetup.value) return 'Select Bow Setup'
    const setup = selectedBowSetup.value
    // Handle both flattened and nested structure
    const drawWeight = setup.draw_weight || setup.bow_config?.draw_weight
    const bowType = setup.bow_type || setup.bow_config?.bow_type
    return `${setup.name} (${drawWeight}lbs, ${bowType})`
  })

  // Actions
  const loadBowSetups = async () => {
    if (isLoading.value) return

    isLoading.value = true
    try {
      const { fetchBowSetups } = useAuth()
      const response = await fetchBowSetups()
      availableBowSetups.value = response || []
    } catch (error) {
      console.error('Error loading bow setups:', error)
      availableBowSetups.value = []
    } finally {
      isLoading.value = false
    }
  }

  const selectBowSetup = (bowSetup: BowSetup | null) => {
    selectedBowSetup.value = bowSetup
    
    // Update the main bowConfig store if a bow is selected
    if (bowSetup) {
      const bowConfigStore = useBowConfigStore()
      
      // Handle both flattened and nested bow config structure
      const bowConfig = bowSetup.bow_config || {
        draw_weight: bowSetup.draw_weight,
        draw_length: bowSetup.draw_length,
        bow_type: bowSetup.bow_type,
        arrow_length: bowSetup.arrow_length || 29,
        point_weight: bowSetup.point_weight || 125,
        arrow_material: bowSetup.arrow_material || 'carbon'
      }
      
      bowConfigStore.updateBowConfig(bowConfig)
    }
    
    // Save selection to localStorage for persistence
    if (process.client) {
      if (bowSetup) {
        localStorage.setItem('selectedBowSetupId', bowSetup.id?.toString() || '')
      } else {
        localStorage.removeItem('selectedBowSetupId')
      }
    }
  }

  const clearSelection = () => {
    selectBowSetup(null)
  }


  // Initialize selected bow from localStorage
  const initializeSelectedBow = async () => {
    if (!process.client) return

    const savedBowSetupId = localStorage.getItem('selectedBowSetupId')
    if (savedBowSetupId && availableBowSetups.value.length > 0) {
      const bowSetup = availableBowSetups.value.find(b => b.id?.toString() === savedBowSetupId)
      if (bowSetup) {
        selectedBowSetup.value = bowSetup
        
        // Update the main bowConfig store
        const bowConfigStore = useBowConfigStore()
        bowConfigStore.updateBowConfig(bowSetup.bow_config)
      }
    }
  }

  // Auto-load bow setups when user is available
  const { user } = useAuth()
  watch(user, async (newUser) => {
    if (newUser && availableBowSetups.value.length === 0) {
      await loadBowSetups()
      await initializeSelectedBow()
    }
  }, { immediate: true })

  // Initialize when store is created if user already exists
  onMounted(() => {
    if (user.value && availableBowSetups.value.length === 0) {
      loadBowSetups().then(() => initializeSelectedBow())
    }
  })

  return {
    // State
    selectedBowSetup: readonly(selectedBowSetup),
    availableBowSetups: readonly(availableBowSetups),
    isLoading: readonly(isLoading),

    // Getters
    hasSelectedBow,
    selectedBowName,
    selectedBowConfig,
    bowDisplayText,

    // Actions
    loadBowSetups,
    selectBowSetup,
    clearSelection,
    initializeSelectedBow
  }
})