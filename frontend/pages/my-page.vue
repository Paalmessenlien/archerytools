<template>
  <div class="card p-6">
    <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">My Page</h2>

    <div v-if="user">
      <p class="text-gray-700 dark:text-gray-300 mb-2">
        Welcome, <span class="font-medium">{{ user.name || user.email }}</span>!
      </p>
      <p v-if="user.email" class="text-gray-600 dark:text-gray-400 mb-4">
        Email: {{ user.email }}
      </p>
      <CustomButton
        @click="logout"
        variant="outlined"
        class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900"
      >
        Logout
      </CustomButton>
    </div>
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
import { useAuth } from '~/composables/useAuth';

const { user, logout, loginWithGoogle } = useAuth();

// Ensure user data is fetched on page load if not already present
// This is important for direct access to /my-page
onMounted(() => {
  if (!user.value) {
    // fetchUser is already called in default.vue layout onMounted
    // but we can add a check here if this page is accessed directly
    // and the layout's onMounted hasn't completed yet or if the token was just set.
    // For simplicity, we rely on the layout's fetchUser for initial load.
    // If a refresh issue occurs, consider adding fetchUser() here as well.
  }
});

definePageMeta({
  middleware: [async (to, from) => {
    const { user, fetchUser } = useAuth();
    if (!user.value) {
      await fetchUser(); // Attempt to fetch user if not already loaded
      if (!user.value) {
        return navigateTo('/'); // Redirect to home if still not logged in
      }
    }
  }]
});
</script>