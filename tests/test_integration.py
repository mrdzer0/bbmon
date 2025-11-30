#!/usr/bin/env python3
"""
Integration tests for bb-monitor
Tests the complete workflow from initialization to monitoring
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor import BBMonitor


class TestIntegration(unittest.TestCase):
    """Integration test cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

        # Create test config
        self.config = {
            'targets': {
                'domains': ['example.com']
            },
            'monitoring': {
                'data_dir': os.path.join(self.test_dir, 'data'),
                'baseline_dir': os.path.join(self.test_dir, 'baseline'),
                'diff_dir': os.path.join(self.test_dir, 'diffs'),
                'reports_dir': os.path.join(self.test_dir, 'reports')
            },
            'checks': {
                'infrastructure': {'subdomain_discovery': True},
                'web_application': {'http_responses': True},
                'content_discovery': {'enabled': False}
            },
            'tools': {
                'subfinder': {'enabled': True, 'timeout': 300},
                'amass': {'enabled': False, 'passive': True, 'timeout': 600},
                'katana': {'enabled': False, 'depth': 3, 'timeout': 300},
                'shodan': {'enabled': False},
                'wayback': {'enabled': False}
            },
            'notifications': {
                'slack': {'enabled': False},
                'discord': {
                    'enabled': True,
                    'webhook_url': 'https://discord.com/api/webhooks/test',
                    'notify_on': ['new_subdomain', 'changed_endpoint', 'baseline_complete']
                },
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

    @patch('modules.notifier.requests.post')
    @patch('monitor.BBMonitor.probe_http')
    @patch('monitor.BBMonitor.discover_subdomains')
    def test_full_init_workflow(self, mock_discover, mock_probe, mock_post):
        """Test complete initialization workflow"""
        # Mock subdomain discovery
        mock_discover.return_value = {
            'subdomains': {'sub1.example.com', 'sub2.example.com', 'api.example.com'},
            'takeovers': [],
            'dns_results': {},
            'by_source': {}
        }

        # Mock HTTP probing
        mock_probe.return_value = {
            'https://sub1.example.com': {
                'status_code': 200,
                'title': 'Subdomain 1',
                'body_length': 5000,
                'technologies': ['Apache'],
                'flags': []
            },
            'https://api.example.com': {
                'status_code': 200,
                'title': 'API',
                'body_length': 2000,
                'technologies': ['nginx'],
                'flags': [
                    {'severity': 'medium', 'category': 'api', 'message': 'API endpoint'}
                ]
            }
        }

        # Mock Discord webhook
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        # Run initialization
        monitor = BBMonitor(config_path=self.config_file)
        monitor.run_initial_baseline()

        # Verify subdomain discovery was called
        mock_discover.assert_called_once_with('example.com')

        # Verify HTTP probing was called
        mock_probe.assert_called_once()

        # Verify baseline was saved
        baseline_file = Path(self.config['monitoring']['baseline_dir']) / 'example.com_baseline.json'
        self.assertTrue(baseline_file.exists())

        # Load and verify baseline content
        with open(baseline_file, 'r') as f:
            baseline = json.load(f)

        self.assertEqual(baseline['domain'], 'example.com')
        self.assertEqual(len(baseline['subdomains']), 3)
        self.assertEqual(len(baseline['endpoints']), 2)

        # Verify baseline_complete notification was sent
        mock_post.assert_called()

        # Check that notification is baseline_complete
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        embed = payload['embeds'][0]
        self.assertIn('Baseline', embed['title'])

    @patch('modules.notifier.requests.post')
    @patch('monitor.BBMonitor.probe_http')
    @patch('monitor.BBMonitor.discover_subdomains')
    def test_full_monitoring_workflow_no_changes(self, mock_discover, mock_probe, mock_post):
        """Test complete monitoring workflow with no changes"""
        # First create baseline
        baseline_data = {
            'domain': 'example.com',
            'timestamp': '20250130_100000',
            'subdomains': {
                'sub1.example.com': True,
                'sub2.example.com': True
            },
            'endpoints': {
                'https://sub1.example.com': {
                    'status_code': 200,
                    'title': 'Test',
                    'body_length': 5000,
                    'technologies': ['Apache'],
                    'flags': []
                }
            },
            'subdomain_takeovers': []
        }

        baseline_file = Path(self.config['monitoring']['baseline_dir'])
        baseline_file.mkdir(parents=True, exist_ok=True)
        with open(baseline_file / 'example.com_baseline.json', 'w') as f:
            json.dump(baseline_data, f)

        # Mock same data for monitoring
        mock_discover.return_value = {
            'subdomains': {'sub1.example.com', 'sub2.example.com'},
            'takeovers': [],
            'dns_results': {},
            'by_source': {}
        }

        mock_probe.return_value = {
            'https://sub1.example.com': {
                'status_code': 200,
                'title': 'Test',
                'body_length': 5000,
                'technologies': ['Apache'],
                'flags': []
            }
        }

        # Run monitoring
        monitor = BBMonitor(config_path=self.config_file)
        monitor.run_monitoring()

        # Should NOT send change notification (no changes)
        # Only baseline update, not alert
        if mock_post.called:
            # If called, should not be for changes
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            # Should not have change notification
            self.assertFalse('Monitoring Alert' in str(payload))

    @patch('modules.notifier.requests.post')
    @patch('monitor.BBMonitor.probe_http')
    @patch('monitor.BBMonitor.discover_subdomains')
    def test_full_monitoring_workflow_with_changes(self, mock_discover, mock_probe, mock_post):
        """Test complete monitoring workflow with changes detected"""
        # First create baseline
        baseline_data = {
            'domain': 'example.com',
            'timestamp': '20250130_100000',
            'subdomains': {
                'sub1.example.com': True
            },
            'endpoints': {
                'https://sub1.example.com': {
                    'status_code': 403,
                    'title': 'Forbidden',
                    'body_length': 1000,
                    'technologies': ['Apache'],
                    'flags': []
                }
            },
            'subdomain_takeovers': []
        }

        baseline_file = Path(self.config['monitoring']['baseline_dir'])
        baseline_file.mkdir(parents=True, exist_ok=True)
        with open(baseline_file / 'example.com_baseline.json', 'w') as f:
            json.dump(baseline_data, f)

        # Mock NEW data with changes
        mock_discover.return_value = {
            'subdomains': {
                'sub1.example.com',
                'new-api.example.com'  # NEW subdomain
            },
            'takeovers': [],
            'dns_results': {},
            'by_source': {}
        }

        mock_probe.return_value = {
            'https://sub1.example.com': {
                'status_code': 200,  # CHANGED from 403
                'title': 'Admin Panel',  # CHANGED
                'body_length': 5000,  # CHANGED
                'technologies': ['Apache', 'PHP'],  # ADDED technology
                'flags': [
                    {'severity': 'high', 'message': 'Admin panel detected'}  # NEW flag
                ]
            },
            'https://new-api.example.com': {  # NEW endpoint
                'status_code': 200,
                'title': 'API',
                'body_length': 2000,
                'technologies': ['nginx'],
                'flags': []
            }
        }

        # Mock Discord webhook
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        # Run monitoring
        monitor = BBMonitor(config_path=self.config_file)
        monitor.run_monitoring()

        # Verify change notification was sent
        mock_post.assert_called()

        # Check notification content
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        embed = payload['embeds'][0]

        # Should be monitoring alert (might be CRITICAL if high-value flags)
        self.assertTrue('Monitoring' in embed['title'] or 'CRITICAL' in embed['title'])

        # Should have fields for changes
        fields = embed['fields']
        field_names = [f['name'] for f in fields]

        # Should show new subdomain
        self.assertTrue(any('New Subdomains' in name for name in field_names))

        # Should show changed endpoint
        self.assertTrue(any('Changed Endpoints' in name for name in field_names))

        # Verify diff file was created
        diff_dir = Path(self.config['monitoring']['diff_dir'])
        diff_files = list(diff_dir.glob('*.json'))
        self.assertGreater(len(diff_files), 0)

        # Load and verify diff
        with open(diff_files[0], 'r') as f:
            diff_data = json.load(f)

        self.assertIn('new-api.example.com', diff_data['new_subdomains'])
        self.assertEqual(len(diff_data['changed_endpoints']), 1)

    @patch('modules.notifier.requests.post')
    @patch('monitor.BBMonitor.probe_http')
    @patch('monitor.BBMonitor.discover_subdomains')
    def test_monitoring_with_subdomain_takeover(self, mock_discover, mock_probe, mock_post):
        """Test monitoring workflow detecting subdomain takeover"""
        # Create baseline
        baseline_data = {
            'domain': 'example.com',
            'timestamp': '20250130_100000',
            'subdomains': {'sub1.example.com': True},
            'endpoints': {},
            'subdomain_takeovers': []
        }

        baseline_file = Path(self.config['monitoring']['baseline_dir'])
        baseline_file.mkdir(parents=True, exist_ok=True)
        with open(baseline_file / 'example.com_baseline.json', 'w') as f:
            json.dump(baseline_data, f)

        # Mock with takeover
        mock_discover.return_value = {
            'subdomains': {'sub1.example.com', 'old-app.example.com'},
            'takeovers': [
                {
                    'subdomain': 'old-app.example.com',
                    'service': 'heroku',
                    'cname': 'old-app.herokuapp.com',
                    'confidence': 'high'
                }
            ],
            'dns_results': {},
            'by_source': {}
        }

        mock_probe.return_value = {}

        # Mock Discord webhook
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        # Add subdomain_takeover to notify_on
        self.config['notifications']['discord']['notify_on'].append('subdomain_takeover')
        with open(self.config_file, 'w') as f:
            import yaml
            yaml.dump(self.config, f)

        # Run monitoring
        monitor = BBMonitor(config_path=self.config_file)
        monitor.run_monitoring()

        # Should send CRITICAL notification
        mock_post.assert_called()

        call_args = mock_post.call_args
        payload = call_args[1]['json']
        embed = payload['embeds'][0]

        # Should be critical alert
        self.assertIn('CRITICAL', embed['title'])
        self.assertEqual(embed['color'], 15158332)  # Red

        # Should have takeover field
        fields = embed['fields']
        takeover_field = next((f for f in fields if 'TAKEOVER' in f['name']), None)
        self.assertIsNotNone(takeover_field)

    @patch('modules.notifier.requests.post')
    @patch('monitor.BBMonitor.discover_subdomains')
    def test_first_time_monitoring_sends_baseline_alert(self, mock_discover, mock_post):
        """Test that first-time monitoring sends baseline alert"""
        # NO existing baseline

        # Mock discovery
        mock_discover.return_value = {
            'subdomains': {'sub1.example.com'},
            'takeovers': [],
            'dns_results': {},
            'by_source': {}
        }

        # Mock Discord webhook
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        # Run monitoring (no baseline exists)
        monitor = BBMonitor(config_path=self.config_file)

        with patch.object(monitor, 'probe_http', return_value={}):
            monitor.run_monitoring()

        # Should send baseline_complete alert (first-time)
        mock_post.assert_called()

        call_args = mock_post.call_args
        payload = call_args[1]['json']
        embed = payload['embeds'][0]

        # Should be baseline alert
        self.assertIn('Baseline', embed['title'])

    def test_baseline_file_structure(self):
        """Test baseline file structure"""
        monitor = BBMonitor(config_path=self.config_file)

        baseline = {
            'domain': 'example.com',
            'timestamp': '20250130_120000',
            'subdomains': {
                'sub1.example.com': True,
                'api.example.com': True
            },
            'endpoints': {
                'https://example.com': {
                    'status_code': 200,
                    'title': 'Test',
                    'body_length': 5000,
                    'technologies': ['Apache'],
                    'flags': []
                }
            },
            'subdomain_takeovers': [],
            'dns_info': {}
        }

        monitor.save_baseline('example.com', baseline, send_alert=False)

        # Load and verify
        baseline_file = Path(self.config['monitoring']['baseline_dir']) / 'example.com_baseline.json'
        with open(baseline_file, 'r') as f:
            loaded = json.load(f)

        # Verify structure
        self.assertIn('domain', loaded)
        self.assertIn('timestamp', loaded)
        self.assertIn('subdomains', loaded)
        self.assertIn('endpoints', loaded)
        self.assertIn('subdomain_takeovers', loaded)

        # Verify data types
        self.assertIsInstance(loaded['subdomains'], dict)
        self.assertIsInstance(loaded['endpoints'], dict)
        self.assertIsInstance(loaded['subdomain_takeovers'], list)


if __name__ == '__main__':
    unittest.main()
