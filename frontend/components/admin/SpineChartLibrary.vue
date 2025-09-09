<template>
  <div class="spine-chart-library">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
          <i class="fas fa-chart-line mr-2"></i>
          Spine Chart Library
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Manage manufacturer spine charts and create custom charts
        </p>
      </div>
      <CustomButton
        @click="showCreateModal = true"
        variant="filled"
        class="bg-green-600 text-white hover:bg-green-700"
      >
        <i class="fas fa-plus mr-2"></i>
        Create Custom Chart
      </CustomButton>
    </div>

    <!-- Stats Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
        <div class="flex items-center">
          <i class="fas fa-industry text-blue-600 dark:text-blue-400 text-2xl mr-3"></i>
          <div>
            <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">
              {{ manufacturerCharts.length }}
            </p>
            <p class="text-sm text-blue-700 dark:text-blue-300">Manufacturer Charts</p>
          </div>
        </div>
      </div>
      
      <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
        <div class="flex items-center">
          <i class="fas fa-user-cog text-green-600 dark:text-green-400 text-2xl mr-3"></i>
          <div>
            <p class="text-2xl font-bold text-green-900 dark:text-green-100">
              {{ customCharts.length }}
            </p>
            <p class="text-sm text-green-700 dark:text-green-300">Custom Charts</p>
          </div>
        </div>
      </div>
      
      <div class="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
        <div class="flex items-center">
          <i class="fas fa-chart-area text-purple-600 dark:text-purple-400 text-2xl mr-3"></i>
          <div>
            <p class="text-2xl font-bold text-purple-900 dark:text-purple-100">
              {{ totalCharts }}
            </p>
            <p class="text-sm text-purple-700 dark:text-purple-300">Total Charts</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            Chart Type
          </label>
          <md-filled-select 
            :value="filters.chartType" 
            @change="updateFilter('chartType', $event.target.value)"
            label="Filter by type"
            class="w-full"
          >
            <md-select-option value="">All Types</md-select-option>
            <md-select-option value="manufacturer">Manufacturer Charts</md-select-option>
            <md-select-option value="custom">Custom Charts</md-select-option>
          </md-filled-select>
        </div>
        
        <div>
          <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            Manufacturer
          </label>
          <md-filled-select 
            :value="filters.manufacturer" 
            @change="updateFilter('manufacturer', $event.target.value)"
            label="Filter by manufacturer"
            class="w-full"
          >
            <md-select-option value="">All Manufacturers</md-select-option>
            <md-select-option 
              v-for="manufacturer in uniqueManufacturers" 
              :key="manufacturer" 
              :value="manufacturer"
            >
              {{ manufacturer }}
            </md-select-option>
          </md-filled-select>
        </div>
        
        <div>
          <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            Bow Type
          </label>
          <md-filled-select 
            :value="filters.bowType" 
            @change="updateFilter('bowType', $event.target.value)"
            label="Filter by bow type"
            class="w-full"
          >
            <md-select-option value="">All Bow Types</md-select-option>
            <md-select-option value="compound">Compound</md-select-option>
            <md-select-option value="recurve">Recurve</md-select-option>
            <md-select-option value="longbow">Longbow</md-select-option>
            <md-select-option value="traditional">Traditional</md-select-option>
          </md-filled-select>
        </div>
        
        <div>
          <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            Search
          </label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search charts..."
            class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
          />
        </div>
      </div>
      
      <div class="flex justify-end mt-3">
        <CustomButton
          @click="clearFilters"
          variant="outlined"
          size="small"
          class="text-gray-600 border-gray-300 hover:bg-gray-100 dark:text-gray-400 dark:border-gray-600"
        >
          <i class="fas fa-times mr-1"></i>
          Clear Filters
        </CustomButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent dark:border-purple-400"></div>
      <span class="ml-3 text-gray-600 dark:text-gray-400">Loading spine charts...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-700 dark:text-red-300">
        <i class="fas fa-exclamation-triangle mr-2"></i>
        {{ error }}
      </p>
    </div>

    <!-- Charts Table -->
    <div v-else class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Chart
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Type
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Bow Type
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Spine System
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Status
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                System Default
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-600">
            <tr 
              v-for="chart in filteredCharts" 
              :key="`${chart.chart_type}-${chart.id}`"
              class="hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <td class="px-4 py-4">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {{ chart.manufacturer }} {{ chart.model }}
                  </p>
                  <p v-if="chart.chart_notes" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {{ chart.chart_notes.substring(0, 50) }}{{ chart.chart_notes.length > 50 ? '...' : '' }}
                  </p>
                </div>
              </td>
              <td class="px-4 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full" :class="[
                  chart.chart_type === 'manufacturer' 
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                    : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                ]">
                  {{ chart.chart_type === 'manufacturer' ? 'Manufacturer' : 'Custom' }}
                </span>
              </td>
              <td class="px-4 py-4 text-sm text-gray-900 dark:text-gray-100">
                {{ formatBowType(chart.bow_type) }}
              </td>
              <td class="px-4 py-4 text-sm text-gray-900 dark:text-gray-100">
                {{ formatSpineSystem(chart.spine_system) }}
              </td>
              <td class="px-4 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full" :class="[
                  chart.is_active 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                ]">
                  {{ chart.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-4 py-4 text-center">
                <span v-if="chart.is_system_default" class="inline-flex items-center px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full">
                  <i class="fas fa-star text-yellow-600 dark:text-yellow-400 mr-1"></i>
                  Default
                </span>
                <span v-else class="text-gray-400 dark:text-gray-500 text-xs">
                  —
                </span>
              </td>
              <td class="px-4 py-4">
                <div class="flex items-center space-x-1">
                  <CustomButton
                    @click="viewChart(chart)"
                    variant="text"
                    size="small"
                    class="text-blue-600 hover:bg-blue-100 dark:text-blue-400"
                    title="View chart details"
                  >
                    <i class="fas fa-eye"></i>
                  </CustomButton>
                  <CustomButton
                    @click="editChart(chart)"
                    variant="text"
                    size="small"
                    class="text-green-600 hover:bg-green-100 dark:text-green-400"
                    :title="chart.chart_type === 'manufacturer' ? 'View/Edit (Read-only for manufacturer charts)' : 'Edit Chart'"
                  >
                    <i class="fas fa-edit"></i>
                  </CustomButton>
                  <!-- System default is now managed through chart editing -->
                  <CustomButton
                    @click="duplicateChart(chart)"
                    variant="text"
                    size="small"
                    class="text-indigo-600 hover:bg-indigo-100 dark:text-indigo-400"
                    title="Duplicate chart for testing"
                  >
                    <i class="fas fa-clone"></i>
                  </CustomButton>
                  <CustomButton
                    v-if="chart.chart_type === 'manufacturer'"
                    @click="createOverride(chart)"
                    variant="text"
                    size="small"
                    class="text-purple-600 hover:bg-purple-100 dark:text-purple-400"
                    title="Create editable custom chart based on this manufacturer chart"
                  >
                    <i class="fas fa-copy"></i>
                  </CustomButton>
                  <CustomButton
                    v-if="chart.chart_type === 'custom'"
                    @click="deleteChart(chart)"
                    variant="text"
                    size="small"
                    class="text-red-600 hover:bg-red-100 dark:text-red-400"
                    title="Delete custom chart"
                  >
                    <i class="fas fa-trash"></i>
                  </CustomButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Empty State -->
      <div v-if="filteredCharts.length === 0" class="text-center py-8">
        <i class="fas fa-chart-line text-4xl text-gray-400 dark:text-gray-500 mb-3"></i>
        <p class="text-gray-500 dark:text-gray-400">No spine charts match your current filters</p>
      </div>
    </div>

    <!-- View Chart Modal -->
    <div v-if="showViewModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 transition-opacity bg-black bg-opacity-50" @click="showViewModal = false"></div>
        
        <!-- Modal -->
        <div class="inline-block w-full max-w-4xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-xl rounded-lg">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              <i class="fas fa-chart-line mr-2"></i>
              {{ selectedChart?.manufacturer }} {{ selectedChart?.model }}
            </h3>
            <CustomButton
              @click="showViewModal = false"
              variant="text"
              size="small"
              class="text-gray-400 hover:text-gray-600"
            >
              <i class="fas fa-times"></i>
            </CustomButton>
          </div>
          
          <!-- Chart Details -->
          <div v-if="selectedChart" class="space-y-4">
            <!-- Basic Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <label class="text-xs font-medium text-gray-500 dark:text-gray-400">Chart Type</label>
                <p class="text-sm font-medium text-gray-900 dark:text-gray-100 capitalize">{{ selectedChart.chart_type }}</p>
              </div>
              <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <label class="text-xs font-medium text-gray-500 dark:text-gray-400">Bow Type</label>
                <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatBowType(selectedChart.bow_type) }}</p>
              </div>
              <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <label class="text-xs font-medium text-gray-500 dark:text-gray-400">Spine System</label>
                <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatSpineSystem(selectedChart.spine_system) }}</p>
              </div>
              <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <label class="text-xs font-medium text-gray-500 dark:text-gray-400">Status</label>
                <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full" :class="[
                  selectedChart.is_active 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                ]">
                  {{ selectedChart.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>

            <!-- Chart Notes -->
            <div v-if="selectedChart.chart_notes" class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded border border-blue-200 dark:border-blue-800">
              <label class="text-xs font-medium text-blue-700 dark:text-blue-300 mb-2 block">Chart Notes</label>
              <p class="text-sm text-blue-800 dark:text-blue-200">{{ selectedChart.chart_notes }}</p>
            </div>

            <!-- Provenance -->
            <div v-if="selectedChart.provenance" class="bg-purple-50 dark:bg-purple-900/20 p-4 rounded border border-purple-200 dark:border-purple-800">
              <label class="text-xs font-medium text-purple-700 dark:text-purple-300 mb-2 block">Source</label>
              <p class="text-sm text-purple-800 dark:text-purple-200">{{ selectedChart.provenance }}</p>
            </div>

            <!-- Spine Grid -->
            <div v-if="selectedChart.spine_grid && selectedChart.spine_grid.length > 0" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <div class="bg-gray-50 dark:bg-gray-700 px-4 py-2 border-b border-gray-200 dark:border-gray-600">
                <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">Spine Chart Grid ({{ selectedChart.spine_grid.length }} entries)</h4>
              </div>
              <div class="overflow-x-auto max-h-64">
                <table class="min-w-full">
                  <thead class="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300">Draw Weight</th>
                      <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300">Arrow Length</th>
                      <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300">Recommended Spine</th>
                      <th v-if="selectedChart.spine_grid.some(entry => entry.arrow_size)" class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300">Arrow Size</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200 dark:divide-gray-600">
                    <tr v-for="(entry, index) in selectedChart.spine_grid" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">{{ entry.draw_weight_range_lbs }} lbs</td>
                      <td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">{{ entry.arrow_length_in }}"</td>
                      <td class="px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400">{{ entry.spine }}</td>
                      <td v-if="entry.arrow_size" class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300">{{ entry.arrow_size }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- No Spine Grid Message -->
            <div v-else class="text-center py-8 bg-gray-50 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
              <i class="fas fa-table text-2xl text-gray-400 mb-2"></i>
              <p class="text-sm text-gray-500 dark:text-gray-400">No spine grid data available for this chart</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Chart Modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 transition-opacity bg-black bg-opacity-50" @click="closeEditModal"></div>
        
        <!-- Modal -->
        <div class="inline-block w-full max-w-3xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-xl rounded-lg">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              <i class="fas fa-edit mr-2"></i>
              {{ editingChart?.chart_type === 'manufacturer' ? 'View Chart (Read-only)' : 'Edit Chart' }}
            </h3>
            <CustomButton
              @click="closeEditModal"
              variant="text"
              size="small"
              class="text-gray-400 hover:text-gray-600"
            >
              <i class="fas fa-times"></i>
            </CustomButton>
          </div>
          
          <!-- Edit Form -->
          <div v-if="editingChart" class="space-y-4">
            <!-- Read-only Notice for Manufacturer Charts -->
            <div v-if="editingChart.chart_type === 'manufacturer'" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
              <div class="flex items-center">
                <i class="fas fa-info-circle text-yellow-600 dark:text-yellow-400 mr-2"></i>
                <p class="text-sm text-yellow-800 dark:text-yellow-200">
                  Manufacturer charts are read-only. You can view the data but cannot make changes.
                </p>
              </div>
            </div>

            <!-- Basic Chart Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Manufacturer</label>
                <input
                  v-model="editingChart.manufacturer"
                  :readonly="editingChart.chart_type === 'manufacturer'"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  :class="{ 'bg-gray-100 dark:bg-gray-600 cursor-not-allowed': editingChart.chart_type === 'manufacturer' }"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Model</label>
                <input
                  v-model="editingChart.model"
                  :readonly="editingChart.chart_type === 'manufacturer'"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  :class="{ 'bg-gray-100 dark:bg-gray-600 cursor-not-allowed': editingChart.chart_type === 'manufacturer' }"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bow Type</label>
                <md-filled-select
                  :value="editingChart.bow_type"
                  @change="editingChart.bow_type = $event.target.value"
                  :disabled="editingChart.chart_type === 'manufacturer'"
                  label="Select bow type"
                  class="w-full"
                >
                  <md-select-option value="compound">Compound</md-select-option>
                  <md-select-option value="recurve">Recurve</md-select-option>
                  <md-select-option value="longbow">Longbow</md-select-option>
                  <md-select-option value="traditional">Traditional</md-select-option>
                </md-filled-select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Spine System</label>
                <md-filled-select
                  :value="editingChart.spine_system"
                  @change="editingChart.spine_system = $event.target.value"
                  :disabled="editingChart.chart_type === 'manufacturer'"
                  label="Select spine system"
                  class="w-full"
                >
                  <md-select-option value="standard_deflection">Standard Deflection</md-select-option>
                  <md-select-option value="carbon">Carbon</md-select-option>
                  <md-select-option value="aluminum">Aluminum</md-select-option>
                  <md-select-option value="wood_spine_range">Wood</md-select-option>
                </md-filled-select>
              </div>
            </div>

            <!-- Chart Notes -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Chart Notes</label>
              <textarea
                v-model="editingChart.chart_notes"
                :readonly="editingChart.chart_type === 'manufacturer'"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                :class="{ 'bg-gray-100 dark:bg-gray-600 cursor-not-allowed': editingChart.chart_type === 'manufacturer' }"
                placeholder="Add notes about this spine chart..."
              ></textarea>
            </div>

            <!-- Active Status -->
            <div class="flex items-center space-x-3">
              <input
                v-model="editingChart.is_active"
                :disabled="editingChart.chart_type === 'manufacturer'"
                type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label class="text-sm text-gray-700 dark:text-gray-300">
                Chart is active and available for calculations
              </label>
            </div>
            
            <!-- System Default Status -->
            <div class="flex items-center space-x-3">
              <input
                v-model="editingChart.is_system_default"
                type="checkbox"
                class="w-4 h-4 text-yellow-600 border-gray-300 rounded focus:ring-yellow-500"
              />
              <label class="text-sm text-gray-700 dark:text-gray-300">
                <i class="fas fa-star text-yellow-500 mr-1"></i>
                Set as system default for {{ formatBowType(editingChart.bow_type) }} bows
              </label>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400 ml-7">
              System default charts are automatically selected when users load the calculator for this bow type.
              Only one chart per bow type can be the system default.
            </p>

            <!-- Spine Grid Editor -->
            <div class="border-t border-gray-200 dark:border-gray-600 pt-4">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">
                  <i class="fas fa-table mr-2"></i>
                  Spine Chart Grid ({{ editingChart.spine_grid?.length || 0 }} entries)
                </h4>
                <div class="flex space-x-2">
                  <CustomButton
                    v-if="editingChart.chart_type === 'custom'"
                    @click="addSpineEntry"
                    variant="outlined"
                    size="small"
                    class="text-green-600 border-green-300 hover:bg-green-50 dark:text-green-400 dark:border-green-600"
                  >
                    <i class="fas fa-plus mr-1"></i>
                    Add Entry
                  </CustomButton>
                  <CustomButton
                    @click="showGridEditor = !showGridEditor"
                    variant="text"
                    size="small"
                    class="text-blue-600 hover:bg-blue-100 dark:text-blue-400"
                  >
                    <i class="fas" :class="showGridEditor ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                    {{ showGridEditor ? 'Hide' : 'Show' }} Grid
                  </CustomButton>
                </div>
              </div>

              <!-- Grid Editor -->
              <div v-if="showGridEditor" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div v-if="editingChart.chart_type === 'manufacturer'" class="mb-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded text-sm text-yellow-800 dark:text-yellow-200">
                  <i class="fas fa-info-circle mr-2"></i>
                  Manufacturer chart data is read-only. Create a custom chart to modify spine grid entries.
                </div>

                <!-- DataTables Component -->
                <SpineChartDataTable
                  ref="spineDataTable"
                  :data="editingChart.spine_grid || []"
                  :readonly="editingChart.chart_type === 'manufacturer'"
                  :loading="false"
                  :error="''"
                  @data-change="handleGridDataChange"
                  @row-add="handleRowAdd"
                  @row-edit="handleRowEdit"
                  @row-delete="handleRowDelete"
                />
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-600">
              <CustomButton
                @click="closeEditModal"
                variant="outlined"
                class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700"
              >
                Cancel
              </CustomButton>
              <CustomButton
                @click="saveChart"
                :disabled="savingChart"
                variant="filled"
                class="bg-blue-600 text-white hover:bg-blue-700"
              >
                <i v-if="savingChart" class="fas fa-spinner fa-spin mr-2"></i>
                <i v-else class="fas fa-save mr-2"></i>
                {{ savingChart ? 'Saving...' : 'Save Changes' }}
              </CustomButton>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Custom Chart Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 transition-opacity bg-black bg-opacity-50" @click="showCreateModal = false"></div>
        
        <!-- Modal -->
        <div class="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-xl rounded-lg">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Create Custom Spine Chart
            </h3>
            <CustomButton
              @click="showCreateModal = false"
              variant="text"
              size="small"
              class="text-gray-400 hover:text-gray-600"
            >
              <i class="fas fa-times"></i>
            </CustomButton>
          </div>
          
          <!-- Create chart form would go here -->
          <div class="text-center py-8 text-gray-500 dark:text-gray-400">
            <i class="fas fa-tools text-4xl mb-3"></i>
            <p>Custom chart creation interface coming soon!</p>
            <p class="text-sm mt-1">This will allow creating custom spine charts with a visual grid editor.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Spine Entry Edit Modal -->
    <SpineEntryEditModal
      :show="showSpineEntryModal"
      :entry="editingSpineEntry"
      :is-edit="isEditingSpineEntry"
      @save="saveSpineEntry"
      @cancel="cancelSpineEntry"
    />

    <!-- Confirmation Modals -->
    <ConfirmDeleteModal
      v-if="confirmAction.show"
      :title="confirmAction.title"
      :message="confirmAction.message"
      :item-name="confirmAction.itemName"
      :confirm-text="confirmAction.confirmText"
      :loading="confirmAction.loading"
      :error="confirmAction.error"
      @confirm="executeConfirmedAction"
      @cancel="cancelConfirmedAction"
    />
  </div>
</template>

<script setup lang="ts">
interface SpineChart {
  id: number
  chart_type: string
  manufacturer: string
  model: string
  bow_type: string
  spine_system: string
  chart_notes: string
  provenance?: string
  created_by?: string
  is_active: boolean
  is_system_default?: boolean
  calculation_priority?: number
  created_at: string
}

// API
const api = useApi()

// Reactive state
const loading = ref(false)
const error = ref('')
const showCreateModal = ref(false)
const showViewModal = ref(false)
const showEditModal = ref(false)
const showGridEditor = ref(false)
const savingChart = ref(false)
const selectedChart = ref<SpineChart | null>(null)
const editingChart = ref<SpineChart | null>(null)

// Spine entry editing modal state
const showSpineEntryModal = ref(false)
const editingSpineEntry = ref<any | null>(null)
const editingSpineEntryIndex = ref(-1)
const isEditingSpineEntry = ref(false)

// Confirmation modal state
const confirmAction = ref({
  show: false,
  title: '',
  message: '',
  itemName: '',
  confirmText: 'Confirm',
  loading: false,
  error: '',
  action: null as (() => void) | null
})

// Data
const manufacturerCharts = ref<SpineChart[]>([])
const customCharts = ref<SpineChart[]>([])

// Filters
const filters = ref({
  chartType: '',
  manufacturer: '',
  bowType: '',
  search: ''
})

// Computed properties
const totalCharts = computed(() => manufacturerCharts.value.length + customCharts.value.length)

const uniqueManufacturers = computed(() => {
  const manufacturers = new Set<string>()
  manufacturerCharts.value.forEach(chart => {
    if (chart.manufacturer) manufacturers.add(chart.manufacturer)
  })
  customCharts.value.forEach(chart => {
    if (chart.manufacturer) manufacturers.add(chart.manufacturer)
  })
  return Array.from(manufacturers).sort()
})

const allCharts = computed(() => [
  ...manufacturerCharts.value,
  ...customCharts.value
])

const filteredCharts = computed(() => {
  let filtered = allCharts.value

  // Apply chart type filter
  if (filters.value.chartType) {
    filtered = filtered.filter(chart => chart.chart_type === filters.value.chartType)
  }

  // Apply manufacturer filter
  if (filters.value.manufacturer) {
    filtered = filtered.filter(chart => chart.manufacturer === filters.value.manufacturer)
  }

  // Apply bow type filter
  if (filters.value.bowType) {
    filtered = filtered.filter(chart => chart.bow_type === filters.value.bowType)
  }

  // Apply search filter
  if (filters.value.search) {
    const searchLower = filters.value.search.toLowerCase()
    filtered = filtered.filter(chart => 
      chart.manufacturer?.toLowerCase().includes(searchLower) ||
      chart.model?.toLowerCase().includes(searchLower) ||
      chart.chart_notes?.toLowerCase().includes(searchLower)
    )
  }

  return filtered
})

// Methods
const loadSpineCharts = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await api.get('/admin/spine-charts')
    manufacturerCharts.value = response.manufacturer_charts || []
    customCharts.value = response.custom_charts || []
  } catch (err) {
    error.value = 'Failed to load spine charts'
    console.error('Error loading spine charts:', err)
  } finally {
    loading.value = false
  }
}

