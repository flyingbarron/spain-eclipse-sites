"""
Unit tests for shared pipeline utility helpers.
"""

import csv
import json
import os
import re
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch


class _FakeTag:
    def __init__(self, attrs):
        self.attrs = attrs

    def get(self, name):
        return self.attrs.get(name)


class _FakeBeautifulSoup:
    def __init__(self, html, _parser):
        self.html = html

    def find_all(self, tag_name):
        if tag_name != 'img':
            return []

        matches = re.findall(r'<img\b([^>]*)>', self.html, flags=re.IGNORECASE)
        tags = []
        for raw_attrs in matches:
            attrs = dict(
                re.findall(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)=["\']([^"\']*)["\']', raw_attrs)
            )
            tags.append(_FakeTag(attrs))
        return tags


fake_bs4_module = types.ModuleType('bs4')
setattr(fake_bs4_module, 'BeautifulSoup', _FakeBeautifulSoup)
sys.modules.setdefault('bs4', fake_bs4_module)

from src.igme_image_service import (
    _normalize_igme_image_src,
    extract_igme_images,
    get_cached_igme_images,
    get_cached_proxy_image,
)
from src.pipeline_utils import (
    check_data_exists,
    count_statuses,
    load_sites_from_csv,
    merge_sites_by_code,
    merge_updated_site,
    process_sites_with_skip,
)


