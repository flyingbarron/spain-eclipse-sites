# EclipseFan Screenshot Scripts

Two scripts are provided to take screenshots of the EclipseFan.org eclipse map.

## Option 1: Selenium (take_eclipsefan_screenshot.py)

### Installation
```bash
# Install Selenium
pip install selenium

# Install ChromeDriver (macOS)
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

### Usage
```bash
# Use default URL (Spain eclipse location)
python3 take_eclipsefan_screenshot.py

# Custom URL
python3 take_eclipsefan_screenshot.py "https://www.eclipsefan.org/?lat=40.0&lng=-3.0&zoom=8&oz=5&lang=en"

# Custom URL and output filename
python3 take_eclipsefan_screenshot.py "https://www.eclipsefan.org/?lat=40.0&lng=-3.0&zoom=8&oz=5&lang=en" "my_screenshot.png"
```

## Option 2: Playwright (take_eclipsefan_screenshot_playwright.py) - RECOMMENDED

Playwright is easier to set up and more reliable.

### Installation
```bash
# Install Playwright
pip install playwright

# Install browser binaries
playwright install chromium
```

### Usage
```bash
# Use default URL (Spain eclipse location)
python3 take_eclipsefan_screenshot_playwright.py

# Custom URL
python3 take_eclipsefan_screenshot_playwright.py "https://www.eclipsefan.org/?lat=40.0&lng=-3.0&zoom=8&oz=5&lang=en"

# Custom URL and output filename
python3 take_eclipsefan_screenshot_playwright.py "https://www.eclipsefan.org/?lat=40.0&lng=-3.0&zoom=8&oz=5&lang=en" "my_screenshot.png"
```

## Default URL

Both scripts default to:
```
https://www.eclipsefan.org/?lat=42.083378&lng=-2.085237&zoom=6&oz=5&lang=en
```

This shows the eclipse path over Spain.

## Features

- **Headless mode**: Runs in background without opening a browser window
- **Full HD resolution**: 1920x1080 screenshot
- **Automatic waiting**: Waits for page and map to load
- **Customizable**: Can specify any URL and output filename

## Troubleshooting

### Selenium Issues
If you get "chromedriver not found":
```bash
# macOS
brew install chromedriver

# Or manually download and add to PATH
```

### Playwright Issues
If browser fails to launch:
```bash
# Reinstall browser binaries
playwright install chromium --force
```

### Map Not Fully Loaded
Increase wait time by editing the script:
- Selenium: Change `wait_time=5` to `wait_time=10`
- Playwright: Change `wait_time=5000` to `wait_time=10000`

## Output

Both scripts create a PNG file (default: `eclipsefan_screenshot.png`) in the current directory.