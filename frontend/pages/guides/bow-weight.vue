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
          <span class="text-gray-900 dark:text-gray-100">Bow Weight Selection</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl mr-4">
          <i class="fas fa-weight-hanging text-green-600 dark:text-green-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Bow Weight Selection Guide</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">Learn how to choose the optimal draw weight for your archery goals and physical ability</p>
        </div>
      </div>
      
      <!-- Guide Info -->
      <div class="flex flex-wrap gap-4 text-sm">
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-clock mr-2"></i>
          12 min read
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

    <!-- Table of Contents -->
    <div class="bg-green-50 dark:bg-green-900/20 rounded-xl p-6 mb-8 border border-green-200 dark:border-green-800">
      <h2 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#understanding" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">1. Understanding Draw Weight</a>
        <a href="#factors" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">2. Factors to Consider</a>
        <a href="#recommendations" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">3. Weight Recommendations</a>
        <a href="#testing" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">4. Testing Draw Weight</a>
        <a href="#adjustment" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">5. Adjusting Over Time</a>
        <a href="#mistakes" class="text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 transition-colors">6. Common Mistakes</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- Understanding Draw Weight -->
      <section id="understanding" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-lightbulb text-yellow-500 mr-3"></i>
          Understanding Draw Weight
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-4">
            Draw weight is the amount of force (measured in pounds) required to pull the bowstring to full draw. 
            It's one of the most important specifications that affects your shooting experience and performance.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                <i class="fas fa-info-circle mr-2"></i>
                Key Points
              </h3>
              <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                <li>• Measured at your specific draw length</li>
                <li>• Affects arrow speed and kinetic energy</li>
                <li>• Influences accuracy and consistency</li>
                <li>• Determines legal hunting requirements</li>
              </ul>
            </div>
            
            <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-amber-900 dark:text-amber-100 mb-3">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                Why It Matters
              </h3>
              <ul class="text-sm text-amber-800 dark:text-amber-200 space-y-2">
                <li>• Too heavy: Poor form, fatigue, injury risk</li>
                <li>• Too light: Insufficient power, poor trajectory</li>
                <li>• Just right: Consistent accuracy, comfort</li>
                <li>• Room to grow: Allow for strength development</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- Factors to Consider -->
      <section id="factors" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <span class="bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3">2</span>
          Factors to Consider
        </h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Physical Factors -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
              <i class="fas fa-user text-blue-500 mr-3"></i>
              Physical Factors
            </h3>
            
            <div class="space-y-4">
              <div class="border-l-4 border-blue-500 pl-4">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">Body Strength</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Upper body, back, and shoulder strength determine sustainable draw weight</p>
              </div>
              
              <div class="border-l-4 border-green-500 pl-4">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">Age & Experience</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Beginners and younger archers should start lighter and build up</p>
              </div>
              
              <div class="border-l-4 border-purple-500 pl-4">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">Physical Condition</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Injuries, disabilities, or fitness level affect draw weight capacity</p>
              </div>
              
              <div class="border-l-4 border-orange-500 pl-4">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">Draw Length</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Longer draws require more strength; affects actual peak weight</p>
              </div>
            </div>
          </div>
          
          <!-- Purpose & Goals -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
              <i class="fas fa-bullseye text-red-500 mr-3"></i>
              Purpose & Goals
            </h3>
            
            <div class="space-y-4">
              <div class="border-l-4 border-red-500 pl-4">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">Target Archery</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Focus on consistency and accuracy over raw power</p>
              </div>
              
              <div class="border-l-4 border-yellow-500 pl-4">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">3D Archery</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Balance between accuracy and sufficient energy for various distances</p>
              </div>
              
              <div class="border-l-4 border-indigo-500 pl-4">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">Hunting</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Legal minimums vary by game; kinetic energy requirements</p>
              </div>
              
              <div class="border-l-4 border-teal-500 pl-4">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">Recreation</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">Comfort and enjoyment are primary considerations</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Weight Recommendations -->
      <section id="recommendations" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <span class="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3">3</span>
          Draw Weight Recommendations
        </h2>
        
        <!-- Age-Based Recommendations -->
        <div class="mb-8">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Age-Based Starting Points</h3>
          <div class="overflow-x-auto">
            <table class="w-full bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Age Group</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Beginner Weight</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Intermediate</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Advanced</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-600">
                <tr>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 font-medium">Youth (8-12)</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">10-20 lbs</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">20-30 lbs</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">30-40 lbs</td>
                </tr>
                <tr class="bg-gray-50 dark:bg-gray-700/50">
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 font-medium">Teen (13-17)</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">20-30 lbs</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">30-45 lbs</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">45-55 lbs</td>
                </tr>
                <tr>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 font-medium">Adult Women</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">25-35 lbs</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">35-45 lbs</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">45-55 lbs</td>
                </tr>
                <tr class="bg-gray-50 dark:bg-gray-700/50">
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 font-medium">Adult Men</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">35-45 lbs</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">45-60 lbs</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">60-70+ lbs</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Purpose-Based Recommendations -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-6 border border-green-200 dark:border-green-800">
            <h3 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
              <i class="fas fa-bullseye mr-2"></i>
              Target Archery
            </h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-green-800 dark:text-green-200">Indoor (18m/20 yards):</span>
                <span class="font-medium text-green-900 dark:text-green-100">25-40 lbs</span>
              </div>
              <div class="flex justify-between">
                <span class="text-green-800 dark:text-green-200">Outdoor (70m/90m):</span>
                <span class="font-medium text-green-900 dark:text-green-100">35-50 lbs</span>
              </div>
              <div class="flex justify-between">
                <span class="text-green-800 dark:text-green-200">Field Archery:</span>
                <span class="font-medium text-green-900 dark:text-green-100">40-55 lbs</span>
              </div>
              <p class="text-green-700 dark:text-green-300 mt-3 text-xs">
                Focus on weight you can shoot 100+ arrows comfortably
              </p>
            </div>
          </div>
          
          <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-6 border border-amber-200 dark:border-amber-800">
            <h3 class="text-lg font-semibold text-amber-900 dark:text-amber-100 mb-4">
              <i class="fas fa-tree mr-2"></i>
              Hunting Applications
            </h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-amber-800 dark:text-amber-200">Small Game:</span>
                <span class="font-medium text-amber-900 dark:text-amber-100">35-45 lbs</span>
              </div>
              <div class="flex justify-between">
                <span class="text-amber-800 dark:text-amber-200">Whitetail Deer:</span>
                <span class="font-medium text-amber-900 dark:text-amber-100">40-50 lbs</span>
              </div>
              <div class="flex justify-between">
                <span class="text-amber-800 dark:text-amber-200">Elk/Large Game:</span>
                <span class="font-medium text-amber-900 dark:text-amber-100">50-65+ lbs</span>
              </div>
              <p class="text-amber-700 dark:text-amber-300 mt-3 text-xs">
                Check local regulations for minimum draw weight requirements
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Testing Draw Weight -->
      <section id="testing" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <span class="bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3">4</span>
          Testing Your Ideal Draw Weight
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">The Draw Weight Test</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <h4 class="font-medium text-gray-900 dark:text-gray-100">Step-by-Step Process:</h4>
              <div class="space-y-3">
                <div class="flex items-start space-x-3">
                  <div class="bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">1</div>
                  <p class="text-sm text-gray-700 dark:text-gray-300">Start with a weight you can easily draw and hold for 30 seconds</p>
                </div>
                <div class="flex items-start space-x-3">
                  <div class="bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">2</div>
                  <p class="text-sm text-gray-700 dark:text-gray-300">Practice drawing and anchoring 20-30 times consecutively</p>
                </div>
                <div class="flex items-start space-x-3">
                  <div class="bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">3</div>
                  <p class="text-sm text-gray-700 dark:text-gray-300">Simulate a full practice session (1-2 hours)</p>
                </div>
                <div class="flex items-start space-x-3">
                  <div class="bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">4</div>
                  <p class="text-sm text-gray-700 dark:text-gray-300">Assess form degradation and fatigue levels</p>
                </div>
              </div>
            </div>
            
            <div class="space-y-4">
              <h4 class="font-medium text-gray-900 dark:text-gray-100">Signs of Proper Weight:</h4>
              <div class="space-y-2">
                <div class="flex items-center space-x-2">
                  <i class="fas fa-check text-green-500"></i>
                  <span class="text-sm text-gray-700 dark:text-gray-300">Smooth, controlled draw</span>
                </div>
                <div class="flex items-center space-x-2">
                  <i class="fas fa-check text-green-500"></i>
                  <span class="text-sm text-gray-700 dark:text-gray-300">Consistent anchor point</span>
                </div>
                <div class="flex items-center space-x-2">
                  <i class="fas fa-check text-green-500"></i>
                  <span class="text-sm text-gray-700 dark:text-gray-300">No shoulder hunching or trembling</span>
                </div>
                <div class="flex items-center space-x-2">
                  <i class="fas fa-check text-green-500"></i>
                  <span class="text-sm text-gray-700 dark:text-gray-300">Maintain good form throughout session</span>
                </div>
                <div class="flex items-center space-x-2">
                  <i class="fas fa-check text-green-500"></i>
                  <span class="text-sm text-gray-700 dark:text-gray-300">Not exhausted after normal practice</span>
                </div>
              </div>
              
              <h4 class="font-medium text-gray-900 dark:text-gray-100 mt-4">Warning Signs (Too Heavy):</h4>
              <div class="space-y-2">
                <div class="flex items-center space-x-2">
                  <i class="fas fa-times text-red-500"></i>
                  <span class="text-sm text-gray-700 dark:text-gray-300">Struggling to reach full draw</span>
                </div>
                <div class="flex items-center space-x-2">
                  <i class="fas fa-times text-red-500"></i>
                  <span class="text-sm text-gray-700 dark:text-gray-300">Shaking or trembling at full draw</span>
                </div>
                <div class="flex items-center space-x-2">
                  <i class="fas fa-times text-red-500"></i>
                  <span class="text-sm text-gray-700 dark:text-gray-300">Form breaks down quickly</span>
                </div>
                <div class="flex items-center space-x-2">
                  <i class="fas fa-times text-red-500"></i>
                  <span class="text-sm text-gray-700 dark:text-gray-300">Shoulder or back pain</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Adjusting Over Time -->
      <section id="adjustment" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <span class="bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3">5</span>
          Adjusting Draw Weight Over Time
        </h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-arrow-up text-green-500 mr-2"></i>
              Increasing Draw Weight
            </h3>
            
            <div class="space-y-4">
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">When to Increase:</h4>
                <ul class="text-sm text-green-800 dark:text-green-200 space-y-1">
                  <li>• Current weight feels easy</li>
                  <li>• Consistent accuracy achieved</li>
                  <li>• No fatigue after normal sessions</li>
                  <li>• Need more speed/energy for hunting</li>
                </ul>
              </div>
              
              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">How to Increase:</h4>
                <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                  <li>• Increase by 2-5 lbs at a time</li>
                  <li>• Allow 2-4 weeks to adapt</li>
                  <li>• Maintain proper form</li>
                  <li>• Reduce practice volume initially</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-arrow-down text-orange-500 mr-2"></i>
              Decreasing Draw Weight
            </h3>
            
            <div class="space-y-4">
              <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                <h4 class="font-medium text-orange-900 dark:text-orange-100 mb-2">When to Decrease:</h4>
                <ul class="text-sm text-orange-800 dark:text-orange-200 space-y-1">
                  <li>• Experiencing pain or injury</li>
                  <li>• Form deteriorating</li>
                  <li>• Returning after break</li>
                  <li>• Focusing on technique refinement</li>
                </ul>
              </div>
              
              <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">Benefits of Lower Weight:</h4>
                <ul class="text-sm text-purple-800 dark:text-purple-200 space-y-1">
                  <li>• Better form development</li>
                  <li>• Reduced injury risk</li>
                  <li>• Longer practice sessions</li>
                  <li>• Improved accuracy focus</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Common Mistakes -->
      <section id="mistakes" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-exclamation-triangle text-red-500 mr-3"></i>
          Common Mistakes to Avoid
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-red-50 dark:bg-red-900/20 rounded-xl p-6 border border-red-200 dark:border-red-800">
            <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-4">
              <i class="fas fa-times-circle mr-2"></i>
              What NOT to Do
            </h3>
            <div class="space-y-3">
              <div class="flex items-start space-x-3">
                <i class="fas fa-ban text-red-500 mt-1 flex-shrink-0"></i>
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200">Starting Too Heavy</h4>
                  <p class="text-sm text-red-700 dark:text-red-300">Most common mistake - leads to poor form and injury</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <i class="fas fa-ban text-red-500 mt-1 flex-shrink-0"></i>
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200">Ego-Based Selection</h4>
                  <p class="text-sm text-red-700 dark:text-red-300">Choosing weight based on what others shoot</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <i class="fas fa-ban text-red-500 mt-1 flex-shrink-0"></i>
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200">Ignoring Fatigue</h4>
                  <p class="text-sm text-red-700 dark:text-red-300">Continuing with heavy weight despite form breakdown</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <i class="fas fa-ban text-red-500 mt-1 flex-shrink-0"></i>
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200">Rushing Increases</h4>
                  <p class="text-sm text-red-700 dark:text-red-300">Increasing weight too quickly without adaptation time</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-green-50 dark:bg-green-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
            <h3 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
              <i class="fas fa-check-circle mr-2"></i>
              Best Practices
            </h3>
            <div class="space-y-3">
              <div class="flex items-start space-x-3">
                <i class="fas fa-check text-green-500 mt-1 flex-shrink-0"></i>
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200">Conservative Start</h4>
                  <p class="text-sm text-green-700 dark:text-green-300">Begin lighter than you think you need</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <i class="fas fa-check text-green-500 mt-1 flex-shrink-0"></i>
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200">Form First</h4>
                  <p class="text-sm text-green-700 dark:text-green-300">Prioritize proper technique over heavy weight</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <i class="fas fa-check text-green-500 mt-1 flex-shrink-0"></i>
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200">Professional Guidance</h4>
                  <p class="text-sm text-green-700 dark:text-green-300">Get advice from experienced archers or coaches</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <i class="fas fa-check text-green-500 mt-1 flex-shrink-0"></i>
                <div>
                  <h4 class="font-medium text-green-800 dark:text-green-200">Listen to Your Body</h4>
                  <p class="text-sm text-green-700 dark:text-green-300">Adjust based on comfort and performance</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Related Guides -->
    <div class="mt-12 bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
        <i class="fas fa-book-open mr-2"></i>
        Related Guides
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <NuxtLink to="/guides/draw-length" class="bg-white dark:bg-gray-700 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
          <h3 class="font-medium text-gray-900 dark:text-gray-100 mb-2">How to Measure Draw Length</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">Learn to accurately measure your draw length for optimal bow setup</p>
        </NuxtLink>
        <div class="bg-white dark:bg-gray-700 rounded-lg p-4 opacity-60">
          <h3 class="font-medium text-gray-500 dark:text-gray-400 mb-2">Proper Grip & Stance</h3>
          <p class="text-sm text-gray-400">Master the fundamentals of archery form - Coming Soon</p>
        </div>
      </div>
    </div>

    <!-- Back to Guides -->
    <div class="mt-8 text-center">
      <NuxtLink 
        to="/guides"
        class="inline-flex items-center px-6 py-3 bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 text-white font-medium rounded-lg transition-colors"
      >
        <i class="fas fa-arrow-left mr-2"></i>
        Back to All Guides
      </NuxtLink>
    </div>
  </div>
</template>

<script setup>
// Set page title and meta
useHead({
  title: 'Bow Weight Selection Guide - Complete Archery Guide',
  meta: [
    { name: 'description', content: 'Learn how to choose the optimal draw weight for your archery goals. Complete guide covering factors, recommendations, and testing methods.' },
    { name: 'keywords', content: 'bow weight, draw weight, archery selection, bow setup, beginner archery, hunting weight' }
  ]
})

// Protect this page with authentication
definePageMeta({
  // No authentication required - public guide
})
</script>

<style scoped>
/* Smooth scrolling for anchor links */
html {
  scroll-behavior: smooth;
}

/* Custom styling for the guide content */
.prose h2 {
  scroll-margin-top: 2rem;
}
</style>