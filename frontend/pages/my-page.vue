<template>
  <div class="container mx-auto px-4 py-8">
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
            <div v-if="bowSetups.length > 0" class="space-y-4 mb-6">
              <div v-for="setup in bowSetups" :key="setup.id" class="card p-4 border border-gray-200 dark:border-gray-700">
                <div class="flex justify-between items-start mb-2">
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ setup.name }} ({{ setup.bow_type || 'Unknown' }})</h4>
                    
                    <!-- Bow Specifications Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 text-sm">
                      <!-- Draw Weight & Length -->
                      <div class="text-gray-700 dark:text-gray-300">
                        <span class="font-medium">Draw Weight:</span> {{ setup.draw_weight || 'N/A' }} lbs
                      </div>
                      <div v-if="setup.draw_length" class="text-gray-700 dark:text-gray-300">
                        <span class="font-medium">Draw Length:</span> {{ setup.draw_length }}"
                      </div>
                      
                      <!-- Arrow Specifications -->
                      <div v-if="setup.arrow_length" class="text-gray-700 dark:text-gray-300">
                        <span class="font-medium">Arrow Length:</span> {{ setup.arrow_length }}"
                      </div>
                      <div v-if="setup.point_weight" class="text-gray-700 dark:text-gray-300">
                        <span class="font-medium">Point Weight:</span> {{ setup.point_weight }} gr
                      </div>
                    </div>
                    
                    <!-- Brand Information Display -->
                    <div v-if="setup.riser_brand && (setup.bow_type === 'recurve' || setup.bow_type === 'traditional')" class="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      <span class="font-medium">Riser:</span> {{ setup.riser_brand }} {{ setup.riser_model }}
                      <span v-if="setup.riser_length" class="ml-1">({{ setup.riser_length }})</span>
                    </div>
                    <div v-if="setup.limb_brand && (setup.bow_type === 'recurve' || setup.bow_type === 'traditional')" class="text-sm text-gray-600 dark:text-gray-400">
                      <span class="font-medium">Limbs:</span> {{ setup.limb_brand }} {{ setup.limb_model }}
                      <span v-if="setup.limb_length" class="ml-1">({{ setup.limb_length }})</span>
                    </div>
                    <div v-if="setup.compound_brand && setup.bow_type === 'compound'" class="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      <span class="font-medium">Bow:</span> {{ setup.compound_brand }} {{ setup.compound_model }}
                      <span v-if="setup.ibo_speed" class="ml-2 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded-full">
                        {{ setup.ibo_speed }} fps IBO
                      </span>
                    </div>
                    
                    <!-- Additional Component Weights (if specified) -->
                    <div v-if="setup.nock_weight || setup.fletching_weight || setup.insert_weight" class="mt-2">
                      <div class="text-xs text-gray-500 dark:text-gray-500 font-medium mb-1">Component Weights:</div>
                      <div class="grid grid-cols-2 md:grid-cols-3 gap-1 text-xs text-gray-600 dark:text-gray-400">
                        <div v-if="setup.nock_weight">
                          <span class="font-medium">Nock:</span> {{ setup.nock_weight }} gr
                        </div>
                        <div v-if="setup.fletching_weight">
                          <span class="font-medium">Fletching:</span> {{ setup.fletching_weight }} gr
                        </div>
                        <div v-if="setup.insert_weight">
                          <span class="font-medium">Insert:</span> {{ setup.insert_weight }} gr
                        </div>
                      </div>
                    </div>
                    
                    <!-- Bow Usage Tags -->
                    <div v-if="setup.bow_usage" class="mt-2">
                      <div class="flex flex-wrap gap-1">
                        <span v-for="usage in getBowUsageArray(setup.bow_usage)" :key="usage"
                              class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          {{ formatBowUsage(usage) }}
                        </span>
                      </div>
                    </div>
                    
                    <p v-if="setup.description" class="text-sm text-gray-600 dark:text-gray-400 mt-2 italic">{{ setup.description }}</p>
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
                      @click="openEditBowSetupModal(setup)"
                      variant="text"
                      size="small"
                      class="text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900 p-1"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
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
                
                <!-- Arrows List for this Bow Setup -->
                <BowSetupArrowsList
                  :arrows="setup.arrows || []"
                  :loading="setup.loadingArrows || false"
                  @remove-arrow="removeArrowFromSetup"
                  @view-details="viewArrowDetails"
                />
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
import BowSetupArrowsList from '~/components/BowSetupArrowsList.vue';
import AddBowSetupModal from '~/components/AddBowSetupModal.vue';
import EditArcherProfileModal from '~/components/EditArcherProfileModal.vue';

const { user, logout, loginWithGoogle, updateUserProfile, fetchUser, fetchBowSetups, addBowSetup, updateBowSetup, deleteBowSetup, addArrowToSetup, fetchSetupArrows, deleteArrowFromSetup } = useAuth();

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

// Arrow search modal state
const isArrowSearchOpen = ref(false);
const selectedBowSetup = ref(null);

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
    // Check if a bow setup is selected
    if (!selectedBowSetup.value) {
      alert('Please select a bow setup first before adding arrows.');
      return;
    }
    
    // Store the setup info before it gets cleared
    const setupId = selectedBowSetup.value.id;
    const setupName = selectedBowSetup.value.name;
    
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
    await addArrowToSetup(setupId, apiData);
    
    // Show success message
    alert(`Successfully added ${arrowData.arrow.manufacturer} ${arrowData.arrow.model_name} to ${setupName}!`);
    
    // Reload arrows for the setup to show the new arrow
    await loadArrowsForSetup(setupId);
    
  } catch (err) {
    console.error('Error adding arrow to setup:', err);
    alert('Failed to add arrow to setup. Please try again.');
  }
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


const removeArrowFromSetup = async (arrowSetupId) => {
  if (!confirm('Are you sure you want to remove this arrow from the setup?')) {
    return;
  }
  
  try {
    await deleteArrowFromSetup(arrowSetupId);
    
    // Reload all bow setups to refresh the arrows lists 
    await loadBowSetups();
    
    alert('Arrow removed successfully!');
  } catch (err) {
    console.error('Error removing arrow from setup:', err);
    alert('Failed to remove arrow. Please try again.');
  }
};

const viewArrowDetails = (arrowId) => {
  // Navigate to arrow details page
  navigateTo(`/arrows/${arrowId}`);
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