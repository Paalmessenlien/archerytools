<template>
  <div>
    <!-- Beta Notice Banner -->
    <div class="mb-6 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
      <div class="flex items-center">
        <i class="fas fa-flask text-orange-600 dark:text-orange-400 mr-3"></i>
        <div>
          <h4 class="text-sm font-medium text-orange-800 dark:text-orange-200">Beta Testing Phase</h4>
          <p class="text-xs text-orange-700 dark:text-orange-300 mt-1">
            This platform is in beta. Features may change and data may be reset. Invitation-only access.
          </p>
        </div>
      </div>
    </div>

    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Arrow Tuning Platform</h1>
      <p class="text-gray-600 dark:text-gray-300">Manage your bow setups and arrow configurations for personalized recommendations</p>
    </div>

    <!-- Navigation Tabs -->
    <div class="mb-6">
      <div class="border-b border-gray-200 dark:border-gray-700">
        <nav class="-mb-px flex space-x-8">
          <button
            @click="activeTab = 'tuning'"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === 'tuning'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            ]"
          >
            <i class="fas fa-crosshairs mr-2"></i>
            Quick Tuning
          </button>
          <button
            @click="activeTab = 'setups'"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === 'setups'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            ]"
          >
            <i class="fas fa-archive mr-2"></i>
            Bow Setups
          </button>
        </nav>
      </div>
    </div>

    <!-- Quick Tuning Tab -->
    <div v-if="activeTab === 'tuning'" class="card card-interactive glass-card">
      <!-- Bow Configuration Form -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Bow Type -->
        <div>
          <md-filled-select
            ref="bowTypeSelect"
            label="Bow Type"
            :value="bowConfig.bow_type"
            @change="updateBowConfig({ bow_type: $event.target.value })"
            class="w-full"
          >
            <md-select-option value="compound">
              <div slot="headline">Compound</div>
            </md-select-option>
            <md-select-option value="recurve">
              <div slot="headline">Recurve</div>
            </md-select-option>
            <md-select-option value="longbow">
              <div slot="headline">Longbow</div>
            </md-select-option>
            <md-select-option value="traditional">
              <div slot="headline">Traditional</div>
            </md-select-option>
          </md-filled-select>
        </div>

        <!-- Point Weight -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Point Weight: <span class="font-semibold text-primary">{{ bowConfig.point_weight || 125 }} gr</span>
          </label>
          <md-slider
            ref="pointWeightSlider"
            min="75"
            max="200"
            step="25"
            :value="bowConfig.point_weight || 125"
            @input="updateBowConfig({ point_weight: parseInt($event.target.value) })"
            labeled
            ticks
            class="w-full"
          ></md-slider>
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
            <span>75 gr</span>
            <span>200 gr</span>
          </div>
        </div>

        <!-- Draw Weight -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Draw Weight: <span class="font-semibold text-primary">{{ bowConfig.draw_weight }} lbs</span>
          </label>
          <md-slider
            ref="drawWeightSlider"
            min="20"
            max="80"
            :value="bowConfig.draw_weight"
            @input="updateBowConfig({ draw_weight: parseInt($event.target.value) })"
            labeled
            ticks
            class="w-full"
          ></md-slider>
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
            <span>20 lbs</span>
            <span>80 lbs</span>
          </div>
        </div>



        <!-- Arrow Length -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Arrow Length: <span class="font-semibold text-primary">{{ bowConfig.arrow_length || 29 }}"</span>
          </label>
          <md-slider
            ref="arrowLengthSlider"
            min="24"
            max="34"
            step="0.5"
            :value="bowConfig.arrow_length || 29"
            @input="updateBowConfig({ arrow_length: parseFloat($event.target.value) })"
            labeled
            ticks
            class="w-full"
          ></md-slider>
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
            <span>24"</span>
            <span>34"</span>
          </div>
        </div>


      </div>


      <!-- Calculated Specifications -->
      <md-elevated-card class="mt-8 light-surface light-elevation">
        <div class="p-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            <i class="fas fa-calculator" style="margin-right: 8px; color: #6366f1;"></i>
            Calculated Specifications
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="flex flex-col">
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">
                <i class="fas fa-bullseye" style="margin-right: 6px; color: #6366f1;"></i>
                Recommended Spine:
              </p>
              <p class="font-semibold text-xl text-primary">{{ recommendedSpine || 'Calculating...' }}</p>
            </div>
            <div class="flex flex-col">
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">
                <i class="fas fa-crosshairs" style="margin-right: 6px; color: #7c3aed;"></i>
                Arrow Setup:
              </p>
              <p class="font-semibold text-gray-900 dark:text-gray-100">{{ arrowSetupDescription }}</p>
            </div>
          </div>
        </div>
      </md-elevated-card>

      <!-- Arrow Recommendations -->
      <div class="mt-8">
        <ArrowRecommendationsList 
          :bow-config="bowConfig"
          :show-search-filters="false"
          class="simplified-recommendations"
        />
      </div>

      <!-- Saved Arrow Setups -->
      <SavedArrowSetups 
        :saved-setups="savedArrowSetups"
        @remove-setup="removeArrowSetup"
      />
    </div>

    <!-- Bow Setups Tab -->
    <div v-if="activeTab === 'setups'">
      <!-- Bow Setups Management -->
      <div class="card card-interactive glass-card">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            <i class="fas fa-archive mr-2 text-indigo-600"></i>
            Your Bow Setups
          </h2>
          <CustomButton
            @click="showCreateSetupModal = true"
            variant="filled"
            class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
          >
            <i class="fas fa-plus mr-2"></i>
            Create Bow Setup
          </CustomButton>
        </div>

        <!-- Bow Setups List -->
        <div v-if="bowSetups.length > 0" class="space-y-4 mb-6">
          <div 
            v-for="setup in bowSetups" 
            :key="setup.id"
            class="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer"
            @click="selectBowSetup(setup)"
            :class="{ 'ring-2 ring-indigo-500': selectedBowSetup?.id === setup.id }"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h3 class="font-medium text-gray-900 dark:text-gray-100 mb-2">{{ setup.name }}</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div>
                    <span class="text-gray-600 dark:text-gray-400">Type:</span>
                    <span class="font-medium ml-1">{{ formatBowType(setup.bow_config?.bow_type) }}</span>
                  </div>
                  
                  <!-- Show bow type specific information -->
                  <div v-if="setup.bow_config?.bow_type === 'compound'">
                    <span class="text-gray-600 dark:text-gray-400">Brand:</span>
                    <span class="font-medium ml-1">{{ setup.bow_config?.brand || 'N/A' }}</span>
                  </div>
                  <div v-else-if="setup.bow_config?.bow_type === 'recurve'">
                    <span class="text-gray-600 dark:text-gray-400">Limb Fitting:</span>
                    <span class="font-medium ml-1">{{ setup.bow_config?.limb_fitting || 'N/A' }}</span>
                  </div>
                  <div v-else-if="setup.bow_config?.bow_type === 'longbow'">
                    <span class="text-gray-600 dark:text-gray-400">Brand:</span>
                    <span class="font-medium ml-1">{{ setup.bow_config?.bow_brand || 'N/A' }}</span>
                  </div>
                  <div v-else-if="setup.bow_config?.bow_type === 'traditional'">
                    <span class="text-gray-600 dark:text-gray-400">Construction:</span>
                    <span class="font-medium ml-1">{{ setup.bow_config?.construction ? formatBowType(setup.bow_config.construction.replace('_', ' ')) : 'N/A' }}</span>
                  </div>
                  
                  <div>
                    <span class="text-gray-600 dark:text-gray-400">Poundage:</span>
                    <span class="font-medium ml-1">{{ setup.bow_config?.poundage || setup.bow_config?.draw_weight }} lbs</span>
                  </div>
                  <div>
                    <span class="text-gray-600 dark:text-gray-400">Draw Length:</span>
                    <span class="font-medium ml-1">{{ setup.bow_config?.draw_length }}"</span>
                  </div>
                </div>
                <div v-if="setup.description" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  {{ setup.description }}
                </div>
              </div>
              <div class="flex space-x-2 ml-4">
                <CustomButton
                  @click.stop="editBowSetup(setup)"
                  variant="outlined"
                  size="small"
                  class="text-gray-600 dark:text-gray-400"
                >
                  <i class="fas fa-edit"></i>
                </CustomButton>
                <CustomButton
                  @click.stop="deleteBowSetup(setup)"
                  variant="outlined"
                  size="small"
                  class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900/20"
                >
                  <i class="fas fa-trash"></i>
                </CustomButton>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
          <i class="fas fa-archive text-4xl mb-4 opacity-50"></i>
          <p class="text-lg mb-2">No bow setups yet</p>
          <p class="text-sm">Create your first bow setup to get started with arrow configurations</p>
        </div>

        <!-- Selected Bow Setup Arrow Configurations -->
        <div v-if="selectedBowSetup" class="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <ArrowConfigurationsList 
            :configurations="getArrowConfigsForSetup(selectedBowSetup.id)"
            :bow-config="selectedBowSetup"
            @add-configuration="addArrowConfigurationToSetup"
            @update-configuration="updateArrowConfiguration"
            @delete-configuration="deleteArrowConfiguration"
            @add-arrow-to-setup="addArrowToSetup"
          />
        </div>

        <!-- Bow Settings Section -->
        <div v-if="selectedBowSetup" class="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              <i class="fas fa-cog mr-2 text-indigo-600"></i>
              Bow Settings
            </h3>
            <CustomButton
              @click="openBraceHeightModal(selectedBowSetup.id)"
              variant="outlined"
              size="small"
              class="text-indigo-600 border-indigo-600 hover:bg-indigo-50 dark:text-indigo-400 dark:border-indigo-400 dark:hover:bg-indigo-900/20"
            >
              <i class="fas fa-plus mr-2"></i>
              Add Brace Height
            </CustomButton>
          </div>

          <!-- Current Brace Height -->
          <div v-if="getCurrentBraceHeight(selectedBowSetup.id)" class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
            <div class="flex justify-between items-center">
              <div>
                <h4 class="font-medium text-gray-900 dark:text-gray-100">Current Brace Height</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {{ getCurrentBraceHeight(selectedBowSetup.id)?.setting_value }}" 
                  <span class="ml-2 text-xs">
                    (Updated {{ formatDate(getCurrentBraceHeight(selectedBowSetup.id)?.created_at) }})
                  </span>
                </p>
                <p v-if="getCurrentBraceHeight(selectedBowSetup.id)?.notes" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {{ getCurrentBraceHeight(selectedBowSetup.id)?.notes }}
                </p>
              </div>
              <CustomButton
                @click="openBraceHeightModal(selectedBowSetup.id)"
                variant="outlined"
                size="small"
                class="text-gray-600 dark:text-gray-400"
              >
                <i class="fas fa-edit"></i>
              </CustomButton>
            </div>
          </div>

          <!-- Brace Height History -->
          <div v-if="getBraceHeightHistory(selectedBowSetup.id).length > 1" class="mt-4">
            <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">
              <i class="fas fa-history mr-2 text-gray-500"></i>
              Brace Height History
            </h4>
            <div class="space-y-2">
              <div 
                v-for="setting in getBraceHeightHistory(selectedBowSetup.id).slice(1)" 
                :key="setting.id"
                class="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <div>
                  <span class="font-medium">{{ setting.setting_value }}"</span>
                  <span class="ml-3 text-sm text-gray-600 dark:text-gray-400">
                    {{ formatDate(setting.created_at) }}
                  </span>
                  <p v-if="setting.notes" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {{ setting.notes }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="!getCurrentBraceHeight(selectedBowSetup.id)" class="text-center py-6 text-gray-500 dark:text-gray-400">
            <i class="fas fa-ruler-vertical text-2xl mb-2 opacity-50"></i>
            <p>No brace height set</p>
            <p class="text-sm">Click "Add Brace Height" to record your bow's brace height</p>
          </div>
        </div>

        <!-- Equipment Management Section -->
        <div v-if="selectedBowSetup" class="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              <i class="fas fa-wrench mr-2 text-indigo-600"></i>
              Equipment
            </h3>
            <CustomButton
              @click="openEquipmentModal(selectedBowSetup.id)"
              variant="outlined"
              size="small"
              class="text-indigo-600 border-indigo-600 hover:bg-indigo-50 dark:text-indigo-400 dark:border-indigo-400 dark:hover:bg-indigo-900/20"
            >
              <i class="fas fa-plus mr-2"></i>
              Add Equipment
            </CustomButton>
          </div>

          <!-- Equipment List -->
          <div v-if="getEquipmentForSetup(selectedBowSetup.id).length > 0" class="space-y-3">
            <div 
              v-for="equipment in getEquipmentForSetup(selectedBowSetup.id)" 
              :key="equipment.id"
              class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
            >
              <div class="flex items-center space-x-3">
                <i :class="getEquipmentIcon(equipment.category)" class="w-5 h-5 text-gray-600 dark:text-gray-400"></i>
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-medium text-gray-900 dark:text-gray-100">
                      {{ formatEquipmentCategory(equipment.category) }}
                    </span>
                    <span v-if="equipment.manufacturer || equipment.model" class="text-sm text-gray-600 dark:text-gray-400">
                      -
                    </span>
                    <span v-if="equipment.manufacturer" class="text-sm text-gray-600 dark:text-gray-400">
                      {{ equipment.manufacturer }}
                    </span>
                    <span v-if="equipment.model" class="text-sm text-gray-600 dark:text-gray-400">
                      {{ equipment.model }}
                    </span>
                  </div>
                  <p v-if="equipment.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {{ equipment.description }}
                  </p>
                  <div v-if="equipment.weight || equipment.notes" class="flex items-center space-x-4 mt-1 text-xs text-gray-500 dark:text-gray-400">
                    <span v-if="equipment.weight">Weight: {{ equipment.weight }}g</span>
                    <span v-if="equipment.notes">{{ equipment.notes }}</span>
                  </div>
                </div>
              </div>
              <div class="flex space-x-2">
                <CustomButton
                  @click="editEquipment(equipment)"
                  variant="outlined"
                  size="small"
                  class="text-gray-600 dark:text-gray-400"
                >
                  <i class="fas fa-edit"></i>
                </CustomButton>
                <CustomButton
                  @click="deleteEquipment(equipment)"
                  variant="outlined"
                  size="small"
                  class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900/20"
                >
                  <i class="fas fa-trash"></i>
                </CustomButton>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
            <i class="fas fa-wrench text-3xl mb-3 opacity-50"></i>
            <p class="text-lg mb-2">No equipment added</p>
            <p class="text-sm">Add sights, stabilizers, rests, and other equipment to track your full setup</p>
          </div>
        </div>

        <!-- Brace Height Modal -->
        <div v-if="showBraceHeightModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-lg">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Set Brace Height
            </h3>
            <form @submit.prevent="saveBraceHeight">
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Brace Height: <span class="font-semibold text-primary">{{ braceHeightForm.value || 7.0 }}"</span>
                </label>
                <md-slider
                  min="6.0"
                  max="9.0"
                  step="0.125"
                  :value="braceHeightForm.value || 7.0"
                  @input="braceHeightForm.value = parseFloat($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                  <span>6.0"</span>
                  <span>9.0"</span>
                </div>
              </div>
              <div class="mb-4">
                <label for="braceHeightNotes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Notes (optional)
                </label>
                <textarea 
                  id="braceHeightNotes"
                  v-model="braceHeightForm.notes" 
                  class="form-textarea w-full h-20 resize-y"
                  placeholder="e.g., Feels good, quiet shot, arrow flight improved..."
                ></textarea>
              </div>
              <div class="flex justify-end space-x-3">
                <CustomButton
                  type="button"
                  @click="closeBraceHeightModal"
                  variant="outlined"
                  class="text-gray-700 dark:text-gray-200"
                >
                  Cancel
                </CustomButton>
                <CustomButton
                  type="submit"
                  variant="filled"
                  class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
                >
                  Save Setting
                </CustomButton>
              </div>
            </form>
          </div>
        </div>

        <!-- Equipment Modal -->
        <div v-if="showEquipmentModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-lg shadow-lg">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              {{ editingEquipment ? 'Edit Equipment' : 'Add Equipment' }}
            </h3>
            <form @submit.prevent="saveEquipment">
              <div class="mb-4">
                <label for="equipmentCategory" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Equipment Type *</label>
                <select id="equipmentCategory" v-model="equipmentForm.category" class="form-select w-full" required>
                  <option value="">Select Equipment Type</option>
                  <option value="sight">Sight</option>
                  <option value="stabilizer">Stabilizer</option>
                  <option value="rest">Arrow Rest</option>
                  <option value="release">Release Aid</option>
                  <option value="quiver">Quiver</option>
                  <option value="dampener">Dampener</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label for="equipmentManufacturer" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Manufacturer</label>
                  <input 
                    type="text" 
                    id="equipmentManufacturer" 
                    v-model="equipmentForm.manufacturer" 
                    class="form-input w-full"
                    placeholder="e.g., Spot Hogg, Bee Stinger"
                  />
                </div>
                <div>
                  <label for="equipmentModel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Model</label>
                  <input 
                    type="text" 
                    id="equipmentModel" 
                    v-model="equipmentForm.model" 
                    class="form-input w-full"
                    placeholder="e.g., Fast Eddie XL, Sport Hunter"
                  />
                </div>
              </div>
              <div class="mb-4">
                <label for="equipmentDescription" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
                <input 
                  type="text" 
                  id="equipmentDescription" 
                  v-model="equipmentForm.description" 
                  class="form-input w-full"
                  placeholder="Brief description or specifications"
                />
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label for="equipmentWeight" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Weight (grams)</label>
                  <input 
                    type="number" 
                    id="equipmentWeight" 
                    v-model="equipmentForm.weight" 
                    class="form-input w-full"
                    placeholder="e.g., 245"
                    min="0"
                    step="1"
                  />
                </div>
                <div>
                  <label for="equipmentInstalled" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Installed Date</label>
                  <input 
                    type="date" 
                    id="equipmentInstalled" 
                    v-model="equipmentForm.installed_at" 
                    class="form-input w-full"
                  />
                </div>
              </div>
              <div class="mb-6">
                <label for="equipmentNotes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Notes</label>
                <textarea 
                  id="equipmentNotes"
                  v-model="equipmentForm.notes" 
                  class="form-textarea w-full h-20 resize-y"
                  placeholder="Installation notes, settings, or other details..."
                ></textarea>
              </div>
              <div class="flex justify-end space-x-3">
                <CustomButton
                  type="button"
                  @click="closeEquipmentModal"
                  variant="outlined"
                  class="text-gray-700 dark:text-gray-200"
                >
                  Cancel
                </CustomButton>
                <CustomButton
                  type="submit"
                  variant="filled"
                  class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
                >
                  {{ editingEquipment ? 'Update Equipment' : 'Add Equipment' }}
                </CustomButton>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Bow Setup Modal -->
    <div v-if="showCreateSetupModal || editingSetup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-lg">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
          {{ editingSetup ? 'Edit Bow Setup' : 'Create Bow Setup' }}
        </h3>
        <form @submit.prevent="saveBowSetup">
          <!-- Basic Info -->
          <div class="mb-6">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Basic Information</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="md:col-span-2">
                <label for="setupName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Setup Name *</label>
                <input 
                  type="text" 
                  id="setupName" 
                  v-model="bowSetupForm.name" 
                  class="form-input w-full" 
                  required 
                  placeholder="e.g., My Hunting Bow"
                />
              </div>
              <div>
                <label for="bowType" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bow Type *</label>
                <select id="bowType" v-model="bowSetupForm.bow_type" class="form-select w-full" required @change="onBowTypeChange">
                  <option value="">Select Bow Type</option>
                  <option value="compound">Compound</option>
                  <option value="recurve">Recurve</option>
                  <option value="longbow">Longbow</option>
                  <option value="traditional">Traditional</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Bow Type Specific Fields -->
          <div v-if="bowSetupForm.bow_type" class="mb-6">
            <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              {{ bowSetupForm.bow_type.charAt(0).toUpperCase() + bowSetupForm.bow_type.slice(1) }} Bow Details
            </h4>
            
            <!-- Compound Bow Fields -->
            <div v-if="bowSetupForm.bow_type === 'compound'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Brand</label>
                <input type="text" v-model="bowSetupForm.brand" class="form-input w-full" placeholder="e.g., Mathews, Hoyt, PSE" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Poundage: <span class="font-semibold text-primary">{{ bowSetupForm.poundage || 60 }} lbs</span>
                </label>
                <md-slider
                  min="30"
                  max="90"
                  :value="bowSetupForm.poundage || 60"
                  @input="bowSetupForm.poundage = parseInt($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Draw Weight: <span class="font-semibold text-primary">{{ bowSetupForm.draw_weight || 45 }} lbs</span>
                </label>
                <md-slider
                  min="20"
                  max="80"
                  :value="bowSetupForm.draw_weight || 45"
                  @input="bowSetupForm.draw_weight = parseInt($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Draw Length: <span class="font-semibold text-primary">{{ bowSetupForm.draw_length || 28 }}"</span>
                </label>
                <md-slider
                  min="24"
                  max="34"
                  step="0.25"
                  :value="bowSetupForm.draw_length || 28"
                  @input="bowSetupForm.draw_length = parseFloat($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">IBO Speed (fps)</label>
                <input type="number" v-model="bowSetupForm.ibo_speed" class="form-input w-full" placeholder="e.g., 340" min="250" max="400" />
              </div>
            </div>

            <!-- Recurve Bow Fields -->
            <div v-else-if="bowSetupForm.bow_type === 'recurve'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Limb Brand</label>
                <input type="text" v-model="bowSetupForm.limb_brand" class="form-input w-full" placeholder="e.g., Win&Win, SF Archery" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Riser Brand</label>
                <input type="text" v-model="bowSetupForm.riser_brand" class="form-input w-full" placeholder="e.g., Hoyt, Win&Win" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Poundage: <span class="font-semibold text-primary">{{ bowSetupForm.poundage || 35 }} lbs</span>
                </label>
                <md-slider
                  min="20"
                  max="60"
                  :value="bowSetupForm.poundage || 35"
                  @input="bowSetupForm.poundage = parseInt($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Limb Fitting *</label>
                <select v-model="bowSetupForm.limb_fitting" class="form-select w-full" required>
                  <option value="">Select Fitting</option>
                  <option value="ILF">ILF (International Limb Fitting)</option>
                  <option value="Formula">Formula</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Draw Length: <span class="font-semibold text-primary">{{ bowSetupForm.draw_length || 28 }}"</span>
                </label>
                <md-slider
                  min="24"
                  max="34"
                  step="0.25"
                  :value="bowSetupForm.draw_length || 28"
                  @input="bowSetupForm.draw_length = parseFloat($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
              </div>
            </div>

            <!-- Longbow Fields -->
            <div v-else-if="bowSetupForm.bow_type === 'longbow'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bow Brand</label>
                <input type="text" v-model="bowSetupForm.bow_brand" class="form-input w-full" placeholder="e.g., Bear Archery, Martin" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Poundage: <span class="font-semibold text-primary">{{ bowSetupForm.poundage || 45 }} lbs</span>
                </label>
                <md-slider
                  min="25"
                  max="70"
                  :value="bowSetupForm.poundage || 45"
                  @input="bowSetupForm.poundage = parseInt($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Draw Length: <span class="font-semibold text-primary">{{ bowSetupForm.draw_length || 28 }}"</span>
                </label>
                <md-slider
                  min="24"
                  max="32"
                  step="0.25"
                  :value="bowSetupForm.draw_length || 28"
                  @input="bowSetupForm.draw_length = parseFloat($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
              </div>
            </div>

            <!-- Traditional Bow Fields -->
            <div v-else-if="bowSetupForm.bow_type === 'traditional'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Construction *</label>
                <select v-model="bowSetupForm.construction" class="form-select w-full" required @change="onConstructionChange">
                  <option value="">Select Construction</option>
                  <option value="one_piece">One Piece</option>
                  <option value="two_piece">Two Piece (Takedown)</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Poundage: <span class="font-semibold text-primary">{{ bowSetupForm.poundage || 40 }} lbs</span>
                </label>
                <md-slider
                  min="20"
                  max="65"
                  :value="bowSetupForm.poundage || 40"
                  @input="bowSetupForm.poundage = parseInt($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
              </div>

              <!-- Two-piece specific fields -->
              <template v-if="bowSetupForm.construction === 'two_piece'">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Limb Fitting</label>
                  <select v-model="bowSetupForm.limb_fitting" class="form-select w-full">
                    <option value="">Select Fitting</option>
                    <option value="ILF">ILF</option>
                    <option value="Bolt_Down">Bolt Down</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Limb Brand</label>
                  <input type="text" v-model="bowSetupForm.limb_brand" class="form-input w-full" placeholder="e.g., Bear, Martin" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Riser Brand</label>
                  <input type="text" v-model="bowSetupForm.riser_brand" class="form-input w-full" placeholder="e.g., Bear, Martin" />
                </div>
              </template>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Draw Length: <span class="font-semibold text-primary">{{ bowSetupForm.draw_length || 28 }}"</span>
                </label>
                <md-slider
                  min="24"
                  max="32"
                  step="0.25"
                  :value="bowSetupForm.draw_length || 28"
                  @input="bowSetupForm.draw_length = parseFloat($event.target.value)"
                  labeled
                  ticks
                  class="w-full"
                ></md-slider>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div class="mb-6">
            <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description (optional)</label>
            <textarea 
              id="description" 
              v-model="bowSetupForm.description" 
              class="form-textarea w-full h-20 resize-y"
              placeholder="Additional notes about this bow setup..."
            ></textarea>
          </div>

          <div class="flex justify-end space-x-3 mt-6">
            <CustomButton
              type="button"
              @click="closeBowSetupModal"
              variant="outlined"
              class="text-gray-700 dark:text-gray-200"
            >
              Cancel
            </CustomButton>
            <CustomButton
              type="submit"
              variant="filled"
              :disabled="isSavingSetup"
              class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
            >
              <span v-if="isSavingSetup">Saving...</span>
              <span v-else>{{ editingSetup ? 'Update Setup' : 'Create Setup' }}</span>
            </CustomButton>
          </div>
          <p v-if="setupError" class="text-red-500 text-sm mt-3">{{ setupError }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useBowConfigStore } from '~/stores/bowConfig'
import type { ArrowConfiguration, ArrowRecommendation, BowSetup } from '~/types/arrow'

// API
const api = useApi()

const bowConfigStore = useBowConfigStore()

// Reactive references from store
const bowConfig = computed(() => bowConfigStore.bowConfig)
const recommendedSpine = computed(() => bowConfigStore.recommendedSpine)
const arrowSetupDescription = computed(() => bowConfigStore.arrowSetupDescription)
const isCompoundBow = computed(() => bowConfigStore.isCompoundBow)

// Store actions
const { updateBowConfig } = bowConfigStore


// Tab management
const activeTab = ref('tuning')

// Bow setups management
const bowSetups = ref<BowSetup[]>([])
const selectedBowSetup = ref<BowSetup | null>(null)
const showCreateSetupModal = ref(false)
const editingSetup = ref<BowSetup | null>(null)
const isSavingSetup = ref(false)
const setupError = ref('')

const bowSetupForm = ref({
  name: '',
  bow_type: '',
  draw_weight: 45,
  draw_length: 28,
  description: '',
  // Compound specific
  brand: '',
  poundage: 60,
  ibo_speed: null,
  // Recurve specific
  limb_brand: '',
  riser_brand: '',
  limb_fitting: '',
  // Longbow specific
  bow_brand: '',
  // Traditional specific
  construction: '',
})

// Brace height settings modal state
const showBraceHeightModal = ref(false)
const braceHeightForm = ref({
  setup_id: null,
  value: 7.0,
  unit: 'inches',
  notes: ''
})
const bowSettings = ref([]) // Store all bow settings

// Equipment management state
const showEquipmentModal = ref(false)
const editingEquipment = ref(null)
const equipmentForm = ref({
  setup_id: null,
  category: '',
  manufacturer: '',
  model: '',
  description: '',
  weight: null,
  notes: '',
  installed_at: ''
})
const bowEquipment = ref([]) // Store all bow equipment

// Arrow configurations state (now linked to bow setups)
const arrowConfigurations = ref<(ArrowConfiguration & { bow_setup_id?: number })[]>([])
const savedArrowSetups = ref([]) // Arrows saved from database recommendations


// Bow setup management functions
const selectBowSetup = (setup: BowSetup) => {
  selectedBowSetup.value = setup
}

const formatBowType = (bowType: string) => {
  if (!bowType || bowType.length === 0) return 'Unknown'
  return bowType.charAt(0).toUpperCase() + bowType.slice(1)
}

const createBowSetup = () => {
  showCreateSetupModal.value = true
  editingSetup.value = null
  resetBowSetupForm()
}

const resetBowSetupForm = () => {
  bowSetupForm.value = {
    name: '',
    bow_type: '',
    draw_weight: 45,
    draw_length: 28,
    description: '',
    // Compound specific
    brand: '',
    poundage: 60,
    ibo_speed: null,
    // Recurve specific
    limb_brand: '',
    riser_brand: '',
    limb_fitting: '',
    // Longbow specific
    bow_brand: '',
    // Traditional specific
    construction: '',
  }
}

const onBowTypeChange = () => {
  // Set appropriate defaults based on bow type
  if (bowSetupForm.value.bow_type === 'compound') {
    bowSetupForm.value.poundage = 60
    bowSetupForm.value.draw_weight = 45
  } else if (bowSetupForm.value.bow_type === 'recurve') {
    bowSetupForm.value.poundage = 35
    bowSetupForm.value.draw_weight = 35
  } else if (bowSetupForm.value.bow_type === 'longbow') {
    bowSetupForm.value.poundage = 45
    bowSetupForm.value.draw_weight = 45
  } else if (bowSetupForm.value.bow_type === 'traditional') {
    bowSetupForm.value.poundage = 40
    bowSetupForm.value.draw_weight = 40
  }
}

const onConstructionChange = () => {
  // Clear two-piece specific fields if switching to one-piece
  if (bowSetupForm.value.construction === 'one_piece') {
    bowSetupForm.value.limb_fitting = ''
    bowSetupForm.value.limb_brand = ''
    bowSetupForm.value.riser_brand = ''
  }
}

const editBowSetup = (setup: BowSetup) => {
  editingSetup.value = setup
  const config = setup.bow_config as any // Type assertion for accessing extended properties
  
  bowSetupForm.value = {
    name: setup.name,
    bow_type: config.bow_type,
    draw_weight: config.draw_weight,
    draw_length: config.draw_length,
    description: setup.description || '',
    // Compound specific
    brand: config.brand || '',
    poundage: config.poundage || 60,
    ibo_speed: config.ibo_speed || null,
    // Recurve specific
    limb_brand: config.limb_brand || '',
    riser_brand: config.riser_brand || '',
    limb_fitting: config.limb_fitting || '',
    // Longbow specific
    bow_brand: config.bow_brand || '',
    // Traditional specific
    construction: config.construction || '',
  }
  showCreateSetupModal.value = true
}

const closeBowSetupModal = () => {
  showCreateSetupModal.value = false
  editingSetup.value = null
  setupError.value = ''
}

const saveBowSetup = () => {
  isSavingSetup.value = true
  setupError.value = ''
  
  try {
    // Create bow configuration based on bow type
    let bowConfig: any = {
      bow_type: bowSetupForm.value.bow_type,
      draw_weight: Number(bowSetupForm.value.draw_weight),
      draw_length: Number(bowSetupForm.value.draw_length),
      arrow_material: 'carbon', // Default
      arrow_rest_type: 'drop-away',
      nock_type: 'pin',
      vane_type: 'plastic',
      vane_length: 4,
      number_of_vanes: 3,
      arrow_length: 29, // Default
      point_weight: 125 // Default
    }

    // Add bow type specific fields
    if (bowSetupForm.value.bow_type === 'compound') {
      bowConfig = {
        ...bowConfig,
        name: bowSetupForm.value.name,
        brand: bowSetupForm.value.brand,
        poundage: Number(bowSetupForm.value.poundage),
        ibo_speed: bowSetupForm.value.ibo_speed ? Number(bowSetupForm.value.ibo_speed) : undefined
      }
    } else if (bowSetupForm.value.bow_type === 'recurve') {
      bowConfig = {
        ...bowConfig,
        name: bowSetupForm.value.name,
        limb_brand: bowSetupForm.value.limb_brand,
        riser_brand: bowSetupForm.value.riser_brand,
        poundage: Number(bowSetupForm.value.poundage),
        limb_fitting: bowSetupForm.value.limb_fitting
      }
    } else if (bowSetupForm.value.bow_type === 'longbow') {
      bowConfig = {
        ...bowConfig,
        name: bowSetupForm.value.name,
        bow_brand: bowSetupForm.value.bow_brand,
        poundage: Number(bowSetupForm.value.poundage)
      }
    } else if (bowSetupForm.value.bow_type === 'traditional') {
      bowConfig = {
        ...bowConfig,
        name: bowSetupForm.value.name,
        construction: bowSetupForm.value.construction,
        poundage: Number(bowSetupForm.value.poundage)
      }
      
      // Add two-piece specific fields if applicable
      if (bowSetupForm.value.construction === 'two_piece') {
        bowConfig.limb_fitting = bowSetupForm.value.limb_fitting
        bowConfig.limb_brand = bowSetupForm.value.limb_brand
        bowConfig.riser_brand = bowSetupForm.value.riser_brand
      }
    }

    const setupData: BowSetup = {
      id: editingSetup.value?.id || Date.now(),
      name: bowSetupForm.value.name,
      bow_config: bowConfig,
      arrow_configurations: [],
      description: bowSetupForm.value.description,
      created_at: editingSetup.value?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    if (editingSetup.value) {
      // Update existing setup
      const index = bowSetups.value.findIndex(s => s.id === editingSetup.value!.id)
      if (index !== -1) {
        bowSetups.value[index] = setupData
      }
    } else {
      // Add new setup
      bowSetups.value.push(setupData)
    }
    
    // Save to localStorage
    localStorage.setItem('bowSetups', JSON.stringify(bowSetups.value))
    
    closeBowSetupModal()
  } catch (error) {
    setupError.value = 'Failed to save bow setup. Please try again.'
    console.error('Error saving bow setup:', error)
  } finally {
    isSavingSetup.value = false
  }
}

const deleteBowSetup = (setup: BowSetup) => {
  if (confirm(`Are you sure you want to delete "${setup.name}"? This will also delete all associated arrow configurations, settings, and equipment.`)) {
    // Remove the bow setup
    const setupIndex = bowSetups.value.findIndex(s => s.id === setup.id)
    if (setupIndex !== -1) {
      bowSetups.value.splice(setupIndex, 1)
    }
    
    // Remove associated arrow configurations
    arrowConfigurations.value = arrowConfigurations.value.filter(config => config.bow_setup_id !== setup.id)
    
    // Remove associated settings
    bowSettings.value = bowSettings.value.filter(setting => setting.bow_setup_id !== setup.id)
    
    // Remove associated equipment
    bowEquipment.value = bowEquipment.value.filter(equipment => equipment.bow_setup_id !== setup.id)
    
    // Clear selection if this setup was selected
    if (selectedBowSetup.value?.id === setup.id) {
      selectedBowSetup.value = null
    }
    
    // Save to localStorage
    localStorage.setItem('bowSetups', JSON.stringify(bowSetups.value))
    localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
    localStorage.setItem('bowSettings', JSON.stringify(bowSettings.value))
    localStorage.setItem('bowEquipment', JSON.stringify(bowEquipment.value))
  }
}

const getArrowConfigsForSetup = (setupId: number) => {
  return arrowConfigurations.value.filter(config => config.bow_setup_id === setupId)
}

// Brace height settings functions
const getCurrentBraceHeight = (setupId: number) => {
  const settings = bowSettings.value.filter(setting => 
    setting.bow_setup_id === setupId && setting.setting_name === 'brace_height'
  )
  // Return the most recent setting (created_at is ISO string, so lexicographic sort works)
  return settings.sort((a, b) => b.created_at.localeCompare(a.created_at))[0] || null
}

const getBraceHeightHistory = (setupId: number) => {
  return bowSettings.value
    .filter(setting => 
      setting.bow_setup_id === setupId && setting.setting_name === 'brace_height'
    )
    .sort((a, b) => b.created_at.localeCompare(a.created_at)) // Most recent first
}

const openBraceHeightModal = (setupId: number) => {
  braceHeightForm.value.setup_id = setupId
  const current = getCurrentBraceHeight(setupId)
  if (current) {
    braceHeightForm.value.value = parseFloat(current.setting_value)
    braceHeightForm.value.notes = ''
  } else {
    braceHeightForm.value.value = 7.0
    braceHeightForm.value.notes = ''
  }
  showBraceHeightModal.value = true
}

const closeBraceHeightModal = () => {
  showBraceHeightModal.value = false
  braceHeightForm.value = {
    setup_id: null,
    value: 7.0,
    unit: 'inches',
    notes: ''
  }
}

const saveBraceHeight = () => {
  if (!braceHeightForm.value.setup_id) return
  
  const newSetting = {
    id: Date.now(),
    bow_setup_id: braceHeightForm.value.setup_id,
    setting_name: 'brace_height',
    setting_value: braceHeightForm.value.value.toString(),
    unit: braceHeightForm.value.unit,
    notes: braceHeightForm.value.notes,
    created_at: new Date().toISOString()
  }
  
  bowSettings.value.push(newSetting)
  
  // Save to localStorage
  localStorage.setItem('bowSettings', JSON.stringify(bowSettings.value))
  
  closeBraceHeightModal()
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'Unknown'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    })
  } catch (error) {
    return 'Invalid date'
  }
}

