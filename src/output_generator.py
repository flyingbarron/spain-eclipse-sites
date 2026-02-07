"""
Output Generator Module
Functions for generating CSV and KML output files
"""

import csv
import os

# Ensure data directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def save_to_csv(results, filename='eclipse_site_data.csv'):
    """Save results to CSV file
    
    Args:
        results: List of site dictionaries
        filename: Output CSV filename
    """
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['code', 'denominacion', 'url', 'valor_turistico', 'confidencialidad',
                     'route_difficulty', 'latitude', 'longitude', 'eclipse_visibility', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"✓ CSV saved to {filepath}")


def get_tourist_value_category(tourist_value):
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


def save_to_kml(results, filename='sites.kml'):
    """Save results to KML file with six folders organized by tourist value and eclipse visibility
    
    Args:
        results: List of site dictionaries
        filename: Output KML filename
    """
    filepath = os.path.join(DATA_DIR, filename)
    
    # Organize sites into categories
    categories = {
        ('High', 'visible'): [],
        ('High', 'not_visible'): [],
        ('Medium', 'visible'): [],
        ('Medium', 'not_visible'): [],
        ('Lower', 'visible'): [],
        ('Lower', 'not_visible'): [],
    }
    
    for result in results:
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
'''
    
    kml_footer = '''  </Document>
</kml>'''
    
    with open(filepath, 'w', encoding='utf-8') as kmlfile:
        kmlfile.write(kml_header)
        
        # Define folder order and names with emojis
        folder_order = [
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
                
                placemark = f'''
      <Placemark>
        <name>{name}</name>
        <description><![CDATA[
          <b>Code:</b> {code}<br/>
          <b>Tourist Value:</b> {result['valor_turistico']}<br/>
          <b>Privacy:</b> {result['confidencialidad']}<br/>
          <b>Route Difficulty:</b> {result.get('route_difficulty', 'N/A')}<br/>
          <b>Eclipse 2026:</b> {eclipse_text}<br/>
          <b>URL:</b> <a href="{url}">{url}</a>
        ]]></description>
        <styleUrl>#{style}</styleUrl>
        <Point>
          <coordinates>{result['longitude']},{result['latitude']},0</coordinates>
        </Point>
      </Placemark>
'''
                kmlfile.write(placemark)
            
            kmlfile.write('    </Folder>\n')
        
        kmlfile.write(kml_footer)
    
    print(f"✓ KML saved to {filepath}")
    print(f"  Total sites: {total_sites} organized in 6 folders")
    
    # Print breakdown
    for key, folder_name in folder_order:
        count = len(categories[key])
        if count > 0:
            print(f"  • {folder_name}: {count} sites")


def print_summary(results):
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
    
    print(f"Total sites collected: {total}")
    print(f"Sites with coordinates: {with_coords}")
    print(f"Eclipse visible: {eclipse_visible}")
    print(f"Eclipse not visible: {eclipse_not_visible}")
    print("\nOutput files:")
    print("  • data/eclipse_site_data.csv - Complete dataset")
    print("  • data/sites.kml - All sites organized in 6 folders")
    print("  • data/eclipse_profiles/*.png - Visibility profile diagrams")

# Made with Bob
