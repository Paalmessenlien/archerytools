export const useDarkMode = () => {
  const isDarkMode = ref(false)

  // Check for saved theme preference or default to light mode
  const initializeTheme = () => {
    if (process.client) {
      const savedTheme = localStorage.getItem('theme')
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      
      if (savedTheme) {
        isDarkMode.value = savedTheme === 'dark'
      } else {
        isDarkMode.value = prefersDark
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