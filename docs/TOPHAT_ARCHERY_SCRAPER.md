# TopHat Archery Scraper Documentation

## Overview

The TopHat Archery scraper is a comprehensive tool for extracting arrow specifications from TopHat Archery's German product database. It processes over 1,350 product URLs from their sitemap to extract detailed arrow specifications including spine values, diameters, weights, and technical details.

## Features

### 🎯 Dual Extraction Strategy
- **Primary**: LLM extraction using DeepSeek API for intelligent content parsing
- **Fallback**: Manual extraction using BeautifulSoup and regex patterns for reliability

### 🌍 German Language Support
- Handles German product pages with automatic translation capability
- Processes German technical terms (Spinewert, Pfeildurchmesser, etc.)
- Converts German decimal format (5,40 → 5.40)

### 📊 Comprehensive Data Extraction
- Product titles and descriptions
- Technical specifications from properties tables
- Spine values, inner/outer diameters, GPI weights
- Materials, arrow types, length options
- Pricing and tolerance information
- Straightness and weight tolerances

### 🔄 Smart Data Processing
- Groups products by manufacturer and model
- Creates spine specifications arrays for each arrow
- Handles multiple spine options per arrow model
- Extracts spine numbers from URLs when needed
- Removes duplicate spine specifications

## Architecture

### Core Components

1. **TopHatArcheryScraper**: Main scraper class
2. **TopHatManualExtractor**: Fallback extraction using BeautifulSoup
3. **TopHatProduct**: Data structure for individual products
4. **Translation Service**: German to English translation support

### Data Flow

```
Sitemap URLs → Crawl4AI → LLM/Manual Extraction → Product Objects → Arrow Format → JSON Export
```

## Installation

### Prerequisites
```bash
# Install required dependencies
pip install crawl4ai beautifulsoup4 pydantic aiofiles
pip install playwright  # For browser automation
playwright install     # Install browser binaries
```

### Environment Setup
```bash
# Required API key for LLM extraction
echo "DEEPSEEK_API_KEY=your_deepseek_api_key_here" >> .env
```

## Usage

### Command Line Interface

```bash
# Navigate to scraper directory
cd arrow_scraper

# Test mode (5 URLs only)
python tophat_archery_scraper.py --test

# Limited scraping for development
python tophat_archery_scraper.py --limit=50

# Full database scraping (1,352 URLs - production)
python tophat_archery_scraper.py
```

### Command Line Arguments

- `--test`: Test mode with 5 URLs only
- `--limit=N`: Limit scraping to first N URLs
- `--help`: Show help message

### Output

Results are saved to `data/processed/extra/tophat_archery_arrows.json` to avoid interfering with the main import system.

## Data Structure

### Input: Sitemap Format
```json
[
  {
    "loc": "https://tophatarchery.com/komponentensuche-nach-schaft/marke/ok-archery/absolute/8387/ok-archery-absolute.15-350",
    "lastmod": "2021-10-07",
    "changefreq": "weekly",
    "priority": "0.5"
  }
]
```

### Output: Arrow Format
```json
{
  "scraping_metadata": {
    "source": "TopHat Archery",
    "scrape_date": "2025-08-03T00:15:26.056332",
    "total_products_found": 5,
    "total_arrows_extracted": 2,
    "scraper_version": "1.0.0"
  },
  "arrows": [
    {
      "manufacturer": "OK",
      "model_name": "Archery Absolute.15",
      "spine_specifications": [
        {
          "spine": "350",
          "outer_diameter": 0.234,
          "inner_diameter": 0.166,
          "gpi_weight": 9.0,
          "length_options": ["32\""]
        }
      ],
      "material": "Carbon",
      "arrow_type": "3D, Allzweck, Feld, Target",
      "description": "German description...",
      "price_range": "133,35",
      "straightness_tolerance": "±.001\""
    }
  ]
}
```

## Technical Implementation

