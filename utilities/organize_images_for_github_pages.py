#!/usr/bin/env python3
"""
Organize IGME cached images by site code for GitHub Pages deployment.

This script reads the cached images and HTML metadata, then copies images
into site-specific directories so they can be accessed directly on GitHub Pages.
"""

import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

# Paths
DATA_DIR = Path('data')
CSV_PATH = DATA_DIR / 'eclipse_site_data.csv'
CACHE_DIR = DATA_DIR / 'cache'
HTML_CACHE_DIR = CACHE_DIR / 'igme_html'
IMAGE_CACHE_DIR = CACHE_DIR / 'igme_images'
OUTPUT_DIR = IMAGE_CACHE_DIR  # Organize in same directory


def url_hash(value: str) -> str:
    """Return a stable cache key for a URL."""
    return hashlib.md5(value.encode()).hexdigest()


def load_sites_from_csv():
    """Load site data from CSV."""
    sites = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('url'):
                sites.append({
                    'code': row['code'],
                    'url': row['url']
                })
    return sites


def get_images_for_site(site_url: str):
    """Get image metadata for a site from cached HTML."""
    url_hash_str = url_hash(site_url)
    json_cache_file = HTML_CACHE_DIR / f'{url_hash_str}.json'
    
    if not json_cache_file.exists():
        return []
    
    try:
        with open(json_cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('images', [])
    except Exception as e:
        print(f"Error reading {json_cache_file}: {e}")
        return []


def find_cached_image(image_url: str):
    """Find the cached image file for a given URL."""
    url_hash_str = url_hash(image_url)
    
    # Try common extensions
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        cache_file = IMAGE_CACHE_DIR / f'{url_hash_str}{ext}'
        if cache_file.exists():
            return cache_file
    
    return None


def organize_images():
    """Organize cached images into site-specific directories."""
    print("Loading sites from CSV...")
    sites = load_sites_from_csv()
    print(f"Found {len(sites)} sites")
    
    total_images = 0
    sites_with_images = 0
    
    for site in sites:
        site_code = site['code']
        site_url = site['url']
        
        # Get images for this site
        images = get_images_for_site(site_url)
        
        if not images:
            continue
        
        # Create site directory
        site_dir = OUTPUT_DIR / site_code
        site_dir.mkdir(exist_ok=True)
        
        # Copy images
        copied = 0
        image_extensions = []
        for idx, img in enumerate(images, 1):
            img_url = img.get('src', '')
            if not img_url:
                continue
            
            # Find cached image
            cached_file = find_cached_image(img_url)
            if not cached_file:
                print(f"  Warning: Image not found in cache: {img_url}")
                continue
            
            # Copy to site directory
            ext = cached_file.suffix
            dest_file = site_dir / f'image_{idx}{ext}'
            
            if not dest_file.exists():
                shutil.copy2(cached_file, dest_file)
                copied += 1
                image_extensions.append(ext)
        
        if copied > 0:
            print(f"✓ {site_code}: Organized {copied} images")
            total_images += copied
            sites_with_images += 1
        
        # Create images.json manifest
        if copied > 0 and image_extensions:
            manifest = {
                'images': [f'image_{i}{image_extensions[i-1]}'
                          for i in range(1, copied + 1)]
            }
            manifest_file = site_dir / 'images.json'
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
    
    print(f"\n✓ Complete!")
    print(f"  Sites with images: {sites_with_images}")
    print(f"  Total images organized: {total_images}")
    print(f"  Output directory: {OUTPUT_DIR}")


if __name__ == '__main__':
    organize_images()

# Made with Bob
