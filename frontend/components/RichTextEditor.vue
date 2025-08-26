<template>
  <div class="rich-text-editor">
    <!-- Toolbar -->
    <div class="editor-toolbar" v-if="showToolbar">
      <!-- Formatting Controls -->
      <div class="toolbar-group">
        <button 
          v-for="format in formatButtons" 
          :key="format.command"
          @click="executeCommand(format.command, format.value)"
          :class="['toolbar-btn', { active: isFormatActive(format.command) }]"
          :title="format.title"
          type="button"
        >
          <i :class="format.icon"></i>
        </button>
      </div>

      <!-- Lists -->
      <div class="toolbar-group">
        <button 
          v-for="list in listButtons" 
          :key="list.command"
          @click="executeCommand(list.command)"
          :class="['toolbar-btn', { active: isFormatActive(list.command) }]"
          :title="list.title"
          type="button"
        >
          <i :class="list.icon"></i>
        </button>
      </div>

      <!-- Links and Special -->
      <div class="toolbar-group">
        <button 
          @click="insertLink"
          :class="['toolbar-btn', { active: isFormatActive('createLink') }]"
          title="Insert Link"
          type="button"
        >
          <i class="fas fa-link"></i>
        </button>
        <button 
          @click="removeFormat"
          class="toolbar-btn"
          title="Clear Formatting"
          type="button"
        >
          <i class="fas fa-remove-format"></i>
        </button>
      </div>

      <!-- Equipment Mentions -->
      <div class="toolbar-group">
        <button 
          @click="showEquipmentMentions = true"
          class="toolbar-btn"
          title="Mention Equipment"
          type="button"
        >
          <i class="fas fa-at"></i>
        </button>
      </div>
    </div>

    <!-- Editor Content -->
    <div class="editor-container">
      <div 
        ref="editorRef"
        class="editor-content"
        :class="{ 
          'editor-focused': isFocused,
          'has-error': hasError,
          'is-empty': isEmpty && showPlaceholder
        }"
        contenteditable="true"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="handleKeyDown"
        @paste="handlePaste"
        v-html="editorContent"
      ></div>
      
      <!-- Placeholder -->
      <div v-if="isEmpty && showPlaceholder && !isFocused" class="editor-placeholder">
        {{ placeholder }}
      </div>
    </div>

    <!-- Character Count -->
    <div v-if="showCharacterCount" class="editor-footer">
      <div class="character-count" :class="{ 'over-limit': isOverLimit }">
        {{ characterCount }}{{ maxLength ? ` / ${maxLength}` : '' }} characters
      </div>
    </div>

    <!-- Equipment Mention Modal -->
    <div v-if="showEquipmentMentions" class="mention-modal-overlay" @click="showEquipmentMentions = false">
      <div class="mention-modal" @click.stop>
        <div class="mention-header">
          <h3>Mention Equipment</h3>
          <button @click="showEquipmentMentions = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="mention-search">
          <div class="search-input-wrapper">
            <i class="fas fa-search search-icon"></i>
            <input
              v-model="equipmentSearchQuery"
              type="text"
              placeholder="Search equipment..."
              class="mention-search-input"
            />
          </div>
        </div>

        <div class="mention-categories">
          <div v-for="category in filteredEquipmentCategories" :key="category.type" class="mention-category">
            <h4 class="category-title">{{ category.title }}</h4>
            <div class="category-items">
              <div 
                v-for="item in category.items" 
                :key="item.id"
                class="mention-item"
                @click="insertEquipmentMention(item)"
              >
                <i :class="category.icon"></i>
                <span class="item-name">{{ item.name }}</span>
                <span v-if="item.manufacturer" class="item-detail">{{ item.manufacturer }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Start writing...'
  },
  maxLength: {
    type: Number,
    default: null
  },
  showToolbar: {
    type: Boolean,
    default: true
  },
  showCharacterCount: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  equipment: {
    type: Array,
    default: () => []
  },
  bowSetups: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur', 'input'])

// Refs
const editorRef = ref(null)
const isFocused = ref(false)
const showEquipmentMentions = ref(false)
const equipmentSearchQuery = ref('')

// Editor state
const editorContent = ref(props.modelValue || '')

// Toolbar configuration
const formatButtons = [
  { command: 'bold', icon: 'fas fa-bold', title: 'Bold' },
  { command: 'italic', icon: 'fas fa-italic', title: 'Italic' },
  { command: 'underline', icon: 'fas fa-underline', title: 'Underline' },
  { command: 'strikeThrough', icon: 'fas fa-strikethrough', title: 'Strikethrough' }
]

const listButtons = [
  { command: 'insertUnorderedList', icon: 'fas fa-list-ul', title: 'Bullet List' },
  { command: 'insertOrderedList', icon: 'fas fa-list-ol', title: 'Numbered List' }
]

// Computed properties
const isEmpty = computed(() => {
  const textContent = editorRef.value?.textContent || ''
  return textContent.trim().length === 0
})

