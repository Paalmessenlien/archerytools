<template>
  <div 
    class="py-4 mx-auto max-w-7xl pb-24 md:pb-8 mobile-safe-content"
    @touchstart="handlePullStart"
    @touchmove="handlePullMove"
    @touchend="handlePullEnd"
  >
    <!-- Notification Toast -->
    <div v-if="notification.show" class="fixed top-4 right-4 z-50 transition-all duration-300">
      <div 
        :class="[
          'p-3 sm-mobile:p-4 rounded-lg shadow-lg max-w-sm',
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
            <span class="mobile-body-medium md:text-base">{{ notification.message }}</span>
          </div>
          <CustomButton
            @click="hideNotification"
            variant="text"
            size="small"
            class="ml-4 opacity-70 hover:opacity-100 mobile-touch-target !p-1 !min-h-0"
            icon="fas fa-times"
          />
        </div>
      </div>
    </div>

    <h1 class="mobile-heading-1 md:text-3xl font-bold text-gray-900 dark:text-gray-100 mobile-compact-spacing md:mb-4">My Setup</h1>
    
    <div v-if="isLoadingUser" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
      <p class="text-gray-700 dark:text-gray-300">Loading...</p>
    </div>

    <div v-else-if="user">
      <!-- Compact Profile Header -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-3 sm-mobile:p-4 mobile-element-spacing md:mb-6">
        <!-- Profile Content -->
        <div class="flex items-center space-x-3 sm-mobile:space-x-4 mb-2 sm-mobile:mb-3">
          <!-- Profile Picture -->
          <div class="flex-shrink-0">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">
              <img 
                v-if="user.profile_picture_url" 
                :src="user.profile_picture_url" 
                :alt="user.name || 'Profile picture'" 
                class="w-10 h-10 rounded-full object-cover"
              />
              <span v-else class="mobile-body-medium md:text-lg">
                {{ (user.name || user.email || 'U').charAt(0).toUpperCase() }}
              </span>
            </div>
          </div>
          
          <!-- Basic Info -->
          <div class="flex-1">
            <h2 class="mobile-heading-4 md:text-xl font-bold text-gray-900 dark:text-gray-100 mb-0">
              {{ user.name || 'Archer' }}
            </h2>
            <div class="flex items-center space-x-3 sm-mobile:space-x-4 mobile-body-small md:text-sm text-gray-600 dark:text-gray-400">
              <span>Draw: {{ user.draw_length || 28.0 }}"</span>
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                    :class="getSkillLevelClass(user.skill_level)">
                {{ formatSkillLevel(user.skill_level) }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- Action Buttons - Full Width -->
        <div class="flex flex-col sm:flex-row gap-2 pt-2.5 border-t border-gray-200 dark:border-gray-700">
          <CustomButton
            @click="openEditModal"
            variant="outlined"
            size="small"
            class="flex-1 text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-purple-400 dark:border-purple-400 dark:hover:bg-purple-900"
          >
            <i class="fas fa-edit mr-2"></i>
            Edit Profile
          </CustomButton>
          <CustomButton
            @click="logout"
            variant="outlined"
            size="small"
            class="flex-1 text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900 lg:hidden"
          >
            <i class="fas fa-sign-out-alt mr-2"></i>
            Logout
          </CustomButton>
        </div>
      </div>

      <!-- Edit Profile Modal -->
      <EditArcherProfileModal
        :is-open="isEditing"
        :user="user"
        :isSaving="isSaving"
        :error="editError"
        @close="closeEditModal"
        @save="saveProfile"
      />

      <!-- Bow Setups Dashboard Section -->
      <div class="mobile-element-spacing">
        <div class="mobile-element-spacing">
          <div>
            <h3 class="mobile-heading-2 md:text-2xl font-bold text-gray-900 dark:text-gray-100">My Bow Setups</h3>
            <p class="mobile-body-small md:text-base text-gray-600 dark:text-gray-400">Manage your bow configurations and arrow selections</p>
          </div>
        </div>

        <!-- Phase 3: Pull-to-Refresh Indicators -->
        <!-- Active Refresh Indicator -->
        <div 
          v-if="pullToRefresh.isRefreshing" 
          class="fixed top-20 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg z-50 flex items-center gap-2 animate-pulse"
        >
          <div class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
          <span class="text-sm font-medium">Refreshing...</span>
        </div>
        
        <!-- Pull Down Indicator (while pulling) -->
        <div 
          v-if="pullToRefresh.isPulling && !pullToRefresh.isRefreshing" 
          class="fixed top-16 left-1/2 transform -translate-x-1/2 z-40 transition-all duration-200"
          :style="{ 
            transform: `translateX(-50%) translateY(${Math.min(pullToRefresh.currentY / 3, 30)}px)`,
            opacity: Math.min(pullToRefresh.currentY / pullToRefresh.threshold, 1)
          }"
        >
          <div 
            class="flex items-center gap-2 px-3 py-2 rounded-full shadow-lg transition-colors duration-200"
            :class="pullToRefresh.isTriggered 
              ? 'bg-green-600 text-white' 
              : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'"
          >
            <i 
              class="fas transition-transform duration-200"
              :class="[
                pullToRefresh.isTriggered ? 'fa-check' : 'fa-arrow-down',
                pullToRefresh.isTriggered ? 'text-white' : 'text-gray-500'
              ]"
            ></i>
            <span class="text-xs font-medium">
              {{ pullToRefresh.isTriggered ? 'Release to refresh' : 'Pull down to refresh' }}
            </span>
          </div>
        </div>


          <div v-if="isLoadingSetups" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
            <p class="text-gray-700 dark:text-gray-300">Loading bow setups...</p>
          </div>

          <div v-else>
            <!-- Add New Setup Button - Only show when setups exist -->
            <div v-if="bowSetups.length > 0" class="flex justify-center mb-6">
              <CustomButton
                @click="openAddSetupModal"
                variant="filled"
                class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700 w-full md:w-auto touch-target mobile-safe-button"
              >
                <i class="fas fa-plus mr-2"></i>
                Add New Setup
              </CustomButton>
            </div>
            <!-- Bow Setup Cards - Responsive Grid -->
            <div
              v-if="bowSetups.length > 0"
              class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              <div
                v-for="(setup, index) in bowSetups"
                :key="setup.id"
                class="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                @click="handleBowSetupClick(setup, index)"
              >
                    <!-- Card Header -->
                    <div class="mb-4">
                      <!-- Setup Name and Type -->
                      <div class="mb-3">
                        <h4 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                          {{ setup.name }}
                        </h4>
                        <div class="flex items-center">
                          <span class="text-sm font-medium text-gray-500 dark:text-gray-400 inline-flex items-center">
                            <i class="fas fa-bow-arrow mr-1.5 text-blue-500"></i>
                            {{ formatBowType(setup.bow_type) }}
                          </span>
                        </div>
                      </div>
                      
                    </div>
                  
                  <!-- Main Bow Information - Improved Layout -->
                  <div class="space-y-4">
                    <!-- Key Specifications Grid -->
                    <div class="bg-gray-50 dark:bg-gray-700/30 p-3 rounded-lg">
                      <div class="grid grid-cols-2 gap-4">
                        <div class="text-center">
                          <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ setup.draw_weight }}</div>
                          <div class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mt-1">Draw Weight (lbs)</div>
                        </div>
                        <div v-if="setup.draw_length" class="text-center">
                          <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ setup.draw_length }}"</div>
                          <div class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mt-1">Draw Length</div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Bow Model Information -->
                    <div v-if="setup.bow_type === 'compound' && setup.compound_brand" class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800">
                      <div class="flex items-center justify-between">
                        <div>
                          <div class="font-semibold text-gray-900 dark:text-gray-100">{{ setup.compound_brand }} {{ setup.compound_model }}</div>
                          <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">Compound Bow</div>
                        </div>
                        <div v-if="setup.ibo_speed" class="text-right">
                          <div class="text-lg font-bold text-blue-600 dark:text-blue-400">{{ setup.ibo_speed }}</div>
                          <div class="text-xs text-gray-600 dark:text-gray-400">fps</div>
                        </div>
                      </div>
                    </div>
                    <div v-else-if="setup.riser_brand" class="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg border border-purple-200 dark:border-purple-800">
                      <div class="font-semibold text-gray-900 dark:text-gray-100">{{ setup.riser_brand }} {{ setup.riser_model }}</div>
                      <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">Recurve Bow</div>
                    </div>
                    
                    <!-- Status Summary -->
                    <div class="flex items-center justify-between py-2">
                      <!-- Usage Tags -->
                      <div class="flex flex-wrap gap-1.5">
                        <span v-for="usage in getBowUsageArray(setup.bow_usage)" :key="usage"
                              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border border-blue-200 dark:border-blue-700">
                          {{ formatBowUsage(usage) }}
                        </span>
                      </div>
                      
                      <!-- Equipment Count Badges and Expand Button -->
                      <div class="flex items-center justify-between gap-3">
                        <div class="flex items-center gap-3">
                          <div v-if="setup.arrows && setup.arrows.length > 0" class="flex items-center gap-1.5 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded-full">
                            <i class="fas fa-location-arrow text-xs text-green-600 dark:text-green-400"></i>
                            <span class="text-xs font-medium text-green-800 dark:text-green-300">{{ setup.arrows.length }} arrow{{ setup.arrows.length === 1 ? '' : 's' }}</span>
                          </div>
                          <div v-if="setup.equipment && setup.equipment.length > 0" class="flex items-center gap-1.5 bg-purple-100 dark:bg-purple-900/30 px-2 py-1 rounded-full">
                            <i class="fas fa-cogs text-xs text-purple-600 dark:text-purple-400"></i>
                            <span class="text-xs font-medium text-purple-800 dark:text-purple-300">{{ setup.equipment.length }} item{{ setup.equipment.length === 1 ? '' : 's' }}</span>
                          </div>
                        </div>
                        
                        <!-- Expand/Collapse Toggle -->
                        <button
                          @click.stop="toggleCardExpansion(setup.id)"
                          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                          :title="expandedCards[setup.id] ? 'Show less' : 'Show more'"
                        >
                          <i 
                            class="fas text-gray-500 dark:text-gray-400 transition-transform duration-200"
                            :class="expandedCards[setup.id] ? 'fa-chevron-up' : 'fa-chevron-down'"
                          ></i>
                        </button>
                      </div>
                    </div>
                    
                    <!-- Phase 3: Expanded Information Panel -->
                    <div 
                      v-if="expandedCards[setup.id]" 
                      class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 animate-fadeIn"
                    >
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Equipment Summary -->
                        <div class="space-y-3">
                          <h5 class="mobile-body-medium font-semibold text-gray-900 dark:text-gray-100 flex items-center">
                            <i class="fas fa-cog text-purple-600 dark:text-purple-400 mr-2"></i>
                            Equipment
                          </h5>
                          <div class="space-y-2 text-sm">
                            <div v-if="setup.equipment && setup.equipment.length > 0">
                              <div v-for="equip in setup.equipment.slice(0, 3)" :key="equip.id" 
                                   class="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
                                <span class="font-medium">{{ equip.category }}</span>
                                <span class="text-gray-600 dark:text-gray-400 text-xs">{{ equip.brand || 'Custom' }}</span>
                              </div>
                              <div v-if="setup.equipment.length > 3" class="text-xs text-gray-500 text-center py-1">
                                +{{ setup.equipment.length - 3 }} more items
                              </div>
                            </div>
                            <div v-else class="text-gray-500 dark:text-gray-400 text-xs italic">
                              No equipment configured
                            </div>
                          </div>
                        </div>

                        <!-- Arrow Information -->
                        <div class="space-y-3">
                          <h5 class="mobile-body-medium font-semibold text-gray-900 dark:text-gray-100 flex items-center">
                            <i class="fas fa-bullseye text-green-600 dark:text-green-400 mr-2"></i>
                            Arrows
                          </h5>
                          <div class="space-y-2 text-sm">
                            <div v-if="setup.arrows && setup.arrows.length > 0">
                              <div v-for="arrow in setup.arrows.slice(0, 2)" :key="arrow.id" 
                                   class="p-2 bg-gray-50 dark:bg-gray-700 rounded">
                                <div class="font-medium">{{ arrow.manufacturer }} {{ arrow.model_name }}</div>
                                <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                  Length: {{ arrow.arrow_length }}" • Weight: {{ arrow.point_weight }}gr
                                </div>
                              </div>
                              <div v-if="setup.arrows.length > 2" class="text-xs text-gray-500 text-center py-1">
                                +{{ setup.arrows.length - 2 }} more arrows
                              </div>
                            </div>
                            <div v-else class="text-gray-500 dark:text-gray-400 text-xs italic">
                              No arrows configured
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Quick Action Bar -->
                      <div class="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                        <div class="flex flex-wrap gap-2">
                          <CustomButton
                            @click="navigateToCalculatorWithSetup(setup.id)"
                            variant="filled"
                            size="small"
                            class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-xs"
                          >
                            <i class="fas fa-calculator mr-1"></i>
                            Calculate Spine
                          </CustomButton>
                          <CustomButton
                            @click="navigateToBowDetail(setup.id)"
                            variant="outlined"
                            size="small"
                            class="text-green-600 border-green-600 hover:bg-green-50 dark:text-green-400 dark:border-green-400 text-xs"
                          >
                            <i class="fas fa-edit mr-1"></i>
                            Edit Setup
                          </CustomButton>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
            
            <!-- Empty State -->
            <div v-else class="text-center py-12">
              <i class="fas fa-bow-arrow text-6xl text-gray-300 dark:text-gray-600 mb-4"></i>
              <h4 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">No Bow Setups Yet</h4>
              <p class="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                Get started by creating your first bow setup. Add your bow specifications and start finding the perfect arrows.
              </p>
              <CustomButton
                @click="openAddSetupModal"
                variant="filled"
                class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
              >
                <i class="fas fa-plus mr-2"></i>
                Create Your First Setup
              </CustomButton>
            </div>
          </div>

        <!-- Add/Edit Bow Setup Modal -->
        <AddBowSetupModal
          v-if="isAddingSetup"
          :modelValue="newSetup"
          :isSaving="isSavingSetup"
          :error="addSetupError"
          @update:modelValue="newSetup = $event"
          @save="handleSaveBowSetup"
          @close="closeAddSetupModal"
        />

        <!-- Confirm Delete Modal -->
        <div v-if="isConfirmingDelete" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center modal-overlay p-4">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-lg text-center">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Confirm Deletion</h3>
            <p class="text-gray-700 dark:text-gray-300 mb-6">Are you sure you want to delete this bow setup?</p>
            <div class="flex justify-center space-x-4">
              <CustomButton
                @click="cancelDeleteSetup"
                variant="outlined"
                class="text-gray-700 dark:text-gray-200"
              >
                Cancel
              </CustomButton>
              <CustomButton
                @click="deleteSetup"
                variant="filled"
                class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
              >
                Delete
              </CustomButton>
            </div>
            <p v-if="deleteSetupError" class="text-red-500 text-sm mt-3">{{ deleteSetupError }}</p>
          </div>
        </div>
        <!-- End of Confirm Delete Modal -->

        <!-- Edit Arrow Modal -->
        <EditArrowModal
          :is-open="isEditArrowModalOpen"
          :arrow-setup="editingArrowSetup"
          @close="closeEditArrowModal"
          @arrow-updated="handleArrowUpdated"
          @error="handleArrowEditError"
        />
        <!-- End of Edit Arrow Modal -->

        <!-- Mobile Action Sheet for Bow Setup Actions -->
        <MobileActionSheet
          v-model="showBowActionSheet"
          title="Bow Setup Actions"
          :subtitle="selectedSetupForActions?.name"
          :actions="bowActionSheetActions"
          :show-cancel="true"
          cancel-text="Cancel"
          @action="handleBowActionSheetAction"
          @cancel="showBowActionSheet = false"
        />

        <!-- Arrow Removal Confirmation Modal -->
        <div v-if="arrowRemovalConfirm.show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center modal-overlay p-4 z-50">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-lg text-center">
            <div class="mb-4">
              <i class="fas fa-exclamation-triangle text-yellow-500 text-4xl mb-2"></i>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Remove Arrow</h3>
            </div>
            <p class="text-gray-700 dark:text-gray-300 mb-6">
              Are you sure you want to remove "{{ arrowRemovalConfirm.arrowName }}" from this setup?
            </p>
            <div class="flex justify-center space-x-4">
              <CustomButton
                @click="hideArrowRemovalConfirm"
                variant="outlined"
                class="text-gray-700 dark:text-gray-200"
              >
                Cancel
              </CustomButton>
              <CustomButton
                @click="confirmRemoveArrow"
                variant="filled"
                class="bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
              >
                Remove
              </CustomButton>
            </div>
          </div>
        </div>
        <!-- End of Arrow Removal Confirmation Modal -->


      </div>
      <!-- End of Bow Setups Section -->
    </div>
    <!-- End of v-else-if="user" section -->

    <div v-else>
      <p class="text-gray-700 dark:text-gray-300 mb-4">
        You are not logged in. Please log in to view your profile.
      </p>
      <CustomButton
        @click="loginWithGoogle"
        variant="filled"
        class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
      >
        Login with Google
      </CustomButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { useBowSetupPickerStore } from '~/stores/bowSetupPicker';
