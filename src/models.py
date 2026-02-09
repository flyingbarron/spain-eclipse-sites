"""
Data Models for Eclipse Site Data
Defines dataclasses for type-safe site data handling
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any


@dataclass
class Site:
    """Represents a geological site with eclipse and cloud data"""
    
    # Core site information
    code: str
    denominacion: str
    url: str
    valor_turistico: str
    confidencialidad: str
    route_difficulty: str
    
    # Location data
    latitude: str = 'N/A'
    longitude: str = 'N/A'
    
    # Eclipse visibility data
    eclipse_visibility: str = 'not_checked'
    
    # Cloud coverage data
    cloud_coverage: Optional[int] = None
    cloud_status: str = 'not_checked'
    cloud_url: Optional[str] = None
    
    # Horizon image data
    horizon_status: str = 'not_checked'
    
    # Processing status
    status: str = 'pending'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert site to dictionary for CSV/JSON export
        
        Returns:
            Dictionary representation of the site
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Site':
        """Create Site instance from dictionary
        
        Args:
            data: Dictionary with site data
            
        Returns:
            Site instance
        """
        # Filter out any keys that aren't in the dataclass
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
    
    @property
    def has_coordinates(self) -> bool:
        """Check if site has valid coordinates
        
        Returns:
            True if site has valid latitude and longitude
        """
        return self.latitude != 'N/A' and self.longitude != 'N/A'
    
    @property
    def lat_float(self) -> Optional[float]:
        """Get latitude as float
        
        Returns:
            Latitude as float or None if invalid
        """
        try:
            return float(self.latitude) if self.latitude != 'N/A' else None
        except (ValueError, TypeError):
            return None
    
    @property
    def lon_float(self) -> Optional[float]:
        """Get longitude as float
        
        Returns:
            Longitude as float or None if invalid
        """
        try:
            return float(self.longitude) if self.longitude != 'N/A' else None
        except (ValueError, TypeError):
            return None
    
    @property
    def tourist_value_float(self) -> Optional[float]:
        """Get tourist value as float
        
        Returns:
            Tourist value as float or None if invalid
        """
        try:
            return float(self.valor_turistico)
        except (ValueError, TypeError):
            return None
    
    @property
    def tourist_value_category(self) -> str:
        """Get tourist value category
        
        Returns:
            'High', 'Medium', 'Lower', or 'Unknown'
        """
        value = self.tourist_value_float
        if value is None:
            return 'Unknown'
        elif value > 5.0:
            return 'High'
        elif value >= 4.0:
            return 'Medium'
        else:
            return 'Lower'
    
    @property
    def is_eclipse_visible(self) -> bool:
        """Check if eclipse is visible from this site
        
        Returns:
            True if eclipse is visible
        """
        return self.eclipse_visibility == 'visible'
    
    @property
    def has_low_cloud_coverage(self) -> bool:
        """Check if site has low cloud coverage (<30%)
        
        Returns:
            True if cloud coverage is less than 30%
        """
        return self.cloud_coverage is not None and self.cloud_coverage < 30
    
    @property
    def cloud_emoji(self) -> str:
        """Get emoji representing cloud coverage
        
        Returns:
            Emoji string: ☀️ (low), ⛅ (medium), ☁️ (high), or ❓ (unknown)
        """
        if self.cloud_coverage is None:
            return '❓'
        elif self.cloud_coverage < 30:
            return '☀️'
        elif self.cloud_coverage < 60:
            return '⛅'
        else:
            return '☁️'
    
    def __str__(self) -> str:
        """String representation of site
        
        Returns:
            Human-readable string
        """
        return f"Site({self.code}: {self.denominacion})"
    
    def __repr__(self) -> str:
        """Developer representation of site
        
        Returns:
            Detailed string representation
        """
        return (f"Site(code='{self.code}', denominacion='{self.denominacion}', "
                f"tourist_value={self.valor_turistico}, eclipse={self.eclipse_visibility})")


# Helper functions for working with Site objects

def sites_to_dicts(sites: list[Site]) -> list[Dict[str, Any]]:
    """Convert list of Site objects to list of dictionaries
    
    Args:
        sites: List of Site objects
        
    Returns:
        List of dictionaries
    """
    return [site.to_dict() for site in sites]


def dicts_to_sites(dicts: list[Dict[str, Any]]) -> list[Site]:
    """Convert list of dictionaries to list of Site objects
    
    Args:
        dicts: List of dictionaries with site data
        
    Returns:
        List of Site objects
    """
    return [Site.from_dict(d) for d in dicts]

# Made with Bob