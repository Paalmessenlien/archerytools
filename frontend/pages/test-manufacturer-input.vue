<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold mb-8 text-gray-900 dark:text-gray-100">
        Manufacturer Input Component Test
      </h1>
      
      <div class="space-y-8">
        <!-- String Category Test -->
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
            String Manufacturer
          </h2>
          <ManufacturerInput
            v-model="stringManufacturer"
            category="strings"
            label="String Manufacturer"
            placeholder="Enter string manufacturer..."
            :required="true"
            @manufacturer-selected="handleManufacturerSelected"
            @manufacturer-created="handleManufacturerCreated"
          />
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Selected: {{ stringManufacturer || 'None' }}
          </p>
        </div>
        
        <!-- Sight Category Test -->
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
            Sight Manufacturer
          </h2>
          <ManufacturerInput
            v-model="sightManufacturer"
            category="sights"
            label="Sight Manufacturer"
            placeholder="Enter sight manufacturer..."
            help-text="Type to search for sight manufacturers"
            @manufacturer-selected="handleManufacturerSelected"
            @manufacturer-created="handleManufacturerCreated"
          />
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Selected: {{ sightManufacturer || 'None' }}
          </p>
        </div>
        
        <!-- Compound Bow Category Test -->
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
            Compound Bow Manufacturer
          </h2>
          <ManufacturerInput
            v-model="compoundManufacturer"
            category="compound_bows"
            label="Bow Manufacturer"
            placeholder="Enter compound bow manufacturer..."
            :min-chars="2"
            @manufacturer-selected="handleManufacturerSelected"
            @manufacturer-created="handleManufacturerCreated"
          />
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Selected: {{ compoundManufacturer || 'None' }}
          </p>
        </div>
        
        <!-- Event Log -->
        <div class="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
          <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
            Event Log
          </h2>
          <div class="space-y-2 max-h-40 overflow-y-auto">
            <div
              v-for="(event, index) in eventLog"
              :key="index"
              class="text-sm p-2 bg-white dark:bg-gray-800 rounded border-l-4"
              :class="event.type === 'selected' ? 'border-green-500' : 'border-blue-500'"
            >
              <span class="font-medium">{{ event.type }}:</span>
              {{ JSON.stringify(event.data) }}
            </div>
            <div v-if="eventLog.length === 0" class="text-gray-500 dark:text-gray-400 text-sm">
              No events yet. Try typing in the manufacturer inputs above.
            </div>
          </div>
          <button
            @click="clearEventLog"
            class="mt-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
          >
            Clear Log
          </button>
        </div>
        
        <!-- Test Values -->
        <div class="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg">
          <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
            Current Values
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span class="font-medium">String:</span>
              <br>{{ stringManufacturer || 'Empty' }}
            </div>
            <div>
              <span class="font-medium">Sight:</span>
              <br>{{ sightManufacturer || 'Empty' }}
            </div>
            <div>
              <span class="font-medium">Compound:</span>
              <br>{{ compoundManufacturer || 'Empty' }}
            </div>
          </div>
        </div>
        
        <!-- Test Instructions -->
        <div class="bg-yellow-50 dark:bg-yellow-900/20 p-6 rounded-lg">
          <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
            Test Instructions
          </h2>
          <ul class="list-disc list-inside space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <li>Type "hoy" to test existing manufacturer suggestions</li>
            <li>Type "test" to test new manufacturer creation</li>
            <li>Try typing less than 3 characters to see dropdown behavior</li>
            <li>Use arrow keys to navigate suggestions</li>
            <li>Press Enter to select highlighted suggestion</li>
            <li>Test different categories to see category-specific behavior</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Page metadata
definePageMeta({
  title: 'Test Manufacturer Input Component'
})

// Component state
const stringManufacturer = ref('')
const sightManufacturer = ref('')
const compoundManufacturer = ref('')
const eventLog = ref([])

// Event handlers
const handleManufacturerSelected = (data) => {
  eventLog.value.unshift({
    type: 'selected',
    timestamp: new Date().toLocaleTimeString(),
    data: data
  })
  
  // Limit log size
  if (eventLog.value.length > 10) {
    eventLog.value = eventLog.value.slice(0, 10)
  }
}

const handleManufacturerCreated = (data) => {
  eventLog.value.unshift({
    type: 'created',
    timestamp: new Date().toLocaleTimeString(),
    data: data
  })
  
  // Limit log size
  if (eventLog.value.length > 10) {
    eventLog.value = eventLog.value.slice(0, 10)
  }
}

const clearEventLog = () => {
  eventLog.value = []
}
</script>

<style scoped>
.container {
  min-height: 100vh;
}
</style>