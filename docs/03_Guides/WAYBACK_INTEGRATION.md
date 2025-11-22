# Wayback Machine Integration Guide

Complete guide for using Wayback Machine to discover historical URLs and classify them by file type.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
  - [Standalone Usage](#standalone-usage)
  - [Integrated with Monitor](#integrated-with-monitor)
- [URL Classification](#url-classification)
- [High-Value Categories](#high-value-categories)
- [Output Data](#output-data)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Wayback Machine integration fetches historical URLs from archive.org's CDX API and automatically classifies them by file type, helping you discover:

- 🗄️ **Backup files** - Old backups that might still be accessible
- 💾 **Database files** - SQL dumps, database exports
- ⚙️ **Configuration files** - .env, .yml, .config files
- 🔑 **Credentials** - Keys, certificates, password files
- 📝 **Version control** - Exposed .git, .svn directories
- 📄 **Documents** - PDFs, spreadsheets, presentations
- 🔧 **Source code** - PHP, ASP, JSP files
- 📊 **API documentation** - Swagger, OpenAPI specs
- 📋 **Logs** - Error logs, debug files

## Features

### URL Discovery
- **Historical Coverage**: Access years of archived URLs
- **Deduplication**: Automatic removal of duplicate URLs
- **Large Scale**: Fetch up to 10,000+ URLs per domain
- **No API Key**: Free access to Wayback CDX API

### Classification System
- **10+ Categories**: Automatically categorize by file type
- **Priority Scoring**: Critical, high, medium, low priorities
- **Smart Detection**: Extension + keyword-based classification
- **Parameter Analysis**: Extracts and flags interesting parameters

### Integration
- **Baseline Scanning**: Run during initial reconnaissance
- **Continuous Monitoring**: Scan new subdomains
- **Auto-Export**: Save high-value categories to separate files
- **Notifications**: Alert on sensitive file discoveries

---

## Setup

### 1. Enable Wayback in Config

Edit `config.yaml`:

```yaml
tools:
  wayback:
    enabled: true              # Enable Wayback analysis
    max_results: 10000         # Max URLs to fetch per domain
    timeout: 30                # API timeout in seconds
    rate_limit_delay: 1        # Delay between requests
    scan_on:
      - new_subdomain          # Scan newly discovered subdomains
      - baseline_init          # Scan during baseline collection
    classify_urls: true        # Enable URL classification
    export_categories:         # Auto-export these categories
      - backup
      - database
      - config
      - credentials
      - version_control
    min_score: 20              # Only save URLs with score >= 20
```

### 2. Enable Content Discovery

Ensure content discovery is enabled:

```yaml
checks:
  content_discovery:
    enabled: true
    wayback_urls: true         # Enable Wayback URL discovery
```

### 3. Configure Notifications (Optional)

Get alerts for sensitive files:

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "YOUR_WEBHOOK"
    notify_on:
      - wayback_sensitive_files
      - wayback_credentials
      - wayback_version_control

priority:
  high:
    - wayback_sensitive_files
    - wayback_credentials
    - wayback_version_control
```

---

## Usage

### Standalone Usage

Run Wayback analyzer independently:

```bash
# Basic analysis
python3 modules/wayback_analyzer.py example.com

# Save results to specific file
python3 modules/wayback_analyzer.py example.com -o results.json

# Export specific category
python3 modules/wayback_analyzer.py example.com -c backup

# Export all URLs to text file
python3 modules/wayback_analyzer.py example.com --export-all all_urls.txt

# Limit results
python3 modules/wayback_analyzer.py example.com -m 5000
```

### Integrated with Monitor

#### Baseline Collection

Wayback runs automatically during baseline:

```bash
./monitor.py --init
```

Output:
```
[*] Running Wayback Machine analysis...
[*] Fetching URLs from Wayback Machine for example.com...
[+] Found 4,523 URLs from Wayback Machine
[*] Classifying 4,523 URLs...

============================================================
Wayback Analysis Summary: example.com
============================================================

[+] Total URLs: 4,523

[+] URLs by Category:
    backup                  23 URLs
    database                 8 URLs
    config                  15 URLs
    credentials              3 URLs
    documents              342 URLs
    source_code            156 URLs

[+] URLs by Priority:
    🔴 critical              3 URLs
    🟠 high                 46 URLs
    🟡 medium              498 URLs

[!!!] High-Value URLs Found: 49

    Top 10 High-Value URLs:
     1. [critical] http://example.com/.git/config
        Categories: version_control
        Score: 60

     2. [high    ] http://example.com/backup/db_backup.sql
        Categories: backup, database
        Score: 50

[+] Wayback analysis completed
```

#### Monitor New Subdomains

Configure to scan new subdomains:

```yaml
tools:
  wayback:
    scan_on:
      - new_subdomain    # Scan when new subdomains discovered
```

Then run monitoring:

```bash
./monitor.py --monitor
```

---

## URL Classification

### Category Definitions

#### 1. Backup Files (High Priority)
**Extensions**: `.bak`, `.backup`, `.old`, `.orig`, `.save`, `.swp`, `.tmp`, `.tar.gz`, `.zip`, `.rar`
**Keywords**: backup, old, copy, archive, dump

**Examples**:
- `http://example.com/config.php.bak`
- `http://example.com/backup/site_backup.tar.gz`
- `http://example.com/database_old.sql`

**Why Important**: May contain source code, credentials, or sensitive data

---

#### 2. Database Files (High Priority)
**Extensions**: `.sql`, `.db`, `.sqlite`, `.sqlite3`, `.mdb`, `.dump`
**Keywords**: database, dump, export, mysql, postgres, mongodb

**Examples**:
- `http://example.com/dump.sql`
- `http://example.com/exports/users.db`
- `http://example.com/backup/mysql_dump.sql`

**Why Important**: Direct access to database contents, user data

---

#### 3. Configuration Files (High Priority)
**Extensions**: `.conf`, `.config`, `.cfg`, `.ini`, `.env`, `.yml`, `.yaml`, `.properties`, `.xml`, `.json`
**Keywords**: config, configuration, settings, env, environment

**Examples**:
- `http://example.com/.env`
- `http://example.com/config/database.yml`
- `http://example.com/settings.ini`

**Why Important**: Contains API keys, database credentials, secrets

---

#### 4. Credentials (Critical Priority)
**Extensions**: `.key`, `.pem`, `.p12`, `.pfx`, `.jks`, `.keystore`, `.crt`
**Keywords**: password, passwd, pwd, credential, secret, key, token, auth, certificate, private

**Examples**:
- `http://example.com/private.key`
- `http://example.com/passwords.txt`
- `http://example.com/api_keys.json`

**Why Important**: Direct access credentials, private keys

---

#### 5. Version Control (Critical Priority)
**Extensions**: `.git`, `.svn`, `.hg`, `.bzr`
**Keywords**: git, svn, mercurial, .git/config

**Examples**:
- `http://example.com/.git/config`
- `http://example.com/.svn/entries`
- `http://example.com/.git/HEAD`

**Why Important**: Full source code disclosure, commit history

---

#### 6. Source Code (Medium Priority)
**Extensions**: `.php`, `.asp`, `.aspx`, `.jsp`, `.java`, `.py`, `.rb`, `.pl`, `.cgi`, `.sh`
**Keywords**: source, src, code

**Examples**:
- `http://example.com/admin.php`
- `http://example.com/upload.asp`

**Why Important**: Logic disclosure, vulnerability identification

---

#### 7. Documents (Medium Priority)
**Extensions**: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.txt`, `.csv`
**Keywords**: document, report, spreadsheet

**Examples**:
- `http://example.com/report_2023.pdf`
- `http://example.com/users.csv`

**Why Important**: Information disclosure, internal documents

---

#### 8. API Documentation (High Priority)
**Extensions**: `.wsdl`, `.wadl`, `.swagger`, `.openapi`
**Keywords**: api, swagger, openapi, graphql, rest

**Examples**:
- `http://example.com/api/swagger.json`
- `http://example.com/api-docs.yaml`

**Why Important**: API endpoint discovery, parameter identification

---

#### 9. Logs (Medium Priority)
**Extensions**: `.log`, `.logs`, `.out`, `.err`, `.trace`
**Keywords**: log, logs, error, debug, trace

**Examples**:
- `http://example.com/error.log`
- `http://example.com/debug/app.log`

**Why Important**: Error messages, stack traces, internal paths

---

#### 10. Sensitive Endpoints (High Priority)
**Keywords**: admin, dashboard, panel, console, phpmyadmin, upload, test, dev, staging

**Examples**:
- `http://example.com/admin/upload.php`
- `http://example.com/phpmyadmin/`
- `http://example.com/dev/test.php`

**Why Important**: Administrative access, testing endpoints

---

## High-Value Categories

### Critical Findings

Files that require immediate investigation:

| Category | Why Critical | What to Test |
|----------|--------------|--------------|
| **credentials** | Direct access to systems | Try credentials on login pages, APIs |
| **version_control** | Full source code access | Download `.git` repo, analyze code |

### High-Priority Findings

Files with significant security impact:

| Category | Impact | Testing Approach |
|----------|--------|------------------|
| **backup** | May contain credentials/source | Download and analyze contents |
| **database** | User data, credentials | Check if still accessible, analyze schema |
| **config** | API keys, secrets | Extract credentials, test validity |
| **api_docs** | API endpoint discovery | Test endpoints, check authentication |
| **sensitive** | Admin panels, upload points | Test authentication, authorization |

---

## Output Data

### JSON Structure

Results are saved to `data/wayback_scans/{domain}_{timestamp}.json`:

```json
{
  "domain": "example.com",
  "total_urls": 4523,
  "timestamp": "2024-01-15T10:30:00",
  "categorized": {
    "backup": [
      {
        "url": "http://example.com/config.bak",
        "categories": ["backup", "config"],
        "priority": "high",
        "file_extension": ".bak",
        "has_parameters": false,
        "parameter_names": [],
        "interesting_params": [],
        "score": 40
      }
    ],
    "credentials": [
      {
        "url": "http://example.com/private.key",
        "categories": ["credentials"],
        "priority": "critical",
        "file_extension": ".key",
        "score": 60
      }
    ]
  },
  "high_value": [
    {
      "url": "http://example.com/.git/config",
      "score": 60,
      "priority": "critical"
    }
  ],
  "statistics": {
    "by_category": {
      "backup": 23,
      "database": 8,
      "config": 15,
      "credentials": 3
    },
    "by_priority": {
      "critical": 3,
      "high": 46,
      "medium": 498,
      "low": 3976
    },
    "by_extension": {
      ".php": 856,
      ".jpg": 1234,
      ".js": 423,
      ".bak": 23
    },
    "top_parameters": {
      "id": 342,
      "file": 56,
      "page": 234
    },
    "with_parameters": 1245,
    "interesting_parameters": 127
  }
}
```

### Exported Category Files

High-value categories are auto-exported to text files:

```
data/wayback_scans/
├── example.com_20240115_103000.json       # Full results
├── example.com_backup_urls.txt            # Backup files only
├── example.com_database_urls.txt          # Database files
├── example.com_config_urls.txt            # Config files
├── example.com_credentials_urls.txt       # Credentials
└── example.com_version_control_urls.txt   # .git, .svn
```

**Example** (`example.com_backup_urls.txt`):
```
http://example.com/config.php.bak
http://example.com/backup/db_backup.sql
http://example.com/old/index.php.old
http://example.com/site_backup.tar.gz
```

---

## Advanced Usage

### Custom Category Export

Export specific categories:

```bash
# Analyze domain
python3 modules/wayback_analyzer.py example.com -o results.json

# Export backup files
python3 modules/wayback_analyzer.py example.com -c backup

# Export database files
python3 modules/wayback_analyzer.py example.com -c database
```

### Filter by Score

Configure minimum score threshold:

```yaml
tools:
  wayback:
    min_score: 20  # Only save URLs with score >= 20
```

Scoring system:
- **Categories**: +10 points per category match
- **Interesting parameters**: +5 points per parameter
- **Priority bonus**:
  - Critical: +50
  - High: +30
  - Medium: +10

### Parameter Analysis

Wayback analyzer extracts URL parameters:

**Interesting parameters flagged**:
- `id`, `user`, `username`, `email`
- `file`, `path`, `url`, `redirect`
- `debug`, `admin`, `token`, `api_key`
- `key`, `secret`, `password`
- `query`, `search`, `q`, `page`

**Example**:
```
URL: http://example.com/download.php?file=/etc/passwd&debug=1
Interesting params: file, debug
Score: +10 (2 interesting params × 5)
```

### Integration with HTTP Monitor

Use Wayback URLs as HTTP probe targets:

```bash
# 1. Fetch Wayback URLs
python3 modules/wayback_analyzer.py example.com --export-all wayback_urls.txt

# 2. Probe with HTTP monitor
python3 modules/http_monitor.py -l wayback_urls.txt -s current.json
```

### Multi-Subdomain Analysis

Analyze all discovered subdomains:

```bash
# Get subdomains from baseline
cat data/baseline/example.com_baseline.json | jq -r '.subdomains | keys[]' > subs.txt

# Analyze each
while read subdomain; do
    python3 modules/wayback_analyzer.py "$subdomain" -o "wayback_${subdomain}.json"
done < subs.txt
```

---

## Best Practices

### 1. Start with Baseline Scan

Always run during initial reconnaissance:

```yaml
tools:
  wayback:
    scan_on:
      - baseline_init  # Essential for initial discovery
```

### 2. Focus on High-Value Categories

Prioritize investigation:

1. **credentials** - Test immediately
2. **version_control** - Download and analyze
3. **backup** - Check accessibility
4. **database** - Test for SQL injection
5. **config** - Extract secrets

### 3. Test URL Accessibility

Not all Wayback URLs are still live:

```bash
# Get high-value URLs
cat data/wayback_scans/example.com_backup_urls.txt | \
    httpx -silent -status-code -title

# Or use built-in HTTP monitor
cat data/wayback_scans/example.com_backup_urls.txt | \
    python3 modules/http_monitor.py -l /dev/stdin
```

### 4. Combine with Other Tools

Chain Wayback with other discovery:

```bash
# 1. Wayback URLs
python3 modules/wayback_analyzer.py example.com --export-all wayback.txt

# 2. Subdomain enumeration
./utils/subdomain_scan.sh -d example.com

# 3. Crawling
cat wayback.txt | katana -depth 2

# 4. Content discovery
cat wayback.txt | grep -E "\.php|\.asp" | \
    gospider -S /dev/stdin
```

### 5. Regular Monitoring

Scan periodically for new archived URLs:

```bash
# Weekly cron job
0 0 * * 0 cd /path/to/bb-monitor && ./monitor.py --wayback-only
```

### 6. Export and Organize

Keep organized records:

```bash
# Create directory structure
mkdir -p wayback_results/{backup,database,config,credentials}

# Move categorized files
mv data/wayback_scans/*_backup_urls.txt wayback_results/backup/
mv data/wayback_scans/*_database_urls.txt wayback_results/database/
```

---

## Troubleshooting

### Issue 1: No URLs Found

**Symptoms**:
```
[!] No URLs found
```

**Causes & Solutions**:

1. **Domain not archived**
   - Check manually: https://web.archive.org/web/*/example.com
   - Try with `www.` prefix: `www.example.com`

2. **New domain**
   - Wayback takes time to index new sites
   - Try older subdomains instead

3. **API timeout**
   - Increase timeout in config:
     ```yaml
     wayback:
       timeout: 60  # Increase from 30
     ```

### Issue 2: Slow Fetching

**Symptoms**: Takes very long to fetch URLs

**Solutions**:

1. **Reduce max_results**:
   ```yaml
   wayback:
     max_results: 5000  # Reduce from 10000
   ```

2. **Use CDX filters** (advanced):
   ```python
   # In modules/wayback_analyzer.py
   filters = ['statuscode:200', 'mimetype:text/html']
   urls = analyzer.fetch_urls(domain, filters=filters)
   ```

3. **Rate limiting**:
   ```yaml
   wayback:
     rate_limit_delay: 2  # Increase delay
   ```

### Issue 3: Too Many URLs

**Symptoms**: Thousands of low-value URLs

**Solutions**:

1. **Increase minimum score**:
   ```yaml
   wayback:
     min_score: 30  # Only high-scoring URLs
   ```

2. **Export only high-value categories**:
   ```yaml
   wayback:
     export_categories:
       - credentials  # Only critical categories
       - version_control
   ```

3. **Filter by extension** (standalone):
   ```bash
   # Only backup files
   python3 modules/wayback_analyzer.py example.com | \
       grep -E '\.(bak|old|backup|sql)$'
   ```

### Issue 4: Classification Issues

**Symptoms**: URLs miscategorized

**Solutions**:

1. **Check file extension**:
   - Ensure URL has proper extension
   - Wayback sometimes archives dynamic URLs

2. **Review scoring**:
   ```python
   # Check classification
   from modules.wayback_analyzer import WaybackAnalyzer
   analyzer = WaybackAnalyzer()
   classification = analyzer.classify_url("http://example.com/test.bak")
   print(classification)
   ```

3. **Custom categories** (advanced):
   Edit `modules/wayback_analyzer.py` to add custom rules

### Issue 5: Export Fails

**Symptoms**: Category export errors

**Causes**:
- Invalid directory permissions
- Disk space issues

**Solutions**:

```bash
# Check permissions
ls -la data/wayback_scans/

# Create directory if missing
mkdir -p data/wayback_scans

# Check disk space
df -h
```

---

## Example Workflow

### Complete Wayback Analysis Workflow

```bash
# 1. Initial baseline with Wayback
./monitor.py --init

# 2. Review high-value findings
cat data/wayback_scans/example.com_*_credentials_urls.txt
cat data/wayback_scans/example.com_*_version_control_urls.txt
cat data/wayback_scans/example.com_*_backup_urls.txt

# 3. Test URL accessibility
cat data/wayback_scans/example.com_*_backup_urls.txt | httpx -silent

# 4. Download interesting files
wget -i data/wayback_scans/example.com_backup_urls.txt

# 5. Analyze results
ls -lh *.bak *.sql *.env

# 6. Test credentials found
# (manual testing)

# 7. Export report
python3 modules/wayback_analyzer.py example.com -o report.json
```

### Integration with Bug Bounty Workflow

```bash
# Day 1: Initial recon
./monitor.py --init  # Includes Wayback

# Day 2-7: Monitor changes
./monitor.py --monitor  # New subdomains get Wayback scanned

# Weekly: Deep dive
python3 modules/wayback_analyzer.py target.com -m 50000
```

---

## Related Documentation

- [Getting Started - USAGE.md](../01_Getting_Started/USAGE.md) - Basic usage
- [Configuration Reference](../04_Reference/CONFIGURATION.md) - All config options
- [Shodan Integration](SHODAN_INTEGRATION.md) - Combine with Shodan
- [Multi-Program Setup](../02_Tutorials/MULTI_PROGRAM_SETUP.md) - Scale to multiple programs

---

## Summary

Wayback Machine integration provides:

✅ **Historical URL discovery** - Access years of archived content
✅ **Automatic classification** - 10+ categories with priority scoring
✅ **Sensitive file detection** - Credentials, configs, backups
✅ **Seamless integration** - Works with baseline and monitoring
✅ **No API key required** - Free access to Wayback CDX API
✅ **Smart exports** - Auto-save high-value categories

**Best for**:
- Discovering old backup files
- Finding exposed configuration files
- Identifying version control exposure (.git)
- Locating sensitive documents
- API endpoint discovery
- Historical attack surface analysis

---

[← Back to Guides](README.md) | [← Back to Main Documentation](../README.md)
