# Bug Bounty Monitoring Framework - Project Structure

## Directory Layout

```
bb-monitor/
│
├── README.md                # Main documentation & quick start
├── LICENSE                  # MIT License
├── CHANGELOG.md             # Version history & roadmap
├── CONTRIBUTING.md          # Contribution guidelines
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
│
├── monitor.py              # 🎯 Main monitoring script
├── config.yaml             # ⚙️ Configuration file
├── targets.txt             # 🎯 Target domains (add yours here)
├── targets.txt.example     # Example targets file
│
├── modules/                # 📦 Core modules
│   ├── __init__.py
│   ├── subdomain_finder.py    # Subdomain discovery & takeover detection
│   ├── http_monitor.py        # HTTP monitoring & smart flagging
│   ├── dashboard.py           # Terminal dashboard
│   └── notifier.py            # Multi-platform notifications
│
├── utils/                  # 🛠️ Utility scripts
│   ├── install.sh             # Installation script
│   ├── setup_cron.sh          # Cron automation setup
│   └── subdomain_scan.sh      # Standalone subdomain scanner
│
├── docs/                   # 📚 Documentation
│   ├── USAGE.md              # Detailed usage guide
│   ├── CONFIGURATION.md      # Configuration reference
│   └── TROUBLESHOOTING.md    # Common issues & solutions
│
├── data/                   # 📊 Data directory (auto-created)
│   ├── baseline/             # Baseline snapshots
│   ├── diffs/                # Change detections
│   ├── subdomain_scans/      # Subdomain scan results
│   └── http_snapshots/       # HTTP probe snapshots
│
├── reports/                # 📈 Generated reports (auto-created)
│   └── report_*.html
│
└── logs/                   # 📝 Log files (auto-created)
    └── monitor.log
```

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `monitor.py` | Main monitoring script - runs baseline collection and change detection |
| `config.yaml` | Configuration for targets, checks, tools, and notifications |
| `targets.txt` | List of domains to monitor (one per line) |
| `requirements.txt` | Python package dependencies |
| `.gitignore` | Files to exclude from git |
| `LICENSE` | MIT License |
| `README.md` | Main documentation with quick start |
| `CHANGELOG.md` | Version history and roadmap |
| `CONTRIBUTING.md` | Guidelines for contributors |

### Modules (modules/)

| Module | Purpose | Size |
|--------|---------|------|
| `subdomain_finder.py` | Multi-source subdomain discovery, DNS validation, takeover detection | 23KB |
| `http_monitor.py` | HTTP probing, technology detection, smart flagging, change comparison | 22KB |
| `dashboard.py` | Terminal-based dashboard for viewing statistics and recent changes | 9KB |
| `notifier.py` | Multi-platform notifications (Slack, Discord, Telegram, Email) | 9KB |
| `__init__.py` | Module initialization and exports | 1KB |

### Utilities (utils/)

| Script | Purpose |
|--------|---------|
| `install.sh` | Automated installation of dependencies and tools |
| `setup_cron.sh` | Configure cron jobs for automated monitoring |
| `subdomain_scan.sh` | Standalone subdomain scanner with multiple modes |

### Documentation (docs/)

| Document | Content |
|----------|---------|
| `USAGE.md` | Detailed usage guide with examples |
| `CONFIGURATION.md` | Complete configuration reference |
| `TROUBLESHOOTING.md` | Common issues and solutions |

## Module Architecture

```
┌─────────────────────────────────────────┐
│          monitor.py (Main)              │
│  Orchestrates all modules               │
└─────────────────────────────────────────┘
              │
              ├──> subdomain_finder.py
              │    • Multi-source discovery
              │    • DNS validation
              │    • Takeover detection
              │
              ├──> http_monitor.py
              │    • HTTP probing
              │    • Technology detection
              │    • Smart flagging
              │    • Change comparison
              │
              ├──> notifier.py
              │    • Slack
              │    • Discord
              │    • Telegram
              │    • Email
              │
              └──> dashboard.py
                   • Statistics
                   • Recent changes
                   • Interactive view
```

## Data Flow

