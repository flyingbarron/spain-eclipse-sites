"""
Unit tests for Site data models
"""
import unittest
from src.models import Site, sites_to_dicts, dicts_to_sites


class TestSiteModel(unittest.TestCase):
    """Test cases for Site dataclass"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.site_data = {
            'code': 'IB200a',
            'denominacion': 'Test Site',
            'url': 'https://example.com',
            'valor_turistico': '5.5',
            'confidencialidad': 'Public',
            'route_difficulty': 'Low',
            'latitude': '42.5',
            'longitude': '-2.5',
            'eclipse_visibility': 'visible',
            'cloud_coverage': 25,
            'cloud_status': 'success',
            'cloud_url': 'https://example.com/cloud',
            'horizon_status': 'success',
            'status': 'success'
        }
        self.site = Site(**self.site_data)
    
    def test_site_creation(self):
        """Test Site object creation"""
        self.assertEqual(self.site.code, 'IB200a')
        self.assertEqual(self.site.denominacion, 'Test Site')
        self.assertEqual(self.site.valor_turistico, '5.5')
    
    def test_has_coordinates(self):
        """Test has_coordinates property"""
        self.assertTrue(self.site.has_coordinates)
        
        site_no_coords = Site(
            code='TEST',
            denominacion='Test',
            url='https://example.com',
            valor_turistico='5.0',
            confidencialidad='Public',
            route_difficulty='Low',
            latitude='N/A',
            longitude='N/A'
        )
        self.assertFalse(site_no_coords.has_coordinates)
    
    def test_lat_float(self):
        """Test lat_float property"""
        self.assertEqual(self.site.lat_float, 42.5)
        
        site_invalid = Site(
            code='TEST',
            denominacion='Test',
            url='https://example.com',
            valor_turistico='5.0',
            confidencialidad='Public',
            route_difficulty='Low',
            latitude='N/A',
            longitude='N/A'
        )
        self.assertIsNone(site_invalid.lat_float)
    
    def test_lon_float(self):
        """Test lon_float property"""
        self.assertEqual(self.site.lon_float, -2.5)
    
    def test_tourist_value_float(self):
        """Test tourist_value_float property"""
        self.assertEqual(self.site.tourist_value_float, 5.5)
    
    def test_tourist_value_category(self):
        """Test tourist_value_category property"""
        self.assertEqual(self.site.tourist_value_category, 'High')
        
        site_medium = Site(**{**self.site_data, 'valor_turistico': '4.5'})
        self.assertEqual(site_medium.tourist_value_category, 'Medium')
        
        site_lower = Site(**{**self.site_data, 'valor_turistico': '3.5'})
        self.assertEqual(site_lower.tourist_value_category, 'Lower')
    
    def test_is_eclipse_visible(self):
        """Test is_eclipse_visible property"""
        self.assertTrue(self.site.is_eclipse_visible)
        
        site_not_visible = Site(**{**self.site_data, 'eclipse_visibility': 'not_visible'})
        self.assertFalse(site_not_visible.is_eclipse_visible)
    
    def test_has_low_cloud_coverage(self):
        """Test has_low_cloud_coverage property"""
        self.assertTrue(self.site.has_low_cloud_coverage)
        
        site_high_cloud = Site(**{**self.site_data, 'cloud_coverage': 70})
        self.assertFalse(site_high_cloud.has_low_cloud_coverage)
    
    def test_cloud_emoji(self):
        """Test cloud_emoji property"""
        self.assertEqual(self.site.cloud_emoji, '☀️')
        
        site_medium = Site(**{**self.site_data, 'cloud_coverage': 45})
        self.assertEqual(site_medium.cloud_emoji, '⛅')
        
        site_high = Site(**{**self.site_data, 'cloud_coverage': 70})
        self.assertEqual(site_high.cloud_emoji, '☁️')
        
        site_unknown = Site(**{**self.site_data, 'cloud_coverage': None})
        self.assertEqual(site_unknown.cloud_emoji, '❓')
    
    def test_to_dict(self):
        """Test to_dict method"""
        site_dict = self.site.to_dict()
        self.assertEqual(site_dict['code'], 'IB200a')
        self.assertEqual(site_dict['denominacion'], 'Test Site')
        self.assertIsInstance(site_dict, dict)
    
    def test_from_dict(self):
        """Test from_dict class method"""
        site = Site.from_dict(self.site_data)
        self.assertEqual(site.code, 'IB200a')
        self.assertEqual(site.denominacion, 'Test Site')
    
    def test_str_representation(self):
        """Test __str__ method"""
        str_repr = str(self.site)
        self.assertIn('IB200a', str_repr)
        self.assertIn('Test Site', str_repr)
    
    def test_repr_representation(self):
        """Test __repr__ method"""
        repr_str = repr(self.site)
        self.assertIn('IB200a', repr_str)
        self.assertIn('Test Site', repr_str)
        self.assertIn('visible', repr_str)


class TestHelperFunctions(unittest.TestCase):
    """Test cases for helper functions"""
    
    def test_sites_to_dicts(self):
        """Test sites_to_dicts function"""
        sites = [
            Site(
                code='TEST1',
                denominacion='Test 1',
                url='https://example.com',
                valor_turistico='5.0',
                confidencialidad='Public',
                route_difficulty='Low'
            ),
            Site(
                code='TEST2',
                denominacion='Test 2',
                url='https://example.com',
                valor_turistico='4.0',
                confidencialidad='Public',
                route_difficulty='Medium'
            )
        ]
        
        dicts = sites_to_dicts(sites)
        self.assertEqual(len(dicts), 2)
        self.assertEqual(dicts[0]['code'], 'TEST1')
        self.assertEqual(dicts[1]['code'], 'TEST2')
    
    def test_dicts_to_sites(self):
        """Test dicts_to_sites function"""
        dicts = [
            {
                'code': 'TEST1',
                'denominacion': 'Test 1',
                'url': 'https://example.com',
                'valor_turistico': '5.0',
                'confidencialidad': 'Public',
                'route_difficulty': 'Low'
            },
            {
                'code': 'TEST2',
                'denominacion': 'Test 2',
                'url': 'https://example.com',
                'valor_turistico': '4.0',
                'confidencialidad': 'Public',
                'route_difficulty': 'Medium'
            }
        ]
        
        sites = dicts_to_sites(dicts)
        self.assertEqual(len(sites), 2)
        self.assertIsInstance(sites[0], Site)
        self.assertEqual(sites[0].code, 'TEST1')
        self.assertEqual(sites[1].code, 'TEST2')


if __name__ == '__main__':
    unittest.main()

# Made with Bob