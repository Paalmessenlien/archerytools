from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

class ArrowType(str, Enum):
    HUNTING = "hunting"
    TARGET = "target"
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    THREE_D = "3d"
    RECREATIONAL = "recreational"

class DiameterCategory(str, Enum):
    ULTRA_THIN = "ultra_thin"      # .166" - Ultra-thin for target arrows
    THIN = "thin"                  # .204" - Thin for 3D and target
    SMALL_HUNTING = "small_hunting" # .244" - Small hunting diameter
    STANDARD_TARGET = "standard_target" # .246" - Common target/hunting
    STANDARD_HUNTING = "standard_hunting" # .300" - Standard hunting
    LARGE_HUNTING = "large_hunting"    # .340" - Larger hunting
    HEAVY_HUNTING = "heavy_hunting"    # .400"+ - Heavy/traditional hunting

def classify_diameter(diameter: float) -> DiameterCategory:
    """Classify arrow diameter into standard categories"""
    if diameter <= 0.166:
        return DiameterCategory.ULTRA_THIN
    elif diameter <= 0.210:  # .204" with small tolerance
        return DiameterCategory.THIN
    elif diameter <= 0.245:  # .244" with tolerance
        return DiameterCategory.SMALL_HUNTING
    elif diameter <= 0.260:  # .246" with tolerance
        return DiameterCategory.STANDARD_TARGET
    elif diameter <= 0.320:  # .300" with tolerance
        return DiameterCategory.STANDARD_HUNTING  
    elif diameter <= 0.360:  # .340" with tolerance
        return DiameterCategory.LARGE_HUNTING
    else:  # .400" and above
        return DiameterCategory.HEAVY_HUNTING

class SpineSpecification(BaseModel):
    """Specifications for a single spine value"""
    spine: int = Field(..., description="Spine value (stiffness)")
    outer_diameter: float = Field(..., description="Arrow outer diameter in inches")
    gpi_weight: float = Field(..., description="Grains per inch weight")
    inner_diameter: Optional[float] = Field(None, description="Arrow inner diameter in inches")
    length_options: Optional[List[float]] = Field(None, description="Available shaft lengths for this spine")
    diameter_category: Optional[DiameterCategory] = Field(None, description="Categorized diameter classification")
    
    @validator('spine')
    def validate_spine(cls, v):
        if v <= 0 or v > 2000:  # Reasonable spine range
            raise ValueError('Spine must be between 0 and 2000')
        return v
    
    @validator('outer_diameter')
    def validate_outer_diameter(cls, v):
        if v <= 0 or v > 1.0:  # Reasonable diameter range
            raise ValueError('Outer diameter must be between 0 and 1.0 inches')
        return v
    
    @validator('gpi_weight')
    def validate_gpi_weight(cls, v):
        if v <= 0 or v > 50:  # Reasonable GPI range
            raise ValueError('GPI weight must be between 0 and 50')
        return v
    
    @validator('diameter_category', always=True)
    def set_diameter_category(cls, v, values):
        """Automatically set diameter category based on outer diameter"""
        if 'outer_diameter' in values:
            # Use inner diameter if available, otherwise outer diameter
            diameter = values.get('inner_diameter') or values['outer_diameter']
            return classify_diameter(diameter)
        return v

