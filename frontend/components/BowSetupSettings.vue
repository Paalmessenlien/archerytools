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
              <option v-for="bt in bowTypes" :key="bt.value" :value="bt.value">
                {{ bt.label }}
              </option>
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
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider mobile-slider-safe"
            />
            <div class="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
              <span>20 lbs</span>
              <span>80 lbs</span>
            </div>
          </div>

          <!-- Universal Draw Length Slider (All Bow Types) -->
          <div v-if="formData.bow_type">
            <label class="block mb-3 text-sm font-medium text-gray-700 dark:text-gray-300">
              Draw Length: <span class="font-semibold text-blue-600 dark:text-blue-400">{{ formData.draw_length || 28 }}"</span>
            </label>
            <input 
              type="range" 
              min="24" 
              max="34" 
              step="0.25" 
              v-model.number="formData.draw_length"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider mobile-slider-safe"
            />
            <div class="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
              <span>24"</span>
              <span>34"</span>
            </div>
            <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
              <span v-if="formData.bow_type === 'compound'">Module-based draw length setting for compound bows</span>
              <span v-else>Physical measurement from nock point to pivot point plus 1.75"</span>
            </p>
          </div>
        </div>
        
        <!-- Bow Type Specific Configuration -->
        <div v-if="formData.bow_type" class="p-4 mb-4 border border-gray-200 rounded-lg bg-gray-50 dark:bg-gray-700/50 dark:border-gray-600">
          <button 
            @click="showBowTypeConfig = !showBowTypeConfig"
            type="button"
            class="flex items-center justify-between w-full mb-4 text-sm font-semibold text-gray-900 dark:text-gray-100 touch-target"
          >
            <div class="flex items-center">
              <i class="mr-2 text-blue-600 fas fa-cog"></i>
              {{ formData.bow_type?.charAt(0).toUpperCase() + formData.bow_type?.slice(1) }} Specific Configuration
            </div>
            <i class="fas transition-transform duration-200" :class="showBowTypeConfig ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
          </button>
          
          <div v-show="showBowTypeConfig" class="space-y-4"
               :class="{ 'md:block': !showBowTypeConfig }"
          >

          <!-- Compound Bow Configuration -->
          <div v-if="isCompoundStyle(formData.bow_type)" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <!-- Compound Brand Selection -->
              <div>
                <ManufacturerInput
                  v-model="formData.compound_brand"
                  category="compound_bows"
                  label="Bow Brand"
                  placeholder="Enter compound bow manufacturer..."
                  :required="false"
                  @manufacturer-selected="handleManufacturerSelected"
                  @manufacturer-created="handleManufacturerCreated"
                />

                <!-- Compound Model Name -->
                <input 
                  v-if="formData.compound_brand"
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
          <div v-else-if="isRecurveBarebow(formData.bow_type)" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <!-- Riser Brand Selection -->
              <div>
                <ManufacturerInput
                  v-model="formData.riser_brand"
                  category="recurve_risers"
                  label="Riser Brand"
                  placeholder="Enter recurve riser manufacturer..."
                  :required="false"
                  @manufacturer-selected="handleManufacturerSelected"
                  @manufacturer-created="handleManufacturerCreated"
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
                <ManufacturerInput
                  v-model="formData.limb_brand"
                  category="recurve_limbs"
                  label="Limb Brand"
                  placeholder="Enter recurve limb manufacturer..."
                  :required="false"
                  @manufacturer-selected="handleManufacturerSelected"
                  @manufacturer-created="handleManufacturerCreated"
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
            
            <div>
              <label for="limbFitting" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Fitting</label>
              <select id="limbFitting" v-model="formData.limb_fitting" class="form-select">
                <option value="ILF">ILF (International Limb Fitting)</option>
                <option value="Formula">Formula (WA Standard)</option>
              </select>
            </div>
          </div>

          <!-- Traditional Bow Configuration -->
          <div v-else-if="isTraditionalStyle(formData.bow_type)" class="space-y-4">
            <div>
              <label for="construction" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Construction Type</label>
              <select id="construction" v-model="formData.construction" class="form-select">
                <option value="one_piece">One Piece</option>
                <option value="two_piece">Two Piece (Takedown)</option>
              </select>
            </div>

            <!-- Two-piece specific fields -->
            <div v-if="formData.construction === 'two_piece'" class="space-y-4">
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <!-- Traditional Riser Brand -->
                <div>
                  <ManufacturerInput
                    v-model="formData.riser_brand"
                    category="traditional_risers"
                    label="Riser Brand"
                    placeholder="Enter traditional riser manufacturer..."
                    :required="false"
                    @manufacturer-selected="handleManufacturerSelected"
                    @manufacturer-created="handleManufacturerCreated"
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
                  <ManufacturerInput
                    v-model="formData.limb_brand"
                    category="traditional_limbs"
                    label="Limb Brand"
                    placeholder="Enter traditional limb manufacturer..."
                    :required="false"
                    @manufacturer-selected="handleManufacturerSelected"
                    @manufacturer-created="handleManufacturerCreated"
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
              
              <div>
                <label for="tradLimbFitting" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Fitting</label>
                <select id="tradLimbFitting" v-model="formData.limb_fitting" class="form-select">
                  <option value="ILF">ILF (International Limb Fitting)</option>
                  <option value="Bolt_Down">Bolt Down</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Longbow Configuration -->
          <div v-else-if="isLongbowStyle(formData.bow_type)" class="space-y-4">
            <div>
              <ManufacturerInput
                v-model="formData.bow_brand"
                category="longbows"
                label="Bow Brand/Maker"
                placeholder="Enter longbow manufacturer..."
                :required="false"
                @manufacturer-selected="handleManufacturerSelected"
                @manufacturer-created="handleManufacturerCreated"
              />
            </div>
          </div>
          </div>
        </div>
        
        <!-- Bow Usage -->
        <div class="mb-4">
          <label class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Bow Usage</label>
          <div class="grid grid-cols-2 md:flex md:flex-wrap gap-2">
            <button
              v-for="usage in usageOptions"
              :key="usage"
              type="button"
              @click="toggleUsage(usage)"
              :class="[
                'px-4 py-3 text-sm rounded-lg border transition-colors touch-target flex items-center justify-center font-medium',
                isUsageSelected(usage)
                  ? 'bg-blue-500 text-white border-blue-500 dark:bg-blue-600 dark:border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
              ]"
            >
              {{ usage }}
            </button>
          </div>
        </div>



        <!-- Description -->
        <div class="mb-4">
          <label for="description" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Description (optional)</label>
          <textarea id="description" v-model="formData.description" class="form-textarea"></textarea>
        </div>

        <!-- Bow Setup Images -->
        <div class="mb-4">
          <label class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            <i class="fas fa-camera mr-2 text-blue-600 dark:text-purple-400"></i>
            Bow Setup Images ({{ attachedImages.length }}/3)
          </label>
          
          <!-- Current Images Display -->
          <div v-if="attachedImages.length" class="mb-3">
            <div class="grid grid-cols-3 gap-3">
              <div v-for="(image, index) in attachedImages" :key="index" class="relative group">
                <img 
                  :src="image.url" 
                  :alt="image.alt || 'Bow setup image'" 
                  class="w-full h-20 object-cover rounded-lg border border-gray-200 dark:border-gray-600"
                />
                <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                  <button 
                    @click="removeImage(index)" 
                    class="p-1 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors"
                    type="button"
                    title="Remove image"
                  >
                    <i class="fas fa-trash text-xs"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Image Upload Component -->
          <div v-if="attachedImages.length < 3">
            <ImageUpload
              :current-image-url="''"
              alt-text="Bow setup image"
              upload-path="bow_setup"
              :max-size-bytes="52428800"
              @upload-success="handleImageUpload"
              @upload-error="handleImageError"
            />
          </div>
          
          <!-- Upload Guidelines -->
          <div class="text-xs text-gray-600 dark:text-gray-400 mt-2">
            <i class="fas fa-info-circle mr-1"></i>
            Add up to 3 photos of your bow setup (max 50MB each)
          </div>
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
import { useImageUpload } from '~/composables/useImageUpload'
import CustomButton from './CustomButton.vue'
import ManufacturerInput from './ManufacturerInput.vue'
import ImageUpload from '~/components/ImageUpload.vue'

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

