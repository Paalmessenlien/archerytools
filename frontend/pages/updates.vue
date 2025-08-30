<template>
  <div>
    <!-- Page Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Platform Updates</h1>
          <p class="text-gray-600 dark:text-gray-300">Recent development activity and changes</p>
        </div>
        <div class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <i class="fas fa-code-branch"></i>
          <span>Latest {{ commits?.length || 0 }} commits</span>
        </div>
      </div>
    </div>

    <!-- Info Banner -->
    <div class="mb-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-info-circle text-blue-600 dark:text-blue-400 mr-3"></i>
        <div>
          <h4 class="text-sm font-medium text-blue-800 dark:text-blue-200">Development Updates</h4>
          <p class="text-xs text-blue-700 dark:text-blue-300 mt-1">
            Track the latest improvements, bug fixes, and new features added to the platform
          </p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !commits" class="flex items-center justify-center py-12">
      <div class="flex items-center space-x-3">
        <div class="w-6 h-6 border-b-2 border-blue-600 rounded-full animate-spin dark:border-purple-400"></div>
        <span class="text-gray-600 dark:text-gray-300">Loading recent commits...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
      <div class="flex items-center">
        <i class="fas fa-exclamation-circle text-red-600 dark:text-red-400 mr-3"></i>
        <div>
          <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Failed to load commits</h3>
          <p class="text-xs text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Commits Timeline -->
    <div v-else-if="commits && commits.length > 0" class="space-y-4">
      <div 
        v-for="(commit, index) in commits" 
        :key="commit.hash"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 transition-all duration-200 hover:shadow-md"
      >
        <div class="flex items-start space-x-4">
          <!-- Commit Icon -->
          <div class="flex-shrink-0 mt-1">
            <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
              <i class="fas fa-code-branch text-blue-600 dark:text-blue-400 text-sm"></i>
            </div>
          </div>
          
          <!-- Commit Details -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="text-gray-900 dark:text-gray-100 font-medium leading-relaxed">
                  {{ formatCommitMessage(commit.message) }}
                </p>
                <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                  <span class="flex items-center">
                    <i class="fas fa-user mr-1"></i>
                    {{ commit.author }}
                  </span>
                  <span class="flex items-center">
                    <i class="fas fa-clock mr-1"></i>
                    {{ commit.relative_time }}
                  </span>
                  <span class="flex items-center font-mono text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    <i class="fas fa-hashtag mr-1"></i>
                    {{ commit.hash }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Commit Type Badge -->
            <div class="mt-3">
              <span 
                :class="getCommitTypeBadgeClass(commit.message)"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              >
                {{ getCommitType(commit.message) }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Load More Info -->
      <div class="text-center py-4">
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Showing latest {{ commits.length }} commits. 
          <a href="https://github.com/Paalmessenlien/archerytools" target="_blank" rel="noopener noreferrer" 
             class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors">
            View full history on GitHub
            <i class="fas fa-external-link-alt ml-1 text-xs"></i>
          </a>
        </p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <i class="fas fa-code-branch text-gray-400 dark:text-gray-500 text-4xl mb-4"></i>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No commits found</h3>
      <p class="text-gray-500 dark:text-gray-400">Unable to load recent development activity</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Set page title
useHead({
  title: 'Platform Updates',
  meta: [
    { name: 'description', content: 'Recent development updates and changes to the ArcheryTool platform' }
  ]
})

// Reactive data
const commits = ref([])
const loading = ref(false)
const error = ref(null)

// API composable
const api = useApi()

// Fetch git commits
const fetchCommits = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await api.get('/git/commits')
    
    commits.value = response.commits || []
    
  } catch (err) {
    console.error('Failed to fetch commits:', err)
    error.value = err.message || 'Failed to load commit history'
  } finally {
    loading.value = false
  }
}

// Format commit message for display
const formatCommitMessage = (message: string) => {
  // Remove emoji prefixes and clean up message
  return message.replace(/^[^\w\s]+[\s]*/, '').trim()
}

// Get commit type from message
const getCommitType = (message: string) => {
  if (message.startsWith('🔧')) return 'Fix'
  if (message.startsWith('🏹')) return 'Feature'
  if (message.startsWith('📚')) return 'Documentation'
  if (message.startsWith('🔐')) return 'Security'
  if (message.startsWith('🗃️')) return 'Database'
  if (message.startsWith('🎨')) return 'UI/UX'
  if (message.startsWith('⚡')) return 'Performance'
  if (message.startsWith('🚀')) return 'Deploy'
  if (message.startsWith('🧪')) return 'Testing'
  return 'Update'
}

// Get badge styling for commit type
const getCommitTypeBadgeClass = (message: string) => {
  const type = getCommitType(message)
  
  const classes: Record<string, string> = {
    'Fix': 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-200',
    'Feature': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-200',
    'Documentation': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-200',
    'Security': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-200',
    'Database': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200',
    'UI/UX': 'bg-pink-100 text-pink-800 dark:bg-pink-900/20 dark:text-pink-200',
    'Performance': 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-200',
    'Deploy': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-200',
    'Testing': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/20 dark:text-cyan-200',
    'Update': 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-200'
  }
  
  return classes[type] || classes['Update']
}

// Lifecycle
onMounted(() => {
  fetchCommits()
})
</script>

<style scoped>
/* Custom timeline styles */
.commit-timeline::before {
  content: '';
  position: absolute;
  left: 1rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: theme('colors.gray.200');
}

.dark .commit-timeline::before {
  background: theme('colors.gray.700');
}
</style>