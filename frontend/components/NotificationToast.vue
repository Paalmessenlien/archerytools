<template>
  <div class="fixed bottom-4 right-4 z-50 transition-all duration-300">
    <div
      class="p-4 rounded-lg shadow-lg max-w-sm flex items-center"
      :class="getNotificationClasses(type)"
    >
      <i :class="getNotificationIcon(type)" class="mr-3"></i>
      <span class="flex-1">{{ message }}</span>
      <button @click="$emit('close')" class="ml-4 opacity-70 hover:opacity-100">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'success'
  }
})

defineEmits(['close'])

const getNotificationClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-green-600 text-white'
    case 'error':
      return 'bg-red-600 text-white'
    case 'warning':
      return 'bg-yellow-600 text-white'
    default:
      return 'bg-blue-600 text-white'
  }
}

const getNotificationIcon = (type) => {
  switch (type) {
    case 'success':
      return 'fas fa-check-circle'
    case 'error':
      return 'fas fa-exclamation-circle'
    case 'warning':
      return 'fas fa-exclamation-triangle'
    default:
      return 'fas fa-info-circle'
  }
}
</script>