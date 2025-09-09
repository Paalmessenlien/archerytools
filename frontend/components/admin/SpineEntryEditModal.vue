<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-black bg-opacity-50" @click="cancel"></div>
      
      <!-- Modal -->
      <div class="inline-block w-full max-w-md p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-xl rounded-lg">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            <i class="fas fa-edit mr-2"></i>
            {{ isEdit ? 'Edit Spine Entry' : 'Add Spine Entry' }}
          </h3>
          <CustomButton
            @click="cancel"
            variant="text"
            size="small"
            class="text-gray-400 hover:text-gray-600"
          >
            <i class="fas fa-times"></i>
          </CustomButton>
        </div>
        
        <!-- Edit Form -->
        <form @submit.prevent="save" class="space-y-4">
          <!-- Draw Weight Range -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Draw Weight (lbs) *
            </label>
            <input
              v-model="formData.draw_weight_range_lbs"
              type="text"
              required
              placeholder="e.g., 40-50 or 45"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              :class="{ 'border-red-500': errors.draw_weight_range_lbs }"
            />
            <p v-if="errors.draw_weight_range_lbs" class="text-xs text-red-600 dark:text-red-400 mt-1">
              {{ errors.draw_weight_range_lbs }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Enter a single weight (e.g., "45") or range (e.g., "40-50")
            </p>
          </div>

          <!-- Arrow Length -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Arrow Length (inches) *
            </label>
            <input
              v-model.number="formData.arrow_length_in"
              type="number"
              required
              step="0.25"
              min="20"
              max="36"
              placeholder="28"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              :class="{ 'border-red-500': errors.arrow_length_in }"
            />
            <p v-if="errors.arrow_length_in" class="text-xs text-red-600 dark:text-red-400 mt-1">
              {{ errors.arrow_length_in }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Typical range: 20-36 inches
            </p>
          </div>

          <!-- Recommended Spine -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Recommended Spine *
            </label>
            <input
              v-model="formData.spine"
              type="text"
              required
              placeholder="e.g., 400, 350-400, or 35-40 lbs"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              :class="{ 'border-red-500': errors.spine }"
            />
            <p v-if="errors.spine" class="text-xs text-red-600 dark:text-red-400 mt-1">
              {{ errors.spine }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Standard deflection (e.g., 400), range (350-400), or wood spine in lbs
            </p>
          </div>

          <!-- Arrow Size (Optional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Arrow Size (optional)
            </label>
            <input
              v-model="formData.arrow_size"
              type="text"
              placeholder="e.g., 2314, 27/64, or 5/16"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Standard sizes like 2314, diameter fractions, or manufacturer codes
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-600">
            <CustomButton
              @click="cancel"
              type="button"
              variant="outlined"
              class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700"
            >
              Cancel
            </CustomButton>
            <CustomButton
              type="submit"
              :disabled="!isFormValid || saving"
              variant="filled"
              class="bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              <i v-if="saving" class="fas fa-spinner fa-spin mr-2"></i>
              <i v-else class="fas fa-save mr-2"></i>
              {{ saving ? 'Saving...' : (isEdit ? 'Save Changes' : 'Add Entry') }}
            </CustomButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface SpineGridEntry {
  draw_weight_range_lbs: string | number
  arrow_length_in: number
  spine: string
  arrow_size?: string
}

interface Props {
  show: boolean
  entry?: SpineGridEntry | null
  isEdit?: boolean
}

interface Emits {
  save: [entry: SpineGridEntry]
  cancel: []
}

const props = withDefaults(defineProps<Props>(), {
  entry: null,
  isEdit: false
})

const emit = defineEmits<Emits>()

// Form data
const formData = reactive<SpineGridEntry>({
  draw_weight_range_lbs: '',
  arrow_length_in: 28,
  spine: '',
  arrow_size: ''
})

// Form state
const saving = ref(false)
const errors = reactive<Record<string, string>>({})

// Computed
const isFormValid = computed(() => {
  return formData.draw_weight_range_lbs && 
         formData.arrow_length_in && 
         formData.spine &&
         Object.keys(errors).length === 0
})

// Methods
const resetForm = () => {
  formData.draw_weight_range_lbs = ''
  formData.arrow_length_in = 28
  formData.spine = ''
  formData.arrow_size = ''
  Object.keys(errors).forEach(key => delete errors[key])
}

const loadEntry = (entry: SpineGridEntry | null) => {
  if (entry) {
    formData.draw_weight_range_lbs = entry.draw_weight_range_lbs
    formData.arrow_length_in = entry.arrow_length_in
    formData.spine = entry.spine
    formData.arrow_size = entry.arrow_size || ''
  } else {
    resetForm()
  }
}

const validateForm = () => {
  Object.keys(errors).forEach(key => delete errors[key])

  // Validate draw weight range
  if (!formData.draw_weight_range_lbs) {
    errors.draw_weight_range_lbs = 'Draw weight is required'
  } else {
    const weightStr = formData.draw_weight_range_lbs.toString()
    // Check if it's a valid single number or range
    if (!/^(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)$/.test(weightStr.trim())) {
      errors.draw_weight_range_lbs = 'Invalid format. Use a number (e.g., 45) or range (e.g., 40-50)'
    }
  }

  // Validate arrow length
  if (!formData.arrow_length_in) {
    errors.arrow_length_in = 'Arrow length is required'
  } else if (formData.arrow_length_in < 20 || formData.arrow_length_in > 36) {
    errors.arrow_length_in = 'Arrow length must be between 20 and 36 inches'
  }

  // Validate spine
  if (!formData.spine) {
    errors.spine = 'Spine value is required'
  }

  return Object.keys(errors).length === 0
}

const save = async () => {
  if (!validateForm()) return

  saving.value = true

  try {
    // Emit the form data
    emit('save', { ...formData })
    
    // Reset form after successful save
    if (!props.isEdit) {
      resetForm()
    }
  } catch (err) {
    console.error('Error saving spine entry:', err)
  } finally {
    saving.value = false
  }
}

const cancel = () => {
  resetForm()
  emit('cancel')
}

// Watch for entry changes
watch(() => props.entry, (newEntry) => {
  loadEntry(newEntry)
}, { immediate: true })

// Watch for show changes
watch(() => props.show, (show) => {
  if (show) {
    loadEntry(props.entry)
  } else {
    // Clear errors when modal is hidden
    Object.keys(errors).forEach(key => delete errors[key])
  }
})
</script>

<style scoped>
/* Modal backdrop styling */
.fixed.inset-0 {
  backdrop-filter: blur(2px);
}

/* Form input focus styling */
input:focus {
  @apply ring-2 ring-blue-500 ring-opacity-50;
}

.dark input:focus {
  @apply ring-purple-500 ring-opacity-50;
}

/* Error state styling */
input.border-red-500:focus {
  @apply ring-red-500 ring-opacity-50;
}
</style>