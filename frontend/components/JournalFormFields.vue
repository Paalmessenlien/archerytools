<template>
  <div class="journal-form-fields">
    <!-- Template Selection Section -->
    <div v-if="showTemplateSelector" class="form-group template-section">
      <div class="template-header">
        <h3 class="section-title">
          <i class="fas fa-magic mr-2"></i>
          Start with a Template
        </h3>
        <button 
          @click="showTemplateSelector = false"
          class="skip-template-btn"
          type="button"
        >
          <i class="fas fa-times mr-1"></i>
          Skip
        </button>
      </div>
      
      <!-- Quick Template Options -->
      <div class="quick-templates">
        <div 
          v-for="template in quickTemplates" 
          :key="template.id"
          class="quick-template-card"
          @click="applyQuickTemplate(template)"
        >
          <div class="template-icon" :class="`icon-${template.entry_type}`">
            <i :class="getEntryTypeIcon(template.entry_type)"></i>
          </div>
          <div class="template-info">
            <h4>{{ template.name }}</h4>
            <p>{{ template.description }}</p>
          </div>
        </div>
      </div>
      
      <div class="template-actions">
        <CustomButton 
          @click="showFullTemplateSelector = true" 
          variant="outlined" 
          icon="fas fa-th"
        >
          Browse All Templates
        </CustomButton>
      </div>
    </div>

    <!-- Title Field -->
    <div class="form-group">
      <div class="form-label-section">
        <label class="form-label">Title *</label>
        <div class="character-count" :class="{ 'over-limit': characterCounts?.title > limits?.title?.max }">
          {{ characterCounts?.title || 0 }} / {{ limits?.title?.max || 200 }}
        </div>
      </div>
      <input
        v-model="titleProxy"
        type="text"
        placeholder="Enter entry title..."
        required
        class="form-input"
        :class="{ 
          'has-error': showValidation && validationResults?.title && !validationResults.title.isValid,
          'has-success': showValidation && validationResults?.title && validationResults.title.isValid && formData.title
        }"
      />
      <div v-if="showValidation && validationResults?.title && !validationResults.title.isValid" class="field-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ validationResults.title.message }}
      </div>
    </div>

    <!-- Bow Setup Field -->
    <div class="form-group">
      <label class="form-label">Bow Setup (Optional)</label>
      <select
        :value="formData.bow_setup_id || ''"
        @change="(e) => $emit('update:form-data', 'bow_setup_id', e.target.value || null)"
        class="form-select"
      >
        <option value="">General Notes (not about a specific setup)</option>
        <option 
          v-for="setup in bowSetups" 
          :key="setup.id"
          :value="setup.id"
        >
          {{ setup.name }} - {{ setup.bow_type }} • {{ getSetupDetails(setup) }}
        </option>
      </select>
    </div>

    <!-- Entry Type Field -->
    <div class="form-group">
      <label class="form-label">Entry Type *</label>
      <select
        :value="formData.entry_type || ''"
        @change="(e) => $emit('update:form-data', 'entry_type', e.target.value)"
        required
        class="form-select"
        :class="{ 
          'has-error': showValidation && validationResults?.entry_type && !validationResults.entry_type.isValid,
          'has-success': showValidation && validationResults?.entry_type && validationResults.entry_type.isValid && formData.entry_type
        }"
      >
        <option value="" disabled>Select entry type...</option>
        <option 
          v-for="type in entryTypes" 
          :key="type.value"
          :value="type.value"
        >
          {{ type.label }} - {{ getEntryTypeDescription(type.value) }}
        </option>
      </select>
      <div v-if="showValidation && validationResults?.entry_type && !validationResults.entry_type.isValid" class="field-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ validationResults.entry_type.message }}
      </div>
    </div>

    <!-- Equipment/Arrow Linking Section -->
    <div v-if="showEquipmentLinking" class="form-group equipment-linking-section">
      <div class="equipment-linking-header">
        <label class="form-label">
          <i :class="getEquipmentLinkingIcon(formData.entry_type)"></i>
          {{ getEquipmentLinkingLabel(formData.entry_type) }}
        </label>
        <div class="equipment-help-text">
          {{ getEquipmentLinkingHelp(formData.entry_type) }}
        </div>
      </div>

      <!-- Equipment Selection -->
      <div v-if="isEquipmentType(formData.entry_type)" class="equipment-selector">
        <div class="equipment-type-tabs">
          <button 
            v-for="equipmentType in availableEquipmentTypes" 
            :key="equipmentType.value"
            @click="selectedEquipmentType = equipmentType.value"
            :class="['equipment-type-tab', { active: selectedEquipmentType === equipmentType.value }]"
            type="button"
          >
            <i :class="equipmentType.icon"></i>
            {{ equipmentType.label }}
          </button>
        </div>

        <div v-if="selectedEquipmentType" class="equipment-list">
          <div v-if="filteredEquipment.length === 0" class="no-equipment-message">
            <i class="fas fa-info-circle"></i>
            <p>No {{ selectedEquipmentType }} found for the selected bow setup.</p>
            <p class="help-text">Select a bow setup first, or add equipment to your bow setup.</p>
          </div>

          <div v-else class="equipment-grid">
            <div 
              v-for="equipment in filteredEquipment" 
              :key="`${selectedEquipmentType}-${equipment.id}`"
              :class="['equipment-card', { 
                selected: selectedEquipment?.id === equipment.id && selectedEquipment?.type === selectedEquipmentType 
              }]"
              @click="selectEquipment(equipment, selectedEquipmentType)"
            >
              <div class="equipment-icon">
                <i :class="getEquipmentIcon(selectedEquipmentType)"></i>
              </div>
              <div class="equipment-info">
                <h5 class="equipment-name">{{ equipment.name || equipment.manufacturer + ' ' + equipment.model }}</h5>
                <p class="equipment-details">{{ getEquipmentDetails(equipment, selectedEquipmentType) }}</p>
                <div class="equipment-specs" v-if="getEquipmentSpecs(equipment, selectedEquipmentType)">
                  {{ getEquipmentSpecs(equipment, selectedEquipmentType) }}
                </div>
              </div>
              <div class="equipment-status">
                <i v-if="selectedEquipment?.id === equipment.id && selectedEquipment?.type === selectedEquipmentType" 
                   class="fas fa-check-circle selected-icon"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Arrow Selection -->
      <div v-else-if="isArrowType(formData.entry_type)" class="arrow-selector">
        <div v-if="availableArrows.length === 0" class="no-arrows-message">
          <i class="fas fa-info-circle"></i>
          <p>No arrows found for the selected bow setup.</p>
          <p class="help-text">Select a bow setup first, or add arrows to your bow setup.</p>
        </div>

        <div v-else class="arrow-grid">
          <div 
            v-for="arrow in availableArrows" 
            :key="`arrow-${arrow.id}`"
            :class="['arrow-card', { 
              selected: selectedArrow?.id === arrow.id 
            }]"
            @click="selectArrow(arrow)"
          >
            <div class="arrow-icon">
              <i class="fas fa-bullseye"></i>
            </div>
            <div class="arrow-info">
              <h5 class="arrow-name">{{ arrow.manufacturer }} {{ arrow.model }}</h5>
              <div class="arrow-specs">
                <div class="arrow-spec">
                  <span class="spec-label">Length:</span>
                  <span class="spec-value">{{ arrow.length }}"</span>
                </div>
                <div class="arrow-spec">
                  <span class="spec-label">Spine:</span>
                  <span class="spec-value">{{ arrow.spine }}</span>
                </div>
                <div class="arrow-spec">
                  <span class="spec-label">Point:</span>
                  <span class="spec-value">{{ arrow.point_weight }}gr</span>
                </div>
                <div class="arrow-spec" v-if="arrow.calculated_spine">
                  <span class="spec-label">Calc. Spine:</span>
                  <span class="spec-value">{{ arrow.calculated_spine }}</span>
                </div>
              </div>
            </div>
            <div class="arrow-status">
              <i v-if="selectedArrow?.id === arrow.id" class="fas fa-check-circle selected-icon"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Selected Equipment/Arrow Summary -->
      <div v-if="selectedEquipment || selectedArrow" class="selection-summary">
        <div class="summary-header">
          <i class="fas fa-link"></i>
          <span>Linked to this entry:</span>
        </div>
        <div class="summary-content">
          <div v-if="selectedEquipment" class="selected-item">
            <i :class="getEquipmentIcon(selectedEquipment.type)"></i>
            <span class="item-name">{{ selectedEquipment.name || selectedEquipment.manufacturer + ' ' + selectedEquipment.model }}</span>
            <button @click="clearEquipmentSelection" class="clear-selection-btn" type="button">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div v-if="selectedArrow" class="selected-item">
            <i class="fas fa-bullseye"></i>
            <span class="item-name">{{ selectedArrow.manufacturer }} {{ selectedArrow.model }} ({{ selectedArrow.length }}", {{ selectedArrow.spine }})</span>
            <button @click="clearArrowSelection" class="clear-selection-btn" type="button">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Content Field -->
    <div class="form-group">
      <div class="form-label-section">
        <label class="form-label">Content *</label>
        <div class="editor-mode-toggle">
          <button 
            @click="useRichEditor = true"
            :class="['mode-btn', { active: useRichEditor }]"
            type="button"
          >
            <i class="fas fa-palette mr-1"></i>
            Rich
          </button>
          <button 
            @click="useRichEditor = false"
            :class="['mode-btn', { active: !useRichEditor }]"
            type="button"
          >
            <i class="fas fa-code mr-1"></i>
            Plain
          </button>
        </div>
      </div>
      
      <!-- Rich Text Editor -->
      <RichTextEditor
        v-if="useRichEditor"
        :model-value="formData.content"
        @update:model-value="(content) => $emit('update:form-data', 'content', content)"
        placeholder="Write your journal entry with rich formatting..."
        :max-length="limits?.content?.max || 5000"
        :equipment="availableEquipment"
        :bow-setups="bowSetups"
        :class="{ 
          'has-error': showValidation && validationResults?.content && !validationResults.content.isValid,
          'has-success': showValidation && validationResults?.content && validationResults.content.isValid && formData.content
        }"
      />
      
      <!-- Plain Text Editor (Fallback) -->
      <textarea
        v-else
        v-model="contentProxy"
        placeholder="Write your journal entry..."
        required
        rows="6"
        class="form-input content-textarea"
        :class="{ 
          'has-error': showValidation && validationResults?.content && !validationResults.content.isValid,
          'has-success': showValidation && validationResults?.content && validationResults.content.isValid && formData.content
        }"
      ></textarea>
      
      <div v-if="showValidation && validationResults?.content && !validationResults.content.isValid" class="field-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ validationResults.content.message }}
      </div>
      <div v-if="characterCounts?.content >= limits?.content?.min" class="field-success">
        <i class="fas fa-check-circle"></i>
        Good length for a detailed entry
      </div>
    </div>

    <!-- Image Upload Section -->
    <div class="form-group">
      <label class="form-label">Images ({{ attachedImages?.length || 0 }}/10)</label>
      <div class="image-upload-section">
        <!-- Current Images Display -->
        <div v-if="attachedImages?.length" class="attached-images-grid">
          <div v-for="(image, index) in attachedImages" :key="index" class="image-preview-item">
            <img :src="image.url" :alt="image.alt || 'Journal image'" class="preview-image" />
            <div class="image-overlay">
              <button 
                @click="removeImage(index)" 
                class="remove-image-btn"
                type="button"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Image Upload Component -->
        <div v-if="!attachedImages?.length || attachedImages.length < 10" class="upload-area">
          <ImageUpload
            :current-image-url="''"
            alt-text="Journal image"
            upload-path="journal"
            :max-size-bytes="5242880"
            @upload-success="handleImageUpload"
            @upload-error="handleImageError"
          />
        </div>
        
        <!-- Upload Guidelines -->
        <div class="upload-guidelines">
          <p class="guideline-text">
            <i class="fas fa-info-circle"></i>
            Add up to 10 photos to document your archery journey (max 5MB each)
          </p>
        </div>
      </div>
    </div>

    <!-- Tags Field -->
    <div class="form-group">
      <div class="form-label-section">
        <label class="form-label">Tags (comma-separated)</label>
        <div class="character-count" :class="{ 'over-limit': characterCounts?.tags > limits?.tags?.max }">
          {{ characterCounts?.tags || 0 }} / {{ limits?.tags?.max || 500 }}
        </div>
      </div>
      <input
        v-model="tagsProxy"
        type="text"
        placeholder="e.g. tuning, sight, arrows..."
        class="form-input"
        :class="{ 
          'has-error': showValidation && validationResults?.tags && !validationResults.tags.isValid,
          'has-success': formData.tagsString && (!showValidation || !validationResults?.tags || validationResults.tags.isValid)
        }"
      />
      <div v-if="showValidation && validationResults?.tags && !validationResults.tags.isValid" class="field-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ validationResults.tags.message }}
      </div>
      <div v-if="formData.tagsString" class="field-hint">
        <i class="fas fa-info-circle"></i>
        {{ getTagCount(formData.tagsString) }} tag{{ getTagCount(formData.tagsString) === 1 ? '' : 's' }}
      </div>
    </div>

    <!-- Private Entry Checkbox -->
    <div class="form-group">
      <md-checkbox 
        :checked="formData.is_private"
        @change="(e) => $emit('update:form-data', 'is_private', e.target.checked)"
      >
        Private entry (only visible to you)
      </md-checkbox>
    </div>

    <!-- Full Template Selector Modal -->
    <div v-if="showFullTemplateSelector" class="template-modal-overlay" @click="showFullTemplateSelector = false">
      <div class="template-modal" @click.stop>
        <EntryTemplateSelector
          :entry-type="formData.entry_type"
          @template-selected="onTemplateSelected"
          @cancel="showFullTemplateSelector = false"
          @new-template="onNewTemplate"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import EntryTemplateSelector from './EntryTemplateSelector.vue'
