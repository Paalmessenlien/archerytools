<template>
  <div class="entry-template-selector">
    <!-- Header -->
    <div class="selector-header">
      <div class="header-content">
        <h3 class="selector-title">
          <i class="fas fa-magic mr-2"></i>
          Choose a Template
        </h3>
        <p class="selector-subtitle">
          {{ templates?.length || 0 }} template{{ (templates?.length || 0) === 1 ? '' : 's' }} available
          <span v-if="selectedEntryType"> for {{ getEntryTypeDisplayName(selectedEntryType) }}</span>
        </p>
      </div>
      <button 
        @click="$emit('cancel')"
        class="close-btn"
        type="button"
        aria-label="Close template selector"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- Template Grid -->
    <div class="templates-container">
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading templates...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <div class="error-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h4>Failed to Load Templates</h4>
        <p>{{ error }}</p>
        <button @click="loadTemplates" class="retry-btn">
          <i class="fas fa-redo mr-1"></i>
          Try Again
        </button>
      </div>

      <div v-else-if="templates.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-file-alt"></i>
        </div>
        <h4>No Templates Found</h4>
        <p>No templates are available yet. Start by creating your first template.</p>
        <button @click="$emit('new-template')" class="create-template-btn">
          <i class="fas fa-plus mr-1"></i>
          Create New Template
        </button>
      </div>

      <div v-else class="templates-grid">
        <!-- System Templates Section -->
        <div v-if="systemTemplates.length > 0" class="template-section">
          <h4 class="section-heading">
            <i class="fas fa-star mr-2"></i>
            System Templates
          </h4>
          <div class="template-cards">
            <div 
              v-for="template in systemTemplates" 
              :key="`system-${template.id}`"
              class="template-card system-template"
              @click="selectTemplate(template)"
            >
              <div class="template-header">
                <div class="template-icon">
                  <i :class="getTemplateIcon(template.category)"></i>
                </div>
                <div class="template-meta">
                  <span class="template-category">{{ getCategoryDisplayName(template.category) }}</span>
                  <div class="template-stats">
                    <span class="usage-count" v-if="template.usage_count > 0">
                      <i class="fas fa-fire"></i>
                      {{ template.usage_count }}
                    </span>
                    <span class="system-badge">
                      <i class="fas fa-shield-alt"></i>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="template-content">
                <h5 class="template-name">{{ template.name }}</h5>
                <p class="template-description">{{ template.description }}</p>
                
                <!-- Template Preview -->
                <div class="template-preview" v-if="template.parsed_data">
                  <div class="preview-field">
                    <strong>Title:</strong> {{ template.parsed_data.title || 'Dynamic title' }}
                  </div>
                  <div class="preview-field">
                    <strong>Type:</strong> {{ getEntryTypeDisplayName(template.parsed_data.entry_type) }}
                  </div>
                  <div class="preview-field" v-if="template.parsed_data.suggested_tags?.length">
                    <strong>Tags:</strong> {{ template.parsed_data.suggested_tags.join(', ') }}
                  </div>
                </div>
              </div>

              <div class="template-actions">
                <button class="select-btn" @click.stop="selectTemplate(template)">
                  <i class="fas fa-check mr-1"></i>
                  Use Template
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- User Templates Section -->
        <div v-if="userTemplates.length > 0" class="template-section">
          <h4 class="section-heading">
            <i class="fas fa-user mr-2"></i>
            Your Templates
          </h4>
          <div class="template-cards">
            <div 
              v-for="template in userTemplates" 
              :key="`user-${template.id}`"
              class="template-card user-template"
              @click="selectTemplate(template)"
            >
              <div class="template-header">
                <div class="template-icon">
                  <i :class="getTemplateIcon(template.category)"></i>
                </div>
                <div class="template-meta">
                  <span class="template-category">{{ getCategoryDisplayName(template.category) }}</span>
                  <div class="template-stats">
                    <span class="usage-count" v-if="template.usage_count > 0">
                      <i class="fas fa-fire"></i>
                      {{ template.usage_count }}
                    </span>
                    <span class="created-date">
                      {{ formatDate(template.created_at) }}
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="template-content">
                <h5 class="template-name">{{ template.name }}</h5>
                <p class="template-description">{{ template.description }}</p>
                
                <!-- Template Preview -->
                <div class="template-preview" v-if="template.parsed_data">
                  <div class="preview-field">
                    <strong>Title:</strong> {{ template.parsed_data.title || 'Dynamic title' }}
                  </div>
                  <div class="preview-field">
                    <strong>Type:</strong> {{ getEntryTypeDisplayName(template.parsed_data.entry_type) }}
                  </div>
                  <div class="preview-field" v-if="template.parsed_data.suggested_tags?.length">
                    <strong>Tags:</strong> {{ template.parsed_data.suggested_tags.join(', ') }}
                  </div>
                </div>
              </div>

              <div class="template-actions">
                <button class="select-btn" @click.stop="selectTemplate(template)">
                  <i class="fas fa-check mr-1"></i>
                  Use Template
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Actions -->
    <div class="selector-footer">
      <div class="footer-left">
        <button @click="$emit('new-template')" class="new-template-btn">
          <i class="fas fa-plus mr-1"></i>
          Create New Template
        </button>
      </div>
      <div class="footer-right">
        <button @click="$emit('cancel')" class="cancel-btn">
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

