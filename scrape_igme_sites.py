import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import math
import argparse

def generate_urls(specific_code=None):
    """Generate URLs from IB200, IB200a to IB200z, IB034, and IB034a to IB034z
    
    Args:
        specific_code: If provided, only generate URL for this specific code (e.g., 'IB200a')
    
    Returns:
        List of tuples (code, url)
    """
    urls = []
    
    # If specific code is requested, generate only that URL
    if specific_code:
        code = specific_code.upper()
        url = f"https://info.igme.es/ielig/LIGInfo.aspx?codigo={code}"
        return [(code, url)]
    
    # Otherwise, generate all URLs
    # Add IB200 without letter suffix
    urls.append(("IB200", "https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB200"))
    
    # Generate IB200 codes from 'a' to 'z' (ASCII 97 to 122)
    base_url_200 = "https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB200"
    for char_code in range(ord('a'), ord('z') + 1):
        code = f"IB200{chr(char_code)}"
        url = f"{base_url_200}{chr(char_code)}"
        urls.append((code, url))
    
    # Add IB034 without letter suffix
    urls.append(("IB034", "https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB034"))
    
    # Generate IB034 codes from 'a' to 'z' (ASCII 97 to 122)
    base_url_034 = "https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB034"
    for char_code in range(ord('a'), ord('z') + 1):
        code = f"IB034{chr(char_code)}"
        url = f"{base_url_034}{chr(char_code)}"
        urls.append((code, url))
    
    return urls

def clean_site_name(name):
    """Remove repeated prefixes from site names"""
    if not name or name == 'N/A':
        return name
    
    # List of prefixes to remove (order matters - more specific first)
    prefixes_to_remove = [
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja).  Yacimiento de ",  # Double space
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja). Yacimiento de ",
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja). Yacimientos de ",
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja). Yacimiento ",  # Without "de"
        "Icnitas de dinosaurio del Weald de Cameros (La Rioja).Yacimiento de ",
        "Icnitas de dinosaurio del Weald de Cameros (Soria). ",
        "Icnitas de dinosaurio del Weald de Cameros (Soria).",
    ]
    
    cleaned = name
    
    # Remove matching prefix
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break
    
    # Clean up any leading/trailing whitespace or periods
    cleaned = cleaned.strip().strip('.')
    
    return cleaned

def extract_site_name(html_content):
    """Extract the site name (Denominación) from the HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the <dt> tag containing "Denominación"
    dt_tags = soup.find_all('dt')
    for dt in dt_tags:
        if 'Denominación' in dt.get_text():
            # Get the next <dd> sibling tag
            dd = dt.find_next_sibling('dd')
            if dd:
                raw_name = dd.get_text().strip()
                # Clean up the name before returning
                return clean_site_name(raw_name)
    
    return None

def extract_tourist_value(html_content):
    """Extract the tourist value (VT) from the HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the <dt> tag containing "Valor turístico (VT)"
    dt_tags = soup.find_all('dt')
    for dt in dt_tags:
        if 'Valor turístico (VT)' in dt.get_text():
            # Get the next <dd> sibling tag
            dd = dt.find_next_sibling('dd')
            if dd:
                # Extract the text and get just the number
                text = dd.get_text().strip()
                # Use regex to extract the number (e.g., "3.5" from "3.5 (Medio)")
                match = re.search(r'(\d+(?:\.\d+)?)', text)
                if match:
                    return match.group(1)
    
    return None

