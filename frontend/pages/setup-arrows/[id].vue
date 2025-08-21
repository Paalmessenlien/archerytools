<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="container mx-auto px-4 py-8">
      <div class="animate-pulse">
        <!-- Breadcrumb skeleton -->
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-64 mb-6"></div>
        
        <!-- Header skeleton -->
        <div class="mb-8">
          <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-96 mb-4"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48"></div>
        </div>
        
        <!-- Content skeleton -->
        <div class="space-y-6">
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4"></div>
            <div class="space-y-3">
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="container mx-auto px-4 py-8">
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <i class="fas fa-exclamation-triangle text-4xl text-red-600 dark:text-red-400 mb-4"></i>
        <h2 class="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">Arrow Setup Not Found</h2>
        <p class="text-red-600 dark:text-red-400 mb-4">{{ error }}</p>
        <div class="flex justify-center space-x-3">
          <button
            @click="$router.go(-1)"
            class="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <i class="fas fa-arrow-left mr-2"></i>
            Go Back
          </button>
          <NuxtLink
            to="/my-setup"
            class="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <i class="fas fa-list mr-2"></i>
            My Setups
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="setupArrowData" class="container mx-auto px-3 sm:px-4 py-4 sm:py-8 max-w-7xl">
      <!-- Breadcrumb Navigation -->
      <SetupContextBreadcrumb
        :bow-setup="setupArrowData.bow_setup"
        :arrow-name="getArrowDisplayName()"
        class="mb-6"
      />

      <!-- Header -->
      <div class="space-y-6 mb-8">
        <!-- Title and Info -->
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 leading-tight">
            {{ getArrowDisplayName() }}
          </h1>
          <p class="text-lg text-gray-600 dark:text-gray-400 mt-2">
            {{ setupArrowData.arrow?.material || 'Unknown Material' }} Arrow in {{ setupArrowData.bow_setup.name }}
          </p>
          
          <!-- Quick Stats Pills -->
          <div class="flex flex-wrap items-center gap-3 mt-4">
            <div class="flex items-center px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-sm">
              <i class="fas fa-ruler-horizontal mr-2"></i>
              {{ setupArrowData.setup_arrow.arrow_length }}" length
            </div>
            <div class="flex items-center px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-full text-sm">
              <i class="fas fa-bullseye mr-2"></i>
              {{ setupArrowData.setup_arrow.point_weight }} gr point
            </div>
            <div class="flex items-center px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 rounded-full text-sm">
              <i class="fas fa-balance-scale mr-2"></i>
              {{ calculateTotalWeight() }} gr total
            </div>
            <div v-if="setupArrowData.setup_arrow.compatibility_score" 
                 class="flex items-center px-3 py-1 rounded-full text-sm"
                 :class="getCompatibilityClass(setupArrowData.setup_arrow.compatibility_score)">
              <i class="fas fa-star mr-2"></i>
              {{ setupArrowData.setup_arrow.compatibility_score }}% match
            </div>
          </div>
        </div>
        
        <!-- Actions - Mobile Responsive -->
        <div class="flex flex-col sm:flex-row gap-3">
          <button
            @click="editMode = !editMode"
            class="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors w-full sm:w-auto"
          >
            <i :class="editMode ? 'fas fa-eye' : 'fas fa-edit'" class="mr-2"></i>
            {{ editMode ? 'View Mode' : 'Edit Setup' }}
          </button>
          <button
            @click="duplicateArrow"
            class="inline-flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors w-full sm:w-auto"
          >
            <i class="fas fa-copy mr-2"></i>
            Duplicate
          </button>
        </div>
      </div>

      <!-- Mobile-First Accordion Content Interface -->
      <div class="space-y-4">
        <!-- Configuration Section - Always Expanded by Default -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <!-- Section Header -->
          <button
            @click="toggleSection('config')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 'bg-blue-50 dark:bg-blue-900/20': expandedSections.config }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30 flex-shrink-0">
                <i class="fas fa-cog text-blue-600 dark:text-blue-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Arrow Configuration</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">View and edit your arrow specifications</p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <!-- Edit Mode Toggle Badge -->
              <div v-if="editMode" class="px-3 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 rounded-full text-xs font-medium">
                Editing
              </div>
              <!-- Unsaved Changes Badge -->
              <div v-if="hasUnsavedChanges" class="px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded-full text-xs font-medium">
                Unsaved
              </div>
              <!-- Expand/Collapse Icon -->
              <i 
                :class="expandedSections.config ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
                class="text-gray-400 transition-transform duration-200"
              ></i>
            </div>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.config" class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <ArrowSetupEditor
              v-if="editMode"
              :setup-arrow="setupArrowData.setup_arrow"
              :arrow="setupArrowData.arrow"
              :spine-specifications="setupArrowData.spine_specifications"
              :bow-config="setupArrowData.bow_setup"
              @update="handleConfigUpdate"
              @save="handleConfigSave"
              @cancel="handleConfigCancel"
              class="space-y-4"
            />
            
            <ArrowSetupDisplay
              v-else
              :setup-arrow="setupArrowData.setup_arrow"
              :arrow="setupArrowData.arrow"
              :spine-specifications="setupArrowData.spine_specifications"
              class="space-y-4"
            />
          </div>
        </div>

        <!-- Performance Analysis Section -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <!-- Section Header -->
          <button
            @click="toggleSection('performance')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 'bg-green-50 dark:bg-green-900/20': expandedSections.performance }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30 flex-shrink-0">
                <i class="fas fa-tachometer-alt text-green-600 dark:text-green-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Performance Analysis</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Detailed arrow performance metrics and chronograph data</p>
              </div>
            </div>
            <i 
              :class="expandedSections.performance ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
              class="text-gray-400 transition-transform duration-200"
            ></i>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.performance" class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <ArrowPerformanceAnalysis
              ref="performanceAnalysisRef"
              :setup-arrow="setupArrowData.setup_arrow"
              :bow-config="setupArrowData.bow_setup"
              :arrow="setupArrowData.arrow"
              @performance-updated="handlePerformanceUpdate"
            />

            <!-- Chronograph Data Section -->
            <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <ChronographDataEntry
                :bow-setup-id="setupArrowData.bow_setup.id"
                :current-setup-arrow="setupArrowData.setup_arrow"
                :current-arrow="setupArrowData.arrow"
                @data-updated="handleChronographDataUpdate"
                @speed-calculated="handleSpeedCalculated"
              />
            </div>
          </div>
        </div>

        <!-- Arrow Information Section -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <!-- Section Header -->
          <button
            @click="toggleSection('info')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 'bg-purple-50 dark:bg-purple-900/20': expandedSections.info }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/30 flex-shrink-0">
                <i class="fas fa-info-circle text-purple-600 dark:text-purple-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Arrow Information</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Manufacturer specifications and database information</p>
              </div>
            </div>
            <i 
              :class="expandedSections.info ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
              class="text-gray-400 transition-transform duration-200"
            ></i>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.info" class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <ArrowDatabaseInfo
              :arrow="setupArrowData.arrow"
              :spine-specifications="setupArrowData.spine_specifications"
            />

            <!-- Bow Setup Context -->
            <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                <i class="fas fa-crosshairs mr-2 text-orange-600"></i>
                Bow Setup Context
              </h4>
              
              <BowSetupContext
                :bow-setup="setupArrowData.bow_setup"
                @edit-bow="navigateToBowSetup"
              />
            </div>
          </div>
        </div>

        <!-- Interactive Tuning Guides Section -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <!-- Section Header -->
          <button
            @click="toggleSection('tuning')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 'bg-indigo-50 dark:bg-indigo-900/20': expandedSections.tuning }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex-shrink-0">
                <i class="fas fa-crosshairs text-indigo-600 dark:text-indigo-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Interactive Tuning Guides</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Test this arrow setup with advanced tuning interfaces</p>
              </div>
            </div>
            <i 
              :class="expandedSections.tuning ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
              class="text-gray-400 transition-transform duration-200"
            ></i>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.tuning" class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <!-- Guide Selection -->
            <div v-if="!activeTuningSession" class="space-y-4">
              <p class="text-gray-600 dark:text-gray-300 text-sm">
                Start an interactive tuning session to test this specific arrow setup. 
                All test results are permanently stored and can be reviewed in your tuning history.
              </p>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <!-- Paper Tuning -->
                <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-500 transition-colors cursor-pointer"
                     @click="startTuningGuide('paper_tuning')">
                  <div class="flex items-center mb-2">
                    <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                      <i class="fas fa-newspaper text-blue-600 dark:text-blue-400"></i>
                    </div>
                    <div class="ml-3">
                      <h4 class="font-medium text-gray-900 dark:text-gray-100">Paper Tuning</h4>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Beginner • 10-15 min</p>
                    </div>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-300">
                    Use a paper test to check arrow flight and tune your bow setup.
                  </p>
                </div>
                
                <!-- Bareshaft Tuning -->
                <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-500 transition-colors cursor-pointer"
                     @click="startTuningGuide('bareshaft_tuning')">
                  <div class="flex items-center mb-2">
                    <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                      <i class="fas fa-crosshairs text-green-600 dark:text-green-400"></i>
                    </div>
                    <div class="ml-3">
                      <h4 class="font-medium text-gray-900 dark:text-gray-100">Bareshaft Tuning</h4>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Intermediate • 15-20 min</p>
                    </div>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-300">
                    Compare fletched and bare arrow impacts to fine-tune spine match.
                  </p>
                </div>
                
                <!-- Walkback Tuning -->
                <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-500 transition-colors cursor-pointer"
                     @click="startTuningGuide('walkback_tuning')">
                  <div class="flex items-center mb-2">
                    <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                      <i class="fas fa-ruler text-purple-600 dark:text-purple-400"></i>
                    </div>
                    <div class="ml-3">
                      <h4 class="font-medium text-gray-900 dark:text-gray-100">Walkback Tuning</h4>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Advanced • 20-30 min</p>
                    </div>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-300">
                    Test arrow flight consistency across multiple distances.
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Active Session Interface -->
            <div v-if="activeTuningSession" class="space-y-4">
              <!-- Paper Tuning Interface -->
              <PaperTuningInterface 
                v-if="activeTuningSession.guide_type === 'paper_tuning'"
                :session-data="activeTuningSession"
                @test-recorded="onTuningTestRecorded"
                @cancel="exitTuningSession"
              />
              
              <!-- Bareshaft Tuning Interface -->
              <BareshaftTuningInterface 
                v-if="activeTuningSession.guide_type === 'bareshaft_tuning'"
                :session-data="activeTuningSession"
                @test-recorded="onTuningTestRecorded"
                @cancel="exitTuningSession"
              />
              
              <!-- Walkback Tuning Interface -->
              <WalkbackTuningInterface 
                v-if="activeTuningSession.guide_type === 'walkback_tuning'"
                :session-data="activeTuningSession"
                @test-recorded="onTuningTestRecorded"
                @cancel="exitTuningSession"
              />
            </div>
          </div>
        </div>

        <!-- Quick Actions Section -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <!-- Section Header -->
          <button
            @click="toggleSection('actions')"
            class="w-full p-4 sm:p-6 text-left flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 touch-manipulation min-h-[64px]"
            :class="{ 'bg-orange-50 dark:bg-orange-900/20': expandedSections.actions }"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 mr-4 flex items-center justify-center rounded-lg bg-orange-100 dark:bg-orange-900/30 flex-shrink-0">
                <i class="fas fa-bolt text-orange-600 dark:text-orange-400 text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Quick Actions</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Manage your arrow setup with convenient actions</p>
              </div>
            </div>
            <i 
              :class="expandedSections.actions ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" 
              class="text-gray-400 transition-transform duration-200"
            ></i>
          </button>

          <!-- Section Content -->
          <div v-if="expandedSections.actions" class="p-4 sm:p-6 space-y-4">
            <!-- Mobile-Optimized Actions Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                @click="calculatePerformance"
                :disabled="calculatingPerformance"
                class="mobile-action-button w-full flex items-center justify-center p-4 rounded-xl border-2 transition-all duration-200 touch-manipulation min-h-[56px] bg-green-50 border-green-200 text-green-700 hover:bg-green-100 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:bg-green-900/20 dark:border-green-700 dark:text-green-300 dark:hover:bg-green-900/30 disabled:opacity-50"
              >
                <div class="flex items-center">
                  <div class="w-8 h-8 mr-3 flex items-center justify-center rounded-lg bg-green-200 dark:bg-green-800 flex-shrink-0">
                    <i :class="calculatingPerformance ? 'fas fa-spinner fa-spin' : 'fas fa-calculator'" class="text-green-700 dark:text-green-300 text-sm"></i>
                  </div>
                  <span class="font-medium">{{ calculatingPerformance ? 'Calculating...' : 'Recalculate Performance' }}</span>
                </div>
              </button>
              
              <button
                @click="viewInDatabase"
                class="mobile-action-button w-full flex items-center justify-center p-4 rounded-xl border-2 transition-all duration-200 touch-manipulation min-h-[56px] bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:bg-blue-900/20 dark:border-blue-700 dark:text-blue-300 dark:hover:bg-blue-900/30"
              >
                <div class="flex items-center">
                  <div class="w-8 h-8 mr-3 flex items-center justify-center rounded-lg bg-blue-200 dark:bg-blue-800 flex-shrink-0">
                    <i class="fas fa-external-link-alt text-blue-700 dark:text-blue-300 text-sm"></i>
                  </div>
                  <span class="font-medium">View in Database</span>
                </div>
              </button>
              
              <button
                @click="addToCalculator"
                class="mobile-action-button w-full flex items-center justify-center p-4 rounded-xl border-2 transition-all duration-200 touch-manipulation min-h-[56px] bg-indigo-50 border-indigo-200 text-indigo-700 hover:bg-indigo-100 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:bg-indigo-900/20 dark:border-indigo-700 dark:text-indigo-300 dark:hover:bg-indigo-900/30"
              >
                <div class="flex items-center">
                  <div class="w-8 h-8 mr-3 flex items-center justify-center rounded-lg bg-indigo-200 dark:bg-indigo-800 flex-shrink-0">
                    <i class="fas fa-plus text-indigo-700 dark:text-indigo-300 text-sm"></i>
                  </div>
                  <span class="font-medium">Add to Calculator</span>
                </div>
              </button>
              
              <button
                @click="removeArrow"
                class="mobile-action-button w-full flex items-center justify-center p-4 rounded-xl border-2 transition-all duration-200 touch-manipulation min-h-[56px] bg-red-50 border-red-200 text-red-700 hover:bg-red-100 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:bg-red-900/20 dark:border-red-700 dark:text-red-300 dark:hover:bg-red-900/30"
              >
                <div class="flex items-center">
                  <div class="w-8 h-8 mr-3 flex items-center justify-center rounded-lg bg-red-200 dark:bg-red-800 flex-shrink-0">
                    <i class="fas fa-trash text-red-700 dark:text-red-300 text-sm"></i>
                  </div>
                  <span class="font-medium">Remove from Setup</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <ConfirmationModal
      v-if="showConfirmModal"
      :title="confirmModal.title"
      :message="confirmModal.message"
      :confirm-text="confirmModal.confirmText"
      :cancel-text="confirmModal.cancelText"
      @confirm="confirmModal.onConfirm"
      @cancel="showConfirmModal = false"
    />

    <!-- Notification Toast -->
    <NotificationToast
      v-if="notification.show"
      :message="notification.message"
      :type="notification.type"
      @close="hideNotification"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter, useHead, onBeforeRouteLeave } from '#imports'
