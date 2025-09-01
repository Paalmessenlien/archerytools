import type { BowConfiguration } from '~/types/arrow'

/**
 * Global spine calculation utilities
 * This should be the ONLY place for calculation logic in the frontend
 */

export interface SpineCalculationResult {
  recommended_spine: number | string
  spine_range: {
    min: number | string
    max: number | string
    optimal?: number | string
  }
  calculations?: {
    base_spine: number
    adjustments: Record<string, number>
    final_spine: number | string
  }
}

export interface CompatibilityResult {
  score: number
  explanation: string
  inTolerance: boolean
}

/**
 * Calculate arrow spine using the API - this is the ONLY way to calculate spine
 * Frontend should NEVER do client-side spine calculations
 * @param bowConfig - The bow configuration for spine calculation
 * @param apiInstance - Required API instance from useApi() composable
 * @param chartSelection - Optional spine chart selection for chart-based calculations
 */
export async function calculateSpineAPI(
  bowConfig: BowConfiguration, 
  apiInstance: any, 
  chartSelection: any = null
): Promise<SpineCalculationResult> {
  if (!apiInstance) {
    throw new Error('API instance is required for spine calculation. Pass useApi() as second parameter.')
  }
  
  // Prepare the calculation data
  const calculationData = { ...bowConfig }
  
  // Add chart parameters if chart is selected
  if (chartSelection?.manufacturer) {
    calculationData.manufacturer_chart = chartSelection.manufacturer
  }
  if (chartSelection?.chartId) {
    calculationData.chart_id = chartSelection.chartId
  }
  
  return await apiInstance.calculateSpine(calculationData)
}

/**
 * Calculate compatibility score using manufacturer spine chart ranges
 * This uses the actual spine ranges from manufacturer charts (like Easton)
 */
export function calculateCompatibilityScore(
  arrowSpine: number | string,
  recommendedSpine: number | string,
  bowType: string = 'compound',
  manufacturer: string = 'easton'
): CompatibilityResult {
  // Convert spine values to numbers for calculation
  const arrowSpineNum = typeof arrowSpine === 'string' 
    ? parseFloat(arrowSpine.replace('#', '').replace('lbs', ''))
    : arrowSpine
  
  const recommendedSpineNum = typeof recommendedSpine === 'string'
    ? parseFloat(recommendedSpine.replace('#', '').replace('lbs', ''))
    : recommendedSpine

  // Handle invalid values
  if (isNaN(arrowSpineNum) || isNaN(recommendedSpineNum) || recommendedSpineNum <= 0) {
    return {
      score: 0,
      explanation: 'Invalid spine values',
      inTolerance: false
    }
  }

  // Get the acceptable spine range for this configuration
  const spineRange = getManufacturerSpineRange(recommendedSpineNum, bowType, manufacturer)
  
  let score: number
  let explanation: string
  let inTolerance: boolean

  // Check if arrow spine is within the acceptable range
  if (arrowSpineNum >= spineRange.min && arrowSpineNum <= spineRange.max) {
    // Within acceptable range - calculate score based on position
    inTolerance = true
    
    const rangeSize = spineRange.max - spineRange.min
    const distanceFromOptimal = Math.abs(arrowSpineNum - recommendedSpineNum)
    const maxDistance = Math.max(recommendedSpineNum - spineRange.min, spineRange.max - recommendedSpineNum)
    
    if (distanceFromOptimal <= rangeSize * 0.1) {
      // Very close to recommended spine
      score = 95 + (5 * (1 - distanceFromOptimal / (rangeSize * 0.1)))
      explanation = 'Excellent spine match - optimal performance expected'
    } else if (distanceFromOptimal <= rangeSize * 0.3) {
      // Good position within range
      const rangePosition = (distanceFromOptimal - rangeSize * 0.1) / (rangeSize * 0.2)
      score = 85 + (10 * (1 - rangePosition))
      explanation = 'Very good spine match - excellent performance expected'
    } else {
      // Acceptable position within range
      const rangePosition = (distanceFromOptimal - rangeSize * 0.3) / (rangeSize * 0.2)
      score = 75 + (10 * (1 - rangePosition))
      explanation = 'Good spine match - performance suitable for most applications'
    }
  } else {
    // Outside acceptable range
    inTolerance = false
    
    const distanceOutside = arrowSpineNum < spineRange.min 
      ? spineRange.min - arrowSpineNum 
      : arrowSpineNum - spineRange.max
    
    const rangeSize = spineRange.max - spineRange.min
    
    if (distanceOutside <= rangeSize * 0.2) {
      // Close to acceptable range
      const proximityScore = 1 - (distanceOutside / (rangeSize * 0.2))
      score = 50 + (25 * proximityScore)
      explanation = arrowSpineNum < spineRange.min 
        ? 'Arrow is too stiff - may work with tuning adjustments'
        : 'Arrow is too weak - may work with tuning adjustments'
    } else if (distanceOutside <= rangeSize * 0.5) {
      // Moderately outside range
      const proximityScore = 1 - ((distanceOutside - rangeSize * 0.2) / (rangeSize * 0.3))
      score = 25 + (25 * proximityScore)
      explanation = arrowSpineNum < spineRange.min 
        ? 'Arrow is significantly too stiff - consider different arrow'
        : 'Arrow is significantly too weak - consider different arrow'
    } else {
      // Far outside acceptable range
      score = Math.max(0, 25 - (distanceOutside / rangeSize * 50))
      explanation = arrowSpineNum < spineRange.min 
        ? 'Arrow is far too stiff - strongly recommend different arrow'
        : 'Arrow is far too weak - strongly recommend different arrow'
    }
  }

  return {
    score: Math.round(Math.max(0, Math.min(100, score))),
    explanation,
    inTolerance
  }
}

