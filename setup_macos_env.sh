#!/bin/bash
#
# DaVinci Resolve Environment Setup for macOS
# This script automatically configures the required environment variables
#

set -e

echo "========================================================================"
echo "  DaVinci Resolve - macOS Environment Setup"
echo "========================================================================"
echo ""

# Detect the current shell
CURRENT_SHELL=$(basename "$SHELL")
echo "Detected shell: $CURRENT_SHELL"

# Determine which config file to use
if [ "$CURRENT_SHELL" = "zsh" ]; then
    CONFIG_FILE="$HOME/.zshrc"
    echo "Will configure: ~/.zshrc"
elif [ "$CURRENT_SHELL" = "bash" ]; then
    if [ -f "$HOME/.bash_profile" ]; then
        CONFIG_FILE="$HOME/.bash_profile"
        echo "Will configure: ~/.bash_profile"
    else
        CONFIG_FILE="$HOME/.bashrc"
        echo "Will configure: ~/.bashrc"
    fi
else
    echo "Warning: Unknown shell. Defaulting to ~/.zshrc"
    CONFIG_FILE="$HOME/.zshrc"
fi

echo ""

# Check if DaVinci Resolve is installed
RESOLVE_PATH="/Applications/DaVinci Resolve/DaVinci Resolve.app"
if [ ! -d "$RESOLVE_PATH" ]; then
    echo "ERROR: DaVinci Resolve not found at: $RESOLVE_PATH"
    echo "Please install DaVinci Resolve first."
    exit 1
fi
echo "✓ Found DaVinci Resolve installation"

# Check if scripting API exists
SCRIPT_API_PATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
if [ ! -d "$SCRIPT_API_PATH" ]; then
    echo "ERROR: Scripting API not found at: $SCRIPT_API_PATH"
    echo "Please reinstall DaVinci Resolve or check your installation."
    exit 1
fi
echo "✓ Found Scripting API"

# Check if fusion script library exists
SCRIPT_LIB_PATH="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
if [ ! -f "$SCRIPT_LIB_PATH" ]; then
    echo "ERROR: Fusion script library not found at: $SCRIPT_LIB_PATH"
    echo "Please reinstall DaVinci Resolve or check your installation."
    exit 1
fi
echo "✓ Found Fusion script library"

echo ""
echo "========================================================================"
echo "  Configuring Environment Variables"
echo "========================================================================"
echo ""

# Create backup of config file
if [ -f "$CONFIG_FILE" ]; then
    BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo "✓ Created backup: $BACKUP_FILE"
else
    touch "$CONFIG_FILE"
    echo "✓ Created new config file: $CONFIG_FILE"
fi

# Check if variables are already configured
if grep -q "RESOLVE_SCRIPT_API" "$CONFIG_FILE"; then
    echo ""
    echo "WARNING: DaVinci Resolve environment variables already exist in $CONFIG_FILE"
    echo ""
    read -p "Do you want to update them? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi

    # Remove old configuration
    echo "Removing old configuration..."
    sed -i.tmp '/# DaVinci Resolve Scripting/d' "$CONFIG_FILE"
    sed -i.tmp '/RESOLVE_SCRIPT_API/d' "$CONFIG_FILE"
    sed -i.tmp '/RESOLVE_SCRIPT_LIB/d' "$CONFIG_FILE"
    sed -i.tmp '/DaVinci Resolve\/Developer\/Scripting/d' "$CONFIG_FILE"
    rm -f "${CONFIG_FILE}.tmp"
fi

# Add environment variables
echo "" >> "$CONFIG_FILE"
echo "# DaVinci Resolve Scripting Environment Variables" >> "$CONFIG_FILE"
echo "# Added by setup script on $(date)" >> "$CONFIG_FILE"
echo 'export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"' >> "$CONFIG_FILE"
echo 'export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"' >> "$CONFIG_FILE"
echo 'export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"' >> "$CONFIG_FILE"
echo "" >> "$CONFIG_FILE"

echo "✓ Added environment variables to $CONFIG_FILE"

echo ""
echo "========================================================================"
echo "  Applying Changes"
echo "========================================================================"
echo ""

# Source the config file for the current session
if [ -f "$CONFIG_FILE" ]; then
    # Export variables for this session
    export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"

    echo "✓ Applied changes to current terminal session"
fi

echo ""
echo "========================================================================"
echo "  Verification"
echo "========================================================================"
echo ""

# Verify the variables are set
if [ -z "$RESOLVE_SCRIPT_API" ]; then
    echo "✗ RESOLVE_SCRIPT_API is not set"
    VERIFY_FAILED=1
else
    echo "✓ RESOLVE_SCRIPT_API = $RESOLVE_SCRIPT_API"
fi

if [ -z "$RESOLVE_SCRIPT_LIB" ]; then
    echo "✗ RESOLVE_SCRIPT_LIB is not set"
    VERIFY_FAILED=1
else
    echo "✓ RESOLVE_SCRIPT_LIB = $RESOLVE_SCRIPT_LIB"
fi

if [[ ":$PYTHONPATH:" != *":$RESOLVE_SCRIPT_API/Modules/:"* ]]; then
    echo "✓ PYTHONPATH includes: $RESOLVE_SCRIPT_API/Modules/"
else
    echo "✓ PYTHONPATH is configured"
fi

echo ""
echo "========================================================================"
echo "  Setup Complete!"
echo "========================================================================"
echo ""
echo "Environment variables have been added to: $CONFIG_FILE"
echo ""
echo "IMPORTANT: To use these variables, you need to:"
echo ""
echo "Option 1 (Recommended): Restart your terminal completely"
echo "  - Close this terminal window"
echo "  - Open a new terminal window"
echo ""
echo "Option 2: Reload the config file in this session:"
if [ "$CURRENT_SHELL" = "zsh" ]; then
    echo "  source ~/.zshrc"
elif [ "$CURRENT_SHELL" = "bash" ]; then
    echo "  source $CONFIG_FILE"
fi
echo ""
echo "After restarting/reloading, verify the setup:"
echo "  cd $(dirname "$0")"
echo "  python3 verify_setup.py"
echo ""
echo "========================================================================"
