import { ref, computed } from 'vue'
import { useApi } from '~/composables/useApi'

export interface TrajectoryData {
  performance_summary: {
    estimated_speed_fps: number
    total_arrow_weight: number
    kinetic_energy_initial: number
    kinetic_energy_40yd: number
    foc_percentage: number
    penetration_category: string
    penetration_score: number
    momentum: number
    speed_source: 'chronograph' | 'enhanced_estimated' | 'estimated'
    confidence?: number
  }
  trajectory_points: Array<{
    distance_yards: number
    velocity_fps: number
    drop_inches: number
    kinetic_energy_ft_lbs: number
    time_seconds: number
  }>
  environmental_conditions: {
    temperature_f: number
    wind_speed_mph: number
    humidity_percent: number
    altitude_feet: number
  }
  shooting_conditions: {
    shot_angle_degrees: number
    sight_height_inches: number
    zero_distance_yards: number
  }
}

export interface ArrowData {
  estimated_speed_fps?: number
  total_weight: number
  outer_diameter: number
  arrow_type: string
  manufacturer: string
  model_name: string
  spine?: string | number
  setup_id?: number
  arrow_id?: number
  speed_source?: string
}

export interface BowConfig {
  drawWeight: number
  bowType: string
  drawLength: number
}

export interface EnvironmentalConditions {
  temperature_f?: number
  wind_speed_mph?: number
  humidity_percent?: number
  altitude_feet?: number
}

export interface ShootingConditions {
  shot_angle_degrees?: number
  sight_height_inches?: number
  zero_distance_yards?: number
}

/**
 * Trajectory Calculation Composable
 * 
 * Provides a unified interface for trajectory calculations across all components.
 * Ensures consistency between main TrajectoryChart and ArrowPerformancePreview.
 */
