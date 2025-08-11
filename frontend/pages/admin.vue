<template>
  <div>
    <!-- Notification Toast -->
    <div v-if="notification.show" class="fixed top-4 right-4 z-50 transition-all duration-300">
      <div 
        :class="[
          'p-4 rounded-lg shadow-lg max-w-sm',
          notification.type === 'success' ? 'bg-green-500 text-white' : '',
          notification.type === 'error' ? 'bg-red-500 text-white' : '',
          notification.type === 'warning' ? 'bg-yellow-500 text-black' : ''
        ]"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <i v-if="notification.type === 'success'" class="fas fa-check-circle mr-2"></i>
            <i v-if="notification.type === 'error'" class="fas fa-exclamation-circle mr-2"></i>
            <i v-if="notification.type === 'warning'" class="fas fa-exclamation-triangle mr-2"></i>
            <span class="text-sm">{{ notification.message }}</span>
          </div>
          <button @click="hideNotification" class="ml-4 opacity-70 hover:opacity-100">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Admin Notice Banner -->
    <div class="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-shield-alt text-red-600 dark:text-red-400 mr-3"></i>
        <div>
          <h4 class="text-sm font-medium text-red-800 dark:text-red-200">Admin Panel</h4>
          <p class="text-xs text-red-700 dark:text-red-300 mt-1">
            Restricted access. Only authorized administrators can manage beta users.
          </p>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Admin Panel</h1>
      <p class="text-gray-600 dark:text-gray-300">Manage beta access, users, and arrow database</p>
    </div>

    <!-- Admin Navigation Tabs -->
    <div v-if="isAdmin" class="mb-6">
      <nav class="flex space-x-8 border-b border-gray-200 dark:border-gray-700">
        <button
          @click="activeTab = 'users'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'users' 
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          <i class="fas fa-users mr-2"></i>
          Users
        </button>
        <button
          @click="activeTab = 'arrows'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'arrows' 
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          <i class="fas fa-bow-arrow mr-2"></i>
          Arrows
        </button>
        <button
          @click="activeTab = 'manufacturers'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'manufacturers' 
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          <i class="fas fa-industry mr-2"></i>
          Manufacturers
        </button>
        <button
          @click="activeTab = 'datatools'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'datatools' 
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          <i class="fas fa-tools mr-2"></i>
          Data Tools
        </button>
        <button
          @click="activeTab = 'backups'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'backups' 
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          <i class="fas fa-database mr-2"></i>
          Backups
        </button>
        <button
          @click="activeTab = 'system'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'system' 
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          <i class="fas fa-server mr-2"></i>
          System
        </button>
      </nav>
    </div>

    <!-- Loading State -->
    <div v-if="isCheckingAdmin" class="text-center py-12">
      <i class="fas fa-spinner fa-spin text-4xl text-indigo-600 mb-4"></i>
      <h2 class="text-xl font-medium text-gray-900 dark:text-gray-100 mb-2">Checking Access...</h2>
      <p class="text-gray-600 dark:text-gray-400">Verifying your admin privileges</p>
    </div>

    <!-- Admin Dashboard -->
    <div v-else-if="!isCheckingAdmin && isAdmin" class="space-y-6">
      <!-- Users Tab -->
      <div v-if="activeTab === 'users'">
        <!-- User Statistics -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-chart-bar mr-2 text-indigo-600"></i>
              User Statistics
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ userStats.total || 0 }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Total Users</div>
              </div>
              <div class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ userStats.active || 0 }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Active Users</div>
              </div>
              <div class="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ userStats.pending || 0 }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Pending Access</div>
              </div>
            </div>
          </div>
        </md-elevated-card>

        <!-- User Management -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                <i class="fas fa-users mr-2 text-indigo-600"></i>
                Beta Users
              </h2>
              <CustomButton
                @click="showInviteModal = true"
                variant="filled"
                class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
              >
                <i class="fas fa-user-plus mr-2"></i>
                Invite User
              </CustomButton>
            </div>

            <!-- Users Table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">User</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Email</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Admin</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Created</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <img class="h-10 w-10 rounded-full" :src="user.picture || '/default-avatar.png'" :alt="user.name">
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ user.name || 'Unnamed User' }}</div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">ID: {{ user.id }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{{ user.email }}</td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="getStatusBadgeClass(user.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ formatStatus(user.status) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="user.is_admin ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ user.is_admin ? 'Admin' : 'User' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {{ formatDate(user.last_login) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <CustomButton
                      @click="toggleAdminStatus(user)"
                      variant="outlined"
                      size="small"
                      :class="user.is_admin ? 'text-orange-600 border-orange-600' : 'text-purple-600 border-purple-600'"
                    >
                      {{ user.is_admin ? 'Remove Admin' : 'Make Admin' }}
                    </CustomButton>
                    <CustomButton
                      @click="toggleUserStatus(user)"
                      variant="outlined"
                      size="small"
                      :class="user.status === 'active' ? 'text-red-600 border-red-600' : 'text-green-600 border-green-600'"
                    >
                      {{ user.status === 'active' ? 'Suspend' : 'Activate' }}
                    </CustomButton>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Empty State -->
          <div v-if="users.length === 0" class="text-center py-8">
            <i class="fas fa-users text-4xl text-gray-400 mb-4"></i>
            <p class="text-gray-500 dark:text-gray-400">No users found</p>
          </div>
          </div>
        </md-elevated-card>
      </div>

      <!-- Arrows Tab -->
      <div v-if="activeTab === 'arrows'">
        <!-- Arrow Statistics -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-chart-bar mr-2 text-indigo-600"></i>
              Arrow Database Statistics
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ arrowStats.total || 0 }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Total Arrows</div>
              </div>
              <div class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ arrowStats.manufacturers || 0 }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Manufacturers</div>
              </div>
              <div class="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ arrowStats.spines || 0 }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Total Spines</div>
              </div>
              <div class="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ arrowStats.withImages || 0 }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">With Images</div>
              </div>
            </div>
          </div>
        </md-elevated-card>

        <!-- Arrow Management -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <AdminArrowsTable
              ref="arrowsTableRef"
              @edit="openEditModal"
              @create="openCreateModal"
              @delete="confirmDeleteArrow"
            />
          </div>
        </md-elevated-card>
      </div>

      <!-- Manufacturers Tab -->
      <div v-if="activeTab === 'manufacturers'">
        <!-- Manufacturer Management -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <AdminManufacturersTable
              ref="manufacturersTableRef"
              @refresh-stats="loadManufacturerStats"
              @show-notification="showNotification"
            />
          </div>
        </md-elevated-card>
      </div>
      
      <!-- Data Tools Tab -->
      <div v-if="activeTab === 'datatools'">
        <!-- Batch Fill Missing Data -->
        <md-elevated-card class="light-surface light-elevation mb-6">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  <i class="fas fa-fill-drip mr-2 text-blue-600"></i>
                  Batch Fill Missing Length Data
                </h3>
                <p class="text-gray-600 dark:text-gray-400 text-sm">
                  Fill missing length data for arrows using a reference arrow from the same manufacturer
                </p>
              </div>
            </div>
            
            <!-- Manufacturer Selection -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select Manufacturer
                </label>
                <select 
                  v-model="batchFill.selectedManufacturer" 
                  @change="loadManufacturerLengthStats"
                  class="form-select w-full"
                >
                  <option value="">Choose a manufacturer...</option>
                  <option v-for="manufacturer in manufacturers" :key="manufacturer.name" :value="manufacturer.name">
                    {{ manufacturer.name }} ({{ manufacturer.arrow_count }} arrows)
                  </option>
                </select>
              </div>
              
              <div v-if="batchFill.lengthStats">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Length Data Statistics
                </label>
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 text-sm">
                  <div class="flex justify-between">
                    <span>Complete:</span>
                    <span class="font-medium text-green-600">{{ batchFill.lengthStats.statistics.fully_complete }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Partial:</span>
                    <span class="font-medium text-yellow-600">{{ batchFill.lengthStats.statistics.partially_complete }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Missing:</span>
                    <span class="font-medium text-red-600">{{ batchFill.lengthStats.statistics.completely_missing }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Reference Arrow Selection -->
            <div v-if="batchFill.lengthStats && batchFill.lengthStats.reference_candidates.length > 0" class="mb-6">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Reference Arrow (Complete Length Data)
              </label>
              <select v-model="batchFill.selectedReferenceArrow" class="form-select w-full">
                <option value="">Choose reference arrow...</option>
                <option 
                  v-for="arrow in batchFill.lengthStats.reference_candidates" 
                  :key="arrow.id" 
                  :value="arrow.id"
                >
                  {{ arrow.model_name }} ({{ arrow.complete_lengths }}/{{ arrow.total_spines }} spines complete)
                </option>
              </select>
            </div>
            
            <!-- No Reference Arrows Warning -->
            <div v-else-if="batchFill.lengthStats && batchFill.lengthStats.reference_candidates.length === 0" class="mb-6">
              <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <div class="flex items-center">
                  <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 mr-3"></i>
                  <div>
                    <h4 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">No Complete Reference Arrows</h4>
                    <p class="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                      No arrows from {{ batchFill.selectedManufacturer }} have complete length data to use as reference.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Preview Section -->
            <div v-if="batchFill.selectedReferenceArrow" class="mb-6">
              <div class="flex gap-4">
                <CustomButton
                  @click="previewBatchFill"
                  :disabled="batchFill.isLoading"
                  variant="outlined"
                  class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20"
                >
                  <i class="fas fa-eye mr-2"></i>
                  {{ batchFill.isLoading ? 'Loading...' : 'Preview Changes' }}
                </CustomButton>
                
                <CustomButton
                  v-if="batchFill.previewData"
                  @click="executeBatchFill"
                  :disabled="batchFill.isExecuting"
                  variant="filled"
                  class="bg-green-600 text-white hover:bg-green-700"
                >
                  <i class="fas fa-play mr-2"></i>
                  {{ batchFill.isExecuting ? 'Executing...' : 'Execute Batch Fill' }}
                </CustomButton>
              </div>
            </div>
            
            <!-- Preview Results -->
            <div v-if="batchFill.previewData" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Batch Fill Preview</h4>
                <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <p><strong>Reference:</strong> {{ batchFill.previewData.reference_arrow.model_name }}</p>
                  <p><strong>Manufacturer:</strong> {{ batchFill.previewData.summary.manufacturer }}</p>
                  <p><strong>Arrows to update:</strong> {{ batchFill.previewData.summary.arrows_to_update }}</p>
                  <p><strong>Spine specifications to fill:</strong> {{ batchFill.previewData.summary.total_spine_updates }}</p>
                </div>
              </div>
              
              <div class="max-h-64 overflow-y-auto">
                <div v-for="arrow in batchFill.previewData.target_arrows" :key="arrow.arrow_id" class="p-3 border-b border-gray-100 dark:border-gray-700 last:border-b-0">
                  <div class="flex justify-between items-start">
                    <div>
                      <div class="font-medium text-gray-900 dark:text-gray-100">{{ arrow.model_name }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">
                        {{ arrow.fillable_count }} of {{ arrow.missing_lengths }} missing lengths can be filled
                      </div>
                    </div>
                    <div class="text-xs text-gray-600 dark:text-gray-400">
                      Spines: {{ arrow.fillable_spines.map(s => s.spine).join(', ') }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </md-elevated-card>
        
        <!-- Length Data Overview -->
        <md-elevated-card class="light-surface light-elevation" v-if="batchFill.lengthStats">
          <div class="p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-chart-bar mr-2 text-indigo-600"></i>
              {{ batchFill.selectedManufacturer }} - Length Data Overview
            </h3>
            
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Arrow Model
                    </th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Completion
                    </th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Progress
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="arrow in batchFill.lengthStats.arrows" :key="arrow.id">
                    <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ arrow.model_name }}
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {{ arrow.complete_lengths }}/{{ arrow.total_spines }} spines
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-16 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                          <div 
                            :class="[
                              'h-2 rounded-full',
                              arrow.completion_percentage === 100 ? 'bg-green-500' :
                              arrow.completion_percentage > 0 ? 'bg-yellow-500' : 'bg-red-500'
                            ]"
                            :style="{ width: arrow.completion_percentage + '%' }"
                          ></div>
                        </div>
                        <span class="text-xs text-gray-500 dark:text-gray-400">{{ arrow.completion_percentage }}%</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </md-elevated-card>
        
        <!-- URL Scraping Tool -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  <i class="fas fa-globe mr-2 text-green-600"></i>
                  URL Scraper & Database Updater
                </h3>
                <p class="text-gray-600 dark:text-gray-400 text-sm">
                  Extract arrow data from specific URLs or update existing arrows with missing spine specifications
                </p>
              </div>
            </div>
            
            <!-- Manufacturer Selection -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Manufacturer to Scrape
                </label>
                <select 
                  v-model="scraping.manufacturer" 
                  class="form-select w-full"
                  :disabled="scraping.isLoading"
                >
                  <option value="">Choose a manufacturer...</option>
                  <option value="easton">Easton Archery</option>
                  <option value="goldtip">Gold Tip</option>
                  <option value="victory">Victory Archery</option>
                  <option value="carbonexpress">Carbon Express</option>
                  <option value="nijora">Nijora Archery</option>
                  <option value="aurel">Aurel Archery</option>
                  <option value="bigarchery">BigArchery/Cross-X</option>
                  <option value="fivics">Fivics</option>
                  <option value="pandarus">Pandarus Archery</option>
                  <option value="skylon">Skylon Archery</option>
                </select>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Select from configured manufacturers with known URL patterns
                </p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Specific Arrow URL (Optional)
                </label>
                <input 
                  v-model="scraping.url" 
                  type="url"
                  placeholder="https://eastonarchery.com/arrows_/x10-parallel-pro/"
                  class="form-input w-full"
                  :disabled="scraping.isLoading"
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Direct link to arrow product page - will extract spine specs and update existing arrows
                </p>
              </div>
            </div>
            
            <!-- Scraping Controls -->
            <div class="flex gap-4 mb-6">
              <CustomButton
                @click="startScraping"
                :disabled="!scraping.manufacturer || scraping.isLoading"
                variant="filled"
                class="bg-green-600 text-white hover:bg-green-700"
              >
                <i class="fas fa-play mr-2"></i>
                {{ scraping.isLoading ? 'Running Scraper...' : 'Run Manufacturer Scraper' }}
              </CustomButton>
              
              <CustomButton
                v-if="scraping.lastResult"
                @click="clearScrapingResults"
                variant="outlined"
                class="text-gray-600 border-gray-300"
              >
                <i class="fas fa-trash mr-2"></i>
                Clear Results
              </CustomButton>
            </div>
            
            <!-- Loading Progress -->
            <div v-if="scraping.isLoading" class="mb-6">
              <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div class="flex items-center">
                  <i class="fas fa-spinner fa-spin text-blue-600 dark:text-blue-400 mr-3"></i>
                  <div>
                    <h4 class="text-sm font-medium text-blue-800 dark:text-blue-200">Manufacturer Scraper Running</h4>
                    <p class="text-xs text-blue-700 dark:text-blue-300 mt-1">
                      Running the manufacturer scraper to update arrow database... This may take up to 2 minutes.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Results Display -->
            <div v-if="scraping.lastResult" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Scraping Results</h4>
                <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <p><strong>Status:</strong> 
                    <span :class="scraping.lastResult.success ? 'text-green-600' : 'text-red-600'">
                      {{ scraping.lastResult.success ? 'Success' : 'Failed' }}
                    </span>
                  </p>
                  <p><strong>URL:</strong> <a :href="scraping.lastResult.url" target="_blank" class="text-blue-600 hover:underline">{{ scraping.lastResult.url }}</a></p>
                  <p><strong>Manufacturer:</strong> {{ scraping.lastResult.manufacturer }}</p>
                  <p v-if="scraping.lastResult.success"><strong>Message:</strong> {{ scraping.lastResult.message }}</p>
                  <p v-else><strong>Error:</strong> {{ scraping.lastResult.error }}</p>
                </div>
              </div>
              
              <!-- Success Details -->
              <div v-if="scraping.lastResult.success && scraping.lastResult.data" class="p-4">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded">
                    <div class="font-medium text-green-800 dark:text-green-200">Arrows Added</div>
                    <div class="text-2xl font-bold text-green-600">{{ scraping.lastResult.data.arrows_added }}</div>
                  </div>
                  <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded">
                    <div class="font-medium text-blue-800 dark:text-blue-200">Spine Specs</div>
                    <div class="text-2xl font-bold text-blue-600">{{ scraping.lastResult.data.spine_specs_added }}</div>
                  </div>
                </div>
                
                <!-- Arrow Models -->
                <div v-if="scraping.lastResult.data.arrow_models && scraping.lastResult.data.arrow_models.length > 0" class="mt-4">
                  <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Extracted Arrow Models:</h5>
                  <div class="flex flex-wrap gap-2">
                    <span 
                      v-for="model in scraping.lastResult.data.arrow_models" 
                      :key="model"
                      class="inline-flex px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded"
                    >
                      {{ model }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Tips and Guidelines -->
            <div class="mt-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <h4 class="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">
                <i class="fas fa-lightbulb mr-2"></i>
                Scraping Tips
              </h4>
              <ul class="text-xs text-yellow-700 dark:text-yellow-300 space-y-1">
                <li>• Use direct product pages with detailed specifications</li>
                <li>• Avoid category pages or general product listings</li>
                <li>• Ensure the page contains spine values, diameters, and weights</li>
                <li>• Pages with tables or structured data work best</li>
                <li>• Scraping may take 30-60 seconds for complex pages</li>
              </ul>
            </div>
          </div>
        </md-elevated-card>
      </div>
      
      <!-- System Tab -->
      <div v-if="activeTab === 'system'">
        <!-- System Information Panel -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                <i class="fas fa-server mr-2 text-indigo-600"></i>
                System Information
              </h2>
              <CustomButton
                @click="loadSystemInfo"
                variant="outlined"
                size="small"
                :disabled="isLoadingSystemInfo"
                class="text-indigo-600 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400"
              >
                <i class="fas fa-refresh mr-2"></i>
                Refresh
              </CustomButton>
            </div>

            <!-- Loading State -->
            <div v-if="isLoadingSystemInfo" class="text-center py-8">
              <i class="fas fa-spinner fa-spin text-2xl text-indigo-600 mb-2"></i>
              <p class="text-gray-600 dark:text-gray-400">Loading system information...</p>
            </div>

            <!-- System Information Content -->
            <div v-else-if="systemInfo" class="space-y-6">
              <!-- Platform & Environment -->
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <div class="text-sm font-medium text-blue-800 dark:text-blue-200">Platform</div>
                  <div class="text-lg font-semibold text-blue-600 dark:text-blue-400">{{ systemInfo.system.platform }}</div>
                  <div class="text-xs text-blue-700 dark:text-blue-300">{{ systemInfo.system.architecture }}</div>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <div class="text-sm font-medium text-green-800 dark:text-green-200">Python Version</div>
                  <div class="text-lg font-semibold text-green-600 dark:text-green-400">{{ systemInfo.system.python_version }}</div>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <div class="text-sm font-medium text-purple-800 dark:text-purple-200">API Port</div>
                  <div class="text-lg font-semibold text-purple-600 dark:text-purple-400">{{ systemInfo.environment.api_port }}</div>
                </div>
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <div class="text-sm font-medium text-orange-800 dark:text-orange-200">SSL Status</div>
                  <div class="text-lg font-semibold" :class="systemInfo.environment.ssl_enabled ? 'text-green-600 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'">
                    {{ systemInfo.environment.ssl_enabled ? 'Enabled' : 'Disabled' }}
                  </div>
                </div>
              </div>

              <!-- Resource Usage -->
              <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
                <h3 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                  <i class="fas fa-chart-line mr-2 text-gray-600"></i>
                  Resource Usage
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {{ systemInfo.resources.memory_usage_percent }}%
                    </div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">Memory Usage</div>
                    <div class="text-xs text-gray-500 dark:text-gray-500">
                      {{ systemInfo.resources.memory_used_gb }} / {{ systemInfo.resources.memory_total_gb }} GB
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-green-600 dark:text-green-400">
                      {{ systemInfo.resources.disk_usage_percent }}%
                    </div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">Disk Usage</div>
                    <div class="text-xs text-gray-500 dark:text-gray-500">
                      {{ systemInfo.resources.disk_used_gb }} / {{ systemInfo.resources.disk_total_gb }} GB
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
                      {{ systemInfo.resources.uptime_hours }}h
                    </div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">Uptime</div>
                    <div class="text-xs text-gray-500 dark:text-gray-500">
                      {{ Math.floor(systemInfo.resources.uptime_hours / 24) }} days
                    </div>
                  </div>
                </div>
              </div>

              <!-- Database Information -->
              <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
                <h3 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                  <i class="fas fa-database mr-2 text-gray-600"></i>
                  Database Locations & Statistics
                </h3>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <!-- Arrow Database -->
                  <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                    <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">
                      <i class="fas fa-bow-arrow mr-2 text-blue-600"></i>
                      Arrow Database
                    </h4>
                    <div class="space-y-2 text-sm">
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Location:</span>
                        <span class="text-gray-900 dark:text-gray-100 font-mono text-xs break-all">{{ systemInfo.databases.arrow_db.location }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Size:</span>
                        <span class="text-gray-900 dark:text-gray-100">{{ systemInfo.databases.arrow_db.size_mb }} MB</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Total Arrows:</span>
                        <span class="text-blue-600 dark:text-blue-400 font-medium">{{ systemInfo.databases.arrow_db.stats.total_arrows || 0 }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Manufacturers:</span>
                        <span class="text-blue-600 dark:text-blue-400 font-medium">{{ systemInfo.databases.arrow_db.stats.total_manufacturers || 0 }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Status:</span>
                        <span class="text-green-600 dark:text-green-400">{{ systemInfo.databases.arrow_db.exists ? 'Available' : 'Missing' }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- User Database -->
                  <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                    <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">
                      <i class="fas fa-users mr-2 text-green-600"></i>
                      User Database
                    </h4>
                    <div class="space-y-2 text-sm">
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Location:</span>
                        <span class="text-gray-900 dark:text-gray-100 font-mono text-xs break-all">{{ systemInfo.databases.user_db.location }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Size:</span>
                        <span class="text-gray-900 dark:text-gray-100">{{ systemInfo.databases.user_db.size_mb }} MB</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Total Users:</span>
                        <span class="text-green-600 dark:text-green-400 font-medium">{{ systemInfo.databases.user_db.stats.total_users || 0 }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Bow Setups:</span>
                        <span class="text-green-600 dark:text-green-400 font-medium">{{ systemInfo.databases.user_db.stats.total_bow_setups || 0 }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Status:</span>
                        <span class="text-green-600 dark:text-green-400">{{ systemInfo.databases.user_db.exists ? 'Available' : 'Missing' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Health Status -->
              <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
                <h3 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                  <i class="fas fa-heartbeat mr-2 text-gray-600"></i>
                  Health Status
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="text-center p-3 rounded-lg" :class="systemInfo.health.status === 'healthy' ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'">
                    <div class="text-2xl font-bold" :class="systemInfo.health.status === 'healthy' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                      <i :class="systemInfo.health.status === 'healthy' ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle'"></i>
                    </div>
                    <div class="text-sm font-medium mt-1" :class="systemInfo.health.status === 'healthy' ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'">
                      System {{ systemInfo.health.status === 'healthy' ? 'Healthy' : 'Issues' }}
                    </div>
                  </div>
                  <div class="text-center p-3 bg-gray-100 dark:bg-gray-900/20 rounded-lg">
                    <div class="text-2xl font-bold text-gray-600 dark:text-gray-400">
                      {{ systemInfo.health.response_time_ms }}ms
                    </div>
                    <div class="text-sm font-medium text-gray-800 dark:text-gray-200 mt-1">
                      Response Time
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Error State -->
            <div v-else-if="systemInfoError" class="text-center py-8">
              <i class="fas fa-exclamation-triangle text-4xl text-red-500 mb-4"></i>
              <p class="text-gray-600 dark:text-gray-400">{{ systemInfoError }}</p>
              <CustomButton
                @click="loadSystemInfo"
                variant="outlined"
                size="small"
                class="mt-4 text-red-600 border-red-600 dark:text-red-400 dark:border-red-400"
              >
                <i class="fas fa-refresh mr-2"></i>
                Retry
              </CustomButton>
            </div>

            <!-- Empty State (initial) -->
            <div v-else class="text-center py-8">
              <i class="fas fa-server text-4xl text-gray-400 mb-4"></i>
              <p class="text-gray-500 dark:text-gray-400">Click "Refresh" to load system information</p>
            </div>
          </div>
        </md-elevated-card>
      </div>

      <!-- Backups Tab -->
      <div v-if="activeTab === 'backups'">
        <!-- Backup Creation -->
        <md-elevated-card class="light-surface light-elevation mb-6">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                <i class="fas fa-plus-circle mr-2 text-green-600"></i>
                Create New Backup
              </h2>
            </div>
            
            <form @submit.prevent="createBackup" class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Backup Name (Optional)
                  </label>
                  <input 
                    v-model="backupForm.name" 
                    type="text" 
                    class="form-input w-full"
                    placeholder="Auto-generated if empty"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Databases to Backup
                  </label>
                  <div class="space-y-2">
                    <label class="flex items-center">
                      <input 
                        v-model="backupForm.includeArrowDb" 
                        type="checkbox" 
                        class="mr-2"
                      />
                      <span class="text-sm text-gray-700 dark:text-gray-300">Arrow Database</span>
                    </label>
                    <label class="flex items-center">
                      <input 
                        v-model="backupForm.includeUserDb" 
                        type="checkbox" 
                        class="mr-2"
                      />
                      <span class="text-sm text-gray-700 dark:text-gray-300">User Database</span>
                    </label>
                  </div>
                </div>
              </div>
              
              <div class="flex justify-end">
                <CustomButton
                  type="submit"
                  variant="filled"
                  :disabled="isCreatingBackup || (!backupForm.includeArrowDb && !backupForm.includeUserDb)"
                  class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800"
                >
                  <span v-if="isCreatingBackup">
                    <i class="fas fa-spinner fa-spin mr-2"></i>
                    Creating Backup...
                  </span>
                  <span v-else>
                    <i class="fas fa-database mr-2"></i>
                    Create Backup
                  </span>
                </CustomButton>
              </div>
            </form>
          </div>
        </md-elevated-card>

        <!-- Upload Backup File for Restore -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-upload mr-2 text-green-600"></i>
              Upload & Restore Backup
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Upload a backup file (.tar.gz or .gz) to restore from external source
            </p>
            
            <form @submit.prevent="uploadAndRestoreBackup" class="space-y-4">
              <!-- File Upload -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Backup File (.tar.gz)
                </label>
                <div class="flex items-center space-x-4">
                  <input
                    ref="fileInput"
                    type="file"
                    accept=".tar.gz"
                    @change="handleFileSelect"
                    class="hidden"
                  />
                  <CustomButton
                    type="button"
                    @click="$refs.fileInput?.click()"
                    variant="outlined"
                    class="text-gray-600 border-gray-300 dark:text-gray-300 dark:border-gray-600"
                  >
                    <i class="fas fa-file mr-2"></i>
                    {{ selectedFile ? selectedFile.name : 'Choose File' }}
                  </CustomButton>
                  <span v-if="selectedFile" class="text-sm text-green-600 dark:text-green-400">
                    {{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB
                  </span>
                </div>
              </div>

              <!-- Restore Options -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Databases to Restore
                </label>
                <div class="space-y-2">
                  <label class="flex items-center">
                    <input
                      type="checkbox"
                      v-model="uploadForm.restoreArrowDb"
                      class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2"
                    />
                    <span class="text-sm text-gray-700 dark:text-gray-300">Arrow Database (specifications, spine data)</span>
                  </label>
                  <label class="flex items-center">
                    <input
                      type="checkbox"
                      v-model="uploadForm.restoreUserDb"
                      class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2"
                    />
                    <span class="text-sm text-gray-700 dark:text-gray-300">User Database (accounts, bow setups)</span>
                  </label>
                </div>
              </div>

              <!-- Warning -->
              <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
                <div class="flex">
                  <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 mr-3 mt-0.5"></i>
                  <div class="text-sm">
                    <p class="text-yellow-800 dark:text-yellow-200 font-medium">Warning</p>
                    <p class="text-yellow-700 dark:text-yellow-300 mt-1">
                      This will overwrite existing data. The current databases will be backed up automatically before restore.
                    </p>
                  </div>
                </div>
              </div>

              <!-- Submit Button -->
              <div class="flex justify-end">
                <CustomButton
                  type="submit"
                  :disabled="isUploadingBackup || !selectedFile || (!uploadForm.restoreArrowDb && !uploadForm.restoreUserDb)"
                  class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600"
                >
                  <span v-if="isUploadingBackup">
                    <i class="fas fa-spinner fa-spin mr-2"></i>
                    Uploading & Restoring...
                  </span>
                  <span v-else>
                    <i class="fas fa-upload mr-2"></i>
                    Upload & Restore
                  </span>
                </CustomButton>
              </div>
            </form>
          </div>
        </md-elevated-card>

        <!-- Backup Management -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                <i class="fas fa-history mr-2 text-indigo-600"></i>
                Available Backups
              </h2>
              <CustomButton
                @click="loadBackups"
                variant="outlined"
                size="small"
                :disabled="isLoadingBackups"
                class="text-indigo-600 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400"
              >
                <i class="fas fa-refresh mr-2"></i>
                Refresh
              </CustomButton>
            </div>

            <!-- Loading State -->
            <div v-if="isLoadingBackups" class="text-center py-8">
              <i class="fas fa-spinner fa-spin text-2xl text-indigo-600 mb-2"></i>
              <p class="text-gray-600 dark:text-gray-400">Loading backups...</p>
            </div>

            <!-- Backup List -->
            <div v-else-if="backups.length > 0" class="space-y-4">
              <div 
                v-for="backup in backups" 
                :key="backup.id" 
                class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="flex items-center mb-2">
                      <h3 class="font-medium text-gray-900 dark:text-gray-100">
                        {{ backup.backup_name }}
                      </h3>
                      <span v-if="backup.cdn_type" class="ml-2 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                        {{ backup.cdn_type.toUpperCase() }}
                      </span>
                      <span 
                        class="ml-2 px-2 py-1 text-xs rounded-full"
                        :class="backup.source === 'cdn' 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                          : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'"
                      >
                        {{ backup.source_description || (backup.source === 'cdn' ? 'Production/CDN' : 'Local Development') }}
                      </span>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <div>
                        <i class="fas fa-calendar-alt mr-1"></i>
                        {{ formatDate(backup.created_at) }}
                      </div>
                      <div>
                        <i class="fas fa-weight-hanging mr-1"></i>
                        {{ backup.file_size_mb ? backup.file_size_mb.toFixed(2) : 'Unknown' }} MB
                      </div>
                      <div>
                        <i class="fas fa-user mr-1"></i>
                        {{ backup.created_by_name || backup.created_by_email }}
                      </div>
                      <div>
                        <i class="fas fa-database mr-1"></i>
                        {{ getBackupContents(backup) }}
                      </div>
                    </div>
                    
                    <div v-if="!backup.local_exists" class="mt-2">
                      <span class="text-xs text-yellow-600 dark:text-yellow-400">
                        <i class="fas fa-cloud mr-1"></i>
                        CDN Only (local file removed)
                      </span>
                    </div>
                  </div>
                  
                  <div class="flex space-x-2 ml-4">
                    <CustomButton
                      @click="downloadBackup(backup)"
                      variant="outlined"
                      size="small"
                      class="text-blue-600 border-blue-600 dark:text-blue-400 dark:border-blue-400"
                    >
                      <i class="fas fa-download mr-1"></i>
                      Download
                    </CustomButton>
                    <CustomButton
                      @click="showRestoreModal(backup)"
                      variant="outlined"
                      size="small"
                      class="text-green-600 border-green-600 dark:text-green-400 dark:border-green-400"
                    >
                      <i class="fas fa-undo mr-1"></i>
                      Restore
                    </CustomButton>
                    <CustomButton
                      @click="confirmDeleteBackup(backup)"
                      variant="outlined"
                      size="small"
                      class="text-red-600 border-red-600 dark:text-red-400 dark:border-red-400"
                    >
                      <i class="fas fa-trash mr-1"></i>
                      Delete
                    </CustomButton>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-8">
              <i class="fas fa-database text-4xl text-gray-400 mb-4"></i>
              <p class="text-gray-500 dark:text-gray-400">No backups found</p>
              <p class="text-sm text-gray-400 dark:text-gray-500">Create your first backup using the form above</p>
            </div>
          </div>
        </md-elevated-card>
      </div>
    </div>

    <!-- Arrow Edit Modal -->
    <AdminArrowEditModal
      :is-open="showArrowEditModal"
      :arrow="selectedArrow"
      :is-creating="isCreatingArrow"
      @close="closeArrowEditModal"
      @save="saveArrow"
    />

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-lg text-center">
        <div class="mb-4">
          <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-2"></i>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Confirm Delete</h3>
        </div>
        <p class="text-gray-700 dark:text-gray-300 mb-6">
          Are you sure you want to delete <strong>{{ arrowToDelete?.manufacturer }} {{ arrowToDelete?.model_name }}</strong>?
          This action cannot be undone.
        </p>
        <div class="flex justify-center space-x-4">
          <CustomButton
            @click="showDeleteModal = false"
            variant="outlined"
            class="text-gray-700 dark:text-gray-200"
          >
            Cancel
          </CustomButton>
          <CustomButton
            @click="deleteArrow"
            variant="filled"
            :disabled="isDeletingArrow"
            class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
          >
            <span v-if="isDeletingArrow">
              <i class="fas fa-spinner fa-spin mr-2"></i>
              Deleting...
            </span>
            <span v-else>
              <i class="fas fa-trash mr-2"></i>
              Delete Arrow
            </span>
          </CustomButton>
        </div>
      </div>
    </div>

    <!-- Access Denied -->
    <div v-else-if="!isCheckingAdmin && !isAdmin" class="text-center py-12">
      <i class="fas fa-shield-alt text-6xl text-red-500 mb-4"></i>
      <h2 class="text-xl font-medium text-gray-900 dark:text-gray-100 mb-2">Access Denied</h2>
      <p class="text-gray-600 dark:text-gray-400 mb-4">You do not have permission to access the admin panel.</p>
      <CustomButton
        @click="$router.push('/')"
        variant="filled"
        class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
      >
        Return to Dashboard
      </CustomButton>
    </div>

    <!-- Invite User Modal -->
    <div v-if="showInviteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Invite Beta User</h3>
        <form @submit.prevent="sendInvite">
          <div class="mb-4">
            <label for="inviteEmail" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email Address</label>
            <input 
              type="email" 
              id="inviteEmail" 
              v-model="inviteForm.email" 
              class="form-input w-full" 
              required 
              placeholder="user@example.com"
            />
          </div>
          <div class="mb-4">
            <label for="inviteMessage" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Message (optional)</label>
            <textarea 
              id="inviteMessage" 
              v-model="inviteForm.message" 
              class="form-textarea w-full h-20 resize-y"
              placeholder="Welcome to the beta testing program..."
            ></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <CustomButton
              type="button"
              @click="showInviteModal = false"
              variant="outlined"
              class="text-gray-700 dark:text-gray-200"
            >
              Cancel
            </CustomButton>
            <CustomButton
              type="submit"
              variant="filled"
              :disabled="isSendingInvite"
              class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
            >
              <span v-if="isSendingInvite">Sending...</span>
              <span v-else>Send Invite</span>
            </CustomButton>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="confirmation.show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-lg text-center">
        <div class="mb-4">
          <i class="fas fa-exclamation-triangle text-yellow-500 text-4xl mb-2"></i>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Confirm Action</h3>
        </div>
        <p class="text-gray-700 dark:text-gray-300 mb-6">
          {{ confirmation.message }}
        </p>
        <div class="flex justify-center space-x-4">
          <CustomButton
            @click="confirmation.onCancel"
            variant="outlined"
            class="text-gray-700 dark:text-gray-200"
          >
            Cancel
          </CustomButton>
          <CustomButton
            @click="confirmation.onConfirm"
            variant="filled"
            class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
          >
            Confirm
          </CustomButton>
        </div>
      </div>
    </div>
    <!-- End of Confirmation Modal -->

    <!-- Restore Backup Modal -->
    <div v-if="showRestoreBackupModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
        <div class="mb-4">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 flex items-center">
            <i class="fas fa-undo text-green-500 mr-2"></i>
            Restore Backup
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {{ backupToRestore?.backup_name }}
          </p>
        </div>

        <form @submit.prevent="restoreBackup" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Databases to Restore
            </label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input 
                  v-model="restoreForm.restoreArrowDb" 
                  type="checkbox" 
                  class="mr-2"
                  :disabled="backupToRestore?.include_arrow_db === false"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  Arrow Database 
                  <span v-if="backupToRestore?.include_arrow_db === false" class="text-xs text-gray-400">(not in backup)</span>
                </span>
              </label>
              <label class="flex items-center">
                <input 
                  v-model="restoreForm.restoreUserDb" 
                  type="checkbox" 
                  class="mr-2"
                  :disabled="backupToRestore?.include_user_db === false"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  User Database
                  <span v-if="backupToRestore?.include_user_db === false" class="text-xs text-gray-400">(not in backup)</span>
                </span>
              </label>
            </div>
          </div>

          <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
            <div class="flex items-center">
              <i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400 mr-2"></i>
              <p class="text-sm text-yellow-800 dark:text-yellow-200">
                This will overwrite existing data. Make sure to create a backup first!
              </p>
            </div>
          </div>

          <div class="flex justify-end space-x-3">
            <CustomButton
              type="button"
              @click="showRestoreBackupModal = false"
              variant="outlined"
              class="text-gray-700 dark:text-gray-200"
            >
              Cancel
            </CustomButton>
            <CustomButton
              type="submit"
              variant="filled"
              :disabled="isRestoringBackup || (!restoreForm.restoreArrowDb && !restoreForm.restoreUserDb)"
              class="bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800"
            >
              <span v-if="isRestoringBackup">
                <i class="fas fa-spinner fa-spin mr-2"></i>
                Restoring...
              </span>
              <span v-else>
                <i class="fas fa-undo mr-2"></i>
                Restore Backup
              </span>
            </CustomButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

// Authentication check
const { user, token, checkAdminStatus, getAllUsers, setUserAdminStatus } = useAuth()

// Check if user is admin
const isAdmin = ref(false)
const isCheckingAdmin = ref(true) // Loading state for admin check

// State
const users = ref([])
const userStats = ref({
  total: 0,
  active: 0,
  pending: 0
})
const loading = ref(false)
const showInviteModal = ref(false)
const isSendingInvite = ref(false)

// Tab management
const activeTab = ref('users')

// Arrow management state
const showArrowEditModal = ref(false)
const selectedArrow = ref(null)
const isCreatingArrow = ref(false)
const showDeleteModal = ref(false)
const arrowToDelete = ref(null)
const isDeletingArrow = ref(false)
const arrowsTableRef = ref(null)
const manufacturersTableRef = ref(null)

// Arrow statistics
const arrowStats = ref({
  total: 0,
  manufacturers: 0,
  spines: 0,
  withImages: 0
})

// Manufacturers data
const manufacturers = ref([])

// Backup management state
const backups = ref([])
const isLoadingBackups = ref(false)
const isCreatingBackup = ref(false)
const isRestoringBackup = ref(false)
const showRestoreBackupModal = ref(false)
const backupToRestore = ref(null)

// System information state
const systemInfo = ref(null)
const isLoadingSystemInfo = ref(false)
const systemInfoError = ref(null)

const backupForm = ref({
  name: '',
  includeArrowDb: true,
  includeUserDb: true
})

const restoreForm = ref({
  restoreArrowDb: true,
  restoreUserDb: false
})

// Upload backup state
const selectedFile = ref(null)
const isUploadingBackup = ref(false)
const uploadForm = ref({
  restoreArrowDb: true,
  restoreUserDb: true
})

// Batch fill state
const batchFill = ref({
  selectedManufacturer: '',
  selectedReferenceArrow: null,
  lengthStats: null,
  previewData: null,
  isLoading: false,
  isExecuting: false
})

// Scraping state
const scraping = ref({
  url: '',
  manufacturer: '',
  isLoading: false,
  lastResult: null
})

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success' // 'success', 'error', 'warning'
})

// Confirmation state
const confirmation = ref({
  show: false,
  message: '',
  onConfirm: null,
  onCancel: null
})

const inviteForm = ref({
  email: '',
  message: ''
})

// API
const api = useApi()

// Load admin data
const loadUsers = async () => {
  if (!isAdmin.value) return
  
  try {
    loading.value = true
    const fetchedUsers = await getAllUsers()
    
    // Transform user data to match expected format
    users.value = fetchedUsers.map(user => ({
      id: user.id,
      name: user.name || 'Unnamed User',
      email: user.email,
      picture: user.profile_picture_url || null,
      status: 'active', // All users in database are considered active
      last_login: user.created_at || new Date().toISOString(),
      is_admin: user.is_admin || false
    }))
    
    updateStats()
  } catch (error) {
    console.error('Error loading users:', error)
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  userStats.value = {
    total: users.value.length,
    active: users.value.filter(u => u.status === 'active').length,
    pending: users.value.filter(u => u.status === 'pending').length
  }
}

// Notification helper functions
const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  };
  
  // Auto-hide after 4 seconds
  setTimeout(() => {
    notification.value.show = false;
  }, 4000);
};

const hideNotification = () => {
  notification.value.show = false;
};

// Confirmation helper functions
const showConfirmation = (message, onConfirm, onCancel = null) => {
  confirmation.value = {
    show: true,
    message,
    onConfirm,
    onCancel: onCancel || (() => confirmation.value.show = false)
  };
};

const hideConfirmation = () => {
  confirmation.value.show = false;
};

// User management functions
const toggleAdminStatus = async (user) => {
  try {
    const newAdminStatus = !user.is_admin
    
    showConfirmation(
      `Are you sure you want to ${newAdminStatus ? 'grant admin access to' : 'remove admin access from'} ${user.name || user.email}?`,
      async () => {
        try {
          await setUserAdminStatus(user.id, newAdminStatus)
          user.is_admin = newAdminStatus
          showNotification(`Successfully ${newAdminStatus ? 'granted' : 'removed'} admin access for ${user.name || user.email}`)
          hideConfirmation()
        } catch (error) {
          console.error('Error updating admin status:', error)
          showNotification('Failed to update admin status: ' + error.message, 'error')
          hideConfirmation()
        }
      }
    )
  } catch (error) {
    console.error('Error updating admin status:', error)
    showNotification('Failed to update admin status: ' + error.message, 'error')
  }
}

const toggleUserStatus = async (user) => {
  try {
    const newStatus = user.status === 'active' ? 'suspended' : 'active'
    // TODO: Implement API call for user status (suspend/activate)
    // await api.updateUserStatus(user.id, newStatus)
    
    user.status = newStatus
    updateStats()
  } catch (error) {
    console.error('Error updating user status:', error)
  }
}

const deleteUser = async (user) => {
  showConfirmation(
    `Are you sure you want to delete ${user.name || user.email}?`,
    async () => {
      try {
        // TODO: Implement API call
        // await api.deleteUser(user.id)
        
          const index = users.value.findIndex(u => u.id === user.id)
          if (index !== -1) {
            users.value.splice(index, 1)
          }
          updateStats()
          showNotification(`Successfully deleted ${user.name || user.email}`)
          hideConfirmation()
        } catch (error) {
          console.error('Error deleting user:', error)
          showNotification('Failed to delete user: ' + error.message, 'error')
          hideConfirmation()
        }
      }
    )
}

const sendInvite = async () => {
  try {
    isSendingInvite.value = true
    // TODO: Implement API call
    // await api.sendBetaInvite(inviteForm.value.email, inviteForm.value.message)
    
    console.log('Sending invite to:', inviteForm.value.email)
    
    // Reset form
    inviteForm.value = { email: '', message: '' }
    showInviteModal.value = false
    
    // Reload users list
    await loadUsers()
  } catch (error) {
    console.error('Error sending invite:', error)
  } finally {
    isSendingInvite.value = false
  }
}

// Helper functions
const getStatusBadgeClass = (status) => {
  const classes = {
    'active': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'suspended': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
}

const formatStatus = (status) => {
  if (!status || status.length === 0) return 'Unknown'
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Unknown'
  }
}

// Arrow management functions
const loadArrowStats = async () => {
  try {
    const data = await api.get('/database/stats')
    arrowStats.value = {
      total: data.total_arrows || 0,
      manufacturers: data.total_manufacturers || 0,
      spines: data.total_specifications || 0,
      withImages: data.arrows_with_images || 0
    }
  } catch (error) {
    console.error('Error loading arrow stats:', error)
  }
}

const loadManufacturerStats = async () => {
  // This is called when manufacturers are refreshed
  // We can reload arrow stats since manufacturer changes affect them
  await loadArrowStats()
}

const openEditModal = (arrow) => {
  selectedArrow.value = arrow
  isCreatingArrow.value = false
  showArrowEditModal.value = true
}

const openCreateModal = () => {
  selectedArrow.value = null
  isCreatingArrow.value = true
  showArrowEditModal.value = true
}

const closeArrowEditModal = () => {
  showArrowEditModal.value = false
  selectedArrow.value = null
  isCreatingArrow.value = false
}

const saveArrow = async (arrowData) => {
  try {
    let result
    
    if (isCreatingArrow.value) {
      // Create new arrow
      result = await api.post('/admin/arrows', arrowData)
    } else {
      // Update existing arrow
      result = await api.put(`/admin/arrows/${selectedArrow.value.id}`, arrowData)
    }
    
    showNotification(result.message || `Arrow ${isCreatingArrow.value ? 'created' : 'updated'} successfully`)
    closeArrowEditModal()
    
    // Refresh the arrows table
    if (arrowsTableRef.value) {
      arrowsTableRef.value.loadArrows()
    }
    
    // Refresh stats
    await loadArrowStats()
  } catch (error) {
    console.error('Error saving arrow:', error)
    showNotification(error.message || 'Failed to save arrow', 'error')
  }
}

const confirmDeleteArrow = (arrow) => {
  arrowToDelete.value = arrow
  showDeleteModal.value = true
}

const deleteArrow = async () => {
  if (!arrowToDelete.value) return
  
  try {
    isDeletingArrow.value = true
    
    const result = await api.delete(`/admin/arrows/${arrowToDelete.value.id}`)
    
    showNotification(result.message || 'Arrow deleted successfully')
    showDeleteModal.value = false
    arrowToDelete.value = null
    
    // Refresh the arrows table
    if (arrowsTableRef.value) {
      arrowsTableRef.value.loadArrows()
    }
    
    // Refresh stats
    await loadArrowStats()
  } catch (error) {
    console.error('Error deleting arrow:', error)
    showNotification(error.message || 'Failed to delete arrow', 'error')
  } finally {
    isDeletingArrow.value = false
  }
}

// System information functions
const loadSystemInfo = async () => {
  if (!isAdmin.value) return
  
  try {
    isLoadingSystemInfo.value = true
    systemInfoError.value = null
    
    const response = await api.get('/admin/system-info')
    systemInfo.value = response
    
    console.log('System information loaded:', response)
  } catch (error) {
    console.error('Error loading system info:', error)
    systemInfoError.value = 'Failed to load system information: ' + error.message
  } finally {
    isLoadingSystemInfo.value = false
  }
}

// Backup management functions
const loadBackups = async () => {
  if (!isAdmin.value) return
  
  try {
    isLoadingBackups.value = true
    const response = await api.get('/admin/backups')
    
    // Use the enhanced all_backups array that includes source information and is sorted
    backups.value = response.all_backups || response.cdn_backups || []
    
    console.log(`Loaded ${backups.value.length} total backups (${response.total_cdn} CDN, ${response.total_local} local)`)
  } catch (error) {
    console.error('Error loading backups:', error)
    showNotification('Failed to load backups: ' + error.message, 'error')
  } finally {
    isLoadingBackups.value = false
  }
}

const createBackup = async () => {
  try {
    isCreatingBackup.value = true
    
    const result = await api.post('/admin/backup', {
      backup_name: backupForm.value.name || undefined,
      include_arrow_db: backupForm.value.includeArrowDb,
      include_user_db: backupForm.value.includeUserDb
    })
    
    showNotification(result.message || 'Backup created successfully')
    
    // Reset form
    backupForm.value = {
      name: '',
      includeArrowDb: true,
      includeUserDb: true
    }
    
    // Reload backups list
    await loadBackups()
    
  } catch (error) {
    console.error('Error creating backup:', error)
    showNotification('Failed to create backup: ' + error.message, 'error')
  } finally {
    isCreatingBackup.value = false
  }
}

const showRestoreModal = (backup) => {
  console.log('Opening restore modal for backup:', backup)
  backupToRestore.value = backup
  
  // Intelligently detect what's in the backup using various property names
  const hasArrowDb = backup.include_arrow_db || backup.includes?.arrow_database || 
                     backup.arrow_db_stats || backup.backup_name?.includes('arrows') ||
                     !backup.backup_name?.includes('users') // If not user-only, likely has arrows
  const hasUserDb = backup.include_user_db || backup.includes?.user_database || 
                    backup.user_db_stats || backup.backup_name?.includes('users')
  
  // Set backup properties for the modal to use
  backup.include_arrow_db = hasArrowDb
  backup.include_user_db = hasUserDb
  
  // Set default restore options - ensure at least one is selected
  restoreForm.value = {
    restoreArrowDb: hasArrowDb, // Default to true if backup contains arrow data
    restoreUserDb: false // Default to false for safety, but allow user to choose
  }
  
  console.log('Backup analysis:', { hasArrowDb, hasUserDb, backup_name: backup.backup_name })
  console.log('Restore form initialized:', restoreForm.value)
  
  showRestoreBackupModal.value = true
}

const restoreBackup = async () => {
  if (!backupToRestore.value) return
  
  try {
    isRestoringBackup.value = true
    
    const result = await api.post(`/admin/backup/${backupToRestore.value.id}/restore`, {
      restore_arrow_db: restoreForm.value.restoreArrowDb,
      restore_user_db: restoreForm.value.restoreUserDb,
      force: true
    })
    
    showNotification(result.message || 'Backup restored successfully')
    showRestoreBackupModal.value = false
    backupToRestore.value = null
    
    // If user database was restored, we might need to refresh user data
    if (restoreForm.value.restoreUserDb) {
      showNotification('User database restored. You may need to refresh the page.', 'warning')
    }
    
  } catch (error) {
    console.error('Error restoring backup:', error)
    showNotification('Failed to restore backup: ' + error.message, 'error')
  } finally {
    isRestoringBackup.value = false
  }
}

const downloadBackup = async (backup) => {
  try {
    const response = await api.get(`/admin/backup/${backup.id}/download`)
    
    console.log('Download response:', response)
    
    if (response.cdn_url) {
      // CDN backup - open URL in new window
      window.open(response.cdn_url, '_blank')
      showNotification('Download started')
    } else if (response.download_type === 'local_file' && response.local_path) {
      // Local file backup - download through file endpoint
      try {
        const config = useRuntimeConfig()
        const downloadResponse = await fetch(`${config.public.apiBase}/admin/backup/download-file`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token.value}`
          },
          body: JSON.stringify({
            local_path: response.local_path
          })
        })
        
        if (!downloadResponse.ok) {
          throw new Error(`Download failed: ${downloadResponse.statusText}`)
        }
        
        // Create blob and download
        const blob = await downloadResponse.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = response.backup_name + '.tar.gz'
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        
        showNotification('Download started')
      } catch (fileError) {
        console.error('Error downloading file:', fileError)
        showNotification('Failed to download file: ' + fileError.message, 'error')
      }
    } else {
      showNotification('Download not available for this backup', 'error')
    }
  } catch (error) {
    console.error('Error downloading backup:', error)
    showNotification('Failed to get download info: ' + error.message, 'error')
  }
}

const confirmDeleteBackup = (backup) => {
  showConfirmation(
    `Are you sure you want to delete the backup "${backup.backup_name}"? This action cannot be undone.`,
    async () => {
      try {
        const result = await api.delete(`/admin/backup/${backup.id}`)
        showNotification(result.message || 'Backup deleted successfully')
        
        // Reload backups list
        await loadBackups()
        hideConfirmation()
      } catch (error) {
        console.error('Error deleting backup:', error)
        showNotification('Failed to delete backup: ' + error.message, 'error')
        hideConfirmation()
      }
    }
  )
}

const getBackupContents = (backup) => {
  const contents = []
  
  // Check various property names that might indicate database inclusion
  const hasArrowDb = backup.include_arrow_db || backup.includes?.arrow_database || 
                     backup.arrow_db_stats || backup.backup_name?.includes('arrows') ||
                     !backup.backup_name?.includes('users') // If not user-only, likely has arrows
  const hasUserDb = backup.include_user_db || backup.includes?.user_database || 
                    backup.user_db_stats || backup.backup_name?.includes('users')
  
  if (hasArrowDb) contents.push('Arrows')
  if (hasUserDb) contents.push('Users')
  return contents.join(', ') || 'Both'
}

// File upload functions
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Validate file type - support both .tar.gz and .gz files
    const filename = file.name.toLowerCase()
    if (!(filename.endsWith('.tar.gz') || filename.endsWith('.gz'))) {
      showNotification('Please select a .tar.gz or .gz backup file', 'error')
      return
    }
    selectedFile.value = file
    console.log('File selected:', file.name, file.size, 'bytes')
  } else {
    selectedFile.value = null
  }
}

const uploadAndRestoreBackup = async () => {
  if (!selectedFile.value) {
    showNotification('Please select a backup file', 'error')
    return
  }
  
  if (!uploadForm.value.restoreArrowDb && !uploadForm.value.restoreUserDb) {
    showNotification('Please select at least one database to restore', 'error')
    return
  }
  
  try {
    isUploadingBackup.value = true
    
    // Create FormData for file upload
    const formData = new FormData()
    formData.append('backup_file', selectedFile.value)
    formData.append('restore_arrow_db', uploadForm.value.restoreArrowDb.toString())
    formData.append('restore_user_db', uploadForm.value.restoreUserDb.toString())
    formData.append('force_restore', 'true')
    
    console.log('Uploading backup file:', selectedFile.value.name)
    console.log('Restore options:', uploadForm.value)
    
    // Upload and restore
    const result = await api.post('/admin/backup/upload', formData)
    
    showNotification(result.message || 'Backup uploaded and restored successfully', 'success')
    
    // Reset form
    selectedFile.value = null
    uploadForm.value = {
      restoreArrowDb: true,
      restoreUserDb: true
    }
    
    // Clear file input
    if (process.client) {
      const fileInput = document.querySelector('input[type="file"]')
      if (fileInput) fileInput.value = ''
    }
    
    // Reload backups list
    await loadBackups()
    
    // Show additional warning if user database was restored
    if (uploadForm.value.restoreUserDb) {
      showNotification('User database restored. You may need to refresh the page.', 'warning')
    }
    
  } catch (error) {
    console.error('Error uploading backup:', error)
    showNotification('Failed to upload backup: ' + error.message, 'error')
  } finally {
    isUploadingBackup.value = false
  }
}

// Check admin status and load data
const checkAndLoadAdminData = async () => {
  try {
    console.log('checkAndLoadAdminData called, user:', user.value)
    isCheckingAdmin.value = true
    
    if (user.value) {
      console.log('User exists, calling checkAdminStatus...')
      const adminStatus = await checkAdminStatus()
      console.log('Admin status result:', adminStatus)
      
      // Set admin status BEFORE setting loading to false
      isAdmin.value = adminStatus
      
      if (adminStatus) {
        console.log('User is admin, loading users and arrow stats...')
        await loadUsers()
        await loadArrowStats()
        // Load backups if we're on the backups tab
        if (activeTab.value === 'backups') {
          await loadBackups()
        }
      } else {
        console.log('User is not admin')
      }
    } else {
      console.log('No user found')
      isAdmin.value = false
    }
  } catch (error) {
    console.error('Error checking admin status:', error)
    isAdmin.value = false
  } finally {
    // Ensure isCheckingAdmin is only set to false after isAdmin is properly set
    isCheckingAdmin.value = false
  }
}

// Load data on mount
onMounted(() => {
  console.log('Admin page mounted!')
  console.log('Current token:', token.value)
  console.log('Current user:', user.value)
  checkAndLoadAdminData()
})

// Batch Fill Methods
const loadManufacturerLengthStats = async () => {
  console.log('loadManufacturerLengthStats called with:', batchFill.value.selectedManufacturer)
  
  if (!batchFill.value.selectedManufacturer) {
    batchFill.value.lengthStats = null
    batchFill.value.selectedReferenceArrow = null
    batchFill.value.previewData = null
    return
  }
  
  try {
    batchFill.value.isLoading = true
    console.log('Loading stats for manufacturer:', batchFill.value.selectedManufacturer)
    const response = await api.get(`/admin/manufacturers/${encodeURIComponent(batchFill.value.selectedManufacturer)}/length-stats`)
    console.log('Length stats response:', response)
    batchFill.value.lengthStats = response
    batchFill.value.selectedReferenceArrow = null
    batchFill.value.previewData = null
  } catch (error) {
    console.error('Error loading manufacturer length stats:', error)
    showNotification('Failed to load manufacturer statistics: ' + error.message, 'error')
  } finally {
    batchFill.value.isLoading = false
  }
}

const previewBatchFill = async () => {
  if (!batchFill.value.selectedManufacturer || !batchFill.value.selectedReferenceArrow) {
    return
  }
  
  try {
    batchFill.value.isLoading = true
    const response = await api.post('/admin/batch-fill/preview', {
      manufacturer: batchFill.value.selectedManufacturer,
      reference_arrow_id: batchFill.value.selectedReferenceArrow
    })
    batchFill.value.previewData = response
    showNotification(`Preview ready: ${response.summary.arrows_to_update} arrows can be updated`, 'success')
  } catch (error) {
    console.error('Error previewing batch fill:', error)
    showNotification('Failed to preview batch fill: ' + error.message, 'error')
  } finally {
    batchFill.value.isLoading = false
  }
}

const executeBatchFill = async () => {
  if (!batchFill.value.selectedManufacturer || !batchFill.value.selectedReferenceArrow) {
    return
  }
  
  try {
    batchFill.value.isExecuting = true
    const response = await api.post('/admin/batch-fill/execute', {
      manufacturer: batchFill.value.selectedManufacturer,
      reference_arrow_id: batchFill.value.selectedReferenceArrow,
      confirm: true
    })
    
    showNotification(`Batch fill completed: ${response.summary.updated_spine_specs} spine specifications updated across ${response.summary.updated_arrows_count} arrows`, 'success')
    
    // Reset form
    batchFill.value.selectedManufacturer = ''
    batchFill.value.selectedReferenceArrow = null
    batchFill.value.lengthStats = null
    batchFill.value.previewData = null
    
    // Refresh arrow stats
    await loadArrowStats()
    
  } catch (error) {
    console.error('Error executing batch fill:', error)
    showNotification('Failed to execute batch fill: ' + error.message, 'error')
  } finally {
    batchFill.value.isExecuting = false
  }
}

const loadManufacturersList = async () => {
  try {
    console.log('Loading manufacturers list...')
    const response = await api.get('/admin/manufacturers')
    console.log('Manufacturers response:', response)
    manufacturers.value = response.manufacturers
    console.log('Manufacturers loaded:', manufacturers.value)
  } catch (error) {
    console.error('Error loading manufacturers:', error)
    showNotification('Failed to load manufacturers', 'error')
  }
}

// Manufacturer Scraping Methods
const startScraping = async () => {
  if (!scraping.value.manufacturer) {
    return
  }
  
  try {
    scraping.value.isLoading = true
    scraping.value.lastResult = null
    
    const response = await api.post('/admin/scrape-url', {
      url: scraping.value.url,
      manufacturer: scraping.value.manufacturer
    })
    
    scraping.value.lastResult = {
      success: true,
      message: response.message,
      url: scraping.value.url,
      manufacturer: scraping.value.manufacturer,
      data: response.data
    }
    
    showNotification(`Successfully scraped ${response.data.arrows_added} arrow(s) from URL`, 'success')
    
    // Refresh arrow stats
    await loadArrowStats()
    
  } catch (error) {
    console.error('Error scraping URL:', error)
    
    scraping.value.lastResult = {
      success: false,
      error: error.message,
      url: scraping.value.url,
      manufacturer: scraping.value.manufacturer
    }
    
    showNotification('Failed to scrape URL: ' + error.message, 'error')
    
  } finally {
    scraping.value.isLoading = false
  }
}

const clearScrapingResults = () => {
  scraping.value.lastResult = null
  scraping.value.url = ''
  scraping.value.manufacturer = ''
}

// Watch for user changes
watch(user, () => {
  if (user.value) {
    checkAndLoadAdminData()
  } else {
    isAdmin.value = false
    isCheckingAdmin.value = false
  }
})

// Watch for tab changes to load data as needed
watch(activeTab, async (newTab) => {
  if (newTab === 'backups' && isAdmin.value && backups.value.length === 0) {
    await loadBackups()
  }
  if (newTab === 'system' && isAdmin.value && !systemInfo.value) {
    await loadSystemInfo()
  }
  if (newTab === 'datatools' && isAdmin.value && manufacturers.value.length === 0) {
    await loadManufacturersList()
  }
})

// Set page title and meta
useHead({
  title: 'Admin Panel - Beta',
  meta: [
    { name: 'description', content: 'Admin panel for managing beta access and user permissions' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
})
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
</style>