<template>
  <div class="card p-6 max-w-2xl mx-auto">
    <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Complete Your Archer Profile</h2>
    <p class="text-gray-700 dark:text-gray-300 mb-6">
      Please provide your information to create a complete archer profile for better arrow recommendations.
    </p>

    <form @submit.prevent="submitProfile">
      <!-- Personal Information -->
      <div class="mb-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Personal Information</h3>
        
        <div class="mb-4">
          <label for="fullName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Full Name *
          </label>
          <md-outlined-text-field
            id="fullName"
            :value="profileData.name"
            @input="profileData.name = $event.target.value"
            label="Full Name"
            required
            class="w-full"
          ></md-outlined-text-field>
        </div>
      </div>

      <!-- Archery Information -->
      <div class="mb-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Archery Information</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <!-- Draw Length -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Draw Length: <span class="font-semibold text-blue-600">{{ profileData.draw_length }}"</span>
            </label>
            <md-slider
              min="20"
              max="36"
              step="0.25"
              :value="profileData.draw_length"
              @input="profileData.draw_length = parseFloat($event.target.value)"
              labeled
              ticks
              class="w-full"
            ></md-slider>
          </div>

          <!-- Skill Level -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Skill Level
            </label>
            <md-filled-select :value="profileData.skill_level" @change="profileData.skill_level = $event.target.value" label="Skill Level" class="w-full">
              <md-select-option value="beginner">
                <div slot="headline">Beginner</div>
              </md-select-option>
              <md-select-option value="intermediate">
                <div slot="headline">Intermediate</div>
              </md-select-option>
              <md-select-option value="advanced">
                <div slot="headline">Advanced</div>
              </md-select-option>
            </md-filled-select>
          </div>
        </div>

        <!-- Shooting Style -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Primary Shooting Style
          </label>
          <md-filled-select :value="profileData.shooting_style" @change="profileData.shooting_style = $event.target.value" label="Shooting Style" class="w-full">
            <md-select-option value="target">
              <div slot="headline">Target Archery</div>
            </md-select-option>
            <md-select-option value="hunting">
              <div slot="headline">Hunting</div>
            </md-select-option>
            <md-select-option value="3d">
              <div slot="headline">3D Archery</div>
            </md-select-option>
            <md-select-option value="traditional">
              <div slot="headline">Traditional</div>
            </md-select-option>
          </md-filled-select>
        </div>

        <!-- Preferred Manufacturers -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Preferred Arrow Manufacturers (Optional)
          </label>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
            <label v-for="manufacturer in popularManufacturers" :key="manufacturer" 
                   class="flex items-center space-x-2 p-2 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
              <input 
                type="checkbox" 
                :value="manufacturer"
                v-model="profileData.preferred_manufacturers"
                class="text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ manufacturer }}</span>
            </label>
          </div>
        </div>

        <!-- Notes -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Additional Notes (Optional)
          </label>
          <md-outlined-text-field
            :value="profileData.notes"
            @input="profileData.notes = $event.target.value"
            label="Any additional information about your archery preferences..."
            type="textarea"
            rows="3"
            class="w-full"
          ></md-outlined-text-field>
        </div>
      </div>

      <CustomButton
        type="submit"
        variant="filled"
        :disabled="isSubmitting"
        class="w-full bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
      >
        <span v-if="isSubmitting">
          <i class="fas fa-spinner fa-spin mr-2"></i>
          Creating Profile...
        </span>
        <span v-else>
          <i class="fas fa-user-check mr-2"></i>
          Complete Registration
        </span>
      </CustomButton>

      <p v-if="error" class="text-red-500 text-sm mt-3">
        <i class="fas fa-exclamation-triangle mr-1"></i>
        {{ error }}
      </p>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/useAuth';

const router = useRouter();
const { user, updateUserProfile, fetchUser } = useAuth();

// Popular arrow manufacturers for selection
const popularManufacturers = [
  'Easton', 'Gold Tip', 'Victory', 'Carbon Express', 
  'Bloodsport', 'Black Eagle', 'Beman', 'PSE', 
  'Bear Archery', 'Fivics', 'Skylon', 'Cross-X'
];

// Comprehensive profile data
const profileData = ref({
  name: '',
  draw_length: 28.0,
  skill_level: 'intermediate',
  shooting_style: 'target',
  preferred_manufacturers: [],
  notes: ''
});

const isSubmitting = ref(false);
const error = ref(null);

// Initialize form with existing user data
const initializeForm = () => {
  if (user.value) {
    profileData.value = {
      name: user.value.name || '',
      draw_length: user.value.draw_length || 28.0,
      skill_level: user.value.skill_level || 'intermediate',
      shooting_style: user.value.shooting_style || 'target',
      preferred_manufacturers: user.value.preferred_manufacturers || [],
      notes: user.value.notes || ''
    };
  }
};

// Watch for user data changes
watch(user, (newUser) => {
  if (newUser) {
    initializeForm();
  }
}, { immediate: true });

const submitProfile = async () => {
  isSubmitting.value = true;
  error.value = null;

  try {
    // Pass the entire profile data object (not just a string)
    await updateUserProfile(profileData.value);
    await fetchUser(); // Ensure local user state is updated
    router.push('/my-page'); // Redirect to My Setup after successful update
  } catch (err) {
    console.error('Error submitting profile:', err);
    error.value = err.message || 'Failed to save profile. Please try again.';
  } finally {
    isSubmitting.value = false;
  }
};

// Ensure user data is fetched on page load if not already present
onMounted(() => {
  if (!user.value) {
    fetchUser().then(() => {
      initializeForm();
    });
  } else {
    initializeForm();
  }
});
</script>

<style scoped>
/* Add any specific styles for this page here if needed */
</style>