import RichTextEditor from './RichTextEditor.vue'

const props = defineProps({
  formData: Object,
  bowSetups: Array,
  entryTypes: Array,
  validationResults: Object,
  characterCounts: Object,
  limits: Object,
  showValidation: Boolean,
  attachedImages: Array,
  isNewEntry: Boolean
})

const emit = defineEmits([
  'update:form-data', 
  'image-uploaded', 
  'image-removed', 
  'image-error',
  'template-applied'
])

// Computed proxy properties for v-model
const titleProxy = computed({
  get: () => props.formData?.title || '',
  set: (value) => emit('update:form-data', 'title', value)
})

const contentProxy = computed({
  get: () => props.formData?.content || '',
  set: (value) => emit('update:form-data', 'content', value)
})

const tagsProxy = computed({
  get: () => props.formData?.tagsString || '',
  set: (value) => emit('update:form-data', 'tagsString', value)
})

// Equipment/Arrow linking state
const selectedEquipmentType = ref('')
const selectedEquipment = ref(null)
const selectedArrow = ref(null)
const setupEquipment = ref({
  bow: [],
  arrows: [],
  sight: [],
  rest: [],
  stabilizer: [],
  release: [],
  quiver: [],
  other: []
})

// Template state
const showTemplateSelector = ref(false)
const showFullTemplateSelector = ref(false)

