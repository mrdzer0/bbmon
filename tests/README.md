# BB-Monitor Test Suite

Comprehensive test suite for BB-Monitor framework.

## 📁 Test Structure

```
tests/
├── README.md                       # This file
├── __init__.py                     # Package initialization
├── test_monitor.py                 # Main monitoring tests (15 tests)
├── test_notifier.py                # Notification system tests (14 tests)
├── test_http_monitor.py            # HTTP monitoring tests (17 tests)
├── test_integration.py             # End-to-end integration tests (11 tests)
└── test_real_notifications.py      # Real notification testing tool
```

## 🚀 Quick Start

### Run All Tests
```bash
# From project root
./run_tests.py

# Output:
# Tests run: 57
# Successes: 57
# ✅ All tests passed!
```

### Run Specific Tests
```bash
# Specific module
./run_tests.py -t tests.test_monitor

# Specific test class
./run_tests.py -t tests.test_monitor.TestBBMonitor

# Specific test method
./run_tests.py -t tests.test_monitor.TestBBMonitor.test_save_baseline_with_alert
```

### With Coverage
```bash
./run_tests.py -c

# View HTML report
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
```

## 📊 Test Coverage

### Unit Tests: 57 Total

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_monitor.py` | 15 | Main monitoring functionality |
| `test_notifier.py` | 14 | Notification system |
| `test_http_monitor.py` | 17 | HTTP monitoring & flagging |
| `test_integration.py` | 11 | End-to-end workflows |

### Critical Tests

**Baseline Alert Fix:**
- ✅ `test_save_baseline_with_alert` - Sends alert when `send_alert=True`
- ✅ `test_save_baseline_without_alert` - NO alert when `send_alert=False`
- ✅ `test_run_initial_baseline` - `--init` mode sends baseline alert
- ✅ `test_run_monitoring` - `--monitor` mode sends change alerts only

**Change Detection:**
- ✅ `test_compare_baselines_new_subdomains` - New subdomain detection
- ✅ `test_compare_baselines_changed_endpoints` - Endpoint changes
- ✅ `test_notify_changes_critical_takeover` - CRITICAL takeover alerts

## 🎯 Real Notification Testing

Test ACTUAL notifications to configured platforms.

```bash
# Show configuration
./tests/test_real_notifications.py --show-config

# Test baseline alert (like --init)
./tests/test_real_notifications.py --baseline

# Test change alert (like --monitor)
./tests/test_real_notifications.py --changes

# Test critical subdomain takeover alert
./tests/test_real_notifications.py --critical

# Test all alert types
./tests/test_real_notifications.py --all

# Platform-specific testing
./tests/test_real_notifications.py --baseline --platform discord
./tests/test_real_notifications.py --changes --platform slack
```

### When to Use Real Tests

- ✅ Before production deployment
- ✅ After config changes
- ✅ Verifying webhook URLs
- ✅ Testing notification formatting
- ✅ Troubleshooting alert issues

## 📋 Test Scenarios

### ✅ Baseline Behavior

| Scenario | Expected | Test |
|----------|----------|------|
| `./monitor.py --init` | Send baseline_complete | ✅ Verified |
| `./monitor.py --monitor` (existing) | NO baseline_complete | ✅ Verified |
| `./monitor.py --monitor` (first-time) | Send baseline_complete | ✅ Verified |
| Cronjob execution | NO baseline_complete | ✅ Verified |

### ✅ Change Notifications

| Change Type | Alert Priority | Test |
|-------------|---------------|------|
| New subdomains | HIGH | ✅ Verified |
| Changed endpoints | HIGH/MEDIUM | ✅ Verified |
| Subdomain takeovers | CRITICAL | ✅ Verified |
| High-value flags | CRITICAL | ✅ Verified |
| No changes | None | ✅ Verified |

## 🔧 Writing New Tests

### Template

```python
import unittest
from unittest.mock import Mock, patch

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pass

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_feature(self):
        """Test feature functionality"""
        result = function_to_test()
        self.assertEqual(result, expected_value)

    @patch('module.dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependency"""
        mock_dep.return_value = "mocked"
        result = function_using_dependency()
        self.assertTrue(mock_dep.called)
```

### Best Practices

1. **One thing per test**
2. **Descriptive test names**
3. **Mock external dependencies**
4. **Use setUp/tearDown for fixtures**
5. **Test both success and failure paths**

## 📖 Documentation

Full testing documentation available in `docs/06_Testing/`:

- [TESTING.md](../docs/06_Testing/TESTING.md) - Complete testing guide
- [TEST_RESULTS.md](../docs/06_Testing/TEST_RESULTS.md) - Detailed test results
- [TEST_CHANGES.md](../docs/06_Testing/TEST_CHANGES.md) - Testing for baseline fix
- [SUMMARY.md](../docs/06_Testing/SUMMARY.md) - Complete project summary

## 🐛 Troubleshooting

### Tests Fail with Import Errors
```bash
# Ensure you're in project root
cd /path/to/bb-monitor

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Mock Not Working
```python
# Patch where it's USED, not where it's DEFINED
# Wrong:
@patch('requests.post')

# Right:
@patch('modules.notifier.requests.post')
```

### Coverage Not Showing
```bash
# Correct source paths
coverage run --source=monitor,modules -m unittest discover tests
coverage report
```

## 📞 Support

Issues with tests?
1. Check [TESTING.md](../docs/06_Testing/TESTING.md)
2. Review test output carefully
3. Run with verbose: `./run_tests.py -v`
4. Check individual test: `./run_tests.py -t tests.test_name`

---

**Test Suite Status: ✅ 57/57 Passing (100%)**
