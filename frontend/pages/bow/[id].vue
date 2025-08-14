<template>
  <div class="container mx-auto px-4 py-4 sm:py-8 max-w-6xl">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-4"></div>
      <p class="text-gray-700 dark:text-gray-300">Loading bow setup...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <div class="text-red-600 dark:text-red-400 mb-4">
        <i class="fas fa-exclamation-circle text-4xl mb-4"></i>
        <p class="text-lg">{{ error }}</p>
      </div>
      <CustomButton @click="navigateTo('/my-setup')" variant="outlined">
        Back to My Setup
      </CustomButton>
    </div>

    <!-- Bow Setup Content -->
    <div v-else-if="bowSetup">
      <!-- Back Navigation -->
      <div class="mb-6">
        <CustomButton @click="navigateTo('/my-setup')" variant="text" class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100">
          <i class="fas fa-arrow-left mr-2"></i>
          Back to My Setup
        </CustomButton>
      </div>

      <!-- Bow Header -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6">
        <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between space-y-4 lg:space-y-0">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2 break-words">{{ bowSetup.name }}</h1>
            
            <!-- Bow Type Badge -->
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mb-4"
                  :class="getBowTypeClass(bowSetup.bow_type)">
              <i :class="getBowTypeIcon(bowSetup.bow_type)" class="mr-2"></i>
              {{ formatBowType(bowSetup.bow_type) }}
            </span>

            <!-- Main Bow Info -->
            <div class="mt-4">
              <div v-if="bowSetup.bow_type === 'compound'" class="text-lg text-gray-700 dark:text-gray-300">
                <span class="font-semibold">Bow:</span> 
                {{ bowSetup.compound_brand }} {{ bowSetup.compound_model }}
                <span v-if="bowSetup.ibo_speed" class="ml-2 text-sm bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded-full">
                  {{ bowSetup.ibo_speed }} fps IBO
                </span>
              </div>
              
              <div v-else class="space-y-2">
                <div v-if="bowSetup.riser_brand" class="text-lg text-gray-700 dark:text-gray-300">
                  <span class="font-semibold">Riser:</span> 
                  {{ bowSetup.riser_brand }} {{ bowSetup.riser_model }}
                  <span v-if="bowSetup.riser_length" class="text-sm text-gray-500">({{ bowSetup.riser_length }})</span>
                </div>
                <div v-if="bowSetup.limb_brand" class="text-lg text-gray-700 dark:text-gray-300">
                  <span class="font-semibold">Limbs:</span> 
                  {{ bowSetup.limb_brand }} {{ bowSetup.limb_model }}
                  <span v-if="bowSetup.limb_length" class="text-sm text-gray-500">({{ bowSetup.limb_length }})</span>
                </div>
              </div>
            </div>

            <!-- Bow Usage Tags -->
            <div v-if="bowSetup.bow_usage" class="mt-4">
              <div class="flex flex-wrap gap-2">
                <span v-for="usage in getBowUsageArray(bowSetup.bow_usage)" :key="usage"
                      class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  <i :class="getUsageIcon(usage)" class="mr-1"></i>
                  {{ formatBowUsage(usage) }}
                </span>
              </div>
            </div>

            <!-- Draw Specifications -->
            <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                <i class="fas fa-bullseye mr-2 text-blue-600 dark:text-blue-400"></i>
                Draw Specifications
              </h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-3">
                <div class="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <span class="text-gray-600 dark:text-gray-400">Draw Weight</span>
                  <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.draw_weight }} lbs</span>
                </div>
                <div v-if="bowSetup.draw_length" class="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <span class="text-gray-600 dark:text-gray-400">Draw Length</span>
                  <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.draw_length }}"</span>
                </div>
                <div v-if="bowSetup.arrow_length" class="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <span class="text-gray-600 dark:text-gray-400">Arrow Length</span>
                  <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.arrow_length }}"</span>
                </div>
                <div v-if="bowSetup.point_weight" class="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <span class="text-gray-600 dark:text-gray-400">Point Weight</span>
                  <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.point_weight }} gr</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons - Mobile Responsive -->
          <div class="flex justify-end w-full lg:w-auto lg:flex-shrink-0">
            <CustomButton
              @click="openEditModal"
              variant="outlined"
              class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-900"
            >
              <i class="fas fa-edit mr-2"></i>
              Edit Setup
            </CustomButton>
          </div>
        </div>
      </div>

      <!-- Component Weights -->
      <div v-if="hasComponentWeights" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          <i class="fas fa-weight mr-2 text-purple-600 dark:text-purple-400"></i>
          Component Weights
        </h2>
        <div class="space-y-3">
          <div v-if="bowSetup.nock_weight" class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-gray-600 dark:text-gray-400">Nock Weight</span>
            <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.nock_weight }} gr</span>
          </div>
          <div v-if="bowSetup.fletching_weight" class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-gray-600 dark:text-gray-400">Fletching Weight</span>
            <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.fletching_weight }} gr</span>
          </div>
          <div v-if="bowSetup.insert_weight" class="flex justify-between items-center py-2">
            <span class="text-gray-600 dark:text-gray-400">Insert Weight</span>
            <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.insert_weight }} gr</span>
          </div>
        </div>
      </div>

      <!-- Description -->
      <div v-if="bowSetup.description" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">Description</h2>
        <p class="text-gray-700 dark:text-gray-300">{{ bowSetup.description }}</p>
      </div>

      <!-- Equipment Section -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6">
        <BowEquipmentManager
          :bow-setup="bowSetup"
          @equipment-updated="handleEquipmentUpdated"
          @show-notification="showNotification"
        />
      </div>

      <!-- Selected Arrows Section -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            <i class="fas fa-location-arrow mr-2 text-orange-600 dark:text-orange-400"></i>
            Selected Arrows
          </h2>
          <CustomButton
            @click="openArrowSearchModal"
            variant="filled"
            class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 w-full sm:w-auto"
          >
            <i class="fas fa-plus mr-2"></i>
            Add Arrow
          </CustomButton>
        </div>

        <!-- Arrows List -->
        <div v-if="bowSetup.arrows && bowSetup.arrows.length > 0">
          <BowSetupArrowsList
            :arrows="bowSetup.arrows"
            :loading="loadingArrows"
            @remove-arrow="removeArrowFromSetup"
            @view-details="viewArrowDetails" 
            @edit-arrow="openEditArrowModal"
            @duplicate-arrow="duplicateArrow"
          />
        </div>
        <div v-else class="text-center py-12 text-gray-500 dark:text-gray-400">
          <i class="fas fa-inbox text-4xl mb-4"></i>
          <p class="text-lg">No arrows selected for this bow setup.</p>
          <p class="text-sm mt-2">Click "Add Arrow" to select arrows from the database.</p>
        </div>
      </div>
    </div>

    <!-- Edit Bow Setup Modal -->
    <AddBowSetupModal
      v-if="isEditingSetup"
      :modelValue="editingSetup"
      :isSaving="isSavingSetup"
      :error="editError"
      @update:modelValue="editingSetup = $event"
      @save="handleUpdateSetup"
      @close="closeEditModal"
    />

    <!-- Arrow Search Modal - Navigate to main page with setup loaded -->
    <!-- This functionality will be handled by navigating to the calculator page -->

    <!-- Edit Arrow Configuration Modal -->
    <EditArrowModal
      :is-open="!!editingArrow"
      :arrow-setup="editingArrow"
      :bow-setup="bowSetup"
      @save="handleUpdateArrow"
      @close="editingArrow = null"
    />

    <!-- Arrow Deletion Confirmation Modal -->
    <ConfirmDeleteModal
      v-if="arrowToDelete"
      :title="`Remove Arrow`"
      :message="`Are you sure you want to remove this arrow from your bow setup?`"
      :item-name="getArrowDisplayName(arrowToDelete)"
      :confirm-text="`Remove`"
      :loading="deletingArrow"
      :error="deleteArrowError"
      @confirm="confirmRemoveArrow"
      @cancel="cancelRemoveArrow"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth } from '~/composables/useAuth';
