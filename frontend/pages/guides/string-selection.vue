<template>
  <div>
    <!-- Breadcrumb Navigation -->
    <nav class="mb-6">
      <ol class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
        <li>
          <NuxtLink to="/guides" class="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            Guides
          </NuxtLink>
        </li>
        <li class="flex items-center">
          <i class="fas fa-chevron-right mx-2"></i>
          <span class="text-gray-900 dark:text-gray-100">Recurve String Selection</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-red-100 dark:bg-red-900/30 rounded-xl mr-4">
          <i class="fas fa-grip-lines text-red-600 dark:text-red-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Recurve String Selection Guide</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">Choose the perfect bowstring length and material for your recurve bow with our comprehensive guide and calculator</p>
        </div>
      </div>
      
      <!-- Guide Info -->
      <div class="flex flex-wrap gap-4 text-sm">
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-clock mr-2"></i>
          14 min read
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-layer-group mr-2"></i>
          Beginner to Advanced
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-tools mr-2"></i>
          Equipment Setup
        </span>
      </div>
    </div>

    <!-- String Length Calculator -->
    <div class="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 rounded-xl p-6 mb-8 border border-red-200 dark:border-red-800">
      <h2 class="text-2xl font-bold text-red-900 dark:text-red-100 mb-4">
        <i class="fas fa-calculator mr-3"></i>
        String Length Calculator
      </h2>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Input Section -->
        <div class="space-y-4">
          <div>
            <label for="bowLength" class="block text-sm font-medium text-red-900 dark:text-red-100 mb-2">
              Bow Length (inches)
            </label>
            <input
              id="bowLength"
              v-model.number="calculator.bowLength"
              type="number"
              min="48"
              max="70"
              step="1"
              class="w-full px-4 py-2 border border-red-300 dark:border-red-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-red-500 focus:border-red-500"
              placeholder="e.g., 68"
            />
            <p class="text-xs text-red-700 dark:text-red-300 mt-1">
              Typical range: 48" to 70"
            </p>
          </div>

          <div>
            <label for="stringType" class="block text-sm font-medium text-red-900 dark:text-red-100 mb-2">
              String Type
            </label>
            <select
              id="stringType"
              v-model="calculator.stringType"
              class="w-full px-4 py-2 border border-red-300 dark:border-red-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-red-500 focus:border-red-500"
            >
              <option value="flemish">Flemish Twist</option>
              <option value="endless">Endless Loop</option>
            </select>
          </div>

          <div>
            <label for="bracingHeight" class="block text-sm font-medium text-red-900 dark:text-red-100 mb-2">
              Desired Bracing Height (inches)
            </label>
            <input
              id="bracingHeight"
              v-model.number="calculator.bracingHeight"
              type="number"
              min="6"
              max="10"
              step="0.25"
              class="w-full px-4 py-2 border border-red-300 dark:border-red-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-red-500 focus:border-red-500"
              placeholder="e.g., 8.5"
            />
            <p class="text-xs text-red-700 dark:text-red-300 mt-1">
              Typical range: 6" to 10" (manufacturer recommended)
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-red-900 dark:text-red-100 mb-2">
              Material
            </label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="calculator.material"
                  type="radio"
                  value="dacron"
                  class="w-4 h-4 text-red-600 bg-gray-100 border-gray-300 focus:ring-red-500 dark:focus:ring-red-600 dark:bg-gray-700 dark:border-gray-600"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Dacron (B-50)</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="calculator.material"
                  type="radio"
                  value="fastflight"
                  class="w-4 h-4 text-red-600 bg-gray-100 border-gray-300 focus:ring-red-500 dark:focus:ring-red-600 dark:bg-gray-700 dark:border-gray-600"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Fast Flight (B-55)</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="calculator.material"
                  type="radio"
                  value="dyneema"
                  class="w-4 h-4 text-red-600 bg-gray-100 border-gray-300 focus:ring-red-500 dark:focus:ring-red-600 dark:bg-gray-700 dark:border-gray-600"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Dyneema (B-55/D97)</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Results Section -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-red-200 dark:border-red-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            <i class="fas fa-chart-line mr-2"></i>
            Calculated Results
          </h3>
          
          <div class="space-y-4">
            <div class="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <div class="text-lg font-bold text-red-900 dark:text-red-100">
                {{ calculatedStringLength }}"
              </div>
              <div class="text-sm text-red-700 dark:text-red-300">
                Recommended String Length
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                  AMO Length
                </div>
                <div class="text-lg font-bold text-gray-700 dark:text-gray-300">
                  {{ calculator.bowLength }}"
                </div>
              </div>
              
              <div class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                  String Type
                </div>
                <div class="text-lg font-bold text-gray-700 dark:text-gray-300">
                  {{ stringTypeDisplay }}
                </div>
              </div>
            </div>

            <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <h4 class="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">
                <i class="fas fa-info-circle mr-1"></i>
                Material Properties
              </h4>
              <div class="text-xs text-blue-800 dark:text-blue-200">
                {{ materialProperties }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Table of Contents -->
    <div class="bg-red-50 dark:bg-red-900/20 rounded-xl p-6 mb-8 border border-red-200 dark:border-red-800">
      <h2 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#string-basics" class="text-red-700 dark:text-red-300 hover:text-red-800 dark:hover:text-red-200 transition-colors">1. String Basics</a>
        <a href="#materials" class="text-red-700 dark:text-red-300 hover:text-red-800 dark:hover:text-red-200 transition-colors">2. String Materials</a>
        <a href="#length-formula" class="text-red-700 dark:text-red-300 hover:text-red-800 dark:hover:text-red-200 transition-colors">3. Length Calculation</a>
        <a href="#construction" class="text-red-700 dark:text-red-300 hover:text-red-800 dark:hover:text-red-200 transition-colors">4. String Construction</a>
        <a href="#maintenance" class="text-red-700 dark:text-red-300 hover:text-red-800 dark:hover:text-red-200 transition-colors">5. Maintenance & Care</a>
        <a href="#troubleshooting" class="text-red-700 dark:text-red-300 hover:text-red-800 dark:hover:text-red-200 transition-colors">6. Troubleshooting</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- String Basics -->
      <section id="string-basics" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-graduation-cap text-blue-500 mr-3"></i>
          String Basics
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            The bowstring is a critical component that directly affects performance, accuracy, and bow longevity. 
            Understanding string selection principles ensures optimal shooting experience.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                <i class="fas fa-info-circle mr-2"></i>
                Key Concepts
              </h3>
              <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                <li>• <strong>AMO Length:</strong> Standardized bow measurement</li>
                <li>• <strong>Bracing Height:</strong> Distance from grip to string</li>
                <li>• <strong>String Length:</strong> Actual string measurement</li>
                <li>• <strong>Nocking Point:</strong> Arrow attachment location</li>
              </ul>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                <i class="fas fa-check-circle mr-2"></i>
                Why String Selection Matters
              </h3>
              <ul class="text-sm text-green-800 dark:text-green-200 space-y-2">
                <li>• Proper bracing height for optimal performance</li>
                <li>• Consistent arrow nocking and release</li>
                <li>• Bow limb protection and longevity</li>
                <li>• Improved accuracy and arrow speed</li>
              </ul>
            </div>
          </div>

          <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <h4 class="font-semibold text-amber-900 dark:text-amber-100 mb-2">
              <i class="fas fa-exclamation-triangle mr-2"></i>
              Critical Formula
            </h4>
            <div class="text-center">
              <div class="text-lg font-mono bg-white dark:bg-gray-800 p-3 rounded border inline-block">
                <strong>String Length = AMO Bow Length - 3 inches</strong>
              </div>
            </div>
            <p class="text-sm text-amber-800 dark:text-amber-200 mt-3 text-center">
              This is the standard AMO formula used by most bow manufacturers for recurve bows.
            </p>
          </div>
        </div>
      </section>

      <!-- String Materials -->
      <section id="materials" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-flask text-purple-500 mr-3"></i>
          String Materials
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            String material significantly affects performance, durability, and bow compatibility. 
            Each material has specific characteristics and applications.
          </p>

          <div class="space-y-6">
            <!-- Dacron -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div class="flex items-center mb-3">
                <div class="w-4 h-4 bg-green-500 rounded mr-3"></div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Dacron (B-50)</h3>
                <span class="ml-auto px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 text-xs rounded">
                  Beginner Friendly
                </span>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Advantages</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Forgiving stretch properties</li>
                    <li>• Compatible with all bow types</li>
                    <li>• Quieter shooting</li>
                    <li>• Easy to maintain</li>
                    <li>• Cost-effective</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Disadvantages</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Lower arrow speeds</li>
                    <li>• More string stretch</li>
                    <li>• Thicker diameter</li>
                    <li>• More affected by weather</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Best For</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Traditional wooden bows</li>
                    <li>• Beginner archers</li>
                    <li>• Vintage equipment</li>
                    <li>• Casual target shooting</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Fast Flight -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div class="flex items-center mb-3">
                <div class="w-4 h-4 bg-blue-500 rounded mr-3"></div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Fast Flight (B-55)</h3>
                <span class="ml-auto px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-xs rounded">
                  Performance
                </span>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Advantages</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Higher arrow speeds</li>
                    <li>• Minimal stretch</li>
                    <li>• Thinner diameter</li>
                    <li>• Weather resistant</li>
                    <li>• Consistent performance</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Disadvantages</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Requires reinforced tips</li>
                    <li>• Less forgiving</li>
                    <li>• More expensive</li>
                    <li>• Can damage older bows</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Best For</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Modern recurve bows</li>
                    <li>• Competition shooting</li>
                    <li>• Advanced archers</li>
                    <li>• Speed-critical applications</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Dyneema -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div class="flex items-center mb-3">
                <div class="w-4 h-4 bg-purple-500 rounded mr-3"></div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Dyneema (D97/B-55)</h3>
                <span class="ml-auto px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 text-xs rounded">
                  Premium
                </span>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Advantages</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Highest performance</li>
                    <li>• Virtually no stretch</li>
                    <li>• Extremely durable</li>
                    <li>• Thin diameter</li>
                    <li>• Temperature stable</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Disadvantages</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Most expensive</li>
                    <li>• Requires proper bow compatibility</li>
                    <li>• Less forgiving</li>
                    <li>• Specialized serving required</li>
                  </ul>
                </div>
                
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Best For</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Olympic-level competition</li>
                    <li>• Professional archers</li>
                    <li>• High-end equipment</li>
                    <li>• Maximum performance needs</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Length Calculation -->
      <section id="length-formula" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-calculator text-green-500 mr-3"></i>
          Length Calculation Methods
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            The AMO (Archery Manufacturers Organization) standard provides a simple and reliable method 
            for calculating recurve bowstring length. This industry standard ensures consistency across manufacturers.
          </p>

          <div class="space-y-6">
            <!-- AMO Standard Formula -->
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
              <h3 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
                <i class="fas fa-formula mr-2"></i>
                AMO Standard Formula
              </h3>
              
              <div class="bg-white dark:bg-gray-800 p-4 rounded border text-center mb-4">
                <div class="text-xl font-mono font-bold text-gray-900 dark:text-gray-100">
                  String Length = AMO Bow Length - 3 inches
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">Example Calculations</h4>
                  <div class="space-y-2">
                    <div class="bg-white dark:bg-gray-800 p-2 rounded text-sm font-mono">
                      68" bow = <strong>65" string</strong>
                    </div>
                    <div class="bg-white dark:bg-gray-800 p-2 rounded text-sm font-mono">
                      66" bow = <strong>63" string</strong>
                    </div>
                    <div class="bg-white dark:bg-gray-800 p-2 rounded text-sm font-mono">
                      70" bow = <strong>67" string</strong>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">String Type Notes</h4>
                  <div class="space-y-2 text-sm text-green-800 dark:text-green-200">
                    <p>• <strong>Flemish Twist:</strong> Use standard AMO calculation</p>
                    <p>• <strong>Endless Loop:</strong> Use standard AMO calculation</p>
                    <p>• <strong>Fine-tuning:</strong> Adjust with string twists (±1/2")</p>
                    <p>• <strong>Range:</strong> Most recurve strings are 3-4" shorter than bow</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step-by-Step Guide -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Step-by-Step Calculation
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-3">
                  <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      1
                    </div>
                    <div>
                      <h4 class="font-medium text-gray-900 dark:text-gray-100">Find AMO Bow Length</h4>
                      <p class="text-sm text-gray-700 dark:text-gray-300">
                        Check bow markings, manufacturer specs, or measure from string groove to string groove following the limb curve. Common lengths: 62", 66", 68", 70"
                      </p>
                    </div>
                  </div>

                  <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      2
                    </div>
                    <div>
                      <h4 class="font-medium text-gray-900 dark:text-gray-100">Apply AMO Formula</h4>
                      <p class="text-sm text-gray-700 dark:text-gray-300">
                        Simply subtract 3 inches from your bow's AMO length. Example: 68" bow = 65" string
                      </p>
                    </div>
                  </div>
                </div>

                <div class="space-y-3">
                  <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      3
                    </div>
                    <div>
                      <h4 class="font-medium text-gray-900 dark:text-gray-100">Select String Type</h4>
                      <p class="text-sm text-gray-700 dark:text-gray-300">
                        Choose Flemish twist or endless loop based on preference. Both use the same length calculation.
                      </p>
                    </div>
                  </div>

                  <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      4
                    </div>
                    <div>
                      <h4 class="font-medium text-gray-900 dark:text-gray-100">Fine-Tune with Twists</h4>
                      <p class="text-sm text-gray-700 dark:text-gray-300">
                        Adjust bracing height by adding or removing string twists (±1/2" range)
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- String Construction -->
      <section id="construction" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-cogs text-orange-500 mr-3"></i>
          String Construction Types
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Understanding string construction affects both performance and the length calculation. 
            Each type has specific characteristics and applications.
          </p>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Flemish Twist -->
            <div class="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-4">
                <i class="fas fa-repeat mr-2"></i>
                Flemish Twist Construction
              </h3>
              
              <div class="space-y-4">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Construction Method</h4>
                  <p class="text-sm text-gray-700 dark:text-gray-300">
                    Individual strands twisted together to form loops at each end. 
                    Traditional method providing natural string elasticity.
                  </p>
                </div>

                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Advantages</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Adjustable string length by twisting</li>
                    <li>• Traditional appearance</li>
                    <li>• No serving required at loops</li>
                    <li>• Can be field-repaired</li>
                    <li>• Naturally dampens vibration</li>
                  </ul>
                </div>

                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Length Calculation</h4>
                  <div class="bg-orange-50 dark:bg-orange-900/20 p-3 rounded">
                    <p class="text-sm text-orange-800 dark:text-orange-200">
                      <strong>Add 3-4 inches</strong> to basic calculation to account for twist and loop formation.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Endless Loop -->
            <div class="border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
                <i class="fas fa-circle mr-2"></i>
                Endless Loop Construction
              </h3>
              
              <div class="space-y-4">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Construction Method</h4>
                  <p class="text-sm text-gray-700 dark:text-gray-300">
                    Continuous loop of material with served loops at each end. 
                    Modern method providing consistent performance.
                  </p>
                </div>

                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Advantages</h4>
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• Consistent string performance</li>
                    <li>• Thinner profile</li>
                    <li>• More uniform strand distribution</li>
                    <li>• Better for high-performance materials</li>
                    <li>• Precise length control</li>
                  </ul>
                </div>

                <div>
                  <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-2">Length Calculation</h4>
                  <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded">
                    <p class="text-sm text-blue-800 dark:text-blue-200">
                      <strong>Add 0-1 inches</strong> to basic calculation. More precise length control required.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Maintenance & Care -->
      <section id="maintenance" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-wrench text-purple-500 mr-3"></i>
          String Maintenance & Care
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Proper string maintenance extends life, maintains performance, and ensures safety. 
            Regular care prevents failures and maintains accuracy.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Regular Maintenance</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">Daily Care</h4>
                  <ul class="text-sm text-purple-800 dark:text-purple-200 space-y-1">
                    <li>• Inspect for fraying or damage</li>
                    <li>• Check serving condition</li>
                    <li>• Clean with soft cloth</li>
                    <li>• Apply string wax as needed</li>
                  </ul>
                </div>

                <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-indigo-900 dark:text-indigo-100 mb-2">Weekly Care</h4>
                  <ul class="text-sm text-indigo-800 dark:text-indigo-200 space-y-1">
                    <li>• Apply bowstring wax</li>
                    <li>• Check nocking point position</li>
                    <li>• Inspect loop condition</li>
                    <li>• Monitor string stretch</li>
                  </ul>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Replacement Indicators</h3>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
                  <h4 class="font-medium text-red-900 dark:text-red-100 mb-2">Replace Immediately</h4>
                  <ul class="text-sm text-red-800 dark:text-red-200 space-y-1">
                    <li>• Visible strand breaks</li>
                    <li>• Severe fraying or fuzzing</li>
                    <li>• Loop separation or damage</li>
                    <li>• Serving unraveling</li>
                  </ul>
                </div>

                <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
                  <h4 class="font-medium text-amber-900 dark:text-amber-100 mb-2">Replace Soon</h4>
                  <ul class="text-sm text-amber-800 dark:text-amber-200 space-y-1">
                    <li>• Excessive string stretch</li>
                    <li>• Inconsistent grouping</li>
                    <li>• Changed bow performance</li>
                    <li>• Heavy use (1000+ shots)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Troubleshooting -->
      <section id="troubleshooting" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-tools text-yellow-500 mr-3"></i>
          Troubleshooting Common Issues
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <div class="space-y-6">
            <div class="border-l-4 border-red-500 pl-4">
              <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
                Problem: String too long (low bracing height)
              </h3>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <p><strong>Symptoms:</strong> Bracing height below manufacturer spec, poor arrow clearance, hand slap</p>
                <p><strong>Solutions:</strong></p>
                <ul class="list-disc list-inside ml-4 space-y-1">
                  <li>Add twists to Flemish string (temporary)</li>
                  <li>Order shorter replacement string</li>
                  <li>Check calculation accuracy</li>
                  <li>Verify bow length measurement</li>
                </ul>
              </div>
            </div>

            <div class="border-l-4 border-orange-500 pl-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-2">
                Problem: String too short (high bracing height)
              </h3>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <p><strong>Symptoms:</strong> Bracing height above spec, difficult to string, harsh shooting</p>
                <p><strong>Solutions:</strong></p>
                <ul class="list-disc list-inside ml-4 space-y-1">
                  <li>Remove twists from Flemish string (limited range)</li>
                  <li>Order longer replacement string</li>
                  <li>Check material stretch properties</li>
                  <li>Verify target bracing height</li>
                </ul>
              </div>
            </div>

            <div class="border-l-4 border-yellow-500 pl-4">
              <h3 class="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
                Problem: Inconsistent performance
              </h3>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <p><strong>Symptoms:</strong> Varying arrow groups, changed bow feel, noise increase</p>
                <p><strong>Solutions:</strong></p>
                <ul class="list-disc list-inside ml-4 space-y-1">
                  <li>Check string condition and age</li>
                  <li>Verify nocking point position</li>
                  <li>Apply fresh bowstring wax</li>
                  <li>Monitor for string stretch</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Conclusion -->
      <section class="mb-12">
        <div class="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 rounded-xl p-6 border border-red-200 dark:border-red-800">
          <h2 class="text-2xl font-bold text-red-900 dark:text-red-100 mb-4">
            <i class="fas fa-trophy mr-3"></i>
            String Selection Mastery
          </h2>
          <p class="text-red-800 dark:text-red-200 mb-4">
            Proper string selection combines technical knowledge with practical experience. 
            Use the calculator above for initial sizing, then fine-tune based on actual bow performance. 
            Remember that string selection significantly impacts your shooting experience.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-red-200 dark:border-red-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Key Success Factors</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Accurate bow measurements</li>
                <li>• Appropriate material selection</li>
                <li>• Proper length calculation</li>
                <li>• Regular maintenance routine</li>
              </ul>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-red-200 dark:border-red-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Safety Reminders</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Never shoot a damaged string</li>
                <li>• Replace strings showing wear</li>
                <li>• Use proper stringing technique</li>
                <li>• Keep spare strings available</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- Related Guides -->
      <section class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Related Guides</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <NuxtLink 
            to="/guides/bow-weight"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-600 transition-colors group"
          >
            <div class="flex items-center mb-2">
              <i class="fas fa-weight-hanging text-green-600 dark:text-green-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-green-600 dark:group-hover:text-green-400">
                Bow Weight Selection
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Choose the optimal draw weight for your shooting goals.
            </p>
          </NuxtLink>

          <NuxtLink 
            to="/guides/sight-setup"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600 transition-colors group"
          >
            <div class="flex items-center mb-2">
              <i class="fas fa-bullseye text-purple-600 dark:text-purple-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-purple-600 dark:group-hover:text-purple-400">
                Sight Setup & Tuning
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Master bow sight installation and calibration techniques.
            </p>
          </NuxtLink>

          <div class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 opacity-60">
            <div class="flex items-center mb-2">
              <i class="fas fa-arrows-alt-h text-gray-400 mr-3"></i>
              <h3 class="font-semibold text-gray-500 dark:text-gray-400">
                Paper Tuning Guide
              </h3>
            </div>
            <p class="text-sm text-gray-400">
              Coming soon - Learn to tune your bow for optimal arrow flight.
            </p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Set page title and meta
useHead({
  title: 'Recurve String Selection Guide - Calculate Perfect String Length',
  meta: [
    { name: 'description', content: 'Complete guide to selecting the perfect recurve bowstring with interactive calculator. Learn string materials, length calculation, and maintenance.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  // No authentication required - public guide
})

// Calculator reactive data
const calculator = ref({
  bowLength: 68,
  stringType: 'flemish',
  bracingHeight: 8.5,
  material: 'dacron'
})

// Computed properties for calculator
const calculatedStringLength = computed(() => {
  const bowLength = calculator.value.bowLength || 68
  const stringType = calculator.value.stringType
  
  // AMO Standard Formula: Recurve strings are typically 3-4 inches shorter than bow length
  // Most manufacturers use 3 inches as the standard
  let stringLength = bowLength - 3
  
  // Fine-tune based on string construction type
  // Flemish twist strings may need slight adjustment due to construction method
  if (stringType === 'flemish') {
    // Flemish strings can be the same length or slightly shorter
    stringLength = stringLength // No adjustment needed for Flemish
  } else {
    // Endless loop strings are typically standard length
    stringLength = stringLength // Standard AMO calculation
  }
  
  return Math.round(stringLength * 4) / 4 // Round to nearest quarter inch
})

const stringTypeDisplay = computed(() => {
  return calculator.value.stringType === 'flemish' ? 'Flemish Twist' : 'Endless Loop'
})

const materialProperties = computed(() => {
  const material = calculator.value.material
  
  const properties = {
    dacron: 'Forgiving stretch, compatible with all bows, quieter shooting, cost-effective',
    fastflight: 'Higher speeds, minimal stretch, requires reinforced tips, weather resistant',
    dyneema: 'Maximum performance, virtually no stretch, premium material, temperature stable'
  }
  
  return properties[material] || 'Select a material to see properties'
})

// Smooth scrolling for table of contents links
onMounted(() => {
  const links = document.querySelectorAll('a[href^="#"]')
  
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault()
      const targetId = link.getAttribute('href').substring(1)
      const targetElement = document.getElementById(targetId)
      
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        })
      }
    })
  })
})
</script>