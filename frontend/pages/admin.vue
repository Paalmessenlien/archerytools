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
      </nav>
    </div>

    <!-- Loading State -->
    <div v-if="isCheckingAdmin" class="text-center py-12">
      <i class="fas fa-spinner fa-spin text-4xl text-indigo-600 mb-4"></i>
      <h2 class="text-xl font-medium text-gray-900 dark:text-gray-100 mb-2">Checking Access...</h2>
      <p class="text-gray-600 dark:text-gray-400">Verifying your admin privileges</p>
    </div>

    <!-- Admin Dashboard -->
    <div v-else-if="isAdmin" class="space-y-6">
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
                      <span class="ml-2 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                        {{ backup.cdn_type.toUpperCase() }}
                      </span>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <div>
                        <i class="fas fa-calendar-alt mr-1"></i>
                        {{ formatDate(backup.created_at) }}
                      </div>
                      <div>
                        <i class="fas fa-weight-hanging mr-1"></i>
                        {{ backup.file_size_mb.toFixed(2) }} MB
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
    <div v-else class="text-center py-12">
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
              <label v-if="backupToRestore?.include_arrow_db" class="flex items-center">
                <input 
                  v-model="restoreForm.restoreArrowDb" 
                  type="checkbox" 
                  class="mr-2"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">Arrow Database</span>
              </label>
              <label v-if="backupToRestore?.include_user_db" class="flex items-center">
                <input 
                  v-model="restoreForm.restoreUserDb" 
                  type="checkbox" 
                  class="mr-2"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">User Database</span>
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

// Backup management state
const backups = ref([])
const isLoadingBackups = ref(false)
const isCreatingBackup = ref(false)
const isRestoringBackup = ref(false)
const showRestoreBackupModal = ref(false)
const backupToRestore = ref(null)

const backupForm = ref({
  name: '',
  includeArrowDb: true,
  includeUserDb: true
})

const restoreForm = ref({
  restoreArrowDb: true,
  restoreUserDb: false
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

// Backup management functions
const loadBackups = async () => {
  if (!isAdmin.value) return
  
  try {
    isLoadingBackups.value = true
    const response = await api.get('/admin/backups')
    
    // Combine CDN backups (primary) with local backups for completeness
    backups.value = response.cdn_backups || []
    
    console.log(`Loaded ${backups.value.length} backups`)
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
  backupToRestore.value = backup
  
  // Set default restore options based on what backup contains
  restoreForm.value = {
    restoreArrowDb: backup.include_arrow_db,
    restoreUserDb: false // Default to false for safety
  }
  
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
    
    // Open CDN URL in new window for download
    if (response.cdn_url) {
      window.open(response.cdn_url, '_blank')
      showNotification('Download started')
    } else {
      showNotification('Download URL not available', 'error')
    }
  } catch (error) {
    console.error('Error downloading backup:', error)
    showNotification('Failed to get download URL: ' + error.message, 'error')
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
  if (backup.include_arrow_db) contents.push('Arrows')
  if (backup.include_user_db) contents.push('Users')
  return contents.join(', ') || 'Unknown'
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