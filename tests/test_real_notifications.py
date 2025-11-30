#!/usr/bin/env python3
"""
Real Notification Testing Script
Tests actual notifications to configured platforms (Discord, Slack, Telegram, Email)
"""

import os
import sys
import yaml
import argparse
from datetime import datetime

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.notifier import Notifier


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def load_config(config_path='config.yaml'):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"{Colors.RED}[!] Error loading config: {e}{Colors.RESET}")
        sys.exit(1)


def test_baseline_alert(config, platform=None):
    """Test baseline completion alert"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}Testing Baseline Alert{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    # Create sample baseline data
    baseline = {
        'domain': 'test-example.com',
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'subdomains': {
            'www.test-example.com': True,
            'api.test-example.com': True,
            'admin.test-example.com': True,
            'staging.test-example.com': True,
            'dev.test-example.com': True
        },
        'endpoints': {
            'https://test-example.com': {
                'status_code': 200,
                'title': 'Test Homepage',
                'body_length': 15000,
                'technologies': ['Apache', 'PHP'],
                'flags': []
            },
            'https://api.test-example.com': {
                'status_code': 200,
                'title': 'API Documentation',
                'body_length': 8000,
                'technologies': ['nginx', 'Node.js'],
                'flags': [
                    {'severity': 'medium', 'message': 'API endpoint detected'}
                ]
            },
            'https://admin.test-example.com': {
                'status_code': 403,
                'title': 'Access Denied',
                'body_length': 1200,
                'technologies': ['Apache'],
                'flags': [
                    {'severity': 'high', 'message': 'High-value target: admin panel'}
                ]
            }
        },
        'subdomain_takeovers': [],
        'shodan_data': {
            'summary': {
                'total_hosts': 5,
                'with_vulnerabilities': 2,
                'high_value_hosts': 1
            }
        },
        'wayback_data': {
            'total_urls': 1250,
            'statistics': {
                'by_priority': {
                    'critical': 3,
                    'high': 12
                },
                'by_category': {
                    'backup': 5,
                    'config': 3,
                    'api': 25
                }
            }
        }
    }

    # Filter config if specific platform requested
    test_config = config['notifications'].copy()
    if platform:
        for p in ['slack', 'discord', 'telegram', 'email']:
            if p != platform:
                test_config[p]['enabled'] = False

    notifier = Notifier(test_config)

    print(f"{Colors.YELLOW}[*] Sending baseline alert to configured platforms...{Colors.RESET}\n")
    print(f"Domain: {Colors.CYAN}{baseline['domain']}{Colors.RESET}")
    print(f"Subdomains: {Colors.GREEN}{len(baseline['subdomains'])}{Colors.RESET}")
    print(f"Endpoints: {Colors.GREEN}{len(baseline['endpoints'])}{Colors.RESET}")
    print(f"Timestamp: {Colors.BLUE}{baseline['timestamp']}{Colors.RESET}\n")

    notifier.send_baseline_alert(baseline['domain'], baseline)

    print(f"\n{Colors.GREEN}✓ Baseline alert sent!{Colors.RESET}")
    print(f"{Colors.YELLOW}Check your configured platforms for the alert.{Colors.RESET}\n")


def test_change_alert(config, platform=None):
    """Test change detection alert"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}Testing Change Detection Alert{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    # Create sample changes data
    changes = {
        'new_subdomains': [
            'new-api.test-example.com',
            'mobile.test-example.com'
        ],
        'removed_subdomains': [],
        'new_endpoints': [
            'https://new-api.test-example.com',
            'https://mobile.test-example.com'
        ],
        'removed_endpoints': [],
        'changed_endpoints': [
            {
                'url': 'https://admin.test-example.com',
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
                        'old': 1200,
                        'new': 25000,
                        'diff_percent': 1983.33
                    },
                    'technologies': {
                        'added': ['PHP', 'MySQL'],
                        'removed': []
                    },
                    'new_flags': [
                        {
                            'severity': 'high',
                            'message': 'High-value target: admin (admin in URL)'
                        }
                    ]
                }
            },
            {
                'url': 'https://upload.test-example.com',
                'changes': {
                    'status_code': {
                        'old': 404,
                        'new': 200
                    },
                    'title': {
                        'old': 'Not Found',
                        'new': 'File Upload Manager'
                    }
                }
            }
        ],
        'new_js_endpoints': [
            '/api/internal/users',
            '/api/admin/config'
        ],
        'new_takeovers': [],
        'resolved_takeovers': [],
        'timestamp': datetime.now().isoformat()
    }

    # Filter config if specific platform requested
    test_config = config['notifications'].copy()
    if platform:
        for p in ['slack', 'discord', 'telegram', 'email']:
            if p != platform:
                test_config[p]['enabled'] = False

    notifier = Notifier(test_config)

    print(f"{Colors.YELLOW}[*] Sending change alert to configured platforms...{Colors.RESET}\n")
    print(f"Domain: {Colors.CYAN}test-example.com{Colors.RESET}")
    print(f"New Subdomains: {Colors.GREEN}{len(changes['new_subdomains'])}{Colors.RESET}")
    print(f"New Endpoints: {Colors.GREEN}{len(changes['new_endpoints'])}{Colors.RESET}")
    print(f"Changed Endpoints: {Colors.YELLOW}{len(changes['changed_endpoints'])}{Colors.RESET}")
    print(f"New JS Endpoints: {Colors.MAGENTA}{len(changes['new_js_endpoints'])}{Colors.RESET}\n")

    notifier.notify_changes('test-example.com', changes)

    print(f"\n{Colors.GREEN}✓ Change alert sent!{Colors.RESET}")
    print(f"{Colors.YELLOW}Check your configured platforms for the alert.{Colors.RESET}\n")