// Equipment management functions
const getEquipmentForSetup = (setupId: number) => {
  return bowEquipment.value.filter(equipment => equipment.bow_setup_id === setupId)
}

const getEquipmentIcon = (category: string) => {
  const icons = {
    sight: 'fas fa-crosshairs',
    stabilizer: 'fas fa-ruler',
    rest: 'fas fa-hand-paper',
    release: 'fas fa-hand-rock',
    quiver: 'fas fa-quidditch',
    dampener: 'fas fa-compress-arrows-alt',
    other: 'fas fa-cog'
  }
  return icons[category] || 'fas fa-cog'
}

const formatEquipmentCategory = (category: string) => {
  const names = {
    sight: 'Sight',
    stabilizer: 'Stabilizer',
    rest: 'Arrow Rest',
    release: 'Release Aid',
    quiver: 'Quiver',
    dampener: 'Dampener',
    other: 'Other'
  }
  return names[category] || category
}

const openEquipmentModal = (setupId: number) => {
  equipmentForm.value.setup_id = setupId
  editingEquipment.value = null
  resetEquipmentForm()
  showEquipmentModal.value = true
}

const resetEquipmentForm = () => {
  equipmentForm.value = {
    setup_id: equipmentForm.value.setup_id, // Keep the setup_id
    category: '',
    manufacturer: '',
    model: '',
    description: '',
    weight: null,
    notes: '',
    installed_at: ''
  }
}

