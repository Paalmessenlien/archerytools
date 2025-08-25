<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl shadow-lg max-h-screen overflow-y-auto">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Edit Archer Profile</h3>
      <form @submit.prevent="saveProfile">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Basic Information -->
            <div class="mb-4">
              <label for="editedName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Full Name
              </label>
              <input
                type="text"
                id="editedName"
                v-model="editedName"
                class="form-input w-full"
                required
              />
            </div>

            <!-- Skill Level -->
            <div class="mb-4">
              <label for="skillLevel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Skill Level
              </label>
              <select id="skillLevel" v-model="editedSkillLevel" class="form-select w-full" required>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <!-- Draw Length -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Draw Length: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ editedDrawLength }}"</span>
              </label>
              <md-slider
                min="20"
                max="36"
                step="0.25"
                :value="editedDrawLength"
                @input="editedDrawLength = parseFloat($event.target.value)"
                labeled
                ticks
                class="w-full mobile-slider-safe"
              ></md-slider>
              <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                <span>20"</span>
                <span>36"</span>
              </div>
            </div>

            <!-- Shooting Styles (Multiple Selection) -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Shooting Styles (select all that apply)
              </label>
              <div class="space-y-2">
                <label v-for="style in shootingStyleOptions" :key="style.value" class="flex items-center">
                  <input
                    type="checkbox"
                    :value="style.value"
                    v-model="editedShootingStyles"
                    class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                  >
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ style.label }}</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Preferred Manufacturers -->
          <div class="mb-4">
            <label for="preferredManufacturers" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Preferred Arrow Manufacturers (comma-separated)
            </label>
            <input
              type="text"
              id="preferredManufacturers"
              v-model="editedPreferredManufacturers"
              class="form-input w-full"
              placeholder="e.g., Easton, Gold Tip, Victory"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Enter manufacturer names separated by commas
            </p>
          </div>

          <!-- Notes -->
          <div class="mb-6">
            <label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Notes
            </label>
            <textarea
              id="notes"
              v-model="editedNotes"
              class="form-textarea w-full"
              rows="3"
              placeholder="Additional notes about your archery preferences, goals, etc."
            ></textarea>
          </div>

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
              type="submit"
              variant="filled"
              :disabled="isSaving"
              class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
            >
              <span v-if="isSaving">Saving...</span>
              <span v-else>Save Changes</span>
            </CustomButton>
          </div>
          <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
        </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  user: {
    type: Object,
    default: null
  },
  isSaving: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['close', 'save']);

// Form data
const editedName = ref('');
const editedDrawLength = ref(28.0);
const editedSkillLevel = ref('intermediate');
const editedShootingStyles = ref([]);
const editedPreferredManufacturers = ref('');
const editedNotes = ref('');

// Shooting style options
const shootingStyleOptions = [
  { value: 'target', label: 'Target Archery' },
  { value: 'hunting', label: 'Hunting' },
  { value: 'traditional', label: 'Traditional' },
  { value: '3d', label: '3D Archery' }
];

// Watch for user prop changes and update form data
watch(() => props.user, (newUser) => {
  if (newUser) {
    editedName.value = newUser.name || '';
    editedDrawLength.value = newUser.draw_length || 28.0;
    editedSkillLevel.value = newUser.skill_level || 'intermediate';
    editedShootingStyles.value = newUser.shooting_style || ['target'];
    editedPreferredManufacturers.value = (newUser.preferred_manufacturers || []).join(', ');
    editedNotes.value = newUser.notes || '';
  }
}, { immediate: true });

// Watch for modal open state and reset form
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && props.user) {
    editedName.value = props.user.name || '';
    editedDrawLength.value = props.user.draw_length || 28.0;
    editedSkillLevel.value = props.user.skill_level || 'intermediate';
    editedShootingStyles.value = props.user.shooting_style || ['target'];
    editedPreferredManufacturers.value = (props.user.preferred_manufacturers || []).join(', ');
    editedNotes.value = props.user.notes || '';
  }
});

const closeModal = () => {
  emit('close');
};

const saveProfile = async () => {
  // Parse preferred manufacturers from comma-separated string
  const preferredManufacturers = editedPreferredManufacturers.value
    .split(',')
    .map(brand => brand.trim())
    .filter(brand => brand.length > 0);
  
  const profileData = {
    name: editedName.value,
    draw_length: editedDrawLength.value,
    skill_level: editedSkillLevel.value,
    shooting_style: editedShootingStyles.value,
    preferred_manufacturers: preferredManufacturers,
    notes: editedNotes.value
  };

  emit('save', profileData);
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