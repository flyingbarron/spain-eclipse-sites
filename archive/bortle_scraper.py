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
    """Get Bortle scale value for coordinates using lightpollutionmap.info PNG tiles
    
    Uses the same PNG tiles that power lightpollutionmap.info website.
    The tiles are color-coded with light pollution data.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        timeout: Request timeout in seconds
    
    Returns:
        Bortle scale value (1-9) or None if failed
    """
    
    try:
        import math
        from io import BytesIO
        from PIL import Image
        
        # Use zoom level 10 for good resolution
        zoom = 10
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        
        # Fetch the PNG tile from lightpollutionmap.info
        tile_url = f"https://www2.lightpollutionmap.info/osm/{zoom}/{xtile}/{ytile}.png"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.lightpollutionmap.info/'
        }
        
        response = requests.get(tile_url, headers=headers, timeout=timeout)
        
        logger.debug(f"PNG tile URL: {tile_url}")
        logger.debug(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Load the PNG image
            try:
                img = Image.open(BytesIO(response.content))
                img = img.convert('RGB')  # Ensure RGB mode
            except Exception as e:
                logger.error(f"Failed to load PNG image: {e}")
                return None
            
            # Calculate pixel position within the tile (256x256)
            tile_size = 256
            x_pixel = int((lon + 180.0) / 360.0 * n * tile_size) % tile_size
            y_pixel = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n * tile_size) % tile_size
            
            # Get the pixel color
            try:
                r, g, b = img.getpixel((x_pixel, y_pixel))
            except Exception as e:
                logger.error(f"Failed to get pixel at ({x_pixel}, {y_pixel}): {e}")
                return None
            
            # Convert RGB color to Bortle scale
            # The lightpollutionmap.info uses a color gradient:
            # Black/Dark Blue (1-2) -> Blue (3) -> Green (4) -> Yellow (5-6) -> Orange (7) -> Red (8-9)
            bortle = rgb_to_bortle(r, g, b)
            
            logger.info(f"Coordinates ({lat}, {lon}): RGB=({r},{g},{b}), Bortle={bortle}")
            return bortle
            
    except Exception as e:
        logger.error(f"Failed to fetch Bortle data for ({lat}, {lon}): {type(e).__name__}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None
    
    # If we get here, response was not 200
    logger.error(f"Could not fetch tile data for ({lat}, {lon}) - HTTP {response.status_code if 'response' in locals() else 'unknown'}")
    return None


def rgb_to_bortle(r: int, g: int, b: int) -> int:
    """Convert RGB color from light pollution map to Bortle scale
    
    The lightpollutionmap.info uses a color gradient to represent light pollution:
    - Black/Very Dark Blue: Bortle 1-2 (excellent dark sky)
    - Dark Blue: Bortle 3 (rural)
    - Blue/Cyan: Bortle 4 (rural/suburban transition)
    - Green: Bortle 5 (suburban)
    - Yellow/Green: Bortle 6 (bright suburban)
    - Orange: Bortle 7 (suburban/urban transition)
    - Red/Orange: Bortle 8 (city)
    - Bright Red/White: Bortle 9 (inner city)
    
    Args:
        r, g, b: RGB color values (0-255)
    
    Returns:
        Bortle scale value (1-9)
    """
    # Calculate color characteristics
    brightness = (r + g + b) / 3.0
    
    # Very dark (black/very dark blue) - Bortle 1-2
    if brightness < 20:
        return 1 if brightness < 10 else 2
    
    # Dark blue - Bortle 3
    if b > r and b > g and brightness < 80:
        return 3
    
    # Blue/Cyan - Bortle 4
    if b >= g and b > r * 1.2 and brightness < 120:
        return 4
    
    # Green dominant - Bortle 5
    if g > r and g > b and brightness < 150:
        return 5
    
    # Yellow/Yellow-Green - Bortle 6
    if r > 100 and g > 100 and b < 100 and brightness < 180:
        return 6
    
    # Orange - Bortle 7
    if r > g * 1.2 and g > b and brightness < 200:
        return 7
    
    # Red/Bright Orange - Bortle 8
    if r > 150 and r > g * 1.3 and brightness < 220:
        return 8
    
    # Very bright (white/bright red) - Bortle 9
    return 9


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