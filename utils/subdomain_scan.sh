#!/bin/bash
# Enhanced Subdomain Discovery Wrapper Script
# Easy-to-use bash wrapper for subdomain_finder.py

VERSION="1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# Help function
show_help() {
    cat << EOF
${BOLD}${CYAN}Enhanced Subdomain Discovery & Takeover Detection${RESET}
Version: $VERSION

${BOLD}USAGE:${RESET}
    $0 -d <domain> [OPTIONS]

${BOLD}OPTIONS:${RESET}
    -d, --domain <domain>       Target domain (required)
    -o, --output <dir>          Output directory (default: ./output)
    -t, --takeover              Enable takeover detection (default: enabled)
    --no-takeover               Disable takeover detection
    --amass                     Include Amass (slower but more results)
    -q, --quick                 Quick scan (subfinder + crt.sh only)
    -f, --full                  Full scan (all tools including Amass)
    -h, --help                  Show this help message

${BOLD}EXAMPLES:${RESET}
    # Basic scan
    $0 -d example.com

    # Quick scan with custom output
    $0 -d example.com -q -o /tmp/scan_results

    # Full scan with all tools
    $0 -d example.com -f

    # Scan without takeover detection
    $0 -d example.com --no-takeover

${BOLD}OUTPUT:${RESET}
    The script will create:
    • <domain>_all_subdomains.txt  - All discovered subdomains
    • <domain>_by_source.json      - Subdomains grouped by tool
    • <domain>_stats.txt           - Discovery statistics
    • <domain>_takeover_report.txt - Takeover vulnerabilities (if found)

${BOLD}TOOLS USED:${RESET}
    • subfinder         - Fast subdomain discovery
    • assetfinder       - Additional subdomain sources
    • crt.sh            - Certificate transparency logs
    • chaos             - ProjectDiscovery's curated dataset
    • dnsx              - DNS validation and CNAME checking
    • amass (optional)  - Comprehensive subdomain enumeration

${BOLD}TAKEOVER DETECTION:${RESET}
    Automatically checks for subdomain takeover vulnerabilities in:
    • GitHub Pages      • Heroku         • Vercel
    • Netlify           • AWS S3         • Azure
    • Shopify           • WordPress      • And 15+ more services

EOF
}

# Check if Python script exists
check_dependencies() {
    local script_dir=$(dirname "$0")
    local python_script="$script_dir/subdomain_finder.py"

    if [ ! -f "$python_script" ]; then
        echo -e "${RED}[!] Error: subdomain_finder.py not found${RESET}"
        echo -e "${YELLOW}[*] Make sure you're running this from the bb-monitor directory${RESET}"
        exit 1
    fi

    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}[!] Error: python3 not found${RESET}"
        exit 1
    fi

    # Check if required tools are installed
    local missing_tools=()

    for tool in subfinder dnsx; do
        if ! command -v $tool &> /dev/null; then
            missing_tools+=($tool)
        fi
    done

    if [ ${#missing_tools[@]} -gt 0 ]; then
        echo -e "${YELLOW}[!] Warning: Missing required tools: ${missing_tools[*]}${RESET}"
        echo -e "${YELLOW}[*] Install with: go install -v github.com/projectdiscovery/{subfinder,dnsx}/cmd/{subfinder,dnsx}@latest${RESET}"
    fi
}

# Parse arguments
DOMAIN=""
OUTPUT="./output"
TAKEOVER=true
MODE="normal"

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -t|--takeover)
            TAKEOVER=true
            shift
            ;;
        --no-takeover)
            TAKEOVER=false
            shift
            ;;
        --amass)
            MODE="amass"
            shift
            ;;
        -q|--quick)
            MODE="quick"
            shift
            ;;
        -f|--full)
            MODE="full"
            shift
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

# Validate domain
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}[!] Error: Domain is required${RESET}"
    echo -e "${YELLOW}[*] Use: $0 -d example.com${RESET}"
    echo ""
    show_help
    exit 1
fi

# Check dependencies
check_dependencies

# Build Python command
SCRIPT_DIR=$(dirname "$0")
PYTHON_CMD="python3 $SCRIPT_DIR/subdomain_finder.py -d $DOMAIN -o $OUTPUT"

if [ "$TAKEOVER" = false ]; then
    PYTHON_CMD="$PYTHON_CMD --no-takeover"
fi

if [ "$MODE" = "full" ] || [ "$MODE" = "amass" ]; then
    PYTHON_CMD="$PYTHON_CMD --amass"
fi

# Display banner
echo -e "${BOLD}${CYAN}======================================${RESET}"
echo -e "${BOLD}${CYAN}Enhanced Subdomain Discovery${RESET}"
echo -e "${BOLD}${CYAN}======================================${RESET}"
echo -e ""
echo -e "${BOLD}Domain:${RESET}      $DOMAIN"
echo -e "${BOLD}Output:${RESET}      $OUTPUT"
echo -e "${BOLD}Takeover:${RESET}    $TAKEOVER"
echo -e "${BOLD}Mode:${RESET}        $MODE"
echo -e ""

# Run the Python script
echo -e "${BLUE}[*] Starting subdomain discovery...${RESET}"
echo ""

$PYTHON_CMD

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}${BOLD}[+] Scan completed successfully!${RESET}"
    echo -e "${GREEN}[+] Results saved to: $OUTPUT${RESET}"

    # Show quick summary if files exist
    SUBDOMAIN_FILE="$OUTPUT/${DOMAIN}_all_subdomains.txt"
    TAKEOVER_FILE="$OUTPUT/${DOMAIN}_takeover_report.txt"

    if [ -f "$SUBDOMAIN_FILE" ]; then
        COUNT=$(wc -l < "$SUBDOMAIN_FILE")
        echo -e "${GREEN}[+] Total subdomains found: $COUNT${RESET}"
    fi

    if [ -f "$TAKEOVER_FILE" ]; then
        echo -e "${RED}${BOLD}[!] Takeover report available: $TAKEOVER_FILE${RESET}"
    fi
else
    echo ""
    echo -e "${RED}[!] Scan failed with errors${RESET}"
    exit 1
fi
