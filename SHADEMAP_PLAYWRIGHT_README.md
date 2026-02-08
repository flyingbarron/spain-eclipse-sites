# Shademap Export with Playwright

This script automates downloading shadow map visualizations from Shademap.app using Playwright, which is more reliable than Selenium for modern web applications.

## Installation

```bash
# Install Playwright
pip install playwright

# Install browser binaries
playwright install chromium
```

## Usage

```bash
# Use default URL (Spain eclipse location at eclipse time)
python3 download_shademap_export_playwright.py

# Custom URL
python3 download_shademap_export_playwright.py "https://shademap.app/@42.13096,-2.15972,20z,1786559455614t,0b,0p,0m"

# Custom URL and output filename
python3 download_shademap_export_playwright.py "https://shademap.app/@42.13096,-2.15972,20z" "my_export.jpg"
```

## Features

- **Headless by default**: Runs in background without visible browser window
- **Automatic popup dismissal**: Clicks "OK" on any popups
- **Auto-zoom**: Zooms in 3 times for better detail
- **JPG export**: Automatically exports and saves as JPG
- **Download handling**: Properly captures and saves the downloaded file
- **Debug screenshots**: Takes screenshots on errors for troubleshooting
- **Anti-detection**: Uses realistic user agent and removes automation flags

## Default URL

The script defaults to:
```
https://shademap.app/@42.13096,-2.15972,20z,1786559455614t,0b,0p,0m!1786511647543!1786562164762,qDMKLwoxMyo5NTgsIC0zCi8KMTU5NzIw=!42.13096!-2.15972
```

This shows the shadow map for the August 12, 2026 total solar eclipse over Spain at the moment of totality.

## Advantages over Selenium

1. **More reliable**: Better handling of modern web apps
2. **Easier setup**: No need to manage separate driver binaries
3. **Better download handling**: Built-in download capture
4. **Faster**: More efficient browser automation
5. **Better selectors**: More flexible element selection with `:has-text()` and other pseudo-selectors

## Troubleshooting

### Playwright not installed
```bash
pip install playwright
playwright install chromium
```

### Browser fails to launch
```bash
# Reinstall browser binaries
playwright install chromium --force
```

### Elements not found
The script tries multiple selectors for each element. If it still fails:
1. Check the debug screenshot (`shademap_playwright_debug.png`)
2. Run with `headless=False` to see what's happening:
   - Edit the script and change `headless=True` to `headless=False` in the function definition

### Download not working
The script uses Playwright's built-in download handling. If the file doesn't appear:
1. Check the `data/` directory
2. Look for error messages in the console output
3. Check the debug screenshot

## Output

The script saves the exported JPG to the `data/` directory (default: `data/shademap_export.jpg`).

## Comparison with Selenium versions

| Feature | Playwright | Selenium Chrome | Selenium Firefox | Selenium Safari |
|---------|-----------|-----------------|------------------|-----------------|
| Setup complexity | Easy | Medium | Medium | Easy |
| Reliability | High | Medium | Medium | Low |
| Download handling | Built-in | Manual | Manual | Manual |
| Headless mode | Yes | Yes | Yes | No |
| Speed | Fast | Medium | Slow | Medium |
| Modern web apps | Excellent | Good | Good | Fair |

**Recommendation**: Use Playwright version for best results.

## Made with Bob