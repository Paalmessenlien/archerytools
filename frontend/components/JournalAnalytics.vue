<template>
  <div class="journal-analytics">
    <div class="analytics-header">
      <h2 class="analytics-title">
        <md-icon class="analytics-icon">analytics</md-icon>
        Journal Insights
      </h2>
      <p class="analytics-subtitle">Discover patterns and trends in your archery journey</p>
    </div>

    <!-- Time Period Selector -->
    <div class="time-period-selector">
      <div class="period-buttons">
        <button 
          v-for="period in timePeriods" 
          :key="period.value"
          @click="selectedPeriod = period.value"
          :class="['period-btn', { active: selectedPeriod === period.value }]"
        >
          {{ period.label }}
        </button>
      </div>
      <div class="custom-range" v-if="selectedPeriod === 'custom'">
        <input 
          type="date" 
          v-model="customRange.start"
          class="range-input"
          :max="customRange.end"
        />
        <span class="range-separator">to</span>
        <input 
          type="date" 
          v-model="customRange.end"
          class="range-input"
          :min="customRange.start"
          :max="today"
        />
      </div>
    </div>

    <!-- Overview Stats -->
    <div class="overview-stats">
      <div class="stat-card">
        <div class="stat-icon">
          <md-icon>article</md-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ analytics.totalEntries }}</div>
          <div class="stat-label">Total Entries</div>
          <div class="stat-change" :class="analytics.entriesChange > 0 ? 'positive' : 'negative'">
            <md-icon>{{ analytics.entriesChange > 0 ? 'trending_up' : 'trending_down' }}</md-icon>
            {{ Math.abs(analytics.entriesChange) }}% vs last period
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <md-icon>photo_library</md-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ analytics.totalImages }}</div>
          <div class="stat-label">Images Uploaded</div>
          <div class="stat-detail">{{ analytics.avgImagesPerEntry.toFixed(1) }} avg per entry</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <md-icon>link</md-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ analytics.totalLinks }}</div>
          <div class="stat-label">Change Links</div>
          <div class="stat-detail">{{ analytics.linkedEntriesPercent }}% entries linked</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <md-icon>star</md-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ analytics.favoritesCount }}</div>
          <div class="stat-label">Favorites</div>
          <div class="stat-detail">{{ analytics.favoritesPercent }}% of entries</div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <!-- Entry Frequency Chart -->
      <div class="chart-card">
        <h3 class="chart-title">
          <md-icon>timeline</md-icon>
          Entry Frequency
        </h3>
        <div class="chart-container">
          <div class="frequency-chart">
            <div 
              v-for="(data, index) in analytics.frequencyData" 
              :key="index"
              class="frequency-bar"
              :style="{ height: (data.count / analytics.maxFrequency * 100) + '%' }"
              :title="`${data.period}: ${data.count} entries`"
            >
              <span class="bar-value">{{ data.count }}</span>
            </div>
          </div>
          <div class="frequency-labels">
            <span 
              v-for="(data, index) in analytics.frequencyData" 
              :key="index"
              class="frequency-label"
            >
              {{ data.period }}
            </span>
          </div>
        </div>
      </div>

      <!-- Entry Types Distribution -->
      <div class="chart-card">
        <h3 class="chart-title">
          <md-icon>donut_large</md-icon>
          Entry Types
        </h3>
        <div class="chart-container">
          <div class="donut-chart">
            <div class="donut-center">
              <div class="donut-total">{{ analytics.totalEntries }}</div>
              <div class="donut-label">Total</div>
            </div>
            <div class="donut-segments">
              <div 
                v-for="(type, index) in analytics.entryTypes" 
                :key="type.type"
                class="donut-segment"
                :style="{ 
                  '--segment-color': getTypeColor(type.type),
                  '--segment-percent': type.percentage + '%'
                }"
              ></div>
            </div>
          </div>
          <div class="type-legend">
            <div 
              v-for="type in analytics.entryTypes" 
              :key="type.type"
              class="legend-item"
            >
              <div 
                class="legend-color" 
                :style="{ backgroundColor: getTypeColor(type.type) }"
              ></div>
              <span class="legend-label">{{ formatEntryType(type.type) }}</span>
              <span class="legend-value">{{ type.count }} ({{ type.percentage }}%)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Writing Activity Heatmap -->
      <div class="chart-card full-width">
        <h3 class="chart-title">
          <md-icon>calendar_month</md-icon>
          Writing Activity
        </h3>
        <div class="heatmap-container">
          <div class="heatmap-grid">
            <div 
              v-for="(day, index) in analytics.activityData" 
              :key="index"
              class="heatmap-cell"
              :class="getActivityLevel(day.count)"
              :title="`${day.date}: ${day.count} entries`"
            ></div>
          </div>
          <div class="heatmap-legend">
            <span class="legend-label">Less</span>
            <div class="legend-scale">
              <div class="scale-cell level-0"></div>
              <div class="scale-cell level-1"></div>
              <div class="scale-cell level-2"></div>
              <div class="scale-cell level-3"></div>
              <div class="scale-cell level-4"></div>
            </div>
            <span class="legend-label">More</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Insights Section -->
    <div class="insights-section">
      <h3 class="insights-title">
        <md-icon>lightbulb</md-icon>
        Key Insights
      </h3>
      <div class="insights-grid">
        <div 
          v-for="insight in analytics.insights" 
          :key="insight.id"
          class="insight-card"
          :class="`insight-${insight.type}`"
        >
          <div class="insight-icon">
            <md-icon>{{ insight.icon }}</md-icon>
          </div>
          <div class="insight-content">
            <h4 class="insight-title">{{ insight.title }}</h4>
            <p class="insight-description">{{ insight.description }}</p>
            <div v-if="insight.action" class="insight-action">
              <CustomButton 
                @click="handleInsightAction(insight.action)"
                variant="outlined"
                size="small"
              >
                {{ insight.actionLabel }}
              </CustomButton>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Trends -->
    <div class="trends-section">
      <h3 class="trends-title">
        <md-icon>trending_up</md-icon>
        Recent Trends
      </h3>
      <div class="trends-list">
        <div 
          v-for="trend in analytics.trends" 
          :key="trend.id"
          class="trend-item"
        >
          <div class="trend-icon">
            <md-icon :class="trend.direction === 'up' ? 'trending-up' : 'trending-down'">
              trending_{{ trend.direction }}
            </md-icon>
          </div>
          <div class="trend-content">
            <div class="trend-metric">{{ trend.metric }}</div>
            <div class="trend-change">{{ trend.change }}{{ trend.unit }} {{ trend.period }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Analytics -->
    <div class="export-section">
      <CustomButton 
        @click="exportAnalytics"
        variant="outlined"
        icon="download"
        :disabled="isExporting"
      >
        {{ isExporting ? 'Exporting...' : 'Export Analytics' }}
      </CustomButton>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '@/composables/useApi'
import { useGlobalNotifications } from '@/composables/useNotificationSystem'

const props = defineProps({
  entries: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['create-entry', 'view-entry', 'filter-entries'])

// Composables
const api = useApi()
const notifications = useGlobalNotifications()

// Reactive state
const selectedPeriod = ref('30d')
const customRange = ref({
  start: '',
  end: ''
})
const isExporting = ref(false)

// Time periods
const timePeriods = [
  { value: '7d', label: '7 Days' },
  { value: '30d', label: '30 Days' },
  { value: '90d', label: '90 Days' },
  { value: '1y', label: '1 Year' },
  { value: 'all', label: 'All Time' },
  { value: 'custom', label: 'Custom' }
]

// Computed properties
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const filteredEntries = computed(() => {
  let entries = props.entries
  let startDate = new Date()
  let endDate = new Date()

  switch (selectedPeriod.value) {
    case '7d':
      startDate.setDate(startDate.getDate() - 7)
      break
    case '30d':
      startDate.setDate(startDate.getDate() - 30)
      break
    case '90d':
      startDate.setDate(startDate.getDate() - 90)
      break
    case '1y':
      startDate.setFullYear(startDate.getFullYear() - 1)
      break
    case 'custom':
      if (customRange.value.start && customRange.value.end) {
        startDate = new Date(customRange.value.start)
        endDate = new Date(customRange.value.end)
        endDate.setHours(23, 59, 59, 999)
      }
      break
    case 'all':
      return entries
  }

  if (selectedPeriod.value !== 'all') {
    entries = entries.filter(entry => {
      const entryDate = new Date(entry.created_at)
      return entryDate >= startDate && entryDate <= endDate
    })
  }

  return entries
})

const analytics = computed(() => {
  const entries = filteredEntries.value
  const totalEntries = entries.length
  
  // Basic stats
  const totalImages = entries.reduce((sum, entry) => sum + (entry.images?.length || 0), 0)
  const totalLinks = entries.reduce((sum, entry) => sum + (entry.linked_changes?.length || 0), 0)
  const favoritesCount = entries.filter(entry => entry.is_favorite).length
  
  // Percentages
  const linkedEntriesCount = entries.filter(entry => entry.linked_changes?.length > 0).length
  const linkedEntriesPercent = totalEntries > 0 ? Math.round((linkedEntriesCount / totalEntries) * 100) : 0
  const favoritesPercent = totalEntries > 0 ? Math.round((favoritesCount / totalEntries) * 100) : 0
  const avgImagesPerEntry = totalEntries > 0 ? totalImages / totalEntries : 0

  // Entry types distribution
  const typeCounts = {}
  entries.forEach(entry => {
    const type = entry.entry_type || 'general'
    typeCounts[type] = (typeCounts[type] || 0) + 1
  })

  const entryTypes = Object.keys(typeCounts).map(type => ({
    type,
    count: typeCounts[type],
    percentage: totalEntries > 0 ? Math.round((typeCounts[type] / totalEntries) * 100) : 0
  })).sort((a, b) => b.count - a.count)

  // Frequency data (last 30 days by default)
  const frequencyData = generateFrequencyData(entries)
  const maxFrequency = Math.max(...frequencyData.map(d => d.count), 1)

  // Activity heatmap data (last 90 days)
  const activityData = generateActivityData(entries)

  // Generate insights
  const insights = generateInsights(entries)

  // Generate trends
  const trends = generateTrends(entries)

  return {
    totalEntries,
    totalImages,
    totalLinks,
    favoritesCount,
    linkedEntriesPercent,
    favoritesPercent,
    avgImagesPerEntry,
    entriesChange: 15, // TODO: Calculate vs previous period
    entryTypes,
    frequencyData,
    maxFrequency,
    activityData,
    insights,
    trends
  }
})

// Methods
const generateFrequencyData = (entries) => {
  const data = []
  const now = new Date()
  const days = selectedPeriod.value === '7d' ? 7 : 30

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    
    const dayEntries = entries.filter(entry => {
      const entryDate = new Date(entry.created_at)
      return entryDate.toDateString() === date.toDateString()
    })

    data.push({
      period: date.getDate().toString(),
      count: dayEntries.length,
      date: date.toISOString().split('T')[0]
    })
  }

  return data
}

const generateActivityData = (entries) => {
  const data = []
  const now = new Date()

  for (let i = 89; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    
    const dayEntries = entries.filter(entry => {
      const entryDate = new Date(entry.created_at)
      return entryDate.toDateString() === date.toDateString()
    })

    data.push({
      date: date.toISOString().split('T')[0],
      count: dayEntries.length
    })
  }

  return data
}

const generateInsights = (entries) => {
  const insights = []

  // Most active day insight
  const dayActivity = {}
  entries.forEach(entry => {
    const day = new Date(entry.created_at).toLocaleDateString('en-US', { weekday: 'long' })
    dayActivity[day] = (dayActivity[day] || 0) + 1
  })
  const mostActiveDay = Object.keys(dayActivity).reduce((a, b) => dayActivity[a] > dayActivity[b] ? a : b, 'Monday')

  insights.push({
    id: 'active_day',
    type: 'info',
    icon: 'calendar_today',
    title: 'Most Active Day',
    description: `You write most journal entries on ${mostActiveDay}s (${dayActivity[mostActiveDay] || 0} entries).`,
  })

  // Favorites suggestion
  const favoritesPercent = entries.length > 0 ? (entries.filter(e => e.is_favorite).length / entries.length) * 100 : 0
  if (favoritesPercent < 10 && entries.length > 5) {
    insights.push({
      id: 'favorites_low',
      type: 'suggestion',
      icon: 'star_border',
      title: 'Mark Important Entries',
      description: 'Only ' + Math.round(favoritesPercent) + '% of your entries are favorited. Consider marking your most valuable insights.',
      action: 'view_entries',
      actionLabel: 'View Entries'
    })
  }

  // Images usage
  const entriesWithImages = entries.filter(entry => entry.images?.length > 0).length
  const imagesPercent = entries.length > 0 ? (entriesWithImages / entries.length) * 100 : 0
  if (imagesPercent < 30 && entries.length > 3) {
    insights.push({
      id: 'images_low',
      type: 'tip',
      icon: 'photo_camera',
      title: 'Visual Documentation',
      description: `Only ${Math.round(imagesPercent)}% of your entries include images. Photos can help track your progress over time.`,
    })
  }

  // Consistency insight
  const recentEntries = entries.filter(entry => {
    const entryDate = new Date(entry.created_at)
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return entryDate >= weekAgo
  }).length

  if (recentEntries === 0 && entries.length > 0) {
    insights.push({
      id: 'consistency',
      type: 'motivation',
      icon: 'edit',
      title: 'Stay Consistent',
      description: "You haven't written any entries this week. Regular journaling helps track your archery progress.",
      action: 'create_entry',
      actionLabel: 'Create Entry'
    })
  }

  return insights
}

const generateTrends = (entries) => {
  const trends = []

  // Weekly entry trend
  const thisWeek = entries.filter(entry => {
    const entryDate = new Date(entry.created_at)
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return entryDate >= weekAgo
  }).length

  const lastWeek = entries.filter(entry => {
    const entryDate = new Date(entry.created_at)
    const twoWeeksAgo = new Date()
    twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14)
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return entryDate >= twoWeeksAgo && entryDate < weekAgo
  }).length

  if (lastWeek > 0) {
    const change = thisWeek - lastWeek
    const changePercent = Math.round((change / lastWeek) * 100)
    
    trends.push({
      id: 'weekly_entries',
      metric: 'Journal Entries',
      change: Math.abs(changePercent),
      unit: '%',
      period: 'this week',
      direction: change >= 0 ? 'up' : 'down'
    })
  }

  return trends
}

