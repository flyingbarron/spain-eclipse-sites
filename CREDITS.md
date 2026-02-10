# Credits and Data Attribution

## Project Creator

**Robert Barron**
- Project conception and development
- Data collection and integration
- Web viewer design and implementation
- Documentation and attribution

This project uses data and services from multiple sources. We respect the terms of service and provide proper attribution.

## Data Sources

### 1. IGME (Instituto Geológico y Minero de España)
**Website**: https://info.igme.es/ielig/

**Data Used**:
- IELIG Database (Spanish Inventory of Sites of Geological Interest)
- Site names, descriptions, and tourist value ratings
- GPS coordinates via MapServer API
- Site photographs

**Usage**: 
- IGME data is publicly accessible for educational and research purposes
- This project is for non-commercial educational use
- All data is properly attributed to IGME
- We recommend users verify current IGME terms of service

**Attribution**: 
> Data sourced from IGME (Instituto Geológico y Minero de España) - IELIG Database
> © Instituto Geológico y Minero de España

### 2. IGN (Instituto Geográfico Nacional)
**Website**: https://visualizadores.ign.es/eclipses/2026

**Data Used**:
- Eclipse 2026 Viewer for visibility calculations
- Eclipse visibility profiles and diagrams
- Astronomical calculations for the August 12, 2026 eclipse

**Usage**:
- IGN provides this data for public information about the 2026 eclipse
- Used for educational and planning purposes
- This is a non-commercial research project

**Attribution**:
> Eclipse visibility data from IGN (Instituto Geográfico Nacional) Eclipse 2026 Viewer
> © Instituto Geográfico Nacional de España

### 3. EclipseFan.org
**Website**: https://www.eclipsefan.org/

**Data Used**:
- Horizon skyline visualizations
- Eclipse path maps and interactive viewer

**Usage**:
- Screenshots and horizon images for educational purposes
- Non-commercial use for eclipse planning
- Users should respect EclipseFan.org terms of service

**Attribution**:
> Horizon visualizations from EclipseFan.org
> © EclipseFan.org

### 4. timeanddate.com
**Website**: https://www.timeanddate.com/

**Data Used**:
- Historical cloud coverage statistics for eclipse date (August 12)
- Weather pattern data for site locations

**Usage**:
- Data scraped from publicly accessible pages
- Used for educational eclipse planning purposes
- Non-commercial use only

**Attribution**:
> Historical cloud coverage data from timeanddate.com
> © Time and Date AS

## Third-Party Services

### 5. Shademap.app
**Website**: https://shademap.app/

**Data Used**:
- Sun and shadow visualization tool
- Shademap snapshots for each site showing sun position at eclipse time
- Interactive shadow maps for site analysis

**Usage**:
- Screenshots captured via Playwright automation
- Stored locally in `data/shademap_snapshot/`
- Linked from viewer for interactive sun/shadow analysis
- Helps users understand lighting conditions at eclipse time

**Attribution**:
> Shademap visualizations from Shademap.app
> © Shademap

### 6. Google Maps
**Website**: https://maps.google.com/

**Data Used**:
- Google Maps Static API for location thumbnails
- Interactive maps for site location and routing
- Satellite imagery for site context

**Usage**:
- Static API thumbnails (400x200px satellite view) displayed in viewer
- Links to interactive Google Maps for each site
- Routing functionality for trip planning
- Subject to Google Maps Terms of Service and API usage limits

**Attribution**:
> Map data and imagery from Google Maps
> © Google LLC

**API Key**: Configured in `config.yaml` - users must provide their own Google Maps API key

### 7. Leaflet & OpenStreetMap
**Websites**:
- https://leafletjs.com/
- https://www.openstreetmap.org/

**Data Used**:
- Interactive map display in viewer
- Map tiles from OpenStreetMap contributors
- Leaflet Routing Machine for route planning

**Usage**:
- Open-source mapping library (Leaflet)
- Map data © OpenStreetMap contributors
- Used under Open Database License (ODbL)

**Attribution**:
> Map data © OpenStreetMap contributors
> Leaflet mapping library © Vladimir Agafonkin
> https://www.openstreetmap.org/copyright

## Web Scraping Ethics

This project follows ethical web scraping practices:

1. **Rate Limiting**: Implements delays between requests (1+ seconds)
2. **Respectful**: Does not overload servers or bypass security measures
3. **Attribution**: Properly credits all data sources
4. **Non-Commercial**: Educational and research use only
5. **Robots.txt**: Respects robots.txt directives where applicable
6. **User-Agent**: Identifies itself properly in requests
7. **Caching**: Stores data locally to minimize repeated requests

## Usage Recommendations

If you use this project or its data:

1. **Verify Terms**: Check current terms of service for all data sources
2. **Non-Commercial**: Keep usage non-commercial and educational
3. **Attribution**: Maintain proper attribution to all sources
4. **Updates**: Be aware that data and terms may change
5. **Respect**: Follow ethical scraping practices
6. **Contact**: Consider contacting data providers for large-scale use

## Disclaimer

This project is provided "as-is" for educational purposes. Users are responsible for:
- Complying with all applicable terms of service
- Verifying data accuracy
- Respecting intellectual property rights
- Following local laws and regulations

The authors make no warranties about data accuracy or completeness.

## License

This project's code is provided for educational use. Data remains property of respective sources.

## Contact

For questions about data usage or attribution, please:
1. Review the terms of service of each data source
2. Contact the respective organizations directly
3. Ensure compliance with all applicable policies

---

**Last Updated**: February 2026

**Note**: Terms of service and data availability may change. Always verify current policies with data providers.