import { useApi } from '~/composables/useApi';
import EditArrowModal from '~/components/EditArrowModal.vue';
import BowEquipmentManager from '~/components/BowEquipmentManager.vue';

const route = useRoute();
const api = useApi();
const { user, token, fetchUser } = useAuth();

// State
const bowSetup = ref(null);
const loading = ref(true);
const loadingArrows = ref(false);
const error = ref(null);
const isEditingSetup = ref(false);
const editingSetup = ref(null);
const isSavingSetup = ref(false);
const editError = ref(null);
const editingArrow = ref(null);

// Arrow deletion state
const arrowToDelete = ref(null);
const deletingArrow = ref(false);
const deleteArrowError = ref('');

// Computed
const hasComponentWeights = computed(() => {
  return bowSetup.value && (
    bowSetup.value.nock_weight ||
    bowSetup.value.fletching_weight ||
    bowSetup.value.insert_weight
  );
});

// Methods
const fetchBowSetup = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // Check authentication first
    if (!user.value) {
      console.log('No user found, attempting to fetch user data...');
      await fetchUser();
      
      if (!user.value) {
        error.value = 'Please log in to view your bow setups';
        return navigateTo('/');
      }
    }
    
    // Check if token exists
    if (!token.value && process.client && !localStorage.getItem('token')) {
      error.value = 'Authentication required. Please log in again.';
      return navigateTo('/');
    }
    
    const response = await api.get(`/bow-setups/${route.params.id}`);
    console.log('Fetched bow setup:', response);
    bowSetup.value = response;
    
    // Fetch arrows for this setup
    await fetchSetupArrows();
  } catch (err) {
    console.error('Error fetching bow setup:', err);
    
    // Handle specific auth errors
    if (err.message.includes('401') || err.message.includes('Token is missing')) {
      error.value = 'Please log in to view your bow setups';
      // Clear invalid token
      if (process.client) {
        localStorage.removeItem('token');
      }
      token.value = null;
      user.value = null;
      return navigateTo('/');
    }
    
    error.value = err.message || 'Failed to load bow setup';
  } finally {
    loading.value = false;
  }
};

