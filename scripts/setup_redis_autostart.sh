#!/bin/bash

# Script to setup Redis auto-start on macOS
# This script installs the LaunchAgent to start Redis on login

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PLIST_NAME="com.taxcollector.redis.plist"
PLIST_SOURCE="$SCRIPT_DIR/$PLIST_NAME"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_DEST="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo "Setting up Redis auto-start on macOS..."
echo "========================================"

# Create LaunchAgents directory if it doesn't exist
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo "Creating LaunchAgents directory..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# Check if plist already exists and unload it first
if [ -f "$PLIST_DEST" ]; then
    echo "Unloading existing LaunchAgent..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# Generate plist file with correct paths
echo "Generating plist file with correct paths..."
cat > "$PLIST_DEST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.taxcollector.redis</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$PROJECT_DIR/scripts/start_redis.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/redis_startup.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/redis_startup.error.log</string>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
EOF

# Make sure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Load the LaunchAgent
echo "Loading LaunchAgent..."
launchctl load "$PLIST_DEST"

if [ $? -eq 0 ]; then
    echo "✓ Redis auto-start has been set up successfully!"
    echo ""
    echo "The LaunchAgent will:"
    echo "  - Start Redis when you log in"
    echo "  - Check every 5 minutes if Redis is running"
    echo "  - Start Docker if it's not running"
    echo ""
    echo "Logs will be written to:"
    echo "  - $PROJECT_DIR/logs/redis_startup.log"
    echo "  - $PROJECT_DIR/logs/redis_startup.error.log"
    echo ""
    echo "To manually start Redis now, run:"
    echo "  $PROJECT_DIR/scripts/start_redis.sh"
    echo ""
    echo "To stop auto-start, run:"
    echo "  launchctl unload $PLIST_DEST"
    echo ""
    echo "To check status, run:"
    echo "  launchctl list | grep com.taxcollector.redis"
else
    echo "✗ Failed to load LaunchAgent"
    exit 1
fi

