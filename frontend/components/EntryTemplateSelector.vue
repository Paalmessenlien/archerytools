<template>
  <div class="entry-template-selector">
    <div class="template-header">
      <h3 class="template-title">
        <i class="fas fa-magic mr-2"></i>
        Choose a Template
      </h3>
      <p class="template-subtitle">Get started faster with pre-filled content</p>
    </div>

    <div class="template-options">
      <!-- No Template Option -->
      <div 
        class="template-option"
        :class="{ selected: !selectedTemplate }"
        @click="selectTemplate(null)"
      >
        <div class="template-icon">
          <i class="fas fa-edit"></i>
        </div>
        <div class="template-content">
          <h4>Blank Entry</h4>
          <p>Start with a completely blank entry</p>
        </div>
      </div>

      <!-- System Templates -->
      <div 
        v-for="template in systemTemplates" 
        :key="`system-${template.id}`"
        class="template-option"
        :class="{ selected: selectedTemplate?.id === template.id }"
        @click="selectTemplate(template)"
      >
        <div class="template-icon" :class="`icon-${template.entry_type}`">
          <i :class="getEntryTypeIcon(template.entry_type)"></i>
        </div>
        <div class="template-content">
          <h4>{{ template.name }}</h4>
          <p>{{ template.description }}</p>
          <div class="template-preview">
            <span class="preview-title">{{ template.title_template }}</span>
          </div>
        </div>
      </div>

      <!-- User Templates -->
      <div 
        v-if="userTemplates.length" 
        class="template-divider"
      >
        <span>My Templates</span>
      </div>
      
      <div 
        v-for="template in userTemplates" 
        :key="`user-${template.id}`"
        class="template-option user-template"
        :class="{ selected: selectedTemplate?.id === template.id }"
        @click="selectTemplate(template)"
      >
        <div class="template-icon">
          <i class="fas fa-user-edit"></i>
        </div>
        <div class="template-content">
          <h4>{{ template.name }}</h4>
          <p>{{ template.description || 'Custom template' }}</p>
          <div class="template-preview">
            <span class="preview-title">{{ template.title_template }}</span>
          </div>
        </div>
        <div class="template-actions">
          <button 
            @click.stop="editTemplate(template)" 
            class="action-btn"
            title="Edit template"
          >
            <i class="fas fa-edit"></i>
          </button>
          <button 
            @click.stop="deleteTemplate(template)" 
            class="action-btn delete"
            title="Delete template"
          >
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Template Preview -->
    <div v-if="selectedTemplate" class="template-preview-section">
      <h4 class="preview-header">Template Preview</h4>
      <div class="preview-content">
        <div class="preview-field">
          <label>Title:</label>
          <span>{{ selectedTemplate.title_template }}</span>
        </div>
        <div class="preview-field">
          <label>Content:</label>
          <div class="preview-text">{{ selectedTemplate.content_template }}</div>
        </div>
        <div v-if="selectedTemplate.suggested_tags" class="preview-field">
          <label>Suggested Tags:</label>
          <div class="preview-tags">
            <span 
              v-for="tag in parseTags(selectedTemplate.suggested_tags)" 
              :key="tag"
              class="preview-tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="template-actions-footer">
      <CustomButton @click="$emit('cancel')" variant="outlined">
        Cancel
      </CustomButton>
      <CustomButton @click="createNewTemplate" variant="outlined" icon="fas fa-plus">
        New Template
      </CustomButton>
      <CustomButton @click="applyTemplate" variant="primary" :disabled="!canApply">
        {{ selectedTemplate ? 'Use Template' : 'Start Blank' }}
      </CustomButton>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'
import { useGlobalNotifications } from '@/composables/useNotificationSystem'

const props = defineProps({
  entryType: String,
  show: Boolean
})

const emit = defineEmits(['template-selected', 'cancel', 'new-template'])

// Composables
const api = useApi()
const notifications = useGlobalNotifications()

// Reactive data
const selectedTemplate = ref(null)
const systemTemplates = ref([])
const userTemplates = ref([])
const loading = ref(false)

// Computed
const canApply = computed(() => true) // Always allow application, even for blank