const fetchSetupArrows = async () => {
  try {
    loadingArrows.value = true;
    const response = await api.get(`/bow-setups/${route.params.id}/arrows`);
    console.log('🔍 Fetched arrows response:', response);
    console.log('🔍 Response.arrows:', response.arrows);
    console.log('🔍 Response.arrows length:', response.arrows?.length || 0);
    
    if (bowSetup.value) {
      // Force reactivity by creating a new array reference
      const newArrows = response.arrows || [];
      bowSetup.value.arrows = [...newArrows];
      
      console.log('🔍 Bow setup arrows after assignment:', bowSetup.value.arrows);
      console.log('🔍 New arrows count:', bowSetup.value.arrows.length);
      
      // Force a reactive update
      nextTick(() => {
        console.log('🔍 After nextTick - arrows count:', bowSetup.value?.arrows?.length || 0);
      });
    }
  } catch (err) {
    console.error('Error fetching setup arrows:', err);
    
    // Handle auth errors for arrows endpoint too
    if (err.message.includes('401') || err.message.includes('Token is missing')) {
      console.log('Auth error fetching arrows, user needs to log in again');
      // Don't redirect here since this is a secondary request
      // Just set empty arrows array
      if (bowSetup.value) {
        bowSetup.value.arrows = [];
      }
    }
  } finally {
    loadingArrows.value = false;
  }
};

const navigateToArrowCalculator = () => {
  navigateTo({
    path: '/calculator',
    query: {
      bow_type: bowSetup.value.bow_type,
      draw_weight: bowSetup.value.draw_weight,
      draw_length: bowSetup.value.draw_length || 28,
      arrow_length: bowSetup.value.arrow_length,
      point_weight: bowSetup.value.point_weight,
      setupId: bowSetup.value.id
    }
  });
};

const openEditModal = () => {
  editingSetup.value = { ...bowSetup.value };
  isEditingSetup.value = true;
};

const closeEditModal = () => {
  isEditingSetup.value = false;
  editingSetup.value = null;
  editError.value = null;
};

const handleUpdateSetup = async (setupData) => {
  try {
    isSavingSetup.value = true;
    editError.value = null;
    
    const updated = await api.put(`/bow-setups/${bowSetup.value.id}`, setupData);
    bowSetup.value = { ...bowSetup.value, ...updated };
    closeEditModal();
  } catch (err) {
    console.error('Error updating bow setup:', err);
    editError.value = err.message || 'Failed to update bow setup';
  } finally {
    isSavingSetup.value = false;
  }
};

const openArrowSearchModal = () => {
  // Navigate to calculator page with this bow setup loaded for arrow selection
  navigateTo({
    path: '/calculator',
    query: {
      bow_type: bowSetup.value.bow_type,
      draw_weight: bowSetup.value.draw_weight,
      draw_length: bowSetup.value.draw_length || 28,
      arrow_length: bowSetup.value.arrow_length,
      point_weight: bowSetup.value.point_weight,
      setupId: bowSetup.value.id,
      returnTo: `/bow/${bowSetup.value.id}`
    }
  });
};


const removeArrowFromSetup = (setupArrowId) => {
  // Find the arrow setup to get details for the confirmation modal
  const arrowSetup = bowSetup.value?.arrows?.find(arrow => arrow.id === setupArrowId);
  if (arrowSetup) {
    arrowToDelete.value = { setupArrowId, arrowSetup };
    deleteArrowError.value = '';
  }
};

