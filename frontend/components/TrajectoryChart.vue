<template>
  <div class="trajectory-chart-container" :class="props.mobileHorizontal ? '' : 'bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden'">
    <!-- Compact Show Trajectory Button (when chart is not displayed) -->
    <div v-if="!showChart" class="p-4 text-center">
      <button 
        @click="generateTrajectoryChart"
        :disabled="isLoading"
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md text-sm font-medium transition-colors flex items-center mx-auto"
      >
        <i v-if="isLoading" class="fas fa-spinner fa-spin mr-2 text-xs"></i>
        <i v-else class="fas fa-chart-line mr-2 text-xs"></i>
        {{ isLoading ? 'Generating...' : 'Show Flight Trajectory' }}
      </button>
    </div>

    <!-- Mobile Vertical Layout -->
    <div v-else-if="props.mobileHorizontal" class="p-4">
      <!-- Header - Mobile Compact -->
      <div class="mb-4">
        <div class="flex flex-col gap-3">
          <div class="flex items-center justify-between">
            <h4 class="text-base font-medium text-gray-900 dark:text-white flex items-center">
              <span class="mr-2 text-sm">🎯</span>
              Flight Trajectory
            </h4>
            <button 
              @click="hideChart"
              class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              title="Close trajectory chart"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <!-- Speed Source Indicator -->
          <div v-if="props.arrowData?.speed_source" class="flex items-center">
            <span class="text-xs px-2 py-1 rounded-full" :class="getSpeedSourceClass()">
              <i :class="getSpeedSourceIcon()" class="mr-1"></i>
              {{ getSpeedSourceText() }}
            </span>
          </div>
          
          <!-- PRIMARY CONTROLS - Always Visible -->
          <div class="space-y-3">
            <!-- Units Toggle & Quick Range -->
            <div class="flex flex-col gap-2">
              <div class="flex bg-gray-100 dark:bg-gray-700 rounded-md text-xs">
                <button 
                  @click="setUnits('imperial')"
                  :class="[
                    'flex-1 px-2 py-1.5 rounded-l-md transition-colors min-h-[44px] touch-manipulation',
                    units === 'imperial' 
                      ? 'bg-blue-600 text-white' 
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  ]"
                >
                  Yards
                </button>
                <button 
                  @click="setUnits('metric')"
                  :class="[
                    'flex-1 px-2 py-1.5 rounded-r-md transition-colors min-h-[44px] touch-manipulation',
                    units === 'metric' 
                      ? 'bg-blue-600 text-white' 
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  ]"
                >
                  Meters
                </button>
              </div>
              
              <!-- Quick Range Presets -->
              <div class="flex gap-1 text-xs">
                <button
                  v-for="preset in rangePresets.slice(0, 3)"
                  :key="preset.value"
                  @click="setRangePreset(preset.value)"
                  :class="[
                    'flex-1 py-2 rounded-md transition-colors min-h-[44px] touch-manipulation',
                    trajectorySettings.maxRange === preset.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-800'
                  ]"
                >
                  {{ preset.label }}
                </button>
              </div>
            </div>
            
            <!-- SECONDARY CONTROLS - Shooting Scenarios -->
            <div>
              <button 
                @click="showSecondaryControls = !showSecondaryControls"
                :class="[
                  'w-full px-3 py-2 text-xs rounded-md transition-colors min-h-[44px] touch-manipulation flex items-center justify-between',
                  showSecondaryControls
                    ? 'bg-green-600 text-white'
                    : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-800'
                ]"
              >
                <span class="flex items-center">
                  <i class="fas fa-bullseye mr-2"></i>
                  Shooting Scenarios
                </span>
                <i :class="showSecondaryControls ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="text-xs"></i>
              </button>
              
              <div v-if="showSecondaryControls" class="grid grid-cols-2 gap-1 mt-2 text-xs">
                <button
                  v-for="preset in shootingPresets"
                  :key="preset.key"
                  @click="applyShootingPreset(preset)"
                  :class="[
                    'px-3 py-3 rounded-md transition-colors text-left min-h-[44px] touch-manipulation',
                    currentPreset === preset.key
                      ? 'bg-green-600 text-white'
                      : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-800'
                  ]"
                >
                  <div class="font-medium text-xs">{{ preset.name }}</div>
                  <div class="text-xs opacity-80">{{ preset.description }}</div>
                </button>
              </div>
            </div>
            
            <!-- TERTIARY CONTROLS - Advanced Settings -->
            <button 
              @click="toggleEnvironmentalControls"
              :class="[
                'w-full px-3 py-2 text-xs rounded-md transition-colors min-h-[44px] touch-manipulation flex items-center justify-between',
                showEnvironmentalControls
                  ? 'bg-blue-600 text-white'
                  : 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-800'
              ]"
            >
              <span class="flex items-center">
                <i class="fas fa-cog mr-2"></i>
                Advanced Settings
              </span>
              <i :class="showEnvironmentalControls ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="text-xs"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- TERTIARY CONTROLS - Advanced Environmental Settings -->
      <div v-if="showEnvironmentalControls" class="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-300 dark:border-gray-600">
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center">
          <i class="fas fa-sliders-h mr-2"></i>
          Advanced Trajectory Settings
        </h4>
        
        <!-- Fine Range Control -->
        <div class="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <label class="block text-xs text-blue-700 dark:text-blue-300 mb-2 font-medium">
            <i class="fas fa-crosshairs mr-1"></i>
            Fine Range Adjustment: {{ trajectorySettings.maxRange }} {{ getDistanceUnit() }}
          </label>
          <input 
            v-model.number="trajectorySettings.maxRange"
            @change="updateTrajectory"
            type="range" 
            :min="units === 'metric' ? 25 : 30" 
            :max="units === 'metric' ? 110 : 120" 
            step="1"
            class="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
          >
          <div class="flex justify-between text-xs text-blue-600 dark:text-blue-400 mt-1">
            <span>{{ units === 'metric' ? 25 : 30 }}</span>
            <span>{{ units === 'metric' ? 110 : 120 }}</span>
          </div>
        </div>
        
        <!-- Distance Interval Control -->
        <div class="mb-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <label class="block text-xs text-green-700 dark:text-green-300 mb-2 font-medium">
            <i class="fas fa-ruler mr-1"></i>
            Distance Marks: {{ trajectorySettings.distanceInterval }} {{ getDistanceUnit() }} intervals
          </label>
          <input 
            v-model.number="trajectorySettings.distanceInterval"
            @change="updateTrajectory"
            type="range" 
            min="1" max="10" step="1"
            class="w-full h-2 bg-green-200 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
          >
        </div>
        
        <!-- Environmental Conditions -->
        <div class="space-y-3">
          <h6 class="text-xs font-medium text-gray-700 dark:text-gray-300 flex items-center">
            <i class="fas fa-cloud-sun mr-1"></i>
            Environmental Conditions
          </h6>
          <div class="grid grid-cols-1 gap-3">
            <div class="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <label class="block text-xs text-gray-600 dark:text-gray-400 mb-2">Wind Speed: {{ environmentalConditions.windSpeed }} mph</label>
              <input 
                v-model.number="environmentalConditions.windSpeed"
                @change="updateTrajectory"
                type="range" 
                min="0" max="15" step="1"
                class="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
              >
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span><span>15 mph</span>
              </div>
            </div>
            <div class="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <label class="block text-xs text-gray-600 dark:text-gray-400 mb-2">Temperature: {{ environmentalConditions.temperature }}°F</label>
              <input 
                v-model.number="environmentalConditions.temperature"
                @change="updateTrajectory"
                type="range" 
                min="30" max="90" step="5"
                class="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
              >
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>30°F</span><span>90°F</span>
              </div>
            </div>
            <div class="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <label class="block text-xs text-gray-600 dark:text-gray-400 mb-2">Sight Elevation: {{ trajectorySettings.sightElevation }}"</label>
              <input 
                v-model.number="trajectorySettings.sightElevation"
                @change="updateTrajectory"
                type="range" 
                min="-3" max="3" step="0.1"
                class="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
              >
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>-3"</span><span>+3"</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart Container -->
      <div class="chart-wrapper overflow-x-auto mb-4" style="position: relative; height: clamp(300px, 35vh, 400px); min-height: 280px;">
        <canvas ref="chartCanvas" class="max-w-full"></canvas>
      </div>

      <!-- Trajectory Summary -->
      <div v-if="trajectorySummary" class="space-y-3">
        <!-- Primary Stats -->
        <div class="grid grid-cols-3 gap-2 text-sm">
          <div class="bg-blue-50 dark:bg-blue-900/30 p-2 rounded-lg text-center">
            <div class="text-blue-600 dark:text-blue-400 font-medium text-xs">Max Range</div>
            <div class="text-gray-900 dark:text-white font-semibold">{{ getDisplayMaxRange() }} {{ getDistanceUnit() }}</div>
          </div>
          <div class="bg-green-50 dark:bg-green-900/30 p-2 rounded-lg text-center">
            <div class="text-green-600 dark:text-green-400 font-medium text-xs">Peak Height</div>
            <div class="text-gray-900 dark:text-white font-semibold">{{ getDisplayPeakHeight() }}{{ getHeightUnit() }}</div>
          </div>
          <div class="bg-orange-50 dark:bg-orange-900/30 p-2 rounded-lg text-center">
            <div class="text-orange-600 dark:text-orange-400 font-medium text-xs">Drop at {{ getDisplayDropReference() }}{{ getDistanceUnit() }}</div>
            <div class="text-gray-900 dark:text-white font-semibold">{{ getDisplayDropAt40() }}{{ getHeightUnit() }}</div>
          </div>
        </div>
        
        <!-- Holdover Guidance -->
        <div v-if="getHoldoverGuidance()" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
          <h5 class="text-yellow-800 dark:text-yellow-200 font-medium text-sm mb-2 flex items-center">
            <i class="fas fa-crosshairs mr-2"></i>
            Aiming Guidance
          </h5>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            <div v-for="guide in getHoldoverGuidance()" :key="guide.distance" 
                 class="flex justify-between items-center py-1">
              <span class="text-yellow-700 dark:text-yellow-300">{{ guide.distance }}{{ getDistanceUnit() }}:</span>
              <span class="font-medium text-yellow-900 dark:text-yellow-100">{{ guide.guidance }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State for Mobile -->
      <div v-if="isLoading" class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 flex items-center justify-center rounded-lg">
        <div class="text-center">
          <div class="animate-spin h-6 w-6 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <div class="text-xs text-gray-600 dark:text-gray-400">Calculating trajectory...</div>
        </div>
      </div>
    </div>

    <!-- Desktop Vertical Layout (when chart is shown) -->
    <div v-else class="p-4">
      <!-- Header - Mobile Responsive -->
      <div class="mb-4">
        <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
          <div class="flex flex-col">
            <h4 class="text-base font-medium text-gray-900 dark:text-white flex items-center">
              <span class="mr-2 text-sm">🎯</span>
              Flight Trajectory
            </h4>
            <!-- Speed Source Indicator -->
            <div v-if="props.arrowData?.speed_source" class="flex items-center mt-1">
              <span class="text-xs px-2 py-1 rounded-full" :class="getSpeedSourceClass()">
                <i :class="getSpeedSourceIcon()" class="mr-1"></i>
                {{ getSpeedSourceText() }}
              </span>
            </div>
          </div>
          
          <!-- PRIMARY CONTROLS - Desktop Layout -->
          <div class="flex flex-col sm:flex-row gap-2 sm:gap-1">
            <!-- Units Toggle -->
            <div class="flex bg-gray-100 dark:bg-gray-700 rounded-md text-xs w-full sm:w-auto">
              <button 
                @click="setUnits('imperial')"
                :class="[
                  'flex-1 sm:flex-none px-2 py-1.5 rounded-l-md transition-colors',
                  units === 'imperial' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                ]"
              >
                Yards
              </button>
              <button 
                @click="setUnits('metric')"
                :class="[
                  'flex-1 sm:flex-none px-2 py-1.5 rounded-r-md transition-colors',
                  units === 'metric' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                ]"
              >
                Meters
              </button>
            </div>
            
            <!-- Quick Range Presets - Desktop Inline -->
            <div class="hidden sm:flex gap-1 text-xs">
              <button
                v-for="preset in rangePresets.slice(0, 3)"
                :key="preset.value"
                @click="setRangePreset(preset.value)"
                :class="[
                  'px-2 py-1.5 rounded-md transition-colors',
                  trajectorySettings.maxRange === preset.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-800'
                ]"
              >
                {{ preset.label }}
              </button>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex gap-1">
              <button 
                @click="showSecondaryControls = !showSecondaryControls"
                :class="[
                  'px-2 py-1.5 text-xs rounded-md transition-colors',
                  showSecondaryControls
                    ? 'bg-green-600 text-white'
                    : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-800'
                ]"
              >
                <i class="fas fa-bullseye mr-1"></i>
                <span class="hidden sm:inline">Scenarios</span>
                <span class="sm:hidden">Scenarios</span>
              </button>
              <button 
                @click="toggleEnvironmentalControls"
                :class="[
                  'px-2 py-1.5 text-xs rounded-md transition-colors',
                  showEnvironmentalControls
                    ? 'bg-blue-600 text-white'
                    : 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-800'
                ]"
              >
                <i class="fas fa-cog mr-1"></i>
                <span class="hidden sm:inline">Advanced</span>
                <span class="sm:hidden">Settings</span>
              </button>
              <button 
                @click="hideChart"
                class="px-2 py-1.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title="Close trajectory chart"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Tooltip moved to separate line on mobile -->
        <div class="mt-2 sm:mt-0 flex justify-center sm:justify-end">
          <PerformanceTooltip 
            :title="'Trajectory Analysis'"
            :content="'Visual representation of arrow flight path showing drop, range, and environmental effects. Toggle between yards/meters and adjust environmental settings.'"
          />
        </div>
        
        <!-- SECONDARY CONTROLS - Desktop Shooting Scenarios -->
        <div v-if="showSecondaryControls" class="grid grid-cols-2 lg:grid-cols-4 gap-2 mt-3 text-xs">
          <button
            v-for="preset in shootingPresets"
            :key="preset.key"
            @click="applyShootingPreset(preset)"
            :class="[
              'px-3 py-2 rounded-md transition-colors text-left',
              currentPreset === preset.key
                ? 'bg-green-600 text-white'
                : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-800'
            ]"
          >
            <div class="font-medium text-xs">{{ preset.name }}</div>
            <div class="text-xs opacity-80">{{ preset.description }}</div>
          </button>
        </div>
      </div>

    <!-- TERTIARY CONTROLS - Desktop Advanced Environmental Settings -->
    <div v-if="showEnvironmentalControls" class="mb-4 p-3 sm:p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-300 dark:border-gray-600">
      <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Trajectory Settings</h4>
      
      <!-- Distance Range Control -->
      <div class="mb-4 p-2 sm:p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="flex-1">
            <label class="block text-xs text-blue-700 dark:text-blue-300 mb-2 font-medium">
              <i class="fas fa-crosshairs mr-1"></i>
              Maximum Range
            </label>
            <input 
              v-model.number="trajectorySettings.maxRange"
              @change="updateTrajectory"
              type="range" 
              :min="units === 'metric' ? 25 : 30" 
              :max="units === 'metric' ? 110 : 120" 
              step="5"
              class="w-full h-3 bg-blue-200 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
            >
            <div class="flex justify-between text-xs text-blue-600 dark:text-blue-400 mt-1">
              <span>{{ units === 'metric' ? 25 : 30 }} {{ getDistanceUnit() }}</span>
              <span class="font-medium">{{ trajectorySettings.maxRange }} {{ getDistanceUnit() }}</span>
              <span>{{ units === 'metric' ? 110 : 120 }} {{ getDistanceUnit() }}</span>
            </div>
          </div>
          
          <!-- Quick Range Buttons -->
          <div class="flex flex-wrap gap-1 sm:gap-2">
            <button
              v-for="preset in rangePresets"
              :key="preset.value"
              @click="setRangePreset(preset.value)"
              :class="[
                'px-2 py-0.5 text-xs rounded-full transition-colors',
                trajectorySettings.maxRange === preset.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-blue-200 dark:bg-blue-800 text-blue-800 dark:text-blue-200 hover:bg-blue-300 dark:hover:bg-blue-700'
              ]"
            >
              {{ preset.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Distance Interval Control -->
      <div class="mb-4 p-2 sm:p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="flex-1">
            <label class="block text-xs text-green-700 dark:text-green-300 mb-2 font-medium">
              <i class="fas fa-ruler mr-1"></i>
              Distance Intervals (Dot Spacing)
            </label>
            <input 
              v-model.number="trajectorySettings.distanceInterval"
              @change="updateTrajectory"
              type="range" 
              :min="units === 'metric' ? 2 : 2" 
              :max="units === 'metric' ? 15 : 20" 
              step="1"
              class="w-full h-3 bg-green-200 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
            >
            <div class="flex justify-between text-xs text-green-600 dark:text-green-400 mt-1">
              <span>2 {{ getDistanceUnit() }}</span>
              <span class="font-medium">{{ trajectorySettings.distanceInterval }} {{ getDistanceUnit() }}</span>
              <span>{{ units === 'metric' ? 15 : 20 }} {{ getDistanceUnit() }}</span>
            </div>
          </div>
          
          <!-- Quick Interval Buttons -->
          <div class="flex flex-wrap gap-1 sm:gap-2">
            <button
              v-for="preset in intervalPresets"
              :key="preset.value"
              @click="setIntervalPreset(preset.value)"
              :class="[
                'px-2 py-0.5 text-xs rounded-full transition-colors',
                trajectorySettings.distanceInterval === preset.value
                  ? 'bg-green-600 text-white'
                  : 'bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200 hover:bg-green-300 dark:hover:bg-green-700'
              ]"
            >
              {{ preset.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Sight Elevation Control -->
      <div class="mb-4 p-2 sm:p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="flex-1">
            <label class="block text-xs text-orange-700 dark:text-orange-300 mb-2 font-medium">
              <i class="fas fa-crosshairs mr-1"></i>
              Sight Elevation: {{ trajectorySettings.sightElevation }}"
            </label>
            <input 
              v-model.number="trajectorySettings.sightElevation"
              @change="updateTrajectory"
              type="range" 
              min="-10" 
              max="20" 
              step="0.5"
              class="w-full h-3 bg-orange-200 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
            >
            <div class="flex justify-between text-xs text-orange-600 dark:text-orange-400 mt-1">
              <span>-10"</span>
              <span class="font-medium">{{ trajectorySettings.sightElevation }}" elevation</span>
              <span>+20"</span>
            </div>
          </div>
          
          <!-- Quick Elevation Buttons -->
          <div class="flex flex-wrap gap-1 sm:gap-2">
            <button
              v-for="preset in [0, 3, 6, 9, 12]"
              :key="preset"
              @click="trajectorySettings.sightElevation = preset; updateTrajectory()"
              :class="[
                'px-2 py-0.5 text-xs rounded-full transition-colors',
                trajectorySettings.sightElevation === preset
                  ? 'bg-orange-600 text-white'
                  : 'bg-orange-200 dark:bg-orange-800 text-orange-800 dark:text-orange-200 hover:bg-orange-300 dark:hover:bg-orange-700'
              ]"
            >
              {{ preset }}"
            </button>
          </div>
        </div>
        <p class="text-xs text-orange-600 dark:text-orange-400 mt-2">
          <i class="fas fa-info-circle mr-1"></i>
          Positive values show how high to aim above your target to compensate for arrow drop.
        </p>
      </div>

      <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Environmental Conditions</h5>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Wind Speed (mph)</label>
          <input 
            v-model.number="environmentalConditions.windSpeed"
            @change="updateTrajectory"
            type="range" 
            min="0" 
            max="20" 
            step="1"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
          >
          <span class="text-xs text-gray-500">{{ environmentalConditions.windSpeed }} mph</span>
        </div>
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Temperature (°F)</label>
          <input 
            v-model.number="environmentalConditions.temperature"
            @change="updateTrajectory"
            type="range" 
            min="20" 
            max="100" 
            step="5"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
          >
          <span class="text-xs text-gray-500">{{ environmentalConditions.temperature }}°F</span>
        </div>
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Altitude (ft)</label>
          <input 
            v-model.number="environmentalConditions.altitude"
            @change="updateTrajectory"
            type="range" 
            min="0" 
            max="8000" 
            step="500"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mobile-slider-safe"
          >
          <span class="text-xs text-gray-500">{{ environmentalConditions.altitude }} ft</span>
        </div>
      </div>
    </div>

    <!-- Chart Container -->
    <div class="chart-wrapper overflow-x-auto" style="position: relative; height: clamp(320px, 40vh, 450px); min-height: 300px;">
      <canvas ref="chartCanvas" class="max-w-full"></canvas>
    </div>

    <!-- Trajectory Summary -->
    <div v-if="trajectorySummary" class="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3 text-sm">
      <div class="bg-blue-50 dark:bg-blue-900/30 p-2 sm:p-3 rounded-lg text-center sm:text-left">
        <div class="text-blue-600 dark:text-blue-400 font-medium">Max Range</div>
        <div class="text-gray-900 dark:text-white font-semibold text-lg">{{ getDisplayMaxRange() }} {{ getDistanceUnit() }}</div>
      </div>
      <div class="bg-green-50 dark:bg-green-900/30 p-2 sm:p-3 rounded-lg text-center sm:text-left">
        <div class="text-green-600 dark:text-green-400 font-medium">Peak Height</div>
        <div class="text-gray-900 dark:text-white font-semibold text-lg">{{ getDisplayPeakHeight() }}{{ getHeightUnit() }}</div>
      </div>
      <div class="bg-orange-50 dark:bg-orange-900/30 p-2 sm:p-3 rounded-lg text-center sm:text-left">
        <div class="text-orange-600 dark:text-orange-400 font-medium">Drop at {{ getDisplayDropReference() }}{{ getDistanceUnit() }}</div>
        <div class="text-gray-900 dark:text-white font-semibold text-lg">{{ getDisplayDropAt40() }}{{ getHeightUnit() }}</div>
      </div>
    </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 flex items-center justify-center rounded-lg">
        <div class="text-center">
          <div class="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <div class="text-sm text-gray-600 dark:text-gray-400">Calculating trajectory...</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick, markRaw } from 'vue'
import PerformanceTooltip from '~/components/PerformanceTooltip.vue'
import { useApi } from '~/composables/useApi'
import { useTrajectoryCalculation } from '~/composables/useTrajectoryCalculation'
// Chart.js loaded from CDN to avoid build issues
const initializeChart = async () => {
  if (typeof window === 'undefined') return null
  
  // Check if Chart.js is already loaded from CDN
  if (window.Chart) {
    return window.Chart
  }
  
  // Load Chart.js from CDN if not available
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js'
    script.onload = () => {
      if (window.Chart) {
        resolve(window.Chart)
      } else {
        reject(new Error('Chart.js failed to load from CDN'))
      }
    }
    script.onerror = () => reject(new Error('Failed to load Chart.js script'))
    document.head.appendChild(script)
  })
}

