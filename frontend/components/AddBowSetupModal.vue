<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="w-full max-w-lg p-6 bg-white shadow-lg dark:bg-gray-800 rounded-xl">
      <h3 class="mb-4 text-xl font-semibold text-gray-900 dark:text-gray-100">
        {{ props.modelValue?.id ? 'Edit Bow Setup' : 'Add New Bow Setup' }}
      </h3>
      <form @submit.prevent="saveBowSetup">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div class="mb-4">
            <label for="setupName" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Setup Name</label>
            <input type="text" id="setupName" v-model="setupData.name" class="form-input" required />
          </div>
          <div class="mb-4">
            <label for="bowType" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Bow Type</label>
            <select id="bowType" v-model="setupData.bow_type" class="form-select" required>
              <option value="">Select Bow Type</option>
              <option value="compound">Compound</option>
              <option value="recurve">Recurve</option>
              <option value="longbow">Longbow</option>
              <option value="traditional">Traditional</option>
            </select>
          </div>
          <div class="mb-4">
            <label for="drawWeight" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Draw Weight (lbs)</label>
            <input type="number" id="drawWeight" v-model.number="setupData.draw_weight" class="form-input" required step="0.5" />
          </div>
          <div class="mb-4">
            <label for="drawLength" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Draw Length (inches)</label>
            <input type="number" id="drawLength" v-model.number="setupData.draw_length" class="form-input" required step="0.1" />
          </div>
          <div class="mb-4">
            <label for="arrowLength" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Arrow Length (inches)</label>
            <input type="number" id="arrowLength" v-model.number="setupData.arrow_length" class="form-input" required step="0.1" />
          </div>
          <div class="mb-4">
            <label for="pointWeight" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Point Weight (gn)</label>
            <input type="number" id="pointWeight" v-model.number="setupData.point_weight" class="form-input" required step="0.5" min="40" />
          </div>
        </div>
        
        <!-- Bow Type Specific Configuration -->
        <div v-if="setupData.bow_type" class="p-4 mb-4 bg-gray-50 border border-gray-200 rounded-lg dark:bg-gray-700/50 dark:border-gray-600">
          <h4 class="flex items-center mb-4 text-sm font-semibold text-gray-900 dark:text-gray-100">
            <i class="mr-2 text-blue-600 fas fa-cog"></i>
            {{ setupData.bow_type.charAt(0).toUpperCase() + setupData.bow_type.slice(1) }} Specific Configuration
          </h4>

          <!-- Compound Bow Configuration -->
          <div v-if="setupData.bow_type === 'compound'" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <!-- Compound Brand Selection -->
              <div>
                <label for="compoundBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Bow Brand</label>
                <select 
                  id="compoundBrand" 
                  :value="setupData.brand || ''"
                  @change="handleBrandSelection('brand', $event.target.value)"
                  class="form-select"
                >
                  <option value="">Select Brand</option>
                  <option value="Hoyt">Hoyt</option>
                  <option value="Mathews">Mathews</option>
                  <option value="PSE">PSE</option>
                  <option value="Bowtech">Bowtech</option>
                  <option value="Prime">Prime</option>
                  <option value="Elite">Elite</option>
                  <option value="Bear">Bear</option>
                  <option value="Diamond">Diamond</option>
                  <option value="Mission">Mission</option>
                  <option value="Other">Other</option>
                </select>

                <!-- Custom brand input when "Other" is selected -->
                <input 
                  v-if="setupData.brand === 'Other'"
                  type="text"
                  v-model="setupData.custom_brand"
                  class="w-full mt-2 form-input"
                  placeholder="Enter brand name..."
                  required
                />

                <!-- Compound Model Name -->
                <input 
                  v-if="setupData.brand"
                  type="text"
                  v-model="setupData.compound_model"
                  class="w-full mt-2 form-input"
                  placeholder="e.g., RX-7 Ultra, Halon X, V3X..."
                />
              </div>
              
              <div>
                <label for="iboSpeed" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">IBO Speed (fps)</label>
                <input 
                  type="number"
                  id="iboSpeed"
                  v-model.number="setupData.ibo_speed"
                  class="form-input"
                  placeholder="e.g., 320, 340..."
                />
              </div>
            </div>
          </div>

          <!-- Recurve Bow Configuration -->
          <div v-else-if="setupData.bow_type === 'recurve'" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <!-- Riser Brand Selection -->
              <div>
                <label for="riserBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Riser Brand</label>
                <select 
                  id="riserBrand"
                  :value="setupData.riser_brand || ''"
                  @change="handleBrandSelection('riser_brand', $event.target.value)"
                  class="form-select"
                >
                  <option value="">Select Riser Brand</option>
                  <option value="Hoyt">Hoyt</option>
                  <option value="Win&Win">Win&Win</option>
                  <option value="Uukha">Uukha</option>
                  <option value="Samick">Samick</option>
                  <option value="Bernardini">Bernardini</option>
                  <option value="Border">Border</option>
                  <option value="Mybo">Mybo</option>
                  <option value="Fivics">Fivics</option>
                  <option value="Other">Other</option>
                </select>

                <!-- Custom riser brand input -->
                <input 
                  v-if="setupData.riser_brand === 'Other'"
                  type="text"
                  v-model="setupData.custom_riser_brand"
                  class="w-full mt-2 form-input"
                  placeholder="Enter riser brand name..."
                  required
                />

                <!-- Riser Model Name -->
                <input 
                  v-if="setupData.riser_brand"
                  type="text"
                  v-model="setupData.riser_model"
                  class="w-full mt-2 form-input"
                  placeholder="e.g., Formula X, Prodigy, Epic..."
                />
              </div>
              
              <!-- Limb Brand Selection -->
              <div>
                <label for="limbBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Brand</label>
                <select 
                  id="limbBrand"
                  :value="setupData.limb_brand || ''"
                  @change="handleBrandSelection('limb_brand', $event.target.value)"
                  class="form-select"
                >
                  <option value="">Select Limb Brand</option>
                  <option value="Hoyt">Hoyt</option>
                  <option value="Win&Win">Win&Win</option>
                  <option value="Uukha">Uukha</option>
                  <option value="Border">Border</option>
                  <option value="Samick">Samick</option>
                  <option value="SF Archery">SF Archery</option>
                  <option value="Core">Core</option>
                  <option value="Fivics">Fivics</option>
                  <option value="Other">Other</option>
                </select>

                <!-- Custom limb brand input -->
                <input 
                  v-if="setupData.limb_brand === 'Other'"
                  type="text"
                  v-model="setupData.custom_limb_brand"
                  class="w-full mt-2 form-input"
                  placeholder="Enter limb brand name..."
                  required
                />

                <!-- Limb Model Name -->
                <input 
                  v-if="setupData.limb_brand"
                  type="text"
                  v-model="setupData.limb_model"
                  class="w-full mt-2 form-input"
                  placeholder="e.g., Quattro, Inno Max, Veloce..."
                />
              </div>
            </div>
            
            <div>
              <label for="limbFitting" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Fitting</label>
              <select id="limbFitting" v-model="setupData.limb_fitting" class="form-select">
                <option value="ILF">ILF (International Limb Fitting)</option>
                <option value="Formula">Formula (WA Standard)</option>
              </select>
            </div>
          </div>

          <!-- Traditional Bow Configuration -->
          <div v-else-if="setupData.bow_type === 'traditional'" class="space-y-4">
            <div>
              <label for="construction" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Construction Type</label>
              <select id="construction" v-model="setupData.construction" class="form-select">
                <option value="one_piece">One Piece</option>
                <option value="two_piece">Two Piece (Takedown)</option>
              </select>
            </div>

            <!-- Two-piece specific fields -->
            <div v-if="setupData.construction === 'two_piece'" class="space-y-4">
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <!-- Traditional Riser Brand -->
                <div>
                  <label for="tradRiserBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Riser Brand</label>
                  <select 
                    id="tradRiserBrand"
                    :value="setupData.riser_brand || ''"
                    @change="handleBrandSelection('riser_brand', $event.target.value)"
                    class="form-select"
                  >
                    <option value="">Select Riser Brand</option>
                    <option value="Samick">Samick</option>
                    <option value="Bear">Bear</option>
                    <option value="PSE">PSE</option>
                    <option value="Martin">Martin</option>
                    <option value="Black Widow">Black Widow</option>
                    <option value="Sage">Sage</option>
                    <option value="Other">Other</option>
                  </select>

                  <!-- Custom traditional riser brand input -->
                  <input 
                    v-if="setupData.riser_brand === 'Other'"
                    type="text"
                    v-model="setupData.custom_trad_riser_brand"
                    class="w-full mt-2 form-input"
                    placeholder="Enter riser brand name..."
                    required
                  />
                </div>
                
                <!-- Traditional Limb Brand -->
                <div>
                  <label for="tradLimbBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Brand</label>
                  <select 
                    id="tradLimbBrand"
                    :value="setupData.limb_brand || ''"
                    @change="handleBrandSelection('limb_brand', $event.target.value)"
                    class="form-select"
                  >
                    <option value="">Select Limb Brand</option>
                    <option value="Samick">Samick</option>
                    <option value="Bear">Bear</option>
                    <option value="PSE">PSE</option>
                    <option value="Martin">Martin</option>
                    <option value="Black Widow">Black Widow</option>
                    <option value="Sage">Sage</option>
                    <option value="Other">Other</option>
                  </select>

                  <!-- Custom traditional limb brand input -->
                  <input 
                    v-if="setupData.limb_brand === 'Other'"
                    type="text"
                    v-model="setupData.custom_trad_limb_brand"
                    class="w-full mt-2 form-input"
                    placeholder="Enter limb brand name..."
                    required
                  />
                </div>
              </div>
              
              <div>
                <label for="tradLimbFitting" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Limb Fitting</label>
                <select id="tradLimbFitting" v-model="setupData.limb_fitting" class="form-select">
                  <option value="ILF">ILF (International Limb Fitting)</option>
                  <option value="Bolt_Down">Bolt Down</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Longbow Configuration -->
          <div v-else-if="setupData.bow_type === 'longbow'" class="space-y-4">
            <div>
              <label for="longbowBrand" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Bow Brand/Maker</label>
              <select 
                id="longbowBrand"
                :value="setupData.bow_brand || ''"
                @change="handleBrandSelection('bow_brand', $event.target.value)"
                class="form-select"
              >
                <option value="">Select Brand/Maker</option>
                <option value="Howard Hill">Howard Hill</option>
                <option value="Bear">Bear</option>
                <option value="Bodnik">Bodnik</option>
                <option value="Black Widow">Black Widow</option>
                <option value="Great Plains">Great Plains</option>
                <option value="Three Rivers Archery">Three Rivers Archery</option>
                <option value="Martin">Martin</option>
                <option value="Samick">Samick</option>
                <option value="Other">Other</option>
              </select>

              <!-- Custom bow brand input -->
              <input 
                v-if="setupData.bow_brand === 'Other'"
                type="text"
                v-model="setupData.custom_bow_brand"
                class="w-full mt-2 form-input"
                placeholder="Enter brand or maker name..."
                required
              />
            </div>
          </div>
        </div>
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
                  ? 'bg-blue-500 text-white border-blue-500 dark:bg-purple-600 dark:border-purple-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
              ]"
            >
              {{ usage }}
            </button>
          </div>
        </div>
        <div class="mb-4">
          <label for="description" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Description (optional)</label>
          <textarea id="description" v-model="setupData.description" class="form-textarea"></textarea>
        </div>

        <div class="flex justify-end space-x-3">
          <CustomButton
            type="button"
            @click="$emit('close')"
            variant="outlined"
            class="text-gray-700 dark:text-gray-200"
          >
            Cancel
          </CustomButton>
          <CustomButton
            type="submit"
            variant="filled"
            :disabled="isSaving"
            class="text-white bg-blue-600 hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
          >
            <span v-if="isSaving">Saving...</span>
            <span v-else>{{ props.modelValue?.id ? 'Update Setup' : 'Add Setup' }}</span>
          </CustomButton>
        </div>
        <p v-if="error" class="mt-3 text-sm text-red-500">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: Object, // Represents newSetup object
  isSaving: Boolean,
  error: String,
});