const getTypeColor = (type) => {
  const colors = {
    general: '#6366f1',
    setup_change: '#10b981',
    equipment_change: '#f59e0b',
    arrow_change: '#ef4444',
    tuning_session: '#8b5cf6',
    shooting_notes: '#06b6d4',
    maintenance: '#84cc16',
    upgrade: '#f97316'
  }
  return colors[type] || '#6366f1'
}

const formatEntryType = (type) => {
  const labels = {
    general: 'General',
    setup_change: 'Setup Changes',
    equipment_change: 'Equipment Changes',
    arrow_change: 'Arrow Changes',
    tuning_session: 'Tuning Sessions',
    shooting_notes: 'Shooting Notes',
    maintenance: 'Maintenance',
    upgrade: 'Upgrades'
  }
  return labels[type] || 'General'
}

const getActivityLevel = (count) => {
  if (count === 0) return 'level-0'
  if (count === 1) return 'level-1'
  if (count === 2) return 'level-2'
  if (count === 3) return 'level-3'
  return 'level-4'
}

const handleInsightAction = (action) => {
  switch (action) {
    case 'create_entry':
      emit('create-entry')
      break
    case 'view_entries':
      emit('view-entry')
      break
    default:
      console.log('Unknown insight action:', action)
  }
}

const exportAnalytics = async () => {
  isExporting.value = true
  try {
    // TODO: Implement analytics export
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate export
    notifications.showSuccess('Analytics exported successfully')
  } catch (error) {
    notifications.showError('Failed to export analytics')
  } finally {
    isExporting.value = false
  }
}

