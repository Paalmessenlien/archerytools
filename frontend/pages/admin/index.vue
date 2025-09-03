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
    <div v-if="hasServerAdminAccess" class="mb-6">
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
          @click="navigateTo('/admin/statistics')"
          class="py-2 px-1 border-b-2 font-medium text-sm border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300"
        >
          <i class="fas fa-chart-bar mr-2"></i>
          Statistics
        </button>
        <button
          @click="activeTab = 'spine-charts'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'spine-charts' 
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          <i class="fas fa-chart-line mr-2"></i>
          Spine Calculator Data
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
          @click="activeTab = 'maintenance'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'maintenance' 
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          <i class="fas fa-wrench mr-2"></i>
          Maintenance
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
    <div v-else-if="!isCheckingAdmin && hasServerAdminAccess" class="space-y-6">
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
                      :class="user.status === 'suspended' ? 'text-green-600 border-green-600' : 'text-red-600 border-red-600'"
                    >
                      {{ user.status === 'suspended' ? 'Reactivate' : 'Suspend' }}
                    </CustomButton>
                    <CustomButton
                      v-if="!user.is_admin"
                      @click="deleteUserHandler(user)"
                      variant="outlined"
                      size="small"
                      class="text-red-700 border-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                    >
                      <i class="fas fa-trash-alt mr-1"></i>
                      Delete
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
        
        <!-- Arrow Data Validation -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  <i class="fas fa-check-circle mr-2 text-purple-600"></i>
                  Arrow Data Validation
                </h3>
                <p class="text-gray-600 dark:text-gray-400 text-sm">
                  Validate arrow database quality and identify issues preventing arrows from displaying in calculator
                </p>
              </div>
            </div>
            
            <!-- Validation Controls -->
            <div class="flex gap-4 mb-6">
              <CustomButton
                @click="runValidation"
                :disabled="validation.isLoading"
                variant="filled"
                class="bg-purple-600 text-white hover:bg-purple-700"
              >
                <i class="fas fa-play mr-2"></i>
                {{ validation.isLoading ? 'Running Validation...' : 'Run Data Validation' }}
              </CustomButton>
              
              <CustomButton
                v-if="validation.lastReport"
                @click="generateSqlFixes"
                :disabled="validation.isGeneratingFixes"
                variant="outlined"
                class="text-purple-600 border-purple-300"
              >
                <i class="fas fa-code mr-2"></i>
                {{ validation.isGeneratingFixes ? 'Generating...' : 'Generate SQL Fixes' }}
              </CustomButton>
              
              <CustomButton
                v-if="validation.lastReport && hasDuplicateIssues"
                @click="showMergeDuplicatesDialog = true"
                :disabled="validation.isExecutingMerge"
                variant="filled"
                class="bg-orange-600 text-white hover:bg-orange-700"
              >
                <i class="fas fa-layer-group mr-2"></i>
                {{ validation.isExecutingMerge ? 'Merging...' : 'Merge Duplicates' }}
              </CustomButton>
              
              <CustomButton
                v-if="validation.lastReport"
                @click="clearValidationResults"
                variant="outlined"
                class="text-gray-600 border-gray-300"
              >
                <i class="fas fa-trash mr-2"></i>
                Clear Results
              </CustomButton>
            </div>
            
            <!-- Loading Progress -->
            <div v-if="validation.isLoading" class="mb-6">
              <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <div class="flex items-center">
                  <i class="fas fa-spinner fa-spin text-purple-600 dark:text-purple-400 mr-3"></i>
                  <div>
                    <h4 class="text-sm font-medium text-purple-800 dark:text-purple-200">Data Validation Running</h4>
                    <p class="text-xs text-purple-700 dark:text-purple-300 mt-1">
                      Analyzing arrow database for quality issues... This may take 30-60 seconds.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Validation Results -->
            <div v-if="validation.lastReport" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Validation Report</h4>
                <div class="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                  <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded">
                    <div class="font-medium text-blue-800 dark:text-blue-200">Total Arrows</div>
                    <div class="text-2xl font-bold text-blue-600">{{ validation.lastReport.total_arrows.toLocaleString() }}</div>
                  </div>
                  <div class="bg-red-50 dark:bg-red-900/20 p-3 rounded">
                    <div class="font-medium text-red-800 dark:text-red-200">Critical Issues</div>
                    <div class="text-2xl font-bold text-red-600">{{ validation.lastReport.critical_issues }}</div>
                  </div>
                  <div class="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded">
                    <div class="font-medium text-yellow-800 dark:text-yellow-200">Warning Issues</div>
                    <div class="text-2xl font-bold text-yellow-600">{{ validation.lastReport.warning_issues }}</div>
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded">
                    <div class="font-medium text-green-800 dark:text-green-200">Info Issues</div>
                    <div class="text-2xl font-bold text-green-600">{{ validation.lastReport.info_issues }}</div>
                  </div>
                  <div class="bg-gray-50 dark:bg-gray-900/20 p-3 rounded">
                    <div class="font-medium text-gray-800 dark:text-gray-200">Calculator Impact</div>
                    <div class="text-2xl font-bold text-gray-600">{{ validation.lastReport.calculator_impact.estimated_calculator_accuracy.toFixed(1) }}%</div>
                  </div>
                </div>
              </div>
              
              <!-- Issues by Category -->
              <div v-if="Object.keys(validation.lastReport.issues_by_category).length > 0" class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Issues by Category</h5>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div 
                    v-for="(count, category) in validation.lastReport.issues_by_category" 
                    :key="category"
                    class="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded"
                  >
                    <span class="text-sm text-gray-700 dark:text-gray-300">{{ category }}</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ count }} issues</span>
                  </div>
                </div>
              </div>
              
              <!-- Fix Recommendations -->
              <div v-if="validation.lastReport.fix_recommendations.length > 0" class="p-4">
                <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Recommended Actions</h5>
                <ul class="space-y-2">
                  <li 
                    v-for="(recommendation, index) in validation.lastReport.fix_recommendations" 
                    :key="index"
                    class="flex items-start text-sm text-gray-700 dark:text-gray-300"
                  >
                    <span class="text-green-500 mr-2">•</span>
                    <span>{{ recommendation }}</span>
                  </li>
                </ul>
              </div>
            </div>
            
            <!-- Detailed Issues List -->
            <div v-if="validation.lastReport && validation.lastReport.issues && validation.lastReport.issues.length > 0" class="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <div class="flex justify-between items-start mb-3">
                  <div>
                    <h5 class="font-medium text-gray-900 dark:text-gray-100">Problematic Arrows ({{ sortedValidationIssues.length }} issues)</h5>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Specific arrows with data quality issues</p>
                  </div>
                  
                  <!-- Sorting Controls -->
                  <div class="flex items-center space-x-3">
                    <div class="flex items-center space-x-2">
                      <label class="text-xs font-medium text-gray-600 dark:text-gray-400">Sort by:</label>
                      <select 
                        v-model="validationSortBy"
                        class="text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      >
                        <option value="severity">Severity</option>
                        <option value="category">Category</option>
                        <option value="arrow_id">Arrow ID</option>
                        <option value="manufacturer">Manufacturer</option>
                      </select>
                    </div>
                    
                    <div class="flex items-center space-x-2">
                      <label class="text-xs font-medium text-gray-600 dark:text-gray-400">Filter:</label>
                      <select 
                        v-model="validationFilterSeverity"
                        class="text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      >
                        <option value="">All</option>
                        <option value="critical">Critical Only</option>
                        <option value="warning">Warning Only</option>
                        <option value="info">Info Only</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="max-h-96 overflow-y-auto">
                <div v-for="(issue, index) in sortedValidationIssues" :key="`${issue.arrow_id}-${issue.field}-${index}`" class="border-b border-gray-100 dark:border-gray-700 last:border-b-0">
                  <div class="p-4">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <div class="flex items-center space-x-2 mb-2">
                          <span 
                            :class="{
                              'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300': issue.severity === 'critical',
                              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300': issue.severity === 'warning',
                              'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300': issue.severity === 'info'
                            }"
                            class="px-2 py-1 rounded-full text-xs font-medium"
                          >
                            <i :class="{
                              'fas fa-exclamation-triangle': issue.severity === 'critical',
                              'fas fa-exclamation-circle': issue.severity === 'warning', 
                              'fas fa-info-circle': issue.severity === 'info'
                            }" class="mr-1"></i>
                            {{ issue.severity.toUpperCase() }}
                          </span>
                          <span class="text-xs text-gray-500 dark:text-gray-400">{{ issue.category }}</span>
                        </div>
                        
                        <div class="mb-2">
                          <h6 class="font-medium text-gray-900 dark:text-gray-100">
                            Arrow ID {{ issue.arrow_id }}: {{ issue.manufacturer }} {{ issue.model_name }}
                          </h6>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            Field: <code class="bg-gray-100 dark:bg-gray-700 px-1 rounded">{{ issue.field }}</code>
                          </p>
                        </div>
                        
                        <div class="mb-2">
                          <p class="text-sm text-red-600 dark:text-red-400">
                            <i class="fas fa-bug mr-1"></i>
                            Problem: {{ issue.issue }}
                          </p>
                          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Current value: <code class="bg-gray-100 dark:bg-gray-700 px-1 rounded">{{ issue.current_value }}</code>
                          </p>
                        </div>
                        
                        <div class="mb-3">
                          <p class="text-sm text-green-600 dark:text-green-400">
                            <i class="fas fa-lightbulb mr-1"></i>
                            Suggested fix: {{ issue.suggested_fix }}
                          </p>
                          
                          <!-- Auto-fixable issues with SQL -->
                          <div v-if="issue.sql_fix && !issue.sql_fix.startsWith('--')" class="mt-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded">
                            <p class="text-xs text-green-600 dark:text-green-400 mb-2 font-medium">
                              <i class="fas fa-magic mr-1"></i>
                              Auto-Fixable SQL Solution:
                            </p>
                            <code class="text-xs text-gray-800 dark:text-gray-200 block mb-3 font-mono bg-white dark:bg-gray-800 p-2 rounded border">{{ issue.sql_fix }}</code>
                            
                            <div class="flex items-center space-x-2">
                              <CustomButton
                                @click="executeIndividualFix(issue, index)"
                                :disabled="issue.executing"
                                variant="filled"
                                size="small"
                                class="bg-green-600 text-white hover:bg-green-700 text-xs"
                              >
                                <i :class="issue.executing ? 'fas fa-spinner fa-spin' : 'fas fa-magic'" class="mr-1"></i>
                                {{ issue.executing ? 'Applying Fix...' : 'Auto Fix' }}
                              </CustomButton>
                              
                              <CustomButton
                                @click="copyIndividualSql(issue.sql_fix)"
                                variant="outlined"
                                size="small"
                                class="text-gray-600 border-gray-300 text-xs"
                              >
                                <i class="fas fa-copy mr-1"></i>
                                Copy SQL
                              </CustomButton>
                            </div>
                          </div>
                          
                          <!-- Manual review issues -->
                          <div v-else-if="issue.sql_fix && issue.sql_fix.startsWith('--')" class="mt-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded">
                            <p class="text-xs text-yellow-700 dark:text-yellow-300 mb-2 font-medium">
                              <i class="fas fa-eye mr-1"></i>
                              Manual Review Required:
                            </p>
                            <code class="text-xs text-gray-700 dark:text-gray-300 block mb-3 font-mono bg-white dark:bg-gray-800 p-2 rounded border">{{ issue.sql_fix }}</code>
                            
                            <div class="flex items-center space-x-2">
                              <CustomButton
                                @click="copyIndividualSql(issue.sql_fix)"
                                variant="outlined"
                                size="small"
                                class="text-yellow-600 border-yellow-300 text-xs"
                              >
                                <i class="fas fa-copy mr-1"></i>
                                Copy Notes
                              </CustomButton>
                              
                              <CustomButton
                                @click="navigateTo(`/arrows/${issue.arrow_id}`)"
                                variant="outlined"
                                size="small"
                                class="text-blue-600 border-blue-300 text-xs"
                              >
                                <i class="fas fa-external-link-alt mr-1"></i>
                                View Arrow
                              </CustomButton>
                            </div>
                          </div>
                          
                          <!-- Issues without SQL fixes (use manual edit field) -->
                          <div v-else class="mt-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded">
                            <p class="text-xs text-blue-700 dark:text-blue-300 mb-2 font-medium">
                              <i class="fas fa-hand-paper mr-1"></i>
                              Manual Fix Required:
                            </p>
                            <div class="text-xs text-blue-600 dark:text-blue-400 mb-2">
                              No automated solution available - use manual edit below
                            </div>
                            
                            <CustomButton
                              @click="navigateTo(`/arrows/${issue.arrow_id}`)"
                              variant="outlined"
                              size="small"
                              class="text-blue-600 border-blue-300 text-xs"
                            >
                              <i class="fas fa-external-link-alt mr-1"></i>
                              View Arrow
                            </CustomButton>
                          </div>
                        </div>
                        
                        <!-- Manual Edit Field -->
                        <div class="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded">
                          <label class="block text-xs font-medium text-blue-800 dark:text-blue-200 mb-1">
                            Manual Edit - {{ issue.field }}:
                          </label>
                          <div class="flex items-center space-x-2">
                            <input
                              v-model="issue.manual_value"
                              type="text"
                              :placeholder="String(issue.current_value)"
                              class="flex-1 text-xs px-2 py-1 border border-blue-300 dark:border-blue-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                            />
                            <CustomButton
                              @click="executeManualFix(issue, index)"
                              :disabled="issue.executing || !issue.manual_value"
                              variant="filled"
                              size="small"
                              class="bg-blue-600 text-white hover:bg-blue-700 text-xs"
                            >
                              <i :class="issue.executing ? 'fas fa-spinner fa-spin' : 'fas fa-edit'" class="mr-1"></i>
                              {{ issue.executing ? 'Updating...' : 'Update' }}
                            </CustomButton>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- SQL Fix Script Display -->
            <div v-if="validation.sqlFixScript" class="mt-6 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <h5 class="font-medium text-gray-900 dark:text-gray-100">SQL Fix Script</h5>
                <div class="flex space-x-2">
                  <CustomButton
                    @click="executeSqlFixes"
                    :disabled="validation.isExecutingFixes"
                    variant="filled"
                    class="bg-green-600 text-white hover:bg-green-700 text-xs px-3 py-1"
                  >
                    <i class="fas fa-database mr-1"></i>
                    {{ validation.isExecutingFixes ? 'Executing...' : 'Backup & Execute Fixes' }}
                  </CustomButton>
                  <CustomButton
                    @click="copySqlScript"
                    variant="outlined"
                    class="text-gray-600 border-gray-300 text-xs px-3 py-1"
                  >
                    <i class="fas fa-copy mr-1"></i>
                    Copy Script
                  </CustomButton>
                </div>
              </div>
              <div class="p-4">
                <pre class="text-xs text-gray-800 dark:text-gray-200 bg-white dark:bg-gray-900 p-3 rounded border overflow-x-auto">{{ validation.sqlFixScript }}</pre>
              </div>
            </div>
            
            <!-- Execution Results -->
            <div v-if="validation.executionResult" class="mt-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
              <h5 class="font-medium text-green-800 dark:text-green-200 mb-2">
                <i class="fas fa-check-circle mr-2"></i>
                Fixes Applied Successfully
              </h5>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-green-700 dark:text-green-300 font-medium">Backup Created:</span>
                  <div class="text-green-600 dark:text-green-400">{{ validation.executionResult.backup_name }}</div>
                </div>
                <div>
                  <span class="text-green-700 dark:text-green-300 font-medium">Fixes Applied:</span>
                  <div class="text-green-600 dark:text-green-400">{{ validation.executionResult.fixes_applied }}</div>
                </div>
                <div>
                  <span class="text-green-700 dark:text-green-300 font-medium">Before Issues:</span>
                  <div class="text-green-600 dark:text-green-400">{{ validation.executionResult.before_issues }}</div>
                </div>
                <div>
                  <span class="text-green-700 dark:text-green-300 font-medium">After Issues:</span>
                  <div class="text-green-600 dark:text-green-400">{{ validation.executionResult.after_issues }}</div>
                </div>
              </div>
              <div v-if="validation.executionResult.errors && validation.executionResult.errors.length > 0" class="mt-3">
                <span class="text-red-700 dark:text-red-300 text-sm font-medium">Errors:</span>
                <ul class="text-xs text-red-600 dark:text-red-400 mt-1">
                  <li v-for="error in validation.executionResult.errors" :key="error">• {{ error }}</li>
                </ul>
              </div>
            </div>
            
            <!-- Validation Tips -->
            <div class="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <h4 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
                <i class="fas fa-info-circle mr-2"></i>
                Validation Information
              </h4>
              <ul class="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                <li>• Critical issues prevent arrows from appearing in calculator results</li>
                <li>• Warning issues may cause filtering or display problems</li>
                <li>• Apply SQL fixes carefully and test calculator functionality afterward</li>
                <li>• Re-run validation after applying fixes to verify improvements</li>
                <li>• Backup database before applying large-scale fixes</li>
              </ul>
            </div>
          </div>
        </md-elevated-card>
      </div>
      
      <!-- Maintenance Tab -->
      <div v-if="activeTab === 'maintenance'">
        <!-- Database Migrations -->
        <md-elevated-card class="light-surface light-elevation mb-6">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                <i class="fas fa-code-branch mr-2 text-indigo-600"></i>
                Database Migrations
              </h2>
              <div class="flex space-x-2">
                <CustomButton
                  @click="refreshMigrationStatus"
                  variant="outlined"
                  class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-800"
                >
                  <i class="fas fa-sync mr-2"></i>
                  Refresh
                </CustomButton>
                <CustomButton
                  @click="runMigrations(false)"
                  variant="filled"
                  class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
                  :disabled="migrationStatus?.pending_count === 0"
                >
                  <i class="fas fa-play mr-2"></i>
                  Run Migrations
                </CustomButton>
              </div>
            </div>

            <!-- Migration Status Overview -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div class="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {{ migrationStatus?.total_migrations || 0 }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Total Migrations</div>
              </div>
              <div class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div class="text-2xl font-bold text-green-600 dark:text-green-400">
                  {{ migrationStatus?.applied_count || 0 }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Applied</div>
              </div>
              <div class="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <div class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {{ migrationStatus?.pending_count || 0 }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Pending</div>
              </div>
              <div class="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div class="text-sm font-medium text-gray-600 dark:text-gray-400">Environment</div>
                <div class="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {{ migrationStatus?.environment || 'Unknown' }}
                </div>
              </div>
            </div>

            <!-- Database Migration Legend -->
            <div v-if="migrationStatus" class="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
                <i class="fas fa-info-circle mr-2 text-blue-600 dark:text-blue-400"></i>
                Database Migration System
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <h5 class="font-medium text-gray-800 dark:text-gray-200 mb-2">Architecture:</h5>
                  <div class="space-y-1">
                    <div v-if="databaseHealth?.database_architecture === 'unified'" class="flex items-center space-x-2">
                      <span class="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 rounded-full text-xs font-medium">
                        <i class="fas fa-check mr-1"></i>Unified
                      </span>
                      <span class="text-gray-600 dark:text-gray-400">Single database with all data</span>
                    </div>
                    <div v-else-if="databaseHealth?.database_architecture === 'separate'" class="flex items-center space-x-2">
                      <span class="px-2 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 rounded-full text-xs font-medium">
                        <i class="fas fa-database mr-1"></i>Separate
                      </span>
                      <span class="text-gray-600 dark:text-gray-400">Dual database architecture</span>
                    </div>
                    <div v-else class="flex items-center space-x-2">
                      <span class="px-2 py-1 bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300 rounded-full text-xs font-medium">
                        <i class="fas fa-question mr-1"></i>Unknown
                      </span>
                      <span class="text-gray-600 dark:text-gray-400">Architecture not detected</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h5 class="font-medium text-gray-800 dark:text-gray-200 mb-2">Database Content:</h5>
                  <div class="space-y-1">
                    <div class="flex items-center space-x-2">
                      <span class="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded-full text-xs font-medium">
                        Arrow {{ databaseHealth?.arrow_table_count || 0 }}
                      </span>
                      <span class="text-gray-600 dark:text-gray-400">Arrow specifications & spine data</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <span class="px-2 py-1 bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300 rounded-full text-xs font-medium">
                        User {{ databaseHealth?.user_table_count || 0 }}
                      </span>
                      <span class="text-gray-600 dark:text-gray-400">User accounts & bow setups</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h5 class="font-medium text-gray-800 dark:text-gray-200 mb-2">Status Indicators:</h5>
                  <div class="space-y-1">
                    <div class="flex items-center space-x-2">
                      <span class="px-1.5 py-0.5 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300 rounded text-xs">A</span>
                      <span class="text-gray-600 dark:text-gray-400">Applied to Arrow Database</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <span class="px-1.5 py-0.5 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300 rounded text-xs">U</span>
                      <span class="text-gray-600 dark:text-gray-400">Applied to User Database</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Consolidation Status -->
              <div v-if="databaseHealth?.consolidation_status" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div class="flex items-center space-x-2">
                  <i class="fas fa-merge text-indigo-600 dark:text-indigo-400"></i>
                  <span class="font-medium text-gray-800 dark:text-gray-200">Consolidation Status:</span>
                  <span v-if="databaseHealth.consolidation_status === 'completed'" 
                        class="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 rounded-full text-xs font-medium">
                    <i class="fas fa-check mr-1"></i>Completed
                  </span>
                  <span v-else-if="databaseHealth.consolidation_status === 'pending'" 
                        class="px-2 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 rounded-full text-xs font-medium">
                    <i class="fas fa-clock mr-1"></i>Pending
                  </span>
                  <span v-else-if="databaseHealth.consolidation_status === 'not_applicable'" 
                        class="px-2 py-1 bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300 rounded-full text-xs font-medium">
                    <i class="fas fa-minus mr-1"></i>Not Applicable
                  </span>
                  <span v-else 
                        class="px-2 py-1 bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 rounded-full text-xs font-medium">
                    <i class="fas fa-exclamation mr-1"></i>{{ databaseHealth.consolidation_status }}
                  </span>
                </div>
                <p v-if="databaseHealth.consolidation_status === 'completed'" class="text-xs text-gray-600 dark:text-gray-400 mt-1 ml-6">
                  Database consolidation completed - all data unified in single database
                </p>
                <p v-else-if="databaseHealth.consolidation_status === 'pending'" class="text-xs text-gray-600 dark:text-gray-400 mt-1 ml-6">
                  User database can be consolidated into arrow database for unified architecture
                </p>
              </div>
            </div>

            <!-- Pending Migrations -->
            <div v-if="migrationStatus?.pending_count > 0" class="mb-6">
              <h3 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                Pending Migrations
              </h3>
              <div class="space-y-2">
                <div
                  v-for="migration in migrationStatus.pending_details"
                  :key="migration.version"
                  class="flex justify-between items-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg"
                >
                  <div class="flex-1">
                    <div class="flex items-center space-x-2">
                      <span class="font-mono text-sm text-yellow-800 dark:text-yellow-300">
                        {{ migration.version }}
                      </span>
                      <!-- Database Target Badge -->
                      <span v-if="migration.target_database" 
                            class="text-xs px-2 py-1 rounded-full font-medium"
                            :class="{
                              'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300': migration.target_database === 'arrow',
                              'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300': migration.target_database === 'user'
                            }">
                        {{ migration.target_database === 'arrow' ? 'Arrow DB' : 'User DB' }}
                      </span>
                    </div>
                    <span class="text-gray-600 dark:text-gray-400 text-sm">
                      {{ migration.description }}
                    </span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <!-- Database Status Indicators -->
                    <div v-if="migration.status_in_arrow_db !== undefined || migration.status_in_user_db !== undefined" 
                         class="flex space-x-1">
                      <span v-if="migration.status_in_arrow_db !== undefined"
                            class="text-xs px-1.5 py-0.5 rounded"
                            :class="{
                              'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300': migration.status_in_arrow_db === 'applied',
                              'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300': migration.status_in_arrow_db === 'pending'
                            }"
                            :title="'Arrow DB: ' + migration.status_in_arrow_db">
                        A
                      </span>
                      <span v-if="migration.status_in_user_db !== undefined"
                            class="text-xs px-1.5 py-0.5 rounded"
                            :class="{
                              'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300': migration.status_in_user_db === 'applied',
                              'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300': migration.status_in_user_db === 'pending'
                            }"
                            :title="'User DB: ' + migration.status_in_user_db">
                        U
                      </span>
                    </div>
                    <span class="text-xs px-2 py-1 bg-yellow-200 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200 rounded">
                      Pending
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Applied Migrations History -->
            <div v-if="migrationStatus?.applied_count > 0" class="mb-6">
              <h3 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                Recent Applied Migrations
              </h3>
              <div class="space-y-2 max-h-60 overflow-y-auto">
                <div
                  v-for="migration in migrationStatus.applied_details.slice(0, 10)"
                  :key="migration.version"
                  class="flex justify-between items-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg"
                >
                  <div class="flex-1">
                    <div class="flex items-center space-x-2">
                      <span class="font-mono text-sm text-green-800 dark:text-green-300">
                        {{ migration.version }}
                      </span>
                      <!-- Database Target Badge -->
                      <span v-if="migration.target_database" 
                            class="text-xs px-2 py-1 rounded-full font-medium"
                            :class="{
                              'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300': migration.target_database === 'arrow',
                              'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300': migration.target_database === 'user'
                            }">
                        {{ migration.target_database === 'arrow' ? 'Arrow DB' : 'User DB' }}
                      </span>
                    </div>
                    <span class="text-gray-600 dark:text-gray-400 text-sm">
                      {{ migration.name || migration.description }}
                    </span>
                  </div>
                  <div class="text-right">
                    <div class="flex items-center space-x-2 mb-1">
                      <!-- Database Status Indicators -->
                      <div v-if="migration.status_in_arrow_db !== undefined || migration.status_in_user_db !== undefined" 
                           class="flex space-x-1">
                        <span v-if="migration.status_in_arrow_db !== undefined"
                              class="text-xs px-1.5 py-0.5 rounded"
                              :class="{
                                'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300': migration.status_in_arrow_db === 'applied',
                                'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300': migration.status_in_arrow_db === 'pending'
                              }"
                              :title="'Arrow DB: ' + migration.status_in_arrow_db">
                          A
                        </span>
                        <span v-if="migration.status_in_user_db !== undefined"
                              class="text-xs px-1.5 py-0.5 rounded"
                              :class="{
                                'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300': migration.status_in_user_db === 'applied',
                                'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300': migration.status_in_user_db === 'pending'
                              }"
                              :title="'User DB: ' + migration.status_in_user_db">
                          U
                        </span>
                      </div>
                      <span class="text-xs px-2 py-1 bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200 rounded">
                        Applied
                      </span>
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      {{ migration.applied_at ? new Date(migration.applied_at).toLocaleDateString() : 'Applied' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Complete Migration History -->
            <div v-if="migrationStatus?.migrations && Object.keys(migrationStatus.migrations).length > 0" class="mb-6">
              <div class="flex justify-between items-center mb-3">
                <h3 class="text-md font-medium text-gray-900 dark:text-gray-100">
                  Complete Migration History
                </h3>
                <CustomButton
                  @click="showAllMigrations = !showAllMigrations"
                  variant="text"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  <i :class="showAllMigrations ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="mr-2"></i>
                  {{ showAllMigrations ? 'Hide All' : 'Show All' }} ({{ Object.keys(migrationStatus.migrations).length }})
                </CustomButton>
              </div>
              
              <div v-show="showAllMigrations" class="space-y-2 max-h-96 overflow-y-auto">
                <div
                  v-for="(migration, version, index) in sortedMigrations"
                  :key="version"
                  class="flex justify-between items-center p-3 rounded-lg"
                  :class="{
                    'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800': migration.applied,
                    'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800': !migration.applied
                  }"
                >
                  <div class="flex-1">
                    <div class="flex items-center space-x-2">
                      <!-- Migration Number -->
                      <span class="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 font-medium min-w-8 text-center">
                        {{ index + 1 }}
                      </span>
                      
                      <!-- Migration Version -->
                      <span class="font-mono text-sm font-medium"
                            :class="{
                              'text-green-800 dark:text-green-300': migration.applied,
                              'text-yellow-800 dark:text-yellow-300': !migration.applied
                            }">
                        Migration {{ version }}
                      </span>
                      
                      <!-- Target Database Badge -->
                      <span v-if="migration.target_database" 
                            class="text-xs px-2 py-1 rounded-full font-medium"
                            :class="{
                              'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300': migration.target_database === 'arrow',
                              'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300': migration.target_database === 'user'
                            }">
                        {{ migration.target_database === 'arrow' ? 'Arrow DB' : 'User DB' }}
                      </span>
                      
                      <!-- Status Badge -->
                      <span class="text-xs px-2 py-1 rounded font-medium"
                            :class="{
                              'bg-green-200 text-green-800 dark:bg-green-800/50 dark:text-green-200': migration.applied,
                              'bg-yellow-200 text-yellow-800 dark:bg-yellow-800/50 dark:text-yellow-200': !migration.applied
                            }">
                        {{ migration.applied ? 'Applied' : 'Pending' }}
                      </span>
                    </div>
                    
                    <!-- Migration Description -->
                    <div class="text-sm mt-1"
                         :class="{
                           'text-gray-600 dark:text-gray-400': migration.applied,
                           'text-gray-700 dark:text-gray-300': !migration.applied
                         }">
                      {{ migration.description || 'No description available' }}
                    </div>
                  </div>
                  
                  <div class="text-right">
                    <!-- Database Status Indicators -->
                    <div v-if="migration.status_in_arrow_db !== undefined || migration.status_in_user_db !== undefined" 
                         class="flex space-x-1 justify-end mb-2">
                      <span v-if="migration.status_in_arrow_db !== undefined"
                            class="text-xs px-1.5 py-0.5 rounded font-medium"
                            :class="{
                              'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300': migration.status_in_arrow_db,
                              'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300': !migration.status_in_arrow_db
                            }"
                            :title="'Arrow DB: ' + (migration.status_in_arrow_db ? 'Applied' : 'Pending')">
                        A
                      </span>
                      <span v-if="migration.status_in_user_db !== undefined"
                            class="text-xs px-1.5 py-0.5 rounded font-medium"
                            :class="{
                              'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300': migration.status_in_user_db,
                              'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300': !migration.status_in_user_db
                            }"
                            :title="'User DB: ' + (migration.status_in_user_db ? 'Applied' : 'Pending')">
                        U
                      </span>
                    </div>
                    
                    <!-- Applied Date -->
                    <div class="text-xs"
                         :class="{
                           'text-gray-500 dark:text-gray-400': migration.applied,
                           'text-gray-600 dark:text-gray-300': !migration.applied
                         }">
                      {{ migration.applied_at ? new Date(migration.applied_at).toLocaleString() : (migration.applied ? 'Applied' : 'Not Applied') }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </md-elevated-card>

        <!-- Database Health -->
        <md-elevated-card class="light-surface light-elevation mb-6">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                <i class="fas fa-heart-pulse mr-2 text-red-600"></i>
                Database Health
              </h2>
              <div class="flex space-x-2">
                <CustomButton
                  @click="refreshDatabaseHealth"
                  variant="outlined"
                  class="text-gray-600 border-gray-300 hover:bg-gray-50 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-800"
                >
                  <i class="fas fa-sync mr-2"></i>
                  Check Health
                </CustomButton>
                <CustomButton
                  @click="optimizeDatabase"
                  variant="filled"
                  class="bg-green-600 text-white hover:bg-green-700"
                  :disabled="isOptimizing"
                >
                  <i class="fas fa-tools mr-2"></i>
                  {{ isOptimizing ? 'Optimizing...' : 'Optimize' }}
                </CustomButton>
              </div>
            </div>

            <!-- Health Status Overview -->
            <div v-if="databaseHealth" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div class="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {{ databaseHealth.database_size_mb }}MB
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Database Size</div>
              </div>
              <div class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div class="text-2xl font-bold text-green-600 dark:text-green-400">
                  {{ databaseHealth.total_tables }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Tables</div>
              </div>
              <div class="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {{ databaseHealth.total_indexes }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Indexes</div>
              </div>
              <div class="text-center p-4 rounded-lg"
                   :class="{
                     'bg-green-50 dark:bg-green-900/20': databaseHealth.performance_score >= 80,
                     'bg-yellow-50 dark:bg-yellow-900/20': databaseHealth.performance_score >= 60 && databaseHealth.performance_score < 80,
                     'bg-red-50 dark:bg-red-900/20': databaseHealth.performance_score < 60
                   }">
                <div class="text-2xl font-bold"
                     :class="{
                       'text-green-600 dark:text-green-400': databaseHealth.performance_score >= 80,
                       'text-yellow-600 dark:text-yellow-400': databaseHealth.performance_score >= 60 && databaseHealth.performance_score < 80,
                       'text-red-600 dark:text-red-400': databaseHealth.performance_score < 60
                     }">
                  {{ databaseHealth.performance_score }}/100
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Health Score</div>
              </div>
            </div>

            <!-- Health Recommendations -->
            <div v-if="databaseHealth?.recommendations?.length" class="mb-4">
              <h3 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                Recommendations
              </h3>
              <div class="space-y-2">
                <div
                  v-for="(recommendation, index) in databaseHealth.recommendations"
                  :key="index"
                  class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg"
                >
                  <div class="flex items-start">
                    <i class="fas fa-lightbulb text-blue-600 dark:text-blue-400 mr-2 mt-1"></i>
                    <span class="text-sm text-gray-700 dark:text-gray-300">
                      {{ recommendation }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Integrity Status -->
            <div v-if="databaseHealth" class="p-4 rounded-lg"
                 :class="{
                   'bg-green-50 dark:bg-green-900/20': databaseHealth.integrity_status === 'HEALTHY',
                   'bg-red-50 dark:bg-red-900/20': databaseHealth.integrity_status !== 'HEALTHY'
                 }">
              <div class="flex items-center">
                <i :class="[
                     'fas mr-2',
                     {
                       'fa-check-circle text-green-600 dark:text-green-400': databaseHealth.integrity_status === 'HEALTHY',
                       'fa-exclamation-triangle text-red-600 dark:text-red-400': databaseHealth.integrity_status !== 'HEALTHY'
                     }
                   ]"></i>
                <span class="font-medium"
                      :class="{
                        'text-green-800 dark:text-green-200': databaseHealth.integrity_status === 'HEALTHY',
                        'text-red-800 dark:text-red-200': databaseHealth.integrity_status !== 'HEALTHY'
                      }">
                  Database Integrity: {{ databaseHealth.integrity_status }}
                </span>
              </div>
            </div>
          </div>
        </md-elevated-card>

        <!-- Maintenance Operations -->
        <md-elevated-card class="light-surface light-elevation">
          <div class="p-6">
            <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-tools mr-2 text-orange-600"></i>
              Maintenance Operations
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- VACUUM Database -->
              <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div class="flex items-center justify-between mb-3">
                  <div>
                    <h3 class="font-medium text-gray-900 dark:text-gray-100">VACUUM Database</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Reclaim unused space and defragment</p>
                  </div>
                  <CustomButton
                    @click="vacuumDatabase"
                    variant="outlined"
                    class="text-blue-600 border-blue-300 hover:bg-blue-50 dark:text-blue-400"
                    :disabled="isVacuuming"
                  >
                    <i class="fas fa-compress mr-2"></i>
                    {{ isVacuuming ? 'Running...' : 'VACUUM' }}
                  </CustomButton>
                </div>
              </div>

              <!-- Schema Verification -->
              <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div class="flex items-center justify-between mb-3">
                  <div>
                    <h3 class="font-medium text-gray-900 dark:text-gray-100">Schema Verification</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Verify database schema integrity for unified architecture</p>
                  </div>
                  <CustomButton
                    @click="verifySchema"
                    variant="outlined"
                    class="text-green-600 border-green-300 hover:bg-green-50 dark:text-green-400"
                    :disabled="isVerifying"
                  >
                    <i class="fas fa-check-double mr-2"></i>
                    {{ isVerifying ? 'Checking...' : 'Verify' }}
                  </CustomButton>
                </div>
                
                <!-- Schema Verification Results -->
                <div v-if="schemaVerification" class="mt-4 space-y-3">
                  <!-- Architecture Type and Validity -->
                  <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        <i class="fas fa-database mr-2"></i>Database Architecture
                      </span>
                      <span class="px-2 py-1 rounded-full text-xs font-medium"
                            :class="{
                              'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300': schemaVerification.architecture_type === 'unified',
                              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300': schemaVerification.architecture_type === 'separate',
                              'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300': schemaVerification.architecture_type === 'unknown'
                            }">
                        {{ schemaVerification.architecture_type === 'unified' ? 'Unified Database' : 
                           schemaVerification.architecture_type === 'separate' ? 'Separate Databases' :
                           'Unknown Architecture' }}
                      </span>
                    </div>
                    
                    <!-- Schema Validity Indicators -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div class="flex items-center space-x-2">
                        <i class="fas fa-shield-alt"
                           :class="{
                             'text-green-600': schemaVerification.schema_valid,
                             'text-red-600': !schemaVerification.schema_valid
                           }"></i>
                        <span class="text-xs text-gray-600 dark:text-gray-400">
                          General Schema: 
                          <span :class="schemaVerification.schema_valid ? 'text-green-600' : 'text-red-600'" class="font-medium">
                            {{ schemaVerification.schema_valid ? 'Valid' : 'Invalid' }}
                          </span>
                        </span>
                      </div>
                      
                      <div v-if="schemaVerification.architecture_type === 'unified'" class="flex items-center space-x-2">
                        <i class="fas fa-layer-group"
                           :class="{
                             'text-green-600': schemaVerification.unified_schema_valid,
                             'text-orange-600': !schemaVerification.unified_schema_valid
                           }"></i>
                        <span class="text-xs text-gray-600 dark:text-gray-400">
                          Unified Schema: 
                          <span :class="schemaVerification.unified_schema_valid ? 'text-green-600' : 'text-orange-600'" class="font-medium">
                            {{ schemaVerification.unified_schema_valid ? 'Complete' : 'Incomplete' }}
                          </span>
                        </span>
                      </div>
                      
                      <div v-if="schemaVerification.architecture_type === 'separate'" class="flex items-center space-x-2">
                        <i class="fas fa-layer-group"
                           :class="{
                             'text-green-600': schemaVerification.separate_schema_valid,
                             'text-orange-600': !schemaVerification.separate_schema_valid
                           }"></i>
                        <span class="text-xs text-gray-600 dark:text-gray-400">
                          Arrow Schema: 
                          <span :class="schemaVerification.separate_schema_valid ? 'text-green-600' : 'text-orange-600'" class="font-medium">
                            {{ schemaVerification.separate_schema_valid ? 'Valid' : 'Invalid' }}
                          </span>
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Issues Summary -->
                  <div v-if="schemaVerification.missing_tables?.length || schemaVerification.missing_columns?.length" 
                       class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3">
                    <h4 class="text-sm font-medium text-orange-800 dark:text-orange-200 mb-2">
                      <i class="fas fa-exclamation-triangle mr-2"></i>Schema Issues Found
                    </h4>
                    
                    <div v-if="schemaVerification.missing_tables?.length" class="mb-2">
                      <span class="text-xs font-medium text-orange-700 dark:text-orange-300">Missing Tables:</span>
                      <ul class="text-xs text-orange-600 dark:text-orange-400 ml-4 mt-1">
                        <li v-for="table in schemaVerification.missing_tables" :key="table" class="list-disc">
                          {{ table }}
                        </li>
                      </ul>
                    </div>
                    
                    <div v-if="schemaVerification.missing_columns?.length">
                      <span class="text-xs font-medium text-orange-700 dark:text-orange-300">Missing Columns:</span>
                      <ul class="text-xs text-orange-600 dark:text-orange-400 ml-4 mt-1">
                        <li v-for="column in schemaVerification.missing_columns" :key="column" class="list-disc">
                          {{ column }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  
                  <!-- Recommendations -->
                  <div v-if="schemaVerification.recommendations?.length" class="space-y-1">
                    <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">
                      <i class="fas fa-lightbulb mr-2"></i>Recommendations
                    </h4>
                    <ul class="space-y-1">
                      <li v-for="(rec, index) in schemaVerification.recommendations" :key="index" 
                          class="text-xs text-gray-600 dark:text-gray-400 flex items-start space-x-2">
                        <span class="text-gray-400 mt-0.5">•</span>
                        <span>{{ rec }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Last Maintenance Operations -->
            <div v-if="lastMaintenanceResults.length" class="mt-6">
              <h3 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                Recent Operations
              </h3>
              <div class="space-y-2 max-h-40 overflow-y-auto">
                <div
                  v-for="(result, index) in lastMaintenanceResults"
                  :key="index"
                  class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div class="flex justify-between items-start">
                    <div>
                      <span class="font-medium text-sm text-gray-900 dark:text-gray-100">
                        {{ result.operation }}
                      </span>
                      <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {{ result.message }}
                      </p>
                    </div>
                    <div class="text-right">
                      <span class="text-xs px-2 py-1 rounded"
                            :class="{
                              'bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200': result.success,
                              'bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200': !result.success
                            }">
                        {{ result.success ? 'Success' : 'Failed' }}
                      </span>
                      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {{ new Date(result.timestamp).toLocaleTimeString() }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
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

      <!-- Spine Charts Tab -->
      <div v-if="activeTab === 'spine-charts'">
        <SpineChartLibrary />
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
                  <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                    <div class="flex items-center">
                      <i class="fas fa-database text-blue-600 dark:text-blue-400 mr-2"></i>
                      <div>
                        <p class="text-sm font-medium text-blue-800 dark:text-blue-200">Unified Database Backup</p>
                        <p class="text-xs text-blue-700 dark:text-blue-300">Backs up the complete unified database including arrows, users, and configurations</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="flex justify-end">
                <CustomButton
                  type="submit"
                  variant="filled"
                  :disabled="isCreatingBackup"
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

              <!-- Restore Information -->
              <div>
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                  <div class="flex items-center">
                    <i class="fas fa-database text-blue-600 dark:text-blue-400 mr-2"></i>
                    <div>
                      <p class="text-sm font-medium text-blue-800 dark:text-blue-200">Unified Database Restore</p>
                      <p class="text-xs text-blue-700 dark:text-blue-300">Will restore the complete unified database including arrows, users, and configurations</p>
                    </div>
                  </div>
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
                  :disabled="isUploadingBackup || !selectedFile"
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
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
              <div>
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                  <i class="fas fa-history mr-2 text-indigo-600"></i>
                  Available Backups
                </h2>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Cross-platform backup access from all environments
                </p>
              </div>
              
              <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <!-- Environment Filter -->
                <div class="flex items-center gap-2">
                  <label class="text-sm text-gray-700 dark:text-gray-300">Environment:</label>
                  <select 
                    v-model="backupFilter.environment" 
                    class="px-3 py-1 text-sm border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300"
                  >
                    <option value="">All</option>
                    <option value="production">Production</option>
                    <option value="development">Development</option>
                    <option value="staging">Staging</option>
                    <option value="unknown">Unknown</option>
                  </select>
                </div>
                
                <!-- Source Filter -->
                <div class="flex items-center gap-2">
                  <label class="text-sm text-gray-700 dark:text-gray-300">Source:</label>
                  <select 
                    v-model="backupFilter.source" 
                    class="px-3 py-1 text-sm border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300"
                  >
                    <option value="">All</option>
                    <option value="cdn">CDN</option>
                    <option value="local">Local</option>
                  </select>
                </div>
                
                <!-- Refresh Button -->
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
            </div>

            <!-- Loading State -->
            <div v-if="isLoadingBackups" class="text-center py-8">
              <i class="fas fa-spinner fa-spin text-2xl text-indigo-600 mb-2"></i>
              <p class="text-gray-600 dark:text-gray-400">Loading backups...</p>
            </div>

            <!-- Backup List -->
            <div v-else-if="backups.length > 0" class="space-y-4">
              <!-- Filtered Results Info -->
              <div v-if="filteredBackups.length !== backups.length" class="text-sm text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                <i class="fas fa-filter mr-2"></i>
                Showing {{ filteredBackups.length }} of {{ backups.length }} backups
                <button 
                  v-if="backupFilter.environment || backupFilter.source" 
                  @click="backupFilter.environment = ''; backupFilter.source = ''"
                  class="ml-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                >
                  Clear filters
                </button>
              </div>
              
              <!-- No Results Message -->
              <div v-if="filteredBackups.length === 0" class="text-center py-8">
                <i class="fas fa-search text-4xl text-gray-400 mb-4"></i>
                <p class="text-gray-600 dark:text-gray-400">No backups match your filter criteria</p>
                <button 
                  @click="backupFilter.environment = ''; backupFilter.source = ''"
                  class="mt-2 text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-200"
                >
                  Clear all filters
                </button>
              </div>
              
              <!-- Backup Items -->
              <div 
                v-for="backup in filteredBackups" 
                :key="backup.id" 
                class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="flex items-center flex-wrap gap-2 mb-2">
                      <h3 class="font-medium text-gray-900 dark:text-gray-100">
                        {{ backup.name || backup.backup_name }}
                      </h3>
                      
                      <!-- Environment Badge -->
                      <span 
                        v-if="backup.environment"
                        class="px-2 py-1 text-xs font-medium rounded-full"
                        :class="{
                          'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300': backup.environment === 'production',
                          'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300': backup.environment === 'development',
                          'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300': backup.environment === 'staging',
                          'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300': !['production', 'development', 'staging'].includes(backup.environment)
                        }"
                      >
                        <i class="fas fa-server mr-1 text-xs"></i>
                        {{ backup.environment.charAt(0).toUpperCase() + backup.environment.slice(1) }}
                      </span>
                      
                      <!-- Backup Type Badge -->
                      <span 
                        v-if="backup.backup_type && backup.backup_type !== 'full'"
                        class="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300"
                      >
                        <i class="fas fa-layer-group mr-1 text-xs"></i>
                        {{ backup.backup_type.replace('_', ' ').toUpperCase() }}
                      </span>
                      
                      <!-- CDN Provider Badge -->
                      <span 
                        v-if="backup.cdn_type" 
                        class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
                      >
                        <i class="fas fa-cloud mr-1 text-xs"></i>
                        {{ backup.cdn_type.toUpperCase() }}
                      </span>
                      
                      <!-- Source Badge -->
                      <span 
                        class="px-2 py-1 text-xs rounded-full"
                        :class="{
                          'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300': backup.source === 'cdn' && backup.is_cdn_direct,
                          'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300': backup.source === 'cdn' && !backup.is_cdn_direct,
                          'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300': backup.source === 'local'
                        }"
                      >
                        <i 
                          class="mr-1 text-xs"
                          :class="{
                            'fas fa-cloud-download-alt': backup.source === 'cdn' && backup.is_cdn_direct,
                            'fas fa-database': backup.source === 'cdn' && !backup.is_cdn_direct,
                            'fas fa-laptop': backup.source === 'local'
                          }"
                        ></i>
                        {{ backup.source_description || (backup.source === 'cdn' ? 'CDN' : 'Local') }}
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
    <div v-else-if="!isCheckingAdmin && !hasServerAdminAccess" class="text-center py-12">
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
            <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
              <div class="flex items-center">
                <i class="fas fa-database text-blue-600 dark:text-blue-400 mr-2"></i>
                <div>
                  <p class="text-sm font-medium text-blue-800 dark:text-blue-200">Unified Database Restore</p>
                  <p class="text-xs text-blue-700 dark:text-blue-300">Will restore the complete unified database including arrows, users, and configurations</p>
                </div>
              </div>
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
              :disabled="isRestoringBackup"
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

  <!-- Merge Duplicates Dialog -->
  <div v-if="showMergeDuplicatesDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          <i class="fas fa-layer-group mr-2 text-orange-600"></i>
          Merge Duplicate Arrows
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Select duplicate arrows to merge. Primary arrow (lowest ID) will be kept, duplicates will be consolidated.
        </p>
      </div>
      
      <div class="p-6 max-h-[60vh] overflow-y-auto">
        <!-- Select All Controls -->
        <div class="flex items-center justify-between mb-4 p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded">
          <div class="flex items-center space-x-3">
            <input
              type="checkbox"
              :checked="selectAllDuplicates"
              @change="toggleSelectAllDuplicates"
              class="w-4 h-4 text-orange-600 bg-gray-100 border-gray-300 rounded focus:ring-orange-500"
            />
            <label class="text-sm font-medium text-orange-800 dark:text-orange-200">
              Select All Duplicates ({{ duplicateIssues.length }} found)
            </label>
          </div>
          <div class="text-xs text-orange-700 dark:text-orange-300">
            {{ selectedDuplicates.size }} selected
          </div>
        </div>
        
        <!-- Duplicate Issues List -->
        <div class="space-y-3">
          <div 
            v-for="(issue, index) in duplicateIssues" 
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
            :class="{
              'bg-orange-50 dark:bg-orange-900/10 border-orange-300 dark:border-orange-700': selectedDuplicates.has(`${issue.arrow_id}_${issue.field}`),
              'bg-white dark:bg-gray-800': !selectedDuplicates.has(`${issue.arrow_id}_${issue.field}`)
            }"
          >
            <div class="flex items-start space-x-3">
              <input
                type="checkbox"
                :checked="selectedDuplicates.has(`${issue.arrow_id}_${issue.field}`)"
                @change="toggleDuplicateSelection(issue, $event.target.checked)"
                class="w-4 h-4 text-orange-600 bg-gray-100 border-gray-300 rounded focus:ring-orange-500 mt-1"
              />
              
              <div class="flex-1">
                <div class="flex items-center space-x-2 mb-2">
                  <span 
                    :class="{
                      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300': issue.severity === 'warning',
                      'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300': issue.severity === 'info'
                    }"
                    class="px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ issue.severity.toUpperCase() }}
                  </span>
                  <span class="text-xs text-gray-500 dark:text-gray-400">{{ issue.field }}</span>
                </div>
                
                <h6 class="font-medium text-gray-900 dark:text-gray-100 mb-1">
                  Arrow ID {{ issue.arrow_id }}: {{ issue.manufacturer }} {{ issue.model_name }}
                </h6>
                
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {{ issue.issue }}
                </p>
                
                <p class="text-xs text-orange-600 dark:text-orange-400 mb-3">
                  <i class="fas fa-lightbulb mr-1"></i>
                  {{ issue.suggested_fix }}
                </p>
                
                <!-- Not a Duplicate Action -->
                <div class="mt-2">
                  <CustomButton
                    @click="markNotDuplicate(issue, index)"
                    :disabled="issue.marking_not_duplicate"
                    variant="outlined"
                    size="small"
                    class="text-blue-600 border-blue-300 text-xs"
                  >
                    <i :class="issue.marking_not_duplicate ? 'fas fa-spinner fa-spin' : 'fas fa-times'" class="mr-1"></i>
                    {{ issue.marking_not_duplicate ? 'Marking...' : 'Not a Duplicate' }}
                  </CustomButton>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="duplicateIssues.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          <i class="fas fa-check-circle text-green-500 text-3xl mb-2"></i>
          <p>No duplicate arrows found!</p>
        </div>
      </div>
      
      <div class="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-between">
        <CustomButton
          @click="showMergeDuplicatesDialog = false"
          variant="outlined"
          class="text-gray-600 border-gray-300"
        >
          Cancel
        </CustomButton>
        
        <div class="space-x-3">
          <CustomButton
            @click="mergeSelectedDuplicates"
            :disabled="selectedDuplicates.size === 0 || validation.isExecutingMerge"
            variant="filled"
            class="bg-orange-600 text-white hover:bg-orange-700"
          >
            <i :class="validation.isExecutingMerge ? 'fas fa-spinner fa-spin' : 'fas fa-layer-group'" class="mr-2"></i>
            {{ validation.isExecutingMerge ? 'Merging...' : `Merge ${selectedDuplicates.size} Selected` }}
          </CustomButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import SpineChartLibrary from '~/components/admin/SpineChartLibrary.vue'

