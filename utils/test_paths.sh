#!/bin/bash
# Test script to verify all paths are correct

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

echo "Testing BB-Monitor Path Configuration"
echo "======================================"
echo ""

# Get paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Script directory: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"
echo ""

# Test files
echo "Checking critical files..."
echo ""

files=(
    "monitor.py"
    "config.yaml.example"
    "requirements.txt"
    "modules/__init__.py"
    "modules/subdomain_finder.py"
    "modules/http_monitor.py"
    "modules/shodan_scanner.py"
    "modules/dashboard.py"
    "modules/notifier.py"
    "utils/subdomain_scan.sh"
    "utils/setup_cron.sh"
    "utils/install.sh"
)

missing=0
for file in "${files[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo -e "${GREEN}✓${RESET} $file"
    else
        echo -e "${RED}✗${RESET} $file (missing)"
        missing=$((missing + 1))
    fi
done

echo ""

# Test Python imports
echo "Testing Python module imports..."
echo ""

cd "$PROJECT_ROOT"

python3 << 'EOF'
import sys
import os

errors = []

# Test core imports
try:
    from modules.subdomain_finder import SubdomainFinder
    print("✓ subdomain_finder module")
except ImportError as e:
    print(f"✗ subdomain_finder module: {e}")
    errors.append("subdomain_finder")

try:
    from modules.http_monitor import HTTPMonitor
    print("✓ http_monitor module")
except ImportError as e:
    print(f"✗ http_monitor module: {e}")
    errors.append("http_monitor")

try:
    from modules.dashboard import Dashboard
    print("✓ dashboard module")
except ImportError as e:
    print(f"✗ dashboard module: {e}")
    errors.append("dashboard")

try:
    from modules.notifier import Notifier
    print("✓ notifier module")
except ImportError as e:
    print(f"✗ notifier module: {e}")
    errors.append("notifier")

# Shodan is optional
try:
    from modules.shodan_scanner import ShodanScanner
    print("✓ shodan_scanner module (optional)")
except ImportError:
    print("⚠ shodan_scanner module (not installed - optional)")

sys.exit(len(errors))
EOF

python_result=$?
echo ""

# Test standalone module execution
echo "Testing standalone module execution..."
echo ""

# Test subdomain_finder help
if python3 "$PROJECT_ROOT/modules/subdomain_finder.py" --help &>/dev/null; then
    echo -e "${GREEN}✓${RESET} subdomain_finder.py standalone"
else
    echo -e "${RED}✗${RESET} subdomain_finder.py standalone"
    missing=$((missing + 1))
fi

# Test http_monitor help
if python3 "$PROJECT_ROOT/modules/http_monitor.py" --help &>/dev/null; then
    echo -e "${GREEN}✓${RESET} http_monitor.py standalone"
else
    echo -e "${RED}✗${RESET} http_monitor.py standalone"
    missing=$((missing + 1))
fi

# Test dashboard help
if python3 "$PROJECT_ROOT/modules/dashboard.py" --help &>/dev/null; then
    echo -e "${GREEN}✓${RESET} dashboard.py standalone"
else
    echo -e "${RED}✗${RESET} dashboard.py standalone"
    missing=$((missing + 1))
fi

echo ""

# Test utility scripts
echo "Testing utility scripts..."
echo ""

if "$PROJECT_ROOT/utils/subdomain_scan.sh" --help &>/dev/null; then
    echo -e "${GREEN}✓${RESET} subdomain_scan.sh"
else
    echo -e "${RED}✗${RESET} subdomain_scan.sh"
    missing=$((missing + 1))
fi

echo ""

# Summary
echo "======================================"
if [ $missing -eq 0 ] && [ $python_result -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${RESET}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the errors above.${RESET}"
    exit 1
fi
