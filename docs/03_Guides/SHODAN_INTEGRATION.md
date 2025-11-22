# Shodan Integration Guide

## Overview

The Bug Bounty Monitoring Framework integrates with Shodan API to provide internet-wide asset intelligence for your targets. This integration helps identify open ports, exposed services, known vulnerabilities, and other security-relevant information about your discovered assets.

## Features

### 🔍 Asset Discovery
- **IP Address Lookup**: Get detailed information about specific IPs
- **Domain Search**: Find all hosts associated with a domain
- **DNS Resolution**: Resolve subdomains to IP addresses
- **Reverse DNS**: Get hostnames for IP addresses

### 🛡️ Security Intelligence
- **Open Ports**: Identify all open ports on discovered hosts
- **Service Detection**: Detect running services and versions
- **Vulnerability Detection**: Find known CVEs affecting targets
- **Exposed Services**: Flag dangerous exposures (RDP, databases, etc.)

### 📊 Enrichment Data
- **Organization Info**: ISP, ASN, organization name
- **Geolocation**: Country, city, coordinates
- **Technology Stack**: Web servers, frameworks, products
- **SSL Certificates**: Certificate information
- **HTTP Headers**: Server headers and configurations

## Setup

### 1. Get Shodan API Key

1. Sign up at [https://account.shodan.io/register](https://account.shodan.io/register)
2. Log in and visit [https://account.shodan.io/](https://account.shodan.io/)
3. Copy your API key from the account page

**Plans**:
- **Free**: 100 query credits/month (suitable for small targets)
- **Membership**: $59/month - unlimited query credits (recommended for bug bounty)
- **Enterprise**: Custom pricing

### 2. Configure in config.yaml

```yaml
tools:
  shodan:
    enabled: true
    api_key: "YOUR_SHODAN_API_KEY"
    max_results: 100
    timeout: 30
    rate_limit_delay: 1  # Seconds between requests
    scan_on:
      - new_subdomain      # Scan newly discovered subdomains
      - baseline_init      # Scan during initial baseline
    lookup_ips: true       # Lookup resolved IPs
    dns_resolve: true      # Use Shodan DNS for resolution
```

### 3. Using Environment Variables (Recommended)

```bash
# Set environment variable
export BB_SHODAN_API_KEY="your_shodan_api_key"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export BB_SHODAN_API_KEY="your_shodan_api_key"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### Automatic Scanning

Shodan will run automatically when enabled during:

1. **Baseline Collection** (`--init`):
```bash
./monitor.py --init
```

2. **Monitoring** (`--monitor`) when new subdomains are discovered:
```bash
./monitor.py --monitor
```

### Standalone Usage

```bash
# Domain search
python3 modules/shodan_scanner.py YOUR_API_KEY example.com

# IP lookup
python3 modules/shodan_scanner.py YOUR_API_KEY 8.8.8.8
```

### Python Integration

```python
from modules.shodan_scanner import ShodanScanner

# Initialize scanner
scanner = ShodanScanner(api_key="YOUR_API_KEY")

# Get API info
info = scanner.get_api_info()
print(f"Query credits: {info['query_credits']}")

# Domain search
results = scanner.search_domain("example.com")
print(f"Found {results['total']} hosts")

# IP lookup
host_info = scanner.host_lookup("8.8.8.8")
print(f"Open ports: {host_info['ports']}")
print(f"Vulnerabilities: {host_info['vulns']}")

# Scan multiple subdomains
subdomains = ["www.example.com", "api.example.com", "mail.example.com"]
scan_results = scanner.scan_subdomains(subdomains)
print(f"Resolved: {scan_results['summary']['resolved']}")
print(f"With vulnerabilities: {scan_results['summary']['with_vulns']}")

# Generate report
report = scanner.generate_report()
print(report['summary'])
```

## Output Data

### Baseline Data

Shodan results are stored in the baseline:

```json
{
  "domain": "example.com",
  "shodan_data": {
    "domain_search": {
      "total": 25,
      "matches": [...]
    },
    "subdomain_scans": {
      "resolved": {
        "www.example.com": "93.184.216.34",
        "api.example.com": "93.184.216.35"
      },
      "hosts": {
        "93.184.216.34": {
          "ip": "93.184.216.34",
          "hostnames": ["www.example.com"],
          "org": "Example Inc",
          "ports": [80, 443],
          "vulns": ["CVE-2021-1234"],
          "services": [...]
        }
      }
    },
    "summary": {
      "total_hosts": 10,
      "with_vulnerabilities": 2,
      "high_value_hosts": 1
    }
  }
}
```

### Detailed Scan Files

Full scan results are saved to `data/shodan_scans/`:

```
data/shodan_scans/
├── example.com_20250121_140530.json
└── target.com_20250121_141230.json
```

## High-Value Findings

The scanner automatically flags these security issues:

### 🔴 High Severity
- **Known Vulnerabilities**: CVEs with public exploits
- **Exposed Remote Access**: RDP (3389), VNC (5900), Telnet (23)
- **Exposed Databases**: MySQL (3306), PostgreSQL (5432), MongoDB (27017), Redis (6379), Elasticsearch (9200)

### 🟡 Medium Severity
- **High-Value Ports**: FTP (21), SSH (22), SMTP (25), SMB (445), MSSQL (1433)
- **Vulnerable Products**: Outdated Apache, nginx, IIS, OpenSSH

### Example Output

```bash
[*] Running Shodan scans...
  [Shodan] Plan: member, Credits: 9847
  [Shodan] Searching domain: example.com
  [Shodan] Scanning 25 subdomains...
[+] Shodan scan completed
  [Shodan] Hosts scanned: 15
  [Shodan] With vulnerabilities: 3
  [Shodan] High-value hosts: 2
```

## Notifications

High-value Shodan findings trigger notifications:

```yaml
notifications:
  slack:
    notify_on:
      - shodan_vulnerabilities  # Hosts with CVEs
      - exposed_database        # Database services exposed
      - exposed_remote_access   # RDP, VNC, Telnet exposed
```

Example notification:
```
🚨 Shodan Alert: example.com

Vulnerabilities Found: 3 hosts
High-Value Hosts: 2

Details:
• 93.184.216.34: MongoDB exposed on port 27017
• 93.184.216.35: 2 CVEs found (CVE-2021-1234, CVE-2021-5678)
```

## Best Practices

### 1. API Credit Management

```yaml
# Limit scans to conserve credits
tools:
  shodan:
    max_results: 50          # Limit results per search
    scan_on:
      - baseline_init         # Only scan during baseline, not every monitor run
    lookup_ips: true          # Balance between coverage and credit usage
```

**Credit Usage**:
- Domain search: 1 credit
- IP lookup: 1 credit
- DNS resolution: Free (but limited to 100 at a time)

### 2. Rate Limiting

```yaml
tools:
  shodan:
    rate_limit_delay: 1  # Wait 1 second between requests
```

Shodan API limits:
- Free: 1 request/second
- Membership: No rate limit (but be reasonable)

### 3. Targeted Scanning

Focus on high-value targets:

```python
# Only scan specific subdomains
priority_subs = [sub for sub in all_subdomains if 'api' in sub or 'admin' in sub]
results = scanner.scan_subdomains(priority_subs)
```

### 4. Scheduled Full Scans

Run comprehensive Shodan scans weekly:

```bash
# Weekly deep scan with Shodan
0 0 * * 0 cd /path/to/bb-monitor && ./monitor.py --init >> logs/weekly_scan.log 2>&1
```

## Troubleshooting

### No API Key

```
[!] Shodan enabled but no API key provided
```

**Solution**: Set API key in config.yaml or environment variable:
```bash
export BB_SHODAN_API_KEY="your_api_key"
```

### API Error: Unauthorized

```
[!] Shodan scan error: 401 Unauthorized
```

**Solution**: Check your API key is correct:
```bash
# Test API key
curl "https://api.shodan.io/api-info?key=YOUR_API_KEY"
```

### Rate Limit Exceeded

```
[!] Shodan scan error: 429 Too Many Requests
```

**Solution**: Increase rate_limit_delay:
```yaml
tools:
  shodan:
    rate_limit_delay: 2  # Increase delay
```

### Insufficient Credits

```
[!] Shodan scan error: 402 Payment Required
```

**Solution**:
1. Check remaining credits: `scanner.get_api_info()`
2. Upgrade plan at https://account.shodan.io/billing
3. Or reduce scan frequency

### Module Not Found

```
ImportError: No module named 'shodan'
```

**Solution**: Install shodan package:
```bash
pip3 install shodan
```

## Advanced Usage

### Custom Queries

```python
from modules.shodan_scanner import ShodanScanner

scanner = ShodanScanner(api_key="YOUR_API_KEY")

# Search for specific vulnerabilities
results = scanner.search("hostname:example.com vuln:CVE-2021-1234")

# Search for specific products
results = scanner.search("hostname:example.com product:Apache")

# Search for open ports
results = scanner.search("hostname:example.com port:3306")
```

### Faceted Search

```python
# Get statistics by country, port, organization
results = scanner.search(
    "hostname:example.com",
    facets=['country', 'port', 'org']
)

print(results['facets']['country'])  # Hosts by country
print(results['facets']['port'])     # Open ports distribution
```

### CVE Lookup

```python
# Check specific CVE details
from shodan import Shodan

api = Shodan('YOUR_API_KEY')
cve = api.exploits.search('CVE-2021-1234')
print(cve['matches'][0]['description'])
```

## Integration with Other Tools

### With Nuclei

After Shodan identifies vulnerable versions:

```bash
# Get IPs with specific vulnerability
python3 -c "
from modules.shodan_scanner import ShodanScanner
scanner = ShodanScanner('YOUR_API_KEY')
results = scanner.search('hostname:example.com vuln:CVE-2021-1234')
for match in results['matches']:
    print(f'http://{match[\"ip_str\"]}')
" | nuclei -t cves/2021/CVE-2021-1234.yaml
```

### With Nmap

Follow up Shodan results with detailed port scans:

```bash
# Export IPs from Shodan results
cat data/shodan_scans/example.com_*.json | jq -r '.hosts | keys[]' > ips.txt

# Scan with nmap
nmap -sV -iL ips.txt -oA nmap_scan
```

## Privacy & Ethics

### Responsible Usage

1. **Authorized Targets Only**: Only scan domains you have permission to test
2. **Respect Rate Limits**: Don't hammer the Shodan API
3. **Verify Findings**: Confirm vulnerabilities before reporting
4. **Responsible Disclosure**: Report findings through proper channels

### Data Handling

- Shodan data contains sensitive information
- Store scan results securely
- Don't share raw Shodan results publicly
- Respect program disclosure policies

## Resources

- **Shodan Website**: https://www.shodan.io/
- **Shodan CLI**: https://cli.shodan.io/
- **API Documentation**: https://developer.shodan.io/api
- **Search Guide**: https://www.shodan.io/search/filters
- **Python Library**: https://shodan.readthedocs.io/

## Examples

### Example 1: Find Exposed Admin Panels

```python
scanner = ShodanScanner(api_key="YOUR_API_KEY")
results = scanner.search('hostname:example.com title:"admin" port:80,443')

for match in results['matches']:
    print(f"{match['ip']}:{match['port']} - {match.get('http', {}).get('title', 'N/A')}")
```

### Example 2: Identify Outdated Software

```python
scanner = ShodanScanner(api_key="YOUR_API_KEY")
results = scanner.search('hostname:example.com product:Apache version:2.4.49')

if results['total'] > 0:
    print(f"⚠️  Found {results['total']} hosts running vulnerable Apache 2.4.49 (CVE-2021-41773)")
```

### Example 3: Monitor New Assets

```python
# During monitoring
new_subdomains = ['new-api.example.com', 'staging.example.com']

scanner = ShodanScanner(api_key="YOUR_API_KEY")
results = scanner.scan_subdomains(new_subdomains)

if results['summary']['with_vulns'] > 0:
    print(f"🚨 {results['summary']['with_vulns']} new subdomains have vulnerabilities!")
```

---

For more information, see:
- [CONFIGURATION.md](CONFIGURATION.md) - Full configuration reference
- [USAGE.md](USAGE.md) - Detailed usage guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
