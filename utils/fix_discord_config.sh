#!/bin/bash
#
# Fix Discord notification configuration
#

WEBHOOK_URL="https://discord.com/api/webhooks/xxxxxx/xxxxxxxxxxxxxx"

echo "=================================================="
echo "Discord Notification Configuration Helper"
echo "=================================================="
echo ""

# Check for config files
echo "Looking for config files..."
CONFIG_FILES=$(find . -maxdepth 1 -name "*.yaml" -type f ! -name "*example*" 2>/dev/null)

if [ -z "$CONFIG_FILES" ]; then
    echo "No config files found!"
    echo ""
    echo "Creating config.yaml from example..."
    if [ -f "config.yaml.example" ]; then
        cp config.yaml.example config.yaml
        echo "✓ Created config.yaml"
        CONFIG_FILE="config.yaml"
    else
        echo "❌ config.yaml.example not found!"
        exit 1
    fi
else
    echo "Found config files:"
    echo "$CONFIG_FILES"
    echo ""
    CONFIG_FILE=$(echo "$CONFIG_FILES" | head -1)
    echo "Using: $CONFIG_FILE"
fi

echo ""
echo "Checking Discord configuration in $CONFIG_FILE..."
echo ""

# Check if Discord is configured
if grep -q "discord:" "$CONFIG_FILE"; then
    echo "✓ Discord section found"

    # Check if enabled
    if grep -A 5 "discord:" "$CONFIG_FILE" | grep -q "enabled: true"; then
        echo "✓ Discord is enabled"
    else
        echo "⚠  Discord is disabled or not set to true"
        echo ""
        echo "To enable Discord notifications, edit $CONFIG_FILE and set:"
        echo "  notifications:"
        echo "    discord:"
        echo "      enabled: true"
    fi

    # Check webhook URL
    if grep -A 5 "discord:" "$CONFIG_FILE" | grep -q "webhook_url:.*YOUR"; then
        echo "⚠  Webhook URL is using placeholder"
        echo ""
        echo "To fix, replace the webhook_url in $CONFIG_FILE with:"
        echo "  webhook_url: \"$WEBHOOK_URL\""
    elif grep -A 5 "discord:" "$CONFIG_FILE" | grep -q "webhook_url:.*discord.com"; then
        CURRENT_WEBHOOK=$(grep -A 5 "discord:" "$CONFIG_FILE" | grep "webhook_url:" | cut -d'"' -f2)
        echo "✓ Webhook URL is set to: ${CURRENT_WEBHOOK:0:50}..."
    else
        echo "⚠  Webhook URL not found or not set"
    fi

    # Check notify_on
    if grep -A 10 "discord:" "$CONFIG_FILE" | grep -A 5 "notify_on:" | grep -q "baseline_complete"; then
        echo "✓ baseline_complete is in notify_on list"
    else
        echo "⚠  baseline_complete is NOT in notify_on list"
        echo ""
        echo "To enable baseline scan alerts, make sure your config has:"
        echo "  notifications:"
        echo "    discord:"
        echo "      notify_on:"
        echo "        - baseline_complete"
        echo "        - new_subdomain"
        echo "        - subdomain_takeover"
    fi

else
    echo "❌ Discord section not found in config!"
fi

echo ""
echo "=================================================="
echo "Quick Fix Options:"
echo "=================================================="
echo ""
echo "1. Manual edit:"
echo "   vim $CONFIG_FILE"
echo ""
echo "2. Auto-fix (backup will be created):"
echo "   python3 utils/test_notifications.py -c $CONFIG_FILE --example"
echo ""
echo "3. Verify after fixing:"
echo "   python3 utils/test_notifications.py -c $CONFIG_FILE --discord"
echo ""

# Offer to show current Discord config
echo "Show current Discord configuration? (y/n)"
read -r SHOW_CONFIG

if [ "$SHOW_CONFIG" = "y" ]; then
    echo ""
    echo "Current Discord configuration:"
    echo "=================================================="
    grep -A 15 "discord:" "$CONFIG_FILE" | head -20
    echo "=================================================="
fi

echo ""
echo "Done!"
