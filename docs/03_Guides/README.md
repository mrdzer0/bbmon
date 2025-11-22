# Guides

In-depth documentation for specific features and integrations.

## 📚 Available Guides

### [SHODAN_INTEGRATION.md](SHODAN_INTEGRATION.md)
**Complete guide for Shodan API integration**

Learn how to:
- Setup Shodan API key
- Configure Shodan scanning
- Use DNS resolution features
- Identify vulnerabilities automatically
- Detect exposed services (databases, RDP, etc.)
- Integrate with monitoring workflow
- Manage API credits efficiently

**Features covered**:
- Asset discovery (IP lookups, domain search)
- Security intelligence (CVEs, open ports, services)
- Enrichment data (organization, geolocation, ISP)
- High-value finding detection
- Results storage and reporting
- Best practices and troubleshooting

**Best for**:
- Adding Shodan intelligence to your recon
- Finding exposed services and vulnerabilities
- Enriching subdomain data with network information

---

### [WAYBACK_INTEGRATION.md](WAYBACK_INTEGRATION.md)
**Complete guide for Wayback Machine URL discovery**

Learn how to:
- Fetch historical URLs from archive.org
- Automatically classify URLs by file type
- Discover backup and configuration files
- Find exposed credentials and keys
- Detect version control exposure (.git, .svn)
- Export high-value categories
- Integrate with monitoring workflow

**Features covered**:
- 10+ file type categories (backup, database, config, credentials, etc.)
- Priority-based scoring system
- Parameter analysis and extraction
- Automatic export of sensitive categories
- No API key required
- Integration with baseline and monitoring
- Standalone usage examples

**Best for**:
- Discovering old backup files that may still be accessible
- Finding exposed configuration files (.env, .yml, .config)
- Identifying version control exposure
- Locating sensitive documents and credentials
- Historical attack surface analysis

---

## 🎯 When to Use These Guides

### Use SHODAN_INTEGRATION.md when:
- You want to add vulnerability intelligence
- You need to identify exposed databases/services
- You want network-level reconnaissance
- You have a Shodan API key
- You want to find CVEs affecting your targets

### Use WAYBACK_INTEGRATION.md when:
- You want to discover historical URLs
- You're looking for old backup/config files
- You need to find exposed credentials or keys
- You want to check for .git exposure
- You're doing historical attack surface analysis
- You want free URL discovery (no API key needed)

---

## 🚀 Quick Start

### Shodan Integration Quick Setup

1. **Get API key**: https://account.shodan.io/
2. **Configure**:
   ```yaml
   tools:
     shodan:
       enabled: true
       api_key: "YOUR_API_KEY"
       scan_on:
         - baseline_init
   ```
3. **Set environment variable** (recommended):
   ```bash
   export BB_SHODAN_API_KEY="your_api_key"
   ```
4. **Run scan**:
   ```bash
   ./monitor.py --init
   ```

### Wayback Integration Quick Setup

1. **Configure** (no API key needed):
   ```yaml
   tools:
     wayback:
       enabled: true
       max_results: 10000
       scan_on:
         - baseline_init
       export_categories:
         - backup
         - database
         - config
         - credentials
   ```
2. **Run scan**:
   ```bash
   ./monitor.py --init
   ```
3. **Or use standalone**:
   ```bash
   python3 modules/wayback_analyzer.py example.com
   ```

---

## 💡 Integration Tips

**Shodan + Multi-Program**:
```yaml
# High-value program - scan everything
tools:
  shodan:
    scan_on:
      - baseline_init
      - new_subdomain

# Low-priority - scan baseline only
tools:
  shodan:
    scan_on:
      - baseline_init
```

**Shodan Standalone**:
```bash
# Use directly without monitoring
python3 modules/shodan_scanner.py API_KEY example.com
```

**Wayback + Shodan**:
```yaml
# Combine both for comprehensive recon
tools:
  shodan:
    enabled: true
    scan_on:
      - baseline_init
  wayback:
    enabled: true
    scan_on:
      - baseline_init
```

**Wayback + HTTP Probing**:
```bash
# Get historical URLs
python3 modules/wayback_analyzer.py example.com --export-all urls.txt

# Test if still accessible
cat urls.txt | httpx -silent -status-code
```

---

## 📊 Common Use Cases

### Shodan Use Cases

#### Use Case 1: Find Exposed Databases
Shodan automatically flags:
- MongoDB (27017)
- Redis (6379)
- Elasticsearch (9200)
- MySQL (3306)
- PostgreSQL (5432)

