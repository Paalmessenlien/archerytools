<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">My Profile</h1>
    
    <div v-if="isLoadingUser" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
      <p class="text-gray-700 dark:text-gray-300">Loading...</p>
    </div>

    <div v-else-if="user">
      <!-- Archer Profile Section -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Archer Profile</h2>
          <div class="flex space-x-3">
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
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Basic Info -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Basic Information</h3>
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Name:</span>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ user.name || 'Not set' }}</p>
              </div>
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Email:</span>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ user.email }}</p>
              </div>
            </div>
          </div>

          <!-- Archer Specifications -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Physical Specifications</h3>
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Draw Length:</span>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ user.draw_length || 28.0 }}"</p>
              </div>
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Skill Level:</span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getSkillLevelClass(user.skill_level)">
                  {{ formatSkillLevel(user.skill_level) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Shooting Preferences -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Shooting Preferences</h3>
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Primary Style:</span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getShootingStyleClass(user.shooting_style)">
                  {{ formatShootingStyle(user.shooting_style) }}
                </span>
              </div>
              <div v-if="user.preferred_manufacturers && user.preferred_manufacturers.length > 0">
                <span class="text-sm text-gray-600 dark:text-gray-400">Preferred Brands:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="brand in user.preferred_manufacturers" :key="brand"
                        class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {{ brand }}
                  </span>
                </div>
              </div>
              <div v-if="user.notes">
                <span class="text-sm text-gray-600 dark:text-gray-400">Notes:</span>
                <p class="text-sm text-gray-700 dark:text-gray-300 mt-1">{{ user.notes }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Profile Modal -->
      <div v-if="isEditing" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
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
                    class="w-full"
                  ></md-slider>
                  <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                    <span>20"</span>
                    <span>36"</span>
                  </div>
                </div>

                <!-- Shooting Style -->
                <div class="mb-4">
                  <label for="shootingStyle" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Primary Shooting Style
                  </label>
                  <select id="shootingStyle" v-model="editedShootingStyle" class="form-select w-full" required>
                    <option value="target">Target</option>
                    <option value="hunting">Hunting</option>
                    <option value="traditional">Traditional</option>
                    <option value="3d">3D</option>
                  </select>
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
                <div class="flex justify-between items-start mb-2">
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ setup.name }} ({{ setup.bow_config?.bow_type || 'Unknown' }})</h4>
                    <p class="text-sm text-gray-700 dark:text-gray-300">Draw Weight: {{ setup.bow_config?.draw_weight || 'N/A' }} lbs</p>
                    <p v-if="setup.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ setup.description }}</p>
                  </div>
                  <div class="flex space-x-2 ml-4">
                    <CustomButton
                      @click="openArrowSearchModal(setup)"
                      variant="filled"
                      size="small"
                      class="bg-green-600 text-white hover:bg-green-700"
                    >
                      <i class="fas fa-search mr-1"></i>
                      Add Arrow
                    </CustomButton>
                    <CustomButton
                      @click="confirmDeleteSetup(setup.id)"
                      variant="text"
                      size="small"
                      class="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900 p-1"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </CustomButton>
                  </div>
                </div>
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

        <!-- Add/Edit Bow Setup Modal -->
        <div v-if="isAddingSetup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl shadow-lg max-h-screen overflow-y-auto">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
              <i class="fas fa-plus-circle mr-2 text-blue-600"></i>
              Create New Bow Setup
            </h3>
            <form @submit.prevent="saveBowSetup">
              <!-- Setup Name -->
              <div class="mb-6">
                <md-outlined-text-field 
                  class="w-full"
                  :value="newSetup.name"
                  @input="newSetup.name = $event.target.value"
                  label="Setup Name"
                  placeholder="e.g. My Hunting Bow, Competition Setup..."
                  required
                >
                  <i class="fas fa-tag" slot="leading-icon" style="color: #6b7280;"></i>
                </md-outlined-text-field>
              </div>

              <!-- Bow Configuration -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <!-- Bow Type -->
                <div>
                  <md-filled-select
                    label="Bow Type"
                    :value="newSetup.bow_type"
                    @change="newSetup.bow_type = $event.target.value"
                    class="w-full"
                    required
                  >
                    <md-select-option value="compound">
                      <div slot="headline">Compound</div>
                    </md-select-option>
                    <md-select-option value="recurve">
                      <div slot="headline">Recurve</div>
                    </md-select-option>
                    <md-select-option value="longbow">
                      <div slot="headline">Longbow</div>
                    </md-select-option>
                    <md-select-option value="traditional">
                      <div slot="headline">Traditional</div>
                    </md-select-option>
                  </md-filled-select>
                </div>

                <!-- Draw Weight -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Draw Weight: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ newSetup.draw_weight || 45 }} lbs</span>
                  </label>
                  <md-slider
                    min="20"
                    max="80"
                    step="5"
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

                <!-- Point Weight -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Point Weight: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ newSetup.point_weight || 125 }} gr</span>
                  </label>
                  <md-slider
                    min="75"
                    max="200"
                    step="25"
                    :value="newSetup.point_weight || 125"
                    @input="newSetup.point_weight = parseInt($event.target.value)"
                    labeled
                    ticks
                    class="w-full"
                  ></md-slider>
                  <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                    <span>75 gr</span>
                    <span>200 gr</span>
                  </div>
                </div>

                <!-- Arrow Length -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Arrow Length: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ newSetup.arrow_length || 29 }}"</span>
                  </label>
                  <md-slider
                    min="24"
                    max="34"
                    step="0.5"
                    :value="newSetup.arrow_length || 29"
                    @input="newSetup.arrow_length = parseFloat($event.target.value)"
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

              <!-- Draw Length Info -->
              <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <i class="fas fa-info-circle mr-2 text-blue-600"></i>
                  <strong>Draw Length:</strong> {{ user?.draw_length || '28.0' }}" (from your archer profile)
                </p>
                <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Update your draw length in the "Edit Profile" section above if needed.
                </p>
              </div>

              <!-- Description -->
              <div class="mb-6">
                <md-outlined-text-field 
                  class="w-full"
                  :value="newSetup.description"
                  @input="newSetup.description = $event.target.value"
                  label="Description (optional)"
                  type="textarea"
                  rows="3"
                  placeholder="Notes about this bow setup, intended use, etc..."
                >
                  <i class="fas fa-comment" slot="leading-icon" style="color: #6b7280;"></i>
                </md-outlined-text-field>
              </div>

              <!-- Action Buttons -->
              <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                <CustomButton
                  type="button"
                  @click="closeAddSetupModal"
                  variant="outlined"
                  class="text-gray-700 dark:text-gray-200"
                >
                  <i class="fas fa-times mr-2"></i>
                  Cancel
                </CustomButton>
                <CustomButton
                  type="submit"
                  variant="filled"
                  :disabled="isSavingSetup"
                  class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
                >
                  <i v-if="isSavingSetup" class="fas fa-spinner fa-spin mr-2"></i>
                  <i v-else class="fas fa-save mr-2"></i>
                  <span v-if="isSavingSetup">Creating Setup...</span>
                  <span v-else>Create Setup</span>
                </CustomButton>
              </div>
              <p v-if="addSetupError" class="text-red-500 text-sm mt-3 flex items-center">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                {{ addSetupError }}
              </p>
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
        <!-- End of Confirm Delete Modal -->

        <!-- Arrow Search Modal -->
        <ArrowSearchModal
          :is-open="isArrowSearchOpen"
          :bow-setup="selectedBowSetup"
          @close="closeArrowSearchModal"
          @add-arrow="handleAddArrow"
        />
        <!-- End of Arrow Search Modal -->

      </div>
      <!-- End of Bow Setups Section -->
    </div>
    <!-- End of v-else-if="user" section -->

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
import ArrowSearchModal from '~/components/ArrowSearchModal.vue';

