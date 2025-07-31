# Arrow Scraper Configuration and Usage Guide

## Overview

The Arrow Scraper system is a sophisticated web scraping platform that extracts arrow specifications from manufacturer websites. The system is **entirely configuration-driven** using the `arrow_scraper/config/manufacturers.yaml` file, which contains all manufacturer URLs, extraction methods, and settings.

## Configuration Structure

### Primary Configuration File: `manufacturers.yaml`

**Location**: `/home/paal/archerytools/arrow_scraper/config/manufacturers.yaml`

This YAML file contains the complete configuration for:
- **15 Manufacturers** with 179 total product URLs
- **Multi-language Support** (English, German, Italian)
- **Multiple Extraction Methods** (text, vision-based)
- **Global Settings** for scraping behavior

### Manufacturer Configuration Format

```yaml
manufacturers:
  "Manufacturer Name":
    base_url: "https://example.com/"
    extraction_method: "text"  # or "vision"
    language: "english"        # optional: "german", "italian"
    product_urls:
      - "https://example.com/product1"
      - "https://example.com/product2"
```

## Supported Manufacturers (15 Total)

### English Language Manufacturers (11)
- **Easton Archery**: 34 URLs, text extraction, premium target/hunting arrows
- **Gold Tip**: 32 URLs, text extraction, target and hunting arrows
- **Victory Archery**: 18 URLs, **vision extraction**, hunting and target arrows
- **Skylon Archery**: 11 URLs, text extraction, European target arrows
- **Carbon Express**: 9 URLs, **vision extraction**, image-based specifications
- **Pandarus Archery**: 10 URLs, text extraction, precision target arrows
- **Fivics**: 4 URLs, **vision extraction**, Korean Olympic-level target arrows
- **Fairbow**: 7 URLs, text extraction, traditional wood arrows
- **The Longbow Shop**: 5 URLs, text extraction, traditional wood arrows
- **The Footed Shaft**: 3 URLs, text extraction, premium wood arrows
- **3Rivers Archery**: 5 URLs, text extraction, traditional wood arrows

### German Language Manufacturers (3)
- **Nijora Archery**: 17 URLs, text extraction + translation
- **DK Bow**: 4 URLs, text extraction + translation
- **Aurel Archery**: 7 URLs, text extraction + precision arrows

### Italian Language Manufacturers (1)
- **BigArchery**: 13 URLs, text extraction + translation, Cross-X competition arrows

## Extraction Methods

### 1. Text Extraction (`method: "text"`)
- **Usage**: Most manufacturers (12/15)
- **Process**: HTML content analysis using DeepSeek LLM
- **Languages**: English, German (auto-translated), Italian (auto-translated)
- **Best for**: Standard product pages with tabular data

### 2. Vision Extraction (`method: "vision"`)
- **Usage**: 3 manufacturers (Victory, Carbon Express, Fivics)
- **Process**: EasyOCR + image analysis for spine charts and specifications
- **Languages**: English only
- **Best for**: Manufacturers with image-based spine charts

## Scraper Usage Commands

### Basic Usage

```bash
# Navigate to scraper directory
cd arrow_scraper

# Set up environment (if needed)
export DEEPSEEK_API_KEY="your_api_key_here"
```

### Individual Manufacturer Scraping

```bash
# Scrape single manufacturer (limited support)
python main.py easton

# Note: Individual scraping only supports Easton currently
# For other manufacturers, use --update-all
```

### Comprehensive All-Manufacturer Update (Recommended)

```bash
# Update ALL 15 manufacturers with automatic translation
python main.py --update-all

# Force update existing data with translation
python main.py --update-all --force

# Update without translation (English-only, faster)
python main.py --update-all --no-translate
```

### Information Commands

```bash
# List all configured manufacturers
python main.py --list-manufacturers

# Show manufacturer details with URL counts and methods
python -c "
import yaml
with open('config/manufacturers.yaml', 'r') as f:
    config = yaml.safe_load(f)
for name, details in config['manufacturers'].items():
    print(f'{name}: {len(details[\"product_urls\"])} URLs, {details[\"extraction_method\"]}')
"
```

## Multi-Language Translation System

### Automatic Translation Features
- **Smart Language Detection**: Automatically detects German, Italian content
- **Technical Preservation**: Maintains spine numbers, diameters, weights unchanged
- **Cascading Fallback**: Falls back to original text if translation fails
- **Translation Metadata**: Tracks confidence scores and original text

### Supported Languages
- 🇩🇪 **German**: Nijora, DK Bow, Aurel manufacturers
- 🇮🇹 **Italian**: BigArchery/Cross-X manufacturers
- 🇫🇷 **French**: Future manufacturer support
- 🇪🇸 **Spanish**: Future manufacturer support

