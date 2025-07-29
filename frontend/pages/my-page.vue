<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">My Setup</h1>
    
    <div v-if="isLoadingUser" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
      <p class="text-gray-700 dark:text-gray-300">Loading...</p>
    </div>

    <div v-else-if="user">
      <!-- Archer Profile Section -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Archer Profile</h2>
          <div class="flex space-x-3">
            <CustomButton
              @click="openEditModal"
              variant="filled"
              class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
            >
              Edit Profile
            </CustomButton>
            <CustomButton
              @click="logout"
              variant="outlined"
              class="text-red-600 border-red-600 hover:bg-red-50 dark:text-red-400 dark:border-red-400 dark:hover:bg-red-900"
            >
              Logout
            </CustomButton>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Basic Info -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Basic Information</h3>
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Name:</span>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ user.name || 'Not set' }}</p>
              </div>
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Email:</span>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ user.email }}</p>
              </div>
            </div>
          </div>

          <!-- Archer Specifications -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Physical Specifications</h3>
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Draw Length:</span>
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ user.draw_length || 28.0 }}"</p>
              </div>
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Skill Level:</span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getSkillLevelClass(user.skill_level)">
                  {{ formatSkillLevel(user.skill_level) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Shooting Preferences -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Shooting Preferences</h3>
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400">Primary Style:</span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getShootingStyleClass(user.shooting_style)">
                  {{ formatShootingStyle(user.shooting_style) }}
                </span>
              </div>
              <div v-if="user.preferred_manufacturers && user.preferred_manufacturers.length > 0">
                <span class="text-sm text-gray-600 dark:text-gray-400">Preferred Brands:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="brand in user.preferred_manufacturers" :key="brand"
                        class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {{ brand }}
                  </span>
                </div>
              </div>
              <div v-if="user.notes">
                <span class="text-sm text-gray-600 dark:text-gray-400">Notes:</span>
                <p class="text-sm text-gray-700 dark:text-gray-300 mt-1">{{ user.notes }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Profile Modal -->
      <div v-if="isEditing" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl shadow-lg max-h-screen overflow-y-auto">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Edit Archer Profile</h3>
          <form @submit.prevent="saveProfile">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Basic Information -->
                <div class="mb-4">
                  <label for="editedName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    id="editedName"
                    v-model="editedName"
                    class="form-input w-full"
                    required
                  />
                </div>

                <!-- Skill Level -->
                <div class="mb-4">
                  <label for="skillLevel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Skill Level
                  </label>
                  <select id="skillLevel" v-model="editedSkillLevel" class="form-select w-full" required>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <!-- Draw Length -->
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Draw Length: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ editedDrawLength }}"</span>
                  </label>
                  <md-slider
                    min="20"
                    max="36"
                    step="0.25"
                    :value="editedDrawLength"
                    @input="editedDrawLength = parseFloat($event.target.value)"
                    labeled
                    ticks
                    class="w-full"
                  ></md-slider>
                  <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                    <span>20"</span>
                    <span>36"</span>
                  </div>
                </div>

                <!-- Shooting Style -->
                <div class="mb-4">
                  <label for="shootingStyle" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Primary Shooting Style
                  </label>
                  <select id="shootingStyle" v-model="editedShootingStyle" class="form-select w-full" required>
                    <option value="target">Target</option>
                    <option value="hunting">Hunting</option>
                    <option value="traditional">Traditional</option>
                    <option value="3d">3D</option>
                  </select>
                </div>
              </div>

              <!-- Preferred Manufacturers -->
              <div class="mb-4">
                <label for="preferredManufacturers" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Preferred Arrow Manufacturers (comma-separated)
                </label>
                <input
                  type="text"
                  id="preferredManufacturers"
                  v-model="editedPreferredManufacturers"
                  class="form-input w-full"
                  placeholder="e.g., Easton, Gold Tip, Victory"
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Enter manufacturer names separated by commas
                </p>
              </div>

              <!-- Notes -->
              <div class="mb-6">
                <label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Notes
                </label>
                <textarea
                  id="notes"
                  v-model="editedNotes"
                  class="form-textarea w-full"
                  rows="3"
                  placeholder="Additional notes about your archery preferences, goals, etc."
                ></textarea>
              </div>

              <div class="flex justify-end space-x-3">
                <CustomButton
                  type="button"
                  @click="closeEditModal"
                  variant="outlined"
                  class="text-gray-700 dark:text-gray-200"
                >
                  Cancel
                </CustomButton>
                <CustomButton
                  type="submit"
                  variant="filled"
                  :disabled="isSaving"
                  class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
                >
                  <span v-if="isSaving">Saving...</span>
                  <span v-else>Save Changes</span>
                </CustomButton>
              </div>
              <p v-if="editError" class="text-red-500 text-sm mt-3">{{ editError }}</p>
            </form>
        </div>
      </div>

      <!-- Bow Setups Section -->
      <div class="mt-8">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">My Bow Setups</h3>

          <div v-if="isLoadingSetups" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-purple-400 mx-auto mb-3"></div>
            <p class="text-gray-700 dark:text-gray-300">Loading bow setups...</p>
          </div>

          <div v-else>
            <div v-if="bowSetups.length > 0" class="space-y-4 mb-6">
              <div v-for="setup in bowSetups" :key="setup.id" class="card p-4 border border-gray-200 dark:border-gray-700">
                <div class="flex justify-between items-start mb-2">
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ setup.name }} ({{ setup.bow_config?.bow_type || 'Unknown' }})</h4>
                    <p class="text-sm text-gray-700 dark:text-gray-300">Draw Weight: {{ setup.bow_config?.draw_weight || 'N/A' }} lbs</p>
                    <p v-if="setup.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ setup.description }}</p>
                  </div>
                  <div class="flex space-x-2 ml-4">
                    <CustomButton
                      @click="openArrowSearchModal(setup)"
                      variant="filled"
                      size="small"
                      class="bg-green-600 text-white hover:bg-green-700"
                    >
                      <i class="fas fa-search mr-1"></i>
                      Add Arrow
                    </CustomButton>
                    <CustomButton
                      @click="confirmDeleteSetup(setup.id)"
                      variant="text"
                      size="small"
                      class="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900 p-1"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </CustomButton>
                  </div>
                </div>
                
                <!-- Arrows List for this Bow Setup -->
                <BowSetupArrowsList
                  :arrows="setup.arrows || []"
                  :loading="setup.loadingArrows || false"
                  @remove-arrow="removeArrowFromSetup"
                  @view-details="viewArrowDetails"
                />
              </div>
            </div>
            <p v-else class="text-gray-600 dark:text-gray-400 mb-4">No bow setups added yet.</p>

            <CustomButton
              @click="openAddSetupModal"
              variant="outlined"
              class="text-blue-600 border-blue-600 hover:bg-blue-50 dark:text-purple-400 dark:border-purple-400 dark:hover:bg-purple-900"
            >
              Add New Bow Setup
            </CustomButton>
          </div>

        <!-- Add/Edit Bow Setup Modal -->
        <div v-if="isAddingSetup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl shadow-lg max-h-screen overflow-y-auto">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
              <i class="fas fa-plus-circle mr-2 text-blue-600"></i>
              Create New Bow Setup
            </h3>
            <form @submit.prevent="saveBowSetup">
              <!-- Setup Name -->
              <div class="mb-6">
                <md-outlined-text-field 
                  class="w-full"
                  :value="newSetup.name"
                  @input="newSetup.name = $event.target.value"
                  label="Setup Name"
                  placeholder="e.g. My Hunting Bow, Competition Setup..."
                  required
                >
                  <i class="fas fa-tag" slot="leading-icon" style="color: #6b7280;"></i>
                </md-outlined-text-field>
              </div>

              <!-- Bow Configuration -->
              <div class="space-y-6 mb-6">
                <!-- Bow Type -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <md-filled-select
                      label="Bow Type"
                      :value="newSetup.bow_type"
                      @change="newSetup.bow_type = $event.target.value"
                      class="w-full"
                      required
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

                  <!-- Draw Weight -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Draw Weight: <span class="font-semibold text-blue-600 dark:text-purple-400">{{ newSetup.draw_weight || 45 }} lbs</span>
                    </label>
                    <md-slider
                      min="20"
                      max="80"
                      step="5"
                      :value="newSetup.draw_weight || 45"
                      @input="newSetup.draw_weight = parseInt($event.target.value)"
                      labeled
                      ticks
                      class="w-full"
                    ></md-slider>
                    <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                      <span>20 lbs</span>
                      <span>80 lbs</span>
                    </div>
                  </div>
                </div>

                <!-- Bow Type Specific Configuration -->
                <div v-if="newSetup.bow_type" class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                  <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                    <i class="fas fa-cog mr-2 text-blue-600"></i>
                    {{ newSetup.bow_type.charAt(0).toUpperCase() + newSetup.bow_type.slice(1) }} Specific Configuration
                  </h4>

                  <!-- Compound Bow Configuration -->
                  <div v-if="newSetup.bow_type === 'compound'" class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <!-- Compound Brand Selection -->
                      <div>
                        <md-filled-select
                          label="Bow Brand"
                          :value="newSetup.brand || ''"
                          @change="handleBrandSelection('brand', $event.target.value)"
                          class="w-full"
                        >
                          <md-select-option value="">
                            <div slot="headline">Select Brand</div>
                          </md-select-option>
                          <md-select-option value="Hoyt">
                            <div slot="headline">Hoyt</div>
                          </md-select-option>
                          <md-select-option value="Mathews">
                            <div slot="headline">Mathews</div>
                          </md-select-option>
                          <md-select-option value="PSE">
                            <div slot="headline">PSE</div>
                          </md-select-option>
                          <md-select-option value="Bowtech">
                            <div slot="headline">Bowtech</div>
                          </md-select-option>
                          <md-select-option value="Prime">
                            <div slot="headline">Prime</div>
                          </md-select-option>
                          <md-select-option value="Elite">
                            <div slot="headline">Elite</div>
                          </md-select-option>
                          <md-select-option value="Bear">
                            <div slot="headline">Bear</div>
                          </md-select-option>
                          <md-select-option value="Diamond">
                            <div slot="headline">Diamond</div>
                          </md-select-option>
                          <md-select-option value="Mission">
                            <div slot="headline">Mission</div>
                          </md-select-option>
                          <md-select-option value="Other">
                            <div slot="headline">Other...</div>
                          </md-select-option>
                        </md-filled-select>
                        
                        <!-- Custom brand input when "Other" is selected -->
                        <md-outlined-text-field 
                          v-if="newSetup.brand === 'Other'"
                          class="w-full mt-2"
                          :value="newSetup.custom_brand || ''"
                          @input="newSetup.custom_brand = $event.target.value"
                          label="Custom Brand Name"
                          placeholder="Enter brand name..."
                          required
                        >
                          <i class="fas fa-edit" slot="leading-icon" style="color: #6b7280;"></i>
                        </md-outlined-text-field>
                        
                        <!-- Compound Model Name -->
                        <md-outlined-text-field 
                          v-if="newSetup.brand"
                          class="w-full mt-2"
                          :value="newSetup.compound_model || ''"
                          @input="newSetup.compound_model = $event.target.value"
                          label="Bow Model Name"
                          placeholder="e.g., RX-7 Ultra, Halon X, V3X..."
                        >
                          <i class="fas fa-tag" slot="leading-icon" style="color: #6b7280;"></i>
                        </md-outlined-text-field>
                      </div>
                      
                      <md-outlined-text-field 
                        class="w-full"
                        :value="newSetup.ibo_speed || ''"
                        @input="newSetup.ibo_speed = parseInt($event.target.value) || ''"
                        label="IBO Speed (fps)"
                        type="number"
                        placeholder="e.g., 320, 340..."
                      >
                        <i class="fas fa-tachometer-alt" slot="leading-icon" style="color: #6b7280;"></i>
                      </md-outlined-text-field>
                    </div>
                  </div>

                  <!-- Recurve Bow Configuration -->
                  <div v-else-if="newSetup.bow_type === 'recurve'" class="space-y-4">
                    <!-- Bow Usage Selection -->
                    <div class="mb-4">
                      <md-filled-select
                        label="Bow Usage Style"
                        :value="newSetup.bow_usage || ''"
                        @change="newSetup.bow_usage = $event.target.value"
                        class="w-full"
                      >
                        <md-select-option value="">
                          <div slot="headline">Select Usage Style</div>
                        </md-select-option>
                        <md-select-option value="Olympic">
                          <div slot="headline">Olympic (Target with sight)</div>
                        </md-select-option>
                        <md-select-option value="Barebow">
                          <div slot="headline">Barebow (No sight, instinctive)</div>
                        </md-select-option>
                        <md-select-option value="Traditional">
                          <div slot="headline">Traditional (Historical style)</div>
                        </md-select-option>
                        <md-select-option value="Field">
                          <div slot="headline">Field Archery</div>
                        </md-select-option>
                        <md-select-option value="3D">
                          <div slot="headline">3D Competition</div>
                        </md-select-option>
                        <md-select-option value="Other">
                          <div slot="headline">Other</div>
                        </md-select-option>
                      </md-filled-select>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <!-- Riser Brand Selection -->
                      <div>
                        <md-filled-select
                          label="Riser Brand"
                          :value="newSetup.riser_brand || ''"
                          @change="handleBrandSelection('riser_brand', $event.target.value)"
                          class="w-full"
                        >
                          <md-select-option value="">
                            <div slot="headline">Select Riser Brand</div>
                          </md-select-option>
                          <md-select-option value="Hoyt">
                            <div slot="headline">Hoyt</div>
                          </md-select-option>
                          <md-select-option value="Win&Win">
                            <div slot="headline">Win&Win</div>
                          </md-select-option>
                          <md-select-option value="Uukha">
                            <div slot="headline">Uukha</div>
                          </md-select-option>
                          <md-select-option value="Samick">
                            <div slot="headline">Samick</div>
                          </md-select-option>
                          <md-select-option value="Bernardini">
                            <div slot="headline">Bernardini</div>
                          </md-select-option>
                          <md-select-option value="Border">
                            <div slot="headline">Border</div>
                          </md-select-option>
                          <md-select-option value="Mybo">
                            <div slot="headline">Mybo</div>
                          </md-select-option>
                          <md-select-option value="Fivics">
                            <div slot="headline">Fivics</div>
                          </md-select-option>
                          <md-select-option value="Other">
                            <div slot="headline">Other...</div>
                          </md-select-option>
                        </md-filled-select>
                        
                        <!-- Custom riser brand input -->
                        <md-outlined-text-field 
                          v-if="newSetup.riser_brand === 'Other'"
                          class="w-full mt-2"
                          :value="newSetup.custom_riser_brand || ''"
                          @input="newSetup.custom_riser_brand = $event.target.value"
                          label="Custom Riser Brand"
                          placeholder="Enter riser brand name..."
                          required
                        >
                          <i class="fas fa-edit" slot="leading-icon" style="color: #6b7280;"></i>
                        </md-outlined-text-field>
                        
                        <!-- Riser Model Name -->
                        <md-outlined-text-field 
                          v-if="newSetup.riser_brand"
                          class="w-full mt-2"
                          :value="newSetup.riser_model || ''"
                          @input="newSetup.riser_model = $event.target.value"
                          label="Riser Model Name"
                          placeholder="e.g., Formula X, Prodigy, Epic..."
                        >
                          <i class="fas fa-tag" slot="leading-icon" style="color: #6b7280;"></i>
                        </md-outlined-text-field>
                      </div>
                      
                      <!-- Limb Brand Selection -->
                      <div>
                        <md-filled-select
                          label="Limb Brand"
                          :value="newSetup.limb_brand || ''"
                          @change="handleBrandSelection('limb_brand', $event.target.value)"
                          class="w-full"
                        >
                          <md-select-option value="">
                            <div slot="headline">Select Limb Brand</div>
                          </md-select-option>
                          <md-select-option value="Hoyt">
                            <div slot="headline">Hoyt</div>
                          </md-select-option>
                          <md-select-option value="Win&Win">
                            <div slot="headline">Win&Win</div>
                          </md-select-option>
                          <md-select-option value="Uukha">
                            <div slot="headline">Uukha</div>
                          </md-select-option>
                          <md-select-option value="Border">
                            <div slot="headline">Border</div>
                          </md-select-option>
                          <md-select-option value="Samick">
                            <div slot="headline">Samick</div>
                          </md-select-option>
                          <md-select-option value="SF Archery">
                            <div slot="headline">SF Archery</div>
                          </md-select-option>
                          <md-select-option value="Core">
                            <div slot="headline">Core</div>
                          </md-select-option>
                          <md-select-option value="Fivics">
                            <div slot="headline">Fivics</div>
                          </md-select-option>
                          <md-select-option value="Other">
                            <div slot="headline">Other...</div>
                          </md-select-option>
                        </md-filled-select>
                        
                        <!-- Custom limb brand input -->
                        <md-outlined-text-field 
                          v-if="newSetup.limb_brand === 'Other'"
                          class="w-full mt-2"
                          :value="newSetup.custom_limb_brand || ''"
                          @input="newSetup.custom_limb_brand = $event.target.value"
                          label="Custom Limb Brand"
                          placeholder="Enter limb brand name..."
                          required
                        >
                          <i class="fas fa-edit" slot="leading-icon" style="color: #6b7280;"></i>
                        </md-outlined-text-field>
                        
                        <!-- Limb Model Name -->
                        <md-outlined-text-field 
                          v-if="newSetup.limb_brand"
                          class="w-full mt-2"
                          :value="newSetup.limb_model || ''"
                          @input="newSetup.limb_model = $event.target.value"
                          label="Limb Model Name"
                          placeholder="e.g., Quattro, Inno Max, Veloce..."
                        >
                          <i class="fas fa-tag" slot="leading-icon" style="color: #6b7280;"></i>
                        </md-outlined-text-field>
                      </div>
                    </div>
                    
                    <md-filled-select
                      label="Limb Fitting"
                      :value="newSetup.limb_fitting || 'ILF'"
                      @change="newSetup.limb_fitting = $event.target.value"
                      class="w-full"
                    >
                      <md-select-option value="ILF">
                        <div slot="headline">ILF (International Limb Fitting)</div>
                      </md-select-option>
                      <md-select-option value="Formula">
                        <div slot="headline">Formula (WA Standard)</div>
                      </md-select-option>
                    </md-filled-select>
                  </div>

                  <!-- Longbow Configuration -->
                  <div v-else-if="newSetup.bow_type === 'longbow'" class="space-y-4">
                    <div>
                      <md-filled-select
                        label="Bow Brand/Maker"
                        :value="newSetup.bow_brand || ''"
                        @change="handleBrandSelection('bow_brand', $event.target.value)"
                        class="w-full"
                      >
                        <md-select-option value="">
                          <div slot="headline">Select Brand/Maker</div>
                        </md-select-option>
                        <md-select-option value="Howard Hill">
                          <div slot="headline">Howard Hill</div>
                        </md-select-option>
                        <md-select-option value="Bear">
                          <div slot="headline">Bear</div>
                        </md-select-option>
                        <md-select-option value="Bodnik">
                          <div slot="headline">Bodnik</div>
                        </md-select-option>
                        <md-select-option value="Black Widow">
                          <div slot="headline">Black Widow</div>
                        </md-select-option>
                        <md-select-option value="Great Plains">
                          <div slot="headline">Great Plains</div>
                        </md-select-option>
                        <md-select-option value="Three Rivers Archery">
                          <div slot="headline">Three Rivers Archery</div>
                        </md-select-option>
                        <md-select-option value="Martin">
                          <div slot="headline">Martin</div>
                        </md-select-option>
                        <md-select-option value="Samick">
                          <div slot="headline">Samick</div>
                        </md-select-option>
                        <md-select-option value="Other">
                          <div slot="headline">Other...</div>
                        </md-select-option>
                      </md-filled-select>
                      
                      <!-- Custom bow brand input -->
                      <md-outlined-text-field 
                        v-if="newSetup.bow_brand === 'Other'"
                        class="w-full mt-2"
                        :value="newSetup.custom_bow_brand || ''"
                        @input="newSetup.custom_bow_brand = $event.target.value"
                        label="Custom Brand/Maker Name"
                        placeholder="Enter brand or maker name..."
                        required
                      >
                        <i class="fas fa-edit" slot="leading-icon" style="color: #6b7280;"></i>
                      </md-outlined-text-field>
                    </div>
                  </div>

                  <!-- Traditional Bow Configuration -->
                  <div v-else-if="newSetup.bow_type === 'traditional'" class="space-y-4">
                    <md-filled-select
                      label="Construction Type"
                      :value="newSetup.construction || 'one_piece'"
                      @change="newSetup.construction = $event.target.value"
                      class="w-full"
                    >
                      <md-select-option value="one_piece">
                        <div slot="headline">One Piece</div>
                      </md-select-option>
                      <md-select-option value="two_piece">
                        <div slot="headline">Two Piece (Takedown)</div>
                      </md-select-option>
                    </md-filled-select>

                    <!-- Two-piece specific fields -->
                    <div v-if="newSetup.construction === 'two_piece'" class="space-y-4">
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Traditional Riser Brand -->
                        <div>
                          <md-filled-select
                            label="Riser Brand"
                            :value="newSetup.riser_brand || ''"
                            @change="handleBrandSelection('riser_brand', $event.target.value)"
                            class="w-full"
                          >
                            <md-select-option value="">
                              <div slot="headline">Select Riser Brand</div>
                            </md-select-option>
                            <md-select-option value="Samick">
                              <div slot="headline">Samick</div>
                            </md-select-option>
                            <md-select-option value="Bear">
                              <div slot="headline">Bear</div>
                            </md-select-option>
                            <md-select-option value="PSE">
                              <div slot="headline">PSE</div>
                            </md-select-option>
                            <md-select-option value="Martin">
                              <div slot="headline">Martin</div>
                            </md-select-option>
                            <md-select-option value="Black Widow">
                              <div slot="headline">Black Widow</div>
                            </md-select-option>
                            <md-select-option value="Sage">
                              <div slot="headline">Sage</div>
                            </md-select-option>
                            <md-select-option value="Other">
                              <div slot="headline">Other...</div>
                            </md-select-option>
                          </md-filled-select>
                          
                          <!-- Custom traditional riser brand input -->
                          <md-outlined-text-field 
                            v-if="newSetup.riser_brand === 'Other'"
                            class="w-full mt-2"
                            :value="newSetup.custom_trad_riser_brand || ''"
                            @input="newSetup.custom_trad_riser_brand = $event.target.value"
                            label="Custom Riser Brand"
                            placeholder="Enter riser brand name..."
                            required
                          >
                            <i class="fas fa-edit" slot="leading-icon" style="color: #6b7280;"></i>
                          </md-outlined-text-field>
                        </div>
                        
                        <!-- Traditional Limb Brand -->
                        <div>
                          <md-filled-select
                            label="Limb Brand"
                            :value="newSetup.limb_brand || ''"
                            @change="handleBrandSelection('limb_brand', $event.target.value)"
                            class="w-full"
                          >
                            <md-select-option value="">
                              <div slot="headline">Select Limb Brand</div>
                            </md-select-option>
                            <md-select-option value="Samick">
                              <div slot="headline">Samick</div>
                            </md-select-option>
                            <md-select-option value="Bear">
                              <div slot="headline">Bear</div>
                            </md-select-option>
                            <md-select-option value="PSE">
                              <div slot="headline">PSE</div>
                            </md-select-option>
                            <md-select-option value="Martin">
                              <div slot="headline">Martin</div>
                            </md-select-option>
                            <md-select-option value="Black Widow">
                              <div slot="headline">Black Widow</div>
                            </md-select-option>
                            <md-select-option value="Sage">
                              <div slot="headline">Sage</div>
                            </md-select-option>
                            <md-select-option value="Other">
                              <div slot="headline">Other...</div>
                            </md-select-option>
                          </md-filled-select>
                          
                          <!-- Custom traditional limb brand input -->
                          <md-outlined-text-field 
                            v-if="newSetup.limb_brand === 'Other'"
                            class="w-full mt-2"
                            :value="newSetup.custom_trad_limb_brand || ''"
                            @input="newSetup.custom_trad_limb_brand = $event.target.value"
                            label="Custom Limb Brand"
                            placeholder="Enter limb brand name..."
                            required
                          >
                            <i class="fas fa-edit" slot="leading-icon" style="color: #6b7280;"></i>
                          </md-outlined-text-field>
                        </div>
                      </div>
                      
                      <md-filled-select
                        label="Limb Fitting"
                        :value="newSetup.limb_fitting || 'ILF'"
                        @change="newSetup.limb_fitting = $event.target.value"
                        class="w-full"
                      >
                        <md-select-option value="ILF">
                          <div slot="headline">ILF (International Limb Fitting)</div>
                        </md-select-option>
                        <md-select-option value="Bolt_Down">
                          <div slot="headline">Bolt Down</div>
                        </md-select-option>
                      </md-filled-select>
                    </div>
                  </div>
                </div>

              </div>

              <!-- Draw Length Info -->
              <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <i class="fas fa-info-circle mr-2 text-blue-600"></i>
                  <strong>Draw Length:</strong> {{ user?.draw_length || '28.0' }}" (from your archer profile)
                </p>
                <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Update your draw length in the "Edit Profile" section above if needed.
                </p>
              </div>

              <!-- Description -->
              <div class="mb-6">
                <md-outlined-text-field 
                  class="w-full"
                  :value="newSetup.description"
                  @input="newSetup.description = $event.target.value"
                  label="Description (optional)"
                  type="textarea"
                  rows="3"
                  placeholder="Notes about this bow setup, intended use, etc..."
                >
                  <i class="fas fa-comment" slot="leading-icon" style="color: #6b7280;"></i>
                </md-outlined-text-field>
              </div>

              <!-- Action Buttons -->
              <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                <CustomButton
                  type="button"
                  @click="closeAddSetupModal"
                  variant="outlined"
                  class="text-gray-700 dark:text-gray-200"
                >
                  <i class="fas fa-times mr-2"></i>
                  Cancel
                </CustomButton>
                <CustomButton
                  type="submit"
                  variant="filled"
                  :disabled="isSavingSetup"
                  class="bg-blue-600 text-white hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700"
                >
                  <i v-if="isSavingSetup" class="fas fa-spinner fa-spin mr-2"></i>
                  <i v-else class="fas fa-save mr-2"></i>
                  <span v-if="isSavingSetup">Creating Setup...</span>
                  <span v-else>Create Setup</span>
                </CustomButton>
              </div>
              <p v-if="addSetupError" class="text-red-500 text-sm mt-3 flex items-center">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                {{ addSetupError }}
              </p>
            </form>
          </div>
        </div>

        <!-- Confirm Delete Modal -->
        <div v-if="isConfirmingDelete" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
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

        <!-- Arrow Search Modal -->
        <ArrowSearchModal
          :is-open="isArrowSearchOpen"
          :bow-setup="selectedBowSetup"
          @close="closeArrowSearchModal"
          @add-arrow="handleAddArrow"
        />
        <!-- End of Arrow Search Modal -->

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
import { ref, onMounted, watch } from 'vue';
import { useAuth } from '~/composables/useAuth';
import ArrowSearchModal from '~/components/ArrowSearchModal.vue';
import BowSetupArrowsList from '~/components/BowSetupArrowsList.vue';

