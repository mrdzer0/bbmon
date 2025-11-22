# Getting Started with BB-Monitor

Essential documentation to get you up and running quickly.

## 📚 Documents in This Section

### [USAGE.md](USAGE.md)
**Complete usage guide from installation to automation**

Learn how to:
- Install dependencies
- Configure your first target
- Run baseline scans
- Monitor for changes
- View dashboards
- Automate with cron

**Start here if**: You're new to BB-Monitor or want a complete overview

---

### [CONFIG_QUICK_START.md](CONFIG_QUICK_START.md)
**5-minute configuration guide**

Quick setup for:
- Basic configuration (no notifications)
- Slack notifications
- Discord notifications
- Telegram notifications
- Shodan integration
- Configuration profiles (fast/comprehensive/security-focused)

**Start here if**: You want to quickly configure notifications or Shodan

---

### [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
**Understanding the codebase architecture**

Learn about:
- Directory layout
- File descriptions
- Module architecture
- Data flow
- Key features by module
- Configuration hierarchy

**Start here if**: You want to understand how BB-Monitor is organized or contribute code

---

## 🚀 Recommended Learning Path

### For Complete Beginners

1. **Read**: [USAGE.md](USAGE.md) - Installation section
2. **Do**: Install dependencies with `./utils/install.sh`
3. **Read**: [USAGE.md](USAGE.md) - Basic operations section
4. **Do**: Create your first target and run `--init`
5. **Read**: [CONFIG_QUICK_START.md](CONFIG_QUICK_START.md)
6. **Do**: Configure Slack/Discord notifications
7. **Read**: [USAGE.md](USAGE.md) - Automation section
8. **Do**: Setup cron with `./utils/setup_cron.sh`

### For Quick Setup (Experienced Users)

1. **Read**: [CONFIG_QUICK_START.md](CONFIG_QUICK_START.md) - Profile 1 (Fast Daily Scans)
2. **Do**: Edit `config.yaml` with recommended settings
3. **Do**: Add targets to `targets.txt`
4. **Do**: Run `./monitor.py --init`
5. **Do**: Setup cron with `./utils/setup_cron.sh`

---

## 💡 Quick Tips

**Installing Go tools**:
```bash
./utils/install.sh
```

**First scan**:
```bash
echo "hackerone.com" >> targets.txt
./monitor.py --init
```

**View results**:
```bash
./modules/dashboard.py
```

**Setup notifications**:
```bash
# Edit config.yaml
vim config.yaml
# Enable Slack/Discord and add webhook URL
```

**Automate monitoring**:
```bash
./utils/setup_cron.sh
```

---

## 🔗 What's Next?

After completing the getting started guides:

- **Want to monitor multiple programs?** → [Tutorials - Multi-Program Setup](../02_Tutorials/MULTI_PROGRAM_SETUP.md)
- **Want to integrate Shodan?** → [Guides - Shodan Integration](../03_Guides/SHODAN_INTEGRATION.md)
- **Need detailed config reference?** → [Reference - Configuration](../04_Reference/CONFIGURATION.md)
- **Having issues?** → [Troubleshooting](../05_Troubleshooting/TROUBLESHOOTING.md)

---

## 📖 Related Documentation

- [Main Documentation Index](../README.md)
- [Tutorials](../02_Tutorials/)
- [Troubleshooting](../05_Troubleshooting/)
