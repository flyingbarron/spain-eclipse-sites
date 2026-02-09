"""
Configuration loader with environment variable override support for containers
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


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
    
    def _apply_env_overrides(self) -> None:
        """Override config with environment variables (for K8s/OpenShift)
        
        Example: ECLIPSE_SITES_SERVER_PORT=9000 overrides server.port
        """
        prefix = "ECLIPSE_SITES_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert ECLIPSE_SITES_SERVER_PORT to ['server', 'port']
                config_path = key[len(prefix):].lower().split('_')
                self._set_nested(config_path, value)
    
    def _set_nested(self, path: list, value: str) -> None:
        """Set nested configuration value"""
        current = self._config
        for key in path[:-1]:
            current = current.setdefault(key, {})
        
        # Try to convert to appropriate type
        converted_value: Any = value
        try:
            if value.lower() in ('true', 'false'):
                converted_value = value.lower() == 'true'
            elif value.isdigit():
                converted_value = int(value)
            elif value.replace('.', '', 1).isdigit():
                converted_value = float(value)
        except:
            pass
        
        current[path[-1]] = converted_value
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation
        
        Args:
            path: Configuration path in dot notation (e.g., 'server.port')
            default: Default value if path not found
        
        Returns:
            Configuration value or default
        
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
        
        Args:
            path_key: Configuration path to directory (e.g., 'directories.data')
        
        Returns:
            Absolute Path object
        
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
ECLIPSE_DATE_ISO = config.get('eclipse.date_iso')
ECLIPSE_AZIMUTH = config.get('eclipse.azimuth')
AZIMUTH_LINE_DISTANCE_KM = config.get('eclipse.azimuth_line_distance_km')
REQUEST_TIMEOUT = config.get('scraping.request_timeout')
RATE_LIMIT_DELAY = config.get('scraping.rate_limit_delay')
CLOUD_SCRAPE_DELAY = config.get('scraping.cloud_scrape_delay')
HORIZON_SCRAPE_DELAY = config.get('scraping.horizon_scrape_delay')
USER_AGENT = config.get('scraping.user_agent')
DATA_DIR = str(config.get_path('directories.data'))
PROFILES_DIR = str(config.get_path('directories.profiles'))
HORIZON_DIR = str(config.get_path('directories.horizon'))
IGME_BASE_URL = config.get('urls.igme_base')
IGME_API_URL = config.get('urls.igme_api')
IGN_ECLIPSE_URL = config.get('urls.ign_eclipse')

# Made with Bob