// Authentication check
const { user, token, isAdmin, checkAdminStatus, getAllUsers, setUserAdminStatus, updateUserStatus, deleteUser } = useAuth()

// Server-side admin verification
const hasServerAdminAccess = ref(false)
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

// Backup filtering
const backupFilter = ref({
  environment: '',
  source: ''
})

// Filtered backups computed property
const filteredBackups = computed(() => {
  let filtered = backups.value
  
  if (backupFilter.value.environment) {
    filtered = filtered.filter(backup => backup.environment === backupFilter.value.environment)
  }
  
  if (backupFilter.value.source) {
    filtered = filtered.filter(backup => backup.source === backupFilter.value.source)
  }
  
  return filtered
})

// Sorted migrations computed property  
const sortedMigrations = computed(() => {
  if (!migrationStatus.value?.migrations) return {}
  
  // Sort migrations by version number (treating them as numbers when possible)
  const entries = Object.entries(migrationStatus.value.migrations)
  entries.sort(([a], [b]) => {
    // Try to parse as numbers first
    const numA = parseInt(a)
    const numB = parseInt(b)
    
    if (!isNaN(numA) && !isNaN(numB)) {
      return numA - numB // Ascending numerical order
    }
    
    // Fallback to string comparison
    return a.localeCompare(b)
  })
  
  return Object.fromEntries(entries)
})