const updateFilter = (filterKey: string, value: string) => {
  filters.value[filterKey] = value
}

const clearFilters = () => {
  filters.value = {
    chartType: '',
    manufacturer: '',
    bowType: '',
    search: ''
  }
}

const viewChart = (chart: SpineChart) => {
  selectedChart.value = chart
  showViewModal.value = true
}

const editChart = (chart: SpineChart) => {
  // Create a deep copy for editing
  editingChart.value = JSON.parse(JSON.stringify(chart))
  // Ensure spine_grid is an array
  if (!editingChart.value.spine_grid) {
    editingChart.value.spine_grid = []
  }
  showGridEditor.value = false
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  showGridEditor.value = false
  editingChart.value = null
}

const addSpineEntry = () => {
  if (!editingChart.value || editingChart.value.chart_type !== 'custom') return
  
  if (!editingChart.value.spine_grid) {
    editingChart.value.spine_grid = []
  }
  
  editingChart.value.spine_grid.push({
    draw_weight_range_lbs: '',
    arrow_length_in: 28,
    spine: '',
    arrow_size: ''
  })
  
  // Show grid editor when adding entry
  showGridEditor.value = true
}

const removeSpineEntry = (index: number) => {
  if (!editingChart.value || !editingChart.value.spine_grid) return
  
  confirmAction.value = {
    show: true,
    title: 'Remove Spine Entry',
    message: 'Are you sure you want to remove this spine grid entry?',
    itemName: `Entry ${index + 1}`,
    confirmText: 'Remove',
    loading: false,
    error: '',
    action: () => {
      editingChart.value!.spine_grid.splice(index, 1)
    }
  }
}

