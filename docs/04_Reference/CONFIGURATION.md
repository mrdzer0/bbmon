# Configuration Guide

Complete reference for `config.yaml` configuration options.

## Table of Contents

- [Target Configuration](#target-configuration)
- [Monitoring Settings](#monitoring-settings)
- [Check Configuration](#check-configuration)
- [Tool Settings](#tool-settings)
- [Notification Settings](#notification-settings)
- [Priority Configuration](#priority-configuration)
- [Advanced Options](#advanced-options)

## Target Configuration

```yaml
targets:
  # Option 1: List domains directly
  domains:
    - example.com
    - target.com

  # Option 2: Use file (recommended)
  domains_file: targets.txt
```

## Monitoring Settings

```yaml
monitoring:
  # Cron schedule format (optional, for reference)
  schedule: "0 */6 * * *"  # Every 6 hours

  # Data retention in days
  retention_days: 30

  # Working directories
  data_dir: ./data
  baseline_dir: ./data/baseline
  diff_dir: ./data/diffs
  reports_dir: ./reports
```

## Check Configuration

### Infrastructure Checks

```yaml
checks:
  infrastructure:
    enabled: true
    subdomain_discovery: true
    port_scanning: false          # Not implemented yet
    dns_records: true
    ssl_certificates: true
```

### Web Application Checks

```yaml
checks:
  web_application:
    enabled: true
    http_responses: true
    page_content: true
    technology_detection: true
    security_headers: true
    cookies: true
```

### Content Discovery

```yaml
checks:
  content_discovery:
    enabled: true
    javascript_files: true
    api_endpoints: true
    forms: true
    wayback_urls: false           # Not implemented yet
```

### Attack Surface

```yaml
checks:
  attack_surface:
    enabled: true
    parameters: true
    upload_points: true
    authentication: true
```

## Tool Settings

### Subfinder

```yaml
tools:
  subfinder:
    enabled: true
    timeout: 300  # seconds
```

### Amass

```yaml
tools:
  amass:
    enabled: false  # Slow, disable for quick scans
    timeout: 600
    passive: true
```

### HTTPx

```yaml
tools:
  httpx:
    enabled: true
    threads: 50
    timeout: 10
```

### Katana (Web Crawler)

```yaml
tools:
  katana:
    enabled: true
    depth: 3
    timeout: 300
```

### Nuclei (Vulnerability Scanner)

```yaml
tools:
  nuclei:
    enabled: false  # Optional
    templates:
      - exposures
      - misconfigurations
      - cves
    severity:
      - critical
      - high
      - medium
```

## Notification Settings

### Slack

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    notify_on:
      - new_subdomain
      - new_endpoint
      - new_vulnerability
      - technology_change
      - critical_change
      - subdomain_takeover
      - high_value_target
```

### Discord

```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/YOUR/WEBHOOK"
    notify_on:
      - new_subdomain
      - new_endpoint
      - critical_change
      - subdomain_takeover
```

### Telegram

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
    notify_on:
      - new_subdomain
      - new_endpoint
      - critical_change
      - subdomain_takeover
```

### Email

```yaml
notifications:
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-app-password"  # Use app password, not regular password
    to_email: "your-email@gmail.com"
```

### Daily Digest

```yaml
notifications:
  daily_digest:
    enabled: true
    time: "09:00"  # 24-hour format
    format: "html"  # html or markdown
```

## Diff Detection Settings

```yaml
diff_settings:
  # Ignore dynamic content
  ignore_timestamp_changes: true
  ignore_dynamic_content: true

  # Minimum change threshold (percentage)
  min_change_percent: 5  # Ignore if <5% changed

  # Noise filtering (regex patterns)
  filter_noise:
    - "Set-Cookie: session"
    - "Date:"
    - "Last-Modified:"
    - "ETag:"
    - "_ga="
    - "csrf_token"
```

## Priority Configuration

```yaml
priority:
  # High priority - instant notification
  high:
    - new_subdomain
    - new_admin_panel
    - new_upload_endpoint
    - new_api_endpoint
    - removed_security_header
    - new_vulnerability
    - exposed_sensitive_file
    - subdomain_takeover

  # Medium priority - daily digest
  medium:
    - technology_change
    - new_parameter
    - new_form
    - port_change
    - status_code_change

  # Low priority - weekly report
  low:
    - content_change
    - minor_update
```

## Advanced Options

```yaml
advanced:
  # Parallel processing
  max_workers: 10  # Number of parallel threads

  # Rate limiting (requests per second)
  rate_limit: 10

  # Screenshots
  take_screenshots: false
  screenshot_new_pages: false

  # Auto-scan new findings
  auto_scan_new_targets: false  # Run nuclei on new endpoints

  # Archive old data
  archive_enabled: true
  archive_after_days: 30
```

## Example Configurations

### Quick Scan Configuration

For fast, daily monitoring:

```yaml
tools:
  subfinder:
    enabled: true
    timeout: 180
  amass:
    enabled: false  # Skip for speed
  httpx:
    threads: 100
  katana:
    enabled: false  # Skip crawling

checks:
  content_discovery:
    enabled: false  # Skip for speed

advanced:
  max_workers: 20
```

### Comprehensive Scan Configuration

For thorough, weekly scans:

```yaml
tools:
  subfinder:
    enabled: true
    timeout: 600
  amass:
    enabled: true
    timeout: 1800
  katana:
    enabled: true
    depth: 5
  nuclei:
    enabled: true

checks:
  content_discovery:
    enabled: true
    javascript_files: true
    api_endpoints: true

advanced:
  max_workers: 5  # Slower but thorough
```

### Security-Focused Configuration

Prioritize security findings:

```yaml
notifications:
  slack:
    notify_on:
      - subdomain_takeover
      - new_vulnerability
      - exposed_sensitive_file
      - removed_security_header

priority:
  high:
    - subdomain_takeover
    - new_vulnerability
    - exposed_sensitive_file
    - new_admin_panel
    - new_upload_endpoint

diff_settings:
  min_change_percent: 0  # Detect all changes
```

## Environment Variables

Override config with environment variables:

```bash
# Slack webhook
export BB_SLACK_WEBHOOK="https://hooks.slack.com/..."

# Discord webhook
export BB_DISCORD_WEBHOOK="https://discord.com/api/..."

# Telegram
export BB_TELEGRAM_TOKEN="bot_token"
export BB_TELEGRAM_CHAT="chat_id"

# Email
export BB_EMAIL_PASSWORD="app_password"
```

## Best Practices

1. **Start Conservative**: Enable only essential checks initially
2. **Tune Over Time**: Adjust thresholds based on noise levels
3. **Separate Configs**: Use different configs for different program types
4. **Backup Config**: Version control your config file
5. **Secure Secrets**: Use environment variables for sensitive data

## Troubleshooting

### High Resource Usage

```yaml
advanced:
  max_workers: 5  # Reduce parallelism
  rate_limit: 5    # Slower requests

tools:
  httpx:
    threads: 20  # Reduce threads
```

### Too Many Notifications

```yaml
diff_settings:
  min_change_percent: 10  # Increase threshold

notifications:
  slack:
    notify_on:
      - subdomain_takeover  # Only critical
      - new_vulnerability
```

### Missing Findings

```yaml
diff_settings:
  min_change_percent: 0  # Detect all changes
  ignore_dynamic_content: false

tools:
  amass:
    enabled: true  # Enable comprehensive scan
```

---

For more information, see:
- [Usage Guide](USAGE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Main README](../README.md)
