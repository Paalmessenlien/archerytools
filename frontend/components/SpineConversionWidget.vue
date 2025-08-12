<template>
  <div class="spine-conversion-widget">
    <!-- Widget Header -->
    <div class="flex items-center justify-between mb-4">
      <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
        <i class="fas fa-exchange-alt mr-2"></i>
        Spine Conversion Tool
      </h4>
      <CustomButton
        @click="showWidget = !showWidget"
        variant="text"
        size="small"
        class="text-blue-600 hover:bg-blue-100 dark:text-blue-400 dark:hover:bg-blue-900"
      >
        <i class="fas transition-transform" :class="showWidget ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
        {{ showWidget ? 'Hide' : 'Show' }}
      </CustomButton>
    </div>

    <!-- Conversion Interface -->
    <div v-if="showWidget" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- From Spine -->
        <div class="space-y-2">
          <label class="block text-xs font-medium text-gray-700 dark:text-gray-300">
            Convert From:
          </label>
          <div class="flex space-x-2">
            <input
              v-model="fromSpine"
              type="text"
              placeholder="e.g., 400 or 45-50"
              class="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            />
            <md-filled-select 
              :value="fromSystem" 
              @change="handleFromSystemChange($event.target.value)"
              label="System"
              class="w-24"
            >
              <md-select-option value="carbon">
                <div slot="headline">Carbon</div>
              </md-select-option>
              <md-select-option value="aluminum">
                <div slot="headline">Aluminum</div>
              </md-select-option>
              <md-select-option value="wood">
                <div slot="headline">Wood</div>
              </md-select-option>
            </md-filled-select>
          </div>
        </div>

        <!-- To Spine -->
        <div class="space-y-2">
          <label class="block text-xs font-medium text-gray-700 dark:text-gray-300">
            Convert To:
          </label>
          <div class="flex space-x-2">
            <div class="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700">
              <span v-if="conversionResult && conversionResult.conversion_available" class="text-gray-900 dark:text-gray-100">
                {{ conversionResult.to_spine }}
              </span>
              <span v-else-if="conversionResult && !conversionResult.conversion_available" class="text-gray-500 dark:text-gray-400 italic">
                No conversion available
              </span>
              <span v-else-if="isConverting" class="text-gray-500 dark:text-gray-400 italic">
                Converting...
              </span>
              <span v-else class="text-gray-400 dark:text-gray-500 italic">
                Select spine to convert
              </span>
            </div>
            <md-filled-select 
              :value="toSystem" 
              @change="handleToSystemChange($event.target.value)"
              label="System"
              class="w-24"
            >
              <md-select-option value="carbon">
                <div slot="headline">Carbon</div>
              </md-select-option>
              <md-select-option value="aluminum">
                <div slot="headline">Aluminum</div>
              </md-select-option>
              <md-select-option value="wood">
                <div slot="headline">Wood</div>
              </md-select-option>
            </md-filled-select>
          </div>
        </div>
      </div>

      <!-- Convert Button -->
      <div class="flex justify-center">
        <CustomButton
          @click="convertSpine"
          :disabled="!fromSpine || fromSystem === toSystem || isConverting"
          variant="filled"
          class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
        >
          <i class="fas fa-sync-alt mr-2" :class="{ 'animate-spin': isConverting }"></i>
          Convert
        </CustomButton>
      </div>

      <!-- Conversion Result -->
      <div v-if="conversionResult" class="mt-4 p-3 rounded-lg border" :class="[
        conversionResult.conversion_available 
          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
          : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
      ]">
        <div class="flex items-start space-x-3">
          <i class="fas mt-1" :class="[
            conversionResult.conversion_available 
              ? 'fa-check-circle text-green-600 dark:text-green-400'
              : 'fa-exclamation-triangle text-yellow-600 dark:text-yellow-400'
          ]"></i>
          <div class="flex-1">
            <p class="text-sm font-medium" :class="[
              conversionResult.conversion_available 
                ? 'text-green-900 dark:text-green-100'
                : 'text-yellow-900 dark:text-yellow-100'
            ]">
              {{ conversionResult.conversion_available ? 'Conversion Available' : 'No Direct Conversion' }}
            </p>
            <p class="text-xs mt-1" :class="[
              conversionResult.conversion_available 
                ? 'text-green-700 dark:text-green-300'
                : 'text-yellow-700 dark:text-yellow-300'
            ]">
              {{ conversionResult.accuracy_note }}
            </p>
            
            <!-- Copy to Clipboard -->
            <div v-if="conversionResult.conversion_available" class="mt-2">
              <CustomButton
                @click="copyToClipboard(conversionResult.to_spine)"
                variant="outlined"
                size="small"
                class="text-green-600 border-green-300 hover:bg-green-100 dark:text-green-400 dark:border-green-600 dark:hover:bg-green-900"
              >
                <i class="fas fa-copy mr-1"></i>
                Copy Result
              </CustomButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Conversion Error -->
      <div v-if="conversionError" class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <p class="text-sm text-red-700 dark:text-red-300">
          <i class="fas fa-exclamation-circle mr-2"></i>
          {{ conversionError }}
        </p>
      </div>

      <!-- Quick Reference -->
      <div class="mt-4 p-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">Quick Reference:</p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs text-gray-600 dark:text-gray-400">
          <div>
            <strong>Carbon:</strong> 150-1000<br>
            (lower = stiffer)
          </div>
          <div>
            <strong>Aluminum:</strong> 1416-2413<br>
            (shaft size codes)
          </div>
          <div>
            <strong>Wood:</strong> 25-80#<br>
            (traditional pounds)
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// API
const api = useApi()

// Reactive state
const showWidget = ref(false)
const fromSpine = ref('')
const fromSystem = ref('carbon')
const toSystem = ref('aluminum')
const isConverting = ref(false)
const conversionResult = ref(null)
const conversionError = ref('')

// Methods
const handleFromSystemChange = (system: string) => {
  fromSystem.value = system
  conversionResult.value = null
  conversionError.value = ''
}

const handleToSystemChange = (system: string) => {
  toSystem.value = system
  conversionResult.value = null
  conversionError.value = ''
}

const convertSpine = async () => {
  if (!fromSpine.value || fromSystem.value === toSystem.value) return
  
  isConverting.value = true
  conversionError.value = ''
  conversionResult.value = null
  
  try {
    const response = await api.post('/calculator/convert-spine', {
      from_spine: fromSpine.value,
      from_system: fromSystem.value,
      to_system: toSystem.value
    })
    
    conversionResult.value = response
    
  } catch (error) {
    conversionError.value = 'Failed to convert spine values. Please check your input and try again.'
    console.error('Error converting spine:', error)
  } finally {
    isConverting.value = false
  }
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    // Could add a brief success indicator here
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
  }
}

// Watch for changes to trigger auto-conversion
watch([fromSpine, fromSystem, toSystem], () => {
  conversionResult.value = null
  conversionError.value = ''
}, { immediate: false })
</script>

<style scoped>
.spine-conversion-widget {
  @apply w-full;
}

/* Loading spinner styling */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Input styling improvements */
input:focus {
  @apply outline-none ring-2;
}

/* Custom select width adjustment */
.w-24 {
  min-width: 6rem;
}

/* Responsive grid adjustments */
@media (max-width: 640px) {
  .grid-cols-1.md\\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 0.75rem;
  }
  
  .grid-cols-1.md\\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 0.5rem;
  }
}
</style>