import { useAuth } from '~/composables/useAuth';
import BowSetupArrowsList from '~/components/BowSetupArrowsList.vue';
import AddBowSetupModal from '~/components/AddBowSetupModal.vue';
import EditArcherProfileModal from '~/components/EditArcherProfileModal.vue';
import EditArrowModal from '~/components/EditArrowModal.vue';
import ImageUpload from '~/components/ImageUpload.vue';
import MobileActionSheet from '~/components/MobileActionSheet.vue';

const { user, logout, loginWithGoogle, updateUserProfile, fetchUser, fetchBowSetups, addBowSetup, updateBowSetup, deleteBowSetup, addArrowToSetup, fetchSetupArrows, deleteArrowFromSetup, updateArrowInSetup } = useAuth();
const bowSetupPickerStore = useBowSetupPickerStore();

const isLoadingUser = ref(true);
const isEditing = ref(false);
const isSaving = ref(false);
const editError = ref(null);

const bowSetups = ref([]);
const isLoadingSetups = ref(true);
const isAddingSetup = ref(false);

// Phase 3: Expandable card state
const expandedCard = ref(null);
const expandedCards = ref({});

// Phase 3: Inline editing state
const editingSetupName = ref(null);
const editedSetupName = ref('');
const setupNameInput = ref(null);