### Manual Extraction Patterns

The manual extractor uses specific patterns to extract data from German HTML:

```python
field_mapping = {
    'Spinewert': 'spine',
    'Pfeildurchmesser (Innen)': 'inner_diameter',
    'Pfeildurchmesser (Außen)': 'outer_diameter',
    'GPI (Grain per Inch)': 'gpi_weight',
    'Auslieferungslänge': 'length_options',
    'Material': 'material',
    'Geradheit': 'straightness_tolerance',
    'Marke': 'manufacturer',
    'Empfohlener Einsatzweck': 'arrow_type'
}
```

### Diameter Conversion

Handles both imperial and metric measurements:
- Extracts inches directly: `.246"`
- Converts mm to inches: `6,25mm` → `0.246"`

### Error Handling

- Comprehensive logging with different log levels
- Graceful fallback from LLM to manual extraction
- Continues processing if individual URLs fail
- Respectful delays between requests (2 seconds)

## Performance

### Timing
- **Test Mode (5 URLs)**: ~15 seconds
- **Limited Mode (50 URLs)**: ~3-4 minutes
- **Full Mode (1,352 URLs)**: ~45-60 minutes (estimated)

### Resource Usage
- Uses AsyncWebCrawler for efficient concurrent processing
- Includes automatic memory management
- Rate limiting prevents server overload

## Integration

### Database Import

The output JSON is compatible with the existing database import system:

```bash
# To import TopHat data (manual process)
cd arrow_scraper
cp data/processed/extra/tophat_archery_arrows.json data/processed/
python database_import_manager.py --import-all --force
```

### Production Deployment

For production use:
1. Run scraper in development environment
2. Review output in `data/processed/extra/`
3. Manually move to `data/processed/` when ready
4. Use standard import process

## Monitoring

### Logs
- Detailed logging to `logs/tophat_scraper.log`
- Console output with progress indicators
- Error tracking and extraction success rates

### Metrics
- Total URLs processed
- Successful extractions vs failures
- LLM vs manual extraction usage
- Products extracted vs arrows created (grouping efficiency)

## Troubleshooting

### Common Issues

1. **Missing DeepSeek API Key**
   ```bash
   Error: DEEPSEEK_API_KEY not found in environment variables
   ```
   **Solution**: Add API key to `.env` file

2. **Playwright Browser Issues**
   ```bash
   playwright install
   ```
   **Solution**: Install browser binaries

3. **Empty Extraction Results**
   - Check internet connectivity
   - Verify target website accessibility
   - Review logs for specific error messages

### Debug Mode

For debugging individual URLs:
```python
# Test single URL extraction
python test_tophat_simple.py
python test_llm_extraction.py
python tophat_manual_extractor.py
```

## Future Enhancements

### Planned Features
- [ ] Automatic translation integration
- [ ] Image URL extraction and CDN upload
- [ ] Component data extraction (nocks, points, etc.)
- [ ] Advanced filtering by arrow categories
- [ ] Incremental updates based on lastmod dates

### Optimization Opportunities
- Concurrent processing optimization
- LLM prompt engineering improvements
- Caching for repeated URL processing
- Smart retry mechanisms for failed extractions

## Contributing

### Development Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run tests: `python tophat_archery_scraper.py --test`

### Code Structure
```
arrow_scraper/
├── tophat_archery_scraper.py      # Main scraper implementation
├── test_tophat_simple.py          # Simple HTML fetching test
├── test_llm_extraction.py         # LLM extraction testing
├── tophat_manual_extractor.py     # Manual extraction testing
├── data/processed/extra/           # Output directory
└── logs/                           # Scraping logs
```

## License

This scraper respects TopHat Archery's robots.txt and terms of service. It includes respectful delays and is designed for research and database enhancement purposes only.

## Contact

For issues or questions regarding the TopHat Archery scraper, please refer to the main project documentation or create an issue in the project repository.