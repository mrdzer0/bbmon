# Multi-Program Setup - Complete Example

This is a complete walkthrough showing how to set up monitoring for multiple bug bounty programs: HackerOne, Bugcrowd, and Intigriti.

## Scenario

You're monitoring 3 bug bounty programs:
- **HackerOne**: High-value program, scan every 4 hours, all alerts
- **Bugcrowd**: Medium-value program, scan every 8 hours, critical alerts only
- **Intigriti**: Low-priority program, scan daily, digest only

## Step-by-Step Setup

### Step 1: Prepare Your Workspace

```bash
cd ~/tools
git clone https://github.com/yourusername/bb-monitor.git
cd bb-monitor

# Install dependencies
./utils/install.sh

# Verify installation
./utils/test_paths.sh
```

### Step 2: Setup HackerOne Program

```bash
# Use the automated setup script
./utils/setup_program.sh -n hackerone

# Or manual setup:
# Create config
cp config.yaml.example config.hackerone.yaml

# Create target list
cat > targets.hackerone.txt << EOF
# HackerOne Bug Bounty Program
hackerone.com
hackerone-ctf.com
api.hackerone.com
resources.hackerone.com
EOF
```

Edit `config.hackerone.yaml`:

```yaml
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

tools:
  subfinder:
    enabled: true
  assetfinder:
    enabled: true
  amass:
    enabled: false  # Fast scans
  katana:
    enabled: false
  shodan:
    enabled: true
    api_key: "${BB_SHODAN_API_KEY}"
    scan_on:
      - baseline_init

advanced:
  max_workers: 20  # Fast parallel processing
```

Run initial baseline:
```bash
./monitor.py -c config.hackerone.yaml --init
```

### Step 3: Setup Bugcrowd Program

```bash
./utils/setup_program.sh -n bugcrowd

# Add targets
cat > targets.bugcrowd.txt << EOF
# Bugcrowd Bug Bounty Program
bugcrowd.com
bugcrowdninja.com
api.bugcrowd.com
EOF
```

Edit `config.bugcrowd.yaml`:

```yaml
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
    webhook_url: "${BB_BUGCROWD_SLACK_WEBHOOK}"
    notify_on:
      - subdomain_takeover
      - high_value_target
      - shodan_vulnerabilities

  daily_digest:
    enabled: true
    time: "09:00"

tools:
  subfinder:
    enabled: true
  assetfinder:
    enabled: true
  amass:
    enabled: true   # More thorough
    passive: true
  katana:
    enabled: true
    depth: 2
  shodan:
    enabled: true
    api_key: "${BB_SHODAN_API_KEY}"

advanced:
  max_workers: 15  # Balanced
```

Run baseline:
```bash
./monitor.py -c config.bugcrowd.yaml --init
```

### Step 4: Setup Intigriti Program

```bash
./utils/setup_program.sh -n intigriti

cat > targets.intigriti.txt << EOF
# Intigriti Bug Bounty Program
intigriti.com
app.intigriti.com
api.intigriti.com
EOF
```

Edit `config.intigriti.yaml`:

```yaml
targets:
  domains_file: targets.intigriti.txt

monitoring:
  data_dir: ./data/intigriti
  baseline_dir: ./data/intigriti/baseline
  diff_dir: ./data/intigriti/diffs
  reports_dir: ./reports/intigriti

notifications:
  slack:
    enabled: true
    webhook_url: "${BB_INTIGRITI_SLACK_WEBHOOK}"
    notify_on:
      - subdomain_takeover

  daily_digest:
    enabled: true
    time: "10:00"

tools:
  subfinder:
    enabled: true
  assetfinder:
    enabled: true
  amass:
    enabled: false  # Daily scans, keep it simple
  shodan:
    enabled: false  # Optional

advanced:
  max_workers: 10
```

Run baseline:
```bash
./monitor.py -c config.intigriti.yaml --init
```

### Step 5: Configure Environment Variables

Create `.env.programs`:

```bash
cat > ~/.bbmon_env << 'EOF'
# Bug Bounty Monitoring - Environment Variables

# HackerOne
export BB_HACKERONE_SLACK_WEBHOOK="https://hooks.slack.com/services/T00/B00/HACKER_ONE"
export BB_HACKERONE_CHAT_ID="123456789"

# Bugcrowd
export BB_BUGCROWD_SLACK_WEBHOOK="https://hooks.slack.com/services/T00/B00/BUG_CROWD"

# Intigriti
export BB_INTIGRITI_SLACK_WEBHOOK="https://hooks.slack.com/services/T00/B00/INTIGRITI"

# Shared credentials
export BB_TELEGRAM_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export BB_SHODAN_API_KEY="your_shodan_api_key_here"
export BB_EMAIL_PASSWORD="your_email_app_password"
EOF

# Load variables
source ~/.bbmon_env

# Make it persistent
echo "source ~/.bbmon_env" >> ~/.bashrc
```