def extract_confidencialidad(html_content):
    """Extract the Confidencialidad (privacy status) from the HTML content
    Translates Spanish values to English: Público -> Public, Privado -> Private
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the <dt> tag containing "Confidencialidad"
    dt_tags = soup.find_all('dt')
    for dt in dt_tags:
        if 'Confidencialidad' in dt.get_text():
            # Get the next <dd> sibling tag
            dd = dt.find_next_sibling('dd')
            if dd:
                # Strip whitespace and periods
                value = dd.get_text().strip().rstrip('.')
                # Translate Spanish to English
                if value == 'Público':
                    return 'Public'
                elif value == 'Privado':
                    return 'Private'
                else:
                    return value  # Return as-is if not recognized
    
    return None

def web_mercator_to_lat_lon(x, y):
    """Convert Web Mercator (EPSG:3857) coordinates to latitude/longitude (EPSG:4326)"""
    lon = (x / 20037508.34) * 180
    lat = (y / 20037508.34) * 180
    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) - math.pi / 2)
    return lat, lon

def calculate_polygon_centroid(rings):
    """Calculate the centroid of a polygon from its rings"""
    if not rings or not rings[0]:
        return None, None
    
    # Use the first ring (outer boundary)
    coords = rings[0]
    
    # Calculate centroid
    x_sum = sum(point[0] for point in coords)
    y_sum = sum(point[1] for point in coords)
    n = len(coords)
    
    centroid_x = x_sum / n
    centroid_y = y_sum / n
    
    # Convert from Web Mercator to lat/lon
    lat, lon = web_mercator_to_lat_lon(centroid_x, centroid_y)
    
    return lat, lon

def get_coordinates_from_api(code):
    """Get coordinates from IGME MapServer API"""
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

def scrape_sites(specific_code=None):
    """Main function to scrape all sites and save results
    
    Args:
        specific_code: If provided, only scrape this specific site code
    """
    urls = generate_urls(specific_code)
    results = []
    
    print(f"Starting to scrape {len(urls)} websites...")
    print("-" * 60)
    
    for code, url in urls:
        try:
            print(f"Scraping {code}: {url}")
            
            # Add headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract site information
            site_name = extract_site_name(response.text)
            tourist_value = extract_tourist_value(response.text)
            confidencialidad = extract_confidencialidad(response.text)
            
            # Get coordinates from API
            lat, lon = get_coordinates_from_api(code)
            
            if tourist_value:
                print(f"  ✓ Found VT: {tourist_value}")
                if confidencialidad:
                    print(f"  ✓ Found Confidencialidad: {confidencialidad}")
                if lat and lon:
                    print(f"  ✓ Found coordinates: {lat:.6f}, {lon:.6f}")
                results.append({
                    'code': code,
                    'denominacion': site_name if site_name else 'N/A',
                    'url': url,
                    'valor_turistico': tourist_value,
                    'confidencialidad': confidencialidad if confidencialidad else 'N/A',
                    'latitude': f"{lat:.6f}" if lat else 'N/A',
                    'longitude': f"{lon:.6f}" if lon else 'N/A',
                    'status': 'success'
                })
            else:
                print(f"  ✗ VT not found")
                results.append({
                    'code': code,
                    'denominacion': site_name if site_name else 'N/A',
                    'url': url,
                    'valor_turistico': 'N/A',
                    'confidencialidad': confidencialidad if confidencialidad else 'N/A',
                    'latitude': f"{lat:.6f}" if lat else 'N/A',
                    'longitude': f"{lon:.6f}" if lon else 'N/A',
                    'status': 'not_found'
                })
            
            # Be polite - add a small delay between requests
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error: {str(e)}")
            results.append({
                'code': code,
                'denominacion': 'N/A',
                'url': url,
                'valor_turistico': 'ERROR',
                'confidencialidad': 'N/A',
                'latitude': 'N/A',
                'longitude': 'N/A',
                'status': f'error: {str(e)}'
            })
            time.sleep(1)
    
    return results

def get_color_for_value(tourist_value):
    """Get KML color code based on tourist value
    Returns color in KML format (aabbggrr - alpha, blue, green, red)
    """
    try:
        value = float(tourist_value)
        if value > 5.0:
            return 'ff00ff00'  # Green (opaque)
        elif value >= 4.0:
            return 'ff00ffff'  # Yellow (opaque)
        else:
            return 'ff0000ff'  # Red (opaque)
    except (ValueError, TypeError):
        return 'ff808080'  # Gray for invalid/missing values

def save_to_csv(results, filename='igme_tourist_values.csv'):
    """Save results to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['code', 'denominacion', 'url', 'valor_turistico', 'confidencialidad', 'latitude', 'longitude', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"\n✓ Results saved to {filename}")

