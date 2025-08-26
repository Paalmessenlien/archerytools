<template>
  <div class="journal-change-log">
    <!-- Header with View Mode Toggle -->
    <div class="changelog-header">
      <div class="header-content">
        <h3 class="header-title">
          <i class="fas fa-history mr-2"></i>
          Change History
        </h3>
        <p class="header-subtitle">
          Track all modifications to your bow setups, arrows, and equipment over time.
        </p>
      </div>
      
      <!-- View Mode Toggle -->
      <div class="view-mode-toggle">
        <div class="toggle-buttons">
          <button
            @click="viewMode = 'setup-specific'"
            :class="['toggle-btn', { active: viewMode === 'setup-specific' }]"
          >
            <i class="fas fa-crosshairs mr-2"></i>
            By Setup
          </button>
          <button
            @click="viewMode = 'global'"
            :class="['toggle-btn', { active: viewMode === 'global' }]"
          >
            <i class="fas fa-globe mr-2"></i>
            All Activities
          </button>
        </div>
      </div>
    </div>

    <!-- Bow Setup Selector -->
    <div v-if="viewMode === 'setup-specific'" class="setup-selector-card">
      <div class="setup-selector-content">
        <h4 class="selector-title">
          <i class="fas fa-crosshairs mr-2"></i>
          Select Bow Setup
        </h4>
        
        <!-- Setup Selection -->
        <div v-if="bowSetups.length > 0" class="setup-selection">
          <div class="setup-grid">
            <div
              v-for="setup in bowSetups"
              :key="setup.id"
              @click="selectBowSetup(setup)"
              :class="[
                'setup-card',
                {
                  'selected': selectedSetup?.id === setup.id,
                  'active-setup': setup.is_active
                }
              ]"
            >
              <div class="setup-header">
                <h5 class="setup-name">{{ setup.name }}</h5>
                <span class="setup-type">{{ setup.bow_type }}</span>
              </div>
              <div class="setup-details">
                <div class="setup-spec">{{ setup.draw_weight }}# @ 28"</div>
                <div v-if="setup.description" class="setup-description">{{ setup.description }}</div>
              </div>
              <div v-if="setup.is_active" class="active-badge">
                <i class="fas fa-star mr-1"></i>Active Setup
              </div>
            </div>
          </div>
        </div>
        
        <!-- No setups message -->
        <div v-else-if="!loadingSetups" class="no-setups">
          <i class="fas fa-crosshairs"></i>
          <h5>No Bow Setups Found</h5>
          <p>Create a bow setup to start tracking changes.</p>
          <CustomButton variant="primary" icon="fas fa-plus">
            Create Your First Setup
          </CustomButton>
        </div>
        
        <!-- Loading setups -->
        <div v-else class="loading-setups">
          <div class="loading-spinner"></div>
          <p>Loading bow setups...</p>
        </div>
      </div>
    </div>

    <!-- Global Activity View -->
    <div v-if="viewMode === 'global'" class="global-view">
      <!-- Global Statistics -->
      <div class="statistics-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Total Activities</p>
            <p class="stat-value">{{ globalStatistics.total_activities || 0 }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-crosshairs"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Bow Setups</p>
            <p class="stat-value">{{ globalStatistics.setup_count || 0 }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Last 30 Days</p>
            <p class="stat-value">{{ globalStatistics.recent_activities || 0 }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-cogs"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Active Setups</p>
            <p class="stat-value">{{ globalStatistics.active_setups || 0 }}</p>
          </div>
        </div>
      </div>

      <!-- Global Activity Timeline -->
      <div class="global-activity-card">
        <h4 class="activity-title">
          <i class="fas fa-timeline mr-2"></i>
          All User Activities
        </h4>
        <GlobalChangeLogViewer
          @statistics-updated="handleGlobalStatisticsUpdate"
          @error="handleError"
        />
      </div>
    </div>

    <!-- Setup-Specific Change History -->
    <div v-if="viewMode === 'setup-specific' && selectedSetup" class="setup-specific-view">
      <!-- Statistics Cards -->
      <div class="statistics-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Total Changes</p>
            <p class="stat-value">{{ statistics.total_changes || 0 }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Last 30 Days</p>
            <p class="stat-value">{{ statistics.changes_last_30_days || 0 }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-bullseye"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Arrow Changes</p>
            <p class="stat-value">{{ getArrowChangesCount() }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-cogs"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Equipment Changes</p>
            <p class="stat-value">{{ getEquipmentChangesCount() }}</p>
          </div>
        </div>
      </div>

      <!-- Enhanced Change History Viewer -->
      <div class="change-history-card">
        <EnhancedChangeLogViewer
          :bow-setup-id="selectedSetup.id"
          :show-header="false"
          @statistics-updated="handleStatisticsUpdate"
          @error="handleError"
        />
      </div>
    </div>

    <!-- Welcome Message for Setup-Specific View -->
    <div v-else-if="viewMode === 'setup-specific' && bowSetups.length > 0" class="welcome-message">
      <i class="fas fa-arrow-up"></i>
      <h4>Select a Bow Setup</h4>
      <p>Choose a bow setup above to view its complete change history including arrows, equipment, and setup modifications.</p>
    </div>

    <!-- Error Toast -->
    <div v-if="error" class="error-toast">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle mr-2"></i>
        {{ error }}
        <button @click="error = ''" class="error-close">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import EnhancedChangeLogViewer from '~/components/EnhancedChangeLogViewer.vue'
import GlobalChangeLogViewer from '~/components/GlobalChangeLogViewer.vue'
import CustomButton from '~/components/CustomButton.vue'

// Define props
const props = defineProps({
  bowSetups: {
    type: Array,
    default: () => []
  }
})

// Define emits
const emit = defineEmits(['journal-create-request'])

// Composables
const api = useApi()

// State
const viewMode = ref('setup-specific')
const selectedSetup = ref(null)
const loadingSetups = ref(true)
const statistics = ref({})
const globalStatistics = ref({})
const error = ref('')

// Methods from original change-history page
const loadBowSetups = async () => {
  try {
    loadingSetups.value = true
    
    // Load bow setups and active setup in parallel
    const [setupsResponse, activeSetupResponse] = await Promise.all([
      api.get('/bow-setups'),
      api.get('/user/active-bow-setup').catch(() => ({ active_bow_setup: null }))
    ])
    
    // Use passed props if available, otherwise use API response
    const setups = props.bowSetups.length > 0 ? props.bowSetups : (setupsResponse.setups || [])
    
    // Auto-select the active bow setup if it exists
    const activeBowSetup = activeSetupResponse.active_bow_setup
    if (activeBowSetup && setups.length > 0) {
      const activeSetup = setups.find(setup => setup.id === activeBowSetup.id)
      if (activeSetup) {
        selectedSetup.value = activeSetup
        await loadStatistics()
      }
    }
  } catch (err) {
    console.error('Error loading bow setups:', err)
    error.value = 'Failed to load bow setups'
  } finally {
    loadingSetups.value = false
  }
}

const selectBowSetup = async (setup) => {
  selectedSetup.value = setup
  await loadStatistics()
}

const loadStatistics = async () => {
  if (!selectedSetup.value) return
  
  try {
    const response = await api.get(`/bow-setups/${selectedSetup.value.id}/change-log/statistics`)
    statistics.value = response
  } catch (err) {
    console.error('Error loading statistics:', err)
    error.value = 'Failed to load change statistics'
  }
}

const loadGlobalStatistics = async () => {
  try {
    const response = await api.get('/change-log/global-statistics')
    globalStatistics.value = response
  } catch (err) {
    console.error('Error loading global statistics:', err)
    error.value = 'Failed to load global statistics'
  }
}

const handleStatisticsUpdate = (newStats) => {
  statistics.value = { ...statistics.value, ...newStats }
}

const handleGlobalStatisticsUpdate = (newStats) => {
  globalStatistics.value = { ...globalStatistics.value, ...newStats }
}

const handleError = (message) => {
  error.value = message
  // Auto-clear error after 5 seconds
  setTimeout(() => {
    error.value = ''
  }, 5000)
}

const getArrowChangesCount = () => {
  const arrowChanges = statistics.value.arrow_changes_by_type || {}
  return Object.values(arrowChanges).reduce((sum, count) => sum + count, 0)
}

const getEquipmentChangesCount = () => {
  const equipmentChanges = statistics.value.equipment_changes_by_type || {}
  return Object.values(equipmentChanges).reduce((sum, count) => sum + count, 0)
}

// Watch for view mode changes
watch(viewMode, (newMode) => {
  if (newMode === 'global') {
    loadGlobalStatistics()
  }
})

// Watch for bowSetups prop changes
watch(() => props.bowSetups, (newSetups) => {
  if (newSetups && newSetups.length > 0 && !selectedSetup.value) {
    // Auto-select first setup if none selected
    selectedSetup.value = newSetups[0]
    loadStatistics()
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  // Load setups if not provided via props
  if (props.bowSetups.length === 0) {
    loadBowSetups()
  } else {
    loadingSetups.value = false
  }
  
  // Load global statistics if starting in global mode
  if (viewMode.value === 'global') {
    loadGlobalStatistics()
  }
})
</script>

<style scoped>
.journal-change-log {
  width: 100%;
}

/* Header Styles */
.changelog-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.header-content {
  flex: 1;
  min-width: 0;
}

.header-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
}

.header-subtitle {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1rem;
  line-height: 1.5;
}

/* View Mode Toggle */
.view-mode-toggle {
  display: flex;
  background: var(--md-sys-color-surface-container-low);
  border-radius: 8px;
  padding: 4px;
}

.toggle-buttons {
  display: flex;
  gap: 0;
}

.toggle-btn {
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  background: transparent;
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
}

.toggle-btn.active {
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toggle-btn:hover:not(.active) {
  color: var(--md-sys-color-on-surface);
  background: var(--md-sys-color-surface-variant);
}

/* Setup Selector */
.setup-selector-card {
  background: var(--md-sys-color-surface-container);
  border-radius: 16px;
  border: 1px solid var(--md-sys-color-outline-variant);
  margin-bottom: 1.5rem;
}

.setup-selector-content {
  padding: 1.5rem;
}

.selector-title {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
}

.setup-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.setup-card {
  padding: 1rem;
  border: 2px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--md-sys-color-surface);
}

.setup-card:hover {
  border-color: var(--md-sys-color-outline);
}

.setup-card.selected {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
}

.setup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.setup-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.setup-type {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.setup-details {
  margin-bottom: 0.75rem;
}

.setup-spec {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 0.25rem;
}

.setup-description {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
}

.active-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* No setups state */
.no-setups {
  text-align: center;
  padding: 3rem 1rem;
}

.no-setups i {
  font-size: 3rem;
  color: var(--md-sys-color-outline);
  margin-bottom: 1rem;
}

.no-setups h5 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.no-setups p {
  margin: 0 0 1.5rem 0;
  color: var(--md-sys-color-on-surface-variant);
}

/* Loading setups state */
.loading-setups {
  text-align: center;
  padding: 2rem 1rem;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--md-sys-color-outline-variant);
  border-top: 2px solid var(--md-sys-color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-setups p {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
}

/* Statistics Grid */
.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
}

.stat-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.stat-icon i {
  font-size: 1.25rem;
}

.stat-card:nth-child(1) .stat-icon {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.stat-card:nth-child(2) .stat-icon {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.stat-card:nth-child(3) .stat-icon {
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
}

.stat-card:nth-child(4) .stat-icon {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
}

.stat-value {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
}

/* Global Activity Card */
.global-activity-card {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 16px;
  padding: 1.5rem;
}

.activity-title {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
}

/* Change History Card */
.change-history-card {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 16px;
  padding: 1.5rem;
}

/* Welcome Message */
.welcome-message {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 16px;
}

.welcome-message i {
  font-size: 4rem;
  color: var(--md-sys-color-primary);
  margin-bottom: 1rem;
}

.welcome-message h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.welcome-message p {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

/* Error Toast */
.error-toast {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.error-content {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  gap: 0.5rem;
}

.error-close {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem;
  margin-left: 0.5rem;
  opacity: 0.8;
  transition: opacity 0.2s ease;
}

.error-close:hover {
  opacity: 1;
}

/* Responsive */
@media (max-width: 768px) {
  .changelog-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .view-mode-toggle {
    align-self: stretch;
  }
  
  .toggle-buttons {
    flex: 1;
  }
  
  .toggle-btn {
    flex: 1;
    justify-content: center;
  }
  
  .setup-grid {
    grid-template-columns: 1fr;
  }
  
  .statistics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .error-toast {
    left: 1rem;
    right: 1rem;
  }
  
  .welcome-message {
    padding: 2rem 1rem;
  }
}

@media (max-width: 480px) {
  .statistics-grid {
    grid-template-columns: 1fr;
  }
  
  .header-title {
    font-size: 1.5rem;
  }
}
</style>