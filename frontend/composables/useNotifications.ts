import { ref } from 'vue'

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  duration?: number
  persistent?: boolean
}

const notifications = ref<Notification[]>([])
let notificationId = 0

export const useNotifications = () => {
  const addNotification = (notification: Omit<Notification, 'id'>) => {
    const id = `notification_${++notificationId}`
    const newNotification: Notification = {
      id,
      duration: 5000,
      persistent: false,
      ...notification
    }
    
    notifications.value.push(newNotification)
    
    // Auto-remove if not persistent
    if (!newNotification.persistent && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }
    
    return id
  }
  
  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  const clearAllNotifications = () => {
    notifications.value = []
  }
  
  // Convenience methods
  const notifySuccess = (message: string, options?: Partial<Notification>) => {
    return addNotification({ type: 'success', message, ...options })
  }
  
  const notifyError = (message: string, options?: Partial<Notification>) => {
    return addNotification({ type: 'error', message, ...options })
  }
  
  const notifyWarning = (message: string, options?: Partial<Notification>) => {
    return addNotification({ type: 'warning', message, ...options })
  }
  
  const notifyInfo = (message: string, options?: Partial<Notification>) => {
    return addNotification({ type: 'info', message, ...options })
  }
  
  return {
    notifications: readonly(notifications),
    addNotification,
    removeNotification,
    clearAllNotifications,
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo
  }
}