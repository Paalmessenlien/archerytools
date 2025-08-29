export const useAppVersion = () => {
  const currentVersion = ref(null)
  const hasUpdate = ref(false)
  const showUpdateNotification = ref(false)

  const checkForUpdates = async () => {
    if (!process.client) return

    try {
      // Get current app version from meta tag
      const versionMeta = document.querySelector('meta[name="app-version"]')
      const pageVersion = versionMeta?.content

      // Get cached version from localStorage
      const cachedVersion = localStorage.getItem('app-version')
      
      if (pageVersion) {
        currentVersion.value = pageVersion
        
        // If we have a cached version and it's different, show update notification
        if (cachedVersion && cachedVersion !== pageVersion) {
          hasUpdate.value = true
          showUpdateNotification.value = true
          
          // Clear localStorage to force fresh data fetch
          clearAppCache()
        }
        
        // Update cached version
        localStorage.setItem('app-version', pageVersion)
      }
    } catch (error) {
      console.error('Version check failed:', error)
    }
  }

  const clearAppCache = () => {
    if (!process.client) return

    // Clear localStorage except for essential items
    const essentialKeys = ['theme', 'google-auth-token']
    const allKeys = Object.keys(localStorage)
    
    allKeys.forEach(key => {
      if (!essentialKeys.includes(key)) {
        localStorage.removeItem(key)
      }
    })

    // Clear sessionStorage
    sessionStorage.clear()

    // Force reload of cached assets
    if ('caches' in window) {
      caches.keys().then(cacheNames => {
        cacheNames.forEach(cacheName => {
          caches.delete(cacheName)
        })
      })
    }
  }

  const dismissUpdateNotification = () => {
    showUpdateNotification.value = false
    hasUpdate.value = false
  }

  const reloadApp = () => {
    if (process.client) {
      // Force hard reload to get fresh assets
      window.location.reload(true)
    }
  }

  return {
    currentVersion: readonly(currentVersion),
    hasUpdate: readonly(hasUpdate),
    showUpdateNotification: readonly(showUpdateNotification),
    checkForUpdates,
    clearAppCache,
    dismissUpdateNotification,
    reloadApp
  }
}