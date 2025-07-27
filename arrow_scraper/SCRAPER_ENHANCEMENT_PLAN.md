# Arrow Scraper Enhancement Plan
## URL Management & Component Integration

### 🎯 Overview
Enhance the arrow scraper with automatic URL management and component database integration to create a comprehensive archery equipment database.

## 📋 Phase 1: URL Management System

### 1.1 Add Individual URLs (`--add` command)
**Command**: `python main.py --add manufacturer=easton type=arrow http://url`

**Features**:
- Add URLs to existing manufacturer configurations
- Validate URL accessibility and content type
- Categorize URLs by type (arrow, components, accessories)
- Update `config/manufacturers.yaml` automatically
- Prevent duplicate URLs

**Implementation**:
```python
# CLI Arguments
parser.add_argument('--add', action='store_true', help='Add URL to manufacturer config')
parser.add_argument('--manufacturer', help='Manufacturer name')
parser.add_argument('--type', help='Content type: arrow, components, accessories')
parser.add_argument('--url', help='URL to add')

# URL Management Class
class URLManager:
    def add_url(self, manufacturer: str, url_type: str, url: str)
    def validate_url(self, url: str) -> bool
    def categorize_content(self, url: str) -> str
    def update_config(self, manufacturer: str, url_type: str, url: str)
```

### 1.2 URL Discovery (`--add-list` command)
**Command**: `python main.py --add-list type=components http://url`

**Features**:
- Crawl page to discover related URLs
- Extract product/component links automatically
- Filter URLs by content type and relevance
- Bulk add discovered URLs to configuration
- Generate report of discovered content

**Implementation**:
```python
# URL Discovery Class
class URLDiscovery:
    def discover_urls(self, base_url: str, content_type: str) -> List[str]
    def extract_product_links(self, html: str, base_url: str) -> List[str]
    def filter_by_type(self, urls: List[str], content_type: str) -> List[str]
    def validate_discovered_urls(self, urls: List[str]) -> List[str]
```

## 📋 Phase 2: Component Database System

### 2.1 Database Schema Extension
**New Tables**:
```sql
-- Component Categories
CREATE TABLE component_categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,  -- points, nocks, fletchings, inserts
    description TEXT
);

-- Components (Points, Nocks, etc.)
CREATE TABLE components (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    manufacturer TEXT NOT NULL,
    model_name TEXT NOT NULL,
    specifications TEXT,  -- JSON field for type-specific specs
    compatibility_data TEXT,  -- JSON field for compatibility rules
    image_url TEXT,
    price_range TEXT,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES component_categories (id)
);

-- Arrow-Component Compatibility
CREATE TABLE arrow_component_compatibility (
    id INTEGER PRIMARY KEY,
    arrow_id INTEGER NOT NULL,
    component_id INTEGER NOT NULL,
    compatibility_type TEXT,  -- direct, universal, adapter_required
    notes TEXT,
    verified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (arrow_id) REFERENCES arrows (id),
    FOREIGN KEY (component_id) REFERENCES components (id),
    UNIQUE(arrow_id, component_id)
);
```

### 2.2 Component Types & Specifications

**Points (Broadheads/Field Points)**:
```python
{
    "weight": "100gr, 125gr, 150gr",
    "thread_type": "8-32, 5/16-24",
    "diameter": "0.945", 
    "length": "2.5",
    "material": "stainless_steel",
    "point_type": "field, broadhead, blunt"
}
```

**Nocks**:
```python
{
    "nock_size": "0.244, 0.246, 0.300",
    "fit_type": "push_in, snap_on, pin",
    "material": "plastic, aluminum",
    "colors": ["red", "yellow", "green"],
    "weight": "7gr"
}
```

**Fletchings**:
```python
{
    "length": "4", 
    "height": "0.5",
    "material": "plastic, feather",
    "profile": "low, high, parabolic",
    "attachment": "adhesive, wrap"
}
```

**Inserts**:
```python
{
    "outer_diameter": "0.244",
    "inner_diameter": "0.166", 
    "thread": "8-32",
    "length": "0.5",
    "weight": "12gr",
    "material": "aluminum, stainless"
}
```

## 📋 Phase 3: Component Extraction System

### 3.1 Component Extractors
**Base Component Extractor**:
```python
class ComponentExtractor:
    def extract_component_data(self, html: str, url: str) -> List[Dict]
    def identify_component_type(self, content: str) -> str
    def extract_specifications(self, content: str, component_type: str) -> Dict
    def extract_compatibility_info(self, content: str) -> Dict
```

