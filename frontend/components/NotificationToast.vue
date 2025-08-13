<template>
  <Transition name="toast">
    <div
      v-if="visible"
      :class="toastClasses"
      class="fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm"
    >
      <div class="flex items-start">
        <div :class="iconClasses" class="mr-3 mt-0.5">
          <i :class="iconType"></i>
        </div>
        <div class="flex-1 min-w-0">
          <h4 v-if="title" class="text-sm font-medium mb-1">{{ title }}</h4>
          <p class="text-sm">{{ message }}</p>
        </div>
        <button
          @click="close"
          class="ml-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <i class="fas fa-times text-sm"></i>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: value => ['success', 'error', 'warning', 'info'].includes(value)
  },
  title: String,
  message: {
    type: String,
    required: true
  },
  duration: {
    type: Number,
    default: 5000
  },
  persistent: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const visible = ref(false)

const toastClasses = computed(() => ({
  'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-800 dark:text-green-200': props.type === 'success',
  'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200': props.type === 'error',
  'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200': props.type === 'warning',
  'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200': props.type === 'info'
}))

const iconClasses = computed(() => ({
  'text-green-600 dark:text-green-400': props.type === 'success',
  'text-red-600 dark:text-red-400': props.type === 'error',
  'text-yellow-600 dark:text-yellow-400': props.type === 'warning',
  'text-blue-600 dark:text-blue-400': props.type === 'info'
}))

const iconType = computed(() => ({
  'fas fa-check-circle': props.type === 'success',
  'fas fa-exclamation-circle': props.type === 'error',
  'fas fa-exclamation-triangle': props.type === 'warning',
  'fas fa-info-circle': props.type === 'info'
}[props.type]))

const close = () => {
  visible.value = false
  setTimeout(() => emit('close'), 300) // Wait for transition
}

onMounted(() => {
  visible.value = true
  
  if (!props.persistent && props.duration > 0) {
    setTimeout(close, props.duration)
  }
})
</script>

<style scoped>
.toast-enter-active {
  transition: all 0.3s ease-out;
}

.toast-leave-active {
  transition: all 0.3s ease-in;
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>