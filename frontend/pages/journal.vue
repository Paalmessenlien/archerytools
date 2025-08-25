<template>
  <div class="journal-page">
    <!-- Header -->
    <div class="journal-header">
      <div class="header-content">
        <div class="title-section">
          <h1>
            <md-icon class="page-icon">book</md-icon>
            Archery Journal
          </h1>
          <p class="subtitle">Document your archery journey with detailed notes and observations</p>
        </div>
        <div class="header-actions">
          <md-filled-button @click="showCreateDialog = true" class="create-btn">
            <md-icon slot="icon">add</md-icon>
            New Entry
          </md-filled-button>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section">
      <div class="search-controls">
        <md-outlined-text-field
          :value="searchQuery"
          placeholder="Search journal entries..."
          class="search-input"
          @input="(e) => { searchQuery = e.target.value; debouncedSearch() }"
        >
          <md-icon slot="leading-icon">search</md-icon>
        </md-outlined-text-field>
      </div>
      
      <div class="filter-controls">
        <md-outlined-select :value="selectedSetup" @change="(e) => { selectedSetup = e.target.value; loadEntries() }" class="setup-filter">
          <md-select-option value="">All Setups</md-select-option>
          <md-select-option v-for="setup in bowSetups" :key="setup.id" :value="setup.id.toString()">
            {{ setup.name }} ({{ setup.bow_type }})
          </md-select-option>
        </md-outlined-select>

        <md-outlined-select :value="selectedType" @change="(e) => { selectedType = e.target.value; loadEntries() }" class="type-filter">
          <md-select-option value="">All Types</md-select-option>
          <md-select-option v-for="type in entryTypes" :key="type.value" :value="type.value">
            {{ type.label }}
          </md-select-option>
        </md-outlined-select>

        <md-outlined-text-field
          :value="selectedTags"
          placeholder="Filter by tags (comma-separated)"
          class="tags-filter"
          @input="(e) => { selectedTags = e.target.value; debouncedSearch() }"
        >
          <md-icon slot="leading-icon">tag</md-icon>
        </md-outlined-text-field>
      </div>
    </div>

    <!-- Journal Entries List -->
    <div class="entries-container">
      <div v-if="loading" class="loading-state">
        <md-circular-progress indeterminate></md-circular-progress>
        <p>Loading journal entries...</p>
      </div>

      <div v-else-if="entries.length === 0" class="empty-state">
        <md-icon class="empty-icon">book</md-icon>
        <h3>No Journal Entries</h3>
        <p>Start documenting your archery journey by creating your first entry.</p>
        <md-filled-button @click="showCreateDialog = true" class="create-btn">
          <md-icon slot="icon">add</md-icon>
          Create First Entry
        </md-filled-button>
      </div>

      <div v-else class="entries-list">
        <JournalEntryCard
          v-for="entry in entries"
          :key="entry.id"
          :entry="entry"
          @edit="editEntry"
          @delete="deleteEntry"
          @view="viewEntry"
        />
      </div>

      <!-- Pagination -->
      <div v-if="pagination.pages > 1" class="pagination">
        <md-text-button 
          @click="loadPage(pagination.page - 1)"
          :disabled="pagination.page <= 1"
        >
          <md-icon slot="icon">chevron_left</md-icon>
          Previous
        </md-text-button>
        
        <span class="page-info">
          Page {{ pagination.page }} of {{ pagination.pages }}
        </span>
        
        <md-text-button 
          @click="loadPage(pagination.page + 1)"
          :disabled="pagination.page >= pagination.pages"
        >
          Next
          <md-icon slot="icon">chevron_right</md-icon>
        </md-text-button>
      </div>
    </div>

    <!-- Create/Edit Entry Dialog -->
    <JournalEntryDialog
      :show="showCreateDialog || showEditDialog"
      :entry="editingEntry"
      :bow-setups="bowSetups"
      :entry-types="entryTypes"
      @close="closeDialogs"
      @save="saveEntry"
    />

    <!-- View Entry Dialog -->
    <JournalEntryViewer
      :show="showViewDialog"
      :entry="viewingEntry"
      @close="showViewDialog = false"
      @edit="editFromViewer"
      @delete="deleteFromViewer"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useApi } from '@/composables/useApi'
import { useJournalStore } from '~/stores/journal'
import { debounce } from '~/utils/debounce'

// Page metadata
definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

// Composables
const { isAuthenticated, user } = useAuth()
const { $fetch } = useApi()
const journalStore = useJournalStore()

// Reactive data
const entries = ref([])
const bowSetups = ref([])
const entryTypes = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedSetup = ref('')
const selectedType = ref('')
const selectedTags = ref('')
const pagination = ref({
  page: 1,
  limit: 20,
  total: 0,
  pages: 0
})