**Specialized Extractors**:
- `PointExtractor` - Broadheads, field points, blunts
- `NockExtractor` - Push-in nocks, snap-on nocks  
- `FletchingExtractor` - Vanes, feathers
- `InsertExtractor` - Arrow inserts and outserts

### 3.2 Compatibility Matching Engine
```python
class CompatibilityEngine:
    def match_components_to_arrow(self, arrow_id: int) -> Dict[str, List[Component]]
    def check_nock_compatibility(self, arrow: Arrow, nock: Component) -> bool
    def check_point_compatibility(self, arrow: Arrow, point: Component) -> bool
    def check_insert_compatibility(self, arrow: Arrow, insert: Component) -> bool
    def calculate_compatibility_score(self, arrow: Arrow, component: Component) -> float
```

## 📋 Phase 4: API & Frontend Integration

### 4.1 Component API Endpoints
```python
# Component endpoints
@app.route('/api/components/<category>')
def get_components_by_category(category: str)

@app.route('/api/arrows/<arrow_id>/compatible-components')
def get_compatible_components(arrow_id: int)

@app.route('/api/components/<component_id>/compatible-arrows') 
def get_compatible_arrows(component_id: int)

# Search endpoints
@app.route('/api/components/search')
def search_components()
```

### 4.2 Frontend Component Display
- **Arrow Detail Page**: Show compatible components tabs
- **Component Search**: Dedicated component search interface
- **Compatibility Matrix**: Visual compatibility chart
- **Build Recommendations**: Complete arrow build suggestions

## 📋 Implementation Priority

### 🚀 **HIGH PRIORITY** (Week 1-2)
1. ✅ **URL Management CLI** - `--add` and `--add-list` commands
2. ✅ **URL Validation System** - Ensure URLs are valid and accessible
3. ✅ **Config Management** - Automatic updates to manufacturers.yaml

### 🎯 **MEDIUM PRIORITY** (Week 3-4)  
4. ✅ **Component Database Schema** - Design and implement tables
5. ✅ **Basic Component Extractors** - Start with points and nocks
6. ✅ **Component API Endpoints** - Basic CRUD operations

### 📈 **LOW PRIORITY** (Week 5-6)
7. ✅ **Compatibility Engine** - Match components to arrows
8. ✅ **Advanced Extractors** - Fletchings, inserts, accessories
9. ✅ **Frontend Integration** - Component display in UI

## 🔧 Technical Considerations

### URL Management
- **Rate Limiting**: Respect robots.txt and implement delays
- **Duplicate Detection**: SHA-256 hashing of normalized URLs
- **Content Validation**: Verify pages contain expected content types
- **Error Handling**: Graceful handling of 404s, timeouts, redirects

### Component Extraction
- **Multi-format Support**: Handle tables, lists, product grids
- **Specification Parsing**: Extract measurements, weights, materials
- **Image Extraction**: Download and process component images
- **Translation Support**: Extend DeepSeek translation to components

### Database Design
- **Normalization**: Proper foreign key relationships
- **Indexing**: Performance optimization for searches
- **Versioning**: Track changes to component specifications
- **Bulk Operations**: Efficient batch inserts and updates

## 📊 Success Metrics

### Phase 1 Completion
- ✅ CLI commands working for URL management
- ✅ 50+ new URLs discovered and added automatically
- ✅ Zero duplicate URLs in configuration

### Phase 2 Completion  
- ✅ Component database schema implemented
- ✅ 500+ components extracted and categorized
- ✅ Basic compatibility matching functional

### Phase 3 Completion
- ✅ 90%+ accuracy in component-arrow matching
- ✅ Complete API coverage for components
- ✅ Frontend integration showing compatible components

## 🚀 Getting Started

### Prerequisites
```bash
# Install additional dependencies
pip install validators beautifulsoup4 urllib3

# Test current scraper functionality
python main.py --list-manufacturers
```

### Development Workflow
```bash
# 1. Implement URL management
python main.py --add manufacturer=easton type=arrow http://example.com

# 2. Test URL discovery
python main.py --add-list type=components http://manufacturer-page.com

# 3. Verify configuration updates
python main.py --list-manufacturers

# 4. Run component extraction
python main.py --update-components manufacturer=easton
```

This enhancement plan transforms the arrow scraper from a simple data collector into a comprehensive archery equipment database with intelligent URL management and component integration capabilities.