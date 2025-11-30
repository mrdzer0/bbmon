# BB-Monitor Testing Guide

Complete guide for running unit tests and ensuring code quality.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)

## Quick Start

### Install Test Dependencies

```bash
# Install testing requirements
pip install -r requirements-test.txt

# Or install individually
pip install coverage mock
```

### Test Real Notifications

```bash
# Show configured platforms
./test_real_notifications.py --show-config

# Test baseline alert to all configured platforms
./test_real_notifications.py --baseline

# Test change detection alert
./test_real_notifications.py --changes

# Test critical subdomain takeover alert
./test_real_notifications.py --critical

# Test all alert types
./test_real_notifications.py --all

# Test specific platform only
./test_real_notifications.py --baseline --platform discord
./test_real_notifications.py --changes --platform slack
```

### Run All Tests

```bash
# Using the test runner
./run_tests.py

# Or using unittest directly
python -m unittest discover tests

# Or using pytest (if installed)
pytest tests/
```

### Run Specific Tests

```bash
# Run a specific test module
./run_tests.py -t tests.test_monitor

# Run a specific test class
./run_tests.py -t tests.test_monitor.TestBBMonitor

# Run a specific test method
./run_tests.py -t tests.test_monitor.TestBBMonitor.test_init
```

## Test Structure

```
bb-monitor/
├── tests/
│   ├── __init__.py
│   ├── test_monitor.py         # Main monitor.py tests
│   ├── test_notifier.py        # Notification tests
│   ├── test_http_monitor.py    # HTTP monitoring tests
│   └── test_integration.py     # End-to-end integration tests
├── run_tests.py                # Test runner script
├── requirements-test.txt       # Testing dependencies
└── TESTING.md                  # This file
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests with normal output
./run_tests.py

# Run all tests with verbose output
./run_tests.py -v

# Run all tests quietly (only show failures)
./run_tests.py -q
```

### Test Filtering

```bash
# Run only monitor tests
./run_tests.py -t tests.test_monitor

# Run only notifier tests
./run_tests.py -t tests.test_notifier

# Run only HTTP monitor tests
./run_tests.py -t tests.test_http_monitor

# Run only integration tests
./run_tests.py -t tests.test_integration
```

### Specific Test Cases

```bash
# Test baseline save/load functionality
./run_tests.py -t tests.test_monitor.TestBBMonitor.test_save_and_load_baseline

# Test baseline alert sending
./run_tests.py -t tests.test_monitor.TestBBMonitor.test_save_baseline_with_alert

# Test change detection
./run_tests.py -t tests.test_monitor.TestBBMonitor.test_compare_baselines_new_subdomains

# Test Discord notifications
./run_tests.py -t tests.test_notifier.TestNotifier.test_send_discord

# Test subdomain takeover detection
./run_tests.py -t tests.test_integration.TestIntegration.test_monitoring_with_subdomain_takeover
```

## Test Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
./run_tests.py -c

# View HTML coverage report
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
start htmlcov/index.html     # Windows
```

### Coverage by Module

```bash
# Generate detailed coverage report
coverage run -m unittest discover tests
coverage report

# Show missing lines
coverage report -m

# Generate HTML report
coverage html
```

### Example Coverage Output

```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
monitor.py                          450     45    90%
modules/__init__.py                   5      0   100%
modules/notifier.py                 320     32    90%
modules/http_monitor.py             280     28    90%
modules/subdomain_finder.py         250     50    80%
modules/shodan_scanner.py           180     54    70%
modules/wayback_analyzer.py         190     57    70%
modules/dashboard.py                200     80    60%
-----------------------------------------------------
TOTAL                              1875    346    82%
```

## Real Notification Testing

### Purpose

The `test_real_notifications.py` script sends **ACTUAL notifications** to your configured platforms (Discord, Slack, Telegram, Email). This is different from unit tests which use mocks.

### When to Use

- ✅ Verifying Discord webhook is working
- ✅ Testing Slack integration
- ✅ Confirming Telegram bot configuration
- ✅ Validating email SMTP settings
- ✅ Checking notification formatting
- ✅ Testing specific platform before production use

### How It Works

1. Reads your `config.yaml` configuration
2. Creates sample data (baseline or changes)
3. Sends REAL notifications to configured platforms
4. You verify the alerts were received

### Usage Examples

```bash
# 1. Check your configuration
./test_real_notifications.py --show-config

# Output:
# 📢 Slack: ENABLED
#   Webhook: https://hooks.slack.com/services/...
#   Triggers: new_subdomain, baseline_complete
# 💬 Discord: ENABLED
#   Webhook: https://discord.com/api/webhooks/...
#   Triggers: new_subdomain, changed_endpoint, baseline_complete
```

```bash
# 2. Test baseline alert (like --init would send)
./test_real_notifications.py --baseline

# This sends a baseline_complete alert with sample data:
# - 5 subdomains
# - 3 endpoints
# - Shodan results
# - Wayback results
```

```bash
# 3. Test change detection alert (like --monitor would send)
./test_real_notifications.py --changes

