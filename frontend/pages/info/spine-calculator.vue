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
          <span class="text-gray-900 dark:text-white">Spine Calculator</span>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Using the Spine Calculator
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Master arrow spine calculations with our professional calculator tool
        </p>
      </div>

      <!-- Quick Access -->
      <div class="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg border border-purple-200 dark:border-purple-800 p-6 mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-purple-800 dark:text-purple-200 mb-2">
              <i class="fas fa-calculator mr-2"></i>
              Ready to Calculate?
            </h2>
            <p class="text-purple-700 dark:text-purple-300">
              Use our professional spine calculator to find the perfect arrow for your bow setup.
            </p>
          </div>
          <NuxtLink
            to="/calculator"
            class="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
          >
            <i class="fas fa-arrow-right mr-2"></i>
            Open Calculator
          </NuxtLink>
        </div>
      </div>

      <div class="space-y-8">
        
        <!-- Getting Started -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            <i class="fas fa-play-circle text-green-600 dark:text-green-400 mr-3"></i>
            Getting Started
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                What You'll Need
              </h3>
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <ul class="space-y-2 text-sm text-green-700 dark:text-green-400">
                  <li class="flex items-center">
                    <i class="fas fa-check text-green-500 mr-2"></i>
                    <strong>Bow Draw Weight:</strong> Your bow's peak draw weight (e.g., 60 lbs)
                  </li>
                  <li class="flex items-center">
                    <i class="fas fa-check text-green-500 mr-2"></i>
                    <strong>Draw Length:</strong> Your measured draw length (e.g., 28")
                  </li>
                  <li class="flex items-center">
                    <i class="fas fa-check text-green-500 mr-2"></i>
                    <strong>Arrow Length:</strong> Desired finished arrow length (e.g., 29")
                  </li>
                  <li class="flex items-center">
                    <i class="fas fa-check text-green-500 mr-2"></i>
                    <strong>Point Weight:</strong> Field point or broadhead weight (e.g., 100 grains)
                  </li>
                  <li class="flex items-center">
                    <i class="fas fa-check text-green-500 mr-2"></i>
                    <strong>Bow Type:</strong> Compound, recurve, or traditional bow
                  </li>
                </ul>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Calculator Features
              </h3>
              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <ul class="space-y-2 text-sm text-blue-700 dark:text-blue-400">
                  <li class="flex items-center">
                    <i class="fas fa-star text-blue-500 mr-2"></i>
                    Professional spine calculations using industry standards
                  </li>
                  <li class="flex items-center">
                    <i class="fas fa-star text-blue-500 mr-2"></i>
                    Real-time arrow recommendations from our database
                  </li>
                  <li class="flex items-center">
                    <i class="fas fa-star text-blue-500 mr-2"></i>
                    FOC (Front of Center) balance calculations
                  </li>
                  <li class="flex items-center">
                    <i class="fas fa-star text-blue-500 mr-2"></i>
                    Kinetic energy and momentum analysis
                  </li>
                  <li class="flex items-center">
                    <i class="fas fa-star text-blue-500 mr-2"></i>
                    Compatibility scoring for arrow matching
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Step-by-Step Guide -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            <i class="fas fa-list-ol text-blue-600 dark:text-blue-400 mr-3"></i>
            Step-by-Step Calculator Guide
          </h2>
          
          <div class="space-y-6">
            <!-- Step 1 -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">1</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Navigate to the Calculator
                </h3>
                <p class="text-gray-600 dark:text-gray-400 mb-3">
                  Access the spine calculator from the main navigation menu or use the quick link above.
                </p>
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <p class="text-sm text-gray-700 dark:text-gray-300">
                    <strong>Location:</strong> Main Menu → Spine Calculator or direct link: <code class="bg-gray-200 dark:bg-gray-600 px-1 rounded">/calculator</code>
                  </p>
                </div>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">2</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Enter Your Bow Specifications
                </h3>
                <p class="text-gray-600 dark:text-gray-400 mb-3">
                  Fill in your bow's specifications in the input fields provided.
                </p>
                <div class="grid gap-4 md:grid-cols-2">
                  <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3">
                    <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">Bow Settings</h4>
                    <ul class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                      <li>• <strong>Draw Weight:</strong> Enter your bow's peak weight</li>
                      <li>• <strong>Draw Length:</strong> Your measured draw length</li>
                      <li>• <strong>Bow Type:</strong> Select compound/recurve/traditional</li>
                    </ul>
                  </div>
                  <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3">
                    <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">Arrow Settings</h4>
                    <ul class="text-sm text-orange-700 dark:text-orange-400 space-y-1">
                      <li>• <strong>Arrow Length:</strong> Desired finished length</li>
                      <li>• <strong>Point Weight:</strong> Field point/broadhead weight</li>
                      <li>• <strong>Use Case:</strong> Target, hunting, or 3D archery</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">3</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Review Calculated Spine Requirements
                </h3>
                <p class="text-gray-600 dark:text-gray-400 mb-3">
                  The calculator will display your optimal spine range and specifications.
                </p>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                    Understanding Your Results
                  </h4>
                  <div class="grid gap-3 md:grid-cols-2">
                    <div>
                      <p class="text-sm text-green-700 dark:text-green-400">
                        <strong>Spine Range:</strong> Recommended spine values (e.g., 340-400)
                      </p>
                      <p class="text-sm text-green-700 dark:text-green-400">
                        <strong>Optimal Spine:</strong> The calculated ideal spine value
                      </p>
                    </div>
                    <div>
                      <p class="text-sm text-green-700 dark:text-green-400">
                        <strong>FOC Range:</strong> Front of Center balance percentage
                      </p>
                      <p class="text-sm text-green-700 dark:text-green-400">
                        <strong>Performance Metrics:</strong> KE, momentum, velocity
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 4 -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">4</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Browse Arrow Recommendations
                </h3>
                <p class="text-gray-600 dark:text-gray-400 mb-3">
                  View arrows from our database that match your calculated specifications.
                </p>
                <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-indigo-800 dark:text-indigo-300 mb-2">
                    Recommendation Features
                  </h4>
                  <ul class="text-sm text-indigo-700 dark:text-indigo-400 space-y-1">
                    <li>• <strong>Compatibility Score:</strong> Percentage match to your specs</li>
                    <li>• <strong>Manufacturer Info:</strong> Brand, model, and specifications</li>
                    <li>• <strong>Performance Data:</strong> Real spine values, GPI, diameter</li>
                    <li>• <strong>Sorting Options:</strong> By compatibility, price, or manufacturer</li>
                    <li>• <strong>Filter Tools:</strong> Narrow results by brand or arrow type</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Step 5 -->
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold">5</div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Save to Your Bow Setup
                </h3>
                <p class="text-gray-600 dark:text-gray-400 mb-3">
                  Add promising arrows to your bow setup for tracking and comparison.
                </p>
                <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-teal-800 dark:text-teal-300 mb-2">
                    Saving Benefits
                  </h4>
                  <ul class="text-sm text-teal-700 dark:text-teal-400 space-y-1">
                    <li>• <strong>Comparison Tool:</strong> Compare multiple arrow options side-by-side</li>
                    <li>• <strong>Performance Tracking:</strong> Monitor real-world performance vs. calculations</li>
                    <li>• <strong>Setup History:</strong> Track changes and tuning progress over time</li>
                    <li>• <strong>Notes & Ratings:</strong> Add personal notes and performance ratings</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Understanding Spine Calculations -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            <i class="fas fa-graduation-cap text-yellow-600 dark:text-yellow-400 mr-3"></i>
            Understanding Spine Calculations
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <!-- Calculation Method -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                How Our Calculator Works
              </h3>
              <div class="space-y-4">
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                    Professional Formula
                  </h4>
                  <p class="text-sm text-yellow-700 dark:text-yellow-400 mb-2">
                    We use industry-standard spine calculation formulas that account for:
                  </p>
                  <ul class="text-sm text-yellow-700 dark:text-yellow-400 list-disc list-inside ml-2 space-y-1">
                    <li>Draw weight at your specific draw length</li>
                    <li>Arrow length beyond rest position</li>
                    <li>Point weight effects on dynamic spine</li>
                    <li>Bow type efficiency factors</li>
                    <li>String angle and force distribution</li>
                  </ul>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
                    Real-World Adjustments
                  </h4>
                  <p class="text-sm text-blue-700 dark:text-blue-400">
                    Our calculations include real-world factors that affect arrow flight, not just theoretical spine values.
                  </p>
                </div>
              </div>
            </div>

            <!-- Factors That Affect Spine -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Key Factors in Spine Selection
              </h3>
              <div class="space-y-3">
                <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-3">
                  <h4 class="font-medium text-gray-900 dark:text-white mb-1">
                    <i class="fas fa-weight-hanging text-red-500 mr-2"></i>
                    Draw Weight
                  </h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Higher draw weights require stiffer arrows. The calculator adjusts for your specific poundage.
                  </p>
                </div>
                
                <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-3">
                  <h4 class="font-medium text-gray-900 dark:text-white mb-1">
                    <i class="fas fa-ruler text-blue-500 mr-2"></i>
                    Arrow Length
                  </h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Longer arrows act weaker. Each inch of length significantly affects spine requirements.
                  </p>
                </div>
                
                <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-3">
                  <h4 class="font-medium text-gray-900 dark:text-white mb-1">
                    <i class="fas fa-dot-circle text-green-500 mr-2"></i>
                    Point Weight
                  </h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Heavier points make arrows act weaker. Critical for broadhead compatibility.
                  </p>
                </div>
                
                <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-3">
                  <h4 class="font-medium text-gray-900 dark:text-white mb-1">
                    <i class="fas fa-archway text-purple-500 mr-2"></i>
                    Bow Type
                  </h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Compound, recurve, and traditional bows have different efficiency factors affecting spine needs.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Advanced Features -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            <i class="fas fa-cogs text-indigo-600 dark:text-indigo-400 mr-3"></i>
            Advanced Calculator Features
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-3">
            <!-- FOC Calculations -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                <i class="fas fa-balance-scale text-orange-500 mr-2"></i>
                FOC Analysis
              </h3>
              <div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <p>Front of Center balance calculations show how your arrow's weight distribution affects flight.</p>
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded p-2">
                  <p class="text-orange-700 dark:text-orange-400">
                    <strong>Optimal FOC:</strong> 10-15% for target, 15-20% for hunting
                  </p>
                </div>
              </div>
            </div>

            <!-- Performance Metrics -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                <i class="fas fa-tachometer-alt text-green-500 mr-2"></i>
                Performance Data
              </h3>
              <div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <p>Real-time calculations of kinetic energy, momentum, and estimated velocity for your setup.</p>
                <div class="bg-green-50 dark:bg-green-900/20 rounded p-2">
                  <p class="text-green-700 dark:text-green-400">
                    <strong>Includes:</strong> KE, momentum, velocity estimates
                  </p>
                </div>
              </div>
            </div>

            <!-- Database Integration -->
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                <i class="fas fa-database text-blue-500 mr-2"></i>
                Live Database
              </h3>
              <div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <p>Instant access to 1,100+ arrows from 13+ manufacturers with real spine data and specifications.</p>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded p-2">
                  <p class="text-blue-700 dark:text-blue-400">
                    <strong>Updated:</strong> Real manufacturer spine charts
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tips for Best Results -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            <i class="fas fa-lightbulb text-yellow-600 dark:text-yellow-400 mr-3"></i>
            Tips for Best Results
          </h2>
          
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Accurate Measurements
              </h3>
              <div class="space-y-3">
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-1">Draw Length</h4>
                  <p class="text-sm text-yellow-700 dark:text-yellow-400">
                    Measure from nock groove to throat of grip + 1.75". Don't guess - this critically affects spine calculations.
                  </p>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-1">Draw Weight</h4>
                  <p class="text-sm text-yellow-700 dark:text-yellow-400">
                    Use actual draw weight at your draw length, not the bow's marked weight. This can vary significantly.
                  </p>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Calculator Best Practices
              </h3>
              <div class="space-y-3">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-1">Start Conservative</h4>
                  <p class="text-sm text-green-700 dark:text-green-400">
                    If between spine recommendations, start with the stiffer option. You can always add point weight to weaken.
                  </p>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <h4 class="font-medium text-green-800 dark:text-green-300 mb-1">Consider Use Case</h4>
                  <p class="text-sm text-green-700 dark:text-green-400">
                    Target arrows can be more precisely tuned. Hunting arrows need broader compatibility for different broadheads.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Next Steps -->
        <div class="bg-gradient-to-br from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg border border-green-200 dark:border-green-800 p-6">
          <h3 class="text-xl font-semibold text-green-800 dark:text-green-200 mb-4">
            <i class="fas fa-arrow-right mr-2"></i>
            Next Steps After Calculation
          </h3>
          
          <div class="grid gap-4 md:grid-cols-3">
            <div class="text-center">
              <div class="w-12 h-12 bg-green-600 text-white rounded-full flex items-center justify-center mx-auto mb-2">
                <i class="fas fa-shopping-cart"></i>
              </div>
              <h4 class="font-medium text-green-800 dark:text-green-300 mb-1">Order Arrows</h4>
              <p class="text-sm text-green-700 dark:text-green-400">
                Use our recommendations to order the right arrows for your setup.
              </p>
            </div>
            
            <div class="text-center">
              <div class="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-2">
                <i class="fas fa-bullseye"></i>
              </div>
              <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-1">Fine-Tune</h4>
              <p class="text-sm text-blue-700 dark:text-blue-400">
                Use our interactive tuning guides to optimize your arrow flight.
              </p>
            </div>
            
            <div class="text-center">
              <div class="w-12 h-12 bg-purple-600 text-white rounded-full flex items-center justify-center mx-auto mb-2">
                <i class="fas fa-chart-line"></i>
              </div>
              <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-1">Track Performance</h4>
              <p class="text-sm text-purple-700 dark:text-purple-400">
                Monitor real-world performance in your bow setup dashboard.
              </p>
            </div>
          </div>
          
          <div class="mt-6 flex justify-center space-x-4">
            <NuxtLink
              to="/calculator"
              class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-calculator mr-2"></i>
              Start Calculating
            </NuxtLink>
            <NuxtLink
              to="/tuning"
              class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <i class="fas fa-play mr-2"></i>
              Interactive Tuning
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Page metadata
definePageMeta({
  layout: 'default'
})

useHead({
  title: 'Spine Calculator Guide - Archery Tools',
  meta: [
    { name: 'description', content: 'Complete guide to using our professional spine calculator for accurate arrow selection and tuning calculations.' }
  ]
})
</script>

<style scoped>
/* Component specific styles */
code {
  @apply bg-gray-200 dark:bg-gray-600 px-1 py-0.5 rounded text-sm;
}
</style>