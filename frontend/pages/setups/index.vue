
<template>
  <div class="container p-4 mx-auto">
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
            <span class="text-sm">{{ notification.message }}</span>
          </div>
          <button @click="hideNotification" class="ml-4 opacity-70 hover:opacity-100">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="mb-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">My Bow Setups</h1>
      <p class="text-gray-600 dark:text-gray-300">Manage your bow configurations and arrow setups</p>
    </div>

    <!-- Bow Setups Grid -->
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      <md-elevated-card v-for="setup in setups" :key="setup.id" class="cursor-pointer light-surface light-elevation">
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ setup.name }}</h3>
              <p class="text-sm text-gray-600 capitalize dark:text-gray-300">{{ setup.bow_type }}</p>
            </div>
          </div>
          
          <!-- Bow Specifications -->
          <div class="mb-4 space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-300">Draw Weight:</span>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ setup.draw_weight }}#</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-300">Draw Length:</span>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ setup.draw_length }}"</span>
            </div>
            <div v-if="setup.arrow_length" class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-300">Arrow Length:</span>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ setup.arrow_length }}"</span>
            </div>
            <div v-if="setup.point_weight" class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-300">Point Weight:</span>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ setup.point_weight }} gn</span>
            </div>
            
            <!-- Bow Brand and Model Display -->
            <div v-if="setup.riser_brand && (setup.bow_type === 'recurve' || setup.bow_type === 'traditional')" class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-300">Riser:</span>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ setup.riser_brand }} {{ setup.riser_model }}</span>
            </div>
            <div v-if="setup.limb_brand && (setup.bow_type === 'recurve' || setup.bow_type === 'traditional')" class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-300">Limbs:</span>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ setup.limb_brand }} {{ setup.limb_model }}</span>
            </div>
            <div v-if="setup.compound_brand && setup.bow_type === 'compound'" class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-300">Bow:</span>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ setup.compound_brand }} {{ setup.compound_model }}</span>
            </div>
            <div v-if="setup.description" class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-300">Notes:</span>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ setup.description }}</span>
            </div>
          </div>

          <!-- Bow Usage Tags -->
          <div v-if="setup.bow_usage" class="mb-4">
            <div class="flex flex-wrap gap-1">
              <span 
                v-for="usage in getBowUsageArray(setup.bow_usage)" 
                :key="usage"
                class="px-2 py-1 text-xs text-blue-800 bg-blue-100 rounded-full dark:bg-blue-900 dark:text-blue-200"
              >
                {{ usage }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col sm:flex-row gap-2 sm:justify-end mt-4">
            <CustomButton @click="editSetup(setup)" variant="outlined" size="small">
              Edit
            </CustomButton>
            <CustomButton @click="deleteSetup(setup.id)" variant="outlined" size="small" class="text-red-600 border-red-300 hover:bg-red-50">
              Delete
            </CustomButton>
          </div>
        </div>
      </md-elevated-card>
    </div>

    <!-- Create New Setup Button -->
    <div class="mt-8">
      <CustomButton @click="showCreateForm = true" variant="filled" class="text-white bg-green-600 hover:bg-green-700">
        <i class="mr-2 fas fa-plus"></i>
        Create New Setup
      </CustomButton>
    </div>

    <div v-if="showCreateForm || editingSetup" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div class="p-8 bg-white rounded-lg shadow-md">
        <h2 class="mb-4 text-2xl font-bold">{{ editingSetup ? 'Edit' : 'Create' }} Bow Setup</h2>
        <form @submit.prevent="saveSetup">
          <div class="mb-4">
            <label class="block mb-1">Name</label>
            <input v-model="form.name" type="text" class="w-full p-2 border rounded" required>
          </div>
          <div class="mb-4">
            <label class="block mb-1">Bow Type</label>
            <select v-model="form.bow_type" class="w-full p-2 border rounded" required>
              <option value="compound">Compound</option>
              <option value="recurve">Recurve</option>
              <option value="longbow">Longbow</option>
              <option value="traditional">Traditional</option>
            </select>
          </div>
          <div class="mb-4">
            <label class="block mb-1">Draw Weight</label>
            <input v-model="form.draw_weight" type="number" step="0.5" class="w-full p-2 border rounded" required>
          </div>
          <div class="mb-4">
            <label class="block mb-1">Draw Length</label>
            <input v-model="form.draw_length" type="number" step="0.1" class="w-full p-2 border rounded" required>
          </div>
          <div class="mb-4">
            <label class="block mb-1">Arrow Length</label>
            <input v-model="form.arrow_length" type="number" step="0.1" class="w-full p-2 border rounded" required>
          </div>
          <div class="mb-4">
            <label class="block mb-1">Bow Usage</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="usage in usageOptions"
                :key="usage"
                type="button"
                @click="toggleUsage(usage)"
                :class="[
                  'px-3 py-1 text-sm rounded-full border transition-colors',
                  isUsageSelected(usage)
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                ]"
              >
                {{ usage }}
              </button>
            </div>
          </div>
          <div class="mb-4">
            <label class="block mb-1">Point Weight (grains)</label>
            <input v-model="form.point_weight" type="number" step="0.5" min="40" class="w-full p-2 border rounded" required>
          </div>
          
          
          <!-- Bow Brand and Model Information -->
          <div class="mb-4" v-if="form.bow_type === 'recurve' || form.bow_type === 'traditional'">
            <label class="block mb-1">Riser Brand</label>
            <select v-model="form.riser_brand" class="w-full p-2 border rounded">
              <option value="">Select Riser Brand</option>
              <option value="Hoyt">Hoyt</option>
              <option value="Win&Win">Win&Win</option>
              <option value="Sebastian Flute">Sebastian Flute</option>
              <option value="Gillo">Gillo</option>
              <option value="Samick">Samick</option>
              <option value="KTA">KTA</option>
              <option value="Border">Border</option>
              <option value="Dryad">Dryad</option>
              <option value="Bear">Bear</option>
              <option value="Martin">Martin</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div class="mb-4" v-if="form.bow_type === 'recurve' || form.bow_type === 'traditional'">
            <label class="block mb-1">Riser Model</label>
            <input v-model="form.riser_model" type="text" class="w-full p-2 border rounded" placeholder="e.g., Satori, Formula Xi, etc.">
          </div>
          <div class="mb-4" v-if="form.bow_type === 'recurve' || form.bow_type === 'traditional'">
            <label class="block mb-1">Limb Brand</label>
            <select v-model="form.limb_brand" class="w-full p-2 border rounded">
              <option value="">Select Limb Brand</option>
              <option value="Uukha">Uukha</option>
              <option value="Win&Win">Win&Win</option>
              <option value="Hoyt">Hoyt</option>
              <option value="KTA">KTA</option>
              <option value="SF Archery">SF Archery</option>
              <option value="Border">Border</option>
              <option value="Samick">Samick</option>
              <option value="Bear">Bear</option>
              <option value="Martin">Martin</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div class="mb-4" v-if="form.bow_type === 'recurve' || form.bow_type === 'traditional'">
            <label class="block mb-1">Limb Model</label>
            <input v-model="form.limb_model" type="text" class="w-full p-2 border rounded" placeholder="e.g., VX1000, Storm, etc.">
          </div>
          <div class="mb-4" v-if="form.bow_type === 'compound'">
            <label class="block mb-1">Compound Bow Brand</label>
            <select v-model="form.compound_brand" class="w-full p-2 border rounded">
              <option value="">Select Compound Brand</option>
              <option value="Mathews">Mathews</option>
              <option value="Hoyt">Hoyt</option>
              <option value="PSE">PSE</option>
              <option value="Bowtech">Bowtech</option>
              <option value="Bear">Bear</option>
              <option value="Prime">Prime</option>
              <option value="Elite">Elite</option>
              <option value="Mission">Mission</option>
              <option value="Diamond">Diamond</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div class="mb-4" v-if="form.bow_type === 'compound'">
            <label class="block mb-1">Compound Bow Model</label>
            <input v-model="form.compound_model" type="text" class="w-full p-2 border rounded" placeholder="e.g., V3X 33, RX-7 Ultra, etc.">
          </div>
          
          <!-- Description -->
          <div class="mb-4">
            <label class="block mb-1">Description</label>
            <textarea v-model="form.description" class="w-full p-2 border rounded" rows="3" placeholder="Optional notes about this bow setup"></textarea>
          </div>
          
          <div class="flex justify-end">
            <button type="button" @click="cancelForm" class="px-4 py-2 mr-2 text-gray-700 bg-gray-200 rounded">Cancel</button>
            <button type="submit" class="px-4 py-2 text-white bg-blue-500 rounded">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="confirmation.show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-lg text-center">
        <div class="mb-4">
          <i class="fas fa-exclamation-triangle text-yellow-500 text-4xl mb-2"></i>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Confirm Deletion</h3>
        </div>
        <p class="text-gray-700 dark:text-gray-300 mb-6">
          {{ confirmation.message }}
        </p>
        <div class="flex justify-center space-x-4">
          <button
            @click="hideConfirmation"
            class="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete"
            class="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
    <!-- End of Confirmation Modal -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuth } from '~/composables/useAuth';

