<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center space-x-3">
          <NuxtLink to="/info" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300">
            <i class="fas fa-arrow-left text-lg"></i>
          </NuxtLink>
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <i class="fas fa-archery text-orange-600 dark:text-orange-400 text-xl"></i>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Barebow Archery</h1>
              <p class="text-gray-600 dark:text-gray-400">Complete guide to barebow equipment, tuning, and technique</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Introduction -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          <i class="fas fa-info-circle mr-2 text-orange-600 dark:text-orange-400"></i>
          What is Barebow Archery?
        </h2>
        <div class="prose dark:prose-invert max-w-none">
          <p class="text-gray-700 dark:text-gray-300 mb-4">
            Barebow is a recurve bow discipline that uses modern materials but prohibits accessories that aid in aiming or stabilization. 
            Archers must rely on consistent form, muscle memory, and specialized aiming techniques to achieve accuracy.
          </p>
          <div class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
            <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">Competition Distances</h4>
            <div class="text-sm text-orange-700 dark:text-orange-400 space-y-1">
              <p><strong>Field Archery:</strong> 5-50 meters at target faces 20-80cm diameter</p>
              <p><strong>Target Archery:</strong> 50 meters at 122cm target face</p>
              <p><strong>Indoor:</strong> 18 meters with specialized arrow setups</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Equipment Setup -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-tools mr-2 text-blue-600 dark:text-blue-400"></i>
          Equipment Setup & Regulations
        </h2>

        <!-- Riser Selection -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Riser Length Selection</h3>
          <div class="grid md:grid-cols-3 gap-4">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">23" Riser</h4>
              <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                <p><strong>Best for:</strong> Draw length < 25"</p>
                <p><strong>With Short Limbs:</strong> 64" bow</p>
                <p><strong>With Medium Limbs:</strong> 66" bow</p>
                <p><strong>Competition:</strong> Standard barebow class</p>
              </div>
            </div>
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">25" Riser (Most Popular)</h4>
              <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                <p><strong>Best for:</strong> Most draw lengths</p>
                <p><strong>With Medium Limbs:</strong> 68" bow (standard)</p>
                <p><strong>With Short Limbs:</strong> 66" bow</p>
                <p><strong>Competition:</strong> Most common choice</p>
              </div>
            </div>
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">27" Riser</h4>
              <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                <p><strong>Best for:</strong> Draw length > 31"</p>
                <p><strong>With Medium Limbs:</strong> 70" bow</p>
                <p><strong>With Long Limbs:</strong> 72" bow</p>
                <p><strong>Benefit:</strong> Increased stability</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Weight System -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Weight System (No Stabilizers)</h3>
          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
            <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
              <i class="fas fa-exclamation-triangle mr-2"></i>
              Equipment Restrictions
            </h4>
            <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
              <p><strong>Prohibited:</strong> Traditional stabilizers, clickers, draw checks, sighting aids</p>
              <p><strong>Allowed:</strong> Fixed weights above/below grip that pass through 12.2cm ring</p>
              <p><strong>Vibration Dampeners:</strong> Allowed if they pass through 12.2cm ring without flexing</p>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">Weight Placement Benefits</h4>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <li><strong>Bottom Weight:</strong> Prevents bow tipping backward, improves vertical balance</li>
                <li><strong>Equal Limb Weights:</strong> Improves shot reaction and stability</li>
                <li><strong>Forward Weight:</strong> Makes bow jump forward instead of falling away</li>
                <li><strong>Heavy Riser:</strong> Natural weight distribution (Spigarelli, Best, Bernardini)</li>
              </ul>
            </div>
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">Recommended Weight Products</h4>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <li><strong>Axcel Stabilizer 10oz Stack:</strong> Inspection-approved design</li>
                <li><strong>Custom Weights:</strong> 1/4 lb to 5/8 lb options</li>
                <li><strong>Stollid Bull Black Thunder:</strong> 2.5kg heavy riser with weight block</li>
                <li><strong>Round Weights:</strong> Fit regulation ring requirements perfectly</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Bow Weight Considerations -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Bow Weight Selection</h3>
          <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
              <i class="fas fa-lightbulb mr-2"></i>
              Key Insight: Higher Poundage ≠ Better Performance
            </h4>
            <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-2">
              <p>Unlike compound or Olympic recurve, higher draw weight can be detrimental to barebow aiming accuracy.</p>
              <p><strong>Range Capability:</strong> Even 22# bows can comfortably reach 100 yards</p>
              <p><strong>Recommendation:</strong> Choose weight that allows consistent, controlled shooting over maximum power</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Arrow Selection & Tuning -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-crosshairs mr-2 text-green-600 dark:text-green-400"></i>
          Arrow Selection & Tuning
        </h2>

        <!-- Spine Selection -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Spine Selection for Barebow</h3>
          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
            <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
              <i class="fas fa-exclamation-triangle mr-2"></i>
              Critical: Barebow Requires Stiffer Arrows
            </h4>
            <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
              <p><strong>Rule:</strong> Generally 1 spine stiffer than Olympic recurve recommendations</p>
              <p><strong>Reality:</strong> Spine charts are not very accurate for barebow shooting</p>
              <p><strong>Method:</strong> Tune all components together - spine, length, point weight, vane weight</p>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">Spine Examples by Poundage</h4>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <p><strong>26# @ 30":</strong> 1000 spine (or longer 900 spine)</p>
                <p><strong>32# @ 30":</strong> 730-800 spine</p>
                <p><strong>36# @ 30":</strong> 660 spine</p>
                <p><strong>Note:</strong> These are starting points - tune with components</p>
              </div>
            </div>
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">Tuning Process</h4>
              <div class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <p><strong>Method:</strong> Bare shaft/fletched grouping at 18-20m</p>
                <p><strong>Components:</strong> Tune spine, length, point, vane, nock weights together</p>
                <p><strong>String Walking:</strong> Choose one crawl distance for tuning</p>
                <p><strong>Goal:</strong> Bare shafts and fletched arrows hit same group</p>
              </div>
            </div>
          </div>
        </div>

        <!-- FOC Balance -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">FOC (Front of Center) Balance</h3>
          <div class="grid md:grid-cols-3 gap-4">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Standard FOC</h4>
              <div class="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                <p><strong>Range:</strong> 10-15%</p>
                <p><strong>Use:</strong> General shooting</p>
                <p><strong>Point Weight:</strong> 100-120 grains</p>
                <p><strong>Application:</strong> Most versatile setup</p>
              </div>
            </div>
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Indoor Competition</h4>
              <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
                <p><strong>Range:</strong> 12-18%</p>
                <p><strong>Use:</strong> Indoor tournaments</p>
                <p><strong>Benefit:</strong> Better grouping at close range</p>
                <p><strong>Point Weight:</strong> 120-200 grains typical</p>
              </div>
            </div>
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">Extreme FOC</h4>
              <div class="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                <p><strong>Range:</strong> 26-28%</p>
                <p><strong>Use:</strong> No string walking tournaments</p>
                <p><strong>Benefit:</strong> Arrow points in right direction quicker</p>
                <p><strong>Expert Level:</strong> Used by top USA barebow archers</p>
              </div>
            </div>
          </div>

          <div class="mt-6 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 class="font-medium text-gray-900 dark:text-white mb-3">FOC as Tuning Tool</h4>
            <p class="text-sm text-gray-700 dark:text-gray-300 mb-3">
              "FOC's best application is fine-tuning the spine of your arrow" - Modern approach uses FOC less as flight tool, more for spine adjustment.
            </p>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              <strong>Testing Method:</strong> Experiment with field points from 100-300 grains to find optimal balance and grouping.
            </div>
          </div>
        </div>

        <!-- Point Weight Effects -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Point Weight Effects on Dynamic Spine</h3>
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">
              <i class="fas fa-physics mr-2"></i>
              Physics Principle
            </h4>
            <p class="text-sm text-blue-700 dark:text-blue-400 mb-3">
              Point weight affects dynamic spine - the actual stiffness in flight. More point weight = weaker dynamic spine 
              because the point provides resistance against the bowstring's driving force, causing increased shaft flex.
            </p>
            <div class="text-sm text-blue-600 dark:text-blue-300">
              <strong>Tuning Strategy:</strong> Use point weight as a primary tool for fine-tuning arrow spine to bow
            </div>
          </div>
        </div>
      </div>

      <!-- Aiming Techniques -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-eye mr-2 text-purple-600 dark:text-purple-400"></i>
          Aiming Techniques
        </h2>

        <div class="grid md:grid-cols-2 gap-8">
          <!-- String Walking -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">String Walking</h3>
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 mb-4">
              <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">Technique Overview</h4>
              <div class="text-sm text-purple-700 dark:text-purple-400 space-y-2">
                <p>Move fingers down the string based on target distance while keeping arrow point on target center.</p>
                <p><strong>Close Targets:</strong> Fingers farther from nock (up to 20cm below)</p>
                <p><strong>Far Targets:</strong> Fingers closer to nock (higher on string)</p>
              </div>
            </div>
            
            <h4 class="font-medium text-gray-900 dark:text-white mb-3">String Walking Requirements</h4>
            <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Finger Tab:</strong> Pre-marked three-under tab with crawl marks</li>
              <li><strong>Anchor Point:</strong> Consistent facial reference (fixed anchor)</li>
              <li><strong>Practice:</strong> Extensive distance practice and data collection</li>
              <li><strong>Tuning:</strong> Choose one crawl distance for arrow tuning</li>
            </ul>

            <div class="mt-4 bg-gray-100 dark:bg-gray-700 rounded-lg p-3">
              <h5 class="font-medium text-gray-800 dark:text-gray-200 mb-2">Tuning Crawl Selection</h5>
              <div class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <p><strong>Field Archery:</strong> Use median crawl distance</p>
                <p><strong>Outdoor Target:</strong> Use 50m crawl</p>
                <p><strong>Indoor Target:</strong> Use 18m crawl</p>
              </div>
            </div>
          </div>

          <!-- Gap Shooting -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Gap Shooting</h3>
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 mb-4">
              <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">Technique Overview</h4>
              <div class="text-sm text-green-700 dark:text-green-400 space-y-2">
                <p>Maintain same finger position and anchor while aiming arrow tip above or below target center.</p>
                <p><strong>Short Distance:</strong> Aim below target center</p>
                <p><strong>Long Distance:</strong> Aim above target center</p>
              </div>
            </div>

            <h4 class="font-medium text-gray-900 dark:text-white mb-3">Gap Shooting Requirements</h4>
            <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Fixed Anchor:</strong> Consistent facial reference point</li>
              <li><strong>Gap Data:</strong> Distance-specific aiming points</li>
              <li><strong>Practice:</strong> Develop gap charts for various distances</li>
              <li><strong>Windage:</strong> Use string/bow window edge alignment</li>
            </ul>

            <div class="mt-4 bg-gray-100 dark:bg-gray-700 rounded-lg p-3">
              <h5 class="font-medium text-gray-800 dark:text-gray-200 mb-2">Gap Development</h5>
              <div class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <p>Start with known distances and record where arrow tip aims</p>
                <p>Build personal gap chart through systematic practice</p>
                <p>Adjust for varying shooting conditions</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Face Walking & Instinctive -->
        <div class="grid md:grid-cols-2 gap-6 mt-8">
          <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
            <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">Face Walking</h4>
            <div class="text-sm text-orange-700 dark:text-orange-400 space-y-2">
              <p><strong>Method:</strong> Change anchor point on face based on distance</p>
              <p><strong>Close Distance:</strong> Anchor closer to eye</p>
              <p><strong>Reliability:</strong> Less reliable than fixed anchor methods</p>
              <p><strong>Challenge:</strong> Difficult to find exact reference points</p>
            </div>
          </div>
          <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
            <h4 class="font-medium text-teal-800 dark:text-teal-300 mb-2">Instinctive Shooting</h4>
            <div class="text-sm text-teal-700 dark:text-teal-400 space-y-2">
              <p><strong>Method:</strong> Subconscious aiming through repetition</p>
              <p><strong>Focus:</strong> Concentrate on target spot, not aiming mechanics</p>
              <p><strong>Development:</strong> Requires extensive practice at all distances</p>
              <p><strong>Mental:</strong> Faith that arrow will go where looking</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Technical Setup -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-cogs mr-2 text-indigo-600 dark:text-indigo-400"></i>
          Technical Setup
        </h2>

        <!-- Finger Tab & Draw -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Finger Tab & Draw Technique</h3>
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">Three-Under Mediterranean Draw</h4>
              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <div class="text-sm text-blue-700 dark:text-blue-400 space-y-2">
                  <p><strong>Finger Position:</strong> Index, middle, and ring fingers all below arrow</p>
                  <p><strong>Benefit:</strong> Arrow closer to eye for better alignment</p>
                  <p><strong>Application:</strong> Enables string walking technique</p>
                  <p><strong>Standard:</strong> Most common barebow draw method</p>
                </div>
              </div>
            </div>
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">Tab Selection</h4>
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <div class="text-sm text-green-700 dark:text-green-400 space-y-2">
                  <p><strong>Type:</strong> Simple single-patch tab (not split-finger Olympic style)</p>
                  <p><strong>String Walking:</strong> Pre-marked tabs with crawl distance marks</p>
                  <p><strong>Material:</strong> Leather or synthetic with good feel</p>
                  <p><strong>Features:</strong> Ledge preferred by most archers</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Anchor Points -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Anchor Points</h3>
          <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-4">
            <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
              <i class="fas fa-target mr-2"></i>
              Most Common Anchor: Index Finger at Lip Corner
            </h4>
            <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
              <p><strong>Position:</strong> Index finger tucked into corner of lip</p>
              <p><strong>Hand Position:</strong> Top of hand runs under cheekbone</p>
              <p><strong>Eye Alignment:</strong> Line up eye with string for proper windage</p>
              <p><strong>Consistency:</strong> Critical for accurate shooting</p>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">Alternative Anchors</h4>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <li><strong>Middle Finger:</strong> Corner of mouth (some archers prefer this)</li>
                <li><strong>Cheekbone:</strong> Just underneath eye (novice recommendation)</li>
                <li><strong>Jaw Line:</strong> Consistent bone reference</li>
                <li><strong>Note:</strong> Choose one and practice consistently</li>
              </ul>
            </div>
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">Regional Preferences</h4>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <li><strong>European Style:</strong> Index finger anchor preferred</li>
                <li><strong>American Style:</strong> Middle finger anchor common</li>
                <li><strong>Beginner:</strong> Cheekbone anchor for learning</li>
                <li><strong>Advanced:</strong> Lip corner for precision</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Arrow Rest Selection -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Arrow Rest Selection</h3>
          <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                <i class="fas fa-medal mr-2"></i>
                Beginner Choice: Hoyt Super Rest
              </h4>
              <div class="text-sm text-green-700 dark:text-green-400 space-y-2">
                <p><strong>Benefits:</strong> Lightweight, flexible, forgiving</p>
                <p><strong>Cost:</strong> Affordable entry-level option</p>
                <p><strong>Setup:</strong> Easy to install and adjust</p>
                <p><strong>Performance:</strong> Excellent for learning barebow</p>
              </div>
            </div>
            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h4 class="font-medium text-purple-800 dark:text-purple-300 mb-2">
                <i class="fas fa-trophy mr-2"></i>
                Advanced Choice: Zniper Drop-Away
              </h4>
              <div class="text-sm text-purple-700 dark:text-purple-400 space-y-2">
                <p><strong>Benefits:</strong> Cleanest shot, minimal arrow contact</p>
                <p><strong>Cost:</strong> Around £70 (premium option)</p>
                <p><strong>Setup:</strong> Requires tuning patience</p>
                <p><strong>Performance:</strong> Competition-level accuracy</p>
              </div>
            </div>
          </div>

          <div class="mt-4 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 class="font-medium text-gray-900 dark:text-white mb-3">Plunger Button Recommendation</h4>
            <div class="text-sm text-gray-700 dark:text-gray-300">
              <p class="mb-2"><strong>Recommended:</strong> Shibuya DX plunger button</p>
              <p><strong>Purpose:</strong> Essential for countering archer's paradox and straightening arrow flight</p>
              <p><strong>Value:</strong> Reasonably priced with excellent performance</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Competition Considerations -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-trophy mr-2 text-gold-600"></i>
          Competition Considerations
        </h2>

        <!-- Equipment Compliance -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Equipment Compliance</h3>
          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
            <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">
              <i class="fas fa-ban mr-2"></i>
              Prohibited Equipment
            </h4>
            <div class="text-sm text-red-700 dark:text-red-400 space-y-1">
              <p>• Sights, marks, or blemishes used as sighting aids</p>
              <p>• Clickers and/or draw checks</p>
              <p>• Traditional stabilizers (vibration dampeners must fit 12.2cm ring)</p>
              <p>• Arrow modifications beyond fletching wraps or use wear</p>
            </div>
          </div>

          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
              <i class="fas fa-check mr-2"></i>
              Allowed Equipment
            </h4>
            <div class="text-sm text-green-700 dark:text-green-400 space-y-1">
              <p>• Weights above and below grip (non-aiming purpose)</p>
              <p>• Vibration dampeners (if they pass 12.2cm ring test)</p>
              <p>• Arrow shafts up to 9.3mm (.366") diameter</p>
              <p>• Field points up to 9.4mm (.370") diameter</p>
            </div>
          </div>
        </div>

        <!-- Arrow Length Strategy -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Arrow Length Strategy</h3>
          <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Outdoor Shooting</h4>
              <div class="text-sm text-blue-700 dark:text-blue-400 space-y-2">
                <p><strong>Shorter Arrows:</strong> Provide longer range with any given crawl</p>
                <p><strong>Benefit:</strong> More efficient for field archery distances</p>
                <p><strong>Trade-off:</strong> May require more crawl adjustments</p>
              </div>
            </div>
            <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
              <h4 class="font-medium text-orange-800 dark:text-orange-300 mb-2">Indoor Shooting</h4>
              <div class="text-sm text-orange-700 dark:text-orange-400 space-y-2">
                <p><strong>Longer Arrows:</strong> Advantageous for indoor distances</p>
                <p><strong>Benefit:</strong> Better sight picture at close range</p>
                <p><strong>Setup:</strong> Optimized for 18m competition</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Premium Equipment -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-star mr-2 text-yellow-600 dark:text-yellow-400"></i>
          Premium Equipment Options
        </h2>

        <div class="grid md:grid-cols-2 gap-8">
          <!-- Elite Arrows -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Elite Arrow Options</h3>
            <div class="space-y-4">
              <div class="bg-gold-50 dark:bg-yellow-900/20 rounded-lg p-4">
                <h4 class="font-medium text-yellow-800 dark:text-yellow-300 mb-2">Easton Premium Series</h4>
                <div class="text-sm text-yellow-700 dark:text-yellow-400 space-y-2">
                  <p><strong>X10 Series:</strong> X10, X10 Protour, X10 Procomp (from £360/12 pack)</p>
                  <p><strong>A/C/E Arrows:</strong> From £260/12 pack</p>
                  <p><strong>Feature:</strong> Digital spine alignment within ±0.5 grains</p>
                  <p><strong>Benefit:</strong> Tighter grouping for elite competition</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Software Tools -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Software Tools</h3>
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h4 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Archer's Advantage Online</h4>
              <div class="text-sm text-blue-700 dark:text-blue-400 space-y-2">
                <p><strong>Cost:</strong> $20/year subscription</p>
                <p><strong>Features:</strong> Shaft spine selection, custom sight tapes</p>
                <p><strong>Calculations:</strong> Velocity and weight optimization</p>
                <p><strong>Purpose:</strong> Optimize arrow design for barebow setup</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mental Game & Practice -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          <i class="fas fa-brain mr-2 text-pink-600 dark:text-pink-400"></i>
          Mental Game & Practice Development
        </h2>

        <div class="grid md:grid-cols-2 gap-8">
          <!-- Mental Requirements -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Mental Game Requirements</h3>
            <div class="bg-pink-50 dark:bg-pink-900/20 rounded-lg p-4 mb-4">
              <h4 class="font-medium text-pink-800 dark:text-pink-300 mb-2">Consistency Demands</h4>
              <div class="text-sm text-pink-700 dark:text-pink-400 space-y-2">
                <p><strong>Draw Length:</strong> Incredible consistency in bow draw repetition required</p>
                <p><strong>Mental Fortitude:</strong> Execute clean shot without mechanical aids</p>
                <p><strong>Shot Process:</strong> Better form = more effective aiming</p>
                <p><strong>Confidence:</strong> Faith that arrow will go where aiming (instinctive)</p>
              </div>
            </div>

            <h4 class="font-medium text-gray-900 dark:text-white mb-3">Practice Philosophy</h4>
            <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Volume:</strong> "Arrow after arrow at all distances" for instinctive</li>
              <li><strong>Data Collection:</strong> Systematic gap/crawl chart development</li>
              <li><strong>Patience:</strong> Aiming methods need most time and practice</li>
              <li><strong>Dedication:</strong> Each method equally effective but requires commitment</li>
            </ul>
          </div>

          <!-- Technique Combination -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Technique Combinations</h3>
            <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4 mb-4">
              <h4 class="font-medium text-teal-800 dark:text-teal-300 mb-2">Hybrid Approaches</h4>
              <div class="text-sm text-teal-700 dark:text-teal-400 space-y-2">
                <p><strong>Combined Methods:</strong> Many archers use string walking + gap shooting</p>
                <p><strong>Scenario-Based:</strong> Different techniques for different shooting situations</p>
                <p><strong>Accuracy:</strong> Nearly as accurate as sighted archery when mastered</p>
                <p><strong>Versatility:</strong> Adapt techniques to match conditions</p>
              </div>
            </div>

            <div class="bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
              <h4 class="font-medium text-gray-800 dark:text-gray-200 mb-3">Development Progression</h4>
              <ol class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>1. <strong>Start with gap shooting</strong> (most intuitive)</li>
                <li>2. <strong>Add string walking</strong> for precision</li>
                <li>3. <strong>Develop instinctive feel</strong> for close shots</li>
                <li>4. <strong>Combine techniques</strong> based on situation</li>
              </ol>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Reference -->
      <div class="bg-gradient-to-r from-orange-100 to-orange-50 dark:from-orange-900/30 dark:to-orange-800/20 rounded-lg p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          <i class="fas fa-bookmark mr-2 text-orange-600 dark:text-orange-400"></i>
          Quick Reference Guide
        </h2>
        
        <div class="grid md:grid-cols-3 gap-6">
          <div>
            <h4 class="font-medium text-gray-900 dark:text-white mb-3">Essential Setup</h4>
            <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
              <li>• 25" riser with medium limbs (68" bow)</li>
              <li>• Three-under finger tab with marks</li>
              <li>• Shibuya DX plunger button</li>
              <li>• Fixed weights below grip</li>
              <li>• 1 spine stiffer than OR charts</li>
            </ul>
          </div>
          <div>
            <h4 class="font-medium text-gray-900 dark:text-white mb-3">Arrow Specifications</h4>
            <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
              <li>• Max 9.3mm shaft diameter</li>
              <li>• 100-120 grain points (standard)</li>
              <li>• 10-15% FOC (general shooting)</li>
              <li>• Bare shaft tuning at 18-20m</li>
              <li>• All components tuned together</li>
            </ul>
          </div>
          <div>
            <h4 class="font-medium text-gray-900 dark:text-white mb-3">Aiming Foundation</h4>
            <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
              <li>• Index finger at lip corner anchor</li>
              <li>• Eye aligned with string (windage)</li>
              <li>• Choose string walking OR gap shooting</li>
              <li>• Extensive practice at all distances</li>
              <li>• Consistent shot execution critical</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Page metadata
useHead({
  title: 'Barebow Archery Guide - Archery Tools',
  meta: [
    { name: 'description', content: 'Complete guide to barebow archery equipment, arrow selection, tuning methods, and aiming techniques for competition and recreation.' },
    { name: 'keywords', content: 'barebow archery, string walking, gap shooting, arrow spine, FOC balance, competition archery' }
  ]
})
</script>

<style scoped>
.text-gold-600 {
  color: #d97706;
}

.bg-gold-50 {
  background-color: #fffbeb;
}

@media (prefers-color-scheme: dark) {
  .dark\:bg-yellow-900\/20 {
    background-color: rgb(113 63 18 / 0.2);
  }
}
</style>