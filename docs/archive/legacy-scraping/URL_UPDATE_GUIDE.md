# URL Update Guide

This guide explains how to use the `update_manufacturer_urls.py` script to automatically update manufacturer URLs when they change their website structure.

## Quick Start

### Update a Single Manufacturer

```bash
# Navigate to arrow_scraper directory
cd arrow_scraper

# Activate virtual environment
source venv/bin/activate

# Update Nijora Archery URLs from their category page
python update_manufacturer_urls.py \
  --manufacturer "Nijora Archery" \
  --category-url "https://nijora.com/product-category/carbonpfeile/carbonschaefte/"

# Preview changes without saving (dry run)
python update_manufacturer_urls.py \
  --manufacturer "Nijora Archery" \
  --category-url "https://nijora.com/product-category/carbonpfeile/carbonschaefte/" \
  --dry-run
```

### Update Multiple Manufacturers

```bash
# Update all configured manufacturers
python update_manufacturer_urls.py --all

# Preview all updates without saving
python update_manufacturer_urls.py --all --dry-run
```

## Features

### ✅ What the Script Does

1. **Scrapes Category Pages**: Automatically finds all product URLs on manufacturer category pages
2. **Smart URL Detection**: Uses multiple patterns to identify product pages (WooCommerce, custom paths, etc.)
3. **Compares Changes**: Shows added, removed, and unchanged URLs
4. **Creates Backups**: Automatically backs up YAML before changes
5. **Preserves Structure**: Maintains all existing configuration (base_url, extraction_method, language)
6. **Adds Timestamps**: Records when URLs were last updated

### 🔍 URL Detection Patterns

The script automatically detects product URLs using these patterns:
- `/product/` - Standard WooCommerce products
- `/produkt/` - German product pages
- `/item/` - Alternative product paths
- `/arrows/`, `/pfeil`, `/schaft`, `/carbon` - Arrow-specific paths

### 🚫 Excluded URLs

The script automatically excludes:
- Category pages (`/category/`)
- Cart/checkout pages
- Admin/login pages
- Images and PDFs
- Blog/news pages

## Example Output

```
🔍 Updating URLs for Nijora Archery
📄 Scraping category page: https://nijora.com/product-category/carbonpfeile/carbonschaefte/
📊 URL Analysis for Nijora Archery:
   ✅ Found: 33 total URLs
   🆕 New: 30 URLs
   ❌ Removed: 14 URLs
   🔄 Unchanged: 3 URLs

🆕 New URLs:
   + https://nijora.com/product/3d-fly/
   + https://nijora.com/product/3k-pro/
   + https://nijora.com/product/bark-heavy/
   ... and 27 more

❌ Removed URLs:
   - https://nijora.com/product/nijora-carbon-schaft-fox-trot/
   - https://nijora.com/product/nijora-carbon-schaft-mambo/
   ... and 12 more

✅ Successfully updated Nijora Archery URLs
```

## Finding Category URLs

### Common Category Page Patterns

Most manufacturers have category pages for their arrows:

| Manufacturer | Example Category URL |
|--------------|---------------------|
| Nijora | `https://nijora.com/product-category/carbonpfeile/carbonschaefte/` |
| Gold Tip | `https://www.goldtip.com/hunting-arrows/` |
| Victory | `https://www.victoryarchery.com/arrows-hunting/` |
| Easton | `https://eastonarchery.com/huntingarrows/` |

### How to Find Category URLs

1. **Visit the manufacturer's website**
2. **Look for navigation menus** with "Products", "Arrows", "Shafts", etc.
3. **Find category pages** that list multiple products
4. **Copy the URL** of the category page (not individual products)

## Adding New Manufacturers

To add support for more manufacturers, edit the `category_urls` dictionary in the script:

```python
category_urls = {
    "Nijora Archery": "https://nijora.com/product-category/carbonpfeile/carbonschaefte/",
    "Gold Tip": "https://www.goldtip.com/hunting-arrows/",
    "Victory Archery": "https://www.victoryarchery.com/arrows-hunting/",
    # Add more manufacturers here
}
```

## Troubleshooting

### Common Issues

1. **No URLs Found**
   - Check if the category URL is correct
   - Some sites may block automated requests
   - Try using `--dry-run` first to test

2. **Wrong URLs Detected**
   - The script uses smart filtering but may occasionally include non-product pages
   - Review the output and manually remove incorrect URLs from YAML if needed

3. **Manufacturer Not Found**
   - Make sure the manufacturer name exactly matches what's in `manufacturers.yaml`
   - Check spelling and capitalization

### Getting Help

```bash
# Show help and examples
python update_manufacturer_urls.py --help

# Test URL detection without updating
python update_manufacturer_urls.py --manufacturer "Name" --category-url "URL" --dry-run
```

## Best Practices

1. **Always run with `--dry-run` first** to preview changes
2. **Check the backup file** if you need to revert changes
3. **Update regularly** to catch URL changes early
4. **Verify URLs work** by testing a few manually after updating
5. **Commit YAML changes** to version control

## Integration with Scraper

After updating URLs, you can immediately use them with the main scraper:

```bash
# Use updated URLs for scraping
python main.py --manufacturer "Nijora Archery" --limit 5

# Full update with new URLs
python main.py --update-all
```

This ensures your scraper always has the most current product URLs!