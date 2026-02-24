"""
IGME Site Scraper Module
Functions for scraping geological site data from IGME IELIG database
"""

import requests
from bs4 import BeautifulSoup
import re
import math
import time
import json
import os
from typing import List, Tuple, Optional, Dict, Any


def load_sites_config(config_path: str = "data/igme_sites_config.json") -> Dict[str, Any]:
    """Load site configuration from JSON file
    
    Args:
        config_path: Path to the config file
    
    Returns:
        Configuration dictionary
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_urls(specific_code: Optional[str] = None, config_path: str = "data/igme_sites_config.json") -> List[Tuple[str, str, Optional[Dict[str, Any]]]]:
    """Generate URLs from configuration file
    
    Args:
        specific_code: If provided, only generate URL for this specific code
        config_path: Path to the configuration file
    
    Returns:
        List of tuples (code, url, custom_data) where custom_data is None for IGME sites
        or a dict with custom site information
    """
    urls: List[Tuple[str, str, Optional[Dict[str, Any]]]] = []
    
    # Load configuration
    try:
        config = load_sites_config(config_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        return urls
    
    base_url = config.get('base_url', 'https://info.igme.es/ielig/LIGInfo.aspx?codigo=')
    excluded_codes = set(code.upper() for code in config.get('excluded_codes', []))
    
    if specific_code:
        code = specific_code.upper()
        # Check if code is excluded
        if code in excluded_codes:
            print(f"Warning: {code} is in excluded_codes list")
            return []
        # Check if it's a custom site
        for custom_site in config.get('custom_sites', []):
            if custom_site['code'].upper() == code:
                return [(code, f"{base_url}{code}", custom_site)]
        # Not a custom site, return as regular IGME site
        url = f"{base_url}{code}"
        return [(code, url, None)]
    
    # Process site series (e.g., IB200, IB200a-z)
    for series in config.get('site_series', []):
        base_code = series['base_code']
        
        # Add base code if specified and not excluded
        if series.get('include_base', False):
            if base_code.upper() not in excluded_codes:
                urls.append((base_code, f"{base_url}{base_code}", None))
        
        # Add suffixed codes if specified
        suffixes = series.get('suffixes', '')
        if suffixes == 'a-z':
            for char_code in range(ord('a'), ord('z') + 1):
                code = f"{base_code}{chr(char_code)}"
                # Skip if excluded
                if code.upper() not in excluded_codes:
                    url = f"{base_url}{code}"
                    urls.append((code, url, None))
    
    # Process individual sites (skip if excluded)
    for site in config.get('individual_sites', []):
        code = site['code']
        if code.upper() not in excluded_codes:
            urls.append((code, f"{base_url}{code}", None))
    
    # Process custom sites (skip if excluded)
    for custom_site in config.get('custom_sites', []):
        code = custom_site['code']
        if code.upper() not in excluded_codes:
            urls.append((code, f"{base_url}{code}", custom_site))
    
    return urls


def clean_site_name(name: str) -> str:
    """Remove repeated prefixes from site names
    
    Args:
        name: Raw site name from IGME
    
    Returns:
        Cleaned site name
    """
    if not name or name == 'N/A':
        return name
    
    prefixes_to_remove = [
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja).  Yacimiento de ",
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja). Yacimiento de ",
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja). Yacimientos de ",
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja). Yacimiento ",
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja).Yacimiento de ",
        "Icnitas de dinosaurio del Weald de Cameros (Soria). ",
        "Icnitas de dinosaurio del Weald de Cameros (Soria).",
    ]
    
    cleaned = name
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break
    
    return cleaned.strip().strip('.')


def extract_site_name(html_content: str) -> Optional[str]:
    """Extract the site name (Denominación) from HTML content
    
    Args:
        html_content: HTML page content
    
    Returns:
        Site name or None
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    dt_tags = soup.find_all('dt')
    for dt in dt_tags:
        if 'Denominación' in dt.get_text():
            dd = dt.find_next_sibling('dd')
            if dd:
                raw_name = dd.get_text().strip()
                return clean_site_name(raw_name)
    return None


