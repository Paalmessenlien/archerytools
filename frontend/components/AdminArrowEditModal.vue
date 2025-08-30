<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl">
      <!-- Modal Header -->
      <div class="bg-gray-50 dark:bg-gray-700 px-6 py-4 border-b border-gray-200 dark:border-gray-600">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            <i class="fas fa-edit mr-2 text-indigo-600"></i>
            {{ isCreating ? 'Create New Arrow' : 'Edit Arrow' }}
          </h2>
          <CustomButton
            @click="closeModal"
            variant="text"
            size="small"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <i class="fas fa-times text-lg"></i>
          </CustomButton>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="overflow-y-auto max-h-[calc(90vh-140px)]">
        <form @submit.prevent="saveArrow" class="p-6 space-y-6">
          <!-- Basic Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Manufacturer *
              </label>
              <input
                v-model="formData.manufacturer"
                type="text"
                required
                class="form-input w-full"
                placeholder="Easton Archery"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Model Name *
              </label>
              <input
                v-model="formData.model_name"
                type="text"
                required
                class="form-input w-full"
                placeholder="X10 Protour"
              />
            </div>
          </div>

          <!-- Material and Type -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Material
              </label>
              <select v-model="formData.material" class="form-select w-full">
                <option value="">Select Material</option>
                <option value="Carbon">Carbon</option>
                <option value="Aluminum">Aluminum</option>
                <option value="Carbon / Aluminum">Carbon / Aluminum</option>
                <option value="Wood">Wood</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Arrow Type
              </label>
              <select v-model="formData.arrow_type" class="form-select w-full">
                <option value="">Select Type</option>
                <option value="hunting">Hunting</option>
                <option value="target">Target</option>
                <option value="indoor">Indoor</option>
                <option value="outdoor">Outdoor</option>
                <option value="3d">3D</option>
                <option value="recreational">Recreational</option>
              </select>
            </div>
          </div>

          <!-- Additional Fields -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Carbon Content
              </label>
              <input
                v-model="formData.carbon_content"
                type="text"
                class="form-input w-full"
                placeholder="100%"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Primary Image URL
              </label>
              <input
                v-model="formData.primary_image_url"
                type="url"
                class="form-input w-full"
                placeholder="https://example.com/image.jpg"
              />
            </div>
          </div>

          <!-- Tolerances -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Straightness Tolerance
              </label>
              <input
                v-model="formData.straightness_tolerance"
                type="text"
                class="form-input w-full"
                placeholder="±0.003"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Weight Tolerance
              </label>
              <input
                v-model="formData.weight_tolerance"
                type="text"
                class="form-input w-full"
                placeholder="±1.0 grain"
              />
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <textarea
              v-model="formData.description"
              class="form-textarea w-full h-24 resize-y"
              placeholder="Professional grade target arrow with excellent accuracy and consistency..."
            ></textarea>
          </div>

          <!-- Recommended Use -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Recommended Use (comma-separated)
            </label>
            <input
              v-model="formData.recommended_use"
              type="text"
              class="form-input w-full"
              placeholder="target, indoor competition, outdoor competition"
            />
          </div>

          <!-- Spine Specifications -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Spine Specifications *
              </label>
              <CustomButton
                type="button"
                @click="addSpineSpecification"
                variant="outlined"
                size="small"
                class="text-green-600 border-green-600 hover:bg-green-50 dark:hover:bg-green-900/20"
              >
                <i class="fas fa-plus mr-1"></i>
                Add Spine
              </CustomButton>
            </div>

            <div class="space-y-4">
              <div
                v-for="(spec, index) in formData.spine_specifications"
                :key="index"
                class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50"
              >
                <div class="flex items-center justify-between mb-3">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Spine Specification {{ index + 1 }}
                  </span>
                  <CustomButton
                    type="button"
                    @click="removeSpineSpecification(index)"
                    variant="text"
                    size="small"
                    class="text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    <i class="fas fa-trash"></i>
                  </CustomButton>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Spine *
                    </label>
                    <input
                      v-model.number="spec.spine"
                      type="number"
                      required
                      min="100"
                      max="1200"
                      class="form-input w-full"
                      placeholder="350"
                    />
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Outer Diameter (inches) *
                    </label>
                    <input
                      v-model.number="spec.outer_diameter"
                      type="number"
                      step="0.001"
                      required
                      min="0.100"
                      max="0.500"
                      class="form-input w-full"
                      placeholder="0.246"
                    />
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                      GPI Weight *
                    </label>
                    <input
                      v-model.number="spec.gpi_weight"
                      type="number"
                      step="0.1"
                      required
                      min="1"
                      max="25"
                      class="form-input w-full"
                      placeholder="9.5"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div>
                    <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Inner Diameter (inches)
                    </label>
                    <input
                      v-model.number="spec.inner_diameter"
                      type="number"
                      step="0.001"
                      min="0.050"
                      max="0.400"
                      class="form-input w-full"
                      placeholder="0.204"
                    />
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Length Options (comma-separated)
                    </label>
                    <input
                      v-model="spec.length_options_text"
                      type="text"
                      class="form-input w-full"
                      placeholder="27, 28, 29, 30, 31, 32"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div v-if="formData.spine_specifications.length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400">
              No spine specifications added. Click "Add Spine" to add one.
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div class="flex items-center">
              <i class="fas fa-exclamation-circle text-red-600 dark:text-red-400 mr-3"></i>
              <span class="text-red-800 dark:text-red-200">{{ errorMessage }}</span>
            </div>
          </div>
        </form>
      </div>

      <!-- Modal Footer -->
      <div class="bg-gray-50 dark:bg-gray-700 px-6 py-4 border-t border-gray-200 dark:border-gray-600">
        <div class="flex justify-end space-x-3">
          <CustomButton
            type="button"
            @click="closeModal"
            variant="outlined"
            class="text-gray-700 dark:text-gray-200"
          >
            Cancel
          </CustomButton>
          <CustomButton
            @click="saveArrow"
            variant="filled"
            :disabled="isLoading"
            class="bg-indigo-600 text-white hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-800"
          >
            <span v-if="isLoading">
              <i class="fas fa-spinner fa-spin mr-2"></i>
              {{ isCreating ? 'Creating...' : 'Updating...' }}
            </span>
            <span v-else>
              <i class="fas fa-save mr-2"></i>
              {{ isCreating ? 'Create Arrow' : 'Update Arrow' }}
            </span>
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface SpineSpecification {
  spine: number;
  outer_diameter: number;
  gpi_weight: number;
  inner_diameter?: number;
  length_options?: number[];
  length_options_text?: string;
}

