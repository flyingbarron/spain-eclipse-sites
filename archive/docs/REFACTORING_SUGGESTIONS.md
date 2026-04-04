# Code Refactoring Suggestions

## Overview
This document outlines suggestions to improve code maintainability, readability, and organization for the Spain Eclipse Sites project.

## Recent Progress (Updated 2026-02-09)

### ✅ Completed Improvements
1. **Modular Python Structure** - Code has been successfully split into focused modules:
   - `src/igme_scraper.py` - IGME site scraping
   - `src/eclipse_checker.py` - Eclipse visibility checking
   - `src/cloud_coverage_scraper.py` - Cloud coverage data scraping
   - `src/eclipsefan_scraper.py` - EclipseFan horizon image downloading
   - `src/output_generator.py` - CSV and KML file generation
   - `generate_eclipse_site_data.py` - Main orchestration script

2. **Docstrings Added** - All modules now have proper docstrings explaining their purpose

3. **Function Documentation** - Key functions include docstrings with Args and Returns sections

4. **Separation of Concerns** - Each module has a single, well-defined responsibility

5. **Utility Scripts Organized** - Test and utility scripts moved to `tests/` directory

### 🔄 Partially Implemented
1. **Type Hints** - Some functions have type hints in docstrings, but not using Python type annotations
2. **Error Handling** - Basic try/catch blocks exist, but no custom exception classes
3. **Configuration** - Constants are defined in modules, but no centralized config system

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

### Priority: MEDIUM → LOW (Mostly Complete)

**Status Update**: The Python backend has been successfully refactored into a modular structure. The main remaining items are optional enhancements.

### ✅ Already Implemented:
- Modular file structure with separate concerns
- Clear function documentation with docstrings
- Organized directory structure (`src/`, `tests/`, `data/`)
- Main orchestration script with command-line arguments
- Progress tracking and error handling

### 🔄 Remaining Recommendations:

#### A. Create Configuration System with YAML (Container-Ready)
**File**: `config.yaml` (for Kubernetes/OpenShift deployment)

```yaml
# Application Configuration
app:
  name: "Spain Eclipse Sites"
  version: "1.0.0"
  environment: "production"  # development, staging, production

# Directories (relative to project root)
directories:
  data: "data"
  profiles: "data/eclipse_profiles"
  shademap: "data/shademap"
  cache: ".cache"
  logs: "logs"

# Eclipse Configuration
eclipse:
  date: "2026-08-12"
  date_iso: "20260812"
  azimuth: 283.7753
  azimuth_line_distance_km: 50

# Scraping Settings
scraping:
  request_timeout: 10
  rate_limit_delay: 1.0
  cloud_scrape_delay: 2.0
  max_retries: 3
  retry_delay: 2.0
  parallel_workers: 5
  user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# External URLs
urls:
  igme_base: "https://info.igme.es/ielig/LIGInfo.aspx?codigo="
  igme_api: "https://mapas.igme.es/gis/rest/services/BasesDatos/IGME_IELIG/MapServer/0/query"
  ign_eclipse: "https://visualizadores.ign.es/eclipses/2026"
  timeanddate: "https://www.timeanddate.com/eclipse/in/@{lat},{lon}?iso={date}"

# Logging Configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/app.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5

# Web Server Settings
server:
  host: "0.0.0.0"  # Bind to all interfaces for containers
  port: 8000
  debug: false

# Feature Flags
features:
  enable_caching: true
  enable_parallel_scraping: false
  enable_cloud_coverage: true
  enable_eclipse_checking: true
```

**File**: `src/config.py` (Configuration loader with env var support)

