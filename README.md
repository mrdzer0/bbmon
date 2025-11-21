# Bug Bounty Change Monitoring System

A comprehensive monitoring framework for bug bounty hunters to track changes in target infrastructure, web applications, and attack surface over time.

## Features

### Core Capabilities
- **Infrastructure Monitoring**: Subdomain discovery, port scanning, DNS records, SSL certificates
- **Web Application Monitoring**: HTTP responses, page content, technology stack, security headers, cookies
- **Content Discovery**: JavaScript files, API endpoints, forms, parameters
- **Attack Surface Tracking**: New endpoints, upload functionality, authentication pages
- **Smart Diff Detection**: Intelligent comparison with noise filtering
- **Automated Notifications**: Slack, Discord, Telegram, Email
- **Visual Reports**: HTML reports, terminal dashboard, daily digests

### Key Benefits
- **Time-Saving**: Automated daily/hourly monitoring instead of manual checks
- **Clear Visibility**: Know exactly what changed and when
- **Prioritization**: Focus on high-value changes (new endpoints, new subdomains)
- **Historical Tracking**: Keep 30-day history of all changes
- **Actionable Output**: Get notified only about important changes

## Architecture

```
┌─────────────────────────────────────────┐
│     BASELINE COLLECTION                 │
│  (Subdomains, Endpoints, JS, Content)   │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│        DIFF DETECTION                   │
│  (Compare current vs baseline)          │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│    NOTIFICATIONS & REPORTS              │
│  (Slack/Discord/Telegram/Email/HTML)    │
└─────────────────────────────────────────┘
```

## Installation

### Quick Install

```bash
cd bb-monitor
chmod +x install.sh
./install.sh
```

### Manual Installation

1. **Install Python dependencies**:
```bash
pip3 install pyyaml requests
```

2. **Install required tools**:
```bash
# Subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# httpx
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Katana
go install github.com/projectdiscovery/katana/cmd/katana@latest

# Nuclei (optional)
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# dnsx
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# Amass (optional)
go install -v github.com/owasp-amass/amass/v4/...@master
```

3. **Make scripts executable**:
```bash
chmod +x monitor.py dashboard.py setup_cron.sh
```

## Configuration

### 1. Edit `config.yaml`

```yaml
targets:
  domains:
    - example.com
    - target.com
  # OR use a file
  domains_file: targets.txt

monitoring:
  schedule: "0 */6 * * *"  # Every 6 hours
  retention_days: 30

checks:
  infrastructure:
    enabled: true
    subdomain_discovery: true
    port_scanning: true

  web_application:
    enabled: true
    http_responses: true
    technology_detection: true

  content_discovery:
    enabled: true
    javascript_files: true
    api_endpoints: true

notifications:
  slack:
    enabled: true
    webhook_url: "YOUR_WEBHOOK_URL"
    notify_on:
      - new_subdomain
      - new_endpoint
      - critical_change
```

### 2. Add Targets

Edit `targets.txt`:
```
example.com
target.com
hackerone-program.com
```

## Usage

### Initial Baseline Collection

First time setup - collect baseline data:

```bash
./monitor.py --init
```

This will:
- Discover all subdomains
- Probe HTTP endpoints
- Crawl websites
- Extract JavaScript endpoints
- Save baseline data

**Time**: 5-15 minutes per domain

### Run Monitoring

Compare current state with baseline:

```bash
./monitor.py --monitor
```

This will:
- Collect current data
- Compare with baseline
- Detect changes
- Send notifications
- Generate reports
- Update baseline

### Automated Monitoring

Setup cron job for automatic monitoring:

```bash
./setup_cron.sh
```

Default: Every 6 hours

### View Dashboard

#### Simple Dashboard
```bash
./dashboard.py
```

#### Interactive Dashboard
```bash
./dashboard.py --interactive
```

Press 'q' to quit.

## Output

### Directory Structure

```
bb-monitor/
├── config.yaml           # Configuration
├── targets.txt           # Target domains
├── monitor.py            # Main monitoring script
├── dashboard.py          # Dashboard viewer
├── notifier.py           # Notification module
├── data/
│   ├── baseline/         # Baseline snapshots
│   │   ├── example.com_baseline.json
│   │   └── target.com_baseline.json
│   └── diffs/            # Change detections
│       ├── example.com_20250121_120000.json
│       └── target.com_20250121_120000.json
├── reports/              # HTML reports
│   └── report_20250121_120000.html
└── logs/                 # Monitoring logs
    └── monitor.log
```

### Example Output

