"""
IGME Site Scraper Module
Functions for scraping geological site data from IGME IELIG database
"""

import requests
from bs4 import BeautifulSoup
import re
import math
import time


def generate_urls(specific_code=None):
    """Generate URLs from IB200, IB200a to IB200z, IB034, and IB034a to IB034z
    
    Args:
        specific_code: If provided, only generate URL for this specific code
    
    Returns:
        List of tuples (code, url)
    """
    urls = []
    
    if specific_code:
        code = specific_code.upper()
        url = f"https://info.igme.es/ielig/LIGInfo.aspx?codigo={code}"
        return [(code, url)]
    
    # IB200 without letter suffix
    urls.append(("IB200", "https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB200"))
    
    # IB200a to IB200z
    base_url_200 = "https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB200"
    for char_code in range(ord('a'), ord('z') + 1):
        code = f"IB200{chr(char_code)}"
        url = f"{base_url_200}{chr(char_code)}"
        urls.append((code, url))
    
    # IB034 without letter suffix
    urls.append(("IB034", "https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB034"))
    
    # IB034a to IB034z
    base_url_034 = "https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB034"
    for char_code in range(ord('a'), ord('z') + 1):
        code = f"IB034{chr(char_code)}"
        url = f"{base_url_034}{chr(char_code)}"
        urls.append((code, url))
    
    return urls


def clean_site_name(name):
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


def extract_site_name(html_content):
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


def extract_tourist_value(html_content):
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


def extract_confidencialidad(html_content):
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


def extract_route_difficulty(html_content):
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


def web_mercator_to_lat_lon(x, y):
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


def calculate_polygon_centroid(rings):
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


def get_coordinates_from_api(code):
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


def scrape_site(code, url):
    """Scrape a single IGME site
    
    Args:
        code: Site code
        url: Site URL
    
    Returns:
        Dictionary with site data or None if scraping failed
    """
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


def scrape_all_sites(specific_code=None):
    """Scrape all IGME sites
    
    Args:
        specific_code: If provided, only scrape this specific site
    
    Returns:
        List of site dictionaries
    """
    urls = generate_urls(specific_code)
    results = []
    
    print(f"Scraping {len(urls)} IGME sites...")
    print("-" * 60)
    
    for code, url in urls:
        print(f"\n[{code}] Scraping IGME data...")
        
        site_data = scrape_site(code, url)
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
        
        time.sleep(1)  # Be polite to the server
    
    return results

# Made with Bob
