# Configuration Quick Start

## 5-Minute Setup

### 1. Basic Setup (No Notifications)

```bash
# Already done! Default config.yaml works out of the box
echo "hackerone.com" >> targets.txt
./monitor.py --init
```

### 2. Add Slack Notifications

Edit `config.yaml`:

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

Get webhook: https://api.slack.com/messaging/webhooks

### 3. Add Discord Notifications

Edit `config.yaml`:

```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/YOUR/WEBHOOK"
```

Get webhook: Discord Server → Settings → Integrations → Webhooks

### 4. Add Telegram Notifications

Edit `config.yaml`:

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```

Setup:
1. Message @BotFather on Telegram: `/newbot`
2. Get bot token
3. Message @userinfobot: Get your chat ID

## Configuration Profiles

### Profile 1: Fast Daily Scans (Recommended)

```yaml
tools:
  amass:
    enabled: false        # Skip slow tool
  katana:
    enabled: false        # Skip crawler

advanced:
  max_workers: 20         # More parallelism

diff_settings:
  min_change_percent: 10  # Ignore small changes
```

**Use for**: Daily monitoring, multiple targets

### Profile 2: Comprehensive Weekly Scans

```yaml
tools:
  amass:
    enabled: true         # Full subdomain discovery
  katana:
    enabled: true         # Deep crawling

advanced:
  max_workers: 5          # Slower but thorough

diff_settings:
  min_change_percent: 0   # Catch all changes
```

**Use for**: Weekly deep scans, new targets

### Profile 3: Security-Focused

```yaml
tools:
  nuclei:
    enabled: true         # Vulnerability scanning

notifications:
  slack:
    notify_on:            # Only critical alerts
      - subdomain_takeover
      - high_value_target
      - new_vulnerability

diff_settings:
  min_change_percent: 0   # Detect everything
```

**Use for**: High-value targets, sensitive programs

## Common Configurations

### Quiet Mode (Minimal Notifications)

```yaml
notifications:
  slack:
    enabled: true
    notify_on:
      - subdomain_takeover  # Only critical
      - high_value_target

  daily_digest:
    enabled: false           # No digest
```

### Verbose Mode (All Changes)

```yaml
notifications:
  slack:
    enabled: true
    notify_on:              # Everything
      - new_subdomain
      - new_endpoint
      - technology_change
      - status_code_change
      - content_change

diff_settings:
  min_change_percent: 0     # All changes
```

### High-Performance Mode

```yaml
advanced:
  max_workers: 30           # More workers
  rate_limit: 50            # Faster requests

tools:
  httpx:
    threads: 100            # More threads
```

**Warning**: May get rate-limited

### Resource-Constrained Mode

```yaml
advanced:
  max_workers: 3            # Fewer workers
  rate_limit: 5             # Slower requests

tools:
  amass:
    enabled: false
  katana:
    enabled: false
  httpx:
    threads: 10
```

**Use for**: Slow internet, shared systems

## Environment Variables

Instead of editing config.yaml, use environment variables:

```bash
# Slack
export BB_SLACK_WEBHOOK="https://hooks.slack.com/..."

# Discord
export BB_DISCORD_WEBHOOK="https://discord.com/api/..."

# Telegram
export BB_TELEGRAM_TOKEN="bot_token"
export BB_TELEGRAM_CHAT="chat_id"

# Email
export BB_EMAIL_USERNAME="your@email.com"
export BB_EMAIL_PASSWORD="app_password"

# Then run
./monitor.py --monitor
```

**Advantage**: Keep secrets out of config file

## Quick Tweaks

### More Subdomains

```yaml
tools:
  amass:
    enabled: true
    timeout: 1800          # 30 minutes
```

### Faster Scans

```yaml
tools:
  subfinder:
    timeout: 180           # 3 minutes
  httpx:
    threads: 100
    timeout: 5
```

### Less Noise

```yaml
diff_settings:
  min_change_percent: 15   # Only big changes
  filter_noise:
    - "timestamp"
    - "date"
    - "session"
    - "token"
    - "nonce"
    - "_ga"
```

### More Sensitive

```yaml
diff_settings:
  min_change_percent: 0    # All changes
  ignore_dynamic_content: false
```

## Config Validation

Test your config:

```bash
# Test notification
python3 -c "
from modules.notifier import Notifier
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

notifier = Notifier(config['notifications'])
notifier.send_slack('Test message', {})
"

# Test tools
subfinder -version
httpx -version
dnsx -version
```

## Common Issues

### Issue: No notifications received

**Solution**:
```yaml
notifications:
  slack:
    enabled: true  # Check this is true!
    webhook_url: "..."  # Must be valid webhook
```

Test webhook:
```bash
curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test"}' \
     YOUR_WEBHOOK_URL
```

### Issue: Too many notifications

**Solution**:
```yaml
diff_settings:
  min_change_percent: 15  # Increase threshold

notifications:
  slack:
    notify_on:
      - subdomain_takeover  # Reduce triggers
      - high_value_target
```

### Issue: Scans too slow

**Solution**:
```yaml
tools:
  amass:
    enabled: false  # Disable slow tools
  katana:
    enabled: false

advanced:
  max_workers: 20   # More parallelism
```

### Issue: Getting rate limited

**Solution**:
```yaml
advanced:
  rate_limit: 5     # Reduce request rate
  max_workers: 3    # Less parallelism

tools:
  httpx:
    timeout: 20     # More patience
```

## Best Practices

1. **Start Simple**: Use default config first
2. **Test Notifications**: Send test messages before monitoring
3. **Tune Gradually**: Adjust thresholds based on experience
4. **Use Profiles**: Different configs for different scenarios
5. **Version Control**: Track config changes in git
6. **Backup Config**: Keep copy before major changes
7. **Use Comments**: Document your customizations

## Templates

### New Bug Bounty Program

```yaml
targets:
  domains_file: targets.txt

tools:
  amass:
    enabled: true  # Full discovery

notifications:
  slack:
    enabled: true
    notify_on:
      - new_subdomain
      - subdomain_takeover
      - high_value_target

diff_settings:
  min_change_percent: 0  # Catch everything
```

### Ongoing Monitoring

```yaml
targets:
  domains_file: targets.txt

tools:
  amass:
    enabled: false  # Quick scans

notifications:
  slack:
    notify_on:
      - subdomain_takeover
      - high_value_target
      - new_endpoint

diff_settings:
  min_change_percent: 5  # Ignore noise
```

### Multiple Programs

Create separate configs:

```bash
# Program 1
cp config.yaml config.hackerone.yaml
echo "hackerone.com" > targets.hackerone.txt

# Program 2
cp config.yaml config.bugcrowd.yaml
echo "bugcrowd.com" > targets.bugcrowd.txt

# Run separately
./monitor.py -c config.hackerone.yaml --init
./monitor.py -c config.bugcrowd.yaml --init
```

---

For complete reference, see [CONFIGURATION.md](CONFIGURATION.md)
