#!/usr/bin/env python3
"""
Take a screenshot of the EclipseFan.org map for a specific location using Playwright.
Requires: pip install playwright
Then run: playwright install chromium
"""

import sys
import asyncio
from playwright.async_api import async_playwright

async def take_screenshot(url, output_file="eclipsefan_screenshot.png", wait_time=5000):
    """
    Take a screenshot of the given URL using Playwright.
    
    Args:
        url: The URL to screenshot
        output_file: Output filename for the screenshot
        wait_time: Time to wait for page to load (milliseconds)
    """
    print(f"Taking screenshot of: {url}")
    
    async with async_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        
        # Create a new page with specific viewport
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        try:
            # Navigate to the URL
            print("Loading page...")
            await page.goto(url, wait_until="networkidle")
            
            # Wait additional time for map to render
            print(f"Waiting {wait_time/1000} seconds for map to fully render...")
            await page.wait_for_timeout(wait_time)
            
            # Optional: Wait for map element
            try:
                await page.wait_for_selector("#map", timeout=10000)
                print("Map element detected")
            except:
                print("Map element not found, but continuing anyway...")
            
            # Take screenshot
            print(f"Taking screenshot and saving to: {output_file}")
            await page.screenshot(path=output_file, full_page=False)
            
            print(f"✓ Screenshot saved successfully!")
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            sys.exit(1)
            
        finally:
            await browser.close()

def main():
    # Default URL for Spain eclipse location
    default_url = "https://www.eclipsefan.org/?lat=42.083378&lng=-2.085237&zoom=6&oz=5&lang=en"
    
    # Allow custom URL from command line
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    output_file = sys.argv[2] if len(sys.argv) > 2 else "eclipsefan_screenshot.png"
    
    # Run async function
    try:
        asyncio.run(take_screenshot(url, output_file))
    except ImportError:
        print("\nError: Playwright not installed.")
        print("\nPlease install it with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob
