<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Notification Toast -->
    <div v-if="notification.show" class="fixed top-4 right-4 z-50 transition-all duration-300">
      <div 
        :class="[
          'p-4 rounded-lg shadow-lg max-w-sm',
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
            <span>{{ notification.message }}</span>
          </div>
          <button @click="hideNotification" class="ml-4 opacity-70 hover:opacity-100">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">My Setup</h1>
    
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
          <!-- Profile Picture & Basic Info -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Profile</h3>
            
            <!-- Profile Picture Upload -->
            <div class="mb-6">
              <ImageUpload
                :current-image-url="user.profile_picture_url"
                alt-text="Profile picture"
                upload-path="profile"
                @upload-success="handleProfilePictureUpload"
                @upload-error="handleUploadError"
                @image-removed="handleProfilePictureRemoval"
              />
            </div>
            
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
                  {{ formatShootingStyles(user.shooting_style) }}
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
      <EditArcherProfileModal
        :is-open="isEditing"
        :user="user"
        :isSaving="isSaving"
        :error="editError"
        @close="closeEditModal"
        @save="saveProfile"
      />

      <!-- Bow Setups Section -->
      <div class="mt-8">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">My Bow Setups</h3>

          <div v-if="isLoadingSetups" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
            <p class="text-gray-700 dark:text-gray-300">Loading bow setups...</p>
          </div>

          <div v-else>
            <div v-if="bowSetups.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div 
                v-for="setup in bowSetups" 
                :key="setup.id" 
                class="card p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow cursor-pointer"
                @click="navigateToBowDetail(setup.id)"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <!-- Bow Name and Type -->
                    <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      {{ setup.name }} 
                      <span class="text-sm font-normal text-gray-600 dark:text-gray-400">({{ formatBowType(setup.bow_type) }})</span>
                    </h4>
                    
                    <!-- Main Bow Info - Simplified -->
                    <div class="space-y-1 text-sm">
                      <div class="text-gray-700 dark:text-gray-300">
                        <span class="font-medium">Draw Weight:</span> {{ setup.draw_weight }} lbs
                      </div>
                      
                      <!-- Show bow model based on type -->
                      <div v-if="setup.bow_type === 'compound' && setup.compound_brand" class="text-gray-700 dark:text-gray-300">
                        <span class="font-medium">Bow:</span> {{ setup.compound_brand }} {{ setup.compound_model }}
                        <span v-if="setup.ibo_speed" class="ml-1 text-xs text-gray-500">({{ setup.ibo_speed }} fps)</span>
                      </div>
                      <div v-else-if="setup.riser_brand" class="text-gray-700 dark:text-gray-300">
                        <span class="font-medium">Riser:</span> {{ setup.riser_brand }} {{ setup.riser_model }}
                      </div>
                    </div>
                    
                    <!-- Bow Usage Tags -->
                    <div v-if="setup.bow_usage" class="mt-3">
                      <div class="flex flex-wrap gap-1">
                        <span v-for="usage in getBowUsageArray(setup.bow_usage)" :key="usage"
                              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          {{ formatBowUsage(usage) }}
                        </span>
                      </div>
                    </div>

                    <!-- Arrow Count Badge -->
                    <div v-if="setup.arrows && setup.arrows.length > 0" class="mt-3">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        <i class="fas fa-location-arrow mr-1"></i>
                        {{ setup.arrows.length }} {{ setup.arrows.length === 1 ? 'arrow' : 'arrows' }} selected
                      </span>
                    </div>
                  </div>
                  
                  <!-- Quick Actions -->
                  <div class="flex flex-col space-y-2 ml-4" @click.stop>
                    <CustomButton
                      @click="openEditBowSetupModal(setup)"
                      variant="text"
                      size="small"
                      class="text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900"
                    >
                      <i class="fas fa-edit"></i>
                    </CustomButton>
                    <CustomButton
                      @click="confirmDeleteSetup(setup.id)"
                      variant="text"
                      size="small"
                      class="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900"
                    >
                      <i class="fas fa-trash"></i>
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
import { useAuth } from '~/composables/useAuth';
import BowSetupArrowsList from '~/components/BowSetupArrowsList.vue';
import AddBowSetupModal from '~/components/AddBowSetupModal.vue';
import EditArcherProfileModal from '~/components/EditArcherProfileModal.vue';
import EditArrowModal from '~/components/EditArrowModal.vue';
import ImageUpload from '~/components/ImageUpload.vue';

const { user, logout, loginWithGoogle, updateUserProfile, fetchUser, fetchBowSetups, addBowSetup, updateBowSetup, deleteBowSetup, addArrowToSetup, fetchSetupArrows, deleteArrowFromSetup, updateArrowInSetup } = useAuth();

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

    if (isEditMode.value && editingSetupId.value) {
      await updateBowSetup(editingSetupId.value, setupData);
    } else {
      await addBowSetup(setupData);
    }
    
    closeAddSetupModal();
    await loadBowSetups();
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

// Navigation methods
const navigateToBowDetail = (setupId) => {
  navigateTo(`/bow/${setupId}`);
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