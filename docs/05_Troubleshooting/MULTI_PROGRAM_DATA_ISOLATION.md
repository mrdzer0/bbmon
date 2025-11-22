# Multi-Program Data Isolation

This document explains how data is isolated between different programs and how to verify it's working correctly.

## How Data Isolation Works

When you use the `-c` flag with a config file, the dashboard reads three key directories from the configuration:

```yaml
monitoring:
  data_dir: ./data/program-a
  baseline_dir: ./data/program-a/baseline
  diff_dir: ./data/program-a/diffs
```

The dashboard will **only** read data from these specific directories, ensuring complete isolation between programs.

## Verifying Data Isolation

### Quick Test

Create two separate programs and verify they show different data:

```bash
# Setup Program A
cat > config.program-a.yaml << 'EOF'
targets:
  domains_file: targets.program-a.txt
monitoring:
  data_dir: ./data/program-a
  baseline_dir: ./data/program-a/baseline
  diff_dir: ./data/program-a/diffs
EOF

# Setup Program B
cat > config.program-b.yaml << 'EOF'
targets:
  domains_file: targets.program-b.txt
monitoring:
  data_dir: ./data/program-b
  baseline_dir: ./data/program-b/baseline
  diff_dir: ./data/program-b/diffs
EOF

# Create different target files
echo "example.com" > targets.program-a.txt
echo "company.com" > targets.program-b.txt

# Initialize both
./monitor.py -c config.program-a.yaml --init
./monitor.py -c config.program-b.yaml --init

# View dashboards - they should show DIFFERENT data
python3 modules/dashboard.py -c config.program-a.yaml
python3 modules/dashboard.py -c config.program-b.yaml
```

### What You Should See

**Program A Dashboard:**
- Shows only data from `./data/program-a/baseline/`
- Lists subdomains for `example.com`
- No data from Program B

**Program B Dashboard:**
- Shows only data from `./data/program-b/baseline/`
- Lists subdomains for `company.com`
- No data from Program A

## Common Issues

### Issue: Dashboard Shows Data from All Programs

**Symptom:**
```bash
python3 modules/dashboard.py -c config.program-a.yaml
# Shows data from both program-a AND program-b
```

**Cause:** Old version of dashboard.py that doesn't properly read config paths.

**Solution:** Make sure you're using the updated dashboard.py that includes:
```python
def main():
    # ...
    if args.config:
        config = load_config(args.config)
        if config:
            monitoring = config.get('monitoring', {})
            data_dir = monitoring.get('data_dir', './data')
            baseline_dir = monitoring.get('baseline_dir')
            diff_dir = monitoring.get('diff_dir')

    dashboard = Dashboard(data_dir=data_dir, baseline_dir=baseline_dir, diff_dir=diff_dir)
```

### Issue: Config File Not Found

**Symptom:**
```bash
python3 modules/dashboard.py -c config.myprogram.yaml
# Error: Config file not found
```

**Solution:**
```bash
# Make sure you're in the project root directory
cd /path/to/bb-monitor

# Check config exists
ls -la config.myprogram.yaml

# Use absolute path if needed
python3 modules/dashboard.py -c /full/path/to/config.myprogram.yaml
```

### Issue: Dashboard Shows No Data

**Symptom:**
```bash
python3 modules/dashboard.py -c config.program-a.yaml
# Shows: Targets: 0, Total Subdomains: 0
```

**Possible Causes:**

1. **Baseline not initialized:**
   ```bash
   # Run init first
   ./monitor.py -c config.program-a.yaml --init
   ```

2. **Wrong data directory in config:**
   ```bash
   # Check your config
   grep -A 3 "monitoring:" config.program-a.yaml

   # Make sure baseline_dir exists
   ls -la data/program-a/baseline/
   ```

3. **No baseline files:**
   ```bash
   # Check for baseline files
   ls -la data/program-a/baseline/*.json

   # If empty, run init
   ./monitor.py -c config.program-a.yaml --init
   ```

## Directory Structure Best Practices

### Recommended Structure (Separate Data Directories)