// Dynamic bow types from API
const bowTypes = ref([
  { value: 'compound', label: 'Compound', is_default: true },
  { value: 'recurve', label: 'Recurve', is_default: true },
  { value: 'barebow', label: 'Barebow', is_default: true },
  { value: 'longbow', label: 'Longbow', is_default: true },
  { value: 'traditional', label: 'Traditional', is_default: true }
])

const loadBowTypes = async () => {
  try {
    const response = await api.get('/bow-types')
    if (response.bow_types && response.bow_types.length > 0) {
      bowTypes.value = response.bow_types
    }
  } catch (error) {
    console.error('Error loading bow types:', error)
    // Keep default bow types on error
  }
}

// Check if bow type uses riser/limbs (recurve-style)
const usesRiserLimbs = (bowTypeValue) => {
  const bt = bowTypes.value.find(b => b.value === bowTypeValue)
  if (bt && bt.config_template) {
    return bt.config_template === 'recurve' || bt.config_template === 'barebow' || bt.config_template === 'traditional'
  }
  return bowTypeValue === 'recurve' || bowTypeValue === 'traditional' || bowTypeValue === 'barebow'
}

// Check if bow type is compound-style
const isCompoundStyle = (bowTypeValue) => {
  const bt = bowTypes.value.find(b => b.value === bowTypeValue)
  if (bt && bt.config_template) {
    return bt.config_template === 'compound'
  }
  return bowTypeValue === 'compound'
}

