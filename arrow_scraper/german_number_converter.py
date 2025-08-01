#!/usr/bin/env python3
"""
German number format converter for DK Bow data
"""

def convert_german_decimals(data):
    """
    Convert German decimal format (5,40) to English format (5.40)
    Handles nested dictionaries and lists
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = convert_german_decimals(value)
        return result
    elif isinstance(data, list):
        return [convert_german_decimals(item) for item in data]
    elif isinstance(data, str):
        # Check if string looks like German decimal number
        if ',' in data and data.replace(',', '').replace('.', '').isdigit():
            try:
                # Convert German decimal format to English
                return float(data.replace(',', '.'))
            except ValueError:
                return data
        return data
    else:
        return data

def preprocess_german_arrow_data(arrow_dict):
    """
    Preprocess German arrow data to handle decimal formats
    """
    if not isinstance(arrow_dict, dict):
        return arrow_dict
    
    processed = arrow_dict.copy()
    
    # Handle spine specifications
    if 'spine_specifications' in processed:
        for spec in processed['spine_specifications']:
            if isinstance(spec, dict):
                # Convert German decimals in spine spec
                for field in ['outer_diameter', 'inner_diameter', 'gpi_weight', 'weight']:
                    if field in spec and isinstance(spec[field], str):
                        if ',' in spec[field]:
                            try:
                                spec[field] = float(spec[field].replace(',', '.'))
                            except ValueError:
                                pass  # Keep original if conversion fails
    
    return processed

if __name__ == "__main__":
    # Test the converter
    test_data = {
        "outer_diameter": "5,40",
        "gpi_weight": "5,20",
        "spine_specifications": [
            {"spine": 500, "outer_diameter": "5,40", "gpi_weight": "5,20"},
            {"spine": 600, "outer_diameter": "5,30", "gpi_weight": "4,70"}
        ]
    }
    
    print("Original:", test_data)
    converted = preprocess_german_arrow_data(test_data)
    print("Converted:", converted)