<template>
  <div class="card p-6 max-w-md mx-auto">
    <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Complete Your Profile</h2>
    <p class="text-gray-700 dark:text-gray-300 mb-4">
      Please provide your full name to complete your registration.
    </p>

    <form @submit.prevent="submitName">
      <div class="mb-4">
        <label for="fullName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Full Name
        </label>
        <input
          type="text"
          id="fullName"
          v-model="fullName"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          required
        />
      </div>

      <CustomButton
        type="submit"
        variant="filled"
        :disabled="isSubmitting"
        class="w-full bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
      >
        <span v-if="isSubmitting">Saving...</span>
        <span v-else>Save Name</span>
      </CustomButton>

      <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/useAuth';

const router = useRouter();
const { user, updateUserProfile, fetchUser } = useAuth();

const fullName = ref('');

onMounted(() => {
  if (user.value) {
    fullName.value = user.value.name || '';
  }
});

watch(user, (newUser) => {
  if (newUser) {
    fullName.value = newUser.name || '';
  }
});
const isSubmitting = ref(false);
const error = ref(null);

const submitName = async () => {
  isSubmitting.value = true;
  error.value = null;

  try {
    await updateUserProfile(fullName.value);
    await fetchUser(); // Ensure local user state is updated
    router.push('/my-page'); // Redirect to My Page after successful update
  } catch (err) {
    console.error('Error submitting name:', err);
    error.value = err.message || 'Failed to save name. Please try again.';
  } finally {
    isSubmitting.value = false;
  }
};

// Ensure user data is fetched on page load if not already present
onMounted(() => {
  if (!user.value) {
    fetchUser();
  }
});
</script>

<style scoped>
/* Add any specific styles for this page here if needed */
</style>