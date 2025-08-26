<template>
  <!-- Modal Version -->
  <div v-if="mode === 'modal' && show" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <div class="modal-title-section">
          <h3 class="modal-title">{{ isEditing ? 'Edit Entry' : 'New Journal Entry' }}</h3>
          <div class="content-progress" v-if="!isEditing">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: contentProgress.percentage + '%' }"
                :class="`progress-${contentProgress.level}`"
              ></div>
            </div>
            <span class="progress-text">{{ contentProgress.score }}/{{ contentProgress.maxScore }} complete</span>
          </div>
        </div>
        <button @click="handleClose" class="modal-close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <!-- Validation Summary -->
        <div v-if="formState.showValidation && !isFormValid" class="validation-summary">
          <div class="validation-header">
            <i class="fas fa-exclamation-triangle"></i>
            <span>Please fix the following issues:</span>
          </div>
          <ul class="validation-list">
            <li v-for="(error, field) in formState.errors" :key="field">
              {{ error }}
            </li>
          </ul>
        </div>
        
        <!-- Submit Error -->
        <div v-if="formState.errors.submit" class="error-message">
          <i class="fas fa-exclamation-circle"></i>
          {{ formState.errors.submit }}
        </div>
        
        <form class="journal-form" @submit.prevent="handleSubmit">
          <JournalFormFields
            :form-data="formData"
            :bow-setups="bowSetups"
            :entry-types="entryTypes"
            :validation-results="validationResults"
            :character-counts="characterCounts"
            :limits="limits"
            :show-validation="formState.showValidation"
            :attached-images="attachedImages"
            :is-new-entry="!isEditing"
            @update:form-data="updateFormData"
            @image-uploaded="handleImageUploaded"
            @image-removed="handleImageRemoved"
            @image-error="handleImageError"
            @template-applied="onTemplateApplied"
          />
        </form>
      </div>

      <div class="modal-footer">
        <div class="footer-info">
          <span v-if="formState.isAutoSaving" class="auto-saving-indicator">
            <md-circular-progress indeterminate class="auto-save-spinner"></md-circular-progress>
            Auto-saving...
          </span>
          <span v-else-if="formState.hasChanges && !formState.lastSaved" class="changes-indicator">
            <i class="fas fa-circle"></i>
            Unsaved changes
          </span>
          <span v-else-if="formState.lastSaved && !formState.hasChanges" class="last-saved">
            <i class="fas fa-check"></i>
            Auto-saved {{ formatLastSaved(formState.lastSaved) }}
          </span>
          <span v-else-if="formState.lastSaved && formState.hasChanges" class="changes-since-save">
            <i class="fas fa-edit"></i>
            Changes since {{ formatLastSaved(formState.lastSaved) }}
          </span>
          <span v-if="formState.autoSaveError" class="auto-save-error">
            <i class="fas fa-exclamation-triangle"></i>
            {{ formState.autoSaveError }}
          </span>
        </div>
        <div class="footer-actions">
          <CustomButton @click="handleCancel" variant="outlined" :disabled="formState.isSubmitting">
            Cancel
          </CustomButton>
          <CustomButton 
            @click="handleSubmit" 
            variant="primary" 
            :disabled="formState.isSubmitting"
            :class="{ 'is-loading': formState.isSubmitting }"
          >
            <md-circular-progress v-if="formState.isSubmitting" indeterminate class="btn-loading"></md-circular-progress>
            <span v-if="!formState.isSubmitting">{{ isEditing ? 'Update Entry' : 'Create Entry' }}</span>
            <span v-else>{{ isEditing ? 'Updating...' : 'Creating...' }}</span>
          </CustomButton>
        </div>
      </div>
    </div>
  </div>

  <!-- Inline Version -->
  <div v-else-if="mode === 'inline'" class="journal-entry-form inline-form-container">
      <div class="form-header">
        <h3 class="form-title">
          <i class="fas fa-plus mr-2"></i>
          {{ isEditing ? 'Edit Journal Entry' : 'New Journal Entry' }}
        </h3>
        <p class="form-subtitle">{{ isEditing ? 'Update your entry details' : 'Document your archery journey' }}</p>
      </div>
      
      <form class="journal-form" @submit.prevent="handleSubmit">
        <JournalFormFields
          :form-data="formData"
          :bow-setups="bowSetups"
          :entry-types="entryTypes"
          :validation-results="validationResults"
          :character-counts="characterCounts"
          :limits="limits"
          :show-validation="formState.showValidation"
          :attached-images="attachedImages"
          :is-new-entry="!isEditing"
          @update:form-data="updateFormData"
          @image-uploaded="handleImageUploaded"
          @image-removed="handleImageRemoved"
          @image-error="handleImageError"
          @template-applied="onTemplateApplied"
        />
        
        <div class="form-actions">
          <div class="form-footer-info">
            <span v-if="formState.isAutoSaving" class="auto-saving-indicator">
              <md-circular-progress indeterminate class="auto-save-spinner"></md-circular-progress>
              Auto-saving...
            </span>
            <span v-else-if="formState.hasChanges && !formState.lastSaved" class="changes-indicator">
              <i class="fas fa-circle"></i>
              Unsaved changes
            </span>
            <span v-else-if="formState.lastSaved && !formState.hasChanges" class="last-saved">
              <i class="fas fa-check"></i>
              Auto-saved {{ formatLastSaved(formState.lastSaved) }}
            </span>
            <span v-else-if="formState.lastSaved && formState.hasChanges" class="changes-since-save">
              <i class="fas fa-edit"></i>
              Changes since {{ formatLastSaved(formState.lastSaved) }}
            </span>
            <span v-if="formState.autoSaveError" class="auto-save-error">
              <i class="fas fa-exclamation-triangle"></i>
              {{ formState.autoSaveError }}
            </span>
          </div>
          <div class="form-buttons">
            <CustomButton @click="handleCancel" variant="outlined" :disabled="formState.isSubmitting">
              Cancel
            </CustomButton>
            <CustomButton 
              @click="handleSubmit" 
              variant="primary" 
              :disabled="formState.isSubmitting"
              :class="{ 'is-loading': formState.isSubmitting }"
            >
              <md-circular-progress v-if="formState.isSubmitting" indeterminate class="btn-loading"></md-circular-progress>
              <span v-if="!formState.isSubmitting">{{ isEditing ? 'Update Entry' : 'Create Entry' }}</span>
              <span v-else>{{ isEditing ? 'Updating...' : 'Creating...' }}</span>
            </CustomButton>
          </div>
        </div>
      </form>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'modal', // 'modal' or 'inline'
    validator: (value) => ['modal', 'inline'].includes(value)
  },
  show: {
    type: Boolean,
    default: false
  },
  entry: Object,
  bowSetups: Array,
  entryTypes: Array
})