const sortSpineGrid = () => {
  if (!editingChart.value || !editingChart.value.spine_grid) return
  
  editingChart.value.spine_grid.sort((a, b) => {
    // Extract numeric value from draw weight range (e.g., "40-50" -> 40)
    const getDrawWeight = (entry) => {
      if (typeof entry.draw_weight_range_lbs === 'string') {
        const match = entry.draw_weight_range_lbs.match(/^(\d+)/)
        return match ? parseInt(match[1]) : 0
      }
      return typeof entry.draw_weight_range_lbs === 'number' ? entry.draw_weight_range_lbs : 0
    }
    
    return getDrawWeight(a) - getDrawWeight(b)
  })
}

const clearSpineGrid = () => {
  if (!editingChart.value) return
  
  confirmAction.value = {
    show: true,
    title: 'Clear All Spine Entries',
    message: 'Are you sure you want to clear all spine grid entries? This cannot be undone.',
    itemName: `${editingChart.value.spine_grid?.length || 0} entries`,
    confirmText: 'Clear All',
    loading: false,
    error: '',
    action: () => {
      editingChart.value!.spine_grid = []
    }
  }
}

// DataTables handler methods
const handleGridDataChange = (data: any[]) => {
  if (editingChart.value) {
    editingChart.value.spine_grid = data
  }
}

