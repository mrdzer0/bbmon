# Quick Start: Using Monitor for Multiple Programs

This guide shows you how to use the Bug Bounty Monitor for multiple programs with different configurations.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Quick Setup (3 Steps)](#quick-setup-3-steps)
- [Common Use Cases](#common-use-cases)
- [Dashboard Views](#dashboard-views)
- [Full Documentation](#full-documentation)

---

## Basic Usage

The monitor supports different configuration files using the `-c` or `--config` flag:

```bash
# Use default config (config.yaml)
./monitor.py --init

# Use custom config
./monitor.py -c config.hackerone.yaml --init
./monitor.py -c config.bugcrowd.yaml --monitor
```

---

## Quick Setup (3 Steps)

### Step 1: Create Program-Specific Configs

```bash
# Copy example config for each program
cp config.yaml.example config.program-a.yaml
cp config.yaml.example config.program-b.yaml
```

### Step 2: Edit Each Config

**config.program-a.yaml**:
```yaml
# Set targets
targets:
  domains_file: targets.program-a.txt

# Set data directories
monitoring:
  data_dir: ./data/program-a
  baseline_dir: ./data/program-a/baseline
  diff_dir: ./data/program-a/diffs
  reports_dir: ./reports/program-a

# Set notifications
notifications:
  slack:
    enabled: true
    webhook_url: "YOUR_PROGRAM_A_WEBHOOK"
```

**config.program-b.yaml**:
```yaml
targets:
  domains_file: targets.program-b.txt

monitoring:
  data_dir: ./data/program-b
  baseline_dir: ./data/program-b/baseline
  diff_dir: ./data/program-b/diffs
  reports_dir: ./reports/program-b

notifications:
  slack:
    enabled: true
    webhook_url: "YOUR_PROGRAM_B_WEBHOOK"
```

### Step 3: Create Target Lists

**targets.program-a.txt**:
```
example.com
api.example.com
app.example.com
```

**targets.program-b.txt**:
```
company.com
dev.company.com
```

### Step 4: Run Initial Scans

```bash
# Initialize program A
./monitor.py -c config.program-a.yaml --init

# Initialize program B
./monitor.py -c config.program-b.yaml --init
```

---

## Common Use Cases

### Use Case 1: Different Scan Frequencies

**Fast scans for high-value program** (config.high-priority.yaml):
```yaml
tools:
  amass:
    enabled: false  # Skip slow tools
  katana:
    enabled: false

advanced:
  max_workers: 30   # Fast parallel processing
```

Run every 4 hours:
```bash
# Add to crontab
0 */4 * * * cd /path/to/bb-monitor && ./monitor.py -c config.high-priority.yaml --monitor
```

**Deep scans for weekly comprehensive check** (config.comprehensive.yaml):
```yaml
tools:
  amass:
    enabled: true   # Enable all tools
  katana:
    enabled: true
    depth: 4
  nuclei:
    enabled: true

advanced:
  max_workers: 5    # Thorough scanning
```

Run weekly:
```bash
# Add to crontab
0 2 * * 0 cd /path/to/bb-monitor && ./monitor.py -c config.comprehensive.yaml --init
```

### Use Case 2: Different Notification Channels

**Critical alerts for program A** (config.critical-program.yaml):
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${PROGRAM_A_SLACK}"
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT}"
    chat_id: "${PROGRAM_A_CHAT}"
  email:
    enabled: true
    to_email: "alerts@yourdomain.com"
```

**Daily digest for program B** (config.low-priority.yaml):
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${PROGRAM_B_SLACK}"
    notify_on:
      - subdomain_takeover  # Only critical alerts
      - shodan_vulnerabilities

  daily_digest:
    enabled: true
    time: "09:00"
```

### Use Case 3: Different Tool Configurations

**Shodan enabled for program A** (config.with-shodan.yaml):
```yaml
tools:
  shodan:
    enabled: true
    api_key: "${BB_SHODAN_API_KEY}"
    scan_on:
      - new_subdomain
      - baseline_init
```

**Wayback enabled for program B** (config.with-wayback.yaml):
```yaml
tools:
  wayback:
    enabled: true
    max_results: 10000
    scan_on:
      - new_subdomain
      - baseline_init
    export_categories:
      - backup
      - database
      - credentials
```

---

## Dashboard Views

### View Specific Program Dashboard

**Option 1: Using Config File (Recommended)**

```bash
# View dashboard for program A (reads data_dir from config)
python3 modules/dashboard.py -c config.program-a.yaml

# View specific section for program B
python3 modules/dashboard.py -c config.program-b.yaml -v security

# View all data for program A
python3 modules/dashboard.py -c config.program-a.yaml -v all

# Filter by domain
python3 modules/dashboard.py -c config.program-a.yaml -d example.com
```

**Option 2: Using Helper Script (Easiest)**

```bash
# View dashboard for program A
./utils/view_program.sh program-a

# View specific section for program B
./utils/view_program.sh program-b security

# View all sections
./utils/view_program.sh program-a all
```

**Option 3: Using Data Directory Directly**

```bash
# View program A dashboard
python3 modules/dashboard.py --data-dir ./data/program-a

# View program B with specific view
python3 modules/dashboard.py --data-dir ./data/program-b -v security

# View all data for program A
python3 modules/dashboard.py --data-dir ./data/program-a -v all
```

### Available Views

- `overview` - Statistics and HTTP status distribution (default)
- `subdomains` - List all subdomains with status codes
- `endpoints` - List endpoints grouped by HTTP status with technologies
- `technologies` - Technology stack statistics
- `security` - Security findings (takeovers, high-value targets, etc.)
- `shodan` - Shodan intelligence with detailed findings
- `wayback` - Wayback Machine results with sample URLs
- `all` - Show everything

### Filter by Domain

```bash
# Using config file
python3 modules/dashboard.py -c config.program-a.yaml -d example.com

# Show Shodan results for specific domain
python3 modules/dashboard.py -c config.program-a.yaml -d example.com -v shodan

# Using data directory directly
python3 modules/dashboard.py --data-dir ./data/program-a -d example.com
```

---

## Monitoring Commands

### Manual Runs

```bash
# Initialize baseline for program A
./monitor.py -c config.program-a.yaml --init

# Run monitoring check for program A
./monitor.py -c config.program-a.yaml --monitor

# Do the same for program B
./monitor.py -c config.program-b.yaml --init
./monitor.py -c config.program-b.yaml --monitor
```

### Automated Monitoring (Cron)

Edit crontab:
```bash
crontab -e
```

Add entries for each program:
```cron
# Program A - Every 6 hours
0 */6 * * * cd /path/to/bb-monitor && ./monitor.py -c config.program-a.yaml --monitor >> logs/program-a.log 2>&1

# Program B - Every 8 hours
0 */8 * * * cd /path/to/bb-monitor && ./monitor.py -c config.program-b.yaml --monitor >> logs/program-b.log 2>&1

# Program C - Daily at 9 AM
0 9 * * * cd /path/to/bb-monitor && ./monitor.py -c config.program-c.yaml --monitor >> logs/program-c.log 2>&1
```

---

## File Organization

Your directory will look like this:

```
bb-monitor/
├── monitor.py
├── config.program-a.yaml          # Config for program A
├── config.program-b.yaml          # Config for program B
├── config.program-c.yaml          # Config for program C
├── targets.program-a.txt          # Targets for program A
├── targets.program-b.txt          # Targets for program B
├── targets.program-c.txt          # Targets for program C
│
├── data/
│   ├── program-a/                 # Program A data
│   │   ├── baseline/
│   │   ├── diffs/
│   │   ├── subdomain_scans/
│   │   ├── shodan_scans/
│   │   └── wayback_scans/
│   ├── program-b/                 # Program B data
│   └── program-c/                 # Program C data
│
├── reports/
│   ├── program-a/
│   ├── program-b/
│   └── program-c/
│
└── logs/
    ├── program-a.log
    ├── program-b.log
    └── program-c.log
```

---

## Quick Reference Commands

```bash
# Initialize new program
./monitor.py -c config.NEW_PROGRAM.yaml --init

# Run monitoring
./monitor.py -c config.NEW_PROGRAM.yaml --monitor

# View dashboard (using config file - recommended)
python3 modules/dashboard.py -c config.NEW_PROGRAM.yaml

# View specific sections
python3 modules/dashboard.py -c config.NEW_PROGRAM.yaml -v shodan
python3 modules/dashboard.py -c config.NEW_PROGRAM.yaml -v wayback
python3 modules/dashboard.py -c config.NEW_PROGRAM.yaml -v security

# View all sections
python3 modules/dashboard.py -c config.NEW_PROGRAM.yaml -v all

# Filter by domain
python3 modules/dashboard.py -c config.NEW_PROGRAM.yaml -d example.com

# Alternative: Using data directory directly
python3 modules/dashboard.py --data-dir ./data/NEW_PROGRAM

# Check logs
tail -f logs/NEW_PROGRAM.log

# View latest report
cat reports/NEW_PROGRAM/latest.html
```

---

## Environment Variables (Optional)

Instead of hardcoding secrets in config files, use environment variables:

**.env**:
```bash
# Shodan
export BB_SHODAN_API_KEY="your_shodan_api_key"

# Program A webhooks
export PROGRAM_A_SLACK="https://hooks.slack.com/services/XXX/YYY/ZZZ"
export PROGRAM_A_CHAT="123456789"

# Program B webhooks
export PROGRAM_B_SLACK="https://hooks.slack.com/services/AAA/BBB/CCC"
export PROGRAM_B_CHAT="987654321"

# Shared credentials
export BB_TELEGRAM_TOKEN="bot_token_here"
export BB_EMAIL_PASSWORD="email_app_password"
```

Load before running:
```bash
source .env
./monitor.py -c config.program-a.yaml --monitor
```

Add to cron:
```cron
0 */6 * * * source /path/to/.env && cd /path/to/bb-monitor && ./monitor.py -c config.program-a.yaml --monitor
```

---

## Troubleshooting

### Config file not found
```bash
# Make sure you're in the bb-monitor directory
cd /path/to/bb-monitor

# Check if config file exists
ls -la config.program-a.yaml

# Verify config syntax
python3 -c "import yaml; yaml.safe_load(open('config.program-a.yaml'))"
```

### No targets found
```bash
# Check if targets file exists
ls -la targets.program-a.txt

# Make sure it's specified in config
grep "domains_file" config.program-a.yaml
```

### Dashboard shows no data
```bash
# Check if baseline was created
ls -lh data/program-a/baseline/

# Make sure you ran --init first
./monitor.py -c config.program-a.yaml --init

# Check correct data directory
python3 modules/dashboard.py --data-dir ./data/program-a
```

---

## Full Documentation

For comprehensive guides, see:

- **Multi-Program Setup**: `docs/02_Tutorials/MULTI_PROGRAM_SETUP.md`
- **Configuration Reference**: `docs/04_Reference/CONFIGURATION.md`
- **Usage Guide**: `docs/01_Getting_Started/USAGE.md`
- **Shodan Integration**: `docs/03_Guides/SHODAN_INTEGRATION.md`
- **Wayback Integration**: `docs/03_Guides/WAYBACK_INTEGRATION.md`

---

## Example: Complete Setup for 2 Programs

```bash
# Step 1: Create configs
cp config.yaml.example config.hackerone.yaml
cp config.yaml.example config.bugcrowd.yaml

# Step 2: Edit configs (set different data_dir, notifications)
vim config.hackerone.yaml   # Set data_dir: ./data/hackerone
vim config.bugcrowd.yaml    # Set data_dir: ./data/bugcrowd

# Step 3: Create target files
echo "hackerone.com" > targets.hackerone.txt
echo "bugcrowd.com" > targets.bugcrowd.txt

# Update configs to use these files
# config.hackerone.yaml -> domains_file: targets.hackerone.txt
# config.bugcrowd.yaml -> domains_file: targets.bugcrowd.txt

# Step 4: Initialize both programs
./monitor.py -c config.hackerone.yaml --init
./monitor.py -c config.bugcrowd.yaml --init

# Step 5: View dashboards
python3 modules/dashboard.py -c config.hackerone.yaml
python3 modules/dashboard.py -c config.bugcrowd.yaml

# Step 6: Setup automated monitoring
crontab -e
# Add:
# 0 */6 * * * cd /path/to/bb-monitor && ./monitor.py -c config.hackerone.yaml --monitor >> logs/hackerone.log 2>&1
# 0 */8 * * * cd /path/to/bb-monitor && ./monitor.py -c config.bugcrowd.yaml --monitor >> logs/bugcrowd.log 2>&1
```

Done! You're now monitoring multiple programs with separate configurations.