const editEquipment = (equipment) => {
  editingEquipment.value = equipment
  equipmentForm.value = {
    setup_id: equipment.bow_setup_id,
    category: equipment.category,
    manufacturer: equipment.manufacturer || '',
    model: equipment.model || '',
    description: equipment.description || '',
    weight: equipment.weight,
    notes: equipment.notes || '',
    installed_at: equipment.installed_at || ''
  }
  showEquipmentModal.value = true
}

const closeEquipmentModal = () => {
  showEquipmentModal.value = false
  editingEquipment.value = null
  resetEquipmentForm()
}

const saveEquipment = () => {
  if (!equipmentForm.value.setup_id || !equipmentForm.value.category) return
  
  if (editingEquipment.value) {
    // Update existing equipment
    const index = bowEquipment.value.findIndex(eq => eq.id === editingEquipment.value.id)
    if (index !== -1) {
      bowEquipment.value[index] = {
        ...editingEquipment.value,
        category: equipmentForm.value.category,
        manufacturer: equipmentForm.value.manufacturer,
        model: equipmentForm.value.model,
        description: equipmentForm.value.description,
        weight: equipmentForm.value.weight ? Number(equipmentForm.value.weight) : null,
        notes: equipmentForm.value.notes,
        installed_at: equipmentForm.value.installed_at
      }
    }
  } else {
    // Add new equipment
    const newEquipment = {
      id: Date.now(),
      bow_setup_id: equipmentForm.value.setup_id,
      category: equipmentForm.value.category,
      manufacturer: equipmentForm.value.manufacturer,
      model: equipmentForm.value.model,
      description: equipmentForm.value.description,
      weight: equipmentForm.value.weight ? Number(equipmentForm.value.weight) : null,
      notes: equipmentForm.value.notes,
      installed_at: equipmentForm.value.installed_at
    }
    bowEquipment.value.push(newEquipment)
  }
  
  // Save to localStorage
  localStorage.setItem('bowEquipment', JSON.stringify(bowEquipment.value))
  
  closeEquipmentModal()
}

