# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Bug Bounty Monitoring Framework** that continuously tracks target infrastructure for changes. It integrates multiple reconnaissance tools, detects security findings, and sends notifications across platforms (Discord, Slack, Telegram, Email).

## Core Architecture

### Main Workflow (`monitor.py`)

The monitoring system operates in two modes:

1. **Baseline Mode (`--init`)**: Creates initial snapshots of target infrastructure
2. **Monitoring Mode (`--monitor`)**: Compares current state with baseline and detects changes

**Data Flow:**
```
Targets (config.yaml/targets.txt)
  → Subdomain Discovery (SubdomainFinder)
  → HTTP Probing (HTTPMonitor)
  → Optional: Shodan Scan, Wayback Analysis
  → Baseline Storage (JSON)
  → Change Detection (difflib)
  → Notifications (Notifier)
  → Reports (HTML/JSON)
```

### Module Architecture

Each module is **self-contained** and **optional** (graceful degradation if not available):

- **`subdomain_finder.py`**: Orchestrates multiple tools (subfinder, assetfinder, amass) and detects subdomain takeovers via CNAME fingerprinting
- **`http_monitor.py`**: Probes URLs, extracts metadata (title, tech stack, headers), flags high-value targets (admin panels, APIs, upload forms)
- **`shodan_scanner.py`**: Queries Shodan API for host intelligence, vulnerability data, and exposed services
- **`wayback_analyzer.py`**: Fetches historical URLs from archive.org, classifies by file type (backups, configs, credentials)
- **`notifier.py`**: Multi-platform notification dispatcher with baseline alerts and change alerts
- **`dashboard.py`**: Terminal-based data viewer with multiple view modes

### Multi-Program Support

The framework supports **isolated monitoring of multiple bug bounty programs** using the `-c/--config` flag:

```bash
./monitor.py -c config.program-a.yaml --init
./monitor.py -c config.program-b.yaml --monitor
python3 modules/dashboard.py -c config.program-a.yaml
```

**Critical**: Each program must have separate `data_dir`, `baseline_dir`, and `diff_dir` in config to ensure data isolation.

### Configuration System

Configuration uses YAML with three layers:
1. **`config.yaml.example`**: Template with all options documented
2. **`config.yaml`** (or `config.{program}.yaml`): User configuration
3. **Environment variables**: Overrides for secrets (e.g., `BB_SHODAN_API_KEY`)

**Key sections:**
- `targets`: Domain lists or file paths
- `monitoring`: Data directories and retention
- `checks`: Enable/disable specific monitoring features
- `tools`: Configuration for external tools (subfinder, httpx, shodan, wayback)
- `notifications`: Multi-platform alert settings

## Common Commands

### Basic Operations
```bash
# Initialize baseline for default config
./monitor.py --init

# Run monitoring check (compares with baseline)
./monitor.py --monitor

# View dashboard (reads from ./data by default)
python3 modules/dashboard.py

# View specific dashboard section
python3 modules/dashboard.py -v shodan
python3 modules/dashboard.py -v wayback
```

### Multi-Program Operations
```bash
# Initialize specific program
./monitor.py -c config.hackerone.yaml --init

# Monitor specific program
./monitor.py -c config.bugcrowd.yaml --monitor

# View program dashboard (reads data_dir from config)
python3 modules/dashboard.py -c config.hackerone.yaml

# Quick view helper script
./utils/view_program.sh hackerone
./utils/view_program.sh bugcrowd security
```

### Testing & Debugging
```bash
# Test Discord notifications
python3 utils/test_notifications.py -c config.yaml --discord

# Test Slack notifications
python3 utils/test_notifications.py -c config.yaml --slack

# Check Discord configuration
./utils/fix_discord_config.sh

# Standalone subdomain scan (without full monitoring)
./utils/subdomain_scan.sh example.com
```

### Automation
```bash
# Setup cron jobs for automated monitoring
./utils/setup_cron.sh

# Install dependencies
./utils/install.sh
```

## Data Storage Structure

```
data/{program}/
├── baseline/              # Baseline snapshots (JSON)
│   └── {domain}_baseline.json
├── diffs/                 # Change detection results
│   └── {domain}_diff_{timestamp}.json
├── subdomain_scans/       # Raw subdomain discovery output
│   └── {domain}_{timestamp}.json
├── shodan_scans/          # Shodan API results
│   └── {domain}_{timestamp}.json
├── wayback_scans/         # Wayback Machine results
│   └── {domain}_{timestamp}.json
└── http_snapshots/        # Directory for HTTP response data
```

**Baseline Format:**
```json
{
  "domain": "example.com",
  "timestamp": "2025-01-22T12:00:00",
  "subdomains": {"www.example.com": ["1.2.3.4"], ...},
  "endpoints": {"https://example.com": {"status_code": 200, "title": "...", ...}},
  "subdomain_takeovers": [...],
  "shodan_data": {...},
  "wayback_data": {...}
}
```

## Critical Implementation Details

### 1. Dashboard Data Isolation (`modules/dashboard.py`)

The Dashboard class **must** derive `baseline_dir` and `diff_dir` from `data_dir` if not explicitly provided:

```python
def __init__(self, data_dir="./data", diff_dir=None, baseline_dir=None):
    self.data_dir = Path(data_dir)
    self.diff_dir = Path(diff_dir) if diff_dir else self.data_dir / "diffs"
    self.baseline_dir = Path(baseline_dir) if baseline_dir else self.data_dir / "baseline"
```

When using `-c` flag, load all three directories from config:
```python
monitoring = config.get('monitoring', {})
data_dir = monitoring.get('data_dir', './data')
baseline_dir = monitoring.get('baseline_dir')
diff_dir = monitoring.get('diff_dir')
dashboard = Dashboard(data_dir=data_dir, baseline_dir=baseline_dir, diff_dir=diff_dir)
```