const handleRowAdd = (entry: any) => {
  showSpineEntryModal.value = true
  editingSpineEntry.value = null
  isEditingSpineEntry.value = false
}

const handleRowEdit = (index: number, entry: any) => {
  editingSpineEntry.value = { ...entry }
  editingSpineEntryIndex.value = index
  isEditingSpineEntry.value = true
  showSpineEntryModal.value = true
}

const handleRowDelete = (index: number) => {
  if (!editingChart.value || !editingChart.value.spine_grid) return
  
  confirmAction.value = {
    show: true,
    title: 'Delete Spine Entry',
    message: 'Are you sure you want to delete this spine grid entry?',
    itemName: `Entry ${index + 1}`,
    confirmText: 'Delete',
    loading: false,
    error: '',
    action: () => {
      if (editingChart.value?.spine_grid) {
        editingChart.value.spine_grid.splice(index, 1)
      }
    }
  }
}

// Spine entry modal handlers
const saveSpineEntry = (entry: any) => {
  if (!editingChart.value) return
  
  if (!editingChart.value.spine_grid) {
    editingChart.value.spine_grid = []
  }
  
  if (isEditingSpineEntry.value && editingSpineEntryIndex.value >= 0) {
    // Update existing entry
    editingChart.value.spine_grid[editingSpineEntryIndex.value] = entry
  } else {
    // Add new entry
    editingChart.value.spine_grid.push(entry)
  }
  
  // Close modal and reset state
  showSpineEntryModal.value = false
  editingSpineEntry.value = null
  editingSpineEntryIndex.value = -1
  isEditingSpineEntry.value = false
  
  // Refresh DataTables component if available
  nextTick(() => {
    const spineDataTable = document.querySelector('#spineDataTable')
    if (spineDataTable && (spineDataTable as any).refreshTable) {
      (spineDataTable as any).refreshTable()
    }
  })
}