const confirmRemoveArrow = async () => {
  if (!arrowToDelete.value) return;
  
  try {
    deletingArrow.value = true;
    deleteArrowError.value = '';
    
    // Use the correct API endpoint for removing arrows from setup
    await api.delete(`/setup-arrows/${arrowToDelete.value.setupArrowId}`);
    await fetchSetupArrows();
    
    notifySuccess('Arrow removed successfully from bow setup');
    arrowToDelete.value = null;
  } catch (err) {
    console.error('Error removing arrow:', err);
    deleteArrowError.value = err.message || 'Failed to remove arrow';
  } finally {
    deletingArrow.value = false;
  }
};

const cancelRemoveArrow = () => {
  arrowToDelete.value = null;
  deleteArrowError.value = '';
};

const getArrowDisplayName = (arrowDeleteInfo) => {
  if (!arrowDeleteInfo?.arrowSetup) return 'Unknown Arrow';
  
  const arrow = arrowDeleteInfo.arrowSetup.arrow || arrowDeleteInfo.arrowSetup;
  const manufacturer = arrow.manufacturer || arrow.manufacturer_name || 'Unknown';
  const model = arrow.model_name || arrow.model || 'Unknown';
  const spine = arrow.spine || arrowDeleteInfo.arrowSetup.calculated_spine || '';
  
  return `${manufacturer} ${model}${spine ? ` (${spine} spine)` : ''}`;
};

const viewArrowDetails = (arrowIdOrArrow) => {
  // Handle both cases: direct ID number or arrow object
  const arrowId = typeof arrowIdOrArrow === 'number' ? arrowIdOrArrow : (arrowIdOrArrow.arrow_id || arrowIdOrArrow.id);
  
  // Navigate to arrow details with bow context
  navigateTo({
    path: `/arrows/${arrowId}`,
    query: {
      bowId: bowSetup.value.id,
      bowName: bowSetup.value.name,
      returnTo: `/bow/${bowSetup.value.id}`
    }
  });
};

const openEditArrowModal = (arrow) => {
  console.log('Opening edit arrow modal for:', arrow);
  console.log('bowSetup.value:', bowSetup.value);
  console.log('bowSetup.value.id:', bowSetup.value?.id);
  editingArrow.value = arrow;
  console.log('editingArrow.value set to:', editingArrow.value);
};

const handleUpdateArrow = async (updatedArrow) => {
  console.log('Handling arrow update:', updatedArrow);
  try {
    // Use the setup-arrows endpoint (the one that works with arrow setup ID)
    await api.put(`/setup-arrows/${editingArrow.value.id}`, {
      arrow_length: updatedArrow.arrow_length,
      point_weight: updatedArrow.point_weight,
      calculated_spine: updatedArrow.calculated_spine,
      nock_weight: updatedArrow.nock_weight,
      insert_weight: updatedArrow.insert_weight,
      bushing_weight: updatedArrow.bushing_weight,
      compatibility_score: updatedArrow.compatibility_score,
      notes: updatedArrow.notes
    });
    
    console.log('Arrow updated successfully');
    editingArrow.value = null;
    await fetchSetupArrows();
  } catch (err) {
    console.error('Error updating arrow configuration:', err);
    console.error('Error details:', err.response?.data || err.message);
    notifyError('Error updating arrow: ' + (err.response?.data?.error || err.message));
  }
};

