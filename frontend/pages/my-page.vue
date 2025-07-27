<template>
  <div class="card p-6">
    <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">My Page</h2>

    <div v-if="user">
      <p class="text-gray-700 dark:text-gray-300 mb-2">
        Welcome, <span class="font-medium">{{ user.name || user.email }}</span>!
      </p>
      <p v-if="user.email" class="text-gray-600 dark:text-gray-400 mb-4">
        Email: {{ user.email }}
      </p>
      <div class="flex space-x-4">
        <CustomButton
          @click="openEditModal"
          variant="filled"
          class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
        >
          Edit Profile
        </CustomButton>
        <CustomButton
          @click="logout"
          variant="outlined"
          class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900"
        >
          Logout
        </CustomButton>
      </div>

      <!-- Edit Profile Modal -->
      <div v-if="isEditing" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Edit Profile</h3>
          <form @submit.prevent="saveProfile">
            <div class="mb-4">
              <label for="editedName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Full Name
              </label>
              <input
                type="text"
                id="editedName"
                v-model="editedName"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                required
              />
            </div>
            <div class="flex justify-end space-x-3">
              <CustomButton
                type="button"
                @click="closeEditModal"
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
            <p v-if="editError" class="text-red-500 text-sm mt-3">{{ editError }}</p>
          </form>
        </div>
      </div>
    </div>
    <div v-else>
      <p class="text-gray-700 dark:text-gray-300 mb-4">
        You are not logged in. Please log in to view your profile.
      </p>
      <CustomButton
        @click="loginWithGoogle"
        variant="filled"
        class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
      >
        Login with Google
      </CustomButton>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuth } from '~/composables/useAuth';

const { user, logout, loginWithGoogle, updateUserProfile, fetchUser } = useAuth();

const isEditing = ref(false);
const editedName = ref('');
const isSaving = ref(false);
const editError = ref(null);

const openEditModal = () => {
  editedName.value = user.value?.name || '';
  isEditing.value = true;
  editError.value = null;
};

const closeEditModal = () => {
  isEditing.value = false;
};

const saveProfile = async () => {
  isSaving.value = true;
  editError.value = null;
  try {
    await updateUserProfile(editedName.value);
    closeEditModal();
  } catch (err) {
    console.error('Error saving profile:', err);
    editError.value = err.message || 'Failed to save profile.';
  } finally {
    isSaving.value = false;
  }
};

// Ensure user data is fetched on page load if not already present
// This is important for direct access to /my-page
onMounted(() => {
  // Ensure user data is fetched on page load if not already present
  if (!user.value) {
    fetchUser();
  }
});

// Watch for changes in the user object and update editedName accordingly
watch(user, (newUser) => {
  if (newUser) {
    editedName.value = newUser.name || '';
  }
}, { immediate: true });

definePageMeta({
  middleware: ['auth-check']
});
</script>