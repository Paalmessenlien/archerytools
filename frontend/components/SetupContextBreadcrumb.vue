<template>
  <nav class="flex" aria-label="Breadcrumb">
    <ol class="inline-flex items-center space-x-1 md:space-x-3">
      <!-- Bow Setup -->
      <li class="inline-flex items-center">
        <NuxtLink
          :to="`/setups/${bowSetup.id}`"
          class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-blue-600 dark:text-gray-400 dark:hover:text-white truncate max-w-32 sm:max-w-48 md:max-w-none"
          :title="bowSetup.name"
        >
          <i class="fas fa-crosshairs mr-1 flex-shrink-0 hidden md:inline-block"></i>
          <span class="truncate">{{ bowSetup.name }}</span>
        </NuxtLink>
      </li>
      
      <!-- Arrows -->
      <li>
        <div class="flex items-center">
          <i class="fas fa-chevron-right text-gray-400 mx-1 flex-shrink-0"></i>
          <NuxtLink
            :to="`/setups/${bowSetup.id}?tab=arrows`"
            class="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 md:ml-2 dark:text-gray-400 dark:hover:text-white"
          >
            <i class="fas fa-bullseye mr-1 hidden md:inline-block"></i>
            Arrows
          </NuxtLink>
        </div>
      </li>
      
      <!-- Current Arrow -->
      <li aria-current="page">
        <div class="flex items-center">
          <i class="fas fa-chevron-right text-gray-400 mx-1 flex-shrink-0"></i>
          <span class="ml-1 text-sm font-medium text-gray-500 md:ml-2 dark:text-gray-400 truncate max-w-32 sm:max-w-48 md:max-w-none" :title="arrowName">
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