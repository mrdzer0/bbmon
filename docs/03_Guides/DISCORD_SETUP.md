# Discord Notification Setup Guide

## Quick Setup (3 Steps)

### Step 1: Add Your Webhook to Config

Edit your `config.yaml` and find the `notifications` section:

```yaml
notifications:
  discord:
    enabled: true  # ← Make sure this is true
    webhook_url: "https://discord.com/api/webhooks/xxxxxx/xxxxxxx"
    notify_on:
      - baseline_complete      # ← REQUIRED for init scan alerts!
      - new_subdomain
      - new_endpoint
      - subdomain_takeover
      - high_value_target
      - critical_change
```

**Important:** Make sure `baseline_complete` is in the `notify_on` list!

### Step 2: Test the Configuration

```bash
# Test Discord notification
python3 utils/test_notifications.py -c config.yaml --discord

# Or test with your specific config
python3 utils/test_notifications.py -c config.your-program.yaml --discord
```

You should see:
```
✅ SUCCESS! Test message sent to Discord
```

And receive a test message in your Discord channel.

### Step 3: Run Initial Scan

```bash
# Run init scan (will send baseline alert to Discord)
./monitor.py --init

# Or with specific config
./monitor.py -c config.your-program.yaml --init
```

You should receive a baseline scan notification in Discord with:
- Number of subdomains discovered
- Number of endpoints found
- HTTP status distribution
- Security findings
- List of discovered subdomains

---

## Common Issues

### Issue 1: No Notification Received After Init Scan

**Check 1:** Is Discord enabled?
```bash
grep -A 3 "discord:" config.yaml
```

Should show:
```yaml
  discord:
    enabled: true
```

**Check 2:** Is `baseline_complete` in notify_on?
```bash
grep -A 10 "discord:" config.yaml | grep baseline_complete
```

Should show:
```yaml
      - baseline_complete
```

**Check 3:** Test the webhook directly
```bash
python3 utils/test_notifications.py -c config.yaml --discord
```

### Issue 2: Webhook URL Not Working

**Verify webhook URL is correct:**
```bash
# Test with curl
curl -X POST "https://discord.com/api/webhooks/1441410030371999797/eCq4539sSF6niLwlwDxjH9FSJE5gvRb03NbnjdGZv4sqwxvAu1jqbPB55QDPH3cvoHIf" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test from command line"}'
```

If this works (returns `204` or `200`), the webhook is valid.

### Issue 3: "Discord is DISABLED in config"

**Fix:**
```bash
# Edit config
vim config.yaml

# Change this:
discord:
  enabled: false

# To this:
discord:
  enabled: true
```

### Issue 4: Multiple Config Files (Multi-Program Setup)

If you're using multiple programs, make sure you're testing/running with the correct config:

```bash
# Test specific config
python3 utils/test_notifications.py -c config.program-a.yaml --discord

# Run init with specific config
./monitor.py -c config.program-a.yaml --init
```

---

## What Gets Sent in Baseline Alerts

When you run `--init`, you'll receive a Discord message with:

### Overview Section
- Domain name
- Total subdomains discovered
- Total endpoints found
- Number of live endpoints

### HTTP Status Breakdown
- 2xx Success (green)
- 3xx Redirect (blue)
- 4xx Client Error (yellow)
- 5xx Server Error (red)

### Security Findings
- Subdomain takeovers detected
- High-value targets (admin, api, upload pages)

### Shodan Results (if enabled)
- Hosts scanned
- Hosts with vulnerabilities

### Wayback Results (if enabled)
- Total historical URLs found
- Critical URLs (backups, configs, credentials)

### Subdomain List
- First 15 discovered subdomains
- "... and X more" if more than 15

---

## Testing Checklist

Use this checklist to verify your setup:

- [ ] Discord webhook URL is added to config.yaml
- [ ] `enabled: true` is set for Discord
- [ ] `baseline_complete` is in the `notify_on` list
- [ ] Test script sends message successfully
- [ ] Webhook works when tested with curl
- [ ] Init scan completes without errors
- [ ] Notification appears in Discord channel

---

## Full Configuration Example

```yaml
# config.yaml
targets:
  domains:
    - example.com
    - test.com

monitoring:
  data_dir: ./data
  baseline_dir: ./data/baseline
  diff_dir: ./data/diffs
  reports_dir: ./reports

notifications:
  # Discord (ENABLED)
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/1441410030371999797/eCq4539sSF6niLwlwDxjH9FSJE5gvRb03NbnjdGZv4sqwxvAu1jqbPB55QDPH3cvoHIf"
    notify_on:
      - baseline_complete      # Required for --init alerts
      - new_subdomain          # When new subdomain discovered
      - new_endpoint           # When new endpoint found
      - subdomain_takeover     # When takeover detected
      - high_value_target      # When admin/api/upload page found
      - new_vulnerability      # When new vuln detected
      - technology_change      # When tech stack changes
      - critical_change        # Critical changes

  # Slack (DISABLED for now)
  slack:
    enabled: false
    webhook_url: ""

  # Telegram (DISABLED for now)
  telegram:
    enabled: false

  # Email (DISABLED for now)
  email:
    enabled: false
```

---

## Quick Commands

```bash
# Check if Discord is configured
./utils/fix_discord_config.sh

# Test Discord notification
python3 utils/test_notifications.py -c config.yaml --discord

# Run init scan (will send notification)
./monitor.py --init

# View logs for errors
tail -f logs/monitor.log

# Run with specific config
./monitor.py -c config.program-a.yaml --init
```

---

## Troubleshooting Commands

```bash
# 1. Check config is valid YAML
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))" && echo "✓ Config is valid"

# 2. Check Discord section
grep -A 15 "discord:" config.yaml

# 3. Check if baseline_complete is present
grep -A 15 "discord:" config.yaml | grep baseline_complete

# 4. Test webhook with curl
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test"}'

# 5. Run test notification script
python3 utils/test_notifications.py -c config.yaml --discord

# 6. Check monitor logs during init
./monitor.py --init 2>&1 | tee /tmp/monitor_output.txt
grep -i discord /tmp/monitor_output.txt
```

---

## Support

If notifications still aren't working after following this guide:

1. Run the diagnostic script:
   ```bash
   ./utils/fix_discord_config.sh
   ```

2. Check the output for specific errors

3. Verify your webhook URL is still valid in Discord server settings

4. Make sure the bot has permission to post in the channel

---

## See Also

- `utils/test_notifications.py` - Test all notification platforms
- `utils/fix_discord_config.sh` - Check Discord configuration
- `config.yaml.example` - Full configuration reference
- `docs/04_Reference/CONFIGURATION.md` - Detailed config documentation
