#!/usr/bin/env python3
"""
Shodan Scanner Module
Integrates Shodan API for gathering information about discovered assets
"""

import json
import time
from typing import Dict, List, Set, Optional
from pathlib import Path
import logging

try:
    import shodan
    SHODAN_AVAILABLE = True
except ImportError:
    SHODAN_AVAILABLE = False

logger = logging.getLogger(__name__)


class ShodanScanner:
    """Shodan API integration for reconnaissance"""

    def __init__(self, api_key: str, config: Dict = None):
        """
        Initialize Shodan scanner

        Args:
            api_key: Shodan API key
            config: Configuration dictionary
        """
        if not SHODAN_AVAILABLE:
            raise ImportError("shodan package not installed. Run: pip install shodan")

        if not api_key:
            raise ValueError("Shodan API key is required")

        self.api_key = api_key
        self.api = shodan.Shodan(api_key)
        self.config = config or {}

        # Configuration options
        self.max_results = self.config.get('max_results', 100)
        self.timeout = self.config.get('timeout', 30)
        self.rate_limit_delay = self.config.get('rate_limit_delay', 1)  # seconds between requests

        # Results storage
        self.results = {
            'hosts': {},
            'vulnerabilities': [],
            'services': [],
            'high_value_findings': []
        }

        # High-value indicators
        self.high_value_ports = [21, 22, 23, 25, 80, 443, 445, 1433, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 9200, 27017]
        self.vulnerable_products = ['Apache', 'nginx', 'IIS', 'OpenSSH', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch']

    def get_api_info(self) -> Dict:
        """Get Shodan API account information"""
        try:
            info = self.api.info()
            logger.info(f"Shodan API - Plan: {info.get('plan', 'unknown')}, "
                       f"Credits: {info.get('query_credits', 0)}, "
                       f"Scan credits: {info.get('scan_credits', 0)}")
            return info
        except shodan.APIError as e:
            logger.error(f"Shodan API error: {e}")
            return {}

    def host_lookup(self, ip: str) -> Optional[Dict]:
        """
        Lookup information about a specific host

        Args:
            ip: IP address to lookup

        Returns:
            Dictionary with host information
        """
        try:
            logger.info(f"Shodan lookup: {ip}")
            host = self.api.host(ip)

            # Extract relevant information
            result = {
                'ip': ip,
                'hostnames': host.get('hostnames', []),
                'domains': host.get('domains', []),
                'org': host.get('org', ''),
                'isp': host.get('isp', ''),
                'asn': host.get('asn', ''),
                'country': host.get('country_name', ''),
                'city': host.get('city', ''),
                'ports': host.get('ports', []),
                'vulns': host.get('vulns', []),
                'tags': host.get('tags', []),
                'os': host.get('os', ''),
                'last_update': host.get('last_update', ''),
                'services': []
            }

            # Extract service information
            for item in host.get('data', []):
                service = {
                    'port': item.get('port'),
                    'transport': item.get('transport', 'tcp'),
                    'product': item.get('product', ''),
                    'version': item.get('version', ''),
                    'banner': item.get('data', '')[:200],  # First 200 chars
                    'ssl': item.get('ssl', {}) if 'ssl' in item else None,
                    'http': {
                        'title': item.get('http', {}).get('title', ''),
                        'server': item.get('http', {}).get('server', ''),
                        'status': item.get('http', {}).get('status', '')
                    } if 'http' in item else None
                }
                result['services'].append(service)

            # Flag high-value findings
            self._flag_high_value_findings(result)

            # Store results
            self.results['hosts'][ip] = result

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            return result

        except shodan.APIError as e:
            logger.error(f"Shodan API error for {ip}: {e}")
            return None

    def search(self, query: str, facets: List[str] = None) -> Dict:
        """
        Search Shodan using a query

        Args:
            query: Shodan search query (e.g., "hostname:example.com")
            facets: List of facets to include (e.g., ['port', 'country'])

        Returns:
            Dictionary with search results
        """
        try:
            logger.info(f"Shodan search: {query}")

            # Prepare facets
            if facets:
                facets_dict = {f: 10 for f in facets}
            else:
                facets_dict = None

            # Perform search
            results = self.api.search(query, facets=facets_dict)

            search_results = {
                'total': results.get('total', 0),
                'matches': []
            }

            # Process matches
            for match in results.get('matches', []):
                item = {
                    'ip': match.get('ip_str', ''),
                    'port': match.get('port', 0),
                    'org': match.get('org', ''),
                    'hostnames': match.get('hostnames', []),
                    'domains': match.get('domains', []),
                    'product': match.get('product', ''),
                    'version': match.get('version', ''),
                    'banner': match.get('data', '')[:200],
                    'vulns': list(match.get('vulns', [])) if match.get('vulns') else []
                }
                search_results['matches'].append(item)

            # Add facets if available
            if 'facets' in results:
                search_results['facets'] = results['facets']

            logger.info(f"Found {search_results['total']} results")

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            return search_results

        except shodan.APIError as e:
            logger.error(f"Shodan search error: {e}")
            return {'total': 0, 'matches': []}

    def search_domain(self, domain: str) -> Dict:
        """
        Search for all hosts associated with a domain

        Args:
            domain: Domain to search

        Returns:
            Dictionary with domain search results
        """
        query = f"hostname:{domain}"
        return self.search(query, facets=['port', 'country', 'org'])

    def dns_lookup(self, hostnames: List[str]) -> Dict[str, str]:
        """
        Resolve hostnames to IP addresses using standard DNS
        (Shodan API doesn't provide DNS resolution, using socket instead)

        Args:
            hostnames: List of hostnames to resolve

        Returns:
            Dictionary mapping hostnames to IPs
        """
        import socket
        results = {}

        logger.info(f"DNS lookup for {len(hostnames)} hostnames")

        for hostname in hostnames:
            try:
                # Use standard DNS resolution
                ip = socket.gethostbyname(hostname)
                results[hostname] = ip

                # Rate limiting to avoid overwhelming DNS
                time.sleep(0.1)

            except (socket.gaierror, socket.herror, socket.timeout):
                # Hostname doesn't resolve
                logger.debug(f"Failed to resolve: {hostname}")
                continue
            except Exception as e:
                logger.debug(f"DNS error for {hostname}: {e}")
                continue

        return results

    def dns_reverse(self, ips: List[str]) -> Dict[str, List[str]]:
        """
        Reverse DNS lookup for IP addresses using standard DNS

        Args:
            ips: List of IP addresses

        Returns:
            Dictionary mapping IPs to hostnames
        """
        import socket
        results = {}

        logger.info(f"Reverse DNS for {len(ips)} IPs")

        for ip in ips:
            try:
                # Use standard reverse DNS
                hostnames = socket.gethostbyaddr(ip)
                results[ip] = [hostnames[0]] if hostnames else []

                # Rate limiting
                time.sleep(0.1)

            except (socket.gaierror, socket.herror, socket.timeout):
                # IP doesn't have reverse DNS
                logger.debug(f"No reverse DNS for: {ip}")
                results[ip] = []
            except Exception as e:
                logger.debug(f"Reverse DNS error for {ip}: {e}")
                results[ip] = []

        return results

    def scan_subdomains(self, subdomains: List[str]) -> Dict:
        """
        Scan a list of subdomains for information

        Args:
            subdomains: List of subdomain hostnames

        Returns:
            Dictionary with scan results
        """
        results = {
            'resolved': {},
            'hosts': {},
            'summary': {
                'total_subdomains': len(subdomains),
                'resolved': 0,
                'with_vulns': 0,
                'high_value': 0
            }
        }

        # Resolve subdomains in batches
        batch_size = 100
        for i in range(0, len(subdomains), batch_size):
            batch = subdomains[i:i+batch_size]
            resolved = self.dns_lookup(batch)
            results['resolved'].update(resolved)

        results['summary']['resolved'] = len(results['resolved'])
        logger.info(f"Resolved {results['summary']['resolved']}/{len(subdomains)} subdomains")

        # Lookup each resolved IP
        processed_ips = set()
        for subdomain, ip in results['resolved'].items():
            if ip and ip not in processed_ips:
                host_info = self.host_lookup(ip)
                if host_info:
                    results['hosts'][ip] = host_info

                    # Update summary
                    if host_info.get('vulns'):
                        results['summary']['with_vulns'] += 1

                    if self._is_high_value(host_info):
                        results['summary']['high_value'] += 1

                processed_ips.add(ip)

        return results

    def _flag_high_value_findings(self, host_info: Dict):
        """Flag high-value findings in host information"""
        findings = []

        # Check for vulnerabilities
        if host_info.get('vulns'):
            findings.append({
                'type': 'vulnerabilities',
                'severity': 'high',
                'description': f"Found {len(host_info['vulns'])} known vulnerabilities",
                'details': host_info['vulns']
            })

        # Check for high-value ports
        open_high_value = [p for p in host_info.get('ports', []) if p in self.high_value_ports]
        if open_high_value:
            findings.append({
                'type': 'high_value_ports',
                'severity': 'medium',
                'description': f"High-value ports open: {', '.join(map(str, open_high_value))}",
                'details': open_high_value
            })

        # Check for vulnerable products
        for service in host_info.get('services', []):
            product = service.get('product', '')
            if any(vp in product for vp in self.vulnerable_products):
                findings.append({
                    'type': 'vulnerable_product',
                    'severity': 'medium',
                    'description': f"Potentially vulnerable product: {product} on port {service.get('port')}",
                    'details': service
                })

        # Check for exposed services
        if any(p in host_info.get('ports', []) for p in [3389, 5900, 23]):  # RDP, VNC, Telnet
            findings.append({
                'type': 'exposed_remote_access',
                'severity': 'high',
                'description': "Remote access service exposed (RDP/VNC/Telnet)",
                'details': [p for p in host_info.get('ports', []) if p in [3389, 5900, 23]]
            })

        # Check for exposed databases
        if any(p in host_info.get('ports', []) for p in [1433, 3306, 5432, 6379, 27017, 9200]):
            findings.append({
                'type': 'exposed_database',
                'severity': 'high',
                'description': "Database service exposed to internet",
                'details': [p for p in host_info.get('ports', []) if p in [1433, 3306, 5432, 6379, 27017, 9200]]
            })

        if findings:
            host_info['high_value_findings'] = findings
            self.results['high_value_findings'].extend(findings)

    def _is_high_value(self, host_info: Dict) -> bool:
        """Determine if a host is high-value"""
        if host_info.get('vulns'):
            return True
        if host_info.get('high_value_findings'):
            return True
        if any(p in host_info.get('ports', []) for p in [3389, 5900, 23, 1433, 3306, 5432, 27017]):
            return True
        return False

    def save_results(self, output_file: Path):
        """Save scan results to JSON file"""
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)

            logger.info(f"Shodan results saved to {output_file}")

        except Exception as e:
            logger.error(f"Error saving Shodan results: {e}")

    def generate_report(self) -> Dict:
        """Generate a summary report of Shodan findings"""
        report = {
            'summary': {
                'total_hosts': len(self.results['hosts']),
                'with_vulnerabilities': sum(1 for h in self.results['hosts'].values() if h.get('vulns')),
                'high_value_hosts': sum(1 for h in self.results['hosts'].values() if self._is_high_value(h)),
                'total_findings': len(self.results['high_value_findings'])
            },
            'top_vulnerabilities': [],
            'top_services': [],
            'top_organizations': []
        }

        # Count vulnerabilities
        vuln_counts = {}
        for host in self.results['hosts'].values():
            for vuln in host.get('vulns', []):
                vuln_counts[vuln] = vuln_counts.get(vuln, 0) + 1

        report['top_vulnerabilities'] = sorted(
            [{'cve': k, 'count': v} for k, v in vuln_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]

        # Count services
        service_counts = {}
        for host in self.results['hosts'].values():
            for service in host.get('services', []):
                port = service.get('port')
                product = service.get('product', 'unknown')
                key = f"{product}:{port}"
                service_counts[key] = service_counts.get(key, 0) + 1

        report['top_services'] = sorted(
            [{'service': k, 'count': v} for k, v in service_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]

        # Count organizations
        org_counts = {}
        for host in self.results['hosts'].values():
            org = host.get('org', 'unknown')
            org_counts[org] = org_counts.get(org, 0) + 1

        report['top_organizations'] = sorted(
            [{'org': k, 'count': v} for k, v in org_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]

        return report


def main():
    """Example usage"""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python shodan_scanner.py <api_key> <domain|ip>")
        sys.exit(1)

    api_key = sys.argv[1]
    target = sys.argv[2]

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Initialize scanner
    scanner = ShodanScanner(api_key)

    # Get API info
    info = scanner.get_api_info()
    print(f"\n[*] Shodan Account: {info.get('plan', 'unknown')}")
    print(f"[*] Query Credits: {info.get('query_credits', 0)}")

    # Check if target is IP or domain
    if target.replace('.', '').isdigit():
        # IP lookup
        print(f"\n[*] Looking up IP: {target}")
        result = scanner.host_lookup(target)
        if result:
            print(f"\n[+] Results:")
            print(f"  Organization: {result.get('org')}")
            print(f"  Open Ports: {', '.join(map(str, result.get('ports', [])))}")
            print(f"  Vulnerabilities: {len(result.get('vulns', []))}")
    else:
        # Domain search
        print(f"\n[*] Searching domain: {target}")
        results = scanner.search_domain(target)
        print(f"\n[+] Found {results['total']} results")

        for match in results['matches'][:5]:
            print(f"\n  IP: {match['ip']}")
            print(f"  Port: {match['port']}")
            print(f"  Product: {match.get('product', 'unknown')}")
            if match.get('vulns'):
                print(f"  Vulnerabilities: {len(match['vulns'])}")

    # Generate report
    report = scanner.generate_report()
    print(f"\n[*] Summary:")
    print(f"  Total Hosts: {report['summary']['total_hosts']}")
    print(f"  With Vulnerabilities: {report['summary']['with_vulnerabilities']}")
    print(f"  High-Value Hosts: {report['summary']['high_value_hosts']}")


if __name__ == '__main__':
    main()