const deleteEquipment = (equipment) => {
  if (confirm(`Are you sure you want to remove this ${formatEquipmentCategory(equipment.category).toLowerCase()}?`)) {
    const index = bowEquipment.value.findIndex(eq => eq.id === equipment.id)
    if (index !== -1) {
      bowEquipment.value.splice(index, 1)
      localStorage.setItem('bowEquipment', JSON.stringify(bowEquipment.value))
    }
  }
}

// Arrow configuration management functions (updated to link to bow setups)
const addArrowConfigurationToSetup = (configData: ArrowConfiguration) => {
  if (!selectedBowSetup.value) return
  
  const newConfig = {
    ...configData,
    id: Date.now(),
    bow_setup_id: selectedBowSetup.value.id,
    created_at: new Date().toISOString()
  }
  arrowConfigurations.value.push(newConfig)
  localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
}

const addArrowConfiguration = (configData: ArrowConfiguration) => {
  const newConfig = {
    ...configData,
    id: Date.now(), // Simple ID generation for now
    created_at: new Date().toISOString()
  }
  arrowConfigurations.value.push(newConfig)
  // Store in localStorage for persistence
  localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
}

const updateArrowConfiguration = (configData: ArrowConfiguration) => {
  const index = arrowConfigurations.value.findIndex(config => config.id === configData.id)
  if (index !== -1) {
    arrowConfigurations.value[index] = configData
    // Store in localStorage for persistence
    localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
  }
}