### Translation Workflow
1. **Content Analysis**: Detects non-English content
2. **DeepSeek Translation**: Uses specialized archery prompts
3. **Technical Preservation**: Keeps specifications unchanged
4. **Dual Storage**: Stores both original and translated content
5. **Metadata Tracking**: Records translation confidence

## Configuration Management

### Adding New Manufacturers

1. **Edit manufacturers.yaml**:
```yaml
"New Manufacturer":
  base_url: "https://newmanufacturer.com/"
  extraction_method: "text"  # or "vision"
  language: "english"        # or "german", "italian"
  product_urls:
    - "https://newmanufacturer.com/arrows/model1"
    - "https://newmanufacturer.com/arrows/model2"
```

2. **Test the configuration**:
```bash
python main.py --list-manufacturers  # Verify new manufacturer appears
python main.py --update-all          # Include in full update
```

### Modifying Existing Manufacturers

- **Add URLs**: Append to `product_urls` array
- **Change Method**: Update `extraction_method` (text/vision)
- **Add Language**: Set `language` field for non-English sites

### Global Settings Configuration

```yaml
settings:
  rate_limit_delay: 2.0    # seconds between requests
  timeout: 60              # request timeout
  max_retries: 5           # retry attempts
  batch_size: 10           # processing batch size
  
  easyocr:                 # Vision extraction settings
    enabled: true
    languages: ["en"]
    confidence_threshold: 0.5
  
  output:                  # File output settings
    directory: "data/processed"
    save_images: true
    image_directory: "data/images"
```

## Output Structure

### JSON Data Files
```
arrow_scraper/data/processed/
├── Easton_Archery_*.json
├── Gold_Tip_*.json
├── Victory_Archery_*.json
├── Nijora_Archery_*.json (German → English)
├── BigArchery_*.json (Italian → English)
└── traditional_wood_arrows.json
```

### Database Integration
- **Automatic Import**: Processed JSON files automatically imported to SQLite
- **Data Validation**: Pydantic models ensure data quality
- **Relationship Management**: Arrows linked to spine specifications
- **Material Classification**: Automatic categorization (Carbon, Wood, Aluminum, etc.)

## Best Practices

### Respectful Scraping
- **Rate Limiting**: 2-second delays between requests (configurable)
- **Retry Logic**: Maximum 5 retries with exponential backoff
- **Error Handling**: Graceful failure handling
- **Batch Processing**: Configurable batch sizes to avoid overwhelming servers

### Data Quality
- **Validation**: Comprehensive Pydantic model validation
- **Deduplication**: Automatic duplicate detection and handling
- **Translation Quality**: Confidence scoring for translated content
- **Error Reporting**: Detailed logging of failed extractions

### Production Usage
- ⚠️ **Server Deployment**: Production servers should NEVER run scraping
- ✅ **Development Only**: Scraping performed in development environments
- ✅ **JSON Import**: Production systems import pre-scraped JSON files
- ✅ **Version Control**: JSON files committed to repository for deployment

## Troubleshooting

### Common Issues

1. **Missing API Key**:
```bash
export DEEPSEEK_API_KEY="your_key_here"
# or create .env file with DEEPSEEK_API_KEY=your_key_here
```

2. **Network Issues**:
```bash
# Check specific manufacturer
python main.py --update-all --force
```

3. **Translation Issues**:
```bash
# Disable translation if issues occur
python main.py --update-all --no-translate
```

4. **Vision Extraction Issues**:
- Ensure EasyOCR dependencies installed
- Check image accessibility
- Review confidence thresholds in settings

### Logs and Debugging
- **Scraping Logs**: Detailed extraction progress
- **Translation Logs**: Language detection and confidence scores
- **Error Logs**: Failed URLs and retry attempts
- **Statistics**: Success rates and processing times

## Architecture Integration

### Components
- **ConfigLoader**: Reads manufacturers.yaml configuration
- **DeepSeekExtractor**: LLM-based content extraction
- **DeepSeekTranslator**: Multi-language translation
- **EasyOCRExtractor**: Vision-based extraction
- **ArrowDatabase**: SQLite database management
- **Pydantic Models**: Data validation and structure

### Data Flow
1. **Config Loading**: manufacturers.yaml → ConfigLoader
2. **URL Processing**: Batch processing with rate limiting
3. **Content Extraction**: Method-specific extraction (text/vision)
4. **Translation**: Automatic for non-English content
5. **Validation**: Pydantic model validation
6. **Storage**: JSON files + SQLite database
7. **Integration**: API endpoints for frontend access

---

## Quick Reference

**Total Configuration**: 15 manufacturers, 179 URLs, 3 languages, 2 extraction methods

**Primary Command**: `python main.py --update-all` (updates all manufacturers)

**Configuration File**: `config/manufacturers.yaml` (single source of truth)

**Output**: JSON files in `data/processed/` + SQLite database

**Languages**: English, German (auto-translated), Italian (auto-translated)