# This sends a change notification with:
# - New subdomains
# - Changed endpoints (status code, title, etc.)
# - New JS endpoints
```

```bash
# 4. Test critical subdomain takeover alert
./test_real_notifications.py --critical

# This sends a CRITICAL alert with:
# - Subdomain takeover detected
# - High confidence
# - Service information
```

```bash
# 5. Test specific platform only
./test_real_notifications.py --baseline --platform discord
./test_real_notifications.py --changes --platform slack
./test_real_notifications.py --critical --platform telegram
```

```bash
# 6. Test all alert types at once
./test_real_notifications.py --all

# Sends: baseline, changes, and critical alerts
```

### Sample Notifications

#### Baseline Alert
```
📊 Baseline Scan Complete

Baseline scan completed for test-example.com

🌐 Subdomains: 5
🔗 Endpoints: 3 (3 live)

✅ 2xx Success: 2
↩️ 3xx Redirect: 0
❌ 4xx Client Error: 1
🔴 5xx Server Error: 0

🎯 High-Value Targets: 1
🛰️ Shodan - Hosts Scanned: 5
📜 Wayback URLs: 1250 (Critical: 3)

Discovered Subdomains (5):
• www.test-example.com
• api.test-example.com
• admin.test-example.com
• staging.test-example.com
• dev.test-example.com
```

#### Change Alert
```
🔍 Monitoring Alert

Monitoring changes detected for test-example.com

Total Changes: 6

🆕 New Subdomains (2)
• new-api.test-example.com
• mobile.test-example.com

🔗 New Endpoints (2)
• https://new-api.test-example.com
• https://mobile.test-example.com

🔄 Changed Endpoints (2)
**https://admin.test-example.com**
  Status: 403 → 200
  Title: Access Denied... → Admin Dashboard...
  Size: 1200 → 25000 (1983.33%)
  Tech Added: PHP, MySQL
  🚩 High-value target: admin (admin in URL)

**https://upload.test-example.com**
  Status: 404 → 200
  Title: Not Found... → File Upload Manager...

📜 New JS Endpoints (2)
• /api/internal/users
• /api/admin/config
```

#### Critical Alert
```
🚨 CRITICAL ALERT

Monitoring changes detected for test-example.com

Total Changes: 2

🚨 SUBDOMAIN TAKEOVERS (2)
• old-app.test-example.com
  Service: heroku
  CNAME: old-app.herokuapp.com
  Confidence: high

• staging-v1.test-example.com
  Service: github
  CNAME: staging-v1.github.io
  Confidence: high
```

### Troubleshooting

#### Discord: "Invalid Webhook"
```bash
# Check webhook URL format
./test_real_notifications.py --show-config

# Correct format:
# https://discord.com/api/webhooks/{id}/{token}
```

#### Slack: "Failed: 404"
```bash
# Webhook URL might be expired or invalid
# Generate new webhook in Slack app settings
```

#### Telegram: No message received
```bash
# Make sure:
# 1. Bot token is correct
# 2. Chat ID is correct
# 3. Bot is added to the chat/channel
# 4. Bot has permission to send messages
```

#### Email: SMTP error
```bash
# Check:
# 1. SMTP server and port
# 2. Username and password
# 3. TLS/SSL settings
# 4. Firewall not blocking SMTP
```

### Integration with Unit Tests

```bash
# Run unit tests (mocked, no real alerts)
./run_tests.py

# After unit tests pass, test real notifications
./test_real_notifications.py --all

# Complete workflow
./run_tests.py && ./test_real_notifications.py --all
```

## Test Coverage Details

### Current Test Coverage

#### test_monitor.py (monitor.py)
✅ **Covers:**
- Initialization and config loading
- Directory setup
- Target retrieval (from config and file)
- Content hashing
- JSON-safe conversion
- Subdomain discovery
- Baseline save/load (WITH and WITHOUT alert flag)
- Baseline comparison (new subdomains, removed subdomains, changed endpoints, takeovers)
- Baseline collection
- Initial baseline run (--init mode)
- Monitoring run (--monitor mode)
- First-time monitoring

**Test Count:** 15 tests

#### test_notifier.py (modules/notifier.py)
✅ **Covers:**
- Notifier initialization
- should_notify logic
- Slack notifications
- Discord notifications
- Telegram notifications
- Baseline alerts (with and without notify_on trigger)
- Change notifications (new subdomains, changed endpoints, takeovers)
- Priority detection (critical/high/normal)
- Discord change notifications with details
- High-value flag handling

**Test Count:** 14 tests

#### test_http_monitor.py (modules/http_monitor.py)
✅ **Covers:**
- HTTPMonitor initialization
- URL probing (success, timeout, connection error)
- Technology detection (WordPress, jQuery)
- Flagging (admin panels, upload endpoints, backup files, outdated tech, status codes, security headers)
- Result comparison (status change, title change, technology change, no changes)
- Snapshot save/load
- Multi-URL probing (sequential and parallel)

**Test Count:** 17 tests

#### test_integration.py
✅ **Covers:**
- Full initialization workflow (--init)
- Full monitoring workflow (no changes)
- Full monitoring workflow (with changes)
- Subdomain takeover detection
- First-time monitoring baseline alert
- Baseline file structure validation
- End-to-end Discord notifications

**Test Count:** 7 tests

### Total Test Count: **53 tests**

## Writing Tests

### Test Template

```python
#!/usr/bin/env python3
"""
Unit tests for modules/your_module.py
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.your_module import YourClass


class TestYourClass(unittest.TestCase):
    """Test cases for YourClass"""

    def setUp(self):
        """Set up test fixtures"""
        self.instance = YourClass()

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_basic_functionality(self):
        """Test basic functionality"""
        result = self.instance.some_method()
        self.assertEqual(result, expected_value)

    @patch('modules.your_module.some_dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependency"""
        mock_dep.return_value = "mocked value"
        result = self.instance.method_using_dependency()
        self.assertTrue(mock_dep.called)