// Phase 3: Swipe gesture state
const swipeState = ref({});
const touchStartX = ref(0);
const touchStartY = ref(0);
const touchStartTime = ref(0);

// Phase 3: Pull-to-refresh state
const pullToRefresh = ref({
  isRefreshing: false,
  startY: 0,
  currentY: 0,
  threshold: 80,
  isTriggered: false,
  isPulling: false
});

// Phase 3: Mobile components state
const showBowActionSheet = ref(false);
const selectedSetupForActions = ref(null);
const bowActionSheetActions = ref([
  {
    id: 'calculator',
    label: 'Find Arrows',
    description: 'Calculate optimal arrows for this setup',
    icon: 'fas fa-calculator',
    iconColor: 'blue-500'
  },
  {
    id: 'edit',
    label: 'Edit Setup',
    description: 'Modify bow configuration',
    icon: 'fas fa-edit',
    iconColor: 'green-500'
  },
  {
    id: 'duplicate',
    label: 'Duplicate Setup',
    description: 'Create a copy of this setup',
    icon: 'fas fa-copy',
    iconColor: 'purple-500'
  },
  {
    id: 'performance',
    label: 'Performance Analysis',
    description: 'View arrow performance metrics',
    icon: 'fas fa-chart-line',
    iconColor: 'orange-500'
  },
  {
    id: 'delete',
    label: 'Delete Setup',
    description: 'Permanently remove this setup',
    icon: 'fas fa-trash',
    iconColor: 'red-500',
    destructive: true
  }
]);
const isSavingSetup = ref(false);
const addSetupError = ref(null);
const isConfirmingDelete = ref(false);
const setupToDeleteId = ref(null);
const deleteSetupError = ref(null);
const isEditMode = ref(false);
const editingSetupId = ref(null);