```python
"""
Configuration loader with environment variable override support for containers
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict

class Config:
    """Configuration manager with YAML file and environment variable support"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = self._load_config()
        self._apply_env_overrides()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _apply_env_overrides(self):
        """Override config with environment variables (for K8s/OpenShift)"""
        # Example: ECLIPSE_SITES_SERVER_PORT=9000 overrides server.port
        prefix = "ECLIPSE_SITES_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert ECLIPSE_SITES_SERVER_PORT to ['server', 'port']
                config_path = key[len(prefix):].lower().split('_')
                self._set_nested(config_path, value)
    
    def _set_nested(self, path: list, value: str):
        """Set nested configuration value"""
        current = self._config
        for key in path[:-1]:
            current = current.setdefault(key, {})
        
        # Try to convert to appropriate type
        try:
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
        except:
            pass
        
        current[path[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation
        
        Example:
            config.get('server.port')  # Returns 8000
            config.get('scraping.request_timeout')  # Returns 10
        """
        keys = path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    @property
    def base_dir(self) -> Path:
        """Get base directory path"""
        return Path(__file__).parent.parent
    
    def get_path(self, path_key: str) -> Path:
        """Get absolute path for a directory configuration
        
        Example:
            config.get_path('directories.data')  # Returns /app/data
        """
        relative_path = self.get(path_key)
        if relative_path:
            return self.base_dir / relative_path
        return self.base_dir

# Global config instance
config = Config()

# Convenience accessors for backward compatibility
ECLIPSE_DATE = config.get('eclipse.date')
ECLIPSE_AZIMUTH = config.get('eclipse.azimuth')
REQUEST_TIMEOUT = config.get('scraping.request_timeout')
DATA_DIR = str(config.get_path('directories.data'))
PROFILES_DIR = str(config.get_path('directories.profiles'))
```

**File**: `config.dev.yaml` (Development overrides)

```yaml
# Development Configuration Overrides
app:
  environment: "development"

server:
  debug: true

logging:
  level: "DEBUG"

scraping:
  rate_limit_delay: 0.5  # Faster for development
  parallel_workers: 2

features:
  enable_caching: false  # Disable cache in dev
```

**File**: `.env.example` (Environment variables for containers)

```bash
# Environment Variables for Container Deployment
# Copy to .env and customize for your environment

# Server Configuration
ECLIPSE_SITES_SERVER_HOST=0.0.0.0
ECLIPSE_SITES_SERVER_PORT=8000

# Logging
ECLIPSE_SITES_LOGGING_LEVEL=INFO

# Scraping Settings
ECLIPSE_SITES_SCRAPING_REQUEST_TIMEOUT=10
ECLIPSE_SITES_SCRAPING_RATE_LIMIT_DELAY=1.0

# Feature Flags
ECLIPSE_SITES_FEATURES_ENABLE_CACHING=true
ECLIPSE_SITES_FEATURES_ENABLE_PARALLEL_SCRAPING=false
```

**Usage in code:**

```python
from src.config import config

# Access configuration
timeout = config.get('scraping.request_timeout')
data_dir = config.get_path('directories.data')

# Or use convenience constants
from src.config import ECLIPSE_DATE, DATA_DIR
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

### Priority: LOW-MEDIUM → LOW (Partially Complete)

**Status Update**: Basic code quality standards are in place. Remaining items are enhancements.

### ✅ Already Implemented:
- Consistent docstrings across modules
- Clear function documentation with Args/Returns
- Organized code structure
- Print statements for user feedback

### 🔄 Remaining Recommendations:

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

#### B. Respectful Scraping Practices

**IMPORTANT**: Always be respectful to the servers we're scraping. Avoid parallel processing for external sites.

```python
# src/scraper_utils.py
import time
from functools import wraps

class RateLimiter:
    """Rate limiter to ensure respectful scraping"""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = {}
    
    def wait(self, domain: str):
        """Wait appropriate time before next request to domain"""
        now = time.time()
        last_time = self.last_request_time.get(domain, 0)
        elapsed = now - last_time
        
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time[domain] = time.time()

# Global rate limiter
rate_limiter = RateLimiter(min_delay=1.5, max_delay=3.0)

