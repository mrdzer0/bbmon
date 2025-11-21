#!/usr/bin/env python3
"""
HTTP Monitoring Module
Tracks: URL, Status Code, Body Length, Title, Technology, Content Changes
Flags: admin, backup, login, outdated tech, and other high-value targets
"""

import os
import sys
import json
import requests
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from urllib.parse import urlparse
import subprocess
from bs4 import BeautifulSoup
from datetime import datetime

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class HTTPMonitor:
    def __init__(self, output_dir: str = "./http_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # High-value keywords to flag
        self.high_value_keywords = {
            'admin': ['admin', 'administrator', 'console', 'dashboard', 'panel', 'manage'],
            'auth': ['login', 'signin', 'authenticate', 'auth', 'sso', 'oauth'],
            'backup': ['backup', 'bak', 'old', 'archive', 'dump', 'sql'],
            'dev': ['dev', 'development', 'test', 'staging', 'debug', 'beta'],
            'api': ['api', 'graphql', 'rest', 'endpoint', 'swagger', 'docs'],
            'upload': ['upload', 'uploader', 'file', 'attachment', 'media'],
            'sensitive': ['config', 'env', 'secret', 'key', 'token', 'password'],
            'internal': ['internal', 'private', 'corp', 'vpn', 'intranet']
        }

        # Outdated/vulnerable technology versions
        self.outdated_tech = {
            'Apache': ['2.4.49', '2.4.50'],  # Path traversal CVEs
            'nginx': ['1.18.0', '1.19.0'],
            'PHP': ['7.3', '7.4', '5.6'],
            'WordPress': ['5.8', '5.9'],
            'jQuery': ['1.', '2.', '3.0', '3.1', '3.2'],
            'Drupal': ['7.', '8.'],
            'Joomla': ['3.'],
            'IIS': ['8.5', '10.0']
        }

        # Status code meanings
        self.interesting_statuses = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            301: 'Moved Permanently',
            302: 'Found (Redirect)',
            307: 'Temporary Redirect',
            308: 'Permanent Redirect',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            405: 'Method Not Allowed',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable'
        }

    def probe_url(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Probe a single URL and extract all information"""
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status_code': None,
            'body_length': 0,
            'title': '',
            'technologies': [],
            'headers': {},
            'server': '',
            'redirects': [],
            'content_hash': '',
            'flags': [],
            'reachable': False
        }

        try:
            # Make request with redirect tracking
            session = requests.Session()
            response = session.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                verify=False,
                headers={'User-Agent': 'Mozilla/5.0 (Security Scanner)'}
            )

            result['status_code'] = response.status_code
            result['body_length'] = len(response.content)
            result['headers'] = dict(response.headers)
            result['server'] = response.headers.get('Server', '')
            result['reachable'] = True

            # Track redirects
            if response.history:
                result['redirects'] = [r.url for r in response.history]

            # Content hash for change detection
            result['content_hash'] = hashlib.sha256(response.content).hexdigest()

            # Extract title
            if 'text/html' in response.headers.get('Content-Type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                if soup.title:
                    result['title'] = soup.title.string.strip() if soup.title.string else ''

            # Detect technologies using httpx-style detection
            result['technologies'] = self.detect_technologies(response)

            # Flag high-value targets
            result['flags'] = self.flag_target(url, result)

        except requests.exceptions.Timeout:
            result['flags'].append({'type': 'error', 'message': 'Timeout'})
        except requests.exceptions.ConnectionError:
            result['flags'].append({'type': 'error', 'message': 'Connection Error'})
        except Exception as e:
            result['flags'].append({'type': 'error', 'message': str(e)})

        return result

    def detect_technologies(self, response: requests.Response) -> List[str]:
        """Detect technologies from headers and content"""
        technologies = []

        # From headers
        headers_to_check = {
            'Server': None,
            'X-Powered-By': None,
            'X-AspNet-Version': 'ASP.NET',
            'X-AspNetMvc-Version': 'ASP.NET MVC',
            'X-Generator': None,
            'X-Drupal-Cache': 'Drupal',
            'X-Drupal-Dynamic-Cache': 'Drupal'
        }

        for header, tech_name in headers_to_check.items():
            value = response.headers.get(header, '')
            if value:
                if tech_name:
                    technologies.append(f"{tech_name} {value}")
                else:
                    technologies.append(value)

        # From content
        content = response.text.lower()

        # WordPress
        if 'wp-content' in content or 'wp-includes' in content:
            # Try to extract version
            version_match = re.search(r'wordpress[/\s]+(\d+\.\d+(?:\.\d+)?)', content)
            if version_match:
                technologies.append(f"WordPress {version_match.group(1)}")
            else:
                technologies.append("WordPress")

        # jQuery
        jquery_match = re.search(r'jquery[/-]?(\d+\.\d+\.\d+)', content)
        if jquery_match:
            technologies.append(f"jQuery {jquery_match.group(1)}")

        # React
        if 'react' in content and '__react' in content:
            technologies.append("React")

        # Vue.js
        if 'vue.js' in content or 'vuejs' in content:
            technologies.append("Vue.js")

        # Angular
        if 'ng-app' in content or 'angular' in content:
            technologies.append("Angular")

        # Bootstrap
        bootstrap_match = re.search(r'bootstrap[/-]?(\d+\.\d+\.\d+)', content)
        if bootstrap_match:
            technologies.append(f"Bootstrap {bootstrap_match.group(1)}")

        # Drupal
        if 'drupal' in content:
            technologies.append("Drupal")

        # Joomla
        if 'joomla' in content:
            technologies.append("Joomla")

        return list(set(technologies))

    def flag_target(self, url: str, result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Flag high-value or interesting targets"""
        flags = []

        url_lower = url.lower()
        title_lower = result.get('title', '').lower()

        # Check URL for high-value keywords
        for category, keywords in self.high_value_keywords.items():
            for keyword in keywords:
                if keyword in url_lower:
                    flags.append({
                        'type': 'high_value',
                        'category': category,
                        'keyword': keyword,
                        'message': f"High-value target: {category} ({keyword} in URL)",
                        'severity': 'high' if category in ['admin', 'backup', 'upload'] else 'medium'
                    })
                    break

        # Check title for high-value keywords
        for category, keywords in self.high_value_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    flags.append({
                        'type': 'high_value',
                        'category': category,
                        'keyword': keyword,
                        'message': f"High-value target: {category} ({keyword} in title)",
                        'severity': 'medium'
                    })
                    break

        # Check for outdated/vulnerable technologies
        for tech in result.get('technologies', []):
            for tech_name, vulnerable_versions in self.outdated_tech.items():
                if tech_name.lower() in tech.lower():
                    for vuln_version in vulnerable_versions:
                        if vuln_version in tech:
                            flags.append({
                                'type': 'outdated_tech',
                                'technology': tech,
                                'message': f"Outdated/vulnerable technology: {tech}",
                                'severity': 'high'
                            })
                            break

        # Interesting status codes
        status = result.get('status_code')
        if status in [401, 403, 500, 502, 503]:
            flags.append({
                'type': 'status',
                'status_code': status,
                'message': f"Interesting status: {status} - {self.interesting_statuses.get(status, 'Unknown')}",
                'severity': 'low' if status == 404 else 'medium'
            })

        # Security headers missing
        headers = result.get('headers', {})
        security_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'Strict-Transport-Security', 'Content-Security-Policy']
        missing_headers = [h for h in security_headers if h not in headers]

        if missing_headers and status == 200:
            flags.append({
                'type': 'security',
                'message': f"Missing security headers: {', '.join(missing_headers)}",
                'severity': 'low'
            })

        # Redirects (potential open redirect)
        if result.get('redirects'):
            flags.append({
                'type': 'redirect',
                'message': f"Redirects detected: {len(result['redirects'])} hop(s)",
                'severity': 'low'
            })

        # Directory listing (common patterns)
        if status == 200 and 'index of' in title_lower:
            flags.append({
                'type': 'directory_listing',
                'message': 'Possible directory listing',
                'severity': 'medium'
            })

        # Default pages
        default_titles = ['apache', 'nginx', 'welcome', 'default page', 'test page', 'it works']
        if any(dt in title_lower for dt in default_titles):
            flags.append({
                'type': 'default_page',
                'message': 'Default/test page detected',
                'severity': 'low'
            })

        return flags

    def compare_results(self, old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two probe results and detect changes"""
        changes = {
            'url': new['url'],
            'timestamp': new['timestamp'],
            'has_changes': False,
            'changes': []
        }

        # Status code change
        if old.get('status_code') != new.get('status_code'):
            changes['has_changes'] = True
            changes['changes'].append({
                'type': 'status_code',
                'old': old.get('status_code'),
                'new': new.get('status_code'),
                'message': f"Status changed: {old.get('status_code')} → {new.get('status_code')}",
                'severity': 'high' if new.get('status_code') in [200, 401, 500] else 'medium'
            })

        # Title change
        if old.get('title') != new.get('title'):
            changes['has_changes'] = True
            changes['changes'].append({
                'type': 'title',
                'old': old.get('title'),
                'new': new.get('title'),
                'message': f"Title changed",
                'severity': 'medium'
            })

        # Body length change (significant = >10%)
        old_length = old.get('body_length', 0)
        new_length = new.get('body_length', 0)

        if old_length > 0:
            length_diff_percent = abs(new_length - old_length) / old_length * 100
            if length_diff_percent > 10:
                changes['has_changes'] = True
                changes['changes'].append({
                    'type': 'body_length',
                    'old': old_length,
                    'new': new_length,
                    'diff_percent': round(length_diff_percent, 2),
                    'message': f"Content size changed: {old_length} → {new_length} ({length_diff_percent:.1f}%)",
                    'severity': 'medium' if length_diff_percent > 50 else 'low'
                })

        # Content hash change
        if old.get('content_hash') != new.get('content_hash'):
            if not any(c['type'] == 'body_length' for c in changes['changes']):
                changes['has_changes'] = True
                changes['changes'].append({
                    'type': 'content',
                    'message': 'Content changed (same size, different hash)',
                    'severity': 'low'
                })

        # Technology changes
        old_tech = set(old.get('technologies', []))
        new_tech = set(new.get('technologies', []))

        added_tech = new_tech - old_tech
        removed_tech = old_tech - new_tech

        if added_tech:
            changes['has_changes'] = True
            changes['changes'].append({
                'type': 'technology_added',
                'technologies': list(added_tech),
                'message': f"New technologies: {', '.join(added_tech)}",
                'severity': 'medium'
            })

        if removed_tech:
            changes['has_changes'] = True
            changes['changes'].append({
                'type': 'technology_removed',
                'technologies': list(removed_tech),
                'message': f"Removed technologies: {', '.join(removed_tech)}",
                'severity': 'low'
            })

        # New flags
        old_flags = {f.get('message') for f in old.get('flags', [])}
        new_flags = {f.get('message') for f in new.get('flags', [])}

        added_flags = [f for f in new.get('flags', []) if f.get('message') not in old_flags]

        if added_flags:
            changes['has_changes'] = True
            changes['changes'].append({
                'type': 'new_flags',
                'flags': added_flags,
                'message': f"New flags detected: {len(added_flags)}",
                'severity': 'high' if any(f.get('severity') == 'high' for f in added_flags) else 'medium'
            })

        # Reachability change
        if old.get('reachable') != new.get('reachable'):
            changes['has_changes'] = True
            changes['changes'].append({
                'type': 'reachability',
                'old': old.get('reachable'),
                'new': new.get('reachable'),
                'message': f"Reachability changed: {old.get('reachable')} → {new.get('reachable')}",
                'severity': 'high'
            })

        return changes

    def probe_multiple(self, urls: List[str], parallel: bool = True) -> Dict[str, Dict[str, Any]]:
        """Probe multiple URLs"""
        results = {}

        if parallel:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                future_to_url = {executor.submit(self.probe_url, url): url for url in urls}

                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        result = future.result()
                        results[url] = result
                    except Exception as e:
                        results[url] = {'error': str(e)}
        else:
            for url in urls:
                results[url] = self.probe_url(url)

        return results

    def save_snapshot(self, results: Dict[str, Dict[str, Any]], filename: str):
        """Save probe results to file"""
        snapshot_file = self.output_dir / filename

        with open(snapshot_file, 'w') as f:
            json.dump(results, f, indent=2)

        return snapshot_file

    def load_snapshot(self, filename: str) -> Optional[Dict[str, Dict[str, Any]]]:
        """Load probe results from file"""
        snapshot_file = self.output_dir / filename

        if not snapshot_file.exists():
            return None

        with open(snapshot_file, 'r') as f:
            return json.load(f)

    def print_results(self, results: Dict[str, Dict[str, Any]]):
        """Print probe results in readable format"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}HTTP Monitoring Results{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")

        # Group by reachability
        reachable = {url: r for url, r in results.items() if r.get('reachable')}
        unreachable = {url: r for url, r in results.items() if not r.get('reachable')}

        # Print reachable URLs
        for url, result in reachable.items():
            status = result.get('status_code', 'N/A')
            status_color = Colors.GREEN if status == 200 else Colors.YELLOW if status in [301, 302] else Colors.RED

            print(f"{status_color}[{status}]{Colors.RESET} {url}")
            print(f"  Title: {result.get('title', 'N/A')[:60]}")
            print(f"  Length: {result.get('body_length', 0)} bytes")

            if result.get('technologies'):
                print(f"  Tech: {', '.join(result['technologies'][:3])}")

            # Print flags
            high_flags = [f for f in result.get('flags', []) if f.get('severity') == 'high']
            if high_flags:
                for flag in high_flags:
                    print(f"  {Colors.RED}[!] {flag.get('message')}{Colors.RESET}")

            print()

        # Summary
        print(f"{Colors.BOLD}Summary:{Colors.RESET}")
        print(f"  Total URLs: {len(results)}")
        print(f"  Reachable: {len(reachable)}")
        print(f"  Unreachable: {len(unreachable)}")

        # Count flags
        total_flags = sum(len(r.get('flags', [])) for r in results.values())
        high_severity = sum(1 for r in results.values() for f in r.get('flags', []) if f.get('severity') == 'high')

        print(f"  Total Flags: {total_flags}")
        if high_severity > 0:
            print(f"  {Colors.RED}High Severity: {high_severity}{Colors.RESET}")

        print()

    def print_changes(self, changes_list: List[Dict[str, Any]]):
        """Print changes in readable format"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}Detected Changes{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}{'='*80}{Colors.RESET}\n")

        for change_data in changes_list:
            if not change_data.get('has_changes'):
                continue

            print(f"{Colors.CYAN}{change_data['url']}{Colors.RESET}")

            for change in change_data['changes']:
                severity = change.get('severity', 'low')
                color = Colors.RED if severity == 'high' else Colors.YELLOW if severity == 'medium' else Colors.BLUE

                print(f"  {color}[{change['type'].upper()}] {change['message']}{Colors.RESET}")

            print()

def main():
    import argparse

    parser = argparse.ArgumentParser(description='HTTP Monitoring Tool')
    parser.add_argument('-u', '--url', help='Single URL to probe')
    parser.add_argument('-l', '--list', help='File containing URLs (one per line)')
    parser.add_argument('-o', '--output', default='./http_data', help='Output directory')
    parser.add_argument('-s', '--snapshot', help='Save snapshot with this name')
    parser.add_argument('-c', '--compare', help='Compare with previous snapshot')

    args = parser.parse_args()

    monitor = HTTPMonitor(args.output)

    # Collect URLs
    urls = []
    if args.url:
        urls.append(args.url)
    if args.list:
        with open(args.list, 'r') as f:
            urls.extend([line.strip() for line in f if line.strip()])

    if not urls:
        print(f"{Colors.RED}[!] No URLs provided. Use -u or -l{Colors.RESET}")
        return

    # Probe URLs
    print(f"{Colors.BLUE}[*] Probing {len(urls)} URL(s)...{Colors.RESET}")
    results = monitor.probe_multiple(urls)

    # Print results
    monitor.print_results(results)

    # Save snapshot
    if args.snapshot:
        snapshot_file = monitor.save_snapshot(results, args.snapshot)
        print(f"{Colors.GREEN}[+] Snapshot saved: {snapshot_file}{Colors.RESET}")

    # Compare with previous
    if args.compare:
        old_results = monitor.load_snapshot(args.compare)
        if old_results:
            changes_list = []
            for url in urls:
                if url in old_results and url in results:
                    changes = monitor.compare_results(old_results[url], results[url])
                    if changes['has_changes']:
                        changes_list.append(changes)

            if changes_list:
                monitor.print_changes(changes_list)
        else:
            print(f"{Colors.YELLOW}[!] Previous snapshot not found: {args.compare}{Colors.RESET}")

if __name__ == "__main__":
    main()