if __name__ == '__main__':
    unittest.main()
```

### Testing Best Practices

1. **Test one thing per test**
   ```python
   # Good
   def test_status_code_change(self):
       changes = compare(old, new)
       self.assertEqual(changes['status_code']['new'], 200)

   # Bad
   def test_everything(self):
       # Testing multiple unrelated things
       pass
   ```

2. **Use descriptive test names**
   ```python
   # Good
   def test_save_baseline_with_alert_sends_notification(self):
       pass

   # Bad
   def test_baseline(self):
       pass
   ```

3. **Mock external dependencies**
   ```python
   @patch('modules.notifier.requests.post')
   def test_discord_notification(self, mock_post):
       mock_post.return_value = Mock(status_code=204)
       # Test logic
   ```

4. **Use setUp and tearDown**
   ```python
   def setUp(self):
       self.temp_dir = tempfile.mkdtemp()

   def tearDown(self):
       shutil.rmtree(self.temp_dir)
   ```

## Test Scenarios Covered

### 1. Baseline Initialization (--init)
- ✅ Creates baseline files
- ✅ Sends baseline_complete alert
- ✅ Discovers subdomains
- ✅ Probes HTTP endpoints
- ✅ Saves to correct directory

### 2. Monitoring Updates (--monitor)
- ✅ Loads existing baseline
- ✅ Compares with new scan
- ✅ Does NOT send baseline_complete alert
- ✅ Sends change notifications when changes detected
- ✅ Updates baseline without alert

### 3. Change Detection
- ✅ Detects new subdomains
- ✅ Detects removed subdomains
- ✅ Detects new endpoints
- ✅ Detects changed endpoints (status, title, content, tech)
- ✅ Detects subdomain takeovers
- ✅ No notification when no changes

### 4. Notification System
- ✅ Baseline alerts only on init
- ✅ Change alerts respect notify_on config
- ✅ Critical alerts for takeovers
- ✅ High priority for new subdomains/endpoints
- ✅ Discord embed formatting
- ✅ Slack block formatting
- ✅ Telegram message formatting

### 5. HTTP Monitoring
- ✅ URL probing with timeout handling
- ✅ Technology detection
- ✅ High-value target flagging
- ✅ Change comparison
- ✅ Parallel probing

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests with coverage
        run: ./run_tests.py -c
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running tests before commit..."
./run_tests.py -q

if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi

echo "All tests passed!"
```

## Troubleshooting

### Tests Fail with Import Errors

```bash
# Make sure you're in the bb-monitor directory
cd /path/to/bb-monitor

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
./run_tests.py
```

### Mock Not Working

```python
# Make sure to patch the correct path
# Patch where it's used, not where it's defined

# Wrong
@patch('requests.post')

# Right
@patch('modules.notifier.requests.post')
```

### Coverage Not Showing Modules

```bash
# Make sure source paths are correct
coverage run --source=monitor,modules -m unittest discover tests
coverage report
```

## Quick Test Commands Cheatsheet

```bash
# Run all tests
./run_tests.py

# Run with coverage
./run_tests.py -c

# Run specific module
./run_tests.py -t tests.test_monitor

# Run specific test
./run_tests.py -t tests.test_monitor.TestBBMonitor.test_init

# Verbose output
./run_tests.py -v

# Quiet output (failures only)
./run_tests.py -q

# Using unittest directly
python -m unittest tests.test_monitor

# Using coverage directly
coverage run -m unittest discover tests
coverage report -m
coverage html
```

## Summary

- **53 total unit tests** covering critical functionality
- Tests for `--init` mode (sends baseline_complete alert)
- Tests for `--monitor` mode (does NOT send baseline_complete alert)
- Tests for change detection and notifications
- Integration tests for complete workflows
- Coverage reporting available
- Easy to run with `./run_tests.py`

All tests focus on ensuring the fix works correctly:
- ✅ Baseline alerts ONLY on `--init`
- ✅ Change notifications on `--monitor`
- ✅ No baseline alerts during routine monitoring/cronjobs
