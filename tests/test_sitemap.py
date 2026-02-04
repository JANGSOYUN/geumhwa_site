#!/usr/bin/env python
"""
Sitemap and robots.txt test script for geumhwa_site.
Tests that sitemap.xml and robots.txt are properly generated.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geumhwa_site.settings')

import django
django.setup()

from django.test import Client


def test_robots_txt():
    """Test that robots.txt is accessible and correct."""
    print("=" * 60)
    print("[TEST 1] Robots.txt Test")
    print("=" * 60)

    client = Client()
    response = client.get('/robots.txt')

    print(f"  Status Code: {response.status_code}")
    print(f"  Content-Type: {response.get('Content-Type')}")

    if response.status_code == 200:
        content = response.content.decode('utf-8')
        print(f"  Content:\n{content}")

        # Check required elements
        checks = [
            ('User-agent' in content, "User-agent directive"),
            ('Sitemap' in content, "Sitemap directive"),
            ('sitemap.xml' in content, "Sitemap URL reference"),
        ]

        all_passed = True
        for check, name in checks:
            status = "OK" if check else "MISSING"
            print(f"    - {name}: {status}")
            if not check:
                all_passed = False

        if all_passed:
            print("[SUCCESS] Robots.txt is correct")
            return True
        else:
            print("[FAILED] Robots.txt is missing required elements")
            return False
    else:
        print(f"[FAILED] Unexpected status code: {response.status_code}")
        return False


def test_sitemap_xml():
    """Test that sitemap.xml is accessible and valid."""
    print("\n" + "=" * 60)
    print("[TEST 2] Sitemap.xml Test")
    print("=" * 60)

    client = Client()
    response = client.get('/sitemap.xml')

    print(f"  Status Code: {response.status_code}")
    print(f"  Content-Type: {response.get('Content-Type')}")

    if response.status_code == 200:
        content = response.content.decode('utf-8')

        # Check XML structure
        checks = [
            ('<?xml' in content, "XML declaration"),
            ('<urlset' in content, "urlset element"),
            ('<url>' in content, "url elements"),
            ('<loc>' in content, "loc elements"),
        ]

        all_passed = True
        for check, name in checks:
            status = "OK" if check else "MISSING"
            print(f"    - {name}: {status}")
            if not check:
                all_passed = False

        # Count URLs
        url_count = content.count('<url>')
        print(f"    - URL count: {url_count}")

        # Show URLs
        print("\n  URLs in sitemap:")
        import re
        urls = re.findall(r'<loc>(.*?)</loc>', content)
        for url in urls:
            print(f"    - {url}")

        if all_passed and url_count >= 1:
            print("\n[SUCCESS] Sitemap.xml is valid")
            return True
        else:
            print("\n[FAILED] Sitemap.xml is invalid or empty")
            return False
    else:
        print(f"[FAILED] Unexpected status code: {response.status_code}")
        return False


def test_sitemap_urls():
    """Test that all sitemap URLs are accessible."""
    print("\n" + "=" * 60)
    print("[TEST 3] Sitemap URLs Accessibility Test")
    print("=" * 60)

    client = Client()
    response = client.get('/sitemap.xml')

    if response.status_code != 200:
        print("[FAILED] Cannot fetch sitemap.xml")
        return False

    content = response.content.decode('utf-8')

    import re
    urls = re.findall(r'<loc>(.*?)</loc>', content)

    all_accessible = True
    for url in urls:
        # Extract path from URL
        path = url.replace('https://www.geumhwabox.com', '').replace('http://testserver', '')
        if not path:
            path = '/'

        try:
            resp = client.get(path)
            status = "OK" if resp.status_code == 200 else f"ERROR ({resp.status_code})"
            print(f"  {path}: {status}")
            if resp.status_code != 200:
                all_accessible = False
        except Exception as e:
            print(f"  {path}: ERROR ({str(e)})")
            all_accessible = False

    if all_accessible:
        print("\n[SUCCESS] All sitemap URLs are accessible")
        return True
    else:
        print("\n[FAILED] Some sitemap URLs are not accessible")
        return False


def main():
    """Run all sitemap tests."""
    print("\n" + "=" * 60)
    print("SITEMAP AND SEO TEST SUITE")
    print("=" * 60)

    results = {}

    results['Robots.txt'] = test_robots_txt()
    results['Sitemap.xml'] = test_sitemap_xml()
    results['URL Accessibility'] = test_sitemap_urls()

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