// Quick templates for popular entry types
const quickTemplates = ref([
  {
    id: 'tuning_quick',
    name: 'Quick Tuning Note',
    entry_type: 'tuning_session',
    description: 'Fast note about tuning adjustments',
    title_template: 'Tuning Notes - {{date}}',
    content_template: 'Made adjustments to:\n\n• \n• \n\nResults:\n\n'
  },
  {
    id: 'practice_quick',
    name: 'Practice Session',
    entry_type: 'shooting_notes', 
    description: 'Record practice results',
    title_template: 'Practice - {{date}}',
    content_template: 'Distance: \nArrows: \nBest group: \nNotes:\n\n'
  },
  {
    id: 'equipment_quick',
    name: 'Equipment Change',
    entry_type: 'equipment_change',
    description: 'Log equipment modifications',
    title_template: 'Changed: {{equipment}}',
    content_template: 'What changed:\n\nWhy:\n\nFirst impression:\n\n'
  }
])

// Handle image upload success
const handleImageUpload = (imageUrl) => {
  const imageData = {
    url: imageUrl,
    uploadedAt: new Date().toISOString(),
    alt: 'Journal image'
  }
  emit('image-uploaded', imageData)
}

// Handle image upload error
const handleImageError = (error) => {
  emit('image-error', error)
}