import { useApi } from '~/composables/useApi'
import { useBowSetupPickerStore } from '~/stores/bowSetupPicker'
import SetupContextBreadcrumb from '~/components/SetupContextBreadcrumb.vue'
import ArrowSetupEditor from '~/components/ArrowSetupEditor.vue'
import ArrowSetupDisplay from '~/components/ArrowSetupDisplay.vue'
import ArrowPerformanceAnalysis from '~/components/ArrowPerformanceAnalysis.vue'
import ArrowDatabaseInfo from '~/components/ArrowDatabaseInfo.vue'
import BowSetupContext from '~/components/BowSetupContext.vue'
import ChronographDataEntry from '~/components/ChronographDataEntry.vue'
import ConfirmationModal from '~/components/ConfirmationModal.vue'
import NotificationToast from '~/components/NotificationToast.vue'
import PaperTuningInterface from '~/components/PaperTuningInterface.vue'
import BareshaftTuningInterface from '~/components/BareshaftTuningInterface.vue'
import WalkbackTuningInterface from '~/components/WalkbackTuningInterface.vue'

// Meta information
definePageMeta({
  title: 'Arrow Setup Details'
})

// Composables
const route = useRoute()
const router = useRouter()
const api = useApi()
const bowSetupPickerStore = useBowSetupPickerStore()

