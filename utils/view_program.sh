#!/bin/bash
#
# Quick wrapper to view dashboard for a specific program
# Usage: ./utils/view_program.sh <program-name> [view-type]
#
# Examples:
#   ./utils/view_program.sh hackerone
#   ./utils/view_program.sh bugcrowd security
#   ./utils/view_program.sh program-a all
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <program-name> [view-type]"
    echo ""
    echo "Examples:"
    echo "  $0 hackerone"
    echo "  $0 bugcrowd security"
    echo "  $0 program-a shodan"
    echo "  $0 program-b wayback"
    echo ""
    echo "Available views:"
    echo "  overview, subdomains, endpoints, technologies, security, shodan, wayback, all"
    exit 1
fi

PROGRAM_NAME=$1
VIEW_TYPE=${2:-overview}

CONFIG_FILE="$PROJECT_ROOT/config.$PROGRAM_NAME.yaml"

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    echo ""
    echo "Available configs:"
    ls -1 "$PROJECT_ROOT"/config.*.yaml 2>/dev/null | sed 's|.*/config.||; s|.yaml||' | sed 's/^/  - /'
    exit 1
fi

# Run dashboard
cd "$PROJECT_ROOT"
python3 modules/dashboard.py -c "$CONFIG_FILE" -v "$VIEW_TYPE"