const emit = defineEmits(['close', 'cancel', 'save', 'auto-save', 'draft-found'])

// Image management state
const attachedImages = computed(() => formData.value.images || [])

const isEditing = computed(() => !!props.entry?.id)

const formData = ref({
  title: '',
  content: '',
  bow_setup_id: null,
  entry_type: 'general',
  tagsString: '',
  is_private: false,
  images: [] // Array of image objects { url, uploadedAt, alt }
})

// Enhanced form state for better UX
const formState = reactive({
  isSubmitting: false,
  hasChanges: false,
  errors: {},
  warnings: {},
  showValidation: false,
  lastSaved: null,
  autoSaveEnabled: true,
  isAutoSaving: false,
  autoSaveError: null
})

// Auto-save configuration
const AUTO_SAVE_DELAY = 3000 // 3 seconds after user stops typing
const AUTO_SAVE_KEY_PREFIX = 'journal_draft_'
let autoSaveTimeout = null

// Character counts for validation feedback
const characterCounts = computed(() => ({
  title: formData.value.title?.length || 0,
  content: formData.value.content?.length || 0,
  tags: formData.value.tagsString?.length || 0
}))

// Validation limits
const limits = {
  title: { min: 3, max: 200 },
  content: { min: 10, max: 5000 },
  tags: { max: 500 }
}