class ArrowSpecification(BaseModel):
    """Main arrow specification data model with spine-specific variations"""
    
    # Required fields
    manufacturer: str = Field(..., description="Arrow manufacturer name")
    model_name: str = Field(..., description="Arrow model name")
    spine_specifications: List[SpineSpecification] = Field(..., description="Specifications for each spine option")
    
    # Material and construction
    material: Optional[str] = Field(None, description="Arrow material composition")
    carbon_content: Optional[str] = Field(None, description="Carbon fiber content percentage")
    
    # Usage classification
    arrow_type: Optional[ArrowType] = Field(None, description="Primary arrow type/category")
    recommended_use: Optional[List[str]] = Field(None, description="All recommended use cases")
    description: Optional[str] = Field(None, description="Brief description of arrow features and purpose")
    
    # Visual information
    primary_image_url: Optional[str] = Field(None, description="URL of main arrow product image")
    gallery_images: Optional[List[str]] = Field(None, description="URLs of additional arrow images")
    saved_images: Optional[List[str]] = Field(None, description="Local paths to downloaded images")
    
    # Technical specifications
    straightness_tolerance: Optional[str] = Field(None, description="Straightness tolerance (e.g., ±0.003)")
    weight_tolerance: Optional[str] = Field(None, description="Weight tolerance (e.g., ±1.0 grain)")
    
    # Commercial information
    price_range: Optional[str] = Field(None, description="Price range or specific price")
    availability: Optional[str] = Field(None, description="Availability status")
    
    # Metadata
    source_url: str = Field(..., description="URL where data was scraped from")
    scraped_at: datetime = Field(default_factory=datetime.now, description="When data was scraped")
    scraper_version: str = Field(default="1.0", description="Version of scraper used")
    
    @validator('spine_specifications')
    def validate_spine_specifications(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one spine specification must be provided')
        
        # Check for duplicate spine values
        spines = [spec.spine for spec in v]
        if len(spines) != len(set(spines)):
            raise ValueError('Duplicate spine values found')
        
        return sorted(v, key=lambda x: x.spine)
    
    def get_spine_options(self) -> List[int]:
        """Get list of available spine values"""
        return [spec.spine for spec in self.spine_specifications]
    
    def get_specification_for_spine(self, spine: int) -> Optional['SpineSpecification']:
        """Get specification for a specific spine value"""
        for spec in self.spine_specifications:
            if spec.spine == spine:
                return spec
        return None
    
    def get_diameter_range(self) -> tuple[float, float]:
        """Get min and max outer diameter across all spines"""
        diameters = [spec.outer_diameter for spec in self.spine_specifications]
        return (min(diameters), max(diameters))
    
    def get_gpi_range(self) -> tuple[float, float]:
        """Get min and max GPI weight across all spines"""
        gpis = [spec.gpi_weight for spec in self.spine_specifications]
        return (min(gpis), max(gpis))
    
    def get_diameter_categories(self) -> List[DiameterCategory]:
        """Get list of unique diameter categories for this arrow"""
        categories = set()
        for spec in self.spine_specifications:
            if spec.diameter_category:
                categories.add(spec.diameter_category)
        return sorted(list(categories), key=lambda x: x.value)
    
    def get_primary_diameter_category(self) -> Optional[DiameterCategory]:
        """Get the most common diameter category, or the first one if tied"""
        categories = self.get_diameter_categories()
        if categories:
            return categories[0]  # Return first/smallest category if multiple
        return None
    
    def get_effective_diameter(self, spine: Optional[int] = None) -> Optional[float]:
        """Get effective diameter (inner diameter preferred) for classification"""
        if spine:
            spec = self.get_specification_for_spine(spine)
            if spec:
                return spec.inner_diameter or spec.outer_diameter
        else:
            # Get from first specification
            if self.spine_specifications:
                spec = self.spine_specifications[0]
                return spec.inner_diameter or spec.outer_diameter
        return None

class ManufacturerData(BaseModel):
    """Container for all arrows from a single manufacturer"""
    
    manufacturer: str = Field(..., description="Manufacturer name")
    arrows: List[ArrowSpecification] = Field(..., description="List of arrow specifications")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    total_arrows: int = Field(default=0, description="Total number of arrows")
    
    @validator('total_arrows', always=True)
    def set_total_arrows(cls, v, values):
        return len(values.get('arrows', []))

class ScrapingResult(BaseModel):
    """Result container for scraping operations"""
    
    success: bool = Field(..., description="Whether scraping was successful")
    url: str = Field(..., description="URL that was scraped")
    arrows_found: int = Field(default=0, description="Number of arrows found")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw scraped data")
    processed_data: Optional[List[ArrowSpecification]] = Field(None, description="Processed arrow specifications")
    processing_time: Optional[float] = Field(None, description="Time taken to process in seconds")

class ScrapingSession(BaseModel):
    """Complete scraping session data"""
    
    session_id: str = Field(..., description="Unique session identifier")
    started_at: datetime = Field(default_factory=datetime.now, description="Session start time")
    completed_at: Optional[datetime] = Field(None, description="Session completion time")
    manufacturer: str = Field(..., description="Target manufacturer")
    urls_scraped: List[str] = Field(default_factory=list, description="URLs processed")
    total_arrows_found: int = Field(default=0, description="Total arrows found in session")
    success_rate: float = Field(default=0.0, description="Percentage of successful scrapes")
    results: List[ScrapingResult] = Field(default_factory=list, description="Individual scraping results")
    
    @validator('success_rate', always=True)
    def calculate_success_rate(cls, v, values):
        results = values.get('results', [])
        if not results:
            return 0.0
        successful = sum(1 for r in results if r.success)
        return (successful / len(results)) * 100