const { token } = useAuth();
const setups = ref([]);
const showCreateForm = ref(false);
const editingSetup = ref(null);

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success' // 'success', 'error', 'warning'
});

// Confirmation state
const confirmation = ref({
  show: false,
  message: '',
  setupId: null
});

const form = ref({
  name: '',
  bow_type: 'compound',
  draw_weight: 70,
  draw_length: 29,
  arrow_length: 28.5,
  point_weight: 100,
  bow_usage: [],
  description: '',
  riser_brand: '',
  riser_model: '',
  limb_brand: '',
  limb_model: '',
  compound_brand: '',
  compound_model: '',
});

const usageOptions = ['Target', 'Field', '3D', 'Hunting'];

const fetchSetups = async () => {
  try {
    const res = await fetch('/api/bow-setups', {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (res.ok) {
      setups.value = await res.json();
    } else {
      console.error('Failed to fetch setups');
    }
  } catch (err) {
    console.error('Failed to fetch setups:', err);
  }
};

onMounted(fetchSetups);

const editSetup = (setup) => {
  editingSetup.value = setup;
  form.value = { 
    ...setup,
    // Ensure numeric fields are properly converted
    draw_weight: parseFloat(setup.draw_weight) || 70,
    draw_length: parseFloat(setup.draw_length) || 29,
    arrow_length: parseFloat(setup.arrow_length) || 28.5,
    point_weight: parseFloat(setup.point_weight) || 100,
    description: setup.description || '',
    riser_brand: setup.riser_brand || '',
    riser_model: setup.riser_model || '',
    limb_brand: setup.limb_brand || '',
    limb_model: setup.limb_model || '',
    compound_brand: setup.compound_brand || '',
    compound_model: setup.compound_model || '',
    bow_usage: setup.bow_usage ? JSON.parse(setup.bow_usage) : []
  };
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

// Confirmation helper functions
const showDeleteConfirmation = (setupId) => {
  confirmation.value = {
    show: true,
    message: 'Are you sure you want to delete this setup?',
    setupId
  };
};

const hideConfirmation = () => {
  confirmation.value = {
    show: false,
    message: '',
    setupId: null
  };
};

const confirmDelete = async () => {
  const setupId = confirmation.value.setupId;
  hideConfirmation();
  await performDelete(setupId);
};

const deleteSetup = async (id) => {
  showDeleteConfirmation(id);
};

const performDelete = async (id) => {
  try {
    const res = await fetch(`/api/bow-setups/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (res.ok) {
      fetchSetups();
      showNotification('Bow setup deleted successfully');
    } else {
      console.error('Failed to delete setup');
      showNotification('Failed to delete setup', 'error');
    }
  } catch (err) {
    console.error('Failed to delete setup:', err);
    showNotification('Failed to delete setup', 'error');
  }
};

const saveSetup = async () => {
  const url = editingSetup.value ? `/api/bow-setups/${editingSetup.value.id}` : '/api/bow-setups';
  const method = editingSetup.value ? 'PUT' : 'POST';

  try {
    const setupData = {
      ...form.value,
      // Convert numeric fields to proper numbers
      draw_weight: parseFloat(form.value.draw_weight),
      draw_length: parseFloat(form.value.draw_length),
      arrow_length: parseFloat(form.value.arrow_length),
      point_weight: parseFloat(form.value.point_weight),
      description: form.value.description || '',
      riser_brand: form.value.riser_brand || '',
      riser_model: form.value.riser_model || '',
      limb_brand: form.value.limb_brand || '',
      limb_model: form.value.limb_model || '',
      compound_brand: form.value.compound_brand || '',
      compound_model: form.value.compound_model || '',
      bow_usage: JSON.stringify(form.value.bow_usage)
    };
    
    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify(setupData),
    });

    if (res.ok) {
      fetchSetups();
      cancelForm();
    } else {
      const errorText = await res.text();
      console.error('Failed to save setup:', errorText);
    }
  } catch (err) {
    console.error('Failed to save setup:', err);
  }
};

const toggleUsage = (usage) => {
  const index = form.value.bow_usage.indexOf(usage);
  if (index > -1) {
    form.value.bow_usage.splice(index, 1);
  } else {
    form.value.bow_usage.push(usage);
  }
};

const isUsageSelected = (usage) => {
  return form.value.bow_usage.includes(usage);
};

const getBowUsageArray = (usageString) => {
  if (!usageString) return [];
  try {
    return JSON.parse(usageString);
  } catch {
    return [];
  }
};

const cancelForm = () => {
  showCreateForm.value = false;
  editingSetup.value = null;
  form.value = {
    name: '',
    bow_type: 'compound',
    draw_weight: 70,
    draw_length: 29,
    arrow_length: 28.5,
    point_weight: 100,
    bow_usage: [],
    description: '',
    riser_brand: '',
    riser_model: '',
    limb_brand: '',
    limb_model: '',
    compound_brand: '',
    compound_model: '',
  };
};
</script>
