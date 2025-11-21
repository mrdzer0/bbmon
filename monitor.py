#!/usr/bin/env python3
"""
Bug Bounty Change Monitoring System
Tracks changes in target infrastructure, web apps, and attack surface
"""

import os
import sys
import json
import yaml
import hashlib
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any
import difflib
from collections import defaultdict

# Import enhanced modules
try:
    from modules.subdomain_finder import SubdomainFinder
    ENHANCED_SUBDOMAIN = True
except ImportError:
    ENHANCED_SUBDOMAIN = False

try:
    from modules.http_monitor import HTTPMonitor
    ENHANCED_HTTP = True
except ImportError:
    ENHANCED_HTTP = False

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class BBMonitor:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self.load_config(config_path)
        self.setup_directories()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.changes = defaultdict(list)

    def _json_safe(self, data: Any) -> Any:
        """Recursively convert sets and other non-JSON types to JSON-safe types."""
        if isinstance(data, dict):
            return {str(k): self._json_safe(v) for k, v in data.items()}
        elif isinstance(data, (set, list, tuple)):
            return [self._json_safe(v) for v in data]
        else:
            # tipe primitif (str, int, float, bool, None) langsung balikin
            return data

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"{Colors.RED}[!] Error loading config: {e}{Colors.RESET}")
            sys.exit(1)

    def setup_directories(self):
        """Create necessary directories"""
        dirs = [
            self.config['monitoring']['data_dir'],
            self.config['monitoring']['baseline_dir'],
            self.config['monitoring']['diff_dir'],
            self.config['monitoring']['reports_dir']
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)

    def get_targets(self) -> List[str]:
        """Get list of target domains"""
        targets = []

        # From config file
        if 'domains' in self.config['targets']:
            targets.extend(self.config['targets']['domains'])

        # From file
        if 'domains_file' in self.config['targets']:
            try:
                with open(self.config['targets']['domains_file'], 'r') as f:
                    targets.extend([line.strip() for line in f if line.strip()])
            except FileNotFoundError:
                pass

        return list(set(targets))  # Remove duplicates

    def run_command(self, cmd: str, timeout: int = 300) -> str:
        """Execute shell command and return output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}[!] Command timeout: {cmd}{Colors.RESET}")
            return ""
        except Exception as e:
            print(f"{Colors.RED}[!] Command error: {e}{Colors.RESET}")
            return ""

    def hash_content(self, content: str) -> str:
        """Generate hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def discover_subdomains(self, domain: str) -> Dict[str, Any]:
        """Discover subdomains using multiple tools (enhanced version)"""
        print(f"{Colors.BLUE}[*] Discovering subdomains for {domain}...{Colors.RESET}")

        # Use enhanced subdomain finder if available
        if ENHANCED_SUBDOMAIN:
            output_dir = Path(self.config['monitoring']['data_dir']) / 'subdomain_scans' / domain
            output_dir.mkdir(parents=True, exist_ok=True)

            finder = SubdomainFinder(domain, str(output_dir))
            results = finder.run_all(check_takeover=True)

            print(f"{Colors.GREEN}[+] Found {len(results['subdomains'])} subdomains{Colors.RESET}")

            # Return both subdomains and takeover info
            return {
                'subdomains': results['subdomains'],
                'takeovers': results.get('takeovers', []),
                'dns_results': results.get('dns_results', {}),
                'by_source': results.get('by_source', {})
            }
        else:
            # Fallback to basic discovery
            subdomains = set()

            # Subfinder
            if self.config['tools']['subfinder']['enabled']:
                output = self.run_command(
                    f"subfinder -d {domain} -silent",
                    timeout=self.config['tools']['subfinder']['timeout']
                )
                subdomains.update(output.strip().split('\n'))

            # Amass (passive)
            if self.config['tools']['amass']['enabled'] and self.config['tools']['amass']['passive']:
                output = self.run_command(
                    f"amass enum -passive -d {domain}",
                    timeout=self.config['tools']['amass']['timeout']
                )
                subdomains.update(output.strip().split('\n'))

            # Remove empty strings
            subdomains.discard('')

            print(f"{Colors.GREEN}[+] Found {len(subdomains)} subdomains{Colors.RESET}")
            return {
                'subdomains': subdomains,
                'takeovers': [],
                'dns_results': {},
                'by_source': {}
            }

    def probe_http(self, subdomains: Set[str]) -> Dict[str, Any]:
        """Probe HTTP/HTTPS endpoints (enhanced version)"""
        print(f"{Colors.BLUE}[*] Probing HTTP endpoints...{Colors.RESET}")

        # Use enhanced HTTP monitor if available
        if ENHANCED_HTTP:
            # Prepare URLs (try both http and https)
            urls = []
            for subdomain in subdomains:
                if not subdomain.startswith('http'):
                    urls.append(f"https://{subdomain}")
                else:
                    urls.append(subdomain)

            # Use HTTPMonitor
            http_monitor = HTTPMonitor(str(Path(self.config['monitoring']['data_dir']) / 'http_snapshots'))
            results_dict = http_monitor.probe_multiple(urls, parallel=True)

            # Convert to compatible format
            results = {}
            for url, data in results_dict.items():
                if data.get('reachable'):
                    results[url] = {
                        'status_code': data.get('status_code'),
                        'title': data.get('title'),
                        'content_length': data.get('body_length'),  # Changed from 'content_length'
                        'body_length': data.get('body_length'),      # Added for compatibility
                        'technologies': data.get('technologies', []),
                        'headers': data.get('headers', {}),
                        'server': data.get('server', ''),
                        'content_hash': data.get('content_hash', ''),
                        'flags': data.get('flags', []),
                        'redirects': data.get('redirects', [])
                    }

            print(f"{Colors.GREEN}[+] Found {len(results)} live endpoints{Colors.RESET}")

            # Print high-value flags
            high_value_count = sum(1 for r in results.values() for f in r.get('flags', []) if f.get('severity') == 'high')
            if high_value_count > 0:
                print(f"{Colors.RED}[!] Found {high_value_count} high-value targets{Colors.RESET}")

            return results
        else:
            # Fallback to httpx-based probing
            # Write subdomains to temp file
            temp_file = f"/tmp/subs_{self.timestamp}.txt"
            with open(temp_file, 'w') as f:
                f.write('\n'.join(subdomains))

            # Run httpx
            output = self.run_command(
                f"httpx -l {temp_file} -silent -json -tech-detect -status-code -title -content-length",
                timeout=600
            )

            # Clean up
            os.remove(temp_file)

            # Parse JSON output
            results = {}
            for line in output.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        url = data.get('url', '')
                        if url:
                            results[url] = {
                                'status_code': data.get('status_code'),
                                'title': data.get('title'),
                                'content_length': data.get('content_length'),
                                'technologies': data.get('tech', []),
                                'headers': data.get('headers', {}),
                            }
                    except json.JSONDecodeError:
                        continue

            print(f"{Colors.GREEN}[+] Found {len(results)} live endpoints{Colors.RESET}")
            return results

    def get_page_content(self, url: str) -> str:
        """Get page content using curl"""
        return self.run_command(f"curl -sL -m 10 '{url}'", timeout=15)

    def extract_js_endpoints(self, js_url: str) -> Set[str]:
        """Extract endpoints from JavaScript files"""
        content = self.get_page_content(js_url)

        # Simple regex-based extraction (you can use LinkFinder for better results)
        import re
        endpoints = set()

        # Find URL patterns
        patterns = [
            r'["\']([/][a-zA-Z0-9/_-]+)["\']',
            r'["\']https?://[^"\']+["\']',
            r'url:\s*["\']([^"\']+)["\']',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            endpoints.update(matches)

        return endpoints

    def crawl_endpoints(self, url: str) -> Set[str]:
        """Crawl website to discover endpoints"""
        if not self.config['tools']['katana']['enabled']:
            return set()

        print(f"{Colors.BLUE}[*] Crawling {url}...{Colors.RESET}")
        output = self.run_command(
            f"katana -u '{url}' -silent -d {self.config['tools']['katana']['depth']} -jc -kf all",
            timeout=self.config['tools']['katana']['timeout']
        )

        endpoints = set(output.strip().split('\n'))
        endpoints.discard('')

        return endpoints

    def collect_baseline(self, domain: str) -> Dict[str, Any]:
        """Collect baseline data for a domain"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}Collecting baseline for: {domain}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

        baseline = {
            'domain': domain,
            'timestamp': self.timestamp,
            'subdomains': {},
            'endpoints': {},
            'javascript_files': {},
            'crawled_urls': {},
            'subdomain_takeovers': [],
            'dns_info': {}
        }

        # 1. Discover subdomains (enhanced)
        if self.config['checks']['infrastructure']['subdomain_discovery']:
            subdomain_results = self.discover_subdomains(domain)
            subdomains = subdomain_results['subdomains']
            baseline['subdomains'] = {sub: True for sub in subdomains}
            baseline['subdomain_takeovers'] = subdomain_results.get('takeovers', [])
            baseline['dns_info'] = subdomain_results.get('dns_results', {})
        else:
            subdomains = {domain}

        # 2. Probe HTTP
        if self.config['checks']['web_application']['http_responses']:
            http_results = self.probe_http(subdomains)
            baseline['endpoints'] = http_results

        # 3. Crawl endpoints and analyze JS
        for url, data in baseline['endpoints'].items():
            # Crawl
            if self.config['checks']['content_discovery']['enabled']:
                crawled = self.crawl_endpoints(url)
                baseline['crawled_urls'][url] = list(crawled)

                # Find JS files
                js_files = [u for u in crawled if u.endswith('.js')]
                for js_file in js_files[:10]:  # Limit to 10 JS files per domain
                    endpoints = self.extract_js_endpoints(js_file)
                    baseline['javascript_files'][js_file] = {
                        'endpoints': list(endpoints),
                        'hash': self.hash_content(self.get_page_content(js_file))
                    }

        return baseline

    def save_baseline(self, domain: str, baseline: Dict[str, Any]):
        """Save baseline data to file"""
        baseline_file = Path(self.config['monitoring']['baseline_dir']) / f"{domain}_baseline.json"
        safe_baseline = self._json_safe(baseline)
        with open(baseline_file, 'w') as f:
            json.dump(safe_baseline, f, indent=2)
        print(f"{Colors.GREEN}[+] Baseline saved: {baseline_file}{Colors.RESET}")


    def load_baseline(self, domain: str) -> Dict[str, Any]:
        """Load baseline data from file"""
        baseline_file = Path(self.config['monitoring']['baseline_dir']) / f"{domain}_baseline.json"

        if not baseline_file.exists():
            return None

        with open(baseline_file, 'r') as f:
            return json.load(f)

    def compare_baselines(self, domain: str, old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two baselines and identify changes"""
        print(f"\n{Colors.BLUE}[*] Comparing baselines for {domain}...{Colors.RESET}")

        changes = {
            'new_subdomains': [],
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

        # Compare subdomains
        old_subs = set(old.get('subdomains', {}).keys())
        new_subs = set(new.get('subdomains', {}).keys())
        changes['new_subdomains'] = list(new_subs - old_subs)
        changes['removed_subdomains'] = list(old_subs - new_subs)

        # Compare subdomain takeovers
        old_takeovers = {t['subdomain']: t for t in old.get('subdomain_takeovers', [])}
        new_takeovers = {t['subdomain']: t for t in new.get('subdomain_takeovers', [])}
        changes['new_takeovers'] = [new_takeovers[sub] for sub in set(new_takeovers.keys()) - set(old_takeovers.keys())]
        changes['resolved_takeovers'] = list(set(old_takeovers.keys()) - set(new_takeovers.keys()))

        # Compare endpoints
        old_endpoints = set(old.get('endpoints', {}).keys())
        new_endpoints = set(new.get('endpoints', {}).keys())
        changes['new_endpoints'] = list(new_endpoints - old_endpoints)
        changes['removed_endpoints'] = list(old_endpoints - new_endpoints)

        # Compare endpoint details (enhanced with HTTP monitoring data)
        for endpoint in old_endpoints & new_endpoints:
            old_data = old['endpoints'][endpoint]
            new_data = new['endpoints'][endpoint]

            endpoint_changes = {}

            # Status code change
            if old_data.get('status_code') != new_data.get('status_code'):
                endpoint_changes['status_code'] = {
                    'old': old_data.get('status_code'),
                    'new': new_data.get('status_code')
                }

            # Title change
            if old_data.get('title') != new_data.get('title'):
                endpoint_changes['title'] = {
                    'old': old_data.get('title', ''),
                    'new': new_data.get('title', '')
                }

            # Body length change (significant = >10%)
            old_length = old_data.get('body_length', old_data.get('content_length', 0))
            new_length = new_data.get('body_length', new_data.get('content_length', 0))

            if old_length > 0:
                length_diff_percent = abs(new_length - old_length) / old_length * 100
                if length_diff_percent > 10:
                    endpoint_changes['body_length'] = {
                        'old': old_length,
                        'new': new_length,
                        'diff_percent': round(length_diff_percent, 2)
                    }

            # Technology changes
            old_tech = set(old_data.get('technologies', []))
            new_tech = set(new_data.get('technologies', []))

            added_tech = new_tech - old_tech
            removed_tech = old_tech - new_tech

            if added_tech or removed_tech:
                endpoint_changes['technologies'] = {
                    'added': list(added_tech),
                    'removed': list(removed_tech)
                }

            # New high-value flags
            if 'flags' in new_data:
                high_flags = [f for f in new_data['flags'] if f.get('severity') == 'high']
                if high_flags:
                    endpoint_changes['new_flags'] = high_flags

            if endpoint_changes:
                changes['changed_endpoints'].append({
                    'url': endpoint,
                    'changes': endpoint_changes,
                    'old': old_data,
                    'new': new_data
                })

        # Compare JS files
        old_js = set(old.get('javascript_files', {}).keys())
        new_js = set(new.get('javascript_files', {}).keys())
        changes['new_js_files'] = list(new_js - old_js)

        for js_file in old_js & new_js:
            old_hash = old['javascript_files'][js_file]['hash']
            new_hash = new['javascript_files'][js_file]['hash']

            if old_hash != new_hash:
                # JS file changed, check for new endpoints
                old_endpoints_set = set(old['javascript_files'][js_file]['endpoints'])
                new_endpoints_set = set(new['javascript_files'][js_file]['endpoints'])
                new_eps = list(new_endpoints_set - old_endpoints_set)

                if new_eps:
                    changes['changed_js_files'].append(js_file)
                    changes['new_js_endpoints'].extend(new_eps)

        return changes

    def print_changes(self, domain: str, changes: Dict[str, Any]):
        """Print changes in a readable format"""
        has_changes = False

        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}Changes detected for: {domain}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.RESET}\n")

        # New subdomains
        if changes['new_subdomains']:
            has_changes = True
            print(f"{Colors.GREEN}[+] New Subdomains ({len(changes['new_subdomains'])})::{Colors.RESET}")
            for sub in changes['new_subdomains']:
                print(f"  {Colors.GREEN}+ {sub}{Colors.RESET}")

        # Removed subdomains
        if changes['removed_subdomains']:
            has_changes = True
            print(f"\n{Colors.RED}[-] Removed Subdomains ({len(changes['removed_subdomains'])})::{Colors.RESET}")
            for sub in changes['removed_subdomains']:
                print(f"  {Colors.RED}- {sub}{Colors.RESET}")

        # New endpoints
        if changes['new_endpoints']:
            has_changes = True
            print(f"\n{Colors.GREEN}[+] New Endpoints ({len(changes['new_endpoints'])})::{Colors.RESET}")
            for ep in changes['new_endpoints']:
                print(f"  {Colors.GREEN}+ {ep}{Colors.RESET}")

        # Changed endpoints (enhanced display)
        if changes['changed_endpoints']:
            has_changes = True
            print(f"\n{Colors.YELLOW}[~] Changed Endpoints ({len(changes['changed_endpoints'])})::{Colors.RESET}")
            for item in changes['changed_endpoints']:
                print(f"  {Colors.YELLOW}~ {item['url']}{Colors.RESET}")

                # Display changes
                endpoint_changes = item.get('changes', {})

                # Status code
                if 'status_code' in endpoint_changes:
                    sc = endpoint_changes['status_code']
                    print(f"    Status: {sc['old']} → {sc['new']}")

                # Title
                if 'title' in endpoint_changes:
                    tc = endpoint_changes['title']
                    old_title = tc['old'][:50] if tc['old'] else 'None'
                    new_title = tc['new'][:50] if tc['new'] else 'None'
                    print(f"    Title: {old_title} → {new_title}")

                # Body length
                if 'body_length' in endpoint_changes:
                    bl = endpoint_changes['body_length']
                    print(f"    Body Length: {bl['old']} → {bl['new']} ({bl['diff_percent']}% change)")

                # Technologies
                if 'technologies' in endpoint_changes:
                    tc = endpoint_changes['technologies']
                    if tc['added']:
                        print(f"    Tech Added: {', '.join(tc['added'])}")
                    if tc['removed']:
                        print(f"    Tech Removed: {', '.join(tc['removed'])}")

                # High-value flags
                if 'new_flags' in endpoint_changes:
                    for flag in endpoint_changes['new_flags']:
                        print(f"    {Colors.RED}[!] FLAG: {flag.get('message')}{Colors.RESET}")

        # New JS files
        if changes['new_js_files']:
            has_changes = True
            print(f"\n{Colors.GREEN}[+] New JavaScript Files ({len(changes['new_js_files'])})::{Colors.RESET}")
            for js in changes['new_js_files']:
                print(f"  {Colors.GREEN}+ {js}{Colors.RESET}")

        # Changed JS files with new endpoints
        if changes['new_js_endpoints']:
            has_changes = True
            print(f"\n{Colors.MAGENTA}[+] New Endpoints from JS ({len(changes['new_js_endpoints'])})::{Colors.RESET}")
            for ep in changes['new_js_endpoints']:
                print(f"  {Colors.MAGENTA}+ {ep}{Colors.RESET}")

        # New subdomain takeovers (CRITICAL!)
        if changes['new_takeovers']:
            has_changes = True
            print(f"\n{Colors.RED}{Colors.BOLD}[!!!] POTENTIAL SUBDOMAIN TAKEOVERS ({len(changes['new_takeovers'])})::{Colors.RESET}")
            for takeover in changes['new_takeovers']:
                print(f"  {Colors.RED}[!] {takeover['subdomain']}{Colors.RESET}")
                print(f"      Service: {takeover['service']}")
                print(f"      CNAME: {takeover['cname']}")
                print(f"      Confidence: {takeover['confidence']}")
                if 'fingerprint' in takeover:
                    print(f"      Fingerprint: {takeover['fingerprint']}")

        # Resolved takeovers
        if changes['resolved_takeovers']:
            has_changes = True
            print(f"\n{Colors.GREEN}[+] Resolved Takeovers ({len(changes['resolved_takeovers'])})::{Colors.RESET}")
            for sub in changes['resolved_takeovers']:
                print(f"  {Colors.GREEN}+ {sub}{Colors.RESET}")

        if not has_changes:
            print(f"{Colors.BLUE}[*] No significant changes detected{Colors.RESET}")

        print()

    def save_changes(self, domain: str, changes: Dict[str, Any]):
        """Save changes to file"""
        diff_file = Path(self.config['monitoring']['diff_dir']) / f"{domain}_{self.timestamp}.json"
        safe_changes = self._json_safe(changes)
        with open(diff_file, 'w') as f:
            json.dump(safe_changes, f, indent=2)
        print(f"{Colors.GREEN}[+] Changes saved: {diff_file}{Colors.RESET}")


    def generate_report(self, all_changes: Dict[str, Dict[str, Any]]):
        """Generate HTML report"""
        report_file = Path(self.config['monitoring']['reports_dir']) / f"report_{self.timestamp}.html"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bug Bounty Monitoring Report - {self.timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        .domain {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .new {{ color: #28a745; }}
        .removed {{ color: #dc3545; }}
        .changed {{ color: #ffc107; }}
        .section {{ margin: 15px 0; }}
        .count {{ background: #007bff; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.9em; }}
        ul {{ list-style-type: none; padding-left: 20px; }}
        li {{ padding: 5px 0; }}
        .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>Bug Bounty Monitoring Report</h1>
    <div class="summary">
        <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
        <strong>Domains Monitored:</strong> {len(all_changes)}
    </div>
"""

        for domain, changes in all_changes.items():
            html += f'<div class="domain"><h2>{domain}</h2>'

            # New subdomains
            if changes['new_subdomains']:
                html += f'<div class="section"><h3 class="new">New Subdomains <span class="count">{len(changes["new_subdomains"])}</span></h3><ul>'
                for sub in changes['new_subdomains']:
                    html += f'<li class="new">+ {sub}</li>'
                html += '</ul></div>'

            # New endpoints
            if changes['new_endpoints']:
                html += f'<div class="section"><h3 class="new">New Endpoints <span class="count">{len(changes["new_endpoints"])}</span></h3><ul>'
                for ep in changes['new_endpoints']:
                    html += f'<li class="new">+ {ep}</li>'
                html += '</ul></div>'

            # Changed endpoints
            if changes['changed_endpoints']:
                html += f'<div class="section"><h3 class="changed">Changed Endpoints <span class="count">{len(changes["changed_endpoints"])}</span></h3><ul>'
                for item in changes['changed_endpoints']:
                    html += f'<li class="changed">~ {item["url"]}</li>'
                html += '</ul></div>'

            # New JS endpoints
            if changes['new_js_endpoints']:
                html += f'<div class="section"><h3 class="new">New JS Endpoints <span class="count">{len(changes["new_js_endpoints"])}</span></h3><ul>'
                for ep in changes['new_js_endpoints']:
                    html += f'<li class="new">+ {ep}</li>'
                html += '</ul></div>'

            html += '</div>'

        html += '</body></html>'

        with open(report_file, 'w') as f:
            f.write(html)

        print(f"{Colors.GREEN}[+] HTML report generated: {report_file}{Colors.RESET}")

    def run_initial_baseline(self):
        """Run initial baseline collection"""
        targets = self.get_targets()

        if not targets:
            print(f"{Colors.RED}[!] No targets configured{Colors.RESET}")
            return

        print(f"{Colors.BOLD}[*] Starting initial baseline collection for {len(targets)} target(s){Colors.RESET}\n")

        for domain in targets:
            baseline = self.collect_baseline(domain)
            self.save_baseline(domain, baseline)

    def run_monitoring(self):
        """Run monitoring and compare with baseline"""
        targets = self.get_targets()
        all_changes = {}

        if not targets:
            print(f"{Colors.RED}[!] No targets configured{Colors.RESET}")
            return

        print(f"{Colors.BOLD}[*] Starting monitoring for {len(targets)} target(s){Colors.RESET}\n")

        for domain in targets:
            # Load old baseline
            old_baseline = self.load_baseline(domain)

            if not old_baseline:
                print(f"{Colors.YELLOW}[!] No baseline found for {domain}, creating initial baseline...{Colors.RESET}")
                baseline = self.collect_baseline(domain)
                self.save_baseline(domain, baseline)
                continue

            # Collect new baseline
            new_baseline = self.collect_baseline(domain)

            # Compare
            changes = self.compare_baselines(domain, old_baseline, new_baseline)

            # Print and save changes
            self.print_changes(domain, changes)
            self.save_changes(domain, changes)

            # Update baseline
            self.save_baseline(domain, new_baseline)

            all_changes[domain] = changes

        # Generate report
        if all_changes:
            self.generate_report(all_changes)

def main():
    parser = argparse.ArgumentParser(description='Bug Bounty Change Monitoring System')
    parser.add_argument('-i', '--init', action='store_true', help='Initialize baseline')
    parser.add_argument('-m', '--monitor', action='store_true', help='Run monitoring')
    parser.add_argument('-c', '--config', default='config.yaml', help='Config file path')

    args = parser.parse_args()

    monitor = BBMonitor(config_path=args.config)

    if args.init:
        monitor.run_initial_baseline()
    elif args.monitor:
        monitor.run_monitoring()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
