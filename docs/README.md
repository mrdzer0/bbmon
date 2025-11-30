# BB-Monitor Documentation

Complete documentation for Bug Bounty Monitoring Framework.

## 📚 Documentation Structure

```
docs/
├── 01_Getting_Started/       # Installation, setup, basics
├── 02_Tutorials/             # Step-by-step guides
├── 03_Guides/                # Feature-specific guides
├── 04_Reference/             # Configuration and API reference
├── 05_Troubleshooting/       # Common issues and solutions
└── 06_Testing/               # Testing documentation
```

## 🚀 Quick Navigation

### New Users Start Here

1. **[Getting Started](01_Getting_Started/README.md)** - Installation and first run
2. **[Usage Guide](01_Getting_Started/USAGE.md)** - Basic usage and commands
3. **[Configuration Quick Start](01_Getting_Started/CONFIG_QUICK_START.md)** - Essential config

### Common Tasks

| Task | Documentation |
|------|--------------|
| 📦 Initial Setup | [Getting Started](01_Getting_Started/) |
| ⚙️ Configuration | [Configuration Reference](04_Reference/CONFIGURATION.md) |
| 🔔 Setup Discord | [Discord Setup Guide](03_Guides/DISCORD_SETUP.md) |
| 🛰️ Add Shodan | [Shodan Integration](03_Guides/SHODAN_INTEGRATION.md) |
| 📜 Add Wayback | [Wayback Integration](03_Guides/WAYBACK_INTEGRATION.md) |
| 🎯 Multiple Programs | [Multi-Program Setup](02_Tutorials/MULTI_PROGRAM_SETUP.md) |
| 🧪 Testing | [Testing Guide](06_Testing/TESTING.md) |
| 🐛 Troubleshooting | [Troubleshooting Guide](05_Troubleshooting/TROUBLESHOOTING.md) |

## 📖 Documentation Index

### 01. Getting Started

Essential documentation for new users.

| Document | Description |
|----------|-------------|
| [README.md](01_Getting_Started/README.md) | Overview and quick links |
| [USAGE.md](01_Getting_Started/USAGE.md) | Basic usage and commands |
| [CONFIG_QUICK_START.md](01_Getting_Started/CONFIG_QUICK_START.md) | Quick configuration guide |
| [PROJECT_STRUCTURE.md](01_Getting_Started/PROJECT_STRUCTURE.md) | Project layout and files |

### 02. Tutorials

Step-by-step guides for common scenarios.

| Document | Description |
|----------|-------------|
| [README.md](02_Tutorials/README.md) | Tutorial overview |
| [MULTI_PROGRAM_SETUP.md](02_Tutorials/MULTI_PROGRAM_SETUP.md) | Monitor multiple programs |
| [MULTI_PROGRAM_EXAMPLE.md](02_Tutorials/MULTI_PROGRAM_EXAMPLE.md) | Complete example walkthrough |
| [QUICK_START_MULTI_PROGRAM.md](02_Tutorials/QUICK_START_MULTI_PROGRAM.md) | Quick multi-program guide |

### 03. Guides

Feature-specific implementation guides.

| Document | Description |
|----------|-------------|
| [README.md](03_Guides/README.md) | Guide overview |
| [DISCORD_SETUP.md](03_Guides/DISCORD_SETUP.md) | Discord webhook setup |
| [SHODAN_INTEGRATION.md](03_Guides/SHODAN_INTEGRATION.md) | Shodan API integration |
| [WAYBACK_INTEGRATION.md](03_Guides/WAYBACK_INTEGRATION.md) | Wayback Machine integration |

### 04. Reference

Technical reference and configuration details.

| Document | Description |
|----------|-------------|
| [README.md](04_Reference/README.md) | Reference overview |
| [CONFIGURATION.md](04_Reference/CONFIGURATION.md) | Complete configuration reference |

### 05. Troubleshooting

Common issues and solutions.

| Document | Description |
|----------|-------------|
| [README.md](05_Troubleshooting/README.md) | Troubleshooting overview |
| [TROUBLESHOOTING.md](05_Troubleshooting/TROUBLESHOOTING.md) | Common problems and fixes |
| [MULTI_PROGRAM_DATA_ISOLATION.md](05_Troubleshooting/MULTI_PROGRAM_DATA_ISOLATION.md) | Multi-program data issues |
| [PATH_TROUBLESHOOTING.md](05_Troubleshooting/PATH_TROUBLESHOOTING.md) | Path-related issues |