// Edit arrow modal state
const isEditArrowModalOpen = ref(false);
const editingArrowSetup = ref(null);

// Mobile Action Sheet state for MobileActionSheet component
// const showBowActionSheet = ref(false); // Already declared above
// const selectedSetupForActions = ref(null); // Already declared above

// Notification state
const notification = ref({
  show: false,
  message: '',
  type: 'success' // 'success', 'error', 'warning'
});

// Arrow removal confirmation state
const arrowRemovalConfirm = ref({
  show: false,
  arrowSetupId: null,
  arrowName: ''
});


const newSetup = ref({
  name: '',
  bow_type: '',
  draw_weight: 45,
  draw_length: 28, // Unified draw length field
  arrow_length: null,
  point_weight: 100,
  description: '',
  bow_usage: [],
});

const openEditModal = () => {
  isEditing.value = true;
  editError.value = null;
};

const closeEditModal = () => {
  isEditing.value = false;
};

// Toggle card expansion
const toggleCardExpansion = (setupId) => {
  if (expandedCards.value[setupId]) {
    delete expandedCards.value[setupId];
  } else {
    expandedCards.value[setupId] = true;
  }
};

const saveProfile = async (profileData) => {
  isSaving.value = true;
  editError.value = null;
  try {
    await updateUserProfile(profileData);
    closeEditModal();
  } catch (err) {
    console.error('Error saving profile:', err);
    editError.value = err.message || 'Failed to save profile.';
  } finally {
    isSaving.value = false;
  }
};