// Enhanced validation with detailed feedback
const validationResults = computed(() => {
  const results = {
    title: { isValid: true, message: '' },
    content: { isValid: true, message: '' },
    tags: { isValid: true, message: '' },
    overall: true
  }
  
  // Title validation
  const titleLength = characterCounts.value.title
  if (!formData.value.title?.trim()) {
    results.title = { isValid: false, message: 'Title is required' }
  } else if (titleLength < limits.title.min) {
    results.title = { isValid: false, message: `Title must be at least ${limits.title.min} characters` }
  } else if (titleLength > limits.title.max) {
    results.title = { isValid: false, message: `Title cannot exceed ${limits.title.max} characters` }
  }
  
  // Content validation
  const contentLength = characterCounts.value.content
  if (!formData.value.content?.trim()) {
    results.content = { isValid: false, message: 'Content is required' }
  } else if (contentLength < limits.content.min) {
    results.content = { isValid: false, message: `Content must be at least ${limits.content.min} characters` }
  } else if (contentLength > limits.content.max) {
    results.content = { isValid: false, message: `Content cannot exceed ${limits.content.max} characters` }
  }
  
  // Tags validation
  if (characterCounts.value.tags > limits.tags.max) {
    results.tags = { isValid: false, message: `Tags cannot exceed ${limits.tags.max} characters` }
  }
  
  // Overall validation
  results.overall = results.title.isValid && results.content.isValid && results.tags.isValid
  
  return results
})

const isFormValid = computed(() => validationResults.value.overall)

// Progress indicator for content completeness
const contentProgress = computed(() => {
  let score = 0
  const maxScore = 5
  
  if (formData.value.title?.trim()) score++
  if (formData.value.content?.trim() && formData.value.content.length >= limits.content.min) score++
  if (formData.value.bow_setup_id) score++
  if (formData.value.entry_type !== 'general') score++
  if (formData.value.tagsString?.trim()) score++
  
  return {
    score,
    maxScore,
    percentage: Math.round((score / maxScore) * 100),
    level: score <= 2 ? 'basic' : score <= 4 ? 'good' : 'complete'
  }
})

const updateFormData = (field, value) => {
  formData.value[field] = value
  formState.hasChanges = true
  
  // Clear field-specific errors when user starts typing
  if (formState.errors[field]) {
    delete formState.errors[field]
  }
  
  // Real-time validation for immediate feedback
  if (formState.showValidation) {
    validateField(field)
  }
  
  // Trigger auto-save after delay
  if (formState.autoSaveEnabled && !isEditing.value) {
    scheduleAutoSave()
  }
}

// Field-specific validation
const validateField = (field) => {
  const validation = validationResults.value[field]
  if (validation && !validation.isValid) {
    formState.errors[field] = validation.message
  } else if (formState.errors[field]) {
    delete formState.errors[field]
  }
}

// Validate all fields
const validateAllFields = () => {
  formState.showValidation = true
  formState.errors = {}
  
  Object.keys(validationResults.value).forEach(field => {
    if (field !== 'overall') {
      validateField(field)
    }
  })
  
  return Object.keys(formState.errors).length === 0
}

const resetForm = () => {
  formData.value = {
    title: '',
    content: '',
    bow_setup_id: null,
    entry_type: 'general',
    tagsString: '',
    is_private: false,
    images: []
  }
  
  // Reset form state
  formState.hasChanges = false
  formState.errors = {}
  formState.warnings = {}
  formState.showValidation = false
  formState.lastSaved = null
  formState.isAutoSaving = false
  formState.autoSaveError = null
  
  // Clear any pending auto-save
  clearTimeout(autoSaveTimeout)
}

const populateForm = (entry) => {
  if (entry) {
    formData.value = {
      title: entry.title || '',
      content: entry.content || '',
      bow_setup_id: entry.bow_setup_id || null,
      entry_type: entry.entry_type || 'general',
      tagsString: entry.tags ? entry.tags.join(', ') : '',
      is_private: entry.is_private || false,
      images: entry.images || []
    }
    
    // Reset form state when populating with existing entry
    formState.hasChanges = false
    formState.errors = {}
    formState.showValidation = false
  }
}

// Handle unsaved changes warning
const handleCancel = () => {
  if (formState.hasChanges) {
    if (confirm('You have unsaved changes. Are you sure you want to cancel?')) {
      emit('cancel')
    }
  } else {
    emit('cancel')
  }
}

const handleClose = () => {
  if (formState.hasChanges) {
    if (confirm('You have unsaved changes. Are you sure you want to close?')) {
      emit('close')
    }
  } else {
    emit('close')
  }
}