const props = defineProps({
  arrowData: {
    type: Object,
    required: true
  },
  bowConfig: {
    type: Object,
    required: true
  },
  mobileHorizontal: {
    type: Boolean,
    default: false
  }
})

// Composables
const api = useApi()
const {
  isCalculating: isApiCalculating,
  trajectoryData: apiTrajectoryData,
  error: trajectoryError,
  hasTrajectoryData,
  performanceSummary,
  trajectoryPoints,
  calculateTrajectory,
  calculateSimplifiedTrajectory,
  buildArrowData,
  buildBowConfig
} = useTrajectoryCalculation()

// Component state
const chartCanvas = ref(null)
const chartInstance = ref(null)
const isLoading = ref(false)
const showChart = ref(false)
const showEnvironmentalControls = ref(false)
const showSecondaryControls = ref(false)
const trajectorySummary = ref(null)
const units = ref('imperial') // 'imperial' or 'metric'

// Trajectory settings
const trajectorySettings = ref({
  maxRange: 120,        // Default to 120 yards (show full flight path)
  distanceInterval: 5,  // Default to 5 yard/meter intervals (for dot spacing on trajectory line)
  sightElevation: 0     // Sight elevation in inches above line of sight (for aiming)
})

// Current active preset
const currentPreset = ref('custom')

