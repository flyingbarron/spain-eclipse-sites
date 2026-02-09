# Code Refactoring Suggestions

## Overview
This document outlines suggestions to improve code maintainability, readability, and organization for the Spain Eclipse Sites project.

---

## 1. JavaScript Frontend (app.js - 1442 lines)

### Priority: HIGH
**Problem**: Single 1442-line file handling all frontend logic makes it difficult to maintain and test.

### Recommendations:

#### A. Split into Modular Files
Create a `static/js/` directory with separate modules:

```
static/js/
├── config.js          # Constants and configuration
├── data-loader.js     # CSV loading and parsing
├── site-display.js    # Site list rendering and filtering
├── site-details.js    # Detail view rendering
├── map-handler.js     # Leaflet map and routing logic
├── modal-handler.js   # Image carousel and info panels
├── drag-drop.js       # Drag and drop functionality
├── utils.js           # Utility functions (DMS conversion, etc.)
└── main.js            # Main initialization and event coordination
```

#### B. Use ES6 Modules
Replace global variables with proper module exports:

```javascript
// config.js
export const HOTEL_COORDS = [42.2167, -2.2833];
export const CSV_PATH = 'data/eclipse_site_data_with_cloud.csv';

// data-loader.js
export class DataLoader {
    async loadCSV(path) { /* ... */ }
    parseCSV(text) { /* ... */ }
}

// main.js
import { DataLoader } from './data-loader.js';
import { SiteDisplay } from './site-display.js';
```

#### C. Implement State Management
Create a simple state manager to avoid scattered global variables:

```javascript
// state.js
export class AppState {
    constructor() {
        this.sites = [];
        this.currentSite = null;
        this.selectedSites = [];
        this.activeTab = 'details';
        this.filters = { search: '', eclipseOnly: false };
    }
    
    subscribe(callback) { /* ... */ }
    setState(updates) { /* ... */ }
}
```

---

## 2. Python Backend Structure

### Priority: MEDIUM

#### A. Create Configuration Module
**File**: `src/config.py`

```python
"""
Configuration constants for the project
"""
import os

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILES_DIR = os.path.join(DATA_DIR, "eclipse_profiles")
SHADEMAP_DIR = os.path.join(DATA_DIR, "shademap")

# Eclipse constants
ECLIPSE_DATE = "2026-08-12"
ECLIPSE_DATE_ISO = "20260812"
ECLIPSE_AZIMUTH = 283.7753
AZIMUTH_LINE_DISTANCE_KM = 50

# Scraping settings
REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 1.0
CLOUD_SCRAPE_DELAY = 2.0

# URLs
IGME_BASE_URL = "https://info.igme.es/ielig/LIGInfo.aspx?codigo="
IGME_API_URL = "https://mapas.igme.es/gis/rest/services/BasesDatos/IGME_IELIG/MapServer/0/query"
IGN_ECLIPSE_URL = "https://visualizadores.ign.es/eclipses/2026"
```

#### B. Add Type Hints Throughout
Improve code documentation with type hints:

```python
from typing import List, Dict, Optional, Tuple

def scrape_site(code: str, url: str) -> Optional[Dict[str, str]]:
    """Scrape a single IGME site"""
    pass

def calculate_endpoint(
    lat: float, 
    lon: float, 
    azimuth: float, 
    distance_km: float = 50
) -> Tuple[float, float]:
    """Calculate endpoint coordinates"""
    pass
```

#### C. Create Data Models
**File**: `src/models.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Site:
    code: str
    denominacion: str
    url: str
    valor_turistico: float
    confidencialidad: str
    route_difficulty: str
    latitude: Optional[float]
    longitude: Optional[float]
    eclipse_visibility: str = 'not_checked'
    cloud_coverage: Optional[int] = None
    cloud_status: str = 'not_checked'
    cloud_url: Optional[str] = None
    status: str = 'pending'
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV export"""
        return {
            'code': self.code,
            'denominacion': self.denominacion,
            # ... etc
        }
```

---

## 3. Error Handling Improvements

### Priority: MEDIUM

#### A. Create Custom Exceptions
**File**: `src/exceptions.py`

```python
class ScraperException(Exception):
    """Base exception for scraper errors"""
    pass

class CoordinateError(ScraperException):
    """Raised when coordinates are invalid or missing"""
    pass

class NetworkError(ScraperException):
    """Raised when network requests fail"""
    pass

class ParsingError(ScraperException):
    """Raised when HTML parsing fails"""
    pass
```

#### B. Implement Retry Logic
Add retry decorator for network requests:

```python
# src/utils.py
from functools import wraps
import time

def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2.0)
def fetch_with_retry(url):
    """Fetch URL with automatic retry"""
    pass
```

