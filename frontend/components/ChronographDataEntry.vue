<template>
  <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
    <div class="flex items-center justify-between mb-4">
      <h4 class="text-lg font-semibold text-blue-900 dark:text-blue-200">
        <i class="fas fa-tachometer-alt mr-2"></i>
        Chronograph Data
      </h4>
      <CustomButton
        @click="showEntry = !showEntry"
        variant="text"
        size="small"
        class="text-blue-600 hover:bg-blue-100 dark:text-blue-400 dark:hover:bg-blue-900"
      >
        <i class="fas transition-transform" :class="showEntry ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
        <span class="ml-2">{{ showEntry ? 'Hide' : 'Add Measured Speed' }}</span>
      </CustomButton>
    </div>
    
    <!-- Existing chronograph data display -->
    <div v-if="existingData.length > 0" class="mb-4">
      <h5 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">Recent Measurements</h5>
      <div class="space-y-2">
        <div 
          v-for="data in existingData" 
          :key="data.id"
          class="flex items-center justify-between p-2 bg-white dark:bg-blue-800/30 rounded border"
        >
          <div class="flex-1">
            <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ data.arrow_name || 'Unknown Arrow' }} - {{ data.arrow_weight_grains }}gr
            </div>
            <div class="text-xs text-gray-600 dark:text-gray-300">
              {{ data.measured_speed_fps }} FPS
              <span v-if="data.shot_count > 1">({{ data.shot_count }} shots)</span>
              <span v-if="data.std_deviation"> ±{{ data.std_deviation }}</span>
              <span class="ml-2">{{ formatDate(data.measurement_date) }}</span>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <button 
              @click="editChronographData(data)"
              class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
            >
              <i class="fas fa-edit text-sm"></i>
            </button>
            <button 
              @click="deleteChronographData(data.id)"
              class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
            >
              <i class="fas fa-trash text-sm"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Entry form -->
    <div v-if="showEntry" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Arrow Selection -->
        <div>
          <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            Arrow Used *
          </label>
          <md-filled-select 
            :value="chronoData.setup_arrow_id?.toString() || ''" 
            @change="chronoData.setup_arrow_id = parseInt($event.target.value)"
            label="Select arrow configuration"
            class="w-full"
            required
          >
            <md-select-option value="">
              <div slot="headline">Select an arrow...</div>
            </md-select-option>
            <md-select-option 
              v-for="arrow in setupArrows" 
              :key="arrow.id" 
              :value="arrow.id.toString()"
            >
              <div slot="headline">
                {{ arrow.arrow?.manufacturer || 'Unknown' }} {{ arrow.arrow?.model_name || 'Arrow' }} 
                ({{ calculateArrowWeight(arrow) }}gr, {{ arrow.arrow_length }}")
              </div>
            </md-select-option>
          </md-filled-select>
        </div>
        
        <!-- Measured Speed -->
        <div>
          <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            Measured Speed (FPS) *
          </label>
          <md-outlined-text-field 
            :value="chronoData.measured_speed_fps?.toString() || ''"
            @input="chronoData.measured_speed_fps = parseFloat($event.target.value)"
            label="Speed in feet per second"
            type="number"
            step="0.1"
            min="100"
            max="500"
            required
            class="w-full"
          />
        </div>
        
        <!-- Shot Count -->
        <div>
          <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            Number of Shots
          </label>
          <md-outlined-text-field 
            :value="chronoData.shot_count?.toString() || '3'"
            @input="chronoData.shot_count = parseInt($event.target.value)"
            label="Number of shots averaged"
            type="number"
            min="1"
            max="50"
            class="w-full"
          />
        </div>
        
        <!-- Standard Deviation -->
        <div>
          <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            Standard Deviation (FPS)
          </label>
          <md-outlined-text-field 
            :value="chronoData.std_deviation?.toString() || ''"
            @input="chronoData.std_deviation = parseFloat($event.target.value)"
            label="Shot consistency (±FPS)"
            type="number"
            step="0.1"
            min="0"
            class="w-full"
          />
        </div>
        
        <!-- Environmental Conditions -->
        <div>
          <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            Temperature (°F)
          </label>
          <md-outlined-text-field 
            :value="chronoData.temperature_f?.toString() || '70'"
            @input="chronoData.temperature_f = parseInt($event.target.value)"
            label="Temperature"
            type="number"
            min="-20"
            max="120"
            class="w-full"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            Humidity (%)
          </label>
          <md-outlined-text-field 
            :value="chronoData.humidity_percent?.toString() || '50'"
            @input="chronoData.humidity_percent = parseInt($event.target.value)"
            label="Relative humidity"
            type="number"
            min="0"
            max="100"
            class="w-full"
          />
        </div>
      </div>
      
      <!-- Additional fields -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Chronograph Model -->
        <div>
          <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            Chronograph Model
          </label>
          <md-outlined-text-field 
            :value="chronoData.chronograph_model || ''"
            @input="chronoData.chronograph_model = $event.target.value"
            label="e.g., Caldwell Ballistic Precision"
            type="text"
            class="w-full"
          />
        </div>
        
        <!-- Speed Range -->
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
              Min Speed (FPS)
            </label>
            <md-outlined-text-field 
              :value="chronoData.min_speed_fps?.toString() || ''"
              @input="chronoData.min_speed_fps = parseFloat($event.target.value)"
              label="Minimum"
              type="number"
              step="0.1"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
              Max Speed (FPS)
            </label>
            <md-outlined-text-field 
              :value="chronoData.max_speed_fps?.toString() || ''"
              @input="chronoData.max_speed_fps = parseFloat($event.target.value)"
              label="Maximum"
              type="number"
              step="0.1"
              class="w-full"
            />
          </div>
        </div>
      </div>
      
      <!-- Notes -->
      <div>
        <label class="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
          Notes
        </label>
        <textarea
          v-model="chronoData.notes"
          rows="2"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          placeholder="Additional notes about conditions, bow changes, etc..."
        ></textarea>
      </div>
      
      <!-- Action buttons -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-blue-200 dark:border-blue-700">
        <CustomButton
          @click="resetForm"
          variant="outlined"
          class="text-gray-700 dark:text-gray-200"
        >
          Reset
        </CustomButton>
        <CustomButton
          @click="saveChronographData"
          :disabled="!canSave || saving"
          variant="filled"
          class="text-white bg-blue-600 hover:bg-blue-700"
        >
          <i v-if="saving" class="fas fa-spinner fa-spin mr-2"></i>
          <i v-else class="fas fa-save mr-2"></i>
          {{ saving ? 'Saving...' : (editingId ? 'Update' : 'Save') }} Data
        </CustomButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import CustomButton from '~/components/CustomButton.vue'

const props = defineProps({
  bowSetupId: {
    type: Number,
    required: true
  },
  setupArrows: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['data-updated', 'speed-calculated'])

// API
const api = useApi()

// State
const showEntry = ref(false)
const saving = ref(false)
const existingData = ref([])
const editingId = ref(null)

// Form data
const chronoData = ref({
  setup_arrow_id: null,
  measured_speed_fps: null,
  shot_count: 3,
  std_deviation: null,
  min_speed_fps: null,
  max_speed_fps: null,
  temperature_f: 70,
  humidity_percent: 50,
  chronograph_model: '',
  notes: ''
})

// Computed
const canSave = computed(() => {
  return chronoData.value.setup_arrow_id && 
         chronoData.value.measured_speed_fps && 
         chronoData.value.measured_speed_fps > 0
})

// Methods
const calculateArrowWeight = (setupArrow) => {
  if (!setupArrow) return 0
  
  const pointWeight = setupArrow.point_weight || 0
  const nockWeight = setupArrow.nock_weight || 10
  const insertWeight = setupArrow.insert_weight || 0
  const bushingWeight = setupArrow.bushing_weight || 0
  const fletchingWeight = setupArrow.fletching_weight || 15
  
  // Calculate shaft weight using GPI if available
  let shaftWeight = 200 // Default estimate
  if (setupArrow.arrow?.spine_specifications?.length > 0) {
    const spineSpec = setupArrow.arrow.spine_specifications.find(spec => 
      spec.spine.toString() === setupArrow.calculated_spine?.toString()
    ) || setupArrow.arrow.spine_specifications[0]
    
    if (spineSpec?.gpi_weight && setupArrow.arrow_length) {
      shaftWeight = spineSpec.gpi_weight * setupArrow.arrow_length
    }
  }
  
  return Math.round(shaftWeight + pointWeight + nockWeight + insertWeight + bushingWeight + fletchingWeight)
}

const loadExistingData = async () => {
  try {
    const response = await api.get(`/chronograph-data/setup/${props.bowSetupId}`)
    existingData.value = response || []
  } catch (error) {
    console.error('Error loading chronograph data:', error)
    existingData.value = []
  }
}

const saveChronographData = async () => {
  if (!canSave.value || saving.value) return
  
  saving.value = true
  try {
    // Calculate arrow weight for the selected setup arrow
    const selectedArrow = props.setupArrows.find(a => a.id === chronoData.value.setup_arrow_id)
    const arrowWeight = calculateArrowWeight(selectedArrow)
    
    const payload = {
      ...chronoData.value,
      setup_id: props.bowSetupId,
      arrow_id: selectedArrow?.arrow_id || null,
      arrow_weight_grains: arrowWeight
    }
    
    let response
    if (editingId.value) {
      response = await api.put(`/chronograph-data/${editingId.value}`, payload)
    } else {
      response = await api.post('/chronograph-data', payload)
    }
    
    // Reload data
    await loadExistingData()
    
    // Reset form
    resetForm()
    
    // Emit events
    emit('data-updated', response)
    emit('speed-calculated', {
      speed: chronoData.value.measured_speed_fps,
      arrow_weight: arrowWeight,
      setup_arrow_id: chronoData.value.setup_arrow_id
    })
    
    showEntry.value = false
  } catch (error) {
    console.error('Error saving chronograph data:', error)
    // Could emit error event here
  } finally {
    saving.value = false
  }
}

const editChronographData = (data) => {
  chronoData.value = { ...data }
  editingId.value = data.id
  showEntry.value = true
}

const deleteChronographData = async (id) => {
  if (!confirm('Are you sure you want to delete this chronograph data?')) return
  
  try {
    await api.delete(`/chronograph-data/${id}`)
    await loadExistingData()
    emit('data-updated')
  } catch (error) {
    console.error('Error deleting chronograph data:', error)
  }
}

const resetForm = () => {
  chronoData.value = {
    setup_arrow_id: null,
    measured_speed_fps: null,
    shot_count: 3,
    std_deviation: null,
    min_speed_fps: null,
    max_speed_fps: null,
    temperature_f: 70,
    humidity_percent: 50,
    chronograph_model: '',
    notes: ''
  }
  editingId.value = null
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  loadExistingData()
})

// Watch for bow setup changes
watch(() => props.bowSetupId, () => {
  if (props.bowSetupId) {
    loadExistingData()
  }
})
</script>

<style scoped>
/* Custom styles for chronograph data entry */
.fa-icon {
  width: 16px;
  height: 16px;
}
</style>