// Shooting scenario presets for common archery situations
const shootingPresets = computed(() => {
  if (units.value === 'metric') {
    return [
      {
        key: '20yd_pin',
        name: '20m Pin',
        description: 'Multi-pin sight',
        settings: {
          maxRange: 70,
          distanceInterval: 5,
          sightElevation: 0,
          windSpeed: 0,
          temperature: 20
        }
      },
      {
        key: 'hunting',
        name: '30m Hunting',
        description: 'Ethical shots',
        settings: {
          maxRange: 90,
          distanceInterval: 5,
          sightElevation: 4,
          windSpeed: 5,
          temperature: 15
        }
      },
      {
        key: '3d_course',
        name: '3D Course',
        description: 'Unknown distance',
        settings: {
          maxRange: 110,
          distanceInterval: 10,
          sightElevation: 2,
          windSpeed: 3,
          temperature: 20
        }
      },
      {
        key: 'long_range',
        name: 'Long Range',
        description: '70m+ shots',
        settings: {
          maxRange: 130,
          distanceInterval: 10,
          sightElevation: 8,
          windSpeed: 8,
          temperature: 20
        }
      }
    ]
  } else {
    return [
      {
        key: '20yd_pin',
        name: '20yd Pin',
        description: 'Multi-pin sight',
        settings: {
          maxRange: 80,
          distanceInterval: 5,
          sightElevation: 0,
          windSpeed: 0,
          temperature: 70
        }
      },
      {
        key: 'hunting',
        name: '30yd Hunting',
        description: 'Ethical shots',
        settings: {
          maxRange: 100,
          distanceInterval: 5,
          sightElevation: 4,
          windSpeed: 5,
          temperature: 60
        }
      },
      {
        key: '3d_course',
        name: '3D Course',
        description: 'Unknown distance',
        settings: {
          maxRange: 120,
          distanceInterval: 10,
          sightElevation: 2,
          windSpeed: 3,
          temperature: 70
        }
      },
      {
        key: 'long_range',
        name: 'Long Range',
        description: '80yd+ shots',
        settings: {
          maxRange: 140,
          distanceInterval: 10,
          sightElevation: 8,
          windSpeed: 8,
          temperature: 70
        }
      }
    ]
  }
})