const emit = defineEmits(['update:modelValue', 'save', 'close']);

// Create a local ref to work with the form data
const setupData = ref({
  name: '',
  bow_type: '',
  draw_weight: null,
  draw_length: null,
  arrow_length: null,
  point_weight: 100,
  description: '',
  riser_brand: '',
  riser_model: '',
  limb_brand: '',
  limb_model: '',
  compound_brand: '',
  compound_model: '',
  bow_usage: [],
  // Additional fields for proper API compatibility
  brand: '', // For compound bow brand selection
  custom_brand: '',
  custom_riser_brand: '',
  custom_limb_brand: '',
  bow_brand: '', // For longbow brand
  custom_bow_brand: '',
  ibo_speed: '',
  limb_fitting: 'ILF',
  construction: 'one_piece',
  custom_trad_riser_brand: '',
  custom_trad_limb_brand: '',
});

const usageOptions = ['Target', 'Field', '3D', 'Hunting'];

const toggleUsage = (usage) => {
  const index = setupData.value.bow_usage.indexOf(usage);
  if (index > -1) {
    setupData.value.bow_usage.splice(index, 1);
  } else {
    setupData.value.bow_usage.push(usage);
  }
};

const isUsageSelected = (usage) => {
  return setupData.value.bow_usage.includes(usage);
};

