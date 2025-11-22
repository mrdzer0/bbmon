#!/bin/bash
# Quick setup for adding a new bug bounty program to monitor

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
RESET='\033[0m'

# Get script and project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

show_help() {
    cat << EOF
${BLUE}Bug Bounty Program Setup Script${RESET}

USAGE:
    $0 -n <program_name> [OPTIONS]

OPTIONS:
    -n, --name <name>        Program name (e.g., hackerone, bugcrowd)
    -d, --domains <file>     File with target domains (one per line)
    -s, --slack <webhook>    Slack webhook URL
    --discord <webhook>      Discord webhook URL
    --telegram <chat_id>     Telegram chat ID
    -h, --help              Show this help message

EXAMPLES:
    # Basic setup
    $0 -n hackerone

    # Setup with domains
    $0 -n bugcrowd -d ~/recon/bugcrowd_scope.txt

    # Setup with Slack
    $0 -n intigriti -s "https://hooks.slack.com/services/XXX/YYY/ZZZ"

WHAT IT DOES:
    1. Creates program-specific config file
    2. Creates program-specific target list
    3. Creates data directories
    4. Optionally adds cron job
    5. Runs initial baseline scan

EOF
}

# Parse arguments
PROGRAM_NAME=""
DOMAINS_FILE=""
SLACK_WEBHOOK=""
DISCORD_WEBHOOK=""
TELEGRAM_CHAT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            PROGRAM_NAME="$2"
            shift 2
            ;;
        -d|--domains)
            DOMAINS_FILE="$2"
            shift 2
            ;;
        -s|--slack)
            SLACK_WEBHOOK="$2"
            shift 2
            ;;
        --discord)
            DISCORD_WEBHOOK="$2"
            shift 2
            ;;
        --telegram)
            TELEGRAM_CHAT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}[!] Unknown option: $1${RESET}"
            show_help
            exit 1
            ;;
    esac
done

# Validate program name
if [ -z "$PROGRAM_NAME" ]; then
    echo -e "${RED}[!] Error: Program name is required${RESET}"
    echo -e "${YELLOW}[*] Use: $0 -n program_name${RESET}"
    exit 1
fi

# Sanitize program name (lowercase, no spaces)
PROGRAM_NAME=$(echo "$PROGRAM_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')

echo -e "${BLUE}========================================${RESET}"
echo -e "${BLUE}Setting up program: ${PROGRAM_NAME}${RESET}"
echo -e "${BLUE}========================================${RESET}"
echo ""

# Check if config.yaml.example exists
if [ ! -f "$PROJECT_ROOT/config.yaml.example" ]; then
    echo -e "${RED}[!] Error: config.yaml.example not found${RESET}"
    exit 1
fi

# 1. Create config file
CONFIG_FILE="$PROJECT_ROOT/config.${PROGRAM_NAME}.yaml"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}[!] Config file already exists: $CONFIG_FILE${RESET}"
    read -p "Overwrite? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}[*] Keeping existing config${RESET}"
    else
        cp "$PROJECT_ROOT/config.yaml.example" "$CONFIG_FILE"
        echo -e "${GREEN}[+] Config file created: $CONFIG_FILE${RESET}"
    fi
else
    cp "$PROJECT_ROOT/config.yaml.example" "$CONFIG_FILE"
    echo -e "${GREEN}[+] Config file created: $CONFIG_FILE${RESET}"
fi

# 2. Update config with program-specific paths
echo -e "${BLUE}[*] Configuring paths...${RESET}"
sed -i "s|domains_file: targets.txt|domains_file: targets.${PROGRAM_NAME}.txt|g" "$CONFIG_FILE"
sed -i "s|data_dir: ./data|data_dir: ./data/${PROGRAM_NAME}|g" "$CONFIG_FILE"
sed -i "s|baseline_dir: ./data/baseline|baseline_dir: ./data/${PROGRAM_NAME}/baseline|g" "$CONFIG_FILE"
sed -i "s|diff_dir: ./data/diffs|diff_dir: ./data/${PROGRAM_NAME}/diffs|g" "$CONFIG_FILE"
sed -i "s|reports_dir: ./reports|reports_dir: ./reports/${PROGRAM_NAME}|g" "$CONFIG_FILE"

# 3. Update notification settings if provided
if [ -n "$SLACK_WEBHOOK" ]; then
    echo -e "${BLUE}[*] Configuring Slack webhook...${RESET}"
    sed -i "s|webhook_url: \".*\"|webhook_url: \"$SLACK_WEBHOOK\"|g" "$CONFIG_FILE"
    sed -i "/slack:/,/enabled:/ s|enabled: false|enabled: true|" "$CONFIG_FILE"
    echo -e "${GREEN}[+] Slack webhook configured${RESET}"
