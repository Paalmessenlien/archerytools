<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-6">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Archery Information Center
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Comprehensive guides and resources for arrow tuning and archery equipment
        </p>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <i class="fas fa-atom text-blue-600 dark:text-blue-400 text-xl"></i>
            </div>
            <div class="ml-4">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Materials</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ materialCount }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <i class="fas fa-tools text-green-600 dark:text-green-400 text-xl"></i>
            </div>
            <div class="ml-4">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Tuning Methods</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ tuningMethodCount }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 text-xl"></i>
            </div>
            <div class="ml-4">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Problems Covered</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ problemCount }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <i class="fas fa-calculator text-purple-600 dark:text-purple-400 text-xl"></i>
            </div>
            <div class="ml-4">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Calculations</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ calculationCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Information Categories -->
      <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        
        <!-- Arrow Materials -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <i class="fas fa-atom text-blue-600 dark:text-blue-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Arrow Materials</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Properties and characteristics</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Learn about different arrow shaft materials, their properties, and how they affect performance.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Carbon fiber arrows
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Aluminum arrows
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Wood arrows
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Hybrid materials
              </div>
            </div>
            
            <NuxtLink
              to="/info/materials"
              class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Learn More
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>

        <!-- Tuning Guides -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <i class="fas fa-tools text-green-600 dark:text-green-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Tuning Guides</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Step-by-step methodologies</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Comprehensive tuning methodologies from basic setup to advanced optimization techniques.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Paper tuning
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Bare shaft tuning
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Group tuning
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Walk-back tuning
              </div>
            </div>
            
            <NuxtLink
              to="/info/tuning-guides"
              class="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              View Guides
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>

        <!-- Problem Diagnostics -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Flight Problems</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Diagnosis and solutions</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Identify and solve common arrow flight problems with our comprehensive diagnostic guide.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Left/right tears
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                High/low impacts
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Erratic grouping
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Poor clearance
              </div>
            </div>
            
            <NuxtLink
              to="/info/flight-problems"
              class="inline-flex items-center px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Diagnose Issues
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>

        <!-- Spine Calculator -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <i class="fas fa-calculator text-purple-600 dark:text-purple-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Spine Calculator</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Calculation methods</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Understanding how spine calculations work and the factors that influence arrow selection.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Draw weight factors
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Arrow length adjustments
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Point weight effects
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Bow type differences
              </div>
            </div>
            
            <NuxtLink
              to="/info/spine-calculator"
              class="inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Learn Calculations
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>

        <!-- Equipment Guide -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
                <i class="fas fa-bow-arrow text-red-600 dark:text-red-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Equipment Guide</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Components and accessories</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Learn about different arrow components and how they affect performance and tuning.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Points and inserts
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Nocks and bushings
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Fletching options
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Wraps and crests
              </div>
            </div>
            
            <NuxtLink
              to="/info/equipment"
              class="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Equipment Guide
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>

        <!-- Quick Reference -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-4">
              <div class="p-2 bg-indigo-100 dark:bg-indigo-900 rounded-lg">
                <i class="fas fa-book text-indigo-600 dark:text-indigo-400 text-xl"></i>
              </div>
              <div class="ml-3">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Quick Reference</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">Charts and formulas</p>
              </div>
            </div>
            
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              Quick reference charts, formulas, and conversion tables for field use.
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Spine charts
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Conversion tables
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Tuning checklists
              </div>
              <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <i class="fas fa-check text-green-500 mr-2"></i>
                Safety guidelines
              </div>
            </div>
            
            <NuxtLink
              to="/info/reference"
              class="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Quick Reference
              <i class="fas fa-arrow-right ml-2"></i>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

// Page metadata
definePageMeta({
  layout: 'default'
})

// Composables
const api = useApi()

// Reactive data
const materialCount = ref(0)
const tuningMethodCount = ref(0)
const problemCount = ref(0)
const calculationCount = ref(0)

// Methods
async function loadInfoStats() {
  try {
    // These would be actual API calls to get statistics
    materialCount.value = 5 // Example count
    tuningMethodCount.value = 8 // Example count
    problemCount.value = 12 // Example count
    calculationCount.value = 15 // Example count
  } catch (error) {
    console.error('Error loading info stats:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadInfoStats()
})
</script>

<style scoped>
/* Add any component-specific styles here */
</style>