// Range presets for quick selection
const rangePresets = computed(() => {
  if (units.value === 'metric') {
    return [
      { label: '50m', value: 50 },
      { label: '70m', value: 70 },
      { label: '90m', value: 90 },
      { label: '110m', value: 110 },
      { label: '130m', value: 130 },
      { label: 'Auto', value: 150 }
    ]
  } else {
    return [
      { label: '60yd', value: 60 },
      { label: '80yd', value: 80 },
      { label: '100yd', value: 100 },
      { label: '120yd', value: 120 },
      { label: '140yd', value: 140 },
      { label: 'Auto', value: 160 }
    ]
  }
})

// Set range preset function
const setRangePreset = (value) => {
  trajectorySettings.value.maxRange = value
  currentPreset.value = 'custom' // Reset to custom when manually adjusting
  updateTrajectory()
}

// Distance interval presets for quick selection
const intervalPresets = computed(() => {
  if (units.value === 'metric') {
    return [
      { label: '2m', value: 2 },
      { label: '5m', value: 5 },
      { label: '10m', value: 10 }
    ]
  } else {
    return [
      { label: '2yd', value: 2 },
      { label: '5yd', value: 5 },
      { label: '10yd', value: 10 }
    ]
  }
})

// Set interval preset function
const setIntervalPreset = (value) => {
  trajectorySettings.value.distanceInterval = value
  currentPreset.value = 'custom' // Reset to custom when manually adjusting
  updateTrajectory()
}