const loadBowSetups = async () => {
  isLoadingSetups.value = true;
  try {
    const setups = await fetchBowSetups();
    bowSetups.value = setups;
    
    // Load arrows for each setup
    await loadArrowsForAllSetups();
  } catch (err) {
    console.error('Error loading bow setups:', err);
    // Optionally display an error message to the user
  } finally {
    isLoadingSetups.value = false;
  }
};

const loadArrowsForAllSetups = async () => {
  // Load arrows for each setup in parallel
  const arrowPromises = bowSetups.value.map(async (setup) => {
    try {
      setup.loadingArrows = true;
      const arrows = await fetchSetupArrows(setup.id);
      setup.arrows = arrows || [];
    } catch (err) {
      console.error(`Error loading arrows for setup ${setup.id}:`, err);
      setup.arrows = [];
    } finally {
      setup.loadingArrows = false;
    }
  });
  
  await Promise.all(arrowPromises);
};

const openAddSetupModal = () => {
  // Reset form for new entry
  isEditMode.value = false;
  editingSetupId.value = null;
  newSetup.value = {
    name: '',
    bow_type: '',
    draw_weight: 45,
    draw_length: 28, // Unified draw length field
    description: '',
    bow_usage: [],
  };
  addSetupError.value = null;
  isAddingSetup.value = true;
};

const closeAddSetupModal = () => {
  isAddingSetup.value = false;
  isEditMode.value = false;
  editingSetupId.value = null;
};

const openEditBowSetupModal = (setup) => {
  // Populate form with existing setup data
  isEditMode.value = true;
  editingSetupId.value = setup.id;
  
  // Pass the setup data to the modal - it will handle the field mapping
  newSetup.value = {
    name: setup.name || '',
    bow_type: setup.bow_type || '',
    draw_weight: setup.draw_weight || 45,
    description: setup.description || '',
    bow_usage: setup.bow_usage ? JSON.parse(setup.bow_usage) : [],
    // Pass existing brand data for the modal to handle
    compound_brand: setup.compound_brand || '',
    compound_model: setup.compound_model || '',
    ibo_speed: setup.ibo_speed || '',
    draw_length: setup.draw_length || 28, // Unified draw length field
    riser_brand: setup.riser_brand || '',
    riser_model: setup.riser_model || '',
    riser_length: setup.riser_length || '',
    limb_brand: setup.limb_brand || '',
    limb_model: setup.limb_model || '',
    limb_length: setup.limb_length || '',
  };
  
  isAddingSetup.value = true;
  addSetupError.value = null;
};

const handleSaveBowSetup = async (setupData) => {
  isSavingSetup.value = true;
  addSetupError.value = null;
  try {
    // The setupData from the modal is already correctly formatted.
    // We just need to ensure draw_length is present if it's a new setup.
    if (!setupData.draw_length) {
      setupData.draw_length = user.value?.draw_length || 28.0;
    }

    let savedSetupId;
    if (isEditMode.value && editingSetupId.value) {
      await updateBowSetup(editingSetupId.value, setupData);
      savedSetupId = editingSetupId.value;
    } else {
      savedSetupId = await addBowSetup(setupData);
    }
    
    closeAddSetupModal();
    await loadBowSetups();
    
    // Refresh bow selector navigation cache after successful save
    if (savedSetupId && bowSetupPickerStore.refreshSelectedBowSetup) {
      await bowSetupPickerStore.refreshSelectedBowSetup(savedSetupId);
    }
  } catch (err) {
    console.error('Error saving bow setup:', err);
    addSetupError.value = err.message || `Failed to ${isEditMode.value ? 'update' : 'add'} bow setup.`;
  } finally {
    isSavingSetup.value = false;
  }
};

const confirmDeleteSetup = (id) => {
  setupToDeleteId.value = id;
  deleteSetupError.value = null;
  isConfirmingDelete.value = true;
};

const cancelDeleteSetup = () => {
  setupToDeleteId.value = null;
  isConfirmingDelete.value = false;
};

const deleteSetup = async () => {
  if (!setupToDeleteId.value) return;

  isSavingSetup.value = true; // Use this for delete loading state too
  deleteSetupError.value = null;
  try {
    await deleteBowSetup(setupToDeleteId.value);
    cancelDeleteSetup();
    await loadBowSetups(); // Reload setups after deleting
  } catch (err) {
    console.error('Error deleting bow setup:', err);
    deleteSetupError.value = err.message || 'Failed to delete bow setup.';
  } finally {
    isSavingSetup.value = false;
  }
};

// Navigation methods
const navigateToArrowCalculator = (setup) => {
  // Store the selected setup in localStorage for the calculator to pick up
  localStorage.setItem('selectedBowSetup', JSON.stringify(setup));
  
  // Navigate to the arrow calculator page
  navigateTo('/calculator');
};

const navigateToCalculatorWithSetup = (setupId) => {
  navigateTo(`/calculator?setupId=${setupId}`);
};


