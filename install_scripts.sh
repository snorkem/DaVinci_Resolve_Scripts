#!/bin/bash
#
# Install DaVinci Resolve Scripts
# Copies scripts to Resolve's Scripts folder so they appear in Workspace → Scripts menu
#

set -e

echo "========================================================================"
echo "  DaVinci Resolve - Script Installation"
echo "========================================================================"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    PLATFORM="Mac";;
    Linux*)     PLATFORM="Linux";;
    CYGWIN*|MINGW*|MSYS*) PLATFORM="Windows";;
    *)          PLATFORM="Unknown";;
esac

echo "Detected platform: $PLATFORM"
echo ""

# Set target directory based on platform
if [ "$PLATFORM" = "Mac" ]; then
    TARGET_DIR="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Support/Fusion/Scripts/Edit"
elif [ "$PLATFORM" = "Linux" ]; then
    TARGET_DIR="$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Edit"
elif [ "$PLATFORM" = "Windows" ]; then
    TARGET_DIR="$APPDATA/Roaming/Blackmagic Design/DaVinci Resolve/Support/Fusion/Scripts/Edit"
else
    echo "ERROR: Unsupported platform: $PLATFORM"
    exit 1
fi

echo "Target directory: $TARGET_DIR"
echo ""

# Create target directory if it doesn't exist
if [ ! -d "$TARGET_DIR" ]; then
    echo "Creating target directory..."
    mkdir -p "$TARGET_DIR"
    echo "✓ Created: $TARGET_DIR"
else
    echo "✓ Target directory exists"
fi

echo ""
echo "========================================================================"
echo "  Copying Scripts"
echo "========================================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="$SCRIPT_DIR/Find_and_Replace"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "ERROR: Source directory not found: $SOURCE_DIR"
    exit 1
fi

# List of scripts to install
SCRIPTS=(
    "find_and_replace_selected.py"
    "batch_edit.py"
    "hello_world_dialog.py"
    "hello_world_working.py"
    "hello_world_with_button.py"
    "show_timeline_name.py"
    "test_resolve_context.py"
    "test_package_import.py"
    "test_ui_methods.py"
    "test_window_creation.py"
    "test_tkinter_dialog.py"
    "test_show_message.py"
    "test_bmd_dispatcher.py"
    "test_uidispatcher_class.py"
    "check_studio_version.py"
    "resolve_utils.py"
)

# Copy each script
for script in "${SCRIPTS[@]}"; do
    SOURCE_FILE="$SOURCE_DIR/$script"
    TARGET_FILE="$TARGET_DIR/$script"

    if [ -f "$SOURCE_FILE" ]; then
        cp "$SOURCE_FILE" "$TARGET_FILE"
        echo "✓ Copied: $script"

        # Make executable
        chmod +x "$TARGET_FILE"
    else
        echo "⚠ Warning: Script not found: $script"
    fi
done

echo ""
echo "========================================================================"
echo "  Installation Complete"
echo "========================================================================"
echo ""
echo "Scripts have been installed to:"
echo "  $TARGET_DIR"
echo ""
echo "To access scripts in DaVinci Resolve:"
echo "  1. (Re)start DaVinci Resolve"
echo "  2. Go to: Workspace → Scripts → Edit"
echo "  3. You should see:"
echo "     - hello_world_dialog"
echo "     - check_studio_version"
echo "     - show_timeline_name"
echo "     - test_resolve_context"
echo "     - test_package_import"
echo ""
echo "NOTE: Scripts can now run from Resolve's menu WITHOUT needing"
echo "      environment variables set!"
echo ""
echo "To test:"
echo "  1. Open DaVinci Resolve"
echo "  2. Run 'hello_world_dialog' for a simple UI test"
echo "  3. Run 'check_studio_version' to see if you have Studio or Free"
echo "  4. Open a project and timeline"
echo "  5. Run 'test_resolve_context' to verify execution context"
echo "  6. Run 'show_timeline_name' to test timeline access"
echo ""
echo "========================================================================"