const { user, logout, loginWithGoogle, updateUserProfile, fetchUser, fetchBowSetups, addBowSetup, deleteBowSetup, addArrowToSetup } = useAuth();

const isLoadingUser = ref(true);
const isEditing = ref(false);
const editedName = ref('');
const editedDrawLength = ref(28.0);
const editedSkillLevel = ref('intermediate');
const editedShootingStyle = ref('target');
const editedPreferredManufacturers = ref('');
const editedNotes = ref('');
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

// Arrow search modal state
const isArrowSearchOpen = ref(false);
const selectedBowSetup = ref(null);

const newSetup = ref({
  name: '',
  bow_type: '',
  draw_weight: 45,
  point_weight: 125,
  arrow_length: 29,
  description: '',
});

const openEditModal = () => {
  editedName.value = user.value?.name || '';
  editedDrawLength.value = user.value?.draw_length || 28.0;
  editedSkillLevel.value = user.value?.skill_level || 'intermediate';
  editedShootingStyle.value = user.value?.shooting_style || 'target';
  editedPreferredManufacturers.value = (user.value?.preferred_manufacturers || []).join(', ');
  editedNotes.value = user.value?.notes || '';
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
    // Parse preferred manufacturers from comma-separated string
    const preferredManufacturers = editedPreferredManufacturers.value
      .split(',')
      .map(brand => brand.trim())
      .filter(brand => brand.length > 0);
    
    await updateUserProfile({
      name: editedName.value,
      draw_length: editedDrawLength.value,
      skill_level: editedSkillLevel.value,
      shooting_style: editedShootingStyle.value,
      preferred_manufacturers: preferredManufacturers,
      notes: editedNotes.value
    });
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
    point_weight: 125,
    arrow_length: 29,
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
    // Send data in the flat format expected by the API
    const setupData = {
      name: newSetup.value.name,
      bow_type: newSetup.value.bow_type,
      draw_weight: Number(newSetup.value.draw_weight),
      draw_length: user.value?.draw_length || 28.0, // Use user's draw length from profile
      description: newSetup.value.description,
      // Include the new configurable fields
      arrow_length: Number(newSetup.value.arrow_length),
      point_weight: Number(newSetup.value.point_weight)
    };

    await addBowSetup(setupData);
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

// Arrow search modal methods
const openArrowSearchModal = (setup) => {
  selectedBowSetup.value = setup;
  isArrowSearchOpen.value = true;
};

const closeArrowSearchModal = () => {
  isArrowSearchOpen.value = false;
  selectedBowSetup.value = null;
};

const handleAddArrow = async (arrowData) => {
  try {
    // Create the API payload
    const apiData = {
      arrow_id: arrowData.arrow.id,
      arrow_length: arrowData.adjustments.arrow_length,
      point_weight: arrowData.adjustments.point_weight,
      calculated_spine: arrowData.calculatedSpine,
      compatibility_score: arrowData.compatibility_score,
      notes: `Added via arrow search - ${arrowData.compatibility_score}% match`
    };
    
    // Call the API to add arrow to setup
    await addArrowToSetup(selectedBowSetup.value.id, apiData);
    
    // Show success message (you could add a toast notification here)
    alert(`Successfully added ${arrowData.arrow.manufacturer} ${arrowData.arrow.model_name} to ${selectedBowSetup.value.name}!`);
    
  } catch (err) {
    console.error('Error adding arrow to setup:', err);
    alert('Failed to add arrow to setup. Please try again.');
  }
};

// Helper functions for display formatting
const formatSkillLevel = (level) => {
  const levels = {
    'beginner': 'Beginner',
    'intermediate': 'Intermediate', 
    'advanced': 'Advanced'
  };
  return levels[level] || level;
};

const formatShootingStyle = (style) => {
  const styles = {
    'target': 'Target',
    'hunting': 'Hunting',
    'traditional': 'Traditional',
    '3d': '3D'
  };
  return styles[style] || style;
};

const getSkillLevelClass = (level) => {
  const classes = {
    'beginner': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'intermediate': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'advanced': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  };
  return classes[level] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
};

const getShootingStyleClass = (style) => {
  const classes = {
    'target': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'hunting': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'traditional': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    '3d': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  };
  return classes[style] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
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