const handleSubmit = async () => {
  // Validate all fields first
  if (!validateAllFields()) {
    return
  }
  
  formState.isSubmitting = true
  
  try {
    const submitData = {
      title: formData.value.title.trim(),
      content: formData.value.content.trim(),
      bow_setup_id: formData.value.bow_setup_id,
      entry_type: formData.value.entry_type,
      tags: formData.value.tagsString 
        ? formData.value.tagsString.split(',').map(tag => tag.trim()).filter(Boolean)
        : [],
      is_private: formData.value.is_private,
      images: formData.value.images || []
    }

    await emit('save', submitData)
    
    // Clear auto-saved draft on successful save
    clearAutoSavedDraft()
    
    // Reset form state on successful save
    formState.hasChanges = false
    formState.lastSaved = new Date().toISOString()
    formState.showValidation = false
    formState.errors = {}
    
  } catch (error) {
    formState.errors.submit = 'Failed to save entry. Please try again.'
  } finally {
    formState.isSubmitting = false
  }
}

// Initialize form when component is used
watch(() => props.show, (newValue) => {
  if (newValue || props.mode === 'inline') {
    if (props.entry) {
      populateForm(props.entry)
    } else {
      resetForm()
    }
  }
})

watch(() => props.entry, (newEntry) => {
  if ((props.show || props.mode === 'inline') && newEntry) {
    populateForm(newEntry)
  }
})

// Helper function to format last saved time
const formatLastSaved = (timestamp) => {
  if (!timestamp) return ''
  
  const now = new Date()
  const saved = new Date(timestamp)
  const diffInSeconds = Math.floor((now - saved) / 1000)
  
  if (diffInSeconds < 60) return 'just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return saved.toLocaleDateString()
}

// Auto-save functionality
const getAutoSaveKey = () => {
  return `${AUTO_SAVE_KEY_PREFIX}${isEditing.value ? props.entry?.id || 'edit' : 'new'}`
}

const scheduleAutoSave = () => {
  clearTimeout(autoSaveTimeout)
  formState.autoSaveError = null
  
  autoSaveTimeout = setTimeout(() => {
    if (formState.hasChanges && !formState.isSubmitting) {
      performAutoSave()
    }
  }, AUTO_SAVE_DELAY)
}

const performAutoSave = async () => {
  if (!process.client || formState.isSubmitting || !formState.hasChanges) return
  
  formState.isAutoSaving = true
  
  try {
    const draftData = {
      ...formData.value,
      timestamp: new Date().toISOString(),
      isEditing: isEditing.value,
      entryId: props.entry?.id
    }
    
    localStorage.setItem(getAutoSaveKey(), JSON.stringify(draftData))
    formState.lastSaved = draftData.timestamp
    formState.autoSaveError = null
    
    // Emit auto-save event for parent component to handle
    emit('auto-save', draftData)
    
  } catch (error) {
    console.warn('Auto-save failed:', error)
    formState.autoSaveError = 'Auto-save failed'
  } finally {
    formState.isAutoSaving = false
  }
}

const loadAutoSavedDraft = () => {
  if (!process.client || isEditing.value) return false
  
  try {
    const saved = localStorage.getItem(getAutoSaveKey())
    if (saved) {
      const draftData = JSON.parse(saved)
      
      // Check if draft is recent (within 24 hours)
      const draftTime = new Date(draftData.timestamp)
      const now = new Date()
      const hoursDiff = (now - draftTime) / (1000 * 60 * 60)
      
      if (hoursDiff < 24) {
        return draftData
      } else {
        // Remove old draft
        localStorage.removeItem(getAutoSaveKey())
      }
    }
  } catch (error) {
    console.warn('Failed to load auto-saved draft:', error)
  }
  
  return false
}

const clearAutoSavedDraft = () => {
  if (!process.client) return
  try {
    localStorage.removeItem(getAutoSaveKey())
  } catch (error) {
    console.warn('Failed to clear auto-saved draft:', error)
  }
}

const restoreFromDraft = (draftData) => {
  formData.value = {
    title: draftData.title || '',
    content: draftData.content || '',
    bow_setup_id: draftData.bow_setup_id || null,
    entry_type: draftData.entry_type || 'general',
    tagsString: draftData.tagsString || '',
    is_private: draftData.is_private || false,
    images: draftData.images || []
  }
  
  formState.hasChanges = true
  formState.lastSaved = draftData.timestamp
}