const cancelSpineEntry = () => {
  showSpineEntryModal.value = false
  editingSpineEntry.value = null
  editingSpineEntryIndex.value = -1
  isEditingSpineEntry.value = false
}

const createOverride = async (chart: SpineChart) => {
  if (chart.chart_type !== 'manufacturer') return
  
  try {
    loading.value = true
    const response = await api.post(`/admin/spine-charts/manufacturer/${chart.id}/override`)
    
    // Reload charts to show new custom override
    await loadSpineCharts()
    
    // Show success message
    console.log('Override created:', response)
  } catch (err) {
    console.error('Error creating override:', err)
    error.value = 'Failed to create custom override chart'
  } finally {
    loading.value = false
  }
}

const saveChart = async () => {
  if (!editingChart.value) return
  
  savingChart.value = true
  try {
    // Handle both custom chart updates and system default changes
    if (editingChart.value.chart_type === 'custom') {
      await api.put(`/admin/spine-charts/custom/${editingChart.value.id}`, {
        manufacturer: editingChart.value.manufacturer,
        model: editingChart.value.model,
        bow_type: editingChart.value.bow_type,
        spine_system: editingChart.value.spine_system,
        chart_notes: editingChart.value.chart_notes,
        is_active: editingChart.value.is_active,
        spine_grid: editingChart.value.spine_grid || [],
        grid_definition: editingChart.value.grid_definition || {}
      })
    }
    
    // Handle system default setting (works for both manufacturer and custom charts)
    if (editingChart.value.is_system_default) {
      await api.post(`/admin/spine-charts/${editingChart.value.chart_type}/${editingChart.value.id}/set-default`)
    }
    
    // Reload charts to reflect changes
    await loadSpineCharts()
    closeEditModal()
  } catch (err) {
    console.error('Error saving chart:', err)
    error.value = 'Failed to save chart changes'
  } finally {
    savingChart.value = false
  }
}

