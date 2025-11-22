#!/usr/bin/env python3
"""
Wayback Machine URL Analyzer
Fetches historical URLs from Wayback Machine and classifies them by file type
"""

import re
import json
import requests
from typing import Dict, List, Set, Optional, Any
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
from datetime import datetime
import time


class WaybackAnalyzer:
    """
    Analyzes domains using Wayback Machine to discover:
    - Historical URLs
    - Interesting file types (backups, configs, databases, etc.)
    - Sensitive endpoints
    - Parameter patterns
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_results = self.config.get('max_results', 10000)
        self.timeout = self.config.get('timeout', 30)
        self.rate_limit = self.config.get('rate_limit_delay', 1)

        # File type classifications
        self.file_categories = {
            'backup': {
                'extensions': ['.bak', '.backup', '.old', '.orig', '.save', '.swp', '.tmp',
                              '.~', '.copy', '.db.bak', '.sql.bak', '.tar.gz', '.zip', '.rar'],
                'keywords': ['backup', 'old', 'copy', 'archive', 'dump'],
                'priority': 'high'
            },
            'database': {
                'extensions': ['.sql', '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb',
                              '.pdb', '.dbf', '.dump'],
                'keywords': ['database', 'dump', 'export', 'mysql', 'postgres', 'mongodb'],
                'priority': 'high'
            },
            'config': {
                'extensions': ['.conf', '.config', '.cfg', '.ini', '.env', '.yml', '.yaml',
                              '.properties', '.xml', '.json', '.toml'],
                'keywords': ['config', 'configuration', 'settings', 'env', 'environment'],
                'priority': 'high'
            },
            'source_code': {
                'extensions': ['.php', '.asp', '.aspx', '.jsp', '.java', '.py', '.rb',
                              '.pl', '.cgi', '.sh', '.bat', '.ps1'],
                'keywords': ['source', 'src', 'code'],
                'priority': 'medium'
            },
            'documents': {
                'extensions': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                              '.odt', '.ods', '.odp', '.rtf', '.txt', '.csv'],
                'keywords': ['document', 'report', 'spreadsheet', 'presentation'],
                'priority': 'medium'
            },
            'credentials': {
                'extensions': ['.key', '.pem', '.p12', '.pfx', '.jks', '.keystore',
                              '.crt', '.cer', '.der'],
                'keywords': ['password', 'passwd', 'pwd', 'credential', 'secret',
                            'key', 'token', 'auth', 'certificate', 'private'],
                'priority': 'critical'
            },
            'logs': {
                'extensions': ['.log', '.logs', '.out', '.err', '.trace'],
                'keywords': ['log', 'logs', 'error', 'debug', 'trace'],
                'priority': 'medium'
            },
            'api_docs': {
                'extensions': ['.wsdl', '.wadl', '.raml', '.swagger', '.openapi'],
                'keywords': ['api', 'swagger', 'openapi', 'graphql', 'rest', 'soap'],
                'priority': 'high'
            },
            'version_control': {
                'extensions': ['.git', '.svn', '.hg', '.bzr'],
                'keywords': ['git', 'svn', 'mercurial', 'bazaar', '.git/config'],
                'priority': 'critical'
            },
            'sensitive': {
                'extensions': [],
                'keywords': ['admin', 'dashboard', 'panel', 'console', 'cpanel',
                            'phpmyadmin', 'upload', 'backup', 'test', 'dev', 'staging'],
                'priority': 'high'
            }
        }

        # High-value parameter names
        self.interesting_params = [
            'id', 'user', 'username', 'email', 'file', 'path', 'url', 'redirect',
            'next', 'return', 'callback', 'debug', 'admin', 'token', 'api_key',
            'key', 'secret', 'password', 'query', 'search', 'q', 'page', 'redirect_uri'
        ]

    def fetch_urls(self, domain: str, filters: List[str] = None) -> List[str]:
        """
        Fetch URLs from Wayback Machine CDX API

        Args:
            domain: Target domain
            filters: Optional list of filters (e.g., ['statuscode:200', 'mimetype:text/html'])

        Returns:
            List of URLs
        """
        print(f"[*] Fetching URLs from Wayback Machine for {domain}...")

        # CDX API endpoint
        cdx_url = "http://web.archive.org/cdx/search/cdx"

        params = {
            'url': f'*.{domain}/*',
            'output': 'json',
            'fl': 'original,statuscode,mimetype,timestamp',
            'collapse': 'urlkey',  # Remove duplicates
            'limit': self.max_results
        }

        # Add filters if provided
        if filters:
            params['filter'] = filters

        urls = []

        try:
            response = requests.get(cdx_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Skip header row
            if data and len(data) > 1:
                for entry in data[1:]:
                    if len(entry) >= 1:
                        url = entry[0]
                        urls.append(url)

            print(f"[+] Found {len(urls)} URLs from Wayback Machine")

        except requests.exceptions.RequestException as e:
            print(f"[!] Error fetching Wayback data: {e}")
        except json.JSONDecodeError as e:
            print(f"[!] Error parsing Wayback response: {e}")

        return urls

    def classify_url(self, url: str) -> Dict[str, Any]:
        """
        Classify URL by file type and extract useful information

        Returns:
            Dict with classification info
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        query = parsed.query.lower()

        classification = {
            'url': url,
            'categories': [],
            'priority': 'low',
            'file_extension': None,
            'has_parameters': bool(parsed.query),
            'parameter_names': [],
            'interesting_params': [],
            'path_parts': parsed.path.split('/'),
            'score': 0
        }

        # Extract file extension
        if '.' in path:
            ext = '.' + path.split('.')[-1]
            classification['file_extension'] = ext

        # Classify by categories
        for category, rules in self.file_categories.items():
            matched = False

            # Check extensions
            if classification['file_extension']:
                for ext in rules['extensions']:
                    if classification['file_extension'] == ext or path.endswith(ext):
                        matched = True
                        break

            # Check keywords in path
            if not matched:
                for keyword in rules['keywords']:
                    if keyword in path or keyword in query:
                        matched = True
                        break

            if matched:
                classification['categories'].append(category)

                # Update priority (critical > high > medium > low)
                current_priority = classification['priority']
                new_priority = rules['priority']

                priority_levels = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
                if priority_levels.get(new_priority, 0) > priority_levels.get(current_priority, 0):
                    classification['priority'] = new_priority

        # Extract parameters
        if parsed.query:
            params = parse_qs(parsed.query)
            classification['parameter_names'] = list(params.keys())

            # Check for interesting parameters
            for param in classification['parameter_names']:
                if param.lower() in self.interesting_params:
                    classification['interesting_params'].append(param)

        # Calculate score
        score = 0
        score += len(classification['categories']) * 10
        score += len(classification['interesting_params']) * 5

        if classification['priority'] == 'critical':
            score += 50
        elif classification['priority'] == 'high':
            score += 30
        elif classification['priority'] == 'medium':
            score += 10

        classification['score'] = score

        return classification

    def analyze_domain(self, domain: str, output_file: str = None) -> Dict[str, Any]:
        """
        Analyze domain and classify all discovered URLs

        Returns:
            Analysis results with categorized URLs
        """
        print(f"\n[*] Starting Wayback analysis for {domain}")
        print("=" * 60)

        # Fetch URLs
        urls = self.fetch_urls(domain)

        if not urls:
            print("[!] No URLs found")
            return {
                'domain': domain,
                'total_urls': 0,
                'categorized': {},
                'high_value': [],
                'timestamp': datetime.now().isoformat()
            }

        # Classify all URLs
        print(f"[*] Classifying {len(urls)} URLs...")

        categorized = defaultdict(list)
        all_classifications = []
        extensions_count = defaultdict(int)
        parameters_count = defaultdict(int)

        for url in urls:
            classification = self.classify_url(url)
            all_classifications.append(classification)

            # Group by categories
            if classification['categories']:
                for category in classification['categories']:
                    categorized[category].append(classification)
            else:
                categorized['uncategorized'].append(classification)

            # Count extensions
            if classification['file_extension']:
                extensions_count[classification['file_extension']] += 1

            # Count parameters
            for param in classification['parameter_names']:
                parameters_count[param] += 1

        # Sort each category by score
        for category in categorized:
            categorized[category].sort(key=lambda x: x['score'], reverse=True)

        # Extract high-value URLs (score > 20 or critical/high priority)
        high_value = [
            c for c in all_classifications
            if c['score'] > 20 or c['priority'] in ['critical', 'high']
        ]
        high_value.sort(key=lambda x: x['score'], reverse=True)

        # Prepare results
        results = {
            'domain': domain,
            'total_urls': len(urls),
            'categorized': dict(categorized),
            'high_value': high_value[:100],  # Top 100 high-value URLs
            'statistics': {
                'by_category': {cat: len(urls) for cat, urls in categorized.items()},
                'by_extension': dict(extensions_count),
                'by_priority': {
                    'critical': len([c for c in all_classifications if c['priority'] == 'critical']),
                    'high': len([c for c in all_classifications if c['priority'] == 'high']),
                    'medium': len([c for c in all_classifications if c['priority'] == 'medium']),
                    'low': len([c for c in all_classifications if c['priority'] == 'low'])
                },
                'top_parameters': dict(sorted(parameters_count.items(), key=lambda x: x[1], reverse=True)[:20]),
                'with_parameters': len([c for c in all_classifications if c['has_parameters']]),
                'interesting_parameters': len([c for c in all_classifications if c['interesting_params']])
            },
            'timestamp': datetime.now().isoformat()
        }

        # Print summary
        self._print_summary(results)

        # Save results if output file specified
        if output_file:
            self._save_results(results, output_file)

        return results

    def _print_summary(self, results: Dict[str, Any]):
        """Print analysis summary"""
        print(f"\n{'='*60}")
        print(f"Wayback Analysis Summary: {results['domain']}")
        print(f"{'='*60}")

        print(f"\n[+] Total URLs: {results['total_urls']}")

        print(f"\n[+] URLs by Category:")
        for category, count in sorted(results['statistics']['by_category'].items(),
                                      key=lambda x: x[1], reverse=True):
            print(f"    {category:20} {count:6} URLs")

        print(f"\n[+] URLs by Priority:")
        for priority, count in results['statistics']['by_priority'].items():
            if count > 0:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '⚪'}.get(priority, '')
                print(f"    {emoji} {priority:10} {count:6} URLs")

        print(f"\n[+] Top File Extensions:")
        for ext, count in sorted(results['statistics']['by_extension'].items(),
                                 key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {ext:15} {count:6} URLs")

        print(f"\n[+] Parameter Statistics:")
        print(f"    URLs with parameters: {results['statistics']['with_parameters']}")
        print(f"    Interesting parameters: {results['statistics']['interesting_parameters']}")

        if results['statistics']['top_parameters']:
            print(f"\n[+] Top Parameters:")
            for param, count in list(results['statistics']['top_parameters'].items())[:10]:
                print(f"    {param:20} {count:6} times")

        if results['high_value']:
            print(f"\n[!!!] High-Value URLs Found: {len(results['high_value'])}")
            print("\n    Top 10 High-Value URLs:")
            for i, item in enumerate(results['high_value'][:10], 1):
                categories = ', '.join(item['categories']) if item['categories'] else 'uncategorized'
                print(f"    {i:2}. [{item['priority']:8}] {item['url']}")
                print(f"        Categories: {categories}")
                print(f"        Score: {item['score']}")

    def _save_results(self, results: Dict[str, Any], output_file: str):
        """Save results to JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n[+] Results saved to {output_file}")
        except Exception as e:
            print(f"[!] Error saving results: {e}")

    def extract_urls_by_category(self, results: Dict[str, Any], category: str) -> List[str]:
        """Extract URLs from a specific category"""
        if category in results['categorized']:
            return [item['url'] for item in results['categorized'][category]]
        return []

    def export_category_urls(self, results: Dict[str, Any], category: str, output_file: str):
        """Export URLs from a category to a text file"""
        urls = self.extract_urls_by_category(results, category)

        if urls:
            try:
                with open(output_file, 'w') as f:
                    for url in urls:
                        f.write(f"{url}\n")
                print(f"[+] Exported {len(urls)} {category} URLs to {output_file}")
            except Exception as e:
                print(f"[!] Error exporting URLs: {e}")
        else:
            print(f"[!] No URLs found in category: {category}")

    def get_all_urls(self, results: Dict[str, Any]) -> List[str]:
        """Get all unique URLs from results"""
        urls = set()
        for category_urls in results['categorized'].values():
            for item in category_urls:
                urls.add(item['url'])
        return sorted(list(urls))


def main():
    """Standalone usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Wayback Machine URL Analyzer')
    parser.add_argument('domain', help='Target domain (e.g., example.com)')
    parser.add_argument('-o', '--output', help='Output JSON file', default=None)
    parser.add_argument('-c', '--category', help='Export specific category to file')
    parser.add_argument('-m', '--max-results', type=int, default=10000,
                       help='Maximum URLs to fetch (default: 10000)')
    parser.add_argument('--export-all', help='Export all URLs to text file')

    args = parser.parse_args()

    # Configure analyzer
    config = {
        'max_results': args.max_results,
        'timeout': 30,
        'rate_limit_delay': 1
    }

    analyzer = WaybackAnalyzer(config)

    # Analyze domain
    if args.output:
        output_file = args.output
    else:
        output_file = f"wayback_{args.domain.replace('.', '_')}.json"

    results = analyzer.analyze_domain(args.domain, output_file)

    # Export specific category if requested
    if args.category:
        category_file = f"wayback_{args.domain.replace('.', '_')}_{args.category}.txt"
        analyzer.export_category_urls(results, args.category, category_file)

    # Export all URLs if requested
    if args.export_all:
        all_urls = analyzer.get_all_urls(results)
        try:
            with open(args.export_all, 'w') as f:
                for url in all_urls:
                    f.write(f"{url}\n")
            print(f"\n[+] Exported {len(all_urls)} total URLs to {args.export_all}")
        except Exception as e:
            print(f"[!] Error exporting all URLs: {e}")

    print("\n[+] Analysis complete!")
    print(f"\nHigh-value categories to check:")
    print("  - backup: Old/backup files that might be accessible")
    print("  - database: Database dumps and exports")
    print("  - config: Configuration files (.env, .yml, etc.)")
    print("  - credentials: Keys, certificates, password files")
    print("  - version_control: Exposed .git, .svn directories")
    print("  - sensitive: Admin panels, upload endpoints, etc.")


if __name__ == '__main__':
    main()
