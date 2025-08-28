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
          <span class="text-gray-900 dark:text-gray-100">Equipment Maintenance</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl mr-4">
          <i class="fas fa-tools text-purple-600 dark:text-purple-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Equipment Maintenance Guide</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">Keep your archery equipment in peak condition with proper care and maintenance routines</p>
        </div>
      </div>
      
      <!-- Guide Info -->
      <div class="flex flex-wrap gap-4 text-sm">
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-clock mr-2"></i>
          20 min read
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-layer-group mr-2"></i>
          Beginner to Intermediate
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-cogs mr-2"></i>
          Tuning & Maintenance
        </span>
      </div>
    </div>

    <!-- Table of Contents -->
    <div class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-6 mb-8 border border-purple-200 dark:border-purple-800">
      <h2 class="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#maintenance-basics" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">1. Maintenance Basics</a>
        <a href="#bow-maintenance" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">2. Bow Care & Inspection</a>
        <a href="#string-maintenance" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">3. String & Cable Care</a>
        <a href="#arrow-maintenance" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">4. Arrow Maintenance</a>
        <a href="#accessories-care" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">5. Accessories & Components</a>
        <a href="#storage-transport" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">6. Storage & Transport</a>
        <a href="#troubleshooting" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">7. Troubleshooting Issues</a>
        <a href="#maintenance-schedule" class="text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 transition-colors">8. Maintenance Schedule</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- Maintenance Basics -->
      <section id="maintenance-basics" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-info-circle text-blue-500 mr-3"></i>
          Equipment Maintenance Fundamentals
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Proper equipment maintenance is essential for safety, performance, and longevity. Regular 
            inspection and care prevent equipment failures, maintain accuracy, and protect your investment. 
            A well-maintained bow performs consistently and safely for years.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                <i class="fas fa-shield-alt mr-2"></i>
                Safety Benefits
              </h3>
              <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                <li>• Prevents catastrophic equipment failure</li>
                <li>• Identifies wear before it becomes dangerous</li>
                <li>• Maintains structural integrity</li>
                <li>• Ensures proper component function</li>
                <li>• Reduces risk of injury</li>
                <li>• Maintains warranty coverage</li>
              </ul>
            </div>
            
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                <i class="fas fa-chart-line mr-2"></i>
                Performance Benefits
              </h3>
              <ul class="text-sm text-green-800 dark:text-green-200 space-y-2">
                <li>• Maintains consistent accuracy</li>
                <li>• Preserves optimal tuning</li>
                <li>• Extends equipment lifespan</li>
                <li>• Prevents performance degradation</li>
                <li>• Reduces unexpected failures</li>
                <li>• Maintains resale value</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Warning Box -->
        <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 mb-6">
          <div class="flex items-start">
            <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 text-xl mt-1 mr-3"></i>
            <div>
              <h3 class="font-semibold text-red-900 dark:text-red-100 mb-2">Critical Safety Note</h3>
              <p class="text-red-800 dark:text-red-200 text-sm">
                Never shoot a bow with damaged strings, cracks in limbs, or loose components. When in doubt, 
                have your equipment inspected by a qualified technician. Equipment failure can cause serious injury.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Bow Maintenance -->
      <section id="bow-maintenance" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-grip-horizontal text-green-500 mr-3"></i>
          Bow Care & Inspection
        </h2>

        <div class="space-y-6">
          <!-- Compound Bow Care -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-cog mr-2"></i>
              Compound Bow Maintenance
            </h3>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Daily Inspection</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2 mb-4">
                  <li>• Check cam alignment and timing marks</li>
                  <li>• Inspect strings and cables for fraying</li>
                  <li>• Verify all screws are tight</li>
                  <li>• Check arrow rest alignment</li>
                  <li>• Examine sight mounting security</li>
                </ul>
                
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Weekly Maintenance</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                  <li>• Wax strings and cables</li>
                  <li>• Check cam lean and rotation</li>
                  <li>• Inspect limb pockets for cracks</li>
                  <li>• Verify rest timing and clearance</li>
                  <li>• Clean and lubricate moving parts</li>
                </ul>
              </div>
              
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Signs of Problems</h4>
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <ul class="text-sm text-orange-800 dark:text-orange-200 space-y-2">
                    <li>• Strings touching cam or limbs</li>
                    <li>• Uneven cam timing or lean</li>
                    <li>• Loose or missing screws</li>
                    <li>• Cracks in limbs or riser</li>
                    <li>• Excessive string wear or serving separation</li>
                    <li>• Unusual noise during draw or shot</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Recurve Bow Care -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-expand-arrows-alt mr-2"></i>
              Recurve Bow Maintenance
            </h3>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Regular Inspection</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2 mb-4">
                  <li>• Examine limb tips for damage</li>
                  <li>• Check riser for cracks or stress marks</li>
                  <li>• Inspect string grooves and nocking points</li>
                  <li>• Verify limb attachment security</li>
                  <li>• Check sight and rest mounting</li>
                </ul>
                
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Limb Care</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                  <li>• Store unstrung when not in use</li>
                  <li>• Avoid temperature extremes</li>
                  <li>• Clean with damp cloth only</li>
                  <li>• Check tiller measurement regularly</li>
                  <li>• Inspect for delamination</li>
                </ul>
              </div>
              
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Wood Bow Specific Care</h4>
                <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
                  <ul class="text-sm text-amber-800 dark:text-amber-200 space-y-2">
                    <li>• Apply appropriate wood finish annually</li>
                    <li>• Store in stable humidity environment</li>
                    <li>• Avoid prolonged direct sunlight</li>
                    <li>• Check for grain separation or cracks</li>
                    <li>• Use only appropriate cleaners</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- String Maintenance -->
      <section id="string-maintenance" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-link text-red-500 mr-3"></i>
          String & Cable Care
        </h2>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Bowstrings are your bow's most critical consumable component. Proper string maintenance 
            ensures consistent performance and prevents dangerous failures. Replace strings before 
            they show signs of significant wear.
          </p>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                <i class="fas fa-spa mr-2"></i>
                String Waxing Procedure
              </h3>
              
              <div class="space-y-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-semibold text-blue-900 dark:text-blue-100 mb-2">Step-by-Step Process</h4>
                  <ol class="text-sm text-blue-800 dark:text-blue-200 space-y-2 list-decimal list-inside">
                    <li>Clean string with soft cloth</li>
                    <li>Apply thin layer of string wax</li>
                    <li>Work wax in with fingers or leather</li>
                    <li>Remove excess wax buildup</li>
                    <li>Check serving areas carefully</li>
                    <li>Wax every 100-150 shots or weekly</li>
                  </ol>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-semibold text-yellow-900 dark:text-yellow-100 mb-2">Waxing Tips</h4>
                  <ul class="text-sm text-yellow-800 dark:text-yellow-200 space-y-2">
                    <li>• Use only bowstring-specific wax</li>
                    <li>• Don't wax serving areas</li>
                    <li>• Work wax in thoroughly</li>
                    <li>• Remove old wax buildup periodically</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                <i class="fas fa-search mr-2"></i>
                String Inspection Guide
              </h3>
              
              <div class="space-y-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-semibold text-red-900 dark:text-red-100 mb-2">Replace Immediately If:</h4>
                  <ul class="text-sm text-red-800 dark:text-red-200 space-y-2">
                    <li>• Any broken strands visible</li>
                    <li>• Fraying at loops or nocking point</li>
                    <li>• Serving separation or unwinding</li>
                    <li>• Excessive stretch or length change</li>
                    <li>• Discoloration from heat damage</li>
                  </ul>
                </div>
                
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-semibold text-orange-900 dark:text-orange-100 mb-2">Monitor Closely:</h4>
                  <ul class="text-sm text-orange-800 dark:text-orange-200 space-y-2">
                    <li>• Fuzzing of string material</li>
                    <li>• Minor serving movement</li>
                    <li>• String stretch over time</li>
                    <li>• Loop wear at cam contact points</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Arrow Maintenance -->
      <section id="arrow-maintenance" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-location-arrow text-yellow-500 mr-3"></i>
          Arrow Maintenance
        </h2>

        <div class="space-y-6">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  <i class="fas fa-search-plus mr-2"></i>
                  Arrow Inspection
                </h3>
                
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Before Every Use</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2 mb-4">
                  <li>• Spin test for straightness</li>
                  <li>• Check nock alignment and security</li>
                  <li>• Inspect point/insert attachment</li>
                  <li>• Examine fletching condition</li>
                  <li>• Look for cracks or damage</li>
                </ul>
                
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Carbon Arrow Specific</h4>
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                    <li>• Never shoot cracked carbon arrows</li>
                    <li>• Check for splintering or delamination</li>
                    <li>• Inspect insert bonding</li>
                    <li>• Look for impact damage</li>
                  </ul>
                </div>
              </div>
              
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  <i class="fas fa-tools mr-2"></i>
                  Arrow Maintenance Tasks
                </h3>
                
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Regular Maintenance</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2 mb-4">
                  <li>• Clean shafts with mild soap</li>
                  <li>• Re-fletch as needed</li>
                  <li>• Replace worn nocks</li>
                  <li>• Tighten loose points</li>
                  <li>• Check spine groupings</li>
                </ul>
                
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Professional Services</h4>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                    <li>• Spine and weight matching</li>
                    <li>• Professional fletching</li>
                    <li>• Point installation and alignment</li>
                    <li>• Straightening bent arrows</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Accessories Care -->
      <section id="accessories-care" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-puzzle-piece text-indigo-500 mr-3"></i>
          Accessories & Components
        </h2>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Sight Maintenance -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-crosshairs mr-2"></i>
              Sight Maintenance
            </h3>
            
            <div class="space-y-4">
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-2">Regular Care</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                  <li>• Clean lenses with appropriate cleaner</li>
                  <li>• Check mounting screw tightness</li>
                  <li>• Lubricate adjustment mechanisms</li>
                  <li>• Protect from impact damage</li>
                  <li>• Store in protective case</li>
                </ul>
              </div>
              
              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h4 class="font-semibold text-blue-900 dark:text-blue-100 mb-2">Fiber Optic Care</h4>
                <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                  <li>• Replace damaged fibers promptly</li>
                  <li>• Keep fiber ends clean</li>
                  <li>• Avoid bending fibers sharply</li>
                  <li>• Use protective guards</li>
                </ul>
              </div>
            </div>
          </div>
          
          <!-- Rest Maintenance -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-grip-lines mr-2"></i>
              Rest Maintenance
            </h3>
            
            <div class="space-y-4">
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-2">Drop-Away Rests</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                  <li>• Check cord condition regularly</li>
                  <li>• Lubricate pivot points</li>
                  <li>• Verify timing consistency</li>
                  <li>• Replace wear components</li>
                  <li>• Keep mechanisms clean</li>
                </ul>
              </div>
              
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 class="font-semibold text-green-900 dark:text-green-100 mb-2">Containment Rests</h4>
                <ul class="text-sm text-green-800 dark:text-green-200 space-y-2">
                  <li>• Check launcher wear</li>
                  <li>• Verify containment arms</li>
                  <li>• Clean debris regularly</li>
                  <li>• Monitor adjustment stability</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Storage & Transport -->
      <section id="storage-transport" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-archive text-teal-500 mr-3"></i>
          Storage & Transport
        </h2>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-home mr-2"></i>
              Long-Term Storage
            </h3>
            
            <div class="space-y-4">
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-2">Compound Bows</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                  <li>• Store at partial draw weight if possible</li>
                  <li>• Keep in climate-controlled environment</li>
                  <li>• Use protective case or cover</li>
                  <li>• Avoid leaning against walls</li>
                  <li>• Store vertically when possible</li>
                </ul>
              </div>
              
              <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
                <h4 class="font-semibold text-amber-900 dark:text-amber-100 mb-2">Recurve Bows</h4>
                <ul class="text-sm text-amber-800 dark:text-amber-200 space-y-2">
                  <li>• Always unstring for storage</li>
                  <li>• Store limbs flat or hanging</li>
                  <li>• Maintain stable humidity</li>
                  <li>• Avoid temperature extremes</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <i class="fas fa-truck mr-2"></i>
              Transport Guidelines
            </h3>
            
            <div class="space-y-4">
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-2">Travel Preparation</h4>
                <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                  <li>• Use proper bow case or bag</li>
                  <li>• Secure all loose components</li>
                  <li>• Remove or protect sight pins</li>
                  <li>• Pack arrows separately</li>
                  <li>• Include basic tools</li>
                </ul>
              </div>
              
              <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                <h4 class="font-semibold text-red-900 dark:text-red-100 mb-2">Air Travel Considerations</h4>
                <ul class="text-sm text-red-800 dark:text-red-200 space-y-2">
                  <li>• Check airline regulations</li>
                  <li>• Use TSA-approved locks</li>
                  <li>• Declare at check-in</li>
                  <li>• Consider shipping valuable equipment</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Troubleshooting -->
      <section id="troubleshooting" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-wrench text-orange-500 mr-3"></i>
          Troubleshooting Common Issues
        </h2>

        <div class="space-y-6">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Performance Issues</h3>
                
                <div class="space-y-4">
                  <div class="border-l-4 border-red-400 pl-4">
                    <h4 class="font-semibold text-red-800 dark:text-red-200 mb-2">Loss of Accuracy</h4>
                    <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                      <li>• Check string condition and waxing</li>
                      <li>• Verify sight tightness</li>
                      <li>• Inspect arrow rest alignment</li>
                      <li>• Confirm nocking point position</li>
                    </ul>
                  </div>
                  
                  <div class="border-l-4 border-orange-400 pl-4">
                    <h4 class="font-semibold text-orange-800 dark:text-orange-200 mb-2">Unusual Noise</h4>
                    <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                      <li>• Lubricate cam bearings</li>
                      <li>• Check for string slapping</li>
                      <li>• Tighten loose components</li>
                      <li>• Inspect stabilizer mounting</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Mechanical Problems</h3>
                
                <div class="space-y-4">
                  <div class="border-l-4 border-blue-400 pl-4">
                    <h4 class="font-semibold text-blue-800 dark:text-blue-200 mb-2">Cam Timing Issues</h4>
                    <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                      <li>• Check cable condition</li>
                      <li>• Verify cam lean alignment</li>
                      <li>• Inspect timing marks</li>
                      <li>• Consider professional service</li>
                    </ul>
                  </div>
                  
                  <div class="border-l-4 border-green-400 pl-4">
                    <h4 class="font-semibold text-green-800 dark:text-green-200 mb-2">Rest Malfunction</h4>
                    <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                      <li>• Clean and lubricate mechanisms</li>
                      <li>• Check cord/cable connections</li>
                      <li>• Verify timing adjustment</li>
                      <li>• Replace worn components</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Maintenance Schedule -->
      <section id="maintenance-schedule" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-calendar-alt text-purple-500 mr-3"></i>
          Maintenance Schedule
        </h2>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div>
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                  <i class="fas fa-daily mr-2"></i>
                  Before Each Session
                </h3>
                <ul class="text-sm text-green-800 dark:text-green-200 space-y-2">
                  <li>• Visual equipment inspection</li>
                  <li>• Arrow condition check</li>
                  <li>• String/cable examination</li>
                  <li>• Sight and rest verification</li>
                  <li>• Safety equipment check</li>
                </ul>
              </div>
            </div>
            
            <div>
              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                  <i class="fas fa-weekly mr-2"></i>
                  Weekly/Monthly
                </h3>
                <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                  <li>• String and cable waxing</li>
                  <li>• Detailed component inspection</li>
                  <li>• Screw tightness check</li>
                  <li>• Cleaning and lubrication</li>
                  <li>• Performance verification</li>
                </ul>
              </div>
            </div>
            
            <div>
              <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
                  <i class="fas fa-annually mr-2"></i>
                  Annual Service
                </h3>
                <ul class="text-sm text-purple-800 dark:text-purple-200 space-y-2">
                  <li>• Professional tune-up</li>
                  <li>• String/cable replacement</li>
                  <li>• Comprehensive safety inspection</li>
                  <li>• Cam bearing service</li>
                  <li>• Deep cleaning and maintenance</li>
                </ul>
              </div>
            </div>
          </div>
          
          <!-- Maintenance Log -->
          <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">
              <i class="fas fa-clipboard-list mr-2"></i>
              Keep a Maintenance Log
            </h3>
            <p class="text-sm text-gray-700 dark:text-gray-300">
              Document all maintenance activities, component replacements, and performance observations. 
              This helps track equipment lifecycle, identify patterns, and maintain warranty coverage.
            </p>
          </div>
        </div>
      </section>

      <!-- Conclusion -->
      <section class="mb-12">
        <div class="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
          <h2 class="text-xl font-bold text-purple-900 dark:text-purple-100 mb-4">
            <i class="fas fa-trophy mr-2"></i>
            Maintenance Excellence
          </h2>
          <p class="text-purple-800 dark:text-purple-200 mb-4">
            Consistent equipment maintenance is an investment in safety, performance, and longevity. 
            Well-maintained equipment not only performs better but also retains its value and provides 
            years of reliable service.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex items-center text-sm text-purple-700 dark:text-purple-300">
              <i class="fas fa-shield-alt text-purple-500 mr-3"></i>
              Regular maintenance prevents dangerous failures
            </div>
            <div class="flex items-center text-sm text-purple-700 dark:text-purple-300">
              <i class="fas fa-bullseye text-purple-500 mr-3"></i>
              Maintains consistent accuracy and performance
            </div>
            <div class="flex items-center text-sm text-purple-700 dark:text-purple-300">
              <i class="fas fa-clock text-purple-500 mr-3"></i>
              Extends equipment lifespan significantly
            </div>
            <div class="flex items-center text-sm text-purple-700 dark:text-purple-300">
              <i class="fas fa-dollar-sign text-purple-500 mr-3"></i>
              Protects your equipment investment
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
// Set page title and meta
useHead({
  title: 'Equipment Maintenance Guide - Archery Tools',
  meta: [
    { name: 'description', content: 'Comprehensive guide to maintaining archery equipment including bows, strings, arrows, and accessories for optimal performance and safety.' },
    { name: 'keywords', content: 'archery equipment maintenance, bow care, string maintenance, arrow inspection, equipment service, archery safety' }
  ]
})

// Middleware for authentication
definePageMeta({
  middleware: ['auth-check']
})

// Smooth scroll for anchor links
onMounted(() => {
  const links = document.querySelectorAll('a[href^="#"]')
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault()
      const target = document.querySelector(link.getAttribute('href'))
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    })
  })
})
</script>