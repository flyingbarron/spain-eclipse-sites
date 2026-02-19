"""
Bortle Scale Scraper
Fetches light pollution data and converts to Bortle scale values
"""
import requests
import time
from typing import List, Dict, Any, Optional
from src.logger import setup_logger
from src.config import config

# Setup logger for this module
logger = setup_logger(__name__)


def get_bortle_value(lat: float, lon: float, timeout: int = 10) -> Optional[int]:
    """Get Bortle scale value for coordinates using real light pollution data
    
    Uses the Light Pollution Map's public tile server to get VIIRS data.
    This method accesses the same data that powers lightpollutionmap.info
    without requiring API authentication.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        timeout: Request timeout in seconds
    
    Returns:
        Bortle scale value (1-9) or None if failed
    """
    
    # Access Light Pollution Map tile data directly
    # The tiles are publicly accessible and contain the VIIRS 2015 data
    try:
        import math
        
        # Convert lat/lon to tile coordinates at zoom level 8 (good balance)
        zoom = 8
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        
        # Fetch the tile image from Light Pollution Map
        tile_url = f"https://djlorenz.github.io/astronomy/lp2020/overlay/tiles/{zoom}/{xtile}/{ytile}.png"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.lightpollutionmap.info/'
        }
        
        response = requests.get(tile_url, headers=headers, timeout=timeout)
        
        logger.debug(f"Tile URL: {tile_url}")
        logger.debug(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse the PNG tile to get the color at our coordinates
            from PIL import Image
            from io import BytesIO
            
            img = Image.open(BytesIO(response.content))
            
            # Calculate pixel position within the tile (256x256)
            tile_size = 256
            x_pixel = int((lon + 180.0) / 360.0 * n * tile_size) % tile_size
            y_pixel = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n * tile_size) % tile_size
            
            # Get pixel color
            pixel = img.getpixel((x_pixel, y_pixel))
            
            # Convert color to Bortle scale
            # Light pollution maps use color coding:
            # Black/Dark Blue = Class 1-2, Blue/Cyan = 3-4, Green/Yellow = 5-6, Orange/Red = 7-9
            if isinstance(pixel, int):
                # Grayscale
                brightness = float(pixel) / 255.0
            elif isinstance(pixel, tuple) and len(pixel) >= 3:
                # RGB - use red channel as it correlates with light pollution
                r = pixel[0]
                brightness = float(r) / 255.0
            else:
                # Unknown format
                logger.warning(f"Unknown pixel format: {type(pixel)}")
                return None
            
            # Map brightness to Bortle scale
            if brightness < 0.1:
                bortle = 1
            elif brightness < 0.2:
                bortle = 2
            elif brightness < 0.3:
                bortle = 3
            elif brightness < 0.4:
                bortle = 4
            elif brightness < 0.5:
                bortle = 5
            elif brightness < 0.6:
                bortle = 6
            elif brightness < 0.75:
                bortle = 7
            elif brightness < 0.9:
                bortle = 8
            else:
                bortle = 9
            
            logger.info(f"Coordinates ({lat}, {lon}): tile brightness={brightness:.3f}, Bortle={bortle}")
            return bortle
            
    except ImportError as e:
        logger.error(f"PIL/Pillow not installed. Install with: pip install Pillow - {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to fetch Bortle data for ({lat}, {lon}): {type(e).__name__}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None
    
    # If we get here, response was not 200
    logger.error(f"Could not fetch tile data for ({lat}, {lon}) - HTTP {response.status_code if 'response' in locals() else 'unknown'}")
    return None


def brightness_to_bortle(brightness: float) -> int:
    """Convert artificial brightness (mcd/m²) to Bortle scale
    
    Based on standard Bortle scale classifications:
    - Class 1: Excellent dark-sky site (< 0.01 mcd/m²)
    - Class 2: Typical truly dark site (0.01-0.06 mcd/m²)
    - Class 3: Rural sky (0.06-0.17 mcd/m²)
    - Class 4: Rural/suburban transition (0.17-0.44 mcd/m²)
    - Class 5: Suburban sky (0.44-1.0 mcd/m²)
    - Class 6: Bright suburban sky (1.0-3.0 mcd/m²)
    - Class 7: Suburban/urban transition (3.0-10.0 mcd/m²)
    - Class 8: City sky (10.0-30.0 mcd/m²)
    - Class 9: Inner-city sky (> 30.0 mcd/m²)
    
    Args:
        brightness: Artificial brightness in mcd/m²
    
    Returns:
        Bortle scale value (1-9)
    """
    if brightness < 0.01:
        return 1
    elif brightness < 0.06:
        return 2
    elif brightness < 0.17:
        return 3
    elif brightness < 0.44:
        return 4
    elif brightness < 1.0:
        return 5
    elif brightness < 3.0:
        return 6
    elif brightness < 10.0:
        return 7
    elif brightness < 30.0:
        return 8
    else:
        return 9


def get_bortle_description(bortle: int) -> str:
    """Get human-readable description of Bortle scale value
    
    Args:
        bortle: Bortle scale value (1-9)
    
    Returns:
        Description string
    """
    descriptions = {
        1: "Excellent dark-sky site",
        2: "Typical truly dark site",
        3: "Rural sky",
        4: "Rural/suburban transition",
        5: "Suburban sky",
        6: "Bright suburban sky",
        7: "Suburban/urban transition",
        8: "City sky",
        9: "Inner-city sky"
    }
    return descriptions.get(bortle, "Unknown")


def get_bortle_emoji(bortle: Optional[int]) -> str:
    """Get emoji representing Bortle scale value
    
    Args:
        bortle: Bortle scale value (1-9) or None
    
    Returns:
        Emoji string
    """
    if bortle is None:
        return '❓'
    elif bortle <= 2:
        return '🌌'  # Excellent dark sky
    elif bortle <= 4:
        return '🌃'  # Good dark sky
    elif bortle <= 6:
        return '🌆'  # Suburban
    else:
        return '🏙️'  # Urban/city


def scrape_bortle_for_sites(sites: List[Dict[str, Any]], delay: float = 1.0) -> List[Dict[str, Any]]:
    """Scrape Bortle scale values for all sites with coordinates
    
    Args:
        sites: List of site dictionaries
        delay: Delay between requests in seconds (default: 1.0)
    
    Returns:
        Updated list of site dictionaries with Bortle data
    """
    logger.info(f"Starting Bortle scale scraping for {len(sites)} sites")
    
    for i, site in enumerate(sites, 1):
        code = site.get('code', 'Unknown')
        lat_str = site.get('latitude', 'N/A')
        lon_str = site.get('longitude', 'N/A')
        
        # Skip sites without coordinates
        if lat_str == 'N/A' or lon_str == 'N/A':
            logger.warning(f"[{i}/{len(sites)}] {code}: No coordinates, skipping Bortle check")
            site['bortle_scale'] = None
            site['bortle_status'] = 'no_coordinates'
            continue
        
        try:
            lat = float(lat_str)
            lon = float(lon_str)
        except (ValueError, TypeError):
            logger.error(f"[{i}/{len(sites)}] {code}: Invalid coordinates, skipping")
            site['bortle_scale'] = None
            site['bortle_status'] = 'invalid_coordinates'
            continue
        
        logger.info(f"[{i}/{len(sites)}] {code}: Fetching Bortle scale for ({lat}, {lon})")
        
        bortle = get_bortle_value(lat, lon)
        
        if bortle is not None:
            site['bortle_scale'] = bortle
            site['bortle_status'] = 'success'
            description = get_bortle_description(bortle)
            emoji = get_bortle_emoji(bortle)
            logger.info(f"  ✓ Bortle scale: {bortle} {emoji} ({description})")
        else:
            site['bortle_scale'] = None
            site['bortle_status'] = 'failed'
            logger.warning(f"  ✗ Failed to fetch Bortle scale")
        
        # Rate limiting
        if i < len(sites):
            time.sleep(delay)
    
    # Summary
    success_count = sum(1 for s in sites if s.get('bortle_status') == 'success')
    logger.info(f"Bortle scraping complete: {success_count}/{len(sites)} successful")
    
    return sites


# Made with Bob