def save_to_kml(results, filename='igme_tourist_values.kml'):
    """Save results to KML file with color-coded markers"""
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>IGME Tourist Sites</name>
    <description>Geological sites from IGME IELIG database with tourist values</description>
    
    <!-- Style definitions -->
    <Style id="greenMarker">
      <IconStyle>
        <color>ff00ff00</color>
        <scale>1.2</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="yellowMarker">
      <IconStyle>
        <color>ff00ffff</color>
        <scale>1.2</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="redMarker">
      <IconStyle>
        <color>ff0000ff</color>
        <scale>1.2</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="grayMarker">
      <IconStyle>
        <color>ff808080</color>
        <scale>1.0</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/wht-circle.png</href>
        </Icon>
      </IconStyle>
    </Style>
'''
    
    kml_footer = '''  </Document>
</kml>'''
    
    with open(filename, 'w', encoding='utf-8') as kmlfile:
        kmlfile.write(kml_header)
        
        for result in results:
            # Skip sites without valid coordinates
            if result['latitude'] == 'N/A' or result['longitude'] == 'N/A':
                continue
            
            # Determine style based on tourist value
            try:
                value = float(result['valor_turistico'])
                if value > 5.0:
                    style = 'greenMarker'
                elif value >= 4.0:
                    style = 'yellowMarker'
                else:
                    style = 'redMarker'
            except (ValueError, TypeError):
                style = 'grayMarker'
            
            # Escape XML special characters
            name = result['denominacion'].replace('&', '&').replace('<', '<').replace('>', '>')
            code = result['code'].replace('&', '&').replace('<', '<').replace('>', '>')
            
            # Create description with HTML formatting
            description = f'''<![CDATA[
<b>Site:</b> {name}<br/>
<b>Code:</b> {code}<br/>
<b>Tourist Value:</b> {result['valor_turistico']}<br/>
<b>Confidencialidad:</b> {result['confidencialidad']}<br/>
<b>URL:</b> <a href="{result['url']}">{result['url']}</a>
]]>'''
            
            # Create placemark
            placemark = f'''
    <Placemark>
      <name>{name}</name>
      <description>{description}</description>
      <styleUrl>#{style}</styleUrl>
      <Point>
        <coordinates>{result['longitude']},{result['latitude']},0</coordinates>
      </Point>
    </Placemark>'''
            
            kmlfile.write(placemark)
        
        kmlfile.write(kml_footer)
    
    print(f"✓ KML file saved to {filename}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Scrape tourist value data from IGME IELIG database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all sites (IB200, IB200a-z, IB034, IB034a-z)
  python scrape_igme_sites.py
  
  # Scrape a specific site
  python scrape_igme_sites.py --code IB200a
  python scrape_igme_sites.py -c IB034
        """
    )
    parser.add_argument(
        '-c', '--code',
        type=str,
        help='Specific site code to scrape (e.g., IB200a, IB034, IB200z)',
        metavar='CODE'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("IGME Tourist Value Scraper")
    print("=" * 60)
    
    if args.code:
        print(f"Mode: Single site ({args.code.upper()})")
    else:
        print("Mode: All sites (54 sites)")
    print()
    
    # Scrape sites (all or specific)
    results = scrape_sites(args.code)
    
    # Save to CSV
    save_to_csv(results)
    
    # Save to KML
    save_to_kml(results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results if r['status'] == 'success')
    not_found = sum(1 for r in results if r['status'] == 'not_found')
    errors = sum(1 for r in results if r['status'].startswith('error'))
    sites_with_coords = sum(1 for r in results if r['latitude'] != 'N/A' and r['longitude'] != 'N/A')
    
    print(f"Total sites scraped: {len(results)}")
    print(f"Successfully extracted: {successful}")
    print(f"VT not found: {not_found}")
    print(f"Errors: {errors}")
    print(f"Sites with coordinates: {sites_with_coords}")
    
    if successful > 0:
        print(f"\n✓ Check 'igme_tourist_values.csv' for results")
        print(f"✓ Check 'igme_tourist_values.kml' for map visualization")

if __name__ == "__main__":
    main()

# Made with Bob
