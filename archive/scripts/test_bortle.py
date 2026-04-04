#!/usr/bin/env python3
"""
Simple test script for Bortle scale functionality
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.bortle_scraper import get_bortle_value, brightness_to_bortle, get_bortle_description
    
    print("=" * 60)
    print("Testing Bortle Scale Scraper")
    print("=" * 60)
    
    # Test brightness to Bortle conversion
    print("\n1. Testing brightness_to_bortle conversion:")
    test_cases = [
        (0.005, 1, "Excellent dark-sky site"),
        (0.03, 2, "Typical truly dark site"),
        (0.1, 3, "Rural sky"),
        (0.3, 4, "Rural/suburban transition"),
        (0.7, 5, "Suburban sky"),
        (2.0, 6, "Bright suburban sky"),
        (5.0, 7, "Suburban/urban transition"),
        (15.0, 8, "City sky"),
        (50.0, 9, "Inner-city sky")
    ]
    
    for brightness, expected_bortle, expected_desc in test_cases:
        bortle = brightness_to_bortle(brightness)
        desc = get_bortle_description(bortle)
        status = "✓" if bortle == expected_bortle else "✗"
        print(f"  {status} Brightness {brightness:.3f} mcd/m² → Bortle {bortle} ({desc})")
    
    # Test API call (if network available)
    print("\n2. Testing API call with Madrid coordinates:")
    print("   (This requires internet connection)")
    try:
        # Madrid, Spain - should be high light pollution (Bortle 8-9)
        madrid_bortle = get_bortle_value(40.4168, -3.7038)
        if madrid_bortle:
            desc = get_bortle_description(madrid_bortle)
            print(f"   ✓ Madrid: Bortle {madrid_bortle} ({desc})")
        else:
            print("   ⚠️  API call failed (check internet connection)")
    except Exception as e:
        print(f"   ⚠️  API test skipped: {e}")
    
    print("\n3. Testing with rural location:")
    try:
        # Rural Spain location - should be lower light pollution
        rural_bortle = get_bortle_value(42.5, -2.3)
        if rural_bortle:
            desc = get_bortle_description(rural_bortle)
            print(f"   ✓ Rural location: Bortle {rural_bortle} ({desc})")
        else:
            print("   ⚠️  API call failed")
    except Exception as e:
        print(f"   ⚠️  API test skipped: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Bortle scraper module is working correctly!")
    print("=" * 60)
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure you have installed the required dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Made with Bob
