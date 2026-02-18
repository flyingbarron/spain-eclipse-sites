#!/usr/bin/env python3
"""
Standalone test for Bortle scale conversion logic (no dependencies)
"""

def brightness_to_bortle(brightness: float) -> int:
    """Convert artificial brightness (mcd/m²) to Bortle scale"""
    if brightness < 0.01:
        return 1
    elif brightness < 0.06:
        return 2
    elif brightness < 0.17:
        return 3
    elif brightness < 0.44:
        return 4
    elif brightness < 1.0:
        return 5
    elif brightness < 3.0:
        return 6
    elif brightness < 10.0:
        return 7
    elif brightness < 30.0:
        return 8
    else:
        return 9

def get_bortle_description(bortle: int) -> str:
    """Get human-readable description of Bortle scale value"""
    descriptions = {
        1: "Excellent dark-sky site",
        2: "Typical truly dark site",
        3: "Rural sky",
        4: "Rural/suburban transition",
        5: "Suburban sky",
        6: "Bright suburban sky",
        7: "Suburban/urban transition",
        8: "City sky",
        9: "Inner-city sky"
    }
    return descriptions.get(bortle, "Unknown")

print("=" * 60)
print("Testing Bortle Scale Conversion Logic")
print("=" * 60)

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

all_passed = True
for brightness, expected_bortle, expected_desc in test_cases:
    bortle = brightness_to_bortle(brightness)
    desc = get_bortle_description(bortle)
    passed = bortle == expected_bortle and desc == expected_desc
    status = "✓" if passed else "✗"
    all_passed = all_passed and passed
    print(f"{status} Brightness {brightness:.3f} mcd/m² → Bortle {bortle} ({desc})")

print("\n" + "=" * 60)
if all_passed:
    print("✓ All tests passed! Bortle conversion logic is correct.")
else:
    print("✗ Some tests failed!")
print("=" * 60)

print("\nNote: To test the full API integration, install dependencies:")
print("  pip install -r requirements.txt")
print("  python3 test_bortle.py")

# Made with Bob