// State
const setupArrowData = ref(null)
const performanceAnalysisRef = ref(null)
const loading = ref(true)
const error = ref('')
const editMode = ref(false)
const hasUnsavedChanges = ref(false)
const calculatingPerformance = ref(false)
// Accordion state - config expanded by default for primary workflow
const expandedSections = ref({
  config: true,        // Configuration always starts expanded 
  performance: false,  // Performance collapsed by default
  info: false,        // Info collapsed by default  
  tuning: false,      // Tuning guides collapsed by default
  actions: false      // Actions collapsed by default
})

// Tuning session state
const activeTuningSession = ref(null)

// Modal state
const showConfirmModal = ref(false)
const confirmModal = ref({
  title: '',
  message: '',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  onConfirm: () => {}
})

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

// Computed
const setupArrowId = computed(() => route.params.id)

// Accordion section toggle method
const toggleSection = (sectionId) => {
  console.log('Accordion section toggled:', sectionId)
  expandedSections.value[sectionId] = !expandedSections.value[sectionId]
}

// Methods
const loadSetupArrowDetails = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await api.get(`/setup-arrows/${setupArrowId.value}/details`)
    setupArrowData.value = response
    
    // Update page title
    const arrowName = getArrowDisplayName()
    useHead({
      title: `${arrowName} - Arrow Setup Details`,
      meta: [
        { 
          name: 'description', 
          content: `Detailed configuration and performance analysis for ${arrowName} in bow setup.` 
        }
      ]
    })
    
  } catch (err) {
    console.error('Error loading arrow setup details:', err)
    error.value = err.message || 'Failed to load arrow setup details'
  } finally {
    loading.value = false
  }
}