def respectful_scrape(func):
    """Decorator to ensure respectful scraping with rate limiting"""
    @wraps(func)
    def wrapper(url, *args, **kwargs):
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        # Wait before making request
        rate_limiter.wait(domain)
        
        # Add random jitter to appear more human-like
        import random
        time.sleep(random.uniform(0.1, 0.5))
        
        return func(url, *args, **kwargs)
    return wrapper

@respectful_scrape
def fetch_page(url):
    """Fetch page with respectful rate limiting"""
    response = requests.get(url, timeout=10)
    return response

# Usage in scraper:
def scrape_all_sites(specific_code=None):
    """Scrape sites sequentially with respectful delays"""
    urls = generate_urls(specific_code)
    results = []
    
    for code, url in urls:
        logger.info(f"Scraping {code}...")
        site_data = scrape_site(code, url)  # Uses @respectful_scrape
        if site_data:
            results.append(site_data)
        
        # Additional delay between sites (configurable)
        time.sleep(config.get('scraping.rate_limit_delay', 1.5))
    
    return results
```

**Best Practices for Respectful Scraping:**

1. **Sequential Processing**: Scrape one site at a time, never in parallel
2. **Rate Limiting**: Minimum 1-2 seconds between requests to same domain
3. **Random Jitter**: Add 0.1-0.5s random delay to appear human-like
4. **Respect robots.txt**: Check and honor robots.txt rules
5. **User-Agent**: Use descriptive User-Agent identifying your project
6. **Retry Logic**: Use exponential backoff, not aggressive retries
7. **Off-Peak Hours**: Consider running during off-peak hours
8. **Cache Results**: Cache responses to avoid re-scraping

**Configuration for Respectful Scraping:**

```yaml
# config.yaml
scraping:
  # Conservative defaults - be respectful!
  request_timeout: 10
  rate_limit_delay: 1.5      # Minimum delay between requests
  max_delay_jitter: 0.5      # Random jitter (0-0.5s)
  max_retries: 2             # Limited retries
  retry_delay: 5.0           # Long delay before retry
  parallel_workers: 1        # ALWAYS 1 for external scraping
  respect_robots_txt: true
  user_agent: "Spain Eclipse Sites Scraper (Educational/Non-commercial; contact@example.com)"
```

**Note**: Parallel processing should ONLY be used for:
- Internal data processing (not scraping)
- APIs with explicit rate limit allowances
- Your own infrastructure

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

## Implementation Priority (Updated)

### ✅ Phase 1 (Completed):
   - ✅ Split Python backend into modules
   - ✅ Organized code structure
   - ✅ Basic error handling implemented

### 🔄 Phase 2 (Remaining - Optional):
   - ⚠️ Split app.js into modules (HIGH priority for frontend)
   - ⚠️ Add centralized configuration system (YAML)
   - ⚠️ Add Python type hints
   - ⚠️ Create data models (dataclasses)
   - ⚠️ Add unit tests
   - ⚠️ Replace print with logging

### 📋 Phase 3 (Future Enhancements):
   - Add caching for API responses
   - Parallel processing for scraping
   - Enhanced documentation
   - Containerization (Docker/Kubernetes)

---

## Estimated Effort (Updated)

- **Phase 1**: ✅ COMPLETED (Python backend refactoring)
- **Phase 2**: 10-14 hours remaining
  - Frontend modularization: 6-8 hours
  - Configuration system: 2-3 hours
  - Type hints & models: 2-3 hours
- **Phase 3**: 4-6 hours (future enhancements)

**Remaining Total**: 14-20 hours of development time

---

## Benefits

1. **Maintainability**: Easier to locate and fix bugs
2. **Testability**: Isolated modules are easier to test
3. **Scalability**: Easier to add new features
4. **Collaboration**: Multiple developers can work on different modules
5. **Performance**: Caching and parallel processing improve speed
6. **Documentation**: Better onboarding for new contributors

---
## 8. Containerization & Deployment

### Priority: MEDIUM (for production deployment)

#### A. Docker Configuration
**File**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/eclipse_profiles data/shademap logs

# Expose port
EXPOSE 8000

# Set environment variables
ENV ECLIPSE_SITES_SERVER_HOST=0.0.0.0
ENV ECLIPSE_SITES_SERVER_PORT=8000

# Run the application
CMD ["python", "serve_viewer.py"]
```

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  eclipse-sites:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config.yaml:/app/config.yaml
      - ./logs:/app/logs
    environment:
      - ECLIPSE_SITES_LOGGING_LEVEL=INFO
      - ECLIPSE_SITES_SERVER_HOST=0.0.0.0
    restart: unless-stopped
