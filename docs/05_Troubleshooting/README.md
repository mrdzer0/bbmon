# Troubleshooting

Solutions to common problems, error messages, and debugging guides.

## 📚 Available Guides

### [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
**General troubleshooting guide**

Solutions for common issues:

**Categories**:
- **Path & Directory Issues** - File/directory not found errors
- **Installation Issues** - Python modules, Go tools, permissions
- **Tool-Specific Problems** - subfinder, httpx, dnsx issues
- **Performance Issues** - Slow scans, timeouts, rate limits
- **Detection Issues** - Missing changes, false positives
- **Notification Problems** - Slack/Discord/Telegram not working
- **Data Issues** - Baseline problems, corrupted data

**Best for**:
- Fixing common errors
- Installation problems
- Tool configuration issues
- Notification setup

---

### [PATH_TROUBLESHOOTING.md](PATH_TROUBLESHOOTING.md)
**Path and directory troubleshooting**

Comprehensive guide for path-related issues:

**Topics**:
- Directory structure explanation
- How to run scripts correctly
- Path resolution in utilities
- Module imports
- Common path errors
- Testing path configuration
- Best practices
- Environment setup

**Best for**:
- "File not found" errors
- "Module not found" errors
- Script path issues
- Cron job path problems

---

## 🎯 Quick Problem Solver

### Select Your Problem

**❌ Scripts won't run / File not found**
→ [PATH_TROUBLESHOOTING.md](PATH_TROUBLESHOOTING.md)