def test_critical_alert(config, platform=None):
    """Test critical subdomain takeover alert"""
    print(f"\n{Colors.BOLD}{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.RED}Testing CRITICAL Alert (Subdomain Takeover){Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.RED}{'='*70}{Colors.RESET}\n")

    # Create critical changes data
    changes = {
        'new_subdomains': [],
        'removed_subdomains': [],
        'new_endpoints': [],
        'removed_endpoints': [],
        'changed_endpoints': [],
        'new_js_endpoints': [],
        'new_takeovers': [
            {
                'subdomain': 'old-app.test-example.com',
                'service': 'heroku',
                'cname': 'old-app.herokuapp.com',
                'confidence': 'high',
                'fingerprint': 'No such app'
            },
            {
                'subdomain': 'staging-v1.test-example.com',
                'service': 'github',
                'cname': 'staging-v1.github.io',
                'confidence': 'high',
                'fingerprint': 'There isn\'t a GitHub Pages site here'
            }
        ],
        'resolved_takeovers': [],
        'timestamp': datetime.now().isoformat()
    }

    # Filter config if specific platform requested
    test_config = config['notifications'].copy()
    if platform:
        for p in ['slack', 'discord', 'telegram', 'email']:
            if p != platform:
                test_config[p]['enabled'] = False

    notifier = Notifier(test_config)

    print(f"{Colors.RED}[!!!] CRITICAL SECURITY ISSUE DETECTED{Colors.RESET}\n")
    print(f"Domain: {Colors.CYAN}test-example.com{Colors.RESET}")
    print(f"Subdomain Takeovers: {Colors.RED}{len(changes['new_takeovers'])}{Colors.RESET}\n")

    for takeover in changes['new_takeovers']:
        print(f"  {Colors.RED}[!] {takeover['subdomain']}{Colors.RESET}")
        print(f"      Service: {takeover['service']}")
        print(f"      CNAME: {takeover['cname']}")
        print(f"      Confidence: {takeover['confidence']}\n")

    notifier.notify_changes('test-example.com', changes)

    print(f"\n{Colors.RED}✓ CRITICAL alert sent!{Colors.RESET}")
    print(f"{Colors.YELLOW}Check your configured platforms for the CRITICAL alert.{Colors.RESET}\n")


