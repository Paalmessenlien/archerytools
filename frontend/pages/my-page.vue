<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">My Profile</h1>
    
    <div v-if="isLoadingUser" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
      <p class="text-gray-700 dark:text-gray-300">Loading...</p>
    </div>

    <div v-else-if="user">
      <div>
        <p class="text-gray-700 dark:text-gray-300 mb-2">
          Welcome, <span class="font-medium">{{ user.name || user.email }}</span>!
        </p>
        <p v-if="user.email" class="text-gray-600 dark:text-gray-400 mb-4">
          Email: {{ user.email }}
        </p>
        <div class="flex space-x-4 mb-8">
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

        <!-- Bow Setups Section -->
        <div class="mt-8">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">My Bow Setups</h3>

          <div v-if="isLoadingSetups" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
            <p class="text-gray-700 dark:text-gray-300">Loading bow setups...</p>
          </div>

          <div v-else>
            <div v-if="bowSetups.length > 0" class="space-y-4 mb-6">
              <div v-for="setup in bowSetups" :key="setup.id" class="card p-4 border border-gray-200 dark:border-gray-700">
                <div class="flex justify-between items-center mb-2">
                  <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ setup.name }} ({{ setup.bow_type }})</h4>
                  <CustomButton
                    @click="confirmDeleteSetup(setup.id)"
                    variant="text"
                    class="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900 p-1"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                  </CustomButton>
                </div>
                <p class="text-sm text-gray-700 dark:text-gray-300">Draw Weight: {{ setup.draw_weight }} lbs, Draw Length: {{ setup.draw_length }} "</p>
                <p v-if="setup.description" class="text-sm text-gray-600 dark:text-gray-400 mt-2">{{ setup.description }}</p>
              </div>
            </div>
            <p v-else class="text-gray-600 dark:text-gray-400 mb-4">No bow setups added yet.</p>

            <CustomButton
              @click="openAddSetupModal"
              variant="outlined"
              class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-purple-400 dark:border-purple-400 dark:hover:bg-purple-900"
            >
              Add New Bow Setup
            </CustomButton>
          </div>
        </div>

        <!-- Add/Edit Bow Setup Modal -->
        <div v-if="isAddingSetup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-lg shadow-lg">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Add New Bow Setup</h3>
            <form @submit.prevent="saveBowSetup">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="mb-4">
                  <label for="setupName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Setup Name</label>
                  <input type="text" id="setupName" v-model="newSetup.name" class="form-input" required />
                </div>
                <div class="mb-4">
                  <label for="bowType" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bow Type</label>
                  <select id="bowType" v-model="newSetup.bow_type" class="form-select" required>
                    <option value="">Select Bow Type</option>
                    <option value="compound">Compound</option>
                    <option value="recurve">Recurve</option>
                    <option value="longbow">Longbow</option>
                    <option value="traditional">Traditional</option>
                  </select>
                </div>
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Draw Weight: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ newSetup.draw_weight || 45 }} lbs</span>
                  </label>
                  <md-slider
                    ref="drawWeightSlider"
                    min="20"
                    max="80"
                    :value="newSetup.draw_weight || 45"
                    @input="newSetup.draw_weight = parseInt($event.target.value)"
                    labeled
                    ticks
                    class="w-full"
                  ></md-slider>
                  <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                    <span>20 lbs</span>
                    <span>80 lbs</span>
                  </div>
                </div>
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Draw Length: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ newSetup.draw_length || 28 }}"</span>
                  </label>
                  <md-slider
                    ref="drawLengthSlider"
                    min="24"
                    max="34"
                    step="0.25"
                    :value="newSetup.draw_length || 28"
                    @input="newSetup.draw_length = parseFloat($event.target.value)"
                    labeled
                    ticks
                    class="w-full"
                  ></md-slider>
                  <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                    <span>24"</span>
                    <span>34"</span>
                  </div>
                </div>
              </div>
              <div class="mb-4">
                <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description (optional)</label>
                <textarea id="description" v-model="newSetup.description" class="form-textarea"></textarea>
              </div>

              <div class="flex justify-end space-x-3">
                <CustomButton
                  type="button"
                  @click="closeAddSetupModal"
                  variant="outlined"
                  class="text-gray-700 dark:text-gray-200"
                >
                  Cancel
                </CustomButton>
                <CustomButton
                  type="submit"
                  variant="filled"
                  :disabled="isSavingSetup"
                  class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
                >
                  <span v-if="isSavingSetup">Saving...</span>
                  <span v-else>Add Setup</span>
                </CustomButton>
              </div>
              <p v-if="addSetupError" class="text-red-500 text-sm mt-3">{{ addSetupError }}</p>
            </form>
          </div>
        </div>

        <!-- Confirm Delete Modal -->
        <div v-if="isConfirmingDelete" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-lg text-center">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Confirm Deletion</h3>
            <p class="text-gray-700 dark:text-gray-300 mb-6">Are you sure you want to delete this bow setup?</p>
            <div class="flex justify-center space-x-4">
              <CustomButton
                @click="cancelDeleteSetup"
                variant="outlined"
                class="text-gray-700 dark:text-gray-200"
              >
                Cancel
              </CustomButton>
              <CustomButton
                @click="deleteSetup"
                variant="filled"
                class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
              >
                Delete
              </CustomButton>
            </div>
            <p v-if="deleteSetupError" class="text-red-500 text-sm mt-3">{{ deleteSetupError }}</p>
          </div>
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
import { ref, onMounted, watch } from 'vue';
import { useAuth } from '~/composables/useAuth';

