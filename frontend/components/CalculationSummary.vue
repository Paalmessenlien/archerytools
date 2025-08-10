<template>
  <div class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <div class="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
          <i class="fas fa-calculator text-blue-600 dark:text-blue-300"></i>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-100">Calculation Results</h3>
          <p class="text-sm text-blue-700 dark:text-blue-300">Based on your bow configuration</p>
        </div>
      </div>
      <button 
        @click="toggleExpanded" 
        class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors"
      >
        <i :class="expanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      </button>
    </div>

    <!-- Bow Configuration Summary -->
    <div class="bg-white dark:bg-gray-800/50 rounded-lg p-4 mb-4">
      <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bow Configuration</h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
        <div>
          <span class="text-gray-500 dark:text-gray-400">Type:</span>
          <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">{{ formatBowType(bowConfig.bow_type) }}</span>
        </div>
        <div>
          <span class="text-gray-500 dark:text-gray-400">Draw Weight:</span>
          <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">{{ bowConfig.draw_weight }}lbs</span>
        </div>
        <div>
          <span class="text-gray-500 dark:text-gray-400">Draw Length:</span>
          <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">{{ bowConfig.draw_length }}"</span>
        </div>
        <div>
          <span class="text-gray-500 dark:text-gray-400">Arrow Length:</span>
          <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">{{ bowConfig.arrow_length }}"</span>
        </div>
      </div>
    </div>

    <!-- Compatibility Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <!-- Match Percentage -->
      <div class="text-center">
        <div class="relative w-16 h-16 mx-auto mb-2">
          <svg class="w-16 h-16 transform -rotate-90" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="28" fill="none" stroke="currentColor" stroke-width="4" 
                    :class="getScoreColor(matchPercentage)" opacity="0.2"/>
            <circle cx="32" cy="32" r="28" fill="none" stroke="currentColor" stroke-width="4" 
                    :class="getScoreColor(matchPercentage)" stroke-linecap="round"
                    :stroke-dasharray="circumference" 
                    :stroke-dashoffset="circumference - (matchPercentage / 100) * circumference"
                    class="transition-all duration-300"/>
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-sm font-bold" :class="getScoreColor(matchPercentage)">{{ matchPercentage }}%</span>
          </div>
        </div>
        <p class="text-xs text-gray-600 dark:text-gray-400">Match Score</p>
      </div>

      <!-- Compatibility Score -->
      <div class="text-center">
        <div class="text-2xl font-bold mb-1" :class="getScoreColor(compatibilityScore)">
          {{ compatibilityScore.toFixed(1) }}
        </div>
        <div class="text-xs px-2 py-1 rounded-full inline-block" :class="getRatingBadgeClass(compatibilityRating)">
          {{ formatRating(compatibilityRating) }}
        </div>
        <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">Compatibility</p>
      </div>

      <!-- Spine Match -->
      <div class="text-center" v-if="spineSpec">
        <div class="text-2xl font-bold mb-1 text-purple-600 dark:text-purple-400">
          {{ spineSpec.spine }}
        </div>
        <div class="text-xs text-gray-600 dark:text-gray-400">
          {{ spineSpec.gpi_weight?.toFixed(1) }}gpi
        </div>
        <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">Recommended Spine</p>
      </div>
    </div>

    <!-- Expanded Content -->
    <div v-if="expanded" class="space-y-4">
      <!-- Match Reasons -->
      <div class="bg-white dark:bg-gray-800/50 rounded-lg p-4">
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Match Analysis</h4>
        <div class="space-y-2">
          <div v-for="reason in reasons" :key="reason" class="flex items-start space-x-2">
            <div class="flex-shrink-0 w-2 h-2 rounded-full bg-blue-400 mt-2"></div>
            <p class="text-sm text-gray-700 dark:text-gray-300">{{ reason }}</p>
          </div>
        </div>
      </div>

      <!-- Spine Specification Details -->
      <div v-if="spineSpec" class="bg-white dark:bg-gray-800/50 rounded-lg p-4">
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Spine Specification</h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div>
            <span class="text-gray-500 dark:text-gray-400">Spine:</span>
            <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">{{ spineSpec.spine }}</span>
          </div>
          <div v-if="spineSpec.outer_diameter">
            <span class="text-gray-500 dark:text-gray-400">Diameter:</span>
            <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">{{ spineSpec.outer_diameter.toFixed(3) }}"</span>
          </div>
          <div v-if="spineSpec.gpi_weight">
            <span class="text-gray-500 dark:text-gray-400">Weight:</span>
            <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">{{ spineSpec.gpi_weight.toFixed(1) }} GPI</span>
          </div>
          <div v-if="spineSpec.inner_diameter">
            <span class="text-gray-500 dark:text-gray-400">Inner Ø:</span>
            <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">{{ spineSpec.inner_diameter.toFixed(3) }}"</span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-wrap gap-2">
        <CustomButton 
          @click="editConfiguration"
          variant="outlined"
          size="small"
          class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-900"
        >
          <i class="fas fa-edit mr-2"></i>
          Edit Configuration
        </CustomButton>
        <CustomButton 
          @click="backToCalculator"
          variant="outlined"
          size="small"
          class="text-gray-600 border-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-400 dark:hover:bg-gray-700"
        >
          <i class="fas fa-arrow-left mr-2"></i>
          Back to Calculator
        </CustomButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BowConfiguration, SpineSpecification } from '~/types/arrow'

// Props
interface Props {
  bowConfig: BowConfiguration
  compatibilityScore: number
  matchPercentage: number
  compatibilityRating: 'excellent' | 'good' | 'poor'
  reasons: string[]
  spineSpec?: SpineSpecification
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  editConfiguration: []
  backToCalculator: []
}>()

// State
const expanded = ref(false)

// Computed
const circumference = computed(() => 2 * Math.PI * 28) // radius = 28

// Methods
const toggleExpanded = () => {
  expanded.value = !expanded.value
}

const formatBowType = (type: string) => {
  return type.charAt(0).toUpperCase() + type.slice(1)
}

const formatRating = (rating: string) => {
  return rating.charAt(0).toUpperCase() + rating.slice(1)
}

const getScoreColor = (score: number) => {
  if (score >= 80) return 'text-green-600 dark:text-green-400'
  if (score >= 60) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

const getRatingBadgeClass = (rating: string) => {
  const baseClasses = 'text-xs font-medium'
  if (rating === 'excellent') return `${baseClasses} bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200`
  if (rating === 'good') return `${baseClasses} bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200`
  return `${baseClasses} bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200`
}

const editConfiguration = () => {
  emit('editConfiguration')
}

const backToCalculator = () => {
  emit('backToCalculator')
}
</script>

<style scoped>
/* Additional styles for the circular progress */
svg circle {
  transition: stroke-dashoffset 0.3s ease;
}
</style>