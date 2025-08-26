<template>
  <div class="journal-categories">
    <div class="categories-header">
      <h3 class="categories-title">
        <md-icon class="categories-icon">category</md-icon>
        Custom Categories
      </h3>
      <p class="categories-subtitle">Organize your journal entries with custom categories</p>
    </div>

    <!-- Create New Category Section -->
    <div class="create-category-section">
      <div class="create-category-header">
        <h4 class="section-title">Create New Category</h4>
        <CustomButton 
          v-if="!showCreateForm"
          @click="showCreateForm = true"
          variant="primary"
          size="small"
          icon="add"
        >
          Add Category
        </CustomButton>
      </div>

      <!-- Create Category Form -->
      <div v-if="showCreateForm" class="create-category-form">
        <div class="form-row">
          <md-outlined-text-field
            v-model="newCategory.name"
            placeholder="Category name"
            required
            class="category-name-input"
            :error="validationErrors.name"
            :error-text="validationErrors.name"
          />
          
          <md-outlined-text-field
            v-model="newCategory.description"
            placeholder="Description (optional)"
            class="category-description-input"
          />
        </div>

        <div class="form-row">
          <div class="color-picker-section">
            <label class="form-label">Color</label>
            <div class="color-options">
              <button
                v-for="color in colorOptions"
                :key="color.value"
                @click="newCategory.color = color.value"
                :class="['color-option', { selected: newCategory.color === color.value }]"
                :style="{ backgroundColor: color.hex }"
                :title="color.name"
              >
                <md-icon v-if="newCategory.color === color.value" class="check-icon">check</md-icon>
              </button>
            </div>
          </div>

          <div class="icon-picker-section">
            <label class="form-label">Icon</label>
            <div class="icon-options">
              <button
                v-for="icon in iconOptions"
                :key="icon.value"
                @click="newCategory.icon = icon.value"
                :class="['icon-option', { selected: newCategory.icon === icon.value }]"
                :title="icon.name"
              >
                <md-icon>{{ icon.value }}</md-icon>
              </button>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <CustomButton @click="cancelCreate" variant="outlined" size="small">
            Cancel
          </CustomButton>
          <CustomButton 
            @click="createCategory" 
            variant="primary" 
            size="small"
            :disabled="!newCategory.name.trim() || isCreating"
            :class="{ 'is-loading': isCreating }"
          >
            <md-circular-progress v-if="isCreating" indeterminate class="btn-loading"></md-circular-progress>
            <span v-if="!isCreating">Create Category</span>
            <span v-else>Creating...</span>
          </CustomButton>
        </div>
      </div>
    </div>

    <!-- Categories List -->
    <div v-if="categories.length" class="categories-list-section">
      <div class="categories-list-header">
        <h4 class="section-title">Your Categories ({{ categories.length }})</h4>
        <div class="view-options">
          <button 
            @click="viewMode = 'grid'"
            :class="['view-btn', { active: viewMode === 'grid' }]"
            title="Grid view"
          >
            <md-icon>grid_view</md-icon>
          </button>
          <button 
            @click="viewMode = 'list'"
            :class="['view-btn', { active: viewMode === 'list' }]"
            title="List view"
          >
            <md-icon>view_list</md-icon>
          </button>
        </div>
      </div>

      <div :class="['categories-list', `view-${viewMode}`]">
        <div
          v-for="category in categories"
          :key="category.id"
          class="category-item"
          :style="{ '--category-color': getCategoryColor(category.color) }"
        >
          <div class="category-header">
            <div class="category-icon-badge">
              <md-icon>{{ category.icon }}</md-icon>
            </div>
            <div class="category-info">
              <h5 class="category-name">{{ category.name }}</h5>
              <p v-if="category.description" class="category-description">{{ category.description }}</p>
            </div>
            <div class="category-stats">
              <span class="entry-count">{{ category.entry_count || 0 }} entries</span>
            </div>
          </div>

          <div class="category-actions">
            <md-icon-button 
              @click="editCategory(category)"
              aria-label="Edit category"
              class="edit-btn"
            >
              <md-icon>edit</md-icon>
            </md-icon-button>
            <md-icon-button 
              @click="deleteCategory(category)"
              aria-label="Delete category"
              class="delete-btn"
              :disabled="category.entry_count > 0"
              :title="category.entry_count > 0 ? 'Cannot delete category with entries' : 'Delete category'"
            >
              <md-icon>delete</md-icon>
            </md-icon-button>
          </div>

          <!-- Recent Entries Preview -->
          <div v-if="category.recent_entries && category.recent_entries.length" class="recent-entries">
            <h6 class="recent-entries-title">Recent entries</h6>
            <div class="recent-entries-list">
              <div 
                v-for="entry in category.recent_entries.slice(0, 3)" 
                :key="entry.id"
                class="recent-entry-item"
                @click="$emit('view-entry', entry)"
              >
                <span class="entry-title">{{ truncateTitle(entry.title) }}</span>
                <span class="entry-date">{{ formatShortDate(entry.created_at) }}</span>
              </div>
              <div 
                v-if="category.recent_entries.length > 3"
                class="more-entries"
                @click="$emit('view-category-entries', category)"
              >
                +{{ category.recent_entries.length - 3 }} more entries
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="empty-categories">
      <div class="empty-icon">
        <md-icon>category</md-icon>
      </div>
      <h4 class="empty-title">No Custom Categories Yet</h4>
      <p class="empty-description">
        Create custom categories to better organize your journal entries beyond the default types.
      </p>
      <CustomButton 
        @click="showCreateForm = true"
        variant="primary"
        icon="add"
      >
        Create First Category
      </CustomButton>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="categories-loading">
      <md-circular-progress indeterminate></md-circular-progress>
      <span>Loading categories...</span>
    </div>

    <!-- Edit Category Modal -->
    <div v-if="editingCategory" class="edit-modal-overlay" @click="cancelEdit">
      <div class="edit-modal" @click.stop>
        <div class="edit-modal-header">
          <h4>Edit Category</h4>
          <md-icon-button @click="cancelEdit">
            <md-icon>close</md-icon>
          </md-icon-button>
        </div>
        
        <div class="edit-modal-content">
          <md-outlined-text-field
            v-model="editingCategory.name"
            placeholder="Category name"
            required
            class="edit-input"
            :error="validationErrors.editName"
            :error-text="validationErrors.editName"
          />
          
          <md-outlined-text-field
            v-model="editingCategory.description"
            placeholder="Description (optional)"
            class="edit-input"
          />

          <div class="color-picker-section">
            <label class="form-label">Color</label>
            <div class="color-options">
              <button
                v-for="color in colorOptions"
                :key="color.value"
                @click="editingCategory.color = color.value"
                :class="['color-option', { selected: editingCategory.color === color.value }]"
                :style="{ backgroundColor: color.hex }"
                :title="color.name"
              >
                <md-icon v-if="editingCategory.color === color.value" class="check-icon">check</md-icon>
              </button>
            </div>
          </div>

          <div class="icon-picker-section">
            <label class="form-label">Icon</label>
            <div class="icon-options">
              <button
                v-for="icon in iconOptions"
                :key="icon.value"
                @click="editingCategory.icon = icon.value"
                :class="['icon-option', { selected: editingCategory.icon === icon.value }]"
                :title="icon.name"
              >
                <md-icon>{{ icon.value }}</md-icon>
              </button>
            </div>
          </div>
        </div>
        
        <div class="edit-modal-actions">
          <CustomButton @click="cancelEdit" variant="outlined">
            Cancel
          </CustomButton>
          <CustomButton 
            @click="saveEditedCategory" 
            variant="primary"
            :disabled="!editingCategory.name.trim() || isSaving"
            :class="{ 'is-loading': isSaving }"
          >
            <md-circular-progress v-if="isSaving" indeterminate class="btn-loading"></md-circular-progress>
            <span v-if="!isSaving">Save Changes</span>
            <span v-else>Saving...</span>
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'
import { useGlobalNotifications } from '@/composables/useNotificationSystem'

