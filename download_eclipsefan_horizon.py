#!/usr/bin/env python3
"""
Download the horizon image from EclipseFan.org for a specific location.
This script clicks the Horizon tab and downloads the generated image.
Requires: pip install selenium
Also requires: Chrome/Chromium browser and chromedriver
"""

import sys
import time
import os
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download_horizon_image(url, output_file="horizon_image.png", headless=False):
    """
    Navigate to EclipseFan, click Horizon tab, and download the image.
    
    Args:
        url: The EclipseFan URL with location parameters
        output_file: Output filename for the horizon image
        headless: Whether to run in headless mode
    """
    print(f"Loading EclipseFan page: {url}")
    
    # Set up Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Initialize the driver
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Remove webdriver property to avoid detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })
        
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("\nPlease ensure you have:")
        print("1. Chrome or Chromium browser installed")
        print("2. chromedriver installed (brew install chromedriver on macOS)")
        print("3. selenium installed (pip install selenium)")
        sys.exit(1)
    
    try:
        # Load the page
        print("Loading page...")
        driver.get(url)
        
        # Wait for page to initialize
        print("Waiting for page to initialize...")
        time.sleep(3)
        
        # Look for and click the Horizon tab
        print("Looking for Horizon tab...")
        
        # Try multiple strategies to find the Horizon tab
        horizon_clicked = False
        
        # Strategy 1: Find by exact text
        try:
            elements = driver.find_elements(By.XPATH, "//*[text()='Horizon']")
            if elements:
                print(f"Found Horizon tab by exact text match")
                elements[0].click()
                horizon_clicked = True
        except:
            pass
        
        # Strategy 2: Find by partial text (case-insensitive)
        if not horizon_clicked:
            try:
                elements = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'HORIZON', 'horizon'), 'horizon')]")
                for elem in elements:
                    if 'horizon' in elem.text.lower():
                        print(f"Found Horizon tab by partial text: {elem.text}")
                        elem.click()
                        horizon_clicked = True
                        break
            except:
                pass
        
        # Strategy 3: Find clickable elements and check their text
        if not horizon_clicked:
            try:
                clickable_elements = driver.find_elements(By.XPATH, "//button | //a | //div[@role='button'] | //span[@role='button']")
                for elem in clickable_elements:
                    try:
                        text = elem.text.strip().lower()
                        if 'horizon' in text:
                            print(f"Found Horizon tab in clickable element: {elem.text}")
                            elem.click()
                            horizon_clicked = True
                            break
                    except:
                        continue
            except:
                pass
        
        if not horizon_clicked:
            print("\nCould not find Horizon tab. Debugging information:")
            print("=" * 60)
            
            # Print all clickable elements
            try:
                clickable = driver.find_elements(By.XPATH, "//button | //a | //div[@role='button']")
                print(f"\nFound {len(clickable)} clickable elements:")
                for i, elem in enumerate(clickable[:20]):  # First 20 only
                    try:
                        print(f"  {i+1}. Tag: {elem.tag_name}, Text: '{elem.text[:50]}'")
                    except:
                        pass
            except:
                pass
            
            # Print page text
            print("\nPage text (first 1000 chars):")
            print(driver.find_element(By.TAG_NAME, "body").text[:1000])
            print("=" * 60)
            
            raise Exception("Horizon tab not found")
        
        print("Clicked Horizon tab, waiting for image to load...")
        time.sleep(5)  # Wait for horizon image to generate
        
        # Look for the specific skyline canvas
        print("Looking for skyline canvas...")
        
        # Wait a bit more for canvas to render
        time.sleep(2)
        
        image_element = None
        
        # Strategy 1: Look for the specific skyline-canvas-v2
        try:
            print("Searching for canvas#skyline-canvas-v2...")
            canvas = driver.find_element(By.ID, 'skyline-canvas-v2')
            
            if canvas and canvas.is_displayed():
                width = canvas.size.get('width', 0)
                height = canvas.size.get('height', 0)
                print(f"Found skyline canvas: {width}x{height}")
                print("Taking screenshot of canvas...")
                canvas.screenshot(output_file)
                print(f"✓ Horizon canvas saved to: {output_file}")
                return
            else:
                print("Canvas found but not displayed")
        except Exception as e:
            print(f"Could not find skyline-canvas-v2: {e}")
        
        # Strategy 2: Look for any canvas in the left sidebar
        try:
            canvases = driver.find_elements(By.TAG_NAME, 'canvas')
            print(f"Found {len(canvases)} canvas elements total")
            
            for i, canvas in enumerate(canvases):
                try:
                    canvas_id = canvas.get_attribute('id') or 'no-id'
                    if canvas.is_displayed():
                        location = canvas.location
                        width = canvas.size.get('width', 0)
                        height = canvas.size.get('height', 0)
                        x_pos = location.get('x', 0)
                        
                        print(f"  Canvas {i+1}: id='{canvas_id}', x={x_pos}, size={width}x{height}")
                        
                        # Look for canvas in left sidebar with reasonable size
                        if x_pos < 500 and width > 200 and height > 200:
                            print(f"  ✓ Using this canvas (left sidebar, good size)")
                            canvas.screenshot(output_file)
                            print(f"✓ Canvas screenshot saved to: {output_file}")
                            return
                except Exception as e:
                    print(f"  Error processing canvas {i+1}: {e}")
        except Exception as e:
            print(f"Error finding canvases: {e}")
        
        # Strategy 3: Look for images in the left sidebar as fallback
        try:
            all_images = driver.find_elements(By.TAG_NAME, 'img')
            print(f"\nFallback: Found {len(all_images)} img elements")
            
            left_side_images = []
            for img in all_images:
                try:
                    src = img.get_attribute('src')
                    if src and img.is_displayed():
                        location = img.location
                        width = img.size.get('width', 0)
                        height = img.size.get('height', 0)
                        x_pos = location.get('x', 0)
                        
                        if x_pos < 500 and width > 100 and height > 100:
                            left_side_images.append((img, width * height, src))
                except:
                    continue
            
            if left_side_images:
                left_side_images.sort(key=lambda x: x[1], reverse=True)
                image_element = left_side_images[0][0]
                print(f"Using fallback image: {left_side_images[0][2][:80]}...")
        except Exception as e:
            print(f"Error in fallback: {e}")
        
        if not image_element:
            print("\nCould not find horizon image. Debug information:")
            print("=" * 60)
            
            # List all images again with more details
            all_imgs = driver.find_elements(By.TAG_NAME, 'img')
            print(f"\nAll {len(all_imgs)} img elements:")
            for i, img in enumerate(all_imgs):
                try:
                    src = img.get_attribute('src') or 'no src'
                    alt = img.get_attribute('alt') or 'no alt'
                    displayed = img.is_displayed()
                    size = img.size
                    print(f"  {i+1}. Displayed: {displayed}, Size: {size}, Alt: '{alt}'")
                    print(f"      Src: {src[:100]}")
                except Exception as e:
                    print(f"  {i+1}. Error: {e}")
            
            print("=" * 60)
            raise Exception("Could not find horizon image")
        
        # Get the image source
        image_url = image_element.get_attribute('src')
        print(f"Image URL: {image_url}")
        
        # Download the image
        print(f"Downloading image...")
        
        # If it's a data URL, save it directly
        if image_url.startswith('data:'):
            print("Image is a data URL, extracting...")
            header, encoded = image_url.split(',', 1)
            data = base64.b64decode(encoded)
            with open(output_file, 'wb') as f:
                f.write(data)
        else:
            # Make URL absolute if needed
            if image_url.startswith('/'):
                image_url = 'https://www.eclipsefan.org' + image_url
            elif not image_url.startswith('http'):
                image_url = 'https://www.eclipsefan.org/' + image_url
            
            # Download using requests with the same session cookies
            import urllib.request
            req = urllib.request.Request(image_url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req) as response:
                image_data = response.read()
            
            with open(output_file, 'wb') as f:
                f.write(image_data)
        
        print(f"✓ Horizon image saved to: {output_file}")
        
        if not headless:
            print("\nBrowser window will close in 3 seconds...")
            time.sleep(3)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Take a screenshot for debugging
        debug_file = "debug_screenshot.png"
        driver.save_screenshot(debug_file)
        print(f"\nDebug screenshot saved to: {debug_file}")
        sys.exit(1)
        
    finally:
        driver.quit()

def main():
    # Default URL for Spain eclipse location
    default_url = "https://www.eclipsefan.org/?lat=42.083378&lng=-2.085237&zoom=6&oz=5&lang=en"
    
    # Allow custom URL from command line
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    output_file = sys.argv[2] if len(sys.argv) > 2 else "horizon_image.png"
    
    download_horizon_image(url, output_file)

if __name__ == "__main__":
    main()

# Made with Bob