```
1. User adds domains to targets.txt
              ↓
2. Run: ./monitor.py --init
   • Discovers subdomains
   • Checks for takeovers
   • Probes HTTP endpoints
   • Detects technologies
   • Flags high-value targets
   • Saves baseline
              ↓
3. Baseline stored in data/baseline/
              ↓
4. Run: ./monitor.py --monitor (daily/hourly)
   • Collects current data
   • Compares with baseline
   • Detects changes
   • Flags new findings
   • Sends notifications
   • Updates baseline
              ↓
5. Changes stored in data/diffs/
              ↓
6. Reports generated in reports/
              ↓
7. View with: ./modules/dashboard.py
```

## Key Features by Module

### subdomain_finder.py
- ✅ Integrates 5+ tools (subfinder, assetfinder, crt.sh, chaos, amass)
- ✅ Parallel execution
- ✅ DNS validation with dnsx
- ✅ Subdomain takeover detection (20+ services)
- ✅ CNAME analysis
- ✅ HTTP fingerprinting
- ✅ Confidence scoring

### http_monitor.py
- ✅ Tracks: status code, title, body length, technologies, headers
- ✅ Content hashing for change detection
- ✅ Smart flagging (admin, login, upload, api, backup)
- ✅ Outdated technology detection
- ✅ Security header analysis
- ✅ Parallel HTTP probing
- ✅ Detailed change comparison

### dashboard.py
- ✅ Real-time statistics
- ✅ Recent changes display
- ✅ Simple & interactive modes
- ✅ Color-coded output
- ✅ Historical tracking

### notifier.py
- ✅ Multi-platform support
- ✅ Configurable triggers
- ✅ Priority-based routing
- ✅ Rich formatting
- ✅ Daily digests

## Configuration Hierarchy

```
config.yaml
├── targets              # Which domains to monitor
├── monitoring           # When and how to monitor
├── checks               # What to check
├── tools                # Tool configurations
├── notifications        # Where to send alerts
├── diff_settings        # Change detection rules
├── priority             # Alert prioritization
└── advanced             # Performance tuning
```

## Usage Patterns

### Pattern 1: Initial Setup
```bash
./utils/install.sh        # Install dependencies
echo "target.com" >> targets.txt
./monitor.py --init       # Collect baseline
```

### Pattern 2: Daily Monitoring
```bash
./monitor.py --monitor    # Check for changes
./modules/dashboard.py    # View results
```

### Pattern 3: Automated
```bash
./utils/setup_cron.sh     # Setup automation
# Runs every 6 hours automatically
```

### Pattern 4: Standalone Scanning
```bash
./utils/subdomain_scan.sh -d example.com
./modules/http_monitor.py -l urls.txt
```

## Best Practices

### For Clean Maintenance

1. **Keep targets.txt organized**:
   ```
   # Group by program
   # HackerOne
   hackerone.com
   hackerone-ctf.com

   # Bugcrowd
   bugcrowd.com
   ```

2. **Regular cleanup**:
   ```bash
   # Remove old diffs (>30 days)
   find data/diffs/ -mtime +30 -delete

   # Archive baselines
   tar -czf backup_$(date +%Y%m%d).tar.gz data/baseline/
   ```

3. **Version control config**:
   ```bash
   git add config.yaml
   git commit -m "Updated notification settings"
   ```

4. **Separate sensitive data**:
   ```bash
   # Use environment variables
   export BB_SLACK_WEBHOOK="..."
   # Don't commit secrets
   ```

### For GitHub

1. **Fork repository**
2. **Clone your fork**
3. **Create branch for changes**
4. **Submit PR with clear description**
5. **Follow code style**

## Quick Commands Reference

```bash
# Setup
./utils/install.sh
echo "target.com" >> targets.txt

# Baseline
./monitor.py --init

# Monitor
./monitor.py --monitor

# Dashboard
./modules/dashboard.py
./modules/dashboard.py --interactive

# Standalone
./utils/subdomain_scan.sh -d example.com
./modules/http_monitor.py -l urls.txt

# Automation
./utils/setup_cron.sh

# Logs
tail -f logs/monitor.log

# Clean
find data/diffs/ -mtime +30 -delete
```

---

This structure keeps everything organized, modular, and easy to maintain! 🎯