// Watch for changes in the modelValue prop and update local setupData
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    setupData.value = { 
      ...setupData.value, // Keep the extended fields
      ...newValue, // Override with provided values
      // Map existing brand data to the correct form fields
      brand: newValue.compound_brand || '',
      riser_brand: newValue.riser_brand || '',
      limb_brand: newValue.limb_brand || '',
      riser_model: newValue.riser_model || '',
      limb_model: newValue.limb_model || '',
      compound_model: newValue.compound_model || '',
      bow_usage: Array.isArray(newValue.bow_usage) ? newValue.bow_usage : []
    };
  }
}, { immediate: true });

const handleBrandSelection = (fieldName, value) => {
  setupData.value[fieldName] = value;
  // Clear custom field when switching away from "Other"
  if (value !== 'Other') {
    const customFields = {
      'brand': 'custom_brand',
      'riser_brand': 'custom_riser_brand', 
      'limb_brand': 'custom_limb_brand',
      'bow_brand': 'custom_bow_brand'
    };
    
    const traditionalFields = {
      'riser_brand': 'custom_trad_riser_brand',
      'limb_brand': 'custom_trad_limb_brand'
    };
    
    if (customFields[fieldName]) {
      setupData.value[customFields[fieldName]] = '';
    }
    
    // Clear traditional custom fields
    if (setupData.value.bow_type === 'traditional' && traditionalFields[fieldName]) {
      setupData.value[traditionalFields[fieldName]] = '';
    }
  }
};