const deleteArrowConfiguration = (configData: ArrowConfiguration) => {
  const index = arrowConfigurations.value.findIndex(config => config.id === configData.id)
  if (index !== -1) {
    arrowConfigurations.value.splice(index, 1)
    // Store in localStorage for persistence
    localStorage.setItem('arrowConfigurations', JSON.stringify(arrowConfigurations.value))
  }
}

const addArrowToSetup = (data: { arrowConfig: ArrowConfiguration, arrowRecommendation: ArrowRecommendation }) => {
  const { arrowConfig, arrowRecommendation } = data
  
  // Create a saved arrow setup combining the configuration and database arrow
  const savedSetup = {
    id: Date.now(),
    arrow_config: arrowConfig,
    database_arrow: arrowRecommendation.arrow,
    spine_spec: arrowRecommendation.spine_specification,
    compatibility_score: arrowRecommendation.compatibility_score,
    match_percentage: arrowRecommendation.match_percentage,
    saved_at: new Date().toISOString()
  }
  
  savedArrowSetups.value.push(savedSetup)
  // Store in localStorage for persistence
  localStorage.setItem('savedArrowSetups', JSON.stringify(savedArrowSetups.value))
  
  // Show success message
  console.log(`Added ${arrowRecommendation.arrow.manufacturer} ${arrowRecommendation.arrow.model_name} to "${arrowConfig.name}" setup`)
}