```

#### B. Kubernetes Deployment
**File**: `k8s/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eclipse-sites
  labels:
    app: eclipse-sites
spec:
  replicas: 2
  selector:
    matchLabels:
      app: eclipse-sites
  template:
    metadata:
      labels:
        app: eclipse-sites
    spec:
      containers:
      - name: eclipse-sites
        image: your-registry/eclipse-sites:latest
        ports:
        - containerPort: 8000
        env:
        - name: ECLIPSE_SITES_SERVER_HOST
          value: "0.0.0.0"
        - name: ECLIPSE_SITES_SERVER_PORT
          value: "8000"
        - name: ECLIPSE_SITES_LOGGING_LEVEL
          valueFrom:
            configMapKeyRef:
              name: eclipse-sites-config
              key: log-level
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: config
          mountPath: /app/config.yaml
          subPath: config.yaml
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: eclipse-sites-data
      - name: config
        configMap:
          name: eclipse-sites-config
```

**File**: `k8s/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: eclipse-sites
spec:
  selector:
    app: eclipse-sites
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**File**: `k8s/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: eclipse-sites-config
data:
  log-level: "INFO"
  config.yaml: |
    app:
      name: "Spain Eclipse Sites"
      version: "1.0.0"
      environment: "production"
    
    directories:
      data: "data"
      profiles: "data/eclipse_profiles"
      shademap: "data/shademap"
      logs: "logs"
    
    eclipse:
      date: "2026-08-12"
      date_iso: "20260812"
      azimuth: 283.7753
      azimuth_line_distance_km: 50
    
    scraping:
      request_timeout: 10
      rate_limit_delay: 1.0
      cloud_scrape_delay: 2.0
    
    server:
      host: "0.0.0.0"
      port: 8000
      debug: false
    
    logging:
      level: "INFO"
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**File**: `k8s/pvc.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: eclipse-sites-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

#### C. OpenShift Configuration
**File**: `openshift/deployment.yaml`

```yaml
apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: eclipse-sites
spec:
  replicas: 2
  selector:
    app: eclipse-sites
  template:
    metadata:
      labels:
        app: eclipse-sites
    spec:
      containers:
      - name: eclipse-sites
        image: eclipse-sites:latest
        ports:
        - containerPort: 8000
        env:
        - name: ECLIPSE_SITES_SERVER_HOST
          value: "0.0.0.0"
        - name: ECLIPSE_SITES_SERVER_PORT
          value: "8000"
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: config
          mountPath: /app/config.yaml
          subPath: config.yaml
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: eclipse-sites-data
      - name: config
        configMap:
          name: eclipse-sites-config
  triggers:
  - type: ConfigChange
  - type: ImageChange
    imageChangeParams:
      automatic: true
      containerNames:
      - eclipse-sites
      from:
        kind: ImageStreamTag
        name: eclipse-sites:latest
```

**File**: `openshift/route.yaml`

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: eclipse-sites
spec:
  to:
    kind: Service
    name: eclipse-sites
  port:
    targetPort: 8000
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

#### D. Deployment Commands

```bash
# Docker
docker build -t eclipse-sites:latest .
docker run -p 8000:8000 -v $(pwd)/data:/app/data eclipse-sites:latest

# Docker Compose
docker-compose up -d

# Kubernetes
kubectl apply -f k8s/

# OpenShift
oc apply -f openshift/
oc new-app . --name=eclipse-sites
oc expose svc/eclipse-sites
```

---


*Generated: 2026-02-09*
*Made with Bob 🤖*