<template>
  <div class="container mx-auto mobile-container md:px-4 py-6 md:py-8 pb-24 md:pb-8">
    <!-- Notification Toast -->
    <div v-if="notification.show" class="fixed top-4 right-4 z-50 transition-all duration-300">
      <div 
        :class="[
          'p-3 sm-mobile:p-4 rounded-lg shadow-lg max-w-sm',
          notification.type === 'success' ? 'bg-green-500 text-white' : '',
          notification.type === 'error' ? 'bg-red-500 text-white' : '',
          notification.type === 'warning' ? 'bg-yellow-500 text-black' : ''
        ]"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <i v-if="notification.type === 'success'" class="fas fa-check-circle mr-2"></i>
            <i v-if="notification.type === 'error'" class="fas fa-exclamation-circle mr-2"></i>
            <i v-if="notification.type === 'warning'" class="fas fa-exclamation-triangle mr-2"></i>
            <span class="mobile-body-medium md:text-base">{{ notification.message }}</span>
          </div>
          <button @click="hideNotification" class="ml-4 opacity-70 hover:opacity-100 mobile-touch-target">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <h1 class="mobile-heading-1 md:text-3xl font-bold text-gray-900 dark:text-gray-100 mobile-element-spacing md:mb-4">My Setup</h1>
    
    <div v-if="isLoadingUser" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
      <p class="text-gray-700 dark:text-gray-300">Loading...</p>
    </div>

    <div v-else-if="user">
      <!-- Compact Profile Header -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-3 sm-mobile:p-4 mobile-section-spacing md:mb-6">
        <!-- Profile Content -->
        <div class="flex items-center space-x-3 sm-mobile:space-x-4 mb-3 sm-mobile:mb-4">
          <!-- Profile Picture -->
          <div class="flex-shrink-0">
            <div class="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">
              <img 
                v-if="user.profile_picture_url" 
                :src="user.profile_picture_url" 
                :alt="user.name || 'Profile picture'" 
                class="w-12 h-12 rounded-full object-cover"
              />
              <span v-else class="mobile-body-large md:text-lg">
                {{ (user.name || user.email || 'U').charAt(0).toUpperCase() }}
              </span>
            </div>
          </div>
          
          <!-- Basic Info -->
          <div class="flex-1">
            <h2 class="mobile-heading-4 md:text-xl font-bold text-gray-900 dark:text-gray-100 mb-0">
              {{ user.name || 'Archer' }}
            </h2>
            <div class="flex items-center space-x-3 sm-mobile:space-x-4 mobile-body-small md:text-sm text-gray-600 dark:text-gray-400">
              <span>Draw: {{ user.draw_length || 28.0 }}"</span>
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                    :class="getSkillLevelClass(user.skill_level)">
                {{ formatSkillLevel(user.skill_level) }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- Action Buttons - Full Width -->
        <div class="flex flex-col sm:flex-row gap-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <CustomButton
            @click="openEditModal"
            variant="outlined"
            size="small"
            class="flex-1 text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-purple-400 dark:border-purple-400 dark:hover:bg-purple-900"
          >
            <i class="fas fa-edit mr-2"></i>
            Edit Profile
          </CustomButton>
          <CustomButton
            @click="logout"
            variant="outlined"
            size="small"
            class="flex-1 text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900"
          >
            <i class="fas fa-sign-out-alt mr-2"></i>
            Logout
          </CustomButton>
        </div>
      </div>

      <!-- Edit Profile Modal -->
      <EditArcherProfileModal
        :is-open="isEditing"
        :user="user"
        :isSaving="isSaving"
        :error="editError"
        @close="closeEditModal"
        @save="saveProfile"
      />

      <!-- Bow Setups Dashboard Section -->
      <div class="mt-6">
        <div class="mb-6">
          <div>
            <h3 class="text-2xl font-bold text-gray-900 dark:text-gray-100">My Bow Setups</h3>
            <p class="text-gray-600 dark:text-gray-400">Manage your bow configurations and arrow selections</p>
          </div>
        </div>

        <!-- Quick Stats - Enhanced Mobile Responsive -->
        <div v-if="bowSetups.length > 0" class="hidden sm-mobile:grid grid-cols-2 md-mobile:grid-cols-3 sm:grid-cols-3 gap-3 md-mobile:gap-4 mb-6">
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-4 rounded-lg border border-blue-200 dark:border-blue-700">
            <div class="flex items-center">
              <i class="fas fa-bow-arrow text-2xl text-blue-600 dark:text-blue-400 mr-3"></i>
              <div>
                <p class="text-2xl font-bold text-blue-900 dark:text-blue-200">{{ bowSetups.length }}</p>
                <p class="text-sm text-blue-700 dark:text-blue-300">Bow {{ bowSetups.length === 1 ? 'Setup' : 'Setups' }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 p-4 rounded-lg border border-green-200 dark:border-green-700">
            <div class="flex items-center">
              <i class="fas fa-location-arrow text-2xl text-green-600 dark:text-green-400 mr-3"></i>
              <div>
                <p class="text-2xl font-bold text-green-900 dark:text-green-200">{{ totalArrows }}</p>
                <p class="text-sm text-green-700 dark:text-green-300">Selected Arrows</p>
              </div>
            </div>
          </div>
          
          <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 p-4 rounded-lg border border-purple-200 dark:border-purple-700">
            <div class="flex items-center">
              <i class="fas fa-calculator text-2xl text-purple-600 dark:text-purple-400 mr-3"></i>
              <div>
                <p class="text-2xl font-bold text-purple-900 dark:text-purple-200">{{ averageDrawWeight }}</p>
                <p class="text-sm text-purple-700 dark:text-purple-300">Avg. Draw Weight</p>
              </div>
            </div>
          </div>
        </div>

          <div v-if="isLoadingSetups" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
            <p class="text-gray-700 dark:text-gray-300">Loading bow setups...</p>
          </div>

          <div v-else>
            <!-- Add New Setup Button -->
            <div class="flex justify-center mb-6">
              <CustomButton
                @click="openAddSetupModal"
                variant="filled"
                class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 w-full md:w-auto touch-target"
              >
                <i class="fas fa-plus mr-2"></i>
                Add New Setup
              </CustomButton>
            </div>
            <div v-if="bowSetups.length > 0" class="grid grid-cols-1 md-mobile:grid-cols-2 lg-mobile:grid-cols-2 md:grid-cols-2 xl:grid-cols-3 gap-3 md-mobile:gap-4 mb-6 w-full">
              <div 
                v-for="setup in bowSetups" 
                :key="setup.id" 
                class="relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-lg transition-all duration-200 cursor-pointer touch-target overflow-hidden w-full max-w-md md-mobile:max-w-none mx-auto"
                @click="navigateToBowDetail(setup.id)"
              >
                <!-- Bow Card Content -->
                <div class="p-4">
                  <div class="w-full max-w-none mx-0">
                    <!-- Card Header -->
                    <div class="flex items-start justify-between mb-4 w-full">
                    <div class="flex-1 min-w-0">
                      <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 leading-tight truncate">
                        {{ setup.name }}
                      </h4>
                      <span class="text-sm text-gray-500 dark:text-gray-400 mt-1 block">{{ formatBowType(setup.bow_type) }}</span>
                    </div>
                    <div class="flex items-center gap-2 ml-3 flex-shrink-0" @click.stop>
                      <CustomButton
                        @click="navigateToCalculatorWithSetup(setup.id)"
                        variant="text"
                        size="small"
                        class="text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900 touch-target p-2"
                        title="Find Arrows"
                      >
                        <i class="fas fa-search text-sm"></i>
                      </CustomButton>
                      <CustomButton
                        @click="navigateToBowDetail(setup.id)"
                        variant="text"
                        size="small"
                        class="text-green-600 hover:bg-green-50 dark:text-green-400 dark:hover:bg-green-900 touch-target p-2"
                        title="View Details"
                      >
                        <i class="fas fa-eye text-sm"></i>
                      </CustomButton>
                    </div>
                  </div>
                  <!-- Main Bow Info - Compact Design -->
                  <div class="space-y-3 w-full">
                    <!-- Key Specs Row -->
                    <div class="grid grid-cols-2 gap-4 text-sm w-full">
                      <div class="min-w-0">
                        <span class="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Draw Weight</span>
                        <div class="font-semibold text-gray-900 dark:text-gray-100 text-base mt-1 truncate">{{ setup.draw_weight }} lbs</div>
                      </div>
                      <div v-if="setup.draw_length" class="min-w-0">
                        <span class="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Draw Length</span>
                        <div class="font-semibold text-gray-900 dark:text-gray-100 text-base mt-1 truncate">{{ setup.draw_length }}"</div>
                      </div>
                    </div>
                    
                    <!-- Bow Model Info -->
                    <div v-if="setup.bow_type === 'compound' && setup.compound_brand" class="text-sm w-full">
                      <span class="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Bow Model</span>
                      <div class="font-medium text-gray-900 dark:text-gray-100 mt-1 truncate">
                        {{ setup.compound_brand }} {{ setup.compound_model }}
                        <span v-if="setup.ibo_speed" class="ml-2 text-xs text-blue-600 dark:text-blue-400">({{ setup.ibo_speed }} fps)</span>
                      </div>
                    </div>
                    <div v-else-if="setup.riser_brand" class="text-sm w-full">
                      <span class="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Riser</span>
                      <div class="font-medium text-gray-900 dark:text-gray-100 mt-1 truncate">{{ setup.riser_brand }} {{ setup.riser_model }}</div>
                    </div>
                    
                    <!-- Status Row -->
                    <div class="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700 w-full">
                      <!-- Left side - Usage tags and status -->
                      <div class="flex flex-wrap gap-1 flex-1 min-w-0">
                        <span v-for="usage in getBowUsageArray(setup.bow_usage)" :key="usage"
                              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                          {{ formatBowUsage(usage) }}
                        </span>
                      </div>
                      
                      <!-- Right side - Counts -->
                      <div class="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 flex-shrink-0">
                        <div v-if="setup.arrows && setup.arrows.length > 0" class="flex items-center">
                          <i class="fas fa-location-arrow mr-1 text-green-600 dark:text-green-400"></i>
                          {{ setup.arrows.length }}
                        </div>
                        <div v-if="setup.equipment && setup.equipment.length > 0" class="flex items-center">
                          <i class="fas fa-cogs mr-1 text-purple-600 dark:text-purple-400"></i>
                          {{ setup.equipment.length }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                </div>
              </div>
            </div>
            
            <!-- Empty State -->
            <div v-else class="text-center py-12">
              <i class="fas fa-bow-arrow text-6xl text-gray-300 dark:text-gray-600 mb-4"></i>
              <h4 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">No Bow Setups Yet</h4>
              <p class="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                Get started by creating your first bow setup. Add your bow specifications and start finding the perfect arrows.
              </p>
              <CustomButton
                @click="openAddSetupModal"
                variant="filled"
                class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
              >
                <i class="fas fa-plus mr-2"></i>
                Create Your First Setup
              </CustomButton>
            </div>
          </div>

        <!-- Add/Edit Bow Setup Modal -->
        <AddBowSetupModal
          v-if="isAddingSetup"
          :modelValue="newSetup"
          :isSaving="isSavingSetup"
          :error="addSetupError"
          @update:modelValue="newSetup = $event"
          @save="handleSaveBowSetup"
          @close="closeAddSetupModal"
        />

        <!-- Confirm Delete Modal -->
        <div v-if="isConfirmingDelete" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center modal-overlay p-4">
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

        <!-- Edit Arrow Modal -->
        <EditArrowModal
          :is-open="isEditArrowModalOpen"
          :arrow-setup="editingArrowSetup"
          @close="closeEditArrowModal"
          @arrow-updated="handleArrowUpdated"
          @error="handleArrowEditError"
        />
        <!-- End of Edit Arrow Modal -->

        <!-- Arrow Removal Confirmation Modal -->
        <div v-if="arrowRemovalConfirm.show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center modal-overlay p-4 z-50">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-lg text-center">
            <div class="mb-4">
              <i class="fas fa-exclamation-triangle text-yellow-500 text-4xl mb-2"></i>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Remove Arrow</h3>
            </div>
            <p class="text-gray-700 dark:text-gray-300 mb-6">
              Are you sure you want to remove "{{ arrowRemovalConfirm.arrowName }}" from this setup?
            </p>
            <div class="flex justify-center space-x-4">
              <CustomButton
                @click="hideArrowRemovalConfirm"
                variant="outlined"
                class="text-gray-700 dark:text-gray-200"
              >
                Cancel
              </CustomButton>
              <CustomButton
                @click="confirmRemoveArrow"
                variant="filled"
                class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
              >
                Remove
              </CustomButton>
            </div>
          </div>
        </div>
        <!-- End of Arrow Removal Confirmation Modal -->


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
import { useBowSetupPickerStore } from '~/stores/bowSetupPicker';
import { useAuth } from '~/composables/useAuth';
import BowSetupArrowsList from '~/components/BowSetupArrowsList.vue';
import AddBowSetupModal from '~/components/AddBowSetupModal.vue';
import EditArcherProfileModal from '~/components/EditArcherProfileModal.vue';
import EditArrowModal from '~/components/EditArrowModal.vue';
import ImageUpload from '~/components/ImageUpload.vue';

const { user, logout, loginWithGoogle, updateUserProfile, fetchUser, fetchBowSetups, addBowSetup, updateBowSetup, deleteBowSetup, addArrowToSetup, fetchSetupArrows, deleteArrowFromSetup, updateArrowInSetup } = useAuth();
const bowSetupPickerStore = useBowSetupPickerStore();

const isLoadingUser = ref(true);
const isEditing = ref(false);
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
const isEditMode = ref(false);
const editingSetupId = ref(null);

// Edit arrow modal state
const isEditArrowModalOpen = ref(false);
const editingArrowSetup = ref(null);

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success' // 'success', 'error', 'warning'
});

// Arrow removal confirmation state
const arrowRemovalConfirm = ref({
  show: false,
  arrowSetupId: null,
  arrowName: ''
});


const newSetup = ref({
  name: '',
  bow_type: '',
  draw_weight: 45,
  draw_length: null,
  draw_length_module: null,  // For compound bow cam specification
  arrow_length: null,
  point_weight: 100,
  description: '',
  bow_usage: [],
});

const openEditModal = () => {
  isEditing.value = true;
  editError.value = null;
};

const closeEditModal = () => {
  isEditing.value = false;
};

const saveProfile = async (profileData) => {
  isSaving.value = true;
  editError.value = null;
  try {
    await updateUserProfile(profileData);
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
    const setups = await fetchBowSetups();
    bowSetups.value = setups;
    
    // Load arrows for each setup
    await loadArrowsForAllSetups();
  } catch (err) {
    console.error('Error loading bow setups:', err);
    // Optionally display an error message to the user
  } finally {
    isLoadingSetups.value = false;
  }
};

const loadArrowsForAllSetups = async () => {
  // Load arrows for each setup in parallel
  const arrowPromises = bowSetups.value.map(async (setup) => {
    try {
      setup.loadingArrows = true;
      const arrows = await fetchSetupArrows(setup.id);
      setup.arrows = arrows || [];
    } catch (err) {
      console.error(`Error loading arrows for setup ${setup.id}:`, err);
      setup.arrows = [];
    } finally {
      setup.loadingArrows = false;
    }
  });
  
  await Promise.all(arrowPromises);
};

const openAddSetupModal = () => {
  // Reset form for new entry
  isEditMode.value = false;
  editingSetupId.value = null;
  newSetup.value = {
    name: '',
    bow_type: '',
    draw_weight: 45,
    draw_length_module: null,
    description: '',
    bow_usage: [],
  };
  addSetupError.value = null;
  isAddingSetup.value = true;
};

const closeAddSetupModal = () => {
  isAddingSetup.value = false;
  isEditMode.value = false;
  editingSetupId.value = null;
};

const openEditBowSetupModal = (setup) => {
  // Populate form with existing setup data
  isEditMode.value = true;
  editingSetupId.value = setup.id;
  
  // Pass the setup data to the modal - it will handle the field mapping
  newSetup.value = {
    name: setup.name || '',
    bow_type: setup.bow_type || '',
    draw_weight: setup.draw_weight || 45,
    description: setup.description || '',
    bow_usage: setup.bow_usage ? JSON.parse(setup.bow_usage) : [],
    // Pass existing brand data for the modal to handle
    compound_brand: setup.compound_brand || '',
    compound_model: setup.compound_model || '',
    ibo_speed: setup.ibo_speed || '',
    draw_length_module: setup.draw_length_module || null,
    riser_brand: setup.riser_brand || '',
    riser_model: setup.riser_model || '',
    riser_length: setup.riser_length || '',
    limb_brand: setup.limb_brand || '',
    limb_model: setup.limb_model || '',
    limb_length: setup.limb_length || '',
  };
  
  isAddingSetup.value = true;
  addSetupError.value = null;
};

const handleSaveBowSetup = async (setupData) => {
  isSavingSetup.value = true;
  addSetupError.value = null;
  try {
    // The setupData from the modal is already correctly formatted.
    // We just need to ensure draw_length is present if it's a new setup.
    if (!setupData.draw_length) {
      setupData.draw_length = user.value?.draw_length || 28.0;
    }

    let savedSetupId;
    if (isEditMode.value && editingSetupId.value) {
      await updateBowSetup(editingSetupId.value, setupData);
      savedSetupId = editingSetupId.value;
    } else {
      savedSetupId = await addBowSetup(setupData);
    }
    
    closeAddSetupModal();
    await loadBowSetups();
    
    // Refresh bow selector navigation cache after successful save
    if (savedSetupId && bowSetupPickerStore.refreshSelectedBowSetup) {
      await bowSetupPickerStore.refreshSelectedBowSetup(savedSetupId);
    }
  } catch (err) {
    console.error('Error saving bow setup:', err);
    addSetupError.value = err.message || `Failed to ${isEditMode.value ? 'update' : 'add'} bow setup.`;
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

// Navigation methods
const navigateToArrowCalculator = (setup) => {
  // Store the selected setup in localStorage for the calculator to pick up
  localStorage.setItem('selectedBowSetup', JSON.stringify(setup));
  
  // Navigate to the arrow calculator page
  navigateTo('/calculator');
};

const navigateToCalculatorWithSetup = (setupId) => {
  navigateTo(`/calculator?setupId=${setupId}`);
};


// Edit arrow modal methods
const openEditArrowModal = (arrowSetup) => {
  editingArrowSetup.value = arrowSetup;
  isEditArrowModalOpen.value = true;
};

const closeEditArrowModal = () => {
  editingArrowSetup.value = null;
  isEditArrowModalOpen.value = false;
};

const handleArrowUpdated = async (updatedArrowData) => {
  // Reload arrows for the bow setup to show updated data
  const setupId = editingArrowSetup.value?.setup_id;
  if (setupId) {
    await loadArrowsForSetup(setupId);
  }
  
  // Close the modal
  closeEditArrowModal();
  
  // Show success message
  showNotification('Arrow settings updated successfully!');
};

const handleArrowEditError = (errorMessage) => {
  showNotification(errorMessage, 'error');
};

const loadArrowsForSetup = async (setupId) => {
  const setup = bowSetups.value.find(s => s.id === setupId);
  if (!setup) return;
  
  try {
    setup.loadingArrows = true;
    const arrows = await fetchSetupArrows(setupId);
    setup.arrows = arrows || [];
  } catch (err) {
    console.error(`Error loading arrows for setup ${setupId}:`, err);
    setup.arrows = [];
  } finally {
    setup.loadingArrows = false;
  }
};


const removeArrowFromSetup = async (arrowSetupId, arrowName = 'arrow') => {
  // Show confirmation dialog instead of alert
  showArrowRemovalConfirm(arrowSetupId, arrowName);
};

const confirmRemoveArrow = async () => {
  const arrowSetupId = arrowRemovalConfirm.value.arrowSetupId;
  hideArrowRemovalConfirm();
  
  try {
    await deleteArrowFromSetup(arrowSetupId);
    
    // Reload all bow setups to refresh the arrows lists 
    await loadBowSetups();
    
    showNotification('Arrow removed successfully!');
  } catch (err) {
    console.error('Error removing arrow from setup:', err);
    showNotification('Failed to remove arrow. Please try again.', 'error');
  }
};

const viewArrowDetails = (arrowId) => {
  // Navigate to arrow details page
  navigateTo(`/arrows/${arrowId}`);
};

// Notification helper functions
const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  };
  
  // Auto-hide after 4 seconds
  setTimeout(() => {
    notification.value.show = false;
  }, 4000);
};

const hideNotification = () => {
  notification.value.show = false;
};

// Arrow removal confirmation helpers
const showArrowRemovalConfirm = (arrowSetupId, arrowName) => {
  arrowRemovalConfirm.value = {
    show: true,
    arrowSetupId,
    arrowName
  };
};

const hideArrowRemovalConfirm = () => {
  arrowRemovalConfirm.value = {
    show: false,
    arrowSetupId: null,
    arrowName: ''
  };
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

const formatShootingStyles = (styles) => {
  const styleLabels = {
    'target': 'Target',
    'hunting': 'Hunting',
    'traditional': 'Traditional',
    '3d': '3D'
  };
  
  if (!styles || !Array.isArray(styles)) {
    return 'Target'; // Default fallback
  }
  
  return styles.map(style => styleLabels[style] || style).join(', ');
};

const getSkillLevelClass = (level) => {
  const classes = {
    'beginner': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'intermediate': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'advanced': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  };
  return classes[level] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
};

const getShootingStyleClass = (styles) => {
  // For multiple styles, use a neutral color
  if (!styles || !Array.isArray(styles) || styles.length === 0) {
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
  }
  
  if (styles.length > 1) {
    return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200';
  }
  
  // Single style, use specific color
  const classes = {
    'target': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'hunting': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'traditional': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    '3d': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  };
  return classes[styles[0]] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
};

// Helper function to parse bow usage from JSON string
const getBowUsageArray = (bowUsage) => {
  if (!bowUsage) return [];
  try {
    return Array.isArray(bowUsage) ? bowUsage : JSON.parse(bowUsage);
  } catch {
    return [bowUsage]; // If not JSON, treat as single string
  }
};

// Helper function to format bow usage for display
const formatBowUsage = (usage) => {
  const usageMap = {
    'target': 'Target',
    'hunting': 'Hunting',
    'field': 'Field',
    '3d': '3D',
    'traditional': 'Traditional',
    'competition': 'Competition',
    'recreational': 'Recreational',
    'indoor': 'Indoor',
    'outdoor': 'Outdoor'
  };
  return usageMap[usage] || usage;
};

// Helper function to get equipment category icons
const getCategoryIcon = (categoryName) => {
  const iconMap = {
    'String': 'fas fa-link',
    'Sight': 'fas fa-crosshairs',
    'Stabilizer': 'fas fa-balance-scale',
    'Arrow Rest': 'fas fa-hand-paper',
    'Weight': 'fas fa-weight-hanging'
  };
  return iconMap[categoryName] || 'fas fa-cog';
};

// Profile picture upload handlers
const handleProfilePictureUpload = async (imageUrl) => {
  try {
    // Update the user's profile picture URL locally first for immediate feedback
    if (user.value) {
      user.value.profile_picture_url = imageUrl;
    }
    
    // The API endpoint already updates the database, so we just show success
    showNotification('Profile picture updated successfully!');
    
    // Refresh user data to ensure everything is in sync
    await fetchUser();
  } catch (error) {
    console.error('Profile picture update error:', error);
    showNotification('Profile picture updated, but there was an issue syncing data.', 'warning');
  }
};

const handleProfilePictureRemoval = async () => {
  try {
    // Update user profile to remove picture URL
    await updateUserProfile({ profile_picture_url: null });
    
    // Update local user object
    if (user.value) {
      user.value.profile_picture_url = null;
    }
    
    showNotification('Profile picture removed successfully!');
  } catch (error) {
    console.error('Profile picture removal error:', error);
    showNotification('Failed to remove profile picture. Please try again.', 'error');
  }
};

const handleUploadError = (errorMessage) => {
  showNotification(errorMessage, 'error');
};

// Dashboard computed properties
const totalArrows = computed(() => {
  return bowSetups.value.reduce((total, setup) => {
    return total + (setup.arrows ? setup.arrows.length : 0);
  }, 0);
});

const averageDrawWeight = computed(() => {
  if (bowSetups.value.length === 0) return '0 lbs';
  
  const totalWeight = bowSetups.value.reduce((total, setup) => {
    return total + (setup.draw_weight || 0);
  }, 0);
  
  const average = totalWeight / bowSetups.value.length;
  return `${Math.round(average)} lbs`;
});

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
  
  // Check if we should open the add setup modal
  const route = useRoute();
  if (route.query.add === 'true') {
    openAddSetupModal();
  }
});

// Navigation methods
const navigateToBowDetail = (setupId) => {
  navigateTo(`/setups/${setupId}`);
};


const formatBowType = (bowType) => {
  if (!bowType) return 'Unknown';
  return bowType.charAt(0).toUpperCase() + bowType.slice(1);
};

// Watch for changes in the user object and reload bow setups
watch(user, async (newUser) => {
  if (newUser) {
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