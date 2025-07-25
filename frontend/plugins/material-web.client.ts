/**
 * Material Web Components Plugin for Nuxt.js
 * Initializes Material Design Web Components for use in Vue.js
 */

// Import core Material Web components we need
import '@material/web/button/filled-button.js'
import '@material/web/button/outlined-button.js'
import '@material/web/button/text-button.js'
import '@material/web/select/filled-select.js'
import '@material/web/select/select-option.js'
import '@material/web/slider/slider.js'
import '@material/web/textfield/filled-text-field.js'
import '@material/web/textfield/outlined-text-field.js'
import '@material/web/progress/linear-progress.js'
import '@material/web/divider/divider.js'
import '@material/web/chips/chip-set.js'
import '@material/web/chips/assist-chip.js'
import '@material/web/chips/filter-chip.js'
import '@material/web/icon/icon.js'

// Import experimental components from labs
import '@material/web/labs/card/elevated-card.js'

export default defineNuxtPlugin(() => {
  // Plugin is automatically executed when components are imported
  // Material Web components are now available globally
  console.log('Material Web components initialized')
})