const props = defineProps({
  userId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['view-entry', 'view-category-entries', 'category-created', 'category-updated', 'category-deleted'])

// Composables
const api = useApi()
const notifications = useGlobalNotifications()

// Reactive state
const categories = ref([])
const loading = ref(false)
const showCreateForm = ref(false)
const isCreating = ref(false)
const isSaving = ref(false)
const viewMode = ref('grid')
const editingCategory = ref(null)
const validationErrors = ref({})

const newCategory = ref({
  name: '',
  description: '',
  color: 'blue',
  icon: 'folder'
})

// Color options for categories
const colorOptions = [
  { value: 'blue', name: 'Blue', hex: '#1976d2' },
  { value: 'green', name: 'Green', hex: '#388e3c' },
  { value: 'orange', name: 'Orange', hex: '#f57c00' },
  { value: 'purple', name: 'Purple', hex: '#7b1fa2' },
  { value: 'red', name: 'Red', hex: '#d32f2f' },
  { value: 'teal', name: 'Teal', hex: '#00796b' },
  { value: 'indigo', name: 'Indigo', hex: '#303f9f' },
  { value: 'pink', name: 'Pink', hex: '#c2185b' }
]

// Icon options for categories
const iconOptions = [
  { value: 'folder', name: 'Folder' },
  { value: 'label', name: 'Label' },
  { value: 'bookmark', name: 'Bookmark' },
  { value: 'star', name: 'Star' },
  { value: 'flag', name: 'Flag' },
  { value: 'tag', name: 'Tag' },
  { value: 'category', name: 'Category' },
  { value: 'collections', name: 'Collections' },
  { value: 'local_offer', name: 'Offer' },
  { value: 'workspace_premium', name: 'Premium' },
  { value: 'grade', name: 'Grade' },
  { value: 'psychology', name: 'Psychology' }
]

// Methods
const loadCategories = async () => {
  loading.value = true
  try {
    const response = await api.get(`/journal/categories?user_id=${props.userId}`)
    if (response.success) {
      categories.value = response.data
    } else {
      notifications.showError('Failed to load categories')
    }
  } catch (error) {
    console.error('Error loading categories:', error)
    notifications.showError('Failed to load categories')
  } finally {
    loading.value = false
  }
}

const validateCategory = (category, field = 'name') => {
  const errors = {}
  
  if (!category.name.trim()) {
    errors[field] = 'Category name is required'
  } else if (category.name.length > 50) {
    errors[field] = 'Category name must be 50 characters or less'
  } else if (categories.value.some(cat => 
    cat.name.toLowerCase() === category.name.toLowerCase() && 
    (!category.id || cat.id !== category.id)
  )) {
    errors[field] = 'A category with this name already exists'
  }
  
  return errors
}

const createCategory = async () => {
  validationErrors.value = validateCategory(newCategory.value)
  if (Object.keys(validationErrors.value).length > 0) return

  isCreating.value = true
  try {
    const response = await api.post('/journal/categories', {
      name: newCategory.value.name.trim(),
      description: newCategory.value.description.trim(),
      color: newCategory.value.color,
      icon: newCategory.value.icon,
      user_id: props.userId
    })

    if (response.success) {
      categories.value.push(response.data)
      notifications.showSuccess('Category created successfully')
      emit('category-created', response.data)
      cancelCreate()
    } else {
      notifications.showError(response.error || 'Failed to create category')
    }
  } catch (error) {
    console.error('Error creating category:', error)
    notifications.showError('Failed to create category')
  } finally {
    isCreating.value = false
  }
}

const cancelCreate = () => {
  showCreateForm.value = false
  newCategory.value = {
    name: '',
    description: '',
    color: 'blue',
    icon: 'folder'
  }
  validationErrors.value = {}
}

const editCategory = (category) => {
  editingCategory.value = { ...category }
  validationErrors.value = {}
}

const cancelEdit = () => {
  editingCategory.value = null
  validationErrors.value = {}
}

const saveEditedCategory = async () => {
  validationErrors.value = validateCategory(editingCategory.value, 'editName')
  if (Object.keys(validationErrors.value).length > 0) return

  isSaving.value = true
  try {
    const response = await api.put(`/journal/categories/${editingCategory.value.id}`, {
      name: editingCategory.value.name.trim(),
      description: editingCategory.value.description?.trim() || '',
      color: editingCategory.value.color,
      icon: editingCategory.value.icon
    })

    if (response.success) {
      const index = categories.value.findIndex(cat => cat.id === editingCategory.value.id)
      if (index >= 0) {
        categories.value[index] = response.data
      }
      notifications.showSuccess('Category updated successfully')
      emit('category-updated', response.data)
      cancelEdit()
    } else {
      notifications.showError(response.error || 'Failed to update category')
    }
  } catch (error) {
    console.error('Error updating category:', error)
    notifications.showError('Failed to update category')
  } finally {
    isSaving.value = false
  }
}

const deleteCategory = async (category) => {
  if (category.entry_count > 0) {
    notifications.showError('Cannot delete category with entries. Please reassign entries first.')
    return
  }

  if (!confirm(`Delete category "${category.name}"? This action cannot be undone.`)) {
    return
  }

  try {
    const response = await api.delete(`/journal/categories/${category.id}`)
    if (response.success) {
      categories.value = categories.value.filter(cat => cat.id !== category.id)
      notifications.showSuccess('Category deleted successfully')
      emit('category-deleted', category)
    } else {
      notifications.showError(response.error || 'Failed to delete category')
    }
  } catch (error) {
    console.error('Error deleting category:', error)
    notifications.showError('Failed to delete category')
  }
}

const getCategoryColor = (colorValue) => {
  const color = colorOptions.find(c => c.value === colorValue)
  return color ? color.hex : '#1976d2'
}

const truncateTitle = (title) => {
  return title.length > 30 ? title.substring(0, 30) + '...' : title
}

const formatShortDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
  
  if (diffInDays === 0) return 'Today'
  if (diffInDays === 1) return 'Yesterday'
  if (diffInDays < 7) return `${diffInDays}d ago`
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// Lifecycle
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.journal-categories {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.categories-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.categories-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.categories-icon {
  color: var(--md-sys-color-primary);
  font-size: 1.75rem;
}

.categories-subtitle {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1rem;
}

/* Create Category Section */
.create-category-section {
  margin-bottom: 3rem;
  padding: 1.5rem;
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 12px;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.create-category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.create-category-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  gap: 1rem;
  align-items: start;
}

.form-row:first-child {
  grid-template-columns: 2fr 3fr;
}

.form-row:nth-child(2) {
  grid-template-columns: 1fr 1fr;
}

.form-label {
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.5rem;
  display: block;
  font-size: 0.875rem;
}

.color-options,
.icon-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.color-option {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.color-option.selected {
  border-color: var(--md-sys-color-outline);
  transform: scale(1.1);
}

.color-option:hover {
  transform: scale(1.05);
}

.check-icon {
  color: white;
  font-size: 1.2rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.icon-option {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 2px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-option.selected {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.icon-option:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-container);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-loading {
  width: 16px;
  height: 16px;
  margin-right: 0.5rem;
}

/* Categories List */
.categories-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.view-options {
  display: flex;
  gap: 0.25rem;
}

.view-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: var(--md-sys-color-surface-container);
  border-color: var(--md-sys-color-primary);
}

.view-btn.active {
  background: var(--md-sys-color-primary-container);
  border-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary-container);
}

.categories-list.view-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.categories-list.view-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.category-item {
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.2s ease;
  position: relative;
}

.category-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--category-color);
  border-radius: 12px 12px 0 0;
}

.category-item:hover {
  border-color: var(--category-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.category-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.category-icon-badge {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--category-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.category-info {
  flex: 1;
  min-width: 0;
}

.category-name {
  margin: 0 0 0.25rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-description {
  margin: 0;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.category-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.entry-count {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
}

.category-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.category-item:hover .category-actions {
  opacity: 1;
}

.edit-btn,
.delete-btn {
  transition: all 0.2s ease;
}

.delete-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.recent-entries {
  border-top: 1px solid var(--md-sys-color-outline-variant);
  padding-top: 1rem;
  margin-top: 1rem;
}

.recent-entries-title {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface-variant);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.recent-entries-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.recent-entry-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: var(--md-sys-color-surface-container);
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.recent-entry-item:hover {
  background: var(--md-sys-color-surface-container-high);
}

.entry-title {
  flex: 1;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface);
  font-weight: 500;
}

.entry-date {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  flex-shrink: 0;
}

.more-entries {
  text-align: center;
  padding: 0.5rem;
  font-size: 0.8rem;
  color: var(--md-sys-color-primary);
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.more-entries:hover {
  background: var(--md-sys-color-primary-container);
}

/* Empty State */
.empty-categories {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  margin-bottom: 1.5rem;
}

.empty-icon md-icon {
  font-size: 4rem;
  color: var(--md-sys-color-on-surface-variant);
  opacity: 0.5;
}

.empty-title {
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.empty-description {
  margin: 0 0 2rem 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1rem;
  line-height: 1.5;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

/* Loading State */
.categories-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 4rem 2rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Edit Modal */
.edit-modal-overlay {
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
}

.edit-modal {
  background: var(--md-sys-color-surface-container);
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.edit-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.edit-modal-header h4 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.edit-modal-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.edit-input {
  width: 100%;
}

.edit-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .journal-categories {
    padding: 1rem;
  }
  
  .categories-title {
    font-size: 1.5rem;
  }
  
  .categories-icon {
    font-size: 1.5rem;
  }
  
  .form-row {
    grid-template-columns: 1fr !important;
  }
  
  .categories-list.view-grid {
    grid-template-columns: 1fr;
  }
  
  .categories-list-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .view-options {
    justify-content: center;
  }
  
  .category-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.75rem;
  }
  
  .category-stats {
    align-items: center;
  }
  
  .category-actions {
    opacity: 1;
    justify-content: center;
  }
  
  .edit-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .empty-categories {
    padding: 2rem 1rem;
  }
  
  .color-options,
  .icon-options {
    justify-content: center;
  }
}
</style>