// Initialize form for inline mode
onMounted(() => {
  if (props.mode === 'inline') {
    if (props.entry) {
      populateForm(props.entry)
    } else {
      resetForm()
      
      // Check for auto-saved draft for new entries
      const draft = loadAutoSavedDraft()
      if (draft) {
        // Show restore option to user
        emit('draft-found', draft)
      }
    }
  }
})

// Image management functions
const handleImageUploaded = (imageData) => {
  if (!formData.value.images) {
    formData.value.images = []
  }
  formData.value.images.push(imageData)
  formState.hasChanges = true
  
  // Trigger auto-save after image upload
  if (formState.autoSaveEnabled && !isEditing.value) {
    scheduleAutoSave()
  }
}

const handleImageRemoved = (index) => {
  if (formData.value.images && index >= 0 && index < formData.value.images.length) {
    formData.value.images.splice(index, 1)
    formState.hasChanges = true
    
    // Trigger auto-save after image removal
    if (formState.autoSaveEnabled && !isEditing.value) {
      scheduleAutoSave()
    }
  }
}

const handleImageError = (error) => {
  formState.errors.image = error
  
  // Clear image error after 5 seconds
  setTimeout(() => {
    if (formState.errors.image === error) {
      delete formState.errors.image
    }
  }, 5000)
}

// Template handler
const onTemplateApplied = (templateData) => {
  // Mark form as having changes when template is applied
  formState.hasChanges = true
  
  // Clear validation errors since template provides valid content
  formState.showValidation = false
  
  // Show success message
  if (templateData.name) {
    notifications.showSuccess(`Applied "${templateData.name}" template`)
  }
  
  // Start auto-save timer
  startAutoSaveTimer()
}

// Prevent accidental navigation with unsaved changes
if (process.client) {
  window.addEventListener('beforeunload', (e) => {
    if (formState.hasChanges) {
      e.preventDefault()
      e.returnValue = 'You have unsaved changes. Are you sure you want to leave?'
      return e.returnValue
    }
  })
}
</script>

<style scoped>

/* Inline Form Styles */
.inline-form-container {
  background: var(--md-sys-color-surface);
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid var(--md-sys-color-outline-variant);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.form-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.form-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
}

.form-subtitle {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
  margin: 0;
}

.journal-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999 !important;
  padding: 1rem;
}

.modal-content {
  background: var(--md-sys-color-surface);
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  border: 1px solid var(--md-sys-color-outline-variant);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin: 0;
}

.modal-close-btn {
  background: none;
  border: none;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1.25rem;
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-close-btn:hover {
  background: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-on-surface);
}

.modal-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

/* Enhanced form styling for validation and UX */
.modal-title-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.content-progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--md-sys-color-surface-container-highest);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.progress-fill.progress-basic {
  background: var(--md-sys-color-error);
}

.progress-fill.progress-good {
  background: var(--md-sys-color-secondary);
}

.progress-fill.progress-complete {
  background: var(--md-sys-color-primary);
}

.progress-text {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
  white-space: nowrap;
}

.validation-summary {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.validation-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.validation-list {
  margin: 0;
  padding-left: 1.5rem;
}

.validation-list li {
  margin-bottom: 0.25rem;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
}

.footer-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.changes-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-primary);
  font-weight: 500;
}

.changes-indicator i {
  font-size: 0.5rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.last-saved {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-primary);
  font-weight: 500;
}

.auto-saving-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-secondary);
  font-weight: 500;
}

.auto-save-spinner {
  width: 14px;
  height: 14px;
}

.changes-since-save {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-tertiary);
  font-weight: 500;
}

.auto-save-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-error);
  font-weight: 500;
  font-size: 0.8rem;
}

.btn-loading {
  width: 16px;
  height: 16px;
  margin-right: 0.5rem;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.form-footer-info {
  display: flex;
  align-items: center;
}

.form-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .inline-form-container {
    padding: 1.5rem;
  }
  
  .form-title {
    font-size: 1.25rem;
  }
  
  .form-buttons {
    flex-direction: column;
  }
  
  .footer-actions {
    flex-direction: column;
  }
  
  .modal-wrapper md-dialog {
    --md-dialog-container-max-width: 100%;
    --md-dialog-container-margin: 1rem;
  }
  
  .content-progress {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .progress-text {
    align-self: center;
  }
}
</style>