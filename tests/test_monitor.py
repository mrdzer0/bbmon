#!/usr/bin/env python3
"""
Unit tests for monitor.py - Main monitoring functionality
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor import BBMonitor, Colors


class TestBBMonitor(unittest.TestCase):
    """Test cases for BBMonitor class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()

        # Create test config
        self.config = {
            'targets': {
                'domains': ['example.com', 'test.com']
            },
            'monitoring': {
                'data_dir': os.path.join(self.test_dir, 'data'),
                'baseline_dir': os.path.join(self.test_dir, 'baseline'),
                'diff_dir': os.path.join(self.test_dir, 'diffs'),
                'reports_dir': os.path.join(self.test_dir, 'reports')
            },
            'checks': {
                'infrastructure': {
                    'subdomain_discovery': True
                },
                'web_application': {
                    'http_responses': True
                },
                'content_discovery': {
                    'enabled': True
                }
            },
            'tools': {
                'subfinder': {'enabled': True, 'timeout': 300},
                'amass': {'enabled': False, 'passive': True, 'timeout': 600},
                'katana': {'enabled': True, 'depth': 3, 'timeout': 300},
                'shodan': {'enabled': False},
                'wayback': {'enabled': False}
            },
            'notifications': {
                'slack': {'enabled': False},
                'discord': {'enabled': False},
                'telegram': {'enabled': False},
                'email': {'enabled': False}
            }
        }

        # Write config to file
        self.config_file = os.path.join(self.test_dir, 'config.yaml')
        import yaml
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test BBMonitor initialization"""
        monitor = BBMonitor(config_path=self.config_file)

        self.assertIsNotNone(monitor.config)
        self.assertEqual(monitor.config['targets']['domains'], ['example.com', 'test.com'])
        self.assertIsNone(monitor.shodan_scanner)
        self.assertIsNone(monitor.wayback_analyzer)

    def test_setup_directories(self):
        """Test directory creation"""
        monitor = BBMonitor(config_path=self.config_file)

        # Check if directories were created
        self.assertTrue(os.path.exists(self.config['monitoring']['data_dir']))
        self.assertTrue(os.path.exists(self.config['monitoring']['baseline_dir']))
        self.assertTrue(os.path.exists(self.config['monitoring']['diff_dir']))
        self.assertTrue(os.path.exists(self.config['monitoring']['reports_dir']))

    def test_get_targets(self):
        """Test target retrieval"""
        monitor = BBMonitor(config_path=self.config_file)
        targets = monitor.get_targets()

        self.assertEqual(len(targets), 2)
        self.assertIn('example.com', targets)
        self.assertIn('test.com', targets)

    def test_get_targets_from_file(self):
        """Test target retrieval from file"""
        # Create targets file
        targets_file = os.path.join(self.test_dir, 'targets.txt')
        with open(targets_file, 'w') as f:
            f.write('fromfile.com\n')
            f.write('another.com\n')

        # Update config
        self.config['targets']['domains_file'] = targets_file
        with open(self.config_file, 'w') as f:
            import yaml
            yaml.dump(self.config, f)

        monitor = BBMonitor(config_path=self.config_file)
        targets = monitor.get_targets()

        # Should have targets from both config and file
        self.assertIn('example.com', targets)
        self.assertIn('fromfile.com', targets)
        self.assertIn('another.com', targets)

    def test_hash_content(self):
        """Test content hashing"""
        monitor = BBMonitor(config_path=self.config_file)

        content1 = "test content"
        content2 = "test content"
        content3 = "different content"

        hash1 = monitor.hash_content(content1)
        hash2 = monitor.hash_content(content2)
        hash3 = monitor.hash_content(content3)

        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)
        self.assertEqual(len(hash1), 64)  # SHA256 hash length

    def test_json_safe(self):
        """Test JSON-safe conversion"""
        monitor = BBMonitor(config_path=self.config_file)

        # Test with sets
        data = {
            'subdomains': {'sub1.example.com', 'sub2.example.com'},
            'count': 2,
            'nested': {
                'items': {'item1', 'item2'}
            }
        }

        safe_data = monitor._json_safe(data)

        # Should convert sets to lists
        self.assertIsInstance(safe_data['subdomains'], list)
        self.assertIsInstance(safe_data['nested']['items'], list)

        # Should be JSON serializable
        json_str = json.dumps(safe_data)
        self.assertIsNotNone(json_str)

    @patch('monitor.SubdomainFinder')
    def test_discover_subdomains_basic(self, mock_subfinder):
        """Test basic subdomain discovery"""
        # Mock SubdomainFinder result
        mock_instance = Mock()
        mock_instance.run_all.return_value = {
            'subdomains': {'sub1.example.com', 'sub2.example.com', 'sub3.example.com'},
            'takeovers': [],
            'dns_results': {},
            'by_source': {}
        }
        mock_subfinder.return_value = mock_instance

        monitor = BBMonitor(config_path=self.config_file)
        result = monitor.discover_subdomains('example.com')

        self.assertIn('subdomains', result)
        self.assertEqual(len(result['subdomains']), 3)

    def test_save_and_load_baseline(self):
        """Test baseline save and load"""
        monitor = BBMonitor(config_path=self.config_file)

        baseline = {
            'domain': 'example.com',
            'timestamp': '20250130_120000',
            'subdomains': {'sub1.example.com': True, 'sub2.example.com': True},
            'endpoints': {},
            'subdomain_takeovers': []
        }

        # Save baseline (without alert)
        monitor.save_baseline('example.com', baseline, send_alert=False)

        # Check file was created
        baseline_file = Path(self.config['monitoring']['baseline_dir']) / 'example.com_baseline.json'
        self.assertTrue(baseline_file.exists())

        # Load baseline
        loaded = monitor.load_baseline('example.com')
        self.assertEqual(loaded['domain'], 'example.com')
        self.assertEqual(len(loaded['subdomains']), 2)

    def test_save_baseline_with_alert(self):
        """Test baseline save with alert flag"""
        monitor = BBMonitor(config_path=self.config_file)

        baseline = {
            'domain': 'example.com',
            'timestamp': '20250130_120000',
            'subdomains': {},
            'endpoints': {}
        }

        # Mock notifier
        with patch('modules.notifier.Notifier') as mock_notifier:
            mock_instance = Mock()
            mock_notifier.return_value = mock_instance

            # Save with alert
            monitor.save_baseline('example.com', baseline, send_alert=True)

            # Should call send_baseline_alert
            mock_instance.send_baseline_alert.assert_called_once_with('example.com', baseline)

    def test_save_baseline_without_alert(self):
        """Test baseline save without alert flag"""
        monitor = BBMonitor(config_path=self.config_file)

        baseline = {
            'domain': 'example.com',
            'timestamp': '20250130_120000',
            'subdomains': {},
            'endpoints': {}
        }

        # Mock notifier
        with patch('modules.notifier.Notifier') as mock_notifier:
            mock_instance = Mock()
            mock_notifier.return_value = mock_instance

            # Save without alert
            monitor.save_baseline('example.com', baseline, send_alert=False)

            # Should NOT call send_baseline_alert
            mock_instance.send_baseline_alert.assert_not_called()

    def test_compare_baselines_new_subdomains(self):
        """Test baseline comparison - new subdomains"""
        monitor = BBMonitor(config_path=self.config_file)

        old = {
            'subdomains': {'sub1.example.com': True, 'sub2.example.com': True},
            'endpoints': {},
            'subdomain_takeovers': []
        }

        new = {
            'subdomains': {
                'sub1.example.com': True,
                'sub2.example.com': True,
                'sub3.example.com': True,  # New
                'sub4.example.com': True   # New
            },
            'endpoints': {},
            'subdomain_takeovers': []
        }

        changes = monitor.compare_baselines('example.com', old, new)

        self.assertEqual(len(changes['new_subdomains']), 2)
        self.assertIn('sub3.example.com', changes['new_subdomains'])
        self.assertIn('sub4.example.com', changes['new_subdomains'])

    def test_compare_baselines_removed_subdomains(self):
        """Test baseline comparison - removed subdomains"""
        monitor = BBMonitor(config_path=self.config_file)

        old = {
            'subdomains': {
                'sub1.example.com': True,
                'sub2.example.com': True,
                'old.example.com': True
            },
            'endpoints': {},
            'subdomain_takeovers': []
        }

        new = {
            'subdomains': {'sub1.example.com': True, 'sub2.example.com': True},
            'endpoints': {},
            'subdomain_takeovers': []
        }

        changes = monitor.compare_baselines('example.com', old, new)

        self.assertEqual(len(changes['removed_subdomains']), 1)
        self.assertIn('old.example.com', changes['removed_subdomains'])

    def test_compare_baselines_changed_endpoints(self):
        """Test baseline comparison - changed endpoints"""
        monitor = BBMonitor(config_path=self.config_file)

        old = {
            'subdomains': {},
            'endpoints': {
                'https://example.com': {
                    'status_code': 403,
                    'title': 'Access Denied',
                    'body_length': 1000,
                    'technologies': ['Apache'],
                    'flags': []
                }
            },
            'subdomain_takeovers': []
        }

        new = {
            'subdomains': {},
            'endpoints': {
                'https://example.com': {
                    'status_code': 200,  # Changed
                    'title': 'Admin Dashboard',  # Changed
                    'body_length': 5000,  # Changed significantly
                    'technologies': ['Apache', 'PHP'],  # Added technology
                    'flags': []
                }
            },
            'subdomain_takeovers': []
        }

        changes = monitor.compare_baselines('example.com', old, new)

        self.assertEqual(len(changes['changed_endpoints']), 1)

        endpoint_change = changes['changed_endpoints'][0]
        self.assertEqual(endpoint_change['url'], 'https://example.com')

        # Check specific changes
        changes_dict = endpoint_change['changes']
        self.assertIn('status_code', changes_dict)
        self.assertIn('title', changes_dict)
        self.assertIn('body_length', changes_dict)
        self.assertIn('technologies', changes_dict)

    def test_compare_baselines_subdomain_takeovers(self):
        """Test baseline comparison - subdomain takeovers"""
        monitor = BBMonitor(config_path=self.config_file)

        old = {
            'subdomains': {},
            'endpoints': {},
            'subdomain_takeovers': []
        }

        new = {
            'subdomains': {},
            'endpoints': {},
            'subdomain_takeovers': [
                {
                    'subdomain': 'old-app.example.com',
                    'service': 'heroku',
                    'cname': 'old-app.herokuapp.com',
                    'confidence': 'high'
                }
            ]
        }

        changes = monitor.compare_baselines('example.com', old, new)

        self.assertEqual(len(changes['new_takeovers']), 1)
        self.assertEqual(changes['new_takeovers'][0]['subdomain'], 'old-app.example.com')
        self.assertEqual(changes['new_takeovers'][0]['service'], 'heroku')

    @patch('monitor.BBMonitor.discover_subdomains')
    @patch('monitor.BBMonitor.probe_http')
    def test_collect_baseline(self, mock_probe_http, mock_discover):
        """Test baseline collection"""
        # Mock subdomain discovery
        mock_discover.return_value = {
            'subdomains': {'sub1.example.com', 'sub2.example.com'},
            'takeovers': [],
            'dns_results': {},
            'by_source': {}
        }

        # Mock HTTP probing
        mock_probe_http.return_value = {
            'https://sub1.example.com': {
                'status_code': 200,
                'title': 'Test',
                'body_length': 1000
            }
        }

        monitor = BBMonitor(config_path=self.config_file)
        baseline = monitor.collect_baseline('example.com')

        self.assertEqual(baseline['domain'], 'example.com')
        self.assertIn('subdomains', baseline)
        self.assertIn('endpoints', baseline)
        self.assertEqual(len(baseline['subdomains']), 2)

    @patch('modules.notifier.Notifier')
    @patch('monitor.BBMonitor.collect_baseline')
    def test_run_initial_baseline(self, mock_collect, mock_notifier):
        """Test initial baseline run"""
        # Mock baseline collection
        mock_collect.return_value = {
            'domain': 'example.com',
            'timestamp': '20250130_120000',
            'subdomains': {},
            'endpoints': {}
        }

        mock_notifier_instance = Mock()
        mock_notifier.return_value = mock_notifier_instance

        monitor = BBMonitor(config_path=self.config_file)
        monitor.run_initial_baseline()

        # Should collect baseline for each target
        self.assertEqual(mock_collect.call_count, 2)

        # Should send alerts (send_alert=True)
        # Check that baseline files were created
        baseline_dir = Path(self.config['monitoring']['baseline_dir'])
        self.assertTrue(len(list(baseline_dir.glob('*.json'))) > 0)

    @patch('modules.notifier.Notifier')
    @patch('monitor.BBMonitor.collect_baseline')
    @patch('monitor.BBMonitor.load_baseline')
    @patch('monitor.BBMonitor.compare_baselines')
    def test_run_monitoring(self, mock_compare, mock_load, mock_collect, mock_notifier):
        """Test monitoring run"""
        # Mock existing baseline
        mock_load.return_value = {
            'domain': 'example.com',
            'subdomains': {'sub1.example.com': True},
            'endpoints': {},
            'subdomain_takeovers': []
        }

        # Mock new baseline
        mock_collect.return_value = {
            'domain': 'example.com',
            'subdomains': {
                'sub1.example.com': True,
                'sub2.example.com': True  # New subdomain
            },
            'endpoints': {},
            'subdomain_takeovers': []
        }

        # Mock comparison
        mock_compare.return_value = {
            'new_subdomains': ['sub2.example.com'],
            'removed_subdomains': [],
            'new_endpoints': [],
            'removed_endpoints': [],
            'changed_endpoints': [],
            'new_js_files': [],
            'changed_js_files': [],
            'new_js_endpoints': [],
            'new_takeovers': [],
            'resolved_takeovers': []
        }

        mock_notifier_instance = Mock()
        mock_notifier.return_value = mock_notifier_instance

        monitor = BBMonitor(config_path=self.config_file)
        monitor.run_monitoring()

        # Should load, collect, and compare baselines
        self.assertEqual(mock_load.call_count, 2)
        self.assertEqual(mock_collect.call_count, 2)
        self.assertEqual(mock_compare.call_count, 2)

        # Should call notify_changes (not send_baseline_alert)
        self.assertEqual(mock_notifier_instance.notify_changes.call_count, 2)

    @patch('modules.notifier.Notifier')
    @patch('monitor.BBMonitor.collect_baseline')
    @patch('monitor.BBMonitor.load_baseline')
    def test_run_monitoring_first_time(self, mock_load, mock_collect, mock_notifier):
        """Test monitoring run when no baseline exists"""
        # Mock no existing baseline
        mock_load.return_value = None

        # Mock new baseline
        mock_collect.return_value = {
            'domain': 'example.com',
            'subdomains': {},
            'endpoints': {}
        }

        mock_notifier_instance = Mock()
        mock_notifier.return_value = mock_notifier_instance

        monitor = BBMonitor(config_path=self.config_file)
        monitor.run_monitoring()

        # Should send alert for first-time baseline
        # Check that baseline was created
        baseline_dir = Path(self.config['monitoring']['baseline_dir'])
        self.assertTrue(len(list(baseline_dir.glob('*.json'))) > 0)


if __name__ == '__main__':
    unittest.main()