const getArrowDisplayName = () => {
  if (!setupArrowData.value) return 'Arrow Setup'
  
  const arrow = setupArrowData.value.arrow
  if (arrow) {
    return `${arrow.manufacturer} ${arrow.model_name}`
  }
  
  return `Arrow ${setupArrowData.value.setup_arrow.arrow_id}`
}

const calculateTotalWeight = () => {
  if (!setupArrowData.value) return 0
  
  const setup = setupArrowData.value.setup_arrow
  const arrow = setupArrowData.value.arrow
  
  // Calculate shaft weight using GPI
  let shaftWeight = 0
  if (arrow?.spine_specifications?.length > 0) {
    const spineSpec = arrow.spine_specifications.find(spec => 
      spec.spine.toString() === setup.calculated_spine?.toString()
    ) || arrow.spine_specifications[0]
    
    if (spineSpec?.gpi_weight) {
      shaftWeight = spineSpec.gpi_weight * (setup.arrow_length || 32)
    }
  }
  
  // Add component weights
  const pointWeight = setup.point_weight || 0
  const nockWeight = setup.nock_weight || 10
  const insertWeight = setup.insert_weight || 0
  const bushingWeight = setup.bushing_weight || 0
  const fletchingWeight = setup.fletching_weight || 15
  
  const totalWeight = shaftWeight + pointWeight + nockWeight + insertWeight + bushingWeight + fletchingWeight
  
  return Math.round(totalWeight * 10) / 10
}

