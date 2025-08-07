<template>
  <div class="bow-setup-picker" :class="{ 'mobile': isMobile }">
    <!-- Desktop Version -->
    <div v-if="!isMobile" class="desktop-picker">
      <div class="picker-container bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div class="container mx-auto px-4 py-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Active Bow:</span>
              
              <!-- Selected Bow Display with dropdown -->
              <div class="relative">
                <button
                  @click="openPicker"
                  class="flex items-center space-x-2 px-3 py-1.5 rounded-full border border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700 transition-colors"
                  :class="{ 'bg-primary-100 text-primary-800 border-primary-500 dark:bg-primary-900 dark:text-primary-200': hasSelectedBow }"
                >
                  <i class="fas fa-bow-arrow text-sm"></i>
                  <span class="font-medium">{{ bowDisplayText }}</span>
                  <i class="fas fa-chevron-down text-xs"></i>
                </button>

                <!-- Desktop Dropdown (positioned relative to button) -->
                <div
                  v-if="isPickerOpen"
                  class="picker-dropdown absolute top-full left-0 mt-1 w-80 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg z-50"
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
                          to="/my-page"
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
              
              <!-- Clear Selection Button -->
              <button
                v-if="hasSelectedBow"
                @click="clearSelection"
                class="p-1.5 rounded-full hover:bg-red-100 text-red-600 hover:text-red-800 dark:hover:bg-red-900 dark:text-red-400 dark:hover:text-red-200 transition-colors"
                title="Clear bow selection"
              >
                <i class="fas fa-times text-sm"></i>
              </button>
            </div>
            
            <!-- Quick Actions -->
            <div class="flex items-center space-x-2">
              <NuxtLink
                to="/my-page"
                class="text-xs text-gray-600 hover:text-primary-600 dark:text-gray-400 dark:hover:text-primary-400 transition-colors"
              >
                Manage Bows
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Version -->
    <div v-else class="mobile-picker">
      <button
        @click="togglePicker"
        class="flex flex-col items-center justify-center p-2 w-16 h-16 rounded-2xl transition-all duration-200"
        :class="hasSelectedBow 
          ? 'bg-primary-100 text-primary-700 dark:bg-primary-800 dark:text-primary-200' 
          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'"
      >
        <div class="relative mb-1">
          <i class="fas fa-cogs text-xl"></i>
          <div v-if="hasSelectedBow" class="absolute -top-1 -right-1 w-2 h-2 bg-primary-500 rounded-full"></div>
        </div>
        <span class="text-xs font-medium max-w-[60px] truncate leading-tight">
          {{ hasSelectedBow ? selectedBowName.split(' ')[0] : 'Setup' }}
        </span>
      </button>
    </div>

    <!-- Mobile Picker Modal (only on mobile screens) -->
    <teleport to="body">
      <div
        v-if="isMobile && isPickerOpen"
        class="fixed inset-0 z-[60] block md:hidden"
      >
        <!-- Overlay -->
        <div
          class="fixed inset-0 bg-black bg-opacity-40 z-[60]"
          @click="closePicker"
        ></div>
        
        <!-- Modal Content -->
        <div class="fixed bottom-20 left-4 right-4 max-h-[70vh] bg-white dark:bg-gray-800 rounded-xl shadow-xl overflow-hidden z-[70]">
          <!-- Header -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Select Bow</h3>
            <button
              @click="closePicker"
              class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <i class="fas fa-times text-lg"></i>
            </button>
          </div>

          <!-- Content -->
          <div class="p-4">
            <!-- Loading State -->
            <div v-if="isLoading" class="flex items-center justify-center py-8">
              <div class="loading-spinner mr-3"></div>
              <span class="text-sm text-gray-600 dark:text-gray-400">Loading...</span>
            </div>

            <!-- Options -->
            <div v-else class="space-y-2">
              <!-- No Bow Option -->
              <button
                @click="handleSelectBowSetup(null)"
                class="w-full text-left p-3 rounded-lg border border-gray-200 dark:border-gray-700 transition-colors"
                :class="!hasSelectedBow 
                  ? 'bg-primary-50 border-primary-300 dark:bg-primary-950 dark:border-primary-700' 
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700'"
              >
                <div class="flex items-center">
                  <i class="fas fa-ban text-gray-400 dark:text-gray-500 mr-3"></i>
                  <div class="flex-1">
                    <div class="font-medium text-gray-900 dark:text-gray-100">No Bow</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Manual configuration</div>
                  </div>
                  <div v-if="!hasSelectedBow" class="w-2 h-2 bg-primary-500 rounded-full"></div>
                </div>
              </button>

              <!-- Empty State -->
              <div v-if="availableBowSetups.length === 0" class="text-center py-8">
                <i class="fas fa-bow-arrow text-2xl text-gray-400 dark:text-gray-500 mb-3"></i>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">No bow setups found</p>
                <NuxtLink
                  to="/my-page"
                  class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
                  @click="closePicker"
                >
                  <i class="fas fa-plus mr-2"></i>
                  Create Setup
                </NuxtLink>
              </div>

              <!-- Bow List -->
              <div v-else class="max-h-60 overflow-y-auto space-y-2">
                <button
                  v-for="bowSetup in availableBowSetups"
                  :key="bowSetup.id"
                  @click="handleSelectBowSetup(bowSetup)"
                  class="w-full text-left p-3 rounded-lg border border-gray-200 dark:border-gray-700 transition-colors"
                  :class="selectedBowSetup?.id === bowSetup.id
                    ? 'bg-primary-50 border-primary-300 dark:bg-primary-950 dark:border-primary-700'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'"
                >
                  <div class="flex items-center">
                    <i class="fas fa-bow-arrow text-primary-600 dark:text-primary-400 mr-3"></i>
                    <div class="flex-1 min-w-0">
                      <div class="font-medium text-gray-900 dark:text-gray-100 truncate">{{ bowSetup.name }}</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">
                        {{ bowSetup.draw_weight || bowSetup.bow_config?.draw_weight }}lbs • 
                        {{ formatBowType(bowSetup.bow_type || bowSetup.bow_config?.bow_type) }}
                      </div>
                    </div>
                    <div v-if="selectedBowSetup?.id === bowSetup.id" class="w-2 h-2 bg-primary-500 rounded-full"></div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { useBowSetupPickerStore } from '~/stores/bowSetupPicker'
import { useBowConfigStore } from '~/stores/bowConfig'
import { useAuth } from '~/composables/useAuth'
import type { BowSetup } from '~/types/arrow'

interface Props {
  isMobile?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isMobile: false
})

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

// Close picker when clicking outside (desktop only)
const handleClickOutside = (event: Event) => {
  if (!props.isMobile && isPickerOpen.value) {
    const target = event.target as HTMLElement
    if (!target.closest('.relative') && !target.closest('.picker-dropdown')) {
      closePicker()
    }
  }
}

onMounted(() => {
  if (!props.isMobile) {
    document.addEventListener('click', handleClickOutside)
  }
})

onUnmounted(() => {
  if (!props.isMobile) {
    document.removeEventListener('click', handleClickOutside)
  }
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