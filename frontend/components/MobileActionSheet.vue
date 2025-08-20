<template>
  <!-- Action Sheet Backdrop -->
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="action-sheet-backdrop"
      :class="backdropClasses"
      @click="handleBackdropClick"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
    >
      <!-- Action Sheet Container -->
      <div
        ref="actionSheet"
        class="action-sheet-container"
        :class="containerClasses"
        @click.stop
      >
        <!-- Drag Handle -->
        <div class="drag-handle-container">
          <div class="drag-handle"></div>
        </div>

        <!-- Header Section -->
        <div v-if="title || subtitle || $slots.header" class="action-sheet-header">
          <slot name="header">
            <div class="text-center py-2">
              <h3 v-if="title" class="mobile-heading-3 text-gray-900 dark:text-gray-100">
                {{ title }}
              </h3>
              <p v-if="subtitle" class="mobile-body-small text-gray-500 dark:text-gray-400 mt-1">
                {{ subtitle }}
              </p>
            </div>
          </slot>
        </div>

        <!-- Content Section -->
        <div class="action-sheet-content" :class="contentClasses">
          <slot name="content">
            <!-- Default Actions List -->
            <div class="actions-list">
              <button
                v-for="(action, index) in actions"
                :key="action.id || index"
                class="action-item"
                :class="getActionClasses(action)"
                :disabled="action.disabled"
                @click="handleActionClick(action, index)"
              >
                <!-- Action Icon -->
                <div v-if="action.icon" class="action-icon" :class="getIconClasses(action)">
                  <i :class="action.icon"></i>
                </div>

                <!-- Action Content -->
                <div class="action-content">
                  <div class="action-label">{{ action.label }}</div>
                  <div v-if="action.description" class="action-description">
                    {{ action.description }}
                  </div>
                </div>

                <!-- Action Badge/Value -->
                <div v-if="action.badge || action.value" class="action-badge">
                  <span v-if="action.badge" class="badge" :class="getBadgeClasses(action)">
                    {{ action.badge }}
                  </span>
                  <span v-if="action.value" class="value">
                    {{ action.value }}
                  </span>
                </div>

                <!-- Action Arrow -->
                <div v-if="action.arrow !== false" class="action-arrow">
                  <i class="fas fa-chevron-right text-gray-400"></i>
                </div>
              </button>
            </div>
          </slot>
        </div>

        <!-- Footer Section -->
        <div v-if="$slots.footer || showCancel" class="action-sheet-footer">
          <slot name="footer">
            <button
              v-if="showCancel"
              class="cancel-button"
              @click="handleCancel"
            >
              {{ cancelText }}
            </button>
          </slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  actions: {
    type: Array,
    default: () => []
  },
  showCancel: {
    type: Boolean,
    default: true
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  persistent: {
    type: Boolean,
    default: false
  },
  swipeToClose: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'auto', // 'small', 'medium', 'large', 'auto'
    validator: (value) => ['small', 'medium', 'large', 'auto'].includes(value)
  },
  position: {
    type: String,
    default: 'bottom', // 'bottom', 'center'
    validator: (value) => ['bottom', 'center'].includes(value)
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'action', 'cancel', 'close'])

// Refs
const actionSheet = ref(null)
const touchStartY = ref(0)
const touchCurrentY = ref(0)
const isDragging = ref(false)
const startTime = ref(0)

// Computed
const backdropClasses = computed(() => ({
  'action-sheet-active': props.modelValue,
  'action-sheet-center': props.position === 'center'
}))

const containerClasses = computed(() => {
  const classes = ['action-sheet']
  
  // Size classes
  classes.push(`size-${props.size}`)
  
  // Position classes
  classes.push(`position-${props.position}`)
  
  return classes
})

const contentClasses = computed(() => {
  const classes = []
  
  // Scrollable content for large action sheets
  if (props.actions.length > 8 || props.size === 'large') {
    classes.push('scrollable')
  }
  
  return classes
})

// Methods
const getActionClasses = (action) => {
  const classes = ['action']
  
  if (action.type) {
    classes.push(`action-${action.type}`)
  }
  
  if (action.disabled) {
    classes.push('action-disabled')
  }
  
  if (action.destructive) {
    classes.push('action-destructive')
  }
  
  return classes
}