const getCompatibilityClass = (score) => {
  if (score >= 90) {
    return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
  } else if (score >= 70) {
    return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
  } else {
    return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
  }
}

// Event handlers
const handleConfigUpdate = (updatedConfig) => {
  hasUnsavedChanges.value = true
  // Update local state for real-time preview
  setupArrowData.value.setup_arrow = { ...setupArrowData.value.setup_arrow, ...updatedConfig }
}

const handleConfigSave = async (updatedConfig) => {
  try {
    await api.put(`/setup-arrows/${setupArrowId.value}`, updatedConfig)
    hasUnsavedChanges.value = false
    editMode.value = false
    showNotification('Arrow configuration updated successfully', 'success')
    await loadSetupArrowDetails() // Reload to get fresh data
    
    // Refresh bow selector navigation cache after successful save
    if (setupArrowData.value?.setup_arrow?.setup_id && bowSetupPickerStore.refreshSelectedBowSetup) {
      await bowSetupPickerStore.refreshSelectedBowSetup(setupArrowData.value.setup_arrow.setup_id)
    }
    
  } catch (err) {
    console.error('Error saving configuration:', err)
    showNotification('Failed to save configuration', 'error')
  }
}

const handleConfigCancel = () => {
  if (hasUnsavedChanges.value) {
    confirmModal.value = {
      title: 'Discard Changes?',
      message: 'You have unsaved changes. Are you sure you want to cancel editing?',
      confirmText: 'Discard',
      cancelText: 'Keep Editing',
      onConfirm: () => {
        hasUnsavedChanges.value = false
        editMode.value = false
        showConfirmModal.value = false
        loadSetupArrowDetails() // Reload original data
      }
    }
    showConfirmModal.value = true
  } else {
    editMode.value = false
  }
}

