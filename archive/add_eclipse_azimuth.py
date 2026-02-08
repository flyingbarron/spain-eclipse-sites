#!/usr/bin/env python3
"""
Add Eclipse Azimuth Lines to KML
Adds directional lines pointing toward the eclipse azimuth (283.7753°) for each site
"""

import xml.etree.ElementTree as ET
import math
import argparse


def calculate_endpoint(lat, lon, azimuth, distance_km=50):
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


def add_azimuth_lines(input_kml, output_kml, azimuth=283.7753, distance_km=50):
    """Add azimuth lines to all placemarks in a KML file, preserving folder structure
    
    Args:
        input_kml: Path to input KML file
        output_kml: Path to output KML file
        azimuth: Eclipse azimuth in degrees
        distance_km: Length of azimuth line in kilometers
    """
    # Parse the KML file
    tree = ET.parse(input_kml)
    root = tree.getroot()
    
    # Define KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    # Register namespace to avoid ns0 prefix
    ET.register_namespace('', 'http://www.opengis.net/kml/2.2')
    
    # Find the Document element
    document = root.find('.//kml:Document', ns)
    if document is None:
        print("Error: No Document element found in KML")
        return
    
    # Add azimuth line style if it doesn't exist
    style_exists = document.find(".//kml:Style[@id='azimuthLine']", ns) is not None
    if not style_exists:
        # Insert style after existing styles
        styles = document.findall('kml:Style', ns)
        insert_pos = len(styles)
        
        style = ET.Element('Style', {'id': 'azimuthLine'})
        line_style = ET.SubElement(style, 'LineStyle')
        color = ET.SubElement(line_style, 'color')
        color.text = 'ff00ffff'  # Yellow line (AABBGGRR format)
        width = ET.SubElement(line_style, 'width')
        width.text = '3'
        
        document.insert(insert_pos, style)
    
    # Process each folder separately to maintain structure
    folders = document.findall('kml:Folder', ns)
    lines_added = 0
    
    for folder in folders:
        # Find all Placemarks with Point coordinates in this folder
        placemarks = folder.findall('kml:Placemark', ns)
        
        # Collect line placemarks to add (we'll add them all at once at the end)
        line_placemarks = []
        
        for placemark in placemarks:
            # Get the point coordinates
            point = placemark.find('.//kml:Point', ns)
            if point is None:
                continue
            
            coordinates_elem = point.find('kml:coordinates', ns)
            if coordinates_elem is None or not coordinates_elem.text:
                continue
            
            # Parse coordinates (format: lon,lat,alt)
            coords = coordinates_elem.text.strip().split(',')
            if len(coords) < 2:
                continue
            
            try:
                lon = float(coords[0])
                lat = float(coords[1])
            except ValueError:
                continue
            
            # Calculate endpoint
            end_lat, end_lon = calculate_endpoint(lat, lon, azimuth, distance_km)
            
            # Get placemark name for the line
            name_elem = placemark.find('kml:name', ns)
            site_name = name_elem.text if name_elem is not None else "Unknown"
            
            # Create a new Placemark for the azimuth line
            line_placemark = ET.Element('Placemark')
            
            # Add name
            line_name = ET.SubElement(line_placemark, 'name')
            line_name.text = f"{site_name} - Eclipse Azimuth"
            
            # Add description
            line_desc = ET.SubElement(line_placemark, 'description')
            line_desc.text = f"Eclipse azimuth: {azimuth}° (pointing toward eclipse direction)"
            
            # Add style reference
            style_url = ET.SubElement(line_placemark, 'styleUrl')
            style_url.text = '#azimuthLine'
            
            # Add LineString
            line_string = ET.SubElement(line_placemark, 'LineString')
            line_coords = ET.SubElement(line_string, 'coordinates')
            line_coords.text = f"{lon},{lat},0 {end_lon},{end_lat},0"
            
            line_placemarks.append(line_placemark)
            lines_added += 1
        
        # Add all line placemarks to the end of this folder
        for line_placemark in line_placemarks:
            folder.append(line_placemark)
    
    # Write the modified KML
    tree.write(output_kml, encoding='utf-8', xml_declaration=True)
    
    print(f"✓ Added {lines_added} azimuth lines to {output_kml}")
    print(f"  Eclipse azimuth: {azimuth}°")
    print(f"  Line length: {distance_km} km")
    print(f"  Lines organized within existing folder structure")


def main():
    parser = argparse.ArgumentParser(
        description='Add eclipse azimuth lines to KML file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add azimuth lines to sites.kml
  python3 add_eclipse_azimuth.py data/sites.kml data/sites_with_azimuth.kml
  
  # Custom azimuth and distance
  python3 add_eclipse_azimuth.py data/sites.kml output.kml --azimuth 283.7753 --distance 100
        """
    )
    parser.add_argument('input_kml', help='Input KML file path')
    parser.add_argument('output_kml', help='Output KML file path')
    parser.add_argument('--azimuth', '-a', type=float, default=283.7753,
                       help='Eclipse azimuth in degrees (default: 283.7753)')
    parser.add_argument('--distance', '-d', type=float, default=50,
                       help='Length of azimuth line in kilometers (default: 50)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Eclipse Azimuth Line Generator")
    print("=" * 60)
    print()
    
    add_azimuth_lines(args.input_kml, args.output_kml, args.azimuth, args.distance)
    
    print("\n✓ Done!")


if __name__ == "__main__":
    main()

# Made with Bob