```
============================================================
Changes detected for: example.com
============================================================

[+] New Subdomains (3):
  + api.example.com
  + staging.example.com
  + beta.example.com

[+] New Endpoints (5):
  + https://api.example.com/v2/users
  + https://example.com/admin/login
  + https://staging.example.com/upload

[+] New JS Endpoints (12):
  + /api/internal/admin
  + /api/v2/delete-user
  + /api/upload-file
```

### HTML Report

Beautiful HTML reports with:
- Summary statistics
- New subdomains with timestamps
- New endpoints categorized
- Changed endpoints highlighted
- Technology changes
- Direct links to investigate

## Notifications

### Slack Integration

1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Add to `config.yaml`:
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Discord Integration

1. Create Discord webhook in channel settings
2. Add to `config.yaml`:
```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/YOUR/WEBHOOK"
```

### Telegram Integration

1. Create bot with @BotFather
2. Get chat ID from @userinfobot
3. Add to `config.yaml`:
```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```

## Advanced Features

### Custom Diff Filters

Ignore noise in `config.yaml`:

```yaml
diff_settings:
  ignore_timestamp_changes: true
  min_change_percent: 5
  filter_noise:
    - "Set-Cookie: session"
    - "Date:"
    - "Last-Modified:"
```

### Priority Scoring

Categorize changes by priority:

```yaml
priority:
  high:
    - new_subdomain
    - new_admin_panel
    - new_upload_endpoint
  medium:
    - technology_change
    - new_parameter
  low:
    - content_change
```

### Auto-Scan New Targets

Automatically run Nuclei on new endpoints:

```yaml
advanced:
  auto_scan_new_targets: true

tools:
  nuclei:
    enabled: true
    templates:
      - exposures
      - misconfigurations
      - cves
```

## Tips for Bug Bounty Hunters

### What to Monitor

**High Priority**:
- New subdomains (often less tested)
- New admin panels
- New upload endpoints
- New API endpoints
- Technology version changes (new CVEs)

**Medium Priority**:
- New parameters (IDOR, SQLi tests)
- New forms (XSS, CSRF)
- JavaScript changes (new endpoints)
- Security header changes

**Low Priority**:
- Content updates
- Minor UI changes
- Marketing pages

### Finding Bugs from Changes

1. **New Subdomain**: Test for subdomain takeover, default credentials
2. **New Upload**: File upload vulnerabilities, path traversal
3. **New API**: Broken authentication, IDOR, rate limiting
4. **New JS Endpoints**: Hidden admin functions, debug endpoints
5. **Technology Change**: Search for CVEs in new version
6. **Removed Security Header**: XSS, clickjacking opportunities

### Best Practices

1. **Run baseline during low-traffic hours**: Avoid getting blocked
2. **Monitor multiple times per day**: Catch changes early
3. **Keep historical data**: Track patterns over time
4. **Integrate with your workflow**: Use notifications effectively
5. **Cross-reference with Wayback**: Find removed-then-restored features

## Troubleshooting

### No subdomains found
- Check if tools are installed: `which subfinder httpx`
- Try manual test: `subfinder -d example.com`
- Enable Amass in config for more sources

### Rate limiting
- Reduce `rate_limit` in config
- Add delays between requests
- Use VPN/proxy rotation

### Too many notifications
- Adjust `notify_on` settings
- Increase `min_change_percent`
- Use daily digest instead of instant notifications

### High resource usage
- Reduce `max_workers`
- Disable heavy checks (port scanning, deep crawling)
- Process targets sequentially instead of parallel

## Roadmap

- [ ] Cloud asset monitoring (S3, Azure, GCP)
- [ ] Screenshot comparison (visual diffs)
- [ ] Parameter fuzzing on new endpoints
- [ ] Integration with Burp Suite
- [ ] API for external integrations
- [ ] Machine learning for change prioritization
- [ ] Multi-target correlation
- [ ] Collaborative monitoring (team features)

## Credits

Built with:
- [Subfinder](https://github.com/projectdiscovery/subfinder) - Subdomain discovery
- [httpx](https://github.com/projectdiscovery/httpx) - HTTP probing
- [Katana](https://github.com/projectdiscovery/katana) - Crawling
- [Nuclei](https://github.com/projectdiscovery/nuclei) - Vulnerability scanning

## License

MIT License - Feel free to use for bug bounty hunting!

## Contributing

Pull requests welcome! Areas for improvement:
- Additional notification platforms
- Better diff algorithms
- Performance optimizations
- New monitoring checks

---

**Happy Hunting!** 🎯

For questions/issues: Create an issue on GitHub
