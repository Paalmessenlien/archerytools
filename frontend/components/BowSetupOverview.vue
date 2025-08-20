<template>
  <div class="bow-setup-overview space-y-6">
    <!-- Basic Information Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-info-circle mr-2 text-blue-600 dark:text-blue-400"></i>
        Bow Information
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Bow Type -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-archway text-blue-600 dark:text-blue-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Bow Type</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.bow_type }}</p>
          </div>
        </div>

        <!-- Draw Weight -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-dumbbell text-green-600 dark:text-green-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Draw Weight</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.draw_weight }}#</p>
          </div>
        </div>

        <!-- Usage -->
        <div v-if="setup.bow_usage" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-target text-purple-600 dark:text-purple-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Usage</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ formatUsage(setup.bow_usage) }}</p>
          </div>
        </div>

        <!-- Draw Length (if available) -->
        <div v-if="setup.draw_length" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-ruler text-orange-600 dark:text-orange-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Draw Length</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.draw_length }}"</p>
          </div>
        </div>

        <!-- IBO Speed (if available) -->
        <div v-if="setup.ibo_speed" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-tachometer-alt text-red-600 dark:text-red-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">IBO Speed</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.ibo_speed }} fps</p>
          </div>
        </div>

        <!-- Created Date -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
            <i class="fas fa-calendar text-gray-600 dark:text-gray-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Created</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ formatDate(setup.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bow Details (for compound/recurve bows) -->
    <div v-if="showBowDetails" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-cogs mr-2 text-green-600 dark:text-green-400"></i>
        {{ setup.bow_type === 'Compound' ? 'Compound Bow Details' : 'Recurve Bow Details' }}
      </h3>
      
      <!-- Compound Bow Details -->
      <div v-if="setup.bow_type === 'Compound'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-if="setup.compound_brand" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-tag text-blue-600 dark:text-blue-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Brand</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.compound_brand }}</p>
          </div>
        </div>

        <div v-if="setup.compound_model" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-barcode text-green-600 dark:text-green-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Model</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.compound_model }}</p>
          </div>
        </div>
      </div>

      <!-- Recurve Bow Details -->
      <div v-else-if="setup.bow_type === 'Recurve'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Riser Details -->
        <div v-if="setup.riser_brand" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-grip-vertical text-blue-600 dark:text-blue-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Riser Brand</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.riser_brand }}</p>
          </div>
        </div>

        <div v-if="setup.riser_model" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-barcode text-green-600 dark:text-green-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Riser Model</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.riser_model }}</p>
          </div>
        </div>

        <div v-if="setup.riser_length" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-ruler-horizontal text-purple-600 dark:text-purple-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Riser Length</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.riser_length }}"</p>
          </div>
        </div>

        <!-- Limb Details -->
        <div v-if="setup.limb_brand" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-grip-lines text-orange-600 dark:text-orange-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Limb Brand</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.limb_brand }}</p>
          </div>
        </div>

        <div v-if="setup.limb_model" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-barcode text-red-600 dark:text-red-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Limb Model</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.limb_model }}</p>
          </div>
        </div>

        <div v-if="setup.limb_length" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-ruler-horizontal text-yellow-600 dark:text-yellow-400"></i>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Limb Length</p>
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ setup.limb_length }}"</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Description -->
    <div v-if="setup.description" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-file-alt mr-2 text-purple-600 dark:text-purple-400"></i>
        Description
      </h3>
      <p class="text-gray-700 dark:text-gray-300 leading-relaxed">{{ setup.description }}</p>
    </div>

    <!-- Statistics Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Arrows Count -->
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1">Arrows</p>
            <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">{{ statistics.arrow_count || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-200 dark:bg-blue-800 rounded-lg flex items-center justify-center">
            <i class="fas fa-bullseye text-blue-600 dark:text-blue-400 text-xl"></i>
          </div>
        </div>
      </div>

      <!-- Equipment Count -->
      <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg border border-green-200 dark:border-green-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-green-600 dark:text-green-400 mb-1">Equipment</p>
            <p class="text-2xl font-bold text-green-900 dark:text-green-100">{{ statistics.equipment_count || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-green-200 dark:bg-green-800 rounded-lg flex items-center justify-center">
            <i class="fas fa-cogs text-green-600 dark:text-green-400 text-xl"></i>
          </div>
        </div>
      </div>

      <!-- Changes Count -->
      <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg border border-purple-200 dark:border-purple-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-purple-600 dark:text-purple-400 mb-1">Changes</p>
            <p class="text-2xl font-bold text-purple-900 dark:text-purple-100">{{ statistics.total_changes || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-purple-200 dark:bg-purple-800 rounded-lg flex items-center justify-center">
            <i class="fas fa-history text-purple-600 dark:text-purple-400 text-xl"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 sm:mb-6">
        <i class="fas fa-lightning-bolt mr-2 text-yellow-600 dark:text-yellow-400"></i>
        Quick Actions
      </h3>
      
      <!-- Mobile-first layout: Single column on mobile, responsive grid on larger screens -->
      <div class="space-y-3 sm:space-y-0 sm:grid sm:grid-cols-2 lg:grid-cols-4 sm:gap-4">
        <!-- Primary Action: Manage Arrows (most common action) -->
        <button
          @click="$emit('switch-tab', 'arrows')"
          class="quick-action-button primary-action w-full flex items-center justify-start sm:justify-center p-4 sm:p-3 rounded-xl border-2 transition-all duration-200 touch-manipulation min-h-[56px] text-left sm:text-center bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:bg-blue-900/20 dark:border-blue-700 dark:text-blue-300 dark:hover:bg-blue-900/30"
        >
          <div class="flex items-center justify-start sm:justify-center w-full">
            <div class="w-8 h-8 sm:w-6 sm:h-6 mr-3 sm:mr-2 flex items-center justify-center rounded-lg bg-blue-200 dark:bg-blue-800 flex-shrink-0">
              <i class="fas fa-bullseye text-blue-700 dark:text-blue-300 text-sm"></i>
            </div>
            <span class="font-medium">Manage Arrows</span>
            <div class="ml-auto sm:ml-2 px-2 py-1 text-xs bg-blue-200 text-blue-800 dark:bg-blue-800 dark:text-blue-200 rounded-full font-medium">
              {{ statistics.arrow_count || 0 }}
            </div>
          </div>
        </button>

        <!-- Secondary Actions -->
        <button
          @click="$emit('switch-tab', 'equipment')"
          class="quick-action-button secondary-action w-full flex items-center justify-start sm:justify-center p-4 sm:p-3 rounded-xl border-2 transition-all duration-200 touch-manipulation min-h-[56px] text-left sm:text-center bg-white border-green-200 text-green-700 hover:bg-green-50 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:bg-gray-800 dark:border-green-700 dark:text-green-300 dark:hover:bg-green-900/20"
        >
          <div class="flex items-center justify-start sm:justify-center w-full">
            <div class="w-8 h-8 sm:w-6 sm:h-6 mr-3 sm:mr-2 flex items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30 flex-shrink-0">
              <i class="fas fa-cogs text-green-700 dark:text-green-300 text-sm"></i>
            </div>
            <span class="font-medium">Manage Equipment</span>
            <div class="ml-auto sm:ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200 rounded-full font-medium">
              {{ statistics.equipment_count || 0 }}
            </div>
          </div>
        </button>

        <button
          @click="$emit('switch-tab', 'history')"
          class="quick-action-button secondary-action w-full flex items-center justify-start sm:justify-center p-4 sm:p-3 rounded-xl border-2 transition-all duration-200 touch-manipulation min-h-[56px] text-left sm:text-center bg-white border-purple-200 text-purple-700 hover:bg-purple-50 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 dark:bg-gray-800 dark:border-purple-700 dark:text-purple-300 dark:hover:bg-purple-900/20"
        >
          <div class="flex items-center justify-start sm:justify-center w-full">
            <div class="w-8 h-8 sm:w-6 sm:h-6 mr-3 sm:mr-2 flex items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/30 flex-shrink-0">
              <i class="fas fa-history text-purple-700 dark:text-purple-300 text-sm"></i>
            </div>
            <span class="font-medium">View History</span>
            <div class="ml-auto sm:ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-200 rounded-full font-medium">
              {{ statistics.total_changes || 0 }}
            </div>
          </div>
        </button>

        <button
          @click="$emit('switch-tab', 'settings')"
          class="quick-action-button secondary-action w-full flex items-center justify-start sm:justify-center p-4 sm:p-3 rounded-xl border-2 transition-all duration-200 touch-manipulation min-h-[56px] text-left sm:text-center bg-white border-gray-200 text-gray-700 hover:bg-gray-50 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          <div class="flex items-center justify-start sm:justify-center w-full">
            <div class="w-8 h-8 sm:w-6 sm:h-6 mr-3 sm:mr-2 flex items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700 flex-shrink-0">
              <i class="fas fa-cog text-gray-700 dark:text-gray-300 text-sm"></i>
            </div>
            <span class="font-medium">Settings</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CustomButton from './CustomButton.vue'

const props = defineProps({
  setup: {
    type: Object,
    required: true
  },
  statistics: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['switch-tab'])

// Computed properties
const showBowDetails = computed(() => {
  return (props.setup.bow_type === 'Compound' && (props.setup.compound_brand || props.setup.compound_model)) ||
         (props.setup.bow_type === 'Recurve' && (props.setup.riser_brand || props.setup.riser_model || props.setup.limb_brand || props.setup.limb_model))
})

// Methods
const formatUsage = (usage) => {
  if (!usage) return 'Not specified'
  
  // Handle array format (JSON string or actual array)
  if (typeof usage === 'string' && usage.startsWith('[')) {
    try {
      const parsed = JSON.parse(usage)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed.join(', ')
      }
    } catch (e) {
      // If parsing fails, treat as regular string
    }
  }
  
  // Handle actual array
  if (Array.isArray(usage) && usage.length > 0) {
    return usage.join(', ')
  }
  
  // Handle regular string
  if (typeof usage === 'string') {
    return usage.charAt(0).toUpperCase() + usage.slice(1)
  }
  
  return 'Not specified'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return 'Unknown'
  }
}
</script>

<style scoped>
/* Component-specific styles if needed */
.bow-setup-overview {
  /* Any custom styling for the overview component */
}
</style>