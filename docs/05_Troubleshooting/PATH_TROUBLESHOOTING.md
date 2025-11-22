# Path Configuration & Troubleshooting

## Overview

This document explains the directory structure and path configuration of the BB-Monitor framework to help troubleshoot path-related issues.

## Directory Structure

```
bb-monitor/                    # Project root
├── monitor.py                 # Main script (run from here)
├── config.yaml               # Your configuration
├── targets.txt               # Your targets
│
├── modules/                  # Python modules
│   ├── __init__.py
│   ├── subdomain_finder.py
│   ├── http_monitor.py
│   ├── shodan_scanner.py
│   ├── dashboard.py
│   └── notifier.py
│
├── utils/                    # Utility scripts
│   ├── install.sh
│   ├── setup_cron.sh
│   ├── subdomain_scan.sh
│   └── test_paths.sh
│
├── data/                     # Auto-created data directory
│   ├── baseline/
│   ├── diffs/
│   ├── subdomain_scans/
│   └── shodan_scans/
│
├── reports/                  # Auto-created reports
└── logs/                     # Auto-created logs
```

## Running Scripts

### ✅ Correct Usage

All scripts should be run from the **project root** directory:

```bash
# Navigate to project root
cd /path/to/bb-monitor

# Run main script
./monitor.py --init

# Run utility scripts
./utils/subdomain_scan.sh -d example.com
./utils/setup_cron.sh

# Run modules directly
python3 modules/subdomain_finder.py -d example.com
python3 modules/http_monitor.py -l urls.txt
python3 modules/dashboard.py
python3 modules/shodan_scanner.py API_KEY example.com
```

### ❌ Common Mistakes

**Wrong**: Running from subdirectories
```bash
cd utils/
./subdomain_scan.sh -d example.com  # FAILS - wrong directory
```

**Correct**: Run from project root
```bash
cd bb-monitor/
./utils/subdomain_scan.sh -d example.com  # WORKS
```

## Path Resolution

### How Scripts Find Files

All utility scripts use this pattern to find the project root:

```bash
# In any utility script (utils/*.sh)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Example: If script is at /home/user/bb-monitor/utils/subdomain_scan.sh
# SCRIPT_DIR = /home/user/bb-monitor/utils
# PROJECT_ROOT = /home/user/bb-monitor
```

### Module Imports

Python modules use relative imports from the project root:

```python
# In monitor.py (project root)
from modules.subdomain_finder import SubdomainFinder
from modules.http_monitor import HTTPMonitor
from modules.shodan_scanner import ShodanScanner
```

## Testing Path Configuration

Run the test script to verify all paths are correct:

```bash
./utils/test_paths.sh
```

This will check:
- ✓ All critical files exist
- ✓ Python modules can be imported
- ✓ Standalone scripts work
- ✓ Utility scripts function correctly

## Common Issues

### Issue 1: "No such file or directory"

**Error**:
```
/usr/bin/python3: can't open file '/home/user/bb-monitor/./utils/subdomain_finder.py': [Errno 2] No such file or directory
```

**Cause**: Script is looking for file in wrong location (utils/ instead of modules/)

**Solution**: Update to latest version with corrected paths:
```bash
git pull origin main
```

Or manually fix in `utils/subdomain_scan.sh` line 168:
```bash
# Old (wrong)
PYTHON_CMD="python3 $SCRIPT_DIR/subdomain_finder.py -d $DOMAIN"

# New (correct)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_CMD="python3 $PROJECT_ROOT/modules/subdomain_finder.py -d $DOMAIN"
```

### Issue 2: "Module not found"

**Error**:
```
ModuleNotFoundError: No module named 'modules'
```

**Cause**: Running Python scripts from wrong directory

**Solution**: Always run from project root:
```bash
# Wrong
cd modules/
python3 subdomain_finder.py -d example.com

# Correct
cd /path/to/bb-monitor/
python3 modules/subdomain_finder.py -d example.com
```

### Issue 3: Config file not found

**Error**:
```
[!] Error loading config: [Errno 2] No such file or directory: 'config.yaml'
```

**Cause**: No config.yaml file exists (only config.yaml.example)

**Solution**: Copy the example config:
```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your settings
```

### Issue 4: Data directories not created

**Error**:
```
FileNotFoundError: [Errno 2] No such file or directory: './data/baseline'
```

**Cause**: Data directories haven't been created yet

**Solution**: Directories are auto-created on first run, or create manually:
```bash
mkdir -p data/{baseline,diffs,subdomain_scans,shodan_scans}
mkdir -p reports logs
```

### Issue 5: Cron job paths incorrect

**Error**: Cron job runs but doesn't find monitor.py

**Cause**: Cron uses different working directory

**Solution**: Use absolute paths in cron. The `setup_cron.sh` script handles this:
```bash
./utils/setup_cron.sh
```

This creates:
```cron
0 */6 * * * cd /absolute/path/to/bb-monitor && /absolute/path/to/bb-monitor/monitor.py --monitor >> /absolute/path/to/bb-monitor/logs/monitor.log 2>&1
```

### Issue 6: Permission denied

**Error**:
```
bash: ./monitor.py: Permission denied
```