const { user, logout, loginWithGoogle, updateUserProfile, fetchUser, fetchBowSetups, addBowSetup, deleteBowSetup, addArrowToSetup, fetchSetupArrows } = useAuth();

const isLoadingUser = ref(true);
const isEditing = ref(false);
const editedName = ref('');
const editedDrawLength = ref(28.0);
const editedSkillLevel = ref('intermediate');
const editedShootingStyle = ref('target');
const editedPreferredManufacturers = ref('');
const editedNotes = ref('');
const isSaving = ref(false);
const editError = ref(null);

const bowSetups = ref([]);
const isLoadingSetups = ref(true);
const isAddingSetup = ref(false);
const isSavingSetup = ref(false);
const addSetupError = ref(null);
const isConfirmingDelete = ref(false);
const setupToDeleteId = ref(null);
const deleteSetupError = ref(null);

// Arrow search modal state
const isArrowSearchOpen = ref(false);
const selectedBowSetup = ref(null);

const newSetup = ref({
  name: '',
  bow_type: '',
  draw_weight: 45,
  description: '',
  // Compound specific
  brand: '',
  custom_brand: '',
  compound_model: '', // New field for compound bow model name
  ibo_speed: '',
  // Recurve specific
  riser_brand: '',
  custom_riser_brand: '',
  limb_brand: '',
  custom_limb_brand: '',
  limb_fitting: 'ILF',
  bow_usage: '', // New field for Olympic/Barebow/other
  riser_model: '', // New field for riser model name
  limb_model: '', // New field for limb model name
  // Longbow specific
  bow_brand: '',
  custom_bow_brand: '',
  // Traditional specific
  construction: 'one_piece',
  custom_trad_riser_brand: '',
  custom_trad_limb_brand: '',
});

