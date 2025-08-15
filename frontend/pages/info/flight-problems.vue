<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-6">
      <!-- Header -->
      <div class="mb-6">
        <nav class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
          <NuxtLink to="/info" class="hover:text-blue-600 dark:hover:text-blue-400">
            Information Center
          </NuxtLink>
          <i class="fas fa-chevron-right"></i>
          <span class="text-gray-900 dark:text-white">Flight Problems</span>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Arrow Flight Problems
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Comprehensive diagnostic guide for identifying and solving arrow flight issues
        </p>
      </div>

      <!-- Quick Diagnostic Tool -->
      <div class="bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800 p-6 mb-8">
        <h2 class="text-xl font-semibold text-yellow-800 dark:text-yellow-200 mb-4">
          <i class="fas fa-search mr-2"></i>
          Quick Problem Finder
        </h2>
        <p class="text-yellow-700 dark:text-yellow-300 mb-4">
          Select your arrow's behavior to get instant diagnostic guidance:
        </p>
        <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <button
            v-for="problem in quickProblems"
            :key="problem.id"
            @click="selectedProblem = problem.id"
            :class="[
              'p-3 rounded-lg border text-left transition-all',
              selectedProblem === problem.id
                ? 'border-yellow-500 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
                : 'border-yellow-300 dark:border-yellow-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:border-yellow-400 dark:hover:border-yellow-600'
            ]"
          >
            <div class="font-medium">{{ problem.name }}</div>
            <div class="text-xs text-gray-600 dark:text-gray-400">{{ problem.description }}</div>
          </button>
        </div>
      </div>

      <!-- Problem Diagnosis Sections -->
      <div class="space-y-8">
        
        <!-- Paper Tuning Tears -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            <i class="fas fa-file-alt text-blue-600 dark:text-blue-400 mr-3"></i>
            Paper Tuning Tears
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <!-- Left/Right Tears -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Left/Right Tears
              </h3>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-arrow-left mr-2"></i>
                    Left Tear (Arrow flying left)
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p><strong>Causes:</strong></p>
                    <ul class="list-disc list-inside ml-2 space-y-1">
                      <li>Arrow spine too weak (under-spined)</li>
                      <li>Rest position too far left</li>
                      <li>Draw weight too high for arrow</li>
                      <li>Point weight too light</li>
                    </ul>
                    <p class="mt-2"><strong>Solutions:</strong></p>
                    <ul class="list-disc list-inside ml-2 space-y-1">
                      <li>Move rest 1/32" to the right</li>
                      <li>Increase point weight by 25-50 grains</li>
                      <li>Use stiffer spine arrow</li>
                      <li>Reduce draw weight if possible</li>
                    </ul>
                  </div>
                </div>

                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
                    <i class="fas fa-arrow-right mr-2"></i>
                    Right Tear (Arrow flying right)
                  </h4>
                  <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
                    <p><strong>Causes:</strong></p>
                    <ul class="list-disc list-inside ml-2 space-y-1">
                      <li>Arrow spine too stiff (over-spined)</li>
                      <li>Rest position too far right</li>
                      <li>Point weight too heavy</li>
                      <li>Draw weight too low for arrow</li>
                    </ul>
                    <p class="mt-2"><strong>Solutions:</strong></p>
                    <ul class="list-disc list-inside ml-2 space-y-1">
                      <li>Move rest 1/32" to the left</li>
                      <li>Reduce point weight by 25-50 grains</li>
                      <li>Use weaker spine arrow</li>
                      <li>Increase draw weight if possible</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- High/Low Tears -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                High/Low Tears
              </h3>
              
              <div class="space-y-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-arrow-up mr-2"></i>
                    High Tear (Arrow flying high)
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p><strong>Causes:</strong></p>
                    <ul class="list-disc list-inside ml-2 space-y-1">
                      <li>Nocking point too low</li>
                      <li>Arrow rest too low</li>
                      <li>Weak arrow release</li>
                      <li>Bow grip issues</li>
                    </ul>
                    <p class="mt-2"><strong>Solutions:</strong></p>
                    <ul class="list-disc list-inside ml-2 space-y-1">
                      <li>Raise nocking point 1/16"</li>
                      <li>Raise arrow rest height</li>
                      <li>Check release technique</li>
                      <li>Verify consistent bow grip</li>
                    </ul>
                  </div>
                </div>

                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    <i class="fas fa-arrow-down mr-2"></i>
                    Low Tear (Arrow flying low)
                  </h4>
                  <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                    <p><strong>Causes:</strong></p>
                    <ul class="list-disc list-inside ml-2 space-y-1">
                      <li>Nocking point too high</li>
                      <li>Arrow rest too high</li>
                      <li>Excessive draw weight</li>
                      <li>Form inconsistencies</li>
                    </ul>
                    <p class="mt-2"><strong>Solutions:</strong></p>
                    <ul class="list-disc list-inside ml-2 space-y-1">
                      <li>Lower nocking point 1/16"</li>
                      <li>Lower arrow rest height</li>
                      <li>Check shooting form</li>
                      <li>Ensure proper anchor point</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Group Problems -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            <i class="fas fa-bullseye text-green-600 dark:text-green-400 mr-3"></i>
            Grouping Issues
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-3">
            <!-- Erratic Grouping -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Erratic Grouping
              </h3>
              <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">
                  Random arrow impacts
                </h4>
                <div class="text-sm text-orange-700 dark:text-orange-400 space-y-2">
                  <p><strong>Common Causes:</strong></p>
                  <ul class="list-disc list-inside ml-2 space-y-1">
                    <li>Inconsistent shooting form</li>
                    <li>Poor arrow rest clearance</li>
                    <li>Damaged arrows or fletching</li>
                    <li>Inconsistent release</li>
                    <li>Bow torque issues</li>
                  </ul>
                  <p class="mt-2"><strong>Check List:</strong></p>
                  <ul class="list-disc list-inside ml-2 space-y-1">
                    <li>Arrow condition (straightness, fletching)</li>
                    <li>Rest alignment and clearance</li>
                    <li>Shooting form consistency</li>
                    <li>Release technique</li>
                    <li>Bow grip pressure</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Vertical Stringing -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Vertical Stringing
              </h3>
              <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                  Arrows grouping vertically
                </h4>
                <div class="text-sm text-purple-700 dark:text-purple-400 space-y-2">
                  <p><strong>Primary Causes:</strong></p>
                  <ul class="list-disc list-inside ml-2 space-y-1">
                    <li>Inconsistent anchor point</li>
                    <li>Varying draw length</li>
                    <li>Release timing issues</li>
                    <li>Nocking point problems</li>
                  </ul>
                  <p class="mt-2"><strong>Solutions:</strong></p>
                  <ul class="list-disc list-inside ml-2 space-y-1">
                    <li>Practice consistent anchor</li>
                    <li>Use back tension release</li>
                    <li>Check nocking point height</li>
                    <li>Verify draw length setting</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Horizontal Stringing -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Horizontal Stringing
              </h3>
              <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
                <h4 class="font-medium text-teal-800 dark:text-teal-300 mb-2">
                  Arrows grouping horizontally
                </h4>
                <div class="text-sm text-teal-700 dark:text-teal-400 space-y-2">
                  <p><strong>Primary Causes:</strong></p>
                  <ul class="list-disc list-inside ml-2 space-y-1">
                    <li>Bow torque/grip pressure</li>
                    <li>Wind drift</li>
                    <li>Rest centershot issues</li>
                    <li>Sight windage problems</li>
                  </ul>
                  <p class="mt-2"><strong>Solutions:</strong></p>
                  <ul class="list-disc list-inside ml-2 space-y-1">
                    <li>Practice consistent grip</li>
                    <li>Check rest centershot</li>
                    <li>Perform walk-back tuning</li>
                    <li>Account for wind conditions</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Clearance Issues -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 mr-3"></i>
            Poor Clearance Issues
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <!-- Arrow Rest Contact -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Arrow Rest Contact
              </h3>
              <div class="space-y-3">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-1">Symptoms:</h4>
                  <ul class="text-sm text-red-700 dark:text-red-400 list-disc list-inside">
                    <li>Fletching damage or wear</li>
                    <li>Inconsistent arrow flight</li>
                    <li>Noise during shot</li>
                    <li>Erratic grouping</li>
                  </ul>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-1">Solutions:</h4>
                  <ul class="text-sm text-green-700 dark:text-green-400 list-disc list-inside">
                    <li>Adjust rest height and centershot</li>
                    <li>Check arrow spine compatibility</li>
                    <li>Verify rest timing (drop-away)</li>
                    <li>Use correct arrow diameter</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Cable/String Contact -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Cable/String Contact
              </h3>
              <div class="space-y-3">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-red-800 dark:text-red-300 mb-1">Symptoms:</h4>
                  <ul class="text-sm text-red-700 dark:text-red-400 list-disc list-inside">
                    <li>Fletching contact marks</li>
                    <li>String/cable wear</li>
                    <li>Left/right arrow impacts</li>
                    <li>Audible contact during shot</li>
                  </ul>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-1">Solutions:</h4>
                  <ul class="text-sm text-green-700 dark:text-green-400 list-disc list-inside">
                    <li>Adjust nocking point position</li>
                    <li>Check arrow length and spine</li>
                    <li>Consider smaller fletching</li>
                    <li>Verify cam timing and sync</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Diagnostic Flowchart -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            <i class="fas fa-sitemap text-indigo-600 dark:text-indigo-400 mr-3"></i>
            Diagnostic Flowchart
          </h2>
          
          <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-indigo-800 dark:text-indigo-300 mb-4">
              Step-by-Step Problem Solving
            </h3>
            
            <div class="space-y-4">
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-300">Initial Assessment</h4>
                  <p class="text-sm text-indigo-700 dark:text-indigo-400">Shoot 3-5 arrows through paper at 6 feet. Note tear patterns and grouping at 20 yards.</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-300">Equipment Check</h4>
                  <p class="text-sm text-indigo-700 dark:text-indigo-400">Verify arrow condition, rest alignment, and bow setup. Check for obvious mechanical issues.</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-300">Form Analysis</h4>
                  <p class="text-sm text-indigo-700 dark:text-indigo-400">Assess shooting form consistency: grip, anchor point, release technique, and follow-through.</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">4</div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-300">Systematic Tuning</h4>
                  <p class="text-sm text-indigo-700 dark:text-indigo-400">Make one adjustment at a time. Test with paper tuning, then verify at distance.</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">5</div>
                <div>
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-300">Final Verification</h4>
                  <p class="text-sm text-indigo-700 dark:text-indigo-400">Confirm improvements with multiple shot groups at various distances.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Interactive Tuning Link -->
        <div class="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-6 text-center">
          <h3 class="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-2">
            Need Interactive Guidance?
          </h3>
          <p class="text-blue-700 dark:text-blue-300 mb-4">
            Use our interactive tuning guides for step-by-step assistance with your specific setup.
          </p>
          <NuxtLink
            to="/tuning"
            class="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-play mr-2"></i>
            Start Interactive Tuning
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Page metadata
definePageMeta({
  layout: 'default'
})