const deleteChart = (chart: SpineChart) => {
  confirmAction.value = {
    show: true,
    title: 'Delete Spine Chart',
    message: 'Are you sure you want to delete this spine chart? This action cannot be undone.',
    itemName: `${chart.manufacturer} ${chart.model}`,
    confirmText: 'Delete',
    loading: false,
    error: '',
    action: async () => {
      try {
        confirmAction.value.loading = true
        confirmAction.value.error = ''
        
        if (chart.chart_type === 'custom') {
          await api.delete(`/admin/spine-charts/custom/${chart.id}`)
          await loadSpineCharts()
          confirmAction.value.show = false
        }
      } catch (err) {
        console.error('Error deleting chart:', err)
        confirmAction.value.error = 'Failed to delete chart'
      } finally {
        confirmAction.value.loading = false
      }
    }
  }
}

// Confirmation modal handlers
const executeConfirmedAction = async () => {
  if (confirmAction.value.action) {
    await confirmAction.value.action()
  }
}

const cancelConfirmedAction = () => {
  confirmAction.value.show = false
  confirmAction.value.error = ''
}

// Duplication functions
const duplicateChart = async (chart: SpineChart) => {
  const newName = prompt(`Enter name for duplicated chart:`, `${chart.manufacturer} ${chart.model} (Copy)`)
  
  if (!newName) return
  
  try {
    const response = await api.post(`/admin/spine-charts/${chart.chart_type}/${chart.id}/duplicate`, {
      name: newName
    })
    
    showToast(`Chart duplicated successfully: ${response.new_chart_name}`, 'success')
    
    // Refresh the charts list to show the new duplicate
    await loadSpineCharts()
  } catch (error) {
    console.error('Error duplicating chart:', error)
    showToast('Failed to duplicate chart', 'error')
  }
}

// Utility functions
const formatBowType = (bowType: string): string => {
  const typeMap: Record<string, string> = {
    'compound': 'Compound',
    'recurve': 'Recurve',
    'longbow': 'Longbow',
    'traditional': 'Traditional'
  }
  return typeMap[bowType] || bowType
}

const formatSpineSystem = (spineSystem: string): string => {
  const systemMap: Record<string, string> = {
    'standard_deflection': 'Standard',
    'wood_spine_range': 'Wood',
    'carbon': 'Carbon',
    'aluminum': 'Aluminum'
  }
  return systemMap[spineSystem] || spineSystem
}

// Lifecycle
onMounted(() => {
  loadSpineCharts()
})
</script>

<style scoped>
/* Custom scrollbar for table */
.overflow-x-auto::-webkit-scrollbar {
  height: 4px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  @apply bg-transparent;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}

/* Table styling */
table {
  @apply min-w-full;
}

th {
  @apply bg-gray-50 dark:bg-gray-700;
}

td {
  @apply bg-white dark:bg-gray-800;
}

/* Modal backdrop styling */
.fixed.inset-0 {
  backdrop-filter: blur(2px);
}
</style>