// Remove attached image
const removeImage = (index) => {
  emit('image-removed', index)
}

// Helper function to count tags
const getTagCount = (tagsString) => {
  if (!tagsString?.trim()) return 0
  return tagsString.split(',').map(tag => tag.trim()).filter(Boolean).length
}

// Helper functions
const getSetupDetails = (setup) => {
  const details = []
  if (setup.draw_weight) details.push(`${setup.draw_weight}#`)
  if (setup.draw_length) details.push(`${setup.draw_length}"`)
  return details.join(' • ') || 'No details'
}

const getEntryTypeIcon = (typeValue) => {
  const icons = {
    general: 'fas fa-sticky-note',
    setup_change: 'fas fa-tools',
    equipment_change: 'fas fa-cog',
    arrow_change: 'fas fa-bullseye',
    tuning_session: 'fas fa-crosshairs',
    shooting_notes: 'fas fa-target',
    maintenance: 'fas fa-wrench',
    upgrade: 'fas fa-arrow-up'
  }
  return icons[typeValue] || 'fas fa-sticky-note'
}

const getEntryTypeDescription = (typeValue) => {
  const descriptions = {
    general: 'General thoughts, observations, or notes',
    setup_change: 'Changes to bow configuration or settings',
    equipment_change: 'Installing, removing, or swapping equipment',
    arrow_change: 'Switching arrows or spine adjustments',
    tuning_session: 'Detailed tuning process and results',
    shooting_notes: 'Performance observations and scores',
    maintenance: 'Cleaning, servicing, or repairs',
    upgrade: 'New equipment purchases and upgrades'
  }
  return descriptions[typeValue] || 'Document your archery journey'
}

// Rich text editor state
const useRichEditor = ref(true)

// Available equipment for mentions (computed from props)
const availableEquipment = computed(() => {
  const equipment = []
  
  // Add bow setups as equipment items
  if (props.bowSetups?.length) {
    equipment.push(...props.bowSetups.map(setup => ({
      id: `setup_${setup.id}`,
      name: setup.name,
      manufacturer: setup.bow_type,
      category: 'bow_setup',
      type: 'bow_setup'
    })))
  }
  
  // Add any other equipment from props if available
  // This would be populated from actual equipment data in a real implementation
  
  return equipment
})

// Equipment/Arrow linking computed properties
const showEquipmentLinking = computed(() => {
  return isEquipmentType(props.formData?.entry_type) || isArrowType(props.formData?.entry_type)
})

