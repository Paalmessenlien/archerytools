/**
 * Reusable Notification System Composable
 * Provides standardized notification functionality across the entire system
 */

import { ref, reactive, computed, nextTick } from 'vue'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: string
  type: NotificationType
  title?: string
  message: string
  duration?: number
  persistent?: boolean
  actions?: NotificationAction[]
  timestamp: number
  show: boolean
}

export interface NotificationAction {
  label: string
  handler: () => void
  style?: 'primary' | 'secondary' | 'danger'
}

export interface NotificationOptions {
  title?: string
  duration?: number
  persistent?: boolean
  actions?: NotificationAction[]
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
}

export const useNotificationSystem = () => {
  // Global notification state
  const notifications = ref<Notification[]>([])
  const maxNotifications = ref(5)
  const defaultDuration = ref(5000) // 5 seconds
  const defaultPosition = ref<NotificationOptions['position']>('top-right')

  // Computed properties
  const activeNotifications = computed(() => 
    notifications.value.filter(n => n.show)
  )
  
  const notificationCount = computed(() => activeNotifications.value.length)
  
  const hasNotifications = computed(() => notificationCount.value > 0)

  // Utility functions
  const generateId = (): string => {
    return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  const getNotificationIcon = (type: NotificationType): string => {
    const icons = {
      success: 'fas fa-check-circle',
      error: 'fas fa-exclamation-circle',
      warning: 'fas fa-exclamation-triangle',
      info: 'fas fa-info-circle'
    }
    return icons[type] || icons.info
  }

  const getNotificationStyles = (type: NotificationType) => {
    const baseStyles = 'notification-toast transition-all duration-300 ease-in-out'
    const typeStyles = {
      success: 'notification-success',
      error: 'notification-error', 
      warning: 'notification-warning',
      info: 'notification-info'
    }
    
    return `${baseStyles} ${typeStyles[type] || typeStyles.info}`
  }

  // Core notification functions
  const addNotification = (
    type: NotificationType,
    message: string,
    options: NotificationOptions = {}
  ): string => {
    const id = generateId()
    const duration = options.duration ?? defaultDuration.value
    const persistent = options.persistent ?? false

    const notification: Notification = {
      id,
      type,
      title: options.title,
      message,
      duration,
      persistent,
      actions: options.actions,
      timestamp: Date.now(),
      show: true
    }

    // Add to the beginning of the array (newest first)
    notifications.value.unshift(notification)

    // Enforce max notifications limit
    if (notifications.value.length > maxNotifications.value) {
      notifications.value = notifications.value.slice(0, maxNotifications.value)
    }

    // Auto-dismiss if not persistent
    if (!persistent && duration > 0) {
      setTimeout(() => {
        dismissNotification(id)
      }, duration)
    }

    return id
  }

  const dismissNotification = (id: string) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.show = false
      
      // Remove from array after animation completes
      setTimeout(() => {
        notifications.value = notifications.value.filter(n => n.id !== id)
      }, 300) // Match CSS transition duration
    }
  }

  const dismissAll = () => {
    notifications.value.forEach(notification => {
      notification.show = false
    })
    
    // Clear all after animation
    setTimeout(() => {
      notifications.value = []
    }, 300)
  }

  const updateNotification = (id: string, updates: Partial<Notification>) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value[index] = { ...notifications.value[index], ...updates }
    }
  }

  // Convenience methods for different notification types
  const showSuccess = (message: string, options?: NotificationOptions): string => {
    return addNotification('success', message, options)
  }

  const showError = (message: string, options?: NotificationOptions): string => {
    return addNotification('error', message, { 
      duration: 8000, // Longer duration for errors
      ...options 
    })
  }

  const showWarning = (message: string, options?: NotificationOptions): string => {
    return addNotification('warning', message, { 
      duration: 6000, // Medium duration for warnings
      ...options 
    })
  }

  const showInfo = (message: string, options?: NotificationOptions): string => {
    return addNotification('info', message, options)
  }

  // Advanced notification methods
  const showConfirmation = (
    message: string,
    onConfirm: () => void,
    onCancel?: () => void,
    options?: NotificationOptions
  ): string => {
    const actions: NotificationAction[] = [
      {
        label: 'Confirm',
        handler: () => {
          onConfirm()
        },
        style: 'primary'
      }
    ]

    if (onCancel) {
      actions.push({
        label: 'Cancel',
        handler: () => {
          onCancel()
        },
        style: 'secondary'
      })
    }

    return addNotification('warning', message, {
      persistent: true,
      actions,
      ...options
    })
  }

  const showProgress = (
    message: string,
    options?: NotificationOptions & { progress?: number }
  ): string => {
    return addNotification('info', message, {
      persistent: true,
      ...options
    })
  }

  const updateProgress = (id: string, progress: number, message?: string) => {
    const updates: Partial<Notification> = {}
    if (message) updates.message = message
    updateNotification(id, updates)
  }

  // API response helpers
  const handleApiResponse = async <T>(
    apiCall: Promise<T>,
    options: {
      successMessage?: string
      errorMessage?: string
      loadingMessage?: string
      showSuccess?: boolean
      showError?: boolean
    } = {}
  ): Promise<T> => {
    const {
      successMessage = 'Operation completed successfully',
      errorMessage = 'Operation failed',
      loadingMessage = 'Processing...',
      showSuccess = true,
      showError = true
    } = options

    let loadingId: string | null = null

    if (loadingMessage) {
      loadingId = showProgress(loadingMessage)
    }

    try {
      const result = await apiCall

      if (loadingId) {
        dismissNotification(loadingId)
      }

      if (showSuccess) {
        showSuccess(successMessage)
      }

      return result
    } catch (error) {
      if (loadingId) {
        dismissNotification(loadingId)
      }

      if (showError) {
        const message = error instanceof Error ? error.message : errorMessage
        showError(message)
      }

      throw error
    }
  }

  // Journal-specific helpers
  const showJournalSuccess = (action: string, entryTitle?: string): string => {
    const message = entryTitle 
      ? `Journal entry "${entryTitle}" ${action} successfully`
      : `Journal entry ${action} successfully`
    
    return showSuccess(message, { duration: 4000 })
  }

  const showJournalError = (action: string, error?: string): string => {
    const message = error 
      ? `Failed to ${action} journal entry: ${error}`
      : `Failed to ${action} journal entry`
    
    return showError(message, { duration: 8000 })
  }

  // Batch operations
  const showBatchOperation = (
    operation: string,
    total: number,
    onComplete?: (successful: number, failed: number) => void
  ) => {
    let completed = 0
    let successful = 0
    let failed = 0

    const progressId = showProgress(`${operation}: 0/${total} completed`)

    const updateBatchProgress = (success: boolean) => {
      completed++
      if (success) successful++
      else failed++

      const message = `${operation}: ${completed}/${total} completed`
      updateProgress(progressId, (completed / total) * 100, message)

      if (completed === total) {
        dismissNotification(progressId)
        
        const resultMessage = failed > 0
          ? `${operation} completed: ${successful} successful, ${failed} failed`
          : `${operation} completed successfully: ${successful} items`

        if (failed > 0) {
          showWarning(resultMessage)
        } else {
          showSuccess(resultMessage)
        }

        onComplete?.(successful, failed)
      }
    }

    return { updateBatchProgress, progressId }
  }

  // Settings and configuration
  const configure = (settings: {
    maxNotifications?: number
    defaultDuration?: number
    defaultPosition?: NotificationOptions['position']
  }) => {
    if (settings.maxNotifications !== undefined) {
      maxNotifications.value = settings.maxNotifications
    }
    if (settings.defaultDuration !== undefined) {
      defaultDuration.value = settings.defaultDuration
    }
    if (settings.defaultPosition !== undefined) {
      defaultPosition.value = settings.defaultPosition
    }
  }

  // Debug and development helpers
  const clearAll = () => {
    notifications.value = []
  }

  const getNotificationHistory = () => {
    return [...notifications.value].sort((a, b) => b.timestamp - a.timestamp)
  }

  return {
    // State
    notifications: readonly(notifications),
    activeNotifications,
    notificationCount,
    hasNotifications,

    // Core methods
    addNotification,
    dismissNotification,
    dismissAll,
    updateNotification,

    // Convenience methods
    showSuccess,
    showError,
    showWarning,
    showInfo,

    // Advanced methods
    showConfirmation,
    showProgress,
    updateProgress,
    handleApiResponse,

    // Journal-specific helpers
    showJournalSuccess,
    showJournalError,

    // Batch operations
    showBatchOperation,

    // Utilities
    getNotificationIcon,
    getNotificationStyles,
    configure,
    clearAll,
    getNotificationHistory,

    // Settings
    maxNotifications: readonly(maxNotifications),
    defaultDuration: readonly(defaultDuration),
    defaultPosition: readonly(defaultPosition)
  }
}

// Global notification instance for use across the app
let globalNotificationInstance: ReturnType<typeof useNotificationSystem> | null = null

export const useGlobalNotifications = () => {
  if (!globalNotificationInstance) {
    globalNotificationInstance = useNotificationSystem()
  }
  return globalNotificationInstance
}

// Type exports
export type UseNotificationSystem = ReturnType<typeof useNotificationSystem>