#!/usr/bin/env python3

# Test the enhanced speed calculation with the new parameters
def test_enhanced_calculation():
    # Input parameters for setup #9
    bow_ibo_speed = 320
    bow_draw_weight = 50
    bow_draw_length = 29.25
    arrow_weight_grains = 410  # 9.5 GPI * 30" + 100 gr point + 25 gr components
    
    # Calculation parameters
    reference_weight = 350.0
    reference_draw_weight = 70.0
    reference_draw_length = 30.0
    
    # New calculation (2.5 fps per pound instead of 10)
    weight_adjustment = (bow_draw_weight - reference_draw_weight) * 2.5
    length_adjustment = (bow_draw_length - reference_draw_length) * 10
    weight_ratio = (reference_weight / arrow_weight_grains) ** 0.5
    string_modifier = 0.92  # dacron
    bow_efficiency = 0.95   # compound
    
    adjusted_ibo = bow_ibo_speed + weight_adjustment + length_adjustment
    estimated_speed = adjusted_ibo * weight_ratio * string_modifier * bow_efficiency
    final_speed = max(150, min(450, estimated_speed))
    
    print(f"Enhanced Speed Calculation Test:")
    print(f"  bow_ibo_speed: {bow_ibo_speed}")
    print(f"  bow_draw_weight: {bow_draw_weight}")  
    print(f"  bow_draw_length: {bow_draw_length}")
    print(f"  arrow_weight_grains: {arrow_weight_grains}")
    print(f"")
    print(f"  weight_adjustment: {weight_adjustment}")
    print(f"  length_adjustment: {length_adjustment}")
    print(f"  adjusted_ibo: {adjusted_ibo}")
    print(f"  weight_ratio: {weight_ratio:.3f}")
    print(f"  string_modifier: {string_modifier}")
    print(f"  bow_efficiency: {bow_efficiency}")
    print(f"")
    print(f"  raw estimated_speed: {estimated_speed:.1f} fps")
    print(f"  final_speed (after bounds): {final_speed:.1f} fps")
    
    # Test old calculation for comparison
    weight_adjustment_old = (bow_draw_weight - reference_draw_weight) * 10
    adjusted_ibo_old = bow_ibo_speed + weight_adjustment_old + length_adjustment
    estimated_speed_old = adjusted_ibo_old * weight_ratio * string_modifier * bow_efficiency
    final_speed_old = max(150, min(450, estimated_speed_old))
    
    print(f"")
    print(f"Old Calculation (10 fps/lb):")
    print(f"  weight_adjustment: {weight_adjustment_old}")
    print(f"  adjusted_ibo: {adjusted_ibo_old}")
    print(f"  raw estimated_speed: {estimated_speed_old:.1f} fps")
    print(f"  final_speed (after bounds): {final_speed_old:.1f} fps")

if __name__ == "__main__":
    test_enhanced_calculation()