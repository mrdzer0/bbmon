# Quick Start Guide

Get started monitoring your bug bounty targets in 5 minutes!

## Installation (2 minutes)

```bash
cd bb-monitor
chmod +x install.sh
./install.sh
```

## Setup (2 minutes)

### 1. Add Your Targets

Edit `targets.txt`:
```bash
nano targets.txt
```

Add your domains:
```
hackerone.com
bugcrowd.com
intigriti.com
```

### 2. Configure Notifications (Optional)

Edit `config.yaml` to add Slack/Discord webhook:
```bash
nano config.yaml
```

```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "YOUR_DISCORD_WEBHOOK"
```

## First Run (1 minute)

### Collect Baseline

```bash
./monitor.py --init
```

Wait 5-15 minutes for initial scan to complete.

## Daily Usage

### Manual Check

```bash
./monitor.py --monitor
```

### View Dashboard

```bash
./dashboard.py
```

### Automated Monitoring

```bash
./setup_cron.sh
```

That's it! You'll now get notifications whenever something changes.

## Example Workflow

### Day 1: Setup
```bash
# Install
./install.sh

# Add targets
echo "example.com" >> targets.txt

# Initial baseline
./monitor.py --init

# Setup automation
./setup_cron.sh
```

### Day 2+: Monitor
```bash
# Check dashboard
./dashboard.py

# Review reports
firefox reports/latest.html

# Manual check (if needed)
./monitor.py --monitor
```

### When Changes Detected

1. **Get notification** on Slack/Discord
2. **Review the change**:
   - New subdomain? → Check for subdomain takeover
   - New endpoint? → Test for vulnerabilities
   - New upload? → Try file upload bypass
   - Changed tech? → Search for CVEs

3. **Test immediately** before it's patched!

## Real-World Example

### Target: example.com

**Initial Baseline (Day 1)**:
- 45 subdomains found
- 120 endpoints discovered
- 89 JS files analyzed

**Change Detected (Day 5)**:
```
[+] New Subdomain: api-staging.example.com
[+] New Endpoint: https://example.com/admin/backup
[+] New JS Endpoint: /api/internal/users/delete
```

**Your Action**:
1. Test `api-staging.example.com` for default credentials
2. Test `/admin/backup` for path traversal
3. Test `/api/internal/users/delete` for IDOR

**Result**: Found IDOR vulnerability in new endpoint → $500 bounty!

## Tips

### Speed Up Scans
```yaml
# In config.yaml
monitoring:
  schedule: "0 */12 * * *"  # Twice daily instead of every 6h

checks:
  content_discovery:
    enabled: false  # Skip slow crawling initially
```

### Focus on High-Value Changes
```yaml
notifications:
  slack:
    notify_on:
      - new_subdomain
      - new_endpoint
      # Skip minor changes
```

### Test Before Production
```bash
# Test on single domain first
echo "test-target.com" > targets_test.txt
./monitor.py --init --config config.yaml
```

## Common Issues

### "subfinder: command not found"
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
export PATH=$PATH:~/go/bin
```

### Too many notifications
Edit `config.yaml`:
```yaml
diff_settings:
  min_change_percent: 10  # Ignore <10% changes
```

### Want faster scans
```yaml
advanced:
  max_workers: 20  # Increase parallel workers
  rate_limit: 50   # More requests per second
```

## Next Steps

- Read full [README.md](README.md) for advanced features
- Configure custom wordlists
- Set up Nuclei for auto-scanning
- Integrate with your bug bounty workflow

**Happy Hunting!** 🎯
