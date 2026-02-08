#!/usr/bin/env python3
"""
Download the horizon image from EclipseFan.org for a specific location.
This script clicks the Horizon tab and downloads the generated image.
Requires: pip install playwright
Then run: playwright install chromium
"""

import sys
import asyncio
import os
from playwright.async_api import async_playwright
import urllib.request

async def download_horizon_image(url, output_file="horizon_image.png", headless=False):
    """
    Navigate to EclipseFan, click Horizon tab, and download the image.
    
    Args:
        url: The EclipseFan URL with location parameters
        output_file: Output filename for the horizon image
        headless: Whether to run in headless mode
    """
    print(f"Loading EclipseFan page: {url}")
    
    async with async_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = await p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create context with realistic user agent
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Remove webdriver property
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        try:
            # Navigate to the URL
            print("Loading page...")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait for page to initialize
            print("Waiting for page to initialize...")
            await page.wait_for_timeout(3000)
            
            # Look for and click the Horizon tab
            print("Looking for Horizon tab...")
            
            # Try different selectors for the Horizon tab
            horizon_selectors = [
                'text=Horizon',
                'button:has-text("Horizon")',
                'a:has-text("Horizon")',
                '[data-tab="horizon"]',
                '.tab:has-text("Horizon")',
                'div:has-text("Horizon")'
            ]
            
            horizon_clicked = False
            for selector in horizon_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        print(f"Found Horizon tab with selector: {selector}")
                        await element.click()
                        horizon_clicked = True
                        break
                except:
                    continue
            
            if not horizon_clicked:
                print("Could not find Horizon tab. Available text on page:")
                page_text = await page.inner_text('body')
                print(page_text[:500])
                raise Exception("Horizon tab not found")
            
            print("Clicked Horizon tab, waiting for image to load...")
            await page.wait_for_timeout(5000)  # Wait for horizon image to generate
            
            # Look for the horizon image
            print("Looking for horizon image...")
            
            # Try to find image element
            image_selectors = [
                'img[src*="horizon"]',
                'img[alt*="horizon"]',
                'img[alt*="Horizon"]',
                '.horizon-image img',
                '#horizon img',
                'canvas',  # Might be rendered on canvas
            ]
            
            image_url = None
            for selector in image_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        # Check if it's an img tag
                        tag_name = await element.evaluate('el => el.tagName')
                        if tag_name.lower() == 'img':
                            image_url = await element.get_attribute('src')
                            print(f"Found image with selector: {selector}")
                            print(f"Image URL: {image_url}")
                            break
                        elif tag_name.lower() == 'canvas':
                            # If it's a canvas, we need to take a screenshot of it
                            print("Horizon is rendered on canvas, taking screenshot...")
                            await element.screenshot(path=output_file)
                            print(f"✓ Canvas screenshot saved to: {output_file}")
                            return
                except:
                    continue
            
            if not image_url:
                # Try to find any images loaded after clicking
                print("Searching for any images in the page...")
                all_images = await page.query_selector_all('img')
                print(f"Found {len(all_images)} images on page")
                
                for img in all_images:
                    src = await img.get_attribute('src')
                    alt = await img.get_attribute('alt') or ''
                    print(f"  - {src} (alt: {alt})")
                
                raise Exception("Could not find horizon image")
            
            # Download the image
            print(f"Downloading image from: {image_url}")
            
            # If it's a data URL, save it directly
            if image_url.startswith('data:'):
                print("Image is a data URL, extracting...")
                # Use page.evaluate to get the image data
                image_data = await page.evaluate(f'''
                    async () => {{
                        const response = await fetch("{image_url}");
                        const blob = await response.blob();
                        const reader = new FileReader();
                        return new Promise((resolve) => {{
                            reader.onloadend = () => resolve(reader.result);
                            reader.readAsDataURL(blob);
                        }});
                    }}
                ''')
                # Save the data URL content
                import base64
                header, encoded = image_data.split(',', 1)
                data = base64.b64decode(encoded)
                with open(output_file, 'wb') as f:
                    f.write(data)
            else:
                # Make URL absolute if needed
                if image_url.startswith('/'):
                    image_url = 'https://www.eclipsefan.org' + image_url
                elif not image_url.startswith('http'):
                    image_url = 'https://www.eclipsefan.org/' + image_url
                
                # Download using the browser context to maintain session
                response = await page.request.get(image_url)
                image_data = await response.body()
                
                with open(output_file, 'wb') as f:
                    f.write(image_data)
            
            print(f"✓ Horizon image saved to: {output_file}")
            
            if not headless:
                print("\nBrowser window will close in 3 seconds...")
                await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            
            # Take a screenshot for debugging
            debug_file = "debug_screenshot.png"
            await page.screenshot(path=debug_file)
            print(f"\nDebug screenshot saved to: {debug_file}")
            sys.exit(1)
            
        finally:
            await context.close()
            await browser.close()

def main():
    # Default URL for Spain eclipse location
    default_url = "https://www.eclipsefan.org/?lat=42.083378&lng=-2.085237&zoom=6&oz=5&lang=en"
    
    # Allow custom URL from command line
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    output_file = sys.argv[2] if len(sys.argv) > 2 else "horizon_image.png"
    
    # Run async function
    try:
        asyncio.run(download_horizon_image(url, output_file))
    except ImportError:
        print("\nError: Playwright not installed.")
        print("\nPlease install it with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob
