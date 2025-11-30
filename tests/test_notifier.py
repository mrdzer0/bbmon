#!/usr/bin/env python3
"""
Unit tests for modules/notifier.py - Notification functionality
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock, call

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.notifier import Notifier


class TestNotifier(unittest.TestCase):
    """Test cases for Notifier class"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'slack': {
                'enabled': True,
                'webhook_url': 'https://hooks.slack.com/test',
                'notify_on': ['new_subdomain', 'baseline_complete']
            },
            'discord': {
                'enabled': True,
                'webhook_url': 'https://discord.com/api/webhooks/test',
                'notify_on': ['new_subdomain', 'new_endpoint', 'changed_endpoint', 'baseline_complete']
            },
            'telegram': {
                'enabled': False,
                'bot_token': 'test_token',
                'chat_id': 'test_chat',
                'notify_on': []
            },
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.test.com',
                'smtp_port': 587,
                'username': 'test@test.com',
                'password': 'password',
                'to_email': 'recipient@test.com',
                'notify_on': []
            }
        }

    def test_init(self):
        """Test Notifier initialization"""
        notifier = Notifier(self.config)
        self.assertEqual(notifier.config, self.config)

    def test_should_notify(self):
        """Test should_notify logic"""
        notifier = Notifier(self.config)

        # Should notify
        self.assertTrue(notifier.should_notify('new_subdomain', self.config['slack']))
        self.assertTrue(notifier.should_notify('baseline_complete', self.config['slack']))

        # Should not notify
        self.assertFalse(notifier.should_notify('changed_endpoint', self.config['slack']))

    @patch('modules.notifier.requests.post')
    def test_send_slack(self, mock_post):
        """Test Slack notification"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        notifier = Notifier(self.config)
        changes = {
            'new_subdomains': ['sub1.example.com', 'sub2.example.com'],
            'new_endpoints': ['https://example.com/api']
        }

        notifier.send_slack("Test message", changes)

        # Should call requests.post
        mock_post.assert_called_once()

        # Check payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        self.assertIn('blocks', payload)

    @patch('modules.notifier.requests.post')
    def test_send_discord(self, mock_post):
        """Test Discord notification"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        notifier = Notifier(self.config)
        changes = {
            'new_subdomains': ['sub1.example.com'],
            'new_endpoints': ['https://example.com/admin']
        }

        notifier.send_discord("Test message", changes)

        # Should call requests.post
        mock_post.assert_called_once()

        # Check payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        self.assertIn('embeds', payload)

    @patch('modules.notifier.requests.post')
    def test_send_telegram(self, mock_post):
        """Test Telegram notification"""
        # Enable telegram
        self.config['telegram']['enabled'] = True

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        notifier = Notifier(self.config)
        changes = {
            'new_subdomains': ['sub1.example.com'],
            'new_endpoints': []
        }

        notifier.send_telegram("Test message", changes)

        # Should call requests.post
        mock_post.assert_called_once()

        # Check URL
        call_args = mock_post.call_args
        url = call_args[0][0]
        self.assertIn('telegram.org', url)

    @patch('modules.notifier.requests.post')
    def test_send_baseline_alert_discord(self, mock_post):
        """Test baseline alert to Discord"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        notifier = Notifier(self.config)

        baseline = {
            'domain': 'example.com',
            'timestamp': '20250130_120000',
            'subdomains': {
                'sub1.example.com': True,
                'sub2.example.com': True,
                'sub3.example.com': True
            },
            'endpoints': {
                'https://example.com': {
                    'status_code': 200,
                    'title': 'Test'
                },
                'https://sub1.example.com': {
                    'status_code': 404,
                    'title': 'Not Found'
                }
            },
            'subdomain_takeovers': [],
            'shodan_data': {},
            'wayback_data': {}
        }

        notifier.send_baseline_alert('example.com', baseline)

        # Should send to Discord (enabled with baseline_complete in notify_on)
        self.assertTrue(mock_post.called)

        # Check payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        self.assertIn('embeds', payload)

        embed = payload['embeds'][0]
        self.assertIn('Baseline Scan Complete', embed['title'])
        self.assertIn('fields', embed)

    @patch('modules.notifier.requests.post')
    def test_send_baseline_alert_not_in_notify_on(self, mock_post):
        """Test baseline alert when not in notify_on list"""
        # Remove baseline_complete from ALL notify_on lists
        self.config['discord']['notify_on'] = ['new_subdomain']
        self.config['slack']['notify_on'] = ['new_subdomain']  # Also remove from Slack
        self.config['telegram']['enabled'] = False
        self.config['email']['enabled'] = False

        notifier = Notifier(self.config)

        baseline = {
            'domain': 'example.com',
            'timestamp': '20250130_120000',
            'subdomains': {},
            'endpoints': {}
        }

        notifier.send_baseline_alert('example.com', baseline)

        # Should NOT send to any platform (baseline_complete not in notify_on)
        mock_post.assert_not_called()

    @patch('modules.notifier.requests.post')
    def test_notify_changes_new_subdomains(self, mock_post):
        """Test change notification for new subdomains"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        notifier = Notifier(self.config)

        changes = {
            'new_subdomains': ['new1.example.com', 'new2.example.com'],
            'removed_subdomains': [],
            'new_endpoints': [],
            'removed_endpoints': [],
            'changed_endpoints': [],
            'new_js_endpoints': [],
            'new_takeovers': [],
            'resolved_takeovers': []
        }

        notifier.notify_changes('example.com', changes)

        # Should send Discord notification (new_subdomain in notify_on)
        self.assertTrue(mock_post.called)

        # Check that it's a change notification, not baseline
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        embed = payload['embeds'][0]
        self.assertIn('Monitoring', embed['title'])

    @patch('modules.notifier.requests.post')
    def test_notify_changes_critical_takeover(self, mock_post):
        """Test critical notification for subdomain takeover"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        # Add subdomain_takeover to notify_on
        self.config['discord']['notify_on'].append('subdomain_takeover')

        notifier = Notifier(self.config)

        changes = {
            'new_subdomains': [],
            'removed_subdomains': [],
            'new_endpoints': [],
            'removed_endpoints': [],
            'changed_endpoints': [],
            'new_js_endpoints': [],
            'new_takeovers': [
                {
                    'subdomain': 'old-app.example.com',
                    'service': 'heroku',
                    'cname': 'old-app.herokuapp.com',
                    'confidence': 'high'
                }
            ],
            'resolved_takeovers': []
        }

        notifier.notify_changes('example.com', changes)

        # Should send critical notification
        self.assertTrue(mock_post.called)

        call_args = mock_post.call_args
        payload = call_args[1]['json']
        embed = payload['embeds'][0]

        # Should be critical
        self.assertIn('CRITICAL', embed['title'])
        self.assertEqual(embed['color'], 15158332)  # Red color

    @patch('modules.notifier.requests.post')
    def test_notify_changes_changed_endpoints(self, mock_post):
        """Test notification for changed endpoints"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        notifier = Notifier(self.config)

        changes = {
            'new_subdomains': [],
            'removed_subdomains': [],
            'new_endpoints': [],
            'removed_endpoints': [],
            'changed_endpoints': [
                {
                    'url': 'https://example.com/admin',
                    'changes': {
                        'status_code': {
                            'old': 403,
                            'new': 200
                        },
                        'title': {
                            'old': 'Access Denied',
                            'new': 'Admin Dashboard'
                        },
                        'body_length': {
                            'old': 1000,
                            'new': 5000,
                            'diff_percent': 400.0
                        }
                    }
                }
            ],
            'new_js_endpoints': [],
            'new_takeovers': [],
            'resolved_takeovers': []
        }

        notifier.notify_changes('example.com', changes)

        # Should send notification
        self.assertTrue(mock_post.called)

        call_args = mock_post.call_args
        payload = call_args[1]['json']
        embed = payload['embeds'][0]

        # Should show changed endpoints
        fields = embed['fields']
        changed_field = next((f for f in fields if 'Changed Endpoints' in f['name']), None)
        self.assertIsNotNone(changed_field)
        self.assertIn('Status: 403', changed_field['value'])

    @patch('modules.notifier.requests.post')
    def test_notify_changes_no_changes(self, mock_post):
        """Test notification when no changes"""
        notifier = Notifier(self.config)

        changes = {
            'new_subdomains': [],
            'removed_subdomains': [],
            'new_endpoints': [],
            'removed_endpoints': [],
            'changed_endpoints': [],
            'new_js_endpoints': [],
            'new_takeovers': [],
            'resolved_takeovers': []
        }

        notifier.notify_changes('example.com', changes)

        # Should NOT send notification (no changes)
        mock_post.assert_not_called()

    @patch('modules.notifier.requests.post')
    def test_discord_changes_with_flags(self, mock_post):
        """Test Discord notification with high-value flags"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        notifier = Notifier(self.config)

        changes = {
            'new_subdomains': [],
            'removed_subdomains': [],
            'new_endpoints': [],
            'removed_endpoints': [],
            'changed_endpoints': [
                {
                    'url': 'https://example.com/upload',
                    'changes': {
                        'new_flags': [
                            {
                                'severity': 'high',
                                'message': 'High-value target: upload (upload in URL)'
                            }
                        ]
                    }
                }
            ],
            'new_js_endpoints': [],
            'new_takeovers': [],
            'resolved_takeovers': []
        }

        notifier.notify_changes('example.com', changes)

        # Should send critical notification due to high-value flag
        self.assertTrue(mock_post.called)

        call_args = mock_post.call_args
        payload = call_args[1]['json']
        embed = payload['embeds'][0]

        # Should be critical
        self.assertIn('CRITICAL', embed['title'])

    @patch('modules.notifier.requests.post')
    def test_send_discord_changes_detailed(self, mock_post):
        """Test detailed Discord change notification"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        notifier = Notifier(self.config)

        changes = {
            'new_subdomains': ['api.example.com', 'admin.example.com'],
            'removed_subdomains': [],
            'new_endpoints': ['https://api.example.com/v2'],
            'removed_endpoints': [],
            'changed_endpoints': [
                {
                    'url': 'https://example.com',
                    'changes': {
                        'status_code': {'old': 403, 'new': 200},
                        'technologies': {
                            'added': ['PHP'],
                            'removed': []
                        }
                    }
                }
            ],
            'new_js_endpoints': ['/api/secret'],
            'new_takeovers': [],
            'resolved_takeovers': []
        }

        notifier._send_discord_changes('example.com', changes, is_critical=False)

        # Should send notification
        self.assertTrue(mock_post.called)

        call_args = mock_post.call_args
        payload = call_args[1]['json']
        embed = payload['embeds'][0]

        # Check all sections are present
        fields = embed['fields']
        field_names = [f['name'] for f in fields]

        self.assertTrue(any('New Subdomains' in name for name in field_names))
        self.assertTrue(any('New Endpoints' in name for name in field_names))
        self.assertTrue(any('Changed Endpoints' in name for name in field_names))
        self.assertTrue(any('New JS Endpoints' in name for name in field_names))


if __name__ == '__main__':
    unittest.main()