---

## 4. Testing Infrastructure

### Priority: MEDIUM

#### A. Add Unit Tests
Create `tests/unit/` directory:

```
tests/
├── unit/
│   ├── test_igme_scraper.py
│   ├── test_eclipse_checker.py
│   ├── test_output_generator.py
│   └── test_utils.py
├── integration/
│   └── test_full_pipeline.py
└── fixtures/
    ├── sample_igme_page.html
    └── sample_site_data.json
```

Example test:

```python
# tests/unit/test_igme_scraper.py
import pytest
from src.igme_scraper import clean_site_name, web_mercator_to_lat_lon

def test_clean_site_name():
    raw = "Icnitas de dinosaurio del Weald de Cameros (La Rioja). Yacimiento de Test Site"
    expected = "Test Site"
    assert clean_site_name(raw) == expected

def test_web_mercator_conversion():
    x, y = 0, 0
    lat, lon = web_mercator_to_lat_lon(x, y)
    assert abs(lat) < 0.01  # Near equator
    assert abs(lon) < 0.01  # Near prime meridian
```

---

## 5. Code Quality Improvements

### Priority: LOW-MEDIUM

#### A. Add Logging
Replace print statements with proper logging:

```python
# src/logger.py
import logging
import sys

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Setup logger with consistent formatting"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Usage in modules:
from src.logger import setup_logger
logger = setup_logger(__name__)

logger.info(f"Scraping site {code}")
logger.error(f"Failed to fetch: {e}")
```

#### B. Add Docstring Standards
Use consistent docstring format (Google style):

```python
def calculate_endpoint(lat: float, lon: float, azimuth: float, 
                      distance_km: float = 50) -> Tuple[float, float]:
    """Calculate endpoint coordinates given start point, azimuth, and distance.
    
    Uses the haversine formula to calculate the destination point given
    a starting point, bearing, and distance.
    
    Args:
        lat: Starting latitude in decimal degrees.
        lon: Starting longitude in decimal degrees.
        azimuth: Bearing in degrees (0=North, 90=East, 180=South, 270=West).
        distance_km: Distance in kilometers. Defaults to 50.
    
    Returns:
        A tuple containing:
            - end_lat: Ending latitude in decimal degrees
            - end_lon: Ending longitude in decimal degrees
    
    Example:
        >>> lat, lon = calculate_endpoint(40.0, -3.0, 90, 100)
        >>> print(f"End point: {lat}, {lon}")
    """
    pass
```

---

## 6. Performance Optimizations

### Priority: LOW

#### A. Cache API Responses
Add caching for repeated API calls:

```python
# src/cache.py
from functools import lru_cache
import json
import os

class FileCache:
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key: str):
        path = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None
    
    def set(self, key: str, value):
        path = os.path.join(self.cache_dir, f"{key}.json")
        with open(path, 'w') as f:
            json.dump(value, f)
```

#### B. Parallel Processing
Use concurrent requests for scraping:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def scrape_all_sites_parallel(codes: List[str], max_workers: int = 5):
    """Scrape multiple sites in parallel"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scrape_site, code, url): code 
            for code, url in generate_urls()
        }
        
        results = []
        for future in as_completed(futures):
            code = futures[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Failed to scrape {code}: {e}")
        
        return results
```

---

## 7. Documentation Improvements

### Priority: LOW

#### A. Add API Documentation
Create `docs/API.md` documenting all functions and modules.

#### B. Add Architecture Diagram
Create `docs/ARCHITECTURE.md` with system overview.

#### C. Add Contributing Guide
Create `CONTRIBUTING.md` with:
- Code style guidelines
- Testing requirements
- Pull request process

---

## Implementation Priority

1. **Phase 1 (High Priority)**:
   - Split app.js into modules
   - Add configuration module
   - Implement proper error handling

2. **Phase 2 (Medium Priority)**:
   - Add type hints
   - Create data models
   - Add unit tests
   - Implement logging

3. **Phase 3 (Low Priority)**:
   - Add caching
   - Parallel processing
   - Enhanced documentation

---

## Estimated Effort

- **Phase 1**: 8-12 hours
- **Phase 2**: 6-8 hours  
- **Phase 3**: 4-6 hours

**Total**: 18-26 hours of development time

---

## Benefits

1. **Maintainability**: Easier to locate and fix bugs
2. **Testability**: Isolated modules are easier to test
3. **Scalability**: Easier to add new features
4. **Collaboration**: Multiple developers can work on different modules
5. **Performance**: Caching and parallel processing improve speed
6. **Documentation**: Better onboarding for new contributors

---

*Generated: 2026-02-09*
*Made with Bob 🤖*