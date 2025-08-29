export const useDarkMode = () => {
  // Initialize with saved theme or default to dark mode
  const isDarkMode = ref(true)

  // Initialize theme immediately on client
  if (process.client) {
    const savedTheme = localStorage.getItem('theme')
    isDarkMode.value = savedTheme ? savedTheme === 'dark' : true
    
    // Apply theme immediately
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
      document.documentElement.classList.remove('light')
    } else {
      document.documentElement.classList.add('light')
      document.documentElement.classList.remove('dark')
    }
  }

  // Check for saved theme preference or default to dark mode
  const initializeTheme = () => {
    if (process.client) {
      const savedTheme = localStorage.getItem('theme')
      
      if (savedTheme) {
        isDarkMode.value = savedTheme === 'dark'
      } else {
        // Default to dark mode for new users
        isDarkMode.value = true
        // Save the default preference
        localStorage.setItem('theme', 'dark')
      }
      
      applyTheme()
    }
  }

  // Apply theme to document
  const applyTheme = () => {
    if (process.client) {
      if (isDarkMode.value) {
        document.documentElement.classList.add('dark')
        document.documentElement.classList.remove('light')
      } else {
        document.documentElement.classList.add('light')
        document.documentElement.classList.remove('dark')
      }
    }
  }

  // Toggle theme
  const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value
    
    if (process.client) {
      localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
      applyTheme()
    }
  }

  // Watch for changes and apply theme
  watch(isDarkMode, applyTheme)

  return {
    isDarkMode: readonly(isDarkMode),
    toggleDarkMode,
    initializeTheme
  }
}