// Check if bow type is longbow-style
const isLongbowStyle = (bowTypeValue) => {
  const bt = bowTypes.value.find(b => b.value === bowTypeValue)
  if (bt && bt.config_template) {
    return bt.config_template === 'longbow'
  }
  return bowTypeValue === 'longbow'
}

// Check if bow type is recurve or barebow style (uses riser+limbs but NOT traditional)
const isRecurveBarebow = (bowTypeValue) => {
  const bt = bowTypes.value.find(b => b.value === bowTypeValue)
  if (bt && bt.config_template) {
    return bt.config_template === 'recurve' || bt.config_template === 'barebow'
  }
  return bowTypeValue === 'recurve' || bowTypeValue === 'barebow'
}

// Check if bow type is traditional style
const isTraditionalStyle = (bowTypeValue) => {
  const bt = bowTypes.value.find(b => b.value === bowTypeValue)
  if (bt && bt.config_template) {
    return bt.config_template === 'traditional'
  }
  return bowTypeValue === 'traditional'
}

// Image Upload Composable
const imageUpload = useImageUpload({
  context: 'bow_setup',
  maxFiles: 3,
  maxSize: 50
})

// State for attached images
const attachedImages = ref([])

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
const showBowTypeConfig = ref(true)
const usageOptions = ['Target', 'Field', '3D', 'Hunting']

// Computed
const hasChanges = computed(() => {
  const formChanged = JSON.stringify(formData.value) !== JSON.stringify(originalData.value)
  const imagesChanged = JSON.stringify(attachedImages.value) !== JSON.stringify(originalData.value.images || [])
  return formChanged || imagesChanged
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
    draw_length: props.setup.draw_length || null,
    
    // Bow type specific fields
    bow_brand: props.setup.bow_brand || '', // For longbow
    limb_fitting: props.setup.limb_fitting || 'ILF',
    construction: props.setup.construction || 'one_piece'
  }
  
  formData.value = { ...setupData }
  originalData.value = { ...setupData }
  
  // Initialize images if available (for editing mode)
  if (props.setup.images && Array.isArray(props.setup.images)) {
    attachedImages.value = props.setup.images.map(img => ({
      url: img.url || img.cdnUrl,
      cdnUrl: img.cdnUrl,
      originalName: img.originalName || 'bow-setup-image.jpg',
      uploadedAt: img.uploadedAt || new Date().toISOString(),
      alt: img.alt || `${props.setup.name || 'Bow Setup'} - Setup Image`
    }))
    // Store original images for comparison
    originalData.value.images = [...attachedImages.value]
  } else {
    attachedImages.value = []
    originalData.value.images = []
  }
}

