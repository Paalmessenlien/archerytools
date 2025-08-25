<template>
  <Teleport to="body">
    <div :class="containerClasses">
      <TransitionGroup
        name="notification"
        tag="div"
        class="notification-list"
      >
        <div
          v-for="notification in activeNotifications"
          :key="notification.id"
          :class="getNotificationClasses(notification)"
          @click="handleNotificationClick(notification)"
        >
          <!-- Notification Content -->
          <div class="notification-content">
            <!-- Icon -->
            <div class="notification-icon">
              <i :class="getNotificationIcon(notification.type)"></i>
            </div>
            
            <!-- Text Content -->
            <div class="notification-text">
              <div v-if="notification.title" class="notification-title">
                {{ notification.title }}
              </div>
              <div class="notification-message">
                {{ notification.message }}
              </div>
            </div>
            
            <!-- Actions -->
            <div v-if="notification.actions && notification.actions.length" class="notification-actions">
              <button
                v-for="action in notification.actions"
                :key="action.label"
                :class="getActionClasses(action)"
                @click.stop="handleActionClick(action, notification)"
              >
                {{ action.label }}
              </button>
            </div>
            
            <!-- Close Button -->
            <button
              class="notification-close"
              @click.stop="dismissNotification(notification.id)"
              aria-label="Close notification"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <!-- Progress Bar for timed notifications -->
          <div
            v-if="!notification.persistent && notification.duration"
            class="notification-progress"
            :style="getProgressStyle(notification)"
          ></div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch, onUnmounted } from 'vue'
import { useGlobalNotifications } from '@/composables/useNotificationSystem'

const props = withDefaults(defineProps<{
  position?: string
  maxWidth?: string
  zIndex?: number
}>(), {
  position: 'top-right',
  maxWidth: '400px',
  zIndex: 1000
})

// Use global notification system
const {
  activeNotifications,
  dismissNotification,
  getNotificationIcon
} = useGlobalNotifications()

// Progress tracking for timed notifications
const progressTimers = ref(new Map())

// Computed classes
const containerClasses = computed(() => {
  const baseClasses = 'notification-container fixed z-50'
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4', 
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
  }
  
  return `${baseClasses} ${positionClasses[props.position]}`
})

// Notification styling
const getNotificationClasses = (notification) => {
  const baseClasses = 'notification-item mb-3 rounded-lg shadow-lg backdrop-filter backdrop-blur-sm border cursor-pointer transition-all duration-300 ease-in-out transform hover:scale-105'
  const typeClasses = {
    success: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200',
    error: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200',
    warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200',
    info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'
  }
  
  return `${baseClasses} ${typeClasses[notification.type] || typeClasses.info}`
}

const getActionClasses = (action) => {
  const baseClasses = 'px-3 py-1 text-xs font-medium rounded transition-colors mr-2 last:mr-0'
  const styleClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white'
  }
  
  return `${baseClasses} ${styleClasses[action.style] || styleClasses.secondary}`
}

// Progress bar styling for timed notifications
const getProgressStyle = (notification) => {
  const elapsed = Date.now() - notification.timestamp
  const progress = Math.max(0, 100 - (elapsed / notification.duration) * 100)
  
  return {
    width: `${progress}%`,
    backgroundColor: getProgressColor(notification.type)
  }
}

const getProgressColor = (type) => {
  const colors = {
    success: '#10b981',
    error: '#ef4444', 
    warning: '#f59e0b',
    info: '#3b82f6'
  }
  return colors[type] || colors.info
}

// Event handlers
const handleNotificationClick = (notification) => {
  if (!notification.persistent && !notification.actions?.length) {
    dismissNotification(notification.id)
  }
}

const handleActionClick = (action, notification) => {
  action.handler()
  
  // Auto-dismiss after action unless it's persistent
  if (!notification.persistent) {
    dismissNotification(notification.id)
  }
}
</script>

<style scoped>
.notification-container {
  pointer-events: none;
  max-width: v-bind('props.maxWidth');
  z-index: v-bind('props.zIndex');
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.notification-item {
  pointer-events: auto;
  position: relative;
  overflow: hidden;
  min-width: 300px;
  max-width: 100%;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  gap: 0.75rem;
}

.notification-icon {
  flex-shrink: 0;
  font-size: 1.25rem;
  margin-top: 0.125rem;
}

.notification-text {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
  line-height: 1.25;
}

.notification-message {
  font-size: 0.875rem;
  line-height: 1.4;
  word-wrap: break-word;
}

.notification-actions {
  display: flex;
  align-items: center;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.notification-close {
  flex-shrink: 0;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  opacity: 0.7;
  background: transparent;
  border: none;
  cursor: pointer;
  color: inherit;
}

.notification-close:hover {
  opacity: 1;
  background-color: rgba(0, 0, 0, 0.1);
}

.notification-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  transition: width 0.1s linear;
  border-radius: 0 0 0.5rem 0.5rem;
}

/* Transition animations */
.notification-enter-active {
  transition: all 0.3s ease-out;
}

.notification-leave-active {
  transition: all 0.3s ease-in;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.notification-move {
  transition: transform 0.3s ease;
}

/* Responsive design */
@media (max-width: 640px) {
  .notification-container {
    left: 1rem !important;
    right: 1rem !important;
    transform: none !important;
    max-width: none;
  }
  
  .notification-item {
    min-width: 0;
  }
  
  .notification-content {
    padding: 0.75rem;
  }
  
  .notification-actions {
    margin-top: 0.75rem;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .notification-actions button {
    width: 100%;
    margin-right: 0;
  }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .notification-close:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
}
</style>