const availableEquipmentTypes = computed(() => {
  return [
    { value: 'bow', label: 'Bow', icon: 'fas fa-bow-arrow' },
    { value: 'sight', label: 'Sight', icon: 'fas fa-crosshairs' },
    { value: 'rest', label: 'Rest', icon: 'fas fa-hand-holding' },
    { value: 'stabilizer', label: 'Stabilizer', icon: 'fas fa-balance-scale' },
    { value: 'release', label: 'Release', icon: 'fas fa-hand-point-up' },
    { value: 'quiver', label: 'Quiver', icon: 'fas fa-quiver' },
    { value: 'other', label: 'Other', icon: 'fas fa-tools' }
  ]
})

const filteredEquipment = computed(() => {
  if (!selectedEquipmentType.value || !props.formData?.bow_setup_id) {
    return []
  }
  return setupEquipment.value[selectedEquipmentType.value] || []
})

const availableArrows = computed(() => {
  if (!props.formData?.bow_setup_id) {
    return []
  }
  return setupEquipment.value.arrows || []
})

// Equipment/Arrow linking methods
const isEquipmentType = (entryType) => {
  return ['equipment_change', 'upgrade'].includes(entryType)
}

const isArrowType = (entryType) => {
  return ['arrow_change'].includes(entryType)
}

const getEquipmentLinkingIcon = (entryType) => {
  const icons = {
    equipment_change: 'fas fa-tools',
    arrow_change: 'fas fa-bullseye',
    upgrade: 'fas fa-arrow-up'
  }
  return icons[entryType] || 'fas fa-link'
}

const getEquipmentLinkingLabel = (entryType) => {
  const labels = {
    equipment_change: 'Select Equipment',
    arrow_change: 'Select Arrow',
    upgrade: 'Select Equipment'
  }
  return labels[entryType] || 'Select Item'
}

const getEquipmentLinkingHelp = (entryType) => {
  const help = {
    equipment_change: 'Choose the specific equipment this entry is about',
    arrow_change: 'Choose the specific arrow this entry is about', 
    upgrade: 'Choose the equipment that was upgraded'
  }
  return help[entryType] || 'Choose an item to link to this entry'
}

const getEquipmentIcon = (equipmentType) => {
  const icons = {
    bow: 'fas fa-bow-arrow',
    sight: 'fas fa-crosshairs',
    rest: 'fas fa-hand-holding',
    stabilizer: 'fas fa-balance-scale',
    release: 'fas fa-hand-point-up',
    quiver: 'fas fa-quiver',
    other: 'fas fa-tools'
  }
  return icons[equipmentType] || 'fas fa-cog'
}

const getEquipmentDetails = (equipment, type) => {
  switch (type) {
    case 'bow':
      return `${equipment.draw_weight || 'Unknown'}# • ${equipment.draw_length || 'Unknown'}"` 
    case 'sight':
      return equipment.pin_count ? `${equipment.pin_count} pins` : 'Sight system'
    case 'rest':
      return equipment.rest_type || 'Arrow rest'
    case 'stabilizer':
      return equipment.length ? `${equipment.length}" stabilizer` : 'Stabilizer system'
    case 'release':
      return equipment.release_type || 'Release aid'
    case 'quiver':
      return equipment.arrow_capacity ? `${equipment.arrow_capacity} arrow capacity` : 'Arrow quiver'
    default:
      return equipment.description || 'Equipment item'
  }
}

const getEquipmentSpecs = (equipment, type) => {
  const specs = []
  if (equipment.manufacturer) specs.push(equipment.manufacturer)
  if (equipment.model) specs.push(equipment.model)
  if (equipment.specifications) {
    try {
      const parsed = JSON.parse(equipment.specifications)
      Object.entries(parsed).forEach(([key, value]) => {
        if (value && key !== 'manufacturer' && key !== 'model') {
          specs.push(`${key}: ${value}`)
        }
      })
    } catch (e) {
      // specifications is not JSON, use as-is
      if (equipment.specifications !== equipment.description) {
        specs.push(equipment.specifications)
      }
    }
  }
  return specs.length > 0 ? specs.join(' • ') : null
}

const selectEquipment = (equipment, type) => {
  selectedEquipment.value = { ...equipment, type }
  // Update form data with selected equipment
  emit('update:form-data', 'linked_equipment', {
    equipment_type: type,
    equipment_id: equipment.id,
    equipment_name: equipment.name || `${equipment.manufacturer} ${equipment.model}`,
    manufacturer: equipment.manufacturer,
    model: equipment.model,
    specifications: equipment.specifications || equipment.description
  })
}

const selectArrow = (arrow) => {
  selectedArrow.value = arrow
  // Update form data with selected arrow
  emit('update:form-data', 'linked_arrow', {
    arrow_id: arrow.id,
    manufacturer: arrow.manufacturer,
    model: arrow.model,
    spine: arrow.spine,
    length: arrow.length,
    point_weight: arrow.point_weight,
    calculated_spine: arrow.calculated_spine
  })
}

const clearEquipmentSelection = () => {
  selectedEquipment.value = null
  emit('update:form-data', 'linked_equipment', null)
}

