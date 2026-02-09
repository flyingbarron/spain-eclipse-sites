"""
Unit tests for configuration module
"""
import unittest
import os
import tempfile
from pathlib import Path
from src.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.yaml')
        
        config_content = """
app:
  name: "Test App"
  version: "1.0.0"

directories:
  data: "test_data"
  logs: "test_logs"

eclipse:
  date: "2026-08-12"
  azimuth: 283.7753

scraping:
  request_timeout: 10
  rate_limit_delay: 1.0

server:
  host: "localhost"
  port: 8000
  debug: true

features:
  enable_caching: false
"""
        with open(self.config_file, 'w') as f:
            f.write(config_content)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_config_loading(self):
        """Test configuration file loading"""
        config = Config(self.config_file)
        self.assertIsNotNone(config._config)
        self.assertIsInstance(config._config, dict)
    
    def test_get_simple_value(self):
        """Test getting simple configuration values"""
        config = Config(self.config_file)
        self.assertEqual(config.get('app.name'), 'Test App')
        self.assertEqual(config.get('app.version'), '1.0.0')
    
    def test_get_nested_value(self):
        """Test getting nested configuration values"""
        config = Config(self.config_file)
        self.assertEqual(config.get('eclipse.date'), '2026-08-12')
        self.assertEqual(config.get('eclipse.azimuth'), 283.7753)
    
    def test_get_with_default(self):
        """Test getting values with default"""
        config = Config(self.config_file)
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
        self.assertIsNone(config.get('nonexistent.key'))
    
    def test_get_boolean(self):
        """Test getting boolean values"""
        config = Config(self.config_file)
        self.assertTrue(config.get('server.debug'))
        self.assertFalse(config.get('features.enable_caching'))
    
    def test_get_number(self):
        """Test getting numeric values"""
        config = Config(self.config_file)
        self.assertEqual(config.get('scraping.request_timeout'), 10)
        self.assertEqual(config.get('scraping.rate_limit_delay'), 1.0)
        self.assertEqual(config.get('server.port'), 8000)
    
    def test_base_dir(self):
        """Test base_dir property"""
        config = Config(self.config_file)
        self.assertIsInstance(config.base_dir, Path)
        self.assertTrue(config.base_dir.exists())
    
    def test_get_path(self):
        """Test get_path method"""
        config = Config(self.config_file)
        data_path = config.get_path('directories.data')
        self.assertIsInstance(data_path, Path)
        self.assertTrue(str(data_path).endswith('test_data'))
    
    def test_env_override_string(self):
        """Test environment variable override for strings"""
        os.environ['ECLIPSE_SITES_APP_NAME'] = 'Overridden App'
        config = Config(self.config_file)
        self.assertEqual(config.get('app.name'), 'Overridden App')
        del os.environ['ECLIPSE_SITES_APP_NAME']
    
    def test_env_override_int(self):
        """Test environment variable override for integers"""
        os.environ['ECLIPSE_SITES_SERVER_PORT'] = '9000'
        config = Config(self.config_file)
        self.assertEqual(config.get('server.port'), 9000)
        del os.environ['ECLIPSE_SITES_SERVER_PORT']
    
    def test_env_override_float(self):
        """Test environment variable override for floats"""
        os.environ['ECLIPSE_SITES_SCRAPING_RATE_LIMIT_DELAY'] = '2.5'
        config = Config(self.config_file)
        self.assertEqual(config.get('scraping.rate_limit_delay'), 2.5)
        del os.environ['ECLIPSE_SITES_SCRAPING_RATE_LIMIT_DELAY']
    
    def test_env_override_bool(self):
        """Test environment variable override for booleans"""
        os.environ['ECLIPSE_SITES_FEATURES_ENABLE_CACHING'] = 'true'
        config = Config(self.config_file)
        self.assertTrue(config.get('features.enable_caching'))
        del os.environ['ECLIPSE_SITES_FEATURES_ENABLE_CACHING']
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file"""
        with self.assertRaises(FileNotFoundError):
            Config('nonexistent_config.yaml')


if __name__ == '__main__':
    unittest.main()

# Made with Bob