#!/usr/bin/env python3
"""
Enhanced Terminal Dashboard for Bug Bounty Monitor
Shows comprehensive data: subdomains, endpoints, technologies, Shodan, Wayback results
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import curses
import argparse

class Dashboard:
    def __init__(self, data_dir="./data", diff_dir="./data/diffs", baseline_dir="./data/baseline"):
        self.data_dir = Path(data_dir)
        self.diff_dir = Path(diff_dir)
        self.baseline_dir = Path(baseline_dir)
        self.shodan_dir = self.data_dir / "shodan_scans"
        self.wayback_dir = self.data_dir / "wayback_scans"

    def get_all_baselines(self):
        """Get all baseline data"""
        baselines = {}
        baseline_files = list(self.baseline_dir.glob("*_baseline.json"))

        for baseline_file in baseline_files:
            try:
                domain = baseline_file.stem.replace('_baseline', '')
                with open(baseline_file, 'r') as f:
                    baselines[domain] = json.load(f)
            except Exception as e:
                print(f"Error loading {baseline_file}: {e}")
                continue

        return baselines

    def get_subdomain_data(self, domain=None):
        """Get detailed subdomain information"""
        baselines = self.get_all_baselines()

        if domain and domain in baselines:
            baselines = {domain: baselines[domain]}

        subdomain_data = []

        for dom, baseline in baselines.items():
            subdomains = baseline.get('subdomains', {})
            endpoints = baseline.get('endpoints', {})

            for subdomain in subdomains.keys():
                # Find endpoints for this subdomain
                sub_endpoints = [url for url in endpoints.keys()
                               if subdomain in url]

                # Get status from endpoints
                status = "Unknown"
                status_code = None
                for url in sub_endpoints:
                    if endpoints[url].get('status_code'):
                        status_code = endpoints[url]['status_code']
                        status = "Live" if 200 <= status_code < 400 else "Error"
                        break

                subdomain_data.append({
                    'domain': dom,
                    'subdomain': subdomain,
                    'status': status,
                    'status_code': status_code,
                    'endpoint_count': len(sub_endpoints)
                })

        return subdomain_data

    def get_endpoint_data(self, domain=None):
        """Get detailed endpoint information"""
        baselines = self.get_all_baselines()

        if domain and domain in baselines:
            baselines = {domain: baselines[domain]}

        endpoint_data = []

        for dom, baseline in baselines.items():
            endpoints = baseline.get('endpoints', {})

            for url, data in endpoints.items():
                endpoint_data.append({
                    'domain': dom,
                    'url': url,
                    'status_code': data.get('status_code', 'N/A'),
                    'title': data.get('title', 'N/A'),
                    'content_length': data.get('body_length', 0),
                    'technologies': ', '.join(data.get('technologies', [])),
                    'server': data.get('server', 'N/A'),
                    'flags': data.get('flags', [])
                })

        return endpoint_data

    def get_technology_stats(self, domain=None):
        """Get technology statistics"""
        baselines = self.get_all_baselines()

        if domain and domain in baselines:
            baselines = {domain: baselines[domain]}

        tech_counter = Counter()
        server_counter = Counter()

        for dom, baseline in baselines.items():
            endpoints = baseline.get('endpoints', {})

            for url, data in endpoints.items():
                # Count technologies
                for tech in data.get('technologies', []):
                    tech_counter[tech] += 1

                # Count servers
                server = data.get('server', 'Unknown')
                if server and server != 'N/A':
                    server_counter[server] += 1

        return {
            'technologies': dict(tech_counter.most_common(20)),
            'servers': dict(server_counter.most_common(10))
        }

    def get_security_findings(self, domain=None):
        """Get security findings"""
        baselines = self.get_all_baselines()

        if domain and domain in baselines:
            baselines = {domain: baselines[domain]}

        findings = {
            'subdomain_takeovers': [],
            'high_value_targets': [],
            'outdated_tech': [],
            'error_pages': []
        }

        for dom, baseline in baselines.items():
            # Subdomain takeovers
            takeovers = baseline.get('subdomain_takeovers', [])
            for takeover in takeovers:
                findings['subdomain_takeovers'].append({
                    'domain': dom,
                    'subdomain': takeover.get('subdomain', 'N/A'),
                    'service': takeover.get('service', 'N/A'),
                    'confidence': takeover.get('confidence', 'N/A')
                })

            # High-value targets and errors
            endpoints = baseline.get('endpoints', {})
            for url, data in endpoints.items():
                # High-value targets
                flags = data.get('flags', [])
                if any('high-value' in str(flag).lower() or 'admin' in str(flag).lower()
                       or 'upload' in str(flag).lower() for flag in flags):
                    findings['high_value_targets'].append({
                        'domain': dom,
                        'url': url,
                        'status_code': data.get('status_code', 'N/A'),
                        'flags': flags
                    })

                # Outdated technology
                if any('outdated' in str(flag).lower() for flag in flags):
                    findings['outdated_tech'].append({
                        'domain': dom,
                        'url': url,
                        'technologies': data.get('technologies', []),
                        'flag': next((f for f in flags if 'outdated' in str(f).lower()), '')
                    })

                # Error pages (5xx)
                status_code = data.get('status_code', 0)
                if 500 <= status_code < 600:
                    findings['error_pages'].append({
                        'domain': dom,
                        'url': url,
                        'status_code': status_code
                    })

        return findings

    def get_shodan_data(self, domain=None):
        """Get Shodan scan results with detailed findings"""
        if not self.shodan_dir.exists():
            return {}

        shodan_data = {}
        shodan_files = list(self.shodan_dir.glob("*.json"))

        # Get most recent file for each domain
        domain_files = {}
        for file in shodan_files:
            file_domain = file.stem.rsplit('_', 1)[0]
            if domain and file_domain != domain:
                continue

            if file_domain not in domain_files or os.path.getmtime(file) > os.path.getmtime(domain_files[file_domain]):
                domain_files[file_domain] = file

        for dom, file in domain_files.items():
            try:
                with open(file, 'r') as f:
                    data = json.load(f)

                    # Extract detailed findings
                    findings = {
                        'open_ports': [],
                        'vulnerabilities': [],
                        'services': [],
                        'high_value': []
                    }

                    # Parse hosts data
                    hosts = data.get('hosts', {})
                    for ip, host_data in hosts.items():
                        # Extract open ports
                        ports = host_data.get('ports', [])
                        if ports:
                            findings['open_ports'].append({
                                'ip': ip,
                                'ports': ports[:10]  # First 10 ports
                            })

                        # Extract vulnerabilities
                        vulns = host_data.get('vulns', [])
                        for vuln in vulns[:3]:  # First 3 CVEs per host
                            findings['vulnerabilities'].append({
                                'ip': ip,
                                'cve': vuln,
                                'hostname': host_data.get('hostnames', [''])[0]
                            })

                        # Extract services
                        services = host_data.get('data', [])
                        for service in services[:3]:  # First 3 services per host
                            findings['services'].append({
                                'ip': ip,
                                'port': service.get('port'),
                                'service': service.get('product', 'Unknown'),
                                'version': service.get('version', '')
                            })

                        # High-value findings
                        if host_data.get('high_value'):
                            findings['high_value'].append({
                                'ip': ip,
                                'reason': host_data.get('high_value_reason', 'Unknown'),
                                'hostname': host_data.get('hostnames', [''])[0]
                            })

                    shodan_data[dom] = {
                        'total_hosts': data.get('summary', {}).get('total_hosts', 0),
                        'with_vulnerabilities': data.get('summary', {}).get('with_vulnerabilities', 0),
                        'high_value_hosts': data.get('summary', {}).get('high_value_hosts', 0),
                        'scanned_at': data.get('timestamp', 'N/A'),
                        'findings': findings
                    }
            except Exception as e:
                continue

        return shodan_data

    def get_wayback_data(self, domain=None):
        """Get Wayback Machine results with sample URLs per category"""
        if not self.wayback_dir.exists():
            return {}

        wayback_data = {}
        wayback_files = list(self.wayback_dir.glob("*[0-9].json"))  # Exclude category files

        # Get most recent file for each domain
        domain_files = {}
        for file in wayback_files:
            file_domain = file.stem.rsplit('_', 1)[0]
            if domain and file_domain != domain:
                continue

            if file_domain not in domain_files or os.path.getmtime(file) > os.path.getmtime(domain_files[file_domain]):
                domain_files[file_domain] = file

        for dom, file in domain_files.items():
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    stats = data.get('statistics', {})
                    categorized = data.get('categorized', {})

                    # Extract sample URLs from each category
                    category_samples = {}
                    for category, items in categorized.items():
                        if items:
                            # Get top 5 URLs by score
                            sorted_items = sorted(items, key=lambda x: x.get('score', 0), reverse=True)
                            category_samples[category] = [
                                {
                                    'url': item.get('url', ''),
                                    'priority': item.get('priority', 'low'),
                                    'score': item.get('score', 0)
                                }
                                for item in sorted_items[:5]
                            ]

                    wayback_data[dom] = {
                        'total_urls': data.get('total_urls', 0),
                        'critical': stats.get('by_priority', {}).get('critical', 0),
                        'high': stats.get('by_priority', {}).get('high', 0),
                        'categories': stats.get('by_category', {}),
                        'category_samples': category_samples,
                        'scanned_at': data.get('timestamp', 'N/A')
                    }
            except Exception as e:
                continue

        return wayback_data

    def get_statistics(self):
        """Calculate comprehensive statistics"""
        baselines = self.get_all_baselines()

        stats = {
            'total_targets': len(baselines),
            'total_subdomains': 0,
            'total_endpoints': 0,
            'live_endpoints': 0,
            'status_breakdown': {'2xx': 0, '3xx': 0, '4xx': 0, '5xx': 0, 'other': 0},
            'changes_24h': defaultdict(int),
            'changes_7d': defaultdict(int),
            'recent_changes': []
        }

        # Count from baselines
        for domain, baseline in baselines.items():
            stats['total_subdomains'] += len(baseline.get('subdomains', {}))
            endpoints = baseline.get('endpoints', {})
            stats['total_endpoints'] += len(endpoints)

            # Count status codes
            for url, data in endpoints.items():
                status_code = data.get('status_code', 0)
                if status_code:
                    stats['live_endpoints'] += 1
                    if 200 <= status_code < 300:
                        stats['status_breakdown']['2xx'] += 1
                    elif 300 <= status_code < 400:
                        stats['status_breakdown']['3xx'] += 1
                    elif 400 <= status_code < 500:
                        stats['status_breakdown']['4xx'] += 1
                    elif 500 <= status_code < 600:
                        stats['status_breakdown']['5xx'] += 1
                    else:
                        stats['status_breakdown']['other'] += 1

        # Analyze changes
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        diff_files = sorted(self.diff_dir.glob("*.json"), key=os.path.getmtime, reverse=True)

        for diff_file in diff_files[:50]:
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(diff_file))
                with open(diff_file, 'r') as f:
                    changes = json.load(f)

                    change_count = sum([
                        len(changes.get('new_subdomains', [])),
                        len(changes.get('new_endpoints', [])),
                        len(changes.get('changed_endpoints', [])),
                        len(changes.get('new_js_endpoints', []))
                    ])

                    if change_count > 0:
                        domain = diff_file.stem.rsplit('_', 2)[0]

                        if len(stats['recent_changes']) < 20:
                            stats['recent_changes'].append({
                                'domain': domain,
                                'time': file_time.strftime("%Y-%m-%d %H:%M"),
                                'changes': changes,
                                'total': change_count
                            })

                        if file_time > day_ago:
                            stats['changes_24h']['new_subdomains'] += len(changes.get('new_subdomains', []))
                            stats['changes_24h']['new_endpoints'] += len(changes.get('new_endpoints', []))

                        if file_time > week_ago:
                            stats['changes_7d']['new_subdomains'] += len(changes.get('new_subdomains', []))
                            stats['changes_7d']['new_endpoints'] += len(changes.get('new_endpoints', []))

            except Exception as e:
                continue

        return stats

    def render_simple(self, domain=None, view='overview'):
        """Enhanced text-based dashboard with multiple views"""
        print("\n" + "="*100)
        print(" " * 35 + "BUG BOUNTY MONITORING DASHBOARD")
        print("="*100)
        print()

        if view == 'overview':
            self._render_overview(domain)
        elif view == 'subdomains':
            self._render_subdomains(domain)
        elif view == 'endpoints':
            self._render_endpoints(domain)
        elif view == 'technologies':
            self._render_technologies(domain)
        elif view == 'security':
            self._render_security(domain)
        elif view == 'shodan':
            self._render_shodan(domain)
        elif view == 'wayback':
            self._render_wayback(domain)
        elif view == 'all':
            self._render_overview(domain)
            self._render_security(domain)
            self._render_technologies(domain)
            if self.shodan_dir.exists():
                self._render_shodan(domain)
            if self.wayback_dir.exists():
                self._render_wayback(domain)

        print("="*100)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)
        print()

    def _render_overview(self, domain=None):
        """Render overview section"""
        stats = self.get_statistics()

        filter_text = f" (Domain: {domain})" if domain else ""

        print(f"📊 OVERVIEW{filter_text}")
        print("-" * 100)
        print(f"  Targets:           {stats['total_targets']}")
        print(f"  Total Subdomains:  {stats['total_subdomains']}")
        print(f"  Total Endpoints:   {stats['total_endpoints']}")
        print(f"  Live Endpoints:    {stats['live_endpoints']}")
        print()

        print("📈 HTTP STATUS DISTRIBUTION")
        print("-" * 100)
        print(f"  2xx (Success):      {stats['status_breakdown']['2xx']:4d}  {'█' * min(50, stats['status_breakdown']['2xx'])}")
        print(f"  3xx (Redirect):     {stats['status_breakdown']['3xx']:4d}  {'█' * min(50, stats['status_breakdown']['3xx'])}")
        print(f"  4xx (Client Error): {stats['status_breakdown']['4xx']:4d}  {'█' * min(50, stats['status_breakdown']['4xx'])}")
        print(f"  5xx (Server Error): {stats['status_breakdown']['5xx']:4d}  {'█' * min(50, stats['status_breakdown']['5xx'])}")
        print()

        print("⏰ CHANGES - LAST 24 HOURS")
        print("-" * 100)
        print(f"  New Subdomains:    {stats['changes_24h']['new_subdomains']}")
        print(f"  New Endpoints:     {stats['changes_24h']['new_endpoints']}")
        print()

        print("📅 CHANGES - LAST 7 DAYS")
        print("-" * 100)
        print(f"  New Subdomains:    {stats['changes_7d']['new_subdomains']}")
        print(f"  New Endpoints:     {stats['changes_7d']['new_endpoints']}")
        print()

    def _render_subdomains(self, domain=None):
        """Render subdomain listing"""
        subdomain_data = self.get_subdomain_data(domain)

        print(f"🌐 SUBDOMAIN LISTING ({len(subdomain_data)} total)")
        print("-" * 100)
        print(f"  {'Subdomain':<50} {'Status':<10} {'Code':<10} {'Endpoints':<10}")
        print("  " + "-" * 98)

        # Sort by status (Live first, then by name)
        subdomain_data.sort(key=lambda x: (x['status'] != 'Live', x['subdomain']))

        for i, sub in enumerate(subdomain_data[:50]):  # Show first 50
            status_icon = "✓" if sub['status'] == 'Live' else "✗"
            code_str = str(sub['status_code']) if sub['status_code'] else "N/A"
            print(f"  {status_icon} {sub['subdomain']:<47} {sub['status']:<10} {code_str:<10} {sub['endpoint_count']:<10}")

        if len(subdomain_data) > 50:
            print(f"\n  ... and {len(subdomain_data) - 50} more subdomains")
        print()

    def _render_endpoints(self, domain=None):
        """Render endpoint listing"""
        endpoint_data = self.get_endpoint_data(domain)

        print(f"🔗 ENDPOINT LISTING ({len(endpoint_data)} total)")
        print("-" * 100)

        # Group by status code
        by_status = defaultdict(list)
        for ep in endpoint_data:
            status = ep['status_code']
            by_status[status].append(ep)

        # Show successful endpoints (2xx)
        if any(200 <= s < 300 for s in by_status.keys() if isinstance(s, int)):
            print("  ✅ 2XX - SUCCESS")
            for code in sorted([s for s in by_status.keys() if isinstance(s, int) and 200 <= s < 300]):
                endpoints = by_status[code][:10]  # First 10 per code
                for ep in endpoints:
                    tech_str = ep['technologies'][:60] if ep['technologies'] else "N/A"
                    print(f"    [{code}] {ep['url']:<70}")
                    if tech_str != "N/A":
                        print(f"           Tech: {tech_str}")
                    if ep['flags']:
                        print(f"           Flags: {', '.join(str(f) for f in ep['flags'][:3])}")

        # Show redirects (3xx)
        if any(300 <= s < 400 for s in by_status.keys() if isinstance(s, int)):
            print("\n  ↩️  3XX - REDIRECTS")
            for code in sorted([s for s in by_status.keys() if isinstance(s, int) and 300 <= s < 400]):
                count = len(by_status[code])
                print(f"    [{code}] {count} endpoint(s)")

        # Show client errors (4xx)
        if any(400 <= s < 500 for s in by_status.keys() if isinstance(s, int)):
            print("\n  ❌ 4XX - CLIENT ERRORS")
            for code in sorted([s for s in by_status.keys() if isinstance(s, int) and 400 <= s < 500]):
                endpoints = by_status[code][:5]
                for ep in endpoints:
                    print(f"    [{code}] {ep['url']}")

        # Show server errors (5xx)
        if any(500 <= s < 600 for s in by_status.keys() if isinstance(s, int)):
            print("\n  🔴 5XX - SERVER ERRORS")
            for code in sorted([s for s in by_status.keys() if isinstance(s, int) and 500 <= s < 600]):
                for ep in by_status[code]:
                    print(f"    [{code}] {ep['url']}")

        print()

    def _render_technologies(self, domain=None):
        """Render technology statistics"""
        tech_stats = self.get_technology_stats(domain)

        print("💻 TECHNOLOGY STACK")
        print("-" * 100)

        if tech_stats['technologies']:
            print("  Top Technologies:")
            for tech, count in list(tech_stats['technologies'].items())[:15]:
                bar = '█' * min(40, count)
                print(f"    {tech:<30} {count:4d}  {bar}")
        else:
            print("  No technology data available")

        print()

        if tech_stats['servers']:
            print("  Web Servers:")
            for server, count in list(tech_stats['servers'].items())[:10]:
                bar = '█' * min(40, count)
                print(f"    {server:<30} {count:4d}  {bar}")

        print()

    def _render_security(self, domain=None):
        """Render security findings"""
        findings = self.get_security_findings(domain)

        print("🔒 SECURITY FINDINGS")
        print("-" * 100)

        # Subdomain takeovers
        if findings['subdomain_takeovers']:
            print(f"  ⚠️  SUBDOMAIN TAKEOVERS ({len(findings['subdomain_takeovers'])})")
            for takeover in findings['subdomain_takeovers'][:10]:
                print(f"    • {takeover['subdomain']} ({takeover['service']}) - Confidence: {takeover['confidence']}")
        else:
            print("  ✓ No subdomain takeovers detected")

        print()

        # High-value targets
        if findings['high_value_targets']:
            print(f"  🎯 HIGH-VALUE TARGETS ({len(findings['high_value_targets'])})")
            for target in findings['high_value_targets'][:15]:
                flags_str = ', '.join(str(f) for f in target['flags'][:2])
                print(f"    [{target['status_code']}] {target['url']}")
                print(f"           {flags_str}")
        else:
            print("  No high-value targets flagged")

        print()

        # Outdated technology
        if findings['outdated_tech']:
            print(f"  🔧 OUTDATED TECHNOLOGY ({len(findings['outdated_tech'])})")
            for tech in findings['outdated_tech'][:10]:
                print(f"    • {tech['url']}")
                print(f"      {tech['flag']}")

        print()

        # Server errors
        if findings['error_pages']:
            print(f"  🔴 SERVER ERRORS (5xx) ({len(findings['error_pages'])})")
            for error in findings['error_pages'][:10]:
                print(f"    [{error['status_code']}] {error['url']}")

        print()

    def _render_shodan(self, domain=None):
        """Render Shodan results with detailed findings"""
        shodan_data = self.get_shodan_data(domain)

        print("🛰️  SHODAN INTELLIGENCE")
        print("-" * 100)

        if shodan_data:
            for dom, data in shodan_data.items():
                print(f"  Domain: {dom}")
                print(f"    Hosts Scanned:       {data['total_hosts']}")
                print(f"    With Vulnerabilities: {data['with_vulnerabilities']}")
                print(f"    High-Value Hosts:    {data['high_value_hosts']}")
                print(f"    Scanned At:          {data['scanned_at']}")
                print()

                # Show vulnerabilities found
                if data.get('findings', {}).get('vulnerabilities'):
                    vulns = data['findings']['vulnerabilities']
                    print(f"  🔴 VULNERABILITIES FOUND ({len(vulns)})")
                    displayed = 0
                    for vuln in vulns:
                        if displayed >= 10:  # Limit to 10
                            remaining = len(vulns) - displayed
                            print(f"    ... and {remaining} more")
                            break
                        hostname = vuln.get('hostname', 'N/A')
                        print(f"    • {vuln['cve']} on {vuln['ip']} ({hostname})")
                        displayed += 1
                    print()

                # Show high-value findings
                if data.get('findings', {}).get('high_value'):
                    hv = data['findings']['high_value']
                    print(f"  🎯 HIGH-VALUE FINDINGS ({len(hv)})")
                    for finding in hv[:8]:  # Show first 8
                        hostname = finding.get('hostname', 'N/A')
                        print(f"    • {finding['ip']} ({hostname})")
                        print(f"      → {finding['reason']}")
                    if len(hv) > 8:
                        print(f"    ... and {len(hv) - 8} more")
                    print()

                # Show interesting services
                if data.get('findings', {}).get('services'):
                    services = data['findings']['services']
                    print(f"  🔧 SERVICES DETECTED ({len(services)})")
                    displayed = 0
                    for svc in services:
                        if displayed >= 12:  # Limit to 12
                            remaining = len(services) - displayed
                            print(f"    ... and {remaining} more services")
                            break
                        version = f" {svc['version']}" if svc.get('version') else ""
                        print(f"    • {svc['ip']}:{svc['port']} - {svc['service']}{version}")
                        displayed += 1
                    print()

                # Show open ports summary
                if data.get('findings', {}).get('open_ports'):
                    ports = data['findings']['open_ports']
                    print(f"  🔌 OPEN PORTS ({len(ports)} hosts)")
                    for port_info in ports[:5]:  # Show first 5 hosts
                        ports_str = ', '.join(map(str, port_info['ports']))
                        print(f"    • {port_info['ip']}: {ports_str}")
                    if len(ports) > 5:
                        print(f"    ... and {len(ports) - 5} more hosts")
                    print()

        else:
            print("  No Shodan data available")
            print("  Enable Shodan scanning in config.yaml to gather network intelligence")

        print()

    def _render_wayback(self, domain=None):
        """Render Wayback Machine results with sample URLs"""
        wayback_data = self.get_wayback_data(domain)

        print("📜 WAYBACK MACHINE RESULTS")
        print("-" * 100)

        if wayback_data:
            for dom, data in wayback_data.items():
                print(f"  Domain: {dom}")
                print(f"    Total URLs:     {data['total_urls']}")
                print(f"    Critical URLs:  {data['critical']}")
                print(f"    High Priority:  {data['high']}")
                print(f"    Scanned At:     {data['scanned_at']}")
                print()

                # Display high-value categories with sample URLs
                if data.get('category_samples'):
                    samples = data['category_samples']

                    # Priority categories to show
                    priority_cats = ['credentials', 'backup', 'database', 'config', 'version_control']

                    for cat in priority_cats:
                        if cat in samples and samples[cat]:
                            urls = samples[cat]
                            print(f"  🔍 {cat.upper().replace('_', ' ')} ({len(urls)} samples)")
                            for url_data in urls[:3]:  # Show top 3 per category
                                priority_icon = "🔴" if url_data['priority'] == 'critical' else "🟡" if url_data['priority'] == 'high' else "🔵"
                                print(f"    {priority_icon} [{url_data['priority']}] Score: {url_data['score']}")
                                # Truncate long URLs
                                url = url_data['url']
                                if len(url) > 85:
                                    url = url[:82] + "..."
                                print(f"       {url}")
                            if len(urls) > 3:
                                print(f"    ... and {len(urls) - 3} more")
                            print()

                    # Show other categories summary
                    other_cats = [cat for cat in samples.keys() if cat not in priority_cats and samples[cat]]
                    if other_cats:
                        print(f"  📋 OTHER CATEGORIES")
                        for cat in other_cats[:5]:
                            count = len(samples[cat])
                            print(f"    • {cat}: {count} URLs")
                        if len(other_cats) > 5:
                            print(f"    ... and {len(other_cats) - 5} more categories")
                        print()

                elif data.get('categories'):
                    # Fallback to old display if no samples
                    print(f"  📋 TOP CATEGORIES:")
                    for cat, count in list(data['categories'].items())[:8]:
                        print(f"    • {cat}: {count}")
                    print()

        else:
            print("  No Wayback data available")
            print("  Enable Wayback scanning in config.yaml to discover historical URLs")

        print()

def main():
    parser = argparse.ArgumentParser(description='Enhanced Bug Bounty Monitoring Dashboard')
    parser.add_argument('-d', '--domain', help='Filter by specific domain')
    parser.add_argument('-v', '--view',
                       choices=['overview', 'subdomains', 'endpoints', 'technologies', 'security', 'shodan', 'wayback', 'all'],
                       default='overview',
                       help='Dashboard view to display')
    parser.add_argument('--data-dir', default='./data', help='Data directory path')

    args = parser.parse_args()

    dashboard = Dashboard(data_dir=args.data_dir)
    dashboard.render_simple(domain=args.domain, view=args.view)

if __name__ == "__main__":
    main()