### Step 6: Setup Cron Jobs

Create `setup_all_crons.sh`:

```bash
cat > setup_all_crons.sh << 'EOF'
#!/bin/bash
# Setup cron jobs for all programs

BBMON_ROOT="/home/$(whoami)/tools/bb-monitor"

# Remove old cron jobs
crontab -l 2>/dev/null | grep -v "bb-monitor" | crontab -

# Add new cron jobs
(crontab -l 2>/dev/null; cat << CRON
# Bug Bounty Monitoring - Multi-Program Setup
# Load environment variables
SHELL=/bin/bash

# HackerOne - Every 4 hours (high-value)
0 */4 * * * source ~/.bbmon_env && cd $BBMON_ROOT && ./monitor.py -c config.hackerone.yaml --monitor >> logs/hackerone_monitor.log 2>&1

# HackerOne - Weekly comprehensive (Sunday 2 AM)
0 2 * * 0 source ~/.bbmon_env && cd $BBMON_ROOT && ./monitor.py -c config.hackerone.yaml --init >> logs/hackerone_weekly.log 2>&1

# Bugcrowd - Every 8 hours (medium-value)
0 2,10,18 * * * source ~/.bbmon_env && cd $BBMON_ROOT && ./monitor.py -c config.bugcrowd.yaml --monitor >> logs/bugcrowd_monitor.log 2>&1

# Bugcrowd - Bi-weekly comprehensive (1st and 15th at 3 AM)
0 3 1,15 * * source ~/.bbmon_env && cd $BBMON_ROOT && ./monitor.py -c config.bugcrowd.yaml --init >> logs/bugcrowd_biweekly.log 2>&1

# Intigriti - Daily at 9 AM (low-priority)
0 9 * * * source ~/.bbmon_env && cd $BBMON_ROOT && ./monitor.py -c config.intigriti.yaml --monitor >> logs/intigriti_monitor.log 2>&1

# Intigriti - Monthly comprehensive (1st of month at 4 AM)
0 4 1 * * source ~/.bbmon_env && cd $BBMON_ROOT && ./monitor.py -c config.intigriti.yaml --init >> logs/intigriti_monthly.log 2>&1
CRON
) | crontab -

echo "[+] Cron jobs installed successfully!"
echo ""
echo "Scheduled jobs:"
crontab -l | grep bb-monitor
EOF

chmod +x setup_all_crons.sh
./setup_all_crons.sh
```

### Step 7: Create Dashboard Scripts

**View specific program**:

```bash
# HackerOne dashboard
cat > view_hackerone.sh << 'EOF'
#!/bin/bash
cd ~/tools/bb-monitor
python3 modules/dashboard.py --data-dir ./data/hackerone "$@"
EOF
chmod +x view_hackerone.sh

# Bugcrowd dashboard
cat > view_bugcrowd.sh << 'EOF'
#!/bin/bash
cd ~/tools/bb-monitor
python3 modules/dashboard.py --data-dir ./data/bugcrowd "$@"
EOF
chmod +x view_bugcrowd.sh

# Intigriti dashboard
cat > view_intigriti.sh << 'EOF'
#!/bin/bash
cd ~/tools/bb-monitor
python3 modules/dashboard.py --data-dir ./data/intigriti "$@"
EOF
chmod +x view_intigriti.sh
```

**View all programs**:

```bash
cat > view_all.sh << 'EOF'
#!/bin/bash
# View all program dashboards

PROGRAMS=("hackerone" "bugcrowd" "intigriti")
BBMON_ROOT="$HOME/tools/bb-monitor"

for program in "${PROGRAMS[@]}"; do
    echo "=========================================="
    echo "Program: $program"
    echo "=========================================="
    python3 $BBMON_ROOT/modules/dashboard.py --data-dir $BBMON_ROOT/data/$program
    echo ""
done
EOF
chmod +x view_all.sh
```

**Compare programs**:

```bash
cat > compare_programs.sh << 'EOF'
#!/bin/bash
# Compare statistics across programs

BBMON_ROOT="$HOME/tools/bb-monitor"

echo "Bug Bounty Monitoring - Program Comparison"
echo "=========================================="
printf "%-20s %-10s %-15s %-15s\n" "Program" "Domains" "Subdomains" "Endpoints"
echo "=========================================="

for program in hackerone bugcrowd intigriti; do
    baseline_dir="$BBMON_ROOT/data/$program/baseline"

    if [ -d "$baseline_dir" ]; then
        domain_count=$(ls -1 $baseline_dir/*_baseline.json 2>/dev/null | wc -l)

        # Count total subdomains and endpoints
        total_subs=0
        total_endpoints=0

        for file in $baseline_dir/*_baseline.json; do
            if [ -f "$file" ]; then
                subs=$(jq '.subdomains | length' "$file" 2>/dev/null || echo 0)
                endpoints=$(jq '.endpoints | length' "$file" 2>/dev/null || echo 0)
                total_subs=$((total_subs + subs))
                total_endpoints=$((total_endpoints + endpoints))
            fi
        done

        printf "%-20s %-10s %-15s %-15s\n" "$program" "$domain_count" "$total_subs" "$total_endpoints"
    else
        printf "%-20s %-10s %-15s %-15s\n" "$program" "N/A" "N/A" "N/A"
    fi
done
EOF
chmod +x compare_programs.sh
```

### Step 8: Create Status Monitoring Script

```bash
cat > check_status.sh << 'EOF'
#!/bin/bash
# Check status of all monitored programs

PROGRAMS=("hackerone" "bugcrowd" "intigriti")
BBMON_ROOT="$HOME/tools/bb-monitor"

echo "Bug Bounty Monitoring - System Status"
echo "======================================"
echo ""

for program in "${PROGRAMS[@]}"; do
    log_file="$BBMON_ROOT/logs/${program}_monitor.log"

    echo "[$program]"

    if [ -f "$log_file" ]; then
        # Last run time
        last_run=$(stat -c %y "$log_file" 2>/dev/null | cut -d. -f1)
        echo "  Last run: $last_run"

        # Log size
        size=$(du -h "$log_file" | cut -f1)
        lines=$(wc -l < "$log_file")
        echo "  Log: $size ($lines lines)"

        # Check for errors
        errors=$(grep -i "error\|fail" "$log_file" 2>/dev/null | wc -l)
        if [ $errors -gt 0 ]; then
            echo "  ⚠️  Errors: $errors"
        else
            echo "  ✓ No errors"
        fi

        # Check baseline exists
        baseline_dir="$BBMON_ROOT/data/$program/baseline"
        if [ -d "$baseline_dir" ]; then
            baseline_count=$(ls -1 $baseline_dir/*_baseline.json 2>/dev/null | wc -l)
            echo "  Baselines: $baseline_count domains"
        else
            echo "  ❌ No baseline directory"
        fi
    else
        echo "  ❌ No log file found"
    fi

    echo ""
done

echo "Cron Jobs:"
cron_count=$(crontab -l 2>/dev/null | grep bb-monitor | wc -l)
echo "  Active: $cron_count jobs"

echo ""
echo "Next scheduled runs:"
crontab -l 2>/dev/null | grep bb-monitor | head -3
EOF
chmod +x check_status.sh
```

## Daily Workflow

### Morning Routine

```bash
# 1. Check overnight activity
./check_status.sh

# 2. View all program dashboards
./view_all.sh

# 3. Compare program statistics
./compare_programs.sh

# 4. Check for critical alerts in Slack/Telegram
# (Handled automatically by notifications)
```

### Investigate Findings

```bash
# HackerOne - Interactive dashboard
./view_hackerone.sh --interactive

# View specific domain
cat data/hackerone/baseline/hackerone.com_baseline.json | jq

# Check recent changes
cat data/hackerone/diffs/hackerone.com_*.json | jq '.new_subdomains'

# View Shodan results
cat data/hackerone/shodan_scans/hackerone.com_*.json | jq '.summary'
```

### Manual Scans

```bash
# On-demand scan for specific program
./monitor.py -c config.hackerone.yaml --monitor

# Force full rescan
./monitor.py -c config.hackerone.yaml --init

# Scan all programs
for program in hackerone bugcrowd intigriti; do
    echo "Scanning $program..."
    ./monitor.py -c config.$program.yaml --monitor
done
```

## Directory Structure After Setup

