# Component Scraping System Guide

This guide explains how to use the comprehensive component scraping and database system for arrow components like inserts, points, nocks, and other accessories.

## Overview

The component system consists of:

1. **Component Configuration** (`config/components.yaml`) - Defines suppliers, categories, and translation mappings
2. **Component Scraper** (`scrape_components.py`) - Scrapes German component pages and translates data
3. **Unified Database** (`arrow_database.db`) - Stores component data alongside arrow specifications

## Quick Start

### 1. Scrape Components from Tophat Archery

```bash
# Navigate to scraper directory
cd arrow_scraper
source venv/bin/activate

# Scrape 20 components from sitemap
python scrape_components.py --import-from-sitemap ../docs/sitemap_non_komponentensuche.json --limit 20

# Preview what would be scraped (dry run)
python scrape_components.py --import-from-sitemap ../docs/sitemap_non_komponentensuche.json --limit 10 --dry-run
```

### 2. Import Components into Database

```bash
# Import component JSON files into unified database
python component_importer.py --force

# Component data is automatically integrated with arrow database
# Components are stored in the same arrow_database.db file
# View component data via API endpoints: /api/components
```

## Component Categories Detected

The system automatically categorizes components based on URL analysis:

| Category | German Path | Description | Examples |
|----------|-------------|-------------|----------|
| **inserts** | `combo-einschraubspitzen-inserts/inserts` | Threaded inserts for carbon arrows | LL Insert GT 30X, LL Insert 22-Series |
| **glue_points** | `klebespitzen` | Glue-on arrow points and tips | LL Apex Full Bore, LL Convex CXL |
| **nocks** | `nocken-bushings` | Arrow nocks and bushings | LL Full Bore Bushing (G-Nock) |
| **outserts** | `outserts` | External mounting components | External threaded components |
| **adapters** | `adapter` | Threading adapters and connectors | Thread conversion adapters |

### Subcategories

- **Target** - Competition/target shooting components
- **Hunting** - Hunting-specific components  
- **Field** - Field archery components

## German Translation System

### Automatic Field Translation

The system automatically translates German specifications:

| German Field | English Field | Example Values |
|--------------|---------------|----------------|
| `Typ` | `type` | Insert, Einklebespitze |
| `Material` | `material` | Alu → Aluminum, Stahl → Steel |
| `Gewicht` | `weight` | "30, 50" → 30.0 grain (+ weight_options) |
| `Innendurchmesser` | `inner_diameter` | ".360", 9,14mm → 0.36" / 9.14mm |
| `Außendurchmesser` | `outer_diameter` | ".399", 10,13mm → 0.399" / 10.13mm |
| `Farbe` | `color` | Silber → Silver, Schwarz → Black |
| `Größe` | `size/compatibility` | "X 30 (9.14/10.13)" |

### Smart Measurement Parsing

The system intelligently parses German measurements:

```
".360", 9,14mm → inner_diameter_inch: 0.36, inner_diameter_mm: 9.14
"30, 50" → weight_grain: 30.0, weight_options: [30.0, 50.0]
"110-120-130-140gn" → weight_grain: 110.0, weight_options: [110, 120, 130, 140]
```

## Sample Output

```json
{
  "component_id": "tophat_ll_insert_gt_30x_50_30_gn",
  "supplier": "Tophat Archery",
  "name": "LL Insert GT 30X 50/30 gn",
  "category": "inserts",
  "type": "Insert",
  "material": "Aluminum",
  "weight_grain": 30.0,
  "weight_options": [30.0, 50.0],
  "inner_diameter_inch": 0.36,
  "inner_diameter_mm": 9.14,
  "outer_diameter_inch": 0.399,
  "outer_diameter_mm": 10.13,
  "color": "Silver",
  "compatibility": ["X 30 (9.14/10.13)"],
  "usage_type": null,
  "source_url": "https://tophatarchery.com/produkte/komponenten-fuer-carbonpfeile/combo-einschraubspitzen-inserts/inserts/inserts-info/1010/ll-insert-gt-30x-50/30-gn"
}
```

## Database Schema

### Components Table
- **Basic Info**: component_id, supplier, name, category, type, subcategory
- **Materials**: material, color, finish
- **Measurements**: weight_grain, inner/outer diameters (inch & mm), length
- **Compatibility**: usage_type, thread_specification
- **Metadata**: description, image_url, source_url, extracted_at

### Related Tables
- **component_weight_options**: Multiple weight choices for single component
- **component_compatibility**: Arrow shaft compatibility information

## Advanced Usage

### Search Components by Specifications

```python
from component_database import ComponentDatabase

db = ComponentDatabase("arrow_database.db")

# Find 30-grain inserts
inserts = db.search_components(category="inserts", weight_min=30, weight_max=30)

# Find components compatible with 0.246" arrow ID
compatible = db.get_compatible_components(arrow_inner_diameter=0.246)
```

### Batch Processing

```bash
# Scrape all 179 components (takes ~15 minutes with rate limiting)
python scrape_components.py --import-from-sitemap ../docs/sitemap_non_komponentensuche.json

# Import everything into database
python component_importer.py --force
```

## Integration with Arrow System

Components can be cross-referenced with arrow specifications:

```python
# Find compatible inserts for Easton X10 arrows
x10_inner_diameter = 0.204  # inches
compatible_inserts = db.search_components(
    category="inserts",
    outer_diameter_max=x10_inner_diameter - 0.005  # with tolerance
)
```

## Configuration Customization

### Adding New Suppliers

Edit `config/components.yaml`:

```yaml
component_suppliers:
  "New Supplier":
    base_url: "https://newsupplier.com/"
    language: "german"  # or "english"
    extraction_method: "table_extraction"
    
    categories:
      inserts:
        path_pattern: "inserts"
        german_name: "Inserts"
        english_name: "Inserts"
```

### Custom Translation Mappings

```yaml
field_translations:
  "Durchmesser": "diameter"
  "Länge": "length"
  "Gewinde": "thread"

material_translations:
  "Titan": "Titanium"
  "Messing": "Brass"
```

## Performance Notes

- **Rate Limiting**: 3-second delay between requests (configurable)
- **Batch Size**: Processes components individually for accuracy
- **Database**: SQLite with indexes for fast searching
- **Memory**: Processes one component at a time for efficiency

## Troubleshooting

### Common Issues

1. **No Components Found**: Check sitemap file path and content
2. **Translation Errors**: Verify German field names in configuration
3. **Database Import Fails**: Check JSON file format and permissions

### Debugging

```bash
# Test single component URL
python -c "
import asyncio
from scrape_components import ComponentScraper
scraper = ComponentScraper()
result = asyncio.run(scraper.scrape_component_page('URL_HERE', 'Tophat Archery'))
print(result)
"
```

## Future Enhancements

- **API Integration**: REST API for component search
- **Compatibility Engine**: Match components to specific arrow models
- **Price Tracking**: Monitor component pricing over time
- **Multi-language Support**: Expand beyond German translations
- **Image Processing**: Extract specifications from product images

This system provides a complete solution for managing arrow component data with automatic German translation and comprehensive database storage!