**Cause**: Script is not executable

**Solution**: Make scripts executable:
```bash
chmod +x monitor.py
chmod +x utils/*.sh
chmod +x modules/*.py
```

Or use python explicitly:
```bash
python3 monitor.py --init
```

## Relative vs Absolute Paths

### Relative Paths (default)

Config uses relative paths by default:
```yaml
monitoring:
  data_dir: ./data
  baseline_dir: ./data/baseline
  diff_dir: ./data/diffs
  reports_dir: ./reports
```

**Advantage**: Project is portable (can move directory)
**Disadvantage**: Must run from project root

### Absolute Paths (for cron)

For cron jobs, use absolute paths:
```yaml
monitoring:
  data_dir: /home/user/bb-monitor/data
  baseline_dir: /home/user/bb-monitor/data/baseline
  diff_dir: /home/user/bb-monitor/data/diffs
  reports_dir: /home/user/bb-monitor/reports
```

**Advantage**: Works from any directory
**Disadvantage**: Breaks if you move the project

## Best Practices

### 1. Always use project root

```bash
# Set up alias for convenience
echo 'alias bbmon="cd /path/to/bb-monitor && "' >> ~/.bashrc
source ~/.bashrc

# Then use
bbmon ./monitor.py --init
bbmon ./utils/subdomain_scan.sh -d example.com
```

### 2. Create wrapper scripts

```bash
# ~/bin/bb-monitor
#!/bin/bash
cd /path/to/bb-monitor
./monitor.py "$@"
```

Make executable and add to PATH:
```bash
chmod +x ~/bin/bb-monitor
export PATH="$HOME/bin:$PATH"

# Now use from anywhere
bb-monitor --init
```

### 3. Use absolute paths in automation

For cron, systemd, or other automation:
```bash
# Use absolute paths
/usr/bin/python3 /home/user/bb-monitor/monitor.py --monitor
```

### 4. Version control config

Keep your config in a separate location:
```bash
# Symlink config from secure location
ln -s ~/secure/bb-monitor-config.yaml config.yaml

# Add to .gitignore
echo "config.yaml" >> .gitignore
```

## Environment Setup

### Shell Configuration

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# BB-Monitor configuration
export BBMON_ROOT="/path/to/bb-monitor"
export PATH="$BBMON_ROOT:$PATH"

# Aliases
alias bbmon="cd $BBMON_ROOT"
alias bbmon-init="cd $BBMON_ROOT && ./monitor.py --init"
alias bbmon-run="cd $BBMON_ROOT && ./monitor.py --monitor"
alias bbmon-dash="cd $BBMON_ROOT && ./modules/dashboard.py"

# API keys
export BB_SHODAN_API_KEY="your_key_here"
export BB_SLACK_WEBHOOK="your_webhook_here"
```

### Python Virtual Environment

For isolated dependencies:

```bash
cd /path/to/bb-monitor

# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run scripts
./monitor.py --init
```

Add to cron with venv:
```cron
0 */6 * * * cd /path/to/bb-monitor && source venv/bin/activate && ./monitor.py --monitor >> logs/monitor.log 2>&1
```

## Troubleshooting Checklist

When encountering path issues, check:

- [ ] Are you in the project root directory? (`pwd` should show `.../bb-monitor`)
- [ ] Does the file exist? (`ls -la` to verify)
- [ ] Are scripts executable? (`ls -l` shows `rwxr-xr-x`)
- [ ] Is Python in PATH? (`which python3`)
- [ ] Are modules importable? (`python3 -c "from modules import *"`)
- [ ] Is config.yaml present? (`test -f config.yaml && echo "exists"`)
- [ ] Run path test: (`./utils/test_paths.sh`)

## Quick Fixes

### Reset everything
```bash
cd /path/to/bb-monitor

# Make all scripts executable
chmod +x monitor.py modules/*.py utils/*.sh

# Create config if missing
[ ! -f config.yaml ] && cp config.yaml.example config.yaml

# Create data directories
mkdir -p data/{baseline,diffs,subdomain_scans,shodan_scans}
mkdir -p reports logs

# Test paths
./utils/test_paths.sh
```

### Verify installation
```bash
# Test main script
./monitor.py --help

# Test utilities
./utils/subdomain_scan.sh --help

# Test modules
python3 modules/subdomain_finder.py --help
python3 modules/http_monitor.py --help
python3 modules/dashboard.py --help

# Test imports
python3 -c "from modules.subdomain_finder import SubdomainFinder; print('OK')"
```

## Getting Help

If issues persist:

1. **Run diagnostics**:
   ```bash
   ./utils/test_paths.sh > path_test.log 2>&1
   ```

2. **Check versions**:
   ```bash
   python3 --version
   pip3 list | grep -E "requests|yaml|shodan"
   ```

3. **Review recent changes**:
   ```bash
   git status
   git log --oneline -5
   ```

4. **Create issue** with:
   - Output of `./utils/test_paths.sh`
   - Your operating system
   - Python version
   - Error messages

## Related Documentation

- [USAGE.md](USAGE.md) - General usage guide
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - General troubleshooting
- [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) - Complete project structure
