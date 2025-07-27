
<template>
  <div class="container p-4 mx-auto">
    <h1 class="mb-4 text-2xl font-bold">My Bow Setups</h1>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div v-for="setup in setups" :key="setup.id" class="p-4 bg-white rounded-lg shadow-md">
        <h2 class="text-xl font-bold">{{ setup.name }}</h2>
        <p><strong>Bow Type:</strong> {{ setup.bow_type }}</p>
        <p><strong>Draw Weight:</strong> {{ setup.draw_weight }}#</p>
        <p><strong>Draw Length:</strong> {{ setup.draw_length }}"</p>
        <div class="flex justify-end mt-4">
          <button @click="editSetup(setup)" class="px-4 py-2 mr-2 text-white bg-blue-500 rounded">Edit</button>
          <button @click="deleteSetup(setup.id)" class="px-4 py-2 text-white bg-red-500 rounded">Delete</button>
        </div>
      </div>
    </div>
    <div class="mt-8">
      <button @click="showCreateForm = true" class="px-4 py-2 text-white bg-green-500 rounded">Create New Setup</button>
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
            <input v-model="form.draw_weight" type="number" class="w-full p-2 border rounded" required>
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
            <label class="block mb-1">Point Weight</label>
            <input v-model="form.point_weight" type="number" class="w-full p-2 border rounded" required>
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
});

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
  form.value = { ...setup };
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
    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify(form.value),
    });

    if (res.ok) {
      fetchSetups();
      cancelForm();
    } else {
      console.error('Failed to save setup');
    }
  } catch (err) {
    console.error('Failed to save setup:', err);
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
  };
};
</script>
