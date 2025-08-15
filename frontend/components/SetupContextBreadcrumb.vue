<template>
  <nav class="flex" aria-label="Breadcrumb">
    <ol class="inline-flex items-center space-x-1 md:space-x-3">
      <!-- Home -->
      <li class="inline-flex items-center">
        <NuxtLink
          to="/"
          class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-blue-600 dark:text-gray-400 dark:hover:text-white"
        >
          <i class="fas fa-home mr-1"></i>
          Home
        </NuxtLink>
      </li>
      
      <!-- My Setups -->
      <li>
        <div class="flex items-center">
          <i class="fas fa-chevron-right text-gray-400 mx-1"></i>
          <NuxtLink
            to="/my-setup"
            class="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 md:ml-2 dark:text-gray-400 dark:hover:text-white"
          >
            My Setups
          </NuxtLink>
        </div>
      </li>
      
      <!-- Bow Setup -->
      <li>
        <div class="flex items-center">
          <i class="fas fa-chevron-right text-gray-400 mx-1"></i>
          <NuxtLink
            :to="`/setups/${bowSetup.id}`"
            class="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 md:ml-2 dark:text-gray-400 dark:hover:text-white"
          >
            {{ bowSetup.name }}
          </NuxtLink>
        </div>
      </li>
      
      <!-- Arrows -->
      <li>
        <div class="flex items-center">
          <i class="fas fa-chevron-right text-gray-400 mx-1"></i>
          <NuxtLink
            :to="`/setups/${bowSetup.id}?tab=arrows`"
            class="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 md:ml-2 dark:text-gray-400 dark:hover:text-white"
          >
            <i class="fas fa-bullseye mr-1"></i>
            Arrows
          </NuxtLink>
        </div>
      </li>
      
      <!-- Current Arrow -->
      <li aria-current="page">
        <div class="flex items-center">
          <i class="fas fa-chevron-right text-gray-400 mx-1"></i>
          <span class="ml-1 text-sm font-medium text-gray-500 md:ml-2 dark:text-gray-400">
            {{ arrowName }}
          </span>
        </div>
      </li>
    </ol>
  </nav>
</template>

<script setup>
defineProps({
  bowSetup: {
    type: Object,
    required: true
  },
  arrowName: {
    type: String,
    required: true
  }
})
</script>