const handlePerformanceUpdate = (performanceData) => {
  if (setupArrowData.value) {
    setupArrowData.value.setup_arrow.performance = performanceData
  }
}

const handleChronographDataUpdate = async (data) => {
  console.log('Chronograph data updated:', data)
  // Trigger performance recalculation when chronograph data changes
  if (setupArrowData.value) {
    try {
      // First reload arrow details to get latest data
      await loadSetupArrowDetails()
      
      // Then trigger performance recalculation directly on the performance component
      if (performanceAnalysisRef.value && performanceAnalysisRef.value.calculatePerformance) {
        await performanceAnalysisRef.value.calculatePerformance()
      } else {
        // Fallback to the page-level calculation
        await calculatePerformance()
      }
      
      showNotification('Performance updated with measured speed data', 'success')
    } catch (error) {
      console.error('Error updating performance after chronograph data change:', error)
      showNotification('Error updating performance calculations', 'error')
    }
  }
}

const handleSpeedCalculated = (speedData) => {
  console.log('Speed calculated from chronograph:', speedData)
  showNotification(`Speed updated: ${speedData.speed} FPS for ${speedData.arrow_weight}gr arrow`, 'success')
}

const calculatePerformance = async () => {
  try {
    calculatingPerformance.value = true
    await api.post(`/setup-arrows/${setupArrowId.value}/calculate-performance`, {
      bow_config: setupArrowData.value.bow_setup
    })
    await loadSetupArrowDetails() // Reload to get performance data
    showNotification('Performance calculated successfully', 'success')
  } catch (err) {
    console.error('Error calculating performance:', err)
    showNotification('Failed to calculate performance', 'error')
  } finally {
    calculatingPerformance.value = false
  }
}

const duplicateArrow = () => {
  confirmModal.value = {
    title: 'Duplicate Arrow?',
    message: 'This will create a copy of this arrow setup that you can modify independently.',
    confirmText: 'Duplicate',
    cancelText: 'Cancel',
    onConfirm: async () => {
      try {
        const setup = setupArrowData.value.setup_arrow
        const duplicateData = {
          arrow_id: setup.arrow_id,
          arrow_length: setup.arrow_length,
          point_weight: setup.point_weight,
          calculated_spine: setup.calculated_spine,
          notes: `Copy of: ${setup.notes || 'arrow setup'}`,
          nock_weight: setup.nock_weight,
          insert_weight: setup.insert_weight,
          bushing_weight: setup.bushing_weight,
          fletching_weight: setup.fletching_weight,
          compatibility_score: setup.compatibility_score,
          allow_duplicate: true
        }
        
        await api.post(`/bow-setups/${setup.setup_id}/arrows`, duplicateData)
        showNotification('Arrow duplicated successfully', 'success')
        showConfirmModal.value = false
      } catch (err) {
        console.error('Error duplicating arrow:', err)
        showNotification('Failed to duplicate arrow', 'error')
      }
    }
  }
  showConfirmModal.value = true
}

const removeArrow = () => {
  confirmModal.value = {
    title: 'Remove Arrow?',
    message: 'This will permanently remove this arrow from your bow setup. This action cannot be undone.',
    confirmText: 'Remove',
    cancelText: 'Cancel',
    onConfirm: async () => {
      try {
        await api.delete(`/setup-arrows/${setupArrowId.value}`)
        showNotification('Arrow removed successfully', 'success')
        showConfirmModal.value = false
        // Navigate back to bow setup
        router.push(`/setups/${setupArrowData.value.setup_arrow.setup_id}?tab=arrows`)
      } catch (err) {
        console.error('Error removing arrow:', err)
        showNotification('Failed to remove arrow', 'error')
      }
    }
  }
  showConfirmModal.value = true
}

const viewInDatabase = () => {
  if (setupArrowData.value?.setup_arrow?.arrow_id) {
    router.push(`/arrows/${setupArrowData.value.setup_arrow.arrow_id}`)
  }
}

const addToCalculator = () => {
  const bow = setupArrowData.value.bow_setup
  router.push({
    path: '/calculator',
    query: {
      draw_weight: bow.draw_weight,
      draw_length: bow.draw_length,
      bow_type: bow.bow_type,
      ibo_speed: bow.ibo_speed,
      let_off: bow.let_off_percentage
    }
  })
}