### 06. Testing

Testing documentation and guides.

| Document | Description |
|----------|-------------|
| [README.md](06_Testing/README.md) | Testing overview |
| [TESTING.md](06_Testing/TESTING.md) | Complete testing guide |
| [TEST_RESULTS.md](06_Testing/TEST_RESULTS.md) | Unit test results |
| [TEST_CHANGES.md](06_Testing/TEST_CHANGES.md) | Baseline alert fix testing |
| [SUMMARY.md](06_Testing/SUMMARY.md) | Complete project summary |

## 🎯 By Use Case

### First Time Setup
```
1. Getting Started/USAGE.md
2. Getting Started/CONFIG_QUICK_START.md
3. Guides/DISCORD_SETUP.md
4. Run: ./monitor.py --init
```

### Adding New Features
```
1. Guides/SHODAN_INTEGRATION.md (if adding Shodan)
2. Guides/WAYBACK_INTEGRATION.md (if adding Wayback)
3. Reference/CONFIGURATION.md (for all options)
```

### Managing Multiple Programs
```
1. Tutorials/MULTI_PROGRAM_SETUP.md
2. Tutorials/MULTI_PROGRAM_EXAMPLE.md
3. Troubleshooting/MULTI_PROGRAM_DATA_ISOLATION.md
```

### Testing & Development
```
1. Testing/TESTING.md (complete guide)
2. Testing/TEST_RESULTS.md (test coverage)
3. Run: ./run_tests.py
4. Run: ./tests/test_real_notifications.py --all
```

### Troubleshooting
```
1. Troubleshooting/TROUBLESHOOTING.md (start here)
2. Guides/DISCORD_SETUP.md (Discord issues)
3. Troubleshooting/PATH_TROUBLESHOOTING.md (path issues)
```

## 🔍 Quick Search

### Commands
- **Initialize**: `./monitor.py --init` - See [USAGE.md](01_Getting_Started/USAGE.md)
- **Monitor**: `./monitor.py --monitor` - See [USAGE.md](01_Getting_Started/USAGE.md)
- **Dashboard**: `./modules/dashboard.py` - See [USAGE.md](01_Getting_Started/USAGE.md)
- **Testing**: `./run_tests.py` - See [Testing/TESTING.md](06_Testing/TESTING.md)

### Configuration
- **Discord**: [Discord Setup Guide](03_Guides/DISCORD_SETUP.md)
- **Shodan**: [Shodan Integration](03_Guides/SHODAN_INTEGRATION.md)
- **Wayback**: [Wayback Integration](03_Guides/WAYBACK_INTEGRATION.md)
- **Full Config**: [Configuration Reference](04_Reference/CONFIGURATION.md)

### Features
- **Subdomain Discovery**: [Getting Started](01_Getting_Started/)
- **HTTP Monitoring**: [Getting Started](01_Getting_Started/)
- **Change Detection**: [USAGE.md](01_Getting_Started/USAGE.md)
- **Notifications**: [Discord Setup](03_Guides/DISCORD_SETUP.md)

## 📝 Contributing to Documentation

### Adding New Documentation

1. Choose appropriate directory:
   - `01_Getting_Started/` - Basic setup and usage
   - `02_Tutorials/` - Step-by-step guides
   - `03_Guides/` - Feature-specific guides
   - `04_Reference/` - Technical reference
   - `05_Troubleshooting/` - Problem solutions
   - `06_Testing/` - Testing documentation

2. Create markdown file with clear structure
3. Update relevant README.md
4. Link from main docs/README.md

### Documentation Standards

- ✅ Use clear, concise language
- ✅ Include code examples
- ✅ Add command outputs
- ✅ Cross-reference related docs
- ✅ Keep table of contents updated

## 🆘 Need Help?

1. **Check docs** - Start with relevant section above
2. **Search** - Use Ctrl+F in browser
3. **Troubleshooting** - See [Troubleshooting Guide](05_Troubleshooting/)
4. **Issues** - [GitHub Issues](https://github.com/mrdzer0/bb-monitor/issues)

## 📊 Documentation Stats

- **Total Docs**: 30+ files
- **Categories**: 6 main sections
- **Code Examples**: 150+ snippets
- **Test Coverage**: 57 unit tests (100%)
- **Last Updated**: 2025-01-30

---

**Start your journey**: [Getting Started →](01_Getting_Started/README.md)