const showPlaceholder = computed(() => {
  return props.placeholder && isEmpty.value
})

const characterCount = computed(() => {
  return editorRef.value?.textContent?.length || 0
})

const isOverLimit = computed(() => {
  return props.maxLength && characterCount.value > props.maxLength
})

const hasError = computed(() => {
  return isOverLimit.value
})

const filteredEquipmentCategories = computed(() => {
  const query = equipmentSearchQuery.value.toLowerCase()
  const categories = [
    {
      type: 'bow_setups',
      title: 'Bow Setups',
      icon: 'fas fa-crosshairs',
      items: props.bowSetups || []
    },
    {
      type: 'sights',
      title: 'Sights',
      icon: 'fas fa-eye',
      items: props.equipment?.filter(e => e.category === 'sight') || []
    },
    {
      type: 'rests',
      title: 'Arrow Rests', 
      icon: 'fas fa-bullseye',
      items: props.equipment?.filter(e => e.category === 'rest') || []
    },
    {
      type: 'stabilizers',
      title: 'Stabilizers',
      icon: 'fas fa-balance-scale',
      items: props.equipment?.filter(e => e.category === 'stabilizer') || []
    },
    {
      type: 'releases',
      title: 'Releases',
      icon: 'fas fa-hand-paper',
      items: props.equipment?.filter(e => e.category === 'release') || []
    }
  ]

  if (!query) return categories

  return categories.map(category => ({
    ...category,
    items: category.items.filter(item => 
      item.name?.toLowerCase().includes(query) ||
      item.manufacturer?.toLowerCase().includes(query)
    )
  })).filter(category => category.items.length > 0)
})

// Methods
const handleInput = (event) => {
  const content = event.target.innerHTML
  editorContent.value = content
  emit('update:modelValue', editorRef.value.textContent || '')
  emit('input', event)
}

const handleFocus = (event) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event) => {
  isFocused.value = false
  emit('blur', event)
}

const handleKeyDown = (event) => {
  // Handle keyboard shortcuts
  if (event.ctrlKey || event.metaKey) {
    switch (event.key) {
      case 'b':
        event.preventDefault()
        executeCommand('bold')
        break
      case 'i':
        event.preventDefault()
        executeCommand('italic')
        break
      case 'u':
        event.preventDefault()
        executeCommand('underline')
        break
      case 'k':
        event.preventDefault()
        insertLink()
        break
    }
  }

  // Prevent typing if over character limit
  if (props.maxLength && characterCount.value >= props.maxLength) {
    // Allow backspace, delete, and navigation keys
    const allowedKeys = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End']
    if (!allowedKeys.includes(event.key) && !event.ctrlKey && !event.metaKey) {
      event.preventDefault()
    }
  }
}

const handlePaste = (event) => {
  event.preventDefault()
  
  // Get plain text from clipboard
  const text = (event.clipboardData || window.clipboardData).getData('text/plain')
  
  // Insert as plain text
  document.execCommand('insertText', false, text)
}

const executeCommand = (command, value = null) => {
  if (props.disabled) return
  
  editorRef.value?.focus()
  document.execCommand(command, false, value)
  
  // Update content after command execution
  nextTick(() => {
    const content = editorRef.value.innerHTML
    editorContent.value = content
    emit('update:modelValue', editorRef.value.textContent || '')
  })
}

const isFormatActive = (command) => {
  if (!editorRef.value) return false
  
  try {
    return document.queryCommandState(command)
  } catch (e) {
    return false
  }
}

const insertLink = () => {
  const selection = window.getSelection()
  const selectedText = selection.toString()
  
  let url = prompt('Enter URL:', selectedText.startsWith('http') ? selectedText : 'https://')
  
  if (url) {
    // Ensure URL has protocol
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url
    }
    
    if (selectedText) {
      executeCommand('createLink', url)
    } else {
      const linkText = prompt('Link text:', url)
      if (linkText) {
        const linkHtml = `<a href="${url}" target="_blank" rel="noopener noreferrer">${linkText}</a>`
        executeCommand('insertHTML', linkHtml)
      }
    }
  }
}

const removeFormat = () => {
  executeCommand('removeFormat')
  executeCommand('unlink')
}

const insertEquipmentMention = (item) => {
  const mentionHtml = `<span class="equipment-mention" data-equipment-id="${item.id}" data-equipment-type="${item.type || 'equipment'}">@${item.name}</span>&nbsp;`
  executeCommand('insertHTML', mentionHtml)
  showEquipmentMentions.value = false
  equipmentSearchQuery.value = ''
}

const focusEditor = () => {
  editorRef.value?.focus()
}

const setContent = (content) => {
  if (editorRef.value) {
    editorRef.value.innerHTML = content
    editorContent.value = content
    emit('update:modelValue', editorRef.value.textContent || '')
  }
}

const getTextContent = () => {
  return editorRef.value?.textContent || ''
}

