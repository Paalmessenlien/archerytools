<template>
  <div class="change-timeline-entry">
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm hover:shadow-md transition-shadow">
      <!-- Change Header -->
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-2">
            <!-- Change type badge -->
            <span :class="[
              'px-3 py-1 text-sm font-medium rounded-full',
              getChangeTypeBadge(change.change_type, change.change_source)
            ]">
              {{ formatChangeType(change.change_type) }}
            </span>
            
            <!-- Source badge -->
            <span :class="[
              'px-2 py-1 text-xs rounded-full',
              getSourceBadge(change.change_source)
            ]">
              {{ change.change_source.charAt(0).toUpperCase() + change.change_source.slice(1) }}
            </span>
          </div>
          
          <!-- Equipment/Arrow info -->
          <div v-if="change.manufacturer_name || change.model_name || change.arrow_id" class="flex items-center space-x-2 mb-2">
            <i :class="getItemIcon(change.change_source, change.category_name)" class="text-gray-500 dark:text-gray-400"></i>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
              <template v-if="change.change_source === 'arrow'">
                <button
                  @click="navigateToArrow(change.item_id)"
                  class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 hover:underline"
                >
                  Arrow ID: {{ change.item_id }}
                </button>
              </template>
              <template v-else-if="change.change_source === 'equipment' && change.item_id">
                <button
                  @click="navigateToEquipment(change.item_id)"
                  class="text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-200 hover:underline"
                >
                  {{ change.manufacturer_name }} {{ change.model_name }}
                </button>
              </template>
              <template v-else>
                {{ change.manufacturer_name }} {{ change.model_name }}
              </template>
            </span>
            
            <!-- Category badge -->
            <span v-if="change.category_name" :class="[
              'px-2 py-1 text-xs rounded-full',
              getCategoryBadge(change.category_name)
            ]">
              {{ change.category_name }}
            </span>
          </div>
        </div>
        
        <!-- Timestamp -->
        <div class="text-right">
          <div class="text-sm text-gray-500 dark:text-gray-400">
            {{ formatTimestamp(change.created_at) }}
          </div>
          <div class="text-xs text-gray-400 dark:text-gray-500">
            {{ formatDate(change.created_at) }}
          </div>
        </div>
      </div>
      
      <!-- Change Description -->
      <div class="mb-4">
        <p class="text-gray-900 dark:text-gray-100 font-medium">
          {{ change.change_description }}
        </p>
      </div>
      
      <!-- Equipment Restore Action -->
      <div v-if="canShowRestoreButton(change)" class="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border-l-4 border-yellow-400">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <i class="fas fa-undo text-yellow-600 dark:text-yellow-400 mr-2"></i>
            <div>
              <p class="text-sm font-medium text-yellow-800 dark:text-yellow-200">Equipment Deleted</p>
              <p class="text-xs text-yellow-700 dark:text-yellow-300">This equipment can be restored if needed</p>
            </div>
          </div>
          <CustomButton
            @click="restoreEquipment"
            variant="filled"
            size="small"
            class="bg-yellow-600 text-white hover:bg-yellow-700 dark:bg-yellow-600 dark:hover:bg-yellow-700"
            :disabled="restoringEquipment"
          >
            <i class="fas fa-undo mr-1"></i>
            <span v-if="restoringEquipment">Restoring...</span>
            <span v-else>Restore</span>
          </CustomButton>
        </div>
      </div>
      
      <!-- User Note -->
      <div v-if="change.change_reason" class="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border-l-4 border-amber-400">
        <div class="flex items-start">
          <i class="fas fa-sticky-note text-amber-600 dark:text-amber-400 mt-0.5 mr-2"></i>
          <div>
            <p class="text-sm font-medium text-amber-800 dark:text-amber-200 mb-1">User Note:</p>
            <p class="text-sm text-amber-700 dark:text-amber-300 italic">
              "{{ change.change_reason }}"
            </p>
          </div>
        </div>
      </div>
      
      <!-- Before/After Values -->
      <div v-if="change.old_value || change.new_value" class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div class="flex items-center mb-3">
          <i class="fas fa-exchange-alt text-gray-500 dark:text-gray-400 mr-2"></i>
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            Field: {{ formatFieldName(change.field_name) }}
          </span>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-if="change.old_value" class="space-y-2">
            <div class="flex items-center">
              <i class="fas fa-arrow-left text-red-500 mr-2"></i>
              <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Before</span>
            </div>
            <div class="p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
              <p class="text-sm text-gray-900 dark:text-gray-100 font-mono break-words">
                {{ formatValue(change.old_value) }}
              </p>
            </div>
          </div>
          
          <div v-if="change.new_value" class="space-y-2">
            <div class="flex items-center">
              <i class="fas fa-arrow-right text-green-500 mr-2"></i>
              <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">After</span>
            </div>
            <div class="p-3 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800">
              <p class="text-sm text-gray-900 dark:text-gray-100 font-mono break-words">
                {{ formatValue(change.new_value) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import CustomButton from '@/components/CustomButton.vue'

const props = defineProps({
  change: {
    type: Object,
    required: true
  },
  bowSetup: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['equipment-restored', 'error'])

// Composables
const api = useApi()
const router = useRouter()

// State
const restoringEquipment = ref(false)

// Equipment restore functionality
const canShowRestoreButton = (change) => {
  return change.change_source === 'equipment' && 
         change.change_type === 'remove' && 
         change.item_id && 
         !change.is_restored
}

const restoreEquipment = async () => {
  if (!props.change.item_id || restoringEquipment.value) return
  
  try {
    restoringEquipment.value = true
    
    await api.post(`/bow-setups/${props.bowSetup.id}/equipment/${props.change.item_id}/restore`)
    
    // Mark this change as restored to hide the button
    props.change.is_restored = true
    
    // Emit success notification
    emit('equipment-restored', {
      equipmentName: props.change.manufacturer_name && props.change.model_name 
        ? `${props.change.manufacturer_name} ${props.change.model_name}`
        : 'Equipment',
      category: props.change.category_name
    })
    
  } catch (error) {
    console.error('Error restoring equipment:', error)
    emit('error', `Failed to restore equipment: ${error.message || 'Unknown error'}`)
  } finally {
    restoringEquipment.value = false
  }
}

// Navigation functions
const navigateToEquipment = (equipmentId) => {
  router.push(`/equipment/${equipmentId}`)
}

const navigateToArrow = (arrowId) => {
  router.push(`/arrows/${arrowId}`)
}

// Styling functions
const getChangeTypeBadge = (changeType, source) => {
  const badges = {
    arrow: {
      'arrow_added': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
      'arrow_removed': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'arrow_modified': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'specifications_changed': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
    },
    equipment: {
      'add': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'remove': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'modify': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'settings_change': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      'activation_change': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
    },
    setup: {
      'created': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      'setup_modified': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'name_changed': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    }
  }
  return badges[source]?.[changeType] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
}

const getSourceBadge = (source) => {
  const badges = {
    'arrow': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'equipment': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'setup': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
  }
  return badges[source] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
}

const getCategoryBadge = (category) => {
  const badges = {
    'Arrow': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'String': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
    'Sight': 'bg-sky-100 text-sky-800 dark:bg-sky-900 dark:text-sky-200',
    'Stabilizer': 'bg-violet-100 text-violet-800 dark:bg-violet-900 dark:text-violet-200',
    'Arrow Rest': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    'Weight': 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200',
    'Setup': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
  }
  return badges[category] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
}

const getItemIcon = (source, category) => {
  if (source === 'arrow') {
    return 'fas fa-bullseye'
  }
  
  const icons = {
    'String': 'fas fa-link',
    'Sight': 'fas fa-crosshairs',
    'Scope': 'fas fa-search',
    'Stabilizer': 'fas fa-balance-scale',
    'Arrow Rest': 'fas fa-hand-paper',
    'Plunger': 'fas fa-bullseye',
    'Weight': 'fas fa-weight-hanging'
  }
  return icons[category] || 'fas fa-cog'
}

// Formatting functions
const formatChangeType = (changeType) => {
  const labels = {
    'arrow_added': 'Arrow Added',
    'arrow_removed': 'Arrow Removed',
    'arrow_modified': 'Arrow Modified',
    'specifications_changed': 'Specs Changed',
    'add': 'Added',
    'remove': 'Removed',
    'modify': 'Modified',
    'settings_change': 'Settings Changed',
    'activation_change': 'Status Changed',
    'created': 'Created',
    'setup_modified': 'Setup Modified',
    'name_changed': 'Name Changed'
  }
  return labels[changeType] || changeType
}

const formatFieldName = (fieldName) => {
  if (!fieldName) return 'General'
  return fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (days > 7) {
    return date.toLocaleDateString()
  } else if (days > 0) {
    return `${days} day${days > 1 ? 's' : ''} ago`
  } else if (hours > 0) {
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  } else if (minutes > 0) {
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  } else {
    return 'Just now'
  }
}

const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatValue = (value) => {
  if (!value) return 'N/A'
  
  try {
    const parsed = JSON.parse(value)
    return JSON.stringify(parsed, null, 2)
  } catch {
    return value
  }
}
</script>

<style scoped>
.change-timeline-entry {
  width: 100%;
}

/* Enhanced hover effects */
.change-timeline-entry .bg-white:hover {
  transform: translateY(-1px);
}

/* Responsive design */
@media (max-width: 640px) {
  .change-timeline-entry .grid-cols-1.md\:grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  .change-timeline-entry .p-6 {
    padding: 1rem;
  }
}
</style>