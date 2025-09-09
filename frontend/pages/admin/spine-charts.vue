<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-4">
          <!-- Navigation -->
          <div class="flex items-center space-x-4">
            <NuxtLink
              to="/admin"
              class="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
            >
              <i class="fas fa-arrow-left mr-2"></i>
              Back to Admin
            </NuxtLink>
            <div class="h-4 w-px bg-gray-300 dark:bg-gray-600"></div>
            <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Spine Chart Editor
            </h1>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center space-x-3">
            <CustomButton
              @click="showImportModal = true"
              variant="outlined"
              class="text-blue-600 border-blue-300 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-600"
            >
              <i class="fas fa-file-import mr-2"></i>
              Import Data
            </CustomButton>
            <CustomButton
              @click="exportAllCharts"
              variant="outlined"
              class="text-green-600 border-green-300 hover:bg-green-50 dark:text-green-400 dark:border-green-600"
            >
              <i class="fas fa-download mr-2"></i>
              Export All
            </CustomButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- Charts List View -->
      <div v-if="!editingChart" class="mb-6">
        <!-- Create New Chart Section -->
        <div class="mb-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            Create New Spine Chart
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <!-- Bow Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Bow Type
              </label>
              <select
                v-model="newChartBowType"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              >
                <option value="">Select Bow Type...</option>
                <option v-for="bowType in bowTypes" :key="bowType" :value="bowType">
                  {{ bowType.charAt(0).toUpperCase() + bowType.slice(1) }}
                </option>
              </select>
            </div>

            <!-- Manufacturer -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Manufacturer
              </label>
              <input
                v-model="newChartManufacturer"
                type="text"
                placeholder="Enter manufacturer name..."
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              />
            </div>

            <!-- Model -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Model (Optional)
              </label>
              <input
                v-model="newChartModel"
                type="text"
                placeholder="Enter model name..."
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              />
            </div>

            <!-- Create Button -->
            <div>
              <CustomButton
                @click="createNewChart"
                :disabled="!newChartBowType || !newChartManufacturer"
                variant="filled"
                class="bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 w-full"
              >
                <i class="fas fa-plus mr-2"></i>
                Create Chart
              </CustomButton>
            </div>
          </div>
        </div>

        <!-- Existing Charts Table -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div class="p-4 md:p-6 border-b border-gray-200 dark:border-gray-700">
            <div class="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
              <div>
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                  Existing Spine Charts
                </h2>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {{ allCharts.length }} spine charts available • 
                  {{ builtInCharts.length }} built-in, {{ customCharts.length }} custom
                </p>
              </div>
              
              <!-- Enhanced Chart type filter buttons with mobile support -->
              <div class="flex flex-wrap items-center gap-2">
                <button @click="filterCharts('all')" 
                        :class="chartFilter === 'all' ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'"
                        class="px-3 py-2 rounded-md text-sm font-medium transition-colors min-h-[36px] flex items-center"
                        aria-label="Show all spine charts">
                  All
                </button>
                <button @click="filterCharts('builtin')" 
                        :class="chartFilter === 'builtin' ? 'bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'"
                        class="px-3 py-2 rounded-md text-sm font-medium transition-colors min-h-[36px] flex items-center"
                        aria-label="Show built-in spine charts only">
                  <i class="fas fa-shield-alt mr-1"></i>
                  <span class="hidden sm:inline">Built-in</span>
                  <span class="sm:hidden">Built</span>
                  <span class="ml-1">({{ builtInCharts.length }})</span>
                </button>
                <button @click="filterCharts('custom')" 
                        :class="chartFilter === 'custom' ? 'bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'"
                        class="px-3 py-2 rounded-md text-sm font-medium transition-colors min-h-[36px] flex items-center"
                        aria-label="Show custom spine charts only">
                  <i class="fas fa-user-edit mr-1"></i>
                  <span class="hidden sm:inline">Custom</span>
                  <span class="sm:hidden">Mine</span>
                  <span class="ml-1">({{ customCharts.length }})</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Desktop table view -->
          <div class="hidden md:block overflow-x-auto">
            <table class="w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider w-20">
                    Type
                  </th>
                  <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Chart Details
                  </th>
                  <th class="px-3 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider w-24">
                    Status
                  </th>
                  <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider w-32">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="chart in filteredCharts" :key="chart.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-150">
                  <!-- Type Column -->
                  <td class="px-3 py-3 whitespace-nowrap text-sm">
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border"
                          :class="getBowTypeColor(chart.bow_type)">
                      {{ chart.bow_type.charAt(0).toUpperCase() }}
                    </span>
                  </td>
                  
                  <!-- Chart Details Column -->
                  <td class="px-3 py-3 text-sm">
                    <div class="space-y-1">
                      <div class="flex items-center space-x-2">
                        <span class="font-medium text-gray-900 dark:text-gray-100">{{ chart.manufacturer }}</span>
                        <span v-if="chart.is_builtin" 
                              class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200">
                          <i class="fas fa-shield-alt mr-1"></i>
                          Built-in
                        </span>
                        <span v-else 
                              class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-200">
                          <i class="fas fa-user-edit mr-1"></i>
                          Custom
                        </span>
                      </div>
                      <div class="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                        <span>{{ chart.model }}</span>
                        <span>•</span>
                        <span class="inline-flex items-center px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 font-medium">
                          {{ chart.entry_count }} entries
                        </span>
                      </div>
                    </div>
                  </td>
                  
                  <!-- Status Column -->
                  <td class="px-3 py-3 whitespace-nowrap text-center">
                    <div class="space-y-1">
                      <div v-if="chart.is_default" class="inline-flex items-center px-2 py-1 rounded-full bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs font-medium">
                        <i class="fas fa-check mr-1"></i>
                        Default
                      </div>
                      <CustomButton
                        v-else
                        @click="setChartAsDefault(chart)"
                        variant="outlined"
                        size="small"
                        class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 text-xs px-2 py-1"
                      >
                        Set Default
                      </CustomButton>
                    </div>
                  </td>
                  
                  <!-- Actions Column -->
                  <td class="px-3 py-3 whitespace-nowrap text-right">
                    <div class="flex items-center justify-end space-x-1">
                      <template v-if="chart.is_builtin">
                        <CustomButton
                          @click="viewChart(chart)"
                          variant="outlined"
                          size="small"
                          class="text-blue-600 border-blue-300 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-600"
                          :title="`View ${chart.manufacturer} spine chart`"
                          :aria-label="`View ${chart.manufacturer} ${chart.model} spine chart`"
                        >
                          <i class="fas fa-eye"></i>
                        </CustomButton>
                      </template>
                      <template v-else>
                        <CustomButton
                          @click="editChart(chart)"
                          variant="filled"
                          size="small"
                          class="bg-blue-600 text-white hover:bg-blue-700"
                          :title="`Edit ${chart.manufacturer} spine chart`"
                          :aria-label="`Edit ${chart.manufacturer} ${chart.model} spine chart`"
                        >
                          <i class="fas fa-edit"></i>
                        </CustomButton>
                        <CustomButton
                          @click="deleteChartFromList(chart)"
                          variant="outlined"
                          size="small"
                          class="text-red-600 border-red-300 hover:bg-red-50 dark:text-red-400 dark:border-red-600 ml-1"
                          :title="`Delete ${chart.manufacturer} spine chart`"
                          :aria-label="`Delete ${chart.manufacturer} ${chart.model} spine chart`"
                        >
                          <i class="fas fa-trash"></i>
                        </CustomButton>
                      </template>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Mobile card view -->
          <div class="md:hidden divide-y divide-gray-200 dark:divide-gray-700">
            <div v-for="chart in filteredCharts" :key="chart.id" 
                 class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-150">
              <div class="flex justify-between items-start mb-3">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2 mb-1">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border"
                          :class="getBowTypeColor(chart.bow_type)">
                      {{ chart.bow_type.charAt(0).toUpperCase() + chart.bow_type.slice(1) }}
                    </span>
                    <span v-if="chart.is_builtin" 
                          class="inline-flex items-center px-2 py-0.5 rounded-md bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 text-xs font-medium border border-amber-200 dark:border-amber-700">
                      <i class="fas fa-shield-alt mr-1"></i>
                      Built-in
                    </span>
                    <span v-else 
                          class="inline-flex items-center px-2 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-200 text-xs font-medium border border-emerald-200 dark:border-emerald-700">
                      <i class="fas fa-user-edit mr-1"></i>
                      Custom
                    </span>
                  </div>
                  <h3 class="font-medium text-gray-900 dark:text-gray-100 text-base truncate">{{ chart.manufacturer }}</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400 truncate">{{ chart.model }}</p>
                  <div class="flex items-center space-x-3 mt-2 text-xs text-gray-500 dark:text-gray-400">
                    <span class="inline-flex items-center px-2 py-1 rounded-md bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 font-medium">
                      {{ chart.entry_count }} entries
                    </span>
                    <span v-if="chart.is_default" class="inline-flex items-center px-2 py-1 rounded-md bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 font-medium">
                      <i class="fas fa-check mr-1"></i>
                      Default
                    </span>
                    <span class="text-xs">{{ formatDate(chart.updated_at) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- Mobile action buttons -->
              <div class="flex flex-col space-y-2">
                <template v-if="chart.is_builtin">
                  <CustomButton
                    @click="viewChart(chart)"
                    variant="outlined"
                    class="w-full justify-center text-blue-600 border-blue-300 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-600 min-h-[44px]"
                    :aria-label="`View ${chart.manufacturer} ${chart.model} spine chart`"
                  >
                    <i class="fas fa-eye mr-2"></i>
                    View Chart
                  </CustomButton>
                  <CustomButton
                    v-if="!chart.is_default"
                    @click="setChartAsDefault(chart)"
                    variant="outlined"
                    class="w-full justify-center text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 min-h-[44px]"
                    :aria-label="`Set ${chart.manufacturer} ${chart.model} as default chart`"
                  >
                    <i class="fas fa-star mr-2"></i>
                    Set as Default
                  </CustomButton>
                </template>
                <template v-else>
                  <div class="grid grid-cols-2 gap-2">
                    <CustomButton
                      @click="editChart(chart)"
                      variant="filled"
                      class="justify-center bg-blue-600 text-white hover:bg-blue-700 min-h-[44px]"
                      :aria-label="`Edit ${chart.manufacturer} ${chart.model} spine chart`"
                    >
                      <i class="fas fa-edit mr-1"></i>
                      Edit
                    </CustomButton>
                    <CustomButton
                      @click="deleteChartFromList(chart)"
                      variant="outlined"
                      class="justify-center text-red-600 border-red-300 hover:bg-red-50 dark:text-red-400 dark:border-red-600 min-h-[44px]"
                      :aria-label="`Delete ${chart.manufacturer} ${chart.model} spine chart`"
                    >
                      <i class="fas fa-trash mr-1"></i>
                      Delete
                    </CustomButton>
                  </div>
                  <CustomButton
                    v-if="!chart.is_default"
                    @click="setChartAsDefault(chart)"
                    variant="outlined"
                    class="w-full justify-center text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 min-h-[44px]"
                    :aria-label="`Set ${chart.manufacturer} ${chart.model} as default chart`"
                  >
                    <i class="fas fa-star mr-2"></i>
                    Set as Default
                  </CustomButton>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart Editor -->
      <div v-if="editingChart" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <!-- Enhanced Read-Only Alert Banner -->
        <div v-if="editingChart.is_builtin" 
             class="mx-6 mt-6 mb-0 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg"
             role="alert"
             aria-live="polite">
          <div class="flex items-start">
            <i class="fas fa-shield-alt text-amber-600 dark:text-amber-400 mt-0.5 mr-3 flex-shrink-0"></i>
            <div class="flex-1">
              <h3 class="text-sm font-medium text-amber-800 dark:text-amber-200">
                Protected Built-in Chart
              </h3>
              <p class="text-sm text-amber-700 dark:text-amber-300 mt-1">
                This chart cannot be modified directly. It's a protected reference from manufacturer specifications.
                Use the "Copy to Edit" button to create an editable version.
              </p>
              <div v-if="editingChart.provenance" class="mt-2">
                <span class="inline-flex items-center px-2 py-1 rounded-md bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-200 text-xs font-medium">
                  <i class="fas fa-file-pdf mr-1"></i>
                  {{ editingChart.provenance }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="mx-6 mt-6 mb-0 p-3 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg">
          <div class="flex items-center">
            <i class="fas fa-edit text-emerald-600 dark:text-emerald-400 mr-2"></i>
            <div>
              <span class="text-sm font-medium text-emerald-800 dark:text-emerald-200">Editable Custom Chart</span>
              <p class="text-xs text-emerald-700 dark:text-emerald-300 mt-0.5">
                You can modify this custom spine chart and save changes.
              </p>
            </div>
          </div>
        </div>

        <!-- Enhanced Editor Header -->
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center space-x-3">
                <CustomButton
                  @click="backToList"
                  variant="outlined"
                  size="small"
                  class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 min-h-[36px]"
                  aria-label="Return to spine charts list"
                >
                  <i class="fas fa-arrow-left mr-1"></i>
                  Back to List
                </CustomButton>
                <div>
                  <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {{ editingChart.bow_type.charAt(0).toUpperCase() + editingChart.bow_type.slice(1) }} - {{ editingChart.manufacturer }}
                    <span v-if="editingChart.model !== 'Standard'" class="text-gray-500 dark:text-gray-400"> • {{ editingChart.model }}</span>
                  </h2>
                  <div class="flex items-center space-x-3 mt-1">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border"
                          :class="getBowTypeColor(editingChart.bow_type)">
                      {{ editingChart.bow_type.charAt(0).toUpperCase() + editingChart.bow_type.slice(1) }}
                    </span>
                    <span class="text-sm text-gray-500 dark:text-gray-400">
                      {{ editingChart.data.length }} {{ editingChart.data.length === 1 ? 'entry' : 'entries' }}
                    </span>
                    <span class="text-sm text-gray-500 dark:text-gray-400">
                      Updated {{ formatDate(editingChart.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <!-- Built-in chart actions -->
              <template v-if="editingChart.is_builtin">
                <CustomButton
                  @click="duplicateCurrentChart"
                  variant="filled"
                  class="bg-green-600 text-white hover:bg-green-700 min-h-[40px]"
                  aria-label="Create editable copy of this chart"
                >
                  <i class="fas fa-copy mr-2"></i>
                  Copy to Edit
                </CustomButton>
              </template>
              <!-- User chart actions -->
              <template v-else>
                <div class="flex items-center space-x-2">
                  <span v-if="hasUnsavedChanges && !saving" 
                        class="inline-flex items-center px-2 py-1 rounded-md bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 text-xs font-medium">
                    <i class="fas fa-exclamation-circle mr-1"></i>
                    Unsaved changes
                  </span>
                  <CustomButton
                    @click="saveChart"
                    :disabled="!hasUnsavedChanges || saving"
                    variant="filled"
                    class="bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed min-h-[40px]"
                    :aria-label="hasUnsavedChanges ? 'Save changes to spine chart' : 'No changes to save'"
                  >
                    <i v-if="saving" class="fas fa-spinner fa-spin mr-2"></i>
                    <i v-else class="fas fa-save mr-2"></i>
                    {{ saving ? 'Saving...' : hasUnsavedChanges ? 'Save Changes' : 'No Changes' }}
                  </CustomButton>
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- DataTable -->
        <div class="p-6">
          <SpineChartDataTable
            :data="editingChart.data"
            :loading="loading"
            :error="error"
            :readonly="editingChart.is_builtin || false"
            :manufacturer="editingChart.manufacturer"
            :model="editingChart.model"
            :bow-type="editingChart.bow_type"
            @data-change="handleDataChange"
            @row-add="handleRowAdd"
            @row-edit="handleRowEdit"
            @row-delete="handleRowDelete"
          />
        </div>
      </div>

    </div>

    <!-- Modals -->
    <SpineEntryEditModal
      :show="showEditModal"
      :entry="editingEntry"
      :is-edit="isEditMode"
      @save="handleEntrySave"
      @cancel="closeEditModal"
    />

    <ImportDataModal
      :show="showImportModal"
      :bow-type="editingChart?.bow_type || ''"
      :manufacturer="editingChart?.manufacturer || ''"
      :existing-data="editingChart?.data || []"
      @import="handleImport"
      @cancel="showImportModal = false"
    />
    
    <!-- Enhanced notification system -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform scale-95 opacity-0 translate-y-2"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-95 opacity-0 translate-y-2"
    >
      <div v-if="notification.show" 
           class="fixed top-4 right-4 z-50 max-w-sm w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg border border-gray-200 dark:border-gray-700 p-4"
           role="alert"
           aria-live="assertive"
           aria-atomic="true">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <i :class="{
              'fas fa-check-circle text-green-500': notification.type === 'success',
              'fas fa-exclamation-circle text-red-500': notification.type === 'error',
              'fas fa-exclamation-triangle text-yellow-500': notification.type === 'warning'
            }"></i>
          </div>
          <div class="ml-3 flex-1">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ notification.message }}
            </p>
          </div>
          <div class="ml-4 flex-shrink-0">
            <button @click="hideNotification"
                    class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                    aria-label="Dismiss notification">
              <i class="fas fa-times text-sm"></i>
            </button>
          </div>
        </div>
        
        <!-- Auto-dismiss progress bar -->
        <div v-if="notification.show" 
             class="absolute bottom-0 left-0 h-1 bg-gray-200 dark:bg-gray-600 w-full rounded-b-lg overflow-hidden">
          <div class="h-full transition-all duration-75 ease-linear"
               :class="{
                 'bg-green-500': notification.type === 'success',
                 'bg-red-500': notification.type === 'error',
                 'bg-yellow-500': notification.type === 'warning'
               }"
               :style="{ width: notificationProgress + '%' }"></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
// Component imports
import CustomButton from '@/components/CustomButton.vue'
import SpineChartDataTable from '~/components/admin/SpineChartDataTable.vue'
import SpineEntryEditModal from '~/components/admin/SpineEntryEditModal.vue'
import ImportDataModal from '~/components/admin/ImportDataModal.vue'

interface SpineGridEntry {
  draw_weight_range_lbs: string | number
  arrow_length_in: number
  spine: string
  arrow_size?: string
  speed?: number
}

interface SpineChart {
  bow_type: string
  manufacturer: string
  data: SpineGridEntry[]
  updated_at: string
}

// Meta
definePageMeta({
  middleware: ['auth-check', 'admin']
})

// SEO
useSeoMeta({
  title: 'Spine Chart Editor - Admin',
  description: 'Full-page spine chart editor with import/export functionality'
})

// API - initialized lazily to avoid Pinia issues
let api: ReturnType<typeof useApi>
const getApi = () => {
  if (!api) { api = useApi() }
  return api
}

// State
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const hasUnsavedChanges = ref(false)

// Chart data
const bowTypes = ref(['recurve', 'compound', 'longbow'])
const allCharts = ref<any[]>([])
const editingChart = ref<SpineChart | null>(null)

// New chart creation
const newChartBowType = ref('')
const newChartManufacturer = ref('')
const newChartModel = ref('')

// Modals
const showEditModal = ref(false)
const showImportModal = ref(false)
const editingEntry = ref<SpineGridEntry | null>(null)
const editingIndex = ref(-1)
const isEditMode = ref(false)

// Methods
const loadAllCharts = async () => {
  try {
    loading.value = true
    const api = getApi()
    const response = await api.get('/admin/spine-charts/list')
    allCharts.value = response.charts || []
    
    // Fix backend issue: Override is_builtin for charts that are clearly custom
    allCharts.value.forEach(chart => {
      // If chart has "Copy" in manufacturer or model is "Custom Chart", it should be custom
      if ((chart.manufacturer && chart.manufacturer.includes('Copy')) || 
          (chart.model && chart.model.includes('Custom Chart'))) {
        if (chart.is_builtin) {
          console.warn(`🔧 Fixing backend issue: Chart "${chart.manufacturer} - ${chart.model}" marked as builtin but appears to be custom`)
          chart.is_builtin = false
        }
      }
    })
    
    // Debug logging for chart list
    console.log('📊 Loaded chart list:', allCharts.value)
    const copyCharts = allCharts.value.filter(chart => chart.manufacturer && chart.manufacturer.includes('Copy'))
    console.log('📋 Copy charts found:', copyCharts)
    copyCharts.forEach(chart => {
      console.log(`📊 Chart: ${chart.manufacturer} - is_builtin: ${chart.is_builtin}`)
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load spine charts'
    console.error('Error loading charts:', err)
  } finally {
    loading.value = false
  }
}

const editChart = async (chart: any) => {
  console.log('🔧 editChart called with chart:', chart)
  console.log('📊 Chart is_builtin from list:', chart.is_builtin)
  try {
    loading.value = true
    const api = getApi()
    const apiUrl = `/admin/spine-charts?bow_type=${encodeURIComponent(chart.bow_type)}&manufacturer=${encodeURIComponent(chart.manufacturer)}`
    console.log('🌐 Making API request to:', apiUrl)
    const response = await api.get(apiUrl)
    console.log('📡 API Response:', response)
    
    // Find the specific chart in the response arrays (like viewChart does)
    let foundChart = null
    
    // Check custom charts first
    if (response.custom_charts) {
      foundChart = response.custom_charts.find((c: any) => 
        c.id === chart.id && 
        c.bow_type === chart.bow_type && 
        c.manufacturer === chart.manufacturer
      )
      console.log('🔍 Searched custom_charts, found:', foundChart)
    }
    
    // Check manufacturer charts if not found in custom charts
    if (!foundChart && response.manufacturer_charts) {
      foundChart = response.manufacturer_charts.find((c: any) => 
        c.id === chart.id && 
        c.bow_type === chart.bow_type && 
        c.manufacturer === chart.manufacturer
      )
      console.log('🔍 Searched manufacturer_charts, found:', foundChart)
    }
    
    // Fallback to legacy response.chart format
    if (!foundChart && response.chart) {
      foundChart = response.chart
      console.log('🔍 Using legacy response.chart format')
    }
    
    if (foundChart) {
      editingChart.value = {
        id: chart.id,
        bow_type: chart.bow_type,
        manufacturer: chart.manufacturer,
        model: chart.model,
        data: foundChart.spine_grid || foundChart.data || [],
        updated_at: foundChart.updated_at || foundChart.created_at || new Date().toISOString(),
        is_builtin: chart.is_builtin, // Use the chart list's determination
        provenance: chart.provenance || foundChart.provenance || null,
        grid_definition: foundChart.grid_definition || {},
        chart_notes: foundChart.chart_notes || ''
      }
      hasUnsavedChanges.value = false
      console.log('✅ editingChart set:', editingChart.value)
    } else {
      console.warn('❌ Chart not found in API response')
      console.log('📊 Looking for chart with id:', chart.id, 'manufacturer:', chart.manufacturer)
      console.log('📊 Full API response structure:', response)
      error.value = 'Chart not found in API response'
      showNotification('Chart not found', 'error')
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load spine chart'
    showNotification('Failed to load chart for editing', 'error')
  } finally {
    loading.value = false
  }
}

const viewChart = async (chart: any) => {
  console.log('🔍 viewChart function called with chart:', chart)
  try {
    loading.value = true
    const api = getApi()
    console.log('📡 Making API request to get chart data...')
    const response = await api.get(`/admin/spine-charts?bow_type=${chart.bow_type}&manufacturer=${chart.manufacturer}`)
    
    // Find the specific chart in the response arrays
    let foundChart = null
    
    // Check custom charts first
    if (response.custom_charts) {
      foundChart = response.custom_charts.find((c: any) => 
        c.id === chart.id && 
        c.bow_type === chart.bow_type && 
        c.manufacturer === chart.manufacturer
      )
    }
    
    // Check manufacturer charts if not found in custom charts
    if (!foundChart && response.manufacturer_charts) {
      foundChart = response.manufacturer_charts.find((c: any) => 
        c.id === chart.id && 
        c.bow_type === chart.bow_type && 
        c.manufacturer === chart.manufacturer
      )
    }
    
    if (foundChart) {
      editingChart.value = {
        id: foundChart.id,
        bow_type: foundChart.bow_type,
        manufacturer: foundChart.manufacturer,
        model: foundChart.model,
        data: foundChart.spine_grid || [],  // The spine data is in spine_grid
        updated_at: foundChart.created_at || new Date().toISOString(),
        is_builtin: chart.is_builtin,  // Use the chart list's determination of built-in status
        provenance: foundChart.provenance || 'Built-in chart',
        grid_definition: foundChart.grid_definition || {},
        chart_notes: foundChart.chart_notes || ''
      }
      hasUnsavedChanges.value = false
      console.log('✅ editingChart set successfully:', editingChart.value)
      console.log('🎯 UI should now show the editor interface')
    } else {
      console.warn('❌ Could not find chart with id', chart.id, 'in API response')
      error.value = 'Chart not found in API response'
      showNotification('Chart not found', 'error')
    }
    console.log('📊 Complete API response:', response)
  } catch (err) {
    console.error('❌ Error in viewChart:', err)
    error.value = err instanceof Error ? err.message : 'Failed to load spine chart'
    showNotification('Failed to load chart for viewing', 'error')
  } finally {
    loading.value = false
    console.log('✅ viewChart function completed, loading set to false')
  }
}

const backToList = () => {
  if (hasUnsavedChanges.value) {
    const confirmed = confirm('You have unsaved changes. Are you sure you want to go back?')
    if (!confirmed) return
  }
  editingChart.value = null
  hasUnsavedChanges.value = false
  loadAllCharts() // Refresh the list
}

const createNewChart = () => {
  if (!newChartBowType.value || !newChartManufacturer.value) return
  
  editingChart.value = {
    id: null, // New chart
    bow_type: newChartBowType.value,
    manufacturer: newChartManufacturer.value,
    model: newChartModel.value || 'Standard',
    data: [],
    updated_at: new Date().toISOString()
  }
  hasUnsavedChanges.value = true
  
  // Clear the form
  newChartBowType.value = ''
  newChartManufacturer.value = ''
  newChartModel.value = ''
}

const saveChart = async () => {
  if (!editingChart.value) return
  
  try {
    saving.value = true
    const api = getApi()
    
    await api.post('/admin/spine-charts', {
      bow_type: editingChart.value.bow_type,
      manufacturer: editingChart.value.manufacturer,
      model: editingChart.value.model,
      data: editingChart.value.data
    })
    
    hasUnsavedChanges.value = false
    showNotification('Chart saved successfully', 'success')
    
    // Update the chart's updated_at timestamp
    editingChart.value.updated_at = new Date().toISOString()
    
    // Refresh the chart list to ensure UI consistency
    await loadAllCharts()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save chart'
    showNotification('Failed to save chart', 'error')
  } finally {
    saving.value = false
  }
}

const duplicateCurrentChart = async () => {
  if (!editingChart.value) return
  
  const newManufacturer = prompt('Enter manufacturer name for the duplicated chart:', `${editingChart.value.manufacturer} Copy`)
  if (!newManufacturer) return
  
  // Create a new editable chart with the same data
  editingChart.value = {
    id: null, // New chart
    bow_type: editingChart.value.bow_type,
    manufacturer: newManufacturer,
    model: editingChart.value.model,
    data: [...editingChart.value.data], // Copy the data
    updated_at: new Date().toISOString(),
    is_builtin: false, // This is now a user-created chart
    provenance: null
  }
  hasUnsavedChanges.value = true
  showNotification('Chart copied for editing. Remember to save your changes.', 'success')
}

const duplicateChartFromList = async (chart: any) => {
  const newManufacturer = prompt('Enter manufacturer name for the duplicated chart:', `${chart.manufacturer} Copy`)
  if (!newManufacturer) return
  
  try {
    loading.value = true
    const api = getApi()
    const response = await api.get(`/admin/spine-charts?bow_type=${chart.bow_type}&manufacturer=${chart.manufacturer}`)
    
    if (response.chart) {
      editingChart.value = {
        id: null, // New chart
        bow_type: chart.bow_type,
        manufacturer: newManufacturer,
        model: chart.model,
        data: response.chart.data || [],
        updated_at: new Date().toISOString(),
        is_builtin: false, // This is now a user-created chart
        provenance: null
      }
      hasUnsavedChanges.value = true
    }
  } catch (err) {
    showNotification('Failed to duplicate chart', 'error')
  } finally {
    loading.value = false
  }
}

const deleteChartFromList = async (chart: any) => {
  const confirmed = confirm(`Are you sure you want to delete the spine chart for ${chart.bow_type} - ${chart.manufacturer}?`)
  if (!confirmed) return
  
  try {
    const api = getApi()
    await api.delete(`/admin/spine-charts?bow_type=${chart.bow_type}&manufacturer=${chart.manufacturer}`)
    
    showNotification('Chart deleted successfully', 'success')
    loadAllCharts() // Refresh the list
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to delete chart'
    showNotification('Failed to delete chart', 'error')
  }
}

const setChartAsDefault = async (chart: any) => {
  try {
    const api = getApi()
    await api.put('/admin/spine-charts/set-default', {
      chart_id: chart.id
    })
    
    showNotification(`Set as default for ${chart.bow_type} bows`, 'success')
    loadAllCharts() // Refresh to show updated default status
  } catch (err) {
    showNotification('Failed to set chart as default', 'error')
  }
}

const exportAllCharts = async () => {
  try {
    const api = getApi()
    const response = await api.get('/admin/spine-charts/export')
    
    const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', 'all-spine-charts.json')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    showNotification('All charts exported successfully', 'success')
  } catch (err) {
    showNotification('Failed to export charts', 'error')
  }
}

// DataTable event handlers
const handleDataChange = (data: SpineGridEntry[]) => {
  if (editingChart.value) {
    editingChart.value.data = data
    hasUnsavedChanges.value = true
  }
}

const handleRowAdd = (entry: SpineGridEntry) => {
  editingEntry.value = entry
  editingIndex.value = -1
  isEditMode.value = false
  showEditModal.value = true
}

const handleRowEdit = (index: number, entry: SpineGridEntry) => {
  // Handle inline editing by directly updating the chart data
  if (!editingChart.value) return
  
  console.log('🔧 Inline edit: Updating entry at index', index, 'with data:', entry)
  editingChart.value.data[index] = { ...entry }
  hasUnsavedChanges.value = true
  
  // Show success notification for inline edit
  showNotification(`Entry updated successfully`, 'success')
}

const handleRowDelete = (index: number) => {
  if (!editingChart.value) return
  
  const confirmed = confirm('Are you sure you want to delete this entry?')
  if (confirmed) {
    editingChart.value.data.splice(index, 1)
    hasUnsavedChanges.value = true
  }
}

const handleEntrySave = (entry: SpineGridEntry) => {
  if (!editingChart.value) return
  
  if (isEditMode.value && editingIndex.value >= 0) {
    // Edit existing entry
    editingChart.value.data[editingIndex.value] = { ...entry }
  } else {
    // Add new entry
    editingChart.value.data.push({ ...entry })
  }
  
  hasUnsavedChanges.value = true
  closeEditModal()
}

const closeEditModal = () => {
  showEditModal.value = false
  editingEntry.value = null
  editingIndex.value = -1
  isEditMode.value = false
}

const handleImport = (importedData: SpineGridEntry[]) => {
  if (!editingChart.value) return
  
  editingChart.value.data = [...editingChart.value.data, ...importedData]
  hasUnsavedChanges.value = true
  showImportModal.value = false
  showNotification(`Imported ${importedData.length} entries successfully`, 'success')
}

// Utilities
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

// Notifications
const notification = ref({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error' | 'warning'
})

// Enhanced notification system with progress bar
const notificationProgress = ref(100)
const notificationTimer = ref<NodeJS.Timeout | null>(null)

const showNotification = (message: string, type: 'success' | 'error' | 'warning' = 'success') => {
  // Clear existing timer
  if (notificationTimer.value) {
    clearTimeout(notificationTimer.value)
  }
  
  notification.value = { show: true, message, type }
  notificationProgress.value = 100
  
  // Animate progress bar
  const startTime = Date.now()
  const duration = 5000
  
  const updateProgress = () => {
    const elapsed = Date.now() - startTime
    const remaining = Math.max(0, duration - elapsed)
    notificationProgress.value = (remaining / duration) * 100
    
    if (remaining > 0 && notification.value.show) {
      requestAnimationFrame(updateProgress)
    } else if (notification.value.show) {
      hideNotification()
    }
  }
  
  requestAnimationFrame(updateProgress)
  
  // Fallback timeout
  notificationTimer.value = setTimeout(() => {
    if (notification.value.show) {
      hideNotification()
    }
  }, duration + 100)
}

const hideNotification = () => {
  notification.value.show = false
  notificationProgress.value = 100
  if (notificationTimer.value) {
    clearTimeout(notificationTimer.value)
    notificationTimer.value = null
  }
}

// Chart filtering
const chartFilter = ref('all')

const filteredCharts = computed(() => {
  switch (chartFilter.value) {
    case 'builtin':
      return allCharts.value.filter(chart => chart.is_builtin)
    case 'custom':
      return allCharts.value.filter(chart => !chart.is_builtin)
    default:
      return allCharts.value
  }
})

const builtInCharts = computed(() => allCharts.value.filter(chart => chart.is_builtin))
const customCharts = computed(() => allCharts.value.filter(chart => !chart.is_builtin))

const filterCharts = (type: string) => {
  chartFilter.value = type
}

// Utilities with enhanced WCAG 2.1 AA compliant color schemes
const getBowTypeColor = (bowType: string) => {
  switch (bowType.toLowerCase()) {
    case 'recurve':
      return 'bg-blue-100 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100 border-blue-200 dark:border-blue-800'
    case 'compound':
      return 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-900 dark:text-emerald-100 border-emerald-200 dark:border-emerald-800'
    case 'longbow':
      return 'bg-purple-100 dark:bg-purple-900/30 text-purple-900 dark:text-purple-100 border-purple-200 dark:border-purple-800'
    default:
      return 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-gray-200 dark:border-gray-600'
  }
}

// Cleanup on unmount
onUnmounted(() => {
  if (notificationTimer.value) {
    clearTimeout(notificationTimer.value)
  }
})

// Lifecycle
onMounted(() => {
  loadAllCharts()
})

// Watch for unsaved changes before navigation
onBeforeRouteLeave((to, from) => {
  if (hasUnsavedChanges.value) {
    const confirmed = confirm('You have unsaved changes. Are you sure you want to leave?')
    if (!confirmed) {
      return false
    }
  }
})
</script>

<style scoped>
/* Page-specific styling */
.min-h-screen {
  min-height: 100vh;
}

/* Notification animations */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}
</style>