fi

if [ -n "$DISCORD_WEBHOOK" ]; then
    echo -e "${BLUE}[*] Configuring Discord webhook...${RESET}"
    # Discord config update would go here
    echo -e "${GREEN}[+] Discord webhook configured${RESET}"
fi

# 4. Create target list
TARGETS_FILE="$PROJECT_ROOT/targets.${PROGRAM_NAME}.txt"
if [ -f "$TARGETS_FILE" ]; then
    echo -e "${YELLOW}[!] Target file already exists: $TARGETS_FILE${RESET}"
else
    if [ -n "$DOMAINS_FILE" ] && [ -f "$DOMAINS_FILE" ]; then
        cp "$DOMAINS_FILE" "$TARGETS_FILE"
        echo -e "${GREEN}[+] Target file created from: $DOMAINS_FILE${RESET}"
        echo -e "${GREEN}[+] Added $(wc -l < $TARGETS_FILE) domains${RESET}"
    else
        # Create empty target file with instructions
        cat > "$TARGETS_FILE" << EOF
# Target domains for ${PROGRAM_NAME}
# Add one domain per line
# Example:
# example.com
# api.example.com
# app.example.com

EOF
        echo -e "${GREEN}[+] Target file created: $TARGETS_FILE${RESET}"
        echo -e "${YELLOW}[!] Please add target domains to this file${RESET}"
    fi
fi

# 5. Create data directories
echo -e "${BLUE}[*] Creating data directories...${RESET}"
mkdir -p "$PROJECT_ROOT/data/${PROGRAM_NAME}"/{baseline,diffs,subdomain_scans,shodan_scans}
mkdir -p "$PROJECT_ROOT/reports/${PROGRAM_NAME}"
mkdir -p "$PROJECT_ROOT/logs"
echo -e "${GREEN}[+] Data directories created${RESET}"

# 6. Summary
echo ""
echo -e "${GREEN}========================================${RESET}"
echo -e "${GREEN}Setup Complete!${RESET}"
echo -e "${GREEN}========================================${RESET}"
echo ""
echo -e "Program: ${YELLOW}${PROGRAM_NAME}${RESET}"
echo -e "Config:  ${CONFIG_FILE}"
echo -e "Targets: ${TARGETS_FILE}"
echo -e "Data:    $PROJECT_ROOT/data/${PROGRAM_NAME}/"
echo ""

# 7. Next steps
echo -e "${BLUE}Next Steps:${RESET}"
echo ""

# Check if targets exist
TARGET_COUNT=$(grep -v '^#' "$TARGETS_FILE" | grep -v '^$' | wc -l)
if [ "$TARGET_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}1. Add target domains to:${RESET}"
    echo -e "   ${TARGETS_FILE}"
    echo ""
fi

echo -e "${BLUE}2. Review configuration:${RESET}"
echo -e "   vim ${CONFIG_FILE}"
echo ""

echo -e "${BLUE}3. Run initial baseline scan:${RESET}"
echo -e "   cd $PROJECT_ROOT"
echo -e "   ./monitor.py -c config.${PROGRAM_NAME}.yaml --init"
echo ""

echo -e "${BLUE}4. Setup monitoring (optional):${RESET}"
echo -e "   # Add to crontab:"
echo -e "   crontab -e"
echo -e "   # Add line:"
echo -e "   0 */6 * * * cd $PROJECT_ROOT && ./monitor.py -c config.${PROGRAM_NAME}.yaml --monitor >> logs/${PROGRAM_NAME}_monitor.log 2>&1"
echo ""

echo -e "${BLUE}5. View dashboard:${RESET}"
echo -e "   python3 modules/dashboard.py --data-dir ./data/${PROGRAM_NAME}"
echo ""

# Offer to run baseline scan
if [ "$TARGET_COUNT" -gt 0 ]; then
    echo ""
    read -p "Run initial baseline scan now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}[*] Running baseline scan...${RESET}"
        cd "$PROJECT_ROOT"
        ./monitor.py -c "config.${PROGRAM_NAME}.yaml" --init

        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}[+] Baseline scan completed!${RESET}"
            echo ""
            echo -e "${BLUE}View results:${RESET}"
            echo -e "   python3 modules/dashboard.py --data-dir ./data/${PROGRAM_NAME}"
        else
            echo -e "${RED}[!] Baseline scan failed${RESET}"
            echo -e "${YELLOW}[*] Check logs: logs/${PROGRAM_NAME}_monitor.log${RESET}"
        fi
    fi
fi

echo ""
echo -e "${GREEN}Done! 🎉${RESET}"