const getHtmlContent = () => {
  return editorRef.value?.innerHTML || ''
}

// Watch for external content changes
watch(() => props.modelValue, (newValue) => {
  if (newValue !== getTextContent()) {
    setContent(newValue || '')
  }
})

// Expose methods to parent
defineExpose({
  focus: focusEditor,
  setContent,
  getTextContent,
  getHtmlContent
})

// Lifecycle
onMounted(() => {
  if (props.modelValue) {
    setContent(props.modelValue)
  }
})
</script>

<style scoped>
.rich-text-editor {
  display: flex;
  flex-direction: column;
  background: var(--md-sys-color-surface);
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s ease;
}

.rich-text-editor.has-error {
  border-color: var(--md-sys-color-error) !important;
}

.rich-text-editor.has-error .editor-content {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container) !important;
}

.rich-text-editor:focus-within {
  border-color: var(--md-sys-color-primary);
}

.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--md-sys-color-surface-container-lowest);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.toolbar-group {
  display: flex;
  gap: 0.25rem;
}

.toolbar-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.toolbar-btn:hover {
  background: var(--md-sys-color-surface-container);
}

.toolbar-btn.active {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.toolbar-btn:active {
  transform: scale(0.95);
}

.editor-container {
  position: relative;
  flex: 1;
  min-height: 120px;
}

.editor-content {
  min-height: 120px;
  padding: 1rem;
  outline: none;
  line-height: 1.6;
  font-family: inherit;
  font-size: 1rem;
  color: var(--md-sys-color-on-surface) !important;
  background: var(--md-sys-color-surface);
  cursor: text;
}

.editor-content.has-error {
  color: var(--md-sys-color-error);
}

.editor-content.is-empty:not(:focus) {
  color: transparent;
}

.editor-content.is-empty:focus {
  color: var(--md-sys-color-on-surface);
}

.editor-placeholder {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  color: var(--md-sys-color-on-surface-variant);
  pointer-events: none;
  font-size: 1rem;
  line-height: 1.6;
}

.editor-footer {
  padding: 0.5rem 1rem;
  background: var(--md-sys-color-surface-container-lowest);
  border-top: 1px solid var(--md-sys-color-outline-variant);
  display: flex;
  justify-content: flex-end;
}

.character-count {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
}

.character-count.over-limit {
  color: var(--md-sys-color-error);
  font-weight: 600;
}

/* Equipment mentions styling */
.editor-content :deep(.equipment-mention) {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  padding: 0.125rem 0.375rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.editor-content :deep(.equipment-mention:hover) {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

/* Link styling */
.editor-content :deep(a) {
  color: var(--md-sys-color-primary);
  text-decoration: underline;
}

.editor-content :deep(a:hover) {
  text-decoration: none;
}

/* List styling */
.editor-content :deep(ul),
.editor-content :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.editor-content :deep(li) {
  margin-bottom: 0.25rem;
}

/* Equipment Mention Modal */
.mention-modal-overlay {
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

.mention-modal {
  background: var(--md-sys-color-surface);
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.mention-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.mention-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: var(--md-sys-color-surface-container);
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.close-btn:hover {
  background: var(--md-sys-color-surface-container-high);
}

.mention-search {
  padding: 1rem 1.5rem;
}

.search-input-wrapper {
  position: relative;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.875rem;
  z-index: 1;
}

.mention-search-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.mention-search-input:focus {
  outline: none;
  border-color: var(--md-sys-color-primary);
}

.mention-search-input:hover {
  border-color: var(--md-sys-color-on-surface-variant);
}

.mention-categories {
  flex: 1;
  overflow-y: auto;
  padding: 0 1.5rem 1.5rem 1.5rem;
}

.mention-category {
  margin-bottom: 1.5rem;
}

.category-title {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface-variant);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.category-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mention-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mention-item:hover {
  background: var(--md-sys-color-surface-container);
  transform: translateY(-1px);
}

.mention-item i {
  width: 20px;
  color: var(--md-sys-color-primary);
  text-align: center;
}

.item-name {
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  flex: 1;
}

.item-detail {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
}

@media (max-width: 768px) {
  .editor-toolbar {
    padding: 0.5rem;
    gap: 0.25rem;
  }
  
  .toolbar-group {
    gap: 0.125rem;
  }
  
  .toolbar-btn {
    width: 28px;
    height: 28px;
    font-size: 0.75rem;
  }
  
  .editor-content {
    padding: 0.75rem;
    min-height: 100px;
    font-size: 0.9rem;
  }
  
  .editor-placeholder {
    top: 0.75rem;
    left: 0.75rem;
    right: 0.75rem;
    font-size: 0.9rem;
  }
  
  .mention-modal {
    margin: 0.5rem;
  }
  
  .mention-header {
    padding: 1rem;
  }
  
  .mention-search,
  .mention-categories {
    padding: 0.75rem 1rem;
  }
}
</style>