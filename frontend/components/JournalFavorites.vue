<template>
  <div class="journal-favorites">
    <div class="favorites-header">
      <h2 class="favorites-title">
        <md-icon class="favorites-icon">star</md-icon>
        Favorite Entries
      </h2>
      <p class="favorites-subtitle">Your starred journal entries for quick access</p>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && (!favorites || favorites.length === 0)" class="empty-favorites">
      <div class="empty-icon">
        <md-icon>star_border</md-icon>
      </div>
      <h3 class="empty-title">No Favorites Yet</h3>
      <p class="empty-description">
        Star your most important journal entries to find them quickly here.
      </p>
      <div class="empty-actions">
        <CustomButton 
          @click="$emit('create-entry')" 
          variant="primary"
          icon="add"
        >
          Create First Entry
        </CustomButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="loading" class="favorites-loading">
      <md-circular-progress indeterminate></md-circular-progress>
      <span>Loading favorites...</span>
    </div>

    <!-- Favorites Grid -->
    <div v-else class="favorites-grid">
      <div class="favorites-meta">
        <span class="favorites-count">{{ favorites.length }} favorite{{ favorites.length === 1 ? '' : 's' }}</span>
        <div class="view-controls">
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

      <div :class="['favorites-container', `view-${viewMode}`]">
        <JournalEntryCard
          v-for="entry in favorites"
          :key="entry.id"
          :entry="entry"
          :view-mode="viewMode"
          @view="$emit('view-entry', $event)"
          @edit="$emit('edit-entry', $event)"
          @delete="$emit('delete-entry', $event)"
          @toggle-favorite="$emit('toggle-favorite', $event)"
          @view-change="$emit('view-change', $event)"
          @show-all-changes="$emit('show-all-changes', $event)"
        />
      </div>
    </div>

    <!-- Quick Stats -->
    <div v-if="favorites && favorites.length > 0" class="favorites-stats">
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ entryTypeStats.most_common?.count || 0 }}</div>
          <div class="stat-label">Most Common: {{ formatEntryType(entryTypeStats.most_common?.type) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ oldestFavorite }}</div>
          <div class="stat-label">Oldest Favorite</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ recentFavorites }}</div>
          <div class="stat-label">Recent Favorites</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  favorites: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'view-entry', 
  'edit-entry', 
  'delete-entry', 
  'toggle-favorite',
  'create-entry',
  'view-change',
  'show-all-changes'
])

// Reactive state
const viewMode = ref('grid')

// Computed properties
const entryTypeStats = computed(() => {
  if (!props.favorites || props.favorites.length === 0) return { most_common: null }
  
  const typeCounts = {}
  props.favorites.forEach(entry => {
    const type = entry.entry_type || 'general'
    typeCounts[type] = (typeCounts[type] || 0) + 1
  })
  
  const mostCommonType = Object.keys(typeCounts).reduce((a, b) => 
    typeCounts[a] > typeCounts[b] ? a : b
  )
  
  return {
    most_common: {
      type: mostCommonType,
      count: typeCounts[mostCommonType]
    }
  }
})

const oldestFavorite = computed(() => {
  if (!props.favorites || props.favorites.length === 0) return 'None'
  
  const oldest = props.favorites.reduce((oldest, entry) => {
    const entryDate = new Date(entry.created_at)
    const oldestDate = new Date(oldest.created_at)
    return entryDate < oldestDate ? entry : oldest
  })
  
  const date = new Date(oldest.created_at)
  const diffInDays = Math.floor((new Date() - date) / (1000 * 60 * 60 * 24))
  
  if (diffInDays === 0) return 'Today'
  if (diffInDays === 1) return 'Yesterday'
  if (diffInDays < 30) return `${diffInDays} days ago`
  if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`
  return `${Math.floor(diffInDays / 365)} years ago`
})

const recentFavorites = computed(() => {
  if (!props.favorites || props.favorites.length === 0) return 0
  
  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  
  return props.favorites.filter(entry => 
    new Date(entry.created_at) > oneWeekAgo
  ).length
})

// Methods
const formatEntryType = (type) => {
  const typeLabels = {
    general: 'General',
    setup_change: 'Setup Changes',
    equipment_change: 'Equipment Changes',
    arrow_change: 'Arrow Changes',
    tuning_session: 'Tuning Sessions',
    shooting_notes: 'Shooting Notes',
    maintenance: 'Maintenance',
    upgrade: 'Upgrades'
  }
  return typeLabels[type] || 'General'
}
</script>

<style scoped>
.journal-favorites {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.favorites-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.favorites-title {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.favorites-icon {
  color: var(--md-sys-color-primary);
  font-size: 2rem;
}

.favorites-subtitle {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1rem;
}

/* Empty State */
.empty-favorites {
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
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

/* Loading State */
.favorites-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 4rem 2rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Favorites Grid */
.favorites-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0 0.5rem;
}

.favorites-count {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
}

.view-controls {
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

.favorites-container.view-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.favorites-container.view-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Quick Stats */
.favorites-stats {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-item {
  text-align: center;
  padding: 1.5rem;
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: 12px;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--md-sys-color-primary);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .journal-favorites {
    padding: 1rem;
  }
  
  .favorites-title {
    font-size: 1.5rem;
  }
  
  .favorites-icon {
    font-size: 1.5rem;
  }
  
  .favorites-container.view-grid {
    grid-template-columns: 1fr;
  }
  
  .favorites-meta {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .view-controls {
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .stat-item {
    padding: 1rem;
  }
  
  .empty-favorites {
    padding: 2rem 1rem;
  }
}
</style>