"""
Unit tests for shared pipeline utility helpers.
"""

import csv
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

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


if __name__ == '__main__':
    unittest.main()

# Made with Bob