<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-6">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Spine Calculation Data Management
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          Configure and manage spine calculation parameters, material properties, and testing tools
        </p>
      </div>

      <!-- Navigation Tabs -->
      <div class="mb-6">
        <nav class="flex space-x-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'bg-blue-600 text-white dark:bg-purple-600'
                : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800'
            ]"
          >
            <i :class="tab.icon" class="mr-2"></i>
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600 dark:text-gray-400">Loading spine data...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex items-center">
          <i class="fas fa-exclamation-triangle text-red-600 mr-2"></i>
          <span class="text-red-800">{{ error }}</span>
        </div>
      </div>

      <!-- Calculation Parameters Tab -->
      <div v-else-if="activeTab === 'parameters'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              Calculation Parameters
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Adjust the mathematical parameters used in spine calculations
            </p>
          </div>
          
          <div class="p-6">
            <div v-for="(group, groupName) in parameters" :key="groupName" class="mb-8">
              <h3 class="text-md font-medium text-gray-900 dark:text-white mb-4 capitalize">
                {{ groupName.replace('_', ' ') }}
              </h3>
              
              <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <div
                  v-for="(param, paramName) in group"
                  :key="paramName"
                  class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4"
                >
                  <label :for="`param-${groupName}-${paramName}`" 
                         class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {{ paramName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) }}
                  </label>
                  
                  <div class="flex items-center space-x-2">
                    <input
                      :id="`param-${groupName}-${paramName}`"
                      type="number"
                      step="0.1"
                      :value="param.value"
                      @change="updateParameter(groupName, paramName, $event.target.value)"
                      class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm 
                             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                             dark:bg-gray-800 dark:text-white"
                    />
                    <span class="text-xs text-gray-500 dark:text-gray-400 min-w-0">
                      {{ param.unit || '' }}
                    </span>
                  </div>
                  
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {{ param.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Material Properties Tab -->
      <div v-else-if="activeTab === 'materials'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <div>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                Arrow Material Properties
              </h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Configure physical properties of different arrow materials
              </p>
            </div>
            <button
              @click="showNewMaterialModal = true"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-plus mr-2"></i>
              Add Material
            </button>
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
                    Spine Factor
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Usage
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="(material, materialName) in materials" :key="materialName">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ materialName }}
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      {{ material.description }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300">
                    {{ material.density }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300">
                    {{ material.elasticity_modulus }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300">
                    {{ material.spine_adjustment_factor }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300">
                    {{ material.typical_use }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      @click="editMaterial(materialName, material)"
                      class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 mr-3"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Manufacturer Charts Tab -->
      <div v-else-if="activeTab === 'charts'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              Manufacturer Spine Charts
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              View manufacturer-specific spine recommendations
            </p>
          </div>
          
          <div class="p-6">
            <div v-if="charts.length === 0" class="text-center py-8">
              <i class="fas fa-chart-bar text-gray-400 text-4xl mb-4"></i>
              <p class="text-gray-500 dark:text-gray-400">No manufacturer spine charts available</p>
            </div>
            <div v-else class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Manufacturer
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Bow Type
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Draw Weight Range
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Arrow Length Range
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Recommended Spine
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Confidence
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="chart in charts" :key="chart.id">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {{ chart.manufacturer }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300 capitalize">
                      {{ chart.bow_type }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300">
                      {{ chart.draw_weight_min }}-{{ chart.draw_weight_max }} lbs
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300">
                      {{ chart.arrow_length_min }}"-{{ chart.arrow_length_max }}"
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {{ chart.recommended_spine }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-300">
                      <div class="flex items-center">
                        <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            class="bg-blue-600 h-2 rounded-full" 
                            :style="{ width: chart.confidence_rating + '%' }"
                          ></div>
                        </div>
                        {{ chart.confidence_rating }}%
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Testing Tab -->
      <div v-else-if="activeTab === 'testing'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              Spine Calculation Testing
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Test spine calculations with current parameters and compare results
            </p>
          </div>
          
          <div class="p-6">
            <div class="grid gap-6 md:grid-cols-2">
              <!-- Input Form -->
              <div>
                <h3 class="text-md font-medium text-gray-900 dark:text-white mb-4">
                  Test Parameters
                </h3>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Draw Weight (lbs)
                    </label>
                    <input
                      v-model="testParams.draw_weight"
                      type="number"
                      step="0.5"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                             dark:bg-gray-700 dark:text-white"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Arrow Length (inches)
                    </label>
                    <input
                      v-model="testParams.arrow_length"
                      type="number"
                      step="0.25"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                             dark:bg-gray-700 dark:text-white"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Point Weight (grains)
                    </label>
                    <input
                      v-model="testParams.point_weight"
                      type="number"
                      step="5"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                             dark:bg-gray-700 dark:text-white"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Bow Type
                    </label>
                    <select
                      v-model="testParams.bow_type"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                             dark:bg-gray-700 dark:text-white"
                    >
                      <option value="compound">Compound</option>
                      <option value="recurve">Recurve</option>
                      <option value="traditional">Traditional</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Material Preference (Optional)
                    </label>
                    <select
                      v-model="testParams.material_preference"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                             dark:bg-gray-700 dark:text-white"
                    >
                      <option value="">None</option>
                      <option v-for="(material, name) in materials" :key="name" :value="name">
                        {{ name }}
                      </option>
                    </select>
                  </div>
                  <button
                    @click="runTest"
                    :disabled="testing"
                    class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 
                           text-white font-medium rounded-lg transition-colors"
                  >
                    <i v-if="testing" class="fas fa-spinner fa-spin mr-2"></i>
                    <i v-else class="fas fa-calculator mr-2"></i>
                    {{ testing ? 'Testing...' : 'Run Test' }}
                  </button>
                </div>
              </div>

              <!-- Results -->
              <div v-if="testResults">
                <h3 class="text-md font-medium text-gray-900 dark:text-white mb-4">
                  Test Results
                </h3>
                
                <!-- Standard Calculation -->
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-4">
                  <h4 class="font-medium text-blue-900 dark:text-blue-300 mb-2">
                    Standard Calculation
                  </h4>
                  <div class="text-2xl font-bold text-blue-900 dark:text-blue-300 mb-2">
                    {{ testResults.standard_calculation.calculated_spine }}
                  </div>
                  <div class="text-sm text-blue-700 dark:text-blue-400">
                    Range: {{ testResults.standard_calculation.spine_range.minimum }}-{{ testResults.standard_calculation.spine_range.maximum }}
                  </div>
                  <div class="text-xs text-blue-600 dark:text-blue-500 mt-1">
                    Source: {{ testResults.standard_calculation.source }}
                  </div>
                </div>

                <!-- Enhanced Calculation -->
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-900 dark:text-green-300 mb-2">
                    Enhanced Calculation
                  </h4>
                  <div class="text-2xl font-bold text-green-900 dark:text-green-300 mb-2">
                    {{ testResults.enhanced_calculation.calculated_spine }}
                  </div>
                  <div class="text-sm text-green-700 dark:text-green-400">
                    Range: {{ testResults.enhanced_calculation.spine_range.minimum }}-{{ testResults.enhanced_calculation.spine_range.maximum }}
                  </div>
                  <div class="text-xs text-green-600 dark:text-green-500 mt-1">
                    Source: {{ testResults.enhanced_calculation.source }}
                  </div>
                  <div v-if="testResults.enhanced_calculation.material_info?.material" class="text-xs text-green-600 dark:text-green-500 mt-1">
                    Material: {{ testResults.enhanced_calculation.material_info.material }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Material Edit/Create Modal -->
    <div v-if="showEditMaterialModal || showNewMaterialModal" 
         class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ showNewMaterialModal ? 'Add New Material' : 'Edit Material' }}
          </h3>
        </div>
        
        <div class="p-6">
          <div class="space-y-4">
            <div v-if="showNewMaterialModal">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Material Name
              </label>
              <input
                v-model="editingMaterial.material_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                       dark:bg-gray-700 dark:text-white"
                placeholder="e.g., Carbon Fiber"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Density
              </label>
              <input
                v-model="editingMaterial.density"
                type="number"
                step="0.1"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                       dark:bg-gray-700 dark:text-white"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Elasticity Modulus
              </label>
              <input
                v-model="editingMaterial.elasticity_modulus"
                type="number"
                step="1"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                       dark:bg-gray-700 dark:text-white"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Spine Adjustment Factor
              </label>
              <input
                v-model="editingMaterial.spine_adjustment_factor"
                type="number"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                       dark:bg-gray-700 dark:text-white"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <textarea
                v-model="editingMaterial.description"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                       dark:bg-gray-700 dark:text-white"
                placeholder="Brief description of the material properties..."
              ></textarea>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Typical Use
              </label>
              <input
                v-model="editingMaterial.typical_use"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                       dark:bg-gray-700 dark:text-white"
                placeholder="e.g., Target and hunting"
              />
            </div>
          </div>
        </div>
        
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
          <button
            @click="closeEditMaterialModal"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="saveMaterial"
            :disabled="saving"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors"
          >
            <i v-if="saving" class="fas fa-spinner fa-spin mr-2"></i>
            {{ saving ? 'Saving...' : (showNewMaterialModal ? 'Create' : 'Save') }}
          </button>
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
  layout: 'default',
  middleware: ['auth-check', 'admin']
})

// Composables
const api = useApi()

// Reactive data
const loading = ref(true)
const error = ref('')
const activeTab = ref('parameters')
const saving = ref(false)
const testing = ref(false)

// Data
const parameters = ref({})
const materials = ref({})
const charts = ref([])
const testResults = ref(null)

// Modals
const showEditMaterialModal = ref(false)
const showNewMaterialModal = ref(false)
const editingMaterial = ref({})
const editingMaterialName = ref('')

// Test parameters
const testParams = ref({
  draw_weight: 50,
  arrow_length: 29,
  point_weight: 125,
  bow_type: 'compound',
  material_preference: ''
})

// Tab configuration
const tabs = [
  {
    id: 'parameters',
    name: 'Calculation Parameters',
    icon: 'fas fa-calculator'
  },
  {
    id: 'materials',
    name: 'Material Properties',
    icon: 'fas fa-atom'
  },
  {
    id: 'charts',
    name: 'Manufacturer Charts',
    icon: 'fas fa-chart-bar'
  },
  {
    id: 'testing',
    name: 'Testing Tools',
    icon: 'fas fa-flask'
  }
]

// Methods
async function loadSpineData() {
  loading.value = true
  error.value = ''
  
  try {
    // Load parameters
    const paramsResponse = await api.get('/admin/spine-data/parameters')
    parameters.value = paramsResponse?.data || paramsResponse || {}
    
    // Load materials
    const materialsResponse = await api.get('/admin/spine-data/materials')
    materials.value = materialsResponse?.data?.materials || materialsResponse?.materials || []
    
    // Load manufacturer charts
    const chartsResponse = await api.get('/admin/spine-data/manufacturer-charts')
    charts.value = chartsResponse?.data?.charts || chartsResponse?.charts || []
    
  } catch (err) {
    console.error('Spine data loading error:', err)
    error.value = 'Failed to load spine data: ' + (err?.response?.data?.error || err?.message || 'Unknown error')
  } finally {
    loading.value = false
  }
}

async function updateParameter(groupName: string, paramName: string, value: string) {
  try {
    await api.put(`/admin/spine-data/parameters/${groupName}/${paramName}`, {
      value: parseFloat(value)
    })
    
    // Update local value
    if (parameters.value[groupName] && parameters.value[groupName][paramName]) {
      parameters.value[groupName][paramName].value = parseFloat(value)
    }
    
    // Show success message (you can implement toast notifications here)
    console.log('Parameter updated successfully')
  } catch (err) {
    error.value = 'Failed to update parameter: ' + (err.response?.data?.error || err.message)
  }
}

function editMaterial(materialName: string, material: any) {
  editingMaterialName.value = materialName
  editingMaterial.value = { ...material }
  showEditMaterialModal.value = true
}

function closeEditMaterialModal() {
  showEditMaterialModal.value = false
  showNewMaterialModal.value = false
  editingMaterial.value = {}
  editingMaterialName.value = ''
}

async function saveMaterial() {
  saving.value = true
  
  try {
    if (showNewMaterialModal.value) {
      // Create new material
      await api.post('/admin/spine-data/materials', editingMaterial.value)
    } else {
      // Update existing material
      await api.put(`/admin/spine-data/materials/${editingMaterialName.value}`, editingMaterial.value)
    }
    
    // Reload materials
    const materialsResponse = await api.get('/admin/spine-data/materials')
    materials.value = materialsResponse?.data?.materials || materialsResponse?.materials || []
    
    closeEditMaterialModal()
  } catch (err) {
    error.value = 'Failed to save material: ' + (err.response?.data?.error || err.message)
  } finally {
    saving.value = false
  }
}

async function runTest() {
  testing.value = true
  
  try {
    const response = await api.post('/admin/spine-data/test-calculation', testParams.value)
    testResults.value = response.data
  } catch (err) {
    error.value = 'Failed to run test: ' + (err.response?.data?.error || err.message)
  } finally {
    testing.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadSpineData()
})
</script>

<style scoped>
/* Add any component-specific styles here */
</style>