const getBrandValue = (brandField, customField) => {
  const selectedBrand = setupData.value[brandField];
  if (selectedBrand === 'Other') {
    return setupData.value[customField] || null;
  }
  return selectedBrand || null;
};

const saveBowSetup = () => {
  // Transform the data to match API expectations
  const transformedData = {
    name: setupData.value.name,
    bow_type: setupData.value.bow_type,
    draw_weight: Number(setupData.value.draw_weight),
    draw_length: setupData.value.draw_length,
    arrow_length: setupData.value.arrow_length,
    point_weight: Number(setupData.value.point_weight),
    description: setupData.value.description,
    bow_usage: JSON.stringify(setupData.value.bow_usage), // Convert to JSON array
    // Map brand fields correctly to database schema
    compound_brand: setupData.value.bow_type === 'compound' ? getBrandValue('brand', 'custom_brand') : '',
    compound_model: setupData.value.bow_type === 'compound' ? setupData.value.compound_model || '' : '',
    riser_brand: (setupData.value.bow_type === 'recurve' || setupData.value.bow_type === 'traditional') 
      ? (setupData.value.bow_type === 'traditional' 
        ? getBrandValue('riser_brand', 'custom_trad_riser_brand')
        : getBrandValue('riser_brand', 'custom_riser_brand')) : '',
    riser_model: (setupData.value.bow_type === 'recurve' || setupData.value.bow_type === 'traditional') 
      ? setupData.value.riser_model || '' : '',
    limb_brand: (setupData.value.bow_type === 'recurve' || setupData.value.bow_type === 'traditional')
      ? (setupData.value.bow_type === 'traditional'
        ? getBrandValue('limb_brand', 'custom_trad_limb_brand')
        : getBrandValue('limb_brand', 'custom_limb_brand')) : '',
    limb_model: (setupData.value.bow_type === 'recurve' || setupData.value.bow_type === 'traditional') 
      ? setupData.value.limb_model || '' : '',
  };
  
  emit('save', transformedData);
};
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
</style>