const clearArrowSelection = () => {
  selectedArrow.value = null
  emit('update:form-data', 'linked_arrow', null)
}

// Template methods
const applyQuickTemplate = (template) => {
  const templateData = {
    title: template.title_template.replace('{{date}}', new Date().toLocaleDateString()).replace('{{equipment}}', ''),
    content: template.content_template,
    entry_type: template.entry_type
  }
  
  // Apply template data to form
  Object.keys(templateData).forEach(key => {
    if (templateData[key]) {
      emit('update:form-data', key, templateData[key])
    }
  })
  
  // Hide template selector
  showTemplateSelector.value = false
  
  // Notify parent that template was applied
  emit('template-applied', template)
}

const onTemplateSelected = (templateData) => {
  // Apply template data to form
  Object.keys(templateData).forEach(key => {
    if (templateData[key] !== undefined) {
      if (key === 'tags' && Array.isArray(templateData[key])) {
        // Convert tags array to string
        emit('update:form-data', 'tagsString', templateData[key].join(', '))
      } else {
        emit('update:form-data', key, templateData[key])
      }
    }
  })
  
  // Close template selector
  showFullTemplateSelector.value = false
  showTemplateSelector.value = false
  
  // Notify parent
  emit('template-applied', templateData)
}

const onNewTemplate = () => {
  // TODO: Implement new template creation
  showFullTemplateSelector.value = false
}

// Load equipment and arrows for the selected bow setup
const loadSetupEquipment = async () => {
  if (!props.formData?.bow_setup_id) {
    // Reset equipment data when no setup is selected
    setupEquipment.value = {
      bow: [],
      arrows: [],
      sight: [],
      rest: [],
      stabilizer: [],
      release: [],
      quiver: [],
      other: []
    }
    return
  }

  try {
    // This would typically make an API call to get equipment for the setup
    // For now, we'll simulate some equipment data based on the bow setup
    const selectedSetup = props.bowSetups?.find(setup => setup.id == props.formData.bow_setup_id)
    
    if (selectedSetup) {
      // Simulate equipment data - in a real implementation, this would come from API
      setupEquipment.value = {
        bow: [{
          id: selectedSetup.id,
          name: selectedSetup.name,
          manufacturer: selectedSetup.bow_type,
          model: selectedSetup.bow_model || 'Unknown Model',
          draw_weight: selectedSetup.draw_weight,
          draw_length: selectedSetup.draw_length,
          specifications: JSON.stringify({
            'Draw Weight': selectedSetup.draw_weight + '#',
            'Draw Length': selectedSetup.draw_length + '"',
            'Bow Type': selectedSetup.bow_type
          })
        }],
        arrows: [
          // This should be loaded from the setup_arrows table
          // For now, simulate some arrow data
        ],
        sight: [
          // These should be loaded from equipment tables
          // For now, simulate some equipment
        ],
        rest: [],
        stabilizer: [],
        release: [],
        quiver: [],
        other: []
      }
      
      // Default to first equipment type if available
      if (!selectedEquipmentType.value && availableEquipmentTypes.value.length > 0) {
        selectedEquipmentType.value = availableEquipmentTypes.value[0].value
      }
    }
  } catch (error) {
    console.error('Error loading setup equipment:', error)
  }
}

// Watch for bow setup changes
watch(
  () => props.formData?.bow_setup_id,
  () => {
    loadSetupEquipment()
    // Clear selections when setup changes
    selectedEquipment.value = null
    selectedArrow.value = null
  },
  { immediate: true }
)

// Watch for entry type changes
watch(
  () => props.formData?.entry_type,
  (newType) => {
    // Clear selections when entry type changes to non-equipment/arrow types
    if (!isEquipmentType(newType) && !isArrowType(newType)) {
      selectedEquipment.value = null
      selectedArrow.value = null
      emit('update:form-data', 'linked_equipment', null)
      emit('update:form-data', 'linked_arrow', null)
    }
    
    // Reset equipment type selection
    selectedEquipmentType.value = ''
  }
)

// Initialize template selector for new entries
onMounted(() => {
  // Show template selector for new entries if form is empty
  if (props.isNewEntry && !props.formData.title && !props.formData.content) {
    showTemplateSelector.value = true
  }
})
</script>

<style scoped>
.journal-form-fields {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  font-size: 0.875rem;
}

.form-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.form-input::placeholder {
  color: var(--md-sys-color-on-surface-variant);
  opacity: 0.7;
}

.form-input:focus {
  outline: none;
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-variant);
  box-shadow: 0 0 0 1px var(--md-sys-color-primary);
}

.form-input:hover {
  border-color: var(--md-sys-color-on-surface-variant);
}

.form-input.has-error {
  border-color: var(--md-sys-color-error);
  background: var(--md-sys-color-error-container);
}

.form-input.has-success {
  border-color: var(--md-sys-color-primary);
}