const removeArrowSetup = (setup) => {
  const index = savedArrowSetups.value.findIndex(s => s.id === setup.id)
  if (index !== -1) {
    savedArrowSetups.value.splice(index, 1)
    // Store in localStorage for persistence
    localStorage.setItem('savedArrowSetups', JSON.stringify(savedArrowSetups.value))
  }
}

// Load saved configurations from localStorage
const loadSavedConfigurations = () => {
  if (process.client) {
    // Load bow setups
    const savedBowSetups = localStorage.getItem('bowSetups')
    if (savedBowSetups) {
      try {
        bowSetups.value = JSON.parse(savedBowSetups)
      } catch (error) {
        console.error('Error loading saved bow setups:', error)
      }
    }
    
    // Load arrow configurations
    const saved = localStorage.getItem('arrowConfigurations')
    if (saved) {
      try {
        arrowConfigurations.value = JSON.parse(saved)
      } catch (error) {
        console.error('Error loading saved configurations:', error)
      }
    }
    
    // Load saved arrow setups from database
    const savedSetups = localStorage.getItem('savedArrowSetups')
    if (savedSetups) {
      try {
        savedArrowSetups.value = JSON.parse(savedSetups)
      } catch (error) {
        console.error('Error loading saved setups:', error)
      }
    }
    
    // Load bow settings
    const savedBowSettings = localStorage.getItem('bowSettings')
    if (savedBowSettings) {
      try {
        bowSettings.value = JSON.parse(savedBowSettings)
      } catch (error) {
        console.error('Error loading saved bow settings:', error)
      }
    }
    
    // Load bow equipment
    const savedBowEquipment = localStorage.getItem('bowEquipment')
    if (savedBowEquipment) {
      try {
        bowEquipment.value = JSON.parse(savedBowEquipment)
      } catch (error) {
        console.error('Error loading saved bow equipment:', error)
      }
    }
  }
}

// Load data on mount
onMounted(() => {
  loadSavedConfigurations()
})

// Set page title
useHead({
  title: 'Arrow Tuning Platform - Beta',
  meta: [
    { name: 'description', content: 'Professional arrow tuning platform for archery enthusiasts (Beta)' }
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