// Apply shooting scenario preset
const applyShootingPreset = (preset) => {
  currentPreset.value = preset.key
  
  // Apply all preset settings
  trajectorySettings.value.maxRange = preset.settings.maxRange
  trajectorySettings.value.distanceInterval = preset.settings.distanceInterval
  trajectorySettings.value.sightElevation = preset.settings.sightElevation
  
  // Apply environmental conditions
  environmentalConditions.value.windSpeed = preset.settings.windSpeed
  environmentalConditions.value.temperature = preset.settings.temperature
  
  // Update trajectory with new settings
  updateTrajectory()
  
  console.log(`Applied shooting preset: ${preset.name}`)
}

// Environmental conditions
const environmentalConditions = ref({
  windSpeed: 0,
  temperature: 70,
  altitude: 0
})

// No automatic watchers - chart generation is on-demand only

onMounted(async () => {
  // Chart initialization is now on-demand only
  // No automatic initialization to improve performance
})

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})

const toggleEnvironmentalControls = () => {
  showEnvironmentalControls.value = !showEnvironmentalControls.value
}

const generateTrajectoryChart = async () => {
  // Ensure we're in the browser environment
  if (typeof window === 'undefined') {
    console.warn('TrajectoryChart: Not in browser environment')
    return
  }

  isLoading.value = true

  try {
    // First, show the chart container so the canvas becomes available
    showChart.value = true
    await nextTick() // Wait for DOM to update
    
    await initializeChartComponent()
    await updateTrajectory()
  } catch (error) {
    console.error('Error generating trajectory chart:', error)
    // Hide chart if initialization failed
    showChart.value = false
  } finally {
    isLoading.value = false
  }
}

const hideChart = () => {
  showChart.value = false
  showEnvironmentalControls.value = false
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
}

const setUnits = (newUnits) => {
  const oldUnits = units.value
  units.value = newUnits
  
  // Convert trajectory settings when switching units
  if (oldUnits !== newUnits) {
    if (newUnits === 'metric') {
      // Convert yards to meters
      trajectorySettings.value.maxRange = Math.round(yardsToMeters(trajectorySettings.value.maxRange))
    } else {
      // Convert meters to yards  
      trajectorySettings.value.maxRange = Math.round(metersToYards(trajectorySettings.value.maxRange))
    }
  }
  
  if (chartInstance.value) {
    updateChartUnits()
  }
}

// Unit conversion functions
const yardsToMeters = (yards) => yards * 0.9144
const metersToYards = (meters) => meters / 0.9144
const inchesToCm = (inches) => inches * 2.54
const cmToInches = (cm) => cm / 2.54

const convertDistance = (distance) => {
  return units.value === 'metric' ? yardsToMeters(distance) : distance
}

const convertHeight = (height) => {
  return units.value === 'metric' ? inchesToCm(height) : height
}

const getDistanceUnit = () => {
  return units.value === 'metric' ? 'm' : 'yd'
}

const getHeightUnit = () => {
  return units.value === 'metric' ? 'cm' : 'in'
}

const updateChartUnits = () => {
  if (!chartInstance.value) return
  
  // Update axis labels
  chartInstance.value.options.scales.x.title.text = `Distance (${getDistanceUnit()})`
  chartInstance.value.options.scales.y.title.text = `Height (${getHeightUnit()})`
  
  // Update data with converted units
  if (chartInstance.value.data.datasets[0].data.length > 0) {
    const originalData = chartInstance.value.data.datasets[0].originalData || chartInstance.value.data.datasets[0].data
    chartInstance.value.data.datasets[0].originalData = originalData
    
    // Convert data points
    chartInstance.value.data.datasets[0].data = originalData.map(point => convertHeight(point))
    chartInstance.value.data.labels = chartInstance.value.data.originalLabels?.map(label => 
      convertDistance(parseFloat(label)).toFixed(1)
    ) || chartInstance.value.data.labels
  }
  
  chartInstance.value.update()
}

const updateChartConfiguration = () => {
  if (!chartInstance.value) return
  
  // Since we're filtering data points by distance interval, use consistent dot styling
  chartInstance.value.data.datasets[0].pointRadius = 5
  chartInstance.value.data.datasets[0].pointBackgroundColor = '#3B82F6'
  
  // Update X-axis configuration including max range
  chartInstance.value.options.scales.x.min = 0
  chartInstance.value.options.scales.x.max = convertDistance(trajectorySettings.value.maxRange)
  chartInstance.value.options.scales.x.ticks.maxTicksLimit = 15 // Allow more labels
  chartInstance.value.options.scales.x.ticks.stepSize = 10 // Try to show every 10 units
  chartInstance.value.options.scales.x.ticks.callback = function(value, index, values) {
    // Show clean distance labels
    const numValue = parseFloat(value)
    if (numValue % 10 === 0 || numValue === 0) {
      return numValue.toFixed(0)
    }
    return numValue.toFixed(0)
  }
  
  console.log(`Updated trajectory chart: interval=${trajectorySettings.value.distanceInterval}, maxRange=${trajectorySettings.value.maxRange}, elevation=${trajectorySettings.value.sightElevation}"`)
}