const navigateToBowSetup = () => {
  router.push(`/setups/${setupArrowData.value.setup_arrow.setup_id}`)
}

const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  }
  
  setTimeout(() => {
    hideNotification()
  }, 5000)
}

const hideNotification = () => {
  notification.value.show = false
}

// Tuning session methods
const startTuningGuide = async (guideType) => {
  try {
    if (!setupArrowData.value) {
      console.error('No setup arrow data available')
      return
    }
    
    showNotification('Starting tuning session...', 'info')
    
    // Create session in database via API
    const sessionData = {
      guide_type: guideType,
      arrow_id: setupArrowData.value.setup_arrow.arrow_id,
      arrow_length: setupArrowData.value.setup_arrow.arrow_length,
      point_weight: setupArrowData.value.setup_arrow.point_weight,
      bow_setup_id: setupArrowData.value.bow_setup.id,
      settings: {
        record_environment: true,
        auto_calculate: true
      }
    }
    
    const session = await api.post('/tuning-guides/sessions', sessionData)
    
    // Create local session object with API response data
    activeTuningSession.value = {
      session_id: session.session_id,
      guide_type: guideType,
      arrow_id: setupArrowData.value.setup_arrow.arrow_id,
      arrow: setupArrowData.value.arrow,
      arrow_length: setupArrowData.value.setup_arrow.arrow_length,
      point_weight: setupArrowData.value.setup_arrow.point_weight,
      bow_setup: setupArrowData.value.bow_setup,
      settings: sessionData.settings,
      // Include session metadata from API
      ...session
    }
    
    // Expand the tuning section if not already expanded
    if (!expandedSections.value.tuning) {
      expandedSections.value.tuning = true
    }
    
    console.log('Started tuning session for setup arrow:', activeTuningSession.value)
    showNotification(`${guideType.replace('_', ' ')} session started`, 'success')
  } catch (error) {
    console.error('Error starting tuning guide:', error)
    showNotification('Failed to start tuning session', 'error')
  }
}

const onTuningTestRecorded = (testResult) => {
  console.log('Tuning test recorded for setup arrow:', testResult)
  showNotification('Test result recorded successfully', 'success')
  // Test results are automatically saved by the individual interface components
}

const exitTuningSession = () => {
  activeTuningSession.value = null
}

// Enhanced accordion interaction with smooth animations
// All interaction is now handled by the toggleSection method above

// Lifecycle
onMounted(() => {
  if (setupArrowId.value) {
    loadSetupArrowDetails()
  }
})

// Watch for route changes
watch(() => setupArrowId.value, (newId) => {
  if (newId) {
    loadSetupArrowDetails()
  }
})

// Warn about unsaved changes when leaving
onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges.value) {
    const leave = confirm('You have unsaved changes. Are you sure you want to leave?')
    if (leave) {
      next()
    } else {
      next(false)
    }
  } else {
    next()
  }
})
</script>

<style scoped>
/* Accordion Section Animation */
.accordion-section {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Section Header Button Styling */
.accordion-header {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.accordion-header:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dark .accordion-header:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Enhanced Mobile Touch Feedback */
@media (max-width: 640px) {
  .accordion-header:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
  }
  
  /* Mobile action buttons */
  .mobile-action-button {
    text-align: left;
  }
  
  .mobile-action-button:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
  }
}

/* Section Content Animation */
.section-content {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Enhanced Focus States for Accessibility */
.accordion-header:focus-visible {
  outline: 2px solid rgb(59 130 246);
  outline-offset: 2px;
  border-radius: 8px;
}

/* Status Badges */
.status-badge {
  transition: all 0.2s ease;
}

.status-badge:hover {
  transform: scale(1.05);
}

/* Chevron Icon Animation */
.chevron-icon {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Desktop Optimizations */
@media (min-width: 641px) {
  .mobile-action-button {
    text-align: center;
  }
  
  .mobile-action-button .flex {
    justify-content: center;
  }
  
  /* Desktop hover states */
  .accordion-header:hover .chevron-icon {
    transform: scale(1.1);
  }
}

/* Smooth Section Spacing */
.accordion-container > * + * {
  margin-top: 1rem;
}

/* Enhanced Visual Hierarchy */
.section-icon {
  transition: all 0.2s ease;
}

.accordion-header:hover .section-icon {
  transform: scale(1.05);
}
</style>