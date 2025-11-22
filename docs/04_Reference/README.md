# Reference Documentation

Technical specifications, complete references, and detailed technical information.

## 📚 Available References

### [CONFIGURATION.md](CONFIGURATION.md)
**Complete configuration reference**

Comprehensive documentation for all configuration options:

**Sections**:
- Target configuration (domains, files, wildcards)
- Monitoring settings (schedules, retention, directories)
- Checks configuration (infrastructure, web app, content discovery)
- Diff detection settings (thresholds, noise filtering)
- Notification settings (Slack, Discord, Telegram, Email)
- Priority configuration (high/medium/low alerts)
- Tool configuration (subfinder, amass, httpx, dnsx, etc.)
- Advanced options (workers, rate limits, screenshots)

**Best for**:
- Looking up specific config options
- Understanding all available settings
- Fine-tuning performance
- Customizing behavior

---

### [CHANGELOG_TEMP_FILES.md](CHANGELOG_TEMP_FILES.md)
**Technical documentation about temporary file management**

Detailed explanation of how temp files are handled:

**Topics**:
- Problem that was fixed (file collisions)
- Solution implemented (temp directories)
- Code changes and why
- Benefits of the new system
- File lifecycle (temp vs permanent)
- Examples and use cases
- Migration guide
- Technical details

**Best for**:
- Understanding internal architecture
- Troubleshooting file issues
- Contributing to codebase
- Understanding how tools interact

---

## 📖 How to Use This Section

### For Quick Lookups
Use CONFIGURATION.md as a reference:
1. Find the section you need (use Table of Contents)
2. Look up the specific option
3. Copy the example
4. Apply to your config.yaml

### For Understanding Architecture
Use CHANGELOG_TEMP_FILES.md:
1. Understand the design decisions
2. See before/after code examples
3. Learn about file lifecycle
4. Understand why changes were made

---

## 🎯 Common Lookups

### Configuration Options

