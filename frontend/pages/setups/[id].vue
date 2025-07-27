
<template>
  <div class="container p-4 mx-auto">
    <div v-if="setup">
      <h1 class="mb-4 text-2xl font-bold">{{ setup.name }}</h1>
      <p><strong>Bow Type:</strong> {{ setup.bow_type }}</p>
      <p><strong>Draw Weight:</strong> {{ setup.draw_weight }}#</p>
      <p><strong>Draw Length:</strong> {{ setup.draw_length }}"</p>
      <p><strong>Arrow Length:</strong> {{ setup.arrow_length }}"</p>
      <p><strong>Point Weight:</strong> {{ setup.point_weight }}gr</p>
    </div>
    <div v-else>
      <p>Loading...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth } from '~/composables/useAuth';

const { token } = useAuth();
const route = useRoute();
const setup = ref(null);

const fetchSetup = async () => {
  try {
    const res = await fetch(`/api/bow-setups/${route.params.id}`,
    {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (res.ok) {
      setup.value = await res.json();
    } else {
      console.error('Failed to fetch setup');
    }
  } catch (err) {
    console.error('Failed to fetch setup:', err);
  }
};

onMounted(fetchSetup);
</script>