const props = defineProps({
  entryType: String
})

const emit = defineEmits(['template-selected', 'cancel', 'new-template'])

// State
const isLoading = ref(true)
const error = ref(null)
const templates = ref([])
const selectedEntryType = ref(props.entryType || '')

// API composable
const { get } = useApi()

// Computed properties
const systemTemplates = computed(() => {
  return templates.value.filter(t => t.is_system_template)
})

const userTemplates = computed(() => {
  return templates.value.filter(t => !t.is_system_template)
})

// Methods
const loadTemplates = async () => {
  isLoading.value = true
  error.value = null

  try {
    const response = await get('/journal/templates')
    templates.value = response.data.templates.map(template => {
      // Parse the template_data JSON
      try {
        template.parsed_data = JSON.parse(template.template_data)
      } catch (e) {
        console.warn(`Failed to parse template data for template ${template.id}:`, e)
        template.parsed_data = {}
      }
      return template
    })
  } catch (err) {
    console.error('Failed to load templates:', err)
    error.value = err.message || 'Failed to load templates'
  } finally {
    isLoading.value = false
  }
}

const selectTemplate = (template) => {
  // Prepare template data for the journal form
  const templateData = {
    title: template.parsed_data.title || '',
    content: template.parsed_data.content || '',
    entry_type: template.parsed_data.entry_type || 'general',
    tags: template.parsed_data.suggested_tags || [],
    template_used: template.id
  }

  // Replace placeholders in template data
  const currentDate = new Date().toLocaleDateString()
  templateData.title = templateData.title.replace(/\{date\}/g, currentDate)
  templateData.content = templateData.content.replace(/\{date\}/g, currentDate)

  emit('template-selected', templateData)
}

// Helper functions
const getCategoryDisplayName = (category) => {
  const names = {
    general: 'General',
    tuning: 'Tuning',
    practice: 'Practice',
    competition: 'Competition',
    equipment: 'Equipment',
    maintenance: 'Maintenance'
  }
  return names[category] || category
}

const getEntryTypeDisplayName = (type) => {
  const names = {
    general: 'General Entry',
    setup_change: 'Setup Change',
    equipment_change: 'Equipment Change',
    arrow_change: 'Arrow Change',
    tuning_session: 'Tuning Session',
    shooting_notes: 'Shooting Notes',
    maintenance: 'Maintenance',
    upgrade: 'Upgrade'
  }
  return names[type] || type
}

const getTemplateIcon = (category) => {
  const icons = {
    general: 'fas fa-sticky-note',
    tuning: 'fas fa-crosshairs',
    practice: 'fas fa-target',
    competition: 'fas fa-trophy',
    equipment: 'fas fa-tools',
    maintenance: 'fas fa-wrench'
  }
  return icons[category] || 'fas fa-file-alt'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Initialize
onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.entry-template-selector {
  max-width: 800px;
  margin: 0 auto;
}

.template-header {
  text-align: center;
  margin-bottom: 2rem;
}

.template-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.template-subtitle {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.9rem;
}

.template-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.template-option {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  background: var(--md-sys-color-surface-container-lowest);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.template-option:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-container);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.template-option.selected {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.template-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  font-size: 1.25rem;
  flex-shrink: 0;
}

.template-option.selected .template-icon {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.template-content {
  flex: 1;
  min-width: 0;
}

.template-content h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.template-content p {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.4;
}

.template-option.selected .template-content p {
  color: var(--md-sys-color-on-primary-container);
  opacity: 0.8;
}

.template-preview {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  font-style: italic;
}

.preview-title {
  background: var(--md-sys-color-surface-container);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.template-option.selected .preview-title {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.template-divider {
  grid-column: 1 / -1;
  text-align: center;
  margin: 1rem 0;
  position: relative;
}

.template-divider span {
  background: var(--md-sys-color-surface);
  padding: 0 1rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
  font-size: 0.875rem;
}

.template-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--md-sys-color-outline-variant);
  z-index: -1;
}

.user-template {
  border-style: dashed;
}

.template-actions {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.template-option:hover .template-actions {
  opacity: 1;
}

.action-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: var(--md-sys-color-surface-container);
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--md-sys-color-secondary-container);
}

.action-btn.delete:hover {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
}

.template-preview-section {
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.preview-header {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.preview-field {
  margin-bottom: 1rem;
}

.preview-field label {
  display: block;
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.preview-text {
  background: var(--md-sys-color-surface-container);
  padding: 0.75rem;
  border-radius: 6px;
  font-family: monospace;
  font-size: 0.8rem;
  line-height: 1.4;
  white-space: pre-wrap;
  max-height: 150px;
  overflow-y: auto;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.preview-tag {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.template-actions-footer {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

/* Type-specific icon colors */
.icon-tuning_session { background: var(--md-sys-color-error-container) !important; }
.icon-equipment_change { background: var(--md-sys-color-secondary-container) !important; }
.icon-shooting_notes { background: var(--md-sys-color-primary-container) !important; }
.icon-maintenance { background: var(--md-sys-color-tertiary-container) !important; }

@media (max-width: 768px) {
  .template-options {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .template-option {
    padding: 0.75rem;
  }
  
  .template-icon {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  .template-actions-footer {
    flex-direction: column;
  }
}
</style>