**Guide section**: [High-Value Findings](SHODAN_INTEGRATION.md#high-value-findings)

#### Use Case 2: Identify Vulnerable Versions
Detect outdated software with known CVEs:
- Apache 2.4.49 (CVE-2021-41773)
- Old nginx versions
- Outdated SSH/OpenSSH

**Guide section**: [Security Intelligence](SHODAN_INTEGRATION.md#features)

#### Use Case 3: Network Reconnaissance
Get comprehensive network data:
- Open ports and services
- Organization and ISP
- Geolocation
- SSL certificates

**Guide section**: [Asset Discovery](SHODAN_INTEGRATION.md#features)

### Wayback Use Cases

#### Use Case 4: Discover Backup Files
Find old backups that may still be accessible:
- `.bak`, `.old`, `.backup` files
- `.sql` database dumps
- `.tar.gz`, `.zip` archives

**Guide section**: [High-Value Categories](WAYBACK_INTEGRATION.md#high-value-categories)

#### Use Case 5: Find Configuration Files
Locate exposed configs with secrets:
- `.env` environment files
- `.yml`, `.yaml` config files
- `.ini`, `.properties` settings

**Guide section**: [URL Classification](WAYBACK_INTEGRATION.md#url-classification)

#### Use Case 6: Version Control Exposure
Check for exposed repositories:
- `.git/config` files
- `.svn/entries`
- Full source code disclosure

**Guide section**: [Critical Findings](WAYBACK_INTEGRATION.md#critical-findings)

---

## 🔗 Related Documentation

### Before Reading Guides
- [Getting Started - USAGE.md](../01_Getting_Started/USAGE.md) - Basic monitoring setup
- [Getting Started - CONFIG_QUICK_START.md](../01_Getting_Started/CONFIG_QUICK_START.md) - Config basics

### While Using Guides
- [Reference - CONFIGURATION.md](../04_Reference/CONFIGURATION.md) - Full config reference
- [Tutorials - MULTI_PROGRAM_SETUP.md](../02_Tutorials/MULTI_PROGRAM_SETUP.md) - Apply to multiple programs

### If Issues Occur
- [Troubleshooting](../05_Troubleshooting/TROUBLESHOOTING.md) - General issues
- [SHODAN_INTEGRATION.md - Troubleshooting](SHODAN_INTEGRATION.md#troubleshooting) - Shodan-specific

---

## 📈 Benefits by Feature

| Feature | Benefit | Guide Section |
|---------|---------|---------------|
| IP Lookup | Find open ports, services | [Usage](SHODAN_INTEGRATION.md#usage) |
| Domain Search | Discover all hosts | [Usage](SHODAN_INTEGRATION.md#usage) |
| CVE Detection | Find vulnerabilities | [Features](SHODAN_INTEGRATION.md#security-intelligence) |
| DNS Resolution | Resolve subdomains | [Usage](SHODAN_INTEGRATION.md#usage) |
| Service Detection | Identify tech stack | [Output Data](SHODAN_INTEGRATION.md#output-data) |

---

## 🎓 Learning Path

### For Beginners
1. Read: [SHODAN_INTEGRATION.md - Overview](SHODAN_INTEGRATION.md#overview)
2. Read: [SHODAN_INTEGRATION.md - Setup](SHODAN_INTEGRATION.md#setup)
3. Do: Get API key and configure
4. Do: Run test scan
5. Read: [SHODAN_INTEGRATION.md - Usage](SHODAN_INTEGRATION.md#usage)

### For Advanced Users
1. Read: [SHODAN_INTEGRATION.md - Advanced Usage](SHODAN_INTEGRATION.md#advanced-usage)
2. Read: [SHODAN_INTEGRATION.md - Best Practices](SHODAN_INTEGRATION.md#best-practices)
3. Read: [SHODAN_INTEGRATION.md - Integration with Other Tools](SHODAN_INTEGRATION.md#integration-with-other-tools)

---

## 💰 API Credit Management

**Free Plan**: 100 credits/month
- Good for: Small programs, testing
- Strategy: Scan baseline only

**Membership** ($59/month): Unlimited
- Good for: Active hunting, multiple programs
- Strategy: Scan baseline + new subdomains

**Tips**:
```yaml
# Conserve credits
tools:
  shodan:
    scan_on:
      - baseline_init  # Only baseline, not every new subdomain

# Use fully
tools:
  shodan:
    scan_on:
      - baseline_init
      - new_subdomain  # Scan everything
```

---

## 🔍 Quick Reference

**Shodan website**: https://www.shodan.io/
**API docs**: https://developer.shodan.io/api
**Get API key**: https://account.shodan.io/
**Search filters**: https://www.shodan.io/search/filters

---

## 📞 Need Help?

**Shodan API errors?**
→ [SHODAN_INTEGRATION.md - Troubleshooting](SHODAN_INTEGRATION.md#troubleshooting)

**Configuration issues?**
→ [Reference - CONFIGURATION.md](../04_Reference/CONFIGURATION.md)

**General problems?**
→ [Troubleshooting](../05_Troubleshooting/TROUBLESHOOTING.md)

---

[← Back to Main Documentation](../README.md)