// Initialize custom range
onMounted(() => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  
  customRange.value = {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0]
  }
})
</script>

<style scoped>
.journal-analytics {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.analytics-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.analytics-title {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.analytics-icon {
  color: var(--md-sys-color-primary);
  font-size: 2rem;
}

.analytics-subtitle {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1rem;
}

/* Time Period Selector */
.time-period-selector {
  margin-bottom: 2rem;
  text-align: center;
}

.period-buttons {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.period-btn {
  padding: 0.5rem 1rem;
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 20px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.period-btn:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-container);
}

.period-btn.active {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.custom-range {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.range-input {
  padding: 0.5rem;
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
}

.range-separator {
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
}

/* Overview Stats */
.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon md-icon {
  font-size: 1.5rem;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  font-weight: 500;
}

.stat-change.positive {
  color: var(--md-sys-color-primary);
}

.stat-change.negative {
  color: var(--md-sys-color-error);
}

.stat-detail {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Charts Section */
.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.chart-card {
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 16px;
  padding: 1.5rem;
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-title {
  margin: 0 0 1.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Frequency Chart */
.frequency-chart {
  display: flex;
  align-items: end;
  gap: 0.25rem;
  height: 200px;
  padding: 1rem 0;
  margin-bottom: 0.5rem;
}

.frequency-bar {
  flex: 1;
  background: var(--md-sys-color-primary-container);
  border-radius: 4px 4px 0 0;
  min-height: 4px;
  display: flex;
  align-items: end;
  justify-content: center;
  padding-bottom: 0.25rem;
  position: relative;
  transition: all 0.2s ease;
}

.frequency-bar:hover {
  background: var(--md-sys-color-primary);
}

.bar-value {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--md-sys-color-on-primary-container);
}

.frequency-labels {
  display: flex;
  gap: 0.25rem;
}

.frequency-label {
  flex: 1;
  text-align: center;
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Donut Chart */
.donut-chart {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 1.5rem;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.donut-total {
  font-size: 2rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
}

.donut-label {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
}

.type-legend {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface);
}

.legend-value {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
}

/* Activity Heatmap */
.heatmap-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(13, 1fr);
  gap: 2px;
  max-width: 600px;
}

.heatmap-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  background: var(--md-sys-color-surface-container-high);
}

.heatmap-cell.level-1 { background: rgba(var(--md-sys-color-primary-rgb), 0.3); }
.heatmap-cell.level-2 { background: rgba(var(--md-sys-color-primary-rgb), 0.5); }
.heatmap-cell.level-3 { background: rgba(var(--md-sys-color-primary-rgb), 0.7); }
.heatmap-cell.level-4 { background: var(--md-sys-color-primary); }

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-scale {
  display: flex;
  gap: 2px;
}

.scale-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.scale-cell.level-0 { background: var(--md-sys-color-surface-container-high); }
.scale-cell.level-1 { background: rgba(var(--md-sys-color-primary-rgb), 0.3); }
.scale-cell.level-2 { background: rgba(var(--md-sys-color-primary-rgb), 0.5); }
.scale-cell.level-3 { background: rgba(var(--md-sys-color-primary-rgb), 0.7); }
.scale-cell.level-4 { background: var(--md-sys-color-primary); }

/* Insights Section */
.insights-section {
  margin-bottom: 3rem;
}

.insights-title {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.insight-card {
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
}

.insight-card.insight-suggestion {
  border-color: var(--md-sys-color-secondary);
  background: var(--md-sys-color-secondary-container);
}

.insight-card.insight-tip {
  border-color: var(--md-sys-color-tertiary);
  background: var(--md-sys-color-tertiary-container);
}

.insight-card.insight-motivation {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
}

.insight-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.insight-content {
  flex: 1;
}

.insight-title {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.insight-description {
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.5;
}

.insight-action {
  margin-top: 1rem;
}

/* Trends Section */
.trends-section {
  margin-bottom: 3rem;
}

.trends-title {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.trends-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trend-item {
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.trend-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.trend-icon .trending-up {
  color: var(--md-sys-color-primary);
}

.trend-icon .trending-down {
  color: var(--md-sys-color-error);
}

.trend-content {
  flex: 1;
}

.trend-metric {
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.25rem;
}

.trend-change {
  font-size: 0.875rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Export Section */
.export-section {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .journal-analytics {
    padding: 1rem;
  }
  
  .analytics-title {
    font-size: 1.5rem;
  }
  
  .overview-stats {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .insights-grid {
    grid-template-columns: 1fr;
  }
  
  .custom-range {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .period-buttons {
    gap: 0.25rem;
  }
  
  .period-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.875rem;
  }
  
  .heatmap-grid {
    grid-template-columns: repeat(7, 1fr);
  }
}
</style>