// System information state
const systemInfo = ref(null)
const isLoadingSystemInfo = ref(false)
const systemInfoError = ref(null)

const backupForm = ref({
  name: ''
  // Unified database - no separate options needed
})

const restoreForm = ref({
  // Unified database - no separate options needed
})

// Upload backup state
const selectedFile = ref(null)
const isUploadingBackup = ref(false)
const uploadForm = ref({
  // Unified database - no separate options needed
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

// Validation state
const validation = ref({
  isLoading: false,
  isGeneratingFixes: false,
  isExecutingFixes: false,
  isExecutingMerge: false,
  lastReport: null,
  sqlFixScript: null,
  executionResult: null
})

// Validation sorting and filtering
const validationSortBy = ref('severity')
const validationFilterSeverity = ref('')

// Merge duplicates state
const showMergeDuplicatesDialog = ref(false)
const selectedDuplicates = ref(new Set())
const selectAllDuplicates = ref(false)

// Computed property for duplicate issues
const hasDuplicateIssues = computed(() => {
  return validation.value.lastReport?.issues?.some(issue => issue.category === 'Duplicate Detection') || false
})

const duplicateIssues = computed(() => {
  return validation.value.lastReport?.issues?.filter(issue => issue.category === 'Duplicate Detection') || []
})

// Computed property for sorted and filtered validation issues
const sortedValidationIssues = computed(() => {
  if (!validation.value.lastReport?.issues) return []
  
  let issues = [...validation.value.lastReport.issues]
  
  // Apply severity filter
  if (validationFilterSeverity.value) {
    issues = issues.filter(issue => issue.severity === validationFilterSeverity.value)
  }
  
  // Define severity order for sorting
  const severityOrder = { critical: 0, warning: 1, info: 2 }
  
  // Apply sorting
  issues.sort((a, b) => {
    switch (validationSortBy.value) {
      case 'severity':
        // Critical first, then warning, then info
        const severityDiff = severityOrder[a.severity] - severityOrder[b.severity]
        if (severityDiff !== 0) return severityDiff
        // Secondary sort by arrow_id
        return a.arrow_id - b.arrow_id
        
      case 'category':
        const categoryDiff = a.category.localeCompare(b.category)
        if (categoryDiff !== 0) return categoryDiff
        // Secondary sort by severity
        return severityOrder[a.severity] - severityOrder[b.severity]
        
      case 'arrow_id':
        return a.arrow_id - b.arrow_id
        
      case 'manufacturer':
        const manufacturerDiff = (a.manufacturer || '').localeCompare(b.manufacturer || '')
        if (manufacturerDiff !== 0) return manufacturerDiff
        // Secondary sort by arrow_id
        return a.arrow_id - b.arrow_id
        
      default:
        return 0
    }
  })
  
  return issues
})

// Maintenance state
const migrationStatus = ref(null)
const showAllMigrations = ref(false)
const databaseHealth = ref(null)
const isOptimizing = ref(false)
const isVacuuming = ref(false)
const isVerifying = ref(false)
const schemaVerification = ref(null)
const lastMaintenanceResults = ref([])

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
  if (!hasServerAdminAccess.value) return
  
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
    const newStatus = user.status === 'suspended' ? 'active' : 'suspended'
    await updateUserStatus(user.id, newStatus)
    
    user.status = newStatus
    updateStats()
    showNotification(`User ${newStatus === 'active' ? 'reactivated' : 'suspended'} successfully`, 'success')
  } catch (error) {
    console.error('Error updating user status:', error)
    showNotification('Failed to update user status: ' + error.message, 'error')
  }
}