.form-select {
  width: 100%;
  padding: 1rem;
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.form-select option {
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  padding: 0.5rem;
}

.form-select option:disabled {
  color: var(--md-sys-color-on-surface-variant);
  opacity: 0.6;
}

.form-select:focus {
  outline: none;
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-variant);
  box-shadow: 0 0 0 1px var(--md-sys-color-primary);
}

.form-select:hover {
  border-color: var(--md-sys-color-on-surface-variant);
}

.form-select.has-error {
  border-color: var(--md-sys-color-error);
}

.form-select.has-success {
  border-color: var(--md-sys-color-primary);
}

.content-textarea {
  min-height: 120px;
  resize: vertical;
  color: var(--md-sys-color-on-surface) !important;
  background: var(--md-sys-color-surface) !important;
}

.content-textarea:focus {
  outline: none;
  border-color: var(--md-sys-color-primary) !important;
  background: var(--md-sys-color-surface-variant) !important;
  box-shadow: 0 0 0 1px var(--md-sys-color-primary);
  color: var(--md-sys-color-on-surface) !important;
}

/* Enhanced form styling for validation feedback */
.form-label-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.character-count {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 8px;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.character-count.over-limit {
  color: var(--md-sys-color-error);
  background: var(--md-sys-color-error-container);
}

.form-input.has-error {
  border-color: var(--md-sys-color-error) !important;
  --md-outlined-text-field-outline-color: var(--md-sys-color-error);
}

.form-input.has-success {
  --md-outlined-text-field-outline-color: var(--md-sys-color-primary);
}

.field-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-error);
  font-size: 0.875rem;
  font-weight: 500;
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--md-sys-color-error-container);
  border-radius: 8px;
}

.field-success {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-primary);
  font-size: 0.875rem;
  font-weight: 500;
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--md-sys-color-primary-container);
  border-radius: 8px;
}

.field-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 8px;
}

/* Image Upload Section Styles */
.image-upload-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.attached-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
}

.image-preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid var(--md-sys-color-outline-variant);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview-item:hover .image-overlay {
  opacity: 1;
}

.remove-image-btn {
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.remove-image-btn:hover {
  background: var(--md-sys-color-error-container);
  transform: scale(1.1);
}

.upload-area {
  border: 2px dashed var(--md-sys-color-outline-variant);
  border-radius: 8px;
  padding: 1rem;
  background: var(--md-sys-color-surface-variant);
  transition: all 0.2s ease;
}

.upload-area:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
}

.upload-guidelines {
  padding: 0.75rem 1rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 8px;
}

.guideline-text {
  margin: 0;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  line-height: 1.4;
}

@media (max-width: 768px) {
  /* Mobile responsiveness for image grid */
  .attached-images-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 0.75rem;
  }
  
  .remove-image-btn {
    width: 28px;
    height: 28px;
    font-size: 0.75rem;
  }
  
  .upload-area {
    padding: 0.75rem;
  }
}

/* Template Section Styles */
.template-section {
  background: var(--md-sys-color-primary-container);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid var(--md-sys-color-primary);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--md-sys-color-on-primary-container);
}

.skip-template-btn {
  background: var(--md-sys-color-surface);
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  transition: all 0.2s ease;
}

.skip-template-btn:hover {
  background: var(--md-sys-color-surface-container);
  border-color: var(--md-sys-color-primary);
}

.quick-templates {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.quick-template-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--md-sys-color-surface);
  border: 2px solid var(--md-sys-color-outline-variant);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-template-card:hover {
  border-color: var(--md-sys-color-primary);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.quick-template-card:focus {
  outline: 2px solid var(--md-sys-color-primary);
  outline-offset: 2px;
}

.template-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  font-size: 1.125rem;
  flex-shrink: 0;
}

.template-icon.icon-tuning_session {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
}

.template-icon.icon-equipment_change {
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
}

.template-icon.icon-shooting_notes {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.template-info p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.3;
}

.template-actions {
  text-align: center;
}

/* Template Modal Styles */
.template-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.template-modal {
  background: var(--md-sys-color-surface);
  border-radius: 16px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  padding: 1.5rem;
  width: 100%;
  max-width: 900px;
}

/* Rich Text Editor Mode Toggle */
.editor-mode-toggle {
  display: flex;
  gap: 0.25rem;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 16px;
  background: var(--md-sys-color-surface-container-lowest);
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-btn:focus {
  outline: 2px solid var(--md-sys-color-primary);
  outline-offset: 2px;
}

.mode-btn:hover {
  background: var(--md-sys-color-surface-container);
  border-color: var(--md-sys-color-primary);
}

.mode-btn.active {
  background: var(--md-sys-color-primary-container);
  border-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary-container);
}

.mode-btn i {
  font-size: 0.7rem;
}

