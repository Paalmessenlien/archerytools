<template>
  <div class="space-y-4">
    <!-- Performance Metrics Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <!-- Speed -->
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 sm:p-4 border border-blue-200 dark:border-blue-800">
        <div class="flex items-center justify-between mb-2">
          <div class="text-lg font-bold text-blue-600 dark:text-blue-400">
            {{ formatSpeedValue(metrics.estimatedSpeed || metrics.estimated_speed_fps) }}
          </div>
          <PerformanceTooltip 
            :title="'Arrow Speed'"
            :content="'Estimated arrow velocity in feet per second.\n\nCalculation Formula:\nSpeed = (IBO_Speed + Draw_Weight_Adj + Draw_Length_Adj) × √(350/Arrow_Weight) × String_Modifier × Bow_Efficiency\n\nWhere:\n• Draw_Weight_Adj = (Draw_Weight - Ref_Weight) × 2.5\n• Draw_Length_Adj = (Draw_Length - Ref_Length) × 10\n• Bow_Efficiency: Compound(95%), Recurve(90%), Longbow(88%)\n\nTypical hunting speeds: 250-350 fps.'"
          />
        </div>
        <div class="text-sm text-blue-800 dark:text-blue-200 font-medium">Speed</div>
        <div class="text-xs text-blue-600 dark:text-blue-400 mt-1">
          {{ getSpeedRating(metrics.estimatedSpeed || metrics.estimated_speed_fps) }}
        </div>
        <!-- Speed Source & Confidence Indicator -->
        <div v-if="metrics.speedSource || metrics.speed_source" class="flex items-center justify-between mt-2">
          <div class="flex items-center">
            <span class="text-xs px-2 py-1 rounded-full" :class="getSpeedSourceClass(metrics.speedSource || metrics.speed_source)">
              <i :class="getSpeedSourceIcon(metrics.speedSource || metrics.speed_source)" class="mr-1"></i>
              {{ getSpeedSourceText(metrics.speedSource || metrics.speed_source) }}
            </span>
          </div>
          <div v-if="metrics.confidence" class="text-xs text-blue-600 dark:text-blue-400">
            {{ metrics.confidence }}% confidence
          </div>
        </div>
      </div>
      
      <!-- Kinetic Energy -->
      <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 sm:p-4 border border-green-200 dark:border-green-800">
        <div class="flex items-center justify-between mb-2">
          <div class="text-lg font-bold text-green-600 dark:text-green-400">
            {{ formatKineticEnergy(metrics.kineticEnergy || metrics.kinetic_energy_40yd || (metrics.kineticEnergy * 0.77)) }}
          </div>
          <PerformanceTooltip 
            :title="'Kinetic Energy at 40 Yards'"
            :content="'Energy remaining after 40 yards of flight. Determines penetration power.\n\nCalculation Formula:\nKE = 0.5 × Mass × Velocity²\nKE_40yd = KE_Initial × Retention_Factor\n\nWhere:\n• Mass = Arrow_Weight ÷ 7000 (grains to pounds)\n• Velocity = Arrow_Speed (fps)\n• Retention_Factor ≈ 0.77 (typical energy retention at 40 yards)\n\nStandards:\n• 25+ ft·lbs (small game)\n• 40+ ft·lbs (deer)\n• 65+ ft·lbs (elk)'"
          />
        </div>
        <div class="text-sm text-green-800 dark:text-green-200 font-medium">KE @40yd</div>
        <div class="text-xs text-green-600 dark:text-green-400 mt-1">
          {{ getKineticEnergyRating(metrics.kineticEnergy || metrics.kinetic_energy_40yd || (metrics.kineticEnergy * 0.77)) }}
        </div>
      </div>
      
      <!-- FOC -->
      <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 sm:p-4 border border-purple-200 dark:border-purple-800">
        <div class="flex items-center justify-between mb-2">
          <div class="text-lg font-bold text-purple-600 dark:text-purple-400">
            {{ formatFocPercentage(metrics.foc || metrics.foc_percentage) }}
          </div>
          <PerformanceTooltip 
            :title="'Front of Center (FOC)'"
            :content="'How much weight is forward of the arrow center. Higher FOC improves stability and penetration.\n\nCalculation Formula:\nFOC = ((Balance_Point - Arrow_Center) ÷ Arrow_Length) × 100\n\nWhere:\n• Balance_Point = Center of mass location from nock\n• Arrow_Center = Arrow_Length ÷ 2\n• Influenced by point weight, insert weight, and shaft distribution\n\nRecommended ranges:\n• 10-15% (target shooting)\n• 15-20% (hunting)'"
          />
        </div>
        <div class="text-sm text-purple-800 dark:text-purple-200 font-medium">FOC</div>
        <div class="text-xs text-purple-600 dark:text-purple-400 mt-1">
          {{ getFOCRating(metrics.foc || metrics.foc_percentage) }}
        </div>
      </div>
      
      <!-- Performance Score or Penetration -->
      <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3 sm:p-4 border border-orange-200 dark:border-orange-800">
        <div class="flex items-center justify-between mb-2">
          <div v-if="metrics.performanceScore" class="text-lg font-bold" :class="getPerformanceScoreClass({ estimated_speed_fps: metrics.estimatedSpeed, kinetic_energy_40yd: metrics.kineticEnergy * 0.77, foc_percentage: metrics.foc })">
            {{ metrics.performanceScore }}/100
          </div>
          <div v-else-if="metrics.penetration_category" :class="getPenetrationClass(metrics.penetration_category)" class="text-lg font-bold capitalize">
            {{ metrics.penetration_category }}
          </div>
          <div v-else class="text-lg font-bold text-orange-600 dark:text-orange-400">
            --
          </div>
          <PerformanceTooltip 
            :title="metrics.performanceScore ? 'Performance Score' : 'Penetration Rating'"
            :content="metrics.performanceScore ? 'Overall performance score based on speed, kinetic energy, and FOC.\n\nCalculation Formula:\nScore = (Penetration_Score × 0.4) + (KE_Score × 0.3) + (FOC_Score × 0.3)\n\nWhere:\n• KE_Score = min(100, (KE_40yd ÷ 80) × 100)\n• FOC_Score = max(0, 100 - |FOC - 12| × 5)\n• Penetration_Score = Based on momentum and arrow design\n\nHigher scores indicate better overall performance.' : 'Overall penetration capability based on kinetic energy and arrow design.\n\nCalculation Factors:\n• Kinetic Energy at impact\n• Momentum (Mass × Velocity)\n• Arrow diameter and design\n• Point weight and sharpness\n\nCategories: Poor < Fair < Good < Excellent'"
          />
        </div>
        <div class="text-sm text-orange-800 dark:text-orange-200 font-medium">
          {{ metrics.performanceScore ? 'Score' : 'Penetration' }}
        </div>
        <div class="text-xs text-orange-600 dark:text-orange-400 mt-1">
          {{ metrics.performanceScore ? (metrics.performanceScore >= 80 ? 'Excellent' : metrics.performanceScore >= 60 ? 'Good' : 'Fair') : getPenetrationDescription(metrics.penetration_category) }}
        </div>
      </div>
    </div>
    
    <!-- Detailed Metrics (if provided) -->
    <div v-if="showDetailed && (metrics.kinetic_energy_initial || metrics.momentum)" class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
      <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Detailed Metrics</h5>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div v-if="metrics.kinetic_energy_initial" class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">Initial KE:</span>
          <span class="font-medium text-gray-900 dark:text-gray-100">
            {{ formatKineticEnergy(metrics.kinetic_energy_initial) }}
          </span>
        </div>
        <div v-if="metrics.momentum" class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">Momentum:</span>
          <span class="font-medium text-gray-900 dark:text-gray-100">
            {{ formatMomentum(metrics.momentum) }}
          </span>
        </div>
        <div v-if="metrics.kinetic_energy_initial && (metrics.kineticEnergy || metrics.kinetic_energy_40yd)" class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">Energy Retention:</span>
          <span class="font-medium text-gray-900 dark:text-gray-100">
            {{ Math.round((metrics.kinetic_energy_40yd / metrics.kinetic_energy_initial) * 100) }}%
          </span>
        </div>
      </div>
    </div>
    
    <!-- Weight Breakdown (if provided) -->
    <div v-if="showWeight && metrics.totalWeight" class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
      <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Weight Information</h5>
      <div class="flex items-center justify-between">
        <span class="text-sm text-gray-600 dark:text-gray-400">Total Arrow Weight:</span>
        <span class="text-lg font-bold text-blue-600 dark:text-blue-400">{{ metrics.totalWeight }} grains</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePerformanceAnalysis } from '~/composables/usePerformanceAnalysis'
import PerformanceTooltip from '~/components/PerformanceTooltip.vue'

const props = defineProps({
  metrics: {
    type: Object,
    required: true
  },
  showDetailed: {
    type: Boolean,
    default: false
  },
  showWeight: {
    type: Boolean,
    default: false
  }
})

// Use the performance analysis composable for consistent formatting and ratings
const {
  formatSpeedValue,
  formatKineticEnergy,
  formatFocPercentage,
  formatMomentum,
  getSpeedRating,
  getKineticEnergyRating,
  getFOCRating,
  getPenetrationDescription,
  getPerformanceScoreClass,
  getPenetrationClass,
  getSpeedSourceClass,
  getSpeedSourceIcon,
  getSpeedSourceText
} = usePerformanceAnalysis()
</script>