# Configuration Guide

This document explains all configuration options for the Spain Eclipse Sites application.

## Configuration Files

### config.yaml

The main configuration file with all application settings.

```yaml
# Application Information
app:
  name: "Spain Eclipse Sites"
  version: "1.0.0"
  environment: "production"  # development, staging, production

# Directories (relative to project root)
directories:
  data: "data"                           # Main data directory
  scrape: "data/scrape"                  # Scraped/downloaded pipeline assets
  profiles: "data/scrape/ign_profiles"   # IGN eclipse profiles
  horizon: "data/scrape/eclipsefan_horizons"  # EclipseFan horizons
  shademap: "data/scrape/shademap_snapshots"  # Shademap snapshots
  brochures: "data/brochures"            # Downloaded brochure PDFs
  cache: "data/cache"                    # Viewer-side IGME cache files
  logs: "logs"                           # Application logs

# Eclipse Configuration
eclipse:
  date: "2026-08-12"              # Eclipse date
  date_iso: "20260812"            # ISO format date
  azimuth: 283.7753               # Eclipse azimuth in degrees
  azimuth_line_distance_km: 50    # Length of azimuth lines in KML

# Scraping Settings
scraping:
  request_timeout: 10             # HTTP request timeout (seconds)
  rate_limit_delay: 1.0           # Delay between IGME requests (seconds)
  cloud_scrape_delay: 2.0         # Delay between cloud requests (seconds)
  horizon_scrape_delay: 2.0       # Delay between horizon requests (seconds)
  max_retries: 3                  # Maximum retry attempts
  retry_delay: 2.0                # Delay between retries (seconds)
  user_agent: "Mozilla/5.0..."    # User agent string

# External URLs
urls:
  igme_base: "https://info.igme.es/ielig/LIGInfo.aspx?codigo="
  igme_api: "https://mapas.igme.es/gis/rest/services/BasesDatos/IGME_IELIG/MapServer/0/query"
  ign_eclipse: "https://visualizadores.ign.es/eclipses/2026"
  timeanddate: "https://www.timeanddate.com/eclipse/in/@{lat},{lon}?iso={date}"
  eclipsefan: "https://www.eclipsefan.org/?lat={lat}&lng={lon}&zoom=6&oz=5&lang=en"

# Logging Configuration
logging:
  level: "INFO"                   # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/app.log"            # Log file path
  max_bytes: 10485760             # Max log file size (10MB)
  backup_count: 5                 # Number of backup log files

# Web Server Settings
server:
  host: "0.0.0.0"                 # Bind address (0.0.0.0 for containers)
  port: 8000                      # Server port
  debug: false                    # Debug mode

# Feature Flags
features:
  enable_caching: false           # Enable API response caching
  enable_eclipse_checking: true   # Enable eclipse visibility checking
  enable_cloud_coverage: true     # Enable cloud coverage scraping
  enable_horizon_download: true   # Enable horizon image downloading

# CSV Output Configuration
csv:
  filename: "eclipse_site_data.csv"
  fieldnames:
    - code
    - denominacion
    - url
    - valor_turistico
    - confidencialidad
    - route_difficulty
    - latitude
    - longitude
    - eclipse_visibility
    - status
    - cloud_coverage
    - cloud_status
    - cloud_url
    - horizon_status

# KML Output Configuration
kml:
  filename: "sites.kml"
  document_name: "Spain Eclipse Sites - Organized by Tourist Value and Eclipse Visibility"
  document_description: "Geological sites from IGME IELIG database organized into six categories"
```

## Environment Variables

Override configuration using environment variables (useful for containers):

### Format

Environment variables use the prefix `ECLIPSE_SITES_` followed by the configuration path in uppercase with underscores:

```
ECLIPSE_SITES_<SECTION>_<KEY>=value
```

### Examples

```bash
# Server configuration
ECLIPSE_SITES_SERVER_HOST=0.0.0.0
ECLIPSE_SITES_SERVER_PORT=9000
ECLIPSE_SITES_SERVER_DEBUG=true

# Logging
ECLIPSE_SITES_LOGGING_LEVEL=DEBUG
ECLIPSE_SITES_LOGGING_FILE=logs/debug.log

# Scraping
ECLIPSE_SITES_SCRAPING_REQUEST_TIMEOUT=15
ECLIPSE_SITES_SCRAPING_RATE_LIMIT_DELAY=2.0

# Feature flags
ECLIPSE_SITES_FEATURES_ENABLE_CACHING=true
ECLIPSE_SITES_FEATURES_ENABLE_ECLIPSE_CHECKING=false
```

### Type Conversion

Environment variables are automatically converted to appropriate types:
- `"true"` / `"false"` → boolean
- `"123"` → integer
- `"1.5"` → float
- Other values → string

## Configuration in Code

### Accessing Configuration