useHead({
  title: 'Arrow Flight Problems - Archery Tools',
  meta: [
    { name: 'description', content: 'Comprehensive guide for diagnosing and solving arrow flight problems including paper tuning tears, grouping issues, and clearance problems.' }
  ]
})

// Quick problem finder data
const quickProblems = ref([
  {
    id: 'left-tear',
    name: 'Left Tear',
    description: 'Arrow tearing left through paper'
  },
  {
    id: 'right-tear', 
    name: 'Right Tear',
    description: 'Arrow tearing right through paper'
  },
  {
    id: 'high-tear',
    name: 'High Tear',
    description: 'Arrow tearing high through paper'
  },
  {
    id: 'low-tear',
    name: 'Low Tear', 
    description: 'Arrow tearing low through paper'
  },
  {
    id: 'erratic-groups',
    name: 'Erratic Groups',
    description: 'Inconsistent arrow grouping'
  },
  {
    id: 'vertical-string',
    name: 'Vertical String',
    description: 'Arrows grouping vertically'
  },
  {
    id: 'horizontal-string',
    name: 'Horizontal String',
    description: 'Arrows grouping horizontally'
  },
  {
    id: 'clearance-issues',
    name: 'Poor Clearance',
    description: 'Fletching contact or damage'
  }
])

const selectedProblem = ref('')
</script>

<style scoped>
/* Component specific styles */
</style>