const resetForm = () => {
  formData.value = { ...originalData.value }
  formData.value.change_reason = ''
  // Reset images to original state
  attachedImages.value = originalData.value.images ? [...originalData.value.images] : []
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

// Handle manufacturer selection from ManufacturerInput component
const handleManufacturerSelected = (data) => {
  console.log('Manufacturer selected:', data)
  // The v-model binding will automatically update the manufacturer name
  // Additional logic could be added here if needed
}

// Handle new manufacturer creation from ManufacturerInput component
const handleManufacturerCreated = (data) => {
  console.log('New manufacturer created:', data)
  // Could show a notification to the user about pending approval
  // The v-model binding will handle the manufacturer name
}

const clearOtherValue = (fieldName) => {
  if (formData.value[fieldName] === 'Other') {
    formData.value[fieldName] = ''
  }
}

// Legacy loadManufacturers function - no longer needed as ManufacturerInput handles this
// Kept for backward compatibility but disabled
const loadManufacturers = async () => {
  // ManufacturerInput component now handles manufacturer loading
  console.log('Legacy loadManufacturers called - now handled by ManufacturerInput component')
  loadingManufacturers.value = false
}

const handleSave = async () => {
  try {
    saving.value = true
    
    // Prepare data similar to AddBowSetupModal's saveBowSetup method
    const { change_reason, ...baseData } = formData.value
    
    const payload = {
      id: props.setup?.id, // Include ID for updates
      name: formData.value.name,
      bow_type: formData.value.bow_type,
      draw_weight: Number(formData.value.draw_weight),
      draw_length: Number(formData.value.draw_length) || null,
      description: formData.value.description || '',
      bow_usage: JSON.stringify(formData.value.bow_usage || []),
      
      // Compound-specific fields
      compound_brand: isCompoundStyle(formData.value.bow_type) ? formData.value.compound_brand || '' : '',
      compound_model: isCompoundStyle(formData.value.bow_type) ? formData.value.compound_model || '' : '',
      ibo_speed: isCompoundStyle(formData.value.bow_type) ? Number(formData.value.ibo_speed) || null : null,

      // Recurve/Traditional/Barebow-specific fields (riser and limbs)
      riser_brand: usesRiserLimbs(formData.value.bow_type) ? formData.value.riser_brand || '' : '',
      riser_model: usesRiserLimbs(formData.value.bow_type) ? formData.value.riser_model || '' : '',
      riser_length: usesRiserLimbs(formData.value.bow_type) ? formData.value.riser_length || '' : '',
      limb_brand: usesRiserLimbs(formData.value.bow_type) ? formData.value.limb_brand || '' : '',
      limb_model: usesRiserLimbs(formData.value.bow_type) ? formData.value.limb_model || '' : '',
      limb_length: usesRiserLimbs(formData.value.bow_type) ? formData.value.limb_length || '' : '',
      limb_fitting: usesRiserLimbs(formData.value.bow_type) ? formData.value.limb_fitting || 'ILF' : '',
      construction: isTraditionalStyle(formData.value.bow_type) ? formData.value.construction || 'one_piece' : '',

      // Longbow-specific fields
      bow_brand: isLongbowStyle(formData.value.bow_type) ? formData.value.bow_brand || '' : '',
      
      user_note: change_reason || 'Setup configuration updated'
    }
    
    // Add images to payload
    payload.images = attachedImages.value.map(img => ({
      url: img.url,
      cdnUrl: img.cdnUrl,
      originalName: img.originalName,
      alt: img.alt
    }))
    
    await api.put(`/bow-setups/${props.setup.id}`, payload)
    
    emit('show-notification', 'Setup configuration saved successfully', 'success')
    emit('setup-updated')
    
    // Update original data to reflect saved state
    originalData.value = { ...formData.value }
    originalData.value.images = [...attachedImages.value]
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

// Image handling methods
const handleImageUpload = (uploadResult) => {
  console.log('Bow setup image uploaded:', uploadResult)
  if (uploadResult && uploadResult.url) {
    attachedImages.value.push({
      url: uploadResult.url,
      cdnUrl: uploadResult.cdnUrl,
      originalName: uploadResult.originalName || 'bow-setup-image.jpg',
      uploadedAt: new Date().toISOString(),
      alt: `${formData.value.name || 'Bow Setup'} - Setup Image`
    })
  }
}

const handleImageError = (error) => {
  console.error('Bow setup image upload error:', error)
  emit('show-notification', 'Failed to upload image', 'error')
}

const removeImage = (index) => {
  attachedImages.value.splice(index, 1)
}

// Watchers
watch(() => props.setup, () => {
  initializeForm()
}, { immediate: true, deep: true })

// Lifecycle
onMounted(() => {
  loadManufacturers()
  loadBowTypes()
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