// Dialog states
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const editingEntry = ref(null)
const viewingEntry = ref(null)

// Computed - isAuthenticated is already reactive from composable

// Methods
const loadEntries = async (page = 1) => {
  if (!isAuthenticated.value) return

  loading.value = true
  try {
    const params = {
      page,
      limit: pagination.value.limit
    }

    if (selectedSetup.value) params.bow_setup_id = selectedSetup.value
    if (selectedType.value) params.entry_type = selectedType.value
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedTags.value) params.tags = selectedTags.value

    const response = await journalStore.getEntries(params)
    entries.value = response.entries
    pagination.value = response.pagination
  } catch (error) {
    console.error('Failed to load journal entries:', error)
    $toast.error('Failed to load journal entries')
  } finally {
    loading.value = false
  }
}

const loadPage = (page) => {
  loadEntries(page)
}

const debouncedSearch = debounce(() => {
  loadEntries(1) // Reset to first page when searching
}, 300)

const loadBowSetups = async () => {
  try {
    const response = await $fetch('/api/bow-setups')
    bowSetups.value = response
  } catch (error) {
    console.error('Failed to load bow setups:', error)
    bowSetups.value = []
  }
}

const loadEntryTypes = async () => {
  try {
    const types = await journalStore.getEntryTypes()
    entryTypes.value = types
  } catch (error) {
    console.error('Failed to load entry types:', error)
  }
}

const editEntry = (entry) => {
  editingEntry.value = { ...entry }
  showEditDialog.value = true
}

const viewEntry = async (entry) => {
  try {
    const fullEntry = await journalStore.getEntry(entry.id)
    viewingEntry.value = fullEntry
    showViewDialog.value = true
  } catch (error) {
    console.error('Failed to load entry details:', error)
    $toast.error('Failed to load entry details')
  }
}

const editFromViewer = () => {
  editingEntry.value = { ...viewingEntry.value }
  showViewDialog.value = false
  showEditDialog.value = true
}

const deleteFromViewer = async () => {
  await deleteEntry(viewingEntry.value)
  showViewDialog.value = false
}

const deleteEntry = async (entry) => {
  if (!confirm(`Are you sure you want to delete "${entry.title}"?`)) return

  try {
    await journalStore.deleteEntry(entry.id)
    $toast.success('Journal entry deleted successfully')
    await loadEntries(pagination.value.page)
  } catch (error) {
    console.error('Failed to delete entry:', error)
    $toast.error('Failed to delete entry')
  }
}

const saveEntry = async (entryData) => {
  try {
    if (editingEntry.value?.id) {
      await journalStore.updateEntry(editingEntry.value.id, entryData)
      $toast.success('Journal entry updated successfully')
    } else {
      await journalStore.createEntry(entryData)
      $toast.success('Journal entry created successfully')
    }
    
    closeDialogs()
    await loadEntries(pagination.value.page)
  } catch (error) {
    console.error('Failed to save entry:', error)
    $toast.error('Failed to save entry')
  }
}

const closeDialogs = () => {
  showCreateDialog.value = false
  showEditDialog.value = false
  editingEntry.value = null
}

// Lifecycle
onMounted(async () => {
  if (isAuthenticated.value) {
    await Promise.all([
      loadBowSetups(),
      loadEntryTypes(),
      loadEntries()
    ])
  }
})

// Watchers
watch(isAuthenticated, async (newValue) => {
  if (newValue) {
    await Promise.all([
      loadBowSetups(),
      loadEntryTypes(),
      loadEntries()
    ])
  }
})
</script>

<style scoped>
.journal-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.journal-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.title-section h1 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: var(--md-sys-color-on-surface);
}

.page-icon {
  color: var(--md-sys-color-primary);
}

.subtitle {
  margin: 0.5rem 0 0 0;
  color: var(--md-sys-color-on-surface-variant);
  opacity: 0.8;
}

.filters-section {
  background: var(--md-sys-color-surface-variant);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.search-controls {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  max-width: 400px;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.setup-filter,
.type-filter,
.tags-filter {
  min-width: 200px;
  flex: 1;
}

.entries-container {
  min-height: 400px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  color: var(--md-sys-color-outline);
  margin-bottom: 1rem;
}

.entries-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem;
}

.page-info {
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .journal-page {
    padding: 1rem;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-controls {
    flex-direction: column;
  }

  .setup-filter,
  .type-filter,
  .tags-filter {
    min-width: unset;
    width: 100%;
  }

  .pagination {
    flex-wrap: wrap;
  }
}
</style>