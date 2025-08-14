<template>
  <div class="bow-setup-settings space-y-6">
    <!-- Setup Configuration -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
        <i class="fas fa-cog mr-2 text-blue-600 dark:text-blue-400"></i>
        Setup Configuration
      </h3>

      <form @submit.prevent="handleSave" class="space-y-6">
        <!-- Basic Information -->
        <div class="space-y-6">
          <!-- Setup Name -->
          <div>
            <label for="setupName" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Setup Name *</label>
            <input 
              type="text" 
              id="setupName" 
              v-model="formData.name" 
              class="w-full form-input" 
              required 
              placeholder="e.g., Hunting Setup, Target Bow..."
            />
          </div>
          
          <!-- Bow Type -->
          <div>
            <label for="bowType" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Bow Type *</label>
            <select id="bowType" v-model="formData.bow_type" class="w-full form-select" required>
              <option value="">Select Bow Type</option>
              <option value="compound">Compound</option>
              <option value="recurve">Recurve</option>
              <option value="longbow">Longbow</option>
              <option value="traditional">Traditional</option>
            </select>
          </div>
          
          <!-- Draw Weight Slider -->
          <div>
            <label class="block mb-3 text-sm font-medium text-gray-700 dark:text-gray-300">
              Draw Weight: <span class="font-semibold text-blue-600 dark:text-blue-400">{{ formData.draw_weight || 45 }} lbs</span>
            </label>
            <input 
              type="range" 
              min="20" 
              max="80" 
              step="0.5" 
              v-model.number="formData.draw_weight"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider"
            />
            <div class="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
              <span>20 lbs</span>
              <span>80 lbs</span>
            </div>
          </div>
        </div>
        
        <!-- Bow Type Specific Configuration -->
        <div v-if="formData.bow_type" class="p-4 mb-4 border border-gray-200 rounded-lg bg-gray-50 dark:bg-gray-700/50 dark:border-gray-600">
          <h4 class="flex items-center mb-4 text-sm font-semibold text-gray-900 dark:text-gray-100">
            <i class="mr-2 text-blue-600 fas fa-cog"></i>
            {{ formData.bow_type?.charAt(0).toUpperCase() + formData.bow_type?.slice(1) }} Specific Configuration
          </h4>

          <!-- Compound Bow Configuration -->
          <div v-if="formData.bow_type === 'compound'" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <!-- Compound Brand Selection -->
              <div>
                <label for="compoundBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Bow Brand</label>
                <select 
                  id="compoundBrand" 
                  :value="formData.brand || ''"
                  @change="handleBrandSelection('brand', $event.target.value)"
                  class="form-select"
                >
                  <option value="">Select Brand</option>
                  <option v-if="loadingManufacturers" disabled>Loading manufacturers...</option>
                  <option 
                    v-for="manufacturer in manufacturerData.compound_bows" 
                    :key="manufacturer" 
                    :value="manufacturer"
                  >
                    {{ manufacturer }}
                  </option>
                  <option value="Other">Other</option>
                </select>

                <!-- Custom brand input when "Other" is selected -->
                <input 
                  v-if="formData.brand === 'Other'"
                  type="text"
                  v-model="formData.custom_brand"
                  class="w-full mt-2 form-input"
                  placeholder="Enter brand name..."
                  required
                />

                <!-- Compound Model Name -->
                <input 
                  v-if="formData.brand"
                  type="text"
                  v-model="formData.compound_model"
                  class="w-full mt-2 form-input"
                  placeholder="e.g., RX-7 Ultra, Halon X, V3X..."
                />
              </div>
              
              <div>
                <label for="iboSpeed" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">IBO Speed (fps)</label>
                <input 
                  type="number"
                  id="iboSpeed"
                  v-model.number="formData.ibo_speed"
                  class="form-input"
                  placeholder="e.g., 320, 340..."
                />
              </div>
            </div>
          </div>

          <!-- Recurve Bow Configuration -->
          <div v-else-if="formData.bow_type === 'recurve'" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <!-- Riser Brand Selection -->
              <div>
                <label for="riserBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Riser Brand</label>
                <select 
                  id="riserBrand"
                  :value="formData.riser_brand || ''"
                  @change="handleBrandSelection('riser_brand', $event.target.value)"
                  class="form-select"
                >
                  <option value="">Select Riser Brand</option>
                  <option v-if="loadingManufacturers" disabled>Loading manufacturers...</option>
                  <option 
                    v-for="manufacturer in manufacturerData.recurve_risers" 
                    :key="manufacturer" 
                    :value="manufacturer"
                  >
                    {{ manufacturer }}
                  </option>
                  <option value="Other">Other</option>
                </select>

                <!-- Custom riser brand input -->
                <input 
                  v-if="formData.riser_brand === 'Other'"
                  type="text"
                  v-model="formData.custom_riser_brand"
                  class="w-full mt-2 form-input"
                  placeholder="Enter riser brand name..."
                  required
                />

                <!-- Riser Model Name -->
                <input 
                  v-if="formData.riser_brand"
                  type="text"
                  v-model="formData.riser_model"
                  class="w-full mt-2 form-input"
                  placeholder="e.g., Formula X, Prodigy, Epic..."
                />
                
                <!-- Riser Length -->
                <div v-if="formData.riser_brand" class="mt-2">
                  <label class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Riser Length</label>
                  <select v-model="formData.riser_length" class="w-full form-select">
                    <option value="">Select Riser Length</option>
                      <option value="17">17"</option>
                      <option value="19">19"</option>
                      <option value="21">21"</option>
                      <option value="23">23"</option>
                      <option value="25">25"</option>
                      <option value="27">27"</option>
                      <option value="Other">Other (custom length)</option>
                  </select>
                  
                  <!-- Custom riser length input -->
                  <input 
                    v-if="formData.riser_length === 'Other'"
                    type="text"
                    v-model="formData.riser_length"
                    @focus="clearOtherValue('riser_length')"
                    class="w-full mt-2 form-input"
                    placeholder="Enter custom riser length (e.g., 24 inches)"
                    required
                  />
                </div>
              </div>
              
              <!-- Limb Brand Selection -->
              <div>
                <label for="limbBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Brand</label>
                <select 
                  id="limbBrand"
                  :value="formData.limb_brand || ''"
                  @change="handleBrandSelection('limb_brand', $event.target.value)"
                  class="form-select"
                >
                  <option value="">Select Limb Brand</option>
                  <option v-if="loadingManufacturers" disabled>Loading manufacturers...</option>
                  <option 
                    v-for="manufacturer in manufacturerData.recurve_limbs" 
                    :key="manufacturer" 
                    :value="manufacturer"
                  >
                    {{ manufacturer }}
                  </option>
                  <option value="Other">Other</option>
                </select>

                <!-- Custom limb brand input -->
                <input 
                  v-if="formData.limb_brand === 'Other'"
                  type="text"
                  v-model="formData.custom_limb_brand"
                  class="w-full mt-2 form-input"
                  placeholder="Enter limb brand name..."
                  required
                />

                <!-- Limb Model Name -->
                <input 
                  v-if="formData.limb_brand"
                  type="text"
                  v-model="formData.limb_model"
                  class="w-full mt-2 form-input"
                  placeholder="e.g., Quattro, Inno Max, Veloce..."
                />
                
                <!-- Limb Length -->
                <div v-if="formData.limb_brand" class="mt-2">
                  <label class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Length</label>
                  <select v-model="formData.limb_length" class="w-full form-select">
                    <option value="">Select Limb Length</option>
                    <option value="Short">Short</option>
                    <option value="Medium">Medium</option>
                    <option value="Long">Long</option>
                    <option value="Other">Other (custom length)</option>
                  </select>
                  
                  <!-- Custom limb length input -->
                  <input 
                    v-if="formData.limb_length === 'Other'"
                    type="text"
                    v-model="formData.limb_length"
                    @focus="clearOtherValue('limb_length')"
                    class="w-full mt-2 form-input"
                    placeholder="Enter custom limb length (e.g., Extra Long)"
                    required
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Traditional Bow Configuration -->
          <div v-else-if="formData.bow_type === 'traditional'" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <!-- Traditional Riser Brand -->
              <div>
                <label for="tradRiserBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Riser Brand</label>
                <select 
                  id="tradRiserBrand"
                  :value="formData.riser_brand || ''"
                  @change="handleBrandSelection('riser_brand', $event.target.value)"
                  class="form-select"
                >
                  <option value="">Select Riser Brand</option>
                  <option v-if="loadingManufacturers" disabled>Loading manufacturers...</option>
                  <option 
                    v-for="manufacturer in manufacturerData.traditional_risers" 
                    :key="manufacturer" 
                    :value="manufacturer"
                  >
                    {{ manufacturer }}
                  </option>
                  <option value="Other">Other</option>
                </select>

                <!-- Custom traditional riser brand input -->
                <input 
                  v-if="formData.riser_brand === 'Other'"
                  type="text"
                  v-model="formData.custom_trad_riser_brand"
                  class="w-full mt-2 form-input"
                  placeholder="Enter riser brand name..."
                  required
                />
                
                <!-- Traditional Riser Length -->
                <div v-if="formData.riser_brand" class="mt-2">
                  <label class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Riser Length</label>
                  <select v-model="formData.riser_length" class="w-full form-select">
                    <option value="">Select Riser Length</option>
                    <option value="17">17"</option>
                    <option value="19">19"</option>
                    <option value="21">21"</option>
                    <option value="23">23"</option>
                    <option value="25">25"</option>
                    <option value="27">27"</option>
                    <option value="Other">Other (custom length)</option>
                  </select>
                  
                  <!-- Custom traditional riser length input -->
                  <input 
                    v-if="formData.riser_length === 'Other'"
                    type="text"
                    v-model="formData.riser_length"
                    @focus="clearOtherValue('riser_length')"
                    class="w-full mt-2 form-input"
                    placeholder="Enter custom riser length (e.g., 20 inches)"
                    required
                  />
                </div>
              </div>
              
              <!-- Traditional Limb Brand -->
              <div>
                <label for="tradLimbBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Brand</label>
                <select 
                  id="tradLimbBrand"
                  :value="formData.limb_brand || ''"
                  @change="handleBrandSelection('limb_brand', $event.target.value)"
                  class="form-select"
                >
                  <option value="">Select Limb Brand</option>
                  <option v-if="loadingManufacturers" disabled>Loading manufacturers...</option>
                  <option 
                    v-for="manufacturer in manufacturerData.traditional_limbs" 
                    :key="manufacturer" 
                    :value="manufacturer"
                  >
                    {{ manufacturer }}
                  </option>
                  <option value="Other">Other</option>
                </select>

                <!-- Custom traditional limb brand input -->
                <input 
                  v-if="formData.limb_brand === 'Other'"
                  type="text"
                  v-model="formData.custom_trad_limb_brand"
                  class="w-full mt-2 form-input"
                  placeholder="Enter limb brand name..."
                  required
                />
                
                <!-- Traditional Limb Length -->
                <div v-if="formData.limb_brand" class="mt-2">
                  <label class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Length</label>
                  <select v-model="formData.limb_length" class="w-full form-select">
                    <option value="">Select Limb Length</option>
                    <option value="Short">Short</option>
                    <option value="Medium">Medium</option>
                    <option value="Long">Long</option>
                    <option value="Other">Other (custom length)</option>
                  </select>
                  
                  <!-- Custom traditional limb length input -->
                  <input 
                    v-if="formData.limb_length === 'Other'"
                    type="text"
                    v-model="formData.limb_length"
                    @focus="clearOtherValue('limb_length')"
                    class="w-full mt-2 form-input"
                    placeholder="Enter custom limb length (e.g., Extra Short)"
                    required
                  />
                </div>
              </div>
            </div>
          </div>

        </div>
        
        <!-- Bow Usage -->
        <div class="mb-4">
          <label class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Bow Usage</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="usage in usageOptions"
              :key="usage"
              type="button"
              @click="toggleUsage(usage)"
              :class="[
                'px-3 py-1 text-sm rounded-full border transition-colors',
                isUsageSelected(usage)
                  ? 'bg-blue-500 text-white border-blue-500 dark:bg-blue-600 dark:border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
              ]"
            >
              {{ usage }}
            </button>
          </div>
        </div>

        <!-- Insert Weight -->
        <div>
          <label for="insert_weight" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            Insert Weight (grains)
          </label>
          <input
            id="insert_weight"
            v-model.number="formData.insert_weight"
            type="number"
            min="0"
            max="50"
            class="w-full form-input"
            placeholder="e.g., 12"
          />
        </div>

        <!-- Description -->
        <div class="mb-4">
          <label for="description" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Description (optional)</label>
          <textarea id="description" v-model="formData.description" class="form-textarea"></textarea>
        </div>

        <!-- Change Reason -->
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <label for="change_reason" class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            Reason for Changes
            <span class="text-blue-600 dark:text-blue-400 font-normal">(optional)</span>
          </label>
          <input
            id="change_reason"
            v-model="formData.change_reason"
            type="text"
            class="w-full px-3 py-2 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-blue-900/30 dark:border-blue-700 dark:text-blue-100"
            placeholder="e.g., Updated bow specifications, Changed draw weight..."
          />
          <p class="mt-2 text-sm text-blue-600 dark:text-blue-400">
            This note will be logged in your change history to help track modifications.
          </p>
        </div>

        <!-- Save Button -->
        <div class="flex justify-end space-x-4">
          <CustomButton
            type="button"
            @click="resetForm"
            variant="outlined"
            class="text-gray-600 border-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-400 dark:hover:bg-gray-700"
          >
            Reset Changes
          </CustomButton>
          
          <CustomButton
            type="submit"
            variant="filled"
            :disabled="saving || !hasChanges"
            class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700"
          >
            <span v-if="saving">
              <i class="fas fa-spinner fa-spin mr-2"></i>
              Saving...
            </span>
            <span v-else>
              <i class="fas fa-save mr-2"></i>
              Save Changes
            </span>
          </CustomButton>
        </div>
      </form>
    </div>

    <!-- Advanced Settings -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
        <i class="fas fa-tools mr-2 text-orange-600 dark:text-orange-400"></i>
        Advanced Actions
      </h3>

      <div class="space-y-4">
        <!-- Export Setup -->
        <div class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
          <div>
            <h4 class="font-medium text-gray-900 dark:text-gray-100">Export Setup</h4>
            <p class="text-sm text-gray-600 dark:text-gray-400">Download your bow setup data as JSON for backup or sharing.</p>
          </div>
          <CustomButton
            @click="exportSetup"
            variant="outlined"
            class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-900/20"
          >
            <i class="fas fa-download mr-2"></i>
            Export
          </CustomButton>
        </div>

        <!-- Duplicate Setup -->
        <div class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
          <div>
            <h4 class="font-medium text-gray-900 dark:text-gray-100">Duplicate Setup</h4>
            <p class="text-sm text-gray-600 dark:text-gray-400">Create a copy of this setup for testing different configurations.</p>
          </div>
          <CustomButton
            @click="duplicateSetup"
            variant="outlined"
            class="text-green-600 border-green-600 hover:bg-green-50 dark:text-green-400 dark:border-green-400 dark:hover:bg-green-900/20"
          >
            <i class="fas fa-copy mr-2"></i>
            Duplicate
          </CustomButton>
        </div>

        <!-- Delete Setup -->
        <div class="flex items-center justify-between p-4 border border-red-200 dark:border-red-700 rounded-lg bg-red-50 dark:bg-red-900/20">
          <div>
            <h4 class="font-medium text-red-900 dark:text-red-100">Delete Setup</h4>
            <p class="text-sm text-red-600 dark:text-red-400">Permanently remove this setup and all associated data.</p>
          </div>
          <CustomButton
            @click="showDeleteConfirm = true"
            variant="filled"
            class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700"
          >
            <i class="fas fa-trash mr-2"></i>
            Delete
          </CustomButton>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Confirm Deletion</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-6">
          Are you sure you want to delete this bow setup? This action cannot be undone.
        </p>
        <div class="flex justify-end space-x-4">
          <CustomButton
            @click="showDeleteConfirm = false"
            variant="outlined"
            class="text-gray-600 border-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-400 dark:hover:bg-gray-700"
          >
            Cancel
          </CustomButton>
          <CustomButton
            @click="handleDelete"
            variant="filled"
            :disabled="deleting"
            class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700"
          >
            <span v-if="deleting">
              <i class="fas fa-spinner fa-spin mr-2"></i>
              Deleting...
            </span>
            <span v-else>
              <i class="fas fa-trash mr-2"></i>
              Delete Setup
            </span>
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import CustomButton from './CustomButton.vue'

