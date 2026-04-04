#!/usr/bin/env python3
"""
Download Google Maps Static API thumbnails for all sites
Run this locally with your API key in .env file, then commit the images

Usage:
    python3 utilities/download_google_maps_thumbnails.py
"""
import os
import csv
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not GOOGLE_MAPS_API_KEY:
    print("ERROR: GOOGLE_MAPS_API_KEY not found in .env file")
    print("Please create a .env file with:")
    print("GOOGLE_MAPS_API_KEY=your_api_key_here")
    exit(1)

print(f"Using API key: {GOOGLE_MAPS_API_KEY[:10]}...{GOOGLE_MAPS_API_KEY[-4:]}")
print()

# Output directory
OUTPUT_DIR = Path("data/google_maps_thumbnails")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Read sites from CSV
csv_path = Path("data/eclipse_site_data.csv")
if not csv_path.exists():
    print(f"ERROR: {csv_path} not found")
    exit(1)

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    sites = list(reader)

print(f"Found {len(sites)} sites")
print(f"Output directory: {OUTPUT_DIR}")
print()

downloaded = 0
skipped = 0
failed = 0

for site in sites:
    code = site["code"]
    lat = site["latitude"]
    lon = site["longitude"]
    
    # Build Google Maps Static API URL
    url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={lat},{lon}&zoom=15&size=400x200&maptype=satellite"
        f"&markers=color:red%7C{lat},{lon}&key={GOOGLE_MAPS_API_KEY}"
    )
    
    output_file = OUTPUT_DIR / f"{code}_map.jpg"
    
    if output_file.exists():
        print(f"✓ {code} already exists (skipped)")
        skipped += 1
        continue
    
    try:
        print(f"⬇ Downloading {code}...", end=" ")
        
        # Create request with User-Agent header
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            with open(output_file, 'wb') as out_file:
                out_file.write(response.read())
        
        print("✓ saved")
        downloaded += 1
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP {e.code}: {e.reason}")
        if e.code == 403:
            print(f"   Check API key restrictions in Google Cloud Console")
            print(f"   URL: {url[:100]}...")
        failed += 1
    except Exception as e:
        print(f"✗ failed: {e}")
        failed += 1

print()
print("=" * 50)
print(f"Summary:")
print(f"  Downloaded: {downloaded}")
print(f"  Skipped:    {skipped}")
print(f"  Failed:     {failed}")
print(f"  Total:      {len(sites)}")
print()
print(f"Images saved to: {OUTPUT_DIR}")
print()
print("Next steps:")
print("  1. Review the downloaded images")
print("  2. git add data/google_maps_thumbnails/")
print("  3. git commit -m 'Add Google Maps thumbnails'")
print("  4. git push")

# Made with Bob
