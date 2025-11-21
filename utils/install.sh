#!/bin/bash
# Installation script for Bug Bounty Monitor

echo "[*] Installing Bug Bounty Monitor..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "[!] Please don't run as root"
    exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create directories
echo -e "${GREEN}[+] Creating directories...${NC}"
mkdir -p data/{baseline,diffs} reports

# Install Python dependencies
echo -e "${GREEN}[+] Installing Python dependencies...${NC}"
pip3 install pyyaml requests --quiet

# Install required tools
echo -e "${GREEN}[+] Checking required tools...${NC}"

install_tool() {
    local tool=$1
    local install_cmd=$2

    if ! command -v $tool &> /dev/null; then
        echo -e "${YELLOW}[!] $tool not found, installing...${NC}"
        eval $install_cmd
    else
        echo -e "${GREEN}[+] $tool already installed${NC}"
    fi
}

# Check for Go
if ! command -v go &> /dev/null; then
    echo -e "${YELLOW}[!] Go not found. Please install Go first.${NC}"
    echo "Visit: https://golang.org/doc/install"
else
    echo -e "${GREEN}[+] Go is installed${NC}"

    # Install Go tools
    echo -e "${GREEN}[+] Installing Go-based recon tools...${NC}"

    # Subfinder
    if ! command -v subfinder &> /dev/null; then
        echo "[*] Installing subfinder..."
        go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    fi

    # httpx
    if ! command -v httpx &> /dev/null; then
        echo "[*] Installing httpx..."
        go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    fi

    # Katana
    if ! command -v katana &> /dev/null; then
        echo "[*] Installing katana..."
        go install github.com/projectdiscovery/katana/cmd/katana@latest
    fi

    # Nuclei
    if ! command -v nuclei &> /dev/null; then
        echo "[*] Installing nuclei..."
        go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    fi

    # dnsx
    if ! command -v dnsx &> /dev/null; then
        echo "[*] Installing dnsx..."
        go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
    fi

    # Amass (optional)
    if ! command -v amass &> /dev/null; then
        echo -e "${YELLOW}[!] Amass not found. Install manually if needed:${NC}"
        echo "go install -v github.com/owasp-amass/amass/v4/...@master"
    fi
fi

# Make scripts executable
echo -e "${GREEN}[+] Making scripts executable...${NC}"
chmod +x monitor.py notifier.py setup_cron.sh

# Create sample targets file
if [ ! -f targets.txt ]; then
    echo -e "${GREEN}[+] Creating sample targets.txt...${NC}"
    cat > targets.txt << 'EOF'
# Add your target domains here (one per line)
# example.com
# target.com
EOF
fi

# Update config with actual paths
echo -e "${GREEN}[+] Setting up configuration...${NC}"
CURRENT_DIR=$(pwd)
sed -i "s|./data|${CURRENT_DIR}/data|g" config.yaml
sed -i "s|./reports|${CURRENT_DIR}/reports|g" config.yaml

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your settings"
echo "2. Add target domains to targets.txt"
echo "3. Run initial baseline: ./monitor.py --init"
echo "4. Set up cron job: ./setup_cron.sh"
echo "5. Monitor changes: ./monitor.py --monitor"
echo ""
echo -e "${YELLOW}Optional:${NC}"
echo "- Configure notifications in config.yaml"
echo "- Update tool configurations as needed"
echo ""
