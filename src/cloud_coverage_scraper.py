"""
Cloud Coverage Scraper for Eclipse Sites

Scrapes historical cloud coverage data from timeanddate.com for the eclipse date.
This helps determine which sites have the best chance of clear skies.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Any, Optional


def get_cloud_coverage(latitude: float, longitude: float, date_iso: str = "20260812") -> Dict[str, Any]:
    """
    Get historical cloud coverage percentage for a location on the eclipse date.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        date_iso: Date in ISO format (YYYYMMDD), default is eclipse date
        
    Returns:
        dict with:
            - cloud_percentage: int (0-100) or None if not found
            - status: str ('success', 'not_found', 'error')
            - message: str with details
            - url: str with the source URL
    """
    
    # Build URL for timeanddate.com eclipse page
    url = f"https://www.timeanddate.com/eclipse/in/@{latitude},{longitude}?iso={date_iso}"
    
    try:
        # Add headers to identify as a legitimate browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for cloud coverage section
        # Pattern: "In the past, this day was cloudy X% of the time"
        cloud_text = soup.find(string=re.compile(r'this day was cloudy \d+% of the time', re.IGNORECASE))
        
        if cloud_text:
            # Convert to string and extract percentage using regex
            text_str = str(cloud_text)
            match = re.search(r'cloudy (\d+)% of the time', text_str, re.IGNORECASE)
            if match:
                percentage = int(match.group(1))
                return {
                    'cloud_percentage': percentage,
                    'status': 'success',
                    'message': f'Cloud coverage: {percentage}%',
                    'url': url
                }
        
        # If not found, return not_found status
        return {
            'cloud_percentage': None,
            'status': 'not_found',
            'message': 'Cloud coverage data not found on page',
            'url': url
        }
        
    except requests.Timeout:
        return {
            'cloud_percentage': None,
            'status': 'timeout',
            'message': 'Request timed out after 30 seconds',
            'url': url
        }
    except requests.RequestException as e:
        return {
            'cloud_percentage': None,
            'status': 'error',
            'message': f'Request error: {str(e)}',
            'url': url
        }
    except Exception as e:
        return {
            'cloud_percentage': None,
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'url': url
        }


def scrape_cloud_coverage_for_sites(sites: List[Dict[str, Any]], delay: float = 2.0) -> List[Dict[str, Any]]:
    """
    Scrape cloud coverage for multiple sites with rate limiting.
    
    Args:
        sites: List of site dictionaries with 'latitude' and 'longitude' keys
        delay: Delay in seconds between requests (default 2.0)
        
    Returns:
        List of sites with added 'cloud_coverage' and 'cloud_status' fields
    """
    
    results: List[Dict[str, Any]] = []
    total = len(sites)
    
    for i, site in enumerate(sites, 1):
        print(f"[{i}/{total}] Checking cloud coverage for {site.get('code', 'unknown')}...")
        
        # Skip if no coordinates
        if not site.get('latitude') or not site.get('longitude'):
            site['cloud_coverage'] = None
            site['cloud_status'] = 'no_coordinates'
            results.append(site)
            continue
        
        # Get cloud coverage
        result = get_cloud_coverage(site['latitude'], site['longitude'])
        
        # Add to site data
        site['cloud_coverage'] = result['cloud_percentage']
        site['cloud_status'] = result['status']
        site['cloud_url'] = result.get('url', '')
        
        print(f"  → {result['message']}")
        
        results.append(site)
        
        # Rate limiting - be respectful to the server
        if i < total:
            time.sleep(delay)
    
    return results


if __name__ == '__main__':
    # Test with a sample location (Madrid area)
    print("Testing cloud coverage scraper...")
    print("-" * 50)
    
    result = get_cloud_coverage(40.4165, -3.7026)
    
    print(f"Status: {result['status']}")
    print(f"Cloud Coverage: {result['cloud_percentage']}%")
    print(f"Message: {result['message']}")
    print(f"URL: {result['url']}")

# Made with Bob