**Enable/disable tools**:
→ [CONFIGURATION.md - Tools Configuration](CONFIGURATION.md#tools-configuration)

**Setup notifications**:
→ [CONFIGURATION.md - Notifications](CONFIGURATION.md#notifications)

**Adjust performance**:
→ [CONFIGURATION.md - Advanced Options](CONFIGURATION.md#advanced-options)

**Filter noise**:
→ [CONFIGURATION.md - Diff Detection](CONFIGURATION.md#diff-detection-settings)

**Set priorities**:
→ [CONFIGURATION.md - Priority Configuration](CONFIGURATION.md#priority-configuration)

### Technical Details

**How temp files work**:
→ [CHANGELOG_TEMP_FILES.md - Solution Implemented](CHANGELOG_TEMP_FILES.md#solution-implemented)

**What files are temporary**:
→ [CHANGELOG_TEMP_FILES.md - File Lifecycle](CHANGELOG_TEMP_FILES.md#file-lifecycle)

**File collision prevention**:
→ [CHANGELOG_TEMP_FILES.md - Benefits](CHANGELOG_TEMP_FILES.md#benefits)

---

## 💡 Configuration Examples

### Quick Copy-Paste Configs

**Fast Daily Scans**:
```yaml
tools:
  amass:
    enabled: false
  katana:
    enabled: false
advanced:
  max_workers: 20
diff_settings:
  min_change_percent: 10
```

**Comprehensive Weekly Scans**:
```yaml
tools:
  amass:
    enabled: true
  katana:
    enabled: true
advanced:
  max_workers: 5
diff_settings:
  min_change_percent: 0
```

**Security-Focused**:
```yaml
tools:
  nuclei:
    enabled: true
  shodan:
    enabled: true
notifications:
  slack:
    notify_on:
      - subdomain_takeover
      - high_value_target
      - new_vulnerability
```

More examples in: [CONFIGURATION.md](CONFIGURATION.md)

---

## 📊 Configuration Reference Quick Links

### Core Settings
- [Targets](CONFIGURATION.md#target-configuration) - What to monitor
- [Monitoring](CONFIGURATION.md#monitoring-settings) - When and where
- [Checks](CONFIGURATION.md#checks-configuration) - What to check

### Detection & Alerts
- [Diff Settings](CONFIGURATION.md#diff-detection-settings) - Change detection rules
- [Notifications](CONFIGURATION.md#notifications) - Where to send alerts
- [Priority](CONFIGURATION.md#priority-configuration) - Alert importance

### Tools & Performance
- [Tools](CONFIGURATION.md#tools-configuration) - External tool settings
- [Advanced](CONFIGURATION.md#advanced-options) - Performance tuning

---

## 🔍 Search by Option Name

### Common Config Keys

| Option | Section | Purpose |
|--------|---------|---------|
| `domains_file` | Targets | Target list file |
| `data_dir` | Monitoring | Data storage location |
| `retention_days` | Monitoring | How long to keep data |
| `min_change_percent` | Diff Settings | Change threshold |
| `webhook_url` | Notifications | Slack/Discord webhook |
| `enabled` | Tools/Notifications | Enable/disable feature |
| `max_workers` | Advanced | Parallel workers |
| `rate_limit` | Advanced | Requests per second |

Full list: [CONFIGURATION.md](CONFIGURATION.md)

---

## 🔗 Related Documentation

### Before Using Reference
- [Getting Started - CONFIG_QUICK_START.md](../01_Getting_Started/CONFIG_QUICK_START.md) - Quick config setup

### While Using Reference
- [Getting Started - USAGE.md](../01_Getting_Started/USAGE.md) - How to apply configs
- [Tutorials - MULTI_PROGRAM_SETUP.md](../02_Tutorials/MULTI_PROGRAM_SETUP.md) - Config examples

### If Issues Occur
- [Troubleshooting](../05_Troubleshooting/TROUBLESHOOTING.md) - Config problems
- [Troubleshooting - PATH_TROUBLESHOOTING.md](../05_Troubleshooting/PATH_TROUBLESHOOTING.md) - Path issues

---

## 📝 Configuration Best Practices

### 1. Start with Defaults
```bash
cp config.yaml.example config.yaml
# Edit only what you need
```

### 2. Use Environment Variables for Secrets
```bash
export BB_SLACK_WEBHOOK="..."
export BB_SHODAN_API_KEY="..."
```

```yaml
notifications:
  slack:
    webhook_url: "${BB_SLACK_WEBHOOK}"
```

### 3. Comment Your Changes
```yaml
tools:
  amass:
    enabled: false  # Disabled for daily scans, enable weekly
```

### 4. Version Control Your Config
```bash
git add config.yaml
git commit -m "Updated notification settings"
```

### 5. Test After Changes
```bash
./monitor.py --init  # Test new config
```

---

## 🎓 Understanding Config Hierarchy

```
config.yaml
├── targets           # What to monitor
├── monitoring        # When/where to monitor
├── checks            # What to check
│   ├── infrastructure
│   ├── web_application
│   ├── content_discovery
│   └── attack_surface
├── diff_settings     # Change detection rules
├── notifications     # Where to alert
│   ├── slack
│   ├── discord
│   ├── telegram
│   └── email
├── priority          # Alert importance
├── tools             # External tools
│   ├── subfinder
│   ├── amass
│   ├── httpx
│   ├── dnsx
│   ├── katana
│   ├── nuclei
│   └── shodan
└── advanced          # Performance tuning
```

Detailed hierarchy: [CONFIGURATION.md](CONFIGURATION.md)

---

## 📞 Need Help?

**Config option not working?**
→ Verify YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"`

**Path issues?**
→ [Troubleshooting - PATH_TROUBLESHOOTING.md](../05_Troubleshooting/PATH_TROUBLESHOOTING.md)

**General config questions?**
→ [Getting Started - CONFIG_QUICK_START.md](../01_Getting_Started/CONFIG_QUICK_START.md)

---

[← Back to Main Documentation](../README.md)
