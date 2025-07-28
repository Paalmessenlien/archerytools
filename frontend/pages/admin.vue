<template>
  <div>
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
      <p class="text-gray-600 dark:text-gray-300">Manage beta access and user permissions</p>
    </div>

    <!-- Admin Dashboard -->
    <div v-if="isAdmin" class="space-y-6">
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
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

// Authentication check
const { user, token, checkAdminStatus, getAllUsers, setUserAdminStatus } = useAuth()

// Check if user is admin
const isAdmin = ref(false)

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

// User management functions
const toggleAdminStatus = async (user) => {
  try {
    const newAdminStatus = !user.is_admin
    const confirmation = confirm(`Are you sure you want to ${newAdminStatus ? 'grant admin access to' : 'remove admin access from'} ${user.name || user.email}?`)
    
    if (confirmation) {
      await setUserAdminStatus(user.id, newAdminStatus)
      user.is_admin = newAdminStatus
    }
  } catch (error) {
    console.error('Error updating admin status:', error)
    alert('Failed to update admin status: ' + error.message)
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
  if (confirm(`Are you sure you want to delete ${user.name || user.email}?`)) {
    try {
      // TODO: Implement API call
      // await api.deleteUser(user.id)
      
      const index = users.value.findIndex(u => u.id === user.id)
      if (index !== -1) {
        users.value.splice(index, 1)
      }
      updateStats()
    } catch (error) {
      console.error('Error deleting user:', error)
    }
  }
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

// Check admin status and load data
const checkAndLoadAdminData = async () => {
  try {
    console.log('checkAndLoadAdminData called, user:', user.value)
    if (user.value) {
      console.log('User exists, calling checkAdminStatus...')
      const adminStatus = await checkAdminStatus()
      console.log('Admin status result:', adminStatus)
      isAdmin.value = adminStatus
      
      if (adminStatus) {
        console.log('User is admin, loading users...')
        await loadUsers()
      } else {
        console.log('User is not admin')
      }
    } else {
      console.log('No user found')
    }
  } catch (error) {
    console.error('Error checking admin status:', error)
    isAdmin.value = false
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