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
          <span class="text-gray-900 dark:text-gray-100">Proper Grip & Stance</span>
        </li>
      </ol>
    </nav>

    <!-- Guide Header -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <div class="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-xl mr-4">
          <i class="fas fa-hand-paper text-orange-600 dark:text-orange-400 text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Proper Grip & Stance Guide</h1>
          <p class="text-gray-600 dark:text-gray-300 mt-2">Master the fundamental foundation of accurate archery through proper grip and stance techniques</p>
        </div>
      </div>
      
      <!-- Guide Info -->
      <div class="flex flex-wrap gap-4 text-sm">
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-clock mr-2"></i>
          16 min read
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-layer-group mr-2"></i>
          Beginner to Intermediate
        </span>
        <span class="flex items-center text-gray-600 dark:text-gray-300">
          <i class="fas fa-user mr-2"></i>
          Shooting Technique
        </span>
      </div>
    </div>

    <!-- Table of Contents -->
    <div class="bg-orange-50 dark:bg-orange-900/20 rounded-xl p-6 mb-8 border border-orange-200 dark:border-orange-800">
      <h2 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-4">
        <i class="fas fa-list mr-2"></i>
        Table of Contents
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <a href="#fundamentals" class="text-orange-700 dark:text-orange-300 hover:text-orange-800 dark:hover:text-orange-200 transition-colors">1. Fundamentals of Form</a>
        <a href="#stance" class="text-orange-700 dark:text-orange-300 hover:text-orange-800 dark:hover:text-orange-200 transition-colors">2. Proper Stance</a>
        <a href="#bow-grip" class="text-orange-700 dark:text-orange-300 hover:text-orange-800 dark:hover:text-orange-200 transition-colors">3. Bow Hand Grip</a>
        <a href="#body-alignment" class="text-orange-700 dark:text-orange-300 hover:text-orange-800 dark:hover:text-orange-200 transition-colors">4. Body Alignment</a>
        <a href="#common-mistakes" class="text-orange-700 dark:text-orange-300 hover:text-orange-800 dark:hover:text-orange-200 transition-colors">5. Common Mistakes</a>
        <a href="#practice" class="text-orange-700 dark:text-orange-300 hover:text-orange-800 dark:hover:text-orange-200 transition-colors">6. Practice Techniques</a>
        <a href="#advanced" class="text-orange-700 dark:text-orange-300 hover:text-orange-800 dark:hover:text-orange-200 transition-colors">7. Advanced Concepts</a>
        <a href="#troubleshooting" class="text-orange-700 dark:text-orange-300 hover:text-orange-800 dark:hover:text-orange-200 transition-colors">8. Troubleshooting</a>
      </div>
    </div>

    <!-- Guide Content -->
    <div class="prose prose-lg max-w-none dark:prose-invert">
      
      <!-- Fundamentals of Form -->
      <section id="fundamentals" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-foundation text-blue-500 mr-3"></i>
          Fundamentals of Form
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Proper grip and stance form the foundation of accurate archery. These fundamentals affect every aspect of your shooting, 
            from arrow flight to consistency. Master these basics, and everything else becomes much easier.
          </p>
          
          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-6 border border-blue-200 dark:border-blue-800">
            <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
              <i class="fas fa-lightbulb mr-2"></i>
              Why Form Matters
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">Consistency</h4>
                <p class="text-sm text-blue-700 dark:text-blue-300">
                  Proper form ensures you shoot the same way every time, leading to tight groups and predictable arrow flight.
                </p>
              </div>
              <div>
                <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">Power Transfer</h4>
                <p class="text-sm text-blue-700 dark:text-blue-300">
                  Correct grip and stance maximize energy transfer from bow to arrow, improving speed and penetration.
                </p>
              </div>
              <div>
                <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">Accuracy</h4>
                <p class="text-sm text-blue-700 dark:text-blue-300">
                  Good form eliminates variables that cause erratic arrow flight, allowing you to hit your target more reliably.
                </p>
              </div>
              <div>
                <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">Injury Prevention</h4>
                <p class="text-sm text-blue-700 dark:text-blue-300">
                  Proper form reduces strain on joints and muscles, preventing common archery injuries and fatigue.
                </p>
              </div>
            </div>
          </div>

          <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
            <h3 class="font-semibold text-amber-900 dark:text-amber-100 mb-2">
              <i class="fas fa-clock mr-2"></i>
              Muscle Memory Development
            </h3>
            <p class="text-sm text-amber-800 dark:text-amber-200">
              Developing proper form takes time and repetition. Expect 3-6 months of consistent practice to build solid muscle memory. 
              Be patient with yourself and focus on quality over quantity in your practice sessions.
            </p>
          </div>
        </div>
      </section>

      <!-- Proper Stance -->
      <section id="stance" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-user-circle text-green-500 mr-3"></i>
          Proper Stance
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Your stance provides the stable platform from which all accurate shots are made. 
            There are several stance variations, each with specific advantages.
          </p>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Square Stance -->
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
              <h3 class="font-semibold text-green-900 dark:text-green-100 mb-3">
                <i class="fas fa-square mr-2"></i>
                Square Stance (Recommended for Beginners)
              </h3>
              
              <div class="space-y-3">
                <div class="flex items-start space-x-2">
                  <i class="fas fa-check text-green-600 dark:text-green-400 mt-1"></i>
                  <div>
                    <p class="text-sm text-green-800 dark:text-green-200 font-medium">Foot Position</p>
                    <p class="text-xs text-green-700 dark:text-green-300">
                      Both feet perpendicular to the shooting line, shoulder-width apart
                    </p>
                  </div>
                </div>
                
                <div class="flex items-start space-x-2">
                  <i class="fas fa-check text-green-600 dark:text-green-400 mt-1"></i>
                  <div>
                    <p class="text-sm text-green-800 dark:text-green-200 font-medium">Weight Distribution</p>
                    <p class="text-xs text-green-700 dark:text-green-300">
                      Equal weight on both feet, slightly forward on the balls of feet
                    </p>
                  </div>
                </div>
                
                <div class="flex items-start space-x-2">
                  <i class="fas fa-check text-green-600 dark:text-green-400 mt-1"></i>
                  <div>
                    <p class="text-sm text-green-800 dark:text-green-200 font-medium">Advantages</p>
                    <p class="text-xs text-green-700 dark:text-green-300">
                      Most stable, easy to learn, consistent bone alignment
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Open Stance -->
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                <i class="fas fa-expand-arrows-alt mr-2"></i>
                Open Stance (Advanced)
              </h3>
              
              <div class="space-y-3">
                <div class="flex items-start space-x-2">
                  <i class="fas fa-check text-blue-600 dark:text-blue-400 mt-1"></i>
                  <div>
                    <p class="text-sm text-blue-800 dark:text-blue-200 font-medium">Foot Position</p>
                    <p class="text-xs text-blue-700 dark:text-blue-300">
                      Front foot angled 45° toward target, back foot perpendicular to shooting line
                    </p>
                  </div>
                </div>
                
                <div class="flex items-start space-x-2">
                  <i class="fas fa-check text-blue-600 dark:text-blue-400 mt-1"></i>
                  <div>
                    <p class="text-sm text-blue-800 dark:text-blue-200 font-medium">Body Position</p>
                    <p class="text-xs text-blue-700 dark:text-blue-300">
                      Torso slightly rotated toward target for better clearance
                    </p>
                  </div>
                </div>
                
                <div class="flex items-start space-x-2">
                  <i class="fas fa-check text-blue-600 dark:text-blue-400 mt-1"></i>
                  <div>
                    <p class="text-sm text-blue-800 dark:text-blue-200 font-medium">Advantages</p>
                    <p class="text-xs text-blue-700 dark:text-blue-300">
                      Better string clearance, more natural draw cycle
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">
              <i class="fas fa-ruler mr-2"></i>
              Stance Setup Steps
            </h4>
            <ol class="list-decimal list-inside text-sm text-gray-700 dark:text-gray-300 space-y-1">
              <li>Stand with feet shoulder-width apart</li>
              <li>Position feet according to chosen stance type</li>
              <li>Distribute weight evenly, keep knees slightly bent</li>
              <li>Maintain straight, relaxed posture</li>
              <li>Check that your shooting shoulder aligns over the corresponding hip</li>
            </ol>
          </div>
        </div>
      </section>

      <!-- Bow Hand Grip -->
      <section id="bow-grip" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-hand-holding text-purple-500 mr-3"></i>
          Bow Hand Grip
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            The bow grip is one of the most critical yet misunderstood aspects of archery form. 
            A proper grip allows the bow to jump forward naturally upon release while maintaining accuracy.
          </p>

          <!-- Illustration -->
          <div class="illustration-container mb-6 bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
            <!-- TODO: Add bow grip illustration -->
            <div class="w-full max-w-md mx-auto h-48 bg-orange-100 dark:bg-orange-800 rounded-lg flex items-center justify-center">
              <div class="text-center text-orange-600 dark:text-orange-300">
                <i class="fas fa-image text-4xl mb-2"></i>
                <p class="text-sm">Bow Grip Technique</p>
              </div>
            </div>
            <p class="text-sm text-orange-700 dark:text-orange-300 text-center mt-3">
              <i class="fas fa-hand-paper mr-2"></i>
              Proper grip: Push with palm heel at 45°, keep fingers relaxed
            </p>
          </div>

          <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 mb-6 border border-red-200 dark:border-red-800">
            <h3 class="font-semibold text-red-900 dark:text-red-100 mb-2">
              <i class="fas fa-exclamation-triangle mr-2"></i>
              Critical Concept: Don't Grip the Bow!
            </h3>
            <p class="text-sm text-red-800 dark:text-red-200">
              The bow hand should push against the grip, not squeeze it. Gripping the bow introduces torque 
              and inconsistency. Think "push, don't grab."
            </p>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Proper Grip Technique</h3>
              
              <div class="space-y-4">
                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    1
                  </div>
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Hand Position</h4>
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                      Place the meaty part of your palm (below the thumb) against the grip. 
                      The grip should contact your hand at a 45-degree angle.
                    </p>
                  </div>
                </div>

                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    2
                  </div>
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Thumb Position</h4>
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                      Keep your thumb relaxed and pointing toward the target. 
                      It should not wrap around the grip or press against it.
                    </p>
                  </div>
                </div>

                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    3
                  </div>
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Finger Position</h4>
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                      Fingers should be relaxed and curved naturally. 
                      They can lightly touch the grip but should not grip or squeeze.
                    </p>
                  </div>
                </div>

                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    4
                  </div>
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Pressure Point</h4>
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                      Apply pressure straight back toward your shoulder through the grip. 
                      This creates a stable pushing platform.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Grip Pressure & Wrist Position</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">
                    <i class="fas fa-hand-peace mr-2"></i>
                    Pressure Level
                  </h4>
                  <p class="text-sm text-purple-800 dark:text-purple-200">
                    Use minimal pressure - just enough to keep the bow in your hand. 
                    On a scale of 1-10, aim for a 2-3 in grip pressure.
                  </p>
                </div>

                <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-indigo-900 dark:text-indigo-100 mb-2">
                    <i class="fas fa-arrows-alt-v mr-2"></i>
                    Wrist Alignment
                  </h4>
                  <p class="text-sm text-indigo-800 dark:text-indigo-200">
                    Keep your wrist straight and strong. Avoid bending it up or down, 
                    which creates inconsistent pressure points.
                  </p>
                </div>

                <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-teal-900 dark:text-teal-100 mb-2">
                    <i class="fas fa-crosshairs mr-2"></i>
                    Consistent Contact
                  </h4>
                  <p class="text-sm text-teal-800 dark:text-teal-200">
                    The same part of your hand should contact the grip for every shot. 
                    Mark your grip if needed to ensure consistency.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <h4 class="font-semibold text-green-900 dark:text-green-100 mb-2">
              <i class="fas fa-lightbulb mr-2"></i>
              Pro Tip: The Follow-Through Test
            </h4>
            <p class="text-sm text-green-800 dark:text-green-200">
              A properly held bow will jump forward and slightly rotate upon release. 
              If your bow doesn't move or twists significantly, you're likely gripping too tightly. 
              Use a bow sling to catch the bow safely during practice.
            </p>
          </div>
        </div>
      </section>

      <!-- Body Alignment -->
      <section id="body-alignment" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-align-center text-blue-500 mr-3"></i>
          Body Alignment
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Proper body alignment creates a strong, consistent platform that works with your bow's natural physics rather than against it.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Upper Body Position</h3>
              
              <div class="space-y-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">Shoulder Alignment</h4>
                  <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                    <li>• Keep shoulders level and relaxed</li>
                    <li>• Bow shoulder slightly lower than drawing shoulder</li>
                    <li>• Avoid hunching or rolling shoulders forward</li>
                    <li>• Maintain natural shoulder blade position</li>
                  </ul>
                </div>
                
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">Torso Position</h4>
                  <ul class="text-sm text-green-800 dark:text-green-200 space-y-1">
                    <li>• Stand tall with natural spine curvature</li>
                    <li>• Engage core muscles for stability</li>
                    <li>• Keep chest open and proud</li>
                    <li>• Avoid leaning forward or backward</li>
                  </ul>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Head & Neck Position</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">Head Position</h4>
                  <ul class="text-sm text-purple-800 dark:text-purple-200 space-y-1">
                    <li>• Keep head upright and balanced</li>
                    <li>• Avoid tilting head toward bow arm</li>
                    <li>• Maintain level chin position</li>
                    <li>• Look straight toward target</li>
                  </ul>
                </div>
                
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-900 dark:text-orange-100 mb-2">Eye Dominance</h4>
                  <ul class="text-sm text-orange-800 dark:text-orange-200 space-y-1">
                    <li>• Use your dominant eye for aiming</li>
                    <li>• Keep both eyes open when possible</li>
                    <li>• Adjust head position to align dominant eye</li>
                    <li>• Consider eye patch if cross-dominant</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <h4 class="font-semibold text-amber-900 dark:text-amber-100 mb-2">
              <i class="fas fa-balance-scale mr-2"></i>
              The T-Formation
            </h4>
            <p class="text-sm text-amber-800 dark:text-amber-200">
              When viewed from above, your shoulders should form a straight line perpendicular to the shooting line, 
              creating a "T" shape. This alignment maximizes stability and allows for natural bone-on-bone support 
              throughout the draw cycle.
            </p>
          </div>
        </div>
      </section>

      <!-- Common Mistakes -->
      <section id="common-mistakes" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-exclamation-triangle text-red-500 mr-3"></i>
          Common Mistakes
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Recognizing and correcting these common form errors will dramatically improve your shooting consistency and accuracy.
          </p>

          <div class="space-y-6">
            <!-- Grip Mistakes -->
            <div class="border-l-4 border-red-500 pl-4">
              <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-3">
                <i class="fas fa-hand-rock mr-2"></i>
                Grip-Related Mistakes
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-900 dark:text-red-100 mb-2">Death Grip</h4>
                  <p class="text-sm text-red-800 dark:text-red-200 mb-2">
                    <strong>Problem:</strong> Squeezing the bow handle tightly with fingers wrapped around.
                  </p>
                  <p class="text-sm text-red-700 dark:text-red-300">
                    <strong>Solution:</strong> Relax fingers, push with palm heel, use bow sling for confidence.
                  </p>
                </div>
                
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-red-900 dark:text-red-100 mb-2">Heeling the Bow</h4>
                  <p class="text-sm text-red-800 dark:text-red-200 mb-2">
                    <strong>Problem:</strong> Pushing primarily with the heel of the hand, causing high shots.
                  </p>
                  <p class="text-sm text-red-700 dark:text-red-300">
                    <strong>Solution:</strong> Contact grip with meaty part below thumb, maintain consistent pressure point.
                  </p>
                </div>
              </div>
            </div>

            <!-- Stance Mistakes -->
            <div class="border-l-4 border-orange-500 pl-4">
              <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100 mb-3">
                <i class="fas fa-user-times mr-2"></i>
                Stance-Related Mistakes
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-900 dark:text-orange-100 mb-2">Leaning Into the Bow</h4>
                  <p class="text-sm text-orange-800 dark:text-orange-200 mb-2">
                    <strong>Problem:</strong> Leaning forward to "help" draw the bow, creating instability.
                  </p>
                  <p class="text-sm text-orange-700 dark:text-orange-300">
                    <strong>Solution:</strong> Stand upright, use back muscles to draw, engage core for stability.
                  </p>
                </div>
                
                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-orange-900 dark:text-orange-100 mb-2">Inconsistent Foot Position</h4>
                  <p class="text-sm text-orange-800 dark:text-orange-200 mb-2">
                    <strong>Problem:</strong> Varying foot placement from shot to shot.
                  </p>
                  <p class="text-sm text-orange-700 dark:text-orange-300">
                    <strong>Solution:</strong> Mark foot positions on practice line, develop consistent setup routine.
                  </p>
                </div>
              </div>
            </div>

            <!-- Alignment Mistakes -->
            <div class="border-l-4 border-yellow-500 pl-4">
              <h3 class="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-3">
                <i class="fas fa-exclamation-circle mr-2"></i>
                Alignment Mistakes
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-900 dark:text-yellow-100 mb-2">Canted Bow</h4>
                  <p class="text-sm text-yellow-800 dark:text-yellow-200 mb-2">
                    <strong>Problem:</strong> Tilting the bow left or right, causing horizontal arrow drift.
                  </p>
                  <p class="text-sm text-yellow-700 dark:text-yellow-300">
                    <strong>Solution:</strong> Use a bow square or level, practice with reference lines, check grip pressure.
                  </p>
                </div>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-yellow-900 dark:text-yellow-100 mb-2">Shoulder Rotation</h4>
                  <p class="text-sm text-yellow-800 dark:text-yellow-200 mb-2">
                    <strong>Problem:</strong> Rotating shoulders out of alignment during draw or at full draw.
                  </p>
                  <p class="text-sm text-yellow-700 dark:text-yellow-300">
                    <strong>Solution:</strong> Maintain square shoulders to target, use mirror for form checks.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Practice Techniques -->
      <section id="practice" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-target text-green-500 mr-3"></i>
          Practice Techniques
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Developing proper grip and stance requires deliberate practice with specific techniques designed to build muscle memory and consistency.
          </p>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Form Development Drills</h3>
              
              <div class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
                  <h4 class="font-medium text-green-900 dark:text-green-100 mb-2">
                    <i class="fas fa-mirror mr-2"></i>
                    Mirror Practice
                  </h4>
                  <p class="text-sm text-green-800 dark:text-green-200 mb-2">
                    Practice your stance and grip setup in front of a mirror without drawing the bow.
                  </p>
                  <ul class="text-xs text-green-700 dark:text-green-300 space-y-1">
                    <li>• Check foot position and weight distribution</li>
                    <li>• Verify shoulder alignment and posture</li>
                    <li>• Practice consistent grip placement</li>
                    <li>• Perform 10-15 repetitions daily</li>
                  </ul>
                </div>

                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                  <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">
                    <i class="fas fa-hand-paper mr-2"></i>
                    Grip Pressure Training
                  </h4>
                  <p class="text-sm text-blue-800 dark:text-blue-200 mb-2">
                    Practice finding the minimal grip pressure needed to control the bow.
                  </p>
                  <ul class="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                    <li>• Start with normal grip, gradually lighten pressure</li>
                    <li>• Use a bow sling to catch the bow</li>
                    <li>• Focus on pushing, not gripping</li>
                    <li>• Practice blank bale shooting</li>
                  </ul>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Consistency Building</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
                  <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">
                    <i class="fas fa-redo mr-2"></i>
                    Setup Routine
                  </h4>
                  <p class="text-sm text-purple-800 dark:text-purple-200 mb-2">
                    Develop a consistent pre-shot routine that includes stance and grip setup.
                  </p>
                  <ol class="text-xs text-purple-700 dark:text-purple-300 space-y-1 list-decimal list-inside">
                    <li>Approach shooting line</li>
                    <li>Set feet in consistent position</li>
                    <li>Check posture and alignment</li>
                    <li>Establish proper grip</li>
                    <li>Take a centering breath</li>
                  </ol>
                </div>

                <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
                  <h4 class="font-medium text-orange-900 dark:text-orange-100 mb-2">
                    <i class="fas fa-video mr-2"></i>
                    Video Analysis
                  </h4>
                  <p class="text-sm text-orange-800 dark:text-orange-200 mb-2">
                    Record yourself shooting from multiple angles to identify form issues.
                  </p>
                  <ul class="text-xs text-orange-700 dark:text-orange-300 space-y-1">
                    <li>• Side view: Check grip and bow cant</li>
                    <li>• Behind view: Verify shoulder alignment</li>
                    <li>• Front view: Check stance and posture</li>
                    <li>• Compare with professional form videos</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <h4 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-2">
              <i class="fas fa-chart-line mr-2"></i>
              Progressive Training Plan
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
              <div>
                <h5 class="font-medium text-indigo-800 dark:text-indigo-200 mb-1">Week 1-2: Foundation</h5>
                <p class="text-xs text-indigo-700 dark:text-indigo-300">
                  Focus on stance setup and basic grip. Practice without shooting arrows.
                </p>
              </div>
              <div>
                <h5 class="font-medium text-indigo-800 dark:text-indigo-200 mb-1">Week 3-4: Integration</h5>
                <p class="text-xs text-indigo-700 dark:text-indigo-300">
                  Begin shooting at close range, focusing on form over accuracy.
                </p>
              </div>
              <div>
                <h5 class="font-medium text-indigo-800 dark:text-indigo-200 mb-1">Week 5+: Refinement</h5>
                <p class="text-xs text-indigo-700 dark:text-indigo-300">
                  Fine-tune details and build consistent muscle memory.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Advanced Concepts -->
      <section id="advanced" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-graduation-cap text-indigo-500 mr-3"></i>
          Advanced Concepts
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Once you've mastered the basics, these advanced concepts will help you achieve expert-level consistency and performance.
          </p>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Biomechanical Optimization</h3>
              
              <div class="space-y-4">
                <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-indigo-900 dark:text-indigo-100 mb-2">
                    <i class="fas fa-bone mr-2"></i>
                    Bone-on-Bone Alignment
                  </h4>
                  <p class="text-sm text-indigo-800 dark:text-indigo-200">
                    Align your skeletal structure to support the bow's forces naturally. 
                    This reduces muscle fatigue and improves consistency over long shooting sessions.
                  </p>
                </div>

                <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-teal-900 dark:text-teal-100 mb-2">
                    <i class="fas fa-balance-scale mr-2"></i>
                    Dynamic Balance
                  </h4>
                  <p class="text-sm text-teal-800 dark:text-teal-200">
                    Learn to maintain balance throughout the shot cycle, even when external conditions change. 
                    Practice shooting in wind or on uneven terrain.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Mental Game Integration</h3>
              
              <div class="space-y-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-purple-900 dark:text-purple-100 mb-2">
                    <i class="fas fa-brain mr-2"></i>
                    Subconscious Competence
                  </h4>
                  <p class="text-sm text-purple-800 dark:text-purple-200">
                    Train until proper form becomes automatic. This allows your conscious mind to focus on 
                    aiming and shot execution rather than body position.
                  </p>
                </div>

                <div class="bg-pink-50 dark:bg-pink-900/20 rounded-lg p-4">
                  <h4 class="font-medium text-pink-900 dark:text-pink-100 mb-2">
                    <i class="fas fa-meditation mr-2"></i>
                    Feel vs. Real
                  </h4>
                  <p class="text-sm text-pink-800 dark:text-pink-200">
                    What feels "right" may not always be correct form. Use video analysis and coaching 
                    to verify that your sensations match proper technique.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <h4 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-2">
              <i class="fas fa-trophy mr-2"></i>
              Competition Considerations
            </h4>
            <p class="text-sm text-indigo-800 dark:text-indigo-200 mb-3">
              In high-pressure situations, your form may deteriorate without conscious attention. 
              Elite archers develop specific pre-shot routines that reinforce proper grip and stance even under stress.
            </p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="bg-white dark:bg-gray-800 rounded-lg p-3">
                <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Stress Response Training</h5>
                <p class="text-xs text-gray-600 dark:text-gray-400">
                  Practice proper form while experiencing elevated heart rate or distractions.
                </p>
              </div>
              <div class="bg-white dark:bg-gray-800 rounded-lg p-3">
                <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Routine Reinforcement</h5>
                <p class="text-xs text-gray-600 dark:text-gray-400">
                  Develop checkpoint systems within your shot process to verify form.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Troubleshooting -->
      <section id="troubleshooting" class="mb-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
          <i class="fas fa-wrench text-yellow-500 mr-3"></i>
          Troubleshooting Form Issues
        </h2>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Use these diagnostic techniques to identify and correct specific form problems affecting your shooting.
          </p>

          <div class="space-y-6">
            <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
              <h3 class="font-semibold text-yellow-900 dark:text-yellow-100 mb-3">
                <i class="fas fa-search mr-2"></i>
                Problem: Consistent Left/Right Misses
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-200 mb-2">Likely Causes:</h4>
                  <ul class="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                    <li>• Bow cant (tilting left or right)</li>
                    <li>• Inconsistent grip pressure</li>
                    <li>• Torquing the grip during draw</li>
                    <li>• Shoulder alignment issues</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-yellow-800 dark:text-yellow-200 mb-2">Solutions:</h4>
                  <ul class="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                    <li>• Use a bow level to check cant</li>
                    <li>• Practice grip consistency drills</li>
                    <li>• Check hand position on grip</li>
                    <li>• Verify square stance to target</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
              <h3 class="font-semibold text-red-900 dark:text-red-100 mb-3">
                <i class="fas fa-arrows-alt-v mr-2"></i>
                Problem: Consistent High/Low Misses
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Likely Causes:</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Heeling or fingering the bow</li>
                    <li>• Inconsistent anchor point</li>
                    <li>• Grip pressure variations</li>
                    <li>• Form breakdown under fatigue</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">Solutions:</h4>
                  <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• Verify consistent grip contact point</li>
                    <li>• Practice anchor point consistency</li>
                    <li>• Reduce shooting volume if fatigued</li>
                    <li>• Use consistent grip pressure</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                <i class="fas fa-expand mr-2"></i>
                Problem: Large, Inconsistent Groups
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">Likely Causes:</h4>
                  <ul class="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                    <li>• Inconsistent stance setup</li>
                    <li>• Variable grip pressure</li>
                    <li>• Poor shot-to-shot routine</li>
                    <li>• Multiple form issues present</li>
                  </ul>
                </div>
                <div>
                  <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">Solutions:</h4>
                  <ul class="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                    <li>• Focus on one form element at a time</li>
                    <li>• Develop strict pre-shot routine</li>
                    <li>• Practice blank bale shooting</li>
                    <li>• Consider professional coaching</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <h4 class="font-semibold text-green-900 dark:text-green-100 mb-2">
              <i class="fas fa-lightbulb mr-2"></i>
              Diagnostic Shooting Exercise
            </h4>
            <p class="text-sm text-green-800 dark:text-green-200 mb-3">
              Shoot groups of arrows while deliberately focusing on just one form element at a time:
            </p>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div class="bg-white dark:bg-gray-800 rounded-lg p-3">
                <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Round 1</h5>
                <p class="text-xs text-gray-600 dark:text-gray-400">Focus only on stance</p>
              </div>
              <div class="bg-white dark:bg-gray-800 rounded-lg p-3">
                <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Round 2</h5>
                <p class="text-xs text-gray-600 dark:text-gray-400">Focus only on grip</p>
              </div>
              <div class="bg-white dark:bg-gray-800 rounded-lg p-3">
                <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Round 3</h5>
                <p class="text-xs text-gray-600 dark:text-gray-400">Focus on alignment</p>
              </div>
              <div class="bg-white dark:bg-gray-800 rounded-lg p-3">
                <h5 class="font-medium text-gray-900 dark:text-gray-100 mb-1">Round 4</h5>
                <p class="text-xs text-gray-600 dark:text-gray-400">Integrate all elements</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Conclusion & Next Steps -->
      <section class="mb-12">
        <div class="bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-xl p-6 border border-orange-200 dark:border-orange-800">
          <h2 class="text-2xl font-bold text-orange-900 dark:text-orange-100 mb-4">
            <i class="fas fa-trophy mr-3"></i>
            Building Your Foundation
          </h2>
          <p class="text-orange-800 dark:text-orange-200 mb-4">
            Proper grip and stance are the bedrock of accurate archery. While these fundamentals may seem simple, 
            they require consistent practice and attention to detail. Remember that even Olympic archers regularly 
            return to these basics to maintain their edge.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-orange-200 dark:border-orange-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Key Success Factors</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Patience with the learning process</li>
                <li>• Consistent practice schedule</li>
                <li>• Focus on quality over quantity</li>
                <li>• Regular form self-assessment</li>
              </ul>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-orange-200 dark:border-orange-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Next Steps</h3>
              <ul class="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>• Master basic grip and stance first</li>
                <li>• Progress to aiming and release techniques</li>
                <li>• Integrate all fundamentals gradually</li>
                <li>• Seek coaching for personalized feedback</li>
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
            to="/guides/draw-length"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-colors group"
          >
            <div class="flex items-center mb-2">
              <i class="fas fa-ruler text-blue-600 dark:text-blue-400 mr-3"></i>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                Draw Length Measurement
              </h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Learn proper techniques for measuring your draw length accurately.
            </p>
          </NuxtLink>

          <div class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 opacity-60">
            <div class="flex items-center mb-2">
              <i class="fas fa-eye text-gray-400 mr-3"></i>
              <h3 class="font-semibold text-gray-500 dark:text-gray-400">
                Aiming Techniques
              </h3>
            </div>
            <p class="text-sm text-gray-400">
              Coming soon - Master different aiming methods for consistent accuracy.
            </p>
          </div>

          <div class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 opacity-60">
            <div class="flex items-center mb-2">
              <i class="fas fa-hand-point-up text-gray-400 mr-3"></i>
              <h3 class="font-semibold text-gray-500 dark:text-gray-400">
                Release Techniques
              </h3>
            </div>
            <p class="text-sm text-gray-400">
              Coming soon - Perfect your release for clean arrow departure.
            </p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
// Set page title and meta
useHead({
  title: 'Proper Grip & Stance Guide - Master Archery Fundamentals',
  meta: [
    { name: 'description', content: 'Master the fundamentals of archery with our comprehensive guide to proper grip and stance. Build a solid foundation for accurate shooting.' }
  ]
})

// Protect this page with authentication
definePageMeta({
  middleware: ['auth-check']
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