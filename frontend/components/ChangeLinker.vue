<template>
  <div class="change-linker">
    <div class="linker-header">
      <h3 class="linker-title">
        <i class="fas fa-link mr-2"></i>
        Link Changes
      </h3>
      <p class="linker-subtitle">Connect this journal entry to related equipment or setup changes</p>
    </div>

    <!-- Current Links Display -->
    <div v-if="linkedChanges.length" class="current-links-section">
      <h4 class="section-header">
        <i class="fas fa-chain mr-2"></i>
        Currently Linked ({{ linkedChanges.length }})
      </h4>
      <div class="linked-changes-list">
        <div 
          v-for="link in linkedChanges" 
          :key="`${link.type}-${link.id}`"
          class="linked-change-item"
        >
          <div class="change-icon" :class="`icon-${link.type}`">
            <i :class="getChangeTypeIcon(link.type)"></i>
          </div>
          <div class="change-content">
            <div class="change-title">{{ link.title }}</div>
            <div class="change-details">
              <span class="change-type">{{ formatChangeType(link.type) }}</span>
              <span class="change-date">{{ formatDate(link.created_at) }}</span>
            </div>
            <div v-if="link.description" class="change-description">
              {{ truncateText(link.description, 100) }}
            </div>
          </div>
          <div class="change-actions">
            <button 
              @click="unlinkChange(link)"
              class="unlink-btn"
              title="Remove link"
            >
              <i class="fas fa-unlink"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Link Type Selection -->
    <div class="link-type-section">
      <h4 class="section-header">
        <i class="fas fa-plus mr-2"></i>
        Add New Links
      </h4>
      
      <div class="link-type-tabs">
        <button 
          v-for="type in linkTypes" 
          :key="type.value"
          @click="selectedLinkType = type.value"
          :class="['link-type-tab', { active: selectedLinkType === type.value }]"
        >
          <i :class="type.icon"></i>
          <span>{{ type.label }}</span>
          <div v-if="availableChanges[type.value]?.length" class="type-count">
            {{ availableChanges[type.value].length }}
          </div>
        </button>
      </div>
    </div>

    <!-- Available Changes List -->
    <div v-if="selectedLinkType && availableChanges[selectedLinkType]?.length" class="available-changes-section">
      <div class="search-filter">
        <md-outlined-text-field
          v-model="searchQuery"
          placeholder="Search changes..."
          class="search-input"
        >
          <i slot="leading-icon" class="fas fa-search"></i>
        </md-outlined-text-field>
      </div>

      <div class="available-changes-list">
        <div 
          v-for="change in filteredAvailableChanges" 
          :key="`available-${change.type}-${change.id}`"
          class="available-change-item"
          @click="linkChange(change)"
        >
          <div class="change-icon" :class="`icon-${change.type}`">
            <i :class="getChangeTypeIcon(change.type)"></i>
          </div>
          <div class="change-content">
            <div class="change-title">{{ change.title }}</div>
            <div class="change-details">
              <span class="change-date">{{ formatDate(change.created_at) }}</span>
              <span v-if="change.equipment_name" class="change-equipment">
                {{ change.equipment_name }}
              </span>
            </div>
            <div v-if="change.description" class="change-description">
              {{ truncateText(change.description, 80) }}
            </div>
          </div>
          <div class="change-actions">
            <button class="link-btn">
              <i class="fas fa-plus"></i>
            </button>
          </div>
        </div>
      </div>

      <div v-if="!filteredAvailableChanges.length" class="no-changes-message">
        <i class="fas fa-search"></i>
        <p>No {{ formatChangeType(selectedLinkType).toLowerCase() }} found matching your search.</p>
      </div>
    </div>

    <div v-else-if="selectedLinkType" class="no-changes-message">
      <i class="fas fa-info-circle"></i>
      <p>No {{ formatChangeType(selectedLinkType).toLowerCase() }} available to link.</p>
    </div>

    <!-- Action Buttons -->
    <div class="linker-actions">
      <div class="link-summary">
        <span v-if="linkedChanges.length">
          <i class="fas fa-check-circle mr-1"></i>
          {{ linkedChanges.length }} change{{ linkedChanges.length === 1 ? '' : 's' }} linked
        </span>
        <span v-else>
          <i class="fas fa-info-circle mr-1"></i>
          No changes linked yet
        </span>
      </div>
      <div class="action-buttons">
        <CustomButton @click="$emit('close')" variant="outlined">
          Done
        </CustomButton>
        <CustomButton @click="saveLinks" variant="primary" :disabled="!hasChanges">
          Save Links
        </CustomButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '@/composables/useApi'
