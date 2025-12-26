<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Component Library</h2>
      <p class="text-gray-600 dark:text-gray-400">
        Complete showcase of all UI components used throughout the Archery Tools application.
      </p>
    </div>

    <!-- Buttons -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Buttons</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Flexible button component with multiple variants, sizes, and states.
      </p>
      
      <div class="space-y-6">
        <!-- Button Variants -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Variants</h4>
          <div class="flex flex-wrap gap-4">
            <CustomButton variant="filled">Filled Button</CustomButton>
            <CustomButton variant="outlined">Outlined Button</CustomButton>
            <CustomButton variant="text">Text Button</CustomButton>
          </div>
        </div>

        <!-- Button Sizes -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Sizes</h4>
          <div class="flex flex-wrap gap-4 items-center">
            <CustomButton size="small">Small</CustomButton>
            <CustomButton size="medium">Medium</CustomButton>
            <CustomButton size="large">Large</CustomButton>
          </div>
        </div>

        <!-- Button States -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">States</h4>
          <div class="flex flex-wrap gap-4">
            <CustomButton>Normal</CustomButton>
            <CustomButton disabled>Disabled</CustomButton>
            <CustomButton icon="fas fa-heart">With Icon</CustomButton>
          </div>
        </div>

        <!-- Specialized Buttons -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Specialized</h4>
          <div class="flex flex-wrap gap-4">
            <button class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">Success</button>
            <button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">Error</button>
            <button class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700">Warning</button>
            <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 dark:bg-purple-600 dark:hover:bg-purple-700">Primary</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Form Controls -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Form Controls</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Comprehensive form elements including inputs, sliders, checkboxes, and other interactive controls.
      </p>
      
      <div class="space-y-8">
        <!-- Text Inputs -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Text Inputs</h4>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Standard Input</label>
                <input type="text" placeholder="Enter text..." class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Number Input</label>
                <input type="number" placeholder="125" min="0" max="500" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">With Icon</label>
                <div class="relative">
                  <input type="text" placeholder="Search..." class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400">
                  <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- Select Dropdowns -->
          <div>
            <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Select Dropdowns</h4>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Standard Select</label>
                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100">
                  <option>Compound Bow</option>
                  <option>Recurve Bow</option>
                  <option>Traditional Bow</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Multi Select</label>
                <select multiple size="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100">
                  <option>Hunting</option>
                  <option>Target</option>
                  <option>3D Archery</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Sliders and Range Inputs -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-4">Sliders & Range Controls</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Draw Weight: <span class="text-blue-600 dark:text-purple-400">{{ drawWeight }}lbs</span>
                </label>
                <input 
                  type="range" 
                  v-model="drawWeight"
                  min="20" 
                  max="80" 
                  class="slider w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                >
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>20lbs</span>
                  <span>80lbs</span>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Draw Length: <span class="text-green-600 dark:text-green-400">{{ drawLength }}"</span>
                </label>
                <input 
                  type="range" 
                  v-model="drawLength"
                  min="24" 
                  max="32" 
                  step="0.25"
                  class="slider w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                >
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>24"</span>
                  <span>32"</span>
                </div>
              </div>
            </div>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Point Weight: <span class="text-purple-600 dark:text-purple-400">{{ pointWeight }}gr</span>
                </label>
                <input 
                  type="range" 
                  v-model="pointWeight"
                  min="75" 
                  max="200" 
                  step="5"
                  class="slider w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                >
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>75gr</span>
                  <span>200gr</span>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Arrow Length: <span class="text-orange-600 dark:text-orange-400">{{ arrowLength }}"</span>
                </label>
                <input 
                  type="range" 
                  v-model="arrowLength"
                  min="26" 
                  max="32" 
                  step="0.5"
                  class="slider w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                >
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>26"</span>
                  <span>32"</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Checkboxes and Radio Buttons -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Checkboxes</h4>
            <div class="space-y-3">
              <label class="flex items-center">
                <input type="checkbox" v-model="features.rest" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <span class="ml-2 text-sm text-gray-900 dark:text-gray-300">Drop-away Rest</span>
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="features.stabilizer" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <span class="ml-2 text-sm text-gray-900 dark:text-gray-300">Stabilizer</span>
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="features.sight" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <span class="ml-2 text-sm text-gray-900 dark:text-gray-300">Multi-pin Sight</span>
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="features.peep" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <span class="ml-2 text-sm text-gray-900 dark:text-gray-300">Peep Sight</span>
              </label>
            </div>
          </div>

          <div>
            <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Radio Buttons</h4>
            <div class="space-y-3">
              <label class="flex items-center">
                <input type="radio" v-model="arrowType" value="hunting" name="arrowType" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <span class="ml-2 text-sm text-gray-900 dark:text-gray-300">Hunting Arrow</span>
              </label>
              <label class="flex items-center">
                <input type="radio" v-model="arrowType" value="target" name="arrowType" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <span class="ml-2 text-sm text-gray-900 dark:text-gray-300">Target Arrow</span>
              </label>
              <label class="flex items-center">
                <input type="radio" v-model="arrowType" value="3d" name="arrowType" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <span class="ml-2 text-sm text-gray-900 dark:text-gray-300">3D Arrow</span>
              </label>
              <label class="flex items-center">
                <input type="radio" v-model="arrowType" value="field" name="arrowType" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <span class="ml-2 text-sm text-gray-900 dark:text-gray-300">Field Arrow</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Toggle Switches -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-4">Toggle Switches</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-900 dark:text-gray-300">Enable Notifications</span>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="toggles.notifications" class="sr-only peer">
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-900 dark:text-gray-300">Dark Mode</span>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="toggles.darkMode" class="sr-only peer">
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-900 dark:text-gray-300">Auto Calculate</span>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="toggles.autoCalc" class="sr-only peer">
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>

            <!-- Form Summary -->
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Current Form Values</h5>
              <div class="text-sm space-y-1">
                <div class="flex justify-between">
                  <span class="text-gray-600 dark:text-gray-400">Draw Weight:</span>
                  <span class="text-gray-900 dark:text-gray-100">{{ drawWeight }}lbs</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600 dark:text-gray-400">Draw Length:</span>
                  <span class="text-gray-900 dark:text-gray-100">{{ drawLength }}"</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600 dark:text-gray-400">Arrow Type:</span>
                  <span class="text-gray-900 dark:text-gray-100 capitalize">{{ arrowType }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600 dark:text-gray-400">Features:</span>
                  <span class="text-gray-900 dark:text-gray-100">{{ activeFeatures }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Textarea and Special Inputs -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Text Areas</h4>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Setup Notes</label>
                <textarea 
                  rows="4" 
                  placeholder="Add notes about your bow setup..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400 resize-none"
                ></textarea>
              </div>
            </div>
          </div>

          <div>
            <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Special Inputs</h4>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tuning Date</label>
                <input type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Session Time</label>
                <input type="time" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Arrow Color</label>
                <input type="color" value="#3B82F6" class="h-10 w-20 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:border-gray-600">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Cards -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Cards</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Various card layouts and styles used for content organization.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Basic Card -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
          <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Basic Card</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">Simple card with border and shadow.</p>
        </div>

        <!-- Info Card -->
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <div class="flex items-center mb-2">
            <i class="fas fa-info-circle text-blue-600 dark:text-blue-400 mr-2"></i>
            <h4 class="font-semibold text-blue-800 dark:text-blue-200">Info Card</h4>
          </div>
          <p class="text-sm text-blue-700 dark:text-blue-300">Information or notice content.</p>
        </div>

        <!-- Success Card -->
        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
          <div class="flex items-center mb-2">
            <i class="fas fa-check-circle text-green-600 dark:text-green-400 mr-2"></i>
            <h4 class="font-semibold text-green-800 dark:text-green-200">Success Card</h4>
          </div>
          <p class="text-sm text-green-700 dark:text-green-300">Success or confirmation message.</p>
        </div>

        <!-- Glass Card -->
        <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg p-4 border border-white/20 dark:border-gray-700/30">
          <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Glass Card</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">Card with glass morphism effect.</p>
        </div>

        <!-- Gradient Card -->
        <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Gradient Card</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">Card with gradient background.</p>
        </div>

        <!-- Elevated Card -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-lg border border-gray-200 dark:border-gray-700">
          <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Elevated Card</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">Card with enhanced shadow.</p>
        </div>
      </div>
    </div>

    <!-- Navigation Components -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Navigation</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Navigation patterns including breadcrumbs, tabs, and mobile navigation.
      </p>
      
      <div class="space-y-6">
        <!-- Breadcrumbs -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Breadcrumbs</h4>
          <nav class="flex items-center space-x-2 text-sm">
            <a href="#" class="text-blue-600 dark:text-purple-400 hover:underline">Home</a>
            <i class="fas fa-chevron-right text-gray-400"></i>
            <a href="#" class="text-blue-600 dark:text-purple-400 hover:underline">Category</a>
            <i class="fas fa-chevron-right text-gray-400"></i>
            <span class="text-gray-600 dark:text-gray-400">Current Page</span>
          </nav>
        </div>

        <!-- Tabs -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Tabs</h4>
          <nav class="flex space-x-6 border-b border-gray-200 dark:border-gray-700">
            <button class="py-2 px-1 border-b-2 border-blue-500 text-blue-600 dark:border-purple-400 dark:text-purple-400 font-medium text-sm">
              Active Tab
            </button>
            <button class="py-2 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm">
              Tab Two
            </button>
            <button class="py-2 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm">
              Tab Three
            </button>
          </nav>
        </div>

        <!-- Pagination -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Pagination</h4>
          <nav class="flex items-center justify-center space-x-2">
            <button class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700" disabled>
              Previous
            </button>
            <button class="px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg dark:bg-purple-600">
              1
            </button>
            <button class="px-3 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:hover:bg-gray-700">
              2
            </button>
            <button class="px-3 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:hover:bg-gray-700">
              3
            </button>
            <button class="px-3 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:hover:bg-gray-700">
              Next
            </button>
          </nav>
        </div>
      </div>
    </div>

    <!-- Feedback Components -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Feedback & Status</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Components for showing status, loading states, and user feedback.
      </p>
      
      <div class="space-y-6">
        <!-- Loading States -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Loading States</h4>
          <div class="flex flex-wrap gap-4 items-center">
            <div class="flex items-center">
              <div class="animate-spin rounded-full h-6 w-6 border-2 border-blue-500 border-t-transparent"></div>
              <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading...</span>
            </div>
            <div class="w-32 bg-gray-200 rounded-full h-2 dark:bg-gray-700">
              <div class="bg-blue-600 h-2 rounded-full dark:bg-purple-600" style="width: 45%"></div>
            </div>
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce dark:bg-purple-600"></div>
              <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce dark:bg-purple-600" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce dark:bg-purple-600" style="animation-delay: 0.2s"></div>
            </div>
          </div>
        </div>

        <!-- Badges -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Badges</h4>
          <div class="flex flex-wrap gap-2">
            <span class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full dark:bg-blue-900/30 dark:text-blue-300">Primary</span>
            <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full dark:bg-green-900/30 dark:text-green-300">Success</span>
            <span class="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full dark:bg-yellow-900/30 dark:text-yellow-300">Warning</span>
            <span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full dark:bg-red-900/30 dark:text-red-300">Error</span>
            <span class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full dark:bg-gray-900/30 dark:text-gray-300">Neutral</span>
          </div>
        </div>

        <!-- Alerts -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Alerts</h4>
          <div class="space-y-3">
            <div class="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded-lg dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-200">
              <div class="flex items-center">
                <i class="fas fa-info-circle mr-3"></i>
                <div class="text-sm">This is an informational alert message.</div>
              </div>
            </div>
            <div class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg dark:bg-green-900/20 dark:border-green-800 dark:text-green-200">
              <div class="flex items-center">
                <i class="fas fa-check-circle mr-3"></i>
                <div class="text-sm">This is a success alert message.</div>
              </div>
            </div>
            <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-200">
              <div class="flex items-center">
                <i class="fas fa-exclamation-triangle mr-3"></i>
                <div class="text-sm">This is a warning alert message.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Components -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Performance Components</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Specialized components for displaying archery performance data and metrics.
      </p>
      
      <div class="space-y-6">
        <!-- Performance Metrics -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Performance Metrics</h4>
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- Speed -->
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <div class="text-lg font-bold text-blue-600 dark:text-blue-400 mb-1">285.4 fps</div>
              <div class="text-sm text-blue-800 dark:text-blue-200 font-medium">Speed</div>
              <div class="text-xs text-blue-600 dark:text-blue-400 mt-1">Fast</div>
            </div>
            
            <!-- Kinetic Energy -->
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
              <div class="text-lg font-bold text-green-600 dark:text-green-400 mb-1">64.2 ft·lbs</div>
              <div class="text-sm text-green-800 dark:text-green-200 font-medium">KE @40yd</div>
              <div class="text-xs text-green-600 dark:text-green-400 mt-1">Good (Deer)</div>
            </div>

            <!-- FOC -->
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
              <div class="text-lg font-bold text-purple-600 dark:text-purple-400 mb-1">12.8%</div>
              <div class="text-sm text-purple-800 dark:text-purple-200 font-medium">FOC</div>
              <div class="text-xs text-purple-600 dark:text-purple-400 mt-1">Good (Target)</div>
            </div>

            <!-- Performance Score -->
            <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
              <div class="text-lg font-bold text-green-600 dark:text-green-400 mb-1">87/100</div>
              <div class="text-sm text-orange-800 dark:text-orange-200 font-medium">Score</div>
              <div class="text-xs text-orange-600 dark:text-orange-400 mt-1">Excellent</div>
            </div>
          </div>
        </div>

        <!-- Data Tables -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">Data Tables</h4>
          <div class="overflow-x-auto">
            <table class="min-w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Arrow</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Spine</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Speed</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Score</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">Easton ACE</td>
                  <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">400</td>
                  <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">285 fps</td>
                  <td class="px-4 py-3 text-sm"><span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full dark:bg-green-900/30 dark:text-green-300">87</span></td>
                </tr>
                <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">Gold Tip Pierce</td>
                  <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">340</td>
                  <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">292 fps</td>
                  <td class="px-4 py-3 text-sm"><span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full dark:bg-blue-900/30 dark:text-blue-300">82</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import CustomButton from '~/components/CustomButton.vue'

// Reactive form data for interactive sliders and controls
const drawWeight = ref(50)
const drawLength = ref(28)
const pointWeight = ref(125)
const arrowLength = ref(29)

// Form controls data
const features = ref({
  rest: true,
  stabilizer: false,
  sight: true,
  peep: true
})

const arrowType = ref('hunting')

const toggles = ref({
  notifications: false,
  darkMode: false,
  autoCalc: true
})

// Computed property to show active features
const activeFeatures = computed(() => {
  const active = Object.keys(features.value).filter(key => features.value[key])
  return active.length > 0 ? active.join(', ') : 'None'
})
</script>

<style scoped>
/* Custom slider styling - Cross-browser compatible */
.slider {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  width: 100%;
  height: 0.5rem;
  background: transparent;
  cursor: pointer;
  border: none;
  outline: none;
}

/* WebKit browsers (Chrome, Safari, Edge) */
.slider::-webkit-slider-track {
  background: #d1d5db;
  border-radius: 0.375rem;
  height: 0.5rem;
  border: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  background: #3b82f6;
  border: none;
  border-radius: 50%;
  height: 1.25rem;
  width: 1.25rem;
  margin-top: -0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.slider::-webkit-slider-thumb:active {
  transform: scale(1.05);
}

/* Firefox */
.slider::-moz-range-track {
  background: #d1d5db;
  border-radius: 0.375rem;
  height: 0.5rem;
  border: none;
  outline: none;
}

.slider::-moz-range-thumb {
  background: #3b82f6;
  border: none;
  border-radius: 50%;
  height: 1.25rem;
  width: 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  /* Remove default Firefox styling */
  -moz-appearance: none;
  appearance: none;
}

.slider::-moz-range-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.slider::-moz-range-thumb:active {
  transform: scale(1.05);
}

/* Firefox focus outline removal */
.slider::-moz-focus-outer {
  border: 0;
}

/* Internet Explorer/Edge legacy support */
.slider::-ms-track {
  background: #d1d5db;
  border-radius: 0.375rem;
  height: 0.5rem;
  border: none;
  color: transparent;
}

.slider::-ms-thumb {
  background: #3b82f6;
  border: none;
  border-radius: 50%;
  height: 1.25rem;
  width: 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.slider::-ms-fill-lower {
  background: transparent;
}

.slider::-ms-fill-upper {
  background: transparent;
}

/* Dark mode styling */
.dark .slider::-webkit-slider-track {
  background: #374151;
}

.dark .slider::-webkit-slider-thumb {
  background: #8b5cf6;
}

.dark .slider::-webkit-slider-thumb:hover {
  background: #7c3aed;
}

.dark .slider::-moz-range-track {
  background: #374151;
}

.dark .slider::-moz-range-thumb {
  background: #8b5cf6;
}

.dark .slider::-moz-range-thumb:hover {
  background: #7c3aed;
}

.dark .slider::-ms-track {
  background: #374151;
}

.dark .slider::-ms-thumb {
  background: #8b5cf6;
}

/* Focus states for accessibility */
.slider:focus {
  outline: none;
}

.slider:focus::-webkit-slider-thumb {
  box-shadow: 0 0 0 2px #3b82f6, 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.slider:focus::-moz-range-thumb {
  box-shadow: 0 0 0 2px #3b82f6, 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.dark .slider:focus::-webkit-slider-thumb {
  box-shadow: 0 0 0 2px #8b5cf6, 0 0 0 4px rgba(139, 92, 246, 0.2);
}

.dark .slider:focus::-moz-range-thumb {
  box-shadow: 0 0 0 2px #8b5cf6, 0 0 0 4px rgba(139, 92, 246, 0.2);
}

/* Fallback for browsers that don't support CSS Grid */
@supports not (display: grid) {
  .grid {
    display: flex;
    flex-wrap: wrap;
  }
  
  .grid > * {
    flex: 1 0 auto;
    min-width: 250px;
    margin: 0.5rem;
  }
}

/* Ensure proper box-sizing */
*, *::before, *::after {
  box-sizing: border-box;
}
</style>