const deleteUserHandler = async (user) => {
  showConfirmation(
    `Are you sure you want to delete ${user.name || user.email}?`,
    async () => {
      try {
        await deleteUser(user.id)
        
        const index = users.value.findIndex(u => u.id === user.id)
        if (index !== -1) {
          users.value.splice(index, 1)
        }
        updateStats()
        showNotification(`Successfully deleted ${user.name || user.email}`, 'success')
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
    'pending': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300', // Change pending to blue (no approval needed)
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
  if (!hasServerAdminAccess.value) return
  
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
  if (!hasServerAdminAccess.value) return
  
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
      backup_name: backupForm.value.name || undefined
      // Unified database - no separate options needed
    })
    
    showNotification(result.message || 'Backup created successfully')
    
    // Reset form
    backupForm.value = {
      name: ''
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
  
  // With unified database, all backups contain the complete database
  // No need for separate detection or options
  restoreForm.value = {
    // Unified database - no separate options needed
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
      force: true
      // Unified database - no separate options needed
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
  // With unified database, all backups contain the complete database
  return 'Unified Database'
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
  
  // With unified database, no validation needed for separate databases
  
  try {
    isUploadingBackup.value = true
    
    // Create FormData for file upload
    const formData = new FormData()
    formData.append('backup_file', selectedFile.value)
    formData.append('force_restore', 'true')
    // Unified database - no separate options needed
    
    console.log('Uploading unified backup file:', selectedFile.value.name)
    
    // Upload and restore
    const result = await api.post('/admin/backup/upload', formData)
    
    showNotification(result.message || 'Backup uploaded and restored successfully', 'success')
    
    // Reset form
    selectedFile.value = null
    uploadForm.value = {
      // Unified database - no separate options needed
    }
    
    // Clear file input
    if (process.client) {
      const fileInput = document.querySelector('input[type="file"]')
      if (fileInput) fileInput.value = ''
    }
    
    // Reload backups list
    await loadBackups()
    
    // Show additional warning for unified database restore
    showNotification('Unified database restored. You may need to refresh the page.', 'warning')
    
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
      hasServerAdminAccess.value = adminStatus
      
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
      hasServerAdminAccess.value = false
    }
  } catch (error) {
    console.error('Error checking admin status:', error)
    hasServerAdminAccess.value = false
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

// Arrow Data Validation Methods
const runValidation = async () => {
  validation.value.isLoading = true
  validation.value.lastReport = null
  validation.value.sqlFixScript = null
  
  try {
    const response = await api.get('/admin/validate-arrows')
    validation.value.lastReport = response
    
    // Show detailed validation summary
    const { total_issues, health_score } = response
    showNotification(`Validation complete: ${total_issues} issues found (Health: ${health_score}%)`, 'success')
  } catch (error) {
    console.error('Error running validation:', error)
    showNotification('Failed to run validation: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    validation.value.isLoading = false
  }
}

const generateSqlFixes = async () => {
  validation.value.isGeneratingFixes = true
  
  try {
    const response = await api.get('/admin/validate-arrows/sql-fix')
    validation.value.sqlFixScript = response.sql_script
    
    showNotification('SQL fix script generated successfully', 'success')
  } catch (error) {
    console.error('Error generating SQL fixes:', error)
    showNotification('Failed to generate SQL fixes: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    validation.value.isGeneratingFixes = false
  }
}

const clearValidationResults = () => {
  validation.value.lastReport = null
  validation.value.sqlFixScript = null
  selectedDuplicates.value.clear()
  selectAllDuplicates.value = false
}

// Merge duplicates methods
const toggleDuplicateSelection = (issue, isSelected) => {
  if (isSelected) {
    selectedDuplicates.value.add(`${issue.arrow_id}_${issue.field}`)
  } else {
    selectedDuplicates.value.delete(`${issue.arrow_id}_${issue.field}`)
  }
}

const toggleSelectAllDuplicates = () => {
  if (selectAllDuplicates.value) {
    selectedDuplicates.value.clear()
  } else {
    duplicateIssues.value.forEach(issue => {
      selectedDuplicates.value.add(`${issue.arrow_id}_${issue.field}`)
    })
  }
  selectAllDuplicates.value = !selectAllDuplicates.value
}

const mergeSelectedDuplicates = async () => {
  if (selectedDuplicates.value.size === 0) {
    showNotification('No duplicates selected for merging', 'warning')
    return
  }
  
  validation.value.isExecutingMerge = true
  
  try {
    const response = await api.post('/admin/validate-arrows/merge-duplicates')
    
    showNotification(`Successfully merged ${response.merged_count} duplicate arrows`, 'success')
    
    // Clear selections and refresh validation
    selectedDuplicates.value.clear()
    selectAllDuplicates.value = false
    showMergeDuplicatesDialog.value = false
    
    // Re-run validation to see updated results
    await runValidation()
    
  } catch (error) {
    console.error('Error merging duplicates:', error)
    showNotification('Failed to merge duplicates: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    validation.value.isExecutingMerge = false
  }
}

const copySqlScript = async () => {
  if (validation.value.sqlFixScript) {
    try {
      await navigator.clipboard.writeText(validation.value.sqlFixScript)
      showNotification('SQL script copied to clipboard', 'success')
    } catch (error) {
      console.error('Error copying to clipboard:', error)
      showNotification('Failed to copy script to clipboard', 'error')
    }
  }
}

const executeSqlFixes = async () => {
  if (!validation.value.sqlFixScript) {
    showNotification('No SQL fixes available', 'error')
    return
  }

  // Confirm execution
  const confirmed = confirm(
    'This will create a backup and execute SQL fixes to resolve arrow data issues. Continue?'
  )
  
  if (!confirmed) return

  validation.value.isExecutingFixes = true
  validation.value.executionResult = null

  try {
    const response = await api.post('/admin/validate-arrows/execute-fixes')
    validation.value.executionResult = response
    
    showNotification(
      `Successfully applied ${response.fixes_applied} fixes. Issues reduced from ${response.before_issues} to ${response.after_issues}.`,
      'success'
    )
    
    // Clear the script since fixes have been applied
    validation.value.sqlFixScript = null
    
    // Optionally re-run validation to show updated status
    setTimeout(() => {
      runValidation()
    }, 1000)
    
  } catch (error) {
    console.error('Error executing SQL fixes:', error)
    showNotification('Failed to execute SQL fixes: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    validation.value.isExecutingFixes = false
  }
}

const executeIndividualFix = async (issue, index) => {
  if (!issue.sql_fix || issue.sql_fix.startsWith('--')) {
    showNotification('No executable SQL fix available for this issue', 'error')
    return
  }

  // Auto-execute without confirmation prompt

  // Set executing state for this specific issue
  validation.value.lastReport.issues[index].executing = true

  try {
    const response = await api.post('/admin/execute-sql', {
      sql: issue.sql_fix,
      description: `Fix for Arrow ID ${issue.arrow_id}: ${issue.issue}`
    })
    
    if (response.success) {
      showNotification(`Successfully fixed Arrow ID ${issue.arrow_id}`, 'success')
      
      // Remove this issue from the list since it's been fixed
      validation.value.lastReport.issues.splice(index, 1)
      validation.value.lastReport.critical_issues = validation.value.lastReport.issues.filter(i => i.severity === 'critical').length
      validation.value.lastReport.warning_issues = validation.value.lastReport.issues.filter(i => i.severity === 'warning').length
      validation.value.lastReport.info_issues = validation.value.lastReport.issues.filter(i => i.severity === 'info').length
    } else {
      showNotification('Failed to execute fix: ' + (response.error || 'Unknown error'), 'error')
    }
  } catch (error) {
    console.error('Error executing individual fix:', error)
    showNotification('Failed to execute fix: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    validation.value.lastReport.issues[index].executing = false
  }
}

const executeManualFix = async (issue, index) => {
  if (!issue.manual_value || issue.manual_value.trim() === '') {
    showNotification('Please enter a value to update', 'error')
    return
  }

  let sql = ''
  const newValue = issue.manual_value.trim()

  // Generate appropriate SQL based on the field and table structure
  if (issue.field === 'spine') {
    sql = `UPDATE spine_specifications SET spine = '${newValue}' WHERE arrow_id = ${issue.arrow_id};`
  } else if (['length_options', 'outer_diameter', 'gpi_weight'].includes(issue.field)) {
    sql = `UPDATE spine_specifications SET ${issue.field} = '${newValue}' WHERE arrow_id = ${issue.arrow_id};`
  } else {
    sql = `UPDATE arrows SET ${issue.field} = '${newValue}' WHERE id = ${issue.arrow_id};`
  }

  const confirmed = confirm(
    `Update ${issue.field} to "${newValue}" for Arrow ID ${issue.arrow_id}?\n\nThis will run: ${sql}`
  )
  
  if (!confirmed) return

  // Set executing state for this specific issue
  validation.value.lastReport.issues[index].executing = true

  try {
    const response = await api.post('/admin/execute-sql', {
      sql: sql,
      description: `Manual update for Arrow ID ${issue.arrow_id}: ${issue.field} = ${newValue}`
    })
    
    if (response.success) {
      showNotification(`Successfully updated ${issue.field} for Arrow ID ${issue.arrow_id}`, 'success')
      
      // Update the current value and clear manual input
      validation.value.lastReport.issues[index].current_value = newValue
      validation.value.lastReport.issues[index].manual_value = ''
      
      // If this was a formatting fix, remove the issue
      if (issue.category === 'Data Field Formatting' || issue.category === 'Spine Data Quality') {
        validation.value.lastReport.issues.splice(index, 1)
        validation.value.lastReport.critical_issues = validation.value.lastReport.issues.filter(i => i.severity === 'critical').length
        validation.value.lastReport.warning_issues = validation.value.lastReport.issues.filter(i => i.severity === 'warning').length
        validation.value.lastReport.info_issues = validation.value.lastReport.issues.filter(i => i.severity === 'info').length
      }
    } else {
      showNotification('Failed to execute manual update: ' + (response.error || 'Unknown error'), 'error')
    }
  } catch (error) {
    console.error('Error executing manual fix:', error)
    showNotification('Failed to execute manual update: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    validation.value.lastReport.issues[index].executing = false
  }
}

const copyIndividualSql = async (sqlFix) => {
  try {
    await navigator.clipboard.writeText(sqlFix)
    showNotification('SQL fix copied to clipboard', 'success')
  } catch (error) {
    console.error('Error copying to clipboard:', error)
    showNotification('Failed to copy SQL to clipboard', 'error')
  }
}

const markNotDuplicate = async (issue, index) => {
  const confirmed = confirm(
    `Mark this as NOT a duplicate?\n\n` +
    `Arrow ID ${issue.arrow_id}: ${issue.manufacturer} ${issue.model_name}\n` +
    `Issue: ${issue.issue}\n\n` +
    `This will exclude this pair from future duplicate detection.`
  )
  
  if (!confirmed) return

  // Set loading state
  validation.value.lastReport.issues[index].marking_not_duplicate = true

  try {
    const response = await api.post('/admin/validation/mark-not-duplicate', {
      arrow_id: issue.arrow_id,
      field: issue.field,
      issue_hash: issue.issue_hash || `${issue.arrow_id}_${issue.field}`,
      reason: `User marked as not duplicate: ${issue.issue}`
    })
    
    if (response.success) {
      showNotification(`Arrow ID ${issue.arrow_id} marked as not a duplicate`, 'success')
      
      // Remove this issue from the duplicate list
      validation.value.lastReport.issues.splice(index, 1)
      
      // Update issue counts
      validation.value.lastReport.critical_issues = validation.value.lastReport.issues.filter(i => i.severity === 'critical').length
      validation.value.lastReport.warning_issues = validation.value.lastReport.issues.filter(i => i.severity === 'warning').length
      validation.value.lastReport.info_issues = validation.value.lastReport.issues.filter(i => i.severity === 'info').length
      
    } else {
      showNotification('Failed to mark as not duplicate: ' + (response.error || 'Unknown error'), 'error')
    }
  } catch (error) {
    console.error('Error marking not duplicate:', error)
    showNotification('Failed to mark as not duplicate: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    validation.value.lastReport.issues[index].marking_not_duplicate = false
  }
}

// Maintenance functions
const refreshMigrationStatus = async () => {
  try {
    const data = await api.get('/admin/migrations/status')
    migrationStatus.value = data
  } catch (error) {
    console.error('Error fetching migration status:', error)
    showNotification('Failed to fetch migration status', 'error')
  }
}

const runMigrations = async (dryRun = false) => {
  try {
    const data = await api.post('/admin/migrations/run', { dry_run: dryRun })
    
    if (data.success) {
      showNotification(data.message, 'success')
      await refreshMigrationStatus() // Refresh status after running migrations
    } else {
      showNotification(data.error || 'Migration failed', 'error')
    }
  } catch (error) {
    console.error('Error running migrations:', error)
    showNotification('Failed to run migrations', 'error')
  }
}

const refreshDatabaseHealth = async () => {
  try {
    const data = await api.get('/admin/database/health')
    databaseHealth.value = data
  } catch (error) {
    console.error('Error fetching database health:', error)
    showNotification('Failed to fetch database health', 'error')
  }
}

const optimizeDatabase = async () => {
  isOptimizing.value = true
  try {
    const data = await api.post('/admin/database/optimize')
    
    if (data.success) {
      const result = {
        operation: 'Database Optimization',
        message: data.message,
        success: true,
        timestamp: new Date().toISOString()
      }
      lastMaintenanceResults.value.unshift(result)
      
      showNotification(data.message, 'success')
      await refreshDatabaseHealth() // Refresh health after optimization
    } else {
      const result = {
        operation: 'Database Optimization',
        message: data.error || 'Optimization failed',
        success: false,
        timestamp: new Date().toISOString()
      }
      lastMaintenanceResults.value.unshift(result)
      
      showNotification(data.error || 'Optimization failed', 'error')
    }
  } catch (error) {
    console.error('Error optimizing database:', error)
    
    const result = {
      operation: 'Database Optimization',
      message: 'Failed to optimize database',
      success: false,
      timestamp: new Date().toISOString()
    }
    lastMaintenanceResults.value.unshift(result)
    
    showNotification('Failed to optimize database', 'error')
  } finally {
    isOptimizing.value = false
  }
}

const vacuumDatabase = async () => {
  isVacuuming.value = true
  try {
    const data = await api.post('/admin/database/vacuum')
    
    if (data.success) {
      const result = {
        operation: 'VACUUM Database',
        message: `${data.message}. Reclaimed: ${data.space_reclaimed_mb}MB`,
        success: true,
        timestamp: new Date().toISOString()
      }
      lastMaintenanceResults.value.unshift(result)
      
      showNotification(`${data.message}. Reclaimed ${data.space_reclaimed_mb}MB`, 'success')
      await refreshDatabaseHealth() // Refresh health after vacuum
    } else {
      const result = {
        operation: 'VACUUM Database',
        message: data.error || 'VACUUM failed',
        success: false,
        timestamp: new Date().toISOString()
      }
      lastMaintenanceResults.value.unshift(result)
      
      showNotification(data.error || 'VACUUM failed', 'error')
    }
  } catch (error) {
    console.error('Error running VACUUM:', error)
    
    const result = {
      operation: 'VACUUM Database',
      message: 'Failed to run VACUUM',
      success: false,
      timestamp: new Date().toISOString()
    }
    lastMaintenanceResults.value.unshift(result)
    
    showNotification('Failed to run VACUUM', 'error')
  } finally {
    isVacuuming.value = false
  }
}

const verifySchema = async () => {
  isVerifying.value = true
  try {
    const data = await api.get('/admin/database/schema-verify')
    
    // Store complete verification results for display
    schemaVerification.value = data
    
    // Enhanced result message based on architecture type
    let message = 'Schema verification completed'
    if (data.architecture_type === 'unified') {
      if (data.unified_schema_valid) {
        message = 'Unified database schema is complete and valid'
      } else {
        message = `Unified schema incomplete - ${(data.missing_tables?.length || 0) + (data.missing_columns?.length || 0)} issues found`
      }
    } else if (data.architecture_type === 'separate') {
      if (data.separate_schema_valid) {
        message = 'Separate database schema is valid'
      } else {
        message = `Separate schema issues - ${(data.missing_tables?.length || 0) + (data.missing_columns?.length || 0)} problems found`
      }
    } else {
      message = `Schema verification completed - architecture: ${data.architecture_type || 'unknown'}`
    }
    
    const result = {
      operation: 'Schema Verification',
      message: message,
      success: data.schema_valid,
      timestamp: new Date().toISOString()
    }
    lastMaintenanceResults.value.unshift(result)
    
    // Enhanced notifications
    if (data.schema_valid) {
      if (data.architecture_type === 'unified' && data.unified_schema_valid) {
        showNotification('✅ Unified database schema is complete and valid', 'success')
      } else {
        showNotification('✅ Database schema is valid', 'success')
      }
    } else {
      const totalIssues = (data.missing_tables?.length || 0) + (data.missing_columns?.length || 0)
      showNotification(`⚠️ Schema issues found: ${totalIssues} problems detected`, 'warning')
    }
  } catch (error) {
    console.error('Error verifying schema:', error)
    
    // Clear verification results on error
    schemaVerification.value = null
    
    const result = {
      operation: 'Schema Verification',
      message: 'Failed to verify schema',
      success: false,
      timestamp: new Date().toISOString()
    }
    lastMaintenanceResults.value.unshift(result)
    
    showNotification('❌ Failed to verify schema', 'error')
  } finally {
    isVerifying.value = false
  }
}

// Watch for user changes
watch(user, () => {
  if (user.value) {
    checkAndLoadAdminData()
  } else {
    hasServerAdminAccess.value = false
    isCheckingAdmin.value = false
  }
})

// Watch for tab changes to load data as needed
watch(activeTab, async (newTab) => {
  if (newTab === 'backups' && hasServerAdminAccess.value && backups.value.length === 0) {
    await loadBackups()
  }
  if (newTab === 'system' && hasServerAdminAccess.value && !systemInfo.value) {
    await loadSystemInfo()
  }
  if (newTab === 'datatools' && hasServerAdminAccess.value && manufacturers.value.length === 0) {
    await loadManufacturersList()
  }
  if (newTab === 'maintenance' && isAdmin.value) {
    if (!migrationStatus.value) {
      await refreshMigrationStatus()
    }
    if (!databaseHealth.value) {
      await refreshDatabaseHealth()
    }
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
  middleware: ['auth-check', 'admin']
})
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
</style>