```
bb-monitor/
├── config.hackerone.yaml
├── config.bugcrowd.yaml
├── config.intigriti.yaml
│
├── data/
│   ├── hackerone/          # Program A data - completely isolated
│   │   ├── baseline/
│   │   ├── diffs/
│   │   ├── subdomain_scans/
│   │   ├── shodan_scans/
│   │   └── wayback_scans/
│   │
│   ├── bugcrowd/           # Program B data - completely isolated
│   │   ├── baseline/
│   │   ├── diffs/
│   │   └── subdomain_scans/
│   │
│   └── intigriti/          # Program C data - completely isolated
│       ├── baseline/
│       └── diffs/
```

### Config File Template

```yaml
# config.PROGRAM_NAME.yaml
targets:
  domains_file: targets.PROGRAM_NAME.txt

monitoring:
  # Use program-specific data directories
  data_dir: ./data/PROGRAM_NAME
  baseline_dir: ./data/PROGRAM_NAME/baseline
  diff_dir: ./data/PROGRAM_NAME/diffs
  reports_dir: ./reports/PROGRAM_NAME

notifications:
  slack:
    enabled: true
    webhook_url: "YOUR_PROGRAM_SPECIFIC_WEBHOOK"

# Other settings...
```

## Testing Data Isolation

### Test Script

Create this test script to verify isolation:

```bash
#!/bin/bash
# test_isolation.sh

echo "Testing data isolation..."

# Create test configs
cat > config.test1.yaml << 'EOF'
targets:
  domains:
    - test1.example.com
monitoring:
  data_dir: ./data/test1
  baseline_dir: ./data/test1/baseline
  diff_dir: ./data/test1/diffs
EOF

cat > config.test2.yaml << 'EOF'
targets:
  domains:
    - test2.example.com
monitoring:
  data_dir: ./data/test2
  baseline_dir: ./data/test2/baseline
  diff_dir: ./data/test2/diffs
EOF

# Initialize both
./monitor.py -c config.test1.yaml --init
./monitor.py -c config.test2.yaml --init

# Get stats from each
echo "Program 1 stats:"
python3 modules/dashboard.py -c config.test1.yaml 2>/dev/null | grep "Total Subdomains"

echo "Program 2 stats:"
python3 modules/dashboard.py -c config.test2.yaml 2>/dev/null | grep "Total Subdomains"

# Cleanup
rm -rf data/test1 data/test2 config.test1.yaml config.test2.yaml

echo "Test complete!"
```

Run with:
```bash
chmod +x test_isolation.sh
./test_isolation.sh
```

## Debugging Commands

### Check Which Directories Are Being Used

```bash
# Dashboard will show directories it's using
python3 modules/dashboard.py -c config.program-a.yaml 2>&1 | head -10
# Output should show:
# [*] Using config: config.program-a.yaml
# [*] Data directory: ./data/program-a
# [*] Baseline directory: ./data/program-a/baseline
# [*] Diff directory: ./data/program-a/diffs
```

### List Baseline Files

```bash
# For program A
ls -lh data/program-a/baseline/

# For program B
ls -lh data/program-b/baseline/

# They should contain DIFFERENT files
```

### Compare Data

```bash
# Get subdomain count for program A
python3 -c "
import json
from pathlib import Path
count = 0
for f in Path('data/program-a/baseline').glob('*_baseline.json'):
    with open(f) as fp:
        data = json.load(fp)
        count += len(data.get('subdomains', {}))
print(f'Program A subdomains: {count}')
"

# Get subdomain count for program B
python3 -c "
import json
from pathlib import Path
count = 0
for f in Path('data/program-b/baseline').glob('*_baseline.json'):
    with open(f) as fp:
        data = json.load(fp)
        count += len(data.get('subdomains', {}))
print(f'Program B subdomains: {count}')
"
```

## Summary

- Each program should have its own `data_dir`, `baseline_dir`, and `diff_dir`
- The `-c` flag makes the dashboard read directories from the config file
- Data is completely isolated between programs when configs are set up correctly
- Always verify isolation after setting up new programs
- Use the helper script `./utils/view_program.sh` for easy access

## See Also

- [QUICK_START_MULTI_PROGRAM.md](../../QUICK_START_MULTI_PROGRAM.md)
- [MULTI_PROGRAM_SETUP.md](../02_Tutorials/MULTI_PROGRAM_SETUP.md)
- [CONFIGURATION.md](../04_Reference/CONFIGURATION.md)
