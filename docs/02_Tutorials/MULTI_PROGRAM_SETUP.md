# Multi-Program Monitoring Setup

Complete guide for monitoring multiple bug bounty programs (A, B, C, etc.) with separate configurations, cron jobs, dashboards, and alerts.

## Table of Contents

- [Quick Start](#quick-start)
- [Directory Structure](#directory-structure)
- [Configuration Setup](#configuration-setup)
- [Target Management](#target-management)
- [Cron Job Setup](#cron-job-setup)
- [Dashboard Monitoring](#dashboard-monitoring)
- [Alert Configuration](#alert-configuration)
- [Advanced Scenarios](#advanced-scenarios)

---

## Quick Start

### Option 1: Shared Workspace (Recommended for Small Scale)

Use the same bb-monitor installation with different config files and target lists:

```bash
cd /path/to/bb-monitor

# Setup for Program A (HackerOne)
cp config.yaml.example config.hackerone.yaml
echo "hackerone.com" > targets.hackerone.txt

# Setup for Program B (Bugcrowd)
cp config.yaml.example config.bugcrowd.yaml
echo "bugcrowd.com" > targets.bugcrowd.txt

# Edit each config with program-specific settings
vim config.hackerone.yaml  # Set Slack channel for HackerOne
vim config.bugcrowd.yaml   # Set Slack channel for Bugcrowd
```

### Option 2: Separate Installations (Recommended for Large Scale)

Each program gets its own complete installation:

```bash
# Program A
git clone https://github.com/yourusername/bb-monitor.git ~/programs/hackerone
cd ~/programs/hackerone
cp config.yaml.example config.yaml
echo "hackerone.com" > targets.txt

# Program B
git clone https://github.com/yourusername/bb-monitor.git ~/programs/bugcrowd
cd ~/programs/bugcrowd
cp config.yaml.example config.yaml
echo "bugcrowd.com" > targets.txt
```

---

## Directory Structure

### Option 1: Shared Workspace

```
bb-monitor/
├── monitor.py
├── config.hackerone.yaml      # Program A config
├── config.bugcrowd.yaml       # Program B config
├── config.intigriti.yaml      # Program C config
├── targets.hackerone.txt      # Program A targets
├── targets.bugcrowd.txt       # Program B targets
├── targets.intigriti.txt      # Program C targets
│
├── data/
│   ├── hackerone/
│   │   ├── baseline/
│   │   ├── diffs/
│   │   ├── subdomain_scans/
│   │   └── shodan_scans/
│   ├── bugcrowd/
│   │   ├── baseline/
│   │   ├── diffs/
│   │   └── subdomain_scans/
│   └── intigriti/
│       ├── baseline/
│       └── diffs/
│
├── reports/
│   ├── hackerone/
│   ├── bugcrowd/
│   └── intigriti/
│
└── logs/
    ├── hackerone_monitor.log
    ├── bugcrowd_monitor.log
    └── intigriti_monitor.log
```

### Option 2: Separate Installations

```
~/programs/
├── hackerone/
│   ├── monitor.py
│   ├── config.yaml
│   ├── targets.txt
│   ├── data/
│   ├── reports/
│   └── logs/
│
├── bugcrowd/
│   ├── monitor.py
│   ├── config.yaml
│   ├── targets.txt
│   ├── data/
│   ├── reports/
│   └── logs/
│
└── intigriti/
    ├── monitor.py
    ├── config.yaml
    ├── targets.txt
    ├── data/
    ├── reports/
    └── logs/
```

---

## Configuration Setup

### Shared Workspace Approach

#### 1. Create Program-Specific Configs

**config.hackerone.yaml**:
```yaml
# HackerOne Program Configuration
targets:
  domains_file: targets.hackerone.txt

monitoring:
  data_dir: ./data/hackerone
  baseline_dir: ./data/hackerone/baseline
  diff_dir: ./data/hackerone/diffs
  reports_dir: ./reports/hackerone

notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/HACKERONE/WEBHOOK"
    notify_on:
      - new_subdomain
      - subdomain_takeover
      - high_value_target

tools:
  shodan:
    enabled: true
    api_key: "${BB_SHODAN_API_KEY}"

# Fast daily scans
advanced:
  max_workers: 20

tools:
  amass:
    enabled: false  # Skip slow tools for daily scans
  katana:
    enabled: false
```

**config.bugcrowd.yaml**:
```yaml
# Bugcrowd Program Configuration
targets:
  domains_file: targets.bugcrowd.txt

monitoring:
  data_dir: ./data/bugcrowd
  baseline_dir: ./data/bugcrowd/baseline
  diff_dir: ./data/bugcrowd/diffs
  reports_dir: ./reports/bugcrowd

notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/BUGCROWD/WEBHOOK"
    notify_on:
      - new_subdomain
      - subdomain_takeover
      - high_value_target

  # Different notification method per program
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/YOUR/BUGCROWD/WEBHOOK"

tools:
  shodan:
    enabled: true
    api_key: "${BB_SHODAN_API_KEY}"

# Comprehensive weekly scans
advanced:
  max_workers: 5

tools:
  amass:
    enabled: true   # Enable for comprehensive scanning
  katana:
    enabled: true
```

#### 2. Create Program-Specific Target Lists

**targets.hackerone.txt**:
```
# HackerOne Program Targets
hackerone.com
hackerone-ctf.com
api.hackerone.com
reports.hackerone.com
```

**targets.bugcrowd.txt**:
```
# Bugcrowd Program Targets
bugcrowd.com
bugcrowdninja.com
api.bugcrowd.com
```

**targets.intigriti.txt**:
```
# Intigriti Program Targets
intigriti.com
app.intigriti.com
api.intigriti.com
```

#### 3. Initialize Baselines

```bash
cd /path/to/bb-monitor

# Initialize HackerOne
./monitor.py -c config.hackerone.yaml --init

# Initialize Bugcrowd
./monitor.py -c config.bugcrowd.yaml --init

# Initialize Intigriti
./monitor.py -c config.intigriti.yaml --init
```

---

## Target Management

### Adding New Targets

```bash
# Add target to specific program
echo "new-target.hackerone.com" >> targets.hackerone.txt

# Re-run baseline for new target
./monitor.py -c config.hackerone.yaml --init
```

### Organizing Targets by Scope

**targets.hackerone.txt** with comments:
```
# Main domains (in scope)
hackerone.com
api.hackerone.com

# Subdomains discovered (auto-added by monitor)
# app.hackerone.com
# reports.hackerone.com

# Out of scope (commented out)
# internal.hackerone.com
# test.hackerone.com
```

### Bulk Import

```bash
# From your recon notes
cat ~/recon/hackerone_scope.txt >> targets.hackerone.txt

# Remove duplicates
sort -u targets.hackerone.txt -o targets.hackerone.txt
```

---

## Cron Job Setup

### Shared Workspace - Multiple Cron Jobs

Create separate cron jobs for each program:

```bash
# Edit crontab
crontab -e
```

Add entries for each program:

```cron
# HackerOne - Every 6 hours
0 */6 * * * cd /path/to/bb-monitor && ./monitor.py -c config.hackerone.yaml --monitor >> logs/hackerone_monitor.log 2>&1

# Bugcrowd - Every 8 hours (offset by 2 hours)
0 2,10,18 * * * cd /path/to/bb-monitor && ./monitor.py -c config.bugcrowd.yaml --monitor >> logs/bugcrowd_monitor.log 2>&1

# Intigriti - Daily at 9 AM
0 9 * * * cd /path/to/bb-monitor && ./monitor.py -c config.intigriti.yaml --monitor >> logs/intigriti_monitor.log 2>&1

# Weekly comprehensive scan for all programs (Sunday 2 AM)
0 2 * * 0 cd /path/to/bb-monitor && ./monitor.py -c config.hackerone.yaml --init >> logs/hackerone_weekly.log 2>&1
0 4 * * 0 cd /path/to/bb-monitor && ./monitor.py -c config.bugcrowd.yaml --init >> logs/bugcrowd_weekly.log 2>&1
0 6 * * 0 cd /path/to/bb-monitor && ./monitor.py -c config.intigriti.yaml --init >> logs/intigriti_weekly.log 2>&1
```

### Separate Installations - Independent Cron Jobs

```cron
# HackerOne
0 */6 * * * cd ~/programs/hackerone && ./monitor.py --monitor >> logs/monitor.log 2>&1

# Bugcrowd
0 */8 * * * cd ~/programs/bugcrowd && ./monitor.py --monitor >> logs/monitor.log 2>&1

# Intigriti
0 9 * * * cd ~/programs/intigriti && ./monitor.py --monitor >> logs/monitor.log 2>&1
```

### Automated Setup Script

Create `setup_multi_program_cron.sh`:

```bash
#!/bin/bash
# Setup cron jobs for multiple programs

BBMON_ROOT="/path/to/bb-monitor"

# Remove old cron jobs
crontab -l | grep -v "bb-monitor" | crontab -

# Add new cron jobs
(crontab -l 2>/dev/null; cat << EOF
# Bug Bounty Monitoring - Multiple Programs
# HackerOne - Every 6 hours
0 */6 * * * cd $BBMON_ROOT && ./monitor.py -c config.hackerone.yaml --monitor >> logs/hackerone_monitor.log 2>&1

# Bugcrowd - Every 8 hours
0 2,10,18 * * * cd $BBMON_ROOT && ./monitor.py -c config.bugcrowd.yaml --monitor >> logs/bugcrowd_monitor.log 2>&1

# Intigriti - Daily at 9 AM
0 9 * * * cd $BBMON_ROOT && ./monitor.py -c config.intigriti.yaml --monitor >> logs/intigriti_monitor.log 2>&1
EOF
) | crontab -

echo "[+] Cron jobs installed successfully"
crontab -l | grep "bb-monitor"
```

Make executable and run:
```bash
chmod +x setup_multi_program_cron.sh
./setup_multi_program_cron.sh
```

---

## Dashboard Monitoring

### View Specific Program Dashboard

#### Shared Workspace

```bash
cd /path/to/bb-monitor

# View HackerOne dashboard
python3 modules/dashboard.py --data-dir ./data/hackerone

# View Bugcrowd dashboard
python3 modules/dashboard.py --data-dir ./data/bugcrowd

# Interactive mode
python3 modules/dashboard.py --data-dir ./data/hackerone --interactive
```

#### Separate Installations

```bash
# HackerOne
cd ~/programs/hackerone
./modules/dashboard.py

# Bugcrowd
cd ~/programs/bugcrowd
./modules/dashboard.py --interactive
```

### Create Program-Specific Dashboard Scripts

**view_hackerone.sh**:
```bash
#!/bin/bash
cd /path/to/bb-monitor
python3 modules/dashboard.py --data-dir ./data/hackerone "$@"
```

**view_bugcrowd.sh**:
```bash
#!/bin/bash
cd /path/to/bb-monitor
python3 modules/dashboard.py --data-dir ./data/bugcrowd "$@"
```

Make executable:
```bash
chmod +x view_*.sh

# Usage
./view_hackerone.sh
./view_bugcrowd.sh --interactive
```

### Unified Dashboard Script

**view_all_programs.sh**:
```bash
#!/bin/bash
# View all program dashboards

PROGRAMS=("hackerone" "bugcrowd" "intigriti")
BBMON_ROOT="/path/to/bb-monitor"

for program in "${PROGRAMS[@]}"; do
    echo "=========================================="
    echo "Program: $program"
    echo "=========================================="
    python3 $BBMON_ROOT/modules/dashboard.py --data-dir $BBMON_ROOT/data/$program
    echo ""
done
```

### Dashboard Comparison

Create a script to compare statistics across programs:

**compare_programs.py**:
```python
#!/usr/bin/env python3
import json
from pathlib import Path

programs = {
    'HackerOne': './data/hackerone/baseline',
    'Bugcrowd': './data/bugcrowd/baseline',
    'Intigriti': './data/intigriti/baseline'
}

print(f"{'Program':<20} {'Domains':<10} {'Subdomains':<15} {'Endpoints':<15}")
print("="*65)

for name, path in programs.items():
    baseline_dir = Path(path)
    total_subdomains = 0
    total_endpoints = 0
    domain_count = 0

    for baseline_file in baseline_dir.glob("*_baseline.json"):
        domain_count += 1
        with open(baseline_file) as f:
            data = json.load(f)
            total_subdomains += len(data.get('subdomains', {}))
            total_endpoints += len(data.get('endpoints', {}))

    print(f"{name:<20} {domain_count:<10} {total_subdomains:<15} {total_endpoints:<15}")
```

Usage:
```bash
python3 compare_programs.py
```

---

## Alert Configuration

### Program-Specific Alerts

#### Different Slack Channels per Program

**config.hackerone.yaml**:
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/T00/B00/HACKERONE_WEBHOOK"
    notify_on:
      - new_subdomain
      - subdomain_takeover
      - high_value_target
      - shodan_vulnerabilities
```

**config.bugcrowd.yaml**:
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/T00/B00/BUGCROWD_WEBHOOK"
    notify_on:
      - new_subdomain
      - subdomain_takeover
```

#### Multiple Notification Channels per Program

**config.hackerone.yaml** (High-value program - all alerts):
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${BB_HACKERONE_SLACK_WEBHOOK}"
    notify_on:
      - new_subdomain
      - subdomain_takeover
      - high_value_target
      - new_endpoint
      - shodan_vulnerabilities

  telegram:
    enabled: true
    bot_token: "${BB_TELEGRAM_TOKEN}"
    chat_id: "${BB_HACKERONE_CHAT_ID}"
    notify_on:
      - subdomain_takeover
      - shodan_vulnerabilities

  email:
    enabled: true
    to_email: "hackerone-alerts@yourdomain.com"
```

**config.bugcrowd.yaml** (Medium priority - critical only):
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${BB_BUGCROWD_SLACK_WEBHOOK}"
    notify_on:
      - subdomain_takeover
      - shodan_vulnerabilities

  daily_digest:
    enabled: true
    time: "09:00"
```

### Environment Variables for Secrets

Create `.env.programs`:
```bash
# HackerOne
export BB_HACKERONE_SLACK_WEBHOOK="https://hooks.slack.com/services/XXX/YYY/ZZZ"
export BB_HACKERONE_CHAT_ID="123456789"

# Bugcrowd
export BB_BUGCROWD_SLACK_WEBHOOK="https://hooks.slack.com/services/AAA/BBB/CCC"
export BB_BUGCROWD_CHAT_ID="987654321"

# Shared credentials
export BB_TELEGRAM_TOKEN="bot_token_here"
export BB_SHODAN_API_KEY="shodan_api_key_here"
export BB_EMAIL_PASSWORD="email_app_password"
```

Load before running:
```bash
source .env.programs
./monitor.py -c config.hackerone.yaml --monitor
```

Add to cron:
```cron
# Source env before each run
0 */6 * * * source /path/to/.env.programs && cd /path/to/bb-monitor && ./monitor.py -c config.hackerone.yaml --monitor >> logs/hackerone_monitor.log 2>&1
```

### Alert Priority Matrix

Configure different alert levels per program:

| Finding Type | HackerOne | Bugcrowd | Intigriti |
|-------------|-----------|----------|-----------|
| New Subdomain | Slack + Telegram | Slack | Digest Only |
| Subdomain Takeover | Slack + Telegram + Email | Slack + Email | Slack |
| High-Value Target | Slack + Telegram | Slack | Slack |
| Shodan Vulns | Slack + Telegram | Slack | Digest Only |
| New Endpoint | Slack | Digest Only | Digest Only |
| Content Change | Digest Only | Digest Only | Digest Only |

### Custom Alert Webhook

Create program-specific webhook handler:

**webhook_handler.py**:
```python
#!/usr/bin/env python3
import sys
import json
import requests

def send_alert(program, alert_type, data):
    # Route to different endpoints based on program
    webhooks = {
        'hackerone': 'https://your-api.com/alerts/hackerone',
        'bugcrowd': 'https://your-api.com/alerts/bugcrowd',
        'intigriti': 'https://your-api.com/alerts/intigriti'
    }

    payload = {
        'program': program,
        'type': alert_type,
        'data': data,
        'timestamp': str(datetime.now())
    }

    webhook_url = webhooks.get(program)
    if webhook_url:
        requests.post(webhook_url, json=payload)

if __name__ == '__main__':
    program = sys.argv[1]
    alert_type = sys.argv[2]
    data = json.loads(sys.argv[3])
    send_alert(program, alert_type, data)
```

---

## Advanced Scenarios

### Scenario 1: Different Scan Schedules

```yaml
# High-value program (config.hackerone.yaml)
# - Fast scans every 4 hours
# - Comprehensive weekly scan

# Medium-value program (config.bugcrowd.yaml)
# - Normal scans every 8 hours
# - Comprehensive bi-weekly scan

# Low-priority program (config.intigriti.yaml)
# - Scans once daily
# - Comprehensive monthly scan
```

**Cron setup**:
```cron
# HackerOne - Every 4 hours (fast)
0 */4 * * * cd /path/to/bb-monitor && ./monitor.py -c config.hackerone.yaml --monitor >> logs/hackerone_monitor.log 2>&1

# HackerOne - Weekly comprehensive (Sunday 2 AM)
0 2 * * 0 cd /path/to/bb-monitor && ./monitor.py -c config.hackerone.yaml --init >> logs/hackerone_weekly.log 2>&1

# Bugcrowd - Every 8 hours
0 */8 * * * cd /path/to/bb-monitor && ./monitor.py -c config.bugcrowd.yaml --monitor >> logs/bugcrowd_monitor.log 2>&1

# Bugcrowd - Bi-weekly comprehensive (1st and 15th at 3 AM)
0 3 1,15 * * cd /path/to/bb-monitor && ./monitor.py -c config.bugcrowd.yaml --init >> logs/bugcrowd_biweekly.log 2>&1

# Intigriti - Daily at 9 AM
0 9 * * * cd /path/to/bb-monitor && ./monitor.py -c config.intigriti.yaml --monitor >> logs/intigriti_monitor.log 2>&1

# Intigriti - Monthly comprehensive (1st of month at 4 AM)
0 4 1 * * cd /path/to/bb-monitor && ./monitor.py -c config.intigriti.yaml --init >> logs/intigriti_monthly.log 2>&1
```

### Scenario 2: Program-Specific Tool Configurations

**HackerOne** (Fast, broad coverage):
```yaml
tools:
  subfinder:
    enabled: true
  assetfinder:
    enabled: true
  amass:
    enabled: false  # Too slow for frequent scans
  katana:
    enabled: false
  shodan:
    enabled: true
    scan_on:
      - baseline_init  # Only during weekly comprehensive scan

advanced:
  max_workers: 30   # Fast parallel processing
```

**Bugcrowd** (Balanced):
```yaml
tools:
  subfinder:
    enabled: true
  assetfinder:
    enabled: true
  amass:
    enabled: true
    passive: true
  katana:
    enabled: true
    depth: 2
  shodan:
    enabled: true

advanced:
  max_workers: 15
```

**Intigriti** (Deep, thorough):
```yaml
tools:
  subfinder:
    enabled: true
  assetfinder:
    enabled: true
  amass:
    enabled: true
    passive: false  # Active enumeration
  katana:
    enabled: true
    depth: 4        # Deep crawling
  nuclei:
    enabled: true   # Vulnerability scanning
  shodan:
    enabled: true
    scan_on:
      - baseline_init
      - new_subdomain

advanced:
  max_workers: 5  # Slower but thorough
```

### Scenario 3: Shared Database / Centralized Logging

Use a central database to store results from all programs:

**config.hackerone.yaml**:
```yaml
monitoring:
  data_dir: /mnt/central_storage/bb-monitor/hackerone/data
  baseline_dir: /mnt/central_storage/bb-monitor/hackerone/baseline
  reports_dir: /mnt/central_storage/bb-monitor/hackerone/reports
```

**config.bugcrowd.yaml**:
```yaml
monitoring:
  data_dir: /mnt/central_storage/bb-monitor/bugcrowd/data
  baseline_dir: /mnt/central_storage/bb-monitor/bugcrowd/baseline
  reports_dir: /mnt/central_storage/bb-monitor/bugcrowd/reports
```

Benefits:
- Centralized backup
- Easier to analyze across programs
- Can use NFS/CIFS for multiple machines

### Scenario 4: Team Collaboration

Multiple team members monitoring different programs:

```bash
# Team structure
team@server:~$ tree /opt/bb-monitor
/opt/bb-monitor/
├── config.hackerone.yaml    # Alice's responsibility
├── config.bugcrowd.yaml     # Bob's responsibility
├── config.intigriti.yaml    # Charlie's responsibility
└── ...

# Separate logs per person/program
logs/
├── alice_hackerone.log
├── bob_bugcrowd.log
└── charlie_intigriti.log
```

**Cron jobs with owner tags**:
```cron
# Alice - HackerOne
0 */6 * * * cd /opt/bb-monitor && ./monitor.py -c config.hackerone.yaml --monitor >> logs/alice_hackerone.log 2>&1

# Bob - Bugcrowd
0 */8 * * * cd /opt/bb-monitor && ./monitor.py -c config.bugcrowd.yaml --monitor >> logs/bob_bugcrowd.log 2>&1

# Charlie - Intigriti
0 9 * * * cd /opt/bb-monitor && ./monitor.py -c config.intigriti.yaml --monitor >> logs/charlie_intigriti.log 2>&1
```

---

## Monitoring Status

### Check Which Programs Are Running

```bash
# Check active cron jobs
crontab -l | grep bb-monitor

# Check recent log activity
ls -lht logs/*.log | head -10

# Check last run time per program
tail -1 logs/hackerone_monitor.log
tail -1 logs/bugcrowd_monitor.log
tail -1 logs/intigriti_monitor.log
```

### Status Dashboard Script

**check_status.sh**:
```bash
#!/bin/bash
# Check status of all monitored programs

PROGRAMS=("hackerone" "bugcrowd" "intigriti")
BBMON_ROOT="/path/to/bb-monitor"

echo "Bug Bounty Monitoring Status"
echo "=============================="
echo ""

for program in "${PROGRAMS[@]}"; do
    log_file="$BBMON_ROOT/logs/${program}_monitor.log"

    if [ -f "$log_file" ]; then
        last_run=$(tail -1 "$log_file" | grep -oP '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' || echo "Unknown")
        lines=$(wc -l < "$log_file")
        size=$(du -h "$log_file" | cut -f1)

        echo "[$program]"
        echo "  Last run: $last_run"
        echo "  Log size: $size ($lines lines)"

        # Check for errors
        errors=$(grep -i "error\|fail" "$log_file" | wc -l)
        if [ $errors -gt 0 ]; then
            echo "  ⚠️  Errors: $errors"
        else
            echo "  ✓ No errors"
        fi

        echo ""
    else
        echo "[$program]"
        echo "  ❌ No log file found"
        echo ""
    fi
done

echo "Cron Jobs:"
crontab -l | grep bb-monitor | wc -l
echo " active jobs"
```

---

## Quick Reference

### Commands Cheat Sheet

```bash
# Initialize program
./monitor.py -c config.PROGRAM.yaml --init

# Run monitoring
./monitor.py -c config.PROGRAM.yaml --monitor

# View dashboard
python3 modules/dashboard.py --data-dir ./data/PROGRAM

# Check logs
tail -f logs/PROGRAM_monitor.log

# View latest changes
cat data/PROGRAM/diffs/latest.json | jq

# List all baselines
ls -lh data/PROGRAM/baseline/
```

### File Naming Convention

```
config.{program}.yaml
targets.{program}.txt
logs/{program}_monitor.log
logs/{program}_weekly.log
data/{program}/
reports/{program}/
```

### Environment Variables

```bash
# Per-program webhooks
BB_{PROGRAM}_SLACK_WEBHOOK
BB_{PROGRAM}_DISCORD_WEBHOOK
BB_{PROGRAM}_CHAT_ID

# Shared credentials
BB_SHODAN_API_KEY
BB_TELEGRAM_TOKEN
BB_EMAIL_PASSWORD
```

---

## Troubleshooting

### Program A works but Program B doesn't

**Check**:
1. Config file exists and is valid YAML
2. Target file exists and has domains
3. Data directories are writable
4. Cron job is properly configured
5. No conflicting cron schedules

```bash
# Validate config
python3 -c "import yaml; yaml.safe_load(open('config.programB.yaml'))"

# Test run manually
./monitor.py -c config.programB.yaml --monitor

# Check cron
crontab -l | grep programB
```

### Alerts not working for specific program

**Check**:
1. Webhook URL is correct in config
2. Environment variables are loaded in cron
3. Notification triggers match findings

```bash
# Test notification
python3 -c "
from modules.notifier import Notifier
import yaml

with open('config.programB.yaml') as f:
    config = yaml.safe_load(f)

notifier = Notifier(config['notifications'])
notifier.send_slack('Test from Program B', {})
"
```

### Dashboard shows no data

**Check**:
1. Correct data directory path
2. Baseline files exist
3. File permissions

```bash
# Check baseline
ls -lh data/PROGRAM/baseline/
python3 modules/dashboard.py --data-dir ./data/PROGRAM
```

---

## See Also

- [USAGE.md](USAGE.md) - General usage guide
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
- [PATH_TROUBLESHOOTING.md](PATH_TROUBLESHOOTING.md) - Path issues
- [SHODAN_INTEGRATION.md](SHODAN_INTEGRATION.md) - Shodan setup
