# Usage Guide

## Table of Contents

- [Installation](#installation)
- [Initial Setup](#initial-setup)
- [Basic Operations](#basic-operations)
- [Advanced Usage](#advanced-usage)
- [Automation](#automation)
- [Best Practices](#best-practices)

## Installation

### Prerequisites

- Python 3.8 or higher
- Go 1.19 or higher
- Linux/macOS (Windows via WSL)

### Quick Install

```bash
cd bb-monitor
chmod +x utils/install.sh
./utils/install.sh
```

### Manual Installation

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Go tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/tomnomnom/assetfinder@latest

# Optional tools
go install -v github.com/owasp-amass/amass/v4/...@master
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
```

## Initial Setup

### 1. Configure Targets

```bash
# Add domains to monitor
echo "hackerone.com" >> targets.txt
echo "bugcrowd.com" >> targets.txt

# Or edit directly
nano targets.txt
```

### 2. Configure Settings

Edit `config.yaml`:

```yaml
targets:
  domains_file: targets.txt

monitoring:
  retention_days: 30

notifications:
  slack:
    enabled: true
    webhook_url: "YOUR_WEBHOOK"
```

### 3. Collect Baseline

```bash
./monitor.py --init
```

This will:
- Discover all subdomains
- Check for takeover vulnerabilities
- Probe HTTP endpoints
- Detect technologies
- Save baseline for future comparison

## Basic Operations

### Monitor Changes

```bash
./monitor.py --monitor
```

Output shows:
- New/removed subdomains
- New/changed endpoints
- Status code changes
- Technology updates
- High-value targets

### View Dashboard

```bash
# Simple dashboard
./modules/dashboard.py

# Interactive mode
./modules/dashboard.py --interactive
```

### Standalone Subdomain Scan

```bash
# Basic scan
./utils/subdomain_scan.sh -d example.com

# Quick scan (faster)
./utils/subdomain_scan.sh -d example.com -q

# Full scan (comprehensive)
./utils/subdomain_scan.sh -d example.com -f
```

### HTTP Monitoring

```bash
# Create URL list
cat data/baseline/*_baseline.json | jq -r '.endpoints | keys[]' > urls.txt

# Probe URLs
./modules/http_monitor.py -l urls.txt -s current.json

# Compare with baseline
./modules/http_monitor.py -l urls.txt -s new.json -c current.json
```

## Advanced Usage

### Custom Wordlists

```bash
# Use custom subdomain wordlist with subfinder
subfinder -d example.com -w /path/to/wordlist.txt
```

### Filtering Results

```bash
# Filter for specific status codes
./monitor.py --monitor | grep "\[200\]"

# Filter high-value targets
cat data/diffs/*.json | jq '.changed_endpoints[] | select(.changes.new_flags)'
```

### Export Data

```bash
# Export subdomains
cat data/baseline/*_baseline.json | jq -r '.subdomains | keys[]' > all_subdomains.txt

# Export endpoints with flags
cat data/baseline/*.json | jq -r '.endpoints[] | select(.flags) | .url'
```

### Integration with Other Tools

```bash
# Use with httpx
cat all_subdomains.txt | httpx -silent -o live.txt

# Use with nuclei
httpx -l all_subdomains.txt | nuclei -t exposures/

# Use with ffuf
ffuf -u "https://FUZZ.example.com" -w all_subdomains.txt
```

## Automation

### Setup Cron Job

```bash
./utils/setup_cron.sh
```

Default schedule: Every 6 hours

### Custom Schedule

Edit crontab:
```bash
crontab -e

# Every 4 hours
0 */4 * * * cd /path/to/bb-monitor && ./monitor.py --monitor

# Daily at 9 AM
0 9 * * * cd /path/to/bb-monitor && ./monitor.py --monitor

# Twice daily
0 9,21 * * * cd /path/to/bb-monitor && ./monitor.py --monitor
```

### Logging

```bash
# View live logs
tail -f logs/monitor.log

# Search logs
grep "high_value" logs/monitor.log

# View specific date
grep "2025-01-21" logs/monitor.log
```

## Best Practices

### 1. Initial Baseline

Always collect a comprehensive baseline first:

```bash
# Use full scan for initial baseline
./monitor.py --init

# Or use standalone scanner with full mode
./utils/subdomain_scan.sh -d example.com -f
```

### 2. Regular Monitoring

- **Active programs**: Monitor every 6-12 hours
- **Passive monitoring**: Once daily
- **Low-priority targets**: Weekly

### 3. Prioritize Findings

Focus on:
1. 🔴 High-severity flags (admin, upload, takeovers)
2. 🟡 Status changes (404→200, 403→200)
3. 🟡 New endpoints
4. 🔵 Technology changes

### 4. Verify Before Reporting

Always manually verify automated findings:
- Test subdomain takeovers yourself
- Confirm outdated technologies
- Verify high-value targets are exploitable

### 5. Organize Data

```bash
# Create project-specific directories
mkdir -p projects/hackerone
cd projects/hackerone

# Link to main config
ln -s ../../config.yaml .
ln -s ../../monitor.py .

# Use project-specific targets
echo "hackerone.com" > targets.txt
```

### 6. Backup Data

```bash
# Backup baselines
tar -czf backup_$(date +%Y%m%d).tar.gz data/baseline/

# Sync to cloud
rclone sync data/ remote:bb-monitor-backup/
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Examples

### Example 1: New Bug Bounty Program

```bash
# Add target
echo "new-program.com" >> targets.txt

# Collect baseline
./monitor.py --init

# Review findings
cat data/baseline/new-program.com_baseline.json | jq '.subdomain_takeovers'

# Setup monitoring
./utils/setup_cron.sh
```

### Example 2: Check for Changes

```bash
# Run monitor
./monitor.py --monitor

# If changes detected, review
cat data/diffs/target_*.json | jq .

# Test new findings manually
```

### Example 3: Focus on High-Value Targets

```bash
# Extract high-value endpoints
cat data/baseline/*.json | jq -r '.endpoints | to_entries[] | select(.value.flags[] | .severity == "high") | .key'

# Test each one
```

---

For more information, see:
- [Configuration Guide](CONFIGURATION.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Main README](../README.md)
