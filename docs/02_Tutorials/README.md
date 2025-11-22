# Tutorials

Step-by-step guides with complete examples for specific use cases.

## 📚 Available Tutorials

### [MULTI_PROGRAM_SETUP.md](MULTI_PROGRAM_SETUP.md)
**Comprehensive guide for monitoring multiple bug bounty programs**

Learn how to:
- Monitor programs A, B, C with different configs
- Setup separate cron jobs per program
- Configure program-specific dashboards
- Setup alerts per program (different Slack channels, etc.)
- Handle different scan schedules (hourly vs daily vs weekly)
- Manage environment variables for secrets
- Use shared workspace vs separate installations

**Topics covered**:
- Directory structure options
- Configuration setup per program
- Target management
- Cron job setup with examples
- Dashboard monitoring
- Alert configuration
- Advanced scenarios (team collaboration, centralized storage, etc.)

**Best for**: Anyone monitoring 2+ bug bounty programs

---

### [MULTI_PROGRAM_EXAMPLE.md](MULTI_PROGRAM_EXAMPLE.md)
**Real-world complete walkthrough**

Complete example with 3 programs:
- **HackerOne**: High-value (scan every 4 hours, all alerts)
- **Bugcrowd**: Medium-value (scan every 8 hours, critical alerts)
- **Intigriti**: Low-priority (scan daily, digest only)

Includes:
- Full configuration files
- Environment variable setup
- Cron job examples
- Dashboard scripts
- Notification examples
- Daily workflow
- Directory structure after setup

**Best for**: Learning by example, copy-paste ready configurations

---

## 🎯 Which Tutorial Should I Follow?

### Choose MULTI_PROGRAM_SETUP.md if:
- You want to understand all the concepts
- You need flexibility for your specific use case
- You want to know all the options available
- You're setting up a custom workflow

### Choose MULTI_PROGRAM_EXAMPLE.md if:
- You want a ready-to-use example
- You want to see complete configurations
- You prefer learning by example
- You want to get started quickly

### Use Both if:
- You want complete understanding (read SETUP first)
- Then copy examples from EXAMPLE
- Best approach for production setups

---

## 🚀 Tutorial Path

### Step 1: Understand the Concepts
Read: [MULTI_PROGRAM_SETUP.md](MULTI_PROGRAM_SETUP.md) - Quick Start section

### Step 2: Choose Your Approach
- **Shared Workspace**: Single bb-monitor with multiple configs
- **Separate Installations**: Each program in its own directory

### Step 3: Follow the Example
Read: [MULTI_PROGRAM_EXAMPLE.md](MULTI_PROGRAM_EXAMPLE.md) - Step-by-step setup

### Step 4: Implement
- Copy configurations
- Adjust for your programs
- Test each program individually
- Setup cron jobs
- Monitor dashboards

---

## 💡 Quick Tips

**Setup multiple programs quickly**:
```bash
# Use the automated script
./utils/setup_program.sh -n hackerone
./utils/setup_program.sh -n bugcrowd
./utils/setup_program.sh -n intigriti
```

**View all program dashboards**:
```bash
# Create helper script from example
cat > view_all.sh << 'EOF'
for program in hackerone bugcrowd intigriti; do
    echo "=== $program ==="
    python3 modules/dashboard.py --data-dir ./data/$program
done
EOF
chmod +x view_all.sh
./view_all.sh
```

**Compare program statistics**:
```bash
# Use compare script from example
./compare_programs.sh
```

---

## 📊 Common Scenarios

### Scenario 1: Different Priorities
- High-value: Scan every 4 hours, instant alerts
- Medium-value: Scan every 8 hours, critical alerts
- Low-priority: Scan daily, digest only

**Solution**: [MULTI_PROGRAM_SETUP.md - Advanced Scenarios](MULTI_PROGRAM_SETUP.md#scenario-1-different-scan-schedules)

### Scenario 2: Team Collaboration
- Multiple people monitoring different programs
- Separate logs per person/program
- Shared data storage

**Solution**: [MULTI_PROGRAM_SETUP.md - Scenario 4](MULTI_PROGRAM_SETUP.md#scenario-4-team-collaboration)

### Scenario 3: Different Tool Configurations
- Fast scans for some programs
- Comprehensive scans for others
- Different Shodan usage

**Solution**: [MULTI_PROGRAM_SETUP.md - Scenario 2](MULTI_PROGRAM_SETUP.md#scenario-2-program-specific-tool-configurations)

---

## 🔗 Related Documentation

### Before Starting Tutorials
- [Getting Started - USAGE.md](../01_Getting_Started/USAGE.md) - Learn basics first
- [Getting Started - CONFIG_QUICK_START.md](../01_Getting_Started/CONFIG_QUICK_START.md) - Understand config

### While Following Tutorials
- [Reference - CONFIGURATION.md](../04_Reference/CONFIGURATION.md) - Config options
- [Troubleshooting](../05_Troubleshooting/TROUBLESHOOTING.md) - If you hit issues

### After Completing Tutorials
- [Guides - SHODAN_INTEGRATION.md](../03_Guides/SHODAN_INTEGRATION.md) - Add Shodan to your programs
- [Troubleshooting - PATH_TROUBLESHOOTING.md](../05_Troubleshooting/PATH_TROUBLESHOOTING.md) - Path issues

---

## 🎓 Learning Objectives

After completing these tutorials, you will be able to:

✅ Monitor multiple bug bounty programs independently
✅ Configure different scan schedules per program
✅ Setup program-specific alerts and notifications
✅ Manage separate dashboards for each program
✅ Automate monitoring with cron jobs
✅ Handle environment variables securely
✅ Troubleshoot multi-program setups
✅ Scale your monitoring infrastructure

---

## 📞 Need Help?

**Configuration questions?**
→ [Reference - CONFIGURATION.md](../04_Reference/CONFIGURATION.md)

**Errors during setup?**
→ [Troubleshooting](../05_Troubleshooting/TROUBLESHOOTING.md)

**Path/directory issues?**
→ [Troubleshooting - PATH_TROUBLESHOOTING.md](../05_Troubleshooting/PATH_TROUBLESHOOTING.md)

---

[← Back to Main Documentation](../README.md)
