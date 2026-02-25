"""
Output Generator Module
Functions for generating CSV and KML output files
"""

import csv
import os
import math
import shutil
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Ensure data directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Eclipse azimuth constant (degrees)
ECLIPSE_AZIMUTH = 283.7753
AZIMUTH_LINE_DISTANCE_KM = 50


def calculate_endpoint(lat: float, lon: float, azimuth: float, distance_km: float = 50) -> Tuple[float, float]:
    """Calculate endpoint coordinates given start point, azimuth, and distance
    
    Args:
        lat: Starting latitude in decimal degrees
        lon: Starting longitude in decimal degrees
        azimuth: Bearing in degrees (0=North, 90=East, 180=South, 270=West)
        distance_km: Distance in kilometers
    
    Returns:
        Tuple of (end_lat, end_lon)
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    azimuth_rad = math.radians(azimuth)
    
    # Angular distance
    angular_distance = distance_km / R
    
    # Calculate end point
    end_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(angular_distance) +
        math.cos(lat_rad) * math.sin(angular_distance) * math.cos(azimuth_rad)
    )
    
    end_lon_rad = lon_rad + math.atan2(
        math.sin(azimuth_rad) * math.sin(angular_distance) * math.cos(lat_rad),
        math.cos(angular_distance) - math.sin(lat_rad) * math.sin(end_lat_rad)
    )
    
    # Convert back to degrees
    end_lat = math.degrees(end_lat_rad)
    end_lon = math.degrees(end_lon_rad)
    
    return end_lat, end_lon


def save_to_csv(results: List[Dict[str, Any]], filename: str = 'eclipse_site_data.csv') -> None:
    """Save results to CSV file, merging with existing data
    
    Args:
        results: List of site dictionaries (new/updated data)
        filename: Output CSV filename
    """
    filepath = os.path.join(DATA_DIR, filename)
    fieldnames = ['code', 'denominacion', 'url', 'valor_turistico', 'confidencialidad',
                 'route_difficulty', 'latitude', 'longitude', 'eclipse_visibility', 'status',
                 'cloud_coverage', 'cloud_status', 'cloud_url', 'bortle_scale', 'bortle_status',
                 'horizon_status', 'shademap_status', 'darksky_sqm', 'darksky_bortle',
                 'darksky_darkness', 'darksky_status']
    
    # Backup existing CSV file if it exists
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filepath = filepath.replace('.csv', f'_backup_{timestamp}.csv')
        try:
            shutil.copy2(filepath, backup_filepath)
            print(f"  ✓ Backed up existing CSV to {backup_filepath}")
        except Exception as e:
            print(f"  Warning: Could not create backup: {e}")
    
    # Load existing data if file exists
    existing_data: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    existing_data[row['code']] = row
            print(f"  Loaded {len(existing_data)} existing entries from CSV")
        except Exception as e:
            print(f"  Warning: Could not load existing CSV: {e}")
    
    # Merge new results with existing data (new data takes precedence)
    for result in results:
        existing_data[result['code']] = result
    
    # Write merged data
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort by code for consistent output
        for code in sorted(existing_data.keys()):
            writer.writerow(existing_data[code])
    
    print(f"✓ CSV saved to {filepath} ({len(existing_data)} total entries, {len(results)} updated)")


def get_tourist_value_category(tourist_value: Any) -> Tuple[str, str]:
    """Determine tourist value category
    
    Args:
        tourist_value: Tourist value as string or number
    
    Returns:
        Tuple of (category_name, style_id)
    """
    try:
        value = float(tourist_value)
        if value > 5.0:
            return ('High', 'greenMarker')
        elif value >= 4.0:
            return ('Medium', 'yellowMarker')
        else:
            return ('Lower', 'redMarker')
    except (ValueError, TypeError):
        return ('Unknown', 'redMarker')


def save_to_kml(results: List[Dict[str, Any]], filename: str = 'sites.kml') -> None:
    """Save results to KML file, merging with existing data
    
    Args:
        results: List of site dictionaries (new/updated data)
        filename: Output KML filename
    """
    filepath = os.path.join(DATA_DIR, filename)
    
    # Load existing data from CSV (which has all merged data)
    csv_filepath = os.path.join(DATA_DIR, 'eclipse_site_data.csv')
    all_sites: List[Dict[str, Any]] = []
    
    if os.path.exists(csv_filepath):
        try:
            with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                all_sites = list(reader)
            print(f"  Loaded {len(all_sites)} entries from CSV for KML generation")
        except Exception as e:
            print(f"  Warning: Could not load CSV for KML: {e}")
            all_sites = results
    else:
        all_sites = results
    
    # Organize sites into categories
    categories: Dict[Tuple[str, str], List[Tuple[Dict[str, Any], str]]] = {
        ('High', 'visible'): [],
        ('High', 'not_visible'): [],
        ('Medium', 'visible'): [],
        ('Medium', 'not_visible'): [],
        ('Lower', 'visible'): [],
        ('Lower', 'not_visible'): [],
    }
    
    for result in all_sites:
        if result['latitude'] == 'N/A' or result['longitude'] == 'N/A':
            continue
        
        category, style = get_tourist_value_category(result['valor_turistico'])
        eclipse_status = result.get('eclipse_visibility', 'unknown')
        
        # Only categorize sites with known eclipse visibility
        if eclipse_status in ['visible', 'not_visible']:
            key = (category, eclipse_status)
            if key in categories:
                categories[key].append((result, style))
    
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Spain Eclipse Sites - Organized by Tourist Value and Eclipse Visibility</name>
    <description>Geological sites from IGME IELIG database organized into six categories</description>
    
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
    <Style id="azimuthLine">
      <LineStyle>
        <color>ff00ffff</color>
        <width>3</width>
      </LineStyle>
    </Style>
'''
    
    kml_footer = '''  </Document>
</kml>'''
    
    with open(filepath, 'w', encoding='utf-8') as kmlfile:
        kmlfile.write(kml_header)
        
        # Define folder order and names with emojis
        folder_order: List[Tuple[Tuple[str, str], str]] = [
            (('High', 'visible'), '🟢 High Tourist Value (>5.0) - Eclipse Visible'),
            (('High', 'not_visible'), '🟢 High Tourist Value (>5.0) - Eclipse Not Visible'),
            (('Medium', 'visible'), '🟡 Medium Tourist Value (4.0-5.0) - Eclipse Visible'),
            (('Medium', 'not_visible'), '🟡 Medium Tourist Value (4.0-5.0) - Eclipse Not Visible'),
            (('Lower', 'visible'), '🔴 Lower Tourist Value (<4.0) - Eclipse Visible'),
            (('Lower', 'not_visible'), '🔴 Lower Tourist Value (<4.0) - Eclipse Not Visible'),
        ]
        
        total_sites = 0
        
        # Create folders - always create all six folders even if empty
        for key, folder_name in folder_order:
            sites = categories[key]
            total_sites += len(sites)
            
            kmlfile.write(f'''
    <Folder>
      <name>{folder_name}</name>
      <description>{len(sites)} sites</description>
      <open>0</open>
''')
            
            for result, style in sites:
                # Escape XML special characters
                name = result['denominacion'].replace('&', '&').replace('<', '<').replace('>', '>')
                code = result['code'].replace('&', '&').replace('<', '<').replace('>', '>')
                url = result['url'].replace('&', '&')
                
                eclipse_status = result.get('eclipse_visibility', 'unknown')
                eclipse_text = {
                    'visible': '🌑 Eclipse VISIBLE',
                    'not_visible': '🌑 Eclipse not visible',
                }.get(eclipse_status, eclipse_status)
                
                # Add cloud coverage info if available
                cloud_info = ''
                if result.get('cloud_coverage') is not None and result.get('cloud_coverage') != '':
                    try:
                        cloud_pct = int(result['cloud_coverage'])
                        cloud_emoji = '☀️' if cloud_pct < 30 else '⛅' if cloud_pct < 60 else '☁️'
                        cloud_info = f'<b>Cloud Coverage:</b> {cloud_emoji} {cloud_pct}%<br/>'
                        if result.get('cloud_url'):
                            cloud_info += f'<b>Cloud Data:</b> <a href="{result["cloud_url"]}">View Details</a><br/>'
                    except (ValueError, TypeError):
                        # Skip cloud info if conversion fails
                        pass
                
                placemark = f'''
      <Placemark>
        <name>{name}</name>
        <description><![CDATA[
          <b>Code:</b> {code}<br/>
          <b>Tourist Value:</b> {result['valor_turistico']}<br/>
          <b>Privacy:</b> {result['confidencialidad']}<br/>
          <b>Route Difficulty:</b> {result.get('route_difficulty', 'N/A')}<br/>
          <b>Eclipse 2026:</b> {eclipse_text}<br/>
          {cloud_info}<b>URL:</b> <a href="{url}">{url}</a>
        ]]></description>
        <styleUrl>#{style}</styleUrl>
        <Point>
          <coordinates>{result['longitude']},{result['latitude']},0</coordinates>
        </Point>
      </Placemark>
'''
                kmlfile.write(placemark)
                
                # Add azimuth line for this site
                try:
                    lat = float(result['latitude'])
                    lon = float(result['longitude'])
                    end_lat, end_lon = calculate_endpoint(lat, lon, ECLIPSE_AZIMUTH, AZIMUTH_LINE_DISTANCE_KM)
                    
                    azimuth_placemark = f'''
      <Placemark>
        <name>{name} - Eclipse Azimuth</name>
        <description><![CDATA[
          Eclipse azimuth: {ECLIPSE_AZIMUTH}° (pointing toward eclipse direction)
        ]]></description>
        <styleUrl>#azimuthLine</styleUrl>
        <LineString>
          <coordinates>{lon},{lat},0 {end_lon},{end_lat},0</coordinates>
        </LineString>
      </Placemark>
'''
                    kmlfile.write(azimuth_placemark)
                except (ValueError, TypeError):
                    # Skip azimuth line if coordinates are invalid
                    pass
            
            kmlfile.write('    </Folder>\n')
        
        kmlfile.write(kml_footer)
    
    print(f"✓ KML saved to {filepath}")
    print(f"  Total sites: {total_sites} organized in 6 folders")
    
    # Print breakdown
    for key, folder_name in folder_order:
        count = len(categories[key])
        if count > 0:
            print(f"  • {folder_name}: {count} sites")


def print_summary(results: List[Dict[str, Any]]) -> None:
    """Print summary statistics
    
    Args:
        results: List of site dictionaries
    """
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total = len(results)
    with_coords = sum(1 for r in results if r['latitude'] != 'N/A')
    eclipse_visible = sum(1 for r in results if r.get('eclipse_visibility') == 'visible')
    eclipse_not_visible = sum(1 for r in results if r.get('eclipse_visibility') == 'not_visible')
    
    # Cloud coverage statistics
    def get_cloud_value(r):
        """Safely convert cloud_coverage to int"""
        try:
            return int(r['cloud_coverage'])
        except (ValueError, TypeError, KeyError):
            return None
    
    cloud_values = [(r, get_cloud_value(r)) for r in results]
    with_cloud_data = sum(1 for r, val in cloud_values if val is not None)
    low_cloud = sum(1 for r, val in cloud_values if val is not None and val < 30)
    medium_cloud = sum(1 for r, val in cloud_values if val is not None and 30 <= val < 60)
    high_cloud = sum(1 for r, val in cloud_values if val is not None and val >= 60)
    
    print(f"Total sites collected: {total}")
    print(f"Sites with coordinates: {with_coords}")
    print(f"Eclipse visible: {eclipse_visible}")
    print(f"Eclipse not visible: {eclipse_not_visible}")
    
    if with_cloud_data > 0:
        print(f"\nCloud coverage data:")
        print(f"  Sites with cloud data: {with_cloud_data}")
        print(f"  ☀️  Low cloud (<30%): {low_cloud}")
        print(f"  ⛅ Medium cloud (30-60%): {medium_cloud}")
        print(f"  ☁️  High cloud (≥60%): {high_cloud}")
    
    # Horizon image statistics
    with_horizon = sum(1 for r in results if r.get('horizon_status') == 'success')
    
    # Shademap statistics
    with_shademap = sum(1 for r in results if r.get('shademap_status') == 'success')
    
    print("\nOutput files:")
    print("  • data/eclipse_site_data.csv - Complete dataset")
    print("  • data/sites.kml - All sites organized in 6 folders")
    print("  • data/scrape/ign_profiles/*.png - IGN visibility profile diagrams")
    if with_horizon > 0:
        print(f"  • data/scrape/eclipsefan_horizons/*.png - EclipseFan horizon profiles ({with_horizon} sites)")
    if with_shademap > 0:
        print(f"  • data/scrape/shademap_snapshots/*.jpg - Shademap shadow visualizations ({with_shademap} sites)")

# Made with Bob