const openEditModal = () => {
  editedName.value = user.value?.name || '';
  editedDrawLength.value = user.value?.draw_length || 28.0;
  editedSkillLevel.value = user.value?.skill_level || 'intermediate';
  editedShootingStyle.value = user.value?.shooting_style || 'target';
  editedPreferredManufacturers.value = (user.value?.preferred_manufacturers || []).join(', ');
  editedNotes.value = user.value?.notes || '';
  isEditing.value = true;
  editError.value = null;
};

const closeEditModal = () => {
  isEditing.value = false;
};

const saveProfile = async () => {
  isSaving.value = true;
  editError.value = null;
  try {
    // Parse preferred manufacturers from comma-separated string
    const preferredManufacturers = editedPreferredManufacturers.value
      .split(',')
      .map(brand => brand.trim())
      .filter(brand => brand.length > 0);
    
    await updateUserProfile({
      name: editedName.value,
      draw_length: editedDrawLength.value,
      skill_level: editedSkillLevel.value,
      shooting_style: editedShootingStyle.value,
      preferred_manufacturers: preferredManufacturers,
      notes: editedNotes.value
    });
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
  newSetup.value = {
    name: '',
    bow_type: '',
    draw_weight: 45,
    description: '',
    // Compound specific
    brand: '',
    custom_brand: '',
    compound_model: '', // New field for compound bow model name
    ibo_speed: '',
    // Recurve specific
    riser_brand: '',
    custom_riser_brand: '',
    limb_brand: '',
    custom_limb_brand: '',
    limb_fitting: 'ILF',
    bow_usage: '', // New field for Olympic/Barebow/other
    riser_model: '', // New field for riser model name
    limb_model: '', // New field for limb model name
    // Longbow specific
    bow_brand: '',
    custom_bow_brand: '',
    // Traditional specific
    construction: 'one_piece',
    custom_trad_riser_brand: '',
    custom_trad_limb_brand: '',
  };
  addSetupError.value = null;
  isAddingSetup.value = true;
};

const closeAddSetupModal = () => {
  isAddingSetup.value = false;
};

const handleBrandSelection = (fieldName, value) => {
  newSetup.value[fieldName] = value;
  // Clear custom field when switching away from "Other"
  if (value !== 'Other') {
    const customFields = {
      'brand': 'custom_brand',
      'riser_brand': 'custom_riser_brand', 
      'limb_brand': 'custom_limb_brand',
      'bow_brand': 'custom_bow_brand'
    };
    
    const traditionalFields = {
      'riser_brand': 'custom_trad_riser_brand',
      'limb_brand': 'custom_trad_limb_brand'
    };
    
    if (customFields[fieldName]) {
      newSetup.value[customFields[fieldName]] = '';
    }
    
    // Clear traditional custom fields
    if (newSetup.value.bow_type === 'traditional' && traditionalFields[fieldName]) {
      newSetup.value[traditionalFields[fieldName]] = '';
    }
  }
};

const saveBowSetup = async () => {
  isSavingSetup.value = true;
  addSetupError.value = null;
  try {
    // Handle brand selection logic - use custom brand if "Other" is selected
    const getBrandValue = (brandField, customField) => {
      const selectedBrand = newSetup.value[brandField];
      if (selectedBrand === 'Other') {
        return newSetup.value[customField] || null;
      }
      return selectedBrand || null;
    };

    // Send data in the flat format expected by the API
    const setupData = {
      name: newSetup.value.name,
      bow_type: newSetup.value.bow_type,
      draw_weight: Number(newSetup.value.draw_weight),
      draw_length: user.value?.draw_length || 28.0, // Use user's draw length from profile
      description: newSetup.value.description,
      // Bow type specific fields with custom brand handling
      brand: getBrandValue('brand', 'custom_brand'),
      ibo_speed: newSetup.value.ibo_speed ? Number(newSetup.value.ibo_speed) : null,
      riser_brand: newSetup.value.bow_type === 'traditional' 
        ? getBrandValue('riser_brand', 'custom_trad_riser_brand')
        : getBrandValue('riser_brand', 'custom_riser_brand'),
      limb_brand: newSetup.value.bow_type === 'traditional'
        ? getBrandValue('limb_brand', 'custom_trad_limb_brand')
        : getBrandValue('limb_brand', 'custom_limb_brand'),
      limb_fitting: newSetup.value.limb_fitting || null,
      bow_brand: getBrandValue('bow_brand', 'custom_bow_brand'),
      construction: newSetup.value.construction || null,
    };

    await addBowSetup(setupData);
    closeAddSetupModal();
    await loadBowSetups(); // Reload setups after adding
  } catch (err) {
    console.error('Error saving bow setup:', err);
    addSetupError.value = err.message || 'Failed to add bow setup.';
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

// Arrow search modal methods
const openArrowSearchModal = (setup) => {
  selectedBowSetup.value = setup;
  isArrowSearchOpen.value = true;
};

const closeArrowSearchModal = () => {
  isArrowSearchOpen.value = false;
  selectedBowSetup.value = null;
};

const handleAddArrow = async (arrowData) => {
  try {
    // Check if a bow setup is selected
    if (!selectedBowSetup.value) {
      alert('Please select a bow setup first before adding arrows.');
      return;
    }
    
    // Create the API payload
    const apiData = {
      arrow_id: arrowData.arrow.id,
      arrow_length: arrowData.adjustments.arrow_length,
      point_weight: arrowData.adjustments.point_weight,
      calculated_spine: arrowData.calculatedSpine,
      compatibility_score: arrowData.compatibility_score,
      notes: `Added via arrow search - ${arrowData.compatibility_score}% match`
    };
    
    // Call the API to add arrow to setup
    await addArrowToSetup(selectedBowSetup.value.id, apiData);
    
    // Show success message (you could add a toast notification here)
    alert(`Successfully added ${arrowData.arrow.manufacturer} ${arrowData.arrow.model_name} to ${selectedBowSetup.value.name}!`);
    
    // Reload arrows for the setup to show the new arrow
    await loadArrowsForSetup(selectedBowSetup.value.id);
    
  } catch (err) {
    console.error('Error adding arrow to setup:', err);
    alert('Failed to add arrow to setup. Please try again.');
  }
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

const removeArrowFromSetup = async (arrowSetupId) => {
  if (!confirm('Are you sure you want to remove this arrow from the setup?')) {
    return;
  }
  
  try {
    const config = useRuntimeConfig();
    const { token } = useAuth();
    
    // Call API to remove arrow from setup (need to implement this endpoint)
    const response = await fetch(`${config.public.apiBase}/setup-arrows/${arrowSetupId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to remove arrow');
    }
    
    // Reload all setups to refresh the display
    await loadBowSetups();
    
  } catch (err) {
    console.error('Error removing arrow from setup:', err);
    alert('Failed to remove arrow. Please try again.');
  }
};

const viewArrowDetails = (arrowId) => {
  // Navigate to arrow details page
  navigateTo(`/arrows/${arrowId}`);
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

const formatShootingStyle = (style) => {
  const styles = {
    'target': 'Target',
    'hunting': 'Hunting',
    'traditional': 'Traditional',
    '3d': '3D'
  };
  return styles[style] || style;
};

const getSkillLevelClass = (level) => {
  const classes = {
    'beginner': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'intermediate': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'advanced': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  };
  return classes[level] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
};

const getShootingStyleClass = (style) => {
  const classes = {
    'target': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'hunting': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'traditional': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    '3d': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  };
  return classes[style] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
};

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
});

// Watch for changes in the user object and update editedName accordingly
watch(user, async (newUser) => {
  if (newUser) {
    editedName.value = newUser.name || '';
    // If user just logged in or user object changed, reload bow setups
    await loadBowSetups();
  }
}, { immediate: true });

definePageMeta({
  middleware: ['auth-check']
});
</script>

<style scoped>
.form-input,
.form-select,
.form-textarea {
  @apply px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100;
}
.form-textarea {
  @apply w-full h-24 resize-y;
}
</style>