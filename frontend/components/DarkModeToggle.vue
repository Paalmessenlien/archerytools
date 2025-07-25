<template>
  <md-outlined-button @click="toggleDarkMode" class="dark-mode-toggle">
    <i :class="isDarkMode ? 'fas fa-sun' : 'fas fa-moon'" style="margin-right: 6px;"></i>
    {{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}
  </md-outlined-button>
</template>

<script setup>
const { isDarkMode, toggleDarkMode } = useDarkMode()
</script>

<style scoped>
.dark-mode-toggle {
  transition: all 0.3s ease;
}
</style>