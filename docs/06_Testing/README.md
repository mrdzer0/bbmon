# Testing Documentation

Complete testing documentation for BB-Monitor framework.

## 📚 Documentation Index

### Quick Links

| Document | Description |
|----------|-------------|
| [TESTING.md](TESTING.md) | **Complete testing guide** - Unit tests, coverage, real notifications |
| [TEST_RESULTS.md](TEST_RESULTS.md) | Unit test results and coverage report |
| [TEST_CHANGES.md](TEST_CHANGES.md) | Testing guide for baseline alert fix |
| [SUMMARY.md](SUMMARY.md) | Complete project and testing summary |

## 🎯 Quick Start

### Run Unit Tests
```bash
# From project root
./run_tests.py

# With coverage
./run_tests.py -c

# Specific module
./run_tests.py -t tests.test_monitor
```

### Test Real Notifications
```bash
# Show configured platforms
./tests/test_real_notifications.py --show-config

# Test baseline alert
./tests/test_real_notifications.py --baseline

# Test change alert
./tests/test_real_notifications.py --changes

# Test all
./tests/test_real_notifications.py --all
```

## 📁 Test Files Location

```
tests/
├── __init__.py                      # Package init
├── test_monitor.py                  # Main monitoring tests (15 tests)
├── test_notifier.py                 # Notification tests (14 tests)
├── test_http_monitor.py             # HTTP monitoring tests (17 tests)
├── test_integration.py              # Integration tests (11 tests)
└── test_real_notifications.py       # Real notification testing tool
```

## 🎨 Test Types

### 1. Unit Tests (Mocked)
- **Location**: `tests/test_*.py`
- **Run with**: `./run_tests.py`
- **Purpose**: Fast automated testing with mocks
- **Coverage**: All critical functionality

### 2. Real Notification Tests
- **Location**: `tests/test_real_notifications.py`
- **Run with**: `./tests/test_real_notifications.py`
- **Purpose**: Send ACTUAL alerts to platforms
- **Use for**: Configuration verification

## 📊 Test Results Summary

✅ **57/57 tests passing (100%)**

| Module | Tests | Status |
|--------|-------|--------|
| test_monitor.py | 15 | ✅ PASS |
| test_notifier.py | 14 | ✅ PASS |
| test_http_monitor.py | 17 | ✅ PASS |
| test_integration.py | 11 | ✅ PASS |

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed results.

## 🔧 Testing Workflow

```bash
# 1. Development
./run_tests.py                              # Unit tests (fast)

# 2. Verification
./tests/test_real_notifications.py --all   # Real alerts

# 3. Platform-specific
./tests/test_real_notifications.py --baseline --platform discord

# 4. Production
./monitor.py --init                         # First run
./monitor.py --monitor                      # Monitoring
```

## 📖 Related Documentation

- [Getting Started](../01_Getting_Started/) - Installation and setup
- [Configuration](../04_Reference/CONFIGURATION.md) - Config reference
- [Troubleshooting](../05_Troubleshooting/) - Common issues

---

**For complete testing guide, see [TESTING.md](TESTING.md)**
