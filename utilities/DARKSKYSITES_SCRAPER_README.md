# Dark Sky Sites Data Scraper

This utility scrapes data from [darkskysites.com](https://www.darkskysites.com/) including the mouseover popup information that shows light pollution data, Bortle scale, and other dark sky metrics for specific locations.

## Prerequisites

Install Playwright and its browser dependencies:

```bash
pip install playwright
playwright install chromium
```

## Usage

### Scrape a Single Site

Scrape data for a specific site by its code (reads coordinates from CSV):

```bash
python3 utilities/scrape_darkskysites_data.py --code IB200a
```

### Scrape All Sites

Process all sites from the eclipse site data CSV:

```bash
python3 utilities/scrape_darkskysites_data.py --all
```

### Scrape Custom Coordinates

Scrape data for any latitude/longitude:

```bash
python3 utilities/scrape_darkskysites_data.py --lat 40.6941 --lon -2.01107
```

### Run in Headless Mode

For faster processing without opening browser windows:

```bash
python3 utilities/scrape_darkskysites_data.py --all --headless
```

### Adjust Delay Between Requests

Change the delay between sites (default is 3 seconds):

```bash
python3 utilities/scrape_darkskysites_data.py --all --delay 5.0
```

## Command-Line Options

- `--code`, `-c`: Site code to scrape (e.g., IB200a)
- `--all`: Scrape all sites from CSV
- `--csv`: Path to CSV file (default: ./data/eclipse_site_data.csv)
- `--lat`: Latitude for custom location
- `--lon`: Longitude for custom location
- `--headless`: Run browser in headless mode (no visible window)
- `--delay`: Delay between sites in seconds (default: 3.0)

## Output

The scraper creates the following files in `data/scrape/darkskysites/`:

### Per-Site Files

- `{site_code}_data.json`: JSON file with scraped data including:
  - Site code and coordinates
  - URL used for scraping
  - Popup data (text content from mouseover window)
  - Status (success/failed/no_popup_found)
  
- `{site_code}_screenshot.png`: Screenshot of the Dark Sky Sites page for reference

### Summary File

- `scrape_summary.json`: Summary of all scraping results when using `--all`

## Example Output

```json
{
  "site_code": "IB200a",
  "latitude": 40.6941,
  "longitude": -2.01107,
  "url": "https://www.darkskysites.com/?lat=40.6941&lng=-2.01107&zoom=8",
  "popup_data": "SQM:\n21.56\nBortle:\n3~\nDarkness:\n85.0%\nObserving Quality\n42.12°N, 2.19°W",
  "parsed_data": {
    "sqm": 21.56,
    "bortle": 3,
    "darkness": 85.0,
    "coordinates": "42.12°N, 2.19°W",
    "raw_text": "SQM:\n21.56\nBortle:\n3~\nDarkness:\n85.0%\nObserving Quality\n42.12°N, 2.19°W"
  },
  "status": "success"
}
```

### Parsed Data Fields

- **sqm**: Sky Quality Meter reading (float) - higher values indicate darker skies (typical range: 18-22)
- **bortle**: Bortle scale classification (integer 1-9) - lower values indicate darker skies
- **darkness**: Darkness percentage (float 0-100) - higher values indicate darker conditions
- **coordinates**: Coordinates string from the tooltip (if present)
- **raw_text**: Original unprocessed tooltip text

**Note:** The "Observing Quality" indicator appears as a visual bar/graph in the tooltip and cannot be extracted from text. It would require image analysis or DOM inspection of the bar element to quantify.

## What Data is Captured?

The scraper follows this process:

1. **Closes the automatic popup**: Dismisses any welcome/info popup that appears on page load
2. **Finds the blue dot marker**: Locates the marker at the specified coordinates
3. **Hovers over the marker**: Triggers the mouseover tooltip
4. **Captures tooltip data**: Extracts the information that appears, which typically includes:
   - **Bortle Scale**: Light pollution classification (1-9)
   - **SQM (Sky Quality Meter)**: Measurement of sky brightness
   - **Light Pollution Level**: Descriptive classification
   - **Location name** (if available)
   - **Any other metrics** displayed in the tooltip

## Troubleshooting

### No Tooltip Found

If the scraper reports "no_tooltip_found", it may be because:
- The page structure has changed
- The marker is not visible or in a different location
- The tooltip requires different interaction
- JavaScript hasn't fully loaded

Try running without `--headless` to see what's happening in the browser. The scraper will save a debug screenshot when no tooltip is found.

### Debug Screenshots

When errors occur, the scraper saves debug screenshots to help identify issues:
- `darkskysites_error_debug.png`: Screenshot when an error occurs

### Rate Limiting

Be respectful of the Dark Sky Sites server:
- Use appropriate delays between requests (default: 3 seconds)
- Consider running during off-peak hours for bulk scraping
- Don't run the scraper too frequently

## Integration with Eclipse Site Data

The scraped data can be integrated into the main eclipse site dataset:

1. Run the scraper for all sites
2. Parse the JSON output files
3. Add relevant fields (Bortle, SQM, etc.) to the CSV
4. Update the viewer to display this information

## Notes

- The scraper uses Playwright for reliable browser automation
- Screenshots are saved for each site for manual verification
- The script handles errors gracefully and continues with remaining sites
- All data is saved in JSON format for easy parsing and integration

## Related Files

- `src/bortle_scraper.py`: Alternative Bortle scale scraper using lightpollutionmap.info
- `utilities/download_shademap_export_playwright.py`: Shademap screenshot scraper
- `src/cloud_coverage_scraper.py`: Cloud coverage data scraper

---

Made with Bob 🤖