<template>
  <!-- Mobile-First Detail Viewer with Bottom Sheet Pattern -->
  <div v-if="show" class="journal-detail-viewer" :class="{ 'full-page-mode': isFullPage }">
    <!-- Backdrop (only for modal mode) -->
    <div 
      v-if="!isFullPage"
      class="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
      :class="{ 'opacity-100': show, 'opacity-0': !show }"
      @click="closeViewer"
    ></div>

    <!-- Bottom Sheet Container (modal) or Full Page Container -->
    <div 
      :class="isFullPage ? 'full-page-container' : 'modal-container'"
    >
      <!-- Handle Bar for Mobile (only in modal mode) -->
      <div v-if="!isFullPage" class="flex justify-center p-2">
        <div class="w-12 h-1 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
      </div>

      <!-- Header -->
      <div class="flex items-start justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex-1 min-w-0">
          <!-- Entry Type Badge -->
          <div class="flex items-center gap-2 mb-2">
            <div class="entry-type-badge" :class="getEntryTypeBadgeClass(entry?.entry_type)">
              <md-icon class="text-sm">{{ getEntryTypeIcon(entry?.entry_type) }}</md-icon>
              <span class="text-xs font-medium">{{ getEntryTypeLabel(entry?.entry_type) }}</span>
            </div>
            <span v-if="entry?.is_favorite" class="text-yellow-500">
              <md-icon class="text-sm">star</md-icon>
            </span>
          </div>

          <!-- Title -->
          <h2 class="text-lg font-bold text-gray-900 dark:text-gray-100 truncate">
            {{ entry?.title || 'Untitled Entry' }}
          </h2>

          <!-- Meta Info -->
          <div class="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mt-1">
            <span class="flex items-center gap-1">
              <md-icon class="text-xs">schedule</md-icon>
              {{ formatDate(entry?.created_at) }}
            </span>
            <span v-if="entry?.setup_name" class="flex items-center gap-1">
              <md-icon class="text-xs">sports</md-icon>
              {{ entry.setup_name }}
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-2">
          <md-icon-button @click="toggleFavorite" :class="{ 'text-yellow-500': entry?.is_favorite }">
            <md-icon>{{ entry?.is_favorite ? 'star' : 'star_border' }}</md-icon>
          </md-icon-button>
          <md-icon-button @click="shareEntry">
            <md-icon>share</md-icon>
          </md-icon-button>
          <md-icon-button @click="editEntry">
            <md-icon>edit</md-icon>
          </md-icon-button>
          <md-icon-button @click="closeViewer">
            <md-icon>close</md-icon>
          </md-icon-button>
        </div>
      </div>

      <!-- Content Area with Scroll -->
      <div class="overflow-y-auto flex-1 p-4 space-y-6">
        
        <!-- Tuning Session Results (Enhanced for Tuning Entries) -->
        <div v-if="isTuningSession" class="tuning-session-results">
          
          <!-- Missing Session Data Notice -->
          <div v-if="!sessionData && !entry?.session_data" class="missing-session-data">
            <div class="missing-data-card p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800 mb-6">
              <div class="flex items-start gap-3">
                <md-icon class="text-amber-600 dark:text-amber-400 mt-1">warning</md-icon>
                <div class="flex-1">
                  <h4 class="font-semibold text-amber-900 dark:text-amber-100 mb-2">Missing Session Data</h4>
                  <p class="text-amber-800 dark:text-amber-200 text-sm mb-3">
                    This entry is marked as a tuning session, but detailed session data is not available. 
                    This may be an older entry created before the enhanced session tracking was implemented.
                  </p>
                  <div class="flex gap-2">
                    <md-outlined-button 
                      @click="editEntry" 
                      size="small"
                      class="text-amber-700 dark:text-amber-300"
                    >
                      <md-icon slot="icon">edit</md-icon>
                      Edit Entry
                    </md-outlined-button>
                    <md-outlined-button 
                      @click="startNewSession" 
                      size="small"
                      class="text-blue-600 dark:text-blue-400"
                    >
                      <md-icon slot="icon">add_circle</md-icon>
                      Start New Session
                    </md-outlined-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Enhanced Session Data Display (when available) -->
          <div v-else-if="sessionData || entry?.session_data" class="enhanced-session-data">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            <md-icon class="mr-2">tune</md-icon>
            {{ getTuningTypeLabel((sessionData || entry?.session_data)?.tuning_type) }} Session Details
          </h3>

          <!-- Session Overview Card -->
          <div class="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Arrow Information -->
              <div v-if="(sessionData || entry?.session_data)?.arrow_info" class="space-y-2">
                <h4 class="font-semibold text-blue-900 dark:text-blue-100 text-sm">Arrow Details</h4>
                <div class="text-sm space-y-1">
                  <div><strong>Arrow:</strong> {{ (sessionData || entry?.session_data)?.arrow_info?.manufacturer }} {{ (sessionData || entry?.session_data)?.arrow_info?.model_name }}</div>
                  <div><strong>Material:</strong> {{ (sessionData || entry?.session_data)?.arrow_info?.material || 'Not specified' }}</div>
                  <div v-if="(sessionData || entry?.session_data)?.arrow_length || (sessionData || entry?.session_data)?.session_details?.arrow_length">
                    <strong>Length:</strong> {{ (sessionData || entry?.session_data)?.arrow_length || (sessionData || entry?.session_data)?.session_details?.arrow_length }}"
                  </div>
                  <div v-if="(sessionData || entry?.session_data)?.point_weight || (sessionData || entry?.session_data)?.session_details?.point_weight">
                    <strong>Point Weight:</strong> {{ (sessionData || entry?.session_data)?.point_weight || (sessionData || entry?.session_data)?.session_details?.point_weight }} grains
                  </div>
                </div>
              </div>
              
              <!-- Session Information -->
              <div class="space-y-2">
                <h4 class="font-semibold text-blue-900 dark:text-blue-100 text-sm">Session Info</h4>
                <div class="text-sm space-y-1">
                  <div><strong>Bow Setup:</strong> {{ entry?.setup_name || (sessionData || entry?.session_data)?.bow_info?.name || entry?.bow_setup_name || 'Unknown' }}</div>
                  <div><strong>Bow Type:</strong> {{ entry?.bow_type || (sessionData || entry?.session_data)?.bow_info?.bow_type || 'Not specified' }}</div>
                  <div v-if="(sessionData || entry?.session_data)?.duration || (sessionData || entry?.session_data)?.session_details?.session_duration">
                    <strong>Duration:</strong> {{ (sessionData || entry?.session_data)?.duration || (sessionData || entry?.session_data)?.session_details?.session_duration }}
                  </div>
                  <div><strong>Date:</strong> {{ formatDate(entry.created_at) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Session Quality Score -->
          <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Session Quality Score</span>
              <span class="text-lg font-bold" :class="getQualityTextColor((sessionData || entry?.session_data)?.session_quality)">
                {{ Math.round((sessionData || entry?.session_data)?.session_quality || entry?.session_quality_score || 0) }}%
              </span>
            </div>
            <div class="w-full h-3 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
              <div 
                class="h-full rounded-full transition-all duration-500"
                :class="getQualityBarColor((sessionData || entry?.session_data)?.session_quality || entry?.session_quality_score)"
                :style="{ width: `${(sessionData || entry?.session_data)?.session_quality || entry?.session_quality_score || 0}%` }"
              ></div>
            </div>
            <div class="mt-2 text-xs text-gray-600 dark:text-gray-400">
              Based on {{ (sessionData || entry?.session_data)?.test_results?.length || 0 }} test result{{ ((sessionData || entry?.session_data)?.test_results?.length || 0) === 1 ? '' : 's' }} and confidence scores
            </div>
          </div>

          <!-- Bareshaft Specific Results -->
          <div v-if="(sessionData || entry?.session_data)?.tuning_type === 'bareshaft'" class="bareshaft-results">
            <!-- Summary Stats -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div class="stat-card">
                <div class="stat-label">Tests Completed</div>
                <div class="stat-value">{{ (sessionData || entry?.session_data)?.test_results?.length || 0 }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Most Common Pattern</div>
                <div class="stat-value text-sm">{{ (sessionData || entry?.session_data)?.most_common_pattern || 'Unknown' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Average Confidence</div>
                <div class="stat-value">{{ getAverageConfidence((sessionData || entry?.session_data)?.test_results) }}%</div>
              </div>
            </div>

            <!-- Test Results Timeline (Visual Recreation) -->
            <div class="mb-6 p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
              <h4 class="font-medium text-orange-900 dark:text-orange-100 mb-4 flex items-center">
                <md-icon class="mr-2 text-sm">history</md-icon>
                Test Results Timeline
              </h4>
              <div class="space-y-3">
                <div 
                  v-for="(test, index) in (sessionData || entry?.session_data)?.test_results" 
                  :key="index"
                  class="test-result-card"
                >
                  <div class="flex items-start justify-between">
                    <div class="flex items-start gap-3">
                      <!-- Test Number Badge -->
                      <div class="flex-shrink-0 w-8 h-8 bg-orange-100 dark:bg-orange-800 rounded-full flex items-center justify-center text-sm font-bold text-orange-800 dark:text-orange-200">
                        {{ index + 1 }}
                      </div>
                      
                      <!-- Test Details -->
                      <div class="flex-1">
                        <div class="flex items-center gap-2 mb-1">
                          <span class="font-medium text-gray-900 dark:text-gray-100">{{ test.pattern_name || test.pattern }}</span>
                          <!-- Quality indicator dot -->
                          <div class="w-2 h-2 rounded-full" :class="getTestQualityColor(test.confidence_score)"></div>
                        </div>
                        
                        <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                          <div>Confidence: {{ Math.round(test.confidence_score) }}%</div>
                          <div v-if="test.notes" class="italic">{{ test.notes }}</div>
                          <div class="text-xs">{{ formatTestTime(test.timestamp) }}</div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Confidence Score Visual -->
                    <div class="flex-shrink-0 text-right">
                      <div class="text-sm font-medium" :class="getConfidenceTextColor(test.confidence_score)">
                        {{ Math.round(test.confidence_score) }}%
                      </div>
                      <div class="w-12 h-1 bg-gray-200 dark:bg-gray-600 rounded-full mt-1">
                        <div 
                          class="h-full rounded-full transition-all"
                          :class="getConfidenceBarColor(test.confidence_score)"
                          :style="{ width: `${test.confidence_score}%` }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Paper Tuning Specific Results -->
          <div v-else-if="(sessionData || entry?.session_data)?.tuning_type === 'paper'" class="paper-results">
            <!-- Summary Stats -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div class="stat-card">
                <div class="stat-label">Total Tests</div>
                <div class="stat-value">{{ (sessionData || entry?.session_data)?.test_results?.length || 0 }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Most Common Tear</div>
                <div class="stat-value text-sm">{{ (sessionData || entry?.session_data)?.most_common_tear || 'Unknown' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Average Tear Size</div>
                <div class="stat-value">{{ formatTearSize((sessionData || entry?.session_data)?.average_tear_size) }}</div>
              </div>
            </div>

            <!-- Test Results Timeline (Visual Recreation) -->
            <div class="mb-6 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
              <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-4 flex items-center">
                <md-icon class="mr-2 text-sm">article</md-icon>
                Paper Tuning Test Results
              </h4>
              <div class="space-y-3">
                <div 
                  v-for="(test, index) in (sessionData || entry?.session_data)?.test_results" 
                  :key="index"
                  class="test-result-card"
                >
                  <div class="flex items-start justify-between">
                    <div class="flex items-start gap-3">
                      <!-- Test Number Badge -->
                      <div class="flex-shrink-0 w-8 h-8 bg-purple-100 dark:bg-purple-800 rounded-full flex items-center justify-center text-sm font-bold text-purple-800 dark:text-purple-200">
                        {{ index + 1 }}
                      </div>
                      
                      <!-- Test Details -->
                      <div class="flex-1">
                        <div class="flex items-center gap-2 mb-1">
                          <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatTearDirection(test.tear_direction) }}</span>
                          <!-- Quality indicator dot -->
                          <div class="w-2 h-2 rounded-full" :class="getTearQualityColor(test.tear_magnitude)"></div>
                        </div>
                        
                        <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                          <div>Tear Size: {{ formatTearSize(test.tear_magnitude) }}</div>
                          <div>Confidence: {{ Math.round(test.confidence_score || 90) }}%</div>
                          <div v-if="test.notes" class="italic">{{ test.notes }}</div>
                          <div class="text-xs">{{ formatTestTime(test.timestamp) }}</div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Tear Size Visual -->
                    <div class="flex-shrink-0 text-right">
                      <div class="text-sm font-mono font-medium" :class="getTearSizeTextColor(test.tear_magnitude)">
                        {{ formatTearSize(test.tear_magnitude) }}
                      </div>
                      <div class="w-12 h-1 bg-gray-200 dark:bg-gray-600 rounded-full mt-1">
                        <div 
                          class="h-full rounded-full transition-all"
                          :class="getTearSizeBarColor(test.tear_magnitude)"
                          :style="{ width: `${Math.min((test.tear_magnitude / 2) * 100, 100)}%` }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Walkback Specific Results -->
          <div v-else-if="(sessionData || entry?.session_data)?.tuning_type === 'walkback' || entry?.session_type === 'walkback_tuning'" class="walkback-results">
            <!-- Summary Stats -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div class="stat-card">
                <div class="stat-label">Distances Tested</div>
                <div class="stat-value">{{ (sessionData || entry?.session_data)?.test_results?.length || 0 }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Drift Rate</div>
                <div class="stat-value text-sm">{{ (sessionData || entry?.session_data)?.drift_analysis?.drift_rate_cm_per_m || '0.0' }} cm/m</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Assessment</div>
                <div class="stat-value text-sm">{{ (sessionData || entry?.session_data)?.drift_analysis?.quality_assessment || 'Unknown' }}</div>
              </div>
            </div>

            <!-- Drift Analysis Visualization -->
            <div class="mb-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <h4 class="font-medium text-green-900 dark:text-green-100 mb-4 flex items-center">
                <md-icon class="mr-2 text-sm">trending_flat</md-icon>
                Drift Analysis Results
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div class="bg-white dark:bg-gray-800 p-3 rounded-lg">
                  <div class="text-sm text-gray-600 dark:text-gray-400">Drift Direction</div>
                  <div class="font-bold text-lg">{{ (sessionData || entry?.session_data)?.drift_analysis?.drift_direction || 'None' }}</div>
                </div>
                <div class="bg-white dark:bg-gray-800 p-3 rounded-lg">
                  <div class="text-sm text-gray-600 dark:text-gray-400">Drift Rate</div>
                  <div class="font-bold text-lg font-mono">{{ (sessionData || entry?.session_data)?.drift_analysis?.drift_rate_cm_per_m || '0.0' }} cm/m</div>
                </div>
                <div class="bg-white dark:bg-gray-800 p-3 rounded-lg">
                  <div class="text-sm text-gray-600 dark:text-gray-400">Slope</div>
                  <div class="font-bold text-lg font-mono">{{ formatSlope((sessionData || entry?.session_data)?.drift_analysis?.slope) }}</div>
                </div>
              </div>
              
              <div class="text-sm">
                <strong>Assessment:</strong> {{ (sessionData || entry?.session_data)?.drift_analysis?.quality_assessment || 'No assessment available' }}
              </div>
            </div>

            <!-- Distance Test Results (Visual Recreation) -->
            <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-4 flex items-center">
                <md-icon class="mr-2 text-sm">straighten</md-icon>
                Distance Test Results
              </h4>
              <div class="space-y-3">
                <div 
                  v-for="(test, index) in getSortedDistanceTests((sessionData || entry?.session_data)?.test_results)" 
                  :key="index"
                  class="test-result-card"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <!-- Distance Badge -->
                      <div class="flex-shrink-0 w-12 h-8 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center text-sm font-bold text-blue-800 dark:text-blue-200">
                        {{ test.distance_m }}m
                      </div>
                      
                      <!-- Test Details -->
                      <div class="flex-1">
                        <div class="flex items-center gap-2 mb-1">
                          <span class="font-medium text-gray-900 dark:text-gray-100">
                            {{ formatOffset(test.horizontal_offset_cm) }} offset
                          </span>
                          <!-- Quality indicator dot -->
                          <div class="w-2 h-2 rounded-full" :class="getTestQualityColor(test.confidence_score)"></div>
                        </div>
                        
                        <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                          <div>Confidence: {{ Math.round(test.confidence_score) }}%</div>
                          <div v-if="test.notes" class="italic">{{ test.notes }}</div>
                          <div class="text-xs">{{ formatTestTime(test.timestamp) }}</div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Offset Visual Indicator -->
                    <div class="flex-shrink-0 text-right">
                      <div class="text-sm font-mono font-medium" :class="getOffsetTextColor(test.horizontal_offset_cm)">
                        {{ formatOffset(test.horizontal_offset_cm) }}
                      </div>
                      <!-- Visual bar showing offset magnitude -->
                      <div class="w-16 h-1 bg-gray-200 dark:bg-gray-600 rounded-full mt-1 relative">
                        <div 
                          class="absolute h-full rounded-full transition-all"
                          :class="getOffsetBarColor(test.horizontal_offset_cm)"
                          :style="getOffsetBarStyle(test.horizontal_offset_cm)"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recommendations Section -->
          <div v-if="(sessionData || entry?.session_data)?.final_recommendations?.length" class="recommendations-section">
            <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">
              <md-icon class="mr-2 text-sm">build</md-icon>
              Tuning Recommendations
            </h4>
            <div class="space-y-3">
              <div 
                v-for="(rec, index) in (sessionData || entry?.session_data)?.final_recommendations" 
                :key="index"
                class="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg"
              >
                <div class="font-medium text-amber-900 dark:text-amber-100 text-sm">{{ rec.title }}</div>
                <div class="text-amber-800 dark:text-amber-200 text-xs mt-1">{{ rec.instruction }}</div>
              </div>
            </div>
          </div>
          </div> <!-- Close enhanced-session-data -->
        </div> <!-- Close tuning-session-results -->

        <!-- Enhanced Journal Content with Tabs -->
        <div class="journal-content-enhanced">
          <div class="content-tabs-container">
            <!-- Tab Navigation -->
            <div class="flex border-b border-gray-200 dark:border-gray-700 mb-4">
              <button
                v-for="tab in contentTabs"
                :key="tab.id"
                @click="activeContentTab = tab.id"
                :class="[
                  'px-4 py-2 text-sm font-medium transition-colors',
                  'border-b-2 border-transparent',
                  activeContentTab === tab.id
                    ? 'text-blue-600 dark:text-blue-400 border-blue-600 dark:border-blue-400'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                ]"
              >
                <md-icon class="text-sm mr-2">{{ tab.icon }}</md-icon>
                {{ tab.label }}
              </button>
            </div>

            <!-- Tab Content -->
            <div class="tab-content">
              <!-- Overview Tab -->
              <div v-show="activeContentTab === 'overview'" class="content-card">
                <div class="prose dark:prose-invert max-w-none">
                  <div class="formatted-content">
                    {{ getContentSummary(entry?.content) }}
                  </div>
                  <md-outlined-button 
                    v-if="isContentLong(entry?.content)"
                    @click="showFullContent = !showFullContent" 
                    class="mt-4"
                  >
                    <md-icon slot="icon">{{ showFullContent ? 'expand_less' : 'expand_more' }}</md-icon>
                    {{ showFullContent ? 'Show Less' : 'Show More' }}
                  </md-outlined-button>
                </div>
              </div>

              <!-- Technical Tab -->
              <div v-show="activeContentTab === 'technical'" class="content-card">
                <div class="technical-specs-grid">
                  <div v-if="parsedTechnicalData.arrow" class="spec-section">
                    <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                      <md-icon class="mr-2">arrow_forward</md-icon>
                      Arrow Specifications
                    </h4>
                    <div class="grid grid-cols-2 gap-3">
                      <div v-for="(value, key) in parsedTechnicalData.arrow" :key="key" class="spec-item">
                        <span class="spec-label">{{ formatSpecLabel(key) }}:</span>
                        <span class="spec-value">{{ value }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="parsedTechnicalData.bow" class="spec-section">
                    <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                      <md-icon class="mr-2">sports</md-icon>
                      Bow Configuration
                    </h4>
                    <div class="grid grid-cols-2 gap-3">
                      <div v-for="(value, key) in parsedTechnicalData.bow" :key="key" class="spec-item">
                        <span class="spec-label">{{ formatSpecLabel(key) }}:</span>
                        <span class="spec-value">{{ value }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Analysis Tab -->
              <div v-show="activeContentTab === 'analysis'" class="content-card">
                <div class="analysis-content">
                  <div v-if="parsedAnalysisData.recommendations" class="analysis-section">
                    <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                      <md-icon class="mr-2">psychology</md-icon>
                      Analysis & Recommendations
                    </h4>
                    <div class="recommendations-list">
                      <div v-for="(rec, index) in parsedAnalysisData.recommendations" :key="index" class="recommendation-item">
                        <md-icon class="recommendation-icon">{{ rec.type === 'success' ? 'check_circle' : 'info' }}</md-icon>
                        <span>{{ rec.text }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="parsedAnalysisData.trends" class="analysis-section">
                    <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                      <md-icon class="mr-2">trending_up</md-icon>
                      Progress Trends
                    </h4>
                    <div class="trends-content">
                      {{ parsedAnalysisData.trends }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Full Notes Tab -->
              <div v-show="activeContentTab === 'notes'" class="content-card">
                <div class="prose dark:prose-invert max-w-none">
                  <pre class="whitespace-pre-wrap font-sans text-gray-700 dark:text-gray-300 leading-relaxed text-sm">{{ entry?.content }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tags Section -->
        <div v-if="entry?.tags && entry.tags.length > 0" class="tags-section">
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Tags</h4>
          <div class="flex flex-wrap gap-2">
            <md-chip 
              v-for="tag in entry.tags" 
              :key="tag"
              class="tag-chip"
            >
              {{ tag }}
            </md-chip>
          </div>
        </div>

        <!-- Equipment References -->
        <div v-if="entry?.equipment_references && entry.equipment_references.length > 0" class="equipment-section">
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Referenced Equipment</h4>
          <div class="space-y-2">
            <div 
              v-for="ref in entry.equipment_references" 
              :key="ref.id"
              class="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg"
            >
              <md-icon class="text-gray-500">{{ ref.bow_equipment_id ? 'hardware' : 'arrow_forward' }}</md-icon>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {{ ref.manufacturer_name || ref.arrow_manufacturer }} 
                  {{ ref.model_name || ref.arrow_model }}
                </div>
                <div class="text-xs text-gray-500">{{ ref.reference_type }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Attachments Section -->
        <div v-if="entry?.attachments && entry.attachments.length > 0" class="attachments-section">
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Attachments</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div 
              v-for="attachment in entry.attachments" 
              :key="attachment.id"
              class="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition-colors"
              @click="openAttachment(attachment)"
            >
              <md-icon class="text-gray-500">{{ getAttachmentIcon(attachment.file_type) }}</md-icon>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {{ attachment.original_filename }}
                </div>
                <div class="text-xs text-gray-500">{{ attachment.file_type }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Entry Metadata -->
        <div class="metadata-section border-t border-gray-200 dark:border-gray-700 pt-4">
          <div class="text-xs text-gray-500 dark:text-gray-400 space-y-1">
            <div class="flex justify-between">
              <span>Created:</span>
              <span>{{ formatDetailedDate(entry?.created_at) }}</span>
            </div>
            <div v-if="entry?.updated_at !== entry?.created_at" class="flex justify-between">
              <span>Updated:</span>
              <span>{{ formatDetailedDate(entry?.updated_at) }}</span>
            </div>
            <div v-if="entry?.is_private" class="flex items-center gap-1">
              <md-icon class="text-xs">lock</md-icon>
              <span>Private Entry</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Fixed Bottom Actions Bar -->
      <div class="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-900">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <!-- View Original Session Button for Tuning Sessions -->
            <md-outlined-button 
              v-if="isTuningSession && (sessionData || entry?.session_data)?.session_id" 
              @click="viewOriginalSession" 
              size="small"
              class="text-blue-600 dark:text-blue-400"
            >
              <md-icon slot="icon">replay</md-icon>
              View Session
            </md-outlined-button>
            
            <!-- Start Similar Session Button -->
            <md-outlined-button 
              v-if="isTuningSession && (sessionData || entry?.session_data)" 
              @click="startSimilarSession" 
              size="small"
              class="text-green-600 dark:text-green-400"
            >
              <md-icon slot="icon">add_circle</md-icon>
              New Session
            </md-outlined-button>
            
            <md-outlined-button @click="editEntry" size="small">
              <md-icon slot="icon">edit</md-icon>
              Edit
            </md-outlined-button>
            <md-outlined-button @click="shareEntry" size="small">
              <md-icon slot="icon">share</md-icon>
              Share
            </md-outlined-button>
          </div>
          
          <md-text-button @click="closeViewer">
            Close
          </md-text-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits, watch, ref } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  entry: {
    type: Object,
    default: null
  },
  fullPage: {
    type: Boolean,
    default: false
  }
})

// Debug the entry data structure
watch(() => props.entry, (newEntry) => {
  if (newEntry) {
    console.log('JournalEntryDetailViewer: Entry data received:', {
      id: newEntry.id,
      title: newEntry.title,
      entry_type: newEntry.entry_type,
      session_metadata: newEntry.session_metadata,
      session_data: newEntry.session_data,
      session_type: newEntry.session_type,
      fullEntry: newEntry
    })
  }
}, { immediate: true })

const emit = defineEmits(['close', 'edit', 'delete', 'favorite', 'view-session', 'start-similar'])

// Computed properties
const isFullPage = computed(() => {
  // Detect full-page mode by prop or by checking if we're in a full-page context
  return props.fullPage || (typeof window !== 'undefined' && window.location.pathname.includes('/journal/'))
})
const isTuningSession = computed(() => {
  const result = props.entry?.entry_type?.includes('tuning') || 
         props.entry?.session_data?.tuning_type ||
         props.entry?.session_type === 'paper' ||
         props.entry?.session_type === 'bareshaft' ||
         props.entry?.session_type === 'walkback'
  
  console.log('JournalEntryDetailViewer: isTuningSession computed:', {
    result,
    entry_type: props.entry?.entry_type,
    session_data_tuning_type: props.entry?.session_data?.tuning_type,
    session_type: props.entry?.session_type
  })
  
  return result
})

// Parse session data from different sources
const sessionData = computed(() => {
  // Parse session_metadata if it exists
  if (props.entry?.session_metadata) {
    try {
      const parsed = typeof props.entry.session_metadata === 'string' 
        ? JSON.parse(props.entry.session_metadata)
        : props.entry.session_metadata
      
      // Debug log to help identify data structure issues
      console.log('Parsed session data:', parsed)
      return parsed
    } catch (e) {
      console.warn('Failed to parse session metadata:', e)
    }
  }
  
  // Fallback to legacy session_data
  if (props.entry?.session_data) {
    console.log('Using legacy session_data:', props.entry.session_data)
    return props.entry.session_data
  }
  
  return null
})

// Entry type mapping
const entryTypeMap = {
  general: { label: 'General', icon: 'notes' },
  setup_change: { label: 'Setup Change', icon: 'build' },
  equipment_change: { label: 'Equipment', icon: 'hardware' },
  arrow_change: { label: 'Arrow', icon: 'arrow_forward' },
  tuning_session: { label: 'Tuning', icon: 'tune' },
  bareshaft_tuning_session: { label: 'Bareshaft Tuning', icon: 'tune' },
  walkback_tuning_session: { label: 'Walkback Tuning', icon: 'tune' },
  paper_tuning_session: { label: 'Paper Tuning', icon: 'tune' },
  shooting_notes: { label: 'Shooting', icon: 'sports' },
  maintenance: { label: 'Maintenance', icon: 'handyman' },
  upgrade: { label: 'Upgrade', icon: 'upgrade' }
}

// Helper functions
const getEntryTypeLabel = (type) => {
  return entryTypeMap[type]?.label || 'General'
}

const getEntryTypeIcon = (type) => {
  return entryTypeMap[type]?.icon || 'notes'
}

const getEntryTypeBadgeClass = (type) => {
  const baseClass = 'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium'
  const typeClasses = {
    tuning_session: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200',
    bareshaft_tuning_session: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200',
    walkback_tuning_session: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200',
    paper_tuning_session: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-200',
    setup_change: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-200',
    equipment_change: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    general: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }
  return `${baseClass} ${typeClasses[type] || typeClasses.general}`
}

const getTuningTypeLabel = (type) => {
  const labels = {
    bareshaft: 'Bareshaft Tuning',
    walkback: 'Walkback Tuning',
    paper: 'Paper Tuning'
  }
  return labels[type] || 'Tuning Session'
}

const getQualityBarColor = (score) => {
  if (score >= 85) return 'bg-green-500'
  if (score >= 70) return 'bg-blue-500'
  if (score >= 55) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getQualityTextColor = (score) => {
  if (score >= 85) return 'text-green-600 dark:text-green-400'
  if (score >= 70) return 'text-blue-600 dark:text-blue-400'
  if (score >= 55) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

const getTestQualityColor = (score) => {
  if (score >= 85) return 'bg-green-500'
  if (score >= 70) return 'bg-blue-500'
  if (score >= 55) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getAttachmentIcon = (fileType) => {
  switch (fileType) {
    case 'image': return 'image'
    case 'video': return 'videocam'
    case 'document': return 'description'
    default: return 'attach_file'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const formatDetailedDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatOffset = (offsetCm) => {
  const abs = Math.abs(offsetCm)
  const direction = offsetCm > 0 ? 'R' : 'L'
  return `${abs.toFixed(1)}cm ${direction}`
}

// Enhanced helper functions for tuning session display
const getAverageConfidence = (testResults) => {
  if (!testResults || testResults.length === 0) return 0
  const total = testResults.reduce((sum, test) => sum + (test.confidence_score || 0), 0)
  return Math.round(total / testResults.length)
}

const formatTestTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: true 
  })
}

const getSortedDistanceTests = (testResults) => {
  if (!testResults) return []
  return [...testResults].sort((a, b) => (a.distance_m || 0) - (b.distance_m || 0))
}

const formatSlope = (slope) => {
  if (slope === null || slope === undefined) return 'N/A'
  return slope.toFixed(4)
}

const getOffsetTextColor = (offset) => {
  const abs = Math.abs(offset)
  if (abs <= 1) return 'text-green-600 dark:text-green-400'
  if (abs <= 2) return 'text-yellow-600 dark:text-yellow-400'
  if (abs <= 4) return 'text-orange-600 dark:text-orange-400'
  return 'text-red-600 dark:text-red-400'
}

const getOffsetBarColor = (offset) => {
  const abs = Math.abs(offset)
  if (abs <= 1) return 'bg-green-500'
  if (abs <= 2) return 'bg-yellow-500'
  if (abs <= 4) return 'bg-orange-500'
  return 'bg-red-500'
}

const getOffsetBarStyle = (offset) => {
  const abs = Math.abs(offset)
  const maxOffset = 6 // Scale bar based on reasonable max offset
  const widthPercent = Math.min((abs / maxOffset) * 100, 100)
  
  // Position bar based on direction (left/right of center)
  const isRight = offset > 0
  return {
    width: `${widthPercent}%`,
    left: isRight ? '50%' : `${50 - widthPercent}%`
  }
}

const getConfidenceTextColor = (score) => {
  if (score >= 85) return 'text-green-600 dark:text-green-400'
  if (score >= 70) return 'text-blue-600 dark:text-blue-400'
  if (score >= 55) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

const getConfidenceBarColor = (score) => {
  if (score >= 85) return 'bg-green-500'
  if (score >= 70) return 'bg-blue-500'
  if (score >= 55) return 'bg-yellow-500'
  return 'bg-red-500'
}

// Paper tuning specific helper functions
const formatTearDirection = (direction) => {
  const directionMap = {
    'high': 'High',
    'high-right': 'High Right',
    'right': 'Right',
    'low-right': 'Low Right',
    'low': 'Low',
    'low-left': 'Low Left',
    'left': 'Left',
    'high-left': 'High Left',
    'clean': 'Perfect Hole'
  }
  return directionMap[direction] || direction || 'Unknown'
}

const formatTearSize = (tearSize) => {
  if (!tearSize && tearSize !== 0) return 'N/A'
  if (tearSize === 0) return 'Clean'
  return `${tearSize}"`
}

const getTearQualityColor = (tearSize) => {
  if (!tearSize && tearSize !== 0) return 'bg-gray-500'
  if (tearSize <= 0.25) return 'bg-green-500'
  if (tearSize <= 0.5) return 'bg-blue-500'
  if (tearSize <= 0.75) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getTearSizeTextColor = (tearSize) => {
  if (!tearSize && tearSize !== 0) return 'text-gray-600 dark:text-gray-400'
  if (tearSize <= 0.25) return 'text-green-600 dark:text-green-400'
  if (tearSize <= 0.5) return 'text-blue-600 dark:text-blue-400'
  if (tearSize <= 0.75) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

const getTearSizeBarColor = (tearSize) => {
  if (!tearSize && tearSize !== 0) return 'bg-gray-500'
  if (tearSize <= 0.25) return 'bg-green-500'
  if (tearSize <= 0.5) return 'bg-blue-500'
  if (tearSize <= 0.75) return 'bg-yellow-500'
  return 'bg-red-500'
}

// Event handlers
const closeViewer = () => {
  emit('close')
}

const editEntry = () => {
  emit('edit', props.entry)
  closeViewer()
}

const toggleFavorite = () => {
  emit('favorite', props.entry)
}

const shareEntry = () => {
  // Implement sharing functionality
  if (navigator.share) {
    navigator.share({
      title: props.entry?.title,
      text: props.entry?.content?.substring(0, 200) + '...',
      url: window.location.href
    })
  } else {
    // Fallback: copy to clipboard
    navigator.clipboard.writeText(`${props.entry?.title}\n\n${props.entry?.content}`)
  }
}

const openAttachment = (attachment) => {
  // Implement attachment opening
  console.log('Opening attachment:', attachment)
}

// New session-related event handlers
const viewOriginalSession = () => {
  const data = sessionData.value || props.entry?.session_data
  if (data?.session_id && data?.tuning_type) {
    emit('view-session', {
      sessionId: data.session_id,
      tuningType: data.tuning_type,
      entry: props.entry
    })
    closeViewer()
  }
}

const startSimilarSession = () => {
  const data = sessionData.value || props.entry?.session_data
  if (data) {
    emit('start-similar', {
      sessionData: data,
      entry: props.entry
    })
    closeViewer()
  }
}

const startNewSession = () => {
  // Navigate to tuning session selection or start a new session
  // For now, we'll navigate to the calculator page where users can start tuning
  if (typeof window !== 'undefined') {
    window.location.href = '/calculator'
  }
}

// Tabbed content interface - Priority 1 improvement
const activeContentTab = ref('overview')
const showFullContent = ref(false)

// Tab definitions
const contentTabs = computed(() => [
  { id: 'overview', label: 'Overview', icon: 'visibility' },
  { id: 'technical', label: 'Technical', icon: 'engineering' },
  { id: 'analysis', label: 'Analysis', icon: 'psychology' },
  { id: 'notes', label: 'Full Notes', icon: 'notes' }
])

// Content processing functions
const isContentLong = (content) => {
  return content && content.length > 500
}

const getContentSummary = (content) => {
  if (!content) return 'No content available'
  if (showFullContent.value || content.length <= 500) return content
  return content.substring(0, 500) + '...'
}

// Technical data parsing
const parsedTechnicalData = computed(() => {
  const content = props.entry?.content || ''
  
  // Extract arrow specifications from content
  const arrowSpecs = {}
  const bowSpecs = {}
  
  // Parse common patterns from content
  const lines = content.split('\n')
  let currentSection = ''
  
  lines.forEach(line => {
    line = line.trim()
    if (line.includes('Arrow Technical Specifications') || line.includes('## Arrow Specifications')) {
      currentSection = 'arrow'
    } else if (line.includes('Bow Setup Configuration') || line.includes('## Bow Configuration')) {
      currentSection = 'bow'
    } else if (line.startsWith('- **')) {
      const match = line.match(/- \*\*([^*]+)\*\*:\s*(.+)/)
      if (match && currentSection) {
        const key = match[1].toLowerCase().replace(/\s+/g, '_')
        const value = match[2]
        if (currentSection === 'arrow') {
          arrowSpecs[key] = value
        } else if (currentSection === 'bow') {
          bowSpecs[key] = value
        }
      }
    }
  })
  
  return {
    arrow: Object.keys(arrowSpecs).length > 0 ? arrowSpecs : null,
    bow: Object.keys(bowSpecs).length > 0 ? bowSpecs : null
  }
})

// Analysis data parsing
const parsedAnalysisData = computed(() => {
  const content = props.entry?.content || ''
  
  // Extract recommendations
  const recommendations = []
  const lines = content.split('\n')
  
  lines.forEach(line => {
    line = line.trim()
    if (line.startsWith('• ') || line.startsWith('- ')) {
      const text = line.substring(2)
      const type = text.toLowerCase().includes('excellent') || text.toLowerCase().includes('good') ? 'success' : 'info'
      recommendations.push({ text, type })
    }
  })
  
  // Extract trends
  let trends = ''
  const trendMatch = content.match(/Progress Trend[^:]*:\s*([^\n]+)/i)
  if (trendMatch) {
    trends = trendMatch[1]
  }
  
  return {
    recommendations: recommendations.length > 0 ? recommendations : null,
    trends: trends || null
  }
})

// Format specification labels
const formatSpecLabel = (key) => {
  return key.replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
    .replace(/Gpi/g, 'GPI')
    .replace(/Id/g, 'ID')
}
</script>

<style scoped>
.journal-detail-viewer {
  /* Ensure proper z-index stacking */
}

/* Modal Container Styles */
.modal-container {
  @apply fixed inset-x-0 bottom-0 bg-white dark:bg-gray-900 rounded-t-xl shadow-2xl z-50 max-h-[90vh] transform transition-transform duration-300;
}

/* Full Page Container Styles */
.full-page-container {
  @apply bg-white dark:bg-gray-900 w-full min-h-screen;
}

/* Full Page Mode Adjustments */
.full-page-mode .full-page-container {
  @apply rounded-none shadow-none;
}

.stat-card {
  @apply p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700;
}

.stat-label {
  @apply text-xs font-medium text-gray-500 dark:text-gray-400 mb-1;
}

.stat-value {
  @apply text-lg font-bold text-gray-900 dark:text-gray-100;
}

.tag-chip {
  @apply bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200;
}

/* Mobile-specific adjustments */
@media (max-width: 640px) {
  .journal-detail-viewer .fixed {
    max-height: 95vh;
  }
}

/* Smooth animations */
.journal-detail-viewer * {
  transition: all 0.2s ease-in-out;
}

/* Enhanced Content Tabs - Priority 1 UI improvement */
.content-tabs-container {
  @apply bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-6;
}

.tab-content .content-card {
  @apply bg-gray-50 dark:bg-gray-900 rounded-lg p-4;
}

.technical-specs-grid .spec-section {
  @apply mb-6 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700;
}

.technical-specs-grid .spec-item {
  @apply flex justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-b-0;
}

.spec-label {
  @apply font-medium text-gray-600 dark:text-gray-400 text-sm;
}

.spec-value {
  @apply text-gray-900 dark:text-gray-100 font-mono text-sm text-right;
}

.analysis-section {
  @apply mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700;
}

.recommendations-list {
  @apply space-y-2;
}

.recommendation-item {
  @apply flex items-center gap-2 text-sm;
}

.recommendation-icon {
  @apply text-sm;
}

.trends-content {
  @apply text-sm text-gray-700 dark:text-gray-300 italic;
}

.formatted-content {
  @apply whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 leading-relaxed;
}
</style>