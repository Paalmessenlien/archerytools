<template>
  <div class="container mx-auto px-4 py-8 max-w-6xl">
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
      <CustomButton @click="navigateTo('/my-page')" variant="outlined">
        Back to My Setup
      </CustomButton>
    </div>

    <!-- Bow Setup Content -->
    <div v-else-if="bowSetup">
      <!-- Back Navigation -->
      <div class="mb-6">
        <CustomButton @click="navigateTo('/my-page')" variant="text" class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100">
          <i class="fas fa-arrow-left mr-2"></i>
          Back to My Setup
        </CustomButton>
      </div>

      <!-- Bow Header -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <div class="flex items-start justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">{{ bowSetup.name }}</h1>
            
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
          </div>

          <!-- Action Buttons -->
          <div class="flex space-x-3">
            <CustomButton
              @click="navigateToArrowCalculator"
              variant="filled"
              class="bg-green-600 text-white hover:bg-green-700"
            >
              <i class="fas fa-calculator mr-2"></i>
              Find Arrows
            </CustomButton>
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

      <!-- Specifications Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Draw Specifications -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            <i class="fas fa-bullseye mr-2 text-blue-600 dark:text-blue-400"></i>
            Draw Specifications
          </h2>
          <div class="space-y-3">
            <div class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
              <span class="text-gray-600 dark:text-gray-400">Draw Weight</span>
              <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.draw_weight }} lbs</span>
            </div>
            <div v-if="bowSetup.draw_length" class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
              <span class="text-gray-600 dark:text-gray-400">Draw Length</span>
              <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.draw_length }}"</span>
            </div>
            <div v-if="bowSetup.arrow_length" class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
              <span class="text-gray-600 dark:text-gray-400">Arrow Length</span>
              <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.arrow_length }}"</span>
            </div>
            <div v-if="bowSetup.point_weight" class="flex justify-between items-center py-2">
              <span class="text-gray-600 dark:text-gray-400">Point Weight</span>
              <span class="font-semibold text-gray-900 dark:text-gray-100">{{ bowSetup.point_weight }} gr</span>
            </div>
          </div>
        </div>

        <!-- Component Weights -->
        <div v-if="hasComponentWeights" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
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
      </div>

      <!-- Description -->
      <div v-if="bowSetup.description" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">Description</h2>
        <p class="text-gray-700 dark:text-gray-300">{{ bowSetup.description }}</p>
      </div>

      <!-- Selected Arrows Section -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            <i class="fas fa-location-arrow mr-2 text-orange-600 dark:text-orange-400"></i>
            Selected Arrows
          </h2>
          <CustomButton
            @click="openArrowSearchModal"
            variant="filled"
            class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
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
            :detailed="true"
            @remove-arrow="removeArrowFromSetup"
            @view-details="viewArrowDetails"
            @edit-arrow="openEditArrowModal"
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
      v-if="editingArrow"
      :arrow="editingArrow"
      :setupId="bowSetup.id"
      @save="handleUpdateArrow"
      @close="editingArrow = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth } from '~/composables/useAuth';
import { useApi } from '~/composables/useApi';

const route = useRoute();
const { user } = useAuth();
const api = useApi();

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
    
    const response = await api.get(`/bow-setups/${route.params.id}`);
    bowSetup.value = response;
    
    // Fetch arrows for this setup
    await fetchSetupArrows();
  } catch (err) {
    console.error('Error fetching bow setup:', err);
    error.value = err.message || 'Failed to load bow setup';
  } finally {
    loading.value = false;
  }
};

const fetchSetupArrows = async () => {
  try {
    loadingArrows.value = true;
    const response = await api.get(`/bow-setups/${route.params.id}/arrows`);
    if (bowSetup.value) {
      bowSetup.value.arrows = response;
    }
  } catch (err) {
    console.error('Error fetching setup arrows:', err);
  } finally {
    loadingArrows.value = false;
  }
};

const navigateToArrowCalculator = () => {
  navigateTo({
    path: '/',
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
  // Navigate to calculator page with this bow setup loaded
  navigateToArrowCalculator();
};

const handleArrowSelection = async (arrow) => {
  try {
    await api.post(`/bow-setups/${bowSetup.value.id}/arrows`, {
      arrow_id: arrow.id,
      arrow_length: bowSetup.value.arrow_length || 28,
      point_weight: bowSetup.value.point_weight || 100
    });
    
    showArrowSearch.value = false;
    await fetchSetupArrows();
  } catch (err) {
    console.error('Error adding arrow to setup:', err);
  }
};

const removeArrowFromSetup = async ({ setupId, arrowId }) => {
  try {
    await api.delete(`/bow-setups/${setupId}/arrows/${arrowId}`);
    await fetchSetupArrows();
  } catch (err) {
    console.error('Error removing arrow:', err);
  }
};

const viewArrowDetails = (arrow) => {
  navigateTo(`/arrows/${arrow.arrow_id || arrow.id}`);
};

const openEditArrowModal = (arrow) => {
  editingArrow.value = arrow;
};

const handleUpdateArrow = async (updatedArrow) => {
  try {
    await api.put(`/bow-setups/${bowSetup.value.id}/arrows/${updatedArrow.arrow_id}`, {
      arrow_length: updatedArrow.arrow_length,
      point_weight: updatedArrow.point_weight
    });
    
    editingArrow.value = null;
    await fetchSetupArrows();
  } catch (err) {
    console.error('Error updating arrow configuration:', err);
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
</script>