interface ArrowFormData {
  manufacturer: string;
  model_name: string;
  material?: string;
  arrow_type?: string;
  description?: string;
  primary_image_url?: string;
  recommended_use?: string;
  straightness_tolerance?: string;
  weight_tolerance?: string;
  carbon_content?: string;
  spine_specifications: SpineSpecification[];
}

interface Props {
  isOpen: boolean;
  arrow?: any;
  isCreating?: boolean;
}

interface Emits {
  (e: 'close'): void;
  (e: 'save', arrow: any): void;
}

const props = withDefaults(defineProps<Props>(), {
  isCreating: false
});

const emit = defineEmits<Emits>();

// State
const isLoading = ref(false);
const errorMessage = ref('');

// Form data
const formData = ref<ArrowFormData>({
  manufacturer: '',
  model_name: '',
  material: '',
  arrow_type: '',
  description: '',
  primary_image_url: '',
  recommended_use: '',
  straightness_tolerance: '',
  weight_tolerance: '',
  carbon_content: '',
  spine_specifications: []
});

// Initialize form data when arrow prop changes
watch(() => props.arrow, (newArrow) => {
  if (newArrow && props.isOpen) {
    initializeFormData(newArrow);
  }
}, { immediate: true });

// Initialize form when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    errorMessage.value = '';
    if (props.isCreating) {
      resetFormData();
    } else if (props.arrow) {
      initializeFormData(props.arrow);
    }
  }
});

const initializeFormData = (arrow: any) => {
  formData.value = {
    manufacturer: arrow.manufacturer || '',
    model_name: arrow.model_name || '',
    material: arrow.material || '',
    arrow_type: arrow.arrow_type || '',
    description: arrow.description || '',
    primary_image_url: arrow.primary_image_url || '',
    recommended_use: arrow.recommended_use || '',
    straightness_tolerance: arrow.straightness_tolerance || '',
    weight_tolerance: arrow.weight_tolerance || '',
    carbon_content: arrow.carbon_content || '',
    spine_specifications: (arrow.spine_specifications || []).map((spec: any) => ({
      ...spec,
      length_options_text: Array.isArray(spec.length_options) 
        ? spec.length_options.join(', ') 
        : (spec.length_options || '')
    }))
  };
};