export const useTrajectoryCalculation = () => {
  const api = useApi()
  
  // State
  const isCalculating = ref(false)
  const trajectoryData = ref<TrajectoryData | null>(null)
  const error = ref<string | null>(null)
  
  // Default environmental conditions
  const defaultEnvironmental: EnvironmentalConditions = {
    temperature_f: 70,
    wind_speed_mph: 0,
    humidity_percent: 50,
    altitude_feet: 1000
  }
  
  // Default shooting conditions
  const defaultShooting: ShootingConditions = {
    shot_angle_degrees: 0.0,
    sight_height_inches: 7.0,
    zero_distance_yards: 20
  }
  
  /**
   * Calculate trajectory using the unified API endpoint
   */
  const calculateTrajectory = async (
    setupArrow: any,
    arrow: any,
    bowConfig: BowConfig,
    environmental?: EnvironmentalConditions,
    shooting?: ShootingConditions
  ): Promise<TrajectoryData | null> => {
    if (isCalculating.value) return null
    
    isCalculating.value = true
    error.value = null
    
    try {
      // Build arrow data with chronograph priority
      const arrowData = await buildArrowData(setupArrow, arrow)
      
      const requestData = {
        arrow_data: {
          estimated_speed_fps: arrowData.estimated_speed_fps || 280,
          total_weight: arrowData.total_weight,
          outer_diameter: arrowData.outer_diameter || 0.246,
          arrow_type: arrowData.arrow_type || 'hunting',
          manufacturer: arrowData.manufacturer || 'Unknown',
          model_name: arrowData.model_name || 'Unknown',
          spine: arrowData.spine,
          setup_id: arrowData.setup_id,
          arrow_id: arrowData.arrow_id,
          speed_source: arrowData.speed_source || 'estimated'
        },
        bow_config: {
          drawWeight: bowConfig.drawWeight || 60,
          bowType: bowConfig.bowType || 'compound',
          drawLength: bowConfig.drawLength || 28
        },
        environmental_conditions: {
          ...defaultEnvironmental,
          ...environmental
        },
        shooting_conditions: {
          ...defaultShooting,
          ...shooting
        }
      }
      
      const response = await api.post('/calculate-trajectory', requestData)
      
      // Debug: Log the full response to understand what's happening
      console.log('🎯 Trajectory API Response:', {
        success: response.success,
        has_trajectory_data: !!response.trajectory_data,
        error: response.error,
        error_details: response.error_details,
        full_response_keys: Object.keys(response),
        full_response: response
      })
      
      if (response.success && response.trajectory_data) {
        trajectoryData.value = response.trajectory_data
        return response.trajectory_data
      } else {
        console.error('🚨 Trajectory calculation failed:', {
          success: response.success,
          error: response.error,
          error_details: response.error_details,
          fallback_data: response.fallback_data
        })
        throw new Error(response.error || 'Failed to calculate trajectory')
      }
    } catch (err) {
      console.error('Trajectory calculation error:', err)
      error.value = err instanceof Error ? err.message : 'Unknown error occurred'
      return null
    } finally {
      isCalculating.value = false
    }
  }
  
  /**
   * Calculate simplified trajectory for fallback scenarios
   */
  const calculateSimplifiedTrajectory = async (
    setupArrow: any,
    arrow: any,
    bowConfig: BowConfig
  ): Promise<Partial<TrajectoryData>> => {
    const arrowData = await buildArrowData(setupArrow, arrow)
    const speed = arrowData.estimated_speed_fps || estimateSpeed(arrowData.total_weight, bowConfig.drawWeight)
    const kineticEnergyInitial = calculateKineticEnergy(arrowData.total_weight, speed)
    const kineticEnergy40yd = kineticEnergyInitial * 0.7 // Simplified energy retention
    
    return {
      performance_summary: {
        estimated_speed_fps: speed,
        total_arrow_weight: arrowData.total_weight,
        kinetic_energy_initial: kineticEnergyInitial,
        kinetic_energy_40yd: kineticEnergy40yd,
        foc_percentage: 12, // Default FOC
        penetration_category: getPenetrationCategory(kineticEnergy40yd),
        penetration_score: Math.min(100, (kineticEnergy40yd / 80) * 100),
        momentum: calculateMomentum(arrowData.total_weight, speed),
        speed_source: arrowData.speed_source as any || 'estimated'
      }
    }
  }
  
  /**
   * Helper function to estimate arrow speed using industry-accurate formulas
   */
  const estimateSpeed = (totalWeight: number, drawWeight: number): number => {
    // Industry-standard IBO speed baseline (more realistic for most compounds)
    const iboBaseSpeed = 350 // Most compound bows rate around 330-370 IBO
    
    // IBO standard: 350gr arrow, 70lb draw weight, 30" draw length
    const iboArrowWeight = 350
    const iboDrawWeight = 70
    
    // Archery accurate weight adjustment formula
    // Industry standard: ~2.5-3 fps loss per 5 grains of additional arrow weight
    const weightDifference = totalWeight - iboArrowWeight
    const speedLossPerGrain = 0.55 // Approximately 2.75 fps per 5 grains = 0.55 fps per grain
    const weightAdjustment = -weightDifference * speedLossPerGrain
    
    // Draw weight adjustment (more accurate than linear scaling)
    // Industry standard: approximately 2-3 fps gain/loss per pound of draw weight
    const drawWeightDifference = drawWeight - iboDrawWeight
    const speedPerPound = 2.5 // fps per pound of draw weight difference
    const drawWeightAdjustment = drawWeightDifference * speedPerPound
    
    // Calculate estimated speed
    const estimatedSpeed = iboBaseSpeed + weightAdjustment + drawWeightAdjustment
    
    // Realistic constraints: modern compound bows typically range 200-400 FPS
    // Traditional bows typically range 150-220 FPS
    const minSpeed = drawWeight < 50 ? 150 : 180 // Lower minimum for light bows
    const maxSpeed = 400 // Maximum realistic speed for compound bows
    
    return Math.max(minSpeed, Math.min(maxSpeed, Math.round(estimatedSpeed)))
  }
  
  /**
   * Calculate kinetic energy
   */
  const calculateKineticEnergy = (weight: number, speed: number): number => {
    // KE = (mass × velocity²) / 450240 (for grains and fps to ft-lbs)
    return (weight * speed * speed) / 450240
  }
  
  /**
   * Calculate momentum
   */
  const calculateMomentum = (weight: number, speed: number): number => {
    // Momentum = mass × velocity (converted to appropriate units)
    return (weight * speed) / 225218
  }
  
  /**
   * Get penetration category based on kinetic energy
   */
  const getPenetrationCategory = (ke: number): string => {
    if (ke >= 65) return 'excellent'
    if (ke >= 40) return 'good'
    if (ke >= 25) return 'fair'
    return 'poor'
  }
  
  /**
   * Check for chronograph data and return speed if available
   */
  const getChronographSpeed = async (setupId: number, arrowId: number): Promise<number | null> => {
    try {
      const response = await api.post('/calculator/arrow-speed-estimate', {
        setup_id: setupId,
        arrow_id: arrowId,
        bow_ibo_speed: 320, // These values won't be used if chronograph data exists
        bow_draw_weight: 60,
        bow_draw_length: 28,
        arrow_weight_grains: 400
      })
      
      if (response.calculation_method === 'chronograph_data') {
        console.log('🎯 Chronograph data found:', {
          speed: response.estimated_speed_fps,
          confidence: response.confidence_percent,
          chronograph_data: response.chronograph_data
        })
        return response.estimated_speed_fps
      }
    } catch (error) {
      console.warn('Failed to check chronograph data:', error)
    }
    
    return null
  }

  /**
   * Build arrow data object from component props with chronograph data priority
   */
  const buildArrowData = async (
    setupArrow: any,
    arrow: any,
    performanceData?: any
  ): Promise<ArrowData> => {
    // Debug logging for arrow object
    if (process.dev) {
      console.log('🔍 Arrow Object Debug:', {
        hasArrow: !!arrow,
        arrowId: arrow?.id,
        hasSpineSpecs: !!arrow?.spine_specifications,
        spineSpecsLength: arrow?.spine_specifications?.length,
        arrowObject: arrow
      })
    }
    
    // Calculate total weight
    let shaftWeight = 0
    if (arrow?.spine_specifications?.length > 0) {
      const spineSpec = arrow.spine_specifications.find((spec: any) => 
        spec.spine.toString() === setupArrow.calculated_spine?.toString()
      ) || arrow.spine_specifications[0]
      
      if (spineSpec?.gpi_weight) {
        shaftWeight = spineSpec.gpi_weight * (setupArrow.arrow_length || 32)
      }
      
      // Debug logging for spine specification matching
      if (process.dev) {
        console.log('🔍 Spine Specification Debug:', {
          calculatedSpine: setupArrow.calculated_spine,
          availableSpines: arrow.spine_specifications.map((spec: any) => ({
            spine: spec.spine,
            gpi_weight: spec.gpi_weight,
            spineString: spec.spine.toString(),
            calculatedSpineString: setupArrow.calculated_spine?.toString(),
            matches: spec.spine.toString() === setupArrow.calculated_spine?.toString()
          })),
          selectedSpineSpec: spineSpec,
          shaftWeightCalculation: {
            gpi: spineSpec?.gpi_weight,
            length: setupArrow.arrow_length,
            result: shaftWeight
          }
        })
      }
    } else {
      // Fallback: Try to get GPI weight from setupArrow performance data or other sources
      if (setupArrow.performance?.gpi_weight || setupArrow.gpi_weight) {
        const gpiWeight = setupArrow.performance?.gpi_weight || setupArrow.gpi_weight
        shaftWeight = gpiWeight * (setupArrow.arrow_length || 32)
        
        if (process.dev) {
          console.log('🔄 Fallback Shaft Weight Calculation:', {
            source: 'setupArrow performance/gpi_weight',
            gpiWeight,
            arrowLength: setupArrow.arrow_length,
            calculatedShaftWeight: shaftWeight
          })
        }
      } else if (arrow?.gpi_weight) {
        // Try arrow-level GPI weight
        shaftWeight = arrow.gpi_weight * (setupArrow.arrow_length || 32)
        
        if (process.dev) {
          console.log('🔄 Fallback Shaft Weight Calculation:', {
            source: 'arrow.gpi_weight',
            gpiWeight: arrow.gpi_weight,
            arrowLength: setupArrow.arrow_length,
            calculatedShaftWeight: shaftWeight
          })
        }
      } else {
        // Last resort: Use a default GPI based on arrow type if available
        const defaultGPI = arrow?.arrow_type === 'carbon' ? 8.5 : 
                          arrow?.arrow_type === 'aluminum' ? 12.0 : 
                          8.9 // Default carbon arrow GPI
        shaftWeight = defaultGPI * (setupArrow.arrow_length || 32)
        
        if (process.dev) {
          console.log('🔄 Fallback Shaft Weight Calculation:', {
            source: 'default GPI estimate',
            arrowType: arrow?.arrow_type,
            defaultGPI,
            arrowLength: setupArrow.arrow_length,
            calculatedShaftWeight: shaftWeight
          })
        }
      }
    }
    
    const componentWeight = 
      (setupArrow.point_weight || 0) +
      (setupArrow.nock_weight || 10) +
      (setupArrow.insert_weight || 0) +
      (setupArrow.bushing_weight || 0) +
      (setupArrow.fletching_weight || 15)
    
    const totalWeight = Math.round((shaftWeight + componentWeight) * 10) / 10
    
    // Check for chronograph data first (highest priority)
    let estimatedSpeed = performanceData?.performance_summary?.estimated_speed_fps
    let speedSource = performanceData?.performance_summary?.speed_source || 'estimated'
    
    // If no performance data provided, try to get enhanced speed calculation directly
    if (!estimatedSpeed && setupArrow.setup_id && setupArrow.arrow_id) {
      try {
        const enhancedSpeedResponse = await getChronographSpeed(setupArrow.setup_id, setupArrow.arrow_id)
        if (enhancedSpeedResponse) {
          estimatedSpeed = enhancedSpeedResponse
          speedSource = 'chronograph'
          console.log('🎯 Using chronograph/enhanced speed:', {
            speed: enhancedSpeedResponse,
            setupId: setupArrow.setup_id,
            arrowId: setupArrow.arrow_id
          })
        }
      } catch (error) {
        console.warn('Failed to get enhanced speed, will use fallback:', error)
      }
    }
    
    // Legacy chronograph check (keep for backward compatibility)
    if (setupArrow.setup_id && setupArrow.arrow_id && !estimatedSpeed) {
      const chronographSpeed = await getChronographSpeed(setupArrow.setup_id, setupArrow.arrow_id)
      if (chronographSpeed) {
        estimatedSpeed = chronographSpeed
        speedSource = 'chronograph'
        console.log('🎯 Using chronograph data:', {
          speed: chronographSpeed,
          setupId: setupArrow.setup_id,
          arrowId: setupArrow.arrow_id
        })
      }
    }
    
    // Debug logging to trace the weight calculation issue
    if (process.dev) {
      console.log('🎯 buildArrowData Debug:', {
        shaftWeight,
        componentWeight,
        totalWeight,
        pointWeight: setupArrow.point_weight,
        nockWeight: setupArrow.nock_weight,
        arrowLength: setupArrow.arrow_length,
        calculatedSpine: setupArrow.calculated_spine,
        estimatedSpeed,
        speedSource
      })
    }
    
    return {
      estimated_speed_fps: estimatedSpeed,
      total_weight: totalWeight,
      outer_diameter: arrow?.spine_specifications?.[0]?.outer_diameter || 0.246,
      arrow_type: arrow?.arrow_type || 'hunting',
      manufacturer: arrow?.manufacturer || 'Unknown',
      model_name: arrow?.model_name || 'Unknown',
      spine: setupArrow.calculated_spine,
      setup_id: setupArrow.setup_id,
      arrow_id: setupArrow.arrow_id,
      speed_source: speedSource
    }
  }
  
  /**
   * Build bow config object from component props
   */
  const buildBowConfig = (bowConfig: any): BowConfig => {
    return {
      drawWeight: bowConfig.draw_weight || 60,
      bowType: bowConfig.bow_type || 'compound',
      drawLength: bowConfig.draw_length || 28
    }
  }
  
  // Computed properties
  const hasTrajectoryData = computed(() => !!trajectoryData.value?.performance_summary)
  const performanceSummary = computed(() => trajectoryData.value?.performance_summary)
  const trajectoryPoints = computed(() => trajectoryData.value?.trajectory_points || [])
  
  // Clear trajectory data
  const clearTrajectoryData = () => {
    trajectoryData.value = null
    error.value = null
  }
  
  return {
    // State
    isCalculating: readonly(isCalculating),
    trajectoryData: readonly(trajectoryData),
    error: readonly(error),
    
    // Computed
    hasTrajectoryData,
    performanceSummary,
    trajectoryPoints,
    
    // Methods
    calculateTrajectory,
    calculateSimplifiedTrajectory,
    buildArrowData,
    buildBowConfig,
    clearTrajectoryData,
    getChronographSpeed,
    
    // Utility methods
    estimateSpeed,
    calculateKineticEnergy,
    calculateMomentum,
    getPenetrationCategory
  }
}