```python
from src.config import config

# Get values using dot notation
timeout = config.get('scraping.request_timeout')  # Returns 10
port = config.get('server.port')  # Returns 8000

# Get with default value
cache_enabled = config.get('features.enable_caching', False)

# Get directory paths
data_dir = config.get_path('directories.data')  # Returns Path object
```

### Using Convenience Constants

```python
from src.config import (
    ECLIPSE_DATE,
    ECLIPSE_AZIMUTH,
    REQUEST_TIMEOUT,
    DATA_DIR,
    PROFILES_DIR
)

print(f"Eclipse date: {ECLIPSE_DATE}")
print(f"Data directory: {DATA_DIR}")
```

## Configuration Sections Explained

### App Section

Basic application metadata:
- `name`: Application name
- `version`: Version number
- `environment`: Deployment environment (development/staging/production)

### Directories Section

All paths are relative to project root:
- `data`: Main data output directory
- `scrape`: Shared root for downloaded/scraped enrichment assets
- `profiles`: IGN eclipse visibility profile images
- `horizon`: EclipseFan horizon profile images
- `shademap`: Shademap snapshot images
- `brochures`: Downloaded brochure PDFs
- `cache`: Viewer-side IGME HTML/image cache files
- `logs`: Application log files

### Eclipse Section

Eclipse-specific settings:
- `date`: Human-readable eclipse date
- `date_iso`: ISO format date for API calls
- `azimuth`: Eclipse direction in degrees (283.7753° for 2026 eclipse)
- `azimuth_line_distance_km`: Length of direction lines in KML files

### Scraping Section

Web scraping behavior:
- `request_timeout`: How long to wait for HTTP responses
- `rate_limit_delay`: Delay between requests (be respectful!)
- `cloud_scrape_delay`: Specific delay for cloud coverage API
- `horizon_scrape_delay`: Specific delay for horizon images
- `max_retries`: Retry failed requests this many times
- `retry_delay`: Wait time between retries
- `user_agent`: Browser identification string

### URLs Section

External service endpoints:
- `igme_base`: IGME site information pages
- `igme_api`: IGME MapServer API for coordinates
- `ign_eclipse`: IGN Eclipse 2026 viewer
- `timeanddate`: Cloud coverage data source
- `eclipsefan`: Horizon visualization service

### Logging Section

Logging configuration:
- `level`: Minimum log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `format`: Log message format string
- `file`: Log file path
- `max_bytes`: Maximum log file size before rotation
- `backup_count`: Number of rotated log files to keep

### Server Section

Web server settings:
- `host`: Bind address (use 0.0.0.0 for containers)
- `port`: HTTP port number
- `debug`: Enable debug mode (more verbose output)

### Features Section

Feature toggles:
- `enable_caching`: Cache API responses to reduce requests
- `enable_eclipse_checking`: Check eclipse visibility (requires Selenium)
- `enable_cloud_coverage`: Scrape cloud coverage data
- `enable_horizon_download`: Download horizon images

Note: the main pipeline’s canonical output directories and step names are now defined in [`src/constants.py`](src/constants.py), while this document describes the configurable application settings exposed through [`config.yaml`](config.yaml).

### CSV Section

CSV output configuration:
- `filename`: Output CSV filename
- `fieldnames`: List of columns to include

### KML Section

KML output configuration:
- `filename`: Output KML filename
- `document_name`: KML document title
- `document_description`: KML document description

## Development vs Production

### Development Configuration

Create `config.dev.yaml`:

```yaml
app:
  environment: "development"

server:
  debug: true

logging:
  level: "DEBUG"

scraping:
  rate_limit_delay: 0.5  # Faster for testing

features:
  enable_caching: false  # Always fetch fresh data
```

Load with:
```python
config = Config('config.dev.yaml')
```

### Production Configuration

Use environment variables in production:

```bash
export ECLIPSE_SITES_LOGGING_LEVEL=INFO
export ECLIPSE_SITES_SERVER_DEBUG=false
export ECLIPSE_SITES_FEATURES_ENABLE_CACHING=true
```

Or use Docker environment variables in `docker-compose.yml`.

## Best Practices

1. **Never commit sensitive data** to config files
2. **Use environment variables** for deployment-specific settings
3. **Keep rate limits respectful** to avoid overwhelming servers
4. **Enable caching in production** to reduce API calls
5. **Use DEBUG logging** only during development
6. **Set appropriate timeouts** based on your network
7. **Monitor log file sizes** and adjust rotation settings

## Troubleshooting

### Configuration not loading

Check that `config.yaml` exists in the project root:
```bash
ls -la config.yaml
```

### Environment variables not working

Verify the variable name format:
```bash
echo $ECLIPSE_SITES_SERVER_PORT
```

### Permission errors

Ensure directories are writable:
```bash
chmod 755 data logs .cache
```

### Import errors

Make sure PyYAML is installed:
```bash
pip install pyyaml
```

## See Also

- [README.md](README.md) - Main documentation
- [DOCKER.md](DOCKER.md) - Docker deployment guide
- [.env.example](.env.example) - Environment variable template

## Made with Bob