@media (max-width: 768px) {
  .quick-templates {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .quick-template-card {
    padding: 0.75rem;
  }
  
  .template-icon {
    width: 36px;
    height: 36px;
    font-size: 1rem;
  }
  
  .template-info h4 {
    font-size: 0.85rem;
  }
  
  .template-info p {
    font-size: 0.75rem;
  }
  
  .template-modal {
    padding: 1rem;
  }
  
  .editor-mode-toggle {
    gap: 0.125rem;
  }
  
  .mode-btn {
    padding: 0.25rem 0.375rem;
    font-size: 0.7rem;
  }
  
  /* Equipment/Arrow Linking Mobile Styles */
  .equipment-linking-section {
    padding: 1rem;
  }
  
  .equipment-type-tabs {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .equipment-type-tab {
    padding: 0.75rem;
    font-size: 0.875rem;
  }
  
  .equipment-grid,
  .arrow-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .equipment-card,
  .arrow-card {
    padding: 1rem;
  }
  
  .selection-summary {
    padding: 1rem;
  }
}

/* Equipment/Arrow Linking Section Styles */
.equipment-linking-section {
  background: var(--md-sys-color-tertiary-container);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid var(--md-sys-color-tertiary);
}

.equipment-linking-header {
  margin-bottom: 1.5rem;
}

.equipment-linking-header .form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-tertiary-container);
  margin-bottom: 0.5rem;
}

.equipment-help-text {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-tertiary-container);
  opacity: 0.8;
  font-style: italic;
}

/* Equipment Type Tabs */
.equipment-type-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.equipment-type-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 500;
}

.equipment-type-tab:focus {
  outline: 2px solid var(--md-sys-color-primary);
  outline-offset: 2px;
}

.equipment-type-tab:hover {
  border-color: var(--md-sys-color-tertiary);
  background: var(--md-sys-color-tertiary-container);
}

.equipment-type-tab.active {
  border-color: var(--md-sys-color-tertiary);
  background: var(--md-sys-color-tertiary);
  color: var(--md-sys-color-on-tertiary);
}

/* Equipment and Arrow Grids */
.equipment-grid,
.arrow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.equipment-card,
.arrow-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 12px;
  background: var(--md-sys-color-surface);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.equipment-card:hover,
.arrow-card:hover {
  border-color: var(--md-sys-color-tertiary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.equipment-card.selected,
.arrow-card.selected {
  border-color: var(--md-sys-color-tertiary);
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
}

.equipment-icon,
.arrow-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.equipment-card.selected .equipment-icon,
.arrow-card.selected .arrow-icon {
  background: var(--md-sys-color-tertiary);
  color: var(--md-sys-color-on-tertiary);
}

.equipment-info,
.arrow-info {
  flex: 1;
  min-width: 0;
}

.equipment-name,
.arrow-name {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.equipment-card.selected .equipment-name,
.arrow-card.selected .arrow-name {
  color: var(--md-sys-color-on-tertiary-container);
}

.equipment-details {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
}

.equipment-card.selected .equipment-details {
  color: var(--md-sys-color-on-tertiary-container);
  opacity: 0.8;
}

.equipment-specs {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  font-style: italic;
}

.equipment-card.selected .equipment-specs {
  color: var(--md-sys-color-on-tertiary-container);
  opacity: 0.7;
}

.equipment-status,
.arrow-status {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.selected-icon {
  color: var(--md-sys-color-tertiary);
  font-size: 1.5rem;
}

.equipment-card.selected .selected-icon,
.arrow-card.selected .selected-icon {
  color: var(--md-sys-color-on-tertiary-container);
}

/* Arrow Specs */
.arrow-specs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.arrow-spec {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.spec-label {
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
}

.spec-value {
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.arrow-card.selected .spec-label {
  color: var(--md-sys-color-on-tertiary-container);
  opacity: 0.8;
}

.arrow-card.selected .spec-value {
  color: var(--md-sys-color-on-tertiary-container);
}

/* No Equipment/Arrows Messages */
.no-equipment-message,
.no-arrows-message {
  text-align: center;
  padding: 2rem;
  color: var(--md-sys-color-on-surface-variant);
}

.no-equipment-message i,
.no-arrows-message i {
  font-size: 2rem;
  margin-bottom: 1rem;
  display: block;
}

.no-equipment-message p,
.no-arrows-message p {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.help-text {
  font-size: 0.875rem;
  opacity: 0.8;
  font-style: italic;
}

/* Selection Summary */
.selection-summary {
  background: var(--md-sys-color-surface-container);
  border-radius: 8px;
  padding: 1.25rem;
  margin-top: 1.5rem;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.selected-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--md-sys-color-tertiary-container);
  border-radius: 8px;
  color: var(--md-sys-color-on-tertiary-container);
}

.item-name {
  flex: 1;
  font-weight: 500;
}

.clear-selection-btn {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.clear-selection-btn:hover {
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
  transform: scale(1.1);
}
</style>