// System template definitions
const defaultSystemTemplates = [
  {
    id: 'tuning_session',
    name: 'Tuning Session',
    entry_type: 'tuning_session',
    description: 'Document a detailed tuning session',
    title_template: 'Tuning Session - [Date]',
    content_template: `**Setup Used:** [Bow Setup Name]

**Goal:** What I wanted to achieve today

**Initial State:**
- Current point of impact:
- Paper tune result:
- Walk-back test result:

**Changes Made:**
1. 
2. 
3. 

**Results:**
- New point of impact:
- Improvement noticed:
- Next steps:

**Notes:**
Additional observations and thoughts...`,
    suggested_tags: '["tuning", "arrows", "sight", "rest"]'
  },
  {
    id: 'equipment_change',
    name: 'Equipment Change',
    entry_type: 'equipment_change',
    description: 'Log equipment installation or changes',
    title_template: 'Installed [Equipment Name]',
    content_template: `**Equipment Changed:** [Old Equipment] → [New Equipment]

**Reason for Change:**
Why I made this change...

**Installation Notes:**
- Installation process:
- Any issues encountered:
- Settings used:

**First Impressions:**
- How it feels:
- Initial performance:
- Comparison to previous:

**Next Actions:**
- Tuning needed:
- Testing planned:`,
    suggested_tags: '["equipment", "upgrade", "installation"]'
  },
  {
    id: 'shooting_notes',
    name: 'Practice Session',
    entry_type: 'shooting_notes',
    description: 'Record practice session details',
    title_template: 'Practice Session - [Location/Date]',
    content_template: `**Session Details:**
- Location: [Range/Location]
- Distance: [Yards/Meters]
- Arrows shot: [Number]
- Duration: [Time]

**Weather Conditions:**
- Temperature:
- Wind:
- Lighting:

**Performance:**
- Best group size:
- Average score:
- Consistency:

**Focus Areas:**
- What I worked on:
- Improvements noticed:
- Areas needing work:

**Equipment Performance:**
- How the bow felt:
- Arrow flight:
- Any issues:

**Next Session Goals:**
What to focus on next time...`,
    suggested_tags: '["practice", "shooting", "performance", "scores"]'
  },
  {
    id: 'maintenance',
    name: 'Maintenance Log',
    entry_type: 'maintenance',
    description: 'Track maintenance and servicing',
    title_template: 'Maintenance - [Equipment/Date]',
    content_template: `**Equipment Serviced:** [Bow/Component]

**Maintenance Performed:**
- [ ] String/cable inspection
- [ ] Cam timing check
- [ ] Rest alignment
- [ ] Sight inspection
- [ ] Arrow inspection
- [ ] Other: 

**Issues Found:**
List any problems discovered...

**Repairs Made:**
Detail any repairs or adjustments...

**Parts Replaced:**
- 
- 

**Next Maintenance Due:** [Date]

**Notes:**
Additional observations...`,
    suggested_tags: '["maintenance", "service", "inspection", "repair"]'
  },
  {
    id: 'competition_prep',
    name: 'Competition Prep',
    entry_type: 'shooting_notes',
    description: 'Prepare for upcoming competitions',
    title_template: 'Competition Prep - [Event Name]',
    content_template: `**Upcoming Event:** [Competition Name]
**Date:** [Date]
**Location:** [Venue]
**Distance:** [Yards/Meters]

**Preparation Checklist:**
- [ ] Equipment tuned and verified
- [ ] Backup equipment ready
- [ ] Arrows checked and matched
- [ ] Practice at competition distance
- [ ] Mental preparation
- [ ] Physical conditioning

**Equipment Setup:**
- Bow setup confirmed: [Setup Name]
- Sight marks verified:
- Rest position locked:
- String condition: Good/Needs replacement

**Practice Results:**
Recent practice scores and consistency...

**Goals:**
- Primary goal:
- Secondary goals:
- Process goals:

**Strategy Notes:**
Competition day strategy and mindset...`,
    suggested_tags: '["competition", "preparation", "practice", "goals"]'
  }
]

// Methods
const loadTemplates = async () => {
  loading.value = true
  try {
    // Load system templates (use defaults if API not available)
    systemTemplates.value = defaultSystemTemplates.filter(template => {
      return !props.entryType || template.entry_type === props.entryType
    })

    // Load user templates from API
    try {
      const response = await api.get('/journal/templates')
      if (response.success && response.data) {
        userTemplates.value = response.data.filter(template => {
          return !props.entryType || template.entry_type === props.entryType
        })
      }
    } catch (apiError) {
      // API not available yet, use empty array
      userTemplates.value = []
    }
  } catch (error) {
    console.error('Error loading templates:', error)
    notifications.showError('Failed to load templates')
  } finally {
    loading.value = false
  }
}

const selectTemplate = (template) => {
  selectedTemplate.value = template
}

const applyTemplate = () => {
  const templateData = selectedTemplate.value ? {
    title: selectedTemplate.value.title_template || '',
    content: selectedTemplate.value.content_template || '',
    tags: selectedTemplate.value.suggested_tags ? parseTags(selectedTemplate.value.suggested_tags) : [],
    entry_type: selectedTemplate.value.entry_type || props.entryType
  } : {
    title: '',
    content: '',
    tags: [],
    entry_type: props.entryType
  }
  
  emit('template-selected', templateData)
}

const createNewTemplate = () => {
  emit('new-template')
}

const editTemplate = (template) => {
  // TODO: Implement template editing
  notifications.showInfo('Template editing coming soon')
}

const deleteTemplate = async (template) => {
  if (!confirm(`Delete template "${template.name}"?`)) return
  
  try {
    const response = await api.delete(`/journal/templates/${template.id}`)
    if (response.success) {
      userTemplates.value = userTemplates.value.filter(t => t.id !== template.id)
      notifications.showSuccess('Template deleted')
      
      // Clear selection if deleted template was selected
      if (selectedTemplate.value?.id === template.id) {
        selectedTemplate.value = null
      }
    } else {
      notifications.showError(response.error || 'Failed to delete template')
    }
  } catch (error) {
    console.error('Error deleting template:', error)
    notifications.showError('Failed to delete template')
  }
}

const parseTags = (tagsString) => {
  try {
    return JSON.parse(tagsString || '[]')
  } catch {
    return tagsString ? tagsString.split(',').map(t => t.trim()) : []
  }
}

const getEntryTypeIcon = (entryType) => {
  const icons = {
    general: 'fas fa-sticky-note',
    setup_change: 'fas fa-tools',
    equipment_change: 'fas fa-cog',
    arrow_change: 'fas fa-bullseye',
    tuning_session: 'fas fa-crosshairs',
    shooting_notes: 'fas fa-target',
    maintenance: 'fas fa-wrench',
    upgrade: 'fas fa-arrow-up',
    competition: 'fas fa-trophy'
  }
  return icons[entryType] || 'fas fa-sticky-note'
}

// Lifecycle
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