const initializeChartComponent = async () => {
  console.log('🎯 Initializing chart component...')
  if (!chartCanvas.value) {
    console.warn('❌ Chart canvas not available for trajectory chart')
    return
  }
  console.log('✅ Chart canvas found:', chartCanvas.value)

  try {
    // Initialize Chart.js dynamically
    const ChartClass = await initializeChart()
    if (!ChartClass) {
      console.warn('❌ Chart.js not available')
      return
    }
    console.log('✅ Chart.js loaded successfully')
    
    const ctx = chartCanvas.value.getContext('2d')
    console.log('✅ Canvas context obtained:', ctx)
    
    chartInstance.value = markRaw(new ChartClass(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Arrow Flight Path',
          data: [],
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 5,
          pointHoverRadius: 8,
          pointBackgroundColor: '#3B82F6',
          pointBorderColor: '#FFFFFF',
          pointBorderWidth: 2
        }, {
          label: 'Point of Impact Markers',
          data: [],
          borderColor: 'transparent',
          backgroundColor: 'transparent',
          pointRadius: 8,
          pointHoverRadius: 12,
          pointBackgroundColor: '#EF4444',
          pointBorderColor: '#FFFFFF',
          pointBorderWidth: 3,
          pointStyle: 'crossRot',
          showLine: false,
          order: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: `Distance (${getDistanceUnit()})`,
              color: '#6B7280',
              font: {
                size: 12,
                weight: 'bold'
              }
            },
            grid: {
              color: 'rgba(107, 114, 128, 0.1)'
            },
            type: 'linear',
            position: 'bottom',
            min: 0,
            max: convertDistance(trajectorySettings.value.maxRange),
            ticks: {
              color: '#6B7280',
              stepSize: 10,
              maxTicksLimit: 10,
              callback: function(value, index, values) {
                // Force display every 10 units  
                if (value % 10 === 0) {
                  return value.toFixed(0)
                }
                return ''
              }
            }
          },
          y: {
            title: {
              display: true,
              text: `Height (${getHeightUnit()})`,
              color: '#6B7280',
              font: {
                size: 12,
                weight: 'bold'
              }
            },
            grid: {
              color: 'rgba(107, 114, 128, 0.1)'
            },
            ticks: {
              color: '#6B7280'
            },
            suggestedMin: -50,
            suggestedMax: 20
          }
        },
        plugins: {
          title: {
            display: false
          },
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(17, 24, 39, 0.95)',
            titleColor: '#F9FAFB',
            bodyColor: '#F9FAFB',
            borderColor: '#374151',
            borderWidth: 1,
            cornerRadius: 8,
            padding: 12,
            titleFont: {
              size: 14,
              weight: 'bold'
            },
            bodyFont: {
              size: 12
            },
            callbacks: {
              title: function(context) {
                const distance = parseFloat(context[0].label)
                const distanceUnit = getDistanceUnit()
                const isImpactMarker = context[0].datasetIndex === 1
                const icon = isImpactMarker ? '🎯' : '📍'
                const type = isImpactMarker ? 'Point of Impact' : 'Distance'
                return `${icon} ${type}: ${distance} ${distanceUnit}`
              },
              label: function(context) {
                const height = context.parsed.y
                const heightUnit = getHeightUnit()
                const distance = parseFloat(context.label)
                const isImpactMarker = context.datasetIndex === 1
                
                // Get trajectory data point for this distance if available
                const trajectoryPoint = context.chart.trajectoryData?.find(p => 
                  Math.abs(p.distance_yards - (units.value === 'metric' ? metersToYards(distance) : distance)) < 1
                )
                
                const labels = []
                
                // Special labeling for impact markers
                if (isImpactMarker) {
                  labels.push(`🏹 Arrow Impact Point`)
                  if (height >= 0) {
                    labels.push(`📈 Hits ${height.toFixed(1)}${heightUnit} above target center`)
                    labels.push(`🎯 Aim ${Math.abs(height).toFixed(1)}${heightUnit} low`)
                  } else {
                    labels.push(`📉 Hits ${Math.abs(height).toFixed(1)}${heightUnit} below target center`)
                    labels.push(`🎯 Aim ${Math.abs(height).toFixed(1)}${heightUnit} high`)
                  }
                } else {
                  // Regular trajectory point information
                  if (height >= 0) {
                    labels.push(`📈 Height: +${height.toFixed(1)}${heightUnit} above sight`)
                  } else {
                    labels.push(`📉 Drop: ${Math.abs(height).toFixed(1)}${heightUnit} below sight`)
                  }
                }
                
                // Additional trajectory data if available
                if (trajectoryPoint) {
                  labels.push(`⚡ Velocity: ${trajectoryPoint.velocity_fps} fps`)
                  labels.push(`⏱️ Flight time: ${trajectoryPoint.time.toFixed(2)}s`)
                  
                  if (trajectoryPoint.wind_drift_inches && Math.abs(trajectoryPoint.wind_drift_inches) > 0.1) {
                    const driftUnit = heightUnit
                    const drift = units.value === 'metric' ? inchesToCm(trajectoryPoint.wind_drift_inches) : trajectoryPoint.wind_drift_inches
                    labels.push(`💨 Wind drift: ${drift.toFixed(1)}${driftUnit}`)
                  }
                }
                
                return labels
              },
              afterLabel: function(context) {
                const distance = parseFloat(context.label)
                const distanceUnit = getDistanceUnit()
                const isImpactMarker = context.datasetIndex === 1
                
                const annotations = []
                
                if (isImpactMarker) {
                  // Special annotations for impact markers
                  const commonDistances = units.value === 'metric' ? [18, 27, 37, 46, 55] : [20, 30, 40, 50, 60]
                  const distanceLabels = units.value === 'metric' 
                    ? ['18m (20yd)', '27m (30yd)', '37m (40yd)', '46m (50yd)', '55m (60yd)']
                    : ['20yd', '30yd', '40yd', '50yd', '60yd']
                  
                  const closestIndex = commonDistances.reduce((closest, d, i) => 
                    Math.abs(d - distance) < Math.abs(commonDistances[closest] - distance) ? i : closest, 0
                  )
                  
                  if (Math.abs(commonDistances[closestIndex] - distance) <= 2) {
                    annotations.push(`📏 Standard ${distanceLabels[closestIndex]} target distance`)
                    
                    if (closestIndex === 0) annotations.push('🎯 Typical sight-in distance')
                    if (closestIndex === 2) annotations.push('🦌 Popular hunting distance')
                    if (closestIndex === 4) annotations.push('🏹 Long range challenge')
                  }
                } else {
                  // Convert reference distances based on current units for trajectory points
                  const zeroDistance = units.value === 'metric' ? convertDistance(20).toFixed(0) : '20'
                  const huntingDistance = units.value === 'metric' ? convertDistance(40).toFixed(0) : '40'
                  const extendedDistance = units.value === 'metric' ? convertDistance(60).toFixed(0) : '60'
                  
                  if (Math.abs(distance - parseFloat(zeroDistance)) <= 1) {
                    annotations.push('🎯 Zero Distance')
                  }
                  if (Math.abs(distance - parseFloat(huntingDistance)) <= 2) {
                    annotations.push('🦌 Common Hunting Distance')
                  }
                  if (Math.abs(distance - parseFloat(extendedDistance)) <= 3) {
                    annotations.push('🏹 Extended Range')
                  }
                }
                const interval = trajectorySettings.value.distanceInterval
                const largerInterval = interval * 2
                
                if (distance % largerInterval === 0) {
                  annotations.push('📊 Major Distance Marker')
                } else if (distance % interval === 0) {
                  annotations.push('📍 Distance Marker')
                }
                
                return annotations
              }
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        },
        hover: {
          mode: 'index',
          intersect: false
        },
        elements: {
          point: {
            hoverRadius: 10
          }
        }
    }
  }))
  
  console.log('🎯 Chart.js instance created successfully:', chartInstance.value)
  
  } catch (error) {
    console.error('❌ Error creating Chart.js instance:', error)
    throw error // Re-throw to be caught by the mounted hook
  }
}