const props = defineProps({
  setup: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['setup-updated', 'show-notification'])

// Composables
const router = useRouter()
const api = useApi()

// State
const formData = ref({})
const originalData = ref({})
const saving = ref(false)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

// Manufacturer data for dropdowns (similar to AddBowSetupModal)
const manufacturerData = ref({
  compound_bows: [],
  recurve_risers: [],
  recurve_limbs: [],
  traditional_risers: [],
  traditional_limbs: [],
  longbows: []
})
const loadingManufacturers = ref(true)
const usageOptions = ['Target', 'Field', '3D', 'Hunting']

// Computed
const hasChanges = computed(() => {
  return JSON.stringify(formData.value) !== JSON.stringify(originalData.value)
})

// Methods
const initializeForm = () => {
  // Parse existing bow_usage if it's a JSON string
  let parsedBowUsage = []
  if (props.setup.bow_usage) {
    try {
      parsedBowUsage = Array.isArray(props.setup.bow_usage) 
        ? props.setup.bow_usage 
        : JSON.parse(props.setup.bow_usage)
    } catch {
      parsedBowUsage = []
    }
  }

  const setupData = {
    name: props.setup.name || '',
    bow_type: props.setup.bow_type || '',
    draw_weight: props.setup.draw_weight || 45,
    bow_usage: parsedBowUsage,
    ibo_speed: props.setup.ibo_speed || null,
    insert_weight: props.setup.insert_weight || null,
    compound_brand: props.setup.compound_brand || '',
    compound_model: props.setup.compound_model || '',
    riser_brand: props.setup.riser_brand || '',
    riser_model: props.setup.riser_model || '',
    riser_length: props.setup.riser_length || '',
    limb_brand: props.setup.limb_brand || '',
    limb_model: props.setup.limb_model || '',
    limb_length: props.setup.limb_length || '',
    description: props.setup.description || '',
    change_reason: '',
    
    // Form helper fields (like AddBowSetupModal)
    brand: props.setup.compound_brand || '', // Compound brand selection
    custom_brand: '',
    custom_riser_brand: '',
    custom_limb_brand: '',
    custom_trad_riser_brand: '',
    custom_trad_limb_brand: ''
  }
  
  formData.value = { ...setupData }
  originalData.value = { ...setupData }
}

const resetForm = () => {
  formData.value = { ...originalData.value }
  formData.value.change_reason = ''
}

// Usage toggle methods (from AddBowSetupModal)
const toggleUsage = (usage) => {
  const index = formData.value.bow_usage.indexOf(usage)
  if (index > -1) {
    formData.value.bow_usage.splice(index, 1)
  } else {
    formData.value.bow_usage.push(usage)
  }
}

const isUsageSelected = (usage) => {
  return formData.value.bow_usage.includes(usage)
}

// Brand selection handling (from AddBowSetupModal)
const handleBrandSelection = (fieldName, value) => {
  formData.value[fieldName] = value
  // Clear custom field when switching away from "Other"
  if (value !== 'Other') {
    const customFields = {
      'brand': 'custom_brand',
      'riser_brand': 'custom_riser_brand', 
      'limb_brand': 'custom_limb_brand',
    }
    
    const traditionalFields = {
      'riser_brand': 'custom_trad_riser_brand',
      'limb_brand': 'custom_trad_limb_brand'
    }
    
    if (customFields[fieldName]) {
      formData.value[customFields[fieldName]] = ''
    }
    
    // Clear traditional custom fields
    if (formData.value.bow_type === 'traditional' && traditionalFields[fieldName]) {
      formData.value[traditionalFields[fieldName]] = ''
    }
  }
}

const getBrandValue = (brandField, customField) => {
  const selectedBrand = formData.value[brandField]
  if (selectedBrand === 'Other') {
    return formData.value[customField] || null
  }
  return selectedBrand || null
}

const clearOtherValue = (fieldName) => {
  if (formData.value[fieldName] === 'Other') {
    formData.value[fieldName] = ''
  }
}

// Load manufacturers from API (from AddBowSetupModal)
const loadManufacturers = async () => {
  try {
    loadingManufacturers.value = true
    
    const response = await api.get('/bow-equipment/manufacturers')
    
    if (response && response.categories) {
      manufacturerData.value = {
        compound_bows: response.categories.compound_bows || [],
        recurve_risers: response.categories.recurve_risers || [],
        recurve_limbs: response.categories.recurve_limbs || [],
        traditional_risers: response.categories.traditional_risers || [],
        traditional_limbs: response.categories.traditional_limbs || [],
        longbows: response.categories.longbows || []
      }
    }
  } catch (error) {
    console.error('Error loading manufacturers:', error)
    
    // Fallback to hardcoded manufacturers if API fails
    manufacturerData.value = {
      compound_bows: ['Hoyt', 'Mathews', 'PSE', 'Bowtech', 'Prime', 'Elite', 'Bear', 'Diamond', 'Mission'],
      recurve_risers: ['Hoyt', 'Win&Win', 'Uukha', 'Samick', 'Bernardini', 'Border', 'Mybo'],
      recurve_limbs: ['Hoyt', 'Win&Win', 'Uukha', 'Border', 'Samick', 'SF Archery', 'Core', 'Fivics'],
      traditional_risers: ['Samick', 'Bear', 'PSE', 'Martin', 'Black Widow'],
      traditional_limbs: ['Samick', 'Bear', 'PSE', 'Martin', 'Black Widow'],
      longbows: ['Howard Hill', 'Bear', 'Bodnik', 'Black Widow', 'Great Plains', 'Three Rivers Archery', 'Martin', 'Samick']
    }
  } finally {
    loadingManufacturers.value = false
  }
}

const handleSave = async () => {
  try {
    saving.value = true
    
    // Prepare data similar to AddBowSetupModal's saveBowSetup method
    const { change_reason, brand, custom_brand, custom_riser_brand, custom_limb_brand, 
            custom_trad_riser_brand, custom_trad_limb_brand, ...baseData } = formData.value
    
    const payload = {
      ...baseData,
      bow_usage: JSON.stringify(formData.value.bow_usage || []),
      
      // Compound-specific fields
      compound_brand: formData.value.bow_type === 'compound' ? getBrandValue('brand', 'custom_brand') : '',
      
      // Recurve/Traditional-specific fields
      riser_brand: (formData.value.bow_type === 'recurve' || formData.value.bow_type === 'traditional') 
        ? (formData.value.bow_type === 'traditional' 
          ? getBrandValue('riser_brand', 'custom_trad_riser_brand')
          : getBrandValue('riser_brand', 'custom_riser_brand')) : '',
      limb_brand: (formData.value.bow_type === 'recurve' || formData.value.bow_type === 'traditional')
        ? (formData.value.bow_type === 'traditional'
          ? getBrandValue('limb_brand', 'custom_trad_limb_brand')
          : getBrandValue('limb_brand', 'custom_limb_brand')) : '',
      
      user_note: change_reason || 'Setup configuration updated'
    }
    
    await api.put(`/bow-setups/${props.setup.id}`, payload)
    
    emit('show-notification', 'Setup configuration saved successfully', 'success')
    emit('setup-updated')
    
    // Update original data to reflect saved state
    originalData.value = { ...formData.value }
    formData.value.change_reason = ''
    
  } catch (error) {
    console.error('Error saving setup:', error)
    emit('show-notification', 'Failed to save setup configuration', 'error')
  } finally {
    saving.value = false
  }
}

const exportSetup = () => {
  try {
    const exportData = {
      ...props.setup,
      exported_at: new Date().toISOString(),
      export_version: '1.0'
    }
    
    const dataStr = JSON.stringify(exportData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    
    const link = document.createElement('a')
    link.href = URL.createObjectURL(dataBlob)
    link.download = `${props.setup.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_setup.json`
    link.click()
    
    emit('show-notification', 'Setup exported successfully', 'success')
  } catch (error) {
    console.error('Error exporting setup:', error)
    emit('show-notification', 'Failed to export setup', 'error')
  }
}

const duplicateSetup = async () => {
  try {
    const { id, created_at, ...setupData } = props.setup
    
    const duplicatedSetup = {
      ...setupData,
      name: `${setupData.name} (Copy)`,
      description: `Copy of ${setupData.name}${setupData.description ? '\n\nOriginal description:\n' + setupData.description : ''}`
    }
    
    const response = await api.post('/bow-setups', duplicatedSetup)
    
    emit('show-notification', 'Setup duplicated successfully', 'success')
    
    // Navigate to the new setup
    router.push(`/setups/${response.id}`)
    
  } catch (error) {
    console.error('Error duplicating setup:', error)
    emit('show-notification', 'Failed to duplicate setup', 'error')
  }
}

const handleDelete = async () => {
  try {
    deleting.value = true
    
    await api.delete(`/bow-setups/${props.setup.id}`)
    
    emit('show-notification', 'Setup deleted successfully', 'success')
    
    // Navigate back to setups list
    router.push('/my-setup')
    
  } catch (error) {
    console.error('Error deleting setup:', error)
    emit('show-notification', 'Failed to delete setup', 'error')
  } finally {
    deleting.value = false
    showDeleteConfirm.value = false
  }
}

// Watchers
watch(() => props.setup, () => {
  initializeForm()
}, { immediate: true, deep: true })

// Lifecycle
onMounted(() => {
  loadManufacturers()
  initializeForm()
})
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
.form-textarea {
  @apply w-full h-24 resize-y;
}

/* Slider Styling */
.slider {
  -webkit-appearance: none;
  appearance: none;
  background: linear-gradient(to right, #3b82f6 0%, #3b82f6 50%, #d1d5db 50%, #d1d5db 100%);
  outline: none;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.slider:hover {
  opacity: 1;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.dark .slider {
  background: linear-gradient(to right, #3b82f6 0%, #3b82f6 50%, #4b5563 50%, #4b5563 100%);
}

.dark .slider::-webkit-slider-thumb {
  background: #3b82f6;
}

.dark .slider::-moz-range-thumb {
  background: #3b82f6;
}
</style>