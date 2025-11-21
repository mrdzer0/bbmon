#!/bin/bash
# Setup cron job for automated monitoring

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MONITOR_SCRIPT="${PROJECT_ROOT}/monitor.py"

echo "[*] Setting up cron job for automated monitoring"

# Check if monitor.py exists
if [ ! -f "$MONITOR_SCRIPT" ]; then
    echo "[!] Error: monitor.py not found at $MONITOR_SCRIPT"
    exit 1
fi

# Make sure script is executable
chmod +x "$MONITOR_SCRIPT"

# Create log directory
mkdir -p "${SCRIPT_DIR}/logs"

# Cron job command
CRON_CMD="0 */6 * * * cd ${SCRIPT_DIR} && ${MONITOR_SCRIPT} --monitor >> ${SCRIPT_DIR}/logs/monitor.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$MONITOR_SCRIPT"; then
    echo "[!] Cron job already exists"
    echo "[*] Current cron jobs:"
    crontab -l | grep "$MONITOR_SCRIPT"
    echo ""
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "[*] Keeping existing cron job"
        exit 0
    fi
    # Remove old cron job
    crontab -l | grep -v "$MONITOR_SCRIPT" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "[+] Cron job added successfully!"
echo ""
echo "Schedule: Every 6 hours"
echo "Command: $CRON_CMD"
echo ""
echo "To view cron jobs: crontab -l"
echo "To remove cron job: crontab -e (then delete the line)"
echo "To view logs: tail -f ${SCRIPT_DIR}/logs/monitor.log"
echo ""

# Offer different schedules
echo "Want a different schedule? Edit crontab -e and use:"
echo "  Every 4 hours:  0 */4 * * *"
echo "  Every 12 hours: 0 */12 * * *"
echo "  Daily at 9 AM:  0 9 * * *"
echo "  Twice daily:    0 9,21 * * *"
