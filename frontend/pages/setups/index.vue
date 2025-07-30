
<template>
  <div class="container p-4 mx-auto">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">My Bow Setups</h1>
      <p class="text-gray-600 dark:text-gray-300">Manage your bow configurations and arrow setups</p>
    </div>

    <!-- Bow Setups Grid -->
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      <md-elevated-card v-for="setup in setups" :key="setup.id" class="cursor-pointer light-surface light-elevation">
        <div class="p-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ setup.name }}</h3>
              <p class="text-sm text-gray-600 dark:text-gray-300 capitalize">{{ setup.bow_type }}</p>
            </div>
          </div>
          
          <!-- Bow Specifications -->
          <div class="space-y-2 mb-4">
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
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ setup.point_weight }} gn ({{ setup.point_weight }} gr)</span>
            </div>
          </div>

          <!-- Bow Usage Tags -->
          <div v-if="setup.bow_usage" class="mb-4">
            <div class="flex flex-wrap gap-1">
              <span 
                v-for="usage in getBowUsageArray(setup.bow_usage)" 
                :key="usage"
                class="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full"
              >
                {{ usage }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-2 mt-4">
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
      <CustomButton @click="showCreateForm = true" variant="filled" class="bg-green-600 text-white hover:bg-green-700">
        <i class="fas fa-plus mr-2"></i>
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
            <label class="block mb-1">Point Weight</label>
            <input v-model="form.point_weight" type="number" step="0.5" min="40" class="w-full p-2 border rounded" required>
          </div>
          <div class="flex justify-end">
            <button type="button" @click="cancelForm" class="px-4 py-2 mr-2 text-gray-700 bg-gray-200 rounded">Cancel</button>
            <button type="submit" class="px-4 py-2 text-white bg-blue-500 rounded">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuth } from '~/composables/useAuth';

const { token } = useAuth();
const setups = ref([]);
const showCreateForm = ref(false);
const editingSetup = ref(null);

const form = ref({
  name: '',
  bow_type: 'compound',
  draw_weight: 70,
  draw_length: 29,
  arrow_length: 28.5,
  point_weight: 100,
  bow_usage: [],
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
    bow_usage: setup.bow_usage ? JSON.parse(setup.bow_usage) : []
  };
};

const deleteSetup = async (id) => {
  if (!confirm('Are you sure you want to delete this setup?')) return;

  try {
    const res = await fetch(`/api/bow-setups/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (res.ok) {
      fetchSetups();
    } else {
      console.error('Failed to delete setup');
    }
  } catch (err) {
    console.error('Failed to delete setup:', err);
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
  };
};
</script>
