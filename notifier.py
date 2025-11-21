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