const updateTrajectory = async () => {
  if (!chartInstance.value || !props.arrowData || !props.bowConfig) return

  isLoading.value = true

  try {
    // Update chart configuration for new distance intervals
    updateChartConfiguration()
    
    // Use the unified trajectory calculation composable
    const trajectoryData = await calculateTrajectory(
      props.arrowData,        // setupArrow
      props.arrowData?.arrow, // arrow (nested arrow object)
      props.bowConfig,        // bowConfig 
      {
        temperature_f: environmentalConditions.value.temperature,
        wind_speed_mph: environmentalConditions.value.windSpeed,
        altitude_feet: environmentalConditions.value.altitude,
        humidity_percent: 50.0
      },
      {
        shot_angle_degrees: 0.0,
        sight_height_inches: 7.0,
        zero_distance_yards: 20.0,
        max_range_yards: units.value === 'metric' ? metersToYards(trajectorySettings.value.maxRange) : trajectorySettings.value.maxRange
      }
    )

    if (trajectoryData) {
      updateChartData(trajectoryData)
      updateTrajectorySummary(trajectoryData)
    } else {
      // Fallback to simplified trajectory
      console.warn('API calculation failed, using simplified trajectory')
      generateFallbackTrajectory()
    }
  } catch (error) {
    console.error('Failed to calculate trajectory:', error)
    // Show fallback trajectory based on basic ballistics
    generateFallbackTrajectory()
  } finally {
    isLoading.value = false
  }
}

const updateChartData = (trajectoryData) => {
  if (!chartInstance.value || !trajectoryData.trajectory_points) return

  const allPoints = trajectoryData.trajectory_points
  
  // Filter points based on distance interval to control dot density on trajectory line
  const interval = trajectorySettings.value.distanceInterval
  const filteredPoints = allPoints.filter(p => {
    const distance = Math.round(p.distance_yards)
    return distance % interval === 0 || distance === 0 // Always include starting point
  })
  
  // Extend trajectory to show ground impact (where arrow hits ground)
  const lastPoint = allPoints[allPoints.length - 1]
  const groundImpactPoint = allPoints.find(p => p.height_inches <= 0) || lastPoint
  
  // Always include the ground impact point if it's not already in filtered points
  if (groundImpactPoint && !filteredPoints.find(p => Math.abs(p.distance_yards - groundImpactPoint.distance_yards) < 0.5)) {
    filteredPoints.push(groundImpactPoint)
    filteredPoints.sort((a, b) => a.distance_yards - b.distance_yards)
  }

  const originalLabels = filteredPoints.map(p => p.distance_yards.toString())
  const originalHeights = filteredPoints.map(p => 
    p.height_inches - 7.0 + trajectorySettings.value.sightElevation // Adjust for sight height and elevation
  )
  
  console.log(`Sight elevation applied: ${trajectorySettings.value.sightElevation}" - Sample heights:`, originalHeights.slice(0, 3))

  // Store original data for unit conversion
  chartInstance.value.data.originalLabels = originalLabels
  chartInstance.value.data.datasets[0].originalData = originalHeights
  
  // Store ALL trajectory data for tooltips (not just filtered)
  chartInstance.value.trajectoryData = allPoints
  
  // Update point of impact markers
  updatePointOfImpactMarkers(allPoints)

  // Apply current unit conversion
  const convertedLabels = originalLabels.map(label => 
    convertDistance(parseFloat(label)).toFixed(1)
  )
  const convertedHeights = originalHeights.map(height => convertHeight(height))

  chartInstance.value.data.labels = convertedLabels
  chartInstance.value.data.datasets[0].data = convertedHeights
  
  // Adjust Y-axis to show full trajectory including ground impact
  const minHeight = Math.min(...convertedHeights)
  const maxHeight = Math.max(...convertedHeights)
  chartInstance.value.options.scales.y.suggestedMin = Math.min(-30, minHeight - 10)
  chartInstance.value.options.scales.y.suggestedMax = Math.max(20, maxHeight + 10)
  
  // Force update to apply changes
  chartInstance.value.update('none')
}

// Update point of impact markers at common distances
const updatePointOfImpactMarkers = (trajectoryData) => {
  if (!chartInstance.value || !trajectoryData) return
  
  // Common archery distances based on units
  const commonDistances = units.value === 'metric' 
    ? [18, 27, 37, 46, 55] // meters (equivalent to 20, 30, 40, 50, 60 yards)
    : [20, 30, 40, 50, 60] // yards
  
  const impactPoints = []
  const impactLabels = []
  
  commonDistances.forEach(distance => {
    // Find the closest trajectory point to this distance
    const closestPoint = trajectoryData.reduce((closest, point) => {
      const currentDistance = units.value === 'metric' 
        ? point.distance_yards * 0.9144 // Convert yards to meters
        : point.distance_yards
      const targetDiff = Math.abs(currentDistance - distance)
      const closestDiff = Math.abs((units.value === 'metric' 
        ? closest.distance_yards * 0.9144 
        : closest.distance_yards) - distance)
      return targetDiff < closestDiff ? point : closest
    })
    
    if (closestPoint) {
      const adjustedHeight = closestPoint.height_inches - 7.0 + trajectorySettings.value.sightElevation
      const convertedDistance = convertDistance(closestPoint.distance_yards)
      const convertedHeight = convertHeight(adjustedHeight)
      
      // Only add markers that fall within the chart range and are above ground
      if (convertedDistance <= trajectorySettings.value.maxRange && adjustedHeight > -12) {
        impactLabels.push(convertedDistance.toFixed(1))
        impactPoints.push(convertedHeight)
      }
    }
  })
  
  // Update the impact markers dataset
  if (chartInstance.value.data.datasets[1]) {
    chartInstance.value.data.datasets[1].data = impactPoints
    // Create sparse dataset aligned with main trajectory labels
    const sparseData = chartInstance.value.data.labels.map((label, index) => {
      const labelFloat = parseFloat(label)
      const impactIndex = impactLabels.findIndex(impactLabel => 
        Math.abs(parseFloat(impactLabel) - labelFloat) < 0.5
      )
      return impactIndex !== -1 ? impactPoints[impactIndex] : null
    })
    chartInstance.value.data.datasets[1].data = sparseData
  }
}

const updateTrajectorySummary = (trajectoryData) => {
  if (!trajectoryData.trajectory_points) return

  const points = trajectoryData.trajectory_points
  const maxRange = Math.max(...points.map(p => p.distance_yards))
  
  // Apply sight elevation to height calculations for display
  const maxHeight = Math.max(...points.map(p => p.height_inches - 7.0 + trajectorySettings.value.sightElevation))
  
  // Find drop at 40 yards with sight elevation applied for display
  const point40yd = points.find(p => Math.abs(p.distance_yards - 40) <= 2)
  const dropAt40yd = point40yd ? Math.abs(point40yd.height_inches - 7.0 + trajectorySettings.value.sightElevation) : 0

  trajectorySummary.value = {
    maxRange: Math.round(maxRange),
    peakHeight: maxHeight.toFixed(1),
    dropAt40yd: dropAt40yd.toFixed(1)
  }
}

