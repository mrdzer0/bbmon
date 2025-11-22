#!/usr/bin/env python3
"""
Notification module for Bug Bounty Monitoring
Supports: Slack, Discord, Telegram, Email
"""

import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List

class Notifier:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def should_notify(self, change_type: str, notification_config: Dict) -> bool:
        """Check if this change type should trigger notification"""
        return change_type in notification_config.get('notify_on', [])

    def send_slack(self, message: str, changes: Dict[str, Any]):
        """Send notification to Slack"""
        if not self.config['slack']['enabled']:
            return

        webhook_url = self.config['slack']['webhook_url']

        # Build rich Slack message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔍 Bug Bounty Changes Detected"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]

        # Add sections for each change type
        if changes.get('new_subdomains'):
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*New Subdomains:*\n{len(changes['new_subdomains'])}"
                    }
                ]
            })

        if changes.get('new_endpoints'):
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*New Endpoints:*\n{len(changes['new_endpoints'])}"
                    }
                ]
            })

        payload = {
            "blocks": blocks
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                print("[+] Slack notification sent")
            else:
                print(f"[!] Slack notification failed: {response.status_code}")
        except Exception as e:
            print(f"[!] Slack notification error: {e}")

    def send_discord(self, message: str, changes: Dict[str, Any]):
        """Send notification to Discord"""
        if not self.config['discord']['enabled']:
            return

        webhook_url = self.config['discord']['webhook_url']

        # Build Discord embed
        embed = {
            "title": "🔍 Bug Bounty Changes Detected",
            "description": message,
            "color": 3447003,  # Blue
            "fields": []
        }

        if changes.get('new_subdomains'):
            embed["fields"].append({
                "name": "New Subdomains",
                "value": str(len(changes['new_subdomains'])),
                "inline": True
            })

        if changes.get('new_endpoints'):
            embed["fields"].append({
                "name": "New Endpoints",
                "value": str(len(changes['new_endpoints'])),
                "inline": True
            })

        if changes.get('new_js_endpoints'):
            embed["fields"].append({
                "name": "New JS Endpoints",
                "value": str(len(changes['new_js_endpoints'])),
                "inline": True
            })

        payload = {
            "embeds": [embed]
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                print("[+] Discord notification sent")
            else:
                print(f"[!] Discord notification failed: {response.status_code}")
        except Exception as e:
            print(f"[!] Discord notification error: {e}")

    def send_telegram(self, message: str, changes: Dict[str, Any]):
        """Send notification to Telegram"""
        if not self.config['telegram']['enabled']:
            return

        bot_token = self.config['telegram']['bot_token']
        chat_id = self.config['telegram']['chat_id']

        # Build formatted message
        text = f"🔍 *Bug Bounty Changes Detected*\n\n{message}\n\n"

        if changes.get('new_subdomains'):
            text += f"*New Subdomains:* {len(changes['new_subdomains'])}\n"
            # Show first 5
            for sub in changes['new_subdomains'][:5]:
                text += f"  • {sub}\n"
            if len(changes['new_subdomains']) > 5:
                text += f"  ... and {len(changes['new_subdomains']) - 5} more\n"

        if changes.get('new_endpoints'):
            text += f"\n*New Endpoints:* {len(changes['new_endpoints'])}\n"
            for ep in changes['new_endpoints'][:5]:
                text += f"  • {ep}\n"
            if len(changes['new_endpoints']) > 5:
                text += f"  ... and {len(changes['new_endpoints']) - 5} more\n"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("[+] Telegram notification sent")
            else:
                print(f"[!] Telegram notification failed: {response.status_code}")
        except Exception as e:
            print(f"[!] Telegram notification error: {e}")

    def send_email(self, subject: str, message: str, changes: Dict[str, Any]):
        """Send email notification"""
        if not self.config['email']['enabled']:
            return

        smtp_server = self.config['email']['smtp_server']
        smtp_port = self.config['email']['smtp_port']
        username = self.config['email']['username']
        password = self.config['email']['password']
        to_email = self.config['email']['to_email']

        # Create HTML email
        html = f"""
        <html>
        <body>
            <h2>🔍 Bug Bounty Changes Detected</h2>
            <p>{message}</p>
            <hr>
        """

        if changes.get('new_subdomains'):
            html += f"<h3>New Subdomains ({len(changes['new_subdomains'])})</h3><ul>"
            for sub in changes['new_subdomains']:
                html += f"<li>{sub}</li>"
            html += "</ul>"

        if changes.get('new_endpoints'):
            html += f"<h3>New Endpoints ({len(changes['new_endpoints'])})</h3><ul>"
            for ep in changes['new_endpoints']:
                html += f"<li>{ep}</li>"
            html += "</ul>"

        html += "</body></html>"

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = to_email

        html_part = MIMEText(html, 'html')
        msg.attach(html_part)

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            print("[+] Email notification sent")
        except Exception as e:
            print(f"[!] Email notification error: {e}")

    def send_baseline_alert(self, domain: str, baseline: Dict[str, Any]):
        """Send notification for completed baseline scan with crucial data"""

        # Extract key metrics
        total_subdomains = len(baseline.get('subdomains', {}))
        total_endpoints = len(baseline.get('endpoints', {}))
        live_endpoints = sum(1 for url, data in baseline.get('endpoints', {}).items()
                            if data.get('status_code'))

        # Count HTTP status categories
        status_2xx = sum(1 for data in baseline.get('endpoints', {}).values()
                        if 200 <= data.get('status_code', 0) < 300)
        status_3xx = sum(1 for data in baseline.get('endpoints', {}).values()
                        if 300 <= data.get('status_code', 0) < 400)
        status_4xx = sum(1 for data in baseline.get('endpoints', {}).values()
                        if 400 <= data.get('status_code', 0) < 500)
        status_5xx = sum(1 for data in baseline.get('endpoints', {}).values()
                        if 500 <= data.get('status_code', 0) < 600)

        # Subdomain takeovers
        takeovers = baseline.get('subdomain_takeovers', [])

        # High-value targets (from flags)
        high_value_urls = []
        for url, data in baseline.get('endpoints', {}).items():
            flags = data.get('flags', [])
            if any('high-value' in str(flag).lower() or 'admin' in str(flag).lower()
                   or 'upload' in str(flag).lower() for flag in flags):
                high_value_urls.append(url)

        # Shodan data
        shodan_data = baseline.get('shodan_data', {})
        shodan_summary = shodan_data.get('summary', {})

        # Wayback data
        wayback_data = baseline.get('wayback_data', {})
        wayback_stats = wayback_data.get('statistics', {})

        # Build comprehensive message
        summary = {
            'domain': domain,
            'timestamp': baseline.get('timestamp', 'N/A'),
            'subdomains': {
                'total': total_subdomains,
                'list': list(baseline.get('subdomains', {}).keys())[:20]  # First 20
            },
            'endpoints': {
                'total': total_endpoints,
                'live': live_endpoints,
                'status_2xx': status_2xx,
                'status_3xx': status_3xx,
                'status_4xx': status_4xx,
                'status_5xx': status_5xx
            },
            'security': {
                'subdomain_takeovers': len(takeovers),
                'high_value_targets': len(high_value_urls),
                'takeover_list': takeovers[:5],  # First 5
                'high_value_list': high_value_urls[:10]  # First 10
            },
            'shodan': {
                'enabled': bool(shodan_data),
                'hosts_scanned': shodan_summary.get('total_hosts', 0),
                'with_vulnerabilities': shodan_summary.get('with_vulnerabilities', 0),
                'high_value_hosts': shodan_summary.get('high_value_hosts', 0)
            },
            'wayback': {
                'enabled': bool(wayback_data),
                'total_urls': wayback_data.get('total_urls', 0),
                'critical_urls': wayback_stats.get('by_priority', {}).get('critical', 0),
                'high_priority_urls': wayback_stats.get('by_priority', {}).get('high', 0),
                'categories': wayback_stats.get('by_category', {})
            }
        }

        # Send to configured channels
        if self.config.get('slack', {}).get('enabled'):
            if 'baseline_complete' in self.config['slack'].get('notify_on', []):
                self._send_slack_baseline(summary)

        if self.config.get('discord', {}).get('enabled'):
            if 'baseline_complete' in self.config['discord'].get('notify_on', []):
                self._send_discord_baseline(summary)

        if self.config.get('telegram', {}).get('enabled'):
            if 'baseline_complete' in self.config['telegram'].get('notify_on', []):
                self._send_telegram_baseline(summary)

        if self.config.get('email', {}).get('enabled'):
            if 'baseline_complete' in self.config['email'].get('notify_on', []):
                self._send_email_baseline(summary)

    def _send_slack_baseline(self, summary: Dict[str, Any]):
        """Send baseline summary to Slack"""
        webhook_url = self.config['slack']['webhook_url']

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Baseline Scan Complete: {summary['domain']}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*🌐 Subdomains:* {summary['subdomains']['total']}"},
                    {"type": "mrkdwn", "text": f"*🔗 Endpoints:* {summary['endpoints']['total']}"},
                    {"type": "mrkdwn", "text": f"*✅ Live:* {summary['endpoints']['live']}"},
                    {"type": "mrkdwn", "text": f"*🔴 Errors (5xx):* {summary['endpoints']['status_5xx']}"}
                ]
            },
            {"type": "divider"}
        ]

        # HTTP Status breakdown
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*HTTP Status:*\n• 2xx (Success): {summary['endpoints']['status_2xx']}\n• 3xx (Redirect): {summary['endpoints']['status_3xx']}\n• 4xx (Client Error): {summary['endpoints']['status_4xx']}\n• 5xx (Server Error): {summary['endpoints']['status_5xx']}"
            }
        })

        # Security findings
        if summary['security']['subdomain_takeovers'] > 0 or summary['security']['high_value_targets'] > 0:
            blocks.append({"type": "divider"})
            security_text = "*🔒 Security Findings:*\n"

            if summary['security']['subdomain_takeovers'] > 0:
                security_text += f"• ⚠️ Subdomain Takeovers: {summary['security']['subdomain_takeovers']}\n"
                for takeover in summary['security']['takeover_list']:
                    security_text += f"  - {takeover.get('subdomain', 'N/A')} ({takeover.get('service', 'unknown')})\n"

            if summary['security']['high_value_targets'] > 0:
                security_text += f"• 🎯 High-Value Targets: {summary['security']['high_value_targets']}\n"
                for url in summary['security']['high_value_list'][:5]:
                    security_text += f"  - {url}\n"

            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": security_text}})

        # Shodan findings
        if summary['shodan']['enabled']:
            blocks.append({"type": "divider"})
            shodan_text = f"*🛰️ Shodan Results:*\n• Hosts Scanned: {summary['shodan']['hosts_scanned']}\n• With Vulnerabilities: {summary['shodan']['with_vulnerabilities']}\n• High-Value Hosts: {summary['shodan']['high_value_hosts']}"
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": shodan_text}})

        # Wayback findings
        if summary['wayback']['enabled'] and summary['wayback']['total_urls'] > 0:
            blocks.append({"type": "divider"})
            wayback_text = f"*📜 Wayback Machine:*\n• Total URLs: {summary['wayback']['total_urls']}\n• Critical: {summary['wayback']['critical_urls']}\n• High Priority: {summary['wayback']['high_priority_urls']}"

            if summary['wayback']['categories']:
                wayback_text += "\n• Categories:"
                for cat, count in list(summary['wayback']['categories'].items())[:5]:
                    wayback_text += f"\n  - {cat}: {count}"

            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": wayback_text}})

        # Subdomain list (first 20)
        if summary['subdomains']['list']:
            blocks.append({"type": "divider"})
            sub_text = f"*Discovered Subdomains (showing {min(20, len(summary['subdomains']['list']))}/{summary['subdomains']['total']}):*\n"
            sub_text += "\n".join([f"• {sub}" for sub in summary['subdomains']['list'][:20]])
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": sub_text}})

        blocks.append({
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"_Scan completed: {summary['timestamp']}_"}]
        })

        payload = {"blocks": blocks}

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                print("[+] Baseline alert sent to Slack")
            else:
                print(f"[!] Slack baseline alert failed: {response.status_code}")
        except Exception as e:
            print(f"[!] Slack baseline alert error: {e}")

    def _send_discord_baseline(self, summary: Dict[str, Any]):
        """Send baseline summary to Discord"""
        webhook_url = self.config['discord']['webhook_url']

        description = f"**Baseline scan completed for {summary['domain']}**\n\n"
        description += f"**🌐 Subdomains:** {summary['subdomains']['total']}\n"
        description += f"**🔗 Endpoints:** {summary['endpoints']['total']} ({summary['endpoints']['live']} live)\n"

        fields = [
            {"name": "✅ 2xx Success", "value": str(summary['endpoints']['status_2xx']), "inline": True},
            {"name": "↩️ 3xx Redirect", "value": str(summary['endpoints']['status_3xx']), "inline": True},
            {"name": "❌ 4xx Client Error", "value": str(summary['endpoints']['status_4xx']), "inline": True},
            {"name": "🔴 5xx Server Error", "value": str(summary['endpoints']['status_5xx']), "inline": True}
        ]

        # Security findings
        if summary['security']['subdomain_takeovers'] > 0:
            fields.append({
                "name": "⚠️ Subdomain Takeovers",
                "value": str(summary['security']['subdomain_takeovers']),
                "inline": True
            })

        if summary['security']['high_value_targets'] > 0:
            fields.append({
                "name": "🎯 High-Value Targets",
                "value": str(summary['security']['high_value_targets']),
                "inline": True
            })

        # Shodan
        if summary['shodan']['enabled']:
            fields.append({
                "name": "🛰️ Shodan - Hosts Scanned",
                "value": str(summary['shodan']['hosts_scanned']),
                "inline": True
            })
            fields.append({
                "name": "🛰️ Shodan - With Vulns",
                "value": str(summary['shodan']['with_vulnerabilities']),
                "inline": True
            })

        # Wayback
        if summary['wayback']['enabled'] and summary['wayback']['total_urls'] > 0:
            fields.append({
                "name": "📜 Wayback URLs",
                "value": f"{summary['wayback']['total_urls']} (Critical: {summary['wayback']['critical_urls']})",
                "inline": True
            })

        # Subdomains list
        if summary['subdomains']['list']:
            sub_list = "\n".join([f"• {sub}" for sub in summary['subdomains']['list'][:15]])
            if len(summary['subdomains']['list']) > 15:
                sub_list += f"\n... and {len(summary['subdomains']['list']) - 15} more"
            fields.append({
                "name": f"Discovered Subdomains ({summary['subdomains']['total']})",
                "value": sub_list,
                "inline": False
            })

        embed = {
            "title": f"📊 Baseline Scan Complete",
            "description": description,
            "color": 3066993,  # Green
            "fields": fields,
            "footer": {"text": f"Completed: {summary['timestamp']}"}
        }

        payload = {"embeds": [embed]}

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                print("[+] Baseline alert sent to Discord")
            else:
                print(f"[!] Discord baseline alert failed: {response.status_code}")
        except Exception as e:
            print(f"[!] Discord baseline alert error: {e}")

    def _send_telegram_baseline(self, summary: Dict[str, Any]):
        """Send baseline summary to Telegram"""
        bot_token = self.config['telegram']['bot_token']
        chat_id = self.config['telegram']['chat_id']

        text = f"📊 *Baseline Scan Complete*\n\n"
        text += f"*Domain:* {summary['domain']}\n\n"

        text += f"🌐 *Subdomains:* {summary['subdomains']['total']}\n"
        text += f"🔗 *Endpoints:* {summary['endpoints']['total']} ({summary['endpoints']['live']} live)\n\n"

        text += "*HTTP Status:*\n"
        text += f"  ✅ 2xx: {summary['endpoints']['status_2xx']}\n"
        text += f"  ↩️ 3xx: {summary['endpoints']['status_3xx']}\n"
        text += f"  ❌ 4xx: {summary['endpoints']['status_4xx']}\n"
        text += f"  🔴 5xx: {summary['endpoints']['status_5xx']}\n\n"

        if summary['security']['subdomain_takeovers'] > 0:
            text += f"⚠️ *Subdomain Takeovers:* {summary['security']['subdomain_takeovers']}\n"

        if summary['security']['high_value_targets'] > 0:
            text += f"🎯 *High-Value Targets:* {summary['security']['high_value_targets']}\n"

        if summary['shodan']['enabled']:
            text += f"\n🛰️ *Shodan:*\n"
            text += f"  Hosts: {summary['shodan']['hosts_scanned']}\n"
            text += f"  With Vulns: {summary['shodan']['with_vulnerabilities']}\n"

        if summary['wayback']['enabled'] and summary['wayback']['total_urls'] > 0:
            text += f"\n📜 *Wayback:*\n"
            text += f"  URLs: {summary['wayback']['total_urls']}\n"
            text += f"  Critical: {summary['wayback']['critical_urls']}\n"

        if summary['subdomains']['list']:
            text += f"\n*Subdomains (showing 10/{summary['subdomains']['total']}):*\n"
            for sub in summary['subdomains']['list'][:10]:
                text += f"  • {sub}\n"

        text += f"\n_Completed: {summary['timestamp']}_"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("[+] Baseline alert sent to Telegram")
            else:
                print(f"[!] Telegram baseline alert failed: {response.status_code}")
        except Exception as e:
            print(f"[!] Telegram baseline alert error: {e}")

    def _send_email_baseline(self, summary: Dict[str, Any]):
        """Send baseline summary via Email"""
        smtp_server = self.config['email']['smtp_server']
        smtp_port = self.config['email']['smtp_port']
        username = self.config['email']['username']
        password = self.config['email']['password']
        to_email = self.config['email']['to_email']

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #4CAF50; color: white; padding: 15px; }}
                .section {{ margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #4CAF50; }}
                .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #4CAF50; }}
                .metric-label {{ font-size: 14px; color: #666; }}
                .warning {{ color: #ff9800; }}
                .critical {{ color: #f44336; }}
                ul {{ list-style-type: none; padding-left: 0; }}
                li {{ padding: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Baseline Scan Complete</h1>
                <p>Domain: {summary['domain']}</p>
            </div>

            <div class="section">
                <h2>Overview</h2>
                <div class="metric">
                    <div class="metric-value">{summary['subdomains']['total']}</div>
                    <div class="metric-label">Subdomains</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary['endpoints']['total']}</div>
                    <div class="metric-label">Endpoints</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary['endpoints']['live']}</div>
                    <div class="metric-label">Live Endpoints</div>
                </div>
            </div>

            <div class="section">
                <h2>HTTP Status Distribution</h2>
                <ul>
                    <li>✅ 2xx (Success): {summary['endpoints']['status_2xx']}</li>
                    <li>↩️ 3xx (Redirect): {summary['endpoints']['status_3xx']}</li>
                    <li>❌ 4xx (Client Error): {summary['endpoints']['status_4xx']}</li>
                    <li class="warning">🔴 5xx (Server Error): {summary['endpoints']['status_5xx']}</li>
                </ul>
            </div>
        """

        if summary['security']['subdomain_takeovers'] > 0 or summary['security']['high_value_targets'] > 0:
            html += '<div class="section"><h2 class="critical">🔒 Security Findings</h2><ul>'
            if summary['security']['subdomain_takeovers'] > 0:
                html += f'<li class="critical">⚠️ Subdomain Takeovers: {summary["security"]["subdomain_takeovers"]}</li>'
            if summary['security']['high_value_targets'] > 0:
                html += f'<li class="warning">🎯 High-Value Targets: {summary["security"]["high_value_targets"]}</li>'
            html += '</ul></div>'

        if summary['shodan']['enabled']:
            html += f'''
            <div class="section">
                <h2>🛰️ Shodan Results</h2>
                <ul>
                    <li>Hosts Scanned: {summary['shodan']['hosts_scanned']}</li>
                    <li>With Vulnerabilities: {summary['shodan']['with_vulnerabilities']}</li>
                    <li>High-Value Hosts: {summary['shodan']['high_value_hosts']}</li>
                </ul>
            </div>
            '''

        if summary['wayback']['enabled'] and summary['wayback']['total_urls'] > 0:
            html += f'''
            <div class="section">
                <h2>📜 Wayback Machine</h2>
                <ul>
                    <li>Total URLs: {summary['wayback']['total_urls']}</li>
                    <li>Critical: {summary['wayback']['critical_urls']}</li>
                    <li>High Priority: {summary['wayback']['high_priority_urls']}</li>
                </ul>
            </div>
            '''

        if summary['subdomains']['list']:
            html += f'''
            <div class="section">
                <h2>Discovered Subdomains (showing 20/{summary['subdomains']['total']})</h2>
                <ul>
            '''
            for sub in summary['subdomains']['list'][:20]:
                html += f'<li>• {sub}</li>'
            html += '</ul></div>'

        html += f'<p style="color: #666; font-size: 12px;">Scan completed: {summary["timestamp"]}</p>'
        html += '</body></html>'

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Baseline Scan Complete: {summary['domain']}"
        msg['From'] = username
        msg['To'] = to_email

        html_part = MIMEText(html, 'html')
        msg.attach(html_part)

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            print("[+] Baseline alert sent via Email")
        except Exception as e:
            print(f"[!] Email baseline alert error: {e}")

    def notify_changes(self, domain: str, changes: Dict[str, Any]):
        """Send notifications for detected changes"""
        if not any([
            changes.get('new_subdomains'),
            changes.get('new_endpoints'),
            changes.get('changed_endpoints'),
            changes.get('new_js_endpoints')
        ]):
            return

        message = f"Changes detected for domain: *{domain}*"

        # Determine priority
        high_priority = False
        if changes.get('new_subdomains') or changes.get('new_endpoints'):
            high_priority = True

        # Send notifications
        if self.config['slack']['enabled']:
            if high_priority or 'all' in self.config['slack']['notify_on']:
                self.send_slack(message, changes)

        if self.config['discord']['enabled']:
            if high_priority or 'all' in self.config['discord']['notify_on']:
                self.send_discord(message, changes)

        if self.config['telegram']['enabled']:
            if high_priority or 'all' in self.config['telegram']['notify_on']:
                self.send_telegram(message, changes)

        if self.config['email']['enabled']:
            if high_priority:
                self.send_email(
                    f"Bug Bounty Changes: {domain}",
                    message,
                    changes
                )