// Edit arrow modal methods
const openEditArrowModal = (arrowSetup) => {
  editingArrowSetup.value = arrowSetup;
  isEditArrowModalOpen.value = true;
};

const closeEditArrowModal = () => {
  editingArrowSetup.value = null;
  isEditArrowModalOpen.value = false;
};

const handleArrowUpdated = async (updatedArrowData) => {
  // Reload arrows for the bow setup to show updated data
  const setupId = editingArrowSetup.value?.setup_id;
  if (setupId) {
    await loadArrowsForSetup(setupId);
  }
  
  // Close the modal
  closeEditArrowModal();
  
  // Show success message
  showNotification('Arrow settings updated successfully!');
};

const handleArrowEditError = (errorMessage) => {
  showNotification(errorMessage, 'error');
};

const loadArrowsForSetup = async (setupId) => {
  const setup = bowSetups.value.find(s => s.id === setupId);
  if (!setup) return;
  
  try {
    setup.loadingArrows = true;
    const arrows = await fetchSetupArrows(setupId);
    setup.arrows = arrows || [];
  } catch (err) {
    console.error(`Error loading arrows for setup ${setupId}:`, err);
    setup.arrows = [];
  } finally {
    setup.loadingArrows = false;
  }
};


const removeArrowFromSetup = async (arrowSetupId, arrowName = 'arrow') => {
  // Show confirmation dialog instead of alert
  showArrowRemovalConfirm(arrowSetupId, arrowName);
};

const confirmRemoveArrow = async () => {
  const arrowSetupId = arrowRemovalConfirm.value.arrowSetupId;
  hideArrowRemovalConfirm();
  
  try {
    await deleteArrowFromSetup(arrowSetupId);
    
    // Reload all bow setups to refresh the arrows lists 
    await loadBowSetups();
    
    showNotification('Arrow removed successfully!');
  } catch (err) {
    console.error('Error removing arrow from setup:', err);
    showNotification('Failed to remove arrow. Please try again.', 'error');
  }
};

const viewArrowDetails = (arrowId) => {
  // Navigate to arrow details page
  navigateTo(`/arrows/${arrowId}`);
};

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

// Arrow removal confirmation helpers
const showArrowRemovalConfirm = (arrowSetupId, arrowName) => {
  arrowRemovalConfirm.value = {
    show: true,
    arrowSetupId,
    arrowName
  };
};

const hideArrowRemovalConfirm = () => {
  arrowRemovalConfirm.value = {
    show: false,
    arrowSetupId: null,
    arrowName: ''
  };
};

// Helper functions for display formatting
const formatSkillLevel = (level) => {
  const levels = {
    'beginner': 'Beginner',
    'intermediate': 'Intermediate', 
    'advanced': 'Advanced'
  };
  return levels[level] || level;
};

const formatShootingStyles = (styles) => {
  const styleLabels = {
    'target': 'Target',
    'hunting': 'Hunting',
    'traditional': 'Traditional',
    '3d': '3D'
  };
  
  if (!styles || !Array.isArray(styles)) {
    return 'Target'; // Default fallback
  }
  
  return styles.map(style => styleLabels[style] || style).join(', ');
};

const getSkillLevelClass = (level) => {
  const classes = {
    'beginner': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'intermediate': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'advanced': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  };
  return classes[level] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
};

const getShootingStyleClass = (styles) => {
  // For multiple styles, use a neutral color
  if (!styles || !Array.isArray(styles) || styles.length === 0) {
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
  }
  
  if (styles.length > 1) {
    return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200';
  }
  
  // Single style, use specific color
  const classes = {
    'target': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'hunting': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'traditional': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    '3d': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  };
  return classes[styles[0]] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
};

// Helper function to parse bow usage from JSON string
const getBowUsageArray = (bowUsage) => {
  if (!bowUsage) return [];
  try {
    return Array.isArray(bowUsage) ? bowUsage : JSON.parse(bowUsage);
  } catch {
    return [bowUsage]; // If not JSON, treat as single string
  }
};

// Helper function to format bow usage for display
const formatBowUsage = (usage) => {
  const usageMap = {
    'target': 'Target',
    'hunting': 'Hunting',
    'field': 'Field',
    '3d': '3D',
    'traditional': 'Traditional',
    'competition': 'Competition',
    'recreational': 'Recreational',
    'indoor': 'Indoor',
    'outdoor': 'Outdoor'
  };
  return usageMap[usage] || usage;
};

// Helper function to get equipment category icons
const getCategoryIcon = (categoryName) => {
  const iconMap = {
    'String': 'fas fa-link',
    'Sight': 'fas fa-crosshairs',
    'Stabilizer': 'fas fa-balance-scale',
    'Arrow Rest': 'fas fa-hand-paper',
    'Weight': 'fas fa-weight-hanging'
  };
  return iconMap[categoryName] || 'fas fa-cog';
};


// Phase 3: Inline editing methods
const startEditSetupName = (setupId, currentName) => {
  editingSetupName.value = setupId;
  editedSetupName.value = currentName;
  nextTick(() => {
    if (setupNameInput.value) {
      setupNameInput.value.focus();
      setupNameInput.value.select();
    }
  });
};

const cancelEditSetupName = () => {
  editingSetupName.value = null;
  editedSetupName.value = '';
};