**❌ Tools not working (subfinder, httpx)**
→ [TROUBLESHOOTING.md - Tool-Specific Problems](TROUBLESHOOTING.md#tool-specific-problems)

**❌ Notifications not sending**
→ [TROUBLESHOOTING.md - Notification Problems](TROUBLESHOOTING.md#notification-problems)

**❌ Scans are slow**
→ [TROUBLESHOOTING.md - Performance Issues](TROUBLESHOOTING.md#performance-issues)

**❌ Python import errors**
→ [TROUBLESHOOTING.md - Installation Issues](TROUBLESHOOTING.md#installation-issues)

**❌ Missing changes**
→ [TROUBLESHOOTING.md - Detection Issues](TROUBLESHOOTING.md#detection-issues)

**❌ Config not loading**
→ [PATH_TROUBLESHOOTING.md - Issue 3](PATH_TROUBLESHOOTING.md#issue-3-config-file-not-found)

**❌ Cron job not working**
→ [PATH_TROUBLESHOOTING.md - Issue 5](PATH_TROUBLESHOOTING.md#issue-5-cron-job-paths-incorrect)

---

## 🔍 Diagnostic Commands

### Check Your Setup

```bash
# Test path configuration
./utils/test_paths.sh

# Check Python modules
python3 -c "from modules.subdomain_finder import SubdomainFinder; print('OK')"

# Verify Go tools
which subfinder httpx dnsx

# Test config syntax
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Check logs
tail -50 logs/monitor.log

# Verify cron jobs
crontab -l | grep bb-monitor
```

---

## 💡 Common Solutions

### Problem: Command not found

```bash
# Add Go bin to PATH
export PATH=$PATH:~/go/bin
echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc

# Verify
which subfinder
```

**Guide**: [TROUBLESHOOTING.md - Go Tools Not Found](TROUBLESHOOTING.md#go-tools-not-found)

---

### Problem: Module not found

```bash
# Install requirements
pip3 install -r requirements.txt

# Verify
python3 -c "import requests, yaml; print('OK')"
```

**Guide**: [TROUBLESHOOTING.md - Python Module Not Found](TROUBLESHOOTING.md#python-module-not-found)

---

### Problem: Script path errors

```bash
# Always run from project root
cd /path/to/bb-monitor

# Test
./utils/subdomain_scan.sh -d example.com
```

**Guide**: [PATH_TROUBLESHOOTING.md - Running Scripts](PATH_TROUBLESHOOTING.md#running-scripts)

---

### Problem: Notifications not working

```bash
# Test webhook
curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test"}' \
     YOUR_WEBHOOK_URL

# Test from Python
python3 -c "
from modules.notifier import Notifier
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)
notifier = Notifier(config['notifications'])
notifier.send_slack('Test', {})
"
```

**Guide**: [TROUBLESHOOTING.md - Notification Problems](TROUBLESHOOTING.md#notification-problems)

---

### Problem: Scans too slow

```yaml
# Edit config.yaml
tools:
  amass:
    enabled: false  # Disable slow tools
  katana:
    enabled: false

advanced:
  max_workers: 20   # More parallelism
```

**Guide**: [TROUBLESHOOTING.md - Performance Issues](TROUBLESHOOTING.md#performance-issues)

---

## 🔧 Troubleshooting Workflow

### Step 1: Identify the Problem
- Read error message carefully
- Check logs: `tail -50 logs/monitor.log`
- Note what you were trying to do

### Step 2: Find the Right Guide
- Path errors → [PATH_TROUBLESHOOTING.md](PATH_TROUBLESHOOTING.md)
- Other errors → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Step 3: Try the Solution
- Follow guide step-by-step
- Test after each change
- Document what worked

### Step 4: Verify Fix
- Run test: `./utils/test_paths.sh`
- Try operation again
- Check logs for errors

---

## 📊 Error Message Reference

### Common Error Messages

| Error | Guide | Section |
|-------|-------|---------|
| `No such file or directory` | PATH_TROUBLESHOOTING.md | Issue 1 |
| `ModuleNotFoundError` | TROUBLESHOOTING.md | Python Module Not Found |
| `command not found: subfinder` | TROUBLESHOOTING.md | Go Tools Not Found |
| `Permission denied` | TROUBLESHOOTING.md | Permission Denied |
| `Config file not found` | PATH_TROUBLESHOOTING.md | Issue 3 |
| `401 Unauthorized` (Shodan) | TROUBLESHOOTING.md | Shodan Errors |
| `Webhook failed` | TROUBLESHOOTING.md | Notification Problems |
| `Timeout` | TROUBLESHOOTING.md | Performance Issues |

---

## 🔗 Related Documentation

### Before Troubleshooting
- [Getting Started - USAGE.md](../01_Getting_Started/USAGE.md) - Verify basic setup
- [Reference - CONFIGURATION.md](../04_Reference/CONFIGURATION.md) - Check config syntax

### After Fixing
- [Getting Started - CONFIG_QUICK_START.md](../01_Getting_Started/CONFIG_QUICK_START.md) - Optimize config
- [Tutorials](../02_Tutorials/) - Continue with tutorials

---

## 🎓 Debugging Tips

### Enable Verbose Logging

```bash
# Run with more output
./monitor.py --init --verbose

# Check detailed logs
tail -f logs/monitor.log
```

### Test Individual Components

```bash
# Test subdomain discovery
python3 modules/subdomain_finder.py -d example.com -o /tmp/test

# Test HTTP monitoring
python3 modules/http_monitor.py -l urls.txt

# Test Shodan
python3 modules/shodan_scanner.py API_KEY example.com

# Test dashboard
python3 modules/dashboard.py --data-dir ./data
```

### Verify Installation

```bash
# Run comprehensive test
./utils/test_paths.sh

# Check individual tools
subfinder -version
httpx -version
dnsx -version

# Check Python packages
pip3 list | grep -E "requests|yaml|shodan"
```

---

## 📞 Still Stuck?

### Collect Debug Information

```bash
# System info
uname -a
python3 --version

# Path test
./utils/test_paths.sh > debug.log 2>&1

# Last 100 log lines
tail -100 logs/monitor.log > recent_logs.txt

# Config validation
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))" > config_parsed.txt
```

### Create an Issue

Include:
1. What you were trying to do
2. What happened (error message)
3. Debug information (debug.log, recent_logs.txt)
4. Your OS and Python version

**GitHub Issues**: https://github.com/yourusername/bb-monitor/issues

---

## 💡 Prevention Tips

### Avoid Common Issues

**1. Always run from project root**:
```bash
cd /path/to/bb-monitor
./monitor.py --init
```

**2. Test after config changes**:
```bash
vim config.yaml
./monitor.py --init  # Test
```

**3. Keep tools updated**:
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

**4. Use absolute paths in cron**:
```cron
0 */6 * * * cd /full/path/to/bb-monitor && ./monitor.py --monitor
```

**5. Verify environment in cron**:
```cron
0 */6 * * * source ~/.bbmon_env && cd /path && ./monitor.py --monitor
```

---

## 📚 Additional Resources

### Troubleshooting Guides
- [PATH_TROUBLESHOOTING.md](PATH_TROUBLESHOOTING.md) - Complete path guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - General troubleshooting

### Configuration Help
- [Reference - CONFIGURATION.md](../04_Reference/CONFIGURATION.md) - All config options
- [Getting Started - CONFIG_QUICK_START.md](../01_Getting_Started/CONFIG_QUICK_START.md) - Quick fixes

### Community
- GitHub Issues - Report bugs
- GitHub Discussions - Ask questions
- GitHub Wiki - Community tips

---

[← Back to Main Documentation](../README.md)