### 2. Notification Triggers (`modules/notifier.py`)

**Baseline alerts** require `baseline_complete` in `notify_on` list:
```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "..."
    notify_on:
      - baseline_complete  # Required for --init scan alerts
      - new_subdomain
      - subdomain_takeover
```

**Change alerts** are triggered by specific change types (`new_subdomain`, `subdomain_takeover`, etc.) during `--monitor` runs.

### 3. Subdomain Takeover Detection (`modules/subdomain_finder.py`)

Takeover detection uses **CNAME fingerprinting** with confidence scoring:
- Checks 20+ cloud service fingerprints (Vercel, Netlify, GitHub Pages, AWS S3, etc.)
- Returns `confidence: "high"` if CNAME matches AND HTTP response matches fingerprint
- Returns `confidence: "medium"` if only CNAME matches

### 4. HTTP Monitoring with HTTPMonitor (`modules/http_monitor.py`)

**Preferred** over raw httpx calls for consistency. Key features:
- Content hashing for change detection
- Smart flagging system (admin, api, upload, backup, dev environments)
- Technology detection and vulnerable version flagging
- Parallel probing with thread pool

```python
http_monitor = HTTPMonitor(output_dir)
results = http_monitor.probe_multiple(urls, parallel=True)
```

### 5. Tool Availability Checks

All external integrations use try/except imports with feature flags:
```python
try:
    from modules.shodan_scanner import ShodanScanner
    SHODAN_AVAILABLE = True
except ImportError:
    SHODAN_AVAILABLE = False
```

Always check availability before using:
```python
if SHODAN_AVAILABLE and self.shodan_scanner:
    results = self.shodan_scanner.scan_subdomains(subdomains)
```

## Extending the Framework

### Adding New Notification Platforms

1. Add platform config to `config.yaml.example`:
```yaml
notifications:
  newplatform:
    enabled: false
    api_key: ""
    notify_on: []
```

2. Add sender method to `Notifier` class (`modules/notifier.py`):
```python
def send_newplatform(self, message: str, changes: Dict[str, Any]):
    if not self.config['newplatform']['enabled']:
        return
    # Implementation
```

3. Add baseline alert method if supporting baseline notifications:
```python
def _send_newplatform_baseline(self, summary: Dict[str, Any]):
    # Implementation
```

4. Call in `send_baseline_alert()`:
```python
if self.config.get('newplatform', {}).get('enabled'):
    if 'baseline_complete' in self.config['newplatform'].get('notify_on', []):
        self._send_newplatform_baseline(summary)
```

### Adding New Dashboard Views

1. Add extraction method in `Dashboard` class (`modules/dashboard.py`):
```python
def get_newdata(self, domain=None):
    """Extract new data from baselines"""
    baselines = self.get_all_baselines()
    # Extract and return data
```

2. Add render method:
```python
def _render_newview(self, domain=None):
    """Render new view"""
    data = self.get_newdata(domain)
    print("📊 NEW VIEW")
    # Display logic
```

3. Add view to choices in `main()`:
```python
parser.add_argument('-v', '--view',
    choices=['overview', 'subdomains', 'endpoints', 'technologies',
             'security', 'shodan', 'wayback', 'newview', 'all'])
```

4. Add case to `render_simple()`:
```python
elif view == 'newview':
    self._render_newview(domain)
```

### Adding New Reconnaissance Tools

1. Create module in `modules/newtool.py` with consistent interface:
```python
class NewTool:
    def __init__(self, config: Dict = None):
        self.config = config or {}

    def scan(self, target: str) -> Dict[str, Any]:
        # Implementation
        return results
```

2. Add optional import to `monitor.py`:
```python
try:
    from modules.newtool import NewTool
    NEWTOOL_AVAILABLE = True
except ImportError:
    NEWTOOL_AVAILABLE = False
```

3. Initialize in `BBMonitor.__init__()`:
```python
self.newtool = None
if NEWTOOL_AVAILABLE:
    tool_config = self.config.get('tools', {}).get('newtool', {})
    if tool_config.get('enabled', False):
        self.newtool = NewTool(tool_config)
```

4. Add scan method:
```python
def run_newtool_scan(self, domain: str) -> Dict[str, Any]:
    if not self.newtool:
        return {}
    return self.newtool.scan(domain)
```

5. Call in `collect_baseline()`:
```python
if self.newtool:
    baseline['newtool_data'] = self.run_newtool_scan(domain)
```

## Known Limitations

- **`http_snapshots` directory is created but unused**: HTTPMonitor doesn't currently save HTTP responses to disk, only metadata is stored in baseline JSON
- **No screenshot functionality**: Despite directory name, httpx screenshot feature is not implemented
- **Shodan DNS methods use standard DNS**: The Shodan Python library doesn't provide DNS resolution APIs, so `dns_lookup()` and `dns_reverse()` use Python's `socket` module instead
- **Change detection threshold**: `min_change_percent` in config only applies to content hash changes, not all change types
- **Parallel processing limit**: `max_workers` config affects subdomain probing but not all operations

## Documentation Structure

- **`QUICK_START_MULTI_PROGRAM.md`**: Complete guide for multi-program setups
- **`DISCORD_SETUP.md`**: Discord notification troubleshooting
- **`docs/01_Getting_Started/`**: Installation and basic usage
- **`docs/02_Tutorials/`**: Step-by-step guides (multi-program setup)
- **`docs/03_Guides/`**: Feature-specific guides (Shodan, Wayback integration)
- **`docs/04_Reference/`**: Configuration reference and API details
- **`docs/05_Troubleshooting/`**: Common issues and solutions