const saveSetupName = async (setupId) => {
  if (!editedSetupName.value.trim()) {
    cancelEditSetupName();
    return;
  }
  
  const setup = bowSetups.value.find(s => s.id === setupId);
  if (!setup || setup.name === editedSetupName.value.trim()) {
    cancelEditSetupName();
    return;
  }
  
  try {
    // Update setup name via API
    await updateBowSetup(setupId, { name: editedSetupName.value.trim() });
    
    // Update local state
    setup.name = editedSetupName.value.trim();
    
    cancelEditSetupName();
  } catch (error) {
    console.error('Error updating setup name:', error);
    // Could add error notification here
    cancelEditSetupName();
  }
};

// Phase 3: Swipe gesture methods
const initSwipeState = (setupId) => {
  if (!swipeState.value[setupId]) {
    swipeState.value[setupId] = {
      transform: 'translateX(0)',
      showActions: false,
      showActionsLeft: false,
      isDragging: false
    };
  }
};

const handleTouchStart = (event, setupId) => {
  initSwipeState(setupId);
  const touch = event.touches[0];
  touchStartX.value = touch.clientX;
  touchStartY.value = touch.clientY;
  touchStartTime.value = Date.now();
  swipeState.value[setupId].isDragging = true;
};

const handleTouchMove = (event, setupId) => {
  if (!swipeState.value[setupId]?.isDragging) return;
  
  const touch = event.touches[0];
  const deltaX = touch.clientX - touchStartX.value;
  const deltaY = touch.clientY - touchStartY.value;
  
  // Only handle horizontal swipes (ignore vertical scrolling)
  if (Math.abs(deltaY) > Math.abs(deltaX)) return;
  
  event.preventDefault(); // Prevent scrolling when swiping horizontally
  
  // Limit swipe distance
  const maxSwipe = 120;
  const clampedDelta = Math.max(-maxSwipe, Math.min(maxSwipe, deltaX));
  
  swipeState.value[setupId].transform = `translateX(${clampedDelta}px)`;
  swipeState.value[setupId].showActions = clampedDelta < -40;
  swipeState.value[setupId].showActionsLeft = clampedDelta > 40;
};

const handleTouchEnd = (event, setupId) => {
  if (!swipeState.value[setupId]?.isDragging) return;
  
  const touch = event.changedTouches[0];
  const deltaX = touch.clientX - touchStartX.value;
  const deltaTime = Date.now() - touchStartTime.value;
  
  swipeState.value[setupId].isDragging = false;
  
  // Determine final state based on swipe distance and velocity
  const swipeThreshold = 60;
  const isQuickSwipe = deltaTime < 200 && Math.abs(deltaX) > 30;
  
  if (deltaX < -swipeThreshold || (isQuickSwipe && deltaX < 0)) {
    // Show right actions (swipe left)
    swipeState.value[setupId].transform = 'translateX(-120px)';
    swipeState.value[setupId].showActions = true;
    swipeState.value[setupId].showActionsLeft = false;
  } else if (deltaX > swipeThreshold || (isQuickSwipe && deltaX > 0)) {
    // Show left actions (swipe right)
    swipeState.value[setupId].transform = 'translateX(120px)';
    swipeState.value[setupId].showActions = false;
    swipeState.value[setupId].showActionsLeft = true;
  } else {
    // Reset to center
    resetSwipeState(setupId);
  }
};

const resetSwipeState = (setupId) => {
  if (swipeState.value[setupId]) {
    swipeState.value[setupId].transform = 'translateX(0)';
    swipeState.value[setupId].showActions = false;
    swipeState.value[setupId].showActionsLeft = false;
  }
};

const resetAllSwipeStates = () => {
  Object.keys(swipeState.value).forEach(setupId => {
    resetSwipeState(setupId);
  });
};

// Phase 3: Pull-to-refresh methods
const handlePullStart = (event) => {
  // Only trigger pull-to-refresh at the top of the page
  if (window.scrollY > 10) return;
  
  const touch = event.touches[0];
  pullToRefresh.value.startY = touch.clientY;
  pullToRefresh.value.isPulling = true;
  pullToRefresh.value.isTriggered = false;
};

const handlePullMove = (event) => {
  if (!pullToRefresh.value.isPulling || window.scrollY > 10) return;
  
  const touch = event.touches[0];
  const deltaY = touch.clientY - pullToRefresh.value.startY;
  
  // Only allow pulling down
  if (deltaY < 0) return;
  
  pullToRefresh.value.currentY = deltaY;
  
  // Trigger threshold reached
  if (deltaY > pullToRefresh.value.threshold && !pullToRefresh.value.isTriggered) {
    pullToRefresh.value.isTriggered = true;
    // Haptic feedback if available
    if (window.navigator.vibrate) {
      window.navigator.vibrate(50);
    }
  } else if (deltaY <= pullToRefresh.value.threshold && pullToRefresh.value.isTriggered) {
    pullToRefresh.value.isTriggered = false;
  }
};

const handlePullEnd = () => {
  if (!pullToRefresh.value.isPulling) return;
  
  pullToRefresh.value.isPulling = false;
  
  if (pullToRefresh.value.isTriggered && !pullToRefresh.value.isRefreshing) {
    // Trigger refresh
    performPullToRefresh();
  }
  
  // Reset state
  pullToRefresh.value.currentY = 0;
  pullToRefresh.value.isTriggered = false;
};