const generateFallbackTrajectory = () => {
  // Generate basic trajectory based on arrow speed estimation
  const speed = estimateArrowSpeed()
  const allPoints = []
  const interval = trajectorySettings.value.distanceInterval
  
  // Generate all points first
  for (let distance = 0; distance <= trajectorySettings.value.maxRange; distance += 1) {
    const time = distance * 3 / speed // Convert yards to feet, then to time
    const drop = -16.1 * time * time // Basic gravity drop (ft)
    const dropInches = drop * 12 + trajectorySettings.value.sightElevation // Convert to inches and add sight elevation
    
    allPoints.push({ distance, height: dropInches })
  }
  
  // Filter points based on distance interval (only show dots at specified intervals)
  const filteredPoints = allPoints.filter(p => {
    return p.distance % interval === 0 || p.distance === 0
  })
  
  // Find ground impact point (where arrow goes below zero)
  const groundImpactPoint = allPoints.find(p => p.height <= -7.0)
  if (groundImpactPoint && !filteredPoints.find(p => p.distance === groundImpactPoint.distance)) {
    filteredPoints.push(groundImpactPoint)
    filteredPoints.sort((a, b) => a.distance - b.distance)
  }
  
  const labels = filteredPoints.map(p => p.distance.toString())
  const points = filteredPoints.map(p => p.height)

  console.log('🎯 Chart Labels Debug:', { 
    labels: labels.slice(0, 10), 
    points: points.slice(0, 10),
    totalPoints: labels.length 
  })

  chartInstance.value.data.labels = labels
  chartInstance.value.data.datasets[0].data = points
  
  // Adjust Y-axis to show full trajectory including ground impact
  const minHeight = Math.min(...points)
  const maxHeight = Math.max(...points)
  chartInstance.value.options.scales.y.suggestedMin = Math.min(-30, minHeight - 10)
  chartInstance.value.options.scales.y.suggestedMax = Math.max(20, maxHeight + 10)
  
  // Update configuration and force re-render
  updateChartConfiguration()
  chartInstance.value.update('none')

  // Basic summary with ground impact distance
  const groundImpactDistance = groundImpactPoint ? groundImpactPoint.distance : trajectorySettings.value.maxRange
  const dropAt40Point = allPoints.find(p => p.distance === 40) || { height: 0 }
  
  trajectorySummary.value = {
    maxRange: groundImpactDistance,
    peakHeight: '2.0',
    dropAt40yd: Math.abs(dropAt40Point.height).toFixed(1)
  }
}

const estimateArrowSpeed = () => {
  // Basic speed estimation
  const drawWeight = props.bowConfig?.drawWeight || 60
  const arrowWeight = props.arrowData?.total_weight || 400
  
  // Simplified speed formula
  const baseSpeed = drawWeight * 3.5 + 180
  const weightFactor = Math.sqrt(350 / arrowWeight)
  
  return Math.max(200, Math.min(350, baseSpeed * weightFactor))
}

// Speed source indicator methods
const getSpeedSourceClass = () => {
  const source = props.arrowData?.speed_source
  if (source === 'chronograph') {
    return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
  } else {
    return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
  }
}

const getSpeedSourceIcon = () => {
  const source = props.arrowData?.speed_source
  if (source === 'chronograph') {
    return 'fas fa-tachometer-alt'
  } else {
    return 'fas fa-calculator'
  }
}

const getSpeedSourceText = () => {
  const source = props.arrowData?.speed_source
  if (source === 'chronograph') {
    return 'Measured Speed'
  } else {
    return 'Estimated Speed'
  }
}

// Trajectory summary unit conversion methods
const getDisplayMaxRange = () => {
  if (!trajectorySummary.value) return 0
  const range = trajectorySummary.value.maxRange
  return units.value === 'metric' ? convertDistance(range).toFixed(1) : Math.round(range)
}

const getDisplayPeakHeight = () => {
  if (!trajectorySummary.value) return '0'
  const height = parseFloat(trajectorySummary.value.peakHeight)
  return units.value === 'metric' ? convertHeight(height).toFixed(1) : trajectorySummary.value.peakHeight
}

const getDisplayDropAt40 = () => {
  if (!trajectorySummary.value) return '0'
  const drop = parseFloat(trajectorySummary.value.dropAt40yd)
  return units.value === 'metric' ? convertHeight(drop).toFixed(1) : trajectorySummary.value.dropAt40yd
}

const getDisplayDropReference = () => {
  const referenceDistance = 40
  return units.value === 'metric' ? convertDistance(referenceDistance).toFixed(0) : referenceDistance
}

// Generate holdover guidance for common shooting distances
const getHoldoverGuidance = () => {
  if (!chartInstance.value?.trajectoryData) return null
  
  const points = chartInstance.value.trajectoryData
  const commonDistances = units.value === 'metric' ? [18, 27, 37, 46, 55] : [20, 30, 40, 50, 60]
  const guidance = []
  
  for (const distance of commonDistances) {
    // Convert metric distances to yards for data lookup
    const lookupDistance = units.value === 'metric' ? metersToYards(distance) : distance
    const point = points.find(p => Math.abs(p.distance_yards - lookupDistance) <= 2)
    
    if (point) {
      // Calculate holdover/holdunder with sight elevation applied
      const drop = -(point.height_inches - 7.0 + trajectorySettings.value.sightElevation)
      const absValue = Math.abs(drop)
      
      let guidanceText = ''
      if (drop > 1) {
        // Need to aim high (holdover)
        const holdover = units.value === 'metric' ? inchesToCm(drop) : drop
        guidanceText = `Aim ${holdover.toFixed(1)}${getHeightUnit()} high`
      } else if (drop < -1) {
        // Need to aim low (holdunder)
        const holdunder = units.value === 'metric' ? inchesToCm(absValue) : absValue
        guidanceText = `Aim ${holdunder.toFixed(1)}${getHeightUnit()} low`
      } else {
        // Close to point-of-aim
        guidanceText = 'Aim center'
      }
      
      guidance.push({
        distance: distance,
        guidance: guidanceText
      })
    }
  }
  
  return guidance.length > 0 ? guidance : null
}
</script>

<style scoped>
.trajectory-chart-container {
  position: relative;
}

.chart-wrapper {
  background: transparent;
}

/* Custom range slider styling */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
  border: 2px solid #FFFFFF;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

input[type="range"]::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
  border: 2px solid #FFFFFF;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.dark input[type="range"]::-webkit-slider-thumb {
  border-color: #374151;
}

.dark input[type="range"]::-moz-range-thumb {
  border-color: #374151;
}
</style>