def show_config_status(config):
    """Show configured notification platforms"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}Notification Configuration Status{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    notifications = config.get('notifications', {})

    platforms = {
        'slack': '📢 Slack',
        'discord': '💬 Discord',
        'telegram': '✈️  Telegram',
        'email': '📧 Email'
    }

    for key, name in platforms.items():
        platform_config = notifications.get(key, {})
        enabled = platform_config.get('enabled', False)
        notify_on = platform_config.get('notify_on', [])

        status = f"{Colors.GREEN}ENABLED{Colors.RESET}" if enabled else f"{Colors.RED}DISABLED{Colors.RESET}"
        print(f"{name}: {status}")

        if enabled:
            # Show webhook/config (masked)
            if key == 'slack':
                webhook = platform_config.get('webhook_url', '')
                if webhook:
                    masked = webhook[:30] + '...' + webhook[-10:] if len(webhook) > 40 else webhook
                    print(f"  Webhook: {masked}")
            elif key == 'discord':
                webhook = platform_config.get('webhook_url', '')
                if webhook:
                    masked = webhook[:40] + '...' + webhook[-10:] if len(webhook) > 50 else webhook
                    print(f"  Webhook: {masked}")
            elif key == 'telegram':
                bot_token = platform_config.get('bot_token', '')
                chat_id = platform_config.get('chat_id', '')
                if bot_token:
                    print(f"  Bot Token: {'*' * 20}...{bot_token[-5:]}")
                if chat_id:
                    print(f"  Chat ID: {chat_id}")
            elif key == 'email':
                to_email = platform_config.get('to_email', '')
                smtp_server = platform_config.get('smtp_server', '')
                print(f"  To: {to_email}")
                print(f"  SMTP: {smtp_server}")

            print(f"  Triggers: {', '.join(notify_on) if notify_on else 'none'}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Test real notifications to configured platforms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show configuration status
  ./test_real_notifications.py --show-config

  # Test all notification types to all platforms
  ./test_real_notifications.py --all

  # Test baseline alert only
  ./test_real_notifications.py --baseline

  # Test change alert only
  ./test_real_notifications.py --changes

  # Test critical alert only
  ./test_real_notifications.py --critical

  # Test specific platform
  ./test_real_notifications.py --baseline --platform discord
  ./test_real_notifications.py --changes --platform slack

  # Use specific config file
  ./test_real_notifications.py --all --config config.yaml
        """
    )

    parser.add_argument('-c', '--config', default='config.yaml',
                        help='Path to config file (default: config.yaml)')
    parser.add_argument('--show-config', action='store_true',
                        help='Show notification configuration status')
    parser.add_argument('--baseline', action='store_true',
                        help='Test baseline completion alert')
    parser.add_argument('--changes', action='store_true',
                        help='Test change detection alert')
    parser.add_argument('--critical', action='store_true',
                        help='Test critical subdomain takeover alert')
    parser.add_argument('--all', action='store_true',
                        help='Test all alert types')
    parser.add_argument('--platform', choices=['slack', 'discord', 'telegram', 'email'],
                        help='Test specific platform only')

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Show banner
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}BB-Monitor Real Notification Testing{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}")

    # Show config status
    if args.show_config or not any([args.baseline, args.changes, args.critical, args.all]):
        show_config_status(config)
        if not any([args.baseline, args.changes, args.critical, args.all]):
            print(f"{Colors.YELLOW}Use --help to see testing options{Colors.RESET}\n")
            return

    # Run tests
    if args.all:
        test_baseline_alert(config, args.platform)
        test_change_alert(config, args.platform)
        test_critical_alert(config, args.platform)
    else:
        if args.baseline:
            test_baseline_alert(config, args.platform)
        if args.changes:
            test_change_alert(config, args.platform)
        if args.critical:
            test_critical_alert(config, args.platform)

    # Final summary
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}Testing Complete!{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}\n")

    print(f"{Colors.CYAN}Next Steps:{Colors.RESET}")
    print(f"1. Check your configured notification platforms")
    print(f"2. Verify the alerts were received")
    print(f"3. Confirm the formatting looks correct")
    print(f"4. Test with real monitoring: ./monitor.py --init\n")


if __name__ == '__main__':
    main()