/**
 * Get the acceptable spine range based on manufacturer charts
 */
function getManufacturerSpineRange(recommendedSpine: number, bowType: string, manufacturer: string): { min: number, max: number } {
  // This uses the same logic as the backend spine calculator ranges
  // Based on manufacturer spine charts
  
  if (bowType === 'compound') {
    // Easton compound bow ranges (based on the PDF chart)
    // Standard tolerance is typically ±25 spine units around the recommended spine
    const tolerance = 25
    
    return {
      min: recommendedSpine - tolerance,
      max: recommendedSpine + tolerance
    }
  } else if (bowType === 'recurve') {
    // Recurve bows have wider tolerance
    const tolerance = 50
    
    return {
      min: recommendedSpine - tolerance,
      max: recommendedSpine + tolerance
    }
  } else {
    // Traditional bows - widest tolerance
    const tolerance = 75
    
    return {
      min: recommendedSpine - tolerance,
      max: recommendedSpine + tolerance
    }
  }
}

/**
 * Find the best matching spine from an arrow's available spine specifications
 */
export function findBestSpineMatch(
  arrowSpineSpecs: Array<{ spine: number | string }>,
  recommendedSpine: number | string,
  bowType: string = 'compound',
  manufacturer: string = 'easton'
): { bestSpine: number | string, compatibility: CompatibilityResult } | null {
  if (!arrowSpineSpecs || arrowSpineSpecs.length === 0) {
    return null
  }

  let bestMatch = null
  let bestScore = -1

  for (const spineSpec of arrowSpineSpecs) {
    if (!spineSpec.spine) continue

    const compatibility = calculateCompatibilityScore(spineSpec.spine, recommendedSpine, bowType, manufacturer)
    
    if (compatibility.score > bestScore) {
      bestScore = compatibility.score
      bestMatch = {
        bestSpine: spineSpec.spine,
        compatibility
      }
    }
  }

  return bestMatch
}

/**
 * Get spine tolerance range for a bow type
 */
export function getSpineTolerance(bowType: string): { min: number, max: number } {
  const tolerances = {
    compound: { min: 0.85, max: 1.15 },    // ±15%
    recurve: { min: 0.80, max: 1.20 },     // ±20%
    traditional: { min: 0.75, max: 1.25 }  // ±25%
  }

  return tolerances[bowType as keyof typeof tolerances] || tolerances.compound
}

/**
 * Check if an arrow spine is within acceptable range
 */
export function isSpineInTolerance(
  arrowSpine: number | string,
  recommendedSpine: number | string,
  bowType: string = 'compound'
): boolean {
  const compatibility = calculateCompatibilityScore(arrowSpine, recommendedSpine, bowType)
  return compatibility.inTolerance
}

/**
 * Format spine value for display
 */
export function formatSpineDisplay(spine: number | string): string {
  if (typeof spine === 'string') {
    return spine // Already formatted (e.g., "50#" for wood arrows)
  }
  
  return spine.toString()
}

/**
 * Client-side fallback calculation - DEPRECATED
 * This should only be used in extreme cases when the API is unavailable
 * The real calculations are done by the backend spine_calculator.py
 */
export function calculateSpineFallback(bowConfig: BowConfiguration): number | string {
  console.warn('Using deprecated client-side spine calculation fallback. This should only happen when API is unavailable.')
  
  // This is intentionally simplified and marked as deprecated
  // Real calculations must go through the API
  const baseSpine = bowConfig.draw_weight * 10
  return Math.round(baseSpine)
}