def extract_tourist_value(html_content: str) -> Optional[str]:
    """Extract the tourist value (VT) from HTML content
    
    Args:
        html_content: HTML page content
    
    Returns:
        Tourist value as string or None
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    dt_tags = soup.find_all('dt')
    for dt in dt_tags:
        if 'Valor turístico (VT)' in dt.get_text():
            dd = dt.find_next_sibling('dd')
            if dd:
                text = dd.get_text().strip()
                match = re.search(r'(\d+(?:\.\d+)?)', text)
                if match:
                    return match.group(1)
    return None


def extract_confidencialidad(html_content: str) -> Optional[str]:
    """Extract the Confidencialidad (privacy status) from HTML content
    
    Args:
        html_content: HTML page content
    
    Returns:
        'Public', 'Private', or None
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    dt_tags = soup.find_all('dt')
    for dt in dt_tags:
        if 'Confidencialidad' in dt.get_text():
            dd = dt.find_next_sibling('dd')
            if dd:
                value = dd.get_text().strip().rstrip('.')
                if value == 'Público':
                    return 'Public'
                elif value == 'Privado':
                    return 'Private'
                else:
                    return value
    return None


def extract_route_difficulty(html_content: str) -> Optional[str]:
    """Extract the Dificultad itinerario (route difficulty) from HTML content
    
    Args:
        html_content: HTML page content
    
    Returns:
        Translated difficulty level or None
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    dt_tags = soup.find_all('dt')
    for dt in dt_tags:
        if 'Dificultad itinerario' in dt.get_text():
            dd = dt.find_next_sibling('dd')
            if dd:
                value = dd.get_text().strip().rstrip('.')
                # Translate Spanish to English
                translations = {
                    'Baja': 'Low',
                    'Media': 'Medium',
                    'Alta': 'High',
                    'Muy alta': 'Very High'
                }
                return translations.get(value, value)
    return None


def web_mercator_to_lat_lon(x: float, y: float) -> Tuple[float, float]:
    """Convert Web Mercator (EPSG:3857) to WGS84 lat/lon (EPSG:4326)
    
    Args:
        x: X coordinate in Web Mercator
        y: Y coordinate in Web Mercator
    
    Returns:
        Tuple of (latitude, longitude)
    """
    lon = (x / 20037508.34) * 180
    lat = (y / 20037508.34) * 180
    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) - math.pi / 2)
    return lat, lon


def calculate_polygon_centroid(rings: List[List[List[float]]]) -> Tuple[Optional[float], Optional[float]]:
    """Calculate the centroid of a polygon from its rings
    
    Args:
        rings: List of polygon rings (list of coordinate pairs)
    
    Returns:
        Tuple of (latitude, longitude) or (None, None)
    """
    if not rings or not rings[0]:
        return None, None
    
    coords = rings[0]
    x_sum = sum(point[0] for point in coords)
    y_sum = sum(point[1] for point in coords)
    n = len(coords)
    
    centroid_x = x_sum / n
    centroid_y = y_sum / n
    
    lat, lon = web_mercator_to_lat_lon(centroid_x, centroid_y)
    return lat, lon


def get_coordinates_from_api(code: str) -> Tuple[Optional[float], Optional[float]]:
    """Get coordinates from IGME MapServer API
    
    Args:
        code: Site code (e.g., 'IB200a')
    
    Returns:
        Tuple of (latitude, longitude) or (None, None)
    """
    try:
        api_url = f"https://mapas.igme.es/gis/rest/services/BasesDatos/IGME_IELIG/MapServer/0/query?where=codigo='{code}'&outFields=*&f=json"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('features') and len(data['features']) > 0:
            feature = data['features'][0]
            geometry = feature.get('geometry')
            
            if geometry and geometry.get('rings'):
                lat, lon = calculate_polygon_centroid(geometry['rings'])
                return lat, lon
        
        return None, None
        
    except Exception as e:
        print(f"    ✗ Error getting coordinates: {str(e)}")
        return None, None


def scrape_site(code: str, url: str, custom_data: Optional[Dict[str, Any]] = None,
                config_path: str = "data/igme_sites_config.json") -> Optional[Dict[str, Any]]:
    """Scrape a single IGME site or use custom site data
    
    Args:
        code: Site code
        url: Site URL
        custom_data: Custom site data (name, lat, lon) if not an IGME site
        config_path: Path to config file for default values
    
    Returns:
        Dictionary with site data or None if scraping failed
    """
    # Load config for default values
    try:
        config = load_sites_config(config_path)
        defaults = config.get('default_values', {})
    except:
        defaults = {}
    
    # If this is a custom site, use provided data with defaults
    if custom_data:
        print(f"  ℹ Using custom site data")
        return {
            'code': code,
            'denominacion': custom_data.get('name', 'N/A'),
            'url': 'N/A',  # Custom sites don't have IGME URLs
            'valor_turistico': defaults.get('valor_turistico', '5.0'),
            'confidencialidad': defaults.get('confidencialidad', 'Public'),
            'route_difficulty': defaults.get('route_difficulty', 'Medium'),
            'latitude': f"{custom_data.get('latitude', 0):.6f}",
            'longitude': f"{custom_data.get('longitude', 0):.6f}",
            'status': 'custom'
        }
    
    # Otherwise, scrape from IGME
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract site information
        site_name = extract_site_name(response.text)
        tourist_value = extract_tourist_value(response.text)
        confidencialidad = extract_confidencialidad(response.text)
        route_difficulty = extract_route_difficulty(response.text)
        lat, lon = get_coordinates_from_api(code)
        
        if not tourist_value:
            return None
        
        return {
            'code': code,
            'denominacion': site_name if site_name else 'N/A',
            'url': url,
            'valor_turistico': tourist_value,
            'confidencialidad': confidencialidad if confidencialidad else 'N/A',
            'route_difficulty': route_difficulty if route_difficulty else 'N/A',
            'latitude': f"{lat:.6f}" if lat else 'N/A',
            'longitude': f"{lon:.6f}" if lon else 'N/A',
            'status': 'success'
        }
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return None


def scrape_all_sites(specific_code: Optional[str] = None) -> List[Dict[str, Any]]:
    """Scrape all IGME sites and custom sites
    
    Args:
        specific_code: If provided, only scrape this specific site
    
    Returns:
        List of site dictionaries
    """
    urls = generate_urls(specific_code)
    results: List[Dict[str, Any]] = []
    
    print(f"Scraping {len(urls)} sites (IGME + custom)...")
    print("-" * 60)
    
    for code, url, custom_data in urls:
        if custom_data:
            print(f"\n[{code}] Processing custom site...")
        else:
            print(f"\n[{code}] Scraping IGME data...")
        
        site_data = scrape_site(code, url, custom_data)
        if site_data:
            print(f"  ✓ VT: {site_data['valor_turistico']}")
            if site_data['confidencialidad'] != 'N/A':
                print(f"  ✓ Privacy: {site_data['confidencialidad']}")
            if site_data['route_difficulty'] != 'N/A':
                print(f"  ✓ Route Difficulty: {site_data['route_difficulty']}")
            if site_data['latitude'] != 'N/A':
                print(f"  ✓ Coordinates: {site_data['latitude']}, {site_data['longitude']}")
            results.append(site_data)
        else:
            print(f"  ✗ VT not found - skipping site")
        
        # Only sleep for IGME sites to be polite to their server
        if not custom_data:
            time.sleep(1)
    
    return results

# Made with Bob