const duplicateArrow = async (arrowSetup) => {
  console.log('🔄 Duplicate arrow function called with:', arrowSetup);
  
  // Check authentication first
  const token = process.client ? localStorage.getItem('token') : null;
  
  if (!token) {
    notifyError('Please log in to duplicate arrows. You need to be authenticated to perform this action.');
    return;
  }
  
  console.log('✅ Authentication check passed, proceeding with duplication');
  
  try {
    // Create a duplicate arrow configuration with the same settings
    // but allow the user to modify them before saving
    const duplicateData = {
      arrow_id: arrowSetup.arrow_id,
      arrow_length: arrowSetup.arrow_length,
      point_weight: arrowSetup.point_weight,
      calculated_spine: arrowSetup.calculated_spine, // Include the spine selection
      compatibility_score: arrowSetup.compatibility_score, // Include the match score
      nock_weight: arrowSetup.nock_weight || 10,
      insert_weight: arrowSetup.insert_weight || 0,
      bushing_weight: arrowSetup.bushing_weight || 0,
      notes: `Duplicate of ${arrowSetup.arrow?.manufacturer || 'Unknown'} ${arrowSetup.arrow?.model_name || 'Arrow'}`,
      allow_duplicate: true  // Allow creating duplicate even with same specs
    };
    
    console.log('🚀 Making API call to duplicate arrow:', arrowSetup.arrow?.manufacturer, arrowSetup.arrow?.model_name);
    console.log('📤 Duplicate data payload:', duplicateData);
    console.log('🎯 API endpoint:', `/bow-setups/${bowSetup.value.id}/arrows`);
    
    const response = await api.post(`/bow-setups/${bowSetup.value.id}/arrows`, duplicateData);
    
    console.log('📥 API response received:', response);
    
    // Add a small delay to ensure database is updated
    await new Promise(resolve => setTimeout(resolve, 500));
    
    await fetchSetupArrows();
    
    console.log('🔄 Setup arrows refreshed after duplication');
    
    // Show success message in console only (no popup)
    console.log('✅ Arrow duplicated successfully:', {
      manufacturer: arrowSetup.arrow?.manufacturer,
      model: arrowSetup.arrow?.model_name,
      spine: arrowSetup.calculated_spine,
      newId: response?.id
    });
    
    // Show brief success notification to user
    notifySuccess(`Arrow duplicated successfully! ${arrowSetup.arrow?.manufacturer || 'Arrow'} ${arrowSetup.arrow?.model_name || ''} has been added to your bow setup.`);
  } catch (err) {
    console.error('❌ Error duplicating arrow:', err);
    
    // Handle specific error cases
    if (err.message && (err.message.includes('401') || err.message.includes('Token is missing'))) {
      notifyError('Please log in to duplicate arrows. The duplicate function requires authentication.');
    } else if (err.message && err.message.includes('403')) {
      notifyError('You do not have permission to duplicate arrows in this bow setup.');  
    } else if (err.message && err.message.includes('404')) {
      notifyError('Bow setup or arrow not found. Please refresh the page and try again.');
    } else {
      notifyError('Error duplicating arrow: ' + (err.response?.data?.error || err.message));
    }
  }
};

// Equipment management handlers
const handleEquipmentUpdated = () => {
  // Refresh bow setup data if needed
  console.log('Equipment updated for bow setup');
};

// Use notification composable
const { notifySuccess, notifyError, notifyInfo, notifyWarning } = useNotifications()

const showNotification = (message, type = 'info') => {
  // Updated to use custom notifications instead of alert()
  switch (type) {
    case 'success':
      notifySuccess(message)
      break
    case 'error':
      notifyError(message)
      break
    case 'warning':
      notifyWarning(message)
      break
    default:
      notifyInfo(message)
      break
  }
};

// Helper functions
const getBowTypeClass = (type) => {
  const classes = {
    compound: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    recurve: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    traditional: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    barebow: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  };
  return classes[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
};

const getBowTypeIcon = (type) => {
  const icons = {
    compound: 'fas fa-cogs',
    recurve: 'fas fa-bullseye',
    traditional: 'fas fa-feather',
    barebow: 'fas fa-bow-arrow'
  };
  return icons[type] || 'fas fa-question-circle';
};

const formatBowType = (type) => {
  return type ? type.charAt(0).toUpperCase() + type.slice(1) : 'Unknown';
};

const getBowUsageArray = (usage) => {
  if (!usage) return [];
  if (Array.isArray(usage)) return usage;
  if (typeof usage === 'string') {
    try {
      return JSON.parse(usage);
    } catch {
      return usage.split(',').map(u => u.trim());
    }
  }
  return [];
};

const formatBowUsage = (usage) => {
  const labels = {
    target: 'Target',
    field: 'Field',
    '3d': '3D',
    hunting: 'Hunting',
    indoor: 'Indoor',
    outdoor: 'Outdoor'
  };
  return labels[usage.toLowerCase()] || usage;
};

const getUsageIcon = (usage) => {
  const icons = {
    target: 'fas fa-bullseye',
    field: 'fas fa-mountain',
    '3d': 'fas fa-cube',
    hunting: 'fas fa-crosshairs',
    indoor: 'fas fa-home',
    outdoor: 'fas fa-sun'
  };
  return icons[usage.toLowerCase()] || 'fas fa-tag';
};

// Lifecycle
onMounted(() => {
  fetchBowSetup();
});

// Define page meta to require authentication
definePageMeta({
  middleware: ['auth-check']
});
</script>