const resetFormData = () => {
  formData.value = {
    manufacturer: '',
    model_name: '',
    material: '',
    arrow_type: '',
    description: '',
    primary_image_url: '',
    recommended_use: '',
    straightness_tolerance: '',
    weight_tolerance: '',
    carbon_content: '',
    spine_specifications: [
      {
        spine: 350,
        outer_diameter: 0.246,
        gpi_weight: 9.5,
        length_options_text: '27, 28, 29, 30, 31, 32'
      }
    ]
  };
};

const addSpineSpecification = () => {
  formData.value.spine_specifications.push({
    spine: 350,
    outer_diameter: 0.246,
    gpi_weight: 9.5,
    length_options_text: '27, 28, 29, 30, 31, 32'
  });
};

const removeSpineSpecification = (index: number) => {
  formData.value.spine_specifications.splice(index, 1);
};

const validateForm = (): boolean => {
  errorMessage.value = '';

  if (!formData.value.manufacturer.trim()) {
    errorMessage.value = 'Manufacturer is required';
    return false;
  }

  if (!formData.value.model_name.trim()) {
    errorMessage.value = 'Model name is required';
    return false;
  }

  if (formData.value.spine_specifications.length === 0) {
    errorMessage.value = 'At least one spine specification is required';
    return false;
  }

  for (let i = 0; i < formData.value.spine_specifications.length; i++) {
    const spec = formData.value.spine_specifications[i];
    
    // Different spine validation ranges based on material type
    const isWoodArrow = formData.value.material === 'Wood';
    const minSpine = isWoodArrow ? 25 : 100;  // Wood arrows can have lower spine values (25-120)
    const maxSpine = isWoodArrow ? 120 : 1200; // Carbon/aluminum arrows: 100-1200
    
    if (!spec.spine || spec.spine < minSpine || spec.spine > maxSpine) {
      const spineRange = isWoodArrow ? '25 and 120' : '100 and 1200';
      errorMessage.value = `Spine specification ${i + 1}: Spine value must be between ${spineRange} ${isWoodArrow ? '(wood arrows)' : '(carbon/aluminum arrows)'}`;
      return false;
    }
    // Different outer diameter ranges for different materials  
    const minDiameter = isWoodArrow ? 0.2 : 0.1;   // Wood arrows typically thicker: 0.2-0.6 inches
    const maxDiameter = isWoodArrow ? 0.6 : 0.5;   // Carbon/aluminum: 0.1-0.5 inches
    
    if (!spec.outer_diameter || spec.outer_diameter < minDiameter || spec.outer_diameter > maxDiameter) {
      const diameterRange = isWoodArrow ? '0.2 and 0.6' : '0.1 and 0.5';
      errorMessage.value = `Spine specification ${i + 1}: Outer diameter must be between ${diameterRange} inches ${isWoodArrow ? '(wood arrows)' : '(carbon/aluminum arrows)'}`;
      return false;
    }
    // Different GPI weight ranges for different materials
    const minGPI = isWoodArrow ? 5 : 1;   // Wood arrows typically heavier: 5-35 GPI
    const maxGPI = isWoodArrow ? 35 : 25; // Carbon/aluminum: 1-25 GPI
    
    if (!spec.gpi_weight || spec.gpi_weight < minGPI || spec.gpi_weight > maxGPI) {
      const gpiRange = isWoodArrow ? '5 and 35' : '1 and 25';
      errorMessage.value = `Spine specification ${i + 1}: GPI weight must be between ${gpiRange} ${isWoodArrow ? '(wood arrows)' : '(carbon/aluminum arrows)'}`;
      return false;
    }
  }

  return true;
};

const saveArrow = async () => {
  if (!validateForm()) {
    return;
  }

  try {
    isLoading.value = true;
    errorMessage.value = '';

    // Process spine specifications
    const processedSpecs = formData.value.spine_specifications.map(spec => ({
      ...spec,
      length_options: spec.length_options_text 
        ? spec.length_options_text.split(',').map(l => parseFloat(l.trim())).filter(l => !isNaN(l))
        : []
    }));

    const arrowData = {
      ...formData.value,
      spine_specifications: processedSpecs
    };

    // Remove text fields used only for display
    arrowData.spine_specifications.forEach(spec => {
      delete (spec as any).length_options_text;
    });

    emit('save', arrowData);
  } catch (error) {
    console.error('Error saving arrow:', error);
    errorMessage.value = 'Failed to save arrow. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

const closeModal = () => {
  if (!isLoading.value) {
    emit('close');
  }
};
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:focus:ring-indigo-400 dark:focus:border-indigo-400;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  @apply ring-2 ring-indigo-500 ring-opacity-50 dark:ring-indigo-400;
}
</style>