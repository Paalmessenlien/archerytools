<template>
  <div class="bow-setup-picker">
    <!-- Responsive Picker for All Screen Sizes -->
    <div class="responsive-picker">
      <div class="picker-container bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div class="px-4 mx-auto max-w-6xl sm:px-6 lg:px-6 py-1.5">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-1.5 md:space-x-3">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400 hidden md:inline">Active Bow:</span>
              
              <!-- Selected Bow Display with dropdown -->
              <div class="relative">
                <button
                  @click="openPicker"
                  class="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg md:rounded-full border border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700 transition-colors text-sm"
                  :class="{ 'bg-primary-100 text-primary-800 border-primary-500 dark:bg-primary-900 dark:text-primary-200': hasSelectedBow }"
                >
                  <i class="fas fa-bow-arrow text-sm"></i>
                  <span class="font-medium">{{ mobileDisplayText }}</span>
                  <i class="fas fa-chevron-down text-xs"></i>
                </button>

                <!-- Responsive Dropdown -->
                <div
                  v-if="isPickerOpen"
                  class="picker-dropdown absolute top-full left-0 mt-1 w-screen max-w-sm md:w-80 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg z-50"
                >
                  <div class="p-4">
                    <div class="flex items-center justify-between mb-3">
                      <h3 class="font-medium text-gray-900 dark:text-gray-100">Select Bow Setup</h3>
                      <button
                        @click="closePicker"
                        class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                      >
                        <i class="fas fa-times text-sm"></i>
                      </button>
                    </div>

                    <!-- Loading State -->
                    <div v-if="isLoading" class="flex items-center justify-center py-8">
                      <div class="loading-spinner"></div>
                      <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading bow setups...</span>
                    </div>

                    <!-- Bow Options -->
                    <div v-else class="space-y-2">
                      <!-- No Bow Option -->
                      <button
                        @click="handleSelectBowSetup(null)"
                        class="w-full text-left p-3 rounded-lg border border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700 transition-colors"
                        :class="{ 'bg-primary-100 border-primary-500 dark:bg-primary-900 dark:border-primary-400': !hasSelectedBow }"
                      >
                        <div class="flex items-center">
                          <i class="fas fa-ban text-gray-500 dark:text-gray-400 mr-3"></i>
                          <div>
                            <div class="font-medium text-gray-900 dark:text-gray-100">No Bow Selected</div>
                            <div class="text-sm text-gray-600 dark:text-gray-400">Use manual configuration</div>
                          </div>
                        </div>
                      </button>

                      <!-- Bow Setups List -->
                      <div v-if="availableBowSetups.length === 0" class="text-center py-8">
                        <i class="fas fa-bow-arrow text-4xl text-gray-500 dark:text-gray-400 mb-2"></i>
                        <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">No bow setups found</p>
                        <NuxtLink
                          to="/my-setup"
                          class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-full text-sm font-medium hover:bg-primary-700 transition-colors"
                          @click="closePicker"
                        >
                          <i class="fas fa-plus mr-2"></i>
                          Create Bow Setup
                        </NuxtLink>
                      </div>

                      <div v-else class="max-h-60 overflow-y-auto space-y-2">
                        <button
                          v-for="bowSetup in availableBowSetups"
                          :key="bowSetup.id"
                          @click="handleSelectBowSetup(bowSetup)"
                          class="w-full text-left p-3 rounded-lg border border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700 transition-colors"
                          :class="{ 
                            'bg-primary-100 border-primary-500 dark:bg-primary-900 dark:border-primary-400': selectedBowSetup?.id === bowSetup.id 
                          }"
                        >
                          <div class="flex items-center">
                            <i class="fas fa-bow-arrow text-primary-600 dark:text-primary-400 mr-3"></i>
                            <div class="flex-1 min-w-0">
                              <div class="font-medium text-gray-900 dark:text-gray-100 truncate">{{ bowSetup.name }}</div>
                              <div class="text-sm text-gray-600 dark:text-gray-400">
                                {{ bowSetup.draw_weight || bowSetup.bow_config?.draw_weight }}lbs • 
                                {{ formatBowType(bowSetup.bow_type || bowSetup.bow_config?.bow_type) }} • 
                                {{ bowSetup.draw_length || bowSetup.bow_config?.draw_length }}" draw
                              </div>
                            </div>
                            <i 
                              v-if="selectedBowSetup?.id === bowSetup.id"
                              class="fas fa-check text-primary-600 dark:text-primary-400 ml-2"
                            ></i>
                          </div>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Quick Actions for Selected Bow -->
              <div v-if="hasSelectedBow" class="flex items-center space-x-2">
                <!-- Quick Link to Bow Setup -->
                <NuxtLink
                  :to="`/setups/${selectedBowSetup.id}`"
                  class="p-1.5 rounded-full hover:bg-blue-100 text-blue-600 hover:text-blue-800 dark:hover:bg-blue-900 dark:text-blue-400 dark:hover:text-blue-200 transition-colors"
                  title="Go to bow setup details"
                >
                  <i class="fas fa-external-link-alt text-sm"></i>
                </NuxtLink>
                
                <!-- Clear Selection Button -->
                <button
                  @click="clearSelection"
                  class="p-1.5 rounded-full hover:bg-red-100 text-red-600 hover:text-red-800 dark:hover:bg-red-900 dark:text-red-400 dark:hover:text-red-200 transition-colors"
                  title="Clear bow selection"
                >
                  <i class="fas fa-times text-sm"></i>
                </button>
              </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="flex items-center space-x-3">
              <NuxtLink
                to="/my-setup"
                class="hidden md:inline-flex items-center px-3 py-1.5 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 transition-colors"
              >
                <i class="fas fa-cog mr-1.5"></i>
                <span class="hidden sm:inline">Manage Bows</span>
                <span class="sm:hidden">Manage</span>
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useBowSetupPickerStore } from '~/stores/bowSetupPicker'
import { useBowConfigStore } from '~/stores/bowConfig'
import { useAuth } from '~/composables/useAuth'
import type { BowSetup } from '~/types/arrow'

