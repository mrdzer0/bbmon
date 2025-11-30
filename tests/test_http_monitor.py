#!/usr/bin/env python3
"""
Unit tests for modules/http_monitor.py - HTTP monitoring functionality
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.http_monitor import HTTPMonitor


class TestHTTPMonitor(unittest.TestCase):
    """Test cases for HTTPMonitor class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.monitor = HTTPMonitor(output_dir=self.test_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test HTTPMonitor initialization"""
        self.assertIsNotNone(self.monitor.output_dir)
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.monitor.high_value_keywords, dict)
        self.assertIsInstance(self.monitor.outdated_tech, dict)

    @patch('modules.http_monitor.requests.Session.get')
    def test_probe_url_success(self, mock_get):
        """Test successful URL probing"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><head><title>Test Page</title></head><body>Content</body></html>'
        mock_response.headers = {
            'Server': 'Apache/2.4.41',
            'Content-Type': 'text/html'
        }
        mock_response.history = []
        mock_get.return_value = mock_response

        result = self.monitor.probe_url('https://example.com')

        self.assertTrue(result['reachable'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['title'], 'Test Page')
        self.assertGreater(result['body_length'], 0)
        self.assertEqual(result['server'], 'Apache/2.4.41')

    @patch('modules.http_monitor.requests.Session.get')
    def test_probe_url_timeout(self, mock_get):
        """Test URL probing with timeout"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        result = self.monitor.probe_url('https://example.com')

        self.assertFalse(result['reachable'])
        self.assertTrue(any('Timeout' in str(f) for f in result['flags']))

    @patch('modules.http_monitor.requests.Session.get')
    def test_probe_url_connection_error(self, mock_get):
        """Test URL probing with connection error"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = self.monitor.probe_url('https://example.com')

        self.assertFalse(result['reachable'])
        self.assertTrue(any('Connection Error' in str(f) for f in result['flags']))

    @patch('modules.http_monitor.requests.Session.get')
    def test_detect_technologies_wordpress(self, mock_get):
        """Test WordPress detection"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body>wp-content wp-includes</body></html>'
        mock_response.text = 'wp-content wp-includes'
        mock_response.headers = {}

        technologies = self.monitor.detect_technologies(mock_response)

        self.assertTrue(any('WordPress' in tech for tech in technologies))

    @patch('modules.http_monitor.requests.Session.get')
    def test_detect_technologies_jquery(self, mock_get):
        """Test jQuery detection"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'jquery-3.6.0.min.js'
        mock_response.text = 'jquery-3.6.0.min.js'
        mock_response.headers = {}

        technologies = self.monitor.detect_technologies(mock_response)

        self.assertTrue(any('jQuery' in tech for tech in technologies))

    def test_flag_admin_panel(self):
        """Test flagging admin panels"""
        result = {
            'status_code': 200,
            'title': 'Admin Dashboard',
            'technologies': [],
            'flags': [],
            'headers': {}
        }

        flags = self.monitor.flag_target('https://example.com/admin', result)

        # Should flag as admin panel
        admin_flags = [f for f in flags if f['type'] == 'high_value' and f['category'] == 'admin']
        self.assertGreater(len(admin_flags), 0)
        self.assertEqual(admin_flags[0]['severity'], 'high')

    def test_flag_upload_endpoint(self):
        """Test flagging upload endpoints"""
        result = {
            'status_code': 200,
            'title': 'File Upload',
            'technologies': [],
            'flags': [],
            'headers': {}
        }

        flags = self.monitor.flag_target('https://example.com/upload', result)

        # Should flag as upload endpoint
        upload_flags = [f for f in flags if f.get('category') == 'upload']
        self.assertGreater(len(upload_flags), 0)

    def test_flag_backup_file(self):
        """Test flagging backup files"""
        result = {
            'status_code': 200,
            'title': '',
            'technologies': [],
            'flags': [],
            'headers': {}
        }

        flags = self.monitor.flag_target('https://example.com/backup.sql', result)

        # Should flag as backup
        backup_flags = [f for f in flags if f.get('category') == 'backup']
        self.assertGreater(len(backup_flags), 0)

    def test_flag_outdated_technology(self):
        """Test flagging outdated technology"""
        result = {
            'status_code': 200,
            'title': 'Test',
            'technologies': ['Apache 2.4.49', 'PHP 5.6'],
            'flags': [],
            'headers': {}
        }

        flags = self.monitor.flag_target('https://example.com', result)

        # Should flag outdated technologies
        tech_flags = [f for f in flags if f['type'] == 'outdated_tech']
        self.assertGreater(len(tech_flags), 0)

    def test_flag_interesting_status_codes(self):
        """Test flagging interesting status codes"""
        result = {
            'status_code': 403,
            'title': 'Forbidden',
            'technologies': [],
            'flags': [],
            'headers': {}
        }

        flags = self.monitor.flag_target('https://example.com', result)

        # Should flag 403 status
        status_flags = [f for f in flags if f['type'] == 'status']
        self.assertGreater(len(status_flags), 0)

    def test_flag_missing_security_headers(self):
        """Test flagging missing security headers"""
        result = {
            'status_code': 200,
            'title': 'Test',
            'technologies': [],
            'flags': [],
            'headers': {}  # No security headers
        }

        flags = self.monitor.flag_target('https://example.com', result)

        # Should flag missing security headers
        security_flags = [f for f in flags if f['type'] == 'security']
        self.assertGreater(len(security_flags), 0)

    def test_compare_results_status_change(self):
        """Test comparing results with status code change"""
        old = {
            'url': 'https://example.com',
            'timestamp': '2025-01-30T10:00:00',
            'status_code': 403,
            'title': 'Forbidden',
            'body_length': 1000,
            'technologies': [],
            'flags': []
        }

        new = {
            'url': 'https://example.com',
            'timestamp': '2025-01-30T11:00:00',
            'status_code': 200,
            'title': 'Welcome',
            'body_length': 5000,
            'technologies': [],
            'flags': []
        }

        changes = self.monitor.compare_results(old, new)

        self.assertTrue(changes['has_changes'])
        self.assertTrue(any(c['type'] == 'status_code' for c in changes['changes']))

    def test_compare_results_title_change(self):
        """Test comparing results with title change"""
        old = {
            'url': 'https://example.com',
            'timestamp': '2025-01-30T10:00:00',
            'status_code': 200,
            'title': 'Old Title',
            'body_length': 1000,
            'technologies': [],
            'flags': []
        }

        new = {
            'url': 'https://example.com',
            'timestamp': '2025-01-30T11:00:00',
            'status_code': 200,
            'title': 'New Title',
            'body_length': 1000,
            'technologies': [],
            'flags': []
        }

        changes = self.monitor.compare_results(old, new)

        self.assertTrue(changes['has_changes'])
        self.assertTrue(any(c['type'] == 'title' for c in changes['changes']))

    def test_compare_results_technology_change(self):
        """Test comparing results with technology change"""
        old = {
            'url': 'https://example.com',
            'timestamp': '2025-01-30T10:00:00',
            'status_code': 200,
            'title': 'Test',
            'body_length': 1000,
            'technologies': ['Apache'],
            'flags': []
        }

        new = {
            'url': 'https://example.com',
            'timestamp': '2025-01-30T11:00:00',
            'status_code': 200,
            'title': 'Test',
            'body_length': 1000,
            'technologies': ['Apache', 'PHP'],
            'flags': []
        }

        changes = self.monitor.compare_results(old, new)

        self.assertTrue(changes['has_changes'])
        tech_changes = [c for c in changes['changes'] if c['type'] == 'technology_added']
        self.assertGreater(len(tech_changes), 0)
        self.assertIn('PHP', tech_changes[0]['technologies'])

    def test_compare_results_no_changes(self):
        """Test comparing identical results"""
        data = {
            'url': 'https://example.com',
            'timestamp': '2025-01-30T10:00:00',
            'status_code': 200,
            'title': 'Test',
            'body_length': 1000,
            'content_hash': 'abc123',
            'technologies': ['Apache'],
            'flags': []
        }

        changes = self.monitor.compare_results(data, data.copy())

        self.assertFalse(changes['has_changes'])

    def test_save_and_load_snapshot(self):
        """Test saving and loading snapshot"""
        results = {
            'https://example.com': {
                'status_code': 200,
                'title': 'Test',
                'body_length': 1000
            }
        }

        # Save snapshot
        snapshot_file = self.monitor.save_snapshot(results, 'test_snapshot.json')

        self.assertTrue(os.path.exists(snapshot_file))

        # Load snapshot
        loaded = self.monitor.load_snapshot('test_snapshot.json')

        self.assertEqual(loaded, results)

    def test_load_nonexistent_snapshot(self):
        """Test loading non-existent snapshot"""
        result = self.monitor.load_snapshot('nonexistent.json')
        self.assertIsNone(result)

    @patch('modules.http_monitor.HTTPMonitor.probe_url')
    def test_probe_multiple_sequential(self, mock_probe):
        """Test probing multiple URLs sequentially"""
        mock_probe.return_value = {
            'url': '',
            'status_code': 200,
            'reachable': True
        }

        urls = ['https://example.com', 'https://test.com']
        results = self.monitor.probe_multiple(urls, parallel=False)

        self.assertEqual(len(results), 2)
        self.assertEqual(mock_probe.call_count, 2)

    @patch('modules.http_monitor.HTTPMonitor.probe_url')
    def test_probe_multiple_parallel(self, mock_probe):
        """Test probing multiple URLs in parallel"""
        mock_probe.return_value = {
            'url': '',
            'status_code': 200,
            'reachable': True
        }

        urls = ['https://example.com', 'https://test.com', 'https://demo.com']
        results = self.monitor.probe_multiple(urls, parallel=True)

        self.assertEqual(len(results), 3)


if __name__ == '__main__':
    unittest.main()
