/**
 * Performance Analysis Composable
 * Provides consistent performance calculation and formatting across all components
 */

import { ref, computed, reactive } from 'vue'
import { useApi } from '~/composables/useApi'

export const usePerformanceAnalysis = () => {
  const api = useApi()
  
  // State
  const isCalculating = ref(false)
  const performanceData = ref(null)
  
  // Reactive configuration for live calculations
  const liveConfig = reactive({
    bowConfig: null,
    arrowData: null,
    setupData: null
  })
  
  /**
   * Calculate performance for a specific arrow setup
   */
  const calculatePerformance = async (setupArrowId, bowConfig) => {
    if (!setupArrowId || !bowConfig) return null
    
    isCalculating.value = true
    try {
      // Ensure we use the bow setup draw length (primary) or fallback properly
      const effectiveDrawLength = bowConfig.draw_length || bowConfig.user_draw_length || 28.0
      
      const response = await api.post(`/setup-arrows/${setupArrowId}/calculate-performance`, {
        bow_config: {
          draw_weight: bowConfig.draw_weight,
          draw_length: effectiveDrawLength,  // Use bow setup draw length with proper fallback
          bow_type: bowConfig.bow_type || 'compound'
          // Don't send ibo_speed - let backend use bow-type-specific ATA fallbacks (140 fps for longbow)
        }
      })
      
      if (response.performance) {
        performanceData.value = response.performance
        return response.performance
      }
    } catch (error) {
      console.error('Error calculating performance:', error)
      return null
    } finally {
      isCalculating.value = false
    }
    
    return null
  }
  
  /**
   * Calculate live performance preview without API call
   */
  const calculateLivePreview = (arrowData, bowConfig, setupData) => {
    if (!arrowData || !bowConfig || !setupData) return null
    
    try {
      // Calculate total weight
      const totalWeight = calculateTotalWeight(arrowData, setupData)
      
      // Estimate speed using similar logic to enhanced calculation
      const estimatedSpeed = estimateArrowSpeed(bowConfig, totalWeight)
      
      // Calculate kinetic energy
      const kineticEnergy = calculateKineticEnergy(totalWeight, estimatedSpeed)
      
      // Calculate FOC
      const foc = calculateFOC(arrowData, setupData, totalWeight)
      
      // Calculate performance score
      const performanceScore = calculatePerformanceScore({
        estimated_speed_fps: estimatedSpeed,
        kinetic_energy_40yd: kineticEnergy * 0.77, // Approximate retention
        foc_percentage: foc
      })
      
      return {
        totalWeight,
        estimatedSpeed,
        kineticEnergy,
        foc,
        performanceScore,
        speedSource: 'live_estimated'
      }
    } catch (error) {
      console.error('Error calculating live preview:', error)
      return null
    }
  }
  
  /**
   * Calculate total arrow weight from components
   */
  const calculateTotalWeight = (arrowData, setupData) => {
    // Calculate shaft weight using GPI
    let shaftWeight = 0
    if (arrowData?.spine_specifications?.length > 0) {
      const spineSpec = arrowData.spine_specifications.find(spec => 
        spec.spine.toString() === setupData.calculated_spine?.toString()
      ) || arrowData.spine_specifications[0]
      
      if (spineSpec?.gpi_weight) {
        shaftWeight = spineSpec.gpi_weight * (setupData.arrow_length || 32)
      }
    }
    
    // Add component weights
    const pointWeight = setupData.point_weight || 0
    const nockWeight = setupData.nock_weight || 10
    const insertWeight = setupData.insert_weight || 0
    const bushingWeight = setupData.bushing_weight || 0
    const fletchingWeight = setupData.fletching_weight || 15
    
    const totalWeight = shaftWeight + pointWeight + nockWeight + insertWeight + bushingWeight + fletchingWeight
    
    return Math.round(totalWeight * 10) / 10
  }
  
  /**
   * Estimate arrow speed using simplified enhanced calculation
   */
  const estimateArrowSpeed = (bowConfig, arrowWeight) => {
    const bowType = bowConfig.bow_type || 'compound'
    const drawWeight = bowConfig.draw_weight || 50
    // Use bow setup draw length with proper fallback hierarchy
    const drawLength = bowConfig.draw_length || bowConfig.user_draw_length || 28
    const iboSpeed = bowConfig.ibo_speed || getDefaultATA(bowType)
    
    // Reference parameters based on bow type
    const referenceWeight = 350.0
    const referenceDrawWeight = bowType === 'compound' ? 70.0 : 50.0
    const referenceDrawLength = bowType === 'compound' ? 30.0 : 28.0
    
    // Adjustments
    const weightAdjustment = (drawWeight - referenceDrawWeight) * 2.5
    const lengthAdjustment = (drawLength - referenceDrawLength) * 10
    const weightRatio = (referenceWeight / arrowWeight) ** 0.5
    
    // Bow efficiency factors
    const efficiencyFactors = {
      compound: 0.95,
      recurve: 0.90,
      longbow: 0.88,
      traditional: 0.85,
      barebow: 0.88
    }
    
    const bowEfficiency = efficiencyFactors[bowType.toLowerCase()] || 0.95
    const stringModifier = 0.92 // Default to dacron
    
    // Calculate speed
    const adjustedIbo = iboSpeed + weightAdjustment + lengthAdjustment
    const estimatedSpeed = adjustedIbo * weightRatio * stringModifier * bowEfficiency
    
    // Apply bounds
    const minSpeed = bowType === 'compound' ? 180 : 120
    const maxSpeed = bowType === 'compound' ? 450 : 350
    
    return Math.round(Math.max(minSpeed, Math.min(maxSpeed, estimatedSpeed)) * 10) / 10
  }
  
  /**
   * Get default ATA speed for bow type
   */
  const getDefaultATA = (bowType) => {
    // Realistic ATA speeds for accurate traditional archery calculations
    const ataSpeeeds = {
      compound: 320,
      recurve: 180,      // Reduced from 210 for realism
      longbow: 140,      // Reduced from 190 for realism
      traditional: 130,  // Reduced from 180 for realism
      barebow: 170       // Reduced from 200 for realism
    }
    return ataSpeeeds[bowType.toLowerCase()] || 320
  }
  
  /**
   * Calculate kinetic energy
   */
  const calculateKineticEnergy = (weightGrains, speedFps) => {
    // KE = 1/2 * m * v^2, with unit conversions
    // Weight in grains to pounds: divide by 7000
    // Speed in fps
    const weightPounds = weightGrains / 7000
    const ke = 0.5 * weightPounds * speedFps * speedFps / 32.174 // ft-lbs
    return Math.round(ke * 100) / 100
  }
  
  /**
   * Calculate FOC percentage
   */
  const calculateFOC = (arrowData, setupData, totalWeight) => {
    const arrowLength = setupData.arrow_length || 32
    const pointWeight = setupData.point_weight || 0
    const insertWeight = setupData.insert_weight || 0
    
    if (totalWeight === 0) return 0
    
    // Simplified FOC calculation
    const balancePoint = arrowLength / 2
    const frontWeight = pointWeight + insertWeight
    const foc = ((balancePoint - (arrowLength / 2)) / arrowLength) * 100 + 
                ((frontWeight / totalWeight) * 100)
    
    return Math.round(foc * 10) / 10
  }
  
  /**
   * Calculate overall performance score
   */
  const calculatePerformanceScore = (performanceSummary) => {
    if (!performanceSummary) return 0
    
    const keScore = Math.min(100, (performanceSummary.kinetic_energy_40yd / 80) * 100)
    const penetrationScore = 75 // Default reasonable score
    const focScore = performanceSummary.foc_percentage ? 
      Math.max(0, 100 - Math.abs((performanceSummary.foc_percentage || 0) - 12) * 5) : 50
    
    const compositeScore = (penetrationScore * 0.4) + (keScore * 0.3) + (focScore * 0.3)
    return Math.round(compositeScore)
  }
  
  // Formatting functions
  const formatSpeedValue = (speed) => {
    if (!speed) return '0 fps'
    return `${parseFloat(speed).toFixed(1)} fps`
  }
  
  const formatKineticEnergy = (ke) => {
    if (!ke) return '0 ft·lbs'
    return `${parseFloat(ke).toFixed(2)} ft·lbs`
  }
  
  const formatFocPercentage = (foc) => {
    if (!foc) return '0%'
    return `${parseFloat(foc).toFixed(1)}%`
  }
  
  const formatMomentum = (momentum) => {
    if (!momentum) return '0 slug·fps'
    return `${parseFloat(momentum).toFixed(2)} slug·fps`
  }
  
  // Rating functions
  const getSpeedRating = (speed) => {
    if (speed >= 350) return 'Very Fast'
    if (speed >= 300) return 'Fast'
    if (speed >= 250) return 'Moderate'
    return 'Slow'
  }
  
  const getKineticEnergyRating = (ke) => {
    if (ke >= 65) return 'Excellent (Elk+)'
    if (ke >= 40) return 'Good (Deer)'
    if (ke >= 25) return 'Fair (Small Game)'
    return 'Low'
  }
  
  const getFOCRating = (foc) => {
    if (foc >= 15 && foc <= 20) return 'Optimal (Hunting)'
    if (foc >= 10 && foc <= 15) return 'Good (Target)'
    if (foc >= 8 && foc <= 22) return 'Acceptable'
    return 'Suboptimal'
  }
  
  const getPenetrationDescription = (category) => {
    switch (category) {
      case 'excellent': return 'Maximum penetration'
      case 'good': return 'Good penetration'
      case 'fair': return 'Limited penetration'
      case 'poor': return 'Poor penetration'
      default: return 'Unknown'
    }
  }
  
  // Performance score styling
  const getPerformanceScoreClass = (performanceSummary) => {
    const score = calculatePerformanceScore(performanceSummary)
    if (score >= 80) return 'text-green-600 dark:text-green-400'
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }
  
  const getPenetrationClass = (category) => {
    switch (category) {
      case 'excellent': return 'text-green-600 dark:text-green-400'
      case 'good': return 'text-blue-600 dark:text-blue-400'
      case 'fair': return 'text-yellow-600 dark:text-yellow-400'
      case 'poor': return 'text-red-600 dark:text-red-400'
      default: return 'text-gray-500 dark:text-gray-400'
    }
  }
  
  // Speed source functions
  const getSpeedSourceClass = (source) => {
    if (source === 'chronograph') {
      return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
    } else if (source === 'enhanced_estimated') {
      return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
    } else if (source === 'live_estimated') {
      return 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200'
    } else {
      return 'bg-gray-100 dark:bg-gray-900/30 text-gray-800 dark:text-gray-200'
    }
  }
  
  const getSpeedSourceIcon = (source) => {
    if (source === 'chronograph') {
      return 'fas fa-tachometer-alt'
    } else if (source === 'enhanced_estimated') {
      return 'fas fa-cog'
    } else if (source === 'live_estimated') {
      return 'fas fa-bolt'
    } else {
      return 'fas fa-calculator'
    }
  }
  
  const getSpeedSourceText = (source) => {
    if (source === 'chronograph') {
      return 'Measured'
    } else if (source === 'enhanced_estimated') {
      return 'Enhanced'
    } else if (source === 'live_estimated') {
      return 'Live'
    } else {
      return 'Estimated'
    }
  }
  
  return {
    // State
    isCalculating,
    performanceData,
    liveConfig,
    
    // Methods
    calculatePerformance,
    calculateLivePreview,
    calculateTotalWeight,
    estimateArrowSpeed,
    calculateKineticEnergy,
    calculateFOC,
    calculatePerformanceScore,
    
    // Formatting
    formatSpeedValue,
    formatKineticEnergy,
    formatFocPercentage,
    formatMomentum,
    
    // Ratings
    getSpeedRating,
    getKineticEnergyRating,
    getFOCRating,
    getPenetrationDescription,
    
    // Styling
    getPerformanceScoreClass,
    getPenetrationClass,
    getSpeedSourceClass,
    getSpeedSourceIcon,
    getSpeedSourceText
  }
}