// No props needed - component is now responsive for all screen sizes

// Store access
const bowSetupPickerStore = useBowSetupPickerStore()
const {
  selectedBowSetup,
  availableBowSetups,
  isLoading,
  hasSelectedBow,
  selectedBowName,
  bowDisplayText
} = storeToRefs(bowSetupPickerStore)

const {
  loadBowSetups,
  clearSelection
} = bowSetupPickerStore

// Local selectBowSetup that also closes the picker
const handleSelectBowSetup = (bowSetup: BowSetup | null) => {
  bowSetupPickerStore.selectBowSetup(bowSetup)
  closePicker()
}

// Local picker open state (not shared between desktop and mobile instances)
const isPickerOpen = ref(false)

// Local picker methods
const togglePicker = () => {
  isPickerOpen.value = !isPickerOpen.value
}

const closePicker = () => {
  isPickerOpen.value = false
}

const openPicker = () => {
  if (availableBowSetups.value.length === 0) {
    loadBowSetups()
  }
  isPickerOpen.value = true
}

// Utility functions
const formatBowType = (bowType: string): string => {
  const typeMap = {
    'compound': 'Compound',
    'recurve': 'Recurve',
    'longbow': 'Longbow',
    'traditional': 'Traditional'
  }
  return typeMap[bowType] || bowType
}

// Mobile display text with character limit
const mobileDisplayText = computed(() => {
  const text = bowDisplayText.value
  // Limit to 20 characters on mobile screens
  if (text.length > 20) {
    return text.substring(0, 17) + '...'
  }
  return text
})

// Close picker when clicking outside
const handleClickOutside = (event: Event) => {
  if (isPickerOpen.value) {
    const target = event.target as HTMLElement
    if (!target.closest('.relative') && !target.closest('.picker-dropdown')) {
      closePicker()
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.loading-spinner {
  @apply animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-primary-500 dark:border-gray-600 dark:border-t-primary-400;
}

/* Custom scrollbar for bow setups list */
.max-h-60::-webkit-scrollbar {
  width: 4px;
}

.max-h-60::-webkit-scrollbar-track {
  @apply bg-transparent;
}

.max-h-60::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

.max-h-60::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}
</style>