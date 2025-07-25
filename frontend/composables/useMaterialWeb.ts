/**
 * Composable for Material Web components integration with Vue.js
 * Provides type-safe wrappers and utilities for Material Web components
 */

export const useMaterialWeb = () => {
  /**
   * Helper to emit events from Material Web components to Vue
   */
  const createMaterialEventHandler = (emit: Function, eventName: string) => {
    return (event: Event) => {
      const target = event.target as any
      emit(eventName, {
        value: target.value,
        selectedIndex: target.selectedIndex,
        checked: target.checked,
        event
      })
    }
  }

  /**
   * Set up Material Web select component with Vue reactivity
   */
  const setupMaterialSelect = (element: any, value: Ref<string>) => {
    if (!element) return

    // Watch for value changes from Vue
    watch(value, (newValue) => {
      if (element.value !== newValue) {
        element.value = newValue
      }
    }, { immediate: true })

    // Listen for changes from Material component
    const handleChange = (event: Event) => {
      const target = event.target as any
      value.value = target.value
    }

    element.addEventListener('change', handleChange)

    // Return cleanup function
    return () => {
      element.removeEventListener('change', handleChange)
    }
  }

  /**
   * Set up Material Web slider component with Vue reactivity
   */
  const setupMaterialSlider = (element: any, value: Ref<number>) => {
    if (!element) return

    // Watch for value changes from Vue
    watch(value, (newValue) => {
      if (element.value !== newValue) {
        element.value = newValue
      }
    }, { immediate: true })

    // Listen for input changes from Material component
    const handleInput = (event: Event) => {
      const target = event.target as any
      value.value = Number(target.value)
    }

    element.addEventListener('input', handleInput)

    // Return cleanup function
    return () => {
      element.removeEventListener('input', handleInput)
    }
  }

  /**
   * Set up Material Web text field component with Vue reactivity
   */
  const setupMaterialTextField = (element: any, value: Ref<string | number>) => {
    if (!element) return

    // Watch for value changes from Vue
    watch(value, (newValue) => {
      if (element.value !== String(newValue)) {
        element.value = String(newValue)
      }
    }, { immediate: true })

    // Listen for input changes from Material component
    const handleInput = (event: Event) => {
      const target = event.target as any
      const newValue = target.type === 'number' ? Number(target.value) : target.value
      value.value = newValue
    }

    element.addEventListener('input', handleInput)

    // Return cleanup function
    return () => {
      element.removeEventListener('input', handleInput)
    }
  }

  return {
    createMaterialEventHandler,
    setupMaterialSelect,
    setupMaterialSlider,
    setupMaterialTextField
  }
}