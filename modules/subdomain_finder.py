#!/usr/bin/env python3
"""
Enhanced Subdomain Discovery & Takeover Detection
Integrates: subfinder, amass, assetfinder, chaos, crt.sh, dnsx
Checks for: Subdomain takeover vulnerabilities
"""

import os
import sys
import json
import subprocess
import requests
import re
from pathlib import Path
from typing import Set, List, Dict, Any
from collections import defaultdict
import concurrent.futures

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class SubdomainFinder:
    def __init__(self, domain: str, output_dir: str = "./output"):
        self.domain = domain
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.subdomains = set()
        self.results = defaultdict(set)

        # Subdomain takeover signatures
        self.takeover_signatures = {
            'github': {
                'cname': ['github.io', 'github.map.fastly.net'],
                'response': ['There isn\'t a GitHub Pages site here', 'For root URLs']
            },
            'heroku': {
                'cname': ['herokuapp.com', 'herokussl.com'],
                'response': ['no-such-app.html', 'No such app']
            },
            'shopify': {
                'cname': ['myshopify.com'],
                'response': ['Sorry, this shop is currently unavailable']
            },
            'tumblr': {
                'cname': ['tumblr.com'],
                'response': ['Whatever you were looking for doesn\'t currently exist']
            },
            'wordpress': {
                'cname': ['wordpress.com'],
                'response': ['Do you want to register']
            },
            'desk': {
                'cname': ['desk.com'],
                'response': ['Please try again or try Desk.com free for']
            },
            'fastly': {
                'cname': ['fastly.net'],
                'response': ['Fastly error: unknown domain']
            },
            'feedpress': {
                'cname': ['redirect.feedpress.me'],
                'response': ['The feed has not been found']
            },
            'ghost': {
                'cname': ['ghost.io'],
                'response': ['The thing you were looking for is no longer here']
            },
            'pantheon': {
                'cname': ['pantheonsite.io'],
                'response': ['404 error unknown site']
            },
            'surge': {
                'cname': ['surge.sh'],
                'response': ['project not found']
            },
            'bitbucket': {
                'cname': ['bitbucket.io'],
                'response': ['Repository not found']
            },
            'uservoice': {
                'cname': ['uservoice.com'],
                'response': ['This UserVoice subdomain is currently unavailable']
            },
            'statuspage': {
                'cname': ['statuspage.io'],
                'response': ['Status page doesn\'t exist', 'You are being']
            },
            'zendesk': {
                'cname': ['zendesk.com'],
                'response': ['Help Center Closed']
            },
            'vercel': {
                'cname': ['vercel.app', 'now.sh'],
                'response': ['The deployment could not be found', 'DEPLOYMENT_NOT_FOUND']
            },
            'netlify': {
                'cname': ['netlify.app', 'netlify.com'],
                'response': ['Not Found - Request ID']
            },
            'aws_s3': {
                'cname': ['s3.amazonaws.com', 's3-website'],
                'response': ['NoSuchBucket', 'The specified bucket does not exist']
            },
            'azure': {
                'cname': ['azurewebsites.net', 'cloudapp.azure.com', 'cloudapp.net'],
                'response': ['404 Web Site not found', 'Error 404']
            },
            'readme': {
                'cname': ['readme.io'],
                'response': ['Project doesnt exist... yet!']
            },
            'cargo': {
                'cname': ['cargocollective.com'],
                'response': ['404 Not Found']
            },
            'webflow': {
                'cname': ['proxy.webflow.com', 'proxy-ssl.webflow.com'],
                'response': ['The page you are looking for doesn\'t exist or has been moved']
            }
        }

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
            print(f"{Colors.YELLOW}[!] Command timeout: {cmd[:50]}...{Colors.RESET}")
            return ""
        except Exception as e:
            print(f"{Colors.RED}[!] Command error: {e}{Colors.RESET}")
            return ""

    def run_subfinder(self) -> Set[str]:
        """Run subfinder for subdomain discovery"""
        print(f"{Colors.BLUE}[*] Running Subfinder...{Colors.RESET}")

        output_file = self.output_dir / "subfinder.txt"
        cmd = f"subfinder -d {self.domain} -all -recursive -silent -o {output_file}"

        self.run_command(cmd, timeout=600)

        if output_file.exists():
            with open(output_file, 'r') as f:
                subs = set([line.strip() for line in f if line.strip()])
                self.results['subfinder'] = subs
                print(f"{Colors.GREEN}[+] Subfinder: {len(subs)} subdomains{Colors.RESET}")
                return subs

        return set()

    def run_amass(self, passive: bool = True) -> Set[str]:
        """Run amass for subdomain discovery"""
        print(f"{Colors.BLUE}[*] Running Amass...{Colors.RESET}")

        output_file = self.output_dir / "amass.txt"

        if passive:
            cmd = f"amass enum -passive -d {self.domain} -o {output_file}"
        else:
            cmd = f"amass enum -d {self.domain} -o {output_file}"

        self.run_command(cmd, timeout=900)

        if output_file.exists():
            with open(output_file, 'r') as f:
                subs = set([line.strip() for line in f if line.strip()])
                self.results['amass'] = subs
                print(f"{Colors.GREEN}[+] Amass: {len(subs)} subdomains{Colors.RESET}")
                return subs

        return set()

    def run_assetfinder(self) -> Set[str]:
        """Run assetfinder for subdomain discovery"""
        print(f"{Colors.BLUE}[*] Running Assetfinder...{Colors.RESET}")

        cmd = f"assetfinder --subs-only {self.domain}"
        output = self.run_command(cmd, timeout=300)

        subs = set([line.strip() for line in output.split('\n') if line.strip()])
        self.results['assetfinder'] = subs
        print(f"{Colors.GREEN}[+] Assetfinder: {len(subs)} subdomains{Colors.RESET}")

        return subs

    def run_chaos(self) -> Set[str]:
        """Run Chaos (ProjectDiscovery) for subdomain discovery"""
        print(f"{Colors.BLUE}[*] Running Chaos Dump (ProjectDiscovery)...{Colors.RESET}")

        chaos_dir = self.output_dir / "chaos"
        chaos_dir.mkdir(exist_ok=True)

        try:
            # Download chaos index
            index_url = "https://chaos-data.projectdiscovery.io/index.json"
            response = requests.get(index_url, timeout=30)
            index_data = response.json()

            # Find domain in index
            chaos_url = None
            for entry in index_data:
                if entry.get('domain') == self.domain:
                    chaos_url = entry.get('URL')
                    break

            if chaos_url:
                print(f"{Colors.CYAN}[*] Downloading Chaos data...{Colors.RESET}")

                # Download zip file
                zip_response = requests.get(chaos_url, timeout=60)
                zip_file = chaos_dir / f"{self.domain}.zip"

                with open(zip_file, 'wb') as f:
                    f.write(zip_response.content)

                # Extract zip
                import zipfile
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(chaos_dir)

                # Read all txt files
                subs = set()
                for txt_file in chaos_dir.glob("*.txt"):
                    with open(txt_file, 'r') as f:
                        subs.update([line.strip() for line in f if line.strip()])

                # Save combined results
                chaos_output = self.output_dir / "chaos.txt"
                with open(chaos_output, 'w') as f:
                    f.write('\n'.join(sorted(subs)))

                # Cleanup
                zip_file.unlink()
                for txt_file in chaos_dir.glob("*.txt"):
                    txt_file.unlink()

                self.results['chaos'] = subs
                print(f"{Colors.GREEN}[+] Chaos Dump: {len(subs)} subdomains{Colors.RESET}")
                return subs
            else:
                print(f"{Colors.YELLOW}[-] Chaos Dump: Not found for this domain{Colors.RESET}")
                return set()

        except Exception as e:
            print(f"{Colors.RED}[!] Chaos error: {e}{Colors.RESET}")
            return set()

    def run_crtsh(self) -> Set[str]:
        """Query crt.sh for subdomain discovery"""
        print(f"{Colors.BLUE}[*] Running crt.sh...{Colors.RESET}")

        try:
            url = f"https://crt.sh/?q=%.{self.domain}&output=json"
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                data = response.json()
                subs = set()

                for entry in data:
                    name = entry.get('name_value', '')
                    # Handle multiple names separated by newlines
                    for subdomain in name.split('\n'):
                        subdomain = subdomain.strip().lower()
                        # Remove wildcards
                        subdomain = subdomain.replace('*.', '')
                        if subdomain and subdomain.endswith(self.domain):
                            subs.add(subdomain)

                self.results['crtsh'] = subs
                print(f"{Colors.GREEN}[+] crt.sh: {len(subs)} subdomains{Colors.RESET}")
                return subs
            else:
                print(f"{Colors.YELLOW}[-] crt.sh: HTTP {response.status_code}{Colors.RESET}")
                return set()

        except Exception as e:
            print(f"{Colors.RED}[!] crt.sh error: {e}{Colors.RESET}")
            return set()

    def check_dns_with_dnsx(self, subdomains: Set[str]) -> Dict[str, Any]:
        """Check DNS records with dnsx and identify potential takeovers"""
        print(f"\n{Colors.BLUE}[*] Checking DNS with dnsx...{Colors.RESET}")

        # Write subdomains to temp file
        temp_input = self.output_dir / "dnsx_input.txt"
        with open(temp_input, 'w') as f:
            f.write('\n'.join(subdomains))

        dns_results = {
            'alive': set(),
            'dead': set(),
            'cnames': {},
            'ips': {},
            'potential_takeovers': []
        }

        # Run dnsx to get A records and CNAMEs
        output_file = self.output_dir / "dnsx_output.json"
        cmd = f"dnsx -l {temp_input} -a -cname -resp -json -o {output_file} -silent"

        self.run_command(cmd, timeout=600)

        if output_file.exists():
            with open(output_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        subdomain = data.get('host', '')

                        # A records
                        a_records = data.get('a', [])
                        if a_records:
                            dns_results['alive'].add(subdomain)
                            dns_results['ips'][subdomain] = a_records

                        # CNAME records
                        cname_records = data.get('cname', [])
                        if cname_records:
                            dns_results['alive'].add(subdomain)
                            dns_results['cnames'][subdomain] = cname_records

                            # Check for potential takeover
                            takeover = self.check_takeover_signature(subdomain, cname_records)
                            if takeover:
                                dns_results['potential_takeovers'].append(takeover)

                    except json.JSONDecodeError:
                        continue

        # Find dead subdomains (no DNS records)
        dns_results['dead'] = subdomains - dns_results['alive']

        print(f"{Colors.GREEN}[+] DNS Check Complete:{Colors.RESET}")
        print(f"    Alive: {len(dns_results['alive'])}")
        print(f"    Dead: {len(dns_results['dead'])}")
        print(f"    CNAMEs: {len(dns_results['cnames'])}")

        # Cleanup
        temp_input.unlink()

        return dns_results

    def check_takeover_signature(self, subdomain: str, cnames: List[str]) -> Dict[str, Any]:
        """Check if CNAME matches known takeover patterns"""
        for cname in cnames:
            cname_lower = cname.lower()

            for service, signatures in self.takeover_signatures.items():
                # Check CNAME pattern
                for pattern in signatures['cname']:
                    if pattern in cname_lower:
                        return {
                            'subdomain': subdomain,
                            'cname': cname,
                            'service': service,
                            'confidence': 'medium'  # Will be updated after HTTP check
                        }

        return None

    def verify_takeover(self, potential_takeovers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify potential takeovers by checking HTTP response"""
        print(f"\n{Colors.YELLOW}[*] Verifying potential takeovers...{Colors.RESET}")

        verified_takeovers = []

        for takeover in potential_takeovers:
            subdomain = takeover['subdomain']
            service = takeover['service']

            # Try HTTP and HTTPS
            for protocol in ['https', 'http']:
                try:
                    url = f"{protocol}://{subdomain}"
                    response = requests.get(url, timeout=10, allow_redirects=True)
                    content = response.text

                    # Check for fingerprint in response
                    signatures = self.takeover_signatures[service]['response']
                    for signature in signatures:
                        if signature.lower() in content.lower():
                            takeover['confidence'] = 'high'
                            takeover['url'] = url
                            takeover['status_code'] = response.status_code
                            takeover['fingerprint'] = signature
                            verified_takeovers.append(takeover)

                            print(f"{Colors.RED}[!] POSSIBLE TAKEOVER:{Colors.RESET}")
                            print(f"    Subdomain: {subdomain}")
                            print(f"    Service: {service}")
                            print(f"    CNAME: {takeover['cname']}")
                            print(f"    Fingerprint: {signature}")
                            break

                    if takeover.get('confidence') == 'high':
                        break

                except Exception as e:
                    continue

        return verified_takeovers

    def save_results(self):
        """Save all results to files"""
        print(f"\n{Colors.BLUE}[*] Saving results...{Colors.RESET}")

        # Save all subdomains
        all_subs_file = self.output_dir / f"{self.domain}_all_subdomains.txt"
        with open(all_subs_file, 'w') as f:
            f.write('\n'.join(sorted(self.subdomains)))

        print(f"{Colors.GREEN}[+] All subdomains: {all_subs_file}{Colors.RESET}")

        # Save by source
        sources_file = self.output_dir / f"{self.domain}_by_source.json"
        sources_data = {source: list(subs) for source, subs in self.results.items()}

        with open(sources_file, 'w') as f:
            json.dump(sources_data, f, indent=2)

        print(f"{Colors.GREEN}[+] By source: {sources_file}{Colors.RESET}")

        # Save statistics
        stats_file = self.output_dir / f"{self.domain}_stats.txt"
        with open(stats_file, 'w') as f:
            f.write(f"Subdomain Discovery Statistics for {self.domain}\n")
            f.write("="*60 + "\n\n")

            for source, subs in sorted(self.results.items()):
                f.write(f"{source:15s}: {len(subs):5d} subdomains\n")

            f.write("\n" + "="*60 + "\n")
            f.write(f"Total Unique: {len(self.subdomains)} subdomains\n")

        print(f"{Colors.GREEN}[+] Statistics: {stats_file}{Colors.RESET}")

    def save_takeover_report(self, takeovers: List[Dict[str, Any]]):
        """Save subdomain takeover findings"""
        if not takeovers:
            return

        report_file = self.output_dir / f"{self.domain}_takeover_report.json"

        with open(report_file, 'w') as f:
            json.dump(takeovers, f, indent=2)

        print(f"\n{Colors.RED}[!] TAKEOVER REPORT: {report_file}{Colors.RESET}")

        # Also create a readable text report
        text_report = self.output_dir / f"{self.domain}_takeover_report.txt"
        with open(text_report, 'w') as f:
            f.write(f"Subdomain Takeover Report for {self.domain}\n")
            f.write("="*70 + "\n\n")

            for i, takeover in enumerate(takeovers, 1):
                f.write(f"Finding #{i}\n")
                f.write("-"*70 + "\n")
                f.write(f"Subdomain:    {takeover['subdomain']}\n")
                f.write(f"Service:      {takeover['service']}\n")
                f.write(f"CNAME:        {takeover['cname']}\n")
                f.write(f"Confidence:   {takeover['confidence']}\n")

                if 'url' in takeover:
                    f.write(f"URL:          {takeover['url']}\n")
                    f.write(f"Status Code:  {takeover['status_code']}\n")
                    f.write(f"Fingerprint:  {takeover['fingerprint']}\n")

                f.write("\n")

        print(f"{Colors.RED}[!] TEXT REPORT: {text_report}{Colors.RESET}")

    def run_all(self, check_takeover: bool = True) -> Dict[str, Any]:
        """Run all subdomain discovery tools"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}Enhanced Subdomain Discovery for: {self.domain}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

        # Run all tools in parallel for speed
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(self.run_subfinder): 'subfinder',
                executor.submit(self.run_assetfinder): 'assetfinder',
                executor.submit(self.run_crtsh): 'crtsh',
                executor.submit(self.run_chaos): 'chaos',
            }

            # Amass can be slow, run separately if needed
            # futures[executor.submit(self.run_amass)] = 'amass'

            for future in concurrent.futures.as_completed(futures):
                tool = futures[future]
                try:
                    subs = future.result()
                    self.subdomains.update(subs)
                except Exception as e:
                    print(f"{Colors.RED}[!] {tool} failed: {e}{Colors.RESET}")

        print(f"\n{Colors.BOLD}{Colors.GREEN}[+] Total unique subdomains: {len(self.subdomains)}{Colors.RESET}\n")

        # DNS checking and takeover detection
        dns_results = None
        verified_takeovers = []

        if self.subdomains and check_takeover:
            dns_results = self.check_dns_with_dnsx(self.subdomains)

            # Verify potential takeovers
            if dns_results['potential_takeovers']:
                verified_takeovers = self.verify_takeover(dns_results['potential_takeovers'])

        # Save results
        self.save_results()

        if verified_takeovers:
            self.save_takeover_report(verified_takeovers)

        return {
            'subdomains': self.subdomains,
            'by_source': self.results,
            'dns_results': dns_results,
            'takeovers': verified_takeovers
        }

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Enhanced Subdomain Discovery & Takeover Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s -d example.com
  %(prog)s -d example.com -o /tmp/output
  %(prog)s -d example.com --no-takeover
  %(prog)s -d example.com --amass
        '''
    )

    parser.add_argument('-d', '--domain', required=True, help='Target domain')
    parser.add_argument('-o', '--output', default='./output', help='Output directory')
    parser.add_argument('--no-takeover', action='store_true', help='Skip takeover detection')
    parser.add_argument('--amass', action='store_true', help='Include Amass (slower)')

    args = parser.parse_args()

    finder = SubdomainFinder(args.domain, args.output)

    # Run discovery
    results = finder.run_all(check_takeover=not args.no_takeover)

    # Print summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    print(f"Total Subdomains: {Colors.GREEN}{len(results['subdomains'])}{Colors.RESET}")
    print(f"\nBy Source:")
    for source, subs in sorted(results['by_source'].items()):
        print(f"  {source:15s}: {len(subs):5d}")

    if results['dns_results']:
        print(f"\nDNS Results:")
        print(f"  Alive:  {len(results['dns_results']['alive'])}")
        print(f"  Dead:   {len(results['dns_results']['dead'])}")
        print(f"  CNAMEs: {len(results['dns_results']['cnames'])}")

    if results['takeovers']:
        print(f"\n{Colors.RED}{Colors.BOLD}[!] Potential Takeovers: {len(results['takeovers'])}{Colors.RESET}")
        for takeover in results['takeovers']:
            print(f"  - {takeover['subdomain']} ({takeover['service']})")

    print(f"\n{Colors.GREEN}[+] Results saved to: {finder.output_dir}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
