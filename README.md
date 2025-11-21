# Bug Bounty Monitoring Framework

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/yourusername/bb-monitor/graphs/commit-activity)

A comprehensive, automated monitoring framework for bug bounty hunters. Track changes in target infrastructure, detect subdomain takeovers, monitor HTTP endpoints, and get instant notifications for high-value findings.

## 🎯 Features

### Core Capabilities

- **🔍 Multi-Source Subdomain Discovery**
  - Integrates 5+ tools (subfinder, assetfinder, crt.sh, chaos, amass)
  - Parallel execution for maximum speed
  - Deduplication and validation with dnsx

- **🚨 Subdomain Takeover Detection**
  - Checks 20+ cloud services (Vercel, Netlify, GitHub Pages, Heroku, AWS S3, Azure, etc.)
  - CNAME analysis and HTTP fingerprinting
  - Confidence scoring (medium/high)

- **📊 Enhanced HTTP Monitoring**
  - Tracks: status code, title, body length, technologies, headers
  - Content hashing for change detection
  - Smart flagging for high-value targets (admin, login, upload, api, backup)
  - Detects outdated/vulnerable technologies

- **🔔 Smart Change Detection**
  - Status code changes (404→200, 403→200)
  - Title and content changes
  - Technology stack updates
  - New security issues
  - Threshold-based filtering (ignore minor changes)

- **📢 Multi-Platform Notifications**
  - Slack, Discord, Telegram, Email
  - Configurable triggers
  - Daily digests and instant alerts
  - Priority-based routing

- **📈 Visual Reporting**
  - HTML reports with highlights
  - Terminal dashboard (simple & interactive)
  - JSON exports for automation
  - Historical tracking

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/bb-monitor.git
cd bb-monitor

# Run installation script
chmod +x utils/install.sh
./utils/install.sh

# Or install dependencies manually
pip3 install -r requirements.txt

# Install Go-based tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/tomnomnom/assetfinder@latest
```

### Basic Usage

```bash
# 1. Add your targets
echo "hackerone.com" >> targets.txt
echo "bugcrowd.com" >> targets.txt

# 2. Collect initial baseline
./monitor.py --init

# 3. Run monitoring
./monitor.py --monitor

# 4. View dashboard
./modules/dashboard.py

# 5. Setup automation (optional)
./utils/setup_cron.sh
```

## 📁 Project Structure

```
bb-monitor/
├── monitor.py              # Main monitoring script
├── config.yaml            # Configuration file
├── targets.txt            # Target domains list
│
├── modules/               # Core modules
│   ├── __init__.py
│   ├── subdomain_finder.py    # Subdomain discovery & takeover detection
│   ├── http_monitor.py        # HTTP monitoring & flagging
│   ├── dashboard.py           # Terminal dashboard
│   └── notifier.py            # Multi-platform notifications
│
├── utils/                 # Utility scripts
│   ├── install.sh             # Installation script
│   ├── setup_cron.sh          # Cron automation setup
│   └── subdomain_scan.sh      # Standalone subdomain scanner
│
├── docs/                  # Documentation
│   ├── USAGE.md              # Detailed usage guide
│   ├── CONFIGURATION.md      # Configuration reference
│   └── TROUBLESHOOTING.md    # Common issues & solutions
│
├── data/                  # Data directory (auto-created)
│   ├── baseline/             # Baseline snapshots
│   ├── diffs/                # Change detections
│   └── subdomain_scans/      # Subdomain scan results
│
└── reports/               # Generated reports (auto-created)
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
# Target configuration
targets:
  domains_file: targets.txt

# Monitoring settings
monitoring:
  schedule: "0 */6 * * *"  # Every 6 hours
  retention_days: 30

# Enable/disable checks
checks:
  infrastructure:
    subdomain_discovery: true
  web_application:
    http_responses: true
  content_discovery:
    javascript_files: true

# Notifications
notifications:
  slack:
    enabled: true
    webhook_url: "YOUR_WEBHOOK_URL"
    notify_on:
      - new_subdomain
      - new_endpoint
      - subdomain_takeover
      - high_value_target
```

## 📖 Usage Examples

### Standalone Subdomain Scanner

```bash
# Basic scan
./utils/subdomain_scan.sh -d example.com

# Quick scan (subfinder + crt.sh only)
./utils/subdomain_scan.sh -d example.com -q

# Full scan with all tools
./utils/subdomain_scan.sh -d example.com -f