const getIconClasses = (action) => {
  const classes = []
  
  if (action.iconColor) {
    classes.push(`text-${action.iconColor}`)
  }
  
  return classes
}

const getBadgeClasses = (action) => {
  const classes = ['badge-default']
  
  if (action.badgeType) {
    classes.push(`badge-${action.badgeType}`)
  }
  
  return classes
}

const handleActionClick = (action, index) => {
  if (action.disabled) return
  
  emit('action', { action, index })
  
  // Auto-close unless action specifies otherwise
  if (action.keepOpen !== true) {
    close()
  }
}

const handleCancel = () => {
  emit('cancel')
  close()
}

const handleBackdropClick = () => {
  if (!props.persistent) {
    close()
  }
}

const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

// Touch/Swipe Methods
const handleTouchStart = (event) => {
  if (!props.swipeToClose || props.position !== 'bottom') return
  
  const touch = event.touches[0]
  touchStartY.value = touch.clientY
  touchCurrentY.value = touch.clientY
  isDragging.value = true
  startTime.value = Date.now()
}

const handleTouchMove = (event) => {
  if (!isDragging.value || !props.swipeToClose) return
  
  const touch = event.touches[0]
  const deltaY = touch.clientY - touchStartY.value
  
  // Only allow downward swipes
  if (deltaY < 0) return
  
  touchCurrentY.value = touch.clientY
  
  // Apply transform to action sheet
  if (actionSheet.value) {
    const translateY = Math.min(deltaY, 200)
    actionSheet.value.style.transform = `translateY(${translateY}px)`
    
    // Adjust opacity based on drag distance
    const opacity = Math.max(1 - (deltaY / 300), 0.3)
    actionSheet.value.style.opacity = opacity
  }
}

const handleTouchEnd = () => {
  if (!isDragging.value || !props.swipeToClose) return
  
  const deltaY = touchCurrentY.value - touchStartY.value
  const deltaTime = Date.now() - startTime.value
  const velocity = deltaY / deltaTime
  
  isDragging.value = false
  
  // Determine if should close
  const shouldClose = deltaY > 100 || (deltaY > 50 && velocity > 0.3)
  
  if (shouldClose) {
    close()
  } else if (actionSheet.value) {
    // Reset position
    actionSheet.value.style.transform = 'translateY(0)'
    actionSheet.value.style.opacity = '1'
  }
}

// Watch for changes
watch(() => props.modelValue, async (newValue) => {
  if (newValue) {
    // Disable body scroll when action sheet is open
    document.body.style.overflow = 'hidden'
    
    // Reset transform when opening
    await nextTick()
    if (actionSheet.value) {
      actionSheet.value.style.transform = 'translateY(0)'
      actionSheet.value.style.opacity = '1'
    }
  } else {
    // Re-enable body scroll
    document.body.style.overflow = ''
  }
})

// Cleanup on unmount
onUnmounted(() => {
  document.body.style.overflow = ''
})

// Expose methods
defineExpose({
  close
})
</script>

<style scoped>
/* Action Sheet Backdrop */
.action-sheet-backdrop {
  @apply fixed inset-0 z-50;
  @apply bg-black/50 backdrop-blur-sm;
  @apply flex items-end justify-center;
  @apply opacity-0 pointer-events-none;
  @apply transition-all duration-300 ease-out;
}

.action-sheet-backdrop.action-sheet-active {
  @apply opacity-100 pointer-events-auto;
}

.action-sheet-backdrop.action-sheet-center {
  @apply items-center;
}

/* Action Sheet Container */
.action-sheet-container {
  @apply w-full max-w-md mx-auto;
  @apply bg-white dark:bg-gray-800;
  @apply rounded-t-3xl;
  @apply shadow-2xl border-t border-gray-200 dark:border-gray-700;
  @apply transform translate-y-full;
  @apply transition-transform duration-300 ease-out;
  @apply max-h-[85vh] overflow-hidden;
  @apply relative;
}

.action-sheet-active .action-sheet-container {
  @apply translate-y-0;
}

/* Position variants */
.position-center .action-sheet-container {
  @apply rounded-3xl border;
  @apply transform scale-95 translate-y-0;
  @apply max-h-[80vh];
}

.action-sheet-active .position-center .action-sheet-container {
  @apply scale-100;
}

/* Size variants */
.size-small .action-sheet-container {
  @apply max-h-[40vh];
}