```
bb-monitor/
├── config.hackerone.yaml
├── config.bugcrowd.yaml
├── config.intigriti.yaml
├── targets.hackerone.txt
├── targets.bugcrowd.txt
├── targets.intigriti.txt
│
├── data/
│   ├── hackerone/
│   │   ├── baseline/
│   │   │   ├── hackerone.com_baseline.json
│   │   │   └── api.hackerone.com_baseline.json
│   │   ├── diffs/
│   │   │   └── hackerone.com_20250121_140530.json
│   │   ├── subdomain_scans/
│   │   │   └── hackerone.com/
│   │   └── shodan_scans/
│   │       └── hackerone.com_20250121_140530.json
│   ├── bugcrowd/
│   └── intigriti/
│
├── reports/
│   ├── hackerone/
│   ├── bugcrowd/
│   └── intigriti/
│
├── logs/
│   ├── hackerone_monitor.log
│   ├── hackerone_weekly.log
│   ├── bugcrowd_monitor.log
│   ├── bugcrowd_biweekly.log
│   ├── intigriti_monitor.log
│   └── intigriti_monthly.log
│
└── scripts/
    ├── view_hackerone.sh
    ├── view_bugcrowd.sh
    ├── view_intigriti.sh
    ├── view_all.sh
    ├── compare_programs.sh
    ├── check_status.sh
    └── setup_all_crons.sh
```

## Notification Examples

### HackerOne (High-Value)

**New Subdomain Found** → Slack + Telegram
```
🎯 New Subdomain: hackerone.com

• New: admin-staging.hackerone.com
• Status: 200 OK
• Tech: nginx 1.18.0, React
• Ports: 80, 443

Time: 2025-01-21 14:05:30
```

**Subdomain Takeover** → Slack + Telegram + Email
```
🚨 CRITICAL: Subdomain Takeover Detected

Domain: old-app.hackerone.com
Service: Heroku
CNAME: oldapp.herokuapp.com
Status: High confidence

Verify: curl -H "Host: old-app.hackerone.com" https://oldapp.herokuapp.com

Time: 2025-01-21 14:10:15
```

### Bugcrowd (Medium-Value)

**Critical Finding Only** → Slack
```
⚠️  High-Value Target: bugcrowd.com

• New: /admin/debug.php
• Status: 200 OK
• Keywords: admin, debug

Time: 2025-01-21 16:30:00
```

**Daily Digest** → Slack (9 AM)
```
📊 Bugcrowd Daily Digest

New Subdomains: 3
New Endpoints: 12
Changes: 5
Takeovers: 0

View: ./view_bugcrowd.sh --interactive

Date: 2025-01-21
```

### Intigriti (Low-Priority)

**Daily Digest Only** → Slack (10 AM)
```
📋 Intigriti Daily Summary

Subdomains: 45 (no changes)
Endpoints: 180 (+2 new)
Last Scan: 09:00:30

View details: ./view_intigriti.sh
```

## Maintenance

### Weekly Tasks

```bash
# Check disk space
du -sh data/*

# Archive old logs (keep last 30 days)
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;

# Verify all baselines exist
for program in hackerone bugcrowd intigriti; do
    ls -lh data/$program/baseline/
done
```

### Monthly Tasks

```bash
# Run comprehensive scans
./monitor.py -c config.hackerone.yaml --init
./monitor.py -c config.bugcrowd.yaml --init
./monitor.py -c config.intigriti.yaml --init

# Backup data
tar -czf backup_$(date +%Y%m).tar.gz data/ logs/

# Review and update targets
vim targets.*.txt
```

## Troubleshooting

### Program not scanning

```bash
# Test manually
./monitor.py -c config.PROGRAM.yaml --monitor

# Check cron
crontab -l | grep PROGRAM

# Check logs
tail -50 logs/PROGRAM_monitor.log
```

### No alerts received

```bash
# Test notification
python3 -c "
from modules.notifier import Notifier
import yaml

with open('config.PROGRAM.yaml') as f:
    config = yaml.safe_load(f)

notifier = Notifier(config['notifications'])
notifier.send_slack('Test Alert', {})
"
```

### Dashboard shows no data

```bash
# Check baseline
ls -lh data/PROGRAM/baseline/

# Verify paths in config
grep data_dir config.PROGRAM.yaml

# Re-run baseline
./monitor.py -c config.PROGRAM.yaml --init
```

## Success Metrics

After 1 week, you should have:
- ✅ 3+ baseline scans per program
- ✅ Automated cron jobs running
- ✅ Notifications working
- ✅ Dashboards showing data
- ✅ No errors in logs

After 1 month:
- ✅ Identified 5-10 new subdomains per program
- ✅ Detected 1-2 configuration changes
- ✅ Found potential takeovers (if any exist)
- ✅ Received daily digests
- ✅ Clean, organized data structure

---

This complete example gives you a production-ready multi-program monitoring setup! 🎉