import { useGlobalNotifications } from '@/composables/useNotificationSystem'

const props = defineProps({
  journalEntryId: Number,
  initialLinks: {
    type: Array,
    default: () => []
  },
  bowSetupId: Number
})

const emit = defineEmits(['close', 'links-updated'])

// Composables
const api = useApi()
const notifications = useGlobalNotifications()

// Reactive state
const linkedChanges = ref([...props.initialLinks])
const selectedLinkType = ref('equipment_change')
const searchQuery = ref('')
const availableChanges = ref({
  equipment_change: [],
  setup_change: [],
  arrow_change: []
})
const loading = ref(false)
const hasChanges = ref(false)

// Link type definitions
const linkTypes = [
  {
    value: 'equipment_change',
    label: 'Equipment Changes',
    icon: 'fas fa-cog'
  },
  {
    value: 'setup_change', 
    label: 'Setup Changes',
    icon: 'fas fa-tools'
  },
  {
    value: 'arrow_change',
    label: 'Arrow Changes', 
    icon: 'fas fa-bullseye'
  }
]

// Computed properties
const filteredAvailableChanges = computed(() => {
  const changes = availableChanges.value[selectedLinkType.value] || []
  const query = searchQuery.value.toLowerCase()
  
  if (!query) return changes.filter(change => !isAlreadyLinked(change))
  
  return changes.filter(change => 
    !isAlreadyLinked(change) && (
      change.title?.toLowerCase().includes(query) ||
      change.description?.toLowerCase().includes(query) ||
      change.equipment_name?.toLowerCase().includes(query)
    )
  )
})

// Methods
const isAlreadyLinked = (change) => {
  return linkedChanges.value.some(linked => 
    linked.type === change.type && linked.id === change.id
  )
}

const loadAvailableChanges = async () => {
  if (!props.bowSetupId) return
  
  loading.value = true
  try {
    // Load equipment changes
    const equipmentResponse = await api.get(`/equipment/changes?bow_setup_id=${props.bowSetupId}`)
    if (equipmentResponse.success) {
      availableChanges.value.equipment_change = equipmentResponse.data.map(change => ({
        ...change,
        type: 'equipment_change'
      }))
    }

    // Load setup changes
    const setupResponse = await api.get(`/bow-setups/${props.bowSetupId}/changes`)
    if (setupResponse.success) {
      availableChanges.value.setup_change = setupResponse.data.map(change => ({
        ...change,
        type: 'setup_change'
      }))
    }

    // Load arrow changes
    const arrowResponse = await api.get(`/arrows/changes?bow_setup_id=${props.bowSetupId}`)
    if (arrowResponse.success) {
      availableChanges.value.arrow_change = arrowResponse.data.map(change => ({
        ...change,
        type: 'arrow_change'
      }))
    }
  } catch (error) {
    console.error('Error loading available changes:', error)
    notifications.showError('Failed to load available changes')
  } finally {
    loading.value = false
  }
}

const linkChange = (change) => {
  if (isAlreadyLinked(change)) return
  
  linkedChanges.value.push(change)
  hasChanges.value = true
  
  notifications.showSuccess(`Linked ${formatChangeType(change.type).toLowerCase()}`)
}