# Custom output directory
./utils/subdomain_scan.sh -d example.com -o /tmp/results
```

### HTTP Monitoring

```bash
# Probe URLs from file
./modules/http_monitor.py -l urls.txt

# Save snapshot
./modules/http_monitor.py -l urls.txt -s baseline.json

# Compare changes
./modules/http_monitor.py -l urls.txt -s current.json -c baseline.json
```

### Automated Monitoring

```bash
# Setup cron job (runs every 6 hours)
./utils/setup_cron.sh

# View logs
tail -f logs/monitor.log

# View dashboard
./modules/dashboard.py --interactive
```

## 🎯 Real-World Example

```bash
$ ./monitor.py --monitor

============================================================
Changes detected for: target.com
============================================================

[+] New Subdomains (3):
  + admin-staging.target.com
  + api-v3.target.com
  + backup.target.com

[!!!] POTENTIAL SUBDOMAIN TAKEOVERS (1):
  [!] old-app.target.com
      Service: heroku
      CNAME: old-app.herokuapp.com
      Confidence: high
      Fingerprint: No such app

[+] New Endpoints (2):
  + https://admin-staging.target.com
  + https://api-v3.target.com/upload

[~] Changed Endpoints (1):
  ~ https://target.com/dashboard
    Status: 403 → 200
    Title: Access Denied → Admin Dashboard
    Body Length: 1,234 → 15,678 (1170% change)
    [!] FLAG: High-value target: admin (dashboard in URL)
    [!] FLAG: Outdated technology: Apache 2.4.49
```

## 🏆 High-Value Findings

The framework automatically flags:

| Category | Keywords | Priority | What to Test |
|----------|----------|----------|--------------|
| **Admin** | admin, administrator, console, dashboard | 🔴 High | Default creds, SQLi, auth bypass |
| **Upload** | upload, uploader, file, attachment | 🔴 High | File upload bypass, RCE |
| **Backup** | backup, bak, old, archive, dump | 🔴 High | File download, info disclosure |
| **Auth** | login, signin, auth, sso, oauth | 🔴 High | Auth bypass, credential stuffing |
| **API** | api, graphql, rest, endpoint | 🟡 Medium | IDOR, broken auth |
| **Dev** | dev, staging, test, debug | 🟡 Medium | Debug info, test accounts |

## 🔐 Vulnerability Detection

Automatically detects outdated/vulnerable technologies:

- Apache 2.4.49, 2.4.50 (CVE-2021-41773 - Path Traversal)
- PHP 7.3, 7.4, 5.6 (End of life, multiple CVEs)
- WordPress < 6.0
- jQuery 1.x, 2.x, 3.0-3.2
- Drupal 7.x, 8.x
- And more...

## 📊 Performance

- **Subdomain Discovery**: 5-15 min (full scan), 2-3 min (quick scan)
- **HTTP Probing**: 20-50 URLs/second (parallel)
- **Change Detection**: <1 minute
- **Resource Usage**: ~200MB RAM per domain

## 🛠️ Dependencies

### Required
```bash
# Python packages
pip3 install requests beautifulsoup4 pyyaml

# Go tools
subfinder   # Subdomain discovery
httpx       # HTTP probing
dnsx        # DNS validation
```

### Optional
```bash
assetfinder # Additional subdomain sources
amass       # Comprehensive enumeration (slower)
katana      # Web crawling
nuclei      # Vulnerability scanning
```

## 📚 Documentation

- **[docs/USAGE.md](docs/USAGE.md)** - Detailed usage guide
- **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Configuration reference
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues & solutions

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for authorized security testing only. Always obtain proper permission before testing any targets. The authors are not responsible for any misuse or damage caused by this tool.

## 🙏 Credits

Built with:
- [subfinder](https://github.com/projectdiscovery/subfinder) - Subdomain discovery
- [httpx](https://github.com/projectdiscovery/httpx) - HTTP probing
- [dnsx](https://github.com/projectdiscovery/dnsx) - DNS validation
- [assetfinder](https://github.com/tomnomnom/assetfinder) - Asset discovery
- [crt.sh](https://crt.sh) - Certificate transparency
- [chaos](https://chaos.projectdiscovery.io) - Curated dataset

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/bb-monitor/issues)
- **Twitter**: [@yourusername](https://twitter.com/yourusername)
- **Email**: your.email@example.com

## ⭐ Star History

If you find this tool useful, please consider giving it a star!

---

**Happy Hunting!** 🎯
