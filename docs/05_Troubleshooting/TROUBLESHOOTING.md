# Troubleshooting Guide

Common issues and solutions for Bug Bounty Monitoring Framework.

## Table of Contents

- [Path & Directory Issues](#path--directory-issues)
- [Installation Issues](#installation-issues)
- [Tool-Specific Problems](#tool-specific-problems)
- [Performance Issues](#performance-issues)
- [Detection Issues](#detection-issues)
- [Notification Problems](#notification-problems)
- [Data Issues](#data-issues)

## Path & Directory Issues

### File or Directory Not Found

**Problem**: Scripts can't find modules, config files, or data directories

**Solution**: See [PATH_TROUBLESHOOTING.md](PATH_TROUBLESHOOTING.md) for comprehensive path troubleshooting guide.

Quick fixes:
```bash
# Always run from project root
cd /path/to/bb-monitor

# Test path configuration
./utils/test_paths.sh

# Create missing directories
mkdir -p data/{baseline,diffs,subdomain_scans,shodan_scans}
mkdir -p reports logs
```

### Script Path Issues

**Problem**: `can't open file './utils/subdomain_finder.py': No such file or directory`

**Solution**: Updated to correct paths. All utility scripts now properly reference `modules/` directory:
```bash
# This now works correctly
./utils/subdomain_scan.sh -d example.com
```

If still having issues, ensure you're on the latest version and paths are correct.

## Installation Issues

### Python Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'requests'`

**Solution**:
```bash
# Install requirements
pip3 install -r requirements.txt

# Or install individually
pip3 install requests beautifulsoup4 pyyaml
```

### Go Tools Not Found

**Problem**: `command not found: subfinder`

**Solution**:
```bash
# Check Go installation
go version

# Install tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Add to PATH
export PATH=$PATH:~/go/bin
echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc
```

### Permission Denied

**Problem**: `Permission denied: ./monitor.py`

**Solution**:
```bash
chmod +x monitor.py
chmod +x modules/*.py
chmod +x utils/*.sh
```

## Tool-Specific Problems

### Subfinder: No Results

**Problem**: Subfinder returns 0 subdomains

**Solutions**:
1. **Check internet connection**:
   ```bash
   curl -I https://crt.sh
   ```

2. **Update subfinder**:
   ```bash
   go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
   ```

3. **Test manually**:
   ```bash
   subfinder -d example.com -v
   ```

4. **Configure API keys** (optional but recommended):
   ```bash
   # Create config
   mkdir -p ~/.config/subfinder
   nano ~/.config/subfinder/provider-config.yaml
   ```

   Add API keys:
   ```yaml
   virustotal:
     - YOUR_API_KEY
   securitytrails:
     - YOUR_API_KEY
   ```

### HTTPx: Connection Timeouts

**Problem**: Many timeouts during HTTP probing

**Solutions**:
1. **Increase timeout in config**:
   ```yaml
   tools:
     httpx:
       timeout: 30  # Increase from 10
   ```

2. **Reduce parallelism**:
   ```yaml
   tools:
     httpx:
       threads: 20  # Reduce from 50
   ```

3. **Check network**:
   ```bash
   # Test single URL
   httpx -u https://example.com -v
   ```

### DNSx: Resolution Failures

**Problem**: DNS resolution failing

**Solutions**:
1. **Check DNS configuration**:
   ```bash
   cat /etc/resolv.conf
   ```

2. **Use custom resolvers**:
   ```bash
   echo "8.8.8.8" > resolvers.txt
   echo "1.1.1.1" >> resolvers.txt
   dnsx -l domains.txt -r resolvers.txt
   ```

3. **Increase timeout**:
   ```bash
   dnsx -l domains.txt -retry 3 -timeout 10
   ```

## Performance Issues

### High Memory Usage

**Problem**: Script using too much RAM

**Solutions**:
1. **Reduce workers**:
   ```yaml
   advanced:
     max_workers: 5  # Reduce from 10
   ```

2. **Process targets sequentially**:
   ```bash
   # Process one domain at a time
   for domain in $(cat targets.txt); do
       echo "$domain" | ./monitor.py --init
   done
   ```

3. **Enable pagination for large datasets**:
   Edit modules to process in batches

### Slow Execution

**Problem**: Scans taking too long

**Solutions**:
1. **Disable slow tools**:
   ```yaml
   tools:
     amass:
       enabled: false  # Very slow
     katana:
       enabled: false  # Slow crawling
   ```

2. **Reduce crawl depth**:
   ```yaml
   tools:
     katana:
       depth: 2  # Reduce from 3
   ```

3. **Use quick mode**:
   ```bash
   ./utils/subdomain_scan.sh -d example.com -q
   ```

### Rate Limiting

**Problem**: Getting rate limited by target

**Solutions**:
1. **Reduce request rate**:
   ```yaml
   advanced:
     rate_limit: 5  # Requests per second
   ```

2. **Add delays**:
   ```python
   # In http_monitor.py
   import time
   time.sleep(1)  # 1 second delay between requests
   ```

3. **Use proxy rotation**:
   ```bash
   # Configure proxy in requests
   export HTTP_PROXY="http://proxy:port"
   export HTTPS_PROXY="https://proxy:port"
   ```

## Detection Issues

### No Changes Detected

**Problem**: Monitor runs but reports no changes

**Solutions**:
1. **Check threshold**:
   ```yaml
   diff_settings:
     min_change_percent: 0  # Detect all changes
   ```

2. **Verify baseline exists**:
   ```bash
   ls -la data/baseline/
   ```

3. **Force re-baseline**:
   ```bash
   rm data/baseline/target_baseline.json
   ./monitor.py --init
   ```

### False Positives

**Problem**: Too many irrelevant changes detected

**Solutions**:
1. **Increase threshold**:
   ```yaml
   diff_settings:
     min_change_percent: 10  # Ignore <10% changes
   ```

2. **Add noise filters**:
   ```yaml
   diff_settings:
     filter_noise:
       - "timestamp"
       - "nonce"
       - "csrf"
   ```

3. **Ignore dynamic content**:
   ```yaml
   diff_settings:
     ignore_dynamic_content: true
   ```

### Missing High-Value Targets

**Problem**: Admin panels not being flagged

**Solutions**:
1. **Check keywords** in `modules/http_monitor.py`:
   ```python
   self.high_value_keywords = {
       'admin': ['admin', 'administrator', 'dashboard'],
       # Add more keywords
   }
   ```

2. **Verify flags are enabled**:
   ```yaml
   checks:
     attack_surface:
       enabled: true
   ```

3. **Test manually**:
   ```bash
   ./modules/http_monitor.py -u https://target.com/admin
   ```

## Notification Problems

### Slack Not Working

**Problem**: No Slack notifications received

**Solutions**:
1. **Verify webhook**:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"Test"}' \
        YOUR_WEBHOOK_URL
   ```

2. **Check configuration**:
   ```yaml
   notifications:
     slack:
       enabled: true  # Must be true
       webhook_url: "https://hooks.slack.com/..."
   ```

3. **Test from script**:
   ```python
   from modules.notifier import Notifier
   notifier = Notifier(config)
   notifier.send_slack("Test", {})
   ```

### Discord Not Working

**Problem**: Discord notifications failing

**Solutions**:
1. **Verify webhook format**:
   ```
   https://discord.com/api/webhooks/ID/TOKEN
   ```

2. **Check rate limits**:
   Discord has strict rate limits. Add delays between messages.

3. **Test manually**:
   ```bash
   curl -H "Content-Type: application/json" \
        -d '{"content":"Test"}' \
        YOUR_DISCORD_WEBHOOK
   ```

### Email Not Sending

**Problem**: Email notifications not working

**Solutions**:
1. **Use app password** (not regular password):
   - Gmail: https://myaccount.google.com/apppasswords
   - Outlook: Use app-specific password

2. **Check SMTP settings**:
   ```yaml
   notifications:
     email:
       smtp_server: "smtp.gmail.com"
       smtp_port: 587  # TLS
       # OR
       smtp_port: 465  # SSL
   ```

3. **Test connection**:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('email', 'app_password')
   ```

## Data Issues

### Corrupted Baseline

**Problem**: JSON decode error when loading baseline

**Solutions**:
1. **Validate JSON**:
   ```bash
   cat data/baseline/target_baseline.json | jq .
   ```

2. **Restore from backup**:
   ```bash
   cp data/baseline/target_baseline.json.bak \
      data/baseline/target_baseline.json
   ```

3. **Re-collect baseline**:
   ```bash
   rm data/baseline/target_baseline.json
   ./monitor.py --init
   ```

### Disk Space Issues

**Problem**: No space left on device

**Solutions**:
1. **Clean old data**:
   ```bash
   # Remove diffs older than 30 days
   find data/diffs/ -name "*.json" -mtime +30 -delete
   ```

2. **Reduce retention**:
   ```yaml
   monitoring:
     retention_days: 15  # Reduce from 30
   ```

3. **Archive data**:
   ```bash
   tar -czf archive_$(date +%Y%m%d).tar.gz data/
   mv archive_*.tar.gz /backup/
   ```

### Permission Errors

**Problem**: Cannot write to data directory

**Solutions**:
```bash
# Fix permissions
chmod -R 755 data/
chown -R $USER:$USER data/

# Or specify different directory
mkdir ~/bb-monitor-data
# Update config.yaml with new path
```

## Module Import Errors

### Cannot Import Modules

**Problem**: `ImportError: cannot import name 'SubdomainFinder'`

**Solutions**:
1. **Check directory structure**:
   ```bash
   ls -la modules/
   # Should have __init__.py
   ```

2. **Verify Python path**:
   ```python
   import sys
   print(sys.path)
   ```

3. **Run from correct directory**:
   ```bash
   cd /path/to/bb-monitor
   ./monitor.py --init
   ```

## Getting Help

If you're still having issues:

1. **Check logs**:
   ```bash
   tail -100 logs/monitor.log
   ```

2. **Run in verbose mode**:
   ```bash
   ./monitor.py --init -v  # If verbose flag exists
   ```

3. **Test components individually**:
   ```bash
   # Test subdomain finder
   ./modules/subdomain_finder.py -d example.com

   # Test HTTP monitor
   ./modules/http_monitor.py -u https://example.com
   ```

4. **Check dependencies**:
   ```bash
   pip3 list | grep -E 'requests|beautifulsoup4|pyyaml'
   which subfinder httpx dnsx
   ```

5. **Open GitHub Issue**:
   - Include error message
   - Include config (remove sensitive data)
   - Include steps to reproduce

---

For more information, see:
- [Usage Guide](USAGE.md)
- [Configuration Guide](CONFIGURATION.md)
- [Main README](../README.md)