const performPullToRefresh = async () => {
  if (pullToRefresh.value.isRefreshing) return;
  
  pullToRefresh.value.isRefreshing = true;
  
  try {
    // Refresh user data and bow setups
    await Promise.all([
      fetchUser(),
      loadBowSetups()
    ]);
    
    // Add a minimum refresh time for better UX
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    showNotification('Setup data refreshed!', 'success');
  } catch (error) {
    console.error('Error refreshing data:', error);
    showNotification('Failed to refresh data', 'error');
  } finally {
    pullToRefresh.value.isRefreshing = false;
  }
};

// Mobile Card Stack event handlers
const handleBowSetupClick = (setup, index) => {
  // Main click action - navigate to bow setup details
  navigateToBowDetail(setup.id);
};

const handleBowSetupEdit = (setup, index) => {
  navigateToBowDetail(setup.id);
};

const handleBowSetupDelete = (setup, index) => {
  confirmDeleteSetup(setup.id);
};

const handleBowSetupExpand = (key, isExpanded) => {
  // The expansion is handled by the MobileCardStack component internally
  console.log(`Bow setup ${key} ${isExpanded ? 'expanded' : 'collapsed'}`);
};

// Mobile Action Sheet event handlers
const handleBowActionSheetAction = ({ action, index }) => {
  const setup = selectedSetupForActions.value;
  if (!setup) return;

  switch (action.id) {
    case 'edit':
      navigateToBowDetail(setup.id);
      break;
    case 'duplicate':
      // TODO: Implement setup duplication
      showNotification('Setup duplication coming soon!', 'info');
      break;
    case 'performance':
      // TODO: Navigate to performance analysis
      showNotification('Performance analysis coming soon!', 'info');
      break;
    case 'delete':
      confirmDeleteSetup(setup.id);
      break;
  }
  
  // Close the action sheet
  showBowActionSheet.value = false;
  selectedSetupForActions.value = null;
};

// Profile picture upload handlers
const handleProfilePictureUpload = async (imageUrl) => {
  try {
    // Update the user's profile picture URL locally first for immediate feedback
    if (user.value) {
      user.value.profile_picture_url = imageUrl;
    }
    
    // The API endpoint already updates the database, so we just show success
    showNotification('Profile picture updated successfully!');
    
    // Refresh user data to ensure everything is in sync
    await fetchUser();
  } catch (error) {
    console.error('Profile picture update error:', error);
    showNotification('Profile picture updated, but there was an issue syncing data.', 'warning');
  }
};

const handleProfilePictureRemoval = async () => {
  try {
    // Update user profile to remove picture URL
    await updateUserProfile({ profile_picture_url: null });
    
    // Update local user object
    if (user.value) {
      user.value.profile_picture_url = null;
    }
    
    showNotification('Profile picture removed successfully!');
  } catch (error) {
    console.error('Profile picture removal error:', error);
    showNotification('Failed to remove profile picture. Please try again.', 'error');
  }
};

const handleUploadError = (errorMessage) => {
  showNotification(errorMessage, 'error');
};

// Dashboard computed properties
const totalArrows = computed(() => {
  return bowSetups.value.reduce((total, setup) => {
    return total + (setup.arrows ? setup.arrows.length : 0);
  }, 0);
});

const averageDrawWeight = computed(() => {
  if (bowSetups.value.length === 0) return '0 lbs';
  
  const totalWeight = bowSetups.value.reduce((total, setup) => {
    return total + (setup.draw_weight || 0);
  }, 0);
  
  const average = totalWeight / bowSetups.value.length;
  return `${Math.round(average)} lbs`;
});

onMounted(async () => {
  // Ensure user data is fetched on page load
  if (!user.value) {
    await fetchUser();
  }
  isLoadingUser.value = false;
  
  // Load bow setups only if user is logged in
  if (user.value) {
    await loadBowSetups();
  }
  
  // Check if we should open the add setup modal
  const route = useRoute();
  if (route.query.add === 'true') {
    openAddSetupModal();
  }
});

// Navigation methods
const navigateToBowDetail = (setupId) => {
  navigateTo(`/setups/${setupId}`);
};


const formatBowType = (bowType) => {
  if (!bowType) return 'Unknown';
  return bowType.charAt(0).toUpperCase() + bowType.slice(1);
};

// Watch for changes in the user object and reload bow setups
watch(user, async (newUser) => {
  if (newUser) {
    // If user just logged in or user object changed, reload bow setups
    await loadBowSetups();
  }
}, { immediate: true });

definePageMeta({
  middleware: ['auth-check']
});
</script>

<style scoped>
/* Custom action button styles for MobileCardStack */
.action-button.action-edit {
  @apply bg-green-500/20;
}

.action-button.action-menu {
  @apply bg-blue-500/20;
}

.action-button.action-search {
  @apply bg-blue-500/20;
}

.action-button.action-delete {
  @apply bg-red-500/20;
}
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
.form-textarea {
  @apply w-full h-24 resize-y;
}

/* Mobile-safe content positioning to avoid bottom navigation overlap */
.mobile-safe-content {
  @apply pb-24 md:pb-8; /* Extra padding on mobile for bottom nav */
}

/* Mobile-safe button positioning */
.mobile-safe-button {
  @apply mb-6 md:mb-4; /* Extra margin on mobile */
}

/* Ensure content doesn't get hidden behind mobile navigation */
@media (max-width: 768px) {
  .mobile-safe-content {
    padding-bottom: calc(96px + env(safe-area-inset-bottom)) !important; /* Bottom nav height + safe area */
  }
  
  .mobile-safe-button {
    margin-bottom: 2rem !important; /* Extra spacing for buttons on mobile */
  }
}
</style>