.size-medium .action-sheet-container {
  @apply max-h-[60vh];
}

.size-large .action-sheet-container {
  @apply max-h-[85vh];
}

.size-auto .action-sheet-container {
  @apply max-h-[85vh];
}

/* Drag Handle */
.drag-handle-container {
  @apply flex justify-center py-3;
  @apply bg-gray-50 dark:bg-gray-700;
  @apply rounded-t-3xl;
}

.drag-handle {
  @apply w-12 h-1 bg-gray-300 dark:bg-gray-600 rounded-full;
  @apply cursor-grab active:cursor-grabbing;
}

.position-center .drag-handle-container {
  @apply hidden;
}

/* Header */
.action-sheet-header {
  @apply px-6 py-4 border-b border-gray-200 dark:border-gray-700;
  @apply bg-white dark:bg-gray-800;
}

/* Content */
.action-sheet-content {
  @apply flex-1 overflow-hidden;
}

.action-sheet-content.scrollable {
  @apply overflow-y-auto;
}

/* Actions List */
.actions-list {
  @apply divide-y divide-gray-200 dark:divide-gray-700;
}

/* Action Item */
.action-item {
  @apply w-full flex items-center space-x-4;
  @apply px-6 py-4 text-left;
  @apply hover:bg-gray-50 dark:hover:bg-gray-700;
  @apply transition-colors duration-200;
  @apply min-h-[60px];
}

.action-item:disabled {
  @apply opacity-50 cursor-not-allowed;
  @apply hover:bg-transparent dark:hover:bg-transparent;
}

.action-item.action-destructive {
  @apply text-red-600 dark:text-red-400;
}

.action-item.action-destructive:hover {
  @apply bg-red-50 dark:bg-red-900/20;
}

/* Action Icon */
.action-icon {
  @apply flex-shrink-0 w-8 h-8;
  @apply flex items-center justify-center;
  @apply text-gray-500 dark:text-gray-400;
  @apply text-lg;
}

/* Action Content */
.action-content {
  @apply flex-1 min-w-0;
}

.action-label {
  @apply font-medium text-gray-900 dark:text-gray-100;
  @apply truncate;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.action-description {
  @apply text-gray-500 dark:text-gray-400;
  @apply mt-1 truncate;
  font-size: 0.75rem;
  line-height: 1rem;
}

/* Action Badge */
.action-badge {
  @apply flex-shrink-0;
}

.badge {
  @apply inline-flex items-center px-2 py-1;
  @apply text-xs font-medium rounded-full;
}

.badge-default {
  @apply bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300;
}

.badge-primary {
  @apply bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300;
}

.badge-success {
  @apply bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300;
}

.badge-warning {
  @apply bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300;
}

.badge-danger {
  @apply bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300;
}

.value {
  @apply text-gray-500 dark:text-gray-400;
  font-size: 0.75rem;
  line-height: 1rem;
}

/* Action Arrow */
.action-arrow {
  @apply flex-shrink-0 ml-2;
}

/* Footer */
.action-sheet-footer {
  @apply px-6 py-4 border-t border-gray-200 dark:border-gray-700;
  @apply bg-gray-50 dark:bg-gray-700;
}

.cancel-button {
  @apply w-full py-3 px-4;
  @apply bg-gray-200 dark:bg-gray-600;
  @apply text-gray-700 dark:text-gray-200;
  @apply font-medium rounded-xl;
  @apply hover:bg-gray-300 dark:hover:bg-gray-500;
  @apply transition-colors duration-200;
  min-height: 44px;
  min-width: 44px;
}

/* Mobile optimizations */
@media (max-width: 413px) {
  .action-sheet-container {
    @apply mx-0 rounded-t-2xl;
  }
  
  .action-item {
    @apply px-4 py-3 space-x-3;
    @apply min-h-[56px];
  }
  
  .action-icon {
    @apply w-6 h-6 text-base;
  }
}

/* Safe area handling */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .action-sheet-footer {
    padding-bottom: calc(1rem + env(safe-area-inset-bottom));
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .action-sheet-backdrop,
  .action-sheet-container {
    @apply transition-none;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .action-item {
    @apply border-b border-gray-400;
  }
  
  .drag-handle {
    @apply bg-gray-600;
  }
}
</style>