const { user, logout, loginWithGoogle, updateUserProfile, fetchUser, fetchBowSetups, addBowSetup, deleteBowSetup } = useAuth();

const isLoadingUser = ref(true);
const isEditing = ref(false);
const editedName = ref('');
const isSaving = ref(false);
const editError = ref(null);

const bowSetups = ref([]);
const isLoadingSetups = ref(true);
const isAddingSetup = ref(false);
const isSavingSetup = ref(false);
const addSetupError = ref(null);
const isConfirmingDelete = ref(false);
const setupToDeleteId = ref(null);
const deleteSetupError = ref(null);

const newSetup = ref({
  name: '',
  bow_type: '',
  draw_weight: 45,
  draw_length: 28,
  description: '',
});

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

const loadBowSetups = async () => {
  isLoadingSetups.value = true;
  try {
    bowSetups.value = await fetchBowSetups();
  } catch (err) {
    console.error('Error loading bow setups:', err);
    // Optionally display an error message to the user
  } finally {
    isLoadingSetups.value = false;
  }
};

const openAddSetupModal = () => {
  // Reset form for new entry
  newSetup.value = {
    name: '',
    bow_type: '',
    draw_weight: 45,
    draw_length: 28,
    description: '',
  };
  addSetupError.value = null;
  isAddingSetup.value = true;
};

const closeAddSetupModal = () => {
  isAddingSetup.value = false;
};

const saveBowSetup = async () => {
  isSavingSetup.value = true;
  addSetupError.value = null;
  try {
    await addBowSetup(newSetup.value);
    closeAddSetupModal();
    await loadBowSetups(); // Reload setups after adding
  } catch (err) {
    console.error('Error saving bow setup:', err);
    addSetupError.value = err.message || 'Failed to add bow setup.';
  } finally {
    isSavingSetup.value = false;
  }
};

const confirmDeleteSetup = (id) => {
  setupToDeleteId.value = id;
  deleteSetupError.value = null;
  isConfirmingDelete.value = true;
};

const cancelDeleteSetup = () => {
  setupToDeleteId.value = null;
  isConfirmingDelete.value = false;
};

const deleteSetup = async () => {
  if (!setupToDeleteId.value) return;

  isSavingSetup.value = true; // Use this for delete loading state too
  deleteSetupError.value = null;
  try {
    await deleteBowSetup(setupToDeleteId.value);
    cancelDeleteSetup();
    await loadBowSetups(); // Reload setups after deleting
  } catch (err) {
    console.error('Error deleting bow setup:', err);
    deleteSetupError.value = err.message || 'Failed to delete bow setup.';
  } finally {
    isSavingSetup.value = false;
  }
};

onMounted(async () => {
  // Ensure user data is fetched on page load
  if (!user.value) {
    await fetchUser();
  }
  isLoadingUser.value = false;
  
  // Load bow setups only if user is logged in
  if (user.value) {
    await loadBowSetups();
  }
});

// Watch for changes in the user object and update editedName accordingly
watch(user, async (newUser) => {
  if (newUser) {
    editedName.value = newUser.name || '';
    // If user just logged in or user object changed, reload bow setups
    await loadBowSetups();
  }
}, { immediate: true });

definePageMeta({
  middleware: ['auth-check']
});
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