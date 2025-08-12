<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-6">
      <!-- Header -->
      <div class="mb-6">
        <nav class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
          <NuxtLink to="/info" class="hover:text-blue-600 dark:hover:text-blue-400">
            Information Center
          </NuxtLink>
          <i class="fas fa-chevron-right"></i>
          <span class="text-gray-900 dark:text-white">Arrow Materials</span>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Arrow Materials Guide
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Understanding the properties and characteristics of different arrow shaft materials
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600 dark:text-gray-400">Loading material data...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex items-center">
          <i class="fas fa-exclamation-triangle text-red-600 mr-2"></i>
          <span class="text-red-800">{{ error }}</span>
        </div>
      </div>

      <!-- Materials Content -->
      <div v-else>
        <!-- Overview -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Material Selection Overview
          </h2>
          <p class="text-gray-600 dark:text-gray-400 mb-4">
            The choice of arrow shaft material significantly affects arrow performance, durability, and cost. 
            Each material has unique properties that make it suitable for different types of archery and 
            shooting conditions.
          </p>
          
          <div class="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-medium text-blue-900 dark:text-blue-300 mb-2">Performance</h3>
              <p class="text-sm text-blue-700 dark:text-blue-400">
                How the material affects speed, accuracy, and consistency
              </p>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-medium text-green-900 dark:text-green-300 mb-2">Durability</h3>
              <p class="text-sm text-green-700 dark:text-green-400">
                Resistance to damage and long-term reliability
              </p>
            </div>
            
            <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
              <h3 class="font-medium text-yellow-900 dark:text-yellow-300 mb-2">Cost</h3>
              <p class="text-sm text-yellow-700 dark:text-yellow-400">
                Initial investment and replacement frequency
              </p>
            </div>
            
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h3 class="font-medium text-purple-900 dark:text-purple-300 mb-2">Application</h3>
              <p class="text-sm text-purple-700 dark:text-purple-400">
                Best use cases and archery disciplines
              </p>
            </div>
          </div>
        </div>

        <!-- Material Comparison Table -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden mb-6">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
              Material Comparison
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Technical properties of different arrow materials
            </p>
          </div>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Material
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Density
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Elasticity
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Strength
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Consistency
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Typical Use
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="(material, materialName) in materials" :key="materialName">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10">
                        <div class="h-10 w-10 rounded-full bg-gradient-to-r from-blue-400 to-blue-600 flex items-center justify-center">
                          <i class="fas fa-atom text-white text-sm"></i>
                        </div>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900 dark:text-white">
                          {{ materialName }}
                        </div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">
                          {{ getRating(material.strength_factor) }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300">
                    {{ material.density }} g/cm³
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300">
                    {{ material.elasticity_modulus }} GPa
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          class="bg-green-600 h-2 rounded-full" 
                          :style="{ width: (material.strength_factor * 100) + '%' }"
                        ></div>
                      </div>
                      <span class="text-sm text-gray-900 dark:text-gray-300">
                        {{ (material.strength_factor * 100).toFixed(0) }}%
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      getConsistencyClass(material.spine_adjustment_factor)
                    ]">
                      {{ getConsistencyLabel(material.spine_adjustment_factor) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-300">
                    {{ material.typical_use }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Material Details -->
        <div class="grid gap-6 lg:grid-cols-2">
          <div v-for="(material, materialName) in materials" :key="materialName"
               class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
            <div class="p-6">
              <div class="flex items-center mb-4">
                <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                  <i class="fas fa-atom text-blue-600 dark:text-blue-400 text-xl"></i>
                </div>
                <div class="ml-3">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ materialName }}
                  </h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    {{ getRating(material.strength_factor) }} Performance Material
                  </p>
                </div>
              </div>
              
              <p class="text-gray-600 dark:text-gray-400 mb-4">
                {{ material.description }}
              </p>
              
              <div class="grid grid-cols-2 gap-4 mb-4">
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <div class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Density
                  </div>
                  <div class="text-sm font-semibold text-gray-900 dark:text-white mt-1">
                    {{ material.density }} g/cm³
                  </div>
                </div>
                
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <div class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Elasticity
                  </div>
                  <div class="text-sm font-semibold text-gray-900 dark:text-white mt-1">
                    {{ material.elasticity_modulus }} GPa
                  </div>
                </div>
                
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <div class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Humidity Resistance
                  </div>
                  <div class="text-sm font-semibold text-gray-900 dark:text-white mt-1">
                    {{ material.humidity_resistance_rating }}/10
                  </div>
                </div>
                
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <div class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Temperature Stability
                  </div>
                  <div class="text-sm font-semibold text-gray-900 dark:text-white mt-1">
                    {{ (material.temperature_coefficient * 10000).toFixed(1) }}×10⁻⁴
                  </div>
                </div>
              </div>
              
              <div class="space-y-2">
                <h4 class="text-sm font-medium text-gray-900 dark:text-white">
                  Recommended For:
                </h4>
                <div class="flex flex-wrap gap-2">
                  <span v-for="use in material.typical_use.split(', ')" :key="use"
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                    {{ use.trim() }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Selection Guide -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mt-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Material Selection Guide
          </h2>
          
          <div class="grid gap-6 md:grid-cols-3">
            <div class="border-l-4 border-blue-500 pl-4">
              <h3 class="font-medium text-gray-900 dark:text-white mb-2">
                For Target Archery
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Precision and consistency are paramount.
              </p>
              <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Carbon arrows for consistent spine</li>
                <li>• Aluminum for budget-friendly options</li>
                <li>• Carbon/Aluminum for competition</li>
              </ul>
            </div>
            
            <div class="border-l-4 border-green-500 pl-4">
              <h3 class="font-medium text-gray-900 dark:text-white mb-2">
                For Hunting
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Durability and penetration are key.
              </p>
              <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Carbon for lightweight speed</li>
                <li>• Carbon/Aluminum for toughness</li>
                <li>• Aluminum for heavy arrows</li>
              </ul>
            </div>
            
            <div class="border-l-4 border-yellow-500 pl-4">
              <h3 class="font-medium text-gray-900 dark:text-white mb-2">
                For Traditional
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Authenticity and feel matter most.
              </p>
              <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Wood arrows for traditional feel</li>
                <li>• Carbon for modern performance</li>
                <li>• Aluminum for practice arrows</li>
              </ul>
            </div>
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
const loading = ref(true)
const error = ref('')
const materials = ref({})

// Methods
async function loadMaterials() {
  loading.value = true
  error.value = ''
  
  try {
    // Try to load materials from enhanced spine data API
    const response = await api.get('/api/admin/spine-charts/materials')
    materials.value = response.data.materials
  } catch (err) {
    // Fallback to static data if API fails
    materials.value = {
      'Carbon': {
        density: 1.6,
        elasticity_modulus: 230.0,
        strength_factor: 1.0,
        spine_adjustment_factor: 1.0,
        temperature_coefficient: 0.0001,
        humidity_resistance_rating: 9,
        description: 'High-performance carbon fiber arrows with excellent consistency and speed. Ideal for target archery and hunting where precision matters.',
        typical_use: 'Target, Hunting'
      },
      'Aluminum': {
        density: 2.7,
        elasticity_modulus: 69.0,
        strength_factor: 0.85,
        spine_adjustment_factor: 0.95,
        temperature_coefficient: 0.0002,
        humidity_resistance_rating: 7,
        description: 'Durable aluminum arrows with good straightness and consistent performance. Cost-effective option for practice and competition.',
        typical_use: 'Target, Practice'
      },
      'Wood': {
        density: 0.6,
        elasticity_modulus: 12.0,
        strength_factor: 0.7,
        spine_adjustment_factor: 1.3,
        temperature_coefficient: 0.001,
        humidity_resistance_rating: 4,
        description: 'Traditional wooden arrows with natural variability. Perfect for traditional archery and historical accuracy.',
        typical_use: 'Traditional, Historical'
      }
    }
  } finally {
    loading.value = false
  }
}

function getRating(strengthFactor: number): string {
  if (strengthFactor >= 0.9) return 'Premium'
  if (strengthFactor >= 0.8) return 'High'
  if (strengthFactor >= 0.7) return 'Good'
  return 'Basic'
}

function getConsistencyClass(factor: number): string {
  if (factor <= 1.05) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
  if (factor <= 1.15) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
  return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
}

function getConsistencyLabel(factor: number): string {
  if (factor <= 1.05) return 'Excellent'
  if (factor <= 1.15) return 'Good'
  return 'Variable'
}

// Lifecycle
onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
/* Add any component-specific styles here */
</style>