class TestPipelineUtils(unittest.TestCase):
    """Test cases for pipeline utility helpers."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.csv_filename = 'test_sites.csv'
        self.csv_path = os.path.join(self.temp_dir, self.csv_filename)

        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['code', 'cloud_coverage', 'darksky_sqm'])
            writer.writeheader()
            writer.writerow({'code': 'IB001', 'cloud_coverage': '25', 'darksky_sqm': '21.5'})
            writer.writerow({'code': 'IB002', 'cloud_coverage': '', 'darksky_sqm': ''})

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_load_sites_from_csv(self):
        with patch('src.pipeline_utils.resolve_data_csv_path', return_value=self.csv_path):
            sites = load_sites_from_csv(self.csv_filename)

        self.assertEqual(len(sites), 2)
        self.assertEqual(sites[0]['code'], 'IB001')
        self.assertEqual(sites[1]['code'], 'IB002')

    def test_check_data_exists_for_csv_backed_data(self):
        with patch('src.pipeline_utils.resolve_data_csv_path', return_value=self.csv_path):
            self.assertTrue(check_data_exists('IB001', 'cloud', self.csv_filename))
            self.assertTrue(check_data_exists('IB001', 'darksky', self.csv_filename))
            self.assertFalse(check_data_exists('IB002', 'cloud', self.csv_filename))
            self.assertFalse(check_data_exists('IB002', 'darksky', self.csv_filename))
            self.assertFalse(check_data_exists('IB999', 'cloud', self.csv_filename))

    def test_check_data_exists_for_file_backed_data(self):
        fake_output = os.path.join(self.temp_dir, 'IB001_profile.png')
        with open(fake_output, 'w', encoding='utf-8') as f:
            f.write('test')

        with patch('src.pipeline_utils.get_output_file_path', return_value=fake_output):
            self.assertTrue(check_data_exists('IB001', 'eclipse', self.csv_filename))

        os.remove(fake_output)

        with patch('src.pipeline_utils.get_output_file_path', return_value=fake_output):
            self.assertFalse(check_data_exists('IB001', 'eclipse', self.csv_filename))

    def test_merge_sites_by_code(self):
        base_sites = [
            {'code': 'IB001', 'status': 'old'},
            {'code': 'IB002', 'status': 'old'},
        ]
        updated_sites = [
            {'code': 'IB002', 'status': 'new'},
        ]

        merged = merge_sites_by_code(base_sites, updated_sites)

        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0]['status'], 'old')
        self.assertEqual(merged[1]['status'], 'new')

    def test_merge_sites_by_code_ignores_unknown_updates(self):
        base_sites = [
            {'code': 'IB001', 'status': 'old'},
        ]
        updated_sites = [
            {'code': 'IB999', 'status': 'new'},
        ]

        merged = merge_sites_by_code(base_sites, updated_sites)

        self.assertEqual(merged, base_sites)

    def test_merge_updated_site(self):
        base_sites = [
            {'code': 'IB001', 'status': 'old'},
            {'code': 'IB002', 'status': 'old'},
        ]

        merged = merge_updated_site(base_sites, {'code': 'IB001', 'status': 'updated'})

        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0]['status'], 'updated')
        self.assertEqual(merged[1]['status'], 'old')

    def test_count_statuses(self):
        sites = [
            {'cloud_status': 'success'},
            {'cloud_status': 'success'},
            {'cloud_status': 'error'},
            {},
        ]

        counts = count_statuses(sites, 'cloud_status')

        self.assertEqual(counts['success'], 2)
        self.assertEqual(counts['error'], 1)
        self.assertEqual(counts['unknown'], 1)

    def test_process_sites_with_skip(self):
        sites = [
            {'code': 'IB001', 'cloud_status': 'not_checked'},
            {'code': 'IB002', 'cloud_status': 'not_checked'},
        ]

        def processor(sites_to_process):
            return [
                {**site, 'cloud_status': 'success'}
                for site in sites_to_process
            ]

        result = process_sites_with_skip(
            sites,
            'cloud',
            processor,
            skip_message='Skipping {code}',
            skipped_status_field='cloud_status',
            data_exists_checker=lambda code, kind: code == 'IB001',
        )

        self.assertEqual(result[0]['cloud_status'], 'skipped_existing')
        self.assertEqual(result[1]['cloud_status'], 'success')

    def test_process_sites_with_skip_logs_summary(self):
        sites = [{'code': 'IB001'}]

        captured = StringIO()
        with redirect_stdout(captured):
            process_sites_with_skip(
                sites,
                'cloud',
                lambda rows: rows,
                skip_message='Skipping {code}',
                data_exists_checker=lambda code, kind: True,
            )

        output = captured.getvalue()
        self.assertIn('Skipping IB001', output)
        self.assertIn('Skipped 1 sites with existing cloud data', output)


class TestIgmeImageService(unittest.TestCase):
    """Test cases for IGME image extraction and caching helpers."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.html_cache_dir = os.path.join(self.temp_dir, 'html')
        self.image_cache_dir = os.path.join(self.temp_dir, 'images')

    def tearDown(self):
        for root, _, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            os.rmdir(root)

    def test_normalize_igme_image_src(self):
        self.assertEqual(
            _normalize_igme_image_src('/files/photo.jpg'),
            'https://info.igme.es/files/photo.jpg',
        )
        self.assertEqual(
            _normalize_igme_image_src('uploads/photo.jpg'),
            'https://info.igme.es/ielig/uploads/photo.jpg',
        )
        self.assertEqual(
            _normalize_igme_image_src('https://cdn.example.com/photo.jpg'),
            'https://cdn.example.com/photo.jpg',
        )

    def test_extract_igme_images_filters_non_site_images(self):
        html = """
        <html><body>
            <img src="/icons/logo.png" alt="Logo">
            <img src="/ielig/fotos/site-1.jpg" alt="Main view">
            <img src="uploads/site-2.png">
            <img src="/banner/header.jpg" alt="Header">
            <img src="https://example.com/photo.jpg" alt="External">
        </body></html>
        """

        images = extract_igme_images(html)

        self.assertEqual(
            images,
            [
                {'src': 'https://info.igme.es/ielig/fotos/site-1.jpg', 'alt': 'Main view'},
                {'src': 'https://info.igme.es/ielig/uploads/site-2.png', 'alt': 'Site image'},
            ],
        )

    def test_get_cached_igme_images_prefers_json_cache(self):
        url = 'https://info.igme.es/example'
        cached_json = json.dumps({'images': [{'src': 'cached', 'alt': 'Cached'}]})

        with patch('src.igme_image_service.IGME_HTML_CACHE_DIR', self.html_cache_dir):
            os.makedirs(self.html_cache_dir, exist_ok=True)
            url_hash = __import__('src.igme_image_service', fromlist=['_url_hash'])._url_hash(url)
            with open(
                os.path.join(self.html_cache_dir, f'{url_hash}.json'),
                'w',
                encoding='utf-8',
            ) as file:
                file.write(cached_json)

            with patch('src.igme_image_service._fetch_url_text') as mock_fetch:
                result = get_cached_igme_images(url)

        self.assertEqual(result, cached_json)
        mock_fetch.assert_not_called()

    def test_get_cached_igme_images_builds_cache_from_html(self):
        url = 'https://info.igme.es/example'
        html = '<img src="/ielig/fotos/site.jpg" alt="View">'

        with patch('src.igme_image_service.IGME_HTML_CACHE_DIR', self.html_cache_dir):
            with patch('src.igme_image_service._fetch_url_text', return_value=html) as mock_fetch:
                result = get_cached_igme_images(url)

        payload = json.loads(result)
        self.assertEqual(
            payload,
            {'images': [{'src': 'https://info.igme.es/ielig/fotos/site.jpg', 'alt': 'View'}]},
        )
        mock_fetch.assert_called_once_with(url)

    def test_get_cached_proxy_image_uses_cached_file_type(self):
        image_url = 'https://info.igme.es/images/photo.png'

        with patch('src.igme_image_service.IGME_IMAGE_CACHE_DIR', self.image_cache_dir):
            os.makedirs(self.image_cache_dir, exist_ok=True)
            url_hash = __import__('src.igme_image_service', fromlist=['_url_hash'])._url_hash(image_url)
            cache_file = os.path.join(self.image_cache_dir, f'{url_hash}.png')
            with open(cache_file, 'wb') as file:
                file.write(b'cached-image')

            with patch('src.igme_image_service._fetch_url_bytes') as mock_fetch:
                result = get_cached_proxy_image(image_url)

        self.assertEqual(result['content_type'], 'image/png')
        self.assertEqual(result['image_data'], b'cached-image')
        mock_fetch.assert_not_called()

    def test_get_cached_proxy_image_downloads_and_defaults_extension(self):
        image_url = 'https://info.igme.es/images/photo.bmp'

        with patch('src.igme_image_service.IGME_IMAGE_CACHE_DIR', self.image_cache_dir):
            with patch(
                'src.igme_image_service._fetch_url_bytes',
                return_value=(b'downloaded-image', 'image/bmp'),
            ) as mock_fetch:
                result = get_cached_proxy_image(image_url)

        self.assertEqual(result['content_type'], 'image/bmp')
        self.assertEqual(result['image_data'], b'downloaded-image')
        mock_fetch.assert_called_once_with(image_url)


if __name__ == '__main__':
    unittest.main()

# Made with Bob