const unlinkChange = (change) => {
  const index = linkedChanges.value.findIndex(linked => 
    linked.type === change.type && linked.id === change.id
  )
  
  if (index >= 0) {
    linkedChanges.value.splice(index, 1)
    hasChanges.value = true
    notifications.showSuccess(`Unlinked ${formatChangeType(change.type).toLowerCase()}`)
  }
}

const saveLinks = async () => {
  if (!props.journalEntryId || !hasChanges.value) return
  
  loading.value = true
  try {
    const linkData = linkedChanges.value.map(change => ({
      change_log_type: change.type,
      change_log_id: change.id,
      link_type: 'documents'
    }))

    const response = await api.post(`/journal/${props.journalEntryId}/links`, {
      links: linkData
    })

    if (response.success) {
      hasChanges.value = false
      notifications.showSuccess('Change links saved successfully')
      emit('links-updated', linkedChanges.value)
    } else {
      notifications.showError(response.error || 'Failed to save links')
    }
  } catch (error) {
    console.error('Error saving links:', error)
    notifications.showError('Failed to save change links')
  } finally {
    loading.value = false
  }
}

const getChangeTypeIcon = (type) => {
  const icons = {
    equipment_change: 'fas fa-cog',
    setup_change: 'fas fa-tools',
    arrow_change: 'fas fa-bullseye'
  }
  return icons[type] || 'fas fa-link'
}

const formatChangeType = (type) => {
  const labels = {
    equipment_change: 'Equipment Change',
    setup_change: 'Setup Change', 
    arrow_change: 'Arrow Change'
  }
  return labels[type] || type
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
  })
}

const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Watch for changes in bow setup
watch(() => props.bowSetupId, () => {
  loadAvailableChanges()
}, { immediate: true })

// Lifecycle
onMounted(() => {
  loadAvailableChanges()
})
</script>

<style scoped>
.change-linker {
  max-width: 700px;
  margin: 0 auto;
}

.linker-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.linker-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.linker-subtitle {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.9rem;
}

.section-header {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
}

/* Current Links Section */
.current-links-section {
  margin-bottom: 2rem;
}

.linked-changes-list, 
.available-changes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.linked-change-item,
.available-change-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  background: var(--md-sys-color-surface-container-lowest);
  transition: all 0.2s ease;
}

.linked-change-item {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
}

.available-change-item {
  cursor: pointer;
}

.available-change-item:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-container);
  transform: translateY(-1px);
}

.change-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.change-icon.icon-equipment_change {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.change-icon.icon-setup_change {
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
}

.change-icon.icon-arrow_change {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
}

.change-content {
  flex: 1;
  min-width: 0;
}

.change-title {
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.25rem;
}

.change-details {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
}

.change-type {
  font-weight: 500;
}

.change-description {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.4;
}

.change-actions {
  display: flex;
  align-items: center;
}

.unlink-btn,
.link-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.unlink-btn {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
}

.unlink-btn:hover {
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
}

.link-btn {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.link-btn:hover {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

/* Link Type Selection */
.link-type-section {
  margin-bottom: 2rem;
}

.link-type-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.link-type-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 2px solid var(--md-sys-color-outline-variant);
  border-radius: 8px;
  background: var(--md-sys-color-surface-container-lowest);
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.link-type-tab:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-container);
}

.link-type-tab.active {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.type-count {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  border-radius: 12px;
  padding: 0.125rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 1.5rem;
  text-align: center;
}

.link-type-tab.active .type-count {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

/* Available Changes Section */
.available-changes-section {
  margin-bottom: 2rem;
}

.search-filter {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
}

.no-changes-message {
  text-align: center;
  padding: 2rem;
  color: var(--md-sys-color-on-surface-variant);
}

.no-changes-message i {
  font-size: 2rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.no-changes-message p {
  margin: 0;
  font-size: 0.9rem;
}

/* Actions */
.linker-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.link-summary {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  display: flex;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

@media (max-width: 768px) {
  .link-type-tabs {
    flex-direction: column;
  }
  
  .link-type-tab {
    justify-content: center;
  }
  
  .change-details {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .linker-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: space-between;
  }
}
</style>